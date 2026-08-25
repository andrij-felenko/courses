# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path(d, fill='none', stroke=LINE, sw=1.5, dash=None, fill_opacity=None):
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity is not None else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{fo}{da}/>'

def circle_ext(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5, dash=None, fill_opacity=None):
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity is not None else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{fo}{da}/>'


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрична побудова хвильового фронту Гюйгенса
# ═══════════════════════════════════════════════════════════════════════════
def fig_wavefront_construction():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, 'Геометрична побудова хвильового фронту за принципом Гюйгенса', 15, INK, 'middle', bold=True))

    # Первинна поверхня хвильового фронту S1 (дуга хвильового фронту)
    cx, cy = 120, 180
    r1 = 160
    f.append(path('M %f %f A %f %f 0 0 1 %f %f' % (cx + r1 * math.cos(-0.6), cy + r1 * math.sin(-0.6),
                                                  r1, r1,
                                                  cx + r1 * math.cos(0.6), cy + r1 * math.sin(0.6)),
                  fill='none', stroke=NEG, sw=2.5))
    f.append(text(cx + r1 * math.cos(-0.62), cy + r1 * math.sin(-0.62) - 8, 'S₁ (t)', 12, NEG, 'middle', bold=True))

    # Точки-джерела вторинних хвиль на S1
    angles = [-0.45, -0.22, 0.0, 0.22, 0.45]
    dr = 90  # r = v * dt
    r2 = r1 + dr

    for idx, a in enumerate(angles):
        px = cx + r1 * math.cos(a)
        py = cy + r1 * math.sin(a)
        # Точка-джерело
        f.append(circle(px, py, 4, fill=POS, stroke=INK, sw=1))
        f.append(text(px - 14, py - 4, 'P%d' % (idx + 1), 10, POS, 'end', bold=True))

        # Вторинна сферична хвиля (кола/дуги навколо точок P)
        f.append(circle_ext(px, py, dr, fill='#fee2e2', fill_opacity=0.25, stroke=POS, sw=1.2, dash='4,3'))

        # Промінь нормалі
        nx = cx + r2 * math.cos(a)
        ny = cy + r2 * math.sin(a)
        f.append(line(px, py, nx, ny, color=MUTED, sw=1, dash='2,2'))

    # Новий хвильовий фронт S2 (огинаюча поверхня)
    f.append(path('M %f %f A %f %f 0 0 1 %f %f' % (cx + r2 * math.cos(-0.6), cy + r2 * math.sin(-0.6),
                                                  r2, r2,
                                                  cx + r2 * math.cos(0.6), cy + r2 * math.sin(0.6)),
                  fill='none', stroke=FIELD, sw=3))
    f.append(text(cx + r2 * math.cos(-0.62), cy + r2 * math.sin(-0.62) - 8, 'S₂ (t + Δt)', 12, FIELD, 'middle', bold=True))

    # Вектор поширення променя (центральний промінь)
    f.append(line(cx + r1, cy, cx + r2 + 40, cy, color=INK, sw=2))
    f.append(path('M %f %f L %f %f L %f %f Z' % (cx + r2 + 40, cy, cx + r2 + 30, cy - 5, cx + r2 + 30, cy + 5), fill=INK, stroke='none', sw=0))
    f.append(text(cx + r2 + 45, cy + 4, 'Оптичний промінь (нормаль k)', 11, INK, 'start', bold=True))

    # Позначка радіуса вторинної хвилі r = v * dt
    p0_x = cx + r1 * math.cos(0.22)
    p0_y = cy + r1 * math.sin(0.22)
    f.append(line(p0_x, p0_y, p0_x + dr * math.cos(0.45), p0_y + dr * math.sin(0.45), color=POS, sw=1.5))
    f.append(text(p0_x + dr * 0.55, p0_y + dr * 0.45 + 14, 'r = v · Δt', 11, POS, 'middle', bold=True, italic=True))

    # Інформаційна картка
    f.append(fitbox(470, 230, 230, 100,
                    'Принцип побудови огинаючої:\n'
                    '1. Кожна точка фронту S₁ випромінює вторинну сферичну хвилю.\n'
                    '2. Радіус вторинних хвиль r = v · Δt = (c / n) · Δt.\n'
                    '3. Огинаюча поверхня S₂ утворює новий фронт у момент t + Δt.',
                    size=10, color=INK, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'huygens-principle-wavefront.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Виведення законів відбиття та заломлення світла за Гюйгенсом
# ═══════════════════════════════════════════════════════════════════════════
def fig_reflection_refraction():
    W, H = 720, 390
    f = []
    f.append(text(W / 2, 26, 'Виведення закону заломлення Снелліуса за принципом Гюйгенса', 15, INK, 'middle', bold=True))

    # Межа двох середовищ y = 200
    my = 200
    f.append(rect(0, 40, W, my - 40, fill='#f8fafc', stroke='none', sw=0, rx=0))
    f.append(rect(0, my, W, H - my - 10, fill='#eff6ff', stroke='none', sw=0, rx=0))
    f.append(line(40, my, W - 40, my, color=INK, sw=2.5))
    f.append(text(60, my - 12, 'Середовище 1 (n₁, швидкість v₁)', 11, NEG, 'start', bold=True))
    f.append(text(60, my + 20, 'Середовище 2 (n₂, швидкість v₂, n₂ > n₁)', 11, FIELD, 'start', bold=True))

    # Точки на межі A та C
    ax, ay = 240, my
    cx, cy = 460, my
    ac_len = cx - ax  # 220 px

    # Падаючий плоский фронт AB під кутом theta1 = 40 deg
    theta1 = math.radians(40)
    bc_len = ac_len * math.sin(theta1)
    bx = cx - bc_len * math.sin(theta1)
    by = cy - bc_len * math.cos(theta1)

    # Падаючий фронт AB
    f.append(line(ax, ay, bx, by, color=NEG, sw=2.5))
    f.append(text((ax + bx)/2 - 16, (ay + by)/2 - 8, 'A B (t = 0)', 11, NEG, 'end', bold=True))

    # Промені 1 та 2
    f.append(line(ax - 90 * math.sin(theta1), ay - 90 * math.cos(theta1), ax, ay, color=NEG, sw=1.8))
    f.append(line(bx - 40 * math.sin(theta1), by - 40 * math.cos(theta1), cx, cy, color=NEG, sw=1.8))
    f.append(text(ax - 50 * math.sin(theta1) - 12, ay - 50 * math.cos(theta1), 'Промінь 1', 10, NEG, 'end'))
    f.append(text(bx - 20 * math.sin(theta1) + 12, by - 20 * math.cos(theta1), 'Промінь 2', 10, NEG, 'end'))

    # Лінія BC (прохід променя 2 до межі за час dt)
    f.append(line(bx, by, cx, cy, color=POS, sw=2, dash='5,3'))
    f.append(text((bx + cx)/2 + 10, (by + cy)/2 - 8, 'v₁ · Δt', 11, POS, 'start', bold=True, italic=True))

    # Вторинна сферична хвиля від точки A у другому середовищі
    n1, n2 = 1.0, 1.5
    ad_len = bc_len * (n1 / n2)
    theta2 = math.asin(ad_len / ac_len)

    # Точка D дотику заломленого фронту CD
    dx = ax + ad_len * math.sin(theta2)
    dy = ay + ad_len * math.cos(theta2)

    # Півколо вторинної хвилі від A
    f.append(path('M %f %f A %f %f 0 0 0 %f %f' % (ax + ad_len, ay, ad_len, ad_len, ax - ad_len, ay),
                  fill='#dbeafe', fill_opacity=0.35, stroke=POS, sw=1.5, dash='4,3'))
    f.append(circle(ax, ay, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(ax - 12, ay - 8, 'A', 12, INK, 'end', bold=True))
    f.append(text(cx + 10, cy - 8, 'C', 12, INK, 'start', bold=True))

    # Заломлений фронт CD
    f.append(line(cx, cy, dx, dy, color=FIELD, sw=3))
    f.append(circle(dx, dy, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(text(dx - 12, dy + 14, 'D', 12, FIELD, 'end', bold=True))
    f.append(text((cx + dx)/2 + 14, (cy + dy)/2 + 10, 'CD (t = Δt)', 11, FIELD, 'start', bold=True))

    # Відрізок AD
    f.append(line(ax, ay, dx, dy, color=POS, sw=2, dash='5,3'))
    f.append(text((ax + dx)/2 - 14, (ay + dy)/2 + 12, 'v₂ · Δt', 11, POS, 'end', bold=True, italic=True))

    # Заломлений промінь з точки A через D далі
    f.append(line(ax, ay, ax + 140 * math.sin(theta2), ay + 140 * math.cos(theta2), color=FIELD, sw=1.8))
    f.append(text(ax + 100 * math.sin(theta2) + 12, ay + 100 * math.cos(theta2), 'Заломлений промінь', 10, FIELD, 'start'))

    # Нормалі до межі в точках A та C
    f.append(line(ax, ay - 70, ax, ay + 100, color=MUTED, sw=1, dash='3,3'))
    f.append(line(cx, cy - 70, cx, cy + 70, color=MUTED, sw=1, dash='3,3'))

    # Кути theta1 та theta2
    f.append(text(ax - 18, ay - 40, 'θ₁', 11, INK, 'middle', bold=True, italic=True))
    f.append(text(ax + 18, ay + 45, 'θ₂', 11, FIELD, 'middle', bold=True, italic=True))

    # Формульний бокс
    f.append(fitbox(480, 290, 215, 80,
                    'Співвідношення Снелліуса:\n'
                    'sin θ₁ = v₁ · Δt / AC\n'
                    'sin θ₂ = v₂ · Δt / AC\n'
                    '⇒ sin θ₁ / sin θ₂ = v₁ / v₂ = n₂ / n₁',
                    size=10, color=INK, fill=BG, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'huygens-reflection-refraction.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Дифракційне огинання перешкод (широка vs вузька щілина)
# ═══════════════════════════════════════════════════════════════════════════
def fig_diffraction_slit():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, 'Поведінка хвильового фронту під час проходження через отвір', 15, INK, 'middle', bold=True))

    # Ліва панель: Широка щілина a >> lambda
    f.append(rect(20, 45, 330, 295, fill='#f8fafc', stroke='#e2e8f0', sw=1, rx=4))
    f.append(text(185, 66, 'А: Широка щілина (a ≫ λ)', 13, INK, 'middle', bold=True))

    # Падаючі плоскі фронти
    for x in [50, 80, 110]:
        f.append(line(x, 90, x, 290, color=NEG, sw=2))
    f.append(text(65, 310, 'Падаюча хвиля', 10, NEG, 'middle'))

    # Екран з щілиною
    sx1 = 140
    f.append(rect(sx1 - 2, 80, 6, 75, fill=INK, stroke='none', sw=0, rx=0))
    f.append(rect(sx1 - 2, 225, 6, 75, fill=INK, stroke='none', sw=0, rx=0))
    f.append(text(sx1, 74, 'Ширма', 10, INK, 'middle'))
    f.append(line(sx1 - 10, 155, sx1 - 10, 225, color=POS, sw=1.2))
    f.append(text(sx1 - 18, 190, 'a', 11, POS, 'end', bold=True, italic=True))

    # Переходження фронту через широку щілину
    for dx, r_edge in [(30, 25), (60, 50), (90, 75), (120, 100)]:
        fx = sx1 + dx
        f.append(line(fx, 165, fx, 215, color=FIELD, sw=2))
        f.append(path('M %f %f Q %f %f %f %f' % (fx, 165, fx - r_edge*0.3, 165 - r_edge*0.6, fx - r_edge*0.6, 165 - r_edge*0.8), fill='none', stroke=FIELD, sw=1.5, dash='3,2'))
        f.append(path('M %f %f Q %f %f %f %f' % (fx, 215, fx - r_edge*0.3, 215 + r_edge*0.6, fx - r_edge*0.6, 215 + r_edge*0.8), fill='none', stroke=FIELD, sw=1.5, dash='3,2'))

    f.append(text(250, 310, 'Збереження плоского фронту в центрі', 10, FIELD, 'middle'))

    # Права панель: Вузька щілина a ≈ lambda
    f.append(rect(370, 45, 330, 295, fill='#f8fafc', stroke='#e2e8f0', sw=1, rx=4))
    f.append(text(535, 66, 'Б: Вузька щілина (a ≈ λ)', 13, INK, 'middle', bold=True))

    # Падаючі плоскі фронти
    for x in [400, 430, 460]:
        f.append(line(x, 90, x, 290, color=NEG, sw=2))

    # Екран з вузькою щілиною
    sx2 = 490
    f.append(rect(sx2 - 2, 80, 6, 95, fill=INK, stroke='none', sw=0, rx=0))
    f.append(rect(sx2 - 2, 205, 6, 95, fill=INK, stroke='none', sw=0, rx=0))
    f.append(text(sx2, 74, 'Ширма', 10, INK, 'middle'))

    # Точкове джерело в щілині
    f.append(circle(sx2, 190, 4, fill=POS, stroke=INK, sw=1))

    # Сферичні вторинні хвилі після вузької щілини
    for r in [30, 60, 90, 120, 150]:
        f.append(path('M %f %f A %f %f 0 0 1 %f %f' % (sx2 + r * math.cos(-1.1), 190 + r * math.sin(-1.1),
                                                      r, r,
                                                      sx2 + r * math.cos(1.1), 190 + r * math.sin(1.1)),
                      fill='none', stroke=FIELD, sw=2))

    # Тіньові області
    f.append(text(610, 105, 'Зона тіні', 10, MUTED, 'middle', italic=True))
    f.append(text(610, 275, 'Зона тіні', 10, MUTED, 'middle', italic=True))
    f.append(text(600, 310, 'Сферичне розсіювання хвилі', 10, FIELD, 'middle', bold=True))

    render(os.path.join(IMG, 'huygens-diffraction-slit.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Фактор спрямованості Кірхгофа K(theta)
# ═══════════════════════════════════════════════════════════════════════════
def fig_obliquity_factor():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, 'Діаграма спрямованості вторинного випромінювача за Френелем — Кірхгофом', 15, INK, 'middle', bold=True))

    # Центр джерела dS
    ox, oy = 260, 190
    f.append(circle(ox, oy, 5, fill=POS, stroke=INK, sw=1))
    f.append(text(ox - 16, oy + 16, 'dS', 12, POS, 'middle', bold=True))

    # Напрямок нормалі n (прямий напрямок theta = 0)
    f.append(line(ox - 140, oy, ox + 220, oy, color=MUTED, sw=1.2, dash='4,4'))
    f.append(line(ox, oy - 140, ox, oy + 140, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(ox + 230, oy + 4, 'n (θ = 0)', 11, INK, 'start', bold=True))
    f.append(text(ox - 150, oy + 4, 'θ = π (назад)', 11, MUTED, 'end'))
    f.append(text(ox, oy - 148, 'θ = π/2', 10, MUTED, 'middle'))
    f.append(text(ox, oy + 158, 'θ = 3π/2', 10, MUTED, 'middle'))

    # Побудова полярного графіка K(theta) = 0.5 * (1 + cos(theta))
    rmax = 180
    pts = []
    for deg in range(0, 361, 5):
        rad = math.radians(deg)
        k_val = 0.5 * (1.0 + math.cos(rad))
        r = rmax * k_val
        px = ox + r * math.cos(rad)
        py = oy - r * math.sin(rad)
        pts.append((px, py))

    path_str = 'M %f %f ' % pts[0] + ' '.join(['L %f %f' % p for p in pts[1:]]) + ' Z'
    f.append(path(path_str, fill='#fef2f2', fill_opacity=0.5, stroke=POS, sw=2.5))

    # Позначки точок для theta = 0, pi/2, pi
    f.append(circle(ox + rmax, oy, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(ox + rmax + 10, oy - 10, 'K(0) = 1.0', 11, POS, 'start', bold=True))

    f.append(circle(ox, oy - rmax * 0.5, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(ox + 12, oy - rmax * 0.5, 'K(π/2) = 0.5', 10, POS, 'start', bold=True))

    f.append(text(ox - 24, oy - 10, 'K(π) = 0', 11, INK, 'end', bold=True))

    # Напрямок спостереження під кутом theta
    angle_obs = math.radians(40)
    r_obs = rmax * 0.5 * (1.0 + math.cos(angle_obs))
    px_obs = ox + r_obs * math.cos(angle_obs)
    py_obs = oy - r_obs * math.sin(angle_obs)
    f.append(line(ox, oy, ox + (rmax + 20) * math.cos(angle_obs), oy - (rmax + 20) * math.sin(angle_obs), color=FIELD, sw=2))
    f.append(circle(px_obs, py_obs, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(text(ox + (rmax + 25) * math.cos(angle_obs), oy - (rmax + 25) * math.sin(angle_obs), 'Вектор k (θ)', 11, FIELD, 'start', bold=True))

    # Кутова дуга theta
    f.append(path('M %f %f A 50 50 0 0 0 %f %f' % (ox + 50, oy, ox + 50 * math.cos(angle_obs), oy - 50 * math.sin(angle_obs)),
                  fill='none', stroke=INK, sw=1.5))
    f.append(text(ox + 60, oy - 16, 'θ', 12, INK, 'middle', bold=True, italic=True))

    # Інформаційна картка з формулою
    f.append(fitbox(480, 230, 220, 95,
                    'Фактор спрямованості Кірхгофа:\n'
                    'K(θ) = ½ · (1 + cos θ)\n\n'
                    '• При θ = 0 (вперед): K = 1 (максимум)\n'
                    '• При θ = π/2 (вбік): K = 0.5\n'
                    '• При θ = π (назад): K = 0 (відсутність зворотної хвилі)',
                    size=10, color=INK, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'huygens-fresnel-obliquity.svg'), W, H, *f)


if __name__ == '__main__':
    fig_wavefront_construction()
    fig_reflection_refraction()
    fig_diffraction_slit()
    fig_obliquity_factor()
    print("Всі фігури успішно згенеровано у теці img/")
