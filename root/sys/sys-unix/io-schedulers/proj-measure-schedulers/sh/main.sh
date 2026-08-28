#!/bin/sh
set -eu
DEV=$1                      # nvme0n1 або sda — цілий пристрій, не nvme0n1p2
DIR=$2                      # тека на файловій системі цього пристрою
SECS=${3:-60}

# файл для читання створюємо один раз і РЕАЛЬНИМИ даними, не дірою
[ -f "$DIR/rfile" ] || dd if=/dev/urandom of="$DIR/rfile" \
        bs=1M count=8192 oflag=direct status=none

printf '%-12s %8s %8s %8s %8s %9s %8s %8s\n' \
       планувальник p50 p99 p99.9 max читань/с прийн. носій

for s in none mq-deadline bfq kyber; do
    echo "$s" > "/sys/block/$DEV/queue/scheduler" 2>/dev/null || {
        echo "$s недоступний"; continue; }
    sync; echo 3 > /proc/sys/vm/drop_caches
    b=$(awk '{print $7}' "/sys/block/$DEV/stat")     # секторів записано
    out=$(./iolat "$DIR/rfile" "$DIR/wfile" "$SECS")
    a=$(awk '{print $7}' "/sys/block/$DEV/stat")
    dev=$(awk -v a="$a" -v b="$b" -v t="$SECS" \
          'BEGIN{printf "%.1f", (a-b)*512/1048576/t}')
    printf '%-12s %s %8s\n' "$s" "$out" "$dev"
done
