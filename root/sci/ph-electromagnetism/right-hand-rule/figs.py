# -*- coding: utf-8 -*-
import sys, os

# Four levels up to root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_right_hand_rule_vectors():
    w, h = 760, 420
    frags = []
    
    # Outer panel
    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Left subpanel: Coordinate axes (Right-handed basis)
    frags.append(rect(30, 30, 340, 360, fill="#fcfcfc", stroke="#d0d0d0", sw=1, rx=6))
    frags.append(text(200, 55, "Правоорієнтована система координат", size=13, color=INK, bold=True))
    
    # Origin O
    ox, oy = 130, 290
    
    # X axis (down-left projection)
    frags.append(arrow(ox, oy, ox - 60, oy + 50, color=INK, sw=2))
    frags.append(text(ox - 75, oy + 55, "X", size=14, color=INK, bold=True))
    
    # Y axis (right)
    frags.append(arrow(ox, oy, ox + 180, oy, color=INK, sw=2))
    frags.append(text(ox + 195, oy + 5, "Y", size=14, color=INK, bold=True))
    
    # Z axis (up)
    frags.append(arrow(ox, oy, ox, oy - 180, color=INK, sw=2))
    frags.append(text(ox, oy - 195, "Z", size=14, color=INK, bold=True))
    
    # Basis relations text block
    frags.append(fitbox(180, 280, 170, 95, "Правоорієнтований базис:\ni × j = k\nj × k = i\nk × i = j", size=12, fill="#ebf5fb", stroke="#2980b9"))
    
    # Right subpanel: Cross product geometry C = A x B
    frags.append(rect(390, 30, 340, 360, fill="#fcfcfc", stroke="#d0d0d0", sw=1, rx=6))
    frags.append(text(560, 55, "Векторний добуток C = A × B", size=13, color=INK, bold=True))
    
    cx, cy = 490, 270
    
    # Vector A (along plane)
    frags.append(arrow(cx, cy, cx + 140, cy - 20, color=NEG, sw=2.5))
    frags.append(text(cx + 155, cy - 20, "A (перший множник)", size=12, color=NEG, anchor="start", bold=True))
    
    # Vector B (slanting plane)
    frags.append(arrow(cx, cy, cx + 70, cy - 100, color=FIELD, sw=2.5))
    frags.append(text(cx + 80, cy - 110, "B (другий множник)", size=12, color=FIELD, anchor="start", bold=True))
    
    # Vector C = A x B (perpendicular up)
    frags.append(arrow(cx, cy, cx, cy - 190, color=POS, sw=3))
    frags.append(text(cx + 15, cy - 180, "C = A × B (аксіальний результат)", size=12, color=POS, anchor="start", bold=True))
    
    # Angle arc and curl indicator
    path_arc = f"M {cx + 50} {cy - 7} A 50 50 0 0 0 {cx + 30} {cy - 40}"
    frags.append(f'<path d="{path_arc}" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="3,3"/>')
    frags.append(arrow(cx + 33, cy - 35, cx + 27, cy - 43, color=MUTED, sw=1.5))
    frags.append(text(cx + 55, cy - 30, "θ", size=13, color=INK, italic=True))
    
    # Explanation note
    frags.append(fitbox(410, 305, 300, 70, "Правило правої руки:\nПальці затискаються від A до B,\nвеликий палець вказує напрямок C", size=11, fill="#fef9e7", stroke="#f39c12"))

    render(os.path.join(IMG_DIR, "right-hand-rule-vectors.svg"), w, h, *frags, title="Правило правої руки та геометрія векторного добутку")

def fig_mirror_reflection_vectors():
    w, h = 760, 440
    frags = []
    
    frags.append(rect(10, 10, 740, 420, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Mirror plane in the middle
    mx = 380
    frags.append(line(mx, 40, mx, 400, color="#7f8c8d", sw=2, dash="6,4"))
    frags.append(text(mx, 32, "Площина дзеркала (YZ)", size=12, color="#7f8c8d", bold=True))
    
    # Left side: Real World
    frags.append(text(190, 55, "Реальний простір (Правий базис)", size=13, color=INK, bold=True))
    
    # Polar vector v (velocity)
    vx0, vy0 = 100, 160
    frags.append(arrow(vx0, vy0, vx0 + 120, vy0 - 40, color=NEG, sw=2.5))
    frags.append(text(vx0 + 130, vy0 - 45, "Полярний вектор v", size=12, color=NEG, anchor="start", bold=True))
    frags.append(text(vx0 + 130, vy0 - 25, "(Змінює знак: P v = −v)", size=10, color=MUTED, anchor="start", italic=True))
    
    # Rotating disk / Axial vector B
    bx0, by0 = 190, 300
    frags.append(f'<circle cx="{bx0}" cy="{by0}" r="45" fill="#f4f6f8" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    # Rotation arrow on circle
    path_rot = f"M {bx0 + 45} {by0} A 45 45 0 0 1 {bx0} {by0 + 45}"
    frags.append(f'<path d="{path_rot}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    frags.append(arrow(bx0 + 5, by0 + 45, bx0 - 5, by0 + 45, color=FIELD, sw=2))
    
    # Axial vector pointing OUT (upwards along axis)
    frags.append(arrow(bx0, by0, bx0, by0 - 90, color=POS, sw=3))
    frags.append(text(bx0 + 18, by0 - 75, "Аксіальний вектор B", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(bx0 + 18, by0 - 55, "(Не змінює знак: P B = +B)", size=10, color=MUTED, anchor="start", italic=True))
    
    # Right side: Mirror Image
    frags.append(text(570, 55, "Дзеркальне відображення", size=13, color=INK, bold=True))
    
    # Mirrored Polar vector v' (points left towards mirror)
    mvx0, mvy0 = 660, 160
    frags.append(arrow(mvx0, mvy0, mvx0 - 120, mvy0 - 40, color=NEG, sw=2.5))
    frags.append(text(mvx0 - 130, mvy0 - 45, "Відображений v'", size=12, color=NEG, anchor="end", bold=True))
    frags.append(text(mvx0 - 130, mvy0 - 25, "(Напрямок перевернуто!)", size=10, color=NEG, anchor="end", italic=True))
    
    # Mirrored disk / Axial vector B'
    mbx0, mby0 = 570, 300
    frags.append(f'<circle cx="{mbx0}" cy="{mby0}" r="45" fill="#f4f6f8" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    # Mirrored rotation arrow (opposite sense)
    mpath_rot = f"M {mbx0 - 45} {mby0} A 45 45 0 0 0 {mbx0} {mby0 + 45}"
    frags.append(f'<path d="{mpath_rot}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    frags.append(arrow(mbx0 - 5, mby0 + 45, mbx0 + 5, mby0 + 45, color=FIELD, sw=2))
    
    # Mirrored Axial vector STILL points UPWARDS!
    frags.append(arrow(mbx0, mby0, mbx0, mby0 - 90, color=POS, sw=3))
    frags.append(text(mbx0 + 18, mby0 - 75, "Відображений B'", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(mbx0 + 18, mby0 - 55, "(Спрямований ТАК САМО вгору!)", size=10, color=POS, anchor="start", italic=True))

    render(os.path.join(IMG_DIR, "mirror-reflection-vectors.svg"), w, h, *frags, title="Різниця трансформацій полярних та аксіальних векторів при дзеркальному відображенні")

def fig_lorentz_force_convention():
    w, h = 760, 460
    frags = []
    
    frags.append(rect(10, 10, 740, 440, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Comparison of two conventions: Right-hand vs Left-hand
    w_box = 340
    
    # Left box: Right-hand convention
    frags.append(rect(30, 30, w_box, 340, fill="#f8fdf8", stroke="#27ae60", sw=1.5, rx=6))
    frags.append(text(200, 55, "1. Конвенція Правої руки", size=13, color=FIELD, bold=True))
    
    frags.append(fitbox(45, 75, 310, 50, "Поле струму: B = + (μ₀ I / 2π r)\nСила Лоренца: F = q (v ×_right B)", size=11, fill="#e8f8f5", stroke="#11999e"))
    
    # Vector diagram
    cx1, cy1 = 200, 250
    frags.append(arrow(cx1, cy1, cx1 + 90, cy1, color=NEG, sw=2))
    frags.append(text(cx1 + 95, cy1 + 4, "v (полярний)", size=11, color=NEG, anchor="start", bold=True))
    
    frags.append(arrow(cx1, cy1, cx1, cy1 - 70, color=POS, sw=2))
    frags.append(text(cx1 + 10, cy1 - 60, "B_right (аксіальний)", size=11, color=POS, anchor="start", bold=True))
    
    # Force F points perpendicular (out of plane towards left/down)
    frags.append(arrow(cx1, cy1, cx1 - 65, cy1 + 65, color=INK, sw=3))
    frags.append(text(cx1 - 75, cy1 + 75, "F_физ (полярний)", size=11, color=INK, anchor="end", bold=True))
    
    # Right box: Left-hand convention
    frags.append(rect(390, 30, w_box, 340, fill="#fef8f8", stroke="#c0392b", sw=1.5, rx=6))
    frags.append(text(560, 55, "2. Конвенція Лівої руки", size=13, color=POS, bold=True))
    
    frags.append(fitbox(405, 75, 310, 50, "Поле струму: B = − (μ₀ I / 2π r)\nСила Лоренца: F = q (v ×_left B)", size=11, fill="#fadbd8", stroke="#e74c3c"))
    
    # Vector diagram
    cx2, cy2 = 560, 250
    frags.append(arrow(cx2, cy2, cx2 + 90, cy2, color=NEG, sw=2))
    frags.append(text(cx2 + 95, cy2 + 4, "v (полярний)", size=11, color=NEG, anchor="start", bold=True))
    
    # B is flipped in left hand convention!
    frags.append(arrow(cx2, cy2, cx2, cy2 + 70, color=POS, sw=2))
    frags.append(text(cx2 + 10, cy2 + 65, "B_left = −B_right", size=11, color=POS, anchor="start", bold=True))
    
    # Force F is AGAIN in the exact same physical direction!
    frags.append(arrow(cx2, cy2, cx2 - 65, cy2 + 65, color=INK, sw=3))
    frags.append(text(cx2 - 75, cy2 + 75, "F_физ (НЕ ЗМІНИЛАСЯ!)", size=11, color=INK, anchor="end", bold=True))
    
    # Bottom summary box spanning both
    frags.append(fitbox(60, 385, 640, 40, "Фізичний результат однаковісінький: (−1) від поля × (−1) від добутку = +1", size=12, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(IMG_DIR, "lorentz-force-convention.svg"), w, h, *frags, title="Незалежність фізичної сили Лоренца від вибору конвенції руки")

def fig_poynting_vector_parity():
    w, h = 760, 420
    frags = []
    
    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Diagram showing E (polar), B (axial), and S = E x B (polar)
    ox, oy = 240, 250
    
    # Electric field E (up)
    frags.append(arrow(ox, oy, ox, oy - 110, color=NEG, sw=2.5))
    frags.append(text(ox + 10, oy - 100, "E (Електричне поле)", size=12, color=NEG, anchor="start", bold=True))
    
    # Magnetic field B (slant right-down)
    frags.append(arrow(ox, oy, ox - 90, oy + 80, color=POS, sw=2.5))
    frags.append(text(ox - 100, oy + 95, "B (Магнітне поле)", size=12, color=POS, anchor="end", bold=True))
    
    # Poynting vector S = E x B (right)
    frags.append(arrow(ox, oy, ox + 280, oy, color=FIELD, sw=3.5))
    frags.append(text(ox + 130, oy - 18, "S = (1 / μ₀) E × B (Пойнтінгів потік енергії)", size=13, color=FIELD, bold=True))
    frags.append(text(ox + 130, oy + 18, "Справжній полярний вектор напрямку імпульсу", size=11, color=MUTED, italic=True))
    
    # Inversion properties box (top-left, x: 20..220, y: 30..130 - clear of ox=240!)
    frags.append(rect(20, 30, 200, 105, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(120, 50, "Трансформація P:", size=12, color=INK, bold=True))
    frags.append(text(120, 70, "P E = −E (Полярний)", size=11, color=NEG))
    frags.append(text(120, 90, "P B = +B (Аксіальний)", size=11, color=POS))
    frags.append(text(120, 110, "P S = −S (Полярний!)", size=11, color=FIELD, bold=True))
    
    # Explanation at bottom
    frags.append(fitbox(40, 335, 680, 50, "Потік енергії має реальний напрямок руху в просторі.\nМноження полярного вектора на аксіальний завжди дає справжній полярний вектор.", size=12, fill="#ebf5fb", stroke="#2980b9"))

    render(os.path.join(IMG_DIR, "poynting-vector-parity.svg"), w, h, *frags, title="Вектор Пойнтінга як полярний вектор перенесення енергії")

if __name__ == "__main__":
    fig_right_hand_rule_vectors()
    fig_mirror_reflection_vectors()
    fig_lorentz_force_convention()
    fig_poynting_vector_parity()
    print("All right-hand-rule figures generated successfully.")
