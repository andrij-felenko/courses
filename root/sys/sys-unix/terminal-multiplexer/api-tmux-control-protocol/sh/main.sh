# Створення спільного каталогу з правами групи
mkdir -p /var/tmux-shared
chgrp devteam /var/tmux-shared
chmod 2775 /var/tmux-shared

# Запуск сервера на спільному сокеті
tmux -S /var/tmux-shared/pairing-socket new-session -s shared-dev

# Підключення іншого користувача з групи devteam:
tmux -S /var/tmux-shared/pairing-socket attach-session -t shared-dev
