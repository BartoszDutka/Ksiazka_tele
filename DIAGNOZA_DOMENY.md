# Diagnozowanie problemu z domeną ksiazka-tel.siec.instytut

## Kroki diagnostyczne:

### 1. Sprawdź czy aplikacja działa lokalnie
```cmd
# Uruchom aplikację
start_app.bat

# Sprawdź w przeglądarce:
http://localhost:80
http://192.168.102.174:80
```

### 2. Sprawdź DNS
```cmd
nslookup ksiazka-tel.siec.instytut
ping ksiazka-tel.siec.instytut
```

### 3. Sprawdź czy port jest otwarty
```cmd
netstat -an | findstr ":80"
telnet ksiazka-tel.siec.instytut 443
```

### 4. Sprawdź certyfikat SSL
```cmd
# W przeglądarce sprawdź czy certyfikat jest ważny
# Lub użyj narzędzia online: https://www.ssllabs.com/ssltest/
```

### 5. Sprawdź logi serwera web
```cmd
# Nginx:
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/ksiazka-tel.error.log

# Apache:
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/ksiazka-tel_error.log

# Windows Event Log:
eventvwr.msc
```

## Możliwe problemy:

### Problem 1: Brak reverse proxy
**Objawy**: Domena nie odpowiada, timeout
**Rozwiązanie**: Skonfiguruj nginx lub Apache zgodnie z plikami:
- nginx-config.conf
- apache-config.conf

### Problem 2: Nieprawidłowy certyfikat SSL
**Objawy**: Błąd SSL, certificate error
**Rozwiązanie**: 
1. Sprawdź ważność certyfikatu
2. Upewnij się że certyfikat obejmuje domenę ksiazka-tel.siec.instytut
3. Odnów certyfikat jeśli jest przeterminowany

### Problem 3: Aplikacja nie działa na porcie 8000
**Objawy**: 502 Bad Gateway, connection refused
**Rozwiązanie**:
1. Uruchom start_app.bat
2. Sprawdź czy port 80 nie jest zablokowany przez firewall
3. Sprawdź logi aplikacji

### Problem 4: DNS nie wskazuje na właściwy serwer
**Objawy**: Domena wskazuje na inny serwer lub nie odpowiada
**Rozwiązanie**:
1. Skontaktuj się z administratorem DNS
2. Sprawdź czy rekord A wskazuje na właściwy IP
3. Sprawdź czy rekord CNAME jest prawidłowy

## Szybka naprawa:

### Jeśli wcześniej działało:
1. Sprawdź czy serwer web (nginx/apache) działa:
   ```cmd
   # Linux:
   systemctl status nginx
   systemctl status apache2
   
   # Windows:
   services.msc (sprawdź usługi nginx/apache)
   ```

2. Restart serwera web:
   ```cmd
   # Linux:
   sudo systemctl restart nginx
   sudo systemctl restart apache2
   
   # Windows:
   # Restart usługi przez services.msc
   ```

3. Sprawdź konfigurację:
   ```cmd
   # Nginx:
   nginx -t
   
   # Apache:
   apache2ctl configtest
   ```

### Adresy testowe:
- **Aplikacja bezpośrednio**: http://192.168.102.174
- **Localhost**: http://localhost  
- **Domena**: https://ksiazka-tel.siec.instytut

### Kontakt:
Jeśli problem nadal występuje, sprawdź:
1. Czy serwer Windows Server działa
2. Czy konfiguracja reverse proxy nie została zmieniona
3. Czy certyfikat SSL nie wygasł
