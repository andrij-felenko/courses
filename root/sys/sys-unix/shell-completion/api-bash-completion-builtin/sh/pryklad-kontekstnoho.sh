_custom_kv_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ "$cur" == *=* ]]; then
        # Праворуч від '=': доповнюємо шляхи до файлів, блокуємо зайвий пропуск
        compopt -o filenames -o nospace
        COMPREPLY=( $(compgen -f -- "${cur#*=}") )
    else
        # Ліворуч від '=': пропонуємо назви ключів із додаванням знака '='
        compopt -o nospace
        COMPREPLY=( $(compgen -W "host= port= timeout= cert=" -- "$cur") )
    fi
}
