# Książka Telefoniczna - Aplikacja Webowa

Kompletna aplikacja webowa do zarządzania książką telefoniczną firmy z numerami wewnętrznymi.

## Funkcjonalności

- **Uwierzytelnianie**: Logowanie administratora z rolą zarządzania kontaktami
- **Zarządzanie kontaktami**: Dodawanie, edytowanie, usuwanie i wyszukiwanie kontaktów
- **Wyszukiwanie i filtrowanie**: Przeszukiwanie po imieniu, nazwisku, dziale, numerze wewnętrznym
- **Sortowanie**: Sortowanie po nazwisku (A-Z, Z-A), dziale, dacie utworzenia
- **Paginacja**: Wyświetlanie wyników po 20 na stronę
- **API**: RESTful API z dokumentacją OpenAPI po polsku

## Stos technologiczny

- **Backend**: FastAPI + Starlette Sessions
- **Frontend**: Jinja2 + HTMX + Tailwind CSS (CDN)
- **Baza danych**: SQLite + SQLModel (SQLAlchemy)
- **Uwierzytelnianie**: Passlib z bcrypt
- **Walidacja numerów**: phonenumbers (region PL)
- **Konfiguracja**: pydantic-settings (.env)

## Instalacja i uruchomienie

### Wymagania

- Python 3.11+
- pip

### Krok po kroku

1. **Klonowanie/pobranie projektu**
   ```bash
   cd ksiazka_tele
   ```

2. **Tworzenie środowiska wirtualnego**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Instalacja zależności**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfiguracja środowiska**
   
   Skopiuj `.env.example` do `.env` i dostosuj ustawienia:
   ```bash
   copy .env.example .env
   ```

   Edytuj `.env`:
   ```
   ADMIN_EMAIL=admin@firma.pl
   ADMIN_PASSWORD=admin123
   SECRET_KEY=twoj_super_tajny_klucz_sesji_min_32_znaki
   DATABASE_URL=sqlite:///./ksiazka_tele.db
   ```

5. **Uruchomienie aplikacji**
   ```bash
   uvicorn app.main:app --reload
   ```

   Lub używając Makefile:
   ```bash
   make run
   ```

6. **Dostęp do aplikacji**
   - Aplikacja: http://localhost
   - Dokumentacja API: http://localhost/docs
   - Lista kontaktów: http://localhost/kontakty
   - Logowanie: http://localhost/logowanie

## Dostęp w sieci lokalnej

Aplikacja jest skonfigurowana do działania w sieci lokalnej, dzięki czemu można uzyskać do niej dostęp z innych urządzeń w tej samej sieci.

### Krok po kroku

1. **Sprawdź adres IP komputera**
   
   **Windows:**
   ```bash
   ipconfig | findstr "IPv4"
   ```
   
   **Linux/Mac:**
   ```bash
   ip addr show | grep inet
   # lub
   ifconfig | grep inet
   ```
   
   Przykładowy wynik: `192.168.102.174`

2. **Dostęp z innych urządzeń**
   
   Otwórz przeglądarkę na dowolnym urządzeniu w tej samej sieci i przejdź do:
   ```
   http://192.168.102.174
   ```

3. **Konfiguracja nazwy domenowej**
   
   Aby aplikacja była dostępna pod adresem `http://igrabka.ksiazka-tel.pl`, edytuj plik hosts:
   
   **Windows** (`C:\Windows\System32\drivers\etc\hosts`):
   ```
   192.168.102.174   igrabka.ksiazka-tel.pl
   ```
   
   **Linux/Mac** (`/etc/hosts`):
   ```
   192.168.102.174   igrabka.ksiazka-tel.pl
   ```
   
   Po dodaniu tego wpisu aplikacja będzie dostępna pod adresem:
   ```
   http://igrabka.ksiazka-tel.pl
   ```

### Uwagi dotyczące bezpieczeństwa

- W środowisku produkcyjnym zaleca się używanie HTTPS
- Należy skonfigurować firewall, aby ograniczyć dostęp tylko do zaufanych urządzeń
- Rozważ zmianę domyślnych danych logowania administratora

### Środowisko korporacyjne (Windows Server)

Dla sieci z wieloma komputerami (np. 200+ stanowisk) zalecana jest konfiguracja DNS na Windows Server:

1. **Otwórz DNS Manager** na serwerze domeny
2. **Dodaj A Record**:
   ```
   Name: igrabka.ksiazka-tel
   IP: 192.168.102.174
   ```
3. **Dostęp dla wszystkich**: `http://igrabka.ksiazka-tel.company.local`

**Zobacz**: `INSTRUKCJA_ADMIN_DNS.md` - szczegółowa instrukcja dla administratora

### Rozwiązywanie problemów sieciowych

**Problem:** Nie można uzyskać dostępu z innych urządzeń w sieci
- Sprawdź czy firewall Windows nie blokuje portu 80
- Upewnij się, że komputer i urządzenie docelowe są w tej samej sieci
- Spróbuj wyłączyć tymczasowo firewall do testów
- **Uwaga**: Port 80 wymaga uprawnień administratora na niektórych systemach

**Problem:** Błąd "Connection refused"
- Upewnij się, że aplikacja została uruchomiona z parametrem `--host 0.0.0.0`
- Sprawdź czy port 80 nie jest używany przez inną aplikację (np. IIS, Apache)
- Na Windows może być konieczne uruchomienie aplikacji jako Administrator

**Sprawdzenie czy port jest otwarty:**
```bash
# Windows
netstat -an | findstr :80

# Linux/Mac  
netstat -an | grep :80
```

## Struktura projektu

```
ksiazka_tele/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Główna aplikacja FastAPI
│   ├── config.py              # Konfiguracja aplikacji
│   ├── database.py            # Konfiguracja bazy danych
│   ├── auth.py                # Uwierzytelnianie i sesje
│   ├── models/
│   │   ├── __init__.py
│   │   ├── contact.py         # Model kontaktu
│   │   └── user.py            # Model użytkownika
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── contacts.py        # Endpointy UI dla kontaktów
│   │   ├── auth.py            # Endpointy uwierzytelniania
│   │   └── api/
│   │       ├── __init__.py
│   │       └── contacts.py    # API endpoints
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── contacts/
│       │   ├── list.html
│       │   ├── detail.html
│       │   ├── create.html
│       │   └── edit.html
│       └── auth/
│           └── login.html
├── static/
│   └── css/
│       └── custom.css
├── .env.example
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .pre-commit-config.yaml
└── README.md
```

## Użytkowanie

### Logowanie administratora

1. Przejdź do http://localhost:8000/logowanie
2. Użyj danych z pliku `.env`:
   - Email: wartość z `ADMIN_EMAIL`
   - Hasło: wartość z `ADMIN_PASSWORD`

### Zarządzanie kontaktami

Po zalogowaniu jako administrator możesz:

- **Przeglądać kontakty**: Lista wszystkich kontaktów z możliwością wyszukiwania i filtrowania
- **Dodawać kontakty**: Formularz z polami: Imię, Nazwisko, Numer wewnętrzny (wymagany), Dział
- **Edytować kontakty**: Modyfikacja istniejących danych kontaktów
- **Usuwać kontakty**: Usuwanie niepotrzebnych kontaktów
- **Wyszukiwać**: Szybkie wyszukiwanie po wszystkich polach kontaktu
- **Filtrować**: Filtrowanie po dziale
- **Sortować**: Sortowanie po nazwisku lub dziale

### Pola kontaktu

- **Imię** - Imię kontaktu
- **Nazwisko** - Nazwisko kontaktu  
- **Numer wewnętrzny** - Unikalny numer wewnętrzny firmy (wymagany)
- **Dział** - Nazwa działu (np. "Sprzedaż", "IT", "HR")
- **Firma** - Nazwa firmy (opcjonalne)
- **Notatki** - Dodatkowe informacje (opcjonalne)

## API

Aplikacja udostępnia RESTful API pod ścieżką `/api/kontakty`:

- `GET /api/kontakty` - Lista kontaktów z parametrami wyszukiwania
- `GET /api/kontakty/{id}` - Szczegóły kontaktu
- `POST /api/kontakty` - Dodanie kontaktu (tylko admin)
- `PUT /api/kontakty/{id}` - Aktualizacja kontaktu (tylko admin)
- `DELETE /api/kontakty/{id}` - Usunięcie kontaktu (tylko admin)

Pełna dokumentacja API dostępna pod: http://localhost:8000/docs

## Rozwój aplikacji

### Narzędzia deweloperskie

```bash
# Uruchomienie aplikacji
make run

# Formatowanie kodu
make format

# Analiza statyczna kodu
make lint

# Wszystkie sprawdzenia
make check
```

### Pre-commit hooks

```bash
# Instalacja pre-commit hooks
pre-commit install

# Uruchomienie ręczne
pre-commit run --all-files
```

### Docker

```bash
# Budowanie i uruchomienie z Docker
docker-compose up --build

# Zatrzymanie
docker-compose down
```

Aplikacja będzie dostępna na:
- Localhost: http://localhost
- Sieć lokalna: http://192.168.102.174
- Nazwa domenowa: http://igrabka.ksiazka-tel.pl (po konfiguracji hosts)

**Uwaga:** Docker automatycznie konfiguruje aplikację do pracy w sieci lokalnej z parametrami `--host 0.0.0.0 --port 80`.

## Licencja

Projekt stworzony dla celów edukacyjnych i biznesowych.
