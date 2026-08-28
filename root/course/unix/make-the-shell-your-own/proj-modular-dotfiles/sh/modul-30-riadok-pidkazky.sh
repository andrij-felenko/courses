# ~/.config/bash/30-prompt.bash — Інформативний дворядковий промпт із захистом ширини

# Якщо встановлено Starship — використовуємо його як основний генератор
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
    return
fi

# Функція визначення активної гілки Git
_git_prompt_info() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        local dirty=""
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            dirty="*"
        fi
        printf " (%s%s)" "$branch" "$dirty"
    fi
}

# Генератор дворядкового промпта
_render_custom_prompt() {
    local last_exit="$?"
    local exit_indicator=""
    
    # Індикатор коду виходу попередньої команди
    if [ "$last_exit" -ne 0 ]; then
        exit_indicator="\[\033[01;31m\][✘ $last_exit]\[\033[00m\] "
    fi

    local c_user="\[\033[01;32m\]"
    local c_host="\[\033[01;34m\]"
    local c_path="\[\033[01;33m\]"
    local c_git="\[\033[01;35m\]"
    local c_reset="\[\033[00m\]"

    # Якщо користувач root — виділяємо червоним
    if [ "$EUID" -eq 0 ]; then
        c_user="\[\033[01;31m\]"
    fi

    local git_str
    git_str=$(_git_prompt_info)

    # Дворядкова структура:
    # [✘ 1] user@host ~/projects/app (main*)
    # $ 
    PS1="${exit_indicator}${c_user}\u${c_reset}@${c_host}\h${c_reset}:${c_path}\w${c_reset}${c_git}${git_str}${c_reset}\n\\$ "
}

# Додавання генератора до ланцюга PROMPT_COMMAND
if [[ "$PROMPT_COMMAND" != *"_render_custom_prompt"* ]]; then
    PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }_render_custom_prompt"
fi
