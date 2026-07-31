# LMS

React + Bootstrap · FastAPI · PostgreSQL · Claude API grading · JWT auth.

A functional demo of three mechanisms: mastery grouping (advanced/average/struggling
buckets), AI-graded submissions, and DAG-based roadmap recommendation.

## Run it

```bash
# 1. Database (needs Docker Desktop running)
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # fill in ANTHROPIC_API_KEY for live AI grading
alembic upgrade head

# 3. Seed data (see "Seeding" below -- order matters)
python -m scripts.seed_base
python -m scripts.seed_submissions
python -m scripts.seed_hardening
python -m scripts.seed_demo_dataset

# 4. Run the backend (no --reload -- restart manually after backend code changes)
uvicorn app.main:app --port 8001

# 5. Frontend, in a separate terminal
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend: http://localhost:8001/docs · Frontend: http://localhost:5173

## Seeding

Run these four scripts in order, right after `alembic upgrade head`. The first three
only create structure (accounts, topics, assignments); the last one is the single
authoritative source for every student's grade history, so there's exactly one place
that decides what a submission history looks like instead of it being scattered
across scripts.

1. `python -m scripts.seed_base` — staff accounts, the original 6 students, the first 4
   topics, and topic 1's assignments. Makes the chain work on a genuinely empty database;
   without it, the other three scripts have nothing to build on.
2. `python -m scripts.seed_submissions` — assignments for topics 2-4.
3. `python -m scripts.seed_hardening` — a 5th topic (a real prerequisite convergence,
   needing both Word Problems and Quadratic Equations, not just a longer chain), its
   assignments, and 5 more student accounts.
4. `python -m scripts.seed_demo_dataset` — adds 13 more students (24 total, 8 per bucket)
   and generates every student's submission/mastery history: exactly one submission per
   assignment, no student ever submitting to the same assignment twice. This one **wipes
   and rebuilds** the `submissions`/`mastery_scores` tables every time it runs, so
   re-running it always yields the same clean result rather than piling on top of
   whatever's already there — deliberately different from the first three, which are
   additive and skip if their data already exists.

None of these call the Claude API — every score and feedback string is directly
authored. Verified end-to-end against a genuinely fresh, empty database (`docker compose up`
→ `alembic upgrade head` → all four scripts in order → backend serving real logins and
correct, duplicate-free data) — not just assumed to work.

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
