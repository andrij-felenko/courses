#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми terminal-size-and-modes.
Розмір вікна й режими екрана: struct winsize, TIOCGWINSZ/TIOCSWINSZ, SIGWINCH, Alternate Screen Buffer.
"""

import sys
import os

# scripts/ лежить 4 рівні вище: root/sys/sys-unix/terminal-size-and-modes -> scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')

def gen_winsize_kernel_flow():
    w, h = 860, 480
    frags = []

    # Заголовок / фонові зони
    # Зона користувача (ліворуч)
    frags.append(rect(20, 50, 240, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(140, 75, "Емулятор термінала (GUI)", size=14, bold=True, color="#1e293b"))
    frags.append(text(140, 95, "Alacritty, xterm, WezTerm", size=11, color="#64748b"))

    # Блок зміни розміру вікна
    frags.append(fitbox(35, 120, 210, 65, "1. Користувач тягне кут вікна\nПікселі = w_px × h_px\nСтовпці = w_px / font_w\nРядки = h_px / font_h", size=11, fill="#ffffff", stroke="#94a3b8"))

    # Блок виклику ioctl TIOCSWINSZ
    frags.append(fitbox(35, 230, 210, 60, "2. Системний виклик ioctl\nioctl(ptmx_fd, TIOCSWINSZ,\n      &winsize)", size=12, fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True))

    # Зона ядра Linux (посередині)
    frags.append(rect(290, 50, 280, 400, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(430, 75, "Ядро Linux: підсистема TTY", size=14, bold=True, color="#0f172a"))
    frags.append(text(430, 95, "Драйвер PTY (struct tty_struct)", size=11, color="#64748b"))

    # Блок збереження геометрії в ядрі
    frags.append(fitbox(305, 120, 250, 110, "3. Оновлення стану лінії\nstruct winsize {\n  ws_row, ws_col;\n  ws_xpixel, ws_ypixel;\n};\ntty->winsize = new_ws;", size=11, fill="#ffffff", stroke="#64748b"))

    # Блок генерації сигналу
    frags.append(fitbox(305, 270, 250, 70, "4. Генерація сигналу\nЯкщо розмір змінився:\nkill_pgrp(tty->pgrp,\n          SIGWINCH, 1);", size=12, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    # Зона прикладного процесу (праворуч)
    frags.append(rect(600, 50, 240, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(720, 75, "TUI-програма (фоновий/активний)", size=14, bold=True, color="#1e293b"))
    frags.append(text(720, 95, "vim, htop, less (/dev/pts/N)", size=11, color="#64748b"))

    # Блок отримання сигналу
    frags.append(fitbox(615, 120, 210, 65, "5. Обробка SIGWINCH\nОбробник сигналу або\nчитання через signalfd(2)\nВстановлення прапорця", size=11, fill="#fffbeb", stroke="#f59e0b", color="#b45309", bold=True))

    # Блок опитування розміру
    frags.append(fitbox(615, 230, 210, 60, "6. Запит нової геометрії\nioctl(STDIN_FILENO,\n      TIOCGWINSZ, &ws)", size=12, fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True))

    # Блок перемалювання
    frags.append(fitbox(615, 340, 210, 65, "7. Адаптація сітки UI\nПеревиділення матриці комірок\nПерерахунок розкладки панелей\nПовне перемалювання кадру", size=11, fill="#f0fdf4", stroke="#22c55e", color="#15803d", bold=True))

    # Стрілки між блоками
    # 1 -> 2
    frags.append(arrow(140, 185, 140, 225, color="#0284c7", sw=2))
    # 2 -> 3 (в ядро)
    frags.append(arrow(245, 260, 305, 175, color="#0284c7", sw=2))
    # 3 -> 4
    frags.append(arrow(430, 230, 430, 265, color="#ef4444", sw=2))
    # 4 -> 5 (до програми)
    frags.append(arrow(555, 305, 615, 152, color="#ef4444", sw=2))
    # 5 -> 6
    frags.append(arrow(720, 185, 720, 225, color="#0284c7", sw=2))
    # 6 -> назад у ядро і відповідь
    frags.append(line(615, 260, 560, 260, color="#0284c7", sw=1.5, dash="4,4"))
    # 6 -> 7
    frags.append(arrow(720, 290, 720, 335, color="#22c55e", sw=2))

    render(os.path.join(OUT_DIR, "winsize-kernel-flow.svg"), w, h, *frags,
           title="Шлях зміни розміру термінала: від зміни вікна GUI до SIGWINCH і перемалювання TUI")

def gen_screen_buffers_switch():
    w, h = 860, 420
    frags = []

    # Ліва колонка: Основний екранний буфер
    frags.append(rect(30, 50, 340, 340, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    frags.append(text(200, 78, "Основний екран (Primary Buffer)", size=15, bold=True, color="#0f172a"))
    frags.append(text(200, 98, "Стандартний режим командного рядка", size=12, color="#64748b"))

    # Блок історії прокрутки
    frags.append(fitbox(45, 120, 310, 70, "Кільцевий буфер прокрутки (Scrollback)\nЗберігає історію виводу: 10 000+ рядків\nДоступний через коліщатко миші / Shift+PageUp", size=11, fill="#ffffff", stroke="#cbd5e1"))

    # Блок видимого вікна
    frags.append(fitbox(45, 205, 310, 110, "Видима сітка (ws_row × ws_col):\n$ git status\n$ cargo build\n$ vim main.c █\n(Курсор стоїть у позиції команди)", size=12, fill="#f1f5f9", stroke="#94a3b8", color="#1e293b"))

    frags.append(text(200, 345, "Вміст не втрачається під час роботи TUI", size=11, italic=True, color="#475569"))
    frags.append(text(200, 365, "Шелл повертається до початкового стану", size=11, italic=True, color="#475569"))

    # Права колонка: Альтернативний екранний буфер
    frags.append(rect(490, 50, 340, 340, fill="#0f172a", stroke="#334155", sw=1.8, rx=8))
    frags.append(text(660, 78, "Альтернативний екран (Alternate Buffer)", size=15, bold=True, color="#38bdf8"))
    frags.append(text(660, 98, "Режим повноекранної програми", size=12, color="#94a3b8"))

    # Блок відсутності скролбеку
    frags.append(fitbox(505, 120, 310, 55, "Немає буфера прокрутки (Scrollback: 0)\nКожна комірка адресована напряму\nКоманди прокрутки керуються самою програмою", size=11, fill="#1e293b", stroke="#475569", color="#cbd5e1"))

    # Блок TUI вікна
    frags.append(fitbox(505, 190, 310, 135, "Матриця комірок (ws_row × ws_col):\n┌── main.c ───────────────────┐\n│ int main() {                 │\n│     printf(\"Hello, TUI\\n\");  │\n│ }                            │\n└── NORMAL ── 1,1 ────────────┘", size=11, fill="#020617", stroke="#0284c7", color="#38bdf8"))

    frags.append(text(660, 350, "Чистий лист без змішування з шеллом", size=11, italic=True, color="#94a3b8"))
    frags.append(text(660, 370, "При виході матриця звільняється", size=11, italic=True, color="#94a3b8"))

    # Центральні стрілки переходів з послідовностями
    # Перехід вперед \e[?1049h
    frags.append(fitbox(385, 130, 90, 55, "Вхід:\n\\e[?1049h", size=12, fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True))
    frags.append(arrow(370, 157, 490, 157, color="#0284c7", sw=2.2))

    # Перехід назад \e[?1049l
    frags.append(fitbox(385, 260, 90, 55, "Вихід:\n\\e[?1049l", size=12, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))
    frags.append(arrow(490, 287, 370, 287, color="#ef4444", sw=2.2))

    render(os.path.join(OUT_DIR, "screen-buffers-switch.svg"), w, h, *frags,
           title="Перемикання між основним та альтернативним екранними буферами термінала")

def gen_terminal_mode_transition():
    w, h = 860, 440
    frags = []

    # Фаза 1: Канонічний режим (початковий)
    frags.append(rect(30, 60, 230, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(145, 88, "1. Канонічний режим", size=15, bold=True, color="#1e293b"))
    frags.append(text(145, 108, "Стан термінала в командній оболонці", size=11, color="#64748b"))

    frags.append(fitbox(45, 125, 200, 100, "Параметри termios:\n• ICANON: рядкова буферизація\n• ECHO: показ натиснутих літер\n• ISIG: обробка Ctrl+C ядром\n• ONLCR: перетворення \\n у \\r\\n", size=11, fill="#ffffff", stroke="#cbd5e1"))

    frags.append(fitbox(45, 240, 200, 80, "Екранні режими:\n• Основний буфер екрана\n• Курсор видимий (\\e[?25h)\n• Прокрутка ввімкнена", size=11, fill="#ffffff", stroke="#cbd5e1"))

    frags.append(fitbox(45, 335, 200, 50, "Дія на старті:\ntcgetattr(fd, &orig_termios)", size=11, fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True))

    # Фаза 2: Сирий режим та TUI (активна робота)
    frags.append(rect(315, 60, 230, 340, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=8))
    frags.append(text(430, 88, "2. Сирий режим (Raw/TUI)", size=15, bold=True, color="#1d4ed8"))
    frags.append(text(430, 108, "Повний контроль над клавішами й екраном", size=11, color="#3b82f6"))

    frags.append(fitbox(330, 125, 200, 110, "Зміни termios:\n• cfmakeraw(&raw) або скидання:\n  ~(ICANON | ECHO | ECHOE |\n    ISIG | IEXTEN | IXON)\n• c_cc[VMIN] = 1, VTIME = 0\n• Застосування: TCSAFLUSH", size=11, fill="#ffffff", stroke="#93c5fd"))

    frags.append(fitbox(330, 250, 200, 80, "Екранні послідовності:\n• Альтернативний екран: \\e[?1049h\n• Сховати курсор: \\e[?25l\n• Сигнал SIGWINCH підключено", size=11, fill="#ffffff", stroke="#93c5fd"))

    frags.append(fitbox(330, 345, 200, 40, "Головний цикл подій програми", size=12, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True))

    # Фаза 3: Безпечне відновлення
    frags.append(rect(600, 60, 230, 340, fill="#f8fafc", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(715, 88, "3. Відновлення стану", size=15, bold=True, color="#15803d"))
    frags.append(text(715, 108, "Вихід або обробка сигналів", size=11, color="#16a34a"))

    frags.append(fitbox(615, 125, 200, 95, "Очищення термінала:\n1. \\e[?25h (показати курсор)\n2. \\e[?1049l (основний екран)\n3. \\e[0m (скинути кольори)\n4. fflush(stdout)", size=11, fill="#ffffff", stroke="#bbf7d0"))

    frags.append(fitbox(615, 235, 200, 85, "Відновлення драйвера:\ntcsetattr(fd, TCSAFLUSH,\n          &orig_termios);\nСкидання залишків вводу\nі повернення лінійних правил", size=11, fill="#ffffff", stroke="#bbf7d0"))

    frags.append(fitbox(615, 335, 200, 50, "Захист: atexit() +\nобробники SIGINT, SIGTERM", size=11, fill="#dcfce7", stroke="#16a34a", color="#15803d", bold=True))

    # Стрілки між фазами
    frags.append(arrow(260, 210, 315, 210, color="#2563eb", sw=2.2))
    frags.append(arrow(545, 210, 600, 210, color="#16a34a", sw=2.2))

    render(os.path.join(OUT_DIR, "terminal-mode-transition.svg"), w, h, *frags,
           title="Життєвий цикл стану термінала: вхід у сирий режим, TUI та гарантоване відновлення")

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    gen_winsize_kernel_flow()
    gen_screen_buffers_switch()
    gen_terminal_mode_transition()
    print("All figures generated successfully.")
