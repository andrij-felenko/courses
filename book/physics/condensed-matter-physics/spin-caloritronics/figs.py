# -*- coding: utf-8 -*-
"""Фігури до теми «Спінова калоритроніка та термоспінові явища».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def fig_spin_seebeck_effect():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Поздовжній спіновий ефект Зеєбека (LSSE) у двошаровій структурі YIG / Pt", size=16, bold=True, color=INK))

    # Top panel: Platinum (Pt) - Heavy Metal
    f.append(rect(140, 70, 480, 80, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    f.append(text(380, 95, "Важкий метал (Pt) — спін-орбітальна взаємодія", size=14, bold=True, color="#1e293b"))
    f.append(text(380, 115, "Обернений спіновий ефект Холла (ISHE): E_ISHE = θ_SH (ρ/ħ) (J_s × σ)", size=11, italic=True, color="#334155"))
    f.append(text(550, 135, "Вольтметр V_ISHE", size=11, bold=True, color=POS))

    # Interface line
    f.append(line(140, 150, 620, 150, color=FIELD, sw=3, dash="6,4"))
    f.append(text(380, 168, "Межа розділу YIG / Pt (спінова провідність змішування g_↑↓)", size=11, bold=True, color=FIELD))

    # Bottom panel: Yttrium Iron Garnet (YIG) - Ferromagnetic Insulator
    f.append(rect(140, 180, 480, 150, fill="#fef3c7", stroke="#d97706", sw=2, rx=4))
    f.append(text(380, 205, "Феромагнітний ізолятор (YIG, Y3Fe5O12) — зарядний струм J_c = 0", size=14, bold=True, color="#92400e"))
    f.append(text(380, 225, "Магнонний термотранспорт спінового моменту", size=12, italic=True, color="#b45309"))

    # Magnon spin current arrow (vertical, injection into Pt)
    f.append(arrow(380, 280, 380, 110, color=POS, sw=3))
    f.append(text(430, 138, "Спіновий струм J_s", size=12, bold=True, color=POS))

    # Temperature gradient (horizontal)
    f.append(arrow(60, 370, 700, 370, color=NEG, sw=2.5))
    f.append(text(70, 355, "Т1 (Гаряче)", size=12, bold=True, color=POS))
    f.append(text(670, 355, "Т2 (Холодне)", size=12, bold=True, color=NEG))
    f.append(text(380, 395, "Тепловий градієнт ∇T (створює магнонне нерівноважне накопичення)", size=12, bold=True, color=INK))

    # Magnetization vector M
    f.append(arrow(180, 290, 270, 290, color="#b45309", sw=3))
    f.append(text(225, 275, "Магнітний момент M", size=11, bold=True, color="#b45309"))

    render(os.path.join(IMG_DIR, 'spin-seebeck-effect.svg'), W, H, "\n".join(f))

def fig_spin_peltier_effect():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28, "Спіновий ефект Пельтьє (SPE): тепловий потік під дією спінового струму", size=16, bold=True, color=INK))

    # Left box: Heating / Cooling at Interface
    f.append(rect(100, 70, 560, 260, fill="#f8fafc", stroke=BORDER, sw=2, rx=6))

    # Platinum top layer
    f.append(rect(160, 90, 440, 70, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    f.append(text(380, 112, "Пропускання електричного струму J_c у важкому металі (Pt)", size=13, bold=True, color="#1e293b"))
    f.append(arrow(200, 135, 560, 135, color=NEG, sw=2.5))
    f.append(text(380, 150, "Зарядний струм J_c (генерує J_s через SHE)", size=11, bold=True, color=NEG))

    # Spin injection arrow downwards into YIG
    f.append(arrow(380, 160, 380, 230, color=POS, sw=3))
    f.append(text(430, 195, "Спіновий струм J_s", size=12, bold=True, color=POS))

    # Interface thermal absorption/emission nodes
    f.append(circle(260, 230, 20, fill="#fee2e2", stroke=POS, sw=2))
    f.append(text(260, 235, "+ΔQ", size=13, bold=True, color=POS))
    f.append(text(260, 268, "Нагрівання", size=11, bold=True, color=POS))

    f.append(circle(500, 230, 20, fill="#dbeafe", stroke=NEG, sw=2))
    f.append(text(500, 235, "-ΔQ", size=13, bold=True, color=NEG))
    f.append(text(500, 268, "Охолодження", size=11, bold=True, color=NEG))

    # Bottom ferromagnetic layer
    f.append(rect(160, 230, 440, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    f.append(text(380, 285, "Феромагнетик / Ізолятор (YIG)", size=13, bold=True, color="#92400e"))

    f.append(text(W / 2, H - 20, "Інжектований спіновий струм спричиняє локальне поглинання або виділення тепла ΔQ = T S_S J_s", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-peltier-effect.svg'), W, H, "\n".join(f))

def fig_spin_nernst_effect():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28, "Порівняння термоспінових та термоелектричних поперечних явищ", size=16, bold=True, color=INK))

    # Three panels for comparative understanding: ANE vs SNE vs ISHE
    panel_w = 220
    panel_h = 280
    y_top = 55

    panels = [
        ("Аномальний ефект Нернста (ANE)", "Феромагнетик\n∇T_x × M_z → E_y\nЕлектричний струм J_c", "#fef2f2", POS, "ane"),
        ("Спіновий ефект Нернста (SNE)", "Немагнітний SOC метал\n∇T_x → Поперечний J_s_y\nСпінова поляризація σ_z", "#f0fdf4", FIELD, "sne"),
        ("Обернений ефект Холла (ISHE)", "Важкий метал\nJ_s_z × σ_y → E_y\nПеретворення спіну в заряд", "#eff6ff", NEG, "ishe")
    ]

    for idx, (p_title, p_desc, bg_col, main_col, p_type) in enumerate(panels):
        x0 = 25 + idx * 240
        f.append(rect(x0, y_top, panel_w, panel_h, fill=bg_col, stroke=BORDER, rx=6))
        f.append(text(x0 + panel_w / 2, y_top + 25, p_title, size=12, bold=True, color=main_col))

        # Internal coordinate system representation
        cx = x0 + panel_w / 2
        cy = y_top + 130

        # Thermal gradient arrow
        f.append(arrow(cx - 60, cy, cx + 60, cy, color=POS, sw=2.5))
        f.append(text(cx, cy - 12, "∇T_x", size=12, bold=True, color=POS))

        # Transverse output arrow
        if p_type == "ane":
            f.append(arrow(cx, cy + 40, cx, cy - 50, color=NEG, sw=2.5))
            f.append(text(cx + 25, cy - 25, "E_y (заряд)", size=11, bold=True, color=NEG))
        elif p_type == "sne":
            f.append(arrow(cx, cy + 40, cx, cy - 50, color=FIELD, sw=3))
            f.append(text(cx + 25, cy - 25, "J_s_y (спін)", size=11, bold=True, color=FIELD))
            f.append(circle(cx, cy, 8, fill=BG, stroke=FIELD, sw=2))
            f.append(circle(cx, cy, 3, fill=FIELD, stroke="none"))
            f.append(text(cx, cy + 22, "σ_z", size=10, bold=True, color=FIELD))
        elif p_type == "ishe":
            f.append(arrow(cx, cy + 40, cx, cy - 50, color=NEG, sw=2.5))
            f.append(text(cx + 25, cy - 25, "E_y (ISHE)", size=11, bold=True, color=NEG))

        # Description text at bottom of panel
        lines = p_desc.split("\n")
        for i_line, line_str in enumerate(lines):
            f.append(text(cx, y_top + panel_h - 65 + i_line * 18, line_str, size=11, bold=(i_line==0), color=INK))

    f.append(text(W / 2, H - 15, "Спіновий ефект Нернста генерує чисто спіновий струм без використання феромагнетика", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-nernst-effect.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_spin_seebeck_effect()
    fig_spin_peltier_effect()
    fig_spin_nernst_effect()
