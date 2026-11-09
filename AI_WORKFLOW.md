# AI-native workflow note

> **Accuracy instruction:** Update this note to reflect the exact tools and iterations you personally performed before submitting. Do not claim an unperformed browser, deployment, or security review.

## AI tools used

- **ChatGPT (GPT-6):** decomposed the assignment, proposed a narrowly scoped product slice, drafted the backend/frontend implementation, generated test coverage, and drafted documentation.
- **Local command-line validation:** ran Python API tests and JavaScript static checks. This is conventional tooling, not AI.

## How AI accelerated delivery

- Converted a broad spec into a small implementation with clear priorities: create/edit/save, file import, owner/viewer sharing, and persistence first.
- Produced a consistent initial API/data model and matching front-end wiring in one pass.
- Generated regression tests for access control and upload behavior.
- Drafted run/deployment and architecture notes, leaving deployment URLs to be filled after verification.

## Iterations and changes

- **Changed after a test failure:** The initial `pytest` run could not import `backend`; added `pytest.ini` with the repository root on the import path, then reran the tests successfully.
- **Scope cuts made deliberately:** avoided real-time multi-user editing, authentication, and `.docx` parsing; chose a read-only share permission and local-first SQLite workflow so core functionality could be tested.
- **Not verified:** A reviewer-accessible cloud deployment and real multi-browser UX were not completed in this generated starter package.

## How correctness was verified

- Automated backend tests check document creation and persistence via API, sanitization, sharing behavior, write authorization, revocation, and upload format validation.
- Run `pytest -q` to reproduce the test results; use the README's review path for manual UI checks.
- Before submitting, run a live deployment and repeat all six end-to-end steps in the README. Record any bugs found and corrections made here.

## Human judgment to demonstrate

In your walkthrough, explain *why* single-owner editing + viewer sharing is a defensible product slice, *where* the trust boundary exists, and *why* real production access needs authenticated sessions. Also mention concrete changes you personally made while reviewing or deploying this project.
