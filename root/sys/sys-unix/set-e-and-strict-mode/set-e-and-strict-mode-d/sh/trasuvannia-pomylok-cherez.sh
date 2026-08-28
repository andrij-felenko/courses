# Обробник аварійного збою з виводом стека викликів
on_error() {
    local exit_code="$1"
    local line_no="$2"
    local cmd="${BASH_COMMAND}"

    echo "==========================================================" >&2
    echo "[ПОМИЛКА] Скрипт зазнав аварії з кодом ${exit_code}" >&2
    echo "[ПОМИЛКА] Команда: '${cmd}' на рядку ${line_no}" >&2
    echo "----------------------------------------------------------" >&2
    echo "Стек викликів:" >&2

    local i=0
    while caller "${i}" >/dev/null 2>&1; do
        local frame
        frame="$(caller "${i}")"
        echo "  [${i}] ${frame}" >&2
        (( i++ ))
    done
    echo "==========================================================" >&2
}

trap 'on_error $? $LINENO' ERR
