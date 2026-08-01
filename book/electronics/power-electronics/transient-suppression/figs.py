# -*- coding: utf-8 -*-
"""Фігури для статті «Придушення перехідних стрибків напруги».
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── локальні гліфи схеми (svgkit не чіпаємо) ────────────────────────────────
def coil(x, y0, y1, n=4, side=1):
    """Вертикальна котушка з бампами (напрямок side=+1/−1) від y0 до y1."""
    r = (y1 - y0) / (2 * n)
    d = "M %.1f %.1f " % (x, y0)
    for _ in range(n):
        d += "a %.1f %.1f 0 0 %d 0 %.1f " % (r, r, 1 if side > 0 else 0, 2 * r)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def diode_up(cx, cy, s=13, color=INK):
    """Діод, що проводить угору (анод знизу, катод-риска зверху)."""
    tri = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" '
           'stroke="%s" stroke-width="1.6"/>' % (cx - s, cy + s, cx + s, cy + s,
                                                 cx, cy - s, "#fdecea" if color == POS else FILL, color))
    bar = line(cx - s, cy - s, cx + s, cy - s, color=color, sw=2.4)
    return tri + bar


def gnd(cx, cy):
    return (line(cx, cy, cx, cy + 6, color=INK, sw=2) +
            line(cx - 13, cy + 6, cx + 13, cy + 6, color=INK, sw=2) +
            line(cx - 8, cy + 11, cx + 8, cy + 11, color=INK, sw=2) +
            line(cx - 3, cy + 16, cx + 3, cy + 16, color=INK, sw=2))


def bolt(x0, y0, x1, y1, color=POS):
    """Зигзаг-блискавка (пробій)."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
        x0, y0, mx + 9, my - 6, mx - 9, my + 6, x1, y1)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, color)


def fig_mechanism():
    """Два кола поруч: без гасильного діода стрибок пробиває ключ; із діодом
    струм замикається в колечко, напруга на ключі впадає до живлення+0.7 В."""
    W, H = 940, 480
    f = []

    def panel(cx, title, with_diode):
        p = []
        railY, coilY0, coilY1, nodeY, swY, gndY = 95, 132, 242, 272, 335, 415
        left = cx - 60          # вертикаль кола
        # верхня шина живлення
        p.append(line(left - 48, railY, left + 150, railY, color=POS, sw=2.4))
        p.append(text(left - 56, railY + 5, "+12 В", size=13, color=POS,
                      anchor="end", bold=True))
        # провід у котушку
        p.append(line(left, railY, left, coilY0, color=INK, sw=2))
        p.append(coil(left, coilY0, coilY1))
        p.append(text(left - 28, (coilY0 + coilY1) / 2 + 5, "L", size=16,
                      color=INK, anchor="end", bold=True))
        # вузол А (низ котушки → ключ)
        p.append(line(left, coilY1, left, swY - 24, color=INK, sw=2))
        p.append(circle(left, nodeY, 3.4, fill=INK, stroke=INK))
        # ключ
        bsw, wsw, hsw = textbox(left, swY, "ключ\n(розімкнено)", size=12,
                                fill=FILL, stroke=INK, sw=2)
        p.append(bsw)
        p.append(line(left, swY + hsw / 2, left, gndY, color=INK, sw=2))
        p.append(gnd(left, gndY))

        if not with_diode:
            # стрибок угору + пробій крізь ключ
            p.append(arrow(left + 22, nodeY, left + 22, railY - 8, color=POS, sw=2.6))
            bx, _, _ = textbox(left + 82, nodeY - 8, "стрибок\n↑↑↑", size=13,
                               fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True)
            p.append(bx)
            p.append(bolt(left - 4, swY - 6, left - 4, swY + 6, color=POS))
            p.append(text(left - 26, swY + 48, "пробій", size=12, color=POS,
                          anchor="end", italic=True))
        else:
            # гасильний діод: анод — вузол А (низ котушки), катод — шина +12 В;
            # струм рециркулює вузол А → діод угору → шина → котушка.
            dx = left + 80
            dcy = 190                     # центр діода
            p.append(line(left, coilY1, dx, coilY1, color=FIELD, sw=2.2))
            p.append(line(dx, coilY1, dx, dcy + 13, color=FIELD, sw=2.2))
            p.append(diode_up(dx, dcy, s=13, color=FIELD))
            p.append(line(dx, dcy - 13, dx, railY, color=FIELD, sw=2.2))
            p.append(text(dx + 18, dcy - 4, "гасильний", size=12,
                          color=FIELD, anchor="start", bold=True))
            p.append(text(dx + 18, dcy + 13, "діод", size=12,
                          color=FIELD, anchor="start", bold=True))
            # напруга на вузлі затиснута
            p.append(text(left - 26, nodeY + 4, "+12.7 В", size=12, color=FIELD,
                          anchor="end", bold=True))
            p.append(text(left + 74, swY + 4, "ключ у безпеці", size=12,
                          color=FIELD, anchor="start", italic=True))
        # заголовок панелі
        p.append(text(cx, 58, title, size=15, bold=True,
                      color=POS if not with_diode else FIELD))
        return p

    f += panel(212, "Без діода", False)
    f += panel(702, "З гасильним діодом", True)
    # роздільник
    f.append(line(462, 78, 462, H - 30, color=MUTED, sw=1.2, dash="6 6"))

    render(os.path.join(IMG, "kickback-mechanism.svg"), W, H, *f,
           title="Куди подіти струм котушки в мить розмикання")
    return "mechanism"


def fig_waveforms():
    """Напруга на ключі після вимкнення: без обмеження (викид+дзвін),
    з діодом (низька довга поличка), з діодом+стабілітроном (вища коротка)."""
    W, H = 900, 470
    f = []
    # осі
    ox, oy = 90, 380          # початок координат
    axW, axH = 740, 300
    f.append(arrow(ox, oy, ox, oy - axH - 10, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 10, oy, color=INK, sw=1.8))
    f.append(text(ox - 12, oy - axH - 6, "напруга на ключі", size=13,
                  color=INK, anchor="start"))
    f.append(text(ox + axW + 4, oy + 20, "час", size=13, color=INK, anchor="end"))

    # рівень живлення Vcc
    vcc = oy - 60
    f.append(line(ox, vcc, ox + axW, vcc, color=MUTED, sw=1.3, dash="7 6"))
    f.append(text(ox - 8, vcc + 4, "живлення", size=11, color=MUTED, anchor="end"))

    t0 = ox + 120            # момент вимкнення
    f.append(line(t0, oy, t0, oy - axH, color=MUTED, sw=1.1, dash="3 5"))
    f.append(text(t0, oy + 20, "вимкнення", size=11, color=MUTED))

    # до вимкнення струм тече, напруга на ключі ≈ 0 (лежить на осі) — усі однакові
    base = oy - 4
    f.append(line(ox, base, t0, base, color=INK, sw=2))

    # A: без обмеження — гострий викид + згасальний дзвін
    top = oy - axH + 8
    ptsA = [(t0, base)]
    ptsA.append((t0 + 10, top))          # злітає за межі
    # дзвін
    for k in range(0, 90):
        tt = t0 + 20 + k * 3.0
        env = math.exp(-k / 22.0)
        v = vcc - (vcc - top) * env * math.cos(k / 3.4)
        if v > oy - 4:
            v = oy - 4
        ptsA.append((tt, v))
        if tt > ox + axW - 6:
            break
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ptsA), POS))
    f.append(text(t0 + 26, top - 2, "без обмеження", size=12, color=POS,
                  anchor="start", bold=True))

    # B: з діодом — низька поличка (Vcc+0.7), дуже довгий спад до Vcc
    blvl = vcc - 16
    ptsB = [(t0, base), (t0 + 8, blvl)]
    for k in range(0, 120):
        tt = t0 + 8 + k * 4.6
        v = vcc - 16 * math.exp(-k / 70.0)   # дуже повільний спад
        ptsB.append((tt, v))
        if tt > ox + axW - 6:
            break
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ptsB), NEG))
    f.append(text(ox + axW - 6, blvl - 8, "діод: низько, але довго", size=12,
                  color=NEG, anchor="end", bold=True))

    # C: діод+стабілітрон — вища поличка, коротка
    clvl = vcc - 70
    ptsC = [(t0, base), (t0 + 8, clvl)]
    # тримається до tc, тоді круто до Vcc
    tc = t0 + 150
    ptsC.append((tc, clvl))
    ptsC.append((tc + 26, vcc - 3))
    ptsC.append((ox + axW - 6, vcc - 3))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ptsC), FIELD))
    f.append(text(t0 + 16, clvl - 8, "діод+стабілітрон: вище, зате коротко",
                  size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, "clamp-waveforms.svg"), W, H, *f,
           title="Терези захисту: висота стрибка проти тривалості спаду")
    return "waveforms"


def fig_fizeau():
    """Історична вставка: перериватель індукційної котушки 1830-х (дуга з'їдає
    контакти) і доробка Фізо 1853-го (конденсатор упоперек контактів)."""
    W, H = 980, 480
    f = []
    ytop, ybot = 150, 370

    def battery(x, cy):
        """Гальванічна батарея на вертикальному проводі (пластини горизонтальні)."""
        p = []
        for i, half in enumerate((14, 7, 14, 7)):
            yy = cy - 15 + i * 10
            p.append(line(x - half, yy, x + half, yy, color=INK,
                          sw=2.6 if half > 10 else 2.0))
        return p

    def panel(cx, title, tcolor, fixed):
        p = []
        xl, xr = cx - 130, cx + 110
        gx1, gx2 = cx - 32, cx + 8          # краї контактного проміжку
        p.append(text(cx, 62, title, size=15, bold=True, color=tcolor))

        # ліва вертикаль із батареєю
        p.append(line(xl, ytop, xl, 233, color=INK, sw=2))
        p += battery(xl, 253)
        p.append(line(xl, 273, xl, ybot, color=INK, sw=2))
        p.append(text(xl - 24, 258, "батарея", size=12, color=INK, anchor="end"))

        # низ і права вертикаль з електромагнітом
        p.append(line(xl, ybot, xr, ybot, color=INK, sw=2))
        p.append(line(xr, ybot, xr, 320, color=INK, sw=2))
        p.append(coil(xr, 200, 320))
        p.append(line(xr, 200, xr, ytop, color=INK, sw=2))
        p.append(text(xr + 20, 264, "електромагніт", size=12, color=INK,
                      anchor="start"))

        # верх із розімкненим переривачем
        p.append(line(xl, ytop, gx1, ytop, color=INK, sw=2))
        p.append(line(gx2, ytop, xr, ytop, color=INK, sw=2))
        p.append(line(gx1, ytop, gx1 + 26, ytop - 17, color=INK, sw=2.4))
        p.append(circle(gx1, ytop, 3.4, fill=INK, stroke=INK))
        p.append(line(gx2, ytop - 9, gx2, ytop + 9, color=INK, sw=2.4))
        p.append(text(cx - 12, 108, "перериватель", size=12, bold=True, color=INK))

        if not fixed:
            p.append(bolt(gx1 + 6, ytop + 2, gx2 - 3, ytop + 2, color=POS))
            p.append(mtext(cx - 10, ytop + 62,
                           ["контакти обгоряють,",
                            "спад поля затягується"],
                           size=12.5, color=POS))
        else:
            ycap = ytop + 58
            p.append(line(gx1, ytop, gx1, ycap, color=FIELD, sw=2.2))
            p.append(line(gx1, ycap, cx - 14, ycap, color=FIELD, sw=2.2))
            p.append(line(cx - 14, ycap - 15, cx - 14, ycap + 15, color=FIELD, sw=2.8))
            p.append(line(cx - 2, ycap - 15, cx - 2, ycap + 15, color=FIELD, sw=2.8))
            p.append(line(cx - 2, ycap, gx2, ycap, color=FIELD, sw=2.2))
            p.append(line(gx2, ycap, gx2, ytop, color=FIELD, sw=2.2))
            p.append(text(cx - 8, ycap + 40, "конденсатор Фізо", size=12.5,
                          bold=True, color=FIELD))
            p.append(text(cx - 8, ycap + 62, "струм іде сюди, а не в дугу",
                          size=12, color=FIELD, italic=True))
        return p

    f += panel(250, "Індукційна котушка, 1830-ті", POS, False)
    f += panel(730, "Доробка Фізо, 1853", FIELD, True)
    f.append(text(250, 432, "дуга з'їдає контакти й краде напругу", size=13,
                  color=POS, italic=True))
    f.append(text(730, 432, "напруга наростає повільно — дуга не займається",
                  size=13, color=FIELD, italic=True))
    f.append(line(490, 82, 490, H - 34, color=MUTED, sw=1.2, dash="6 6"))

    render(os.path.join(IMG, "fizeau-interrupter.svg"), W, H, *f,
           title="Перериватель індукційної котушки до і після конденсатора Фізо")
    return "fizeau"


def cap_plates(cx, cy, w=34, gap=12, color=INK):
    """Горизонтальні пластини конденсатора з центром (cx, cy)."""
    return (line(cx - w / 2, cy - gap / 2, cx + w / 2, cy - gap / 2, color=color, sw=2.6) +
            line(cx - w / 2, cy + gap / 2, cx + w / 2, cy + gap / 2, color=color, sw=2.6))


def pline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── фігури математичної вставки ─────────────────────────────────────────────
def fig_lc_ceiling():
    """Стелю вільного викиду ставить не швидкість ключа, а паразитна ємність:
    ½L·I² перетікає в ½C·V², звідки пік I₀·√(L/C) через чверть періоду."""
    W, H = 980, 540
    f = []

    # ── ліворуч: куди тече струм, коли ключ розімкнено ──────────────────────
    left = 150
    railY, c0, c1, nodeY, swY, gndY = 120, 158, 268, 302, 372, 462
    f.append(line(left - 52, railY, left + 40, railY, color=POS, sw=2.4))
    f.append(text(left - 60, railY + 5, "+12 В", size=13, color=POS,
                  anchor="end", bold=True))
    f.append(line(left, railY, left, c0, color=INK, sw=2))
    f.append(coil(left, c0, c1))
    f.append(text(left - 28, (c0 + c1) / 2 - 4, "L", size=16, color=INK,
                  anchor="end", bold=True))
    f.append(text(left - 28, (c0 + c1) / 2 + 17, "100 мГн", size=11, color=MUTED,
                  anchor="end"))
    f.append(line(left, c1, left, swY - 28, color=INK, sw=2))
    f.append(circle(left, nodeY, 3.4, fill=INK, stroke=INK))
    bsw, _, hsw = textbox(left, swY, "ключ\nрозімкнено", size=12,
                          fill=FILL, stroke=INK, sw=2)
    f.append(bsw)
    f.append(line(left, swY + hsw / 2, left, gndY, color=INK, sw=2))
    f.append(gnd(left, gndY))
    # єдина дорога — паразитна ємність
    capX = left + 140
    f.append(line(left, nodeY, capX, nodeY, color=NEG, sw=2.4))
    f.append(arrow(capX, nodeY, capX, nodeY + 46, color=NEG, sw=2.4))
    f.append(cap_plates(capX, nodeY + 62, color=NEG))
    f.append(line(capX, nodeY + 68, capX, gndY, color=NEG, sw=2.4))
    f.append(gnd(capX, gndY))
    f.append(text(capX + 24, nodeY + 56, "Cпар", size=13, color=NEG,
                  anchor="start", bold=True))
    f.append(text(capX + 24, nodeY + 74, "≈ 100 пФ", size=11, color=NEG,
                  anchor="start"))
    f.append(mtext(left + 70, nodeY - 30, ["струмові лишилась", "одна дорога"],
                   size=11.5, color=NEG))
    f.append(text(180, 84, "Розімкнений ключ — це ємність", size=14,
                  bold=True, color=INK))

    # ── праворуч: чверть періоду обміну ─────────────────────────────────────
    ox, oy = 500, 452
    axW, axH = 420, 306
    f.append(arrow(ox, oy, ox, oy - axH - 16, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 18, oy, color=INK, sw=1.8))
    f.append(text(ox + axW + 14, oy + 24, "час", size=12, color=INK, anchor="end"))

    tpk = ox + 250                       # чверть періоду
    vtop = oy - axH + 16
    ipk = oy - 172
    n = 60
    ptsV, ptsI = [], []
    for k in range(n + 1):
        u = k / float(n)                 # частка чверті періоду
        xx = ox + (tpk - ox) * u
        ptsV.append((xx, oy - (oy - vtop) * math.sin(u * math.pi / 2)))
        ptsI.append((xx, oy - (oy - ipk) * math.cos(u * math.pi / 2)))
    f.append(pline(ptsV, color=POS, sw=2.6))
    f.append(pline(ptsI, color=NEG, sw=2.6))
    # згасальне продовження — пунктиром
    ptsD = []
    for k in range(0, 60):
        u = 1 + k / 30.0
        xx = ox + (tpk - ox) * u
        if xx > ox + axW:
            break
        env = math.exp(-(u - 1) * 0.30)
        ptsD.append((xx, oy - (oy - vtop) * math.sin(u * math.pi / 2) * env))
    f.append(pline(ptsD, color=POS, sw=1.8, dash="5 5"))

    f.append(line(ox, vtop, tpk, vtop, color=MUTED, sw=1.2, dash="6 5"))
    f.append(line(tpk, oy, tpk, vtop, color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(ox - 10, vtop + 5, "3.2 кВ", size=12, color=POS,
                  anchor="end", bold=True))
    f.append(text(ox - 10, ipk + 5, "100 мА", size=12, color=NEG,
                  anchor="end", bold=True))
    f.append(text(tpk, oy + 24, "5 мкс", size=12, color=MUTED))
    f.append(text(ox + 10, oy + 24, "0", size=12, color=MUTED, anchor="start"))

    f.append(text(ox + 60, ipk - 16, "струм котушки", size=12, color=NEG,
                  anchor="start", bold=True))
    f.append(text(tpk + 18, vtop + 30, "напруга", size=12, color=POS,
                  anchor="start", bold=True))
    f.append(text(tpk + 18, vtop + 47, "на ключі", size=12, color=POS,
                  anchor="start", bold=True))

    bx, _, _ = textbox(ox + 176, oy - 56, "½·L·I₀²  →  ½·C·V²", size=14,
                       fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    f.append(bx)
    f.append(text(710, 84, "Уся енергія переїжджає в ємність", size=14,
                  bold=True, color=INK))

    render(os.path.join(IMG, "lc-ceiling.svg"), W, H, *f,
           title="Пік ставить не ключ, а паразитна ємність: V = I₀·√(L/C)")
    return "lc-ceiling"


def fig_energy_split():
    """Яка частка ½L·I₀² дістається обмежувачу залежно від того, наскільки
    його падіння сильніше за резистивне падіння на самій обмотці."""
    W, H = 960, 540
    f = []
    ox, oy = 150, 412
    axW, axH = 700, 296
    f.append(arrow(ox, oy, ox, oy - axH - 18, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 18, oy, color=INK, sw=1.8))

    def X(x):                       # лог-вісь: x від 0.01 до 100
        return ox + axW * (math.log10(x) + 2) / 4.0

    def Y(e):
        return oy - axH * e

    for dec, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        f.append(line(X(dec), oy, X(dec), oy - 8, color=MUTED, sw=1.2))
        f.append(text(X(dec), oy + 24, lab, size=12, color=MUTED))
    for e, lab in ((0.25, "25 %"), (0.5, "50 %"), (0.75, "75 %"), (1.0, "100 %")):
        f.append(line(ox, Y(e), ox + 8, Y(e), color=MUTED, sw=1.2))
        f.append(text(ox - 14, Y(e) + 5, lab, size=12, color=MUTED, anchor="end"))

    pts = []
    for k in range(0, 241):
        x = 10 ** (-2 + 4.0 * k / 240)
        eta = 2 * (x - math.log(1 + x)) / (x * x)
        pts.append((X(x), Y(eta)))
    f.append(pline(pts, color=FIELD, sw=3.0))

    def mark(x, lab, lab2, dx, dy, color):
        eta = 2 * (x - math.log(1 + x)) / (x * x)
        anc = "start" if dx > 0 else "end"
        f.append(circle(X(x), Y(eta), 6, fill=color, stroke=color))
        f.append(text(X(x) + dx, Y(eta) + dy, lab, size=12, color=color,
                      anchor=anc, bold=True))
        f.append(text(X(x) + dx, Y(eta) + dy + 18, lab2, size=11, color=color,
                      anchor=anc))

    mark(0.486, "діод + стабілітрон 24 В", "76 % → 381 мкДж", 18, -40, POS)
    mark(17.14, "лише діод 0.7 В", "9.7 % → 48 мкДж", 18, -32, NEG)

    f.append(text(ox + axW / 2, oy + 56,
                  "x = I₀·R / Vобм   —   падіння на обмотці проти падіння на обмежувачі",
                  size=13, color=INK))
    f.append(text(ox - 118, oy - axH - 34,
                  "частка ½·L·I₀², що дістається обмежувачу",
                  size=13, color=INK, anchor="start"))

    f.append(mtext(X(0.055), Y(0.26),
                   ["обмежувач сильніший —", "забирає майже все"],
                   size=11.5, color=MUTED))
    f.append(mtext(X(28), Y(0.60),
                   ["обмотка сильніша —", "гріється сама"],
                   size=11.5, color=MUTED))

    render(os.path.join(IMG, "clamp-energy-split.svg"), W, H, *f,
           title="Частка енергії обмежувачу: η = 2·[x − ln(1+x)] / x²")
    return "energy-split"


def fig_decay_race():
    """За однакового піка 24 В стабілітрон садить струм удвічі швидше:
    резистор слабшає разом зі струмом, стабілітрон тисне на повну до нуля."""
    W, H = 960, 520
    f = []
    ox, oy = 140, 400
    axW, axH = 700, 282
    Tmax = 800e-6          # вісь часу, с
    f.append(arrow(ox, oy, ox, oy - axH - 18, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 18, oy, color=INK, sw=1.8))

    def X(t):
        return ox + axW * t / Tmax

    def Y(i):
        return oy - axH * i / 0.1

    for t in (200e-6, 400e-6, 600e-6, 800e-6):
        f.append(text(X(t), oy + 26, "%d мкс" % round(t * 1e6), size=12, color=MUTED))
        f.append(line(X(t), oy, X(t), oy - 7, color=MUTED, sw=1.2))
    f.append(text(ox - 14, Y(0.1) + 5, "100 мА", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 14, Y(0.01) + 5, "10 мА", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 14, Y(0) + 5, "0", size=12, color=MUTED, anchor="end"))
    f.append(line(ox, Y(0.01), ox + axW, Y(0.01), color=MUTED, sw=1.1, dash="5 6"))

    Lh, I0, Rc = 0.1, 0.1, 120.0
    tauR = Lh / (Rc + 240.0)          # резистор 240 Ом у колечку
    ptsR = [(X(k * Tmax / 200), Y(I0 * math.exp(-(k * Tmax / 200) / tauR)))
            for k in range(201)]
    f.append(pline(ptsR, color=NEG, sw=2.8))

    tau, a = Lh / Rc, 24.0 / Rc       # стабілітрон 24 В
    ptsZ = []
    for k in range(0, 201):
        t = k * Tmax / 200
        i = (I0 + a) * math.exp(-t / tau) - a
        if i < 0:
            ptsZ.append((X(t), Y(0)))
            break
        ptsZ.append((X(t), Y(i)))
    f.append(pline(ptsZ, color=POS, sw=2.8))

    f.append(circle(X(337.9e-6), Y(0), 6, fill=POS, stroke=POS))
    f.append(text(X(337.9e-6) + 14, Y(0) - 14, "нуль за 338 мкс", size=12,
                  color=POS, anchor="start", bold=True))
    f.append(circle(X(639.6e-6), Y(0.01), 6, fill=NEG, stroke=NEG))
    f.append(text(X(639.6e-6) + 14, Y(0.01) - 16, "10 % аж за 640 мкс", size=12,
                  color=NEG, anchor="end", bold=True))

    f.append(text(X(96e-6), Y(0.082), "резистор 240 Ом", size=13,
                  color=NEG, anchor="start", bold=True))
    f.append(text(X(96e-6), Y(0.082) + 19, "гальмо слабшає зі струмом", size=11.5,
                  color=NEG, anchor="start", italic=True))
    f.append(text(X(330e-6), Y(0.056), "стабілітрон 24 В", size=13,
                  color=POS, anchor="start", bold=True))
    f.append(text(X(330e-6), Y(0.056) + 19, "гальмо тримає повну силу", size=11.5,
                  color=POS, anchor="start", italic=True))
    f.append(text(ox - 106, oy - axH - 36, "струм котушки", size=13, color=INK,
                  anchor="start"))

    render(os.path.join(IMG, "clamp-decay-race.svg"), W, H, *f,
           title="Однаковий пік 24 В — удвічі різний час згасання")
    return "decay-race"


if __name__ == "__main__":
    print(fig_mechanism())
    print(fig_waveforms())
    print(fig_fizeau())
    print(fig_lc_ceiling())
    print(fig_energy_split())
    print(fig_decay_race())
    print("Готово:", IMG)
