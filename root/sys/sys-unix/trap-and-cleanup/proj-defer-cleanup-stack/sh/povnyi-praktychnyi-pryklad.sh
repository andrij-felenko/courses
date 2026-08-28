#!/usr/bin/env bash
set -euo pipefail

# Завантаження та ініціалізація реєстру defer
# source ./defer.sh
defer_init

echo "[1/5] Захоплення ексклюзивного замка завдання..."
LOCK_FILE="/var/lock/db_backup.lock"
defer_flock "${LOCK_FILE}" 200

echo "[2/5] Створення ізольованого робочого каталогу..."
defer_mktemp_dir WORK_DIR "db_backup"
echo "Робочий каталог створено: ${WORK_DIR}"

echo "[3/5] Запуск локального агента моніторингу метрик..."
defer_spawn MONITOR_PID sleep 600
echo "Моніторинг запущено в фоні (PID=${MONITOR_PID})"

echo "[4/5] Генерація тестового дампу бази даних..."
DUMP_FILE="${WORK_DIR}/production_data.sql"
# Емуляція запису великого обсягу даних
dd if=/dev/urandom of="${DUMP_FILE}" bs=1M count=20 status=none

echo "[5/5] Стиснення архіву..."
gzip -c "${DUMP_FILE}" > "${DUMP_FILE}.gz"

echo "Резервне копіювання завершено без помилок."
