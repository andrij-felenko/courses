log_entry="[2026-08-25 14:32:01] ERROR: Connection timeout on port 8080"
regex='^\[([0-9]{4}-[0-9]{2}-[0-9]{2}) [^]]+\] ([A-Z]+): (.*)$'

if [[ $log_entry =~ $regex ]]; then
    date="${BASH_REMATCH[1]}"
    level="${BASH_REMATCH[2]}"
    message="${BASH_REMATCH[3]}"

    printf "Дата: %s | Рівень: %s | Текст: %s\n" "$date" "$level" "$message"
fi
