# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що на платі — блок-схема устрою ───────────────────────────────
def fig_block():
    W, H = 820, 440
    f = []
    # межа плати
    f.append(rect(150, 70, 640, 340, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(470, 56, "Що всередині модуля", size=17, bold=True))

    # зовнішні піни (ліворуч, поза платою)
    f.append(text(60, 150, "VIN", size=14, bold=True, color=POS))
    f.append(text(45, 320, "SCL / SDA", size=13, bold=True))

    # регулятор
    b, w, h = textbox(280, 150, "Регулятор 3.3 В\n(LDO)", size=13, bold=True,
                      fill="#eafaf1", stroke=FIELD, min_w=170)
    f.append(b)
    # рівнезсувачі
    b, w, h = textbox(280, 320, "Зсувачі рівня\nSCL / SDA", size=13, bold=True,
                      fill="#eafaf1", stroke=FIELD, min_w=170)
    f.append(b)

    # LSM6DS33
    b, w, h = textbox(610, 150, "LSM6DS33\nакселерометр + гіроскоп\nадреса 0x6B", size=13, bold=True,
                      fill="#eef2ff", stroke=NEG, min_w=280)
    f.append(b)
    # LIS3MDL
    b, w, h = textbox(610, 320, "LIS3MDL\nмагнетометр\nадреса 0x1E", size=13, bold=True,
                      fill="#eef2ff", stroke=NEG, min_w=280)
    f.append(b)

    # живлення (зелене): VIN → регулятор → 3.3 В на обидві мікросхеми
    f.append(arrow(78, 150, 194, 150, color=POS))
    f.append(arrow(366, 150, 470, 150, color=FIELD))   # до LSM6DS33
    f.append(line(410, 150, 410, 300, color=FIELD, sw=2))
    f.append(arrow(410, 300, 470, 300, color=FIELD))   # до LIS3MDL (верхній край рамки)
    f.append(text(398, 232, "3.3 В", size=12, color=FIELD, anchor="middle"))

    # I2C (темне): піни → зсувачі → внутрішня шина → обидві мікросхеми
    f.append(arrow(110, 320, 194, 320))
    f.append(arrow(366, 320, 470, 320))                # до LIS3MDL (нижче центру)
    f.append(line(390, 320, 390, 168, sw=2))
    f.append(arrow(390, 168, 470, 168))                # до LSM6DS33 (нижче центру)
    f.append(text(470, 372, "внутрішня шина I²C 3.3 В", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'block.svg'), W, H, *f)


# ── Фігура 2: розводка пін-у-пін до мікроконтролера ─────────────────────────
def fig_wiring():
    W, H = 780, 430
    f = []
    f.append(text(W/2, 34, "Підключення до мікроконтролера (I²C)", size=17, bold=True))

    # модуль (ліворуч) — 6 пінів
    mx, my, mw, mh = 70, 70, 190, 300
    f.append(rect(mx, my, mw, mh, fill="#eef2ff", stroke=NEG, sw=1.8, rx=10))
    f.append(text(mx+mw/2, my+26, "MinIMU-9", size=14, bold=True))
    pins = ["VIN", "VDD", "GND", "SCL", "SDA", "SA0"]
    py0 = my+64
    step = 40
    pin_y = {}
    for i, p in enumerate(pins):
        y = py0 + i*step
        pin_y[p] = y
        f.append(circle(mx+mw-14, y, 6, fill=BG, stroke=INK, sw=1.5))
        f.append(text(mx+mw-30, y+4, p, size=13, bold=True, anchor="end"))

    # МК (праворуч)
    cx, cy, cw, ch = 540, 90, 180, 260
    f.append(rect(cx, cy, cw, ch, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(cx+cw/2, cy+26, "МК", size=14, bold=True))
    f.append(text(cx+cw/2, cy+44, "(напр. 3.3 В)", size=11, color=MUTED))
    mcu = ["3V3", "GND", "SCL", "SDA"]
    cy0 = cy+70
    cstep = 44
    mcu_y = {}
    for i, p in enumerate(mcu):
        y = cy0 + i*cstep
        mcu_y[p] = y
        f.append(circle(cx+14, y, 6, fill=BG, stroke=INK, sw=1.5))
        f.append(text(cx+30, y+4, p, size=13, bold=True, anchor="start"))

    def link(p_mod, p_mcu, color, label=None):
        x1 = mx+mw-8; y1 = pin_y[p_mod]
        x2 = cx+8; y2 = mcu_y[p_mcu]
        xm = (x1+x2)/2
        f.append(line(x1, y1, xm, y1, color=color, sw=2))
        f.append(line(xm, y1, xm, y2, color=color, sw=2))
        f.append(arrow(xm, y2, x2, y2, color=color))
        if label:
            f.append(text(xm, (y1+y2)/2, label, size=11, color=color, anchor="middle"))

    link("VIN", "3V3", POS)
    link("GND", "GND", INK)
    link("SCL", "SCL", NEG)
    link("SDA", "SDA", NEG)

    # підтяжки I2C
    f.append(text(W/2, H-64, "Живимо VIN — регулятор дає 3.3 В на мікросхеми; VDD лишаємо вільним.",
                  size=12, color=MUTED))
    f.append(text(W/2, H-44, "Підтяжки SCL/SDA до 3.3 В (часто вже є на шині/платі МК); SA0 не чіпаємо — адреси за замовчуванням.",
                  size=12, color=MUTED))
    f.append(text(W/2, H-24, "SA0 → GND робить другу пару адрес (два модулі на одній шині).",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── Фігура 3: сирі 16 біт → фізичні одиниці ─────────────────────────────────
def fig_pipeline():
    W, H = 780, 250
    f = []
    f.append(text(W/2, 34, "Від регістрів до фізичних одиниць", size=17, bold=True))

    y = 130
    b, w, h = textbox(120, y, "два байти\nOUTX_L + OUTX_H", size=13, bold=True, min_w=180)
    f.append(b)
    b, w, h = textbox(370, y, "16-бітне\nчисло зі знаком\n(−32768…32767)", size=13, bold=True, min_w=190)
    f.append(b)
    b, w, h = textbox(650, y, "× чутливість\n= g, °/с, гаус", size=13, bold=True, min_w=200,
                      fill="#eafaf1", stroke=FIELD)
    f.append(b)

    f.append(arrow(212, y, 274, y))
    f.append(arrow(466, y, 549, y))

    f.append(text(243, y-14, "склеїти", size=11, color=MUTED))
    f.append(text(508, y-14, "×", size=11, color=MUTED))

    f.append(text(W/2, 210, "Напр. акселерометр на ±2 g: 1 LSB = 0.061 мг, тож 16384 → 16384 × 0.000061 ≈ 1.00 g.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'pipeline.svg'), W, H, *f)


# ── Фігура 4 (для proj-вставки): API-потік read() → члени → фізика ───────────
def fig_api_flow():
    W, H = 860, 440
    f = []
    f.append(text(W/2, 34, "Від виклику read() до фізичних одиниць", size=17, bold=True))

    # крок 1: read() зчитує обидва чипи
    b, w, h = textbox(150, 130, "imu.read()\nmag.read()", size=14, bold=True,
                      fill="#eef2ff", stroke=NEG, min_w=200)
    f.append(b)
    f.append(text(150, 190, "звертання по I²C", size=11, color=MUTED))

    # крок 2: сирі int16_t у членах-векторах
    b, w, h = textbox(430, 130, "члени-вектори (int16_t)\na.x a.y a.z\ng.x g.y g.z\nm.x m.y m.z",
                      size=13, bold=True, fill="#fbfcfd", stroke=MUTED, min_w=240)
    f.append(b)
    f.append(text(430, 210, "сирі відліки (LSB), зі знаком", size=11, color=MUTED))

    # крок 3: × чутливість = фізика
    b, w, h = textbox(720, 130, "× чутливість шкали\n= g, °/с, гаус",
                      size=13, bold=True, fill="#eafaf1", stroke=FIELD, min_w=210)
    f.append(b)

    # стрілки між кроками (ведемо по верхньому рівні, повз написи знизу)
    f.append(arrow(252, 130, 306, 130, color=INK))
    f.append(arrow(552, 130, 612, 130, color=INK))
    f.append(text(279, 116, "чит.", size=11, color=MUTED))
    f.append(text(582, 116, "×", size=13, color=MUTED))

    # нижній блок: конкретні множники для налаштувань enableDefault() за замовчуванням
    f.append(line(90, 280, W-90, 280, color=MUTED, sw=1))
    f.append(text(W/2, 306, "Чутливості для enableDefault() (шкали за замовчуванням):",
                  size=13, bold=True))

    b, w, h = textbox(220, 366, "акселерометр ±2 g\n× 0.000061  → g", size=12,
                      fill="#fbfcfd", stroke=FIELD, min_w=230)
    f.append(b)
    b, w, h = textbox(490, 366, "гіроскоп ±245 °/с\n× 0.00875  → °/с", size=12,
                      fill="#fbfcfd", stroke=FIELD, min_w=230)
    f.append(b)
    b, w, h = textbox(730, 366, "магнетометр ±4 Gs\n÷ 6842  → гаус", size=12,
                      fill="#fbfcfd", stroke=POS, min_w=200)
    f.append(b)

    render(os.path.join(IMG, 'api-flow.svg'), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_wiring()
    fig_pipeline()
    fig_api_flow()
    print("ok")
