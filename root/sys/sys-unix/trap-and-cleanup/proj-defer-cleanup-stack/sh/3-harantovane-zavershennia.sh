defer_spawn() {
    local pid_var="$1"
    shift
    
    "$@" &
    local spawned_pid=$!
    
    # Реєстрація зупинки процесу та очікування вивільнення ресурсів
    defer "kill -TERM ${spawned_pid} 2>/dev/null && wait ${spawned_pid} 2>/dev/null || true"
    
    printf -v "${pid_var}" "%s" "${spawned_pid}"
}
