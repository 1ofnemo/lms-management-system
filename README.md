# LMS

React + Bootstrap · FastAPI · PostgreSQL · Claude API grading · JWT auth.

A functional demo of three mechanisms: mastery grouping (advanced/average/struggling
buckets), AI-graded submissions, and DAG-based roadmap recommendation.

## Run it

Only requirement: **Docker Desktop**, installed and running. Nothing else needs to be
on your machine — the app, its database, and all dependencies run in containers.

1. Double-click `setup.bat` (one time only). It builds the containers and loads demo
   data. Takes a few minutes the first time.
2. Double-click `run-app.bat` every time you want to use the app. It starts everything
   and opens http://localhost:5173 in your browser. Leave that window open; press any
   key in it when you're done to shut the app down.

Don't have Docker Desktop? Install it from
https://www.docker.com/products/docker-desktop/, then run `setup.bat`.

Want AI grading to actually call Claude instead of using pre-seeded results? Open the
`.env` file created by `setup.bat` and set `ANTHROPIC_API_KEY=<your key>`, then re-run
`run-app.bat`. Everything else works without a key.

Backend: http://localhost:8001/docs · Frontend: http://localhost:5173

## Seeding

`setup.bat` runs these four scripts in order, right after the database migrations.
The first three only create structure (accounts, topics, assignments); the last one is
the single authoritative source for every student's grade history, so there's exactly
one place that decides what a submission history looks like instead of it being
scattered across scripts.

1. `seed_base` — staff accounts, the original 6 students, the first 4 topics, and
   topic 1's assignments. Makes the chain work on a genuinely empty database; without
   it, the other three scripts have nothing to build on.
2. `seed_submissions` — assignments for topics 2-4.
3. `seed_hardening` — a 5th topic (a real prerequisite convergence, needing both Word
   Problems and Quadratic Equations, not just a longer chain), its assignments, and 5
   more student accounts.
4. `seed_demo_dataset` — adds 13 more students (24 total, 8 per bucket) and generates
   every student's submission/mastery history: exactly one submission per assignment,
   no student ever submitting to the same assignment twice. This one **wipes and
   rebuilds** the `submissions`/`mastery_scores` tables every time it runs, so
   re-running `setup.bat` always yields the same clean result rather than piling on top
   of whatever's already there — deliberately different from the first three, which are
   additive and skip if their data already exists.

None of these call the Claude API — every score and feedback string is directly
authored.

## Test accounts

All passwords: `pass1234`

| Role | Email |
|---|---|
| teacher | teacher2@test.com |
| admin | admin@test.com |
| student (advanced) | ava.martinez@test.com |
| student (average) | noah.patel@test.com |
| student (struggling) | mason.rivera@test.com |

21 more students exist across the same three groups (24 total, 8 per bucket) — see
`backend/scripts/seed_demo_dataset.py` for the full roster.

## Troubleshooting

- **"Docker is installed but not running"** — open Docker Desktop and wait for the
  whale icon in the system tray to stop animating, then re-run the script.
- **Ports already in use (5432, 8001, or 5173)** — something else on your machine is
  using one of those ports. Stop it, or edit the port mappings in `docker-compose.yml`.
- **Need to see backend/frontend logs** — run `docker compose logs -f backend` or
  `docker compose logs -f frontend` in a terminal from this folder while the app is
  running.
- **Want a completely clean slate** — run `docker compose down -v` in a terminal from
  this folder (this deletes the database volume), then run `setup.bat` again.

## Local dev without Docker (advanced/optional)

Only needed if you're actively developing and want hot-reload/debuggers attached to a
host-installed Python/Node instead of the containers. Everyday use should go through
`setup.bat`/`run-app.bat` above.

```bash
# 1. Database (needs Docker Desktop running)
docker compose up -d db

# 2. Backend
cd backend
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # fill in ANTHROPIC_API_KEY for live AI grading
alembic upgrade head
python -m scripts.seed_base
python -m scripts.seed_submissions
python -m scripts.seed_hardening
python -m scripts.seed_demo_dataset
uvicorn app.main:app --port 8001 --reload

# 3. Frontend, in a separate terminal
cd frontend
npm install
cp .env.example .env
npm run dev
```
