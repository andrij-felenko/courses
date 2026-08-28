#!/bin/sh
set -eu

PROGNAME="${0##*/}"
VERSION="1.4.0"

usage() {
    cat <<EOF
Використання: $PROGNAME [ОПЦІЇ] [ФАЙЛ ...]

Опції:
  -h, --help            Показати цю довідку й вийти
  -v, --version         Показати версію програми
  -o, --output FILE     Вказати шлях до файлу виводу
  -f, --force           Перезаписувати існуючий файл без запиту
  --                    Завершення списку опцій

Приклад:
  $PROGNAME -f -o /tmp/out.bin "Звіт за 2026.pdf" input2.dat
EOF
}

# Значення параметрів за замовчуванням
OUTPUT_FILE=""
FORCE_FLAG=0

# Основний цикл синтаксичного аналізу аргументів
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--version)
            printf "%s %s\n" "$PROGNAME" "$VERSION"
            exit 0
            ;;
        -f|--force)
            FORCE_FLAG=1
            shift
            ;;
        -o|--output)
            # Обробка формату з окремим словом: -o FILE або --output FILE
            if [ $# -lt 2 ]; then
                printf "%s: Помилка: опція '%s' вимагає значення файлу\n" "$PROGNAME" "$1" >&2
                exit 2
            fi
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --output=*)
            # Обробка формату зі знаком рівності: --output=FILE
            OUTPUT_FILE="${1#*=}"
            if [ -z "$OUTPUT_FILE" ]; then
                printf "%s: Помилка: значення для '--output' не може бути порожнім\n" "$PROGNAME" >&2
                exit 2
            fi
            shift
            ;;
        -o*)
            # Обробка злитого короткого формату: -oFILE
            OUTPUT_FILE="${1#-o}"
            shift
            ;;
        --)
            # Маркер завершення опцій: відкидаємо сам дефіс і виходимо з циклу
            shift
            break
            ;;
        -*)
            printf "%s: Помилка: невідома опція '%s'\n" "$PROGNAME" "$1" >&2
            printf "Спробуйте '%s --help' для отримання довідки.\n" "$PROGNAME" >&2
            exit 2
            ;;
        *)
            # Перший аргумент без провідного дефіса є позиційним операндом
            break
            ;;
    esac
done

# Валідація обов'язкових параметрів
if [ -z "$OUTPUT_FILE" ]; then
    printf "%s: Помилка: обов'язкова опція '-o/--output' не вказана\n" "$PROGNAME" >&2
    exit 2
fi

printf "Режим виконання:\n"
printf "  Цільовий файл: [%s]\n" "$OUTPUT_FILE"
printf "  Прапорець Force: %d\n" "$FORCE_FLAG"
printf "  Кількість залишкових позиційних операндів: %d\n" "$#"

# Ітерація за залишковими операндами з повним збереженням пробілів
for file_arg in "$@"; do
    printf "  -> Обробка операнда: [%s]\n" "$file_arg"
done
