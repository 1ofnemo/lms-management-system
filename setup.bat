@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  LMS one-time setup
echo  Builds the containers and seeds demo data.
echo  Safe to re-run.
echo ============================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker was not found. Install Docker Desktop first: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is installed but not running. Open Docker Desktop, wait for it to finish starting
    echo ^(the whale icon in the system tray stops animating^), then re-run this script.
    pause
    exit /b 1
)

if not exist .env (
    copy .env.example .env >nul
    echo Created .env - edit it and add your ANTHROPIC_API_KEY to enable AI grading ^(optional, the rest of the app works without it^).
    echo.
)

echo [1/3] Building images ^(first run downloads a few hundred MB, can take a few minutes^)...
docker compose build
if errorlevel 1 (
    echo [ERROR] Build failed, see above.
    pause
    exit /b 1
)

echo [2/3] Starting the database...
docker compose up -d --wait db
if errorlevel 1 (
    echo [ERROR] Database did not start, see above.
    pause
    exit /b 1
)

echo [3/3] Applying migrations and seeding demo data...
docker compose run --rm backend sh -c "alembic upgrade head && python -m scripts.seed_base && python -m scripts.seed_submissions && python -m scripts.seed_hardening && python -m scripts.seed_demo_dataset"
if errorlevel 1 (
    echo [ERROR] Migration/seeding failed, see above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup complete. Run run-app.bat to start the app.
echo ============================================
pause
