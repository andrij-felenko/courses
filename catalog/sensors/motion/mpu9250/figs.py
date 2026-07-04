# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що на платі GY-91 — три чипи, дві шини, регулятор ──────────────
def fig_inside():
    W, H = 820, 470
    f = []
    f.append(text(W/2, 30, "Що на платі GY-91: три давачі, один регулятор, дві шини", size=17, bold=True))

    # Плата-рамка
    f.append(rect(40, 60, W-80, H-160, fill="#eef7f0", stroke=FIELD, sw=2, rx=12))
    f.append(text(60, 84, "GY-91 (плата-брейкаут)", size=13, color=FIELD, bold=True, anchor="start"))

    # MPU-9250 (велика — MCM із двох кристалів)
    mx, my, mw, mh = 90, 110, 300, 200
    f.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=8))
    f.append(text(mx+mw/2, my+24, "MPU-9250 (MCM)", size=14, bold=True))
    # кристал 1
    b1, w1, h1 = fitbox(mx+18, my+42, mw-36, 66,
                        "Кристал 1:\nгіроскоп 3 осі  +  акселерометр 3 осі",
                        size=12, fill="#fdf3ec", stroke=POS, sw=1.5), 0, 0
    f.append(b1)
    # кристал 2
    f.append(fitbox(mx+18, my+118, mw-36, 66,
                    "Кристал 2 — AK8963 (Asahi Kasei):\nмагнетометр 3 осі",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=1.5))

    # BMP280 (окремий чип)
    bx, by, bw, bh = 470, 110, 260, 92
    f.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=8))
    f.append(text(bx+bw/2, by+26, "BMP280 (Bosch)", size=14, bold=True))
    f.append(fitbox(bx+16, by+40, bw-32, 40, "барометр (тиск)  +  термометр",
                    size=12, fill="#eef7f0", stroke=FIELD, sw=1.3))

    # Регулятор 3.3 В
    rx0, ry0, rw0, rh0 = 470, 226, 260, 74
    f.append(rect(rx0, ry0, rw0, rh0, fill="#fff7e6", stroke="#c98a00", sw=1.6, rx=8))
    f.append(text(rx0+rw0/2, ry0+26, "LDO 3.3 В", size=13, bold=True, color="#8a5d00"))
    f.append(fitbox(rx0+16, ry0+36, rw0-32, 30, "живить усі три давачі від VIN 3–5 В",
                    size=11, fill=BG, stroke="#c98a00", sw=1.0))

    # Внутрішня шина I²C між MPU і AK8963 (пунктир)
    f.append(line(mx+mw/2, my+mh, mx+mw/2, my+mh+18, color=MUTED, sw=1.4, dash="4 3"))

    # Виводи назовні: VIN + 3V3 + I2C/SPI
    yb = H-70
    f.append(line(40, H-90, W-40, H-90, color=MUTED, sw=1.0, dash="2 4"))
    f.append(text(60, yb-2, "Назовні (гребінка контактів):", size=12, color=MUTED, bold=True, anchor="start"))
    f.append(fitbox(300, yb-20, 150, 34, "VIN  3–5 В", size=12, fill="#fff7e6", stroke="#c98a00", sw=1.2))
    f.append(fitbox(462, yb-20, 130, 34, "SCL · SDA", size=12, fill="#f4f6f8", stroke=LINE, sw=1.2))
    f.append(fitbox(604, yb-20, 176, 34, "SDO · NCS · CSB (SPI)", size=12, fill="#f4f6f8", stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'inside.svg'), W, H, *f)


# ── Фігура 2: розводка пін-у-пін GY-91 ↔ МК (I²C) ───────────────────────────
def fig_wiring():
    W, H = 780, 470
    f = []
    f.append(text(W/2, 30, "Розводка GY-91 ↔ мікроконтролер по I²C (5 дротів)", size=17, bold=True))

    # МК зліва
    mcx, mcy, mcw, mch = 60, 90, 210, 300
    f.append(rect(mcx, mcy, mcw, mch, fill="#eef7f0", stroke=FIELD, sw=2, rx=10))
    f.append(text(mcx+mcw/2, mcy+28, "Мікроконтролер", size=14, bold=True))
    f.append(text(mcx+mcw/2, mcy+48, "(3.3 В логіка)", size=11, color=MUTED))

    # GY-91 справа
    gx, gy, gw, gh = 510, 90, 210, 300
    f.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2, rx=10))
    f.append(text(gx+gw/2, gy+28, "GY-91", size=14, bold=True))

    rows = [
        ("3V3",  "VIN",  "живлення 3.3 В", FIELD),
        ("GND",  "GND",  "спільна земля", INK),
        ("SCL",  "SCL",  "такт I²C (+ підтяжка 4.7 кΩ)", NEG),
        ("SDA",  "SDA",  "дані I²C (+ підтяжка 4.7 кΩ)", NEG),
        ("GND",  "SDO",  "адреса MPU = 0x68 (SDO до GND)", MUTED),
    ]
    y0 = mcy + 74
    dy = 42
    for i, (lp, rp, note, col) in enumerate(rows):
        yy = y0 + i*dy
        # контакт на МК
        f.append(fitbox(mcx+18, yy-15, 90, 30, lp, size=12, fill=BG, stroke=col, sw=1.4))
        # контакт на GY-91
        f.append(fitbox(gx+gw-108, yy-15, 90, 30, rp, size=12, fill=BG, stroke=col, sw=1.4))
        # дріт
        f.append(line(mcx+108, yy, gx+gw-108, yy, color=col, sw=2.0))
        # підпис по центру над дротом
        f.append(text((mcx+108+gx+gw-108)/2, yy-9, note, size=10.5, color=MUTED))

    # Примітка про CSB/NCS
    f.append(fitbox(mcx, mcy+mch+16, W-2*mcx, 40,
                    "NCS і CSB лишаємо непідключеними (або на VIN) — на високому рівні обидва чипи в режимі I²C.",
                    size=11.5, fill="#fff7e6", stroke="#c98a00", sw=1.2))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── Фігура 3: два шляхи до магнетометра AK8963 (bypass vs slave) ─────────────
def fig_mag_paths():
    W, H = 900, 560
    f = []
    f.append(text(W/2, 30, "Два шляхи до магнетометра AK8963", size=17, bold=True))

    # ── Ліва панель: BYPASS ─────────────────────────────────────────────
    f.append(text(230, 66, "Шлях 1 — bypass (наскрізний прохід)", size=13, bold=True, color=NEG))

    # МК
    f.append(fitbox(60, 90, 150, 56, "Мікроконтролер",
                    size=12, fill="#eef7f0", stroke=FIELD, sw=1.8))
    # Корпус MPU (з внутрішнім майстром — вимкненим)
    f.append(rect(60, 180, 340, 220, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=8))
    f.append(text(230, 204, "Корпус MPU-9250", size=12, bold=True))
    # внутрішній майстер — вимкнений
    f.append(fitbox(80, 220, 150, 56, "внутр. I²C-майстер\n(ВИМКНЕНО)",
                    size=10.5, fill="#f0f0f0", stroke=MUTED, sw=1.3))
    # AK8963
    f.append(fitbox(250, 300, 130, 68, "AK8963\nмагнетометр\n0x0C",
                    size=11, fill="#eaf0fd", stroke=NEG, sw=1.5))
    # акс+гіро
    f.append(fitbox(80, 300, 150, 56, "акселерометр\n+ гіроскоп",
                    size=10.5, fill="#fdf3ec", stroke=POS, sw=1.3))

    # Наскрізна лінія: МК → повз майстер → прямо на AK8963 (0x0C)
    f.append(line(135, 146, 135, 180, color=NEG, sw=2.2))          # МК вниз у корпус
    f.append(line(135, 292, 315, 292, color=NEG, sw=2.2, dash="6 4"))  # прохід управо
    f.append(line(315, 292, 315, 300, color=NEG, sw=2.2, dash="6 4"))  # вниз в AK
    f.append(text(225, 285, "прямий доступ на 0x0C", size=10, color=NEG))

    # Підсумок лівої панелі
    f.append(fitbox(60, 414, 340, 54,
                    "Магнетометр читається ОКРЕМО, своїм викликом.\nПросто, але осі не синхронні з акс/гіро.",
                    size=10.5, fill="#eaf0fd", stroke=NEG, sw=1.2))

    # ── Роздільник ──────────────────────────────────────────────────────
    f.append(line(W/2, 60, W/2, H-40, color=MUTED, sw=1.0, dash="3 5"))

    # ── Права панель: SLAVE ─────────────────────────────────────────────
    f.append(text(680, 66, "Шлях 2 — slave (внутр. I²C-майстер)", size=13, bold=True, color=POS))

    # МК
    f.append(fitbox(510, 90, 150, 56, "Мікроконтролер",
                    size=12, fill="#eef7f0", stroke=FIELD, sw=1.8))
    # Корпус MPU (майстер увімкнено)
    f.append(rect(510, 180, 340, 220, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=8))
    f.append(text(680, 204, "Корпус MPU-9250", size=12, bold=True))
    # внутрішній майстер — увімкнений
    f.append(fitbox(530, 220, 150, 56, "внутр. I²C-майстер\n(УВІМКНЕНО)",
                    size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.4))
    # EXT_SENS_DATA
    f.append(fitbox(700, 220, 130, 56, "EXT_SENS_DATA\n(поле складено)",
                    size=10, fill="#fff7e6", stroke="#c98a00", sw=1.3))
    # AK8963
    f.append(fitbox(700, 300, 130, 68, "AK8963\nмагнетометр\n0x0C",
                    size=11, fill="#eaf0fd", stroke=NEG, sw=1.5))
    # акс+гіро
    f.append(fitbox(530, 300, 150, 56, "акселерометр\n+ гіроскоп",
                    size=10.5, fill="#fdf3ec", stroke=POS, sw=1.3))

    # Внутрішній майстер сам опитує AK і складає в EXT_SENS_DATA
    f.append(arrow(660, 300, 620, 276, color=INK, sw=1.6))         # AK → майстер (унизу зліва)
    f.append(arrow(765, 300, 765, 278, color=INK, sw=1.6))         # AK → EXT (вгору)
    # МК одним читанням забирає все з регістрів MPU
    f.append(arrow(585, 180, 585, 148, color=POS, sw=2.2))         # МК ← корпус (усе)
    f.append(text(680, 168, "усі 9 осей одним читанням", size=10, color=POS))

    # Підсумок правої панелі
    f.append(fitbox(510, 414, 340, 54,
                    "MPU сам опитує AK і складає поле в свої регістри.\nСкладніше, але всі 9 осей СИНХРОННІ.",
                    size=10.5, fill="#fdf3ec", stroke=POS, sw=1.2))

    render(os.path.join(IMG, 'mag-paths.svg'), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_mag_paths()
    print("figs done")
