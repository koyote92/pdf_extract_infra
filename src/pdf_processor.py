import logging
import os
import subprocess
import requests


logger = logging.getLogger("uvicorn.error")  # Используем логгер FastAPI (uvicorn.error)
logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования


def download_pdf(url, output_path):
    """Скачивание PDF по ссылке"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return output_path
    raise ValueError("Ошибка скачивания PDF")


def get_pdf_page_count(input_pdf):
    """Возвращает количество страниц в PDF с помощью pdfinfo"""
    command = ["pdfinfo", input_pdf]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    
    # Ищем строку с количеством страниц и извлекаем число
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    
    raise ValueError("Не удалось извлечь количество страниц из PDF")


def parse_pages(pages_str, max_pages):
    """Парсинг строки с номерами страниц и диапазонами"""
    pages = []
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            try:
                start, end = int(start), int(end)
                if start > max_pages or end > max_pages:
                    raise ValueError(f"Диапазон выходит за пределы допустимого количества страниц ({max_pages})")
                if start > end:
                    raise ValueError(f"Некорректный диапазон: начало больше конца ({part})")
                pages.extend(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Некорректный диапазон: {part}")
        else:
            try:
                page = int(part)
                if page > max_pages:
                    raise ValueError(f"Номер страницы {page} выходит за пределы допустимого количества страниц ({max_pages})")
                pages.append(page)
            except ValueError:
                raise ValueError(f"Некорректный номер страницы: {part}")
    
    # Убираем дубликаты и сортируем
    return sorted(set(pages))  


def extract_pages_as_png(input_pdf, output_folder, pages=None):
    """Конвертирует страницы PDF в PNG (все страницы или указанные)"""
    os.makedirs(output_folder, exist_ok=True)

    # Получаем количество страниц в PDF
    max_pages = get_pdf_page_count(input_pdf)

    # Если страницы не указаны, конвертируем весь PDF
    if pages is None:
        command = [
            "pdftoppm",
            "-png",  # Вывод в формат PNG
            input_pdf,
            os.path.join(output_folder, "page")  # Префикс для имен файлов
        ]
        subprocess.run(command, check=True)
    else:
        for page in pages:
            # Формируем команду для конвертации указанной страницы
            command = [
                "pdftoppm",
                "-png",  # Вывод в формат PNG
                "-f", str(page),  # Страница
                "-l", str(page),  # Страница
                input_pdf,
                os.path.join(output_folder, f"page")  # Префикс для имен файлов
            ]
            subprocess.run(command, check=True)
    
    return output_folder
