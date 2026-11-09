# Ajaia assessment submission — Draftly

## Contents

- `backend/main.py`: FastAPI application, data model, sharing rules, validation and import API.
- `frontend/index.html`, `frontend/style.css`, `frontend/app.js`: browser interface and rich-text editor.
- `tests/test_api.py`: backend automated tests.
- `requirements.txt`, `pytest.ini`, `Procfile`, `render.yaml`: environment and deployment files.
- `README.md`: installation, local run instructions, demo steps, constraints, deployment directions.
- `ARCHITECTURE.md`: system overview and prioritized tradeoffs.
- `AI_WORKFLOW.md`: truthful AI-use and test-process notes.
- `WALKTHROUGH_URL.txt`: placeholder for your 3–5 minute recording.

## Review links — complete these before submission

- **Google Drive folder:** NOT YET UPLOADED
- **Live app URL:** NOT YET DEPLOYED
- **Walkthrough video URL:** NOT YET RECORDED

## Demo identities

Choose a user using the bottom-left dropdown:

- Alex Morgan (owner) — `alex@demo.local`
- Jordan Lee (shared viewer) — `jordan@demo.local`

No passwords: **mocked users, not real authentication**. New documents are private to the selected owner until shared.

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000; run `pytest -q` for tests.

## Status

Implemented in source: rich-text editing, create/rename/autosave/reopen, `.txt`/`.md` plain-text upload, owner/viewer sharing, SQLite persistence, PostgreSQL config path, input validation, permission tests, basic responsive UI.

**Needs owner completion:** live URL, real deployment validation, manual browser walkthrough/video, Google Drive folder upload. This is **not** a claim of a finished external submission.

## If given another 2–4 hours

Replace mocked identity with secure sessions, migrate native editing to TipTap, add optimistic concurrency/versioning, and write browser integration tests.
