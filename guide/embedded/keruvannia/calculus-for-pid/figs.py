# -*- coding: utf-8 -*-
"""Figures for «Похідна й інтеграл для PID».
Import svgkit from scripts/ (do not copy it). Output to ./img/.
Run:  python figs.py    then  python ../../../../scripts/svgcheck.py img
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — three readings of ONE error curve: value (P), area (I), slope (D)
# A single e(t) curve; P reads its height now, I reads accumulated area, D reads
# the slope of the tangent now. The point: P, I, D are three views of the same
# signal, not three different signals.
# ════════════════════════════════════════════════════════════════════════════
def fig_three_readings():
    W, H = 640, 380
    ox, oy = 70, 250          # math origin in SVG px (t=0, e=0)
    sx = 42                   # px per time unit (t in 0..13)
    sy = 26                   # px per error unit (e in -2..6)

    def gx(t): return ox + t * sx
    def gy(e): return oy - e * sy

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # error curve e(t): starts high (+5), decays toward 0, dips slightly, recovers.
    # e(t) = 5*exp(-0.28 t) ... plus a small bump so D has both signs visibly
    import math
    def e_of(t):
        return 5.0 * math.exp(-0.30 * t) + 0.9 * math.sin(0.55 * t) * math.exp(-0.18 * t)

    # axes
    f.append(arrow(gx(-0.2), gy(0), gx(13.2), gy(0), color=INK, sw=1.5))
    f.append(text(gx(13.3), gy(0) + 5, 't', 14, INK, 'start'))
    f.append(arrow(gx(0), gy(-2.0), gx(0), gy(6.2), color=INK, sw=1.5))
    f.append(text(gx(0) - 6, gy(6.3), 'e', 14, INK, 'end'))
    f.append(text(gx(0) - 30, gy(3.0), 'похибка', 11, MUTED, 'middle'))

    # zero line label
    f.append(text(gx(13.0), gy(0) - 6, 'e = 0', 10, MUTED, 'end'))

    # ── I: shaded area under the curve up to t = tnow (the accumulated integral)
    # pick a "now" where the curve is still descending steeply, so the D-tangent
    # visibly slopes down — height (P), area (I) and slope (D) all clearly differ.
    tnow = 3.4
    N = 120
    area_pts = ['%.1f,%.1f' % (gx(0), gy(0))]
    t = 0.0
    while t <= tnow + 1e-9:
        area_pts.append('%.1f,%.1f' % (gx(t), gy(e_of(t))))
        t += tnow / N
    area_pts.append('%.1f,%.1f' % (gx(tnow), gy(0)))
    f.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="none"/>'
             % (' '.join(area_pts), NEG))

    # ── the error curve itself
    curve = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        curve.append('%.1f,%.1f' % (gx(t), gy(e_of(t))))
        t += 13.0 / 240
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(curve), INK))

    # ── P: current height — vertical drop from curve to axis at tnow
    enow = e_of(tnow)
    f.append(line(gx(tnow), gy(0), gx(tnow), gy(enow), color=POS, sw=2.0, dash='4,3'))
    f.append(circle(gx(tnow), gy(enow), 4.5, fill=POS, stroke=INK, sw=1.2))
    f.append(text(gx(tnow) + 10, gy(enow) - 16, 'P: висота зараз', 11, POS, 'start'))
    f.append(text(gx(tnow) + 10, gy(enow) - 1, 'e(t)', 10, POS, 'start'))

    # ── D: tangent slope at tnow (numeric derivative)
    h = 0.05
    slope = (e_of(tnow + h) - e_of(tnow - h)) / (2 * h)
    # draw tangent segment of horizontal half-width dt time units
    dt = 1.9
    tx0, tx1 = tnow - dt, tnow + dt
    ty0, ty1 = enow + slope * (tx0 - tnow), enow + slope * (tx1 - tnow)
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.2"/>' % (gx(tx0), gy(ty0), gx(tx1), gy(ty1), FIELD))
    f.append(text(gx(tx1) + 6, gy(ty1) + 4, 'D: нахил зараз', 11, FIELD, 'start'))
    f.append(text(gx(tx1) + 6, gy(ty1) + 19, '(de/dt < 0)', 10, FIELD, 'start'))

    # ── I label inside the shaded area
    f.append(text(gx(1.55), gy(0) + 22, 'I: площа', 11, NEG, 'middle'))
    f.append(text(gx(1.55), gy(0) + 36, 'досі', 11, NEG, 'middle'))

    # tick on t axis at tnow
    f.append(line(gx(tnow), gy(0) - 4, gx(tnow), gy(0) + 4, color=INK, sw=1))
    f.append(text(gx(tnow), gy(0) + 18, 'зараз', 10, INK, 'middle'))

    # caption
    f.append(text(W // 2, H - 8,
                  'Одна крива похибки — три покази: P бере висоту, I — площу досі, D — нахил',
                  10, MUTED, 'middle'))

    render(os.path.join(IMG, 'three-readings.svg'), W, H, *f,
           title='P, I, D — три погляди на ту саму похибку e(t)')


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — why I removes steady-state error.
# Top: P-only response settles BELOW setpoint (a permanent gap).
# Adding I, the accumulator keeps growing while the gap exists, lifting output
# until the gap closes — then the accumulator holds its value.
# Two stacked panels sharing the time axis.
# ════════════════════════════════════════════════════════════════════════════
def fig_integral_closes_gap():
    import math
    W, H = 640, 430

    # ---- panel A (process value vs setpoint)
    axL, axR = 70, W - 20
    aT, aB = 56, 210           # top panel y-range (px)
    sx = (axR - axL) / 13.0    # px per time unit

    def gx(t): return axL + t * sx

    setpoint = 1.0
    # P-only: first-order rise to a value below setpoint (offset)
    p_final = 0.72
    def pv_p(t):  return p_final * (1 - math.exp(-0.6 * t))
    # P+I: rises then the integral term drags it up to setpoint with mild overshoot
    def pv_pi(t):
        base = p_final * (1 - math.exp(-0.6 * t))
        ramp = (setpoint - p_final) * (1 - math.exp(-0.42 * (t)))
        over = 0.12 * math.sin(0.9 * t) * math.exp(-0.4 * t)
        return base + ramp + over

    def yA(v):   # map process value (0..1.25) into panel A
        vmin, vmax = 0.0, 1.30
        return aB - (v - vmin) / (vmax - vmin) * (aB - aT)

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # panel A frame baseline + setpoint line
    f.append(arrow(axL - 4, yA(0), axR + 4, yA(0), color=INK, sw=1.4))
    f.append(arrow(axL, aB + 4, axL, aT - 6, color=INK, sw=1.4))
    f.append(line(axL, yA(setpoint), axR, yA(setpoint), color=MUTED, sw=1.3, dash='6,4'))
    f.append(text(axR, yA(setpoint) - 6, 'ціль (уставка)', 10, MUTED, 'end'))
    f.append(text(axL - 8, (aT + aB) / 2, 'вихід', 11, MUTED, 'middle'))

    # P-only curve
    cp = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        cp.append('%.1f,%.1f' % (gx(t), yA(pv_p(t))))
        t += 13.0 / 220
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7,4"/>' % (' '.join(cp), POS))

    # P+I curve
    cpi = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        cpi.append('%.1f,%.1f' % (gx(t), yA(pv_pi(t))))
        t += 13.0 / 220
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(cpi), FIELD))

    # the residual gap bracket (P-only) at right
    tgap = 12.0
    f.append(line(gx(tgap), yA(pv_p(tgap)), gx(tgap), yA(setpoint), color=POS, sw=1.6))
    f.append(text(gx(tgap) - 6, (yA(pv_p(tgap)) + yA(setpoint)) / 2, 'стала', 10, POS, 'end'))
    f.append(text(gx(tgap) - 6, (yA(pv_p(tgap)) + yA(setpoint)) / 2 + 12, 'похибка', 10, POS, 'end'))

    # legend for panel A
    lx, ly = axL + 14, aT + 4
    f.append(rect(lx - 6, ly - 2, 196, 40, fill='#f8f9fa', stroke=MUTED, sw=1, rx=5))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.4" stroke-dasharray="7,4"/>'
             % (lx, ly + 9, lx + 22, ly + 9, POS))
    f.append(text(lx + 28, ly + 13, 'лише P — лишається зазор', 10, INK, 'start'))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.6"/>'
             % (lx, ly + 27, lx + 22, ly + 27, FIELD))
    f.append(text(lx + 28, ly + 31, 'P + I — зазор закривається', 10, INK, 'start'))

    # ---- panel B (the integral accumulator value)
    bT, bB = 268, 392
    def yB(v):
        vmin, vmax = 0.0, 1.0
        return bB - (v - vmin) / (vmax - vmin) * (bB - bT)

    f.append(arrow(axL - 4, yB(0), axR + 4, yB(0), color=INK, sw=1.4))
    f.append(arrow(axL, bB + 4, axL, bT - 6, color=INK, sw=1.4))
    f.append(text(axL - 8, (bT + bB) / 2, 'нагром.', 11, NEG, 'middle'))
    f.append(text(gx(13.0), yB(0) + 16, 'час →', 10, MUTED, 'end'))

    # accumulator = running integral of (setpoint - pv_pi); grows while gap>0, flattens at close
    acc = []
    s = 0.0
    dt = 13.0 / 260
    t = 0.0
    samples = []
    while t <= 13.0 + 1e-9:
        err = setpoint - pv_pi(t)
        s += err * dt
        samples.append((t, s))
        t += dt
    smax = max(v for _, v in samples) or 1.0
    for (tt, vv) in samples:
        acc.append('%.1f,%.1f' % (gx(tt), yB(vv / smax * 0.92)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(acc), NEG))
    f.append(text(gx(6.5), yB(0.88), 'інтеграл росте, поки є похибка', 10, NEG, 'middle'))
    f.append(text(gx(11.4), yB(0.55), 'похибка→0:', 10, NEG, 'middle'))
    f.append(text(gx(11.4), yB(0.40), 'нагром. завмирає', 10, NEG, 'middle'))

    # panel titles
    f.append(text(W // 2, 30, 'Інтеграл прибирає сталу похибку', 16, INK, 'middle', bold=True))
    f.append(text(W // 2, 250, 'а ось що робить накопичувач I весь цей час:', 11, MUTED, 'middle'))
    f.append(text(W // 2, H - 6,
                  'Поки лишається зазор, накопичувач росте й піднімає вихід; зазор зник — він завмер',
                  10, MUTED, 'middle'))

    render(os.path.join(IMG, 'integral-closes-gap.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — integral windup.
# Actuator saturates (clamped at 100%). Error persists because the plant can't
# keep up; the unclamped integral keeps piling up far beyond what's useful, so
# when the error finally flips sign the huge accumulator drives a big overshoot.
# Clamped integral stays bounded → small overshoot.
# ════════════════════════════════════════════════════════════════════════════
def fig_windup():
    import math
    W, H = 640, 420
    axL, axR = 70, W - 20
    sx = (axR - axL) / 13.0
    def gx(t): return axL + t * sx

    # ---- panel A: process value chasing a big setpoint step, two cases
    aT, aB = 60, 215
    sp = 1.0
    def yA(v):
        vmin, vmax = 0.0, 1.55
        return aB - (v - vmin) / (vmax - vmin) * (aB - aT)

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(arrow(axL - 4, yA(0), axR + 4, yA(0), color=INK, sw=1.4))
    f.append(arrow(axL, aB + 4, axL, aT - 6, color=INK, sw=1.4))
    f.append(line(axL, yA(sp), axR, yA(sp), color=MUTED, sw=1.3, dash='6,4'))
    f.append(text(axR, yA(sp) - 6, 'ціль', 10, MUTED, 'end'))
    f.append(text(axL - 8, (aT + aB) / 2, 'вихід', 11, MUTED, 'middle'))

    # windup case: slow rise (actuator saturated), then large overshoot, slow settle
    def pv_windup(t):
        rise = sp * 1.0 * (1 - math.exp(-0.45 * t))
        # overshoot hump centered ~ t=8 caused by bloated accumulator
        hump = 0.52 * math.exp(-((t - 8.2) ** 2) / 5.0)
        return min(1.55, rise) + hump - 0.0
    # clamped case: similar slow rise, tiny overshoot
    def pv_clamp(t):
        rise = sp * 1.0 * (1 - math.exp(-0.45 * t))
        hump = 0.10 * math.exp(-((t - 7.0) ** 2) / 4.0)
        return rise + hump

    cw = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        cw.append('%.1f,%.1f' % (gx(t), yA(pv_windup(t))))
        t += 13.0 / 240
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(cw), POS))

    cc = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        cc.append('%.1f,%.1f' % (gx(t), yA(pv_clamp(t))))
        t += 13.0 / 240
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7,4"/>' % (' '.join(cc), FIELD))

    # overshoot marker
    f.append(text(gx(8.2), yA(pv_windup(8.2)) - 8, 'великий викид', 10, POS, 'middle'))

    # legend
    lx, ly = axL + 12, aT - 2
    f.append(rect(lx - 6, ly - 2, 232, 40, fill='#f8f9fa', stroke=MUTED, sw=1, rx=5))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.6"/>'
             % (lx, ly + 9, lx + 22, ly + 9, POS))
    f.append(text(lx + 28, ly + 13, 'без обмеження I (насичення)', 10, INK, 'start'))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.4" stroke-dasharray="7,4"/>'
             % (lx, ly + 27, lx + 22, ly + 27, FIELD))
    f.append(text(lx + 28, ly + 31, 'з обмеженням накопичувача', 10, INK, 'start'))

    # ---- panel B: accumulator value, unclamped balloons vs clamped flat-top
    bT, bB = 272, 388
    def yB(v):
        vmin, vmax = 0.0, 1.0
        return bB - (v - vmin) / (vmax - vmin) * (bB - bT)
    f.append(arrow(axL - 4, yB(0), axR + 4, yB(0), color=INK, sw=1.4))
    f.append(arrow(axL, bB + 4, axL, bT - 6, color=INK, sw=1.4))
    f.append(text(axL - 8, (bT + bB) / 2, 'нагром.', 11, NEG, 'middle'))
    f.append(text(gx(13.0), yB(0) + 16, 'час →', 10, MUTED, 'end'))

    # unclamped: keeps integrating while saturated → grows large, then unwinds slowly
    accU = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        # grows ~linearly while error positive (t<7.5), then slowly unwinds
        if t < 7.5:
            v = 0.12 * t
        else:
            v = 0.12 * 7.5 - 0.10 * (t - 7.5)
            v = max(0.0, v)
        accU.append('%.1f,%.1f' % (gx(t), yB(min(0.95, v))))
        t += 13.0 / 240
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' '.join(accU), POS))

    # clamped: rises then hits the clamp ceiling and flattens
    clampv = 0.42
    accC = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        v = min(clampv, 0.12 * t)
        # after error clears, drops a bit
        if t > 8.0:
            v = max(0.0, clampv - 0.05 * (t - 8.0))
        accC.append('%.1f,%.1f' % (gx(t), yB(v)))
        t += 13.0 / 240
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7,4"/>' % (' '.join(accC), FIELD))
    f.append(line(axL, yB(clampv), axR, yB(clampv), color=MUTED, sw=1.0, dash='3,3'))
    f.append(text(axR, yB(clampv) - 5, 'стеля clamp', 10, MUTED, 'end'))
    f.append(text(gx(5.6), yB(0.85), 'без clamp: роздувається', 10, POS, 'middle'))

    f.append(text(W // 2, 30, 'Інтегральне насичення (windup)', 16, INK, 'middle', bold=True))
    f.append(text(W // 2, 250, 'причина — у накопичувачі, що ріс під час насичення:', 11, MUTED, 'middle'))
    f.append(text(W // 2, H - 6,
                  'Виконавчий орган уперся в межу, а I все накопичує — роздутий запас потім дає викид',
                  10, MUTED, 'middle'))

    render(os.path.join(IMG, 'windup.svg'), W, H, *f)


if __name__ == '__main__':
    fig_three_readings()
    fig_integral_closes_gap()
    fig_windup()
    print('Done.')
