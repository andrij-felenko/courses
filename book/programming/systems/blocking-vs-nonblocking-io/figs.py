# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо (чотири рівні вгору від book/programming/systems/blocking-vs-nonblocking-io)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. io-latency-gap: часова прірва між CPU, пам'яттю та периферією ─────────
def fig_io_latency_gap():
    W, H = 840, 360
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))
    p.append(text(W / 2, 42, "Прірва затримок: чому ввід-вивід вимагає зупинки або асинхронності", size=13, color=INK, bold=True))
    p.append(text(W / 2, 60, "Порівняння часу доступу в реальних одиницях та в масштабі процесорних тактів (3.3 ГГц)", size=10.5, color=MUTED, italic=True))

    items = [
        ("Регістри CPU / L1-кеш", "0.3 – 1 нс", "1 – 3 такти", 70, "#eff6ff", NEG),
        ("Оперативна пам'ять (DRAM)", "50 – 100 нс", "150 – 300 тактів", 150, "#eff6ff", NEG),
        ("Твердотільний диск (NVMe SSD)", "10 – 50 мкс", "30 000 – 150 000 тактів", 310, "#fef3c7", "#d97706"),
        ("Локальна мережа (10 GbE LAN)", "50 – 200 мкс", "150 000 – 600 000 тактів", 470, "#fff1f2", POS),
        ("Інтернет / WAN (через континент)", "50 – 150 мс", "150 000 000 – 500 000 000 тактів", 690, "#fff1f2", POS),
    ]

    sy = 85
    bar_h = 36

    for title_txt, real_time, cpu_cycles, bar_len_px, fill_c, stroke_c in items:
        p.append(text(35, sy + 22, title_txt, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(255, sy + 22, real_time, size=10.5, color=MUTED, bold=False, anchor="start"))
        bx = 350
        bw = bar_len_px / 2.05
        p.append(rect(bx, sy + 6, bw, bar_h - 12, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        p.append(text(bx + bw + 12, sy + 22, cpu_cycles, size=10, color=stroke_c, bold=True, anchor="start"))
        sy += 46

    p.append(line(35, H - 55, W - 35, H - 55, color="#cbd5e1", sw=1, dash="4,4"))
    p.append(text(W / 2, H - 32, "Поки CPU чекає 1 пакет з мережі (100 мс), він міг би виконати 300 мільйонів обчислень", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "io-latency-gap.svg"), W, H, *p,
           title="Прірва затримок між процесором та пристроями вводу-виводу")


# ── 2. blocking-lifecycle: життєвий цикл блокуючого виклику в ядрі ────────────
def fig_blocking_lifecycle():
    W, H = 840, 420
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(W / 2, 40, "Анатомія блокуючого виклику read() у ядрі ОС", size=13, color=INK, bold=True))
    p.append(text(W / 2, 58, "Взаємодія простору користувача, планувальника ядра та апаратних переривань", size=10.5, color=MUTED, italic=True))

    col_w = 240
    c1_x, c2_x, c3_x = 35, 300, 565

    p.append(rect(c1_x, 75, col_w, 310, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(c1_x + col_w / 2, 95, "Простір користувача (User)", size=11.5, color=INK, bold=True))

    p.append(rect(c2_x, 75, col_w, 310, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    p.append(text(c2_x + col_w / 2, 95, "Ядро / Планувальник (Kernel)", size=11.5, color=NEG, bold=True))

    p.append(rect(c3_x, 75, col_w, 310, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(c3_x + col_w / 2, 95, "Апаратура / Мережа (NIC / DMA)", size=11.5, color=FIELD, bold=True))

    steps = [
        (c1_x + 15, 115, 210, 32, "1. read(fd, buf, size)", "#ffffff", INK, True),
        (c2_x + 15, 115, 210, 32, "2. Перевірка буфера: порожній", "#dbeafe", NEG, False),
        (c2_x + 15, 160, 210, 38, "3. Стан: TASK_INTERRUPTIBLE\nПотік додано у wait_queue", "#fee2e2", POS, False),
        (c2_x + 15, 210, 210, 34, "4. schedule(): перемикання CPU\nна інший потік процесу", "#fef3c7", "#d97706", False),
        (c3_x + 15, 210, 210, 34, "5. Пакет прибув з мережі →\nDMA запис у sk_buff RAM", "#dcfce7", FIELD, False),
        (c3_x + 15, 256, 210, 32, "6. Апаратне переривання IRQ", "#dcfce7", FIELD, True),
        (c2_x + 15, 298, 210, 34, "7. wake_up(): стан TASK_RUNNING\nПотік повертається в чергу CPU", "#dbeafe", NEG, False),
        (c1_x + 15, 342, 210, 32, "8. Копіювання в buf, read() > 0", "#dcfce7", FIELD, True),
    ]

    for bx, by, bw, bh, btxt, bfill, bcol, is_bold in steps:
        p.append(rect(bx, by, bw, bh, fill=bfill, stroke=bcol, sw=1, rx=4))
        if "\n" in btxt:
            parts = btxt.split("\n")
            p.append(text(bx + bw / 2, by + 14, parts[0], size=9.5, color=bcol, bold=is_bold))
            p.append(text(bx + bw / 2, by + 27, parts[1], size=9, color=bcol, bold=False))
        else:
            p.append(text(bx + bw / 2, by + 20, btxt, size=9.5, color=bcol, bold=is_bold))

    p.append(arrow(c1_x + 225, 131, c2_x + 15, 131, color=NEG, sw=1.5))
    p.append(arrow(c3_x + 15, 272, c2_x + 225, 305, color=FIELD, sw=1.5))
    p.append(arrow(c2_x + 15, 358, c1_x + 225, 358, color=FIELD, sw=1.5))

    p.append(text(W / 2, H - 12, "Потік спить у черзі очікування сокета без витрати процесорного часу до появи сигналу від DMA/IRQ", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "blocking-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл блокуючого системного виклику в ядрі")


# ── 3. blocking-vs-nonblocking-flow: порівняння потоків виконання ─────────────
def fig_blocking_vs_nonblocking_flow():
    W, H = 840, 430
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))
    p.append(text(W / 2, 40, "Парадигми вводу-виводу: Блокування проти Неблокуючого Мультиплексування", size=13, color=INK, bold=True))
    p.append(text(W / 2, 58, "Поведінка системного виклику при відсутності та появі даних у сокеті", size=10.5, color=MUTED, italic=True))

    lx, ly, lw, lh = 35, 75, 365, 320
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(lx + lw / 2, ly + 24, "Блокуючий ввід-вивід (Blocking I/O)", size=12, color=POS, bold=True))

    rx, ry, rw, rh = 440, 75, 365, 320
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(rx + rw / 2, ry + 24, "Неблокуючий ввід-вивід + Мультиплексор", size=12, color=NEG, bold=True))

    b_steps = [
        (ly + 40, "Виклик read(fd, ...)", "#eff6ff", NEG),
        (ly + 82, "Немає даних → Ядро заморожує потік", "#fee2e2", POS),
        (ly + 128, "ПОТІК СПИТЬ (блокування потоку)\nРесурси стека заблоковано", "#fef2f2", POS),
        (ly + 185, "Дані надійшли в буфер сокета", "#f0fdf4", FIELD),
        (ly + 227, "Ядро будить потік → копіює дані", "#eff6ff", NEG),
        (ly + 269, "read() повертає N байтів", "#dcfce7", FIELD)
    ]
    for b_y, b_txt, b_bg, b_col in b_steps:
        p.append(rect(lx + 20, b_y, lw - 40, 36, fill=b_bg, stroke=b_col, sw=1, rx=5))
        if "\n" in b_txt:
            t1, t2 = b_txt.split("\n")
            p.append(text(lx + lw / 2, b_y + 14, t1, size=9.5, color=b_col, bold=True))
            p.append(text(lx + lw / 2, b_y + 27, t2, size=9.5, color=MUTED))
        else:
            p.append(text(lx + lw / 2, b_y + 22, b_txt, size=10, color=b_col, bold=True))

    nb_steps = [
        (ry + 40, "epoll_wait() / kqueue() спить на пулі fd", "#eff6ff", NEG),
        (ry + 85, "Подія: сокет #42 готовий до читання", "#dcfce7", FIELD),
        (ry + 130, "read(fd_42) у неблокуючому режимі", "#eff6ff", NEG),
        (ry + 175, "Читання порції даних (наприклад, 4 КБ)", "#f0fdf4", FIELD),
        (ry + 220, "read() → EAGAIN (буфер вичерпано)", "#fef3c7", "#d97706"),
        (ry + 265, "Повернення в epoll_wait для інших fd", "#eff6ff", NEG)
    ]
    for n_y, n_txt, n_bg, n_col in nb_steps:
        p.append(rect(rx + 20, n_y, rw - 40, 36, fill=n_bg, stroke=n_col, sw=1, rx=5))
        p.append(text(rx + rw / 2, n_y + 22, n_txt, size=10, color=n_col, bold=True))

    p.append(text(W / 2, H - 12, "1 потік на 1 блокуючий клієнт (обмеження пам'яті) проти 1 потоку на 100 000 неблокуючих з'єднань", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "blocking-vs-nonblocking-flow.svg"), W, H, *p,
           title="Порівняння потоків виконання: блокуючий ввід-вивід проти неблокуючого з мультиплексуванням")


if __name__ == "__main__":
    fig_io_latency_gap()
    fig_blocking_lifecycle()
    fig_blocking_vs_nonblocking_flow()
    print("All figures generated successfully.")
