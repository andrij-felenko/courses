# -*- coding: utf-8 -*-
"""Фігури до теми «MLCC».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CERAMIC = "#e7dcc3"   # колір тіла кераміки
METAL   = "#9aa0a6"   # електроди / металізація
WARM    = "#e08a3c"


# ── 1. Будова: гребінка електродів через один → N конденсаторів паралельно ────
def fig_structure():
    W, H = 720, 360
    f = [text(W / 2, 26, "MLCC у розрізі: сотні конденсаторів, увімкнених паралельно",
              size=16, bold=True)]
    f.append(text(W / 2, 46, "електроди-гребінка через один з'єднані з протилежними торцями",
                  size=11, color=MUTED, italic=True))

    # тіло кераміки
    bx, by, bw, bh = 60, 90, 300, 210
    f.append(rect(bx, by, bw, bh, fill=CERAMIC, stroke="#b9a97f", sw=2, rx=4))
    # дві металізовані «шапки» — торці
    cap = 26
    f.append(rect(bx - cap, by, cap, bh, fill=METAL, stroke="#6f7479", sw=1.6, rx=3))
    f.append(rect(bx + bw, by, cap, bh, fill=METAL, stroke="#6f7479", sw=1.6, rx=3))
    f.append(text(bx - cap / 2, by - 8, "торець", size=10.5, color=MUTED))
    f.append(text(bx + bw + cap / 2, by - 8, "торець", size=10.5, color=MUTED))

    # електроди: парні чіпляються лівого торця, непарні — правого
    n = 9
    gap = bh / (n + 1)
    elen = bw - 40
    for i in range(n):
        ey = by + (i + 1) * gap
        if i % 2 == 0:                       # від лівого торця
            ex = bx
        else:                                # від правого торця
            ex = bx + bw - elen
        col = POS if i % 2 == 0 else NEG
        f.append(rect(ex, ey - 3, elen, 6, fill=col, stroke="none", sw=0, rx=1))

    # пара сусідів = один конденсатор: виносна дужка
    y1 = by + 1 * gap
    y2 = by + 2 * gap
    f.append(line(bx + bw - 6, y1, bx + bw + 40, y1, color=MUTED, sw=1))
    f.append(line(bx + bw - 6, y2, bx + bw + 40, y2, color=MUTED, sw=1))
    f.append(line(bx + bw + 40, y1, bx + bw + 40, y2, color=MUTED, sw=1))
    f.append(text(bx + bw + 46, (y1 + y2) / 2 + 4, "одна пара —", size=10.5,
                  color=INK, anchor="start"))
    f.append(text(bx + bw + 46, (y1 + y2) / 2 + 18, "це конденсатор", size=10.5,
                  color=INK, anchor="start"))

    # права колонка — пояснення формули
    tx = 470
    f.append(text(tx, 150, "усі пари — паралельно:", size=12.5, color=INK,
                  anchor="start", bold=True))
    f.append(text(tx, 174, "C = N · (один шар)", size=14, color=FIELD,
                  anchor="start", bold=True))
    f.append(text(tx, 210, "шар кераміки — одиниці мкм:", size=12, color=INK, anchor="start"))
    f.append(text(tx, 230, "велике A, крихітне d", size=12, color=INK, anchor="start"))
    f.append(text(tx, 250, "у C = ε₀·εr·A/d", size=13, color=INK, anchor="start"))
    f.append(text(tx, 286, "корпус — від 0.4 мм;", size=12, color=INK, anchor="start"))
    f.append(text(tx, 306, "полярності немає", size=12, color=INK, anchor="start"))

    f.append(text(W / 2, 340, "червоні електроди йдуть до лівого торця, сині — до правого; "
                  "між кожними двома — шар кераміки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'mlcc-structure.svg'), W, H, *f)


# ── 2. Два класи кераміки: чому клас 1 стабільний, а клас 2 — ні ──────────────
def fig_classes():
    W, H = 720, 330
    f = [text(W / 2, 26, "Два класи кераміки: стабільність проти ємності", size=16, bold=True)]
    f.append(text(W / 2, 46, "диполі вирішують усе — і εr, і чи «пливе» ємність",
                  size=11, color=MUTED, italic=True))

    # ── ліва панель: клас 1 (параелектрик) ──
    f.append(rect(28, 64, 318, 168, fill="#f1f7f1", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(187, 86, "клас 1 — параелектрик (C0G/NP0)", size=12.5, color=FIELD, bold=True))
    # дрібні випадкові диполі, що ледь реагують
    import random
    random.seed(3)
    for _ in range(22):
        x = 60 + random.random() * 252
        y = 104 + random.random() * 96
        ang = random.random() * 360
        dx, dy = 7 * math.cos(math.radians(ang)), 7 * math.sin(math.radians(ang))
        f.append(line(x - dx, y - dy, x + dx, y + dy, color=MUTED, sw=1.6))
    f.append(text(187, 216, "εr скромна → лише дрібні номінали", size=10.5, color=INK))

    # ── права панель: клас 2 (сегнетоелектрик) ──
    f.append(rect(374, 64, 318, 168, fill="#fbf2f1", stroke=POS, sw=1.3, rx=8))
    f.append(text(533, 86, "клас 2 — сегнетоелектрик (титанат барію)", size=11.5, color=POS, bold=True))
    # великі домени, вишикувані рядами (легко вирівнюються полем)
    for row in range(3):
        for col in range(8):
            x = 400 + col * 35
            y = 118 + row * 30
            f.append(arrow(x - 9, y, x + 9, y, color=POS, sw=2))
    f.append(text(533, 216, "εr у тисячі → мкФ у крихітному корпусі", size=10.5, color=INK))

    # підсумок-стрічка
    f.append(rect(28, 246, 664, 64, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(48, 268, "ціна за велику εr:", size=12, anchor="start", bold=True))
    f.append(text(48, 290, "ті самі диполі, що дають ємність, вишиковуються й від температури, "
                  "і від постійної напруги — тому ємність класу 2 «пливе»",
                  size=11.5, anchor="start", color=INK))
    render(os.path.join(IMG, 'ceramic-classes.svg'), W, H, *f)


# ── 3. DC bias: залишок ємності проти постійної напруги ───────────────────────
def fig_dc_bias():
    W, H = 720, 380
    f = [text(W / 2, 26, "DC bias: скільки ємності лишається під постійною напругою",
              size=16, bold=True)]
    f.append(text(W / 2, 46, "кераміка класу 2 «насичується» полем — ємність провалюється",
                  size=11, color=MUTED, italic=True))

    # осі
    ox, oy = 96, 330            # початок координат
    ax, ay = 600, 80            # дальні кінці осей (x вправо, y вгору)
    f.append(line(ox, oy, ox, ay, color=INK, sw=2))                 # Y
    f.append(line(ox, oy, ax + 20, oy, color=INK, sw=2))            # X
    # сітка та підписи Y (0..100 %)
    for p in (0, 25, 50, 75, 100):
        yy = oy - (oy - ay) * p / 100.0
        if p:
            f.append(line(ox, yy, ax, yy, color="#e4e4e4", sw=1))
        f.append(text(ox - 10, yy + 4, "%d%%" % p, size=11, color=MUTED, anchor="end"))
    # підписи X (0..100 % від номіналу)
    for p in (0, 25, 50, 75, 100):
        xx = ox + (ax - ox) * p / 100.0
        f.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.2))
        f.append(text(xx, oy + 20, "%d%%" % p, size=11, color=MUTED))
    f.append(text((ox + ax) / 2, oy + 44, "постійна напруга, % від номінальної",
                  size=12, bold=True))
    # вертикальний підпис Y
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 34 %.1f)">'
             '%s</text>' % ((oy + ay) / 2, FONT, INK, (oy + ay) / 2,
                            esc("ємність, % від заявленої")))

    def curve(frac_at_100, color, label, ly):
        """Орієнтовна крива спаду: 100% при 0 В → frac_at_100 при 100%."""
        pts = []
        for i in range(101):
            x = i / 100.0
            # плавний, увігнутий спад
            val = 100 - (100 - frac_at_100) * (x ** 1.5)
            px = ox + (ax - ox) * x
            py = oy - (oy - ay) * val / 100.0
            pts.append((px, py))
        d = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, color))
        f.append(text(ax + 6, ly, label, size=11, color=color, anchor="start", bold=True))

    curve(100, FIELD, "C0G (клас 1)", oy - (oy - ay) * 100 / 100.0 + 4)
    curve(70,  NEG,   "X7R",          oy - (oy - ay) * 70 / 100.0 + 4)
    curve(48,  "#caa24a", "X5R, дрібний", oy - (oy - ay) * 48 / 100.0 + 4)
    curve(12,  POS,   "Y5V",          oy - (oy - ay) * 12 / 100.0 + 14)

    # пунктир «номінал»
    f.append(line(ox, ay, ax, ay, color=MUTED, sw=1.2, dash="6,5"))
    # підказка про корпус
    f.append(text(ox + 18, oy - (oy - ay) * 0.30,
                  "менший корпус того самого номіналу =", size=11, anchor="start", bold=True))
    f.append(text(ox + 18, oy - (oy - ay) * 0.30 + 16,
                  "тонші шари = сильніше поле = глибший провал", size=11, anchor="start", bold=True))
    render(os.path.join(IMG, 'dc-bias.svg'), W, H, *f)


if __name__ == "__main__":
    fig_structure()
    fig_classes()
    fig_dc_bias()
    print("OK: 3 фігури у", IMG)
