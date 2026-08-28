#!/usr/bin/env bash
set -euo pipefail

# 1. Створення ресурсів
WORK_DIR=$(mktemp -d)

# 2. Функція очищення прив'язується ВИКЛЮЧНО до псевдосигналу EXIT
cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

# 3. Обробники сигналів: скидають пастку та відправляють сигнал собі
trap 'trap - INT; kill -s INT "$$"' INT
trap 'trap - TERM; kill -s TERM "$$"' TERM
trap 'trap - HUP; kill -s HUP "$$"' HUP
