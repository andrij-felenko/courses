# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_FILL  = "#eef4ff"
RED_FILL   = "#fdecea"
GREY_FILL  = "#eef1f5"
GREEN_FILL = "#e8f8ee"
DASH = "5,4"


def node(cx, cy, s, r=19, fill=GREY_FILL, stroke=INK):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=1.7) + \
           text(cx, cy + 5, s, size=15, color=INK, bold=True)


def leaf(cx, cy, s, w=32, h=28):
    fill = RED_FILL if s == "1" else GREY_FILL
    col = POS if s == "1" else MUTED
    return rect(cx - w / 2.0, cy - h / 2.0, w, h, fill=fill, stroke=INK, sw=1.3, rx=4) + \
           text(cx, cy + 5, s, size=15, color=col, bold=True)


def edge(x1, y1, x2, y2, r1, r2, dash=None, color=LINE, sw=1.6):
    """Відрізок між вузлами, підрізаний на радіуси — не заходить усередину вузла."""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    if d == 0:
        return ""
    ux, uy = dx / d, dy / d
    return line(x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2,
                color=color, sw=sw, dash=dash)


def legend_01(x, y):
    """Спільна легенда «пунктир — нуль, суцільна — одиниця»."""
    out = line(x, y, x + 36, y, dash=DASH, sw=1.6)
    out += text(x + 44, y + 5, "змінна = 0", size=12, color=MUTED, anchor="start")
    out += line(x + 168, y, x + 204, y, sw=1.6)
    out += text(x + 212, y + 5, "змінна = 1", size=12, color=MUTED, anchor="start")
    return out


# ── 1. Канонічна форма: багато записів — один представник ────────────────────
def fig_canonical():
    W, H = 1020, 600
    p = []

    # ── верхній ряд: дроби (знайома аналогія) ──
    p.append(text(60, 76, "знайомий випадок — дроби", size=14, color=INK,
                  anchor="start", bold=True))
    p.append(rect(60, 92, 470, 108, fill=GREY_FILL, stroke=MUTED, sw=1.3, rx=10))
    for k, s in enumerate(["6/8", "75/100", "300/400", "27/36"]):
        b, _, _ = textbox(128 + k * 112, 146, s, size=16, bold=True,
                          fill=BG, stroke=MUTED, min_w=84)
        p.append(b)
    p.append(text(295, 220, "усі різні на вигляд — усі одне число", size=12, color=MUTED))

    p.append(arrow(556, 146, 636, 146))
    p.append(text(596, 128, "скоротити", size=12, color=MUTED))

    b, _, _ = textbox(736, 146, "3/4", size=20, bold=True, fill=GREEN_FILL,
                      stroke=FIELD, min_w=110)
    p.append(b)
    p.append(text(736, 220, "один представник класу", size=12, color=FIELD, bold=True))

    p.append(line(60, 258, 960, 258, color="#dfe3e8", sw=1.2))

    # ── нижній ряд: булеві функції ──
    p.append(text(60, 300, "той самий випадок — булеві функції", size=14, color=INK,
                  anchor="start", bold=True))
    p.append(rect(60, 316, 470, 168, fill=GREY_FILL, stroke=MUTED, sw=1.3, rx=10))
    forms = ["a·b + c", "(a + c)·(b + c)", "‾(c̄ · ‾(a·b))", "a·b·c̄ + c"]
    for k, s in enumerate(forms):
        b, _, _ = textbox(180 + (k % 2) * 232, 364 + (k // 2) * 76, s, size=15,
                          bold=True, fill=BG, stroke=MUTED, min_w=196)
        p.append(b)
    p.append(text(295, 508, "чотири формули — одна функція", size=12, color=MUTED))

    p.append(arrow(556, 396, 636, 396))
    p.append(mtext(596, 366, ["фіксуємо порядок", "a < b < c", "і скорочуємо"],
                   size=11, color=MUTED))

    # діаграма-представник
    DX, DY = 736, 340
    p.append(rect(654, 316, 168, 168, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=10))
    NA, NB, NC = (700, 350), (772, 396), (700, 396)
    T0, T1 = (700, 454), (772, 454)
    p.append(edge(NA[0], NA[1], NC[0], NC[1], 19, 19, dash=DASH))
    p.append(edge(NA[0], NA[1], NB[0], NB[1], 19, 19))
    p.append(edge(NB[0], NB[1], NC[0], NC[1], 19, 19, dash=DASH))
    p.append(edge(NB[0], NB[1], T1[0], T1[1], 19, 16))
    p.append(edge(NC[0], NC[1], T0[0], T0[1], 19, 16, dash=DASH))
    p.append(edge(NC[0], NC[1], T1[0], T1[1], 19, 16))
    p.append(node(NA[0], NA[1], "a", r=15, fill=BG))
    p.append(node(NB[0], NB[1], "b", r=15, fill=BG))
    p.append(node(NC[0], NC[1], "c", r=15, fill=BG))
    p.append(leaf(T0[0], T0[1], "0", w=26, h=22))
    p.append(leaf(T1[0], T1[1], "1", w=26, h=22))
    p.append(text(736, 508, "рівно одна діаграма", size=12, color=FIELD, bold=True))

    # де аналогія ламається
    b, _, _ = textbox(510, 560,
                      "Де аналогія ламається: у дробів представника видно оком — поділив на НСД, і по всьому.\n"
                      "У функції його не видно ніяк: діаграму треба спершу побудувати, а вона буває завелика.",
                      size=12, fill=RED_FILL, stroke=POS, color=INK)
    p.append(b)

    render(os.path.join(OUT, "canonical.svg"), W, H, *p,
           title="Канонічна форма: багато записів — рівно один представник")


# ── 2. Вузли — це і є різні звуження функції ─────────────────────────────────
def fig_subfunctions():
    W, H = 1040, 620
    p = []

    # ── ліворуч: перебір звужень за префіксами порядку ──
    p.append(text(60, 74, "усі звуження f = a·b + c за префіксами порядку a < b < c",
                  size=14, color=INK, anchor="start", bold=True))

    rows = [
        (110, "нічого не фіксуємо", ["f = a·b + c"], BLUE_FILL, NEG),
        (186, "фіксуємо a", ["f|a=0 = c", "f|a=1 = b + c"], BLUE_FILL, NEG),
        (262, "фіксуємо a, b", ["f|a=0,b=0 = c", "f|a=0,b=1 = c",
                                "f|a=1,b=0 = c", "f|a=1,b=1 = 1"], GREY_FILL, MUTED),
        (376, "фіксуємо a, b, c", ["константи 0 і 1"], GREY_FILL, MUTED),
    ]
    for y, cap, items, fill, col in rows:
        p.append(text(66, y + 6, cap, size=12, color=col, anchor="start", bold=True))
        for k, s in enumerate(items):
            b, _, _ = textbox(300 + (k % 2) * 172, y + (k // 2) * 42, s, size=13,
                              fill=fill, stroke=MUTED, min_w=158)
            p.append(b)

    b, _, _ = textbox(272, 470,
                      "Різних ФУНКЦІЙ тут лише п'ять: a·b + c, b + c, c, 1, 0.\n"
                      "Решта — повтори: f|a=0,b=0 і f|a=1,b=0 — та сама функція c,\n"
                      "бо жодна з них від b не залежить.",
                      size=12, fill=GREEN_FILL, stroke=FIELD)
    p.append(b)

    p.append(arrow(556, 262, 636, 262))
    p.append(text(596, 244, "кожній —", size=11, color=MUTED))
    p.append(text(596, 288, "свій вузол", size=11, color=MUTED))

    # ── праворуч: діаграма, кожен вузол підписано своїм звуженням ──
    p.append(text(860, 74, "діаграма тієї самої функції", size=14, color=INK, bold=True))

    NA, NB, NC = (820, 130), (940, 232), (820, 232)
    T0, T1 = (820, 340), (940, 340)
    p.append(edge(NA[0], NA[1], NC[0], NC[1], 19, 19, dash=DASH))
    p.append(edge(NA[0], NA[1], NB[0], NB[1], 19, 19))
    p.append(edge(NB[0], NB[1], NC[0], NC[1], 19, 19, dash=DASH))
    p.append(edge(NB[0], NB[1], T1[0], T1[1], 19, 16))
    p.append(edge(NC[0], NC[1], T0[0], T0[1], 19, 16, dash=DASH))
    p.append(edge(NC[0], NC[1], T1[0], T1[1], 19, 16))
    p.append(node(NA[0], NA[1], "a"))
    p.append(node(NB[0], NB[1], "b"))
    p.append(node(NC[0], NC[1], "c"))
    p.append(leaf(T0[0], T0[1], "0"))
    p.append(leaf(T1[0], T1[1], "1"))

    # підписи вузлів — праворуч/ліворуч від вузла, повз лінії
    labels = [
        (NA[0] - 34, NA[1] + 5, "a·b + c", "end", NEG),
        (NB[0] + 34, NB[1] + 5, "b + c", "start", NEG),
        (NC[0] - 34, NC[1] + 5, "c", "end", NEG),
        (T0[0] - 30, T0[1] + 5, "0", "end", MUTED),
        (T1[0] + 30, T1[1] + 5, "1", "start", MUTED),
    ]
    for x, y, s, anc, col in labels:
        p.append(text(x, y, s, size=13, color=col, anchor=anc, bold=True))

    b, _, _ = textbox(860, 434,
                      "5 різних звужень → 5 вузлів.\n"
                      "Вибору немає: менше — злиплися б різні\n"
                      "функції, більше — щось лежало б двічі.",
                      size=12, fill=GREEN_FILL, stroke=FIELD)
    p.append(b)

    p.append(legend_01(742, 508))

    b, _, _ = textbox(520, 576,
                      "Ось чому діаграма не залежить від формули: звуження — властивість самої\n"
                      "функції, а формула про них нічого не знає.",
                      size=12, fill=BG, stroke=MUTED, color=INK)
    p.append(b)

    render(os.path.join(OUT, "subfunctions.svg"), W, H, *p,
           title="Вузол діаграми — це не «крок обчислення», а окреме звуження функції")


# ── 3. Розріз: скільки різних звужень доводиться пам'ятати ───────────────────
def fig_width_cut():
    W, H = 1060, 660
    p = []
    p.append(text(530, 62, "f = x₁·x₂ + x₃·x₄ + x₅·x₆ — та сама функція, два порядки",
                  size=14, color=INK, bold=True))

    # ── ліворуч: порядок парами ──
    p.append(text(255, 108, "порядок  x₁ x₂ x₃ x₄ x₅ x₆", size=13, color=FIELD, bold=True))
    p.append(text(255, 130, "партнери поруч", size=12, color=MUTED))

    XL, XR = 170, 300
    LV = [178, 240, 302, 364, 426, 488]
    TY = 566
    Z, O = 140, 330
    names = ["x₁", "x₂", "x₃", "x₄", "x₅", "x₆"]
    for k, yy in enumerate(LV):
        p.append(text(104, yy + 5, names[k], size=12, color=MUTED, bold=True))

    p.append(edge(XL, LV[0], XL, LV[2], 19, 19, dash=DASH))
    p.append(edge(XL, LV[0], XR, LV[1], 19, 19))
    p.append(edge(XR, LV[1], XL, LV[2], 19, 19, dash=DASH))
    p.append(edge(XR, LV[1], O, TY, 19, 16))
    p.append(edge(XL, LV[2], XL, LV[4], 19, 19, dash=DASH))
    p.append(edge(XL, LV[2], XR, LV[3], 19, 19))
    p.append(edge(XR, LV[3], XL, LV[4], 19, 19, dash=DASH))
    p.append(edge(XR, LV[3], O, TY, 19, 16))
    p.append(edge(XL, LV[4], Z, TY, 19, 16, dash=DASH))
    p.append(edge(XL, LV[4], XR, LV[5], 19, 19))
    p.append(edge(XR, LV[5], Z, TY, 19, 16, dash=DASH))
    p.append(edge(XR, LV[5], O, TY, 19, 16))

    for k, yy in enumerate(LV):
        p.append(node(XL if k % 2 == 0 else XR, yy, names[k]))
    p.append(leaf(Z, TY, "0"))
    p.append(leaf(O, TY, "1"))

    # розріз після першої пари
    p.append(line(96, 272, 420, 272, color=POS, sw=1.6, dash="7,5"))
    p.append(text(428, 262, "розріз", size=12, color=POS, anchor="start", bold=True))
    p.append(text(428, 280, "2 звуження", size=12, color=POS, anchor="start", bold=True))

    b, _, _ = textbox(255, 622,
                      "після пари пам'ятати нема чого: або вже одиниця,\n"
                      "або починай спочатку → разом 2n + 2 = 8 вузлів",
                      size=12, fill=GREEN_FILL, stroke=FIELD)
    p.append(b)

    p.append(line(530, 96, 530, 596, color="#dfe3e8", sw=1.2))

    # ── праворуч: порядок «спершу всі непарні» ──
    p.append(text(810, 108, "порядок  x₁ x₃ x₅ x₂ x₄ x₆", size=13, color=POS, bold=True))
    p.append(text(810, 130, "партнери порізно", size=12, color=MUTED))

    # верхня половина — віяло 1 → 2 → 4
    up = [("x₁", 178, 1), ("x₃", 240, 2), ("x₅", 302, 4)]
    for nm, yy, w in up:
        p.append(text(600, yy + 5, nm, size=12, color=MUTED, bold=True))
        span = 240
        for i in range(w):
            cx = 810 - span / 2.0 + (span / (w - 1) if w > 1 else 0) * i if w > 1 else 810
            p.append(circle(cx, yy, 13, fill=GREY_FILL, stroke=INK, sw=1.4))
        p.append(text(972, yy + 5, "%d вузл%s" % (w, "" if w == 1 else "и"),
                      size=11, color=MUTED, anchor="start"))
    for yy0, w0, yy1, w1 in ((178, 1, 240, 2), (240, 2, 302, 4)):
        for i in range(w0):
            span0 = 240
            cx0 = 810 - span0 / 2.0 + (span0 / (w0 - 1) if w0 > 1 else 0) * i if w0 > 1 else 810
            for j in (0, 1):
                span1 = 240
                k = i * 2 + j
                cx1 = 810 - span1 / 2.0 + (span1 / (w1 - 1)) * k
                p.append(edge(cx0, yy0, cx1, yy1, 13, 13,
                              dash=(DASH if j == 0 else None)))

    # розріз
    p.append(line(600, 348, 1000, 348, color=POS, sw=1.8, dash="7,5"))
    p.append(text(810, 340, "розріз: 2³ = 8 різних звужень", size=12, color=POS, bold=True))

    # нижня половина — 8 залишків
    rest = ["0", "x₆", "x₄", "x₄+x₆", "x₂", "x₂+x₆", "x₂+x₄", "x₂+x₄+x₆"]
    for i, s in enumerate(rest):
        cx = 660 + (i % 4) * 100
        cy = 392 + (i // 4) * 48
        b, _, _ = textbox(cx, cy, s, size=11,
                          fill=(GREY_FILL if i == 0 else BLUE_FILL),
                          stroke=MUTED, min_w=88)
        p.append(b)

    b, _, _ = textbox(810, 512,
                      "усі 8 залишків — різні функції, тож жоден\n"
                      "не можна злити з іншим: кожному потрібен свій вузол",
                      size=12, fill=RED_FILL, stroke=POS)
    p.append(b)

    b, _, _ = textbox(810, 622,
                      "перед першою парною змінною треба пам'ятати, ЯКІ саме\n"
                      "непарні були одиницями → разом 2ⁿ⁺¹ = 16 вузлів",
                      size=12, fill=RED_FILL, stroke=POS)
    p.append(b)

    render(os.path.join(OUT, "width-cut.svg"), W, H, *p,
           title="Ширина розрізу — це пам'ять: 8 вузлів проти 16 на тій самій функції")


# ── 4. Два скорочення формально: вилучення й злиття ──────────────────────────
def fig_reduction_rules():
    W, H = 1080, 560
    p = []

    # ═══ верх: правило вилучення (зайвий вузол) ═══
    p.append(text(60, 60, "Правило вилучення — вузол з однаковими гілками",
                  size=15, color=INK, anchor="start", bold=True))

    # before: v, обидві гілки в один вузол w
    vx, vy, wx, wy = 168, 116, 168, 228
    p.append(line(vx - 12, vy + 16, wx - 22, wy - 16, color=LINE, sw=1.6, dash=DASH))
    p.append(line(vx + 12, vy + 16, wx + 22, wy - 16, color=LINE, sw=1.6))
    p.append(text(vx - 44, 178, "0", size=12, color=MUTED, bold=True))
    p.append(text(vx + 44, 178, "1", size=12, color=MUTED, bold=True))
    p.append(node(vx, vy, "v", r=19, fill=BLUE_FILL))
    p.append(rect(wx - 26, wy - 17, 52, 34, fill=GREY_FILL, stroke=INK, sw=1.4, rx=6))
    p.append(text(wx, wy + 5, "w", size=15, color=INK, bold=True))
    p.append(text(vx, 268, "low(v) = high(v) = w", size=12, color=NEG))

    p.append(arrow(258, 176, 338, 176))

    # after: сам w, вхідні стрілки — прямо в нього
    ax, ay = 438, 228
    p.append(arrow(ax, 122, ax, ay - 20))
    p.append(rect(ax - 26, ay - 17, 52, 34, fill=GREY_FILL, stroke=INK, sw=1.4, rx=6))
    p.append(text(ax, ay + 5, "w", size=15, color=INK, bold=True))
    p.append(mtext(ax, 100, ["стрілки, що вели у v,", "ведуть прямо у w"],
                   size=12, color=MUTED))

    b, _, _ = textbox(818, 152,
                      "Обидва виходи вузла ведуть в одне місце — отже його змінна\n"
                      "не впливає на відповідь. Питати про неї марно: вузол викидаємо,\n"
                      "а вхідні стрілки ведемо туди, куди він і так показував.",
                      size=12, fill=BLUE_FILL, stroke=NEG, color=INK)
    p.append(b)

    p.append(line(60, 300, 1020, 300, color="#dfe3e8", sw=1.2))

    # ═══ низ: правило злиття (дублікати) ═══
    p.append(text(60, 338, "Правило злиття — два вузли з тими самими гілками",
                  size=15, color=INK, anchor="start", bold=True))

    ux, vx2, ty = 130, 250, 388
    px, qx, by = 150, 300, 498
    for nx in (ux, vx2):
        p.append(line(nx, ty + 18, px + (0 if nx == ux else 8), by - 16,
                      color=LINE, sw=1.5, dash=DASH))        # low -> p
        p.append(line(nx, ty + 18, qx - (8 if nx == ux else 0), by - 16,
                      color=LINE, sw=1.5))                   # high -> q
    p.append(node(ux, ty, "u", r=19, fill=BLUE_FILL))
    p.append(node(vx2, ty, "v", r=19, fill=BLUE_FILL))
    p.append(node(px, by, "p", r=18))
    p.append(node(qx, by, "q", r=18))

    p.append(arrow(360, 443, 440, 443))

    mx, my = 542, 388
    p.append(line(mx, my + 22, mx - 30, by - 16, color=LINE, sw=1.5, dash=DASH))
    p.append(line(mx, my + 22, mx + 30, by - 16, color=LINE, sw=1.5))
    p.append(node(mx, my, "u≡v", r=23, fill=GREEN_FILL))
    p.append(node(mx - 32, by, "p", r=18))
    p.append(node(mx + 32, by, "q", r=18))

    p.append(text(300, 543, "та сама змінна xᵢ, ті самі p і q  ⟹  та сама функція",
                  size=12, color=MUTED))

    b, _, _ = textbox(842, 430,
                      "Однакова змінна й однакові діти — отже той самий кофактор,\n"
                      "та сама функція. Два примірники зайві: лишаємо один вузол,\n"
                      "усі посилання перенаправляємо на нього.",
                      size=12, fill=GREEN_FILL, stroke=FIELD, color=INK)
    p.append(b)

    render(os.path.join(OUT, "reduction-rules.svg"), W, H, *p,
           title="Два скорочення формально: коли вузол зайвий і коли двоє — одне")


# ── 5. Крок індукції: вузол змушений своїми двома звуженнями ──────────────────
def fig_canonicity_proof():
    W, H = 1100, 580
    p = []
    p.append(text(548, 58, "Один крок індукції: вузол змушений своїми двома звуженнями",
                  size=15, color=INK, bold=True))

    # ── ліворуч: вузол g і два кофактори ──
    gx, gy = 262, 132
    g0x, g1x, ccy = 172, 352, 304
    p.append(edge(gx, gy, g0x, ccy, 20, 34, dash=DASH))
    p.append(edge(gx, gy, g1x, ccy, 20, 34))
    p.append(text(196, 236, "xᵢ = 0", size=12, color=MUTED, bold=True))
    p.append(text(330, 236, "xᵢ = 1", size=12, color=MUTED, bold=True))
    p.append(node(gx, gy, "g", r=20, fill=BLUE_FILL))
    p.append(text(gx + 32, gy + 4, "рівень i, змінна xᵢ", size=12, color=NEG, anchor="start"))

    for xx, lab, sub in ((g0x, "g₀", "g|xᵢ=0"), (g1x, "g₁", "g|xᵢ=1")):
        p.append(circle(xx, ccy, 30, fill=GREY_FILL, stroke=INK, sw=1.6))
        p.append(text(xx, ccy - 3, lab, size=15, color=INK, bold=True))
        p.append(text(xx, ccy + 15, sub, size=10, color=MUTED))

    b, _, _ = textbox(262, 402,
                      "рівні > i: за припущенням індукції\n"
                      "кожне звуження вже має свій ЄДИНИЙ вузол",
                      size=12, fill=BG, stroke=MUTED, color=INK)
    p.append(b)

    p.append(line(538, 92, 538, 512, color="#dfe3e8", sw=1.2))

    # ── праворуч: логічний ланцюг ──
    chain = [
        (150, "g істотно залежить від xᵢ", BLUE_FILL, NEG),
        (216, "⟹   g₀ ≠ g₁", GREY_FILL, INK),
        (282, "⟹   node(g₀) ≠ node(g₁)   (різні звуження — різні вузли)", GREY_FILL, INK),
        (348, "⟹   low ≠ high: вузол не зайвий, переживає вилучення", GREEN_FILL, FIELD),
    ]
    for yy, s, fill, col in chain:
        b, _, _ = textbox(812, yy, s, size=12, fill=fill, stroke=col, color=INK, min_w=120)
        p.append(b)

    b, _, _ = textbox(812, 436,
                      "а правило злиття  ⟹  такий вузол рівно ОДИН.\n"
                      "Отже кожному звуженню — свій єдиний вузол,\n"
                      "а low і high теж задані звуженнями g₀, g₁.",
                      size=12, fill=GREEN_FILL, stroke=FIELD, color=INK)
    p.append(b)

    b, _, _ = textbox(550, 542,
                      "Уся діаграма визначена функцією f — її звуженнями, а не записом.\n"
                      "Дві скорочені діаграми однієї f збігаються вузол-у-вузол;   |вузли| = число різних звужень.",
                      size=12, fill=BLUE_FILL, stroke=NEG, color=INK)
    p.append(b)

    render(os.path.join(OUT, "canonicity-proof.svg"), W, H, *p,
           title="Чому скорочена діаграма єдина: вузли в бієкції зі звуженнями функції")


fig_canonical()
fig_subfunctions()
fig_width_cut()
fig_reduction_rules()
fig_canonicity_proof()
print("готово:", sorted(os.listdir(OUT)))
