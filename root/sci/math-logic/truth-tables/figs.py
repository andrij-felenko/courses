# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_hypercube():
    W, H = 760, 480
    p = []
    
    # Title
    p.append(text(W / 2, 28, "Геометрична оцінка булевого куба B^3 для функції F(P, Q, R) = (P ∧ Q) ∨ R", size=15, bold=True, color=INK))
    
    # 3D Hypercube projection vertices (B^3)
    # Front face (R=0)
    v000 = (220, 340)
    v100 = (420, 340)
    v110 = (420, 180)
    v010 = (220, 180)
    
    # Back face (R=1)
    v001 = (310, 260)
    v101 = (510, 260)
    v111 = (510, 100)
    v011 = (310, 100)
    
    # Draw edges
    edges = [
        (v000, v100), (v100, v110), (v110, v010), (v010, v000), # Front face (R=0)
        (v001, v101), (v101, v111), (v111, v011), (v011, v001), # Back face (R=1)
        (v000, v001), (v100, v101), (v110, v111), (v010, v011)  # Interconnecting edges along R
    ]
    
    for start, end in edges:
        p.append(line(start[0], start[1], end[0], end[1], color="#94a3b8", sw=2))
        
    # Vertices data: (coords, binary label, function value F, label offset (dx, dy))
    vertices = [
        (v000, "000 (F=0)", NEG, (-48, 26)),
        (v100, "100 (F=0)", NEG, (48, 26)),
        (v010, "010 (F=0)", NEG, (-48, -16)),
        (v110, "110 (F=1)", FIELD, (48, -16)),
        (v001, "001 (F=1)", FIELD, (-48, 22)),
        (v101, "101 (F=1)", FIELD, (48, 22)),
        (v011, "011 (F=1)", FIELD, (-48, -18)),
        (v111, "111 (F=1)", FIELD, (48, -18))
    ]
    
    # Highlight the 2D subcube face R=1 (all 4 vertices are F=1)
    face_r1_poly = f'<polygon points="{v001[0]},{v001[1]} {v101[0]},{v101[1]} {v111[0]},{v111[1]} {v011[0]},{v011[1]}" fill="{FIELD}" fill-opacity="0.15" stroke="{FIELD}" stroke-width="2" stroke-dasharray="4,4"/>'
    p.append(face_r1_poly)
    
    # Highlight the 1D edge P=1, Q=1 on front face
    p.append(line(v110[0], v110[1], v111[0], v111[1], color=FIELD, sw=4))
    
    for (cx, cy), label, col, (ldx, ldy) in vertices:
        p.append(circle(cx, cy, 14, fill=col, stroke="#ffffff", sw=2.5))
        p.append(text(cx, cy + 4, "1" if col == FIELD else "0", size=12, bold=True, color="#ffffff"))
        p.append(text(cx + ldx, cy + ldy, label, size=12, bold=True, color=INK))
        
    # Legend box
    p.append(rect(40, 370, 230, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(circle(65, 395, 10, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(text(85, 400, "F = 1 (істинні мінтерми)", size=12, anchor="start", color=INK))
    p.append(circle(65, 425, 10, fill=NEG, stroke="#ffffff", sw=1.5))
    p.append(text(85, 430, "F = 0 (хибні мінтерми)", size=12, anchor="start", color=INK))
    
    # Annotation box on right
    p.append(rect(480, 370, 240, 80, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(600, 395, "Склеювання граней:", size=12, bold=True, anchor="middle", color=INK))
    p.append(text(600, 415, "Грань R=1 покриває 4 вершини", size=11, anchor="middle", color=MUTED))
    p.append(text(600, 435, "Ребро P·Q покриває 110 та 111", size=11, anchor="middle", color=MUTED))

    render(os.path.join(OUT, "fig-hypercube.svg"), W, H, *p)

def fig_karnaugh():
    W, H = 760, 460
    p = []
    
    p.append(text(W / 2, 28, "Карта Карно для 4 змінних: мінімізація склеюванням підкубів", size=15, bold=True, color=INK))
    
    ox, oy = 210, 100
    cs = 64 # cell size
    
    # Headers
    p.append(text(ox - 50, oy - 25, "AB \\ CD", size=13, bold=True, color=INK))
    
    cols = ["00", "01", "11", "10"]
    rows = ["00", "01", "11", "10"]
    
    for j, c in enumerate(cols):
        p.append(text(ox + j * cs + cs / 2, oy - 15, c, size=13, bold=True, color=INK))
        
    for i, r in enumerate(rows):
        p.append(text(ox - 30, oy + i * cs + cs / 2 + 5, r, size=13, bold=True, color=INK))
        
    grid_vals = [
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 1]
    ]
    
    # Draw table container rect
    p.append(rect(ox, oy, 4 * cs, 4 * cs, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=0))
    
    # Grid internal lines
    for k in range(1, 4):
        p.append(line(ox + k * cs, oy, ox + k * cs, oy + 4 * cs, color="#e2e8f0", sw=1.2))
        p.append(line(ox, oy + k * cs, ox + 4 * cs, oy + k * cs, color="#e2e8f0", sw=1.2))
        
    # Cell values
    for i in range(4):
        for j in range(4):
            x = ox + j * cs
            y = oy + i * cs
            val = grid_vals[i][j]
            p.append(text(x + cs / 2, y + cs / 2 + 6, str(val), size=16, bold=True, color=FIELD if val == 1 else MUTED))
            
    # Group 1 (A · D): 2x2 block at rows AB={11, 10}, cols CD={01, 11}
    gx1 = ox + 1 * cs + 4
    gy1 = oy + 2 * cs + 4
    gw1 = 2 * cs - 8
    gh1 = 2 * cs - 8
    p.append(f'<rect x="{gx1:.1f}" y="{gy1:.1f}" width="{gw1:.1f}" height="{gh1:.1f}" rx="10" fill="none" stroke="{FIELD}" stroke-width="3" stroke-dasharray="6,3"/>')
    
    # Group 2 (¬B · C · ¬D): 2x1 block wrapped at rows AB={00, 10}, col CD={10}
    gx2_top = ox + 3 * cs + 5
    gy2_top = oy + 0 * cs + 5
    p.append(f'<rect x="{gx2_top:.1f}" y="{gy2_top:.1f}" width="{cs - 10:.1f}" height="{cs - 10:.1f}" rx="8" fill="none" stroke="{POS}" stroke-width="3" stroke-dasharray="4,3"/>')
    
    gx2_bot = ox + 3 * cs + 5
    gy2_bot = oy + 3 * cs + 5
    p.append(f'<rect x="{gx2_bot:.1f}" y="{gy2_bot:.1f}" width="{cs - 10:.1f}" height="{cs - 10:.1f}" rx="8" fill="none" stroke="{POS}" stroke-width="3" stroke-dasharray="4,3"/>')
    
    # Explanatory Callouts
    p.append(rect(490, 130, 240, 90, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(610, 155, "Імпліканта 1: A · D", size=13, bold=True, color=FIELD))
    p.append(text(610, 178, "Квадрат 2×2 (4 клітинки)", size=11, color=INK))
    p.append(text(610, 198, "B та C склеюються (зникають)", size=11, color=MUTED))
    
    p.append(rect(490, 245, 240, 90, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    p.append(text(610, 270, "Імпліканта 2: ¬B · C · ¬D", size=13, bold=True, color=POS))
    p.append(text(610, 293, "Крайні клітинки по вертикалі", size=11, color=INK))
    p.append(text(610, 313, "A склеюється: 00_10 та 10_10", size=11, color=MUTED))
    
    p.append(rect(80, 380, 600, 60, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(380, 405, "Мінімізована ДНФ: F = A · D ∨ ¬B · C · ¬D", size=14, bold=True, color=INK))
    p.append(text(380, 425, "Сусідні клітинки відрізняються рівно в одному біті завдяки коду Грея", size=11, color=MUTED))

    render(os.path.join(OUT, "fig-karnaugh.svg"), W, H, *p)

def fig_post_classes():
    W, H = 760, 460
    p = []
    
    p.append(text(W / 2, 28, "5 замкнених класів Поста та критерій функціональної повноти", size=15, bold=True, color=INK))
    
    classes = [
        ("T0: Збереження 0", "f(0,...,0) = 0", ["AND", "OR", "XOR"], 60, 80),
        ("T1: Збереження 1", "f(1,...,1) = 1", ["AND", "OR", "XNOR"], 290, 80),
        ("S: Самодвоїстість", "¬f(¬x) = f(x)", ["NOT"], 520, 80),
        ("M: Монотонність", "x ≤ y ⇒ f(x) ≤ f(y)", ["AND", "OR", "0", "1"], 170, 210),
        ("L: Лінійність", "f = a0 ⊕ a1 x1 ...", ["NOT", "XOR", "XNOR"], 400, 210)
    ]
    
    for title_txt, def_txt, ops, bx, by in classes:
        p.append(rect(bx, by, 200, 105, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
        p.append(text(bx + 100, by + 24, title_txt, size=12, bold=True, color=INK))
        p.append(text(bx + 100, by + 48, def_txt, size=11, color=MUTED))
        ops_str = "Належать: " + ", ".join(ops)
        p.append(text(bx + 100, by + 74, ops_str, size=11, bold=True, color=NEG))
        
    p.append(rect(60, 340, 640, 95, fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    p.append(text(380, 368, "Універсальні одноелементні базиси: Штрих Шеффера (NAND) та Стрілка Пірса (NOR)", size=14, bold=True, color=FIELD))
    p.append(text(380, 395, "NAND ∉ T0, NAND ∉ T1, NAND ∉ S, NAND ∉ M, NAND ∉ L  ⇒  Повний базис!", size=12, bold=True, color=INK))
    p.append(text(380, 418, "NOR ∉ T0, NOR ∉ T1, NOR ∉ S, NOR ∉ M, NOR ∉ L   ⇒  Повний базис!", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "fig-post-classes.svg"), W, H, *p)

if __name__ == "__main__":
    fig_hypercube()
    fig_karnaugh()
    fig_post_classes()
    print("[OK] Generated all truth-tables SVG figures.")
