@echo off
title DevHub - Safe Local Developer Social Network
color 0A

echo =====================================================================
echo   DevHub - Developer Social Network ^& Project Showcase
echo   100%% Local-First, Safe PC Architecture
echo =====================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Check Virtual Environment
if not exist ".venv" (
    echo [*] Creating isolated local virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Install Dependencies
echo [*] Installing and verifying dependencies...
call .\.venv\Scripts\pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Could not install all packages silently. Retrying with verbose output...
    call .\.venv\Scripts\pip install -r requirements.txt
)

echo.
echo =====================================================================
echo  [SUCCESS] Environment verified and dependencies ready!
echo  Launching DevHub on http://127.0.0.1:5000 ...
echo =====================================================================
echo.

:: Open default browser after a brief delay in the background
start "" timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000

:: Run the application
call .\.venv\Scripts\python run.py

pause
