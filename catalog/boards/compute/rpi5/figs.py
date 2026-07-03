# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Raspberry Pi 5».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Архітектура: два чипи — BCM2712 (мозок) і RP1 (порти) через PCIe ────────
def fig_architecture():
    W, H = 860, 470
    f = [text(W / 2, 30, "Дві мікросхеми Pi 5: обчислення в BCM2712, порти в RP1",
              size=15, bold=True)]

    # BCM2712 — велика ліва коробка
    bx, by, bw, bh = 60, 70, 300, 250
    f.append(rect(bx, by, bw, bh, fill="#eef2f8", stroke=NEG, sw=2.0, rx=12))
    f.append(text(bx + bw / 2, by + 28, "BCM2712", size=15, bold=True, color=NEG))
    f.append(text(bx + bw / 2, by + 48, "процесор (16 нм)", size=10.5, color=MUTED))
    inner = [
        "4 × Cortex-A76 @ 2.4 ГГц",
        "L2 512 кБ/ядро · L3 2 МБ",
        "GPU VideoCore VII @ 800 МГц",
        "контролер LPDDR4X-4267",
        "2 × HDMI (4Kp60)",
    ]
    iy = by + 78
    for s in inner:
        f.append(text(bx + 22, iy, "• " + s, size=10.5, color=INK, anchor="start"))
        iy += 26

    # RP1 — права коробка
    rx, ry, rw, rh = 560, 70, 240, 250
    f.append(rect(rx, ry, rw, rh, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(rx + rw / 2, ry + 28, "RP1", size=15, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, ry + 48, "південний міст (порти)", size=10.5, color=MUTED))
    ports = [
        "2 × USB 3.0 · 2 × USB 2.0",
        "Gigabit Ethernet",
        "40-пін GPIO (3.3 В)",
        "UART · SPI · I²C · I²S · PWM",
        "2 × MIPI (камера/дисплей)",
    ]
    py = ry + 78
    for s in ports:
        f.append(text(rx + 18, py, "• " + s, size=10.5, color=INK, anchor="start"))
        py += 26

    # PCIe-міст між ними
    my = by + bh / 2
    f.append(line(bx + bw, my, rx, my, color=POS, sw=3.0))
    b, bw2, _ = textbox((bx + bw + rx) / 2, my - 30,
                        "PCIe ×4\nвнутрішня шина",
                        size=10.5, bold=True, color=POS, fill="#fdecea", stroke=POS)
    f.append(b)

    # окремий PCIe-роз'єм назовні (з BCM2712)
    ex, ey = bx + bw / 2, by + bh + 60
    f.append(rect(ex - 95, ey - 20, 190, 40, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(ex, ey + 5, "роз'єм PCIe 2.0 ×1", size=11, bold=True))
    f.append(line(ex, by + bh, ex, ey - 20, color=NEG, sw=2.4))
    f.append(text(ex + 66, (by + bh + ey - 20) / 2, "1 лінія назовні", size=9, color=MUTED, anchor="start"))

    b2, _, _ = textbox(W / 2, 448,
                       "усе, що встромляється в порти, йде через RP1; роз'єм PCIe — пряма лінія від BCM2712 до SSD/прискорювача",
                       size=10.5, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "architecture.svg"), W, H, *f)


# ── 2. Розводка: живлення й головні роз'єми по краях плати ─────────────────────
def fig_board_layout():
    W, H = 940, 560
    f = [text(W / 2, 30, "Живлення й роз'єми Raspberry Pi 5: що куди підключати",
              size=15, bold=True)]

    # плата — по центру, з запасом навколо для виносок
    bx, by, bw, bh = 320, 90, 300, 300
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + bh / 2 - 8, "Raspberry Pi 5", size=13, bold=True, color=MUTED))
    f.append(text(bx + bw / 2, by + bh / 2 + 12, "85.6 × 56.5 мм", size=10, color=MUTED))

    # 40-пін GPIO — угорі плати
    gpx = bx + bw / 2
    f.append(rect(gpx - 115, by + 8, 230, 20, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=5))
    f.append(text(gpx, by + 22, "40-пін GPIO (3.3 В логіка)", size=9.5, bold=True, color=FIELD))

    # виносна підпис-коробка: сама малює свій прямокутник + 2 рядки (без дублю тексту)
    def callout(cx, cy, title, sub, accent, anchor_x, anchor_y, side):
        pad = 9
        tw = max(text_width(title, 10.5, True), text_width(sub, 9.5, False))
        w = tw + 2 * pad
        h = 40
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=BG, stroke=accent, sw=1.6, rx=7))
        f.append(text(cx, cy - 4, title, size=10.5, bold=True, color=accent))
        f.append(text(cx, cy + 12, sub, size=9.5, color=INK))
        # лідер від краю коробки (з боку плати) до пункту на платі
        edge = cx + w / 2 if side == "L" else cx - w / 2
        f.append(line(edge, cy, anchor_x, anchor_y, color=accent, sw=1.6))

    # ── ЛІВИЙ край плати — живлення й відео (виноски ще лівіше) ──
    lx = 150  # центр лівих виносок
    # USB-C живлення
    f.append(rect(bx - 8, by + 55, 16, 30, fill=POS, stroke=POS, sw=1, rx=3))
    callout(lx, by + 55, "USB-C живлення", "5.1 В, до 5 А (PD 27 Вт)", POS, bx - 8, by + 70, "L")
    # HDMI
    f.append(rect(bx - 8, by + 130, 16, 20, fill=INK, stroke=INK, sw=1, rx=3))
    f.append(rect(bx - 8, by + 158, 16, 20, fill=INK, stroke=INK, sw=1, rx=3))
    callout(lx, by + 150, "2 × micro-HDMI", "два екрани 4Kp60", INK, bx - 8, by + 158, "L")

    # ── ПРАВИЙ край плати — дані й мережа (виноски ще правіше) ──
    rx = W - 150  # центр правих виносок
    # USB 3.0
    f.append(rect(bx + bw - 8, by + 45, 16, 36, fill=NEG, stroke=NEG, sw=1, rx=3))
    callout(rx, by + 50, "2 × USB 3.0", "5 Гбіт/с, сині", NEG, bx + bw + 8, by + 63, "R")
    # USB 2.0
    f.append(rect(bx + bw - 8, by + 105, 16, 36, fill="#555", stroke="#555", sw=1, rx=3))
    callout(rx, by + 130, "2 × USB 2.0", "миша/клавіатура", MUTED, bx + bw + 8, by + 123, "R")
    # Ethernet
    f.append(rect(bx + bw - 8, by + 165, 16, 30, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    callout(rx, by + 210, "Gigabit Ethernet", "1 Гбіт/с, PoE+ через HAT", FIELD, bx + bw + 8, by + 180, "R")

    # ── НИЗ плати — три виноски рознесено по ширині нижче плати ──
    fy = by + bh + 60
    # PCIe FFC (ліво-низ)
    f.append(rect(bx + 30, by + bh - 8, 66, 16, fill=POS, stroke=POS, sw=1, rx=3))
    callout(bx + 5, fy, "PCIe 2.0 ×1", "SSD/прискорювач (FFC)", POS, bx + 60, by + bh + 8, "R")
    # RTC-батарейка (центр-низ)
    f.append(circle(bx + bw / 2, by + bh - 18, 11, fill=BG, stroke=MUTED, sw=1.6))
    callout(bx + bw / 2, fy, "RTC + батарейка", "CR2032 тримає час", MUTED, bx + bw / 2, by + bh - 7, "R")
    # кнопка живлення + вентилятор (право-низ)
    f.append(circle(bx + bw - 40, by + bh - 18, 8, fill="#fdecea", stroke=POS, sw=1.6))
    callout(bx + bw - 5, fy, "кнопка + вентил.", "ON/OFF, 4-пін fan", MUTED, bx + bw - 40, by + bh - 7, "L")

    b2, _, _ = textbox(W / 2, 535,
                       "живлення — ліворуч (USB-C), дані й мережа — праворуч; повні 5 А та збільшений струм на USB дає лише офіційний PD-блок",
                       size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "board-layout.svg"), W, H, *f)


# ── 3. Дві нумерації того самого штирка: фізичний № vs BCM № ───────────────────
def fig_pin_numbering():
    W, H = 900, 560
    f = [text(W / 2, 30, "Один штирок — два номери: фізичне місце vs назва GPIO",
              size=15, bold=True)]

    # Гребінка: два стовпці по 5 рядків (показуємо перші 10 штирків), як на платі
    # ліва колонка — непарні (1,3,5,7,9), права — парні (2,4,6,8,10)
    rows = [
        # (фізичний_лівий, BCM_лівий, фізичний_правий, BCM_правий)
        ("1",  "3.3 В",   "живл.", "2",  "5 В",    "живл."),
        ("3",  "GPIO 2",  "SDA",   "4",  "5 В",    "живл."),
        ("5",  "GPIO 3",  "SCL",   "6",  "земля",  "GND"),
        ("7",  "GPIO 4",  "",      "8",  "GPIO 14","TXD"),
        ("9",  "земля",   "GND",   "10", "GPIO 15","RXD"),
    ]

    # координати гребінки
    gx, gy = W / 2, 90          # верх-центр між колонками
    dy = 74                     # крок між рядками
    r = 15                      # радіус контакту
    colgap = 60                 # відстань між двома колонками контактів

    # заголовки колонок
    f.append(text(gx - colgap - 120, gy - 24, "непарні (ліворуч)", size=10.5, color=MUTED))
    f.append(text(gx + colgap + 120, gy - 24, "парні (праворуч)", size=10.5, color=MUTED))

    def pin(cx, cy, phys, bcm, note, side):
        # колір: живлення — червоне, земля — сіре, GPIO — зелене
        if bcm.startswith("GPIO"):
            fillc, strokec = "#eef6ef", FIELD
        elif "В" in bcm:
            fillc, strokec = "#fdecea", POS
        else:
            fillc, strokec = "#eef2f8", MUTED
        f.append(circle(cx, cy, r, fill=fillc, stroke=strokec, sw=2.0))
        f.append(text(cx, cy + 4, phys, size=11, bold=True, color=INK))
        # підпис BCM/функції — назовні від гребінки
        tx = cx - r - 12 if side == "L" else cx + r + 12
        anc = "end" if side == "L" else "start"
        f.append(text(tx, cy - 3, bcm, size=11, bold=True, color=strokec, anchor=anc))
        if note:
            f.append(text(tx, cy + 13, note, size=9, color=MUTED, anchor=anc))

    for i, (pl, bl, nl, pr, br, nr) in enumerate(rows):
        cy = gy + i * dy
        pin(gx - colgap, cy, pl, bl, nl, "L")
        pin(gx + colgap, cy, pr, br, nr, "R")

    # рамка навколо гребінки
    f.append(rect(gx - colgap - r - 6, gy - r - 6,
                  2 * (colgap + r + 6), (len(rows) - 1) * dy + 2 * r + 12,
                  fill="none", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(gx, gy + (len(rows) - 1) * dy + r + 28,
                  "… далі до 40", size=10, color=MUTED))

    # виносна пояснювальна коробка ліворуч знизу
    b1, _, _ = textbox(230, 500,
                       "«Фізичний 3» і «GPIO 2» — ОДИН штирок.\n"
                       "Число всередині = місце на гребінці (1…40).\n"
                       "GPIO N = ім'я лінії в чипі (для коду).",
                       size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    # застереження праворуч знизу
    b2, _, _ = textbox(680, 500,
                       "libgpiod хоче BCM-зсув (offset),\n"
                       "а не фізичний номер!\n"
                       "GPIO 17 → offset 17, а не «11».",
                       size=10.5, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "pin-numbering.svg"), W, H, *f)


if __name__ == "__main__":
    fig_architecture()
    fig_board_layout()
    fig_pin_numbering()
    print("OK: 3 figures ->", IMG)
