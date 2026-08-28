parse_helper() {
    # Скидання індексу для коректного старту вбудованого парсера
    OPTIND=1
    while getopts "ab:" opt; do
        case "$opt" in
            a) echo "Прапорець a" ;;
            b) echo "Значення b: $OPTARG" ;;
        esac
    done
    shift "$((OPTIND - 1))"
}
