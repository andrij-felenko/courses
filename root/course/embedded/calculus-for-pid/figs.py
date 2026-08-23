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


# ════════════════════════════════════════════════════════════════════════════
# Figure 4 (detailed) — why the derivative amplifies noise.
# Left: time picture — slow useful error signal with fine high-frequency noise on
# top. Right: frequency picture — d/dt multiplies every component's amplitude by
# its frequency w, so the low useful frequency stays small while the high-freq
# noise blows up into a tall spike. The point: differentiation has unbounded gain
# that rises linearly with frequency.
# ════════════════════════════════════════════════════════════════════════════
def fig_derivative_noise_gain():
    import math
    W, H = 680, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 26, 'Чому похідна підсилює шум', 16, INK, 'middle', bold=True))

    # ── LEFT panel: time domain ──────────────────────────────────────────────
    Lx, Ly = 60, 250          # origin of left plot
    Lw = 250                  # width
    sx = Lw / 12.0
    sy = 20.0

    def lx(t): return Lx + t * sx
    def ly(v): return Ly - v * sy

    f.append(text(Lx + Lw / 2, 58, 'у часі', 12, MUTED, 'middle'))
    f.append(arrow(lx(-0.2), ly(0), lx(12.3), ly(0), color=INK, sw=1.4))
    f.append(text(lx(12.4), ly(0) + 5, 't', 13, INK, 'start'))
    f.append(arrow(lx(0), ly(-1.0), lx(0), ly(6.0), color=INK, sw=1.4))

    # slow useful signal + fine fast noise on top
    def base(t): return 4.0 * math.exp(-0.16 * t) + 0.6
    pts = []
    t = 0.0
    while t <= 12.0 + 1e-9:
        noise = 0.45 * math.sin(9.0 * t) + 0.28 * math.sin(15.0 * t + 1.0)
        pts.append('%.1f,%.1f' % (lx(t), ly(base(t) + noise)))
        t += 12.0 / 300
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (' '.join(pts), INK))
    # smooth underlying signal (what we actually want)
    sp = []
    t = 0.0
    while t <= 12.0 + 1e-9:
        sp.append('%.1f,%.1f' % (lx(t), ly(base(t))))
        t += 12.0 / 120
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="6,4"/>' % (' '.join(sp), NEG))
    b1, w1, h1 = textbox(lx(7.6), ly(4.7), 'дрібне швидке\nтремтіння = шум', 9.5,
                         pad=5, fill='#fff', stroke=MUTED, sw=1.0, color=INK)
    f.append(b1)
    f.append(text(lx(6.2), ly(0.2) + 16, 'повільний корисний сигнал', 9.5, NEG, 'middle'))

    # ── RIGHT panel: frequency domain, gain of d/dt = w ───────────────────────
    Rx, Ry = 400, 250
    Rw = 230
    fx = Rw / 12.0
    fyv = 20.0

    def rx(w): return Rx + w * fx
    def ry(a): return Ry - a * fyv

    f.append(text(Rx + Rw / 2, 58, 'у частоті: |d/dt| = ω', 12, MUTED, 'middle'))
    f.append(arrow(rx(-0.2), ry(0), rx(12.3), ry(0), color=INK, sw=1.4))
    f.append(text(rx(12.4), ry(0) + 5, 'ω', 13, INK, 'start'))
    f.append(arrow(rx(0), ry(-0.3), rx(0), ry(6.0), color=INK, sw=1.4))
    f.append(text(rx(0) - 6, ry(6.1), 'амплітуда', 10, INK, 'end'))

    # the gain line: amplitude out = amplitude_in * w. Show the diagonal w-line.
    f.append(line(rx(0), ry(0), rx(11.0), ry(5.5), color=MUTED, sw=1.2, dash='4,3'))
    f.append(text(rx(9.6), ry(5.5) - 4, 'множник ω', 9.5, MUTED, 'middle'))

    # low useful frequency: small input -> small output
    wl = 1.3
    f.append(line(rx(wl), ry(0), rx(wl), ry(0.9), color=NEG, sw=3.0))
    f.append(circle(rx(wl), ry(0.9), 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(rx(wl), ry(0.9) - 8, 'сигнал', 9.5, NEG, 'middle'))

    # high noise frequency: same-ish input -> huge output (blown up by *w)
    wh = 9.0
    f.append(line(rx(wh), ry(0), rx(wh), ry(5.0), color=POS, sw=3.0))
    f.append(circle(rx(wh), ry(5.0), 3.5, fill=POS, stroke=POS, sw=1))
    b2, w2, h2 = textbox(rx(wh) - 2, ry(5.0) - 20, 'шум\nроздувається', 9.5,
                         pad=5, fill='#fff', stroke=POS, sw=1.0, color=POS)
    f.append(b2)

    f.append(text(W // 2, H - 8,
                  'Оператор d/dt множить амплітуду кожної частоти на ω — тому дрібний '
                  'високочастотний шум роздувається найдужче',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'derivative-noise-gain.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure 5 (detailed) — three anti-windup strategies on one big setpoint step.
# Top: output. No anti-windup = big overshoot + long settle; clamping = smaller
# overshoot; back-calculation (tracking) = almost no overshoot, fastest settle.
# Bottom: the integrator accumulator — unprotected blows up linearly during
# saturation, clamped hits a ceiling, tracking eases to the right level.
# ════════════════════════════════════════════════════════════════════════════
def fig_antiwindup_compare():
    import math
    W, H = 680, 470
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 26, 'Три стратегії проти насичення', 16, INK, 'middle', bold=True))

    axL, axR = 70, W - 30
    span = axR - axL

    def gx(t): return axL + (t / 13.0) * span

    # ── TOP: output vs setpoint ───────────────────────────────────────────────
    tY0, tY1 = 60, 230        # top plot band (y px, high value = tY0)
    setp = 1.0

    def yT(v): return tY1 - (v / 1.5) * (tY1 - tY0)   # v in 0..1.5

    f.append(line(axL, yT(setp), axR, yT(setp), color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(axR, yT(setp) - 6, 'уставка', 10, MUTED, 'end'))
    f.append(arrow(axL, tY1, axL, tY0 - 6, color=INK, sw=1.3))
    f.append(text(axL - 8, tY0 - 2, 'вихід', 10, INK, 'end'))
    f.append(arrow(axL, tY1, axR + 4, tY1, color=INK, sw=1.3))
    f.append(text(axR + 5, tY1 + 4, 't', 12, INK, 'start'))

    # no anti-windup: rises, big overshoot, long oscillatory settle
    def out_none(t):
        return setp * (1 - math.exp(-0.55 * t)) + 0.62 * math.exp(-0.28 * t) * math.sin(0.62 * t) * (t > 1.5)
    # clamped: moderate overshoot
    def out_clamp(t):
        return setp * (1 - math.exp(-0.6 * t)) + 0.28 * math.exp(-0.5 * t) * math.sin(0.7 * t) * (t > 1.5)
    # tracking: almost no overshoot, fast settle
    def out_track(t):
        return setp * (1 - math.exp(-0.72 * t)) + 0.06 * math.exp(-0.7 * t) * math.sin(0.8 * t) * (t > 1.5)

    def curve(fn, color, dash=None, sw=2.4):
        pts = []
        t = 0.0
        while t <= 13.0 + 1e-9:
            pts.append('%.1f,%.1f' % (gx(t), yT(max(0.0, fn(t)))))
            t += 13.0 / 260
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (' '.join(pts), color, sw, d))

    f.append(curve(out_none, POS))
    f.append(curve(out_clamp, NEG, dash='8,4'))
    f.append(curve(out_track, FIELD))
    b1, w1, h1 = textbox(gx(4.2), yT(1.42), 'без захисту: великий переліт', 10,
                         pad=5, fill='#fff', stroke=POS, sw=1.0, color=POS)
    f.append(b1)

    # ── BOTTOM: integrator accumulator ────────────────────────────────────────
    bY0, bY1 = 300, 430
    f.append(text(W // 2, 270, 'накопичувач інтеграла:', 11, MUTED, 'middle'))

    def yB(v): return bY1 - v * (bY1 - bY0)          # v in 0..1

    f.append(arrow(axL, bY1, axL, bY0 - 6, color=INK, sw=1.3))
    f.append(text(axL - 8, bY0 - 2, '∫e dt', 10, INK, 'end'))
    f.append(arrow(axL, bY1, axR + 4, bY1, color=INK, sw=1.3))
    f.append(text(axR + 5, bY1 + 4, 't', 12, INK, 'start'))

    sat_end = 4.5   # while saturated, unprotected integrator grows linearly
    # unprotected: linear blow-up during saturation, then slow drain
    accN = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        if t <= sat_end:
            v = 0.20 * t
        else:
            v = min(0.95, 0.20 * sat_end) - 0.03 * (t - sat_end)
        accN.append('%.1f,%.1f' % (gx(t), yB(min(0.97, v))))
        t += 13.0 / 260
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (' '.join(accN), POS))

    # clamped: rises to ceiling, flattens, then relaxes
    ceil = 0.55
    accC = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        v = min(ceil, 0.20 * t)
        if t > 5.5:
            v = max(0.30, ceil - 0.04 * (t - 5.5))
        accC.append('%.1f,%.1f' % (gx(t), yB(v)))
        t += 13.0 / 260
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="8,4"/>' % (' '.join(accC), NEG))
    f.append(line(axL, yB(ceil), axR, yB(ceil), color=MUTED, sw=1.0, dash='3,3'))
    f.append(text(axR, yB(ceil) - 5, 'стеля', 9.5, MUTED, 'end'))

    # tracking: eases smoothly to the right level, never blows up
    accT = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        v = 0.42 * (1 - math.exp(-0.5 * t))
        accT.append('%.1f,%.1f' % (gx(t), yB(v)))
        t += 13.0 / 260
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (' '.join(accT), FIELD))

    # legend
    lx0 = gx(6.0)
    ly0 = yB(0.94)
    f.append(line(lx0, ly0, lx0 + 22, ly0, color=POS, sw=2.4))
    f.append(text(lx0 + 27, ly0 + 4, 'без захисту', 9.5, POS, 'start'))
    f.append(line(lx0, ly0 + 15, lx0 + 22, ly0 + 15, color=NEG, sw=2.2, dash='8,4'))
    f.append(text(lx0 + 27, ly0 + 19, 'затискання', 9.5, NEG, 'start'))
    f.append(line(lx0, ly0 + 30, lx0 + 22, ly0 + 30, color=FIELD, sw=2.4))
    f.append(text(lx0 + 27, ly0 + 34, 'зворотний перерахунок', 9.5, FIELD, 'start'))

    f.append(text(W // 2, H - 8,
                  'Трекінг зливає з інтеграла рівно надлишок, що орган не видав — '
                  'накопичувач тримається на реальному рівні',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'antiwindup-compare.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (history insert) — the three layers of the PID story on one timeline:
# 1911 Sperry builds working hardware (idea, in metal, intuitive) →
# 1922 Minorsky writes the math of three terms (theory) →
# 1923 New Mexico trial (proof it works) →
# 1940s Tustin ports it to discrete time (path into firmware).
# The point: idea / theory / realisation are DIFFERENT acts by DIFFERENT people.
# ════════════════════════════════════════════════════════════════════════════
def fig_pid_timeline():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # baseline (the arrow of time)
    ay = 250
    f.append(arrow(40, ay, W - 24, ay, color=INK, sw=1.8))
    f.append(text(W - 22, ay + 18, 'час', 12, MUTED, 'end'))

    # four milestones: (x, year, top-title, body-lines, kind-colour, tick-label)
    # kind colours: hardware = MUTED, theory/birth = FIELD, proof = INK, digital = NEG
    posts = [
        (150, '1911', 'Сперрі', ['гіроавтостерновий', '«Metal Mike»',
                                  'ідея — у залізі,', 'на дотик'], MUTED),
        (330, '1922', 'Мінорський', ['стаття про три члени', 'P · I · D',
                                     'теорія —', 'уперше в рівняннях'], FIELD),
        (485, '1923', 'USS New Mexico', ['випробування:', 'нишпорення ±1/6°',
                                        'доказ, що', 'воно працює'], INK),
        (635, '1940-і', 'Тастін', ['перенос у', 'дискретний час',
                                   'шлях у', 'прошивку'], NEG),
    ]

    for (x, yr, name, body, col) in posts:
        # tick on the time axis
        f.append(line(x, ay - 7, x, ay + 7, color=INK, sw=1.6))
        f.append(circle(x, ay, 4, fill=col, stroke=col, sw=1))
        # year under the axis
        f.append(text(x, ay + 26, yr, 14, col, 'middle', bold=True))
        # card above the axis
        lines = [name] + body
        bx, bw, bh = textbox(x, 120, "\n".join(lines), size=11, pad=9,
                             stroke=col, min_w=132)
        f.append(bx)
        # name line bold-emphasised by a coloured underline stub
        f.append(line(x - 26, 120 - bh / 2 + 20, x + 26, 120 - bh / 2 + 20,
                      color=col, sw=1.4))
        # connector card → tick
        f.append(line(x, 120 + bh / 2, x, ay - 8, color=col, sw=1.2,
                      dash='3,3'))

    # legend strip: idea → theory → proof → digital
    ly = 305
    f.append(text(40, ly, 'ідея (залізо)', 11, MUTED, 'start'))
    f.append(text(250, ly, '→  теорія', 11, FIELD, 'start'))
    f.append(text(400, ly, '→  доказ', 11, INK, 'start'))
    f.append(text(540, ly, '→  цифра', 11, NEG, 'start'))

    render(os.path.join(IMG, 'pid-timeline.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (insert math-steady-state) — closed-loop block diagram + error formula.
# R → summing junction (minus feedback) → C(s) regulator → G(s) plant → Y, fed
# back. The point: the whole steady-state story compresses to E = R/(1+GC).
# ════════════════════════════════════════════════════════════════════════════
def fig_loop_error_formula():
    W, H = 700, 300
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 28, 'Замкнений контур і його похибка', 16, INK, 'middle', bold=True))

    ymid = 130
    sjx, sjy = 130, ymid
    bw, bh = 100, 54
    cx0 = 250
    gx0 = 430
    cyb = ymid - bh / 2

    f.append(arrow(48, ymid, sjx - 16, ymid, color=INK, sw=1.8))
    f.append(text(52, ymid - 10, 'R(s)', 12, INK, 'start'))
    f.append(text(52, ymid + 20, 'ціль', 10, MUTED, 'start'))

    f.append(circle(sjx, sjy, 15, fill='#fff', stroke=INK, sw=1.6))
    f.append(text(sjx - 4, sjy - 4, '+', 13, POS, 'middle', bold=True))
    f.append(text(sjx + 5, sjy + 15, '−', 13, NEG, 'middle', bold=True))

    f.append(arrow(sjx + 16, ymid, cx0 - 2, ymid, color=INK, sw=1.8))
    f.append(text((sjx + cx0) / 2, ymid - 9, 'E(s)', 12, FIELD, 'middle'))
    f.append(text((sjx + cx0) / 2, ymid + 20, 'похибка', 10, MUTED, 'middle'))

    f.append(rect(cx0, cyb, bw, bh, fill='#eef4ff', stroke=NEG, sw=1.8, rx=7))
    f.append(text(cx0 + bw / 2, ymid - 6, 'C(s)', 14, INK, 'middle', bold=True))
    f.append(text(cx0 + bw / 2, ymid + 12, 'регулятор', 10, MUTED, 'middle'))

    f.append(arrow(cx0 + bw, ymid, gx0 - 2, ymid, color=INK, sw=1.8))
    f.append(text((cx0 + bw + gx0) / 2, ymid - 9, 'U(s)', 11, INK, 'middle'))

    f.append(rect(gx0, cyb, bw, bh, fill='#eafaf0', stroke=FIELD, sw=1.8, rx=7))
    f.append(text(gx0 + bw / 2, ymid - 6, 'G(s)', 14, INK, 'middle', bold=True))
    f.append(text(gx0 + bw / 2, ymid + 12, 'об’єкт', 10, MUTED, 'middle'))

    outx = gx0 + bw
    tapx = outx + 45
    f.append(line(outx, ymid, tapx + 40, ymid, color=INK, sw=1.8))
    f.append(arrow(tapx + 40, ymid, tapx + 78, ymid, color=INK, sw=1.8))
    f.append(text(tapx + 82, ymid - 9, 'Y(s)', 12, INK, 'start'))
    f.append(text(tapx + 82, ymid + 12, 'вихід', 10, MUTED, 'start'))
    f.append(circle(tapx, ymid, 3, fill=INK, stroke=INK, sw=1))

    fby = ymid + 78
    f.append(line(tapx, ymid, tapx, fby, color=INK, sw=1.6))
    f.append(line(tapx, fby, sjx, fby, color=INK, sw=1.6))
    f.append(arrow(sjx, fby, sjx, sjy + 16, color=INK, sw=1.6))
    f.append(text((sjx + tapx) / 2, fby + 16, 'зворотний зв’язок', 10, MUTED, 'middle'))

    b, bwf, bhf = textbox(W / 2, 258, 'E(s) = R(s) / [ 1 + G(s)·C(s) ]', 14,
                          pad=9, fill='#fffbea', stroke=MUTED, sw=1.2, color=INK, bold=True)
    f.append(b)

    render(os.path.join(IMG, 'loop-error-formula.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (insert math-steady-state) — the system-type table.
# Rows: type 0, 1, 2 (number of integrators). Cols: step, ramp, parabola.
# Cells: steady-state error. Diagonal = finite nonzero; above-right = 0;
# below-left = ∞. Each integrator shifts the whole picture one cell to the right.
# ════════════════════════════════════════════════════════════════════════════
def fig_system_type_table():
    W, H = 620, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 28, 'Тип системи проти класу цілі', 16, INK, 'middle', bold=True))

    x0, y0 = 150, 96
    cw, ch = 130, 64
    ncol, nrow = 3, 3

    col_titles = ['сходинка\nR=A/s', 'ramp\nR=A/s²', 'парабола\nR=A/s³']
    row_titles = ['тип 0\n0 інтегр.', 'тип 1\n1 інтегр.', 'тип 2\n2 інтегр.']

    inf = '∞'
    vals = [
        ['A/(1+K)', inf,       inf     ],
        ['0',       'A/K',     inf     ],
        ['0',       '0',       'A/K'   ],
    ]
    kinds = [
        ['finite', 'inf',    'inf'   ],
        ['zero',   'finite', 'inf'   ],
        ['zero',   'zero',   'finite'],
    ]
    fillmap = {'zero': '#eafaf0', 'finite': '#fff6e6', 'inf': '#fdecea'}
    strkmap = {'zero': FIELD,     'finite': '#b8860b',  'inf': POS}
    txtmap  = {'zero': FIELD,     'finite': '#8a6d00',  'inf': POS}

    for j in range(ncol):
        f.append(fitbox(x0 + j * cw + 4, y0 - 50, cw - 8, 44, col_titles[j], 11,
                        pad=3, fill='#f3f4f6', stroke=MUTED, sw=1.0, color=INK, bold=True))

    for i in range(nrow):
        f.append(fitbox(x0 - 126, y0 + i * ch + 4, 118, ch - 8, row_titles[i], 11,
                        pad=3, fill='#f3f4f6', stroke=MUTED, sw=1.0, color=INK, bold=True))

    for i in range(nrow):
        for j in range(ncol):
            k = kinds[i][j]
            x = x0 + j * cw
            y = y0 + i * ch
            f.append(rect(x + 4, y + 4, cw - 8, ch - 8, fill=fillmap[k],
                          stroke=strkmap[k], sw=1.6, rx=7))
            f.append(text(x + cw / 2, y + ch / 2 + 6, vals[i][j], 17, txtmap[k],
                          'middle', bold=True))

    f.append(text(W // 2, y0 + nrow * ch + 30,
                  'кожен інтегратор зсуває картину на клітину праворуч: ∞ → скінченна → 0',
                  11, INK, 'middle'))
    f.append(text(W // 2, y0 + nrow * ch + 50,
                  'нуль похибки ⇔ тип системи БІЛЬШИЙ за степінь цілі',
                  10, MUTED, 'middle'))

    render(os.path.join(IMG, 'system-type-table.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (insert math-discretization) — three ways to close ONE strip.
# One strip of width Δt between two samples e[n-1], e[n] on a DECAYING curve.
# forward rectangle uses the LEFT height (overshoots the curve on the way down),
# backward rectangle uses the RIGHT height (undershoots), trapezoid joins the two
# edges by a straight line (lies almost on the curve; only a second-order sliver
# of curvature is left). The point: rectangles ignore the slope, trapezoid keeps it.
# ════════════════════════════════════════════════════════════════════════════
def fig_integration_schemes():
    import math
    W, H = 680, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 26, 'Три способи закрити смужку між двома відліками', 15, INK, 'middle', bold=True))

    ox, oy = 96, 296          # origin (left edge, e=0)
    dt_px = 400               # strip width in px (this is Δt)
    sy = 40                   # px per error unit

    def e_of(u):              # decaying curve across the strip, u in [0,1]
        return 4.3 * math.exp(-0.62 * u) + 0.2
    eL, eR = e_of(0.0), e_of(1.0)

    def gx(u): return ox + u * dt_px
    def gy(e): return oy - e * sy

    # axes
    f.append(arrow(ox - 30, gy(0), ox + dt_px + 44, gy(0), color=INK, sw=1.4))
    f.append(text(ox + dt_px + 46, gy(0) + 5, 't', 13, INK, 'start'))
    f.append(arrow(ox, gy(0) + 8, ox, gy(5.4), color=INK, sw=1.4))
    f.append(text(ox - 6, gy(5.5), 'e', 13, INK, 'end'))

    # forward rectangle (left height) — light red fill behind everything
    f.append(rect(gx(0), gy(eL), dt_px, eL * sy, fill='#fdecea', stroke=POS, sw=1.4, rx=0))
    # backward rectangle ceiling (right height) — dashed blue line
    f.append(line(gx(0), gy(eR), gx(1), gy(eR), color=NEG, sw=2.0, dash='7,4'))

    # strip edges + Δt bracket
    f.append(line(gx(1), gy(0), gx(1), gy(eR), color=MUTED, sw=1.0, dash='3,3'))
    f.append(line(gx(0), gy(0) + 18, gx(1), gy(0) + 18, color=INK, sw=1.2))
    f.append(line(gx(0), gy(0) + 14, gx(0), gy(0) + 22, color=INK, sw=1.2))
    f.append(line(gx(1), gy(0) + 14, gx(1), gy(0) + 22, color=INK, sw=1.2))
    f.append(text((gx(0) + gx(1)) / 2, gy(0) + 33, 'Δt', 12, INK, 'middle'))
    f.append(text(gx(0), gy(0) + 48, 'tₙ₋₁', 11, MUTED, 'middle'))
    f.append(text(gx(1), gy(0) + 48, 'tₙ', 11, MUTED, 'middle'))

    # the true curve
    curve = []
    u = 0.0
    while u <= 1.0 + 1e-9:
        curve.append('%.1f,%.1f' % (gx(u), gy(e_of(u))))
        u += 1.0 / 160
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (' '.join(curve), INK))

    # trapezoid top (straight line joining the two edge samples)
    f.append(line(gx(0), gy(eL), gx(1), gy(eR), color=FIELD, sw=2.6))

    # sample dots
    f.append(circle(gx(0), gy(eL), 5.0, fill=INK, stroke=BG, sw=1.4))
    f.append(circle(gx(1), gy(eR), 5.0, fill=INK, stroke=BG, sw=1.4))
    f.append(text(gx(0) - 8, gy(eL) - 8, 'e[n−1]', 11, INK, 'end'))
    f.append(text(gx(1) + 8, gy(eR) - 8, 'e[n]', 11, INK, 'start'))

    # scheme labels
    f.append(text(gx(0.30), gy(1.0), 'прямокутник вперед', 10.5, POS, 'middle'))
    f.append(text(gx(0.30), gy(0.55), '(ліва висота)', 9.5, POS, 'middle'))
    f.append(text(gx(0.70), gy(eR) + 16, 'прямокутник назад (права висота)', 10, NEG, 'middle'))
    b, w, h = textbox(gx(0.60), gy(4.2), 'трапеція:\nпохила стеля ловить нахил', 10,
                      pad=5, fill='#fff', stroke=FIELD, sw=1.1, color=FIELD)
    f.append(b)

    f.append(text(W // 2, H - 8,
                  'Прямокутники бачать лише висоту й мажуть на трикутник під нахилом; '
                  'трапеція ловить нахил — лишає тільки серпик кривини',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'integration-schemes.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (insert math-discretization) — bilinear frequency warping.
# Mapping ω_d = f(ω_a): near zero follows the 45° reference (frequencies match),
# but as analog ω_a → ∞ the digital ω_d saturates at the shelf π/Δt. The whole
# infinite analog axis is squeezed into a finite segment up to Nyquist; near
# Nyquist a fixed step in ω_d costs an ever-larger step in ω_a — any specified
# frequency drifts down, worse the closer it sits to Nyquist.
# ════════════════════════════════════════════════════════════════════════════
def fig_frequency_warping():
    import math
    W, H = 620, 430
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 26, 'Викривлення частоти в білінійному перетворенні', 15, INK, 'middle', bold=True))

    axL, axR = 82, W - 42
    axB, axT = 356, 64
    f.append(arrow(axL - 4, axB, axR + 6, axB, color=INK, sw=1.5))
    f.append(text(axR + 8, axB + 5, 'ω_а', 13, INK, 'start'))
    f.append(text((axL + axR) / 2, axB + 34, 'аналогова частота ω_а (0 → ∞)', 11, MUTED, 'middle'))
    f.append(arrow(axL, axB + 4, axL, axT - 6, color=INK, sw=1.5))
    f.append(text(axL - 8, axT - 2, 'ω_д', 13, INK, 'end'))

    shelf = math.pi                 # dimensionless: Δt=1 → Nyquist = π
    Wa_max = 7.0 * math.pi
    span_x = axR - axL
    span_y = axB - axT

    def X(wa): return axL + (wa / Wa_max) * span_x
    def Y(wd): return axB - (wd / (shelf * 1.12)) * span_y

    # shelf ω_d = π/Δt
    f.append(line(axL, Y(shelf), axR, Y(shelf), color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(axR, Y(shelf) - 6, 'π/Δt  (Найквіст)', 10, MUTED, 'end'))

    # ideal no-warp reference ω_d = ω_a
    ref = []
    wa = 0.0
    while wa <= Wa_max + 1e-9:
        if wa > shelf * 1.12: break
        ref.append('%.1f,%.1f' % (X(wa), Y(wa)))
        wa += Wa_max / 300
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="6,4"/>' % (' '.join(ref), NEG))

    # true bilinear mapping ω_d = 2·atan(ω_a/2)  (Δt=1)
    real = []
    wa = 0.0
    while wa <= Wa_max + 1e-9:
        real.append('%.1f,%.1f' % (X(wa), Y(2.0 * math.atan(wa / 2.0))))
        wa += Wa_max / 400
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (' '.join(real), INK))

    # equal steps in ω_d → growing steps in ω_a (green guides)
    for wd_mark in (0.55 * shelf, 0.80 * shelf):
        wa_mark = 2.0 * math.tan(wd_mark / 2.0)
        if wa_mark > Wa_max: continue
        f.append(line(axL, Y(wd_mark), X(wa_mark), Y(wd_mark), color=FIELD, sw=1.0, dash='2,3'))
        f.append(line(X(wa_mark), Y(wd_mark), X(wa_mark), axB, color=FIELD, sw=1.0, dash='2,3'))

    b1, w1, h1 = textbox(X(1.3 * math.pi), Y(0.28 * shelf), 'біля нуля:\nчастоти майже збігаються', 9.5,
                         pad=5, fill='#fff', stroke=NEG, sw=1.0, color=NEG)
    f.append(b1)
    b2, w2, h2 = textbox(X(4.7 * math.pi), Y(0.60 * shelf),
                         'уся нескінченна вісь\nстиснена до Найквіста', 9.5,
                         pad=5, fill='#fff', stroke=INK, sw=1.0, color=INK)
    f.append(b2)
    f.append(text(X(2.1 * math.pi), Y(1.02 * shelf), 'справжнє відображення', 9.5, INK, 'middle'))

    f.append(text(W // 2, H - 8,
                  'Нескінченна аналогова вісь тисне у скінченний відрізок [0, π/Δt] — '
                  'тому зріз тим дужче з’їжджає, чим ближче він до Найквіста',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'frequency-warping.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Figure (proj-pid-production) — back-calculation anti-windup on a big setpoint
# step. Top: output vs setpoint — no protection = big overshoot + long settle;
# with back-calculation the output eases in with almost no overshoot. Bottom: the
# integrator accumulator — unprotected keeps integrating while the actuator is
# saturated and blows past the level that actually holds the limit (that excess
# is what drives the overshoot); back-calculation feeds (u_sat − u)/Tt back so
# the accumulator eases to exactly that level and no further.
# ════════════════════════════════════════════════════════════════════════════
def fig_back_calculation():
    import math
    W, H = 680, 470
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W // 2, 26, 'Зворотний перерахунок проти насичення', 16, INK, 'middle', bold=True))

    axL, axR = 70, W - 30
    span = axR - axL
    def gx(t): return axL + (t / 13.0) * span

    tY0, tY1 = 58, 228
    setp = 1.0
    def yT(v): return tY1 - (v / 1.5) * (tY1 - tY0)

    f.append(line(axL, yT(setp), axR, yT(setp), color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(axR, yT(setp) - 6, 'ціль', 10, MUTED, 'end'))
    f.append(arrow(axL, tY1, axL, tY0 - 6, color=INK, sw=1.3))
    f.append(text(axL - 8, tY0 - 2, 'вихід', 10, INK, 'end'))
    f.append(arrow(axL, tY1, axR + 4, tY1, color=INK, sw=1.3))
    f.append(text(axR + 5, tY1 + 4, 't', 12, INK, 'start'))

    def out_none(t):
        rise = setp * (1 - math.exp(-0.5 * t))
        over = 0.55 * math.exp(-0.30 * (t - 4.5)) * math.sin(0.60 * (t - 4.5)) * (t > 4.5)
        return rise + over
    def out_track(t):
        rise = setp * (1 - math.exp(-0.55 * t))
        over = 0.07 * math.exp(-0.6 * (t - 4.5)) * math.sin(0.8 * (t - 4.5)) * (t > 4.5)
        return rise + over

    def curve(fn, color, dash=None, sw=2.5):
        pts = []
        t = 0.0
        while t <= 13.0 + 1e-9:
            pts.append('%.1f,%.1f' % (gx(t), yT(max(0.0, fn(t)))))
            t += 13.0 / 260
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (' '.join(pts), color, sw, d))

    f.append(curve(out_none, POS, dash='8,4'))
    f.append(curve(out_track, FIELD))
    f.append(text(gx(5.0), yT(1.46), 'без захисту: великий переліт', 10, POS, 'middle'))
    f.append(text(gx(9.7), yT(0.80), 'із перерахунком:', 10, FIELD, 'middle'))
    f.append(text(gx(9.7), yT(0.66), 'майже без перельоту', 10, FIELD, 'middle'))

    bY0, bY1 = 300, 428
    f.append(text(W // 2, 268, 'накопичувач інтеграла (в одиницях виходу):', 11, MUTED, 'middle'))
    def yB(v): return bY1 - v * (bY1 - bY0)

    f.append(arrow(axL, bY1, axL, bY0 - 6, color=INK, sw=1.3))
    f.append(text(axL - 8, bY0 - 2, 'I_term', 10, INK, 'end'))
    f.append(arrow(axL, bY1, axR + 4, bY1, color=INK, sw=1.3))
    f.append(text(axR + 5, bY1 + 4, 't', 12, INK, 'start'))

    sat_end = 4.5
    hold = 0.50
    f.append(line(axL, yB(hold), axR, yB(hold), color=MUTED, sw=1.0, dash='3,3'))
    f.append(text(axR, yB(hold) - 5, 'потрібний рівень', 9.5, MUTED, 'end'))

    accN = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        if t <= sat_end:
            v = 0.185 * t
        else:
            v = min(0.95, 0.185 * sat_end) - 0.055 * (t - sat_end)
            v = max(hold, v)
        accN.append('%.1f,%.1f' % (gx(t), yB(min(0.97, v))))
        t += 13.0 / 260
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" '
             'stroke-dasharray="8,4"/>' % (' '.join(accN), POS))

    accT = []
    t = 0.0
    while t <= 13.0 + 1e-9:
        v = hold * (1 - math.exp(-0.5 * t))
        accT.append('%.1f,%.1f' % (gx(t), yB(v)))
        t += 13.0 / 260
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (' '.join(accT), FIELD))

    f.append(text(gx(2.9), yB(0.90), 'без захисту:', 10, POS, 'middle'))
    f.append(text(gx(2.9), yB(0.78), 'роздувається', 10, POS, 'middle'))

    lx0, ly0 = gx(7.2), yB(0.94)
    f.append(rect(lx0 - 8, ly0 - 12, 216, 38, fill='#f8f9fa', stroke=MUTED, sw=1, rx=5))
    f.append(line(lx0, ly0, lx0 + 22, ly0, color=POS, sw=2.5, dash='8,4'))
    f.append(text(lx0 + 28, ly0 + 4, 'без anti-windup', 9.5, INK, 'start'))
    f.append(line(lx0, ly0 + 16, lx0 + 22, ly0 + 16, color=FIELD, sw=2.5))
    f.append(text(lx0 + 28, ly0 + 20, 'зворотний перерахунок', 9.5, INK, 'start'))

    f.append(text(W // 2, H - 8,
                  'Перерахунок зливає з інтеграла надлишок «порахував мінус видав» — '
                  'накопичувач сам виходить на потрібний рівень',
                  10, MUTED, 'middle'))
    render(os.path.join(IMG, 'back-calculation.svg'), W, H, *f,
           title='Зворотний перерахунок: інтеграл сам виходить на потрібний рівень')


if __name__ == '__main__':
    fig_three_readings()
    fig_integral_closes_gap()
    fig_windup()
    fig_derivative_noise_gain()
    fig_antiwindup_compare()
    fig_pid_timeline()
    fig_loop_error_formula()
    fig_system_type_table()
    fig_integration_schemes()
    fig_frequency_warping()
    fig_back_calculation()
    print('Done.')
