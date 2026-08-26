# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. spi-vs-i2c-silicon-blocks.svg ─────────────────────────────────────────
# Порівняння кремнієвої архітектури: простий зсувний регістр SPI проти
# складного шинного автомата I2C з компаратором адрес та контролем SCL.

def fig_silicon_blocks():
    W, H = 720, 340
    p = []

    # Заголовки двох світів
    p.append(text(180, 25, "SPI: Зсувний конвеєр (Shift Pipeline)", size=12, color=INK, bold=True))
    p.append(text(540, 25, "I2C: Шинний автомат (Bus State Machine)", size=12, color=INK, bold=True))

    # Розділювач
    p.append(line(360, 15, 360, 325, color=MUTED, sw=1.0, dash="4 4"))

    # --- SPI БЛОК (ліворуч) ---
    # Зовнішній контейнер
    p.append(rect(20, 45, 320, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Буфер даних TX/RX
    b_dr, _, _ = textbox(110, 85, "Регістр даних (DR / FIFO)\nБуфери TXDR та RXDR", size=10, pad=8, fill="#eff6ff", stroke="#3b82f6", sw=1.2)
    p.append(b_dr)

    # Прапорці стану
    b_sr, _, _ = textbox(260, 85, "Прапорці SR\nTXE, RXNE, BSY", size=10, pad=8, fill="#fef2f2", stroke=POS, sw=1.2)
    p.append(b_sr)

    # Зсувний регістр
    b_shift, _, _ = textbox(180, 165, "Кільцевий зсувний регістр (8 / 16 біт)\nСинхронний зсув такт-у-такт", size=10, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    p.append(b_shift)

    # Подільник частоти SCK
    b_br, _, _ = textbox(180, 245, "Генератор такту (Baud Rate Prescaler)\nДільники f_PCLK / (2..256)", size=10, pad=8, fill="#faf5ff", stroke="#8b5cf6", sw=1.2)
    p.append(b_br)

    # Зв'язки ліворуч
    p.append(arrow(110, 110, 140, 142, color=INK, sw=1.5))
    p.append(arrow(220, 142, 250, 110, color=INK, sw=1.5))
    p.append(arrow(180, 222, 180, 192, color="#8b5cf6", sw=1.5))

    # Виводи назовні SPI
    p.append(line(275, 155, 330, 155, color=INK, sw=1.5))
    p.append(text(310, 147, "MOSI", size=9.5, color=INK, bold=True))
    p.append(arrow(320, 155, 338, 155, color=INK, sw=1.5))

    p.append(line(275, 175, 330, 175, color=INK, sw=1.5))
    p.append(text(310, 169, "MISO", size=9.5, color=INK, bold=True))
    p.append(arrow(338, 175, 278, 175, color=INK, sw=1.5))

    p.append(line(265, 245, 330, 245, color="#8b5cf6", sw=1.5))
    p.append(text(310, 237, "SCK", size=9.5, color="#8b5cf6", bold=True))
    p.append(arrow(320, 245, 338, 245, color="#8b5cf6", sw=1.5))

    p.append(text(180, 305, "Пряма передача бітів без аналізу протоколу", size=9.5, color=MUTED, italic=True))

    # --- I2C БЛОК (праворуч) ---
    # Зовнішній контейнер
    p.append(rect(380, 45, 320, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Кінцевий автомат шини (FSM)
    b_fsm, _, _ = textbox(540, 85, "Кінцевий автомат протоколу (FSM)\nSTART, STOP, ACK, NACK, арбітраж", size=10, pad=8, fill="#fffbeb", stroke="#f59e0b", sw=1.5, bold=True)
    p.append(b_fsm)

    # Компаратор адреси + Регістр даних
    b_addr, _, _ = textbox(460, 165, "Компаратор адреси\n(7 / 10 біт, OAR1/2)\n+ Буфер даних DR", size=9.5, pad=8, fill="#eff6ff", stroke="#3b82f6", sw=1.2)
    p.append(b_addr)

    # Контроль такту SCL та Clock Stretching
    b_scl_ctrl, _, _ = textbox(620, 165, "Контроль лінії SCL\nГенератор такту +\nДетектор розтягування", size=9.5, pad=8, fill="#fdf4ff", stroke="#d946ef", sw=1.2)
    p.append(b_scl_ctrl)

    # Фільтри та Open-Drain каскад
    b_flt, _, _ = textbox(540, 245, "Аналоговий/цифровий фільтр шуму\n+ Open-Drain ключі ліній SDA/SCL", size=9.5, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.2)
    p.append(b_flt)

    # Зв'язки праворуч
    p.append(arrow(540, 115, 480, 142, color=INK, sw=1.5))
    p.append(arrow(540, 115, 600, 142, color=INK, sw=1.5))
    p.append(arrow(480, 195, 520, 222, color=INK, sw=1.5))
    p.append(arrow(600, 195, 560, 222, color=INK, sw=1.5))

    # Виводи назовні I2C
    p.append(line(645, 235, 690, 235, color=INK, sw=1.5))
    p.append(text(675, 227, "SDA", size=9.5, color=INK, bold=True))
    p.append(arrow(675, 235, 695, 235, color=INK, sw=1.5))

    p.append(line(645, 255, 690, 255, color="#d946ef", sw=1.5))
    p.append(text(675, 247, "SCL", size=9.5, color="#d946ef", bold=True))
    p.append(arrow(675, 255, 695, 255, color="#d946ef", sw=1.5))

    p.append(text(540, 305, "Постійний апаратний аналіз ліній і стану мережі", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "spi-vs-i2c-silicon-blocks.svg"), W, H, *p,
           title="Порівняння кремнієвої архітектури SPI та I2C")


# ── 2. spi-modes-timing.svg ──────────────────────────────────────────────────
# Часова діаграма 4 режимів SPI (CPOL = 0/1, CPHA = 0/1) з точками вибірки.

def fig_spi_modes():
    W, H = 720, 360
    p = []

    p.append(text(360, 20, "Чотири режими тактування SPI (Полярність CPOL та Фаза CPHA)", size=12, color=INK, bold=True))

    modes = [
        ("Mode 0: CPOL=0, CPHA=0 (Спокій = LOW, вибірка по 1-му наростаючому фронту)", 0, 0, 40),
        ("Mode 1: CPOL=0, CPHA=1 (Спокій = LOW, вибірка по 2-му спадному фронту)", 0, 1, 115),
        ("Mode 2: CPOL=1, CPHA=0 (Спокій = HIGH, вибірка по 1-му спадному фронту)", 1, 0, 190),
        ("Mode 3: CPOL=1, CPHA=1 (Спокій = HIGH, вибірка по 2-му наростаючому фронту)", 1, 1, 265)
    ]

    for title, cpol, cpha, ybase in modes:
        # Фон блоку режиму
        p.append(rect(15, ybase, 690, 68, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
        p.append(text(30, ybase + 15, title, size=10, color=INK, anchor="start", bold=True))

        # Сигнал SCK
        sck_y = ybase + 42
        sck_x = 220
        step = 28

        p.append(text(180, sck_y + 4, "SCK", size=9.5, color="#8b5cf6", bold=True))
        p.append(text(180, sck_y + 18, "MOSI", size=9.5, color=FIELD, bold=True))

        # Малюємо тактові імпульси
        # Рівні: для CPOL=0 низький рівень y=sck_y+6, високий y=sck_y-6
        # для CPOL=1 навпаки
        low_y = sck_y + 6
        high_y = sck_y - 6

        base_lvl = low_y if cpol == 0 else high_y
        act_lvl = high_y if cpol == 0 else low_y

        pts = [(sck_x, base_lvl), (sck_x + 15, base_lvl)]
        curr_x = sck_x + 15

        for i in range(4):
            pts.append((curr_x, act_lvl))
            curr_x += step
            pts.append((curr_x, act_lvl))
            pts.append((curr_x, base_lvl))
            curr_x += step
            pts.append((curr_x, base_lvl))

        pts.append((curr_x + 15, base_lvl))

        # Будуємо polyline для SCK
        poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        p.append(f'<polyline points="{poly_str}" fill="none" stroke="#8b5cf6" stroke-width="1.6"/>')

        # Малюємо точки захоплення даних (Sample points)
        sample_x_list = []
        if cpha == 0:
            # Вибірка по першому фронту
            for i in range(4):
                sample_x_list.append(sck_x + 15 + i * (2 * step))
        else:
            # Вибірка по другому фронту
            for i in range(4):
                sample_x_list.append(sck_x + 15 + step + i * (2 * step))

        for sx in sample_x_list:
            p.append(circle(sx, sck_y, 3.5, fill=POS, stroke=POS, sw=1.0))
            p.append(line(sx, sck_y - 12, sx, sck_y + 22, color=POS, sw=1.0, dash="2 2"))

        # Малюємо шину даних MOSI під SCK
        data_y = sck_y + 18
        p.append(line(sck_x, data_y, curr_x + 15, data_y, color=FIELD, sw=1.4))

    p.append(circle(540, 345, 3.5, fill=POS, stroke=POS, sw=1.0))
    p.append(text(550, 348, "Точка фіксації біта (Sample Edge)", size=9.5, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "spi-modes-timing.svg"), W, H, *p,
           title="Часові діаграми режимів SPI")


# ── 3. i2c-event-flow.svg ────────────────────────────────────────────────────
# Послідовність подій апаратного автомата I2C (EV5, EV6, EV8, EV7, STOP)

def fig_i2c_events():
    W, H = 720, 320
    p = []

    p.append(text(360, 22, "Подійна модель апаратного ведучого I2C (Master Transmitter Flow)", size=12, color=INK, bold=True))

    # Сходинки подій
    steps = [
        (80, 80, "1. СТАРТ", "CR1: START=1\nЛінії захоплено", "Подія EV5\nSR1: SB=1\n(Старт згенеровано)", "#eff6ff", "#3b82f6"),
        (220, 80, "2. АДРЕСА", "Запис адреси у DR\n(7 біт + R/W=0)", "Подія EV6\nSR1: ADDR=1\n(Отримано ACK адреси)", "#fffbeb", "#f59e0b"),
        (360, 80, "3. БАЙТ 1", "Запис даних у DR\nЗсув байта по SDA", "Подія EV8\nSR1: TXE=1\n(Буфер DR вільний)", "#f0fdf4", FIELD),
        (500, 80, "4. БАЙТ 2 (фінал)", "Останній байт у DR\nОчікування ACK", "Подія EV8_2\nSR1: BTF=1, TXE=1\n(Передачу завершено)", "#faf5ff", "#8b5cf6"),
        (640, 80, "5. СТОП", "CR1: STOP=1\nФормування STOP", "Шина вільна\nSR2: BUSY=0\n(Готовий до обміну)", "#fef2f2", POS)
    ]

    for cx, cy, title, action, ev_text, fill_c, strk_c in steps:
        # Верхній блок (Дія ПЗ)
        b_act, _, _ = textbox(cx, cy + 30, f"{title}\n{action}", size=9.5, pad=6, fill=fill_c, stroke=strk_c, sw=1.3, bold=True)
        p.append(b_act)

        # Стрілка вниз
        p.append(arrow(cx, cy + 62, cx, cy + 90, color=INK, sw=1.3))

        # Нижній блок (Апаратна подія)
        b_ev, _, _ = textbox(cx, cy + 130, ev_text, size=9.5, pad=6, fill="#ffffff", stroke=strk_c, sw=1.2)
        p.append(b_ev)

        # Стрілка праворуч до наступного кроку (якщо не останній)
        if cx < 600:
            p.append(arrow(cx + 52, cy + 130, cx + 88, cy + 130, color=MUTED, sw=1.4))

    # Пояснення внизу
    p.append(rect(40, 245, 640, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=6))
    p.append(text(360, 265, "Дисципліна обробки: запис у DR очищує TXE, читання SR1+SR2 очищує ADDR,", size=9.5, color=INK, bold=True))
    p.append(text(360, 282, "а затримка запису активує BTF (Byte Transfer Finished) і розтягує SCL для захисту від Underrun.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "i2c-event-flow.svg"), W, H, *p,
           title="Подійна модель автомата I2C")


# ── 4. i2c-bus-hang-recovery.svg ─────────────────────────────────────────────
# Механізм мертвого зависання I2C та процедура 9 тактів розблокування через GPIO.

def fig_bus_recovery():
    W, H = 720, 320
    p = []

    p.append(text(360, 20, "Апаратне розблокування шини I2C (I2C Bus Recovery Pattern)", size=12, color=INK, bold=True))

    # Сценарій 1: Зависання
    p.append(rect(15, 45, 335, 255, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(182, 65, "Проблема: Ресет МК під час читання", size=10.5, color=POS, bold=True))

    tb_prob, _, _ = textbox(182, 125, "1. Ведений передавав біт '0' і притягнув SDA до GND.\n2. У ведучого стався Watchdog / Brown-out ресет.\n3. Після рестарту МК бачить SDA = 0.\n4. Апаратний блок виставляє BUSY = 1 і блокує START.", size=9.5, pad=8, fill="#ffffff", stroke="#f87171", sw=1.0)
    p.append(tb_prob)

    # Часова діаграма глухого кута
    p.append(text(50, 195, "SCL", size=9.5, color=MUTED, bold=True))
    p.append(line(80, 195, 320, 195, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(200, 185, "SCL висить у '1' (МК мовчить)", size=9.5, color=MUTED))

    p.append(text(50, 225, "SDA", size=9.5, color=POS, bold=True))
    p.append(line(80, 225, 320, 225, color=POS, sw=2.0))
    p.append(text(200, 240, "Ведений тримає SDA = 0 і чекає такту", size=9.5, color=POS, bold=True))

    p.append(text(182, 285, "Клінч: обидва чекають один одного", size=9.5, color=POS, bold=True))

    # Сценарій 2: Лікування через 9 тактів GPIO
    p.append(rect(370, 45, 335, 255, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(537, 65, "Розв'язок: 9 тактів SCL через GPIO", size=10.5, color=FIELD, bold=True))

    tb_sol, _, _ = textbox(537, 125, "1. Вимкнути I2C, перемкнути SCL у GPIO Open-Drain.\n2. Згенерувати до 9 ручних імпульсів такту на SCL.\n3. Ведений докручує свій зсувний регістр і відпускає SDA.\n4. Згенерувати явну умову STOP через GPIO.", size=9.5, pad=8, fill="#ffffff", stroke="#4ade80", sw=1.0)
    p.append(tb_sol)

    # Часова діаграма лікування
    p.append(text(400, 195, "SCL", size=9.5, color=FIELD, bold=True))
    # Малюємо 5 імпульсів такту
    scl_pts = [(430, 200)]
    cx = 430
    for i in range(5):
        scl_pts.append((cx + 5, 200))
        scl_pts.append((cx + 5, 185))
        scl_pts.append((cx + 15, 185))
        scl_pts.append((cx + 15, 200))
        cx += 20
    scl_pts.append((cx + 15, 200))
    scl_pts.append((cx + 25, 185))
    scl_pts.append((680, 185))
    poly_scl = " ".join(f"{x:.1f},{y:.1f}" for x, y in scl_pts)
    p.append(f'<polyline points="{poly_scl}" fill="none" stroke="{FIELD}" stroke-width="1.5"/>')

    p.append(text(400, 230, "SDA", size=9.5, color=FIELD, bold=True))
    p.append(line(430, 235, 510, 235, color=POS, sw=2.0))
    p.append(line(510, 235, 520, 220, color=FIELD, sw=1.5))
    p.append(line(520, 220, 640, 220, color=FIELD, sw=1.5))
    # STOP умова: SDA опускається і піднімається при високому SCL
    p.append(line(640, 220, 645, 235, color="#3b82f6", sw=1.5))
    p.append(line(645, 235, 660, 235, color="#3b82f6", sw=1.5))
    p.append(line(660, 235, 670, 220, color="#3b82f6", sw=1.5))
    p.append(line(670, 220, 685, 220, color=FIELD, sw=1.5))

    p.append(text(580, 248, "SDA відпущено в '1'", size=9.5, color=FIELD, bold=True))
    p.append(text(665, 205, "STOP", size=9.5, color="#3b82f6", bold=True))

    p.append(text(537, 285, "Шина розблокована, I2C реініціалізується", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "i2c-bus-hang-recovery.svg"), W, H, *p,
           title="Відновлення завислої шини I2C")


if __name__ == "__main__":
    fig_silicon_blocks()
    fig_spi_modes()
    fig_i2c_events()
    fig_bus_recovery()
    print("All figures generated successfully.")
