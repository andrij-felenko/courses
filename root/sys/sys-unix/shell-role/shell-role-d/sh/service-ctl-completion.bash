# Контекстно-залежне автодоповнення для утиліти service-ctl.
# Встановлення: source цей файл або покласти його в
# /usr/share/bash-completion/completions/service-ctl — тоді його підвантажить
# _completion_loader при першому натисканні Tab після слова service-ctl.

[[ -n "${BASH_VERSION-}" ]] || return 0

# Список служб системи. systemctl може бути відсутній (контейнер, не-systemd),
# тому маємо запасний шлях через /etc/init.d.
_service_ctl_services() {
    local -a units=()

    if command -v systemctl >/dev/null 2>&1; then
        mapfile -t units < <(
            systemctl list-unit-files --type=service --no-legend --no-pager 2>/dev/null |
                awk '{ sub(/\.service$/, "", $1); print $1 }'
        )
    fi
    if [[ ${#units[@]} -eq 0 && -d /etc/init.d ]]; then
        mapfile -t units < <(cd /etc/init.d && compgen -f -- '' 2>/dev/null)
    fi
    (( ${#units[@]} )) && printf '%s\n' "${units[@]}"
}

# Файли *.conf і каталоги; glue дописується перед кожним варіантом, коли
# readline розбив "--config=шлях" і замінювати доведеться саме "=".
_service_ctl_conf_files() {
    local base="$1" glue="$2" item

    COMPREPLY=()
    while IFS= read -r item; do
        [[ -n "$item" ]] && COMPREPLY+=( "${glue}${item}" )
    done < <(
        compgen -f -X '!*.conf' -- "$base"
        compgen -d -S / -- "$base"
    )
}

_service_ctl_complete() {
    local cur prev prev2 subcommands global_flags services

    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    prev2="${COMP_WORDS[COMP_CWORD-2]}"

    subcommands="start stop restart status logs config"
    global_flags="--help --version --verbose --config="

    # Символ '=' входить у типовий COMP_WORDBREAKS, тож "--config=/et"
    # readline подає трьома словами: "--config", "=", "/et".
    if [[ "$prev" == "=" && "$prev2" == "--config" ]]; then
        _service_ctl_conf_files "$cur" ""
        return 0
    fi
    if [[ "$cur" == "=" && "$prev" == "--config" ]]; then
        # Замінюється саме "=", тому кожен варіант несе його на собі.
        _service_ctl_conf_files "" "="
        return 0
    fi
    # Оболонки з ощадливим COMP_WORDBREAKS віддають слово цілим.
    if [[ "$cur" == --config=* ]]; then
        _service_ctl_conf_files "${cur#--config=}" "--config="
        return 0
    fi

    # Перше слово після імені утиліти: підкоманда або глобальний прапорець.
    if [[ $COMP_CWORD -eq 1 ]]; then
        if [[ "$cur" == -* ]]; then
            mapfile -t COMPREPLY < <(compgen -W "$global_flags" -- "$cur")
        else
            mapfile -t COMPREPLY < <(compgen -W "$subcommands" -- "$cur")
        fi
        return 0
    fi

    case "$prev" in
        start|stop|restart|status)
            services="$(_service_ctl_services)"
            mapfile -t COMPREPLY < <(compgen -W "$services" -- "$cur")
            ;;
        logs)
            mapfile -t COMPREPLY < <(compgen -W "-f --lines= --tail" -- "$cur")
            ;;
        config)
            mapfile -t COMPREPLY < <(compgen -W "show edit reload" -- "$cur")
            ;;
        -f|--tail)
            services="$(_service_ctl_services)"
            mapfile -t COMPREPLY < <(compgen -W "$services" -- "$cur")
            ;;
        *)
            if [[ "$cur" == -* ]]; then
                mapfile -t COMPREPLY < <(compgen -W "$global_flags" -- "$cur")
            else
                COMPREPLY=()
            fi
            ;;
    esac
    return 0
}

# -o default: за порожнього COMPREPLY readline доповнює імена файлів;
# -o nospace: не дописувати пробіл після "--config=" і після каталогів.
complete -F _service_ctl_complete -o default -o nospace service-ctl
