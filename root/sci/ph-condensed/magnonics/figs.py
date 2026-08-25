# -*- coding: utf-8 -*-
"""Генератор графічних ілюстрацій для теми 'Магноніка та магнонні кристали'."""

import os
import sys
import math

# Підключаємо svgkit із кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox, textbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR, exist_ok=True)


def fig_charge_vs_magnonic():
    """Фігура 1: Порівняння електронного (заряд) та магнонного (спін) переносу."""
    w, h = 760, 360
    f = []

    # Заголовок блоку електронного переносу
    f.append(fitbox(20, 15, 345, 40, "Електронний перенос (CMOS / Мідь)", size=14, bold=True, fill="#fdecea", stroke=POS))
    # Заголовок блоку магнонного переносу
    f.append(fitbox(395, 15, 345, 40, "Магнонний перенос (Спінові хвилі)", size=14, bold=True, fill="#eaf0fd", stroke=NEG))

    # Лівий канал: Дрейф електронів з розсіюванням
    f.append(rect(20, 65, 345, 180, fill="#fffaf9", stroke=POS, sw=1.2))
    # Атомна ґратка (дефекти / фонони)
    for cx, cy in [(60, 110), (130, 170), (200, 110), (270, 170), (330, 120)]:
        f.append(circle(cx, cy, 10, fill="#e5e7eb", stroke=MUTED, sw=1.5))
        f.append(text(cx, cy + 4, "Fe", size=10, color=MUTED))

    # Траєкторії електронів (ламані лінії)
    f.append(line(35, 130, 60, 110, color=POS, sw=1.5, dash="2,2"))
    f.append(line(60, 110, 110, 150, color=POS, sw=1.5, dash="2,2"))
    f.append(line(110, 150, 130, 170, color=POS, sw=1.5, dash="2,2"))
    f.append(line(130, 170, 190, 130, color=POS, sw=1.5, dash="2,2"))
    f.append(line(190, 130, 270, 170, color=POS, sw=1.5, dash="2,2"))
    f.append(arrow(270, 170, 345, 140, color=POS, sw=2))

    # Заряд і джоулеве тепло
    f.append(circle(110, 150, 7, fill=POS, stroke=INK, sw=1))
    f.append(text(110, 153, "e⁻", size=10, color="#ffffff", bold=True))
    f.append(circle(190, 130, 7, fill=POS, stroke=INK, sw=1))
    f.append(text(190, 133, "e⁻", size=10, color="#ffffff", bold=True))

    f.append(fitbox(35, 205, 315, 30, "Джоулеве тепло: P = I²R ≠ 0", size=12, bold=True, color=POS, fill="#ffffff", stroke=POS))

    # Правий канал: Прецесія спінів без переміщення атомів чи заряду
    f.append(rect(395, 65, 345, 180, fill="#f8fafc", stroke=NEG, sw=1.2))

    # Ланцюжок атомарних спінів із хвильовим зсувом фази
    x_positions = [435, 490, 545, 600, 655, 710]
    phases = [0, 45, 90, 135, 180, 225]

    for x_c, phase in zip(x_positions, phases):
        y_c = 150
        f.append(circle(x_c, y_c, 8, fill="#cbd5e1", stroke=MUTED, sw=1.5))
        # Спіновий вектор під кутом фази
        rad = math.radians(phase - 90)
        dx = 24 * math.cos(rad)
        dy = 24 * math.sin(rad)
        f.append(arrow(x_c, y_c, x_c + dx, y_c + dy, color=NEG, sw=2.2))

    # Синусоїдна обвідна спінової хвилі
    wave_pts = []
    for x_i in range(420, 725, 5):
        y_i = 150 + 25 * math.sin(math.radians((x_i - 420) * 1.5))
        wave_pts.append((x_i, y_i))
    for i in range(len(wave_pts) - 1):
        f.append(line(wave_pts[i][0], wave_pts[i][1], wave_pts[i+1][0], wave_pts[i+1][1], color=FIELD, sw=1.8, dash="3,2"))

    f.append(fitbox(410, 205, 315, 30, "Заряд не рухається: j_e = 0, P_Joule = 0", size=12, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD))

    # Нижні порівняльні блоки
    f.append(fitbox(20, 255, 345, 85, "• Матеріальні втрати через опір\n• Обмеження за частотою (RC-затримка)\n• Високе енергоспоживання", size=12, pad=6, fill="#fdf2f2", stroke="#f87171"))
    f.append(fitbox(395, 255, 345, 85, "• Перенос кутового моменту (магнони)\n• Частоти ГГц – ТГц при нм-довжинах хвиль\n• Відсутність джоулевих втрат у середовищі", size=12, pad=6, fill="#f0fdf4", stroke="#4ade80"))

    render(os.path.join(IMG_DIR, 'charge-vs-magnonic-transfer.svg'), w, h, *f)


def fig_gilbert_damping_precession():
    """Фігура 2: Прецесія намагніченості та затухання Ґільберта (LLG dynamics)."""
    w, h = 680, 400
    f = []

    cx, cy = 240, 230

    # Еліпс прецесійного конуса
    rx_cone, ry_cone = 120, 45
    cone_y = cy - 110
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cone_y, rx_cone, ry_cone, MUTED))

    # Вісь ефективного поля H_eff
    f.append(arrow(cx, cy, cx, cy - 180, color=FIELD, sw=2.5))
    f.append(text(cx + 15, cy - 165, "H_eff (Зовнішнє + Обмінне + Дипольне поле)", size=13, color=FIELD, bold=True, anchor="start"))

    # Спіральна траєкторія затухання
    spiral_pts = []
    for t in range(0, 360 * 3 + 1, 10):
        r_scale = 1.0 - (t / (360 * 3.5))
        rad = math.radians(t)
        x_s = cx + rx_cone * r_scale * math.cos(rad)
        y_s = cone_y + ry_cone * r_scale * math.sin(rad) + (t / (360 * 3)) * 60
        spiral_pts.append((x_s, y_s))

    for i in range(len(spiral_pts) - 1):
        f.append(line(spiral_pts[i][0], spiral_pts[i][1], spiral_pts[i+1][0], spiral_pts[i+1][1], color=NEG, sw=1.5))

    # Вектор намагніченості M у певний момент часу
    m_x = cx + rx_cone * 0.8 * math.cos(math.radians(40))
    m_y = cone_y + ry_cone * 0.8 * math.sin(math.radians(40))
    f.append(arrow(cx, cy, m_x, m_y, color=POS, sw=3))
    f.append(text(m_x + 12, m_y - 5, "M (Намагніченість)", size=13, color=POS, bold=True, anchor="start"))

    # Вектор прецесійного моменту: -γ [M × H_eff]
    prec_dx, prec_dy = -35, 12
    f.append(arrow(m_x, m_y, m_x + prec_dx, m_y + prec_dy, color=NEG, sw=2))
    f.append(text(m_x + prec_dx - 10, m_y + prec_dy + 15, "Торсіон прецесії: -γ(M × H_eff)", size=11, color=NEG, bold=True, anchor="end"))

    # Вектор затухання Ґільберта: (α/M_s) [M × dM/dt]
    damp_dx, damp_dy = (cx - m_x) * 0.35, (cy - 120 - m_y) * 0.35
    f.append(arrow(m_x, m_y, m_x + damp_dx, m_y + damp_dy, color=POS, sw=2))
    f.append(text(m_x + damp_dx + 10, m_y + damp_dy - 5, "Затухання Ґільберта: (α/M_s)(M × ∂M/∂t)", size=11, color=POS, bold=True, anchor="start"))

    # Пояснювальний блок праворуч
    f.append(fitbox(430, 50, 230, 45, "Рівняння Ландау—Ліфшиця—Ґільберта", size=13, bold=True, fill="#f4f6f8", stroke=LINE))
    
    info_text = (
        "∂M/∂t = -γ(M × H_eff)\n"
        "        + (α/M_s)(M × ∂M/∂t)\n\n"
        "• α — безрозмірний коефіцієнт\n"
        "  затухання Ґільберта;\n"
        "• γ — ґіромагнітне відношення;\n"
        "• При α → 0 намагніченість\n"
        "  прецесує вічно без втрат;\n"
        "• У чистих монокристалах YIG\n"
        "  α ≈ 10⁻⁴ (найнижче з відомих)."
    )
    f.append(fitbox(430, 110, 230, 260, info_text, size=11, pad=10, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG_DIR, 'gilbert-damping-precession.svg'), w, h, *f)


def fig_magnonic_band_structure():
    """Фігура 3: Дисперсійна діаграма магнонного кристала та заборонені зони (Band gaps)."""
    w, h = 740, 380
    f = []

    # Ліва частина: Геометрія 1D магнонного кристала
    f.append(fitbox(20, 20, 310, 35, "Структура 1D магнонного кристала", size=13, bold=True, fill="#f4f6f8", stroke=LINE))
    
    # Періодичний хвилевід з періодом a
    f.append(rect(20, 75, 310, 110, fill="#ffffff", stroke=MUTED, sw=1))
    
    # Періодичні канавки або зони іплантації
    for i in range(4):
        x_block = 35 + i * 70
        f.append(rect(x_block, 95, 35, 70, fill="#dbeafe", stroke=NEG, sw=1.5))
        f.append(text(x_block + 17.5, 134, "M_s1", size=11, color=NEG, bold=True))
        
        x_gap = x_block + 35
        f.append(rect(x_gap, 105, 35, 50, fill="#fef3c7", stroke=POS, sw=1.5))
        f.append(text(x_gap + 17.5, 134, "M_s2", size=11, color=POS, bold=True))

    # Позначення періоду ґратки 'a'
    f.append(arrow(35, 180, 105, 180, color=INK, sw=1.5))
    f.append(arrow(105, 180, 35, 180, color=INK, sw=1.5))
    f.append(text(70, 195, "Період ґратки a", size=12, color=INK, bold=True))

    f.append(fitbox(20, 210, 310, 150, 
                    "Модуляція параметрів:\n"
                    "• Намагніченість насичення M_s(x)\n"
                    "• Геометрична ширина w(x)\n"
                    "• Внутрішнє поле H_0(x)\n"
                    "Бреггівське відбиття магнонів:\n"
                    "k = n · (π / a)", size=11, pad=8, fill="#fafafa", stroke=MUTED))

    # Права частина: Дисперсійні криві ω(k) з забороненими зонами
    ox, oy = 400, 330
    w_chart, h_chart = 310, 280

    f.append(fitbox(400, 20, 320, 35, "Дисперсія ω(k) та магнонні заборонені зони", size=13, bold=True, fill="#f4f6f8", stroke=LINE))

    # Осі координат
    f.append(arrow(ox, oy, ox + w_chart, oy, color=INK, sw=1.8))
    f.append(text(ox + w_chart - 15, oy + 25, "Хвильове число k", size=12, color=INK, bold=True))

    f.append(arrow(ox, oy, ox, oy - h_chart, color=INK, sw=1.8))
    f.append(text(ox - 30, oy - h_chart + 15, "Частота ω", size=12, color=INK, bold=True))

    # Межі зон Бріллюена: k = π/a, 2π/a
    k1 = ox + 110
    k2 = ox + 220
    f.append(line(k1, oy, k1, oy - h_chart + 20, color=MUTED, sw=1, dash="3,3"))
    f.append(text(k1, oy + 18, "π/a", size=11, color=MUTED))

    f.append(line(k2, oy, k2, oy - h_chart + 20, color=MUTED, sw=1, dash="3,3"))
    f.append(text(k2, oy + 18, "2π/a", size=11, color=MUTED))

    # Заборонені зони (Бандґепи) - горизонтальні смуги
    gap1_y, gap1_h = oy - 120, 30
    f.append(rect(ox + 5, gap1_y - gap1_h, w_chart - 15, gap1_h, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=0))
    f.append(text(ox + w_chart / 2, gap1_y - gap1_h / 2 + 4, "Заборонена зона 1 (Band Gap)", size=11, color=POS, bold=True))

    gap2_y, gap2_h = oy - 220, 25
    f.append(rect(ox + 5, gap2_y - gap2_h, w_chart - 15, gap2_h, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=0))
    f.append(text(ox + w_chart / 2, gap2_y - gap2_h / 2 + 4, "Заборонена зона 2 (Band Gap)", size=11, color=POS, bold=True))

    # Дозволені гілки дисперсії
    pts_b1 = []
    for px in range(0, 111, 5):
        k_rel = px / 110.0
        py = oy - 30 - 60 * (k_rel ** 1.3)
        pts_b1.append((ox + px, py))
    for i in range(len(pts_b1) - 1):
        f.append(line(pts_b1[i][0], pts_b1[i][1], pts_b1[i+1][0], pts_b1[i+1][1], color=NEG, sw=2.5))

    pts_b2 = []
    for px in range(110, 221, 5):
        k_rel = (px - 110) / 110.0
        py = (gap1_y - gap1_h - 10) - 60 * (k_rel ** 1.2)
        pts_b2.append((ox + px, py))
    for i in range(len(pts_b2) - 1):
        f.append(line(pts_b2[i][0], pts_b2[i][1], pts_b2[i+1][0], pts_b2[i+1][1], color=NEG, sw=2.5))

    render(os.path.join(IMG_DIR, 'magnonic-band-structure.svg'), w, h, *f)


def fig_magnonic_mach_zehnder_gate():
    """Фігура 4: Логічний елемент на основі магнонного інтерферометра Маха—Цендера."""
    w, h = 760, 360
    f = []

    # Заголовок
    f.append(fitbox(20, 15, 720, 35, "Магнонний інтерферометр Маха—Цендера (Логічні вентилі XOR / AND)", size=14, bold=True, fill="#f4f6f8", stroke=LINE))

    # Вхідна копланарна антенна (CPW)
    f.append(fitbox(30, 150, 100, 70, "Вхідний\nзбудник\n(CPW A)", size=11, bold=True, fill="#dbeafe", stroke=NEG))
    f.append(arrow(130, 185, 180, 185, color=NEG, sw=2.5))
    f.append(text(155, 175, "Ψ_in", size=12, color=NEG, bold=True))

    # Розгалуження на два плечі
    f.append(line(180, 185, 230, 100, color=FIELD, sw=3))
    f.append(line(180, 185, 230, 270, color=FIELD, sw=3))

    # Плече A (верхнє)
    f.append(rect(230, 85, 280, 30, fill="#f0fdf4", stroke=FIELD, sw=2))
    f.append(text(370, 105, "Плече A (Опорна фаза φ_A)", size=12, color=FIELD, bold=True))

    # Плече B (нижнє - сегмент 1)
    f.append(rect(230, 255, 140, 30, fill="#fff7ed", stroke=POS, sw=2))
    f.append(text(300, 275, "Плече B1", size=12, color=POS, bold=True))

    # Керувальний затвор (розміщено поруч з плечем B, на y=235..295, x=380..440)
    f.append(rect(380, 240, 65, 60, fill="#fed7aa", stroke="#f97316", sw=2, rx=4))
    f.append(mtext(412.5, 260, "Затвор\nI_gate", size=11, color="#c2410c", bold=True))
    f.append(arrow(412.5, 195, 412.5, 240, color="#c2410c", sw=2))
    f.append(text(412.5, 185, "Струм I_ctrl (зсув фази Δφ)", size=11, color="#c2410c", bold=True))

    # Плече B (нижнє - сегмент 2)
    f.append(rect(455, 255, 55, 30, fill="#fff7ed", stroke=POS, sw=2))
    f.append(text(482.5, 275, "B2", size=12, color=POS, bold=True))

    # Зведення плечей в один вихідний хвилевід
    f.append(line(510, 100, 560, 185, color=FIELD, sw=3))
    f.append(line(510, 270, 560, 185, color=FIELD, sw=3))

    f.append(arrow(560, 185, 610, 185, color=INK, sw=2.5))

    # Вихідний детектор
    f.append(fitbox(610, 150, 120, 70, "Вихідний\nдетектор\n(BLS / CPW)", size=11, bold=True, fill="#e0e7ff", stroke=INK))

    # Нижній інфо-блок інтерференції
    f.append(fitbox(30, 295, 340, 50, "Конструктивна інтерференція (Δφ = 0):\nСигнал на виході високий → Логічна 1", size=11, pad=6, fill="#f0fdf4", stroke="#4ade80"))
    f.append(fitbox(390, 295, 350, 50, "Деструктивна інтерференція (Δφ = π):\nСигнал гаситься в нуль → Логічний 0", size=11, pad=6, fill="#fdf2f2", stroke="#f87171"))

    render(os.path.join(IMG_DIR, 'magnonic-mach-zehnder-gate.svg'), w, h, *f)


def main():
    fig_charge_vs_magnonic()
    fig_gilbert_damping_precession()
    fig_magnonic_band_structure()
    fig_magnonic_mach_zehnder_gate()
    print("Усі 4 фігури магноніки успішно згенеровано.")


if __name__ == "__main__":
    main()
