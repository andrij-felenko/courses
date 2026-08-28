#!/usr/bin/env bash
# test_app.sh — тестовий додаток з підключенням діагностичних модулів

# Підключаємо генератор бектрейсу
source "./lib_stacktrace.bash"

# Підключаємо кроковий відлагоджувач за потреби
# source "./lib_debugger.bash"
# debugger_add_breakpoint "fetch_remote_resource"

fetch_remote_resource() {
    local endpoint="$1"
    local timeout_sec="$2"

    echo "Підключення до ${endpoint} (таймаут ${timeout_sec}с)..."
    
    # Симулюємо помилку виконання команди
    ls "/неіснуючий/системний/шлях/до/ресурсу"
}

sync_pipeline() {
    local target_host="api.internal.service"
    local retries=3

    echo "Підготовка конвеєра синхронізації для ${target_host}..."
    fetch_remote_resource "${target_host}" 10
}

main() {
    echo "Запуск сервісу обробки..."
    sync_pipeline
    echo "Синхронізацію успішно завершено."
}

main "$@"
