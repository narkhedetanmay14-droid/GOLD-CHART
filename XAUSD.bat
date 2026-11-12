@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo XAU/USD AI Trading Research ^& Prediction System
echo Project Directory: %~dp0
echo ===================================================

cd /d "%~dp0"

set PYTHON_EXE=%~dp0.venv\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
    echo Run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

set MODE=%1
if "%MODE%"=="" set MODE=live

if /i "%MODE%"=="setup" goto setup
if /i "%MODE%"=="check" goto check
if /i "%MODE%"=="verify" goto verify
if /i "%MODE%"=="notebooks" goto notebooks
if /i "%MODE%"=="live" goto live
if /i "%MODE%"=="paper" goto paper
if /i "%MODE%"=="report" goto report

echo [ERROR] Unknown or invalid command: %MODE%
goto usage

:check
echo Running project preflight checks...
"%PYTHON_EXE%" run_project.py --mode check
if %errorlevel% neq 0 (
    echo [ERROR] Preflight tests failed!
    pause
    exit /b %errorlevel%
)
echo [SUCCESS] All preflight tests passed successfully.
goto end

:setup
echo Installing required dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt
goto end

:verify
echo Running Full Independent Verification Suite...
"%PYTHON_EXE%" run_project.py --mode verify
goto end

:notebooks
echo Launching Jupyter Lab / Notebooks...
"%PYTHON_EXE%" -m jupyter lab --notebook-dir=notebooks
goto end

:live
echo Running preflight checks before live session...
"%PYTHON_EXE%" run_project.py --mode check
if %errorlevel% neq 0 (
    echo [ERROR] Preflight checks failed. Aborting live launch.
    pause
    exit /b %errorlevel%
)
echo Launching Live SignalR Market Data ^& Prediction System...
"%PYTHON_EXE%" run_project.py --mode live
goto end

:paper
echo Running preflight checks before paper trading...
"%PYTHON_EXE%" run_project.py --mode check
if %errorlevel% neq 0 (
    echo [ERROR] Preflight checks failed. Aborting paper launch.
    pause
    exit /b %errorlevel%
)
echo Launching Paper Trading System...
"%PYTHON_EXE%" run_project.py --mode paper
goto end

:report
echo Generating Performance Report...
"%PYTHON_EXE%" run_project.py --mode report
goto end

:usage
echo Usage: XAUSD.bat [setup^|check^|verify^|notebooks^|live^|paper^|report]
goto end

:end
pause
