# -*- coding: utf-8 -*-
"""Фігури курс-кроку «Макетка й перший монтаж» (root/course/embedded/breadboard-prototyping).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG у ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

HOLE = "#c9ccd1"          # колір гнізда
HOLE_R = 3.0
STEP = 15                 # крок сітки в пікселях


def hole(cx, cy, fill=HOLE):
    return circle(cx, cy, HOLE_R, fill=fill, stroke="#9aa0a8", sw=0.8)


def hole_col(x, y0, n, fill=HOLE):
    """Стовпчик із n гнізд згори вниз."""
    s = ""
    for i in range(n):
        s += hole(x, y0 + i * STEP, fill)
    return s


# ── 1. anatomy.svg — карта прихованих з'єднань макетки ───────────────────────
def fig_anatomy():
    W, H = 720, 372
    parts = []
    left = 60
    cols = 20                       # вужча плата → чиста колонка приміток праворуч
    grid_w = cols * STEP
    board_r = left + grid_w - STEP  # x останнього гнізда

    # тіло плати
    parts.append(rect(left - 20, 22, grid_w + 20, H - 44, fill="#f7f8fa",
                       stroke=LINE, sw=1.6, rx=10))

    # верхня пара шин живлення
    ry1, ry2 = 46, 64
    parts.append(line(left, ry1 - 11, board_r, ry1 - 11, color=POS, sw=2))
    parts.append(text(left - 30, ry1 + 4, "+", size=16, color=POS, bold=True))
    parts.append(line(left, ry2 + 11, board_r, ry2 + 11, color=NEG, sw=2))
    parts.append(text(left - 30, ry2 + 5, "–", size=16, color=NEG, bold=True))
    for i in range(cols):
        x = left + i * STEP
        parts.append(hole(x, ry1))
        parts.append(hole(x, ry2))

    # центральна зона: два блоки по 5 рядків, канавка між ними
    top0 = 116
    gutter = 208
    bot0 = 244
    for i in range(cols):
        x = left + i * STEP
        parts.append(hole_col(x, top0, 5))
        parts.append(hole_col(x, bot0, 5))

    # канавка
    parts.append(rect(left - 8, gutter - 4, grid_w + 8 - STEP, 20,
                      fill="#eceef1", stroke="#c9ccd1", sw=1, rx=3))
    parts.append(text(left + (grid_w - STEP) / 2, gutter + 10,
                      "центральна канавка", size=11, color=MUTED, italic=True))

    # нижня пара шин
    ry3, ry4 = H - 58, H - 40
    for i in range(cols):
        x = left + i * STEP
        parts.append(hole(x, ry3))
        parts.append(hole(x, ry4))
    parts.append(line(left, ry3 - 11, board_r, ry3 - 11, color=POS, sw=2))
    parts.append(text(left - 30, ry3 + 4, "+", size=16, color=POS, bold=True))
    parts.append(line(left, ry4 + 11, board_r, ry4 + 11, color=NEG, sw=2))
    parts.append(text(left - 30, ry4 + 5, "–", size=16, color=NEG, bold=True))

    # ── примітки в чистій колонці праворуч від плати ──
    ann = board_r + 40           # ліва межа підписів
    ldx = board_r + 12           # звідки тягнути виноски

    # 1) стовпчик-вузол (верхня зона): підсвітити 2-й стовпчик
    hi = 1
    hx = left + hi * STEP
    parts.append(rect(hx - 7, top0 - 7, 14, 4 * STEP + 14, fill="none",
                      stroke=FIELD, sw=2, rx=6))
    parts.append(line(hx + 7, top0 + 2 * STEP, ann - 6, 96, color=FIELD, sw=1.2))
    parts.append(text(ann, 92, "стовпчик із 5 гнізд —", size=12, color=FIELD,
                      bold=True, anchor="start"))
    parts.append(text(ann, 108, "один спільний вузол", size=12, color=FIELD,
                      anchor="start"))

    # 2) канавка розриває стовпчик надвоє
    cx = left + (cols - 3) * STEP
    parts.append(line(cx, top0 + 4 * STEP + 4, cx, gutter - 4, color=POS, sw=1.6, dash="3,3"))
    parts.append(line(cx, gutter + 16, cx, bot0 - 4, color=POS, sw=1.6, dash="3,3"))
    parts.append(text(cx, gutter + 9, "✕", size=14, color=POS, bold=True))
    parts.append(line(cx + 6, gutter + 6, ann - 6, gutter + 6, color=POS, sw=1.2))
    parts.append(text(ann, gutter + 2, "канавка розриває", size=12, color=POS,
                      bold=True, anchor="start"))
    parts.append(text(ann, gutter + 18, "стовпчик надвоє:", size=12, color=POS,
                      anchor="start"))
    parts.append(text(ann, gutter + 34, "верх ≠ низ", size=12, color=POS,
                      anchor="start"))

    # 3) шини живлення вздовж усієї плати
    parts.append(line(board_r, ry1 - 11, ann - 6, 40, color=MUTED, sw=1.2))
    parts.append(text(ann, 36, "шини «+» і «–» —", size=12, color=MUTED,
                      bold=True, anchor="start"))
    parts.append(text(ann, 52, "уздовж усієї плати", size=12, color=MUTED,
                      anchor="start"))

    render(out("anatomy.svg"), W, H, *parts,
           title="Приховані з'єднання макетної плати")


# ── 2. schematic-to-board.svg — переклад схеми у монтаж ──────────────────────
def fig_s2b():
    W, H = 720, 340
    parts = []

    # ── ліворуч: схема ──
    sx = 40
    parts.append(text(sx + 80, 26, "схема", size=13, color=MUTED, bold=True))
    # рамка блоку схеми
    # плюсова й земляна шина
    pv, gv = 52, 300
    parts.append(line(sx, pv, sx + 170, pv, color=POS, sw=2))
    parts.append(text(sx - 6, pv - 6, "+5 В", size=11, color=POS, anchor="end"))
    parts.append(line(sx, gv, sx + 170, gv, color=NEG, sw=2))
    parts.append(text(sx - 6, gv + 4, "GND", size=11, color=NEG, anchor="end"))

    # гілка: кнопка -> вузол A
    bx = sx + 40
    parts.append(line(bx, pv, bx, 100, color=INK, sw=1.6))
    parts.append(rect(bx - 16, 100, 32, 26, fill="#fff", stroke=INK, sw=1.6, rx=3))
    parts.append(text(bx, 116, "SW", size=10, color=INK, bold=True))
    parts.append(line(bx, 126, bx, 168, color=INK, sw=1.6))       # до вузла A
    # підтяжка донизу від A
    parts.append(rect(bx - 9, 176, 18, 40, fill="#fff", stroke=INK, sw=1.6, rx=3))
    parts.append(text(bx + 26, 200, "10k", size=10, color=INK, anchor="middle"))
    parts.append(line(bx, 168, bx, 176, color=INK, sw=1.6))
    parts.append(line(bx, 216, bx, gv, color=INK, sw=1.6))
    parts.append(circle(bx, 168, 3, fill=INK, stroke=INK, sw=1))
    parts.append(text(bx - 12, 164, "A", size=11, color=FIELD, bold=True, anchor="end"))

    # гілка: R -> LED
    lx = sx + 130
    parts.append(line(lx, pv, lx, 110, color=INK, sw=1.6))
    parts.append(rect(lx - 9, 110, 18, 40, fill="#fff", stroke=INK, sw=1.6, rx=3))
    parts.append(text(lx + 26, 132, "330", size=10, color=INK, anchor="middle"))
    parts.append(line(lx, 150, lx, 168, color=INK, sw=1.6))
    # світлодіод — трикутник + риска
    parts.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#fff" stroke="%s" stroke-width="1.6"/>'
                 % (lx - 9, 168, lx + 9, 168, lx, 186, INK))
    parts.append(line(lx - 9, 186, lx + 9, 186, color=INK, sw=2))
    parts.append(text(lx + 24, 182, "LED", size=10, color=INK, anchor="middle"))
    parts.append(line(lx, 186, lx, gv, color=INK, sw=1.6))

    # стрілка переходу
    parts.append(arrow(sx + 200, H / 2, sx + 250, H / 2, color=FIELD, sw=2.4))
    parts.append(text(sx + 225, H / 2 - 12, "монтаж", size=11, color=FIELD, bold=True))

    # ── праворуч: макетка ──
    mx = 300
    left = mx
    cols = 16
    grid_w = cols * STEP
    parts.append(rect(left - 14, 40, grid_w + 28, H - 78, fill="#f7f8fa",
                      stroke=LINE, sw=1.5, rx=8))
    # плюс/мінус шини (верх)
    pry, nry = 58, H - 58
    for i in range(cols):
        x = left + i * STEP
        parts.append(hole(x, pry))
        parts.append(hole(x, nry))
    parts.append(line(left, pry - 11, left + grid_w - STEP, pry - 11, color=POS, sw=2))
    parts.append(line(left, nry + 11, left + grid_w - STEP, nry + 11, color=NEG, sw=2))
    parts.append(text(left - 20, pry - 7, "+", size=15, color=POS, bold=True))
    parts.append(text(left - 20, nry + 15, "–", size=15, color=NEG, bold=True))

    # центральні гнізда
    top0 = 108
    gy = 190
    bot0 = 214
    for i in range(cols):
        x = left + i * STEP
        parts.append(hole_col(x, top0, 5))
        parts.append(hole_col(x, bot0, 5))
    parts.append(rect(left - 6, gy - 3, grid_w + 12 - STEP, 16,
                      fill="#eceef1", stroke="#c9ccd1", sw=1, rx=3))

    # деталі на макетці
    # струмообмежувальний резистор: з + шини у стовпчик c3 (верх)
    c3 = left + 3 * STEP
    parts.append(line(c3, pry, c3, top0, color=POS, sw=2))
    # R лежить між двома стовпцями верхньої зони
    c5 = left + 5 * STEP
    parts.append(rect(c3 - 3, top0 + STEP, (c5 - c3) + 6, 8, fill="#e8c07d",
                      stroke="#a5793a", sw=1, rx=3))
    parts.append(text((c3 + c5) / 2, top0 - 6, "330", size=9, color=INK))
    # LED зі стовпця c5 (верх) у c5 (низ) через канавку
    parts.append(line(c5, top0 + STEP, c5, top0 + 4 * STEP, color=INK, sw=1.4))
    parts.append(circle(c5, bot0 + STEP, 4, fill="#c0392b", stroke="#7d2620", sw=1))
    parts.append(line(c5, top0 + 4 * STEP, c5, gy - 3, color=INK, sw=1.4))
    parts.append(line(c5, gy + 13, c5, bot0 + STEP, color=INK, sw=1.4))
    parts.append(text(c5 + 34, bot0 + STEP + 3, "LED", size=9, color=INK, anchor="middle"))
    # від LED (низ, c5) на – шину
    parts.append(line(c5, bot0 + 4 * STEP, c5, nry, color=NEG, sw=1.6))

    # підпис-натяк
    parts.append(text(left + grid_w / 2 - STEP / 2, H - 20,
                      "кожен вузол схеми → свій стовпчик", size=11,
                      color=MUTED, italic=True))

    render(out("schematic-to-board.svg"), W, H, *parts,
           title="Від схеми до макетки")


# ── 3. debug.svg — три класичні провали монтажу ──────────────────────────────
def fig_debug():
    W, H = 720, 260
    parts = []
    panels = [
        ("Розірвана шина",
         "живлення дійшло лише\nдо половини плати"),
        ("Через канавку",
         "дві ніжки в одному стовпці,\nале по різні боки — не з'єднані"),
        ("Плавучий контакт",
         "крива чи тонка ніжка\nтримається нещільно"),
    ]
    pw = 232
    gap = 8
    x0 = 8
    for idx, (title, desc) in enumerate(panels):
        px = x0 + idx * (pw + gap)
        parts.append(rect(px, 8, pw, H - 16, fill="#fbfcfd", stroke=LINE, sw=1.3, rx=8))
        parts.append(text(px + pw / 2, 30, title, size=13, color=POS, bold=True))

        cx = px + pw / 2
        if idx == 0:
            # шина з розривом посередині
            y = 70
            parts.append(line(px + 20, y, px + pw / 2 - 10, y, color=POS, sw=3))
            parts.append(line(px + pw / 2 + 10, y, px + pw - 20, y, color=POS, sw=3))
            for i in range(9):
                hx = px + 24 + i * ((pw - 48) / 8.0)
                parts.append(hole(hx, y + 16))
            # позначка розриву
            parts.append(text(cx, y - 8, "розрив", size=10, color=POS))
            parts.append(line(cx - 6, y - 5, cx + 6, y + 5, color=POS, sw=2))
            parts.append(line(cx + 6, y - 5, cx - 6, y + 5, color=POS, sw=2))
            # знеструмлена половина
            parts.append(text(px + pw * 0.72, y + 40, "тут 0 В", size=10, color=MUTED))
        elif idx == 1:
            # два стовпці, канавка, ніжки по різні боки
            y0 = 56
            for r in range(4):
                parts.append(hole(cx, y0 + r * STEP))
            gy = y0 + 4 * STEP
            parts.append(rect(cx - 26, gy, 52, 12, fill="#eceef1",
                              stroke="#c9ccd1", sw=1, rx=2))
            for r in range(4):
                parts.append(hole(cx, gy + 14 + r * STEP))
            # ніжка згори
            parts.append(circle(cx, y0 + STEP, 4, fill=INK, stroke=INK, sw=1))
            # ніжка знизу
            parts.append(circle(cx, gy + 14 + STEP, 4, fill=INK, stroke=INK, sw=1))
            parts.append(text(cx + 40, gy + 7, "✕", size=15, color=POS, bold=True, anchor="middle"))
        else:
            # гніздо з косою ніжкою
            y = 96
            parts.append(hole(cx, y, fill="#dfe2e6"))
            parts.append(line(cx - 14, y - 30, cx + 6, y, color=INK, sw=2.4))
            parts.append(text(cx + 44, y - 6, "то є,", size=10, color=MUTED, anchor="middle"))
            parts.append(text(cx + 44, y + 8, "то нема", size=10, color=MUTED, anchor="middle"))

        parts.append(mtext(px + pw / 2, H - 44, desc.split("\n"),
                           size=11, color=MUTED, lh=1.25))

    render(out("debug.svg"), W, H, *parts,
           title="Три класичні провали монтажу на макетці")


# ── 4. bread-timeline.svg — три покоління «хлібної дошки» ────────────────────
def fig_timeline():
    """Три панелі: дерев'яна дошка з цвяхами → пружинні смужки → сітка 0.1″."""
    W, H = 720, 300
    parts = []
    pw = 224
    gap = 12
    x0 = 12

    def panel_frame(px, top_title, year):
        parts.append(rect(px, 40, pw, H - 78, fill="#fbfcfd", stroke=LINE, sw=1.4, rx=10))
        parts.append(text(px + pw / 2, 62, top_title, size=13, color=INK, bold=True))
        parts.append(text(px + pw / 2, 80, year, size=11, color=MUTED, italic=True))

    # ── панель 1: дерев'яна дошка, цвяхи, накручені дроти ──
    p1 = x0
    panel_frame(p1, "дерев'яна дошка", "рання радіоаматорика")
    bx, by, bw, bh = p1 + 34, 108, pw - 68, 118
    # текстура дерева
    parts.append(rect(bx, by, bw, bh, fill="#e5c9a0", stroke="#a5793a", sw=1.6, rx=4))
    for i in range(1, 5):
        yy = by + i * bh / 5.0
        parts.append(line(bx + 4, yy, bx + bw - 4, yy, color="#c8a672", sw=0.8))
    # цвяхи (голівки) + накручені між ними дроти
    nails = [(bx + 24, by + 26), (bx + bw - 24, by + 30),
             (bx + 30, by + bh - 26), (bx + bw - 28, by + bh - 30),
             (bx + bw / 2, by + bh / 2)]
    parts.append(line(nails[0][0], nails[0][1], nails[4][0], nails[4][1], color="#8a6a3a", sw=1.6))
    parts.append(line(nails[4][0], nails[4][1], nails[1][0], nails[1][1], color="#8a6a3a", sw=1.6))
    parts.append(line(nails[2][0], nails[2][1], nails[4][0], nails[4][1], color="#8a6a3a", sw=1.6))
    parts.append(line(nails[4][0], nails[4][1], nails[3][0], nails[3][1], color="#8a6a3a", sw=1.6))
    for nx, ny in nails:
        parts.append(circle(nx, ny, 4, fill="#6b6f76", stroke="#3c3f45", sw=1))
    parts.append(text(p1 + pw / 2, H - 20, "цвяхи + накручений дріт",
                      size=10, color=MUTED, italic=True))

    # ── панель 2: пружинні металеві смужки (Thompson) ──
    p2 = x0 + (pw + gap)
    panel_frame(p2, "пружинні смужки", "Thompson · 1960→1963")
    cx = p2 + pw / 2
    # три «затискачі»: пара пружних губок, між ними ніжка
    for k, cyc in enumerate((124, 168, 212)):
        gx = p2 + 44 + k * 46
        # дві губки
        parts.append('<path d="M%.0f %.0f q -10 12 0 24" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (gx - 6, cyc - 12, POS))
        parts.append('<path d="M%.0f %.0f q 10 12 0 24" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (gx + 6, cyc - 12, POS))
        # ніжка деталі, затиснута
        parts.append(line(gx, cyc - 24, gx, cyc + 20, color=INK, sw=2))
        parts.append(circle(gx, cyc - 24, 3, fill=INK, stroke=INK, sw=1))
    parts.append(text(cx, H - 20, "метал пружинить — тримає ніжку",
                      size=10, color=MUTED, italic=True))

    # ── панель 3: сітка 0.1″ під DIP (Portugal) ──
    p3 = x0 + 2 * (pw + gap)
    panel_frame(p3, "сітка 0.1″ під DIP", "Portugal · 1971→1973")
    left = p3 + 40
    cols, rows = 8, 4
    top0 = 116
    for i in range(cols):
        hx = left + i * STEP
        parts.append(hole_col(hx, top0, rows))
    gy = top0 + rows * STEP - STEP + 6
    parts.append(rect(left - 6, gy, cols * STEP - STEP + 12, 14,
                      fill="#eceef1", stroke="#c9ccd1", sw=1, rx=3))
    for i in range(cols):
        hx = left + i * STEP
        parts.append(hole_col(hx, gy + 20, rows))
    # мікросхема DIP верхи канавки
    chip_y = gy - 4
    parts.append(rect(left + STEP - 4, chip_y - 30, 4 * STEP + 8, 34,
                      fill="#2b2f36", stroke="#000", sw=1, rx=3))
    for i in range(3):
        px_ = left + STEP + i * 2 * STEP
        parts.append(line(px_, chip_y - 4, px_, chip_y + 24, color="#9aa0a8", sw=1.6))
        parts.append(line(px_ + STEP, chip_y - 4, px_ + STEP, chip_y + 24, color="#9aa0a8", sw=1.6))
    # мірка кроку
    y_dim = top0 - 16
    parts.append(line(left, y_dim, left + STEP, y_dim, color=FIELD, sw=1.4))
    parts.append(line(left, y_dim - 4, left, y_dim + 4, color=FIELD, sw=1.4))
    parts.append(line(left + STEP, y_dim - 4, left + STEP, y_dim + 4, color=FIELD, sw=1.4))
    parts.append(text(left + STEP / 2, y_dim - 6, "0.1″", size=10, color=FIELD, bold=True))
    parts.append(text(p3 + pw / 2, H - 20, "крок ніжки чипа = крок гнізда",
                      size=10, color=MUTED, italic=True))

    # стрілки поступу між панелями
    ay = 38
    parts.append(arrow(p2 - gap - 2, ay, p2 + 2, ay, color=FIELD, sw=2.2))
    parts.append(arrow(p3 - gap - 2, ay, p3 + 2, ay, color=FIELD, sw=2.2))

    render(out("bread-timeline.svg"), W, H, *parts,
           title="Три покоління «хлібної дошки»")


def main():
    fig_anatomy()
    fig_s2b()
    fig_debug()
    fig_timeline()
    print("Згенеровано фігури у", IMG)


if __name__ == "__main__":
    main()
