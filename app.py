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

# Конфигурация страницы
st.set_page_config(
    page_title="Image Uniqueizer Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 30 ПРОФЕССИОНАЛЬНЫХ ЦВЕТОВЫХ СХЕМ
# Все схемы имеют РЕАЛЬНЫЕ заметные изменения цветов
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

    def shift_hsv_fast(self, img, hue_shift, sat_shift, val_shift):
        """
        БЫСТРЫЙ И РАБОЧИЙ сдвиг в HSV пространстве
        Использует правильный алгоритм изменения цветов
        """
        # Конвертация в numpy array
        img_array = np.array(img, dtype=np.float32) / 255.0

        # Покомпонентная конвертация RGB -> HSV
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]

        maxc = np.maximum(np.maximum(r, g), b)
        minc = np.minimum(np.minimum(r, g), b)
        v = maxc

        deltac = maxc - minc
        s = deltac / (maxc + 1e-10)

        # Вычисление Hue
        deltac = np.where(deltac == 0, 1, deltac)
        rc = (maxc - r) / deltac
        gc = (maxc - g) / deltac
        bc = (maxc - b) / deltac

        h = np.zeros_like(v)
        h = np.where((r == maxc), bc - gc, h)
        h = np.where((g == maxc), 2.0 + rc - bc, h)
        h = np.where((b == maxc), 4.0 + gc - rc, h)
        h = (h / 6.0) % 1.0

        # Применение сдвигов
        h = (h + hue_shift / 360.0) % 1.0
        s = np.clip(s + sat_shift / 100.0, 0, 1)
        v = np.clip(v + val_shift / 100.0, 0, 1)

        # Конвертация HSV -> RGB
        i = (h * 6.0).astype(int)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6

        # Собираем RGB обратно
        conditions = [
            (i == 0),
            (i == 1),
            (i == 2),
            (i == 3),
            (i == 4),
            (i == 5)
        ]

        r = np.select(conditions, [v, q, p, p, t, v])
        g = np.select(conditions, [t, v, v, q, p, p])
        b = np.select(conditions, [p, p, t, v, v, q])

        rgb_array = np.stack([r, g, b], axis=2)
        rgb_array = (np.clip(rgb_array, 0, 1) * 255).astype(np.uint8)

        return Image.fromarray(rgb_array)

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

            # Случайная дата
            random_date = datetime.now()
            date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode()

            # Ориентация
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

            # Случайные данные камеры
            cameras = [
                b"iPhone 12", b"iPhone 13", b"iPhone 14", b"iPhone 15",
                b"Samsung Galaxy S21", b"Samsung Galaxy S22",
                b"Xiaomi Redmi Note 10", b"Xiaomi Redmi Note 11",
                b"Canon EOS 2000D", b"Nikon D5600", b"Sony Alpha 6000"
            ]
            exif_dict["0th"][piexif.ImageIFD.Make] = random.choice(cameras)

            exif_bytes = piexif.dump(exif_dict)
            return exif_bytes
        except:
            return None

    def uniqueize(self, img, scheme_index, variant_number):
        """
        ПРОФЕССИОНАЛЬНАЯ УНИКАЛИЗАЦИЯ

        Каждое изображение проходит:
        1. Цветовую схему (ГЛАВНОЕ - меняет цвета реально!)
        2. Микро-adjustments
        3. Шум (меняет MD5 хеш)
        4. Ресайз/кроп (меняет pHash)
        5. EXIF (критично для Avito)
        """

        # 1. ЦВЕТОВАЯ СХЕМА (ГЛАВНОЕ!)
        scheme = PROFESSIONAL_COLOR_SCHEMES[scheme_index % len(PROFESSIONAL_COLOR_SCHEMES)]
        img = self.shift_hsv_fast(
            img,
            scheme['hue'],
            scheme['sat'],
            scheme['val']
        )

        # 2. Случайные тонкие изменения
        intensity = self.settings['intensity']

        # Контраст
        if self.settings['adjust_contrast']:
            factor = random.uniform(0.98, 1.02)
            img = ImageEnhance.Contrast(img).enhance(factor)

        # Яркость
        if self.settings['adjust_brightness']:
            factor = random.uniform(0.99, 1.01)
            img = ImageEnhance.Brightness(img).enhance(factor)

        # Насыщенность
        if self.settings['adjust_saturation']:
            factor = random.uniform(0.97, 1.03)
            img = ImageEnhance.Color(img).enhance(factor)

        # Резкость
        if self.settings['adjust_sharpness'] and random.random() < 0.3:
            factor = random.uniform(1.0, 1.04)
            img = ImageEnhance.Sharpness(img).enhance(factor)

        # 3. Микро-шум (важно для MD5!)
        if self.settings['add_noise']:
            noise_level = intensity * 0.8
            img = self.add_micro_noise(img, noise_level)

        # 4. Микро-размытие
        if self.settings['add_blur'] and random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(radius=0.1))

        # 5. Микро-ресайз (важно для pHash!)
        if self.settings['micro_resize']:
            img = self.micro_resize(img, max_percent=0.5)

        # 6. Микро-кроп
        if self.settings['micro_crop']:
            img = self.micro_crop(img, max_pixels=2)

        return img


def process_folder(source_folder, num_copies, settings, progress_callback=None):
    """
    Обработка папки с фото для Avito

    ЛОГИКА:
    - Исходная папка: "GPT PLUS" с 10 фото
    - Создается: "GPT PLUS_1", "GPT PLUS_2", ... "GPT PLUS_N"
    - В КАЖДОЙ папке: 10 УНИКАЛИЗИРОВАННЫХ фото (1.jpg, 2.jpg... 10.jpg)
    - Цвета РЕАЛЬНО изменены по цветовым схемам!
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

                # УНИКАЛИЗАЦИЯ (ЦВЕТА МЕНЯЮТСЯ!)
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
    st.markdown("**30 цветовых схем • Реальное изменение цветов • Без оригинала**")

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

        st.info("📌 Формат определяется автоматически")

    # Основная область
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Папка с фото")

        folder_path = st.text_input(
            "Путь к папке",
            placeholder="C:\\Users\\Name\\Desktop\\GPT PLUS",
            help="Если в папке 10 фото → в каждой выходной папке будет 10 уникализированных фото"
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
            "Объявлений?",
            min_value=1,
            max_value=30,
            value=5,
            help="Рекомендуется 3-7"
        )

        st.success(f"""
        **Результат:**
        - Папок: **{num_copies}**
        - Все фото с новыми цветами
        - 30 схем на выбор
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
            st.error("❌ Укажите путь к папке или загрузите файлы")
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
                st.metric("Папок", len(result['created_folders']))
            with col2:
                st.metric("Фото в каждой", result['images_per_folder'])
            with col3:
                st.metric("Всего", result['total_images'])

            # Список созданных папок
            st.markdown("### 📁 Созданные папки:")
            for folder in result['created_folders']:
                st.code(str(folder.absolute()), language=None)

            st.info(f"""
            ✨ **Готово к загрузке на Avito:**
            - В каждой папке: **{result['images_per_folder']} фото**
            - Все с ИЗМЕНЕННЫМИ цветами
            - EXIF, хеши - разные
            - Визуально выглядят профессионально!
            """)
        else:
            st.error(f"❌ Ошибка: {result.get('error')}")

    # Информация
    st.markdown("---")
    with st.expander("ℹ️ Как это работает?"):
        st.markdown("""
        ### Стратегия для Avito 2024-2025:

        **1. Цветовые схемы (30 вариантов)**
        Каждая схема РЕАЛЬНО меняет цвета в HSV пространстве:
        - Теплые (8): золотой, закатный, янтарный...
        - Холодные (8): морозный, ледяной, бирюзовый...
        - Насыщенные (8): яркий, сочный, тропический...
        - Винтаж (6): ретро, выцветший, пастельный...

        **2. Технические изменения:**
        - ✅ MD5/SHA хеш (шум)
        - ✅ pHash (ресайз, кроп)
        - ✅ EXIF данные (критично!)
        - ✅ Размер файла

        **3. Пример работы:**
        ```
        Исходная папка: "GPT PLUS" (10 фото)

        Результат (5 объявлений):
        GPT PLUS_1/ → 10 фото с "Золотой рассвет"
        GPT PLUS_2/ → 10 фото с "Закатный"
        GPT PLUS_3/ → 10 фото с "Янтарный"
        GPT PLUS_4/ → 10 фото с "Медовый"
        GPT PLUS_5/ → 10 фото с "Персиковый"
        ```

        **4. Рекомендации:**
        - Интенсивность: 3-5
        - Объявлений: 3-7
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
