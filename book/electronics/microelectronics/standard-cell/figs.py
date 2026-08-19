# -*- coding: utf-8 -*-
"""Фігури до теми «Стандартні комірки (standard cell)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Внутрішня будова стандартної комірки на сітці треків металізації ─────
def fig_cell_structure():
    W, H = 880, 520
    f = [text(W / 2, 28, "Внутрішня топологія стандартної комірки (9-трекова сітка 9T)", size=16, bold=True)]

    cx, cy = W / 2, 260
    cell_w, cell_h = 560, 360
    x0, y0 = cx - cell_w / 2, cy - cell_h / 2

    # Фон комірки (PR Boundary)
    f.append(rect(x0, y0, cell_w, cell_h, fill="#ffffff", stroke="#2c3e50", sw=2.0, rx=4))

    # Сітка треків металізації M1 (9 горизонтальних треків)
    num_tracks = 9
    track_pitch = cell_h / (num_tracks - 1)
    for i in range(num_tracks):
        ty = y0 + i * track_pitch
        f.append(line(x0, ty, x0 + cell_w, ty, color="#e2e8f0", sw=1.0, dash="4,4"))
        # підпис треків ліворуч
        f.append(text(x0 - 15, ty + 4, "T%d" % (8 - i), size=10, color=MUTED, anchor="end"))

    # Підпис сітки треків праворуч
    f.append(text(x0 + cell_w + 15, y0 + cell_h / 2 - 10, "9 треків M1", size=11, color=MUTED, anchor="start", bold=True))
    f.append(text(x0 + cell_w + 15, y0 + cell_h / 2 + 10, "(Track Pitch)", size=11, color=MUTED, anchor="start"))

    # Верхня шина живлення VDD (M1)
    f.append(rect(x0, y0, cell_w, 24, fill="#fdedec", stroke=POS, sw=1.5, rx=0))
    f.append(text(cx, y0 + 16, "Шина живлення VDD (шар Metal 1)", size=12, color=POS, bold=True))

    # Нижня шина живлення VSS (M1)
    f.append(rect(x0, y0 + cell_h - 24, cell_w, 24, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=0))
    f.append(text(cx, y0 + cell_h - 8, "Шина землі VSS (шар Metal 1)", size=12, color=NEG, bold=True))

    # Область n-кишені (n-well) для PMOS (верхня половина)
    well_h = 150
    well_y = y0 + 24
    f.append(rect(x0 + 4, well_y, cell_w - 8, well_h, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=0))
    f.append(text(x0 + 20, well_y + 20, "n-кишеня (N-Well)", size=11, color="#b7950b", bold=True, anchor="start"))

    # Область p-підкладки для NMOS (нижня половина)
    sub_y = well_y + well_h
    sub_h = cell_h - 48 - well_h
    f.append(rect(x0 + 4, sub_y, cell_w - 8, sub_h, fill="#f4f6f7", stroke="#7f8c8d", sw=1.2, rx=0))
    f.append(text(x0 + 20, sub_y + 20, "p-підкладка (P-Substrate)", size=11, color="#515a5a", bold=True, anchor="start"))

    # Межа між n-well та p-substrate (по центру)
    f.append(line(x0 + 4, sub_y, x0 + cell_w - 4, sub_y, color="#e67e22", sw=1.5, dash="6,4"))

    # Активні дифузійні смуги (показані лініями великої товщини)
    pdiff_y = y0 + 95
    f.append(line(x0 + 50, pdiff_y, x0 + cell_w - 50, pdiff_y, color="#fadbd8", sw=60))
    f.append(line(x0 + 50, pdiff_y, x0 + cell_w - 50, pdiff_y, color=POS, sw=1.5))
    f.append(text(x0 + 60, pdiff_y + 4, "p⁺ дифузія (PMOS)", size=11, color=POS, anchor="start", bold=True))

    ndiff_y = y0 + 245
    f.append(line(x0 + 50, ndiff_y, x0 + cell_w - 50, ndiff_y, color="#d4e6f1", sw=60))
    f.append(line(x0 + 50, ndiff_y, x0 + cell_w - 50, ndiff_y, color=NEG, sw=1.5))
    f.append(text(x0 + 60, ndiff_y + 4, "n⁺ дифузія (NMOS)", size=11, color=NEG, anchor="start", bold=True))

    # Полікремнієві затвори (Poly Gates) на фіксованому кроці CPP
    poly_xs = [x0 + 170, x0 + 290, x0 + 410]
    for px in poly_xs:
        f.append(line(px, y0 + 32, px, y0 + cell_h - 32, color="#27ae60", sw=16))
        f.append(line(px, y0 + 32, px, y0 + cell_h - 32, color="#1e8449", sw=1.5))

    # Підпис затворів
    f.append(text(poly_xs[0], y0 + 25, "Затвор A", size=11, color="#1e8449", bold=True))
    f.append(text(poly_xs[1], y0 + 25, "Затвор B", size=11, color="#1e8449", bold=True))
    f.append(text(poly_xs[2], y0 + 25, "Dummy", size=10, color=MUTED))

    # Крок затворів (CPP)
    f.append(line(poly_xs[0], y0 + cell_h - 32, poly_xs[1], y0 + cell_h - 32, color="#1e8449", sw=1.5))
    f.append(line(poly_xs[0], y0 + cell_h - 36, poly_xs[0], y0 + cell_h - 28, color="#1e8449", sw=1.5))
    f.append(line(poly_xs[1], y0 + cell_h - 36, poly_xs[1], y0 + cell_h - 28, color="#1e8449", sw=1.5))
    f.append(text((poly_xs[0] + poly_xs[1]) / 2, y0 + cell_h - 36, "Крок затворів (CPP)", size=10, color="#1e8449", bold=True))

    # Вхідні та вихідні металеві піни M1 на сітці
    # Пін входу A (на треку T5)
    pin_a_x, pin_a_y = poly_xs[0], y0 + 135
    f.append(circle(pin_a_x, pin_a_y, 14, fill="#3498db", stroke="#2980b9", sw=1.5))
    f.append(text(pin_a_x, pin_a_y + 4, "A", size=12, color="#ffffff", bold=True))

    # Пін входу B (на треку T3)
    pin_b_x, pin_b_y = poly_xs[1], y0 + 225
    f.append(circle(pin_b_x, pin_b_y, 14, fill="#3498db", stroke="#2980b9", sw=1.5))
    f.append(text(pin_b_x, pin_b_y + 4, "B", size=12, color="#ffffff", bold=True))

    # Пін виходу Y (на треку T4)
    pin_y_x, pin_y_y = x0 + 475, y0 + 180
    f.append(circle(pin_y_x, pin_y_y, 16, fill="#9b59b6", stroke="#8e44ad", sw=1.5))
    f.append(text(pin_y_x, pin_y_y + 4, "Y", size=12, color="#ffffff", bold=True))

    # Виноска для пінів на перетині сітки
    f.append(text(pin_y_x, pin_y_y - 24, "Вихідний пін (M1)", size=11, color="#8e44ad", bold=True))
    f.append(text((pin_a_x + pin_b_x) / 2, pin_a_y - 24, "Вхідні піни A, B на сітці треків", size=11, color="#2980b9", bold=True))

    # Межі комірки (PR Boundary) підпис
    f.append(text(cx, y0 + cell_h + 20, "Межа комірки (Cell Boundary / PR Boundary) кратна кроку сітки трасування", size=11, color=INK))

    render(os.path.join(IMG, "standard-cell-structure.svg"), W, H, *f)


# ── 2. Розміщення комірок у регулярні ряди з дзеркальним чергуванням ─────────
def fig_row_placement():
    W, H = 880, 520
    f = [text(W / 2, 28, "Розміщення в ряди (Placement Rows) зі спільними шинами VDD/VSS", size=16, bold=True)]

    x0, y0 = 60, 55
    rw, rh = 760, 120

    # Ряд 0 (Орієнтація R0 — нормальна)
    f.append(rect(x0, y0, rw, rh, fill="#ffffff", stroke="#95a5a6", sw=1.5, rx=0))
    f.append(rect(x0, y0, rw, 16, fill="#fdedec", stroke=POS, sw=1.2, rx=0))
    f.append(text(x0 + 10, y0 + 12, "VDD (M1)", size=11, color=POS, bold=True, anchor="start"))
    f.append(rect(x0, y0 + rh - 16, rw, 16, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=0))
    f.append(text(x0 + 10, y0 + rh - 4, "VSS (M1)", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 - 15, y0 + rh / 2 + 4, "Ряд 0 (R0)", size=12, color=INK, bold=True, anchor="end"))

    # Комірки у ряді 0
    # Endcap ліворуч
    f.append(fitbox(x0 + 60, y0 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))
    # Tap cell
    f.append(fitbox(x0 + 105, y0 + 16, 45, rh - 32, "Well\nTap", size=10, fill="#fcf3cf", stroke="#f39c12", bold=True))
    # Logic cell 1: NAND2_X1
    f.append(fitbox(x0 + 155, y0 + 16, 110, rh - 32, "NAND2_X1\n(Логіка)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    # Logic cell 2: DFF_X2
    f.append(fitbox(x0 + 270, y0 + 16, 170, rh - 32, "DFF_X2 (Тригер)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    # Decap cell
    f.append(fitbox(x0 + 445, y0 + 16, 75, rh - 32, "Decap\n(C_decap)", size=10, fill="#e8f8f5", stroke="#1abc9c", bold=True))
    # Logic cell 3: INV_X4
    f.append(fitbox(x0 + 525, y0 + 16, 85, rh - 32, "INV_X4\n(Буфер)", size=11, fill="#ebf5fb", stroke="#3498db", bold=True))
    # Filler cell
    f.append(fitbox(x0 + 615, y0 + 16, 80, rh - 32, "Filler\n(Наповнювач)", size=10, fill="#eaeded", stroke="#bdc3c7"))
    # Endcap праворуч
    f.append(fitbox(x0 + 700, y0 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))

    # Ряд 1 (Орієнтація MX — віддзеркалена по X)
    # Сусідній ряд стикується до VSS ряду 0, утворюючи спільну подвійну шину VSS!
    y1 = y0 + rh
    f.append(rect(x0, y1, rw, rh, fill="#fafafa", stroke="#95a5a6", sw=1.5, rx=0))
    # Спільна шина VSS посередині
    f.append(rect(x0, y1, rw, 16, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=0))
    f.append(text(x0 + 10, y1 + 12, "Спільна шина VSS (GND)", size=11, color=NEG, bold=True, anchor="start"))
    # Нижня шина VDD ряду 1
    f.append(rect(x0, y1 + rh - 16, rw, 16, fill="#fdedec", stroke=POS, sw=1.2, rx=0))
    f.append(text(x0 + 10, y1 + rh - 4, "VDD (M1)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(x0 - 15, y1 + rh / 2 + 4, "Ряд 1 (MX)", size=12, color=INK, bold=True, anchor="end"))

    # Комірки у ряді 1
    f.append(fitbox(x0 + 60, y1 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))
    f.append(fitbox(x0 + 105, y1 + 16, 140, rh - 32, "NOR2_X1\n(Логіка)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    f.append(fitbox(x0 + 250, y1 + 16, 65, rh - 32, "Filler", size=10, fill="#eaeded", stroke="#bdc3c7"))
    f.append(fitbox(x0 + 320, y1 + 16, 190, rh - 32, "MUX2_X2 (Мультиплексор)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    f.append(fitbox(x0 + 515, y1 + 16, 45, rh - 32, "Well\nTap", size=10, fill="#fcf3cf", stroke="#f39c12", bold=True))
    f.append(fitbox(x0 + 565, y1 + 16, 130, rh - 32, "XOR2_X1\n(Логіка)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    f.append(fitbox(x0 + 700, y1 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))

    # Ряд 2 (Орієнтація R0 — знову нормальна)
    y2 = y1 + rh
    f.append(rect(x0, y2, rw, rh, fill="#ffffff", stroke="#95a5a6", sw=1.5, rx=0))
    # Спільна шина VDD між рядом 1 і рядом 2
    f.append(rect(x0, y2, rw, 16, fill="#fdedec", stroke=POS, sw=1.2, rx=0))
    f.append(text(x0 + 10, y2 + 12, "Спільна шина VDD (Power)", size=11, color=POS, bold=True, anchor="start"))
    f.append(rect(x0, y2 + rh - 16, rw, 16, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=0))
    f.append(text(x0 + 10, y2 + rh - 4, "VSS (M1)", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 - 15, y2 + rh / 2 + 4, "Ряд 2 (R0)", size=12, color=INK, bold=True, anchor="end"))

    # Комірки у ряді 2
    f.append(fitbox(x0 + 60, y2 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))
    f.append(fitbox(x0 + 105, y2 + 16, 180, rh - 32, "AOI22_X1 (Складений вентиль)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True))
    f.append(fitbox(x0 + 290, y2 + 16, 75, rh - 32, "Decap", size=10, fill="#e8f8f5", stroke="#1abc9c", bold=True))
    f.append(fitbox(x0 + 370, y2 + 16, 120, rh - 32, "CLKBUF_X4\n(Тактовий)", size=11, fill="#f4ecf7", stroke="#8e44ad", bold=True))
    f.append(fitbox(x0 + 495, y2 + 16, 105, rh - 32, "Filler", size=10, fill="#eaeded", stroke="#bdc3c7"))
    f.append(fitbox(x0 + 605, y2 + 16, 90, rh - 32, "AND2_X1", size=11, fill="#ebf5fb", stroke="#3498db", bold=True))
    f.append(fitbox(x0 + 700, y2 + 16, 40, rh - 32, "End-\ncap", size=10, fill="#d5dbdb", stroke="#7f8c8d", bold=True))

    # Пояснювальний підпис унизу
    f.append(text(W / 2, y2 + rh + 28, "Чергування орієнтацій R0 / MX зливає сусідні шини живлення та усуває зазори між кишенями", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "cell-row-placement.svg"), W, H, *f)


# ── 3. Сила приводу та мультипорогові транзистори (Drive Strength & Multi-Vt)
def fig_drive_multivt():
    W, H = 880, 480
    f = [text(W / 2, 28, "Параметри бібліотек: сила приводу (Drive Strength) та пороги Multi-Vt", size=16, bold=True)]

    # Ліва панель: Сила приводу (Drive Strength)
    lx, ly, lw, lh = 40, 55, 380, 380
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 25, "Сила приводу (Drive Strength: 1X, 2X, 4X)", size=14, bold=True, color="#2980b9"))

    # Порівняння X1, X2, X4
    # X1
    y_x1 = ly + 50
    f.append(rect(lx + 20, y_x1, lw - 40, 65, fill="#ebf5fb", stroke="#3498db", sw=1.2, rx=4))
    f.append(text(lx + 35, y_x1 + 22, "INV_X1 (1 палець / 2 fins)", size=12, bold=True, color="#1b4f72", anchor="start"))
    f.append(text(lx + 35, y_x1 + 42, "C_in = 1.2 fF · R_on = 4.8 кОм · t_pd = 18 пс (@ 5 fF)", size=11, color=MUTED, anchor="start"))
    f.append(line(lx + 270, y_x1 + 15, lx + 270, y_x1 + 50, color="#3498db", sw=3))

    # X2
    y_x2 = y_x1 + 75
    f.append(rect(lx + 20, y_x2, lw - 40, 65, fill="#ebf5fb", stroke="#3498db", sw=1.2, rx=4))
    f.append(text(lx + 35, y_x2 + 22, "INV_X2 (2 пальці / 4 fins)", size=12, bold=True, color="#1b4f72", anchor="start"))
    f.append(text(lx + 35, y_x2 + 42, "C_in = 2.3 fF · R_on = 2.4 кОм · t_pd = 12 пс (@ 10 fF)", size=11, color=MUTED, anchor="start"))
    f.append(line(lx + 265, y_x2 + 15, lx + 265, y_x2 + 50, color="#3498db", sw=3))
    f.append(line(lx + 275, y_x2 + 15, lx + 275, y_x2 + 50, color="#3498db", sw=3))

    # X4
    y_x4 = y_x2 + 75
    f.append(rect(lx + 20, y_x4, lw - 40, 65, fill="#ebf5fb", stroke="#3498db", sw=1.2, rx=4))
    f.append(text(lx + 35, y_x4 + 22, "INV_X4 (4 пальці / 8 fins)", size=12, bold=True, color="#1b4f72", anchor="start"))
    f.append(text(lx + 35, y_x4 + 42, "C_in = 4.6 fF · R_on = 1.2 кОм · t_pd = 9 пс (@ 20 fF)", size=11, color=MUTED, anchor="start"))
    for k in range(4):
        f.append(line(lx + 260 + k * 8, y_x4 + 15, lx + 260 + k * 8, y_x4 + 50, color="#3498db", sw=2.5))

    # Підсумок зліва
    f.append(fitbox(lx + 20, ly + 285, lw - 40, 80,
                    "Більший розмір транзисторів:\n↓ R_on (швидший заряд навантаження C_load)\n↑ C_in (більше навантажує попередній каскад)",
                    size=11, fill="#f4f6f7", stroke="#bdc3c7"))

    # Права панель: Multi-Vt (HVT, SVT, LVT, eLVT)
    rx, ry, rw, rh = 460, 55, 380, 380
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 25, "Мультипорогові транзистори (Multi-Vt)", size=14, bold=True, color="#8e44ad"))

    # Таблиця Multi-Vt
    ty = ry + 50
    # HVT
    f.append(rect(rx + 20, ty, rw - 40, 60, fill="#fcf3cf", stroke="#f1c40f", sw=1.2, rx=4))
    f.append(text(rx + 35, ty + 20, "HVT (High Vt) — високий поріг (~0.45 В)", size=12, bold=True, color="#7d6608", anchor="start"))
    f.append(text(rx + 35, ty + 40, "Затримка: +35% · Струм витоку: 0.1× (базовий)", size=11, color="#7d6608", anchor="start"))

    # SVT
    ty2 = ty + 68
    f.append(rect(rx + 20, ty2, rw - 40, 60, fill="#e8f8f5", stroke="#1abc9c", sw=1.2, rx=4))
    f.append(text(rx + 35, ty2 + 20, "SVT (Standard Vt) — стандартний поріг (~0.35 В)", size=12, bold=True, color="#0e6251", anchor="start"))
    f.append(text(rx + 35, ty2 + 40, "Затримка: базова (1.0×) · Струм витоку: 1.0×", size=11, color="#0e6251", anchor="start"))

    # LVT
    ty3 = ty2 + 68
    f.append(rect(rx + 20, ty3, rw - 40, 60, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    f.append(text(rx + 35, ty3 + 20, "LVT (Low Vt) — низький поріг (~0.25 В)", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(rx + 35, ty3 + 40, "Затримка: −25% (швидкий) · Струм витоку: 8×–12×", size=11, color=POS, anchor="start"))

    # Підсумок справа
    f.append(fitbox(rx + 20, ry + 265, rw - 40, 100,
                    "Стратегія P&R оптимізації:\n• Критичні шляхи (Timing Critical): LVT / eLVT\n• Некритичні шляхи (Non-critical Slack): HVT\nРезультат: макс. частота за мін. витоку (Leakage Recovery)",
                    size=11, fill="#fdfefe", stroke="#8e44ad"))

    render(os.path.join(IMG, "drive-strength-multivt.svg"), W, H, *f)


# ── 4. Двовимірна таблиця NLDM та інтерполяція затримки ───────────────────────
def fig_timing_tables():
    W, H = 880, 480
    f = [text(W / 2, 28, "Таблична модель затримок NLDM (2D Lookup Table у Liberty .lib)", size=16, bold=True)]

    # Ліва частина: Графік сигналу і затримки (Propagation Delay & Slew)
    gx, gy, gw, gh = 50, 60, 360, 370
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(gx + gw / 2, gy + 25, "Визначення затримки та крутості", size=13, bold=True, color=INK))

    # Осі
    ax_x, ax_y = gx + 40, gy + gh - 45
    f.append(line(ax_x, ax_y, ax_x + 280, ax_y, color=LINE, sw=1.5))
    f.append(line(ax_x, ax_y, ax_x, ax_y - 250, color=LINE, sw=1.5))
    f.append(text(ax_x + 280, ax_y + 20, "Час (t)", size=11, color=INK, anchor="end"))
    f.append(text(ax_x - 10, ax_y - 250, "Напруга (V)", size=11, color=INK, anchor="end"))

    # Рівні напруги
    f.append(line(ax_x, ax_y - 220, ax_x + 270, ax_y - 220, color="#bdc3c7", sw=1.0, dash="3,3"))
    f.append(text(ax_x - 8, ax_y - 220, "VDD", size=10, color=MUTED, anchor="end"))
    f.append(line(ax_x, ax_y - 110, ax_x + 270, ax_y - 110, color="#bdc3c7", sw=1.0, dash="3,3"))
    f.append(text(ax_x - 8, ax_y - 110, "50%", size=10, color=MUTED, anchor="end"))

    # Крива входу (наростання)
    f.append(line(ax_x + 20, ax_y, ax_x + 60, ax_y, color="#2980b9", sw=2.2))
    f.append(line(ax_x + 60, ax_y, ax_x + 110, ax_y - 220, color="#2980b9", sw=2.2))
    f.append(line(ax_x + 110, ax_y - 220, ax_x + 160, ax_y - 220, color="#2980b9", sw=2.2))
    f.append(text(ax_x + 70, ax_y - 180, "Вхід (A)", size=11, color="#2980b9", bold=True, anchor="start"))

    # Крива виходу (спад)
    f.append(line(ax_x + 20, ax_y - 220, ax_x + 105, ax_y - 220, color=POS, sw=2.2))
    f.append(line(ax_x + 105, ax_y - 220, ax_x + 195, ax_y, color=POS, sw=2.2))
    f.append(line(ax_x + 195, ax_y, ax_x + 260, ax_y, color=POS, sw=2.2))
    f.append(text(ax_x + 190, ax_y - 180, "Вихід (Y)", size=11, color=POS, bold=True, anchor="start"))

    # Стрілка затримки t_pd (між точками 50% входу та 50% виходу)
    t_in_50 = ax_x + 85
    t_out_50 = ax_x + 150
    f.append(line(t_in_50, ax_y - 110, t_in_50, ax_y - 50, color="#27ae60", sw=1.2, dash="2,2"))
    f.append(line(t_out_50, ax_y - 110, t_out_50, ax_y - 50, color="#27ae60", sw=1.2, dash="2,2"))
    f.append(line(t_in_50, ax_y - 55, t_out_50, ax_y - 55, color="#27ae60", sw=1.8))
    f.append(text((t_in_50 + t_out_50) / 2, ax_y - 62, "Затримка t_pd", size=11, color="#27ae60", bold=True))

    # Підпис крутості фронту (Slew)
    f.append(text(gx + gw / 2, gy + gh - 15, "Крутість фронту Slew: час переходу 10% ↔ 90% (або 20% ↔ 80%)", size=10, color=MUTED))

    # Права частина: 2D Таблиця NLDM (Slew vs C_load)
    tx, ty, tw, th = 440, 60, 400, 370
    f.append(rect(tx, ty, tw, th, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(tx + tw / 2, ty + 25, "Таблиця затримки cell_fall(Slew, C_load)", size=13, bold=True, color=INK))

    # Осі таблиці
    f.append(text(tx + tw / 2 + 30, ty + 50, "Ємність навантаження C_load (fF) →", size=11, color="#2980b9", bold=True))
    f.append(text(tx + 25, ty + 100, "Вхідний\nSlew (пс)\n↓", size=10, color=POS, bold=True))

    # Сітка таблиці
    cols = ["2 fF", "8 fF", "25 fF", "80 fF"]
    rows = ["10 пс", "30 пс", "90 пс", "250 пс"]
    matrix = [
        ["12 пс", "18 пс", "32 пс", "78 пс"],
        ["16 пс", "23 пс", "38 пс", "85 пс"],
        ["24 пс", "31 пс", "49 пс", "98 пс"],
        ["42 пс", "51 пс", "72 пс", "125 пс"]
    ]

    ox, oy = tx + 75, ty + 75
    cw, ch = 72, 35

    # Заголовки стовпців
    for j, c in enumerate(cols):
        f.append(rect(ox + j * cw, oy, cw, ch, fill="#ebf5fb", stroke="#aed6f1", sw=1.0, rx=0))
        f.append(text(ox + j * cw + cw / 2, oy + ch / 2 + 4, c, size=11, color="#1b4f72", bold=True))

    # Рядки таблиці
    for i, r in enumerate(rows):
        # Заголовок рядка
        f.append(rect(ox - 65, oy + (i + 1) * ch, 65, ch, fill="#fdedec", stroke="#f5b7b1", sw=1.0, rx=0))
        f.append(text(ox - 32, oy + (i + 1) * ch + ch / 2 + 4, r, size=11, color=POS, bold=True))
        # Комірки даних
        for j in range(4):
            val = matrix[i][j]
            is_highlight = (i == 1 and j == 1)
            fill_col = "#e8f8f5" if is_highlight else "#ffffff"
            stroke_col = "#27ae60" if is_highlight else "#d5dbdb"
            f.append(rect(ox + j * cw, oy + (i + 1) * ch, cw, ch, fill=fill_col, stroke=stroke_col, sw=1.2, rx=0))
            f.append(text(ox + j * cw + cw / 2, oy + (i + 1) * ch + ch / 2 + 4, val, size=11, color=INK))

    # Виноска про білінійну інтерполяцію
    f.append(fitbox(tx + 20, ty + 245, tw - 40, 105,
                    "Білінійна інтерполяція в Liberty:\nДля довільної пари (S_in, C_L), що потрапляє\nміж вузлами сітки, STA-таймер обчислює затримку\nчерез 4 сусідні точки зваженим усередненням.",
                    size=11, fill="#fdfefe", stroke="#bdc3c7"))

    render(os.path.join(IMG, "timing-tables-interpolation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cell_structure()
    fig_row_placement()
    fig_drive_multivt()
    fig_timing_tables()
    print("Всі фігури згенеровано успішно.")
