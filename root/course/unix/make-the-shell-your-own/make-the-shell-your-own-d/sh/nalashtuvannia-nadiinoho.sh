# 1. Збільшення розміру буфера пам'яті та дискового файлу
export HISTSIZE=50000
export HISTFILESIZE=100000

# 2. Перемикання з режиму перезапису на режим дописування (O_APPEND)
shopt -s histappend

# 3. Багаторядкові команди зберігаються як один запис історії
shopt -s cmdhist

# 4. Фіксація часових міток виконання (РРРР-ММ-ДД ГГ:ХХ:СС)
export HISTTIMEFORMAT="%F %T "

# 5. Керування дублікатами та чутливими даними
export HISTCONTROL="ignoreboth:erasedups"

# 6. Ігнорування тривіальних та навігаційних команд
export HISTIGNORE="ls:ll:la:cd:pwd:exit:history:clear:bg:fg"
