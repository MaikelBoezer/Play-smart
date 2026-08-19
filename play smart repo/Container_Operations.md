# Container Operations

This document describes the Docker containers that make up the Play-Smart application stack, along with procedures for building, publishing, and deploying updated images to the server.

---

## Container Overview

The Play-Smart stack consists of five containers. Four are maintained by the Play-Smart team and published to the project's Docker Hub account (`220755842`). The fifth is a third-party image.

| Image | Container Name | Description |
|---|---|---|
| `220755842/bg-app-frontend` | `app-frontend` | React/Nginx frontend serving the Play-Smart dashboard. |
| `220755842/bg-app-backend` | `app-backend` | FastAPI backend exposing REST endpoints for the dashboard and data access layer. |
| `220755842/bg-app-pipeline` | `app-pipeline` | Data processing pipeline handling multi-source data merging, cleaning, and automated DQ report generation. |
| `220755842/bg-app-inference` | `app-inference` | Inference watcher running on the Hive workstations, forwarding prediction requests to the deployed ML models. |
| `atmoz/sftp` | `app-sftp-container` | SFTP endpoint for transferring session data from Hive workstations to the server. |

---

## Updating a Container

When code changes are made to a service, its image must be rebuilt, pushed to Docker Hub, and pulled on the server. The steps below cover the full update cycle.

### Prerequisites

- Docker Desktop must be running on the development machine.
- You must be authenticated with the Play-Smart Docker Hub account (see step 1 below).

---

### Step 1 — Authenticate with Docker Hub

Open a terminal and log in to the shared project account:

```bash
docker login
```

---

### Step 2 — Build the Updated Image

Navigate to the project root and build only the image(s) for the service(s) that changed:

```bash
docker build -t playsmartbuas/bg-app-backend   ./backend
docker build -t playsmartbuas/bg-app-frontend  ./electron-app
docker build -t playsmartbuas/bg-app-pipeline  ./pipeline
docker build -t playsmartbuas/bg-app-inference ./inference
```

---

### Step 3 — Push to Docker Hub

Push the newly built image(s) to the registry:

```bash
docker push playsmartbuas/bg-app-backend
docker push playsmartbuas/bg-app-frontend
docker push playsmartbuas/bg-app-pipeline
docker push playsmartbuas/bg-app-inference
```

---

### Step 4 — Pull the New Image on the Server

SSH into the server and navigate to the application directory:

```bash
cd app
```

Pull all updated images at once, or target a specific service:

```bash
# Pull all images
docker compose pull

# Pull a specific image
docker compose pull backend
docker compose pull frontend
docker compose pull pipeline
docker compose pull inference
```

---

### Step 5 — Recreate the Container

Restart the relevant container using its **service name** (as defined in `docker-compose.yml`), not the container name:

```bash
docker compose up -d --force-recreate <service-name>
```

---

## Project Structure

The repository layout for all four team-managed containers is shown below:

```bash
project/
├── backend/
│   ├── app/
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── coach_config.py
│   │   │   ├── feedback.py
│   │   │   ├── toolkit.py
│   │   │   └── users.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── coach_config.py
│   │   │   ├── database_models.py
│   │   │   ├── feedback.py
│   │   │   ├── Model_YoloV11_4.pt
│   │   │   ├── toolkit.py
│   │   │   └── users.py
│   │   ├── router/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── biometrics.py
│   │   │   ├── coach.py
│   │   │   ├── feedback.py
│   │   │   ├── match_data.py
│   │   │   ├── reaction_time.py
│   │   │   ├── riot.py
│   │   │   ├── toolkit.py
│   │   │   ├── valorant.py
│   │   │   └── videos.py
│   │   ├── services/
│   │   │   ├── biometric_processor.py
│   │   │   └── inference.py
│   │   ├── utils/
│   │   │   └── auth.py
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── main.py
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── migrate_feedback.py
│   ├── migrate_match_id.py
│   ├── pyproject.toml
│   ├── run_production.bat
│   └── run_production.sh
├── electron-app/
│   ├── assets/
│   ├── docs/
│   ├── electron/
│   │   ├── main.cjs
│   │   └── preload.cjs
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── EmotionPieChart.tsx
│   │   │   │   ├── GazeMetrics.tsx
│   │   │   │   ├── InputMetrics.tsx
│   │   │   │   └── WASDCharts.tsx
│   │   │   ├── layout/
│   │   │   │   ├── coachlayout.tsx
│   │   │   │   └── playerlayout.tsx
│   │   │   └── Valorant/
│   │   │       └── MatchHistoryTable.tsx
│   │   ├── hooks/
│   │   │   └── usePlayerData.ts
│   │   ├── pages/
│   │   │   ├── coach/
│   │   │   └── player/
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── riot.ts
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── inference/
│   ├── Dockerfile
│   ├── inference_client.py
│   ├── requirements.txt
│   └── watcher.py
├── pipeline/
│   ├── auto_cleaning_and_dq.py
│   ├── auto_dq_report.py
│   ├── auto_merge.py
│   ├── Dockerfile
│   ├── esports_utils.py
│   ├── generate_dq_report.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```
