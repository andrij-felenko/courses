#!/usr/bin/env bash
# Масиви: перелік РЕАЛЬНИХ індексів розрідженого масиву, склеювання через
# IFS[0] і передавання елементів без втрати меж аргументів.
# Потрібен Bash 4.3+ (nameref у `local -n`).
#
# Назви локальних посилань мають префікс __arrayutil_: nameref розв'язується
# в динамічній області видимості, тож коротке ім'я на кшталт `ref` захопило б
# однойменну локальну змінну викликача замість його масиву.

# Кількість ІНІЦІАЛІЗОВАНИХ елементів (дірки розрідженого масиву не рахуються).
array_count() {
    local -n __arrayutil_ref=$1
    printf '%d' "${#__arrayutil_ref[@]}"
}

# Наявні індекси (для declare -a) або ключі (для declare -A), по одному в рядок.
array_keys() {
    local -n __arrayutil_ref=$1
    local __arrayutil_key
    for __arrayutil_key in "${!__arrayutil_ref[@]}"; do
        printf '%s\n' "$__arrayutil_key"
    done
}

# "індекс -> значення" по існуючих вузлах у порядку зростання індексу.
# Проміжні неініціалізовані комірки не існують у пам'яті, тож ітератор
# їх просто не бачить: arr[0], arr[50], arr[200] дають рівно три рядки.
array_dump() {
    local -n __arrayutil_ref=$1
    local __arrayutil_key
    for __arrayutil_key in "${!__arrayutil_ref[@]}"; do
        printf 'Індекс: %s -> Значення: %s\n' \
            "$__arrayutil_key" "${__arrayutil_ref[$__arrayutil_key]}"
    done
}

# Склеювання в ОДНЕ слово, як "${arr[*]}": з роздільника береться лише
# перший байт, решта символів IFS у склеюванні участі не бере.
# IFS оголошено локальним — глобальний стан оболонки не чіпаємо.
array_join() {
    local __arrayutil_sep=$1
    local -n __arrayutil_ref=$2
    local IFS=$__arrayutil_sep
    printf '%s' "${__arrayutil_ref[*]-}"
}

# Виклик команди з елементами масиву як окремими аргументами argv.
# Форма ${arr[@]+"${arr[@]}"} потрібна для сумісності з Bash < 4.4:
# там звернення до ПОРОЖНЬОГО масиву під set -u було фатальним.
array_apply() {
    local __arrayutil_cmd=$1
    local -n __arrayutil_ref=$2
    "$__arrayutil_cmd" ${__arrayutil_ref[@]+"${__arrayutil_ref[@]}"}
}
