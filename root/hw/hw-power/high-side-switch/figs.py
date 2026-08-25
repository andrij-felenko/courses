# -*- coding: utf-8 -*-
"""Фігури до теми «Верхній ключ» та її вставки «P-MOSFET як верхній ключ навантаження».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── символи транзисторів ─────────────────────────────────────────────────────
def nmos_symbol(cx, cy, color=INK, sw=2.2):
    """Спрощений символ N-MOSFET. Стік угорі (D), витік унизу (S), затвор ліворуч (G).
    Повертає (svg, точки D, G, S)."""
    out = []
    chx = cx
    d_y, s_y = cy - 34, cy + 34
    out.append(line(chx, d_y, chx, s_y, color=color, sw=sw + 0.4))
    gx = cx - 26
    out.append(line(gx, cy - 22, gx, cy + 22, color=color, sw=sw + 0.4))
    out.append(line(gx, cy, gx + 26, cy, color=color, sw=sw))
    out.append(line(gx, cy, gx - 22, cy, color=color, sw=sw))
    out.append(line(chx, d_y, chx, d_y - 18, color=color, sw=sw))
    out.append(line(chx, s_y, chx, s_y + 18, color=color, sw=sw))
    out.append(text(chx + 14, d_y + 4, "D", size=13, bold=True, color=color, anchor="start"))
    out.append(text(chx + 14, s_y + 4, "S", size=13, bold=True, color=color, anchor="start"))
    out.append(text(gx - 26, cy + 4, "G", size=13, bold=True, color=color, anchor="end"))
    return "".join(out), (chx, d_y - 18), (gx - 22, cy), (chx, s_y + 18)


def pmos_symbol(cx, cy, color=INK, sw=2.2):
    """Спрощений символ P-MOSFET. Витік угорі (S), стік унизу (D), затвор ліворуч (G).
    Повертає (svg, точки S, G, D у вигляді кортежів)."""
    out = []
    chx = cx
    s_y, d_y = cy - 34, cy + 34
    out.append(line(chx, s_y, chx, d_y, color=color, sw=sw + 0.4))
    gx = cx - 26
    out.append(line(gx, cy - 22, gx, cy + 22, color=color, sw=sw + 0.4))
    out.append(line(gx, cy, gx + 26, cy, color=color, sw=sw))
    out.append(line(gx, cy, gx - 22, cy, color=color, sw=sw))
    out.append(line(chx, s_y, chx, s_y - 18, color=color, sw=sw))
    out.append(line(chx, d_y, chx, d_y + 18, color=color, sw=sw))
    out.append(text(chx + 14, s_y + 4, "S", size=13, bold=True, color=color, anchor="start"))
    out.append(text(chx + 14, d_y + 4, "D", size=13, bold=True, color=color, anchor="start"))
    out.append(text(gx - 26, cy + 4, "G", size=13, bold=True, color=color, anchor="end"))
    return "".join(out), (chx, s_y - 18), (gx - 22, cy), (chx, d_y + 18)


def cap_symbol(x, ytop, ybot, color=LINE, sw=2.4, gap=8, half=11):
    """Конденсатор на вертикальному проводі x між ytop і ybot. Повертає svg і середину пластин."""
    midy = (ytop + ybot) / 2
    out = [line(x, ytop, x, midy - gap / 2, color=color, sw=1.8),
           line(x - half, midy - gap / 2, x + half, midy - gap / 2, color=color, sw=sw),
           line(x - half, midy + gap / 2, x + half, midy + gap / 2, color=color, sw=sw),
           line(x, midy + gap / 2, x, ybot, color=color, sw=1.8)]
    return "".join(out), midy


def diode_symbol(x, ytop, ybot, color=LINE, sw=1.8, down=True):
    """Діод на вертикальному проводі x. down=True → провідність згори вниз (катод унизу)."""
    midy = (ytop + ybot) / 2
    s = 9
    out = [line(x, ytop, x, midy - s, color=color, sw=sw)]
    if down:
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
            x - s, midy - s, x + s, midy - s, x, midy + s, color))
        out.append(line(x - s, midy + s, x + s, midy + s, color=color, sw=sw + 0.6))  # катодна риска
    else:
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
            x - s, midy + s, x + s, midy + s, x, midy - s, color))
        out.append(line(x - s, midy - s, x + s, midy - s, color=color, sw=sw + 0.6))
    out.append(line(x, midy + s, x, ybot, color=color, sw=sw))
    return "".join(out), midy


# ═════════════════════ ФІГУРИ СТАТТІ «Верхній ключ» ═════════════════════════

# ── 1. Чому верхньому N-ключу мало шини: витік сам злітає до Vbus ─────────────
def fig_why_above_rail():
    W, H = 760, 410
    f = [text(W / 2, 26, "Верхній N-ключ: Vgs міряється від витоку, а витік злітає до шини",
              size=15, bold=True)]

    def panel(x0, title, gate_v, src_v, vgs_txt, ok):
        col = FIELD if ok else MUTED
        f.append(rect(x0, 52, 340, 326, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 76, title, size=12.5, bold=True, color=INK))
        railx0, railx1 = x0 + 40, x0 + 300
        ry = 104
        f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
        f.append(text(x0 + 170, ry - 8, "+12 В (шина = найвища напруга)", size=11, bold=True, color=POS))
        tcx, tcy = x0 + 150, 198
        sym, dp, gp, sp = nmos_symbol(tcx, tcy)
        f.append(sym)
        f.append(line(dp[0], dp[1], dp[0], ry, color=LINE, sw=1.8))      # стік до шини
        # навантаження від витоку до землі
        ly = 312
        f.append(rect(tcx - 24, sp[1] + 4, 48, 30, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(tcx, sp[1] + 23, "наван-", size=10, color=INK))
        f.append(line(sp[0], sp[1], tcx, sp[1] + 4, color=LINE, sw=1.8))
        f.append(line(tcx, sp[1] + 34, tcx, ly, color=LINE, sw=1.8))
        f.append(line(railx0, ly, railx1, ly, color=NEG, sw=2.2))
        f.append(text(x0 + 170, ly + 18, "0 В (земля)", size=11, color=NEG))
        # позначка напруги витоку
        f.append(text(tcx + 30, sp[1] - 6, "витік = %s" % src_v, size=11, bold=True,
                      color=NEG, anchor="start"))
        # керування затвором
        gcol = FIELD if ok else POS
        f.append(line(gp[0], gp[1], gp[0] - 36, gp[1], color=gcol, sw=2.2))
        box, _, _ = textbox(gp[0] - 86, gp[1], "затвор\n= %s" % gate_v, size=11, bold=True,
                            fill=("#eef6ef" if ok else "#fbeee6"), stroke=gcol, color=gcol)
        f.append(box)
        f.append(text(tcx + 30, tcy - 2, vgs_txt, size=11.5, bold=True, color=col, anchor="start"))
        f.append(text(tcx + 30, tcy + 16, ("ON ✓" if ok else "OFF ✗"), size=13, bold=True,
                      color=col, anchor="start"))

    panel(28, "Подаємо саму шину — ключ замкнений", "12 В", "≈12 В", "Vgs = 12−12 = 0", False)
    panel(392, "Затвор вище шини — ключ відкритий", "17 В", "≈12 В", "Vgs = 17−12 = +5", True)
    return render(os.path.join(IMG, "why-above-rail.svg"), W, H, *f)


# ── 2. Нижній ключ: опора нерухома; верхній: опора плаває ────────────────────
def fig_low_vs_high():
    W, H = 760, 420
    f = [text(W / 2, 26, "Уся різниця — де стоїть опора, від якої міряється Vgs", size=15, bold=True)]

    # ЛІВО: нижній ключ — витік на землі
    x0 = 28
    f.append(rect(x0, 52, 340, 338, fill=BG, stroke=FIELD, sw=2, rx=12))
    f.append(text(x0 + 170, 76, "Нижній ключ: опора прибита до землі", size=12.5, bold=True, color=INK))
    railx0, railx1 = x0 + 40, x0 + 300
    ry = 100
    f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
    f.append(text(x0 + 170, ry - 8, "+V (шина)", size=11, bold=True, color=POS))
    # навантаження зверху, ключ знизу
    tcx = x0 + 150
    f.append(rect(tcx - 24, 116, 48, 30, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(tcx, 135, "наван-", size=10, color=INK))
    f.append(line(tcx, ry, tcx, 116, color=LINE, sw=1.8))
    tcy = 232
    sym, dp, gp, sp = nmos_symbol(tcx, tcy)
    f.append(sym)
    f.append(line(dp[0], dp[1], tcx, 146, color=LINE, sw=1.8))
    gy = 330
    f.append(line(sp[0], sp[1], sp[0], gy, color=NEG, sw=2.2))
    f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.2))
    f.append(text(x0 + 170, gy + 18, "0 В (земля)", size=11, color=NEG))
    f.append(circle(sp[0], gy, 3.2, fill=NEG, stroke=NEG))
    f.append(text(sp[0] + 12, sp[1] + 18, "витік = 0 (не їде)", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(gp[0], gp[1], gp[0] - 34, gp[1], color=FIELD, sw=2.2))
    box, _, _ = textbox(gp[0] - 82, gp[1], "5 В\nвід МК", size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD)
    f.append(box)
    f.append(text(tcx + 28, tcy + 2, "Vgs = 5−0 = 5 В", size=11.5, bold=True, color=FIELD, anchor="start"))

    # ПРАВО: верхній ключ — витік плаває
    x0 = 392
    f.append(rect(x0, 52, 340, 338, fill=BG, stroke=POS, sw=2, rx=12))
    f.append(text(x0 + 170, 76, "Верхній ключ: опора плаває 0…+V", size=12.5, bold=True, color=INK))
    railx0, railx1 = x0 + 40, x0 + 300
    ry = 100
    f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
    f.append(text(x0 + 170, ry - 8, "+V (шина)", size=11, bold=True, color=POS))
    tcx = x0 + 150
    tcy = 178
    sym, dp, gp, sp = nmos_symbol(tcx, tcy)
    f.append(sym)
    f.append(line(dp[0], dp[1], dp[0], ry, color=LINE, sw=1.8))
    # навантаження під ключем
    f.append(rect(tcx - 24, 248, 48, 30, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(tcx, 267, "наван-", size=10, color=INK))
    f.append(line(sp[0], sp[1], tcx, 248, color=LINE, sw=1.8))
    gy = 330
    f.append(line(tcx, 278, tcx, gy, color=LINE, sw=1.8))
    f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.2))
    f.append(text(x0 + 170, gy + 18, "0 В (земля)", size=11, color=NEG))
    # подвійна стрілка «плаває»
    f.append(line(sp[0] + 30, ry + 6, sp[0] + 30, 244, color=POS, sw=1.6, dash="5,4"))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        sp[0] + 30, ry + 4, sp[0] + 26, ry + 14, sp[0] + 34, ry + 14, POS))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        sp[0] + 30, 246, sp[0] + 26, 236, sp[0] + 34, 236, POS))
    f.append(text(sp[0] + 38, 175, "витік", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(sp[0] + 38, 191, "плаває", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(gp[0], gp[1], gp[0] - 34, gp[1], color=POS, sw=2.2))
    box, _, _ = textbox(gp[0] - 90, gp[1], "затвор ?\n> шини", size=11, bold=True, fill="#fbeee6", stroke=POS, color=POS)
    f.append(box)
    return render(os.path.join(IMG, "low-vs-high.svg"), W, H, *f)


# ── 3. Бутстреп у дві фази ───────────────────────────────────────────────────
def fig_bootstrap():
    W, H = 780, 430
    f = [text(W / 2, 26, "Бутстреп: конденсатор заряджається внизу й їде з витоком угору", size=15, bold=True)]

    def half(x0, title, phase2):
        f.append(rect(x0, 52, 348, 350, fill=BG, stroke=(POS if phase2 else FIELD), sw=2, rx=12))
        f.append(text(x0 + 174, 76, title, size=12.5, bold=True, color=INK))
        # шина Vbus
        railx0, railx1 = x0 + 30, x0 + 320
        ry = 102
        f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
        f.append(text(railx0 + 4, ry - 8, "Vbus", size=11, bold=True, color=POS, anchor="start"))
        # низьковольтне Vdrv (ліворуч)
        vdrv_x = x0 + 44
        f.append(text(vdrv_x, 132, "Vdrv 12 В", size=10.5, bold=True, color=INK, anchor="start"))
        f.append(circle(vdrv_x + 2, 140, 3, fill=INK, stroke=INK))
        # верхній ключ
        tcx = x0 + 196
        tcy = 196
        sym, dp, gp, sp = nmos_symbol(tcx, tcy)
        f.append(sym)
        f.append(line(dp[0], dp[1], dp[0], ry, color=LINE, sw=1.8))
        # точка SW = витік верхнього
        swx = tcx
        swy = sp[1]
        # нижній ключ під SW
        ntcy = 320
        nsym, ndp, ngp, nsp = nmos_symbol(tcx, ntcy)
        f.append(nsym)
        f.append(line(sp[0], swy, ndp[0], ndp[1], color=LINE, sw=1.8))
        gy = 392
        f.append(line(nsp[0], nsp[1], nsp[0], gy, color=NEG, sw=2.0))
        f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.2))
        f.append(text(railx0 + 4, gy + 16, "GND", size=10.5, color=NEG, anchor="start"))
        f.append(circle(swx, swy, 3.2, fill=INK, stroke=INK))
        f.append(text(swx + 14, swy - 6, "SW", size=11, bold=True, color=INK, anchor="start"))
        # діод Dbs від Vdrv до VB
        vbx = vdrv_x + 2
        dsvg, dmid = diode_symbol(vbx, 140, 200, down=True)
        f.append(dsvg)
        f.append(text(vbx - 6, dmid + 4, "Dbs", size=10, color=MUTED, anchor="end"))
        vby = 200
        f.append(circle(vbx, vby, 3, fill=INK, stroke=INK))
        f.append(text(vbx + 6, vby - 6, "VB", size=11, bold=True, color=FIELD, anchor="start"))
        # Cbs між VB і SW
        csvg, cmid = cap_symbol(vbx, vby, swy)
        f.append(csvg)
        # провід Cbs низ до SW
        f.append(line(vbx, swy, swx, swy, color=LINE, sw=1.6))
        f.append(text(vbx - 6, cmid + 4, "Cbs", size=10, bold=True, color=INK, anchor="end"))
        if not phase2:
            # фаза 1: нижній ON, SW≈0, струм заряду
            f.append(text(ngp[0] - 4, ngp[1] - 8, "ON", size=11, bold=True, color=FIELD, anchor="end"))
            f.append(text(gp[0] - 4, gp[1] - 8, "off", size=10.5, color=MUTED, anchor="end"))
            f.append(text(swx + 14, swy + 14, "SW ≈ 0", size=11, bold=True, color=NEG, anchor="start"))
            box, _, _ = textbox(x0 + 174, 372, "Cbs набирає 12 В  (Vdrv→Dbs→Cbs→SW→GND)",
                                size=10.5, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD)
            f.append(box)
        else:
            f.append(text(gp[0] - 4, gp[1] - 8, "ON", size=11, bold=True, color=POS, anchor="end"))
            f.append(text(ngp[0] - 4, ngp[1] - 8, "off", size=10.5, color=MUTED, anchor="end"))
            f.append(text(swx + 14, swy + 14, "SW ↑ Vbus", size=11, bold=True, color=POS, anchor="start"))
            f.append(text(vbx + 6, vby + 4, "= Vbus+12", size=10, bold=True, color=POS, anchor="start"))
            box, _, _ = textbox(x0 + 174, 372, "VB = Vbus+12 → Vgs(верх)=12 В,  Dbs замкнений",
                                size=10.5, bold=True, fill="#fbeee6", stroke=POS, color=POS)
            f.append(box)

    half(20, "Фаза 1 — заряд (нижній ON)", False)
    half(412, "Фаза 2 — робота (верхній ON)", True)
    return render(os.path.join(IMG, "bootstrap.svg"), W, H, *f)


# ── 4. Бутстреп стікає між перезарядами ──────────────────────────────────────
def fig_bootstrap_limit():
    W, H = 760, 360
    f = [text(W / 2, 26, "Напруга бутстрепа стікає, поки SW не впаде до землі", size=15, bold=True)]
    ox, oy = 90, 300         # початок осей
    ow, oh = 600, 210
    f.append(line(ox, oy, ox + ow, oy, color=INK, sw=1.8))   # вісь часу
    f.append(line(ox, oy, ox, oy - oh, color=INK, sw=1.8))   # вісь напруги
    f.append(text(ox + ow, oy + 20, "час", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - oh + 4, "VB − SW", size=12, bold=True, color=INK, anchor="end"))
    # рівень повного заряду й поріг
    full_y = oy - 170
    thr_y = oy - 70
    f.append(line(ox, full_y, ox + ow, full_y, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(ox + ow + 2, full_y + 4, "12 В", size=11, color=MUTED, anchor="start"))
    f.append(line(ox, thr_y, ox + ow, thr_y, color=POS, sw=1.4, dash="6,4"))
    f.append(text(ox + ow + 2, thr_y + 4, "поріг", size=11, bold=True, color=POS, anchor="start"))

    # пилкоподібна крива: заряд (стрибок угору при SW=0) і повільний спад
    pts = []
    x = ox
    y = full_y
    seg = 150
    import math
    # перший цикл — нормальний
    for cyc in range(2):
        # перезаряд: вертикально вгору
        pts.append((x, full_y))
        # повільний спад
        for i in range(0, seg + 1, 10):
            yy = full_y + (oy - 40 - full_y) * 0  # placeholder
        # лінійний спад до ~thr+30
        x2 = x + seg
        y2 = full_y + 95
        pts.append((x2, y2))
        x = x2
    # третій цикл — затяжне ON, спад нижче порога
    pts.append((x, full_y))
    x3 = x + 230
    y3 = thr_y + 45     # нижче порога
    pts.append((x3, y3))
    # будуємо polyline
    pstr = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pstr, FIELD))
    # позначки SW↓ під перезарядами
    for (px, _) in pts:
        if abs(px - ox) < 1 or abs(px - (ox + seg)) < 1 or abs(px - (ox + 2 * seg)) < 1:
            f.append(line(px, oy, px, oy + 8, color=NEG, sw=1.6))
            f.append(text(px, oy + 22, "SW↓", size=9.5, color=NEG))
    # хрестик там, де крива впала нижче порога
    f.append(circle(x3, y3, 5, fill=POS, stroke=POS))
    f.append(text(x3 - 6, y3 - 10, "ключ згас", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(ox + 2 * seg + 115, full_y - 10, "верхній тримають без пауз →", size=10.5, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, "bootstrap-limit.svg"), W, H, *f)


# ── 5. Зарядова помпа — два такти ────────────────────────────────────────────
def fig_charge_pump():
    W, H = 780, 410
    f = [text(W / 2, 26, "Зарядова помпа: летючий конденсатор переливає заряд тактами", size=15, bold=True)]

    def half(x0, title, takt_b):
        col = POS if takt_b else FIELD
        f.append(rect(x0, 52, 348, 330, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 174, 76, title, size=12.5, bold=True, color=INK))
        railx0, railx1 = x0 + 30, x0 + 320
        ry = 104
        f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
        f.append(text(railx0 + 4, ry - 8, "12 В", size=11, bold=True, color=POS, anchor="start"))
        gy = 350
        f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.2))
        f.append(text(railx0 + 4, gy + 16, "GND", size=10.5, color=NEG, anchor="start"))
        # летючий конденсатор C1 (ліворуч)
        c1x = x0 + 120
        topnode = 150 if not takt_b else 150
        if not takt_b:
            # такт A: C1 між 12В і землею
            f.append(line(c1x, ry, c1x, 150, color=LINE, sw=1.8))
            csvg, cmid = cap_symbol(c1x, 150, 270)
            f.append(csvg)
            f.append(line(c1x, 270, c1x, gy, color=LINE, sw=1.8))
            f.append(text(c1x - 8, cmid + 4, "C1", size=11, bold=True, color=INK, anchor="end"))
            f.append(text(c1x + 12, cmid - 28, "верх", size=10, color=MUTED, anchor="start"))
            f.append(text(c1x + 12, cmid - 14, "= 12 В", size=10, bold=True, color=FIELD, anchor="start"))
            box, _, _ = textbox(x0 + 174, 322, "C1 заряджається до 12 В", size=10.5, bold=True,
                                fill="#eef6ef", stroke=FIELD, color=FIELD)
            f.append(box)
        else:
            # такт B: низ C1 підкинуто на 12В, верх → 24 В, через діод у Cout
            f.append(line(c1x, gy, c1x, 270, color=POS, sw=1.8))   # низ тепер до +12 (підкинуто)
            f.append(line(railx0, 290, c1x, 290, color=POS, sw=1.6, dash="4,3"))
            csvg, cmid = cap_symbol(c1x, 150, 270)
            f.append(csvg)
            f.append(text(c1x - 8, cmid + 4, "C1", size=11, bold=True, color=INK, anchor="end"))
            f.append(text(c1x + 12, cmid - 28, "верх", size=10, color=MUTED, anchor="start"))
            f.append(text(c1x + 12, cmid - 14, "≈ 24 В", size=10, bold=True, color=POS, anchor="start"))
            # діод від верху C1 до Cout
            dx0, dx1 = c1x, x0 + 250
            f.append(line(c1x, 150, dx0 + 40, 150, color=LINE, sw=1.6))
            ddsvg, _ = diode_symbol(dx0 + 40, 150, 150, down=True)
            # горизонтальний діод намалюємо вручну
            dy = 150
            ax = dx0 + 70
            f.append(line(dx0 + 40, dy, ax, dy, color=LINE, sw=1.6))
            f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
                ax, dy - 9, ax, dy + 9, ax + 16, dy, LINE))
            f.append(line(ax + 16, dy - 9, ax + 16, dy + 9, color=LINE, sw=2.2))
            f.append(line(ax + 16, dy, dx1, dy, color=LINE, sw=1.6))
            f.append(text(ax + 6, dy - 14, "D", size=10, color=MUTED))
            # Cout
            coutx = dx1
            f.append(line(coutx, dy, coutx, 200, color=LINE, sw=1.8))
            csvg2, cmid2 = cap_symbol(coutx, 200, 300)
            f.append(csvg2)
            f.append(line(coutx, 300, coutx, gy, color=LINE, sw=1.8))
            f.append(text(coutx + 10, cmid2 + 4, "Cout", size=11, bold=True, color=INK, anchor="start"))
            f.append(text(coutx + 10, cmid2 + 20, "≈ 24 В", size=10, bold=True, color=POS, anchor="start"))
            box, _, _ = textbox(x0 + 174, 322, "низ C1 ↑ 12 В → верх 24 В → у Cout", size=10.5, bold=True,
                                fill="#fbeee6", stroke=POS, color=POS)
            f.append(box)

    half(20, "Такт A — заряд C1", False)
    half(412, "Такт B — переливання у Cout", True)
    return render(os.path.join(IMG, "charge-pump.svg"), W, H, *f)


# ── 6. Бутстреп проти помпи — порівняння ─────────────────────────────────────
def fig_boot_vs_pump():
    W, H = 760, 360
    f = [text(W / 2, 28, "Бутстреп проти зарядової помпи: коли що брати", size=16, bold=True)]
    rows = [
        ("",               "бутстреп",                 "зарядова помпа"),
        ("деталі",         "1 діод + 1 конденсатор",   "кілька конд. + такт"),
        ("V над шиною",    "конденсатор їде з SW",     "перекачка заряду тактами"),
        ("тримає 100% ON", "НІ (стікає)",              "ТАК (постійно)"),
        ("струм у затвор", "великий (імпульсний)",     "малий"),
        ("типове місце",   "ШІМ-мости, інвертори",     "always-on верхній ключ"),
    ]
    x0, y0 = 40, 60
    cw = [180, 250, 250]
    rh = 44
    cx = [x0, x0 + cw[0], x0 + cw[0] + cw[1]]
    for ri, row in enumerate(rows):
        y = y0 + ri * rh
        for ci, cell in enumerate(row):
            head = (ri == 0) or (ci == 0)
            fill = FILL if head else BG
            if ri == 0 and ci == 1:
                fill = "#eef6ef"
            if ri == 0 and ci == 2:
                fill = "#fbeee6"
            f.append(rect(cx[ci], y, cw[ci], rh, fill=fill, stroke=LINE, sw=1.2, rx=4))
            col = INK
            if ri == 3 and ci == 1:
                col = POS
            if ri == 3 and ci == 2:
                col = FIELD
            f.append(fitbox(cx[ci], y, cw[ci], rh, cell, size=12.5,
                            bold=head, fill="none", stroke="none", color=col))
    return render(os.path.join(IMG, "boot-vs-pump.svg"), W, H, *f)


# ── 7. Мікросхема-драйвер півмоста ───────────────────────────────────────────
def fig_halfbridge_driver():
    W, H = 780, 400
    f = [text(W / 2, 26, "Драйвер півмоста ховає бутстреп, зсув рівня й мертвий час", size=15, bold=True)]
    # корпус мікросхеми
    chx, chy, chw, chh = 230, 90, 220, 220
    f.append(rect(chx, chy, chw, chh, fill="#f8fafb", stroke=INK, sw=2, rx=10))
    f.append(text(chx + chw / 2, chy + 26, "драйвер півмоста", size=13, bold=True, color=INK))
    f.append(text(chx + chw / 2, chy + 70, "зсув рівня", size=11.5, color=MUTED))
    f.append(text(chx + chw / 2, chy + 92, "+ мертвий час", size=11.5, color=MUTED))
    # логічні входи зліва
    f.append(rect(40, 150, 78, 44, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    f.append(mtext(79, 168, ["МК", "(HIN/LIN)"], size=11, bold=True))
    f.append(line(118, 162, chx, 132, color=LINE, sw=1.8))
    f.append(line(118, 182, chx, 168, color=LINE, sw=1.8))
    f.append(text(chx - 6, 130, "HIN", size=10.5, bold=True, color=INK, anchor="end"))
    f.append(text(chx - 6, 170, "LIN", size=10.5, bold=True, color=INK, anchor="end"))
    # живлення драйвера + діод до VB
    f.append(text(chx - 6, 220, "Vdrv", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(line(150, 232, chx, 220, color=LINE, sw=1.6))
    f.append(circle(150, 232, 3, fill=POS, stroke=POS))

    # вихід LO (нижній ключ)
    railx1 = 740
    ry = 70
    f.append(line(470, ry, railx1, ry, color=POS, sw=2.4))
    f.append(text(railx1 - 4, ry - 8, "Vbus", size=11, bold=True, color=POS, anchor="end"))
    gy = 360
    f.append(line(470, gy, railx1, gy, color=NEG, sw=2.2))
    f.append(text(railx1 - 4, gy + 16, "GND", size=10.5, color=NEG, anchor="end"))

    # верхній ключ праворуч
    tcx = 600
    tcy = 150
    sym, dp, gp, sp = nmos_symbol(tcx, tcy)
    f.append(sym)
    f.append(line(dp[0], dp[1], dp[0], ry, color=LINE, sw=1.8))
    swx, swy = tcx, sp[1]
    # нижній ключ
    ntcy = 290
    nsym, ndp, ngp, nsp = nmos_symbol(tcx, ntcy)
    f.append(nsym)
    f.append(line(swx, swy, ndp[0], ndp[1], color=LINE, sw=1.8))
    f.append(line(nsp[0], nsp[1], nsp[0], gy, color=LINE, sw=1.8))
    f.append(circle(swx, swy, 3.2, fill=INK, stroke=INK))
    f.append(text(swx + 12, swy + 4, "SW", size=10.5, bold=True, color=INK, anchor="start"))
    # HO → затвор верхнього
    f.append(line(chx + chw, 132, gp[0], gp[1], color=FIELD, sw=2.0))
    f.append(text(chx + chw + 6, 128, "HO", size=10.5, bold=True, color=FIELD, anchor="start"))
    # LO → затвор нижнього
    f.append(line(chx + chw, 250, ngp[0], ngp[1], color=LINE, sw=1.8))
    f.append(text(chx + chw + 6, 250, "LO", size=10.5, bold=True, color=INK, anchor="start"))
    # VB / VS плаваюча пара + бутстреп конд.
    vbx = chx + chw + 40
    f.append(text(chx + chw + 6, 150, "VB", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(chx + chw + 6, 200, "VS", size=10, bold=True, color=MUTED, anchor="start"))
    f.append(line(chx + chw, 150, vbx, 150, color=POS, sw=1.6))
    f.append(line(chx + chw, 200, vbx, 200, color=MUTED, sw=1.6))
    csvg, cmid = cap_symbol(vbx, 150, 200)
    f.append(csvg)
    f.append(text(vbx + 8, cmid + 4, "Cbs", size=10, bold=True, color=INK, anchor="start"))
    # VS стежить за SW
    f.append(line(vbx, 200, vbx, 232, color=MUTED, sw=1.4, dash="4,3"))
    f.append(line(vbx, 232, swx, 232, color=MUTED, sw=1.4, dash="4,3"))
    f.append(line(swx, 232, swx, swy, color=MUTED, sw=1.4, dash="4,3"))
    return render(os.path.join(IMG, "halfbridge-driver.svg"), W, H, *f)


# ═══════════ ФІГУРИ ВСТАВКИ «P-MOSFET як верхній ключ навантаження» ══════════

# ── Чому PMOS зручний зверху: затвор НИЖЧЕ витоку вмикає ──────────────────────
def fig_why_pmos_on_top():
    W, H = 760, 400
    f = [text(W / 2, 26, "P-MOSFET зверху: щоб увімкнути, затвор тягнемо НИЖЧЕ витоку", size=15.5, bold=True)]

    def panel(x0, title, gate_low, ok):
        col = FIELD if ok else MUTED
        f.append(rect(x0, 52, 340, 320, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 76, title, size=13, bold=True, color=INK))
        railx0, railx1 = x0 + 40, x0 + 300
        ry = 104
        f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
        f.append(text(x0 + 170, ry - 8, "+12 В (шина)", size=12, bold=True, color=POS))
        tcx, tcy = x0 + 170, 200
        sym, sp, gp, dp = pmos_symbol(tcx, tcy)
        f.append(sym)
        f.append(line(sp[0], sp[1], sp[0], ry, color=LINE, sw=1.8))
        ly = 300
        f.append(rect(tcx - 22, dp[1] + 4, 44, 30, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(tcx, dp[1] + 23, "наван-", size=10, color=INK))
        f.append(line(dp[0], dp[1], tcx, dp[1] + 4, color=LINE, sw=1.8))
        gy0 = ly
        f.append(line(tcx, dp[1] + 34, tcx, gy0, color=LINE, sw=1.8))
        f.append(line(railx0, gy0, railx1, gy0, color=NEG, sw=2.2))
        f.append(text(x0 + 170, gy0 + 18, "0 В (земля)", size=11, color=NEG))
        if gate_low:
            f.append(line(gp[0], gp[1], gp[0] - 36, gp[1], color=FIELD, sw=2.2))
            box, _, _ = textbox(gp[0] - 86, gp[1], "затвор\n≈ 0 В", size=11.5, bold=True,
                                fill="#eef6ef", stroke=FIELD, color=FIELD)
            f.append(box)
            f.append(text(tcx + 64, tcy - 2, "Vgs = 0−12 = −12 В", size=11.5, bold=True, color=FIELD, anchor="start"))
            f.append(text(tcx + 64, tcy + 16, "ON ✓", size=13, bold=True, color=FIELD, anchor="start"))
        else:
            f.append(line(gp[0], gp[1], gp[0] - 36, gp[1], color=POS, sw=2.2))
            box, _, _ = textbox(gp[0] - 88, gp[1], "затвор\n= +12 В", size=11.5, bold=True,
                                fill="#fbeee6", stroke=POS, color=POS)
            f.append(box)
            f.append(text(tcx + 64, tcy - 2, "Vgs = 12−12 = 0 В", size=11.5, bold=True, color=MUTED, anchor="start"))
            f.append(text(tcx + 64, tcy + 16, "OFF", size=13, bold=True, color=MUTED, anchor="start"))

    panel(28, "Затвор піднятий до витоку → замкнено", False, False)
    panel(392, "Затвор стягнутий униз → відкрито", True, True)
    return render(os.path.join(IMG, "pmos-on-top.svg"), W, H, *f)


# ── Реальна схема: NPN перекладає рівень, конденсатор робить плавний пуск ─────
def fig_npn_drive():
    W, H = 780, 440
    f = [text(W / 2, 26, "Керування P-ключем з логіки: NPN тягне затвор, RC згладжує пуск", size=15, bold=True)]

    railx0, railx1 = 70, 710
    ry = 70
    f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.6))
    f.append(text(railx1 - 4, ry - 8, "+12 В", size=12.5, bold=True, color=POS, anchor="end"))

    gy = 392
    f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.4))
    f.append(text(railx1 - 4, gy + 18, "0 В", size=12, color=NEG, anchor="end"))

    tcx, tcy = 560, 190
    sym, sp, gp, dp = pmos_symbol(tcx, tcy)
    f.append(sym)
    f.append(line(sp[0], sp[1], sp[0], ry, color=LINE, sw=1.8))
    f.append(rect(tcx - 34, 300, 68, 36, fill=FILL, stroke=LINE, sw=1.5))
    f.append(mtext(tcx, 316, ["наван-", "таження"], size=10, color=INK, lh=1.25))
    f.append(line(dp[0], dp[1], tcx, 300, color=LINE, sw=1.8))
    f.append(line(tcx, 336, tcx, gy, color=LINE, sw=1.8))

    gnx = gp[0]
    gny = gp[1]
    r1x = gnx
    f.append(rect(r1x - 11, 96, 22, 46, fill=BG, stroke=LINE, sw=1.6))
    f.append(line(r1x, ry, r1x, 96, color=LINE, sw=1.8))
    f.append(line(r1x, 142, r1x, gny, color=LINE, sw=1.8))
    f.append(text(r1x + 16, 122, "R1", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(r1x + 16, 138, "10к", size=10.5, color=MUTED, anchor="start"))
    f.append(line(gnx, gny, gnx + 40, gny, color=LINE, sw=1.6))
    f.append(line(gnx + 40, gny, gnx + 40, gny - 24, color=LINE, sw=1.6))
    f.append(line(gnx + 32, gny - 24, gnx + 48, gny - 24, color=LINE, sw=2.4))
    f.append(line(gnx + 32, gny - 32, gnx + 48, gny - 32, color=LINE, sw=2.4))
    f.append(line(gnx + 40, gny - 32, gnx + 40, gny - 50, color=LINE, sw=1.6))
    f.append(line(gnx + 40, gny - 50, sp[0], gny - 50, color=LINE, sw=1.6))
    f.append(line(sp[0], gny - 50, sp[0], sp[1], color=LINE, sw=1.6))
    f.append(text(gnx + 54, gny - 26, "C", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(gnx + 54, gny - 10, "пуск", size=10, color=MUTED, anchor="start"))

    npx, npy = 300, 250
    f.append(line(npx, npy - 30, npx, npy + 30, color=INK, sw=2.6))
    f.append(line(npx - 26, npy, npx, npy, color=INK, sw=2.2))
    f.append(line(npx, npy - 22, npx + 22, npy - 36, color=INK, sw=2.2))
    f.append(line(npx, npy + 22, npx + 22, npy + 36, color=INK, sw=2.2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        npx + 22, npy + 36, npx + 12, npy + 28, npx + 18, npy + 24, INK))
    f.append(text(npx + 26, npy - 34, "C", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(npx + 26, npy + 42, "E", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(npx - 30, npy + 4, "B", size=11.5, bold=True, color=INK, anchor="end"))
    f.append(text(npx, npy + 60, "NPN", size=11, color=MUTED))
    f.append(line(npx + 22, npy - 36, gnx, npy - 36, color=LINE, sw=1.8))
    f.append(line(gnx, npy - 36, gnx, gny, color=LINE, sw=1.8))
    f.append(circle(gnx, gny, 3.2, fill=INK, stroke=INK))
    f.append(line(npx + 22, npy + 36, npx + 22, gy, color=LINE, sw=1.8))
    f.append(rect(150, npy - 11, 46, 22, fill=BG, stroke=LINE, sw=1.6))
    f.append(line(196, npy, npx - 26, npy, color=LINE, sw=1.8))
    f.append(text(173, npy - 16, "Rb", size=11.5, bold=True, color=INK))
    f.append(line(70, npy, 150, npy, color=LINE, sw=1.8))
    f.append(rect(58, npy - 22, 70, 44, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    f.append(mtext(93, npy - 2, ["MCU", "GPIO"], size=11, bold=True))
    f.append(line(128, npy, 150, npy, color=LINE, sw=1.8))

    lx, ly0 = 70, 120
    f.append(rect(lx - 8, ly0 - 20, 372, 62, fill="#f8fafb", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(lx, ly0, "GPIO = 1 → NPN ON → затвор вниз → P-ключ ON", size=11.5, color=FIELD, anchor="start", bold=True))
    f.append(text(lx, ly0 + 22, "GPIO = 0 → NPN OFF → R1 тягне затвор до +12 → OFF", size=11.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "pmos-npn-drive.svg"), W, H, *f)


# ═══════════ ФІГУРА ВСТАВКИ «Розмір бутстрепного конденсатора» ══════════════
def fig_bootstrap_cap_sizing():
    W, H = 780, 380
    f = [text(W / 2, 26, "Розмір Cbs: заряд за такт ділимо на припустиме просідання", size=15, bold=True)]

    # ── Панель A: бюджет заряду за один такт «верхній ON» ──
    ax0 = 24
    f.append(rect(ax0, 48, 350, 312, fill=BG, stroke=INK, sw=1.6, rx=12))
    f.append(text(ax0 + 175, 72, "Заряд, що витікає за один такт «верхній ON»", size=12, bold=True))
    baseY = 320
    barx, barw = ax0 + 96, 78
    scale = 6.9  # px на нКл
    f.append(line(barx - 18, baseY, ax0 + 330, baseY, color=INK, sw=1.6))  # вісь
    # Qg (низ, разово)
    qg_h = 20 * scale
    qg_top = baseY - qg_h
    f.append(rect(barx, qg_top, barw, qg_h, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    f.append(text(barx + barw / 2, (qg_top + baseY) / 2 + 5, "Qg", size=14, bold=True, color=FIELD))
    # цівка спокою+витоків (верх)
    iq_h = 9 * scale
    iq_top = qg_top - iq_h
    f.append(rect(barx, iq_top, barw, iq_h, fill="#fbeee6", stroke=POS, sw=1.6, rx=4))
    f.append(text(barx + barw / 2, (iq_top + qg_top) / 2 + 4, "Iq·t_on", size=11, bold=True, color=POS))
    # підписи праворуч від стовпчика
    lx = barx + barw + 14
    f.append(text(lx, (qg_top + baseY) / 2 - 4, "заряд затвора", size=10.5, color=INK, anchor="start"))
    f.append(text(lx, (qg_top + baseY) / 2 + 13, "20 нКл — разово", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(lx, (iq_top + qg_top) / 2 - 3, "спокій + витоки", size=10.5, color=INK, anchor="start"))
    f.append(text(lx, (iq_top + qg_top) / 2 + 14, "9 нКл — росте з t_on", size=10.5, bold=True, color=POS, anchor="start"))
    # дужка Q_total ліворуч
    f.append(line(barx - 10, iq_top, barx - 10, baseY, color=INK, sw=1.4))
    f.append(line(barx - 14, iq_top, barx - 10, iq_top, color=INK, sw=1.4))
    f.append(line(barx - 14, baseY, barx - 10, baseY, color=INK, sw=1.4))
    f.append(text(barx - 16, (iq_top + baseY) / 2 - 2, "Q_total", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(barx - 16, (iq_top + baseY) / 2 + 14, "= 29 нКл", size=10.5, bold=True, color=INK, anchor="end"))

    # ── Панель B: просідання vs розмір Cbs ──
    bx0 = 398
    f.append(rect(bx0, 48, 358, 312, fill=BG, stroke=INK, sw=1.6, rx=12))
    f.append(text(bx0 + 179, 72, "Просідання ΔV = Q_total / Cbs", size=12, bold=True))
    ox, oy = bx0 + 64, 322
    pw, ph = 250, 224
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))      # вісь Cbs
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))      # вісь ΔV
    f.append(text(ox + pw, oy + 18, "Cbs, нФ", size=10.5, color=INK, anchor="end"))
    f.append(text(ox - 6, oy - ph + 2, "ΔV, В", size=10.5, bold=True, color=INK, anchor="end"))
    cmin, cmax, vmax = 20.0, 300.0, 1.5

    def sx(c):
        return ox + (c - cmin) / (cmax - cmin) * pw

    def sy(v):
        return oy - v / vmax * ph
    # крива ΔV = 29 / Cbs
    pts, c = [], 20.0
    while c <= 300.01:
        pts.append((sx(c), sy(29.0 / c)))
        c += 5.0
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    # стеля припустимого просідання 0.3 В
    yallow = sy(0.3)
    f.append(line(ox, yallow, ox + pw, yallow, color=POS, sw=1.5, dash="6,4"))
    f.append(text(ox + pw, yallow - 6, "стеля ΔV = 0.3 В", size=10, bold=True, color=POS, anchor="end"))
    # Cbs_min на перетині (~97 нФ) + обрана точка 100 нФ
    xmin = sx(97)
    f.append(line(xmin, oy, xmin, yallow, color=MUTED, sw=1.2, dash="4,3"))
    f.append(circle(xmin, yallow, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(xmin + 9, yallow - 7, "100 нФ ✓", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(xmin, oy + 33, "Cbs_min", size=9.5, bold=True, color=INK))
    # зона «замало» (мала ємність → велике просідання)
    f.append(text(sx(46), sy(0.98), "замало:", size=10, bold=True, color=POS))
    f.append(text(sx(54), sy(0.82), "просідає нижче порога", size=9.5, color=POS))
    # позначки осі Cbs
    for cc in (50, 150, 200, 300):
        f.append(line(sx(cc), oy, sx(cc), oy + 5, color=INK, sw=1.2))
        f.append(text(sx(cc), oy + 17, str(cc), size=9.5, color=MUTED))
    return render(os.path.join(IMG, "bootstrap-cap-sizing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_above_rail()
    fig_low_vs_high()
    fig_bootstrap()
    fig_bootstrap_limit()
    fig_charge_pump()
    fig_boot_vs_pump()
    fig_halfbridge_driver()
    fig_why_pmos_on_top()
    fig_npn_drive()
    fig_bootstrap_cap_sizing()
    print("OK: why-above-rail, low-vs-high, bootstrap, bootstrap-limit, charge-pump, "
          "boot-vs-pump, halfbridge-driver, pmos-on-top, pmos-npn-drive, bootstrap-cap-sizing")
