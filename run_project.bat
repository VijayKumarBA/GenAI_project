@echo off
echo ============================================
echo   AI House Plan Generator - Windows Launcher
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

echo [1/4] Setting up Python virtual environment...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/4] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo [3/4] Setting up .env file...
if not exist ".env" (
    copy .env.example .env
    echo.
    echo  ** IMPORTANT: Open backend\.env and add your GEMINI_API_KEY **
    echo     Get a free key at: https://makersuite.google.com/app/apikey
    echo.
    pause
)

echo [4/4] Starting Flask backend in background...
start "Flask Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python app.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Setup and start frontend
echo.
echo Starting React frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies (first time only)...
    npm install
)

echo.
echo ============================================
echo  Backend:  http://localhost:5000
echo  Frontend: http://localhost:3000
echo ============================================
echo.
start "" "http://localhost:3000"
npm start
