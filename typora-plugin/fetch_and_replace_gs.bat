@echo off
REM Typora custom command wrapper script (Windows, Google Scholar mode)
REM Usage: fetch_and_replace_gs.bat "<selected_url>"
REM This version prioritizes Google Scholar for more accurate citation counts

setlocal

REM Get script directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%..\fetch_paper_info.py

REM Get the input URL
set URL=%~1

REM Call Python script with Google Scholar priority
REM This provides more accurate and up-to-date citation counts
python "%PYTHON_SCRIPT%" "%URL%" --use-google-scholar-citations 2>nul
if errorlevel 1 (
    python3 "%PYTHON_SCRIPT%" "%URL%" --use-google-scholar-citations
)

endlocal