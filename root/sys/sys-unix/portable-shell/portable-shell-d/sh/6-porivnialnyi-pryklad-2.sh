#!/bin/sh
# Гарантовано переносний варіант: працює на dash, ash, FreeBSD sh, macOS
set -eu
export LC_ALL=C
export LC_COLLATE=C
(set -o pipefail 2>/dev/null) && set -o pipefail || true

# Замість масиву: позиційні параметри пари "служба:шлях"
set -- "nginx:/var/log/nginx" "db:/var/log/postgresql"

TMP_LIST=$(mktemp "${TMPDIR:-/tmp}/logs.XXXXXX")
TMP_REPORT=$(mktemp "${TMPDIR:-/tmp}/rep.XXXXXX")

cleanup() {
    status=$?
    rm -f "$TMP_LIST" "$TMP_REPORT"
    exit "$status"
}
trap cleanup EXIT INT TERM HUP

# Обхід пар без використання асоціативних масивів
for pair in "$@"; do
    svc="${pair%%:*}"
    dir="${pair#*:}"
    
    if [ -d "$dir" ]; then
        # Переносне обмеження глибини каталогу без -maxdepth
        find "$dir" -path "$dir/*/*" -prune -o -type f -name "*.log" -print >> "$TMP_LIST"
    else
        printf 'Пропуск %s: нема каталогу %s\n' "$svc" "$dir" >&2
    fi
done

file_count=0
if [ -s "$TMP_LIST" ]; then
    file_count=$(wc -l < "$TMP_LIST" | tr -d '[:space:]')
fi
printf 'Знайдено файлів: %s ... ' "$file_count"

if [ "$file_count" -gt 0 ]; then
    # Переносний ERE regex замість Perl -P
    xargs grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*(ERROR|FATAL)' < "$TMP_LIST" \
        | sed 's/token=[^ ]*/token=***/g' > "$TMP_REPORT"
    mv -f "$TMP_REPORT" report.txt
fi

printf 'Завершено.\n'
