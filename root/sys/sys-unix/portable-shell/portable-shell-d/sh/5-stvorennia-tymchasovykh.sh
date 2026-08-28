TMPDIR="${TMPDIR:-/tmp}"
# Переносне створення захищеного тимчасового каталогу
WORKDIR=$(mktemp -d "${TMPDIR}/app.XXXXXX" 2>/dev/null || mktemp -d -t 'app')

cleanup() {
    exit_code=$?
    release_lock
    rm -rf "$WORKDIR"
    exit "$exit_code"
}
# Реєстрація сигналів за стандартними символьними іменами (без префіксу SIG)
trap cleanup EXIT INT TERM HUP
