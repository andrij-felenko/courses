# -*- coding: utf-8 -*-
"""Generator for SVG figures in book/physics/oscillations-waves/coherence/img/"""
import os
import sys
import math

# Add scripts directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, text, rect, line, arrow, circle, textbox, fitbox, INK, MUTED, POS, NEG, FIELD, FILL, BG, LINE

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def gen_temporal_coherence():
    w, h = 800, 380
    frags = []
    
    # Title / Header areas
    frags.append(rect(20, 20, 760, 155, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(rect(20, 195, 760, 165, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    
    # Section 1: High Temporal Coherence
    frags.append(text(35, 45, "Висока часова когерентність (монохроматичне світло / лазер)", size=14, color=INK, bold=True, anchor="start"))
    frags.append(text(35, 63, "Тривалий хвильовий цуг, фаза зберігається на всій довжині", size=12, color=MUTED, anchor="start"))
    
    # Waveform 1: continuous sine wave
    pts1 = []
    for x in range(40, 740, 2):
        y = 110 + 28 * math.sin(2 * math.pi * (x - 40) / 45)
        pts1.append(f"{x:.1f},{y:.1f}")
    frags.append(f'<polyline points="{" ".join(pts1)}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    
    # Coherence length marker
    frags.append(line(40, 150, 730, 150, color=POS, sw=1.5, dash="4,4"))
    frags.append(line(40, 142, 40, 158, color=POS, sw=1.5))
    frags.append(line(730, 142, 730, 158, color=POS, sw=1.5))
    frags.append(textbox(385, 150, "Довжина когерентності L_c = c · τ_c (велика)", size=12, pad=6, fill="#fef2f2", stroke=POS, color=POS, bold=True)[0])
    
    # Section 2: Low Temporal Coherence
    frags.append(text(35, 220, "Низька часова когерентність (теплове випромінювання / біле світло)", size=14, color=INK, bold=True, anchor="start"))
    frags.append(text(35, 238, "Короткі хвильові цуги з випадковими зсувами фази", size=12, color=MUTED, anchor="start"))
    
    # Waveform 2: short wave packets with phase jumps
    pts2 = []
    phases = [0, 1.8, 4.2, 0.9, 3.1, 5.0, 1.2]
    segment_len = 100
    for i in range(7):
        start_x = 40 + i * segment_len
        ph = phases[i]
        for dx in range(0, segment_len, 2):
            x = start_x + dx
            if x > 740:
                break
            # Envelope to fade packet ends slightly
            env = math.sin(math.pi * dx / segment_len)
            y = 285 + 28 * env * math.sin(2 * math.pi * dx / 40 + ph)
            pts2.append(f"{x:.1f},{y:.1f}")
        # Draw phase jump vertical marker
        if i < 6:
            jx = start_x + segment_len
            frags.append(line(jx, 255, jx, 315, color="#f59e0b", sw=1.2, dash="2,2"))
            
    frags.append(f'<polyline points="{" ".join(pts2)}" fill="none" stroke="{POS}" stroke-width="2"/>')
    
    # Short Coherence length marker
    frags.append(line(40, 335, 140, 335, color=POS, sw=1.5))
    frags.append(line(40, 327, 40, 343, color=POS, sw=1.5))
    frags.append(line(140, 327, 140, 343, color=POS, sw=1.5))
    frags.append(textbox(210, 335, "Малий цуг L_c", size=11, pad=5, fill="#fef2f2", stroke=POS, color=POS)[0])
    
    frags.append(text(540, 335, "▲ Жовті штрихи — випадкові стрибки фази", size=11, color="#b45309", anchor="start"))
    
    render(os.path.join(IMG_DIR, 'temporal-coherence.svg'), w, h, *frags)

def gen_spatial_coherence():
    w, h = 800, 390
    frags = []
    
    # Background boxes
    frags.append(rect(20, 20, 370, 350, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(rect(410, 20, 370, 350, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    
    # Left: Extended Source (Low spatial coherence)
    frags.append(text(205, 45, "Протяжне джерело", size=14, color=INK, bold=True))
    frags.append(text(205, 63, "Низька просторова когерентність", size=12, color=MUTED))
    
    # Extended source body
    frags.append(rect(40, 110, 25, 160, fill="#fde047", stroke="#eab308", rx=4))
    frags.append(text(52, 190, "Джерело", size=11, color="#713f12", bold=True, anchor="middle"))
    
    # Uncorrelated emitters
    emitters_y = [130, 160, 190, 220, 250]
    for ey in emitters_y:
        frags.append(circle(52, ey, 4, fill=POS, stroke="#991b1b"))
        # Wavefronts from each point emitter
        for r in [40, 80, 120, 160]:
            frags.append(f'<path d="M {52+r*0.7:.1f} {ey-r*0.7:.1f} A {r} {r} 0 0 1 {52+r*0.7:.1f} {ey+r*0.7:.1f}" fill="none" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3"/>')
            
    # Screen / Observation points
    frags.append(line(270, 90, 270, 290, color=LINE, sw=2))
    frags.append(circle(270, 140, 5, fill=NEG, stroke="#1e3a8a"))
    frags.append(circle(270, 240, 5, fill=NEG, stroke="#1e3a8a"))
    frags.append(text(285, 140, "P₁", size=13, color=NEG, bold=True, anchor="start"))
    frags.append(text(285, 240, "P₂", size=13, color=NEG, bold=True, anchor="start"))
    
    # Random phase relation note
    frags.append(textbox(205, 325, "Різниця фаз між P₁ та P₂\nвипадково змінюється з часом", size=11, pad=6, fill="#fef2f2", stroke=POS, color=POS)[0])
    
    # Right: Point Source / Far Field (High spatial coherence)
    frags.append(text(595, 45, "Точкове джерело / Віддалений фронт", size=14, color=INK, bold=True))
    frags.append(text(595, 63, "Висока просторова когерентність", size=12, color=MUTED))
    
    # Point source
    frags.append(circle(440, 190, 8, fill="#fde047", stroke="#eab308"))
    frags.append(text(440, 215, "Джерело", size=11, color="#713f12", bold=True))
    
    # Concentric coherent spherical wavefronts
    for r in [40, 80, 120, 160, 200]:
        frags.append(f'<path d="M {440+r*0.7:.1f} {190-r*0.7:.1f} A {r} {r} 0 0 1 {440+r*0.7:.1f} {190+r*0.7:.1f}" fill="none" stroke="{FIELD}" stroke-width="2"/>')
        
    # Observation screen
    frags.append(line(670, 90, 670, 290, color=LINE, sw=2))
    frags.append(circle(670, 140, 5, fill=FIELD, stroke="#14532d"))
    frags.append(circle(670, 240, 5, fill=FIELD, stroke="#14532d"))
    frags.append(text(685, 140, "P₁", size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(685, 240, "P₂", size=13, color=FIELD, bold=True, anchor="start"))
    
    # Coherent phase relation note
    frags.append(textbox(595, 325, "Різниця фаз між P₁ та P₂\nстрого фіксована в часі", size=11, pad=6, fill="#f0fdf4", stroke=FIELD, color=FIELD)[0])
    
    render(os.path.join(IMG_DIR, 'spatial-coherence.svg'), w, h, *frags)

def gen_michelson_coherence():
    w, h = 760, 420
    frags = []
    
    frags.append(rect(20, 20, 720, 380, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    
    # Light Source
    frags.append(rect(50, 180, 70, 50, fill="#fef08a", stroke="#eab308", rx=6))
    frags.append(text(85, 210, "Джерело", size=12, color="#713f12", bold=True))
    
    # Light beam from source to beam splitter
    frags.append(line(120, 205, 320, 205, color="#f59e0b", sw=3))
    frags.append(arrow(200, 205, 220, 205, color="#f59e0b", sw=2))
    
    # Beam splitter (semi-transparent mirror at 45 deg)
    frags.append(line(300, 225, 340, 185, color="#38bdf8", sw=4))
    frags.append(text(345, 175, "Світлодільник", size=12, color=INK, bold=True, anchor="start"))
    
    # Beam 1: upward to fixed mirror
    frags.append(line(320, 205, 320, 70, color="#ef4444", sw=2.5))
    frags.append(arrow(320, 150, 320, 120, color="#ef4444", sw=2))
    frags.append(arrow(320, 100, 320, 140, color="#ef4444", sw=2))
    
    # Fixed mirror M1
    frags.append(rect(280, 55, 80, 15, fill="#94a3b8", stroke="#475569", rx=2))
    frags.append(text(320, 40, "Нерухоме дзеркало Д₁", size=12, color=INK, bold=True))
    
    # Beam 2: right to movable mirror
    frags.append(line(320, 205, 570, 205, color="#3b82f6", sw=2.5))
    frags.append(arrow(400, 205, 430, 205, color="#3b82f6", sw=2))
    frags.append(arrow(500, 205, 470, 205, color="#3b82f6", sw=2))
    
    # Movable mirror M2
    frags.append(rect(570, 165, 15, 80, fill="#94a3b8", stroke="#475569", rx=2))
    frags.append(text(650, 205, "Рухоме дзеркало Д₂\n(зсув Δd)", size=11, color=INK, bold=True, anchor="start"))
    frags.append(arrow(600, 140, 630, 140, color=POS, sw=1.5))
    frags.append(arrow(630, 140, 600, 140, color=POS, sw=1.5))
    
    # Combined Beam down to detector
    frags.append(line(320, 205, 320, 340, color="#8b5cf6", sw=3))
    frags.append(arrow(320, 250, 320, 280, color="#8b5cf6", sw=2))
    
    # Detector / Screen
    frags.append(rect(270, 340, 100, 45, fill="#e2e8f0", stroke="#475569", rx=6))
    frags.append(text(320, 367, "Детектор / Екран", size=12, color=INK, bold=True))
    
    # Callout info box
    info = "Різниця ходу Δx = 2·Δd\nЧас запізнення τ = Δx / c\nПри Δx > L_c смуги зникають (V → 0)"
    frags.append(textbox(150, 325, info, size=11, pad=8, fill="#ffffff", stroke="#cbd5e1", color=INK)[0])
    
    render(os.path.join(IMG_DIR, 'michelson-coherence.svg'), w, h, *frags)

def gen_coherence_visibility():
    w, h = 800, 360
    frags = []
    
    frags.append(rect(20, 20, 760, 320, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    
    # 3 columns for V = 1.0, V = 0.5, V = 0.0
    col_w = 230
    cols = [
        (40, "Повна когерентність", "|γ| = 1.0, V = 1.0", FIELD, 1.0),
        (285, "Часткова когерентність", "|γ| = 0.5, V = 0.5", "#f59e0b", 0.5),
        (530, "Некогерентне світло", "|γ| = 0.0, V = 0.0", POS, 0.0)
    ]
    
    for x_start, title_str, sub_str, col_color, v_val in cols:
        frags.append(rect(x_start, 40, col_w, 280, fill="#ffffff", stroke="#e2e8f0", rx=6))
        frags.append(text(x_start + col_w/2, 65, title_str, size=13, color=INK, bold=True))
        frags.append(text(x_start + col_w/2, 83, sub_str, size=12, color=col_color, bold=True))
        
        # Coordinate axes inside panel
        ax_x1, ax_x2 = x_start + 20, x_start + col_w - 20
        ax_y0 = 240
        frags.append(line(ax_x1, ax_y0, ax_x2, ax_y0, color="#94a3b8", sw=1.2))
        frags.append(line(ax_x1, 110, ax_x1, ax_y0 + 10, color="#94a3b8", sw=1.2))
        
        # Plotting intensity fringes I(x) = I0 * (1 + V * cos(k x))
        pts = []
        i0 = 60
        for px in range(int(ax_x1), int(ax_x2) + 1, 2):
            rel_x = px - ax_x1
            cos_val = math.cos(2 * math.pi * rel_x / 40)
            i_val = i0 * (1 + v_val * cos_val)
            py = ax_y0 - i_val
            pts.append(f"{px:.1f},{py:.1f}")
        frags.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col_color}" stroke-width="2.2"/>')
        
        # Max and Min markers if v_val > 0
        if v_val > 0:
            ymax = ax_y0 - i0 * (1 + v_val)
            ymin = ax_y0 - i0 * (1 - v_val)
            frags.append(line(ax_x1 - 3, ymax, ax_x2, ymax, color=MUTED, sw=0.8, dash="2,2"))
            frags.append(line(ax_x1 - 3, ymin, ax_x2, ymin, color=MUTED, sw=0.8, dash="2,2"))
            frags.append(text(ax_x1 + 10, ymax - 4, "I_max", size=10, color=MUTED, anchor="start"))
            frags.append(text(ax_x1 + 10, ymin + 12, "I_min", size=10, color=MUTED, anchor="start"))
            
        # Formula box below plot
        v_formula = "V = (I_max - I_min) / (I_max + I_min)"
        frags.append(textbox(x_start + col_w/2, 285, v_formula, size=10, pad=4, fill="#f8fafc", stroke="#cbd5e1", color=INK)[0])
        
    render(os.path.join(IMG_DIR, 'coherence-visibility.svg'), w, h, *frags)

if __name__ == '__main__':
    gen_temporal_coherence()
    gen_spatial_coherence()
    gen_michelson_coherence()
    gen_coherence_visibility()
    print("All SVG figures generated successfully in img/")
