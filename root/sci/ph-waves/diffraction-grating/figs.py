# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрія дифракції на ґратці: різниця ходу та максимуми
# ═══════════════════════════════════════════════════════════════════════════
def fig_grating_diffraction_geometry():
    W, H = 720, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Геометрія дифракції на ґратці: різниця ходу та порядок максимуму', 16, INK, 'middle', bold=True))

    gx = 220  # X координата плоскості ґратки
    py_start = 70
    d_step = 60 # період ґратки d у пікселях
    a_width = 24 # ширина щілини a у пікселях

    # Прозорі та непрозорі ділянки ґратки (3 щелини)
    # Малюємо блок ґратки
    f.append(line(gx, py_start - 20, gx, py_start + 4 * d_step + 10, color=MUTED, sw=1.5, dash='4,4'))
    
    # Непрозорі штрихи (блокатори)
    for i in range(4):
        y_top = py_start + i * d_step
        y_bot = y_top + (d_step - a_width)
        f.append(rect(gx - 4, y_top, 8, d_step - a_width, fill=INK, stroke='none'))

    # Позначення періоду d та ширини щілини a
    y0 = py_start + d_step - a_width
    y1 = py_start + 2 * d_step - a_width
    f.append(line(gx - 25, y0, gx - 25, y1, color=POS, sw=1.5))
    f.append(line(gx - 30, y0, gx - 20, y0, color=POS, sw=1.5))
    f.append(line(gx - 30, y1, gx - 20, y1, color=POS, sw=1.5))
    f.append(text(gx - 38, (y0 + y1) / 2 + 4, 'd', 13, POS, 'end', bold=True, italic=True))

    y_slit1 = py_start + (d_step - a_width)
    y_slit1_end = py_start + d_step
    f.append(line(gx + 18, y_slit1, gx + 18, y_slit1_end, color=FIELD, sw=1.5))
    f.append(line(gx + 13, y_slit1, gx + 23, y_slit1, color=FIELD, sw=1.5))
    f.append(line(gx + 13, y_slit1_end, gx + 23, y_slit1_end, color=FIELD, sw=1.5))
    f.append(text(gx + 28, (y_slit1 + y_slit1_end) / 2 + 4, 'a', 12, FIELD, 'start', bold=True, italic=True))

    # Точки-джерела вторинних хвиль у центрах щілин
    s_y = [py_start + i * d_step + (d_step - a_width) + a_width / 2 for i in range(3)]

    # Падаючі промені (під кутом θ_i)
    theta_i_deg = 20.0
    t_i = math.radians(theta_i_deg)
    L_in = 130
    for y in s_y:
        x_in = gx - L_in * math.cos(t_i)
        y_in = y - L_in * math.sin(t_i)
        f.append(arrow(x_in, y_in, gx, y, color=NEG, sw=2))

    # Дифракційні промені (під кутом θ_m)
    theta_m_deg = 35.0
    t_m = math.radians(theta_m_deg)
    L_out = 240
    for y in s_y:
        x_out = gx + L_out * math.cos(t_m)
        y_out = y + L_out * math.sin(t_m)
        f.append(arrow(gx, y, x_out, y_out, color=POS, sw=2))

    # Відрізок перпендикуляра для різниці ходу ΔL між двома сусідніми променями
    y_A = s_y[0]
    y_B = s_y[1]
    # Перпендикуляр з точки (gx, y_A) до другого променя
    # Напрямок променя (cos t_m, sin t_m), перпендикуляр (-sin t_m, cos t_m)
    dist_perp = d_step * math.sin(t_m)
    px = gx + dist_perp * math.sin(t_m)
    py = y_A + dist_perp * math.cos(t_m)

    f.append(line(gx, y_A, px, py, color=FIELD, sw=2, dash='4,3'))
    f.append(circle(px, py, 3.5, fill=FIELD, stroke=INK, sw=1))
    f.append(line(gx, y_B, px, py, color=POS, sw=2.5)) # Відрізок різниці ходу ΔL

    f.append(text(gx + 45, y_B - 6, 'ΔL = d·sin θₘ', 11, POS, 'start', bold=True))

    # Кут θ_m до нормалі
    f.append(line(gx, s_y[1], gx + 100, s_y[1], color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(gx + 75, s_y[1] + 18, 'θₘ', 12, INK, 'start', bold=True, italic=True))
    f.append(text(gx - 75, s_y[1] - 14, 'θᵢ', 12, INK, 'end', bold=True, italic=True))
    f.append(line(gx - 100, s_y[1], gx, s_y[1], color=MUTED, sw=1.2, dash='5,4'))

    # Позначки порядків дифракції m на екрані праворуч
    ex = gx + L_out * math.cos(t_m) + 15
    f.append(line(ex, 50, ex, H - 40, color=LINE, sw=2))
    f.append(text(ex + 10, 65, 'Екран', 11, INK, 'start', bold=True))

    # Порядочки: m=0, m=+1, m=-1, m=+2
    y_m0 = s_y[1] + (L_out + 15) * math.sin(t_i)
    y_m1 = s_y[1] + (L_out + 15) * math.sin(t_m)
    y_m_minus1 = s_y[1] - (L_out + 15) * math.sin(math.radians(10.0))

    f.append(circle(ex, y_m0, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(ex + 10, y_m0 + 4, 'm = 0 (прямий промінь)', 10, INK, 'start'))

    f.append(circle(ex, y_m1, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(ex + 10, y_m1 + 4, 'm = +1 (перший порядок)', 10, POS, 'start', bold=True))

    f.append(circle(ex, y_m_minus1, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(ex + 10, y_m_minus1 + 4, 'm = -1 (відвідний порядок)', 10, NEG, 'start'))

    # Пояснювальний блок знизу
    f.append(fitbox(40, H - 75, 480, 55,
                    'Рівняння дифракційної ґратки:\nd · (sin θₘ ± sin θᵢ) = m · λ\nКонструктивна інтерференція виникає, коли різниця ходу ΔL дорівнює цілому числу довжин хвиль mλ.',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'grating-diffraction-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Розподіл інтенсивності світла: максимуми та обвідна
# ═══════════════════════════════════════════════════════════════════════════
def fig_grating_intensity_distribution():
    W, H = 720, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Розподіл інтенсивності: головні максимуми та дифракційна обвідна', 16, INK, 'middle', bold=True))

    ox, oy = 70, 320
    gw, gh = 520, 240

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill='#fafbfc', stroke=MUTED, sw=1))

    # Головні позначки фазової різниці γ = π d sin(θ) / λ
    # Позначки gamma = -3π, -2π, -π, 0, π, 2π, 3π
    gammas = [(-3, '-3π'), (-2, '-2π'), (-1, '-π'), (0, '0'), (1, 'π'), (2, '2π'), (3, '3π')]
    for val, label in gammas:
        x = ox + gw / 2 + (val / 3.5) * (gw / 2)
        f.append(line(x, oy, x, oy - gh, color='#e2e8f0', sw=1))
        f.append(text(x, oy + 18, label, 11, MUTED, 'middle'))

    f.append(text(ox + gw / 2, oy + 38, 'Різниця фаз γ = (π·d·sin θ) / λ', 12, INK, 'middle', bold=True))
    f.append(text(ox - 45, oy - gh / 2, 'I(θ) / I₀', 12, INK, 'middle', bold=True))

    # Побудова графіка для N=6 щілин та d/a = 3 (m=3 зникає)
    N = 6
    d_over_a = 3.0

    pts_intensity = []
    pts_envelope = []
    steps = 400
    for i in range(steps + 1):
        # gamma від -3.5*pi до +3.5*pi
        g = -3.5 * math.pi + (i / float(steps)) * (7.0 * math.pi)
        beta = g / d_over_a

        # Дифракційна обвідна однощілинна (sin beta / beta)^2
        if abs(beta) < 1e-6:
            env = 1.0
        else:
            env = (math.sin(beta) / beta) ** 2

        # Багатопроменева інтерференція (sin N g / sin g)^2 / N^2
        if abs(math.sin(g)) < 1e-5:
            interf = 1.0
        else:
            interf = (math.sin(N * g) / (N * math.sin(g))) ** 2

        I_total = env * interf

        x = ox + gw / 2 + (g / (3.5 * math.pi)) * (gw / 2)
        y_int = oy - I_total * (gh - 20)
        y_env = oy - env * (gh - 20)

        pts_intensity.append((x, y_int))
        pts_envelope.append((x, y_env))

    d_int = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_intensity)
    d_env = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_envelope)

    # Малюємо обвідну (пунктиром)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' % (d_env, NEG))
    # Малюємо інтенсивність ґратки
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_int, POS))

    # Позначки зниклого максимуму при m = ±3 (оскільки d/a = 3)
    x_m3_pos = ox + gw / 2 + (3.0 / 3.5) * (gw / 2)
    x_m3_neg = ox + gw / 2 + (-3.0 / 3.5) * (gw / 2)

    f.append(circle(x_m3_pos, oy, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(circle(x_m3_neg, oy, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(text(x_m3_pos, oy + 22, 'm = 3 (зникає)', 10, FIELD, 'middle', bold=True))
    f.append(text(x_m3_neg, oy + 22, 'm = -3 (зникає)', 10, FIELD, 'middle', bold=True))

    # Позначки порядків m=0, m=1, m=2 (над піками)
    x_m0 = ox + gw / 2
    x_m1 = ox + gw / 2 + (1.0 / 3.5) * (gw / 2)
    x_m2 = ox + gw / 2 + (2.0 / 3.5) * (gw / 2)

    f.append(text(x_m0, oy - gh - 8, 'm = 0', 11, INK, 'middle', bold=True))
    f.append(text(x_m1, oy - 0.7 * gh - 16, 'm = 1', 11, POS, 'middle', bold=True))
    f.append(text(x_m2, oy - 0.28 * gh - 16, 'm = 2', 11, POS, 'middle', bold=True))

    # Легенда праворуч згори
    f.append(line(580, 50, 610, 50, color=POS, sw=2.2))
    f.append(text(616, 54, 'I(θ) ґратки (N=6)', 10, POS, 'start', bold=True))

    f.append(line(580, 70, 610, 70, color=NEG, sw=2, dash='5,4'))
    f.append(text(616, 74, 'Обвідна (sin β / β)²', 10, NEG, 'start', bold=True))

    f.append(fitbox(565, 95, 145, 125,
                    'Властивості:\n• Головні максимуми вузькі\n  (ширина δγ ~ 2π/N)\n• Висота максимумів ~ N²\n• Зникнення максимуму:\n  якщо d/a = 3, то m = 3\n  потрапляє в мінімум',
                    size=9.5, color=INK, fill='#fdfbf7', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'grating-intensity-distribution.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Профільована ґратка Блейза (Blazed Grating)
# ═══════════════════════════════════════════════════════════════════════════
def fig_blazed_grating_geometry():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Профільована ґратка Блейза: дзеркальна концентріція світла в порядок m = +1', 15, INK, 'middle', bold=True))

    bx, by = 60, 240
    step_w = 110
    step_h = 45 # вис пилоподібного зуба

    # Малюємо пилоподібний профіль ґратки Блейза (4 штрихи)
    pts = ["%.1f %.1f" % (bx, by)]
    for i in range(4):
        x0 = bx + i * step_w
        x1 = x0 + step_w * 0.8
        x2 = x0 + step_w
        pts.append("%.1f %.1f" % (x1, by - step_h))
        pts.append("%.1f %.1f" % (x2, by))
    pts.append("%.1f %.1f" % (bx + 4 * step_w, by + 40))
    pts.append("%.1f %.1f" % (bx, by + 40))

    d_poly = "M " + " L ".join(pts) + " Z"
    f.append('<path d="%s" fill="#e2e8f0" stroke="%s" stroke-width="2"/>' % (d_poly, INK))

    # Робоча грань одного зуба (другий зуб)
    tooth2_x0 = bx + step_w
    tooth2_x1 = tooth2_x0 + step_w * 0.8
    tooth2_y1 = by - step_h

    # Кут Блейза θ_b
    f.append(line(tooth2_x0, by, tooth2_x0 + step_w, by, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(tooth2_x0 + 40, by + 16, 'Кут Блейза θ_b', 11, POS, 'start', bold=True, italic=True))

    # Нормаль до робочої грані
    mid_x = (tooth2_x0 + tooth2_x1) / 2
    mid_y = (by + tooth2_y1) / 2
    dx = tooth2_x1 - tooth2_x0
    dy = tooth2_y1 - by
    facet_angle = math.atan2(dy, dx)
    norm_angle = facet_angle - math.pi / 2

    nx = mid_x + 80 * math.cos(norm_angle)
    ny = mid_y + 80 * math.sin(norm_angle)
    f.append(line(mid_x, mid_y, nx, ny, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(nx + 6, ny - 6, 'нормаль до грані', 10, MUTED, 'start'))

    # Падаючий промінь перпендикулярно до основної площини
    in_len = 110
    f.append(arrow(mid_x, mid_y - in_len, mid_x, mid_y, color=NEG, sw=2.5))
    f.append(text(mid_x, mid_y - in_len - 10, 'падаюче світло', 11, NEG, 'middle', bold=True))

    # Дзеркально відбитий промінь від грані під кутом 2 θ_b (напрямок максимуму m = +1)
    spec_angle = norm_angle + (norm_angle - (-math.pi / 2))
    rx = mid_x + 130 * math.cos(spec_angle)
    ry = mid_y + 130 * math.sin(spec_angle)
    f.append(arrow(mid_x, mid_y, rx, ry, color=POS, sw=2.8))
    f.append(text(rx - 10, ry - 10, 'дзеркальне відбиття = порядок m = +1', 11, POS, 'end', bold=True))

    # Охоплення довжин хвилин (λ_b = 2 d sin θ_b)
    f.append(circle(mid_x, mid_y, 4, fill=POS, stroke=INK, sw=1))

    # Пояснювальний блок праворуч
    f.append(fitbox(530, 70, 180, 160,
                    'Принцип Блейза:\n• Грані нахилені під кутом θ_b\n• Дзеркальне відбиття\n  напрямлене в порядок m = +1\n• ККД досягає 80–90%\n  на довжині хвилі Блейза:\n  λ_b = 2 · d · sin θ_b',
                    size=9.5, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'blazed-grating-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Схема спектрометра Черні — Тернера
# ═══════════════════════════════════════════════════════════════════════════
def fig_grating_spectrometer_setup():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптична схема монохроматора / спектрометра (Черні — Тернера)', 16, INK, 'middle', bold=True))

    # Вхідна щілина (Entrance Slit)
    sx, sy = 70, 200
    f.append(rect(sx - 4, sy - 40, 8, 30, fill=INK, stroke='none'))
    f.append(rect(sx - 4, sy + 10, 8, 30, fill=INK, stroke='none'))
    f.append(text(sx, sy - 48, 'вхідна щілина', 10, INK, 'middle', bold=True))

    # Біле світло від джерела
    f.append(arrow(20, sy, sx, sy, color=MUTED, sw=2))
    f.append(text(25, sy - 10, 'біле світло', 10, MUTED, 'start'))

    # Коліматорне дзеркало M1 (увігнуте)
    m1x, m1y = 240, 310
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="4"/>' %
             (m1x - 30, m1y - 20, m1x, m1y, m1x + 30, m1y + 15, INK))
    f.append(text(m1x, m1y + 28, 'коліматорне дзеркало М₁', 10, INK, 'middle', bold=True))

    # Промінь від вхідної щілини до М1
    f.append(line(sx, sy, m1x, m1y, color='#f39c12', sw=1.8))

    # Колімований пучок від М1 до дифракційної ґратки
    gx, gy = 380, 140
    f.append(line(m1x, m1y, gx, gy, color='#f39c12', sw=2))

    # Дифракційна ґратка (Reflective Grating)
    f.append(rect(gx - 25, gy - 15, 50, 30, fill='#cbd5e1', stroke=INK, sw=2, rx=2))
    # Штрихи на ґратці
    for i in range(-15, 18, 5):
        f.append(line(gx + i, gy - 12, gx + i, gy + 12, color=INK, sw=1))
    f.append(text(gx, gy - 24, 'дифракційна ґратка', 11, INK, 'middle', bold=True))

    # Фокусуюче дзеркало M2
    m2x, m2y = 560, 310
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="4"/>' %
             (m2x - 30, m2y + 15, m2x, m2y, m2x + 30, m2y - 20, INK))
    f.append(text(m2x, m2y + 28, 'фокусуюче дзеркало М₂', 10, INK, 'middle', bold=True))

    # Дисперговані промені від ґратки до М2 (Червоний, Зелений, Синій)
    f.append(line(gx, gy, m2x - 10, m2y, color='#e74c3c', sw=2)) # Червоний (найбільший кут)
    f.append(line(gx, gy, m2x, m2y, color='#2ecc71', sw=2))     # Зелений
    f.append(line(gx, gy, m2x + 10, m2y, color='#3498db', sw=2)) # Синій (найменший кут)

    # Детекторний масив / ПЗЗ-лінійка (CCD / CMOS sensor)
    det_x, det_y = 660, 170
    f.append(rect(det_x - 15, det_y - 45, 30, 90, fill='#1e293b', stroke=INK, sw=1.5, rx=3))
    f.append(text(det_x + 22, det_y - 20, 'ПЗЗ / CMOS\nдетектор', 10, INK, 'start', bold=True))

    # Сфокусовані промені від М2 на детектор
    f.append(line(m2x - 10, m2y, det_x - 15, det_y + 30, color='#e74c3c', sw=2))
    f.append(line(m2x, m2y, det_x - 15, det_y, color='#2ecc71', sw=2))
    f.append(line(m2x + 10, m2y, det_x - 15, det_y - 30, color='#3498db', sw=2))

    # Кольорові точки спектра на лінійці
    f.append(circle(det_x - 15, det_y + 30, 4, fill='#e74c3c', stroke='none'))
    f.append(circle(det_x - 15, det_y, 4, fill='#2ecc71', stroke='none'))
    f.append(circle(det_x - 15, det_y - 30, 4, fill='#3498db', stroke='none'))

    # Текстова інформація
    f.append(fitbox(200, 60, 150, 60,
                    'Черні — Тернера:\n1. Колімація променя\n2. Дисперсія на ґратці\n3. Фокусування на матрицю',
                    size=9.5, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'grating-spectrometer-setup.svg'), W, H, *f)

if __name__ == '__main__':
    fig_grating_diffraction_geometry()
    fig_grating_intensity_distribution()
    fig_blazed_grating_geometry()
    fig_grating_spectrometer_setup()
    print("All diffraction grating figures generated successfully!")
