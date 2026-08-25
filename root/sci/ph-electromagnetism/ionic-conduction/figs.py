# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def path(d, color=INK, sw=3.0, fill='none', dash=None):
    dd = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round"%s/>' % (d, fill, color, sw, dd))


# ═══════════════════════════════════════════════════════════════════════════
# Figure — the defining trait of ionic conduction: at the electrode the ion
# stops being a carrier and BECOMES matter. A Cu²⁺ ion reaches the cathode,
# grabs 2 electrons and deposits as a neutral copper atom. So charge passed ↔
# substance transformed (Faraday). This is what a metal never does.
# ═══════════════════════════════════════════════════════════════════════════
def fig_electrode_reaction():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'На електроді іон стає речовиною: струм працює хімічно', 17, INK, 'middle', bold=True))

    # cell (solution)
    cx0, cy0, cx1, cy1 = 150, 95, 610, 300
    f.append(rect(cx0, cy0, cx1 - cx0, cy1 - cy0, fill='#eef4fb', stroke=NEG, sw=1.4, rx=10))
    f.append(text((cx0 + cx1) / 2, cy1 - 12, 'розчин солі міді', 12, MUTED, 'middle'))

    # electrodes
    ax = 168   # anode (+), left
    kx = 592   # cathode (−), right
    f.append(rect(ax - 9, 110, 18, 175, fill='#f3d9d6', stroke=POS, sw=1.6, rx=3))
    f.append(rect(kx - 9, 110, 18, 175, fill='#d9e2f6', stroke=NEG, sw=1.6, rx=3))
    f.append(plus(ax, 128, 9))
    f.append(minus(kx, 128, 9))
    f.append(text(ax, 302, 'анод', 12, POS, 'middle'))
    f.append(text(kx, 302, 'катод', 12, NEG, 'middle'))

    # deposited copper layer building on the cathode (solution side = left face)
    for i in range(5):
        yy = 150 + i * 26
        f.append(rect(kx - 22, yy, 12, 12, fill='#c0733a', stroke='#8a4f22', sw=1.0, rx=2))

    # drifting Cu²⁺ ions heading to the cathode
    for (ix, iy) in [(300, 165), (380, 225), (330, 265)]:
        f.append(circle(ix, iy, 12, fill='#fdecea', stroke=POS, sw=1.8))
        f.append(text(ix, iy + 4, 'Cu', 11, POS, 'middle', bold=True))
        f.append(arrow(ix + 16, iy, ix + 56, iy, color=POS, sw=1.8))

    # external electron flow into the cathode (top wire)
    f.append(line(ax, 96, ax, 66, color=INK, sw=1.6))
    f.append(line(ax, 66, kx, 66, color=INK, sw=1.6))
    f.append(line(kx, 66, kx, 96, color=INK, sw=1.6))
    f.append(arrow(kx - 120, 66, kx - 60, 66, color=NEG, sw=1.8))
    f.append(text((ax + kx) / 2 - 40, 58, 'електрони по дроту →', 12, NEG, 'middle'))

    # reaction label near the cathode surface, clear of arrows
    f.append(fitbox(400, 118, 150, 30, 'Cu²⁺ + 2e⁻ → Cu', size=13,
                    fill='#fff7ee', stroke='#c0733a', color='#8a4f22', bold=True))

    # bottom takeaway
    f.append(fitbox(150, 336, 460, 46,
                    'Іон дійшов до електрода → віддав/забрав електрони → став нейтральним атомом і осів.\n'
                    'Скільки заряду пройшло — стільки речовини перетворилось (закон Фарадея).',
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'electrode-reaction.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure — the temperature fingerprint. A metal's resistance RISES with heat
# (lattice vibrations scatter the electrons); an electrolyte's resistance FALLS
# (the liquid thins, more ions break free). Opposite signs reveal who carries.
# ═══════════════════════════════════════════════════════════════════════════
def fig_temperature():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Нагрів: у металі опір росте, в електроліті — падає', 17, INK, 'middle', bold=True))

    def axes(ox, oy, tx, ty):
        g = []
        g.append(arrow(ox, oy, ox, ty, color=INK, sw=1.6))      # y up
        g.append(arrow(ox, oy, tx, oy, color=INK, sw=1.6))      # x right
        return g

    # left panel — metal
    ox, oy = 95, 300
    f += axes(ox, oy, 340, 110)
    f.append(text(ox - 6, 105, 'опір', 12, MUTED, 'end'))
    f.append(text(345, oy + 18, 't°', 12, MUTED, 'middle'))
    f.append(path('M105,278 L330,150', color=NEG, sw=3.2))
    f.append(text(190, 180, 'метал', 13, NEG, 'middle', bold=True))
    f.append(fitbox(70, 322, 280, 44,
                    'МЕТАЛ: гарячіша ґратка дужче коливається\nй сильніше розсіює електрони → опір ↑',
                    size=12, fill='#eef2fb', stroke=NEG))

    # right panel — electrolyte
    ox2 = 470
    f += axes(ox2, oy, 715, 110)
    f.append(text(ox2 - 6, 105, 'опір', 12, MUTED, 'end'))
    f.append(text(720, oy + 18, 't°', 12, MUTED, 'middle'))
    f.append(path('M480,140 Q560,250 705,285', color=FIELD, sw=3.2))
    f.append(text(605, 188, 'електроліт', 13, FIELD, 'middle', bold=True))
    f.append(fitbox(452, 322, 285, 44,
                    'ЕЛЕКТРОЛІТ: тепліша рідина рідшає, іони\nрухливіші й численніші → опір ↓',
                    size=12, fill='#eaf7ef', stroke=FIELD))

    render(os.path.join(IMG, 'temperature.svg'), W, H, *f)


fig_electrode_reaction()
fig_temperature()
print('Done.')
