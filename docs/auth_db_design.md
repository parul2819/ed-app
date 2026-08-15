# Auth & Database Design — Learn with Masti

## Login Model (Confirmed)
- **Parent**: full account — email + password (standard auth, password reset support later)
- **Child**: profile under a parent — logs in via a short numeric PIN (no email needed)
- One parent can have multiple children (siblings), each with their own PIN and their own progress

## Database: PostgreSQL (with pgvector extension enabled, unused for now)
Running via Docker (`postgres` image + `pgvector/pgvector` variant so the extension is available without a later migration).

## Schema (v1 — scalable design)

### `parents`
| column | type | notes |
|---|---|---|
| id | UUID (PK) | |
| email | text, unique, not null | |
| password_hash | text, not null | bcrypt/argon2, never plaintext |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### `children`
| column | type | notes |
|---|---|---|
| id | UUID (PK) | |
| parent_id | UUID (FK → parents.id) | cascade delete |
| name | text, not null | display name |
| pin_hash | text, not null | hashed, not plaintext, even though it's a short PIN |
| grade | int, default 3 | future-proofs for other classes later |
| created_at | timestamptz | |

**Index:** `(parent_id)` — fast lookup of "all children for this parent"

### `practice_sessions`
Tracks each practice attempt (scored or open) — this is the growth table, will have the most rows.

| column | type | notes |
|---|---|---|
| id | UUID (PK) | |
| child_id | UUID (FK → children.id) | cascade delete |
| topic | text | addition / subtraction / multiplication |
| track | text | school / olympiad |
| mode | text | "scored" / "open" |
| started_at | timestamptz | |
| completed_at | timestamptz, nullable | |

**Index:** `(child_id, topic)`, `(child_id, started_at)` — for progress queries

### `question_attempts`
One row per question answered within a session.

| column | type | notes |
|---|---|---|
| id | UUID (PK) | |
| session_id | UUID (FK → practice_sessions.id) | cascade delete |
| question_id | text | matches id from content/questions/*.json, or LLM-generated id |
| selected_answer | text | |
| is_correct | boolean | |
| answered_at | timestamptz | |

**Index:** `(session_id)`

### `child_progress` (aggregated/denormalized for fast dashboard reads)
Avoids recalculating stats from question_attempts every time the progress screen loads.

| column | type | notes |
|---|---|---|
| child_id | UUID (FK → children.id) | |
| topic | text | |
| track | text | |
| questions_attempted | int | |
| questions_correct | int | |
| stars_earned | int | |
| updated_at | timestamptz | |

**Primary key:** `(child_id, topic, track)` — one row per child per topic/track combo, updated incrementally after each session.

## Why this design scales
- UUIDs (not auto-increment ints) — safe for eventual multi-region/sharding, no ID collision risk when merging data later
- `practice_sessions` + `question_attempts` split — keeps raw event data separate from session metadata, standard event-sourcing-friendly pattern
- `child_progress` as a materialized/aggregated table — avoids expensive COUNT/SUM queries on every app open once data grows to millions of rows
- pgvector extension pre-installed — zero-downtime to adopt later (e.g., semantic duplicate-question detection) without a DB migration
- Parent/child separation mirrors real-world usage (siblings) and keeps auth (parents) cleanly separated from app-profile data (children) — easier to add parent-side features (billing, multiple schools) later without touching child data model

## Auth Flow (MVP)
1. Parent signs up (email + password) → `parents` row created, password hashed
2. Parent adds a child (name + sets a PIN) → `children` row created, PIN hashed
3. Parent logs in normally (JWT/session token)
4. Child login: parent selects child from a list (still under parent's session) OR a simplified device-level flow where the child taps their name + enters PIN — **decide UX later**, backend just needs a `POST /children/{id}/verify-pin` endpoint
5. All practice endpoints require a valid child session (not parent's)

## Next Step
Build with Claude Code:
- `docker-compose.yml` for Postgres (pgvector image)
- SQLAlchemy models matching this schema
- Alembic for migrations (so schema changes are tracked properly from day 1)
- Auth endpoints: parent signup/login, add child, child PIN verify
- Password/PIN hashing via `passlib` or `bcrypt`
