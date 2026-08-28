#!/usr/bin/env bash
set -euo pipefail

PROGNAME="${0##*/}"
OUTPUT_FILE=""
FORCE=0

while [ $# -gt 0 ]; do
    case "$1" in
        --help)
            printf "Використання: %s [ОПЦІЇ] [ФАЙЛ ...]\n" "$PROGNAME"
            exit 0
            ;;
        --output=*)
            OUTPUT_FILE="${1#*=}"
            shift
            ;;
        --output)
            [[ $# -ge 2 ]] || { printf "Помилка: --output вимагає аргументу\n" >&2; exit 2; }
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --)
            shift
            break
            ;;
        --*)
            printf "Помилка: невідома довга опція '%s'\n" "$1" >&2
            exit 2
            ;;
        -*)
            # Обробка коротких прапорців через getopts
            OPTIND=1
            while getopts ":hfo:v" opt "$1"; do
                case "$opt" in
                    h) printf "Довідка %s\n" "$PROGNAME"; exit 0 ;;
                    f) FORCE=1 ;;
                    o) 
                        if [[ -n "$OPTARG" ]]; then
                            OUTPUT_FILE="$OPTARG"
                        fi
                        ;;
                    :)
                        # Якщо аргумент йде наступним словом у командному рядку
                        [[ $# -ge 2 ]] || { printf "Помилка: -o вимагає аргументу\n" >&2; exit 2; }
                        OUTPUT_FILE="$2"
                        shift
                        ;;
                    \?) printf "Помилка: невідомий прапорець '-%s'\n" "$OPTARG" >&2; exit 2 ;;
                esac
            done
            shift
            ;;
        *)
            break
            ;;
    esac
done
