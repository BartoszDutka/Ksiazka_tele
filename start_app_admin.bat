@echo off
echo ========================================
echo    Ksiazka Telefoniczna - Uruchomienie jako Administrator
echo ========================================

:: Sprawdz czy uruchomione jako administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Uruchomiono jako administrator - OK
) else (
    echo UWAGA: Port 80 wymaga uprawnien administratora!
    echo Uruchamianie z uprawnieniami administratora...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "c:\Users\bdutka\Desktop\Ksiazka_tele"

echo Aktywowanie srodowiska wirtualnego...
call venv\Scripts\activate.bat

echo Sprawdzanie zaleznoci...
pip install -r requirements.txt

echo Uruchamianie serwera na porcie 80...
echo Aplikacja bedzie dostepna pod adresami:
echo   - Lokalnie: http://localhost
echo   - W sieci: http://192.168.102.174
echo   - Domena: https://ksiazka-tel.siec.instytut
echo Aby zatrzymac serwer, nacisnij Ctrl+C
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80

pause
