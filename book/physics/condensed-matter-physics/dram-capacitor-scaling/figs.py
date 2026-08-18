# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Масштабування конденсатора DRAM"
(book/physics/condensed-matter-physics/dram-capacitor-scaling)
"""

import os
import sys

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
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2c3e50"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2980b9"/>
    </marker>
  </defs>'''

# 1. dram-capacitor-evolution.svg
def gen_dram_capacitor_evolution():
    w, h = 860, 480
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    # Main Title
    out.append(textbox(430, 15, "Еволюція тривимірної геометричної структури конденсатора DRAM", size=15, bold=True)[0])

    # Three Panels: Planar (1980s), Trench/Crown (1990s-2000s), Pillar MIM (Сучасність)
    # Panel 1: Planar
    p1_x = 30
    out.append(rect(p1_x, 50, 250, 390, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(p1_x + 125, 75, "1. Плоский конденсатор", size=13, bold=True, anchor="middle"))
    out.append(text(p1_x + 125, 95, "(1970–1980-ті, > 1 мкм)", size=11, color="#7f8c8d", anchor="middle"))

    # Substrate
    out.append(rect(p1_x + 20, 320, 210, 80, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    out.append(text(p1_x + 125, 360, "Кремнієва підкладка (Si)", size=11, color="#16a085", anchor="middle"))

    # Planar gate & dielectric
    out.append(rect(p1_x + 50, 305, 150, 15, fill="#fadbd8", stroke="#e74c3c", sw=1)) # dielectric SiO2
    out.append(rect(p1_x + 50, 275, 150, 30, fill="#ebf5fb", stroke="#2980b9", sw=1.5)) # Poly-Si Top electrode
    out.append(text(p1_x + 125, 293, "Електрод Poly-Si", size=11, color="#2980b9", anchor="middle"))

    # Aspect ratio label
    out.append(rect(p1_x + 35, 130, 180, 75, fill="#f4f6f7", stroke="#bdc3c7", sw=1, rx=4))
    out.append(text(p1_x + 125, 150, "Аспективне відношення:", size=11, bold=True, anchor="middle"))
    out.append(text(p1_x + 125, 170, "AR ≈ 1 : 1", size=14, bold=True, color="#c0392b", anchor="middle"))
    out.append(text(p1_x + 125, 190, "Діелектрик: SiO₂ (k ≈ 3.9)", size=10, color="#34495e", anchor="middle"))

    # Panel 2: Trench / Crown Stacked
    p2_x = 305
    out.append(rect(p2_x, 50, 250, 390, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(p2_x + 125, 75, "2. Відкрита корона (Crown)", size=13, bold=True, anchor="middle"))
    out.append(text(p2_x + 125, 95, "(1990–2000-ні, 130–90 нм)", size=11, color="#7f8c8d", anchor="middle"))

    # Substrate & Crown cup
    out.append(rect(p2_x + 20, 320, 210, 80, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    out.append(text(p2_x + 125, 360, "Кремнієва підкладка", size=11, color="#16a085", anchor="middle"))

    # Crown cup geometry
    # Bottom electrode (outer cup)
    out.append(polyline(f"{p2_x+70},220 {p2_x+70},320 {p2_x+180},320 {p2_x+180},220", color="#2980b9", sw=12, fill="none"))
    # Dielectric ONO layer inside cup
    out.append(polyline(f"{p2_x+76},215 {p2_x+76},314 {p2_x+174},314 {p2_x+174},215", color="#e74c3c", sw=4, fill="none"))
    # Top electrode filling interior
    out.append(rect(p2_x + 80, 210, 90, 100, fill="#ebf5fb", stroke="#2980b9", sw=1))
    out.append(text(p2_x + 125, 260, "Верхній Poly-Si", size=10, color="#2980b9", anchor="middle"))

    # Aspect ratio label
    out.append(rect(p2_x + 35, 130, 180, 75, fill="#f4f6f7", stroke="#bdc3c7", sw=1, rx=4))
    out.append(text(p2_x + 125, 150, "Аспективне відношення:", size=11, bold=True, anchor="middle"))
    out.append(text(p2_x + 125, 170, "AR ≈ 12 : 1", size=14, bold=True, color="#d35400", anchor="middle"))
    out.append(text(p2_x + 125, 190, "Діелектрик: ONO (k ≈ 5–6)", size=10, color="#34495e", anchor="middle"))

    # Panel 3: Ultra-High AR MIM Pillar (Modern)
    p3_x = 580
    out.append(rect(p3_x, 50, 250, 390, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(p3_x + 125, 75, "3. Циліндричний MIM-стовпчик", size=13, bold=True, anchor="middle"))
    out.append(text(p3_x + 125, 95, "(Сучасні вузли < 15 нм)", size=11, color="#7f8c8d", anchor="middle"))

    # Tall vertical pillar structure
    pillar_x = p3_x + 105
    # Outer electrode TiN
    out.append(rect(pillar_x - 30, 200, 90, 180, fill="#ebf5fb", stroke="#2c3e50", sw=1.5))
    # High-k dielectric ZAZ
    out.append(rect(pillar_x - 18, 200, 66, 180, fill="#fadbd8", stroke="#e74c3c", sw=1))
    # Inner metal electrode TiN
    out.append(rect(pillar_x - 10, 200, 50, 180, fill="#34495e", stroke="#2c3e50", sw=1))
    out.append(text(pillar_x + 15, 290, "TiN", size=11, bold=True, color="#ffffff", anchor="middle"))

    # Height & Width indicators
    out.append(line(pillar_x - 45, 200, pillar_x - 45, 380, color="#95a5a6", sw=1.5))
    out.append(arrow(pillar_x - 45, 250, pillar_x - 45, 200, color="#95a5a6"))
    out.append(arrow(pillar_x - 45, 330, pillar_x - 45, 380, color="#95a5a6"))
    out.append(text(pillar_x - 55, 290, "h > 1.5 мкм", size=10, bold=True, color="#7f8c8d", anchor="middle"))

    # Aspect ratio label
    out.append(rect(p3_x + 35, 130, 180, 65, fill="#f4f6f7", stroke="#bdc3c7", sw=1, rx=4))
    out.append(text(p3_x + 125, 148, "Аспективне відношення:", size=11, bold=True, anchor="middle"))
    out.append(text(p3_x + 125, 168, "AR > 45 : 1", size=14, bold=True, color="#27ae60", anchor="middle"))
    out.append(text(p3_x + 125, 185, "Діелектрик: ZAZ (k ≈ 35)", size=10, color="#34495e", anchor="middle"))

    # Bottom Substrate
    out.append(rect(p3_x + 20, 380, 210, 20, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    out.append(text(p3_x + 125, 394, "Кремнієва пластина", size=10, color="#16a085", anchor="middle"))

    out.append("</svg>")
    save_svg("dram-capacitor-evolution.svg", "\n".join(out))

# 2. band-diagram-mim-zaz.svg
def gen_band_diagram_mim_zaz():
    w, h = 860, 460
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(textbox(430, 15, "Зонна діаграма MIM-структури TiN / ZrO₂ / Al₂O₃ / ZrO₂ / TiN під напругою", size=15, bold=True)[0])

    ox, oy = 80, 380
    
    # Metal 1 (Bottom Electrode TiN)
    out.append(rect(ox, oy - 260, 120, 260, fill="#eaeded", stroke="#7f8c8d", sw=1.5))
    out.append(text(ox + 60, oy - 230, "Низький електрод", size=11, bold=True, anchor="middle"))
    out.append(text(ox + 60, oy - 210, "TiN (метал 1)", size=12, bold=True, color="#2c3e50", anchor="middle"))
    # Fermi level E_F1
    out.append(line(ox, oy - 140, ox + 120, oy - 140, color="#2980b9", sw=2, dash="4 4"))
    out.append(text(ox + 60, oy - 148, "E_F1", size=11, bold=True, color="#2980b9", anchor="middle"))

    # Dielectric ZAZ region: ZrO2 (1) | Al2O3 | ZrO2 (2)
    # ZrO2 (1)
    d1_x = ox + 120
    out.append(rect(d1_x, oy - 260, 150, 260, fill="#fef9e7", stroke="none"))
    # Al2O3 thin barrier
    d2_x = d1_x + 150
    out.append(rect(d2_x, oy - 260, 40, 260, fill="#fadbd8", stroke="none"))
    # ZrO2 (2)
    d3_x = d2_x + 40
    out.append(rect(d3_x, oy - 260, 150, 260, fill="#fef9e7", stroke="none"))

    # Labels for dielectric layers
    out.append(text(d1_x + 75, oy - 245, "ZrO₂ (k ≈ 35)", size=11, bold=True, color="#d35400", anchor="middle"))
    out.append(text(d2_x + 20, oy - 245, "Al₂O₃", size=10, bold=True, color="#c0392b", anchor="middle"))
    out.append(text(d3_x + 75, oy - 245, "ZrO₂ (k ≈ 35)", size=11, bold=True, color="#d35400", anchor="middle"))

    # Metal 2 (Top Electrode TiN)
    m2_x = d3_x + 150
    out.append(rect(m2_x, oy - 260, 120, 260, fill="#eaeded", stroke="#7f8c8d", sw=1.5))
    out.append(text(m2_x + 60, oy - 230, "Верхній електрод", size=11, bold=True, anchor="middle"))
    out.append(text(m2_x + 60, oy - 210, "TiN (метал 2)", size=12, bold=True, color="#2c3e50", anchor="middle"))
    # Fermi level E_F2 (shifted by voltage V)
    out.append(line(m2_x, oy - 60, m2_x + 120, oy - 60, color="#2980b9", sw=2, dash="4 4"))
    out.append(text(m2_x + 60, oy - 68, "E_F2 (E_F1 - e·V)", size=11, bold=True, color="#2980b9", anchor="middle"))

    # Conduction band edge E_c profile under electric field bias
    # ZrO1 conduction edge sloped from oy - 210 down to oy - 150
    # Al2O3 central barrier spikes up by 1.4 eV higher!
    # ZrO2 second layer sloped from oy - 180 down to oy - 110
    ec_path = f"M {d1_x} {oy - 210} L {d1_x + 150} {oy - 150} L {d1_x + 150} {oy - 230} L {d2_x + 40} {oy - 220} L {d2_x + 40} {oy - 140} L {d3_x + 150} {oy - 90}"
    out.append(f'<path d="{ec_path}" fill="none" stroke="#e67e22" stroke-width="3"/>')
    out.append(text(d1_x + 30, oy - 225, "E_c (ZrO₂)", size=11, bold=True, color="#e67e22"))

    # Barrier height offset Delta E_c label placed cleanly outside lines
    out.append(line(ox + 120, oy - 140, ox + 120, oy - 210, color="#7f8c8d", sw=1.5, dash="2 2"))
    out.append(text(ox + 60, oy - 175, "ΔE_c ≈ 1.4 еВ", size=10, bold=True, color="#7f8c8d", anchor="middle"))

    # Leakage Mechanisms Annotations
    # 1. Direct / FN Tunneling arrow through Al2O3 spike
    out.append(line(d1_x + 100, oy - 130, d3_x + 50, oy - 130, color="#c0392b", sw=2))
    out.append(arrow(d1_x + 100, oy - 130, d3_x + 50, oy - 130, color="#c0392b"))
    out.append(text(d1_x + 175, oy - 115, "1. Пряме тунелювання (DT)", size=10, bold=True, color="#c0392b", anchor="middle"))

    # 2. Poole-Frenkel emission via trap state
    trap_x, trap_y = d1_x + 80, oy - 160
    out.append(circle(trap_x, trap_y, 4, fill="#f1c40f", stroke="#d35400", sw=1.5))
    out.append(line(trap_x, trap_y, trap_x + 50, oy - 140, color="#d35400", sw=2, dash="3 3"))
    out.append(arrow(trap_x, trap_y, trap_x + 50, oy - 140, color="#d35400"))
    out.append(text(d1_x + 80, oy - 135, "2. Емісія Пула — Френкеля", size=10, bold=True, color="#d35400", anchor="middle"))

    # 3. Schottky Emission over barrier
    out.append(line(ox + 110, oy - 140, ox + 135, oy - 215, color="#27ae60", sw=2))
    out.append(arrow(ox + 110, oy - 140, ox + 135, oy - 215, color="#27ae60"))
    out.append(text(ox + 60, oy - 110, "3. Емісія Шотткі", size=10, bold=True, color="#27ae60", anchor="middle"))

    out.append("</svg>")
    save_svg("band-diagram-mim-zaz.svg", "\n".join(out))

if __name__ == "__main__":
    gen_dram_capacitor_evolution()
    gen_band_diagram_mim_zaz()
