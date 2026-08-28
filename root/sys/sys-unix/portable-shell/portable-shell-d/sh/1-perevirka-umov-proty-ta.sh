# Заміна regex перевірки [[ "$input" =~ ^[0-9]+$ ]]
case "$input" in
    ''|*[!0-9]*)
        echo "Помилка: $input не є числом" >&2
        return 1
        ;;
    *)
        echo "Коректне число: $input"
        ;;
esac
