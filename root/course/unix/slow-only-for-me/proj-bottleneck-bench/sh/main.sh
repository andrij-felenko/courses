#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Використання: $0 <PID> [тривалість_секунд]"
    exit 1
fi

PID="$1"
DURATION="${2:-3}"

if [[ ! -d "/proc/$PID" ]]; then
    echo "Помилка: процес з PID $PID не знайдено."
    exit 1
fi

CMD=$(cat "/proc/$PID/comm")
echo "=========================================================="
echo " ДІАГНОСТИЧНИЙ ЗОНД ПРОЦЕСУ: $CMD (PID: $PID)"
echo "=========================================================="

echo -e "\n[1] Розподіл CPU та перемикань контексту (pidstat):"
pidstat -u -w -r -p "$PID" 1 2

echo -e "\n[2] Поточний стан та функція очікування ядра (wchan):"
ps -o pid,tid,stat,wchan:24,comm -T -p "$PID"

echo -e "\n[3] Облік введення-виведення (/proc/$PID/io):"
cat "/proc/$PID/io"

echo -e "\n[4] Статистика затримки в черзі (/proc/$PID/schedstat):"
read -r CPU_TIME WAIT_TIME SLICES < "/proc/$PID/schedstat"
echo "  Час на CPU:       $((CPU_TIME / 1000000)) мс"
echo "  Очікування черги: $((WAIT_TIME / 1000000)) мс"
echo "  Квантів часу:     $SLICES"

echo -e "\n[5] Швидкий зріз системних викликів (strace $DURATION сек):"
strace -c -f -p "$PID" sleep "$DURATION" 2>&1 | tail -n 12

echo "=========================================================="
echo " Діагностику завершено."
