@echo off
chcp 65001 >nul
echo ========================================
echo   Image Uniqueizer Pro - Web Interface
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
    pause
    exit /b 1
)

echo [OK] Python найден
python --version
echo.

REM Установка зависимостей
echo Установка зависимостей...
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось установить зависимости!
    pause
    exit /b 1
)

echo [OK] Все зависимости установлены
echo.
echo ========================================
echo   Запуск веб-интерфейса...
echo ========================================
echo.
echo Откроется окно браузера с программой!
echo.
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

REM Запуск Streamlit
streamlit run app.py

pause
