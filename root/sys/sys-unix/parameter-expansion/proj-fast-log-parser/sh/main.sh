#!/usr/bin/env bash
set -euo pipefail

# Функція токенізації рядка параметрів URI (query string)
# Використовує посилання за ім'ям (nameref) для заповнення асоціативного масиву
parse_query_params() {
    local query="${1:-}"
    declare -n out_map="$2"
    out_map=()

    [[ -z "$query" ]] && return 0

    local pair key value
    while [[ -n "$query" ]]; do
        # Виділяємо першу пару до роздільника '&'
        pair="${query%%&*}"
        
        # Обрізаємо виділену пару з вихідного рядка query
        if [[ "$query" == *"&"* ]]; then
            query="${query#*&}"
        else
            query=""
        fi

        # Розділяємо пару на ключ і значення по першому '='
        if [[ "$pair" == *"="* ]]; then
            key="${pair%%=*}"
            value="${pair#*=}"
        else
            key="$pair"
            value=""
        fi

        # Заміна URL-кодованих плюсів на пробіли
        value="${value//+/ }"
        
        # Заміна базових шістнадцяткових escape-послідовностей
        value="${value//%20/ }"
        value="${value//%2F//}"
        value="${value//%3A/:}"

        out_map["$key"]="$value"
    done
}

# Функція деконструкції окремого рядка журналу доступу
parse_log_entry() {
    local line="$1"

    # 1. Виділення IP-адреси (все до першого пробілу)
    local ip="${line%% *}"
    local rest="${line#* }"

    # 2. Виділення часової мітки з квадратних дужок
    local timestamp="${rest#*\[}"
    timestamp="${timestamp%%\]*}"
    rest="${rest#*\] \"}"

    # 3. Виділення HTTP-запиту з подвійних лапок
    local request="${rest%%\"*}"
    rest="${rest#*\" }"

    # Розбиття запиту на метод, URI та протокол
    local method="${request%% *}"
    local req_tail="${request#* }"
    local uri="${req_tail% *}"
    local proto="${req_tail##* }"

    # 4. Деконструкція URI
    local raw_path="${uri%%\?*}"
    local query_string=""
    if [[ "$uri" == *"\?"* ]]; then
        query_string="${uri#*\?}"
    fi

    # Виділення каталогу та файлу (ідіоми dirname та basename)
    local dir_path="${raw_path%/*}"
    dir_path="${dir_path:-/}"
    local filename="${raw_path##*/}"
    
    local file_ext=""
    if [[ "$filename" == *"."* ]]; then
        file_ext="${filename##*.}"
    fi

    # 5. Виділення HTTP-статусу та кількості байтів
    local status="${rest%% *}"
    rest="${rest#* }"
    local body_bytes="${rest%% *}"

    # Вивід результатів аналізу
    echo "--------------------------------------------------"
    echo "Клієнт:     $ip"
    echo "Час:        $timestamp"
    echo "Метод:      $method"
    echo "Протокол:   $proto"
    echo "Шлях:       $raw_path"
    echo "Каталог:    $dir_path"
    echo "Файл:       $filename (тип: ${file_ext:-none})"
    echo "Статус:     $status (${body_bytes} байтів)"

    # Обробка параметрів запиту, якщо вони присутні
    if [[ -n "$query_string" ]]; then
        declare -A query_params
        parse_query_params "$query_string" query_params
        echo "Параметри запиту:"
        for k in "${!query_params[@]}"; do
            echo "  * $k => ${query_params[$k]}"
        done
    fi
}

# Демонстраційний запуск на тестовому записі
test_line='192.168.1.105 - - [25/Aug/2026:14:32:10 +0300] "GET /api/v2/telemetry/sensors.json?device_id=node-42&interval=5s&format=raw HTTP/1.1" 200 4096 "https://dashboard.internal/overview" "Agent/3.1" 0.012'
parse_log_entry "$test_line"
