# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 5.3 — «Молекули життя» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; атоми/групи — стримані кольори;
кисень червоний. Хелпери скопійовані (розділи не діляться файлами).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e9e9e9"
GREEN = "#1f8a3b"
RED = "#c0271e"
BLUE = "#1f47b5"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
BOND = "#7c7c7c"
BEAD = "#ece9f3"
BEADLN = "#9b90bd"
CELL = "#eef6f1"
CELLLN = "#9fbfa9"
MITO = "#f3e1b6"
MITOLN = "#caa24a"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    m = "aGreen" if color == GREEN else "aInk"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=2):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def poly(points, color=INK, w=2, fill="none", close=True):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + (" Z" if close else "")
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def bond(x1, y1, x2, y2, w=4):
    return line(x1, y1, x2, y2, BOND, w)


def wavy(x0, y0, length, amp=6, n=3, color="#caa24a", w=3.5, direction=1):
    steps = 24
    pts = [(x0 + direction * length * i / steps, y0 + amp * math.sin(i / steps * n * 2 * math.pi))
           for i in range(steps + 1)]
    return poly(pts, color, w, close=False)


def hexagon(cx, cy, r, fill=BEAD, stroke=BEADLN, w=2, rot=0):
    pts = [(cx + r * math.cos(math.radians(60 * k + rot)),
            cy + r * math.sin(math.radians(60 * k + rot))) for k in range(6)]
    return poly(pts, stroke, w, fill)


def o2(cx, cy):
    return circle(cx - 6, cy, 6, O_FILL, O_LINE, 1.4) + circle(cx + 6, cy, 6, O_FILL, O_LINE, 1.4)


def lightning(cx, cy):
    pts = [(cx, cy - 16), (cx - 8, cy + 2), (cx - 1, cy + 2), (cx - 6, cy + 16),
           (cx + 9, cy - 4), (cx + 1, cy - 4)]
    return poly(pts, "#caa22e", 1.4, "#f4c430")


def glucose(cx, cy, r=30, detailed=False, label=None):
    s = hexagon(cx, cy, r, "#fff4e6", "#d9a441", 2.4)
    if detailed:
        for k in range(6):
            a = math.radians(60 * k - 30)
            vx, vy = cx + r * math.cos(a), cy + r * math.sin(a)
            if k in (0, 1, 3, 4):
                ox, oy = cx + (r + 16) * math.cos(a), cy + (r + 16) * math.sin(a)
                s += line(vx, vy, ox, oy, BOND, 2)
                s += text(ox, oy + 4, "OH", 10, "#9f2c22", "middle", "bold")
    if label:
        s += text(cx, cy + 4, label, 13, "#7a5a12", "middle", "bold")
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 5.3.1-1 — глюкоза як пальне клітини ─────────────────────────────────
def fig_fuel():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 28, "Глюкоза — головне пальне клітини", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "клітина поволі «спалює» глюкозу киснем — і дістає енергію",
              12.5, GREY, "middle", style="italic")

    # клітина з мітохондрією
    s += ellipse(410, 178, 160, 84, CELL, CELLLN, 2.4)
    s += text(300, 116, "клітина", 12.5, "#5a7a64", "middle", "bold")
    s += ellipse(410, 184, 56, 28, MITO, MITOLN, 2)
    s += text(410, 188, "тут горить", 11.5, "#7a5a12", "middle", "bold")

    # вхід — глюкоза + кисень
    s += glucose(120, 150, 22)
    s += text(120, 116, "глюкоза", 12.5, INK, "middle", "bold")
    s += o2(120, 200)
    s += text(138, 204, "+ кисень", 12, RED, "start", "bold")
    s += arrow(170, 176, 246, 178, INK, 2.6)
    s += text(208, 164, "пальне", 11.5, GREY, "middle", style="italic")

    # вихід — енергія + відходи
    s += arrow(572, 178, 676, 178, INK, 2.6)
    s += lightning(700, 160)
    s += text(716, 166, "енергія", 13, GREEN, "start", "bold")
    s += text(700, 198, "CO₂ + вода", 12, GREY, "middle")

    s += text(W / 2, 286, "те саме горіння, що в топці, лише повільне й кероване",
              12.5, GREY, "middle", style="italic")
    save("fig-5-3-1-1-fuel.svg", s)


# ── Рис. 5.3.1-2 — крохмаль і целюлоза: та сама ланка, інший стик ─────────────
def fig_chains():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 28, "Одна цеглинка — глюкоза; два різні ланцюги з неї", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "крохмаль і целюлоза складені з ТІЄЇ САМОЇ глюкози — різниця лише в стику ланок",
              12.5, GREY, "middle", style="italic")

    # цеглинка
    s += glucose(450, 110, 30, detailed=True)
    s += text(450, 172, "глюкоза — цеглинка (пальне клітин)", 13, INK, "middle", "bold")
    s += text(450, 200, "зчепити в ланцюг ↓", 12, GREY, "middle", style="italic")

    xs = [170, 250, 330, 410, 490]
    # крохмаль — рівний ряд однакових ланок
    s += text(95, 256, "крохмаль", 14, INK, "middle", "bold")
    for i in range(len(xs) - 1):
        s += line(xs[i] + 20, 256, xs[i + 1] - 20, 256, BOND, 4)
    for x in xs:
        s += hexagon(x, 256, 20)
        s += text(x, 261, "G", 12, "#5b5170", "middle", "bold")
    s += text(600, 250, "✓ ми перетравлюємо", 12.5, GREEN, "start", "bold")
    s += text(600, 268, "хліб, картопля, рис", 11.5, GREY, "start")

    # целюлоза — ті самі ланки, але «перевернуті» (зигзаг)
    s += text(95, 360, "целюлоза", 14, INK, "middle", "bold")
    yz = [360, 344, 360, 344, 360]
    for i in range(len(xs) - 1):
        s += line(xs[i] + 16, yz[i], xs[i + 1] - 16, yz[i + 1], BOND, 4)
    for x, y, k in zip(xs, yz, range(5)):
        s += hexagon(x, y, 20, rot=30 if k % 2 else 0)
        s += text(x, y + 5, "G", 12, "#5b5170", "middle", "bold")
    s += text(600, 354, "✗ не перетравлюємо", 12.5, RED, "start", "bold")
    s += text(600, 372, "дерево, папір, бавовна", 11.5, GREY, "start")

    s += text(330, 306, "та сама ланка «G» — лише взята за руки по-різному", 12, INK, "middle", style="italic")
    save("fig-5-3-1-2-glucose-chains.svg", s)


# ── Рис. 5.3.2-1 — жир як щільне пальне ──────────────────────────────────────
def fig_fat_energy():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 28, "Жир — найщільніший склад енергії", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "хвости напхані зв'язками Карбон–Гідроген — тим самим пальним, що й бензин",
              12.5, GREY, "middle", style="italic")

    # жир: гліцерин + 3 хвости
    gx, ys = 110, [120, 160, 200]
    for i in range(2):
        s += bond(gx, ys[i], gx, ys[i + 1])
    for y in ys:
        s += bond(gx, y, gx + 26, y) + circle(gx + 26, y, 9, O_FILL, O_LINE, 1.4)
        s += text(gx + 26, y + 3, "O", 9, "#fff", "middle", "bold")
        s += wavy(gx + 38, y, 150, 6, 5)
        s += circle(gx, y, 11, "#454545", "#2a2a2a", 1.8) + text(gx, y + 4, "C", 11, "#fff", "middle", "bold")
    s += text(150, 250, "жир: гліцерин + 3 хвости", 12, INK, "middle", "bold")
    s += text(150, 268, "хвіст = чисте пальне", 11, "#9a7d1c", "middle", style="italic")

    # порівняння енергії
    s += text(640, 118, "1 грам — скільки енергії", 13, INK, "middle", "bold")
    s += text(512, 162, "цукор", 12.5, INK, "end", "bold")
    s += rect(522, 150, 120, 24, "#cddc39", "#9aa81f", 1.5, 4)
    s += text(512, 210, "жир", 12.5, INK, "end", "bold")
    s += rect(522, 198, 244, 24, "#e0b24a", "#b8902f", 1.5, 4)
    s += text(640, 246, "жиру в грамі — десь удвічі більше", 11.5, GREY, "middle", style="italic")

    s += text(W / 2, 300, "тому тіло (і ведмідь) відкладає жир на голодний час",
              12.5, GREY, "middle", style="italic")
    save("fig-5-3-2-1-fat-energy.svg", s)


# ── Рис. 5.3.2-2 — білок: ланцюг → форма → денатурація ───────────────────────
_AA = ["#c0392b", "#2c7fb8", "#1f8a3b", "#e0a020", "#7b46a6", "#0f9e8e",
       "#d6457f", "#5a6acb", "#9aa81f", "#c0392b", "#2c7fb8", "#1f8a3b"]


def _beads(positions):
    s = ""
    for i in range(len(positions) - 1):
        s += line(*positions[i], *positions[i + 1], "#b8b8b8", 2.4)
    for i, (x, y) in enumerate(positions):
        s += circle(x, y, 8, _AA[i % len(_AA)], "#333", 1.4)
    return s


def fig_protein():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 28, "Білок: ланцюг, що згортається в машину", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "≈20 видів амінокислот у точному порядку → одна форма → робота",
              12.5, GREY, "middle", style="italic")

    # 1 — ланцюг
    chain = [(70 + i * 19, 165 + (8 if i % 2 else -8)) for i in range(10)]
    s += _beads(chain)
    s += text(150, 248, "ланцюг амінокислот", 12.5, INK, "middle", "bold")
    s += text(150, 266, "≈20 видів намистин", 11, GREY, "middle")

    s += arrow(298, 165, 372, 165, GREEN, 2.6)
    s += text(335, 150, "згортається", 11.5, GREEN, "middle", "bold")

    # 2 — згорнута форма
    folded = [(470, 150), (492, 138), (508, 160), (488, 176), (462, 172),
              (452, 150), (478, 130), (512, 140), (500, 184), (466, 192)]
    s += _beads(folded)
    s += text(482, 248, "згорнута форма = робота", 12.5, INK, "middle", "bold")
    s += text(482, 266, "фермент · м'яз · волос", 11, GREY, "middle")

    s += arrow(560, 165, 634, 165, RED, 2.6)
    s += text(597, 150, "нагрів", 11.5, RED, "middle", "bold")
    s += text(597, 186, "(назад не можна)", 10, RED, "middle", style="italic")

    # 3 — денатурований жмут
    tangle = [(700, 150), (740, 134), (770, 160), (810, 140), (835, 172),
              (800, 188), (760, 192), (725, 176), (785, 158), (820, 196)]
    s += _beads(tangle)
    s += text(770, 248, "денатурація", 12.5, RED, "middle", "bold")
    s += text(770, 266, "варене яйце — назад не можна", 11, GREY, "middle")

    s += text(W / 2, 312, "форма тримається на слабких зачіпках; нагрів їх розхитує — і вже не згорнути",
              12.5, GREY, "middle", style="italic")
    save("fig-5-3-2-2-protein.svg", s)


def _aroma(x, ybase, h=50):
    pts = [(x + 6 * math.sin(k * 1.1), ybase - k * h / 6) for k in range(7)]
    return poly(pts, "#9aa0a6", 2, close=False)


# ── Рис. 5.3.3-1 — реакція Маяра ─────────────────────────────────────────────
def fig_maillard():
    W, H = 880, 340
    s = header(W, H)
    s += text(W / 2, 28, "Реакція Маяра: чому смажене пахне, а варене — ні", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "у воді не гарячіше 100° — блідо; на сухому жару цукор зустрічає білок",
              12.5, GREY, "middle", style="italic")

    # варене
    s += rect(140, 158, 120, 88, "#eef2f4", INK, 2.4, 8)
    s += rect(146, 182, 108, 60, "#cfe6f5", "none", 0, 4)
    s += ellipse(200, 212, 28, 17, "#e8dcc0", "#b9a86a", 2)
    s += text(200, 272, "варене · 100°", 13, INK, "middle", "bold")
    s += text(200, 290, "вода тримає прохолоду → блідо", 11, GREY, "middle")

    s += line(440, 80, 440, 300, FAINT, 2, dash="5 5")

    # смажене
    s += ellipse(620, 216, 74, 13, "#9a9a9a", "#5a5a5a", 2)
    s += line(692, 216, 744, 208, "#5a5a5a", 6)
    s += ellipse(620, 200, 30, 19, "#b5793a", "#7a4a18", 2)
    for x in (602, 620, 638):
        s += _aroma(x, 180, 48)
    s += text(672, 150, "аромат", 11.5, GREY, "start", style="italic")
    # реакція над пательнею
    s += hexagon(556, 114, 14, "#fff4e6", "#d9a441", 2)
    s += text(556, 118, "цукор", 8.5, "#7a5a12", "middle", "bold")
    s += text(584, 119, "+", 16, INK, "middle", "bold")
    s += circle(608, 114, 11, "#2c7fb8", "#1c4f80", 1.6) + text(608, 118, "білок", 7.5, "#fff", "middle", "bold")
    s += arrow(624, 114, 660, 114, INK, 2.2)
    s += circle(684, 114, 13, "#8a5a2a", "#5a3a18", 1.6)
    s += text(620, 272, "смажене · ≈180°", 13, INK, "middle", "bold")
    s += text(620, 290, "цукор + білок → буре, пахуче", 11, GREY, "middle")
    save("fig-5-3-3-1-maillard.svg", s)


# ── Рис. 5.3.3-2 — дріжджі піднімають тісто ──────────────────────────────────
def fig_yeast():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 28, "Дріжджі їдять цукор — тісто росте", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "без повітря дріжджі лиш наполовину спалюють цукор і видихають газ",
              12.5, GREY, "middle", style="italic")

    # дріжджова клітина
    s += ellipse(180, 170, 48, 40, "#f0e2b8", "#c9a93f", 2.4)
    s += text(180, 174, "дріжджі", 12, "#7a5a12", "middle", "bold")
    s += hexagon(72, 170, 15, "#fff4e6", "#d9a441", 2)
    s += text(72, 140, "цукор", 11.5, INK, "middle", "bold")
    s += arrow(94, 170, 128, 170, INK, 2.4)
    s += arrow(224, 150, 268, 116, INK, 2.2)
    s += circle(288, 104, 15, "#eaf6fb", "#9bc0d6", 1.6) + text(288, 108, "CO₂", 10.5, "#5b7d90", "middle", "bold")
    s += text(300, 150, "+ трохи спирту", 11, GREY, "start", style="italic")
    s += text(180, 232, "з'їдають цукор, видихають газ", 11.5, GREY, "middle")

    s += arrow(348, 170, 426, 170, GREEN, 2.6)
    s += text(387, 156, "газ — у тісто", 11, GREEN, "middle", "bold")

    # тісто з бульбашками
    s += ellipse(620, 178, 78, 56, "#efe2c0", "#caa24a", 2.4)
    for bx, by, br in [(596, 168, 9), (636, 160, 11), (650, 196, 8),
                       (604, 200, 7), (628, 184, 6), (660, 176, 7)]:
        s += circle(bx, by, br, "#fbf6e8", "#cbb98a", 1.4)
    s += arrow(620, 250, 620, 214, GREEN, 2.6)
    s += text(620, 270, "тісто росте", 13, INK, "middle", "bold")
    s += text(620, 288, "(бульбашки CO₂ всередині)", 11, GREY, "middle")

    s += text(W / 2, 308, "той самий CO₂, що в газованці; працюють ферменти-білки",
              11.5, GREY, "middle", style="italic")
    save("fig-5-3-3-2-yeast.svg", s)


# ── Рис. 5.3.4-1 — карта: мова книги → назви підручника ──────────────────────
def fig_map():
    W, H = 920, 424
    s = header(W, H)
    s += text(W / 2, 28, "Що ти знаєш — мовою «великої» хімії", 20, INK, "middle", "bold")
    s += text(235, 56, "мовою цієї книги", 12.5, GREY, "middle", "bold")
    s += text(694, 56, "як зветься в підручнику", 12.5, GREY, "middle", "bold")

    rows = [
        (["Атоми й таблиця"], ["Будова атома · Періодичний закон"], "#eef3fb", "#9fb6e0"),
        (["Як атоми тримаються"], ["Хімічний зв'язок ·", "кількість речовини (моль)"], "#fdeef0", "#e0a9a9"),
        (["Реакції"], ["Хімічні реакції ·", "швидкість і рівновага"], "#fef6e6", "#e6c98a"),
        (["Розчини, кислоти,", "солі, метали"], ["Розчини · дисоціація ·", "класи неорг. сполук · метали"], "#eef7ef", "#9fc7a9"),
        (["Органіка"], ["Органічна хімія"], "#f3eef9", "#b9a0d8"),
    ]
    for i, (ll, rl, tint, bd) in enumerate(rows):
        top = 70 + i * 68
        cy = top + 29
        s += rect(40, top, 372, 58, tint, bd, 1.8, 10)
        s += circle(66, cy, 14, "#fff", bd, 2) + text(66, cy + 5, str(i + 1), 14, INK, "middle", "bold")
        if len(ll) == 1:
            s += text(252, cy + 5, ll[0], 13.5, INK, "middle", "bold")
        else:
            s += text(252, top + 26, ll[0], 13, INK, "middle", "bold")
            s += text(252, top + 45, ll[1], 13, INK, "middle", "bold")
        s += rect(500, top, 380, 58, "#f7f7f7", "#cfcfcf", 1.6, 10)
        if len(rl) == 1:
            s += text(690, cy + 5, rl[0], 12.5, INK, "middle")
        else:
            s += text(690, top + 26, rl[0], 12, INK, "middle")
            s += text(690, top + 45, rl[1], 12, INK, "middle")
        s += arrow(416, cy, 496, cy, INK, 2)

    s += text(W / 2, 412, "ти вже пройшов усю карту — далі лише деталі, що лягають на неї",
              12.5, GREY, "middle", style="italic")
    save("fig-5-3-4-1-map.svg", s)


if __name__ == "__main__":
    fig_fuel()
    fig_chains()
    fig_fat_energy()
    fig_protein()
    fig_maillard()
    fig_yeast()
    fig_map()
