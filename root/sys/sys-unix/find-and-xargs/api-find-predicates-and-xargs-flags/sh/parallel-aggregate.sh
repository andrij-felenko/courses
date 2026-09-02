#!/usr/bin/env bash
# Три схеми безпечного агрегування виводу паралельних воркерів `xargs -P`:
#
#   slot      — кожен воркер пише у власний файл за номером слота
#               (--process-slot-var), наприкінці — детерміноване злиття;
#   flock     — спільний файл під консультативним блокуванням flock(2);
#   collector — воркери пишуть у спільний канал, читає один процес-колектор.
#
# Корисне навантаження воркера — запис «розмір TAB sha256 TAB шлях», який
# завершується NUL: у назві файлу може бути й перевід рядка.
#
# Скрипт сам собі воркер: xargs запускає ЦЕЙ файл із --worker, і саме так
# роблять у житті, бо інакше тіло воркера довелося б віддавати через
# `sh -c '...'` з екрануванням у три поверхи.
set -euo pipefail
export LC_ALL=C

self_dir=$(cd -- "$(dirname -- "$0")" && pwd)
# shellcheck source=lib/common.sh
. "$self_dir/lib/common.sh"
self="$self_dir/$(basename -- "$0")"

# --- воркер ---------------------------------------------------------------

emit_records() {
    local f size sum
    for f in "$@"; do
        # Файл міг зникнути між getdents64() у find і open() тут — та сама
        # гонитва, що дає ENOENT у `-exec`. Пропускаємо, не валячи весь пакет.
        if [[ ! -f $f || ! -r $f ]]; then
            warn "зник або недоступний: $f"
            continue
        fi
        size=$(stat -c '%s' -- "$f" 2>/dev/null) || { warn "stat не вдався: $f"; continue; }
        sum=$(sha256sum -- "$f" 2>/dev/null) || { warn "sha256sum не вдався: $f"; continue; }
        sum=${sum%% *}
        # Один запис — один printf, тобто один write(2). Поки запис менший за
        # PIPE_BUF (у Linux 4096 байтів), ядро не поріже його навпіл у каналі.
        printf '%s\t%s\t%s\0' "$size" "$sum" "$f"
    done
}

if [[ ${1-} == --worker ]]; then
    shift
    case ${AGG_MODE:-} in
        slot)
            [[ -n ${SLOT_OUT_DIR:-} ]] || die "воркер: не задано SLOT_OUT_DIR"
            # SLOT приходить від xargs --process-slot-var і має значення
            # 0..jobs-1, тож два живі воркери ніколи не ділять один файл.
            emit_records "$@" >>"$SLOT_OUT_DIR/part.${SLOT:-0}"
            ;;
        flock)
            [[ -n ${SHARED_OUT:-} && -n ${LOCK_FILE:-} ]] \
                || die "воркер: не задано SHARED_OUT/LOCK_FILE"
            buf=$(mktemp "${TMPDIR:-/tmp}/agg.XXXXXX") || die "воркер: mktemp не спрацював"
            trap 'rm -f -- "$buf"' EXIT
            # Рахуємо ПОЗА критичною секцією: під блокуванням тримаємо лише
            # сам дозапис, інакше паралельність вироджується в чергу.
            emit_records "$@" >"$buf"
            exec 9>"$LOCK_FILE"
            flock -x 9
            cat -- "$buf" >>"$SHARED_OUT"
            flock -u 9
            exec 9>&-
            ;;
        collector)
            # stdout воркера — спільний канал до колектора.
            emit_records "$@"
            ;;
        *)
            die "воркер: невідомий режим '${AGG_MODE:-}'"
            ;;
    esac
    exit 0
fi

# --- диспетчер ------------------------------------------------------------

usage() {
    cat >&2 <<'EOF'
використання: parallel-aggregate.sh -o ФАЙЛ [-m slot|flock|collector] [-j N] [-n N] КАТАЛОГ
  -o ФАЙЛ   куди скласти зібрані записи (NUL-розділені)
  -m РЕЖИМ  схема агрегування (типово slot)
  -j N      скільки воркерів тримати одночасно (xargs -P, типово 4)
  -n N      скільки шляхів віддавати одному запуску (xargs -n, типово 16)
EOF
    exit 2
}

mode=slot
jobs=4
batch=16
out=''
while getopts ':m:j:n:o:h' opt; do
    case $opt in
        m) mode=$OPTARG ;;
        j) jobs=$OPTARG ;;
        n) batch=$OPTARG ;;
        o) out=$OPTARG ;;
        h) usage ;;
        :) die "прапорець -$OPTARG вимагає значення" ;;
        *) die "невідомий прапорець -$OPTARG" ;;
    esac
done
shift $((OPTIND - 1))
(( $# == 1 )) || usage
dir=$1

[[ -d $dir ]] || die "не каталог: $dir"
[[ -n $out ]] || die "потрібен -o ФАЙЛ"
case $mode in slot|flock|collector) ;; *) die "режим має бути slot|flock|collector" ;; esac
[[ $jobs  =~ ^[1-9][0-9]*$ ]] || die "-j: потрібне додатне число"
[[ $batch =~ ^[1-9][0-9]*$ ]] || die "-n: потрібне додатне число"

need find xargs stat sha256sum tr wc cat
require_gnu find xargs
if [[ $mode == flock ]]; then need flock; fi

make_tmpdir
: >"$out"

# Список складаємо окремим кроком і віддаємо його через `xargs -a`, а не
# конвеєром. Дві причини: код виходу find не змішується з кодом виходу xargs,
# а stdin лишається вільним — воркер може ним користуватися сам.
list="$SELF_TMPDIR/list"
find_err="$SELF_TMPDIR/find.err"
find_rc=0
find "$dir" -xdev -ignore_readdir_race -type f -print0 \
    >"$list" 2>"$find_err" || find_rc=$?
if (( find_rc != 0 )); then
    warn "find повернув $find_rc: частина дерева недоступна ($(wc -l <"$find_err") повідомлень)"
fi

planned=$(nul_count "$list")
log "файлів у черзі: $planned, воркерів: $jobs, пакет: $batch, режим: $mode"

collect() {
    # Єдиний читач спільного каналу: розбирає NUL-записи й складає їх у вихід
    # послідовно. Перемішатися тут нічому — пише один процес.
    local size sum path
    local n=0
    while IFS=$'\t' read -r -d '' size sum path; do
        printf '%s\t%s\t%s\0' "$size" "$sum" "$path"
        n=$((n + 1))
    done
    log "колектор прийняв записів: $n"
}

failed=0
rc=0
case $mode in
    slot)
        parts="$SELF_TMPDIR/parts"
        mkdir -p "$parts"
        AGG_MODE=slot SLOT_OUT_DIR="$parts" \
            xargs -0 -a "$list" -r -P "$jobs" -n "$batch" \
                  --process-slot-var=SLOT -- "$self" --worker || rc=$?
        explain_xargs_status "$rc" || failed=1
        # Злиття детерміноване: частини йдуть у порядку номерів слотів,
        # тож повторний прогін дає байт-у-байт той самий файл.
        for part in "$parts"/part.*; do
            if [[ -e $part ]]; then
                cat -- "$part" >>"$out"
            fi
        done
        ;;
    flock)
        lock="$SELF_TMPDIR/agg.lock"
        : >"$lock"
        AGG_MODE=flock LOCK_FILE="$lock" SHARED_OUT="$out" \
            xargs -0 -a "$list" -r -P "$jobs" -n "$batch" \
                  -- "$self" --worker || rc=$?
        explain_xargs_status "$rc" || failed=1
        ;;
    collector)
        # Код виходу xargs беремо з PIPESTATUS: у конвеєрі `$?` — це статус
        # колектора, а нам потрібен статус пулу воркерів.
        set +e
        AGG_MODE=collector \
            xargs -0 -a "$list" -r -P "$jobs" -n "$batch" \
                  -- "$self" --worker | collect >"$out"
        rc=${PIPESTATUS[0]}
        set -e
        explain_xargs_status "$rc" || failed=1
        ;;
esac

got=$(nul_count "$out")
log "записів у '$out': $got із $planned запланованих"
log "прочитати результат: tr '\\0' '\\n' < '$out'"
if (( got != planned )); then
    warn "частина файлів не дала запису — див. попередження воркерів вище"
fi
exit "$failed"
