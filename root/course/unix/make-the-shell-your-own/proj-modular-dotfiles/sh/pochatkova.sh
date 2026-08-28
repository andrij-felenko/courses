# 1. Створення голого сховища Git у прихованому каталозі
git init --bare "$HOME/.dotfiles"

# 2. Оголошення спеціального аліаса для роботи з dotfiles
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# 3. Вимкнення відображення невідстежуваних файлів у звітах статусу
dotfiles config --local status.showUntrackedFiles no

# 4. Додавання створених модулів конфігурації
dotfiles add ~/.bashrc
dotfiles add ~/.config/bash/
dotfiles commit -m "feat: початкова ініціалізація модульних dotfiles"

# 5. Підключення віддаленого репозиторію на GitHub або GitLab
dotfiles remote add origin git@github.com:username/dotfiles.git
dotfiles branch -M main
dotfiles push -u origin main
