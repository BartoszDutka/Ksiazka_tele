@echo off
echo ========================================
echo    Test połączenia sieciowego
echo ========================================

echo Aktualne IP komputera:
ipconfig | findstr "IPv4"

echo.
echo Testowanie portu 8000...
netstat -an | findstr ":8000"

echo.
echo Sprawdzanie firewall...
netsh advfirewall firewall show rule name="Python" | findstr "Enabled"

echo.
echo ========================================
echo    Instrukcje dla innych komputerów:
echo ========================================
echo.
echo 1. Otwórz przeglądarkę na innym komputerze
echo 2. Wpisz adres: http://192.168.102.174:8000
echo 3. Jeśli nie działa, sprawdź:
echo    - Czy firewall nie blokuje portu 8000
echo    - Czy oba komputery są w tej samej sieci
echo    - Czy IP 192.168.102.174 jest aktualny
echo.

pause
