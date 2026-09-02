#!/usr/bin/env bash
# Канонізація шляху та аналоги dirname/basename у пам'яті процесу.
# $(basename "$p") коштує fork + execve + завантаження ELF; ${p##*/} —
# один пошук останнього байта в рядку, що вже лежить у купі оболонки.
# Потрібен Bash 4.3+ (від'ємний індекс у unset).
#
# Функції-перетворювачі пишуть результат через printf -v у змінну, назву
# якої дав викликач: так між ними немає жодного $(...), тобто жодного форку.
# Внутрішні локальні змінні мають префікс __pathutil_, щоб не затінити
# змінну викликача, чию назву нам щойно передали.

# Стискає повторні слеші: /a//b///c -> /a/b/c
path_squeeze_slashes() {
    local __pathutil_out=$1
    local __pathutil_path=$2
    while [[ $__pathutil_path == *//* ]]; do
        __pathutil_path=${__pathutil_path//\/\//\/}
    done
    printf -v "$__pathutil_out" '%s' "$__pathutil_path"
}

# Повна канонізація: стиснення слешів, зняття кінцевого слеша та згортання
# сегментів "." і "..". Файлова система не опитується — це чисто текстова
# операція, тож символьні посилання лишаються нерозв'язаними (як у dirname).
path_canonicalize() {
    local __pathutil_out=$1
    local __pathutil_path=$2
    local __pathutil_seg __pathutil_joined
    local __pathutil_abs=0
    local -a __pathutil_stack=()

    [[ $__pathutil_path == /* ]] && __pathutil_abs=1

    while [[ -n $__pathutil_path ]]; do
        __pathutil_seg=${__pathutil_path%%/*}
        if [[ $__pathutil_path == "$__pathutil_seg" ]]; then
            __pathutil_path=""
        else
            __pathutil_path=${__pathutil_path#*/}
        fi

        case $__pathutil_seg in
            ""|.)
                # Порожній сегмент від "//" та "." нічого не додають.
                ;;
            ..)
                if (( ${#__pathutil_stack[@]} > 0 )) \
                   && [[ ${__pathutil_stack[-1]} != ".." ]]; then
                    unset -v '__pathutil_stack[-1]'
                elif (( __pathutil_abs == 0 )); then
                    # Відносний шлях має право вийти вгору: ../../lib
                    __pathutil_stack+=("..")
                fi
                # Для абсолютного шляху ".." у корені нікуди не веде -> ігноруємо.
                ;;
            *)
                __pathutil_stack+=("$__pathutil_seg")
                ;;
        esac
    done

    local IFS=/
    __pathutil_joined="${__pathutil_stack[*]-}"

    if (( __pathutil_abs )); then
        printf -v "$__pathutil_out" '/%s' "$__pathutil_joined"
    else
        [[ -n $__pathutil_joined ]] || __pathutil_joined="."
        printf -v "$__pathutil_out" '%s' "$__pathutil_joined"
    fi
}

# Каталог: найкоротший суфікс від останнього слеша.
path_dirname() {
    local __pathutil_out=$1
    local __pathutil_clean __pathutil_dir
    path_canonicalize __pathutil_clean "$2"

    if [[ $__pathutil_clean != */* ]]; then
        printf -v "$__pathutil_out" '%s' "."
        return 0
    fi

    __pathutil_dir=${__pathutil_clean%/*}
    # "/etc" -> "" : порожній результат означає корінь.
    printf -v "$__pathutil_out" '%s' "${__pathutil_dir:-/}"
}

# Ім'я файлу: найдовший префікс до останнього слеша.
path_basename() {
    local __pathutil_out=$1
    local __pathutil_clean
    path_canonicalize __pathutil_clean "$2"

    if [[ $__pathutil_clean == / ]]; then
        printf -v "$__pathutil_out" '%s' "/"
        return 0
    fi
    printf -v "$__pathutil_out" '%s' "${__pathutil_clean##*/}"
}

# Друкує три поля розібраного шляху.
canonicalize_path() {
    local path=$1
    local clean dir base

    if [[ -z $path ]]; then
        printf 'path: порожній шлях\n' >&2
        return 1
    fi

    path_canonicalize clean "$path"
    path_dirname dir "$path"
    path_basename base "$path"

    printf 'Dirname:  %s\n' "$dir"
    printf 'Basename: %s\n' "$base"
    printf 'Clean:    %s\n' "$clean"
}
