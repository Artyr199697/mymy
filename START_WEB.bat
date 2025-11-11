@echo off
REM ========================================
REM   Image Uniqueizer Pro - Web Version
REM ========================================

echo.
echo Starting Image Uniqueizer Pro (Web)...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python: OK
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q streamlit pillow numpy piexif

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo Dependencies: OK
echo.
echo ========================================
echo Starting web interface...
echo ========================================
echo.
echo Browser will open automatically!
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

REM Start Streamlit
streamlit run app.py

pause
