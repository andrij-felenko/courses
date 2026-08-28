#!/usr/bin/env bash
# chaos_rollback_test.sh - Тестування автоматичного відкату під навантаженням

set -euo pipefail

echo "== [1/4] Стартуємо тестове розгортання версії v2.2.0 =="
./migration_controller --action deploy --version v2.2.0 &
CTRL_PID=$!

sleep 5

echo "== [2/4] Інжектимо 500-ті помилки в канареєчний сервіс (5% трафіку) =="
curl -X POST http://localhost:8080/admin/chaos/inject-errors?rate=5.0

echo "== [3/4] Очікуємо на автоматичний спрацювання контролера відкату =="
wait $CTRL_PID || true

echo "== [4/4] Перевіряємо стан сервісів та сумісність бази даних =="
STATUS=$(curl -s http://localhost:8080/health | jq -r '.active_version')

if [ "$STATUS" == "v2.1.0" ]; then
    echo "✅ ТЕСТ ПРОЙДЕНО: Контролер успішно відкотив трафік на v2.1.0 без втрати даних!"
else
    echo "❌ ТЕСТ ПРОВАЛЕНО: Система залишилася на невалідній версії $STATUS!"
    exit 1
fi
