# -*- coding: utf-8 -*-
"""Фігури теми «Шина I3C» (book/communications/buses/i3c).
Чистий Python без зовнішніх залежностей; svgkit імпортується зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Топологія шини I3C ──────────────────────────────────────────────────
def fig_topology():
    W, H = 960, 470
    p = []
    p.append(text(W/2, 26, "Топологія та фізичний рівень шини MIPI I3C", size=17, bold=True))
    p.append(text(W/2, 46, "Двопровідна магістраль: динамічний Push-Pull/Open-Drain, внутрішньосмугові переривання без ліній INT", size=12, color=MUTED, italic=True))

    y_scl = 135
    y_sda = 185

    p.append(rect(40, 75, 880, 145, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))

    # High-Keeper / Pull-Up Block placed inside background rect
    p.append(rect(80, 85, 160, 30, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(160, 104, "High-Keeper / Підтяжка", size=10, bold=True, color="#92400e"))

    p.append(line(70, y_scl, 820, y_scl, color=POS, sw=3))
    p.append(text(60, y_scl+4, "SCL", size=13, bold=True, color=POS, anchor="end"))
    p.append(text(830, y_scl+4, "12.5 МГц", size=11, bold=True, color=POS, anchor="start"))

    p.append(line(70, y_sda, 820, y_sda, color=NEG, sw=3))
    p.append(text(60, y_sda+4, "SDA", size=13, bold=True, color=NEG, anchor="end"))
    p.append(text(830, y_sda+4, "Дані / IBI / DAA", size=11, bold=True, color=NEG, anchor="start"))

    devs = [
        {"x": 120, "w": 170, "title": "Головний контролер", "sub": "Main Controller (Primary)", "role": "Тактування SCL, Push-Pull, DAA", "fill": "#eff6ff", "stroke": "#3b82f6"},
        {"x": 325, "w": 170, "title": "Вторинний контролер", "sub": "Secondary Controller", "role": "Handover, Target у спокої", "fill": "#f0fdf4", "stroke": "#22c55e"},
        {"x": 530, "w": 170, "title": "Цільовий I3C давач", "sub": "I3C Target (IMU/ToF)", "role": "DAA, IBI переривання, SDR/HDR", "fill": "#faf5ff", "stroke": "#a855f7"},
        {"x": 735, "w": 170, "title": "Сумісний I2C ведений", "sub": "Legacy I2C Slave", "role": "50 нс фільтр, Open-Drain, 400 кГц", "fill": "#fff1f2", "stroke": "#f43f5e"},
    ]

    y_dev = 255
    for d in devs:
        cx = d["x"] + d["w"] / 2
        p.append(line(cx - 20, y_scl, cx - 20, y_dev, color=POS, sw=2))
        p.append(circle(cx - 20, y_scl, 4, fill=POS, stroke="none"))
        p.append(line(cx + 20, y_sda, cx + 20, y_dev, color=NEG, sw=2))
        p.append(circle(cx + 20, y_sda, 4, fill=NEG, stroke="none"))

        p.append(rect(d["x"], y_dev, d["w"], 120, fill=d["fill"], stroke=d["stroke"], sw=1.8, rx=8))
        p.append(text(cx, y_dev + 24, d["title"], size=12.5, bold=True, color=INK))
        p.append(text(cx, y_dev + 42, d["sub"], size=10, bold=False, color=MUTED))
        p.append(line(d["x"] + 10, y_dev + 52, d["x"] + d["w"] - 10, y_dev + 52, color="#e2e8f0", sw=1))
        p.append(fitbox(d["x"] + 8, y_dev + 58, d["w"] - 16, 52, d["role"], size=11, fill="none", stroke="none", color="#334155"))

    p.append(rect(40, 400, 880, 52, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=6))
    p.append(text(W/2, 421, "Немає окремих ліній CS (як в SPI) та INT/DRDY (як в I2C). Усі переривання та конфігурація передаються по SDA.", size=11.5, bold=True, color="#1e293b"))
    p.append(text(W/2, 439, "Контролер динамічно перемикає лінії між Open-Drain (старт, адреса, арбітраж) та Push-Pull (дані 12.5 Мбіт/с).", size=11, color=MUTED))

    render(os.path.join(OUT, "i3c-topology.svg"), W, H, *p)


# ── 2. Динамічне перемикання Open-Drain -> Push-Pull ─────────────────────────
def fig_push_pull_switch():
    W, H = 940, 440
    p = []
    p.append(text(W/2, 26, "Динамічне перемикання режимів драйвера в кадрі I3C SDR", size=17, bold=True))
    p.append(text(W/2, 46, "Відкритий стік (Open-Drain) для адреси й арбітражу → Двотактний каскад (Push-Pull) для даних на 12.5 МГц", size=12, color=MUTED, italic=True))

    zones = [
        {"x": 60, "w": 110, "name": "START / Заголовок", "mode": "Open-Drain", "color": "#fef3c7", "stroke": "#d97706", "txt": "#92400e"},
        {"x": 170, "w": 200, "name": "7-біт Динамічна Адреса + R/W", "mode": "Open-Drain (Арбітраж)", "color": "#fef3c7", "stroke": "#d97706", "txt": "#92400e"},
        {"x": 370, "w": 80, "name": "ACK / NACK", "mode": "Open-Drain", "color": "#fee2e2", "stroke": "#dc2626", "txt": "#991b1b"},
        {"x": 450, "w": 190, "name": "Байт даних 1 (D7..D0 + T)", "mode": "Push-Pull (12.5 Мбіт/с)", "color": "#dcfce7", "stroke": "#16a34a", "txt": "#166534"},
        {"x": 640, "w": 190, "name": "Байт даних 2 (D7..D0 + T)", "mode": "Push-Pull (12.5 Мбіт/с)", "color": "#dcfce7", "stroke": "#16a34a", "txt": "#166534"},
        {"x": 830, "w": 60, "name": "STOP", "mode": "Open-Drain", "color": "#fef3c7", "stroke": "#d97706", "txt": "#92400e"},
    ]

    y_z = 70
    for z in zones:
        p.append(rect(z["x"], y_z, z["w"], 44, fill=z["color"], stroke=z["stroke"], sw=1.2, rx=4))
        p.append(text(z["x"] + z["w"]/2, y_z + 18, z["name"], size=10.5, bold=True, color=z["txt"]))
        p.append(text(z["x"] + z["w"]/2, y_z + 34, z["mode"], size=9, color=MUTED))

    y_scl = 180
    y_sda = 270

    p.append(text(45, y_scl+10, "SCL", size=13, bold=True, color=POS, anchor="end"))
    p.append(text(45, y_sda+10, "SDA", size=13, bold=True, color=NEG, anchor="end"))

    p.append(line(60, y_scl - 30, 890, y_scl - 30, color="#e2e8f0", sw=1))
    p.append(line(60, y_scl + 30, 890, y_scl + 30, color="#e2e8f0", sw=1))
    p.append(line(60, y_sda - 30, 890, y_sda - 30, color="#e2e8f0", sw=1))
    p.append(line(60, y_sda + 30, 890, y_sda + 30, color="#e2e8f0", sw=1))

    p.append(line(60, y_scl-20, 100, y_scl-20, color=POS, sw=2))
    p.append(line(100, y_scl-20, 110, y_scl+20, color=POS, sw=2))
    x = 110
    for _ in range(4):
        p.append(line(x, y_scl+20, x+30, y_scl+20, color=POS, sw=2))
        p.append(line(x+30, y_scl+20, x+45, y_scl-20, color=POS, sw=2))
        p.append(line(x+45, y_scl-20, x+65, y_scl-20, color=POS, sw=2))
        p.append(line(x+65, y_scl-20, x+75, y_scl+20, color=POS, sw=2))
        x += 75

    p.append(line(450, 65, 450, 320, color="#16a34a", sw=1.8, dash="4,3"))
    p.append(line(830, 65, 830, 320, color="#d97706", sw=1.8, dash="4,3"))

    x = 450
    for _ in range(16):
        p.append(line(x, y_scl+20, x+2, y_scl-20, color=POS, sw=2.2))
        p.append(line(x+2, y_scl-20, x+11, y_scl-20, color=POS, sw=2.2))
        p.append(line(x+11, y_scl-20, x+13, y_scl+20, color=POS, sw=2.2))
        p.append(line(x+13, y_scl+20, x+23, y_scl+20, color=POS, sw=2.2))
        x += 23.5

    p.append(line(830, y_scl+20, 850, y_scl-20, color=POS, sw=2))
    p.append(line(850, y_scl-20, 890, y_scl-20, color=POS, sw=2))

    p.append(line(60, y_sda-20, 85, y_sda-20, color=NEG, sw=2))
    p.append(line(85, y_sda-20, 95, y_sda+20, color=NEG, sw=2))
    p.append(line(95, y_sda+20, 130, y_sda+20, color=NEG, sw=2))

    p.append(line(130, y_sda+20, 150, y_sda-20, color=NEG, sw=2))
    p.append(line(150, y_sda-20, 210, y_sda-20, color=NEG, sw=2))
    p.append(line(210, y_sda-20, 225, y_sda+20, color=NEG, sw=2))
    p.append(line(225, y_sda+20, 290, y_sda+20, color=NEG, sw=2))
    p.append(line(290, y_sda+20, 310, y_sda-20, color=NEG, sw=2))
    p.append(line(310, y_sda-20, 360, y_sda-20, color=NEG, sw=2))
    p.append(line(360, y_sda-20, 375, y_sda+20, color=NEG, sw=2))
    p.append(line(375, y_sda+20, 440, y_sda+20, color=NEG, sw=2))
    p.append(line(440, y_sda+20, 450, y_sda-20, color=NEG, sw=2))

    x = 450
    levels = [1, 0, 1, 1, 0, 1, 0, 0, 1,   0, 1, 1, 0, 0, 1, 0, 1, 0]
    for i, lev in enumerate(levels):
        y_target = y_sda - 20 if lev == 1 else y_sda + 20
        p.append(line(x, y_target, x+21, y_target, color=NEG, sw=2.2))
        x += 21
        if i < len(levels) - 1:
            next_y = y_sda - 20 if levels[i+1] == 1 else y_sda + 20
            p.append(line(x, y_target, x+1, next_y, color=NEG, sw=2.2))

    p.append(line(830, y_sda+20, 865, y_sda+20, color=NEG, sw=2))
    p.append(line(865, y_sda+20, 875, y_sda-20, color=NEG, sw=2))
    p.append(line(875, y_sda-20, 890, y_sda-20, color=NEG, sw=2))

    p.append(rect(60, 350, 380, 70, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(250, 372, "Фаза відкритого стоку (Open-Drain)", size=11.5, bold=True, color="#92400e"))
    p.append(text(250, 390, "Плавні фронти через RC-ланцюг підтяжки.", size=10.5, color="#78350f"))
    p.append(text(250, 406, "Забезпечує сумісність з I2C та безконфліктний арбітраж.", size=10, color=MUTED))

    p.append(rect(460, 350, 420, 70, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    p.append(text(670, 372, "Фаза Push-Pull (12.5 МГц)", size=11.5, bold=True, color="#166534"))
    p.append(text(670, 390, "Круті активні фронти, немає розсіювання струму на резисторі.", size=10.5, color="#14532d"))
    p.append(text(670, 406, "Замість ACK кожен байт завершується перехідним бітом парності (T-bit).", size=10, color=MUTED))

    render(os.path.join(OUT, "i3c-push-pull-switch.svg"), W, H, *p)


# ── 3. Процедура DAA (Dynamic Address Assignment) ───────────────────────────
def fig_daa_flow():
    W, H = 940, 450
    p = []
    p.append(text(W/2, 26, "Динамічне призначення адрес (ENTDAA) та арбітраж 48-бітного ID", size=17, bold=True))
    p.append(text(W/2, 46, "Порозрядне порівняння Provisional ID на відкритому стоці: нуль перемагає одиницю", size=12, color=MUTED, italic=True))

    steps = [
        {"x": 50, "y": 75, "w": 260, "h": 70, "t": "1. Команда контролера", "d": "Широкомовна команда CCC 0x07 (ENTDAA)\nПереводить усі неініціалізовані цілі в режим DAA", "bg": "#eff6ff", "br": "#3b82f6"},
        {"x": 340, "y": 75, "w": 260, "h": 70, "t": "2. Передача 48-біт ID + BCR/DCR", "d": "Усі цілі одночасно видають свій PID біт-за-бітом\nДомінантний нуль витісняє одиницю", "bg": "#fef3c7", "br": "#d97706"},
        {"x": 630, "y": 75, "w": 260, "h": 70, "t": "3. Призначення адреси", "d": "Контролер шле унікальну 7-бітну Dynamic Address\nПереможець вимикається з подальших раундів DAA", "bg": "#dcfce7", "br": "#16a34a"},
    ]

    for s in steps:
        p.append(rect(s["x"], s["y"], s["w"], s["h"], fill=s["bg"], stroke=s["br"], sw=1.5, rx=6))
        p.append(text(s["x"] + s["w"]/2, s["y"] + 22, s["t"], size=12, bold=True, color=INK))
        p.append(fitbox(s["x"] + 8, s["y"] + 28, s["w"] - 16, 38, s["d"], size=10, fill="none", stroke="none", color=MUTED))

    p.append(arrow(310, 110, 335, 110, color=LINE, sw=1.8))
    p.append(arrow(600, 110, 625, 110, color=LINE, sw=1.8))

    y_arb = 165
    p.append(rect(50, y_arb, 840, 205, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(W/2, y_arb + 24, "Приклад арбітражу на 5-му біті Provisional ID між двома давачами", size=13, bold=True, color=INK))

    cols = [
        {"x": 70, "w": 220, "name": "Поле / Біт", "sub": "48-бітний Provisional ID"},
        {"x": 290, "w": 160, "name": "Біт 1 (MSB)", "sub": "MIPI Vendor ID"},
        {"x": 450, "w": 160, "name": "Біт 2 .. 4", "sub": "Part ID"},
        {"x": 610, "w": 130, "name": "Біт 5 (Конфлікт)", "sub": "Instance ID"},
        {"x": 740, "w": 130, "name": "Результат раунду", "sub": "Статус цілі"},
    ]

    for c in cols:
        p.append(rect(c["x"], y_arb + 40, c["w"], 32, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
        p.append(text(c["x"] + c["w"]/2, y_arb + 56, c["name"], size=11, bold=True, color=INK))
        p.append(text(c["x"] + c["w"]/2, y_arb + 68, c["sub"], size=9, color=MUTED))

    ya = y_arb + 80
    p.append(rect(70, ya, 220, 38, fill="#faf5ff", stroke="#a855f7", sw=1, rx=4))
    p.append(text(180, ya + 23, "Давач A (IMU): ID = ...0...", size=11, bold=True, color="#6b21a8"))
    p.append(rect(290, ya, 160, 38, fill="#faf5ff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(370, ya + 23, "0 (збіг)", size=11, color=INK))
    p.append(rect(450, ya, 160, 38, fill="#faf5ff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(530, ya + 23, "1, 0, 1 (збіг)", size=11, color=INK))
    p.append(rect(610, ya, 130, 38, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    p.append(text(675, ya + 23, "0 (тягне до 0)", size=11, bold=True, color="#166534"))
    p.append(rect(740, ya, 130, 38, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    p.append(text(805, ya + 23, "Виграв → Адреса 0x08", size=10, bold=True, color="#166534"))

    yb = ya + 46
    p.append(rect(70, yb, 220, 38, fill="#fff1f2", stroke="#f43f5e", sw=1, rx=4))
    p.append(text(180, yb + 23, "Давач B (ToF): ID = ...1...", size=11, bold=True, color="#9f1239"))
    p.append(rect(290, yb, 160, 38, fill="#fff1f2", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(370, yb + 23, "0 (збіг)", size=11, color=INK))
    p.append(rect(450, yb, 160, 38, fill="#fff1f2", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(530, yb + 23, "1, 0, 1 (збіг)", size=11, color=INK))
    p.append(rect(610, yb, 130, 38, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(675, yb + 23, "1 (бачить на SDA 0)", size=11, bold=True, color="#991b1b"))
    p.append(rect(740, yb, 130, 38, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(805, yb + 23, "Програв → чекає раунд 2", size=9.5, bold=True, color="#991b1b"))

    ysda = yb + 46
    p.append(rect(70, ysda, 800, 24, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(W/2, ysda + 16, "Спільний стан лінії SDA: на 5-му біті залишається '0'. Давач B миттєво глушить свій вихід.", size=10.5, italic=True, color="#334155"))

    p.append(rect(50, 385, 840, 50, fill="#f8fafc", stroke="#64748b", sw=1, rx=6))
    p.append(text(W/2, 406, "Повний цикл DAA повторюється доти, доки на черговий запит ENTDAA жоден пристрій не притягне SDA до нуля.", size=11, bold=True, color="#0f172a"))
    p.append(text(W/2, 424, "Це усуває всі апаратні конфлікти статичних адрес I2C раз і назавжди без жодних DIP-перемикачів.", size=10.5, color=MUTED))

    render(os.path.join(OUT, "i3c-daa-flow.svg"), W, H, *p)


# ── 4. Внутрішньосмугові переривання (In-Band Interrupts, IBI) ───────────────
def fig_ibi_timeline():
    W, H = 940, 440
    p = []
    p.append(text(W/2, 26, "Внутрішньосмугове переривання (In-Band Interrupt, IBI)", size=17, bold=True))
    p.append(text(W/2, 46, "Асинхронний запит давача по лінії SDA без виділеного апаратного виводу GPIO INT", size=12, color=MUTED, italic=True))

    phases = [
        {"x": 60, "w": 140, "t": "1. Стан спокою", "sub": "Bus Idle (SDA=1, SCL=1)", "bg": "#f1f5f9", "br": "#94a3b8"},
        {"x": 210, "w": 180, "t": "2. Запит переривання", "sub": "Давач притягує SDA до '0'", "bg": "#fee2e2", "br": "#ef4444"},
        {"x": 400, "w": 220, "t": "3. Арбітраж адреси IBI", "sub": "Давач видає свою Dynamic Addr + RnW=1", "bg": "#fef3c7", "br": "#f59e0b"},
        {"x": 630, "w": 110, "t": "4. Відповідь ACK", "sub": "Контролер підтверджує", "bg": "#dcfce7", "br": "#22c55e"},
        {"x": 750, "w": 130, "t": "5. Передача MDB", "sub": "Обов'язковий байт даних", "bg": "#eff6ff", "br": "#3b82f6"},
    ]

    y_p = 75
    for ph in phases:
        p.append(rect(ph["x"], y_p, ph["w"], 46, fill=ph["bg"], stroke=ph["br"], sw=1.2, rx=4))
        p.append(text(ph["x"] + ph["w"]/2, y_p + 19, ph["t"], size=10.5, bold=True, color=INK))
        p.append(text(ph["x"] + ph["w"]/2, y_p + 35, ph["sub"], size=9, color=MUTED))

    y_scl = 180
    y_sda = 260

    p.append(text(45, y_scl+6, "SCL", size=13, bold=True, color=POS, anchor="end"))
    p.append(text(45, y_sda+6, "SDA", size=13, bold=True, color=NEG, anchor="end"))

    p.append(line(60, y_scl - 25, 880, y_scl - 25, color="#e2e8f0", sw=1))
    p.append(line(60, y_scl + 25, 880, y_scl + 25, color="#e2e8f0", sw=1))
    p.append(line(60, y_sda - 25, 880, y_sda - 25, color="#e2e8f0", sw=1))
    p.append(line(60, y_sda + 25, 880, y_sda + 25, color="#e2e8f0", sw=1))

    p.append(line(60, y_scl-20, 240, y_scl-20, color=POS, sw=2))
    p.append(line(240, y_scl-20, 250, y_scl+20, color=POS, sw=2))
    x = 250
    for _ in range(12):
        p.append(line(x, y_scl+20, x+20, y_scl+20, color=POS, sw=2))
        p.append(line(x+20, y_scl+20, x+25, y_scl-20, color=POS, sw=2))
        p.append(line(x+25, y_scl-20, x+45, y_scl-20, color=POS, sw=2))
        p.append(line(x+45, y_scl-20, x+50, y_scl+20, color=POS, sw=2))
        x += 50

    p.append(line(60, y_sda-20, 200, y_sda-20, color=MUTED, sw=2))
    p.append(line(200, y_sda-20, 215, y_sda+20, color=NEG, sw=2.5))
    p.append(text(210, y_sda+38, "Запит IBI", size=10, bold=True, color="#dc2626"))

    p.append(line(215, y_sda+20, 280, y_sda+20, color=NEG, sw=2))
    p.append(line(280, y_sda+20, 290, y_sda-20, color=NEG, sw=2))
    p.append(line(290, y_sda-20, 340, y_sda-20, color=NEG, sw=2))
    p.append(line(340, y_sda-20, 350, y_sda+20, color=NEG, sw=2))
    p.append(line(350, y_sda+20, 520, y_sda+20, color=NEG, sw=2))
    p.append(line(520, y_sda+20, 530, y_sda-20, color=NEG, sw=2))
    p.append(line(530, y_sda-20, 580, y_sda-20, color=NEG, sw=2))
    p.append(line(580, y_sda-20, 590, y_sda+20, color=NEG, sw=2))
    p.append(line(590, y_sda+20, 650, y_sda+20, color=POS, sw=2))
    p.append(text(620, y_sda+36, "ACK (0)", size=9.5, bold=True, color="#16a34a"))

    p.append(line(650, y_sda+20, 665, y_sda-20, color=NEG, sw=2))
    p.append(line(665, y_sda-20, 720, y_sda-20, color=NEG, sw=2))
    p.append(line(720, y_sda-20, 730, y_sda+20, color=NEG, sw=2))
    p.append(line(730, y_sda+20, 800, y_sda+20, color=NEG, sw=2))
    p.append(line(800, y_sda+20, 810, y_sda-20, color=NEG, sw=2))
    p.append(line(810, y_sda-20, 880, y_sda-20, color=NEG, sw=2))

    p.append(rect(60, 335, 820, 90, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(W/2, 356, "Перевага: Давач відправляє причину переривання (MDB) одразу в кадрі IBI", size=11.5, bold=True, color="#0f172a"))
    p.append(text(W/2, 375, "Контролеру не потрібно робити повторний окремий запит читання статусного регістра (як в I2C).", size=11, color="#334155"))
    p.append(text(W/2, 393, "Якщо одночасно переривання шлють два давачі, арбітраж виграє той, у кого менша динамічна адреса.", size=10.5, color=MUTED))
    p.append(text(W/2, 411, "Економія: на платі смартфона з 15 сенсорами ліквідовано 15 окремих сигнальних доріжок INT.", size=10.5, bold=True, color="#16a34a"))

    render(os.path.join(OUT, "i3c-ibi-timeline.svg"), W, H, *p)


# ── 5. Порівняння швидкісних режимів (I2C vs SDR vs HDR-DDR) ────────────────
def fig_modes_comparison():
    W, H = 940, 450
    p = []
    p.append(text(W/2, 26, "Еволюція швидкості: I2C Fast-Mode Plus, I3C SDR та I3C HDR-DDR", size=17, bold=True))
    p.append(text(W/2, 46, "Відкритий стік (1 Мбіт/с) → Однотактний Push-Pull (12.5 Мбіт/с) → Двоточковий такт DDR (25 Мбіт/с)", size=12, color=MUTED, italic=True))

    rows = [
        {"y": 75, "title": "1. I2C Fast-Mode Plus (Fm+): 1 МГц Open-Drain", "sub": "Повільні спади/фронти через підтяжку R_pullup; 9 тактів на байт (8 біт + ACK); максимум 0.89 Мбіт/с", "color": "#fee2e2", "br": "#dc2626"},
        {"y": 195, "title": "2. I3C SDR (Single Data Rate): 12.5 МГц Push-Pull", "sub": "Активне керування лініями; зчитування по спаду/фронту SCL; 9 тактів на байт (8 біт + T-біт); до 12.5 Мбіт/с", "color": "#dcfce7", "br": "#16a34a"},
        {"y": 315, "title": "3. I3C HDR-DDR (Double Data Rate): 12.5 МГц / 25 Мбіт/с", "sub": "Подвійна швидкість: дані передаються і на наростаючому, і на спадному фронті SCL; корисний потік до 25 Мбіт/с", "color": "#eff6ff", "br": "#2563eb"},
    ]

    for r in rows:
        p.append(rect(50, r["y"], 840, 105, fill=r["color"], stroke=r["br"], sw=1.2, rx=6))
        p.append(text(65, r["y"] + 20, r["title"], size=11.5, bold=True, color=INK, anchor="start"))
        p.append(text(65, r["y"] + 36, r["sub"], size=10, color=MUTED, anchor="start"))

    y1 = 135
    p.append(text(75, y1+15, "SDA", size=11, bold=True, color=NEG, anchor="start"))
    p.append(line(120, y1+20, 150, y1+20, color=NEG, sw=2))
    p.append(line(150, y1+20, 170, y1-10, color=NEG, sw=1.8))
    p.append(line(170, y1-10, 240, y1-10, color=NEG, sw=2))
    p.append(line(240, y1-10, 245, y1+20, color=NEG, sw=2))
    p.append(line(245, y1+20, 310, y1+20, color=NEG, sw=2))
    p.append(line(310, y1+20, 335, y1-10, color=NEG, sw=1.8))
    p.append(line(335, y1-10, 420, y1-10, color=NEG, sw=2))
    p.append(text(500, y1+5, "1 біт = 1000 нс (RC затримка обмежує підйом сигналу)", size=10, bold=True, color="#991b1b"))

    y2 = 255
    p.append(text(75, y2+15, "SDA", size=11, bold=True, color=NEG, anchor="start"))
    x = 120
    for _ in range(8):
        p.append(line(x, y2+18, x+2, y2-12, color=NEG, sw=2))
        p.append(line(x+2, y2-12, x+20, y2-12, color=NEG, sw=2))
        p.append(line(x+20, y2-12, x+22, y2+18, color=NEG, sw=2))
        p.append(line(x+22, y2+18, x+40, y2+18, color=NEG, sw=2))
        x += 40
    p.append(text(500, y2+5, "1 біт = 80 нс (12.5 МГц активні фронти Push-Pull)", size=10, bold=True, color="#166534"))

    y3 = 375
    p.append(text(75, y3+15, "SDA", size=11, bold=True, color=NEG, anchor="start"))
    x = 120
    for _ in range(16):
        p.append(line(x, y3+18, x+1, y3-12, color=NEG, sw=2))
        p.append(line(x+1, y3-12, x+10, y3-12, color=NEG, sw=2))
        p.append(line(x+10, y3-12, x+11, y3+18, color=NEG, sw=2))
        p.append(line(x+11, y3+18, x+20, y3+18, color=NEG, sw=2))
        x += 20
    p.append(text(500, y3+5, "1 біт = 40 нс (25 Мбіт/с подвійна передача на такт SCL)", size=10, bold=True, color="#1e40af"))

    render(os.path.join(OUT, "i3c-modes-comparison.svg"), W, H, *p)


if __name__ == "__main__":
    fig_topology()
    fig_push_pull_switch()
    fig_daa_flow()
    fig_ibi_timeline()
    fig_modes_comparison()
    print("All I3C figures generated successfully.")
