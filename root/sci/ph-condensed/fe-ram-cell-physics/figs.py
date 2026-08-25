# -*- coding: utf-8 -*-
"""
Генератор SVG-ілюстрацій для теми "Фізика FeRAM комірки (1T1C FeRAM)"
(book/physics/condensed-matter-physics/fe-ram-cell-physics)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

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

def svg_arrow(x1, y1, x2, y2, color="#2c3e50", sw=1.5, marker="url(#arrow)"):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw:.1f}" marker-end="{marker}"/>'

def polyline(pts_str, color="#333333", sw=1.5, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'

# 1. feram-1t1c-schematic.svg
def gen_feram_1t1c_schematic():
    w, h = 880, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(text(440, 25, "Схема комірки 1T1C FeRAM та часові діаграми руйнівного зчитування", size=15, bold=True, anchor="middle"))

    # Left Panel: Schematic (x: 20..420)
    out.append(rect(20, 50, 400, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(220, 75, "Схемотехніка комірки 1T1C", size=13, bold=True, anchor="middle"))

    # Bitline (BL) - vertical line
    out.append(line(65, 115, 65, 360, color="#2980b9", sw=3))
    out.append(text(65, 98, "Bitline (BL)", size=10, color="#2980b9", bold=True, anchor="middle"))

    # Access Transistor (NMOS)
    out.append(line(65, 200, 130, 200, color="#2980b9", sw=2))
    out.append(rect(130, 170, 45, 60, fill="#e8f8f5", stroke="#16a085", sw=2))
    out.append(text(152, 204, "NMOS", size=11, color="#16a085", bold=True, anchor="middle"))

    # Wordline (WL) - horizontal line to Gate
    out.append(line(152, 115, 152, 170, color="#d35400", sw=3))
    out.append(text(205, 98, "Wordline (WL)", size=10, color="#d35400", bold=True, anchor="middle"))

    # Line from transistor to Capacitor
    out.append(line(175, 200, 235, 200, color="#2c3e50", sw=2))

    # Ferroelectric Capacitor (C_fe)
    out.append(line(235, 170, 235, 230, color="#2c3e50", sw=4))
    out.append(rect(239, 170, 12, 60, fill="#f9e79f", stroke="#f39c12", sw=1.5))
    out.append(line(255, 170, 255, 230, color="#2c3e50", sw=4))
    out.append(text(245, 258, "C_fe (HfO₂ / PZT)", size=10, color="#d68910", bold=True, anchor="middle"))

    out.append(svg_arrow(245, 215, 245, 185, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(text(245, 153, "Pᵣ (±)", size=10, color="#c0392b", bold=True, anchor="middle"))

    # Plateline (PL)
    out.append(line(255, 200, 390, 200, color="#8e44ad", sw=3))
    out.append(text(340, 186, "Plateline (PL)", size=10, color="#8e44ad", bold=True, anchor="middle"))

    # Sense Amplifier box at BL bottom
    out.append(rect(25, 360, 130, 45, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=4))
    out.append(text(90, 386, "Sense Amp", size=10, color="#2980b9", bold=True, anchor="middle"))

    # Right Panel: Waveforms (x: 440..860)
    out.append(rect(440, 50, 420, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(650, 75, "Часова діаграма зчитування та відновлення", size=13, bold=True, anchor="middle"))

    # Time axis
    out.append(svg_arrow(480, 380, 830, 380, color="#2c3e50", sw=1.5, marker="url(#arrow)"))
    out.append(text(830, 398, "Час (t)", size=10, anchor="middle"))

    out.append(text(460, 122, "WL", size=10, color="#d35400", bold=True, anchor="middle"))
    out.append(polyline("480,130 510,130 520,100 770,100 780,130 820,130", color="#d35400", sw=2))

    out.append(text(460, 182, "PL", size=10, color="#8e44ad", bold=True, anchor="middle"))
    out.append(polyline("480,190 540,190 550,150 670,150 680,190 820,190", color="#8e44ad", sw=2))

    out.append(text(460, 262, "BL", size=10, color="#2c3e50", bold=True, anchor="middle"))
    out.append(line(480, 280, 820, 280, color="#bdc3c7", sw=1, dash="4,4"))

    out.append(polyline("480,280 550,280 570,230 670,230 680,210 770,210 780,280 820,280", color="#c0392b", sw=2.5))
    out.append(text(620, 222, "Стан «1» (Q_total)", size=10, color="#c0392b", bold=True, anchor="middle"))

    out.append(polyline("480,280 550,280 570,265 670,265 680,280 820,280", color="#2980b9", sw=2, dash="5,3"))
    out.append(text(620, 257, "Стан «0» (Q_nsw)", size=10, color="#2980b9", bold=True, anchor="middle"))

    out.append(line(675, 90, 675, 380, color="#27ae60", sw=1.5, dash="3,3"))
    out.append(text(675, 342, "Строб Sense Amp", size=10, color="#27ae60", bold=True, anchor="middle"))
    out.append(text(735, 307, "Відновлення «1»", size=10, color="#8e44ad", bold=True, anchor="middle"))

    save_svg("feram-1t1c-schematic.svg", "\n".join(out) + "\n</svg>")

# 2. hysteresis-qsw-diagram.svg
def gen_hysteresis_qsw_diagram():
    w, h = 880, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(text(440, 25, "Петля гістерезису P-E та виділення заряду переключення Q_sw", size=15, bold=True, anchor="middle"))

    # Left Panel: P-E Hysteresis Loop (x: 20..420)
    out.append(rect(20, 50, 400, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(220, 75, "Петля гістерезису P-E", size=13, bold=True, anchor="middle"))

    cx, cy = 220, 235
    out.append(svg_arrow(50, cy, 390, cy, color="#2c3e50", sw=1.5, marker="url(#arrow)"))
    out.append(svg_arrow(cx, 390, cx, 95, color="#2c3e50", sw=1.5, marker="url(#arrow)"))
    out.append(text(375, cy + 20, "Поле (E)", size=10, anchor="middle"))
    out.append(text(cx - 35, 105, "Поляризація (P)", size=10, anchor="middle"))

    path_d = f"M 90,{cy+90} C 120,{cy+90} 160,{cy+90} {cx-40},{cy+70} C {cx},{cy+50} {cx+50},{cy+30} 340,{cy-90} C 360,{cy-90} 370,{cy-90} 370,{cy-90} C 340,{cy-90} 280,{cy-90} {cx+40},{cy-70} C {cx},{cy-50} {cx-50},{cy-30} 100,{cy+90} Z"
    out.append(f'<path d="{path_d}" fill="none" stroke="#2c3e50" stroke-width="2.5"/>')

    out.append(circle(cx, cy - 65, 5, fill="#2980b9"))
    out.append(text(cx + 65, cy - 61, "+Pᵣ (Стан «0»)", size=10, bold=True, color="#2980b9", anchor="middle"))

    out.append(circle(cx, cy + 65, 5, fill="#c0392b"))
    out.append(text(cx - 65, cy + 69, "-Pᵣ (Стан «1»)", size=10, bold=True, color="#c0392b", anchor="middle"))

    out.append(circle(cx + 68, cy, 4, fill="#27ae60"))
    out.append(text(cx + 70, cy + 20, "+E_c", size=10, color="#27ae60", bold=True, anchor="middle"))
    out.append(circle(cx - 68, cy, 4, fill="#27ae60"))
    out.append(text(cx - 70, cy - 18, "-E_c", size=10, color="#27ae60", bold=True, anchor="middle"))

    out.append(svg_arrow(cx + 10, cy + 60, 320, cy - 80, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(text(315, cy + 48, "Перемикання «1»", size=10, color="#c0392b", bold=True, anchor="middle"))

    # Right Panel: Q_sw Breakdown (x: 440..860)
    out.append(rect(440, 50, 420, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(650, 75, "Компоненти заряду зчитування Q", size=13, bold=True, anchor="middle"))

    b1_x = 505
    out.append(rect(b1_x, 170, 95, 190, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=4))
    out.append(text(b1_x + 47, 265, "Q_nsw (C_lin · V)", size=10, color="#2980b9", bold=True, anchor="middle"))
    out.append(text(b1_x + 47, 380, "Зчитування «0»", size=11, bold=True, anchor="middle"))

    b2_x = 730
    out.append(rect(b2_x, 280, 105, 80, fill="#ebf5fb", stroke="#2980b9", sw=2))
    out.append(text(b2_x + 52, 320, "Q_nsw", size=10, color="#2980b9", anchor="middle"))
    out.append(rect(b2_x, 110, 105, 170, fill="#fadbd8", stroke="#c0392b", sw=2))
    out.append(text(b2_x + 52, 195, "Q_sw = 2·Pᵣ·A_cap", size=10, color="#c0392b", bold=True, anchor="middle"))
    out.append(text(b2_x + 52, 380, "Зчитування «1»", size=11, bold=True, anchor="middle"))

    out.append(line(610, 110, 720, 110, color="#c0392b", sw=1, dash="3,3"))
    out.append(line(610, 280, 720, 280, color="#c0392b", sw=1, dash="3,3"))
    out.append(svg_arrow(665, 195, 665, 110, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(svg_arrow(665, 195, 665, 280, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(text(665, 198, "ΔQ = Q_sw", size=10, color="#c0392b", bold=True, anchor="middle"))

    save_svg("hysteresis-qsw-diagram.svg", "\n".join(out) + "\n</svg>")

# 3. pzt-vs-hfo2-crystal.svg
def gen_pzt_vs_hfo2_crystal():
    w, h = 880, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(text(440, 25, "Кристалографічні структури сегнетоелектричних PZT та HfO₂ (Pca2₁)", size=15, bold=True, anchor="middle"))

    # Left Panel: PZT Perovskite (x: 20..420)
    out.append(rect(20, 50, 400, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(220, 75, "Перовськіт PZT (Pb[Zr,Ti]O₃)", size=13, bold=True, anchor="middle"))

    cx, cy = 200, 240
    s = 90
    out.append(rect(cx - s/2 + 25, cy - s/2 - 25, s, s, fill="none", stroke="#bdc3c7", sw=1.5, rx=0))
    out.append(rect(cx - s/2 - 15, cy - s/2 + 15, s, s, fill="none", stroke="#2c3e50", sw=2, rx=0))
    out.append(line(cx - s/2 + 25, cy - s/2 - 25, cx - s/2 - 15, cy - s/2 + 15, color="#2c3e50", sw=1.5))
    out.append(line(cx + s/2 + 25, cy - s/2 - 25, cx + s/2 - 15, cy - s/2 + 15, color="#2c3e50", sw=1.5))
    out.append(line(cx - s/2 + 25, cy + s/2 - 25, cx - s/2 - 15, cy + s/2 + 15, color="#2c3e50", sw=1.5))
    out.append(line(cx + s/2 + 25, cy + s/2 - 25, cx + s/2 - 15, cy + s/2 + 15, color="#2c3e50", sw=1.5))

    for dx in [-15, 25]:
        for dy in [15, -25]:
            out.append(circle(cx - s/2 + dx, cy - s/2 + dy, 7, fill="#7f8c8d", stroke="#2c3e50", sw=1))
            out.append(circle(cx + s/2 + dx, cy - s/2 + dy, 7, fill="#7f8c8d", stroke="#2c3e50", sw=1))
            out.append(circle(cx - s/2 + dx, cy + s/2 + dy, 7, fill="#7f8c8d", stroke="#2c3e50", sw=1))
            out.append(circle(cx + s/2 + dx, cy + s/2 + dy, 7, fill="#7f8c8d", stroke="#2c3e50", sw=1))

    out.append(circle(cx + 5, cy - s/2 - 5, 6, fill="#e74c3c"))
    out.append(circle(cx + 5, cy + s/2 - 5, 6, fill="#e74c3c"))
    out.append(circle(cx - s/2 + 5, cy - 5, 6, fill="#e74c3c"))
    out.append(circle(cx + s/2 + 5, cy - 5, 6, fill="#e74c3c"))

    out.append(circle(cx + 5, cy - 25, 9, fill="#3498db", stroke="#2980b9", sw=2))
    out.append(svg_arrow(cx + 5, cy - 5, cx + 5, cy - 25, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(text(cx + 95, cy - 21, "Зсув Ti⁴⁺ / Zr⁴⁺", size=10, color="#c0392b", bold=True, anchor="middle"))

    out.append(text(220, 380, "Pb²⁺ (сірий) • O²⁻ (червоний) • Ti⁴⁺/Zr⁴⁺ (синій)", size=10, anchor="middle"))

    # Right Panel: Orthorhombic HfO2 Pca2_1 (x: 440..860)
    out.append(rect(440, 50, 420, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(650, 75, "Орторомбічна фаза Pca2₁ HfO₂", size=13, bold=True, anchor="middle"))

    hx, hy = 580, 230
    out.append(rect(hx - 70, hy - 70, 140, 140, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=4))

    out.append(circle(hx - 45, hy - 40, 11, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    out.append(text(hx - 45, hy - 36, "Hf", size=9, color="#ffffff", bold=True))

    out.append(circle(hx + 45, hy - 40, 11, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    out.append(text(hx + 45, hy - 36, "Hf", size=9, color="#ffffff", bold=True))

    out.append(circle(hx - 45, hy + 40, 11, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    out.append(text(hx - 45, hy + 44, "Hf", size=9, color="#ffffff", bold=True))

    out.append(circle(hx + 45, hy + 40, 11, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    out.append(text(hx + 45, hy + 44, "Hf", size=9, color="#ffffff", bold=True))

    out.append(circle(hx, hy - 25, 8, fill="#e74c3c", stroke="#922b21", sw=1.5))
    out.append(svg_arrow(hx, hy, hx, hy - 25, color="#c0392b", sw=2, marker="url(#arrow-red)"))

    out.append(circle(hx, hy + 15, 8, fill="#e74c3c", stroke="#922b21", sw=1.5))
    out.append(svg_arrow(hx, hy + 35, hx, hy + 15, color="#c0392b", sw=2, marker="url(#arrow-red)"))

    out.append(text(hx + 155, hy + 4, "Зсув O²⁻ вздовж c-осі", size=10, color="#c0392b", bold=True, anchor="middle"))
    out.append(text(650, 380, "Hf⁴⁺ (синій) • Зміщені іони O²⁻ (червоний)", size=10, anchor="middle"))

    save_svg("pzt-vs-hfo2-crystal.svg", "\n".join(out) + "\n</svg>")

# 4. degradation-mechanisms.svg
def gen_degradation_mechanisms():
    w, h = 880, 440
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           make_defs()]

    out.append(text(440, 25, "Фізичні механізми деградації: втома (Fatigue) та вкарбування (Imprint)", size=15, bold=True, anchor="middle"))

    # Left Panel: Fatigue Mechanism (x: 20..420)
    out.append(rect(20, 50, 400, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(220, 75, "(А) Втома: пінінг доменних стінок", size=13, bold=True, anchor="middle"))

    out.append(rect(50, 100, 340, 35, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5, rx=0))
    out.append(text(220, 121, "Верхній електрод (TiN)", size=10, bold=True, anchor="middle"))

    out.append(rect(50, 135, 340, 160, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=0))

    out.append(rect(50, 295, 340, 35, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5, rx=0))
    out.append(text(220, 316, "Нижній електрод (TiN / IrO₂)", size=10, bold=True, anchor="middle"))

    for x_pos in [80, 130, 180, 240, 300, 350]:
        out.append(circle(x_pos, 152, 7.5, fill="#e67e22"))
        out.append(text(x_pos, 155, "v", size=9, color="#ffffff", bold=True))

        out.append(circle(x_pos - 15, 278, 7.5, fill="#e67e22"))
        out.append(text(x_pos - 15, 281, "v", size=9, color="#ffffff", bold=True))

    out.append(line(190, 135, 190, 295, color="#c0392b", sw=2, dash="4,4"))
    out.append(text(190, 219, "Зафіксована доменна стінка", size=10, color="#c0392b", bold=True, anchor="middle"))

    out.append(text(220, 380, "Накопичення вакансій оксигену V_O²⁺ блокує домени", size=10, anchor="middle"))

    # Right Panel: Imprint Mechanism (x: 440..860)
    out.append(rect(440, 50, 420, 370, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(650, 75, "(Б) Вкарбування: зсув петлі V_shift", size=13, bold=True, anchor="middle"))

    cx, cy = 650, 235
    out.append(svg_arrow(470, cy, 830, cy, color="#2c3e50", sw=1.5, marker="url(#arrow)"))
    out.append(svg_arrow(cx, 390, cx, 100, color="#2c3e50", sw=1.5, marker="url(#arrow)"))
    out.append(text(820, cy + 20, "V", size=10, anchor="middle"))
    out.append(text(cx - 25, 110, "P", size=10, anchor="middle"))

    path_normal = f"M 560,{cy+60} C 590,{cy+60} 620,{cy+50} {cx-20},{cy+40} C {cx},{cy+30} {cx+30},{cy+20} 740,{cy-60} C 750,{cy-60} 750,{cy-60} 750,{cy-60} C 720,{cy-60} 680,{cy-50} {cx+20},{cy-40} C {cx},{cy-30} {cx-30},{cy-20} 570,{cy+60} Z"
    out.append(f'<path d="{path_normal}" fill="none" stroke="#2980b9" stroke-width="1.5" stroke-dasharray="4,4"/>')

    shift = 45
    path_shifted = f"M {560+shift},{cy+60} C {590+shift},{cy+60} {620+shift},{cy+50} {cx-20+shift},{cy+40} C {cx+shift},{cy+30} {cx+30+shift},{cy+20} {740+shift},{cy-60} C {750+shift},{cy-60} {750+shift},{cy-60} {750+shift},{cy-60} C {720+shift},{cy-60} {680+shift},{cy-50} {cx+20+shift},{cy-40} C {cx}+{shift},{cy-30} {cx-30+shift},{cy-20} {570+shift},{cy+60} Z"
    out.append(f'<path d="{path_shifted}" fill="none" stroke="#c0392b" stroke-width="2.5"/>')

    out.append(svg_arrow(cx, cy + 80, cx + shift, cy + 80, color="#c0392b", sw=2, marker="url(#arrow-red)"))
    out.append(text(cx + shift/2, cy + 104, "V_shift (Імпринт)", size=10, color="#c0392b", bold=True, anchor="middle"))

    out.append(text(650, 380, "Зсув коерцитивної напруги викликає помилку зчитування", size=10, anchor="middle"))

    save_svg("degradation-mechanisms.svg", "\n".join(out) + "\n</svg>")

if __name__ == "__main__":
    gen_feram_1t1c_schematic()
    gen_hysteresis_qsw_diagram()
    gen_pzt_vs_hfo2_crystal()
    gen_degradation_mechanisms()
