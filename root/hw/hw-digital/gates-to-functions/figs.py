# -*- coding: utf-8 -*-
"""Фігури теми «Складні функції з вентилів».
svgkit імпортуємо зі scripts/ (не копіюємо). Запуск: python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER = "#d98a00"   # перенос / акцент


# ── ladder: драбина абстракції ────────────────────────────────────────────────
def fig_ladder():
    W, H = 720, 360
    p = []
    rungs = [
        ("Транзистор", "ключ: відкрито / закрито", "#eef4ff", "#c9d6f0"),
        ("Вентиль", "кілька транзисторів (CMOS)", "#e9f6ee", "#bfe3cd"),
        ("Блок", "десятки вентилів: суматор, MUX", "#fff3e0", "#f0d8a8"),
        ("Функціональний вузол", "АЛП, регістр: блоки + пам'ять", "#f3eafe", "#ddc8f2"),
        ("Процесор", "вузли + керування", "#fdecea", "#f2c4bd"),
    ]
    n = len(rungs)
    bw, bh = 360, 44
    gap = 18
    x = 60
    y0 = 56
    cx = x + bw / 2
    for i, (title, sub, fill, stroke) in enumerate(rungs):
        y = y0 + (n - 1 - i) * (bh + gap)     # знизу вгору
        p.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(x + 14, y + bh / 2 - 2, title, size=14, color=INK,
                      anchor="start", bold=True))
        p.append(text(x + 14, y + bh / 2 + 15, sub, size=11, color=MUTED, anchor="start"))
        if i < n - 1:
            yt = y                              # верх поточної смуги
            yb = y - gap                        # низ смуги вище
            p.append(arrow(cx, y - 2, cx, y - gap + 2, color=INK, sw=1.8))

    # підпис праворуч: «ховаємо деталі нижчого»
    bx = x + bw + 46
    p.append(line(bx, y0 + bh / 2, bx, y0 + (n - 1) * (bh + gap) + bh / 2,
                  color=MUTED, sw=1.4, dash="4 4"))
    p.append(arrow(bx, y0 + (n - 1) * (bh + gap) + bh / 2, bx, y0 + bh / 2,
                   color=MUTED, sw=1.4))
    p.append(mtext(bx + 14, H / 2 - 18, ["вище — кожен", "рівень ховає", "деталі нижчого"],
                   size=12, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "ladder.svg"), W, H, *p)


# ── completeness: сила (зведення до вентилів) vs стіна (2ⁿ вибухає) ────────────
def fig_completeness():
    W, H = 720, 340
    p = []
    p.append(line(W / 2, 50, W / 2, H - 30, color="#d0d4da", sw=1.4, dash="5 5"))

    # ── ліва половина: таблиця → СД → вентилі ──
    p.append(text(W / 4, 38, "Сила: будь-яка таблиця → вентилі", size=14,
                  color=FIELD, bold=True))
    # маленька таблиця істинності
    tx, ty = 50, 70
    cellw, cellh = 26, 22
    p.append(rect(tx, ty, cellw * 3, cellh, fill="#eef2f7", stroke=LINE, sw=1.2, rx=3))
    for j, h in enumerate(["A", "B", "Y"]):
        p.append(text(tx + cellw * j + cellw / 2, ty + 15, h, size=12, color=INK, bold=True))
    rows = [("0", "0", "0"), ("0", "1", "1"), ("1", "0", "1"), ("1", "1", "0")]
    for r, row in enumerate(rows):
        yy = ty + cellh * (r + 1)
        p.append(rect(tx, yy, cellw * 3, cellh, fill=BG, stroke="#dfe3e8", sw=1.0, rx=0))
        for j, v in enumerate(row):
            p.append(text(tx + cellw * j + cellw / 2, yy + 15, v, size=12, color=INK))
    p.append(arrow(tx + cellw * 3 + 8, ty + cellh * 2.5, tx + cellw * 3 + 44,
                   ty + cellh * 2.5, color=INK, sw=1.6))
    p.append(text(tx + cellw * 3 + 26, ty + cellh * 2.5 - 8, "СД", size=11,
                  color=MUTED))
    # символ вентиля (трикутник-блок)
    gx = tx + cellw * 3 + 56
    gy = ty + cellh * 2.5
    p.append(rect(gx, gy - 26, 92, 52, fill="#e9f6ee", stroke=FIELD, sw=1.8))
    p.append(text(gx + 46, gy + 5, "вентилі", size=13, color=FIELD, bold=True))
    p.append(text(W / 4, H - 34, "досить навіть самих NAND", size=11, color=MUTED))

    # ── права половина: 2ⁿ вибухає ──
    rx0 = W / 2 + 40
    p.append(text(3 * W / 4, 38, "Стіна: пряма таблиця = 2ⁿ рядків", size=14,
                  color=POS, bold=True))
    bars = [("8", 256, 0.06), ("16", 65536, 0.28), ("32", 4_000_000_000, 1.0)]
    base_y = H - 60
    max_h = 150
    bw = 60
    sx = rx0 + 30
    for i, (n_in, val, frac) in enumerate(bars):
        h = max(10, max_h * frac)
        x = sx + i * (bw + 34)
        p.append(rect(x, base_y - h, bw, h, fill="#fdecea", stroke=POS, sw=1.6))
        p.append(text(x + bw / 2, base_y + 16, n_in + " вх.", size=11, color=INK))
        lbl = {256: "256", 65536: "65 тис.", 4_000_000_000: "~4 млрд"}[val]
        p.append(text(x + bw / 2, base_y - h - 8, lbl, size=11, color=POS, bold=True))
    p.append(line(sx - 12, base_y, sx + 3 * (bw + 34) - 24, base_y, color=INK, sw=1.4))
    render(os.path.join(OUT, "completeness.svg"), W, H, *p)


# ── no-memory: комбінаційна схема не пам'ятає ─────────────────────────────────
def fig_no_memory():
    W, H = 700, 300
    p = []
    # блок «комбінаційна логіка»
    bx, by, bw, bh = 250, 110, 200, 90
    p.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.8))
    p.append(mtext(bx + bw / 2, by + bh / 2 - 4, ["комбінаційна", "логіка"],
                   size=15, color=INK, bold=True))
    p.append(text(bx + bw / 2, by + bh - 12, "(без пам'яті)", size=11, color=MUTED))

    # входи «зараз»
    p.append(arrow(bx - 70, by + 28, bx, by + 28, color=INK, sw=1.7))
    p.append(arrow(bx - 70, by + 62, bx, by + 62, color=INK, sw=1.7))
    p.append(text(bx - 76, by + 12, "входи зараз", size=12, color=INK, anchor="end"))
    # вихід
    p.append(arrow(bx + bw, by + bh / 2, bx + bw + 70, by + bh / 2, color=INK, sw=1.7))
    p.append(text(bx + bw + 76, by + bh / 2 + 4, "вихід", size=12, color=INK, anchor="start"))

    # питання, на яке вона не відповість
    p.append(text(W / 2, 56, "«Скільки разів натиснули кнопку?»", size=15,
                  color=INK, bold=True))
    qx = W / 2
    p.append(text(qx, by + bh + 52, "— не знає: не пам'ятає попередніх натискань", size=12,
                  color=POS))
    p.append(text(qx, by + bh + 74, "потрібні ПАМ'ЯТЬ (зберегти стан) і ТАКТ (ритм кроків)",
                  size=12, color=FIELD, bold=True))
    render(os.path.join(OUT, "no-memory.svg"), W, H, *p)


# ── alu: блоки рахують паралельно, MUX обирає за кодом операції ────────────────
def fig_alu():
    W, H = 700, 360
    p = []
    # рамка АЛП
    ax, ay, aw, ah = 60, 60, 580, 250
    p.append(rect(ax, ay, aw, ah, fill="#fbfcfe", stroke=LINE, sw=1.8))
    p.append(text(ax + 16, ay + 24, "АЛП", size=15, color=INK, anchor="start", bold=True))

    # входи A, B
    p.append(text(ax - 8, ay + 80, "A", size=14, color=INK, anchor="end", bold=True))
    p.append(text(ax - 8, ay + 150, "B", size=14, color=INK, anchor="end", bold=True))

    # три блоки, що рахують паралельно
    blocks = [("суматор", "A + B", "#fff3e0", "#f0d8a8", 90),
              ("логіка", "A·B, A+B", "#e9f6ee", "#bfe3cd", 160),
              ("компаратор", "A ? B", "#eef4ff", "#c9d6f0", 230)]
    bw, bh = 150, 46
    bx = ax + 70
    mux_x = ax + 400
    mux_in_y = []
    for name, expr, fill, stroke, by in blocks:
        p.append(rect(bx, ay + by - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(bx + bw / 2, ay + by - 4, name, size=13, color=INK, bold=True))
        p.append(text(bx + bw / 2, ay + by + 14, expr, size=11, color=MUTED))
        # від A,B у кожен блок (натяк)
        p.append(line(ax, ay + 80, bx, ay + by - 10, color="#c7ccd3", sw=1.0))
        p.append(line(ax, ay + 150, bx, ay + by + 10, color="#c7ccd3", sw=1.0))
        # вихід блоку → MUX
        p.append(arrow(bx + bw, ay + by, mux_x, ay + by, color=INK, sw=1.5))
        mux_in_y.append(ay + by)

    # мультиплексор — трапеція
    my_top, my_bot = ay + 70, ay + 250
    mw_top, mw_bot = 54, 20
    mxc = mux_x + 30
    pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
        mux_x, my_top, mux_x + mw_top, my_top + mw_top,
        mux_x + mw_top, my_bot - mw_top, mux_x, my_bot)
    p.append('<polygon points="%s" fill="#f3eafe" stroke="#caa8ee" stroke-width="1.8"/>' % pts)
    p.append(mtext(mux_x + 24, (my_top + my_bot) / 2 - 6, ["MUX"], size=13,
                   color=INK, bold=True))

    # код операції знизу в MUX
    p.append(arrow(mux_x + 24, my_bot + 40, mux_x + 24, my_bot - 4, color=POS, sw=1.7))
    p.append(text(mux_x + 24, my_bot + 56, "код операції", size=12, color=POS, bold=True))

    # вихід MUX → результат
    outx = mux_x + mw_top
    p.append(arrow(outx, (my_top + my_bot) / 2, ax + aw + 6, (my_top + my_bot) / 2,
                   color=INK, sw=1.8))
    p.append(text(ax + aw + 12, (my_top + my_bot) / 2 + 4, "результат", size=12,
                  color=INK, anchor="start", bold=True))
    render(os.path.join(OUT, "alu.svg"), W, H, *p)


# ── space-vs-time: окрема швидка схема vs маленький АЛП по кроках ──────────────
def fig_space_vs_time():
    W, H = 720, 340
    p = []
    p.append(line(W / 2, 50, W / 2, H - 30, color="#d0d4da", sw=1.4, dash="5 5"))

    # ── ліворуч: просторово ──
    p.append(text(W / 4, 38, "Простором: окрема схема", size=14, color=FIELD, bold=True))
    # розкидані вентилі, з'єднані в один великий блок
    nodes = [(80, 90), (150, 80), (120, 140), (200, 120), (170, 180),
             (250, 100), (240, 170), (300, 150)]
    for (nx, ny) in nodes:
        p.append(rect(nx, ny, 36, 24, fill="#e9f6ee", stroke=FIELD, sw=1.4, rx=4))
    links = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 7)]
    for a, b in links:
        ax_, ay_ = nodes[a]
        bx_, by_ = nodes[b]
        p.append(line(ax_ + 36, ay_ + 12, bx_, by_ + 12, color="#bfe3cd", sw=1.3))
    p.append(arrow(nodes[7][0] + 36, nodes[7][1] + 12, nodes[7][0] + 80,
                   nodes[7][1] + 12, color=INK, sw=1.6))
    p.append(mtext(W / 4, H - 56, ["швидко (1 прохід),", "але жорстко: лише ця функція"],
                   size=11, color=MUTED))

    # ── праворуч: у часі ──
    p.append(text(3 * W / 4, 38, "У часі: маленький АЛП по кроках", size=14,
                  color=POS, bold=True))
    ax, ay = W / 2 + 90, 90
    p.append(rect(ax, ay, 90, 50, fill="#fff3e0", stroke="#f0d8a8", sw=1.6))
    p.append(text(ax + 45, ay + 30, "АЛП", size=14, color=INK, bold=True))
    # регістри
    p.append(rect(ax + 130, ay - 6, 70, 26, fill="#eef4ff", stroke="#c9d6f0", sw=1.4))
    p.append(text(ax + 165, ay + 12, "регістри", size=11, color=INK))
    # цикл такту
    p.append(arrow(ax + 90, ay + 14, ax + 130, ay + 7, color=INK, sw=1.4))
    p.append(arrow(ax + 130, ay + 30, ax + 90, ay + 38, color=INK, sw=1.4))
    p.append(text(ax + 110, ay + 60, "такт за тактом", size=11, color=POS))
    # стрічка кроків
    steps_y = ay + 110
    for i in range(4):
        sx = ax + i * 50
        p.append(rect(sx, steps_y, 40, 26, fill="#fdecea", stroke=POS, sw=1.3, rx=3))
        p.append(text(sx + 20, steps_y + 17, "крок", size=10, color=POS))
        if i < 3:
            p.append(arrow(sx + 40, steps_y + 13, sx + 50, steps_y + 13, color=POS, sw=1.3))
    p.append(mtext(3 * W / 4, H - 56, ["гнучко й компактно,", "але повільніше"],
                   size=11, color=MUTED))
    render(os.path.join(OUT, "space-vs-time.svg"), W, H, *p)


if __name__ == "__main__":
    fig_ladder()
    fig_completeness()
    fig_no_memory()
    fig_alu()
    fig_space_vs_time()
    print("OK: figures written to", OUT)
