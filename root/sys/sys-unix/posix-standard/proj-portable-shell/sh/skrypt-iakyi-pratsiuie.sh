#!/bin/bash
set -e
source ./collect.conf          # SERVICES=(nginx postgres), OUT_DIR=…

collect() {
    local svc=$1
    local dir=/var/log/$svc
    [[ -d $dir ]] || { echo "нема каталогу $dir"; return 1; }

    local files=()
    for f in "$dir"/*.log; do
        [[ -f $f ]] && files+=("$f")
    done

    echo -n "· $svc: ${#files[@]} файлів … "
    grep -P '^\d{4}-\d{2}-\d{2}.*\b(ERROR|FATAL)\b' "${files[@]}" \
        | sed -E 's/(token=)[^ ]+/\1***/g' \
        | sort > "$OUT_DIR/$svc.txt"
    echo "готово"
}

which zstd >/dev/null || { echo "нема zstd"; exit 1; }
OUT_DIR=$(readlink -f "$OUT_DIR")
for svc in "${SERVICES[@]}"; do collect "$svc"; done
tar cf - -C "$OUT_DIR" . | zstd -q -o "report-$(date +%Y-%m-%d).tar.zst"
