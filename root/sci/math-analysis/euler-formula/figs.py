import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: e^(iθ) — точка на одиничному колі; θ — довжина дуги ─────────────
# Показує комплексну площину: горизонталь — дійсна вісь, вертикаль — уявна.
# Точка e^(iθ) лежить на колі радіуса 1; її координати — (cos θ, sin θ).
# Кут θ дорівнює довжині пройденої дуги. Це ЯДРО формули.

def fig_unit_circle():
    W, H = 560, 470
    ox, oy = 250, 250        # центр кола (= початок площини) у пікселях
    R = 170                  # радіус одиничного кола у пікселях

    th = math.radians(52)    # обраний кут θ для ілюстрації
    px = ox + R * math.cos(th)
    py = oy - R * math.sin(th)

    parts = []

    # осі
    parts.append(arrow(ox - R - 50, oy, ox + R + 55, oy, color=INK, sw=1.5))
    parts.append(arrow(ox, oy + R + 55, ox, oy - R - 55, color=INK, sw=1.5))
    parts.append(text(ox + R + 64, oy + 5, 'Re', size=13, color=INK, anchor='start'))
    parts.append(text(ox + 8, oy - R - 60, 'Im', size=13, color=INK, anchor='start'))

    # позначки 1 та i на осях
    parts.append(text(ox + R, oy + 18, '1', size=12, color=MUTED, anchor='middle'))
    parts.append(text(ox - 12, oy - R + 4, 'i', size=12, color=MUTED, anchor='end'))
    parts.append(line(ox + R, oy - 4, ox + R, oy + 4, color=MUTED, sw=1))
    parts.append(line(ox - 4, oy - R, ox + 4, oy - R, color=MUTED, sw=1))

    # одиничне коло
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (ox, oy, R, FIELD))

    # дуга θ від додатної дійсної осі (виділяє, що θ = довжина дуги)
    aN = 40
    arc = []
    for i in range(aN + 1):
        a = th * i / aN
        arc.append('%.1f,%.1f' % (ox + (R + 0) * math.cos(a), oy - (R + 0) * math.sin(a)))
    # маленька дуга-індикатор кута біля центра
    rk = 40
    karc = []
    for i in range(aN + 1):
        a = th * i / aN
        karc.append('%.1f,%.1f' % (ox + rk * math.cos(a), oy - rk * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (' '.join(karc), POS))
    parts.append(text(ox + (rk + 22) * math.cos(th / 2), oy - (rk + 22) * math.sin(th / 2),
                      'θ', size=15, color=POS, anchor='middle'))

    # радіус-вектор до точки e^(iθ)
    parts.append(arrow(ox, oy, px, py, color=NEG, sw=2.5))

    # проєкції: cos θ (по дійсній) і sin θ (по уявній)
    parts.append(line(px, py, px, oy, color=MUTED, sw=1.3, dash='5 3'))   # вниз на Re
    parts.append(line(px, py, ox, py, color=MUTED, sw=1.3, dash='5 3'))   # вліво на Im
    # відрізок cos θ на дійсній осі
    parts.append(line(ox, oy, px, oy, color=POS, sw=3))
    parts.append(text((ox + px) / 2, oy + 18, 'cos θ', size=12, color=POS, anchor='middle'))
    # відрізок sin θ на уявній осі
    parts.append(line(ox, oy, ox, py, color=NEG, sw=3))
    parts.append(text(ox - 14, (oy + py) / 2 + 4, 'sin θ', size=12, color=NEG, anchor='end'))

    # точка
    parts.append(circle(px, py, 5.5, fill=NEG, stroke=INK, sw=1.2))
    # підпис точки
    tb, tw, thh = textbox(px + 70, py - 18, 'e^(iθ) = cos θ + i·sin θ',
                          size=13, color=INK, fill=FILL, stroke=NEG, sw=1.3)
    parts.append(tb)
    # лінія-вказівник від підпису до точки
    parts.append(line(px + 7, py - 4, px + 70 - tw / 2 - 2, py - 18, color=MUTED, sw=1))

    # центр
    parts.append(circle(ox, oy, 3.5, fill=INK, stroke=INK, sw=1))
    parts.append(text(ox - 10, oy + 16, '0', size=12, color=INK, anchor='end'))

    # підказка про довжину дуги внизу
    parts.append(text(W / 2, H - 14,
                      'Радіус завжди 1; θ — довжина дуги від «1». Координати точки — (cos θ, sin θ)',
                      size=11, color=MUTED, anchor='middle'))

    render(os.path.join(OUT, 'unit-circle.svg'), W, H, *parts,
           title='e^(iθ): точка на одиничному колі під кутом θ')


# ── Фігура 2: рух точки колом ⇄ коливання cos θ і sin θ ──────────────────────
# Зліва — обертання на колі; справа — як проєкції на осі викреслюють косинус
# і синус, коли θ росте. Показує, ЧОМУ обертання породжує коливання.

def fig_rotation_to_waves():
    W, H = 620, 380
    # ── ліворуч: коло
    cx, cy, R = 130, 190, 110
    th = math.radians(58)
    px = cx + R * math.cos(th)
    py = cy - R * math.sin(th)

    parts = []
    # осі кола
    parts.append(line(cx - R - 18, cy, cx + R + 18, cy, color=MUTED, sw=1))
    parts.append(line(cx, cy + R + 18, cx, cy - R - 18, color=MUTED, sw=1))
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="2"/>' % (cx, cy, R, FIELD))
    # стрілка обертання (проти годинникової)
    aN = 30
    ar = []
    for i in range(aN + 1):
        a = math.radians(-18) + (math.radians(108) - math.radians(-18)) * i / aN
        ar.append('%.1f,%.1f' % (cx + (R + 16) * math.cos(a), cy - (R + 16) * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)"/>' % (' '.join(ar), POS))
    parts.append(text(cx + (R + 30) * math.cos(math.radians(50)),
                      cy - (R + 30) * math.sin(math.radians(50)),
                      'θ росте', size=11, color=POS, anchor='middle'))
    # радіус-вектор і проєкції
    parts.append(arrow(cx, cy, px, py, color=NEG, sw=2.3))
    parts.append(line(px, py, px, cy, color=MUTED, sw=1.2, dash='4 3'))
    parts.append(line(px, py, cx, py, color=MUTED, sw=1.2, dash='4 3'))
    parts.append(circle(px, py, 5, fill=NEG, stroke=INK, sw=1.1))
    parts.append(circle(cx, cy, 3, fill=INK, stroke=INK, sw=1))
    parts.append(text(cx, cy + R + 32, 'обертання', size=12, color=INK, anchor='middle'))

    # ── праворуч: дві хвилі (cos і sin) як функції θ
    gx0 = 290               # початок осі θ
    gw = 300                # довжина по θ
    axc = 110               # вісь косинуса (y-рівень)
    axs = 270               # вісь синуса
    amp = 60                # амплітуда у пікселях (= R-незалежно, для читабельності)
    Tpx = gw / (2 * math.pi)  # пікселів на радіан

    # осі θ для обох хвиль
    for ay, lab, col in [(axc, 'cos θ', POS), (axs, 'sin θ', NEG)]:
        parts.append(arrow(gx0 - 6, ay, gx0 + gw + 16, ay, color=MUTED, sw=1))
        parts.append(text(gx0 + gw + 22, ay + 4, 'θ', size=12, color=MUTED, anchor='start'))
        parts.append(text(gx0 - 10, ay - amp - 6, lab, size=12, color=col, anchor='start'))

    # криві
    N = 120
    cpts, spts = [], []
    for i in range(N + 1):
        a = 2 * math.pi * i / N
        x = gx0 + a * Tpx
        cpts.append('%.1f,%.1f' % (x, axc - amp * math.cos(a)))
        spts.append('%.1f,%.1f' % (x, axs - amp * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (' '.join(cpts), POS))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (' '.join(spts), NEG))

    # поточний кут θ на обох графіках + горизонтальні «містки» від кола
    xth = gx0 + th * Tpx
    cyv = axc - amp * math.cos(th)
    syv = axs - amp * math.sin(th)
    parts.append(line(xth, axc - amp - 6, xth, axs + amp + 6, color=MUTED, sw=1, dash='3 3'))
    parts.append(circle(xth, cyv, 4.5, fill=POS, stroke=INK, sw=1))
    parts.append(circle(xth, syv, 4.5, fill=NEG, stroke=INK, sw=1))
    # містки: висота точки на колі = висота синуса; ширина = косинус
    parts.append(line(px, py, xth, syv, color=NEG, sw=1, dash='2 4'))

    # підпис унизу
    parts.append(text((gx0 + gx0 + gw) / 2, H - 12,
                      'Та сама точка: її висота — sin θ, її «ширина» — cos θ',
                      size=11, color=MUTED, anchor='middle'))

    render(os.path.join(OUT, 'rotation-to-waves.svg'), W, H, *parts,
           title='Обертання породжує коливання: проєкції дають cos і sin')


# ── Фігура 3: e^(iπ) = −1 — пів-оберт; e^(iπ)+1 = 0 ──────────────────────────
# Показує особливі точки кола (θ = 0, π/2, π, 3π/2) і чому пів-кола приводить
# рівно в −1, звідки тотожність Ейлера.

def fig_eipi():
    W, H = 540, 470
    ox, oy, R = 270, 205, 150

    parts = []
    # осі
    parts.append(arrow(ox - R - 45, oy, ox + R + 50, oy, color=INK, sw=1.5))
    parts.append(arrow(ox, oy + R + 45, ox, oy - R - 50, color=INK, sw=1.5))
    parts.append(text(ox + R + 58, oy + 5, 'Re', size=13, color=INK, anchor='start'))
    parts.append(text(ox + 8, oy - R - 42, 'Im', size=13, color=INK, anchor='start'))

    # коло
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.8"/>' % (ox, oy, R, FIELD))

    # верхня півдуга 0 → π (шлях руху) — виділена
    aN = 60
    half = []
    for i in range(aN + 1):
        a = math.pi * i / aN
        half.append('%.1f,%.1f' % (ox + R * math.cos(a), oy - R * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
                 'marker-end="url(#arrow)"/>' % (' '.join(half), POS))

    # ключові точки
    pts = [
        (0,            'e^(i·0) = 1',      '1',  MUTED, 'start',  14, 18),
        (math.pi / 2,  'e^(iπ/2) = i',     'i',  NEG,   'middle', 0, -14),
        (math.pi,      'e^(iπ) = −1',      '−1', POS,   'end',    -14, 18),
        (3 * math.pi / 2, 'e^(i·3π/2) = −i', '−i', MUTED, 'end',   -12, 5),
    ]
    for a, lab, short, col, anch, dx, dy in pts:
        x = ox + R * math.cos(a)
        y = oy - R * math.sin(a)
        parts.append(circle(x, y, 5.5, fill=col, stroke=INK, sw=1.2))
        parts.append(text(x + dx, y + dy, short, size=13, color=col, anchor=anch, bold=True))

    # вектор у −1
    parts.append(arrow(ox, oy, ox - R, oy, color=POS, sw=2.2))

    # дуга-кут π
    rk = 46
    karc = []
    for i in range(aN + 1):
        a = math.pi * i / aN
        karc.append('%.1f,%.1f' % (ox + rk * math.cos(a), oy - rk * math.sin(a)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (' '.join(karc), INK))
    parts.append(text(ox, oy - rk - 8, 'θ = π', size=12, color=INK, anchor='middle'))

    # центр
    parts.append(circle(ox, oy, 3.5, fill=INK, stroke=INK, sw=1))

    # тотожність унизу, у рамці (нижче −i, без накладань)
    fb, fw, fh = textbox(ox, H - 42, 'e^(iπ) + 1 = 0',
                         size=18, color=INK, fill='#fff8e1', stroke='#f0b429', sw=1.6, bold=True)
    parts.append(fb)
    parts.append(text(ox, H - 12,
                      'Пів-оберт (θ=π) приводить рівно в −1 — звідси тотожність Ейлера',
                      size=11, color=MUTED, anchor='middle'))

    render(os.path.join(OUT, 'euler-identity.svg'), W, H, *parts,
           title='Чотири чверті кола та e^(iπ) + 1 = 0')


fig_unit_circle()
fig_rotation_to_waves()
fig_eipi()
print('SVG figures generated in', OUT)
