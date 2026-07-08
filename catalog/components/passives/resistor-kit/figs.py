# -*- coding: utf-8 -*-
"""Фігури для статті «Набір резисторів» (catalog/components/passives/resistor-kit).
Дві фігури: (1) анатомія виводного резистора з розшифровкою чотирьох кольорових смуг;
(2) «логарифмічна лінійка» E12 — чому саме ці числа рівномірні в логарифмі.
Запуск: python figs.py  →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# кольори смуг за стандартом (для картинки резистора)
BAND = {
    "чорний":   "#1a1a1a", "коричн.":  "#7a4a1e", "черв.":    "#c0392b",
    "оранж.":   "#e07b00", "жовтий":   "#e8c400", "зелений":  "#27ae60",
    "синій":    "#2457d6", "фіолет.":  "#7b46b0", "сірий":    "#8a8a8a",
    "білий":    "#f2f2f2", "золотий":  "#c9a227",
}

# ── Фігура 1: анатомія резистора + розшифровка 220 Ω ±5 % ────────────────────
def fig_anatomy():
    W, H = 760, 400
    frags = []

    # тіло резистора (бежевий циліндр) з виводами
    body_x, body_y, body_w, body_h = 210, 70, 340, 74
    cy = body_y + body_h / 2
    # дротяні виводи
    frags.append(line(60, cy, body_x, cy, color=MUTED, sw=4))
    frags.append(line(body_x + body_w, cy, W - 60, cy, color=MUTED, sw=4))
    # тіло
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="34" '
                 'fill="#e9dcc3" stroke="#b9a77e" stroke-width="2"/>'
                 % (body_x, body_y, body_w, body_h))

    # чотири смуги: черв(2) черв(2) коричн(×10) золот(±5%)
    bands = [("черв.", "2"), ("черв.", "2"), ("коричн.", "×10"), None, ("золотий", "±5 %")]
    # позиції: три перші близько зліва, четверта відсунута праворуч
    xs = [body_x + 46, body_x + 78, body_x + 110, None, body_x + body_w - 46]
    bw = 16
    label_y = body_y + body_h + 30
    for (info, x) in zip(bands, xs):
        if info is None:
            continue
        name, meaning = info
        col = BAND[name]
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'fill="%s"/>' % (x - bw / 2, body_y + 4, bw, body_h - 8, col))
        # виноска вниз до підпису
        frags.append(line(x, body_y + body_h, x, label_y - 14, color=MUTED, sw=1, dash="3,3"))
        frags.append(text(x, label_y, name, size=12, color=INK))
        frags.append(text(x, label_y + 17, meaning, size=12, color=MUTED, bold=True))

    # підпис ролей смуг зверху
    frags.append(text(body_x + 78, body_y - 14, "1-а і 2-а цифри", size=12, color=INK))
    frags.append(text(body_x + 110, body_y - 32, "множник", size=12, color=INK, anchor="start"))
    frags.append(line(body_x + 110, body_y - 26, body_x + 110, body_y + 2, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(body_x + body_w - 46, body_y - 14, "допуск", size=12, color=INK))

    # обчислення внизу — власна рамка (не накладається)
    calc = "2   2   × 10   =  2 2 × 10  =  220 Ω,   ±5 %"
    box = fitbox(90, 250, W - 180, 58, calc, size=17, bold=True,
                 fill="#eef6ee", stroke=FIELD)
    frags.append(box)
    frags.append(text(W / 2, 340, "перші дві смуги дають число «22», третя множить на 10, "
                                  "остання — точність", size=13, color=MUTED))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *frags,
           title="Як чотири кольорові смуги кодують «220 Ω ±5 %»")

# ── Фігура 2: E12 як рівні кроки на логарифмічній осі ────────────────────────
def fig_e12():
    W, H = 780, 300
    frags = []
    e12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82, 100]  # +100 закриває декаду

    # вісь: логарифм від 1.0 до 10 (тобто 10..100 у цій декаді)
    ax_x0, ax_x1 = 70, W - 40
    ax_y = 150
    lo, hi = math.log10(10), math.log10(100)

    def X(v):
        return ax_x0 + (math.log10(v) - lo) / (hi - lo) * (ax_x1 - ax_x0)

    # сама вісь
    frags.append(line(ax_x0, ax_y, ax_x1, ax_y, color=INK, sw=2))
    # позначки декади 10 і 100
    for v, lab in [(10, "10"), (100, "100")]:
        frags.append(line(X(v), ax_y - 8, X(v), ax_y + 8, color=INK, sw=2))

    # риски E12 — рівні кроки в логарифмі, тому справа густіше в лінійному вимірі
    for v in e12:
        x = X(v)
        up = (e12.index(v) % 2 == 0)
        ty = ax_y - 22 if up else ax_y + 34
        frags.append(line(x, ax_y - 6, x, ax_y + 6, color=NEG, sw=1.6))
        frags.append(text(x, ty, str(v), size=13, color=INK, bold=(v in (10, 100))))

    # показати, що КРОК у логарифмі однаковий: дуги ×1.21 між сусідами
    a, b = 10, 12
    frags.append(text((X(a) + X(b)) / 2, ax_y + 66, "×1.21", size=12, color=POS))
    frags.append(line(X(a), ax_y + 52, X(b), ax_y + 52, color=POS, sw=1.4))
    c, d = 82, 100
    frags.append(text((X(c) + X(d)) / 2, ax_y + 66, "×1.21", size=12, color=POS))
    frags.append(line(X(c), ax_y + 52, X(d), ax_y + 52, color=POS, sw=1.4))

    # підпис-пояснення внизу власною рамкою
    note = ("однаковий множник між сусідами  →  однаковий відсотковий розрив; "
            "12 кроків замикають декаду ×10")
    frags.append(fitbox(70, 232, W - 110, 44, note, size=13, fill="#eef2ff", stroke=NEG))

    render(os.path.join(OUT, "e12-ladder.svg"), W, H, *frags,
           title="E12: дивні числа стоять рівно — у логарифмі, не в лінійці")

# ── Фігура 3: смуги допуску змикаються без дір (вставка math-e-series) ────────
def fig_stitch():
    """E12 з ±10 %: інтервали допуску сусідів торкаються на геометричному середньому.
    Показує ГОЛОВНИЙ аргумент вставки — чому крок саме ¹²√10."""
    W, H = 820, 360
    frags = []
    e12 = [10, 12, 15, 18, 22, 27, 33]        # шматок декади, щоб було видно
    tol = 0.10

    ax_x0, ax_x1 = 70, W - 40
    ax_y = 210
    lo, hi = math.log10(9), math.log10(36)

    def X(v):
        return ax_x0 + (math.log10(v) - lo) / (hi - lo) * (ax_x1 - ax_x0)

    # вісь (логарифмічна)
    frags.append(line(ax_x0, ax_y, ax_x1, ax_y, color=INK, sw=2))

    # для кожного номіналу — брусок допуску [v(1−t), v(1+t)]
    bar_h = 26
    for i, v in enumerate(e12):
        xL, xR = X(v * (1 - tol)), X(v * (1 + tol))
        col = NEG if i % 2 == 0 else POS
        fillc = "#eef2ff" if i % 2 == 0 else "#fdecea"
        y = ax_y - bar_h / 2 - (18 if i % 2 == 0 else -18)   # через один — вище/нижче, щоб не злипались
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
                     'fill="%s" stroke="%s" stroke-width="1.4"/>'
                     % (xL, y, xR - xL, bar_h, fillc, col))
        # риска номіналу + підпис
        frags.append(line(X(v), ax_y - 7, X(v), ax_y + 7, color=INK, sw=2))
        frags.append(text(X(v), ax_y + 26, str(v), size=13, color=INK, bold=True))

    # позначити точку стику двох сусідів (22 і 27) — геометричне середнє
    a, b = 22, 27
    gm = math.sqrt(a * b)
    frags.append(line(X(gm), ax_y - 78, X(gm), ax_y + 40, color=FIELD, sw=1.6, dash="4,4"))
    frags.append(text(X(gm), ax_y - 84, "стик: 22·1.1 ≈ 27·0.9", size=12, color=FIELD, bold=True))

    # підпис-висновок власною рамкою
    note = ("верхній край одного номіналу (×1.1) сходиться з нижнім краєм сусіда (×0.9)\n"
            "жодної діри — і майже жодного перекриття")
    frags.append(fitbox(70, 290, W - 110, 50, note, size=13, fill="#eef6ee", stroke=FIELD))

    render(os.path.join(OUT, "stitch.svg"), W, H, *frags,
           title="±10 % рівно зшиває сусідів E12 — звідси крок ¹²√10")

# ── Фігура 4: клас допуску ↔ густина ряду (E6/E12/E24/E96) ────────────────────
def fig_density():
    """Таблиця-місток: що тонший допуск, то щільніший ряд. Формула стику t = √(ⁿ√10) − 1."""
    W, H = 700, 340
    frags = []
    rows = [
        ("E6",  6,  "±20 %", 1.468),
        ("E12", 12, "±10 %", 1.212),
        ("E24", 24, "±5 %",  1.101),
        ("E96", 96, "±1 %",  1.024),
    ]
    # заголовки колонок
    cols_x = [110, 260, 430, 600]
    heads  = ["ряд", "крок ⁿ√10", "стик √(ⁿ√10)−1", "клас допуску"]
    top = 70
    for cx, h in zip(cols_x, heads):
        frags.append(text(cx, top, h, size=13, color=MUTED, bold=True))
    frags.append(line(60, top + 12, W - 40, top + 12, color=MUTED, sw=1))

    for i, (name, n, cls, r) in enumerate(rows):
        y = top + 44 + i * 52
        t = (math.sqrt(r) - 1) * 100
        frags.append(text(cols_x[0], y, name, size=16, color=INK, bold=True))
        frags.append(text(cols_x[1], y, "%.3f" % r, size=15, color=NEG))
        frags.append(text(cols_x[2], y, "≈ ±%.0f %%" % round(t), size=15, color=POS, bold=True))
        frags.append(text(cols_x[3], y, cls, size=15, color=FIELD, bold=True))
        if i < len(rows) - 1:
            frags.append(line(60, y + 20, W - 40, y + 20, color="#e5e7eb", sw=1))

    note = "тонший допуск ⇒ вужчі бруски ⇒ їх треба більше на декаду, щоб зімкнутися"
    frags.append(fitbox(70, 300, W - 110, 34, note, size=13, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, "density.svg"), W, H, *frags,
           title="Клас допуску сам диктує густину ряду")

if __name__ == "__main__":
    fig_anatomy()
    fig_e12()
    fig_stitch()
    fig_density()
    print("done:", os.listdir(OUT))
