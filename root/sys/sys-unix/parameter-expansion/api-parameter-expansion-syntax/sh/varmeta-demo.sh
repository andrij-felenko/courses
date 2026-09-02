#!/usr/bin/env bash
# Оператори трансформації ${var@op} у роботі: @Q, @E, @A, @a, @k.
# Запуск: ./varmeta-demo.sh
set -uo pipefail

source "${BASH_SOURCE[0]%/*}/lib/varmeta.sh"

if ! varmeta_supported; then
    printf 'Потрібен Bash 4.4+, маємо %s\n' "$BASH_VERSION" >&2
    exit 1
fi

# Глобальна змінна демонстрації: readonly + export одним оголошенням.
declare -rx SYS_UUID="abcd-1234"
declare -i CALC_LIMIT=1024
declare CFG_HOST="127.0.0.1"
declare CFG_PORT=""

# 1. @Q — захист від командної ін'єкції при генерації коду для eval чи ssh.
demo_quoting() {
    local untrusted='filename.txt; rm -rf /'
    local remote_script="process_file ${untrusted@Q}"
    printf 'Q: %s\n' "$remote_script"

    # Перевіряємо результат: після повторного розбору мусить лишитися
    # рівно два слова, а не команда з крапкою з комою всередині.
    local -a words=()
    eval "words=($remote_script)"
    printf 'Q: слів після eval: %d, друге = %s\n' "${#words[@]}" "${words[1]}"
}

# 2. @E — розгортання escape-послідовностей зворотного слеша.
demo_escapes() {
    local raw='Server\tStatus\nNode-1\tONLINE'
    printf 'E:\n%s\n' "${raw@E}"
}

# 3. @A — серіалізація стану змінної з атрибутами й відновлення через eval.
demo_serialization() {
    declare -A db_config=([host]="10.0.0.1" [port]="5432" [name]="production")
    local state="${db_config@A}"
    printf 'A: %s\n' "$state"

    unset -v db_config
    eval "$state"
    printf 'A: після відновлення port=%s\n' "${db_config[port]}"
}

# 4. @a — опитування бітового поля атрибутів у таблиці символів.
demo_attributes() {
    printf 'a: SYS_UUID -> %s\n' "$(var_attributes SYS_UUID)"
    printf 'a: CALC_LIMIT -> %s\n' "$(var_attributes CALC_LIMIT)"

    if is_readonly_var SYS_UUID; then
        printf 'a: SYS_UUID захищено прапорцем readonly, мутувати не будемо\n'
    fi
    if is_integer_var CALC_LIMIT; then
        printf 'a: CALC_LIMIT має арифметичний тип\n'
    fi

    # Дефолти проставляються лише туди, де порожньо, і лише де це дозволено.
    safe_set_default CFG_PORT "8080"
    safe_set_default CFG_HOST "0.0.0.0"
    safe_set_default SYS_UUID "підмінений" \
        || printf 'a: SYS_UUID не змінено (readonly), значення лишилось %s\n' "$SYS_UUID"
    printf 'a: CFG_HOST=%s CFG_PORT=%s\n' "$CFG_HOST" "$CFG_PORT"

    printf 'a: змінні з префіксом CFG_:\n'
    vars_with_prefix CFG_
}

# 5. @k — сплющення асоціативного масиву в черговані пари ключ-значення.
demo_kv_pairs() {
    if (( BASH_VERSINFO[0] > 5 || (BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 1) )); then
        declare -A http_headers=(
            [Content-Type]="application/json"
            [Authorization]="Bearer token123"
        )
        local entry
        for entry in "${http_headers[@]@k}"; do
            printf 'k: %s\n' "$entry"
        done
    else
        printf 'k: оператор @k потребує Bash 5.1+, пропущено\n' >&2
    fi
}

main() {
    demo_quoting
    demo_escapes
    demo_serialization
    demo_attributes
    demo_kv_pairs
}

main "$@"
