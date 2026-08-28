# -*- coding: utf-8 -*-
"""Фігури до статті «Автомат цілей: стани, переходи, охоронні умови» (sys-dron/avtomat-tsilei).
Запуск: python figs.py  ->  ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Архітектура місійного керування ──────────────────────────────────────
def fig_target_fsm_architecture():
    W, H = 860, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Архітектура трирівневого місійного керування БПЛА", size=16, bold=True))

    # 1. Верхній шар: Сенсорно-перцептивний стек
    f.append(rect(25, 55, 810, 95, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(430, 75, "ПЕРЦЕПТИВНИЙ ТА ТЕЛЕМЕТРИЧНИЙ ШАР (Perception & Telemetry)", size=12, bold=True, color=INK))

    b_cam = fitbox(40, 90, 175, 46, "Оптична камера / CV\n(детекція, bbox, трекер)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    b_gnss = fitbox(230, 90, 185, 46, "GNSS / EKF3 стек\n(позиція, 3D Fix, HDOP)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    b_bms = fitbox(430, 90, 185, 46, "BMS / Монітор батареї\n(напруга, струм, SoC %)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    b_rng = fitbox(630, 90, 185, 46, "Лазерний далекомір\n(висота AGL, дистанція)", size=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    f.extend([b_cam, b_gnss, b_bms, b_rng])

    # Стрілки передачі подій вниз
    f.append(arrow(127, 150, 127, 180, color=MUTED, sw=1.5))
    f.append(arrow(322, 150, 322, 180, color=MUTED, sw=1.5))
    f.append(arrow(522, 150, 522, 180, color=MUTED, sw=1.5))
    f.append(arrow(722, 150, 722, 180, color=MUTED, sw=1.5))

    # 2. Середній шар: Місійний автомат цілей (High-Level Goal HSM)
    f.append(rect(25, 180, 810, 155, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(430, 202, "МІСІЙНИЙ АВТОМАТ ЦІЛЕЙ (High-Level Mission Goal HSM)", size=13, bold=True, color=NEG))

    b_eval = fitbox(45, 220, 225, 95, "Оцінювач Guard-умов\n• Енергетичний баланс RTB\n• Достовірність цілі (NIS, Conf)\n• Геозона та радіус зв'язку", size=10, fill="#ffffff", stroke=NEG, sw=1.4)
    b_hsm = fitbox(290, 220, 260, 95, "Диспетчер станів HSM\n• Пошук (Grid/Boustrophedon)\n• Супроводження (Visual/Target)\n• Активація корисного навантаження\n• Збереження історії (Shallow/Deep)", size=10, fill="#ffffff", stroke=NEG, sw=1.5)
    b_arb = fitbox(570, 220, 245, 95, "Арбітр стратегічних цілей\n• Пріоритезація цілей у кадрі\n• Тайм-аути втрати треку\n• Failsafe-преемпція місії", size=10, fill="#ffffff", stroke=NEG, sw=1.4)
    f.extend([b_eval, b_hsm, b_arb])

    # Зв'язки всередині HSM
    f.append(arrow(270, 268, 290, 268, color=NEG, sw=1.4))
    f.append(arrow(550, 268, 570, 268, color=NEG, sw=1.4))

    # Стрілки команд вниз
    f.append(arrow(430, 335, 430, 365, color=FIELD, sw=2.0))
    f.append(text(555, 352, "Стратегічні цілі: WP, Loiter, Setpoint NED", size=10, color=FIELD, bold=True))

    # 3. Нижній шар: Навігація та польотний контролер
    f.append(rect(25, 365, 810, 115, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(430, 385, "НИЖНІЙ ШАР: ПОЛЬОТНИЙ КОНТРОЛЕР ТА АВТОМАТ РЕЖИМІВ", size=12, bold=True, color=FIELD))

    b_nav = fitbox(45, 405, 235, 60, "Навігаційний планувач\n(NPFG / L1 генератор траєкторій)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2)
    b_modes = fitbox(305, 405, 230, 60, "Автомат режимів польоту\n(AUTO, GUIDED, POS_HOLD, RTL)", size=10, fill="#ffffff", stroke=FIELD, sw=1.4)
    b_ctrl = fitbox(560, 405, 255, 60, "Контур стабілізації та актуатори\n(ПІД положення/кутів -> ESC/серво)", size=10, fill="#ffffff", stroke=FIELD, sw=1.2)
    f.extend([b_nav, b_modes, b_ctrl])

    # Зв'язки в нижньому шарі
    f.append(arrow(280, 435, 305, 435, color=FIELD, sw=1.4))
    f.append(arrow(535, 435, 560, 435, color=FIELD, sw=1.4))

    # Коментар унизу
    f.append(rect(25, 490, 810, 22, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(430, 505, "Місійний автомат оперує високорівневими задачами й транслює їх у команди навігаційному контролеру.", size=10, color=INK))

    render(os.path.join(IMG, "target-fsm-architecture.svg"), W, H, *f)


# ── 2. Граф переходів та Statechart HSM ─────────────────────────────────────
def fig_target_hsm_statechart():
    W, H = 880, 540
    f = []

    # Заголовок
    f.append(text(W / 2, 26, "Ієрархічний автомат місії: стани, події та охоронні умови", size=15, bold=True))

    # 1. Суперстан OPERATIONAL
    f.append(rect(20, 50, 565, 435, fill="#f8fafc", stroke=NEG, sw=1.6, rx=10))
    f.append(text(160, 72, "СУПЕРСТАН: OPERATIONAL", size=12, bold=True, color=NEG))

    # Значок історії H
    f.append(circle(555, 72, 12, fill="#eff6ff", stroke=NEG, sw=1.4))
    f.append(text(555, 76, "H", size=11, bold=True, color=NEG))

    # Підстани всередині OPERATIONAL
    # IDLE
    b_idle = fitbox(35, 95, 140, 42, "IDLE\n(очікування старту)", size=10, fill="#ffffff", stroke=MUTED, sw=1.4)
    # SEARCH
    b_search = fitbox(35, 185, 140, 48, "SEARCH\n(пошуковий патерн)", size=10, fill="#ffffff", stroke=NEG, sw=1.6)
    # ACQUIRE
    b_acq = fitbox(215, 185, 155, 48, "ACQUIRE\n(верифікація об'єкта)", size=10, fill="#ffffff", stroke=NEG, sw=1.6)
    # TRACK
    b_track = fitbox(405, 185, 160, 48, "TRACK\n(перехоплення/супровід)", size=10, fill="#ffffff", stroke=FIELD, sw=1.8)
    # ENGAGE
    b_eng = fitbox(405, 305, 160, 48, "ENGAGE\n(скид / дія на цілі)", size=10, fill="#ffffff", stroke=POS, sw=1.8)
    # VERIFY
    b_ver = fitbox(215, 305, 155, 48, "VERIFY\n(оцінка результату)", size=10, fill="#ffffff", stroke=FIELD, sw=1.5)

    f.extend([b_idle, b_search, b_acq, b_track, b_eng, b_ver])

    # Стрілка початкового входу
    f.append(circle(45, 116, 5, fill=INK, stroke=INK))

    # Переходи в OPERATIONAL
    # IDLE -> SEARCH
    f.append(arrow(105, 137, 105, 185, color=NEG, sw=1.5))
    f.append(text(145, 160, "[EV_START]", size=9, color=MUTED))

    # SEARCH -> ACQUIRE
    f.append(arrow(175, 209, 215, 209, color=NEG, sw=1.5))
    f.append(text(195, 198, "[CANDIDATE]", size=9, color=NEG))

    # ACQUIRE -> TRACK
    f.append(arrow(370, 209, 405, 209, color=FIELD, sw=1.6))
    f.append(text(388, 198, "[CONFIRMED]", size=9, color=FIELD))

    # ACQUIRE -> SEARCH (відхилення)
    f.append(arrow(240, 233, 150, 233, color=MUTED, sw=1.3))
    f.append(text(195, 246, "[FALSE_ALARM]", size=9, color=MUTED))

    # TRACK -> ENGAGE
    f.append(arrow(485, 233, 485, 305, color=POS, sw=1.6))
    f.append(text(540, 268, "[IN_RANGE / Armed]", size=9, color=POS))

    # TRACK -> SEARCH (втрата цілі за тайм-аутом)
    f.append(arrow(440, 233, 140, 305, color=MUTED, sw=1.3))
    f.append(text(285, 275, "[TARGET_LOST: t > 3s]", size=9, color=MUTED))

    # ENGAGE -> VERIFY
    f.append(arrow(405, 329, 370, 329, color=FIELD, sw=1.5))
    f.append(text(388, 320, "[DONE]", size=9, color=FIELD))

    # VERIFY -> SEARCH
    f.append(arrow(215, 329, 105, 233, color=NEG, sw=1.4))
    f.append(text(140, 345, "[NEXT_TARGET]", size=9, color=NEG))

    # 2. Суперстан RECOVERY & FAILSAFE
    f.append(rect(610, 50, 250, 435, fill="#fef2f2", stroke=POS, sw=1.6, rx=10))
    f.append(text(735, 72, "СУПЕРСТАН: RECOVERY", size=12, bold=True, color=POS))

    b_rtb = fitbox(635, 120, 200, 46, "RTB (Return to Base)\n(повернення на висоті)", size=10, fill="#ffffff", stroke=POS, sw=1.6)
    b_loit = fitbox(635, 220, 200, 46, "LOITER_HOME\n(очікування над базою)", size=10, fill="#ffffff", stroke=POS, sw=1.5)
    b_land = fitbox(635, 320, 200, 46, "AUTOLAND\n(автопосадка з детекцією)", size=10, fill="#ffffff", stroke=POS, sw=1.6)
    b_term = fitbox(635, 415, 200, 44, "ABORT / TERMINATION\n(екстрене припинення)", size=10, fill="#ffffff", stroke=POS, sw=1.8)

    f.extend([b_rtb, b_loit, b_land, b_term])

    # Внутрішні переходи RECOVERY
    f.append(arrow(735, 166, 735, 220, color=POS, sw=1.4))
    f.append(text(785, 193, "[HOME_REACHED]", size=9, color=POS))

    f.append(arrow(735, 266, 735, 320, color=POS, sw=1.4))
    f.append(text(785, 293, "[TIMEOUT / CMD]", size=9, color=POS))

    # Преемптивні переходи з OPERATIONAL в RECOVERY
    # Зверху: Bat Low / Link Loss
    f.append(arrow(585, 140, 635, 140, color=POS, sw=1.8))
    f.append(text(610, 128, "[EV_BAT_LOW / Guard]", size=9, color=POS, anchor="middle"))

    # Знизу: Geofence Breach -> ABORT
    f.append(arrow(585, 425, 635, 425, color=POS, sw=1.8))
    f.append(text(610, 413, "[EV_GEOFENCE_BREACH]", size=9, color=POS, anchor="middle"))

    # Пояснення знизу
    f.append(rect(20, 495, 840, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(440, 514, "Групування в суперстани запобігає вибуху кількості переходів: загальні тригери Failsafe обробляються на рівні суперстану.", size=10, color=INK))

    render(os.path.join(IMG, "target-hsm-statechart.svg"), W, H, *f)


if __name__ == "__main__":
    fig_target_fsm_architecture()
    fig_target_hsm_statechart()
    print("OK: generated SVGs in img/")
