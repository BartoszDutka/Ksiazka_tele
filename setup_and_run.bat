@echo off
echo ========================================
echo    Ksiazka Telefoniczna - Pierwsza Instalacja
echo ========================================

cd /d "c:\Users\bdutka\Desktop\Ksiazka_tele"

if not exist "venv\" (
    echo Tworzenie srodowiska wirtualnego...
    python -m venv venv
    if errorlevel 1 (
        echo BLAD: Nie udalo sie utworzyc srodowiska wirtualnego
        echo Sprawdz czy masz zainstalowany Python
        pause
        exit /b 1
    )
)

echo Aktywowanie srodowiska wirtualnego...
call venv\Scripts\activate.bat

echo Instalowanie zaleznosci...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo    Instalacja zakonczona pomyslnie!
echo ========================================
echo.
echo Teraz mozesz uruchomic aplikacje za pomoca:
echo   start_app.bat
echo.
echo Lub uruchom teraz:

choice /C YN /M "Czy chcesz uruchomic aplikacje teraz"
if errorlevel 2 goto end
if errorlevel 1 goto start

:start
echo Uruchamianie serwera...
echo Aplikacja bedzie dostepna pod adresami:
echo   - Lokalnie: http://localhost:80
echo   - W sieci: http://192.168.102.174:80
echo   - Domena: https://ksiazka-tel.siec.instytut (przez reverse proxy)
echo Aby zatrzymac serwer, nacisnij Ctrl+C
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80

:end
pause
