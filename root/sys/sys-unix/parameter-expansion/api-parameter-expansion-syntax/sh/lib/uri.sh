#!/usr/bin/env bash
# Декомпозиція URI (RFC 3986) самими підстановками параметрів.
# Результат — асоціативний масив URI_PARTS: scheme, userinfo, host, port,
# path, query, fragment.
#
# Порядок відрізань не довільний: спершу знімаємо хвіст (fragment, потім
# query), бо вони можуть містити "/", "@" і ":", і лише тоді розбираємо
# authority. Розбір у зворотному порядку розсипався б на першому ж "?".

parse_network_uri() {
    local raw_uri=$1

    if [[ -z $raw_uri ]]; then
        printf 'uri: порожній рядок\n' >&2
        return 1
    fi

    local rest=$raw_uri
    local scheme="" userinfo="" host="" port=""
    local path="" query="" fragment="" after=""

    # Схема: усе до "://"
    if [[ $rest == *://* ]]; then
        scheme=${rest%%://*}
        rest=${rest#*://}
        if [[ -z $scheme ]]; then
            printf 'uri: порожня схема: %s\n' "$raw_uri" >&2
            return 1
        fi
    fi

    # Фрагмент і запит — з кінця рядка.
    if [[ $rest == *\#* ]]; then
        fragment=${rest#*\#}
        rest=${rest%%\#*}
    fi
    if [[ $rest == *\?* ]]; then
        query=${rest#*\?}
        rest=${rest%%\?*}
    fi

    # Шлях: усе від першого "/" після authority.
    if [[ $rest == */* ]]; then
        path=/${rest#*/}
        rest=${rest%%/*}
    fi

    # userinfo відділяє ОСТАННІЙ "@": пароль цілком може містити "@",
    # тому беремо найдовший префікс (%@*), а не найкоротший.
    if [[ $rest == *@* ]]; then
        userinfo=${rest%@*}
        rest=${rest##*@}
    fi

    # Хост: літеральна адреса IPv6 у квадратних дужках або звичайне ім'я.
    # Без окремої гілки двокрапки всередині [::1] розповзлись би на порт.
    if [[ $rest == \[*\]* ]]; then
        host=${rest%%\]*}
        host=${host#\[}
        after=${rest#*\]}
        if [[ $after == :* ]]; then
            port=${after#:}
        elif [[ -n $after ]]; then
            printf 'uri: сміття після адреси IPv6: %s\n' "$after" >&2
            return 1
        fi
    elif [[ $rest == *:* ]]; then
        port=${rest##*:}
        host=${rest%:*}
    else
        host=$rest
    fi

    if [[ -n $port && -n ${port//[0-9]/} ]]; then
        printf 'uri: невалідний порт: %s\n' "$port" >&2
        return 1
    fi
    if [[ -z $host && -z $path ]]; then
        printf 'uri: не знайдено ні хоста, ні шляху: %s\n' "$raw_uri" >&2
        return 1
    fi

    declare -g -A URI_PARTS=()
    URI_PARTS[scheme]=$scheme
    URI_PARTS[userinfo]=$userinfo
    URI_PARTS[host]=$host
    URI_PARTS[port]=$port
    URI_PARTS[path]=$path
    URI_PARTS[query]=$query
    URI_PARTS[fragment]=$fragment

    return 0
}

print_uri_parts() {
    local key
    for key in scheme userinfo host port path query fragment; do
        printf '%-10s%s\n' "$key:" "${URI_PARTS[$key]}"
    done
}
