@echo off
setlocal
PATH=%~dp0;%PATH%
python "%~dp0ccpt.py" %*
