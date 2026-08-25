# -*- coding: utf-8 -*-
import sys
import os

# Four parent levels up to reach scripts/ folder from book/physics/mechanics/hydrodynamic-instability
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def save_svg(filename, content):
    filepath = os.path.join(IMG_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {filepath}")

def generate_kelvin_helmholtz():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Title / Headers
    out.append(textbox(380, 25, "Механізм нестійкості Кельвіна — Гельмгольца (зсувний потік)", size=15, bold=True)[0])
    
    # Upper layer (faster fluid)
    out.append(rect(40, 55, 680, 95, fill="#e8f0fe", stroke="#a0c0e8", sw=1))
    out.append(text(120, 80, "Верхній шар: швидкість U₁ (велика)", size=13, color=NEG, bold=True, anchor="start"))
    out.append(arrow(120, 105, 240, 105, color=NEG, sw=2.5))
    out.append(arrow(320, 105, 440, 105, color=NEG, sw=2.5))
    out.append(arrow(520, 105, 640, 105, color=NEG, sw=2.5))
    
    # Wavy Interface / Vortex roll-up path
    path_d = ("M 40,150 "
              "C 120,130 160,170 220,150 "
              "C 260,125 300,115 340,145 "
              "C 370,175 350,205 320,185 "
              "C 300,165 330,135 380,150 "
              "C 440,170 480,120 540,150 "
              "C 580,175 570,205 540,190 "
              "C 520,175 540,145 600,150 "
              "L 720,150")
    out.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="3"/>')
    
    # Lower layer (slower fluid)
    out.append(rect(40, 165, 680, 95, fill="#fef3e8", stroke="#e8c0a0", sw=1))
    out.append(text(120, 240, "Нижній шар: швидкість U₂ (мала)", size=13, color=POS, bold=True, anchor="start"))
    out.append(arrow(120, 215, 180, 215, color=POS, sw=2))
    out.append(arrow(320, 215, 380, 215, color=POS, sw=2))
    out.append(arrow(520, 215, 580, 215, color=POS, sw=2))

    # Pressure labels
    out.append(textbox(200, 125, "P низький (Бернуллі)", size=11, fill="#ffffff", stroke=NEG, pad=4)[0])
    out.append(textbox(200, 175, "P високий", size=11, fill="#ffffff", stroke=POS, pad=4)[0])
    out.append(textbox(450, 280, "Згортання зсувного шару у вихори", size=12, fill="#ffffff", stroke=LINE, pad=6, bold=True)[0])

    out.append('</svg>')
    save_svg("kelvin-helmholtz.svg", "".join(out))

def generate_rayleigh_taylor():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Еволюція нестійкості Релея — Тейлора (важка рідина над легкою)", size=14, bold=True)[0])
    
    # Stage 1: Initial perturbation
    out.append(rect(30, 50, 210, 220, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(135, 72, "1. Початкове збурення", size=12, bold=True))
    out.append(rect(35, 85, 200, 80, fill="#d0e0fc", stroke="none"))
    out.append(text(135, 120, "Важка рідина (ρ₁)", size=11, color=NEG, bold=True))
    out.append(rect(35, 175, 200, 85, fill="#fce0d0", stroke="none"))
    out.append(text(135, 220, "Легка рідина (ρ₂)", size=11, color=POS, bold=True))
    # Small wavy line interface
    out.append(f'<path d="M 35,170 Q 85,165 135,170 T 235,170" fill="none" stroke="{LINE}" stroke-width="2"/>')
    out.append(arrow(135, 90, 135, 110, color=LINE, sw=1.5))
    out.append(text(150, 102, "g", size=11, italic=True))

    # Stage 2: Linear / early non-linear
    out.append(rect(275, 50, 210, 220, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(380, 72, "2. Лінійне зростання", size=12, bold=True))
    # Draw background light fluid
    out.append(rect(280, 85, 200, 175, fill="#fce0d0", stroke="none"))
    # Wave fingers (heavy fluid on top) - bubble peak at 380, 150
    path_s2 = "M 280,85 L 480,85 L 480,170 Q 445,220 430,220 Q 415,220 380,160 Q 345,220 330,220 Q 315,220 280,170 Z"
    out.append(f'<path d="{path_s2}" fill="#d0e0fc" stroke="{LINE}" stroke-width="1.5"/>')
    out.append(text(380, 100, "Важка (ρ₁)", size=10, color=NEG, bold=True))
    out.append(textbox(330, 245, "Шпилька", size=10, fill="#ffffff", stroke=NEG, pad=3)[0])
    out.append(textbox(380, 185, "Бульбашка", size=10, fill="#ffffff", stroke=POS, pad=3)[0])

    # Stage 3: Fully non-linear mushroom caps
    out.append(rect(520, 50, 210, 220, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(625, 72, "3. Грибоподібні структури", size=12, bold=True))
    out.append(rect(525, 85, 200, 175, fill="#fce0d0", stroke="none"))
    # Mushroom shape
    path_s3 = ("M 525,85 L 725,85 L 725,170 "
               "C 710,210 690,240 675,230 "
               "C 660,150 665,110 650,110 "
               "C 635,110 585,130 575,170 "
               "C 565,210 570,240 550,240 "
               "C 520,240 545,220 525,170 Z")
    out.append(f'<path d="{path_s3}" fill="#d0e0fc" stroke="{LINE}" stroke-width="1.5"/>')
    out.append(text(625, 100, "Важка (ρ₁)", size=10, color=NEG, bold=True))
    out.append(textbox(625, 250, "Вторинні вихори", size=10, fill="#ffffff", stroke=LINE, pad=3)[0])

    out.append('</svg>')
    save_svg("rayleigh-taylor.svg", "".join(out))

def generate_rayleigh_benard():
    w, h = 760, 300
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Конвективна нестійкість Релея — Бенара (осередки конвекції)", size=14, bold=True)[0])
    
    # Top cold plate
    out.append(rect(60, 50, 640, 25, fill="#e8f0fe", stroke=NEG, sw=2))
    out.append(text(380, 67, "Верхня холодна стінка (T_cold)", size=12, color=NEG, bold=True))
    
    # Bottom hot plate
    out.append(rect(60, 225, 640, 25, fill="#fce0d0", stroke=POS, sw=2))
    out.append(text(380, 242, "Нижня гаряча стінка (T_hot)", size=12, color=POS, bold=True))
    
    # Fluid gap height label
    out.append(arrow(45, 75, 45, 225, color=LINE, sw=1.5))
    out.append(arrow(45, 225, 45, 75, color=LINE, sw=1.5))
    out.append(text(32, 153, "d", size=13, italic=True))
    
    # Convection rolls (circular arrows / paths)
    # Roll 1 (counter-clockwise)
    out.append(circle(180, 150, 55, fill="none", stroke=LINE, sw=2))
    out.append(arrow(235, 145, 235, 130, color=POS, sw=2.5))
    out.append(arrow(125, 155, 125, 170, color=NEG, sw=2.5))
    out.append(text(180, 150, "Осередок 1", size=11, bold=True))

    # Roll 2 (clockwise)
    out.append(circle(340, 150, 55, fill="none", stroke=LINE, sw=2))
    out.append(arrow(285, 135, 285, 120, color=POS, sw=2.5))
    out.append(arrow(395, 165, 395, 180, color=NEG, sw=2.5))
    out.append(text(340, 150, "Осередок 2", size=11, bold=True))

    # Roll 3 (counter-clockwise)
    out.append(circle(500, 150, 55, fill="none", stroke=LINE, sw=2))
    out.append(arrow(555, 145, 555, 130, color=POS, sw=2.5))
    out.append(arrow(445, 155, 445, 170, color=NEG, sw=2.5))
    out.append(text(500, 150, "Осередок 3", size=11, bold=True))

    # Thermal plume labels
    out.append(textbox(260, 205, "Теплий підйом", size=10, fill="#ffffff", stroke=POS, pad=3)[0])
    out.append(textbox(420, 95, "Холодне опускання", size=10, fill="#ffffff", stroke=NEG, pad=3)[0])
    
    out.append(textbox(640, 150, "Критичне число:\nRa_c ≈ 1708", size=11, fill="#ffffff", stroke=FIELD, pad=6, bold=True)[0])

    out.append('</svg>')
    save_svg("rayleigh-benard.svg", "".join(out))

def generate_orr_sommerfeld_spectrum():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Спектр власних значень рівняння Орра — Зоммерфельда", size=14, bold=True)[0])
    
    # Coordinate system (c_r vs c_i)
    ox, oy = 120, 220
    out.append(line(50, oy, 680, oy, color=LINE, sw=2)) # Real axis (c_r)
    out.append(arrow(50, oy, 690, oy, color=LINE, sw=2))
    out.append(text(685, oy - 10, "c_r (фазова швидкість)", size=11, anchor="end", bold=True))

    out.append(line(ox, 280, ox, 50, color=LINE, sw=2)) # Imaginary axis (c_i)
    out.append(arrow(ox, 280, ox, 40, color=LINE, sw=2))
    out.append(text(ox - 10, 42, "c_i (інкремент)", size=11, anchor="end", bold=True))

    # Neutral axis c_i = 0 label
    out.append(text(ox - 15, oy + 15, "0", size=10, color=MUTED))

    # Unstable region (c_i > 0)
    out.append(rect(ox + 1, 50, 560, oy - 51, fill="#fce0d0", stroke="none"))
    out.append(text(480, 75, "ЗОНА НЕСТІЙКОСТІ (c_i > 0)", size=11, color=POS, bold=True))

    # Stable region (c_i < 0)
    out.append(rect(ox + 1, oy + 1, 560, 55, fill="#e8f0fe", stroke="none"))
    out.append(text(480, 270, "ЗОНА СТІЙКОСТІ (c_i < 0)", size=11, color=NEG, bold=True))

    # Spectrum branches (P, A, S branches)
    # A-branch (wall modes)
    pts_A = [(200, 240), (250, 210), (300, 180), (350, 160), (400, 175), (450, 205)]
    for px, py in pts_A:
        if py < oy:
            out.append(circle(px, py, 6, fill=POS, stroke=LINE, sw=1.5))
        else:
            out.append(circle(px, py, 5, fill=NEG, stroke=LINE, sw=1.5))
            
    # Highlight the unstable mode (350, 160)
    out.append(circle(350, 160, 9, fill="none", stroke=POS, sw=2.5))
    out.append(textbox(350, 120, "Найнестійкіша мода!\n(c_i > 0)", size=11, fill="#ffffff", stroke=POS, pad=5, bold=True)[0])
    out.append(arrow(350, 138, 350, 149, color=POS, sw=1.5))

    # P-branch (center modes)
    pts_P = [(220, 250), (280, 245), (340, 242), (400, 240), (460, 245), (520, 250)]
    for px, py in pts_P:
        out.append(circle(px, py, 4, fill="#6c757d", stroke=LINE, sw=1))

    # S-branch
    pts_S = [(500, 230), (540, 215), (580, 225), (620, 240)]
    for px, py in pts_S:
        out.append(circle(px, py, 4, fill="#6c757d", stroke=LINE, sw=1))

    out.append(textbox(570, 170, "A-гілка (настінні моди)", size=10, fill="#ffffff", stroke=LINE, pad=3)[0])
    out.append(textbox(430, 290, "P-гілка (центральні)", size=10, fill="#ffffff", stroke=LINE, pad=3)[0])

    out.append('</svg>')
    save_svg("orr-sommerfeld-spectrum.svg", "".join(out))

if __name__ == "__main__":
    generate_kelvin_helmholtz()
    generate_rayleigh_taylor()
    generate_rayleigh_benard()
    generate_orr_sommerfeld_spectrum()
