# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект обмінного зміщення (Exchange Bias)».
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

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Асиметрична петля гістерезису та параметри зміщення ────────────
def fig_hysteresis_shift_exchange_bias():
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 28, "Петля гістерезису з ефектом обмінного зміщення", size=16, bold=True, color=INK))

    # Axes
    ox, oy = 380, 220
    f.append(line(60, oy, 700, oy, color="#94a3b8", sw=1.5))
    f.append(arrow(680, oy, 715, oy, color="#64748b", sw=1.5))
    f.append(text(715, oy + 20, "H (Зовнішнє магнітне поле)", size=12, color=INK, anchor="end"))

    f.append(line(ox, 380, ox, 60, color="#94a3b8", sw=1.5))
    f.append(arrow(ox, 370, ox, 50, color="#64748b", sw=1.5))
    f.append(text(ox + 15, 60, "M (Намагніченість FM)", size=12, color=INK, anchor="start"))

    # Unbiased loop (dashed grey)
    def get_unbiased_pts():
        pts_up = []
        pts_dn = []
        for i in range(-150, 151):
            h_val = i * 2.0
            m_up = math.tanh((h_val + 60) / 70.0) * 120
            m_dn = math.tanh((h_val - 60) / 70.0) * 120
            pts_up.append((ox + h_val, oy - m_up))
            pts_dn.append((ox + h_val, oy - m_dn))
        return pts_up, pts_dn

    pts_unb_up, pts_unb_dn = get_unbiased_pts()
    d_unb_up = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in pts_unb_up])
    d_unb_dn = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in reversed(pts_unb_dn)])
    f.append(path_svg(d_unb_up, stroke="#cbd5e1", sw=1.5, dash="4,4"))
    f.append(path_svg(d_unb_dn, stroke="#cbd5e1", sw=1.5, dash="4,4"))

    # Shifted loop (solid red/blue)
    shift_h = -110  # Left shift by H_eb
    def get_shifted_pts():
        pts_up = []
        pts_dn = []
        for i in range(-150, 151):
            h_val = i * 2.0
            h_eff = h_val - shift_h
            m_up = math.tanh((h_eff + 80) / 75.0) * 120
            m_dn = math.tanh((h_eff - 80) / 75.0) * 120
            pts_up.append((ox + h_val, oy - m_up))
            pts_dn.append((ox + h_val, oy - m_dn))
        return pts_up, pts_dn

    pts_sh_up, pts_sh_dn = get_shifted_pts()
    d_sh_up = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in pts_sh_up])
    d_sh_dn = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in reversed(pts_sh_dn)])
    f.append(path_svg(d_sh_up, stroke="#2563eb", sw=2.5))
    f.append(path_svg(d_sh_dn, stroke="#dc2626", sw=2.5))

    # Coercive points of shifted loop
    h_c1_x = ox + shift_h - 80
    h_c2_x = ox + shift_h + 80
    f.append(circle(h_c1_x, oy, 4, fill="#dc2626", stroke="none"))
    f.append(circle(h_c2_x, oy, 4, fill="#2563eb", stroke="none"))
    f.append(circle(ox, oy, 4, fill="#64748b", stroke="none"))

    # H_EB shift arrow
    eb_center_x = ox + shift_h
    f.append(line(eb_center_x, oy - 140, eb_center_x, oy + 140, color="#ef4444", sw=1.2, dash="3,3"))
    f.append(arrow(ox, oy - 110, eb_center_x, oy - 110, color="#dc2626", sw=2.0))
    f.append(arrow(eb_center_x, oy - 110, ox, oy - 110, color="#dc2626", sw=2.0))
    f.append(rect(eb_center_x + 15, oy - 128, 80, 24, fill="#fee2e2", stroke="#fca5a5", rx=4))
    f.append(text(eb_center_x + 55, oy - 112, "H_EB < 0", size=12, bold=True, color="#991b1b"))

    # Coercivity H_c annotations
    f.append(line(h_c1_x, oy + 20, h_c1_x, oy + 80, color="#64748b", sw=1.0, dash="2,2"))
    f.append(line(h_c2_x, oy + 20, h_c2_x, oy + 80, color="#64748b", sw=1.0, dash="2,2"))
    f.append(arrow(h_c1_x, oy + 70, h_c2_x, oy + 70, color="#1e293b", sw=1.5))
    f.append(arrow(h_c2_x, oy + 70, h_c1_x, oy + 70, color="#1e293b", sw=1.5))
    f.append(text(eb_center_x, oy + 88, "2·H_c", size=11, bold=True, color="#1e293b"))

    # Labels for H_c1 and H_c2
    f.append(text(h_c1_x - 10, oy + 18, "H_c1", size=11, bold=True, color="#dc2626", anchor="end"))
    f.append(text(h_c2_x + 10, oy + 18, "H_c2", size=11, bold=True, color="#2563eb", anchor="start"))

    # Legend box
    f.append(rect(80, 70, 210, 85, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(line(95, 90, 135, 90, color="#cbd5e1", sw=1.5, dash="4,4"))
    f.append(text(145, 94, "Ізольований FM (симетрична)", size=11, color="#475569", anchor="start"))
    f.append(line(95, 115, 135, 115, color="#2563eb", sw=2.5))
    f.append(text(145, 119, "FM/AFM структура (зсунута)", size=11, bold=True, color="#1e3a8a", anchor="start"))
    f.append(text(95, 142, "H_EB = (H_c1 + H_c2)/2", size=11, italic=True, color="#991b1b", anchor="start"))

    f.append(text(W / 2, H - 15, "Зсув петлі вздовж осі H визначається інтерфейсною обмінною взаємодією FM/AFM", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'hysteresis-shift-exchange-bias.svg'), W, H, "\n".join(f))


# ── Фігура 2: Мікроскопічний механізм закріплення спінів на інтерфейсі ───────
def fig_interface_coupling_mechanism():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Мікроскопічний механізм обмінного зміщення на інтерфейсі FM/AFM", size=16, bold=True, color=INK))

    panel_w = 350
    panel_h = 310
    y_top = 55

    # Panel A: Field H in direction of FC (Positive H)
    x1 = 30
    f.append(rect(x1, y_top, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x1 + panel_w / 2, y_top + 22, "а) Пряме поле H > 0 (напрямок H_FC)", size=13, bold=True, color="#1e293b"))

    # Layers in Panel A
    f.append(rect(x1 + 20, y_top + 45, panel_w - 40, 80, fill="#dbeafe", stroke="#93c5fd", rx=4))
    f.append(text(x1 + 35, y_top + 65, "Феромагнетик (FM)", size=11, bold=True, color="#1e40af", anchor="start"))
    for r in range(2):
        for c in range(5):
            sx = x1 + 80 + c * 50
            sy = y_top + 75 + r * 25
            f.append(arrow(sx - 12, sy, sx + 12, sy, color="#2563eb", sw=2.5))

    # Interface line
    f.append(line(x1 + 20, y_top + 130, x1 + panel_w - 20, y_top + 130, color="#ef4444", sw=2.0, dash="4,2"))
    f.append(text(x1 + panel_w - 25, y_top + 126, "Інтерфейс J_EB", size=10, bold=True, color="#dc2626", anchor="end"))

    # AFM Layer (bottom)
    f.append(rect(x1 + 20, y_top + 135, panel_w - 40, 110, fill="#f0fdf4", stroke="#86efac", rx=4))
    f.append(text(x1 + 35, y_top + 230, "Антиферомагнетик (AFM)", size=11, bold=True, color="#166534", anchor="start"))
    for c in range(5):
        sx = x1 + 80 + c * 50
        sy = y_top + 155
        f.append(circle(sx, sy, 5, fill="#dc2626", stroke="none"))
        f.append(arrow(sx - 10, sy, sx + 10, sy, color="#dc2626", sw=2.2))
    f.append(text(x1 + panel_w - 25, y_top + 158, "Закріплені спіни", size=10, color="#991b1b", anchor="end"))

    for r in range(2):
        for c in range(5):
            sx = x1 + 80 + c * 50
            sy = y_top + 180 + r * 22
            is_right = ((r + c) % 2 == 0)
            if is_right:
                f.append(arrow(sx - 10, sy, sx + 10, sy, color="#16a34a", sw=1.8))
            else:
                f.append(arrow(sx + 10, sy, sx - 10, sy, color="#15803d", sw=1.8))

    f.append(text(x1 + panel_w / 2, y_top + panel_h - 20, "Енергія мінімальна: FM і закріплені спіни паралельні", size=10, color="#475569"))

    # Panel B: Reversal Field H < 0
    x2 = 400
    f.append(rect(x2, y_top, panel_w, panel_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x2 + panel_w / 2, y_top + 22, "б) Обернене поле H < 0 (проти H_FC)", size=13, bold=True, color="#1e293b"))

    f.append(rect(x2 + 20, y_top + 45, panel_w - 40, 80, fill="#fee2e2", stroke="#fca5a5", rx=4))
    f.append(text(x2 + 35, y_top + 65, "Феромагнетик (FM)", size=11, bold=True, color="#991b1b", anchor="start"))
    for r in range(2):
        for c in range(5):
            sx = x2 + 80 + c * 50
            sy = y_top + 75 + r * 25
            f.append(arrow(sx + 12, sy, sx - 12, sy, color="#dc2626", sw=2.5))

    f.append(line(x2 + 20, y_top + 130, x2 + panel_w - 20, y_top + 130, color="#ef4444", sw=2.0, dash="4,2"))

    f.append(rect(x2 + 20, y_top + 135, panel_w - 40, 110, fill="#f0fdf4", stroke="#86efac", rx=4))
    f.append(text(x2 + 35, y_top + 230, "Антиферомагнетик (AFM)", size=11, bold=True, color="#166534", anchor="start"))
    for c in range(5):
        sx = x2 + 80 + c * 50
        sy = y_top + 155
        f.append(circle(sx, sy, 5, fill="#dc2626", stroke="none"))
        f.append(arrow(sx - 10, sy, sx + 10, sy, color="#dc2626", sw=2.2))

    for r in range(2):
        for c in range(5):
            sx = x2 + 80 + c * 50
            sy = y_top + 180 + r * 22
            is_right = ((r + c) % 2 == 0)
            if is_right:
                f.append(arrow(sx - 10, sy, sx + 10, sy, color="#16a34a", sw=1.8))
            else:
                f.append(arrow(sx + 10, sy, sx - 10, sy, color="#15803d", sw=1.8))

    f.append(text(x2 + panel_w / 2, y_top + panel_h - 20, "Опорний момент FM чинить опір: потрібне більше поле |H|", size=10, color="#991b1b"))

    f.append(text(W / 2, H - 15, "Закріплені спіни AFM виступають як внутрішнє ефективне поле, що повертає FM у вихідний стан", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'interface-coupling-mechanism.svg'), W, H, "\n".join(f))


# ── Фігура 3: Температурні режими та процес термомагнітного охолодження (FC) ─
def fig_field_cooling_temperature_regimes():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28, "Температурні режими термомагнітного оброблення (Field Cooling)", size=16, bold=True, color=INK))

    ax_y = 310
    f.append(line(70, ax_y, 700, ax_y, color="#64748b", sw=2.0))
    f.append(arrow(680, ax_y, 715, ax_y, color="#64748b", sw=2.0))
    f.append(text(715, ax_y + 25, "Температура T", size=12, bold=True, color=INK, anchor="end"))

    tb_x = 220
    tn_x = 440
    tc_x = 620

    f.append(line(tb_x, 70, tb_x, ax_y + 10, color="#ef4444", sw=1.5, dash="4,4"))
    f.append(circle(tb_x, ax_y, 6, fill="#ef4444", stroke="none"))
    f.append(text(tb_x, ax_y + 25, "T_B", size=13, bold=True, color="#dc2626"))
    f.append(text(tb_x, ax_y + 42, "Температура блокування", size=10, color="#7f1d1d"))

    f.append(line(tn_x, 70, tn_x, ax_y + 10, color="#16a34a", sw=1.5, dash="4,4"))
    f.append(circle(tn_x, ax_y, 6, fill="#16a34a", stroke="none"))
    f.append(text(tn_x, ax_y + 25, "T_N", size=13, bold=True, color="#15803d"))
    f.append(text(tn_x, ax_y + 42, "Температура Нееля (AFM)", size=10, color="#14532d"))

    f.append(line(tc_x, 70, tc_x, ax_y + 10, color="#2563eb", sw=1.5, dash="4,4"))
    f.append(circle(tc_x, ax_y, 6, fill="#2563eb", stroke="none"))
    f.append(text(tc_x, ax_y + 25, "T_C", size=13, bold=True, color="#1d4ed8"))
    f.append(text(tc_x, ax_y + 42, "Температура Кюрі (FM)", size=10, color="#1e3a8a"))

    f.append(rect(80, 80, tb_x - 80, 200, fill="#eff6ff", stroke="#bfdbfe", rx=6))
    f.append(text(80 + (tb_x - 80)/2, 105, "Обмінне зміщення", size=12, bold=True, color="#1e40af"))
    f.append(text(80 + (tb_x - 80)/2, 125, "активне (H_EB > 0)", size=11, bold=True, color="#1e3a8a"))
    f.append(text(80 + (tb_x - 80)/2, 160, "FM: феромагнітний\nAFM: спіни закріплені", size=10, color="#3b82f6"))

    f.append(rect(tb_x + 10, 80, tn_x - tb_x - 20, 200, fill="#fff7ed", stroke="#fed7aa", rx=6))
    f.append(text(tb_x + (tn_x - tb_x)/2, 105, "Розблокована фаза", size=12, bold=True, color="#c2410c"))
    f.append(text(tb_x + (tn_x - tb_x)/2, 125, "H_EB = 0, зростає H_c", size=11, bold=True, color="#9a3412"))
    f.append(text(tb_x + (tn_x - tb_x)/2, 160, "Тепловий рух долає\nанізотропію K_AFM", size=10, color="#ea580c"))

    f.append(rect(tn_x + 10, 80, tc_x - tn_x - 20, 200, fill="#fefce8", stroke="#fef08a", rx=6))
    f.append(text(tn_x + (tc_x - tn_x)/2, 105, "Нагрівання FC", size=12, bold=True, color="#a16207"))
    f.append(text(tn_x + (tc_x - tn_x)/2, 125, "AFM у парамагнітному стані", size=10, color="#854d0e"))
    f.append(text(tn_x + (tc_x - tn_x)/2, 160, "FM орієнтується уздовж H_FC", size=10, color="#ca8a04"))

    f.append(arrow(tn_x + 50, 245, tb_x - 30, 245, color="#dc2626", sw=3.0))
    f.append(text((tn_x + tb_x)/2, 235, "Охолодження в полі H_FC (Field Cooling)", size=11, bold=True, color="#991b1b"))

    f.append(text(W / 2, H - 15, "Для створення обмінного зміщення структуру нагрівають вище T_B та охолоджують у полі H_FC", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'field-cooling-temperature-regimes.svg'), W, H, "\n".join(f))


# ── Фігура 4: Спіновий клапан / MTJ та структура SAF ────────────────────────
def fig_spin_valve_mtj_stack():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Архітектура спінового клапана та MTJ з синтетичним антиферомагнетиком (SAF)", size=16, bold=True, color=INK))

    stack_w = 420
    x0 = 60
    y0 = 60
    layer_h = 36

    layers = [
        ("Вільний шар (Free Layer: CoFeB)", "#dbeafe", "#1e40af", "M рухомий (чутливий до полів)"),
        ("Бар'єр / Спейсер (MgO / Cu)", "#f1f5f9", "#475569", "Тунельний бар'єр або метал"),
        ("Закріплений шар FM2 (CoFeB)", "#fee2e2", "#991b1b", "Верхній шар SAF (M2)"),
        ("Рутенієвий місток (Ru spacer ~0.8 нм)", "#fae8ff", "#86198f", "Руклівець РККІ обміну (J_RKKY < 0)"),
        ("Опорний шар FM1 (CoFe)", "#fecaca", "#b91c1c", "Нижній шар SAF (M1)"),
        ("Антиферомагнетик (AFM: IrMn)", "#dcfce7", "#15803d", "Шаруватий шпінель/сплав (H_EB фіксація)"),
        ("Підкладка / Буферний шар (Ta / Ru)", "#e2e8f0", "#334155", "Кристалічна текстура (111)")
    ]

    for idx, (title_str, bg_col, txt_col, desc_str) in enumerate(layers):
        ly = y0 + idx * (layer_h + 4)
        f.append(rect(x0, ly, stack_w, layer_h, fill=bg_col, stroke=BORDER, rx=4))
        f.append(text(x0 + 15, ly + 22, title_str, size=11, bold=True, color=txt_col, anchor="start"))
        f.append(text(x0 + stack_w + 20, ly + 22, desc_str, size=10, color="#475569", anchor="start"))

        if "Free Layer" in title_str:
            f.append(arrow(x0 + stack_w - 60, ly + 18, x0 + stack_w - 20, ly + 18, color="#2563eb", sw=2.5))
            f.append(text(x0 + stack_w - 40, ly + 32, "⇄", size=14, bold=True, color="#2563eb"))
        elif "FM2" in title_str:
            f.append(arrow(x0 + stack_w - 60, ly + 18, x0 + stack_w - 20, ly + 18, color="#dc2626", sw=2.5))
        elif "FM1" in title_str:
            f.append(arrow(x0 + stack_w - 20, ly + 18, x0 + stack_w - 60, ly + 18, color="#b91c1c", sw=2.5))

    saf_top_y = y0 + 2 * (layer_h + 4)
    saf_bot_y = y0 + 5 * (layer_h + 4) + layer_h
    f.append(line(x0 - 15, saf_top_y, x0 - 15, saf_bot_y, color="#86198f", sw=2.0))
    f.append(line(x0 - 15, saf_top_y, x0 - 5, saf_top_y, color="#86198f", sw=2.0))
    f.append(line(x0 - 15, saf_bot_y, x0 - 5, saf_bot_y, color="#86198f", sw=2.0))
    f.append(text(x0 - 25, (saf_top_y + saf_bot_y) / 2, "SAF + Pinning", size=11, bold=True, color="#86198f", anchor="end"))

    f.append(text(W / 2, H - 15, "Синтетичний антиферомагнетик у поєднанні з IrMn забезпечує нульове дипольне поле розсіяння", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spin-valve-mtj-stack.svg'), W, H, "\n".join(f))


if __name__ == "__main__":
    fig_hysteresis_shift_exchange_bias()
    fig_interface_coupling_mechanism()
    fig_field_cooling_temperature_regimes()
    fig_spin_valve_mtj_stack()
    print("Figures created successfully!")
