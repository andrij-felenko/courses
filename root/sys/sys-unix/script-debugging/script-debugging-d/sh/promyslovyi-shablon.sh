#!/usr/bin/env bash
# ==============================================================================
# Промисловий шаблон системного сценарію з повною діагностикою
# ==============================================================================
set -Eeuo pipefail
shopt -s inherit_errexit 2>/dev/null || true

# 1. Налаштування детального префіксу трасування
export PS4='+ [${EPOCHREALTIME:-0}] [pid:${BASHPID}] [${BASH_SOURCE[0]##*/}:${LINENO}] ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'

# 2. Обробник аварійного стек-трейсу
__emergency_backtrace() {
    local err_code="$1"
    local cmd="$2"
    local line="$3"
    local src="$4"
    trap '' ERR

    echo -e "\n\033[1;31m[CRITICAL FAILURE]\033[0m Сценарій завершився з кодом ${err_code}" >&2
    echo "  Невдала інструкція: '${cmd}'" >&2
    echo "  Файл та рядок:      ${src}:${line}" >&2
    echo "  Стек викликів:" >&2

    local depth=${#FUNCNAME[@]}
    for (( i=1; i<depth; i++ )); do
        echo "    #$((i-1)) ${FUNCNAME[$i]}() у ${BASH_SOURCE[$i]}:${BASH_LINENO[$((i-1))]}" >&2
    done
    exit "${err_code}"
}

# 3. Реєстрація пастки
trap '__emergency_backtrace "$?" "${BASH_COMMAND}" "${LINENO}" "${BASH_SOURCE[0]}"' ERR

# 4. Основна логіка сценарію
main() {
    local target_env="${1:-production}"
    echo "Запуск сценарію для середовища: ${target_env}"
    # Бізнес-логіка...
}

main "$@"
