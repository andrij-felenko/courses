# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Дифузійна довжина носіїв"
(book/physics/condensed-matter-physics/diffusion-length)
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def polyline(pts_str, color=LINE, sw=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'

def save_svg(name, content):
    filepath = os.path.join(OUT_DIR, name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Збережено: {filepath}")

def make_defs():
    return '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2980b9"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>
    </marker>
  </defs>'''

# 1. carrier-injection-decay.svg
def gen_carrier_injection_decay():
    w, h = 820, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 25, "Експоненціальний спад концентрації надлишкових носіїв Δn(x) = Δn₀ · exp(-x / L)", size=15, bold=True)[0])

    ox, oy = 110, 340
    pw, ph = 620, 250

    # Grid & Axes
    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw - 10, oy + 35, "x (відстань від межі)", size=12, bold=True, anchor="end"))
    out.append(text(ox - 15, oy - ph - 15, "Δn(x)", size=12, bold=True, anchor="end"))

    # Characteristic positions: L, 2L, 3L
    l_px = 160
    
    # Points
    y0 = oy - ph * 0.9  # Δn0
    y_l1 = oy - (ph * 0.9) * math.exp(-1)   # ~0.368
    y_l2 = oy - (ph * 0.9) * math.exp(-2)   # ~0.135
    y_l3 = oy - (ph * 0.9) * math.exp(-3)   # ~0.050

    # Vertical dash lines
    for x_val, label_txt, y_val in [(1, "L", y_l1), (2, "2L", y_l2), (3, "3L", y_l3)]:
        x_pos = ox + x_val * l_px
        out.append(line(x_pos, oy, x_pos, y_val, color="#7f8c8d", sw=1, dash="4 4"))
        out.append(line(ox, y_val, x_pos, y_val, color="#7f8c8d", sw=1, dash="4 4"))
        out.append(text(x_pos, oy + 20, label_txt, size=13, bold=True, anchor="middle"))
        out.append(circle(x_pos, y_val, 4, fill="#c0392b"))

    # Origin markers
    out.append(text(ox - 10, oy + 20, "0", size=13, anchor="end"))
    out.append(text(ox - 12, y0 + 5, "Δn₀ (100%)", size=12, bold=True, anchor="end", color="#c0392b"))
    out.append(text(ox - 12, y_l1 + 4, "36.8%", size=11, anchor="end", color="#c0392b"))
    out.append(text(ox - 12, y_l2 + 4, "13.5%", size=11, anchor="end", color="#c0392b"))

    # Draw decay curve
    pts = []
    steps = 100
    for i in range(steps + 1):
        x_norm = (i / steps) * 3.6
        x_p = ox + x_norm * l_px
        y_norm = 0.9 * math.exp(-x_norm)
        y_p = oy - ph * y_norm
        pts.append(f"{x_p:.1f},{y_p:.1f}")

    out.append(polyline(" ".join(pts), color="#c0392b", sw=3))

    # Annotation box
    out.append(fitbox(ox + l_px + 20, oy - ph + 30, 300, 70, 
                      ["На відстані x = L концентрація", 
                       "парує у e ≈ 2.718 раза від початкової",
                       "Δn(L) = Δn₀ / e ≈ 0.368 · Δn₀"], 
                      bg="#fdfefe", stroke="#c0392b", size=12)[0])

    out.append("</svg>")
    save_svg("carrier-injection-decay.svg", "\n".join(out))


# 2. diffusion-vs-lifetime.svg
def gen_diffusion_vs_lifetime():
    w, h = 820, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 25, "Мікроскопічний механізм: хаотичне блукання D та рекомбінація τ", size=15, bold=True)[0])

    # Left panel: Brownian trajectory
    out.append(rect(40, 60, 350, 320, fill="#ffffff", stroke="#bdc3c7", rx=6))
    out.append(text(215, 85, "Хаотичне броунівське блукання", size=13, bold=True, anchor="middle", color="#2c3e50"))

    traj = [
        (80, 220), (105, 190), (130, 215), (115, 250), (145, 270), 
        (170, 240), (195, 260), (220, 210), (200, 185), (235, 160), 
        (270, 180), (290, 150), (320, 190), (340, 220)
    ]
    traj_str = " ".join([f"{x},{y}" for x, y in traj])
    out.append(polyline(traj_str, color="#2980b9", sw=2, dash="3 3"))

    for x, y in traj:
        out.append(circle(x, y, 3, fill="#3498db"))

    out.append(circle(80, 220, 6, fill="#27ae60"))
    out.append(text(80, 245, "Інжекція (t=0)", size=11, bold=True, anchor="middle", color="#27ae60"))

    out.append(circle(340, 220, 7, fill="#c0392b"))
    out.append(text(340, 245, "Рекомбінація (t=τ)", size=11, bold=True, anchor="middle", color="#c0392b"))

    out.append(line(80, 310, 340, 310, color="#c0392b", sw=2))
    out.append(arrow(80, 310, 340, 310, color="#c0392b", sw=2))
    out.append(arrow(340, 310, 80, 310, color="#c0392b", sw=2))
    out.append(text(210, 305, "Зсув L = √(D · τ)", size=13, bold=True, anchor="middle", color="#c0392b"))

    # Right panel: Formula & Balance
    out.append(rect(430, 60, 350, 320, fill="#ffffff", stroke="#bdc3c7", rx=6))
    out.append(text(605, 85, "Баланс параметрів переносу", size=13, bold=True, anchor="middle", color="#2c3e50"))

    out.append(fitbox(605, 140, 320, 50, ["Коефіцієнт дифузії (інтенсивність):", "D = μ · (k_B · T / q)"], bg="#ebf5fb", stroke="#2980b9", size=12)[0])
    out.append(fitbox(605, 210, 320, 50, ["Час життя неосновного носія:", "τ = 1 / (N_t · σ · v_th)"], bg="#fdebd0", stroke="#e67e22", size=12)[0])
    out.append(fitbox(605, 290, 320, 60, ["Дифузійна довжина:", "L = √(D · τ) = √[ (k_B·T/q) · μ · τ ]"], bg="#fadbd8", stroke="#c0392b", size=13)[0])

    out.append("</svg>")
    save_svg("diffusion-vs-lifetime.svg", "\n".join(out))


# 3. solar-cell-collection.svg
def gen_solar_cell_collection():
    w, h = 820, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 25, "Вплив дифузійної довжини L на збирання носіїв у сонячному елементі", size=15, bold=True)[0])

    # Left diagram: L >= W (Good case)
    out.append(rect(40, 60, 350, 340, fill="#ffffff", stroke="#27ae60", sw=2, rx=6))
    out.append(text(215, 76, "Високий ККД: L ≥ W (чистий кристал)", size=12, bold=True, anchor="middle", color="#27ae60"))

    out.append(rect(60, 110, 310, 30, fill="#d6eaf8", stroke="#2980b9"))
    out.append(text(215, 130, "n+ емітер (тонкий)", size=11, anchor="middle"))

    out.append(rect(60, 140, 310, 25, fill="#f9e79f", stroke="#f39c12"))
    out.append(text(215, 157, "p-n перехід (збіднена зона)", size=11, anchor="middle", bold=True))

    out.append(rect(60, 165, 310, 200, fill="#e8f8f5", stroke="#27ae60"))
    out.append(text(215, 290, "p-база (товщина W)", size=12, anchor="middle", color="#16a085"))

    for lx in [100, 215, 330]:
        out.append(line(lx, 94, lx, 108, color="#f1c40f", sw=2, dash="4 2"))
        out.append(arrow(lx, 94, lx, 108, color="#f39c12", sw=2))

    out.append(circle(215, 220, 6, fill="#f39c12"))
    out.append(text(230, 220, "hν → e⁻ + h⁺", size=11, bold=True, color="#e67e22"))

    out.append(line(215, 220, 215, 165, color="#27ae60", sw=2, dash="3 3"))
    out.append(arrow(215, 220, 215, 165, color="#27ae60", sw=2))
    out.append(text(130, 195, "Доходить до p-n!", size=11, bold=True, color="#27ae60"))

    out.append(line(355, 165, 355, 365, color="#27ae60", sw=2))
    out.append(text(345, 265, "W", size=12, bold=True, anchor="end", color="#27ae60"))
    out.append(fitbox(215, 340, 280, 30, ["Носій досягає переходу і дає фотострум"], bg="#d5f5e3", stroke="#27ae60", size=11)[0])

    # Right diagram: L << W (Bad case)
    out.append(rect(430, 60, 350, 340, fill="#ffffff", stroke="#c0392b", sw=2, rx=6))
    out.append(text(605, 76, "Низький ККД: L << W (бруд / дефекти)", size=12, bold=True, anchor="middle", color="#c0392b"))

    out.append(rect(450, 110, 310, 30, fill="#d6eaf8", stroke="#2980b9"))
    out.append(text(605, 130, "n+ емітер (тонкий)", size=11, anchor="middle"))

    out.append(rect(450, 140, 310, 25, fill="#f9e79f", stroke="#f39c12"))
    out.append(text(605, 157, "p-n перехід (збіднена зона)", size=11, anchor="middle", bold=True))

    out.append(rect(450, 165, 310, 200, fill="#fadbd8", stroke="#c0392b"))
    out.append(text(605, 290, "p-база (з дефектами)", size=12, anchor="middle", color="#922b21"))

    for lx in [490, 605, 720]:
        out.append(line(lx, 94, lx, 108, color="#f1c40f", sw=2, dash="4 2"))
        out.append(arrow(lx, 94, lx, 108, color="#f39c12", sw=2))

    out.append(circle(605, 240, 6, fill="#f39c12"))
    out.append(text(620, 240, "hν → e⁻ + h⁺", size=11, bold=True, color="#e67e22"))

    out.append(line(605, 240, 605, 200, color="#c0392b", sw=2, dash="3 3"))
    out.append(circle(605, 200, 8, fill="#c0392b"))
    out.append(text(605, 204, "✕", size=10, color="#ffffff", anchor="middle"))
    out.append(text(500, 215, "Рекомбінація!", size=11, bold=True, color="#c0392b"))

    out.append(line(745, 200, 745, 240, color="#c0392b", sw=2))
    out.append(text(735, 220, "L", size=12, bold=True, anchor="end", color="#c0392b"))
    out.append(fitbox(605, 340, 280, 30, ["Носій вмирає в об'ємі, струм втрачено"], bg="#fadbd8", stroke="#c0392b", size=11)[0])

    out.append("</svg>")
    save_svg("solar-cell-collection.svg", "\n".join(out))


# 4. bjt-base-width.svg
def gen_bjt_base_width():
    w, h = 820, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 25, "Транспорт неосновних носіїв у базі біполярного транзистора", size=15, bold=True)[0])

    # Left: W_B << L_B (Working BJT)
    out.append(rect(40, 60, 350, 330, fill="#ffffff", stroke="#27ae60", sw=2, rx=6))
    out.append(text(215, 85, "Тонка база: W_B << L_B (α_T ≈ 1, β >> 1)", size=13, bold=True, anchor="middle", color="#27ae60"))

    out.append(rect(60, 110, 90, 200, fill="#d6eaf8", stroke="#2980b9"))
    out.append(text(105, 210, "Емітер n+", size=12, anchor="middle", bold=True))

    out.append(rect(150, 110, 60, 200, fill="#e8f8f5", stroke="#27ae60"))
    out.append(text(180, 140, "База p", size=12, anchor="middle", bold=True, color="#16a085"))
    out.append(text(180, 280, "W_B", size=12, anchor="middle", bold=True, color="#27ae60"))

    out.append(rect(210, 110, 160, 200, fill="#ebf5fb", stroke="#2980b9"))
    out.append(text(290, 210, "Колектор n", size=12, anchor="middle", bold=True))

    for y_p in [160, 190, 220, 250]:
        out.append(line(75, y_p, 290, y_p, color="#27ae60", sw=2))
        out.append(arrow(75, y_p, 290, y_p, color="#27ae60", sw=2))

    out.append(fitbox(215, 345, 320, 30, ["Майже всі електрони пролітають у колектор"], bg="#d5f5e3", stroke="#27ae60", size=11)[0])

    # Right: W_B >= L_B (Failed BJT)
    out.append(rect(430, 60, 350, 330, fill="#ffffff", stroke="#c0392b", sw=2, rx=6))
    out.append(text(605, 85, "Товста база: W_B ≥ L_B (транзистор не працює)", size=13, bold=True, anchor="middle", color="#c0392b"))

    out.append(rect(450, 110, 80, 200, fill="#d6eaf8", stroke="#2980b9"))
    out.append(text(490, 210, "Емітер n+", size=12, anchor="middle", bold=True))

    out.append(rect(530, 110, 150, 200, fill="#fadbd8", stroke="#c0392b"))
    out.append(text(605, 140, "Широка база p (W_B ≥ L_B)", size=12, anchor="middle", bold=True, color="#922b21"))

    out.append(rect(680, 110, 80, 200, fill="#ebf5fb", stroke="#2980b9"))
    out.append(text(720, 210, "Колектор n", size=12, anchor="middle", bold=True))

    for y_p, end_x in [(160, 630), (190, 610), (220, 640), (250, 600)]:
        out.append(line(460, y_p, end_x, y_p, color="#c0392b", sw=2, dash="3 3"))
        out.append(circle(end_x, y_p, 5, fill="#c0392b"))
        out.append(line(end_x, y_p, end_x, 290, color="#e67e22", sw=1.5))
        out.append(arrow(end_x, y_p, end_x, 290, color="#e67e22", sw=1.5))

    out.append(fitbox(605, 345, 320, 30, ["Носії рекомбінують у базі, струм колектора = 0"], bg="#fadbd8", stroke="#c0392b", size=11)[0])

    out.append("</svg>")
    save_svg("bjt-base-width.svg", "\n".join(out))


# 5. doping-defects-impact.svg
def gen_doping_defects_impact():
    w, h = 820, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(410, 25, "Залежність дифузійної довжини L від легування N та чистоти матеріалу", size=15, bold=True)[0])

    ox, oy = 110, 350
    pw, ph = 620, 250

    out.append(line(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    out.append(arrow(ox, oy, ox + pw + 30, oy, color=INK, sw=2))
    out.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))

    out.append(text(ox + pw - 10, oy + 35, "Концентрація легування N (см⁻³)", size=12, bold=True, anchor="end"))
    out.append(text(ox + 10, oy - ph - 15, "L (мкм, логарифмічна шкала)", size=12, bold=True, anchor="start"))

    xticks = [
        (ox + 50, "10¹⁴"), (ox + 180, "10¹⁵"), (ox + 310, "10¹⁶"), 
        (ox + 440, "10¹⁷"), (ox + 570, "10¹⁸")
    ]
    for xt, label in xticks:
        out.append(line(xt, oy, xt, oy + 6, color=INK, sw=1.5))
        out.append(text(xt, oy + 22, label, size=11, anchor="middle"))

    yticks = [
        (oy - 50, "1 мкм"), (oy - 120, "10 мкм"), (oy - 190, "100 мкм"), (oy - 240, "1000 мкм")
    ]
    for yt, label in yticks:
        out.append(line(ox - 6, yt, ox, yt, color=INK, sw=1.5))
        out.append(text(ox - 12, yt + 4, label, size=11, anchor="end"))
        out.append(line(ox, yt, ox + pw, yt, color="#eaeded", sw=1, dash="2 2"))

    pts_clean = []
    clean_data = [
        (ox + 50, oy - 240), (ox + 180, oy - 220), (ox + 310, oy - 180), 
        (ox + 440, oy - 120), (ox + 570, oy - 45)
    ]
    for x, y in clean_data:
        pts_clean.append(f"{x},{y}")

    out.append(polyline(" ".join(pts_clean), color="#27ae60", sw=3))
    out.append(text(ox + 360, oy - 215, "Очищений Si (мало пасток, високий τ)", size=11, bold=True, color="#27ae60"))

    pts_def = []
    def_data = [
        (ox + 50, oy - 140), (ox + 180, oy - 130), (ox + 310, oy - 105), 
        (ox + 440, oy - 70), (ox + 570, oy - 30)
    ]
    for x, y in def_data:
        pts_def.append(f"{x},{y}")

    out.append(polyline(" ".join(pts_def), color="#c0392b", sw=3, dash="6 3"))
    out.append(text(ox + 340, oy - 120, "Легований золотом Si (багато пасток SRH)", size=11, bold=True, color="#c0392b"))

    out.append(line(ox + 480, oy - 10, ox + 570, oy - 10, color="#95a5a6", sw=1))
    out.append(fitbox(ox + 470, oy - 40, 140, 45, ["Оже-рекомбінація", "і розсіяння домішок"], bg="#f2f4f4", stroke="#7f8c8d", size=10)[0])

    out.append("</svg>")
    save_svg("doping-defects-impact.svg", "\n".join(out))


if __name__ == "__main__":
    gen_carrier_injection_decay()
    gen_diffusion_vs_lifetime()
    gen_solar_cell_collection()
    gen_bjt_base_width()
    gen_doping_defects_impact()
