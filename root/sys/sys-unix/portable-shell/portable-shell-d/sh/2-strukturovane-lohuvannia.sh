log_info() {
    printf '[INFO] %s\n' "$*" >&2
}

log_warn() {
    printf '[WARN] %s\n' "$*" >&2
}

die() {
    printf '[FATAL] %s\n' "$*" >&2
    exit 1
}
