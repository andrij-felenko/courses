# запуск
worker &
echo $! > /run/worker.pid

# зупинка, можливо через години й уже з іншого процесу
pid=$(cat /run/worker.pid)
kill -0 "$pid" 2>/dev/null || exit 0   # «перевірили, що живий»
kill -TERM "$pid"
sleep 5
kill -KILL "$pid" 2>/dev/null          # добиваємо
