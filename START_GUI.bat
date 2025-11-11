@echo off
REM ========================================
REM   Image Uniqueizer Pro - GUI Version
REM ========================================

echo.
echo Starting Image Uniqueizer Pro (GUI)...
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
pip install -q pillow numpy

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo Dependencies: OK
echo.
echo ========================================
echo Starting GUI...
echo ========================================
echo.

REM Start GUI
python image_uniqueizer.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Program crashed!
    pause
)

echo.
echo Done!
pause
