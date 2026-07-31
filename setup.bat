@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  LMS one-time setup: installs dependencies
echo  and seeds demo data. Safe to re-run.
echo ============================================
echo.

set NEEDS_RESTART=0

where winget >nul 2>&1
if errorlevel 1 (
    echo [ERROR] winget ^(Windows Package Manager^) was not found, so Python/Node.js can't be auto-installed.
    echo Install Python and Node.js manually, then re-run this script.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found — installing via winget...
    winget install -e --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
    set NEEDS_RESTART=1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo Node.js not found — installing via winget...
    winget install -e --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
    set NEEDS_RESTART=1
)

if "%NEEDS_RESTART%"=="1" (
    echo.
    echo Some tools were just installed. Close this window, then double-click setup.bat again to continue.
    pause
    exit /b 0
)

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

echo [1/5] Starting database container...
docker compose up -d
if errorlevel 1 (
    echo [ERROR] Could not start the database container. Check the output above.
    pause
    exit /b 1
)

echo Waiting for database to accept connections...
for /l %%i in (1,1,15) do (
    docker compose exec -T db pg_isready -U lms >nul 2>&1
    if not errorlevel 1 goto :db_ready
    timeout /t 2 /nobreak >nul
)
echo [ERROR] Database did not become ready in time.
pause
exit /b 1
:db_ready

echo [2/5] Setting up backend virtual environment...
cd backend
if not exist .venv (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create the virtual environment, see above.
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat

if not exist .venv\Scripts\pip.exe (
    echo [ERROR] .venv exists but has no pip - it's likely broken from a previous failed run.
    echo Delete the backend\.venv folder and re-run this script.
    pause
    exit /b 1
)

echo [3/5] Installing backend packages...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed, see above.
    pause
    exit /b 1
)

if not exist .env (
    copy .env.example .env >nul
    echo Created backend\.env - edit it to add your ANTHROPIC_API_KEY for AI grading.
)

echo [4/5] Applying migrations and seeding demo data...
alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Database migration failed, see above.
    pause
    exit /b 1
)

python -m scripts.seed_base && python -m scripts.seed_submissions && python -m scripts.seed_hardening && python -m scripts.seed_demo_dataset
if errorlevel 1 (
    echo [ERROR] Seeding failed, see above.
    pause
    exit /b 1
)

echo [5/5] Installing frontend packages...
cd ..\frontend
if not exist .env (
    copy .env.example .env >nul
)
call npm install
if errorlevel 1 (
    echo [ERROR] npm install failed, see above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup complete. Run run-app.bat to start the app.
echo ============================================
pause
