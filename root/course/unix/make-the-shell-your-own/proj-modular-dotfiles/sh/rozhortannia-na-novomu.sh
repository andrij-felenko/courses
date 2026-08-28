# 1. Клонування сховища у вигляді голого репозиторію
git clone --bare git@github.com:username/dotfiles.git "$HOME/.dotfiles"

# 2. Тимчасове оголошення аліаса для виконання початкового налаштування
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# 3. Створення резервної копії стандартних файлів дистрибутива, якщо вони існують
mkdir -p "$HOME/.dotfiles-backup"
dotfiles checkout 2>&1 | grep -E "^\s+\." | awk '{print $1}' | while read -r file; do
    mkdir -p "$HOME/.dotfiles-backup/$(dirname "$file")"
    mv "$HOME/$file" "$HOME/.dotfiles-backup/$file"
done

# 4. Застосування файлів із репозиторію
dotfiles checkout

# 5. Вимкнення відображення сторонніх файлів домашнього каталогу
dotfiles config --local status.showUntrackedFiles no
