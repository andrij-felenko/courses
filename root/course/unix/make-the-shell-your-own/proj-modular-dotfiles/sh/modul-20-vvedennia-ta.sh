# ~/.config/bash/20-readline.bash — Налаштування введення й поведінки оболонки

# Увімкнення розширених опцій Bash
shopt -s checkwinsize       # Автооновлення розмірів рядків/колонок після SIGWINCH
shopt -s globstar           # Рекурсивний глоб через **
shopt -s nocaseglob         # Регістронезалежний пошук файлів за масками
shopt -s cdspell            # Автоматичне виправлення дрібних одруківок у cd

# Префіксний пошук команд за вже набраним початком (Up / Down)
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# Навігація словами через Ctrl + Стрілки
bind '"\e[1;5C": forward-word'
bind '"\e[1;5D": backward-word'

# Встановлення власного шляху до inputrc, якщо він розміщений у XDG
if [ -r "${XDG_CONFIG_HOME}/readline/inputrc" ]; then
    export INPUTRC="${XDG_CONFIG_HOME}/readline/inputrc"
fi
