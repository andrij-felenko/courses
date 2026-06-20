# -*- coding: utf-8 -*-
"""Фігури до вставки «P-MOSFET як верхній ключ навантаження».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def pmos_symbol(cx, cy, color=INK, sw=2.2):
    """Спрощений символ P-MOSFET. Витік угорі (S), стік унизу (D), затвор ліворуч (G).
    Повертає (svg, точки S, G, D у вигляді кортежів)."""
    out = []
    # вертикальний канал
    chx = cx
    s_y, d_y = cy - 34, cy + 34
    out.append(line(chx, s_y, chx, d_y, color=color, sw=sw + 0.4))
    # затворна пластина (вертикальна риска ліворуч від каналу)
    gx = cx - 26
    out.append(line(gx, cy - 22, gx, cy + 22, color=color, sw=sw + 0.4))
    out.append(line(gx, cy, gx + 26, cy, color=color, sw=sw))   # вивід затвора до каналу
    # вивід затвора назовні
    out.append(line(gx, cy, gx - 22, cy, color=color, sw=sw))
    # витік і стік назовні
    out.append(line(chx, s_y, chx, s_y - 18, color=color, sw=sw))
    out.append(line(chx, d_y, chx, d_y + 18, color=color, sw=sw))
    # підписи
    out.append(text(chx + 14, s_y + 4, "S", size=13, bold=True, color=color, anchor="start"))
    out.append(text(chx + 14, d_y + 4, "D", size=13, bold=True, color=color, anchor="start"))
    out.append(text(gx - 26, cy + 4, "G", size=13, bold=True, color=color, anchor="end"))
    return "".join(out), (chx, s_y - 18), (gx - 22, cy), (chx, d_y + 18)


# ── 1. Чому PMOS зручний зверху: затвор НИЖЧЕ витоку вмикає ───────────────────
def fig_why_pmos_on_top():
    W, H = 760, 400
    f = [text(W / 2, 26, "P-MOSFET зверху: щоб увімкнути, затвор тягнемо НИЖЧЕ витоку", size=15.5, bold=True)]

    def panel(x0, title, gate_low, ok):
        col = FIELD if ok else MUTED
        f.append(rect(x0, 52, 340, 320, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 76, title, size=13, bold=True, color=INK))
        # шина +12 угорі
        railx0, railx1 = x0 + 40, x0 + 300
        ry = 104
        f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.4))
        f.append(text(x0 + 170, ry - 8, "+12 В (шина)", size=12, bold=True, color=POS))
        # транзистор у центрі
        tcx, tcy = x0 + 170, 200
        sym, sp, gp, dp = pmos_symbol(tcx, tcy)
        f.append(sym)
        # витік до шини
        f.append(line(sp[0], sp[1], sp[0], ry, color=LINE, sw=1.8))
        # стік до навантаження → земля
        ly = 300
        f.append(rect(tcx - 22, dp[1] + 4, 44, 30, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(tcx, dp[1] + 23, "наван-", size=10, color=INK))
        f.append(line(dp[0], dp[1], tcx, dp[1] + 4, color=LINE, sw=1.8))
        gy0 = ly
        f.append(line(tcx, dp[1] + 34, tcx, gy0, color=LINE, sw=1.8))
        # земля
        f.append(line(railx0, gy0, railx1, gy0, color=NEG, sw=2.2))
        f.append(text(x0 + 170, gy0 + 18, "0 В (земля)", size=11, color=NEG))
        # керування затвором
        if gate_low:
            f.append(line(gp[0], gp[1], gp[0] - 36, gp[1], color=FIELD, sw=2.2))
            box, _, _ = textbox(gp[0] - 86, gp[1], "затвор\n≈ 0 В", size=11.5, bold=True,
                                fill="#eef6ef", stroke=FIELD, color=FIELD)
            f.append(box)
            f.append(text(tcx + 64, tcy - 2, "Vgs = 0−12 = −12 В", size=11.5, bold=True, color=FIELD, anchor="start"))
            f.append(text(tcx + 64, tcy + 16, "ON ✓", size=13, bold=True, color=FIELD, anchor="start"))
        else:
            f.append(line(gp[0], gp[1], gp[0] - 36, gp[1], color=POS, sw=2.2))
            box, _, _ = textbox(gp[0] - 88, gp[1], "затвор\n= +12 В", size=11.5, bold=True,
                                fill="#fbeee6", stroke=POS, color=POS)
            f.append(box)
            f.append(text(tcx + 64, tcy - 2, "Vgs = 12−12 = 0 В", size=11.5, bold=True, color=MUTED, anchor="start"))
            f.append(text(tcx + 64, tcy + 16, "OFF", size=13, bold=True, color=MUTED, anchor="start"))

    panel(28, "Затвор піднятий до витоку → замкнено", False, False)
    panel(392, "Затвор стягнутий униз → відкрито", True, True)
    return render(os.path.join(IMG, "pmos-on-top.svg"), W, H, *f)


# ── 2. Реальна схема: NPN перекладає рівень, конденсатор робить плавний пуск ──
def fig_npn_drive():
    W, H = 780, 440
    f = [text(W / 2, 26, "Керування P-ключем з логіки: NPN тягне затвор, RC згладжує пуск", size=15, bold=True)]

    # шина +12 угорі
    railx0, railx1 = 70, 710
    ry = 70
    f.append(line(railx0, ry, railx1, ry, color=POS, sw=2.6))
    f.append(text(railx1 - 4, ry - 8, "+12 В", size=12.5, bold=True, color=POS, anchor="end"))

    # земля внизу
    gy = 392
    f.append(line(railx0, gy, railx1, gy, color=NEG, sw=2.4))
    f.append(text(railx1 - 4, gy + 18, "0 В", size=12, color=NEG, anchor="end"))

    # P-MOSFET праворуч
    tcx, tcy = 560, 190
    sym, sp, gp, dp = pmos_symbol(tcx, tcy)
    f.append(sym)
    f.append(line(sp[0], sp[1], sp[0], ry, color=LINE, sw=1.8))      # витік до +12
    # навантаження від стоку до землі
    f.append(rect(tcx - 34, 300, 68, 36, fill=FILL, stroke=LINE, sw=1.5))
    f.append(mtext(tcx, 316, ["наван-", "таження"], size=10, color=INK, lh=1.25))
    f.append(line(dp[0], dp[1], tcx, 300, color=LINE, sw=1.8))
    f.append(line(tcx, 336, tcx, gy, color=LINE, sw=1.8))

    # вузол затвора G
    gnx = gp[0]
    gny = gp[1]
    # підтягувальний резистор R1 від затвора до +12
    r1x = gnx
    f.append(rect(r1x - 11, 96, 22, 46, fill=BG, stroke=LINE, sw=1.6))
    f.append(line(r1x, ry, r1x, 96, color=LINE, sw=1.8))
    f.append(line(r1x, 142, r1x, gny, color=LINE, sw=1.8))
    f.append(text(r1x + 16, 122, "R1", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(r1x + 16, 138, "10к", size=10.5, color=MUTED, anchor="start"))
    # софт-старт конденсатор Cgs від затвора до витоку (паралельно G–S)
    csx = gnx + 0  # вузол той самий; малюємо праворуч маленьку гілку до витоку
    f.append(line(gnx, gny, gnx + 40, gny, color=LINE, sw=1.6))
    f.append(line(gnx + 40, gny, gnx + 40, gny - 24, color=LINE, sw=1.6))
    # пластини конденсатора
    f.append(line(gnx + 32, gny - 24, gnx + 48, gny - 24, color=LINE, sw=2.4))
    f.append(line(gnx + 32, gny - 32, gnx + 48, gny - 32, color=LINE, sw=2.4))
    f.append(line(gnx + 40, gny - 32, gnx + 40, gny - 50, color=LINE, sw=1.6))
    f.append(line(gnx + 40, gny - 50, sp[0], gny - 50, color=LINE, sw=1.6))
    f.append(line(sp[0], gny - 50, sp[0], sp[1], color=LINE, sw=1.6))
    f.append(text(gnx + 54, gny - 26, "C", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(gnx + 54, gny - 10, "пуск", size=10, color=MUTED, anchor="start"))

    # NPN перекладач ліворуч-знизу
    npx, npy = 300, 250
    # символ NPN: колектор угорі, емітер униз, база ліворуч
    f.append(line(npx, npy - 30, npx, npy + 30, color=INK, sw=2.6))   # вертикальна риска
    f.append(line(npx - 26, npy, npx, npy, color=INK, sw=2.2))         # база
    f.append(line(npx, npy - 22, npx + 22, npy - 36, color=INK, sw=2.2))  # колектор
    f.append(line(npx, npy + 22, npx + 22, npy + 36, color=INK, sw=2.2))  # емітер
    # стрілка емітера (NPN — назовні)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        npx + 22, npy + 36, npx + 12, npy + 28, npx + 18, npy + 24, INK))
    f.append(text(npx + 26, npy - 34, "C", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(npx + 26, npy + 42, "E", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(npx - 30, npy + 4, "B", size=11.5, bold=True, color=INK, anchor="end"))
    f.append(text(npx, npy + 60, "NPN", size=11, color=MUTED))
    # колектор NPN → вузол затвора
    f.append(line(npx + 22, npy - 36, gnx, npy - 36, color=LINE, sw=1.8))
    f.append(line(gnx, npy - 36, gnx, gny, color=LINE, sw=1.8))
    f.append(circle(gnx, gny, 3.2, fill=INK, stroke=INK))   # вузол G
    # емітер NPN → земля
    f.append(line(npx + 22, npy + 36, npx + 22, gy, color=LINE, sw=1.8))
    # база через Rb від логіки
    f.append(rect(150, npy - 11, 46, 22, fill=BG, stroke=LINE, sw=1.6))
    f.append(line(196, npy, npx - 26, npy, color=LINE, sw=1.8))
    f.append(text(173, npy - 16, "Rb", size=11.5, bold=True, color=INK))
    f.append(line(70, npy, 150, npy, color=LINE, sw=1.8))
    box, _, _ = textbox(108, npy, "MCU\nGPIO", size=11, bold=True, fill=FILL, stroke=LINE)
    # перемалюємо вхідну рамку акуратно
    f.append(rect(58, npy - 22, 70, 44, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    f.append(mtext(93, npy - 2, ["MCU", "GPIO"], size=11, bold=True))
    f.append(line(128, npy, 150, npy, color=LINE, sw=1.8))

    # пояснювальні підписи логіки — у вільному верхньому-лівому куті
    lx, ly0 = 70, 120
    f.append(rect(lx - 8, ly0 - 20, 372, 62, fill="#f8fafb", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(lx, ly0, "GPIO = 1 → NPN ON → затвор вниз → P-ключ ON", size=11.5, color=FIELD, anchor="start", bold=True))
    f.append(text(lx, ly0 + 22, "GPIO = 0 → NPN OFF → R1 тягне затвор до +12 → OFF", size=11.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "pmos-npn-drive.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_pmos_on_top()
    fig_npn_drive()
    print("OK: pmos-on-top.svg, pmos-npn-drive.svg")
