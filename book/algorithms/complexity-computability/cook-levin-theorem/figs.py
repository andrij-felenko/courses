# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Кука — Левіна» (book/algorithms/complexity-computability/cook-levin-theorem)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
COLOR_BG_BOX = "#f8fafc"
COLOR_GRID_BORDER = "#cbd5e1"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_BG = "#dbeafe"
COLOR_SUCCESS = "#059669"
COLOR_SUCCESS_BG = "#d1fae5"
COLOR_WARNING = "#d97706"
COLOR_WARNING_BG = "#fef3c7"
COLOR_MUTED = "#64748b"


def fig_tableau_grid():
    """Фігура 1: Таблиця обчислення недетермінованої машини Тюринга (p(n) x p(n))."""
    W, H = 1000, 560
    frags = []

    # Заголовок / пояснення зверху
    top_box, _, _ = textbox(500, 40,
                            "Таблиця обчислення NDTM: розмір (p(n)+1) × (p(n)+1)",
                            size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=12)
    frags.append(top_box)

    # Сітка таблиці
    grid_x, grid_y = 200, 100
    cell_w, cell_h = 75, 45
    cols = 8  # 0, 1, 2, ..., p(n)
    rows = 7  # 0, 1, 2, ..., p(n)

    # Підписи осей
    # Вісь часу (рядки)
    frags.append(text(80, grid_y + (rows * cell_h) / 2, "Час t (0..p(n))",
                      size=14, color=COLOR_ACCENT, bold=True))
    # Вісь стрічки (стовпчики)
    frags.append(text(grid_x + (cols * cell_w) / 2, grid_y - 25, "Комірки стрічки j (0 .. p(n))",
                      size=14, color=COLOR_ACCENT, bold=True))

    # Номери стовпчиків
    col_labels = ["0", "1", "2", "3", "...", "j", "...", "p(n)"]
    for c in range(cols):
        cx = grid_x + c * cell_w + cell_w / 2
        frags.append(text(cx, grid_y - 8, col_labels[c], size=13, color=COLOR_MUTED, bold=True))

    # Номери рядків та вміст
    row_labels = ["t = 0", "t = 1", "...", "t = i", "t = i+1", "...", "t = p(n)"]

    for r in range(rows):
        ry = grid_y + r * cell_h + cell_h / 2
        frags.append(text(grid_x - 45, ry, row_labels[r], size=13, color=COLOR_MUTED, bold=True))

        for c in range(cols):
            cx = grid_x + c * cell_w + cell_w / 2
            rx_left = grid_x + c * cell_w
            ry_top = grid_y + r * cell_h

            fill_c = COLOR_BG_BOX
            stroke_c = COLOR_GRID_BORDER
            sw_c = 1.0
            txt = ""
            txt_color = INK
            is_bold = False

            # Початковий рядок t = 0
            if r == 0:
                fill_c = "#eff6ff"
                stroke_c = "#93c5fd"
                if c == 0:
                    txt = "q0, w1"
                    txt_color = COLOR_ACCENT
                    is_bold = True
                elif c == 1:
                    txt = "w2"
                elif c == 2:
                    txt = "w3"
                elif c in (3, 5, 7):
                    txt = "⊔"
                    txt_color = COLOR_MUTED
                elif c in (4, 6):
                    txt = "..."

            # Проміжний рядок t = i (вікно переходу)
            elif r == 3:
                if c in (1, 2, 3):
                    fill_c = COLOR_WARNING_BG
                    stroke_c = COLOR_WARNING
                    sw_c = 2.0
                    if c == 2:
                        txt = "qi, a"
                        txt_color = COLOR_WARNING
                        is_bold = True
                    elif c == 1:
                        txt = "x"
                    else:
                        txt = "y"
                elif c in (0, 7):
                    txt = "⊔"
                    txt_color = COLOR_MUTED
                elif c in (4, 6):
                    txt = "..."

            # Рядок t = i+1
            elif r == 4:
                if c in (1, 2, 3):
                    fill_c = "#fef9c3"
                    stroke_c = "#eab308"
                    sw_c = 2.0
                    if c == 1:
                        txt = "q', x'"
                        txt_color = "#b45309"
                        is_bold = True
                    elif c == 2:
                        txt = "a'"
                    else:
                        txt = "y"
                elif c in (0, 7):
                    txt = "⊔"
                    txt_color = COLOR_MUTED
                elif c in (4, 6):
                    txt = "..."

            # Фінальний рядок t = p(n)
            elif r == rows - 1:
                fill_c = COLOR_SUCCESS_BG
                stroke_c = COLOR_SUCCESS
                if c == 3:
                    txt = "q_acc"
                    txt_color = COLOR_SUCCESS
                    is_bold = True
                elif c in (0, 1, 2, 5, 7):
                    txt = "⊔"
                    txt_color = COLOR_MUTED
                elif c in (4, 6):
                    txt = "..."

            # Заповнення порожніх рядків
            else:
                if c in (0, 7):
                    txt = "⊔"
                    txt_color = COLOR_MUTED
                elif c in (4, 6):
                    txt = "..."

            frags.append(rect(rx_left, ry_top, cell_w, cell_h, fill=fill_c, stroke=stroke_c, sw=sw_c))
            if txt:
                frags.append(text(cx, ry, txt, size=13, color=txt_color, bold=is_bold))

    # Рамка локального вікна переходу 2x3
    wx = grid_x + 1 * cell_w
    wy = grid_y + 3 * cell_h
    ww = 3 * cell_w
    wh = 2 * cell_h
    frags.append(rect(wx - 2, wy - 2, ww + 4, wh + 4, fill="none", stroke=COLOR_ACCENT, sw=2.5))

    # Підписи збоку від сітки
    legend_x = grid_x + cols * cell_w + 30

    b_start, _, _ = textbox(legend_x + 85, grid_y + cell_h / 2, "Початкова конфігурація\n(стан q0, вхід w1..wn)",
                            size=12, bold=False, fill="#eff6ff", stroke="#93c5fd", sw=1.2, pad=8)
    b_win, _, _ = textbox(legend_x + 85, grid_y + 3.5 * cell_h, "Локальне вікно 2×3:\nстан на t+1 залежить\nлише від сусіда на t",
                          size=12, bold=False, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=1.5, pad=8)
    b_acc, _, _ = textbox(legend_x + 85, grid_y + (rows - 0.5) * cell_h, "Приймальний стан q_accept\nзнайдено до кроку p(n)",
                          size=12, bold=False, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.2, pad=8)

    frags.extend([b_start, b_win, b_acc])

    # Зв'язуючі стрілки від легенди
    frags.append(arrow(legend_x + 5, grid_y + cell_h / 2, grid_x + cols * cell_w + 5, grid_y + cell_h / 2, color="#93c5fd", sw=1.5))
    frags.append(arrow(legend_x + 5, grid_y + 3.5 * cell_h, wx + ww + 5, wy + wh / 2, color=COLOR_WARNING, sw=1.5))
    frags.append(arrow(legend_x + 5, grid_y + (rows - 0.5) * cell_h, grid_x + cols * cell_w + 5, grid_y + (rows - 0.5) * cell_h, color=COLOR_SUCCESS, sw=1.5))

    # Нижній висновок
    bot_box, _, _ = textbox(500, 520,
                             "Булева формула Φ задовольняється ⟺ існує прийнятька таблиця розміру O(p(n)²)",
                             size=14, bold=True, fill="#f1f5f9", stroke="#64748b", sw=1.8, pad=10)
    frags.append(bot_box)

    render(os.path.join(IMG, "fig1-tableau-grid.svg"), W, H, *frags,
           title="Таблиця обчислення недетермінованої машини Тюринга")


def fig_reduction_tree():
    """Фігура 2: Каскад зведення Кука — Левіна та 21 NP-повна задача Карпа."""
    W, H = 1000, 480
    frags = []

    # 1. Будь-яка задача L в NP
    b1, w1, _ = textbox(150, 160, "Довільна задача L ∈ NP\n(NDTM M + вхід w)",
                        size=14, bold=True, fill="#eff6ff", stroke=COLOR_ACCENT, sw=2, pad=12)

    # 2. Таблиця обчислення
    b2, w2, _ = textbox(400, 160, "Таблиця обчислення\nрозм. (p(n)+1) × (p(n)+1)",
                        size=14, bold=True, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=2, pad=12)

    # 3. SAT (Теорема Кука — Левіна)
    b3, w3, _ = textbox(650, 160, "Теорема Кука — Левіна\nSAT (Здійсненність КНФ)",
                        size=15, bold=True, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2.5, pad=14)

    # 4. 3-SAT
    b4, w4, _ = textbox(900, 160, "3-SAT\n(3-КНФ)",
                        size=14, bold=True, fill="#fce7f3", stroke="#db2777", sw=2, pad=12)

    frags.extend([b1, b2, b3, b4])

    # Стрілки верхнього ланцюжка
    frags.append(arrow(150 + w1 / 2 + 5, 160, 400 - w2 / 2 - 5, 160, color=INK, sw=2))
    frags.append(arrow(400 + w2 / 2 + 5, 160, 650 - w3 / 2 - 5, 160, color=INK, sw=2.2))
    frags.append(arrow(650 + w3 / 2 + 5, 160, 900 - w4 / 2 - 5, 160, color=INK, sw=2))

    # Підписи під стрілками верхнього ланцюжка
    frags.append(text(275, 130, "кодування в сітку", size=12, color=COLOR_MUTED, bold=True))
    frags.append(text(525, 130, "булеві формули Φ", size=12, color=COLOR_MUTED, bold=True))
    frags.append(text(775, 130, "розбиття диз'юнктів", size=12, color=COLOR_MUTED, bold=True))

    # Нижня частина: 21 задача Карпа (1972)
    karp_y = 350
    karp_nodes = [
        ("Кліка / Незалежна множина", 180),
        ("Покриття вершин", 400),
        ("Гамільтонів цикл", 620),
        ("Сума підмножини", 840)
    ]

    frags.append(text(500, 280, "21 NP-повна задача Карпа (1972 рік)", size=14, color="#374151", bold=True))

    for label, kx in karp_nodes:
        kb, kw, _ = textbox(kx, karp_y + 20, label, size=13, bold=True, fill="#fff", stroke="#9ca3af", sw=1.5, pad=10)
        frags.append(kb)
        # Стрілки від 3-SAT до кожної задачі Карпа
        frags.append(arrow(900, 195, kx, karp_y - 5, color="#db2777", sw=1.8))

    # Головний висновок внизу
    bot_box, _, _ = textbox(500, 455,
                             "Кук і Левін довели NP-повноту SAT ➔ Карп довів NP-повноту сотень практичних задач",
                             size=13, bold=True, fill="#f1f5f9", stroke="#475569", sw=1.5, pad=8)
    frags.append(bot_box)

    render(os.path.join(IMG, "fig2-reduction-tree.svg"), W, H, *frags,
           title="Каскад зведення Кука — Левіна та 21 NP-повна задача Карпа")


def fig_window_transitions():
    """Фігура 3: Фізика машини Тюринга: локальне вікно 2x3."""
    W, H = 900, 420
    frags = []

    # Заголовок
    top_box, _, _ = textbox(450, 35,
                            "Перевірка коректності переходу: вікно розміру 2 × 3",
                            size=16, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(top_box)

    # Дві строки по 3 комірки
    cx_base = 300
    cy_t = 120
    cy_t1 = 220
    cw, ch = 90, 55

    # Крок t
    frags.append(text(cx_base - 100, cy_t + ch / 2, "Крок t:", size=15, color=INK, bold=True))
    t_cells = [("j-1", "a"), ("j (головка q)", "q, b"), ("j+1", "c")]
    for idx, (pos_label, val_label) in enumerate(t_cells):
        x = cx_base + idx * cw
        fill_c = COLOR_WARNING_BG if idx == 1 else "#f8fafc"
        stroke_c = COLOR_WARNING if idx == 1 else "#cbd5e1"
        frags.append(rect(x, cy_t, cw, ch, fill=fill_c, stroke=stroke_c, sw=2))
        frags.append(text(x + cw / 2, cy_t + 18, pos_label, size=11, color=COLOR_MUTED))
        frags.append(text(x + cw / 2, cy_t + 38, val_label, size=14, color=INK, bold=True))

    # Стрілка локальної залежності
    frags.append(arrow(cx_base + 1.5 * cw, cy_t + ch + 5, cx_base + 1.5 * cw, cy_t1 - 5, color=COLOR_ACCENT, sw=2.5))
    frags.append(text(cx_base + 1.5 * cw + 110, (cy_t + ch + cy_t1) / 2, "функція переходу δ",
                      size=13, color=COLOR_ACCENT, bold=True))

    # Крок t+1
    frags.append(text(cx_base - 100, cy_t1 + ch / 2, "Крок t+1:", size=15, color=INK, bold=True))
    t1_cells = [("j-1 (головка q')", "q', a'"), ("j", "b'"), ("j+1", "c")]
    for idx, (pos_label, val_label) in enumerate(t1_cells):
        x = cx_base + idx * cw
        fill_c = COLOR_ACCENT_BG if idx == 0 else "#f8fafc"
        stroke_c = COLOR_ACCENT if idx == 0 else "#cbd5e1"
        frags.append(rect(x, cy_t1, cw, ch, fill=fill_c, stroke=stroke_c, sw=2))
        frags.append(text(x + cw / 2, cy_t1 + 18, pos_label, size=11, color=COLOR_MUTED))
        frags.append(text(x + cw / 2, cy_t1 + 38, val_label, size=14, color=INK, bold=True))

    # Пояснення праворуч
    info_box, _, _ = textbox(cx_base + 3 * cw + 150, 190,
                             "Локальне правило:\nКомірка j у момент t+1\nзалежить ТІЛЬКИ від\nкомірок j-1, j, j+1\nу момент t.",
                             size=13, bold=False, fill="#eff6ff", stroke=COLOR_ACCENT, sw=1.5, pad=12)
    frags.append(info_box)

    # Нижній висновок
    bot_box, _, _ = textbox(450, 370,
                             "Локальність дозволяє виразити крок обчислення КНФ-формулою сталого розміру O(1) для кожного вікна",
                             size=13, bold=True, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.8, pad=10)
    frags.append(bot_box)

    render(os.path.join(IMG, "fig3-window-transitions.svg"), W, H, *frags,
           title="Локальність фізики машини Тюринга: вікно 2x3")


if __name__ == "__main__":
    fig_tableau_grid()
    fig_reduction_tree()
    fig_window_transitions()
    print("Всі фігури успішно згенеровано у теку img/")
