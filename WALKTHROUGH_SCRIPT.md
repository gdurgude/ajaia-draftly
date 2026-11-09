# Suggested 3–5 minute walkthrough script (adapt to what you actually verified)

**0:00–0:25 — Scope:** “I focused on a complete document workflow rather than real-time collaboration. Draftly supports rich-text writing, imports, saved documents, and owner/viewer sharing.”

**0:25–1:35 — Editing:** As Alex, create a document, change title, type a heading, bold text, a bulleted list, wait for ‘All changes saved,’ refresh to show persistence.

**1:35–2:15 — File upload:** Import a UTF-8 `.txt` file, show it becomes a document. Explain `.md` imports as plain text; `.docx` was intentionally excluded.

**2:15–3:10 — Sharing:** Share with Jordan. Switch to Jordan; show ‘Shared by Alex’ and read-only access. Switch to Alex to revoke; show it disappears for Jordan.

**3:10–4:10 — Engineering:** Briefly explain the FastAPI routes, SQLAlchemy/SQLite or deployed PostgreSQL, sanitization, owner-side permission enforcement, and backend test results.

**4:10–4:45 — AI and tradeoffs:** Explain AI-assisted initial implementation, the import-path test issue and correction, what *you* manually verified, and the next 2–4 hours (secure auth, TipTap, versioning).

**Important:** Do not claim a behavior works until you have demonstrated and verified it on the deployed app.
