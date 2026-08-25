# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path(d, color=LINE, fill='none', sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Трирівнева енергетична схема іона Er³⁺ у кварцовому склі.
# ═══════════════════════════════════════════════════════════════════════════
def fig_energy_levels():
    W, H = 720, 420
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Трирівнева енергетична схема іона Er³⁺ у склі', 17, INK, 'middle', bold=True))

    x0, x1 = 160, 560
    y1 = 340   # E1 — основний стан 4I_15/2
    y2 = 200   # E2 — метастабільний стан 4I_13/2
    y3 = 100   # E3 — рівень накачки 4I_11/2

    # Енергетичні рівні (товсті горизонтальні лінії)
    f.append(line(x0, y1, x1, y1, color=INK, sw=3))
    f.append(line(x0, y2, x1, y2, color=INK, sw=3))
    f.append(line(x0, y3, x1, y3, color=INK, sw=3))

    # Назви рівнів та позначення підсистем
    f.append(text(x0 - 15, y1 + 5, 'E₁ (⁴I₁₅/₂)', 13, INK, 'end', bold=True))
    f.append(text(x0 - 15, y1 + 22, 'Основний стан', 11, MUTED, 'end'))

    f.append(text(x0 - 15, y2 + 5, 'E₂ (⁴I₁₃/₂)', 13, INK, 'end', bold=True))
    f.append(text(x0 - 15, y2 + 22, 'Метастабільний (τ ≈ 10 мс)', 11, MUTED, 'end'))

    f.append(text(x0 - 15, y3 + 5, 'E₃ (⁴I₁₁/₂)', 13, INK, 'end', bold=True))
    f.append(text(x0 - 15, y3 + 22, 'Рівень накачки (τ ≈ 1 мкс)', 11, MUTED, 'end'))

    # Перехід 1: Накачка 980 нм (зелена стрілка вгору E1 -> E3)
    xpump = 210
    f.append(line(xpump, y1 - 4, xpump, y3 + 12, color=FIELD, sw=2.5))
    f.append(arrow(xpump, y3 + 12, xpump, y3 + 4, color=FIELD, sw=2.5))
    f.append(text(xpump - 12, (y1 + y3) / 2, 'Поглинання накачки\n980 нм (hνₚ)', 12, FIELD, 'end', bold=True))

    # Перехід 2: Безвипромінювальний релаксаційний перехід (E3 -> E2)
    xdecay = 310
    f.append(line(xdecay, y3 + 4, xdecay, y2 - 4, color=MUTED, sw=2.0, dash='4,4'))
    f.append(arrow(xdecay, y2 - 12, xdecay, y2 - 4, color=MUTED, sw=2.0))
    f.append(text(xdecay + 12, (y3 + y2) / 2 + 4, 'Швидкий розпад\n(фонони, 1 мкс)', 11, MUTED, 'start'))

    # Перехід 3: Вимушене випромінювання (E2 -> E1) під дією сигналу 1550 нм
    xstim = 450
    f.append(line(xstim, y2 + 4, xstim, y1 - 12, color=POS, sw=2.8))
    f.append(arrow(xstim, y1 - 12, xstim, y1 - 4, color=POS, sw=2.8))
    f.append(text(xstim - 12, (y2 + y1) / 2 - 8, 'Вимушене випромінювання\n1550 нм (сигнал)', 12, POS, 'end', bold=True))

    # Вхідний і вихідний фотони біля вимушеного переходу
    f.append(path("M %d %d Q %d %d %d %d T %d %d" %
                  (xstim - 70, y2 + 40, xstim - 55, y2 + 30, xstim - 40, y2 + 40, xstim - 20, y2 + 40),
                  color=POS, fill='none', sw=1.8))
    f.append(arrow(xstim - 25, y2 + 40, xstim - 15, y2 + 40, color=POS, sw=1.8))
    f.append(text(xstim - 75, y2 + 44, 'вхідний hν', 11, POS, 'end'))

    f.append(path("M %d %d Q %d %d %d %d T %d %d" %
                  (xstim + 15, y1 - 40, xstim + 35, y1 - 50, xstim + 55, y1 - 40, xstim + 75, y1 - 40),
                  color=POS, fill='none', sw=1.8))
    f.append(arrow(xstim + 65, y1 - 40, xstim + 80, y1 - 40, color=POS, sw=1.8))

    f.append(path("M %d %d Q %d %d %d %d T %d %d" %
                  (xstim + 15, y1 - 20, xstim + 35, y1 - 30, xstim + 55, y1 - 20, xstim + 75, y1 - 20),
                  color=POS, fill='none', sw=1.8))
    f.append(arrow(xstim + 65, y1 - 20, xstim + 80, y1 - 20, color=POS, sw=1.8))

    f.append(text(xstim + 85, y1 - 30, '2 однакових фотони\n(фаза, колір, напрям)', 11, POS, 'start', bold=True))

    f.append(text(W / 2, H - 18,
                  'Накачка 980 нм створює інверсію N₂ > N₁; сигнальний фотон викликає лавинне випромінювання клонів',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'energy-levels.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Структурна схема оптичного підсилювача EDFA.
# ═══════════════════════════════════════════════════════════════════════════
def fig_edfa_schema():
    W, H = 740, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Функціональна схема однокаскадного EDFA', 17, INK, 'middle', bold=True))

    cy = 160
    blocks = [
        (40, 70, 'Ізолятор\nвхідний', FILL, POS),
        (150, 75, 'WDM\nсуматор', FILL, INK),
        (265, 120, 'Ербієве волокно\nEDF (10-30 м)', '#fde9c8', POS),
        (425, 80, 'Фільтр GFF\n(вирівнювання)', FILL, INK),
        (545, 75, 'Оптичний\nвідгалужувач', FILL, MUTED),
        (640, 70, 'Ізолятор\nвихідний', FILL, POS),
    ]

    f.append(line(15, cy, 725, cy, color=POS, sw=2.5))
    f.append(arrow(715, cy, 725, cy, color=POS, sw=2.5))

    f.append(text(20, cy - 12, 'Вхід 1550 нм', 11, POS, 'start', bold=True))
    f.append(text(725, cy - 12, 'Вихід (підсилений)', 11, POS, 'end', bold=True))

    for bx, bw, blabel, bfill, bstroke in blocks:
        bh = 64
        by = cy - bh / 2
        f.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, sw=1.5, rx=4))
        f.append(mtext(bx + bw / 2, cy - 10, blabel, size=11, color=INK, anchor='middle'))

    py = cy + 110
    px = 150 + 75 / 2
    f.append(rect(px - 45, py - 25, 90, 45, fill='#e6eef7', stroke=FIELD, sw=1.5, rx=4))
    f.append(mtext(px, py - 8, 'Лазер накачки\n980 / 1480 нм', size=11, color=FIELD, anchor='middle', bold=True))

    f.append(line(px, py - 25, px, cy + 32, color=FIELD, sw=2.2))
    f.append(arrow(px, cy + 38, px, cy + 32, color=FIELD, sw=2.2))
    f.append(text(px + 8, py - 40, 'Світло накачки', 10, FIELD, 'start'))

    tap_x = 545 + 75 / 2
    pd_y = cy + 110
    f.append(rect(tap_x - 45, pd_y - 25, 90, 45, fill='#f4f6f8', stroke=MUTED, sw=1.2, rx=4))
    f.append(mtext(tap_x, pd_y - 8, 'Фотодіод AGC\nта контролер', size=11, color=MUTED, anchor='middle'))

    f.append(line(tap_x, cy + 32, tap_x, pd_y - 25, color=MUTED, sw=1.5, dash='3,3'))
    f.append(arrow(tap_x, pd_y - 30, tap_x, pd_y - 25, color=MUTED, sw=1.5))
    f.append(text(tap_x - 8, cy + 50, '1% відвід', 10, MUTED, 'end'))

    f.append(line(tap_x - 45, pd_y, px + 45, pd_y, color=MUTED, sw=1.2, dash='4,4'))
    f.append(arrow(px + 50, pd_y, px + 45, pd_y, color=MUTED, sw=1.2))
    f.append(text((tap_x + px) / 2, pd_y + 16, 'керування струмом накачки (AGC)', 10, MUTED, 'middle'))

    f.append(text(W / 2, H - 16,
                  'Вхідний та вихідний ізолятори блокують відбиття, GFF вирівнює спектр WDM, AGC тримає сталий коефіцієнт',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'edfa-schema.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Залежність підсилення G та вихідної потужності P_out від Pin.
# ═══════════════════════════════════════════════════════════════════════════
def fig_gain_curve():
    W, H = 700, 400
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Криві підсилення та вихідної потужності EDFA', 17, INK, 'middle', bold=True))

    ox, oy = 90, 320
    gw, gh = 520, 230

    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.5))
    f.append(arrow(ox + gw - 10, oy, ox + gw, oy, color=INK, sw=1.5))
    f.append(text(ox + gw / 2, oy + 38, 'Вхідна оптична потужність Pᵢₙ (дБм)', 13, INK, 'middle', bold=True))

    f.append(line(ox, oy, ox, oy - gh, color=POS, sw=1.5))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh, color=POS, sw=1.5))
    f.append(text(ox - 50, oy - gh / 2, 'Підсилення G (дБ)', 13, POS, 'middle', bold=True))

    f.append(line(ox + gw, oy, ox + gw, oy - gh, color=NEG, sw=1.5))
    f.append(arrow(ox + gw, oy - gh + 10, ox + gw, oy - gh, color=NEG, sw=1.5))
    f.append(text(ox + gw + 55, oy - gh / 2, 'Вихідна потужність Pₒᵤₜ (дБм)', 13, NEG, 'middle', bold=True))

    f.append(text(ox, oy + 18, '−30', 11, MUTED, 'middle'))
    f.append(text(ox + gw * 0.35, oy + 18, '−15', 11, MUTED, 'middle'))
    f.append(text(ox + gw * 0.65, oy + 18, '0', 11, MUTED, 'middle'))
    f.append(text(ox + gw, oy + 18, '+10', 11, MUTED, 'middle'))

    f.append(text(ox - 12, oy - gh + 30, '30 дБ (G₀)', 11, POS, 'end', bold=True))
    f.append(text(ox - 12, oy - gh + 80, '27 дБ', 11, POS, 'end'))
    f.append(text(ox - 12, oy + 4, '0 дБ', 11, POS, 'end'))

    pts_g = []
    for i in range(101):
        rel_x = i / 100.0
        pin_val = -30.0 + 40.0 * rel_x
        g_db = 30.0 / (1.0 + math.pow(10.0, (pin_val + 10.0) / 18.0))
        if g_db < 2.0: g_db = 2.0
        px = ox + rel_x * gw
        py = oy - (g_db / 30.0) * (gh - 30)
        pts_g.append((px, py))

    path_g = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in pts_g])
    f.append(path(path_g, color=POS, fill='none', sw=2.5))

    pts_p = []
    for i in range(101):
        rel_x = i / 100.0
        pin_val = -30.0 + 40.0 * rel_x
        g_db = 30.0 / (1.0 + math.pow(10.0, (pin_val + 10.0) / 18.0))
        if g_db < 2.0: g_db = 2.0
        pout_val = pin_val + g_db
        rel_pout = (pout_val - 0.0) / 22.0
        if rel_pout > 1.0: rel_pout = 1.0
        px = ox + rel_x * gw
        py = oy - rel_pout * (gh - 30)
        pts_p.append((px, py))

    path_p = "M " + " L ".join(["%.1f %.1f" % (p[0], p[1]) for p in pts_p])
    f.append(path(path_p, color=NEG, fill='none', sw=2.5))

    x_sat = ox + gw * 0.42
    f.append(line(x_sat, oy, x_sat, oy - gh + 20, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(x_sat + 6, oy - gh + 45, 'Поріг насичення (3 дБ спад G)', 11, MUTED, 'start'))

    f.append(text(ox + 80, oy - gh + 60, 'Режим малого сигналу\n(G = G₀ = const)', 12, POS, 'middle', bold=True))
    f.append(text(ox + gw - 90, oy - 100, 'Режим насичення\n(Pₒᵤₜ ➔ Pₛₐₜ,ₘₐₓ)', 12, NEG, 'middle', bold=True))

    f.append(text(W / 2, H - 14,
                  'За слабких сигналів підсилення максимальне (G₀); при підвищенні Pᵢₙ підсилення падає через виснаження N₂',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'gain-curve.svg'), W, H, *f)


if __name__ == '__main__':
    fig_energy_levels()
    fig_edfa_schema()
    fig_gain_curve()
    print("SVG generation complete.")
