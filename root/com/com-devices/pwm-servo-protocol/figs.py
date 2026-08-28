# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми pwm-servo-protocol."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def fig_pwm_timing():
    """Часова діаграма класичного керування сервоприводом (RC PWM 50 Гц)."""
    w, h = 860, 480
    frags = []

    # Заголовок блоку часової сітки
    frags.append(rect(20, 20, 820, 440, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 48, "Часова діаграма сигналів RC PWM (Період 20 мс / Частота 50 Гц)", size=16, bold=True, color=INK))

    # Вісь часу зверху
    frags.append(line(80, 80, 800, 80, color=LINE, sw=1.5))
    for t_val, t_str in [(0, "0 мс"), (5, "5 мс"), (10, "10 мс"), (15, "15 мс"), (20, "20 мс")]:
        gx = 100 + t_val * 32
        frags.append(line(gx, 75, gx, 85, color=MUTED, sw=1))
        frags.append(text(gx, 70, t_str, size=11, color=MUTED, anchor="middle"))

    # Допоміжна сітка 20 мс
    frags.append(line(100, 80, 100, 400, color="#e2e8f0", sw=1, dash="4,4"))
    frags.append(line(740, 80, 740, 400, color="#e2e8f0", sw=1, dash="4,4"))

    # Стрілка повного періоду
    frags.append(line(100, 105, 740, 105, color=LINE, sw=1.5))
    frags.append(arrow(450, 105, 740, 105, color=LINE, sw=1.5))
    frags.append(arrow(390, 105, 100, 105, color=LINE, sw=1.5))
    tbox, _, _ = textbox(420, 105, "Повний період T = 20 мс (50 Гц)", size=12, fill="#ffffff", pad=6, bold=True)
    frags.append(tbox)

    # Рядок 1: 1000 мкс (-90° / Крайнє ліве положення)
    y1 = 175
    frags.append(text(90, y1 - 10, "1000 мкс:", size=13, bold=True, color=INK, anchor="end"))
    pw1 = 32 # 1 ms = 32 px
    p1 = f"M 100 {y1} L 100 {y1-30} L {100+pw1} {y1-30} L {100+pw1} {y1} L 740 {y1}"
    frags.append(f'<path d="{p1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(rect(100, y1-30, pw1, 30, fill="#fee2e2", stroke="none"))
    frags.append(text(100 + pw1/2, y1 - 38, "1.0 мс", size=11, bold=True, color=POS))
    frags.append(text(430, y1 - 12, "Мінімальний кут повороту (-90° / 0°)", size=12, color=MUTED, anchor="middle"))

    # Рядок 2: 1500 мкс (0° / Нейтраль)
    y2 = 260
    frags.append(text(90, y2 - 10, "1500 мкс:", size=13, bold=True, color=INK, anchor="end"))
    pw2 = 48 # 1.5 ms = 48 px
    p2 = f"M 100 {y2} L 100 {y2-30} L {100+pw2} {y2-30} L {100+pw2} {y2} L 740 {y2}"
    frags.append(f'<path d="{p2}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    frags.append(rect(100, y2-30, pw2, 30, fill="#dcfce7", stroke="none"))
    frags.append(text(100 + pw2/2, y2 - 38, "1.5 мс", size=11, bold=True, color=FIELD))
    frags.append(text(430, y2 - 12, "Нейтраль (Центральне положення / 0° або 90°)", size=12, color=MUTED, anchor="middle"))

    # Рядок 3: 2000 мкс (+90° / Крайнє праве положення)
    y3 = 345
    frags.append(text(90, y3 - 10, "2000 мкс:", size=13, bold=True, color=INK, anchor="end"))
    pw3 = 64 # 2.0 ms = 64 px
    p3 = f"M 100 {y3} L 100 {y3-30} L {100+pw3} {y3-30} L {100+pw3} {y3} L 740 {y3}"
    frags.append(f'<path d="{p3}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    frags.append(rect(100, y3-30, pw3, 30, fill="#dbeafe", stroke="none"))
    frags.append(text(100 + pw3/2, y3 - 38, "2.0 мс", size=11, bold=True, color=NEG))
    frags.append(text(430, y3 - 12, "Максимальний кут повороту (+90° / 180°)", size=12, color=MUTED, anchor="middle"))

    # Нижня інформаційна плашка
    frags.append(rect(60, 400, 740, 45, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(430, 428, "Розширений діапазон (extended pulse): 500...2500 мкс для сервоприводів із ходом 180°...270°", size=12, color=INK))

    render(os.path.join(IMG_DIR, "fig-servo-pwm-timing.svg"), w, h, *frags)

def fig_internal_architecture():
    """Схемотехніка та контур зворотного зв'язку аналогового сервоприводу."""
    w, h = 900, 440
    frags = []

    # Загальний контур сервомашинки
    frags.append(rect(20, 20, 860, 400, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(450, 45, "Внутрішня функціональна схема аналогового сервоприводу", size=16, bold=True, color=INK))

    # Блок 1: Вхідний імпульс
    frags.append(rect(40, 90, 110, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(95, 115, "Вхід PWM", size=13, bold=True))
    frags.append(text(95, 135, "(1.0–2.0 мс)", size=11, color=MUTED))

    # Стрілка від входу до компаратора
    frags.append(arrow(150, 120, 210, 120, color=LINE, sw=1.5))
    frags.append(text(180, 112, "t_in", size=11, bold=True, color=POS))

    # Блок 2: Часовий компаратор / Фазовий детектор
    frags.append(rect(210, 80, 140, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(280, 112, "Часовий", size=13, bold=True, color="#92400e"))
    frags.append(text(280, 130, "компаратор", size=13, bold=True, color="#92400e"))
    frags.append(text(280, 148, "Δt = t_in − t_ref", size=10, color="#78350f"))

    # Стрілка від компаратора до Deadband / Error Amp
    frags.append(arrow(350, 120, 410, 120, color=LINE, sw=1.5))
    frags.append(text(380, 112, "Δt", size=11, bold=True, color=INK))

    # Блок 3: Зона нечутливості та підсилювач похибки
    frags.append(rect(410, 80, 140, 80, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(480, 105, "Підсилювач", size=12, bold=True, color=POS))
    frags.append(text(480, 123, "похибки та", size=12, bold=True, color=POS))
    frags.append(text(480, 143, "Deadband (3 мкс)", size=10, bold=True, color="#991b1b"))

    # Стрілка до H-мосту
    frags.append(arrow(550, 120, 600, 120, color=LINE, sw=1.5))

    # Блок 4: Драйвер мотора (H-міст)
    frags.append(rect(600, 80, 110, 80, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(655, 115, "H-міст", size=13, bold=True, color=NEG))
    frags.append(text(655, 135, "(Драйвер)", size=11, color=MUTED))

    # Стрілка до мотора
    frags.append(arrow(710, 120, 750, 120, color=LINE, sw=1.5))

    # Блок 5: Електродвигун DC
    frags.append(circle(785, 120, 32, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(785, 125, "DC Мотор", size=11, bold=True))

    # Механічний зв'язок: Мотор -> Редуктор
    frags.append(arrow(785, 155, 785, 220, color=MUTED, sw=1.8))
    frags.append(text(815, 185, "Вал мотора", size=10, color=MUTED))

    # Блок 6: Редуктор (Gearbox)
    frags.append(rect(715, 220, 140, 65, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(785, 245, "Редуктор", size=13, bold=True))
    frags.append(text(785, 265, "шестерень (1:200)", size=10, color=MUTED))

    # Вихідний вал (Servo Horn)
    frags.append(arrow(855, 252, 875, 252, color=FIELD, sw=2.5))
    frags.append(text(855, 280, "Вихідний вал", size=11, bold=True, color=FIELD, anchor="end"))

    # Механічний зв'язок: Редуктор -> Потенціометр
    frags.append(arrow(715, 252, 570, 252, color=MUTED, sw=1.8))
    frags.append(text(645, 242, "Механічний зв'язок", size=10, color=MUTED))

    # Блок 7: Потенціометр зворотного зв'язку
    frags.append(rect(430, 220, 140, 65, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(500, 245, "Потенціометр", size=13, bold=True, color=FIELD))
    frags.append(text(500, 265, "зворотного зв'язку", size=11, color="#166534"))

    # Електричний зв'язок: Потенціометр -> Одновібратор
    frags.append(arrow(430, 252, 350, 252, color=LINE, sw=1.5))
    frags.append(text(390, 242, "R_pot", size=11, bold=True, color=FIELD))

    # Блок 8: Внутрішній одновібратор
    frags.append(rect(210, 220, 140, 65, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(280, 245, "Одновібратор", size=12, bold=True, color="#92400e"))
    frags.append(text(280, 265, "t_ref = k·R_pot·C", size=10, color="#78350f"))

    # Зв'язок: Одновібратор -> Компаратор
    frags.append(arrow(280, 220, 280, 160, color=LINE, sw=1.5))
    frags.append(text(295, 190, "t_ref", size=11, bold=True, color=NEG))

    # Пояснення контуру
    frags.append(rect(40, 330, 820, 65, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(450, 355, "Контур замкнений: якщо t_in > t_ref, мотор обертає редуктор вперед, змінюючи опір R_pot,", size=11, color=INK))
    frags.append(text(450, 375, "доки опорний імпульс одновібратора t_ref не зрівняється з t_in з точністю до зони нечутливості.", size=11, color=INK))

    render(os.path.join(IMG_DIR, "fig-servo-internal-architecture.svg"), w, h, *frags)

def fig_analog_vs_digital():
    """Порівняння відпрацювання аналогового та цифрового сервоприводів."""
    w, h = 860, 440
    frags = []

    frags.append(rect(20, 20, 820, 400, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 48, "Аналоговий проти Цифрового сервоприводу: частота збудження мотора", size=16, bold=True, color=INK))

    # Ліва колонка: Аналоговий сервопривід
    frags.append(rect(40, 75, 370, 325, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(225, 105, "Аналоговий сервопривід (50 Гц)", size=14, bold=True, color=POS))
    frags.append(text(225, 125, "Імпульс на мотор тільки при надходженні сигналу", size=11, color=MUTED))

    # Графік імпульсів на мотор аналогового серво
    y_a = 180
    frags.append(line(60, y_a, 390, y_a, color=LINE, sw=1))
    p_a = f"M 60 {y_a} L 80 {y_a} L 80 {y_a-40} L 95 {y_a-40} L 95 {y_a} L 220 {y_a} L 220 {y_a-40} L 235 {y_a-40} L 235 {y_a} L 360 {y_a} L 360 {y_a-40} L 375 {y_a-40} L 375 {y_a} L 390 {y_a}"
    frags.append(f'<path d="{p_a}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(150, y_a + 20, "Пауза 20 мс (мотор знеструмлений)", size=10, color=MUTED))

    # Опис властивостей аналогового серво
    frags.append(rect(55, 230, 340, 155, fill="#fff1f2", stroke="#fecdd3", sw=1, rx=4))
    frags.append(text(70, 255, "• Частота оновлення мотора: 50 Гц (T = 20 мс)", size=11, color=INK, anchor="start"))
    frags.append(text(70, 280, "• При малій похибці (1-2°): слабкий пусковий", size=11, color=INK, anchor="start"))
    frags.append(text(80, 298, "момент через мізерне заповнення (duty cycle)", size=11, color=MUTED, anchor="start"))
    frags.append(text(70, 323, "• Повільна реакція на зовнішнє навантаження", size=11, color=INK, anchor="start"))
    frags.append(text(70, 348, "• Зона нечутливості (Deadband): 3–5 мкс", size=11, color=INK, anchor="start"))
    frags.append(text(70, 370, "• Схильність до просідання під статичною силою", size=11, color=POS, bold=True, anchor="start"))

    # Права колонка: Цифровий сервопривід
    frags.append(rect(450, 75, 370, 325, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(635, 105, "Цифровий сервопривід (300 Гц+)", size=14, bold=True, color=FIELD))
    frags.append(text(635, 125, "Власний MCU генерує високочастотні ШІМ-пакети", size=11, color=MUTED))

    # Графік імпульсів на мотор цифрового серво
    y_d = 180
    frags.append(line(470, y_d, 800, y_d, color=LINE, sw=1))
    p_d_parts = [f"M 470 {y_d}"]
    for x_i in range(480, 790, 25):
        p_d_parts.append(f"L {x_i} {y_d} L {x_i} {y_d-40} L {x_i+12} {y_d-40} L {x_i+12} {y_d}")
    p_d_parts.append(f"L 800 {y_d}")
    p_d = " ".join(p_d_parts)
    frags.append(f'<path d="{p_d}" fill="none" stroke="{FIELD}" stroke-width="2"/>')
    frags.append(text(635, y_d + 20, "Постійне високочастотне підживлення (300 Гц)", size=10, color=FIELD))

    # Опис властивостей цифрового серво
    frags.append(rect(465, 230, 340, 155, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=4))
    frags.append(text(480, 255, "• Внутрішній цикл PID-контролера: 250–400 Гц", size=11, color=INK, anchor="start"))
    frags.append(text(480, 280, "• Максимальний пусковий момент навіть при", size=11, color=INK, anchor="start"))
    frags.append(text(490, 298, "мінімальних відхиленнях (holding torque)", size=11, color=MUTED, anchor="start"))
    frags.append(text(480, 323, "• Миттєве наростання зусилля та жорсткість", size=11, color=INK, anchor="start"))
    frags.append(text(480, 348, "• Вузька зона нечутливості: 1–2 мкс", size=11, color=INK, anchor="start"))
    frags.append(text(480, 370, "• Підвищене енергоспоживання при утриманні", size=11, color="#15803d", bold=True, anchor="start"))

    render(os.path.join(IMG_DIR, "fig-analog-vs-digital.svg"), w, h, *frags)

def fig_timer_pwm_generation():
    """Апаратна генерація ШІМ за допомогою таймера мікроконтролера."""
    w, h = 860, 440
    frags = []

    frags.append(rect(20, 20, 820, 400, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(430, 48, "Апаратний таймер мікроконтролера: Формування PWM для сервоприводу", size=16, bold=True, color=INK))

    ox, oy = 80, 220
    w_cycle = 320

    # Вісь лічильника
    frags.append(line(ox, oy, ox + 680, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, 90, color=LINE, sw=1.5))
    frags.append(text(ox - 10, 95, "CNT", size=12, bold=True, anchor="end"))
    frags.append(text(ox + 695, oy + 4, "t", size=12, bold=True, anchor="start"))

    # Рівень ARR (20 000 мкс)
    y_arr = 110
    frags.append(line(ox, y_arr, ox + 680, y_arr, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(ox - 10, y_arr + 4, "ARR (20000)", size=11, bold=True, color=MUTED, anchor="end"))

    # Рівень CCR (1500 мкс)
    y_ccr = 195
    frags.append(line(ox, y_ccr, ox + 680, y_ccr, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(ox - 10, y_ccr + 4, "CCR1 (1500)", size=11, bold=True, color=POS, anchor="end"))

    # Пилкоподібний сигнал CNT (два періоди по 320 px)
    for k in range(2):
        bx = ox + k * w_cycle
        frags.append(line(bx, oy, bx + w_cycle, y_arr, color=LINE, sw=2))
        frags.append(line(bx + w_cycle, y_arr, bx + w_cycle, oy, color=LINE, sw=1.5, dash="2,2"))
        x_match = bx + 24
        frags.append(circle(x_match, y_ccr, 3.5, fill=POS, stroke=POS))

    frags.append(text(ox + w_cycle, oy + 18, "T = 20 мс (Переповнення ARR)", size=11, color=MUTED, anchor="middle"))
    frags.append(text(ox + 2*w_cycle, oy + 18, "40 мс", size=11, color=MUTED, anchor="middle"))

    # Вихідний сигнал на піні GPIO
    y_out = 310
    frags.append(text(ox - 10, y_out - 15, "PWM Вихід:", size=12, bold=True, color=INK, anchor="end"))
    frags.append(line(ox, y_out, ox + 680, y_out, color=LINE, sw=1))

    for k in range(2):
        bx = ox + k * w_cycle
        x_match = bx + 24
        p_pwm = f"M {bx} {y_out} L {bx} {y_out-30} L {x_match} {y_out-30} L {x_match} {y_out} L {bx+w_cycle} {y_out}"
        frags.append(f'<path d="{p_pwm}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
        frags.append(rect(bx, y_out-30, 24, 30, fill="#dcfce7", stroke="none"))

    frags.append(text(ox + 12, y_out - 36, "1500 мкс", size=11, bold=True, color=FIELD))
    frags.append(text(ox + 160, y_out - 10, "LOW (18 500 мкс)", size=11, color=MUTED))

    # Нижній блок формул і регістрів
    frags.append(rect(40, 360, 780, 48, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(430, 382, "f_timer = f_clk / (PSC + 1) = 1 МГц (1 такт = 1 мкс)  →  ARR = 20000 − 1  →  CCR1 = тривалість імпульсу [1000...2000]", size=11, bold=True, color=INK))
    frags.append(text(430, 398, "Апаратне формування ШІМ повністю розвантажує CPU та усуває джиттер переривань.", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "fig-timer-pwm-generation.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_pwm_timing()
    fig_internal_architecture()
    fig_analog_vs_digital()
    fig_timer_pwm_generation()
    print("Всі фігури згенеровано успішно.")
