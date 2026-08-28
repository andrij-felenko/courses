#!/usr/bin/env bash
# /usr/share/bash-completion/completions/clusterctl
# Сценарій автодоповнення для утиліти clusterctl

_clusterctl_get_nodes() {
    # Кешування списку вузлів на 30 секунд для усунення мережевих затримок
    local cache_file="/tmp/.clusterctl_nodes_cache_${UID}"
    local now
    now=$(date +%s)

    if [[ -f "$cache_file" ]]; then
        local mtime
        mtime=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if (( now - mtime < 30 )); then
            cat "$cache_file"
            return 0
        fi
    fi

    # Якщо кеш застарів або відсутній, виконуємо швидкий системний запит
    local nodes
    if nodes=$(clusterctl nodes list --format=names 2>/dev/null); then
        echo "$nodes" > "$cache_file"
        echo "$nodes"
    fi
}

_clusterctl_get_services() {
    local cache_file="/tmp/.clusterctl_services_cache_${UID}"
    local now
    now=$(date +%s)

    if [[ -f "$cache_file" ]]; then
        local mtime
        mtime=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if (( now - mtime < 30 )); then
            cat "$cache_file"
            return 0
        fi
    fi

    local svrs
    if svrs=$(clusterctl service list --format=names 2>/dev/null); then
        echo "$svrs" > "$cache_file"
        echo "$svrs"
    fi
}

_clusterctl() {
    local cur prev words cword
    # Ініціалізація стандартизованого контексту з усуненням розриву по '=' та ':'
    if declare -F _init_completion >/dev/null 2>&1; then
        _init_completion -n "=:" || return
    else
        # Резервна ініціалізація для чистих середовищ без bash-completion
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        words=("${COMP_WORDS[@]}")
        cword=$COMP_CWORD
    fi

    local global_opts="--kubeconfig= --verbose --help -v -h"
    local top_commands="nodes service help"

    # Обробка аргументів, якщо поточне слово починається зі знака рівності
    if [[ "$cur" == --kubeconfig=* ]]; then
        local file_prefix="${cur#--kubeconfig=}"
        compopt -o filenames -o nospace
        COMPREPLY=( $(compgen -f -- "$file_prefix") )
        return 0
    fi

    if [[ "$cur" == --format=* ]]; then
        local format_val="${cur#--format=}"
        COMPREPLY=( $(compgen -W "table json yaml names" -- "$format_val") )
        return 0
    fi

    if [[ "$cur" == --status=* ]]; then
        local status_val="${cur#--status=}"
        COMPREPLY=( $(compgen -W "ready notready" -- "$status_val") )
        return 0
    fi

    if [[ "$cur" == --env=* ]]; then
        local env_val="${cur#--env=}"
        COMPREPLY=( $(compgen -W "prod stage dev" -- "$env_val") )
        return 0
    fi

    # Визначення позиції головної команди та підкоманди
    local cmd=""
    local subcmd=""
    local i

    for (( i=1; i < cword; i++ )); do
        local w="${words[i]}"
        # Пропускаємо глобальні опції та їхні значення
        if [[ "$w" == --kubeconfig=* || "$w" == -v || "$w" == --verbose || "$w" == -h || "$w" == --help ]]; then
            continue
        fi
        if [[ "$w" == --kubeconfig ]]; then
            (( i++ )) # Пропускаємо наступний аргумент як значення опції
            continue
        fi

        if [[ -z "$cmd" ]]; then
            cmd="$w"
        elif [[ -z "$subcmd" ]]; then
            subcmd="$w"
            break
        fi
    done

    # 1. Рівень кореня: доповнення команд першого рівня та глобальних опцій
    if [[ -z "$cmd" ]]; then
        if [[ "$cur" == -* ]]; then
            COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
            [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
        else
            COMPREPLY=( $(compgen -W "$top_commands" -- "$cur") )
        fi
        return 0
    fi

    # 2. Рівень підкоманд: розгалуження за головною командою
    case "$cmd" in
        nodes)
            if [[ -z "$subcmd" ]]; then
                local node_subcmds="list drain"
                if [[ "$cur" == -* ]]; then
                    COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
                else
                    COMPREPLY=( $(compgen -W "$node_subcmds" -- "$cur") )
                fi
                return 0
            fi

            case "$subcmd" in
                list)
                    local list_opts="--format= --status="
                    COMPREPLY=( $(compgen -W "$list_opts" -- "$cur") )
                    [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    ;;
                drain)
                    if [[ "$cur" == -* ]]; then
                        local drain_opts="--force --timeout="
                        COMPREPLY=( $(compgen -W "$drain_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        # Доповнення імені вузла
                        local nodes
                        nodes=$(_clusterctl_get_nodes)
                        COMPREPLY=( $(compgen -W "$nodes" -- "$cur") )
                    fi
                    ;;
            esac
            ;;

        service)
            if [[ -z "$subcmd" ]]; then
                local srv_subcmds="deploy logs restart"
                if [[ "$cur" == -* ]]; then
                    COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
                else
                    COMPREPLY=( $(compgen -W "$srv_subcmds" -- "$cur") )
                fi
                return 0
            fi

            case "$subcmd" in
                deploy)
                    if [[ "$cur" == -* ]]; then
                        local deploy_opts="--env= --tag="
                        COMPREPLY=( $(compgen -W "$deploy_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        # Перший позиційний аргумент після deploy — ім'я сервісу
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
                logs)
                    if [[ "$cur" == -* ]]; then
                        local logs_opts="-f --tail="
                        COMPREPLY=( $(compgen -W "$logs_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
                restart)
                    if [[ "$cur" == -* ]]; then
                        local restart_opts="--grace-period="
                        COMPREPLY=( $(compgen -W "$restart_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
            esac
            ;;

        help)
            COMPREPLY=( $(compgen -W "$top_commands" -- "$cur") )
            ;;
    esac
}

# Реєстрація точки входу комплішена
complete -F _clusterctl clusterctl
