#!/bin/sh
set -eu
export LC_ALL=C

. ./collect.conf                 # SERVICES='nginx postgres', OUT_DIR=…

die()  { printf '%s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "нема команди: $1"; }

abspath() (
    d=$(dirname -- "$1")
    b=$(basename -- "$1")
    cd -- "$d" || exit 1
    printf '%s/%s\n' "$(pwd -P)" "$b"
)

collect() (                      # тіло в дужках: змінні нікуди не витікають
    svc=$1
    case $svc in
        ''|*[!a-z0-9_-]*) die "недобра назва служби: $svc" ;;
    esac
    dir=/var/log/$svc
    [ -d "$dir" ] || die "нема каталогу $dir"

    set --                       # у функції позиційні параметри свої
    for f in "$dir"/*.log; do
        [ -f "$f" ] || continue  # шаблон без збігів лишається собою
        set -- "$@" "$f"
    done
    [ "$#" -gt 0 ] || die "$svc: жодного .log"

    printf '· %s: %d файлів … ' "$svc" "$#"

    tmp=$OUT_DIR/.$svc.$$
    (set -C; : > "$tmp") || die "тимчасовий файл уже існує"
    trap 'rm -f "$tmp"' EXIT INT TERM

    grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*(ERROR|FATAL)' -- "$@" \
        | sed 's/\(token=\)[^ ][^ ]*/\1***/g' \
        | sort > "$tmp"
    mv -- "$tmp" "$OUT_DIR/$svc.txt"

    printf 'готово\n'
)

need zstd
need tar
OUT_DIR=$(abspath "$OUT_DIR")
[ -d "$OUT_DIR" ] || die "нема каталогу $OUT_DIR"

for svc in $SERVICES; do         # без лапок свідомо: імена служб без пробілів
    collect "$svc" || exit 1     # exit у підоболонці нас не зупинить — перевіряємо
done

tar cf - -C "$OUT_DIR" . | zstd -q -o "report-$(date +%Y-%m-%d).tar.zst"
