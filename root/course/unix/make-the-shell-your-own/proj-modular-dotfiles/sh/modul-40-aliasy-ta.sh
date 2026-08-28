# ~/.config/bash/40-aliases.bash — Аліаси та захист від випадкового знищення даних

# Автоматичне підсвічування виводу базових утиліт
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias diff='diff --color=auto'
fi

# Зручні списки файлів
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Захист від ненавмисного перезапису або видалення
alias cp='cp -iv'
alias mv='mv -iv'
alias rm='rm -I --preserve-root'

# Навігаційні скорочення
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Утилітарні скорочення
alias df='df -h'
alias du='du -h'
alias free='free -m'
