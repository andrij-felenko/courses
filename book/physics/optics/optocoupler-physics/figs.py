# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def svg_polygon(pts, fill='#fef08a', stroke='#eab308', sw=1):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Фізична структура та оптична геометрія оптрона
# ═══════════════════════════════════════════════════════════════════════════
def fig_optocoupler_geometry():
    W, H = 720, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Фізична структура та оптичні межі в геометрії оптрона', 16, INK, 'middle', bold=True))

    # Зовнішній корпусуючий епоксидний непрозорий корпус
    f.append(rect(40, 50, 640, 310, fill='#f8fafc', stroke='#94a3b8', sw=1.5, rx=8))
    f.append(text(55, 72, 'Непрозорий корпус (епоксидний компаунд)', 11, MUTED, 'start', bold=True))

    # Ліва частина (Вхід/Світлодіод)
    led_x, led_y = 110, 220
    f.append(rect(led_x, led_y, 90, 60, fill='#fde68a', stroke='#d97706', sw=2, rx=4))
    f.append(text(led_x + 45, led_y + 25, 'Світлодіод', 12, INK, 'middle', bold=True))
    f.append(text(led_x + 45, led_y + 42, 'GaAs (n = 3.5)', 10, '#b45309', 'middle'))

    # Виводи світлодіода
    f.append(line(60, led_y + 30, led_x, led_y + 30, color='#d97706', sw=4))
    f.append(text(55, led_y + 34, 'Анод', 11, INK, 'end', bold=True))

    # Права частина (Вихід/Фотодетектор)
    det_x, det_y = 520, 220
    f.append(rect(det_x, det_y, 90, 60, fill='#bfdbfe', stroke='#1d4ed8', sw=2, rx=4))
    f.append(text(det_x + 45, det_y + 25, 'Фотодіод', 12, INK, 'middle', bold=True))
    f.append(text(det_x + 45, det_y + 42, 'Кремній (n = 3.4)', 10, '#1e40af', 'middle'))

    # Виводи фотодетектора
    f.append(line(det_x + 90, det_y + 30, 660, det_y + 30, color='#1d4ed8', sw=4))
    f.append(text(665, det_y + 34, 'Колектор', 11, INK, 'start', bold=True))

    # Прозорий ізоляційний діелектричний бар'єр (силікон / поліімид)
    bar_x, bar_y = 230, 95
    bar_w, bar_h = 260, 235
    f.append(rect(bar_x, bar_y, bar_w, bar_h, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=6))
    f.append(text(bar_x + bar_w / 2, bar_y + 22, "Прозорий бар'єр ізоляції (n = 1.45)", 11, '#0369a1', 'middle', bold=True))
    f.append(text(bar_x + bar_w / 2, bar_y + 38, 'Силікон / Поліізобутилен (d = 0.2..0.4 мм)', 10, MUTED, 'middle'))

    # Оптичний конус випромінювання та критичний кут Снеліуса
    f.append(svg_polygon([(led_x + 90, led_y + 30), (bar_x + bar_w, bar_y + 50), (bar_x + bar_w, bar_y + 190)],
                         fill='#fef08a', stroke='#eab308', sw=1))

    # Фотонні промені
    f.append(arrow(led_x + 90, led_y + 30, det_x, det_y + 10, color='#eab308', sw=2))
    f.append(arrow(led_x + 90, led_y + 30, det_x, det_y + 30, color='#eab308', sw=2))
    f.append(arrow(led_x + 90, led_y + 30, det_x, det_y + 50, color='#eab308', sw=2))

    # Повне внутрішнє відбиття на межі GaAs-силікон (критичний конус)
    f.append(line(led_x + 90, led_y + 5, led_x + 90 + 40, led_y - 20, color='#dc2626', sw=1.5, dash='4,3'))
    f.append(arrow(led_x + 90 + 40, led_y - 20, led_x + 70, led_y + 45, color='#dc2626', sw=1.5))
    f.append(text(led_x + 100, led_y - 30, 'ПВВ (θ > θ_c ≈ 24.5°)', 10, NEG, 'start', bold=True))

    # Інформаційна картка внизу (поза основним корпусом)
    f.append(fitbox(60, 375, 600, 50,
                    "Електромагнітне випромінювання (λ = 850..940 нм) долає оптичний бар'єр.\n"
                    "Електричний опір ізоляції R_iso > 10¹² Ом, витримувана напруга V_iso = 3.75..5.0 кВ_RMS.",
                    size=10, color=INK, fill='#ffffff', stroke=LINE, sw=1))

    render(os.path.join(IMG, 'optocoupler-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Квантовий каскад перетворення енергії та CTR
# ═══════════════════════════════════════════════════════════════════════════
def fig_ctr_quantum_chain():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Квантовий каскад коефіцієнта передачі струму (CTR)', 16, INK, 'middle', bold=True))

    bw, bh = 110, 80
    y_pos = 110

    blocks = [
        ('Вхідний струм', 'I_in', 'Електрони', '#f1f5f9', INK),
        ('Електролюмінесценція', 'η_int (GaAs)', 'Внутрішня КЕ', '#fef3c7', '#b45309'),
        ('Виведення світла', 'η_ext_LED', 'Закон Снелла', '#fef9c3', '#ca8a04'),
        ('Оптичний транспорт', 'η_opt', 'Геометрія та ПВВ', '#e0f2fe', '#0369a1'),
        ('Фотопоглинання', 'η_det (Si)', 'Генерація e⁻/h⁺', '#dbeafe', '#1e40af'),
    ]

    for i, (b_title, b_param, b_desc, b_fill, b_color) in enumerate(blocks):
        bx = 35 + i * 135
        f.append(rect(bx, y_pos, bw, bh, fill=b_fill, stroke=b_color, sw=1.5, rx=6))
        f.append(text(bx + bw / 2, y_pos + 20, b_title, 10, INK, 'middle', bold=True))
        f.append(text(bx + bw / 2, y_pos + 42, b_param, 12, b_color, 'middle', bold=True))
        f.append(text(bx + bw / 2, y_pos + 62, b_desc, 9, MUTED, 'middle'))

        if i < len(blocks) - 1:
            f.append(arrow(bx + bw + 2, y_pos + bh / 2, bx + 135 - 2, y_pos + bh / 2, color=MUTED, sw=1.8))

    bx_out = 35 + 4 * 135
    f.append(arrow(bx_out + bw / 2, y_pos + bh, bx_out + bw / 2, y_pos + bh + 45, color=POS, sw=2))
    f.append(rect(bx_out - 20, y_pos + bh + 45, bw + 40, 50, fill='#d1fae5', stroke='#059669', sw=2, rx=6))
    f.append(text(bx_out + bw / 2, y_pos + bh + 67, 'Вихідний струм I_out', 11, INK, 'middle', bold=True))
    f.append(text(bx_out + bw / 2, y_pos + bh + 84, 'I_out = I_in · CTR', 10, POS, 'middle', bold=True))

    f.append(fitbox(35, 235, 480, 85,
                    "Формула CTR (Current Transfer Ratio):\n"
                    "CTR = η_int · η_ext_LED · η_opt · η_det · β\n"
                    "Кожен коефіцієнт каскаду становить < 1.0, тому для оптичного фотодіода\n"
                    "типовий CTR становить 0.1%..2%, а для фототранзистора (з підсиленням β) — 50%..500%.",
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'ctr-quantum-chain.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Паразитна ємність C_iso, струм зміщення та оптичний екран
# ═══════════════════════════════════════════════════════════════════════════
def fig_cmti_parasitic_capacitance():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Паразитна ємність бар\'єру C_iso та прозорий оптичний екран (CMTI)', 16, INK, 'middle', bold=True))

    # Схема без екрана (ліворуч)
    f.append(rect(40, 60, 300, 290, fill='#fff1f2', stroke='#fda4af', sw=1.5, rx=6))
    f.append(text(190, 85, 'БЕЗ екранування: Паразитний струм', 12, NEG, 'middle', bold=True))

    # LED
    f.append(rect(60, 120, 50, 140, fill='#fde68a', stroke='#d97706', sw=1.5))
    f.append(text(85, 190, 'LED', 11, INK, 'middle', bold=True))

    # Детектор
    f.append(rect(270, 120, 50, 140, fill='#bfdbfe', stroke='#1d4ed8', sw=1.5))
    f.append(text(295, 190, 'База', 11, INK, 'middle', bold=True))

    # Паразитна ємність
    f.append(line(110, 150, 160, 150, color=NEG, sw=1.5))
    f.append(line(160, 135, 160, 165, color=NEG, sw=2.5))
    f.append(line(175, 135, 175, 165, color=NEG, sw=2.5))
    f.append(line(175, 150, 270, 150, color=NEG, sw=1.5))
    f.append(text(167, 125, 'C_iso ≈ 0.5 pF', 10, NEG, 'middle', bold=True))

    # Струм зміщення I_disp = C_iso * dV/dt
    f.append(arrow(110, 190, 270, 190, color=NEG, sw=2))
    f.append(text(190, 210, 'I_disp = C_iso · (dV/dt)', 10, NEG, 'middle', bold=True))
    f.append(text(190, 226, 'помилкове відмикання!', 10, NEG, 'middle'))

    # Схема З екраном Фарадея (праворуч)
    f.append(rect(380, 60, 300, 290, fill='#f0fdf4', stroke='#86efac', sw=1.5, rx=6))
    f.append(text(530, 85, 'З екраном Фарадея: Захищений детектор', 12, POS, 'middle', bold=True))

    # LED
    f.append(rect(400, 120, 50, 140, fill='#fde68a', stroke='#d97706', sw=1.5))
    f.append(text(425, 190, 'LED', 11, INK, 'middle', bold=True))

    # Прозорий провідний екран (Faraday Shield mesh)
    f.append(line(490, 110, 490, 270, color=POS, sw=3, dash='6,4'))
    f.append(line(490, 270, 490, 300, color=POS, sw=2))
    f.append(line(475, 300, 505, 300, color=POS, sw=2))
    f.append(line(480, 305, 500, 305, color=POS, sw=1.5))
    f.append(line(485, 310, 495, 310, color=POS, sw=1))
    f.append(text(510, 285, 'GND_shield', 9, POS, 'start', bold=True))

    # Детектор
    f.append(rect(610, 120, 50, 140, fill='#bfdbfe', stroke='#1d4ed8', sw=1.5))
    f.append(text(635, 190, 'База', 11, INK, 'middle', bold=True))

    # Струм зміщення стікає в землю
    f.append(arrow(450, 190, 490, 190, color=NEG, sw=1.8))
    f.append(arrow(490, 190, 490, 260, color=POS, sw=2))
    f.append(text(465, 215, 'I_disp стікає', 10, POS, 'middle', bold=True))
    f.append(text(465, 230, 'в землю', 10, POS, 'middle'))

    # Фотони вільно проходять крізь прозорий екран
    f.append(arrow(450, 150, 610, 150, color='#eab308', sw=2))
    f.append(text(530, 140, 'ІЧ-фотони hν', 10, '#b45309', 'middle', bold=True))

    render(os.path.join(IMG, 'cmti-parasitic-capacitance.svg'), W, H, *f)

if __name__ == '__main__':
    fig_optocoupler_geometry()
    fig_ctr_quantum_chain()
    fig_cmti_parasitic_capacitance()
    print("All figures successfully generated in ./img/")
