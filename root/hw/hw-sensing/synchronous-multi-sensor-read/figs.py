# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Асинхронне опитування проти апаратного синхронного зчитування ──
def fig_skew_vs_sync():
    W, H = 780, 440
    parts = []
    parts.append(text(W/2, 24, "Асинхронне опитування проти апаратної синхронізації вибірок", size=15, bold=True))

    # Роздільник двох частин
    parts.append(line(40, 220, 740, 220, color=MUTED, sw=1.0, dash="4 4"))

    # ── Верхній блок: Асинхронне опитування (Phase Skew + Jitter) ──
    parts.append(text(50, 48, "Асинхронний збір (програмний цикл опитування):", size=13, bold=True, color=POS, anchor="start"))

    # Вісь часу верхнього блоку
    ax1_y = 175
    parts.append(line(60, ax1_y, 730, ax1_y, color=LINE, sw=1.5))
    parts.append(text(735, ax1_y+4, "t", size=12, color=MUTED, anchor="start"))

    # Подія 1: Фізичний рух / збурення
    box_event, _, _ = textbox(130, 80, "Фізичне збурення\n(стрибок кута / прискорення)", size=11, fill="#fff2f0", stroke=POS, color=POS, bold=True)
    parts.append(box_event)
    parts.append(line(130, 106, 130, ax1_y, color=POS, sw=1.5, dash="3 3"))

    # IMU вибірка (готова о 130, зчитана о 160)
    parts.append(circle(130, ax1_y, 4, fill=POS, stroke=POS))
    parts.append(rect(160, 125, 110, 26, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    parts.append(text(215, 142, "Зчитування IMU (SPI)", size=10.5, color=POS, bold=True))
    parts.append(line(130, 138, 160, 138, color=POS, sw=1.2))

    # Mag вибірка (готова о 130, зчитана о 340 через блокування шини та планувальник RTOS)
    parts.append(rect(340, 125, 135, 26, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    parts.append(text(407, 142, "Зчитування Mag (I2C)", size=10.5, color=POS, bold=True))

    # Стрілка розбігу фаз (Phase Skew)
    parts.append(line(270, 138, 340, 138, color=POS, sw=1.8))
    parts.append(arrow(270, 138, 340, 138, color=POS, sw=1.8))
    box_skew, _, _ = textbox(410, 85, "Розбіг фаз (Phase Skew) Δt\nДані стосуються різних моментів!", size=11, fill="#ffffff", stroke=POS, color=POS, bold=True)
    parts.append(box_skew)

    # Наслідок у фільтрі
    box_err, _, _ = textbox(630, 138, "Помилка синтезу:\nФантомний дрейф EKF", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(box_err)

    # ── Нижній блок: Апаратна синхронізація ──
    parts.append(text(50, 245, "Апаратна синхронізація (FSYNC / DRDY + Timer TRGO + DMA):", size=13, bold=True, color=FIELD, anchor="start"))

    # Вісь часу нижнього блоку
    ax2_y = 385
    parts.append(line(60, ax2_y, 730, ax2_y, color=LINE, sw=1.5))
    parts.append(text(735, ax2_y+4, "t", size=12, color=MUTED, anchor="start"))

    # Загальний тактовий імпульс / FSYNC
    parts.append(line(130, 265, 130, ax2_y, color=FIELD, sw=2))
    parts.append(circle(130, 265, 4, fill=FIELD, stroke=FIELD))
    box_sync, _, _ = textbox(130, 285, "Спільний FSYNC / TRGO\nЄдиний такт квантування", size=11, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_sync)

    # Паралельні перетворення та зчитування DMA
    parts.append(rect(150, 335, 140, 24, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(220, 351, "DMA SPI1: Кадр IMU", size=10.5, color=FIELD, bold=True))

    parts.append(rect(150, 365, 140, 24, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(220, 381, "DMA SPI2: Кадр Mag", size=10.5, color=FIELD, bold=True))

    # Захоплення апаратної мітки часу
    box_latch, _, _ = textbox(410, 355, "Апаратна мітка часу\nЗахоплення таймером без затримок CPU", size=11, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_latch)

    # Узгоджений стан
    box_ok, _, _ = textbox(630, 355, "Узгоджені вибірки:\nФазовий розбіг ≈ 0", size=11, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_ok)

    render(os.path.join(IMG, "skew-vs-sync.svg"), W, H, *parts)


# ── Фігура 2: Апаратна архітектура зв'язку та синхронізації ──────────────────
def fig_hardware_architecture():
    W, H = 800, 480
    parts = []
    parts.append(text(W/2, 24, "Апаратна архітектура координованого зчитування сенсорної матриці", size=15, bold=True))

    # Контейнер мікроконтролера (MCU)
    parts.append(rect(40, 50, 360, 400, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    parts.append(text(220, 75, "Мікроконтролер польотного контролера (MCU)", size=13, bold=True))

    # Внутрішні блоки MCU
    # 1. Master Timer
    box_tim, _, _ = textbox(130, 130, "Головний таймер\n(TIM1 TRGO @ 1 кГц)", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(box_tim)

    # 2. Timer Capture (Latching)
    box_cap, _, _ = textbox(310, 130, "Блок захоплення\n(TIM2 32-bit @ 1 МГц)", size=11, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(box_cap)

    # 3. DMA Controller
    box_dma, _, _ = textbox(220, 240, "Контролер прямого доступу (DMA)\nБагатоканальний асинхронний трансфер", size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_dma)

    # 4. Bus Peripherals
    parts.append(rect(60, 310, 85, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(102, 335, "SPI1", size=12, bold=True))

    parts.append(rect(175, 310, 85, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(217, 335, "SPI2", size=12, bold=True))

    parts.append(rect(290, 310, 85, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(332, 335, "I2C1 / SPI3", size=11.5, bold=True))

    # 5. RAM Ring Buffers
    box_ram, _, _ = textbox(220, 410, "Кільцевий буфер вибірок у SRAM\n(Дані сенсорів + точні мітки часу)", size=11, fill="#ffffff", stroke=LINE, color=INK, bold=True)
    parts.append(box_ram)

    # Зв'язки всередині MCU
    parts.append(arrow(130, 160, 130, 215, color=POS, sw=1.5))
    parts.append(arrow(220, 265, 102, 310, color=FIELD, sw=1.5))
    parts.append(arrow(220, 265, 217, 310, color=FIELD, sw=1.5))
    parts.append(arrow(220, 265, 332, 310, color=FIELD, sw=1.5))
    parts.append(arrow(220, 350, 220, 385, color=LINE, sw=1.5))

    # ── Зовнішні сенсори (праворуч) ──
    # IMU 1 (Primary)
    parts.append(rect(480, 70, 280, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(620, 95, "Основний IMU (ICM-42688-P)", size=12, bold=True))
    parts.append(text(620, 115, "Гіроскоп + Акселерометр (FIFO 2 кБ)", size=10.5, color=MUTED))
    parts.append(text(620, 132, "Входи: FSYNC | Виходи: DRDY, SPI1", size=10, color=MUTED))

    # IMU 2 (Secondary / Резервний)
    parts.append(rect(480, 170, 280, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(620, 195, "Резервний IMU (IIM-42652)", size=12, bold=True))
    parts.append(text(620, 215, "Гіроскоп + Акселерометр (FIFO 2 кБ)", size=10.5, color=MUTED))
    parts.append(text(620, 232, "Входи: FSYNC | Виходи: DRDY, SPI2", size=10, color=MUTED))

    # Барометр + Магнітометр
    parts.append(rect(480, 270, 280, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(620, 295, "Магнітометр + Барометр", size=12, bold=True))
    parts.append(text(620, 315, "LIS3MDL / BMP390 (50–100 Гц)", size=10.5, color=MUTED))
    parts.append(text(620, 332, "Виходи: DRDY / INT, I2C1", size=10, color=MUTED))

    # GNSS модуль
    parts.append(rect(480, 370, 280, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(620, 395, "GNSS приймач (u-blox F9P)", size=12, bold=True))
    parts.append(text(620, 415, "Позиція 10 Гц + PPS фронт 1 Гц", size=10.5, color=MUTED))
    parts.append(text(620, 432, "Виходи: PPS (TIMEPULSE), UART", size=10, color=MUTED))

    # ── Лінії зв'язку між MCU та сенсорами ──
    # FSYNC з TRGO до IMU 1 та IMU 2
    parts.append(line(130, 105, 430, 105, color=POS, sw=1.8))
    parts.append(arrow(430, 105, 480, 105, color=POS, sw=1.8))
    parts.append(line(430, 105, 430, 205, color=POS, sw=1.8))
    parts.append(arrow(430, 205, 480, 205, color=POS, sw=1.8))
    parts.append(text(450, 95, "FSYNC", size=10, color=POS, bold=True))

    # DRDY від IMU1 до Timer Capture
    parts.append(line(480, 125, 440, 125, color=NEG, sw=1.5))
    parts.append(line(440, 125, 440, 140, color=NEG, sw=1.5))
    parts.append(arrow(440, 140, 380, 140, color=NEG, sw=1.5))
    parts.append(text(445, 137, "DRDY", size=9.5, color=NEG, bold=True))

    # PPS від GNSS до Timer Capture
    parts.append(line(480, 410, 420, 410, color=NEG, sw=1.5))
    parts.append(line(420, 410, 420, 150, color=NEG, sw=1.5))
    parts.append(arrow(420, 150, 380, 150, color=NEG, sw=1.5))
    parts.append(text(435, 380, "PPS", size=10, color=NEG, bold=True))

    # Шини даних (SPI1, SPI2, I2C1)
    parts.append(line(102, 350, 102, 360, color=FIELD, sw=1.5))
    parts.append(line(102, 360, 450, 360, color=FIELD, sw=1.5))
    parts.append(line(450, 360, 450, 115, color=FIELD, sw=1.5))
    parts.append(arrow(450, 115, 480, 115, color=FIELD, sw=1.5))

    parts.append(line(217, 350, 217, 370, color=FIELD, sw=1.5))
    parts.append(line(217, 370, 460, 370, color=FIELD, sw=1.5))
    parts.append(line(460, 370, 460, 215, color=FIELD, sw=1.5))
    parts.append(arrow(460, 215, 480, 215, color=FIELD, sw=1.5))

    parts.append(line(332, 350, 480, 320, color=FIELD, sw=1.5))
    parts.append(arrow(332, 350, 480, 320, color=FIELD, sw=1.5))

    render(os.path.join(IMG, "hardware-sync-architecture.svg"), W, H, *parts)


# ── Фігура 3: Часова шкала EKF та ретроспективне зведення ─────────────────────
def fig_ekf_timeline():
    W, H = 780, 360
    parts = []
    parts.append(text(W/2, 24, "Ретроспективне зведення вибірок у розширеному фільтрі Калмана (EKF)", size=15, bold=True))

    # Вісь часу фільтра
    ax_y = 130
    parts.append(line(60, ax_y, 720, ax_y, color=LINE, sw=1.8))
    parts.append(text(725, ax_y+4, "t", size=13, color=MUTED, anchor="start"))

    # Високочастотні кроки IMU (1 кГц)
    steps_x = [100, 160, 220, 280, 340, 400, 460, 520, 580, 640]
    for i, sx in enumerate(steps_x):
        parts.append(line(sx, ax_y-8, sx, ax_y+8, color=LINE, sw=1.5))
        parts.append(circle(sx, ax_y, 3, fill=FIELD, stroke=FIELD))
        parts.append(text(sx, ax_y+22, "t%d" % i, size=10, color=MUTED))

    # Кільцевий буфер станів (SRAM Ring Buffer)
    parts.append(rect(80, 170, 580, 45, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(370, 198, "Кільцевий буфер збережених навігаційних станів x̂(tk) та коваріацій P(tk)", size=11, bold=True, color=INK))

    # Момент запізнілого вимірювання (наприклад, GNSS або барометра)
    t_meas_x = steps_x[3]  # t3
    parts.append(line(t_meas_x, ax_y-55, t_meas_x, ax_y, color=NEG, sw=2, dash="3 3"))
    parts.append(circle(t_meas_x, ax_y-55, 5, fill="#ffffff", stroke=NEG, sw=2))
    box_meas, _, _ = textbox(t_meas_x-20, 55, "Вимірювання z(t3)\n(GNSS / Барометр / Mag)", size=10.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(box_meas)

    # Прибуття вимірювання в MCU на поточному кроці t9
    t_now_x = steps_x[9]  # t9
    parts.append(line(t_now_x, ax_y-55, t_now_x, ax_y, color=POS, sw=2, dash="3 3"))
    box_now, _, _ = textbox(t_now_x, 55, "Поточний час tnow = t9\n(Отримання пакета по шині)", size=10.5, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(box_now)

    # Ретроспективне оновлення (Rewind & Update)
    parts.append(line(t_now_x, 240, t_meas_x, 240, color=POS, sw=2))
    parts.append(arrow(t_now_x, 240, t_meas_x, 240, color=POS, sw=2))
    box_rewind, _, _ = textbox((t_meas_x+t_now_x)/2, 255, "1. Відкат (Rewind): зчитування стану x̂(t3) з буфера та корекція EKF", size=11, fill="#ffffff", stroke=POS, color=POS, bold=True)
    parts.append(box_rewind)

    # Пряме перепрогравання (Fast-forward propagation)
    parts.append(line(t_meas_x, 305, t_now_x, 305, color=FIELD, sw=2))
    parts.append(arrow(t_meas_x, 305, t_now_x, 305, color=FIELD, sw=2))
    box_ffwd, _, _ = textbox((t_meas_x+t_now_x)/2, 320, "2. Пряме перепрогравання (Fast-Forward): інтегрування IMU від t3 до t9", size=11, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box_ffwd)

    render(os.path.join(IMG, "ekf-delayed-fusion-timeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_skew_vs_sync()
    fig_hardware_architecture()
    fig_ekf_timeline()
    print("Figures generated successfully.")
