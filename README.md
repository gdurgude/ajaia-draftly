# Draftly — lightweight collaborative document workspace

A deliberately scoped Google Docs-inspired editor for Ajaia's AI-Native Full Stack assessment. **Demo users are simulated, not authenticated.** Sharing means owner-only edits + explicit viewer access, not simultaneous co-editing.

## Features

- Create, rename, edit, autosave and reopen rich-text documents.
- Bold, italic, underline, headings, ordered and unordered lists.
- Import UTF-8 `.txt` and `.md` files (up to **1 MB**) as editable **plain text**. Markdown is **not rendered**; markdown syntax remains literal.
- Switch between seeded **Alex Morgan** and **Jordan Lee** to demonstrate owner/shared distinction.
- Owners can grant/revoke read-only access. Viewers see shared documents but cannot edit.
- SQLite persistence locally; PostgreSQL when `DATABASE_URL` is configured.
- Backend validates document titles and size, checks access on each request, sanitizes allowed HTML, and validates imported file types and encoding.

## Local setup (Python 3.11+)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000**. No Node.js, npm, API key, or paid service is needed.

The SQLite database is created as `docspace.db` beside this README. Restarting the server preserves documents, unless this file is deleted.

### Test

```bash
pytest -q
```

## 2-minute review path

1. As **Alex Morgan**, create a document and give it a title.
2. Add formatted text, wait for **All changes saved**, and refresh.
3. Use **Share** to invite **Jordan Lee**.
4. Switch users using the bottom-left dropdown. The document should appear as **Shared by Alex Morgan** and be read-only.
5. Switch to Alex to revoke access; switch back to Jordan and verify it disappears.
6. Import a `.txt` or `.md` file using **Import**.

## Deployment

Recommended: **Render web service + free managed PostgreSQL (for example, Neon free tier)**.

1. Push the source to your own GitHub repository.
2. Create a free PostgreSQL database from a managed provider and copy its connection URL. Never commit database credentials.
3. In Render, choose **New > Blueprint** and select your repository (it contains `render.yaml`).
4. Set `DATABASE_URL` to the PostgreSQL connection string. The backend accepts `postgres://` and `postgresql://` URLs, converting them for psycopg. If the URL contains special characters in a password, use a provider-provided properly encoded URI.
5. Wait for build/deploy, visit the assigned service URL, and repeat the review path above.
6. On free hosting, the service may sleep after inactivity. The first load might be slower.

**Important:** Render's free local filesystem is ephemeral, so **do not deploy using SQLite without persistent storage** if you want saved documents to survive restarts/redeployments. Configure PostgreSQL for a real review deployment. Database free tiers and hosting offerings can change.

**Live URL:** not deployed in this supplied package; add your real tested URL here and to `SUBMISSION.md`.

## API overview

`GET /api/users`, `GET/POST /api/documents`, `GET/PATCH /api/documents/{id}`, `POST /api/documents/{id}/share`, `DELETE /api/documents/{id}/share/{user_id}`, and `POST /api/import`.

Every document request sends an `X-User-Id` header set to one of the two seeded IDs. **This is intentionally insecure mocked identity for an assessment demo.** Never expose real confidential documents using this model. A real implementation would use login sessions, verified identity, CSRF protections, and more granular permission checks.

## Known limitations

- No concurrent editing, comments, version history, document export, or offline support.
- Sharing is viewer-only; there are no editable shared roles.
- Rich-text uses native `contenteditable` / `execCommand`; the latter is deprecated, and browser-specific editing behavior varies. For production use, switch to TipTap/ProseMirror.
- Autosave has simple debouncing and a navigation/unload warning; it does not support offline edits or full conflict resolution.
- `.md` imports are plain text, not converted from Markdown formatting. `.docx` is unsupported.
- Mocked demo user switching does not provide real authentication.
- No stress testing or browser automation suite. Backend permission and upload tests exist.

## Next 2–4 hours

1. Introduce actual sign-in with signed sessions and authorization tests.
2. Replace the editor engine with TipTap, and add deterministic rich-text serialization.
3. Add revision numbers/optimistic locking for concurrent modification prevention.
4. Add browser-level E2E checks and health/structured error logging.

See [`ARCHITECTURE.md`](ARCHITECTURE.md), [`AI_WORKFLOW.md`](AI_WORKFLOW.md), and [`SUBMISSION.md`](SUBMISSION.md).
