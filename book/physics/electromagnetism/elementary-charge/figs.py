# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — quantization staircase: free charge sits ONLY on integer multiples
# of e; the gaps are forbidden. Quark fractions live "inside", shown shaded off.
# ═══════════════════════════════════════════════════════════════════════════
def fig_quantization():
    W, H = 660, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # horizontal axis = charge value q
    ax_y = 215
    x0, x1 = 60, W - 40
    f.append(arrow(x0 - 10, ax_y, x1 + 10, ax_y, color=INK, sw=1.6))
    f.append(text(x1 + 18, ax_y + 5, 'q', 15, INK, 'start', italic=True))

    # allowed levels: -3e .. +3e, evenly spaced
    levels = [-3, -2, -1, 0, 1, 2, 3]
    cx_zero = (x0 + x1) / 2
    step = 80
    def px(n): return cx_zero + n * step

    # forbidden zone shading between ticks (light wash) + "заборонено" hint once
    for n in range(-3, 3):
        xa, xb = px(n) + 13, px(n + 1) - 13
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fbeaea" '
                 'opacity="0.55" rx="3"/>' % (xa, ax_y - 30, xb - xa, 26))

    # ticks + balls on each allowed level
    for n in levels:
        x = px(n)
        f.append(line(x, ax_y - 7, x, ax_y + 7, color=INK, sw=1.4))
        col = NEG if n < 0 else (POS if n > 0 else MUTED)
        # marker dot on the level (a "rung")
        f.append(circle(x, ax_y - 40, 9, fill=('#eaf0fd' if n < 0 else ('#fdecea' if n > 0 else '#eef0f2')),
                        stroke=col, sw=2))
        # tidy labels
        if n == 0:
            lab = '0'
        elif n == 1:
            lab = '+e'
        elif n == -1:
            lab = '−e'
        else:
            lab = ('+%de' % n) if n > 0 else ('−%de' % abs(n))
        f.append(text(x, ax_y + 26, lab, 14, col, 'middle', bold=True))

    # title-line above the rungs
    f.append(text(W / 2, 60,
                  'Вільний заряд буває лише цілим кратним e', 16, INK, 'middle', bold=True))
    f.append(text(W / 2, 84,
                  'між сходинками — порожньо: значень на кшталт +1.5e не існує', 12, MUTED, 'middle'))

    # the forbidden example marker: +1.5e with a cross
    xf = px(1.5)
    f.append(circle(xf, ax_y - 40, 8, fill='#ffffff', stroke=MUTED, sw=1.6))
    f.append(line(xf - 6, ax_y - 46, xf + 6, ax_y - 34, color=POS, sw=2.2))
    f.append(line(xf - 6, ax_y - 34, xf + 6, ax_y - 46, color=POS, sw=2.2))
    f.append(text(xf, ax_y - 58, '+1.5e', 12, POS, 'middle'))
    f.append(text(xf, ax_y - 72, 'нема', 11, POS, 'middle'))

    # bottom note about quarks (the only sub-e thing, but confined)
    by = 292
    f.append(fitbox(x0 - 10, by, x1 + 10 - (x0 - 10), 54,
                    'Усередині протонів і нейтронів живуть кварки з дробовими ⅓ та ⅔ e,\n'
                    'але вони замкнені (конфайнмент) і вільно не виходять;\n'
                    'будь-який вільний заряд лишається цілим кратним e.',
                    size=12, color=INK, fill='#f4f6f8', stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'quantization.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — quarks combine to integer charge: proton (uud) and neutron (udd).
# Fractions inside sum to +1 and 0. Shows WHY confinement hides the fractions.
# ═══════════════════════════════════════════════════════════════════════════
def fig_quarks():
    W, H = 660, 330
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 34, 'Дробові кварки складаються в цілий заряд',
                  16, INK, 'middle', bold=True))

    def quark(cx, cy, name, q, col):
        r = 26
        out = circle(cx, cy, r, fill=('#fdecea' if '+' in q else '#eaf0fd'), stroke=col, sw=2.2)
        out += text(cx, cy - 2, name, 17, col, 'middle', bold=True, italic=True)
        out += text(cx, cy + 15, q, 11, col, 'middle')
        return out

    def nucleon(cx, cy, title, quarks, total, total_col):
        out = []
        # binding "bag"
        out.append('<rect x="%.1f" y="%.1f" width="150" height="150" rx="26" '
                   'fill="#f4f6f8" stroke="%s" stroke-width="1.8"/>' % (cx - 75, cy - 60, MUTED))
        out.append(text(cx, cy - 44, title, 14, INK, 'middle', bold=True))
        # three quarks in a triangle
        pos = [(cx - 38, cy + 8), (cx + 38, cy + 8), (cx, cy + 56)]
        for (qx, qy), (nm, q, col) in zip(pos, quarks):
            out.append(quark(qx, qy, nm, q, col))
        return out, (cx, cy)

    # proton uud → +e ; neutron udd → 0
    px, py = 175, 150
    nx, ny = 485, 150
    p_q = [('u', '+⅔e', POS), ('u', '+⅔e', POS), ('d', '−⅓e', NEG)]
    n_q = [('u', '+⅔e', POS), ('d', '−⅓e', NEG), ('d', '−⅓e', NEG)]
    pf, _ = nucleon(px, py, 'Протон  (u u d)', p_q, '+e', POS)
    nf, _ = nucleon(nx, ny, 'Нейтрон  (u d d)', n_q, '0', MUTED)
    f += pf + nf

    # sum lines under each
    f.append(text(px, py + 108, '⅔ + ⅔ − ⅓ = +1', 14, INK, 'middle'))
    f.append(text(px, py + 130, 'разом  +e', 15, POS, 'middle', bold=True))
    f.append(text(nx, ny + 108, '⅔ − ⅓ − ⅓ = 0', 14, INK, 'middle'))
    f.append(text(nx, ny + 130, 'разом  0', 15, MUTED, 'middle', bold=True))

    render(os.path.join(IMG, 'quarks.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — the coulomb's scale & the 2019 SI definition: the coulomb is now
# DEFINED by fixing e exactly. One coulomb ≈ 6.24×10¹⁸ e.
# ═══════════════════════════════════════════════════════════════════════════
def fig_coulomb_scale():
    W, H = 660, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 34, 'Кулон тепер означено через e',
                  16, INK, 'middle', bold=True))

    # left: the defining constant box
    lb = fitbox(40, 70, 250, 70,
                'e = 1.602 176 634 × 10⁻¹⁹ Кл\n(зафіксовано точно з 2019 р.)',
                size=13, color=INK, fill='#eef7f0', stroke=FIELD, sw=1.8, bold=False)
    f.append(lb)

    # arrow defines →
    f.append(arrow(300, 105, 372, 105, color=INK, sw=2))
    f.append(text(336, 95, 'означує', 11, MUTED, 'middle'))

    # right: the coulomb box
    rb = fitbox(380, 70, 240, 70,
                '1 Кл = заряд\n6.241 509 × 10¹⁸ елементарних e',
                size=13, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.6)
    f.append(rb)

    # bottom: a magnitude ladder of charges (log-ish, illustrative)
    base_y = 250
    f.append(line(60, base_y, W - 40, base_y, color=INK, sw=1.5))
    ladder = [
        (90,  '1 e',            '1.6×10⁻¹⁹ Кл', NEG),
        (220, 'статика на тілі', '≈10⁻⁷ Кл',     MUTED),
        (350, 'імпульс ESD',    '≈10⁻⁶ Кл',     POS),
        (470, '1 А·год батареї', '3600 Кл',      FIELD),
        (590, 'розряд блискавки', '≈15 Кл',      POS),
    ]
    for x, name, val, col in ladder:
        f.append(line(x, base_y - 6, x, base_y + 6, color=col, sw=2))
        f.append(circle(x, base_y - 40, 6, fill='#ffffff', stroke=col, sw=2))
        f.append(line(x, base_y - 34, x, base_y - 6, color=col, sw=1, dash='3,3'))
        f.append(text(x, base_y - 52, name, 11, INK, 'middle'))
        f.append(text(x, base_y + 22, val, 10, col, 'middle'))

    f.append(text(W / 2, base_y + 70,
                  'Кулон — велетенська порція: один кулон складають понад шість мільярдів мільярдів електронів',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'coulomb-scale.svg'), W, H, *f)


fig_quantization()
fig_quarks()
fig_coulomb_scale()
print('Done.')
