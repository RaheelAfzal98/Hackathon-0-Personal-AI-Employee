@echo off
REM Start Script for AI Employee - Bronze Tier
REM Starts both File System Watcher and Orchestrator

echo ========================================
echo AI Employee - Bronze Tier Startup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    exit /b 1
)

REM Check if vault path is provided
if "%~1"=="" (
    set VAULT_PATH=.
) else (
    set VAULT_PATH=%1
)

echo Vault Path: %VAULT_PATH%
echo.

REM Start File System Watcher
echo Starting File System Watcher...
start "AI Employee - File Watcher" python scripts\filesystem_watcher.py "%VAULT_PATH%" --interval 30

REM Wait a moment for watcher to initialize
timeout /t 2 /nobreak >nul

REM Start Orchestrator
echo Starting Orchestrator...
start "AI Employee - Orchestrator" python scripts\orchestrator.py "%VAULT_PATH%" --interval 60

echo.
echo ========================================
echo AI Employee Started Successfully!
echo ========================================
echo.
echo Running processes:
echo   - File System Watcher (monitoring Inbox/)
echo   - Orchestrator (triggering Qwen Code)
echo.
echo To stop: Run stop.bat or close these terminal windows
echo To view logs: Check the Logs/ folder
echo.
