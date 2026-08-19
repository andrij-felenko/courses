# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Тунельний діод (діод Лео Есакі)».
book/electronics/components/tunnel-diode
"""

import sys
import os

# scripts/ чотири рівні вище (book/electronics/components/tunnel-diode -> root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_band_diagrams():
    """Енергетичні зонні діаграми тунельного p-n переходу в чотирьох режимах зміщення."""
    w, h = 920, 520
    frags = []

    panels = [
        {"x": 20, "y": 45, "title": "1. Зворотне зміщення (V < 0)", "sub": "Тунелювання p-валентна → n-провідність (величезний струм)"},
        {"x": 470, "y": 45, "title": "2. Теплова рівновага (V = 0)", "sub": "Рівні Фермі вирівняні (зустрічні потоки скомпенсовані, I = 0)"},
        {"x": 20, "y": 280, "title": "3. Піковий прямий струм (V = V_P)", "sub": "Максимальне перекриття n-провідність → p-валентна (I = I_P)"},
        {"x": 470, "y": 280, "title": "4. Зона западини (V = V_V)", "sub": "Зони розійшлися, пряме тунелювання припинено (I = I_V)"}
    ]

    pw, ph = 430, 215

    for p in panels:
        px, py = p["x"], p["y"]
        frags.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=8))
        frags.append(text(px + 14, py + 22, p["title"], size=13, bold=True, anchor="start", color=INK))
        frags.append(text(px + 14, py + 38, p["sub"], size=10.5, color=MUTED, anchor="start"))
        frags.append(line(px + 215, py + 48, px + 215, py + ph - 10, color="#9ca3af", sw=1, dash="3,3"))
        frags.append(text(px + 105, py + ph - 14, "n++ область", size=11, bold=True, color="#1e40af"))
        frags.append(text(px + 325, py + ph - 14, "p++ область", size=11, bold=True, color="#b91c1c"))

    # Панель 1: V < 0
    p1 = panels[0]
    x0, y0 = p1["x"], p1["y"]
    frags.append(rect(x0 + 20, y0 + 100, 160, 45, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(x0 + 100, y0 + 125, "Зона провідності (E_c)", size=10, bold=True, color="#1e40af"))
    frags.append(rect(x0 + 20, y0 + 160, 160, 25, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 100, y0 + 176, "Валентна зона (E_v)", size=9.5, color=MUTED))
    frags.append(line(x0 + 20, y0 + 115, x0 + 180, y0 + 115, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 195, y0 + 117, "E_Fn", size=10, bold=True, color=POS, anchor="start"))

    frags.append(rect(x0 + 250, y0 + 55, 160, 30, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 330, y0 + 73, "Зона провідності (E_c)", size=9.5, color=MUTED))
    frags.append(rect(x0 + 250, y0 + 100, 160, 50, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(x0 + 330, y0 + 130, "Валентна зона (E_v)", size=10, bold=True, color="#b91c1c"))
    frags.append(line(x0 + 250, y0 + 140, x0 + 410, y0 + 140, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 235, y0 + 142, "E_Fp", size=10, bold=True, color=POS, anchor="end"))

    frags.append(arrow(x0 + 250, y0 + 120, x0 + 180, y0 + 120, color=POS, sw=2.5))
    frags.append(text(x0 + 215, y0 + 105, "e⁻ тунелювання", size=9.5, bold=True, color=POS))

    # Панель 2: V = 0
    p2 = panels[1]
    x0, y0 = p2["x"], p2["y"]
    frags.append(rect(x0 + 20, y0 + 75, 160, 50, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(x0 + 100, y0 + 102, "Зона провідності (E_c)", size=10, bold=True, color="#1e40af"))
    frags.append(rect(x0 + 20, y0 + 140, 160, 35, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 100, y0 + 160, "Валентна зона (E_v)", size=9.5, color=MUTED))

    frags.append(rect(x0 + 250, y0 + 60, 160, 35, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 330, y0 + 80, "Зона провідності (E_c)", size=9.5, color=MUTED))
    frags.append(rect(x0 + 250, y0 + 110, 160, 65, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(x0 + 330, y0 + 145, "Валентна зона (E_v)", size=10, bold=True, color="#b91c1c"))

    frags.append(line(x0 + 20, y0 + 95, x0 + 410, y0 + 95, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 215, y0 + 90, "E_F (рівновага)", size=9.5, bold=True, color=POS))

    frags.append(arrow(x0 + 180, y0 + 115, x0 + 245, y0 + 115, color="#2563eb", sw=1.5))
    frags.append(arrow(x0 + 245, y0 + 125, x0 + 180, y0 + 125, color="#dc2626", sw=1.5))
    frags.append(text(x0 + 215, y0 + 145, "I_net = 0", size=10, bold=True, color=INK))

    # Панель 3: V = V_P
    p3 = panels[2]
    x0, y0 = p3["x"], p3["y"]
    frags.append(rect(x0 + 20, y0 + 55, 160, 55, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(x0 + 100, y0 + 85, "Зона провідності (E_c)", size=10, bold=True, color="#1e40af"))
    frags.append(rect(x0 + 20, y0 + 130, 160, 45, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 100, y0 + 155, "Валентна зона (E_v)", size=9.5, color=MUTED))
    frags.append(line(x0 + 20, y0 + 70, x0 + 180, y0 + 70, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 195, y0 + 72, "E_Fn", size=10, bold=True, color=POS, anchor="start"))

    frags.append(rect(x0 + 250, y0 + 75, 160, 30, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 330, y0 + 93, "Зона провідності (E_c)", size=9.5, color=MUTED))
    frags.append(rect(x0 + 250, y0 + 120, 160, 55, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(x0 + 330, y0 + 150, "Валентна зона (E_v)", size=10, bold=True, color="#b91c1c"))
    frags.append(line(x0 + 250, y0 + 135, x0 + 410, y0 + 135, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 235, y0 + 137, "E_Fp", size=10, bold=True, color=POS, anchor="end"))

    frags.append(arrow(x0 + 180, y0 + 90, x0 + 250, y0 + 90, color=FIELD, sw=2.5))
    frags.append(arrow(x0 + 180, y0 + 105, x0 + 250, y0 + 105, color=FIELD, sw=2.5))
    frags.append(text(x0 + 215, y0 + 75, "Макс. струм I_P", size=10, bold=True, color=FIELD))

    # Панель 4: V = V_V
    p4 = panels[3]
    x0, y0 = p4["x"], p4["y"]
    frags.append(rect(x0 + 20, y0 + 45, 160, 50, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(x0 + 100, y0 + 72, "Зона провідності (E_c)", size=10, bold=True, color="#1e40af"))
    frags.append(rect(x0 + 20, y0 + 115, 160, 60, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 100, y0 + 145, "Валентна зона (E_v)", size=9.5, color=MUTED))
    frags.append(line(x0 + 20, y0 + 58, x0 + 180, y0 + 58, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 195, y0 + 60, "E_Fn", size=10, bold=True, color=POS, anchor="start"))

    frags.append(rect(x0 + 250, y0 + 90, 160, 30, fill="#f3f4f6", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(x0 + 330, y0 + 108, "Зона провідності (E_c)", size=9.5, color=MUTED))
    frags.append(rect(x0 + 250, y0 + 140, 160, 35, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(x0 + 330, y0 + 160, "Валентна зона (E_v)", size=10, bold=True, color="#b91c1c"))
    frags.append(line(x0 + 250, y0 + 155, x0 + 410, y0 + 155, color=POS, sw=1.5, dash="4,2"))
    frags.append(text(x0 + 235, y0 + 157, "E_Fp", size=10, bold=True, color=POS, anchor="end"))

    frags.append(line(x0 + 180, y0 + 100, x0 + 250, y0 + 130, color="#dc2626", sw=2))
    frags.append(line(x0 + 180, y0 + 130, x0 + 250, y0 + 100, color="#dc2626", sw=2))
    frags.append(text(x0 + 215, y0 + 90, "Заборонено", size=9.5, bold=True, color="#dc2626"))
    frags.append(text(x0 + 215, y0 + 140, "Струм I_V (мінімум)", size=9.5, color=MUTED))

    frags.append(text(w / 2, 22, "Еволюція енергетичних зон тунельного діода при зміні напруги", size=15, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "band-diagrams.svg"), w, h, *frags)


def fig_iv_curve():
    """Вольт-амперна характеристика тунельного діода з розкладом на складові струму."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 24, "Повна вольт-амперна характеристика тунельного діода та складові струму", size=15, bold=True, color=INK))

    ox, oy = 160, 390
    frags.append(arrow(ox - 120, oy, ox + 700, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy + 40, ox, oy - 340, color=LINE, sw=1.8))
    frags.append(text(ox + 705, oy + 5, "Напруга V (мВ)", size=12, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy - 345, "Струм I (мА)", size=12, bold=True, anchor="end"))

    v_p_x = ox + 80
    v_v_x = ox + 240
    v_f_x = ox + 400
    frags.append(line(v_p_x, oy - 5, v_p_x, oy + 5, color=LINE, sw=1.5))
    frags.append(text(v_p_x, oy + 22, "V_P (65 мВ)", size=11, bold=True, color=POS))
    frags.append(line(v_v_x, oy - 5, v_v_x, oy + 5, color=LINE, sw=1.5))
    frags.append(text(v_v_x, oy + 22, "V_V (350 мВ)", size=11, bold=True, color=NEG))
    frags.append(line(v_f_x, oy - 5, v_f_x, oy + 5, color=LINE, sw=1.5))
    frags.append(text(v_f_x, oy + 22, "V_F (500 мВ)", size=11, color=MUTED))

    i_p_y = oy - 270
    i_v_y = oy - 45
    frags.append(line(ox - 5, i_p_y, ox + 5, i_p_y, color=LINE, sw=1.5))
    frags.append(text(ox - 12, i_p_y + 4, "I_P (5 мА)", size=11, bold=True, color=POS, anchor="end"))
    frags.append(line(ox - 5, i_v_y, ox + 5, i_v_y, color=LINE, sw=1.5))
    frags.append(text(ox - 12, i_v_y + 4, "I_V (0.5 мА)", size=11, bold=True, color=NEG, anchor="end"))

    frags.append(line(v_p_x, oy, v_p_x, i_p_y, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(line(ox, i_p_y, v_p_x, i_p_y, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(line(v_v_x, oy, v_v_x, i_v_y, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(line(ox, i_v_y, v_v_x, i_v_y, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(line(v_f_x, oy, v_f_x, i_p_y, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(line(v_p_x, i_p_y, v_f_x, i_p_y, color="#9ca3af", sw=1, dash="3,3"))

    # 1. Тунельний струм I_tu (пунктир зелений)
    frags.append('<path d="M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' %
                 (ox - 90, oy - 290, ox - 30, oy - 50, ox, oy, v_p_x, i_p_y,
                  v_p_x + 80, oy - 240, v_v_x - 30, oy, v_v_x + 20, oy, FIELD))

    # 2. Надлишковий струм I_ex (пунктир синій)
    frags.append('<path d="M %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' %
                 (ox, oy, ox + 130, oy - 15, v_v_x, i_v_y, v_v_x + 130, oy - 70, NEG))

    # 3. Дифузійний струм I_diff (пунктир фіолетовий)
    frags.append('<path d="M %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' %
                 (v_v_x - 50, oy, v_v_x + 30, oy - 15, v_f_x, i_p_y, ox + 490, oy - 330, "#7c3aed"))

    # 4. Сумарна ВАХ (червона лінія)
    frags.append('<path d="M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="3"/>' %
                 (ox - 90, oy - 290, ox - 30, oy - 50, ox, oy, v_p_x, i_p_y,
                  v_p_x + 80, oy - 220, v_v_x - 40, i_v_y + 10, v_v_x, i_v_y,
                  v_v_x + 50, i_v_y + 5, v_f_x - 30, oy - 180, ox + 490, oy - 330, POS))

    frags.append(circle(v_p_x, i_p_y, 5, fill=POS, stroke="#ffffff", sw=2))
    frags.append(circle(v_v_x, i_v_y, 5, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(circle(v_f_x, i_p_y, 4.5, fill="#7c3aed", stroke="#ffffff", sw=2))

    # Підпис ділянки ВДО
    frags.append(rect(ox + 105, oy - 195, 115, 40, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    frags.append(text(ox + 162, oy - 180, "Ділянка ВДО", size=10.5, bold=True, color=POS))
    frags.append(text(ox + 162, oy - 165, "dI/dV < 0", size=9.5, color=POS))

    # Зворотний тунельний струм
    frags.append(rect(ox - 145, oy - 200, 130, 42, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=5))
    frags.append(text(ox - 80, oy - 185, "Зворотне тунелювання", size=10.5, bold=True, color="#1e40af"))
    frags.append(text(ox - 80, oy - 169, "«Обернений діод»", size=10, color="#1e40af"))

    # Легенда розміщена праворуч у безпечній зоні (lx = 670, ly = 55)
    lx, ly = 670, 55
    frags.append(rect(lx, ly, 215, 140, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(lx + 107, ly + 20, "Складові струму ВАХ", size=11.5, bold=True, color=INK))

    frags.append(line(lx + 12, ly + 45, lx + 38, ly + 45, color=POS, sw=3))
    frags.append(text(lx + 46, ly + 49, "Сумарний струм I(V)", size=10, bold=True, anchor="start", color=POS))

    frags.append(line(lx + 12, ly + 70, lx + 38, ly + 70, color=FIELD, sw=1.8, dash="5,3"))
    frags.append(text(lx + 46, ly + 74, "Тунельний струм I_tu", size=10, anchor="start", color=FIELD))

    frags.append(line(lx + 12, ly + 95, lx + 38, ly + 95, color=NEG, sw=1.8, dash="5,3"))
    frags.append(text(lx + 46, ly + 99, "Надлишковий струм I_ex", size=10, anchor="start", color=NEG))

    frags.append(line(lx + 12, ly + 120, lx + 38, ly + 120, color="#7c3aed", sw=1.8, dash="5,3"))
    frags.append(text(lx + 46, ly + 124, "Дифузійний струм I_diff", size=10, anchor="start", color="#7c3aed"))

    render(os.path.join(IMG_DIR, "tunnel-diode-iv-curve.svg"), w, h, *frags)


def fig_equivalent_circuit():
    """Малосигнальна еквівалентна схема тунельного діода та частотна залежність імпедансу."""
    w, h = 880, 440
    frags = []

    frags.append(text(w / 2, 22, "Малосигнальна еквівалентна схема та активний імпеданс тунельного діода", size=15, bold=True, color=INK))

    sx, sy = 40, 60
    sw_box, sh_box = 400, 350
    frags.append(rect(sx, sy, sw_box, sh_box, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(sx + sw_box / 2, sy + 25, "Малосигнальна схема заміщення", size=13, bold=True, color=INK))

    cy = sy + 180
    frags.append(circle(sx + 30, cy, 4.5, fill=INK, stroke=INK))
    frags.append(text(sx + 30, cy - 14, "Анод", size=11, bold=True))

    frags.append(line(sx + 30, cy, sx + 60, cy, color=LINE, sw=2))
    frags.append(rect(sx + 60, cy - 14, 50, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(sx + 85, cy + 5, "L_s", size=11, bold=True))
    frags.append(text(sx + 85, cy + 30, "0.1–1 нГн", size=9.5, color=MUTED))

    frags.append(line(sx + 110, cy, sx + 135, cy, color=LINE, sw=2))

    frags.append(rect(sx + 135, cy - 14, 50, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(sx + 160, cy + 5, "R_s", size=11, bold=True))
    frags.append(text(sx + 160, cy + 30, "0.5–2 Ом", size=9.5, color=MUTED))

    frags.append(line(sx + 185, cy, sx + 220, cy, color=LINE, sw=2))
    frags.append(circle(sx + 220, cy, 3.5, fill=INK, stroke=INK))

    frags.append(line(sx + 220, cy, sx + 220, cy - 60, color=LINE, sw=2))
    frags.append(line(sx + 220, cy - 60, sx + 250, cy - 60, color=LINE, sw=2))
    frags.append(rect(sx + 250, cy - 75, 65, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(sx + 282, cy - 55, "−R_N", size=11.5, bold=True, color=POS))
    frags.append(text(sx + 282, cy - 83, "ВДО переходу", size=9.5, color=POS))
    frags.append(line(sx + 315, cy - 60, sx + 345, cy - 60, color=LINE, sw=2))
    frags.append(line(sx + 345, cy - 60, sx + 345, cy, color=LINE, sw=2))

    frags.append(line(sx + 220, cy, sx + 220, cy + 60, color=LINE, sw=2))
    frags.append(line(sx + 220, cy + 60, sx + 250, cy + 60, color=LINE, sw=2))
    frags.append(rect(sx + 250, cy + 45, 65, 30, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=3))
    frags.append(text(sx + 282, cy + 65, "C_j", size=11.5, bold=True, color="#0369a1"))
    frags.append(text(sx + 282, cy + 90, "1–10 пФ", size=9.5, color="#0369a1"))
    frags.append(line(sx + 315, cy + 60, sx + 345, cy + 60, color=LINE, sw=2))
    frags.append(line(sx + 345, cy + 60, sx + 345, cy, color=LINE, sw=2))

    frags.append(circle(sx + 345, cy, 3.5, fill=INK, stroke=INK))
    frags.append(line(sx + 345, cy, sx + 375, cy, color=LINE, sw=2))
    frags.append(circle(sx + 375, cy, 4.5, fill=INK, stroke=INK))
    frags.append(text(sx + 375, cy - 14, "Катод", size=11, bold=True))

    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,3"/>' %
                 (sx + 205, cy - 100, 155, 205))
    frags.append(text(sx + 282, cy + 120, "Внутрішній p-n перехід", size=10, bold=True, color="#b45309"))

    gx, gy = 470, 60
    gw_box, gh_box = 380, 350
    frags.append(rect(gx, gy, gw_box, gh_box, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(gx + gw_box / 2, gy + 25, "Активна частина імпедансу Re[Z(f)]", size=13, bold=True, color=INK))

    gox, goy = gx + 50, gy + 210
    frags.append(arrow(gox, goy, gox + 300, goy, color=LINE, sw=1.5))
    frags.append(arrow(gox, goy + 110, gox, goy - 140, color=LINE, sw=1.5))
    frags.append(text(gox + 305, goy + 5, "Частота f", size=11, bold=True, anchor="start"))
    frags.append(text(gox - 8, goy - 145, "Re[Z]", size=11, bold=True, anchor="end"))

    frags.append(text(gox - 10, goy + 4, "0", size=10, color=MUTED, anchor="end"))

    frags.append(line(gox, goy - 45, gox + 280, goy - 45, color="#9ca3af", sw=1, dash="3,3"))
    frags.append(text(gox - 8, goy - 42, "+R_s", size=10.5, color=MUTED, anchor="end"))

    frags.append(text(gox - 8, goy + 85, "−(R_N−R_s)", size=10, bold=True, color=POS, anchor="end"))

    f_max_x = gox + 190
    frags.append('<path d="M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' %
                 (gox, goy + 85, gox + 80, goy + 80, gox + 140, goy + 35, f_max_x, goy,
                  f_max_x + 40, goy - 30, gox + 250, goy - 42, gox + 280, goy - 44, POS))

    # Точка f_max без перетину з лінією
    frags.append(circle(f_max_x, goy, 5, fill=POS, stroke="#ffffff", sw=2))
    frags.append(line(f_max_x, goy - 60, f_max_x, goy - 5, color=POS, sw=1, dash="3,3"))
    frags.append(text(f_max_x + 8, goy + 20, "f_max (гранична частота)", size=10.5, bold=True, color=POS, anchor="start"))

    frags.append(rect(gox + 5, goy + 5, f_max_x - gox - 10, 75, fill="#fef2f2", stroke="none"))
    frags.append(text((gox + f_max_x) / 2 - 5, goy + 45, "Активна зона (Re[Z] < 0)", size=10, bold=True, color=POS))
    frags.append(text((gox + f_max_x) / 2 - 5, goy + 60, "Генерація та підсилення", size=9, color=POS))

    render(os.path.join(IMG_DIR, "equivalent-circuit-rf.svg"), w, h, *frags)


def fig_load_line():
    """Навантажувальна пряма, режими стійкості та пікосекундне перемикання."""
    w, h = 900, 460
    frags = []

    frags.append(text(w / 2, 22, "Навантажувальна пряма та динаміка тригерного перемикання", size=15, bold=True, color=INK))

    ox, oy = 90, 390
    frags.append(arrow(ox - 20, oy, ox + 480, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy + 20, ox, oy - 340, color=LINE, sw=1.8))
    frags.append(text(ox + 485, oy + 5, "Напруга V (мВ)", size=12, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy - 345, "Струм I (мА)", size=12, bold=True, anchor="end"))

    v_p_x = ox + 80
    i_p_y = oy - 270
    v_v_x = ox + 220
    i_v_y = oy - 45
    v_f_x = ox + 360

    # ВАХ діода (не заходить у правий бік занадто далеко)
    frags.append('<path d="M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' %
                 (ox, oy, ox + 30, oy - 150, ox + 50, i_p_y + 10, v_p_x, i_p_y,
                  v_p_x + 60, oy - 230, v_v_x - 40, i_v_y + 15, v_v_x, i_v_y,
                  v_v_x + 40, i_v_y + 5, v_f_x - 30, oy - 180, ox + 430, oy - 310, INK))

    # Навантажувальна пряма: I = (E_0 - V) / R_L
    e_0_x = ox + 410
    e_0_rl_y = oy - 290
    frags.append(line(ox, e_0_rl_y, e_0_x, oy, color="#2563eb", sw=2))
    frags.append(text(e_0_x, oy + 20, "E_0", size=11.5, bold=True, color="#2563eb"))
    frags.append(text(ox - 10, e_0_rl_y + 4, "E_0 / R_L", size=11, bold=True, color="#2563eb", anchor="end"))

    pt_a_x, pt_a_y = ox + 65, oy - 250
    frags.append(circle(pt_a_x, pt_a_y, 6, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(pt_a_x - 12, pt_a_y - 12, "Точка A («0»)", size=11, bold=True, color=FIELD, anchor="end"))
    frags.append(text(pt_a_x - 12, pt_a_y + 4, "V < V_P", size=9.5, color=FIELD, anchor="end"))

    pt_c_x, pt_c_y = ox + 165, oy - 175
    frags.append(circle(pt_c_x, pt_c_y, 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(pt_c_x + 12, pt_c_y - 10, "Точка C (нестійка)", size=10.5, bold=True, color=POS, anchor="start"))
    frags.append(text(pt_c_x + 12, pt_c_y + 6, "R_L > R_N", size=9.5, color=POS, anchor="start"))

    pt_b_x, pt_b_y = ox + 350, oy - 50
    frags.append(circle(pt_b_x, pt_b_y, 6, fill="#7c3aed", stroke="#ffffff", sw=2))
    frags.append(text(pt_b_x + 12, pt_b_y - 10, "Точка B («1»)", size=11, bold=True, color="#7c3aed", anchor="start"))
    frags.append(text(pt_b_x + 12, pt_b_y + 6, "V ≈ V_F", size=9.5, color="#7c3aed", anchor="start"))

    frags.append(arrow(v_p_x, i_p_y, v_f_x - 15, i_p_y, color=POS, sw=2.5))
    frags.append(text((v_p_x + v_f_x) / 2, i_p_y - 12, "Стрибок A → B (τ ≈ 20–50 пс)", size=10.5, bold=True, color=POS))

    frags.append(arrow(v_v_x, i_v_y, ox + 25, i_v_y, color=NEG, sw=2.5))
    frags.append(text((v_v_x + ox) / 2 + 5, i_v_y + 22, "Стрибок B → A", size=10.5, bold=True, color=NEG))

    # Пояснювальний блок у правій частині (bx = 580, by = 60)
    bx, by = 580, 60
    frags.append(rect(bx, by, 300, 140, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(bx + 150, by + 22, "Критерій бістабільного тригера", size=11.5, bold=True, color=INK))
    frags.append(text(bx + 15, by + 48, "1. Навантажувальний опір: R_L > |R_N|", size=10.5, anchor="start", color=INK))
    frags.append(text(bx + 15, by + 72, "2. Дві стійкі точки (A, B) + одна нестійка (C)", size=9.5, anchor="start", color=MUTED))
    frags.append(text(bx + 15, by + 96, "3. Швидкість перемикання обмежена лише C_j", size=9.5, anchor="start", color=MUTED))
    frags.append(text(bx + 15, by + 120, "4. Час фронту: t_r ≈ (V_F - V_P) · C_j / I_P", size=9.5, bold=True, anchor="start", color=POS))

    render(os.path.join(IMG_DIR, "load-line-switching.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_band_diagrams()
    fig_iv_curve()
    fig_equivalent_circuit()
    fig_load_line()
    print("All figures generated successfully.")
