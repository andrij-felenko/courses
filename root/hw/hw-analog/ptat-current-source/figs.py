# -*- coding: utf-8 -*-
"""Фігури до статті «PTAT-джерело струму» (book/electronics/analog/ptat-current-source).
Три фігури:
  idea.svg     — ідея: два переходи з різною щільністю струму дають проміжок ΔU_BE,
                 що росте з температурою; резистор перетворює його на струм ∝ T
  circuit.svg  — робоча схема: дзеркало згори зрівнює струми, площі 1:N задають ΔU_BE,
                 резистор R у емітері «жирного» транзистора ставить I = ΔU_BE / R
  slope.svg    — характеристика: I_PTAT росте лінійно з T і прямує в нуль при 0 K
                 (пряма крізь початок), на відміну від звичайного струму
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def npn(cx, cy, label=None, r=22):
    """NPN-транзистор: вертикальна риска бази, колектор зверху, емітер знизу зі стрілкою.
    Повертає (svg, dict-вузлів base/coll/emit)."""
    bar_x = cx - 4
    bx_top, bx_bot = cy - 14, cy + 14
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.6),
           line(bar_x, bx_top, bar_x, bx_bot, color=INK, sw=2.6),
           line(cx - r, cy, bar_x, cy, color=INK, sw=1.6)]
    out.append(line(bar_x, cy - 7, cx + 9, cy - 18, color=INK, sw=1.6))
    out.append(line(cx + 9, cy - 18, cx + 9, cy - r - 6, color=INK, sw=1.6))
    out.append(line(bar_x, cy + 7, cx + 9, cy + 18, color=INK, sw=1.6))
    out.append(arrow(cx + 4, cy + 11, cx + 9, cy + 18, color=INK, sw=1.8))
    out.append(line(cx + 9, cy + 18, cx + 9, cy + r + 6, color=INK, sw=1.6))
    if label:
        out.append(text(cx - r - 16, cy + 4, label, size=13, color=INK, bold=True, anchor="middle"))
    nodes = {"base": (cx - r, cy), "coll": (cx + 9, cy - r - 6), "emit": (cx + 9, cy + r + 6)}
    return "".join(out), nodes


def pnp(cx, cy, label=None, r=22):
    """PNP-транзистор (дзеркало згори): емітер зверху, колектор знизу, стрілка всередину."""
    bar_x = cx - 4
    bx_top, bx_bot = cy - 14, cy + 14
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.6),
           line(bar_x, bx_top, bar_x, bx_bot, color=INK, sw=2.6),
           line(cx - r, cy, bar_x, cy, color=INK, sw=1.6)]
    # емітер зверху (стрілка всередину — до бази)
    out.append(line(bar_x, cy - 7, cx + 9, cy - 18, color=INK, sw=1.6))
    out.append(arrow(cx + 9, cy - 18, cx + 4, cy - 11, color=INK, sw=1.8))
    out.append(line(cx + 9, cy - 18, cx + 9, cy - r - 6, color=INK, sw=1.6))
    # колектор знизу
    out.append(line(bar_x, cy + 7, cx + 9, cy + 18, color=INK, sw=1.6))
    out.append(line(cx + 9, cy + 18, cx + 9, cy + r + 6, color=INK, sw=1.6))
    if label:
        out.append(text(cx - r - 16, cy + 4, label, size=13, color=INK, bold=True, anchor="middle"))
    nodes = {"base": (cx - r, cy), "emit": (cx + 9, cy - r - 6), "coll": (cx + 9, cy + r + 6)}
    return "".join(out), nodes


def rail(y, x0, x1, label=None):
    out = [line(x0, y, x1, y, color=INK, sw=2.4)]
    if label:
        out.append(text(x1 + 6, y + 4, label, size=12, color=INK, bold=True, anchor="start"))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="right", col=POS):
    """Вертикальний резистор-зигзаг між (x,y0) і (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 2)
    amp = 6
    out.append(line(x, y0, x, y0 + seg, color=INK, sw=1.6))
    yy = y0 + seg
    prev = x
    for i in range(n):
        nx = x + (amp if i % 2 == 0 else -amp)
        out.append(line(prev, yy, nx, yy + seg, color=INK, sw=1.6))
        prev = nx
        yy += seg
    out.append(line(prev, yy, x, yy + seg, color=INK, sw=1.6))
    out.append(line(x, yy + seg, x, y1, color=INK, sw=1.6))
    if label:
        lx = x - 16 if side == "left" else x + 16
        an = "end" if side == "left" else "start"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=col, bold=True, anchor=an))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — суть: різна щільність струму → проміжок ΔU_BE, що росте з T → струм
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 660, 360
    f = []

    # два «переходи» як стовпчики падіння напруги
    base_y = 250
    top_y = 70
    x1, x2 = 150, 360
    barw = 70

    # лівий — мала площа, велика щільність → більше падіння U_BE
    h1 = base_y - top_y
    f.append(rect(x1 - barw / 2, top_y, barw, h1, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(x1, top_y - 28, "малий перехід", size=12, color=INK, bold=True))
    f.append(text(x1, top_y - 12, "велика щільність j", size=11, color=MUTED))
    f.append(text(x1, base_y + 24, "U_BE1", size=13, color=POS, bold=True))
    f.append(text(x1, base_y + 42, "(вище)", size=11, color=MUTED))

    # правий — у N разів більша площа, менша щільність → менше падіння
    h2 = base_y - (top_y + 46)
    f.append(rect(x2 - barw / 2, top_y + 46, barw, h2, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(x2, top_y - 28, "у N разів більший", size=12, color=INK, bold=True))
    f.append(text(x2, top_y - 12, "мала щільність j", size=11, color=MUTED))
    f.append(text(x2, base_y + 24, "U_BE2", size=13, color=POS, bold=True))
    f.append(text(x2, base_y + 42, "(нижче)", size=11, color=MUTED))

    # стрілка-проміжок між верхами стовпчиків = ΔU_BE
    gx = (x1 + x2) / 2 + 4
    f.append(line(x1 + barw / 2, top_y, gx + 40, top_y, color=NEG, sw=1.2, dash="4 4"))
    f.append(line(x2 - barw / 2, top_y + 46, gx - 40, top_y + 46, color=NEG, sw=1.2, dash="4 4"))
    f.append(arrow(gx, top_y, gx, top_y + 46, color=NEG, sw=2.4))
    f.append(arrow(gx, top_y + 46, gx, top_y, color=NEG, sw=2.4))
    f.append(text(gx + 12, top_y + 26, "ΔU_BE", size=14, color=NEG, bold=True, anchor="start"))

    # спільна землю-лінія
    f.append(line(80, base_y, 430, base_y, color=INK, sw=2.0))
    f.append(gnd(255, base_y))

    # права частина: ΔU_BE на резистор → струм ∝ T
    body, w0, h0 = textbox(560, 150,
                           "ΔU_BE = (kT/q)·ln N\n\nросте ПРЯМО\nз температурою T",
                           size=12, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    f.append(arrow(440, 150, 560 - w0 / 2 - 6, 150, color=NEG, sw=2.4))

    body2, w2, h2b = textbox(560, 290,
                             "поклади на резистор R:\nI = ΔU_BE / R  →  ∝ T",
                             size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body2)
    f.append(arrow(560, 150 + h0 / 2 + 4, 560, 290 - h2b / 2 - 4, color=FIELD, sw=2.4))

    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. circuit.svg — робоча схема ΔU_BE-джерела (самозміщене)
# ════════════════════════════════════════════════════════════════════════════
def fig_circuit():
    W, H = 660, 440
    f = []
    top = 56
    f.append(rail(top, 110, 540, "+V"))

    # верхнє дзеркало PNP — змушує однакові струми в обох гілках
    p1x, p2x, py = 230, 430, 130
    sp1, np1 = pnp(p1x, py, label="P1", r=20)
    sp2, np2 = pnp(p2x, py, label="P2", r=20)
    f.append(sp1); f.append(sp2)
    # емітери PNP до +V
    f.append(line(np1["emit"][0], np1["emit"][1], np1["emit"][0], top, color=INK, sw=1.8))
    f.append(line(np2["emit"][0], np2["emit"][1], np2["emit"][0], top, color=INK, sw=1.8))
    # спільні бази PNP, діодне ввімкнення P1 (база=колектор P1)
    pby = py + 2
    f.append(line(np1["base"][0] - 22, pby, np1["base"][0], pby, color=FIELD, sw=2.2))
    f.append(line(np1["base"][0] - 22, pby, np1["base"][0] - 22, np1["coll"][1] + 8, color=FIELD, sw=2.2))
    f.append(line(np1["base"][0] - 22, np1["coll"][1] + 8, np1["coll"][0], np1["coll"][1] + 8, color=FIELD, sw=2.2))
    f.append(line(np1["base"][0] - 22, pby, np2["base"][0], pby, color=FIELD, sw=2.2))
    f.append(text((p1x + p2x) / 2, pby + 20, "дзеркало: I_ліво = I_право", size=12, color=FIELD, bold=True))

    # нижні NPN: ліворуч — звичайний (площа 1, x1), праворуч — у N разів більший
    n1x, n2x, ny = 230, 430, 280
    sn1, nn1 = npn(n1x, ny, label="Q1·1", r=20)
    sn2, nn2 = npn(n2x, ny, label="Q2·N", r=20)
    f.append(sn1); f.append(sn2)

    # з'єднання колекторів P→N
    f.append(line(np1["coll"][0], np1["coll"][1], nn1["coll"][0], nn1["coll"][1], color=INK, sw=1.8))
    f.append(line(np2["coll"][0], np2["coll"][1], nn2["coll"][0], nn2["coll"][1], color=INK, sw=1.8))

    # спільні бази NPN, діодне ввімкнення Q1 праворуч? — у класиці база-вузол спільний,
    # тут малюємо як «бази разом», зав'язані на колектор Q1 (петля самозміщення)
    nby = ny + 2
    f.append(line(nn1["base"][0] - 22, nby, nn1["base"][0], nby, color=POS, sw=2.2))
    f.append(line(nn1["base"][0] - 22, nby, nn1["base"][0] - 22, nn1["coll"][1], color=POS, sw=2.2))
    f.append(line(nn1["base"][0] - 22, nn1["coll"][1], nn1["coll"][0], nn1["coll"][1], color=POS, sw=2.2))
    f.append(line(nn1["base"][0] - 22, nby, nn2["base"][0], nby, color=POS, sw=2.2))

    # емітер Q1 — прямо на землю
    f.append(line(nn1["emit"][0], nn1["emit"][1], nn1["emit"][0], 380, color=INK, sw=1.8))
    # емітер Q2 — крізь резистор R на землю (ОСЬ де ставиться струм)
    f.append(resistor_v(nn2["emit"][0], nn2["emit"][1] + 2, 360, label="R", side="right", col=POS))
    f.append(line(nn2["emit"][0], 360, nn2["emit"][0], 380, color=INK, sw=1.8))
    f.append(line(nn1["emit"][0], 380, nn2["emit"][0], 380, color=INK, sw=1.8))
    f.append(gnd((nn1["emit"][0] + nn2["emit"][0]) / 2, 380))

    # позначка струму-виходу: знімаємо копію зі стовпа струму (з дзеркала)
    f.append(text(p2x + 30, py - 26, "I_PTAT", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(p2x + 30, py - 10, "роздаємо далі", size=10, color=MUTED, anchor="start"))

    # головна формула збоку
    body, w0, h0 = textbox(W / 2, 412,
                           "На R падає рівно ΔU_BE = (kT/q)·ln N,  тож  I = (kT/q)·ln N / R  —  ∝ T",
                           size=12, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)

    render(os.path.join(IMG, "circuit.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. slope.svg — I_PTAT лінійний з T, пряма крізь 0 K
# ════════════════════════════════════════════════════════════════════════════
def fig_slope():
    W, H = 620, 360
    f = []
    ox, oy = 80, 290
    axw, axh = 480, 230
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 24, "T, абсолютна температура (K)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - axh + 4, "I", size=13, color=INK, bold=True, anchor="end"))
    f.append(text(ox, oy + 20, "0 K", size=11, color=MUTED))

    # пряма PTAT крізь початок координат
    x_end = ox + axw - 30
    y_end = oy - axh + 30
    f.append(line(ox, oy, x_end, y_end, color=NEG, sw=2.8))
    f.append(text(x_end - 6, y_end - 10, "I_PTAT  ∝  T", size=13, color=NEG, bold=True, anchor="end"))

    # робочий діапазон −40…+125 °C ≈ 233…398 K — підсвітити дві точки
    def Tx(T):  # 0..420 K на осі
        return ox + axw * (T / 420.0) * (axw - 30) / axw
    def onln(T):
        # точка на прямій
        x = ox + (x_end - ox) * (T / 420.0)
        y = oy + (y_end - oy) * (T / 420.0)
        return x, y

    for T, lab in [(233, "−40 °C"), (398, "+125 °C")]:
        x, y = onln(T)
        f.append(line(x, oy, x, y, color=MUTED, sw=1.0, dash="3 3"))
        f.append(line(ox, y, x, y, color=MUTED, sw=1.0, dash="3 3"))
        f.append(circle(x, y, 4, fill="#ffffff", stroke=NEG, sw=2.2))
        f.append(text(x, oy + 16, lab, size=10, color=MUTED))

    # для контрасту — «звичайний» струм від резистора з живлення: майже плаский, не крізь 0
    yflat = oy - 120
    f.append(line(ox + 40, yflat + 14, x_end, yflat - 10, color=MUTED, sw=1.8, dash="7 5"))
    f.append(text(x_end - 6, yflat - 18, "звичайний струм: не ∝ T", size=11, color=MUTED, anchor="end"))

    # підпис-висновок
    body, w0, h0 = textbox(W / 2 + 40, oy - 200,
                           "Пряма йде крізь 0 K:\nподвоїв T — подвоїв струм", size=11,
                           color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(body)

    render(os.path.join(IMG, "slope.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. cancel.svg — серце виведення: дикий хвіст I_S входить однаково в обидві U_BE
#    і скорочується в різниці, лишаючи пряму PTAT (для вставки math-ptat-derivation)
# ════════════════════════════════════════════════════════════════════════════
def fig_cancel():
    W, H = 680, 380
    f = []
    f.append(text(W / 2, 28, "Що залежить від температури — і що з цього лишається", size=14, bold=True))

    # ── ліворуч: дві окремі U_BE, кожна з дикою кривиною від I_S ──────────────
    ox, oy = 70, 300
    axw, axh = 230, 230
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw - 2, oy + 22, "T", size=12, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - axh + 6, "U_BE", size=12, color=INK, bold=True, anchor="end"))

    # дві спадні криві U_BE(T) з помітною кривиною (CTAT + curvature)
    import math as _m
    def vbe_curve(x0_off, y0_off, col):
        pts = []
        N = 40
        for i in range(N + 1):
            t = i / N                      # 0..1 по осі T
            # спадна, з угнутістю донизу (curvature) — для наочності
            yv = 1.0 - 0.62 * t - 0.18 * t * t
            x = ox + 20 + (axw - 40) * t
            y = oy - 10 - (axh - 40) * (yv * 0.0) - (axh - 40) * yv * 0.0  # placeholder
            y = oy - 12 - (axh - 30) * (yv - 0.20) / 0.80
            pts.append((x + x0_off, y + y0_off))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))

    f.append(vbe_curve(0, 0, POS))
    f.append(vbe_curve(0, 28, NEG))
    f.append(text(ox + axw - 6, oy - axh + 40, "U_BE1 (малий)", size=10, color=POS, anchor="end"))
    f.append(text(ox + axw - 6, oy - axh + 92, "U_BE2 (×N)", size=10, color=NEG, anchor="end"))
    # підпис: обидві несуть однаковий хвіст I_S
    body, w0, h0 = textbox(ox + axw / 2 + 8, oy - axh - 6,
                           "обидві криві:\nспад + кривина від I_S ~ Tᵉ·e^(−Eg/kT)",
                           size=9.5, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)

    # ── стрілка «беремо різницю» ─────────────────────────────────────────────
    midx = ox + axw + 48
    f.append(arrow(ox + axw + 8, oy - axh / 2, midx + 22, oy - axh / 2, color=FIELD, sw=2.6))
    f.append(text(midx + 4, oy - axh / 2 - 12, "різниця", size=11, color=FIELD, bold=True))
    f.append(text(midx + 4, oy - axh / 2 + 22, "I_S зникає", size=10, color=MUTED))

    # ── праворуч: ΔU_BE — ідеальна пряма крізь 0 ─────────────────────────────
    ox2 = ox + axw + 100
    f.append(arrow(ox2, oy, ox2 + axw - 30, oy, color=INK, sw=1.6))
    f.append(arrow(ox2, oy, ox2, oy - axh, color=INK, sw=1.6))
    f.append(text(ox2 + axw - 34, oy + 22, "T", size=12, color=INK, anchor="end"))
    f.append(text(ox2 - 8, oy - axh + 6, "ΔU_BE", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(ox2, oy + 18, "0 K", size=10, color=MUTED))
    # пряма крізь початок
    xe = ox2 + axw - 60
    ye = oy - axh + 36
    f.append(line(ox2, oy, xe, ye, color=FIELD, sw=2.8))
    f.append(text(xe - 4, ye - 8, "ΔU_BE = (k/q)·ln N · T", size=10, color=FIELD, bold=True, anchor="end"))
    f.append(mtext(ox2 + 14, oy - axh + 60, ["ідеально лінійна,", "крізь нуль"], size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "cancel.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. curvature.svg — звідки кривина: лінійний PTAT гасить лінійну частину U_BE,
#    лишаючи горбик-залишок ln(T) — те, що добиває бандгеп
# ════════════════════════════════════════════════════════════════════════════
def fig_curvature():
    W, H = 669, 360
    f = []
    ox, oy = 80, 250
    axw, axh = 470, 210
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy - axh, ox, oy + 40, color=INK, sw=1.6))
    f.append(text(ox + axw - 2, oy + 26, "T (робочий діапазон)", size=12, color=INK, anchor="end"))

    midy = oy - axh / 2 + 10
    x0 = ox + 14
    x1 = ox + axw - 16

    # CTAT-падіння U_BE: спадна пряма + кривина (увігнута)
    def vbe_y(t):  # t: 0..1
        return midy - 70 * (0.5 - t) + 22 * (t - 0.5) ** 2 - 5
    pts = []
    Nn = 40
    for i in range(Nn + 1):
        t = i / Nn
        pts.append((x0 + (x1 - x0) * t, vbe_y(t)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
    f.append(text(x1 + 4, vbe_y(1.0) + 4, "U_BE ↓ (CTAT, +кривина)", size=10, color=POS, anchor="start"))

    # PTAT-доданок: зростна ПРЯМА, підібрана гасити лінійну частину
    def ptat_y(t):
        return midy + 60 * (0.5 - t)
    f.append(line(x0, ptat_y(0), x1, ptat_y(1), color=NEG, sw=2.4))
    f.append(text(x1 + 4, ptat_y(1.0) + 4, "PTAT ↑ (рівно пряма)", size=10, color=NEG, anchor="start"))

    # сума: майже плоска, але з горбиком-залишком (кривина не скоротилась)
    def sum_y(t):
        # лінійні частини гасяться, лишається тільки квадратичний горб
        return midy - 16 - 26 * 4 * (t - 0.5) ** 2 + 24
    pts2 = []
    for i in range(Nn + 1):
        t = i / Nn
        pts2.append((x0 + (x1 - x0) * t, sum_y(t)))
    d2 = "M %.1f %.1f " % pts2[0] + " ".join("L %.1f %.1f" % p for p in pts2[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d2, FIELD))
    f.append(text((x0 + x1) / 2, sum_y(0.5) - 12, "сума ≈ плоска", size=11, color=FIELD, bold=True))

    # винесена дужка на горбик-залишок
    f.append(text((x0 + x1) / 2 + 120, sum_y(0.95) + 4,
                  "горб-залишок ∝ U_T·ln T", size=10, color=INK, anchor="start"))
    f.append(arrow((x0 + x1) / 2 + 118, sum_y(0.95), x0 + (x1 - x0) * 0.78, sum_y(0.78) - 2,
                   color=MUTED, sw=1.4))

    body, w0, h0 = textbox(W / 2, oy + 50,
                           "Прямий PTAT гасить ЛІНІЙНУ частину спаду U_BE начисто.\n"
                           "Лишається тільки кривина ~ln T — її добиває бандгеп окремою поправкою.",
                           size=10.5, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "curvature.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_circuit()
    fig_slope()
    fig_cancel()
    fig_curvature()
    print("OK: 5 фігур у", IMG)
