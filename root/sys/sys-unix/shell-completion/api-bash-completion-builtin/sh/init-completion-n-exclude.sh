_mytool() {
    local cur prev words cword
    _init_completion -n ":=" || return

    case "$prev" in
        --config)
            _filedir "yaml|json"
            return
            ;;
        --port)
            COMPREPLY=( $(compgen -W "80 443 8080 8443" -- "$cur") )
            return
            ;;
    esac
}
