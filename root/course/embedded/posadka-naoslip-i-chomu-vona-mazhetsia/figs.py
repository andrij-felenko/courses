# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Посадка наосліп і чому вона мажеться'."""

import sys
import os

# Імпортуємо спільний набір svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_ground_effect_pressure():
    """Екранний ефект та аеродинамічний підпір на барометрі."""
    W, H = 840, 440
    frags = []

    # Тло та межі
    frags.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    # Заголовок секцій: Ліва (Фізика потоків) та Права (Графік тиску/помилки)
    frags.append(rect(25, 45, 435, 370, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(rect(475, 45, 340, 370, fill="#ffffff", stroke="#94a3b8", rx=6))

    frags.append(text(242, 30, "Аеродинаміка біля поверхні (Екранний ефект)", size=13, bold=True, color=INK))
    frags.append(text(645, 30, "Вплив на сенсори та автопілот", size=13, bold=True, color=INK))

    # Земля
    frags.append(line(40, 370, 445, 370, color="#64748b", sw=3))
    for xg in range(50, 440, 25):
        frags.append(line(xg, 370, xg - 10, 385, color="#94a3b8", sw=1.5))
    frags.append(text(242, 400, "Поверхня землі (Твердий екран)", size=11, color=MUTED, anchor="middle", bold=True))

    # Дрон на висоті h < D
    cx, cy = 242, 230
    frags.append(rect(cx - 35, cy - 15, 70, 30, fill="#e2e8f0", stroke=LINE, sw=2, rx=4)) # Корпус
    frags.append(text(cx, cy + 4, "FC / Баро", size=11, bold=True, color=INK, anchor="middle"))

    # Промені
    frags.append(line(cx - 100, cy, cx - 35, cy, color=LINE, sw=3))
    frags.append(line(cx + 35, cy, cx + 100, cy, color=LINE, sw=3))

    # Мотори
    frags.append(rect(cx - 110, cy - 12, 14, 24, fill="#64748b", stroke=LINE, sw=1.5, rx=2))
    frags.append(rect(cx + 96, cy - 12, 14, 24, fill="#64748b", stroke=LINE, sw=1.5, rx=2))

    # Пропелери (діаметр D)
    frags.append(line(cx - 145, cy - 12, cx - 65, cy - 12, color=NEG, sw=3.5))
    frags.append(line(cx + 65, cy - 12, cx + 145, cy - 12, color=NEG, sw=3.5))
    frags.append(text(cx - 105, cy - 22, "Гвинт D", size=11, color=NEG, bold=True, anchor="middle"))
    frags.append(text(cx + 105, cy - 22, "Гвинт D", size=11, color=NEG, bold=True, anchor="middle"))

    # Ніжки шасі
    frags.append(line(cx - 30, cy + 15, cx - 45, 365, color=LINE, sw=2))
    frags.append(line(cx + 30, cy + 15, cx + 45, 365, color=LINE, sw=2))

    # Розмір висоти h
    frags.append(line(cx + 160, cy - 12, cx + 160, 370, color=POS, sw=1.5, dash="3,3"))
    frags.append(arrow(cx + 160, cy + 40, cx + 160, cy - 12, color=POS, sw=1.5))
    frags.append(arrow(cx + 160, 320, cx + 160, 370, color=POS, sw=1.5))
    frags.append(text(cx + 168, 290, "h < 1.0·D", size=11, color=POS, bold=True, anchor="start"))

    # Повітряні струмені та завихрення
    frags.append(arrow(cx - 105, cy, cx - 105, 330, color="#38bdf8", sw=2.5))
    frags.append(arrow(cx + 105, cy, cx + 105, 330, color="#38bdf8", sw=2.5))

    # Розтікання по землі
    frags.append(arrow(cx - 110, 355, cx - 170, 360, color="#38bdf8", sw=2))
    frags.append(arrow(cx + 110, 355, cx + 170, 360, color="#38bdf8", sw=2))

    # Рециркуляція та підпір під корпус
    frags.append(line(cx - 90, 350, cx - 40, 290, color=POS, sw=2, dash="3,2"))
    frags.append(arrow(cx - 40, 290, cx - 10, cy + 25, color=POS, sw=2))
    frags.append(line(cx + 90, 350, cx + 40, 290, color=POS, sw=2, dash="3,2"))
    frags.append(arrow(cx + 40, 290, cx + 10, cy + 25, color=POS, sw=2))

    # Повітряна подушка
    frags.append(rect(cx - 80, 310, 160, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(cx, 328, "Зона надлишкового тиску", size=11, bold=True, color=POS, anchor="middle"))
    frags.append(text(cx, 344, "Повітряна подушка (T_IGE > T_OGE)", size=10, color=POS, anchor="middle"))

    # Права панель: 3 блоки
    box_p1, _, _ = textbox(645, 120, "1. Стрибок статичного тиску:\n"
                                     "Відбитий потік створює підпір ΔP = ½·ρ·v².\n"
                                     "Барометр бачить зростання тиску на 10-25 Па.\n"
                                     "Формула висоти дає: Δh_baro = -1.0...-2.5 м.",
                           size=11, pad=8, fill="#eff6ff", stroke="#93c5fd")
    frags.append(box_p1)

    box_p2, _, _ = textbox(645, 235, "2. Реакція автопілота наосліп:\n"
                                     "• Контролер думає: 'я падаю занадто швидко'\n"
                                     "• PID додає тягу моторів -> дрон підкидає вгору\n"
                                     "• Вийшовши з подушки, тяга падає -> просідання\n"
                                     "• Наслідок: вертикальна розкачка біля землі.",
                           size=11, pad=8, fill="#fef2f2", stroke="#fca5a5")
    frags.append(box_p2)

    box_p3, _, _ = textbox(645, 345, "3. Зростання тяги (Ground Effect):\n"
                                     "При сталій потужності тяга росте на 15-30%.\n"
                                     "Без зниження газу дрон зависає на висоті 20 см\n"
                                     "і не може торкнутися землі (пружинить).",
                           size=11, pad=8, fill="#fefce8", stroke="#fde047")
    frags.append(box_p3)

    render(os.path.join(IMG_DIR, "ground-effect-pressure.svg"), W, H, *frags)


def fig_tip_over_mechanism():
    """Механізм перекидання дрона (Tip-over) через інтегратор PID-регулятора."""
    W, H = 860, 420
    frags = []

    # Тло
    frags.append(rect(10, 10, 840, 400, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    # Три колонки стадій
    w_col = 265
    frags.append(rect(20, 45, w_col, 350, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(rect(295, 45, w_col, 350, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(rect(570, 45, w_col, 350, fill="#ffffff", stroke="#94a3b8", rx=6))

    frags.append(text(152, 30, "Етап 1: Перший контакт", size=12, bold=True, color=INK))
    frags.append(text(427, 30, "Етап 2: Накопичення I-терму", size=12, bold=True, color=INK))
    frags.append(text(702, 30, "Етап 3: Перекидання (Tip-over)", size=12, bold=True, color=INK))

    y_ground = 270

    # ЕТАП 1
    frags.append(line(30, y_ground, 275, y_ground, color="#64748b", sw=2))
    frags.append(rect(100, 185, 55, 20, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=3))
    frags.append(line(60, 192, 195, 198, color=LINE, sw=2.5))
    frags.append(line(80, 194, 70, y_ground, color=LINE, sw=2))
    frags.append(line(170, 197, 180, y_ground - 15, color=LINE, sw=2))
    frags.append(circle(70, y_ground, 5, fill=POS, stroke=LINE, sw=1.5))

    frags.append(text(70, y_ground + 20, "Точка опори", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(text(180, y_ground - 25, "Зазор 3 см", size=10, color=MUTED, anchor="middle"))

    box1, _, _ = textbox(152, 340, "Торкання однією лапою.\n"
                                   "Апарат отримує крен Δφ = 4°.\n"
                                   "Гіроскоп фіксує помилку кута.",
                         size=11, pad=6, fill="#f1f5f9", stroke="#cbd5e1")
    frags.append(box1)

    # ЕТАП 2
    frags.append(line(305, y_ground, 550, y_ground, color="#64748b", sw=2))
    frags.append(rect(375, 180, 55, 20, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(line(335, 188, 470, 196, color=LINE, sw=2.5))
    frags.append(line(355, 190, 345, y_ground, color=LINE, sw=2))
    frags.append(line(445, 194, 455, y_ground - 20, color=LINE, sw=2))
    frags.append(circle(345, y_ground, 6, fill=POS, stroke=LINE, sw=1.5))

    # Вектори тяги
    frags.append(arrow(340, 180, 340, 150, color=MUTED, sw=2))
    frags.append(text(340, 140, "Тяга 10%", size=10, color=MUTED, anchor="middle"))

    frags.append(arrow(465, 185, 465, 100, color=POS, sw=3.5))
    frags.append(text(465, 90, "Тяга 100% (I-Windup!)", size=11, color=POS, bold=True, anchor="middle"))

    frags.append(arrow(380, 150, 330, 170, color=POS, sw=2))
    frags.append(text(385, 135, "Момент перекидання", size=10, color=POS, bold=True))

    box2, _, _ = textbox(427, 340, "PID намагається вирівняти крен.\n"
                                   "Але опора блокує рух корпусу!\n"
                                   "Інтегратор росте до максимуму,\n"
                                   "розкручуючи правий мотор.",
                         size=11, pad=6, fill="#fef2f2", stroke="#fca5a5")
    frags.append(box2)

    # ЕТАП 3
    frags.append(line(580, y_ground, 825, y_ground, color="#64748b", sw=2))
    frags.append(rect(640, 230, 20, 55, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    frags.append(line(645, 200, 655, 310, color=LINE, sw=2.5))
    frags.append(circle(620, y_ground, 6, fill=POS, stroke=LINE, sw=1.5))

    frags.append(line(610, y_ground, 635, y_ground - 15, color=POS, sw=3))
    frags.append(line(610, y_ground, 595, y_ground - 10, color=POS, sw=2, dash="2,2"))
    frags.append(text(600, y_ground - 25, "Удар пропелера!", size=11, color=POS, bold=True, anchor="middle"))

    box3, _, _ = textbox(702, 340, "Перекидання через ніжку.\n"
                                   "Удар лопатей об ґрунт,\n"
                                   "згинання валів моторів,\n"
                                   "згоряння ключів ESC.",
                         size=11, pad=6, fill="#fefce8", stroke="#fde047")
    frags.append(box3)

    render(os.path.join(IMG_DIR, "tip-over-mechanism.svg"), W, H, *frags)


def fig_landing_fsm_states():
    """Скінченний автомат детектора посадки (Land Detector FSM)."""
    W, H = 940, 430
    frags = []

    # Тло
    frags.append(rect(10, 10, 920, 410, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    frags.append(text(470, 32, "Скінченний автомат детектора посадки (Land Detector FSM)", size=14, bold=True, color=INK))

    y_box = 85
    w_box, h_box = 175, 90

    # Стан 1: DESCENDING (x: 25..200)
    b1 = rect(25, y_box, w_box, h_box, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6)
    b1_t = mtext(25 + w_box / 2, y_box + 22,
                 ["1. DESCENDING", "(Швидкий спуск)", "V_z = -1.0...-1.5 м/с", "Повний PID-контроль"],
                 size=10.5, color=INK, bold=True)
    frags.append(b1 + b1_t)

    frags.append(arrow(200, y_box + h_box / 2, 255, y_box + h_box / 2, color=LINE, sw=2))
    frags.append(text(227, y_box + h_box / 2 - 12, "h < h_trans", size=10, color=MUTED, anchor="middle", bold=True))

    # Стан 2: NEAR_GROUND (x: 255..430)
    b2 = rect(255, y_box, w_box, h_box, fill="#fefce8", stroke="#eab308", sw=2, rx=6)
    b2_t = mtext(255 + w_box / 2, y_box + 20,
                 ["2. NEAR GROUND", "(Майже земля)", "V_z = -0.3...-0.4 м/с", "Заморозка I-терму", "T_max ≤ 0.7·T_hover"],
                 size=10, color=INK, bold=True)
    frags.append(b2 + b2_t)

    frags.append(arrow(430, y_box + h_box / 2, 485, y_box + h_box / 2, color=LINE, sw=2))
    frags.append(text(457, y_box + h_box / 2 - 12, "Дотик", size=10, color=MUTED, anchor="middle", bold=True))

    # Стан 3: GROUND_CONTACT (x: 485..660)
    b3 = rect(485, y_box, w_box, h_box, fill="#fef2f2", stroke="#ef4444", sw=2, rx=6)
    b3_t = mtext(485 + w_box / 2, y_box + 20,
                 ["3. GROUND CONTACT", "(Контакт із землею)", "V_z ≈ 0, Газ мінімальний", "Підтвердження accel/I", "Таймер t ≥ 0.35 с"],
                 size=10, color=INK, bold=True)
    frags.append(b3 + b3_t)

    frags.append(arrow(660, y_box + h_box / 2, 715, y_box + h_box / 2, color=LINE, sw=2))
    frags.append(text(687, y_box + h_box / 2 - 12, "Таймаут", size=10, color=MUTED, anchor="middle", bold=True))

    # Стан 4: DISARMED (x: 715..890)
    b4 = rect(715, y_box, w_box, h_box, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=6)
    b4_t = mtext(715 + w_box / 2, y_box + 22,
                 ["4. DISARMED", "(Роззброєно)", "Мотори вимкнено", "ШІМ заблоковано", "Посадка завершена"],
                 size=10.5, color=INK, bold=True)
    frags.append(b4 + b4_t)

    # Нижня секція: 3 окремі картки
    y_card = 215
    w_card, h_card = 275, 175

    # Картка А
    frags.append(rect(25, y_card, w_card, h_card, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(25 + w_card / 2, y_card + 28, "А. Критерій зупинки спуску", size=12, bold=True, color=INK))
    frags.append(mtext(25 + w_card / 2, y_card + 60,
                       ["• Вертикальна швидкість |V_z| < 0.15 м/с",
                        "• Контролер вивів газ у нижній упор",
                        "• Дисперсія шуму акселерометра в нормі",
                        "• Підтвердження падіння струму шини"],
                       size=10.5, color=INK, anchor="middle", lh=1.4))

    # Картка Б
    frags.append(rect(332, y_card, w_card, h_card, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(332 + w_card / 2, y_card + 28, "Б. Захист від Tip-over", size=12, bold=True, color=INK))
    frags.append(mtext(332 + w_card / 2, y_card + 60,
                       ["• Обнулення інтегратора крену/тангажу",
                        "• Заморожування I-терму в зоні подушки",
                        "• Зниження коефіцієнтів PID на 40%",
                        "• Заборона набору висоти при контакті"],
                       size=10.5, color=INK, anchor="middle", lh=1.4))

    # Картка В
    frags.append(rect(640, y_card, w_card, h_card, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(640 + w_card / 2, y_card + 28, "В. Аварійні запобіжники", size=12, bold=True, color=INK))
    frags.append(mtext(640 + w_card / 2, y_card + 60,
                       ["• Крен > 25° під час спуску -> газ 80%",
                        "• Стрибок барометра -> перехід на ToF",
                        "• Таймаут контакту > 3.0 с -> Disarm",
                        "• Відмова сенсорів -> аварійний зрив"],
                       size=10.5, color=INK, anchor="middle", lh=1.4))

    render(os.path.join(IMG_DIR, "landing-fsm-states.svg"), W, H, *frags)


def fig_blind_landing_trajectory():
    """Порівняння траєкторій: сліпа посадка за GNSS/баро проти сенсорного комплексування."""
    W, H = 840, 440
    frags = []

    # Тло
    frags.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    # Ліва і права панелі
    frags.append(rect(25, 45, 385, 370, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(rect(430, 45, 385, 370, fill="#ffffff", stroke="#94a3b8", rx=6))

    frags.append(text(217, 30, "Посадка наосліп (GNSS + Баро)", size=13, bold=True, color=POS))
    frags.append(text(622, 30, "Сенсорне комплексування (ToF + Flow)", size=13, bold=True, color=FIELD))

    # Ліва частина: сліпа посадка
    box_l, _, _ = textbox(217, 105, "• Горизонтальний дрейф GNSS: 1.5-3.5 м\n"
                                     "• Підскоки на екранній подушці\n"
                                     "• Спотворення барометра на 1.5 м\n"
                                     "• Ризик tip-over або посадки в каміння",
                          size=10.5, pad=6, fill="#fef2f2", stroke="#fca5a5")
    frags.append(box_l)

    # Земля зліва
    frags.append(line(35, 360, 400, 360, color="#64748b", sw=2.5))
    frags.append(rect(180, 355, 60, 8, fill="#cbd5e1", stroke=LINE, sw=1))
    frags.append(text(210, 380, "Цільовий майданчик", size=10, color=MUTED, anchor="middle"))

    # Траєкторія починається нижче інформаційного блоку (y=175)
    frags.append(line(210, 175, 250, 230, color=POS, sw=2, dash="4,2"))
    frags.append(line(250, 230, 290, 280, color=POS, sw=2, dash="4,2"))
    frags.append(line(290, 280, 275, 315, color=POS, sw=2))
    frags.append(line(275, 315, 310, 295, color=POS, sw=2)) # підскок
    frags.append(line(310, 295, 335, 358, color=POS, sw=2.5)) # удар
    frags.append(circle(335, 358, 6, fill=POS, stroke=LINE, sw=1.5))

    frags.append(text(340, 335, "Удар об ґрунт", size=10, color=POS, bold=True, anchor="start"))
    frags.append(line(210, 365, 335, 365, color=POS, sw=1.5))
    frags.append(arrow(260, 365, 335, 365, color=POS, sw=1.5))
    frags.append(arrow(260, 365, 210, 365, color=POS, sw=1.5))
    frags.append(text(272, 380, "Похибка 2.5 м", size=11, color=POS, bold=True, anchor="middle"))

    # Права частина: комплексування сенсорів
    box_r, _, _ = textbox(622, 105, "• ToF далекомір: точність висоти 1 см\n"
                                     "• Optical Flow: нульовий дрейф (V_xy=0)\n"
                                     "• Двоетапний профіль швидкості\n"
                                     "• М'який дотик і скидання I-терму",
                          size=10.5, pad=6, fill="#f0fdf4", stroke="#86efac")
    frags.append(box_r)

    # Земля справа
    frags.append(line(440, 360, 805, 360, color="#64748b", sw=2.5))
    frags.append(rect(590, 355, 60, 8, fill="#dcfce7", stroke=FIELD, sw=1.5))
    frags.append(text(620, 380, "Цільовий майданчик", size=10, color=FIELD, anchor="middle", bold=True))

    # Вертикальна траєкторія (починається з y=175 нижче інфоблоку)
    frags.append(line(620, 175, 620, 270, color=FIELD, sw=2.5))
    frags.append(text(635, 220, "Спуск 1.2 м/с", size=10, color=FIELD, bold=True, anchor="start"))

    frags.append(circle(620, 270, 5, fill="#bbf7d0", stroke=FIELD, sw=1.5))
    frags.append(text(635, 270, "ToF перехід (h = 1.5 м)", size=10, color=INK, bold=True, anchor="start"))

    frags.append(line(620, 270, 620, 356, color=FIELD, sw=3))
    frags.append(text(635, 315, "0.35 м/с", size=10, color=FIELD, bold=True, anchor="start"))
    frags.append(circle(620, 356, 5, fill=FIELD, stroke=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "blind-landing-trajectory.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_ground_effect_pressure()
    fig_tip_over_mechanism()
    fig_landing_fsm_states()
    fig_blind_landing_trajectory()
    print("All figures generated successfully.")
