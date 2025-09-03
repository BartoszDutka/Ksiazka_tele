@echo off
echo ========================================
echo    Konfiguracja Firewall dla Książki Telefonicznej
echo ========================================

echo UWAGA: Ten skrypt wymaga uprawnień administratora!
echo.

echo Otwieranie portu 80 w firewall...
netsh advfirewall firewall add rule name="Ksiazka Telefoniczna - Port 80" dir=in action=allow protocol=TCP localport=8000

echo.
echo Dodawanie Python do wyjątków firewall...
netsh advfirewall firewall add rule name="Python - Ksiazka Telefoniczna" dir=in action=allow program="%cd%\venv\Scripts\python.exe"

echo.
echo ========================================
echo    Konfiguracja zakończona!
echo ========================================
echo.
echo Teraz inne komputery powinny móc łączyć się pod adresem:
echo http://192.168.102.174:80
echo.

pause
