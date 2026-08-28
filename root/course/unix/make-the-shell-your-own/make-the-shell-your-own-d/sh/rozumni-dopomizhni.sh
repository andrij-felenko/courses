# Швидкий підйом на N рівнів вгору по дереву каталогів: up 3 -> cd ../../..
up() {
    local levels="${1:-1}"
    local target=""
    for (( i=0; i<levels; i++ )); do
        target="../$target"
    done
    cd "$target" || return 1
}

# Універсальний розпакувальник архівів за їхнім магічним розширенням
extract() {
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
