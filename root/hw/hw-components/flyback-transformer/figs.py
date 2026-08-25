# -*- coding: utf-8 -*-
"""Фігури для теми flyback-transformer (Трансформатор зворотноходового перетворювача).
svgkit імпортуємо зі scripts/, вивід у ./img/.

    python figs.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра для схем
MAG   = "#b8860b"   # осердя / магнітний потік
HOT   = "#fdecea"   # первинна сторона / висока напруга
COLD  = "#eaf2f8"   # вторинна сторона / вихід
GAP   = "#f9e79f"   # повітряний зазор
WARN  = "#d35400"   # небезпека / викид напруги


def fig_energy_storage():
    """Дві фази роботи flyback: прямий хід (накопичення в зазорі) та зворотний хід (віддача в навантаження)."""
    W, H = 880, 420
    mid_x = W / 2
    f = []

    # Тло двох фаз
    f.append(rect(20, 45, mid_x - 30, 355, fill="#fcfcfc", stroke=LINE, sw=1.2))
    f.append(rect(mid_x + 10, 45, mid_x - 30, 355, fill="#fcfcfc", stroke=LINE, sw=1.2))

    # Заголовки фаз
    b1, _, _ = textbox(mid_x / 2 + 5, 70, "1. ПРЯМИЙ ХІД (Ключ замкнено, t_on)", size=14, bold=True, fill=HOT, stroke=POS)
    f.append(b1)
    b2, _, _ = textbox(mid_x + mid_x / 2 - 5, 70, "2. ЗВОРОТНИЙ ХІД (Ключ розімкнено, t_off)", size=14, bold=True, fill=COLD, stroke=NEG)
    f.append(b2)

    # ── Ліва колонка: Прямий хід ──
    lx = 40
    # Джерело Vin
    f.append(circle(lx + 30, 160, 16, fill="#ffffff", stroke=POS, sw=1.8))
    f.append(text(lx + 30, 165, "V_in", size=11, bold=True, color=POS))
    f.append(line(lx + 30, 144, lx + 30, 115, color=POS, sw=2))
    f.append(line(lx + 30, 115, lx + 130, 115, color=POS, sw=2))

    # Первинна обмотка
    f.append(rect(lx + 130, 115, 36, 90, fill="#fff8e7", stroke=MAG, sw=2))
    f.append(text(lx + 148, 160, "N_p", size=13, bold=True, color=MAG))
    # Крапка полярності
    f.append(circle(lx + 120, 125, 4, fill=POS, stroke=POS))

    # Ключ (замкнений)
    f.append(line(lx + 148, 205, lx + 148, 235, color=POS, sw=2))
    f.append(rect(lx + 133, 235, 30, 35, fill="#e8f8f5", stroke=FIELD, sw=1.8))
    f.append(text(lx + 148, 257, "SW", size=11, bold=True, color=FIELD))
    f.append(line(lx + 148, 270, lx + 148, 300, color=LINE, sw=2))
    f.append(line(lx + 148, 300, lx + 30, 300, color=LINE, sw=2))
    f.append(line(lx + 30, 300, lx + 30, 176, color=LINE, sw=2))

    # Струм первинної
    f.append(arrow(lx + 75, 107, lx + 115, 107, color=POS, sw=2))
    f.append(text(lx + 95, 100, "I_p наростає", size=11, color=POS, bold=True))

    # Осердя з зазором
    f.append(rect(lx + 185, 110, 24, 100, fill="#eaecee", stroke=MAG, sw=1.5))
    f.append(rect(lx + 185, 150, 24, 20, fill=GAP, stroke=WARN, sw=1.5))
    f.append(text(lx + 197, 163, "GAP", size=9, bold=True, color=WARN))

    # Вторинна обмотка
    f.append(rect(lx + 230, 115, 36, 90, fill="#fff8e7", stroke=MAG, sw=2))
    f.append(text(lx + 248, 160, "N_s", size=13, bold=True, color=MAG))
    # Крапка полярності (інвертована - знизу)
    f.append(circle(lx + 220, 195, 4, fill=NEG, stroke=NEG))

    # Вторинне коло (діод закритий)
    f.append(line(lx + 248, 115, lx + 310, 115, color=MUTED, sw=1.5, dash="4 3"))
    # Символ запертого діода
    f.append(line(lx + 310, 105, lx + 310, 125, color=MUTED, sw=2))
    f.append(line(lx + 310, 115, lx + 325, 105, color=MUTED, sw=1.5))
    f.append(line(lx + 310, 115, lx + 325, 125, color=MUTED, sw=1.5))
    f.append(line(lx + 325, 105, lx + 325, 125, color=MUTED, sw=2))
    f.append(text(lx + 318, 95, "D_out ЗАКРИТИЙ", size=10, color=MUTED, bold=True))

    # Конденсатор і навантаження
    f.append(line(lx + 325, 115, lx + 370, 115, color=MUTED, sw=1.5))
    f.append(line(lx + 370, 115, lx + 370, 300, color=MUTED, sw=1.5))
    f.append(line(lx + 248, 205, lx + 248, 300, color=MUTED, sw=1.5))
    f.append(line(lx + 248, 300, lx + 370, 300, color=MUTED, sw=1.5))

    b_info1, _, _ = textbox(lx + 185, 350, "Енергія W = 0.5·L_p·I_pk² накопичується\nвиключно в магнітному полі зазору.\nВторинне коло відсічене діодом.", size=12, pad=6, fill="#ffffff", stroke=POS)
    f.append(b_info1)

    # ── Права колонка: Зворотний хід ──
    rx = mid_x + 30
    # Джерело Vin
    f.append(circle(rx + 30, 160, 16, fill="#ffffff", stroke=MUTED, sw=1.5))
    f.append(text(rx + 30, 165, "V_in", size=11, color=MUTED))

    # Первинна обмотка (струм = 0)
    f.append(rect(rx + 130, 115, 36, 90, fill="#f4f6f7", stroke=MUTED, sw=1.5))
    f.append(text(rx + 148, 160, "N_p", size=13, color=MUTED))
    f.append(circle(rx + 120, 125, 4, fill=MUTED, stroke=MUTED))

    # Ключ (розімкнений)
    f.append(line(rx + 148, 205, rx + 148, 230, color=LINE, sw=1.5))
    f.append(line(rx + 148, 230, rx + 135, 255, color=POS, sw=2)) # відкритий контакт
    f.append(circle(rx + 148, 230, 3, fill=LINE, stroke=LINE))
    f.append(circle(rx + 148, 265, 3, fill=LINE, stroke=LINE))
    f.append(text(rx + 115, 245, "SW OFF", size=11, bold=True, color=POS))
    f.append(line(rx + 148, 265, rx + 148, 300, color=LINE, sw=1.5))
    f.append(line(rx + 148, 300, rx + 30, 300, color=MUTED, sw=1.5))
    f.append(line(rx + 30, 300, rx + 30, 176, color=MUTED, sw=1.5))

    # Осердя з зазором
    f.append(rect(rx + 185, 110, 24, 100, fill="#eaecee", stroke=MAG, sw=1.5))
    f.append(rect(rx + 185, 150, 24, 20, fill=GAP, stroke=WARN, sw=1.5))
    f.append(text(rx + 197, 163, "GAP", size=9, bold=True, color=WARN))

    # Вторинна обмотка (активна)
    f.append(rect(rx + 230, 115, 36, 90, fill="#fff8e7", stroke=MAG, sw=2))
    f.append(text(rx + 248, 160, "N_s", size=13, bold=True, color=MAG))
    f.append(circle(rx + 220, 195, 4, fill=NEG, stroke=NEG))

    # Вторинне коло (діод відкритий, струм тече)
    f.append(line(rx + 248, 115, rx + 310, 115, color=FIELD, sw=2))
    # Діод відкритий
    f.append(line(rx + 310, 105, rx + 310, 125, color=FIELD, sw=2))
    f.append(line(rx + 310, 115, rx + 325, 105, color=FIELD, sw=2))
    f.append(line(rx + 310, 115, rx + 325, 125, color=FIELD, sw=2))
    f.append(line(rx + 325, 105, rx + 325, 125, color=FIELD, sw=2))
    f.append(arrow(rx + 265, 107, rx + 300, 107, color=FIELD, sw=2))
    f.append(text(rx + 318, 95, "D_out ВІДКРИТИЙ", size=10, color=FIELD, bold=True))

    f.append(line(rx + 325, 115, rx + 370, 115, color=FIELD, sw=2))
    # Конденсатор C_out
    f.append(line(rx + 350, 115, rx + 350, 195, color=FIELD, sw=1.8))
    f.append(line(rx + 340, 195, rx + 360, 195, color=FIELD, sw=2.5))
    f.append(line(rx + 340, 205, rx + 360, 205, color=FIELD, sw=2.5))
    f.append(line(rx + 350, 205, rx + 350, 300, color=FIELD, sw=1.8))
    f.append(text(rx + 375, 200, "C_out", size=11, color=FIELD))

    # Навантаження R_load
    f.append(line(rx + 370, 115, rx + 370, 300, color=FIELD, sw=1.8))
    f.append(line(rx + 248, 205, rx + 248, 300, color=FIELD, sw=2))
    f.append(line(rx + 248, 300, rx + 370, 300, color=FIELD, sw=2))
    f.append(arrow(rx + 320, 292, rx + 270, 292, color=FIELD, sw=2))
    f.append(text(rx + 295, 283, "I_s спадає", size=11, color=FIELD, bold=True))

    b_info2, _, _ = textbox(rx + 185, 350, "Полярність е.р.с. змінюється на протилежну.\nЕнергія з зазору 'переливається'\nу вторинний конденсатор та навантаження.", size=12, pad=6, fill="#ffffff", stroke=FIELD)
    f.append(b_info2)

    return render(os.path.join(IMG, "flyback-energy-storage.svg"), W, H, *f)


def fig_magnetic_air_gap():
    """Фізика немагнітного зазору: B-H крива з зазором та без нього, локалізація 98% енергії."""
    W, H = 880, 400
    mid_x = 440
    f = []

    # Ліва частина: B-H петля
    f.append(rect(20, 40, mid_x - 35, 335, fill="#fdfefe", stroke=LINE, sw=1.2))
    b_lh, _, _ = textbox(mid_x / 2 + 3, 62, "Крива намагнічування: без зазору проти з зазором", size=13, bold=True, fill=FILL, stroke=LINE)
    f.append(b_lh)

    ox, oy = 80, 260
    # Осі H та B
    f.append(arrow(ox - 20, oy, ox + 300, oy, color=LINE, sw=1.8))
    f.append(text(ox + 310, oy + 5, "H (струм I)", size=12, bold=True, anchor="start"))
    f.append(arrow(ox, oy + 80, ox, oy - 170, color=LINE, sw=1.8))
    f.append(text(ox - 10, oy - 175, "B (індукція)", size=12, bold=True, anchor="end"))

    # Рівень насичення B_sat
    f.append(line(ox - 10, oy - 130, ox + 280, oy - 130, color=POS, sw=1.5, dash="6 4"))
    f.append(text(ox + 285, oy - 130, "B_sat (насичення)", size=11, color=POS, bold=True, anchor="start"))

    # Крива БЕЗ зазору (дуже крута)
    f.append(line(ox, oy, ox + 35, oy - 130, color=POS, sw=2.5))
    f.append(line(ox + 35, oy - 130, ox + 280, oy - 135, color=POS, sw=2))
    f.append(text(ox + 40, oy - 90, "Суцільний ферит (μ_r=2500)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(ox + 40, oy - 75, "Насичення при мізерному I_sat", size=10, color=POS, anchor="start"))

    # Крива З ЗАЗОРОМ (похила)
    f.append(line(ox, oy, ox + 200, oy - 130, color=FIELD, sw=2.5))
    f.append(line(ox + 200, oy - 130, ox + 280, oy - 135, color=FIELD, sw=2))
    f.append(text(ox + 130, oy - 35, "Осердя з зазором l_gap", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(ox + 130, oy - 20, "Широкий запас струму ΔI_pk", size=10, color=FIELD, anchor="start"))

    # Стрілка нахилу петлі
    f.append(arrow(ox + 60, oy - 110, ox + 150, oy - 70, color=LINE, sw=1.5))
    f.append(text(ox + 115, oy - 95, "Зазор нахиляє криву", size=10, italic=True))

    # Права частина: Локалізація густини енергії w = 0.5 * B^2 / mu
    rx = mid_x + 15
    f.append(rect(rx, 40, W - rx - 20, 335, fill="#fdfefe", stroke=LINE, sw=1.2))
    b_rh, _, _ = textbox(rx + (W - rx - 20) / 2, 62, "Де насправді зберігається енергія?", size=13, bold=True, fill=FILL, stroke=LINE)
    f.append(b_rh)

    # Рисунок осердя
    core_cx = rx + 195
    core_cy = 175
    # Зовнішнє коло осердя
    f.append(rect(core_cx - 130, core_cy - 75, 260, 150, fill="#eaecee", stroke=MAG, sw=2, rx=10))
    # Внутрішнє вікно
    f.append(rect(core_cx - 85, core_cy - 45, 170, 90, fill="#ffffff", stroke=MAG, sw=1.5, rx=6))
    # Центральний керн з зазором
    f.append(rect(core_cx - 25, core_cy - 45, 50, 90, fill="#eaecee", stroke=MAG, sw=1.5))
    # Сам зазор
    f.append(rect(core_cx - 25, core_cy - 10, 50, 20, fill=GAP, stroke=WARN, sw=2))
    f.append(text(core_cx, core_cy + 4, "Зазор l_gap", size=10, bold=True, color=WARN))

    # Лінії магнітного потоку
    f.append(line(core_cx - 105, core_cy - 60, core_cx + 105, core_cy - 60, color=MAG, sw=1.5, dash="5 3"))
    f.append(line(core_cx - 105, core_cy + 60, core_cx + 105, core_cy + 60, color=MAG, sw=1.5, dash="5 3"))

    # Баланс енергії
    b_en1, _, _ = textbox(rx + 100, 290, "Ферит (μ_r ≈ 2500):\nw = 0.5·B²/(μ_0·μ_r)\nВсього ~2% енергії", size=11, pad=6, fill="#f4f6f7", stroke=MUTED)
    f.append(b_en1)

    b_en2, _, _ = textbox(rx + 295, 290, "Зазор (μ_r = 1):\nw = 0.5·B²/μ_0\nБільше 98% енергії!", size=11, pad=6, fill="#fef9e7", stroke=WARN)
    f.append(b_en2)

    f.append(text(rx + 195, 355, "Ферит слугує лише 'магнітопроводом' для підведення потоку до зазору", size=11, italic=True, color=INK))

    return render(os.path.join(IMG, "magnetic-air-gap.svg"), W, H, *f)


def fig_leakage_snubber():
    """Індуктивність розсіювання L_leak, викид напруги на стоку та RCD-снабер."""
    W, H = 880, 390
    f = []

    # Ліва частина: Схема з L_leak та RCD-клампом
    f.append(rect(20, 35, 480, 335, fill="#fdfefe", stroke=LINE, sw=1.2))
    b_lh, _, _ = textbox(260, 58, "Еквівалентна схема первинного кола з RCD-снабером", size=13, bold=True, fill=FILL, stroke=LINE)
    f.append(b_lh)

    sx = 50
    # V_in шина
    f.append(line(sx, 110, sx + 220, 110, color=POS, sw=2))
    f.append(circle(sx, 110, 4, fill=POS, stroke=POS))
    f.append(text(sx, 95, "+V_in (DC)", size=12, bold=True, color=POS, anchor="start"))

    # Індуктивність розсіювання L_leak
    f.append(rect(sx + 100, 95, 55, 30, fill="#fdebd0", stroke=WARN, sw=1.8))
    f.append(text(sx + 127, 114, "L_leak", size=11, bold=True, color=WARN))

    # Головна індуктивність намагнічування L_m
    f.append(rect(sx + 175, 95, 55, 30, fill="#fff8e7", stroke=MAG, sw=1.8))
    f.append(text(sx + 202, 114, "L_m", size=11, bold=True, color=MAG))

    # Вузол стоку MOSFET (Drain)
    drain_x = sx + 255
    f.append(line(sx + 230, 110, drain_x, 110, color=LINE, sw=2))
    f.append(line(drain_x, 110, drain_x, 260, color=LINE, sw=2))
    f.append(circle(drain_x, 200, 4, fill=LINE, stroke=LINE))
    f.append(text(drain_x + 10, 200, "Вузол стоку (Drain)", size=11, bold=True, anchor="start"))

    # Ключ MOSFET
    f.append(rect(drain_x - 15, 260, 30, 45, fill="#e8f8f5", stroke=FIELD, sw=1.8))
    f.append(text(drain_x, 287, "MOSFET", size=10, bold=True, color=FIELD))
    f.append(line(drain_x, 305, drain_x, 335, color=LINE, sw=2))
    # GND
    f.append(line(drain_x - 15, 335, drain_x + 15, 335, color=LINE, sw=2))
    f.append(line(drain_x - 10, 340, drain_x + 10, 340, color=LINE, sw=1.5))
    f.append(line(drain_x - 5, 345, drain_x + 5, 345, color=LINE, sw=1))

    # RCD Snubber паралельно первинній обмотці
    # Відведення до RCD діода D_snubber
    f.append(line(drain_x, 155, sx + 340, 155, color=WARN, sw=1.8))
    # Діод D_snubber направлений вгору
    f.append(line(sx + 340, 155, sx + 340, 135, color=WARN, sw=1.8))
    f.append(line(sx + 330, 135, sx + 350, 135, color=WARN, sw=2))
    f.append(line(sx + 340, 135, sx + 330, 120, color=WARN, sw=1.5))
    f.append(line(sx + 340, 135, sx + 350, 120, color=WARN, sw=1.5))
    f.append(line(sx + 330, 120, sx + 350, 120, color=WARN, sw=2))
    f.append(text(sx + 360, 130, "D_snubber", size=10, color=WARN, anchor="start"))

    # Шина після діода до R_s || C_s
    f.append(line(sx + 340, 120, sx + 340, 90, color=WARN, sw=1.8))
    f.append(line(sx + 340, 90, sx + 430, 90, color=WARN, sw=1.8))

    # C_snubber
    f.append(line(sx + 390, 90, sx + 390, 105, color=WARN, sw=1.5))
    f.append(line(sx + 380, 105, sx + 400, 105, color=WARN, sw=2.5))
    f.append(line(sx + 380, 115, sx + 400, 115, color=WARN, sw=2.5))
    f.append(line(sx + 390, 115, sx + 390, 130, color=WARN, sw=1.5))
    f.append(text(sx + 368, 112, "C_s", size=10, bold=True, color=WARN))

    # R_snubber
    f.append(line(sx + 430, 90, sx + 430, 100, color=WARN, sw=1.5))
    f.append(rect(sx + 420, 100, 20, 25, fill="#ffffff", stroke=WARN, sw=1.5))
    f.append(line(sx + 430, 125, sx + 430, 130, color=WARN, sw=1.5))
    f.append(text(sx + 450, 114, "R_s", size=10, bold=True, color=WARN))

    # З'єднання R_s || C_s назад до +Vin
    f.append(line(sx + 390, 130, sx + 430, 130, color=WARN, sw=1.8))
    f.append(line(sx + 410, 130, sx + 410, 170, color=WARN, sw=1.8))
    f.append(line(sx + 410, 170, sx + 80, 170, color=WARN, sw=1.8))
    f.append(line(sx + 80, 170, sx + 80, 110, color=WARN, sw=1.8))

    # Права частина: Осцилограма напруги на стоку V_DS
    rx = 520
    f.append(rect(rx, 35, W - rx - 20, 335, fill="#fdfefe", stroke=LINE, sw=1.2))
    b_rh, _, _ = textbox(rx + (W - rx - 20) / 2, 58, "Осцилограма напруги на стоку V_DS", size=13, bold=True, fill=FILL, stroke=LINE)
    f.append(b_rh)

    gx, gy = rx + 40, 310
    # Осі t та V
    f.append(arrow(gx - 10, gy, gx + 270, gy, color=LINE, sw=1.8))
    f.append(text(gx + 280, gy + 4, "t", size=12, bold=True, anchor="start"))
    f.append(arrow(gx, gy + 10, gx, gy - 210, color=LINE, sw=1.8))
    f.append(text(gx - 10, gy - 215, "V_DS", size=12, bold=True, anchor="end"))

    # Рівні напруг
    # V_in
    f.append(line(gx, gy - 50, gx + 260, gy - 50, color=MUTED, sw=1, dash="4 3"))
    f.append(text(gx - 8, gy - 50, "V_in", size=10, color=MUTED, anchor="end"))

    # V_in + V_reflected
    f.append(line(gx, gy - 110, gx + 260, gy - 110, color=FIELD, sw=1, dash="4 3"))
    f.append(text(gx - 8, gy - 110, "V_in + V_ro", size=10, color=FIELD, anchor="end"))

    # V_clamp (зрізаний снабером)
    f.append(line(gx, gy - 160, gx + 260, gy - 160, color=POS, sw=1.5, dash="6 3"))
    f.append(text(gx - 8, gy - 160, "V_clamp", size=10, bold=True, color=POS, anchor="end"))

    # Форма сигналу
    # 0 -> t_on (0 В)
    f.append(line(gx, gy, gx + 70, gy, color=FIELD, sw=2))
    f.append(text(gx + 35, gy + 18, "ON-стан", size=9, color=FIELD))

    # Вимикання: стрімкий сплеск
    f.append(line(gx + 70, gy, gx + 75, gy - 160, color=POS, sw=2.5))
    # Зріз снабером і дзвоніння
    f.append(line(gx + 75, gy - 160, gx + 110, gy - 160, color=POS, sw=2.5))
    f.append(line(gx + 110, gy - 160, gx + 125, gy - 105, color=POS, sw=1.8))
    f.append(line(gx + 125, gy - 105, gx + 140, gy - 115, color=POS, sw=1.8))
    f.append(line(gx + 140, gy - 115, gx + 155, gy - 110, color=POS, sw=1.8))
    # Полиця зворотного ходу
    f.append(line(gx + 155, gy - 110, gx + 210, gy - 110, color=FIELD, sw=2))
    f.append(text(gx + 175, gy - 125, "Зворотний хід", size=9, color=FIELD))

    # Падіння при розряді
    f.append(line(gx + 210, gy - 110, gx + 225, gy - 50, color=FIELD, sw=1.8))
    f.append(line(gx + 225, gy - 50, gx + 260, gy - 50, color=FIELD, sw=1.8))

    # Текстова підказка про небезпеку
    b_warn, _, _ = textbox(rx + 155, gy - 190, "Без снабера L_leak спричинить\nпробій ключа (> V_DS_max)", size=10, fill="#fdecea", stroke=POS)
    f.append(b_warn)

    return render(os.path.join(IMG, "leakage-snubber.svg"), W, H, *f)


def fig_winding_interleaving():
    """Конструкція обмоток: звичайна шарова намотка проти сендвіча (Interleaving) та поле H(x)."""
    W, H = 880, 400
    mid_x = W / 2
    f = []

    # Ліва частина: Звичайна намотка (Non-interleaved)
    f.append(rect(20, 35, mid_x - 30, 345, fill="#fdfefe", stroke=LINE, sw=1.2))
    b1, _, _ = textbox(mid_x / 2 + 5, 58, "1. Звичайна намотка (P - S)", size=13, bold=True, fill=FILL, stroke=LINE)
    f.append(b1)

    lx = 45
    # Шари: Осердя | Первинна (P) | Вторинна (S)
    f.append(rect(lx, 90, 35, 120, fill="#eaecee", stroke=MAG, sw=1.5))
    f.append(text(lx + 17, 150, "Осердя", size=10, color=MAG, anchor="middle"))

    f.append(rect(lx + 45, 90, 60, 120, fill="#fdebd0", stroke=POS, sw=1.8))
    f.append(text(lx + 75, 150, "P (Первинна)", size=11, bold=True, color=POS))

    f.append(rect(lx + 115, 90, 60, 120, fill="#d4efdf", stroke=FIELD, sw=1.8))
    f.append(text(lx + 145, 150, "S (Вторинна)", size=11, bold=True, color=FIELD))

    # Графік поля H(x) під шарами
    g_ly = 320
    f.append(arrow(lx, g_ly, lx + 280, g_ly, color=LINE, sw=1.5))
    f.append(text(lx + 290, g_ly + 4, "x", size=11, bold=True, anchor="start"))
    f.append(arrow(lx, g_ly + 10, lx, g_ly - 100, color=LINE, sw=1.5))
    f.append(text(lx - 5, g_ly - 105, "H(x)", size=11, bold=True, anchor="end"))

    # Трикутник напруженості поля H(x)
    f.append(line(lx + 45, g_ly, lx + 110, g_ly - 80, color=POS, sw=2.5))
    f.append(line(lx + 110, g_ly - 80, lx + 175, g_ly, color=FIELD, sw=2.5))
    f.append(line(lx + 110, g_ly, lx + 110, g_ly - 80, color=MUTED, sw=1, dash="4 3"))
    f.append(text(lx + 110, g_ly - 90, "H_max (100%)", size=11, bold=True, color=POS))

    b_res1, _, _ = textbox(lx + 270, 150, "Висока L_leak\nЕнергія поля E ∝ ∫H²dx\n(100% втрат)", size=11, pad=6, fill="#fdecea", stroke=POS)
    f.append(b_res1)

    # Права частина: Секціонована намотка (Interleaved Sandwich P1 - S - P2)
    rx = mid_x + 10
    f.append(rect(rx, 35, mid_x - 30, 345, fill="#fdfefe", stroke=LINE, sw=1.2))
    b2, _, _ = textbox(rx + (mid_x - 30) / 2, 58, "2. Сендвіч-намотка (P1 - S - P2)", size=13, bold=True, fill=FILL, stroke=FIELD)
    f.append(b2)

    # Шари: Осердя | P1 (1/2) | S | P2 (1/2)
    f.append(rect(rx + 20, 90, 30, 120, fill="#eaecee", stroke=MAG, sw=1.5))
    f.append(text(rx + 35, 150, "Осердя", size=10, color=MAG, anchor="middle"))

    f.append(rect(rx + 55, 90, 45, 120, fill="#fdebd0", stroke=POS, sw=1.5))
    f.append(text(rx + 77, 150, "P1 (½)", size=10, bold=True, color=POS))

    f.append(rect(rx + 105, 90, 55, 120, fill="#d4efdf", stroke=FIELD, sw=1.8))
    f.append(text(rx + 132, 150, "S", size=11, bold=True, color=FIELD))

    f.append(rect(rx + 165, 90, 45, 120, fill="#fdebd0", stroke=POS, sw=1.5))
    f.append(text(rx + 187, 150, "P2 (½)", size=10, bold=True, color=POS))

    # Графік поля H(x) для сендвіча
    f.append(arrow(rx + 20, g_ly, rx + 280, g_ly, color=LINE, sw=1.5))
    f.append(text(rx + 290, g_ly + 4, "x", size=11, bold=True, anchor="start"))
    f.append(arrow(rx + 20, g_ly + 10, rx + 20, g_ly - 100, color=LINE, sw=1.5))
    f.append(text(rx + 15, g_ly - 105, "H(x)", size=11, bold=True, anchor="end"))

    # Два маленьких трикутники H(x) з піком H_max / 2
    f.append(line(rx + 55, g_ly, rx + 102, g_ly - 40, color=POS, sw=2))
    f.append(line(rx + 102, g_ly - 40, rx + 132, g_ly, color=FIELD, sw=2))
    f.append(line(rx + 132, g_ly, rx + 162, g_ly - 40, color=FIELD, sw=2))
    f.append(line(rx + 162, g_ly - 40, rx + 210, g_ly, color=POS, sw=2))

    f.append(text(rx + 102, g_ly - 50, "H_max / 2", size=10, bold=True, color=FIELD))
    f.append(text(rx + 162, g_ly - 50, "H_max / 2", size=10, bold=True, color=FIELD))

    b_res2, _, _ = textbox(rx + 280, 150, "L_leak падає у 4 рази!\nОскільки E ∝ (H/2)²,\nзалишок енергії ~25%", size=11, pad=6, fill="#e8f8f5", stroke=FIELD)
    f.append(b_res2)

    return render(os.path.join(IMG, "winding-interleaving.svg"), W, H, *f)


if __name__ == "__main__":
    fig_energy_storage()
    fig_magnetic_air_gap()
    fig_leakage_snubber()
    fig_winding_interleaving()
    print("Всі фігури згенеровано успішно.")
