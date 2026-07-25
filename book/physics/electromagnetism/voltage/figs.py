# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ═══════════════════════════════════════════════════════════════════════════
# Figure — energy landscape: voltage is a height on a map of potential.
# Source (EMF) lifts each coulomb by U (energy in); the charge rolls down the
# load ramp and releases the same U (energy out). The vertical gap U = the voltage.
# ═══════════════════════════════════════════════════════════════════════════
def fig_energy_landscape():
    W, H = 700, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Напруга — перепад висот на мапі потенціалу', 17, INK, 'middle', bold=True))

    y_hi, y_lo = 120, 300

    # the two levels (dashed guides spanning to the U-bracket at right)
    f.append(line(110, y_hi, 665, y_hi, color=MUTED, sw=1.3, dash='6,5'))
    f.append(line(110, y_lo, 665, y_lo, color=MUTED, sw=1.3, dash='6,5'))
    f.append(text(112, y_hi - 8, 'високий потенціал (+)', 12, POS, 'start'))
    f.append(text(648, y_lo - 8, 'низький потенціал (−)', 12, NEG, 'end'))

    # source: EMF lifts a coulomb from low to high
    f.append(arrow(150, y_lo, 150, y_hi, color=FIELD, sw=2.6))
    f.append(plus(188, 210))
    sb, sw_, sh_ = textbox(150, 342, 'джерело (ЕРС)\nвкладає U на кулон',
                           size=12, fill='#eef7f0', stroke=FIELD, sw=1.4)
    f.append(sb)

    # top platform: the charge travels along the high level
    f.append(plus(295, 105))

    # load: the ramp downhill; the charge releases U
    f.append(arrow(320, y_hi, 540, y_lo, color=LINE, sw=2.6))
    f.append(plus(380, 150))
    lb, _, _ = textbox(600, 262, 'навантаження:\nвіддає U на кулон',
                       size=12, fill=FILL, stroke=LINE, sw=1.4)
    f.append(lb)

    # U bracket on the right between the two levels
    f.append(line(665, y_hi, 665, y_lo, color=INK, sw=1.6))
    f.append(arrow(665, y_hi + 18, 665, y_hi, color=INK, sw=1.6))
    f.append(arrow(665, y_lo - 18, 665, y_lo, color=INK, sw=1.6))
    f.append(text(650, 208, 'U', 20, INK, 'end', bold=True, italic=True))
    f.append(text(650, 228, 'напруга', 12, MUTED, 'end'))

    render(os.path.join(IMG, 'energy-landscape.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure — measuring: voltage ACROSS (voltmeter in parallel), current THROUGH
# (ammeter in series). Voltage is a difference between two points, so it is read
# from the side without breaking the circuit; current needs a break.
# ═══════════════════════════════════════════════════════════════════════════
def fig_measure_across():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Напругу міряють упоперек, струм — наскрізь', 17, INK, 'middle', bold=True))

    L, R, T, B = 150, 520, 120, 300

    # loop wires (with gaps for ammeter, battery, resistor)
    f.append(line(L, T, 315, T))              # top-left
    f.append(line(355, T, R, T))              # top-right
    f.append(line(L, B, R, B))                # bottom
    f.append(line(L, T, L, 203))              # left-upper
    f.append(line(L, 217, L, B))              # left-lower
    f.append(line(R, T, R, 172))              # right-upper
    f.append(line(R, 248, R, B))              # right-lower

    # battery (left)
    f.append(line(135, 203, 165, 203, color=INK, sw=2))
    f.append(line(143, 217, 157, 217, color=INK, sw=4))
    f.append(text(120, 214, 'джерело', 13, INK, 'end'))

    # resistor (right)
    f.append(rect(509, 172, 22, 76, fill=FILL, stroke=INK, sw=1.8, rx=3))
    f.append(text(500, 214, 'R', 15, INK, 'end', italic=True))

    # ammeter — in series (breaks the top wire)
    f.append(circle(335, T, 20, fill='#fdf6e3', stroke=INK, sw=1.8))
    f.append(text(335, 127, 'A', 20, INK, 'middle', bold=True))
    ab, _, _ = textbox(335, 63, 'амперметр — наскрізь\n(у розриві кола)',
                       size=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(ab)

    # voltmeter — in parallel (across the resistor)
    f.append(line(R, 172, 600, 172))
    f.append(line(600, 172, 600, 190))
    f.append(line(R, 248, 600, 248))
    f.append(line(600, 248, 600, 230))
    f.append(circle(600, 210, 22, fill='#eef2fb', stroke=NEG, sw=1.8))
    f.append(text(600, 217, 'V', 20, NEG, 'middle', bold=True))
    vb, _, _ = textbox(600, 300, 'вольтметр — впоперек\n(паралельно)',
                       size=12, fill='#eef2fb', stroke=NEG, sw=1.3)
    f.append(vb)

    # current direction + high-impedance note
    f.append(arrow(360, B, 300, B, color=POS, sw=2))
    f.append(text(332, 290, 'I', 13, POS, 'middle', italic=True))
    nb, _, _ = textbox(335, 333, 'ідеальний вольтметр\nмайже не бере струму',
                       size=12, fill='#f6f7f9', stroke=MUTED, sw=1.2)
    f.append(nb)

    render(os.path.join(IMG, 'measure-across.svg'), W, H, *f)


fig_energy_landscape()
fig_measure_across()
print('Done.')
