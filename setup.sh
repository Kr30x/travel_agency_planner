#!/bin/bash

# Скрипт быстрой установки и запуска Hotel Planner

echo "🏨 Установка Hotel Planner..."
echo ""

# Получаем абсолютный путь к директории приложения
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"

# Установка зависимостей
echo ""
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Зависимости установлены"
else
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# Создание ярлыка на рабочем столе
echo ""
echo "🔗 Создание ярлыка на рабочем столе..."

DESKTOP_DIR="$HOME/Desktop"
if [ ! -d "$DESKTOP_DIR" ]; then
    DESKTOP_DIR="$HOME/Рабочий стол"
fi

if [ -d "$DESKTOP_DIR" ]; then
    # Для macOS создаём ссылку на run.sh
    if [[ "$OSTYPE" == "darwin"* ]]; then
        SHORTCUT_PATH="$DESKTOP_DIR/Hotel Planner.command"
        ln -sf "$APP_DIR/run.sh" "$SHORTCUT_PATH"
        chmod +x "$SHORTCUT_PATH"
        echo "✓ Ярлык создан: $SHORTCUT_PATH"
    
    # Для Linux создаём .desktop файл
    else
        SHORTCUT_PATH="$DESKTOP_DIR/hotel-planner.desktop"
        cat > "$SHORTCUT_PATH" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Hotel Planner
Comment=Планировщик размещения гостей
Exec=bash "$APP_DIR/run.sh"
Icon=applications-office
Terminal=true
Categories=Office;
EOF
        chmod +x "$SHORTCUT_PATH"
        echo "✓ Ярлык создан: $SHORTCUT_PATH"
    fi
else
    echo "⚠️  Рабочий стол не найден, ярлык не создан"
fi

# Запуск приложения
echo ""
echo "🚀 Запуск приложения..."
echo "📍 Приложение будет доступно по адресу: http://localhost:5001"
echo ""
echo "💡 В следующий раз используйте ярлык на рабочем столе!"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""

python3 app.py
