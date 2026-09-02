#!/usr/bin/env bash
# Інтроспекція таблиці символів: ${var@a}, ${var@Q}, ${var@A} і непряме
# читання ${!name}. Оператори @ потребують Bash 4.4+, тож модуль перевіряє
# версію й каже про це чесно, а не мовчки повертає порожнечу.
#
# Усі локальні змінні мають довгий префікс __varmeta_. Причина не в стилі:
# непряме розгортання розв'язується в ДИНАМІЧНІЙ області видимості, тож
# виклик is_integer_var name із коротким локальним `name` усередині функції
# читав би саму себе, а не змінну викликача.

varmeta_supported() {
    (( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 4) ))
}

# Чи існує змінна (скаляр чи масив) із такою назвою у видимій області.
var_exists() {
    declare -p "$1" >/dev/null 2>&1
}

# Назва мусить бути валідним ідентифікатором: усе інше або зламає
# printf -v, або відкриє дірку для підстановки чужого коду.
# Свідомо через =~, а не через extglob-шаблон *([A-Za-z_0-9]): модуль не
# має права вмикати shopt у чужій оболонці, а без extglob такий шаблон
# мовчки перетворився б на "*" плюс дужки й пропускав би будь-що.
varmeta_valid_name() {
    [[ $1 =~ ^[A-Za-z_][A-Za-z_0-9]*$ ]]
}

# Друкує рядок прапорців атрибутів ("ilrx" тощо); порожньо — атрибутів немає.
# Код 1 — змінної немає, 2 — застара оболонка.
var_attributes() {
    local __varmeta_name=$1
    if ! varmeta_supported; then
        printf 'varmeta: оператор @a потребує Bash 4.4+, маємо %s\n' "$BASH_VERSION" >&2
        return 2
    fi
    var_exists "$__varmeta_name" || return 1
    printf '%s' "${!__varmeta_name@a}"
}

# Предикати читають ${!name@a} напряму, а не через $(var_attributes ...):
# підстановка команди коштувала б fork + pipe на кожну перевірку.
is_integer_var() {
    local __varmeta_name=$1
    varmeta_supported || return 2
    var_exists "$__varmeta_name" || return 1
    [[ ${!__varmeta_name@a} == *i* ]]
}

is_readonly_var() {
    local __varmeta_name=$1
    varmeta_supported || return 2
    var_exists "$__varmeta_name" || return 1
    [[ ${!__varmeta_name@a} == *r* ]]
}

is_array_var() {
    local __varmeta_name=$1
    varmeta_supported || return 2
    var_exists "$__varmeta_name" || return 1
    [[ ${!__varmeta_name@a} == *[aA]* ]]
}

# Записує дефолт, якщо змінна не існує або порожня.
# 0 — значення на місці, 1 — змінна readonly (не чіпали), 2 — погана назва.
safe_set_default() {
    local __varmeta_name=$1
    local __varmeta_default=$2

    if ! varmeta_valid_name "$__varmeta_name"; then
        printf 'varmeta: некоректна назва змінної: %s\n' "$__varmeta_name" >&2
        return 2
    fi

    # Спроба мутувати readonly обірвала б неінтерактивний сценарій, тому
    # питаємо про прапорець ДО запису, а не ловимо помилку після.
    if is_readonly_var "$__varmeta_name"; then
        return 1
    fi

    # ${!name-} з дефолтом: під set -u звичайне ${!name} на неоголошеній
    # змінній завершило б процес із "unbound variable".
    if [[ -z ${!__varmeta_name-} ]]; then
        printf -v "$__varmeta_name" '%s' "$__varmeta_default"
    fi
    return 0
}

# Значення у формі, безпечній для повторного розбору (eval, ssh-командний рядок).
var_quote() {
    local __varmeta_name=$1
    varmeta_supported || return 2
    var_exists "$__varmeta_name" || return 1
    printf '%s' "${!__varmeta_name@Q}"
}

# Повна команда оголошення разом з атрибутами — аналог declare -p.
var_assignment() {
    local __varmeta_name=$1
    varmeta_supported || return 2
    var_exists "$__varmeta_name" || return 1
    printf '%s' "${!__varmeta_name@A}"
}

# Назви всіх змінних із заданим префіксом — по одній у рядок.
#
# Пастка: ${!prefix@} бере префікс ЛІТЕРАЛЬНО з тексту виразу, а не зі
# значення змінної, тож зробити його динамічним можна лише через eval.
# Тому назву префікса спершу валідуємо як ідентифікатор — тоді в eval
# потрапляє рівно те, що ми перевірили, і нічого більше.
vars_with_prefix() {
    local __varmeta_prefix=$1
    local __varmeta_name

    if ! varmeta_valid_name "$__varmeta_prefix"; then
        printf 'varmeta: некоректний префікс: %s\n' "$__varmeta_prefix" >&2
        return 2
    fi

    eval "for __varmeta_name in \${!${__varmeta_prefix}@}; do
              printf '%s\\n' \"\$__varmeta_name\"
          done"
}
