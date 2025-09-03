# Instrukcja dostępu do Książki Telefonicznej w sieci lokalnej

## Szybki start

1. **Adres IP serwera**: `192.168.102.174`

2. **Otwórz aplikację w przeglądarce**:
   ```
   http://192.168.102.174
   ```

3. **Zaloguj się jako administrator**:
   - Email: `admin@firma.pl`
   - Hasło: `admin123`

## Dostęp z różnych urządzeń

### Komputer Windows/Mac/Linux
Otwórz dowolną przeglądarkę i wpisz adres IP:
```
http://192.168.102.174
```

### Telefon/Tablet
1. Połącz się z tą samą siecią Wi-Fi
2. Otwórz przeglądarkę mobilną
3. Wpisz ten sam adres: `http://192.168.102.174`

### Konfiguracja nazwy domenowej (opcjonalnie)

Jeśli chcesz używać przyjaznej nazwy zamiast adresu IP:

**Windows:**
1. Otwórz Notatnik jako Administrator
2. Otwórz plik: `C:\Windows\System32\drivers\etc\hosts`
3. Dodaj linię: `192.168.102.174   igrabka.ksiazka-tel.pl`
4. Zapisz plik
5. Aplikacja będzie dostępna pod: `http://igrabka.ksiazka-tel.pl`

**Mac/Linux:**
1. Otwórz terminal
2. Wykonaj: `sudo nano /etc/hosts`
3. Dodaj linię: `192.168.102.174   igrabka.ksiazka-tel.pl`
4. Zapisz plik (Ctrl+X, Y, Enter w nano)
5. Aplikacja będzie dostępna pod: `http://igrabka.ksiazka-tel.pl`

## Dostęp przez adres IP vs nazwę domenową

### Opcja A: Bezpośredni dostęp przez IP
```
http://192.168.102.174
```
✅ Działa od razu, bez konfiguracji  
❌ Trudny do zapamiętania adres

### Opcja B: Dostęp przez nazwę domenową  
```
http://igrabka.ksiazka-tel.pl
```
✅ Łatwy do zapamiętania adres  
❌ Wymaga konfiguracji pliku hosts

**Zalecenie**: Użyj opcji B (nazwa domenowa) dla wygody użytkowników

## Funkcje aplikacji

- **Przeglądanie kontaktów**: Lista wszystkich numerów wewnętrznych
- **Wyszukiwanie**: Szybkie znajdowanie kontaktów po imieniu, nazwisku, dziale
- **Filtrowanie**: Sortowanie po dziale
- **Zarządzanie** (tylko admin): Dodawanie, edytowanie, usuwanie kontaktów

## Pomoc techniczna

Jeśli masz problemy z dostępem:
1. Sprawdź czy oba urządzenia są w tej samej sieci
2. Upewnij się, że serwer jest uruchomiony
3. Sprawdź firewall na komputerze serwera (port 80)
4. Spróbuj dostępu przez `http://localhost` bezpośrednio na serwerze
5. **Ważne**: Port 80 może wymagać uprawnień administratora
