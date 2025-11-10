@echo off
chcp 65001 >nul
echo ========================================
echo   Image Uniqueizer Pro - Запуск
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.7+ с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python найден
python --version
echo.

REM Проверка pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] pip не найден!
    pause
    exit /b 1
)

echo [OK] pip найден
echo.

REM Установка зависимостей
echo Проверка и установка зависимостей...
echo.
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось установить зависимости!
    pause
    exit /b 1
)

echo [OK] Все зависимости установлены
echo.
echo ========================================
echo   Запуск Image Uniqueizer Pro...
echo ========================================
echo.

REM Запуск программы
python image_uniqueizer.py

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Программа завершилась с ошибкой
    pause
    exit /b 1
)

echo.
echo Программа завершена успешно!
pause
