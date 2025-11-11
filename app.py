#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Uniqueizer Pro - Web Interface
Профессиональная уникализация изображений для Avito 2024-2025
"""

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
from pathlib import Path
import colorsys
import random
from datetime import datetime
import piexif

# Конфигурация страницы
st.set_page_config(
    page_title="Image Uniqueizer Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 30 ПРОФЕССИОНАЛЬНЫХ ЦВЕТОВЫХ СХЕМ
# ИСПРАВЛЕНО: Увеличены сдвиги для ЗАМЕТНОГО изменения цветов!
COLOR_SCHEMES = [
    # Сильные сдвиги (ОЧЕНЬ ЗАМЕТНО) (1-10)
    {"name": "Золотистый", "hue": 60},      # Красный → Желтый
    {"name": "Холодный", "hue": -90},       # Красный → Циановый
    {"name": "Теплый", "hue": 90},          # Синий → Желтый
    {"name": "Морской", "hue": -60},        # Желтый → Синий
    {"name": "Виноградный", "hue": 120},    # Красный → Фиолетовый
    {"name": "Лимонный", "hue": -120},      # Фиолетовый → Желтый
    {"name": "Закатный", "hue": 75},        # Средне-сильный
    {"name": "Арктический", "hue": -75},    # Средне-сильный
    {"name": "Янтарный", "hue": 105},       # Сильный
    {"name": "Небесный", "hue": -105},      # Сильный

    # Средние сдвиги (ХОРОШО ЗАМЕТНО) (11-20)
    {"name": "Розовый", "hue": 45},
    {"name": "Бирюзовый", "hue": -45},
    {"name": "Персиковый", "hue": 50},
    {"name": "Голубой", "hue": -50},
    {"name": "Коралловый", "hue": 55},
    {"name": "Аквамариновый", "hue": -55},
    {"name": "Медовый", "hue": 65},
    {"name": "Ледяной", "hue": -65},
    {"name": "Рыжий", "hue": 70},
    {"name": "Зимний", "hue": -70},

    # Малые сдвиги (СЛАБО ЗАМЕТНО) (21-26)
    {"name": "Теплый_песок", "hue": 30},
    {"name": "Морозный", "hue": -30},
    {"name": "Осенний", "hue": 35},
    {"name": "Стальной", "hue": -35},
    {"name": "Карамельный", "hue": 40},
    {"name": "Лавандовый", "hue": -40},

    # Очень малые сдвиги (ЕДВА ЗАМЕТНО) (27-30)
    {"name": "Мягкий", "hue": 20},
    {"name": "Пастельный", "hue": -20},
    {"name": "Винтажный", "hue": 25},
    {"name": "Ретро", "hue": -25},
]


def shift_hue(img, degrees):
    """
    РАБОЧИЙ алгоритм сдвига оттенка (Hue) в HSV
    ИЗ ПЕРВОЙ ВЕРСИИ - ПРОВЕРЕННЫЙ!
    """
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


def modify_exif():
    """Создание случайных EXIF метаданных"""
    try:
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }

        software_id = f"PhotoEditor_{random.randint(1000, 9999)}"
        exif_dict["0th"][piexif.ImageIFD.Software] = software_id.encode()

        date_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode()
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

        cameras = [
            b"iPhone 12", b"iPhone 13", b"iPhone 14", b"iPhone 15",
            b"Samsung Galaxy S21", b"Samsung Galaxy S22",
            b"Xiaomi Redmi Note 10", b"Xiaomi Redmi Note 11",
            b"Canon EOS 2000D", b"Nikon D5600", b"Sony Alpha 6000"
        ]
        exif_dict["0th"][piexif.ImageIFD.Make] = random.choice(cameras)

        return piexif.dump(exif_dict)
    except:
        return None


def uniqueize_image(img, hue_shift):
    """
    ПОЛНАЯ УНИКАЛИЗАЦИЯ изображения
    Использует проверенный алгоритм из первой версии
    """
    # 1. ГЛАВНОЕ - Сдвиг цветовой схемы (ВСЕГДА применяется!)
    img = shift_hue(img, hue_shift)

    # 2. Случайные изменения
    contrast_factor = random.uniform(0.95, 1.15)
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)

    brightness_factor = random.uniform(0.97, 1.08)
    img = ImageEnhance.Brightness(img).enhance(brightness_factor)

    saturation_factor = random.uniform(0.92, 1.12)
    img = ImageEnhance.Color(img).enhance(saturation_factor)

    # 3. Шум (меняет MD5 хеш)
    noise_level = random.uniform(0.005, 0.015)
    img = add_noise(img, noise_level)

    # 4. Размытие (иногда)
    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

    # 5. Резкость (иногда)
    if random.random() < 0.4:
        sharpness_factor = random.uniform(1.0, 1.15)
        img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)

    return img


def process_folder(source_folder, num_copies, settings, progress_callback=None):
    """
    ПРАВИЛЬНАЯ ЛОГИКА:

    Исходная папка: "GPT PLUS" с 10 фото
    Количество объявлений: 5

    Результат:
    GPT PLUS_1/ → 10 уникализированных фото (схема "Золотой рассвет")
    GPT PLUS_2/ → 10 уникализированных фото (схема "Закатный")
    GPT PLUS_3/ → 10 уникализированных фото (схема "Янтарный")
    GPT PLUS_4/ → 10 уникализированных фото (схема "Медовый")
    GPT PLUS_5/ → 10 уникализированных фото (схема "Персиковый")

    В КАЖДОЙ папке столько же фото, сколько в исходной!
    """
    source_path = Path(source_folder)
    folder_name = source_path.name
    parent_folder = source_path.parent

    # Поиск всех изображений
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    image_files = []

    for ext in image_extensions:
        image_files.extend(source_path.glob(f"*{ext}"))
        image_files.extend(source_path.glob(f"*{ext.upper()}"))

    image_files = sorted(image_files)

    if not image_files:
        return {"success": False, "error": "Изображения не найдены в папке"}

    num_images = len(image_files)
    total_operations = num_copies * num_images
    current_operation = 0
    created_folders = []

    # Создание копий объявлений с временной меткой (НЕ перезаписываем!)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for copy_num in range(1, num_copies + 1):
        # Папка для объявления
        output_folder = parent_folder / f"{folder_name}_{timestamp}_{copy_num}"
        output_folder.mkdir(exist_ok=True)
        created_folders.append(output_folder)

        # Цветовая схема для ВСЕЙ папки
        scheme = COLOR_SCHEMES[(copy_num - 1) % len(COLOR_SCHEMES)]
        hue_shift = scheme['hue']

        # Обработка каждого фото
        for img_index, img_path in enumerate(image_files, 1):
            try:
                # Открытие
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # УНИКАЛИЗАЦИЯ (цвета меняются!)
                unique_img = uniqueize_image(img.copy(), hue_shift)

                # Определение формата
                original_ext = img_path.suffix.lower()
                if original_ext in ['.png']:
                    output_format = 'PNG'
                    output_ext = 'png'
                    save_params = {'optimize': True}
                else:
                    output_format = 'JPEG'
                    output_ext = 'jpg'
                    save_params = {
                        'quality': settings.get('jpeg_quality', 93),
                        'optimize': True
                    }

                # Сохранение
                output_filename = f"{img_index}.{output_ext}"
                output_path = output_folder / output_filename

                # EXIF
                if output_format == 'JPEG' and settings.get('modify_exif', True):
                    exif_bytes = modify_exif()
                    if exif_bytes:
                        save_params['exif'] = exif_bytes

                unique_img.save(output_path, format=output_format, **save_params)

                current_operation += 1
                if progress_callback:
                    progress_callback(current_operation, total_operations)

            except Exception as e:
                st.error(f"Ошибка: {img_path.name}: {e}")
                continue

    return {
        "success": True,
        "created_folders": created_folders,
        "total_images": current_operation,
        "images_per_folder": num_images
    }


def main():
    st.title("🎨 Image Uniqueizer Pro для Avito")
    st.markdown("**30 цветовых схем • Реальное изменение цветов**")

    with st.sidebar:
        st.header("⚙️ Настройки")

        jpeg_quality = st.slider("Качество JPEG", 85, 98, 93)
        modify_exif = st.checkbox("Изменить EXIF", value=True, help="Критически важно!")

        st.info("Цвета меняются автоматически по схемам")

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
        - В каждой столько же фото
        - Все с новыми цветами
        """)

    st.markdown("---")

    if st.button("🚀 СОЗДАТЬ УНИКАЛЬНЫЕ ОБЪЯВЛЕНИЯ", type="primary", use_container_width=True):

        settings = {
            'jpeg_quality': jpeg_quality,
            'modify_exif': modify_exif,
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

        # Прогресс
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

            st.markdown("### 📊 Результаты:")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Папок", len(result['created_folders']))
            with col2:
                st.metric("Фото в каждой", result['images_per_folder'])
            with col3:
                st.metric("Всего", result['total_images'])

            st.markdown("### 📁 Созданные папки:")
            for folder in result['created_folders']:
                st.code(str(folder.absolute()), language=None)

            st.info(f"""
            ✨ **Готово к загрузке на Avito:**
            - В каждой папке: **{result['images_per_folder']} фото**
            - Все с РАЗНЫМИ цветами
            - EXIF, хеши - уникальные
            """)
        else:
            st.error(f"❌ Ошибка: {result.get('error')}")

    st.markdown("---")
    with st.expander("ℹ️ Как это работает?"):
        st.markdown("""
        ### ПРАВИЛЬНАЯ логика:

        **Пример:**
        ```
        Исходная папка: "GPT PLUS" (10 фото)
        Количество объявлений: 5

        Результат:
        GPT PLUS_1/ → 10 фото (цвета: Золотой рассвет)
        GPT PLUS_2/ → 10 фото (цвета: Закатный)
        GPT PLUS_3/ → 10 фото (цвета: Янтарный)
        GPT PLUS_4/ → 10 фото (цвета: Медовый)
        GPT PLUS_5/ → 10 фото (цвета: Персиковый)
        ```

        **В каждой папке:**
        - Столько же фото, сколько в исходной
        - Все фото с одинаковой цветовой схемой
        - Но каждое фото уникализировано случайно

        **Уникализация:**
        - ✅ Изменение цветов (Hue shift)
        - ✅ Контраст, яркость, насыщенность
        - ✅ Шум (MD5 хеш)
        - ✅ EXIF метаданные
        """)

    with st.expander("🎨 30 Цветовых схем"):
        st.markdown("### Схемы:")
        for i, scheme in enumerate(COLOR_SCHEMES, 1):
            st.markdown(f"**{i}. {scheme['name']}** - Hue: {scheme['hue']:+d}°")


if __name__ == "__main__":
    main()
