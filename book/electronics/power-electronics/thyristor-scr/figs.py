# -*- coding: utf-8 -*-
"""Фігури до теми «Тиристор (SCR)».
П'ять фігур, на які посилається стаття:
  pnpn-two-bjt.svg   — чотири шари PNPN ↔ два зчеплені транзистори
  latch-loop.svg     — самопідтримний цикл защіпки
  iv-curve.svg       — ВАХ: блокуюча й провідна гілки, точка перемикання
  holding-current.svg— струм півхвилі гасне нижче Iн
  half-wave-circuit.svg — тиристор у мережі, керована додатна півхвиля
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви ──────────────────────────────────────────────────────
def dot(cx, cy, r=3.2, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, color)


def npn(cx, cy, label=None, lab_anchor="start", lab_dx=34):
    """NPN: планка бази (вивід ліворуч), колектор угору-праворуч, емітер
    униз-праворуч зі стрілкою назовні. Повертає (svg, xb, xc, yC, yE, yb)."""
    out = []
    bt, bb = cy - 26, cy + 26
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))
    cx2 = cx + 30
    out.append(line(cx, bt + 8, cx2, bt - 9, color=INK, sw=2))
    yC = bt - 32
    out.append(line(cx2, bt - 9, cx2, yC, color=INK, sw=2))
    out.append(line(cx, bb - 8, cx2, bb + 9, color=INK, sw=2))
    yE = bb + 32
    out.append(line(cx2, bb + 9, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 17, bb + 3, cx2, bb + 10, cx + 15, bb + 11, INK))
    if label:
        ax = cx2 + lab_dx if lab_anchor == "start" else cx - 36
        out.append(text(ax, cy + 4, label, size=12, color=INK, bold=True, anchor=lab_anchor))
    return "".join(out), cx - 30, cx2, yC, yE, cy


def pnp(cx, cy, label=None, lab_anchor="start", lab_dx=34):
    """PNP: емітер угору-праворуч зі стрілкою ВСЕРЕДИНУ (до бази), колектор
    униз-праворуч. Повертає (svg, xb, xc, yC, yE, yb): yC — кінець колектора (унизу),
    yE — кінець емітера (угорі)."""
    out = []
    bt, bb = cy - 26, cy + 26
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 30, cy, cx, cy, color=INK, sw=2))
    cx2 = cx + 30
    out.append(line(cx, bt + 8, cx2, bt - 9, color=INK, sw=2))
    yE = bt - 32
    out.append(line(cx2, bt - 9, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx2 - 2, bt - 9, cx + 15, bt + 1, cx + 16, bt + 11, INK))
    out.append(line(cx, bb - 8, cx2, bb + 9, color=INK, sw=2))
    yC = bb + 32
    out.append(line(cx2, bb + 9, cx2, yC, color=INK, sw=2))
    if label:
        ax = cx2 + lab_dx if lab_anchor == "start" else cx - 36
        out.append(text(ax, cy + 4, label, size=12, color=INK, bold=True, anchor=lab_anchor))
    return "".join(out), cx - 30, cx2, yC, yE, cy


def scr_symbol(cx, cy, scale=1.0):
    """Символ тиристора: діод (трикутник + катодна планка) з виводом затвора.
    Анод угорі, катод унизу, затвор збоку від катодної планки.
    Повертає (svg, x_anode_top, y_anode_top, x_cath_bot, y_cath_bot, x_gate, y_gate)."""
    s = scale
    out = []
    ax_t = cy - 30 * s            # верх анодного виводу
    tri_t = cy - 14 * s           # вершина трикутника зверху? ні — основа зверху
    # трикутник вістрям униз: основа вгорі, вістря торкається катодної планки
    bw = 18 * s
    base_y = cy - 13 * s
    tip_y = cy + 11 * s
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
        cx - bw, base_y, cx + bw, base_y, cx, tip_y, FILL, INK))
    # катодна планка
    bar_y = tip_y
    out.append(line(cx - bw, bar_y, cx + bw, bar_y, color=INK, sw=2.6))
    # анодний вивід
    out.append(line(cx, ax_t, cx, base_y, color=INK, sw=2))
    # катодний вивід
    cb = cy + 32 * s
    out.append(line(cx, bar_y, cx, cb, color=INK, sw=2))
    # затвор: від катодної планки косо вниз-ліворуч
    gx = cx - bw - 22 * s
    gy = bar_y + 16 * s
    out.append(line(cx - bw, bar_y, gx, gy, color=FIELD, sw=2))
    return "".join(out), cx, ax_t, cx, cb, gx, gy


def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 32, label, size=11, color=INK, bold=True))
    return "".join(out)


# ── Фігура 1: PNPN ↔ два транзистори ────────────────────────────────────────
def fig_pnpn_two_bjt():
    W, H = 820, 360
    f = [text(W / 2, 28, "Чотири шари PNPN — це два транзистори, зчеплені навхрест",
              size=16, bold=True)]

    # ── ліворуч: стовпчик шарів p-n-p-n ──
    cx = 150
    lw, lh = 120, 52
    layers = [("p", "#fdecea"), ("n", "#eaf0fd"), ("p", "#fdecea"), ("n", "#eaf0fd")]
    top = 70
    for i, (lab, col) in enumerate(layers):
        y = top + i * lh
        f.append(rect(cx - lw / 2, y, lw, lh, fill=col, stroke=INK, sw=1.6, rx=0))
        f.append(text(cx, y + lh / 2 + 6, lab, size=17, bold=True))
    # анод від верхнього p
    f.append(line(cx, top, cx, top - 22, color=POS, sw=2.4))
    f.append(text(cx, top - 28, "анод A", size=11, color=POS, bold=True))
    # катод від нижнього n
    yb = top + 4 * lh
    f.append(line(cx, yb, cx, yb + 22, color=NEG, sw=2.4))
    f.append(text(cx, yb + 36, "катод K", size=11, color=NEG, bold=True))
    # затвор від внутрішнього p (3-й шар)
    yg = top + 2 * lh + lh / 2
    f.append(line(cx - lw / 2, yg, cx - lw / 2 - 34, yg, color=FIELD, sw=2.4))
    f.append(text(cx - lw / 2 - 38, yg + 4, "затвор G", size=11, color=FIELD, bold=True, anchor="end"))
    # пунктир діагонального розрізу
    f.append(line(cx - lw / 2 - 4, top + lh, cx + lw / 2 + 4, top + 3 * lh,
                  color=MUTED, sw=1.4, dash="5,4"))
    f.append(text(cx, yb + 58, "p–n–p–n", size=13, bold=True, color=MUTED))

    # стрілка «розщепити»
    f.append(arrow(cx + lw / 2 + 18, H / 2 - 10, cx + lw / 2 + 78, H / 2 - 10, color=MUTED))
    f.append(text(cx + lw / 2 + 48, H / 2 - 18, "розщепити", size=10, color=MUTED, bold=True))

    # ── праворуч: пара транзисторів ──
    qx = 540
    f.append(text(qx + 30, 60, "PNP і NPN: колектор кожного живить базу іншого",
                  size=12, bold=True))
    # PNP угорі (емітер угорі = анод)
    psvg, pxb, pxc, pyC, pyE, pyb = pnp(qx, 130, "Q1 (PNP)")
    f.append(psvg)
    # анод до емітера PNP
    f.append(line(pxc, pyE, pxc, pyE - 18, color=POS, sw=2))
    f.append(text(pxc, pyE - 24, "A", size=11, color=POS, bold=True))
    # NPN унизу (емітер унизу = катод)
    nsvg, nxb, nxc, nyC, nyE, nyb = npn(qx, 250, "Q2 (NPN)")
    f.append(nsvg)
    f.append(line(nxc, nyE, nxc, nyE + 18, color=NEG, sw=2))
    f.append(text(nxc, nyE + 32, "K", size=11, color=NEG, bold=True))
    # колектор PNP (унизу, pyC) → база NPN (nxb, nyb): червоний дріт
    f.append(line(pxc, pyC, pxc, (pyC + nyb) / 2, color=POS, sw=1.8))
    f.append(line(pxc, (pyC + nyb) / 2, nxb - 18, (pyC + nyb) / 2, color=POS, sw=1.8))
    f.append(line(nxb - 18, (pyC + nyb) / 2, nxb - 18, nyb, color=POS, sw=1.8))
    f.append(line(nxb - 18, nyb, nxb, nyb, color=POS, sw=1.8))
    f.append(dot(pxc, pyC, color=POS))
    # колектор NPN (угорі, nyC) → база PNP (pxb, pyb): зелений дріт довкола праворуч
    rx = pxc + 70
    f.append(line(nxc, nyC, nxc, (nyC + pyb) / 2, color=FIELD, sw=1.8))
    f.append(line(nxc, (nyC + pyb) / 2, rx, (nyC + pyb) / 2, color=FIELD, sw=1.8))
    f.append(line(rx, (nyC + pyb) / 2, rx, pyb, color=FIELD, sw=1.8))
    f.append(line(rx, pyb, pxc, pyb, color=FIELD, sw=1.8))
    f.append(dot(nxc, nyC, color=FIELD))
    # затвор у базу NPN
    f.append(line(nxb - 40, nyb, nxb, nyb, color=FIELD, sw=2))
    f.append(text(nxb - 44, nyb + 4, "G", size=11, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(IMG, "pnpn-two-bjt.svg"), W, H, *f)


# ── Фігура 2: цикл защіпки ──────────────────────────────────────────────────
def fig_latch_loop():
    W, H = 800, 320
    f = [text(W / 2, 30, "Защіпка: імпульс у затвор запускає самопідтримний цикл",
              size=16, bold=True)]

    cx, cy, R = W / 2, 175, 86
    nodes = [
        ("імпульс\nу затвор", FIELD, -90),
        ("Q2 (NPN)\nтрохи відкрився", INK, -18),
        ("струм\nу базу Q1", INK, 54),
        ("Q1 (PNP) ще\nдужче відкрив Q2", INK, 126),
        ("обидва\nнасичені", POS, 198),
    ]
    pts = []
    for lab, col, ang in nodes:
        a = math.radians(ang)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        pts.append((x, y, lab, col))
    # стрілки по колу
    for i in range(len(pts)):
        x1, y1, _, _ = pts[i]
        x2, y2, _, _ = pts[(i + 1) % len(pts)]
        # скоротити до країв вузлів
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        f.append(arrow(x1 + ux * 30, y1 + uy * 22, x2 - ux * 30, y2 - uy * 22, color=MUTED))
    # вузли поверх
    for x, y, lab, col in pts:
        box, w, h = textbox(x, y, lab, size=11, color=col, bold=True,
                            fill="#ffffff", stroke=col, sw=1.8)
        f.append(box)
    f.append(text(cx, cy + 5, "ЗАМКНУТО", size=14, color=POS, bold=True))

    render(os.path.join(IMG, "latch-loop.svg"), W, H, *f)


# ── Фігура 3: ВАХ ───────────────────────────────────────────────────────────
def fig_iv_curve():
    W, H = 740, 380
    f = [text(W / 2, 28, "ВАХ тиристора: дві стійкі гілки й перемикання між ними",
              size=16, bold=True)]
    ox, oy = 370, 210                      # центр осей
    # осі
    f.append(line(60, oy, 680, oy, color=INK, sw=1.8))
    f.append(arrow(660, oy, 686, oy, color=INK))
    f.append(text(694, oy + 4, "U(A–K)", size=12, bold=True, anchor="middle"))
    f.append(line(ox, 330, ox, 56, color=INK, sw=1.8))
    f.append(arrow(ox, 70, ox, 50, color=INK))
    f.append(text(ox - 12, 56, "I", size=13, bold=True))

    # пряма блокуюча гілка: майже вздовж осі, чуть угору до Vbo
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.4"/>' % (
        ox, oy, 540, oy - 6, 620, oy - 34, MUTED))
    f.append(text(620, oy - 44, "блокує (вимкнено)", size=10, color=MUTED))
    f.append(circle(620, oy - 34, 5, fill="#fff3b0", stroke="#d98a1f", sw=2))
    f.append(text(628, oy - 22, "Vbo", size=11, color="#b5732e", bold=True, anchor="start"))
    # пунктир-перекидання на провідну
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>' % (
        620, oy - 34, 430, oy - 78, POS))
    f.append(text(498, oy - 70, "перемикання", size=10, color=POS, bold=True, anchor="start"))
    # провідна гілка: крута, біля невеликого U
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="3"/>' % (
        404, oy - 64, 412, 78, FIELD))
    f.append(text(420, 90, "проводить (увімкнено)", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(396, oy - 72, "Vt ≈ 1…1.5 В", size=10, color=FIELD, bold=True, anchor="end"))
    # точка Iн на провідній гілці
    f.append(circle(406, oy - 50, 5, fill="#cdeccd", stroke=FIELD, sw=2))
    f.append(text(392, oy - 46, "Iн", size=11, color=FIELD, bold=True, anchor="end"))
    # імпульс затвора підпис
    f.append(text(560, oy + 22, "↑ U або імпульс затвора", size=10, color=FIELD, bold=True))

    # зворотна гілка: блокує до пробою
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.4"/>' % (
        ox, oy, 120, oy + 8, NEG))
    f.append(text(220, oy + 24, "зворотна: блокує", size=10, color=NEG))
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>' % (
        120, oy + 8, 112, oy + 62, NEG))
    f.append(text(112, oy + 78, "лавинний пробій", size=9.5, color=NEG))

    render(os.path.join(IMG, "iv-curve.svg"), W, H, *f)


# ── Фігура 4: утримуючий струм ──────────────────────────────────────────────
def fig_holding_current():
    W, H = 820, 330
    f = [text(W / 2, 28, "Вимикається сам: коли струм півхвилі падає нижче Iн",
              size=16, bold=True)]
    ox, oy = 80, 250
    f.append(line(ox, oy, ox, 50, color=INK, sw=1.8))
    f.append(arrow(ox, 64, ox, 46, color=INK))
    f.append(line(ox, oy, 690, oy, color=INK, sw=1.8))
    f.append(arrow(672, oy, 694, oy, color=INK))
    f.append(text(700, oy + 4, "t", size=13, bold=True, anchor="start"))
    f.append(text(ox, 42, "I через тиристор", size=12, bold=True))

    # півхвиля синуса від 80 до 660
    x0, x1 = 98, 660
    amp = 150
    pts = []
    n = 200
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ph = math.pi * i / n
        y = oy - amp * math.sin(ph)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>' % (
        " L ".join(pts), POS))

    # лінія Iн
    iy = oy - 22
    f.append(line(ox, iy, 660, iy, color=FIELD, sw=1.6, dash="6,4"))
    f.append(text(674, iy + 4, "Iн (утрим.)", size=10, color=FIELD, bold=True, anchor="start"))

    # точка старту (імпульс)
    sy = oy - amp * math.sin(math.pi * (x0 + 16 - x0) / (x1 - x0))  # приблизно
    f.append(circle(x0 + 14, iy - 4, 5.5, fill="#cdeccd", stroke=FIELD, sw=2))
    f.append(arrow(x0 + 14, oy + 36, x0 + 14, iy + 4, color=FIELD))
    f.append(text(x0 + 14, oy + 52, "імпульс затвора → ON", size=10, color=FIELD, bold=True))

    # точка згасання (де синус знову перетинає Iн на спаді)
    # sin(ph)=22/150 → ph = pi - asin(0.1467)
    ph_off = math.pi - math.asin(22.0 / amp)
    xoff = x0 + (x1 - x0) * ph_off / math.pi
    f.append(circle(xoff, iy, 5.5, fill="#fdecea", stroke=POS, sw=2))
    f.append(arrow(xoff + 60, iy - 44, xoff + 4, iy - 4, color=POS))
    f.append(text(xoff + 64, iy - 50, "I < Iн → защіпка зривається → OFF",
                  size=10, color=POS, bold=True, anchor="start"))

    # смуги «проводить» / «закрито»
    f.append(line(x0 + 14, oy + 8, xoff, oy + 8, color=FIELD, sw=3))
    f.append(text((x0 + 14 + xoff) / 2, oy + 22, "проводить", size=10, color=FIELD, bold=True))
    f.append(text((xoff + 660) / 2, oy + 22, "закрито", size=10, color=NEG, bold=True))

    render(os.path.join(IMG, "holding-current.svg"), W, H, *f)


# ── Фігура 5: тиристор у мережі ─────────────────────────────────────────────
def fig_half_wave_circuit():
    W, H = 720, 300
    f = [text(W / 2, 26, "Тиристор у мережі: керована додатна півхвиля на лампі",
              size=15, bold=True)]

    topY, botY = 80, 232
    # джерело ~230 В ліворуч
    sx = 100
    f.append(circle(sx, 156, 24, fill=BG, stroke=INK, sw=2))
    # синус усередині кола
    spts = []
    for i in range(0, 31):
        x = sx - 15 + i
        y = 156 - 11 * math.sin(2 * math.pi * (i / 30.0))
        spts.append("%.1f,%.1f" % (x, y))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2"/>' % (" L ".join(spts), INK))
    f.append(text(sx - 32, 160, "~230 В", size=10, bold=True, anchor="end"))
    f.append(line(sx, topY, sx, 132, color=INK, sw=2))
    f.append(line(sx, 180, sx, botY, color=INK, sw=2))

    # верхній дріт до тиристора
    tx = 330
    f.append(line(sx, topY, tx, topY, color=INK, sw=2))
    # символ тиристора (анод угорі)
    svg, axt, ayt, cxb, cyb, gx, gy = scr_symbol(tx, 118, scale=1.15)
    f.append(svg)
    f.append(line(tx, topY, tx, ayt, color=INK, sw=2))
    f.append(text(tx - 26, topY + 6, "A", size=10, color=POS, bold=True, anchor="end"))
    f.append(text(tx + 26, cyb - 6, "K", size=10, color=NEG, bold=True, anchor="start"))
    # запуск у затвор
    f.append(line(gx, gy, gx, gy + 40, color=FIELD, sw=2))
    f.append(rect(gx - 62, gy + 40, 124, 36, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(gx, gy + 57, "запуск", size=10, color=FIELD, bold=True))
    f.append(text(gx, gy + 71, "(від МК, через розв'язку)", size=9, color=MUTED))

    # катод → навантаження (лампа) → назад
    lx = 580
    f.append(line(tx, cyb, lx, cyb, color=INK, sw=2))
    f.append(line(lx, cyb, lx, 137, color=INK, sw=2))
    f.append(circle(lx, 156, 18, fill="#fff6cf", stroke=INK, sw=2))
    f.append(line(lx - 9, 165, lx + 9, 147, color=INK, sw=1.6))
    f.append(line(lx - 9, 147, lx + 9, 165, color=INK, sw=1.6))
    f.append(text(lx + 26, 160, "лампа", size=10, anchor="start"))
    f.append(line(lx, 174, lx, botY, color=INK, sw=2))
    # нижній зворотний дріт
    f.append(line(sx, botY, lx, botY, color=INK, sw=2))

    render(os.path.join(IMG, "half-wave-circuit.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pnpn_two_bjt()
    fig_latch_loop()
    fig_iv_curve()
    fig_holding_current()
    fig_half_wave_circuit()
    print("OK: pnpn-two-bjt, latch-loop, iv-curve, holding-current, half-wave-circuit -> img/")
