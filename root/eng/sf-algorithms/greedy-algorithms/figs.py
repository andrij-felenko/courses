# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEDY_COL = POS       # червоний / акцент для жадібного вибору
OPT_COL    = FIELD     # зелений для оптимального / глобального розв'язку
NEUT_COL   = "#2457d6" # синій для базових елементів

# ── ФІГУРА 1: Локальний крок проти глобального перебору ──────────────────────
def fig_greedy_choice_step():
    W, H = 900, 390
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Жадібний вибір: локально оптимальний крок проти повного перебору",
                  size=16, bold=True))

    # Ліва панель: Жадібний алгоритм
    lx0, lw = 30, 400
    p.append(rect(lx0, 55, lw, 260, fill="#fdfaf6", stroke=GREEDY_COL, sw=1.8, rx=10))
    p.append(text(lx0 + lw / 2, 80, "Жадібна стратегія (O(n log n))", size=14.5, color=GREEDY_COL, bold=True))
    p.append(text(lx0 + lw / 2, 102, "Один безповоротний крок на кожному етапі", size=12, color=MUTED))

    # Вузли жадібного шляху
    g_nodes = [
        (lx0 + 60, 160, "Стан 0"),
        (lx0 + 200, 160, "Крок 1"),
        (lx0 + 340, 160, "Крок 2")
    ]
    for i, (nx, ny, nlbl) in enumerate(g_nodes):
        if i > 0:
            px, py, _ = g_nodes[i - 1]
            p.append(arrow(px + 35, py, nx - 35, ny, color=GREEDY_COL, sw=2.0))
            p.append(text((px + nx) / 2, py - 14, "max", size=11, color=GREEDY_COL, bold=True))
        tb, tw, th = textbox(nx, ny, nlbl, size=12, pad=8, fill="#fff5f5", stroke=GREEDY_COL, bold=(i > 0))
        p.append(tb)

    p.append(text(lx0 + lw / 2, 235, "Ніяких повернень (No backtracking)", size=12.5, color=INK, bold=True))
    p.append(text(lx0 + lw / 2, 258, "Рішення приймається безапеляційно", size=11.5, color=MUTED))

    # Права панель: Повний перебір / ДП
    rx0, rw = 470, 400
    p.append(rect(rx0, 55, rw, 260, fill="#f6fdf8", stroke=OPT_COL, sw=1.8, rx=10))
    p.append(text(rx0 + rw / 2, 80, "Повний перебір / ДП (O(2ⁿ) або O(n³))", size=14.5, color=OPT_COL, bold=True))
    p.append(text(rx0 + rw / 2, 102, "Обчислення всіх можливих гілок і варіантів", size=12, color=MUTED))

    # Дерево варіантів
    r_root = (rx0 + 200, 140, "Корінь")
    r_left = (rx0 + 100, 195, "Гілка A")
    r_mid  = (rx0 + 200, 195, "Гілка B")
    r_right = (rx0 + 300, 195, "Гілка C")

    p.append(arrow(r_root[0] - 15, r_root[1] + 15, r_left[0] + 15, r_left[1] - 15, color=MUTED, sw=1.5))
    p.append(arrow(r_root[0], r_root[1] + 15, r_mid[0], r_mid[1] - 15, color=OPT_COL, sw=2.2))
    p.append(arrow(r_root[0] + 15, r_root[1] + 15, r_right[0] - 15, r_right[1] - 15, color=MUTED, sw=1.5))

    tb, _, _ = textbox(r_root[0], r_root[1], r_root[2], size=12, pad=8, fill="#ffffff", stroke=LINE)
    p.append(tb)
    tb, _, _ = textbox(r_left[0], r_left[1], r_left[2], size=11, pad=7, fill="#ffffff", stroke=MUTED)
    p.append(tb)
    tb, _, _ = textbox(r_mid[0], r_mid[1], r_mid[2], size=11, pad=7, fill="#e8f8ed", stroke=OPT_COL, bold=True)
    p.append(tb)
    tb, _, _ = textbox(r_right[0], r_right[1], r_right[2], size=11, pad=7, fill="#ffffff", stroke=MUTED)
    p.append(tb)

    p.append(text(rx0 + rw / 2, 245, "Порівняння всіх підзадач", size=12.5, color=INK, bold=True))
    p.append(text(rx0 + rw / 2, 268, "Гарантує оптимум ціною високої складності", size=11.5, color=MUTED))

    # Нижня висновкова примітка
    note, _, _ = textbox(W / 2, H - 35,
                         "Жадібний вибір зменшує розмірність задачі за один крок без побудови дерева підзадач.",
                         size=12.5, pad=10, fill="#f4f6f8", stroke=LINE)
    p.append(note)

    render(os.path.join(OUT, "greedy-choice-step.svg"), W, H, *p)


# ── ФІГУРА 2: Інтервальне планування ─────────────────────────────────────────
def fig_interval_scheduling():
    W, H = 940, 420
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 28, "Інтервальне планування: вибір інтервалів з найранішим фінішем",
                  size=15.5, bold=True))

    # Вісь часу
    x_start, x_end = 100, 760
    y_axis = 75
    p.append(line(x_start, y_axis, x_end, y_axis, color=INK, sw=2.0))
    p.append(text(x_start - 30, y_axis + 4, "Час t", size=12, color=INK, bold=True))

    # Засічки на осі часу
    for t_val in range(0, 11):
        tx = x_start + t_val * (x_end - x_start) / 10
        p.append(line(tx, y_axis - 5, tx, y_axis + 5, color=INK, sw=1.5))
        p.append(text(tx, y_axis - 12, str(t_val), size=11, color=MUTED))

    # Інтервали (start, end, label, is_selected)
    intervals = [
        (0, 3, "I₁ [0, 3]", True),
        (1, 4, "I₂ [1, 4]", False),
        (2, 6, "I₃ [2, 6]", False),
        (3, 7, "I₄ [3, 7]", True),
        (5, 8, "I₅ [5, 8]", False),
        (7, 10, "I₆ [7, 10]", True),
    ]

    y_base = 115
    row_h = 36

    for idx, (st, fn, lbl, sel) in enumerate(intervals):
        iy = y_base + idx * row_h
        sx = x_start + st * (x_end - x_start) / 10
        ex = x_start + fn * (x_end - x_start) / 10
        w = ex - sx

        if sel:
            f_col = "#e8f8ed"
            s_col = OPT_COL
            t_col = OPT_COL
            tag = "  ✓ Обрано"
        else:
            f_col = "#fff5f5"
            s_col = GREEDY_COL
            t_col = MUTED
            tag = "  ✗ Конфлікт"

        p.append(rect(sx, iy, w, 24, fill=f_col, stroke=s_col, sw=1.8, rx=4))
        p.append(text(sx + w / 2, iy + 16, lbl, size=11.5, color=t_col, bold=sel))
        p.append(text(ex + 45, iy + 16, tag, size=11, color=t_col, anchor="start"))

    # Підсумкова примітка
    note, _, _ = textbox(W / 2, H - 32,
                         "Сортування за часом закінчення (finish time) гарантує максимально можливу кількість подій.",
                         size=12.5, pad=10, fill="#f4f6f8", stroke=LINE)
    p.append(note)

    render(os.path.join(OUT, "interval-scheduling.svg"), W, H, *p)


# ── ФІГУРА 3: Метод заміни (Exchange Argument) ────────────────────────────────
def fig_matroid_greedy_exchange():
    W, H = 880, 390
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 28, "Метод заміни (Exchange Argument) для доведення оптимальності",
                  size=15.5, bold=True))

    # Схема двох розв'язків G та O
    y1, y2 = 90, 200

    # Жадібний розв'язок G
    p.append(text(100, y1 + 18, "Жадібний розв'язок G:", size=13, color=GREEDY_COL, bold=True, anchor="start"))
    g_elems = ["g₁", "g₂", "g₃", "...", "gₖ"]
    for i, e in enumerate(g_elems):
        cx = 300 + i * 80
        col = GREEDY_COL if i == 2 else NEUT_COL
        bg_col = "#fff5f5" if i == 2 else "#ffffff"
        p.append(rect(cx - 25, y1, 50, 32, fill=bg_col, stroke=col, sw=1.8, rx=6))
        p.append(text(cx, y1 + 21, e, size=13, color=col, bold=(i == 2)))

    # Оптимальний розв'язок O
    p.append(text(100, y2 + 18, "Оптимальний розв'язок O:", size=13, color=OPT_COL, bold=True, anchor="start"))
    o_elems = ["g₁", "g₂", "o₃", "...", "oₖ"]
    for i, e in enumerate(o_elems):
        cx = 300 + i * 80
        col = OPT_COL if i == 2 else (NEUT_COL if i < 2 else MUTED)
        bg_col = "#e8f8ed" if i == 2 else "#ffffff"
        p.append(rect(cx - 25, y2, 50, 32, fill=bg_col, stroke=col, sw=1.8, rx=6))
        p.append(text(cx, y2 + 21, e, size=13, color=col, bold=(i == 2)))

    # Заміна o3 на g3
    p.append(arrow(460, y1 + 35, 460, y2 - 5, color=GREEDY_COL, sw=2.2))
    p.append(text(505, (y1 + y2) / 2 + 5, "Заміна o₃ → g₃", size=12, color=GREEDY_COL, bold=True, anchor="start"))

    # Пояснювальний блок нижче
    exp_txt = "Оскільки w(g₃) ≥ w(o₃), заміна не зменшує вагу: w(O') = w(O) − w(o₃) + w(g₃) ≥ w(O).\nОтже, трансформований розв'язок O' залишається оптимальним!"
    tb, _, _ = textbox(W / 2, 310, exp_txt, size=12.5, pad=12, fill="#fffdf5", stroke="#f59e0b", color="#78350f")
    p.append(tb)

    render(os.path.join(OUT, "matroid-greedy-exchange.svg"), W, H, *p)


if __name__ == "__main__":
    fig_greedy_choice_step()
    fig_interval_scheduling()
    fig_matroid_greedy_exchange()
    print("SVG figures generated successfully.")
