#!/usr/bin/env bash
# Універсальна обгортка періодичного завдання: ексклюзивний замок, таймаут,
# протокол виконання й атомарний експорт метрик у node_exporter.
# Виклик: cron-job-wrapper.sh <job_name> <timeout_sec> <команда> [аргументи...]
set -u

if [ "$#" -lt 3 ]; then
    echo "Використання: $0 <job_name> <timeout_sec> <команда> [аргументи...]" >&2
    exit 2
fi

JOB_NAME="$1"
TIMEOUT_SEC="$2"
shift 2

if [ -z "$JOB_NAME" ]; then
    echo "Помилка: не вказано ім'я завдання" >&2
    exit 2
fi

case "$JOB_NAME" in
    *[!a-zA-Z0-9_-]*)
        echo "Помилка: ім'я завдання «$JOB_NAME» містить недопустимі символи" >&2
        exit 2
        ;;
esac

case "$TIMEOUT_SEC" in
    ''|*[!0-9]*)
        echo "Помилка: таймаут «$TIMEOUT_SEC» має бути цілим числом секунд" >&2
        exit 2
        ;;
esac

LOCK_DIR="/var/lock/cron"
METRICS_DIR="/var/lib/node_exporter/textfile_collector"
LOG_DIR="/var/log/cron"

mkdir -p "$LOCK_DIR" "$METRICS_DIR" "$LOG_DIR" || {
    echo "Помилка: не вдалося створити службові каталоги" >&2
    exit 2
}

LOCK_FILE="${LOCK_DIR}/${JOB_NAME}.lock"
PROM_FILE="${METRICS_DIR}/cron_${JOB_NAME}.prom"
LOG_FILE="${LOG_DIR}/${JOB_NAME}.log"

# Дескриптор 200 живе до кінця процесу — ядро зніме замок саме, навіть після
# SIGKILL. Завислих замків, на відміну від PID-файлів, тут не буває.
exec 200>"$LOCK_FILE"

if ! flock -n 200; then
    echo "[$(date -Iseconds)] [WARN] Завдання '${JOB_NAME}' уже виконується. Запуск пропущено." >> "$LOG_FILE"
    exit 0
fi

START_TS=$(date +%s)
START_HIRES=$(date +%s.%N)

echo "[$(date -Iseconds)] [INFO] Старт завдання '${JOB_NAME}': $*" >> "$LOG_FILE"

# Двоетапне завершення: спершу SIGTERM, через 30 с — безумовний SIGKILL.
timeout --kill-after=30s --signal=TERM "${TIMEOUT_SEC}" "$@" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

END_HIRES=$(date +%s.%N)
DURATION=$(awk -v a="$START_HIRES" -v b="$END_HIRES" 'BEGIN { printf "%.3f", b - a }')

SUCCESS=1
if [ "$EXIT_CODE" -ne 0 ]; then
    SUCCESS=0
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "[$(date -Iseconds)] [ERROR] Завдання '${JOB_NAME}' убито за таймаутом ${TIMEOUT_SEC}s" >> "$LOG_FILE"
    else
        echo "[$(date -Iseconds)] [ERROR] Завдання '${JOB_NAME}' завершилося з кодом ${EXIT_CODE}" >> "$LOG_FILE"
    fi
else
    echo "[$(date -Iseconds)] [INFO] Завдання '${JOB_NAME}' успішно завершено за ${DURATION} с" >> "$LOG_FILE"
fi

# Метрики пишемо у сусідній тимчасовий файл і переміщуємо атомарним rename(2):
# інакше скрапер прочитає недописаний файл і спіткнеться на півметриці.
TMP_PROM="${PROM_FILE}.$$"
cat > "$TMP_PROM" << EOF
# HELP node_cron_job_last_run_timestamp_seconds Unix timestamp останнього запуску завдання
# TYPE node_cron_job_last_run_timestamp_seconds gauge
node_cron_job_last_run_timestamp_seconds{job="${JOB_NAME}"} ${START_TS}
# HELP node_cron_job_duration_seconds Тривалість виконання завдання у секундах
# TYPE node_cron_job_duration_seconds gauge
node_cron_job_duration_seconds{job="${JOB_NAME}"} ${DURATION}
# HELP node_cron_job_success Статус виконання завдання (1 = успіх, 0 = помилка)
# TYPE node_cron_job_success gauge
node_cron_job_success{job="${JOB_NAME}"} ${SUCCESS}
# HELP node_cron_job_exit_code Код повернення процесу
# TYPE node_cron_job_exit_code gauge
node_cron_job_exit_code{job="${JOB_NAME}"} ${EXIT_CODE}
EOF

if ! mv -f "$TMP_PROM" "$PROM_FILE"; then
    rm -f "$TMP_PROM"
    echo "[$(date -Iseconds)] [WARN] Не вдалося оновити метрики ${PROM_FILE}" >> "$LOG_FILE"
fi

exit "$EXIT_CODE"
