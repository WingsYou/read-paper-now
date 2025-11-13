@echo off
REM Typora 自定义命令包装脚本 (Windows)
REM 用法: fetch_and_replace.bat "<selected_url>"

setlocal

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%..\fetch_paper_info.py

REM 获取传入的 URL
set URL=%~1

REM 调用 Python 脚本
python "%PYTHON_SCRIPT%" "%URL%" 2>nul
if errorlevel 1 (
    python3 "%PYTHON_SCRIPT%" "%URL%"
)

endlocal
