#!/usr/bin/env python3
"""
Тестовый скрипт для проверки алгоритма уникализации
Работает без GUI
"""

from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import colorsys
import random
from pathlib import Path
import os


# Цветовые схемы (название: сдвиг Hue в градусах)
COLOR_SCHEMES = [
    ("Оригинал+", 0),
    ("Теплый_закат", 15),
    ("Холодный", -30),
    ("Виноградный", 25),
    ("Морской", -45),
    ("Лавандовый", 35),
    ("Лимонный", -15),
    ("Коралловый", 20),
    ("Бирюзовый", -40),
    ("Персиковый", 10)
]


def shift_hue(img, degrees):
    """Сдвиг оттенка (Hue) в HSV"""
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


def add_noise(img, noise_level):
    """Добавление едва заметного шума"""
    img_array = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, noise_level * 255, img_array.shape)
    noisy_array = img_array + noise
    noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_array)


def uniqueize_image(img, hue_shift):
    """Применение уникализации к изображению"""
    # 1. Сдвиг цветовой схемы
    if hue_shift != 0:
        img = shift_hue(img, hue_shift)

    # 2. Случайные изменения
    contrast_factor = random.uniform(0.95, 1.15)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_factor)

    brightness_factor = random.uniform(0.97, 1.08)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_factor)

    saturation_factor = random.uniform(0.92, 1.12)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)

    noise_level = random.uniform(0.005, 0.015)
    img = add_noise(img, noise_level)

    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

    if random.random() < 0.4:
        sharpness_factor = random.uniform(1.0, 1.15)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness_factor)

    return img


def process_images(input_dir, variant_count=5):
    """Обработка изображений"""
    print(f"🎨 Тестирование Image Uniqueizer Pro")
    print(f"=" * 50)
    print(f"Входная папка: {input_dir}")
    print(f"Количество вариантов: {variant_count}")
    print()

    # Создание выходной папки
    output_dir = Path("uniqueized_images")
    output_dir.mkdir(exist_ok=True)

    # Поиск изображений
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
        image_files.extend(Path(input_dir).glob(f"*{ext}"))

    if not image_files:
        print("❌ Изображения не найдены!")
        return

    print(f"Найдено изображений: {len(image_files)}")
    print()

    total_created = 0

    for img_path in image_files:
        print(f"📸 Обработка: {img_path.name}")

        try:
            # Открытие изображения
            img = Image.open(img_path)

            # Конвертация в RGB если необходимо
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Создание вариантов
            for i in range(variant_count):
                scheme_name, hue_shift = COLOR_SCHEMES[i % len(COLOR_SCHEMES)]

                # Применение уникализации
                unique_img = uniqueize_image(img.copy(), hue_shift)

                # Сохранение
                output_path = output_dir / f"{img_path.stem}_v{i+1}_{scheme_name}.jpg"
                unique_img.save(output_path, 'JPEG', quality=95, optimize=True)

                total_created += 1
                print(f"  ✅ Создан: {output_path.name}")

        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            continue

        print()

    print(f"=" * 50)
    print(f"✨ Готово!")
    print(f"Обработано изображений: {len(image_files)}")
    print(f"Создано вариантов: {total_created}")
    print(f"Папка с результатами: {output_dir.absolute()}")


if __name__ == "__main__":
    # Проверка существования тестовых изображений
    if Path("test_images").exists():
        process_images("test_images", variant_count=5)
    else:
        print("❌ Папка 'test_images' не найдена!")
        print("Запустите сначала: python3 create_test_images.py")
