# -*- coding: utf-8 -*-
"""Фігури до теми «Каскадний захист від перенапруги».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


# ── 1. Чому одного елемента мало: енергія × точність ──────────────────────────
def fig_tradeoff():
    W, H = 720, 430
    f = []
    # осі
    x0, y0 = 110, 360          # початок осей
    xr, yt = 660, 70           # кінці осей
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=2))     # вісь X: енергія
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=2))     # вісь Y: точність/швидкість
    f.append(text((x0 + xr) / 2, y0 + 38, "енергія, яку елемент стерпить  →", size=13, color=INK))
    # підпис осі Y вертикально
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'точність і швидкість затиску  →</text>' % (38, (y0 + yt) / 2, FONT, INK, 38, (y0 + yt) / 2))

    # три елементи як кружки в кутах
    def node(cx, cy, label, sub, color, fillc):
        out = circle(cx, cy, 30, fill=fillc, stroke=color, sw=2.4)
        out += text(cx, cy + 5, label, size=15, color=color, bold=True)
        out += text(cx, cy + 52, sub, size=11, color=MUTED)
        return out

    f.append(node(560, 320, "GDT", "кілоампери, але грубий і повільний", RED, "#fdecea"))
    f.append(node(360, 215, "MOV", "сотні ампер, середній", FIELD, "#eafaf0"))
    f.append(node(180, 110, "TVS", "наносекунди, точно — та мало енергії", BLU, "#eaf0fd"))

    # «жадана» зона — порожній кут (багато енергії І точно)
    f.append(rect(470, 95, 175, 70, fill="#fff7e6", stroke="#d9a441", sw=1.6, rx=8))
    f.append(fitbox(470, 95, 175, 70,
                    "жоден один елемент\nсюди не дістає",
                    size=11.5, fill="#fff7e6", stroke="#d9a441", color="#8a5a00"))
    f.append(arrow(545, 165, 470, 230, color="#d9a441", sw=1.6))
    f.append(arrow(560, 165, 560, 285, color="#d9a441", sw=1.6))

    return render(os.path.join(IMG, "tradeoff.svg"), W, H, *f,
                  title="Три захисники — три кути; верхній правий нікому не дається")


# ── 2. Серце каскаду: розв'язувальний імпеданс між щаблями ───────────────────
def fig_decoupling():
    W, H = 720, 470
    f = []

    # --- верх: БЕЗ розв'язки ---
    f.append(text(W / 2, 30, "Без розв'язки: швидкий MOV спрацьовує перший і гине", size=14, bold=True, color=RED))
    yb = 95
    # лінія
    f.append(line(70, yb, 650, yb, color=INK, sw=2.2))
    f.append(text(60, yb + 5, "вхід", size=11, color=MUTED, anchor="end"))
    # GDT (грубий) ліворуч, MOV праворуч — обидва поперек на землю, БЕЗ опору між ними
    f.append(line(200, yb, 200, yb + 40, color=INK, sw=2))
    f.append(rect(178, yb + 40, 44, 26, fill="#fdecea", stroke=RED, sw=2, rx=5))
    f.append(text(200, yb + 57, "GDT", size=11, color=RED, bold=True))
    f.append(line(200, yb + 66, 200, yb + 86, color=INK, sw=2))
    f.append(line(420, yb, 420, yb + 40, color=INK, sw=2))
    f.append(rect(398, yb + 40, 44, 26, fill="#eafaf0", stroke=FIELD, sw=2, rx=5))
    f.append(text(420, yb + 57, "MOV", size=11, color=FIELD, bold=True))
    f.append(line(420, yb + 66, 420, yb + 86, color=INK, sw=2))
    # земля
    f.append(line(120, yb + 86, 520, yb + 86, color=INK, sw=2.2))
    for i, gx in enumerate((150, 200, 250, 370, 420, 470)):
        f.append(line(gx, yb + 86, gx - 8, yb + 96, color=INK, sw=2))
    # підпис біди
    f.append(fitbox(545, yb + 30, 150, 56,
                    "нема чому впасти —\nMOV бачить увесь\nкидок першим",
                    size=10.5, fill="#fdecea", stroke=RED, color=RED))

    # --- низ: З розв'язкою ---
    f.append(text(W / 2, 270, "З розв'язкою R/L: напруга падає на ній — GDT встигає перебрати удар", size=14, bold=True, color=FIELD))
    yc = 335
    f.append(line(70, yc, 650, yc, color=INK, sw=2.2))
    f.append(text(60, yc + 5, "вхід", size=11, color=MUTED, anchor="end"))
    # GDT
    f.append(line(180, yc, 180, yc + 40, color=INK, sw=2))
    f.append(rect(158, yc + 40, 44, 26, fill="#fdecea", stroke=RED, sw=2, rx=5))
    f.append(text(180, yc + 57, "GDT", size=11, color=RED, bold=True))
    f.append(line(180, yc + 66, 180, yc + 86, color=INK, sw=2))
    # розв'язувальний елемент у лінії
    f.append(rect(250, yc - 13, 70, 26, fill="#fff7e6", stroke="#d9a441", sw=2, rx=5))
    f.append(text(285, yc + 5, "R / L", size=12, color="#8a5a00", bold=True))
    f.append(text(285, yc - 22, "≥10 Ω або ≥10 мкГн", size=10, color="#8a5a00"))
    # MOV
    f.append(line(420, yc, 420, yc + 40, color=INK, sw=2))
    f.append(rect(398, yc + 40, 44, 26, fill="#eafaf0", stroke=FIELD, sw=2, rx=5))
    f.append(text(420, yc + 57, "MOV", size=11, color=FIELD, bold=True))
    f.append(line(420, yc + 66, 420, yc + 86, color=INK, sw=2))
    # земля
    f.append(line(100, yc + 86, 520, yc + 86, color=INK, sw=2.2))
    for gx in (130, 180, 230, 370, 420, 470):
        f.append(line(gx, yc + 86, gx - 8, yc + 96, color=INK, sw=2))
    # напрям струму удару
    f.append(arrow(95, yc - 14, 165, yc - 14, color=RED, sw=2))
    f.append(text(130, yc - 24, "кидок", size=10, color=RED))
    f.append(fitbox(545, yc + 30, 150, 56,
                    "на R/L «зайва»\nнапруга падає —\nGDT бере силу",
                    size=10.5, fill="#eafaf0", stroke=FIELD, color=FIELD))

    return render(os.path.join(IMG, "decoupling.svg"), W, H, *f)


# ── 3. Естафета вниз ланцюгом: напруга на вузлах + хвіст рве запобіжник ───────
def fig_letthrough():
    W, H = 820, 430
    f = []
    f.append(text(W / 2, 30, "Естафета каскаду: кожен щабель збиває кидок усе нижче", size=15, bold=True))

    # горизонтальний ланцюг блоків
    y = 130
    boxw, boxh = 96, 50
    xs = [55, 215, 375, 535]
    names = ["вхід\nкабелю", "GDT", "MOV", "TVS"]
    cols  = [MUTED, RED, FIELD, BLU]
    fills = ["#f1f3f5", "#fdecea", "#eafaf0", "#eaf0fd"]
    for x, nm, c, fl in zip(xs, names, cols, fills):
        f.append(fitbox(x, y, boxw, boxh, nm, size=11.5, fill=fl, stroke=c, color=c, bold=True))
    # розв'язки між блоками + стрілки
    for x in xs[:-1]:
        ax1 = x + boxw
        ax2 = x + 160
        f.append(rect((ax1 + ax2) / 2 - 18, y + boxh / 2 - 11, 36, 22, fill="#fff7e6", stroke="#d9a441", sw=1.6, rx=4))
        f.append(text((ax1 + ax2) / 2, y + boxh / 2 + 4, "R/L", size=10, color="#8a5a00", bold=True))
        f.append(arrow(ax1 + 2, y + boxh / 2, ax2 - 2, y + boxh / 2, color=INK, sw=1.8))
    # вихід на чип
    f.append(arrow(xs[-1] + boxw + 2, y + boxh / 2, xs[-1] + boxw + 55, y + boxh / 2, color=INK, sw=1.8))
    f.append(fitbox(xs[-1] + boxw + 57, y + boxh / 2 - 22, 78, 44, "чип\n3.3 В", size=11, fill="#fff", stroke=INK, color=INK))

    # рядок напруг під блоками
    yv = y + boxh + 36
    volts = ["8000 В", "≈700 В", "≈40 В", "≈6 В"]
    for x, v, c in zip(xs, volts, cols):
        f.append(text(x + boxw / 2, yv, v, size=14, color=c, bold=True))
    f.append(text(xs[0] + boxw / 2, yv + 20, "грозова\nнаводка".split("\n")[0], size=10, color=MUTED))
    f.append(text(xs[-1] + boxw + 96, yv, "стерпно", size=11, color=INK))

    # стовпчики «висоти кидка» — наочно спадають
    yb = 380
    base = yv + 34
    heights = [150, 70, 24, 8]
    for x, hgt, c in zip(xs, heights, cols):
        f.append(rect(x + boxw / 2 - 16, yb - hgt, 32, hgt, fill=c, stroke=c, sw=1, rx=3))
    f.append(line(50, yb, 670, yb, color=INK, sw=1.5))
    f.append(text(60, yb + 16, "висота кидка спадає від щабля до щабля — кожен бере свою частку", size=11, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "letthrough.svg"), W, H, *f)


# ── 4. Повна карта вузла: запобіжник у розрив + каскад поперек ────────────────
def fig_full_node():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 28, "Повний вузол: запобіжник у розрив, каскад — поперек на землю", size=14, bold=True))

    yL = 110          # «гаряча» лінія
    yG = 300          # земля
    f.append(text(55, yL + 5, "вхід", size=11, color=MUTED, anchor="end"))
    # запобіжник у розрив на самому початку
    f.append(line(60, yL, 110, yL, color=INK, sw=2.2))
    f.append(rect(110, yL - 12, 56, 24, fill="#fff", stroke=INK, sw=2, rx=10))
    f.append(text(138, yL + 5, "FUSE", size=11, color=INK, bold=True))
    f.append(text(138, yL - 20, "у розрив", size=10, color=MUTED))
    f.append(line(166, yL, 650, yL, color=INK, sw=2.2))

    # земляна шина
    f.append(line(60, yG, 660, yG, color=INK, sw=2.4))
    for gx in (100, 360, 620):
        f.append(line(gx, yG, gx - 10, yG + 12, color=INK, sw=2))
        f.append(line(gx + 14, yG, gx + 4, yG + 12, color=INK, sw=2))
        f.append(line(gx + 28, yG, gx + 18, yG + 12, color=INK, sw=2))

    # три щаблі поперек + розв'язки в лінії між ними
    def shunt(x, label, color, fillc):
        out = line(x, yL, x, yL + 55, color=INK, sw=2)
        out += rect(x - 26, yL + 55, 52, 28, fill=fillc, stroke=color, sw=2.2, rx=6)
        out += text(x, yL + 73, label, size=12, color=color, bold=True)
        out += line(x, yL + 83, x, yG, color=INK, sw=2)
        return out

    def decouple(x, lab):
        out = rect(x - 30, yL - 12, 60, 24, fill="#fff7e6", stroke="#d9a441", sw=2, rx=5)
        out += text(x, yL + 5, lab, size=11, color="#8a5a00", bold=True)
        return out

    f.append(shunt(230, "GDT", RED, "#fdecea"))
    f.append(decouple(320, "R/L"))
    f.append(shunt(410, "MOV", FIELD, "#eafaf0"))
    f.append(decouple(500, "R/L"))
    f.append(shunt(590, "TVS", BLU, "#eaf0fd"))

    # вихід до схеми
    f.append(arrow(650, yL, 690, yL, color=INK, sw=1.8))
    f.append(text(672, yL - 10, "до схеми", size=10, color=INK, anchor="middle"))

    # підписи ролей знизу
    f.append(text(230, yG + 40, "груба сила\nкілоампери".replace("\n", ", "), size=10, color=RED))
    f.append(text(410, yG + 40, "середній\nсотні А".replace("\n", ", "), size=10, color=FIELD))
    f.append(text(590, yG + 40, "тонкий доводчик\nдо вольтів".replace("\n", ", "), size=10, color=BLU))

    return render(os.path.join(IMG, "full-node.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tradeoff()
    fig_decoupling()
    fig_letthrough()
    fig_full_node()
    print("OK: figures written to", IMG)
