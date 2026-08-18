# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS_FILL = "#e8f1f9"
FILM_FILL  = "#fff9e6"
AIR_FILL   = "#ffffff"
ACCENT     = "#e67e22"

def rad(deg):
    return math.radians(deg)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрія падіння та відбиття променів у тонкій плівці
# ═══════════════════════════════════════════════════════════════════════════
def fig_film_reflection_geometry():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Геометрія поширення променів та оптична різниця ходу в тонкій плівці', 15, INK, 'middle', bold=True))

    y1 = 150 # верхня межа плівки
    y2 = 270 # нижня межа плівки
    d_val = y2 - y1

    # Заповнення середовищ
    f.append(rect(40, 45, 640, y1 - 45, fill=AIR_FILL, stroke='none', sw=0, rx=0))
    f.append(rect(40, y1, 640, d_val, fill=FILM_FILL, stroke='none', sw=0, rx=0))
    f.append(rect(40, y2, 640, H - y2 - 60, fill=GLASS_FILL, stroke='none', sw=0, rx=0))

    # Межі розділу
    f.append(line(40, y1, 680, y1, color=INK, sw=2))
    f.append(line(40, y2, 680, y2, color=INK, sw=2))

    # Підписи середовищ
    f.append(text(60, y1 - 15, 'Середовище 1: n₁ (повітря)', 12, MUTED, 'start', bold=True))
    f.append(text(60, y1 + 25, 'Середовище 2: n₂ (плівка, товщина d)', 12, ACCENT, 'start', bold=True))
    f.append(text(60, y2 + 25, 'Середовище 3: n₃ (підкладка)', 12, MUTED, 'start', bold=True))

    # Точки заломлення
    cx1 = 280 # перша точка падіння на верхній межі (A)
    theta1 = 40.0
    t1 = rad(theta1)
    n1, n2 = 1.0, 1.45
    t2 = math.asin((n1 / n2) * math.sin(t1))
    theta2 = math.degrees(t2)

    # Нормаль у точці A
    f.append(line(cx1, y1 - 60, cx1, y2 + 30, color=MUTED, sw=1.2, dash='4,4'))
    f.append(text(cx1 - 8, y1 - 50, 'нормаль', 10, MUTED, 'end'))

    # Падаючий промінь (1)
    L1 = 90
    ix = cx1 - L1 * math.sin(t1)
    iy = y1 - L1 * math.cos(t1)
    f.append(arrow(ix, iy, cx1, y1, color=POS, sw=2.5))
    f.append(text(ix - 10, iy - 6, 'падаючий промінь 1', 11, POS, 'end', bold=True))

    # Перший відбитий промінь (1') від верхньої межі
    rx1 = cx1 + L1 * math.sin(t1)
    ry1 = y1 - L1 * math.cos(t1)
    f.append(arrow(cx1, y1, rx1, ry1, color=NEG, sw=2.2))
    f.append(text(rx1 + 10, ry1 - 10, 'відбитий промінь 1\' (здвиг фази π)', 11, NEG, 'start', bold=True))

    # Заломлений промінь всередині плівки від A до B на нижній межі
    dx_film = d_val * math.tan(t2)
    cx2 = cx1 + dx_film # точка B на нижній межі
    f.append(line(cx1, y1, cx2, y2, color=FIELD, sw=2.2))

    # Нормаль у точці B
    f.append(line(cx2, y1 + 20, cx2, y2 + 40, color=MUTED, sw=1.0, dash='4,4'))

    # Відбитий промінь всередині плівки від B до C на верхній межі
    cx3 = cx2 + dx_film # точка C на верхній межі
    f.append(line(cx2, y2, cx3, y1, color=FIELD, sw=2.2))

    # Нормаль у точці C
    f.append(line(cx3, y1 - 60, cx3, y2 + 20, color=MUTED, sw=1.0, dash='4,4'))

    # Другий відбитий промінь (2') виходить із точки C у перше середовище
    rx2 = cx3 + L1 * math.sin(t1)
    ry2 = y1 - L1 * math.cos(t1)
    f.append(arrow(cx3, y1, rx2, ry2, color=FIELD, sw=2.5))
    f.append(text(rx2 + 10, ry2 + 15, 'відбитий промінь 2\' (після проходу плівки)', 11, FIELD, 'start', bold=True))

    # Позначки точок A, B, C
    f.append(circle(cx1, y1, 3.5, fill=INK, stroke='none'))
    f.append(text(cx1 - 12, y1 - 10, 'A', 12, INK, 'end', bold=True))

    f.append(circle(cx2, y2, 3.5, fill=INK, stroke='none'))
    f.append(text(cx2, y2 + 16, 'B', 12, INK, 'middle', bold=True))

    f.append(circle(cx3, y1, 3.5, fill=INK, stroke='none'))
    f.append(text(cx3 + 10, y1 + 16, 'C', 12, INK, 'start', bold=True))

    # Позначення товщини d зліва
    f.append(line(130, y1, 130, y2, color=ACCENT, sw=1.5))
    f.append(arrow(130, y1 + 30, 130, y1, color=ACCENT, sw=1.5))
    f.append(arrow(130, y2 - 30, 130, y2, color=ACCENT, sw=1.5))
    f.append(text(145, (y1 + y2) / 2 + 5, 'd', 13, ACCENT, 'start', bold=True))

    # Кути θ1 та θ2
    f.append(text(cx1 - 18, y1 - 30, 'θ₁', 12, INK, 'middle', italic=True))
    f.append(text(cx1 + 12, y1 + 30, 'θ₂', 12, INK, 'middle', italic=True))

    # Перпендикуляр із точки A на хвильовий фронт променя 2' (точка D)
    dx_AC = cx3 - cx1
    dxD = dx_AC * math.cos(t1)**2
    dyD = -dx_AC * math.sin(t1) * math.cos(t1)
    xD = cx1 + dxD
    yD = y1 + dyD
    f.append(line(cx1, y1, xD, yD, color=NEG, sw=1.5, dash='3,3'))
    f.append(circle(xD, yD, 3, fill=NEG, stroke='none'))
    f.append(text(xD - 10, yD - 8, 'D', 11, NEG, 'end', bold=True))

    # Пояснювальний бокс унизу
    f.append(rect(40, H - 48, 640, 36, fill='#f0f4f8', stroke=MUTED, sw=1.5, rx=6))
    f.append(text(W / 2, H - 25, 'Оптична різниця ходу Δ = n₂·(AB + BC) - n₁·AD ± λ/2 = 2·n₂·d·cos(θ₂) ± λ/2', 12, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'film-reflection-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Порівняння умов стрибка фази для двох типів оптичних систем
# ═══════════════════════════════════════════════════════════════════════════
def fig_phase_shift_conditions():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Стрибок фази на межах розділу та умови інтерференції', 15, INK, 'middle', bold=True))

    # Панель 1: Мильна бульбашка у повітрі (n1 < n2 > n3)
    w_p, h_p = 330, 300
    x_p1, y_p = 30, 55
    f.append(rect(x_p1, y_p, w_p, h_p, fill='#fafafa', stroke=MUTED, sw=1, rx=6))
    f.append(text(x_p1 + w_p/2, y_p + 22, 'А: Мильна плівка (n₁ < n₂ > n₃)', 13, INK, 'middle', bold=True))

    # Межі плівки для Панелі 1
    y_b1 = y_p + 110
    y_b2 = y_p + 190
    f.append(rect(x_p1 + 10, y_b1, w_p - 20, y_b2 - y_b1, fill=FILM_FILL, stroke='none', sw=0))
    f.append(line(x_p1 + 10, y_b1, x_p1 + w_p - 10, y_b1, color=INK, sw=1.5))
    f.append(line(x_p1 + 10, y_b2, x_p1 + w_p - 10, y_b2, color=INK, sw=1.5))

    f.append(text(x_p1 + 20, y_b1 - 12, 'Повітря (n₁ = 1.00)', 11, MUTED, 'start'))
    f.append(text(x_p1 + 20, y_b1 + 22, 'Вода/мило (n₂ = 1.33)', 11, ACCENT, 'start', bold=True))
    f.append(text(x_p1 + 20, y_b2 + 22, 'Повітря (n₃ = 1.00)', 11, MUTED, 'start'))

    # Позначки фазових стрибків
    f.append(text(x_p1 + w_p - 20, y_b1 - 12, 'Стрибок фази Δφ₁ = π', 11, NEG, 'end', bold=True))
    f.append(text(x_p1 + w_p - 20, y_b2 + 22, 'Без стрибка Δφ₂ = 0', 11, POS, 'end', bold=True))

    # Висновки для Панелі 1
    f.append(rect(x_p1 + 15, y_p + 225, w_p - 30, 60, fill='#fff0f0', stroke=NEG, sw=1.5, rx=6))
    f.append(text(x_p1 + w_p/2, y_p + 242, 'Сумарний зсув фаз = π', 11, INK, 'middle', bold=True))
    f.append(text(x_p1 + w_p/2, y_p + 258, 'Максимум: 2·n₂·d·cos(θ₂) = (m + ½)·λ', 11, INK, 'middle'))
    f.append(text(x_p1 + w_p/2, y_p + 274, 'Мінімум (d→0): 2·n₂·d·cos(θ₂) = m·λ (ЧОРНА)', 11, NEG, 'middle', bold=True))


    # Панель 2: Просвітлювальне покриття (n1 < n2 < n3)
    x_p2 = 380
    f.append(rect(x_p2, y_p, w_p, h_p, fill='#fafafa', stroke=MUTED, sw=1, rx=6))
    f.append(text(x_p2 + w_p/2, y_p + 22, 'Б: Просвітлювальне покриття (n₁ < n₂ < n₃)', 13, INK, 'middle', bold=True))

    # Межі плівки для Панелі 2
    f.append(rect(x_p2 + 10, y_b1, w_p - 20, y_b2 - y_b1, fill=FILM_FILL, stroke='none', sw=0))
    f.append(rect(x_p2 + 10, y_b2, w_p - 20, y_p + h_p - y_b2 - 10, fill=GLASS_FILL, stroke='none', sw=0))
    f.append(line(x_p2 + 10, y_b1, x_p2 + w_p - 10, y_b1, color=INK, sw=1.5))
    f.append(line(x_p2 + 10, y_b2, x_p2 + w_p - 10, y_b2, color=INK, sw=1.5))

    f.append(text(x_p2 + 20, y_b1 - 12, 'Повітря (n₁ = 1.00)', 11, MUTED, 'start'))
    f.append(text(x_p2 + 20, y_b1 + 22, 'Плівка MgF₂ (n₂ = 1.38)', 11, ACCENT, 'start', bold=True))
    f.append(text(x_p2 + 20, y_b2 + 22, 'Скло (n₃ = 1.52)', 11, FIELD, 'start', bold=True))

    # Позначки фазових стрибків
    f.append(text(x_p2 + w_p - 20, y_b1 - 12, 'Стрибок фази Δφ₁ = π', 11, NEG, 'end', bold=True))
    f.append(text(x_p2 + w_p - 20, y_b2 + 22, 'Стрибок фази Δφ₂ = π', 11, NEG, 'end', bold=True))

    # Висновки для Панелі 2
    f.append(rect(x_p2 + 15, y_p + 225, w_p - 30, 60, fill='#f0fff0', stroke=POS, sw=1.5, rx=6))
    f.append(text(x_p2 + w_p/2, y_p + 242, 'Сумарний зсув фаз = 2π ≡ 0', 11, INK, 'middle', bold=True))
    f.append(text(x_p2 + w_p/2, y_p + 258, 'Мінімум відбиття: 2·n₂·d·cos(θ₂) = (m + ½)·λ', 11, INK, 'middle'))
    f.append(text(x_p2 + w_p/2, y_p + 274, 'Оптимальна товщина d = λ / (4·n₂)', 11, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'phase-shift-conditions.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Кільця Ньютона: схема експерименту та інтерференційна картина
# ═══════════════════════════════════════════════════════════════════════════
def fig_newton_rings_diagram():
    W, H = 740, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Схема утворення кілець Ньютона та інтерференційна картина', 15, INK, 'middle', bold=True))

    # Ліва частина: Геометрія лінзи на пластині
    cx, cy = 200, 240
    R_lens = 220
    w_plate = 300
    y_plate = cy + 40

    # Скляна пластина
    f.append(rect(cx - w_plate/2, y_plate, w_plate, 40, fill=GLASS_FILL, stroke=INK, sw=1.5))
    f.append(text(cx, y_plate + 25, 'Плоска скляна пластина', 11, MUTED, 'middle'))

    # Лінза (дуга плоско-опуклої лінзи)
    d_path = f"M {cx - 130:.1f} {y_plate - 38:.1f} Q {cx:.1f} {y_plate:.1f} {cx + 130:.1f} {y_plate - 38:.1f} L {cx + 130:.1f} {cy - 80:.1f} L {cx - 130:.1f} {cy - 80:.1f} Z"
    f.append(f'<path d="{d_path}" fill="{GLASS_FILL}" stroke="{INK}" stroke-width="1.5"/>')
    f.append(text(cx, cy - 50, 'Плоско-опукла лінза (R)', 11, INK, 'middle', bold=True))

    # Повітряний зазор
    f.append(circle(cx, y_plate, 3, fill=NEG, stroke='none'))
    f.append(text(cx, y_plate - 8, 'Центральний контакт (d=0, чорна пляма)', 10, NEG, 'middle', bold=True))

    # Падаюче світло (вертикальні промені)
    for dx_r in [-80, -40, 40, 80]:
        f.append(arrow(cx + dx_r, cy - 110, cx + dx_r, cy - 75, color=POS, sw=1.8))
    f.append(text(cx, cy - 120, 'паралельний пучок світла (λ)', 11, POS, 'middle', bold=True))

    # Позначення радіуса r та товщини d(r)
    rx_mark = cx + 80
    y_lens_at_r = y_plate - (80**2) / (2 * R_lens)
    f.append(line(cx, y_plate + 6, rx_mark, y_plate + 6, color=ACCENT, sw=1.2))
    f.append(text(cx + 40, y_plate + 18, 'r', 11, ACCENT, 'middle', italic=True))

    f.append(line(rx_mark, y_lens_at_r, rx_mark, y_plate, color=NEG, sw=1.5))
    f.append(text(rx_mark + 14, (y_lens_at_r + y_plate)/2 + 4, 'd(r)', 10, NEG, 'start', italic=True))

    # Права частина: Інтерференційні кільця
    rcx, rcy = 550, 220
    r_max = 130

    # Фон інтерференційної картини
    f.append(circle(rcx, rcy, r_max, fill='#111111', stroke=INK, sw=2))

    # Намалюємо серію концентричних кілець
    num_rings = 7
    for m in range(num_rings, 0, -1):
        r_outer = r_max * math.sqrt(m / num_rings)
        r_inner = r_max * math.sqrt((m - 0.5) / num_rings)
        sw_ring = max(1.5, (r_outer - r_inner))
        f.append(circle(rcx, rcy, (r_outer + r_inner)/2, fill='none', stroke='#ffffff', sw=sw_ring))

    # Центральна темна пляма
    f.append(circle(rcx, rcy, r_max * math.sqrt(0.4 / num_rings), fill='#000000', stroke='none'))

    f.append(text(rcx, rcy + r_max + 22, 'Концентричні кільця Ньютона в відбитому світлі', 12, INK, 'middle', bold=True))
    f.append(text(rcx, rcy + r_max + 38, 'Радіуси темних кілець: rₘ = √(m·λ·R)', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'newton-rings-diagram.svg'), W, H, *f)

if __name__ == '__main__':
    fig_film_reflection_geometry()
    fig_phase_shift_conditions()
    fig_newton_rings_diagram()
    print("Figures generated successfully.")
