# ⚙️ Модульний каркас конфігурації оболонки та версіонування dotfiles

З часом конфігураційні файли оболонки перетворюються на хаотичний монолітний скрипт на сотні або тисячі рядків, де змінні оточення перемішані з аліасами, секретами, функціями та специфічними налаштуваннями окремих серверів. Будь-яка помилка в такому файлі блокує запуск оболонки, а синхронізація між різними машинами призводить до конфліктів.

Цей проект надає завершений, перевірений на практиці каркас модульної організації конфігураційних файлів (`dotfiles`) з ізоляцією функціональних блоків, захистом від рекурсивного завантаження та механізмом безконфліктного версіонування через Git Bare Repository.

## Архітектурний розподіл каталогів та стандарти XDG

Історично програми Unix розміщували свої конфігурації безпосередньо в корені домашнього каталогу користувача у вигляді прихованих файлів (`~/.bashrc`, `~/.vimrc`, `~/.gitconfig`). З часом це призводило до засмічення каталогу `$HOME` десятками файлів різного призначення.

Сучасний стандарт XDG Base Directory чітко розмежовує типи даних за чотирма категоріями:
- Конфігурація (`$XDG_CONFIG_HOME`, дефолт: `~/.config`) — статичні налаштування, які можна безпечно версіонувати в Git.
- Дані застосунків (`$XDG_DATA_HOME`, дефолт: `~/.local/share`) — довговічні робочі файли, бази даних, плагіни.
- Стан сеансу (`$XDG_STATE_HOME`, дефолт: `~/.local/state`) — файли історії команд, логи, збережені позиції курсора.
- Кеш (`$XDG_CACHE_HOME`, дефолт: `~/.cache`) — тимчасові файли, які можна безболісно видалити без втрати працездатності.

У запропонованому каркасі використовується такий розподіл файлів:
- `~/.bashrc` — мінімальна точка входу, яка перевіряє інтерактивність сеансу та ітерує по каталогу модулів.
- `~/.config/bash/` — каталог незалежних скриптів конфігурації з числовими префіксами пріоритету виконання (`00-env.bash`, `10-history.bash` тощо).
- `~/.config/bash/99-local.bash` — ізольований файл для специфічних локальних параметрів конкретного комп'ютера, який додається до `.gitignore` і ніколи не потрапляє у віддалений Git-репозиторій.

## Головний завантажувач ~/.bashrc

Головний файл конфігурації має бути максимально лаконічним. Його єдина мета — безпечно завантажити модулі у визначеному порядку.

Критично важливим є захист від виконання в неінтерактивних сеансах. Коли віддалений клієнт виконує команду через SSH без виділення TTY (наприклад, `ssh server 'cat /etc/os-release'` або протоколи SCP/SFTP), оболонка запускається в неінтерактивному режимі. Якщо в цей момент `.bashrc` спробує надрукувати будь-який текст або ініціалізувати промпт, протокол SFTP зламається з помилкою збою синхронізації пакетів.

```bash
# ~/.bashrc — Точка входу інтерактивної оболонки Bash

# 1. Захист: якщо сеанс не інтерактивний, негайно завершуємо роботу
case $- in
    *i*) ;;
      *) return;;
esac

# 2. Визначення шляху до модулів згідно з XDG
DOTFILES_BASH_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/bash"

# 3. Завантаження всіх чинних модулів у строгому числовому порядку
if [ -d "$DOTFILES_BASH_DIR" ]; then
    for module in "$DOTFILES_BASH_DIR"/[0-9][0-9]-*.bash; do
        if [ -r "$module" ]; then
            # Завантаження модуля через вбудовану команду source (.)
            # shellcheck source=/dev/null
            . "$module"
        fi
    done
    unset module
fi

# 4. Локальний файл перевизначень (не під версійним контролем)
if [ -r "$DOTFILES_BASH_DIR/99-local.bash" ]; then
    # shellcheck source=/dev/null
    . "$DOTFILES_BASH_DIR/99-local.bash"
fi
```

## Модуль 00: Базове середовище (00-env.bash)

Цей модуль експортує глобальні змінні середовища та налаштовує шляхи пошуку виконуваних файлів `$PATH`.

Зверніть увагу на функцію `_add_to_path`. Вона перевіряє, чи існує цільовий каталог на диску, і чи не присутній він уже в змінній `$PATH`. Це запобігає розростанню рядка шляхів при багаторазовому відкритті вкладених підоболонок. Наприкінці файлу допоміжна функція видаляється через `unset -f`, щоб не засмічувати простір імен оболонки.

```bash
# ~/.config/bash/00-env.bash — Базові змінні середовища та шляхи

# Стандартизація базових каталогів XDG
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Базові утиліти взаємодії
export EDITOR="vim"
export VISUAL="vim"
export PAGER="less"
export LESS="-R -F -X"

# Безпечне додавання локальних шляхів до PATH без дублювання
_add_to_path() {
    local target="$1"
    if [ -d "$target" ] && [[ ":$PATH:" != *":$target:"* ]]; then
        export PATH="$target:$PATH"
    fi
}

_add_to_path "$HOME/.local/bin"
_add_to_path "$HOME/bin"
_add_to_path "$HOME/.cargo/bin"

unset -f _add_to_path
```

## Модуль 10: Керування історією (10-history.bash)

Модуль вирішує проблему втрати історії команд при роботі з багатьма термінальними вікнами одночасно.

Опція `shopt -s histappend` перемикає оболонку з режиму перезапису файлу на режим дописування в кінець. Спеціальна функція `_history_sync` виконує три послідовні дії:
1. `history -a` — скидає нові виконані команди з оперативної пам'яті в кінець дискового файлу.
2. `history -c` — очищає буфер пам'яті поточного процесу Bash.
3. `history -r` — перечитує весь оновлений дисковий файл у пам'ять.

Функція підключається до системного хука `PROMPT_COMMAND`, який викликається ядром Bash перед кожним відображенням рядка підказки.

```bash
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
```

## Модуль 20: Введення та Readline (20-readline.bash)

Налаштовує розширені можливості парсера Bash та пов'язує гарячі клавіші для інтерактивної роботи.

Опція `checkwinsize` змушує Bash перевіряти розмір вікна термінала після виконання кожної зовнішньої команди та оновлювати змінні `$LINES` і `$COLUMNS` при отриманні сигналу `SIGWINCH`. Опція `globstar` вмикає підтримку рекурсивного глобінгу через синтаксис `**/*.txt`.

```bash
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
```

## Модуль 30: Рядок підказки (30-prompt.bash)

Формує інформативний дворядковий промпт із відображенням активної гілки Git, статусу незафіксованих змін та коду повернення останньої команди.

Усі кольорові послідовності ANSI обов'язково обгортаються в маркери `\[` та `\]`. Це сигналізує бібліотеці Readline, що байти ескейп-кодів мають нульову видиму ширину на екрані, запобігаючи спотворенню переносу рядків під час набору довгого тексту.

```bash
# ~/.config/bash/30-prompt.bash — Інформативний дворядковий промпт із захистом ширини

# Якщо встановлено Starship — використовуємо його як основний генератор
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
    return
fi

# Функція визначення активної гілки Git
_git_prompt_info() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        local dirty=""
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            dirty="*"
        fi
        printf " (%s%s)" "$branch" "$dirty"
    fi
}

# Генератор дворядкового промпта
_render_custom_prompt() {
    local last_exit="$?"
    local exit_indicator=""
    
    # Індикатор коду виходу попередньої команди
    if [ "$last_exit" -ne 0 ]; then
        exit_indicator="\[\033[01;31m\][✘ $last_exit]\[\033[00m\] "
    fi

    local c_user="\[\033[01;32m\]"
    local c_host="\[\033[01;34m\]"
    local c_path="\[\033[01;33m\]"
    local c_git="\[\033[01;35m\]"
    local c_reset="\[\033[00m\]"

    # Якщо користувач root — виділяємо червоним
    if [ "$EUID" -eq 0 ]; then
        c_user="\[\033[01;31m\]"
    fi

    local git_str
    git_str=$(_git_prompt_info)

    # Дворядкова структура:
    # [✘ 1] user@host ~/projects/app (main*)
    # $ 
    PS1="${exit_indicator}${c_user}\u${c_reset}@${c_host}\h${c_reset}:${c_path}\w${c_reset}${c_git}${git_str}${c_reset}\n\\$ "
}

# Додавання генератора до ланцюга PROMPT_COMMAND
if [[ "$PROMPT_COMMAND" != *"_render_custom_prompt"* ]]; then
    PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }_render_custom_prompt"
fi
```

## Модуль 40: Аліаси та безпечні прапорці (40-aliases.bash)

Містить скорочення для повсякденних команд та захисні прапорці для утиліт маніпуляції файлами.

Прапорець `-i` змушує утиліти `cp` та `mv` запитувати підтвердження перед перезаписом існуючого файлу. Прапорець `--preserve-root` для утиліти `rm` блокує випадкове рекурсивне видалення кореневого каталогу системи.

```bash
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
```

## Модуль 50: Корисні функції оболонки (50-functions.bash)

Функції відрізняються від аліасів тим, що підтримують логічні розгалуження, обробку позиційних параметрів (`$1`, `$2`) та виконання ланцюгів дій.

- `mkcd` — створює дерево каталогів за допомогою `mkdir -p` і негайно переходить у створений каталог через `cd`.
- `up` — дозволяє піднятися на довільну кількість рівнів вгору по дереву каталогів без введення довгих послідовностей `../../..`.
- `extract` — універсальна функція-обгортка, яка аналізує розширення архіву та викликає відповідну системну утиліту розпакування з правильними прапорцями.

```bash
# ~/.config/bash/50-functions.bash — Розширені сценарії та допоміжні утиліти

# Створення каталогу та миттєвий перехід у нього
mkcd() {
    if [ -z "$1" ]; then
        echo "Використання: mkcd <назва_каталогу>" >&2
        return 1
    fi
    mkdir -p "$1" && cd "$1" || return 1
}

# Швидкий підйом на N рівнів вгору по дереву файлової системи
up() {
    local limit="${1:-1}"
    local path=""
    for (( i=1; i<=limit; i++ )); do
        path="../$path"
    done
    cd "$path" || return 1
}

# Універсальний розпакувальник архівів за розширенням файлу
extract() {
    if [ -z "$1" ]; then
        echo "Використання: extract <архів>" >&2
        return 1
    fi
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"     ;;
            *.tar.gz)    tar xzf "$1"     ;;
            *.tar.xz)    tar xJf "$1"     ;;
            *.bz2)       bunzip2 "$1"     ;;
            *.rar)       unrar x "$1"     ;;
            *.gz)        gunzip "$1"      ;;
            *.tar)       tar xf "$1"      ;;
            *.tbz2)      tar xjf "$1"     ;;
            *.tgz)       tar xzf "$1"     ;;
            *.zip)       unzip "$1"       ;;
            *.Z)         uncompress "$1"  ;;
            *.7z)        7z x "$1"        ;;
            *)           echo "Невідомий формат архіву '$1'" >&2; return 1 ;;
        esac
    else
        echo "'$1' не є дійсним файлом" >&2
        return 1
    fi
}
```

## Керування конфігурацією через Git Bare Repository

Традиційний підхід до версіонування конфігураційних файлів полягає у створенні каталогу `~/dotfiles` і подальшому створенні сотень символічних посилань у домашньому каталозі вручну або за допомогою утиліти `GNU Stow`. Цей метод має суттєві недоліки: посилання ламаються при перейменуванні, а сторонні програми часто замінюють симлінки реальними файлами при збереженні конфігурацій.

Найбільш елегантним та надійним підходом є використання «голого» репозиторію Git (`Git Bare Repository`). При такому підході каталог репозиторію (`.git`) зберігається ізольовано у прихованій теці `~/.dotfiles`, а робочим деревом (`work-tree`) оголошується безпосередньо домашній каталог `$HOME`.

### Початкова ініціалізація на головному комп'ютері

Під час початкового налаштування репозиторію критично важливо вимкнути відображення невідстежуваних файлів. Оскільки робочим деревом є `$HOME`, за замовчуванням команда `git status` виводитиме тисячі файлів із завантажень, робочого столу та кешу.

```bash
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
```

### Розгортання на новому сервері або чистій системі

Під час клонування конфігурації на нову машину типовою проблемою є наявність дефолтних файлів `~/.bashrc` та `~/.profile`, створених дистрибутивом при створенні користувача. Пряма команда `checkout` завершиться помилкою через конфлікт існуючих файлів.

Нижче наведено автоматизований скрипт розгортання, який створює резервну копію конфліктуючих дефолтних файлів перед застосуванням конфігурації з репозиторію:

```bash
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
```
