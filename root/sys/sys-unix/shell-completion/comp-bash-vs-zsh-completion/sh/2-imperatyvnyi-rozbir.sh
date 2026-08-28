# Bash: ручна перевірка контексту через індексацію слів
_mycmd_bash() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "$prev" in
        -o|--output)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
        -l|--level)
            COMPREPLY=( $(compgen -W "debug info warn error" -- "$cur") )
            return 0
            ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $(compgen -W "-o --output -l --level -h --help" -- "$cur") )
    fi
}
complete -F _mycmd_bash mycmd
