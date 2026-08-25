# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «OLED-дисплей 0.96" SSD1306 (I2C, 128x64)».
Запуск:  python figs.py   -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

OLED_ON = "#eaf2ff"   # «світиться» на склі — блакитний
OLED_OFF = "#2a2f3a"  # погашений піксель — темний


# ── 1. Що всередині: контролер SSD1306 + зарядний насос + скло ─────────────────
def fig_anatomy():
    W, H = 900, 500
    f = [text(W / 2, 30, "Усередині модуля: SSD1306 сам робить усе, що LCD вимагав ззовні",
              size=16, bold=True)]

    # Мікроконтролер ліворуч
    mcx, mcy = 92, 250
    f.append(rect(mcx - 56, mcy - 42, 112, 84, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mcx, mcy - 8, "МК", size=13, bold=True))
    f.append(text(mcx, mcy + 12, "3.3 чи 5 В", size=9.5, color=MUTED))

    # дві лінії I2C
    f.append(line(mcx + 56, mcy - 12, 250, mcy - 12, color=NEG, sw=2.2))
    f.append(text((mcx + 56 + 250) / 2, mcy - 20, "SDA", size=10, bold=True, color=NEG))
    f.append(line(mcx + 56, mcy + 12, 250, mcy + 12, color=NEG, sw=2.2))
    f.append(text((mcx + 56 + 250) / 2, mcy + 26, "SCL", size=10, bold=True, color=NEG))
    f.append(text((mcx + 56 + 250) / 2, mcy + 2, "лише дві лінії", size=9, color=MUTED, italic=True))

    # Межа модуля
    bx, by, bw, bh = 250, 66, 400, 360
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(bx + bw / 2, by + 20, "плата 0.96\" — одна мікросхема SSD1306", size=11.5, bold=True, color=MUTED))

    # Блоки всередині контролера — колонка
    innx = bx + 118
    def block(cy, tag, desc, col, fill):
        w, h = 214, 54
        f.append(rect(innx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(text(innx, cy - 8, tag, size=11.5, bold=True, color=col))
        f.append(text(innx, cy + 11, desc, size=9, color=MUTED))

    block(by + 70, "I2C-приймач", "розбирає адресу 0x3C і байти", NEG, "#eaf0fd")
    block(by + 140, "GDDRAM 128x64", "власна пам'ять-картинка", FIELD, "#eef6ef")
    block(by + 210, "зарядний насос", "з 3.3 В робить ~7-9 В на OLED", POS, "#fdecea")
    block(by + 280, "драйвер стовпців", "живить кожен піксель сам", INK, "#f1f3f5")

    # тонкі стрілки вниз між блоками
    for yy in (by + 70, by + 140, by + 210):
        f.append(arrow(innx, yy + 27, innx, yy + 43, color=MUTED, sw=1.3))

    # Скло праворуч — маленька матриця, що світиться
    gx, gy = 610, 150
    cols, rows = 12, 6
    cell = 9
    f.append(text(gx + cols * cell / 2, gy - 14, "скло OLED", size=11, bold=True))
    # темна підкладка
    f.append(rect(gx - 6, gy - 4, cols * cell + 12, rows * cell + 10, fill=OLED_OFF, stroke=INK, sw=1.4, rx=5))
    demo = [
        "011110",
        "100001",
        "101101",
        "100001",
        "011110",
        "000000",
    ]
    # намалюємо «смайлик» у лівій половині матриці, решта погашена
    for r in range(rows):
        for c in range(cols):
            on = c < 6 and demo[r][c] == "1"
            fill = OLED_ON if on else "#3a4150"
            f.append(rect(gx + c * cell, gy + r * cell, cell - 1.5, cell - 1.5,
                          fill=fill, stroke="none", sw=0))

    # стрілка від драйвера до скла
    f.append(arrow(innx + 107, by + 280, gx - 10, gy + rows * cell / 2, color=INK, sw=1.8))
    f.append(text((innx + 107 + gx) / 2 + 4, by + 268, "світить", size=9.5, color=INK, bold=True))
    f.append(text((innx + 107 + gx) / 2 + 4, by + 282, "піксель", size=9.5, color=INK, bold=True))

    b, _, _ = textbox(W / 2, H - 24,
                      "ні потенціометра контрасту, ні окремої підсвітки, ні зовнішнього перетворювача — усе в чипі",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Пам'ять як 8 сторінок: байт — це вертикальний стовпчик із 8 пікселів ─────
def fig_pages():
    W, H = 940, 540
    f = [text(W / 2, 30, "Пам'ять картинки: 8 сторінок, і байт — це стовпчик з 8 пікселів угору",
              size=15.5, bold=True)]

    # Ліворуч — увесь екран, розкреслений на 8 горизонтальних смуг-сторінок
    lx, ly = 60, 78
    scrW, scrH = 300, 300
    pageH = scrH / 8
    f.append(rect(lx, ly, scrW, scrH, fill=OLED_OFF, stroke=INK, sw=1.6, rx=6))
    for p in range(8):
        yy = ly + p * pageH
        if p > 0:
            f.append(line(lx, yy, lx + scrW, yy, color="#5a6270", sw=1.0, dash="4,4"))
        f.append(text(lx - 10, yy + pageH / 2 + 4, "PAGE %d" % p, size=10,
                      color=MUTED, anchor="end", bold=(p == 2)))
    f.append(text(lx + scrW / 2, ly - 12, "екран 128 x 64", size=11, bold=True))
    f.append(text(lx + scrW + 6, ly + scrH + 18, "кожна сторінка — смуга 8 пікселів заввишки",
                  size=9.5, color=MUTED, anchor="end"))

    # виділимо один стовпчик у PAGE 2
    colX = lx + scrW * 0.30
    p2y = ly + 2 * pageH
    f.append(rect(colX, p2y, 10, pageH, fill="#4a5160", stroke=POS, sw=1.8, rx=1))

    # Праворуч — розгортка того стовпчика: 1 байт -> 8 пікселів угору
    rx = 560
    ry = 96
    cell = 34
    f.append(text(rx + 60, ry - 22, "один байт цієї клітинки", size=11.5, bold=True, anchor="middle"))
    # байт зверху як 8 біт
    bits = [0, 0, 1, 1, 1, 1, 0, 0]  # D7..D0, малюємо як стовпчик
    # підпис розрядів
    labels = ["D0 (низ)", "D1", "D2", "D3", "D4", "D5", "D6", "D7 (верх)"]
    for i in range(8):
        yy = ry + (7 - i) * cell   # D7 угорі
        b = bits[7 - i]
        fill = OLED_ON if b else "#3a4150"
        f.append(rect(rx, yy, cell, cell - 3, fill=fill, stroke=INK, sw=1.2, rx=3))
        f.append(text(rx + cell / 2, yy + cell / 2 + 2, str(b), size=13, bold=True,
                      color=(INK if b else "#c9cdd4")))
        f.append(text(rx + cell + 12, yy + cell / 2 + 4, labels[7 - i], size=9.5,
                      color=MUTED, anchor="start"))

    # підсумковий байт як число
    f.append(text(rx + cell / 2, ry + 8 * cell + 22, "0b00111100 = 0x3C",
                  size=12, bold=True, color=POS, anchor="middle"))

    # стрілка від виділеного стовпчика до розгортки
    f.append(arrow(colX + 10, p2y + pageH / 2, rx - 14, ry + 4 * cell, color=POS, sw=1.8))
    f.append(text((colX + rx) / 2 + 20, p2y + pageH / 2 - 12, "розгорнули", size=9.5,
                  color=POS, bold=True))

    b, _, _ = textbox(W / 2, H - 24,
                      "щоб змінити один піксель, треба прочитати-змінити-записати весь його байт: тому кадр малюють у пам'яті МК, а тоді женуть цілком",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "pages.svg"), W, H, *f)


# ── 3. Розводка: 4 ніжки до ESP32 (3.3 В) і до STM32 (3.3 В) ────────────────────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 30, "Підключення: чотири ніжки, однаково до ESP32 і до STM32",
              size=16, bold=True)]

    # Модуль по центру
    mx = W / 2
    top = 78
    pinH = 46
    pins = [
        ("GND", "земля", INK),
        ("VCC", "живлення 3.3 В (терпить і 5 В)", POS),
        ("SCL", "такт I2C", NEG),
        ("SDA", "дані I2C", NEG),
    ]
    n = len(pins)
    boxW = 150
    bx0 = mx - boxW / 2
    f.append(rect(bx0, top - 12, boxW, n * pinH + 20, fill=OLED_OFF, stroke=INK, sw=1.8, rx=10))
    f.append(text(mx, top - 22, "OLED 0.96\" SSD1306", size=12, bold=True))
    f.append(text(mx, top + n * pinH + 24, "адреса 0x3C", size=10, color="#9aa2ad", italic=True))

    # ліва плата — ESP32
    ex = 150
    f.append(rect(ex - 62, top + 6, 124, n * pinH - 10, fill="#eef2f8", stroke=INK, sw=1.6, rx=10))
    f.append(text(ex, top - 8, "ESP32", size=12, bold=True))
    # права плата — STM32
    sx = W - 150
    f.append(rect(sx - 62, top + 6, 124, n * pinH - 10, fill="#eef2f8", stroke=INK, sw=1.6, rx=10))
    f.append(text(sx, top - 8, "STM32", size=12, bold=True))

    esp_dest = ["GND", "3V3", "GPIO22", "GPIO21"]
    stm_dest = ["GND", "3V3", "PB6", "PB7"]

    for i, (pin, desc, col) in enumerate(pins):
        y = top + i * pinH + pinH / 2
        # ніжка модуля (обидва боки — точки)
        f.append(text(mx, y + 4, pin, size=12, bold=True, color="#e6ecf5"))
        lpx = bx0
        rpx = bx0 + boxW
        f.append(circle(lpx, y, 3.5, fill=col, stroke=col, sw=1))
        f.append(circle(rpx, y, 3.5, fill=col, stroke=col, sw=1))
        # до ESP зліва
        f.append(line(ex + 62, y, lpx, y, color=col, sw=1.8))
        f.append(text(ex, y + 4, esp_dest[i], size=10, bold=True, color=col))
        # до STM справа
        f.append(line(rpx, y, sx - 62, y, color=col, sw=1.8))
        f.append(text(sx, y + 4, stm_dest[i], size=10, bold=True, color=col))

    b1, _, _ = textbox(W / 2, H - 58,
                       "SDA/SCL — підтяжки до 3.3 В зазвичай уже на модулі; окремих не треба",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    b2, _, _ = textbox(W / 2, H - 24,
                       "живиш від 5 В — усе одно шинні лінії тримай на 3.3 В, щоб не побити 3.3-вольтовий МК",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. (hist) До SSD1306 vs після: зовнішній DC/DC -> насос усередині чипа ──────
def fig_charge_pump_moved_in():
    W, H = 940, 470
    f = [text(W / 2, 30, "Що змінив SSD1306: підвищувач напруги переїхав із плати в чип",
              size=15.5, bold=True)]

    # спільне: OLED-склу для світіння треба ~7-9 В, а логіка дає лише 3.3 В
    def oled_glass(gx, gy, label_col):
        cols, rows, cell = 9, 5, 8
        f.append(rect(gx - 6, gy - 6, cols * cell + 12, rows * cell + 12,
                      fill=OLED_OFF, stroke=INK, sw=1.4, rx=5))
        for r in range(rows):
            for c in range(cols):
                on = (r + c) % 2 == 0
                f.append(rect(gx + c * cell, gy + r * cell, cell - 1.6, cell - 1.6,
                              fill=(OLED_ON if on else "#3a4150"), stroke="none", sw=0))
        f.append(text(gx + cols * cell / 2, gy - 12, "OLED-скло", size=9.5, bold=True))
        f.append(text(gx + cols * cell / 2, gy + rows * cell + 22,
                      "світить від ~7-9 В", size=9, color=label_col, italic=True))

    colW = 420
    # ── ЛІВА колонка: класичний драйвер до 2008 ────────────────────────────────
    Lx = 30
    f.append(rect(Lx, 58, colW, 356, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=12))
    f.append(text(Lx + colW / 2, 80, "до SSD1306 — окремий підвищувач на платі",
                  size=12, bold=True, color=MUTED))

    # МК
    f.append(rect(Lx + 26, 150, 78, 54, fill="#eef2f8", stroke=INK, sw=1.6, rx=8))
    f.append(text(Lx + 65, 172, "МК", size=12, bold=True))
    f.append(text(Lx + 65, 190, "3.3 В", size=9, color=MUTED))

    # окремий DC/DC блок з котушкою + конденсаторами
    dcx, dcy = Lx + 150, 132
    f.append(rect(dcx, dcy, 116, 92, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(dcx + 58, dcy + 20, "DC/DC", size=11.5, bold=True, color=POS))
    f.append(text(dcx + 58, dcy + 36, "перетворювач", size=9, color=POS))
    # символ котушки (дуги)
    coil = dcx + 20
    coily = dcy + 60
    arcs = "".join('<path d="M%.0f %.0f q 7 -12 14 0" fill="none" stroke="%s" stroke-width="2"/>'
                   % (coil + i * 14, coily, POS) for i in range(3))
    f.append(arcs)
    f.append(text(dcx + 58, dcy + 80, "котушка + C", size=9, color=MUTED, italic=True))
    # окремий контролер OLED
    ocx = Lx + 150
    f.append(rect(ocx, 244, 116, 46, fill="#f1f3f5", stroke=INK, sw=1.5, rx=8))
    f.append(text(ocx + 58, 266, "OLED-контролер", size=9.5, bold=True))
    f.append(text(ocx + 58, 281, "(без насоса)", size=9, color=MUTED))

    oled_glass(Lx + 320, 170, POS)

    # дроти: МК -> DC/DC (дані/живл), DC/DC -> контролер (7-9 В), контролер -> скло
    f.append(line(Lx + 104, 177, dcx, 177, color=MUTED, sw=1.7))
    f.append(arrow(dcx + 58, dcy + 92, ocx + 58, 244, color=POS, sw=1.9))
    f.append(text(dcx + 92, 236, "7-9 В", size=9, bold=True, color=POS, anchor="start"))
    f.append(line(Lx + 104, 190, ocx + 20, 244, color=MUTED, sw=1.3, dash="3,3"))
    f.append(arrow(ocx + 116, 267, Lx + 314, 190, color=INK, sw=1.7))
    f.append(text(Lx + colW / 2, 400, "три деталі, більша плата, дорожче",
                  size=10, color=POS, bold=True))

    # ── ПРАВА колонка: SSD1306 з насосом усередині ─────────────────────────────
    Rx = W - 30 - colW
    f.append(rect(Rx, 58, colW, 356, fill="#f5faf6", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(Rx + colW / 2, 80, "SSD1306 — насос усередині, зовні нічого",
                  size=12, bold=True, color=FIELD))

    f.append(rect(Rx + 26, 170, 78, 54, fill="#eef2f8", stroke=INK, sw=1.6, rx=8))
    f.append(text(Rx + 65, 192, "МК", size=12, bold=True))
    f.append(text(Rx + 65, 210, "3.3 В", size=9, color=MUTED))

    # один чип SSD1306, усередині — блок насоса
    chx, chy = Rx + 150, 132
    f.append(rect(chx, chy, 150, 130, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(chx + 75, chy + 20, "SSD1306", size=12, bold=True, color=FIELD))
    f.append(text(chx + 75, chy + 36, "один чип", size=9, color=MUTED))
    f.append(rect(chx + 20, chy + 52, 110, 40, fill="#d7ecdb", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(chx + 75, chy + 70, "зарядний насос", size=9.5, bold=True, color=FIELD))
    f.append(text(chx + 75, chy + 84, "робить 7-9 В сам", size=9, color=MUTED))
    f.append(text(chx + 75, chy + 112, "+ контролер + пам'ять", size=9, color=MUTED, italic=True))

    oled_glass(Rx + 340, 170, FIELD)

    # дроти: МК -> чип (2 лінії I2C), чип -> скло; жодного зовнішнього DC/DC
    f.append(line(Rx + 104, 190, chx, 190, color=NEG, sw=2.0))
    f.append(line(Rx + 104, 205, chx, 205, color=NEG, sw=2.0))
    f.append(text((Rx + 104 + chx) / 2, 182, "2 дроти", size=9, color=NEG, bold=True))
    f.append(arrow(chx + 150, 197, Rx + 334, 190, color=INK, sw=1.7))
    f.append(text(Rx + colW / 2, 400, "нуль зовнішніх деталей — плата з нігтик, дешево",
                  size=10, color=FIELD, bold=True))

    b, _, _ = textbox(W / 2, H - 20,
                      "той самий зарядний насос, лише переміщений із плати всередину кремнію — ось що зробило OLED-модуль крихітним і дешевим",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "charge-pump-moved-in.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_pages()
    fig_wiring()
    fig_charge_pump_moved_in()
    print("OK: 4 figures ->", IMG)
