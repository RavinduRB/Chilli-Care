@echo off
REM ChilliDoc AI - Windows Startup Script

echo ========================================
echo ChilliDoc AI - Startup Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python detected
echo.

REM Create virtual environment if not exists
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully
) else (
    echo [2/4] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/4] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements_web.txt --quiet
echo Dependencies installed successfully
echo.

REM Check for model file
if not exist "best_chilli_disease_model.h5" (
    if not exist "chilli_disease_detection_model_final.h5" (
        if not exist "chilli_disease_detection_model_final.keras" (
            echo WARNING: No model file found!
            echo Please ensure you have trained the model first using the Jupyter notebook.
            echo Looking for one of these files:
            echo   - best_chilli_disease_model.h5
            echo   - chilli_disease_detection_model_final.h5
            echo   - chilli_disease_detection_model_final.keras
            echo.
            pause
        )
    )
)

echo ========================================
echo Starting ChilliDoc AI Server...
echo ========================================
echo.
echo Server will start at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the Flask application
python app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
