# -*- coding: utf-8 -*-
"""Фігури до теми «Логарифми».
Імпортує спільний svgkit зі scripts/ (НЕ копіювати функції).
Дві фігури:
  1) log-graph.svg   — графік y=log₂x: множення на x ⇒ додавання до y.
  2) log-scale.svg   — логарифмічна шкала: кожне ×10 — однакова відстань.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — графік y = log₂(x)
# Показуємо: x подвоюється (1,2,4,8,16 — множення) ⇒ y росте на +1 (0,1,2,3,4).
# x-діапазон на полотні: [0, 16]; y-діапазон: [-2.4, 4.4].
# Початок мат-координат у пікселях (ox, oy); масштаби sx, sy.
# Перевірка меж: при x=16 → ox+16*sx; при y=4.4 → oy-4.4*sy (мають бути в W×H).
# ════════════════════════════════════════════════════════════════════════════
def fig_graph():
    W, H = 600, 400
    ox, oy = 70, 250          # SVG-координати мат-точки (0,0)
    sx = 31.0                 # px на одиницю x  → 70 + 16*31 = 566  (< 600)
    sy = 40.0                 # px на одиницю y  → 250 - 4.4*40 = 74 (> 0); 250 + 2.4*40 = 346 (< 400)

    def gx(xv): return ox + xv * sx
    def gy(yv): return oy - yv * sy

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # осі
    f.append(arrow(gx(-0.3), gy(0), gx(16.4), gy(0), color=INK, sw=1.5))
    f.append(text(gx(16.4), gy(0) + 18, 'x', 14, INK, 'middle'))
    f.append(arrow(gx(0), gy(-2.4), gx(0), gy(4.5), color=INK, sw=1.5))
    f.append(text(gx(0) - 16, gy(4.5) + 4, 'y', 14, INK, 'middle'))

    # крива y=log2(x) — від малого x>0 до 16
    pts = []
    xv = 0.28
    while xv <= 16.0001:
        yv = math.log(xv, 2)
        pts.append('%.1f,%.1f' % (gx(xv), gy(yv)))
        xv += 0.12
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (' '.join(pts), POS))

    # вузли подвоєння: x=1,2,4,8,16 → y=0,1,2,3,4
    for k in range(0, 5):
        xv = 2 ** k
        yv = k
        # пунктир до осей
        f.append(line(gx(xv), gy(0), gx(xv), gy(yv), color=MUTED, sw=1, dash='3,3'))
        f.append(line(gx(0), gy(yv), gx(xv), gy(yv), color=MUTED, sw=1, dash='3,3'))
        f.append(circle(gx(xv), gy(yv), 4.0, fill=POS, stroke=BG, sw=1.5))
        # підпис x під віссю
        f.append(text(gx(xv), gy(0) + 18, str(xv), 12, INK, 'middle'))
        # підпис y ліворуч від осі
        f.append(text(gx(0) - 14, gy(yv) + 4, str(yv), 12, INK, 'middle'))

    # анотація: ×2 на x ⇒ +1 на y  (між x=4 і x=8)
    f.append(text(gx(6), gy(0) + 40, '×2 по x', 12, NEG, 'middle', bold=True))
    f.append(text(gx(0) - 46, gy(2.5), '+1 по y', 12, FIELD, 'middle', bold=True))

    # підпис кривої
    f.append(text(gx(11), gy(3.4) + 4, 'y = log₂ x', 14, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'log-graph.svg'), W, H, *f,
           title='Логарифм: множення на осі x → додавання на осі y')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — логарифмічна шкала
# Числа 1, 10, 100, 1000, 10000 стоять РІВНОМІРНО (кожне ×10 — однаковий крок).
# Знизу прив'язка до реальних шкал, що так влаштовані (дБ, Ріхтер, pH).
# ════════════════════════════════════════════════════════════════════════════
def fig_scale():
    W, H = 640, 300
    x0 = 70                   # лівий край шкали (10^0)
    x1 = 570                  # правий край шкали (10^4)
    ybar = 130                # вертикаль смуги
    steps = 4                 # від 10^0 до 10^4
    dx = (x1 - x0) / steps    # 125 px на кожне ×10

    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))

    # головна вісь
    f.append(arrow(x0 - 20, ybar, x1 + 24, ybar, color=INK, sw=2))

    labels = ['1', '10', '100', '1000', '10000']
    powers = ['10⁰', '10¹', '10²', '10³', '10⁴']
    for i in range(steps + 1):
        x = x0 + i * dx
        f.append(line(x, ybar - 8, x, ybar + 8, color=INK, sw=2))
        f.append(text(x, ybar - 16, labels[i], 13, INK, 'middle', bold=True))
        f.append(text(x, ybar + 26, powers[i], 12, MUTED, 'middle'))

    # дуги «×10 = однакова відстань» між сусідніми мітками
    for i in range(steps):
        xa = x0 + i * dx
        xb = x0 + (i + 1) * dx
        midx = (xa + xb) / 2
        f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.4"/>'
                 % (xa + 6, ybar - 40, midx, ybar - 58, xb - 6, ybar - 40, NEG))
        f.append(text(midx, ybar - 62, '×10', 11, NEG, 'middle', bold=True))

    # підпис зверху
    f.append(text(W / 2, ybar - 80, 'Кожен крок ×10 — однакова відстань',
                  13, INK, 'middle', bold=True))

    # прив'язка до реальних шкал
    box, bw, bh = textbox(W / 2, 232,
                          'Так само влаштовані: децибели (×10 потужності = +10 дБ),\n'
                          'шкала Ріхтера (×10 амплітуди = +1 бал), pH (×10 [H⁺] = −1 pH)',
                          size=12.5, pad=12, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'log-scale.svg'), W, H, *f,
           title='Логарифмічна шкала стискає велике в осяжне')


if __name__ == '__main__':
    fig_graph()
    fig_scale()
    print('OK: log-graph.svg, log-scale.svg')
