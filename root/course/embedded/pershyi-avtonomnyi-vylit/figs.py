#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Перший автономний виліт: страхувальний пілот, межа, план скасування»."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_roles():
    """Фігура 1: Трикутник ролей на полігоні під час автономного випробування."""
    W, H = 820, 360
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Трикутник ролей на льотному полігоні", size=16, bold=True))

    # Три основні ролі у вигляді блоків
    # 1. Оператор GCS (ліворуч)
    gcs_x, gcs_y = 170, 130
    f.append(fitbox(gcs_x - 130, gcs_y - 65, 260, 130,
                    "ОПЕРАТОР НАЗЕМНОЇ СТАНЦІЇ (GCS)\n"
                    "• Моніторинг телеметрії (HDOP, EKF, струм)\n"
                    "• Контроль виконання пунктів місії\n"
                    "• Фіксація відхилень від плану\n"
                    "• Голосовий зв'язок: інформування пілота",
                    size=12, pad=10, fill="#edf4fc", stroke=NEG))

    # 2. Страхувальний пілот (по центру / праворуч)
    pilot_x, pilot_y = 650, 130
    f.append(fitbox(pilot_x - 130, pilot_y - 65, 260, 130,
                    "СТРАХУВАЛЬНИЙ ПІЛОТ (SAFETY PILOT)\n"
                    "• Пульт RC в руках, палець на тумблері\n"
                    "• Постійний візуальний контакт з БПЛА\n"
                    "• Абсолютне право вето на автономію\n"
                    "• Негайне ручне перехоплення (Manual/Kill)",
                    size=12, pad=10, fill="#fdeeed", stroke=POS))

    # 3. Спостерігач простору (внизу по центру)
    spotter_x, spotter_y = 410, 290
    f.append(fitbox(spotter_x - 140, spotter_y - 50, 280, 100,
                    "СПОСТЕРІГАЧ ПРОСТОРУ (SPOTTER)\n"
                    "• Огляд 360°: цивільні, інші БПЛА, птахи\n"
                    "• Контроль зони посадки та вітру\n"
                    "• Голосова команда: «УВАГА!» / «СТОП!»",
                    size=12, pad=10, fill="#eef8f2", stroke=FIELD))

    # Зв'язки між ролями (стрілки та підписи)
    # GCS <-> Pilot
    f.append(arrow(gcs_x + 135, gcs_y - 15, pilot_x - 135, gcs_y - 15, color=LINE, sw=1.8))
    f.append(arrow(pilot_x - 135, gcs_y + 15, gcs_x + 135, gcs_y + 15, color=LINE, sw=1.8))
    f.append(text((gcs_x + pilot_x) / 2, gcs_y - 25, "Статус місії / Команда перехоплення", size=11, bold=True, color=INK))
    f.append(text((gcs_x + pilot_x) / 2, gcs_y + 32, "Підтвердження стану («РУЧНИЙ!»)", size=11, bold=True, color=POS))

    # Spotter -> Pilot & GCS
    f.append(arrow(spotter_x - 145, spotter_y - 20, gcs_x + 60, gcs_y + 70, color=FIELD, sw=1.6))
    f.append(text(210, 230, "Перешкоди / Вітер", size=11, color=FIELD, bold=True))

    f.append(arrow(spotter_x + 145, spotter_y - 20, pilot_x - 60, gcs_y + 70, color=FIELD, sw=1.6))
    f.append(text(610, 230, "Трафік у зоні", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "flight-test-roles.svg"), W, H, *f)


def fig_geofence():
    """Фігура 2: Геометрична модель безпеки польоту: Geofence, No-Fly Zone, RTL та Ditching Zone."""
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 26, "Геометричні межі безпеки: Geofence, RTL та аварійні зони", size=16, bold=True))

    # Зовнішня межа - Жорсткий Geofence (Inclusive)
    fence_x, fence_y, fence_w, fence_h = 50, 55, 740, 340
    f.append(rect(fence_x, fence_y, fence_w, fence_h, fill="#fdfefe", stroke=FIELD, sw=2, rx=12))
    f.append(text(fence_x + 150, fence_y + 22, "ДОЗВОЛЕНА ЗОНА (Inclusive Geofence)", size=12, bold=True, color=FIELD))
    f.append(text(fence_x + 150, fence_y + 38, "Межа відсікання: RTL / Land / Terminate", size=10, italic=True, color=MUTED))

    # Точка Home / Зліт
    home_x, home_y = 150, 310
    f.append(circle(home_x, home_y, 16, fill="#e8f4fd", stroke=NEG, sw=2))
    f.append(text(home_x, home_y + 4, "H", size=14, bold=True, color=NEG))
    f.append(text(home_x, home_y + 30, "Точка старту (HOME)", size=11, bold=True))

    # Заборонена зона (Exclusive Geofence / No-Fly Zone)
    nf_x, nf_y, nf_w, nf_h = 420, 90, 170, 110
    f.append(rect(nf_x, nf_y, nf_w, nf_h, fill="#fdeeed", stroke=POS, sw=2, rx=8))
    f.append(text(nf_x + nf_w / 2, nf_y + 45, "ЗАБОРОНЕНА ЗОНА\n(No-Fly Zone)", size=12, bold=True, color=POS))
    f.append(text(nf_x + nf_w / 2, nf_y + 80, "Будівлі / Люди / Дорога", size=10, italic=True, color=MUTED))

    # Резервна зона аварійної посадки (Ditching Zone)
    dz_x, dz_y, dz_w, dz_h = 600, 270, 160, 90
    f.append(rect(dz_x, dz_y, dz_w, dz_h, fill="#fff9e6", stroke="#d48806", sw=1.8, rx=8))
    f.append(text(dz_x + dz_w / 2, dz_y + 35, "АВАРІЙНА ЗОНА\n(Ditching Zone)", size=11, bold=True, color="#d48806"))
    f.append(text(dz_x + dz_w / 2, dz_y + 68, "Трава / безпечне поле", size=10, italic=True, color=MUTED))

    # Вейпойнти штатної місії
    wp1_x, wp1_y = 260, 220
    wp2_x, wp2_y = 330, 120
    wp3_x, wp3_y = 660, 140

    # Траєкторія місії
    f.append(arrow(home_x, home_y - 18, wp1_x - 10, wp1_y + 10, color=LINE, sw=2))
    f.append(arrow(wp1_x + 10, wp1_y - 10, wp2_x - 10, wp2_y + 10, color=LINE, sw=2))
    f.append(arrow(wp2_x + 15, wp2_y + 5, wp3_x - 15, wp3_y, color=LINE, sw=2))

    for idx, (wx, wy) in enumerate([(wp1_x, wp1_y), (wp2_x, wp2_y), (wp3_x, wp3_y)], 1):
        f.append(circle(wx, wy, 10, fill="#f4f6f8", stroke=LINE, sw=1.8))
        f.append(text(wx, wy + 4, str(idx), size=10, bold=True))
        f.append(text(wx, wy - 16, f"WP{idx}", size=11, bold=True, color=INK))

    # Траєкторія RTL при порушенні межі біля WP3
    breach_x, breach_y = 750, 140
    f.append(line(wp3_x + 10, wp3_y, breach_x, breach_y, color=POS, sw=2, dash="4,4"))
    f.append(circle(breach_x, breach_y, 8, fill="#fdeeed", stroke=POS, sw=2))
    f.append(text(breach_x - 40, breach_y - 14, "Вихід за межу!", size=10, bold=True, color=POS))

    # RTL зворотний шлях (набір висоти та політ додому)
    f.append(arrow(breach_x - 10, breach_y + 15, home_x + 20, home_y - 15, color=NEG, sw=2.2))
    f.append(text(460, 245, "Траєкторія RTL (набір безпечної висоти RTL_ALT → політ до Home)", size=11, bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "geofence-and-failsafe.svg"), W, H, *f)


def fig_decision_tree():
    """Фігура 3: Дерево рішень та ланцюг реакції на аномалії (Abort Plan)."""
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 26, "Матриця рішень: дії при виникненні аномалії в автономному польоті", size=16, bold=True))

    # Рівень 1: Виявлення аномалії
    box_root = fitbox(W / 2 - 140, 50, 280, 50, "ВИЯВЛЕННЯ АНОМАЛІЇ\n(Телеметрія GCS / Візуально пілотом)", size=12, bold=True, fill="#edf4fc", stroke=NEG)
    f.append(box_root)

    # 3 гілки: Критична загроза людині / Відхилення від курсу / Втрата лінка
    y_branch = 150

    # Гілка 1 (ліворуч): Загроза життю / Неконтрольований розгін
    b1_x = 140
    f.append(fitbox(b1_x - 110, y_branch, 220, 60, "КРИТИЧНА ЗАГРОЗА\n• Некерований рух на людей\n• Пожежа / руйнування в повітрі", size=11, bold=True, fill="#fdeeed", stroke=POS))
    f.append(arrow(W / 2 - 100, 100, b1_x + 30, y_branch, color=POS, sw=2))

    # Дія 1
    f.append(fitbox(b1_x - 110, 260, 220, 75, "АВАРІЙНЕ ЗНЕСТРУМЛЕННЯ\n(KILL SWITCH / FTS)\n• Миттєве вимкнення моторів\n• Падіння на місці / парашут", size=11, bold=True, fill="#c0392b", stroke="#900", color="#fff"))
    f.append(arrow(b1_x, y_branch + 60, b1_x, 260, color=POS, sw=2))
    f.append(text(b1_x, 370, "Пріоритет: безпека людей\nПланер приноситься в жертву", size=10, italic=True, color=MUTED))

    # Гілка 2 (по центру): Відхилення траєкторії / дрейф EKF
    b2_x = 420
    f.append(fitbox(b2_x - 120, y_branch, 240, 60, "АНОМАЛІЯ ТРАЄКТОРІЇ\n• Crosstrack > 15 м, дрейф EKF\n• Розгойдування (хитавиця PID)", size=11, bold=True, fill="#fff9e6", stroke="#d48806"))
    f.append(arrow(W / 2, 100, b2_x, y_branch, color="#d48806", sw=2))

    # Дія 2
    f.append(fitbox(b2_x - 120, 260, 240, 75, "РУЧНЕ ПЕРЕХОПЛЕННЯ\n(MANUAL TAKEOVER)\n• Тумблер в STABILIZE / POSHOLD\n• Пілот вирівнює апарат вручну", size=11, bold=True, fill="#e8f4fd", stroke=NEG))
    f.append(arrow(b2_x, y_branch + 60, b2_x, 260, color=NEG, sw=2))
    f.append(text(b2_x, 370, "Посадка в аварійній зоні\nабо повернення на базу", size=10, italic=True, color=MUTED))

    # Гілка 3 (праворуч): Втрата зв'язку / Просідання батареї
    b3_x = 700
    f.append(fitbox(b3_x - 110, y_branch, 220, 60, "ВТРАТА ЗВ'ЯЗКУ / ЖИВЛЕННЯ\n• Обрив RC або GCS лінка\n• Поріг розряду Battery Warn", size=11, bold=True, fill="#eef8f2", stroke=FIELD))
    f.append(arrow(W / 2 + 100, 100, b3_x - 30, y_branch, color=FIELD, sw=2))

    # Дія 3
    f.append(fitbox(b3_x - 110, 260, 220, 75, "АВТОМАТИЧНИЙ FAILSAFE\n(RTL / AUTO LAND)\n• Набір безпечної висоти\n• Автоматичний політ додому", size=11, bold=True, fill="#eafaf0", stroke=FIELD))
    f.append(arrow(b3_x, y_branch + 60, b3_x, 260, color=FIELD, sw=2))
    f.append(text(b3_x, 370, "Автоматика відновлює контроль\nабо безпечно саджає", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "abort-decision-tree.svg"), W, H, *f)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_roles()
    fig_geofence()
    fig_decision_tree()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
