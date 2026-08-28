#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми avtoposadka (sys-dron).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_landing_phases_profile():
    """Фігура 1: Вертикальний профіль автопосадки: етапи зниження, зміна швидкості та контакт."""
    w, h = 840, 420
    frags = []

    # Смуга ґрунту внизу
    frags.append(rect(0, 360, w, 60, fill="#e5e7eb", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(120, 395, "Поверхня землі (Z = 0 м)", size=12, color=MUTED, bold=True))

    # Зона екранного ефекту (Ground Effect Zone, h < 1.2 м)
    frags.append(rect(60, 315, 750, 45, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    frags.append(text(270, 335, "Зона екранного ефекту (h < 1.2 м): подушка тиску, баро-шум", size=10, color="#92400e", bold=True))

    # Вертикальна шкала висоти зліва
    frags.append(line(50, 50, 50, 360, color=LINE, sw=1.5))
    frags.append(arrow(50, 360, 50, 40, color=LINE, sw=1.5))
    frags.append(text(50, 35, "Висота h (м)", size=11, color=INK, bold=True))

    # Позначки висоти
    frags.append(line(45, 70, 55, 70, color=LINE, sw=1.0))
    frags.append(text(35, 74, "30", size=10, color=MUTED, anchor="end"))
    frags.append(line(45, 160, 55, 160, color=LINE, sw=1.0))
    frags.append(text(35, 164, "15", size=10, color=MUTED, anchor="end"))
    frags.append(line(45, 260, 55, 260, color=LINE, sw=1.0))
    frags.append(text(35, 264, "5", size=10, color=MUTED, anchor="end"))
    frags.append(line(45, 315, 55, 315, color=LINE, sw=1.0))
    frags.append(text(35, 319, "1.2", size=10, color=MUTED, anchor="end"))
    frags.append(line(45, 360, 55, 360, color=LINE, sw=1.0))
    frags.append(text(35, 364, "0", size=10, color=MUTED, anchor="end"))

    # Фазові вертикальні роздільники (пунктир)
    frags.append(line(260, 60, 260, 360, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(480, 60, 480, 360, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(670, 60, 670, 360, color=MUTED, sw=1.0, dash="4,4"))

    # Заголовки фаз вгорі
    b1, _, _ = textbox(155, 65, "1. Швидкий спуск\n(Fast Descent)\nVz = -2.0 м/с", size=10, pad=5, fill="#eff6ff", stroke=NEG)
    frags.append(b1)

    b2, _, _ = textbox(370, 65, "2. Гальмування й підкрадання\n(Slow Touchdown Approach)\nVz = -0.5 м/с", size=10, pad=5, fill="#f0fdf4", stroke=FIELD)
    frags.append(b2)

    b3, _, _ = textbox(575, 65, "3. Детект контакту\n(Ground Contact Confirm)\nТаймаут 1.0-1.5 с", size=10, pad=5, fill="#fef2f2", stroke=POS)
    frags.append(b3)

    b4, _, _ = textbox(750, 65, "4. Розброєння\n(Auto-Disarm)\nЗупинка ШІМ", size=10, pad=5, fill="#f3f4f6", stroke=LINE)
    frags.append(b4)

    # Крива траєкторії спуску дрона (відрізки)
    frags.append(line(80, 80, 260, 260, color=NEG, sw=2.5))
    frags.append(line(260, 260, 350, 300, color=FIELD, sw=2.5))
    frags.append(line(350, 300, 530, 360, color=FIELD, sw=2.5))
    frags.append(line(530, 360, 800, 360, color=LINE, sw=2.5))

    # Точки на кривій траєкторії
    frags.append(circle(80, 80, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(text(95, 95, "Початок посадки", size=9, color=NEG, bold=True, anchor="start"))

    frags.append(circle(260, 260, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    frags.append(text(275, 255, "h = LAND_ALT_LOW (5 м)", size=9, color=FIELD, bold=True, anchor="start"))

    frags.append(circle(530, 360, 6, fill=POS, stroke="#ffffff", sw=2.0))
    frags.append(text(545, 350, "Торкання (Touchdown)", size=10, color=POS, bold=True, anchor="start"))

    frags.append(circle(670, 360, 6, fill=LINE, stroke="#ffffff", sw=2.0))
    frags.append(text(685, 350, "Landed -> Disarmed", size=10, color=LINE, bold=True, anchor="start"))

    # Інформаційні блоки параметрів знизу
    b_ge, _, _ = textbox(370, 210, "Зниження швидкості:\n• Гасіння кінетичної енергії\n• Захист від VRS\n• Блокування баро-шуму", size=9, pad=5, fill="#ffffff", stroke=FIELD)
    frags.append(b_ge)

    b_trig, _, _ = textbox(590, 230, "Критерії детекту землі:\n• Тяга < 25% від висіння\n• Швидкість |Vz| < 0.15 м/с\n• Акселерометр: сплеск az\n• Обнулення I-термів PID", size=9, pad=5, fill="#ffffff", stroke=POS)
    frags.append(b_trig)

    # Дрон іконка в точці торкання
    frags.append(rect(515, 348, 30, 8, fill="#374151", stroke="none", rx=2))
    frags.append(line(505, 346, 555, 346, color="#111827", sw=2.0))
    frags.append(line(518, 356, 512, 360, color="#111827", sw=1.5))
    frags.append(line(542, 356, 548, 360, color="#111827", sw=1.5))

    render(os.path.join(IMG_DIR, "landing-phases-profile.svg"), w, h, *frags,
           title="Вертикальний профіль автопосадки та фази детектування землі")


def fig_ground_detector_fsm():
    """Фігура 2: Граф станів скінченного автомата детектування землі (Ground Detector FSM)."""
    w, h = 840, 400
    frags = []

    # Стан 1: IN_AIR (У повітрі)
    b_air, _, _ = textbox(120, 130, "IN_AIR\n(У повітрі)\nМотори активні\nСпуск Vz_cmd < 0", size=11, pad=8, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b_air)

    # Стан 2: GROUND_CONTACT (Торкання ґрунту)
    b_contact, _, _ = textbox(370, 130, "GROUND_CONTACT\n(Первинний контакт)\nПадіння тяги < Thr_min\n|Vz| < 0.15 м/с, az сплеск", size=11, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_contact)

    # Стан 3: MAYBE_LANDED (Підтвердження контакту)
    b_maybe, _, _ = textbox(630, 130, "MAYBE_LANDED\n(Очікування стійкості)\nТаймер persistence t > 0.5 с\nЗаморожування I-термів", size=11, pad=8, fill="#fef2f2", stroke=POS, bold=True)
    frags.append(b_maybe)

    # Стан 4: LANDED (Посадку зафіксовано)
    b_landed, _, _ = textbox(630, 310, "LANDED\n(Землю зафіксовано)\nt_landed > 1.0 с\nRamp-down газу до 0", size=11, pad=8, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b_landed)

    # Стан 5: DISARMED (Розброєно)
    b_disarm, _, _ = textbox(240, 310, "DISARMED\n(Мотори зупинено)\nШІМ вимкнено\nЗавершення місії", size=11, pad=8, fill="#f3f4f6", stroke=LINE, bold=True)
    frags.append(b_disarm)

    # Прямі стрілки переходів (Головна гілка)
    # IN_AIR -> GROUND_CONTACT
    frags.append(arrow(190, 130, 275, 130, color=LINE, sw=2.0))
    frags.append(text(232, 115, "Тяга мала + Vz ~ 0", size=9, color=MUTED, bold=True))

    # GROUND_CONTACT -> MAYBE_LANDED
    frags.append(arrow(465, 130, 535, 130, color=LINE, sw=2.0))
    frags.append(text(500, 115, "Контакт триває", size=9, color=MUTED, bold=True))

    # MAYBE_LANDED -> LANDED
    frags.append(arrow(630, 185, 630, 265, color=FIELD, sw=2.5))
    frags.append(text(640, 225, "t_confirm >= 1.0 с", size=10, color=FIELD, bold=True, anchor="start"))

    # LANDED -> DISARMED
    frags.append(arrow(535, 310, 335, 310, color=POS, sw=2.5))
    frags.append(text(435, 295, "Auto-disarm timeout (0.5-1.0 с)", size=10, color=POS, bold=True))

    # Зворотні стрілки (Відкати при хибному спрацьовуванні чи відриві)
    # GROUND_CONTACT -> IN_AIR (Підстрибування / відрив)
    frags.append(line(370, 185, 370, 220, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(370, 220, 120, 220, color=NEG, sw=1.5, dash="4,3"))
    frags.append(arrow(120, 220, 120, 185, color=NEG, sw=1.5))
    frags.append(text(245, 235, "Відрив: ріст Vz або зростання газу -> Скидання в IN_AIR", size=9, color=NEG))

    # MAYBE_LANDED -> IN_AIR (Порив вітру / перекидання)
    frags.append(line(725, 130, 780, 130, color=POS, sw=1.5, dash="4,3"))
    frags.append(line(780, 130, 780, 60, color=POS, sw=1.5, dash="4,3"))
    frags.append(line(780, 60, 120, 60, color=POS, sw=1.5, dash="4,3"))
    frags.append(arrow(120, 60, 120, 85, color=POS, sw=1.5))
    frags.append(text(450, 52, "Сплеск кутової швидкості або ріст висоти -> Аварійне скидання в IN_AIR", size=9, color=POS))

    render(os.path.join(IMG_DIR, "ground-detector-fsm.svg"), w, h, *frags,
           title="Граф станів автомата детектування землі (Ground Detector FSM)")


if __name__ == "__main__":
    fig_landing_phases_profile()
    fig_ground_detector_fsm()
    print("SVG generated successfully in %s" % IMG_DIR)
