# -*- coding: utf-8 -*-
import os
import sys
import math

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_direct_vs_indirect():
    """Фігура 1: Прямозонні проти непрямозонних напівпровідників у E(k) просторі."""
    w, h = 800, 390
    out = []
    
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # --- Ліва панель: Прямозонний напівпровідник (GaAs, GaN) ---
    out.append(rect(15, 15, 375, 360, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=8))
    out.append(text(202, 38, "Прямозонний напівпровідник (GaAs, GaN)", size=13, bold=True, color=INK))
    
    cx_l = 202
    out.append(arrow(55, 290, 350, 290, color=MUTED, sw=1.2)) # k axis
    out.append(text(360, 293, "k", size=13, italic=True, color=MUTED, anchor="start"))
    out.append(arrow(cx_l, 300, cx_l, 55, color=MUTED, sw=1.2)) # E axis
    out.append(text(cx_l, 48, "E", size=13, italic=True, color=MUTED, anchor="middle"))
    
    pts_ec_l = []
    for dx in range(-100, 101, 5):
        x = cx_l + dx
        y = 125 + 0.007 * (dx**2)
        pts_ec_l.append(f"{x:.1f},{y:.1f}")
    out.append(f'<path d="M {" L ".join(pts_ec_l)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(text(cx_l + 105, 120, "Зона провідності E_c", size=11, bold=True, color=NEG, anchor="start"))
    
    pts_ev_l = []
    for dx in range(-100, 101, 5):
        x = cx_l + dx
        y = 235 - 0.007 * (dx**2)
        pts_ev_l.append(f"{x:.1f},{y:.1f}")
    out.append(f'<path d="M {" L ".join(pts_ev_l)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    out.append(text(cx_l + 105, 250, "Валентна зона E_v", size=11, bold=True, color=POS, anchor="start"))
    
    out.append(line(cx_l - 60, 125, cx_l - 60, 235, color=MUTED, sw=1, dash="3,3"))
    out.append(arrow(cx_l - 60, 180, cx_l - 60, 127, color=INK, sw=1.2))
    out.append(arrow(cx_l - 60, 180, cx_l - 60, 233, color=INK, sw=1.2))
    out.append(text(cx_l - 72, 184, "E_g", size=13, bold=True, color=INK, anchor="end"))
    
    out.append(circle(cx_l, 125, 6, fill=NEG, stroke="#ffffff", sw=1.5))
    out.append(text(cx_l, 128, "−", size=11, bold=True, color="#ffffff", anchor="middle"))
    
    out.append(circle(cx_l, 235, 6, fill=POS, stroke="#ffffff", sw=1.5))
    out.append(text(cx_l, 238, "+", size=11, bold=True, color="#ffffff", anchor="middle"))
    
    out.append(arrow(cx_l, 135, cx_l, 225, color=FIELD, sw=2))
    
    out.append(arrow(cx_l + 10, 180, cx_l + 70, 180, color="#e67e22", sw=2))
    out.append(text(cx_l + 75, 184, "Фотон hν", size=12, bold=True, color="#d35400", anchor="start"))
    
    tb_l, _, _ = textbox(202, 340, "Вертикальний перехід: Δk = 0\nВисока випромінювальна ефективність", size=11, fill="#e8f8f5", stroke=FIELD, sw=1)
    out.append(tb_l)

    # --- Права панель: Непрямозонний напівпровідник (Si, Ge) ---
    out.append(rect(410, 15, 375, 360, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=8))
    out.append(text(597, 38, "Непрямозонний напівпровідник (Si, Ge)", size=13, bold=True, color=INK))
    
    cx_r = 520
    out.append(arrow(435, 290, 755, 290, color=MUTED, sw=1.2))
    out.append(text(763, 293, "k", size=13, italic=True, color=MUTED, anchor="start"))
    out.append(arrow(cx_r, 300, cx_r, 55, color=MUTED, sw=1.2))
    out.append(text(cx_r, 305, "k = 0", size=10, color=MUTED, anchor="middle"))
    out.append(text(cx_r - 8, 48, "E", size=13, italic=True, color=MUTED, anchor="end"))
    
    cx_ec = cx_r + 110
    pts_ec_r = []
    for dx in range(-75, 76, 5):
        x = cx_ec + dx
        y = 125 + 0.008 * (dx**2)
        pts_ec_r.append(f"{x:.1f},{y:.1f}")
    out.append(f'<path d="M {" L ".join(pts_ec_r)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(text(cx_ec, 100, "Мінімум E_c", size=11, bold=True, color=NEG, anchor="middle"))
    
    pts_ev_r = []
    for dx in range(-75, 76, 5):
        x = cx_r + dx
        y = 235 - 0.008 * (dx**2)
        pts_ev_r.append(f"{x:.1f},{y:.1f}")
    out.append(f'<path d="M {" L ".join(pts_ev_r)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    out.append(text(cx_r - 40, 260, "Максимум E_v", size=11, bold=True, color=POS, anchor="end"))
    
    out.append(circle(cx_ec, 125, 6, fill=NEG, stroke="#ffffff", sw=1.5))
    out.append(text(cx_ec, 128, "−", size=11, bold=True, color="#ffffff", anchor="middle"))
    
    out.append(circle(cx_r, 235, 6, fill=POS, stroke="#ffffff", sw=1.5))
    out.append(text(cx_r, 238, "+", size=11, bold=True, color="#ffffff", anchor="middle"))
    
    out.append(line(cx_ec, 133, cx_r + 10, 227, color=MUTED, sw=1.5, dash="4,4"))
    
    out.append(arrow(cx_ec, 150, cx_r + 20, 150, color="#8e44ad", sw=1.8))
    out.append(text(cx_r + 65, 140, "Фонон ℏq (Δk)", size=11, bold=True, color="#8e44ad", anchor="middle"))
    
    out.append(arrow(cx_r, 185, cx_r, 225, color="#e67e22", sw=1.8))
    out.append(text(cx_r - 12, 205, "hν", size=11, bold=True, color="#d35400", anchor="end"))
    
    tb_r, _, _ = textbox(597, 340, "Невертикальний перехід: потрібен фонон (3 частинки)\nНизька ймовірність, виділення тепла", size=11, fill="#fdf2e9", stroke="#e67e22", sw=1)
    out.append(tb_r)
    
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        f'<defs>\n'
        f'<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'<path d="M 0 1 L 10 5 L 0 9 z" fill="{INK}"/>\n'
        f'</marker>\n'
        f'</defs>\n'
        + "\n".join(out) +
        '\n</svg>'
    )
    return svg_content

def generate_pn_injection_luminescence():
    """Фігура 2: Інжекція носіїв та випромінювальна рекомбінація в прямозміщеному p-n переході."""
    w, h = 760, 380
    out = []
    
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    out.append(rect(40, 40, 240, 280, fill="#ebf5fb", stroke="#aed6f1", sw=1.5, rx=0))
    out.append(rect(280, 40, 200, 280, fill="#e8f8f5", stroke="#a3e4d7", sw=1.5, rx=0))
    out.append(rect(480, 40, 240, 280, fill="#fadbd8", stroke="#f5b7b1", sw=1.5, rx=0))
    
    out.append(text(160, 65, "n-область (донори)", size=13, bold=True, color=NEG))
    out.append(text(380, 65, "Зона рекомбінації", size=13, bold=True, color=FIELD))
    out.append(text(600, 65, "p-область (акцептори)", size=13, bold=True, color=POS))
    
    path_ec = "M 40,120 L 260,120 C 330,120 350,170 420,170 L 720,170"
    out.append(f'<path d="{path_ec}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    out.append(text(60, 110, "E_c (зона провідності)", size=11, bold=True, color=NEG))
    
    path_ev = "M 40,240 L 260,240 C 330,240 350,290 420,290 L 720,290"
    out.append(f'<path d="{path_ev}" fill="none" stroke="{POS}" stroke-width="3"/>')
    out.append(text(60, 255, "E_v (валентна зона)", size=11, bold=True, color=POS))
    
    out.append(line(40, 140, 380, 140, color=NEG, sw=1.5, dash="5,3"))
    out.append(text(80, 155, "E_Fn (квазірівень Фермі)", size=11, color=NEG))
    
    out.append(line(380, 270, 720, 270, color=POS, sw=1.5, dash="5,3"))
    out.append(text(640, 260, "E_Fp", size=11, color=POS, anchor="end"))
    
    out.append(arrow(360, 140, 360, 270, color=INK, sw=1.2))
    out.append(arrow(360, 270, 360, 140, color=INK, sw=1.2))
    out.append(text(348, 205, "qV_f", size=12, bold=True, color=INK, anchor="end"))
    
    for x_e in [120, 180, 240, 290]:
        out.append(circle(x_e, 120, 5, fill=NEG, stroke="#ffffff", sw=1))
        out.append(text(x_e, 123, "−", size=9, bold=True, color="#ffffff", anchor="middle"))
    out.append(arrow(200, 100, 310, 100, color=NEG, sw=2))
    out.append(text(250, 92, "Інжекція електронів", size=11, bold=True, color=NEG, anchor="middle"))
    
    for x_h in [640, 580, 520, 460]:
        out.append(circle(x_h, 290, 5, fill=POS, stroke="#ffffff", sw=1))
        out.append(text(x_h, 293, "+", size=9, bold=True, color="#ffffff", anchor="middle"))
    out.append(arrow(580, 310, 450, 310, color=POS, sw=2))
    out.append(text(515, 325, "Інжекція дірок", size=11, bold=True, color=POS, anchor="middle"))
    
    out.append(circle(380, 145, 6, fill=NEG, stroke="#ffffff", sw=1.5))
    out.append(circle(380, 245, 6, fill=POS, stroke="#ffffff", sw=1.5))
    out.append(arrow(380, 155, 380, 235, color=FIELD, sw=2.5))
    
    out.append(arrow(390, 195, 470, 195, color="#e67e22", sw=2.5))
    out.append(text(475, 199, "Випромінений фотон hν ≈ E_g", size=12, bold=True, color="#d35400", anchor="start"))
    
    out.append(line(160, 320, 160, 355, color=INK, sw=1.5))
    out.append(line(600, 320, 600, 355, color=INK, sw=1.5))
    out.append(line(160, 355, 340, 355, color=INK, sw=1.5))
    out.append(line(420, 355, 600, 355, color=INK, sw=1.5))
    
    out.append(line(340, 340, 340, 370, color=NEG, sw=3))
    out.append(line(355, 347, 355, 363, color=INK, sw=1.5))
    out.append(line(370, 340, 370, 370, color=INK, sw=1.5))
    out.append(line(385, 347, 385, 363, color=INK, sw=1.5))
    out.append(line(400, 340, 400, 370, color=POS, sw=3))
    out.append(text(370, 333, "Пряме зміщення V_f", size=11, bold=True, color=INK, anchor="middle"))
    out.append(text(325, 358, "−", size=14, bold=True, color=NEG))
    out.append(text(412, 358, "+", size=14, bold=True, color=POS))
    
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        f'<defs>\n'
        f'<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'<path d="M 0 1 L 10 5 L 0 9 z" fill="{INK}"/>\n'
        f'</marker>\n'
        f'</defs>\n'
        + "\n".join(out) +
        '\n</svg>'
    )
    return svg_content

def generate_quantum_efficiency_droop():
    """Фігура 3: Залежність внутрішнього квантового виходу η_int від густини струму J (ефект Оже-згасання / Auger droop)."""
    w, h = 820, 370
    out = []
    
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    out.append(text(w/2, 30, "Внутрішній квантовий вихід η_int та ефект Оже-згасання (Droop)", size=14, bold=True, color=INK))
    
    ox, oy = 80, 310
    gw, gh = 680, 230
    
    out.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    out.append(text(ox + gw, oy + 25, "Густина струму інжекції J (A/cm²)", size=11, bold=True, color=INK, anchor="end"))
    
    out.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    out.append(text(ox, oy - gh - 15, "Квантовий вихід η_int (%)", size=11, bold=True, color=INK, anchor="middle"))
    
    out.append(line(ox, oy - gh*0.5, ox + gw, oy - gh*0.5, color="#eaeded", sw=1, dash="4,4"))
    out.append(text(ox - 15, oy - gh*0.5 + 4, "50%", size=10, color=MUTED, anchor="end"))
    
    out.append(line(ox, oy - gh*0.9, ox + gw, oy - gh*0.9, color="#eaeded", sw=1, dash="4,4"))
    out.append(text(ox - 15, oy - gh*0.9 + 4, "90%", size=10, color=MUTED, anchor="end"))
    
    pts = []
    for i in range(100):
        t = i / 99.0
        x = ox + t * gw
        if t < 0.25:
            y_val = 0.1 + 0.78 * math.sin((t / 0.25) * (math.pi / 2))
        else:
            y_val = 0.88 - 0.48 * ((t - 0.25) / 0.75)**0.7
            
        y = oy - y_val * gh
        pts.append(f"{x:.1f},{y:.1f}")
        
    out.append(f'<path d="M {" L ".join(pts)}" fill="none" stroke="{FIELD}" stroke-width="3.5"/>')
    
    out.append(line(ox + 90, oy, ox + 90, oy - gh, color="#fadbd8", sw=1, dash="3,3"))
    tb1, _, _ = textbox(ox + 65, oy - gh*0.3, "Дефекти SRH\nR ~ An\n(низький струм)", size=10, fill="#fdf2e9", stroke="#e67e22", sw=1)
    out.append(tb1)
    
    x_peak = ox + 0.25 * gw
    y_peak = oy - 0.88 * gh
    out.append(circle(x_peak, y_peak, 6, fill=POS, stroke="#ffffff", sw=1.5))
    tb2, _, _ = textbox(x_peak + 50, y_peak - 25, "Максимум η_int\nR_r = B n²", size=11, bold=True, fill="#e8f8f5", stroke=FIELD, sw=1.2)
    out.append(tb2)
    
    out.append(line(ox + 410, oy, ox + 410, oy - gh, color="#d6eaf8", sw=1, dash="3,3"))
    # Розміщуємо tb3 у порожньому просторі над кривою спаду (y = oy - gh*0.8)
    tb3, _, _ = textbox(ox + 530, oy - gh*0.8, "Оже-згасання (Auger Droop)\nR_{Auger} ~ C n³\n(перегрів та високий струм)", size=10, fill="#ebf5fb", stroke=NEG, sw=1)
    out.append(tb3)
    
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        f'<defs>\n'
        f'<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'<path d="M 0 1 L 10 5 L 0 9 z" fill="{INK}"/>\n'
        f'</marker>\n'
        f'</defs>\n'
        + "\n".join(out) +
        '\n</svg>'
    )
    return svg_content

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    figures = {
        'direct-vs-indirect.svg': generate_direct_vs_indirect(),
        'pn-injection-luminescence.svg': generate_pn_injection_luminescence(),
        'quantum-efficiency-droop.svg': generate_quantum_efficiency_droop(),
    }
    
    for filename, content in figures.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Згенеровано: {filepath}")

if __name__ == '__main__':
    main()
