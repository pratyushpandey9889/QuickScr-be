@echo off
cd /d "%~dp0..\backend"
if not exist logs mkdir logs
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > logs\uvicorn.out.log 2> logs\uvicorn.err.log

