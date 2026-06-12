# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки r11-s5-c-pico-board.md
(🔌 Компонент: плата Pico-класу — зовнішня QSPI-Flash і прошивка UF2)

Фігури:
  fig-r11-5c-1-anatomy.svg  — анатомія плати Pico-класу (block-diagram)
  fig-r11-5c-2-uf2-flow.svg — потік прошивки UF2 (BOOTSEL → диск → flash → run)

Вивід → ./img/
Стиль (AUTHORING §9): svgkit — спільні примітиви; текст лише через textbox()/fitbox().
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.5c.1 — Анатомія плати Pico-класу
# ────────────────────────────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 780, 460
    frags = []

    # ── Фон плати ───────────────────────────────────────────────────────────
    BOARD = "#1a6b3a"   # зелений текстоліт
    frags.append('<rect x="60" y="60" width="660" height="340" rx="12" '
                 'fill="%s" stroke="#0f4a28" stroke-width="2"/>' % BOARD)

    # ── Castellated-гребінка (зліва й справа, умовно) ───────────────────────
    for i in range(9):
        yy = 100 + i * 34
        # ліва
        frags.append('<rect x="50" y="%.0f" width="20" height="18" rx="3" '
                     'fill="#b8a060" stroke="#8a7040" stroke-width="1"/>' % yy)
        # права
        frags.append('<rect x="710" y="%.0f" width="20" height="18" rx="3" '
                     'fill="#b8a060" stroke="#8a7040" stroke-width="1"/>' % yy)

    # ── RP2040 — головний чип ───────────────────────────────────────────────
    frags.append('<rect x="270" y="155" width="180" height="150" rx="8" '
                 'fill="#2c2c2c" stroke="#666" stroke-width="2"/>')
    tb, tw, th = textbox(360, 225, "RP2040\nCortex-M0+\nдвоядерний",
                         size=13, fill="#2c2c2c", stroke="#aaa", color="#eeeeee", bold=True)
    frags.append(tb)

    # ── QSPI-Flash — ОКРЕМИЙ чип ─────────────────────────────────────────────
    frags.append('<rect x="490" y="165" width="140" height="90" rx="6" '
                 'fill="#3a3a5c" stroke="#7777cc" stroke-width="2.5"/>')
    tb2, _, _ = textbox(560, 205, "QSPI-Flash\nW25Q16-клас\n~2 МБ",
                        size=12, fill="#3a3a5c", stroke="#7777cc", color="#ccccff", bold=True)
    frags.append(tb2)

    # Підпис «окремий чип» з акцентом
    frags.append(text(560, 268, "← окремий чип від RP2040", size=11,
                      color="#ffcc44", anchor="middle", italic=True))

    # Лінія QSPI між RP2040 і Flash
    frags.append(line(450, 210, 490, 210, color="#7777cc", sw=2.5))
    frags.append(arrow(450, 230, 490, 230, color="#7777cc", sw=2.5))
    frags.append(text(470, 248, "QSPI", size=10, color="#9999ee", anchor="middle"))

    # ── USB-роз'єм (напряму до RP2040) ──────────────────────────────────────
    frags.append('<rect x="95" y="345" width="80" height="40" rx="4" '
                 'fill="#888899" stroke="#555" stroke-width="1.5"/>')
    tb3, _, _ = textbox(135, 365, "USB\n(micro/C)", size=11,
                        fill="#888899", stroke="#555", color="#ffffff")
    frags.append(tb3)
    # лінія до RP2040 (напряму — без UART-моста)
    frags.append(arrow(175, 360, 270, 290, color=NEG, sw=2))
    frags.append(text(215, 340, "напряму", size=10, color=NEG, anchor="middle", italic=True))
    frags.append(text(215, 353, "(без UART-моста)", size=10, color=NEG, anchor="middle", italic=True))

    # ── BOOTSEL-кнопка ─────────────────────────────────────────────────────
    frags.append('<circle cx="185" cy="180" r="22" fill="#cc4444" stroke="#882222" stroke-width="2"/>')
    frags.append(text(185, 185, "BOOT\nSEL", size=10, color="#fff", bold=True, anchor="middle"))

    # ── Buck-boost / SMPS ──────────────────────────────────────────────────
    frags.append('<rect x="95" y="170" width="70" height="55" rx="5" '
                 'fill="#4a3a1a" stroke="#aa7722" stroke-width="1.5"/>')
    tb4, _, _ = textbox(130, 197, "Buck-\nbooст\n3.3 В", size=10,
                        fill="#4a3a1a", stroke="#aa7722", color="#ffdd88")
    frags.append(tb4)

    # ── Кварц ──────────────────────────────────────────────────────────────
    frags.append('<rect x="320" y="105" width="80" height="36" rx="4" '
                 'fill="#444422" stroke="#aaaa33" stroke-width="1.5"/>')
    tb5, _, _ = textbox(360, 123, "Кварц\n12 МГц", size=10,
                        fill="#444422", stroke="#aaaa33", color="#eeee88")
    frags.append(tb5)
    frags.append(line(360, 141, 360, 155, color="#aaaa33", sw=1.5))

    # ── Піни живлення — підписи ──────────────────────────────────────────────
    frags.append(fitbox(92, 250, 80, 22, "VBUS (5 В)", size=10,
                        fill="#3a1a1a", stroke=POS, color="#ffaaaa"))
    frags.append(fitbox(92, 276, 80, 22, "VSYS (1.8–5.5 В)", size=9,
                        fill="#3a1a1a", stroke=POS, color="#ffaaaa"))
    frags.append(fitbox(92, 302, 80, 22, "3V3 / GND", size=10,
                        fill="#2a2a3a", stroke=MUTED, color="#cccccc"))

    # ── SWD ────────────────────────────────────────────────────────────────
    frags.append('<rect x="490" y="310" width="80" height="36" rx="4" '
                 'fill="#1a2a1a" stroke="#44aa44" stroke-width="1.5"/>')
    tb6, _, _ = textbox(530, 328, "SWD\n(3-пін)", size=10,
                        fill="#1a2a1a", stroke="#44aa44", color="#88ee88")
    frags.append(tb6)

    # ── Легенда ──────────────────────────────────────────────────────────────
    frags.append(fitbox(590, 360, 150, 60,
                        "Flash — окремий чип\n(у ESP32 вона\nвсередині модуля)",
                        size=10, fill="#fffbe6", stroke="#ccaa00", color=INK))

    # ── Заголовок ─────────────────────────────────────────────────────────
    frags.append(text(390, 36, "Анатомія плати Pico-класу", size=15, bold=True, color=INK))

    render(os.path.join(OUT, "fig-r11-5c-1-anatomy.svg"), W, H, *frags)
    print("  fig-r11-5c-1-anatomy.svg — OK")


# ────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.5c.2 — Прошивка перетягуванням: потік UF2
# ────────────────────────────────────────────────────────────────────────────
def fig_uf2_flow():
    W, H = 820, 220
    frags = []

    # 6 блоків: горизонтальний потік
    steps = [
        ("BOOTSEL\n+ USB/RESET",   "#3a1a1a", POS,      90),
        ("RP2040\nu bootrom",       "#1a1a3a", NEG,      210),
        ("Диск RPI-RP2\n(Mass Storage)", "#1a3a1a", FIELD, 350),
        ("Перетягуєш\nfirmware.uf2", "#2a2a1a", "#cc9900", 490),
        ("Bootrom пише\nu QSPI-Flash", "#1a1a3a", NEG,   630),
        ("Програма\nбіжить!",        "#1a3a1a", FIELD,   760),
    ]

    BOX_W, BOX_H = 110, 68
    CY = 110

    for label, fill, stroke, cx in steps:
        tb, tw, th = textbox(cx, CY, label, size=12, fill=fill, stroke=stroke,
                              color="#eeeeee", bold=False, min_w=BOX_W)
        frags.append(tb)

    # Стрілки між блоками
    arrow_xs = [
        (90 + BOX_W//2 + 2,  210 - BOX_W//2 - 2),
        (210 + BOX_W//2 + 2, 350 - BOX_W//2 - 2),
        (350 + BOX_W//2 + 2, 490 - BOX_W//2 - 2),
        (490 + BOX_W//2 + 2, 630 - BOX_W//2 - 2),
        (630 + BOX_W//2 + 2, 760 - BOX_W//2 - 2),
    ]
    for x1, x2 in arrow_xs:
        frags.append(arrow(x1, CY, x2, CY, color=LINE, sw=2.2))

    # Підписи над стрілками
    labels = [
        (150, "bootrom\nstartup"),
        (280, "USB Mass\nStorage"),
        (420, "drag &\ndrop"),
        (560, "запис у\nFlash"),
        (695, "reboot →\nдиск зник"),
    ]
    for lx, lbl in labels:
        frags.append(mtext(lx, CY - 46, lbl, size=9, color=MUTED, anchor="middle"))

    # Акцент на «Диск RPI-RP2» — ключовий крок
    frags.append('<rect x="294" y="76" width="112" height="68" rx="8" '
                 'fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % FIELD)
    frags.append(text(350, 165, "ключовий крок", size=9, color=FIELD,
                      anchor="middle", italic=True))

    # Контраст-підпис знизу
    frags.append(fitbox(20, 176, 780, 26,
                        "Нуль інструментів і драйверів — контраст із esptool + USB-UART міст + DTR/RTS у ESP32",
                        size=10, fill="#fffbe6", stroke="#ccaa00", color=INK))

    # Заголовок
    frags.append(text(410, 28, "Прошивка перетягуванням — шлях UF2-файлу", size=14, bold=True, color=INK))

    render(os.path.join(OUT, "fig-r11-5c-2-uf2-flow.svg"), W, H, *frags)
    print("  fig-r11-5c-2-uf2-flow.svg — OK")


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Генерую SVG для r11-s5-c-pico-board …")
    fig_anatomy()
    fig_uf2_flow()
    print("Готово.")
