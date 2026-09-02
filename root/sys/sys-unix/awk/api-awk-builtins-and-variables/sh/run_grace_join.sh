#!/usr/bin/env bash
# run_grace_join.sh — оркестрація секціонованого (Grace) хеш-з'єднання.
# Спершу обидва відношення розкладаються по K партиціях за хешем ключа, далі
# партиції з однаковими номерами з'єднуються попарно в пам'яті. Споживання
# RAM визначає розмір ОДНІЄЇ партиції, а не розмір вхідних файлів.
#
# Використання: run_grace_join.sh <rel_r.tsv> <rel_s.tsv> <out.tsv> [K] [KEY]
set -euo pipefail

usage() {
    echo "використання: $(basename "$0") <rel_r.tsv> <rel_s.tsv> <out.tsv> [K] [KEY]" >&2
    exit 2
}

(( $# >= 3 )) || usage
REL_R=$1
REL_S=$2
RESULT=$3
K=${4:-64}
KEY=${5:-1}

[[ $K =~ ^[0-9]+$ ]] && (( K >= 2 )) || usage
[[ $KEY =~ ^[0-9]+$ ]] && (( KEY >= 1 )) || usage
command -v gawk >/dev/null || { echo "потрібен gawk: partition.awk спирається на and()/xor()" >&2; exit 2; }
[[ -r $REL_R ]] || { echo "не читається $REL_R" >&2; exit 2; }
[[ -r $REL_S ]] || { echo "не читається $REL_S" >&2; exit 2; }

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PARTITION_AWK=$SCRIPT_DIR/../awk/join/partition.awk
[[ -r $PARTITION_AWK ]] || { echo "не знайшов $PARTITION_AWK" >&2; exit 2; }

# Партиції — тимчасові файли на десятки гігабайтів: прибираємо їх і після
# Ctrl+C, і після падіння, а не лише після успішного проходу.
WORK=$(mktemp -d "${TMPDIR:-/tmp}/grace-join.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# Побайтові порівняння й побайтовий хеш: без цього ключі з кирилицею
# роз'їхалися б по різних партиціях у різних локалях.
export LC_ALL=C

echo "1/3 розбиття $REL_R на $K партицій" >&2
gawk -b -F'\t' -v K="$K" -v KEY="$KEY" -v PREFIX="$WORK/part_r" -f "$PARTITION_AWK" "$REL_R"

echo "2/3 розбиття $REL_S на $K партицій" >&2
gawk -b -F'\t' -v K="$K" -v KEY="$KEY" -v PREFIX="$WORK/part_s" -f "$PARTITION_AWK" "$REL_S"

: > "$RESULT"
last=$(( K - 1 ))
pad=${#last}          # та сама ширина номера, що й у partition.awk
pairs=0

for (( i = 0; i < K; i++ )); do
    f_r=$(printf '%s/part_r_%0*d.tsv' "$WORK" "$pad" "$i")
    f_s=$(printf '%s/part_s_%0*d.tsv' "$WORK" "$pad" "$i")

    # Партиція могла й не народитися: у неї просто не влучив жоден ключ.
    if [[ ! -s $f_r || ! -s $f_s ]]; then
        rm -f "$f_r" "$f_s"
        continue
    fi

    # Партиції нормалізовані partition.awk у два стовпці (ключ, решта), тому
    # тут потрібне лише звичайне з'єднання в пам'яті — з повною підтримкою
    # дублікатів ключа з обох боків.
    gawk -F'\t' -v OFS='\t' '
        function payload(line,   t) { t = index(line, "\t"); return (t ? substr(line, t + 1) : "") }
        FNR == NR { r[$1, ++n[$1]] = payload($0); next }
        $1 in n   { p = payload($0); for (j = 1; j <= n[$1]; j++) print $1, r[$1, j], p }
    ' "$f_r" "$f_s" >> "$RESULT"

    rm -f "$f_r" "$f_s"      # звільняємо диск одразу, а не наприкінці
    pairs=$(( pairs + 1 ))
done

echo "3/3 з'єднано пар партицій: $pairs; $RESULT — $(wc -l < "$RESULT") рядків" >&2
