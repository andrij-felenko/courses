# Запуск фонового процесу зі збереженням PID
start_background_collector() {
    python3 -u metric_daemon.py &
    DAEMON_PID=$!
}

cleanup_processes() {
    if [[ -n "${DAEMON_PID:-}" ]] && kill -0 "${DAEMON_PID}" 2>/dev/null; then
        # Спочатку ввічливий запит на коректне завершення
        kill -TERM "${DAEMON_PID}" 2>/dev/null || true
        # Очікування завершення протягом 2 секунд
        local count=0
        while kill -0 "${DAEMON_PID}" 2>/dev/null && (( count < 20 )); do
            sleep 0.1
            (( count++ ))
        done
        # Якщо процес завис — примусове знищення
        kill -KILL "${DAEMON_PID}" 2>/dev/null || true
        wait "${DAEMON_PID}" 2>/dev/null || true
    fi
}
