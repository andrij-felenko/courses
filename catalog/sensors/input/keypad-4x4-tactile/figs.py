# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Матрична клавіатура 4×4 (тактильна)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

KEYS = [["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]]


# ── 1. Що це за плата: 16 тактових кнопок S1..S16 у сітці 4×4 і гребінка 8 пінів ──
def fig_board():
    W, H = 900, 560
    f = [text(W / 2, 30, "Плата: 16 тактових кнопок у сітці 4×4 і 8-контактна гребінка збоку",
              size=15, bold=True)]

    # корпус плати
    bx, by, bw, bh = 120, 70, 470, 420
    f.append(rect(bx, by, bw, bh, fill="#eef4f0", stroke=INK, sw=2.0, rx=16))
    f.append(text(bx + 14, by + 24, "друкована плата 43×39 мм", size=11, bold=True, color=MUTED, anchor="start"))

    # сітка кнопок
    n = 4
    gx, gy = bx + 60, by + 66
    step = 92
    idx = 1
    for r in range(n):
        for c in range(n):
            cx = gx + c * step
            cy = gy + r * step
            # тактова кнопка: квадратний корпус зі штовхачем
            f.append(rect(cx - 22, cy - 22, 44, 44, fill=BG, stroke=INK, sw=1.6, rx=5))
            f.append(circle(cx, cy, 10, fill="#dfe6ee", stroke=INK, sw=1.4))
            f.append(text(cx, cy + 5, KEYS[r][c], size=15, bold=True, color=INK))
            f.append(text(cx - 22, cy - 26, "S%d" % idx, size=8.5, color=MUTED, anchor="start"))
            idx += 1

    # гребінка 8 пінів праворуч від плати
    hx = bx + bw + 40
    hy0 = by + 60
    hstep = 44
    f.append(text(hx + 20, hy0 - 22, "гребінка (8 штирів)", size=11, bold=True, color=INK, anchor="middle"))
    labels = [("Col3", FIELD), ("Col2", FIELD), ("Col1", FIELD), ("Col0", FIELD),
              ("Row0", POS), ("Row1", POS), ("Row2", POS), ("Row3", POS)]
    for i, (lab, col) in enumerate(labels):
        py = hy0 + i * hstep
        # доріжка від краю плати до штиря
        f.append(line(bx + bw, py, hx, py, color=col, sw=1.6))
        f.append(rect(hx, py - 9, 20, 18, fill=BG, stroke=col, sw=1.8, rx=3))
        f.append(text(hx + 30, py + 4, lab, size=11, bold=True, color=col, anchor="start"))

    b, _, _ = textbox(W / 2, 526,
                      "16 кнопок — а назовні лише 8 проводів: 4 стовпці (Col) і 4 рядки (Row).\n"
                      "Кожна кнопка сидить на перетині свого рядка й стовпця.",
                      size=11, fill=BG, stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "board.svg"), W, H, *f)


# ── 2. Внутрішня схема: кнопка на кожному перетині рядок×стовпець (16 = 4×4) ──────
def fig_matrix():
    W, H = 820, 660
    f = [text(W / 2, 30, "Внутрішня схема: кнопка на кожному перетині — 4 рядки × 4 стовпці = 16 кнопок",
              size=14.5, bold=True)]

    # координати сітки
    left, top = 150, 90
    step = 130
    rows_y = [top + i * step for i in range(4)]
    cols_x = [left + j * step for j in range(4)]
    x_end = cols_x[-1] + 70
    y_end = rows_y[-1] + 70

    # горизонтальні шини (рядки)
    for i, ry in enumerate(rows_y):
        f.append(line(left - 60, ry, x_end, ry, color=POS, sw=1.8))
        f.append(circle(left - 60, ry, 5, fill=BG, stroke=POS, sw=2))
        f.append(text(left - 72, ry + 4, "Row%d" % i, size=11, bold=True, color=POS, anchor="end"))

    # вертикальні шини (стовпці)
    for j, cx in enumerate(cols_x):
        f.append(line(cx, top - 60, cx, y_end, color=FIELD, sw=1.8))
        f.append(circle(cx, top - 60, 5, fill=BG, stroke=FIELD, sw=2))
        f.append(text(cx, top - 68, "Col%d" % j, size=11, bold=True, color=FIELD))

    # кнопка на кожному перетині — крихітний розрив + значок кнопки
    for i, ry in enumerate(rows_y):
        for j, cx in enumerate(cols_x):
            # кнопка як «місток» між рядком і стовпцем: коротка похила рисочка з двома контактами
            f.append(circle(cx, ry, 4, fill=BG, stroke=INK, sw=1.4))     # контакт на стовпці
            f.append(circle(cx + 22, ry, 4, fill=BG, stroke=INK, sw=1.4)) # контакт на рядку
            f.append(line(cx + 4, ry, cx + 18, ry, color=INK, sw=1.4))    # відведення до рядка
            # штовхач кнопки — коротка коса рисочка над розривом (розімкнено)
            f.append(line(cx, ry, cx + 6, ry - 12, color=INK, sw=2.0))
            f.append(text(cx + 12, ry + 18, KEYS[i][j], size=11, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, y_end + 55,
                      "Кожна кнопка з'єднує СВІЙ рядок зі СВОЇМ стовпцем, лише коли натиснута.\n"
                      "Стовпці й рядки не торкаються ніде більше — тому 8 проводів обслуговують 16 кнопок.",
                      size=11, fill=BG, stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "matrix.svg"), W, H, *f)


# ── 3. Сканування: один стовпець тягнемо в LOW, рядки з підтяжками читаємо ───────
def fig_scan():
    W, H = 860, 600
    f = [text(W / 2, 30, "Сканування: одному стовпцю даємо LOW, решту — HIGH; читаємо рядки з підтяжками",
              size=14, bold=True)]

    left, top = 190, 110
    step = 118
    rows_y = [top + i * step for i in range(4)]
    cols_x = [left + j * step for j in range(4)]
    x_end = cols_x[-1] + 60
    y_end = rows_y[-1] + 55

    active_col = 1          # активний (LOW) стовпець
    pressed = (2, 1)        # натиснута кнопка (row2, col1) — «8»

    # рядки — входи з підтяжкою до +
    for i, ry in enumerate(rows_y):
        f.append(line(left - 50, ry, x_end, ry, color=INK, sw=1.6))
        # підтяжка ліворуч
        f.append(rect(left - 96, ry - 8, 16, 16, fill=BG, stroke=POS, sw=1.4, rx=3))
        f.append(line(left - 88, ry - 8, left - 88, ry - 24, color=POS, sw=1.4))
        f.append(text(left - 88, ry - 28, "+", size=12, bold=True, color=POS))
        f.append(line(left - 80, ry, left - 50, ry, color=INK, sw=1.6))
        # стан рядка
        state = "LOW" if i == pressed[0] else "HIGH"
        scol = POS if state == "LOW" else FIELD
        f.append(text(x_end + 12, ry + 4, "Row%d = %s" % (i, state), size=11, bold=True, color=scol, anchor="start"))

    # стовпці — виходи, активний у LOW
    for j, cx in enumerate(cols_x):
        drv = "LOW" if j == active_col else "HIGH"
        dcol = POS if drv == "LOW" else MUTED
        f.append(line(cx, top - 62, cx, y_end, color=(POS if j == active_col else FIELD),
                      sw=(2.4 if j == active_col else 1.4)))
        f.append(text(cx, top - 70, "Col%d" % j, size=11, bold=True, color=FIELD))
        f.append(text(cx, top - 86, drv, size=10, bold=True, color=dcol))

    # кнопки на перетинах
    for i, ry in enumerate(rows_y):
        for j, cx in enumerate(cols_x):
            is_pressed = (i, j) == pressed
            r = 5 if is_pressed else 4
            fillc = "#fdecea" if is_pressed else BG
            f.append(circle(cx, ry, r, fill=fillc, stroke=(POS if is_pressed else MUTED),
                            sw=(2.2 if is_pressed else 1.2)))
            if is_pressed:
                # замкнута кнопка з'єднала LOW-стовпець із рядком → рядок просів у LOW
                f.append(text(cx + 12, ry - 10, "натиснуто «8»", size=10, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, y_end + 48,
                      "Активний стовпець Col1 у LOW. Натиснута кнопка на перетині Col1×Row2 тягне Row2 у LOW —\n"
                      "решта рядків лишаються HIGH завдяки підтяжкам. LOW-рядок при LOW-стовпці = натиснута клавіша.",
                      size=10.5, fill="#fff8e6", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "scan.svg"), W, H, *f)


# ── 4. Примара (ghosting): три кнопки в кутах прямокутника → четверта «натиснута» ──
def fig_ghost():
    W, H = 900, 560
    f = [text(W / 2, 28, "Примара: три кнопки в кутах прямокутника вдають четверту (без діодів)",
              size=14.5, bold=True)]

    # маленька матриця 3×3, показуємо кути прямокутника (2 рядки × 2 стовпці)
    left, top = 210, 100
    step = 150
    rows_y = [top + i * step for i in range(2)]
    cols_x = [left + j * step for j in range(2)]

    # шини
    for i, ry in enumerate(rows_y):
        f.append(line(left - 70, ry, cols_x[-1] + 70, ry, color=INK, sw=1.6))
        f.append(text(left - 82, ry + 4, "Row%d" % i, size=11, bold=True, color=POS, anchor="end"))
    for j, cx in enumerate(cols_x):
        f.append(line(cx, top - 70, cx, rows_y[-1] + 70, color=INK, sw=1.6))
        f.append(text(cx, top - 78, "Col%d" % j, size=11, bold=True, color=FIELD))

    # активний стовпець Col0 = LOW (сканер), Col1 читається
    f.append(text(cols_x[0], top - 96, "LOW (скан)", size=10, bold=True, color=POS))

    # три натиснуті кнопки: (0,0),(0,1),(1,0); примара — (1,1)
    real = [(0, 0), (0, 1), (1, 0)]
    ghost = (1, 1)
    for (i, j) in real:
        cx, cy = cols_x[j], rows_y[i]
        f.append(circle(cx, cy, 7, fill="#d5f0e0", stroke=FIELD, sw=2.4))
        f.append(text(cx + 12, cy - 12, "натиснуто", size=9.5, bold=True, color=FIELD, anchor="start"))
    gx, gy = cols_x[ghost[1]], rows_y[ghost[0]]
    f.append(circle(gx, gy, 7, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(gx + 12, gy + 20, "ПРИМАРА (не натиснута,\nа виглядає як натиснута)",
                  size=9.5, bold=True, color=POS, anchor="start"))

    # шлях-обхід струму: Col0(LOW) → кнопка(1,0) → Row1 → кнопка(0,0)? — покажемо стрілками контур
    # обхідний контур: LOW заходить у Row0 через (0,0), біжить по Row0 у (0,1), спускається в Col1,
    # і Col1 бачить LOW навіть без справжнього натиску (1,1)
    path = [(cols_x[0], rows_y[0]), (cols_x[1], rows_y[0]), (cols_x[1], rows_y[1])]
    for k in range(len(path) - 1):
        (x1, y1), (x2, y2) = path[k], path[k + 1]
        f.append(arrow(x1, y1, x2, y2, color=POS, sw=2.4))

    b, _, _ = textbox(W / 2, 470,
                      "LOW зі скан-стовпця біжить через натиснуту (0,0) у Row0, по Row0 — у натиснуту (0,1),\n"
                      "звідти в Col1 — і Col1 бачить LOW, наче натиснули (1,1). Мінімум для примари — ТРИ кнопки.\n"
                      "Ліки: діод послідовно з кожною кнопкою — пускає струм лише в один бік, обхід зникає.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "ghost.svg"), W, H, *f)


# ── 5. Підключення пін-у-пін: 8 штирів клавіатури → 8 GPIO мікроконтролера ───────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 30, "Підключення: 8 штирів (4 Row + 4 Col) — на 8 будь-яких цифрових GPIO",
              size=14.5, bold=True)]

    kx, ky, kw, kh = 70, 80, 250, 330
    f.append(rect(kx, ky, kw, kh, fill="#eef4f0", stroke=INK, sw=2.0, rx=14))
    f.append(text(kx + kw / 2, ky + 26, "клавіатура 4×4", size=14, bold=True, color=INK))
    f.append(text(kx + kw / 2, ky + 44, "тактильна (S1..S16)", size=9.5, color=MUTED))

    pins = [("Col3", FIELD), ("Col2", FIELD), ("Col1", FIELD), ("Col0", FIELD),
            ("Row0", POS), ("Row1", POS), ("Row2", POS), ("Row3", POS)]
    p_y0 = ky + 70
    p_step = 34
    for i, (lab, col) in enumerate(pins):
        py = p_y0 + i * p_step
        f.append(circle(kx + kw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(kx + kw - 16, py + 4, lab, size=11, bold=True, color=col, anchor="end"))

    bx, by, bw, bh = 620, 80, 250, 330
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 26, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))

    tgts = [("D9", FIELD), ("D8", FIELD), ("D7", FIELD), ("D6", FIELD),
            ("D5", POS), ("D4", POS), ("D3", POS), ("D2", POS)]
    t_y0 = by + 70
    for i, (lab, col) in enumerate(tgts):
        ty = t_y0 + i * p_step
        f.append(circle(bx, ty, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, ty + 4, lab, size=11, bold=True, color=col, anchor="start"))

    for i in range(8):
        py = p_y0 + i * p_step
        ty = t_y0 + i * p_step
        f.append(line(kx + kw + 6, py, bx - 6, ty, color=pins[i][1], sw=1.8))

    b, _, _ = textbox(W / 2, 440,
                      "Жодного живлення й землі: клавіатура — просто 8 проводів, самі кнопки. Підтяжки на рядкові входи\n"
                      "беруть ВНУТРІШНІ (INPUT_PULLUP). Порядок пінів — за маркуванням плати, будь-які 8 цифрових GPIO.",
                      size=10.5, fill="#fff8e6", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки proj-keypad-scan.md (драйвер сканування + антибрязкіт)
# ══════════════════════════════════════════════════════════════════════════════

# ── P1. Чому наївний скан дає «555»: брязкіт у часі й що бачить debounce ──────────
def fig_scan_bounce():
    W, H = 940, 520
    f = [text(W / 2, 30, "Один натиск, а лічильник бачить пачку: брязкіт у часі й що з ним робить антибрязкіт",
              size=14, bold=True)]

    # вісь часу
    ax0, ax1 = 90, 860
    yl = 130                     # рівень «сирого» сигналу з ніжки
    f.append(text(ax0 - 26, yl - 42, "сира\nніжка", size=10, bold=True, color=MUTED, anchor="middle"))

    # сирий сигнал рядка: HIGH(1) до натиску, потім пачка брязкоту, потім стабільний LOW(0), потім відпускання
    hi, lo = yl - 34, yl + 6     # рівні для 1 і 0 (LOW = натиснуто)
    # відрізки (x_start, x_end, level): 1 = HIGH(відпущено), 0 = LOW(натиснуто)
    seq = [(ax0, 250, 1),
           (250, 262, 0), (262, 270, 1), (270, 280, 0), (280, 286, 1), (286, 296, 0),  # брязкіт входу ~1..10 мс
           (296, 560, 0),                                                                # стабільно натиснуто
           (560, 572, 1), (572, 578, 0), (578, 590, 1),                                  # брязкіт відпускання
           (590, ax1, 1)]
    prev_lvl = None
    prev_x = None
    for (xs, xe, lvl) in seq:
        yy = hi if lvl == 1 else lo
        f.append(line(xs, yy, xe, yy, color=INK, sw=2.0))
        if prev_lvl is not None and prev_lvl != lvl:
            f.append(line(prev_x, hi, prev_x, lo, color=INK, sw=2.0))
        prev_lvl, prev_x = lvl, xe
    f.append(text(ax0 - 6, hi + 4, "HIGH", size=9, color=MUTED, anchor="end"))
    f.append(text(ax0 - 6, lo + 4, "LOW", size=9, color=POS, anchor="end"))

    # позначки зон брязкоту
    for (bx0, bx1, lbl) in [(250, 296, "брязкіт\n~1..10 мс"), (560, 590, "брязкіт\nвідпускання")]:
        f.append(rect(bx0, hi - 20, bx1 - bx0, (lo - hi) + 46, fill="none", stroke=POS, sw=1.2, rx=4))
        f.append(text((bx0 + bx1) / 2, lo + 42, lbl, size=9, bold=True, color=POS))

    # що бачить НАЇВНИЙ скан (реагує на кожне LOW) — під віссю
    yn = 300
    f.append(text(ax0 - 26, yn + 4, "наївний\nскан", size=10, bold=True, color=POS, anchor="middle"))
    for cx in [256, 275, 291, 566, 584]:
        f.append(circle(cx, yn, 6, fill="#fdecea", stroke=POS, sw=2.0))
    b1, _, _ = textbox(675, yn, "→ у поле лягає «5 5 5»\n(один натиск = кілька)", size=10.5,
                       fill="#fdecea", stroke=POS, bold=False)
    f.append(b1)

    # що бачить debounce: чекає, поки стан устоявся T_db мс, тоді один подій
    yd = 390
    f.append(text(ax0 - 26, yd + 4, "з анти-\nбрязкотом", size=10, bold=True, color=FIELD, anchor="middle"))
    # вікно очікування стабільності після першого краю
    f.append(line(296, yd - 22, 296, yd + 22, color=FIELD, sw=1.4, dash="4,3"))
    f.append(text(340, yd - 30, "стан устоявся ≥ T_db → зараховуємо", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(circle(360, yd, 7, fill="#d5f0e0", stroke=FIELD, sw=2.2))
    f.append(text(372, yd + 4, "рівно ОДИН «5»", size=10.5, bold=True, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 470,
                      "Механічний контакт після дотику кілька разів відскакує (1..10 мс) — сира ніжка дає пачку LOW-HIGH.\n"
                      "Наївний скан рахує кожне LOW окремим натиском («555»). Антибрязкіт чекає, поки стан УСТОЯВСЯ на T_db мс,\n"
                      "і лише тоді зараховує один натиск — та сама пачка стає єдиною подією.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "scan_bounce.svg"), W, H, *f)


# ── P2. Розкладка (keymap): фізичний (row,col) → символ; переплутані піни зсувають букви ──
def fig_keymap():
    W, H = 940, 560
    f = [text(W / 2, 28, "Розкладка keymap: індекс (рядок, стовпець) → символ; порядок пінів вирішує, ЯКА буква вийде",
              size=13.5, bold=True)]

    KEYS = [["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]]

    # ── зліва: правильна відповідність rowPins/colPins → правильна сітка ──
    gx0, gy0, cell = 120, 130, 62
    f.append(text(gx0 + 2 * cell, gy0 - 46, "правильний порядок пінів", size=11, bold=True, color=FIELD))
    # підписи стовпців (colPins) зверху
    for j in range(4):
        f.append(text(gx0 + j * cell + cell / 2, gy0 - 16, "Col%d" % j, size=9.5, bold=True, color=FIELD))
    for i in range(4):
        f.append(text(gx0 - 14, gy0 + i * cell + cell / 2 + 4, "Row%d" % i, size=9.5, bold=True, color=POS, anchor="end"))
        for j in range(4):
            x = gx0 + j * cell
            y = gy0 + i * cell
            f.append(rect(x, y, cell - 8, cell - 8, fill="#eef7f1", stroke=INK, sw=1.3, rx=6))
            f.append(text(x + (cell - 8) / 2, y + (cell - 8) / 2 + 6, KEYS[i][j], size=17, bold=True, color=INK))
    # підкреслимо натиснуту фізичну кнопку (row2,col1) → «8»
    hx, hy = gx0 + 1 * cell, gy0 + 2 * cell
    f.append(rect(hx, hy, cell - 8, cell - 8, fill="none", stroke=POS, sw=2.6, rx=6))
    f.append(text(hx + (cell - 8) / 2, hy + (cell - 8) + 16, "натиснули тут", size=9, bold=True, color=POS))
    f.append(text(gx0 + 2 * cell, gy0 + 4 * cell + 34, "getKey() → '8'  ✓", size=13, bold=True, color=FIELD))

    # ── справа: два стовпці переплутано (Col1↔Col2) → та сама кнопка дає іншу букву ──
    sx0 = 560
    order = [0, 2, 1, 3]         # colPins переплутано: стовпці 1 і 2 помінялись
    f.append(text(sx0 + 2 * cell, gy0 - 46, "переплутано Col1↔Col2", size=11, bold=True, color=POS))
    for jj in range(4):
        realcol = order[jj]
        f.append(text(sx0 + jj * cell + cell / 2, gy0 - 16, "Col%d" % realcol, size=9.5, bold=True, color=POS))
    for i in range(4):
        f.append(text(sx0 - 14, gy0 + i * cell + cell / 2 + 4, "Row%d" % i, size=9.5, bold=True, color=POS, anchor="end"))
        for jj in range(4):
            realcol = order[jj]
            x = sx0 + jj * cell
            y = gy0 + i * cell
            f.append(rect(x, y, cell - 8, cell - 8, fill="#fdeeec", stroke=INK, sw=1.3, rx=6))
            f.append(text(x + (cell - 8) / 2, y + (cell - 8) / 2 + 6, KEYS[i][realcol], size=17, bold=True, color=INK))
    # та сама ФІЗИЧНА кнопка (row2, фізичний col1) тепер сидить у видимій позиції jj=2
    jj_pos = order.index(1)
    hx2, hy2 = sx0 + jj_pos * cell, gy0 + 2 * cell
    f.append(rect(hx2, hy2, cell - 8, cell - 8, fill="none", stroke=POS, sw=2.6, rx=6))
    f.append(text(hx2 + (cell - 8) / 2, hy2 + (cell - 8) + 16, "та сама кнопка", size=9, bold=True, color=POS))
    f.append(text(sx0 + 2 * cell, gy0 + 4 * cell + 34, "getKey() → '9'  ✗", size=13, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 500,
                      "keymap[row][col] — це просто таблиця: фізичний перетин (рядок, стовпець) обирає з неї символ.\n"
                      "Переплутав порядок у rowPins[] чи colPins[] — індекс зсунувся, і та сама кнопка віддає ІНШУ букву.\n"
                      "Нічого не горить, помилки нема — просто «8» перетворюється на «9». Ліки: звірити порядок пінів тестером.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)
    render(os.path.join(IMG, "keymap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_board()
    fig_matrix()
    fig_scan()
    fig_ghost()
    fig_wiring()
    fig_scan_bounce()
    fig_keymap()
    print("keypad-4x4-tactile figs done ->", IMG)
