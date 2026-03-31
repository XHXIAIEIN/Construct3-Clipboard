@echo off
cd /d "%~dp0"
python -m uvicorn src.api:app --host 0.0.0.0 --port 8766 --reload
