# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_hump():
    """Крива складності по номеру системи: 1 — ощадна, 2 — роздута (пік небезпеки), 3 — вгамована."""
    W, H = 720, 400
    parts = []
    # осі
    ox, oy = 90, 320          # початок координат
    ax_w, ax_h = 560, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # X
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # Y
    parts.append(text(ox - 12, oy - ax_h + 4, "складність", size=13, color=MUTED, anchor="end"))
    parts.append(text(ox - 12, oy - ax_h + 20, "рішення", size=13, color=MUTED, anchor="end"))
    parts.append(text(ox + ax_w, oy + 26, "яка це система за рахунком", size=13, color=MUTED, anchor="end"))

    # три точки по X
    x1, x2, x3 = ox + 90, ox + 280, ox + 470
    # висоти (від осі вгору): 1 — низько, 2 — пік, 3 — середньо
    y1 = oy - 70
    y2 = oy - 225
    y3 = oy - 120
    # рівень "потрібного" (пунктир) — куди складність мала б сісти
    need = oy - 115
    parts.append(line(ox, need, ox + ax_w, need, color=FIELD, sw=1.6, dash="7 5"))
    parts.append(text(ox + ax_w - 4, need - 8, "стеля потрібного", size=12, color=FIELD, anchor="end"))

    # крива через точки (проста ламана з плавним піком)
    parts.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f" '
                  'fill="none" stroke="%s" stroke-width="3"/>' % (
                      x1, y1, (x1 + x2) / 2, y2 - 30, x2, y2,
                      (x2 + x3) / 2, y2 + 10, x3, y3, POS)))

    # маркери-точки
    for (px, py, col) in ((x1, y1, INK), (x2, y2, POS), (x3, y3, FIELD)):
        parts.append(circle(px, py, 7, fill=col, stroke=col, sw=1))

    # підписи точок — розставлені з запасом, поза кривою
    b1, w1, h1 = textbox(x1, oy - 30, "Перша\nощадна, чиста", size=12, fill="#eef1f4", stroke=INK)
    b2, w2, h2 = textbox(x2, y2 - 42, "Друга\nроздута — пік\nнебезпеки", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    b3, w3, h3 = textbox(x3, oy - 34, "Третя\nвгамована\nдосвідом", size=12, fill="#eafaf1", stroke=FIELD)
    parts.append(b1)
    parts.append(b2)
    parts.append(b3)

    render(os.path.join(IMG, 'hump.svg'), W, H, *parts)


def fig_forces():
    """Що надуває другу систему і що її стримує: три сили тиснуть, дисципліна — клапан."""
    W, H = 720, 430
    parts = []
    # центр — "друга система"
    cx, cy = 360, 250
    core, cw, ch = textbox(cx, cy, "ДРУГА\nСИСТЕМА", size=16, pad=16,
                           fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=170)
    # три джерела тиску згори
    srcs = [
        (150, 70, "Упевненість\n«тепер я знаю, як треба»", NEG),
        (360, 55, "Відкладений список\nвсе, що вирізали з першої", NEG),
        (570, 70, "Престиж великого\nхочеться показати розмах", NEG),
    ]
    boxes = []
    for (sx, sy, label, col) in srcs:
        b, bw, bh = textbox(sx, sy, label, size=12, fill="#eaf0fd", stroke=col)
        boxes.append((sx, sy, bh))
        parts.append(b)
    # стрілки від джерел до ядра (тиск усередину)
    top_core = cy - ch / 2
    for (sx, sy, bh) in boxes:
        parts.append(arrow(sx, sy + bh / 2 + 4, cx + (sx - cx) * 0.28, top_core - 8, color=POS, sw=2))

    parts.append(core)

    # клапан-дисципліна знизу — стримує роздування
    vy = 360
    valve, vw, vh = textbox(cx, vy, "Самодисципліна: ціна кожної риси на очах · пріоритети архітектора · YAGNI",
                            size=12, pad=12, fill="#eafaf1", stroke=FIELD, color=INK, min_w=520)
    parts.append(valve)
    # стрілка від клапана вгору до ядра (протитиск)
    parts.append(arrow(cx, vy - vh / 2 - 4, cx, cy + ch / 2 + 6, color=FIELD, sw=2.4))

    render(os.path.join(IMG, 'forces.svg'), W, H, *parts)


def fig_cost_ledger():
    """Три цінники МК: роздутий драйвер проти чесного мінімуму (LOC / RAM / робота на читання)."""
    W, H = 760, 448
    parts = []

    # заголовки колонок
    col_bloat_x = 470       # центр колонки "роздутий"
    col_lean_x = 650        # центр колонки "чесний"
    head_y = 60
    parts.append(text(col_bloat_x, head_y, "Роздутий драйвер", size=14, color=POS, bold=True))
    parts.append(text(col_lean_x, head_y, "Чесний мінімум", size=14, color=FIELD, bold=True))
    parts.append(text(40, head_y, "Цінник МК", size=14, color=MUTED, anchor="start", bold=True))

    # рядки: (мітка ліворуч, значення роздутого, значення чесного)
    rows = [
        ("Рядки коду\n(читати й супроводжувати)", "~140", "1"),
        ("RAM під реєстр\n44 Б × 8 записів", "352 Б", "0 Б"),
        ("Робота на кожне читання", "strcmp +\nнепрямий BLX", "пряме\nмноження"),
    ]

    row_top = 95
    row_h = 100
    left_x = 40
    for i, (label, bloat, lean) in enumerate(rows):
        cy = row_top + i * row_h + row_h / 2 - 10
        # мітка рядка ліворуч
        parts.append(mtext(left_x, cy - (label.count("\n")) * 8, label,
                           size=12, color=INK, anchor="start"))
        # клітина роздутого
        bb, bw, bh = textbox(col_bloat_x, cy, bloat, size=13, pad=12,
                             fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=150)
        parts.append(bb)
        # клітина чесного
        lb, lw, lh = textbox(col_lean_x, cy, lean, size=13, pad=12,
                             fill="#eafaf1", stroke=FIELD, color=INK, bold=True, min_w=120)
        parts.append(lb)
        # роздільна лінія між рядками
        if i > 0:
            sep_y = row_top + i * row_h - 6
            parts.append(line(left_x, sep_y, W - 30, sep_y, color=FIELD, sw=0.8, dash="3 4"))

    # підсумковий рядок унизу
    foot_y = row_top + len(rows) * row_h + 6
    fb, fw, fh = textbox(W / 2, foot_y + 12,
                         "Кожен знятий шматок — не оптимізація, а повернення роботи, якої не було потреби робити",
                         size=12, pad=10, fill="#eef1f4", stroke=MUTED, color=INK, min_w=W - 80)
    parts.append(fb)

    render(os.path.join(IMG, 'cost-ledger.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_hump()
    fig_forces()
    fig_cost_ledger()
    print("ok")
