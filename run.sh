#!/bin/bash

echo "========================================"
echo "  Image Uniqueizer Pro - Web Interface"
echo "========================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python 3 не найден!"
    echo ""
    echo "Установите Python 3.7+ используя менеджер пакетов"
    exit 1
fi

echo "[OK] Python найден"
python3 --version
echo ""

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось установить зависимости!"
    exit 1
fi

echo "[OK] Все зависимости установлены"
echo ""
echo "========================================"
echo "  Запуск веб-интерфейса..."
echo "========================================"
echo ""
echo "Откроется окно браузера с программой!"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "========================================"
echo ""

# Запуск Streamlit
streamlit run app.py
