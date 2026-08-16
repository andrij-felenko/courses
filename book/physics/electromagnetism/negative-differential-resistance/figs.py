# -*- coding: utf-8 -*-
import os
import sys
import math

# Add scripts directory to path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT,
    text, mtext, fit_font, text_width, esc
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fitbox(x, y, w, h, title="", subtitle="", fill=FILL, border=LINE, title_color=INK, title_size=13, title_bold=True):
    """Draw a box with title and subtitle fitted properly."""
    res = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{border}" stroke-width="1.5" rx="4"/>']
    if title:
        tsize = fit_font(title, w - 16, size=title_size, bold=title_bold, min_size=10)
        res.append(text(x + w/2, y + (18 if subtitle else h/2 + 4), title, size=tsize, color=title_color, bold=title_bold))
    if subtitle:
        ssize = fit_font(subtitle, w - 16, size=11, bold=False, min_size=9)
        res.append(text(x + w/2, y + 36, subtitle, size=ssize, color=MUTED, bold=False))
    return "".join(res)

def arrow(x1, y1, x2, y2, color=LINE, width=1.5):
    """Draw a line with an arrowhead."""
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    head_len = 8
    a1 = angle + math.pi - 0.4
    a2 = angle + math.pi + 0.4
    px1 = x2 + head_len * math.cos(a1)
    py1 = y2 + head_len * math.sin(a1)
    px2 = x2 + head_len * math.cos(a2)
    py2 = y2 + head_len * math.sin(a2)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"/>' \
           f'<polygon points="{x2:.1f},{y2:.1f} {px1:.1f},{py1:.1f} {px2:.1f},{py2:.1f}" fill="{color}"/>'


# ==============================================================================
# Figure 1: iv-curves-types.svg
# N-type (Voltage-Controlled) vs S-type (Current-Controlled) NDR curves
# ==============================================================================
def create_fig_iv_curves():
    w, h = 820, 420
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    # Panel 1: N-type (Voltage controlled - Tunnel diode / Gunn)
    svg.append(f'<rect x="20" y="20" width="375" height="380" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(207.5, 45, "N-тип (керований напругою / VCNDR)", size=13, color=INK, bold=True))
    svg.append(text(207.5, 63, "Приклад: тунельний діод, діод Ґанна", size=10, color=MUTED))

    # Axes N-type
    ox1, oy1 = 70, 340
    svg.append(arrow(ox1, oy1, 360, oy1, color=LINE, width=1.5)) # V axis
    svg.append(arrow(ox1, oy1, ox1, 85, color=LINE, width=1.5))  # I axis
    svg.append(text(365, oy1 + 4, "V", size=12, color=INK, bold=True, anchor="start"))
    svg.append(text(ox1 - 10, 85, "I", size=12, color=INK, bold=True, anchor="end"))

    # N-curve coordinates
    p_peak = (150, 140)
    p_val  = (240, 290)
    
    path_n = f"M {ox1},{oy1} C 100,240 125,140 {p_peak[0]},{p_peak[1]} C 175,140 210,290 {p_val[0]},{p_val[1]} C 270,290 310,200 340,110"
    svg.append(f'<path d="{path_n}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    # NDR region label positioned above the slope
    svg.append(text(215, 175, "NDR (dV/dI < 0)", size=11, color=POS, bold=True))

    # Dashed lines for V_p, I_p, V_v, I_v
    svg.append(f'<line x1="{p_peak[0]}" y1="{p_peak[1]}" x2="{p_peak[0]}" y2="{oy1}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<line x1="{ox1}" y1="{p_peak[1]}" x2="{p_peak[0]}" y2="{p_peak[1]}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<circle cx="{p_peak[0]}" cy="{p_peak[1]}" r="4" fill="{POS}"/>')
    svg.append(text(p_peak[0], oy1 + 16, "V_p", size=11, color=INK, bold=True))
    svg.append(text(ox1 - 8, p_peak[1] + 4, "I_p", size=11, color=INK, bold=True, anchor="end"))

    svg.append(f'<line x1="{p_val[0]}" y1="{p_val[1]}" x2="{p_val[0]}" y2="{oy1}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<line x1="{ox1}" y1="{p_val[1]}" x2="{p_val[0]}" y2="{p_val[1]}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<circle cx="{p_val[0]}" cy="{p_val[1]}" r="4" fill="{POS}"/>')
    svg.append(text(p_val[0], oy1 + 16, "V_v", size=11, color=INK, bold=True))
    svg.append(text(ox1 - 8, p_val[1] + 4, "I_v", size=11, color=INK, bold=True, anchor="end"))

    # Load line for N-type (low R_L, steep load line)
    svg.append(f'<line x1="90" y1="100" x2="310" y2="330" stroke="{FIELD}" stroke-width="2"/>')
    svg.append(text(315, 325, "R_L < |r_d| (Стійка)", size=10, color=FIELD, bold=True, anchor="start"))


    # Panel 2: S-type (Current controlled - GDT / UJT / Dynatron / Thyristor)
    svg.append(f'<rect x="425" y="20" width="375" height="380" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(612.5, 45, "S-тип (керований струмом / CCNDR)", size=13, color=INK, bold=True))
    svg.append(text(612.5, 63, "Приклад: газорозрядник (GDT), одноперехідний транзистор", size=10, color=MUTED))

    # Axes S-type
    ox2, oy2 = 475, 340
    svg.append(arrow(ox2, oy2, 765, oy2, color=LINE, width=1.5)) # V axis
    svg.append(arrow(ox2, oy2, ox2, 85, color=LINE, width=1.5))  # I axis
    svg.append(text(770, oy2 + 4, "V", size=12, color=INK, bold=True, anchor="start"))
    svg.append(text(ox2 - 10, 85, "I", size=12, color=INK, bold=True, anchor="end"))

    # S-curve coordinates
    p_br = (730, 310)
    p_m  = (540, 200)

    path_s = f"M {ox2},{oy2} L 710,310 C 730,310 740,290 {p_br[0]},{p_br[1]} C 660,270 550,230 {p_m[0]},{p_m[1]} C 530,170 630,120 720,105"
    svg.append(f'<path d="{path_s}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    # NDR region highlight S-type
    svg.append(text(640, 230, "NDR (dV/dI < 0)", size=11, color=POS, bold=True))

    # Dashed lines for V_br, I_br, V_m, I_m
    svg.append(f'<line x1="{p_br[0]}" y1="{p_br[1]}" x2="{p_br[0]}" y2="{oy2}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<circle cx="{p_br[0]}" cy="{p_br[1]}" r="4" fill="{POS}"/>')
    svg.append(text(p_br[0], oy2 + 16, "V_br", size=11, color=INK, bold=True))

    svg.append(f'<line x1="{p_m[0]}" y1="{p_m[1]}" x2="{p_m[0]}" y2="{oy2}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<circle cx="{p_m[0]}" cy="{p_m[1]}" r="4" fill="{POS}"/>')
    svg.append(text(p_m[0], oy2 + 16, "V_m", size=11, color=INK, bold=True))

    # High impedance load line for S-type
    svg.append(f'<line x1="495" y1="120" x2="745" y2="330" stroke="{FIELD}" stroke-width="2"/>')
    svg.append(text(500, 110, "R_L > |r_d| (Стійка)", size=10, color=FIELD, bold=True, anchor="start"))

    svg.append('</svg>')
    with open(os.path.join(IMG_DIR, "iv-curves-types.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ==============================================================================
# Figure 2: tunnel-diode-bands.svg
# Energy band diagrams of Tunnel Diode across bias states
# ==============================================================================
def create_fig_tunnel_bands():
    w, h = 840, 400
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    stages = [
        ("а) Нульовий зсув (V = 0)", "Рівновага Фермі, I = 0", 0, 0),
        ("б) Піковий струм (V = V_p)", "Максимальне тунелювання", 15, 80),
        ("в) Зона NDR (V_p < V < V_v)", "Перекриття зменшується", 35, 40),
        ("г) Долина (V = V_v)", "Тунелювання припинено", 55, 10)
    ]

    box_w = 195
    box_h = 350
    spacing = 10

    for i, (title_str, desc_str, shift_y, tunnel_w) in enumerate(stages):
        bx = 15 + i * (box_w + spacing)
        by = 25

        svg.append(f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="5"/>')
        
        tsize = fit_font(title_str, box_w - 10, size=11, bold=True)
        svg.append(text(bx + box_w/2, by + 20, title_str, size=tsize, color=INK, bold=True))
        dsize = fit_font(desc_str, box_w - 10, size=10, bold=False)
        svg.append(text(bx + box_w/2, by + 36, desc_str, size=dsize, color=MUTED))

        mid_x = bx + box_w/2
        
        p_ec = 140 + shift_y
        p_ev = 220 + shift_y
        
        n_ec = 170
        n_ev = 250

        svg.append(f'<line x1="{bx+15}" y1="{p_ec}" x2="{mid_x-10}" y2="{p_ec}" stroke="{NEG}" stroke-width="2"/>')
        svg.append(f'<line x1="{bx+15}" y1="{p_ev}" x2="{mid_x-10}" y2="{p_ev}" stroke="{NEG}" stroke-width="2"/>')
        svg.append(f'<rect x="{bx+15}" y="{p_ev}" width="{mid_x-10-(bx+15)}" height="45" fill="{NEG}" opacity="0.15"/>')
        svg.append(text(bx+35, p_ev+25, "p-тип", size=10, color=NEG, bold=True))

        svg.append(f'<path d="M {mid_x-10},{p_ec} C {mid_x},{p_ec} {mid_x},{n_ec} {mid_x+10},{n_ec}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
        svg.append(f'<path d="M {mid_x-10},{p_ev} C {mid_x},{p_ev} {mid_x},{n_ev} {mid_x+10},{n_ev}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')

        svg.append(f'<line x1="{mid_x+10}" y1="{n_ec}" x2="{bx+box_w-15}" y2="{n_ec}" stroke="{POS}" stroke-width="2"/>')
        svg.append(f'<line x1="{mid_x+10}" y1="{n_ev}" x2="{bx+box_w-15}" y2="{n_ev}" stroke="{POS}" stroke-width="2"/>')
        svg.append(f'<rect x="{mid_x+10}" y="{n_ec}" width="{bx+box_w-15-(mid_x+10)}" height="45" fill="{POS}" opacity="0.15"/>')
        svg.append(text(bx+box_w-35, n_ec+25, "n-тип", size=10, color=POS, bold=True))

        ef_y = 200
        svg.append(f'<line x1="{bx+10}" y1="{ef_y}" x2="{bx+box_w-10}" y2="{ef_y}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3,3"/>')
        svg.append(text(bx+18, ef_y-6, "E_F", size=9, color=MUTED, bold=True, anchor="start"))

        if tunnel_w > 0:
            tunnel_y = (n_ec + p_ev) / 2
            svg.append(arrow(mid_x+30, tunnel_y, mid_x-30, tunnel_y, color=POS, width=2))
            svg.append(text(mid_x, tunnel_y + 15, "e⁻ тунель", size=9, color=POS, bold=True))
        else:
            svg.append(text(mid_x, 280, "Немає перекриття", size=9, color=MUTED, italic=True))

        svg.append(text(bx + box_w/2, by + box_h - 15, f"V_fwd = {shift_y} mV", size=10, color=INK))

    svg.append('</svg>')
    with open(os.path.join(IMG_DIR, "tunnel-diode-bands.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ==============================================================================
# Figure 3: gunn-band-velocity.svg
# Gunn effect: Band structure (Gamma vs L valleys) and v(E) drift velocity curve
# ==============================================================================
def create_fig_gunn_band_velocity():
    w, h = 820, 400
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    # Panel 1: Band Structure GaAs (Gamma and L valleys)
    svg.append(f'<rect x="20" y="20" width="375" height="360" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(207.5, 45, "Дводолинна зона провідності GaAs", size=13, color=INK, bold=True))
    svg.append(text(207.5, 63, "Міждолинне розсіювання гарячих електронів", size=10, color=MUTED))

    cx_g = 120
    cy_g = 300
    path_gamma = f"M {cx_g-50},{cy_g-130} Q {cx_g},{cy_g} {cx_g+50},{cy_g-130}"
    svg.append(f'<path d="{path_gamma}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    svg.append(text(cx_g, cy_g + 18, "Центральна долина Г", size=10, color=NEG, bold=True))
    svg.append(text(cx_g, cy_g + 34, "m₁* = 0.067m₀", size=9, color=MUTED))

    cx_l = 290
    cy_l = 210
    path_l = f"M {cx_l-45},{cy_l-75} Q {cx_l},{cy_l} {cx_l+45},{cy_l-75}"
    svg.append(f'<path d="{path_l}" fill="none" stroke="{POS}" stroke-width="3"/>')
    svg.append(text(cx_l, cy_l + 18, "Супутникова долина L", size=10, color=POS, bold=True))
    svg.append(text(cx_l, cy_l + 34, "m₂* = 0.55m₀", size=9, color=MUTED))

    svg.append(f'<line x1="{cx_g+40}" y1="{cy_g}" x2="{cx_l-30}" y2="{cy_g}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<line x1="{cx_g+40}" y1="{cy_l}" x2="{cx_l-30}" y2="{cy_l}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(arrow(cx_g+25, cy_g, cx_g+25, cy_l, color=INK, width=1.5))
    svg.append(text(cx_g+20, (cy_g+cy_l)/2 + 4, "ΔE = 0.31 eV", size=9, color=INK, bold=True, anchor="end"))

    # Scattering arrow
    svg.append(arrow(cx_g+30, cy_g-50, cx_l-30, cy_l-10, color=POS, width=2))
    svg.append(text(210, 160, "Нагрів електронів", size=9, color=POS, bold=True))


    # Panel 2: Drift Velocity vs Field v(E)
    svg.append(f'<rect x="425" y="20" width="375" height="360" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(612.5, 45, "Характеристика дрейфової швидкості v(E)", size=13, color=INK, bold=True))
    svg.append(text(612.5, 63, "Область від'ємної диференційної рухливості", size=10, color=MUTED))

    ox2, oy2 = 475, 330
    svg.append(arrow(ox2, oy2, 765, oy2, color=LINE, width=1.5))
    svg.append(arrow(ox2, oy2, ox2, 100, color=LINE, width=1.5))
    svg.append(text(770, oy2 + 4, "E (кВ/см)", size=10, color=INK, bold=True, anchor="start"))
    svg.append(text(ox2 - 10, 100, "v (10⁷ см/с)", size=10, color=INK, bold=True, anchor="end"))

    e_th_x = 550
    v_peak_y = 140
    path_ve = f"M {ox2},{oy2} C 510,250 530,140 {e_th_x},{v_peak_y} C 590,140 650,260 690,260 L 750,250"
    svg.append(f'<path d="{path_ve}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    svg.append(text(630, 175, "dv/dE < 0 (NDR)", size=11, color=POS, bold=True))

    svg.append(f'<line x1="{e_th_x}" y1="{v_peak_y}" x2="{e_th_x}" y2="{oy2}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<line x1="{ox2}" y1="{v_peak_y}" x2="{e_th_x}" y2="{v_peak_y}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
    svg.append(f'<circle cx="{e_th_x}" cy="{v_peak_y}" r="4" fill="{POS}"/>')

    svg.append(text(e_th_x, oy2 + 16, "E_th ≈ 3.2 kV/cm", size=10, color=INK, bold=True))
    svg.append(text(ox2 - 8, v_peak_y + 4, "v_peak", size=10, color=INK, bold=True, anchor="end"))

    svg.append('</svg>')
    with open(os.path.join(IMG_DIR, "gunn-band-velocity.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ==============================================================================
# Figure 4: lc-oscillator-cancellation.svg
# LC Resonator with NDR element compensating loss resistance R_s
# ==============================================================================
def create_fig_lc_oscillator():
    w, h = 800, 360
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    svg.append(f'<rect x="20" y="20" width="760" height="320" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(400, 45, "Компенсація втрат у LC-контурі за допомогою NDR", size=13, color=INK, bold=True))
    svg.append(text(400, 63, "Повна активна опірність R_total = R_втрат - |r_d| ≤ 0 створює незатухаючі коливання", size=10, color=MUTED))

    lx1, ly1 = 90, 110
    lx2, ly2 = 470, 270

    svg.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly1}" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<line x1="{lx1}" y1="{ly2}" x2="{lx2}" y2="{ly2}" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx1}" y2="{ly2}" stroke="{LINE}" stroke-width="2"/>')
    svg.append(f'<line x1="{lx2}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="{LINE}" stroke-width="2"/>')

    svg.append(fitbox(50, 160, 80, 60, title="L", subtitle="Індуктивність", fill=BG, border=LINE))

    svg.append(f'<line x1="230" y1="{ly1}" x2="230" y2="{ly2}" stroke="{LINE}" stroke-width="2"/>')
    svg.append(fitbox(190, 160, 80, 60, title="C", subtitle="Ємність", fill=BG, border=LINE))

    svg.append(f'<line x1="350" y1="{ly1}" x2="350" y2="{ly2}" stroke="{LINE}" stroke-width="2"/>')
    svg.append(fitbox(310, 160, 80, 60, title="R_s", subtitle="Втрати (>0)", fill=BG, border=POS))

    svg.append(fitbox(430, 160, 80, 60, title="-|r_d|", subtitle="NDR (<0)", fill=BG, border=NEG))

    svg.append(arrow(520, 190, 570, 190, color=FIELD, width=2))
    svg.append(text(545, 175, "Джерело DC", size=9, color=FIELD, bold=True))

    # Right side: Mathematical summary box with proper text spacing
    box_rx = 580
    box_ry = 95
    box_rw = 190
    box_rh = 220
    svg.append(f'<rect x="{box_rx}" y="{box_ry}" width="{box_rw}" height="{box_rh}" fill="{BG}" stroke="{FIELD}" stroke-width="1.5" rx="4"/>')
    svg.append(text(box_rx + box_rw/2, box_ry + 22, "Умова генерації", size=12, color=INK, bold=True))
    svg.append(text(box_rx + box_rw/2, box_ry + 55, "R_total = R_s - |r_d|", size=11, color=INK, bold=True))
    svg.append(text(box_rx + box_rw/2, box_ry + 90, "Якщо |r_d| > R_s:", size=10, color=MUTED))
    svg.append(text(box_rx + box_rw/2, box_ry + 118, "Амплітуда зростає", size=11, color=POS, bold=True))
    svg.append(text(box_rx + box_rw/2, box_ry + 155, "Стаціонарний режим:", size=10, color=MUTED))
    svg.append(text(box_rx + box_rw/2, box_ry + 185, "|r_d(A)| = R_s", size=11, color=FIELD, bold=True))

    svg.append('</svg>')
    with open(os.path.join(IMG_DIR, "lc-oscillator-cancellation.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ==============================================================================
# Figure 5: bistable-loadline.svg
# Load line analysis showing bistability (Points A, B stable, C unstable)
# ==============================================================================
def create_fig_bistable_loadline():
    w, h = 820, 380
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    svg.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    svg.append(f'<rect x="20" y="20" width="780" height="340" fill="{FILL}" stroke="{LINE}" stroke-width="1" rx="6"/>')
    svg.append(text(410, 45, "Навантажувальна пряма та три точки рівноваги (бістабільність)", size=13, color=INK, bold=True))
    svg.append(text(410, 63, "Перетин навантажувальної прямої R_L з вольт-амперною характеристикою N-типу", size=10, color=MUTED))

    ox, oy = 80, 320
    svg.append(arrow(ox, oy, 740, oy, color=LINE, width=1.5))
    svg.append(arrow(ox, oy, ox, 90, color=LINE, width=1.5))
    svg.append(text(745, oy + 4, "V", size=12, color=INK, bold=True, anchor="start"))
    svg.append(text(ox - 10, 90, "I", size=12, color=INK, bold=True, anchor="end"))

    p_peak = (240, 130)
    p_val  = (460, 280)
    path_n = f"M {ox},{oy} C 150,240 180,130 {p_peak[0]},{p_peak[1]} C 300,130 400,280 {p_val[0]},{p_val[1]} C 520,280 620,200 680,110"
    svg.append(f'<path d="{path_n}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    p_vcc = (700, oy)
    p_imax = (110, 110)
    svg.append(f'<line x1="{p_imax[0]}" y1="{p_imax[1]}" x2="{p_vcc[0]}" y2="{p_vcc[1]}" stroke="{POS}" stroke-width="2"/>')
    svg.append(text(p_vcc[0], oy + 16, "V_CC", size=10, color=POS, bold=True))
    svg.append(text(p_imax[0] + 40, p_imax[1] - 5, "I_max = V_CC / R_L", size=9, color=POS, bold=True))

    pt_a = (180, 215)
    svg.append(f'<circle cx="{pt_a[0]}" cy="{pt_a[1]}" r="5" fill="{FIELD}"/>')
    svg.append(text(pt_a[0], pt_a[1] + 20, "Точка A (Стан «УВІМК»)", size=10, color=FIELD, bold=True))

    pt_c = (350, 180)
    svg.append(f'<circle cx="{pt_c[0]}" cy="{pt_c[1]}" r="5" fill="{POS}"/>')
    svg.append(text(pt_c[0], pt_c[1] - 12, "Точка C (Нестійка NDR)", size=10, color=POS, bold=True))

    pt_b = (560, 150)
    svg.append(f'<circle cx="{pt_b[0]}" cy="{pt_b[1]}" r="5" fill="{FIELD}"/>')
    svg.append(text(pt_b[0] + 35, pt_b[1] + 25, "Точка B (Стан «ВИМК»)", size=10, color=FIELD, bold=True, anchor="start"))

    svg.append('</svg>')
    with open(os.path.join(IMG_DIR, "bistable-loadline.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def main():
    create_fig_iv_curves()
    create_fig_tunnel_bands()
    create_fig_gunn_band_velocity()
    create_fig_lc_oscillator()
    create_fig_bistable_loadline()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
