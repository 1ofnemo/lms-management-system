@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  LMS: starting backend + frontend
echo ============================================
echo.

if not exist backend\.venv\Scripts\activate.bat (
    echo [ERROR] Backend not set up yet. Run setup.bat first.
    pause
    exit /b 1
)
if not exist backend\.env (
    echo [ERROR] backend\.env is missing. Run setup.bat first.
    pause
    exit /b 1
)
if not exist frontend\node_modules (
    echo [ERROR] Frontend not set up yet. Run setup.bat first.
    pause
    exit /b 1
)
if not exist frontend\.env (
    echo [ERROR] frontend\.env is missing. Run setup.bat first.
    pause
    exit /b 1
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

echo [1/3] Starting database container...
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

echo [2/3] Starting backend and frontend windows...
start "LMS Backend" /D "%~dp0backend" cmd /k "call .venv\Scripts\activate.bat && uvicorn app.main:app --port 8001"
start "LMS Frontend" /D "%~dp0frontend" cmd /k "npm run dev"

echo [3/3] Waiting for the frontend to come up...
for /l %%i in (1,1,20) do (
    curl -s -o nul http://localhost:5173
    if not errorlevel 1 goto :frontend_ready
    timeout /t 1 /nobreak >nul
)
:frontend_ready

start http://localhost:5173

echo.
echo ============================================
echo  App running at http://localhost:5173
echo  Backend and frontend are in their own windows (logs visible there).
echo  Press any key in THIS window when you're done to shut everything down.
echo ============================================
pause >nul

echo Shutting down...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8001 ^| findstr LISTENING') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%p /F >nul 2>&1

echo Done. You can close the backend/frontend windows if they're still open.
pause
