WORKING.md

SecureVote Pro — How everything works (developer reference)

## Overview

SecureVote Pro is a compact demo/prototype of a cryptographically-inspired electronic voting system. It combines a FastAPI backend and a small client-side frontend (server-served templates + static JavaScript and CSS). The core educational goals are:

- Demonstrate cryptographic ballot hashing and Merkle proofs for tamper-evidence.
- Use data structures (Bloom Filter, Merkle Tree, Audit Stack) to illustrate performance/security trade-offs.
- Show a simple production-like architecture with JWT auth, OTP 2FA for voters, and an admin/voter UI.

This document explains how the pieces fit together, where code lives, how data flows, how to run the app locally, and where to change the frontend (fonts, icons, colors).

## Table of contents

- Project layout (important files)
- How to run (dev & production notes)
- Backend architecture
  - Entry point and routing
  - Data model and persistence
  - Services and core logic (VotingService)
  - Authentication & 2FA flow
  - Cryptography utilities
  - Redis / Mock Redis usage
- Frontend architecture
  - Templates and main pages
  - Static assets: CSS, JS, fonts, icons
  - Where icons come from and how they’re loaded
  - How data is requested/updated from the frontend
- The Merkle tree & proofs (how to generate/verify)
- How OTACs work (generation, hashing, use)
- Demo/Undo / Audit stack
- Where to change theme, fonts, and icons
- Troubleshooting & common maintenance tasks

## Project layout (high level)

Important top-level files and folders (most relevant to developers):

- `main.py` — FastAPI application entrypoint and routing (serves HTML pages and JSON APIs).
- `config.py` — App configuration (env-driven). Contains salts, flags (DEMO_MODE, DEVELOPMENT_MODE), DB/SMTP information.
- `database.py` — SQLAlchemy models and connection factory; in-memory MockRedis fallback when Redis is not available.
- `services/voting_service.py` — Business logic for registering voters, issuing OTACs, casting votes, tallying, Merkle proof generation, audit stack handling.
- `utils/crypto_utils.py` — Crypto helpers (voter hashing, OTAC generation + hashing, ballot hash generation/verification).
- `email_service.py` — OTP sending / verification (not detailed here but used in 2FA flow).
- `templates/` — Jinja/HTML templates served for `login`, `admin`, `voter`, and `index`.
- `static/` — Frontend static assets: JS, CSS, images, and icons (Font Awesome loaded from CDN).
  - `static/styles.css` & `static/styles_clean.css` — Main UI styling and theme variables.
  - `static/styles_old.css` — legacy styling (kept for reference).
  - `static/*.js` — Front-end logic (page wiring, API calls). Notable files are `scripts.js`, `auth.js`, `app.js`, `admin.js`, `voter.js`.
- `data_structures/` — Implementations of Bloom Filter, Merkle Tree, Audit Stack used by VotingService.
- `tests/` — Unit tests (where present).

## How to run

Requirements: Python 3.9+, pip. See `requirements.txt` for the project dependencies.

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. (Optional) Create a `.env` file to set production credentials / config. See `README.md` for common environment variables:

- `DATABASE_URL` — defaults to `sqlite:///./voting_system.db`.
- `SMTP_EMAIL` / `SMTP_PASSWORD` — Gmail credentials for sending OTP (or configure an SMTP server).
- `SECRET_KEY` and `VOTER_SALT` — change in production.

3. Start the dev server (auto reload):

```powershell
python main.py
# or
uvicorn main:app --reload
```

4. Open the web UI at http://127.0.0.1:8000 (the root redirects to `/login`).

## Backend architecture — how requests flow

Entrypoint (`main.py`):

- The app mounts `StaticFiles` at `/static` and serves templates (login/admin/voter) via routes.
- API endpoints are declared in `main.py` and call `VotingService` for business logic.

Database & models (`database.py`):

- Uses SQLAlchemy with declarative models:
  - `Voter` — stores `voter_id_hash` and `has_voted` (boolean)
  - `Ballot` — stores `seq`, `ballot_hash`, `candidate_id`, `timestamp`
  - `Tally` — per-candidate vote counts
  - `AuditEvent` — audit trail entries with prev/new merkle root
  - `MerkleLeaf` — leaves indexing ballot hashes
  - `OTACMapping` — mapping of hashed OTAC -> voter_id_hash and used flag
- `create_tables()` creates the DB tables on startup.

Redis / Mock Redis:

- `database.py` attempts to set up `redis_client` from `Config.REDIS_URL`. If `redis` library or server is absent, a `MockRedis` object is used (an in-memory dict). This keeps dev setup simple while allowing production to use Redis if configured.

Core logic (VotingService — `services/voting_service.py`):

- High-level responsibilities:
  - Register voters (hash voter IDs and store Voter entries)
  - Issue OTACs (generate secure OTAC strings, hash them for storage in `OTACMapping` and return plain codes to admin)
  - Cast votes: validate OTAC, ensure voter hasn't voted, mark OTAC used, record ballot (seq + ballot_hash), increment tally, add leaf to Merkle tree, persist audit event
  - Generate Merkle inclusion proofs and verify proofs
  - Provide system stats (tallies, merkle root, filter/audit stats)
  - Demo undo: In DEMO_MODE, use AuditStack to undo last action and rebuild Merkle tree
- Data structures used:
  - BloomFilter to check duplicates (fast probabilistic check)
  - MerkleTree to compute root and proofs (tamper-evident storage)
  - AuditStack to record/undo recent operations (LIFO for demo)

## Authentication

- Lightweight auth implemented in `main.py` and `auth.py` (AuthService helper):
  - Admin/commissioner: direct username/password login, returns JWT access token with role `admin`.
  - Voter: login with username/password + email — upon valid credentials, server sends OTP to email and returns a temporary token (`temp_token`) that is used during OTP verification. After verifying OTP, a final JWT access token for `voter` is issued.
  - Tokens are short lived (e.g., 10 minutes for temp token, 30 minutes for access token) — stored in JWT payloads. `AuthService` provides `create_access_token` and `verify_token` helpers.

## 2FA and OTP flow

- `email_service.send_otp_email(email, username)` is used to generate and send OTP. The OTPs are stored in an in-memory store (`utils/simple_otp_storage.py`) or delivered via SMTP when configured.
- Process:
  1. Voter submits username/password + email to `/auth/login`. App validates credentials and calls `send_otp_email`.
  2. Server returns `temp_token` and `requires_2fa=true` to the client.
  3. Client posts OTP + `temp_token` to `/auth/verify-otp`.
  4. Server verifies OTP and `temp_token`, then issues final access JWT token.

## Cryptography utilities (`utils/crypto_utils.py`)

- `hash_voter_id(voter_id)` — salted SHA-256 hash using `Config.SALT`. We store only the hash in the DB (avoids storing raw voter IDs).
- `generate_otac()` — secure OTAC generation via `secrets.token_urlsafe(32)`.
- `hash_otac(otac)` — SHA-256 hash of OTAC for storage; plain OTAC is only returned to admin when issuing codes.
- `generate_ballot_hash(candidate_id)` — produces (ballot_hash, nonce). Ballot hash uses salt + candidate_id + nonce to anonymize ballots while keeping verifiable proof when nonce is revealed.
- `verify_ballot_hash(candidate_id, nonce, ballot_hash)` — recomputes hash and uses HMAC compare for integrity.

## Frontend architecture — templates & static assets

Templates are simple server-served HTML files in `templates/`. They include minimal templating (mostly static HTML) and rely on client-side JS to call JSON APIs.

Main templates:

- `templates/login.html` — Login and OTP verification UI. Loads `auth.js` and `scripts.js`.
- `templates/admin.html` — Admin dashboard: register voters, issue OTACs, view results, audit trail. Loads `admin.js`, `app.js`, and shared scripts.
- `templates/voter.html` — Voter portal for casting votes. Loads `voter.js` and shared scripts.
- `templates/index.html` — Landing page that links to sections.

Static JS files:

- `static/scripts.js` — Shared API helpers, DOM helpers, utility functions (fetch wrappers, notifications, etc.).
- `static/auth.js` — Login flow, OTP timer, resend OTP, handles temp tokens and final access token.
- `static/admin.js` — Admin-specific UI wiring (upload CSV, call `POST /admin/register-voters`, `POST /admin/issue-otacs`, display stats and audit trail).
- `static/voter.js` — Voter-specific UI for submitting OTAC and candidate choice (POST /voter/cast-vote).
- `static/app.js` — UI helpers (show/hide sections, particle background generation, theme toggles, and page init routines).

Styling & fonts (`static/styles.css` and `static/styles_clean.css`)

- The current theme uses a muted professional palette with CSS variables at the top of `styles.css`/`styles_clean.css`.
- Fonts are loaded in templates via a Google Fonts link:
  - Noto Sans (UI) and Roboto Mono (monospace areas) — see `<link href="https://fonts.googleapis.com/...` in the templates.
- Utility CSS classes provided by our stylesheet:
  - `.font-sans` and `.font-mono` to force Noto Sans or Roboto Mono where needed.
  - `.glass-card`, `.gradient-btn`, `.nav-btn`, `.input-field`, `.merkle-root` and helper classes.

## Icons — where they come from

- Font Awesome is used for icons and is loaded from a CDN via this link in templates:
  - `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />`
- The HTML uses Font Awesome classes (e.g., `<i class="fas fa-shield-alt"></i>`).
- Because Font Awesome is loaded via CDN, icons appear without bundling. To replace with local icons or another provider (e.g., Heroicons or SVG sprites):
  - Remove the CDN link and add local icon assets or inline SVGs in templates.
  - Update markup to use the new icon classes or inline SVG markup.

## How front-end talks to back-end (data flow)

- The front-end JS uses fetch to call the API routes in `main.py`.
  - Login flow: POST `/auth/login` -> if `requires_2fa` receive temp_token and show OTP UI -> POST `/auth/verify-otp` with OTP + temp_token -> get final access token.
  - Register voters: Admin uploads CSV -> POST `/admin/register-voters` (multipart upload) -> receives registration stats.
  - Issue OTACs: Admin submits voter IDs -> POST `/admin/issue-otacs` -> receives list of plain OTACs (admin should distribute them securely).
  - Cast vote: Voter posts OTAC + candidate id -> POST `/voter/cast-vote` -> receives ballot_hash, new merkle root, seq in response.
  - Results: GET `/results` or `/admin/results` for tallies and merkle root to display chart and root hash.
  - Merkle proof generation: GET `/admin/generate-proof/{ballot_hash}` or `/generate-proof/{ballot_hash}`

## Merkle tree internals and proofs

- Merkle tree lives in `data_structures/merkle_tree.py` and is mirrored in the DB via `MerkleLeaf` rows (one per ballot seq).
- When a ballot is added, VotingService:
  1. Generates ballot_hash and a sequence number (seq).
  2. Stores Ballot and MerkleLeaf in DB.
  3. Calls `merkle_tree.add_leaf(ballot_hash)` to update the in-memory Merkle tree root.
  4. Persists an `AuditEvent` containing prev_root and new_root.
- To produce a proof for a ballot, the service looks up the ballot by hash, determines its 0-based index (seq-1), and asks the MerkleTree for the proof for that leaf index. The proof returned is an ordered list of sibling hashes to recompute root on the client or another verifier.

## OTAC lifecycle

- Admin calls `issue_otacs` which:
  - Generates secure OTAC strings (random tokens).
  - Hashes the OTACs and stores the `otac_hash -> voter_id_hash` mapping as `OTACMapping` rows.
  - Returns the plain OTACs to the admin (these tokens are sensitive; distribute via secure channels).
- Voter uses an OTAC to cast a vote. On `/voter/cast-vote` the server:
  - Hashes supplied OTAC and looks up `OTACMapping` where `otac_hash` matches and `used == False`.
  - If mapping exists and voter hasn't voted, mark mapping used, set `Voter.has_voted=True`, increment tally, and save ballot.
  - This prevents re-use of the OTAC and enforces single-vote rules.

## Undo (demo) and audit

- In DEMO_MODE, `VotingService.undo_last_action` will pop the last AuditStack event and revert DB state as much as possible (rebuild Merkle tree from remaining `MerkleLeaf` rows, decrement tally, flip `has_voted` on voter, remove ballot rows).
- `AuditEvent` rows are persisted and can be downloaded or shown in UI. They contain prev_root and new_root so auditors can see the Merkle root changes.

## Where to change the theme, fonts, and icons

- Colors and theme variables: `static/styles.css` (and `static/styles_clean.css`) define CSS variables under `:root` (e.g., `--bg-900`, `--accent`, `--accent-deep`). Change these to adjust global theme colors.
- Fonts:
  - Templates include a Google Fonts link to load Noto Sans and Roboto Mono. Modify the `<link>` in `templates/*.html` if you want different fonts or to self-host fonts.
  - Utility classes `.font-sans` and `.font-mono` in the stylesheet ensure monospace where needed.
- Icons:
  - Icons come from Font Awesome CDN. Replace CDN link in templates with another provider or local SVGs to change icons.
- Buttons, card radii, shadows: change `.gradient-btn`, `.glass-card`, and `.nav-btn` rules in `static/styles.css`.

## Troubleshooting & dev tips

- If something looks off (fonts or icons not loading):
  - Confirm your browser can reach Google Fonts and Font Awesome CDN URLs. If blocked (airgapped environment), switch to self-hosted fonts/icons.
- If Redis is not installed, the project uses `MockRedis`. For production, install and configure Redis and set `REDIS_URL` in `.env`.
- If DB tables are missing: ensure `create_tables()` runs on startup (it is called in `main.py`). If using a custom DB URL, ensure migrations or schema creation are compatible.
- To inspect Merkle leaves/roots:
  - Use the admin endpoints `GET /admin/results` and `GET /admin/audit-trail` to fetch current data.

## Developer notes & common modifications

- To add a new candidate:
  - There's no candidate table — candidates are free-form string IDs. Add candidate IDs to the frontend selects in templates (`templates/*.html`). If you want canonical candidate metadata, add a `Candidate` DB model and update templates/API.
- To persist the Merkle tree between restarts:
  - The DB stores leaves (`MerkleLeaf`) and `AuditEvent` rows. `VotingService._load_existing_data` should on startup read those rows and reconstruct the in-memory `MerkleTree` instance. Currently it is a placeholder; implement rebuilding there by querying `MerkleLeaf` ordered by seq and calling `MerkleTree(leaf_hashes)`.
- To improve security:
  - Replace demo credential checks with proper user records and password hashing (bcrypt), use HTTPS, rotate `SECRET_KEY`, and harden token expiration.

## Files to inspect for deeper changes

- `services/voting_service.py`
- `data_structures/merkle_tree.py`
- `utils/crypto_utils.py`
- `database.py`
- `templates/*.html` and `static/*.js` for UI wiring
- `static/styles.css` for theme

## Contact / contribution

If you plan to extend this project, please open PRs with small, focused changes. For production work, insist on an independent security audit.

## Appendix — Quick reference (endpoints)

- `GET /login`, `GET /admin`, `GET /voter` — UI pages
- `POST /auth/login`, `POST /auth/verify-otp`, `POST /auth/resend-otp` — auth flows
- `POST /admin/register-voters` — upload CSV of voters
- `POST /admin/issue-otacs` — issue OTACs
- `POST /voter/cast-vote` — cast a vote (requires valid OTAC)
- `GET /results`, `GET /admin/results` — tallies and merkle root
- `GET /generate-proof/{ballot_hash}` and `GET /admin/generate-proof/{ballot_hash}` — merkle proofs
- `POST /verify-proof` — verify merkle proof
- `POST /api/undoLast` — undo last action (demo only)

End of WORKING.md
