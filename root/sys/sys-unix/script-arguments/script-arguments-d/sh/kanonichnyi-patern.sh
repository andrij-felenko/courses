#!/bin/sh
set -eu

OUTPUT_PATH=""
DRY_RUN=0

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            printf "Використання: %s [ОПЦІЇ] [ФАЙЛИ...]\n" "$0"
            exit 0
            ;;
        -n|--dry-run)
            DRY_RUN=1
            shift
            ;;
        -o|--output)
            # Обробка формату з роздільним значенням: --output /tmp/file
            if [ $# -lt 2 ]; then
                printf "Помилка: опція '%s' вимагає аргументу.\n" "$1" >&2
                exit 1
            fi
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --output=*)
            # Обробка формату зі знаком рівності: --output=/tmp/file
            OUTPUT_PATH="${1#*=}"
            shift
            ;;
        --)
            # Явний маркер кінця опцій
            shift
            break
            ;;
        -*)
            printf "Помилка: невідома опція '%s'\n" "$1" >&2
            exit 1
            ;;
        *)
            # Перший не-опціональний аргумент
            break
            ;;
    esac
done

# Усі залишки в "$@" тепер є суто позиційними операндами
