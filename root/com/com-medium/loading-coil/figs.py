# -*- coding: utf-8 -*-
"""Фігури до теми «Завантажувальна котушка: укорочення антени індуктивністю».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Спільні кольори канону
WAVE = "#c0392b"      # Струм / випромінювання (червоний)
VOLT = "#8e44ad"      # Напруга / високовольтне поле (пурпуровий)
COIL = "#d35400"      # Котушка / індуктивність (оранжевий)
ANT  = "#2980b9"      # Полотнище антени / провідник (синій)
GOOD = FIELD          # Зеленкуватий / нормований стан
BORDER = INK

# ── 1. Еквівалентна схема укороченого монополя та компенсація реактивності ───────
def fig_equivalent_circuit():
    W, H = 780, 380
    f = [text(W / 2, 25, "Еквівалентна схема укороченого монополя та компенсація реактивності", size=15, bold=True)]

    # Ліва панель: Укорочений монополь без котушки (X_in < 0)
    f.append(rect(20, 55, 360, 305, fill="#fdfefe", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(200, 80, "Укорочений штир (L < λ/4)", size=13, bold=True, color=INK))
    f.append(text(200, 98, "Ємнісний імпеданс: Z = R_рад + R_втрат - jX_C", size=11, color=MUTED))

    # Схема ліворуч
    # Генератор
    f.append(circle(60, 220, 18, fill="none", stroke=INK, sw=1.5))
    f.append('<path d="M 50 220 Q 55 212 60 220 T 70 220" stroke="%s" stroke-width="1.5" fill="none"/>' % INK)
    f.append(text(60, 255, "RF Gen", size=10, bold=True, color=INK))

    # Провідники
    f.append(line(78, 220, 110, 220, color=INK, sw=1.5))
    
    # R_rad
    f.append(rect(110, 210, 45, 20, fill="#eaefd3", stroke=BORDER, sw=1.5))
    f.append(text(132, 200, "R_рад", size=11, bold=True, color=GOOD))
    f.append(text(132, 224, "1.5 Ом", size=9, color=MUTED))
    f.append(line(155, 220, 185, 220, color=INK, sw=1.5))

    # R_loss
    f.append(rect(185, 210, 45, 20, fill="#fcedea", stroke=BORDER, sw=1.5))
    f.append(text(207, 200, "R_втрат", size=11, bold=True, color=WAVE))
    f.append(text(207, 224, "5 Ом", size=9, color=MUTED))
    f.append(line(230, 220, 260, 220, color=INK, sw=1.5))

    # C_ant (Конденсатор)
    f.append(line(260, 210, 260, 230, color=ANT, sw=2.5))
    f.append(line(268, 210, 268, 230, color=ANT, sw=2.5))
    f.append(line(230, 220, 260, 220, color=INK, sw=1.5))
    f.append(line(268, 220, 310, 220, color=INK, sw=1.5))
    f.append(text(264, 198, "-j X_C", size=12, bold=True, color=ANT))
    f.append(text(264, 244, "-j 600 Ом", size=10, color=MUTED))

    # Антена / земля
    f.append(line(310, 220, 350, 220, color=INK, sw=1.5))
    f.append(line(60, 238, 60, 300, color=INK, sw=1.5))
    f.append(line(350, 220, 350, 300, color=INK, sw=1.5))
    f.append(line(60, 300, 350, 300, color=INK, sw=1.5))
    f.append(line(200, 300, 200, 315, color=INK, sw=1.5))
    f.append(line(185, 315, 215, 315, color=INK, sw=2))
    f.append(line(190, 320, 210, 320, color=INK, sw=1.5))
    f.append(line(195, 325, 205, 325, color=INK, sw=1))

    # Попередження ліворуч
    f.append(rect(40, 275, 320, 30, fill="#fadbd8", stroke=WAVE, sw=1, rx=4))
    f.append(text(200, 294, "Неузгоджено! Відбивається > 99% потужності", size=11, bold=True, color=WAVE))


    # Права панель: Внесення завантажувальної котушки (+j X_L)
    f.append(rect(400, 55, 360, 305, fill="#fdfefe", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(580, 80, "Резонанс із котушкою L_coil", size=13, bold=True, color=INK))
    f.append(text(580, 98, "Компенсація: +jX_L = +jX_C  →  X_вх = 0", size=11, color=GOOD))

    # Схема праворуч
    f.append(circle(440, 220, 18, fill="none", stroke=INK, sw=1.5))
    f.append('<path d="M 430 220 Q 435 212 440 220 T 450 220" stroke="%s" stroke-width="1.5" fill="none"/>' % INK)
    f.append(text(440, 255, "RF Gen", size=10, bold=True, color=INK))

    # L_coil (Котушка)
    f.append(line(458, 220, 475, 220, color=INK, sw=1.5))
    # Малювання витків котушки
    coil_path = "M 475 220 Q 480 205 485 220 T 495 220 T 505 220 T 515 220 T 525 220"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (coil_path, COIL))
    f.append(text(500, 196, "+j X_L", size=12, bold=True, color=COIL))
    f.append(text(500, 244, "+j 600 Ом", size=10, color=MUTED))
    f.append(line(525, 220, 545, 220, color=INK, sw=1.5))

    # R_coil (Втрати в котушці)
    f.append(rect(545, 210, 35, 20, fill="#fdebd0", stroke=BORDER, sw=1.5))
    f.append(text(562, 200, "R_кот", size=10, bold=True, color=COIL))
    f.append(text(562, 224, "3 Ом", size=9, color=MUTED))
    f.append(line(580, 220, 600, 220, color=INK, sw=1.5))

    # R_rad
    f.append(rect(600, 210, 35, 20, fill="#eaefd3", stroke=BORDER, sw=1.5))
    f.append(text(617, 200, "R_рад", size=10, bold=True, color=GOOD))
    f.append(line(635, 220, 655, 220, color=INK, sw=1.5))

    # C_ant
    f.append(line(655, 210, 655, 230, color=ANT, sw=2.5))
    f.append(line(663, 210, 663, 230, color=ANT, sw=2.5))
    f.append(line(663, 220, 710, 220, color=INK, sw=1.5))
    f.append(text(659, 198, "-j X_C", size=11, bold=True, color=ANT))

    # Земля
    f.append(line(440, 238, 440, 300, color=INK, sw=1.5))
    f.append(line(710, 220, 710, 300, color=INK, sw=1.5))
    f.append(line(440, 300, 710, 300, color=INK, sw=1.5))
    f.append(line(575, 300, 575, 315, color=INK, sw=1.5))
    f.append(line(560, 315, 590, 315, color=INK, sw=2))
    f.append(line(565, 320, 585, 320, color=INK, sw=1.5))
    f.append(line(570, 325, 580, 325, color=INK, sw=1))

    # Статус праворуч
    f.append(rect(420, 275, 320, 30, fill="#e8f8f5", stroke=GOOD, sw=1, rx=4))
    f.append(text(580, 294, "Резонанс досягнуто! Z_вх = R_рад + R_втрат + R_кот", size=11, bold=True, color=GOOD))

    render(os.path.join(IMG, "equivalent-circuit.svg"), W, H, *f)


# ── 2. Розподіл струму при різних позиціях завантажувальної котушки ───────────────
def fig_coil_positions():
    W, H = 780, 380
    f = [text(W / 2, 25, "Розподіл високочастотного струму I(z) при різних позиціях котушки", size=15, bold=True)]

    # 3 колонки: В основі (Base), Посередині (Center), Згори (Top-Hat)
    col_w = 230
    gap = 20
    left_margin = 25

    configs = [
        ("В основі (Base Loading)", "Найпростіша механіка, але мінімальний R_рад", 0.05),
        ("Посередині (Center Loading)", "Оптимальний компроміс: R_рад зростає в 2–3 рази", 0.5),
        ("Згори / Ємнісна шапка", "Максимальний струм по всій довжині, найвищий ККД", 0.95)
    ]

    for i, (title, sub, coil_pos) in enumerate(configs):
        cx = left_margin + i * (col_w + gap)
        cy = 55
        
        # Рамка колонки
        f.append(rect(cx, cy, col_w, 305, fill="#fafafa", stroke=BORDER, sw=1, rx=6))
        f.append(text(cx + col_w / 2, cy + 22, title, size=12, bold=True, color=INK))
        f.append(text(cx + col_w / 2, cy + 38, sub, size=9.5, color=MUTED))

        # Основа землі
        base_y = cy + 260
        f.append(line(cx + 30, base_y, cx + col_w - 30, base_y, color=INK, sw=2))
        f.append(text(cx + col_w / 2, base_y + 16, "Земля / Екран", size=10, color=MUTED))

        # Осі антени
        ant_x = cx + 80
        top_y = cy + 70
        height = base_y - top_y

        # Малювання штиря з котушкою
        coil_y = base_y - coil_pos * height

        # Нижній сегмент штиря
        if coil_pos > 0.08:
            f.append(line(ant_x, base_y, ant_x, coil_y + 12, color=ANT, sw=3))

        # Верхній сегмент штиря
        if coil_pos < 0.92:
            f.append(line(ant_x, coil_y - 12, ant_x, top_y, color=ANT, sw=3))

        # Котушка
        f.append(rect(ant_x - 10, coil_y - 12, 20, 24, fill="#fdebd0", stroke=COIL, sw=1.5, rx=3))
        # Витки
        for wy in range(int(coil_y - 8), int(coil_y + 10), 5):
            f.append(line(ant_x - 8, wy, ant_x + 8, wy, color=COIL, sw=1.5))

        # Ємнісна шапка для 3-го варіанту
        if i == 2:
            f.append(line(ant_x - 30, top_y, ant_x + 30, top_y, color=ANT, sw=2.5))
            f.append(circle(ant_x - 30, top_y, 4, fill=ANT, stroke="none"))
            f.append(circle(ant_x + 30, top_y, 4, fill=ANT, stroke="none"))

        # Малювання профілю струму I(z) [Червона заштрихована область]
        pts = []
        num_steps = 30
        for step in range(num_steps + 1):
            t = step / float(num_steps) # 0 біля землі, 1 на верхівці
            curr_y = base_y - t * height

            # Модель струму залежно від позиції котушки
            if i == 0: # Base loading
                val = 1.0 - t
            elif i == 1: # Center loading
                if t < 0.5:
                    val = 1.0 - 0.2 * t
                else:
                    val = 0.9 * (1.0 - t) / 0.5
            else: # Top loading
                val = 1.0 - 0.25 * t

            curr_x = ant_x + val * 85
            pts.append((curr_x, curr_y))

        # Шлях заливки струму
        path_str = "M %d %d " % (ant_x, base_y)
        for px, py in pts:
            path_str += "L %.1f %.1f " % (px, py)
        path_str += "L %d %d Z" % (ant_x, top_y)

        f.append('<path d="%s" fill="%s" opacity="0.25"/>' % (path_str, WAVE))
        
        # Лінія профілю струму
        line_str = "M " + " L ".join(["%.1f %.1f" % p for p in pts])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (line_str, WAVE))

        f.append(text(ant_x + 45, cy + 180, "I(z)", size=12, bold=True, color=WAVE))

    render(os.path.join(IMG, "coil-positions.svg"), W, H, *f)


# ── 3. Падіння ККД та звуження смуги пропускання при укороченні антени ───────────
def fig_efficiency_vs_length():
    W, H = 780, 360
    f = [text(W / 2, 25, "Залежність ККД (η) та смуги пропускання (BW) від відносної висоти (h/λ)", size=15, bold=True)]

    # Область графіка
    gx, gy, gw, gh = 80, 60, 620, 240
    f.append(rect(gx, gy, gw, gh, fill="#fcfcfc", stroke=BORDER, sw=1))

    # Сітка
    for rel_h in [0.05, 0.10, 0.15, 0.20, 0.25]:
        x_px = gx + (rel_h / 0.25) * gw
        f.append(line(x_px, gy, x_px, gy + gh, color="#e5e8e8", sw=1, dash="3,3"))
        f.append(text(x_px, gy + gh + 18, "%.2f λ" % rel_h, size=11, color=INK))

    f.append(text(gx + gw / 2, gy + gh + 38, "Фізична висота штиря (h / λ)", size=12, bold=True, color=INK))

    # Ліва вісь Y: ККД (%) [Зелена/Червона крива]
    for eff in [0, 25, 50, 75, 100]:
        y_px = gy + gh - (eff / 100.0) * gh
        f.append(line(gx, y_px, gx + gw, y_px, color="#e5e8e8", sw=1, dash="3,3"))
        f.append(text(gx - 12, y_px + 4, "%d%%" % eff, size=10, bold=True, color=GOOD))

    f.append('<g transform="rotate(-90 %d %d)">%s</g>' % (gx - 45, gy + gh / 2, text(gx - 45, gy + gh / 2, "ККД антени η (%)", size=11, bold=True, color=GOOD)))

    # Права вісь Y: Смуга пропускання (кГц) [Синя крива]
    for bw_val in [0, 50, 100, 150, 200]:
        y_px = gy + gh - (bw_val / 200.0) * gh
        f.append(text(gx + gw + 15, y_px + 4, "%d кГц" % bw_val, size=10, bold=True, color=ANT))

    f.append('<g transform="rotate(90 %d %d)">%s</g>' % (gx + gw + 48, gy + gh / 2, text(gx + gw + 48, gy + gh / 2, "Смуга BW (кГц при 7 МГц)", size=11, bold=True, color=ANT)))

    # Крива ККД η(h): η = R_rad / (R_rad + R_loss + R_coil)
    eff_pts = []
    bw_pts = []

    for step in range(101):
        rel_h = 0.01 + (step / 100.0) * 0.24 # 0.01..0.25
        r_rad = 160.0 * (math.pi ** 2) * (rel_h ** 2)
        r_loss = 5.0
        r_coil = 3.0 * (0.25 / rel_h)
        r_total = r_rad + r_loss + r_coil

        eff = (r_rad / r_total) * 100.0
        
        x_c = 600.0 * (0.25 / rel_h)
        q_ant = x_c / r_total
        bw = 7000.0 / q_ant

        x_px = gx + (rel_h / 0.25) * gw
        y_eff = gy + gh - (eff / 100.0) * gh
        y_bw = gy + gh - min(200.0, bw) / 200.0 * gh

        eff_pts.append("%.1f,%.1f" % (x_px, y_eff))
        bw_pts.append("%.1f,%.1f" % (x_px, y_bw))

    # Малювання кривої ККД
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="3"/>' % (" L ".join(eff_pts), GOOD))
    # Малювання кривої смуги
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % (" L ".join(bw_pts), ANT))

    # Аннотаційні мітки на графіку
    x_005 = gx + (0.05 / 0.25) * gw
    f.append(circle(x_005, gy + gh - (12.0 / 100.0) * gh, 5, fill=WAVE, stroke="none"))
    f.append(rect(x_005 + 10, gy + gh - (12.0 / 100.0) * gh - 22, 145, 32, fill="#fdfefe", stroke=BORDER, sw=1, rx=4))
    f.append(text(x_005 + 82, gy + gh - (12.0 / 100.0) * gh - 10, "h = 0.05λ: ККД ≈ 12%", size=10, bold=True, color=WAVE))
    f.append(text(x_005 + 82, gy + gh - (12.0 / 100.0) * gh + 4, "Смуга BW ≈ 15 кГц", size=9.5, color=ANT))

    # Легенда
    f.append(rect(gx + 20, gy + 15, 230, 48, fill="#ffffff", stroke=BORDER, sw=1, rx=4))
    f.append(line(gx + 30, gy + 30, gx + 60, gy + 30, color=GOOD, sw=3))
    f.append(text(gx + 135, gy + 34, "ККД випромінювання η (%)", size=10.5, bold=True, color=GOOD))

    f.append(line(gx + 30, gy + 48, gx + 60, gy + 48, color=ANT, sw=2.5, dash="6,4"))
    f.append(text(gx + 135, gy + 52, "Смуга пропускання BW (кГц)", size=10.5, bold=True, color=ANT))

    render(os.path.join(IMG, "efficiency-vs-length.svg"), W, H, *f)


# ── 4. Висока напруга та ризик пробою на завантажувальній котушці ─────────────────
def fig_voltage_high_q():
    W, H = 780, 360
    f = [text(W / 2, 25, "Високовольтний бар'єр: напруга на котушці при P = 100 Вт", size=15, bold=True)]

    # Конструкція котушки посередині
    # Ліворуч: Схема напруги вздовж витків
    f.append(rect(30, 55, 350, 305, fill="#fcfcfc", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(205, 80, "Фізика високовольтного пробою", size=13, bold=True, color=INK))

    # Котушка детально
    cx = 120
    f.append(rect(cx - 35, 110, 70, 190, fill="#f8f9f9", stroke=BORDER, sw=1.5, rx=4))
    f.append(text(cx, 100, "Діелектричний каркас", size=10, color=MUTED))

    # Витки з високою напругою
    num_turns = 8
    turn_step = 20
    start_y = 125

    for t in range(num_turns):
        ty = start_y + t * turn_step
        color_t = VOLT if t < 4 else COIL
        f.append(rect(cx - 42, ty, 84, 10, fill=color_t, stroke="none", rx=3))
        f.append(text(cx, ty + 8, "Виток %d" % (t + 1), size=9, color="#ffffff", bold=True))

    # Коронарні розряди / дуга
    f.append('<path d="M 165 130 Q 185 140 165 150 Q 190 160 165 170" fill="none" stroke="%s" stroke-width="2"/>' % VOLT)
    f.append(text(215, 150, "Коронний розряд / дуга", size=10, bold=True, color=VOLT))
    f.append(text(215, 166, "V_котушки = I_ант · X_L", size=10, color=INK))

    # Пояснення напруги
    f.append(line(cx + 45, 125, cx + 110, 125, color=VOLT, sw=1.5, dash="3,3"))
    f.append(line(cx + 45, 265, cx + 110, 265, color=INK, sw=1.5, dash="3,3"))
    f.append(arrow(cx + 100, 265, cx + 100, 125, color=VOLT, sw=2))
    f.append('<g transform="rotate(-90 %d 195)">%s</g>' % (cx + 100, text(cx + 100, 195, "V_ампл ≈ 6–8 кВ!", size=11, bold=True, color=VOLT)))

    # Права панель: Числовий розрахунок та інженерні заходи
    f.append(rect(400, 55, 350, 305, fill="#fdfefe", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(575, 80, "Розрахунок для P = 100 Вт", size=13, bold=True, color=INK))

    # Формули та числа
    box_y = 105
    calc_steps = [
        ("Вхідна потужність:", "P = 100 Вт"),
        ("Повний опір втрат:", "R_втрат = 4.0 Ом"),
        ("Струм в антені:", "I = √(P / R) = 5.0 А"),
        ("Реактивність котушки:", "X_L = 1200 Ом"),
        ("Діюча напруга (RMS):", "V_rms = 5A × 1200 Ом = 6000 В"),
        ("Пікова напруга (Peak):", "V_peak = 6000 × √2 = 8485 В!")
    ]

    for title, val in calc_steps:
        f.append(text(420, box_y + 12, title, size=11, color=INK, anchor="start"))
        f.append(text(730, box_y + 12, val, size=11, bold=True, color=VOLT if "В!" in val else INK, anchor="end"))
        box_y += 24

    # Інженерні вимоги для захисту
    f.append(rect(415, 260, 320, 85, fill="#fcedea", stroke=WAVE, sw=1, rx=4))
    f.append(text(575, 278, "Вимоги до конструкції котушки:", size=11, bold=True, color=WAVE))
    f.append(text(425, 296, "• Крок витків s ≥ 1.5–2 × d_дроту (захист від пробою)", size=9.5, color=INK))
    f.append(text(425, 312, "• Каркас із фторопласту (PTFE) або склотекстоліту", size=9.5, color=INK))
    f.append(text(425, 328, "• Великий діаметр D (зменшує необхідну довжину)", size=9.5, color=INK))

    render(os.path.join(IMG, "voltage-high-q.svg"), W, H, *f)


if __name__ == "__main__":
    fig_equivalent_circuit()
    fig_coil_positions()
    fig_efficiency_vs_length()
    fig_voltage_high_q()
    print("Успішно згенеровано 4 SVG-фігури у ./img/")
