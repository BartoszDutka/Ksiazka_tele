# Instrukcja konfiguracji DNS dla Administratora Windows Server

## 🎯 Cel
Udostępnienie aplikacji "Książka Telefoniczna" dla ~200 komputerów w sieci firmowej pod adresem:
`http://igrabka.ksiazka-tel.company.local`

## 🔧 Konfiguracja DNS na Windows Server

### Krok 1: Otwórz DNS Manager
```
Start → Administrative Tools → DNS Manager
lub uruchom: dnsmgmt.msc
```

### Krok 2: Dodaj A Record
1. **Rozwiń serwer DNS**
2. **Rozwiń "Forward Lookup Zones"**
3. **Prawym klikiem na domenę firmową** (np. `company.local`)
4. **Wybierz "New Host (A or AAAA)..."**

### Krok 3: Konfiguracja wpisu
```
Name: igrabka.ksiazka-tel
IP Address: 192.168.102.174
☑ Create associated pointer (PTR) record
```
**Kliknij "Add Host"**

### Krok 4: Weryfikacja
```cmd
# Na dowolnym komputerze w domenie:
nslookup igrabka.ksiazka-tel.company.local
```

Powinno zwrócić: `192.168.102.174`

## 🌐 Dostęp dla użytkowników

Po konfiguracji DNS wszyscy użytkownicy będą mogli korzystać z aplikacji pod adresem:
```
http://igrabka.ksiazka-tel.company.local
```

### Alternatywne adresy:
- Bezpośredni IP: `http://192.168.102.174`
- Localhost (na serwerze): `http://localhost`

## 📱 Instrukcja dla użytkowników końcowych

### Dostęp do aplikacji:
1. **Otwórz przeglądarkę**
2. **Wpisz adres**: `http://igrabka.ksiazka-tel.company.local`
3. **Zaloguj się jako admin** (jeśli potrzebujesz edytować kontakty):
   - Email: `admin@firma.pl`
   - Hasło: `admin123`

### Funkcje aplikacji:
- 📋 **Przeglądanie kontaktów** - lista wszystkich numerów wewnętrznych
- 🔍 **Wyszukiwanie** - szybkie znajdowanie po imieniu, nazwisku, dziale
- 🏢 **Filtrowanie** - sortowanie po dziale
- ⚙️ **Zarządzanie** (tylko admin) - dodawanie, edytowanie, usuwanie

## 🔒 Bezpieczeństwo

### Zalecenia:
- Zmień domyślne hasło administratora
- Rozważ ograniczenie dostępu przez grupy AD
- Skonfiguruj HTTPS w środowisku produkcyjnym

### Firewall:
Upewnij się, że port 80 jest otwarty na serwerze z aplikacją.

## 📞 Pomoc techniczna

### Problemy z dostępem:
1. Sprawdź połączenie sieciowe
2. Sprawdź czy DNS resolver działa: `nslookup igrabka.ksiazka-tel.company.local`
3. Sprawdź czy aplikacja działa: `telnet 192.168.102.174 80`
4. Wyczyść cache DNS: `ipconfig /flushdns`

### Logi aplikacji:
Dostępne w terminalu na serwerze gdzie uruchomiona jest aplikacja.
