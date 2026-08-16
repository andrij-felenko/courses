# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach root/scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # 1. domain-reorientation.svg
    # Visualizing domain structure changes under magnetic field H
    w, h = 760, 280
    frags = []
    frags.append(text(w / 2, 25, "Мікроскопічний механізм магнітострикції: доменна переорієнтація", size=16, bold=True))
    
    # Panel 1: H = 0
    frags.append(rect(30, 55, 210, 190, fill="#f8fafc", stroke=MUTED, sw=1))
    frags.append(text(135, 78, "H = 0 (без поля)", size=13, bold=True, color=INK))
    frags.append(rect(50, 95, 170, 110, fill="#e2e8f0", stroke=LINE, sw=1.5))
    # Domain walls inside panel 1
    frags.append(line(135, 95, 135, 205, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(50, 150, 220, 150, color=MUTED, sw=1, dash="4,4"))
    # Arrows inside domains
    frags.append(arrow(92, 115, 92, 135, color=NEG, sw=2))
    frags.append(arrow(177, 135, 177, 115, color=NEG, sw=2))
    frags.append(arrow(115, 177, 75, 177, color=NEG, sw=2))
    frags.append(arrow(155, 177, 195, 177, color=NEG, sw=2))
    frags.append(text(135, 228, "Хаотична орієнтація", size=12, color=MUTED))
    frags.append(text(135, 245, "L₀ (початкова довжина)", size=12, bold=True))

    # Panel 2: Moderate H
    frags.append(rect(275, 55, 210, 190, fill="#f8fafc", stroke=MUTED, sw=1))
    frags.append(text(380, 78, "Слабке поле H →", size=13, bold=True, color=FIELD))
    frags.append(rect(295, 95, 170, 110, fill="#dcfce7", stroke=FIELD, sw=1.5))
    # Moving domain walls
    frags.append(line(355, 95, 355, 205, color=FIELD, sw=1, dash="4,4"))
    frags.append(arrow(325, 125, 345, 125, color=FIELD, sw=2))
    frags.append(arrow(410, 125, 430, 125, color=FIELD, sw=2))
    frags.append(arrow(325, 175, 345, 175, color=FIELD, sw=2))
    frags.append(arrow(410, 175, 430, 175, color=FIELD, sw=2))
    frags.append(text(380, 228, "Зміщення меж доменів", size=12, color=MUTED))
    frags.append(text(380, 245, "Невелика деформація", size=12, bold=True))

    # Panel 3: Strong H
    frags.append(rect(520, 55, 210, 190, fill="#f8fafc", stroke=MUTED, sw=1))
    frags.append(text(625, 78, "Сильне поле H ➔", size=13, bold=True, color=POS))
    # Elongated box
    frags.append(rect(535, 95, 180, 110, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(arrow(555, 150, 695, 150, color=POS, sw=3))
    frags.append(text(625, 228, "Повне обертання доменів", size=12, color=MUTED))
    frags.append(text(625, 245, "L₀ + ΔL (насичення λₛ)", size=12, bold=True, color=POS))

    render(os.path.join(img_dir, "domain-reorientation.svg"), w, h, *frags)

    # 2. magnetostriction-curve.svg
    w, h = 680, 360
    frags = []
    frags.append(text(w / 2, 25, "Крива поздовжньої магнітострикції Джоуля λ(H)", size=16, bold=True))
    
    # Axes
    ox, oy = 340, 270
    frags.append(arrow(60, oy, 640, oy, color=LINE, sw=1.5))  # H axis
    frags.append(arrow(ox, 310, ox, 50, color=LINE, sw=1.5))   # lambda axis
    frags.append(text(645, oy + 5, "H", size=14, bold=True, anchor="start"))
    frags.append(text(ox + 10, 55, "λ = ΔL / L", size=14, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy + 20, "0", size=13, color=MUTED))

    # Saturation line
    frags.append(line(80, 110, 600, 110, color=POS, sw=1.2, dash="5,5"))
    frags.append(text(520, 95, "Насичення λₛ (максимальне видовження)", size=12, bold=True, color=POS))

    # Curve paths (Symmetric quadratic shape turning into saturation)
    path_left = "M 340 270 C 260 270, 180 120, 80 110"
    path_right = "M 340 270 C 420 270, 500 120, 600 110"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_left, NEG))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_right, POS))

    # Annotations
    frags.append(circle(340, 270, 4, fill=LINE, stroke=LINE))
    frags.append(text(460, 220, "Квадратична зона: λ ∝ H²", size=12, color=POS))
    frags.append(arrow(440, 205, 410, 230, color=POS, sw=1.2))

    frags.append(text(210, 220, "λ(-H) = λ(+H)", size=12, color=NEG))
    frags.append(arrow(240, 205, 270, 230, color=NEG, sw=1.2))

    frags.append(text(w / 2, 335, "Напрям деформації не залежить від знака поля H (парний ефект)", size=13, italic=True, color=MUTED))

    render(os.path.join(img_dir, "magnetostriction-curve.svg"), w, h, *frags)

    # 3. villari-effect.svg
    w, h = 680, 360
    frags = []
    frags.append(text(w / 2, 25, "Зворотний магнітострикційний ефект (ефект Вілларі)", size=16, bold=True))

    ox, oy = 80, 290
    frags.append(arrow(ox, oy, 620, oy, color=LINE, sw=1.5)) # H axis
    frags.append(arrow(ox, oy, ox, 50, color=LINE, sw=1.5))  # B axis
    frags.append(text(625, oy + 5, "H", size=14, bold=True, anchor="start"))
    frags.append(text(ox - 10, 55, "B", size=14, bold=True, anchor="end"))

    # Curves: tension vs un-stressed vs compression for material with lambda_s > 0
    path_tension = "M 80 290 Q 200 100, 580 80"       # High permeability
    path_normal  = "M 80 290 Q 250 160, 580 140"      # Normal
    path_compress= "M 80 290 Q 320 230, 580 210"      # Low permeability

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_tension, POS))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_normal, LINE))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_compress, NEG))

    # Labels for curves
    frags.append(text(460, 70, "Розтяг (σ > 0): B зростає", size=12, bold=True, color=POS))
    frags.append(text(460, 130, "Без напруження (σ = 0)", size=12, bold=True, color=INK))
    frags.append(text(460, 200, "Стиск (σ < 0): B спадає", size=12, bold=True, color=NEG))

    frags.append(text(w / 2, 335, "Для матеріалів з λₛ > 0 розтяг полегшує намагнічування вздовж осі", size=13, italic=True, color=MUTED))

    render(os.path.join(img_dir, "villari-effect.svg"), w, h, *frags)

    # 4. terfenol-actuator-design.svg
    w, h = 780, 320
    frags = []
    frags.append(text(w / 2, 25, "Конструкція гігантського магнітострикційного приводу (Terfenol-D)", size=16, bold=True))

    # Outer Magnetic Yoke (closed magnetic circuit) from 60 to 560
    frags.append(rect(60, 70, 500, 180, fill="#f1f5f9", stroke=LINE, sw=2, rx=8))
    frags.append(rect(120, 110, 380, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))

    # Terfenol-D rod inside (190 to 470)
    frags.append(rect(190, 135, 280, 50, fill="#fca5a5", stroke=POS, sw=2, rx=3))
    frags.append(text(330, 165, "Стрижень Terfenol-D", size=14, bold=True, color=POS))

    # Excitation coils around rod (top and bottom)
    frags.append(rect(190, 115, 280, 18, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(rect(190, 187, 280, 18, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(330, 128, "Обмотка збудження (котушка)", size=11, color="#854d0e"))

    # Pre-stress Spring at left end (125 to 185)
    frags.append(rect(125, 135, 60, 50, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=2))
    frags.append('<path d="M 125 160 L 135 145 L 145 175 L 155 145 L 165 175 L 175 160" fill="none" stroke="%s" stroke-width="2"/>' % LINE)
    frags.append(text(155, 205, "Пружина σ₀", size=11, color=MUTED))

    # Output pushrod extending out to the right (starts at right edge of yoke 560 to 720)
    frags.append(rect(560, 150, 160, 20, fill="#94a3b8", stroke=LINE, sw=1.5, rx=2))
    frags.append(arrow(640, 160, 740, 160, color=POS, sw=3))
    frags.append(text(670, 140, "Вихідний рух Δx", size=12, bold=True, color=POS))

    frags.append(text(w / 2, 290, "Постійне попереднє стискання (10-15 МПа) вирівнює домени для максимального ходу", size=13, italic=True, color=MUTED))

    render(os.path.join(img_dir, "terfenol-actuator-design.svg"), w, h, *frags)
    print("Generated 4 SVG figures in ./img/")

if __name__ == '__main__':
    main()
