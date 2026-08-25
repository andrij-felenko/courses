# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. drdy-vs-polling: Порівняння опитування та апаратного сповіщення DRDY ─────
def fig_drdy_vs_polling():
    W, H = 760, 440
    p = []

    # Верхня панель: Опитування (Polling)
    top_y = 40
    p.append(rect(20, top_y, 720, 175, fill="#fffaf9", stroke=POS, sw=1.5))
    p.append(text(35, top_y + 24, "Опитування (Polling) — завантаження шини, джиттер вибірки", size=12, color=POS, bold=True, anchor="start"))

    # Часова вісь для Polling
    p.append(line(50, top_y + 90, 710, top_y + 90, color=LINE, sw=1.5))
    p.append(text(710, top_y + 106, "t", size=11, color=MUTED, bold=True, anchor="end"))

    # Події Polling: опитування шини
    poll_times = [(100, "Читання", "Не готові"),
                  (220, "Читання", "Не готові"),
                  (340, "Читання", "Готові (OK)"),
                  (490, "Читання", "Не готові"),
                  (630, "Читання", "Готові (джиттер!)")]

    for px, label, status in poll_times:
        p.append(line(px, top_y + 60, px, top_y + 90, color=POS, sw=2))
        p.append(circle(px, top_y + 60, 4, fill=POS, stroke=POS))
        p.append(text(px, top_y + 50, label, size=10, color=POS, bold=True))
        p.append(text(px, top_y + 115, status, size=9.5, color=MUTED))

    p.append(text(380, top_y + 152, "Процесор постійно шле запити шиною → втрата енергії, змінний інтервал дискретизації", size=10.5, color=POS, italic=True))

    # Нижня панель: DRDY (Data Ready Interrupt)
    bot_y = 235
    p.append(rect(20, bot_y, 720, 185, fill="#f9fcf9", stroke=FIELD, sw=1.5))
    p.append(text(35, bot_y + 24, "Шаблон DRDY (Push / Event-Driven) — точний інтервал, 0 марних опитувань", size=12, color=FIELD, bold=True, anchor="start"))

    # Часова вісь для DRDY
    p.append(line(50, bot_y + 100, 710, bot_y + 100, color=LINE, sw=1.5))
    p.append(text(710, bot_y + 116, "t", size=11, color=MUTED, bold=True, anchor="end"))

    # Сигнал DRDY
    drdy_events = [140, 380, 620]
    for i, dx in enumerate(drdy_events):
        t_start = dx - 100
        p.append(rect(t_start, bot_y + 55, 90, 24, fill="#e8f5e9", stroke=FIELD, sw=1.2))
        p.append(text(t_start + 45, bot_y + 71, "АЦП / Фільтр", size=10, color=FIELD, bold=True))

        p.append(line(dx, bot_y + 100, dx, bot_y + 45, color=FIELD, sw=2.2))
        p.append(line(dx, bot_y + 45, dx + 25, bot_y + 45, color=FIELD, sw=2.2))
        p.append(line(dx + 25, bot_y + 45, dx + 25, bot_y + 100, color=FIELD, sw=2.2))
        p.append(text(dx + 12, bot_y + 38, "DRDY", size=10, color=FIELD, bold=True))

        p.append(rect(dx + 30, bot_y + 80, 65, 22, fill="#eaf0fd", stroke=NEG, sw=1.2))
        p.append(text(dx + 62, bot_y + 95, "SPI Read", size=9.5, color=NEG, bold=True))

        if i < len(drdy_events) - 1:
            next_dx = drdy_events[i+1]
            mid_x = (dx + next_dx) / 2
            p.append(line(dx, bot_y + 132, next_dx, bot_y + 132, color=MUTED, sw=1.2, dash="3 3"))
            p.append(circle(dx, bot_y + 132, 2.5, fill=MUTED, stroke=MUTED))
            p.append(circle(next_dx, bot_y + 132, 2.5, fill=MUTED, stroke=MUTED))
            p.append(text(mid_x, bot_y + 125, "Фіксований період T_ODR = 1 / ODR", size=10, color=INK, bold=True))

    p.append(text(380, bot_y + 165, "Давач сам повідомляє про готовність вибірки → процесор спить до переривання", size=10.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "drdy-vs-polling.svg"), W, H, *p,
           title="Опитування проти апаратного переривання DRDY")


# ── 2. drdy-electrical-modes: Push-Pull проти Open-Drain (Wired-OR) ───────────
def fig_drdy_electrical():
    W, H = 760, 330
    p = []

    # Ліва панель: Push-Pull
    p.append(rect(20, 20, 350, 290, fill="#fafbfc", stroke=LINE, sw=1.5))
    p.append(text(195, 45, "Двотактний вихід (Push-Pull)", size=12, color=INK, bold=True))
    p.append(text(195, 62, "Окрема лінія на кожен давач", size=10, color=MUTED))

    p.append(rect(40, 90, 110, 65, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(95, 115, "Давач 1", size=11, color=INK, bold=True))
    p.append(text(95, 133, "DRDY (P-P)", size=10, color=FIELD))

    p.append(rect(240, 90, 110, 150, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(295, 118, "MCU", size=12, color=FIELD, bold=True))
    p.append(text(295, 138, "EXTI0", size=10, color=INK, bold=True))
    p.append(text(295, 200, "EXTI1", size=10, color=INK, bold=True))

    p.append(line(150, 122, 240, 122, color=FIELD, sw=2))

    p.append(rect(40, 175, 110, 65, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(95, 200, "Давач 2", size=11, color=INK, bold=True))
    p.append(text(95, 218, "DRDY (P-P)", size=10, color=FIELD))

    p.append(line(150, 207, 240, 207, color=FIELD, sw=2))

    p.append(text(195, 265, "Фронти < 5 нс, немає статичного струму", size=10, color=FIELD, bold=True))
    p.append(text(195, 285, "Потрібно N ніжок GPIO для N давачів", size=9.5, color=MUTED))

    # Права панель: Open-Drain
    p.append(rect(390, 20, 350, 290, fill="#fafbfc", stroke=LINE, sw=1.5))
    p.append(text(565, 45, "Відкритий стік (Open-Drain)", size=12, color=INK, bold=True))
    p.append(text(565, 62, "Монтажне АБО (спільна лінія переривання)", size=10, color=MUTED))

    p.append(line(565, 75, 565, 95, color=POS, sw=1.8))
    p.append(text(565, 70, "+VDD (3.3V)", size=10, color=POS, bold=True))
    p.append(rect(555, 95, 20, 35, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(565, 116, "R_PU", size=9.5, color=INK, bold=True))
    p.append(line(565, 130, 565, 160, color=LINE, sw=2))

    p.append(line(490, 160, 630, 160, color=NEG, sw=2.2))
    p.append(text(565, 150, "Спільна лінія INT / nDRDY", size=9.5, color=NEG, bold=True))

    p.append(rect(410, 185, 95, 55, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(457, 207, "Давач 1", size=10.5, color=INK, bold=True))
    p.append(text(457, 224, "nINT (OD)", size=9.5, color=NEG))
    p.append(line(457, 185, 457, 160, color=NEG, sw=1.8))

    p.append(rect(520, 185, 95, 55, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(567, 207, "Давач 2", size=10.5, color=INK, bold=True))
    p.append(text(567, 224, "nINT (OD)", size=9.5, color=NEG))
    p.append(line(567, 185, 567, 160, color=NEG, sw=1.8))

    p.append(rect(630, 135, 95, 60, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(677, 160, "MCU", size=11, color=FIELD, bold=True))
    p.append(text(677, 178, "EXTI (1 pin)", size=9.5, color=INK, bold=True))
    p.append(line(615, 160, 630, 160, color=NEG, sw=2))

    p.append(text(565, 265, "1 ніжка на всі давачі, активний нуль (nINT)", size=10, color=NEG, bold=True))
    p.append(text(565, 285, "t_r = 2.2 · R_PU · C_bus (повільніший спад/підйом)", size=9.5, color=MUTED))

    render(os.path.join(OUT, "drdy-electrical-modes.svg"), W, H, *p,
           title="Електричні конфігурації виводу DRDY: Push-Pull та Open-Drain")


# ── 3. drdy-timing-diagram: Часові параметри, ODR та скидання переривання ─────
def fig_drdy_timing():
    W, H = 760, 360
    p = []

    p.append(rect(15, 15, 730, 330, fill="#ffffff", stroke=LINE, sw=1.2))

    y1 = 60
    p.append(text(30, y1 + 14, "Внутрішній АЦП", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(line(170, y1 + 10, 710, y1 + 10, color=MUTED, sw=1.2))
    p.append(rect(200, y1 - 8, 140, 26, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    p.append(text(270, y1 + 9, "Перетворення вибірки N", size=9.5, color=FIELD, bold=True))

    p.append(rect(480, y1 - 8, 140, 26, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    p.append(text(550, y1 + 9, "Перетворення вибірки N+1", size=9.5, color=FIELD, bold=True))

    y2 = 130
    p.append(text(30, y2 + 14, "DRDY (Pulsed)", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(line(170, y2 + 20, 340, y2 + 20, color=FIELD, sw=2))
    p.append(line(340, y2 + 20, 340, y2 - 10, color=FIELD, sw=2))
    p.append(line(340, y2 - 10, 380, y2 - 10, color=FIELD, sw=2))
    p.append(line(380, y2 - 10, 380, y2 + 20, color=FIELD, sw=2))
    p.append(line(380, y2 + 20, 620, y2 + 20, color=FIELD, sw=2))
    p.append(line(620, y2 + 20, 620, y2 - 10, color=FIELD, sw=2))
    p.append(line(620, y2 - 10, 660, y2 - 10, color=FIELD, sw=2))
    p.append(line(660, y2 - 10, 660, y2 + 20, color=FIELD, sw=2))
    p.append(line(660, y2 + 20, 710, y2 + 20, color=FIELD, sw=2))

    p.append(text(360, y2 - 18, "t_pulse", size=9.5, color=FIELD, bold=True))

    y3 = 200
    p.append(text(30, y3 + 14, "DRDY (Latched)", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(line(170, y3 + 20, 340, y3 + 20, color=POS, sw=2))
    p.append(line(340, y3 + 20, 340, y3 - 10, color=POS, sw=2))
    p.append(line(340, y3 - 10, 440, y3 - 10, color=POS, sw=2))
    p.append(line(440, y3 - 10, 440, y3 + 20, color=POS, sw=2))
    p.append(line(440, y3 + 20, 620, y3 + 20, color=POS, sw=2))
    p.append(line(620, y3 + 20, 620, y3 - 10, color=POS, sw=2))
    p.append(line(620, y3 - 10, 710, y3 - 10, color=POS, sw=2))

    p.append(text(390, y3 - 18, "Скидання при зчитуванні (Clear on Read)", size=9.5, color=POS))

    y4 = 270
    p.append(text(30, y4 + 14, "Шина SPI / I2C", size=10.5, color=NEG, bold=True, anchor="start"))
    p.append(line(170, y4 + 20, 360, y4 + 20, color=MUTED, sw=1.2))
    p.append(rect(360, y4 + 2, 85, 26, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(402, y4 + 18, "Burst Read", size=9.5, color=NEG, bold=True))
    p.append(line(445, y4 + 20, 710, y4 + 20, color=MUTED, sw=1.2))

    p.append(line(340, 20, 340, 310, color=MUTED, sw=1, dash="2 2"))
    p.append(line(620, 20, 620, 310, color=MUTED, sw=1, dash="2 2"))
    p.append(line(340, 315, 620, 315, color=INK, sw=1.5))
    p.append(circle(340, 315, 3, fill=INK, stroke=INK))
    p.append(circle(620, 315, 3, fill=INK, stroke=INK))
    p.append(text(480, 332, "Період вибірки T_ODR = 1 / ODR (наприклад 1 мс для 1000 Гц)", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "drdy-timing-diagram.svg"), W, H, *p,
           title="Часова діаграма DRDY: Pulsed та Latched режими зчитування")


# ── 4. exti-dma-chain: Апаратне зчеплення EXTI та DMA без участі процесора ────
def fig_exti_dma():
    W, H = 760, 310
    p = []

    p.append(rect(15, 15, 730, 280, fill="#ffffff", stroke=LINE, sw=1.2))

    b1_x, b1_y = 35, 90
    p.append(rect(b1_x, b1_y, 115, 120, fill="#f4f6f8", stroke=LINE, sw=1.8))
    p.append(text(b1_x + 57, b1_y + 30, "Давач", size=12, color=INK, bold=True))
    p.append(text(b1_x + 57, b1_y + 50, "(IMU / АЦП)", size=9.5, color=MUTED))
    p.append(rect(b1_x + 10, b1_y + 75, 95, 30, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    p.append(text(b1_x + 57, b1_y + 94, "DRDY Pin", size=10, color=FIELD, bold=True))

    p.append(line(b1_x + 115, b1_y + 90, 190, b1_y + 90, color=FIELD, sw=2.2))
    p.append(text(160, b1_y + 80, "DRDY", size=9.5, color=FIELD, bold=True))

    b2_x, b2_y = 190, 60
    p.append(rect(b2_x, b2_y, 130, 170, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(b2_x + 65, b2_y + 25, "MCU EXTI /", size=11, color=FIELD, bold=True))
    p.append(text(b2_x + 65, b2_y + 42, "Timer Trigger", size=11, color=FIELD, bold=True))
    p.append(text(b2_x + 65, b2_y + 75, "Детектор фронту", size=9.5, color=INK))
    p.append(text(b2_x + 65, b2_y + 95, "Апаратний тригер", size=9.5, color=INK))
    p.append(rect(b2_x + 10, b2_y + 120, 110, 32, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(text(b2_x + 65, b2_y + 140, "DMA Request", size=9.5, color=FIELD, bold=True))

    p.append(line(b2_x + 130, b2_y + 135, 360, b2_y + 135, color=FIELD, sw=2.2))

    b3_x, b3_y = 360, 60
    p.append(rect(b3_x, b3_y, 140, 170, fill="#eaf0fd", stroke=NEG, sw=1.8))
    p.append(text(b3_x + 70, b3_y + 25, "Контролер DMA", size=11, color=NEG, bold=True))
    p.append(text(b3_x + 70, b3_y + 42, "(Direct Memory)", size=9.5, color=MUTED))
    p.append(text(b3_x + 70, b3_y + 75, "Авто-генерація CS/SCK", size=9.5, color=INK))
    p.append(text(b3_x + 70, b3_y + 95, "Зчитування без CPU", size=9.5, color=INK))
    p.append(rect(b3_x + 10, b3_y + 120, 120, 32, fill="#ffffff", stroke=NEG, sw=1.2))
    p.append(text(b3_x + 70, b3_y + 140, "Запис у пам'ять", size=9.5, color=NEG, bold=True))

    p.append(line(360, b3_y + 40, b1_x + 115, b3_y + 40, color=NEG, sw=1.8, dash="4 4"))
    p.append(text(250, b3_y + 30, "Апаратне читання SPI (CS, SCK, MISO)", size=9.5, color=NEG, bold=True))

    p.append(line(b3_x + 140, b3_y + 135, 540, b3_y + 135, color=NEG, sw=2.2))

    b4_x, b4_y = 540, 60
    p.append(rect(b4_x, b4_y, 185, 170, fill="#fef9e7", stroke="#d4ac0d", sw=1.8))
    p.append(text(b4_x + 92, b4_y + 25, "ОЗП (RAM)", size=11, color=INK, bold=True))
    p.append(text(b4_x + 92, b4_y + 42, "Подвійний буфер (Ping-Pong)", size=9.5, color=MUTED))

    p.append(rect(b4_x + 15, b4_y + 65, 155, 36, fill="#ffffff", stroke="#d4ac0d", sw=1.2))
    p.append(text(b4_x + 92, b4_y + 87, "Буфер A (Заповнюється)", size=9.5, color=FIELD, bold=True))

    p.append(rect(b4_x + 15, b4_y + 115, 155, 36, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(b4_x + 92, b4_y + 137, "Буфер B (Обробляється DSP)", size=9.5, color=MUTED))

    p.append(text(380, 265, "Повний конвеєр збору даних виконується апаратно із нульовим джиттером", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "exti-dma-chain.svg"), W, H, *p,
           title="Апаратний ланцюжок синхронізації EXTI → DMA → Подвійний буфер")


# ── 5. deadlock-latched-state: Пастка зависання у режимі фіксації (Latch) ──────
def fig_deadlock():
    W, H = 760, 310
    p = []

    p.append(rect(15, 15, 730, 280, fill="#ffffff", stroke=LINE, sw=1.2))

    p.append(rect(30, 35, 335, 240, fill="#fffaf9", stroke=POS, sw=1.5))
    p.append(text(197, 60, "Пастка зависання (Latched Hang Trap)", size=11.5, color=POS, bold=True))

    p.append(text(45, 90, "1. Давач виставив nINT = 0 (Data Ready)", size=9.5, color=INK, anchor="start"))
    p.append(text(45, 115, "2. MCU раптово перезавантажився (Watchdog)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(45, 140, "3. MCU стартує і вмикає EXTI (Falling Edge)", size=9.5, color=INK, anchor="start"))
    p.append(text(45, 165, "4. На лінії nINT ВЖЕ статичний 0 (немає перепаду!)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(45, 190, "5. Детектор фронту мовчить → система зависла", size=9.5, color=POS, anchor="start"))

    p.append(rect(50, 215, 295, 45, fill="#fdecea", stroke=POS, sw=1.2))
    p.append(text(197, 235, "DEADLOCK: Переривання ніколи не прийде,", size=9.5, color=POS, bold=True))
    p.append(text(197, 250, "бо давач чекає вичитування старих даних", size=9.5, color=POS))

    p.append(rect(395, 35, 335, 240, fill="#f9fcf9", stroke=FIELD, sw=1.5))
    p.append(text(562, 60, "Алгоритм відновлення (Dummy Flush)", size=11.5, color=FIELD, bold=True))

    p.append(text(410, 90, "1. Ініціалізація шини SPI / I2C", size=9.5, color=INK, anchor="start"))
    p.append(text(410, 115, "2. Холосте читання (Dummy Read):", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(425, 135, "• Зчитування STATUS_REG / INT_STATUS", size=9.5, color=MUTED, anchor="start"))
    p.append(text(425, 155, "• Зчитування вихідних регістрів (OUT_X..Z)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(410, 180, "3. Фіксатор скинуто → nINT повертається в 1", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(410, 205, "4. Тільки тепер вмикаємо EXTI в MCU", size=9.5, color=INK, anchor="start"))

    p.append(rect(415, 215, 295, 45, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    p.append(text(562, 235, "ГАРАНТОВАНИЙ СТАРТ: Наступна вибірка", size=9.5, color=FIELD, bold=True))
    p.append(text(562, 250, "створить чистий фронт 1 → 0 для EXTI", size=9.5, color=FIELD))

    render(os.path.join(OUT, "deadlock-latched-state.svg"), W, H, *p,
           title="Пастка мертвого зависання у режимі фіксації Latch та її усунення")


def main():
    fig_drdy_vs_polling()
    fig_drdy_electrical()
    fig_drdy_timing()
    fig_exti_dma()
    fig_deadlock()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()

