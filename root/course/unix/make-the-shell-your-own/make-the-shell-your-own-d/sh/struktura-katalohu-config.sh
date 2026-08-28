# ~/.bashrc — Легковага точка входу

# Якщо сеанс не інтерактивний — виходимо
case $- in
    *i*) ;;
      *) return;;
esac

DOTFILES_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/bash"

# Завантаження модулів у числовому порядку
if [ -d "$DOTFILES_DIR" ]; then
    for mod in "$DOTFILES_DIR"/[0-9][0-9]-*.bash; do
        [ -r "$mod" ] && . "$mod"
    done
    unset mod
fi

# Підключення локальних налаштувань за наявності
[ -r "$DOTFILES_DIR/99-local.bash" ] && . "$DOTFILES_DIR/99-local.bash"
