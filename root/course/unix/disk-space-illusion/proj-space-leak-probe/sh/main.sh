#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="/tmp/bash_disk_experiment"
mkdir -p "$TEST_DIR"

echo "=== 1. Початковий стан ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Запускаємо фоновий процес, який створює файл і утримує його відкритим
python3 -c "
import time, os
f = open('$TEST_DIR/leak.log', 'w')
f.write('X' * (64 * 1024 * 1024))
f.flush()
print('Файл створено. Очікування...')
while True:
    time.sleep(1)
" &
PY_PID=$!
sleep 2

echo "=== 2. Файл створено ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Видаляємо файл із каталогу
rm -f "$TEST_DIR/leak.log"

echo "=== 3. Файл видалено через rm, але процес працює ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

echo "=== 4. Пошук через lsof ==="
lsof +L1 "$TEST_DIR" || true

echo "=== 5. Звільнення місця через /proc ==="
# Знаходимо дескриптор процесу python
FD=$(ls -l /proc/$PY_PID/fd | grep 'leak.log' | awk '{print $9}')
echo "Обнулення /proc/$PY_PID/fd/$FD..."
: > "/proc/$PY_PID/fd/$FD"

echo "=== 6. Стан після обнулення ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Завершуємо процес
kill -9 "$PY_PID"
rm -rf "$TEST_DIR"
