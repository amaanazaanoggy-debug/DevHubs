@echo off
title DevHub Server
echo Starting DevHub on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
call .\.venv\Scripts\python run.py
pause
