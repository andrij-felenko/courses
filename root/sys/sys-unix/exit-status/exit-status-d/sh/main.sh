#!/usr/bin/env bash
set -euo pipefail

TMPFILE=$(mktemp)

# Зареєструвати обробник видалення тимчасового файлу при виході з процесів
trap 'rm -f "$TMPFILE"' EXIT
trap 'echo "Аварійне зупинення через помилку на рядку $LINENO!"' ERR

# Основна логіка
echo "Обробка даних..." > "$TMPFILE"
