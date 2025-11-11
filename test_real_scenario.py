#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реальный тест: создание файлов для проверки дублирования
"""

from pathlib import Path
from PIL import Image
import shutil

def create_test_scenario():
    """Создаём тестовую папку с 3 фотографиями"""

    # Создаём временную папку
    test_dir = Path("TEST_SCENARIO")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВОГО СЦЕНАРИЯ")
    print("=" * 60)
    print()
    print(f"Папка: {test_dir.absolute()}")
    print()

    # Копируем 3 тестовых изображения
    source_images = list(Path("test_images").glob("*.png"))[:3]

    for i, src in enumerate(source_images, 1):
        dest = test_dir / f"photo_{i}.png"
        shutil.copy(src, dest)
        print(f"✅ Создан: {dest.name}")

    print()
    print("=" * 60)
    print("ТЕСТ ПОИСКА ФАЙЛОВ")
    print("=" * 60)
    print()

    # Тест старого способа
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

    print("Старый способ (БЕЗ set()):")
    image_files_old = []
    for ext in image_extensions:
        found_lower = list(test_dir.glob(f"*{ext}"))
        found_upper = list(test_dir.glob(f"*{ext.upper()}"))
        image_files_old.extend(found_lower)
        image_files_old.extend(found_upper)

        if found_lower or found_upper:
            print(f"  {ext}: найдено {len(found_lower)} + {len(found_upper)} = {len(found_lower) + len(found_upper)}")

    print(f"  ИТОГО: {len(image_files_old)} файлов")
    print()

    # Тест нового способа
    print("Новый способ (С set()):")
    image_files_new = []
    for ext in image_extensions:
        image_files_new.extend(test_dir.glob(f"*{ext}"))
        image_files_new.extend(test_dir.glob(f"*{ext.upper()}"))

    image_files_new = list(set(image_files_new))
    print(f"  ИТОГО: {len(image_files_new)} файлов (дубликаты удалены)")
    print()

    # Результат
    print("=" * 60)
    print("РАСЧЁТ ДЛЯ AVITO:")
    print("=" * 60)
    print()

    num_photos = len(image_files_new)
    num_ads = 5

    print(f"📸 Фотографий: {num_photos}")
    print(f"📋 Объявлений: {num_ads}")
    print()
    print(f"СТАРЫЙ СПОСОБ:")
    print(f"  Обработано файлов: {len(image_files_old)} × {num_ads} = {len(image_files_old) * num_ads}")
    print()
    print(f"НОВЫЙ СПОСОБ:")
    print(f"  Обработано файлов: {num_photos} × {num_ads} = {num_photos * num_ads} ✅")
    print()

    if len(image_files_old) > len(image_files_new):
        print(f"⚠️  ВНИМАНИЕ: Старый способ обрабатывал {len(image_files_old) - len(image_files_new)} лишних файлов!")
        print(f"   Это объясняет, почему получалось {len(image_files_old) * num_ads} вместо {num_photos * num_ads}")
    else:
        print("✅ Дубликатов нет!")

    print()
    print(f"Тестовая папка: {test_dir.absolute()}")
    print("Используйте эту папку для тестирования в Streamlit!")
    print()


if __name__ == "__main__":
    create_test_scenario()
