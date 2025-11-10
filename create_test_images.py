#!/usr/bin/env python3
"""
Скрипт для создания тестовых изображений
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename, color, text):
    """Создание тестового изображения"""
    img = Image.new('RGB', (800, 600), color=color)
    draw = ImageDraw.Draw(img)

    # Добавление текста
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    # Рисование текста по центру
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((800 - text_width) // 2, (600 - text_height) // 2)
    draw.text(position, text, fill='white', font=font)

    # Добавление рамки
    draw.rectangle([10, 10, 790, 590], outline='white', width=5)

    # Добавление паттерна для лучшего тестирования
    for i in range(0, 800, 50):
        draw.line([(i, 0), (i, 600)], fill=(255, 255, 255, 50), width=1)
    for i in range(0, 600, 50):
        draw.line([(0, i), (800, i)], fill=(255, 255, 255, 50), width=1)

    img.save(filename)
    print(f"Создано: {filename}")

# Создание тестовой папки
os.makedirs('test_images', exist_ok=True)

# Создание тестовых изображений
create_test_image('test_images/test_red.png', (220, 20, 60), 'TEST IMAGE 1')
create_test_image('test_images/test_blue.png', (30, 144, 255), 'TEST IMAGE 2')
create_test_image('test_images/test_green.png', (50, 205, 50), 'TEST IMAGE 3')

print("\nТестовые изображения созданы в папке 'test_images/'")
