import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)

def fig_express_lane():
    """Ідея багаторівневих експрес-смуг над зв'язаним списком."""
    w, h = 900, 320
    frags = []
    
    frags.append(text(w/2, 28, "Ідея багаторівневої навігації: прискорення лінійного списку", size=16, bold=True))
    
    levels = [
        ("Рівень 2 (експрес 4×)", 90, [1, 9, 17, 25]),
        ("Рівень 1 (експрес 2×)", 170, [1, 5, 9, 13, 17, 21, 25]),
        ("Рівень 0 (базовий список)", 250, [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25])
    ]
    
    all_keys = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
    x_map = {k: 240 + i * 50 for i, k in enumerate(all_keys)}
    
    for lbl, y, keys in levels:
        frags.append(text(30, y + 5, lbl, size=13, color=MUTED, anchor="start", bold=True))
        for i in range(len(keys) - 1):
            k1, k2 = keys[i], keys[i+1]
            x1, x2 = x_map[k1], x_map[k2]
            frags.append(line(x1 + 18, y, x2 - 18, y, color=LINE, sw=1.5))
            frags.append(arrow(x2 - 25, y, x2 - 18, y, color=LINE, sw=1.5))
        
        for k in keys:
            cx = x_map[k]
            is_search = k in [1, 9, 17] and ((y == 90 and k in [1, 9]) or (y == 90 and k == 17) or (y == 170 and k == 17) or (y == 250 and k == 17))
            fill_c = "#eaf0fd" if is_search else FILL
            stroke_c = NEG if is_search else LINE
            sw_val = 2.0 if is_search else 1.5
            frags.append(rect(cx - 18, y - 16, 36, 32, fill=fill_c, stroke=stroke_c, sw=sw_val, rx=5))
            frags.append(text(cx, y + 5, str(k), size=13, color=INK, bold=True))
            
    for k in all_keys:
        cx = x_map[k]
        present_y = [y for _, y, keys in levels if k in keys]
        for i in range(len(present_y) - 1):
            y1, y2 = present_y[i], present_y[i+1]
            frags.append(line(cx, y1 + 16, cx, y2 - 16, color=MUTED, sw=1.2, dash="3,3"))

    frags.append(line(x_map[1] + 18, 80, x_map[9] - 18, 80, color=POS, sw=2.5))
    frags.append(arrow(x_map[9] - 25, 80, x_map[9] - 18, 80, color=POS, sw=2.5))
    frags.append(line(x_map[9] + 18, 80, x_map[17] - 18, 80, color=POS, sw=2.5))
    frags.append(arrow(x_map[17] - 25, 80, x_map[17] - 18, 80, color=POS, sw=2.5))
    
    frags.append(text(x_map[9], 68, "Пошук 17: крок через 8 елементів", size=11, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "express-lane-intuition.svg"), w, h, *frags)

def fig_skip_list_structure():
    """Анатомія вузлів та покажчиків forward[level] у Skip List."""
    w, h = 920, 360
    frags = []
    
    frags.append(text(w/2, 28, "Анатомія пропускного списку: вежі покажчиків forward[i]", size=16, bold=True))
    
    nodes = [
        ("HEAD", 4, 90),
        ("12", 2, 240),
        ("17", 1, 370),
        ("25", 4, 500),
        ("31", 2, 630),
        ("42", 3, 760),
        ("NIL", 4, 880)
    ]
    
    cell_h = 32
    base_y = 280
    
    for key, height, cx in nodes:
        is_nil = (key == "NIL")
        is_head = (key == "HEAD")
        
        box_w = 64 if is_head or is_nil else 54
        
        k_fill = "#e0e7ff" if is_head else ("#f3f4f6" if is_nil else "#fef3c7")
        k_stroke = NEG if is_head else (MUTED if is_nil else "#d97706")
        frags.append(rect(cx - box_w/2, base_y, box_w, 26, fill=k_fill, stroke=k_stroke, sw=1.5, rx=4))
        frags.append(text(cx, base_y + 17, key, size=12, bold=True, color=INK))
        
        for lvl in range(height):
            cy = base_y - 20 - lvl * cell_h
            c_fill = "#ffffff"
            frags.append(rect(cx - box_w/2, cy - cell_h/2, box_w, cell_h - 4, fill=c_fill, stroke=LINE, sw=1.3, rx=3))
            frags.append(text(cx - 8, cy + 4, f"fwd[{lvl}]", size=10, color=MUTED))
            frags.append(circle(cx + box_w/2 - 12, cy, 3, fill=NEG, stroke=NEG, sw=1))

    level_links = [
        [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
        [(0, 1), (1, 3), (3, 4), (4, 5), (5, 6)],
        [(0, 3), (3, 5), (5, 6)],
        [(0, 3), (3, 6)]
    ]
    
    for lvl, links in enumerate(level_links):
        cy = base_y - 20 - lvl * cell_h
        for src_idx, dst_idx in links:
            src_node = nodes[src_idx]
            dst_node = nodes[dst_idx]
            src_w = 64 if src_node[0] in ["HEAD", "NIL"] else 54
            dst_w = 64 if dst_node[0] in ["HEAD", "NIL"] else 54
            
            x1 = src_node[2] + src_w/2 - 12
            x2 = dst_node[2] - dst_w/2
            frags.append(line(x1, cy, x2, cy, color=LINE, sw=1.4))
            frags.append(arrow(x2 - 7, cy, x2, cy, color=LINE, sw=1.4))
            
    for lvl in range(4):
        cy = base_y - 20 - lvl * cell_h
        frags.append(text(25, cy + 4, f"Рівень {lvl}", size=11, bold=True, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "skip-list-structure.svg"), w, h, *frags)

def fig_search_path():
    """Траєкторія пошуку елемента у Skip List: рух управо та спуск униз."""
    w, h = 900, 360
    frags = []
    
    frags.append(text(w/2, 28, "Траєкторія пошуку ключа 31: спуск униз при перевищенні", size=16, bold=True))
    
    nodes = [
        ("HEAD", 4, 90),
        ("7", 1, 230),
        ("19", 3, 370),
        ("26", 2, 510),
        ("31", 4, 650),
        ("45", 2, 790),
        ("NIL", 4, 880)
    ]
    
    cell_h = 32
    base_y = 280
    
    for key, height, cx in nodes:
        is_nil = (key == "NIL")
        is_head = (key == "HEAD")
        box_w = 60 if is_head or is_nil else 50
        
        is_target = (key == "31")
        k_fill = "#d1fae5" if is_target else ("#e0e7ff" if is_head else ("#f3f4f6" if is_nil else "#fef3c7"))
        k_stroke = FIELD if is_target else (NEG if is_head else (MUTED if is_nil else "#d97706"))
        frags.append(rect(cx - box_w/2, base_y, box_w, 26, fill=k_fill, stroke=k_stroke, sw=1.5, rx=4))
        frags.append(text(cx, base_y + 17, key, size=12, bold=True, color=INK))
        
        for lvl in range(height):
            cy = base_y - 20 - lvl * cell_h
            frags.append(rect(cx - box_w/2, cy - cell_h/2, box_w, cell_h - 4, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
            frags.append(circle(cx + box_w/2 - 10, cy, 2.5, fill=NEG, stroke=NEG, sw=1))

    level_links = [
        [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
        [(0, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
        [(0, 2), (2, 4), (4, 6)],
        [(0, 4), (4, 6)]
    ]
    for lvl, links in enumerate(level_links):
        cy = base_y - 20 - lvl * cell_h
        for src_idx, dst_idx in links:
            x1 = nodes[src_idx][2] + (30 if nodes[src_idx][0] in ["HEAD","NIL"] else 25) - 10
            x2 = nodes[dst_idx][2] - (30 if nodes[dst_idx][0] in ["HEAD","NIL"] else 25)
            frags.append(line(x1, cy, x2, cy, color="#d1d5db", sw=1.2))

    path_points = [
        (90, base_y - 20 - 3*cell_h),   # HEAD L3
        (90, base_y - 20 - 2*cell_h),   # HEAD L2 (спуск)
        (370, base_y - 20 - 2*cell_h),  # 19 L2 (праворуч)
        (370, base_y - 20 - 1*cell_h),  # 19 L1 (спуск)
        (510, base_y - 20 - 1*cell_h),  # 26 L1 (праворуч)
        (510, base_y - 20 - 0*cell_h),  # 26 L0 (спуск)
        (650, base_y - 20 - 0*cell_h),  # 31 L0 (праворуч -> успіх)
    ]
    
    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i+1]
        is_down = (x1 == x2)
        c = POS if is_down else FIELD
        frags.append(line(x1, y1, x2, y2, color=c, sw=2.8))
        frags.append(arrow(x2 - (5 if not is_down else 0), y2 - (5 if is_down else 0), x2, y2, color=c, sw=2.8))

    frags.append(rect(140, 70, 240, 48, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    frags.append(text(260, 90, "Червоний: спуск униз (next ≥ key)", size=11, color=POS, bold=True))
    frags.append(text(260, 106, "Зелений: крок управо (next < key)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "search-path.svg"), w, h, *frags)

def fig_insert_update():
    """Вставка нового вузла: масив update[] та локальне перечіплення покажчиків."""
    w, h = 900, 360
    frags = []
    
    frags.append(text(w/2, 28, "Вставка вузла 22 (висота 3): роль масиву попередників update[]", size=16, bold=True))
    
    nodes = [
        ("HEAD", 4, 90),
        ("10", 2, 240),
        ("17", 4, 390),
        ("22", 3, 540), # Новий вузол
        ("35", 3, 690),
        ("NIL", 4, 840)
    ]
    
    cell_h = 32
    base_y = 280
    
    for idx, (key, height, cx) in enumerate(nodes):
        if key == "22":
            continue
        box_w = 60 if key in ["HEAD", "NIL"] else 52
        frags.append(rect(cx - box_w/2, base_y, box_w, 26, fill="#f3f4f6", stroke=LINE, sw=1.5, rx=4))
        frags.append(text(cx, base_y + 17, key, size=12, bold=True, color=INK))
        
        for lvl in range(height):
            cy = base_y - 20 - lvl * cell_h
            is_upd = (key == "17") or (key == "HEAD" and lvl == 3)
            fill_c = "#e0e7ff" if is_upd else "#ffffff"
            frags.append(rect(cx - box_w/2, cy - cell_h/2, box_w, cell_h - 4, fill=fill_c, stroke=NEG if is_upd else LINE, sw=1.5 if is_upd else 1.2, rx=3))
            frags.append(circle(cx + box_w/2 - 10, cy, 2.5, fill=NEG, stroke=NEG, sw=1))

    cx_new = 540
    frags.append(rect(cx_new - 26, base_y, 52, 26, fill="#fef3c7", stroke="#d97706", sw=2, rx=4))
    frags.append(text(cx_new, base_y + 17, "22", size=12, bold=True, color="#b45309"))
    frags.append(text(cx_new, base_y + 44, "новий вузол", size=11, color="#b45309", bold=True))
    
    for lvl in range(3):
        cy = base_y - 20 - lvl * cell_h
        frags.append(rect(cx_new - 26, cy - cell_h/2, 52, cell_h - 4, fill="#fef9c3", stroke="#d97706", sw=1.8, rx=3))
        frags.append(circle(cx_new + 16, cy, 3, fill=POS, stroke=POS, sw=1))
        
        frags.append(line(cx_new + 16, cy, 690 - 26, cy, color=FIELD, sw=2))
        frags.append(arrow(690 - 33, cy, 690 - 26, cy, color=FIELD, sw=2))
        
        frags.append(line(390 + 16, cy, cx_new - 26, cy, color=POS, sw=2))
        frags.append(arrow(cx_new - 33, cy, cx_new - 26, cy, color=POS, sw=2))

    frags.append(rect(60, 60, 240, 52, fill="#eef2ff", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(180, 80, "update[0..2] = вузол 17", size=12, color=NEG, bold=True))
    frags.append(text(180, 98, "Перечіплюються лише 3 покажчики!", size=11, color=INK))

    render(os.path.join(OUT_DIR, "insert-update-pointers.svg"), w, h, *frags)

def fig_concurrent_isolation():
    """Порівняння конкурентності: блокування піддерева в AVL/RB проти CAS у Skip List."""
    w, h = 920, 320
    frags = []
    
    frags.append(text(w/2, 28, "Конкурентність: локальна модифікація проти каскадних поворотів", size=16, bold=True))
    
    frags.append(rect(30, 60, 410, 240, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(235, 88, "Збалансоване дерево (AVL / Червоно-чорне)", size=13, color=POS, bold=True))
    
    frags.append(circle(235, 125, 16, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(235, 130, "A", size=11, bold=True))
    
    frags.append(circle(175, 180, 16, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(175, 185, "B", size=11, bold=True))
    
    frags.append(circle(295, 180, 16, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(295, 185, "C", size=11, bold=True))
    
    frags.append(line(223, 137, 187, 168, color=POS, sw=1.5))
    frags.append(line(247, 137, 283, 168, color=POS, sw=1.5))
    
    frags.append(rect(145, 215, 180, 70, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(235, 235, "Каскадний поворот:", size=11, color=POS, bold=True))
    frags.append(text(235, 252, "Блокує шлях від листка до кореня.", size=10, color=INK))
    frags.append(text(235, 268, "Потоки чекають глобального замка.", size=10, color=MUTED))

    frags.append(rect(480, 60, 410, 240, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(685, 88, "Пропускний список (Skip List)", size=13, color=FIELD, bold=True))
    
    for i, name in enumerate(["P", "New", "N"]):
        cx = 560 + i * 125
        frags.append(rect(cx - 24, 135, 48, 50, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
        frags.append(text(cx, 164, name, size=11, bold=True))
        if i < 2:
            frags.append(line(cx + 24, 155, cx + 101, 155, color=FIELD, sw=1.8))
            frags.append(arrow(cx + 94, 155, cx + 101, 155, color=FIELD, sw=1.8))

    frags.append(rect(525, 215, 320, 70, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(685, 235, "Локальна атомарна вставка (CAS):", size=11, color=FIELD, bold=True))
    frags.append(text(685, 252, "Оновлює лише покажчики сусіда на кожному рівні.", size=10, color=INK))
    frags.append(text(685, 268, "Інші гілки списку читаються паралельно без блокувань.", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "concurrent-isolation.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_express_lane()
    fig_skip_list_structure()
    fig_search_path()
    fig_insert_update()
    fig_concurrent_isolation()
    print("All figures generated successfully.")
