defer_mktemp_dir() {
    local var_name="$1"
    local prefix="${2:-tmpdir}"
    
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/${prefix}.XXXXXXXXXX") || {
        echo "defer_mktemp_dir: не вдалося створити тимчасовий каталог" >&2
        return 1
    }
    
    # Примусове обмеження прав доступу лише для поточного користувача
    chmod 0700 "${dir}"
    
    # Реєстрація видалення каталогу
    defer "rm -rf '${dir}'"
    
    # Повернення шляху через змінну за посиланням
    printf -v "${var_name}" "%s" "${dir}"
}
