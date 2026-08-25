# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Карта завантаження конфігураційних файлів ─────────────────────────────
def fig_shell_startup_matrix():
    W, H = 1060, 600
    p = []

    # Верхній блок — вхідна подія
    p.append(fitbox(280, 20, 500, 42,
                    "Подія запуску оболонки: системний виклик execve(2)",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    p.append(arrow(400, 62, 260, 100, color=LINE, sw=1.8))
    p.append(arrow(660, 62, 800, 100, color=LINE, sw=1.8))

    # Ліва колонка: Login Shell
    p.append(fitbox(40, 100, 460, 50,
                    "1. Стартова оболонка сеансу (Login Shell)\n"
                    "Ознака: argv[0][0] == '-' (наприклад, «-bash») або ключ --login / -l\n"
                    "(Консольний логін, SSH-сесія, su - user, логін на macOS)",
                    size=10.5, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    p.append(arrow(270, 150, 270, 180, color=NEG, sw=1.5))

    p.append(fitbox(40, 180, 460, 45,
                    "Глобальний системний профіль: /etc/profile\n"
                    "(і скрипти з теки /etc/profile.d/*.sh)",
                    size=10.5, fill="#fff", stroke=NEG, sw=1.2, color=INK))

    p.append(arrow(270, 225, 270, 255, color=NEG, sw=1.5))

    p.append(fitbox(40, 255, 460, 55,
                    "Перший знайдений користувацький файл (пошук до першого збігу):\n"
                    "1. ~/.bash_profile  →  2. ~/.bash_login  →  3. ~/.profile\n"
                    "⚠️ Читається лише ОДИН із них! Зазвичай підключає ~/.bashrc",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.5, color=INK, bold=True))

    p.append(arrow(270, 310, 270, 340, color=NEG, sw=1.5))

    p.append(fitbox(40, 340, 460, 60,
                    "Завершення сеансу (Login Shell Exit):\n"
                    "Виконуються файли очищення термінала й сеансу:\n"
                    "~/.bash_logout  та  /etc/bash.bash_logout",
                    size=10, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    # Права колонка: Non-Login Interactive Shell
    p.append(fitbox(560, 100, 460, 50,
                    "2. Інтерактивна вторинна оболонка (Non-Login Interactive)\n"
                    "Ознака: argv[0][0] != '-', термінал підключено (isatty(0) == 1)\n"
                    "(Нова вкладка GNOME Terminal / Alacritty, вікно tmux, запуск bash)",
                    size=10.5, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(arrow(790, 150, 790, 180, color=POS, sw=1.5))

    p.append(fitbox(560, 180, 460, 45,
                    "Глобальний системний RC: /etc/bash.bashrc\n"
                    "(у дистрибутивах Debian, Ubuntu та похідних)",
                    size=10.5, fill="#fff", stroke=POS, sw=1.2, color=INK))

    p.append(arrow(790, 225, 790, 255, color=POS, sw=1.5))

    p.append(fitbox(560, 255, 460, 55,
                    "Головний користувацький конфіг: ~/.bashrc\n"
                    "Читається при КОЖНОМУ відкритті нового термінального вікна.\n"
                    "Містить аліаси, функції, промпт $PS1, налаштування історії",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.5, color=INK, bold=True))

    p.append(arrow(790, 310, 790, 340, color=POS, sw=1.5))

    p.append(fitbox(560, 340, 460, 60,
                    "Неінтерактивний запуск сценаріїв (Non-Interactive Script):\n"
                    "Не читає profile і bashrc! Якщо задано змінну $BASH_ENV,\n"
                    "оболонка виконує файл, вказаний у ній, перед запуском коду.",
                    size=10, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    # Нижній синтезний блок: правила розміщення
    p.append(fitbox(40, 430, 460, 140,
                    "Що класти у Profile (~/.profile, ~/.bash_profile):\n"
                    "• Змінні середовища: export PATH, export EDITOR, export LANG\n"
                    "• Одноразова ініціалізація сеансу (umask, ssh-agent)\n\n"
                    "Чому: Змінні успадковуються всіма дочірніми процесами через environ.\n"
                    "Їх непотрібно повторно обчислювати при відкритті кожного вікна!",
                    size=10, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    p.append(fitbox(560, 430, 460, 140,
                    "Що класти у RC (~/.bashrc):\n"
                    "• Аліаси: alias ll='ls -la'\n"
                    "• Функції оболонки та автодоповнення (bash-completion)\n"
                    "• Рядок підказки: PS1, інтеграція Starship, хуки PROMPT_COMMAND\n\n"
                    "Чому: Аліаси та функції НЕ передаються через execve(2) іншим процесам,\n"
                    "тому кожен новий процес інтерактивної оболонки мусить визначити їх заново.",
                    size=10, fill=WARM, stroke=POS, sw=1.5, color=INK))

    render(os.path.join(OUT, "shell-startup-matrix.svg"), W, H, *p,
           title="Карта завантаження конфігураційних файлів оболонки")


# ── 2. Архітектура Readline та розрахунок ширини ──────────────────────────────
def fig_readline_architecture():
    W, H = 1060, 560
    p = []

    # Верхній блок — апаратний потік вводу
    p.append(fitbox(40, 20, 460, 60,
                    "Ввід користувача через TTY-пристрій (клавіатура)\n"
                    "Дисципліна лінії переведена у сирий режим (termios RAW mode):\n"
                    "Посимвольна передача байтів без буферизації рядка ядром",
                    size=10.5, fill=PALE, stroke=LINE, sw=1.5, color=INK))

    p.append(arrow(500, 50, 560, 50, color=LINE, sw=1.8))

    p.append(fitbox(560, 20, 460, 60,
                    "Бібліотека GNU Readline (усередині процесу bash/python/gdb)\n"
                    "Конфігурація: ~/.inputrc (глобально) або bind у bashrc\n"
                    "Режими редагування: Emacs (дефолт) або Vi (командний/вставки)",
                    size=10.5, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    p.append(arrow(790, 80, 790, 115, color=NEG, sw=1.5))

    # Середній блок: Диспетчер дій
    p.append(fitbox(560, 115, 460, 95,
                    "Диспетчеризація послідовностей клавіш:\n"
                    "• Tab → menu-complete / complete (автодоповнення шляхів і команд)\n"
                    "• Стрілка вгору/вниз → history-search-backward / forward\n"
                    "• Ctrl+R → reverse-search-history (інкрементальний пошук)\n"
                    "• Редагування буфера в пам'яті (вставка, видалення слів, kill-ring)",
                    size=10, fill="#fff", stroke=NEG, sw=1.2, color=INK))

    p.append(arrow(560, 160, 500, 240, color=LINE, sw=1.8))

    # Лівий блок: Проблема ширини промпта (без екранування)
    p.append(fitbox(40, 240, 460, 140,
                    "❌ Катастрофа без екранування: PS1=\"\\033[32m\\u@\\h\\033[0m$ \"\n"
                    "1. Readline рахує символи '\\033', '[', '3', '2', 'm' як видимі стовпчики.\n"
                    "2. Помилкова ширина: вважає, що промпт займає на 10 колонок більше.\n"
                    "3. Наслідок: при введенні довгого рядка перенесення на новий рядок\n"
                    "   відбувається завчасно або текст накладається сам на себе!\n"
                    "   Курсор стрибає назад і затирає вже надруковані символи.",
                    size=10, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    # Правий блок: Правильний розрахунок ширини (з дужками)
    p.append(fitbox(560, 240, 460, 140,
                    "✓ Правильно: PS1=\"\\[\\033[32m\\]\\u@\\h\\[\\033[0m\\]$ \"\n"
                    "1. Послідовності '\\[ ' (\\001) та '\\] ' (\\002) вказують Readline:\n"
                    "   «Усі байти між цими дужками мають НУЛЬОВУ видиму ширину на екрані».\n"
                    "2. Колір надсилається терміналу, але лічильник стовпчиків не збільшується.\n"
                    "3. Наслідок: ідеальний розрахунок довжини рядка, плавний перенос тексту,\n"
                    "   стабільна робота клавіш Home, End, Backspace та історії.",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(arrow(270, 380, 270, 415, color=POS, sw=1.5))
    p.append(arrow(790, 380, 790, 415, color=FIELD, sw=1.5))

    # Нижній блок: Вивід у термінал
    p.append(fitbox(40, 415, 980, 110,
                    "Підсумок дисплейного рушія Readline (rl_redisplay):\n"
                    "Рядок у пам'яті синхронізується з екраном емулятора термінала через команди ANSI VT100.\n"
                    "Правильне маркування невидимих байтів гарантує, що координата курсора X у терміналі\n"
                    "точно відповідає логічній позиції вставки в буфері програми.",
                    size=10.5, fill=PALE, stroke=INK, sw=1.5, color=INK, bold=True))

    render(os.path.join(OUT, "readline-architecture.svg"), W, H, *p,
           title="Архітектура GNU Readline та розрахунок ширини промпта")


# ── 3. Синхронізація історії між термінальними вікнами ────────────────────────
def fig_history_sync_flow():
    W, H = 1060, 530
    p = []

    # Верхній опис проблеми
    p.append(fitbox(40, 20, 460, 115,
                    "Поведінка за замовчуванням (Втрата команд):\n"
                    "1. Кожне вікно тримає свій буфер у пам'яті (HISTSIZE).\n"
                    "2. При закритті сеансу буфер ПЕРЕЗАПИСУЄ ~/.bash_history.\n"
                    "3. Вікно, закрите останнім, безповоротно затирає історію\n"
                    "   усіх інших терміналів, відкритих паралельно!",
                    size=10, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(fitbox(560, 20, 460, 115,
                    "Оптимізована синхронізація в реальному часі:\n"
                    "1. shopt -s histappend (дописування замість перезапису).\n"
                    "2. PROMPT_COMMAND=\"history -a; history -c; history -r; ...\"\n"
                    "3. Кожна команда негайно скидається на диск і стає\n"
                    "   доступною у сусідніх вікнах вже на наступному натисканні Enter!",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    # Схема взаємодії двох терміналів
    p.append(fitbox(40, 165, 290, 80,
                    "Термінал 1 (Процес Bash A)\n"
                    "Користувач виконав команду:\n"
                    "$ make build\n"
                    "Буфер A містить новий запис",
                    size=10, fill=COOL, stroke=NEG, sw=1.5, color=INK, bold=True))

    p.append(arrow(330, 205, 410, 205, color=NEG, sw=2.0))

    # Центральний блок — дисковий файл
    p.append(fitbox(410, 165, 240, 155,
                    "Дисковий файл\n~/.bash_history\n(HISTFILESIZE=100000)\n\n"
                    "Спільне сховище всіх сеансів.\n"
                    "Захищене від дублікатів\n"
                    "через erasedups",
                    size=10, fill=PALE, stroke=LINE, sw=2.0, color=INK, bold=True))

    p.append(arrow(650, 205, 730, 205, color=FIELD, sw=2.0))

    p.append(fitbox(730, 165, 290, 80,
                    "Термінал 2 (Процес Bash B)\n"
                    "Користувач натискає Enter перед вводом.\n"
                    "Спрацьовує PROMPT_COMMAND\n"
                    "Буфер B оновлюється з диска",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.5, color=INK, bold=True))

    # Деталізація трьох команд синхронізації
    p.append(fitbox(40, 345, 310, 145,
                    "1. history -a (Append)\n"
                    "Скидає лише нові, ще не записані рядки\n"
                    "з оперативної пам'яті поточного процесу\n"
                    "в кінець файлу ~/.bash_history на диску.\n"
                    "Не перезаписує старі записи.",
                    size=10, fill="#fff", stroke=NEG, sw=1.2, color=INK))

    p.append(fitbox(375, 345, 310, 145,
                    "2. history -c (Clear)\n"
                    "Повністю очищає внутрішній список\n"
                    "історії в пам'яті процесу оболонки.\n"
                    "Звільняє вказівники буфера перед\n"
                    "повторним завантаженням з диска.",
                    size=10, fill="#fff", stroke=LINE, sw=1.2, color=INK))

    p.append(fitbox(710, 345, 310, 145,
                    "3. history -r (Read)\n"
                    "Зчитує актуальний стан дискового файлу\n"
                    "і заповнює буфер пам'яті.\n"
                    "У результаті стрілка 'Вгору' одразу бачить\n"
                    "команду, щойно виконану в іншому терміналі.",
                    size=10, fill="#fff", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(OUT, "history-sync-flow.svg"), W, H, *p,
           title="Синхронізація історії команд між термінальними вікнами")


# ── 4. Модульна архітектура dotfiles ──────────────────────────────────────────
def fig_modular_dotfiles_structure():
    W, H = 1060, 540
    p = []

    # Верхній блок — кореневий ~/.bashrc
    p.append(fitbox(320, 20, 420, 50,
                    "Головний файл: ~/.bashrc\n"
                    "Мінімальний захищений цикл завантаження модулів",
                    size=12, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    p.append(arrow(530, 70, 530, 105, color=LINE, sw=2.0))

    # Каталог модулів ~/.config/bash/ або ~/.bashrc.d/
    p.append(fitbox(40, 105, 980, 40,
                    "Каталог модулів: ~/.config/bash/*.bash (виконуються в алфавітно-числовому порядку)",
                    size=12, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    # Стовпчики модулів за пріоритетами
    modules = [
        ("00-env.bash", "Базове середовище\n• PATH, EDITOR, PAGER\n• XDG-директорії\n• Локаль та кодування", 40, 160, 185, "#fff", LINE),
        ("10-history.bash", "Історія команд\n• HISTSIZE, HISTFILESIZE\n• HISTCONTROL=erasedups\n• history -a sync-хук", 240, 160, 185, "#fff", LINE),
        ("20-readline.bash", "Ввід і клавіші\n• bind для пошуку історії\n• Режим vi / emacs\n• Підключення .inputrc", 440, 160, 185, "#fff", LINE),
        ("30-prompt.bash", "Рядок підказки\n• Кольоровий $PS1 з \\[\\]\n• Інтеграція Starship\n• Git-статус гілки", 640, 160, 185, "#fff", LINE),
        ("40-aliases.bash", "Аліаси та функції\n• ls, grep кольори\n• Безпечні cp/mv/rm\n• mkcd(), up(), extract()", 840, 160, 180, "#fff", LINE),
    ]

    for title, desc, x, y, w, bg_col, br_col in modules:
        p.append(fitbox(x, y, w, 32, title, size=10.5, fill=PALE, stroke=br_col, sw=1.5, color=INK, bold=True))
        p.append(fitbox(x, y + 36, w, 110, desc, size=9.5, fill=bg_col, stroke=br_col, sw=1.2, color=INK))

    p.append(arrow(530, 315, 530, 345, color=LINE, sw=1.8))

    # Модуль локальних перевизначень 99-local.bash
    p.append(fitbox(40, 345, 980, 55,
                    "99-local.bash (Локальні машинні налаштування, секрети, токени)\n"
                    "⚠️ Додано у .gitignore! Не публікується у відкритому Git-репозиторії.\n"
                    "Містить специфічні для конкретного сервера або ноутбука шляхи та змінні.",
                    size=10.5, fill=WARM, stroke=POS, sw=1.5, color=INK, bold=True))

    # Нижній блок: Керування версіями через Git Bare Repo
    p.append(fitbox(40, 420, 980, 95,
                    "Керування та версіонування через Git Bare Repository:\n"
                    "$ git init --bare $HOME/.dotfiles\n"
                    "$ alias dotfiles='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'\n"
                    "$ dotfiles config --local status.showUntrackedFiles no\n"
                    "Перевага: Домашній каталог не засмічується окремими симлінками, dotfiles версіонуються як рідні файли.",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    render(os.path.join(OUT, "modular-dotfiles-structure.svg"), W, H, *p,
           title="Модульна архітектура конфігурації оболонки (Dotfiles)")


if __name__ == "__main__":
    fig_shell_startup_matrix()
    fig_readline_architecture()
    fig_history_sync_flow()
    fig_modular_dotfiles_structure()
    print("All figures generated successfully.")
