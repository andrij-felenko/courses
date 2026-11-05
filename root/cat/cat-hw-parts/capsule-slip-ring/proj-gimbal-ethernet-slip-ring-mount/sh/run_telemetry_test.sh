#!/usr/bin/env bash
# run_telemetry_test.sh
# Скрипт для тестування мережі через капсульне ковзне кільце з одночасним збором телеметрії кута.

set -euo pipefail

TARGET_HOST="${1:-192.168.1.100}"
DURATION="${2:-30}"
OUTPUT_DIR="./telemetry_logs"

mkdir -p "$OUTPUT_DIR"

IPERF_LOG="$OUTPUT_DIR/iperf.log"
PING_LOG="$OUTPUT_DIR/ping.log"
ANGLE_LOG="$OUTPUT_DIR/angle.log"

echo "[*] Початок тестування ковзного кільця. Ціль: $TARGET_HOST, Тривалість: $DURATION с"

# 1. Запуск iperf3 у фоновому режимі (передача даних)
echo "[*] Запуск iperf3..."
iperf3 -c "$TARGET_HOST" -t "$DURATION" -i 1 --json > "$IPERF_LOG" 2>&1 &
IPERF_PID=$!

# 2. Запуск ping у фоновому режимі (вимірювання латентності та втрат)
echo "[*] Запуск ping..."
ping -i 0.2 "$TARGET_HOST" > "$PING_LOG" 2>&1 &
PING_PID=$!

# 3. Симуляція/збір кутового положення підвісу з мітками часу
echo "[*] Збір кутової телеметрії..."
START_TIME=$(date +%s%N)
END_TIME=$((START_TIME + DURATION * 1000000000))

while [ $(date +%s%N) -lt "$END_TIME" ]; do
    CURRENT_TIME=$(date +%s.%N)
    # Симулюємо обертування підвісу (наприклад, 36 градусів на секунду)
    ELAPSED=$(echo "$(date +%s%N) - $START_TIME" | bc)
    ELAPSED_SEC=$(echo "scale=3; $ELapSED / 1000000000" | bc 2>/dev/null || awk "BEGIN {print $ELAPSED/1000000000}")
    ANGLE=$(echo "scale=1; (int($ELAPSED_SEC * 36)) % 360" | bc 2>/dev/null || awk "BEGIN {print int($ELAPSED_SEC * 36) % 360}")
    
    echo "$CURRENT_TIME angle=$ANGLE" >> "$ANGLE_LOG"
    sleep 0.05
done

# Зупинка фонових процесів, якщо вони ще тривають
kill "$IPERF_PID" "$PING_PID" 2>/dev/null || true
wait "$IPERF_PID" "$PING_PID" 2>/dev/null || true

echo "[*] Тестування завершено. Логовані дані збережено в $OUTPUT_DIR"
