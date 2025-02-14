import requests

# URL вашего FastAPI сервера
url = "http://localhost:10000/process-pdf/"

# Пример данных для теста
data = {
    "url": "https://api.slingacademy.com/v1/sample-data/files/text-and-table.pdf",  # Здесь используйте URL вашего PDF файла
    "pages": "1-2"  # Пример страниц для конвертации
}

# Отправляем POST-запрос
response = requests.post(url, json=data)

# Проверяем статус код ответа
if response.status_code == 200:
    print("Конвертация прошла успешно!")
    # Можно вывести URL для скачивания PNG или другой ответ, если требуется
    print("Ответ от сервера:", response.json())
else:
    print(f"Ошибка: {response.status_code}")
    print("Ответ от сервера:", response.text)
