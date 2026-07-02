# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Цикл зведення таймінгу (замкнена петля) ──────────────────────────────
def fig_loop():
    W, H = 720, 380
    cx, cy = 360, 210
    rx, ry = 250, 120
    frags = []

    # чотири вузли по еліпсу
    nodes = [
        ("Синтез\n(HDL → вентилі)", cx,        cy - ry, FILL),
        ("Розміщення\nй трасування", cx + rx,   cy,      FILL),
        ("Аналіз таймінгу\n(WNS, TNS)", cx,      cy + ry, "#eef6ee"),
        ("Виправлення\nкритичних шляхів", cx - rx, cy,    "#fdf0ee"),
    ]
    centers = []
    for label, x, y, fill in nodes:
        b, w, h = textbox(x, y, label, size=14, pad=12, fill=fill, bold=True)
        frags.append(b)
        centers.append((x, y, w, h))

    # стрілки по колу (за годинниковою)
    def edge(a, b):
        xa, ya, wa, ha = centers[a]
        xb, yb, wb, hb = centers[b]
        dx, dy = xb - xa, yb - ya
        import math
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # відступ від країв рамок (грубо — по більшій півосі)
        sa = max(wa, ha) / 2 + 6
        sb = max(wb, hb) / 2 + 10
        return arrow(xa + ux * sa, ya + uy * sa, xb - ux * sb, yb - uy * sb, color=LINE, sw=2.0)

    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        frags.append(edge(a, b))

    # мітка «зійшлося → вихід»
    b, w, h = textbox(cx, cy, "WNS ≥ 0\nі THS = 0\n→ зійшлося", size=13, pad=10,
                      fill="#ffffff", stroke=FIELD, sw=2.0, color=FIELD, bold=True)
    frags.append(b)

    # підпис петлі збоку
    frags.append(text(cx + rx + 4, cy + ry - 6, "повторювати,", size=12, color=MUTED, anchor="middle"))
    frags.append(text(cx + rx + 4, cy + ry + 10, "доки не зійдеться", size=12, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'loop.svg'), W, H, *frags,
           title="Зведення таймінгу — замкнений цикл")


# ── 2. Розподіл slack по всіх кінцевих точках; WNS і TNS ────────────────────
def fig_wns_tns():
    W, H = 720, 400
    frags = []
    # горизонтальна вісь slack, вертикаль — «скільки шляхів»
    x0, y0 = 90, 300     # початок осей (нуль slack)
    axw = 560
    zero_x = 360         # де slack = 0
    # смуги: висоти-«кількість шляхів» для кошиків slack від −3 до +6 нс
    bins = [(-3, 2), (-2, 5), (-1, 11), (0, 20), (1, 34), (2, 40),
            (3, 30), (4, 18), (5, 8), (6, 3)]
    bw = 46
    scale = 5.0  # px на один шлях
    # осі
    frags.append(line(x0, y0, x0 + axw, y0, color=INK, sw=2))          # вісь slack
    frags.append(line(zero_x, 60, zero_x, y0 + 6, color=NEG, sw=2, dash="5,4"))  # slack = 0
    frags.append(text(zero_x, 52, "slack = 0", size=13, color=NEG, bold=True))

    # стовпчики
    step = axw / len(bins)
    for i, (s, cnt) in enumerate(bins):
        bx = x0 + 30 + i * step
        h = cnt * scale
        col = POS if s < 0 else FIELD
        fillc = "#fdecea" if s < 0 else "#eaf6ee"
        frags.append(rect(bx - bw / 2, y0 - h, bw, h, fill=fillc, stroke=col, sw=1.6, rx=3))
        frags.append(text(bx, y0 + 20, "%+d" % s, size=12, color=MUTED))

    frags.append(text(x0 + axw / 2, y0 + 42, "запас часу шляху, slack (нс)", size=13, color=INK))
    frags.append(text(x0 - 8, y0 - 90, "к-сть", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, y0 - 74, "шляхів", size=12, color=MUTED, anchor="end"))

    # позначити WNS (найлівіший = найгірший) і TNS (сума лівих)
    worst_x = x0 + 30 + 0 * step
    frags.append(arrow(worst_x, 110, worst_x, y0 - 2 * scale - 4, color=POS, sw=2))
    b, w, h = textbox(worst_x + 6, 95, "WNS = −3 нс\n(найгірший)", size=12, pad=8,
                      fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b)

    b, w, h = textbox(x0 + 175, 150, "TNS = сума всіх\nвід'ємних slack\n(тут = −24 нс)",
                      size=12, pad=9, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'wns-tns.svg'), W, H, *frags,
           title="WNS і TNS — два числа про всю схему")


# ── 3. Набір прийомів проти від'ємного slack ────────────────────────────────
def fig_fixes():
    W, H = 720, 430
    frags = []
    # верх: критичний шлях, що не влазить у період
    tx, ty = 60, 70
    period_w = 560
    frags.append(rect(tx, ty, period_w, 34, fill="#ffffff", stroke=NEG, sw=1.8))
    frags.append(text(tx + period_w + 6, ty + 22, "період", size=12, color=NEG, anchor="start"))
    # шлях довший за період (вилазить)
    path_w = 650
    frags.append(rect(tx, ty + 4, path_w, 26, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    frags.append(text(tx + 200, ty + 21, "критичний шлях задовгий → slack < 0", size=13, color=POS, bold=True))

    # чотири прийоми — картки
    box = [
        ("Конвеєр\n(розрізати регістром)", "довгий шлях → дві короткі\nділянки; +1 такт латентності", FIELD, "#eaf6ee"),
        ("Більший драйвер\n(gate sizing)", "сильніший вентиль\nшвидше жене ємність", INK, FILL),
        ("Буфери на дроті", "довгий дріт ділять —\nRC-затримка падає", INK, FILL),
        ("Менше рівнів логіки\n(перебудова)", "переписати вузол так,\nщоб шлях був коротший", INK, FILL),
    ]
    cw, ch = 315, 96
    gx, gy = 60, 170
    xs = [gx, gx + cw + 30]
    ys = [gy, gy + ch + 26]
    idx = 0
    for r in range(2):
        for c in range(2):
            title, sub, sc, fc = box[idx]
            x, y = xs[c], ys[r]
            frags.append(rect(x, y, cw, ch, fill=fc, stroke=sc, sw=1.8, rx=8))
            frags.append(mtext(x + cw / 2, y + 26, title, size=14, color=sc, bold=True))
            frags.append(mtext(x + cw / 2, y + 62, sub, size=12, color=MUTED))
            idx += 1

    render(os.path.join(IMG, 'fixes.svg'), W, H, *frags,
           title="Чим виправляють від'ємний slack")


# ── 4. Перехрестя: затримка дроту наздоганяє й переганяє затримку вентиля ────
def fig_crossover():
    W, H = 720, 430
    frags = []
    # осі
    ox, oy = 90, 330          # початок осей (низ-ліво)
    axw, axh = 560, 250
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))        # X: техпроцес
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))        # Y: затримка

    # підписи осей
    frags.append(text(ox + axw / 2, oy + 46, "дедалі тонший техпроцес  →", size=13, color=INK))
    frags.append(text(ox - 8, oy - axh - 8, "затримка", size=12, color=MUTED, anchor="middle"))

    # вузли техпроцесу по осі X (грубо, зліва «товстий» → справа «тонкий»)
    nodes = ["0.7 мкм", "0.35", "0.25", "0.18", "0.13", "90 нм"]
    step = axw / (len(nodes) - 1)
    for i, nm in enumerate(nodes):
        x = ox + i * step
        frags.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        frags.append(text(x, oy + 22, nm, size=11, color=MUTED))

    # крива затримки вентиля (спадає)  — точки (частка висоти)
    gate = [0.72, 0.55, 0.44, 0.34, 0.26, 0.18]
    # крива затримки дроту (росте)
    wire = [0.20, 0.30, 0.42, 0.58, 0.74, 0.88]

    def poly(vals, color):
        pts = []
        for i, v in enumerate(vals):
            x = ox + i * step
            y = oy - v * axh
            pts.append((x, y))
        seg = []
        for j in range(len(pts) - 1):
            x1, y1 = pts[j]; x2, y2 = pts[j + 1]
            seg.append(line(x1, y1, x2, y2, color=color, sw=2.6))
        for (x, y) in pts:
            seg.append(circle(x, y, 3.5, fill=color, stroke=color, sw=1))
        return seg

    frags += poly(gate, NEG)
    frags += poly(wire, POS)

    # точка перетину — приблизно між 0.25 і 0.18
    xcross = ox + 3 * step - step * 0.35
    ycross = oy - 0.36 * axh
    frags.append(circle(xcross, ycross, 6, fill="#ffffff", stroke=FIELD, sw=2.4))
    b, w, h = textbox(xcross + 4, ycross - 54, "тут дроти\nпереганяють вентилі",
                      size=12, pad=8, fill="#eaf6ee", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b)

    # легенда кривих
    frags.append(line(ox + 30, oy - axh + 8, ox + 60, oy - axh + 8, color=NEG, sw=2.6))
    frags.append(text(ox + 66, oy - axh + 12, "затримка вентиля (спадає)", size=12, color=NEG, anchor="start"))
    frags.append(line(ox + 30, oy - axh + 30, ox + 60, oy - axh + 30, color=POS, sw=2.6))
    frags.append(text(ox + 66, oy - axh + 34, "затримка дроту (росте)", size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, 'crossover.svg'), W, H, *frags,
           title="Чому народився фізичний синтез: дроти обігнали вентилі")


# ── 5. Старий цикл (розірваний) проти фізичного синтезу (злитий) ────────────
def fig_merge():
    W, H = 760, 430
    frags = []

    # ── ліворуч: старий розірваний потік ──
    lx = 40
    frags.append(text(lx + 150, 56, "Старий потік: синтез і розкладка нарізно",
                      size=14, color=POS, bold=True))
    steps = ["Синтез\n(оцінка дротів — здогад)", "Окрема розкладка\n(дроти стають реальні)",
             "Таймінг не сходиться", "Правити HDL,\nпересинтезувати"]
    cw, chh = 250, 52
    sx = lx + 25
    ys = [80, 150, 220, 290]
    cen = []
    for s, y in zip(steps, ys):
        fill = "#fdecea" if ("не сходиться" in s or "Правити" in s) else FILL
        sc = POS if fill != FILL else INK
        frags.append(rect(sx, y, cw, chh, fill=fill, stroke=sc, sw=1.7, rx=6))
        frags.append(mtext(sx + cw / 2, y + 22, s, size=12, color=sc, bold=("не сходиться" in s)))
        cen.append((sx + cw / 2, y, chh))
    # стрілки вниз
    for a in range(3):
        x = cen[a][0]; y1 = cen[a][1] + chh; y2 = cen[a + 1][1]
        frags.append(arrow(x, y1, x, y2 - 2, color=LINE, sw=1.8))
    # довга стрілка-повернення знизу вгору (цикл)
    rx = sx + cw + 14
    frags.append(line(cen[3][0], ys[3] + chh, rx, ys[3] + chh, color=POS, sw=1.8))
    frags.append(line(rx, ys[3] + chh, rx, ys[0] + 26, color=POS, sw=1.8, dash="5,4"))
    frags.append(arrow(rx, ys[0] + 26, cen[0][0] + cw / 2 + 2, ys[0] + 26, color=POS, sw=1.8))
    frags.append(text(rx + 10, (ys[0] + ys[3]) / 2, "довгий", size=11, color=POS, anchor="start"))
    frags.append(text(rx + 10, (ys[0] + ys[3]) / 2 + 16, "цикл, що", size=11, color=POS, anchor="start"))
    frags.append(text(rx + 10, (ys[0] + ys[3]) / 2 + 32, "не збігається", size=11, color=POS, anchor="start"))

    # роздільна межа
    frags.append(line(W / 2 + 30, 70, W / 2 + 30, 360, color=MUTED, sw=1, dash="3,4"))

    # ── праворуч: фізичний синтез (одне ядро) ──
    rxc = W / 2 + 70
    frags.append(text(rxc + 130, 56, "Фізичний синтез: усе в одному циклі",
                      size=14, color=FIELD, bold=True))
    # велика рамка-ядро
    bx, by, bw, bh = rxc + 10, 90, 300, 210
    frags.append(rect(bx, by, bw, bh, fill="#eaf6ee", stroke=FIELD, sw=2.2, rx=12))
    inner = ["Синтез логіки", "Розміщення", "Добір розміру вентилів", "Уставляння буферів", "Перебудова логіки"]
    for i, s in enumerate(inner):
        iy = by + 30 + i * 34
        frags.append(rect(bx + 26, iy, bw - 52, 26, fill="#ffffff", stroke=FIELD, sw=1.4, rx=5))
        frags.append(text(bx + bw / 2, iy + 17, s, size=12, color=INK))
    frags.append(text(bx + bw / 2, by + bh + 26,
                      "дроти відомі одразу → таймінг зводиться на місці", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'merge.svg'), W, H, *frags,
           title="Що злив докупи фізичний синтез")


if __name__ == "__main__":
    fig_loop()
    fig_wns_tns()
    fig_fixes()
    fig_crossover()
    fig_merge()
    print("figures written to", IMG)
