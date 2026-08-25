# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_four_fundamental_variables():
    w, h = 780, 540
    frags = []
    
    cx, cy = 390, 270
    rx, ry = 250, 170
    
    v_pos = (cx, cy - ry)
    q_pos = (cx + rx, cy)
    i_pos = (cx, cy + ry)
    phi_pos = (cx - rx, cy)
    
    # Outer lines
    frags.append(line(phi_pos[0], phi_pos[1], v_pos[0], v_pos[1], color=MUTED, sw=2, dash="4,4"))
    frags.append(line(v_pos[0], v_pos[1], q_pos[0], q_pos[1], color=MUTED, sw=2))
    frags.append(line(q_pos[0], q_pos[1], i_pos[0], i_pos[1], color=MUTED, sw=2, dash="4,4"))
    frags.append(line(i_pos[0], i_pos[1], phi_pos[0], phi_pos[1], color=MUTED, sw=2))
    
    # Vertex Boxes
    v_box = fitbox(v_pos[0] - 75, v_pos[1] - 25, 150, 50, "Напруга v(t)\n(Вольт)", size=14, bold=True, fill="#ffffff", stroke=LINE, sw=2)
    q_box = fitbox(q_pos[0] - 75, q_pos[1] - 25, 150, 50, "Заряд q(t)\n(Кулон)", size=14, bold=True, fill="#ffffff", stroke=LINE, sw=2)
    i_box = fitbox(i_pos[0] - 75, i_pos[1] - 25, 150, 50, "Струм i(t)\n(Ампер)", size=14, bold=True, fill="#ffffff", stroke=LINE, sw=2)
    phi_box = fitbox(phi_pos[0] - 75, phi_pos[1] - 25, 150, 50, "Потік φ(t)\n(Вебер)", size=14, bold=True, fill="#ffffff", stroke=LINE, sw=2)
    
    # Internal connections broken around boxes to prevent line-text overlaps
    # Resistor Box (Vertical): top at cy - 65, bottom at cy - 25
    res_box = fitbox(cx - 75, cy - 65, 150, 42, "Резистор (R)\ndv = R·di", size=12, fill="#f4f6f8", stroke=LINE)
    frags.append(line(v_pos[0], v_pos[1] + 25, cx, cy - 65, color=LINE, sw=2))
    frags.append(line(cx, cy - 23, i_pos[0], cy + 25, color=LINE, sw=2))
    
    # Memristor Box (Horizontal): left at cx - 85, right at cx + 85
    mem_box = fitbox(cx - 85, cy + 25, 170, 48, "МЕМРИСТОР (M)\ndφ = M(q)·dq", size=13, fill="#fdecea", stroke=POS, bold=True, sw=2)
    frags.append(line(phi_pos[0] + 75, cy, cx - 85, cy, color=POS, sw=3.5))
    frags.append(line(cx + 85, cy, q_pos[0] - 75, cy, color=POS, sw=3.5))
    
    # Labels on edges (with textbox/fitbox)
    frags.append(fitbox(phi_pos[0] + 30, cy - ry/2 - 35, 150, 42, "Інтегрування dφ = v·dt", size=12, fill="#f8f9fa", stroke=MUTED))
    frags.append(fitbox(cx + rx/2 - 20, cy - ry/2 - 35, 140, 42, "Конденсатор (C)\ndq = C·dv", size=12, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(cx + rx/2 - 20, cy + ry/2 - 5, 150, 42, "Інтегрування dq = i·dt", size=12, fill="#f8f9fa", stroke=MUTED))
    frags.append(fitbox(cx - rx/2 - 130, cy + ry/2 - 5, 140, 42, "Індуктивність (L)\ndφ = L·di", size=12, fill="#eaf0fd", stroke=NEG))
    
    frags.extend([v_box, q_box, i_box, phi_box, res_box, mem_box])
    
    render(os.path.join(IMG_DIR, 'four-fundamental-variables.svg'), w, h, *frags,
           title="Чотири фундаментальні змінні кола та зв'язуючі двополюсники")

def fig_hp_memristor_structure():
    w, h = 760, 460
    frags = []
    
    dev_x, dev_y, dev_w, dev_h = 100, 110, 560, 210
    
    # Top electrode
    frags.append(rect(dev_x, dev_y, dev_w, 35, fill="#d0d7de", stroke=LINE, sw=2))
    frags.append(mtext(dev_x + dev_w/2, dev_y + 22, "Верхній платиновий електрод (Pt / +)", size=13, bold=True))
    
    # Bottom electrode
    frags.append(rect(dev_x, dev_y + dev_h - 35, dev_w, 35, fill="#d0d7de", stroke=LINE, sw=2))
    frags.append(mtext(dev_x + dev_w/2, dev_y + dev_h - 12, "Нижній платиновий електрод (Pt / −)", size=13, bold=True))
    
    film_y = dev_y + 35
    film_h = 140
    
    w_ratio = 0.42
    w_px = dev_w * w_ratio
    
    # Doped region TiO_{2-x}
    frags.append(rect(dev_x, film_y, w_px, film_h, fill="#fdecea", stroke=POS, sw=2))
    frags.append(mtext(dev_x + w_px/2, film_y + 25, "Збагачений шар TiO₂₋ₓ", size=13, color=POS, bold=True))
    frags.append(mtext(dev_x + w_px/2, film_y + 44, "(Вакансії оксигену V_O⁺⁺)", size=11, color=POS))
    frags.append(mtext(dev_x + w_px/2, film_y + 120, "Низький опір R_ON", size=12, color=POS, bold=True))
    
    # Oxygen vacancies (red pluses in single middle row)
    for px in [dev_x + 35, dev_x + 85, dev_x + 135, dev_x + 185]:
        frags.append(plus(px, film_y + 75, r=8))
        
    # Undoped region TiO2
    frags.append(rect(dev_x + w_px, film_y, dev_w - w_px, film_h, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(mtext(dev_x + w_px + (dev_w - w_px)/2, film_y + 35, "Чистий стехіометричний TiO₂", size=13, color=NEG, bold=True))
    frags.append(mtext(dev_x + w_px + (dev_w - w_px)/2, film_y + 56, "(Чистий діелектрик)", size=11, color=NEG))
    frags.append(mtext(dev_x + w_px + (dev_w - w_px)/2, film_y + 120, "Високий опір R_OFF", size=12, color=NEG, bold=True))
    
    # Interface boundary line (movable w)
    frags.append(line(dev_x + w_px, film_y, dev_x + w_px, film_y + film_h, color=POS, sw=2.5, dash="5,3"))
    frags.append(fitbox(dev_x + w_px - 45, film_y - 25, 90, 22, "Межа w(t)", size=11, fill="#ffffff", stroke=POS, bold=True))
    
    # Dimensions indicators
    # Width w(t)
    frags.append(arrow(dev_x, film_y + film_h + 15, dev_x + w_px, film_y + film_h + 15, color=POS))
    frags.append(text(dev_x + w_px/2, film_y + film_h + 30, "w(t)", size=12, color=POS, bold=True))
    
    # Total D ~ 10 nm
    frags.append(arrow(dev_x, film_y + film_h + 45, dev_x + dev_w, film_y + film_h + 45, color=LINE))
    frags.append(text(dev_x + dev_w/2, film_y + film_h + 62, "Повна товщина плівки D ≈ 10 нм", size=12, bold=True))
    
    # Equation at bottom
    frags.append(fitbox(w/2 - 200, h - 40, 400, 34, "R(w) = R_ON · (w/D) + R_OFF · (1 − w/D)", size=12, fill="#ffffff", stroke=LINE, bold=True))
    
    render(os.path.join(IMG_DIR, 'hp-memristor-structure.svg'), w, h, *frags,
           title="Двошарова фізична структура наномемристора TiO₂ (HP Labs)")

def fig_pinched_hysteresis_loop():
    w, h = 760, 480
    frags = []
    
    cx, cy = 380, 250
    ax_w, ax_h = 280, 180
    
    # Grid / Axes
    frags.append(arrow(cx - ax_w - 20, cy, cx + ax_w + 30, cy, color=LINE, sw=1.5))
    frags.append(text(cx + ax_w + 45, cy + 5, "v(t)", size=14, bold=True))
    
    frags.append(arrow(cx, cy + ax_h + 20, cx, cy - ax_h - 30, color=LINE, sw=1.5))
    frags.append(text(cx, cy - ax_h - 42, "i(t)", size=14, bold=True))
    
    frags.append(circle(cx, cy, 3, fill=INK, stroke=INK))
    frags.append(text(cx - 15, cy + 18, "(0,0)", size=11, color=MUTED))
    
    pts_low = []
    pts_med = []
    pts_high = []
    
    steps = 100
    for s in range(steps + 1):
        t = 2.0 * math.pi * s / steps
        v_val = ax_w * 0.85 * math.sin(t)
        
        m_low = 1.0 + 0.5 * math.cos(t)
        i_low = (v_val / m_low) * 0.7
        pts_low.append((cx + v_val, cy - i_low))
        
        m_med = 1.0 + 0.25 * math.cos(t)
        i_med = (v_val / m_med) * 0.7
        pts_med.append((cx + v_val, cy - i_med))
        
        i_high = v_val * 0.65
        pts_high.append((cx + v_val, cy - i_high))
        
    def polyline_path(pts, color, sw, dash=None):
        d_str = " ".join(["%s%.1f,%.1f" % ("M" if i==0 else "L", p[0], p[1]) for i, p in enumerate(pts)])
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d_str, color, sw, dash_attr)
        
    frags.append(polyline_path(pts_low, POS, 2.5))
    frags.append(polyline_path(pts_med, FIELD, 2.0, dash="6,3"))
    frags.append(polyline_path(pts_high, NEG, 2.0, dash="2,2"))
    
    leg_x, leg_y = 70, 70
    frags.append(rect(leg_x, leg_y, 250, 105, fill="#ffffff", stroke=LINE, rx=6))
    
    frags.append(line(leg_x + 15, leg_y + 25, leg_x + 55, leg_y + 25, color=POS, sw=2.5))
    frags.append(text(leg_x + 65, leg_y + 29, "Низька частота ω₁ (широка петля)", size=12, anchor="start", bold=True))
    
    frags.append(line(leg_x + 15, leg_y + 55, leg_x + 55, leg_y + 55, color=FIELD, sw=2.0, dash="6,3"))
    frags.append(text(leg_x + 65, leg_y + 59, "Середня частота ω₂ > ω₁", size=12, anchor="start"))
    
    frags.append(line(leg_x + 15, leg_y + 85, leg_x + 55, leg_y + 85, color=NEG, sw=2.0, dash="2,2"))
    frags.append(text(leg_x + 65, leg_y + 89, "Висока частота ω → ∞ (лінійний опір)", size=12, anchor="start"))
    
    frags.append(fitbox(cx + 110, cy + 130, 220, 42, "Стискання в точці (0,0)\nPasses through origin", size=12, fill="#fdecea", stroke=POS))
    frags.append(arrow(cx + 110, cy + 108, cx + 15, cy + 10, color=POS))
    
    render(os.path.join(IMG_DIR, 'pinched-hysteresis-loop.svg'), w, h, *frags,
           title="Стиснута петля гістерезису вольт-амперної характеристики (ВАХ)")

def fig_window_functions_drift():
    w, h = 760, 460
    frags = []
    
    ox, oy = 100, 370
    gw, gh = 560, 270
    
    frags.append(arrow(ox - 10, oy, ox + gw + 30, oy, color=LINE, sw=1.5))
    frags.append(text(ox + gw + 40, oy + 5, "x = w/D", size=14, bold=True))
    
    frags.append(arrow(ox, oy + 10, ox, oy - gh - 30, color=LINE, sw=1.5))
    frags.append(text(ox, oy - gh - 42, "f(x)", size=14, bold=True))
    
    for x_val, label in [(0, "0.0"), (0.5, "0.5"), (1.0, "1.0")]:
        px = ox + x_val * gw
        frags.append(line(px, oy, px, oy + 6, color=LINE))
        frags.append(text(px, oy + 22, label, size=12))
        if x_val > 0:
            frags.append(line(px, oy, px, oy - gh, color="#e5e7eb", sw=1, dash="3,3"))
            
    frags.append(line(ox - 6, oy - gh, ox, oy - gh, color=LINE))
    frags.append(text(ox - 22, oy - gh + 4, "1.0", size=12))
    frags.append(line(ox, oy - gh, ox + gw, oy - gh, color="#e5e7eb", sw=1, dash="3,3"))
    
    pts_linear = []
    pts_joglekar = []
    pts_prodromakis = []
    
    steps = 100
    p = 2
    p_prod = 3
    j_prod = 1.0
    
    for s in range(steps + 1):
        x = s / float(steps)
        px = ox + x * gw
        
        py_lin = oy - 1.0 * gh
        pts_linear.append((px, py_lin))
        
        f_jog = 1.0 - math.pow(2.0 * x - 1.0, 2 * p)
        py_jog = oy - max(0.0, f_jog) * gh
        pts_joglekar.append((px, py_jog))
        
        f_prod = j_prod * (1.0 - math.pow(math.pow(x - 0.5, 2) + 0.75, p_prod))
        py_prod = oy - max(0.0, f_prod) * gh
        pts_prodromakis.append((px, py_prod))
        
    def draw_path(pts, color, sw, dash=None):
        d_str = " ".join(["%s%.1f,%.1f" % ("M" if i==0 else "L", p[0], p[1]) for i, p in enumerate(pts)])
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d_str, color, sw, dash_attr)
        
    frags.append(draw_path(pts_linear, MUTED, 1.5, dash="4,4"))
    frags.append(draw_path(pts_joglekar, POS, 2.5))
    frags.append(draw_path(pts_prodromakis, NEG, 2.5))
    
    leg_x, leg_y = ox + 40, oy - gh + 20
    frags.append(rect(leg_x, leg_y, 300, 100, fill="#ffffff", stroke=LINE, rx=6))
    
    frags.append(line(leg_x + 15, leg_y + 22, leg_x + 55, leg_y + 22, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(leg_x + 65, leg_y + 26, "Ідеальний дрейф f(x) = 1", size=12, anchor="start"))
    
    frags.append(line(leg_x + 15, leg_y + 50, leg_x + 55, leg_y + 50, color=POS, sw=2.5))
    frags.append(text(leg_x + 65, leg_y + 54, "Вікно Джоглекара f(x) = 1 − (2x−1)²ᵖ", size=12, anchor="start", bold=True))
    
    frags.append(line(leg_x + 15, leg_y + 78, leg_x + 55, leg_y + 78, color=NEG, sw=2.5))
    frags.append(text(leg_x + 65, leg_y + 82, "Вікно Продромакіса f(x) = j·(1 − [...])", size=12, anchor="start", bold=True))
    
    frags.append(fitbox(ox - 30, oy - gh/2 - 15, 110, 36, "Придушення\nпри x → 0", size=11, fill="#fdecea", stroke=POS))
    frags.append(fitbox(ox + gw - 80, oy - gh/2 - 15, 110, 36, "Придушення\nпри x → 1", size=11, fill="#fdecea", stroke=POS))
    
    render(os.path.join(IMG_DIR, 'window-functions-drift.svg'), w, h, *frags,
           title="Віконні функції нелінійного дрейфу вакансій біля меж наноплівки")

if __name__ == '__main__':
    fig_four_fundamental_variables()
    fig_hp_memristor_structure()
    fig_pinched_hysteresis-loop() if False else None
    fig_pinched_hysteresis_loop()
    fig_window_functions_drift()
    print("All figures generated successfully!")
