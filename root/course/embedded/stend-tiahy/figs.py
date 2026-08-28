# -*- coding: utf-8 -*-
"""Фігури до теми «Стенд тяги: міряємо грами на ват» (курс embedded/drony).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Кінематика важільного стенду тяги ─────────────────────────────────────
def fig_thrust_stand_mechanics():
    W, H = 780, 430
    f = [text(W / 2, 28, "Кінематика L-подібного важільного стенду тяги", size=16, bold=True)]

    # Координати шарніра (pivot)
    px, py = 260, 270

    # Опорна стійка (трикутник/основа шарніра)
    f.append(rect(60, 360, 660, 16, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=3))
    f.append(text(390, 395, "Масивна жорстка станина (кріплення до столу)", size=12, color=MUTED))

    # Стійка шарніра
    f.append(rect(px - 14, py, 28, 90, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=4))

    # L-подібний важіль
    # Вертикальне плече (L1) вгору до мотора
    motor_y = 110
    f.append(line(px, py, px, motor_y, color=LINE, sw=7))
    # Горизонтальне плече (L2) вправо до датчика
    sensor_x = 450
    f.append(line(px, py, sensor_x, py, color=LINE, sw=7))

    # Шарнірний вузол (прецизійний підшипник)
    f.append(circle(px, py, 14, fill="#f8fafc", stroke=LINE, sw=2))
    f.append(circle(px, py, 4, fill=INK, stroke=INK))
    f.append(text(px - 28, py + 20, "Шарнір", size=11, bold=True, anchor="end"))
    f.append(text(px - 28, py + 34, "(кулькопідшипник)", size=10, color=MUTED, anchor="end"))

    # Мотор і гвинт на верхньому кінці
    f.append(rect(px - 16, motor_y - 20, 32, 40, fill="#334155", stroke=LINE, sw=1.5, rx=4))
    f.append(text(px, motor_y + 30, "BLDC мотор", size=11, bold=True))

    # Гвинт
    f.append(line(px - 6, motor_y - 65, px - 6, motor_y + 65, color=INK, sw=5))
    f.append(circle(px - 6, motor_y, 6, fill=POS, stroke=POS))

    # Струмінь повітря вліво (вільний викид)
    for dy in [-40, -20, 0, 20, 40]:
        f.append(arrow(px - 18, motor_y + dy, px - 110, motor_y + dy, color=NEG, sw=2))
    f.append(text(px - 75, motor_y - 52, "Відкидний струмінь", size=11, bold=True, color=NEG))
    f.append(text(px - 75, motor_y - 38, "(вільний простір)", size=10, color=MUTED))

    # Вектор сили тяги F_thrust вправо
    f.append(arrow(px + 18, motor_y, px + 95, motor_y, color=POS, sw=3))
    f.append(text(px + 60, motor_y - 12, "Тяга F_тяг", size=13, bold=True, color=POS))

    # Розміри плечей L1 та L2
    f.append(line(px + 40, motor_y, px + 40, py, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(px + 52, (motor_y + py) / 2, "Плече L1", size=12, bold=True, color=INK))

    f.append(line(px, py + 30, sensor_x, py + 30, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text((px + sensor_x) / 2, py + 48, "Плече L2", size=12, bold=True, color=INK))

    # Тензодатчик сили під правим кінцем L2
    f.append(rect(sensor_x - 20, py + 12, 40, 50, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=4))
    f.append(circle(sensor_x, py + 6, 5, fill=POS, stroke=POS))
    f.append(arrow(sensor_x, py, sensor_x, py + 26, color=POS, sw=2.5))
    f.append(rect(sensor_x - 28, py + 62, 56, 12, fill="#94a3b8", stroke=LINE, sw=1.2, rx=2))
    f.append(text(sensor_x, py + 92, "Тензодатчик", size=11, bold=True))
    f.append(text(sensor_x, py + 106, "(Load Cell)", size=10, color=MUTED))

    # Права інформаційна панель із правилом моменту
    bx, by = 610, 160
    b1, _, _ = textbox(bx, by, "БАЛАНС МОМЕНТІВ\nF_тяг · L1 = F_датч · L2\n\nF_тяг = F_датч · (L2 / L1)",
                       size=13, bold=True, color=INK, fill="#f8fafc", stroke=LINE, min_w=220)
    f.append(b1)

    b2, _, _ = textbox(bx, by + 130, "ЧОМУ НЕ ПОВЕРХНЯ ВАГ:\n• Downwash б'є в стіл (+20% хиби)\n• Реактивний момент скручує опору\n• Вібрація вибиває нуль",
                       size=11, bold=False, color=POS, fill="#fef2f2", stroke=POS, min_w=220)
    f.append(b2)

    render(os.path.join(IMG, 'thrust-stand-mechanics.svg'), W, H, *f)


# ── 2. Схемотехніка сенсорного тракту ─────────────────────────────────────────
def fig_sensor_circuit_pipeline():
    W, H = 800, 410
    f = [text(W / 2, 28, "Сенсорний тракт та синхронізація збору даних", size=16, bold=True)]

    # Блоки силового контуру (верхній ряд)
    # 1. Живлення
    b_pwr, _, _ = textbox(100, 100, "ДЖЕРЕЛО / БАТАРЕЯ\n4S–6S LiPo або БЖ\nU: 12–25 В",
                          size=11, bold=True, fill="#fef3c7", stroke="#d97706", min_w=140)
    f.append(b_pwr)

    # 2. Шунт + INA226
    b_ina, _, _ = textbox(300, 100, "МОНІТОР ПОТУЖНОСТІ\nINA226 + Шунт 1 мОм\nU_bus, I_shunt, P_el",
                          size=11, bold=True, fill="#ecfdf5", stroke=FIELD, min_w=160)
    f.append(b_ina)

    # 3. ESC
    b_esc, _, _ = textbox(520, 100, "РЕГУЛЯТОР (ESC)\nBLHeli_32 / AM32\nDShot600 / PWM",
                          size=11, bold=True, fill="#eff6ff", stroke=NEG, min_w=140)
    f.append(b_esc)

    # 4. Мотор
    b_mot, _, _ = textbox(710, 100, "BLDC МОТОР\n+ Гвинт\nТяга + Оберти",
                          size=11, bold=True, fill="#fdf2f8", stroke=POS, min_w=120)
    f.append(b_mot)

    # Зв'язки силового ряду
    f.append(arrow(170, 100, 220, 100, color=LINE, sw=2))
    f.append(arrow(380, 100, 450, 100, color=LINE, sw=2))
    f.append(arrow(590, 100, 650, 100, color=LINE, sw=2))

    # Нижній ряд вимірювачів
    # Тензодатчик + HX711
    b_hx, _, _ = textbox(170, 240, "СИЛА: LOAD CELL + HX711\n• 24-біт ΔΣ АЦП, 80 SPS\n• Повний міст Вітстона\n• Сирий код тяги (ADC_raw)",
                         size=11, bold=True, fill="#f8fafc", stroke=LINE, min_w=220)
    f.append(b_hx)

    # Тахометр (RPM)
    b_rpm, _, _ = textbox(440, 240, "ТАХОМЕТР (RPM)\n• Оптичний датчик / Холл\n• Або eRPM з DShot телеметрії\n• Вхід захоплення таймера",
                          size=11, bold=True, fill="#f8fafc", stroke=LINE, min_w=220)
    f.append(b_rpm)

    # Температура тензобалки
    b_temp, _, _ = textbox(700, 240, "ТЕРМОДАТЧИК\nNTC / I2C (балка)\nКомпенсація дрейфу",
                           size=11, bold=True, fill="#fef2f2", stroke=POS, min_w=150)
    f.append(b_temp)

    # Центральний контролер стенду
    b_mcu, _, _ = textbox(400, 350, "МІКРОКОНТРОЛЕР СТЕНДУ (STM32 / ESP32)\n• Синхронізація зрізів даних  • Медіанний фільтр  • Розрахунок g/W  • Стрімінг CSV по UART",
                          size=12, bold=True, fill="#f1f5f9", stroke=LINE, min_w=640)
    f.append(b_mcu)

    # Шини до MCU
    f.append(arrow(300, 140, 340, 315, color=FIELD, sw=1.8))
    f.append(text(305, 200, "I2C (U, I)", size=10, bold=True, color=FIELD))

    f.append(arrow(470, 315, 520, 140, color=NEG, sw=1.8))
    f.append(text(515, 200, "DShot наказ", size=10, bold=True, color=NEG))

    f.append(arrow(170, 280, 240, 315, color=LINE, sw=1.8))
    f.append(text(180, 305, "2-wire DOUT/SCK", size=10, color=MUTED))

    f.append(arrow(440, 280, 420, 315, color=LINE, sw=1.8))
    f.append(text(445, 300, "Timer Capture", size=10, color=MUTED))

    f.append(arrow(700, 280, 580, 315, color=POS, sw=1.8))
    f.append(text(660, 305, "ADC / I2C", size=10, color=POS))

    render(os.path.join(IMG, 'sensor-circuit-pipeline.svg'), W, H, *f)


# ── 3. Часова діаграма ступінчастого тесту ────────────────────────────────────
def fig_step_test_timeline():
    W, H = 780, 390
    f = [text(W / 2, 28, "Часовий профіль та вікна вимірювання (Step Test Sequence)", size=16, bold=True)]

    # Вісі графіку
    ox, oy = 80, 240
    f.append(arrow(ox, oy, 720, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, 60, color=LINE, sw=1.8))
    f.append(text(720, oy + 24, "Час t, с", size=12, bold=True, anchor="end"))
    f.append(text(ox - 10, 65, "Газ %", size=12, bold=True, anchor="end"))

    # Сходинки газу (Throttle steps): 0% -> 25% -> 50% -> 75% -> 100% -> 0%
    pts = [
        (ox, oy), (ox + 60, oy),
        (ox + 60, oy - 40), (ox + 180, oy - 40),
        (ox + 180, oy - 80), (ox + 300, oy - 80),
        (ox + 300, oy - 120), (ox + 420, oy - 120),
        (ox + 420, oy - 160), (ox + 540, oy - 160),
        (ox + 540, oy), (ox + 620, oy)
    ]
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=2.5))

    # Позначки рівнів газу
    f.append(text(ox - 10, oy - 40 + 4, "25%", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 80 + 4, "50%", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 120 + 4, "75%", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 160 + 4, "100%", size=11, color=MUTED, anchor="end"))

    # Виділення фаз на сходинці 50% (x = 260 .. 380)
    sx0, sx_mid, sx1 = ox + 180, ox + 230, ox + 300
    # Фаза перехідного процесу
    f.append(rect(sx0, 70, sx_mid - sx0, oy - 70, fill="#fef2f2", stroke="none"))
    f.append(line(sx_mid, 70, sx_mid, oy, color=POS, sw=1.2, dash="3,3"))
    f.append(text((sx0 + sx_mid) / 2, 85, "Розгін ротора", size=10, bold=True, color=POS))
    f.append(text((sx0 + sx_mid) / 2, 100, "(1.0–1.5 с)", size=9, color=MUTED))

    # Фаза стаціонарного усереднення
    f.append(rect(sx_mid, 70, sx1 - sx_mid, oy - 70, fill="#ecfdf5", stroke="none"))
    f.append(line(sx1, 70, sx1, oy, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text((sx_mid + sx1) / 2, 85, "Вікно виміру", size=10, bold=True, color=FIELD))
    f.append(text((sx_mid + sx1) / 2, 100, "(2.0 с, медіана)", size=9, color=MUTED))

    # Початкова та кінцева тара (нуль)
    f.append(circle(ox + 30, oy, 6, fill=FIELD, stroke=FIELD))
    f.append(text(ox + 30, oy - 15, "Тара ДО", size=11, bold=True, color=FIELD))

    f.append(circle(ox + 580, oy, 6, fill=POS, stroke=POS))
    f.append(text(ox + 580, oy - 15, "Тара ПІСЛЯ", size=11, bold=True, color=POS))

    # Нижня лінія температурного дрейфу нуля
    f.append(line(ox + 30, 310, ox + 580, 340, color=POS, sw=2, dash="4,4"))
    f.append(text(ox + 30, 295, "Нуль холодний (0 г)", size=11, bold=True, color=FIELD))
    f.append(text(ox + 580, 360, "Дрейф нуля від нагріву (+15 г)", size=11, bold=True, color=POS))
    f.append(text((ox + 300), 340, "Лінійна інтерполяція зміщення нуля у часі", size=11, color=MUTED))

    render(os.path.join(IMG, 'step-test-timeline.svg'), W, H, *f)


# ── 4. Карти ефективності мото-гвинтової пари ────────────────────────────────
def fig_thrust_efficiency_curves():
    W, H = 780, 410
    f = [text(W / 2, 28, "Карти характеристик: тяга та питома ефективність (г/Вт)", size=16, bold=True)]

    # Лівий графік: Тяга F(Throttle) та Потужність P(Throttle)
    lx0, ly0 = 80, 320
    lw, lh = 280, 240
    f.append(rect(lx0, ly0 - lh, lw, lh, fill="#fafafa", stroke=LINE, sw=1.2, rx=4))
    f.append(text(lx0 + lw / 2, ly0 - lh - 12, "Тяга (г) та Потужність (Вт) vs Газ (%)", size=12, bold=True))

    f.append(arrow(lx0, ly0, lx0 + lw - 10, ly0, color=LINE, sw=1.5))
    f.append(arrow(lx0, ly0, lx0, ly0 - lh + 15, color=LINE, sw=1.5))
    f.append(text(lx0 + lw - 10, ly0 + 20, "Газ %", size=11, color=MUTED, anchor="end"))

    # Крива тяги (квадратична ~ x^2) - синя
    pts_t = [(lx0 + 20 * i, ly0 - int(2.1 * (i**1.8))) for i in range(14)]
    for i in range(len(pts_t) - 1):
        f.append(line(pts_t[i][0], pts_t[i][1], pts_t[i+1][0], pts_t[i+1][1], color=NEG, sw=2.5))
    f.append(text(lx0 + 170, ly0 - 90, "Тяга T ∝ n²", size=11, bold=True, color=NEG))

    # Крива потужності (кубічна ~ x^3) - червона
    pts_p = [(lx0 + 20 * i, ly0 - int(0.7 * (i**2.3))) for i in range(14)]
    for i in range(len(pts_p) - 1):
        f.append(line(pts_p[i][0], pts_p[i][1], pts_p[i+1][0], pts_p[i+1][1], color=POS, sw=2.5))
    f.append(text(lx0 + 130, ly0 - 180, "Потужність P ∝ n³", size=11, bold=True, color=POS))

    # Правий графік: Питома тяга (г/Вт) vs Тяга (г)
    rx0, ry0 = 440, 320
    rw, rh = 280, 240
    f.append(rect(rx0, ry0 - rh, rw, rh, fill="#fafafa", stroke=LINE, sw=1.2, rx=4))
    f.append(text(rx0 + rw / 2, ry0 - rh - 12, "Питома тяга (г/Вт) vs Тяга (г)", size=12, bold=True))

    f.append(arrow(rx0, ry0, rx0 + rw - 10, ry0, color=LINE, sw=1.5))
    f.append(arrow(rx0, ry0, rx0, ry0 - rh + 15, color=LINE, sw=1.5))
    f.append(text(rx0 + rw - 10, ry0 + 20, "Тяга T, г", size=11, color=MUTED, anchor="end"))
    f.append(text(rx0 - 8, ry0 - rh + 20, "г/Вт", size=11, color=MUTED, anchor="end"))

    # Крива спадної ефективності (параболічно падає від 12 до 3 г/Вт)
    pts_eff = [
        (rx0 + 15, ry0 - 200),
        (rx0 + 40, ry0 - 170),
        (rx0 + 80, ry0 - 130),
        (rx0 + 130, ry0 - 95),
        (rx0 + 190, ry0 - 65),
        (rx0 + 260, ry0 - 45)
    ]
    for i in range(len(pts_eff) - 1):
        f.append(line(pts_eff[i][0], pts_eff[i][1], pts_eff[i+1][0], pts_eff[i+1][1], color=FIELD, sw=3))

    # Зона висіння (Hover Zone)
    f.append(rect(rx0 + 60, ry0 - 160, 80, 110, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    f.append(circle(rx0 + 100, ry0 - 115, 6, fill=FIELD, stroke=LINE))
    f.append(text(rx0 + 100, ry0 - 170, "ТОЧКА ВИСІННЯ", size=10, bold=True, color=FIELD))
    f.append(text(rx0 + 100, ry0 - 75, "7–9 г/Вт (40% газу)", size=10, color=INK))

    # Зона повного газу (Full throttle)
    f.append(circle(rx0 + 260, ry0 - 45, 6, fill=POS, stroke=LINE))
    f.append(text(rx0 + 220, ry0 - 25, "Повний газ: 3.2 г/Вт", size=10, bold=True, color=POS))

    # Пояснення знизу
    f.append(text(W / 2, 385, "Кубічне зростання споживання потужності P неминуче обвалює питому віддачу г/Вт на високих обертах",
                  size=12, bold=False, color=MUTED))

    render(os.path.join(IMG, 'thrust-efficiency-curves.svg'), W, H, *f)


if __name__ == '__main__':
    fig_thrust_stand_mechanics()
    fig_sensor_circuit_pipeline()
    fig_step_test_timeline()
    fig_thrust_efficiency_curves()
    print("All figures generated successfully.")
