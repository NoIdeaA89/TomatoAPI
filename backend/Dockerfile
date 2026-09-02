FROM python:3.12-slim

WORKDIR /app

# Instala dependencias primero para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

# Render (y la mayoría de PaaS) inyectan la variable PORT en runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
