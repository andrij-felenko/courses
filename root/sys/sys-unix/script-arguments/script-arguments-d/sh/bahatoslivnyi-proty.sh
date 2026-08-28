# Тихий режим: на початку optstring стоїть двокрапка ':'
while getopts ":f:o:vh" opt; do
    case "$opt" in
        f)
            FORCE_FILE="$OPTARG"
            ;;
        o)
            OUTPUT_FILE="$OPTARG"
            ;;
        v)
            VERBOSE=1
            ;;
        h)
            show_help
            exit 0
            ;;
        :)
            # Опція вимагала аргумент, але користувач його не вказав
            printf "Помилка: опція '-%s' вимагає значення аргументу.\n" "$OPTARG" >&2
            exit 1
            ;;
        \?|*)
            # Вказано невідомий прапорець
            printf "Помилка: невідома опція '-%s'.\n" "$OPTARG" >&2
            printf "Використовуйте -h для перегляду списку опцій.\n" >&2
            exit 1
            ;;
    esac
done
