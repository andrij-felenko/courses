#!/usr/bin/env bash
set -euo pipefail

# Лічильники стану основного процесу
total_records=0
valid_records=0
invalid_records=0

# Регулярні вирази для перевірки формату
readonly IP_REGEX='^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$'
readonly NAME_REGEX='^[a-zA-Z0-9_-]+$'

# Функція валідації октету IPv4
validate_ip() {
    local ip="$1"
    if [[ "$ip" =~ $IP_REGEX ]]; then
        local o1="${BASH_REMATCH[1]}"
        local o2="${BASH_REMATCH[2]}"
        local o3="${BASH_REMATCH[3]}"
        local o4="${BASH_REMATCH[4]}"
        
        # Перевірка діапазону 0..255 для кожного октету
        if (( o1 <= 255 && o2 <= 255 && o3 <= 255 && o4 <= 255 )); then
            return 0
        fi
    fi
    return 1
}

# Обробка потоку даних
process_stream() {
    local input_file="${1:-/dev/stdin}"
    
    if [[ ! -r "$input_file" ]]; then
        printf "Помилка: файл '%s' недоступний для читання\n" "$input_file" >&2
        return 2
    fi

    # Канонічний патерн: IFS= захищає від обрізання пробілів, -r захищає від \
    # || [ -n "$line" ] рятує останній рядок без \n
    while IFS= read -r raw_line || [ -n "$raw_line" ]; do
        # 1. Нативне видалення початкових і кінцевих пробілів без виклику зовнішніх утиліт
        local line="${raw_line#"${raw_line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"

        # 2. Фільтрація коментарів та порожніх рядків через оператор case
        case "$line" in
            ""|\#*)
                continue
                ;;
        esac

        (( total_records++ ))

        # 3. Розбір запису на окремі поля за роздільником ':'
        # Тимчасово перевизначаємо IFS для read без впливу на решту скрипту
        local name="" ip="" port="" status=""
        IFS=':' read -r name ip port status <<< "$line"

        # Очищення пробілів у кожному витягнутому полі
        name="${name#"${name%%[![:space:]]*}"}"
        name="${name%"${name##*[![:space:]]}"}"
        ip="${ip#"${ip%%[![:space:]]*}"}"
        ip="${ip%"${ip##*[![:space:]]}"}"
        port="${port#"${port%%[![:space:]]*}"}"
        port="${port%"${port##*[![:space:]]}"}"
        status="${status#"${status%%[![:space:]]*}"}"
        status="${status%"${status##*[![:space:]]}"}"

        # 4. Комплексна перевірка валідності полів
        local is_valid=1

        # Перевірка імені
        if [[ ! "$name" =~ $NAME_REGEX ]]; then
            is_valid=0
        fi

        # Перевірка IP-адреси
        if ! validate_ip "$ip"; then
            is_valid=0
        fi

        # Перевірка порту (1..65535)
        if ! [[ "$port" =~ ^[0-9]+$ ]] || (( port < 1 || port > 65535 )); then
            is_valid=0
        fi

        # Перевірка статусу через case
        case "$status" in
            ENABLED|DISABLED|MAINTENANCE)
                ;;
            *)
                is_valid=0
                ;;
        esac

        # 5. Вивід результату та оновлення статистики
        if (( is_valid == 1 )); then
            (( valid_records++ ))
            printf "[OK] Сервіс: %-15s | Адреса: %-15s:%-5d | Стан: %s\n" \
                "$name" "$ip" "$port" "$status"
        else
            (( invalid_records++ ))
            printf "[ПОМИЛКА] Некоректний запис: '%s'\n" "$raw_line" >&2
        fi

    # Перенаправлення вводу безпосередньо у цикл:
    # Змінні total_records/valid_records лишаються доступними після завершення циклу
    done < "$input_file"

    printf "\n=== Підсумок обробки ===\n"
    printf "Усього записів:   %d\n" "$total_records"
    printf "Валідних:         %d\n" "$valid_records"
    printf "Невалідних:       %d\n" "$invalid_records"
}

# Запуск з переданим аргументом або через стандартний потік
process_stream "${1:-/dev/stdin}"
