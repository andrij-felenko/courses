# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tradeoff():
    """Порівняння 4 критеріїв Річарда Ґебріела: підхід MIT проти підходу Нью-Джерсі."""
    W, H = 820, 520
    parts = []

    # Заголовок зверху
    parts.append(text(W / 2, 28, "Чотири критерії Ґебріела: MIT проти Нью-Джерсі", size=16, bold=True, color=INK))

    # Дві головні колонки: ліва — MIT, права — New Jersey
    col_w = 370
    gap = 20
    left_x = (W - (2 * col_w + gap)) / 2 + col_w / 2
    right_x = left_x + col_w + gap

    # Заголовки колонок
    h_mit, _, _ = textbox(left_x, 65, "Підхід MIT («Роби як слід»)\nПріоритет: чистий інтерфейс", size=13, pad=10, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True, min_w=col_w)
    h_nj, _, _ = textbox(right_x, 65, "Підхід Нью-Джерсі («Worse is Better»)\nПріоритет: проста реалізація", size=13, pad=10, fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=col_w)
    parts.append(h_mit)
    parts.append(h_nj)

    # 4 блоки критеріїв
    rows = [
        (
            150,
            "1. ПРОСТОТА",
            "Інтерфейс має бути простим.\nРеалізація може бути як завгодно\nскладною заради зручності користувача.",
            "Реалізація МАЄ бути простою.\nПростота інтерфейсу бажана, але\nпростота реалізації завжди вища.",
        ),
        (
            245,
            "2. КОРЕКТНІСТЬ",
            "Абсолютна в усіх аспектах.\nНекоректність неприпустима,\nкрайові випадки покриваються на 100%.",
            "Коректна в усіх спостережуваних аспектах.\nКраще мати просту систему, ніж\nускладнювати її заради 1% рідкісних країв.",
        ),
        (
            340,
            "3. УЗГОДЖЕНІСТЬ",
            "Сувора ортогональність правил.\nЖодних винятків чи спеціальних випадків\nв інтерфейсі не дозволяється.",
            "Узгодженість важлива, але нею можна\nпоступитися: краще дозволити виняток,\nніж роздувати ядро складністю.",
        ),
        (
            435,
            "4. ПОВНОТА",
            "Покриває всі передбачувані ситуації.\nУсі системні випадки мають бути\nповністю вирішені ядром.",
            "Покриває лише практичні щоденні задачі.\nПовнотою жертвують першою заради\nзбереження простоти реалізації.",
        ),
    ]

    for y_pos, title, mit_txt, nj_txt in rows:
        # Підпис критерію по центру
        parts.append(text(W / 2, y_pos - 18, title, size=11, bold=True, color=MUTED))

        # Блоки для MIT та NJ
        b_mit, _, _ = textbox(left_x, y_pos + 12, mit_txt, size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK, min_w=col_w)
        b_nj, _, _ = textbox(right_x, y_pos + 12, nj_txt, size=11, pad=8, fill="#f4f6f8", stroke=LINE, color=INK, min_w=col_w)
        parts.append(b_mit)
        parts.append(b_nj)

    render(os.path.join(IMG, 'mit-vs-nj-tradeoff.svg'), W, H, *parts)


def fig_syscall():
    """Анатомія переривання виклику: приховання складності в ядрі (MIT) проти EINTR у просторі користувача (Unix)."""
    W, H = 840, 480
    parts = []

    # Заголовок
    parts.append(text(W / 2, 26, "Обробка перерваного вводу-виводу: де живе складність", size=15, bold=True, color=INK))

    # Секція 1: MIT / ITS
    sec1_y = 60
    parts.append(text(50, sec1_y, "1. Підхід MIT / ITS (автоматичний перезапуск PC-restart)", size=13, bold=True, color=NEG, anchor="start"))
    
    # Ланцюжок MIT: 4 кроки
    steps_mit = [
        (130, sec1_y + 48, "read() у ядро\nПочаток IO", "#eaf0fd", NEG),
        (330, sec1_y + 48, "Сигнал / переривання\nЯдро зберігає PC і стан", "#fdecea", POS),
        (530, sec1_y + 48, "Обробник сигналу\nЯдро відновлює виклик", "#eaf0fd", NEG),
        (730, sec1_y + 48, "Повернення даних\nЗастосунок не знає про збій", "#eafaf1", FIELD),
    ]
    for i, (sx, sy, txt, fill_c, strk_c) in enumerate(steps_mit):
        b, bw, _ = textbox(sx, sy, txt, size=11, pad=8, fill=fill_c, stroke=strk_c, color=INK, min_w=160)
        parts.append(b)
        if i < len(steps_mit) - 1:
            next_sx = steps_mit[i + 1][0]
            parts.append(arrow(sx + bw / 2 + 3, sy, next_sx - 83, sy, color=LINE, sw=1.5))

    parts.append(text(W / 2, sec1_y + 105, "Ціна: величезна складність ядра (стеки, реентрабельність, розмотування). Простір користувача чистий.", size=11, italic=True, color=MUTED))

    # Розділювач
    parts.append(line(50, 245, W - 50, 245, color="#d0d7de", sw=1, dash="4 4"))

    # Секція 2: New Jersey / Unix
    sec2_y = 270
    parts.append(text(50, sec2_y, "2. Підхід Нью-Джерсі / Unix (повернення помилки EINTR)", size=13, bold=True, color=POS, anchor="start"))

    # Ланцюжок NJ: 4 кроки
    steps_nj = [
        (130, sec2_y + 48, "read() у ядро\nПочаток IO", "#fdecea", POS),
        (330, sec2_y + 48, "Сигнал / переривання\nЯдро негайно скидає IO", "#fdecea", POS),
        (530, sec2_y + 48, "Повернення -1\nerrno = EINTR", "#fdecea", POS),
        (730, sec2_y + 48, "Цикл retry у софті\nПовторний виклик read()", "#eafaf1", FIELD),
    ]
    for i, (sx, sy, txt, fill_c, strk_c) in enumerate(steps_nj):
        b, bw, _ = textbox(sx, sy, txt, size=11, pad=8, fill=fill_c, stroke=strk_c, color=INK, min_w=160)
        parts.append(b)
        if i < len(steps_nj) - 1:
            next_sx = steps_nj[i + 1][0]
            parts.append(arrow(sx + bw / 2 + 3, sy, next_sx - 83, sy, color=LINE, sw=1.5))

    parts.append(text(W / 2, sec2_y + 105, "Ціна: ядро елементарне й легко портується. Кожен прикладний програміст зобов'язаний писати цикл повтору.", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'syscall-interruption.svg'), W, H, *parts)


def fig_evolution():
    """Еволюційний маховик Worse is Better: як простота реалізації захоплює екосистему."""
    W, H = 820, 480
    parts = []

    # Заголовок
    parts.append(text(W / 2, 28, "Еволюційний маховик Worse is Better", size=16, bold=True, color=INK))

    # Центр кола
    cx, cy = W / 2, 255

    nodes = [
        (cx, cy - 145, "1. Проста реалізація\nМінімальний обсяг коду ядра,\nнемає складних машин стану", "#eaf0fd", NEG),
        (cx + 250, cy, "2. Легке портування\nПеренесення на новий процесор\nза лічені тижні / дні", "#eafaf1", FIELD),
        (cx, cy + 145, "3. Вірусне впровадження\nСистема працює всюди,\nвитісняє дорогі аналоги", "#fdecea", POS),
        (cx - 250, cy, "4. Доопрацювання зверху\nСпільнота пише бібліотеки\nй закриває вади ядра", "#fdf6e2", "#b58900"),
    ]

    boxes = []
    for nx, ny, txt, fill_c, strk_c in nodes:
        b, bw, bh = textbox(nx, ny, txt, size=11, pad=10, fill=fill_c, stroke=strk_c, color=INK, bold=False, min_w=200)
        boxes.append((nx, ny, bw, bh))
        parts.append(b)

    # З'єднувальні стрілки по колу
    parts.append(arrow(cx + 120, cy - 120, cx + 220, cy - 50, color=LINE, sw=2))
    parts.append(arrow(cx + 220, cy + 50, cx + 120, cy + 120, color=LINE, sw=2))
    parts.append(arrow(cx - 120, cy + 120, cx - 220, cy + 50, color=LINE, sw=2))
    parts.append(arrow(cx - 220, cy - 50, cx - 120, cy - 120, color=LINE, sw=2))

    # Центральний блок-висновок
    core, _, _ = textbox(cx, cy, "Результат:\n«Гірша» система\nстає світовим\nстандартом", size=13, pad=12, fill="#ffffff", stroke=INK, color=INK, bold=True, min_w=140)
    parts.append(core)

    render(os.path.join(IMG, 'evolutionary-cycle.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_tradeoff()
    fig_syscall()
    fig_evolution()
    print("All figures generated successfully.")
