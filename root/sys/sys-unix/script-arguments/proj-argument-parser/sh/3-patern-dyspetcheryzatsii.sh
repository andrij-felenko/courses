# Зразок дворівневого парсера підкоманд
handle_deploy() {
    OPTIND=1
    TARGET_ENV="staging"
    while getopts "e:" opt; do
        case "$opt" in
            e) TARGET_ENV="$OPTARG" ;;
            *) return 2 ;;
        esac
    done
    shift "$((OPTIND - 1))"
    printf "Розгортання у середовище: %s, файли: %s\n" "$TARGET_ENV" "$*"
}

case "${1:-}" in
    deploy)
        shift
        handle_deploy "$@"
        ;;
    status)
        shift
        printf "Статус системи: OK\n"
        ;;
    *)
        printf "Помилка: невідома підкоманда '%s'\n" "${1:-}" >&2
        exit 2
        ;;
esac
