# -*- coding: utf-8 -*-
"""Фігури теми «Вбудована система оглядом».
Запуск: python figs.py -> ./img/*.svg
Імпортуємо svgkit зі scripts/."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: замкнений контур керування ──────────────────────────────────────
def fig_closed_loop():
    W, H = 780, 380
    parts = []

    # Фон блоків і контурів
    # Зовнішнє середовище / Фізичний світ
    parts.append(rect(40, 45, 700, 75, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    parts.append(text(390, 70, "ФІЗИЧНИЙ СВІТ І ОБ'ЄКТ КЕРУВАННЯ (ДРОН У ПОВІТРІ)", size=13, bold=True, color=INK))
    parts.append(text(390, 95, "Кутова орієнтація, швидкість обертання, висота, пориви вітру", size=11, color=MUTED))

    # Збурення (вітер)
    parts.append(arrow(390, 10, 390, 45, color=POS, sw=2))
    parts.append(text(390, 0, "Зовнішнє збурення (вітер)", size=11, bold=True, color=POS))

    # Ліва гілка: зчитування стану (давачі)
    parts.append(arrow(160, 120, 160, 160, color=NEG, sw=2))
    parts.append(text(160, 145, "стан (фізика)", size=10, color=NEG, anchor="end"))

    parts.append(fitbox(60, 160, 200, 60, "Давачі (сенсори)\nГіроскоп, акселерометр,\nбарометр, магнітометр", size=11, fill="#eaf0fd", stroke=NEG))

    parts.append(arrow(160, 220, 160, 260, color=NEG, sw=2))
    parts.append(text(160, 245, "електричний сигнал", size=10, color=NEG, anchor="end"))

    # Центральний блок: Обчислювальне ядро (МК)
    parts.append(rect(60, 260, 660, 105, fill="#ffffff", stroke=FIELD, sw=2, rx=8))
    parts.append(text(390, 282, "ОБЧИСЛЮВАЛЬНЕ ЯДРО ВБУДОВАНОЇ СИСТЕМИ (МІКРОКОНТРОЛЕР)", size=12, bold=True, color=FIELD))

    # Внутрішні блоки МК
    parts.append(fitbox(80, 298, 170, 55, "1. Зчитування та фільтрація\nОпитування АЦП / шини SPI,\nоцінка кута й швидкості", size=10.5, fill="#f4fbf6", stroke=FIELD))

    parts.append(arrow(250, 325, 290, 325, color=FIELD, sw=1.8))

    parts.append(fitbox(290, 298, 180, 55, "2. Розрахунок похибки\ne(t) = Бажаний стан −\nВиміряний стан", size=10.5, fill="#f4fbf6", stroke=FIELD))

    parts.append(arrow(470, 325, 510, 325, color=FIELD, sw=1.8))

    parts.append(fitbox(510, 298, 190, 55, "3. Закон керування (ПІД)\nФормування коригуючого\nмоменту та коду ШІМ", size=10.5, fill="#f4fbf6", stroke=FIELD))

    # Права гілка: вплив на світ (актуатори)
    parts.append(arrow(605, 260, 605, 220, color=POS, sw=2))
    parts.append(text(605, 245, "сигнал керування (ШІМ / DShot)", size=10, color=POS, anchor="start"))

    parts.append(fitbox(505, 160, 200, 60, "Виконавчі механізми\nДрайвери (ESC), BLDC-мотори,\nповітряні гвинти (тяга)", size=11, fill="#fdecea", stroke=POS))

    parts.append(arrow(605, 160, 605, 120, color=POS, sw=2))
    parts.append(text(605, 145, "механічна дія (момент і тяга)", size=10, color=POS, anchor="start"))

    render(os.path.join(IMG, "closed-loop-feedback.svg"), W, H, *parts,
           title="Замкнений контур керування вбудованої системи")


# ── Фігура 2: часовий детермінізм ─────────────────────────────────────────────
def fig_timing_determinism():
    W, H = 760, 360
    parts = []

    # Верхній трек: Твердий реальний час (Вбудований МК)
    parts.append(rect(30, 45, 700, 130, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(50, 68, "Твердий реальний час (Bare-metal / RTOS на мікроконтролері)", size=12, bold=True, color=FIELD, anchor="start"))

    # Вісь часу
    parts.append(line(50, 145, 710, 145, color=LINE, sw=1.5))
    parts.append(arrow(710, 145, 720, 145, color=LINE, sw=1.5))
    parts.append(text(715, 162, "t", size=11, color=MUTED))

    # 4 періоди по 150 px
    for i in range(4):
        x0 = 80 + i * 150
        # Дедлайн
        parts.append(line(x0, 85, x0, 150, color=MUTED, sw=1, dash="3 3"))
        parts.append(text(x0, 80, "T%d (0 µs)" % (i + 1), size=9.5, color=MUTED))
        # Робота
        parts.append(rect(x0, 115, 55, 30, fill="#d4edda", stroke=FIELD, sw=1.5, rx=3))
        parts.append(text(x0 + 27, 133, "220 µs", size=10, bold=True, color=FIELD))
        # Вільний час
        parts.append(text(x0 + 100, 133, "очікування таймера", size=9, color=MUTED))

    parts.append(text(50, 162, "Джитер < 1 µs: обчислення завжди закінчуються задовго до дедлайну (1000 µs)", size=10.5, color=FIELD, anchor="start"))

    # Нижній трек: Універсальна ОС
    parts.append(rect(30, 195, 700, 150, fill="#f8fafc", stroke=POS, sw=1.5, rx=6))
    parts.append(text(50, 218, "Універсальна ОС без гарантій реального часу (Linux / Windows)", size=12, bold=True, color=POS, anchor="start"))

    # Вісь часу
    parts.append(line(50, 305, 710, 305, color=LINE, sw=1.5))
    parts.append(arrow(710, 305, 720, 305, color=LINE, sw=1.5))
    parts.append(text(715, 322, "t", size=11, color=MUTED))

    # Періоди з затримками
    x0 = 80
    parts.append(line(x0, 235, x0, 310, color=MUTED, sw=1, dash="3 3"))
    parts.append(rect(x0, 275, 60, 30, fill="#d4edda", stroke=FIELD, sw=1.5, rx=3))
    parts.append(text(x0 + 30, 293, "250 µs", size=10, color=FIELD))

    # Другий період: витиснення ядром / скидання кешу
    x1 = 230
    parts.append(line(x1, 235, x1, 310, color=MUTED, sw=1, dash="3 3"))
    parts.append(rect(x1 + 30, 275, 80, 30, fill="#f8d7da", stroke=POS, sw=1.5, rx=3))
    parts.append(text(x1 + 70, 293, "затримка 450 µs", size=9.5, bold=True, color=POS))
    parts.append(text(x1 + 15, 260, "перемикання контексту", size=9, color=POS))

    # Третій період: зрив дедлайну через GC / page fault
    x2 = 380
    parts.append(line(x2, 235, x2, 310, color=MUTED, sw=1, dash="3 3"))
    parts.append(rect(x2 + 70, 275, 120, 30, fill="#f8d7da", stroke=POS, sw=1.8, rx=3))
    parts.append(text(x2 + 130, 293, "1300 µs (ЗРИВ ДЕДЛАЙНУ)", size=9.5, bold=True, color=POS))

    # Лінія наступного дедлайну
    x3 = 530
    parts.append(line(x3, 235, x3, 310, color=POS, sw=1.5, dash="2 2"))
    parts.append(text(x3, 245, "дедлайн T4 пропущено!", size=9.5, bold=True, color=POS))

    parts.append(text(50, 335, "Непередбачуваний джитер призводить до фазового запізнення та перекидання дрона", size=10.5, color=POS, anchor="start"))

    render(os.path.join(IMG, "timing-determinism.svg"), W, H, *parts,
           title="Часовий детермінізм: твердий реальний час проти непередбачуваної ОС")


# ── Фігура 3: анатомія апаратної платформи ────────────────────────────────────
def fig_hardware_anatomy():
    W, H = 780, 410
    parts = []

    # Центральний блок — МК
    parts.append(rect(230, 100, 320, 210, fill="#f0f7ff", stroke=NEG, sw=2, rx=8))
    parts.append(text(390, 124, "МІКРОКОНТРОЛЕР (MCU)", size=13, bold=True, color=NEG))

    # Підблоки МК
    parts.append(fitbox(245, 138, 140, 42, "CPU Ядро (Cortex-M)\nFPU, Регістри, NVIC", size=9.5, fill="#ffffff", stroke=NEG))
    parts.append(fitbox(395, 138, 140, 42, "Пам'ять\nFlash (код), SRAM (дані)", size=9.5, fill="#ffffff", stroke=NEG))
    parts.append(fitbox(245, 190, 140, 50, "Апаратні таймери\nШІМ-генератори,\nлічильники часу", size=9.5, fill="#ffffff", stroke=NEG))
    parts.append(fitbox(395, 190, 140, 50, "Комунікація\nSPI, I2C, UART,\nDMA-контролер", size=9.5, fill="#ffffff", stroke=NEG))
    parts.append(fitbox(245, 250, 290, 48, "Аналогова периферія та GPIO\nАЦП (ADC), компаратори, цифрові виводи", size=9.5, fill="#ffffff", stroke=NEG))

    # Лівий блок — Живлення
    parts.append(rect(20, 110, 160, 190, fill="#fffaf0", stroke="#d97706", sw=1.5, rx=6))
    parts.append(text(100, 132, "СИСТЕМА ЖИВЛЕННЯ", size=11, bold=True, color="#d97706"))
    parts.append(fitbox(35, 145, 130, 36, "LiPo Батарея\n3S–6S (11.1–25.2 В)", size=9.5, fill="#ffffff", stroke="#d97706"))
    parts.append(fitbox(35, 190, 130, 42, "Buck DCDC 5 В\nЖивлення логіки\nта радіоприймача", size=9.5, fill="#ffffff", stroke="#d97706"))
    parts.append(fitbox(35, 240, 130, 42, "LDO 3.3 В\nЧисте живлення\nдля сенсорів та МК", size=9.5, fill="#ffffff", stroke="#d97706"))
    parts.append(arrow(180, 205, 230, 205, color="#d97706", sw=1.8))
    parts.append(text(205, 195, "3.3 В", size=9.5, color="#d97706"))

    # Верхній блок — Сенсори
    parts.append(rect(230, 15, 320, 65, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    parts.append(text(390, 34, "СЕНСОРНИЙ БЛОК (ДАВАЧІ)", size=11, bold=True, color=NEG))
    parts.append(text(390, 54, "IMU (акселерометр + гіроскоп), барометр, магнітометр", size=9.5, color=INK))
    parts.append(arrow(390, 80, 390, 100, color=NEG, sw=1.8))
    parts.append(text(405, 92, "SPI (20 Мбіт/с)", size=9.5, color=NEG, anchor="start"))

    # Правий блок — Силова частина
    parts.append(rect(600, 110, 160, 190, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    parts.append(text(680, 132, "СИЛОВИЙ ВИХІД", size=11, bold=True, color=POS))
    parts.append(fitbox(615, 145, 130, 40, "4x ESC (регулятори)\nСилові MOSFET-модулі", size=9.5, fill="#ffffff", stroke=POS))
    parts.append(fitbox(615, 195, 130, 40, "4x BLDC-мотори\nБезколекторна тяга", size=9.5, fill="#ffffff", stroke=POS))
    parts.append(fitbox(615, 245, 130, 40, "Повітряні гвинти\nФормування сили тяги", size=9.5, fill="#ffffff", stroke=POS))
    parts.append(arrow(550, 205, 600, 205, color=POS, sw=1.8))
    parts.append(text(575, 195, "ШІМ/DShot", size=9.5, color=POS))

    # Нижній блок — Комунікація та телеметрія
    parts.append(rect(230, 330, 320, 65, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(390, 350, "РАДІОКАНАЛ І ТЕЛЕМЕТРІЯ", size=11, bold=True, color=FIELD))
    parts.append(text(390, 372, "Приймач керування (CRSF/SBUS), MAVLink-модем на ПК", size=9.5, color=INK))
    parts.append(arrow(390, 310, 390, 330, color=FIELD, sw=1.8))
    parts.append(text(405, 322, "UART (420 кбіт/с)", size=9.5, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "hardware-anatomy.svg"), W, H, *parts,
           title="Апаратна анатомія типової вбудованої системи керування")


# ── Фігура 4: багаторівнева ієрархія циклів прошивки ──────────────────────────
def fig_firmware_rate_loops():
    W, H = 760, 340
    parts = []

    # Рівень 1: 8 кГц — Апаратне переривання таймера
    parts.append(rect(40, 45, 680, 55, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    parts.append(text(60, 75, "8 кГц (кожні 125 µs)", size=12, bold=True, color=POS, anchor="start"))
    parts.append(text(240, 75, "Швидкий цикл: зчитування гіроскопа, PID кутової швидкості, видача DShot на мотори", size=11, color=INK, anchor="start"))

    parts.append(arrow(120, 100, 120, 120, color=MUTED, sw=1.5))
    parts.append(text(130, 112, "поділ частоти ÷ 4", size=9.5, color=MUTED, anchor="start"))

    # Рівень 2: 2 кГц — Орієнтація
    parts.append(rect(40, 120, 680, 55, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    parts.append(text(60, 150, "2 кГц (кожні 500 µs)", size=12, bold=True, color=NEG, anchor="start"))
    parts.append(text(240, 150, "Контур кутів: злиття вимірів акселерометра й гіроскопа (фільтр Махоні / Калмана)", size=11, color=INK, anchor="start"))

    parts.append(arrow(120, 175, 120, 195, color=MUTED, sw=1.5))
    parts.append(text(130, 187, "поділ частоти ÷ 40", size=9.5, color=MUTED, anchor="start"))

    # Рівень 3: 50 Гц — Навігація та висота
    parts.append(rect(40, 195, 680, 55, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(60, 225, "50 Гц (кожні 20 ms)", size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(text(240, 225, "Контур висоти та позиції: опитування барометра й GNSS, утримання координати", size=11, color=INK, anchor="start"))

    parts.append(arrow(120, 250, 120, 270, color=MUTED, sw=1.5))
    parts.append(text(130, 262, "поділ частоти ÷ 5", size=9.5, color=MUTED, anchor="start"))

    # Рівень 4: 10 Гц — Телеметрія та стан
    parts.append(rect(40, 270, 680, 55, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    parts.append(text(60, 300, "10 Гц (кожні 100 ms)", size=12, bold=True, color=MUTED, anchor="start"))
    parts.append(text(240, 300, "Фоновий моніторинг: напруга батареї, надсилання пакетів телеметрії, світлодіоди", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "firmware-rate-loops.svg"), W, H, *parts,
           title="Багаточастотна ієрархія завдань у прошивці керування")


if __name__ == "__main__":
    fig_closed_loop()
    fig_timing_determinism()
    fig_hardware_anatomy()
    fig_firmware_rate_loops()
    print("OK: 4 figures ->", IMG)
