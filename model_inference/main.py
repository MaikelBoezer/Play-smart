"""
FastAPI Inference Service — Play-Smart YOLOv8 Reaction Time Analysis
=====================================================================

HOW THIS FITS IN THE PIPELINE
──────────────────────────────
This file runs on the GPU PC. It wraps run_yolo_inference() in an HTTP server
so that queenbee (or any other machine on the LAN) can trigger inference jobs
over the network without needing Python or CUDA installed themselves.

The full flow looks like this:

  1. A session finishes on queenbee → video + merged CSV land in the SFTP volume
  2. The pipeline container on queenbee sends a POST /predict request to this service
  3. This service receives the file paths, runs YOLO inference on the GPU, returns JSON
  4. The pipeline container receives the reaction_data and stores it in the database

Nothing in this file does the actual inference — that's all still in
run_yolo_inference.py (your existing script). This file is purely the
HTTP "front door" that makes the inference script callable over the network.
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import torch
import time
import threading
from datetime import datetime, timedelta

# ── Import your existing inference script ────────────────────────────────────
# This assumes main.py lives in the same directory as run_yolo_inference.py.
# If they're in different folders, adjust the import path accordingly.
from run_yolo_inference import run_yolo_inference, run_yolo_batch_inference

# ── Logging ───────────────────────────────────────────────────────────────────
# Mirrors the logging config in your existing script so output is consistent.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── App setup ─────────────────────────────────────────────────────────────────
# FastAPI() creates the application object. Think of it as the container that
# holds all your endpoints and handles incoming HTTP requests.
app = FastAPI(
    title="Play-Smart Inference Service",
    description="YOLOv8 reaction time analysis — GPU inference endpoint",
    version="1.0.0",
)


# ── Request model ─────────────────────────────────────────────────────────────
# Pydantic models define the shape of the JSON body that callers must send.
# FastAPI automatically validates the request against this model and returns
# a 422 error if required fields are missing or have the wrong type.
# This is the contract between queenbee and this service.
class InferenceRequest(BaseModel):
    video_path: str          # e.g. "Z:/uploads/session_01/gameplay.mp4"
    csv_path: str            # e.g. "Z:/uploads/session_01/merged.csv"
    model_path: str = ""     # Optional: leave empty to use the default model
    threshold: float = 0.8   # Confidence threshold, defaults to 0.8
    batch_size: int = 16   # batch size of the model
    use_batch: bool = True  # batch is default


# ── Response model ────────────────────────────────────────────────────────────
# Defines what the caller gets back. Using a response model means FastAPI
# will filter and validate the output — callers always get a predictable shape.
class InferenceResponse(BaseModel):
    status: str
    message: str
    reaction_data: list       # List of reaction time dicts from your script
    output_csv_path: str = "" # Path where the CSV was written (if any)


# ── In-memory job store ───────────────────────────────────────────────────────
# YOLO inference on a full gameplay video can take minutes. Rather than making
# the caller wait with a hanging HTTP connection, we run inference in the
# background and let the caller poll for the result using a job ID.
#
# In production you'd use Redis or a database for this. For the Hive, a simple
# dict is fine since there's only one GPU PC and one caller (queenbee).
jobs: dict = {}


# ── Background inference function ─────────────────────────────────────────────
# This function is what actually runs when a job is submitted. FastAPI's
# BackgroundTasks runs it in a separate thread so the HTTP response can return
# immediately without blocking.


def run_inference_job(job_id: str, req: InferenceRequest):
    logger.info(f"[Job {job_id}] Starting {'batch' if req.use_batch else 'standard'} inference...")

    video_path_normalized = os.path.normpath(req.video_path)
    output_csv = os.path.join(
        os.path.dirname(video_path_normalized),
        f"reaction_times_{job_id[:8]}.csv"
    )

    try:
        if req.use_batch:
            result = run_yolo_batch_inference(
                model_path=req.model_path,
                video_path=req.video_path,
                input_log_path=req.csv_path,
                gaze_log_path=req.csv_path,
                threshold=req.threshold,
                batch_size=req.batch_size,
                output_csv_path=output_csv,
            )
        else:
            result = run_yolo_inference(
                model_path=req.model_path,
                video_path=req.video_path,
                input_log_path=req.csv_path,
                gaze_log_path=req.csv_path,
                threshold=req.threshold,
                output_csv_path=output_csv,
            )

        if "error" in result:
            logger.error(f"[Job {job_id}] Inference error: {result['error']}")
            jobs[job_id] = {"status": "failed", "error": result["error"]}
        else:
            logger.info(f"[Job {job_id}] Complete. {len(result['reaction_data'])} instances found.")
            jobs[job_id] = {
                "status": "complete",
                "reaction_data": result["reaction_data"],
                "output_csv_path": output_csv,
                "created_at": jobs[job_id]["created_at"],
            }

    except Exception as e:
        logger.exception(f"[Job {job_id}] Unexpected error: {e}")
        jobs[job_id] = {"status": "failed", "error": str(e)}




# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Queenbee's pipeline container should call this before submitting a job to
    confirm the GPU PC is up and the service is running. If this returns 200,
    everything is ready. If it times out or errors, the pipeline knows to skip
    inference or raise an alert.
    """

    share_ok = Path("Z:/sftp_data").exists()

    return {
        "status": "ok" if share_ok else "degraded",
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "share_accessible": share_ok,
    }

@app.post("/predict")
def submit_inference(req: InferenceRequest, background_tasks: BackgroundTasks):
    if not os.path.exists(req.video_path):
        raise HTTPException(status_code=400, detail=f"Video not found: {req.video_path}")
    if not os.path.exists(req.csv_path):
        raise HTTPException(status_code=400, detail=f"CSV not found: {req.csv_path}")

    job_id = str(uuid.uuid4())

    # Add a timestamp when a job is created or updated
    jobs[job_id] = {"status": "queued", "created_at": datetime.now()}


    background_tasks.add_task(run_inference_job, job_id, req)

    logger.info(f"[Job {job_id}] Queued {'batch' if req.use_batch else 'standard'} inference for {req.video_path}")
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
def get_job_result(job_id: str):
    """
    Poll for the result of a submitted inference job.

    Queenbee calls this repeatedly (e.g. every 10 seconds) until status is
    'complete' or 'failed'. Possible statuses:
      - 'queued'   : job received, not started yet
      - 'running'  : inference is in progress
      - 'complete' : done, reaction_data is populated
      - 'failed'   : something went wrong, check the 'error' field
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.get("/jobs")
def list_jobs():
    """
    List all jobs and their statuses.
    Useful for debugging — lets you see everything that's been submitted
    since the service started.
    """
    return {jid: {"status": info["status"]} for jid, info in jobs.items()}

def cleanup_old_jobs():
    """Remove jobs older than 1 hour to prevent the dict growing forever."""
    while True:
        cutoff = datetime.now() - timedelta(hours=1)
        to_delete = [
            jid for jid, info in list(jobs.items())
            if info.get("created_at", datetime.now()) < cutoff
        ]
        for jid in to_delete:
            del jobs[jid]
            logger.info(f"Cleaned up old job {jid}")
        time.sleep(300)

cleanup_thread = threading.Thread(target=cleanup_old_jobs, daemon=True)
cleanup_thread.start()
