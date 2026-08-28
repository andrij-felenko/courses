# ~/.config/bash/30-prompt.bash

_git_branch() {
    local ref
    ref=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -n "$ref" ]; then
        local dirty=""
        # Перевірка наявності не зафіксованих змін
        [ -n "$(git status --porcelain 2>/dev/null)" ] && dirty="*"
        printf " \[\033[35m\](%s%s)\[\033[0m\]" "$ref" "$dirty"
    fi
}

_build_prompt() {
    local exit_code="$?"
    local prompt_color="\[\033[32m\]"
    local exit_str=""

    # Якщо попередня команда завершилась із помилкою — показуємо код
    if [ "$exit_code" -ne 0 ]; then
        exit_str="\[\033[31m\][✘ $exit_code]\[\033[0m\] "
    fi

    # Виділення користувача root червоним кольором
    [ "$EUID" -eq 0 ] && prompt_color="\[\033[31m\]"

    # OSC 0 для оновлення заголовка вікна термінала
    local title_seq="\[\033]0;\u@\h: \w\007\]"

    PS1="${title_seq}${exit_str}${prompt_color}\u@\h\[\033[0m\]:\[\033[34m\]\w\[\033[0m\]$(_git_branch)\n\\$ "
}

PROMPT_COMMAND="_build_prompt; ${PROMPT_COMMAND:-}"
