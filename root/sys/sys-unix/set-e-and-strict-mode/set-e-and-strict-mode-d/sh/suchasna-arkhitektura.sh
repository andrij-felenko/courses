#!/usr/bin/env bash
# ==============================================================================
# Сучасна преамбула надійного виробничого сценарію
# ==============================================================================
set -euo pipefail
set -E                               # Успадкування trap ERR функціями та subshells
shopt -s inherit_errexit 2>/dev/null || true  # Успадкування errexit у $(...)

# 1. Реєстрація гарантованого прибирання ресурсів
TEMP_DIR=""

cleanup() {
    local exit_code=$?
    set +e  # Вимикаємо errexit, щоб помилки видалення не блокували вихід
    if [[ -n "${TEMP_DIR:-}" && -d "${TEMP_DIR}" ]]; then
        rm -rf "${TEMP_DIR}"
    fi
    exit "${exit_code}"
}

trap cleanup EXIT
trap 'exit 130' INT   # Коректне завершення по Ctrl+C
trap 'exit 143' TERM  # Коректне завершення по kill/systemd
