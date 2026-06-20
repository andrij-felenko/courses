# -*- coding: utf-8 -*-
"""Фігури теми «Матриці як дії». Імпортує спільний svgkit зі scripts/.
Запуск:  python figs.py   → пише ./img/machine.svg, ./img/order.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRID = "#e4e4e4"   # тонка сітка


def _grid(ox, oy, ex, ey, n=4, step=26):
    """Сітка-паралелограм у пікселях: початок (ox,oy), осі задані векторами
    ex=(ex_x,ex_y) та ey=(ey_x,ey_y) у пікселях на 1 клітину. Повертає список фрагментів."""
    fr = []
    exx, exy = ex
    eyx, eyy = ey
    for k in range(n + 1):
        # лінії вздовж ex (фіксований крок по ey)
        x0 = ox + k * eyx; y0 = oy + k * eyy
        fr.append(line(x0, y0, x0 + n * exx, y0 + n * exy, color=GRID, sw=1))
        # лінії вздовж ey (фіксований крок по ex)
        x1 = ox + k * exx; y1 = oy + k * exy
        fr.append(line(x1, y1, x1 + n * eyx, y1 + n * eyy, color=GRID, sw=1))
    return fr


def _vec(ox, oy, vx, vy, color, sw=3.0):
    return arrow(ox, oy, ox + vx, oy + vy, color=color, sw=sw)


# ── Фігура 1: матриця як машина «вектор → вектор» ────────────────────────────
# Ліворуч — вхідна площина з базисом e1,e2 і вектором v=(2,1).
# Посередині — рамка з M=[[1,1],[0,1]] (зсув).
# Праворуч — вихідна площина: e1 на місці, e2 нахилений, сітка перекошена.

def fig_machine():
    W, H = 760, 360
    step = 26
    parts = []
    parts.append(text(W / 2, 26, 'Матриця M — це машина: бере вектор, повертає вектор',
                      size=17, bold=True))

    # ── ліворуч: вхідна площина (ортонормований базис) ──
    ox, oy = 70, 300
    ex, ey = (step, 0), (0, -step)
    parts += _grid(ox, oy, ex, ey, n=4, step=step)
    parts.append(_vec(ox, oy, ex[0], ex[1], POS))                 # e1
    parts.append(_vec(ox, oy, ey[0], ey[1], NEG))                 # e2
    parts.append(text(ox + ex[0] + 4, oy + ex[1] + 14, 'e₁', size=13, color=POS, anchor='start', bold=True))
    parts.append(text(ox + ey[0] + 4, oy + ey[1] + 14, 'e₂', size=13, color=NEG, anchor='start', bold=True))
    vx, vy = 2 * step, -1 * step
    parts.append(_vec(ox, oy, vx, vy, "#7a3ea8", sw=3.4))
    parts.append(text(ox + vx + 4, oy + vy - 6, 'v = (2, 1)', size=13, color="#7a3ea8", anchor='start', bold=True))
    parts.append(text(ox + 2 * step, oy + 26, 'вхідна площина', size=12, color=MUTED))

    # ── посередині: рамка M ──
    bx, by, bw, bh = 320, 150, 120, 70
    parts.append(rect(bx, by, bw, bh, fill="#f3eefb", stroke="#7a3ea8", sw=2.2, rx=10))
    cxm = bx + bw / 2
    parts.append(text(cxm, by + 24, 'M =', size=14, bold=True))
    parts.append(text(cxm, by + 46, '[1  1]', size=14))
    parts.append(text(cxm, by + 62, '[0  1]', size=14))
    parts.append(text(cxm, by - 12, '«зсув» (shear)', size=12, color="#7a3ea8", italic=True))
    parts.append(arrow(255, 150, bx - 6, 175, color=INK, sw=2.4))
    parts.append(arrow(bx + bw + 6, 175, 525, 150, color=INK, sw=2.4))

    # ── праворуч: вихідна площина (e1 на місці, e2 нахилений) ──
    ox2, oy2 = 545, 300
    ex2, ey2 = (step, 0), (step, -step)        # зсув: e2 -> (1,1)
    parts += _grid(ox2, oy2, ex2, ey2, n=4, step=step)
    parts.append(_vec(ox2, oy2, ex2[0], ex2[1], POS))
    parts.append(_vec(ox2, oy2, ey2[0], ey2[1], NEG))
    parts.append(text(ox2 + 6, oy2 + 8, 'M·e₁ = стовпець 1', size=11, color=POS, anchor='start'))
    parts.append(text(ox2 + ey2[0] + 6, oy2 + ey2[1] - 6, 'M·e₂ = стовпець 2', size=11, color=NEG, anchor='start'))
    mvx, mvy = 3 * step, -1 * step             # Mv = (3,1)
    parts.append(_vec(ox2, oy2, mvx, mvy, "#7a3ea8", sw=3.4))
    parts.append(text(ox2 + mvx + 4, oy2 + mvy - 8, 'Mv = (3, 1)', size=13, color="#7a3ea8", anchor='start', bold=True))
    parts.append(text(ox2 + 2 * step, oy2 + 26, 'вихідна площина', size=12, color=MUTED))

    render(os.path.join(OUT, 'machine.svg'), W, H, *parts)


# ── Фігура 2: порядок важить, R·S ≠ S·R ──────────────────────────────────────
# Вихідний «прапорець» згори; ліворуч результат R·S, праворуч S·R.

def _flag(pts, fill):
    body = ' '.join('%.1f,%.1f' % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="0.6" stroke="%s" '
            'stroke-width="1.8"/>' % (body, fill, INK))


def _apply(M, p):
    return (M[0][0] * p[0] + M[0][1] * p[1], M[1][0] * p[0] + M[1][1] * p[1])


def fig_order():
    W, H = 760, 470
    parts = []
    parts.append(text(W / 2, 26, 'Порядок важить: R·S ≠ S·R (та сама фігура, різний результат)',
                      size=16, bold=True))

    # одиничний «прапорець» у математичних координатах (вісь y — вгору)
    flag = [(0, 0), (1, 0), (1, 1), (0.5, 1.4), (0, 1)]
    s = 30.0  # масштаб px на одиницю

    th = math.radians(50)
    R = [[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]
    S = [[2.0, 0.0], [0.0, 0.7]]
    RS = [[R[0][0] * S[0][0] + R[0][1] * S[1][0], R[0][0] * S[0][1] + R[0][1] * S[1][1]],
          [R[1][0] * S[0][0] + R[1][1] * S[1][0], R[1][0] * S[0][1] + R[1][1] * S[1][1]]]
    SR = [[S[0][0] * R[0][0] + S[0][1] * R[1][0], S[0][0] * R[0][1] + S[0][1] * R[1][1]],
          [S[1][0] * R[0][0] + S[1][1] * R[1][0], S[1][0] * R[0][1] + S[1][1] * R[1][1]]]

    def draw(cx, cy, M, fill):
        fr = []
        fr.append(line(cx - 10, cy, cx + 130, cy, color=GRID, sw=1))
        fr.append(line(cx, cy - 60, cx, cy + 100, color=GRID, sw=1))
        pts = [(cx + p[0] * s, cy - p[1] * s) for p in (_apply(M, q) for q in flag)]
        fr.append(_flag(pts, fill))
        return fr

    # ── зверху: вихідна фігура ──
    cx0, cy0 = 330, 110
    parts.append(line(cx0 - 12, cy0, cx0 + 130, cy0, color=GRID, sw=1))
    parts.append(line(cx0, cy0 - 90, cx0, cy0 + 70, color=GRID, sw=1))
    pts0 = [(cx0 + p[0] * s, cy0 - p[1] * s) for p in flag]
    parts.append(_flag(pts0, FIELD))
    parts.append(text(cx0 + 60, cy0 + 92, 'вихідна фігура', size=13, bold=True))
    parts.append(text(cx0 + 60, cy0 + 110, 'одиничний «прапорець»', size=11, color=MUTED))

    # ── ліворуч: R·S ──
    cxL, cyL = 120, 320
    parts += draw(cxL, cyL, RS, "#cfe3ff")
    parts.append(arrow(300, 150, cxL + 55, cyL - 70, color=NEG, sw=2.2))
    parts.append(text(205, 195, 'R·S', size=13, color=NEG, anchor='start', bold=True))
    parts.append(text(cxL + 60, cyL + 92, 'R·S  (спершу розтяг, тоді поворот)', size=13, bold=True))
    parts.append(text(cxL + 60, cyL + 110, 'розтягнутий, далі повернутий', size=11, color=MUTED))

    # ── праворуч: S·R ──
    cxR, cyR = 540, 320
    parts += draw(cxR, cyR, SR, "#ffd9d2")
    parts.append(arrow(360, 150, cxR + 5, cyR - 70, color=POS, sw=2.2))
    parts.append(text(470, 195, 'S·R', size=13, color=POS, anchor='start', bold=True))
    parts.append(text(cxR + 60, cyR + 92, 'S·R  (спершу поворот, тоді розтяг)', size=13, bold=True))
    parts.append(text(cxR + 60, cyR + 110, 'повернутий, далі розтягнутий', size=11, color=MUTED))

    parts.append(text(W / 2, H - 14, 'Множення матриць читають праворуч-наліво; інша черга — інша геометрія.',
                      size=12, color="#7a3ea8", italic=True))

    render(os.path.join(OUT, 'order.svg'), W, H, *parts)


fig_machine()
fig_order()
print('SVG figures generated in', OUT)
