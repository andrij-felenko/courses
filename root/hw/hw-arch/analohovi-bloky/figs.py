# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми analohovi-bloky."""

import sys
import os

# scripts/ у корені репо: 4 рівні вгору від root/hw/hw-arch/analohovi-bloky
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_comp_internals_and_break():
    """Фігура 1: Архітектура компаратора, вибір опорних напруг, гістерезис і Break-вхід таймера."""
    w, h = 880, 480
    frags = []

    # Заголовок блоку компаратора
    frags.append(rect(20, 20, 390, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(215, 48, "Вбудований компаратор (COMP)", size=16, color=INK, bold=True))

    # Мультиплексор неінверсного входу (INP)
    frags.append(fitbox(35, 75, 125, 60, "GPIO пін (INP)\nабо вихід OPAMP", size=11, fill="#eef2f6", stroke=LINE))
    frags.append(arrow(160, 105, 210, 105, color=LINE, sw=1.5))
    frags.append(text(185, 95, "V_IN", size=11, color=INK, italic=True))

    # Мультиплексор інверсного входу (INM)
    frags.append(rect(35, 160, 130, 170, fill="#eef2f6", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(100, 182, "Вибір порогу (INM)", size=11, color=INK, bold=True))
    frags.append(fitbox(42, 195, 116, 26, "Зовнішній GPIO", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(fitbox(42, 227, 116, 26, "Внутрішній ЦАП", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(fitbox(42, 259, 116, 26, "VREFINT (1.21 В)", size=10, fill="#ffffff", stroke=MUTED))
    frags.append(fitbox(42, 291, 116, 26, "1/4, 1/2, 3/4 VREF", size=10, fill="#ffffff", stroke=MUTED))

    frags.append(arrow(165, 245, 210, 245, color=LINE, sw=1.5))
    frags.append(text(187, 235, "V_REF", size=11, color=INK, italic=True))

    # Символ аналогового компаратора
    frags.append('<polygon points="210,75 210,275 300,175" fill="#ffffff" stroke="%s" stroke-width="2"/>' % LINE)
    frags.append(text(225, 110, "+", size=20, color=POS, bold=True))
    frags.append(text(225, 250, "−", size=20, color=NEG, bold=True))
    frags.append(text(250, 180, "COMP", size=12, color=MUTED, bold=True))

    # Блок гістерезису
    frags.append(fitbox(180, 360, 170, 75, "Програмований\nгістерезис (HYST)\n0 / 10 / 20 / 40 мВ", size=11, fill="#fff7ed", stroke="#ea580c"))
    frags.append(line(265, 360, 265, 210, color="#ea580c", sw=1.5, dash="4,3"))
    frags.append(arrow(265, 210, 245, 190, color="#ea580c", sw=1.5))

    # Вихід компаратора
    frags.append(line(300, 175, 350, 175, color=LINE, sw=1.8))
    frags.append(circle(350, 175, 4, fill=INK, stroke=INK))
    frags.append(text(340, 160, "OUT", size=11, color=INK, bold=True))

    # Розгалуження на EXTI переривання
    frags.append(line(350, 175, 350, 105, color=LINE, sw=1.5))
    frags.append(arrow(350, 105, 390, 105, color=LINE, sw=1.5))
    frags.append(text(380, 95, "IRQ", size=10, color=MUTED, bold=True))

    # Апаратний зв'язок з таймером Break (швидка червона магістраль)
    frags.append(line(350, 175, 490, 175, color=POS, sw=2.5))
    frags.append(arrow(490, 175, 520, 175, color=POS, sw=2.5))
    frags.append(fitbox(418, 120, 95, 46, "Апаратний лінк\nt_prop ≈ 15-25 нс", size=10, fill="#fee2e2", stroke=POS))

    # Блок таймера ШІМ
    frags.append(rect(490, 20, 370, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(675, 48, "Силовий таймер ШІМ (TIM1 / TIM8)", size=15, color=INK, bold=True))

    # Вхід Break
    frags.append(fitbox(510, 150, 120, 50, "Вхід захисту\nTIMx_BKIN", size=12, fill="#fecaca", stroke=POS, bold=True))
    frags.append(arrow(630, 175, 660, 175, color=POS, sw=2))

    # Логіка аварії BDTR
    frags.append(fitbox(660, 125, 180, 95, "Логіка аварії BDTR\nСкидання біта MOE\n(Main Output Enable)\nв 0 за < 1 такт (< 10 нс)", size=11, fill="#ffffff", stroke=LINE))

    frags.append(arrow(750, 220, 750, 255, color=POS, sw=2))

    # Вихідні канали ШІМ
    frags.append(rect(510, 255, 330, 185, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(675, 280, "Комплементарні канали виходу", size=13, color=INK, bold=True))

    frags.append(fitbox(525, 300, 135, 45, "Верхнє плече (CH1)\n→ ВИТИКНУТО", size=11, fill="#f1f5f9", stroke=MUTED))
    frags.append(fitbox(525, 360, 135, 45, "Нижнє плече (CH1N)\n→ ВИТИКНУТО", size=11, fill="#f1f5f9", stroke=MUTED))

    frags.append(fitbox(680, 300, 145, 105, "Політика AOE:\n• AOE=0: Lock\n(скидання кодом)\n• AOE=1: Цикл-в-цикл\n(авто-відновлення)", size=11, fill="#fef3c7", stroke="#d97706"))

    return render(os.path.join(IMG_DIR, "comp-internals-and-break.svg"), w, h, *frags)


def fig_opamp_pga_routing():
    """Фігура 2: Вбудований OPAMP у режимі PGA з внутрішньою матрицею та калібруванням зсуву."""
    w, h = 860, 460
    frags = []

    # Загальний корпус блоку OPAMP
    frags.append(rect(20, 20, 520, 420, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(280, 48, "Вбудований OPAMP у режимі PGA (2x–64x)", size=16, color=INK, bold=True))

    # Зовнішній вхід від шунта
    frags.append(fitbox(40, 80, 120, 60, "Низькоомний шунт\n(напр. 5 мОм)\nВхід OPAMP_VINP", size=11, fill="#eef2f6", stroke=LINE))
    frags.append(arrow(160, 110, 220, 110, color=LINE, sw=1.5))
    frags.append(text(190, 100, "V_IN+", size=12, color=INK, italic=True))

    # Трикутник операційного підсилювача
    frags.append('<polygon points="220,70 220,250 320,160" fill="#ffffff" stroke="%s" stroke-width="2"/>' % LINE)
    frags.append(text(235, 115, "+", size=20, color=POS, bold=True))
    frags.append(text(235, 215, "−", size=20, color=NEG, bold=True))
    frags.append(text(265, 165, "OPAMP", size=13, color=MUTED, bold=True))

    # Внутрішній резистивний дільник зворотного зв'язку (PGA)
    frags.append(line(320, 160, 360, 160, color=LINE, sw=1.8))
    frags.append(circle(360, 160, 3, fill=INK, stroke=INK))
    frags.append(line(360, 160, 360, 280, color=LINE, sw=1.5))
    frags.append(line(360, 280, 300, 280, color=LINE, sw=1.5))

    # Блок резистивної матриці
    frags.append(rect(140, 255, 160, 65, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(220, 275, "R-2R матриця PGA", size=12, color="#b45309", bold=True))
    frags.append(text(220, 300, "R_f / R_in = 2x ... 64x", size=11, color=INK))

    frags.append(line(140, 280, 100, 280, color=LINE, sw=1.5))
    frags.append(fitbox(40, 260, 60, 40, "GND / \nVM_SEL", size=10, fill="#f1f5f9", stroke=MUTED))

    # Зворотний зв'язок на інверсний вхід
    frags.append(line(220, 270, 200, 270, color=LINE, sw=1.5))
    frags.append(line(200, 270, 200, 210, color=LINE, sw=1.5))
    frags.append(arrow(200, 210, 220, 210, color=LINE, sw=1.5))

    # Блок калібрування зсуву (Offset Trimming)
    frags.append(fitbox(40, 345, 230, 75, "Калібрування зсуву (Offset Trim)\n5-бітний ЦАП зміщення нуля\nTRIMOFFSETP / TRIMOFFSETN\nV_offset: 3 мВ → < 200 мкВ", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(line(270, 380, 280, 380, color=FIELD, sw=1.5, dash="3,2"))
    frags.append(line(280, 380, 280, 215, color=FIELD, sw=1.5, dash="3,2"))
    frags.append(arrow(280, 215, 260, 185, color=FIELD, sw=1.5))

    # Вихід OPAMP і внутрішня маршрутизація
    frags.append(line(360, 160, 430, 160, color=LINE, sw=2))
    frags.append(circle(430, 160, 4, fill=INK, stroke=INK))
    frags.append(text(400, 145, "OPAMP_OUT", size=12, color=INK, bold=True))

    # Розгалуження внутрішнього сигналу (без виводу на пін!)
    frags.append(line(430, 160, 480, 160, color=POS, sw=2))
    frags.append(arrow(480, 160, 560, 110, color=POS, sw=2))
    frags.append(arrow(480, 160, 560, 270, color=POS, sw=2))

    # Зовнішній пін (опціонально)
    frags.append(line(430, 160, 430, 90, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(arrow(430, 90, 480, 90, color=MUTED, sw=1.5))
    frags.append(text(485, 80, "Зовнішній GPIO (опція)", size=10, color=MUTED))

    # Приймачі всередині МК
    # Блок швидкісного АЦП
    frags.append(rect(560, 60, 280, 130, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(700, 85, "Швидкісний АЦП (ADCx_IN3)", size=13, color=INK, bold=True))
    frags.append(fitbox(580, 105, 240, 70, "Внутрішній аналоговий канал:\n• Немає паразитної ємності плати\n• Відсутні наведення ЕМС\n• Економія виводів чіпа", size=11, fill="#ffffff", stroke=MUTED))

    # Блок компаратора аварії
    frags.append(rect(560, 220, 280, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(700, 245, "Швидкий компаратор (COMPx)", size=13, color=INK, bold=True))
    frags.append(fitbox(580, 265, 240, 100, "Прямий вхід INP:\nМиттєве порівняння підсиленого\nструму з аварійним порогом КЗ\n(перехід до TIM Break за 20 нс)", size=11, fill="#fee2e2", stroke=POS))

    return render(os.path.join(IMG_DIR, "opamp-pga-routing.svg"), w, h, *frags)


def fig_analog_watchdog_window():
    """Фігура 3: Графік роботи аналогового сторожового пса (AWD) з коридором допустимих напруг."""
    w, h = 860, 440
    frags = []

    # Верхній напис статусу аварії над графіком
    frags.append(fitbox(180, 12, 160, 26, "AWD IRQ (High Fault)", size=11, fill="#fee2e2", stroke=POS, bold=True))

    # Фон і сітка графіку
    frags.append(rect(60, 50, 520, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))

    # Осі
    frags.append(arrow(60, 360, 600, 360, color=LINE, sw=2)) # Вісь часу
    frags.append(text(590, 385, "Час (t)", size=12, color=INK, bold=True))
    frags.append(arrow(60, 360, 60, 30, color=LINE, sw=2))  # Вісь коду АЦП
    frags.append(text(45, 30, "Код АЦП (12 біт)", size=12, color=INK, bold=True))

    # Поріг HTR (High Threshold)
    y_htr = 115
    frags.append(line(60, y_htr, 580, y_htr, color=POS, sw=1.8, dash="6,4"))
    frags.append(text(120, y_htr - 8, "Верхній поріг HTR (напр. 3400 / 2.74 В)", size=11, color=POS, bold=True))

    # Поріг LTR (Low Threshold)
    y_ltr = 275
    frags.append(line(60, y_ltr, 580, y_ltr, color=NEG, sw=1.8, dash="6,4"))
    frags.append(text(120, y_ltr + 18, "Нижній поріг LTR (напр. 800 / 0.64 В)", size=11, color=NEG, bold=True))

    # Безпечна зона (зеленуватий фон)
    frags.append(rect(61, y_htr, 518, y_ltr - y_htr, fill="#f0fdf4", stroke="none"))
    frags.append(text(320, 195, "БЕЗПЕЧНИЙ КОРИДОР (AWD_FLAG = 0)", size=13, color=FIELD, bold=True))

    # Крива аналогового сигналу (траєкторія вимірювань АЦП)
    path_d = ("M 60,200 Q 120,180 180,140 T 250,75 T 320,160 T 400,220 T 460,320 T 520,240 T 580,180")
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path_d, INK))

    # Точки вибірки АЦП
    samples = [
        (100, 188), (140, 168), (180, 140), (215, 105), (250, 75),
        (285, 110), (320, 160), (360, 195), (400, 220), (430, 265),
        (460, 320), (490, 275), (520, 240), (550, 205)
    ]
    for sx, sy in samples:
        c_fill = POS if sy < y_htr else (NEG if sy > y_ltr else FIELD)
        frags.append(circle(sx, sy, 4, fill=c_fill, stroke=INK, sw=1))

    # Позначення спрацювання переривання AWD
    # Зона 1: Перевищення HTR
    frags.append(circle(250, 75, 9, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(line(250, 65, 250, 38, color=POS, sw=1.5))

    # Зона 2: Провал нижче LTR
    frags.append(circle(460, 320, 9, fill="#e0e7ff", stroke=NEG, sw=2))
    frags.append(line(460, 330, 460, 385, color=NEG, sw=1.5))
    frags.append(fitbox(380, 385, 160, 26, "AWD IRQ (Low Fault)", size=11, fill="#e0e7ff", stroke=NEG, bold=True))

    # Панель пояснень праворуч
    frags.append(rect(610, 50, 230, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(725, 78, "Особливості AWD", size=14, color=INK, bold=True))

    frags.append(fitbox(620, 95, 210, 80, "Цифрове вікно:\n• 12-бітна точність по коду\n• Не потребує ЦАП чи дільників\n• Програмна зміна HTR / LTR", size=11, fill="#ffffff", stroke=MUTED))

    frags.append(fitbox(620, 185, 210, 85, "Режими роботи:\n• Одиночний канал (Single)\n• Всі канали сканування\n(моніторинг температури NTC\nта напруги акумулятора)", size=11, fill="#ffffff", stroke=MUTED))

    frags.append(fitbox(620, 280, 210, 115, "Час реакції:\n• t_conv ~0.5–2 мкс (час АЦП)\n• Підходить для теплового\nзахисту й контролю живлення,\nале НЕ для миттєвого КЗ", size=11, fill="#fffbeb", stroke="#d97706"))

    return render(os.path.join(IMG_DIR, "analog-watchdog-window.svg"), w, h, *frags)


def fig_system_analog_protection_loop():
    """Фігура 4: Повний апаратно-аналоговий контур силового захисту в мікроконтролері."""
    w, h = 860, 480
    frags = []

    # Зовнішнє силове коло (ліворуч)
    frags.append(rect(20, 20, 180, 440, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=8))
    frags.append(text(110, 48, "Силовий каскад", size=14, color="#9a3412", bold=True))

    frags.append(fitbox(35, 75, 150, 60, "Напівміст / Інвертор\n(MOSFET / GaN / IGBT)\nШина живлення V_BUS", size=11, fill="#ffffff", stroke="#ea580c"))

    frags.append(fitbox(35, 160, 150, 65, "Драйвер затворів\n(Gate Driver)\nВходи PWM_H / PWM_L\nВхід Enable / Shutdown", size=11, fill="#ffffff", stroke="#ea580c"))

    frags.append(fitbox(35, 260, 150, 65, "Шунт Кельвіна\nв нижньому плечі\n(напр. 5 мОм, 4-провідний)", size=11, fill="#ffffff", stroke="#ea580c"))

    frags.append(fitbox(35, 360, 150, 80, "Критичний час:\nСтрум КЗ наростає за\ndi/dt = V_bus / L_stray\nРуйнація за < 1 мкс!", size=10, fill="#fee2e2", stroke=POS, bold=True))

    # Зв'язок від шунта до МК
    frags.append(arrow(185, 290, 230, 290, color=POS, sw=2))
    frags.append(text(205, 280, "V_shunt", size=11, color=POS, italic=True))

    # Корпус мікроконтролера (праворуч)
    frags.append(rect(230, 20, 610, 440, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(text(535, 48, "Мікроконтролер (Внутрішній апаратно-аналоговий захист)", size=15, color=INK, bold=True))

    # Вбудований OPAMP (PGA)
    frags.append(rect(250, 80, 180, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(340, 105, "Вбудований OPAMP", size=13, color=INK, bold=True))
    frags.append(fitbox(260, 120, 160, 105, "Режим PGA (Gain = 16x)\nПідсилення 50 мВ → 800 мВ\nКалібрований зсув нуля\n(TRIM < 200 мкВ)", size=11, fill="#f0fdf4", stroke=FIELD))

    # Лінія від шунта в OPAMP
    frags.append(line(230, 290, 240, 290, color=POS, sw=2))
    frags.append(line(240, 290, 240, 160, color=POS, sw=2))
    frags.append(arrow(240, 160, 250, 160, color=POS, sw=2))

    # Вихід OPAMP розгалужується внутрішньо
    frags.append(line(430, 160, 470, 160, color=POS, sw=2))
    frags.append(circle(470, 160, 4, fill=POS, stroke=POS))

    # Гілка 1: на АЦП + AWD (повільний / регулярний контур)
    frags.append(line(470, 160, 470, 100, color=LINE, sw=1.5))
    frags.append(arrow(470, 100, 510, 100, color=LINE, sw=1.5))

    frags.append(rect(510, 70, 150, 95, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(585, 92, "Швидкий АЦП", size=12, color=INK, bold=True))
    frags.append(fitbox(520, 102, 130, 55, "Оцифрування струму\nдля контуру FOC/PID\n+ AWD (перегрів)", size=10, fill="#f8fafc", stroke=MUTED))

    frags.append(arrow(660, 115, 700, 115, color=MUTED, sw=1.5))
    frags.append(fitbox(700, 85, 120, 60, "Ядро CPU\nРегулятор FOC\n(час ~10-50 мкс)", size=10, fill="#f1f5f9", stroke=MUTED))

    # Гілка 2: на швидкісний компаратор COMP (наносекундний контур)
    frags.append(line(470, 160, 470, 260, color=POS, sw=2.5))
    frags.append(arrow(470, 260, 510, 260, color=POS, sw=2.5))

    frags.append(rect(510, 190, 150, 140, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(585, 212, "Компаратор COMP", size=12, color=POS, bold=True))
    frags.append(fitbox(520, 222, 130, 95, "Поріг від ЦАП (DAC)\nГістерезис 20 мВ\nЧас спрацювання:\nt_prop ≈ 15-20 нс!", size=10, fill="#ffffff", stroke=POS))

    # Зв'язок від компаратора до Break-входу таймера
    frags.append(arrow(660, 260, 700, 260, color=POS, sw=2.5))
    frags.append(text(680, 248, "BKIN", size=11, color=POS, bold=True))

    # Блок силового таймера ШІМ
    frags.append(rect(700, 190, 125, 250, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(762, 212, "Таймер ШІМ", size=12, color=INK, bold=True))
    frags.append(fitbox(708, 222, 110, 100, "TIM1 / TIM8\nЛогіка Break:\nСкидання MOE=0\nза < 10 нс\nБлокування ШІМ", size=10, fill="#fef3c7", stroke="#d97706"))

    # Вихід ШІМ із таймера назад на драйвер затворів
    frags.append(fitbox(708, 335, 110, 95, "Виходи ШІМ:\nCH1 / CH1N\n(у стані вимкнено\nабо High-Z)", size=10, fill="#f1f5f9", stroke=MUTED))

    # Зворотна магістраль ШІМ до силового каскаду
    frags.append(line(700, 380, 680, 380, color=POS, sw=2))
    frags.append(line(680, 380, 680, 445, color=POS, sw=2))
    frags.append(line(680, 445, 195, 445, color=POS, sw=2))
    frags.append(line(195, 445, 195, 190, color=POS, sw=2))
    frags.append(arrow(195, 190, 185, 190, color=POS, sw=2))
    frags.append(text(450, 435, "Миттєве відключення ШІМ (Сумарний час аварійного захисту ≈ 25–35 нс)", size=11, color=POS, bold=True))

    return render(os.path.join(IMG_DIR, "system-analog-protection-loop.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_comp_internals_and_break()
    fig_opamp_pga_routing()
    fig_analog_watchdog_window()
    fig_system_analog_protection_loop()
    print("Всі фігури згенеровано успішно.")
