#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Визуальный тест изменения цветов
Показывает, как hue_shift влияет на изображение
"""

from PIL import Image
import numpy as np
import colorsys


def shift_hue(img, degrees):
    """Сдвиг оттенка (копия из основного кода)"""
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


def create_color_palette(width=200, height=100):
    """Создает палитру основных цветов для демонстрации"""
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    # Градиент по Hue
    for x in range(width):
        hue = x / width  # 0.0 до 1.0
        for y in range(height):
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            pixels[x, y] = (int(r*255), int(g*255), int(b*255))

    return img


def test_hue_shifts():
    """Тест различных значений hue shift"""
    print("=" * 60)
    print("ВИЗУАЛЬНЫЙ ТЕСТ ИЗМЕНЕНИЯ ЦВЕТОВ")
    print("=" * 60)
    print()

    # Создаем тестовую палитру
    original = create_color_palette(600, 100)
    original.save("color_test_original.png")
    print("✅ Создан оригинал: color_test_original.png")

    # Тесты разных сдвигов
    test_cases = [
        (0, "Оригинал+ (БЕЗ ИЗМЕНЕНИЙ!)"),
        (15, "Теплый закат (ЕДВА ЗАМЕТНО)"),
        (30, "Сдвиг 30° (СЛАБО ЗАМЕТНО)"),
        (60, "Сдвиг 60° (ХОРОШО ЗАМЕТНО)"),
        (90, "Сдвиг 90° (ОЧЕНЬ ЗАМЕТНО)"),
        (120, "Сдвиг 120° (СИЛЬНО ЗАМЕТНО)"),
        (180, "Противоположные цвета (МАКСИМАЛЬНО)"),
    ]

    print()
    print("Создаю варианты с разными сдвигами Hue:")
    print()

    for degrees, description in test_cases:
        if degrees == 0:
            shifted = original.copy()
        else:
            shifted = shift_hue(original.copy(), degrees)

        filename = f"color_test_hue_{degrees:+04d}.png"
        shifted.save(filename)

        # Вычисляем процент от цветового круга
        percent = abs(degrees) / 360 * 100

        print(f"  📸 {filename}")
        print(f"     Сдвиг: {degrees:+4d}° ({percent:5.1f}% цветового круга)")
        print(f"     {description}")
        print()

    print("=" * 60)
    print("АНАЛИЗ ТЕКУЩИХ НАСТРОЕК:")
    print("=" * 60)
    print()

    current_schemes = [
        ("Оригинал+", 0),
        ("Теплый закат", 15),
        ("Холодный", -30),
        ("Виноградный", 25),
        ("Морской", -45),
    ]

    print("Текущие цветовые схемы:")
    print()
    for name, hue in current_schemes:
        percent = abs(hue) / 360 * 100
        visibility = "НЕ ЗАМЕТНО" if abs(hue) < 20 else \
                    "ЕДВА ЗАМЕТНО" if abs(hue) < 40 else \
                    "ЗАМЕТНО"
        print(f"  • {name:20s} → {hue:+4d}° ({percent:4.1f}%) - {visibility}")

    print()
    print("=" * 60)
    print("ВЫВОД:")
    print("=" * 60)
    print()
    print("❌ ПРОБЛЕМА: Большинство сдвигов < 45° (12.5%)")
    print("   Это СЛИШКОМ МАЛО для визуального восприятия!")
    print()
    print("✅ РЕКОМЕНДАЦИЯ: Использовать сдвиги 60-120° (17-33%)")
    print("   Это обеспечит ЗАМЕТНОЕ изменение цветов")
    print()
    print("🔍 Откройте файлы color_test_hue_*.png")
    print("   чтобы УВИДЕТЬ разницу своими глазами!")
    print()


def test_real_image():
    """Тест на реальном изображении, если оно есть"""
    import os

    test_images = ["test_images/test_red.png",
                   "test_images/test_blue.png",
                   "test_images/test_green.png"]

    for test_img_path in test_images:
        if os.path.exists(test_img_path):
            print("=" * 60)
            print(f"ТЕСТ НА РЕАЛЬНОМ ИЗОБРАЖЕНИИ: {test_img_path}")
            print("=" * 60)
            print()

            img = Image.open(test_img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            base_name = os.path.splitext(os.path.basename(test_img_path))[0]

            shifts = [0, 15, 30, 60, 90, 120]
            for shift in shifts:
                if shift == 0:
                    result = img.copy()
                else:
                    result = shift_hue(img.copy(), shift)

                output_name = f"real_test_{base_name}_hue_{shift:+04d}.png"
                result.save(output_name)
                print(f"  ✅ {output_name}")

            print()
            break
    else:
        print("⚠️  Тестовые изображения не найдены")
        print("    Создайте папку test_images/ с тестовыми PNG")
        print()


if __name__ == "__main__":
    test_hue_shifts()
    print()
    test_real_image()

    print("=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН!")
    print("=" * 60)
    print()
    print("Откройте созданные файлы и сравните:")
    print("  1. color_test_original.png - оригинал")
    print("  2. color_test_hue_*.png - варианты с разными сдвигами")
    print("  3. real_test_*.png - реальные изображения (если есть)")
    print()
    print("ВЫ УВИДИТЕ своими глазами, как меняются цвета!")
    print()
