#!/usr/bin/env bash
# Розбір INI та key-value без eval і без підпроцесів.
# Заповнює асоціативний масив CONFIG_MAP ключами вигляду "секція.ключ".
#
# Обрізання пробілів робиться ПОРТАТИВНОЮ ідіомою подвійної підстановки:
#   ${line%%[![:space:]]*}  -> самі провідні пробіли рядка
#   ${line#"$те_саме"}      -> рядок без них
# extglob для неї не потрібен, тож модуль працює і в оболонках без розширень.

# Обрізає пробіли з обох боків і КЛАДЕ результат у змінну з назвою $1.
# printf -v замість $(...) — жодного форку на кожен рядок конфігурації.
ini_trim_var() {
    local __inicfg_out=$1
    local __inicfg_value=$2
    __inicfg_value=${__inicfg_value#"${__inicfg_value%%[![:space:]]*}"}
    __inicfg_value=${__inicfg_value%"${__inicfg_value##*[![:space:]]}"}
    printf -v "$__inicfg_out" '%s' "$__inicfg_value"
}

# 0 — файл розібрано без зауважень, 1 — файл недоступний або є биті рядки.
parse_ini_configuration() {
    local config_file=$1

    if [[ ! -f $config_file || ! -r $config_file ]]; then
        printf 'ini: файл не знайдено або не читається: %s\n' "$config_file" >&2
        return 1
    fi

    declare -g -A CONFIG_MAP=()

    local current_section="global"
    local line_num=0
    local bad_lines=0
    local line sec key val

    # Читання БЕЗ subshell: перенаправлення стоїть на самому while.
    # Конвеєр `cat file | while ...` виконував би тіло в дочірньому процесі,
    # і заповнений там CONFIG_MAP помер би разом з ним.
    # `|| [[ -n $line ]]` дочитує останній рядок без завершального переводу.
    while IFS= read -r line || [[ -n $line ]]; do
        line_num=$(( line_num + 1 ))

        ini_trim_var line "$line"

        # Порожні рядки й коментарі (# та ;)
        if [[ -z $line || $line == [#\;]* ]]; then
            continue
        fi

        # Заголовок секції [name]
        if [[ $line == \[*\] ]]; then
            sec=${line#\[}
            sec=${sec%\]}
            ini_trim_var sec "$sec"
            if [[ -z $sec ]]; then
                printf 'ini: %s:%d: порожня назва секції\n' "$config_file" "$line_num" >&2
                bad_lines=$(( bad_lines + 1 ))
                continue
            fi
            current_section=$sec
            continue
        fi

        # Пара ключ-значення за ПЕРШИМ роздільником "=" або ":".
        # %% бере найдовший суфікс -> лишає ключ; #* бере найкоротший
        # префікс -> лишає значення разом з усіма роздільниками всередині.
        if [[ $line == *[=:]* ]]; then
            key=${line%%[=:]*}
            val=${line#*[=:]}

            ini_trim_var key "$key"
            ini_trim_var val "$val"

            if [[ -z $key ]]; then
                printf 'ini: %s:%d: порожній ключ\n' "$config_file" "$line_num" >&2
                bad_lines=$(( bad_lines + 1 ))
                continue
            fi

            # Знімаємо РІВНО одну пару обрамляючих лапок. Усередині нічого
            # не розгортається: значення лишається даними, а не кодом.
            if (( ${#val} >= 2 )); then
                if [[ $val == \"*\" ]]; then
                    val=${val#\"}
                    val=${val%\"}
                elif [[ $val == \'*\' ]]; then
                    val=${val#\'}
                    val=${val%\'}
                fi
            fi

            CONFIG_MAP["${current_section}.${key}"]=$val
        else
            printf 'ini: %s:%d: рядок без роздільника: %s\n' \
                "$config_file" "$line_num" "$line" >&2
            bad_lines=$(( bad_lines + 1 ))
        fi
    done < "$config_file"

    (( bad_lines == 0 ))
}

# Каскад пріоритетів: конфігурація -> оточення -> дефолт.
# "server.port" шукається в оточенні як SERVER_PORT.
get_config() {
    local __inicfg_key=$1
    local __inicfg_default=$2
    local __inicfg_env

    __inicfg_env=${__inicfg_key//[.-]/_}
    __inicfg_env=${__inicfg_env^^}

    # ${arr[k]+set} безпечне навіть тоді, коли масиву ще немає:
    # форма з "+" ніколи не спричиняє unbound variable під set -u.
    if [[ -n ${CONFIG_MAP[$__inicfg_key]+set} ]]; then
        printf '%s' "${CONFIG_MAP[$__inicfg_key]}"
    elif [[ -n ${!__inicfg_env-} ]]; then
        printf '%s' "${!__inicfg_env}"
    else
        printf '%s' "$__inicfg_default"
    fi
}
