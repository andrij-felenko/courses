#!/usr/bin/env bash
# log_analyzer.sh — виробничий скрипт моніторингу помилок 5xx
set -euo pipefail

LOG_FILE="${1:-/var/log/nginx/access.log}"
TOP_LIMIT="${2:-10}"

# Перевірка наявності та прав читання файлу
if [[ ! -r "$LOG_FILE" ]]; then
    echo "[ПОМИЛКА] Файл логів не існує або недоступний для читання: $LOG_FILE" >&2
    exit 1
fi

# Тимчасовий іменований канал для безпечного завершення
FIFO_DIR=$(mktemp -d -t logpipe.XXXXXX)
FIFO_PATH="$FIFO_DIR/stream.fifo"
mkfifo "$FIFO_PATH"

# Прибирання ресурсів при виході або отриманні сигналів переривання
cleanup() {
    local exit_code=$?
    rm -rf "$FIFO_DIR"
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

echo "[ІНФО] Початок обробки: $LOG_FILE (Top $TOP_LIMIT аномальних IP)" >&2

# Запуск конвеєра з примусовою локаллю LC_ALL=C для максимальної швидкості
LC_ALL=C tail -n +1 -F "$LOG_FILE" 2>/dev/null | \
stdbuf -i0 -oL -e0 grep -E '" (500|502|503|504) ' | \
stdbuf -i0 -oL -e0 awk '{ print $1, $9, $7 }' | \
stdbuf -i0 -oL -e0 sed -E 's/\?.*//' > "$FIFO_PATH" &

PID_PRODUCER=$!

# Споживач: зчитування з каналу, агрегація та вивід звіту
awk '
{
    ip = $1;
    status = $2;
    uri = $3;
    
    count[ip]++;
    total_errors++;
}
END {
    printf "\n=== ЗВІТ ПРО АНОМАЛІЇ 5XX ===\n";
    printf "Всього зафіксовано помилок: %d\n", total_errors;
    printf "%-8s %-18s\n", "КІЛЬКІСТЬ", "IP-АДРЕСА";
    printf "%-8s %-18s\n", "--------", "-----------------";
    
    for (ip in count) {
        printf "%-8d %-18s\n", count[ip], ip;
    }
}' "$FIFO_PATH" | sort -k1,1nr | head -n "$TOP_LIMIT" || {
    status=$?
    # Код 141 (SIGPIPE) є штатним для head
    if [[ "$status" -ne 141 && "$status" -ne 0 ]]; then
        echo "[ПОМИЛКА] Збій агрегатора, код: $status" >&2
        exit "$status"
    fi
}

wait "$PID_PRODUCER" 2>/dev/null || true
echo "[ІНФО] Обробку завершено успішно." >&2
