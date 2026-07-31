@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  LMS one-time setup: installs dependencies
echo  and seeds demo data. Safe to re-run.
echo ============================================
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo [ERROR] winget ^(Windows Package Manager^) was not found, so Python/Node.js can't be auto-installed.
    echo Install Python and Node.js manually, then re-run this script.
    pause
    exit /b 1
)

rem `where python` alone is unreliable: Windows ships a fake python.exe "stub" (the
rem App Execution Alias in WindowsApps) on machines with no real Python installed, and
rem `where` finds it happily even though running it does nothing but redirect to the
rem Microsoft Store. Checking `python --version` actually invokes it, so the stub's
rem failure is caught instead of being mistaken for a real install.
set NEEDS_INSTALL=0

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found — installing via winget...
    winget install -e --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
    set NEEDS_INSTALL=1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found — installing via winget...
    winget install -e --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
    set NEEDS_INSTALL=1
)

if "%NEEDS_INSTALL%"=="1" (
    rem A freshly installed tool isn't on THIS window's PATH yet - Windows only updates
    rem PATH for new processes launched after the install, and this window already
    rem started. Rebuilding PATH from the registry here (instead of asking the user to
    rem close and reopen) picks the change up immediately in this same session.
    echo Refreshing this window's PATH so newly installed tools are recognized...
    for /f "usebackq skip=2 tokens=2,*" %%A in (`reg query "HKCU\Environment" /v Path 2^>nul`) do set "USER_PATH=%%B"
    for /f "usebackq skip=2 tokens=2,*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path`) do set "SYS_PATH=%%B"
    rem Registry PATH values are REG_EXPAND_SZ and can contain literal tokens like
    rem %SystemRoot% instead of the real path. A plain `set` only substitutes once, so
    rem those tokens would end up in PATH unexpanded. `call set` re-parses the line,
    rem giving a second substitution pass that resolves them.
    call set "SYS_PATH=%SYS_PATH%"
    call set "USER_PATH=%USER_PATH%"
    set "PATH=%SYS_PATH%;%USER_PATH%"

    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python still isn't available after installing it. Close this window, run setup.bat
        echo again, and if it still fails, install manually: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    npm --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Node.js still isn't available after installing it. Close this window, run setup.bat
        echo again, and if it still fails, install manually: https://nodejs.org/
        pause
        exit /b 1
    )
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
