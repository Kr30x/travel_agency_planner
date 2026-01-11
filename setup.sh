#!/bin/bash

# Скрипт быстрой установки и запуска Hotel Planner

echo "🏨 Установка Hotel Planner..."
echo ""

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

# Запуск приложения
echo ""
echo "🚀 Запуск приложения..."
echo "📍 Приложение будет доступно по адресу: http://localhost:5001"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""

python3 app.py
