# Architecture and product decisions

## Product slice

**A usable single-author document editor with an explicit read-only sharing boundary**. The assessment asks for collaboration but does not require real-time multiplayer editing. This choice lets a reviewer finish an end-to-end workflow rather than seeing several unfinished stretch features.

## Components

```text
Browser (HTML/CSS/JS)
  | REST + X-User-Id (demo identity only)
  v
FastAPI
  | SQLAlchemy ORM + per-request sessions
  v
SQLite locally / PostgreSQL when configured
  ├─ users (seeded accounts)
  ├─ documents (owner_id, title, sanitized HTML, updated_at)
  └─ shares (unique document_id + user_id)
```

- **Front end:** single-page, responsive vanilla JavaScript application; rich text uses native `contenteditable`, formatting toolbar commands, and 650 ms autosave debounce.
- **Back end:** FastAPI endpoints for listing, creating, opening, editing, importing, sharing, and revoking. Server-side checks enforce ownership for mutations and permit granted viewers to read only.
- **Storage:** SQLAlchemy maps the same data model to local SQLite and managed PostgreSQL. Database survives local restarts; deployment persistence depends on a durable PostgreSQL connection.
- **Content:** HTML is stored to preserve common rich-text structure. Bleach strips unsafe tags and all HTML attributes before persistence. Uploads are escaped and imported as simple paragraphs with line breaks.

## Priorities and tradeoffs

| Priority | Implemented | Intentional compromise |
|---|---|---|
| P0 | Create/edit/rename/autosave | Native editor instead of heavier rich-text library |
| P0 | Durable documents and shares | No revision history |
| P0 | Owner and shared viewer states | Demo identity, no secure login |
| P1 | Import `.txt`/`.md` | Markdown imported literally; no DOCX |
| P1 | Access checks and tests | No browser automation |
| P2 | Mobile-friendly responsive layout | No live cursors or simultaneous editing |

## Security and correctness

- Direct API calls enforce share lookup, not just UI read-only state.
- Only owners can modify documents or grant/revoke access.
- User permissions and share uniqueness are checked server-side.
- Imported filenames are reduced to their basename, file types are allowlisted, UTF-8 decoding is checked, upload size is bounded at 1 MiB.
- HTML is allowlist-sanitized on save, and UI displays document titles as text rather than interpolated HTML.
- **Important limitation:** `X-User-Id` can be spoofed intentionally. This is a **demo-only** access model, not authentication. Do not use this with production customer data.

## Verification

Automated tests use `fastapi.testclient` and an isolated local SQLite database to verify create/save, sanitization, hiding unshared documents, viewer write denial, granting and revoking shares, and upload allowlisting. Front-end behavior still requires browser manual validation and actual deployment verification.
