# Zsh: декларативний опис синтаксису через _arguments
#compdef mycmd

_mycmd_zsh() {
    _arguments -s -S \
        '(-h --help)'{-h,--help}'[Показати довідку]' \
        '(-o --output)'{-o,--output}'[Шлях до файлу звіту]:файл виводу:_files' \
        '(-l --level)'{-l,--level}'[Рівень логування]:рівень:(debug info warn error)' \
        '*:вхідні файли:_files -g "*.log"'
}
_mycmd_zsh "$@"
