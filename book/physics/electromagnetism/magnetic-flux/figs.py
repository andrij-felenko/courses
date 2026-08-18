# -*- coding: utf-8 -*-
"""
Generator of SVG figures for book/physics/electromagnetism/magnetic-flux
"""

import sys
import os
import math

# Add scripts/ directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_flux_definition():
    """1. Flux definition: B passing through planar area A at angle theta."""
    w, h = 640, 360
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    cx, cy = 300, 200
    lx, ly = 140, 70

    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#eaf0fd" stroke="%s" stroke-width="2.5" stroke-dasharray="none"/>' %
                 (cx - lx, cy + 20, cx + 40, cy + 20 - ly, cx + lx + 40, cy + 20 - ly + 20, cx - lx + 140, cy + 40, NEG))

    nx, ny = cx + 20, cy - 10
    frags.append(arrow(nx, ny, nx - 40, ny - 110, color=POS, sw=2.5))
    frags.append(text(nx - 55, ny - 115, "n̂ (нормаль)", size=14, color=POS, bold=True))

    frags.append(arrow(nx, ny, nx + 60, ny - 90, color=FIELD, sw=2.5))
    frags.append(text(nx + 70, ny - 95, "B (магнітне поле)", size=14, color=FIELD, bold=True))

    frags.append('<path d="M %d,%d A 45 45 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' %
                 (nx - 16, ny - 44, nx + 24, ny - 36, INK))
    frags.append(text(nx + 6, ny - 50, "θ", size=15, color=INK, bold=True, italic=True))

    for offset_x in (-80, -30, 20, 70):
        fx = cx + offset_x
        fy = cy + 10 - offset_x * 0.2
        frags.append(arrow(fx - 40, fy + 80, fx + 60, fy - 70, color="#81c784", sw=1.8))

    box_s = fitbox(430, 40, 190, 100, "Формула потоку:\nΦ = B · A · cos(θ)\n\n• Φ — вебер (Wb)\n• B — тесла (T)\n• A — м²", size=13, fill="#f4f6f8", stroke="#d1d5db")
    frags.append(box_s)

    box_cases = fitbox(430, 155, 190, 180, "Крайові випадки кута θ:\n\n1) θ = 0° (B ⊥ контуру):\n   cos(0°) = 1 → Φ_max = B·A\n\n2) θ = 60°:\n   cos(60°) = 0.5 → Φ = 0.5 B·A\n\n3) θ = 90° (B ∥ контуру):\n   cos(90°) = 0 → Φ = 0", size=12, fill="#f9fafb", stroke="#d1d5db")
    frags.append(box_cases)

    render(os.path.join(IMG_DIR, "flux-definition.svg"), w, h, *frags)

def fig_flux_element():
    """2. Surface integral dPhi = B * dA over curved surface S."""
    w, h = 640, 360
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    frags.append('<path d="M 80,240 Q 180,100 320,180 T 520,140 L 480,260 Q 340,300 200,240 Z" fill="#eaf0fd" stroke="%s" stroke-width="2"/>' % NEG)
    frags.append(text(120, 265, "Поверхня S", size=15, color=NEG, bold=True))

    ex, ey = 300, 190
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#fdecea" stroke="%s" stroke-width="2"/>' %
                 (ex - 20, ey + 10, ex + 15, ey - 10, ex + 35, ey + 5, ex, ey + 25, POS))
    frags.append(text(ex - 35, ey + 30, "dA = n̂ dA", size=13, color=POS, bold=True))

    frags.append(arrow(ex + 8, ey + 7, ex + 20, ey - 60, color=POS, sw=2))
    frags.append(text(ex + 25, ey - 62, "n̂", size=14, color=POS, bold=True))

    frags.append(arrow(ex + 8, ey + 7, ex + 65, ey - 45, color=FIELD, sw=2.2))
    frags.append(text(ex + 72, ey - 47, "B", size=14, color=FIELD, bold=True))

    frags.append(text(250, 40, "Інтегрування по довільній поверхні S:", size=15, color=INK, bold=True))
    frags.append(fitbox(180, 65, 340, 45, "dΦ = B · dA = B · n̂ dA = B cos(θ) dA\nΦ = ∫_S B · dA", size=14, fill="#f4f6f8", stroke=FIELD, sw=1.5))

    for x_start, y_start, x_end, y_end in [(140, 290, 200, 110), (220, 290, 270, 120), (380, 280, 430, 110), (450, 280, 490, 120)]:
        frags.append(arrow(x_start, y_start, x_end, y_end, color="#81c784", sw=1.5))

    render(os.path.join(IMG_DIR, "flux-element.svg"), w, h, *frags)

def fig_gauss_law_closed():
    """3. Gauss's Law for magnetism: closed surface integral B * dA = 0."""
    w, h = 640, 360
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    cx, cy = 240, 190
    rx, ry = 130, 90
    frags.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#eaf0fd" stroke="%s" stroke-width="2.5" stroke-dasharray="none"/>' %
                 (cx, cy, rx, ry, NEG))
    frags.append(text(cx - 70, cy + 60, "Замкнена поверхня S", size=13, color=NEG, bold=True))

    frags.append(arrow(50, 170, cx - rx + 5, 170, color=FIELD, sw=2))
    frags.append(arrow(cx - rx + 5, 170, cx + rx - 5, 170, color=FIELD, sw=2))
    frags.append(arrow(cx + rx - 5, 170, 410, 170, color=FIELD, sw=2))

    frags.append(arrow(60, 240, 140, 220, color=FIELD, sw=2))
    frags.append(arrow(140, 220, 330, 140, color=FIELD, sw=2))
    frags.append(arrow(330, 140, 410, 120, color=FIELD, sw=2))

    frags.append(text(120, 140, "Вхідний потік (Φ_in < 0)", size=12, color=NEG, bold=True))
    frags.append(text(340, 220, "Вихідний потік (Φ_out > 0)", size=12, color=POS, bold=True))

    frags.append(fitbox(430, 40, 190, 90, "Закон Гаусса для B:\n\n∮_S B · dA = 0\n\n(Інтегральна форма)", size=13, fill="#f4f6f8", stroke=FIELD, sw=2))

    frags.append(fitbox(430, 145, 190, 80, "Диференціальна форма:\n\n∇ · B = 0\n\n(див. ротор/дивергенція)", size=13, fill="#f9fafb", stroke="#d1d5db"))

    frags.append(fitbox(430, 240, 190, 95, "Фізичний зміст:\n• Немає магнітних зарядів\n• Силові лінії B замкнені\n• Φ_in + Φ_out = 0", size=12, fill="#fffbe6", stroke="#f59e0b"))

    render(os.path.join(IMG_DIR, "gauss-law-closed.svg"), w, h, *frags)

def fig_stokes_vector_potential():
    """4. Stokes' theorem relation: flux Phi = contour integral A * dl."""
    w, h = 640, 360
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    cx, cy = 240, 195
    frags.append('<path d="M 120,180 C 140,110 320,110 360,180 C 380,250 200,270 120,180 Z" fill="#eaf0fd" stroke="%s" stroke-width="2.5"/>' % POS)
    frags.append(text(cx, cy + 10, "Поверхня S", size=14, color=NEG, bold=True))

    frags.append(arrow(340, 220, 310, 240, color=POS, sw=2.5))
    frags.append(text(340, 255, "Контур C (напрям dl)", size=13, color=POS, bold=True))

    frags.append(arrow(160, 130, 220, 120, color="#8e44ad", sw=2.5))
    frags.append(text(180, 110, "A (векторний потенціал)", size=13, color="#8e44ad", bold=True))

    for bx, by in [(200, 160), (260, 150), (230, 210), (290, 190)]:
        frags.append(arrow(bx, by + 30, bx + 10, by - 30, color=FIELD, sw=2))

    frags.append(text(295, 140, "B = ∇ × A", size=14, color=FIELD, bold=True))

    frags.append(fitbox(420, 45, 200, 95, "Теорема Стокса:\n\nΦ = ∬_S B · dA\n  = ∬_S (∇ × A) · dA\n  = ∮_C A · dl", size=14, fill="#f4f6f8", stroke="#8e44ad", sw=2))

    frags.append(fitbox(420, 160, 200, 165, "Значення зв'язку B та A:\n\n• Потік — це циркуляція\n  векторного потенціалу A\n  вздовж замкненого контуру C.\n\n• Не залежить від формації\n  поверхні S, натягнутої\n  на контур C.", size=12, fill="#f9fafb", stroke="#d1d5db"))

    render(os.path.join(IMG_DIR, "stokes-vector-potential.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_flux_definition()
    fig_flux_element()
    fig_gauss_law_closed()
    fig_stokes_vector_potential()
    print("Figures generated successfully in", IMG_DIR)
