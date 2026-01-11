@echo off
REM Быстрый запуск Hotel Planner

REM Получаем путь к директории приложения
cd /d "%~dp0"

echo 🏨 Запуск Hotel Planner...
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден.
    echo Запустите setup.bat для установки.
    pause
    exit /b 1
)

echo 🚀 Приложение запущено!
echo 📍 Откройте в браузере: http://localhost:5001
echo.
echo Нажмите Ctrl+C для остановки
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Открываем браузер
start http://localhost:5001

REM Запуск приложения
python app.py

pause
