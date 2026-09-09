@echo off
cd /d "%~dp0"
python -m uvicorn src.api:app --host 127.0.0.1 --port 8766 --reload
