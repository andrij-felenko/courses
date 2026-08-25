# -*- coding: utf-8 -*-
"""Фігури до теми «Спиновий обертальний момент (Spin-Transfer Torque, STT)».
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

def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Механізм передачі спінового моменту в спіновому вентилі ──────
def fig_stt_mechanism():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 28, "Передача спінового кутового моменту в тришаровій структурі", size=16, bold=True, color=INK))

    # Background zones for layers
    x_fixed_start = 70
    w_fixed = 180
    
    x_spacer_start = x_fixed_start + w_fixed
    w_spacer = 100

    x_free_start = x_spacer_start + w_spacer
    w_free = 180

    y_top = 65
    h_layer = 300

    # Draw layer backgrounds
    f.append(rect(x_fixed_start, y_top, w_fixed, h_layer, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=4))
    f.append(rect(x_spacer_start, y_top, w_spacer, h_layer, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=0))
    f.append(rect(x_free_start, y_top, w_free, h_layer, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=4))

    # Layer Headers
    f.append(text(x_fixed_start + w_fixed / 2, y_top + 24, "Фіксований шар", size=13, bold=True, color="#1d4ed8"))
    f.append(text(x_fixed_start + w_fixed / 2, y_top + 42, "(Pinned Layer, M_p)", size=11, color="#3b82f6"))

    f.append(text(x_spacer_start + w_spacer / 2, y_top + 24, "Прошарок", size=13, bold=True, color="#475569"))
    f.append(text(x_spacer_start + w_spacer / 2, y_top + 42, "(Cu / MgO)", size=11, color="#64748b"))

    f.append(text(x_free_start + w_free / 2, y_top + 24, "Вільний шар", size=13, bold=True, color="#b91c1c"))
    f.append(text(x_free_start + w_free / 2, y_top + 42, "(Free Layer, M)", size=11, color="#ef4444"))

    # Magnetization M_p in Fixed Layer (Upward)
    cx_fixed = x_fixed_start + w_fixed / 2
    cy_mid = y_top + h_layer / 2 + 10
    f.append(arrow(cx_fixed, cy_mid + 60, cx_fixed, cy_mid - 70, color="#1d4ed8", sw=3.5))
    f.append(text(cx_fixed + 25, cy_mid - 25, "M_p", size=14, bold=True, italic=True, color="#1d4ed8"))

    # Electron flux line (Left to Right)
    y_e = cy_mid - 10
    f.append(path_svg(f"M 15 {y_e} L {x_free_start + w_free + 50} {y_e}", stroke=MUTED, sw=1.5, dash="4,4"))
    f.append(text(35, y_e - 12, "Потік електронів (e-)", size=11, bold=True, color=MUTED))

    # Electron 1: Unpolarized before fixed layer
    f.append(circle(35, y_e, 10, fill="#ffffff", stroke="#64748b", sw=1.5))
    f.append(arrow(35, y_e + 7, 35, y_e - 7, color="#64748b", sw=1.5))
    f.append(arrow(35, y_e - 7, 35, y_e + 7, color="#64748b", sw=1.5))

    # Electron 2: Inside fixed layer - spin filtering
    f.append(circle(x_fixed_start + 90, y_e, 10, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    f.append(arrow(x_fixed_start + 90, y_e + 7, x_fixed_start + 90, y_e - 7, color="#1d4ed8", sw=2.0))

    # Electron 3: In spacer - spin polarized stream
    f.append(circle(x_spacer_start + 50, y_e, 10, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    f.append(arrow(x_spacer_start + 50, y_e + 7, x_spacer_start + 50, y_e - 7, color="#1d4ed8", sw=2.2))
    f.append(text(x_spacer_start + 50, y_e + 24, "s || M_p", size=11, bold=True, color="#1d4ed8"))

    # Free Layer Magnetization M (canted at angle theta)
    cx_free = x_free_start + 110
    angle_deg = 45
    rad = math.radians(angle_deg)
    dx_m = 65 * math.sin(rad)
    dy_m = 65 * math.cos(rad)

    # Free layer magnetization arrow
    f.append(arrow(cx_free - dx_m*0.6, cy_mid + dy_m*0.6, cx_free + dx_m, cy_mid - dy_m, color="#b91c1c", sw=3.5))
    f.append(text(cx_free + dx_m + 15, cy_mid - dy_m, "M", size=14, bold=True, italic=True, color="#b91c1c"))

    # Entering spin s in Free layer
    x_in_free = x_free_start + 35
    f.append(circle(x_in_free, y_e, 10, fill="#fee2e2", stroke="#dc2626", sw=1.5))
    f.append(arrow(x_in_free, y_e + 7, x_in_free, y_e - 7, color="#1d4ed8", sw=2.2))

    # Absorption zone (interface boundary)
    f.append(path_svg(f"M {x_free_start + 5} {y_top + 60} L {x_free_start + 5} {y_top + h_layer - 20}", stroke="#dc2626", sw=2, dash="3,3"))
    f.append(text(x_free_start + 55, y_top + h_layer - 40, "Поглинання s_perp", size=11, bold=True, color="#dc2626"))

    # STT Torque vector T_STT (perpendicular to M in plane)
    dx_t = 45 * math.cos(rad)
    dy_t = 45 * math.sin(rad)
    f.append(arrow(cx_free + dx_m*0.4, cy_mid - dy_m*0.4, cx_free + dx_m*0.4 + dx_t, cy_mid - dy_m*0.4 + dy_t, color="#16a34a", sw=3.0))
    f.append(text(cx_free + dx_m*0.4 + dx_t + 10, cy_mid - dy_m*0.4 + dy_t + 5, "T_STT", size=13, bold=True, italic=True, color="#16a34a"))

    # Angle arc between M_p (upward) and M (canted)
    f.append(path_svg(f"M {cx_free} {cy_mid - 40} A 40 40 0 0 1 {cx_free + 28} {cy_mid - 28}", stroke="#64748b", sw=1.5))
    f.append(text(cx_free + 14, cy_mid - 46, "θ", size=13, bold=True, italic=True, color="#475569"))

    # Bottom explanation
    f.append(text(W / 2, H - 20, "Спін-поляризований струм передає поперечну компоненту кутового моменту моменту намагніченості M", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'stt-mechanism-spin-filtering.svg'), W, H, "\n".join(f))

# ── Фігура 2: Векторна діаграма моментів у рівнянні ЛЛҐС ──────────────────────
def fig_llgs_vectors():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Вектори моментів у рівнянні Ландау — Ліфшиця — Ґільберта з термому Слончевського", size=15, bold=True, color=INK))

    cx, cy = 340, 230

    # Effective field H_eff (vertical)
    f.append(arrow(cx, cy, cx, cy - 140, color="#1e293b", sw=2.5))
    f.append(text(cx + 12, cy - 130, "H_eff", size=14, bold=True, italic=True, color="#1e293b"))

    # Precession cone (dashed ellipse)
    rx_cone, ry_cone = 130, 40
    y_cone = cy - 90
    f.append(ellipse_svg(cx, y_cone, rx_cone, ry_cone, fill="none", stroke="#cbd5e1", sw=1.5, dash="3,3"))

    # Magnetization vector m (pointing to cone)
    mx = cx + 110
    my = y_cone - 15
    f.append(arrow(cx, cy, mx, my, color="#b91c1c", sw=3.5))
    f.append(text(mx + 12, my - 5, "m", size=15, bold=True, italic=True, color="#b91c1c"))

    # Spin polarization vector p (vertical, reference direction)
    f.append(arrow(cx - 100, cy, cx - 100, cy - 120, color="#2563eb", sw=2.2))
    f.append(text(cx - 120, cy - 60, "p", size=14, bold=True, italic=True, color="#2563eb"))
    f.append(text(cx - 140, cy - 40, "(поляризація)", size=11, color="#3b82f6"))

    # Precession Torque T_prec = -gamma (m x H_eff) -> tangent to cone (out of page / left-up)
    tx_p = mx - 50
    ty_p = my - 25
    f.append(arrow(mx, my, tx_p, ty_p, color="#7c3aed", sw=2.5))
    f.append(text(tx_p - 15, ty_p - 10, "T_prec", size=12, bold=True, italic=True, color="#7c3aed"))

    # Damping Torque T_damp = alpha (m x dm/dt) -> towards H_eff (inwards to axis)
    tx_d = mx - 40
    ty_d = my + 35
    f.append(arrow(mx, my, tx_d, ty_d, color="#d97706", sw=2.5))
    f.append(text(tx_d - 45, ty_d + 10, "T_damp (загасання)", size=12, bold=True, italic=True, color="#d97706"))

    # Slonczewski Torque T_STT -> opposite to damping (outwards from axis, driving switching)
    tx_s = mx + 50
    ty_s = my - 40
    f.append(arrow(mx, my, tx_s, ty_s, color="#16a34a", sw=3.0))
    f.append(text(tx_s + 10, ty_s - 5, "T_STT (Слончевський)", size=13, bold=True, italic=True, color="#16a34a"))

    # Legend / Equation summary box
    bx = 550
    by = 70
    bw = 190
    bh = 280
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(bx + bw/2, by + 20, "Рівняння ЛЛҐС", size=13, bold=True, color=INK))

    f.append(text(bx + 15, by + 50, "dm/dt =", size=12, bold=True, anchor="start", color=INK))
    f.append(text(bx + 15, by + 75, "-γ₀ (m × H_eff)", size=11, bold=True, anchor="start", color="#7c3aed"))
    f.append(text(bx + 15, by + 95, "(прецесія)", size=10, italic=True, anchor="start", color=MUTED))

    f.append(text(bx + 15, by + 125, "+ α (m × dm/dt)", size=11, bold=True, anchor="start", color="#d97706"))
    f.append(text(bx + 15, by + 145, "(дисипація Ґільберта)", size=10, italic=True, anchor="start", color=MUTED))

    f.append(text(bx + 15, by + 175, "- γ₀ a_J [m × (m × p)]", size=11, bold=True, anchor="start", color="#16a34a"))
    f.append(text(bx + 15, by + 195, "(момент Слончевського)", size=10, italic=True, anchor="start", color=MUTED))

    f.append(text(bx + 15, by + 225, "- γ₀ b_J (m × p)", size=11, bold=True, anchor="start", color="#2563eb"))
    f.append(text(bx + 15, by + 245, "(польовий момент)", size=10, italic=True, anchor="start", color=MUTED))

    f.append(text(W / 2, H - 15, "При T_STT > T_damp виникає антизагасання, що веде до перемикання або автоколивань", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'llgs-torque-vectors.svg'), W, H, "\n".join(f))

# ── Фігура 3: Перемикання P <-> AP у комірці STT-MRAM ───────────────────────
def fig_stt_mram_switching():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Режими перемикання станів P і AP у комірці STT-MRAM", size=16, bold=True, color=INK))

    panel_w = 345
    panel_h = 320
    y_top = 55

    # --- PANEL 1: AP Switching ---
    x1 = 30
    f.append(rect(x1, y_top, panel_w, panel_h, fill="#fff7ed", stroke="#fed7aa", sw=1.5, rx=6))
    f.append(text(x1 + panel_w / 2, y_top + 22, "Запис стану AP (High R)", size=13, bold=True, color="#c2410c"))
    f.append(text(x1 + panel_w / 2, y_top + 40, "Струм: Вільний → Фіксований шар", size=11, color="#ea580c"))

    # Layers for Panel 1
    ly_w = 260
    ly_h = 40
    cx1 = x1 + panel_w / 2

    # Free layer top
    f.append(rect(cx1 - ly_w/2, y_top + 65, ly_w, ly_h, fill="#fef2f2", stroke="#fca5a5", rx=4))
    f.append(text(cx1 - 40, y_top + 89, "Вільний (Free)", size=11, bold=True, color="#b91c1c"))

    # Barrier mid
    f.append(rect(cx1 - ly_w/2, y_top + 115, ly_w, 25, fill="#f8fafc", stroke="#cbd5e1", rx=2))
    f.append(text(cx1 - 20, y_top + 131, "Тунельний бар'єр MgO", size=10, color="#64748b"))

    # Fixed layer bot
    f.append(rect(cx1 - ly_w/2, y_top + 150, ly_w, ly_h, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(cx1 - 40, y_top + 174, "Фіксований (Fixed)", size=11, bold=True, color="#1d4ed8"))

    # Fixed layer magnetization (UP)
    f.append(arrow(cx1 + 45, y_top + 182, cx1 + 45, y_top + 158, color="#1d4ed8", sw=3.0))

    # Free layer magnetization switched to DOWN (Anti-Parallel)
    f.append(arrow(cx1 + 45, y_top + 73, cx1 + 45, y_top + 97, color="#dc2626", sw=3.0))

    # Electron motion arrow
    f.append(arrow(cx1 - 118, y_top + 75, cx1 - 118, y_top + 180, color="#ea580c", sw=2.5))
    f.append(text(cx1 - 132, y_top + 130, "e-", size=12, bold=True, color="#ea580c", anchor="end"))

    # Reflected spin arrow (pointing DOWN into Free layer)
    f.append(path_svg(f"M {cx1 + 85} {y_top + 145} Q {cx1 + 100} {y_top + 130} {cx1 + 85} {y_top + 85}", stroke="#dc2626", sw=2.0, dash="3,3"))
    f.append(text(cx1 + 95, y_top + 115, "Відбиті спіни", size=9, bold=True, color="#dc2626", anchor="start"))

    f.append(text(cx1, y_top + 215, "Електрони зі спіном проти M_p", size=11, bold=True, color="#c2410c"))
    f.append(text(cx1, y_top + 232, "відбиваються від межі й повертаються", size=11, color="#c2410c"))
    f.append(text(cx1, y_top + 249, "у вільний шар, повертаючи M вниз", size=11, color="#c2410c"))

    f.append(textbox(cx1, y_top + 288, "Стан AP: R_AP (Високий)", size=12, bold=True, fill="#fff7ed", stroke="#c2410c", color="#c2410c")[0])

    # --- PANEL 2: P Switching ---
    x2 = 405
    f.append(rect(x2, y_top, panel_w, panel_h, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=6))
    f.append(text(x2 + panel_w / 2, y_top + 22, "Запис стану P (Low R)", size=13, bold=True, color="#15803d"))
    f.append(text(x2 + panel_w / 2, y_top + 40, "Струм: Фіксований → Вільний шар", size=11, color="#16a34a"))

    cx2 = x2 + panel_w / 2

    # Free layer top
    f.append(rect(cx2 - ly_w/2, y_top + 65, ly_w, ly_h, fill="#fef2f2", stroke="#fca5a5", rx=4))
    f.append(text(cx2 - 40, y_top + 89, "Вільний (Free)", size=11, bold=True, color="#b91c1c"))

    # Barrier mid
    f.append(rect(cx2 - ly_w/2, y_top + 115, ly_w, 25, fill="#f8fafc", stroke="#cbd5e1", rx=2))
    f.append(text(cx2 - 20, y_top + 131, "Тунельний бар'єр MgO", size=10, color="#64748b"))

    # Fixed layer bot
    f.append(rect(cx2 - ly_w/2, y_top + 150, ly_w, ly_h, fill="#eff6ff", stroke="#93c5fd", rx=4))
    f.append(text(cx2 - 40, y_top + 174, "Фіксований (Fixed)", size=11, bold=True, color="#1d4ed8"))

    # Fixed layer magnetization (UP)
    f.append(arrow(cx2 + 45, y_top + 182, cx2 + 45, y_top + 158, color="#1d4ed8", sw=3.0))

    # Free layer magnetization switched to UP (Parallel)
    f.append(arrow(cx2 + 45, y_top + 73, cx2 + 45, y_top + 97, color="#16a34a", sw=3.0))

    # Electron motion arrow (UPWARD: from Fixed to Free)
    f.append(arrow(cx2 - 118, y_top + 180, cx2 - 118, y_top + 75, color="#16a34a", sw=2.5))
    f.append(text(cx2 - 132, y_top + 130, "e-", size=12, bold=True, color="#16a34a", anchor="end"))

    # Transmitted spin arrow (pointing UP into Free layer)
    f.append(arrow(cx2 + 85, y_top + 160, cx2 + 85, y_top + 85, color="#1d4ed8", sw=2.2))
    f.append(text(cx2 + 95, y_top + 115, "Пропущені спіни", size=9, bold=True, color="#1d4ed8", anchor="start"))

    f.append(text(cx2, y_top + 215, "Електрони поляризуються уздовж M_p", size=11, bold=True, color="#15803d"))
    f.append(text(cx2, y_top + 232, "і передають спіновий момент у вільний", size=11, color="#15803d"))
    f.append(text(cx2, y_top + 249, "шар, орієнтуючи M паралельно M_p", size=11, color="#15803d"))

    f.append(textbox(cx2, y_top + 288, "Стан P: R_P (Низький)", size=12, bold=True, fill="#f0fdf4", stroke="#15803d", color="#15803d")[0])

    f.append(text(W / 2, H - 15, "Полярність електричного струму визначає напрямок перемикання між станами R_P та R_AP", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'stt-mram-p-ap-switching.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_stt_mechanism()
    fig_llgs_vectors()
    fig_stt_mram_switching()
    print("Згенеровано фігури в", IMG_DIR)
