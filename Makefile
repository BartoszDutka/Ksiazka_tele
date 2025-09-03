# Makefile for Książka Telefoniczna

.PHONY: help install run dev format lint check test clean docker-build docker-run

# Default target
help:
	@echo "Dostępne komendy:"
	@echo "  install      - Instaluj zależności"
	@echo "  run          - Uruchom aplikację"
	@echo "  dev          - Uruchom w trybie deweloperskim"
	@echo "  format       - Formatuj kod (black, isort)"
	@echo "  lint         - Sprawdź kod (ruff)"
	@echo "  check        - Uruchom wszystkie sprawdzenia"
	@echo "  test         - Uruchom testy (jeśli dostępne)"
	@echo "  clean        - Wyczyść pliki tymczasowe"
	@echo "  docker-build - Zbuduj obraz Docker"
	@echo "  docker-run   - Uruchom z Docker Compose"

# Instalacja zależności
install:
	pip install -r requirements.txt

# Uruchomienie aplikacji
run:
	uvicorn app.main:app --host 0.0.0.0 --port 80

# Uruchomienie w trybie deweloperskim
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 80 --reload

# Formatowanie kodu
format:
	@echo "Formatowanie kodu nie jest dostępne - brak narzędzi"

# Sprawdzanie kodu
lint:
	@echo "Sprawdzanie kodu nie jest dostępne - brak narzędzi"

# Wszystkie sprawdzenia
check: lint
	@echo "Sprawdzenia zakończone"

# Testy (placeholder)
test:
	@echo "Testy nie są jeszcze zaimplementowane"

# Czyszczenie
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -delete

# Docker
docker-build:
	docker build -t ksiazka-tele .

docker-run:
	docker-compose up --build
