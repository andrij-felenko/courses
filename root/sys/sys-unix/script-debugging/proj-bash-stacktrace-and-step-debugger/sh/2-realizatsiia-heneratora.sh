#!/usr/bin/env bash
# ==============================================================================
# lib_stacktrace.bash — модуль автоматичної генерації стек-трейсу при збоях
# ==============================================================================

# Забезпечуємо наскрізне наслідування пасток функціями та підоболонками
set -E
set -o pipefail

__stacktrace_handler() {
    # 1. Фіксуємо статус виходу та параметри аварійної інструкції
    local exit_code="$1"
    local failed_command="$2"
    local trigger_line="$3"
    local trigger_source="$4"

    # Запобігаємо повторному входженню в обробник при помилках форматування
    trap '' ERR

    local red="\033[1;31m"
    local yellow="\033[1;33m"
    local cyan="\033[1;36m"
    local dim="\033[2m"
    local reset="\033[0m"

    # Вимикаємо ANSI-послідовності кольорів, якщо stderr перенаправлено у файл
    if [[ ! -t 2 ]]; then
        red="" yellow="" cyan="" dim="" reset=""
    fi

    echo -e "\n${red}════════════════════════════════════════════════════════════════════════════${reset}" >&2
    echo -e "${red}  ПОМИЛКА ВИКОНАННЯ СЦЕНАРІЮ (EXIT CODE: ${exit_code})${reset}" >&2
    echo -e "${red}════════════════════════════════════════════════════════════════════════════${reset}" >&2
    echo -e "  ${yellow}Команда:${reset}   ${failed_command}" >&2
    echo -e "  ${yellow}Місце:${reset}     ${trigger_source}:${trigger_line}" >&2
    echo -e "  ${yellow}PID:${reset}       ${BASHPID} (батьківський процес: ${PPID})" >&2

    # 2. Вивід контекстного фрагмента вихідного коду навколо точки падіння
    if [[ -f "${trigger_source}" && -r "${trigger_source}" ]]; then
        echo -e "\n  ${cyan}Контекст вихідного коду:${reset}" >&2
        local start_line=$(( trigger_line > 2 ? trigger_line - 2 : 1 ))
        local end_line=$(( trigger_line + 2 ))
        local current_l=0

        while IFS= read -r line || [[ -n "${line}" ]]; do
            (( current_l++ ))
            if (( current_l >= start_line && current_l <= end_line )); then
                if (( current_l == trigger_line )); then
                    printf "  ${red}► %4d | %s${reset}\n" "${current_l}" "${line}" >&2
                else
                    printf "    ${dim}%4d | %s${reset}\n" "${current_l}" "${line}" >&2
                fi
            fi
        done < "${trigger_source}"
    fi

    # 3. Реконструкція ієрархії викликів функцій
    local stack_depth=${#FUNCNAME[@]}
    echo -e "\n  ${cyan}Стек викликів (Call Stack):${reset}" >&2

    # Починаємо з індексу 1, оскільки індекс 0 відповідає самому обробнику
    for (( i=1; i<stack_depth; i++ )); do
        local func="${FUNCNAME[$i]}"
        local file="${BASH_SOURCE[$i]:-unknown}"
        local line="${BASH_LINENO[$((i-1))]:-0}"

        if [[ "${func}" == "main" && "${i}" -eq $((stack_depth - 1)) ]]; then
            func="<корінь сценарію>"
        fi

        printf "    ${yellow}#%-2d${reset} %s() у ${dim}%s:%d${reset}\n" \
            "$((i-1))" "${func}" "${file}" "${line}" >&2
    done

    echo -e "${red}════════════════════════════════════════════════════════════════════════════\n${reset}" >&2

    # Завершуємо роботу процесу з оригінальним кодом помилки
    exit "${exit_code}"
}

# Реєструємо обробник для сигналу ERR з передачею повного набору змінних стану
trap '__stacktrace_handler "$?" "${BASH_COMMAND}" "${LINENO}" "${BASH_SOURCE[0]}"' ERR
