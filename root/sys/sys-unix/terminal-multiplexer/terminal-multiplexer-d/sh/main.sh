#!/bin/sh
# Автоматичне розгортання середовища розробки
SESSION="project-alpha"

# Створення сеансу у фоні (-d) з назвою першого вікна 'editor'
tmux new-session -d -s "$SESSION" -n 'editor'

# Запуск редактора у першій панелі
tmux send-keys -t "$SESSION:editor.0" 'nvim src/main.rs' C-m

# Розбиття вікна по горизонталі (нижня панель 30% висоти)
tmux split-window -v -p 30 -t "$SESSION:editor"

# Запуск спостереження за компіляцією у нижній панелі
tmux send-keys -t "$SESSION:editor.1" 'cargo watch -x check' C-m

# Створення другого вікна для моніторингу системи
tmux new-window -t "$SESSION" -n 'system'
tmux send-keys -t "$SESSION:system" 'htop' C-m

# Підключення до готового сеансу
tmux attach-session -t "$SESSION"
