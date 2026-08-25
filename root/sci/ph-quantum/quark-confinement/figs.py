# -*- coding: utf-8 -*-
"""Фігури до теми «Конфайнмент кварків».
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


# ── Фігура 1: Ефективний потенціал Корнелла ───────────────────────────────────
def fig_cornell_potential():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 28, "Ефективний потенціал Корнелла V(r) у КХД", size=16, bold=True, color=INK))

    # Plot axes area
    x0, y0 = 90, 360
    pw, ph = 640, 290
    x_max = x0 + pw
    y_min = y0 - ph

    # Grid background
    f.append(rect(x0, y_min, pw, ph, fill="#f8fafc", stroke=BORDER, rx=4))

    # Grid lines
    for i in range(1, 6):
        gx = x0 + i * (pw / 6)
        f.append(path_svg(f"M {gx:.1f} {y0} L {gx:.1f} {y_min}", stroke="#e2e8f0", sw=1.0, dash="4,4"))
    for j in range(1, 5):
        gy = y0 - j * (ph / 5)
        f.append(path_svg(f"M {x0} {gy:.1f} L {x_max} {gy:.1f}", stroke="#e2e8f0", sw=1.0, dash="4,4"))

    # Axes
    f.append(arrow(x0, y0, x_max + 15, y0, color=INK, sw=2.0))
    f.append(arrow(x0, y0, x0, y_min - 15, color=INK, sw=2.0))
    f.append(text(x_max + 20, y0 + 5, "r (fm)", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(x0 - 15, y_min - 15, "V(r)", size=13, bold=True, color=INK, anchor="middle"))

    # Curves physics parameters
    # r from 0.08 to 2.2 fm
    # V(r) = -A/r + K*r
    A = 0.4    # Coulomb coefficient
    K = 1.0    # String tension coefficient
    
    # Scale functions
    def r_to_x(r_val):
        return x0 + (r_val / 2.2) * pw

    def v_to_y(v_val):
        # Map V from -1.5 to 2.5
        v_min, v_max = -1.5, 2.5
        norm = (v_val - v_min) / (v_max - v_min)
        return y0 - norm * ph

    # 1. Coulomb term (-A/r)
    pts_coulomb = []
    for step in range(1, 200):
        r_v = 0.12 + step * (2.1 / 200)
        v_v = -A / r_v
        if -1.5 <= v_v <= 2.5:
            pts_coulomb.append((r_to_x(r_v), v_to_y(v_v)))
    
    path_c = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_coulomb)
    f.append(path_svg(path_c, stroke=NEG, sw=2.0, dash="6,4"))

    # 2. Linear string term (K*r)
    pts_linear = []
    for step in range(0, 200):
        r_v = step * (2.2 / 200)
        v_v = K * r_v - 0.5
        if -1.5 <= v_v <= 2.5:
            pts_linear.append((r_to_x(r_v), v_to_y(v_v)))

    path_l = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_linear)
    f.append(path_svg(path_l, stroke=POS, sw=2.0, dash="6,4"))

    # 3. Total Cornell Potential
    pts_total = []
    for step in range(1, 200):
        r_v = 0.10 + step * (2.1 / 200)
        v_v = -A / r_v + K * r_v
        if -1.5 <= v_v <= 2.5:
            pts_total.append((r_to_x(r_v), v_to_y(v_v)))

    path_t = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_total)
    f.append(path_svg(path_t, stroke="#0f172a", sw=3.2))

    # Horizontal Threshold: String Breaking (2 m_q)
    r_break = 1.2
    v_break = -A / r_break + K * r_break
    y_break = v_to_y(v_break)
    f.append(path_svg(f"M {x0} {y_break:.1f} L {x_max} {y_break:.1f}", stroke="#d97706", sw=2.0, dash="8,4"))
    f.append(text(x_max - 10, y_break - 8, "Поріг народження пари 2m_q c² (розрив струни)", size=11, bold=True, color="#d97706", anchor="end"))

    # Break point marker
    x_b = r_to_x(r_break)
    f.append(circle(x_b, y_break, 6, fill="#d97706", stroke="#ffffff"))

    # Annotations on graph
    f.append(text(x0 + 80, y0 - 45, "Кулоноподібна зона V(r) ∝ -1/r", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(x0 + 440, y0 - 240, "Лінійна зона струни V(r) = K·r", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(x0 + 260, y0 - 130, "Потенціал Корнелла V(r) = -4α_s/(3r) + K·r", size=12, bold=True, color="#0f172a", anchor="start"))

    # X-axis ticks & labels
    for r_val, label_str in [(0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0")]:
        tx = r_to_x(r_val)
        f.append(path_svg(f"M {tx:.1f} {y0} L {tx:.1f} {y0+6}", stroke=INK, sw=1.5))
        f.append(text(tx, y0 + 22, label_str, size=11, color=INK))

    # Legend box
    leg_x, leg_y = x0 + 20, y_min + 20
    f.append(rect(leg_x, leg_y, 240, 75, fill="#ffffff", stroke=BORDER, rx=4))
    f.append(path_svg(f"M {leg_x+10} {leg_y+18} L {leg_x+40} {leg_y+18}", stroke="#0f172a", sw=3.0))
    f.append(text(leg_x + 48, leg_y + 22, "Повний потенціал Корнелла", size=11, bold=True, color=INK, anchor="start"))
    f.append(path_svg(f"M {leg_x+10} {leg_y+38} L {leg_x+40} {leg_y+38}", stroke=NEG, sw=2.0, dash="6,4"))
    f.append(text(leg_x + 48, leg_y + 42, "Одноглюонний обмін (-4α_s/3r)", size=11, color=INK, anchor="start"))
    f.append(path_svg(f"M {leg_x+10} {leg_y+58} L {leg_x+40} {leg_y+58}", stroke=POS, sw=2.0, dash="6,4"))
    f.append(text(leg_x + 48, leg_y + 62, "Натяг глюонної струни (K·r)", size=11, color=INK, anchor="start"))

    f.append(text(W / 2, H - 12, "При зростанні відстані r енергія глюонної струни зростає лінійно до досягнення порогу порододження частинок", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'cornell-potential.svg'), W, H, "\n".join(f))


# ── Фігура 2: Поле у КЕД та КХД (глюонна струна) ──────────────────────────────
def fig_gluon_flux_tube():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 28, "Порівняння конфігурації силових ліній у КЕД та КХД", size=16, bold=True, color=INK))

    panel_w = 360
    panel_h = 280
    y_top = 55

    # Panel A: QED (Electrodynamics)
    x_a = 25
    f.append(rect(x_a, y_top, panel_w, panel_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x_a + panel_w / 2, y_top + 24, "Квантова електродинаміка (КЕД)", size=14, bold=True, color="#1e40af"))
    f.append(text(x_a + panel_w / 2, y_top + 42, "Безмасові неточковою взаємодією фотони (Абелева U(1))", size=11, color=MUTED))

    # QED Charges
    q1_x, q1_y = x_a + 90, y_top + 140
    q2_x, q2_y = x_a + 270, y_top + 140

    # Curved field lines QED
    for curve_h in [-80, -55, -28, 0, 28, 55, 80]:
        if curve_h == 0:
            f.append(path_svg(f"M {q1_x} {q1_y} L {q2_x} {q2_y}", stroke="#3b82f6", sw=1.8))
        else:
            cp_y = q1_y + curve_h * 1.4
            path_str = f"M {q1_x} {q1_y} Q {x_a + panel_w/2:.1f} {cp_y:.1f} {q2_x} {q2_y}"
            f.append(path_svg(path_str, stroke="#3b82f6", sw=1.8))

    # QED Charge circles
    f.append(circle(q1_x, q1_y, 16, fill=POS, stroke="#ffffff", sw=2))
    f.append(text(q1_x, q1_y + 5, "+q", size=13, bold=True, color="#ffffff"))
    f.append(circle(q2_x, q2_y, 16, fill=NEG, stroke="#ffffff", sw=2))
    f.append(text(q2_x, q2_y + 5, "-q", size=13, bold=True, color="#ffffff"))

    f.append(text(x_a + panel_w / 2, y_top + panel_h - 35, "Силові лінії радіально розходяться у просторі", size=11, bold=True, color=INK))
    f.append(text(x_a + panel_w / 2, y_top + panel_h - 18, "Потенціал: V(r) ∝ 1/r (закон Кулона)", size=11, bold=True, color=INK))

    # Panel B: QCD (Chromodynamics - Flux Tube)
    x_b = 395
    f.append(rect(x_b, y_top, panel_w, panel_h, fill="#f0fdf4", stroke=BORDER, rx=6))
    f.append(text(x_b + panel_w / 2, y_top + 24, "Квантова хромодинаміка (КХД)", size=14, bold=True, color="#15803d"))
    f.append(text(x_b + panel_w / 2, y_top + 42, "Самовзаємодія глюонів (Неабелева SU(3))", size=11, color=MUTED))

    # QCD Quarks
    k1_x, k1_y = x_b + 90, y_top + 140
    k2_x, k2_y = x_b + 270, y_top + 140

    # Flux tube background shading (cylinder)
    tube_top = k1_y - 28
    tube_bot = k1_y + 28
    f.append(rect(k1_x, tube_top, k2_x - k1_x, tube_bot - tube_top, fill="#dcfce7", stroke="#86efac", rx=12))

    # Tight flux lines QCD
    for curve_h in [-20, -10, 0, 10, 20]:
        if curve_h == 0:
            f.append(path_svg(f"M {k1_x} {k1_y} L {k2_x} {k2_y}", stroke="#16a34a", sw=2.2))
        else:
            cp_y = k1_y + curve_h * 0.8
            path_str = f"M {k1_x} {k1_y} Q {x_b + panel_w/2:.1f} {cp_y:.1f} {k2_x} {k2_y}"
            f.append(path_svg(path_str, stroke="#16a34a", sw=2.0))

    # Self-interaction gluon vertices (small nodes in flux tube)
    for g_x in [x_b + 145, x_b + 180, x_b + 215]:
        f.append(circle(g_x, k1_y - 8, 4, fill="#ea580c", stroke="none"))
        f.append(circle(g_x + 10, k1_y + 8, 4, fill="#ea580c", stroke="none"))

    # QCD Quarks circles
    f.append(circle(k1_x, k1_y, 16, fill="#dc2626", stroke="#ffffff", sw=2))
    f.append(text(k1_x, k1_y + 5, "q (r)", size=12, bold=True, color="#ffffff"))
    f.append(circle(k2_x, k2_y, 16, fill="#2563eb", stroke="#ffffff", sw=2))
    f.append(text(k2_x, k2_y + 5, "q̄ (r̄)", size=12, bold=True, color="#ffffff"))

    # Tube dimension annotation
    f.append(path_svg(f"M {x_b + panel_w/2:.1f} {tube_top} L {x_b + panel_w/2:.1f} {tube_bot}", stroke="#15803d", sw=1.2, dash="3,3"))
    f.append(text(x_b + panel_w / 2 + 8, k1_y - 32, "d ≈ 1 fm", size=10, bold=True, color="#15803d", anchor="start"))

    f.append(text(x_b + panel_w / 2, y_top + panel_h - 35, "Силові лінії стискаються у тонку трубку струни", size=11, bold=True, color=INK))
    f.append(text(x_b + panel_w / 2, y_top + panel_h - 18, "Потенціал: V(r) = K·r (K ≈ 1 GeV/fm)", size=11, bold=True, color=INK))

    f.append(text(W / 2, H - 12, "Самовзаємодія глюонів завадить поширенню силових ліній у просторі, формуючи трубку силового поля", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'gluon-flux-tube.svg'), W, H, "\n".join(f))


# ── Фігура 3: Механізм розриву струни та утворення струменів ──────────────────
def fig_string_breaking_jets():
    W, H = 780, 460
    f = []

    f.append(text(W / 2, 26, "Динаміка розриву глюонної струни та формоутворення струменів", size=16, bold=True, color=INK))

    steps = [
        ("1. Розтягнення кварк-антикваркової пари", "Натяг струни накопичує енергію E = K·r", 60),
        ("2. Квантовий розрив струни з вакууму", "Народження нової пари q'q̄' за механізмом Швінгера", 155),
        ("3. Утворення двох кольорово-синглетних мезонів", "Струна розділяється на два окремі адрони", 250),
        ("4. Формування адронних струменів (Jets)", "Колінеарний розліт створених частинок у детекторі", 345)
    ]

    box_w = 720
    box_h = 75
    x0 = 30

    # Step 1
    y1 = 55
    f.append(rect(x0, y1, box_w, box_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x0 + 15, y1 + 22, steps[0][0], size=12, bold=True, color="#c2410c", anchor="start"))
    f.append(text(x0 + 15, y1 + 38, steps[0][1], size=10, color=MUTED, anchor="start"))
    
    q1_x, q2_x = x0 + 360, x0 + 560
    cy1 = y1 + 45
    f.append(rect(q1_x, cy1 - 10, q2_x - q1_x, 20, fill="#ffedd5", stroke="#fdba74", rx=6))
    f.append(path_svg(f"M {q1_x} {cy1} L {q2_x} {cy1}", stroke="#ea580c", sw=2.5))
    f.append(circle(q1_x, cy1, 11, fill="#dc2626", stroke="#ffffff"))
    f.append(text(q1_x, cy1 + 4, "q", size=10, bold=True, color="#ffffff"))
    f.append(circle(q2_x, cy1, 11, fill="#2563eb", stroke="#ffffff"))
    f.append(text(q2_x, cy1 + 4, "q̄", size=10, bold=True, color="#ffffff"))
    f.append(arrow(q1_x - 15, cy1, q1_x - 35, cy1, color="#c2410c", sw=2.0))
    f.append(arrow(q2_x + 15, cy1, q2_x + 35, cy1, color="#c2410c", sw=2.0))

    # Step 2
    y2 = 145
    f.append(rect(x0, y2, box_w, box_h, fill="#fef2f2", stroke=BORDER, rx=6))
    f.append(text(x0 + 15, y2 + 22, steps[1][0], size=12, bold=True, color="#b91c1c", anchor="start"))
    f.append(text(x0 + 15, y2 + 38, steps[1][1], size=10, color=MUTED, anchor="start"))

    q1_x, q2_x = x0 + 320, x0 + 600
    mid_x = (q1_x + q2_x) / 2
    cy2 = y2 + 45
    f.append(path_svg(f"M {q1_x} {cy2} L {mid_x-20} {cy2}", stroke="#ef4444", sw=2.5))
    f.append(path_svg(f"M {mid_x+20} {cy2} L {q2_x} {cy2}", stroke="#ef4444", sw=2.5))
    f.append(circle(q1_x, cy2, 11, fill="#dc2626", stroke="#ffffff"))
    f.append(text(q1_x, cy2 + 4, "q", size=10, bold=True, color="#ffffff"))
    f.append(circle(q2_x, cy2, 11, fill="#2563eb", stroke="#ffffff"))
    f.append(text(q2_x, cy2 + 4, "q̄", size=10, bold=True, color="#ffffff"))
    
    # New pair created in vacuum
    f.append(circle(mid_x - 12, cy2, 10, fill="#2563eb", stroke="#d97706", sw=2))
    f.append(text(mid_x - 12, cy2 + 4, "q̄'", size=9, bold=True, color="#ffffff"))
    f.append(circle(mid_x + 12, cy2, 10, fill="#dc2626", stroke="#d97706", sw=2))
    f.append(text(mid_x + 12, cy2 + 4, "q'", size=9, bold=True, color="#ffffff"))
    f.append(text(mid_x, cy2 - 20, "Вакуумне народження q'q̄'", size=10, bold=True, color="#d97706"))

    # Step 3
    y3 = 235
    f.append(rect(x0, y3, box_w, box_h, fill="#f0fdf4", stroke=BORDER, rx=6))
    f.append(text(x0 + 15, y3 + 22, steps[2][0], size=12, bold=True, color="#15803d", anchor="start"))
    f.append(text(x0 + 15, y3 + 38, steps[2][1], size=10, color=MUTED, anchor="start"))

    m1_x, m2_x = x0 + 380, x0 + 540
    cy3 = y3 + 45
    # Meson 1
    f.append(rect(m1_x - 30, cy3 - 16, 60, 32, fill="#dcfce7", stroke="#16a34a", rx=16))
    f.append(circle(m1_x - 14, cy3, 10, fill="#dc2626", stroke="#ffffff"))
    f.append(text(m1_x - 14, cy3 + 4, "q", size=9, bold=True, color="#ffffff"))
    f.append(circle(m1_x + 14, cy3, 10, fill="#2563eb", stroke="#ffffff"))
    f.append(text(m1_x + 14, cy3 + 4, "q̄'", size=9, bold=True, color="#ffffff"))
    f.append(text(m1_x, cy3 - 22, "Мезон 1", size=10, bold=True, color="#15803d"))

    # Meson 2
    f.append(rect(m2_x - 30, cy3 - 16, 60, 32, fill="#dcfce7", stroke="#16a34a", rx=16))
    f.append(circle(m2_x - 14, cy3, 10, fill="#dc2626", stroke="#ffffff"))
    f.append(text(m2_x - 14, cy3 + 4, "q'", size=9, bold=True, color="#ffffff"))
    f.append(circle(m2_x + 14, cy3, 10, fill="#2563eb", stroke="#ffffff"))
    f.append(text(m2_x + 14, cy3 + 4, "q̄", size=9, bold=True, color="#ffffff"))
    f.append(text(m2_x, cy3 - 22, "Мезон 2", size=10, bold=True, color="#15803d"))

    # Step 4
    y4 = 325
    f.append(rect(x0, y4, box_w, box_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x0 + 15, y4 + 22, steps[3][0], size=12, bold=True, color="#1d4ed8", anchor="start"))
    f.append(text(x0 + 15, y4 + 38, steps[3][1], size=10, color=MUTED, anchor="start"))

    jet_center_x = x0 + 460
    cy4 = y4 + 42

    # Left Jet Cone
    f.append(path_svg(f"M {jet_center_x} {cy4} L {jet_center_x - 130} {cy4 - 24} L {jet_center_x - 130} {cy4 + 24} Z", fill="#dbeafe", stroke="#3b82f6", sw=1.2))
    # Right Jet Cone
    f.append(path_svg(f"M {jet_center_x} {cy4} L {jet_center_x + 130} {cy4 - 24} L {jet_center_x + 130} {cy4 + 24} Z", fill="#dbeafe", stroke="#3b82f6", sw=1.2))

    # Hadron particles inside cones
    for p_x, p_y in [(-60, -8), (-90, 10), (-110, -14), (-75, 12)]:
        f.append(circle(jet_center_x + p_x, cy4 + p_y, 5, fill="#1d4ed8", stroke="none"))
    for p_x, p_y in [(60, 8), (90, -10), (110, 14), (75, -12)]:
        f.append(circle(jet_center_x + p_x, cy4 + p_y, 5, fill="#1d4ed8", stroke="none"))

    f.append(text(jet_center_x - 80, cy4 - 30, "Струмінь 1 (Jet 1)", size=11, bold=True, color="#1d4ed8"))
    f.append(text(jet_center_x + 80, cy4 - 30, "Струмінь 2 (Jet 2)", size=11, bold=True, color="#1d4ed8"))

    f.append(text(W / 2, H - 12, "Колосальна енергія утворення струни перетворюється на каскад вторинних безкольорових адронів", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'string-breaking-jets.svg'), W, H, "\n".join(f))


if __name__ == "__main__":
    fig_cornell_potential()
    fig_gluon_flux_tube()
    fig_string_breaking_jets()
    print("Згенеровано фігури у", IMG_DIR)
