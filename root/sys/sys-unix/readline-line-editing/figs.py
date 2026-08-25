# -*- coding: utf-8 -*-
"""Фігури до теми «readline: редагування рядка й прив'язки клавіш»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_readline_architecture():
    """Архітектура взаємодії Readline, ядра, термінала й програми."""
    W, H = 1120, 500
    g = []

    g.append(text(W / 2, 38,
                  "Потік введення та перемальовування в архітектурі GNU Readline",
                  size=16, color=INK, bold=True))

    # Вхідний потік (згори)
    g.append(fitbox(40, 70, 210, 80,
                    "Емулятор термінала\nабо клавіатура\nпотік байтів у pty",
                    size=12.5, fill=FILL, stroke=LINE))

    g.append(arrow(254, 110, 306, 110))

    g.append(fitbox(310, 70, 240, 80,
                    "Ядро: лінійна дисципліна TTY\nСирий режим (raw mode)\nICANON=0, ECHO=0, VMIN=1",
                    size=12, fill="#eaf0fd", stroke=NEG))

    g.append(arrow(554, 110, 606, 110))

    g.append(fitbox(610, 70, 230, 80,
                    "Диспетчер клавіш Readline\nKeymap (Emacs / Vi)\nРозбір escape-послідовностей",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    g.append(arrow(844, 110, 896, 110))

    g.append(fitbox(900, 70, 180, 80,
                    "Буфер рядка\nrl_line_buffer\nrl_point / rl_end",
                    size=12.5, fill="#fff8e6", stroke=MUTED))

    # Стан і структури посередині
    g.append(fitbox(200, 195, 720, 80,
                    "Внутрішній стан бібліотеки:\n"
                    "Збережений термінальний стан termios · Кільце вирізання (Kill Ring) · Історія команд\n"
                    "Таблиці прив'язок клавіш ~/.inputrc · Хуки завершення слів (Completion)",
                    size=12, fill="#f8fafc", stroke=MUTED))

    # Вихідний потік (знизу)
    g.append(fitbox(900, 320, 180, 80,
                    "Дисплейний рушій\nrl_redisplay()\nмінімальний VT100 diff",
                    size=12, fill="#fff8e6", stroke=MUTED))

    g.append(arrow(990, 154, 990, 316))

    g.append(arrow(896, 360, 694, 360))

    g.append(fitbox(450, 320, 240, 80,
                    "Екран термінала\nКеруючі коди CSI:\nпереміщення курсора, оновлення",
                    size=12, fill=FILL, stroke=LINE))

    g.append(arrow(990, 404, 990, 440))
    g.append(line(990, 440, 145, 440))
    g.append(arrow(145, 440, 145, 404))

    g.append(fitbox(40, 320, 210, 80,
                    "Прикладна програма\n(Bash, Python REPL, GDB)\nотримує готовий char* після Enter",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    g.append(text(W / 2, 478,
                  "Readline бере відлуння й редагування на себе, повертаючи ядру оригінальний termios при виході",
                  size=12.5, color=MUTED))

    return render(os.path.join(IMG, 'readline-architecture.svg'), W, H, *g,
                  title="Архітектура GNU Readline")


def fig_emacs_vs_vi_modes():
    """Порівняння парадигм редагування: безмодальний Emacs проти модального Vi."""
    W, H = 1100, 480
    g = []

    g.append(text(W / 2, 38,
                  "Два світи взаємодії: безмодальний Emacs проти модального автомата Vi",
                  size=16, color=INK, bold=True))

    # Ліва колонка: Emacs
    g.append(fitbox(40, 70, 480, 50,
                    "Режим Emacs (безмодальний, за замовчуванням)",
                    size=13.5, bold=True, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(40, 135, 480, 100,
                    "Єдиний стан введення:\n"
                    "• Звичайні символи відразу додаються в буфер\n"
                    "• Ctrl+ (символьні операції): Ctrl+A (початок), Ctrl+E (кінець), Ctrl+T (своп)\n"
                    "• Alt+ / Meta (операції над словами): Alt+F, Alt+B, Alt+U, Alt+L",
                    size=12, fill=FILL, stroke=LINE))

    g.append(fitbox(40, 250, 480, 115,
                    "Кільцевий буфер вирізання (Kill Ring):\n"
                    "Ctrl+K (вбити до кінця), Ctrl+U (до початку), Ctrl+W (слово назад)\n"
                    "                      ↓ запис у kill_ring[ ]\n"
                    "Ctrl+Y (yank: вставити)  ⇄  Alt+Y (yank-pop: перебрати старіші записи)",
                    size=12, fill="#fff8e6", stroke=MUTED))

    g.append(fitbox(40, 380, 480, 60,
                    "Пошук в історії:\n"
                    "Ctrl+R (зворотний інкрементний пошук) · Ctrl+S (прямий)",
                    size=12, fill=FILL, stroke=LINE))

    # Права колонка: Vi
    g.append(fitbox(580, 70, 480, 50,
                    "Режим Vi (модальний: set editing-mode vi)",
                    size=13.5, bold=True, fill="#eaf0fd", stroke=NEG))

    g.append(fitbox(580, 135, 220, 85,
                    "Insert Mode (вставка)\n"
                    "Введення тексту;\n"
                    "Enter виконує команду\n"
                    "Backspace видаляє знак",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(840, 135, 220, 85,
                    "Normal / Command Mode\n"
                    "Клавіші = команди;\n"
                    "Навігація h, j, k, l, w, b, $, 0\n"
                    "Повтор «.», пошук «/», «?»",
                    size=12, fill="#fdecea", stroke=POS))

    g.append(arrow(804, 160, 836, 160))
    g.append(text(820, 150, "ESC", size=11, bold=True, color=POS))

    g.append(arrow(836, 195, 804, 195))
    g.append(text(820, 212, "i, a, I, A", size=11, bold=True, color=FIELD))

    g.append(fitbox(580, 250, 480, 115,
                    "Граматика команд Normal Mode:\n"
                    "[лічильник] + оператор + [лічильник] + рух\n"
                    "• d + w  → видалити слово (dw)  ·  3 + d + w → видалити 3 слова\n"
                    "• c + $  → змінити до кінця рядка (перехід у Insert Mode)\n"
                    "• y + y  → скопіювати рядок у регістр · p / P → вставити з регістру",
                    size=12, fill="#fff8e6", stroke=MUTED))

    g.append(fitbox(580, 380, 480, 60,
                    "Візуальна індикація режиму в терміналі:\n"
                    "show-mode-in-prompt або форма курсора (паличка в Insert, блок у Normal)",
                    size=12, fill=FILL, stroke=LINE))

    return render(os.path.join(IMG, 'emacs-vs-vi-modes.svg'), W, H, *g,
                  title="Порівняння режимів Emacs і Vi")


def fig_escape_dispatch_fsm():
    """Розбір вхідних escape-послідовностей та розв'язання неоднозначності ESC."""
    W, H = 1080, 470
    g = []

    g.append(text(W / 2, 38,
                  "Дерево диспетчеризації вхідних байтів та таймаут keyseq-timeout",
                  size=16, color=INK, bold=True))

    g.append(fitbox(40, 80, 230, 80,
                    "Вхідний байт із read(0)\n"
                    "Звичайний друкований знак\nабо базовий Ctrl-код",
                    size=12.5, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(40, 210, 230, 80,
                    "Префіксний байт 0x1B (ESC)\n"
                    "Початок керівної послідовності\nабо одиночна клавіша Esc",
                    size=12.5, fill="#fff8e6", stroke=MUTED))

    g.append(fitbox(40, 340, 230, 80,
                    "Таймер keyseq-timeout\n"
                    "(типово 500 мс)\nочікування наступного байта",
                    size=12, fill="#fdecea", stroke=POS))

    g.append(arrow(155, 294, 155, 336))

    # Гілка А: таймаут сплив
    g.append(arrow(274, 380, 366, 380))
    g.append(fitbox(370, 340, 320, 80,
                    "Таймаут вичерпано, більше байтів немає:\n"
                    "Подія: натиснуто одиночний «Escape»\n"
                    "Emacs: префікс Meta · Vi: перехід у Normal Mode",
                    size=12, fill=FILL, stroke=LINE))

    # Гілка Б: наступний байт надійшов вчасно
    g.append(arrow(274, 250, 366, 250))
    g.append(fitbox(370, 210, 320, 80,
                    "Байт надійшов до вичерпання таймауту:\n"
                    "Пошук гілки в дереві Keymap:\n"
                    "«[» (CSI) або «O» (SS3) або символ для Meta-",
                    size=12, fill="#eaf0fd", stroke=NEG))

    # Дерево послідовностей
    g.append(arrow(694, 250, 756, 140))
    g.append(fitbox(760, 90, 280, 75,
                    "ESC [ A  →  Стрілка вгору (previous-history)\n"
                    "ESC [ B  →  Стрілка вниз (next-history)\n"
                    "ESC [ C  →  Стрілка вправо (forward-char)",
                    size=11.5, fill=FILL, stroke=LINE))

    g.append(arrow(694, 250, 756, 250))
    g.append(fitbox(760, 210, 280, 80,
                    "ESC [ 3 ~  →  Delete (delete-char)\n"
                    "ESC [ 1 ; 5 C  →  Ctrl+Right (forward-word)\n"
                    "ESC [ H / ESC [ F  →  Home / End",
                    size=11.5, fill=FILL, stroke=LINE))

    g.append(arrow(694, 250, 756, 360))
    g.append(fitbox(760, 330, 280, 75,
                    "ESC f  →  Alt+F (forward-word)\n"
                    "ESC b  →  Alt+B (backward-word)\n"
                    "ESC d  →  Alt+D (kill-word)",
                    size=11.5, fill=FILL, stroke=LINE))

    g.append(text(W / 2, 448,
                  "База terminfo зіставляє послідовності емулятора (kcuu1, kdch1) з функціями Readline",
                  size=12.5, color=MUTED))

    return render(os.path.join(IMG, 'escape-dispatch-fsm.svg'), W, H, *g,
                  title="Диспетчеризація послідовностей клавіш")


def fig_prompt_redisplay_width():
    """Розрахунок видимої ширини промпта та маркери невидимих послідовностей."""
    W, H = 1080, 460
    g = []

    g.append(text(W / 2, 38,
                  "Обчислення видимої ширини промпта та маркери невидимих escape-кодів",
                  size=16, color=INK, bold=True))

    # Верхня панель: Помилка без маркерів
    g.append(fitbox(40, 70, 1000, 160,
                    "ПРОБЛЕМА: Промпт із сирими ANSI-кодами кольору без маркерів екранування\n\n"
                    "Рядок у PS1:  \\033[32m user@host:~$ \\033[0m   (довжина: 24 байти)\n"
                    "Видимий текст: user@host:~$                    (реальна ширина: 12 стовпчиків)\n\n"
                    "Без маркерів Readline вважає довжину 24 стовпчиками: курсор на екрані стоїть на 13-й колонці,\n"
                    "а внутрішній лічильник думає, що на 25-й. Довгі команди ламають перенесення рядків і затирають промпт!",
                    size=12, fill="#fdecea", stroke=POS))

    # Нижня панель: Виправлення з маркерами
    g.append(fitbox(40, 255, 1000, 165,
                    "РІШЕННЯ: Маркери нульової ширини \\[ і \\] (у Readline: \\001 RL_PROMPT_START_IGNORE та \\002 RL_PROMPT_END_IGNORE)\n\n"
                    "Рядок у PS1:  \\[\\033[32m\\] user@host:~$ \\[\\033[0m\\]\n"
                    "Дисплейний рушій: байти між \\001 та \\002 передаються терміналу для забарвлення,\n"
                    "але їхня ширина прирівнюється до 0 під час обчислення позиції курсора через wcwidth().\n\n"
                    "Результат: Readline знає точну ширину 12 стовпчиків, і перенесення рядка спрацьовує точно на краю вікна.",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    g.append(text(W / 2, 442,
                  "Функція rl_redisplay() використовує видиму ширину колонок для обчислення мінімальної різниці оновлення",
                  size=12.5, color=MUTED))

    return render(os.path.join(IMG, 'prompt-redisplay-width.svg'), W, H, *g,
                  title="Розрахунок видимої ширини промпта")


if __name__ == '__main__':
    fig_readline_architecture()
    fig_emacs_vs_vi_modes()
    fig_escape_dispatch_fsm()
    fig_prompt_redisplay_width()
    print("Згенеровано фігури:", os.listdir(IMG))
