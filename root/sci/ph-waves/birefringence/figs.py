# -*- coding: utf-8 -*-
import os
import sys

# Add root scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def generate_calcite_double_refraction():
    w, h = 760, 340
    frags = []

    # Title
    frags.append(text(w / 2, 25, "Явище двозаломлення у кристалі ісландського шпату (кальциту)", size=16, bold=True))

    # Calcite crystal block outline
    crystal_points = "220,100 540,100 480,260 160,260"
    frags.append('<polygon points="%s" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>' % crystal_points)
    frags.append(text(350, 240, "Кристал кальциту (одновісний негативний, nₑ < nₒ)", size=12, color=MUTED, bold=True))

    # Optic axis direction (dashed line inside crystal)
    frags.append(line(200, 240, 480, 120, color="#94a3b8", sw=1.5, dash="6,4"))
    frags.append(text(495, 125, "Оптична вісь", size=11, color="#64748b", italic=True))

    # Incident unpolarized ray
    frags.append(arrow(60, 180, 260, 180, color=LINE, sw=2.5))
    frags.append(text(120, 155, "Падаючий промінь", size=13, bold=True))
    frags.append(text(120, 205, "Неполяризований", size=11, color=MUTED))

    # Unpolarized light markers (cross arrows and dots)
    for px in [100, 170]:
        frags.append(line(px, 165, px, 195, color=POS, sw=1.5))
        frags.append(circle(px, 180, 2.5, fill=NEG, stroke=NEG))

    # Point of incidence on front crystal face
    inc_x, inc_y = 190, 180
    frags.append(circle(inc_x, inc_y, 4, fill=POS, stroke=POS))

    # Ordinary ray (o-ray): travels straight or according to Snell's law
    frags.append(arrow(inc_x, inc_y, 440, 180, color=NEG, sw=2.5))
    # Polarization markers for o-ray: dots
    for px in [250, 330, 410]:
        frags.append(circle(px, 180, 3.5, fill=NEG, stroke=NEG))
    frags.append(text(340, 163, "Звичайний промінь (o-ray)", size=12, color=NEG, bold=True))

    # Extraordinary ray (e-ray): deviates upward by walk-off angle
    frags.append(arrow(inc_x, inc_y, 465, 130, color=POS, sw=2.5))
    # Polarization markers for e-ray
    for t in [0.3, 0.6, 0.85]:
        ex = inc_x + t * (465 - inc_x)
        ey = inc_y + t * (130 - inc_y)
        frags.append(line(ex - 4, ey - 9, ex + 4, ey + 9, color=POS, sw=1.8))
    frags.append(text(330, 115, "Незвичайний промінь (e-ray)", size=12, color=POS, bold=True))

    # Emergent rays (parallel to incident ray)
    frags.append(arrow(440, 180, 600, 180, color=NEG, sw=2))
    frags.append(arrow(465, 130, 600, 130, color=POS, sw=2))

    frags.append(text(530, 205, "o-промінь (s-поляризація ⊥)", size=11, color=NEG))
    frags.append(text(530, 105, "e-промінь (p-поляризація ∥)", size=11, color=POS))

    # Spatial separation bracket
    frags.append(line(620, 130, 620, 180, color=LINE, sw=1, dash="3,3"))
    frags.append(text(685, 155, "Просторове\nрозщеплення Δ", size=11, color=INK, bold=True))

    render(os.path.join(IMG_DIR, "fig1-calcite-double-refraction.svg"), w, h, *frags)


def generate_optical_indicatrix_wavefronts():
    w, h = 760, 320
    frags = []

    # Title
    frags.append(text(w / 2, 22, "Оптична індикатриса та хвильові поверхні Гюйгенса в одновісному кристалі", size=15, bold=True))

    # Panel 1: Optical Indicatrix (Ellipsoid)
    frags.append(rect(15, 45, 355, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(192, 68, "Оптична індикатриса (еліпсоїд n)", size=13, bold=True, color="#1e293b"))

    # Axes
    cx1, cy1 = 192, 175
    frags.append(line(cx1 - 130, cy1, cx1 + 130, cy1, color="#94a3b8", sw=1, dash="4,4")) # x-axis (n_o)
    frags.append(line(cx1, cy1 + 90, cx1, cy1 - 100, color="#94a3b8", sw=1.5)) # z-axis (optic axis, n_e)

    # Ellipsoid cross section
    frags.append('<ellipse cx="%d" cy="%d" rx="100" ry="65" fill="none" stroke="%s" stroke-width="2"/>' % (cx1, cy1, POS))
    # Dashed circle for n_o comparison
    frags.append('<ellipse cx="%d" cy="%d" rx="100" ry="100" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' % (cx1, cy1, NEG))

    frags.append(text(cx1 + 105, cy1 + 15, "x, y (nₒ)", size=11, color=NEG, bold=True))
    frags.append(text(cx1 + 8, cy1 - 85, "z (оптична вісь, nₑ)", size=11, color=POS, bold=True))
    frags.append(text(cx1, cy1 + 115, "Рівняння: x²/nₒ² + y²/nₒ² + z²/nₑ² = 1", size=11, color=INK))

    # Panel 2: Huygens wave surfaces (Negative uniaxial crystal n_e < n_o)
    frags.append(rect(390, 45, 355, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(567, 68, "Хвильові поверхні (негативний кристал)", size=13, bold=True, color="#1e293b"))

    cx2, cy2 = 567, 175
    frags.append(line(cx2 - 130, cy2, cx2 + 130, cy2, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(cx2, cy2 + 90, cx2, cy2 - 100, color="#94a3b8", sw=1.5))

    # Ordinary wave surface: inner sphere (v_o = c / n_o)
    frags.append(circle(cx2, cy2, 60, fill="none", stroke=NEG, sw=2))
    frags.append(text(cx2 - 80, cy2 + 45, "o-сфера (vₒ)", size=11, color=NEG, bold=True))

    # Extraordinary wave surface: outer ellipsoid (v_e = c / n_e along x, v_o along z)
    frags.append('<ellipse cx="%d" cy="%d" rx="95" ry="60" fill="none" stroke="%s" stroke-width="2"/>' % (cx2, cy2, POS))
    frags.append(text(cx2 + 55, cy2 - 40, "e-еліпсоїд (vₑ)", size=11, color=POS, bold=True))

    # Touch points on optic axis
    frags.append(circle(cx2, cy2 - 60, 3.5, fill=INK, stroke=INK))
    frags.append(circle(cx2, cy2 + 60, 3.5, fill=INK, stroke=INK))
    frags.append(text(cx2 + 12, cy2 - 62, "Точки дотику", size=10, color=MUTED))

    frags.append(text(cx2, cy2 + 115, "Швидкості: vₑ(θ) ≥ vₒ, дотик на осі z", size=11, color=INK))

    render(os.path.join(IMG_DIR, "fig2-optical-indicatrix-wavefronts.svg"), w, h, *frags)


def generate_wavevector_vs_poynting():
    w, h = 720, 320
    frags = []

    # Title
    frags.append(text(w / 2, 25, "Розходження векторів хвильової нормалі k та потоку енергії Пойнтінга S", size=15, bold=True))

    # Center origin
    ox, oy = 260, 220

    # Phase wavefront (line)
    frags.append(line(ox - 160, oy - 80, ox + 160, oy + 80, color="#94a3b8", sw=2))
    frags.append(text(ox + 165, oy + 95, "Фронт хвилі (площина рівної фази)", size=11, color="#64748b", bold=True))

    # Normal vector k (wavevector)
    kx, ky = ox + 60, oy - 120
    frags.append(arrow(ox, oy, kx, ky, color=NEG, sw=2.5))
    frags.append(text(kx + 10, ky - 5, "k (хвильовий вектор ⊥ фронту)", size=12, color=NEG, bold=True))

    # Electric field E
    ex, ey = ox + 110, oy + 55
    frags.append(arrow(ox, oy, ex, ey, color=POS, sw=2))
    frags.append(text(ex + 10, ey + 15, "E (вектор напруженості)", size=12, color=POS, bold=True))

    # Displacement vector D
    dx_vec, dy_vec = ox + 120, oy + 60
    frags.append(arrow(ox, oy, dx_vec, dy_vec, color="#8e44ad", sw=2))
    frags.append(text(dx_vec + 10, dy_vec - 5, "D (електрична індукція ⊥ k)", size=12, color="#8e44ad", bold=True))

    # Poynting vector S
    sx, sy = ox + 95, oy - 145
    frags.append(arrow(ox, oy, sx, sy, color=FIELD, sw=2.5))
    frags.append(text(sx + 10, sy - 10, "S (вектор Пойнтінга / промінь)", size=12, color=FIELD, bold=True))

    # Angle of walk-off eta
    frags.append(text(ox + 42, oy - 75, "η", size=14, color=POS, bold=True))

    # Informational panel on the right
    box, bw, bh = textbox(570, 160, "Кут зносу (Walk-off angle η):\n\n• k ⊥ фронту фази\n• S ∥ напрямку променя (енергії)\n• D ⊥ k, але E ∦ D\n• S = E × H ∦ k\n\nη = arctan[(nₒ²-nₑ²)tan θ / (nₒ²+nₑ²tan² θ)]", size=11, pad=10, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(box)

    render(os.path.join(IMG_DIR, "fig3-wavevector-vs-poynting.svg"), w, h, *frags)


def generate_waveplate_phase_shift():
    w, h = 760, 300
    frags = []

    # Title
    frags.append(text(w / 2, 22, "Перетворення поляризації фазовою платівкою (Чвертьхвильова λ/4 та Напівхвильова λ/2)", size=15, bold=True))

    # Incoming linearly polarized light (at 45 degrees)
    frags.append(text(80, 45, "Падаюче світло (45°)", size=12, bold=True, color="#1e293b"))
    frags.append(arrow(20, 150, 130, 150, color=LINE, sw=2))
    frags.append(line(55, 125, 95, 175, color=POS, sw=2))
    frags.append(text(75, 190, "Лінійна 45°", size=11, color=MUTED))

    # Waveplate crystal slab
    frags.append(rect(140, 70, 120, 160, fill="#e2e8f0", stroke="#475569", sw=2))
    frags.append(text(200, 95, "Фазова\nплатівка", size=12, bold=True, color="#0f172a"))
    frags.append(line(200, 125, 200, 210, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(200, 222, "Швидка вісь", size=10, color=POS))

    # Branch 1: Quarter-waveplate Output -> Circular Polarization
    frags.append(arrow(260, 110, 480, 110, color=LINE, sw=2))
    frags.append(circle(370, 110, 25, fill="none", stroke=FIELD, sw=2))
    frags.append(arrow(370, 110, 388, 92, color=FIELD, sw=1.8))
    frags.append(text(595, 102, "Платівка λ/4 (Δφ = π/2)", size=12, bold=True, color=FIELD))
    frags.append(text(595, 122, "→ Кругова поляризація", size=11, color=INK))

    # Branch 2: Half-waveplate Output -> Rotated Linear Polarization
    frags.append(arrow(260, 190, 480, 190, color=LINE, sw=2))
    frags.append(line(350, 210, 390, 170, color=NEG, sw=2))
    frags.append(text(595, 182, "Платівка λ/2 (Δφ = π)", size=12, bold=True, color=NEG))
    frags.append(text(595, 202, "→ Повернена лінійна (-45°)", size=11, color=INK))

    # Formula box at bottom
    frags.append(text(w / 2, 275, "Різниця фаз: Δφ = (2π / λ) · d · |nₑ - nₒ|", size=13, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "fig4-waveplate-phase-shift.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_calcite_double_refraction()
    generate_optical_indicatrix_wavefronts()
    generate_wavevector_vs_poynting()
    generate_waveplate_phase_shift()
    print("Successfully generated all SVG figures for birefringence.")
