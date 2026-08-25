# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def nmos(cx, cy, on=True, scale=1.0):
    """Простий символ n-канального MOSFET (збагачений), вивід затвора зліва.
    Повертає фрагмент + координати виводів D (зверху), S (знизу), G (зліва)."""
    s = scale
    chan_x = cx
    d_y = cy - 38 * s          # сток (зверху)
    s_y = cy + 38 * s          # витік (знизу)
    g_x = cx - 52 * s          # затвор (зліва)
    col = FIELD if on else MUTED
    out = []
    # вертикальний канал (три рисочки збагаченого приладу)
    bar_x = chan_x - 6 * s
    for yy in (cy - 22 * s, cy, cy + 22 * s):
        out.append(line(bar_x, yy - 9 * s, bar_x, yy + 9 * s, color=col, sw=3))
    # пластина затвора
    gate_plate_x = bar_x - 9 * s
    out.append(line(gate_plate_x, cy - 30 * s, gate_plate_x, cy + 30 * s, color=INK, sw=2.5))
    out.append(line(g_x, cy, gate_plate_x, cy, color=INK, sw=2))
    # сток: верхня рисочка → вгору
    out.append(line(chan_x, cy - 22 * s, chan_x, d_y, color=INK, sw=2))
    out.append(line(bar_x, cy - 22 * s, chan_x, cy - 22 * s, color=INK, sw=2))
    # витік: нижня рисочка → вниз
    out.append(line(chan_x, cy + 22 * s, chan_x, s_y, color=INK, sw=2))
    out.append(line(bar_x, cy + 22 * s, chan_x, cy + 22 * s, color=INK, sw=2))
    # стрілка тіла-витоку всередину (n-канал)
    out.append(line(bar_x, cy, chan_x, cy, color=INK, sw=2))
    out.append(arrow(bar_x + 2 * s, cy, chan_x, cy, color=INK))
    return "".join(out), (chan_x, d_y), (chan_x, s_y), (g_x, cy)


# ── Фігура 1: дві крайні точки — затвор-напруга замикає/розмикає шлях ─────────
def fig_two_states():
    W, H = 720, 360
    parts = []
    # ─ ліва панель: ВИМКНЕНО ─
    bx = 70
    parts.append(text(180, 56, "Затвор низький → канал зник", size=15, bold=True, color=MUTED))
    sym, D, S, G = nmos(180, 190, on=False)
    parts.append(sym)
    # рейка живлення, навантаження, земля
    parts.append(line(180, 90, 180, D[1], color=LINE, sw=2))
    parts.append(text(180, 84, "+12 В", size=13, color=POS))
    parts.append(line(180, S[1], 180, 300, color=LINE, sw=2))
    parts.append(line(150, 300, 210, 300, color=INK, sw=3))  # земля
    parts.append(line(160, 306, 200, 306, color=INK, sw=2))
    parts.append(line(170, 311, 190, 311, color=INK, sw=2))
    # затвор на 0
    parts.append(line(G[0], G[1], 70, G[1], color=LINE, sw=2))
    parts.append(text(58, G[1] + 4, "0 В", size=13, anchor="end", color=NEG))
    # навантаження (лампа) — символ кола з хрестиком
    parts.append(circle(180, 130, 17, fill="#f0f0f0", stroke=MUTED, sw=2))
    parts.append(line(168, 118, 192, 142, color=MUTED, sw=1.5))
    parts.append(line(192, 118, 168, 142, color=MUTED, sw=1.5))
    parts.append(text(225, 134, "не світить", size=12, anchor="start", color=MUTED))
    # розрив
    b1, _, _ = textbox(180, 250, "розімкнено", size=12, color=MUTED, stroke=MUTED)
    parts.append(b1)

    # ─ права панель: УВІМКНЕНО ─
    parts.append(text(540, 56, "Затвор високий → канал відкрито", size=15, bold=True, color=FIELD))
    sym, D, S, G = nmos(540, 190, on=True)
    parts.append(sym)
    parts.append(line(540, 90, 540, D[1], color=LINE, sw=2))
    parts.append(text(540, 84, "+12 В", size=13, color=POS))
    parts.append(line(540, S[1], 540, 300, color=LINE, sw=2))
    parts.append(line(510, 300, 570, 300, color=INK, sw=3))
    parts.append(line(520, 306, 560, 306, color=INK, sw=2))
    parts.append(line(530, 311, 550, 311, color=INK, sw=2))
    parts.append(line(G[0], G[1], 430, G[1], color=LINE, sw=2))
    parts.append(text(418, G[1] + 4, "+10 В", size=13, anchor="end", color=POS))
    parts.append(circle(540, 130, 17, fill="#fff6cc", stroke=POS, sw=2))
    parts.append(line(528, 118, 552, 142, color=POS, sw=1.5))
    parts.append(line(552, 118, 528, 142, color=POS, sw=1.5))
    parts.append(text(585, 134, "світить", size=12, anchor="start", color=POS))
    b2, _, _ = textbox(540, 250, "струм тече", size=12, color=FIELD, stroke=FIELD)
    parts.append(b2)

    # роздільник
    parts.append(line(360, 70, 360, 330, color="#dddddd", sw=1.5, dash="5,5"))
    render(os.path.join(IMG, 'two-states.svg'), W, H, *parts)


# ── Фігура 2: ключ нижнього плеча на n-MOSFET ────────────────────────────────
def fig_low_side():
    W, H = 640, 420
    parts = []
    cx = 360
    sym, D, S, G = nmos(cx, 250, on=True)
    parts.append(sym)
    # рейка +
    rail_y = 60
    parts.append(line(120, rail_y, 560, rail_y, color=POS, sw=2.5))
    parts.append(text(120, rail_y - 10, "+ живлення (напр. 12 В)", size=13, anchor="start", color=POS))
    # навантаження між рейкою і стоком
    parts.append(line(cx, rail_y, cx, 120, color=LINE, sw=2))
    b, _, _ = textbox(cx, 150, "навантаження\n(мотор, реле, лампа)", size=12)
    parts.append(b)
    parts.append(line(cx, 178, cx, D[1], color=LINE, sw=2))
    parts.append(text(cx + 14, (rail_y + 120) / 2 + 6, "I", size=13, anchor="start", color=POS, italic=True))
    parts.append(arrow(cx, 95, cx, 118, color=POS))
    # витік → земля
    parts.append(line(cx, S[1], cx, 360, color=LINE, sw=2))
    parts.append(line(cx - 30, 360, cx + 30, 360, color=INK, sw=3))
    parts.append(line(cx - 20, 366, cx + 20, 366, color=INK, sw=2))
    parts.append(line(cx - 10, 371, cx + 10, 371, color=INK, sw=2))
    parts.append(text(cx + 40, 364, "GND", size=12, anchor="start", color=MUTED))
    # затвор: вузол затвора, резистор послідовно, стяжка вниз
    gx = G[0]
    node_x = gx - 60                         # вузол затвора (тут гілкується стяжка)
    parts.append(line(gx, G[1], node_x, G[1], color=LINE, sw=2))
    parts.append(circle(node_x, G[1], 3, fill=INK, stroke=INK))   # точка вузла
    # резистор затвора (прямокутник) ліворуч від вузла
    rx0 = node_x - 60
    parts.append(rect(rx0, G[1] - 9, 50, 18, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    parts.append(line(node_x, G[1], rx0 + 50, G[1], color=LINE, sw=2))
    parts.append(text(rx0 + 25, G[1] - 16, "Rзатв ~100 Ω", size=11, color=MUTED))
    parts.append(line(rx0, G[1], rx0 - 40, G[1], color=LINE, sw=2))
    parts.append(text(rx0 - 50, G[1] + 4, "сигнал", size=12, anchor="end", color=NEG))
    parts.append(text(rx0 - 50, G[1] + 20, "МК", size=11, anchor="end", color=MUTED))
    # підтягувальний (стяжка) резистор затвор→витік від вузла вниз
    parts.append(line(node_x, G[1], node_x, 312, color=LINE, sw=1.5))
    parts.append(rect(node_x - 9, 250, 18, 44, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    parts.append(text(node_x - 14, 276, "100к", size=10, anchor="end", color=MUTED))
    parts.append(text(node_x - 14, 308, "стяжка", size=10, anchor="end", color=MUTED))
    parts.append(line(node_x, 312, cx, 312, color=LINE, sw=1.5))  # до витоку (землі)
    parts.append(circle(cx, 312, 3, fill=INK, stroke=INK))
    render(os.path.join(IMG, 'low-side.svg'), W, H, *parts)


# ── Фігура 3: тепло — BJT (стале падіння) проти MOSFET (R·I) ──────────────────
def fig_heat():
    W, H = 700, 380
    parts = []
    parts.append(text(W / 2, 30, "Втрати на відкритому ключі: BJT vs MOSFET", size=16, bold=True))
    # осі
    ox, oy = 90, 320
    ax_w, ax_h = 520, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))      # X
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))      # Y
    parts.append(text(ox + ax_w / 2, oy + 40, "струм навантаження I →", size=13, color=INK))
    parts.append(text(ox - 60, oy - ax_h / 2, "втрати P", size=13, color=INK))
    parts.append(text(ox - 60, oy - ax_h / 2 + 18, "(тепло)", size=11, color=MUTED))

    # BJT: P = Vce(sat)·I — пряма (Vce≈0.2 В стала)
    import math
    Vsat = 0.25
    Rds = 0.05
    Imax = 10.0
    def px(I): return ox + (I / Imax) * ax_w
    def py(P, Pmax): return oy - (P / Pmax) * ax_h
    Pmax = max(Vsat * Imax, Rds * Imax * Imax) * 1.05
    # BJT лінія
    pts_b = " ".join("%.1f,%.1f" % (px(I), py(Vsat * I, Pmax)) for I in [x / 4 for x in range(0, 41)])
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_b, NEG))
    # MOSFET крива P=I^2 R
    pts_m = " ".join("%.1f,%.1f" % (px(I), py(Rds * I * I, Pmax)) for I in [x / 8 for x in range(0, 81)])
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_m, FIELD))
    # точка перетину I = Vsat/Rds
    Icross = Vsat / Rds
    parts.append(line(px(Icross), oy, px(Icross), py(Vsat * Icross, Pmax), color=MUTED, sw=1.2, dash="4,4"))
    parts.append(circle(px(Icross), py(Vsat * Icross, Pmax), 4, fill=POS, stroke=POS))
    parts.append(text(px(Icross), oy + 18, "≈%.0f А" % Icross, size=11, color=MUTED))
    # підписи кривих
    parts.append(text(px(8.4), py(Vsat * 8.4, Pmax) - 12, "BJT: P = Vce·I", size=12, color=NEG, anchor="end"))
    parts.append(text(px(8.6), py(Rds * 8.6 * 8.6, Pmax) - 8, "MOSFET: P = I²·R", size=12, color=FIELD, anchor="start"))
    # пояснювальні рамки
    bl, _, _ = textbox(px(2.0), oy - ax_h + 40, "малий струм:\nMOSFET холодніший", size=11, color=FIELD, stroke=FIELD)
    parts.append(bl)
    br, _, _ = textbox(px(8.5), oy - ax_h + 150, "великий струм:\nквадрат бере своє", size=11, color=POS, stroke=POS)
    parts.append(br)
    render(os.path.join(IMG, 'heat-bjt-vs-mosfet.svg'), W, H, *parts)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки comp-gate-drive.md
# ════════════════════════════════════════════════════════════════════════════

def _gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=10, color=MUTED, bold=True))
    return "".join(out)


# ── Фігура A: поріг проти повного відкриття — крива R_DS(on)(V_GS) ────────────
def fig_threshold_vs_full():
    W, H = 720, 400
    parts = []
    parts.append(text(W / 2, 30, "Поріг — це ще не «відкрито»: R_DS(on) падає сходинками", size=16, bold=True))
    ox, oy = 95, 330
    ax_w, ax_h = 560, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 42, "напруга на затворі V_GS →", size=13, color=INK))
    parts.append(text(ox - 64, oy - ax_h / 2 - 6, "R_DS(on)", size=13, color=INK))
    parts.append(text(ox - 64, oy - ax_h / 2 + 12, "(опір)", size=11, color=MUTED))

    # модельна крива: дуже високий опір біля порога, спадає до плато
    import math
    Vth = 2.0
    Vmax = 11.0
    Rfloor = 0.10        # відносний «дах» плато
    def px(v): return ox + (v / Vmax) * ax_w
    def ry(v):
        if v <= Vth:
            return 1.0
        # спад до плато: гіпербола з насиченням
        r = Rfloor + (1.0 - Rfloor) * (Vth / v) ** 2.4
        return min(1.0, r)
    def py(r): return oy - (1.0 - r) * ax_h * 0.0 - (ax_h * (1 - r))  # r=1→top? хочемо r великий = високо
    # хочемо: великий опір = високо на графіку. r у [Rfloor..1], висота ∝ r
    def yfor(r): return oy - (r) * ax_h
    pts = []
    v = Vth
    while v <= Vmax + 0.01:
        pts.append("%.1f,%.1f" % (px(v), yfor(ry(v))))
        v += 0.15
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), FIELD))
    # вертикаль порога
    parts.append(line(px(Vth), oy, px(Vth), oy - ax_h, color=MUTED, sw=1.3, dash="4,4"))
    parts.append(text(px(Vth), oy + 18, "V_GS(th)", size=11, color=MUTED))
    parts.append(text(px(Vth), oy - ax_h - 6, "канал лише\nз'являється", size=10, color=MUTED))
    b0 = mtext(px(Vth), oy - ax_h - 22, "канал лише з'являється", size=10, color=MUTED)
    # позначки стовпців даташита: 4.5 В і 10 В
    for vv, lab, col in [(4.5, "при 4.5 В", NEG), (10.0, "при 10 В", POS)]:
        parts.append(line(px(vv), oy, px(vv), yfor(ry(vv)), color=col, sw=1.2, dash="3,3"))
        parts.append(circle(px(vv), yfor(ry(vv)), 4.5, fill=col, stroke=col))
        parts.append(text(px(vv), oy + 18, "%.1f В" % vv, size=11, color=col))
    # підпис точок
    parts.append(text(px(4.5) + 8, yfor(ry(4.5)) - 8, "ще вдвічі-втричі вищий", size=11, color=NEG, anchor="start"))
    parts.append(text(px(10) + 8, yfor(ry(10)) + 16, "паспортний мінімум", size=11, color=POS, anchor="start"))
    # зони
    bl = textbox(px(3.0), oy - 40, "недо-\nвідкрито", size=11, color=POS, stroke=POS)[0]
    parts.append(bl)
    br = textbox(px(9.5), oy - ax_h + 200, "повністю\nвідкрито", size=11, color=FIELD, stroke=FIELD)[0]
    parts.append(br)
    render(os.path.join(IMG, 'threshold-vs-full.svg'), W, H, *parts)


# ── Фігура B: крива заряду затвора — плато Міллера як сходинка ────────────────
def fig_gate_charge():
    W, H = 720, 400
    parts = []
    parts.append(text(W / 2, 30, "Крива заряду затвора: фронт застрягає на плато Міллера", size=16, bold=True))
    ox, oy = 80, 330
    ax_w, ax_h = 580, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 42, "закачаний у затвор заряд Q →", size=13, color=INK))
    parts.append(text(ox - 50, oy - ax_h / 2 - 6, "V_GS", size=13, color=INK))
    # три ділянки: підйом до плато, плато, добір до повного
    q1, q2, q3, q4 = 0.0, 0.30, 0.62, 1.0     # частки заряду
    Vth_y = 0.28          # частка висоти на порозі
    Vpl_y = 0.42          # рівень плато
    Vfull_y = 0.86        # кінцева V_GS (напр. 10 В)
    def px(q): return ox + q * ax_w
    def vy(h): return oy - h * ax_h
    pts = [(px(q1), vy(0.02)),
           (px(q2), vy(Vpl_y)),       # підйом до плато (через поріг)
           (px(q3), vy(Vpl_y)),       # ПЛАТО — горизонталь
           (px(q4), vy(Vfull_y))]     # добір угору до повного
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' %
                 (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    # поріг — горизонталь
    parts.append(line(ox, vy(Vth_y), px(q4), vy(Vth_y), color=MUTED, sw=1.1, dash="4,4"))
    parts.append(text(px(q4) + 4, vy(Vth_y) + 4, "V_GS(th)", size=11, color=MUTED, anchor="start"))
    # рівень плато
    parts.append(line(ox, vy(Vpl_y), px(q3), vy(Vpl_y), color=MUTED, sw=1.0, dash="2,3"))
    parts.append(text(ox - 6, vy(Vpl_y) + 4, "плато", size=10, color=MUTED, anchor="end"))
    # межі ділянок
    for q in (q2, q3):
        parts.append(line(px(q), oy, px(q), oy - ax_h, color="#dddddd", sw=1, dash="3,4"))
    # підписи ділянок під віссю
    parts.append(text((px(q1) + px(q2)) / 2, oy + 20, "Q_gs", size=11, color=INK))
    parts.append(text((px(q2) + px(q3)) / 2, oy + 20, "Q_gd (плато)", size=11, color=POS, bold=True))
    parts.append(text((px(q3) + px(q4)) / 2, oy + 20, "добір", size=11, color=INK))
    parts.append(text(px(q4), oy + 20, "Q_g", size=11, color=INK, anchor="end"))
    # анотація плато
    bx = textbox((px(q2) + px(q3)) / 2, vy(Vpl_y) - 48,
                 "увесь струм іде в C_gd:\nстік падає, V_GS стоїть", size=11, color=POS, stroke=POS)[0]
    parts.append(bx)
    # стрілка від анотації на плато
    parts.append(arrow((px(q2) + px(q3)) / 2, vy(Vpl_y) - 30, (px(q2) + px(q3)) / 2, vy(Vpl_y) - 3, color=POS))
    # точка «тут канал відкрито навстіж»
    parts.append(circle(px(q4), vy(Vfull_y), 4.5, fill=FIELD, stroke=FIELD))
    parts.append(text(px(q4) - 6, vy(Vfull_y) - 8, "повністю відкрито", size=11, color=FIELD, anchor="end"))
    render(os.path.join(IMG, 'gate-charge.svg'), W, H, *parts)


# ── Фігура C: драйвер затвора між логікою і n-MOSFET (нижнє плече) ────────────
def fig_driver_block():
    W, H = 720, 420
    parts = []
    parts.append(text(W / 2, 28, "Драйвер затвора: від 3.3 В логіки — повні 12 В на затвор", size=16, bold=True))

    # ── ліворуч: мікроконтролер ──
    mcu = rect(40, 150, 96, 90, fill=FILL, stroke=LINE, sw=1.6, rx=8)
    parts.append(mcu)
    parts.append(mtext(88, 188, ["МК", "3.3 В"], size=13, bold=True))
    parts.append(text(88, 232, "PWM/GPIO", size=10, color=MUTED))

    # ── драйвер (мікросхема) ──
    dvx, dvy, dvw, dvh = 230, 120, 150, 150
    parts.append(rect(dvx, dvy, dvw, dvh, fill="#eef6ff", stroke=NEG, sw=2, rx=8))
    parts.append(text(dvx + dvw / 2, dvy + 24, "ДРАЙВЕР", size=13, bold=True, color=NEG))
    parts.append(text(dvx + dvw / 2, dvy + 42, "затвора", size=11, color=NEG))
    # двотактний вихідний каскад усередині (схематично)
    midx = dvx + dvw / 2 + 24
    parts.append(text(midx, dvy + 74, "⎍ верх", size=10, color=MUTED, anchor="start"))
    parts.append(text(midx, dvy + 92, "⎍ низ", size=10, color=MUTED, anchor="start"))
    parts.append(text(dvx + 14, dvy + 84, "IN", size=10, color=INK, anchor="start"))
    parts.append(text(dvx + dvw - 14, dvy + 84, "OUT", size=10, color=INK, anchor="end"))
    # живлення драйвера V_DD = 12 В
    parts.append(line(dvx + dvw / 2, 70, dvx + dvw / 2, dvy, color=POS, sw=2))
    parts.append(text(dvx + dvw / 2, 62, "V_DD = 10–12 В", size=12, color=POS))
    parts.append(_gnd(dvx + dvw / 2, dvy + dvh, None))

    # вхід драйвера від МК
    parts.append(line(136, 195, dvx, 195, color=LINE, sw=2))
    parts.append(arrow(180, 195, dvx - 2, 195, color=LINE))
    parts.append(text((136 + dvx) / 2, 186, "логіка", size=10, color=MUTED))

    # ── праворуч: силова частина (n-MOSFET нижнього плеча) ──
    sym, D, S, G = nmos(560, 250, on=True, scale=1.0)
    parts.append(sym)
    # рейка живлення силова
    parts.append(line(470, 80, 660, 80, color=POS, sw=2.5))
    parts.append(text(660, 72, "+V (мотор)", size=12, color=POS, anchor="end"))
    parts.append(line(560, 80, 560, 120, color=LINE, sw=2))
    bld = textbox(560, 142, "навантаження", size=11)[0]
    parts.append(bld)
    parts.append(line(560, 164, 560, D[1], color=LINE, sw=2))
    parts.append(line(560, S[1], 560, 360, color=LINE, sw=2))
    parts.append(_gnd(560, 360, "GND"))

    # вихід драйвера → R_g → затвор
    out_x = dvx + dvw
    parts.append(line(out_x, dvy + 84, 430, dvy + 84, color=LINE, sw=2))
    parts.append(line(430, dvy + 84, 430, G[1], color=LINE, sw=2))
    # резистор затвора
    rg = rect(442, G[1] - 9, 46, 18, fill="#ffffff", stroke=INK, sw=1.6, rx=3)
    parts.append(line(430, G[1], 442, G[1], color=LINE, sw=2))
    parts.append(rg)
    parts.append(text(465, G[1] - 15, "R_g", size=11, color=INK))
    parts.append(line(488, G[1], G[0], G[1], color=LINE, sw=2))
    # вузол затвора
    node_x = 510
    parts.append(circle(node_x, G[1], 3, fill=INK, stroke=INK))
    # стяжка затвор–витік
    parts.append(line(node_x, G[1], node_x, 320, color=LINE, sw=1.4))
    rpd = rect(node_x - 9, 250, 18, 40, fill="#ffffff", stroke=INK, sw=1.4, rx=3)
    parts.append(rpd)
    parts.append(text(node_x - 13, 274, "стяжка", size=9, color=MUTED, anchor="end"))
    parts.append(line(node_x, 320, 560, 320, color=LINE, sw=1.4))
    parts.append(circle(560, 320, 3, fill=INK, stroke=INK))

    # підпис «ампери заряду»
    parts.append(text((488 + G[0]) / 2, G[1] + 22, "піковий струм — ампери", size=10, color=POS))
    render(os.path.join(IMG, 'driver-block.svg'), W, H, *parts)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки math-rdson-heat.md
# ════════════════════════════════════════════════════════════════════════════

# ── Фігура M1: паралель ключів — опір ділиться, струм теж ─────────────────────
def fig_parallel_split():
    W, H = 720, 360
    parts = []
    parts.append(text(W / 2, 30, "Чотири ключі паралельно: опір на ¼, тепло на ¼", size=16, bold=True))
    # спільна верхня шина (від навантаження) і нижня (на землю)
    top_y, bot_y = 90, 270
    x0, x1 = 110, 610
    parts.append(line(x0, top_y, x1, top_y, color=POS, sw=2.5))
    parts.append(line(x0, bot_y, x1, bot_y, color=INK, sw=2.5))
    parts.append(text(x0 - 6, top_y - 10, "від навантаження (I = 40 А)", size=12, color=POS, anchor="start"))
    parts.append(text(x0 - 6, bot_y + 24, "на землю", size=12, color=MUTED, anchor="start"))
    # чотири транзистори у ряд між шинами
    xs = [170, 310, 450, 590]
    for i, cx in enumerate(xs):
        sym, D, S, G = nmos(cx, 180, on=True, scale=0.62)
        parts.append(line(cx, top_y, cx, D[1], color=LINE, sw=2))
        parts.append(line(cx, S[1], cx, bot_y, color=LINE, sw=2))
        parts.append(sym)
        # підпис струму гілки
        parts.append(text(cx + 30, 150, "10 А", size=11, color=POS, anchor="start"))
        parts.append(arrow(cx, top_y + 6, cx, D[1] - 2, color=POS))
        # спільний затвор-вузол (схематично — всі затвори разом)
        parts.append(line(G[0], G[1], G[0] - 14, G[1], color=LINE, sw=1.5))
    # спільна лінія затворів
    gate_y = 180
    gx_line = nmos(xs[0], 180, on=True, scale=0.62)[3][0] - 14
    parts.append(line(gx_line, gate_y, gx_line, 330, color=LINE, sw=1.5))
    for cx in xs[1:]:
        gx = nmos(cx, 180, on=True, scale=0.62)[3][0] - 14
        parts.append(line(gx, gate_y, gx, 330, color=LINE, sw=1))
        parts.append(line(gx_line, 330, gx, 330, color=LINE, sw=1))
    parts.append(text(gx_line - 6, 330, "спільний затвор", size=10, color=MUTED, anchor="end"))
    # підсумкова рамка
    b = textbox(W / 2, 322,
                "кожен веде I/4 = 10 А · на кожному P = 10²·R · разом учетверо менше, ніж на одному",
                size=11, color=FIELD, stroke=FIELD)[0]
    parts.append(b)
    render(os.path.join(IMG, 'parallel-split.svg'), W, H, *parts)


# ── Фігура M2: кондуктивні vs перемикальні втрати залежно від частоти ─────────
def fig_cond_vs_sw():
    W, H = 720, 400
    parts = []
    parts.append(text(W / 2, 30, "Дві втрати з частотою: де яка переважає", size=16, bold=True))
    ox, oy = 95, 320
    ax_w, ax_h = 555, 240
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 42, "частота комутації f →", size=13, color=INK))
    parts.append(text(ox - 58, oy - ax_h / 2 - 6, "втрати P", size=13, color=INK))
    parts.append(text(ox - 58, oy - ax_h / 2 + 12, "(тепло)", size=11, color=MUTED))

    fmax = 500.0          # умовні кГц
    Pcond = 0.75          # кондуктивні — стала (від I²R), Вт
    ksw = 0.75 / 100.0    # перемикальні ∝ f: на 100 кГц зрівнялися з кондуктивними
    Pmax = (Pcond + ksw * fmax) * 1.05
    def px(f): return ox + (f / fmax) * ax_w
    def py(P): return oy - (P / Pmax) * ax_h
    # кондуктивні — горизонталь
    parts.append(line(px(0), py(Pcond), px(fmax), py(Pcond), color=FIELD, sw=2.5))
    # перемикальні — пряма з нуля
    parts.append(line(px(0), py(0), px(fmax), py(ksw * fmax), color=POS, sw=2.5))
    # сума — пунктир
    pts = " ".join("%.1f,%.1f" % (px(f), py(Pcond + ksw * f)) for f in [x * 10 for x in range(0, 51)])
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4"/>' % (pts, INK))
    # точка рівноваги f, де Psw = Pcond
    fcr = Pcond / ksw
    parts.append(line(px(fcr), oy, px(fcr), py(Pcond), color=MUTED, sw=1.2, dash="4,4"))
    parts.append(circle(px(fcr), py(Pcond), 4, fill=NEG, stroke=NEG))
    parts.append(text(px(fcr), oy + 18, "≈100 кГц", size=11, color=MUTED))
    # підписи кривих
    parts.append(text(px(fmax) - 6, py(Pcond) - 8, "кондуктивні: I²·R (стала)", size=12, color=FIELD, anchor="end"))
    parts.append(text(px(fmax) - 6, py(ksw * fmax) - 8, "перемикальні ∝ f", size=12, color=POS, anchor="end"))
    parts.append(text(px(330), py(Pcond + ksw * 330) + 18, "сума", size=11, color=INK, anchor="start"))
    # зони
    bl = textbox(px(45), oy - ax_h + 40, "повільне\nклацання:\nпанує R_DS(on)", size=11, color=FIELD, stroke=FIELD)[0]
    parts.append(bl)
    br = textbox(px(430), oy - 64, "імпульсний\nперетворювач:\nпанує перемикання", size=11, color=POS, stroke=POS)[0]
    parts.append(br)
    render(os.path.join(IMG, 'cond-vs-sw.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_two_states()
    fig_low_side()
    fig_heat()
    fig_threshold_vs_full()
    fig_gate_charge()
    fig_driver_block()
    fig_parallel_split()
    fig_cond_vs_sw()
    print("OK figures")
