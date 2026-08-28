LOCKDIR="${TMPDIR:-/tmp}/my_script.lock"

acquire_lock() {
    if mkdir "$LOCKDIR" 2>/dev/null; then
        return 0
    else
        log_warn "Скрипт уже виконується (каталог блокування $LOCKDIR зайнятий)"
        return 1
    fi
}

release_lock() {
    rmdir "$LOCKDIR" 2>/dev/null || true
}
