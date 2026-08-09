@echo off
setlocal

echo This script sets FINAGE_API_KEY only for this process.
echo The value is not persisted system-wide and is not written to disk.
set /p FINAGE_API_KEY="Enter Finage API key: "

if not defined FINAGE_API_KEY (
  echo FINAGE_API_KEY was not provided.
  exit /b 1
)

set "FINAGE_API_KEY=%FINAGE_API_KEY%"
echo FINAGE_API_KEY is available only inside this script process.
echo Start the application from this script or set the variable in your current shell.
python "%~dp0..\src\main.py"
set "FINAGE_API_KEY="
endlocal
