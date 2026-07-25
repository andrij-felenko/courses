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


# ── Фігура 3: множення на i — поворот на 90°, звідки i² = −1 ─────────────────
# Геометричне серце фазорної алгебри. Помножити стрілку на i = повернути її на
# +90° без зміни довжини; двічі поспіль (i²) = розворот на 180° = зміна знака.
# Саме це «повернути на 90°» стоїть за зсувом фази реактивного елемента й за
# похідною = множенням на i·ω. Три стрілки z, i·z, i²·z=−z на спільному колі.

def fig_multiply_i():
    W, H = 680, 430
    cx, cy = 300, 235
    R = 120

    th_z = math.radians(35)     # z у першій чверті
    th_iz = math.radians(125)   # i·z = z + 90°
    th_nz = math.radians(215)   # i²·z = z + 180° = −z

    def pt(th, r=R):
        return cx + r * math.cos(th), cy - r * math.sin(th)

    zx, zy = pt(th_z)
    gx, gy = pt(th_iz)
    bx, by = pt(th_nz)

    parts = []

    # осі комплексної площини
    parts.append(arrow(150, cy, 470, cy, color=MUTED, sw=1.3))
    parts.append(arrow(cx, 375, cx, 95, color=MUTED, sw=1.3))
    parts.append(text(476, cy + 4, 'Re', 12, MUTED, 'start'))
    parts.append(text(cx, 88, 'Im', 12, MUTED, 'middle'))

    # напрямне коло сталої довжини (усі три стрілки однакові)
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.2" stroke-dasharray="4 4"/>' % (cx, cy, R, MUTED))

    # дуги двох поворотів на +90° (полілінії на колі)
    def arc(a1, a2, color):
        steps = 40
        pts = ['%.1f,%.1f' % pt(a1 + (a2 - a1) * i / steps) for i in range(steps + 1)]
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                % (' '.join(pts), color))
    parts.append(arc(th_z, th_iz, FIELD))
    parts.append(arc(th_iz, th_nz, NEG))

    # мітки «·i» усередині, біля середини кожної дуги
    lx1, ly1 = pt(math.radians(80), 90)
    lx2, ly2 = pt(math.radians(170), 90)
    parts.append(text(lx1, ly1, '·i', 13, INK, 'middle', bold=True))
    parts.append(text(lx2, ly2, '·i', 13, INK, 'middle', bold=True))

    # три стрілки
    parts.append(arrow(cx, cy, zx, zy, color=POS, sw=3.0))
    parts.append(arrow(cx, cy, gx, gy, color=FIELD, sw=3.0))
    parts.append(arrow(cx, cy, bx, by, color=NEG, sw=3.0))
    parts.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))

    # мітки стрілок (поза кінцями, щоб лінія не різала напис)
    parts.append(text(zx + 12, zy - 4, 'z', 15, POS, 'start', bold=True))
    parts.append(text(gx, gy - 16, 'i·z', 14, FIELD, 'middle', bold=True))
    parts.append(text(bx, by + 22, 'i²·z = −z', 14, NEG, 'middle', bold=True))

    parts.append(text(cx + 40, H - 18,
                      'Помножити на i — поворот на +90° без зміни довжини; двічі (i²) — розворот, тобто −1',
                      12, INK, 'middle'))

    render(os.path.join(IMG, 'multiply-by-i.svg'), W, H, *parts,
           title='Множення на i — це поворот на 90°')


fig_rotating()
fig_addition()
fig_multiply_i()
print('Done. SVG in', IMG)
