# Dockerfile dla Książki Telefonicznej
FROM python:3.11-slim

# Ustaw zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Utwórz katalog aplikacji
WORKDIR /app

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements i zainstaluj zależności Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Utwórz katalog na bazę danych
RUN mkdir -p /app/data

# Ustaw uprawnienia
RUN chmod +x /app

# Eksponuj port
EXPOSE 8000

# Uruchom aplikację
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
