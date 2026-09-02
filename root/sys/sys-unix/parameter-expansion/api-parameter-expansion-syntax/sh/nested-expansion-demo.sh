#!/usr/bin/env bash
# Вкладення змінних у шаблони, тексти заміни та межі зрізів.
#
# Головне, що показує демонстрація: у полі ШАБЛОНА значення змінної за
# замовчуванням читається як glob-маска, а не як літерал. Подвійні лапки
# навколо "$var" усередині ${...} — не косметика, а перемикач режиму.
#
# Запуск: ./nested-expansion-demo.sh
set -uo pipefail

# Динамічний префікс. Лапки роблять $prefix літералом: без них префікс
# "module_" ще спрацював би, а "module[0]_" зіставився б як набір символів.
strip_dynamic_prefix() {
    local value=$1
    local prefix=$2
    printf '%s' "${value#"$prefix"}"
}

# Глобальна заміна ЛІТЕРАЛЬНОГО підрядка.
strip_replace_literal() {
    local value=$1
    local needle=$2
    local replacement=$3

    if [[ -z $needle ]]; then
        printf 'replace: порожній зразок пошуку\n' >&2
        return 2
    fi
    printf '%s' "${value//"$needle"/$replacement}"
}

# Те саме БЕЗ лапок навколо зразка — залишено навмисно, щоб побачити,
# у що перетворюється пошук, коли значення читають як маску.
strip_replace_glob() {
    local value=$1
    local needle=$2
    local replacement=$3
    printf '%s' "${value//$needle/$replacement}"
}

# Межі зрізу обчислюються в арифметичному контексті: імена змінних
# усередині пишуться БЕЗ знака $, дозволені дії й тернарний оператор.
slice_window() {
    local value=$1
    local offset=$2
    local length=$3

    if (( offset < 0 || length < 0 )); then
        printf "slice: від'ємні межі тут не підтримано\n" >&2
        return 2
    fi
    # Зміщення за межами рядка дає порожнечу, і це не помилка.
    (( offset < ${#value} )) || return 0
    printf '%s' "${value:offset:length}"
}

# Хвіст рядка. Від'ємне зміщення вимагає пробілу після двокрапки: без
# нього ":-" розібралося б як оператор дефолтного значення.
slice_tail() {
    local value=$1
    local count=$2

    (( count > 0 )) || return 2
    if (( count >= ${#value} )); then
        printf '%s' "$value"
        return 0
    fi
    printf '%s' "${value: -count}"
}

# Каскад джерел значення: аргумент -> оточення -> конфігурація -> дефолт.
# Вкладені дефолти обчислюються ліниво — праву гілку читають лише тоді,
# коли всі ліві виявилися порожніми.
resolve_setting() {
    local from_cli=$1
    local from_env=$2
    local from_cfg=$3
    local fallback=$4
    printf '%s' "${from_cli:-${from_env:-${from_cfg:-$fallback}}}"
}

main() {
    local log_line='module_core: DEBUG connect; DEBUG retry'
    local prefix='module_'
    local search='DEBUG'
    local replace='INFO'
    local offset=5
    local length=10

    printf '# Динамічний префікс\n'
    printf '    вхід:  %s\n' "$log_line"
    printf '    вихід: '; strip_dynamic_prefix "$log_line" "$prefix"; printf '\n'

    printf '# Динамічна заміна\n'
    printf '    вихід: '; strip_replace_literal "$log_line" "$search" "$replace"; printf '\n'

    # Зразок із метасимволом показує різницю двох режимів на тому самому рядку.
    local priced='cost 100*200 plus 100 to 200 units'
    local pattern='100*200'
    printf '    зразок %s як літерал: ' "$pattern"
    strip_replace_literal "$priced" "$pattern" '20000'; printf '\n'
    printf '    зразок %s як маска:   ' "$pattern"
    strip_replace_glob "$priced" "$pattern" '20000'; printf '\n'

    printf '# Динамічний зріз\n'
    printf '    ${log_line:offset:length} = '
    slice_window "$log_line" "$offset" "$length"; printf '\n'
    printf '    ${log_line:offset*0:length+2} = '
    slice_window "$log_line" $(( offset * 0 )) $(( length + 2 )); printf '\n'
    printf '    останні 6 символів = '
    slice_tail "$log_line" 6; printf '\n'

    printf '# Каскад дефолтів\n'
    printf '    порожні джерела -> '
    resolve_setting "" "" "" "8080"; printf '\n'
    printf '    є значення з оточення -> '
    resolve_setting "" "9090" "7070" "8080"; printf '\n'
}

main "$@"
