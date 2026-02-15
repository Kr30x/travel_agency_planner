@echo off
REM Скрипт быстрой установки и запуска Hotel Planner (Windows)

echo 🏨 Установка Hotel Planner...
echo.

REM Получаем путь к текущей директории
set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

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

REM Создание ярлыка на рабочем столе
echo.
echo 🔗 Создание ярлыка на рабочем столе...

set "DESKTOP=%USERPROFILE%\Desktop"

REM Создаём VBS скрипт для создания ярлыка
set "VBS_FILE=%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_FILE%"
echo sLinkFile = "%DESKTOP%\Hotel Planner.lnk" >> "%VBS_FILE%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_FILE%"
echo oLink.TargetPath = "%APP_DIR%\run.bat" >> "%VBS_FILE%"
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%VBS_FILE%"
echo oLink.Description = "Планировщик размещения гостей" >> "%VBS_FILE%"
echo oLink.Save >> "%VBS_FILE%"

REM Выполняем VBS скрипт
cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%"

echo ✓ Ярлык создан на рабочем столе

REM Запуск приложения
echo.
echo 🚀 Запуск приложения...
echo 📍 Приложение будет доступно по адресу: http://localhost:5001
echo.
echo 💡 В следующий раз используйте ярлык на рабочем столе!
echo.
echo Нажмите Ctrl+C для остановки
echo.

start http://localhost:5001
python app.py
pause
