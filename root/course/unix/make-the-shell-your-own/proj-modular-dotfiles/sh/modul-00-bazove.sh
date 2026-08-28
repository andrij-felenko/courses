# ~/.config/bash/00-env.bash — Базові змінні середовища та шляхи

# Стандартизація базових каталогів XDG
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Базові утиліти взаємодії
export EDITOR="vim"
export VISUAL="vim"
export PAGER="less"
export LESS="-R -F -X"

# Безпечне додавання локальних шляхів до PATH без дублювання
_add_to_path() {
    local target="$1"
    if [ -d "$target" ] && [[ ":$PATH:" != *":$target:"* ]]; then
        export PATH="$target:$PATH"
    fi
}

_add_to_path "$HOME/.local/bin"
_add_to_path "$HOME/bin"
_add_to_path "$HOME/.cargo/bin"

unset -f _add_to_path
