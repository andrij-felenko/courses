#!/usr/bin/env bash
# Розбір аргументів командного рядка без getopt і без жодного підпроцесу:
# усе роблять зрізи ${arg:0:1} та обрізання ${arg#*=}.
#
# Підтримано: --key=value, --key value, короткі -v, склеєні пакети -vdp8080,
# значення впритул до короткого ключа (-p8080, -c/etc/app.ini), термінатор --
# і позиційні аргументи.
#
# Результат — глобальні CLI_*. Прапорець -g обов'язковий: `declare` усередині
# функції створює ЛОКАЛЬНУ змінну, і масив результату помер би разом з нею.

cli_usage() {
    printf '%s\n' \
        "Використання: prog [опції] [--] [аргументи]" \
        "  --host=ХОСТ | --host ХОСТ    адреса прослуховування (типово 127.0.0.1)" \
        "  --port=N | --port N | -pN    порт 1..65535 (типово 8080)" \
        "  --config=ФАЙЛ | -cФАЙЛ       шлях до конфігурації" \
        "  --verbose | -v               збільшити докладність (можна кілька разів)" \
        "  --dry-run | -d               нічого не виконувати" \
        "  --help | -h                  ця довідка"
}

# Валідація порту без regex і без зовнішніх утиліт:
# ${value//[0-9]/} лишає рівно ті символи, що цифрами НЕ є.
cli_is_valid_port() {
    local value=$1
    local digits

    [[ -n $value ]] || return 1
    [[ -z ${value//[0-9]/} ]] || return 1
    (( ${#value} <= 5 )) || return 1   # довше не влізе в 65535, а в арифметиці переповниться

    # Провідні нулі знімаємо самою підстановкою: інакше (( 0080 )) впаде
    # з "value too great for base" — вісімкове число з вісімкою всередині.
    digits=${value#"${value%%[!0]*}"}
    [[ -n $digits ]] || return 1       # "000" -> порожньо -> порт 0 невалідний

    (( digits >= 1 && digits <= 65535 ))
}

# 0 — розібрано, 1 — помилка в аргументах, 2 — попросили довідку.
parse_cli_arguments() {
    declare -g CLI_HOST="127.0.0.1"
    declare -g CLI_PORT=8080
    declare -g CLI_VERBOSE=0
    declare -g CLI_DRY_RUN=0
    declare -g CLI_CONFIG_FILE=""
    declare -g -a CLI_POSITIONAL=()

    local arg opt flags raw

    while (( $# > 0 )); do
        arg=$1
        shift

        case $arg in
            --)
                # Після термінатора все є позиційним, навіть якщо схоже на опцію.
                CLI_POSITIONAL+=("$@")
                break
                ;;

            --help)
                cli_usage
                return 2
                ;;

            # Довгі опції з роздільником "=" — значення після ПЕРШОГО знака рівності.
            --host=*)
                CLI_HOST=${arg#*=}
                if [[ -z $CLI_HOST ]]; then
                    printf 'cli: порожнє значення --host\n' >&2
                    return 1
                fi
                ;;
            --port=*)
                raw=${arg#*=}
                if ! cli_is_valid_port "$raw"; then
                    printf 'cli: невалідний порт: %s\n' "$raw" >&2
                    return 1
                fi
                CLI_PORT=$raw
                ;;
            --config=*)
                CLI_CONFIG_FILE=${arg#*=}
                if [[ -z $CLI_CONFIG_FILE ]]; then
                    printf 'cli: порожнє значення --config\n' >&2
                    return 1
                fi
                ;;

            # Довгі опції з окремим значенням.
            --host)
                if (( $# == 0 )); then
                    printf 'cli: опція --host вимагає значення\n' >&2
                    return 1
                fi
                CLI_HOST=$1
                shift
                ;;
            --port)
                if (( $# == 0 )); then
                    printf 'cli: опція --port вимагає значення\n' >&2
                    return 1
                fi
                raw=$1
                shift
                if ! cli_is_valid_port "$raw"; then
                    printf 'cli: невалідний порт: %s\n' "$raw" >&2
                    return 1
                fi
                CLI_PORT=$raw
                ;;
            --config)
                if (( $# == 0 )); then
                    printf 'cli: опція --config вимагає значення\n' >&2
                    return 1
                fi
                CLI_CONFIG_FILE=$1
                shift
                ;;

            --verbose)
                # Свідомо не ((CLI_VERBOSE++)): постінкремент від нуля повертає
                # код 1, і під set -e така "успішна" команда вбила б сценарій.
                CLI_VERBOSE=$(( CLI_VERBOSE + 1 ))
                ;;
            --dry-run)
                CLI_DRY_RUN=1
                ;;

            --*)
                printf 'cli: невідома опція: %s\n' "$arg" >&2
                return 1
                ;;

            # Пакет коротких прапорців: -v, -vd, -vdp8080, -c/etc/app.ini
            -[!-]*)
                flags=${arg#-}
                while [[ -n $flags ]]; do
                    opt=${flags:0:1}     # перший символ пакета
                    flags=${flags:1}     # решта пакета

                    case $opt in
                        v)
                            CLI_VERBOSE=$(( CLI_VERBOSE + 1 ))
                            ;;
                        d)
                            CLI_DRY_RUN=1
                            ;;
                        h)
                            cli_usage
                            return 2
                            ;;
                        p)
                            # Хвіст пакета після 'p' — це значення (-p8080),
                            # а якщо хвіст порожній, значення в наступному слові.
                            if [[ -n $flags ]]; then
                                raw=$flags
                                flags=""
                            else
                                if (( $# == 0 )); then
                                    printf 'cli: опція -p вимагає порт\n' >&2
                                    return 1
                                fi
                                raw=$1
                                shift
                            fi
                            if ! cli_is_valid_port "$raw"; then
                                printf 'cli: невалідний порт: %s\n' "$raw" >&2
                                return 1
                            fi
                            CLI_PORT=$raw
                            ;;
                        c)
                            if [[ -n $flags ]]; then
                                CLI_CONFIG_FILE=$flags
                                flags=""
                            else
                                if (( $# == 0 )); then
                                    printf 'cli: опція -c вимагає файл\n' >&2
                                    return 1
                                fi
                                CLI_CONFIG_FILE=$1
                                shift
                            fi
                            ;;
                        *)
                            printf 'cli: невідомий короткий прапорець: -%s\n' "$opt" >&2
                            return 1
                            ;;
                    esac
                done
                ;;

            # Самотній "-" — це домовленість про stdin, а не опція.
            *)
                CLI_POSITIONAL+=("$arg")
                ;;
        esac
    done

    return 0
}
