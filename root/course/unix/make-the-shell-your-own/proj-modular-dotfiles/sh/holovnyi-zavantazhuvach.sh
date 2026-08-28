# ~/.bashrc — Точка входу інтерактивної оболонки Bash

# 1. Захист: якщо сеанс не інтерактивний, негайно завершуємо роботу
case $- in
    *i*) ;;
      *) return;;
esac

# 2. Визначення шляху до модулів згідно з XDG
DOTFILES_BASH_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/bash"

# 3. Завантаження всіх чинних модулів у строгому числовому порядку
if [ -d "$DOTFILES_BASH_DIR" ]; then
    for module in "$DOTFILES_BASH_DIR"/[0-9][0-9]-*.bash; do
        if [ -r "$module" ]; then
            # Завантаження модуля через вбудовану команду source (.)
            # shellcheck source=/dev/null
            . "$module"
        fi
    done
    unset module
fi

# 4. Локальний файл перевизначень (не під версійним контролем)
if [ -r "$DOTFILES_BASH_DIR/99-local.bash" ]; then
    # shellcheck source=/dev/null
    . "$DOTFILES_BASH_DIR/99-local.bash"
fi
