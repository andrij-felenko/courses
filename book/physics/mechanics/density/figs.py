# -*- coding: utf-8 -*-
"""Фігури до теми «Густина».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WATER = "#bfe0f2"
WATERD = "#7cc0e0"
GAS = "#dfe4ea"
LIGHT = "#9ec9e8"      # легкі атоми
LIGHTD = "#5b9bd0"
HEAVY = "#d4b24a"      # важкі атоми (метал)
HEAVYD = "#a8842a"
STEEL = "#c4c9d2"
STEELD = "#8b9099"
CORK = "#dcb579"
WOOD = "#c69a5c"
ICE = "#e6f3fb"
ICED = "#a9d3ea"
GREEN = FIELD


# ── Фігура 1: густина = маса атомів × щільність упаковки ───────────────────────
def fig_packing():
    W, H = 1040, 560
    F = []

    # три однакові за розміром скриньки
    bx = 236                       # ширина/висота скриньки
    top = 96
    centers = [190, 520, 850]
    names = ["розріджений газ", "щільна легка речовина", "щільний важкий метал"]
    subs = ["легкі атоми, далеко", "легкі атоми, впритул", "важкі атоми, впритул"]
    rhos = ["ρ мала", "ρ середня", "ρ велика"]
    rhocols = [MUTED, LIGHTD, HEAVYD]

    def fill_grid(cx, r, cols, cold, n):
        """Регулярна щільна сітка кружечків радіуса r у скриньці."""
        g = []
        x0 = cx - bx / 2 + r + 6
        y0 = top + r + 6
        step = 2 * r + 6
        cxr = int((bx - 12) // step)
        cyr = int((bx - 12) // step)
        for iy in range(cyr):
            for ix in range(cxr):
                g.append(circle(x0 + ix * step, y0 + iy * step, r,
                                fill=cols, stroke=cold, sw=1.4))
        return "".join(g)

    def fill_gas(cx):
        """Кілька дрібних атомів, розкиданих далеко один від одного."""
        g = []
        pts = [(0.22, 0.20), (0.68, 0.14), (0.44, 0.46),
               (0.16, 0.72), (0.80, 0.58), (0.58, 0.82)]
        for fx, fy in pts:
            x = cx - bx / 2 + 14 + fx * (bx - 28)
            y = top + 14 + fy * (bx - 28)
            g.append(circle(x, y, 9, fill=LIGHT, stroke=LIGHTD, sw=1.4))
        return "".join(g)

    for i, cx in enumerate(centers):
        # скринька
        F.append(rect(cx - bx / 2, top, bx, bx, fill=BG, stroke=INK, sw=1.8, rx=6))
        if i == 0:
            F.append(fill_gas(cx))
        elif i == 1:
            F.append(fill_grid(cx, 11, LIGHT, LIGHTD, 0))
        else:
            F.append(fill_grid(cx, 15, HEAVY, HEAVYD, 0))
        # той самий об'єм — підпис під скринькою
        F.append(text(cx, top + bx + 22, "той самий об'єм V", size=12, color=MUTED))
        # назва
        F.append(text(cx, top + bx + 48, names[i], size=13.5, bold=True))
        F.append(text(cx, top + bx + 68, subs[i], size=11.5, color=MUTED))
        # ρ-мітка
        tb, _, _ = textbox(cx, top + bx + 100, rhos[i], size=13.5, bold=True, pad=8,
                           fill="#ffffff", stroke=rhocols[i], color=rhocols[i], min_w=110)
        F.append(tb)

    # знаки «менше» між скриньками
    F.append(text(355, top + bx / 2 + 6, "<", size=30, color=MUTED, bold=True))
    F.append(text(685, top + bx / 2 + 6, "<", size=30, color=MUTED, bold=True))

    render(os.path.join(IMG, "packing.svg"), W, H, *F,
           title="Густина = маса атомів × щільність їх упаковки")


# ── Фігура 2: шкала густин (логарифмічна) ──────────────────────────────────────
def fig_ladder():
    W, H = 1040, 600
    F = []

    # (назва, ρ кг/м³, колір смуги)
    rows = [
        ("повітря",   1.2,    GAS),
        ("суха деревина", 500, WOOD),
        ("крига",     917,    ICE),
        ("ВОДА",      1000,   WATER),
        ("алюміній",  2700,   STEEL),
        ("залізо",    7870,   STEELD),
        ("свинець",   11340,  "#8e7fa6"),
        ("золото",    19300,  HEAVY),
        ("осмій",     22590,  HEAVYD),
    ]

    x_lab = 30                     # ліва межа підписів назв
    x0 = 250                       # початок смуг
    x1 = 950                       # права межа поля смуг
    LOGMAX = 4.5                   # шкала log10 від 0 до 4.5
    span = x1 - x0

    def xof(rho):
        return x0 + max(0.0, math.log10(rho)) / LOGMAX * span

    y0 = 108
    dy = 50
    bar_h = 30

    # вертикальні лінії-декади з підписами (10, 100, 1000, 10000)
    for e in range(0, 5):
        xx = x0 + e / LOGMAX * span
        F.append(line(xx, y0 - 24, xx, y0 + len(rows) * dy - 18, color="#e3e7ec", sw=1.2))
        lab = "10" + "⁰¹²³⁴"[e] + " кг/м³" if e else "1 кг/м³"
        F.append(text(xx, y0 - 32, lab, size=11, color=MUTED))

    for i, (name, rho, col) in enumerate(rows):
        yc = y0 + i * dy
        highlight = (name == "ВОДА")
        # назва ліворуч
        F.append(text(x_lab, yc + 5, name, size=13, bold=highlight,
                      color=(NEG if highlight else INK), anchor="start"))
        # смуга
        bw = xof(rho) - x0
        F.append(rect(x0, yc - bar_h / 2, max(bw, 3), bar_h, fill=col,
                      stroke=(NEG if highlight else STEELD), sw=(2.2 if highlight else 1.2), rx=4))
        # значення в кінці смуги
        val = ("%d" % rho) if rho >= 10 else ("%.1f" % rho)
        F.append(text(xof(rho) + 12, yc + 5, val + " кг/м³", size=12,
                      bold=highlight, color=(NEG if highlight else INK), anchor="start"))

    # позначка опорної одиниці «вода»
    yw = y0 + 3 * dy
    F.append(text(x0 + 4, yw - bar_h / 2 - 8, "опорна одиниця", size=10.5,
                  color=NEG, bold=True, anchor="start"))

    F.append(fitbox(90, 548, 860, 40,
                    "Логарифмічна шкала: кожна поділка — у десять разів густіше. "
                    "Від повітря до осмію — майже п'ять порядків.",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "ladder.svg"), W, H, *F,
           title="Шкала густин: від повітря до найважчих металів")


# ── Фігура 3: плавучість за густиною — частка занурення = ρ/ρ_води ─────────────
def fig_floating():
    W, H = 1040, 560
    F = []

    tx0, tx1 = 70, 970
    wl = 168                       # рівень води (y)
    bot = 462                      # дно бака

    # бак з водою
    F.append(rect(tx0, wl, tx1 - tx0, bot - wl, fill=WATER, stroke=WATERD, sw=1.6, rx=0))
    F.append(rect(tx0, bot, tx1 - tx0, 10, fill=STEELD, stroke="none", rx=0))
    # лінія рівня води
    F.append(line(tx0, wl, tx1, wl, color=WATERD, sw=2.4, dash="8 5"))
    F.append(text(tx1 + 4, wl + 4, "рівень", size=11, color=WATERD, bold=True, anchor="start"))
    F.append(text(tx1 + 4, wl + 18, "води", size=11, color=WATERD, bold=True, anchor="start"))

    bh = 104                       # висота бруска
    bw = 92                        # ширина бруска

    # (центр x, назва, ρ, колір, темний контур, «тоне»?)
    objs = [
        (185, "корок",   240,  CORK, "#b98a3e", False),
        (400, "деревина", 500, WOOD, "#9c7638", False),
        (620, "крига",   917,  ICE,  ICED, False),
        (835, "залізо",  7870, STEEL, STEELD, True),
    ]

    for cx, name, rho, col, cold, sink in objs:
        if sink:
            # тоне на дно
            ytop = bot - bh
            F.append(rect(cx - bw / 2, ytop, bw, bh, fill=col, stroke=cold, sw=1.8, rx=6))
            F.append(text(cx, ytop - 30, name, size=13.5, bold=True))
            F.append(text(cx, ytop - 12, "ρ = %d" % rho, size=12, color=INK))
            tb, _, _ = textbox(cx, (ytop + bot) / 2, "тоне", size=13, bold=True, pad=7,
                               fill="#fdecea", stroke=POS, color=POS, min_w=78)
            F.append(tb)
            # стрілка вниз
            F.append(arrow(cx, wl + 22, cx, wl + 60, color=POS, sw=2.6))
        else:
            frac = rho / 1000.0
            sub = frac * bh                    # занурена частина
            ytop = wl - (bh - sub)
            # надводна частина (над лінією)
            F.append(rect(cx - bw / 2, ytop, bw, bh, fill=col, stroke=cold, sw=1.8, rx=6))
            # перекреслимо лінію води поверх бруска, щоб було видно межу занурення
            F.append(line(cx - bw / 2, wl, cx + bw / 2, wl, color=WATERD, sw=2.0, dash="5 4"))
            # назва над бруском
            F.append(text(cx, ytop - 26, name, size=13.5, bold=True))
            F.append(text(cx, ytop - 8, "ρ = %d" % rho, size=12, color=INK))
            # відсоток занурення
            pct = int(round(frac * 100))
            tb, _, _ = textbox(cx, wl + sub / 2 + 4, "занурено\n%d %%" % pct, size=12, bold=True,
                               pad=6, fill="#eef7ff", stroke=NEG, color=NEG, min_w=88)
            F.append(tb)

    # формула-підказка в лівому верхньому кутку над водою
    fb, _, _ = textbox(250, 66,
                       "частка занурена = ρ_тіла / ρ_води", size=13.5, bold=True, pad=10,
                       fill="#eafaf0", stroke=GREEN, color=INK)
    F.append(fb)

    F.append(fitbox(90, 494, 860, 46,
                    "Плаває те, що легше за воду, — і тим вище, чим легше. Крига (917 проти 1000) "
                    "виступає лише на десяту частину: звідси «верхівка айсберга».",
                    size=13, bold=True, fill="#eef4fb", stroke=NEG, pad=10))

    render(os.path.join(IMG, "floating.svg"), W, H, *F,
           title="Плаває чи тоне — вирішує густина")


# ── Фігура 4 (вставка math): комірка як цеглинка густини ────────────────────────
def fig_cell():
    W, H = 1060, 600
    F = []

    # ── ліворуч: ОЦК-комірка в косій проєкції ──
    s = 150
    fx, fy = 150, 250
    ox, oy = 92, -74
    FTL = (fx, fy);         FTR = (fx + s, fy)
    FBL = (fx, fy + s);     FBR = (fx + s, fy + s)
    BTL = (fx + ox, fy + oy);         BTR = (fx + s + ox, fy + oy)
    BBL = (fx + ox, fy + s + oy);     BBR = (fx + s + ox, fy + s + oy)
    center = (fx + (s + ox) / 2, fy + (s + oy) / 2)
    EB = "#b8bec7"

    # задні ребра + з'єднувачі (світліші, «за» коміркою)
    for p, q in [(BTL, BTR), (BTR, BBR), (BBR, BBL), (BBL, BTL),
                 (FTL, BTL), (FTR, BTR), (FBR, BBR), (FBL, BBL)]:
        F.append(line(p[0], p[1], q[0], q[1], color=EB, sw=1.6))
    # діагональ тіла — уздовж неї атоми торкаються (4r = a√3)
    F.append(line(FBL[0], FBL[1], BTR[0], BTR[1], color=HEAVYD, sw=1.5, dash="6 5"))
    # передні ребра (темні)
    for p, q in [(FTL, FTR), (FTR, FBR), (FBR, FBL), (FBL, FTL)]:
        F.append(line(p[0], p[1], q[0], q[1], color=INK, sw=2.0))
    # атоми: 8 кутів + 1 центральний
    r = 13
    for p in [FTL, FTR, FBL, FBR, BTL, BTR, BBL, BBR, center]:
        F.append(circle(p[0], p[1], r, fill=HEAVY, stroke=HEAVYD, sw=1.6))

    # розмір a вздовж переднього нижнього ребра
    yd = fy + s + 30
    F.append(line(fx, yd, fx + s, yd, color=MUTED, sw=1.4))
    F.append(line(fx, yd - 6, fx, yd + 6, color=MUTED, sw=1.4))
    F.append(line(fx + s, yd - 6, fx + s, yd + 6, color=MUTED, sw=1.4))
    F.append(text(fx + s / 2, yd + 22, "a = 2.866 Å (стала ґратки)", size=12.5))
    F.append(text((fx + fx + s + ox) / 2, yd + 62,
                  "n = 2 атоми в комірці  (8 × ⅛ кутових + 1 центральний)",
                  size=12.5, color=MUTED))

    # ── праворуч: формула з розшифровкою ──
    F.append(text(770, 210, "ρ = n·M / (Nₐ·a³)", size=25, bold=True))
    legend = ("n — атомів у комірці (ОЦК: 2)\n"
              "M — молярна маса, кг/моль\n"
              "Nₐ — стала Авогадро, 6.022×10²³ /моль\n"
              "a³ — об'єм комірки")
    tb, _, _ = textbox(770, 320, legend, size=13, pad=12, fill="#ffffff",
                       stroke=MUTED, color=INK)
    F.append(tb)

    F.append(fitbox(90, 512, 880, 62,
                    "Кристал — та сама комірка, повторена мільярди разів; копіювання\n"
                    "не міняє відношення маси до об'єму. Тож густина тіла = густина однієї комірки.",
                    size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=10))

    render(os.path.join(IMG, "cell.svg"), W, H, *F,
           title="Комірка як цеглинка густини")


# ── Фігура 5 (вставка math): коефіцієнт упаковки ОЦК/ГЦК/ГЩП ─────────────────────
def fig_packfrac():
    W, H = 1060, 430
    F = []

    rows = [
        ("проста кубічна (ПК)",      0.52, "напр. полоній",                  GAS,   "#9aa1ab"),
        ("об'ємноцентрована (ОЦК)",  0.68, "залізо, вольфрам, хром",         STEEL, STEELD),
        ("щільна: ГЦК і ГЩП",        0.74, "осмій, іридій, золото, алюміній", HEAVY, HEAVYD),
    ]
    xlab = 30
    x0, x1 = 470, 980
    span = x1 - x0
    y0, dy, bar_h = 118, 94, 46

    for i, (name, f, metals, col, cold) in enumerate(rows):
        yc = y0 + i * dy
        F.append(text(xlab, yc - 2, name, size=14, bold=True, anchor="start"))
        F.append(text(xlab, yc + 18, metals, size=11.5, color=MUTED, anchor="start"))
        # повний об'єм комірки (рамка 0..1) і заповнена атомами частка
        F.append(rect(x0, yc - bar_h / 2, span, bar_h, fill=BG, stroke=MUTED, sw=1.3))
        F.append(rect(x0, yc - bar_h / 2, span * f, bar_h, fill=col, stroke=cold, sw=1.4))
        F.append(text(x0 + span * f + 12, yc + 5, "%d %%" % round(f * 100),
                      size=14, bold=True, anchor="start", color=cold))

    ybot = y0 + 2 * dy + bar_h / 2 + 22
    F.append(text(x0, ybot, "0", size=11, color=MUTED))
    F.append(text(x1, ybot, "увесь об'єм комірки", size=11, color=MUTED, anchor="end"))

    F.append(fitbox(90, y0 + 2 * dy + 46, 880, 64,
                    "Частка об'єму комірки, зайнята атомами. Перехід від ОЦК (0.68)\n"
                    "до щільної укладки (0.74) додає ~9 % густини за тих самих атомів.",
                    size=13.5, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "packfrac.svg"), W, H, *F,
           title="Коефіцієнт упаковки: скільки комірки заповнено атомами")


# ── Вставка «Корона Гієрона» ───────────────────────────────────────────────────
GOLD, GOLDD = HEAVY, HEAVYD             # золото
SILVER, SILVERD = "#c4c9d2", "#8b9099"  # срібло
CROWN, CROWND = "#cbb26e", "#9c8038"    # сплав корони


# ── Фігура: метод переливання за Вітрувієм ─────────────────────────────────────
def fig_crown_overflow():
    W, H = 1040, 560
    F = []

    cols = [200, 520, 840]
    names = ["срібло", "золото", "корона"]
    lumpR = [42, 28, 31]
    fills = [SILVER, GOLD, CROWN]
    stroke = [SILVERD, GOLDD, CROWND]
    vols = [95.2, 51.8, 56.2]

    top = 92
    bw, bh = 150, 168
    for i, cx in enumerate(cols):
        F.append(rect(cx - bw / 2, top, bw, bh, fill="#f7fafc", stroke="#9fb2c2", sw=2, rx=8))
        F.append(rect(cx - bw / 2 + 5, top + 12, bw - 10, bh - 17, fill=WATER, stroke="none", rx=6))
        F.append(line(cx - bw / 2 + 5, top + 12, cx + bw / 2 - 5, top + 12, color=WATERD, sw=2))
        F.append(circle(cx, top + 92, lumpR[i], fill=fills[i], stroke=stroke[i], sw=2))
        F.append(text(cx, top - 14, names[i], size=15, bold=True))
    F.append(text(520, top + bh + 30, "однакова вага — різний об'єм тіла", size=13,
                  color=MUTED, italic=True))

    # нижні смуги: скільки води вилилося через край
    F.append(text(150, 352, "вилито води через край, см³:", size=13, bold=True, anchor="start"))
    x0 = 250
    scale = 620 / max(vols)
    ybar, dy, barh = 384, 50, 30
    for i in range(3):
        yc = ybar + i * dy
        L = vols[i] * scale
        F.append(text(150, yc + 5, names[i], size=13, bold=True, anchor="start"))
        F.append(rect(x0, yc - barh / 2, max(L, 3), barh, fill=fills[i], stroke=stroke[i], sw=1.6, rx=4))
        F.append(text(x0 + L + 12, yc + 5, "%.0f" % vols[i], size=13, bold=True, anchor="start"))

    render(os.path.join(IMG, "crown-overflow.svg"), W, H, *F,
           title="Метод переливання: однакова вага, різний витіснений об'єм")


# ── Фігура: гідростатичні терези ───────────────────────────────────────────────
def fig_crown_balance():
    W, H = 1040, 560
    F = []

    F.append(text(280, 74, "у повітрі: рівновага", size=14, bold=True))
    F.append(text(770, 74, "у воді: корона легшає — плече вгору", size=14, bold=True))
    F.append(arrow(500, 175, 560, 175, color=MUTED, sw=2.4))
    F.append(text(530, 160, "занурюємо", size=11, color=MUTED))

    def post(xf, yb):
        return [line(xf, yb, xf, yb + 92, color=INK, sw=3),
                line(xf - 32, yb + 92, xf + 32, yb + 92, color=INK, sw=4),
                '<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>' %
                (xf, yb - 2, xf - 13, yb + 16, xf + 13, yb + 16, MUTED)]

    def pan_right(rx, ry, ch):
        return [line(rx, ry, rx, ry + ch, color=MUTED, sw=1.5),
                line(rx - 24, ry + ch, rx + 24, ry + ch, color=INK, sw=2.4),
                rect(rx - 14, ry + ch - 24, 28, 22, fill=SILVER, stroke=SILVERD, sw=1.6, rx=3),
                text(rx, ry + ch + 22, "противага", size=12, bold=True)]

    ch = 44
    # стан А — у повітрі, коромисло рівне
    xf, yb, half = 280, 150, 110
    F += post(xf, yb)
    lx, rx = xf - half, xf + half
    F.append(line(lx, yb, rx, yb, color=INK, sw=5))
    F.append(line(lx, yb, lx, yb + ch, color=MUTED, sw=1.5))
    F.append(line(lx - 24, yb + ch, lx + 24, yb + ch, color=INK, sw=2.4))
    F.append(circle(lx, yb + ch - 11, 12, fill=GOLD, stroke=GOLDD, sw=2))
    F.append(text(lx, yb + ch + 22, "корона", size=12, bold=True))
    F += pan_right(rx, yb, ch)

    # стан Б — корона у воді, коромисло хитнулось (лівий бік угору)
    xf, yb, half, tilt = 770, 150, 110, 22
    F += post(xf, yb)
    lx, rx = xf - half, xf + half
    ly, ry = yb - tilt, yb + tilt
    F.append(line(lx, ly, rx, ry, color=INK, sw=5))
    F += pan_right(rx, ry, ch)
    jw, jh, jtop = 78, 108, 150
    F.append(rect(lx - jw / 2, jtop, jw, jh, fill=WATER, stroke=WATERD, sw=1.8, rx=4))
    F.append(line(lx - jw / 2, jtop, lx + jw / 2, jtop, color=WATERD, sw=2))
    F.append(line(lx, ly, lx, jtop + 30, color=MUTED, sw=1.5))
    F.append(circle(lx, jtop + 44, 13, fill=GOLD, stroke=GOLDD, sw=2))
    F.append(text(lx, jtop + jh + 20, "корона у воді", size=12, bold=True))

    F.append(fitbox(120, 362, 800, 44,
                    "втрата ваги у воді = вага витісненої води = ρ_води · V   ⇒   об'єм, а з ним густина",
                    size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=10))
    tb, _, _ = textbox(520, 446, "густина корони  17.8  ≠  19.3  (чисте золото)", size=14, bold=True,
                       pad=11, fill="#eef4fb", stroke=NEG, color=INK, min_w=380)
    F.append(tb)

    render(os.path.join(IMG, "crown-balance.svg"), W, H, *F,
           title="Гідростатичні терези: об'єм читаємо вагою, не калюжею")


# ── Фігура: той самий сигнал — два показання ───────────────────────────────────
def fig_crown_precision():
    W, H = 1040, 480
    F = []
    F.append(line(514, 60, 514, 415, color="#dfe4ea", sw=1.5))

    # ── ліворуч: переливання ──
    F.append(text(255, 78, "переливання", size=15, bold=True))
    base, top_noise = 350, 150
    nh = base - top_noise
    F.append(rect(150, top_noise, 66, nh, fill="#f6d6d2", stroke=POS, sw=1.8, rx=4))
    F.append(text(183, top_noise - 12, "шум", size=12, bold=True, color=POS))
    F.append(text(183, base + 20, "меніск + крапля", size=11.5, color=MUTED))
    F.append(text(183, base + 36, "≈ 1–2 мм", size=11.5, color=MUTED))
    sh = nh * (0.14 / 1.6)
    F.append(rect(330, base - sh, 66, max(sh, 3), fill=WATER, stroke=WATERD, sw=1.8, rx=3))
    F.append(text(363, base - sh - 12, "сигнал", size=12, bold=True, color=NEG))
    F.append(text(363, base + 20, "0.14 мм", size=11.5, color=INK, bold=True))
    F.append(line(120, base, 470, base, color=INK, sw=2))
    tb, _, _ = textbox(300, 445, "сигнал тоне в шумі", size=13, bold=True, pad=8,
                       fill="#fdecea", stroke=POS, color=POS, min_w=220)
    F.append(tb)

    # ── праворуч: терези ──
    F.append(text(775, 78, "гідростатичні терези", size=15, bold=True))
    ax0, ax1, ay = 620, 950, 250
    v0, v1 = 17.0, 20.0

    def xof(v):
        return ax0 + (v - v0) / (v1 - v0) * (ax1 - ax0)

    F.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    for v in [17, 18, 19, 20]:
        F.append(line(xof(v), ay - 5, xof(v), ay + 5, color=INK, sw=1.5))
        F.append(text(xof(v), ay + 22, str(v), size=11, color=MUTED))
    F.append(text((ax0 + ax1) / 2, ay + 44, "густина, г/см³", size=11.5, color=MUTED, italic=True))
    xc, xg = xof(17.8), xof(19.3)
    F.append(rect(xc, ay - 40, xg - xc, 40, fill="#fdf3d6", stroke="none", rx=0))
    F.append(line(xc, ay - 46, xc, ay + 6, color=CROWND, sw=2.4))
    F.append(line(xg, ay - 46, xg, ay + 6, color=GOLDD, sw=2.4))
    F.append(text(xc, ay - 54, "корона 17.8", size=12, bold=True))
    F.append(text(xg, ay - 54, "золото 19.3", size=12, bold=True))
    tbx, _, _ = textbox((xc + xg) / 2, ay - 20, "8 %", size=13, bold=True, pad=6,
                        fill="#ffffff", stroke=GOLDD, color=GOLDD, min_w=54)
    F.append(tbx)
    tb2, _, _ = textbox(775, 445, "розрив 8 % — недвозначно", size=13, bold=True, pad=8,
                        fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=240)
    F.append(tb2)

    render(os.path.join(IMG, "crown-precision.svg"), W, H, *F,
           title="Один надлишок 4.3 см³ — два різні показання")


if __name__ == "__main__":
    fig_packing()
    fig_ladder()
    fig_floating()
    fig_cell()
    fig_packfrac()
    fig_crown_overflow()
    fig_crown_balance()
    fig_crown_precision()
    print("OK: 8 SVG ->", IMG)
