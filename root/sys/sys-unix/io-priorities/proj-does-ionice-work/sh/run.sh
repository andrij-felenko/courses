#!/bin/sh
# run.sh — звід «чи діє ionice»: планувальник × клас навантажувача.
#   sudo ./run.sh nvme0n1 /mnt/test/big.bin
set -eu
DEV=$1; FILE=$2
SEC=20; THREADS=16

echo "пристрій: $DEV   файл: $FILE"
for sched in none mq-deadline bfq; do
    if ! echo "$sched" > "/sys/block/$DEV/queue/scheduler" 2>/dev/null; then
        echo "$sched — недоступний (modprobe bfq?)"
        continue
    fi
    for cls in off 2 3; do
        sync
        echo 3 > /proc/sys/vm/drop_caches
        pid=
        if [ "$cls" != off ]; then
            ./iotest load "$FILE" "$cls" 0 "$THREADS" $((SEC + 5)) &
            pid=$!
            sleep 2                     # дати черзі наповнитися
        fi
        printf '%-12s  навантажувач %-3s  ' "$sched" "$cls"
        ./iotest meter "$FILE" "$SEC"
        if [ -n "$pid" ]; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
        sleep 2                         # дати носієві заспокоїтися
    done
done
