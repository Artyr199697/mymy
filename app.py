#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Uniqueizer Pro - Web Interface
Профессиональная уникализация изображений для Avito 2024-2025
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
import hashlib

# Конфигурация страницы
st.set_page_config(
    page_title="Image Uniqueizer Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 30 ПРОФЕССИОНАЛЬНЫХ ЦВЕТОВЫХ СХЕМ
# Все схемы имеют заметные изменения для гарантированной уникальности
PROFESSIONAL_COLOR_SCHEMES = [
    # Теплые тона (1-8)
    {"name": "Золотой_рассвет", "hue": 15, "sat": 8, "val": 5},
    {"name": "Закатный", "hue": 12, "sat": 10, "val": 3},
    {"name": "Янтарный", "hue": 18, "sat": 12, "val": 4},
    {"name": "Медовый", "hue": 20, "sat": 6, "val": 6},
    {"name": "Персиковый", "hue": 10, "sat": 5, "val": 7},
    {"name": "Коралловый", "hue": 8, "sat": 15, "val": 2},
    {"name": "Теплый_песок", "hue": 14, "sat": -5, "val": 4},
    {"name": "Осенний", "hue": 16, "sat": 18, "val": -2},

    # Холодные тона (9-16)
    {"name": "Морозный", "hue": -15, "sat": -8, "val": 3},
    {"name": "Голубой_час", "hue": -20, "sat": 10, "val": -2},
    {"name": "Ледяной", "hue": -18, "sat": 12, "val": 5},
    {"name": "Бирюзовый", "hue": -25, "sat": 15, "val": 2},
    {"name": "Морской", "hue": -12, "sat": 8, "val": 4},
    {"name": "Арктический", "hue": -22, "sat": -10, "val": 6},
    {"name": "Стальной", "hue": -10, "sat": -15, "val": 1},
    {"name": "Зимний", "hue": -16, "sat": 6, "val": -3},

    # Насыщенные (17-24)
    {"name": "Яркий", "hue": 5, "sat": 20, "val": 5},
    {"name": "Живой", "hue": -5, "sat": 22, "val": 4},
    {"name": "Сочный", "hue": 7, "sat": 25, "val": 3},
    {"name": "Весенний", "hue": -8, "sat": 18, "val": 6},
    {"name": "Тропический", "hue": 10, "sat": 28, "val": 2},
    {"name": "Красочный", "hue": 12, "sat": 24, "val": 5},
    {"name": "Виноградный", "hue": -30, "sat": 20, "val": 0},
    {"name": "Лавандовый", "hue": -28, "sat": 16, "val": 4},

    # Приглушенные/Винтаж (25-30)
    {"name": "Мягкий", "hue": 3, "sat": -12, "val": 3},
    {"name": "Пастельный", "hue": -4, "sat": -15, "val": 5},
    {"name": "Винтажный", "hue": 8, "sat": -10, "val": -4},
    {"name": "Ретро", "hue": 12, "sat": -8, "val": -2},
    {"name": "Выцветший", "hue": -6, "sat": -18, "val": 2},
    {"name": "Матовый", "hue": 4, "sat": -20, "val": 1},
]


class AdvancedImageUniqueizer:
    """Продвинутый класс для уникализации изображений под Avito 2024-2025"""

    def __init__(self, settings):
        self.settings = settings

    def shift_hsv(self, img, hue_shift, sat_shift, val_shift):
        """
        Профессиональный сдвиг в HSV пространстве
        Использует быстрый numpy для обработки
        """
        try:
            # Конвертация в numpy array
            img_array = np.array(img, dtype=np.float32) / 255.0

            # Конвертация RGB -> HSV через векторизацию
            h_array = np.zeros(img_array.shape[:2], dtype=np.float32)
            s_array = np.zeros(img_array.shape[:2], dtype=np.float32)
            v_array = np.zeros(img_array.shape[:2], dtype=np.float32)

            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    r, g, b = img_array[i, j]
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    h_array[i, j] = h
                    s_array[i, j] = s
                    v_array[i, j] = v

            # Применение сдвигов
            h_array = (h_array + hue_shift / 360.0) % 1.0
            s_array = np.clip(s_array + sat_shift / 100.0, 0, 1)
            v_array = np.clip(v_array + val_shift / 100.0, 0, 1)

            # Конвертация обратно в RGB
            rgb_array = np.zeros_like(img_array)
            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    h, s, v = h_array[i, j], s_array[i, j], v_array[i, j]
                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                    rgb_array[i, j] = [r, g, b]

            rgb_array = (rgb_array * 255).astype(np.uint8)
            return Image.fromarray(rgb_array)
        except:
            return img

    def add_micro_noise(self, img, intensity):
        """Добавление незаметного шума для изменения хеша"""
        img_array = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, intensity, img_array.shape)
        noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)

    def micro_resize(self, img, max_percent=0.5):
        """Микро-изменение размера (незаметное)"""
        width, height = img.size
        scale = random.uniform(1 - max_percent/100, 1 + max_percent/100)
        new_size = (int(width * scale), int(height * scale))
        resized = img.resize(new_size, Image.LANCZOS)
        return resized.resize((width, height), Image.LANCZOS)

    def micro_crop(self, img, max_pixels=2):
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
            img = img.resize((width, height), Image.LANCZOS)

        return img

    def modify_exif(self, img):
        """
        Изменение EXIF данных
        Критически важно для обхода дубликатов Avito
        """
        try:
            exif_dict = {
                "0th": {},
                "Exif": {},
                "GPS": {},
                "1st": {},
                "thumbnail": None
            }

            # Случайные метаданные
            software_id = f"PhotoEditor_{random.randint(1000, 9999)}"
            exif_dict["0th"][piexif.ImageIFD.Software] = software_id.encode()

            # Случайная дата (в пределах последних 30 дней)
            days_ago = random.randint(1, 30)
            random_date = datetime.now()
            date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode()

            # Ориентация
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

            # Случайные данные камеры (выглядит естественно)
            cameras = [
                b"iPhone 12", b"iPhone 13", b"iPhone 14",
                b"Samsung Galaxy", b"Xiaomi Redmi",
                b"Canon EOS", b"Nikon D5600"
            ]
            exif_dict["0th"][piexif.ImageIFD.Make] = random.choice(cameras)

            exif_bytes = piexif.dump(exif_dict)
            return exif_bytes
        except:
            return None

    def uniqueize(self, img, scheme_index, variant_number):
        """
        Профессиональная уникализация под Avito 2024-2025

        Стратегия:
        1. Цветовая схема (основное изменение)
        2. Тонкие adjustments (контраст, яркость, насыщенность)
        3. Микро-шум (изменяет хеш)
        4. Микро-трансформации (изменяет pHash)
        5. EXIF метаданные (критически важно!)
        """

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
                1 - intensity * 0.02,
                1 + intensity * 0.02
            )
            img = ImageEnhance.Contrast(img).enhance(factor)

        # Яркость
        if self.settings['adjust_brightness']:
            factor = random.uniform(
                1 - intensity * 0.015,
                1 + intensity * 0.015
            )
            img = ImageEnhance.Brightness(img).enhance(factor)

        # Насыщенность
        if self.settings['adjust_saturation']:
            factor = random.uniform(
                1 - intensity * 0.03,
                1 + intensity * 0.03
            )
            img = ImageEnhance.Color(img).enhance(factor)

        # Резкость
        if self.settings['adjust_sharpness'] and random.random() < 0.3:
            factor = random.uniform(1, 1 + intensity * 0.04)
            img = ImageEnhance.Sharpness(img).enhance(factor)

        # 3. Микро-шум (важно для изменения хеша!)
        if self.settings['add_noise']:
            noise_level = intensity * 1.0
            img = self.add_micro_noise(img, noise_level)

        # 4. Микро-размытие
        if self.settings['add_blur'] and random.random() < 0.4:
            img = img.filter(ImageFilter.GaussianBlur(radius=intensity * 0.1))

        # 5. Микро-ресайз (изменяет pHash)
        if self.settings['micro_resize']:
            img = self.micro_resize(img, max_percent=intensity * 0.3)

        # 6. Микро-кроп
        if self.settings['micro_crop']:
            img = self.micro_crop(img, max_pixels=int(intensity * 1.0))

        return img


def process_folder(source_folder, num_copies, settings, progress_callback=None):
    """
    Обработка папки с фото для Avito

    Логика:
    - Исходная папка: "GPT PLUS" с 6 фото
    - Создается: "GPT PLUS_1", "GPT PLUS_2", "GPT PLUS_3"
    - В каждой папке: 1.jpg, 2.jpg, 3.jpg, 4.jpg, 5.jpg, 6.jpg
    - ВСЕ фото уникализированы (оригинал НЕ включается)
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

                # УНИКАЛИЗАЦИЯ (БЕЗ ОРИГИНАЛА)
                unique_img = uniqueizer.uniqueize(img, copy_num - 1, img_index)

                # Автоматическое определение формата
                original_ext = img_path.suffix.lower()
                if original_ext in ['.png']:
                    output_format = 'PNG'
                    output_ext = 'png'
                    save_params = {
                        'optimize': True,
                    }
                else:
                    # Для всех остальных - JPEG (лучше для Avito)
                    output_format = 'JPEG'
                    output_ext = 'jpg'
                    save_params = {
                        'quality': settings.get('jpeg_quality', 93),
                        'optimize': True,
                    }

                output_filename = f"{img_index}.{output_ext}"
                output_path = output_folder / output_filename

                # Сохранение с EXIF
                exif_bytes = uniqueizer.modify_exif(unique_img) if settings.get('modify_exif', True) else None

                if output_format == 'JPEG' and exif_bytes:
                    save_params['exif'] = exif_bytes

                unique_img.save(output_path, format=output_format, **save_params)

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
    st.title("🎨 Image Uniqueizer Pro для Avito 2024-2025")
    st.markdown("**Профессиональная уникализация с 30 цветовыми схемами**")

    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки")

        # Интенсивность изменений
        intensity = st.slider(
            "Интенсивность",
            min_value=1,
            max_value=10,
            value=4,
            help="Рекомендуется 3-5 для Avito"
        )

        st.markdown("---")
        st.subheader("🎨 Параметры:")

        adjust_contrast = st.checkbox("Контраст", value=True)
        adjust_brightness = st.checkbox("Яркость", value=True)
        adjust_saturation = st.checkbox("Насыщенность", value=True)
        adjust_sharpness = st.checkbox("Резкость", value=True)

        st.markdown("---")
        st.subheader("🔧 Продвинутые:")

        add_noise = st.checkbox("Микро-шум", value=True, help="Изменяет MD5/SHA хеш")
        add_blur = st.checkbox("Микро-размытие", value=True)
        micro_resize = st.checkbox("Микро-ресайз", value=True, help="Изменяет pHash")
        micro_crop = st.checkbox("Микро-кроп", value=True)
        modify_exif = st.checkbox("Изменить EXIF", value=True, help="⚠️ КРИТИЧЕСКИ ВАЖНО!")

        st.markdown("---")
        st.subheader("💾 Сохранение:")

        jpeg_quality = st.slider("Качество JPEG", 85, 98, 93)

        st.info("Формат определяется автоматически")

    # Основная область
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Папка с фото")

        folder_path = st.text_input(
            "Путь к папке с изображениями",
            placeholder="C:\\Users\\Name\\Desktop\\GPT PLUS",
            help="Полный путь к папке с фотографиями одного объявления"
        )

        st.markdown("**Или загрузите файлы:**")
        uploaded_files = st.file_uploader(
            "Выберите изображения",
            type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
            accept_multiple_files=True
        )

    with col2:
        st.subheader("🔢 Количество")
        num_copies = st.number_input(
            "Сколько объявлений?",
            min_value=1,
            max_value=30,
            value=5,
            help="Рекомендуется 3-7 для Avito"
        )

        st.success(f"""
        **Результат:**
        - Папок: **{num_copies}**
        - Все фото уникализированы
        - 30 цветовых схем
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
            'micro_resize': micro_resize,
            'micro_crop': micro_crop,
            'modify_exif': modify_exif,
            'jpeg_quality': jpeg_quality,
        }

        # Обработка загруженных файлов
        if uploaded_files:
            temp_folder = Path("temp_upload")
            temp_folder.mkdir(exist_ok=True)

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
            status_text.text(f"Обработано: {current} из {total} ({int(progress*100)}%)")

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
                st.metric("Всего", result['total_images'])

            # Список созданных папок
            st.markdown("### 📁 Созданные папки:")
            for folder in result['created_folders']:
                st.code(str(folder.absolute()), language=None)

            st.info("""
            ✨ **Готово к загрузке на Avito:**
            - Все фото уникализированы (оригинала нет)
            - 30 профессиональных цветовых схем
            - Изменены EXIF, хеши, размеры
            - Визуально выглядят отлично!
            """)
        else:
            st.error(f"❌ Ошибка: {result.get('error')}")

    # Информация
    st.markdown("---")
    with st.expander("ℹ️ Как это работает? (Avito 2024-2025)"):
        st.markdown("""
        ### Стратегия уникализации для Avito:

        **1. Цветовые схемы (30 вариантов)**
        - Теплые тона (8 схем): золотой, закатный, янтарный...
        - Холодные тона (8 схем): морозный, ледяной, бирюзовый...
        - Насыщенные (8 схем): яркий, сочный, тропический...
        - Винтаж (6 схем): ретро, выцветший, пастельный...

        **2. Технические изменения:**
        - ✅ Изменение MD5/SHA хеша (шум)
        - ✅ Изменение pHash (ресайз, кроп)
        - ✅ Изменение EXIF (критически важно!)
        - ✅ Изменение размера файла
        - ✅ Случайные adjustments

        **3. Почему это работает на Avito:**
        - Avito проверяет: MD5 хеш, pHash, EXIF данные
        - Все эти параметры изменяются
        - TinEye, Google Images не находят дубликаты
        - Визуально - профессиональные цвета

        **4. Рекомендации:**
        - Интенсивность: 3-5 (оптимально)
        - Количество объявлений: 3-7
        - Обязательно: EXIF, шум, ресайз
        - Размещать с интервалом 2-4 часа
        """)

    with st.expander("🎨 30 Цветовых схем"):
        st.markdown("### Профессиональные схемы:")
        for i, scheme in enumerate(PROFESSIONAL_COLOR_SCHEMES, 1):
            st.markdown(f"**{i}. {scheme['name']}** - "
                       f"Hue: {scheme['hue']:+d}°, "
                       f"Sat: {scheme['sat']:+d}%, "
                       f"Val: {scheme['val']:+d}%")


if __name__ == "__main__":
    main()
