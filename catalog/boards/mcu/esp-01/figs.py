# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «ESP-01 (Wi-Fi, ESP8266)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розпіновка: гребінка 2×4, групи виводів ────────────────────────────────
def fig_pinout():
    W, H = 820, 510
    f = [text(W / 2, 30, "ESP-01: вісім виводів двома рядами", size=17, bold=True)]

    # межа плати
    bx, by, bw, bh = 250, 70, 320, 250
    f.append(rect(bx, by, bw, bh, fill="#eaf2fb", stroke="#2457d6", sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 26, "ESP-01 (вид згори)", size=12, bold=True, color=MUTED))

    # чип + флеш + антена (схематично) у центрі плати
    f.append(rect(bx + bw / 2 - 40, by + 55, 80, 62, fill="#3a3a3a", stroke=INK, sw=1.4, rx=6))
    f.append(text(bx + bw / 2, by + 82, "ESP8266", size=10.5, bold=True, color="#ffffff"))
    f.append(text(bx + bw / 2, by + 100, "чип", size=9, color="#d0d0d0"))
    f.append(rect(bx + 30, by + 60, 40, 44, fill="#555", stroke=INK, sw=1.2, rx=4))
    f.append(text(bx + 50, by + 86, "флеш", size=9, color="#ffffff"))
    # антена-змійка натяком угорі-праворуч
    ax = bx + bw - 46
    f.append(text(ax, by + 78, "))) антена", size=9, color=MUTED))

    # два ряди по 4 контакти, ліворуч від плати їх підписуємо назовні
    # координати гнізд (2 ряди × 4)
    padY_top = by + bh - 70
    padY_bot = by + bh - 34
    xs = [bx + 46 + i * 76 for i in range(4)]

    top = [("GND", "GND", MUTED, "земля"),
           ("GPIO2", "I/O", NEG, "вивід (high@boot)"),
           ("GPIO0", "boot", NEG, "вивід / режим"),
           ("RX", "UART", "#555", "прийом")]
    bot = [("TX", "UART", "#555", "передача"),
           ("CH_PD", "EN", POS, "увімкнути чип"),
           ("RST", "rst", NEG, "скидання"),
           ("VCC", "3.3В", POS, "живлення")]

    def pad(cx, cy, name, col):
        f.append(circle(cx, cy, 9, fill="#ffffff", stroke=col, sw=2.2))
        f.append(text(cx, cy + 3.5, "○", size=9, color=col))

    for i, (name, tag, col, desc) in enumerate(top):
        pad(xs[i], padY_top, name, col)
    for i, (name, tag, col, desc) in enumerate(bot):
        pad(xs[i], padY_bot, name, col)

    # виносні підписи назовні (під платою), по два стовпці, щоб не накладались
    # верхній ряд -> підписуємо ліворуч, нижній -> праворуч, з лініями-виносками
    labY0 = by + bh + 36
    colL = 40
    colR = W - 40 - 230

    def leg(x, y, name, col, desc):
        b = fitbox(x, y, 230, 30, "%s — %s" % (name, desc), size=10.5,
                   fill=FILL, stroke=col, sw=1.6, bold=False)
        f.append(b)

    # ліва колонка — верхній ряд
    for i, (name, tag, col, desc) in enumerate(top):
        leg(colL, labY0 + i * 36, name, col, desc)
    # права колонка — нижній ряд
    for i, (name, tag, col, desc) in enumerate(bot):
        leg(colR, labY0 + i * 36, name, col, desc)

    render(os.path.join(IMG, "pinout.svg"), W, H, *f)


# ── 2. Режими завантаження: рівні ніжок при скиданні ──────────────────────────
def fig_boot_mode():
    W, H = 800, 430
    f = [text(W / 2, 30, "Рівні ніжок при скиданні обирають режим", size=17, bold=True)]

    cw = 330
    lx, rx = 44, W - 44 - cw
    topY = 60
    boxH = 300

    def panel(px, title, sub, accent, fill, rows, foot):
        f.append(rect(px, topY, cw, boxH, fill=fill, stroke=accent, sw=1.9, rx=12))
        f.append(text(px + cw / 2, topY + 28, title, size=14, bold=True, color=accent))
        f.append(text(px + cw / 2, topY + 47, sub, size=10.5, color=MUTED))
        # таблиця ніжка -> рівень
        ry0 = topY + 78
        for i, (pinname, level, col) in enumerate(rows):
            ry = ry0 + i * 38
            f.append(fitbox(px + 24, ry, 150, 30, pinname, size=11.5,
                            fill="#ffffff", stroke=MUTED, sw=1.3))
            f.append(fitbox(px + 186, ry, 120, 30, level, size=11.5,
                            fill="#ffffff", stroke=col, sw=1.6, color=col, bold=True))
        f.append(text(px + cw / 2, topY + boxH - 22, foot, size=10.5,
                      color=accent, italic=True))

    panel(lx, "Робота", "запуск прошивки з флеша", FIELD, "#eef6ef",
          [("CH_PD", "↑ 3.3 В", FIELD),
           ("GPIO0", "↑ високий", FIELD),
           ("GPIO2", "↑ високий", FIELD)],
          "чип бере код із флеша")

    panel(rx, "Прошивання", "прийом нової прошивки", POS, "#fdecea",
          [("CH_PD", "↑ 3.3 В", FIELD),
           ("GPIO0", "↓ на землю", POS),
           ("GPIO2", "↑ високий", FIELD)],
          "чип чекає прошивку по TX/RX")

    b, _, _ = textbox(W / 2, 412,
                      "різниця лише в рівні GPIO0 у момент скидання",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "boot-mode.svg"), W, H, *f)


# ── 3. Схема під'єднання для прошивання ───────────────────────────────────────
def fig_wiring():
    W, H = 860, 500
    f = [text(W / 2, 30, "Під'єднання ESP-01 до перехідника USB-UART", size=17, bold=True)]

    # два блоки: перехідник ліворуч, ESP-01 праворуч
    ux, uy, uw, uh = 60, 96, 190, 250
    ew, eh = 210, 250
    ex, ey = W - 60 - ew, 96
    f.append(rect(ux, uy, uw, uh, fill="#eef2f8", stroke=INK, sw=1.7, rx=12))
    f.append(text(ux + uw / 2, uy + 24, "USB-UART", size=12.5, bold=True))
    f.append(text(ux + uw / 2, uy + 42, "(3.3 В логіка)", size=9.5, color=MUTED))

    f.append(rect(ex, ey, ew, eh, fill="#eaf2fb", stroke="#2457d6", sw=1.8, rx=12))
    f.append(text(ex + ew / 2, ey + 24, "ESP-01", size=12.5, bold=True, color="#2457d6"))

    uy0 = uy + 66
    step = 34
    # клеми перехідника (праворуч від блоку)
    uports = {}
    for i, nm in enumerate(["3V3", "GND", "TXD", "RXD"]):
        py = uy0 + i * step
        f.append(circle(ux + uw - 16, py, 7, fill="#fff", stroke=INK, sw=1.8))
        uports[nm] = (ux + uw - 16, py)
    ulabels = ["3V3 (кволе!)", "GND", "TXD", "RXD"]
    for i, lb in enumerate(ulabels):
        f.append(text(ux + uw - 30, uy0 + i * step + 3.5, lb, size=9.5, anchor="end", color=INK))

    # клеми ESP-01 (ліворуч від блоку) — 5 клем, включно з CH_PD
    eorder = ["VCC", "CH_PD", "GND", "RXD", "TXD", "GPIO0"]
    elabels = ["VCC", "CH_PD", "GND", "RX", "TX", "GPIO0"]
    ecol = [POS, POS, MUTED, "#555", "#555", NEG]
    estep = 33
    ey0 = ey + 58
    eports = {}
    for i, nm in enumerate(eorder):
        py = ey0 + i * estep
        f.append(circle(ex + 16, py, 7, fill="#fff", stroke=INK, sw=1.8))
        eports[nm] = (ex + 16, py)
        f.append(text(ex + 30, py + 3.5, elabels[i], size=10, anchor="start",
                      color=ecol[i], bold=True))

    # окреме джерело 3.3 В зверху (бо кволе 3V3 перехідника — погано)
    psx, psy = W / 2 - 74, 58
    f.append(rect(psx, psy - 4, 148, 30, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(psx + 74, psy + 15, "3.3 В (≥300 мА)", size=10, bold=True, color=POS))
    psout = (psx + 74, psy + 26)

    def wire(a, b, col, sw=2.2, dash=None):
        (x1, y1), (x2, y2) = a, b
        f.append(line(x1, y1, x2, y2, color=col, sw=sw, dash=dash))

    # живлення від зовнішнього джерела -> на VCC і CH_PD (обидва до плюса)
    wire(psout, eports["VCC"], POS, 2.4)
    wire(psout, eports["CH_PD"], POS, 2.0)
    # спільна земля перехідник<->ESP
    wire(uports["GND"], eports["GND"], MUTED, 2.2)
    # TX перехідника -> RX плати (перехрестя)
    wire(uports["TXD"], eports["RXD"], "#c0392b", 2.4)
    # RX перехідника -> TX плати
    wire(uports["RXD"], eports["TXD"], "#2457d6", 2.4)

    # GPIO0 -> земля: короткий відвід донизу до спільної шини землі під блоками
    railY = ey + eh + 34
    wire(eports["GPIO0"], (eports["GPIO0"][0], railY), INK, 2.0, dash="5 4")
    wire((eports["GPIO0"][0], railY), (uports["GND"][0], railY), INK, 2.0, dash="5 4")
    wire((uports["GND"][0], railY), uports["GND"], INK, 2.0, dash="5 4")
    f.append(text((eports["GPIO0"][0] + uports["GND"][0]) / 2, railY - 8,
                  "GPIO0 → GND (лише на час прошивання)", size=9.5, color=INK, bold=True))

    # підписи перехресть посередині, рознесені по вертикалі, щоб не накластись
    midx = (ux + uw + ex) / 2
    f.append(text(midx, eports["RXD"][1] - 8, "TX→RX", size=10, color="#c0392b", bold=True))
    f.append(text(midx, eports["TXD"][1] + 18, "RX→TX", size=10, color="#2457d6", bold=True))

    # конденсатор біля живлення ESP (позначка всередині блоку ESP, унизу)
    f.append(text(ex + ew / 2, ey + eh - 14, "‖ конденсатор біля VCC/GND", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 478,
                      "живлення й CH_PD — до плюса; TX/RX — перехрестям; GPIO0 на землі лише на час прошивання",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Цикл прошивання: увійти в завантажувач → залити → вийти → запустити ────
def fig_flash_cycle():
    W, H = 900, 380
    f = [text(W / 2, 30, "Цикл прошивання ESP-01: п'ять кроків по колу", size=17, bold=True)]

    # п'ять кроків уздовж дуги (зліва направо), кожен — рамка з коротким написом
    steps = [
        ("1. GPIO0 → GND", "притиснути до землі", NEG),
        ("2. Скидання", "RST на землю й відпустити", INK),
        ("3. Заливка", "esptool / IDE пише флеш", POS),
        ("4. Зняти GPIO0", "прибрати провід із землі", NEG),
        ("5. Скидання", "плата стартує з новим кодом", FIELD),
    ]
    n = len(steps)
    bx0, by = 28, 120
    bw, bh, gap = 156, 84, 16
    centers = []
    for i, (title, sub, col) in enumerate(steps):
        x = bx0 + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill="#f7fafc", stroke=col, sw=1.8, rx=12))
        f.append(fitbox(x + 8, by + 12, bw - 16, 26, title, size=12.5,
                        fill="#ffffff", stroke=col, sw=1.4, color=col, bold=True))
        f.append(fitbox(x + 8, by + 44, bw - 16, 30, sub, size=10,
                        fill="none", stroke="none", color=MUTED))
        centers.append((x + bw / 2, by))

    # стрілки між кроками (по верху)
    for i in range(n - 1):
        (cx1, _), (cx2, _) = centers[i], centers[i + 1]
        y = by - 12
        f.append(line(cx1 + bw / 2 - 6, y, cx2 - bw / 2 + 6, y, color=INK, sw=1.6))
        f.append(arrow(cx2 - bw / 2 + 2, y, cx2 - bw / 2 + 6, y, color=INK, sw=1.6))

    # петля-повернення від кроку 5 до кроку 1 знизу: «наступний запуск — уже без GPIO0»
    yb = by + bh + 40
    (cx5, _) = centers[-1]
    (cx1, _) = centers[0]
    f.append(line(cx5, by + bh, cx5, yb, color=MUTED, sw=1.5, dash="5 4"))
    f.append(line(cx5, yb, cx1, yb, color=MUTED, sw=1.5, dash="5 4"))
    f.append(line(cx1, yb, cx1, by + bh, color=MUTED, sw=1.5, dash="5 4"))
    f.append(arrow(cx1, by + bh + 6, cx1, by + bh, color=MUTED, sw=1.5))
    f.append(text((cx1 + cx5) / 2, yb + 18,
                  "щоб прошити ще раз — знову крок 1; для звичайного запуску GPIO0 просто лишається вільним",
                  size=10.5, color=MUTED))

    b, _, _ = textbox(W / 2, 350,
                      "у boot-режим уводить крок 1+2; крок 4 випускає плату у нормальний запуск",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "flash-cycle.svg"), W, H, *f)


# ── 5. Зовнішній світлодіод на GPIO2 (у класичного ESP-01 бортового тут нема) ──
def fig_gpio2_led():
    W, H = 980, 470
    f = [text(W / 2, 30, "Світлодіод на GPIO2: два способи ввімкнути", size=17, bold=True)]

    # плата ESP-01 ліворуч із виводом GPIO2
    bx, by, bw, bh = 60, 150, 150, 150
    f.append(rect(bx, by, bw, bh, fill="#eaf2fb", stroke="#2457d6", sw=1.8, rx=12))
    f.append(text(bx + bw / 2, by + 26, "ESP-01", size=12.5, bold=True, color="#2457d6"))
    f.append(text(bx + bw / 2, by + 44, "3.3 В логіка", size=9.5, color=MUTED))
    # вивід GPIO2 праворуч від плати
    g2 = (bx + bw, by + bh / 2 - 20)
    f.append(circle(g2[0], g2[1], 7, fill="#fff", stroke=NEG, sw=1.9))
    f.append(text(g2[0] - 12, g2[1] + 3.5, "GPIO2", size=10, anchor="end", color=NEG, bold=True))
    # вивід GND
    gnd = (bx + bw, by + bh / 2 + 40)
    f.append(circle(gnd[0], gnd[1], 7, fill="#fff", stroke=MUTED, sw=1.9))
    f.append(text(gnd[0] - 12, gnd[1] + 3.5, "GND", size=10, anchor="end", color=MUTED, bold=True))
    # вивід 3V3
    v33 = (bx + bw, by + bh / 2 - 62)
    f.append(circle(v33[0], v33[1], 7, fill="#fff", stroke=POS, sw=1.9))
    f.append(text(v33[0] - 12, v33[1] + 3.5, "3.3 В", size=10, anchor="end", color=POS, bold=True))

    def led(cx, cy, col):
        # трикутник-діод + рисочка
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (cx - 9, cy - 9, cx - 9, cy + 9, cx + 7, cy, "#fff", col))
        f.append(line(cx + 7, cy - 10, cx + 7, cy + 10, color=col, sw=2.2))

    def resistor(x1, y1, x2, y2, col=INK):
        f.append(rect((x1 + x2) / 2 - 16, (y1 + y2) / 2 - 7, 32, 14, fill="#fff", stroke=col, sw=1.5, rx=3))
        f.append(text((x1 + x2) / 2, (y1 + y2) / 2 + 3.5, "R", size=10, color=col, bold=True))

    # СПОСІБ A (активно-високий): GPIO2 → анод LED → R → GND. HIGH світить.
    ax = 320
    f.append(rect(ax, 96, 220, 150, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=12))
    f.append(text(ax + 110, 118, "A. Анод на GPIO2", size=12, bold=True, color=FIELD))
    f.append(text(ax + 110, 136, "HIGH → світить", size=10, color=MUTED))
    ya = 185
    led(ax + 60, ya, FIELD)
    resistor(ax + 90, ya, ax + 150, ya, INK)
    f.append(line(ax + 30, ya, ax + 51, ya, color=INK, sw=2))
    f.append(line(ax + 60 + 7, ya, ax + 90, ya, color=INK, sw=2))
    f.append(line(ax + 150, ya, ax + 190, ya, color=INK, sw=2))
    f.append(text(ax + 30, ya - 12, "GPIO2", size=9.5, color=NEG, anchor="middle"))
    f.append(text(ax + 190, ya - 12, "GND", size=9.5, color=MUTED, anchor="middle"))

    # СПОСІБ B (активно-низький): 3.3В → R → катод... анод LED → GPIO2. LOW світить.
    bx2 = 320
    f.append(rect(bx2, 270, 220, 150, fill="#fdecea", stroke=POS, sw=1.7, rx=12))
    f.append(text(bx2 + 110, 292, "B. Катод на GPIO2", size=12, bold=True, color=POS))
    f.append(text(bx2 + 110, 310, "LOW → світить", size=10, color=MUTED))
    yb2 = 360
    # 3.3В -> R -> анод LED -> (вістря вліво = катод до GPIO2)
    f.append(text(bx2 + 30, yb2 - 12, "3.3 В", size=9.5, color=POS, anchor="middle"))
    f.append(line(bx2 + 30, yb2, bx2 + 60, yb2, color=INK, sw=2))
    resistor(bx2 + 60, yb2, bx2 + 120, yb2, INK)
    f.append(line(bx2 + 120, yb2, bx2 + 150, yb2, color=INK, sw=2))
    # діод вістрям вліво (провідність від 3.3В до GPIO2)
    cx = bx2 + 165
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (cx + 9, yb2 - 9, cx + 9, yb2 + 9, cx - 7, yb2, "#fff", POS))
    f.append(line(cx - 7, yb2 - 10, cx - 7, yb2 + 10, color=POS, sw=2.2))
    f.append(line(cx - 7, yb2, bx2 + 190, yb2, color=INK, sw=2))
    f.append(text(bx2 + 190, yb2 - 12, "GPIO2", size=9.5, color=NEG, anchor="middle"))

    # права колонка — застереження про бортовий LED класичного ESP-01
    nx = 560
    note = ("У класичного ESP-01 бортового світлодіода на GPIO2 НЕМА —\n"
            "синій висить на TX (GPIO1). Тому «блимати GPIO2»\n"
            "означає поставити СВІЙ, зовнішній світлодіод.\n"
            "У ESP-01S бортовий LED уже на GPIO2, і він\n"
            "активно-низький: LOW = світить, HIGH = гасне.\n\n"
            "Резистор R ≈ 220–470 Ом обмежує струм.\n"
            "GPIO2 мусить бути ВИСОКИМ у момент старту —\n"
            "спосіб B (катод на GPIO2) гарантує це сам собою.")
    f.append(fitbox(nx, 96, W - nx - 40, 200, note, size=11,
                    fill="#f7fafc", stroke=INK, sw=1.4, color=INK))

    b, _, _ = textbox(W / 2, 448,
                      "напрям діода задає полярність: анод на GPIO2 → HIGH світить; катод на GPIO2 → LOW світить",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "gpio2-led.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pinout()
    fig_boot_mode()
    fig_wiring()
    fig_flash_cycle()
    fig_gpio2_led()
    print("OK: 5 figures ->", IMG)
