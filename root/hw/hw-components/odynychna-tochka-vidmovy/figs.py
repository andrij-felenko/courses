# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Одинична точка відмови' (Single Point of Failure - SPOF)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_spof_power_vs_isolated_domains():
    """Фігура 1: Порівняння одноточкової системи живлення (SPOF) та відмовостійкої архітектури з ізольованими доменами."""
    w, h = 820, 480
    frags = []

    # Заголовок блоку 1: Вразлива архітектура
    frags.append(rect(15, 12, 790, 210, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(30, 36, "Вразлива архітектура: спільне джерело живлення (SPOF)", size=13, color=POS, bold=True, anchor="start"))

    # Елементи верхньої схеми
    frags.append(fitbox(35, 60, 130, 60, "Батарея / Вхід\nVIN (9–36 В)", size=12, fill="#ffffff", stroke=LINE, bold=True))
    frags.append(arrow(165, 90, 220, 90, color=LINE))

    # Спільний LDO (червоний контур як SPOF)
    frags.append(fitbox(220, 55, 140, 70, "Спільний LDO\n3.3 В (SPOF)", size=12, fill="#ffebee", stroke=POS, bold=True, sw=2))
    
    # Шина 3.3 В
    frags.append(line(360, 90, 430, 90, color=POS, sw=2.5))
    frags.append(line(430, 60, 430, 180, color=POS, sw=2.5))
    frags.append(text(440, 85, "+3.3 В", size=11, color=POS, bold=True, anchor="start"))

    # Споживачі
    frags.append(arrow(430, 65, 480, 65, color=LINE))
    frags.append(fitbox(480, 45, 130, 40, "Головний MCU", size=11, fill="#ffffff", stroke=LINE))

    frags.append(arrow(430, 120, 480, 120, color=LINE))
    frags.append(fitbox(480, 100, 130, 40, "Давачі I2C/SPI", size=11, fill="#ffffff", stroke=LINE))

    frags.append(arrow(430, 175, 480, 175, color=LINE))
    frags.append(fitbox(480, 155, 130, 40, "Аналогова АЦП-колонка", size=11, fill="#ffffff", stroke=LINE))

    # Пояснення аварії
    frags.append(fitbox(640, 75, 150, 90, "Аварія давача:\nКЗ на лінію GND\n— просідання до 0 В\n— колапс MCU та АЦП", size=11, fill="#ffebee", stroke=POS, color=POS, bold=False))
    frags.append(arrow(610, 120, 640, 120, color=POS, sw=1.5))


    # Заголовок блоку 2: Відмовостійка архітектура
    frags.append(rect(15, 240, 790, 225, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(30, 264, "Відмовостійка архітектура: дубльовані джерела та розділені домени (1+1 Hot-Standby)", size=13, color=FIELD, bold=True, anchor="start"))

    # Два незалежні входи
    frags.append(fitbox(35, 285, 115, 45, "Вхід живлення A\n(Головний)", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(35, 395, 115, 45, "Вхід живлення B\n(Резервний)", size=11, fill="#ffffff", stroke=LINE))

    # Незалежні перетворювачі
    frags.append(arrow(150, 307, 185, 307, color=LINE))
    frags.append(arrow(150, 417, 185, 417, color=LINE))
    frags.append(fitbox(185, 285, 110, 45, "DC-DC Регулятор A\n(3.3 В)", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(185, 395, 110, 45, "DC-DC Регулятор B\n(3.3 В)", size=11, fill="#ffffff", stroke=LINE))

    # Схема активного змішування Ideal Diode ORing
    frags.append(arrow(295, 307, 335, 335, color=FIELD, sw=1.5))
    frags.append(arrow(295, 417, 335, 385, color=FIELD, sw=1.5))
    frags.append(fitbox(335, 335, 130, 55, "Ideal Diode ORing\n(MOSFET-комутатор\nбез падіння Vf)", size=10, fill="#e8f5e9", stroke=FIELD, bold=True))

    # Вихід на ізольовані домени через eFuse / перемикачі
    frags.append(line(465, 362, 510, 362, color=FIELD, sw=2))
    frags.append(line(510, 290, 510, 435, color=FIELD, sw=2))

    # Домен 1 (MCU A)
    frags.append(arrow(510, 290, 550, 290, color=LINE))
    frags.append(fitbox(550, 275, 100, 32, "eFuse захист 1", size=10, fill="#ffffff", stroke=LINE))
    frags.append(arrow(650, 290, 675, 290, color=LINE))
    frags.append(fitbox(675, 275, 115, 32, "Домен 1: MCU ядро", size=10, fill="#ffffff", stroke=LINE, bold=True))

    # Домен 2 (Периферія)
    frags.append(arrow(510, 362, 550, 362, color=LINE))
    frags.append(fitbox(550, 347, 100, 32, "eFuse захист 2", size=10, fill="#ffffff", stroke=LINE))
    frags.append(arrow(650, 362, 675, 362, color=LINE))
    frags.append(fitbox(675, 347, 115, 32, "Домен 2: Давачі", size=10, fill="#ffffff", stroke=LINE, bold=True))

    # Домен 3 (Аналог)
    frags.append(arrow(510, 435, 550, 435, color=LINE))
    frags.append(fitbox(550, 420, 100, 32, "eFuse захист 3", size=10, fill="#ffffff", stroke=LINE))
    frags.append(arrow(650, 435, 675, 435, color=LINE))
    frags.append(fitbox(675, 420, 115, 32, "Домен 3: АЦП/Джерело Vref", size=10, fill="#ffffff", stroke=LINE, bold=True))

    render(os.path.join(OUT_DIR, "spof-power-vs-isolated-domains.svg"), w, h, *frags)


def fig_i2c_stuck_bus_and_buffer():
    """Фігура 2: Механізм зависання I2C (Stuck-Bus) та ізоляція шинним буфером."""
    w, h = 820, 420
    frags = []

    # Ліва частина: Зависання шини
    frags.append(rect(15, 15, 385, 390, fill="#fffafb", stroke=POS, sw=1.5, rx=8))
    frags.append(text(205, 40, "Блокування спільної шини (SPOF)", size=13, color=POS, bold=True))

    # Ведучий MCU
    frags.append(fitbox(30, 65, 100, 50, "Ведучий MCU\n(I2C Master)", size=10, fill="#ffffff", stroke=LINE, bold=True))

    # Лінії шини
    frags.append(line(130, 80, 380, 80, color=LINE, sw=2)) # SCL
    frags.append(line(130, 100, 380, 100, color=POS, sw=2)) # SDA
    frags.append(text(330, 74, "SCL", size=10, color=LINE, bold=True))
    frags.append(text(330, 115, "SDA (притягнуто до 0 В)", size=10, color=POS, bold=True))

    # Підтяжки до VDD
    frags.append(line(170, 80, 170, 55, color=LINE, sw=1.2))
    frags.append(line(190, 100, 190, 55, color=LINE, sw=1.2))
    frags.append(text(180, 50, "Rp +3.3В", size=9, color=MUTED))

    # Давач 1 (Справний)
    frags.append(line(240, 80, 240, 170, color=LINE, sw=1.5))
    frags.append(line(250, 100, 250, 170, color=LINE, sw=1.5))
    frags.append(fitbox(210, 170, 100, 50, "Давач 1\n(Справний)", size=10, fill="#ffffff", stroke=LINE))

    # Давач 2 (Несправний / завислий)
    frags.append(line(320, 80, 320, 250, color=LINE, sw=1.5))
    frags.append(line(330, 100, 330, 250, color=POS, sw=2))
    frags.append(fitbox(280, 250, 105, 60, "Давач 2 (Аварія)\nN-MOSFET відкритий\nSDA замкнено на GND", size=10, fill="#ffebee", stroke=POS, color=POS, bold=True))

    # Пояснення колапсу
    frags.append(fitbox(30, 325, 355, 65, "Результат: SDA=0 В паралізує всю лінію.\nВедучий не може надіслати START.\nЖоден справний давач не відповідає.", size=11, fill="#ffffff", stroke=POS, color=POS))


    # Права частина: Ізоляція шинним буфером із авто-відключенням
    frags.append(rect(415, 15, 390, 390, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(610, 40, "Ізоляція буфером зі Stuck-Bus Recovery", size=13, color=FIELD, bold=True))

    # Ведучий MCU
    frags.append(fitbox(430, 65, 95, 50, "Ведучий MCU\n(I2C Master)", size=10, fill="#ffffff", stroke=LINE, bold=True))

    # Основна шина (Сегмент A)
    frags.append(line(525, 80, 570, 80, color=FIELD, sw=2))
    frags.append(line(525, 100, 570, 100, color=FIELD, sw=2))

    # Буфер I2C
    frags.append(fitbox(570, 65, 110, 95, "I2C Буфер-ізолятор\nз таймером зависання\n(Stuck-Bus Timer\nt > 30 мс)", size=9, fill="#e8f5e9", stroke=FIELD, bold=True))

    # Справний давач на основному сегменті
    frags.append(line(550, 100, 550, 185, color=FIELD, sw=1.5))
    frags.append(fitbox(500, 185, 100, 45, "Давач 1\n(Працює штатно)", size=10, fill="#ffffff", stroke=FIELD, bold=True))

    # Відсічений аварійний сегмент B
    frags.append(line(680, 80, 715, 80, color=LINE, sw=1.5, dash="3,3"))
    frags.append(line(680, 100, 715, 100, color=POS, sw=2, dash="3,3"))
    frags.append(text(710, 70, "Розмикання ключа", size=9, color=POS, bold=True, anchor="middle"))

    # Аварійний давач на ізольованому сегменті
    frags.append(fitbox(695, 185, 95, 60, "Давач 2 (Аварія)\nSDA=0 В\n(ІЗОЛЬОВАНО)", size=10, fill="#ffebee", stroke=POS, color=POS))
    frags.append(line(742, 100, 742, 185, color=POS, sw=1.5, dash="3,3"))

    # Пояснення успіху
    frags.append(fitbox(430, 310, 360, 80, "Апаратна ізоляція:\n1. Буфер фіксує SDA=LOW понад 30 мс.\n2. Внутрішній ключ відсікає Сегмент B.\n3. Сегмент A підтягується до 3.3 В.\n4. MCU продовжує опитувати Давач 1.", size=10, fill="#ffffff", stroke=FIELD, color=INK))

    render(os.path.join(OUT_DIR, "i2c-stuck-bus-mechanism-and-buffer.svg"), w, h, *frags)


def fig_tmr_2oo3_voting():
    """Фігура 3: Архітектура потрійного модульного резервування 2oo3 (TMR)."""
    w, h = 820, 440
    frags = []

    frags.append(rect(15, 15, 790, 410, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(410, 40, "Архітектура потрійного модульного резервування 2oo3 (TMR) з мажоритарним арбітром", size=13, color=INK, bold=True))

    # Вхідний сигнал
    frags.append(line(35, 220, 95, 220, color=LINE, sw=2))
    frags.append(line(95, 100, 95, 340, color=LINE, sw=2))
    frags.append(text(65, 210, "Вхідні дані", size=11, color=INK, bold=True))

    # Три канали
    # Канал 1
    frags.append(arrow(95, 100, 140, 100, color=LINE))
    frags.append(fitbox(140, 75, 140, 50, "Канал A (MCU 1)\nРезультат: 1", size=11, fill="#ffffff", stroke=FIELD, bold=True))

    # Канал 2 (збійний)
    frags.append(arrow(95, 220, 140, 220, color=LINE))
    frags.append(fitbox(140, 195, 140, 50, "Канал B (MCU 2)\nРезультат: 0 (ЗБІЙ)", size=11, fill="#ffebee", stroke=POS, color=POS, bold=True))

    # Канал 3
    frags.append(arrow(95, 340, 140, 340, color=LINE))
    frags.append(fitbox(140, 315, 140, 50, "Канал C (MCU 3)\nРезультат: 1", size=11, fill="#ffffff", stroke=FIELD, bold=True))

    # Лінії до мажоритарного блоку
    frags.append(arrow(280, 100, 350, 180, color=FIELD, sw=1.8))
    frags.append(arrow(280, 220, 350, 220, color=POS, sw=1.8))
    frags.append(arrow(280, 340, 350, 260, color=FIELD, sw=1.8))

    # Блок мажоритарного арбітражу 2oo3
    frags.append(rect(350, 150, 200, 140, fill="#e8f4fd", stroke="#2457d6", sw=2, rx=6))
    frags.append(text(450, 175, "Мажоритарний орган", size=12, color="#2457d6", bold=True))
    frags.append(text(450, 195, "2-out-of-3 Voter", size=11, color=INK))
    frags.append(text(450, 220, "Y = (A∧B) ∨ (B∧C) ∨ (A∧C)", size=11, color=INK, bold=True))
    frags.append(text(450, 245, "Голосування: 2 проти 1", size=10, color=FIELD, bold=True))
    frags.append(text(450, 265, "Маскування відмови B", size=10, color=FIELD))

    # Вихідний сигнал
    frags.append(arrow(550, 220, 640, 220, color=FIELD, sw=2.5))
    frags.append(fitbox(640, 195, 145, 50, "Вихідний сигнал\nІстинне значення: 1\n(Безпечна робота)", size=11, fill="#f0fdf4", stroke=FIELD, bold=True))

    # Блок діагностики розбіжностей
    frags.append(arrow(450, 290, 450, 340, color=POS, sw=1.5))
    frags.append(fitbox(350, 340, 200, 65, "Діагностика FMECA:\nРозбіжність каналу B!\n— Запис у журнал відмов\n— Запит техобслуговування", size=10, fill="#fff3e0", stroke="#f57c00", color="#e65100", bold=False))

    render(os.path.join(OUT_DIR, "tmr-2oo3-voting-architecture.svg"), w, h, *frags)


def fig_window_watchdog_timing():
    """Фігура 4: Часова діаграма роботи віконного сторожового таймера (Window Watchdog)."""
    w, h = 820, 380
    frags = []

    frags.append(rect(15, 15, 790, 350, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(410, 40, "Часові інтервали віконного сторожового таймера (Window Watchdog)", size=13, color=INK, bold=True))

    # Горизонтальна вісь часу
    frags.append(arrow(60, 220, 760, 220, color=LINE, sw=2))
    frags.append(text(750, 245, "Час (t)", size=11, color=INK, bold=True, anchor="end"))

    # Початок циклу t=0
    frags.append(line(120, 120, 120, 240, color=LINE, sw=1.5))
    frags.append(text(120, 255, "t = 0\n(Скид таймера)", size=10, color=INK, bold=True))

    # Поріг t_min (Нижня межа вікна)
    frags.append(line(320, 120, 320, 240, color=POS, sw=1.5, dash="4,3"))
    frags.append(text(320, 255, "t_min\n(Рання межа)", size=10, color=POS, bold=True))

    # Поріг t_max (Верхня межа вікна / таймаут)
    frags.append(line(560, 120, 560, 240, color=POS, sw=1.5, dash="4,3"))
    frags.append(text(560, 255, "t_max\n(Таймаут)", size=10, color=POS, bold=True))

    # Зона 1: Занадто ранній скид (АВАРІЯ)
    frags.append(rect(120, 130, 200, 70, fill="#ffebee", stroke=POS, sw=1, rx=4))
    frags.append(text(220, 155, "ЗАБОРОНЕНА ЗОНА", size=10, color=POS, bold=True))
    frags.append(text(220, 175, "Раннє годування сторожа\n(Збій / шалений цикл)", size=9, color=POS))
    frags.append(text(220, 195, "→ АПАРТНИЙ СКИД MCU", size=9, color=POS, bold=True))

    # Зона 2: Дозволене вікно (НОРМА)
    frags.append(rect(320, 130, 240, 70, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(440, 155, "ДОЗВОЛЕНЕ ВІКНО", size=11, color=FIELD, bold=True))
    frags.append(text(440, 175, "Штатне скидання сторожа", size=10, color=FIELD))
    frags.append(text(440, 195, "t_min < t_refresh < t_max", size=10, color=FIELD, bold=True))

    # Зона 3: Запізнілий скид (АВАРІЯ)
    frags.append(rect(560, 130, 170, 70, fill="#ffebee", stroke=POS, sw=1, rx=4))
    frags.append(text(645, 155, "ТАЙМАУТ", size=10, color=POS, bold=True))
    frags.append(text(645, 175, "Зависання коду / дедлок", size=9, color=POS))
    frags.append(text(645, 195, "→ АПАРАТНИЙ СКИД MCU", size=9, color=POS, bold=True))

    # Стрілка штатного імпульсу
    frags.append(arrow(440, 100, 440, 130, color=FIELD, sw=2))
    frags.append(text(440, 85, "Штатний імпульс WDI (Good Feed)", size=10, color=FIELD, bold=True))

    # Пояснення переваги над звичайним WDT
    frags.append(fitbox(60, 290, 700, 60, "Перевага віконного сторожа над звичайним: якщо помилка в коді призводить до нескінченного циклу\nабо зациклення переривання, де команда скидання сторожа викликається занадто швидко (t < t_min),\nзвичайний сторож не помітить зависання, а віконний сторож миттєво перезавантажить систему.", size=10, fill="#f8f9fa", stroke=LINE))

    render(os.path.join(OUT_DIR, "window-watchdog-state-diagram.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_spof_power_vs_isolated_domains()
    fig_i2c_stuck_bus_and_buffer()
    fig_tmr_2oo3_voting()
    fig_window_watchdog_timing()
    print("All figures successfully generated in", OUT_DIR)
