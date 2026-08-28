#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми tsil-zahublena (sys-dron).
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


def fig_target_lost_fsm():
    """Фігура 1: Кінцевий автомат обробки втрати візуального контакту з ціллю."""
    w, h = 900, 480
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(450, 26, "Кінцевий автомат (FSM) відновлення супроводу та відмови від цілі", size=14, color=INK, bold=True))

    # Стан 1: TRACKING (Нормальний супровід)
    s1_x, s1_y, s1_w, s1_h = 40, 70, 230, 150
    elements.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    elements.append(text(s1_x + s1_w/2, s1_y + 26, "1. TRACKING (Супровід)", size=12, color=FIELD, bold=True))
    elements.append(line(s1_x + 10, s1_y + 36, s1_x + s1_w - 10, s1_y + 36, color=FIELD, sw=1, dash="2,2"))
    elements.append(text(s1_x + 15, s1_y + 58, "• Прямий візуальний контакт", size=10, color=INK, anchor="start"))
    elements.append(text(s1_x + 15, s1_y + 78, "• Оновлення EKF цілі (30–60 Гц)", size=10, color=INK, anchor="start"))
    elements.append(text(s1_x + 15, s1_y + 98, "• Оцінка швидкості [v_x, v_y, v_z]", size=10, color=INK, anchor="start"))
    elements.append(text(s1_x + 15, s1_y + 118, "• Збереження Re-ID дескриптора", size=10, color=INK, anchor="start"))
    elements.append(text(s1_x + 15, s1_y + 138, "• Коваріація похибки P мінімальна", size=9.5, color=MUTED, anchor="start"))

    # Стан 2: COAST (Кінематична екстраполяція)
    s2_x, s2_y, s2_w, s2_h = 335, 70, 245, 150
    elements.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    elements.append(text(s2_x + s2_w/2, s2_y + 26, "2. COAST (Екстраполяція)", size=12, color=NEG, bold=True))
    elements.append(line(s2_x + 10, s2_y + 36, s2_x + s2_w - 10, s2_y + 36, color=NEG, sw=1, dash="2,2"))
    elements.append(text(s2_x + 15, s2_y + 58, "• Таймаут T_coast: 0.5–2.0 с", size=10, color=INK, anchor="start"))
    elements.append(text(s2_x + 15, s2_y + 78, "• Рух камери за вектором v_last", size=10, color=INK, anchor="start"))
    elements.append(text(s2_x + 15, s2_y + 98, "• Прогноз позиції: p_k = p_0 + v·Δt", size=10, color=INK, anchor="start"))
    elements.append(text(s2_x + 15, s2_y + 118, "• Розширення стробу Махаланобіса", size=10, color=INK, anchor="start"))
    elements.append(text(s2_x + 15, s2_y + 138, "• Очікування виходу з оклюзії", size=9.5, color=MUTED, anchor="start"))

    # Стан 3: SEARCH (Розширений пошук)
    s3_x, s3_y, s3_w, s3_h = 640, 70, 220, 150
    elements.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    elements.append(text(s3_x + s3_w/2, s3_y + 26, "3. SEARCH (Пошук)", size=12, color="#d97706", bold=True))
    elements.append(line(s3_x + 10, s3_y + 36, s3_x + s3_w - 10, s3_y + 36, color="#d97706", sw=1, dash="2,2"))
    elements.append(text(s3_x + 15, s3_y + 58, "• Таймаут T_search: 2–10 с", size=10, color=INK, anchor="start"))
    elements.append(text(s3_x + 15, s3_y + 78, "• Оптичний Zoom-out (FOV+)", size=10, color=INK, anchor="start"))
    elements.append(text(s3_x + 15, s3_y + 98, "• Спіральне/секторне сканування", size=10, color=INK, anchor="start"))
    elements.append(text(s3_x + 15, s3_y + 118, "• Фільтрація Re-ID та Gate", size=10, color=INK, anchor="start"))
    elements.append(text(s3_x + 15, s3_y + 138, "• Збільшення висоти огляду", size=9.5, color=MUTED, anchor="start"))

    # Стан 4: DISENGAGED / FAILSAFE (Відмова / Аварійний режим)
    s4_x, s4_y, s4_w, s4_h = 335, 295, 245, 140
    elements.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    elements.append(text(s4_x + s4_w/2, s4_y + 26, "4. DISENGAGED / FAILSAFE", size=12, color=POS, bold=True))
    elements.append(line(s4_x + 10, s4_y + 36, s4_x + s4_w - 10, s4_y + 36, color=POS, sw=1, dash="2,2"))
    elements.append(text(s4_x + 15, s4_y + 58, "• Повна втрата цілі (Timeout)", size=10, color=INK, anchor="start"))
    elements.append(text(s4_x + 15, s4_y + 78, "• LOITER: зависання в точці", size=10, color=INK, anchor="start"))
    elements.append(text(s4_x + 15, s4_y + 98, "• MISSION RESUME: далі за WPT", size=10, color=INK, anchor="start"))
    elements.append(text(s4_x + 15, s4_y + 118, "• RTL: повернення на точку старту", size=10, color=INK, anchor="start"))

    # СТРІЛКИ ТА ПЕРЕХОДИ МІЖ СТАНАМИ

    # Перехід 1 -> 2: Втрата детекції (Loss of Detection)
    elements.append(arrow(s1_x + s1_w, 115, s2_x, 115, color=NEG, sw=2))
    elements.append(text(s1_x + s1_w + 32, 103, "Зрив детекції", size=10, color=NEG, bold=True))
    elements.append(text(s1_x + s1_w + 32, 127, "score < γ_conf", size=9, color=MUTED))

    # Перехід 2 -> 1: Швидке перезахоплення у фазі Coast
    elements.append(arrow(s2_x, 160, s1_x + s1_w, 160, color=FIELD, sw=2))
    elements.append(text(s1_x + s1_w + 32, 150, "Re-acquired", size=10, color=FIELD, bold=True))
    elements.append(text(s1_x + s1_w + 32, 175, "d_M < γ & S_app > γ", size=9, color=FIELD))

    # Перехід 2 -> 3: Вичерпання Coast Timeout
    elements.append(arrow(s2_x + s2_w, 115, s3_x, 115, color="#d97706", sw=2))
    elements.append(text(s2_x + s2_w + 30, 103, "t > T_coast", size=10, color="#d97706", bold=True))
    elements.append(text(s2_x + s2_w + 30, 127, "(0.5–2.0 с)", size=9, color=MUTED))

    # Перехід 3 -> 1: Перезахоплення у фазі Search
    elements.append(line(s3_x + s3_w/2, s3_y, s3_x + s3_w/2, 45, color=FIELD, sw=1.8, dash="4,2"))
    elements.append(line(s3_x + s3_w/2, 45, s1_x + s1_w/2, 45, color=FIELD, sw=1.8, dash="4,2"))
    elements.append(arrow(s1_x + s1_w/2, 45, s1_x + s1_w/2, s1_y, color=FIELD, sw=1.8))
    elements.append(text(450, 40, "Перезахоплення під час пошуку (Строб + Re-ID валідація)", size=10, color=FIELD, bold=True))

    # Перехід 3 -> 4: Вичерпання Search Timeout -> Відмова
    elements.append(line(s3_x + s3_w/2, s3_y + s3_h, s3_x + s3_w/2, 365, color=POS, sw=2))
    elements.append(arrow(s3_x + s3_w/2, 365, s4_x + s4_w, 365, color=POS, sw=2))
    elements.append(text(670, 352, "t > T_search (Таймаут пошуку)", size=10, color=POS, bold=True))
    elements.append(text(670, 380, "Ціль не знайдена → Failsafe", size=9, color=MUTED))

    # Перехід 4 -> 1: Ручне перезахоплення оператором / нова місія
    elements.append(line(s4_x, 365, s1_x + s1_w/2, 365, color=MUTED, sw=1.5, dash="3,3"))
    elements.append(arrow(s1_x + s1_w/2, 365, s1_x + s1_w/2, s1_y + s1_h, color=MUTED, sw=1.5))
    elements.append(text(155, 352, "Нове цілевказання / Скидання", size=9.5, color=MUTED, bold=True))

    # Рамка таймінгу внизу
    elements.append(rect(40, 445, 820, 25, fill=FILL, stroke=LINE, sw=1, rx=4))
    elements.append(text(450, 461, "Детерміновані фази: безперервний контроль безпеки, захист від безконтрольного крутіння та зависання", size=10, color=MUTED, italic=True))

    path = os.path.join(IMG_DIR, 'target-lost-fsm-phases.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_search_pattern_and_gating():
    """Фігура 2: Просторова схема екстраполяції, стробування Махаланобіса та пошукових траєкторій."""
    w, h = 900, 460
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    elements.append(text(450, 26, "Просторове стробування (Spatial Gating) та траєкторія спірального пошуку", size=14, color=INK, bold=True))

    # Ліва частина: Еволюція еліпсоїда невизначеності та строб Махаланобіса
    elements.append(rect(20, 50, 410, 385, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(225, 75, "Екстраполяція та просторовий строб", size=13, color=INK, bold=True))

    # Траєкторія руху цілі до оклюзії
    t0_x, t0_y = 60, 310
    t1_x, t1_y = 130, 260
    t_loss_x, t_loss_y = 190, 220

    # Лінія минулої траєкторії
    elements.append(line(t0_x, t0_y, t1_x, t1_y, color=FIELD, sw=2.5))
    elements.append(line(t1_x, t1_y, t_loss_x, t_loss_y, color=FIELD, sw=2.5))
    elements.append(circle(t0_x, t0_y, 4, fill=FIELD, stroke=FIELD))
    elements.append(text(t0_x - 12, t0_y + 14, "t_-2", size=9, color=MUTED))
    elements.append(circle(t1_x, t1_y, 4, fill=FIELD, stroke=FIELD))
    elements.append(text(t1_x - 12, t1_y + 14, "t_-1", size=9, color=MUTED))
    elements.append(circle(t_loss_x, t_loss_y, 5, fill=POS, stroke=LINE, sw=1.5))
    elements.append(text(t_loss_x - 30, t_loss_y - 12, "Втрата цілі", size=10, color=POS, bold=True))
    elements.append(text(t_loss_x - 30, t_loss_y + 3, "(t_0, v_last)", size=9, color=MUTED))

    # Вектор швидкості v_last
    elements.append(arrow(t_loss_x, t_loss_y, t_loss_x + 50, t_loss_y - 35, color=NEG, sw=2))
    elements.append(text(t_loss_x + 55, t_loss_y - 40, "v_last", size=10, color=NEG, bold=True))

    # Перешкода (будівля / міст / ліс)
    elements.append(rect(160, 100, 80, 85, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    elements.append(text(200, 145, "Оклюзія", size=11, color="#475569", bold=True))
    elements.append(text(200, 160, "(Будівля/Ліс)", size=9, color="#64748b"))

    # Екстрапольовані точки t+1, t+2
    t_pred1_x, t_pred1_y = 260, 170
    t_pred2_x, t_pred2_y = 330, 120
    elements.append(line(t_loss_x, t_loss_y, t_pred1_x, t_pred1_y, color=NEG, sw=2, dash="4,3"))
    elements.append(line(t_pred1_x, t_pred1_y, t_pred2_x, t_pred2_y, color=NEG, sw=2, dash="4,3"))

    # Еліпси невизначеності
    def draw_ellipse(cx, cy, rx, ry, angle_deg, color, dash="3,2"):
        pts = []
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        for deg in range(0, 360, 15):
            r = math.radians(deg)
            px = rx * math.cos(r)
            py = ry * math.sin(r)
            gx = cx + px * cos_a - py * sin_a
            gy = cy + px * sin_a + py * cos_a
            pts.append((gx, gy))
        res = []
        for i in range(len(pts)):
            p1 = pts[i]
            p2 = pts[(i+1)%len(pts)]
            res.append(line(p1[0], p1[1], p2[0], p2[1], color=color, sw=1.5, dash=dash))
        return "".join(res)

    elements.append(circle(t_pred1_x, t_pred1_y, 4, fill=NEG, stroke=NEG))
    elements.append(text(t_pred1_x + 12, t_pred1_y + 16, "p̂(t_coast)", size=9.5, color=NEG, bold=True))
    elements.append(draw_ellipse(t_pred1_x, t_pred1_y, 35, 20, -35, NEG, dash="3,2"))

    # Великий еліпс у t+2 (розширений строб)
    elements.append(circle(t_pred2_x, t_pred2_y, 4, fill="#d97706", stroke="#d97706"))
    elements.append(text(t_pred2_x + 12, t_pred2_y + 18, "p̂(t_search)", size=9.5, color="#d97706", bold=True))
    elements.append(draw_ellipse(t_pred2_x, t_pred2_y, 65, 38, -35, "#d97706", dash="4,3"))

    # Кандидати детекції: Валідний vs Хибний
    c_valid_x, c_valid_y = 315, 135
    elements.append(circle(c_valid_x, c_valid_y, 6, fill=FIELD, stroke=LINE, sw=1.5))
    elements.append(text(c_valid_x - 35, c_valid_y - 12, "Справжня ціль", size=10, color=FIELD, bold=True))
    elements.append(text(c_valid_x - 35, c_valid_y + 4, "d_M² ≤ γ_gate", size=9.5, color=FIELD))

    c_false_x, c_false_y = 360, 240
    elements.append(circle(c_false_x, c_false_y, 6, fill=POS, stroke=LINE, sw=1.5))
    elements.append(text(c_false_x + 12, c_false_y - 4, "Хибний об'єкт (ID Switch)", size=10, color=POS, bold=True, anchor="start"))
    elements.append(text(c_false_x + 12, c_false_y + 12, "d_M² > γ_gate → Відкинуто", size=9.5, color=POS, anchor="start"))

    # Формула внизу лівої панелі
    elements.append(rect(30, 360, 390, 60, fill=FILL, stroke=LINE, sw=1, rx=6))
    elements.append(text(225, 382, "Критерій просторового стробу Махаланобіса:", size=10, color=INK, bold=True))
    elements.append(text(225, 402, "d_M² = (z - ẑ)ᵀ · S⁻¹ · (z - ẑ) ≤ γ_gate", size=10.5, color=NEG, bold=True))


    # Права частина: Патерни пошуку (Спіраль Архімеда та Секторне сканування)
    elements.append(rect(450, 50, 430, 385, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(665, 75, "Траєкторія пошуку: Архімедова спіраль підвісу", size=13, color=INK, bold=True))

    # Центр спіралі
    sp_cx, sp_cy = 665, 230
    elements.append(circle(sp_cx, sp_cy, 5, fill=NEG, stroke=LINE, sw=1.5))
    elements.append(text(sp_cx, sp_cy - 12, "Центр: p̂_lost", size=10, color=NEG, bold=True))

    # Генерація витків архімедової спіралі: r = a + b * theta
    sp_pts = []
    a_param = 8.0
    b_param = 4.2
    for t_step in range(120):
        th = t_step * 0.12
        r_dist = a_param + b_param * th
        gx = sp_cx + r_dist * math.cos(th)
        gy = sp_cy + r_dist * math.sin(th)
        sp_pts.append((gx, gy))

    for i in range(len(sp_pts)-1):
        elements.append(line(sp_pts[i][0], sp_pts[i][1], sp_pts[i+1][0], sp_pts[i+1][1], color="#d97706", sw=2))

    for idx in [25, 60, 95]:
        p1 = sp_pts[idx]
        p2 = sp_pts[idx+2]
        elements.append(arrow(p1[0], p1[1], p2[0], p2[1], color="#b45309", sw=2))

    # FOV камери
    fov_x, fov_y = sp_pts[75]
    elements.append(rect(fov_x - 30, fov_y - 20, 60, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    elements.append(text(fov_x, fov_y + 4, "FOV", size=10, color="#b45309", bold=True))

    elements.append(text(sp_cx + 120, sp_cy - 85, "Крок витка: Δr ≤ FOV · (1 - overlap)", size=9.5, color=MUTED, bold=True))
    elements.append(text(sp_cx + 120, sp_cy - 70, "Перекриття (overlap) ≈ 20–30%", size=9.5, color=MUTED))

    elements.append(rect(465, 360, 400, 60, fill=FILL, stroke=LINE, sw=1, rx=6))
    elements.append(text(665, 380, "Закон керування підвісом / курсом дрона:", size=10, color=INK, bold=True))
    elements.append(text(665, 396, "ψ_gimbal(t) = ψ_0 + (k_s · t) · cos(ω_s · t)", size=10, color="#d97706", bold=True))
    elements.append(text(665, 411, "θ_gimbal(t) = θ_0 + (k_s · t) · sin(ω_s · t)", size=10, color="#d97706", bold=True))

    path = os.path.join(IMG_DIR, 'search-pattern-and-spatial-gating.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_target_lost_fsm()
    fig_search_pattern_and_gating()
