@echo off
REM Typora custom command wrapper script (Windows)
REM Usage: fetch_and_replace.bat "<selected_url>"

setlocal

REM Get script directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%..\fetch_paper_info.py

REM Get the input URL
set URL=%~1

REM Call Python script to fetch paper information
REM Using default mode (Semantic Scholar with automatic fallback to Google Scholar)
python "%PYTHON_SCRIPT%" "%URL%" 2>nul
if errorlevel 1 (
    python3 "%PYTHON_SCRIPT%" "%URL%"
)

endlocal