# Play-O-Meter-2025-26 — Repository Management

This document captures the recommended GitHub workflows, branch and release strategy, PR and review rules, CI/testing guidance, code ownership, and repository-level conventions for the Play-O-Meter-2025-26 repository. It's intended for contributors, maintainers, and reviewers.

## Table of contents

- Repository overview
- Goals & roles
- High-level branch strategy
- Branch naming conventions
- Pull request (PR) process and checklist
- Issue tracking, labels & milestones
- Code review checklist
- CI / tests / status checks
- Releases & changelogs
- Security & secrets
- Data, large files and artifacts
- Local development and bootstrapping
- Repo housekeeping & maintenance tasks
- Quick references (commands, templates, suggested files)

---

## Repository overview

Repository: `Play-O-Meter-2025-26`
Main technologies:

- Backend: Python (FastAPI), uvicorn, pandas, ultralytics/YOLO, torch
  - Path: `elctron_application/backend/app` (routers, services, models)
- Frontend: Electron + React + TypeScript + Vite
  - Path: `elctron_application/electron-app/src`
- Tooling & data processing components under `play-o-meter` and `src/`
- Tests: `tests/` (pytest)

Important repo-specific notes:

- Default packaged model: `backend/app/models/Model_YoloV11_4.pt`
- Data layout expected by the app (convention):
  - Videos: `data/video/*.mp4`
  - Merged CSVs: `data/merged/*_merged.csv`
- Sensitive keys (e.g. Riot API key) must be stored in server-side env (`RIOT_API_KEY`) — do not commit keys.

---

## Goals & roles

- Maintain a stable `main` branch that is always deployable.
- Use a predictable branching model for features, releases and hotfixes.
- Ensure PRs are reviewed and have passing CI before merge.
- Keep secrets out of source control and enforce code ownership for critical areas (backend/riot, data processing).

Roles (example):

- Maintainers: core team with merge permissions and branch protection config access.
- Reviewers: team members assigned via CODEOWNERS or PR reviewers.
- Contributors: open-source contributors or teammates creating feature branches and PRs.

---

## Branch strategy (recommended)

Adopt a simple Git branching model that balances stability and fast iteration:

- `main`
  - Always stable. Contains production-ready commits. Protected branch.
- `develop` (optional)
  - Integration branch for ongoing work. If you prefer trunk-based development, you can omit `develop` and merge feature branches directly into `main` via PRs.
- Feature branches
  - Pattern: `feature/<short-desc>`, e.g. `feature/valorant-reaction-markers`
- Bugfix/hotfix branches
  - Pattern: `fix/<short-desc>` or `hotfix/<short-desc>`
- Release branches (optional)
  - Pattern: `release/v1.2.0`

Branch protection rules to enable on `main` (and `develop` if used):

- Require PR reviews (1-2 reviewers)
- Require passing CI checks (unit tests, lint)
- Enforce linear history (no direct pushes)
- Require signed commits if desired

---

## Branch & commit naming conventions

- Branch names: lowercase, hyphen-separated, prefixed with the type: `feature/`, `fix/`, `hotfix/`, `chore/`.
- Commit messages: use imperative-style short subject plus optional body. Example:
  - `feat(reaction): add YOLO-based reaction time endpoint`
  - `fix(lol-dashboard): prefer hook-ranked-entries over local fallback`

---

## Pull request (PR) process & checklist

1. Create a branch from `develop` (or `main` if not using `develop`).
2. Make focused changes and write tests for logic changes where reasonable.
3. Push branch to origin and open a PR against `develop` (or `main`).
4. Fill PR template (title, description, linked issue(s), testing notes, screenshot if UI change).
5. Request reviewers; add labels (feature, bug, docs, chore).
6. Ensure CI passes and at least one review approves.
7. Squash/merge (or merge commit per project preference) once approved and CI green.

PR checklist (required before merge):

- [ ] Linked issue or clear description of intent
- [ ] Unit tests added/updated for backend logic and major frontend logic
- [ ] Linting and type checks pass (TS/ESLint, python linters optional)
- [ ] No secrets or large binaries accidentally included
- [ ] Changes documented (README or docs/) if required

---

## Issue lifecycle, labels & templates

Suggested label set:

- type: bug, feature, enhancement, docs, test, chore
- priority: p0, p1, p2
- status: triage, in-progress, needs-review, blocked, wontfix

Suggested issue template contents:

- Short description
- Steps to reproduce (if bug)
- Expected behavior
- Actual behavior
- Environment (OS, backend venv, node/npm versions)
- Screenshots / logs
- Suggested fix or notes

Suggested PR template contents:

- Summary of changes
- Related issue(s)
- How to test (steps)
- Checklist (tests, lint, docs)

---

## Code review checklist (concise)

- Read the PR description and link to issue.
- Does the change implement the stated goal?
- Are there unit/integration tests? Do they cover edge cases?
- Are new dependencies necessary and vetted?
- Are secrets or large files added? (If so, block and revert)
- Is the code readable and adequately commented?
- Are performance and security implications considered (e.g., server-side Riot API usage)?
- Is there any user-visible UI/UX change — are screenshots provided?

---

## CI / tests / status checks

Minimal checks to enforce on PRs (GitHub Actions recommended):

- Backend unit tests (pytest) run and pass. Example job name `python-tests`.
- Frontend build + TypeScript typecheck + lint (ESLint). Example job name `frontend-check`.
- Optional: e2e tests or smoke tests for critical flows.

Suggested commands (PowerShell on Windows):

Backend (Python)

```powershell
# from repo root
cd .\elctron_application\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Frontend (Electron / Vite)

```powershell
cd .\elctron_application\electron-app
npm ci
# run lint / typecheck
npm run build # or npm run dev for dev server
```

CI tips:

- Keep tests fast; run slow or optional integration tests in separate workflows.
- Run linters and type-checkers early.
- Cache pip and node modules to speed up CI.

---

## Releases & changelog

- Use semantic versioning (MAJOR.MINOR.PATCH).
- For small teams, consider tagged releases from `main` (e.g., `v1.2.0`).
- Maintain a changelog (e.g., keep `CHANGELOG.md`) or use release notes drafted from PRs.
- Release checklist:
  - All PRs merged into `main`
  - CI green
  - Tag release and draft GitHub Release notes

---

## Security & secrets

- Never commit API keys, passwords, or private certificates.
- Use GitHub Secrets for workflows and server-side environment variables for runtime secrets (e.g. `RIOT_API_KEY`).
- For local dev, store keys in `.env` and add `.env` to `.gitignore`.
- If a secret is accidentally committed, rotate it immediately and purge the secret from repo history.

---

## Data handling & large files

This repo processes video files, CSVs and ML model files. Follow these rules:

- Do not commit raw data (videos, large CSVs) to Git.
- Add large or generated files to `.gitignore` (for example `data/` and `models/*.pt` if you prefer to store models in releases or LFS).
- Use Git LFS for large artifacts if tracking them in repo is necessary (model weights, trained artifacts).
- For reproducibility, store small sample datasets or links to external storage in `docs/` instead of large files.

Recommended `.gitignore` entries (examples):

```
# data and artifacts
/data/
*.mp4
*.mov
/models/*.pt
.env
__pycache__/
.vscode/
node_modules/
.elctron_application/backend/.venv
```

---

## Local development & bootstrapping (quick start)

Backend (FastAPI)

1. Create and activate venv

```powershell
cd .\elctron_application\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set required env vars (example in PowerShell)

```powershell
$env:RIOT_API_KEY = 'REPLACE_ME'
```

3. Run dev server

```powershell
# run uvicorn with the project venv python to avoid Conda collisions
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Frontend (Electron / Vite)

```powershell
cd .\elctron_application\electron-app
npm ci
npm run dev
# or build for production
npm run build
```

Running tests

```powershell
# from repo root
pytest -q
```

---

## Repo housekeeping & maintenance

- Update dependencies regularly and test on a branch.
- Run `pytest` and linting before merging large PRs.
- Periodically prune stale branches and close stale issues.
- Keep `README.md` and `docs/` up to date with setup notes and data expectations.

---

## Suggested repository files to add (if not present)

- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/ci.yml` (GitHub Actions for tests/build)
- `CODEOWNERS` (to auto-request reviews from owners of backend/frontend folders)
- `CHANGELOG.md`
- `RELEASE_PROCESS.md` (detailed steps for creating a release)

### Example `CODEOWNERS`

```
# Require reviews from backend owners for backend changes
/elctron_application/backend/ @your-backend-team
/elctron_application/electron-app/ @your-frontend-team
```

---

## Quick PR template (suggestion)

Title: `[type(scope)]: short description` (e.g., `feat(react): add reaction markers`)

Description:

- What: short summary
- Why: motivation
- How: high level approach

Testing:

- Steps to reproduce / run
- Unit tests added: yes/no

Checklist:

- [ ] Linked issue
- [ ] Tests pass locally
- [ ] Lint passed
- [ ] Documentation updated

---

## Troubleshooting & common pitfalls (repo-specific)

- Backend venv collisions with Conda/Python: always run `uvicorn` with the venv Python executable explicitly (`.venv\Scripts\python.exe -m uvicorn ...`).
- Riot API errors: ensure `RIOT_API_KEY` is set server-side and not exposed to the frontend.
- File path mismatches: The app builds server file paths from the locally configured `toolkit_data_directory`. If the frontend requests paths the backend cannot read, you'll get 400s — ensure the `data_directory` used in the app points to the correct backend data root.
- Large models & artifacts: keep production weights in `backend/app/models/` or an external artifact store. Use git tags and releases to attach large files if needed.

---

## Where to go from here (recommended next steps)

1. Add the file `REPOSITORY_MANAGEMENT.md` to the repo (this document).
2. Create a minimal `ci.yml` in `.github/workflows/` that runs Python tests and frontend build on PRs to `main`/`develop`.
3. Add `CODEOWNERS` to auto-assign reviewers.
4. Add ISSUE/PR templates under `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`.
5. Protect `main` with required status checks and reviewers.
