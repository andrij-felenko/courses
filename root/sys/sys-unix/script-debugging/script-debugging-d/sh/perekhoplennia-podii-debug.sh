#!/usr/bin/env bash
set -T

# Простий лічильник команд та протоколювання інструкцій
__trace_instruction() {
    local cmd="${BASH_COMMAND}"
    local line="${BASH_LINENO[0]}"
    local src="${BASH_SOURCE[1]}"
    echo ">> [DEBUG] Виконується: '${cmd}' на рядку ${src}:${line}" >&2
}

trap '__trace_instruction' DEBUG

x=10
y=20
z=$(( x + y ))
