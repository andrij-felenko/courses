# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми 'vymiriuvach-napruzhenosti-polia'."""

import os
import sys

# Підключаємо svgkit з scripts/ (4 рівні вгору від root/hw/hw-sensing/vymiriuvach-napruzhenosti-polia)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_isotropic_probe_geometry():
    """Конструкція триосьового ізотропного зонда E-поля."""
    w, h = 820, 430
    frags = []

    frags.append(text(w / 2, 26, "Конструкція триосьового ізотропного зонда напруженості E-поля", size=16, bold=True))

    # Ліва частина: 3D-ізометрія / ортогональні диполі в діелектричній сфері
    cx, cy, r_radome = 230, 215, 125

    # Діелектричний захисний ковпак (радом)
    frags.append(circle(cx, cy, r_radome, fill="#f8fafc", stroke="#94a3b8", sw=2))
    frags.append(text(cx, cy - r_radome + 22, "Діелектрична сфера (радом)", size=11, color=MUTED, italic=True))

    # Центр датчика
    frags.append(circle(cx, cy, 5, fill=INK, stroke=INK))

    # Вісь X (горизонтальний диполь - червоний)
    frags.append(line(cx - 95, cy, cx - 12, cy, color=POS, sw=3))
    frags.append(line(cx + 12, cy, cx + 95, cy, color=POS, sw=3))
    frags.append(circle(cx - 12, cy, 3, fill=POS, stroke=POS))
    frags.append(circle(cx + 12, cy, 3, fill=POS, stroke=POS))
    frags.append(textbox(cx + 105, cy - 14, "Диполь X", size=11, pad=4, fill="#fee2e2", stroke=POS, bold=True)[0])

    # Вісь Y (вертикальний диполь - синій)
    frags.append(line(cx, cy - 95, cx, cy - 12, color=NEG, sw=3))
    frags.append(line(cx, cy + 12, cx, cy + 95, color=NEG, sw=3))
    frags.append(circle(cx, cy - 12, 3, fill=NEG, stroke=NEG))
    frags.append(circle(cx, cy + 12, 3, fill=NEG, stroke=NEG))
    frags.append(textbox(cx + 18, cy - 105, "Диполь Y", size=11, pad=4, fill="#dbeafe", stroke=NEG, bold=True)[0])

    # Вісь Z (діагональний / ортогональний диполь - зелений)
    frags.append(line(cx - 65, cy + 65, cx - 10, cy + 10, color=FIELD, sw=3))
    frags.append(line(cx + 10, cy - 10, cx + 65, cy - 65, color=FIELD, sw=3))
    frags.append(circle(cx - 10, cy + 10, 3, fill=FIELD, stroke=FIELD))
    frags.append(circle(cx + 10, cy - 10, 3, fill=FIELD, stroke=FIELD))
    frags.append(textbox(cx - 85, cy + 85, "Диполь Z", size=11, pad=4, fill="#dcfce7", stroke=FIELD, bold=True)[0])

    # Детекторний діод Шотткі в центрі
    frags.append(rect(cx - 10, cy - 6, 20, 12, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(cx, cy + 3, "D", size=9, bold=True, color="#854d0e"))

    # Високоомні лінії зв'язку (резистивні провідники до ручки зонда)
    frags.append(line(cx, cy + 95, cx, cy + 175, color="#64748b", sw=1.8, dash="4,3"))
    frags.append(line(cx - 6, cy + 95, cx - 6, cy + 175, color="#64748b", sw=1.8, dash="4,3"))
    frags.append(text(cx + 10, cy + 160, "Високоомні лінії (100 кОм/м)", size=10, color=MUTED, anchor="start"))

    # Права частина: ключові конструктивні вузли та математика складання
    rx_start = 450
    cards = [
        ("Електрично короткі диполі (l << λ)",
         "Довжина стрижнів 8–15 мм забезпечує сталий\nємнісний імпеданс і відсутність паразитного\nрезонансу до частот 3–6 ГГц.",
         "#f8fafc", "#cbd5e1"),
        ("Діоди Шотткі прямо в точці збудження",
         "ВЧ сигнал детектується на клемах диполя.\nУ ручку зонда передається лише постійна напруга\nV_DC, що усуває ВЧ втрати в кабелі.",
         "#fefce8", "#eab308"),
        ("Резистивні лінії відведення сигналу",
         "Вуглецеві або ніхромові доріжки з опором\n~100 кОм/м прозорі для ЕМ хвилі й не спотворюють\nвимірюване поле навколо диполів.",
         "#f0fdf4", "#22c55e"),
    ]

    card_y = 55
    for title_c, desc_c, bg_c, stroke_c in cards:
        frags.append(rect(rx_start, card_y, 340, 78, fill=bg_c, stroke=stroke_c, sw=1.5, rx=6))
        frags.append(text(rx_start + 14, card_y + 20, title_c, size=12, bold=True, anchor="start"))
        lines = desc_c.split("\n")
        for idx_l, line_str in enumerate(lines):
            frags.append(text(rx_start + 14, card_y + 38 + idx_l * 16, line_str, size=10.5, color=INK, anchor="start"))
        card_y += 88

    # Нижня підсумкова плашка: формула просторового складання
    b_formula, _, _ = textbox(rx_start + 170, 355,
                              "Ізотропна напруженість: E_total = √(E_x² + E_y² + E_z²)\nГустина потоку енергії: S_total = E_total² / Z_0  (Z_0 ≈ 377 Ом)",
                              size=12, pad=10, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b_formula)

    render(os.path.join(IMG_DIR, "isotropic-probe-geometry.svg"), w, h, *frags)


def fig_detector_types_transfer():
    """Порівняння передавальних характеристик ВЧ детекторів поля."""
    w, h = 840, 390
    frags = []

    frags.append(text(w / 2, 26, "Характеристики детектування ВЧ сигналу: діодний, логарифмічний та True RMS", size=16, bold=True))

    col_w = 250
    gap = 22
    start_x = (w - (3 * col_w + 2 * gap)) / 2

    detectors = [
        ("Діодний (Square-Law)",
         "Zero-Bias Schottky",
         "V_out ∝ V_RF² (низький рівень)\nV_out ∝ V_RF (піковий режим)",
         "Діапазон: ~30-40 дБ\nЧутливий до пік-фактора\nПростий, пасивний",
         POS, "#fef2f2", 0),
        ("Логарифмічний (Log Amp)",
         "AD8313 / AD8318",
         "V_out = −Slope · (P_in − P_0)\nВихід лінійний у дБм (мВ/дБ)",
         "Діапазон: 60–70 дБ\nЧастота: 1 МГц – 8 ГГц\nПомилка на шумі/OFDM ~1–3 дБ",
         NEG, "#eff6ff", 1),
        ("Справжнє СКЗ (True RMS)",
         "AD8361 / AD8362 / LTC5508",
         "V_out ∝ √( 1/T ∫ V_RF²(t) dt )\nНезмінний від форми сигналу",
         "Діапазон: 40–60 дБ\nТочний для 5G NR, LTE, GSM\nІнтегрує потужність у часі",
         FIELD, "#f0fdf4", 2),
    ]

    for idx, (name_d, chip_d, math_d, feat_d, color_d, bg_d, mode) in enumerate(detectors):
        cx = start_x + idx * (col_w + gap)
        cy = 55
        frags.append(rect(cx, cy, col_w, 310, fill=bg_d, stroke="#cbd5e1", sw=1.5, rx=6))

        # Заголовок картки
        frags.append(text(cx + col_w / 2, cy + 22, name_d, size=13, bold=True, color=color_d))
        frags.append(text(cx + col_w / 2, cy + 38, chip_d, size=10.5, color=MUTED, italic=True))

        # Графік характеристики V_out vs P_in
        gx = cx + 24
        gy = cy + 56
        gw = col_w - 48
        gh = 100

        # Осі графіка
        frags.append(line(gx, gy + gh, gx + gw, gy + gh, color="#94a3b8", sw=1.2))
        frags.append(line(gx, gy, gx, gy + gh, color="#94a3b8", sw=1.2))
        frags.append(text(gx + gw - 6, gy + gh + 14, "P_in (дБм)", size=9.5, color=MUTED))
        frags.append(text(gx + 16, gy + 10, "V_out", size=9.5, color=MUTED))

        if mode == 0:
            # Квадратична крива знизу, що переходить у лінійну
            frags.append(line(gx + 5, gy + gh - 4, gx + 35, gy + gh - 15, color=POS, sw=2))
            frags.append(line(gx + 35, gy + gh - 15, gx + 75, gy + gh - 45, color=POS, sw=2))
            frags.append(line(gx + 75, gy + gh - 45, gx + gw - 10, gy + 15, color=POS, sw=2))
            frags.append(text(gx + 40, gy + gh - 26, "Квадратична", size=9, color=POS))
            frags.append(text(gx + gw - 25, gy + 28, "Лінійна", size=9, color=POS))
        elif mode == 1:
            # Пряма лінія спаду для логарифмічного детектора (slope < 0)
            frags.append(line(gx + 10, gy + 15, gx + gw - 15, gy + gh - 15, color=NEG, sw=2))
            frags.append(text(gx + gw / 2 + 10, gy + 45, "V_out ~ −k · P_in", size=9.5, bold=True, color=NEG))
        elif mode == 2:
            # Пряма зростання (лінійна за потужністю або RMS напругою)
            frags.append(line(gx + 10, gy + gh - 15, gx + gw - 15, gy + 15, color=FIELD, sw=2))
            frags.append(text(gx + gw / 2 - 10, gy + 45, "V_out ~ P_RMS", size=9.5, bold=True, color=FIELD))

        # Блок математики
        frags.append(rect(cx + 10, cy + 180, col_w - 20, 48, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        lines_m = math_d.split("\n")
        frags.append(text(cx + col_w / 2, cy + 198, lines_m[0], size=10, bold=True))
        frags.append(text(cx + col_w / 2, cy + 214, lines_m[1], size=9.5, color=MUTED))

        # Особливості застосування
        lines_f = feat_d.split("\n")
        for i_f, l_f in enumerate(lines_f):
            frags.append(text(cx + 16, cy + 248 + i_f * 18, "• " + l_f, size=10, anchor="start", color=INK))

    render(os.path.join(IMG_DIR, "detector-types-transfer.svg"), w, h, *frags)


def fig_field_probe_signal_chain():
    """Повна структурна схема вимірювача напруженості поля."""
    w, h = 860, 390
    frags = []

    frags.append(text(w / 2, 26, "Тракт вимірювання та цифрової обробки напруженості поля", size=16, bold=True))

    # Верхній ряд: Апаратні блоки (зліва направо)
    blocks = [
        ("Триосьовий зонд\n(X, Y, Z диполі +\nдіоди Шотткі)", 40, 65, 130, 85, "#fef2f2", POS),
        ("Високоомний\nбуфер / ПУ\n(3 канали)", 210, 65, 115, 85, "#f8fafc", "#64748b"),
        ("3-канальний\nTrue RMS / Log\nдетектор (AD8318)", 365, 65, 135, 85, "#eff6ff", NEG),
        ("Прецизійний\n24-бітний АЦП\n(диференційний)", 540, 65, 125, 85, "#fefce8", "#ca8a04"),
        ("Мікроконтролер\n(STM32 / ESP32)\nDSP обробка", 705, 65, 120, 85, "#f0fdf4", FIELD),
    ]

    for label, bx, by, bw, bh, bg_c, stroke_c in blocks:
        frags.append(fitbox(bx, by, bw, bh, label, size=11.5, pad=6, fill=bg_c, stroke=stroke_c, sw=1.8, bold=True))

    # Стрілки між блоками
    frags.append(arrow(170, 107, 210, 107, color=LINE, sw=2))
    frags.append(arrow(325, 107, 365, 107, color=LINE, sw=2))
    frags.append(arrow(500, 107, 540, 107, color=LINE, sw=2))
    frags.append(arrow(665, 107, 705, 107, color=LINE, sw=2))

    # Підписи під стрілками
    frags.append(text(190, 96, "V_x,y,z", size=9.5, color=MUTED))
    frags.append(text(345, 96, "Аналог", size=9.5, color=MUTED))
    frags.append(text(520, 96, "V_det", size=9.5, color=MUTED))
    frags.append(text(685, 96, "SPI / I2C", size=9.5, color=MUTED))

    # Нижній ряд: Програмні модулі всередині мікроконтролера
    frags.append(rect(40, 185, 785, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(55, 206, "Програмний конвеєр обробки даних (Firmware Processing Pipeline):", size=12, bold=True, anchor="start"))

    dsp_steps = [
        ("1. Калібрування\nі лінеаризація", "Компенсація темп. дрейфу\nта корекція АХ детектора\nчерез поліноми або LUT", 60, 220, 160, 120, "#ffffff"),
        ("2. Антенний фактор\nAF(f) та E_x,y,z", "Множення на AF(f):\nE_k = V_k · 10^(AF/20)\nВрахування частоти джерела", 250, 220, 165, 120, "#ffffff"),
        ("3. Просторовий\nвектор E_total", "Розрахунок модуля:\nE_tot = √(E_x² + E_y² + E_z²)\nГустина S = E_tot² / 377", 445, 220, 165, 120, "#ffffff"),
        ("4. Усереднення й\nнорма ICNIRP", "Ковзне вікно 6 хв (RMS)\nПорівняння з лімітом ГДР\nТривога перевищення %", 640, 220, 165, 120, "#ffffff"),
    ]

    for title_s, desc_s, sx, sy, sw_b, sh_b, bg_s in dsp_steps:
        frags.append(rect(sx, sy, sw_b, sh_b, fill=bg_s, stroke="#94a3b8", sw=1.2, rx=5))
        frags.append(text(sx + sw_b / 2, sy + 18, title_s.split("\n")[0], size=11, bold=True, color=INK))
        frags.append(text(sx + sw_b / 2, sy + 32, title_s.split("\n")[1], size=10.5, bold=True, color=INK))
        lines_d = desc_s.split("\n")
        for i_d, l_d in enumerate(lines_d):
            frags.append(text(sx + sw_b / 2, sy + 56 + i_d * 16, l_d, size=9.5, color=MUTED))

    # Стрілки між DSP етапами
    frags.append(arrow(220, 280, 250, 280, color=FIELD, sw=2))
    frags.append(arrow(415, 280, 445, 280, color=FIELD, sw=2))
    frags.append(arrow(610, 280, 640, 280, color=FIELD, sw=2))

    render(os.path.join(IMG_DIR, "field-probe-signal-chain.svg"), w, h, *frags)


def fig_safety_limits_curve():
    """Норми безпеки електромагнітного поля за стандартами ICNIRP 2020 / IEEE C95.1."""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 26, "Гранично допустимі рівні напруженості поля E (ICNIRP 2020 Guidelines)", size=16, bold=True))

    # Область графіка
    gx = 85
    gy = 60
    gw = 680
    gh = 260

    # Сітка та фон графіка
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))

    # Частотні мітки на осі X (логарифмічна шкала від 100 кГц до 300 ГГц)
    freq_ticks = [
        ("100 кГц", 0.0),
        ("1 МГц", 0.14),
        ("10 МГц", 0.28),
        ("30 МГц", 0.38),
        ("400 МГц", 0.55),
        ("2 ГГц", 0.70),
        ("10 ГГц", 0.82),
        ("100 ГГц", 0.95),
        ("300 ГГц", 1.0),
    ]

    for lbl, frac in freq_ticks:
        tx = gx + frac * gw
        frags.append(line(tx, gy, tx, gy + gh, color="#f1f5f9", sw=1))
        frags.append(line(tx, gy + gh, tx, gy + gh + 5, color="#64748b", sw=1))
        frags.append(text(tx, gy + gh + 18, lbl, size=9.5, color=MUTED))

    # Рівні поля на осі Y (напруженість E, В/м)
    y_ticks = [
        ("614 В/м", 0.08),
        ("200 В/м", 0.28),
        ("87 В/м", 0.48),
        ("28 В/м", 0.75),
        ("10 В/м", 0.92),
    ]

    for lbl, frac in y_ticks:
        ty = gy + frac * gh
        frags.append(line(gx, ty, gx + gw, ty, color="#f1f5f9", sw=1))
        frags.append(line(gx - 5, ty, gx, ty, color="#64748b", sw=1))
        frags.append(text(gx - 10, ty + 4, lbl, size=9.5, color=MUTED, anchor="end"))

    # Підписи осей
    frags.append(text(gx + gw / 2, gy + gh + 38, "Частота електромагнітного поля (f)", size=11, bold=True))
    frags.append(text(gx - 55, gy + gh / 2, "E (В/м)", size=11, bold=True))

    # Зона резонансу людського тіла (30 МГц – 400 МГц) - виділення
    res_x1 = gx + 0.38 * gw
    res_x2 = gx + 0.55 * gw
    frags.append(rect(res_x1, gy, res_x2 - res_x1, gh, fill="#fee2e2", stroke="none"))
    frags.append(text((res_x1 + res_x2) / 2, gy + 30, "Резонанс тіла людини (максимальне поглинання)", size=9.5, color=POS, bold=True))

    # Крива 1: Професійне опромінення (Occupational / Workers) - Синя
    # Точки: (100к: 614), (1М: 614), (30М: 614->87), (400М: 61), (2Г: 137), (300Г: 137)
    pts_occ = [
        (gx + 0.0 * gw, gy + 0.08 * gh),
        (gx + 0.14 * gw, gy + 0.08 * gh),
        (gx + 0.38 * gw, gy + 0.48 * gh),
        (gx + 0.55 * gw, gy + 0.58 * gh),
        (gx + 0.70 * gw, gy + 0.40 * gh),
        (gx + 1.0 * gw, gy + 0.40 * gh),
    ]
    for i in range(len(pts_occ) - 1):
        frags.append(line(pts_occ[i][0], pts_occ[i][1], pts_occ[i+1][0], pts_occ[i+1][1], color=NEG, sw=2.5))

    # Крива 2: Населення (General Public) - Червона
    # Точки: (100к: 200), (1М: 87), (30М: 87->28), (400М: 28), (2Г: 61), (300Г: 61)
    pts_pub = [
        (gx + 0.0 * gw, gy + 0.28 * gh),
        (gx + 0.14 * gw, gy + 0.48 * gh),
        (gx + 0.38 * gw, gy + 0.75 * gh),
        (gx + 0.55 * gw, gy + 0.75 * gh),
        (gx + 0.70 * gw, gy + 0.60 * gh),
        (gx + 1.0 * gw, gy + 0.60 * gh),
    ]
    for i in range(len(pts_pub) - 1):
        frags.append(line(pts_pub[i][0], pts_pub[i][1], pts_pub[i+1][0], pts_pub[i+1][1], color=POS, sw=2.5))

    # Легенда знизу
    lx = gx + 40
    ly = gy + gh + 52
    frags.append(line(lx, ly, lx + 30, ly, color=POS, sw=3))
    frags.append(text(lx + 38, ly + 4, "Загальне населення (General Public, E_lim = 28 В/м при 30–400 МГц, S = 2 Вт/м²)", size=10.5, color=INK, anchor="start", bold=True))

    ly += 20
    frags.append(line(lx, ly, lx + 30, ly, color=NEG, sw=3))
    frags.append(text(lx + 38, ly + 4, "Професійний персонал (Occupational, E_lim = 61 В/м при 30–400 МГц, S = 10 Вт/м²)", size=10.5, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG_DIR, "safety-limits-curve.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    fig_isotropic_probe_geometry()
    fig_detector_types_transfer()
    fig_field_probe_signal_chain()
    fig_safety_limits_curve()
    print("All figures for vymiriuvach-napruzhenosti-polia generated successfully.")


if __name__ == "__main__":
    main()
