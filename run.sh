#!/bin/bash

# Быстрый запуск Hotel Planner

# Получаем абсолютный путь к директории приложения
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$APP_DIR"

echo "🏨 Запуск Hotel Planner..."
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден."
    echo "Запустите setup.sh для установки."
    exit 1
fi

# Открываем браузер через 2 секунды (в фоне)
(sleep 2 && open http://localhost:5001 2>/dev/null || xdg-open http://localhost:5001 2>/dev/null) &

echo "🚀 Приложение запущено!"
echo "📍 Откройте в браузере: http://localhost:5001"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Запуск приложения
python3 app.py
