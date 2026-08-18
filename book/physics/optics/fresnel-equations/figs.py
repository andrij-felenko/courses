# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"
AIR   = "#ffffff"

def ang(a):
    return math.radians(a)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрія падіння: площина падіння, s- та p-поляризації
# ═══════════════════════════════════════════════════════════════════════════
def fig_polarization_geometry():
    W, H = 700, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Геометрія падіння: s- та p-поляризації світла', 16, INK, 'middle', bold=True))

    cx, py = 320, 190
    # Нижнє середовище (n2 - скло)
    f.append(rect(60, py, 520, H - py - 30, fill=GLASS, stroke='none', sw=0, rx=0))
    # Межа розділу
    f.append(line(60, py, 580, py, color=INK, sw=2))
    # Нормаль
    f.append(line(cx, py - 110, cx, py + 110, color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(cx + 8, py - 96, 'нормаль', 10, MUTED, 'start'))

    n1, n2 = 1.00, 1.50
    theta1 = 45.0
    t1 = ang(theta1)
    t2 = math.asin((n1 / n2) * math.sin(t1))
    theta2 = math.degrees(t2)
    L = 120

    # Падаючий промінь (згори-зліва до точки падіння)
    ix = cx - L * math.sin(t1)
    iy = py - L * math.cos(t1)
    f.append(arrow(ix, iy, cx, py, color=POS, sw=2.5))
    f.append(text(ix - 10, iy - 6, 'падаючий промінь', 11, POS, 'end', bold=True))

    # Відбитий промінь (з точки падіння вгору-вправо)
    rx = cx + L * math.sin(t1)
    ry = py - L * math.cos(t1)
    f.append(arrow(cx, py, rx, ry, color=NEG, sw=2.2))
    f.append(text(rx + 10, ry - 6, 'відбитий промінь', 11, NEG, 'start', bold=True))

    # Заломлений промінь (з точки падіння вниз-вправо)
    tx = cx + L * math.sin(t2)
    ty = py + L * math.cos(t2)
    f.append(arrow(cx, py, tx, ty, color=FIELD, sw=2.5))
    f.append(text(tx + 10, ty + 12, 'заломлений промінь', 11, FIELD, 'start', bold=True))

    # Позначки кутів θ1 та θ2
    f.append(text(cx - 22, py - 45, 'θ₁', 13, INK, 'middle', bold=True, italic=True))
    f.append(text(cx + 18, py + 45, 'θ₂', 13, INK, 'middle', bold=True, italic=True))

    # s-поляризація (вектор E_s перпендикулярний до площини малюнка — точка ⊙)
    sx = cx - 0.5 * L * math.sin(t1) - 18
    sy = py - 0.5 * L * math.cos(t1) + 10
    f.append(circle(sx, sy, 7, fill=BG, stroke=POS, sw=1.5))
    f.append(circle(sx, sy, 2, fill=POS, stroke=POS, sw=1))
    f.append(text(sx - 12, sy + 4, 'Eₛ (перпендикулярно)', 10, POS, 'end'))

    # p-поляризація (вектор E_p у площині малюнка)
    px = cx - 0.5 * L * math.sin(t1) + 16
    py_p = py - 0.5 * L * math.cos(t1) - 10
    ex1 = px - 12 * math.cos(t1)
    ey1 = py_p + 12 * math.sin(t1)
    ex2 = px + 12 * math.cos(t1)
    ey2 = py_p - 12 * math.sin(t1)
    f.append(line(ex1, ey1, ex2, ey2, color=NEG, sw=2))
    f.append(text(px + 14, py_p - 6, 'Eₚ (у площині падіння)', 10, NEG, 'start'))

    # Підписи середовищ
    f.append(text(80, py - 14, 'середовище 1 (n₁)', 11, MUTED, 'start'))
    f.append(text(80, py + 22, 'середовище 2 (n₂ > n₁)', 11, MUTED, 'start'))

    # Інформаційна рамка праворуч
    f.append(fitbox(590, 80, 100, 110,
                    'Площина падіння:\nмістить падаючий промінь\nта нормаль до межі.\ns: E ⟂ площині\np: E ∥ площині',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'polarization-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Графік коефіцієнтів відбиття R_s та R_p від кута падіння θ1
# ═══════════════════════════════════════════════════════════════════════════
def fig_fresnel_curves():
    W, H = 680, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Залежність коефіцієнтів відбиття Rₛ та Rₚ від кута падіння', 16, INK, 'middle', bold=True))

    ox, oy = 70, 310
    gw, gh = 480, 240

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill='#fafbfc', stroke=MUTED, sw=1))

    # Вертикальні лінії сітки (кути 0°, 15°, 30°, 45°, 60°, 75°, 90°)
    for deg in [0, 15, 30, 45, 60, 75, 90]:
        x = ox + (deg / 90.0) * gw
        f.append(line(x, oy, x, oy - gh, color='#e2e8f0', sw=1))
        f.append(text(x, oy + 18, '%d°' % deg, 11, MUTED, 'middle'))

    # Горизонтальні лінії сітки (R = 0, 0.2, 0.4, 0.6, 0.8, 1.0)
    for val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y = oy - val * gh
        f.append(line(ox, y, ox + gw, y, color='#e2e8f0', sw=1))
        f.append(text(ox - 8, y + 4, '%.1f' % val, 11, MUTED, 'end'))

    f.append(text(ox + gw / 2, oy + 38, 'Кут падіння θ₁', 12, INK, 'middle', bold=True))
    f.append(text(ox - 45, oy - gh / 2, 'R', 13, INK, 'middle', bold=True))

    n1, n2 = 1.00, 1.50
    theta_b = math.degrees(math.atan(n2 / n1)) # ~56.31°
    xb = ox + (theta_b / 90.0) * gw

    # Обчислення кривих R_s та R_p
    pts_rs = []
    pts_rp = []
    steps = 180
    for i in range(steps + 1):
        deg = (i / float(steps)) * 89.9
        t1 = ang(deg)
        sin_t2 = (n1 / n2) * math.sin(t1)
        t2 = math.asin(sin_t2)

        rs = (n1 * math.cos(t1) - n2 * math.cos(t2)) / (n1 * math.cos(t1) + n2 * math.cos(t2))
        rp = (n2 * math.cos(t1) - n1 * math.cos(t2)) / (n2 * math.cos(t1) + n1 * math.cos(t2))

        Rs = rs * rs
        Rp = rp * rp

        x = ox + (deg / 90.0) * gw
        ys = oy - Rs * gh
        yp = oy - Rp * gh

        pts_rs.append((x, ys))
        pts_rp.append((x, yp))

    pts_rs.append((ox + gw, oy - gh))
    pts_rp.append((ox + gw, oy - gh))

    d_rs = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_rs)
    d_rp = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_rp)

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_rs, POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_rp, NEG))

    # Вертикальна пунктирна лінія для Кута Брюстера
    f.append(line(xb, oy, xb, oy - gh, color=FIELD, sw=1.5, dash='4,3'))
    f.append(circle(xb, oy, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(xb, oy - gh + 20, 'Кут Брюстера θ_B ≈ 56.3°', 11, FIELD, 'middle', bold=True))
    f.append(text(xb + 5, oy - 15, 'Rₚ = 0', 11, FIELD, 'start', bold=True))

    # Позначка нормального падіння (θ=0, R = 4%)
    f.append(circle(ox, oy - 0.04 * gh, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(text(ox + 12, oy - 0.04 * gh + 14, 'R(0°) = 4%', 10, INK, 'start'))

    # Легенда
    f.append(line(570, 100, 600, 100, color=POS, sw=2.5))
    f.append(text(606, 104, 'R⛛ (s-поляризація)', 11, POS, 'start', bold=True))

    f.append(line(570, 126, 600, 126, color=NEG, sw=2.5))
    f.append(text(606, 130, 'Rₚ (p-поляризація)', 11, NEG, 'start', bold=True))

    f.append(fitbox(565, 160, 105, 110,
                    'Параметри:\nмежа повітря-скло\nn₁ = 1.0, n₂ = 1.5\nПри θ_B відбивається\nлише s-хвиля!',
                    size=10, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'fresnel-curves.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Фізичний механізм Кута Брюстера (випромінювання диполів)
# ═══════════════════════════════════════════════════════════════════════════
def fig_brewster_dipoles():
    W, H = 680, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Фізичний механізм кута Брюстера: дипольні коливання', 16, INK, 'middle', bold=True))

    cx, py = 280, 185
    f.append(rect(60, py, 420, H - py - 25, fill=GLASS, stroke='none', sw=0, rx=0))
    f.append(line(60, py, 480, py, color=INK, sw=2))
    f.append(line(cx, py - 110, cx, py + 110, color=MUTED, sw=1.2, dash='5,4'))

    n1, n2 = 1.00, 1.50
    tb = math.atan(n2 / n1) # ~56.3°
    t2 = math.pi / 2 - tb   # θ1 + θ2 = 90°
    L = 120

    # Падаючий промінь (p-поляризований)
    ix = cx - L * math.sin(tb)
    iy = py - L * math.cos(tb)
    f.append(arrow(ix, iy, cx, py, color=POS, sw=2.5))
    f.append(text(ix - 8, iy - 6, 'падаючий p-промінь', 11, POS, 'end', bold=True))

    # Заломлений промінь
    tx = cx + L * math.sin(t2)
    ty = py + L * math.cos(t2)
    f.append(arrow(cx, py, tx, ty, color=FIELD, sw=2.5))
    f.append(text(tx + 8, ty + 12, 'заломлений промінь', 11, FIELD, 'start', bold=True))

    # Напрям відбитого променя
    rx = cx + L * math.sin(tb)
    ry = py - L * math.cos(tb)
    f.append(line(cx, py, rx, ry, color=NEG, sw=1.8, dash='4,4'))
    f.append(text(rx + 8, ry - 6, 'відбитий промінь = 0', 11, NEG, 'start', bold=True))

    # Напрям коливань диполів у другому середовищі
    dx1 = cx - 35 * math.sin(tb)
    dy1 = py + 35 * math.cos(tb)
    dx2 = cx + 35 * math.sin(tb)
    dy2 = py - 35 * math.cos(tb)
    f.append(line(dx1, dy1, dx2, dy2, color=POS, sw=3))
    f.append(circle(cx, py, 6, fill=POS, stroke=INK, sw=1))
    f.append(text(cx - 50, py + 35, 'напрям коливання\nдиполів у склі', 10, POS, 'end', bold=True))

    f.append(text(cx + 35, py + 5, '90°', 13, INK, 'middle', bold=True))
    f.append(text(cx - 24, py - 45, 'θ_B', 12, INK, 'middle', bold=True, italic=True))

    # Пояснювальний блок праворуч
    f.append(fitbox(500, 110, 160, 140,
                    'Чому Rₚ = 0?\nЗаломлена хвиля розгойдує\nелектричні диполі в склі.\nДиполі коливаються ВЗДОВЖ\nлінії потенційного відбитого\nпроменя. Диполь НЕ випромінює\nвздовж осі своїх коливань!',
                    size=10, color=INK, fill='#fdfbf7', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'brewster-dipoles.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Ромб Френеля: перетворення лінійної поляризації в колову
# ═══════════════════════════════════════════════════════════════════════════
def fig_fresnel_rhomb():
    W, H = 680, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Ромб Френеля: зсув фаз при повному внутрішньому відбитті', 16, INK, 'middle', bold=True))

    ax, ay = 100, 200
    bx, by = 250, 100
    cx_p, cy_p = 550, 100
    dx, dy = 400, 200

    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="2"/>' %
             (ax, ay, bx, by, cx_p, cy_p, dx, dy, GLASS, INK))

    # Вхідний промінь
    f.append(arrow(40, 150, 175, 150, color=POS, sw=2.5))
    f.append(text(100, 135, 'лінійно поляризоване (45°)', 10, POS, 'middle', bold=True))

    # Перше повне відбиття
    m1x, m1y = 250, 100
    f.append(line(175, 150, m1x, m1y, color=POS, sw=2.2))

    # Друге повне відбиття
    m2x, m2y = 375, 200
    f.append(line(m1x, m1y, m2x, m2y, color=FIELD, sw=2.2))

    # Вихідний промінь
    f.append(arrow(m2x, m2y, 630, 150, color=NEG, sw=2.5))
    f.append(text(540, 135, 'колово поляризоване світло', 10, NEG, 'middle', bold=True))

    # Точки відбиття
    f.append(circle(m1x, m1y, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(m2x, m2y, 4, fill=FIELD, stroke=INK, sw=1))

    f.append(text(m1x, m1y - 12, '1-ше відбиття (зсув Δδ = 45°)', 10, POS, 'middle', bold=True))
    f.append(text(m2x, m2y + 18, '2-ге відбиття (зсув Δδ = 45°)', 10, FIELD, 'middle', bold=True))

    # Загальний підпис
    f.append(fitbox(200, 240, 280, 55,
                    'Сумарна різниця фаз між s- та p-компонентами:\nΔδ_загальна = 45° + 45° = 90° (перетворення у колову поляризацію)',
                    size=10, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'fresnel-rhomb.svg'), W, H, *f)

if __name__ == '__main__':
    fig_polarization_geometry()
    fig_fresnel_curves()
    fig_brewster_dipoles()
    fig_fresnel_rhomb()
    print("All figures generated successfully!")
