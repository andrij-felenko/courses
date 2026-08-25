# -*- coding: utf-8 -*-
"""Фігури до теми «stty і зламаний термінал»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_terminal_state_architecture():
    """Архітектура стану термінала: де саме живе стан під час аварії програми."""
    W, H = 1040, 560
    g = []

    g.append(fitbox(20, 20, 1000, 44,
                    "Розподіл стану термінальної сесії між трьома незалежними сутностями",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    # 1. Простір користувача: Процес застосунку
    g.append(rect(20, 80, 310, 400, fill=BG, stroke=POS, sw=1.8))
    g.append(fitbox(30, 90, 290, 42, "1. Процес застосунку (vim, sudo, fzf)",
                    size=13, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(30, 142, 290, 76,
                    "• Пам'ять процесу (стек, купа)\n"
                    "• Буфери termios всередині libc\n"
                    "• Обробники сигналів та деструктори",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(30, 228, 290, 100,
                    "АВАРІЯ:\n"
                    "• SIGKILL, SIGSEGV, обрив SSH\n"
                    "• Процес зникає миттєво\n"
                    "• Не встигає викликати tcsetattr()\n"
                    "• Пам'ять процесу очищено",
                    size=12, fill="#fdf3f2", stroke=POS))
    g.append(fitbox(30, 340, 290, 126,
                    "НАСЛІДОК:\n"
                    "Увесь код відновлення в пам'яті\n"
                    "знищено. Але стан термінала\n"
                    "живе НЕ ТУТ, тому термінал\n"
                    "залишається спотвореним.",
                    size=12, fill=FILL, stroke=MUTED))

    # 2. Ядро ОС: Дисципліна лінії N_TTY
    g.append(rect(365, 80, 310, 400, fill=BG, stroke=NEG, sw=1.8))
    g.append(fitbox(375, 90, 290, 42, "2. Ядро ОС (struct termios в N_TTY)",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(375, 142, 290, 76,
                    "• c_lflag: ECHO, ICANON, ISIG\n"
                    "• c_oflag: OPOST, ONLCR\n"
                    "• c_iflag: ICRNL, IXON, BRKINT",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(375, 228, 290, 100,
                    "ПОВЕДІНКА:\n"
                    "• Належить пристрою (/dev/pts/N)\n"
                    "• НЕ залежить від життя процесу\n"
                    "• Зберігає біти сирого режиму\n"
                    "• Передається наступній програмі",
                    size=12, fill="#eaf6ee", stroke=FIELD))
    g.append(fitbox(375, 340, 290, 126,
                    "НАСЛІДОК:\n"
                    "Оболонка (bash/zsh) отримує\n"
                    "дескриптор із вимкненим ECHO\n"
                    "або ONLCR. Будь-який ввід стає\n"
                    "невидимим або кривим.",
                    size=12, fill=FILL, stroke=MUTED))

    # 3. Емулятор термінала: Стан рендера VT100
    g.append(rect(710, 80, 310, 400, fill=BG, stroke=MUTED, sw=1.8))
    g.append(fitbox(720, 90, 290, 42, "3. Емулятор (xterm, alacritty, kitty)",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED))
    g.append(fitbox(720, 142, 290, 76,
                    "• Таблиця символів G0/G1 (DEC alt)\n"
                    "• Видимість курсора (DECTCEM)\n"
                    "• Альтернативний екранний буфер",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(720, 228, 290, 100,
                    "ПОВЕДІНКА:\n"
                    "• Керується байтами у stdout\n"
                    "• Бінарне сміття шле ESC ( 0 або SO\n"
                    "• Перемикає рендер на графіку\n"
                    "• Ядро про це нічого не знає",
                    size=12, fill="#fff8e7", stroke="#d97706"))
    g.append(fitbox(720, 340, 290, 126,
                    "НАСЛІДОК:\n"
                    "Звичайні літери перетворюються\n"
                    "на лінії й кутики (┌─┐│).\n"
                    "Ядро працює ідеально, але екран\n"
                    "рендерить рунічне сміття.",
                    size=12, fill=FILL, stroke=MUTED))

    g.append(fitbox(20, 494, 1000, 48,
                    "ВИСНОВОК: Лікування вимагає двох дій: (1) stty sane лагодить ядро; (2) reset / RIS лагодить емулятор.",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))

    render(os.path.join(IMG, 'terminal-state-architecture.svg'), W, H, *g,
           title="Архітектура розподілу стану термінала")


def fig_breakage_symptoms_matrix():
    """Матриця симптомів поломки термінала, прапорці termios та прояви."""
    W, H = 1040, 520
    g = []

    g.append(fitbox(20, 20, 1000, 44,
                    "Чотири класичних синдроми зіпсованого термінала",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    cards = [
        (20, 80, "Синдром 1: Сліпий ввід",
         "Знято прапорець ECHO",
         "Клавіатура не відлунює ввід на екран.\nКоманди йдуть, але друк невидимий.",
         "sudo, ssh або ncurses впали\nдо відновлення прапорця ECHO.",
         "stty echo  або  stty sane"),

        (540, 80, "Синдром 2: Ефект сходів",
         "Знято прапорець ONLCR",
         "Символ \\n не додає повернення каретки \\r.\nТекст з'їжджає вправо сходинками.",
         "Редактори вимикають ONLCR\nдля прямого позиціонування курсора.",
         "stty opost onlcr  або  stty sane"),

        (20, 290, "Синдром 3: Завислий сирий режим",
         "Знято ICANON та ISIG",
         "Забій пише ^H, Enter не завершує рядок,\nCtrl+C не шле SIGINT, а пише ^C.",
         "Програма сирого вводу впала;\nядро не редагує рядок і не шле сигнали.",
         "<Ctrl+J>stty sane<Ctrl+J>"),

        (540, 290, "Синдром 4: Графіка замість літер",
         "Увімкнено DEC VT100 Alt Charset",
         "Букви стають рамками й псевдографікою\n(наприклад, ls друкує ┌⎺).",
         "cat бінарного файлу чи /dev/urandom\nнадіслав SO (0x0E) або ESC ( 0.",
         "echo -e '\\033(B\\017'  або  reset"),
    ]

    for x, y, title, flags, desc, cause, fix in cards:
        g.append(rect(x, y, 480, 195, fill=BG, stroke=MUTED, sw=1.5))
        g.append(fitbox(x + 10, y + 10, 460, 32, title, size=13, bold=True, fill="#eaf0fd", stroke=NEG))
        g.append(fitbox(x + 10, y + 46, 460, 26, "Причина: " + flags, size=12, bold=True, fill="#fdecea", stroke=POS))
        g.append(fitbox(x + 10, y + 76, 460, 40, "Прояв:\n" + desc, size=11, fill=FILL, stroke=MUTED))
        g.append(fitbox(x + 10, y + 120, 460, 32, "Джерело:\n" + cause, size=11, fill=FILL, stroke=MUTED))
        g.append(fitbox(x + 10, y + 156, 460, 28, "Лікування: " + fix, size=12, bold=True, fill="#eaf6ee", stroke=FIELD))

    render(os.path.join(IMG, 'breakage-symptoms-matrix.svg'), W, H, *g,
           title="Матриця симптомів пошкодження термінала")


def fig_resuscitation_flow():
    """Покроковий алгоритм реанімації зламаного термінала."""
    W, H = 1040, 520
    g = []

    g.append(fitbox(20, 20, 1000, 44,
                    "Покроковий протокол реанімації (CPR) для термінала",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    steps = [
        (20, 80, "Крок 1: Очищення",
         "<Ctrl+C>",
         "Перериває завислу фонову\n"
         "програму чи конвеєр,\n"
         "якщо прапорець ISIG\n"
         "ще активний у ядрі.",
         "#eaf0fd", NEG),

        (275, 80, "Крок 2: Наосліп",
         "<Ctrl+J>stty sane<Ctrl+J>",
         "Якщо ICRNL вимкнено,\n"
         "Enter (0x0D) ігнорується.\n"
         "Ctrl+J шле LF (0x0A),\n"
         "змушуючи shell виконати\n"
         "скидання termios у ядрі.",
         "#fdecea", POS),

        (530, 80, "Крок 3: Графіка",
         "echo -e '\\033(B\\017'",
         "Шле послідовності:\n"
         "ESC ( B (G0 -> ASCII)\n"
         "та SI (0x0F, Shift In).\n"
         "Повертає нормальний\n"
         "шрифт в емуляторі.",
         "#fff8e7", "#d97706"),

        (785, 80, "Крок 4: Ресет",
         "reset / tput reset",
         "Шле терміналу код\n"
         "ініціалізації RIS (ESC c),\n"
         "очищає екранний буфер,\n"
         "скидає шрифти й стан.",
         "#eaf6ee", FIELD),
    ]

    for x, y, title, cmd, desc, fill_col, stroke_col in steps:
        g.append(rect(x, y, 235, 360, fill=BG, stroke=stroke_col, sw=1.8))
        g.append(fitbox(x + 8, y + 10, 219, 36, title, size=12, bold=True, fill=fill_col, stroke=stroke_col))
        g.append(fitbox(x + 8, y + 54, 219, 44, cmd, size=11, bold=True, fill="#eef2f7", stroke=LINE))
        g.append(fitbox(x + 8, y + 106, 219, 238, desc, size=12, fill=FILL, stroke=MUTED))

    # Стрілки між кроками
    g.append(arrow(257, 240, 273, 240, color=LINE, sw=2.0))
    g.append(arrow(512, 240, 528, 240, color=LINE, sw=2.0))
    g.append(arrow(767, 240, 783, 240, color=LINE, sw=2.0))

    g.append(fitbox(20, 456, 1000, 48,
                    "Універсальна «сліпа рятівна комбінація»: <Enter><Ctrl+C><Ctrl+J>stty sane<Ctrl+J>",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))

    render(os.path.join(IMG, 'resuscitation-flow.svg'), W, H, *g,
           title="Протокол покрокової реанімації термінала")


def fig_signal_lifecycle_raii():
    """Життєвий цикл безпечного керування терміналом у програмі."""
    W, H = 1040, 500
    g = []

    g.append(fitbox(20, 20, 1000, 44,
                    "Життєвий цикл програми: гарантоване відновлення termios у C та C++",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    # Лівий блок: нормальний потік
    g.append(rect(20, 80, 480, 390, fill=BG, stroke=FIELD, sw=1.8))
    g.append(fitbox(30, 90, 460, 36, "Штатний потік виконання (RAII / atexit)",
                    size=13, bold=True, fill="#eaf6ee", stroke=FIELD))
    g.append(fitbox(30, 134, 460, 54,
                    "1. Збереження початкового стану:\n"
                    "tcgetattr(STDIN_FILENO, &orig_termios);",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(30, 196, 460, 54,
                    "2. Вхід у сирий режим:\n"
                    "raw = orig_termios; cfmakeraw(&raw); tcsetattr(...);",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(30, 258, 460, 60,
                    "3. Робота програми:\n"
                    "Інтерактивний ввід, редагування, меню TUI.",
                    size=12, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(30, 326, 460, 60,
                    "4. Штатний вихід (Clean Exit):\n"
                    "Деструктор RAII або функція atexit() автоматично\n"
                    "викликає tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios).",
                    size=12, fill="#eaf6ee", stroke=FIELD))
    g.append(fitbox(30, 394, 460, 64,
                    "РЕЗУЛЬТАТ:\n"
                    "Термінал бездоганно чистий і готовий до роботи оболонки.",
                    size=12, bold=True, fill=FILL, stroke=MUTED))

    # Правий блок: асинхронні сигнали та зупинка (Job Control)
    g.append(rect(540, 80, 480, 390, fill=BG, stroke=POS, sw=1.8))
    g.append(fitbox(550, 90, 460, 36, "Аварійні сигнали та Job Control (sigaction)",
                    size=13, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(550, 134, 460, 74,
                    "Сигнали завершення (SIGINT, SIGTERM, SIGHUP, SIGQUIT):\n"
                    "• Обробник відновлює tcsetattr(..., &orig_termios);\n"
                    "• Скидає дію на SIG_DFL та повторно шле сигнал через raise().",
                    size=12, fill=FILL, stroke=MUTED))
    g.append(fitbox(550, 216, 460, 96,
                    "Зупинка процесу клавішею Ctrl+Z (SIGTSTP):\n"
                    "• Обробник ловить SIGTSTP;\n"
                    "• Відновлює початковий termios (віддає термінал shell);\n"
                    "• Розблоковує SIGTSTP і присипляє процес через raise(SIGTSTP).",
                    size=12, fill="#fff8e7", stroke="#d97706"))
    g.append(fitbox(550, 320, 460, 68,
                    "Повернення у foreground (SIGCONT):\n"
                    "• Обробник ловить SIGCONT після команди fg;\n"
                    "• Повторно застосовує сирий режим raw_termios.",
                    size=12, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(550, 396, 460, 62,
                    "РЕЗУЛЬТАТ:\n"
                    "Програма виживає при фонуванні й не ламає термінал при аварії.",
                    size=12, bold=True, fill="#eaf6ee", stroke=FIELD))

    render(os.path.join(IMG, 'signal-lifecycle-raii.svg'), W, H, *g,
           title="Життєвий цикл безпечного керування терміналом")


if __name__ == '__main__':
    fig_terminal_state_architecture()
    fig_breakage_symptoms_matrix()
    fig_resuscitation_flow()
    fig_signal_lifecycle_raii()
    print("ok")
