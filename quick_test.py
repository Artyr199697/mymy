#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест исправлений
"""

from PIL import Image
import numpy as np
import colorsys
import os
from pathlib import Path
from datetime import datetime


def shift_hue(img, degrees):
    """Сдвиг оттенка"""
    img_array = np.array(img, dtype=np.float32) / 255.0
    hsv_array = np.zeros_like(img_array)

    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            r, g, b = img_array[i, j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            h = (h + degrees / 360.0) % 1.0
            hsv_array[i, j] = [h, s, v]

    rgb_array = np.zeros_like(img_array)
    for i in range(hsv_array.shape[0]):
        for j in range(hsv_array.shape[1]):
            h, s, v = hsv_array[i, j]
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            rgb_array[i, j] = [r, g, b]

    rgb_array = (rgb_array * 255).astype(np.uint8)
    return Image.fromarray(rgb_array)


def quick_test():
    """Быстрый тест с НОВЫМИ настройками"""
    print("=" * 60)
    print("БЫСТРЫЙ ТЕСТ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    print()

    # Новые цветовые схемы
    NEW_SCHEMES = [
        ("Золотистый", 60),
        ("Холодный", -90),
        ("Теплый", 90),
        ("Морской", -60),
        ("Виноградный", 120),
    ]

    # Проверка тестового изображения
    test_img = "test_images/test_red.png"
    if not os.path.exists(test_img):
        print(f"❌ Тестовое изображение не найдено: {test_img}")
        print("   Создайте папку test_images/ с тестовыми PNG")
        return

    print(f"✅ Загружено: {test_img}")
    print()

    img = Image.open(test_img)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Создание выходной папки с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"quick_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)

    print(f"📁 Выходная папка: {output_dir}/")
    print()
    print("Создание вариантов с НОВЫМИ цветовыми схемами:")
    print()

    for i, (name, hue_shift) in enumerate(NEW_SCHEMES, 1):
        # Применение сдвига
        result = shift_hue(img.copy(), hue_shift)

        # Сохранение
        output_path = output_dir / f"variant_{i}_{name}.png"
        result.save(output_path)

        percent = abs(hue_shift) / 360 * 100
        visibility = "ОЧЕНЬ ЗАМЕТНО" if abs(hue_shift) >= 90 else \
                    "ХОРОШО ЗАМЕТНО" if abs(hue_shift) >= 60 else \
                    "ЗАМЕТНО"

        print(f"  ✅ {i}. {name:20s} (Hue: {hue_shift:+4d}° / {percent:5.1f}%) - {visibility}")

    print()
    print("=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН!")
    print("=" * 60)
    print()
    print(f"Откройте папку: {output_dir.absolute()}/")
    print()
    print("СРАВНИТЕ изображения:")
    print("  • Оригинал: test_images/test_red.png")
    print(f"  • Варианты: {output_dir}/variant_*.png")
    print()
    print("ВЫ УВИДИТЕ, что цвета РЕАЛЬНО изменились!")
    print("Красное изображение стало желтым, синим, зеленым и т.д.")
    print()


if __name__ == "__main__":
    quick_test()
