# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-013 — аналоговий давач температури (термістор)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def resistor_v(f, cx, y_top, y_bot, label, sub=None, lab_side=1):
    """Вертикальний резистор (символ-прямокутник) між y_top і y_bot на осі cx.
    lab_side: +1 підпис праворуч, -1 ліворуч. Повертає нічого (пише у f)."""
    rh = 46
    rmid = (y_top + y_bot) / 2
    ry = rmid - rh / 2
    f.append(line(cx, y_top, cx, ry, color=INK, sw=1.8))
    f.append(line(cx, ry + rh, cx, y_bot, color=INK, sw=1.8))
    f.append(rect(cx - 16, ry, 32, rh, fill=BG, stroke=INK, sw=1.6, rx=3))
    ax = cx + 26 if lab_side > 0 else cx - 26
    anc = "start" if lab_side > 0 else "end"
    f.append(text(ax, rmid - 3, label, size=11.5, bold=True, color=INK, anchor=anc))
    if sub:
        f.append(text(ax, rmid + 13, sub, size=9.5, color=MUTED, anchor=anc))


def thermistor_v(f, cx, y_top, y_bot, lab_side=1):
    """Вертикальний термістор: резистор із діагоналлю-стрілкою (символ t°).
    lab_side: +1 підпис праворуч, -1 ліворуч."""
    rh = 50
    rmid = (y_top + y_bot) / 2
    ry = rmid - rh / 2
    f.append(line(cx, y_top, cx, ry, color=INK, sw=1.8))
    f.append(line(cx, ry + rh, cx, y_bot, color=INK, sw=1.8))
    f.append(rect(cx - 17, ry, 34, rh, fill="#eaf3fb", stroke=NEG, sw=1.8, rx=3))
    # діагональ через тіло (позначка «змінний від t°»)
    f.append(line(cx - 24, ry + rh + 8, cx + 22, ry - 8, color=NEG, sw=2.0,
                  dash=None))
    f.append(text(cx + 22, ry - 12, "t°", size=11, bold=True, color=NEG, anchor="start"))
    ax = cx + 30 if lab_side > 0 else cx - 30
    anc = "start" if lab_side > 0 else "end"
    f.append(text(ax, rmid - 3, "термістор NTC", size=11.5, bold=True, color=NEG, anchor=anc))
    f.append(text(ax, rmid + 13, "10 кОм · B≈3950", size=9.5, color=MUTED, anchor=anc))


# ── 1. Внутрішня схема KY-013: дільник термістор + сталий резистор ──────────────
def fig_ky013_schematic():
    W, H = 900, 500
    f = [text(W / 2, 30, "Що всередині KY-013: дільник із термістора й сталого резистора 10 кОм",
              size=15, bold=True)]

    # рамка плати
    bx, by, bw, bh = 150, 62, 600, 350
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-013", size=11, bold=True, color=MUTED, anchor="start"))

    # шина + (VCC) угорі, шина − (GND) внизу
    vcc_y = by + 64
    gnd_y = by + bh - 40
    axc = bx + bw * 0.36            # вісь дільника (ліворуч від центру, щоб підписи справа не билися з S)
    f.append(line(bx + 40, vcc_y, bx + bw - 40, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 40, vcc_y - 12, "+  (живлення 3.3–5 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(bx + 40, gnd_y, bx + bw - 40, gnd_y, color=NEG, sw=2.2))
    f.append(text(bx + 40, gnd_y + 24, "−  (GND)", size=11, bold=True, color=NEG, anchor="start"))

    node_y = (vcc_y + gnd_y) / 2

    # ВЕРХНЄ плече — термістор (між + і вузлом S); НИЖНЄ — сталий резистор
    thermistor_v(f, axc, vcc_y, node_y, lab_side=-1)
    resistor_v(f, axc, node_y, gnd_y, "R  10 кОм", "сталий (опорний)", lab_side=-1)

    # вузол-крапка S
    f.append(circle(axc, node_y, 3.6, fill=INK, stroke=INK, sw=1))

    # вивід S праворуч від вузла
    sx = bx + bw - 40
    f.append(line(axc, node_y, sx, node_y, color=FIELD, sw=1.8))
    f.append(circle(sx, node_y, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(sx - 14, node_y - 10, "S  (сигнал → АЦП)", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(text(sx - 14, node_y + 8, "U середньої точки", size=9.5, color=MUTED, anchor="end"))

    # пояснення поведінки — окремим блоком нижче, поза схемою
    b, _, _ = textbox(W / 2, 456, "гарячіше → опір термістора падає → для цієї розводки (термістор угорі) напруга на S РОСТЕ\n"
                                  "інша партія розводить навпаки (термістор унизу) — тоді нагрів напругу на S ОПУСКАЄ",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky013-schematic.svg"), W, H, *f)


# ── 2. Підключення пін-у-пін: KY-013 ↔ мікроконтролер ──────────────────────────
def fig_ky013_wiring():
    W, H = 900, 430
    f = [text(W / 2, 30, "Підключення KY-013: три дроти, сигнал — на АНАЛОГОВИЙ вхід",
              size=15, bold=True)]

    # Модуль ліворуч
    mx, my, mw, mh = 70, 92, 250, 210
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=NEG, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-013", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 48, "термістор", size=10, color=MUTED))
    # три контактні площадки праворуч на модулі
    pads = [("S", FIELD, my + 92), ("+", POS, my + 137), ("−", NEG, my + 182)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    # Плата праворуч
    bx, by, bw, bh = 600, 92, 250, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("A0", FIELD, by + 92, "аналоговий вхід"),
            ("3.3–5 В", POS, by + 137, "живлення"),
            ("GND", NEG, by + 182, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # три дроти між ними — прямі, різного кольору, без перетинів
    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    # нагадування про середній штир
    f.append(text(W / 2, my + 137 - 16, "+ — СЕРЕДНІЙ штир (підключай за літерами!)",
                  size=10, bold=True, color=POS))

    # застереження про рівень/опорну — унизу, окремо
    b, _, _ = textbox(W / 2, 375, "Живи давач під логіку плати: на 3.3-вольтовій платі (ESP32) — від 3.3 В, не 5 В.\n"
                                  "Найкраще — від ТІЄЇ Ж напруги, що опорна для АЦП: тоді живлення у формулі скорочується.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky013-wiring.svg"), W, H, *f)


# ── 3. Таблиця + лінійна інтерполяція: як без log() дістати градуси ─────────────
def fig_ky013_lut():
    W, H = 900, 470
    f = [text(W / 2, 30, "Замість log() — таблиця «відлік АЦП → °C» і пряма між двома рядками",
              size=15, bold=True)]

    # ── ліворуч: сама таблиця (кілька рядків) ──
    tx, ty = 60, 78
    rows = [("відлік", "°C"),
            ("…", "…"),
            ("612", "20"),
            ("548", "25"),   # ← сусідні рядки, між якими інтерполюємо
            ("486", "30"),
            ("…", "…")]
    rh, cw = 34, 78
    for i, (a, b) in enumerate(rows):
        yy = ty + i * rh
        head = (i == 0)
        hot = (a in ("548", "486"))            # два «сусідні» рядки — виділити
        fillc = "#eef3fb" if head else ("#fdf3e7" if hot else BG)
        f.append(rect(tx, yy, cw, rh, fill=fillc, stroke=INK, sw=1.3, rx=0))
        f.append(rect(tx + cw, yy, cw, rh, fill=fillc, stroke=INK, sw=1.3, rx=0))
        col = MUTED if head else INK
        f.append(text(tx + cw / 2, yy + rh / 2 + 5, a, size=13, bold=head or hot, color=col))
        f.append(text(tx + cw + cw / 2, yy + rh / 2 + 5, b, size=13, bold=head or hot, color=col))
    # позначка «шукаємо 517»
    y_target = ty + 3 * rh + rh / 2      # між рядками 548 і 486
    f.append(text(tx + cw, ty - 14, "таблиця в flash", size=10, color=MUTED, anchor="middle"))
    f.append(arrow(tx - 26, y_target, tx - 4, y_target, color=POS, sw=2.2))
    f.append(text(tx - 30, y_target + 4, "517?", size=12, bold=True, color=POS, anchor="end"))

    # ── праворуч: пряма між двома точками ──
    gx, gy, gw, gh = 420, 96, 380, 300
    f.append(rect(gx, gy, gw, gh, fill="#f7f9fc", stroke=MUTED, sw=1.2, rx=8))
    # осі
    f.append(line(gx + 40, gy + gh - 40, gx + gw - 20, gy + gh - 40, color=INK, sw=1.6))  # X
    f.append(line(gx + 40, gy + 24, gx + 40, gy + gh - 40, color=INK, sw=1.6))            # Y
    f.append(text(gx + gw - 20, gy + gh - 20, "відлік АЦП", size=10, color=MUTED, anchor="end"))
    f.append(text(gx + 24, gy + 18, "°C", size=11, bold=True, color=MUTED, anchor="middle"))

    # дві табличні точки (486,30) і (548,25) → у пікселі
    pA = (gx + 110, gy + gh - 90)    # (548, 25)  нижчий відлік праворуч? беремо як є, ілюстративно
    pB = (gx + 300, gy + gh - 200)   # (486, 30)
    # відрізок-хорда між ними
    f.append(line(pA[0], pA[1], pB[0], pB[1], color=NEG, sw=2.6))
    for (px, py), lab in ((pA, "548 → 25°"), (pB, "486 → 30°")):
        f.append(circle(px, py, 5.5, fill=BG, stroke=NEG, sw=2.4))
        f.append(text(px, py - 14, lab, size=10.5, bold=True, color=NEG))

    # шукана точка 517 → її частка між 548 і 486; y лінійно
    frac = 0.5   # 517 приблизно посередині 548..486
    qx = pA[0] + (pB[0] - pA[0]) * frac
    qy = pA[1] + (pB[1] - pA[1]) * frac
    f.append(line(qx, gy + gh - 40, qx, qy, color=POS, sw=1.6, dash="4 3"))
    f.append(line(gx + 40, qy, qx, qy, color=POS, sw=1.6, dash="4 3"))
    f.append(circle(qx, qy, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(qx + 8, qy - 8, "517 → 27.5°", size=11, bold=True, color=POS, anchor="start"))

    # підпис-суть унизу, окремо, поза графіком
    b, _, _ = textbox(W / 2, 448, "відлік лежить МІЖ двома рядками таблиці → температуру беремо з ПРЯМОЇ, "
                                  "проведеної між їхніми °C (лінійна інтерполяція) — жодного логарифма",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky013-lut-interp.svg"), W, H, *f)


# ── 4. Історія термістора: спостереження → робочий прилад → масовий випуск ─────
def fig_thermistor_history():
    W, H = 940, 470
    f = [text(W / 2, 30, "Від спостереження до приладу: три різні кроки, майже 115 років",
              size=15, bold=True)]

    # горизонтальна вісь часу
    ax_y = 150
    x0, x1 = 90, W - 60
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    f.append(arrow(x1 - 2, ax_y, x1 + 8, ax_y, color=INK, sw=2.2))
    f.append(text(x1 + 6, ax_y + 22, "час", size=10, color=MUTED, anchor="end"))

    # три віхи: (частка по осі, рік, кому, що саме, колір, статус-крок)
    milestones = [
        (0.06, "1833", "Майкл Фарадей",
         "Ag₂S проводить\nкраще з нагрівом", NEG, "СПОСТЕРЕЖЕННЯ"),
        (0.62, "бл. 1930", "Семюел Рубен",
         "перший придатний\nдо випуску термістор", FIELD, "РОБОЧИЙ ПРИЛАД"),
        (0.93, "1946–47", "Bell Labs\n(Беккер·Ґрін·Пірсон)",
         "промислова серія,\nтеорія й назва", POS, "МАСОВИЙ ВИПУСК"),
    ]
    for frac, year, who, what, col, step in milestones:
        mx = x0 + (x1 - x0) * frac
        f.append(circle(mx, ax_y, 7, fill=BG, stroke=col, sw=2.6))
        # рік — над віссю
        f.append(text(mx, ax_y - 16, year, size=13, bold=True, color=col))
        # хто — трохи вище
        for i, ln in enumerate(who.split("\n")):
            f.append(text(mx, ax_y - 40 - (len(who.split("\n")) - 1 - i) * 15,
                          ln, size=10.5, bold=True, color=INK))
        # що — під віссю у рамці, щоб не збігалося з сусідами
        b, bw, bh = textbox(mx, ax_y + 62, what, size=10, fill="#f7f9fc", stroke=col, pad=8)
        f.append(b)
        # ярлик-крок — ще нижче, окремо
        f.append(text(mx, ax_y + 62 + bh / 2 + 18, step, size=9.5, bold=True, color=col))

    # проміжок «майже століття мовчання» — дуга-підпис між 1833 і 1930
    gx0 = x0 + (x1 - x0) * 0.06
    gx1 = x0 + (x1 - x0) * 0.62
    gap_y = ax_y + 150
    f.append(line(gx0, gap_y, gx1, gap_y, color=MUTED, sw=1.4, dash="5 4"))
    f.append(line(gx0, gap_y - 6, gx0, gap_y + 6, color=MUTED, sw=1.4))
    f.append(line(gx1, gap_y - 6, gx1, gap_y + 6, color=MUTED, sw=1.4))
    f.append(text((gx0 + gx1) / 2, gap_y - 8, "≈ століття без практичного приладу",
                  size=10.5, italic=True, color=MUTED))
    f.append(text((gx0 + gx1) / 2, gap_y + 18, "ранні зразки нестабільні й нетехнологічні",
                  size=9.5, color=MUTED))

    # висновок-суть — унизу, окремо
    b, _, _ = textbox(W / 2, 448, "«хтось помітив ефект» ≠ «хтось зробив робочу річ» ≠ «хтось запустив у серію» — це три різні внески",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "thermistor-history.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ky013_schematic()
    fig_ky013_wiring()
    fig_ky013_lut()
    fig_thermistor_history()
    print("KY-013 figs done ->", IMG)
