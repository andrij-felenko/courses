# Запускаємо безперервний запис у файл у фоні
python3 -c '
import time, os
with open("/tmp/critical_service.data", "w") as f:
    i = 0
    while True:
        f.write(f"Record {i}: {time.ctime()}\n")
        f.flush()
        time.sleep(1)
        i += 1
' &
PID=$!
echo "Запущено тестовий процес із PID: $PID"
