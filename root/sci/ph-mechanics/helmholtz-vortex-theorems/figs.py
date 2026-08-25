# -*- coding: utf-8 -*-
import sys
import os

# Four parent levels up to reach scripts/ folder from book/physics/mechanics/helmholtz-vortex-theorems
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def generate_vortex_tube():
    w, h = 760, 340
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Геометрія вихорової трубки та збереження інтенсивності Г1 = Г2", size=14, bold=True)[0])
    
    # Outer tube envelope (curved 3D-like cylinder)
    path_top = "M 120,120 Q 300,80 520,130 Q 620,150 680,160"
    path_bot = "M 120,240 Q 300,200 520,230 Q 620,245 680,240"
    
    # Fill tube body
    path_fill = ("M 120,120 Q 300,80 520,130 Q 620,150 680,160 "
                 "L 680,240 Q 620,245 520,230 Q 300,200 120,240 Z")
    out.append(f'<path d="{path_fill}" fill="#e8f0fe" stroke="none" opacity="0.7"/>')
    out.append(f'<path d="{path_top}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    out.append(f'<path d="{path_bot}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    
    # Vortex lines inside the tube
    out.append(f'<path d="M 120,160 Q 300,120 520,165 Q 620,185 680,190" fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="6,4"/>')
    out.append(f'<path d="M 120,200 Q 300,160 520,195 Q 620,215 680,215" fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="6,4"/>')
    
    # Arrows on central vortex line
    out.append(arrow(320, 142, 360, 145, color=POS, sw=2))
    out.append(arrow(580, 191, 610, 195, color=POS, sw=2))
    out.append(text(375, 133, "ω (вихореність)", size=11, color=POS, bold=True, italic=True))
    
    # Cross-section S1 (ellipse at left end)
    out.append(f'<ellipse cx="120" cy="180" rx="20" ry="60" fill="#d0e0fc" stroke="{LINE}" stroke-width="2"/>')
    out.append(arrow(120, 180, 70, 180, color=LINE, sw=2))
    out.append(text(55, 175, "n₁", size=12, bold=True, italic=True))
    out.append(textbox(120, 275, "Переріз S₁\nГ₁ = ∬ ω·n₁ dS", size=11, fill="#ffffff", stroke=NEG, pad=5, bold=True)[0])
    
    # Intermediate Cross-section S2 (smaller ellipse in middle-right)
    out.append(f'<ellipse cx="520" cy="180" rx="15" ry="50" fill="#fce0d0" stroke="{LINE}" stroke-width="2"/>')
    out.append(arrow(520, 180, 565, 183, color=LINE, sw=2))
    out.append(text(575, 178, "n₂", size=12, bold=True, italic=True))
    out.append(textbox(520, 275, "Переріз S₂\nГ₂ = ∬ ω·n₂ dS", size=11, fill="#ffffff", stroke=POS, pad=5, bold=True)[0])
    
    # Relation box
    out.append(textbox(330, 275, "Теорема 2:\nГ₁ = Г₂ = const", size=12, fill="#ffffff", stroke=FIELD, pad=6, bold=True)[0])
    
    # Closed surface annotation (Gauss theorem context)
    out.append(textbox(340, 75, "Поверхня трубки: ω · n = 0 (немає потоку через бічну поверхню)", size=11, fill="#ffffff", stroke=LINE, pad=5)[0])

    out.append('</svg>')
    render(os.path.join(IMG_DIR, "helmholtz-vortex-tube.svg"), w, h, "".join(out))
    print("Saved helmholtz-vortex-tube.svg")

def generate_vortex_stretching():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Механізм розтягнення вихорових трубок (Vortex Stretching)", size=14, bold=True)[0])
    
    # Initial state (short, thick cylinder)
    out.append(rect(40, 50, 300, 240, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(190, 75, "Стан 1: Короткий товстий вихор", size=12, bold=True))
    
    # Cylinder 1
    out.append(f'<ellipse cx="190" cy="120" rx="60" ry="20" fill="#d0e0fc" stroke="{NEG}" stroke-width="2"/>')
    out.append(rect(130, 120, 120, 100, fill="#e8f0fe", stroke="none"))
    out.append(line(130, 120, 130, 220, color=NEG, sw=2))
    out.append(line(250, 120, 250, 220, color=NEG, sw=2))
    out.append(f'<ellipse cx="190" cy="220" rx="60" ry="20" fill="#d0e0fc" stroke="{NEG}" stroke-width="2"/>')
    
    # Vorticity vector 1
    out.append(arrow(190, 220, 190, 100, color=POS, sw=2.5))
    out.append(text(205, 140, "ω₀", size=13, color=POS, bold=True, italic=True))
    
    # Parameters 1
    out.append(textbox(190, 260, "Площа S₀, Довжина L₀\nВихореність ω₀", size=11, fill="#ffffff", stroke=NEG, pad=4)[0])
    
    # Transition arrow (stretching process)
    out.append(arrow(350, 170, 410, 170, color=LINE, sw=3))
    out.append(text(380, 145, "Розтягнення", size=11, bold=True))
    out.append(text(380, 195, "L₁ > L₀\nS₁ < S₀", size=10, color=MUTED))
    
    # Final state (long, thin cylinder)
    out.append(rect(420, 50, 300, 240, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(570, 75, "Стан 2: Розтягнутий тонкий вихор", size=12, bold=True))
    
    # Cylinder 2
    out.append(f'<ellipse cx="570" cy="100" rx="25" ry="10" fill="#fce0d0" stroke="{POS}" stroke-width="2"/>')
    out.append(rect(545, 100, 50, 140, fill="#fef3e8", stroke="none"))
    out.append(line(545, 100, 545, 240, color=POS, sw=2))
    out.append(line(595, 100, 595, 240, color=POS, sw=2))
    out.append(f'<ellipse cx="570" cy="240" rx="25" ry="10" fill="#fce0d0" stroke="{POS}" stroke-width="2"/>')
    
    # Vorticity vector 2 (much longer)
    out.append(arrow(570, 240, 570, 70, color=POS, sw=3.5))
    out.append(text(585, 120, "ω₁ ≫ ω₀", size=13, color=POS, bold=True, italic=True))
    
    # Parameters 2
    out.append(textbox(570, 265, "Г = ω₀·S₀ = ω₁·S₁ = const\nОбертання прискорюється!", size=10, fill="#ffffff", stroke=POS, pad=4, bold=True)[0])

    out.append('</svg>')
    render(os.path.join(IMG_DIR, "helmholtz-vortex-stretching.svg"), w, h, "".join(out))
    print("Saved helmholtz-vortex-stretching.svg")

def generate_kelvin_circulation():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Теорема Кельвіна: збереження циркуляції вздовж рідкого контуру C(t)", size=14, bold=True)[0])
    
    # Time t contour C(t)
    out.append(rect(40, 50, 310, 240, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(195, 75, "Момент часу t: Контур C(t)", size=12, bold=True))
    
    # Closed contour 1
    path_c1 = ("M 120,160 "
               "C 140,110 220,110 260,150 "
               "C 280,180 250,230 190,220 "
               "C 130,210 100,190 120,160 Z")
    out.append(f'<path d="{path_c1}" fill="#e8f0fe" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(arrow(210, 115, 230, 125, color=NEG, sw=2.5))
    out.append(text(195, 102, "C(t)", size=12, color=NEG, bold=True, italic=True))
    
    # Velocity field vectors on contour 1
    out.append(arrow(120, 160, 145, 140, color=POS, sw=1.8))
    out.append(text(130, 135, "u₁", size=11, color=POS, italic=True))
    out.append(arrow(260, 150, 285, 175, color=POS, sw=1.8))
    out.append(text(285, 165, "u₂", size=11, color=POS, italic=True))
    
    out.append(textbox(195, 260, "Г(t) = ∮ u · dr", size=12, fill="#ffffff", stroke=NEG, pad=5, bold=True)[0])
    
    # Evolution arrow
    out.append(arrow(360, 170, 400, 170, color=LINE, sw=3))
    out.append(text(380, 150, "Перенос", size=11, bold=True))
    out.append(text(380, 190, "потоком", size=10, color=MUTED))
    
    # Time t + dt contour C(t + dt)
    out.append(rect(410, 50, 310, 240, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(565, 75, "Момент t + Δt: Контур C(t + Δt)", size=12, bold=True))
    
    # Deformed closed contour 2
    path_c2 = ("M 470,140 "
               "C 500,90 600,120 630,170 "
               "C 650,210 590,250 530,230 "
               "C 480,210 440,170 470,140 Z")
    out.append(f'<path d="{path_c2}" fill="#fce0d0" stroke="{POS}" stroke-width="2.5"/>')
    out.append(arrow(580, 122, 600, 138, color=POS, sw=2.5))
    out.append(text(565, 110, "C(t + Δt)", size=12, color=POS, bold=True, italic=True))
    
    out.append(textbox(565, 260, "Г(t + Δt) = ∮ u · dr = Г(t)\ndГ/dt = 0", size=11, fill="#ffffff", stroke=POS, pad=5, bold=True)[0])

    out.append('</svg>')
    render(os.path.join(IMG_DIR, "kelvin-circulation-loop.svg"), w, h, "".join(out))
    print("Saved kelvin-circulation-loop.svg")

def generate_vortex_leapfrog():
    w, h = 760, 320
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(textbox(380, 22, "Взаємодія двох коаксіальних вихорових кілець («чехарда» кілець)", size=14, bold=True)[0])
    
    # Left Panel: Stage 1
    out.append(rect(30, 50, 330, 230, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(195, 72, "1. Заднє кільце (1) наздоганяє (2)", size=12, bold=True))
    out.append(line(40, 160, 350, 160, color=MUTED, sw=1.5, dash="5,4"))
    
    # Ring 1 cores (contracted)
    out.append(circle(110, 110, 12, fill="#e8f0fe", stroke=NEG, sw=2))
    out.append(circle(110, 210, 12, fill="#e8f0fe", stroke=NEG, sw=2))
    out.append(text(110, 110, "↺", size=14, color=NEG, bold=True))
    out.append(text(110, 210, "↻", size=14, color=NEG, bold=True))
    out.append(arrow(110, 110, 150, 110, color=NEG, sw=2.5))
    out.append(arrow(110, 210, 150, 210, color=NEG, sw=2.5))
    out.append(text(110, 88, "Кільце 1", size=10, color=NEG, bold=True))

    # Ring 2 cores (expanded)
    out.append(circle(250, 80, 12, fill="#fce0d0", stroke=POS, sw=2))
    out.append(circle(250, 240, 12, fill="#fce0d0", stroke=POS, sw=2))
    out.append(text(250, 80, "↺", size=14, color=POS, bold=True))
    out.append(text(250, 240, "↻", size=14, color=POS, bold=True))
    out.append(arrow(250, 80, 280, 80, color=POS, sw=1.8))
    out.append(arrow(250, 240, 280, 240, color=POS, sw=1.8))
    out.append(text(250, 58, "Кільце 2", size=10, color=POS, bold=True))

    # Center transition arrow
    out.append(arrow(370, 160, 390, 160, color=LINE, sw=2.5))

    # Right Panel: Stage 2
    out.append(rect(400, 50, 330, 230, fill="#f8f9fa", stroke=LINE, sw=1.5))
    out.append(text(565, 72, "2. Кільце (1) проскакує крізь (2)", size=12, bold=True))
    out.append(line(410, 160, 720, 160, color=MUTED, sw=1.5, dash="5,4"))

    # Ring 2 cores (behind, widened)
    out.append(circle(480, 75, 12, fill="#fce0d0", stroke=POS, sw=2))
    out.append(circle(480, 245, 12, fill="#fce0d0", stroke=POS, sw=2))
    out.append(text(480, 75, "↺", size=14, color=POS, bold=True))
    out.append(text(480, 245, "↻", size=14, color=POS, bold=True))
    out.append(text(480, 53, "Кільце 2", size=10, color=POS, bold=True))

    # Ring 1 cores (ahead, contracted)
    out.append(circle(620, 115, 12, fill="#e8f0fe", stroke=NEG, sw=2))
    out.append(circle(620, 205, 12, fill="#e8f0fe", stroke=NEG, sw=2))
    out.append(text(620, 115, "↺", size=14, color=NEG, bold=True))
    out.append(text(620, 205, "↻", size=14, color=NEG, bold=True))
    out.append(arrow(620, 115, 665, 115, color=NEG, sw=2.5))
    out.append(arrow(620, 205, 665, 205, color=NEG, sw=2.5))
    out.append(text(620, 93, "Кільце 1", size=10, color=NEG, bold=True))

    # Bottom summary
    out.append(textbox(380, 298, "Індуковане поле Біо — Савара викликає періодичне випередження кілець", size=11, fill="#ffffff", stroke=FIELD, pad=4, bold=True)[0])

    out.append('</svg>')
    render(os.path.join(IMG_DIR, "vortex-ring-leapfrog.svg"), w, h, "".join(out))
    print("Saved vortex-ring-leapfrog.svg")

if __name__ == "__main__":
    generate_vortex_tube()
    generate_vortex_stretching()
    generate_kelvin_circulation()
    generate_vortex_leapfrog()
