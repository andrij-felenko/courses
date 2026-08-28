   # Створення голого репозиторію в прихованому каталозі
   git init --bare "$HOME/.dotfiles"

   # Створення зручного аліаса для керування
   alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

   # Критично: приховування сторонніх невідстежуваних файлів з домашнього каталогу
   dotfiles config --local status.showUntrackedFiles no

   # Додавання конфігурацій і створення першого коміту
   dotfiles add ~/.bashrc ~/.config/bash/ ~/.inputrc
   dotfiles commit -m "feat: модульна структура dotfiles"
