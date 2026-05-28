@echo off
title SuRaksha - Agentic Regulatory Intelligence
color 0B

echo.
echo  ============================================================
echo   SuRaksha - Agentic Regulatory Intelligence ^& Compliance
echo   Canara Bank ^| SuRaksha 2024
echo  ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

:: ── Backend Setup ─────────────────────────────────────────────────────────
if not exist "backend\venv\Scripts\uvicorn.exe" (
    echo [SETUP] Installing backend dependencies...
    python -m venv backend\venv
    backend\venv\Scripts\pip install -r backend\requirements.txt -q
    if errorlevel 1 (
        echo [ERROR] Backend install failed. Check requirements.txt
        pause
        exit /b 1
    )
    echo [OK] Backend ready.
    echo.
)

:: ── Streamlit Setup ───────────────────────────────────────────────────────
if not exist "streamlit_app\venv\Scripts\streamlit.exe" (
    echo [SETUP] Installing Streamlit dependencies...
    python -m venv streamlit_app\venv
    streamlit_app\venv\Scripts\pip install -r streamlit_app\requirements.txt -q
    if errorlevel 1 (
        echo [ERROR] Streamlit install failed. Check streamlit_app/requirements.txt
        pause
        exit /b 1
    )
    echo [OK] Streamlit ready.
    echo.
)

:: ── Launch Backend ────────────────────────────────────────────────────────
echo [START] Launching SuRaksha Backend (FastAPI on port 8000)...
start "SuRaksha Backend" cmd /k "set PYTHONIOENCODING=utf-8 && cd /d %~dp0backend && ..\backend\venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait for backend
echo [WAIT] Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

:: ── Launch Streamlit ──────────────────────────────────────────────────────
echo [START] Launching SuRaksha Dashboard (Streamlit on port 8501)...
start "SuRaksha Dashboard" cmd /k "set PYTHONIOENCODING=utf-8 && cd /d %~dp0streamlit_app && ..\streamlit_app\venv\Scripts\streamlit run app.py --server.port 8501 --server.headless false"

echo.
echo  ============================================================
echo   SuRaksha is running!
echo.
echo   Backend API  :  http://localhost:8000
echo   API Docs     :  http://localhost:8000/docs
echo   Dashboard    :  http://localhost:8501
echo  ============================================================
echo.

timeout /t 5 /nobreak >nul
start "" http://localhost:8501
pause
