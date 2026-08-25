# -*- coding: utf-8 -*-
"""
Generator script for standing wave figures.
Uses svgkit from scripts directory.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def svg_path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_dash = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, d_dash)


# -----------------------------------------------------------------------------
# Figure 1: standing-wave-nodes.svg
# -----------------------------------------------------------------------------
def gen_standing_wave_nodes():
    out_path = os.path.join(IMG_DIR, 'standing-wave-nodes.svg')
    w, h = 760, 360
    frags = []

    # Envelope curves (dotted/dashed)
    x0, y0 = 60, 160
    length = 640
    amplitude = 75
    wavelength = 320  # 2 full wavelengths in 640px -> 4 half-waves

    # Envelope top and bottom
    pts_top = []
    pts_bot = []
    for px in range(0, length + 1):
        x = x0 + px
        # Standing wave spatial envelope: 2A |sin(2pi x / lambda)|
        env = amplitude * math.sin(2 * math.pi * px / wavelength)
        pts_top.append((x, y0 - abs(env)))
        pts_bot.append((x, y0 + abs(env)))

    d_top = "M " + " L ".join("%.1f,%.1f" % p for p in pts_top)
    d_bot = "M " + " L ".join("%.1f,%.1f" % p for p in pts_bot)
    frags.append(svg_path(d_top, fill="none", stroke=MUTED, sw=1.5, dash="4,4"))
    frags.append(svg_path(d_bot, fill="none", stroke=MUTED, sw=1.5, dash="4,4"))

    # Instantaneous wave profiles at different times t
    times = [
        (0.0, POS, 2.2, "t = 0 (макс. відхилення)"),
        (0.25, FIELD, 1.6, "t = T/8"),
        (0.50, NEG, 1.8, "t = T/4 (плоска струна)"),
    ]

    for phase_t, color, sw, _label in times:
        pts = []
        cos_t = math.cos(phase_t * math.pi)
        for px in range(0, length + 1):
            x = x0 + px
            y = y0 - amplitude * math.sin(2 * math.pi * px / wavelength) * cos_t
            pts.append((x, y))
        d_wave = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
        frags.append(svg_path(d_wave, fill="none", stroke=color, sw=sw))

    # Equilibrium center line
    frags.append(line(x0 - 20, y0, x0 + length + 20, y0, color=LINE, sw=1.2, dash="6,4"))

    # Node locations: x = 0, lambda/2, lambda, 3lambda/2, 2lambda
    node_xs = [0, wavelength / 2, wavelength, 3 * wavelength / 2, 2 * wavelength]
    for i, nx_rel in enumerate(node_xs):
        nx = x0 + nx_rel
        frags.append(circle(nx, y0, 5, fill=INK, stroke=BG, sw=1.5))
        lbl = "Вузол %d" % (i + 1)
        ly = y0 + 26 if i % 2 == 0 else y0 - 26
        frags.append(text(nx, ly, lbl, size=12, bold=True, color=INK))

    # Antinode locations: x = lambda/4, 3lambda/4, 5lambda/4, 7lambda/4
    antinode_xs = [wavelength / 4, 3 * wavelength / 4, 5 * wavelength / 4, 7 * wavelength / 4]
    for i, ax_rel in enumerate(antinode_xs):
        ax = x0 + ax_rel
        ay_top = y0 - amplitude
        frags.append(circle(ax, ay_top, 4, fill=POS, stroke=BG, sw=1.5))
        frags.append(text(ax, ay_top - 14, "Пучність", size=11, bold=True, color=POS))

    # Dimension arrows: lambda/2 and lambda/4
    y_dim1 = y0 + 70
    x_n1, x_n2 = x0, x0 + wavelength / 2
    frags.append(line(x_n1, y_dim1, x_n2, y_dim1, color=NEG, sw=1.5))
    frags.append(line(x_n1, y0 + 15, x_n1, y_dim1 + 8, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(x_n2, y0 + 15, x_n2, y_dim1 + 8, color=MUTED, sw=1, dash="2,2"))
    frags.append(text((x_n1 + x_n2) / 2, y_dim1 + 18, "Відстань між вузлами = λ/2", size=12, color=NEG, bold=True))

    y_dim2 = y0 + 115
    x_a2 = x0 + 3 * wavelength / 4
    frags.append(line(x_n2, y_dim2, x_a2, y_dim2, color=FIELD, sw=1.5))
    frags.append(line(x_a2, y0 + 15, x_a2, y_dim2 + 8, color=MUTED, sw=1, dash="2,2"))
    frags.append(text((x_n2 + x_a2) / 2, y_dim2 + 18, "Вузол–пучність = λ/4", size=12, color=FIELD, bold=True))

    # Legend
    frags.append(textbox(630, 55, "Червона: t=0\nЗелена: t=T/8\nСиня: t=T/4", size=11, fill="#f8fafc", stroke=MUTED, sw=1)[0])

    render(out_path, w, h, *frags, title="Анатомія стоячої хвилі: вузли, пучності та відстані")


# -----------------------------------------------------------------------------
# Figure 2: reflection-boundaries.svg
# -----------------------------------------------------------------------------
def gen_reflection_boundaries():
    out_path = os.path.join(IMG_DIR, 'reflection-boundaries.svg')
    w, h = 760, 380
    frags = []

    # Panel A: Fixed boundary
    ax0, ay0 = 50, 140
    aw = 310
    frags.append(rect(20, 20, 350, 340, fill="none", stroke=MUTED, sw=1))
    frags.append(text(195, 45, "(а) Жорстко закріплений кінець", size=14, bold=True, color=INK))

    # Wall
    frags.append(rect(ax0 + aw, ay0 - 80, 16, 160, fill="#64748b", stroke=INK, sw=1.5))
    for wy in range(ay0 - 75, ay0 + 75, 15):
        frags.append(line(ax0 + aw + 16, wy, ax0 + aw + 26, wy + 10, color=INK, sw=1.2))

    # Incident pulse
    pts_inc = []
    for px in range(0, aw + 1):
        x = ax0 + px
        pulse = 45 * math.exp(-((px - 110) ** 2) / 400)
        pts_inc.append((x, ay0 - 35 - pulse))
    d_inc = "M " + " L ".join("%.1f,%.1f" % p for p in pts_inc)
    frags.append(svg_path(d_inc, fill="none", stroke=POS, sw=2))
    frags.append(arrow(ax0 + 150, ay0 - 65, ax0 + 190, ay0 - 65, color=POS, sw=1.8))
    frags.append(text(ax0 + 110, ay0 - 88, "Падна хвиля (+)", size=11, color=POS, bold=True))

    # Reflected pulse
    pts_ref = []
    for px in range(0, aw + 1):
        x = ax0 + px
        pulse = 45 * math.exp(-((px - 200) ** 2) / 400)
        pts_ref.append((x, ay0 + 35 + pulse))
    d_ref = "M " + " L ".join("%.1f,%.1f" % p for p in pts_ref)
    frags.append(svg_path(d_ref, fill="none", stroke=NEG, sw=2))
    frags.append(arrow(ax0 + 170, ay0 + 65, ax0 + 130, ay0 + 65, color=NEG, sw=1.8))
    frags.append(text(ax0 + 200, ay0 + 88, "Відбита хвиля (−)", size=11, color=NEG, bold=True))

    # Node indicator at wall
    frags.append(circle(ax0 + aw, ay0, 5, fill=INK, stroke=BG, sw=1.5))
    frags.append(text(ax0 + aw - 35, ay0 - 10, "Вузол", size=11, bold=True, color=INK))

    # Text explanation panel A
    frags.append(textbox(195, ay0 + 145, "Фаза змінюється на 180° (π)\nГорб відбивається як западина", size=11, fill="#fee2e2", stroke=POS, sw=1)[0])

    # Panel B: Free boundary
    bx0, by0 = 430, 140
    bw = 300
    frags.append(rect(390, 20, 350, 340, fill="none", stroke=MUTED, sw=1))
    frags.append(text(565, 45, "(б) Вільний кінець (кільце)", size=14, bold=True, color=INK))

    # Vertical rod with ring
    frags.append(line(bx0 + bw, by0 - 80, bx0 + bw, by0 + 80, color="#64748b", sw=3))
    frags.append(circle(bx0 + bw, by0 - 35, 7, fill=BG, stroke=FIELD, sw=2.5))

    # Incident pulse
    pts_b_inc = []
    for px in range(0, bw + 1):
        x = bx0 + px
        pulse = 45 * math.exp(-((px - 100) ** 2) / 400)
        pts_b_inc.append((x, by0 - 35 - pulse))
    d_b_inc = "M " + " L ".join("%.1f,%.1f" % p for p in pts_b_inc)
    frags.append(svg_path(d_b_inc, fill="none", stroke=POS, sw=2))
    frags.append(arrow(bx0 + 130, by0 - 65, bx0 + 170, by0 - 65, color=POS, sw=1.8))
    frags.append(text(bx0 + 100, by0 - 88, "Падна хвиля (+)", size=11, color=POS, bold=True))

    # Reflected pulse
    pts_b_ref = []
    for px in range(0, bw + 1):
        x = bx0 + px
        pulse = 45 * math.exp(-((px - 190) ** 2) / 400)
        pts_b_ref.append((x, by0 - 35 - pulse))
    d_b_ref = "M " + " L ".join("%.1f,%.1f" % p for p in pts_b_ref)
    frags.append(svg_path(d_b_ref, fill="none", stroke=FIELD, sw=2, dash="5,3"))
    frags.append(arrow(bx0 + 160, by0 + 25, bx0 + 120, by0 + 25, color=FIELD, sw=1.8))
    frags.append(text(bx0 + 190, by0 + 45, "Відбита хвиля (+)", size=11, color=FIELD, bold=True))

    # Antinode indicator
    frags.append(circle(bx0 + bw, by0 - 35, 4, fill=FIELD, stroke=BG, sw=1.5))
    frags.append(text(bx0 + bw - 45, by0 - 45, "Пучність", size=11, bold=True, color=FIELD))

    # Text explanation panel B
    frags.append(textbox(565, by0 + 145, "Фаза НЕ змінюється (0°)\nГорб відбивається як горб (2A)", size=11, fill="#dcfce7", stroke=FIELD, sw=1)[0])

    render(out_path, w, h, *frags, title=None)


# -----------------------------------------------------------------------------
# Figure 3: harmonics-modes.svg
# -----------------------------------------------------------------------------
def gen_harmonics_modes():
    out_path = os.path.join(IMG_DIR, 'harmonics-modes.svg')
    w, h = 760, 420
    frags = []

    x0, sw_len = 160, 530
    y_starts = [80, 160, 240, 320]
    modes_info = [
        (1, "1-ша мода (n=1)\nОсновний тон", "λ₁ = 2L", "f₁ = v / 2L", POS),
        (2, "2-га мода (n=2)\n2-га гармоніка", "λ₂ = L", "f₂ = 2·f₁", NEG),
        (3, "3-тя мода (n=3)\n3-тя гармоніка", "λ₃ = 2L/3", "f₃ = 3·f₁", FIELD),
        (4, "4-та мода (n=4)\n4-та гармоніка", "λ₄ = L/2", "f₄ = 4·f₁", INK),
    ]

    # Boundaries
    frags.append(line(x0, 40, x0, 360, color=INK, sw=3))
    frags.append(line(x0 + sw_len, 40, x0 + sw_len, 360, color=INK, sw=3))
    frags.append(text(x0, 28, "x = 0 (Вузол)", size=11, bold=True))
    frags.append(text(x0 + sw_len, 28, "x = L (Вузол)", size=11, bold=True))

    for n, title_str, lambda_str, freq_str, color in modes_info:
        cy = y_starts[n - 1]
        amplitude = 28

        frags.append(text(15, cy - 8, title_str.split('\n')[0], size=12, bold=True, color=color, anchor="start"))
        frags.append(text(15, cy + 10, title_str.split('\n')[1], size=10, color=MUTED, anchor="start"))

        frags.append(text(x0 + sw_len + 15, cy - 8, lambda_str, size=11, bold=True, color=color, anchor="start"))
        frags.append(text(x0 + sw_len + 15, cy + 10, freq_str, size=11, color=INK, anchor="start"))

        frags.append(line(x0, cy, x0 + sw_len, cy, color=MUTED, sw=1, dash="3,3"))

        pts_p = []
        pts_m = []
        for px in range(0, sw_len + 1):
            x = x0 + px
            y_val = amplitude * math.sin(n * math.pi * px / sw_len)
            pts_p.append((x, cy - y_val))
            pts_m.append((x, cy + y_val))

        d_p = "M " + " L ".join("%.1f,%.1f" % p for p in pts_p)
        d_m = "M " + " L ".join("%.1f,%.1f" % p for p in pts_m)
        frags.append(svg_path(d_p, fill="none", stroke=color, sw=2))
        frags.append(svg_path(d_m, fill="none", stroke=color, sw=1.2, dash="4,3"))

        for node_idx in range(n + 1):
            nx = x0 + node_idx * (sw_len / n)
            frags.append(circle(nx, cy, 3.5, fill=INK, stroke=BG, sw=1))

    y_bot = 385
    frags.append(arrow(x0 + 40, y_bot, x0, y_bot, color=INK, sw=1.5))
    frags.append(arrow(x0 + sw_len - 40, y_bot, x0 + sw_len, y_bot, color=INK, sw=1.5))
    frags.append(line(x0, y_bot, x0 + sw_len, y_bot, color=INK, sw=1.5))
    frags.append(text(x0 + sw_len / 2, y_bot - 6, "Довжина резонатора L", size=12, bold=True))

    render(out_path, w, h, *frags, title="Власні моди та гармоніки стоячих хвиль у затиснутій струні")


# -----------------------------------------------------------------------------
# Figure 4: energy-flow.svg
# -----------------------------------------------------------------------------
def gen_energy_flow():
    out_path = os.path.join(IMG_DIR, 'energy-flow.svg')
    w, h = 760, 360
    frags = []

    # Top box: Traveling wave
    frags.append(rect(20, 25, 720, 140, fill="#f8fafc", stroke=MUTED, sw=1))
    frags.append(text(40, 50, "Біжуча хвиля: переносу речовини немає, але є НЕТТО-ПЕРЕНОС ЕНЕРГІЇ", size=13, bold=True, color=POS, anchor="start"))

    tx0, ty0 = 60, 110
    pts_tr = []
    for px in range(0, 480):
        x = tx0 + px
        y = ty0 - 30 * math.sin(2 * math.pi * px / 200)
        pts_tr.append((x, y))
    d_tr = "M " + " L ".join("%.1f,%.1f" % p for p in pts_tr)
    frags.append(svg_path(d_tr, fill="none", stroke=POS, sw=2))

    frags.append(arrow(tx0 + 500, ty0, tx0 + 620, ty0, color=POS, sw=3))
    frags.append(text(tx0 + 560, ty0 - 15, "Потік енергії P > 0", size=11, bold=True, color=POS))
    frags.append(text(tx0 + 560, ty0 + 20, "вправо зі швидкістю v", size=10, color=MUTED))

    # Bottom box: Standing wave
    frags.append(rect(20, 185, 720, 155, fill="#f8fafc", stroke=MUTED, sw=1))
    frags.append(text(40, 210, "Стояча хвиля: НЕТТО-ПОТІК ЕНЕРГІЇ ДОРІВНЮЄ НУЛЮ (<P> = 0)", size=13, bold=True, color=NEG, anchor="start"))

    sx0, sy0 = 60, 275
    pts_st = []
    for px in range(0, 360):
        x = sx0 + px
        y = sy0 - 35 * math.sin(2 * math.pi * px / 180)
        pts_st.append((x, y))
    d_st = "M " + " L ".join("%.1f,%.1f" % p for p in pts_st)
    frags.append(svg_path(d_st, fill="none", stroke=NEG, sw=2))
    frags.append(line(sx0, sy0, sx0 + 360, sy0, color=MUTED, sw=1, dash="4,3"))

    frags.append(textbox(sx0 + 90, sy0 - 50, "t=0: Максимум E_пот\n(струна розтягнута, v=0)", size=10, fill="#fee2e2", stroke=POS, sw=1)[0])
    frags.append(circle(sx0 + 180, sy0, 4, fill=INK, stroke=BG, sw=1))
    frags.append(text(sx0 + 180, sy0 + 18, "Вузол: E = 0", size=10, bold=True))
    frags.append(textbox(sx0 + 270, sy0 + 42, "t=T/4: Максимум E_кін\n(струна плоска, v=v_max)", size=10, fill="#dbeafe", stroke=NEG, sw=1)[0])

    frags.append(textbox(575, 275, "Енергія замкнена між вузлами\nперекачується локально:\nE_потенціальна ⇄ E_кінетична", size=11, fill="#f1f5f9", stroke=INK, sw=1.5)[0])

    render(out_path, w, h, *frags, title=None)


# -----------------------------------------------------------------------------
# Figure 5: swr-mismatch.svg
# -----------------------------------------------------------------------------
def gen_swr_mismatch():
    out_path = os.path.join(IMG_DIR, 'swr-mismatch.svg')
    w, h = 760, 360
    frags = []

    x0, y0 = 70, 170
    sw_len = 480
    wavelength = 240
    a1 = 60
    a2 = 30

    v_max = a1 + a2
    v_min = a1 - a2

    pts_env_top = []
    pts_env_bot = []
    for px in range(0, sw_len + 1):
        x = x0 + px
        kx = 2 * math.pi * px / (wavelength / 2)
        env_val = math.sqrt(a1 * a1 + a2 * a2 + 2 * a1 * a2 * math.cos(kx))
        pts_env_top.append((x, y0 - env_val))
        pts_env_bot.append((x, y0 + env_val))

    d_env_top = "M " + " L ".join("%.1f,%.1f" % p for p in pts_env_top)
    d_env_bot = "M " + " L ".join("%.1f,%.1f" % p for p in pts_env_bot)
    frags.append(svg_path(d_env_top, fill="none", stroke=POS, sw=1.8, dash="5,3"))
    frags.append(svg_path(d_env_bot, fill="none", stroke=POS, sw=1.8, dash="5,3"))

    pts_inst = []
    for px in range(0, sw_len + 1):
        x = x0 + px
        y_val = a1 * math.sin(2 * math.pi * px / wavelength - math.pi / 4) + a2 * math.sin(2 * math.pi * px / wavelength + math.pi / 4)
        pts_inst.append((x, y0 - y_val))
    d_inst = "M " + " L ".join("%.1f,%.1f" % p for p in pts_inst)
    frags.append(svg_path(d_inst, fill="none", stroke=NEG, sw=2))

    frags.append(line(x0 - 20, y0, x0 + sw_len + 20, y0, color=MUTED, sw=1, dash="4,4"))

    frags.append(rect(x0 + sw_len, y0 - 100, 30, 200, fill="#e2e8f0", stroke=INK, sw=1.5))
    frags.append(text(x0 + sw_len + 15, y0, "Навантаження Z_L ≠ Z₀", size=11, bold=True, anchor="middle"))

    frags.append(line(x0, y0 - v_max, x0, y0 + v_max, color=POS, sw=1.5))
    frags.append(circle(x0, y0 - v_max, 3, fill=POS, stroke=BG, sw=1))
    frags.append(circle(x0, y0 + v_max, 3, fill=POS, stroke=BG, sw=1))
    frags.append(text(x0 - 25, y0 - v_max - 8, "V_max = A₁ + A₂", size=11, bold=True, color=POS, anchor="end"))

    x_min = x0 + wavelength / 4
    frags.append(line(x_min, y0 - v_min, x_min, y0 + v_min, color=FIELD, sw=1.5))
    frags.append(circle(x_min, y0 - v_min, 3, fill=FIELD, stroke=BG, sw=1))
    frags.append(circle(x_min, y0 + v_min, 3, fill=FIELD, stroke=BG, sw=1))
    frags.append(text(x_min, y0 - v_min - 12, "V_min = A₁ − A₂", size=11, bold=True, color=FIELD))

    summary_str = "Неповне відбиття (|Γ| = 0.5)\nКоефіцієнт стоячої хвилі:\nКСХ = V_max / V_min = 90 / 30 = 3.0"
    frags.append(textbox(200, 55, summary_str, size=11, fill="#fef3c7", stroke="#d97706", sw=1.2)[0])

    render(out_path, w, h, *frags, title="Частково стояча хвиля при неузгодженому навантаженні (КСХ / SWR)")


def main():
    gen_standing_wave_nodes()
    gen_reflection_boundaries()
    gen_harmonics_modes()
    gen_energy_flow()
    gen_swr_mismatch()

if __name__ == '__main__':
    main()
