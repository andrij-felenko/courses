#!/usr/bin/env bash
# Дві форми розкриття масиву — "${arr[@]}" і "${arr[*]}" — та їхня ціна.
#
# Демонстрація міряє те єдине, що тут має значення: скільки СЛІВ дійшло до
# argv команди-приймача. На екрані вивід обох форм часто виглядає однаково,
# і саме тому різницю ловлять лічильником $#, а не оком.
#
# Потрібен Bash 4.3+ (nameref у lib/arrayutil.sh).
# Запуск: ./array-forms-demo.sh
set -uo pipefail

source "${BASH_SOURCE[0]%/*}/lib/arrayutil.sh"

# Команда-приймач: друкує рівно те, що оболонка поклала в її argv.
# %q екранує пробіли й переводи рядка, тож межі слів видно однозначно.
report_argv() {
    local label=$1
    shift
    printf '%s -> слів: %d\n' "$label" "$#"

    local index=1
    local arg
    for arg in "$@"; do
        printf '    argv[%d] = %q\n' "$index" "$arg"
        index=$(( index + 1 ))
    done
}

# Приймач без підпису — для array_apply, який передає лише елементи масиву.
count_argv() {
    printf '    приймач отримав аргументів: %d\n' "$#"

    local index=1
    local arg
    for arg in "$@"; do
        printf '    argv[%d] = %q\n' "$index" "$arg"
        index=$(( index + 1 ))
    done
}

# 1. Вектор проти скаляра на тому самому масиві.
demo_word_boundaries() {
    local -a hosts=("web node" "db node" "*.log")

    printf '# Межі слів\n'
    report_argv '"${hosts[@]}"' "${hosts[@]}"
    report_argv '"${hosts[*]}"' "${hosts[*]}"

    # Без лапок до результату ще застосовуються поділ за IFS і зіставлення
    # шляхів: "web node" розсипається надвоє, а "*.log" може перетворитися
    # на список файлів поточного каталогу.
    report_argv '${hosts[@]} без лапок' ${hosts[@]}
}

# 2. Склеювання бере лише ПЕРШИЙ байт IFS, решта символів ігнорується.
demo_ifs_join() {
    local -a ips=("192.168.1.1" "10.0.0.1" "172.16.0.1")

    printf '# Роздільник склеювання\n'
    printf '    IFS=";,"  -> '; array_join ';,' ips; printf '\n'
    printf '    IFS=" "   -> '; array_join ' ' ips;  printf '\n'
    printf '    IFS=""    -> '; array_join '' ips;   printf '\n'
}

# 3. Порожній масив: нуль ітерацій проти однієї зайвої.
demo_empty_array() {
    local -a empty=()
    local item
    local rounds=0

    printf '# Порожній масив у циклі for\n'

    # Захисна форма ${arr[@]+"${arr[@]}"} потрібна лише для Bash < 4.4;
    # у сучасних версіях "${empty[@]}" під set -u безпечне саме по собі.
    for item in ${empty[@]+"${empty[@]}"}; do
        rounds=$(( rounds + 1 ))
    done
    printf '    через [@]: ітерацій %d\n' "$rounds"

    rounds=0
    for item in "${empty[*]}"; do
        rounds=$(( rounds + 1 ))
        printf '    через [*]: ітерація %d, item=%q\n' "$rounds" "$item"
    done
    printf '    через [*]: ітерацій %d (зайва)\n' "$rounds"
}

# 4. Розріджений масив: ітератор бачить лише існуючі вузли.
demo_sparse_array() {
    local -a sparse=()
    sparse[0]="first"
    sparse[42]="middle"
    sparse[999]="last"

    printf '# Розріджений масив\n'
    printf '    ініціалізованих елементів: '; array_count sparse; printf '\n'
    array_dump sparse
}

# 5. Передавання елементів у команду без втрати меж аргументів.
demo_apply() {
    local -a files=("config file.json" $'data\nз переводом рядка.txt' "*.log")
    local -a nothing=()

    printf '# Передавання в команду\n'
    array_apply count_argv files
    printf '    той самий виклик на порожньому масиві:\n'
    array_apply count_argv nothing
}

main() {
    demo_word_boundaries
    demo_ifs_join
    demo_empty_array
    demo_sparse_array
    demo_apply
}

main "$@"
