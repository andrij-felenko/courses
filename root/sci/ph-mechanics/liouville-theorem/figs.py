# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема Ліувілля».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math

# Чотири рівні вгору від book/physics/mechanics/liouville-theorem до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, op=1.0):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, op, stroke, sw))


# ── Фігура 1: Збереження фазового об'єму (phase-volume-preservation.svg) ──
def gen_phase_volume_preservation():
    w, h = 760, 360
    elements = []
    
    # Осі координатної системи (q, p)
    elements.append(arrow(60, 310, 710, 310, color=LINE, sw=2.0))
    elements.append(arrow(80, 330, 80, 40, color=LINE, sw=2.0))
    elements.append(text(720, 315, "q (координата)", size=13, anchor="start", bold=True))
    elements.append(text(85, 30, "p (імпульс)", size=13, anchor="start", bold=True))
    
    # Допоміжна сітка фазового простору
    for x in range(160, 700, 80):
        elements.append(line(x, 50, x, 300, color="#e5e7eb", sw=1.0, dash="3,3"))
    for y in range(80, 300, 50):
        elements.append(line(90, y, 690, y, color="#e5e7eb", sw=1.0, dash="3,3"))

    # Стан t0: Початковий круглий/еліптичний об'єм Ω(t₀)
    c0_x, c0_y, rx0 = 170, 180, 45
    elements.append(circle(c0_x, c0_y, rx0, fill="#3b82f6", stroke="#1d4ed8", sw=2.0))
    elements.append(textbox(c0_x, c0_y - 5, "Ω(t₀)", size=14, pad=4, fill="#ffffff", stroke="#1d4ed8", bold=True)[0])
    elements.append(text(c0_x, c0_y + 65, "Початковий стан t₀", size=12, color=MUTED, anchor="middle"))

    # Стрілка еволюції потоку t0 -> t1
    elements.append(arrow(230, 180, 310, 180, color=FIELD, sw=2.5))
    elements.append(text(270, 165, "Фазовий потік gᵗ", size=12, color=FIELD, anchor="middle", bold=True))

    # Стан t1: Деформований подовжений еліпс Ω(t₁)
    c1_x, c1_y = 400, 180
    path_t1 = "M 330 220 C 360 130, 440 130, 470 140 C 440 230, 360 230, 330 220 Z"
    elements.append(f'<path d="{path_t1}" fill="#3b82f6" fill-opacity="0.85" stroke="#1d4ed8" stroke-width="2.0"/>')
    elements.append(textbox(c1_x, c1_y - 5, "Ω(t₁)", size=14, pad=4, fill="#ffffff", stroke="#1d4ed8", bold=True)[0])
    elements.append(text(c1_x, c1_y + 65, "Деформація зсуву t₁", size=12, color=MUTED, anchor="middle"))

    # Стрілка еволюції потоку t1 -> t2
    elements.append(arrow(485, 180, 545, 180, color=FIELD, sw=2.5))

    # Стан t2: Складне викривлення Ω(t₂)
    path_t2 = "M 570 260 C 580 100, 670 100, 680 120 C 660 135, 600 145, 590 260 Z"
    elements.append(f'<path d="{path_t2}" fill="#3b82f6" fill-opacity="0.85" stroke="#1d4ed8" stroke-width="2.0"/>')
    elements.append(textbox(630, 180, "Ω(t₂)", size=14, pad=4, fill="#ffffff", stroke="#1d4ed8", bold=True)[0])
    elements.append(text(630, 280, "Складне викривлення t₂", size=12, color=MUTED, anchor="middle"))

    # Пояснювальний підпис-рівність площ
    eq_box, _, _ = textbox(380, 335, "Рівність фазових об'ємів: Volume(Ω(t₀)) = Volume(Ω(t₁)) = Volume(Ω(t₂))", 
                           size=13, pad=8, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True)
    elements.append(eq_box)

    path = os.path.join(IMG_DIR, "phase-volume-preservation.svg")
    render(path, w, h, *elements)
    print(f"Збережено: {path}")


# ── Фігура 2: Консервативний проти дисипативного потоку (dissipative-vs-conservative.svg) ──
def gen_dissipative_vs_conservative():
    w, h = 760, 360
    elements = []
    
    # ── Ліва панель: Консервативна система (Гамільтонова) ──
    elements.append(rect(20, 15, 345, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    elements.append(text(192, 40, "Консервативна система (∇·v = 0)", size=14, color="#0f172a", anchor="middle", bold=True))
    elements.append(text(192, 60, "Закон збереження енергії H(q,p) = const", size=11, color=MUTED, anchor="middle"))
    
    elements.append(line(60, 190, 325, 190, color=LINE, sw=1.5))
    elements.append(line(192, 75, 192, 305, color=LINE, sw=1.5))
    elements.append(text(330, 194, "q", size=13, anchor="start", bold=True))
    elements.append(text(192, 70, "p", size=13, anchor="middle", bold=True))
    
    for rx, ry in [(50, 35), (90, 63), (125, 88)]:
        elements.append(ellipse(192, 190, rx, ry, fill="none", stroke="#2563eb", sw=1.8))
    
    elements.append(ellipse(192 + 90, 190, 18, 18, fill="#93c5fd", stroke="#1d4ed8", sw=1.5, op=0.7))
    elements.append(text(192 + 90, 190, "Ω₀", size=12, anchor="middle", bold=True))
    elements.append(text(192, 295, "Об'єм зберігається сталим", size=12, color="#1e40af", anchor="middle", bold=True))

    # ── Права панель: Дисипативна система (З тертям) ──
    elements.append(rect(395, 15, 345, 330, fill="#fff1f2", stroke="#fca5a5", sw=1.5, rx=8))
    elements.append(text(567, 40, "Дисипативна система (∇·v < 0)", size=14, color="#991b1b", anchor="middle", bold=True))
    elements.append(text(567, 60, "Наявність тертя/згасання γ > 0", size=11, color=MUTED, anchor="middle"))

    elements.append(line(435, 190, 700, 190, color=LINE, sw=1.5))
    elements.append(line(567, 75, 567, 305, color=LINE, sw=1.5))
    elements.append(text(705, 194, "q", size=13, anchor="start", bold=True))
    elements.append(text(567, 70, "p", size=13, anchor="middle", bold=True))

    spiral_pts = []
    cx, cy = 567, 190
    for deg in range(0, 1080, 10):
        rad = math.radians(deg)
        r = 120 * math.exp(-0.003 * deg)
        px = cx + r * math.cos(rad)
        py = cy - r * math.sin(rad)
        spiral_pts.append(f"{px:.1f},{py:.1f}")
    path_spiral = "M " + " L ".join(spiral_pts)
    elements.append(f'<path d="{path_spiral}" fill="none" stroke="#dc2626" stroke-width="2.0"/>')

    elements.append(ellipse(cx + 100, cy, 22, 22, fill="#fca5a5", stroke="#dc2626", sw=1.5, op=0.7))
    elements.append(text(cx + 100, cy, "Ω₀", size=11, anchor="middle", bold=True))
    
    elements.append(circle(cx, cy, 5, fill="#991b1b", stroke="#991b1b", sw=1.0))
    elements.append(text(cx, cy + 22, "Атрактор (0,0)", size=11, color="#991b1b", anchor="middle", bold=True))
    elements.append(text(567, 295, "Об'єм стискається до нуля: Ω(t) → 0", size=12, color="#991b1b", anchor="middle", bold=True))

    path = os.path.join(IMG_DIR, "dissipative-vs-conservative.svg")
    render(path, w, h, *elements)
    print(f"Збережено: {path}")


# ── Фігура 3: Симплектичні та несимплектичні інтегратори (symplectic-vs-euler.svg) ──
def gen_symplectic_vs_euler():
    w, h = 760, 360
    elements = []
    
    elements.append(rect(20, 15, 345, 330, fill="#fffbf0", stroke="#fde68a", sw=1.5, rx=8))
    elements.append(text(192, 40, "Явний метод Ейлера (det J > 1)", size=14, color="#92400e", anchor="middle", bold=True))
    elements.append(text(192, 60, "Штучне розширення фазового об'єму", size=11, color=MUTED, anchor="middle"))
    
    elements.append(line(60, 190, 325, 190, color=LINE, sw=1.5))
    elements.append(line(192, 75, 192, 305, color=LINE, sw=1.5))
    
    spiral_out = []
    cx, cy = 192, 190
    for deg in range(0, 720, 15):
        rad = math.radians(deg)
        r = 30 * math.exp(0.002 * deg)
        px = cx + r * math.cos(rad)
        py = cy - r * math.sin(rad)
        spiral_out.append(f"{px:.1f},{py:.1f}")
    elements.append(f'<path d="M {" L ".join(spiral_out)}" fill="none" stroke="#d97706" stroke-width="2.0"/>')
    elements.append(text(192, 295, "Енергія та об'єм нефізично зростають", size=12, color="#b45309", anchor="middle", bold=True))

    elements.append(rect(395, 15, 345, 330, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    elements.append(text(567, 40, "Симплектичний метод (det J ≡ 1)", size=14, color="#166534", anchor="middle", bold=True))
    elements.append(text(567, 60, "Точне збереження фазової міри", size=11, color=MUTED, anchor="middle"))

    elements.append(line(435, 190, 700, 190, color=LINE, sw=1.5))
    elements.append(line(567, 75, 567, 305, color=LINE, sw=1.5))

    cx, cy = 567, 190
    elements.append(ellipse(cx, cy, 95, 80, fill="none", stroke="#16a34a", sw=2.0))
    elements.append(rect(cx + 40, cy - 60, 30, 30, fill="#bbf7d0", stroke="#16a34a", sw=1.5, rx=3))
    elements.append(rect(cx - 70, cy + 30, 45, 20, fill="#bbf7d0", stroke="#16a34a", sw=1.5, rx=3))
    elements.append(text(567, 295, "Орбіта стійка, det J = 1.000... строго", size=12, color="#15803d", anchor="middle", bold=True))

    path = os.path.join(IMG_DIR, "symplectic-vs-euler.svg")
    render(path, w, h, *elements)
    print(f"Збережено: {path}")


# ── Фігура 4: Дивергенція потоку фазової рідини (density-continuity.svg) ──
def gen_density_continuity():
    w, h = 760, 360
    elements = []
    
    cx, cy = 380, 180
    box_w, box_h = 240, 160
    bx, by = cx - box_w / 2, cy - box_h / 2
    
    elements.append(rect(bx, by, box_w, box_h, fill="#eff6ff", stroke="#2563eb", sw=2.0, rx=4))
    elements.append(text(cx, cy, "Осередок dq·dp", size=16, color="#1d4ed8", anchor="middle", bold=True))
    
    elements.append(arrow(bx - 70, cy, bx - 10, cy, color=FIELD, sw=2.5))
    elements.append(text(bx - 40, cy - 15, "Вхід q̇(q)", size=12, color=FIELD, anchor="middle", bold=True))

    elements.append(arrow(bx + box_w + 10, cy, bx + box_w + 70, cy, color=FIELD, sw=2.5))
    elements.append(text(bx + box_w + 40, cy - 15, "Вихід q̇(q+dq)", size=12, color=FIELD, anchor="middle", bold=True))

    elements.append(arrow(cx, by + box_h + 60, cx, by + box_h + 10, color=POS, sw=2.5))
    elements.append(text(cx + 60, by + box_h + 35, "Вхід ṗ(p)", size=12, color=POS, anchor="start", bold=True))

    elements.append(arrow(cx, by - 10, cx, by - 60, color=POS, sw=2.5))
    elements.append(text(cx + 60, by - 35, "Вихід ṗ(p+dp)", size=12, color=POS, anchor="start", bold=True))

    eq_str = "Баланс потоків:  ∂q̇/∂q + ∂ṗ/∂p = ∂²H/(∂q ∂p) - ∂²H/(∂p ∂q) ≡ 0  ⇒  div v = 0"
    eq_box, _, _ = textbox(cx, 325, eq_str, size=13, pad=8, fill="#f8fafc", stroke="#0f172a", color="#0f172a", bold=True)
    elements.append(eq_box)

    path = os.path.join(IMG_DIR, "density-continuity.svg")
    render(path, w, h, *elements)
    print(f"Збережено: {path}")


def main():
    gen_phase_volume_preservation()
    gen_dissipative_vs_conservative()
    gen_symplectic_vs_euler()
    gen_density_continuity()
    print("Усі фігури успішно згенеровано.")

if __name__ == '__main__':
    main()
