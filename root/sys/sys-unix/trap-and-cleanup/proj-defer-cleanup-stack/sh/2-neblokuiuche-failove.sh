defer_flock() {
    local lock_file="$1"
    local fd="${2:-200}"

    # Відкриття дескриптора на запис
    eval "exec ${fd}>'${lock_file}'" || return 1
    
    # Спроба негайного захоплення замка без очікування
    if ! flock -n "${fd}"; then
        echo "defer_flock: блокування вже утримується іншим процесом: ${lock_file}" >&2
        eval "exec ${fd}>&-"
        return 1
    fi

    # Закриття дескриптора в кінці роботи автоматично звільнить замок у VFS
    defer "exec ${fd}>&-"
}
