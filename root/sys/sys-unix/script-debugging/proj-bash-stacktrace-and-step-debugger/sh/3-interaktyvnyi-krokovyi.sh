#!/usr/bin/env bash
# ==============================================================================
# lib_debugger.bash — інтерактивний кроковий відлагоджувач для Bash
# ==============================================================================

# Вмикаємо функціональне трасування та розширений режим відлагодження
set -T
shopt -s extdebug

# Глобальний стан відлагоджувача
__DBG_STEPPING=1          # 1 = режим покрокового виконання, 0 = режим continue
__DBG_BREAKPOINTS=()      # Масив точок зупинки: "file.sh:line" або "func_name"

debugger_add_breakpoint() {
    __DBG_BREAKPOINTS+=("$1")
}

__debugger_prompt() {
    # Зберігаємо статус повернення попередньої інструкції
    local last_status="$?"
    local current_cmd="${BASH_COMMAND}"
    local current_line="${BASH_LINENO[0]}"
    local current_file="${BASH_SOURCE[1]}"
    local current_func="${FUNCNAME[1]:-main}"

    # Перевіряємо умови зупинки: покроковий режим або спрацьовування точки зупинки
    local should_break="${__DBG_STEPPING}"

    if [[ "${should_break}" -eq 0 ]]; then
        for bp in "${__DBG_BREAKPOINTS[@]}"; do
            if [[ "${bp}" == "${current_func}" || \
                  "${bp}" == "${current_file}:${current_line}" || \
                  "${bp}" == "${current_line}" ]]; then
                should_break=1
                echo -e "\n\033[1;32m[BP]\033[0m Зупинка на точці: ${bp}" >&2
                break
            fi
        done
    fi

    # Якщо умов для зупинки немає — негайно повертаємо управління
    if [[ "${should_break}" -eq 0 ]]; then
        return 0
    fi

    # Перевіряємо доступність термінала для інтерактивного сеансу
    if [[ ! -r /dev/tty || ! -w /dev/tty ]]; then
        return 0
    fi

    # Відкриваємо дескриптори 3 і 4 для прямого зв'язку з терміналом
    exec 3< /dev/tty 4> /dev/tty

    echo -e "\n\033[1;34m[DEBUG]\033[0m ${current_file}:${current_line} (${current_func}) -> \033[1;33m${current_cmd}\033[0m" >&4

    while true; do
        printf "\033[1;36mdbg>\033[0m " >&4
        local user_input=""
        if ! read -r -u 3 user_input; then
            echo "Сеанс відлагодження завершено." >&4
            break
        fi

        local cmd_name="${user_input%% *}"
        local cmd_args="${user_input#* }"
        [[ "${cmd_name}" == "${cmd_args}" ]] && cmd_args=""

        case "${cmd_name}" in
            s|step|"")
                # Крок до наступної команди
                __DBG_STEPPING=1
                break
                ;;
            c|cont|continue)
                # Продовження виконання до наступної точки зупинки
                __DBG_STEPPING=0
                break
                ;;
            p|print)
                # Вивід значення вказаної змінної
                if [[ -z "${cmd_args}" ]]; then
                    echo "Використання: p <ім'я_змінної>" >&4
                else
                    eval "echo \"${cmd_args} = \${${cmd_args}}\"" >&4 2>&1
                fi
                ;;
            e|eval)
                # Виконання довільної команди або виразу в поточному контексті
                if [[ -z "${cmd_args}" ]]; then
                    echo "Використання: e <команда_або_вираз>" >&4
                else
                    eval "${cmd_args}" >&4 2>&1
                fi
                ;;
            w|where|bt)
                # Друк поточного стека викликів
                echo "Стек викликів:" >&4
                for (( j=1; j<${#FUNCNAME[@]}; j++ )); do
                    printf "  #%-2d %s() у %s:%d\n" \
                        "$((j-1))" "${FUNCNAME[$j]}" "${BASH_SOURCE[$j]}" "${BASH_LINENO[$((j-1))]}" >&4
                done
                ;;
            b|break)
                # Динамічне додавання точки зупинки
                if [[ -n "${cmd_args}" ]]; then
                    debugger_add_breakpoint "${cmd_args}"
                    echo "Точку зупинки зареєстровано: ${cmd_args}" >&4
                else
                    echo "Список активних точок: ${__DBG_BREAKPOINTS[*]}" >&4
                fi
                ;;
            h|help)
                echo "Команди інтерактивного відлагоджувача:" >&4
                echo "  s, step      - виконати наступну інструкцію (клавіша Enter)" >&4
                echo "  c, cont      - продовжити виконання до наступної точки зупинки" >&4
                echo "  p <var>      - надрукувати значення змінної" >&4
                echo "  e <expr>     - обчислити довільний вираз у поточному контексті" >&4
                echo "  b <target>   - встановити точку зупинки (назва функції або рядок)" >&4
                echo "  w, bt        - вивести поточний стек викликів (backtrace)" >&4
                echo "  q, quit      - аварійно зупинити виконання процесу" >&4
                ;;
            q|quit)
                echo "Примусове аварійне завершення сценарію." >&4
                exec 3<&- 4>&-
                exit 130
                ;;
            *)
                echo "Невідома команда '${cmd_name}'. Введіть 'h' для перегляду довідки." >&4
                ;;
        esac
    done

    # Закриваємо виділені файлові дескриптори термінала
    exec 3<&- 4>&-

    # Відновлюємо код завершення попередньої команди
    return "${last_status}"
}

# Реєструємо перехоплення події DEBUG
trap '__debugger_prompt' DEBUG
