# Książka Telefoniczna - Instrukcje uruchamiania

## Szybkie uruchomienie

### Opcja 1: Użyj skryptu (zalecane)
1. Kliknij dwukrotnie na plik `start_app.bat`
2. Poczekaj na uruchomienie serwera
3. Aplikacja będzie dostępna pod adresami:
   - **Lokalnie**: http://localhost:80 (lub po prostu http://localhost)
   - **W sieci**: http://192.168.102.174:80 (lub po prostu http://192.168.102.174)
   - **Domena**: https://ksiazka-tel.siec.instytut

### Dostęp z innych komputerów
Inne komputery w sieci mogą łączyć się pod adresami:
- **HTTP**: http://192.168.102.174
- **HTTPS (domena)**: https://ksiazka-tel.siec.instytut

### Opcja 2: Pierwsza instalacja
Jeśli uruchamiasz po raz pierwszy lub masz problemy:
1. Kliknij dwukrotnie na plik `setup_and_run.bat`
2. Wybierz "Y" aby uruchomić aplikację po instalacji

### Opcja 3: PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start_app.ps1
```

### Opcja 4: Ręcznie
```cmd
cd "c:\Users\bdutka\Desktop\Ksiazka_tele"
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80
```

## Dostęp sieciowy

### Adres sieciowy
- **IP serwera**: 192.168.102.174
- **Port**: 80 (standardowy HTTP)
- **Pełny adres HTTP**: http://192.168.102.174
- **Domena HTTPS**: https://ksiazka-tel.siec.instytut

### Konfiguracja firewall (jeśli potrzebna)
Jeśli inne komputery nie mogą się połączyć, może być potrzebne:
1. Otwórz "Windows Defender Firewall"
2. Kliknij "Allow an app or feature through Windows Defender Firewall"
3. Dodaj Python lub port 80 do wyjątków

### Uprawnienia administratora
Port 80 wymaga uprawnień administratora na Windows.
Uruchom cmd lub PowerShell jako administrator przed uruchomieniem skryptu.

## Pliki

- `start_app.bat` - Główny skrypt uruchamiający
- `start_app.ps1` - Wersja PowerShell
- `setup_and_run.bat` - Pierwsza instalacja + uruchomienie
- `requirements.txt` - Lista wymaganych pakietów Python

## Rozwiązywanie problemów

### Problem: "python nie jest rozpoznany"
- Zainstaluj Python z https://python.org
- Podczas instalacji zaznacz "Add Python to PATH"

### Problem: Błąd aktywacji środowiska wirtualnego
- Uruchom `setup_and_run.bat` aby odtworzyć środowisko

### Problem: Port 8000 jest zajęty
- Zamknij inne aplikacje używające portu 8000
- Lub zmień port w skrypcie na inny (np. 8001)

## Zatrzymywanie aplikacji

Naciśnij `Ctrl+C` w oknie terminala aby zatrzymać serwer.
