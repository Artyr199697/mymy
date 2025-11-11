#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Uniqueizer Pro - Web Interface
Профессиональная уникализация изображений для Avito
"""

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import os
from pathlib import Path
import colorsys
import random
import time
from datetime import datetime
import piexif
import io

# Конфигурация страницы
st.set_page_config(
    page_title="Image Uniqueizer Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Дизайнерские цветовые схемы (гармоничные, незаметные изменения)
PROFESSIONAL_COLOR_SCHEMES = [
    {"name": "Натуральный", "hue": 0, "sat": 0, "val": 0},
    {"name": "Теплый свет", "hue": 5, "sat": -3, "val": 2},
    {"name": "Холодный свет", "hue": -5, "sat": -2, "val": -1},
    {"name": "Золотой час", "hue": 8, "sat": 5, "val": 3},
    {"name": "Утренний", "hue": 3, "sat": -5, "val": 2},
    {"name": "Вечерний", "hue": -3, "sat": 3, "val": -2},
    {"name": "Нейтральный+", "hue": 2, "sat": 0, "val": 1},
    {"name": "Мягкий", "hue": -2, "sat": -4, "val": 1},
    {"name": "Насыщенный", "hue": 4, "sat": 6, "val": 0},
    {"name": "Приглушенный", "hue": -4, "sat": -6, "val": -1},
]


class AdvancedImageUniqueizer:
    """Продвинутый класс для уникализации изображений"""

    def __init__(self, settings):
        self.settings = settings

    def shift_hsv(self, img, hue_shift, sat_shift, val_shift):
        """Тонкий сдвиг в HSV пространстве"""
        try:
            # Конвертация в HSV через numpy (быстрее)
            img_hsv = img.convert('HSV')
            h, s, v = img_hsv.split()

            # Применение сдвигов
            h_array = np.array(h, dtype=np.float32)
            s_array = np.array(s, dtype=np.float32)
            v_array = np.array(v, dtype=np.float32)

            # Hue shift (0-255 шкала)
            h_array = (h_array + hue_shift * 255 / 360) % 255

            # Saturation shift
            s_array = np.clip(s_array * (1 + sat_shift / 100), 0, 255)

            # Value shift
            v_array = np.clip(v_array * (1 + val_shift / 100), 0, 255)

            # Обратно в изображение
            h = Image.fromarray(h_array.astype(np.uint8), mode='L')
            s = Image.fromarray(s_array.astype(np.uint8), mode='L')
            v = Image.fromarray(v_array.astype(np.uint8), mode='L')

            result = Image.merge('HSV', (h, s, v))
            return result.convert('RGB')
        except:
            return img

    def add_micro_noise(self, img, intensity):
        """Добавление микро-шума (незаметного)"""
        img_array = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, intensity, img_array.shape)
        noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)

    def micro_rotate(self, img, max_angle=0.5):
        """Микро-поворот на доли градуса"""
        angle = random.uniform(-max_angle, max_angle)
        return img.rotate(angle, resample=Image.BICUBIC, expand=False)

    def micro_resize(self, img, max_percent=1):
        """Микро-изменение размера"""
        width, height = img.size
        scale = random.uniform(1 - max_percent/100, 1 + max_percent/100)
        new_size = (int(width * scale), int(height * scale))
        resized = img.resize(new_size, Image.LANCZOS)

        # Вернуть к исходному размеру
        return resized.resize((width, height), Image.LANCZOS)

    def micro_crop(self, img, max_pixels=3):
        """Микро-кроп с границ"""
        width, height = img.size
        crop_pixels = random.randint(0, max_pixels)

        if crop_pixels > 0:
            img = img.crop((
                crop_pixels,
                crop_pixels,
                width - crop_pixels,
                height - crop_pixels
            ))
            # Вернуть к исходному размеру
            img = img.resize((width, height), Image.LANCZOS)

        return img

    def modify_exif(self, img):
        """Изменение EXIF данных"""
        try:
            # Создание новых EXIF данных
            exif_dict = {
                "0th": {},
                "Exif": {},
                "GPS": {},
                "1st": {},
                "thumbnail": None
            }

            # Случайные метаданные
            exif_dict["0th"][piexif.ImageIFD.Software] = f"Editor_{random.randint(1000, 9999)}".encode()
            exif_dict["0th"][piexif.ImageIFD.DateTime] = datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode()

            # Случайная ориентация (1 - нормальная)
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

            exif_bytes = piexif.dump(exif_dict)
            return exif_bytes
        except:
            return None

    def uniqueize(self, img, scheme_index, variant_number):
        """Применение полного цикла уникализации"""

        # 1. Цветовая схема
        scheme = PROFESSIONAL_COLOR_SCHEMES[scheme_index % len(PROFESSIONAL_COLOR_SCHEMES)]
        img = self.shift_hsv(
            img,
            scheme['hue'],
            scheme['sat'],
            scheme['val']
        )

        # 2. Случайные тонкие изменения
        intensity = self.settings['intensity']

        # Контраст
        if self.settings['adjust_contrast']:
            factor = random.uniform(
                1 - intensity * 0.03,
                1 + intensity * 0.03
            )
            img = ImageEnhance.Contrast(img).enhance(factor)

        # Яркость
        if self.settings['adjust_brightness']:
            factor = random.uniform(
                1 - intensity * 0.02,
                1 + intensity * 0.02
            )
            img = ImageEnhance.Brightness(img).enhance(factor)

        # Насыщенность
        if self.settings['adjust_saturation']:
            factor = random.uniform(
                1 - intensity * 0.04,
                1 + intensity * 0.04
            )
            img = ImageEnhance.Color(img).enhance(factor)

        # Резкость
        if self.settings['adjust_sharpness'] and random.random() < 0.3:
            factor = random.uniform(1, 1 + intensity * 0.05)
            img = ImageEnhance.Sharpness(img).enhance(factor)

        # 3. Микро-шум
        if self.settings['add_noise']:
            noise_level = intensity * 1.5
            img = self.add_micro_noise(img, noise_level)

        # 4. Микро-размытие
        if self.settings['add_blur'] and random.random() < 0.4:
            img = img.filter(ImageFilter.GaussianBlur(radius=intensity * 0.15))

        # 5. Микро-поворот
        if self.settings['micro_rotate']:
            img = self.micro_rotate(img, max_angle=intensity * 0.3)

        # 6. Микро-ресайз
        if self.settings['micro_resize']:
            img = self.micro_resize(img, max_percent=intensity * 0.5)

        # 7. Микро-кроп
        if self.settings['micro_crop']:
            img = self.micro_crop(img, max_pixels=int(intensity * 1.5))

        return img


def process_folder(source_folder, num_copies, settings, progress_callback=None):
    """
    Обработка папки с фото

    Args:
        source_folder: путь к папке с оригинальными фото
        num_copies: количество копий объявления
        settings: настройки уникализации
    """
    source_path = Path(source_folder)
    folder_name = source_path.name
    parent_folder = source_path.parent

    # Поиск всех изображений в папке
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    image_files = []

    for ext in image_extensions:
        image_files.extend(source_path.glob(f"*{ext}"))
        image_files.extend(source_path.glob(f"*{ext.upper()}"))

    image_files = sorted(image_files)

    if not image_files:
        return {"success": False, "error": "Изображения не найдены в папке"}

    total_operations = num_copies * len(image_files)
    current_operation = 0

    uniqueizer = AdvancedImageUniqueizer(settings)
    created_folders = []

    # Создание копий
    for copy_num in range(1, num_copies + 1):
        # Создание папки для копии
        output_folder = parent_folder / f"{folder_name}_{copy_num}"
        output_folder.mkdir(exist_ok=True)
        created_folders.append(output_folder)

        # Обработка каждого изображения
        for img_index, img_path in enumerate(image_files, 1):
            try:
                # Открытие изображения
                img = Image.open(img_path)

                # Конвертация в RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Уникализация
                unique_img = uniqueizer.uniqueize(img, copy_num - 1, img_index)

                # Определение расширения
                output_ext = settings.get('output_format', 'jpg')
                output_filename = f"{img_index}.{output_ext}"
                output_path = output_folder / output_filename

                # Сохранение с EXIF
                exif_bytes = uniqueizer.modify_exif(unique_img) if settings.get('modify_exif', True) else None

                save_params = {
                    'quality': settings.get('jpeg_quality', 93),
                    'optimize': True,
                }

                if output_ext.lower() in ['jpg', 'jpeg'] and exif_bytes:
                    save_params['exif'] = exif_bytes

                unique_img.save(output_path, format='JPEG', **save_params)

                current_operation += 1

                if progress_callback:
                    progress_callback(current_operation, total_operations)

            except Exception as e:
                st.error(f"Ошибка при обработке {img_path.name}: {e}")
                continue

    return {
        "success": True,
        "created_folders": created_folders,
        "total_images": current_operation,
        "images_per_folder": len(image_files)
    }


# Основной интерфейс
def main():
    st.title("🎨 Image Uniqueizer Pro для Avito")
    st.markdown("**Профессиональная уникализация изображений для объявлений**")

    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки уникализации")

        # Интенсивность изменений
        intensity = st.slider(
            "Интенсивность изменений",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = минимальные изменения, 10 = максимальные"
        )

        st.markdown("---")
        st.subheader("🎨 Что изменять:")

        adjust_contrast = st.checkbox("Контраст", value=True)
        adjust_brightness = st.checkbox("Яркость", value=True)
        adjust_saturation = st.checkbox("Насыщенность", value=True)
        adjust_sharpness = st.checkbox("Резкость", value=True)

        st.markdown("---")
        st.subheader("🔧 Продвинутые:")

        add_noise = st.checkbox("Микро-шум", value=True, help="Незаметный шум для уникальности")
        add_blur = st.checkbox("Микро-размытие", value=True)
        micro_rotate = st.checkbox("Микро-поворот", value=True, help="Поворот на доли градуса")
        micro_resize = st.checkbox("Микро-ресайз", value=True)
        micro_crop = st.checkbox("Микро-кроп", value=True)
        modify_exif = st.checkbox("Изменить EXIF", value=True, help="Метаданные файла")

        st.markdown("---")
        st.subheader("💾 Сохранение:")

        jpeg_quality = st.slider("Качество JPEG", 85, 98, 93)
        output_format = st.selectbox("Формат", ["jpg", "png"], index=0)

    # Основная область
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Выбор папки с фото")

        # Ввод пути к папке
        folder_path = st.text_input(
            "Путь к папке с изображениями",
            placeholder="Например: C:\\Users\\Name\\Desktop\\GPT PLUS",
            help="Введите полный путь к папке с фотографиями одного объявления"
        )

        # Или загрузка файлов
        st.markdown("**Или загрузите файлы:**")
        uploaded_files = st.file_uploader(
            "Выберите изображения",
            type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
            accept_multiple_files=True
        )

    with col2:
        st.subheader("🔢 Количество копий")
        num_copies = st.number_input(
            "Сколько объявлений создать?",
            min_value=1,
            max_value=20,
            value=3,
            help="Из одной папки будет создано N папок с уникальными фото"
        )

        st.info(f"""
        **Результат:**
        - Будет создано: **{num_copies} папок**
        - Каждая папка - готовое объявление
        - Фото пронумерованы: 1.jpg, 2.jpg и т.д.
        """)

    # Кнопка обработки
    st.markdown("---")

    if st.button("🚀 СОЗДАТЬ УНИКАЛЬНЫЕ ОБЪЯВЛЕНИЯ", type="primary", use_container_width=True):

        settings = {
            'intensity': intensity,
            'adjust_contrast': adjust_contrast,
            'adjust_brightness': adjust_brightness,
            'adjust_saturation': adjust_saturation,
            'adjust_sharpness': adjust_sharpness,
            'add_noise': add_noise,
            'add_blur': add_blur,
            'micro_rotate': micro_rotate,
            'micro_resize': micro_resize,
            'micro_crop': micro_crop,
            'modify_exif': modify_exif,
            'jpeg_quality': jpeg_quality,
            'output_format': output_format,
        }

        # Обработка загруженных файлов
        if uploaded_files:
            # Создание временной папки
            temp_folder = Path("temp_upload")
            temp_folder.mkdir(exist_ok=True)

            # Сохранение загруженных файлов
            for uploaded_file in uploaded_files:
                file_path = temp_folder / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            folder_path = str(temp_folder)

        if not folder_path or not Path(folder_path).exists():
            st.error("❌ Укажите корректный путь к папке или загрузите файлы")
            return

        # Прогресс-бар
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Обработано: {current} из {total} изображений ({int(progress*100)}%)")

        # Обработка
        with st.spinner("Создание уникальных объявлений..."):
            result = process_folder(folder_path, num_copies, settings, update_progress)

        if result['success']:
            st.success("✅ Готово!")

            st.balloons()

            # Результаты
            st.markdown("### 📊 Результаты:")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Создано папок", len(result['created_folders']))
            with col2:
                st.metric("Фото в каждой", result['images_per_folder'])
            with col3:
                st.metric("Всего изображений", result['total_images'])

            # Список созданных папок
            st.markdown("### 📁 Созданные папки:")
            for folder in result['created_folders']:
                st.code(str(folder.absolute()), language=None)

            st.info("""
            ✨ **Теперь вы можете:**
            1. Зайти в каждую папку
            2. Загрузить фото на Avito как отдельное объявление
            3. Все фото уникальные - Avito не будет ругаться!
            """)
        else:
            st.error(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")

    # Информация
    st.markdown("---")
    with st.expander("ℹ️ Как это работает?"):
        st.markdown("""
        ### Алгоритм уникализации:

        **Каждое изображение проходит через:**
        1. 🎨 Дизайнерскую цветовую коррекцию (10 гармоничных схем)
        2. 🔧 Микро-изменения контраста, яркости, насыщенности
        3. 📐 Микро-поворот на доли градуса
        4. 📏 Микро-изменение размера (незаметное)
        5. ✂️ Микро-кроп с границ
        6. 🎲 Добавление незаметного шума
        7. 📝 Изменение EXIF метаданных

        ### Результат:
        - ✅ Визуально изображения выглядят идентично
        - ✅ Технически - полностью уникальные файлы
        - ✅ Avito, Google, TinEye не находят дубликаты
        - ✅ Цвета гармоничные, подобраны дизайнером

        ### Пример работы:
        **У вас есть папка "GPT PLUS" с 6 фото**

        Вы выбираете: создать 3 объявления

        **Программа создаст:**
        - `GPT PLUS_1/` → 1.jpg, 2.jpg, 3.jpg, 4.jpg, 5.jpg, 6.jpg
        - `GPT PLUS_2/` → 1.jpg, 2.jpg, 3.jpg, 4.jpg, 5.jpg, 6.jpg
        - `GPT PLUS_3/` → 1.jpg, 2.jpg, 3.jpg, 4.jpg, 5.jpg, 6.jpg

        Каждая папка - готовое объявление с уникальными фото!
        """)

    with st.expander("🎨 Цветовые схемы"):
        st.markdown("### Профессиональные дизайнерские схемы:")
        for i, scheme in enumerate(PROFESSIONAL_COLOR_SCHEMES, 1):
            st.markdown(f"**{i}. {scheme['name']}** - "
                       f"Оттенок: {scheme['hue']:+d}°, "
                       f"Насыщенность: {scheme['sat']:+d}%, "
                       f"Яркость: {scheme['val']:+d}%")


if __name__ == "__main__":
    main()
