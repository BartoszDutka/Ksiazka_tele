# Książka Telefoniczna - Skrypt uruchamiający
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Książka Telefoniczna - Uruchamianie" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan

Set-Location "c:\Users\bdutka\Desktop\Ksiazka_tele"

Write-Host "Aktywowanie środowiska wirtualnego..." -ForegroundColor Yellow
& venv\Scripts\Activate.ps1

Write-Host "Sprawdzanie zależności..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Uruchamianie serwera..." -ForegroundColor Green
Write-Host "Aplikacja będzie dostępna pod adresami:" -ForegroundColor Green
Write-Host "  - Lokalnie: http://localhost:80" -ForegroundColor Green
Write-Host "  - W sieci: http://192.168.102.174:80" -ForegroundColor Green
Write-Host "  - Domena: https://ksiazka-tel.siec.instytut (przez reverse proxy)" -ForegroundColor Green
Write-Host "Aby zatrzymać serwer, naciśnij Ctrl+C" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80
