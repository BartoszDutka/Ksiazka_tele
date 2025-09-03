@echo off
echo ========================================
echo    Ksiazka Telefoniczna - Uruchamianie
echo ========================================

cd /d "c:\Users\bdutka\Desktop\Ksiazka_tele"

echo Aktywowanie srodowiska wirtualnego...
call venv\Scripts\activate.bat

echo Sprawdzanie zaleznoci...
pip install -r requirements.txt

echo Uruchamianie serwera...
echo Aplikacja bedzie dostepna pod adresami:
echo   - Lokalnie: http://localhost:80
echo   - W sieci: http://192.168.102.174:80
echo   - Domena: https://ksiazka-tel.siec.instytut (przez reverse proxy)
echo Aby zatrzymac serwer, nacisnij Ctrl+C
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80

pause
