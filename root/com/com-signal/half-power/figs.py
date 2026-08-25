# -*- coding: utf-8 -*-
"""Фігури до теми «Точка половинної потужності».
Імпортує спільний svgkit зі scripts/ (НЕ копіювати функції).
Дві фігури:
  1) half-power-curve.svg — АЧХ фільтра нижніх частот із позначеною точкою −3 дБ
     (рівень 0.707 за напругою) і частотою зрізу.
  2) bandwidth.svg        — смугова АЧХ: дві точки −3 дБ обмежують смугу пропускання.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — АЧХ фільтра нижніх частот, точка −3 дБ
# Вісь x — частота (логарифмічна, у декадах); вісь y — коефіцієнт передачі за
# напругою від 0 до ~1.08. Крива першого порядку: |H| = 1/√(1+(f/fc)²).
# На fc маємо |H| = 1/√2 ≈ 0.707 — це й є точка половинної потужності.
# Полотно W×H; математична рамка [ml..(W-mr)] × [(H-mb)..mt].
# Перевірка меж: усі gx() у [ml..W-mr], усі gy() у [mt..H-mb].
# ════════════════════════════════════════════════════════════════════════════
def fig_curve():
    W, H = 640, 420
    ml, mr, mt, mb = 70, 40, 56, 60      # поля рамки
    x_lo, x_hi = -1.6, 1.6               # log10(f/fc): від 0.025·fc до ~40·fc
    y_lo, y_hi = 0.0, 1.08               # коефіцієнт передачі за напругою

    def gx(lf): return ml + (lf - x_lo) / (x_hi - x_lo) * (W - ml - mr)
    def gy(v):  return (H - mb) - (v - y_lo) / (y_hi - y_lo) * (H - mb - mt)

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # осі
    f.append(arrow(gx(x_lo), gy(0), gx(x_hi) + 8, gy(0), color=INK, sw=1.5))
    f.append(text(gx(x_hi) + 6, gy(0) + 20, 'частота', 12, INK, 'end'))
    f.append(arrow(gx(x_lo), gy(0), gx(x_lo), gy(y_hi) + 4, color=INK, sw=1.5))
    f.append(text(gx(x_lo) - 8, gy(1.0), '|H|', 12, INK, 'end'))

    # рівні 1.0 і 0.707 пунктиром
    f.append(line(gx(x_lo), gy(1.0), gx(x_hi), gy(1.0), color=MUTED, sw=1, dash='4,4'))
    f.append(text(gx(x_lo) - 8, gy(1.0) + 4, '1.0', 11, MUTED, 'end'))
    yhp = 1.0 / math.sqrt(2.0)
    f.append(line(gx(x_lo), gy(yhp), gx(0.0), gy(yhp), color=FIELD, sw=1.4, dash='4,4'))
    f.append(text(gx(x_lo) - 8, gy(yhp) + 4, '0.707', 11, FIELD, 'end'))

    # вертикаль на частоті зрізу fc (log10(f/fc)=0)
    f.append(line(gx(0.0), gy(0), gx(0.0), gy(yhp), color=FIELD, sw=1.4, dash='4,4'))
    f.append(text(gx(0.0), gy(0) + 20, 'fc', 12, FIELD, 'middle', bold=True))

    # крива |H| = 1/sqrt(1+(f/fc)^2)
    pts = []
    lf = x_lo
    while lf <= x_hi + 1e-6:
        r = 10 ** lf                      # f/fc
        v = 1.0 / math.sqrt(1.0 + r * r)
        pts.append('%.1f,%.1f' % (gx(lf), gy(v)))
        lf += 0.04
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (' '.join(pts), POS))

    # маркер точки половинної потужності на (fc, 0.707)
    f.append(circle(gx(0.0), gy(yhp), 4.6, fill=POS, stroke=BG, sw=1.6))

    # виноска −3 дБ
    bx, bw, bh = textbox(gx(0.62), gy(0.93),
                         '−3 дБ\nпотужність ÷ 2\nнапруга × 0.707',
                         size=12, pad=9, fill=FILL, stroke=FIELD, color=INK, bold=False)
    f.append(bx)
    f.append(line(gx(0.30), gy(0.86), gx(0.04), gy(yhp + 0.02), color=FIELD, sw=1.2))

    # зона пропускання / зона послаблення
    f.append(text(gx(-1.1), gy(0.30), 'пропускає', 12, MUTED, 'middle'))
    f.append(text(gx(1.05), gy(0.30), 'послаблює', 12, MUTED, 'middle'))

    render(os.path.join(IMG, 'half-power-curve.svg'), W, H, *f,
           title='Точка −3 дБ: межа, де потужність падає вдвічі')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — смугова АЧХ і смуга пропускання
# Дзвоноподібна крива з пласкою вершиною на 1.0; дві точки на рівні 0.707
# (зліва f_low, справа f_high) обмежують смугу. BW = f_high − f_low.
# Будуємо штучну симетричну криву в координатах log10(f/f0).
# ════════════════════════════════════════════════════════════════════════════
def fig_bandwidth():
    W, H = 640, 420
    ml, mr, mt, mb = 60, 40, 56, 62
    x_lo, x_hi = -1.3, 1.3
    y_lo, y_hi = 0.0, 1.10

    def gx(lf): return ml + (lf - x_lo) / (x_hi - x_lo) * (W - ml - mr)
    def gy(v):  return (H - mb) - (v - y_lo) / (y_hi - y_lo) * (H - mb - mt)

    # резонансна крива другого порядку: |H| = 1 / sqrt(1 + Q^2 (r - 1/r)^2)
    Q = 0.9
    def mag(lf):
        r = 10 ** lf
        return 1.0 / math.sqrt(1.0 + (Q * (r - 1.0 / r)) ** 2)

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # осі
    f.append(arrow(gx(x_lo), gy(0), gx(x_hi) + 8, gy(0), color=INK, sw=1.5))
    f.append(text(gx(x_hi) + 6, gy(0) + 20, 'частота', 12, INK, 'end'))
    f.append(arrow(gx(x_lo), gy(0), gx(x_lo), gy(y_hi) + 2, color=INK, sw=1.5))
    f.append(text(gx(x_lo) - 8, gy(1.0), '|H|', 12, INK, 'end'))

    # рівні
    f.append(line(gx(x_lo), gy(1.0), gx(x_hi), gy(1.0), color=MUTED, sw=1, dash='4,4'))
    f.append(text(gx(x_lo) - 8, gy(1.0) + 4, '1.0', 11, MUTED, 'end'))
    yhp = 1.0 / math.sqrt(2.0)
    f.append(line(gx(x_lo), gy(yhp), gx(x_hi), gy(yhp), color=FIELD, sw=1.3, dash='4,4'))
    f.append(text(gx(x_lo) - 8, gy(yhp) + 4, '0.707', 11, FIELD, 'end'))

    # крива
    pts = []
    lf = x_lo
    while lf <= x_hi + 1e-6:
        pts.append('%.1f,%.1f' % (gx(lf), gy(mag(lf))))
        lf += 0.02
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (' '.join(pts), POS))

    # знайти дві точки перетину рівня 0.707 (зліва й справа від резонансу lf=0)
    def cross(a, b):
        for _ in range(60):
            m = 0.5 * (a + b)
            if (mag(m) - yhp) * (mag(a) - yhp) <= 0:
                b = m
            else:
                a = m
        return 0.5 * (a + b)
    lf_lo = cross(-1.0, 0.0)
    lf_hi = cross(1.0, 0.0)

    for lf in (lf_lo, lf_hi):
        f.append(line(gx(lf), gy(0), gx(lf), gy(yhp), color=FIELD, sw=1.3, dash='4,4'))
        f.append(circle(gx(lf), gy(yhp), 4.6, fill=POS, stroke=BG, sw=1.6))
    f.append(text(gx(lf_lo), gy(0) + 20, 'f_low', 12, FIELD, 'middle', bold=True))
    f.append(text(gx(lf_hi), gy(0) + 20, 'f_high', 12, FIELD, 'middle', bold=True))

    # двостороння стрілка смуги під рівнем 0.707
    yb = gy(yhp) - 16
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="1.8" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (gx(lf_lo), yb, gx(lf_hi), yb, NEG))
    f.append(text(gx(0.0), yb - 8, 'смуга = f_high − f_low', 12, NEG, 'middle', bold=True))

    # підпис обох точок
    bx, bw, bh = textbox(gx(0.0), gy(0.30),
                         'обидві межі — на −3 дБ\n(потужність вдвічі менша)',
                         size=12, pad=9, fill=FILL, stroke=LINE, color=INK)
    f.append(bx)

    render(os.path.join(IMG, 'bandwidth.svg'), W, H, *f,
           title='Смуга пропускання: відстань між двома точками −3 дБ')


if __name__ == '__main__':
    fig_curve()
    fig_bandwidth()
    print('OK: half-power-curve.svg, bandwidth.svg')
