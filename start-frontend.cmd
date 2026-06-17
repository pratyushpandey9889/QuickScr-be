@echo off
subst Q: /d >nul 2>&1
subst Q: "%~dp0.." >nul 2>&1
cd /d Q:\frontend
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
subst Q: /d >nul 2>&1

