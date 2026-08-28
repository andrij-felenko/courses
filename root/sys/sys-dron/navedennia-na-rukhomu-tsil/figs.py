#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми navedennia-na-rukhomu-tsil.
Вивід у ./img/
"""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_pursuit_vs_pn():
    """Фігура 1: Порівняння кінематики прямої погоні (Pure Pursuit) та пропорційної навігації (PN)."""
    w, h = 880, 420
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Ліва панель: Пряма погоня (Pure Pursuit)
    elements.append(rect(20, 20, 405, 380, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(222, 45, "Пряма погоня (Pure Pursuit)", size=14, color=INK, bold=True))
    elements.append(text(222, 68, "Вектор швидкості V_d завжди спрямований на ціль", size=11, color=MUTED))
    
    # Траєкторія цілі (ліва панель) - пряма лінія вгору-вправо
    # T0 -> T1 -> T2 -> T3 -> T4
    t_pts_left = [(280, 330), (295, 260), (310, 190), (325, 120), (340, 50)]
    for i in range(len(t_pts_left)-1):
        elements.append(line(t_pts_left[i][0], t_pts_left[i][1], t_pts_left[i+1][0], t_pts_left[i+1][1], color=POS, sw=2, dash="4,4"))
    for i, pt in enumerate(t_pts_left):
        elements.append(circle(pt[0], pt[1], 4, fill=POS, stroke=POS))
        elements.append(text(pt[0] + 18, pt[1] + 4, f"T{i}", size=10, color=POS, bold=True))
    
    # Траєкторія переслідувача PP (хвіст, що закручується)
    d_pts_left = [(60, 330), (130, 285), (205, 230), (275, 155), (325, 65)]
    for i in range(len(d_pts_left)-1):
        elements.append(line(d_pts_left[i][0], d_pts_left[i][1], d_pts_left[i+1][0], d_pts_left[i+1][1], color=NEG, sw=2.2))
    for i, pt in enumerate(d_pts_left):
        elements.append(circle(pt[0], pt[1], 4, fill=NEG, stroke=NEG))
        elements.append(text(pt[0] - 16, pt[1] + 4, f"D{i}", size=10, color=NEG, bold=True))
        # Лінія візування LOS (пунктир)
        elements.append(line(pt[0], pt[1], t_pts_left[i][0], t_pts_left[i][1], color="#94a3b8", sw=1, dash="2,2"))
    
    # Підпис дефекту PP
    elements.append(rect(40, 350, 365, 40, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    elements.append(text(222, 368, "Крива погоні: лінія LOS неперервно крутиться", size=10, color=POS, bold=True))
    elements.append(text(222, 382, "При R → 0 потрібне поперечне прискорення a_n → ∞", size=10, color=POS))
    
    # Права панель: Пропорційна навігація (PN)
    elements.append(rect(455, 20, 405, 380, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(657, 45, "Пропорційна навігація (PN)", size=14, color=INK, bold=True))
    elements.append(text(657, 68, "Курс на випередження з постійним кутом візування", size=11, color=MUTED))
    
    # Траєкторія цілі (права панель)
    t_pts_right = [(715, 330), (730, 260), (745, 190), (760, 120), (775, 50)]
    for i in range(len(t_pts_right)-1):
        elements.append(line(t_pts_right[i][0], t_pts_right[i][1], t_pts_right[i+1][0], t_pts_right[i+1][1], color=POS, sw=2, dash="4,4"))
    for i, pt in enumerate(t_pts_right):
        elements.append(circle(pt[0], pt[1], 4, fill=POS, stroke=POS))
        elements.append(text(pt[0] + 18, pt[1] + 4, f"T{i}", size=10, color=POS, bold=True))
    
    # Траєкторія дрона PN (пряма траєкторія зустрічі)
    d_pts_right = [(495, 330), (565, 260), (635, 190), (705, 120), (775, 50)]
    for i in range(len(d_pts_right)-1):
        elements.append(line(d_pts_right[i][0], d_pts_right[i][1], d_pts_right[i+1][0], d_pts_right[i+1][1], color=FIELD, sw=2.2))
    for i, pt in enumerate(d_pts_right):
        elements.append(circle(pt[0], pt[1], 4, fill=FIELD, stroke=FIELD))
        elements.append(text(pt[0] - 16, pt[1] + 4, f"D{i}", size=10, color=FIELD, bold=True))
        # Паралельні лінії візування LOS (постійний пеленг)
        elements.append(line(pt[0], pt[1], t_pts_right[i][0], t_pts_right[i][1], color="#94a3b8", sw=1.2, dash="3,3"))
    
    # Позначка паралельності LOS
    elements.append(text(615, 305, "λ = const (Ω = 0)", size=10, color=FIELD, bold=True))
    
    # Підпис переваги PN
    elements.append(rect(475, 350, 365, 40, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    elements.append(text(657, 368, "Постійний пеленг: трикутник зіткнення замкнено", size=10, color=FIELD, bold=True))
    elements.append(text(657, 382, "Прискорення a_cmd спадає до нуля біля точки зустрічі", size=10, color=FIELD))
    
    path = os.path.join(IMG_DIR, 'pursuit-vs-proportional-navigation.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_engagement_geometry():
    """Фігура 2: Геометрія зближення (Engagement Geometry) та вектори лінії візування (LOS)."""
    w, h = 840, 440
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок
    elements.append(text(420, 28, "Кінематична схема взаємного зближення дрона (D) та цілі (T)", size=14, color=INK, bold=True))
    
    # Осі інерційної системи координат X_I, Y_I
    elements.append(arrow(50, 390, 170, 390, color=MUTED, sw=1.5))
    elements.append(text(175, 394, "X_I (Схід / Східний)", size=10, color=MUTED, anchor="start"))
    elements.append(arrow(50, 390, 50, 270, color=MUTED, sw=1.5))
    elements.append(text(50, 258, "Y_I (Північ / Північний)", size=10, color=MUTED))
    
    # Точки D (Дрон) та T (Ціль)
    xd, yd = 180, 310
    xt, yt = 620, 110
    
    # Горизонтальна опорна вісь від D
    elements.append(line(xd, yd, xd + 200, yd, color="#cbd5e1", sw=1.2, dash="4,4"))
    # Горизонтальна опорна вісь від T
    elements.append(line(xt, yt, xt + 140, yt, color="#cbd5e1", sw=1.2, dash="4,4"))
    
    # Лінія візування LOS (R)
    elements.append(line(xd, yd, xt, yt, color=LINE, sw=2))
    
    # Одиничні орти лінії візування: e_los та e_los_perp
    cos_l = (xt - xd) / math.hypot(xt - xd, yt - yd)
    sin_l = (yt - yd) / math.hypot(xt - xd, yt - yd)
    
    # e_los
    elements.append(arrow(xd + 80 * cos_l, yd + 80 * sin_l, xd + 140 * cos_l, yd + 140 * sin_l, color=LINE, sw=2))
    elements.append(text(xd + 145 * cos_l + 10, yd + 145 * sin_l - 10, "e_los", size=11, color=INK, bold=True))
    
    # e_los_perp (повернутий на +90 градусів: (-sin, cos))
    elements.append(arrow(xd + 80 * cos_l, yd + 80 * sin_l, xd + 80 * cos_l - 50 * sin_l, yd + 80 * sin_l + 50 * cos_l, color="#7c3aed", sw=2))
    elements.append(text(xd + 80 * cos_l - 55 * sin_l - 15, yd + 80 * sin_l + 55 * cos_l + 10, "e_los_⊥", size=11, color="#7c3aed", bold=True))
    
    # Кут візування lambda (LOS angle)
    elements.append(text(xd + 75, yd - 14, "λ", size=13, color=LINE, bold=True))
    elements.append(text(380, 225, "Дальність R = ||r_t - r_d||", size=11, color=INK, bold=True))
    elements.append(text(380, 243, "Швидкість зближення V_c = -dR/dt", size=10, color=MUTED))
    
    # Дрон D
    elements.append(circle(xd, yd, 8, fill=NEG, stroke=LINE, sw=2))
    elements.append(text(xd - 20, yd + 20, "D (Дрон)", size=12, color=NEG, bold=True))
    
    # Вектор швидкості V_d (напрямок під кутом gamma_d)
    v_dx, v_dy = xd + 110, yd - 120
    elements.append(arrow(xd, yd, v_dx, v_dy, color=NEG, sw=2.5))
    elements.append(text(v_dx + 10, v_dy - 10, "V_d (Швидкість дрона)", size=11, color=NEG, bold=True))
    
    # Кут випередження delta_d між V_d та LOS
    elements.append(text(xd + 45, yd - 65, "δ_d", size=11, color=NEG))
    
    # Командне прискорення a_cmd_perp (перпендикулярне до V_d або LOS)
    a_cmd_x, a_cmd_y = xd - 45, yd - 45
    elements.append(arrow(xd + 40, yd - 40, a_cmd_x, a_cmd_y, color=POS, sw=2.5))
    elements.append(text(a_cmd_x - 35, a_cmd_y - 8, "a_cmd = N · V_c · Ω", size=11, color=POS, bold=True))
    
    # Ціль T
    elements.append(circle(xt, yt, 8, fill=POS, stroke=LINE, sw=2))
    elements.append(text(xt + 25, yt + 20, "T (Ціль)", size=12, color=POS, bold=True))
    
    # Вектор швидкості V_t
    v_tx, v_ty = xt + 80, yt - 60
    elements.append(arrow(xt, yt, v_tx, v_ty, color=POS, sw=2.5))
    elements.append(text(v_tx + 10, v_ty - 5, "V_t (Швидкість цілі)", size=11, color=POS, bold=True))
    
    # Обертання лінії візування Omega
    elements.append(text(460, 160, "Кутова швидкість LOS: Ω = dλ/dt = (R × V_r) / R²", size=11, color="#7c3aed", bold=True))
    
    # Інформаційна рамка внизу
    elements.append(rect(30, 360, 780, 60, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(420, 382, "Закон наведення: прискорення a_cmd прикладається перпендикулярно до лінії візування", size=11, color=INK, bold=True))
    elements.append(text(420, 402, "Мета контуру керування — обнулити кутову швидкість обертання лінії візування (Ω → 0)", size=11, color=MUTED))
    
    path = os.path.join(IMG_DIR, 'engagement-geometry-los.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_pn_acceleration_profiles():
    """Фігура 3: Профілі командного прискорення a_cmd(t) при різних коефіцієнтах N."""
    w, h = 820, 340
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(410, 25, "Динаміка прискорення a_cmd(t) залежно від навігаційного коефіцієнта N", size=14, color=INK, bold=True))
    
    # Графік: осі
    ox, oy = 80, 280
    gw, gh = 420, 220
    
    # Сітка
    elements.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    elements.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    elements.append(arrow(ox + gw, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    elements.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))
    
    elements.append(text(ox + gw + 15, oy + 18, "Час t → t_go", size=11, color=INK, bold=True))
    elements.append(text(ox - 35, oy - gh - 8, "a_cmd", size=12, color=INK, bold=True))
    
    # Відмітки осі X
    elements.append(text(ox, oy + 18, "0", size=10, color=MUTED))
    elements.append(text(ox + gw * 0.5, oy + 18, "0.5 · t_f", size=10, color=MUTED))
    elements.append(text(ox + gw, oy + 18, "t_f (Зустріч)", size=10, color=POS, bold=True))
    
    # Криві:
    # 1) N = 1 (Pure Pursuit): a ~ 1 / (1 - t/t_f) -> стрімке зростання до нескінченності
    pts_n1 = []
    for step in range(30):
        frac = step / 30.0 * 0.92
        x = ox + frac * gw
        y = oy - (15 + 10 / (1.0 - frac * 0.98)**1.6)
        pts_n1.append((x, max(oy - gh + 5, y)))
    for i in range(len(pts_n1)-1):
        elements.append(line(pts_n1[i][0], pts_n1[i][1], pts_n1[i+1][0], pts_n1[i+1][1], color="#dc2626", sw=2.2))
    elements.append(text(pts_n1[-1][0] - 15, pts_n1[-1][1] - 8, "N = 1 (PP: a → ∞)", size=10, color="#dc2626", bold=True))
    
    # 2) N = 2: майже постійне або слабке зростання
    pts_n2 = []
    for step in range(30):
        frac = step / 30.0
        x = ox + frac * gw
        y = oy - (45 + 25 * frac**1.2)
        pts_n2.append((x, y))
    for i in range(len(pts_n2)-1):
        elements.append(line(pts_n2[i][0], pts_n2[i][1], pts_n2[i+1][0], pts_n2[i+1][1], color="#ea580c", sw=2, dash="4,2"))
    elements.append(text(pts_n2[-1][0] + 10, pts_n2[-1][1] - 4, "N = 2", size=10, color="#ea580c", bold=True, anchor="start"))
    
    # 3) N = 3 (Оптимум): спадання до нуля
    pts_n3 = []
    for step in range(30):
        frac = step / 30.0
        x = ox + frac * gw
        y = oy - (105 * (1.0 - frac * 0.85))
        pts_n3.append((x, y))
    for i in range(len(pts_n3)-1):
        elements.append(line(pts_n3[i][0], pts_n3[i][1], pts_n3[i+1][0], pts_n3[i+1][1], color=FIELD, sw=2.5))
    elements.append(text(pts_n3[-1][0] + 10, pts_n3[-1][1] + 4, "N = 3 (Оптимум)", size=10, color=FIELD, bold=True, anchor="start"))
    
    # 4) N = 4..5: високе початкове, швидке спадання
    pts_n5 = []
    for step in range(30):
        frac = step / 30.0
        x = ox + frac * gw
        y = oy - (175 * (1.0 - frac)**1.8 + 8)
        pts_n5.append((x, y))
    for i in range(len(pts_n5)-1):
        elements.append(line(pts_n5[i][0], pts_n5[i][1], pts_n5[i+1][0], pts_n5[i+1][1], color=NEG, sw=2, dash="5,3"))
    elements.append(text(pts_n5[-1][0] + 10, pts_n5[-1][1] + 12, "N = 5", size=10, color=NEG, bold=True, anchor="start"))
    
    # Права панель: Пояснення та висновки
    bx, by, bw, bh = 540, 55, 260, 245
    elements.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(bx + bw/2, by + 25, "Висновки вибору N", size=12, color=INK, bold=True))
    
    elements.append(text(bx + 15, by + 58, "• N < 2:", size=11, color="#dc2626", bold=True, anchor="start"))
    elements.append(text(bx + 68, by + 58, "перевантаження зростає наприкінці", size=10, color=INK, anchor="start"))
    elements.append(text(bx + 20, by + 74, "неминучий зрив стеження при обмеженні a_max", size=9.5, color=MUTED, anchor="start"))
    
    elements.append(text(bx + 15, by + 105, "• N = 3:", size=11, color=FIELD, bold=True, anchor="start"))
    elements.append(text(bx + 68, by + 105, "мінімум інтегралу енергії ∫ a² dt", size=10, color=INK, anchor="start"))
    elements.append(text(bx + 20, by + 121, "найкращий баланс для маневрених дронів", size=9.5, color=MUTED, anchor="start"))
    
    elements.append(text(bx + 15, by + 152, "• N = 4..5:", size=11, color=NEG, bold=True, anchor="start"))
    elements.append(text(bx + 80, by + 152, "швидке виправлення помилки курсу", size=10, color=INK, anchor="start"))
    elements.append(text(bx + 20, by + 168, "чутливий до шумів давача та запізнень", size=9.5, color=MUTED, anchor="start"))
    
    elements.append(text(bx + 15, by + 200, "• N > 5:", size=11, color=POS, bold=True, anchor="start"))
    elements.append(text(bx + 68, by + 200, "шумове тремтіння приводів", size=10, color=INK, anchor="start"))
    elements.append(text(bx + 20, by + 216, "високий ризик насичення моторів", size=9.5, color=MUTED, anchor="start"))
    
    path = os.path.join(IMG_DIR, 'pn-acceleration-profiles.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_moving_vessel_landing():
    """Фігура 4: Фази посадки дрона на рухому платформу (Moving Vessel Landing / Rendezvous)."""
    w, h = 860, 360
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(430, 26, "Архітектура трифазного зближення та посадки на рухому морську платформу", size=14, color=INK, bold=True))
    
    # 3 Фази як послідовні горизонтальні блоки
    # Фаза 1: PN Rendezvous
    elements.append(rect(20, 60, 260, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(150, 88, "Фаза 1: PN-Рандеву", size=13, color=NEG, bold=True))
    elements.append(text(150, 110, "Дальність: 500 м → 20 м", size=11, color=MUTED))
    elements.append(text(150, 140, "• Наведення PN з профілем V_c(R)", size=10.5, color=INK))
    elements.append(text(150, 165, "• Гальмування відносної швидкості", size=10.5, color=INK))
    elements.append(text(150, 190, "• Вирівнювання векторів швидкості", size=10.5, color=INK))
    elements.append(text(150, 215, "• Захоплення палуби камерою/GNSS", size=10.5, color=INK))
    elements.append(rect(35, 245, 230, 40, fill="#e0e7ff", stroke=NEG, sw=1, rx=6))
    elements.append(text(150, 268, "Критерій: R < 20м, ΔV < 2 м/с", size=10.5, color=NEG, bold=True))
    
    # Стрілка 1 -> 2
    elements.append(arrow(285, 175, 305, 175, color=LINE, sw=2))
    
    # Фаза 2: Station Keeping
    elements.append(rect(310, 60, 260, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(440, 88, "Фаза 2: Синхронізація", size=13, color="#d97706", bold=True))
    elements.append(text(440, 110, "Дальність: 20 м → 2 м над палубою", size=11, color=MUTED))
    elements.append(text(440, 140, "• Перехід у локальний NED палуби", size=10.5, color=INK))
    elements.append(text(440, 165, "• Відносне PD-стеження позиції", size=10.5, color=INK))
    elements.append(text(440, 190, "• Оцінка кілевої/бортової качки", size=10.5, color=INK))
    elements.append(text(440, 215, "• Утримання точки зависання над H", size=10.5, color=INK))
    elements.append(rect(325, 245, 230, 40, fill="#fef3c7", stroke="#d97706", sw=1, rx=6))
    elements.append(text(440, 268, "Критерій: похибка < 0.2м, фаза качки", size=10.5, color="#d97706", bold=True))
    
    # Стрілка 2 -> 3
    elements.append(arrow(575, 175, 595, 175, color=LINE, sw=2))
    
    # Фаза 3: Touchdown
    elements.append(rect(600, 60, 240, 240, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(720, 88, "Фаза 3: Торкання", size=13, color=FIELD, bold=True))
    elements.append(text(720, 110, "Висота: 2 м → 0 м (Контакт)", size=11, color=MUTED))
    elements.append(text(720, 140, "• Швидке вертикальне зниження", size=10.5, color=INK))
    elements.append(text(720, 165, "• Синхронізація з фазою качки", size=10.5, color=INK))
    elements.append(text(720, 190, "• Компенсація екранного ефекту", size=10.5, color=INK))
    elements.append(text(720, 215, "• Вимкнення моторів (Disarm)", size=10.5, color=INK))
    elements.append(rect(615, 245, 210, 40, fill="#f0fdf4", stroke=FIELD, sw=1, rx=6))
    elements.append(text(720, 268, "Контакт: розпізнавання посадки", size=10.5, color=FIELD, bold=True))
    
    # Пояснення знизу
    elements.append(rect(20, 315, 820, 35, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(430, 337, "Головна відмінність від перехоплення: при посадці відносна швидкість V_r у момент контакту має дорівнювати нулю", size=11, color=INK, bold=True))
    
    path = os.path.join(IMG_DIR, 'moving-vessel-landing-phases.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_kalman_guidance_pipeline():
    """Фігура 5: Повний контур наведення: Сенсори -> EKF стану цілі -> PN -> Автопілот."""
    w, h = 860, 290
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(430, 25, "Контур оцінки стану цілі та формування команд автопілота", size=14, color=INK, bold=True))
    
    # 1. Сенсори
    elements.append(rect(20, 55, 175, 175, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(107, 80, "Сенсори та зір", size=12, color=INK, bold=True))
    elements.append(text(107, 110, "Камера / Трекер", size=10.5, color=INK))
    elements.append(text(107, 130, "(пікселі u, v)", size=10, color=MUTED))
    elements.append(text(107, 158, "Далекомір / Лідар", size=10.5, color=INK))
    elements.append(text(107, 178, "(дальність r_meas)", size=10, color=MUTED))
    elements.append(text(107, 205, "Бортовий EKF дрона", size=10, color=MUTED))
    
    # Стрілка 1 -> 2
    elements.append(arrow(195, 142, 235, 142, color=LINE, sw=1.8))
    elements.append(text(215, 130, "Z_k", size=11, color=INK, bold=True))
    
    # 2. Kalman Filter (Target State Estimator)
    elements.append(rect(240, 55, 205, 175, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    elements.append(text(342, 80, "Фільтр Калмана (Ціль)", size=12, color=NEG, bold=True))
    elements.append(text(342, 105, "Стан: [r_t, v_t, a_t]ᵀ", size=10.5, color=INK, bold=True))
    elements.append(text(342, 132, "• Фільтрація шуму кутів", size=10, color=INK))
    elements.append(text(342, 152, "• Оцінка прискорення цілі", size=10, color=INK))
    elements.append(text(342, 172, "• Компенсація затримки vision", size=10, color=INK))
    elements.append(text(342, 205, "Обчислення: Ω_LOS, V_c", size=10.5, color=NEG, bold=True))
    
    # Стрілка 2 -> 3
    elements.append(arrow(445, 142, 485, 142, color=LINE, sw=1.8))
    elements.append(text(465, 130, "Ω, V_c", size=11, color=INK, bold=True))
    
    # 3. Guidance Law (PN / APN)
    elements.append(rect(490, 55, 170, 175, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    elements.append(text(575, 80, "Закон наведення", size=12, color=FIELD, bold=True))
    elements.append(text(575, 105, "PN / APN", size=12, color=FIELD, bold=True))
    elements.append(text(575, 135, "a_cmd = N·V_c·Ω", size=11, color=INK, bold=True))
    elements.append(text(575, 155, "+ N/2 · a_t (APN)", size=10, color=MUTED))
    elements.append(text(575, 185, "Обмеження a_max", size=10, color=INK))
    elements.append(text(575, 205, "Rate Limiting (ривок)", size=10, color=INK))
    
    # Стрілка 3 -> 4
    elements.append(arrow(660, 142, 695, 142, color=LINE, sw=1.8))
    elements.append(text(677, 130, "a_des", size=11, color=INK, bold=True))
    
    # 4. Flight Controller Inner Loops
    elements.append(rect(700, 55, 140, 175, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(770, 80, "Автопілот", size=12, color=INK, bold=True))
    elements.append(text(770, 105, "Контур кутів", size=11, color=INK))
    elements.append(text(770, 135, "a_des → [θ, φ]des", size=10.5, color=INK, bold=True))
    elements.append(text(770, 155, "T_des (Тяга)", size=10, color=MUTED))
    elements.append(text(770, 185, "PID кутових", size=10, color=INK))
    elements.append(text(770, 205, "швидкостей", size=10, color=INK))
    
    # Пояснення знизу
    elements.append(rect(20, 245, 820, 32, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(430, 266, "Повний цикл замкненого контуру: частота оцінки стану цілі 30–100 Гц, контури кутів 250–500 Гц", size=11, color=MUTED, italic=True))
    
    path = os.path.join(IMG_DIR, 'kalman-guidance-pipeline.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_pursuit_vs_pn()
    fig_engagement_geometry()
    fig_pn_acceleration_profiles()
    fig_moving_vessel_landing()
    fig_kalman_guidance_pipeline()
