# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура: імпеданс Z на комплексній площині ────────────────────────────────
# Стрілка Z = R + jX від початку координат. Горизонтальний катет R (активний
# опір, дійсна вісь), вертикальний катет X (реактивність, уявна вісь), сама
# стрілка — модуль |Z|, дуга біля початку — аргумент φ (зсув фази).
# Підказки на осях: угору = індуктивне (котушка, X>0), униз = ємнісне
# (конденсатор, X<0). Так одна картинка показує: дійсна вісь = тепло,
# уявна = зсув фази на 90°, а Z = їхня векторна сума.

def fig_plane():
    W, H = 660, 440
    ox, oy = 170, 250            # початок координат (нуль комплексної площини)

    # катети імпедансу (px): R праворуч, X угору (індуктивний випадок)
    R = 200.0
    X = 150.0
    ex = ox + R                  # кінець стрілки Z по горизонталі
    ey = oy - X                  # кінець стрілки Z по вертикалі

    parts = []

    # ── осі комплексної площини
    parts.append(arrow(ox - 40, oy, ox + R + 70, oy, color=MUTED, sw=1.4))   # Re →
    parts.append(arrow(ox, oy + 110, ox, oy - X - 80, color=MUTED, sw=1.4))  # Im ↑
    parts.append(text(ox + R + 78, oy + 16, 'Re', 13, MUTED, 'start'))
    parts.append(text(ox + 14, oy - X - 74, 'Im', 13, MUTED, 'start'))
    # підписи сенсу осей
    parts.append(text(ox + R + 78, oy + 34, '(R, тепло)', 11, MUTED, 'start'))
    parts.append(text(ox + 14, oy - X - 58, '(X, фаза)', 11, MUTED, 'start'))

    # ── катет R (дійсна частина) — пунктир по горизонталі
    parts.append(line(ox, oy, ex, oy, color=POS, sw=1.6, dash="6 4"))
    parts.append(text(ox + R / 2, oy + 22, 'R  (активний опір)', 12, POS, 'middle'))

    # ── катет X (уявна частина) — пунктир по вертикалі від кінця R угору
    parts.append(line(ex, oy, ex, ey, color=FIELD, sw=1.6, dash="6 4"))
    parts.append(text(ex + 14, oy - X / 2, 'X = ω·L', 12, FIELD, 'start'))
    parts.append(text(ex + 14, oy - X / 2 + 16, '(реактивність)', 11, FIELD, 'start'))

    # ── стрілка Z = R + jX (модуль |Z|) — головна, червона
    parts.append(arrow(ox, oy, ex, ey, color=INK, sw=3.0))
    tbz, _, _ = textbox(ox + 0.5 * R - 26, oy - 0.5 * X - 18,
                        '|Z| = √(R²+X²)', size=13, color=INK,
                        fill="#fff8e1", stroke="#f0b429", sw=1.2)
    parts.append(tbz)
    parts.append(text(ex + 6, ey - 10, 'Z = R + jX', 13, INK, 'start', bold=True))

    # ── дуга кута φ біля початку координат
    ar = 52
    phi = math.atan2(X, R)
    a_pts = []
    steps = 28
    for i in range(steps + 1):
        a = phi * i / steps
        a_pts.append('%.1f,%.1f' % (ox + ar * math.cos(a), oy - ar * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (' '.join(a_pts), NEG))
    parts.append(text(ox + ar + 20, oy - 14, 'φ', 14, NEG, 'middle', italic=True))
    parts.append(text(ox + ar + 16, oy - 30, '(зсув фази)', 10, NEG, 'middle'))

    # ── точки
    parts.append(circle(ox, oy, 5, fill=INK, stroke=INK, sw=1))
    parts.append(circle(ex, ey, 5.5, fill=POS, stroke=INK, sw=1.3))

    # ── маркери напрямків реактивності на уявній осі
    parts.append(text(ox - 12, oy - X - 40, '↑ котушка: X > 0', 11, FIELD, 'end'))
    parts.append(text(ox - 12, oy + 80, '↓ конденсатор: X < 0', 11, POS, 'end'))

    # ── рамка-висновок праворуч унизу
    box = fitbox(W - 212, H - 116, 196, 96,
                 'Z — стрілка на площині:\n• довжина |Z| = у скільки разів\n   напруга більша за струм\n• кут φ = на скільки струм\n   зсунутий за фазою',
                 size=12, fill=FILL, stroke=MUTED, sw=1.2, color=INK)
    parts.append(box)

    render(os.path.join(IMG, 'impedance-plane.svg'), W, H, *parts,
           title='Імпеданс Z = R + jX на комплексній площині')


fig_plane()
print('Done. SVG in', IMG)
