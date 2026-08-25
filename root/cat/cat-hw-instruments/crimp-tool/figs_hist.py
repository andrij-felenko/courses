# -*- coding: utf-8 -*-
"""Фігури для вставки «як народилося з'єднання обтиском» (hist).
Окремий від figs.py файл теми, щоб не переганяти фігури основної статті.
Чистий Python, svgkit зі scripts/. Вивід — ./img."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

STEEL = "#5a6270"
STEELF = "#c9ced6"
BRASS = "#b8860b"
BRASSF = "#f3e2b3"
COPPER = "#c0522a"
SOLDER = "#8a8f98"     # сірий припій
GOOD = "#27ae60"
BAD = "#c0392b"


# ── Фігура 1: стрічка часу народження обтиску (AMP / Вітакер) ────────────────
def fig_timeline():
    W, H = 900, 470
    frags = []

    frags.append(text(W / 2, 30, "Народження безпайкового обтиску",
                      size=17, bold=True))

    # горизонтальна вісь
    axis_y = 250
    x0, x1 = 90, 820
    frags.append(line(x0, axis_y, x1, axis_y, color=STEEL, sw=3))
    frags.append(arrow(x1 - 4, axis_y, x1 + 30, axis_y, color=STEEL, sw=3))

    marks = [
        (0.02, "1941", ["Вітакер засновує", "Aircraft-Marine", "Products (AMP)",
                        "у Нью-Джерсі"], "up"),
        (0.30, "1943", ["штаб-квартира", "переїздить у", "Гаррісбург, Пенс."], "down"),
        (0.60, "WWII", ["контракти:", "Boeing, Ford,", "Electric Boat"], "up"),
        (0.92, "1956", ["перейменування", "на AMP", "Incorporated"], "down"),
    ]
    for frac, yr, lines, side in marks:
        cx = x0 + (x1 - x0) * frac
        frags.append(circle(cx, axis_y, 8, fill=BRASSF, stroke=BRASS, sw=2.5))
        # короткий стеблинка-стуб від вузла до картки (обривається ДО тексту)
        if side == "up":
            frags.append(line(cx, axis_y - 8, cx, axis_y - 30,
                              color=MUTED, sw=1, dash="3 3"))
        else:
            frags.append(line(cx, axis_y + 8, cx, axis_y + 30,
                              color=MUTED, sw=1, dash="3 3"))
        # рік — збоку від вузла, щоб стеблинка його не пронизувала
        yy = axis_y + 5
        frags.append(text(cx + 26, yy, yr, size=15, bold=True, color=STEEL,
                          anchor="start"))
        # картка-опис — далі від осі, з запасом ширини
        by = axis_y - 108 if side == "up" else axis_y + 108
        b, bw, bh = textbox(cx, by, lines, size=11.5, pad=8, min_w=150)
        frags.append(b)

    render(os.path.join(IMG, "timeline.svg"), W, H, *frags,
           title=None)


# ── Фігура 2: чому тиск зварює, а припій тріскається ────────────────────────
def fig_coldweld():
    W, H = 940, 520
    frags = []

    midx = W / 2
    frags.append(line(midx, 70, midx, 470, color=MUTED, sw=1.5, dash="6 4"))

    # ── ЛІВА панель: паяний контакт під вібрацією ───────────────────────────
    frags.append(text(245, 60, "Пайка: жорсткий наплив тріскається",
                      size=14.5, bold=True, color=BAD))

    # дріт (пучок жил) заходить зліва в наплив припою
    wy = 200
    for dy in (-12, -4, 4, 12):
        frags.append(line(40, wy + dy, 190, wy + dy, color=COPPER, sw=3))
    # наплив припою — суцільна крапля, що застигла на жилах
    frags.append('<path d="M 175 165 Q 260 150 300 200 Q 260 250 175 235 Z" '
                 'fill="%s" stroke="%s" stroke-width="2"/>' % (SOLDER, STEEL))
    # клема праворуч
    frags.append(rect(295, 178, 70, 44, fill=BRASSF, stroke=BRASS, sw=2, rx=4))

    # ЧЕРВОНА зона напруги на межі «де припій кінчається»
    frags.append(circle(178, wy, 15, fill="none", stroke=BAD, sw=2.5))
    # тріщина
    frags.append('<path d="M 168 190 L 176 200 L 168 210" '
                 'fill="none" stroke="%s" stroke-width="2.5"/>' % BAD)

    # стрілки вібрації (дріт хитається вгору-вниз)
    frags.append(arrow(95, 150, 95, 175, color=MUTED, sw=1.5))
    frags.append(arrow(95, 250, 95, 225, color=MUTED, sw=1.5))
    frags.append(text(95, 135, "вібрація", size=11, color=MUTED))

    # підпис-пояснення (окремими рядками — коротко, поза лініями)
    b, bw, bh = textbox(210, 340, [
        "Припій жорсткий і крихкий. Гнучкий дріт",
        "хитається — а біля краю напливу, де м'яка",
        "мідь зустрічає тверду пайку, росте напруга.",
        "Метал там і тріскається (стрес-концентратор)."],
        size=11.5, pad=9, min_w=380)
    frags.append(b)
    frags.append(text(210, 430, "✗ ламається від вібрації", size=13.5,
                      color=BAD, bold=True))

    # ── ПРАВА панель: обтиск — холодне зварювання тиском ────────────────────
    frags.append(text(midx + 230, 60, "Обтиск: тиск зварює метал начисто",
                      size=14.5, bold=True, color=GOOD))

    # губки, що стискають (стрілки згори й знизу)
    bx = midx + 130
    frags.append(rect(bx, 130, 190, 26, fill=STEELF, stroke=STEEL, sw=2, rx=4))
    frags.append(rect(bx, 244, 190, 26, fill=STEELF, stroke=STEEL, sw=2, rx=4))
    frags.append(arrow(bx + 95, 118, bx + 95, 130, color=STEEL, sw=2.5))
    frags.append(arrow(bx + 95, 282, bx + 95, 270, color=STEEL, sw=2.5))

    # латунний барабан, обтиснутий на жилах
    frags.append(rect(bx + 20, 162, 150, 76, fill=BRASSF, stroke=BRASS, sw=2, rx=6))
    # жили, сплющені в «стільник» — шестикутнички впритул
    import math
    hex_cx, hex_cy, r = bx + 95, 200, 11
    centers = [(hex_cx - 20, hex_cy), (hex_cx, hex_cy), (hex_cx + 20, hex_cy),
               (hex_cx - 10, hex_cy - 17), (hex_cx + 10, hex_cy - 17),
               (hex_cx - 10, hex_cy + 17), (hex_cx + 10, hex_cy + 17)]
    for hx, hy in centers:
        pts = []
        for k in range(6):
            a = math.radians(60 * k - 30)
            pts.append("%.1f,%.1f" % (hx + r * math.cos(a), hy + r * math.sin(a)))
        frags.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.2"/>'
                     % (" ".join(pts), COPPER, BRASS))

    # зелена «зона зварювання» по стиках
    frags.append(circle(hex_cx, hex_cy, 34, fill="none", stroke=GOOD, sw=2.5, ))

    b, bw, bh = textbox(midx + 230, 340, [
        "Тиск чавить жили: круглі перетини сплющуються",
        "в стільник упритул. Оксидні плівки тріскають і",
        "сходять — чистий метал тисне на чистий метал і",
        "зварюється холодним, без нагріву й флюсу.",
        "Наплив м'яко тече в дріт — краю-тріщини нема."],
        size=11.5, pad=9, min_w=400)
    frags.append(b)
    frags.append(text(midx + 230, 448, "✓ тримає під вібрацією", size=13.5,
                      color=GOOD, bold=True))

    render(os.path.join(IMG, "coldweld.svg"), W, H, *frags,
           title="Чому холодний тиск надійніший за припій")


if __name__ == "__main__":
    fig_timeline()
    fig_coldweld()
    print("hist figures written to", IMG)
