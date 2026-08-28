# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Запуск і посадка без смуги'."""

import sys
import os

# Імпортуємо спільний набір svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_launch_modes():
    """Схема способів старту без смуги: рука, банджі-катапульта, пневматична рейка."""
    W, H = 840, 420
    frags = []

    # Заголовок секцій
    frags.append(rect(10, 10, 260, 395, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(rect(290, 10, 260, 395, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(rect(570, 10, 260, 395, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    # 1. Старт з руки
    frags.append(text(140, 35, "1. Старт з руки (Hand Launch)", size=14, bold=True, color=INK))
    # Малюнок руки та літака
    frags.append(line(50, 220, 100, 180, color=LINE, sw=3)) # Рука
    frags.append(circle(50, 220, 10, fill="#e2e8f0", stroke=LINE, sw=2)) # Плече
    frags.append(circle(100, 180, 7, fill="#fed7aa", stroke=LINE, sw=2)) # Кисть

    # Фюзеляж літака під кутом 15 градусів
    frags.append(line(80, 185, 170, 155, color=NEG, sw=4)) # Фюзеляж
    frags.append(line(110, 195, 140, 145, color=NEG, sw=6)) # Крило
    frags.append(circle(80, 185, 8, fill="#fee2e2", stroke=POS, sw=1.5)) # Точка небезпеки (гвинт позаду)

    # Вектор кидка
    frags.append(arrow(100, 175, 190, 145, color=FIELD, sw=2.5))
    frags.append(text(195, 135, "V_throw = 10-12 м/с", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(195, 150, "Кут pitch = 12°-18°", size=11, color=MUTED, anchor="start"))

    # Небезпечна зона
    frags.append(line(40, 160, 75, 185, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(75, 235, "Штовхаючий гвинт: небезпека", size=11, color=POS, bold=True, anchor="middle"))
    frags.append(text(75, 250, "Затримка газу 200-400 мс", size=10, color=MUTED, anchor="middle"))

    # Інфобокс параметрів
    box_t1, _, _ = textbox(140, 335, "Маса: до 2.5-3.5 кг\nV_stall: до 10-11 м/с\nПеревантаження: 1.5g-2.5g\nТяга підхоплення: T/W > 0.4", size=11, pad=8, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_t1)

    # 2. Гумовий джгут (Банджі)
    frags.append(text(420, 35, "2. Гумовий джгут (Bungee)", size=14, bold=True, color=INK))
    # Рейка
    frags.append(line(310, 240, 520, 150, color=LINE, sw=3))
    frags.append(line(310, 240, 310, 260, color=MUTED, sw=2)) # Опора 1
    frags.append(line(520, 150, 520, 260, color=MUTED, sw=2)) # Опора 2
    frags.append(line(300, 260, 540, 260, color="#94a3b8", sw=2)) # Земля

    # Гумовий шнур
    frags.append(line(330, 230, 480, 255, color=POS, sw=2.5, dash="4,2")) # Кілок у землі
    frags.append(line(480, 255, 480, 275, color=POS, sw=3)) # Анкер
    frags.append(text(480, 290, "Кілок-анкер", size=10, color=POS, anchor="middle"))

    # Каретка з літаком
    frags.append(rect(370, 205, 30, 12, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=2))
    frags.append(line(365, 205, 415, 185, color=NEG, sw=3))
    frags.append(arrow(400, 195, 460, 170, color=FIELD, sw=2.5))
    frags.append(text(440, 155, "F_гуми = k·Δx", size=11, color=FIELD, bold=True, anchor="middle"))

    box_t2, _, _ = textbox(420, 335, "Маса: 3-8 кг\nV_stall: 12-16 м/с\nПеревантаження: 3g-5g\nДовжина рейки: 2.5-3.5 м", size=11, pad=8, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_t2)

    # 3. Пневматична катапульта
    frags.append(text(700, 35, "3. Пневматична рейка (Pneumatic)", size=14, bold=True, color=INK))
    # Рейка з циліндром
    frags.append(line(590, 235, 800, 145, color=LINE, sw=4))
    frags.append(rect(600, 240, 60, 25, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=3)) # Ресивер
    frags.append(text(630, 256, "P = 8 бар", size=10, color=INK, bold=True, anchor="middle"))

    # Трос поліспаста
    frags.append(line(660, 250, 770, 160, color=MUTED, sw=1.5, dash="2,2"))
    # Літак на каретці
    frags.append(rect(680, 185, 35, 14, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=2))
    frags.append(line(675, 185, 735, 160, color=NEG, sw=4))
    frags.append(arrow(715, 170, 785, 140, color=FIELD, sw=2.5))
    frags.append(text(760, 130, "V_вихід > 20 м/с", size=11, color=FIELD, bold=True, anchor="middle"))

    box_t3, _, _ = textbox(700, 335, "Маса: 8-25+ кг\nV_stall: 16-22 м/с\nПеревантаження: 5g-8g\nТиск циліндра: 6-10 бар", size=11, pad=8, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_t3)

    render(os.path.join(IMG_DIR, "launch-modes.svg"), W, H, *frags)


def fig_catapult_dynamics():
    """Динаміка розгону на рейці катапульти: прискорення, швидкість і шлях."""
    W, H = 820, 380
    frags = []

    # Сітка та осі координат
    frags.append(rect(60, 40, 700, 280, fill="#fcfdfe", stroke="#e2e8f0", rx=4))

    # Вісь X (час t, 0 до 0.4 с або дистанція по рейці)
    frags.append(line(100, 280, 720, 280, color=LINE, sw=2))
    frags.append(text(720, 305, "Час руху по рейці t (с)", size=12, color=INK, anchor="end", bold=True))

    # Ліва вісь Y: Прискорення a (g)
    frags.append(line(100, 280, 100, 50, color=POS, sw=2))
    frags.append(text(90, 50, "Прискорення a (g)", size=12, color=POS, anchor="end", bold=True))

    # Права вісь Y: Швидкість V (м/с)
    frags.append(line(720, 280, 720, 50, color=NEG, sw=2))
    frags.append(text(730, 50, "Швидкість V (м/с)", size=12, color=NEG, anchor="start", bold=True))

    # Відмітки по осях
    for i, t_val in enumerate(["0.0", "0.1", "0.2", "0.3", "0.4"]):
        x_pos = 100 + i * 140
        frags.append(line(x_pos, 280, x_pos, 285, color=LINE, sw=1.5))
        frags.append(text(x_pos, 300, t_val, size=11, color=MUTED, anchor="middle"))
        if i > 0:
            frags.append(line(x_pos, 280, x_pos, 60, color="#f1f5f9", sw=1, dash="2,2"))

    # Відмітки прискорення (ліворуч)
    for i, g_val in enumerate(["0g", "2g", "4g", "6g"]):
        y_pos = 280 - i * 65
        frags.append(line(95, y_pos, 100, y_pos, color=POS, sw=1.5))
        frags.append(text(90, y_pos + 4, g_val, size=11, color=POS, anchor="end"))

    # Відмітки швидкості (праворуч)
    for i, v_val in enumerate(["0", "6", "12", "18", "24"]):
        y_pos = 280 - i * 50
        frags.append(line(720, y_pos, 725, y_pos, color=NEG, sw=1.5))
        frags.append(text(730, y_pos + 4, v_val, size=11, color=NEG, anchor="start"))

    # Крива прискорення a(t) для гумового джгута: пік на старті (6g), потім спадання до 1.5g
    frags.append('<path d="M 100 85 Q 180 120 380 200 T 520 230" fill="none" stroke="%s" stroke-width="3.5"/>' % POS)
    frags.append(text(190, 85, "Пікове перевантаження a_peak ≈ 6g", size=11, color=POS, bold=True))

    # Крива швидкості V(t): від 0 до 18 м/с на виході (t=0.3 с)
    frags.append('<path d="M 100 280 Q 240 180 380 135 T 520 130" fill="none" stroke="%s" stroke-width="3.5"/>' % NEG)
    frags.append(text(540, 115, "V_launch = 18 м/с (> 1.2·V_stall)", size=12, color=NEG, bold=True, anchor="start"))

    # Лінія V_stall
    frags.append(line(100, 163, 720, 163, color="#e11d48", sw=1.5, dash="5,4"))
    frags.append(text(650, 155, "Поріг звалювання V_stall = 14 м/с", size=11, color="#e11d48", bold=True, anchor="end"))

    # Вертикальна лінія відриву з каретки (t = 0.3 с)
    frags.append(line(520, 280, 520, 60, color=FIELD, sw=2, dash="4,3"))
    frags.append(text(525, 75, "Схід з рейки (L_rail = 3.0 м)", size=11, color=FIELD, bold=True, anchor="start"))

    # Інформаційна плашка знизу
    box_info, _, _ = textbox(410, 350, "Імпульсний розгін: захист батареї від поздовжнього зсуву, IMU перемикається в діапазон ±16g", size=11, pad=6, fill="#f8fafc", stroke="#94a3b8")
    frags.append(box_info)

    render(os.path.join(IMG_DIR, "catapult-dynamics.svg"), W, H, *frags)


def fig_belly_landing_flare():
    """Профіль посадки на черево: глісада, вирівнювання (flare), зупинка пропелера та дотик."""
    W, H = 840, 360
    frags = []

    # Земля (трава/ґрунт)
    frags.append(rect(40, 280, 760, 40, fill="#f0fdf4", stroke="#86efac", rx=4))
    frags.append(line(40, 280, 800, 280, color=FIELD, sw=3))
    frags.append(text(420, 305, "Поверхня ґрунту / трава (тертя по днищу фюзеляжу)", size=12, color="#166534", anchor="middle", bold=True))

    # Траєкторія зниження (Approach -> Flare -> Touchdown -> Slide)
    frags.append('<path d="M 60 70 L 380 230 Q 480 270 560 276 L 760 278" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="6,3"/>' % NEG)

    # 1. Етап підходу (Approach)
    frags.append(circle(160, 120, 6, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(line(140, 110, 180, 130, color=INK, sw=3)) # Силует літака з тангажем вниз
    frags.append(text(160, 85, "1. Глісада (Approach)", size=12, bold=True, color=INK))
    frags.append(text(160, 100, "Кут γ = 3°-5°, V = 1.3·V_stall", size=10, color=MUTED))

    # 2. Етап вирівнювання (Flare)
    frags.append(circle(450, 255, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(line(430, 260, 470, 250, color=INK, sw=3)) # Силует з піднятим носом
    frags.append(text(450, 185, "2. Вирівнювання (Flare, h = 1.0-1.5 м)", size=12, bold=True, color=POS))
    frags.append(text(450, 200, "Тангаж pitch = +5°...+8°", size=10, color=MUTED))
    frags.append(text(450, 215, "Гасіння V_z до < 0.4 м/с", size=10, color=MUTED))

    # Стрілка відсічення газу
    frags.append(arrow(370, 180, 420, 230, color=POS, sw=2))
    frags.append(text(330, 170, "Вимкнення тяги + Гальмо ESC", size=11, color=POS, bold=True))

    # 3. Складання лопатей (Folding prop)
    frags.append(circle(560, 276, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(text(560, 235, "3. Дотик (Touchdown)", size=12, bold=True, color=FIELD))
    frags.append(text(560, 250, "Лопаті складені вздовж корпусу", size=10, color=MUTED))

    # 4. Пробіг / Ковзання (Ground Slide)
    frags.append(arrow(580, 270, 740, 270, color=LINE, sw=2))
    frags.append(text(660, 255, "4. Ковзання на лижі (L_slide ≈ 5-15 м)", size=11, color=INK, bold=True, anchor="middle"))

    # Позначення висоти вирівнювання
    frags.append(line(480, 280, 480, 230, color=LINE, sw=1.5, dash="2,2"))
    frags.append(text(495, 255, "h_flare", size=11, color=INK, italic=True))

    render(os.path.join(IMG_DIR, "belly-landing-flare.svg"), W, H, *frags)


def fig_net_and_parachute():
    """Схеми посадки в сітку (Net recovery) та на парашуті."""
    W, H = 840, 380
    frags = []

    # Ліва половина: Посадка в сітку
    frags.append(rect(10, 10, 400, 355, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(210, 35, "А. Вловлювання в сітку (Net Recovery)", size=14, bold=True, color=INK))

    # Стійки сітки та сітка
    frags.append(line(300, 70, 300, 270, color=LINE, sw=5)) # Стійка 1
    frags.append(line(360, 90, 360, 290, color=LINE, sw=5)) # Стійка 2
    # Сітка (сітка ліній)
    for y in range(80, 270, 20):
        frags.append(line(300, y, 360, y + 20, color="#64748b", sw=1.5))
    for x in range(300, 360, 12):
        frags.append(line(x, 70 + (x-300)/3, x, 270 + (x-300)/3, color="#64748b", sw=1.5))

    # Літак, що летить у сітку
    frags.append(line(80, 180, 210, 180, color=NEG, sw=4)) # Фюзеляж
    frags.append(line(140, 120, 140, 240, color=NEG, sw=6)) # Крило з лонжероном
    frags.append(arrow(170, 180, 260, 180, color=FIELD, sw=2.5))
    frags.append(text(210, 165, "V_approach = 15 м/с", size=11, color=FIELD, bold=True, anchor="middle"))

    # Позначення навантаження на лонжерон
    frags.append(circle(140, 140, 8, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(circle(140, 220, 8, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(140, 255, "Згинальний удар по лонжерону (до 10g)", size=10, color=POS, bold=True, anchor="middle"))

    box_net, _, _ = textbox(210, 320, "Точність заходу: RTK GNSS / оптичний маркер ±0.8 м\nАмортизація: гальмівні троси з поліспастом", size=10.5, pad=6, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_net)

    # Права половина: Посадка на парашуті
    frags.append(rect(430, 10, 400, 355, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(630, 35, "Б. Парашутний спуск (Parachute)", size=14, bold=True, color=INK))

    # Купол парашута
    frags.append('<path d="M 540 100 Q 630 40 720 100 Z" fill="#fed7aa" stroke="%s" stroke-width="2"/>' % POS)
    # Стропи
    frags.append(line(540, 100, 630, 170, color=MUTED, sw=1.5))
    frags.append(line(600, 100, 630, 170, color=MUTED, sw=1.5))
    frags.append(line(660, 100, 630, 170, color=MUTED, sw=1.5))
    frags.append(line(720, 100, 630, 170, color=MUTED, sw=1.5))

    # Вузол підвісу та фали до літака (2-точкова підвіска)
    frags.append(circle(630, 170, 4, fill=POS, stroke=LINE, sw=1.5))
    frags.append(line(630, 170, 590, 220, color=LINE, sw=2)) # Передній фал
    frags.append(line(630, 170, 670, 225, color=LINE, sw=2)) # Задній фал

    # Літак у горизонтальному / злегка хвостовому положенні
    frags.append(line(570, 215, 690, 230, color=NEG, sw=4)) # Фюзеляж під невеликим кутом
    frags.append(circle(620, 222, 5, fill=FIELD, stroke=LINE, sw=1.5)) # Центр ваги CG
    frags.append(text(620, 242, "CG", size=10, color=FIELD, bold=True, anchor="middle"))

    # Вектор вертикальної швидкості
    frags.append(arrow(720, 190, 720, 240, color=POS, sw=2))
    frags.append(text(730, 215, "V_descent ≈ 3.5-5.0 м/с", size=10.5, color=POS, bold=True, anchor="start"))

    box_para, _, _ = textbox(630, 320, "Вимкнення мотора (throttle=0) при викиді\nКут тангажу при дотику: +3°...+5° (на хвіст)", size=10.5, pad=6, fill="#ffffff", stroke="#94a3b8")
    frags.append(box_para)

    render(os.path.join(IMG_DIR, "net-and-parachute.svg"), W, H, *frags)


def fig_takeoff_landing_fsm():
    """Скінченний автомат (FSM) автопілота для процедур зльоту та посадки."""
    W, H = 840, 440
    frags = []

    # Верхній контур: Зліт (Takeoff Chain)
    frags.append(text(420, 25, "Контур автозльоту (Auto-Takeoff Sequence)", size=13, bold=True, color=FIELD))

    b1, _, _ = textbox(110, 70, "1. PREARM_CHECK\nСенсори, IMU, GPS", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    b2, _, _ = textbox(290, 70, "2. WAIT_TRIGGER\nОчікування кидка/катапульти", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    b3, _, _ = textbox(490, 70, "3. MOTOR_RAMPUP\nЗатримка -> Плавний газ", size=11, pad=6, fill="#fef3c7", stroke="#f59e0b")
    b4, _, _ = textbox(710, 70, "4. CLIMB_OUT\nУтримання тангажу й крену", size=11, pad=6, fill="#ecfdf5", stroke=FIELD)

    frags.extend([b1, b2, b3, b4])
    frags.append(arrow(175, 70, 210, 70, color=LINE, sw=1.8))
    frags.append(arrow(370, 70, 410, 70, color=LINE, sw=1.8))
    frags.append(text(390, 58, "a > a_trig", size=9.5, color=POS, bold=True, anchor="middle"))
    frags.append(arrow(570, 70, 620, 70, color=LINE, sw=1.8))
    frags.append(text(595, 58, "V > V_stall", size=9.5, color=FIELD, bold=True, anchor="middle"))

    # Центральний стан: MISSION_NAV
    b_mid, _, _ = textbox(420, 175, "5. MISSION_NAV (Політ по маршруту)\nКонтроль висоти, швидкості, точок місії", size=12, pad=10, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b_mid)

    frags.append(arrow(710, 105, 540, 155, color=FIELD, sw=2))
    frags.append(text(660, 135, "Висота > h_safe", size=10, color=FIELD, bold=True, anchor="middle"))

    # Нижній контур: Посадка (Landing Chain)
    frags.append(text(420, 245, "Контур посадки на черево (Belly Landing Sequence)", size=13, bold=True, color=POS))

    b5, _, _ = textbox(130, 310, "6. LAND_APPROACH\nЗахід на глісаду проти вітру", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    b6, _, _ = textbox(340, 310, "7. GLIDESLOPE_DESC\nЗниження γ = 3°-5°", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    b7, _, _ = textbox(540, 310, "8. LAND_FLARE\nГаз=0, Гальмо ESC, Pitch+", size=11, pad=6, fill="#fee2e2", stroke=POS)
    b8, _, _ = textbox(720, 310, "9. TOUCHDOWN\nЗупинка, Disarm", size=11, pad=6, fill="#f1f5f9", stroke=LINE)

    frags.extend([b5, b6, b7, b8])

    frags.append(arrow(360, 205, 180, 280, color=LINE, sw=2))
    frags.append(text(240, 235, "Команда посадки", size=10, color=MUTED, bold=True, anchor="middle"))

    frags.append(arrow(220, 310, 260, 310, color=LINE, sw=1.8))
    frags.append(arrow(420, 310, 460, 310, color=LINE, sw=1.8))
    frags.append(text(440, 298, "h < h_flare", size=9.5, color=POS, bold=True, anchor="middle"))
    frags.append(arrow(620, 310, 660, 310, color=LINE, sw=1.8))
    frags.append(text(640, 298, "V_z ≈ 0", size=9.5, color=LINE, bold=True, anchor="middle"))

    # Аварійний перехід: Go-Around (Abort)
    frags.append('<path d="M 540 345 Q 540 400 340 400 T 130 345" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % POS)
    frags.append(arrow(135, 360, 130, 345, color=POS, sw=2))
    frags.append(text(340, 415, "Аварійне переривання посадки (Go-Around / Abort): різкий газ 100%, вихід на друге коло", size=10.5, color=POS, bold=True, anchor="middle"))

    render(os.path.join(IMG_DIR, "takeoff-landing-fsm.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_launch_modes()
    fig_catapult_dynamics()
    fig_belly_landing_flare()
    fig_net_and_parachute()
    fig_takeoff_landing_fsm()
    print("Всі 5 SVG-фігур успішно згенеровано.")
