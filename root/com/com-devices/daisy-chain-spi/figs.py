# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CSCOL = "#b07d00"   # колір ліній CS / Latch
MOSICOL = "#c0392b" # червоний — лінія даних MOSI / SDI
MISOCOL = "#27ae60" # зелений — лінія даних MISO / SDO
SCKCOL  = "#2457d6" # синій — лінія тактування SCLK

# ── 1. topology.svg: Порівняння Star SPI та Daisy-Chain SPI ───────────────────
def fig_topology():
    W, H = 840, 480
    p = []

    # Тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1))

    # Ліва панель — Зіркова топологія (Star SPI)
    p.append(rect(20, 20, 390, 440, fill="#fbfcfd", stroke="#d0d7de", sw=1.2))
    p.append(text(215, 48, "Зіркова топологія (Star SPI)", size=14, color=INK, bold=True))
    p.append(text(215, 68, "3 спільні лінії + N окремих ліній CS", size=11, color=MUTED, italic=True))

    # Ведучий (ліворуч у зірці)
    p.append(rect(35, 110, 95, 290, fill="#eef4fb", stroke=NEG, sw=1.5))
    p.append(text(82, 140, "ВЕДУЧИЙ", size=12, color=NEG, bold=True))
    p.append(text(82, 156, "(Master)", size=10, color=MUTED, italic=True))

    p.append(text(120, 195, "MOSI", size=10, color=MOSICOL, bold=True, anchor="end"))
    p.append(text(120, 235, "MISO", size=10, color=MISOCOL, bold=True, anchor="end"))
    p.append(text(120, 275, "SCLK", size=10, color=SCKCOL, bold=True, anchor="end"))
    p.append(text(120, 320, "CS1", size=10, color=CSCOL, bold=True, anchor="end"))
    p.append(text(120, 350, "CS2", size=10, color=CSCOL, bold=True, anchor="end"))
    p.append(text(120, 380, "CS3", size=10, color=CSCOL, bold=True, anchor="end"))

    # Спільні шини (горизонтальні)
    p.append(line(130, 190, 390, 190, color=MOSICOL, sw=1.6))
    p.append(line(130, 230, 390, 230, color=MISOCOL, sw=1.6))
    p.append(line(130, 270, 390, 270, color=SCKCOL, sw=1.6))

    # Ведені мікросхеми 1, 2, 3 у зірці
    dev_xs = [170, 250, 330]
    for i, dx in enumerate(dev_xs):
        p.append(rect(dx, 100, 65, 300, fill="#f4f6f8", stroke=INK, sw=1.2))
        p.append(text(dx + 32, 122, f"IC {i+1}", size=11, color=INK, bold=True))

        # Входи шин
        p.append(line(dx + 32, 190, dx + 32, 160, color=MOSICOL, sw=1.2))
        p.append(circle(dx + 32, 190, 2.5, fill=MOSICOL, stroke=MOSICOL))

        p.append(line(dx + 48, 230, dx + 48, 160, color=MISOCOL, sw=1.2))
        p.append(circle(dx + 48, 230, 2.5, fill=MISOCOL, stroke=MISOCOL))

        p.append(line(dx + 16, 270, dx + 16, 160, color=SCKCOL, sw=1.2))
        p.append(circle(dx + 16, 270, 2.5, fill=SCKCOL, stroke=SCKCOL))

        # Окремі CS
        cs_y = 315 + i * 30
        p.append(line(130, cs_y, dx + 32, cs_y, color=CSCOL, sw=1.4))
        p.append(line(dx + 32, cs_y, dx + 32, 360, color=CSCOL, sw=1.4))
        p.append(text(dx + 32, 375, f"CS", size=9.5, color=CSCOL, bold=True))

    p.append(text(215, 435, "Потрібно 3 + N виводів мікроконтролера", size=11, color=POS, bold=True))

    # Права панель — Каскадна топологія (Daisy-Chain SPI)
    p.append(rect(430, 20, 390, 440, fill="#fbfcfd", stroke="#d0d7de", sw=1.2))
    p.append(text(625, 48, "Каскадна топологія (Daisy-Chain SPI)", size=14, color=INK, bold=True))
    p.append(text(625, 68, "Рівно 4 лінії незалежно від кількості N мікросхем", size=11, color=FIELD, bold=True))

    # Ведучий (ліворуч у каскаді)
    p.append(rect(445, 110, 85, 290, fill="#eef4fb", stroke=NEG, sw=1.5))
    p.append(text(487, 140, "ВЕДУЧИЙ", size=12, color=NEG, bold=True))
    p.append(text(487, 156, "(Master)", size=10, color=MUTED, italic=True))

    p.append(text(522, 195, "MOSI", size=10, color=MOSICOL, bold=True, anchor="end"))
    p.append(text(522, 245, "MISO", size=10, color=MISOCOL, bold=True, anchor="end"))
    p.append(text(522, 305, "SCLK", size=10, color=SCKCOL, bold=True, anchor="end"))
    p.append(text(522, 360, "CS", size=10, color=CSCOL, bold=True, anchor="end"))

    # Ведені мікросхеми 1, 2, 3 у каскаді
    dc_xs = [560, 650, 740]
    for i, dx in enumerate(dc_xs):
        p.append(rect(dx, 110, 70, 160, fill="#f4f6f8", stroke=INK, sw=1.2))
        p.append(text(dx + 35, 132, f"IC {i+1}", size=11, color=INK, bold=True))
        p.append(text(dx + 15, 195, "SDI", size=9, color=MOSICOL, bold=True, anchor="start"))
        p.append(text(dx + 55, 195, "SDO", size=9, color=MISOCOL, bold=True, anchor="end"))
        p.append(text(dx + 35, 225, "Зсувний", size=9, color=MUTED))
        p.append(text(dx + 35, 238, "регістр", size=9, color=MUTED))

    # З'єднання даних Daisy-Chain: MOSI -> IC1.SDI, IC1.SDO -> IC2.SDI, IC2.SDO -> IC3.SDI, IC3.SDO -> MISO
    p.append(arrow(530, 190, 560, 190, color=MOSICOL, sw=1.6))
    p.append(arrow(630, 190, 650, 190, color=MOSICOL, sw=1.6))
    p.append(arrow(720, 190, 740, 190, color=MOSICOL, sw=1.6))

    # Зворотний зв'язок SDO останньої мікросхеми -> MISO ведучого
    p.append(line(810, 190, 815, 190, color=MISOCOL, sw=1.6))
    p.append(line(815, 190, 815, 240, color=MISOCOL, sw=1.6))
    p.append(line(815, 240, 530, 240, color=MISOCOL, sw=1.6))
    p.append(arrow(540, 240, 530, 240, color=MISOCOL, sw=1.6))

    # Спільна лінія SCLK
    p.append(line(530, 300, 775, 300, color=SCKCOL, sw=1.6))
    for dx in dc_xs:
        p.append(line(dx + 25, 300, dx + 25, 270, color=SCKCOL, sw=1.2))
        p.append(circle(dx + 25, 300, 2.5, fill=SCKCOL, stroke=SCKCOL))
        p.append(text(dx + 25, 265, "CLK", size=9.5, color=SCKCOL, bold=True))

    # Спільна лінія CS / Latch
    p.append(line(530, 355, 775, 355, color=CSCOL, sw=1.6))
    for dx in dc_xs:
        p.append(line(dx + 48, 355, dx + 48, 270, color=CSCOL, sw=1.2))
        p.append(circle(dx + 48, 355, 2.5, fill=CSCOL, stroke=CSCOL))
        p.append(text(dx + 48, 265, "CS", size=9.5, color=CSCOL, bold=True))

    p.append(text(625, 435, "Завжди 4 виводи GPIO на будь-яку довжину ланцюга", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "topology.svg"), W, H, *p,
           title="Порівняння зіркової топології SPI та послідовного каскаду Daisy-Chain")


# ── 2. shift-frame.svg: Покроковий зсув кадру крізь каскад ─────────────────────
def fig_shift_frame():
    W, H = 820, 460
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1))
    p.append(text(W / 2, 38, "Механізм просування даних у 3-ланковому каскаді (N=3)", size=15, color=INK, bold=True))
    p.append(text(W / 2, 58, "Порядок надсилання байтів ведучим: [ Байт для IC3 ] → [ Байт для IC2 ] → [ Байт для IC1 ]", size=11.5, color=MUTED, italic=True))

    # 4 часові фази (Крок 0, Крок 1, Крок 2, Крок 3 + Latch)
    steps = [
        ("Фаза 1: Початок транзакції (CS переходить у 0)", "Ведучий надсилає Байт 3. Байт потрапляє у зсувний регістр IC1.", [("Байт 3", POS), ("порожньо", MUTED), ("порожньо", MUTED)]),
        ("Фаза 2: Зсув другого байта (після 16 тактів)", "Байт 3 витісняється через SDO1 в IC2; Байт 2 займає регістр IC1.", [("Байт 2", NEG), ("Байт 3", POS), ("порожньо", MUTED)]),
        ("Фаза 3: Зсув третього байта (після 24 тактів)", "Байт 3 досяг IC3, Байт 2 став у IC2, Байт 1 зайняв IC1.", [("Байт 1", FIELD), ("Байт 2", NEG), ("Байт 3", POS)]),
        ("Фаза 4: Фіксація (Фронт CS 0 → 1)", "Одночасне замикання тіньових регістрів виводу (Latch) на всіх мікросхемах.", [("Вихід 1", FIELD), ("Вихід 2", NEG), ("Вихід 3", POS)])
    ]

    y_start = 85
    row_h = 82

    for s_idx, (title, subtitle, contents) in enumerate(steps):
        sy = y_start + s_idx * row_h
        # Рамка фази
        bg_col = "#f6fbf7" if s_idx == 3 else "#fdfdfe"
        border_col = FIELD if s_idx == 3 else "#d8dee4"
        p.append(rect(25, sy, 770, 72, fill=bg_col, stroke=border_col, sw=1.2, rx=4))

        # Опис кроку ліворуч
        p.append(text(35, sy + 22, title, size=11, color=FIELD if s_idx == 3 else INK, bold=True, anchor="start"))
        p.append(text(35, sy + 40, subtitle, size=9.5, color=MUTED, anchor="start"))

        # Блоки регістрів праворуч
        dev_w = 90
        dev_h = 32
        base_x = 450
        for d_idx, (c_label, c_col) in enumerate(contents):
            cx = base_x + d_idx * 115
            cy = sy + 30
            # Коробка регістра
            p.append(rect(cx, cy, dev_w, dev_h, fill="#ffffff", stroke=c_col if c_col != MUTED else "#cbd5e1", sw=1.5, rx=3))
            p.append(text(cx + dev_w / 2, cy + 14, f"IC {d_idx + 1}", size=9, color=MUTED, bold=True))
            p.append(text(cx + dev_w / 2, cy + 26, c_label, size=10, color=c_col, bold=True))

            # Стрілка зсуву між регістрами (якщо не остання фаза і не останній пристрій)
            if s_idx < 3 and d_idx < 2:
                p.append(arrow(cx + dev_w + 3, cy + dev_h / 2, cx + 112, cy + dev_h / 2, color=MUTED, sw=1.2))

        if s_idx == 3:
            # Позначка Latch
            p.append(text(base_x + 145, sy + 18, "Засувка (CS = 1): виходи оновлено синхронно", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 18, "Завдяки двоступеневій структурі (Shift + Latch) виходи не блимають під час зсуву", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "shift-frame.svg"), W, H, *p,
           title="Послідовне просування байтів крізь зсувні регістри мікросхем")


# ── 3. timing-propagation.svg: Нагромадження затримок розповсюдження ──────────
def fig_timing_propagation():
    W, H = 820, 440
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1))
    p.append(text(W / 2, 38, "Часові затримки розповсюдження SDO (Clock-to-Out) у каскаді", size=15, color=INK, bold=True))
    p.append(text(W / 2, 58, "SCLK надходить паралельно, а вихідні дані SDO затримуються на t_prop(SDO) у кожній ланці", size=11.5, color=MUTED, italic=True))

    # Вісь часу
    t_x0, t_x1 = 160, 770
    p.append(line(t_x0, 400, t_x1, 400, color=LINE, sw=1.2))
    p.append(arrow(t_x1 - 10, 400, t_x1, 400, color=LINE, sw=1.2))
    p.append(text(t_x1, 418, "Час (t)", size=10, color=MUTED, anchor="end", italic=True))

    # Рівні сигналів
    sig_y = [110, 165, 220, 275, 330]
    sig_names = [
        ("SCLK", SCKCOL, "Тактовий сигнал ведучого"),
        ("MOSI (SDI1)", MOSICOL, "Дані на вході IC1"),
        ("SDO1 (SDI2)", MISOCOL, "Вихід IC1 після затримки t_prop"),
        ("SDO2 (SDI3)", MISOCOL, "Вихід IC2 після затримки 2 · t_prop"),
        ("MISO (SDO_N)", POS, "Дані повертаються у ведучий")
    ]

    for idx, (name, col, desc) in enumerate(sig_names):
        y = sig_y[idx]
        p.append(text(t_x0 - 15, y + 6, name, size=11, color=col, bold=True, anchor="end"))
        p.append(text(t_x0 - 15, y + 20, desc, size=9.5, color=MUTED, anchor="end"))
        # Тонка лінія розмежування
        p.append(line(t_x0, y + 30, t_x1, y + 30, color="#f0f2f5", sw=1))

    # Малюємо тактові імпульси SCLK
    clk_edges = [220, 340, 460, 580, 700]
    for i in range(len(clk_edges) - 1):
        x1 = clk_edges[i]
        x2 = clk_edges[i] + 60
        x3 = clk_edges[i+1]
        y_hi, y_lo = sig_y[0] - 12, sig_y[0] + 12
        p.append(line(x1, y_lo, x1, y_hi, color=SCKCOL, sw=1.8))
        p.append(line(x1, y_hi, x2, y_hi, color=SCKCOL, sw=1.8))
        p.append(line(x2, y_hi, x2, y_lo, color=SCKCOL, sw=1.8))
        p.append(line(x2, y_lo, x3, y_lo, color=SCKCOL, sw=1.8))

        # Пунктир тактового фронту вниз
        p.append(line(x1, y_lo, x1, 385, color="#cbd5e1", sw=1, dash="3 3"))

    # Сигнал MOSI (синхронний з ведучим)
    y_m = sig_y[1]
    p.append(line(t_x0, y_m + 10, 200, y_m + 10, color=MOSICOL, sw=1.6))
    p.append(line(200, y_m + 10, 205, y_m - 10, color=MOSICOL, sw=1.6))
    p.append(line(205, y_m - 10, 320, y_m - 10, color=MOSICOL, sw=1.6))
    p.append(line(320, y_m - 10, 325, y_m + 10, color=MOSICOL, sw=1.6))
    p.append(line(325, y_m + 10, 440, y_m + 10, color=MOSICOL, sw=1.6))
    p.append(line(440, y_m + 10, 445, y_m - 10, color=MOSICOL, sw=1.6))
    p.append(line(445, y_m - 10, t_x1, y_m - 10, color=MOSICOL, sw=1.6))

    # Сигнал SDO1 (зсунутий на t_prop1 ≈ 25px)
    y_s1 = sig_y[2]
    p.append(line(t_x0, y_s1 + 10, 245, y_s1 + 10, color=MISOCOL, sw=1.6))
    p.append(line(245, y_s1 + 10, 250, y_s1 - 10, color=MISOCOL, sw=1.6))
    p.append(line(250, y_s1 - 10, 365, y_s1 - 10, color=MISOCOL, sw=1.6))
    p.append(line(365, y_s1 - 10, 370, y_s1 + 10, color=MISOCOL, sw=1.6))
    p.append(line(370, y_s1 + 10, t_x1, y_s1 + 10, color=MISOCOL, sw=1.6))

    # Сигнал SDO2 (зсунутий на 2*t_prop1 ≈ 50px)
    y_s2 = sig_y[3]
    p.append(line(t_x0, y_s2 + 10, 270, y_s2 + 10, color=MISOCOL, sw=1.6))
    p.append(line(270, y_s2 + 10, 275, y_s2 - 10, color=MISOCOL, sw=1.6))
    p.append(line(275, y_s2 - 10, 390, y_s2 - 10, color=MISOCOL, sw=1.6))
    p.append(line(390, y_s2 - 10, 395, y_s2 + 10, color=MISOCOL, sw=1.6))
    p.append(line(395, y_s2 + 10, t_x1, y_s2 + 10, color=MISOCOL, sw=1.6))

    # Сигнал MISO (сумарна затримка N*t_prop)
    y_sn = sig_y[4]
    p.append(line(t_x0, y_sn + 10, 310, y_sn + 10, color=POS, sw=1.8))
    p.append(line(310, y_sn + 10, 315, y_sn - 10, color=POS, sw=1.8))
    p.append(line(315, y_sn - 10, 430, y_sn - 10, color=POS, sw=1.8))
    p.append(line(430, y_sn - 10, 435, y_sn + 10, color=POS, sw=1.8))
    p.append(line(435, y_sn + 10, t_x1, y_sn + 10, color=POS, sw=1.8))

    # Стрілки та позначення затримки t_prop
    p.append(line(220, sig_y[0] + 15, 245, sig_y[2] - 12, color=MUTED, sw=1.2, dash="2 2"))
    p.append(text(242, sig_y[2] - 15, "t_prop", size=9, color=MUTED, bold=True))

    p.append(line(220, sig_y[0] + 15, 310, sig_y[4] - 12, color=POS, sw=1.2, dash="2 2"))
    p.append(text(275, sig_y[4] - 15, "Затримка N-ї ланки", size=9, color=POS, bold=True))

    # Виділення часу встановлення t_setup
    p.append(rect(430, 310, 30, 35, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    p.append(text(445, 370, "t_setup порушено при надто високій частоті", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "timing-propagation.svg"), W, H, *p,
           title="Часові затримки розповсюдження SDO та межа тактової частоти")


# ── 4. fault-diagnostics.svg: Діагностика обриву та локалізація несправності ──
def fig_fault_diagnostics():
    W, H = 820, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1))
    p.append(text(W / 2, 36, "Діагностика обриву ланцюга через повнодуплексний зворотний зв'язок (MISO)", size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "Ведучий надсилає тестовий сигнатурний вектор; обрив на ланці K проявляється нулями/одиницями", size=11, color=MUTED, italic=True))

    # Справний ланцюг (Зверху)
    p.append(rect(20, 75, 780, 145, fill="#f6fbf7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(35, 96, "Справний каскад: сигнатура проходить крізь усі мікросхеми", size=11.5, color=FIELD, bold=True, anchor="start"))

    # Ведучий зверху
    p.append(rect(35, 115, 80, 85, fill="#eef4fb", stroke=NEG, sw=1.2))
    p.append(text(75, 142, "ВЕДУЧИЙ", size=10, color=NEG, bold=True))
    p.append(text(75, 158, "TX: 0xAA55", size=9, color=MOSICOL, bold=True))
    p.append(text(75, 174, "RX: 0xAA55 ✓", size=9, color=FIELD, bold=True))

    # IC1, IC2, IC3, IC4 зверху
    top_xs = [170, 310, 450, 590]
    for i, x in enumerate(top_xs):
        p.append(rect(x, 120, 95, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
        p.append(text(x + 47, 142, f"IC {i+1}", size=11, color=INK, bold=True))
        p.append(text(x + 47, 160, "Регістр OK", size=9, color=MUTED))
        p.append(text(x + 47, 175, f"0x{i+1:02X} дані", size=9, color=FIELD))

        # Стрілка вперед
        if i == 0:
            p.append(arrow(115, 150, 170, 150, color=MOSICOL, sw=1.4))
        if i < 3:
            p.append(arrow(x + 95, 150, top_xs[i+1], 150, color=FIELD, sw=1.4))

    # Повернення MISO зверху
    p.append(line(685, 150, 750, 150, color=FIELD, sw=1.4))
    p.append(line(750, 150, 750, 195, color=FIELD, sw=1.4))
    p.append(line(750, 195, 75, 195, color=FIELD, sw=1.4))
    p.append(line(75, 195, 75, 200, color=FIELD, sw=1.4))

    # Несправний ланцюг з обривом (Знизу)
    p.append(rect(20, 235, 780, 160, fill="#fffaf9", stroke=POS, sw=1.2, rx=4))
    p.append(text(35, 256, "Обрив між IC2 та IC3: локалізація місця аварії", size=11.5, color=POS, bold=True, anchor="start"))

    # Ведучий знизу
    p.append(rect(35, 275, 80, 95, fill="#eef4fb", stroke=NEG, sw=1.2))
    p.append(text(75, 302, "ВЕДУЧИЙ", size=10, color=NEG, bold=True))
    p.append(text(75, 318, "TX: 0xAA55", size=9, color=MOSICOL, bold=True))
    p.append(text(75, 335, "RX: 0x0000 ✗", size=9, color=POS, bold=True))
    p.append(text(75, 352, "Помилка IC3..4", size=9.5, color=POS))

    bot_xs = [170, 310, 450, 590]
    for i, x in enumerate(bot_xs):
        is_broken_downstream = (i >= 2)
        b_stroke = POS if is_broken_downstream else (FIELD if i < 2 else INK)
        b_fill = "#fee2e2" if is_broken_downstream else "#ffffff"

        p.append(rect(x, 280, 95, 75, fill=b_fill, stroke=b_stroke, sw=1.2, rx=3))
        p.append(text(x + 47, 302, f"IC {i+1}", size=11, color=INK, bold=True))
        if i < 2:
            p.append(text(x + 47, 320, "Працює", size=9, color=FIELD))
            p.append(text(x + 47, 335, f"0x{i+1:02X} дані", size=9, color=FIELD))
        else:
            p.append(text(x + 47, 320, "Немає входу", size=9, color=POS))
            p.append(text(x + 47, 335, "0x0000 (Pull-down)", size=9.5, color=POS))

        if i == 0:
            p.append(arrow(115, 310, 170, 310, color=MOSICOL, sw=1.4))
        elif i == 1:
            # Обрив після IC2
            p.append(line(x + 95, 310, x + 115, 310, color=FIELD, sw=1.4))
            p.append(text(x + 120, 305, "ОБРИВ", size=9.5, color=POS, bold=True))
            p.append(line(x + 115, 302, x + 125, 318, color=POS, sw=2))
            p.append(line(x + 125, 302, x + 115, 318, color=POS, sw=2))
            p.append(arrow(x + 130, 310, bot_xs[i+1], 310, color=POS, sw=1.4))
        elif i == 2:
            p.append(arrow(x + 95, 310, bot_xs[i+1], 310, color=POS, sw=1.4))

    # Повернення MISO знизу (порожні нулі)
    p.append(line(685, 310, 750, 310, color=POS, sw=1.4, dash="3 3"))
    p.append(line(750, 310, 750, 380, color=POS, sw=1.4))
    p.append(line(750, 380, 75, 380, color=POS, sw=1.4))
    p.append(line(75, 380, 75, 370, color=POS, sw=1.4))

    render(os.path.join(OUT, "fault-diagnostics.svg"), W, H, *p,
           title="Діагностика обриву лінії та локалізація несправності")


def main():
    fig_topology()
    fig_shift_frame()
    fig_timing_propagation()
    fig_fault_diagnostics()
    print("Всі фігури згенеровано успішно.")

if __name__ == "__main__":
    main()
