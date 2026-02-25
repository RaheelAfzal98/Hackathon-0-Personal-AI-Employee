@echo off
REM Stop Script for AI Employee - Bronze Tier
REM Stops all running AI Employee processes

echo ========================================
echo AI Employee - Bronze Tier Shutdown
echo ========================================
echo.

echo Stopping AI Employee processes...
echo.

REM Stop File System Watcher
echo Stopping File System Watcher...
taskkill /F /FI "WINDOWTITLE eq AI Employee - File Watcher*" >nul 2>&1
if errorlevel 1 (
    echo   (Watcher already stopped or not running)
) else (
    echo   Watcher stopped
)

REM Stop Orchestrator
echo Stopping Orchestrator...
taskkill /F /FI "WINDOWTITLE eq AI Employee - Orchestrator*" >nul 2>&1
if errorlevel 1 (
    echo   (Orchestrator already stopped or not running)
) else (
    echo   Orchestrator stopped
)

REM Also kill any orphaned Python processes running our scripts
echo Cleaning up any remaining processes...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *filesystem_watcher*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *orchestrator*" >nul 2>&1

echo.
echo ========================================
echo AI Employee Stopped
echo ========================================
echo.
echo Note: Check Task Manager if any processes remain
echo Logs are available in the Logs/ folder
echo.
