# ~/.config/bash/10-history.bash — Синхронізація та надійне збереження історії

# Ліміти пам'яті та дискового файлу
export HISTSIZE=50000
export HISTFILESIZE=100000

# Шлях до файлу історії згідно з XDG State
export HISTFILE="${XDG_STATE_HOME}/bash/history"
mkdir -p "$(dirname "$HISTFILE")" 2>/dev/null

# Формат часу для кожної команди (РРРР-ММ-ДД ГГ:ХХ:СС)
export HISTTIMEFORMAT="%F %T "

# Фільтрація дублікатів і команд із початковим пробілом
export HISTCONTROL="ignoreboth:erasedups"

# Ігнорування рутинних дрібних команд
export HISTIGNORE="ls:ll:la:cd:pwd:exit:history:clear:bg:fg"

# Дописування у файл замість перезапису при виході
shopt -s histappend
shopt -s cmdhist

# Синхронізація історії між паралельними терміналами перед кожним промптом
_history_sync() {
    builtin history -a
    builtin history -c
    builtin history -r
}

# Безпечне додавання функції до PROMPT_COMMAND
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_history_sync"
elif [[ "$PROMPT_COMMAND" != *"_history_sync"* ]]; then
    PROMPT_COMMAND="_history_sync; $PROMPT_COMMAND"
fi
