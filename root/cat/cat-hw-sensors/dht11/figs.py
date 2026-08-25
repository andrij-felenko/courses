# -*- coding: utf-8 -*-
"""Фігури до статті DHT11 (catalog/sensors/environment/dht11).
Вивід — ./img/*.svg. Запуск: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Що всередині: два давачі + чип → одна лінія DATA ──────────────────────
def fig_inside():
    W, H = 760, 340
    f = []
    # Корпус модуля
    f.append(rect(30, 60, 700, 240, fill="#eef1f4", stroke=LINE, sw=1.6, rx=12))
    f.append(text(380, 46, "Усередині DHT11", size=17, bold=True))

    # Давач вологості (ліворуч)
    b, w, h = textbox(150, 130, "Ємнісний\nдавач вологості", size=13, pad=12, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    f.append(text(150, 178, "(волога міняє", size=11, color=MUTED))
    f.append(text(150, 194, "ємність плівки)", size=11, color=MUTED))

    # Давач температури (ліворуч нижче)
    b2, w2, h2 = textbox(150, 250, "Термістор (NTC)", size=13, pad=12, fill="#fdecea", stroke=POS)
    f.append(b2)

    # Чип (центр)
    b3, w3, h3 = textbox(410, 165, "8-бітний чип\n(АЦП + пам'ять\n+ калібрування)", size=13, pad=14, fill=FILL, stroke=LINE, bold=True)
    f.append(b3)

    # Стрілки від давачів у чип
    f.append(arrow(213, 130, 355, 150, color=FIELD, sw=2))
    f.append(arrow(232, 250, 355, 185, color=POS, sw=2))

    # Вихід: одна лінія DATA
    b4, w4, h4 = textbox(630, 165, "1 лінія\nDATA", size=14, pad=14, fill="#eef4ff", stroke=NEG, bold=True)
    f.append(b4)
    f.append(arrow(465, 165, 585, 165, color=NEG, sw=2.4))
    f.append(text(525, 150, "цифрові біти", size=11, color=MUTED))

    render(os.path.join(IMG, "dht11-inside.svg"), W, H, *f)


# ── 2. Протокол на одній лінії: старт → відповідь → біт «0» → біт «1» ────────
def fig_protocol():
    W, H = 860, 360
    f = []
    f.append(text(430, 30, "Обмін по одній лінії DATA", size=17, bold=True))

    base = 300          # рівень «низько»
    hi = 200            # рівень «високо»
    x = 40

    def seg_low(x, w, label, sub=None, color=NEG):
        f.append(line(x, base, x + w, base, color=color, sw=3))
        f.append(text(x + w / 2, base + 26, label, size=12, color=color, bold=True))
        if sub:
            f.append(text(x + w / 2, base + 44, sub, size=10, color=MUTED))
        return x + w

    def seg_high(x, w, label, sub=None, color=POS):
        f.append(line(x, hi, x + w, hi, color=color, sw=3))
        f.append(text(x + w / 2, hi - 14, label, size=12, color=color, bold=True))
        if sub:
            f.append(text(x + w / 2, hi - 30, sub, size=10, color=MUTED))
        return x + w

    def edge(x):
        f.append(line(x, base, x, hi, color=INK, sw=2))

    # Старт від хоста: тримає низько ≥ 18 мс
    x = seg_low(x, 150, "хост тягне низько", "≥ 18 мс (старт)")
    edge(x)
    # Хост відпускає, підтяжка тягне високо 20–40 мкс
    x = seg_high(x, 90, "хост відпустив", "20–40 мкс")
    edge(x)
    # DHT відповідає: 80 мкс низько
    x = seg_low(x, 90, "DHT: відповідь", "80 мкс", color=FIELD)
    edge(x)
    # DHT: 80 мкс високо (готовність)
    x = seg_high(x, 90, "готовність", "80 мкс", color=FIELD)
    edge(x)

    # роздільник «далі — 40 біт»
    f.append(line(x + 4, 150, x + 4, 330, color=MUTED, sw=1, dash="4,4"))
    f.append(text(x + 4, 145, "далі 40 біт:", size=11, color=MUTED, bold=True))

    # Біт «0»: 50 мкс низько + 26 мкс високо
    x2 = x + 8
    x2 = seg_low(x2, 70, "50 мкс", None, color=INK)
    edge(x2)
    xb = seg_high(x2, 40, "26 мкс", "= 0", color=INK)
    edge(xb)
    # Біт «1»: 50 мкс низько + 70 мкс високо
    xb = seg_low(xb, 70, "50 мкс", None, color=INK)
    edge(xb)
    xb = seg_high(xb, 90, "70 мкс", "= 1", color=INK)
    edge(xb)

    # ключова підказка знизу
    b, w, h = textbox(430, 344, "Значення біта — у ДОВЖИНІ високого імпульсу після 50 мкс низько: коротко → 0, довго → 1",
                      size=12, pad=8, fill="#fff8e6", stroke="#d6a419")
    f.append(b)

    render(os.path.join(IMG, "dht11-protocol.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: 3-пін модуль і голий 4-пін сенсор ──────────────
def fig_wiring():
    W, H = 820, 400
    f = []
    f.append(text(410, 28, "Підключення до мікроконтролера", size=17, bold=True))

    # ── Ліворуч: 3-пін модуль (підтяжка вже на платі) ──
    f.append(text(200, 60, "3-пін модуль (з підтяжкою)", size=13, bold=True, color=FIELD))
    f.append(rect(60, 80, 130, 210, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(125, 104, "DHT11", size=14, bold=True))
    f.append(text(125, 122, "модуль", size=11, color=MUTED))
    # 3 контакти
    pins3 = [("+", 160, POS), ("OUT", 205, NEG), ("−", 250, INK)]
    for name, y, col in pins3:
        f.append(circle(180, y, 7, fill="#fff", stroke=col, sw=2))
        f.append(text(150, y + 4, name, size=12, color=col, bold=True))
    # МК праворуч від модуля
    f.append(rect(300, 130, 110, 160, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(355, 156, "МК", size=14, bold=True))
    mk3 = [("3.3–5 В", 180, POS), ("GPIO", 205, NEG), ("GND", 250, INK)]
    for name, y, col in mk3:
        f.append(circle(300, y, 6, fill="#fff", stroke=col, sw=2))
        f.append(text(360, y + 4, name, size=11, color=col))
    # дроти
    f.append(line(187, 160, 300, 180, color=POS, sw=2))
    f.append(line(187, 205, 300, 205, color=NEG, sw=2))
    f.append(line(187, 250, 300, 250, color=INK, sw=2))
    f.append(text(235, 318, "Підтяжка вже стоїть", size=11, color=FIELD))
    f.append(text(235, 334, "на платі — просто 3 дроти", size=11, color=MUTED))

    # ── Праворуч: голий 4-пін сенсор (треба свій резистор) ──
    f.append(text(620, 60, "4-пін сенсор (голий)", size=13, bold=True, color=POS))
    f.append(rect(490, 80, 120, 210, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(text(550, 104, "DHT11", size=14, bold=True))
    f.append(text(550, 122, "сенсор", size=11, color=MUTED))
    pins4 = [("VCC", 155, POS), ("DATA", 195, NEG), ("NC", 235, MUTED), ("GND", 275, INK)]
    for name, y, col in pins4:
        f.append(circle(602, y, 6, fill="#fff", stroke=col, sw=2))
        f.append(text(560, y + 4, name, size=11, color=col, bold=(name != "NC")))
    # МК праворуч
    f.append(rect(710, 130, 90, 160, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(755, 156, "МК", size=14, bold=True))
    # дроти
    f.append(line(608, 155, 710, 180, color=POS, sw=2))   # VCC
    f.append(line(608, 195, 710, 205, color=NEG, sw=2))   # DATA
    f.append(line(608, 275, 710, 260, color=INK, sw=2))   # GND
    # резистор підтяжки DATA→VCC
    f.append(line(660, 195, 660, 155, color="#d6a419", sw=2))
    f.append(rect(650, 165, 20, 18, fill="#fff8e6", stroke="#d6a419", sw=1.5, rx=3))
    f.append(text(700, 150, "4.7–10 кОм", size=10, color="#d6a419", bold=True))
    f.append(text(690, 320, "Свій резистор підтяжки", size=11, color="#d6a419"))
    f.append(text(690, 336, "DATA → VCC — обов'язково", size=11, color=MUTED))

    render(os.path.join(IMG, "dht11-wiring.svg"), W, H, *f)


# ── 4. (вставка proj) Скінченний автомат драйвера: старт → відповідь → біти → сума ──
def fig_driver_states():
    W, H = 780, 560
    f = []

    steps = [
        ("СТАРТ ВІД ХОСТА", "притисни DATA до землі\n≥ 18 мс, тоді відпусти", POS),
        ("ЧЕКАЙ ВІДПОВІДЬ", "лови 80 мкс низько +\n80 мкс високо від давача", FIELD),
        ("ЧИТАЙ 40 БІТІВ",  "на кожен: пропусти 50 мкс\nнизько, зміряй ширину\nвисокого імпульсу", INK),
        ("ЗБЕРИ 5 БАЙТІВ",  "8 бітів → байт,\nп'ять байтів у масив", INK),
        ("ПЕРЕВІР СУМУ",    "b0+b1+b2+b3 (нижні 8)\n== b4 ?", NEG),
    ]

    cx = 210
    box_w = 250
    top = 78
    gap = 92
    box_h = 60
    centers = []
    for i, (name, desc, col) in enumerate(steps):
        cy = top + i * gap
        centers.append(cy)
        f.append(rect(cx - box_w / 2, cy - box_h / 2, box_w, box_h,
                      fill="#f4f6f8", stroke=col, sw=2.2, rx=8))
        f.append(text(cx, cy - box_h / 2 + 19, name, size=14, color=col, bold=True))
        f.append(mtext(cx, cy - box_h / 2 + 35, desc, size=10.5, color=MUTED))
        if i < len(steps) - 1:
            f.append(arrow(cx, cy + box_h / 2, cx, cy + gap - box_h / 2, color=INK, sw=1.8))

    # розгалуження після перевірки суми
    last_cy = centers[-1]
    ok_y = last_cy + 84
    f.append(arrow(cx - 40, last_cy + box_h / 2, cx - 120, ok_y - 26, color=FIELD, sw=1.8))
    f.append(arrow(cx + 40, last_cy + box_h / 2, cx + 118, ok_y - 26, color=POS, sw=1.8))
    b1, _, _ = textbox(cx - 128, ok_y + 2, "збіглася:\nдані цілі, віддай", size=11,
                       fill="#eafaf1", stroke=FIELD, color="#1e7a48")
    f.append(b1)
    b2, _, _ = textbox(cx + 128, ok_y + 2, "не збіглася:\nвідкинь, повтори", size=11,
                       fill="#fdecea", stroke=POS, color="#a5271b")
    f.append(b2)

    # права колонка: правило біта
    rx0 = 470
    f.append(rect(rx0, top - 30, 262, 196, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=8))
    f.append(text(rx0 + 131, top - 8, "Правило одного біта", size=13, color=INK, bold=True))
    f.append(mtext(rx0 + 131, top + 16, "низько 50 мкс — завжди\n(роздільник, не дані)",
                   size=10.5, color=MUTED))
    f.append(mtext(rx0 + 131, top + 58, "потім високо:\n≈26 мкс → біт 0\n≈70 мкс → біт 1",
                   size=12, color=INK))
    f.append(text(rx0 + 131, top + 134, "дивишся на ШИРИНУ,", size=10.5, color=NEG, bold=True))
    f.append(text(rx0 + 131, top + 150, "не на рівень лінії", size=10.5, color=NEG, bold=True))

    # права нижня: пауза між читаннями
    f.append(rect(rx0, top + 178, 262, 100, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=8))
    f.append(text(rx0 + 131, top + 200, "Пауза між читаннями", size=13, color=INK, bold=True))
    f.append(mtext(rx0 + 131, top + 224, "≥ 1 с (краще 2 с):\nдавач міряє повільно,\nчастіше — самі помилки",
                   size=11, color=MUTED))

    render(os.path.join(IMG, "dht11-driver-states.svg"), W, H, *f,
           title="Що робить драйвер: п'ять станів від старту до контрольної суми")


# ── 5. (вставка proj) Серце ручного читання: біт = ширина високого імпульсу ──
def fig_pulse_width():
    W, H = 780, 430
    f = []

    base = 250
    hi = 120
    x0 = 70

    f.append(line(x0 - 10, base, W - 30, base, color=MUTED, sw=1.2))
    f.append(text(W - 34, base + 18, "час →", size=11, color=MUTED, anchor="end"))

    def pulse(xs, low_w, high_w, label, col):
        f.append(line(xs, base, xs + low_w, base, color=INK, sw=2.4))
        f.append(line(xs + low_w, base, xs + low_w, hi, color=INK, sw=2.4))
        f.append(line(xs + low_w, hi, xs + low_w + high_w, hi, color=col, sw=3))
        f.append(line(xs + low_w + high_w, hi, xs + low_w + high_w, base, color=INK, sw=2.4))
        wy = hi - 16
        f.append(line(xs + low_w, wy, xs + low_w + high_w, wy, color=col, sw=1.3, dash="4 3"))
        f.append(text(xs + low_w + high_w / 2, wy - 6, label, size=11.5, color=col, bold=True))
        return xs + low_w + high_w

    x = x0
    f.append(text(x + 42, base + 20, "50 мкс низько", size=10.5, color=MUTED))
    x = pulse(x, 84, 40, "≈26 мкс → 0", NEG)
    f.append(line(x, base, x + 26, base, color=INK, sw=2.4))
    x += 26
    f.append(text(x + 42, base + 20, "50 мкс низько", size=10.5, color=MUTED))
    x = pulse(x, 84, 110, "≈70 мкс → 1", POS)
    f.append(line(x, base, x + 26, base, color=INK, sw=2.4))

    # маркери micros() на фронтах першого (нульового) біта
    fx0 = x0 + 84
    fx1 = x0 + 84 + 40
    f.append(line(fx0, hi, fx0, hi - 40, color=NEG, sw=1.1, dash="3 3"))
    f.append(line(fx1, hi, fx1, hi - 40, color=NEG, sw=1.1, dash="3 3"))
    f.append(text(fx0 - 4, hi - 46, "t0=micros()", size=10, color=NEG, anchor="end"))
    f.append(text(fx1 + 4, hi - 46, "t1=micros()", size=10, color=NEG, anchor="start"))
    f.append(text((fx0 + fx1) / 2, hi - 66, "ширина = t1 − t0", size=11.5, color=NEG, bold=True, anchor="middle"))

    # рамка рішення
    f.append(rect(x0, 306, W - x0 - 40, 96, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=8))
    f.append(text((x0 + W - 40) / 2, 330, "Рішення за одним числом", size=13.5, color=INK, bold=True))
    f.append(mtext((x0 + W - 40) / 2, 354,
                   "фронт угору → засік micros(); фронт униз → знову micros().\n"
                   "різниця мала (< ≈50 мкс) — біт 0, велика — біт 1.\n"
                   "абсолютні числа не важать: важить, який високий імпульс довший.",
                   size=11, color=MUTED))

    render(os.path.join(IMG, "dht11-pulse-width.svg"), W, H, *f,
           title="Серце ручного драйвера: біт — це ширина високого імпульсу")


if __name__ == "__main__":
    fig_inside()
    fig_protocol()
    fig_wiring()
    fig_driver_states()
    fig_pulse_width()
    print("OK: dht11-inside.svg, dht11-protocol.svg, dht11-wiring.svg, "
          "dht11-driver-states.svg, dht11-pulse-width.svg")
