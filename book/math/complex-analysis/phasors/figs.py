# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: фазор як обертовий вектор → синусоїда ──────────────────────────
# Зліва коло на комплексній площині з вектором (фазором) під кутом φ.
# Справа — графік проєкції кінця вектора на вертикальну вісь у часі:
# повний оберт малює один період синусоїди. Горизонтальний пунктир пов'язує
# висоту вектора з висотою точки на хвилі — це і є «фазор подає синусоїду».

def fig_rotating():
    W, H = 660, 380
    # ліве коло
    cx, cy = 150, 200          # центр кола (комплексна площина)
    R = 110                    # радіус = амплітуда
    phi = math.radians(38)     # поточний кут фазора ωt+φ

    # права вісь часу
    gx0 = 300                  # початок осі часу (x), збігається з рівнем cx по фазі 0
    gy0 = cy                   # нульова лінія хвилі = центр кола по висоті
    span = 330                 # довжина осі часу в px
    # один оберт (2π) розкладаємо на span; амплітуда по висоті = R

    parts = []

    # ── комплексна площина: осі
    parts.append(arrow(cx - R - 24, cy, cx + R + 28, cy, color=MUTED, sw=1.3))  # Re
    parts.append(arrow(cx, cy + R + 24, cx, cy - R - 28, color=MUTED, sw=1.3))  # Im
    parts.append(text(cx + R + 30, cy + 14, 'Re', 12, MUTED, 'middle'))
    parts.append(text(cx + 16, cy - R - 18, 'Im', 12, MUTED, 'middle'))

    # коло, яким ходить кінець фазора
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.3" stroke-dasharray="4 4"/>' % (cx, cy, R, MUTED))

    # кінець фазора
    ex = cx + R * math.cos(phi)
    ey = cy - R * math.sin(phi)

    # дуга кута φ біля центра
    ar = 34
    a_pts = []
    steps = 24
    for i in range(steps + 1):
        a = phi * i / steps
        a_pts.append('%.1f,%.1f' % (cx + ar * math.cos(a), cy - ar * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (' '.join(a_pts), POS))
    parts.append(text(cx + ar + 16, cy - 10, 'ωt+φ', 11, POS, 'middle'))

    # проєкція кінця на Im (вертикальний катет = миттєве значення)
    parts.append(line(cx, ey, ex, ey, color=FIELD, sw=1.3, dash="5 3"))
    parts.append(line(ex, cy, ex, ey, color=MUTED, sw=1.0, dash="3 3"))

    # сам фазор (обертовий вектор) — червоний
    parts.append(arrow(cx, cy, ex, ey, color=POS, sw=2.6))
    tb, _, _ = textbox(cx + 0.55 * (ex - cx) - 6, cy - 0.55 * (cy - ey) - 16,
                       'A', size=15, color=POS, fill="#fdecea", stroke=POS, sw=1)
    parts.append(tb)

    # ── права частина: синусоїда як проєкція
    parts.append(arrow(gx0 - 6, gy0, gx0 + span + 16, gy0, color=MUTED, sw=1.3))
    parts.append(text(gx0 + span + 18, gy0 + 14, 't', 12, MUTED, 'middle'))
    # вертикальна вісь значення на старті
    parts.append(line(gx0, gy0 - R - 6, gx0, gy0 + R + 6, color=MUTED, sw=1.0))

    # синусоїда: value(t) = R*sin(phi + 2π * t)
    npts = 240
    sin_pts = []
    for i in range(npts + 1):
        frac = i / npts                       # 0..1 = один оберт
        ang = phi + 2 * math.pi * frac
        xx = gx0 + frac * span
        yy = gy0 - R * math.sin(ang)
        sin_pts.append('%.1f,%.1f' % (xx, yy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (' '.join(sin_pts), NEG))

    # стартова точка хвилі = поточна висота фазора; пунктир єднає їх
    parts.append(line(ex, ey, gx0, ey, color=FIELD, sw=1.2, dash="5 3"))
    parts.append(circle(gx0, ey, 4, fill=FIELD, stroke=INK, sw=1))
    parts.append(circle(ex, ey, 4.5, fill=POS, stroke=INK, sw=1.2))

    # позначка амплітуди на хвилі
    peak_x = gx0 + span * ((math.pi / 2 - phi) / (2 * math.pi) % 1.0)
    parts.append(line(gx0, gy0 - R, peak_x + 4, gy0 - R, color=MUTED, sw=1.0, dash="2 4"))
    parts.append(text(gx0 + 8, gy0 - R - 6, 'A', 12, NEG, 'start'))

    # підпис під лівим і правим блоком
    parts.append(text(cx, cy + R + 44, 'фазор: вектор A під кутом ωt+φ', 11, INK, 'middle'))
    parts.append(text(gx0 + span / 2, gy0 + R + 44, 'його вертикальна проєкція у часі = синусоїда', 11, INK, 'middle'))

    render(os.path.join(IMG, 'rotating-phasor.svg'), W, H, *parts,
           title='Фазор: обертовий вектор і синусоїда, яку він малює')


# ── Фігура 2: додавання двох синусоїд через фазори ──────────────────────────
# Дві синусоїди однакової частоти, різні амплітуди й фази. Зліва — складання
# їх як векторів (голова до хвоста / паралелограм) дає один фазор-суму.
# Праворуч — підпис, що сума теж синусоїда тієї ж частоти.

def fig_addition():
    W, H = 640, 400
    ox, oy = 150, 250          # спільний початок фазорів

    # фазор 1: амплітуда 120, кут 20°
    A1, p1 = 120.0, math.radians(18)
    # фазор 2: амплітуда 95, кут 78°
    A2, p2 = 95.0, math.radians(74)

    x1 = ox + A1 * math.cos(p1)
    y1 = oy - A1 * math.sin(p1)
    x2 = ox + A2 * math.cos(p2)
    y2 = oy - A2 * math.sin(p2)
    # сума (комплексне додавання = векторне)
    sx = ox + A1 * math.cos(p1) + A2 * math.cos(p2)
    sy = oy - (A1 * math.sin(p1) + A2 * math.sin(p2))

    parts = []

    # осі комплексної площини
    parts.append(arrow(ox - 24, oy, ox + 300, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 26, ox, oy - 240, color=MUTED, sw=1.3))
    parts.append(text(ox + 302, oy + 14, 'Re', 12, MUTED, 'middle'))
    parts.append(text(ox + 16, oy - 236, 'Im', 12, MUTED, 'middle'))

    # перенесений фазор 2 (від кінця 1) — пунктир, метод голова-до-хвоста
    tx2 = x1 + A2 * math.cos(p2)
    ty2 = y1 - A2 * math.sin(p2)
    parts.append(arrow(x1, y1, tx2, ty2, color=MUTED, sw=1.6))
    # перенесений фазор 1 (від кінця 2) — пунктир, замикає паралелограм
    parts.append(line(x2, y2, sx, sy, color=MUTED, sw=1.1, dash="5 4"))

    # фазор 1 — синій
    parts.append(arrow(ox, oy, x1, y1, color=NEG, sw=2.6))
    tb1, _, _ = textbox(ox + 0.5 * (x1 - ox) + 4, oy - 0.5 * (oy - y1) + 18,
                        'A₁ ∠φ₁', size=12, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1)
    parts.append(tb1)

    # фазор 2 — зелений
    parts.append(arrow(ox, oy, x2, y2, color=FIELD, sw=2.6))
    tb2, _, _ = textbox(ox - 38, oy - 0.5 * (oy - y2), 'A₂ ∠φ₂',
                        size=12, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1)
    parts.append(tb2)

    # сума — червоний
    parts.append(arrow(ox, oy, sx, sy, color=POS, sw=3.0))
    tbs, _, _ = textbox(ox + 0.52 * (sx - ox) + 30, oy - 0.52 * (oy - sy) - 6,
                        'A ∠φ', size=14, color=POS, fill="#fdecea", stroke=POS, sw=1)
    parts.append(tbs)

    # точки
    parts.append(circle(ox, oy, 5, fill=INK, stroke=INK, sw=1))
    parts.append(circle(x1, y1, 4, fill=NEG, stroke=INK, sw=1))
    parts.append(circle(x2, y2, 4, fill=FIELD, stroke=INK, sw=1))
    parts.append(circle(sx, sy, 5, fill=POS, stroke=INK, sw=1.2))

    # права рамка-висновок
    box = fitbox(W - 196, 60, 184, 96,
                 'Складаємо вектори,\nне функції:\nдві суми по осях →\nодин фазор A ∠φ.\nЦе знову синусоїда\nтієї самої частоти.',
                 size=12, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK)
    parts.append(box)

    parts.append(text(W // 2, H - 12,
                      'Сума двох синусоїд однакової частоти = векторна сума їхніх фазорів',
                      11, MUTED, 'middle'))

    render(os.path.join(IMG, 'phasor-addition.svg'), W, H, *parts,
           title='Додавання синусоїд через фазори: вектор + вектор')


fig_rotating()
fig_addition()
print('Done. SVG in', IMG)
