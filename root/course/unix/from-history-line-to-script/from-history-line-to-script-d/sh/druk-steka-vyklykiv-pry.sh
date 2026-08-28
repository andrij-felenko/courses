set -E # Дозволяє функціям успадковувати trap ERR

print_stacktrace() {
    local exit_code=$?
    printf '[FATAL] Скрипт впав на рядку %s із кодом %s\n' "${1}" "${exit_code}" >&2
    printf 'Стек викликів:\n' >&2
    local frame=0
    while caller ${frame}; do
        ((frame++))
    done >&2
}

trap 'print_stacktrace ${LINENO}' ERR
