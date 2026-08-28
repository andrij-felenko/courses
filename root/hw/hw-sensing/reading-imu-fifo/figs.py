# -*- coding: utf-8 -*-
"""Фігури до статті «Читання апаратного FIFO в IMU» (reading-imu-fifo-d.md).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#caa24a"
ACCENT_BLUE = "#1e40af"
ACCENT_GREEN = "#15803d"
ACCENT_RED = "#b91c1c"
ACCENT_PURPLE = "#6b21a8"
PANEL_BG = "#f8fafc"
PANEL_BORDER = "#cbd5e1"

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))

# ── 1. Внутрішня апаратна архітектура IMU з FIFO ─────────────────────────────
def fig_imu_fifo_architecture():
    W, H = 960, 480
    f = [
        text(W / 2, 28, "Апаратна архітектура буфера FIFO в інерційному модулі (IMU)", size=17, bold=True),
        text(W / 2, 48, "Конвеєр перетворення: від синхронного АЦП до вичитування через SPI DMA", size=11, color=MUTED, italic=True)
    ]

    # Область сенсора IMU (ліворуч)
    f.append(rect(30, 70, 520, 380, fill="#f0fdf4", stroke=ACCENT_GREEN, sw=2, rx=8))
    f.append(text(290, 95, "Кристал сенсора IMU (наприклад, ICM-42688-P / LSM6DSO)", size=13, bold=True, color=ACCENT_GREEN))

    # Сенсорні блоки
    f.append(fitbox(50, 120, 110, 60, "MEMS\nАкселерометр", size=11, bold=True, fill="#ffffff", stroke="#059669"))
    f.append(fitbox(50, 200, 110, 60, "MEMS\nГіроскоп", size=11, bold=True, fill="#ffffff", stroke="#059669"))
    f.append(fitbox(50, 280, 110, 50, "Датчик\nТемператури", size=10, bold=True, fill="#ffffff", stroke="#059669"))

    # Блок синхронного АЦП
    f.append(fitbox(180, 120, 90, 210, "Синхронний\n24-бітний\nΣΔ-АЦП\n\n(Lock-step\nSampling)", size=10, bold=True, fill="#e0f2fe", stroke=ACCENT_BLUE))

    # Стрілки від MEMS до АЦП
    f.append(arrow(160, 150, 180, 150, color=LINE, sw=1.5))
    f.append(arrow(160, 230, 180, 230, color=LINE, sw=1.5))
    f.append(arrow(160, 305, 180, 305, color=LINE, sw=1.5))

    # Цифрова обробка та ODR
    f.append(fitbox(290, 120, 90, 210, "DSP:\nФільтри AAF\n+\nДециматор\nODR\n(100 Гц..8 кГц)", size=10, bold=True, fill="#ede9fe", stroke=ACCENT_PURPLE))
    f.append(arrow(270, 225, 290, 225, color=LINE, sw=1.5))

    # Кільцевий SRAM FIFO
    f.append(fitbox(400, 120, 130, 140, "SRAM FIFO\n(512 – 4096 байт)\n───────────────\nКільцевий буфер\n[Head ➔ Data ➔ Tail]", size=10, bold=True, fill="#fef3c7", stroke=GOLD))
    f.append(arrow(380, 190, 400, 190, color=LINE, sw=1.5))

    # Логіка Watermark / Лічильник байтів
    f.append(fitbox(400, 280, 130, 50, "Лічильник FIFO_COUNT\nПорівнювач Watermark", size=9, bold=True, fill="#fee2e2", stroke=ACCENT_RED))
    f.append(arrow(465, 260, 465, 280, color=LINE, sw=1.5))

    # Генератор тактування
    f.append(fitbox(180, 355, 200, 40, "Внутрішній PLL / RC (Кварцовий ODR)", size=10, bold=True, fill="#ffffff", stroke=MUTED))
    f.append(arrow(280, 355, 280, 330, color=MUTED, sw=1.5))

    # Шина між IMU та Хостом
    f.append(arrow(530, 180, 600, 180, color=ACCENT_BLUE, sw=2))
    f.append(text(565, 170, "SPI Bus\n(до 24 МГц)", size=9, bold=True, color=ACCENT_BLUE))

    f.append(arrow(530, 305, 600, 305, color=ACCENT_RED, sw=2))
    f.append(text(565, 295, "INT (Watermark)", size=9, bold=True, color=ACCENT_RED))

    # Область мікроконтролера Хоста (праворуч)
    f.append(rect(600, 70, 330, 380, fill="#eff6ff", stroke=ACCENT_BLUE, sw=2, rx=8))
    f.append(text(765, 95, "Мікроконтролер Хоста (Cortex-M / ESP32)", size=13, bold=True, color=ACCENT_BLUE))

    # EXTI / DMA / Ring Buffer
    f.append(fitbox(620, 280, 110, 50, "EXTI ISR\n(Watermark Trig)", size=10, bold=True, fill="#ffffff", stroke=ACCENT_RED))
    f.append(fitbox(620, 150, 110, 60, "SPI Master +\nDMA Engine", size=10, bold=True, fill="#ffffff", stroke=ACCENT_BLUE))
    f.append(arrow(675, 280, 675, 210, color=ACCENT_RED, sw=1.5))

    f.append(fitbox(755, 150, 155, 60, "Подвійний буфер RAM\n(Ping-Pong / Ring)", size=10, bold=True, fill="#ffffff", stroke="#0284c7"))
    f.append(arrow(730, 180, 755, 180, color=ACCENT_BLUE, sw=1.5))

    f.append(fitbox(755, 245, 155, 85, "Парсер кадрів\nта алгоритм орієнтації\n(EKF / Madgwick / AHRS)\n───────────────\ndt = 1 / ODR_hw", size=10, bold=True, fill="#f0fdf4", stroke=ACCENT_GREEN))
    f.append(arrow(832, 210, 832, 245, color=LINE, sw=1.5))

    render(os.path.join(IMG, "imu-fifo-architecture.svg"), W, H, *f)


# ── 2. Джиттер опитування проти апаратного ODR FIFO ─────────────────────────
def fig_polling_vs_fifo_jitter():
    W, H = 940, 440
    f = [
        text(W / 2, 28, "Усунення джиттеру дискретизації: опитування CPU проти апаратного FIFO", size=17, bold=True),
        text(W / 2, 48, "Програмна нестабільність інтервалу dt руйнує інтегрування; FIFO фіксує dt апаратно", size=11, color=MUTED, italic=True)
    ]

    # Верхня панель: Опитування за таймером MCU
    f.append(rect(30, 70, 880, 160, fill="#fff1f2", stroke="#fda4af", sw=1.5, rx=6))
    f.append(text(50, 95, "1. Опитування регістра або обробка DRDY процесором (Software Jitter):", size=12, bold=True, anchor="start", color=ACCENT_RED))

    # Вісь часу верхня
    f.append(arrow(80, 150, 860, 150, color=LINE, sw=1.5))
    f.append(text(870, 154, "t", size=12, bold=True, color=LINE, anchor="start"))

    # Ідеальні мітки
    ideal_x = [150, 270, 390, 510, 630, 750]
    for x in ideal_x:
        f.append(line(x, 140, x, 160, color=MUTED, sw=1, dash="2 2"))

    # Реальні моменти опитування з джиттером
    real_x = [152, 305, 380, 545, 620, 775]
    for i, rx in enumerate(real_x):
        f.append(circle(rx, 150, 6, fill=ACCENT_RED, stroke=LINE, sw=1.5))
        f.append(line(rx, 125, rx, 150, color=ACCENT_RED, sw=1.5))
        f.append(text(rx, 118, "IRQ %d" % (i+1), size=9, bold=True, color=ACCENT_RED))

    # Підписи інтервалів dt
    f.append(text(228, 175, "dt = 1.28 мс", size=10, bold=True, color=ACCENT_RED))
    f.append(text(342, 175, "dt = 0.62 мс", size=10, bold=True, color=ACCENT_RED))
    f.append(text(462, 175, "dt = 1.37 мс", size=10, bold=True, color=ACCENT_RED))
    f.append(text(582, 175, "dt = 0.62 мс", size=10, bold=True, color=ACCENT_RED))
    f.append(text(698, 175, "dt = 1.29 мс", size=10, bold=True, color=ACCENT_RED))

    f.append(text(470, 215, "Латентність переривань, конфлікти пріоритетів та RTOS спотворюють dt → помилка інтегрування кута", size=10, color=ACCENT_RED, italic=True))

    # Нижня панель: Апаратний FIFO
    f.append(rect(30, 250, 880, 165, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    f.append(text(50, 275, "2. Апаратна фіксація вибірок в IMU FIFO та пакетне вичитування (Hardware ODR):", size=12, bold=True, anchor="start", color=ACCENT_GREEN))

    # Вісь часу нижня
    f.append(arrow(80, 335, 860, 335, color=LINE, sw=1.5))
    f.append(text(870, 339, "t", size=12, bold=True, color=LINE, anchor="start"))

    # Апаратні вибірки (ідеально рівномірні)
    fifo_samples = [140, 200, 260, 320, 380, 440, 500, 560, 620, 680, 740, 800]
    for sx in fifo_samples:
        f.append(circle(sx, 335, 4, fill=ACCENT_GREEN, stroke=LINE, sw=1))
        f.append(line(sx, 325, sx, 335, color=ACCENT_GREEN, sw=1))

    f.append(text(230, 318, "Апаратні відліки: dt_hw = 1.000 мс (джиттер < 5 нс)", size=9, bold=True, color=ACCENT_GREEN))
    f.append(text(590, 318, "Апаратні відліки: dt_hw = 1.000 мс (джиттер < 5 нс)", size=9, bold=True, color=ACCENT_GREEN))

    # Пакетне зчитування Watermark
    f.append(rect(430, 348, 140, 48, fill="#e0f2fe", stroke=ACCENT_BLUE, sw=1.5, rx=4))
    f.append(text(500, 366, "Watermark IRQ + SPI DMA", size=9, bold=True, color=ACCENT_BLUE))
    f.append(text(500, 384, "Пакет із 6 кадрів (60 мкс)", size=9, color=ACCENT_BLUE))

    f.append(rect(730, 348, 140, 48, fill="#e0f2fe", stroke=ACCENT_BLUE, sw=1.5, rx=4))
    f.append(text(800, 366, "Watermark IRQ + SPI DMA", size=9, bold=True, color=ACCENT_BLUE))
    f.append(text(800, 384, "Пакет із 6 кадрів (60 мкс)", size=9, color=ACCENT_BLUE))

    render(os.path.join(IMG, "polling-vs-fifo-jitter.svg"), W, H, *f)


# ── 3. Формати кадрів даних у FIFO різних поколінь ──────────────────────────
def fig_fifo_frame_formats():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Формати кадрів даних у буфері FIFO інерційних сенсорів", size=17, bold=True),
        text(W / 2, 48, "Порівняння структури пакетів: фіксований, заголовковий та тегований формати", size=11, color=MUTED, italic=True)
    ]

    # Формат 1: MPU-6050 (Беззаголовковий фіксований)
    f.append(rect(30, 70, 880, 115, fill=PANEL_BG, stroke=PANEL_BORDER, sw=1.5, rx=6))
    f.append(text(50, 93, "1. Фіксований беззаголовковий кадр (MPU-6050, 14 байт):", size=12, bold=True, anchor="start"))
    f.append(text(50, 110, "Будь-яка втрата байта призводить до перманентного зсуву всіх наступних осей до скидання FIFO", size=10, color=MUTED, anchor="start"))

    bx = 50
    fields_mpu = [
        ("Accel X [H:L]", 100, "#e0f2fe", ACCENT_BLUE),
        ("Accel Y [H:L]", 100, "#e0f2fe", ACCENT_BLUE),
        ("Accel Z [H:L]", 100, "#e0f2fe", ACCENT_BLUE),
        ("Temp [H:L]", 80, "#fee2e2", ACCENT_RED),
        ("Gyro X [H:L]", 100, "#fef3c7", GOLD),
        ("Gyro Y [H:L]", 100, "#fef3c7", GOLD),
        ("Gyro Z [H:L]", 100, "#fef3c7", GOLD),
    ]
    for name, w, fill_c, strk_c in fields_mpu:
        f.append(fitbox(bx, 125, w, 42, name + "\n2 байти", size=9, bold=True, fill=fill_c, stroke=strk_c))
        bx += w + 6

    # Формат 2: ICM-42688-P (Кадр із заголовком та розширенням High-Res)
    f.append(rect(30, 200, 880, 130, fill=PANEL_BG, stroke=PANEL_BORDER, sw=1.5, rx=6))
    f.append(text(50, 223, "2. Заголовковий пакет із 20-бітним розширенням (ICM-42688-P, 16 / 20 байт):", size=12, bold=True, anchor="start"))
    f.append(text(50, 240, "Байт заголовка визначає наявність сенсорів, валідність даних та дозволяє синхронізувати потік", size=10, color=MUTED, anchor="start"))

    bx = 50
    fields_icm = [
        ("Header\n1 байт", 65, "#f3e8ff", ACCENT_PURPLE),
        ("Accel X,Y,Z\n6 байтів", 150, "#e0f2fe", ACCENT_BLUE),
        ("Gyro X,Y,Z\n6 байтів", 150, "#fef3c7", GOLD),
        ("Temp\n1-2 байти", 75, "#fee2e2", ACCENT_RED),
        ("Timestamp\n2 байти", 95, "#dcfce7", ACCENT_GREEN),
        ("20-bit Ext (HiRes)\n3 байти (опція)", 135, "#f1f5f9", LINE),
    ]
    for name, w, fill_c, strk_c in fields_icm:
        f.append(fitbox(bx, 255, w, 44, name, size=9, bold=True, fill=fill_c, stroke=strk_c))
        bx += w + 6

    # Формат 3: LSM6DSO / BMI270 (Тегований потоковий формат)
    f.append(rect(30, 345, 880, 120, fill=PANEL_BG, stroke=PANEL_BORDER, sw=1.5, rx=6))
    f.append(text(50, 368, "3. Тегований потоковий кадр (LSM6DSO / BMI270, змінний розмір):", size=12, bold=True, anchor="start"))
    f.append(text(50, 385, "Кожен пакет має 1-байтний Sensor Tag, що дозволяє асинхронно змішувати події, крокомір та IMU", size=10, color=MUTED, anchor="start"))

    bx = 50
    fields_lsm = [
        ("TAG: Accel\n(1 байт)", 85, "#e0f2fe", ACCENT_BLUE),
        ("Accel [X,Y,Z]\n6 байтів", 120, "#e0f2fe", ACCENT_BLUE),
        ("TAG: Gyro\n(1 байт)", 85, "#fef3c7", GOLD),
        ("Gyro [X,Y,Z]\n6 байтів", 120, "#fef3c7", GOLD),
        ("TAG: Time\n(1 байт)", 85, "#dcfce7", ACCENT_GREEN),
        ("Timestamp\n3 байти", 95, "#dcfce7", ACCENT_GREEN),
        ("TAG: Step/Cfg\n(1 байт)", 90, "#f3e8ff", ACCENT_PURPLE),
    ]
    for name, w, fill_c, strk_c in fields_lsm:
        f.append(fitbox(bx, 400, w, 44, name, size=9, bold=True, fill=fill_c, stroke=strk_c))
        bx += w + 5

    render(os.path.join(IMG, "fifo-frame-formats.svg"), W, H, *f)


# ── 4. Часова діаграма Watermark переривання та SPI DMA ───────────────────────
def fig_dma_watermark_timeline():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Хронограма вичитування: поріг Watermark, переривання та SPI DMA Burst", size=17, bold=True),
        text(W / 2, 48, "Процесор спить або зайнятий іншими задачами під час накопичення та фонового трансферу", size=11, color=MUTED, italic=True)
    ]

    # Шкала FIFO Fill Level
    f.append(text(40, 110, "Рівень заповнення FIFO (байти)", size=11, bold=True, anchor="start"))
    f.append(line(50, 180, 880, 180, color=LINE, sw=1.5))
    f.append(line(50, 180, 50, 120, color=LINE, sw=1.5))

    # Рівень Watermark (пунктир)
    f.append(line(50, 135, 880, 135, color=ACCENT_RED, sw=1.5, dash="5 4"))
    f.append(text(890, 138, "Поріг Watermark (WM = 160 B)", size=10, bold=True, color=ACCENT_RED, anchor="start"))

    # Зубчастий графік накопичення та скидання даних
    pts1 = [(50, 180), (350, 135), (370, 180), (670, 135), (690, 180), (880, 150)]
    f.append(polyline(pts1, color=ACCENT_BLUE, sw=2))

    f.append(text(200, 160, "Накопичення кадрів (10 кадрів × 16 Б = 10 мс)", size=9, color=MUTED))
    f.append(text(520, 160, "Накопичення кадрів (10 кадрів × 16 Б = 10 мс)", size=9, color=MUTED))

    # Сигнал INT1 (Watermark IRQ)
    f.append(text(40, 220, "Пін переривання INT1", size=11, bold=True, anchor="start"))
    f.append(line(50, 250, 880, 250, color=LINE, sw=1.5))

    # Імпульс переривання 1
    f.append(polyline([(50, 250), (350, 250), (350, 225), (370, 225), (370, 250),
                       (670, 250), (670, 225), (690, 225), (690, 250), (880, 250)], color=ACCENT_RED, sw=2))
    f.append(text(360, 215, "EXTI IRQ", size=9, bold=True, color=ACCENT_RED))
    f.append(text(680, 215, "EXTI IRQ", size=9, bold=True, color=ACCENT_RED))

    # Шина SPI (DMA Burst Read)
    f.append(text(40, 290, "Транзакція SPI Bus (DMA)", size=11, bold=True, anchor="start"))
    f.append(line(50, 320, 880, 320, color=LINE, sw=1.5))

    # Пакет DMA 1
    f.append(rect(355, 305, 55, 30, fill="#e0f2fe", stroke=ACCENT_BLUE, sw=1.5, rx=3))
    f.append(text(382, 323, "DMA Read\n(64 мкс)", size=9, bold=True, color=ACCENT_BLUE))

    # Пакет DMA 2
    f.append(rect(675, 305, 55, 30, fill="#e0f2fe", stroke=ACCENT_BLUE, sw=1.5, rx=3))
    f.append(text(702, 323, "DMA Read\n(64 мкс)", size=9, bold=True, color=ACCENT_BLUE))

    # Завантаження процесора (CPU Activity)
    f.append(text(40, 370, "Активність CPU (Cortex-M)", size=11, bold=True, anchor="start"))
    f.append(rect(50, 395, 830, 45, fill="#f8fafc", stroke=PANEL_BORDER, sw=1.5, rx=4))

    # Сон / Корисні задачі
    f.append(rect(55, 400, 290, 35, fill="#dcfce7", stroke=ACCENT_GREEN, sw=1, rx=3))
    f.append(text(200, 421, "CPU вільний (Сон / WFI / інші процеси)", size=10, bold=True, color=ACCENT_GREEN))

    # Короткий старт DMA (1 мкс)
    f.append(rect(350, 400, 15, 35, fill="#fee2e2", stroke=ACCENT_RED, sw=1, rx=2))

    # Обробка пачки (Парсинг + Фільтр Калмана)
    f.append(rect(415, 400, 130, 35, fill="#fef3c7", stroke=GOLD, sw=1, rx=3))
    f.append(text(480, 421, "Парсинг 10 кадрів + EKF", size=9, bold=True, color=INK))

    # Вільний час 2
    f.append(rect(550, 400, 120, 35, fill="#dcfce7", stroke=ACCENT_GREEN, sw=1, rx=3))
    f.append(text(610, 421, "Вільний CPU", size=9, bold=True, color=ACCENT_GREEN))

    # Короткий старт DMA 2
    f.append(rect(670, 400, 15, 35, fill="#fee2e2", stroke=ACCENT_RED, sw=1, rx=2))

    # Обробка пачки 2
    f.append(rect(735, 400, 130, 35, fill="#fef3c7", stroke=GOLD, sw=1, rx=3))
    f.append(text(800, 421, "Парсинг 10 кадрів + EKF", size=9, bold=True, color=INK))

    render(os.path.join(IMG, "dma-watermark-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_imu_fifo_architecture()
    fig_polling_vs_fifo_jitter()
    fig_fifo_frame_formats()
    fig_dma_watermark_timeline()
    print("Всі 4 фігури успішно згенеровано у img/")
