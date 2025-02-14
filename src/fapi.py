import os
import zipfile

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pdf_processor import download_pdf, extract_pages_as_png, get_pdf_page_count, parse_pages

app = FastAPI()

# Папки для хранения PDF и PNG
PDF_FOLDER = "/app/pdfs"
PNG_FOLDER = "/app/pngs"
PNG_PATH_PREFIX = "pngs"

# Настроим FastAPI на отдачу статических файлов из папки с изображениями
app.mount("/static", StaticFiles(directory=PNG_FOLDER, html=True), name="static")

def validate_pdf_url(url: str) -> bool:
    """Проверка, заканчивается ли URL на .pdf"""
    return url.lower().endswith('.pdf')

@app.post("/process-pdf/")
async def process_pdf(request: Request):
    data = await request.json()
    url = data.get("url")
    pages = data.get("pages")

    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    # Проверка, что URL заканчивается на .pdf
    if not validate_pdf_url(url):
        raise HTTPException(status_code=400, detail="URL must end with .pdf")

    try:
        # Скачивание PDF
        pdf_name = os.path.basename(url)
        pdf_path = os.path.join(PDF_FOLDER, pdf_name)
        download_pdf(url, pdf_path)

        # Если pages не указаны, конвертируем весь файл
        if pages is None:
            pages = None
        else:
            # Парсим и проверяем формат pages
            max_pages = get_pdf_page_count(pdf_path)
            try:
                pages = parse_pages(pages, max_pages)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid pages format: {str(e)}")

        # Создаем папку для изображений
        folder_name = os.path.splitext(pdf_name)[0]
        output_folder = os.path.join(PNG_FOLDER, folder_name)

        # Извлечение страниц (или весь файл, если страницы не указаны)
        os.makedirs(output_folder, exist_ok=True)
        extract_pages_as_png(pdf_path, output_folder, pages)

        # Возвращаем ссылку на папку
        return {"status": "success", "message": "PDF processed", "folder_url": f"/static/{folder_name}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/{PNG_PATH_PREFIX}/{folder_name}/")
async def list_files(folder_name: str):
    """
    Возвращает HTML-страницу с списком файлов в указанной папке и ссылку для скачивания архива.
    """
    folder_path = os.path.join(PNG_FOLDER, folder_name)
    
    # Проверяем, существует ли папка
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Получаем список файлов в папке
    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]  # Только файлы
    
    # Генерируем HTML-страницу
    html_content = f"<h1>{folder_name}</h1><ul>"
    for file in sorted(files):
        file_url = f"/{PNG_PATH_PREFIX}/{folder_name}/{file}"
        html_content += f'<li><a href="{file_url}">{file}</a></li>'
    
    # Ссылка для скачивания архива
    zip_url = f"/{PNG_PATH_PREFIX}/{folder_name}/download/"
    html_content += f'<br><a href="{zip_url}">Download all as ZIP</a>'
    html_content += "</ul>"
    
    return HTMLResponse(content=html_content)


@app.get("/{PNG_PATH_PREFIX}/{folder_name}/download/")
async def download_folder_as_zip(folder_name: str):
    """
    Скачивает все файлы из папки как ZIP-архив без сжатия.
    """
    folder_path = os.path.join(PNG_FOLDER, folder_name)
    
    # Проверяем, существует ли папка
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Создаем ZIP-архив без сжатия
    zip_filename = f"{folder_name}.zip"
    zip_filepath = os.path.join(PNG_FOLDER, zip_filename)
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_STORED) as zipf:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=file)  # arcname сохраняет только имя файла без пути
    
    # Возвращаем ZIP-архив
    return FileResponse(zip_filepath, media_type='application/zip', filename=zip_filename)


@app.get("/{PNG_PATH_PREFIX}/{folder_name}/{filename}")
async def get_png(folder_name: str, filename: str):
    """
    Возвращает PNG файл по имени из указанной папки.
    """
    file_path = os.path.join(PNG_FOLDER, folder_name, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")
