#!/usr/bin/env bash
set -Eeuo pipefail

on_error_backtrace() {
    local exit_code="$1"
    local failed_cmd="$2"
    local failed_line="$3"
    local failed_file="$4"

    # Вимикаємо ERR-пастку для запобігання рекурсивним збоям усередині обробника
    trap '' ERR

    echo -e "\n[АВАРІЙНИЙ СТЕК-ТРЕЙС] Код помилки: ${exit_code}" >&2
    echo "  Збій команди: '${failed_cmd}'" >&2
    echo "  Локація:      ${failed_file}:${failed_line}" >&2
    echo "  Стек викликів:" >&2

    local depth=${#FUNCNAME[@]}
    for (( i=1; i<depth; i++ )); do
        local fn="${FUNCNAME[$i]}"
        local file="${BASH_SOURCE[$i]}"
        local line="${BASH_LINENO[$((i-1))]}"
        echo "    #$((i-1)) ${fn}() у ${file}:${line}" >&2
    done
    exit "${exit_code}"
}

trap 'on_error_backtrace "$?" "${BASH_COMMAND}" "${LINENO}" "${BASH_SOURCE[0]}"' ERR
