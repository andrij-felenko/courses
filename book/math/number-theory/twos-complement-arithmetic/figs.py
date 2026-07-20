# -*- coding: utf-8 -*-
"""Фігури для math/number-theory/twos-complement-arithmetic.
svgkit імпортуємо зі scripts/, не переписуємо (§5 AUTHORING). Вивід — у ./img/.
Запуск:  python figs.py   →  python ../../../../scripts/svgcheck.py img
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"
BARF = "#4a4f57"          # засувка-шторка Паскалевої машини
REDF = "#fdecea"          # заливка під «червоний» ряд (доповнення)
BLKF = "#f2f4f7"          # заливка під «чорний» ряд (саме число)
GRNF = "#eef7f0"          # заливка під ствердне
WRNF = "#fdf3e3"          # заливка під «увага»


def mono(x, y, s, size=17, color=INK, anchor="middle", bold=True):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%g" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def win(cx, cy, s, w=52, h=44, fill=FILL, color=INK, fsize=20):
    """Віконце-цифра лічильника."""
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=LINE, sw=1.4, rx=5)
    out += mono(cx, cy + fsize * 0.35, s, size=fsize, color=color)
    return out


# ── 1. Паскалева машина: один стан коліс — два прочитання ────────────────────
def fig_pascaline():
    W, H = 1000, 470
    P = [text(W / 2, 34, "Паскалева машина: одні й ті самі колеса — два ряди віконець",
              size=19, bold=True),
         text(W / 2, 57, "засувка закриває один ряд, і ви читаєте або саме число, або його доповнення до дев'ятки",
              size=12.5, color=MUTED, italic=True)]

    digits_black = "000547"
    digits_red = "999452"
    cols = len(digits_black)
    cw = 62
    panel_w = cols * cw + 44
    gap = 66
    x0 = (W - 2 * panel_w - gap) / 2

    panels = [
        (x0, "Додавання", "засувка вгорі — читаємо нижній ряд", "у лічильнику  000547", GRNF),
        (x0 + panel_w + gap, "Віднімання", "засувка внизу — читаємо верхній ряд", "999999 − 000547 = 999452", WRNF),
    ]

    for pi, (px, ttl, sub, note, tint) in enumerate(panels):
        top_open = (pi == 1)
        cy_top, cy_bot = 176, 250

        P.append(rect(px, 96, panel_w, 250, fill="#ffffff", stroke=LINE, sw=1.8, rx=10))
        P.append(text(px + panel_w / 2, 121, ttl, size=16, bold=True))
        P.append(text(px + panel_w / 2, 141, sub, size=11.5, color=MUTED, italic=True))

        for i in range(cols):
            cx = px + 22 + cw * i + cw / 2
            P.append(win(cx, cy_top, digits_red[i], w=48, h=44,
                         fill=REDF if top_open else "#ffffff",
                         color=POS if top_open else "#d8dbe0"))
            P.append(win(cx, cy_bot, digits_black[i], w=48, h=44,
                         fill="#ffffff" if top_open else BLKF,
                         color="#d8dbe0" if top_open else INK))

        # засувка-шторка поверх закритого ряду
        by = cy_top if not top_open else cy_bot
        P.append(rect(px + 14, by - 25, panel_w - 28, 50, fill=BARF, stroke=BARF, sw=1.4, rx=6))
        P.append(text(px + panel_w / 2, by + 5, "засувка", size=13, color="#ffffff", bold=True))

        P.append(fitbox(px + 22, 306, panel_w - 44, 30, note, size=12.5, fill=tint, stroke=LINE))

    # підсумковий рядок
    P.append(rect(x0, 372, 2 * panel_w + gap, 64, fill=BLKF, stroke=LINE, sw=1.4, rx=8))
    P.append(mono(W / 2, 400, "547  +  452  =  999", size=19, color=INK))
    P.append(text(W / 2, 424, "у кожному стовпчику чорна цифра й червона дають дев'ятку — це й є доповнення до дев'ятки",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "pascaline-two-rows.svg"), W, H, *P)


# ── 2. Дев'ятка з кінцевим переносом проти десятки з викинутим переносом ──────
def fig_nines_vs_tens():
    W, H = 1020, 560
    P = [text(W / 2, 34, "547 − 218 двома доповненнями: куди подіти зайву одиницю",
              size=19, bold=True),
         text(W / 2, 57, "обидва шляхи дають 329 — різниця лише в тому, що робити з переносом, який виліз за розрядну сітку",
              size=12.5, color=MUTED, italic=True)]

    pw = 448
    gap = 40
    x0 = (W - 2 * pw - gap) / 2

    # ── ліва панель: доповнення до дев'ятки ──
    px = x0
    P.append(rect(px, 92, pw, 388, fill="#ffffff", stroke=LINE, sw=1.8, rx=10))
    P.append(text(px + pw / 2, 119, "Доповнення до дев'ятки", size=16, bold=True, color=NEG))
    P.append(text(px + pw / 2, 139, "999 − 218 = 781   (кожна цифра — до 9, без позик)",
                  size=11.5, color=MUTED, italic=True))

    lx = px + 118
    P.append(mono(lx, 184, "   547", size=20))
    P.append(mono(lx, 214, " + 781", size=20))
    P.append(line(px + 46, 228, px + 236, 228, color=INK, sw=1.6))
    P.append(mono(lx, 256, "  1328", size=20))
    P.append(text(px + 262, 258, "перенос виліз", size=12, color=POS, anchor="start", bold=True))
    P.append(arrow(px + 258, 252, px + 128, 248, color=POS, sw=1.6))

    P.append(mono(lx, 300, "   328", size=20))
    P.append(mono(lx, 328, " +   1", size=20, color=POS))
    P.append(line(px + 46, 342, px + 236, 342, color=INK, sw=1.6))
    P.append(mono(lx, 370, "   329", size=20, color=FIELD))
    P.append(text(px + 262, 330, "і повертається", size=12, color=POS, anchor="start", bold=True))
    P.append(text(px + 262, 348, "у молодший розряд", size=12, color=POS, anchor="start", bold=True))

    P.append(fitbox(px + 24, 392, pw - 48, 72,
                    "Кінцевий перенос: одиницю не викидають,\nа доливають назад у молодший розряд —\nце ще одне повне додавання.",
                    size=12.5, fill=WRNF, stroke=LINE))

    # ── права панель: доповнення до десятки ──
    px = x0 + pw + gap
    P.append(rect(px, 92, pw, 388, fill="#ffffff", stroke=LINE, sw=1.8, rx=10))
    P.append(text(px + pw / 2, 119, "Доповнення до десятки", size=16, bold=True, color=FIELD))
    P.append(text(px + pw / 2, 139, "1000 − 218 = 782   (та сама дев'ятка, вже з +1)",
                  size=11.5, color=MUTED, italic=True))

    lx = px + 118
    P.append(mono(lx, 184, "   547", size=20))
    P.append(mono(lx, 214, " + 782", size=20))
    P.append(line(px + 46, 228, px + 236, 228, color=INK, sw=1.6))
    P.append(mono(lx, 256, "  1329", size=20))
    P.append(text(px + 262, 258, "перенос", size=12, color=MUTED, anchor="start", bold=True))
    P.append(text(px + 262, 276, "просто зникає", size=12, color=MUTED, anchor="start", bold=True))
    P.append(arrow(px + 258, 252, px + 128, 248, color=MUTED, sw=1.6))

    P.append(mono(lx, 328, "   329", size=20, color=FIELD))
    P.append(text(px + 262, 330, "відповідь", size=12, color=FIELD, anchor="start", bold=True))

    P.append(fitbox(px + 24, 392, pw - 48, 72,
                    "Перенос за розрядну сітку нікого не обходить:\nлічильник і так рахує за модулем 1000.\nДругого додавання немає.",
                    size=12.5, fill=GRNF, stroke=LINE))

    P.append(text(W / 2, 512, "Саме ця різниця й вирішила суперечку в двійкових машинах:",
                  size=13.5, bold=True))
    P.append(text(W / 2, 534, "обернений код успадкував кінцевий перенос, а доповняльний — викидає перенос і економить цілий прохід суматора",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "nines-vs-tens.svg"), W, H, *P)


# ── 3. Три способи записати знак на тетраді: де скільки нулів ────────────────
def fig_three_codes():
    W, H = 880, 838
    P = [text(W / 2, 34, "Три суперники на чотирьох бітах: скільки в кожного нулів",
              size=19, bold=True),
         text(W / 2, 57, "усі 16 комбінацій і що вони означають у кожному записі",
              size=12.5, color=MUTED, italic=True)]

    cols = ["біти", "знак-величина", "обернений код", "доповняльний код"]
    cwid = [140, 220, 220, 220]
    x0 = (W - sum(cwid)) / 2
    y0 = 88
    rh = 36

    xs = []
    acc = x0
    for w in cwid:
        xs.append(acc)
        acc += w

    # шапка
    for i, c in enumerate(cols):
        P.append(rect(xs[i], y0, cwid[i], 42, fill=BLKF, stroke=LINE, sw=1.4, rx=0))
        P.append(text(xs[i] + cwid[i] / 2, y0 + 27, c, size=13.5, bold=True))

    def sm(v):
        s = -1 if v & 8 else 1
        m = v & 7
        return ("−0" if (s < 0 and m == 0) else "%+d" % (s * m))

    def oc(v):
        return ("−0" if v == 15 else "%+d" % (v if v < 8 else -(15 - v)))

    def tc(v):
        return "%+d" % (v if v < 8 else v - 16)

    for v in range(16):
        y = y0 + 42 + rh * v
        bits = format(v, "04b")
        neg = bool(v & 8)
        base = "#ffffff" if not neg else "#fbfcfe"
        P.append(rect(xs[0], y, cwid[0], rh, fill=base, stroke=LINE, sw=1.1, rx=0))
        P.append(mono(xs[0] + cwid[0] / 2, y + 24, bits, size=16, color=INK))

        for i, fn in enumerate((sm, oc, tc), start=1):
            s = fn(v)
            zero = (s == "−0")
            lone = (i == 3 and v == 8)
            fill = REDF if zero else (GRNF if (s == "+0") else (WRNF if lone else base))
            col = POS if zero else (FIELD if s == "+0" else INK)
            P.append(rect(xs[i], y, cwid[i], rh, fill=fill, stroke=LINE, sw=1.1, rx=0))
            P.append(mono(xs[i] + cwid[i] / 2, y + 24, s, size=16, color=col,
                          bold=zero or lone or s == "+0"))

    yb = y0 + 42 + rh * 16 + 22
    P.append(rect(x0, yb, sum(cwid), 78, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    P.append(text(W / 2, yb + 25,
                  "Червоне — другий, зайвий нуль: у знак-величині це 1000, в оберненому коді — 1111.",
                  size=12.5, color=POS))
    P.append(text(W / 2, yb + 47,
                  "Доповняльний код має рівно один нуль — ціною самотнього −8, у якого немає додатної пари.",
                  size=12.5, color=INK))
    P.append(text(W / 2, yb + 69,
                  "Обидва суперники змушені перевіряти на «мінус нуль» усюди, де важлива рівність.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-codes.svg"), W, H, *P)


# ── 4. Драбина тотожностей і два місця розрізу (вставка math-overflow-detection) ──
BLUF = "#eaf0fd"          # холодна заливка під беззнаковий закон


def fig_telescope():
    W, H = 1000, 660
    P = []

    BX, BW, BH = 60, 410, 40          # рамки розрядів
    CX = BX + BW / 2                  # вісь переносів
    LX = BX + BW + 20                 # підписи переносів (anchor=start)

    rows = [
        (80, "розряд 0:    a₀ + b₀ + c₀ = s₀ + 2·c₁"),
        (150, "розряд 1:    a₁ + b₁ + c₁ = s₁ + 2·c₂"),
        (250, "розряд n−2:  aₙ₋₂ + bₙ₋₂ + cₙ₋₂ = sₙ₋₂ + 2·cₙ₋₁"),
        (330, "розряд n−1:  aₙ₋₁ + bₙ₋₁ + cₙ₋₁ = sₙ₋₁ + 2·cₙ"),
    ]
    for y, s in rows:
        P.append(fitbox(BX, y, BW, BH, s, size=13, fill=BLKF))

    # вхідний перенос c₀ — без пари
    P.append(arrow(CX, 56, CX, 80, color=FIELD, sw=2.2))
    P.append(text(LX, 70, "c₀ · 2⁰ — без пари", size=12, color=FIELD,
                  anchor="start", bold=True))

    # внутрішні переноси — кожен двічі, гасне
    P.append(arrow(CX, 120, CX, 150))
    P.append(text(LX, 140, "c₁ · 2¹ — двічі, гасне", size=12,
                  color=MUTED, anchor="start"))

    P.append(text(CX, 228, "⋮", size=22, color=MUTED))
    P.append(text(LX, 224, "⋮", size=14, color=MUTED, anchor="start"))

    P.append(arrow(CX, 290, CX, 330, color=POS, sw=2.2))
    P.append(text(LX, 314, "cₙ₋₁ · 2ⁿ⁻¹ — ключовий", size=12,
                  color=POS, anchor="start", bold=True))

    # вихідний перенос cₙ — без пари
    P.append(arrow(CX, 370, CX, 406, color=FIELD, sw=2.2))
    P.append(text(LX, 394, "cₙ · 2ⁿ — без пари", size=12, color=FIELD,
                  anchor="start", bold=True))

    def bracket(x, y1, y2, color):
        return [line(x, y1, x, y2, color=color, sw=2.4),
                line(x - 7, y1, x, y1, color=color, sw=2.4),
                line(x - 7, y2, x, y2, color=color, sw=2.4)]

    XA, XB = 830, 890
    P += bracket(XA, 80, 370, NEG)                 # уся драбина 0…n−1
    P.append(circle(XA, 396, 12, fill=BLUF, stroke=NEG, sw=2))
    P.append(text(XA, 401, "А", size=13, color=NEG, bold=True))

    P += bracket(XB, 80, 290, POS)                 # драбина 0…n−2
    P.append(circle(XB, 316, 12, fill=REDF, stroke=POS, sw=2))
    P.append(text(XB, 321, "Б", size=13, color=POS, bold=True))

    P.append(fitbox(40, 450, 450, 170,
                    "А · склали ВСІ розряди (0 … n−1)\n"
                    "\n"
                    "Кожен внутрішній перенос стоїть двічі:\n"
                    "праворуч у рядку i та ліворуч у рядку i+1,\n"
                    "з тією самою вагою → скорочується.\n"
                    "Без пари лишились тільки c₀ і cₙ:\n"
                    "\n"
                    "A + B + c₀ = S + 2ⁿ · cₙ\n"
                    "\n"
                    "БЕЗЗНАКОВИЙ ЗАКОН",
                    size=13, fill=BLUF, stroke=NEG))

    P.append(fitbox(510, 450, 450, 170,
                    "Б · зупинили на розряд раніше (0 … n−2)\n"
                    "\n"
                    "Рядка n−1 у сумі немає — і cₙ₋₁ втрачає пару,\n"
                    "лишаючись у підсумку. Старший розряд додаємо\n"
                    "окремо, з вагою −2ⁿ⁻¹ замість +2ⁿ⁻¹:\n"
                    "\n"
                    "a + b + c₀ = s + 2ⁿ · (cₙ₋₁ − cₙ)\n"
                    "\n"
                    "ЗНАКОВИЙ ЗАКОН",
                    size=13, fill=REDF, stroke=POS))

    render(os.path.join(OUT, "math-telescope.svg"), W, H, *P,
           title="Одна драбина тотожностей — два місця розрізу")


# ── 5. Куди лягає те, що не влізло (вставка math-overflow-detection) ─────────
def fig_two_folds():
    W, H = 1000, 700
    P = []
    X0, X1 = 90, 890
    SPAN = X1 - X0

    # ── Панель А: знакове, обидва доданки ≥ 0 ──
    P.append(text(W / 2, 62, "Знакове: обидва доданки додатні (0 ≤ a, b ≤ +127)",
                  size=15, bold=True))

    sA = SPAN / 254.0                      # справжня сума 0 … +254
    xa = lambda v: X0 + v * sA
    yb, yax = 92, 122

    P.append(rect(xa(0), yb, xa(127) - xa(0), yax - yb, fill=GRNF,
                  stroke=FIELD, sw=1.8))
    P.append(text((xa(0) + xa(127)) / 2, 112, "0 … +127 — влізло", size=12,
                  color=FIELD, bold=True))
    P.append(rect(xa(128), yb, xa(254) - xa(128), yax - yb, fill=REDF,
                  stroke=POS, sw=1.8))
    P.append(text((xa(128) + xa(254)) / 2, 112, "+128 … +254 — вискочило",
                  size=12, color=POS, bold=True))

    P.append(line(X0, yax, X1, yax, sw=1.8))
    P.append(text(X0, 141, "0", size=11, color=MUTED))
    P.append(text(xa(127.5), 141, "+127 ┊ +128", size=11, color=MUTED))
    P.append(text(X1, 141, "+254", size=11, color=MUTED))
    P.append(text(X1 + 4, 108, "справжня сума", size=11, color=MUTED,
                  anchor="start"))

    sB = SPAN / 255.0                      # у слові: −128 … +127
    xb = lambda v: X0 + (v + 128) * sB
    ybar, ybarb = 252, 282

    P.append(arrow(xa(64), 152, xb(64), 246, color=FIELD, sw=2))
    P.append(arrow(xa(191), 152, xb(-65), 246, color=POS, sw=2))
    P.append(text(250, 186, "як є", size=12, color=FIELD, bold=True))
    P.append(text(742, 186, "− 2⁸", size=12, color=POS, bold=True))

    P.append(line(X0, ybar, X1, ybar, sw=1.8))
    P.append(rect(xb(-128), ybar, xb(-2) - xb(-128), ybarb - ybar,
                  fill=REDF, stroke=POS, sw=1.8))
    P.append(text((xb(-128) + xb(-2)) / 2, 272,
                  "образ: −128 … −2   (знаковий біт 1)", size=12,
                  color=POS, bold=True))
    P.append(rect(xb(0), ybar, xb(127) - xb(0), ybarb - ybar,
                  fill=GRNF, stroke=FIELD, sw=1.8))
    P.append(text((xb(0) + xb(127)) / 2, 272,
                  "образ: 0 … +127   (знаковий біт 0)", size=12,
                  color=FIELD, bold=True))
    P.append(text(X1 + 4, 268, "у слові", size=11, color=MUTED, anchor="start"))

    P.append(fitbox(40, 300, 920, 46,
                    "Образи НЕ перетинаються — їх розділяє рівно знаковий біт. "
                    "Тому «+ і + дали −» означає переповнення без винятків.",
                    size=13, fill=GRNF, stroke=FIELD))

    # ── Панель Б: беззнакове ──
    P.append(text(W / 2, 412, "Беззнакове: будь-які два доданки (0 ≤ A, B ≤ 255)",
                  size=15, bold=True))

    sC = SPAN / 510.0                      # справжня сума 0 … 510
    xc = lambda v: X0 + v * sC
    yb2, yax2 = 442, 472

    P.append(rect(xc(0), yb2, xc(255) - xc(0), yax2 - yb2, fill=GRNF,
                  stroke=FIELD, sw=1.8))
    P.append(text((xc(0) + xc(255)) / 2, 462, "0 … 255 — влізло", size=12,
                  color=FIELD, bold=True))
    P.append(rect(xc(256), yb2, xc(510) - xc(256), yax2 - yb2, fill=REDF,
                  stroke=POS, sw=1.8))
    P.append(text((xc(256) + xc(510)) / 2, 462, "256 … 510 — вискочило",
                  size=12, color=POS, bold=True))

    P.append(line(X0, yax2, X1, yax2, sw=1.8))
    P.append(text(X0, 491, "0", size=11, color=MUTED))
    P.append(text(xc(255.5), 491, "255 ┊ 256", size=11, color=MUTED))
    P.append(text(X1, 491, "510", size=11, color=MUTED))
    P.append(text(X1 + 4, 458, "справжня сума", size=11, color=MUTED,
                  anchor="start"))

    # у слові: 0 … 255, ТОЙ САМИЙ масштаб, що й на верхній осі панелі
    ybar2, ybar2b = 602, 632
    P.append(arrow(xc(128), 502, xc(100), 596, color=FIELD, sw=2))
    P.append(arrow(xc(383), 502, xc(160), 596, color=POS, sw=2))
    P.append(text(150, 552, "як є", size=12, color=FIELD, bold=True))
    P.append(text(620, 540, "− 2⁸", size=12, color=POS, bold=True))

    P.append(line(X0, ybar2, xc(255), ybar2, sw=1.8))
    P.append(rect(xc(0), ybar2, xc(255) - xc(0), ybar2b - ybar2,
                  fill="#f6eef8", stroke="#7d3c98", sw=1.8))
    P.append(text(xc(127.5), 622, "той самий відрізок 0 … 255", size=12,
                  color="#7d3c98", bold=True))
    P.append(text(xc(255) + 10, 622, "у слові", size=11, color=MUTED,
                  anchor="start"))

    P.append(fitbox(40, 650, 920, 46,
                    "Образи ЗБІГАЮТЬСЯ — 44 однаково законний результат і для 20+24, "
                    "і для 200+100. Жоден біт слова не виказує переповнення: потрібна сама цифра cₙ.",
                    size=13, fill=REDF, stroke=POS))

    render(os.path.join(OUT, "math-two-folds.svg"), W, H, *P,
           title="Куди лягає те, що не влізло")


if __name__ == "__main__":
    fig_pascaline()
    fig_nines_vs_tens()
    fig_three_codes()
    fig_telescope()
    fig_two_folds()
    print("ok:", os.listdir(OUT))
