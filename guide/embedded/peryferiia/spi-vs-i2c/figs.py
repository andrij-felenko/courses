# -*- coding: utf-8 -*-
"""Фігури до теми «SPI проти I2C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Семантика кольорів у цій темі: I2C — тепле золото (економія), SPI — зелене поле (швидкість).
I2C = "#b9770e"
SPI = FIELD
UART = NEG


# ── 1. По кожному критерію: таблиця ──────────────────────────────────────────
def fig_compare_table():
    W, H = 760, 432
    f = [text(W / 2, 26, "SPI проти I2C: по кожному критерію", size=16, bold=True)]
    f.append(text(W / 2, 46, "зелене — де ця шина сильніша; вибір — за тим, що для проєкту важить",
                  size=11, color=MUTED, italic=True))

    cx_i2c, cx_spi = 470, 648
    win = "#eef6ef"   # підсвітка переможця в рядку

    # шапка
    f.append(rect(24, 64, 712, 30, fill="#f0f0f0", stroke=MUTED, sw=1.2))
    f.append(text(40, 84, "критерій", size=12, anchor="start", bold=True))
    f.append(text(cx_i2c, 84, "I2C", size=12.5, color=I2C, bold=True))
    f.append(text(cx_spi, 84, "SPI", size=12.5, color=SPI, bold=True))

    rows = [
        ("ніжки на N пристроїв", "2 на всіх", "i", "3 + N", ""),
        ("швидкість такту",      "≤ 3.4 МГц", "",  "десятки МГц", "s"),
        ("дуплекс",              "напівдуплекс", "", "повний", "s"),
        ("додати пристрій",      "дати адресу", "i", "ще лінія CS", ""),
        ("контроль кожного байта", "є ACK", "i", "немає", ""),
        ("службові біти",        "адреса + ACK", "", "майже нуль", "s"),
        ("кілька ведучих",       "так, з арбітражем", "i", "зазвичай ні", ""),
        ("лінії на платі",       "відкритий стік + підтяжки", "", "штовхай-тягни", "s"),
        ("відстань",             "сантиметри", "", "сантиметри", ""),
    ]

    y = 94
    rh = 34
    for label, a, awin, b, bwin in rows:
        f.append(rect(24, y, 712, rh, fill=BG, stroke="#dddddd", sw=1))
        f.append(text(40, y + 22, label, size=11.5, anchor="start"))
        if awin:
            f.append(rect(366, y + 3, 200, rh - 6, fill=win, stroke="none", sw=0, rx=4))
        if bwin:
            f.append(rect(560, y + 3, 168, rh - 6, fill=win, stroke="none", sw=0, rx=4))
        f.append(text(cx_i2c, y + 22, a, size=11,
                      color=I2C if awin else INK, bold=bool(awin)))
        f.append(text(cx_spi, y + 22, b, size=11,
                      color=SPI if bwin else INK, bold=bool(bwin)))
        y += rh
    render(os.path.join(IMG, "compare-table.svg"), W, H, *f)


# ── 2. Коротке дерево рішень ─────────────────────────────────────────────────
def fig_decision_tree():
    W, H = 760, 366
    f = [text(W / 2, 26, "Як обрати: три питання", size=16, bold=True)]

    # Q1 швидкість
    f.append(rect(280, 52, 200, 52, fill=FILL, stroke=INK, sw=2))
    f.append(text(380, 74, "потрібен великий", size=12, bold=True))
    f.append(text(380, 91, "потік / висока швидкість?", size=12, bold=True))

    # → так: SPI
    f.append(arrow(480, 78, 600, 78, color=SPI, sw=1.8))
    f.append(text(540, 70, "так", size=10, color=MUTED, italic=True))
    f.append(rect(600, 58, 130, 40, fill=BG, stroke=SPI, sw=1.8))
    f.append(text(665, 83, "SPI", size=14, color=SPI, bold=True))

    # ↓ ні: Q2
    f.append(arrow(380, 104, 380, 144, color=INK, sw=1.8))
    f.append(text(396, 128, "ні", size=10, color=MUTED, anchor="start", italic=True))

    f.append(rect(280, 144, 200, 52, fill=FILL, stroke=INK, sw=2))
    f.append(text(380, 166, "багато дрібних пристроїв,", size=11.5, bold=True))
    f.append(text(380, 183, "мало вільних ніжок?", size=11.5, bold=True))

    # → так: I2C
    f.append(arrow(480, 170, 600, 170, color=I2C, sw=1.8))
    f.append(text(540, 162, "так", size=10, color=MUTED, italic=True))
    f.append(rect(600, 150, 130, 40, fill=BG, stroke=I2C, sw=1.8))
    f.append(text(665, 175, "I2C", size=14, color=I2C, bold=True))

    # ↓ ні: Q3 тонкі випадки
    f.append(arrow(380, 196, 380, 236, color=INK, sw=1.8))
    f.append(text(396, 220, "ні", size=10, color=MUTED, anchor="start", italic=True))

    f.append(rect(250, 236, 260, 50, fill=FILL, stroke=INK, sw=2))
    f.append(text(380, 258, "тонкий випадок:", size=11.5, bold=True))
    f.append(text(380, 275, "що важливіше?", size=11.5, bold=True))

    f.append(arrow(380, 286, 250, 322, color=SPI, sw=1.6))
    f.append(rect(120, 322, 130, 34, fill=BG, stroke=SPI, sw=1.6))
    f.append(text(185, 343, "дуплекс → SPI", size=10.5, color=SPI, bold=True))

    f.append(arrow(380, 286, 540, 322, color=I2C, sw=1.6))
    f.append(rect(510, 322, 170, 34, fill=BG, stroke=I2C, sw=1.6))
    f.append(text(595, 343, "ACK-контроль → I2C", size=10.5, color=I2C, bold=True))

    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 3. Типові пристрої на кожній шині ────────────────────────────────────────
def fig_typical_devices():
    W, H = 760, 270
    f = [text(W / 2, 26, "Що зазвичай вішають на кожну шину", size=16, bold=True)]

    def column(x, title, col, items, note):
        f.append(rect(x, 50, 340, 180, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 170, 74, title, size=14, color=col, bold=True))
        f.append(line(x + 20, 86, x + 320, 86, color=col, sw=1.2))
        yy = 110
        for it in items:
            f.append(text(x + 30, yy, "•", size=12, color=col, anchor="start", bold=True))
            f.append(text(x + 46, yy, it, size=11.5, anchor="start"))
            yy += 24
        f.append(text(x + 170, 220, note, size=10, color=MUTED, italic=True))

    column(24, "I2C — дрібне й повільне", I2C,
           ["давачі: IMU, барометр, світло", "годинник реального часу (RTC)",
            "невелика EEPROM", "малий монохромний OLED"],
           "важить економія ніжок, швидкість другорядна")
    column(396, "SPI — швидке й об'ємне", SPI,
           ["кольоровий TFT-дисплей", "SD-картка", "флеш-пам'ять",
            "швидкий АЦП, деякі радіомодулі"],
           "потрібен великий потік на сантиметрах плати")

    f.append(text(W / 2, 256,
                  "не закон, а звичай: повільне й дрібне тяжіє до I2C, швидке й об'ємне — до SPI",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "typical-devices.svg"), W, H, *f)


# ── 4. Обидві шини на одній платі ────────────────────────────────────────────
def fig_both_buses():
    W, H = 760, 300
    f = [text(W / 2, 26, "Типова плата: обидві шини разом", size=16, bold=True)]

    # MCU у центрі
    mx, my, mw, mh = 320, 120, 120, 64
    f.append(rect(mx, my, mw, mh, fill=FILL, stroke=INK, sw=2))
    f.append(text(mx + mw / 2, my + 30, "MCU", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 48, "обидва блоки", size=9.5, color=MUTED, italic=True))

    # I2C шина ліворуч (дві лінії)
    f.append(text(150, 70, "I2C — 2 дроти", size=12, color=I2C, bold=True))
    for dy in (96, 108):
        f.append(line(60, dy, mx, dy, color=I2C, sw=2))
    devs_i2c = ["IMU", "баро", "RTC"]
    dx = 60
    for d in devs_i2c:
        f.append(rect(dx, 130, 70, 34, fill=BG, stroke=I2C, sw=1.5))
        f.append(text(dx + 35, 152, d, size=11, color=I2C, bold=True))
        f.append(line(dx + 35, 130, dx + 35, 108, color=I2C, sw=1.3))
        dx += 80
    f.append(text(155, 200, "повільні давачі — дві ніжки на всіх", size=9.5, color=MUTED, italic=True))

    # SPI шина праворуч (спільні + CS)
    f.append(text(610, 70, "SPI — спільні + CS", size=12, color=SPI, bold=True))
    for dy in (96, 104, 112):
        f.append(line(mx + mw, dy, 700, dy, color=SPI, sw=2))
    devs_spi = ["TFT", "SD"]
    dx = 560
    for i, d in enumerate(devs_spi):
        f.append(rect(dx, 150, 90, 36, fill=BG, stroke=SPI, sw=1.5))
        f.append(text(dx + 45, 173, d, size=11.5, color=SPI, bold=True))
        f.append(line(dx + 45, 150, dx + 45, 112, color=SPI, sw=1.3))
        # окрема лінія CS
        f.append(line(mx + mw, 150 + i * 0, dx, 200, color=SPI, sw=1, dash="4 3"))
        dx += 110
    f.append(text(615, 210, "швидкі пристрої — кожен зі своїм CS", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 250, "один мікроконтролер тримає обидві шини —", size=11, bold=True))
    f.append(text(W / 2, 270, "кожна робить те, у чому сильна; правильне питання — «яку шину для кожного пристрою»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "both-buses.svg"), W, H, *f)


# ── 5. Три дротові шини поряд ─────────────────────────────────────────────────
def fig_three_buses():
    W, H = 760, 280
    f = [text(W / 2, 26, "Три дротові шини плати: не конкуренти, а інструменти", size=15, bold=True)]

    def card(x, name, col, line1, line2, when):
        f.append(rect(x, 52, 224, 168, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 112, 78, name, size=15, color=col, bold=True))
        f.append(line(x + 20, 90, x + 204, 90, color=col, sw=1.2))
        f.append(text(x + 112, 116, line1, size=11, anchor="middle"))
        f.append(text(x + 112, 136, line2, size=11, anchor="middle"))
        f.append(line(x + 20, 156, x + 204, 156, color="#dddddd", sw=1))
        f.append(fitbox(x + 14, 168, 196, 40, when, size=10.5, color=MUTED, italic=True,
                        fill=FILL, stroke="none", sw=0))

    card(24, "UART", UART, "точка-точка, асинхронно", "два пристрої потоком",
         "з модулем, ПК, GPS, радіомодемом")
    card(268, "I2C", I2C, "два дроти, адреси", "багато дрібних пристроїв",
         "грона давачів на мінімумі дротів")
    card(512, "SPI", SPI, "окремі лінії + CS", "кілька швидких пристроїв",
         "великий потік на платі")

    f.append(text(W / 2, 256,
                  "разом покривають увесь дротовий зв'язок — обираєш доречну під кожен зв'язок, не «єдино правильну»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "three-buses.svg"), W, H, *f)


# ── 6. Бюджет ніжок на прикладі ──────────────────────────────────────────────
def fig_pin_budget():
    W, H = 760, 300
    f = [text(W / 2, 26, "Бюджет ніжок: п'ять пристроїв, три розклади", size=16, bold=True)]
    f.append(text(W / 2, 46, "3 давачі (IMU, баро, магнітометр) + TFT-дисплей + SD-картка",
                  size=11, color=MUTED, italic=True))

    def bar(y, label, n, col, note, nmax=8):
        f.append(text(30, y + 18, label, size=12, anchor="start", bold=True))
        x0 = 250
        full = 360
        w = full * n / nmax
        f.append(rect(x0, y, full, 26, fill="#f2f2f2", stroke="#dddddd", sw=1))
        f.append(rect(x0, y, w, 26, fill=col, stroke="none", sw=0))
        f.append(text(x0 + w + 10, y + 18, "%d ніжок" % n, size=12, color=col, anchor="start", bold=True))
        f.append(text(30, y + 38, note, size=9.5, color=MUTED, anchor="start", italic=True))

    bar(86,  "усе на SPI", 8, SPI, "3 спільні + 5 CS — найбільше ніжок")
    bar(150, "усе на I2C", 2, I2C, "дешево, але дисплей і картка по I2C повільні/незручні")
    bar(214, "розумно: давачі I2C, дисплей+SD SPI", 7, "#2c7a4b",
        "I2C: 2 ніжки на 3 давачі  ·  SPI: 3 спільні + 2 CS")

    f.append(text(W / 2, 286,
                  "виграє розподіл: кожен пристрій на «своїй» шині, а не «або-або»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "pin-budget.svg"), W, H, *f)


# ── 7. Підсумкові «за замовчуванням» ─────────────────────────────────────────
def fig_defaults():
    W, H = 760, 270
    f = [text(W / 2, 26, "Замовчування під типову задачу", size=16, bold=True)]

    rows = [
        ("дрібний давач, мало ніжок", "I2C", I2C),
        ("швидкий дисплей / SD / флеш", "SPI", SPI),
        ("зв'язок із модулем, ПК, GPS, радіо", "UART", UART),
        ("і давачі, і дисплей на платі", "I2C + SPI разом", INK),
        ("метри або кабель із завадами", "ні те, ні те → диференційна шина", POS),
    ]
    y = 58
    for label, ans, col in rows:
        f.append(rect(24, y, 712, 36, fill=FILL, stroke="#e0e0e0", sw=1.2))
        f.append(text(44, y + 23, label, size=12, anchor="start"))
        f.append(arrow(360, y + 18, 392, y + 18, color=col, sw=1.6))
        f.append(text(404, y + 23, ans, size=12.5, color=col, anchor="start", bold=True))
        y += 42

    f.append(text(W / 2, 262,
                  "правила покривають майже все; головне вміння — зважити критерії, а не завчити рядок",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "defaults.svg"), W, H, *f)


if __name__ == "__main__":
    fig_compare_table()
    fig_decision_tree()
    fig_typical_devices()
    fig_both_buses()
    fig_three_buses()
    fig_pin_budget()
    fig_defaults()
    print("OK: 7 figures ->", IMG)
