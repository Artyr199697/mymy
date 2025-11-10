#!/bin/bash

echo "========================================"
echo "  Image Uniqueizer Pro - Запуск"
echo "========================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python 3 не найден!"
    echo ""
    echo "Установите Python 3.7+ используя менеджер пакетов:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

echo "[OK] Python найден"
python3 --version
echo ""

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "[ОШИБКА] pip3 не найден!"
    exit 1
fi

echo "[OK] pip найден"
echo ""

# Установка зависимостей
echo "Проверка и установка зависимостей..."
echo ""
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось установить зависимости!"
    exit 1
fi

echo "[OK] Все зависимости установлены"
echo ""
echo "========================================"
echo "  Запуск Image Uniqueizer Pro..."
echo "========================================"
echo ""

# Запуск программы
python3 image_uniqueizer.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ОШИБКА] Программа завершилась с ошибкой"
    exit 1
fi

echo ""
echo "Программа завершена успешно!"
