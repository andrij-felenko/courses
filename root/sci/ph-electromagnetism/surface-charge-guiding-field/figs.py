# -*- coding: utf-8 -*-
"""Фігури до теми «Поверхневий заряд у провіднику».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Поверхневий заряд на вигині дроту ─────────────────────────────
def fig_wire_bend_charge():
    W, H = 740, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Перерозподіл поверневого заряду на вигині провідника", size=16, bold=True))

    path_conductor = (
        "M 160 380 L 160 140 L 580 140 L 580 240 L 260 240 L 260 380 Z"
    )
    f.append('<path d="%s" fill="#eef4fb" stroke="%s" stroke-width="2"/>' % (path_conductor, LINE))

    f.append(arrow(210, 360, 210, 290, color=POS, sw=2.2))
    f.append(text(225, 335, "J (вхід)", size=12, bold=True, color=POS))

    f.append(arrow(210, 280, 235, 205, color=POS, sw=2.2))

    f.append(arrow(260, 190, 360, 190, color=POS, sw=2.2))
    f.append(text(310, 175, "J (поворот)", size=12, bold=True, color=POS))

    f.append(arrow(400, 190, 520, 190, color=POS, sw=2.2))

    pos_coords = [(145, 155), (145, 185), (145, 215), (170, 125), (200, 125), (230, 125)]
    for px, py in pos_coords:
        f.append(circle(px, py, 9, fill="#fde8e8", stroke=POS, sw=1.5))
        f.append(text(px, py + 4, "+", size=13, bold=True, color=POS))

    neg_coords = [(275, 255), (275, 275), (295, 255)]
    for nx, ny in neg_coords:
        f.append(circle(nx, ny, 9, fill="#e8f0fe", stroke=NEG, sw=1.5))
        f.append(text(nx, ny + 3, "−", size=13, bold=True, color=NEG))

    f.append(arrow(180, 170, 245, 225, color=FIELD, sw=2))
    f.append(text(190, 210, "E_поперечне", size=12, bold=True, color=FIELD))

    b1, _, _ = textbox(110, 80, "Зовнішній вигин:\nскупчення «+» заряду", size=12, pad=6, fill="#fdf2f2", stroke=POS, sw=1.2)
    f.append(b1)
    f.append(line(110, 106, 150, 135, color=POS, sw=1.2, dash="3,3"))

    b2, _, _ = textbox(410, 310, "Поперечне поле E створює\nдоцентрову силу для електронів", size=12, pad=8, fill="#eafaf1", stroke=FIELD, sw=1.2)
    f.append(b2)
    f.append(line(310, 290, 230, 210, color=FIELD, sw=1.2, dash="3,3"))

    b3, _, _ = textbox(360, 380, "Внутрішній вигин:\nскупчення «−» заряду", size=12, pad=6, fill="#edf4ff", stroke=NEG, sw=1.2)
    f.append(b3)
    f.append(line(340, 360, 285, 275, color=NEG, sw=1.2, dash="3,3"))

    render(os.path.join(IMG, 'wire-bend-charge.svg'), W, H, *f)


# ── Фігура 2: Поверхневий заряд на межі двох провідників ──────────────────
def fig_resistor_boundary_charge():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Поверхневий та міжфазний заряд на межі двох середовищ", size=16, bold=True))

    f.append(rect(60, 110, 200, 120, fill="#eef6ff", stroke=LINE, sw=1.8, rx=0))
    f.append(text(160, 135, "Провідник 1 (Мідь, σ1 — велика)", size=12, bold=True, color=NEG))

    f.append(rect(260, 110, 240, 120, fill="#fff8ec", stroke=LINE, sw=1.8, rx=0))
    f.append(text(380, 135, "Провідник 2 (Резистор, σ2 < σ1)", size=12, bold=True, color="#d35400"))

    f.append(rect(500, 110, 180, 120, fill="#eef6ff", stroke=LINE, sw=1.8, rx=0))
    f.append(text(590, 135, "Провідник 3 (σ1)", size=12, bold=True, color=NEG))

    f.append(arrow(90, 170, 170, 170, color=FIELD, sw=2))
    f.append(text(130, 190, "E1 = J / σ1 (мале)", size=11, bold=True, color=FIELD))

    f.append(arrow(290, 170, 470, 170, color=FIELD, sw=2.5))
    f.append(text(380, 190, "E2 = J / σ2 (велике!)", size=12, bold=True, color=FIELD))

    f.append(arrow(530, 170, 630, 170, color=FIELD, sw=2))
    f.append(text(580, 190, "E1 = J / σ1", size=11, bold=True, color=FIELD))

    for py in [125, 145, 165, 185, 205, 225]:
        f.append(circle(260, py, 7, fill="#fde8e8", stroke=POS, sw=1.2))
        f.append(text(260, py + 3.5, "+", size=10, bold=True, color=POS))

    for ny in [125, 145, 165, 185, 205, 225]:
        f.append(circle(500, ny, 7, fill="#e8f0fe", stroke=NEG, sw=1.2))
        f.append(text(500, ny + 3, "−", size=10, bold=True, color=NEG))

    b1, _, _ = textbox(260, 65, "Позитивний міжфазний заряд:\nσ_surf = ε0 · J · (1/σ2 − 1/σ1) > 0", size=11, pad=6, fill="#fdf2f2", stroke=POS, sw=1.2)
    f.append(b1)
    f.append(line(260, 90, 260, 110, color=POS, sw=1.2, dash="3,3"))

    b2, _, _ = textbox(500, 65, "Негативний міжфазний заряд:\nσ_surf = ε0 · J · (1/σ1 − 1/σ2) < 0", size=11, pad=6, fill="#edf4ff", stroke=NEG, sw=1.2)
    f.append(b2)
    f.append(line(500, 90, 500, 110, color=NEG, sw=1.2, dash="3,3"))

    b3, _, _ = textbox(W / 2, 295, "Оскільки густина струму J неперервна, стрибок провідності σ змушує електричне поле E підскочити.\nЗа законом Гаусса стрибок вектора E формує міжфазну площину заряду на стику двох матеріалів.", size=12, pad=8, fill=FILL, stroke=MUTED, sw=1.2)
    f.append(b3)

    render(os.path.join(IMG, 'resistor-boundary-charge.svg'), W, H, *f)


# ── Фігура 3: Потік вектора Пойнтінга ─────────────────────────────────────
def fig_poynting_vector_flow():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Перенесення енергії електромагнітним полем (Вектор Пойнтінга)", size=16, bold=True))

    f.append(rect(150, 140, 460, 100, fill="#f5f7fa", stroke=LINE, sw=2, rx=4))
    f.append(text(380, 190, "Провідник з опором R (струм I →)", size=14, bold=True, color=INK))

    f.append(arrow(180, 190, 270, 190, color=LINE, sw=2))

    for px in range(180, 590, 50):
        f.append(circle(px, 140, 7, fill="#fde8e8", stroke=POS, sw=1.2))
        f.append(text(px, 143.5, "+", size=10, bold=True, color=POS))

    for nx in range(180, 590, 50):
        f.append(circle(nx, 240, 7, fill="#e8f0fe", stroke=NEG, sw=1.2))
        f.append(text(nx, 243, "−", size=10, bold=True, color=NEG))

    f.append(arrow(200, 95, 560, 95, color=FIELD, sw=1.8))
    f.append(text(380, 80, "Зовнішнє електричне поле E_z", size=12, bold=True, color=FIELD))

    f.append(circle(100, 190, 25, fill="#fff8ec", stroke="#d35400", sw=1.5))
    f.append(text(100, 185, "B", size=13, bold=True, color="#d35400"))
    f.append(text(100, 202, "колове", size=10, color="#d35400"))

    for sx in [220, 330, 440, 550]:
        f.append(arrow(sx, 105, sx, 138, color=POS, sw=2.2))
        f.append(text(sx + 14, 122, "S", size=12, bold=True, color=POS))

    for sx in [220, 330, 440, 550]:
        f.append(arrow(sx, 275, sx, 242, color=POS, sw=2.2))
        f.append(text(sx + 14, 262, "S", size=12, bold=True, color=POS))

    b1, _, _ = textbox(W / 2, 340, "Вектор Пойнтінга S = (1/μ0) · (E × B) входить ВСЕРЕДИНУ провідника з навколишнього простору.\nЕнергія джерела тече не всередині мідного дроту, а через зовнішнє поле в бічну поверхню!", size=12, pad=8, fill="#fdf2f2", stroke=POS, sw=1.2)
    f.append(b1)

    render(os.path.join(IMG, 'poynting-vector-flow.svg'), W, H, *f)


# ── Фігура 4: Градієнт потенціалу та поверхневий заряд ─────────────────────
def fig_coaxial_surface_charge():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Градієнт потенціалу V(z) та профайл поверхневого заряду σ(z)", size=16, bold=True))

    f.append(line(100, 260, 640, 260, color=LINE, sw=1.8))
    f.append(arrow(640, 260, 670, 260, color=LINE, sw=1.8))
    f.append(text(675, 264, "z (довжина)", size=12, bold=True))

    f.append(line(120, 280, 120, 60, color=LINE, sw=1.8))
    f.append(arrow(120, 60, 120, 45, color=LINE, sw=1.8))
    f.append(text(120, 38, "V(z), σ_surf(z)", size=12, bold=True))

    f.append(line(120, 80, 600, 260, color=NEG, sw=2.5))
    f.append(text(280, 110, "Потенціал V(z) = V0 · (1 − z/L)", size=12, bold=True, color=NEG))

    f.append(line(120, 130, 600, 260, color=POS, sw=2, dash="5,5"))
    f.append(text(340, 175, "Густина заряду σ_surf(z) ∝ V(z)", size=12, bold=True, color=POS))

    f.append(circle(120, 80, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(90, 84, "+V0", size=12, bold=True, color=NEG))

    f.append(circle(600, 260, 4, fill=LINE, stroke=LINE, sw=1))
    f.append(text(600, 280, "z = L (0 В)", size=12, bold=True))

    f.append(rect(120, 300, 480, 20, fill="#eef4fb", stroke=LINE, sw=1.5, rx=3))
    f.append(text(360, 314, "Дріт зі струмом I (високий потенціал ліворуч → земля праворуч)", size=11, bold=True))

    charges = [(150, "+3"), (240, "+2"), (330, "+1"), (420, "0"), (510, "−1")]
    for cx, lbl in charges:
        col = POS if "+" in lbl else (NEG if "−" in lbl else MUTED)
        f.append(text(cx, 293, lbl, size=11, bold=True, color=col))

    render(os.path.join(IMG, 'coaxial-surface-charge.svg'), W, H, *f)


if __name__ == '__main__':
    fig_wire_bend_charge()
    fig_resistor_boundary_charge()
    fig_poynting_vector_flow()
    fig_coaxial_surface_charge()
    print("Фігури успішно згенеровано в ./img/")
