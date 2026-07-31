@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  LMS: starting the app
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
    echo [ERROR] Not set up yet. Run setup.bat first.
    pause
    exit /b 1
)

echo Starting containers...
docker compose up -d --wait
if errorlevel 1 (
    echo [ERROR] Could not start the app. Run setup.bat first if you haven't, or check the output above.
    pause
    exit /b 1
)

echo Waiting for the frontend to come up...
for /l %%i in (1,1,30) do (
    curl -s -o nul http://localhost:5173
    if not errorlevel 1 goto :frontend_ready
    timeout /t 1 /nobreak >nul
)
:frontend_ready

start http://localhost:5173

echo.
echo ============================================
echo  App running at http://localhost:5173
echo  Press any key in THIS window when you're done to shut everything down.
echo ============================================
pause >nul

echo Shutting down...
docker compose down

echo Done.
pause
