# Спільні помічники скриптів довідника find/xargs.
# Файл лише підключають через `.` — власного shebang у нього немає
# і самостійно він не запускається.

log()  { printf '%s\n' "$*" >&2; }
warn() { printf 'увага: %s\n' "$*" >&2; }
die()  { printf 'помилка: %s\n' "$*" >&2; exit 2; }

# Кожна утиліта з переліку мусить бути в PATH. Падаємо одразу, а не посеред
# обходу дерева на сотні тисяч файлів.
need() {
    local cmd
    local missing=()
    for cmd in "$@"; do
        command -v -- "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
    done
    (( ${#missing[@]} == 0 )) || die "у PATH немає: ${missing[*]}"
}

# -printf, --process-slot-var, -O3, --show-limits — це розширення GNU.
# На BSD-версіях їх просто немає, і тихий різнобій гірший за чесну відмову.
# `--version` беремо цілком: обрізати його через `head` не можна, бо SIGPIPE
# під `set -o pipefail` зробив би з цього хибну діагностику.
require_gnu() {
    local tool ver
    for tool in "$@"; do
        ver=$("$tool" --version 2>/dev/null) || ver=''
        [[ $ver == *GNU* ]] \
            || die "потрібна GNU-версія '$tool' (findutils/coreutils)"
    done
}

# Тимчасова тека, яку прибирає trap навіть при аварійному виході чи Ctrl+C.
SELF_TMPDIR=''
make_tmpdir() {
    SELF_TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/findxargs.XXXXXX") \
        || die "mktemp не створив тимчасову теку"
    trap 'drop_tmpdir' EXIT HUP INT TERM
}
drop_tmpdir() {
    if [[ -n $SELF_TMPDIR && -d $SELF_TMPDIR ]]; then
        rm -rf -- "$SELF_TMPDIR"
        SELF_TMPDIR=''
    fi
    return 0   # trap на EXIT не має міняти підсумковий код виходу
}

# Розшифровка коду виходу xargs. Повертає 0, лише якщо все справді минуло
# добре, — виклик зручно писати як `explain_xargs_status "$rc" || failed=1`.
explain_xargs_status() {
    case $1 in
        0)   return 0 ;;
        123) warn "xargs: частина воркерів завершилася кодом 1..125" ;;
        124) warn "xargs: воркер повернув 255 — читання входу перервано" ;;
        125) warn "xargs: внутрішній збій (ліміт -s при -x, брак пам'яті, хибний прапорець)" ;;
        126) warn "xargs: команду знайдено, але вона не запускається (EACCES/ENOEXEC)" ;;
        127) warn "xargs: команду не знайдено в PATH (ENOENT)" ;;
        *)   warn "xargs: код виходу $1" ;;
    esac
    return 1
}

# Скільки NUL-розділених записів у файлі.
nul_count() {
    tr -cd '\0' <"$1" | wc -c | tr -d ' '
}
