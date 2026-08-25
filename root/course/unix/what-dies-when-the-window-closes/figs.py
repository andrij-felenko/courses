# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"
WARN = "#fef9e7"
WARN_STROKE = "#d4ac0d"
PURPLE = "#f4ecf7"
PURPLE_STROKE = "#8e44ad"


# ── 1. Топологія сеансу й термінала ──────────────────────────────────────────
def fig_pty_session_topology():
    W, H = 1000, 580
    p = []

    # Ліва колонка: Простір емулятора (GUI / SSH)
    p.append(rect(30, 60, 260, 480, fill=SOFT, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(160, 85, "ПРОСТІР КОРИСТУВАЧА", size=11, color=MUTED, bold=True))
    p.append(text(160, 105, "Емулятор термінала", size=13, color=INK, bold=True))

    p.append(rect(50, 125, 220, 100, fill=COLD, stroke=NEG, sw=1.5, rx=6))
    p.append(text(160, 150, "Процес GUI (Alacritty / GNOME)", size=12, color=NEG, bold=True))
    p.append(mtext(160, 175, [
        "PID = 4120",
        "Тримає master_fd = 3",
        "Читає клавіші, малює вікно"
    ], size=11, color=INK, lh=1.3))

    p.append(rect(50, 245, 220, 100, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(160, 270, "Подія закриття вікна", size=12, color=POS, bold=True))
    p.append(mtext(160, 295, [
        "Клік [X] або розрив TCP",
        "close(master_fd)",
        "Вихід процесу GUI"
    ], size=11, color=INK, lh=1.3))

    p.append(rect(50, 365, 220, 155, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(160, 390, "Керівний сокет / X11", size=12, color=INK, bold=True))
    p.append(mtext(160, 415, [
        "Wayland / X11 з'єднання",
        "або мережевий сокет SSH",
        "Втрата дескриптора",
        "ініціює ланцюг ядра"
    ], size=11, color=MUTED, lh=1.3))

    # Центральна колонка: Ядро та PTY пара
    p.append(rect(320, 60, 300, 480, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8))
    p.append(text(470, 85, "ПРОСТІР ЯДРА (KERNEL SPACE)", size=11, color="#495057", bold=True))
    p.append(text(470, 105, "Драйвер псевдотермінала (PTY)", size=13, color=INK, bold=True))

    p.append(rect(340, 130, 260, 90, fill=COLD, stroke=NEG, sw=1.5, rx=6))
    p.append(text(470, 155, "PTY Master (/dev/ptmx)", size=12, color=NEG, bold=True))
    p.append(mtext(470, 178, [
        "Дескриптор у процесі емулятора",
        "Лічильник відкриттів: refcount",
        "Буфери вводу / виводу"
    ], size=11, color=INK, lh=1.3))

    p.append(line(470, 220, 470, 260, color=MUTED, sw=2, dash="4,4"))
    p.append(text(470, 245, "Лінійна дисципліна N_TTY", size=10, color=MUTED, italic=True))

    p.append(rect(340, 260, 260, 110, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(470, 285, "PTY Slave (/dev/pts/3)", size=12, color=FIELD, bold=True))
    p.append(mtext(470, 308, [
        "Керівний TTY сеансу (SID 5001)",
        "Дескриптори 0, 1, 2 процесів",
        "Передній PGID: tcsetpgrp()",
        "Стан: активний або hung up"
    ], size=11, color=INK, lh=1.3))

    p.append(rect(340, 390, 260, 130, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(470, 415, "Маршрутизатор сигналів ядра", size=12, color=POS, bold=True))
    p.append(mtext(470, 438, [
        "pty_close() -> tty_vhangup()",
        "Генерація SIGHUP -> SID 5001",
        "SIGCONT для зупинених груп",
        "Скидання session->tty = NULL"
    ], size=11, color=INK, lh=1.3))

    # Права колонка: Сеанс і процеси
    p.append(rect(650, 60, 320, 480, fill=SOFT, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(810, 85, "СЕАНС КОРИСТУВАЧА (SID = 5001)", size=11, color=MUTED, bold=True))
    p.append(text(810, 105, "Ієрархія процесів сеансу", size=13, color=INK, bold=True))

    p.append(rect(670, 125, 280, 100, fill=PURPLE, stroke=PURPLE_STROKE, sw=1.5, rx=6))
    p.append(text(810, 150, "Лідер сеансу (Session Leader)", size=12, color=PURPLE_STROKE, bold=True))
    p.append(mtext(810, 175, [
        "Оболонка Bash (PID=5001, PGID=5001)",
        "Керує таблицею завдань (Jobs)",
        "Отримує SIGHUP першим від ядра"
    ], size=11, color=INK, lh=1.3))

    p.append(rect(670, 245, 280, 125, fill=COLD, stroke=NEG, sw=1.5, rx=6))
    p.append(text(810, 270, "Група переднього плану (Foreground)", size=12, color=NEG, bold=True))
    p.append(mtext(810, 295, [
        "Текстовий редактор Neovim",
        "PID = 5210, PGID = 5210",
        "Володіє терміналом (tcgetpgrp = 5210)",
        "Отримує ввід з PTY Slave"
    ], size=11, color=INK, lh=1.3))

    p.append(rect(670, 390, 280, 130, fill=WARN, stroke=WARN_STROKE, sw=1.5, rx=6))
    p.append(text(810, 415, "Фонові групи (Background Jobs)", size=12, color=WARN_STROKE, bold=True))
    p.append(mtext(810, 440, [
        "Компіляція: make -j4 (PGID=5300)",
        "Зупинений процес: sleep (PGID=5400)",
        "У таблиці завдань оболонки",
        "Отримують SIGHUP від Bash"
    ], size=11, color=INK, lh=1.3))

    # З'єднувальні стрілки
    p.append(arrow(270, 175, 340, 175, color=NEG, sw=2))
    p.append(arrow(340, 315, 270, 315, color=FIELD, sw=2))
    p.append(arrow(600, 315, 670, 175, color=PURPLE_STROKE, sw=2))
    p.append(arrow(600, 315, 670, 305, color=NEG, sw=2))
    p.append(arrow(600, 455, 670, 455, color=POS, sw=2))

    render(os.path.join(OUT, "pty-session-topology.svg"), W, H, *p, title="ТОПОЛОГІЯ ТЕРМІНАЛЬНОГО СЕАНСУ ТА ГРУП ПРОЦЕСІВ")


# ── 2. Каскад Hangup в ядрі ──────────────────────────────────────────────────
def fig_hangup_cascade():
    W, H = 1040, 560
    p = []

    steps = [
        ("1. Закриття дескриптора", "GUI емулятор / SSH завершується", "close(master_fd)", "refcount майстра падає до 0", WARM, POS),
        ("2. Фіксація розриву ядром", "Драйвер PTY переводить slave у hung up", "tty_vhangup() / pty_close()", "read -> EOF (0), write -> EIO", WARN, WARN_STROKE),
        ("3. Сигнал лідеру сесії", "Ядро знаходить лідера сесії за SID", "kill(SID, SIGHUP)", "Оболонка Bash отримує сигнал 1", COLD, NEG),
        ("4. Поширення таблицею завдань", "Оболонка обходить jobs table", "kill(-pgid, SIGHUP)", "Розсилка фоновим групам процесу", PURPLE, PURPLE_STROKE),
        ("5. Пробудження зупинених", "Зупинені процеси розбуджуються", "kill(-pgid, SIGCONT)", "Обробка SIGHUP у розбуджених", GREENFILL, FIELD),
        ("6. Від'єднання термінала", "Ядро очищає керівний термінал", "session->tty = NULL", "Доступ до /dev/tty дає ENXIO", SOFT, MUTED)
    ]

    x_left = 60
    box_w = 420
    box_h = 115
    y_gap = 145

    # Ліва колонка: кроки 1, 2, 3
    for i in range(3):
        title, sub, code_txt, desc, fill_c, stroke_c = steps[i]
        y = 70 + i * y_gap
        p.append(rect(x_left, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        p.append(text(x_left + 20, y + 25, title, size=12, color=stroke_c, bold=True, anchor="start"))
        p.append(text(x_left + 20, y + 48, sub, size=13, color=INK, bold=True, anchor="start"))
        p.append(rect(x_left + 20, y + 60, 380, 24, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
        p.append(text(x_left + 30, y + 76, code_txt, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x_left + 20, y + 102, desc, size=11, color=MUTED, anchor="start"))

        if i < 2:
            p.append(arrow(x_left + box_w // 2, y + box_h, x_left + box_w // 2, y + y_gap, color=MUTED, sw=2))

    # Стрілка переходу між колонками
    p.append(arrow(x_left + box_w, 70 + 2 * y_gap + box_h // 2, x_left + 500, 70 + box_h // 2, color=POS, sw=2.5))
    p.append(text(500, 240, "Перехід", size=10, color=POS, bold=True))

    # Права колонка: кроки 4, 5, 6
    x_right = 560
    for i in range(3, 6):
        title, sub, code_txt, desc, fill_c, stroke_c = steps[i]
        y = 70 + (i - 3) * y_gap
        p.append(rect(x_right, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        p.append(text(x_right + 20, y + 25, title, size=12, color=stroke_c, bold=True, anchor="start"))
        p.append(text(x_right + 20, y + 48, sub, size=13, color=INK, bold=True, anchor="start"))
        p.append(rect(x_right + 20, y + 60, 380, 24, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
        p.append(text(x_right + 30, y + 76, code_txt, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x_right + 20, y + 102, desc, size=11, color=MUTED, anchor="start"))

        if i < 5:
            p.append(arrow(x_right + box_w // 2, y + box_h, x_right + box_w // 2, y + y_gap, color=MUTED, sw=2))

    render(os.path.join(OUT, "hangup-cascade.svg"), W, H, *p, title="ХРОНОЛОГІЯ КАСКАДУ РОЗРИВУ ЗВ'ЯЗКУ (HANGUP CASCADE)")


# ── 3. Порівняння механізмів виживання ────────────────────────────────────────
def fig_survival_mechanisms():
    W, H = 1040, 560
    p = []

    cols = [
        ("За замовчуванням", WARM, POS, [
            "Диспозиція: SIG_DFL",
            "Дескриптори: PTY slave",
            "Таблиця завдань: присутній",
            "Сеанс: старий SID",
            "Результат при закритті:",
            "Отримує SIGHUP",
            "Загибель процесу (Term)"
        ]),
        ("nohup", WARN, WARN_STROKE, [
            "Диспозиція: SIG_IGN",
            "Дескриптори: nohup.out / null",
            "Таблиця завдань: присутній",
            "Сеанс: старий SID",
            "Результат при закритті:",
            "Ігнорує сигнал SIGHUP",
            "Виживає, ввід/вивід у файл"
        ]),
        ("disown", COLD, NEG, [
            "Диспозиція: не змінюється",
            "Дескриптори: PTY slave (!)",
            "Таблиця завдань: видалено",
            "Сеанс: старий SID",
            "Результат при закритті:",
            "Оболонка не шле сигнал",
            "Виживає, ризик EIO на TTY"
        ]),
        ("setsid", PURPLE, PURPLE_STROKE, [
            "Диспозиція: не змінюється",
            "Дескриптори: успадковані",
            "Таблиця завдань: відсутній",
            "Сеанс: новий SID=PID (без TTY)",
            "Результат при закритті:",
            "Ядро не знає про процес",
            "Повна ізоляція від сеансу"
        ]),
        ("tmux / screen", GREENFILL, FIELD, [
            "Диспозиція: звичайна",
            "Дескриптори: внутрішній PTY",
            "Таблиця завдань: у tmux shell",
            "Сеанс: tmux server session",
            "Результат при закритті:",
            "PTY master тримає сервер",
            "Процес працює без перерв"
        ])
    ]

    card_w = 180
    card_h = 460
    start_x = 40
    gap_x = 20

    for idx, (name, fill_c, stroke_c, lines) in enumerate(cols):
        x = start_x + idx * (card_w + gap_x)
        y = 65
        p.append(rect(x, y, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        p.append(rect(x, y, card_w, 45, fill=stroke_c, stroke=stroke_c, sw=1.8, rx=8))
        p.append(rect(x, y + 25, card_w, 20, fill=stroke_c, stroke=stroke_c, sw=0))
        p.append(text(x + card_w // 2, y + 28, name, size=12, color="#ffffff", bold=True))

        p.append(line(x + 10, y + 180, x + card_w - 10, y + 180, color=stroke_c, sw=1, dash="3,3"))

        # Параметри
        for l_idx, line_txt in enumerate(lines[:4]):
            p.append(text(x + 12, y + 70 + l_idx * 26, line_txt, size=10, color=INK, anchor="start"))

        # Підсумок
        p.append(text(x + card_w // 2, y + 205, lines[4], size=10, color=stroke_c, bold=True))
        p.append(text(x + card_w // 2, y + 235, lines[5], size=11, color=INK, bold=True))
        p.append(text(x + card_w // 2, y + 260, lines[6], size=11, color=stroke_c, bold=True))

        # Нижня графічна плашка зі статусом
        status_fill = "#fdecea" if idx == 0 else "#eafaf1"
        status_color = POS if idx == 0 else FIELD
        status_text = "ЗНИЩУЄТЬСЯ" if idx == 0 else "ВИЖИВАЄ"
        p.append(rect(x + 15, y + 390, card_w - 30, 45, fill=status_fill, stroke=status_color, sw=1.5, rx=6))
        p.append(text(x + card_w // 2, y + 418, status_text, size=12, color=status_color, bold=True))

    render(os.path.join(OUT, "survival-mechanisms.svg"), W, H, *p, title="ПОРІВНЯННЯ СТРАТЕГІЙ ЗБЕРЕЖЕННЯ ПРОЦЕСІВ ПРИ РОЗРИВІ TTY")


if __name__ == "__main__":
    fig_pty_session_topology()
    fig_hangup_cascade()
    fig_survival_mechanisms()
    print("OK: generated 3 figures in img/")
