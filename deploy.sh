#!/bin/bash
# Быстрое распределение всех исправлений

set -e  # Остановиться при ошибке

echo "✋ НАЧИНАЕМ РАСПРЕДЕЛЕНИЕ фиксов..."

# 1. Обновить код
echo "✍️  Шаг 1: Обновление кода..."
git pull origin main
echo "✅ Код обновлен!"

# 2. Показать актуальные коммиты
echo ""
echo "🔗 Примененные коммиты:"
git log --oneline | head -5

# 3. Перезагружить Django
echo ""
echo "✍️  Шаг 2: Перезагрузка Django..."

# Проверяем если служба systemd
if sudo systemctl status hair-purchase &> /dev/null; then
    echo "🔄 Перезагружаем systemd службу..."
    sudo systemctl restart hair-purchase
    echo "✅ Systemd перезагружен!"
else
    echo "🔄 Перезагружаем gunicorn..."
    pkill -f gunicorn || true
    sleep 2
    source venv/bin/activate 2>/dev/null || true
    nohup gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 > /tmp/gunicorn.log 2>&1 &
    echo "✅ Gunicorn перезагружен!"
fi

# 4. Ожидание
echo ""
echo "⏳ Небольшое ожидание (3 сек)..."
sleep 3

# 5. Проверка статуса
echo ""
echo "✍️  Шаг 3: Проверка статуса..."

if sudo systemctl status hair-purchase &> /dev/null 2>&1; then
    echo "✅ Сервис работает!"
    echo ""
    echo "📄 Последние логи:"
    journalctl -u hair-purchase -n 10 --no-pager
else
    echo "⚠️  Не удалось сразу. Проверяю..."
    sleep 3
    if sudo systemctl status hair-purchase &> /dev/null 2>&1; then
        echo "✅ Нынче работает!"
    else
        echo "❌ Ошибка! Проверьте логи:"
        journalctl -u hair-purchase -n 20 --no-pager
        exit 1
    fi
fi

echo ""
echo "🎉 ВСЕ ГОТОВО!"
echo ""
echo "🌐 Проверьте сайт:"
echo "   https://4895c9d9450e.vps.myjino.ru/"
echo ""
echo "📄 Документация:"
echo "   - BUG_FIX_100_PLUS.md (исправление для 100+ см)"
echo "   - DEPLOYMENT_INSTRUCTIONS.md (инструкции)"
echo ""
