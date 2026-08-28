# ~/.config/bash/50-functions.bash — Розширені сценарії та допоміжні утиліти

# Створення каталогу та миттєвий перехід у нього
mkcd() {
    if [ -z "$1" ]; then
        echo "Використання: mkcd <назва_каталогу>" >&2
        return 1
    fi
    mkdir -p "$1" && cd "$1" || return 1
}

# Швидкий підйом на N рівнів вгору по дереву файлової системи
up() {
    local limit="${1:-1}"
    local path=""
    for (( i=1; i<=limit; i++ )); do
        path="../$path"
    done
    cd "$path" || return 1
}

# Універсальний розпакувальник архівів за розширенням файлу
extract() {
    if [ -z "$1" ]; then
        echo "Використання: extract <архів>" >&2
        return 1
    fi
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"     ;;
            *.tar.gz)    tar xzf "$1"     ;;
            *.tar.xz)    tar xJf "$1"     ;;
            *.bz2)       bunzip2 "$1"     ;;
            *.rar)       unrar x "$1"     ;;
            *.gz)        gunzip "$1"      ;;
            *.tar)       tar xf "$1"      ;;
            *.tbz2)      tar xjf "$1"     ;;
            *.tgz)       tar xzf "$1"     ;;
            *.zip)       unzip "$1"       ;;
            *.Z)         uncompress "$1"  ;;
            *.7z)        7z x "$1"        ;;
            *)           echo "Невідомий формат архіву '$1'" >&2; return 1 ;;
        esac
    else
        echo "'$1' не є дійсним файлом" >&2
        return 1
    fi
}
