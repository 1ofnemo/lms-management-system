# LMS

React + Bootstrap · FastAPI · PostgreSQL · Claude API grading · JWT auth.

## Run it

```bash
# 1. Database (needs Docker Desktop running)
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # fill in ANTHROPIC_API_KEY when Sprint 3 needs it
alembic upgrade head           # once there are migrations to run
uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend: http://localhost:8000/health · Frontend: http://localhost:5173

Role Email
student student@test.com
teacher teacher2@test.com
admin admin@test.com

all password pass1234

## Status

Sprint 0 scaffolding only — no models, auth, or routes yet beyond a health check. See the sprint backlog for what's next.
