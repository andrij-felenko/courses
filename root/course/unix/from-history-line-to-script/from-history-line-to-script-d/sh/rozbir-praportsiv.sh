while getopts ":s:d:k:vh" opt; do
    case "${opt}" in
        s) SOURCE_DIR="${OPTARG}" ;;
        d) DEST_DIR="${OPTARG}" ;;
        k) RETENTION_DAYS="${OPTARG}" ;;
        v) VERBOSE=1 ;;
        h) usage; exit 0 ;;
        \?) printf 'Невідомий прапорець: -%s\n' "${OPTARG}" >&2; exit 2 ;;
        :)  printf 'Опція -%s вимагає аргументу.\n' "${OPTARG}" >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1)) # Зсуває оброблені прапорці, залишаючи лише залишок позиційних аргументів
