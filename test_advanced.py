#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой логики уникализации
"""

from PIL import Image
from pathlib import Path
import sys

# Импорт из основного файла
sys.path.insert(0, str(Path(__file__).parent))

# Импортируем функцию обработки
from app import process_folder

def test_processing():
    """Тестирование обработки папки"""

    print("=" * 60)
    print("  Тестирование Image Uniqueizer Pro 2.0")
    print("=" * 60)
    print()

    # Проверка существования тестовых изображений
    test_folder = Path("test_images")

    if not test_folder.exists():
        print("❌ Папка test_images не найдена!")
        print("Запустите сначала: python3 create_test_images.py")
        return

    # Настройки для тестирования
    settings = {
        'intensity': 5,
        'adjust_contrast': True,
        'adjust_brightness': True,
        'adjust_saturation': True,
        'adjust_sharpness': True,
        'add_noise': True,
        'add_blur': True,
        'micro_rotate': True,
        'micro_resize': True,
        'micro_crop': True,
        'modify_exif': True,
        'jpeg_quality': 93,
        'output_format': 'jpg',
    }

    num_copies = 3

    print(f"📁 Исходная папка: {test_folder.name}")
    print(f"🔢 Количество копий: {num_copies}")
    print(f"⚙️  Интенсивность: {settings['intensity']}")
    print()

    # Прогресс callback
    def progress_callback(current, total):
        percent = int((current / total) * 100)
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f'\r[{bar}] {percent}% ({current}/{total})', end='', flush=True)

    # Обработка
    print("Обработка...")
    result = process_folder(str(test_folder), num_copies, settings, progress_callback)

    print()
    print()

    if result['success']:
        print("✅ Обработка завершена успешно!")
        print()
        print(f"📊 Результаты:")
        print(f"   • Создано папок: {len(result['created_folders'])}")
        print(f"   • Фото в каждой: {result['images_per_folder']}")
        print(f"   • Всего изображений: {result['total_images']}")
        print()
        print(f"📁 Созданные папки:")

        for folder in result['created_folders']:
            files = sorted(folder.glob("*.jpg"))
            print(f"   • {folder.name}/ ({len(files)} файлов)")
            for f in files[:3]:  # Показываем первые 3 файла
                size_kb = f.stat().st_size / 1024
                print(f"      - {f.name} ({size_kb:.1f} KB)")
            if len(files) > 3:
                print(f"      - ... и еще {len(files) - 3} файлов")

        print()
        print("=" * 60)
        print("✨ Проверьте созданные папки!")
        print(f"   Путь: {result['created_folders'][0].parent.absolute()}")
        print("=" * 60)

    else:
        print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")


if __name__ == "__main__":
    test_processing()
