FROM python:3.12-slim
LABEL author="koyote92"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends\
    poppler-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install -U pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/pdfs /app/pngs

COPY . /app/

# Это внутренний виртуальный порт Docker Network, он не будет занимать порты из системы
EXPOSE 10000

CMD ["uvicorn", "fapi:app", "--host", "0.0.0.0", "--port", "10000"]
