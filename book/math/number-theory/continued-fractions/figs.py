# -*- coding: utf-8 -*-
"""Фігури до статті «Ланцюгові дроби».
Три SVG у ./img/:
  peel.svg        — механіка розкладу 43/19 ліворуч + вкладена башта праворуч
  convergents.svg — підхідні дроби π обступають π з двох боків (схема, не в масштабі)
  golden.svg      — зростання знаменників: золотий перетин (Фібоначчі) vs велика неповна частка
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. peel.svg — розклад 43/19: механіка ліворуч, башта праворуч
# ─────────────────────────────────────────────────────────────────────────────
def fig_peel():
    W, H = 700, 380
    f = []

    # роздільник між панелями
    f.append(line(430, 45, 430, 350, color=MUTED, sw=1, dash="4,5"))
    f.append(text(220, 60, "механіка розкладу", size=13, color=MUTED, italic=True))
    f.append(text(565, 60, "вкладена башта", size=13, color=MUTED, italic=True))

    # ── ліва панель: чотири щаблі ділення ──
    rows = [
        ("43/19 =", "2", "+ 5/19"),
        ("19/5 =",  "3", "+ 4/5"),
        ("5/4 =",   "1", "+ 1/4"),
        ("4/1 =",   "4", ""),
    ]
    ys = [100, 170, 240, 310]
    for (lhs, q, rhs), y in zip(rows, ys):
        f.append(text(120, y, lhs, size=19, color=INK, anchor="end"))
        f.append(text(140, y, q, size=19, color=FIELD, anchor="start", bold=True))
        if rhs:
            f.append(text(168, y, rhs, size=19, color=INK, anchor="start"))

    # стрілки «перевернути хвіст» між щаблями
    for y in ys[:-1]:
        f.append(arrow(360, y + 6, 360, y + 54, color=NEG, sw=1.6))
    f.append(text(374, 140, "перевертаємо", size=12, color=NEG, anchor="start"))
    f.append(text(374, 156, "хвіст", size=12, color=NEG, anchor="start"))

    # підпис під лівою панеллю: цілі частини — це і є дріб
    f.append(text(200, 352, "цілі частини: 2, 3, 1, 4", size=13, color=FIELD, bold=True))

    # ── права панель: вкладена башта [2; 3, 1, 4] ──
    # спадні щаблі: інт + дробова риска, знаменник — наступний щабель нижче-праворуч
    levels = [
        ("2", 470, 150),
        ("3", 500, 190),
        ("1", 530, 230),
        ("4", 560, 270),
    ]
    for i, (q, x, y) in enumerate(levels):
        f.append(text(x, y, q, size=20, color=FIELD, anchor="start", bold=True))
        if i < len(levels) - 1:
            f.append(text(x + 18, y, "+", size=18, color=INK, anchor="start"))
            bx1, bx2, by = x + 33, x + 73, y - 5
            f.append(text((bx1 + bx2) / 2, by - 6, "1", size=15, color=INK))  # чисельник
            f.append(line(bx1, by, bx2, by, color=INK, sw=1.6))               # дробова риска

    f.append(text(470, 320, "= [2; 3, 1, 4]", size=17, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, "peel.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. convergents.svg — підхідні дроби π обступають число з двох боків
# ─────────────────────────────────────────────────────────────────────────────
def fig_convergents():
    W, H = 820, 340
    f = []
    axis_y = 200
    pi_x = 430

    # вісь
    f.append(line(50, axis_y, 790, axis_y, color=LINE, sw=1.8))
    f.append(text(70, axis_y - 10, "менше", size=12, color=MUTED, anchor="start"))
    f.append(text(770, axis_y - 10, "більше", size=12, color=MUTED, anchor="end"))

    # π у центрі
    f.append(line(pi_x, 95, pi_x, 300, color=INK, sw=1.6, dash="5,4"))
    f.append(text(pi_x, 84, "π = 3.14159265…", size=17, color=INK, bold=True))

    # точки: (x, колір, згори/знизу, [рядки підпису])
    pts = [
        (95,  NEG, "below", ["3",       "[3]",           "3.000000"]),
        (330, NEG, "below", ["333/106", "[3; 7, 15]",    "3.141509"]),
        (520, POS, "above", ["355/113", "[3; 7, 15, 1]", "3.14159292"]),
        (755, POS, "above", ["22/7",    "[3; 7]",        "3.142857"]),
    ]
    for x, col, side, lines in pts:
        f.append(circle(x, axis_y, 5.5, fill=col, stroke=col, sw=1))
        # стрілочка до π
        if x < pi_x:
            f.append(arrow(x + 9, axis_y, min(x + 55, pi_x - 8), axis_y, color=col, sw=1.4))
        else:
            f.append(arrow(x - 9, axis_y, max(x - 55, pi_x + 8), axis_y, color=col, sw=1.4))
        if side == "above":
            ty = axis_y - 78
        else:
            ty = axis_y + 34
        f.append(mtext(x, ty, lines, size=14, color=col, lh=1.35, bold=False))

    # позначка «найближчий»
    f.append(text(520, axis_y + 30, "майже впритул", size=12, color=POS, italic=True))
    # застереження
    f.append(text(60, 322, "положення схематичне, не в масштабі", size=12, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "convergents.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. golden.svg — зростання знаменників: Фібоначчі (найповільніше) vs стрибок
# ─────────────────────────────────────────────────────────────────────────────
def fig_golden():
    import math
    W, H = 840, 380
    f = []
    base_y = 300
    scale = 46.0  # px на одиницю log10(q)

    def bar(x, w, q, col):
        h = scale * math.log10(q) + 3
        f.append(rect(x, base_y - h, w, h, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + w / 2, base_y - h - 7, str(q), size=12, color=col))

    # роздільник
    f.append(line(430, 55, 430, base_y + 6, color=MUTED, sw=1, dash="4,5"))

    # спільна базова лінія
    f.append(line(50, base_y, 800, base_y, color=LINE, sw=1.6))
    f.append(text(60, base_y + 22, "крок розкладу →", size=12, color=MUTED, anchor="start"))
    f.append(text(60, 78, "знаменник qₙ (лог. шкала)", size=12, color=MUTED, anchor="start"))

    # ── панель A: золотий перетин, усі частки = 1 ──
    f.append(text(215, 52, "φ = [1; 1, 1, 1, …]", size=16, color=INK, bold=True))
    golden_q = [1, 2, 3, 5, 8, 13, 21, 34]
    xs = 70
    for i, q in enumerate(golden_q):
        bar(xs + i * 44, 28, q, FIELD)
    f.append(mtext(215, 336, ["знаменники — числа Фібоначчі:",
                              "ростуть найповільніше з можливих"],
                   size=12, color=FIELD, lh=1.3))

    # ── панель B: велика неповна частка ──
    f.append(text(625, 52, "x = [3; 7, 15, 1, 292, …]", size=16, color=INK, bold=True))
    big_q = [1, 7, 106, 113, 33102]
    xs2 = 480
    for i, q in enumerate(big_q):
        col = POS if i == len(big_q) - 1 else INK
        bar(xs2 + i * 62, 40, q, col)
    # позначити стрибок (стрілка на великий стовпчик, підпис у межах полотна)
    big_x = xs2 + 4 * 62  # ліва грань останнього стовпчика (=728)
    f.append(arrow(big_x - 34, 120, big_x - 4, 95, color=POS, sw=1.7))
    f.append(text(big_x - 40, 116, "стрибок", size=12, color=POS, anchor="end", bold=True))
    f.append(mtext(625, 336, ["велика частка 292 → знаменник",
                              "стрибає до 33 102 за один крок"],
                   size=12, color=POS, lh=1.3))

    render(os.path.join(IMG, "golden.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. birth-timeline.svg — до нарису hist-birth: два тисячоліття між машиною і числом
# ─────────────────────────────────────────────────────────────────────────────
def fig_birth_timeline():
    W, H = 880, 320
    f = []
    axis_y = 150

    # вісь із розривом (антика ліворуч, європейський сплеск праворуч)
    f.append(line(55, axis_y, 244, axis_y, color=LINE, sw=1.8))
    f.append(line(276, axis_y, 828, axis_y, color=LINE, sw=1.8))
    # злам осі — дві похилі рисочки
    f.append(line(250, axis_y - 9, 260, axis_y + 9, color=MUTED, sw=1.6))
    f.append(line(260, axis_y - 9, 270, axis_y + 9, color=MUTED, sw=1.6))

    def marker(x, name, year, side, col):
        f.append(circle(x, axis_y, 5, fill=col, stroke=col, sw=1))
        if side == "above":
            f.append(line(x, axis_y - 4, x, axis_y - 24, color=col, sw=1.3))
            f.append(text(x, axis_y - 46, name, size=13, color=col, bold=True))
            f.append(text(x, axis_y - 30, year, size=12, color=col))
        else:
            f.append(line(x, axis_y + 4, x, axis_y + 24, color=col, sw=1.3))
            f.append(text(x, axis_y + 40, name, size=13, color=col, bold=True))
            f.append(text(x, axis_y + 56, year, size=12, color=col))

    # антика — двигун є, але чисел у ньому не бачать (приглушено)
    marker(120, "антифайресис", "греки, ~450 до н.е.", "above", MUTED)
    marker(205, "куттака", "Індія, 499", "below", MUTED)

    # європейський сплеск — 220 років від першого запису до закону
    marker(320, "Бомбеллі", "1572 · √13", "below", INK)
    marker(417, "Катальді", "1613 · √18", "above", INK)
    marker(519, "Валліс · Броункер", "1655–56 · 4/π", "below", FIELD)
    marker(700, "Ойлер", "1737 · e іррац.", "above", INK)
    marker(792, "Лагранж", "1770 · період", "below", INK)

    # підписи зон
    f.append(text(140, axis_y + 92, "двигун працює — чисел у ньому не бачать",
                  size=12, color=MUTED, anchor="middle", italic=True))
    f.append(text(560, axis_y + 92, "220 років: від першого запису до теорії й закону",
                  size=12, color=INK, anchor="middle", italic=True))

    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *f,
           title="Народження ланцюгового дробу")


# ─────────────────────────────────────────────────────────────────────────────
# 5. best-ceiling.svg — до вставки proj-best-approximation:
#    похибка vs знаменник для π; стеля Q=100 відтинає 333/106, і найкращий
#    дозволений дріб — напівпідхідний 311/99, а НЕ остання підхідна 22/7.
# ─────────────────────────────────────────────────────────────────────────────
def fig_best_ceiling():
    import math
    W, H = 800, 430
    f = []
    X0, X1 = 95, 720        # горизонт: знаменник q = 0 … 112
    Ytop, Ybot = 70, 340    # вертикаль: log10(похибки)
    QMAX = 112.0
    Ltop, Lbot = -1.6, -4.3

    def xq(q):
        return X0 + q / QMAX * (X1 - X0)

    def yE(err):
        L = math.log10(err)
        return Ytop + (Ltop - L) / (Ltop - Lbot) * (Ybot - Ytop)

    def err(p, q):
        return abs(math.pi - p / q)

    # осі
    f.append(line(X0, Ytop - 6, X0, Ybot, color=LINE, sw=1.6))
    f.append(line(X0, Ybot, X1 + 8, Ybot, color=LINE, sw=1.6))
    # поділки знаменника
    for qt in (0, 20, 40, 60, 80, 100):
        f.append(line(xq(qt), Ybot, xq(qt), Ybot + 5, color=MUTED, sw=1.2))
        f.append(text(xq(qt), Ybot + 20, str(qt), size=12, color=MUTED))
    f.append(text(X1 - 10, Ybot + 38, "знаменник q →", size=13, color=MUTED, anchor="end"))
    f.append(mtext(X0 - 6, Ytop - 20, ["похибка │π − p/q│", "(лог; нижче — точніше)"],
                   size=12, color=MUTED, anchor="start", lh=1.25))

    # стеля Q = 100
    xc = xq(100)
    f.append(line(xc, Ytop - 10, xc, Ybot, color=POS, sw=1.7, dash="5,4"))
    f.append(text(xc + 6, Ytop + 2, "стеля Q = 100", size=13, color=POS, anchor="start", bold=True))
    f.append(text(xc + 6, Ytop + 18, "далі — заборонено", size=11, color=POS, anchor="start"))

    # драбина напівпідхідних sₜ = (3+t·22)/(1+t·7), t = 1 … 13 (проміжні)
    stair = []
    for t in range(1, 14):
        p, q = 3 + t * 22, 1 + t * 7
        stair.append((xq(q), yE(err(p, q))))
    for (x1, y1), (x2, y2) in zip(stair, stair[1:]):
        f.append(line(x1, y1, x2, y2, color=MUTED, sw=1.1))
    for x, y in stair:
        f.append(circle(x, y, 3.2, fill=BG, stroke=MUTED, sw=1.3))
    f.append(text(xq(45), yE(err(157, 50)) - 16, "напівпідхідні (драбина)",
                  size=12, color=MUTED, italic=True, anchor="middle"))

    # 22/7 — остання підхідна, що влізла (наївна, але далека відповідь)
    x7, y7 = xq(7), yE(err(22, 7))
    # горизонтальний орієнтир: рівень 22/7 тягнеться до стелі
    f.append(line(x7, y7, xc, y7, color=INK, sw=1.0, dash="2,4"))
    f.append(circle(x7, y7, 5.5, fill=BG, stroke=INK, sw=1.8))
    f.append(mtext(x7 + 12, y7 + 4, ["22/7 · q = 7", "остання підхідна"],
                   size=12.5, color=INK, anchor="start", lh=1.2))

    # 311/99 — напівпідхідний під стелею: ВІДПОВІДЬ
    x99, y99 = xq(99), yE(err(311, 99))
    f.append(circle(x99, y99, 6.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(mtext(x99 - 14, y99 + 5, ["311/99 · q = 99", "найкращий під стелею"],
                   size=13, color=FIELD, anchor="end", lh=1.2, bold=True))

    # 333/106 — підхідний ЗА стелею (недосяжний)
    x106, y106 = xq(106), yE(err(333, 106))
    f.append(circle(x106, y106, 5, fill=BG, stroke=MUTED, sw=1.5))
    f.append(mtext(x106 + 9, y106 + 4, ["333/106", "q = 106 — за стелею"],
                   size=11.5, color=MUTED, anchor="start", lh=1.2))

    render(os.path.join(IMG, "best-ceiling.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 6. lattice.svg — до вставки math-convergents: підхідні дроби √2 як вузли
#    цілочислової ґратки; ±1 = одинична площа паралелограма на сусідніх векторах
# ─────────────────────────────────────────────────────────────────────────────
def fig_lattice():
    import math
    W, H = 560, 470
    f = []

    U = 42.0            # px на одиницю ґратки
    ox, oy = 85.0, 400.0
    def sx(q): return ox + U * q
    def sy(p): return oy - U * p

    QMAX, PMAX = 6, 8
    slope = math.sqrt(2)

    # ── вузли ґратки (легкі крапки) ──
    for q in range(0, QMAX + 1):
        for p in range(0, PMAX + 1):
            f.append(circle(sx(q), sy(p), 1.7, fill=MUTED, stroke=MUTED, sw=0.5))

    # ── осі ──
    f.append(arrow(ox, oy, sx(QMAX) + 14, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, sy(PMAX) - 10, color=INK, sw=1.6))
    f.append(text(ox + 8, sy(PMAX) - 6, "чисельник p", size=11, color=MUTED, anchor="start"))
    f.append(text(sx(QMAX) + 20, oy + 4, "знаменник q", size=11, color=MUTED, anchor="start"))
    # позначки осей
    for q in range(1, QMAX + 1):
        f.append(text(sx(q), oy + 16, str(q), size=10, color=MUTED))
    for p in range(1, PMAX + 1):
        f.append(text(ox - 12, sy(p) + 4, str(p), size=10, color=MUTED, anchor="middle"))

    # ── промінь нахилу √2 ──
    f.append(line(ox, oy, sx(QMAX), sy(QMAX * slope), color=FIELD, sw=1.8, dash="6,4"))
    f.append(text(350, 150, "промінь нахилу", size=12, color=FIELD, anchor="start", italic=True))
    f.append(text(350, 167, "y = √2·q", size=12, color=FIELD, anchor="start", italic=True))

    # ── вектори до перших двох підхідних дробів ──
    f.append(line(ox, oy, sx(1), sy(1), color=MUTED, sw=1.3))
    f.append(line(ox, oy, sx(2), sy(3), color=MUTED, sw=1.3))

    # ── одинична клітинка на векторах (1,1) та (2,3): вузли 0,(1,1),(3,4),(2,3) ──
    poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
            'fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="1.6"/>'
            % (sx(0), sy(0), sx(1), sy(1), sx(3), sy(4), sx(2), sy(3), FIELD, FIELD))
    f.append(poly)
    f.append(line(225, 303, 150, 316, color=MUTED, sw=1.0))
    f.append(text(233, 300, "площа = 1", size=12, color=FIELD, anchor="start", bold=True))

    # ── точки-підхідні дроби: (1,1) низ, (2,3) верх, (5,7) низ ──
    conv = [
        (1, 1, NEG, "1/1", "start", 11, 16),
        (2, 3, POS, "3/2", "end",  -11, -8),
        (5, 7, NEG, "7/5", "end",  -11, -6),
    ]
    for q, p, col, lab, anc, dx, dy in conv:
        f.append(circle(sx(q), sy(p), 5.5, fill=col, stroke=col, sw=1))
        f.append(text(sx(q) + dx, sy(p) + dy, lab, size=14, color=col, anchor=anc, bold=True))

    # легенда боків (у відкритому куті праворуч)
    f.append(circle(360, 200, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(372, 204, "непарні — над променем", size=11, color=POS, anchor="start"))
    f.append(circle(360, 222, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(372, 226, "парні — під променем", size=11, color=NEG, anchor="start"))

    render(os.path.join(IMG, "lattice.svg"), W, H, *f,
           title="Підхідні дроби √2 у цілочисловій ґратці")


if __name__ == "__main__":
    fig_peel()
    fig_convergents()
    fig_golden()
    fig_birth_timeline()
    fig_best_ceiling()
    fig_lattice()
    print("OK:", ", ".join(sorted(os.listdir(IMG))))
