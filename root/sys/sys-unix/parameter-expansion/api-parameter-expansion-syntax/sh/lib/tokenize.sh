#!/usr/bin/env bash
# Ітеративний токенізатор рядка за роздільником-літералом.
#
# Ніякої рекурсії: рядок вкорочується самими підстановками, тож глибина
# C-стека інтерпретатора лишається сталою (один фрейм) незалежно від того,
# скільки в потоці токенів — десять чи мільйон.

# tokenize_stream_iterative <потік> <роздільник> <назва_колбека>
# Колбек викликається на кожен НЕПОРОЖНІЙ токен у порядку появи.
# Повертає 0, якщо потік розібрано; 2 — помилка аргументів; код колбека,
# якщо той сам сигналізує про відмову.
tokenize_stream_iterative() {
    local stream=$1
    local delimiter=$2
    local callback=$3
    local token status

    if [[ -z $delimiter ]]; then
        printf 'tokenize: порожній роздільник\n' >&2
        return 2
    fi
    if ! declare -F "$callback" >/dev/null; then
        printf 'tokenize: невідомий колбек: %s\n' "$callback" >&2
        return 2
    fi

    while [[ -n $stream ]]; do
        if [[ $stream == *"$delimiter"* ]]; then
            # Роздільник узято в лапки: інакше символи *, ? і [ у ньому
            # стали б glob-маскою і зіставили б зовсім інше місце рядка.
            token=${stream%%"$delimiter"*}
            stream=${stream#*"$delimiter"}
        else
            token=$stream
            stream=""
        fi

        if [[ -n $token ]]; then
            # Свідомо через if, а не `[[ ... ]] && cb`: остання команда тіла
            # циклу задає код завершення while, і хибний тест на порожньому
            # токені перетворив би успішний розбір на помилку.
            "$callback" "$token" || {
                status=$?
                printf 'tokenize: колбек %s відмовив на токені: %s\n' "$callback" "$token" >&2
                return "$status"
            }
        fi
    done

    return 0
}
