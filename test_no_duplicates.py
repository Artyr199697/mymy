#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест: проверка, что нет дублирования файлов
"""

from pathlib import Path

def test_find_images():
    """Тест поиска изображений без дубликатов"""
    source_path = Path("test_images")

    # Старый способ (с дубликатами)
    print("=" * 60)
    print("ТЕСТ ПОИСКА ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    print()

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

    # Способ 1: БЕЗ удаления дубликатов (старый)
    image_files_old = []
    for ext in image_extensions:
        image_files_old.extend(source_path.glob(f"*{ext}"))
        image_files_old.extend(source_path.glob(f"*{ext.upper()}"))

    print(f"Способ 1 (старый - С дубликатами):")
    print(f"  Найдено файлов: {len(image_files_old)}")
    for f in sorted(image_files_old):
        print(f"    - {f.name}")
    print()

    # Способ 2: С удалением дубликатов (новый)
    image_files_new = []
    for ext in image_extensions:
        image_files_new.extend(source_path.glob(f"*{ext}"))
        image_files_new.extend(source_path.glob(f"*{ext.upper()}"))

    # Удаляем дубликаты
    image_files_new = sorted(list(set(image_files_new)))

    print(f"Способ 2 (новый - БЕЗ дубликатов):")
    print(f"  Найдено файлов: {len(image_files_new)}")
    for f in image_files_new:
        print(f"    - {f.name}")
    print()

    # Проверка
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    print()

    if len(image_files_old) == len(image_files_new):
        print("✅ Дубликатов НЕТ - всё хорошо!")
    else:
        duplicates = len(image_files_old) - len(image_files_new)
        print(f"❌ БЫЛО {duplicates} дубликатов!")
        print(f"   Старый способ: {len(image_files_old)} файлов")
        print(f"   Новый способ: {len(image_files_new)} файлов")
        print()
        print("✅ ИСПРАВЛЕНО: теперь дубликаты удаляются!")

    print()
    print("=" * 60)
    print("РАСЧЁТ ДЛЯ AVITO:")
    print("=" * 60)
    print()

    num_photos = len(image_files_new)
    num_ads = 5

    print(f"Фотографий в папке: {num_photos}")
    print(f"Количество объявлений: {num_ads}")
    print(f"Итого файлов будет создано: {num_photos} × {num_ads} = {num_photos * num_ads}")
    print()
    print(f"В каждой папке (объявлении): {num_photos} фотографий")
    print(f"Всего папок (объявлений): {num_ads}")
    print()


if __name__ == "__main__":
    test_find_images()
