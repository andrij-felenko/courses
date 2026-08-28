VERBOSE=0
OUTPUT_FILE=""

while getopts ":hvf:o:" opt; do
    case "$opt" in
        h)
            show_help
            exit 0
            ;;
        v)
            VERBOSE=$((VERBOSE + 1))
            ;;
        f|o)
            OUTPUT_FILE="$OPTARG"
            ;;
        :)
            die "Опція -$OPTARG вимагає аргументу."
            ;;
        \?)
            die "Невідома опція -$OPTARG."
            ;;
    esac
done
# Зсув оброблених опцій: далі у $@ залишаються тільки позиційні аргументи
shift "$((OPTIND - 1))"
