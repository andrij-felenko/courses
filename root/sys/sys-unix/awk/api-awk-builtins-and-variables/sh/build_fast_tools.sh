#!/usr/bin/env bash
# build_fast_tools.sh — збірка модуля розширення з C- і C++-варіантів,
# підключення через AWKLIBPATH і димовий тест обох функцій.
#
#   ./build_fast_tools.sh          # тести моделей + обидва варіанти + звірка
#   ./build_fast_tools.sh c        # лише C
#   ./build_fast_tools.sh cpp      # лише C++
#   ./build_fast_tools.sh test     # лише тести cpp/internals (gawk не потрібен)
set -euo pipefail

VARIANT=${1:-both}
case $VARIANT in
    c|cpp|both|test) ;;
    *) echo "варіант: c | cpp | both | test" >&2; exit 2 ;;
esac

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT=$(cd -- "$SCRIPT_DIR/.." && pwd)

WORK=$(mktemp -d "${TMPDIR:-/tmp}/fast-tools.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# Моделі з cpp/internals навмисно не знають про <gawkapi.h>, тому їхні тести
# збираються й на машині без gawk-devel — і йдуть ПЕРШИМИ.
run_model_tests() {
    ${CXX:-c++} -std=c++17 -O2 -Wall -Wextra \
        -o "$WORK/test_internals" "$PROJECT/cpp/tests/test_internals.cpp"
    "$WORK/test_internals"
}

if [[ $VARIANT == test ]]; then
    run_model_tests
    exit 0
fi

run_model_tests

command -v gawk >/dev/null || { echo "API розширень є лише в gawk" >&2; exit 2; }

read -r API_MAJOR API_MINOR GAWK_VER < <(
    gawk 'BEGIN { print PROCINFO["api_major"], PROCINFO["api_minor"], PROCINFO["version"] }'
)
[[ -n ${API_MAJOR:-} ]] || {
    echo "цей gawk не повідомляє версії API — зібраний без підтримки розширень" >&2
    exit 2
}
echo "gawk $GAWK_VER, Extension API $API_MAJOR.$API_MINOR" >&2

# gawkapi.h у стандартному шляху компілятора лежить рідко — шукаємо явно.
API_DIR=""
for d in "${GAWK_INCLUDE:-}" /usr/include/gawk /usr/local/include/gawk \
         /usr/include /usr/local/include /opt/homebrew/include; do
    if [[ -n $d && -r $d/gawkapi.h ]]; then API_DIR=$d; break; fi
done
[[ -n $API_DIR ]] || {
    echo "не знайшов gawkapi.h — постав пакет gawk-devel / gawk-dev" >&2
    exit 2
}
echo "заголовок: $API_DIR/gawkapi.h" >&2

# Димовий тест. Хеш порожнього рядка мусить дорівнювати базису FNV-1a —
# це єдина константа алгоритму, яку можна перевірити без таблиці векторів.
cat > "$WORK/smoke.awk" <<'AWK'
@load "fast_tools"
BEGIN {
    if (fnv1a_64("") != "0xcbf29ce484222325") {
        print "базис FNV-1a не збігся: " fnv1a_64("") > "/dev/stderr"
        exit 1
    }
    n = split("a b abc ключ 0123456789 -", w, " ")
    for (i = 1; i <= n; i++) printf "%s\t%s\n", w[i], fnv1a_64(w[i])

    t0 = monotonic_time_ns()
    for (i = 0; i < 200000; i++) h = fnv1a_64("навантаження")
    t1 = monotonic_time_ns()
    if (t1 <= t0) { print "монотонний час не зростає" > "/dev/stderr"; exit 1 }
    printf "200000 викликів за %.1f мс\n", (t1 - t0) / 1000000 > "/dev/stderr"
}
AWK

build_and_run() {
    local kind=$1 dir="$WORK/$1"
    mkdir -p "$dir"
    case $kind in
        c)
            ${CC:-cc} -fPIC -shared -O2 -Wall -Wextra -I"$API_DIR" \
                -o "$dir/fast_tools.so" \
                "$PROJECT/c/fast_tools.c" "$PROJECT/c/fnv1a.c"
            ;;
        cpp)
            ${CXX:-c++} -fPIC -shared -O2 -Wall -Wextra -std=c++17 -I"$API_DIR" \
                -o "$dir/fast_tools.so" \
                "$PROJECT/cpp/extension.cpp" "$PROJECT/cpp/builtins.cpp"
            ;;
    esac
    echo "зібрано $dir/fast_tools.so ($kind)" >&2

    # @load шукає бібліотеку саме по AWKLIBPATH, а не по LD_LIBRARY_PATH.
    AWKLIBPATH=$dir gawk -f "$WORK/smoke.awk" > "$WORK/out.$kind"
    echo "димовий тест ($kind) пройдено" >&2
}

if [[ $VARIANT == c || $VARIANT == both ]]; then build_and_run c; fi
if [[ $VARIANT == cpp || $VARIANT == both ]]; then build_and_run cpp; fi

if [[ $VARIANT == both ]]; then
    if diff -u "$WORK/out.c" "$WORK/out.cpp"; then
        echo "C і C++ дають побайтово однакові хеші" >&2
    else
        echo "варіанти розійшлися — див. diff вище" >&2
        exit 1
    fi
    cat "$WORK/out.c"
else
    cat "$WORK/out.$VARIANT"
fi
