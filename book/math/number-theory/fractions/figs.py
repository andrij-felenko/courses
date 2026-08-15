import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, mtext, textbox, POS, NEG, FIELD, INK, MUTED, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)


def draw_equivalence_classes():
    frags = []
    
    # Dimensions
    w, h = 640, 430
    ox, oy = 90, 360
    scale_x, scale_y = 60, 60
    
    # Background grid
    for i in range(1, 9):
        x = ox + i * scale_x
        frags.append(line(x, 50, x, oy + 15, color="#e5e7eb", sw=1.0))
        frags.append(text(x, oy + 22, str(i), size=12, color=MUTED))
        
    for j in range(1, 6):
        y = oy - j * scale_y
        frags.append(line(ox + 5, y, ox + 8 * scale_x, y, color="#e5e7eb", sw=1.0))
        frags.append(text(ox - 20, y + 4, str(j), size=12, color=MUTED))
        
    # Axes
    frags.append(arrow(ox, oy, ox + 8.5 * scale_x, oy, color=INK, sw=1.8))
    frags.append(text(ox + 8.5 * scale_x + 10, oy + 4, "b (знаменник)", size=13, color=INK, bold=True, anchor="start"))
    
    frags.append(arrow(ox, oy, ox, 25, color=INK, sw=1.8))
    frags.append(text(ox, 12, "a (чисельник)", size=13, color=INK, bold=True, anchor="middle"))
    
    frags.append(text(ox - 15, oy + 18, "0", size=12, color=MUTED))
    
    # Rays of equivalence classes
    ray1_end_x = ox + 8 * scale_x
    ray1_end_y = oy - 4 * scale_y
    frags.append(line(ox, oy, ray1_end_x, ray1_end_y, color=NEG, sw=2.0, dash="5,3"))
    frags.append(text(ray1_end_x + 8, ray1_end_y + 4, "Клас [1/2]", size=13, color=NEG, bold=True, anchor="start"))
    
    ray2_end_x = ox + 7.5 * scale_x
    ray2_end_y = oy - 5 * scale_y
    frags.append(line(ox, oy, ray2_end_x, ray2_end_y, color=POS, sw=2.0, dash="5,3"))
    frags.append(text(ray2_end_x + 8, ray2_end_y - 2, "Клас [2/3]", size=13, color=POS, bold=True, anchor="start"))
    
    # Points on Ray 1 (1/2)
    p1_x, p1_y = ox + 2 * scale_x, oy - 1 * scale_y
    frags.append(circle(p1_x, p1_y, 7, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(p1_x, p1_y - 12, "(2, 1) ⇒ 1/2 (нескоротний)", size=12, color=INK, bold=True))
    
    p2_x, p2_y = ox + 4 * scale_x, oy - 2 * scale_y
    frags.append(circle(p2_x, p2_y, 6, fill=FILL, stroke=NEG, sw=1.5))
    frags.append(text(p2_x, p2_y - 11, "(4, 2) ⇒ 2/4", size=12, color=INK))
    
    p3_x, p3_y = ox + 6 * scale_x, oy - 3 * scale_y
    frags.append(circle(p3_x, p3_y, 6, fill=FILL, stroke=NEG, sw=1.5))
    frags.append(text(p3_x, p3_y - 11, "(6, 3) ⇒ 3/6", size=12, color=INK))
    
    # Points on Ray 2 (2/3)
    r1_x, r1_y = ox + 3 * scale_x, oy - 2 * scale_y
    frags.append(circle(r1_x, r1_y, 7, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(r1_x + 15, r1_y + 14, "(3, 2) ⇒ 2/3 (нескоротний)", size=12, color=INK, bold=True, anchor="start"))
    
    r2_x, r2_y = ox + 6 * scale_x, oy - 4 * scale_y
    frags.append(circle(r2_x, r2_y, 6, fill=FILL, stroke=POS, sw=1.5))
    frags.append(text(r2_x, r2_y - 11, "(6, 4) ⇒ 4/6", size=12, color=INK))
    
    # Legend box
    leg_box, _, _ = textbox(210, 75, "Класи еквівалентності дробів (a, b) ~ (c, d):\n"
                                     "• Точка ґратки (b, a) відповідає дробу a/b\n"
                                     "• Усі точки на одному промені рівні\n"
                                     "• Зелена точка — канонічний нескоротний дріб",
                            size=12, fill=BG, stroke="#cbd5e1", pad=8, min_w=280)
    frags.append(leg_box)
    
    os.makedirs('img', exist_ok=True)
    render('img/fig-equivalence-classes.svg', w, h, *frags, title="Класи еквівалентності звичайних дробів")


def draw_farey_stern_brocot():
    frags = []
    w, h = 660, 380
    
    nodes = [
        {"id": "L0", "x": 60, "y": 60, "val": "0/1", "bg": FILL, "stroke": MUTED},
        {"id": "R0", "x": 600, "y": 60, "val": "1/1", "bg": FILL, "stroke": MUTED},
        
        {"id": "M1", "x": 330, "y": 120, "val": "1/2", "bg": FIELD, "stroke": INK},
        
        {"id": "M2_1", "x": 195, "y": 200, "val": "1/3", "bg": FILL, "stroke": NEG},
        {"id": "M2_2", "x": 465, "y": 200, "val": "2/3", "bg": FILL, "stroke": POS},
        
        {"id": "M3_1", "x": 125, "y": 290, "val": "1/4", "bg": BG, "stroke": MUTED},
        {"id": "M3_2", "x": 265, "y": 290, "val": "2/5", "bg": BG, "stroke": MUTED},
        {"id": "M3_3", "x": 395, "y": 290, "val": "3/5", "bg": BG, "stroke": MUTED},
        {"id": "M3_4", "x": 535, "y": 290, "val": "3/4", "bg": BG, "stroke": MUTED},
    ]
    
    edges = [
        ("L0", "M1"), ("R0", "M1"),
        ("L0", "M2_1"), ("M1", "M2_1"),
        ("M1", "M2_2"), ("R0", "M2_2"),
        ("L0", "M3_1"), ("M2_1", "M3_1"),
        ("M2_1", "M3_2"), ("M1", "M3_2"),
        ("M1", "M3_3"), ("M2_2", "M3_3"),
        ("M2_2", "M3_4"), ("R0", "M3_4"),
    ]
    
    node_dict = {n["id"]: n for n in nodes}
    
    for src_id, dst_id in edges:
        src = node_dict[src_id]
        dst = node_dict[dst_id]
        frags.append(line(src["x"], src["y"], dst["x"], dst["y"], color="#cbd5e1", sw=1.5))
        
    for n in nodes:
        tb, _, _ = textbox(n["x"], n["y"], n["val"], size=13, pad=6, fill=n["bg"], stroke=n["stroke"], rx=5, bold=True)
        frags.append(tb)
        
    frags.append(text(20, 60, "Рівень 0:", size=12, color=MUTED, anchor="start"))
    frags.append(text(20, 120, "Рівень 1:", size=12, color=MUTED, anchor="start"))
    frags.append(text(20, 200, "Рівень 2:", size=12, color=MUTED, anchor="start"))
    frags.append(text(20, 290, "Рівень 3:", size=12, color=MUTED, anchor="start"))
    
    expl_box, _, _ = textbox(330, 345, "Формула медіанти: m(a/b, c/d) = (a + c) / (b + d)\n"
                                       "Кожен новий дріб створюється між двома батьківськими дробів",
                             size=12, fill=BG, stroke=FIELD, pad=7, min_w=480)
    frags.append(expl_box)
    
    os.makedirs('img', exist_ok=True)
    render('img/fig-farey-stern-brocot.svg', w, h, *frags, title="Дерево Штерна-Броко та обчислення медіант")


def draw_repeating_decimal_cycle():
    frags = []
    w, h = 620, 360
    
    import math
    cx, cy = 310, 170
    radius = 110
    
    remainders = [
        {"rem": "1", "digit": "1"},
        {"rem": "3", "digit": "4"},
        {"rem": "2", "digit": "2"},
        {"rem": "6", "digit": "8"},
        {"rem": "4", "digit": "5"},
        {"rem": "5", "digit": "7"},
    ]
    
    n_pts = len(remainders)
    pos = []
    for i in range(n_pts):
        angle = -math.pi / 2 + i * (2 * math.pi / n_pts)
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        pos.append((px, py))
        
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        x1, y1 = pos[i]
        x2, y2 = pos[next_i]
        
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        v_x, v_y = mx - cx, my - cy
        v_len = math.sqrt(v_x**2 + v_y**2)
        curve_x = mx + (v_x / v_len) * 20
        curve_y = my + (v_y / v_len) * 20
        
        frags.append(arrow(x1, y1, curve_x, curve_y, color=NEG, sw=1.6))
        frags.append(arrow(curve_x, curve_y, x2, y2, color=NEG, sw=1.6))
        
        frags.append(text(curve_x, curve_y, f"цифра '{remainders[i]['digit']}'", size=11, color=POS, bold=True))
        
    for i in range(n_pts):
        px, py = pos[i]
        rem_str = remainders[i]["rem"]
        node_fill = FIELD if rem_str == "1" else FILL
        tb, _, _ = textbox(px, py, f"r = {rem_str}", size=13, fill=node_fill, stroke=INK, pad=5, bold=True)
        frags.append(tb)
        
    sum_box, _, _ = textbox(cx, 320, "Ділення 1/7 = 0.142857142857... (Період T = 6)\n"
                                     "Остачі r ∈ {1, 3, 2, 6, 4, 5} утворюють зациклений граф станів. Довжина періоду T = ord_7(10) = 6.",
                            size=12, fill=BG, stroke="#94a3b8", pad=8, min_w=520)
    frags.append(sum_box)
    
    os.makedirs('img', exist_ok=True)
    render('img/fig-repeating-decimal-cycle.svg', w, h, *frags, title="Цикл остач ділення для періодичного десяткового дробу")


if __name__ == '__main__':
    draw_equivalence_classes()
    draw_farey_stern_brocot()
    draw_repeating_decimal_cycle()
    print("Figures generated successfully.")
