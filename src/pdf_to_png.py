# -*- coding: utf-8 -*-
"""pdf to png.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15SQoIKGvsTJTfH_oFBg-7C2wzUJcNmLu
"""

import os

# Пути к папкам
folder_path = '/content/PDF'
output_folder = '/content/PNG'
output_folder2 = '/content/LLM2'

# Функция для создания папок, если они не существуют
def create_folders(*folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
        else:
            print(f"Folder already exists: {folder}")

# Создание папок
create_folders(folder_path, output_folder, output_folder2)

"""установка"""

# Часть 1: Установка и импорт
import os
import subprocess

def setup_environment():
    # Установка poppler-utils (если еще не установлено)
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y", "poppler-utils"], check=True)

# Вызов функции настройки окружения (нужно выполнить только один раз)
setup_environment()

import os
import subprocess
import zipfile

def process_pdfs(input_folder, output_folder):
    # Убедимся, что выходная папка существует
    os.makedirs(output_folder, exist_ok=True)

    # Получаем список PDF-файлов в папке
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    if not pdf_files:
        print("Нет PDF-файлов в папке:", input_folder)
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]  # Название файла без расширения

        # Создаем подкаталог для текущего PDF
        pdf_output_folder = os.path.join(output_folder, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)

        # Команда для преобразования PDF в PNG
        command = [
            "pdftoppm",
            "-png",  # Конвертировать в PNG
            pdf_path,
            os.path.join(pdf_output_folder, "page")  # Префикс имени файла
        ]

        # Выполнение команды
        subprocess.run(command, check=True)
        print(f"Обработан PDF: {pdf_file}, PNG сохранены в: {pdf_output_folder}")

        # Создание ZIP-архива без сжатия
        zip_path = os.path.join(output_folder, f"{pdf_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as zipf:
            for root, _, files in os.walk(pdf_output_folder):
                for file in files:
                    if file.endswith('.png'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, pdf_output_folder)
                        zipf.write(file_path, arcname)
        print(f"Создан ZIP-архив: {zip_path}")

    print("Готово!")

# Пример вызова функции обработки
# Укажите ваши папки
input_folder = '/content/PDF'
output_folder = '/content/PNG'
process_pdfs(input_folder, output_folder)

"""только архив"""

import os
import zipfile

def create_zip(input_folder, output_folder):
    # Убедимся, что выходная папка существует
    os.makedirs(output_folder, exist_ok=True)

    # Получаем список файлов в папке
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    if not files:
        print("Нет файлов в папке:", input_folder)
        return

    # Создание ZIP-архива
    zip_path = os.path.join(output_folder, "archive.zip")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as zipf:
        for file in files:
            file_path = os.path.join(input_folder, file)
            zipf.write(file_path, os.path.basename(file))

    print(f"Создан ZIP-архив: {zip_path}")

# Пример вызова функции создания архива
# Укажите ваши папки
input_folder = '/content/PNG/percyliang'  # Папка с файлами для архивации
output_folder = '/content/PNG1'  # Папка для сохранения архива
create_zip(input_folder, output_folder)

"""несколь файлов"""

import os
import subprocess
import zipfile
from concurrent.futures import ProcessPoolExecutor

def convert_pdf_to_png(pdf_path, pdf_output_folder):
    """
    Конвертация PDF в PNG с помощью pdftoppm.
    """
    command = [
        "pdftoppm",
        "-png",  # Конвертировать в PNG
        "-r", "300",  # Установка DPI на 300
        pdf_path,
        os.path.join(pdf_output_folder, "page")  # Префикс имени файла
    ]
    subprocess.run(command, check=True)
    print(f"Обработан PDF: {os.path.basename(pdf_path)}")

def create_zip(output_folder, pdf_name):
    """
    Создание ZIP-архива для изображений, полученных из PDF.
    """
    pdf_output_folder = os.path.join(output_folder, pdf_name)
    zip_path = os.path.join(output_folder, f"{pdf_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(pdf_output_folder):
            for file in files:
                if file.endswith('.png'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, pdf_output_folder)
                    zipf.write(file_path, arcname)
    print(f"Создан ZIP-архив: {zip_path}")

def process_single_pdf(pdf_file, input_folder, output_folder):
    """
    Обработка одного PDF-файла: конвертация и подготовка к архивации.
    """
    pdf_path = os.path.join(input_folder, pdf_file)
    pdf_name = os.path.splitext(pdf_file)[0]
    pdf_output_folder = os.path.join(output_folder, pdf_name)
    os.makedirs(pdf_output_folder, exist_ok=True)

    # Конвертация PDF в PNG
    convert_pdf_to_png(pdf_path, pdf_output_folder)
    return pdf_name  # Возвращаем имя файла для архивации

def process_pdfs(input_folder, output_folder):
    """
    Основной процесс обработки всех PDF-файлов.
    """
    os.makedirs(output_folder, exist_ok=True)
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    if not pdf_files:
        print("Нет PDF-файлов в папке:", input_folder)
        return

    # Многопроцессорная обработка PDF-файлов
    with ProcessPoolExecutor() as executor:
        pdf_names = list(executor.map(
            process_single_pdf, pdf_files,
            [input_folder] * len(pdf_files),
            [output_folder] * len(pdf_files)
        ))

    # Создание ZIP-архивов после обработки всех PDF
    for pdf_name in pdf_names:
        create_zip(output_folder, pdf_name)

    print("Готово!")

# Пример вызова функции обработки
input_folder = '/content/PDF'
output_folder = '/content/PNG'
process_pdfs(input_folder, output_folder)
