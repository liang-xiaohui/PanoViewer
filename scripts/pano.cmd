@echo off
setlocal
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0pano.py" %*
  exit /b %errorlevel%
)
python "%~dp0pano.py" %*
