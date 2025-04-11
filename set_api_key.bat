@echo off
setlocal

REM Check if API key is already set
if defined FINAGE_API_KEY (
  echo API key is already set.
  goto :eof
)

REM Prompt for API key and secret key
set /p API_KEY="Enter API key: "
set /p SECRET_KEY="Enter secret key: "

REM Set API key in environment variables (temporary)
set FINAGE_API_KEY=%API_KEY%
set FINAGE_SECRET_KEY=%SECRET_KEY%

REM Set API key in environment variables (permanent)
setx FINAGE_API_KEY "%API_KEY%" /M
setx FINAGE_SECRET_KEY "%SECRET_KEY%" /M

echo API key has been set.

endlocal