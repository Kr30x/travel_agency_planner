@echo off
REM Скрипт быстрой установки и запуска Hotel Planner (Windows)

echo 🏨 Установка Hotel Planner...
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8 или выше.
    pause
    exit /b 1
)

echo ✓ Python найден
python --version

REM Установка зависимостей
echo.
echo 📦 Установка зависимостей...
pip install -r requirements.txt --quiet

if %errorlevel% equ 0 (
    echo ✓ Зависимости установлены
) else (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)

REM Запуск приложения
echo.
echo 🚀 Запуск приложения...
echo 📍 Приложение будет доступно по адресу: http://localhost:5001
echo.
echo Нажмите Ctrl+C для остановки
echo.

python app.py
pause
