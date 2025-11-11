#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Uniqueizer Pro
Профессиональная программа для создания уникальных вариантов изображений
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
import random
from pathlib import Path
import colorsys
import threading
from datetime import datetime


class ImageUniqueizerApp:
    """Главное приложение для уникализации изображений"""

    # Цветовые схемы (название: сдвиг Hue в градусах)
    # ИСПРАВЛЕНО: Увеличены сдвиги для ЗАМЕТНОГО изменения цветов!
    COLOR_SCHEMES = [
        ("Золотистый", 60),      # Красный → Желтый
        ("Холодный", -90),       # Красный → Циановый
        ("Теплый", 90),          # Синий → Желтый
        ("Морской", -60),        # Желтый → Синий
        ("Виноградный", 120),    # Красный → Фиолетовый
        ("Лимонный", -120),      # Фиолетовый → Желтый
        ("Розовый", 30),         # Небольшой сдвиг
        ("Бирюзовый", -30),      # Небольшой сдвиг
        ("Янтарный", 45),        # Средний сдвиг
        ("Лавандовый", -45)      # Средний сдвиг
    ]

    # Поддерживаемые форматы
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Image Uniqueizer Pro")
        self.root.geometry("600x550")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(False, False)

        # Переменные
        self.selected_files = []
        self.variant_count = tk.IntVar(value=5)
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """Создание интерфейса"""

        # Стили
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей для темной темы
        style.configure('Dark.TFrame', background='#2b2b2b')
        style.configure('Dark.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Arial', 10))
        style.configure('Title.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Arial', 16, 'bold'))
        style.configure('Dark.TButton', background='#3d3d3d', foreground='#ffffff', borderwidth=0, font=('Arial', 10))
        style.map('Dark.TButton', background=[('active', '#4d4d4d')])

        # Главный контейнер
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(main_frame, text="🎨 Image Uniqueizer Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Кнопки выбора файлов
        buttons_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(0, 15))

        select_files_btn = tk.Button(
            buttons_frame,
            text="📁 Выбрать изображения",
            command=self._select_files,
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        select_files_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)

        select_folder_btn = tk.Button(
            buttons_frame,
            text="📂 Выбрать папку",
            command=self._select_folder,
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        select_folder_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Список выбранных файлов
        files_label = ttk.Label(main_frame, text="Выбранные файлы:", style='Dark.TLabel')
        files_label.pack(anchor=tk.W, pady=(0, 5))

        # Рамка для списка файлов
        list_frame = tk.Frame(main_frame, bg='#1e1e1e', relief=tk.SUNKEN, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Scrollbar для списка
        scrollbar = tk.Scrollbar(list_frame, bg='#3d3d3d')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.files_listbox = tk.Listbox(
            list_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Arial', 9),
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.files_listbox.yview)

        # Кнопка удаления выбранных файлов
        remove_btn = tk.Button(
            main_frame,
            text="🗑️ Удалить выбранные",
            command=self._remove_selected,
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Arial', 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        remove_btn.pack(pady=(0, 15))

        # Настройки
        settings_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        variants_label = ttk.Label(settings_frame, text="Количество вариантов:", style='Dark.TLabel')
        variants_label.pack(side=tk.LEFT, padx=(0, 10))

        variants_spinbox = tk.Spinbox(
            settings_frame,
            from_=2,
            to=10,
            textvariable=self.variant_count,
            width=5,
            bg='#3d3d3d',
            fg='#ffffff',
            buttonbackground='#3d3d3d',
            font=('Arial', 10),
            relief=tk.FLAT
        )
        variants_spinbox.pack(side=tk.LEFT)

        # Кнопка обработки
        self.process_btn = tk.Button(
            main_frame,
            text="🚀 ОБРАБОТАТЬ",
            command=self._start_processing,
            bg='#4CAF50',
            fg='#ffffff',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.process_btn.pack(pady=(0, 15))

        # Статус
        self.status_label = ttk.Label(
            main_frame,
            text="Статус: Готов к работе",
            style='Dark.TLabel',
            font=('Arial', 9)
        )
        self.status_label.pack(pady=(0, 10))

        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=500
        )
        self.progress.pack(fill=tk.X)

    def _select_files(self):
        """Выбор файлов"""
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("Все файлы", "*.*")
            ]
        )

        if files:
            for file in files:
                if file not in self.selected_files:
                    ext = Path(file).suffix.lower()
                    if ext in self.SUPPORTED_FORMATS:
                        self.selected_files.append(file)
            self._update_files_list()

    def _select_folder(self):
        """Выбор папки"""
        folder = filedialog.askdirectory(title="Выберите папку с изображениями")

        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext in self.SUPPORTED_FORMATS:
                        full_path = os.path.join(root, file)
                        if full_path not in self.selected_files:
                            self.selected_files.append(full_path)
            self._update_files_list()

    def _remove_selected(self):
        """Удаление выбранных файлов из списка"""
        selected_indices = self.files_listbox.curselection()
        for index in reversed(selected_indices):
            del self.selected_files[index]
        self._update_files_list()

    def _update_files_list(self):
        """Обновление списка файлов"""
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, os.path.basename(file))

    def _update_status(self, message):
        """Обновление статуса"""
        self.status_label.config(text=f"Статус: {message}")
        self.root.update_idletasks()

    def _update_progress(self, current, total):
        """Обновление прогресс-бара"""
        progress_percent = (current / total) * 100
        self.progress['value'] = progress_percent
        self.root.update_idletasks()

    def _start_processing(self):
        """Запуск обработки в отдельном потоке"""
        if not self.selected_files:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите файлы для обработки")
            return

        if self.is_processing:
            return

        # Запуск в отдельном потоке
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED, bg='#808080')

        thread = threading.Thread(target=self._process_images)
        thread.daemon = True
        thread.start()

    def _process_images(self):
        """Обработка изображений"""
        try:
            variant_count = self.variant_count.get()
            total_operations = len(self.selected_files) * variant_count
            current_operation = 0

            # Создание выходной папки с временной меткой (НЕ перезаписываем!)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"uniqueized_images_{timestamp}")
            output_dir.mkdir(exist_ok=True)

            for file_path in self.selected_files:
                try:
                    file_name = Path(file_path).stem
                    self._update_status(f"Обработка: {os.path.basename(file_path)}")

                    # Открытие изображения
                    img = Image.open(file_path)

                    # Конвертация в RGB если необходимо
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Создание вариантов
                    for i in range(variant_count):
                        scheme_name, hue_shift = self.COLOR_SCHEMES[i % len(self.COLOR_SCHEMES)]

                        # Применение уникализации
                        unique_img = self._uniqueize_image(img.copy(), hue_shift)

                        # Сохранение
                        safe_scheme_name = scheme_name.replace(" ", "_")
                        output_path = output_dir / f"{file_name}_v{i+1}_{safe_scheme_name}.jpg"
                        unique_img.save(output_path, 'JPEG', quality=95, optimize=True)

                        current_operation += 1
                        self._update_progress(current_operation, total_operations)

                except Exception as e:
                    print(f"Ошибка при обработке {file_path}: {e}")
                    continue

            self._update_status(f"Готово! Обработано {len(self.selected_files)} изображений")
            self._update_progress(100, 100)

            messagebox.showinfo(
                "Успех",
                f"Обработано {len(self.selected_files)} изображений!\n"
                f"Создано {current_operation} вариантов\n"
                f"Папка: {output_dir.absolute()}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            self._update_status("Ошибка при обработке")

        finally:
            self.is_processing = False
            self.process_btn.config(state=tk.NORMAL, bg='#4CAF50')

    def _uniqueize_image(self, img, hue_shift):
        """Применение уникализации к изображению"""

        # 1. Сдвиг цветовой схемы (Hue shift) - ВСЕГДА применяется!
        img = self._shift_hue(img, hue_shift)

        # 2. Случайные изменения

        # Контраст (95-115%)
        contrast_factor = random.uniform(0.95, 1.15)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)

        # Яркость (97-108%)
        brightness_factor = random.uniform(0.97, 1.08)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)

        # Насыщенность (92-112%)
        saturation_factor = random.uniform(0.92, 1.12)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(saturation_factor)

        # Шум (0.5-1.5%, едва заметный)
        noise_level = random.uniform(0.005, 0.015)
        img = self._add_noise(img, noise_level)

        # Размытие (0.3px, 50% вероятность)
        if random.random() < 0.5:
            img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

        # Резкость (100-115%, 40% вероятность)
        if random.random() < 0.4:
            sharpness_factor = random.uniform(1.0, 1.15)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness_factor)

        return img

    def _shift_hue(self, img, degrees):
        """Сдвиг оттенка (Hue) в HSV"""
        # Конвертация в numpy array
        img_array = np.array(img, dtype=np.float32) / 255.0

        # Конвертация RGB -> HSV для каждого пикселя
        hsv_array = np.zeros_like(img_array)

        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                r, g, b = img_array[i, j]
                h, s, v = colorsys.rgb_to_hsv(r, g, b)

                # Сдвиг Hue
                h = (h + degrees / 360.0) % 1.0

                hsv_array[i, j] = [h, s, v]

        # Конвертация обратно в RGB
        rgb_array = np.zeros_like(img_array)

        for i in range(hsv_array.shape[0]):
            for j in range(hsv_array.shape[1]):
                h, s, v = hsv_array[i, j]
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                rgb_array[i, j] = [r, g, b]

        # Конвертация обратно в изображение
        rgb_array = (rgb_array * 255).astype(np.uint8)
        return Image.fromarray(rgb_array)

    def _add_noise(self, img, noise_level):
        """Добавление едва заметного шума"""
        img_array = np.array(img, dtype=np.float32)

        # Генерация Gaussian шума
        noise = np.random.normal(0, noise_level * 255, img_array.shape)

        # Добавление шума
        noisy_array = img_array + noise

        # Ограничение значений
        noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)

        return Image.fromarray(noisy_array)


def main():
    """Точка входа в программу"""
    root = tk.Tk()
    app = ImageUniqueizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
