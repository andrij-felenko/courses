import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG, INK, MUTED, FIELD, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_floor_ceiling_step():
    frags = []
    
    # Title
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Східчасті функції підлоги ⌊x⌋ та стелі ⌈x⌉ у порівнянні з y = x", size=13, bold=True, color="#212529", anchor="middle"))

    # Main coordinate box
    box_x, box_y, box_w, box_h = 40, 55, 680, 250
    frags.append(rect(box_x, box_y, box_w, box_h, rx=6, fill="#ffffff", stroke="#dee2e6", sw=1.5))

    # Grid background
    cx, cy = 380, 180  # Origin (0,0)
    scale = 60         # 60 pixels per unit

    # Axis lines
    frags.append(line(box_x + 20, cy, box_x + box_w - 20, cy, color="#adb5bd", sw=1.5))
    frags.append(arrow(box_x + box_w - 30, cy, box_x + box_w - 15, cy, color="#495057", sw=1.5))
    frags.append(text(box_x + box_w - 10, cy + 4, "x", size=12, bold=True, color="#495057", anchor="start"))

    frags.append(line(cx, box_y + box_h - 15, cx, box_y + 15, color="#adb5bd", sw=1.5))
    frags.append(arrow(cx, box_y + 25, cx, box_y + 10, color="#495057", sw=1.5))
    frags.append(text(cx + 10, box_y + 15, "y", size=12, bold=True, color="#495057", anchor="start"))

    # Identity line y = x (dashed)
    frags.append(line(cx - 140, cy + 140, cx + 140, cy - 140, color="#ced4da", sw=1.5, dash="4,4"))
    frags.append(text(cx + 145, cy - 140, "y = x", size=10, italic=True, color="#868e96", anchor="start"))

    # Ticks and grid numbers
    for val in [-2, -1, 1, 2]:
        tx = cx + val * scale
        ty = cy - val * scale
        # Vertical grid line
        frags.append(line(tx, box_y + 20, tx, box_y + box_h - 20, color="#f1f3f5", sw=1.0))
        # Horizontal grid line
        frags.append(line(box_x + 20, ty, box_x + box_w - 20, ty, color="#f1f3f5", sw=1.0))

        # Axis ticks
        frags.append(line(tx, cy - 4, tx, cy + 4, color="#495057", sw=1.0))
        frags.append(text(tx, cy + 18, str(val), size=10, color="#495057", anchor="middle"))

        frags.append(line(cx - 4, ty, cx + 4, ty, color="#495057", sw=1.0))
        frags.append(text(cx - 10, ty + 4, str(val), size=10, color="#495057", anchor="end"))

    frags.append(text(cx - 8, cy + 16, "0", size=10, color="#495057", anchor="end"))

    # Floor function steps ⌊x⌋ (Blue)
    # Intervals: [-2, -1), [-1, 0), [0, 1), [1, 2)
    for k in range(-2, 3):
        x1 = cx + k * scale
        x2 = cx + (k + 1) * scale
        y_val = cy - k * scale

        if x1 >= box_x + 20 and x2 <= box_x + box_w - 20:
            # Segment
            frags.append(line(x1, y_val, x2, y_val, color="#1c7ed6", sw=2.5))
            # Filled circle at start (left-closed)
            frags.append(circle(x1, y_val, 3.5, fill="#1c7ed6", stroke="#1864ab", sw=1.0))
            # Open circle at end (right-open)
            frags.append(circle(x2, y_val, 3.5, fill="#ffffff", stroke="#1c7ed6", sw=1.5))

    # Ceiling function steps ⌈x⌉ (Red offset/dashed)
    for k in range(-2, 3):
        x1 = cx + (k - 1) * scale
        x2 = cx + k * scale
        y_val = cy - k * scale

        if x1 >= box_x + 20 and x2 <= box_x + box_w - 20:
            # Segment (dashed above floor)
            frags.append(line(x1, y_val - 3, x2, y_val - 3, color="#e03131", sw=2.0, dash="3,3"))
            # Open circle at left
            frags.append(circle(x1, y_val - 3, 3.0, fill="#ffffff", stroke="#e03131", sw=1.2))
            # Filled circle at right
            frags.append(circle(x2, y_val - 3, 3.0, fill="#e03131", stroke="#c92a2a", sw=1.0))

    # Legend
    frags.append(rect(box_x + 20, box_y + 15, 230, 48, rx=4, fill="#ffffff", stroke="#ced4da", sw=1.0))
    frags.append(line(box_x + 30, box_y + 30, box_x + 55, box_y + 30, color="#1c7ed6", sw=2.5))
    frags.append(circle(box_x + 30, box_y + 30, 3, fill="#1c7ed6"))
    frags.append(circle(box_x + 55, box_y + 30, 3, fill="#ffffff", stroke="#1c7ed6", sw=1.2))
    frags.append(text(box_x + 65, box_y + 34, "Підлога y = ⌊x⌋ (зліва включно)", size=10, bold=True, color="#1864ab", anchor="start"))

    frags.append(line(box_x + 30, box_y + 48, box_x + 55, box_y + 48, color="#e03131", sw=2.0, dash="3,3"))
    frags.append(circle(box_x + 30, box_y + 48, 3, fill="#ffffff", stroke="#e03131", sw=1.2))
    frags.append(circle(box_x + 55, box_y + 48, 3, fill="#e03131"))
    frags.append(text(box_x + 65, box_y + 52, "Стеля y = ⌈x⌉ (справа включно)", size=10, bold=True, color="#c92a2a", anchor="start"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'floor-ceiling-step.svg'), 760, 320, *frags, title="Східчасті функції підлоги та стелі")

def draw_division_models_comparison():
    frags = []
    
    # Title
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Порівняння трьох моделей ділення -7 ÷ 3", size=13, bold=True, color="#212529", anchor="middle"))

    # Three model boxes
    models = [
        ("Усічення (Truncated / C99 / C++)", "-7 / 3 = -2  (остача -1)", "Округлення до НУЛЯ (trunc)", "-2 × 3 + (-1) = -7", "#e7f5ff", "#1c7ed6", "#1864ab", -2, -1),
        ("Підлога (Floor / Python / Julia)", "-7 // 3 = -3  (остача +2)", "Округлення до -∞ (floor)", "-3 × 3 + (+2) = -7", "#e6fcf5", "#0ca678", "#099268", -3, 2),
        ("Евклідове ділення (Euclidean / Ada)", "-7 div 3 = -3  (остача +2)", "Строго невід'ємна остача 0 ≤ r < 3", "-3 × 3 + (+2) = -7", "#fff9db", "#f59f00", "#e67700", -3, 2),
    ]

    for idx, (title, formula, mode_desc, check_eq, fill_col, border_col, title_col, q_val, r_val) in enumerate(models):
        y_top = 58 + idx * 84
        frags.append(rect(40, y_top, 680, 74, rx=6, fill=fill_col, stroke=border_col, sw=1.5))
        
        # Left title & mode
        frags.append(text(55, y_top + 20, title, size=12, bold=True, color=title_col, anchor="start"))
        frags.append(text(55, y_top + 40, mode_desc, size=10, color="#495057", anchor="start"))
        frags.append(text(55, y_top + 58, check_eq, size=10, italic=True, color="#6c757d", anchor="start"))

        # Right result callout
        frags.append(rect(390, y_top + 10, 310, 54, rx=4, fill="#ffffff", stroke=border_col, sw=1.0))
        frags.append(text(545, y_top + 28, formula, size=12, bold=True, color=title_col, anchor="middle"))
        r_sign_note = "Остача має знак діленого" if r_val < 0 else "Остача завжди невід'ємна"
        frags.append(text(545, y_top + 46, r_sign_note, size=10, color="#495057", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'division-models-comparison.svg'), 760, 320, *frags, title="Моделі цілочислового ділення")

def draw_nested_floors_lattice():
    frags = []
    
    # Title
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Ієрархічне групування ⌊ ⌊x / 3⌋ / 2 ⌋ = ⌊x / 6⌋ для x ∈ [0, 11]", size=13, bold=True, color="#212529", anchor="middle"))

    # Grid of numbers 0..11
    start_x, start_y = 50, 60
    cell_w, cell_h = 55, 38

    # Row 1: Raw numbers x
    frags.append(text(start_x, start_y + 24, "Число x:", size=11, bold=True, color="#212529", anchor="start"))
    for i in range(12):
        x = start_x + 95 + i * cell_w
        frags.append(rect(x, start_y, cell_w - 4, cell_h, rx=4, fill="#f8f9fa", stroke="#dee2e6", sw=1.0))
        frags.append(text(x + cell_w/2 - 2, start_y + 24, str(i), size=11, bold=True, color="#343a40", anchor="middle"))

    # Row 2: First floor division ⌊x / 3⌋
    start_y2 = 115
    frags.append(text(start_x, start_y2 + 24, "⌊x / 3⌋:", size=11, bold=True, color="#1864ab", anchor="start"))
    blocks_a = [
        (0, 3, "0", "#e7f5ff", "#1c7ed6"),
        (3, 6, "1", "#d0ebff", "#1c7ed6"),
        (6, 9, "2", "#a5d8ff", "#1c7ed6"),
        (9, 12, "3", "#74c0fc", "#1c7ed6"),
    ]
    for b_start, b_end, val, fill_c, stroke_c in blocks_a:
        x_left = start_x + 95 + b_start * cell_w
        w_block = (b_end - b_start) * cell_w - 4
        frags.append(rect(x_left, start_y2, w_block, cell_h, rx=4, fill=fill_c, stroke=stroke_c, sw=1.5))
        frags.append(text(x_left + w_block/2, start_y2 + 24, f"значення = {val}", size=11, bold=True, color="#1864ab", anchor="middle"))

    # Row 3: Second floor division ⌊ ⌊x / 3⌋ / 2 ⌋
    start_y3 = 170
    frags.append(text(start_x, start_y3 + 24, "⌊ ⌊x/3⌋ / 2 ⌋:", size=11, bold=True, color="#c92a2a", anchor="start"))
    blocks_b = [
        (0, 6, "0", "#ffe3e3", "#e03131"),
        (6, 12, "1", "#ffc9c9", "#e03131"),
    ]
    for b_start, b_end, val, fill_c, stroke_c in blocks_b:
        x_left = start_x + 95 + b_start * cell_w
        w_block = (b_end - b_start) * cell_w - 4
        frags.append(rect(x_left, start_y3, w_block, cell_h, rx=4, fill=fill_c, stroke=stroke_c, sw=1.5))
        frags.append(text(x_left + w_block/2, start_y3 + 24, f"значення = {val}", size=11, bold=True, color="#c92a2a", anchor="middle"))

    # Row 4: Direct division ⌊x / 6⌋
    start_y4 = 225
    frags.append(text(start_x, start_y4 + 24, "Пряме ⌊x / 6⌋:", size=11, bold=True, color="#099268", anchor="start"))
    blocks_direct = [
        (0, 6, "0", "#e6fcf5", "#0ca678"),
        (6, 12, "1", "#c3fae8", "#0ca678"),
    ]
    for b_start, b_end, val, fill_c, stroke_c in blocks_direct:
        x_left = start_x + 95 + b_start * cell_w
        w_block = (b_end - b_start) * cell_w - 4
        frags.append(rect(x_left, start_y4, w_block, cell_h, rx=4, fill=fill_c, stroke=stroke_c, sw=1.5))
        frags.append(text(x_left + w_block/2, start_y4 + 24, f"значення = {val}  (ЗБІГ!)", size=11, bold=True, color="#099268", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'nested-floors-lattice.svg'), 760, 285, *frags, title="Властивість вкладених підлог")

def draw_legendre_formula_grid():
    frags = []
    
    # Title
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Обчислення v₂(12!) за формулою Лежандра: ⌊12/2⌋ + ⌊12/4⌋ + ⌊12/8⌋ = 6 + 3 + 1 = 10", size=12, bold=True, color="#212529", anchor="middle"))

    start_x, start_y = 50, 60
    cell_w, cell_h = 52, 34

    # Header numbers 1..12
    frags.append(text(start_x, start_y + 22, "Множники 1..12:", size=10, bold=True, color="#212529", anchor="start"))
    for i in range(1, 13):
        x = start_x + 100 + (i - 1) * cell_w
        frags.append(rect(x, start_y, cell_w - 4, cell_h, rx=3, fill="#f8f9fa", stroke="#dee2e6", sw=1.0))
        frags.append(text(x + cell_w/2 - 2, start_y + 22, str(i), size=11, bold=True, color="#343a40", anchor="middle"))

    # Level k=1: multiples of 2^1 = 2 (⌊12/2⌋ = 6)
    y1 = 105
    frags.append(text(start_x, y1 + 22, "k=1: ⌊12/2¹⌋ = 6", size=10, bold=True, color="#1864ab", anchor="start"))
    for i in range(1, 13):
        x = start_x + 100 + (i - 1) * cell_w
        is_mult = (i % 2 == 0)
        fill_c = "#d0ebff" if is_mult else "#ffffff"
        stroke_c = "#1c7ed6" if is_mult else "#e9ecef"
        frags.append(rect(x, y1, cell_w - 4, cell_h, rx=3, fill=fill_c, stroke=stroke_c, sw=1.2 if is_mult else 1.0))
        mark = "+1" if is_mult else "0"
        col = "#1864ab" if is_mult else "#adb5bd"
        frags.append(text(x + cell_w/2 - 2, y1 + 22, mark, size=10, bold=is_mult, color=col, anchor="middle"))

    # Level k=2: multiples of 2^2 = 4 (⌊12/4⌋ = 3)
    y2 = 148
    frags.append(text(start_x, y2 + 22, "k=2: ⌊12/2²⌋ = 3", size=10, bold=True, color="#c92a2a", anchor="start"))
    for i in range(1, 13):
        x = start_x + 100 + (i - 1) * cell_w
        is_mult = (i % 4 == 0)
        fill_c = "#ffc9c9" if is_mult else "#ffffff"
        stroke_c = "#e03131" if is_mult else "#e9ecef"
        frags.append(rect(x, y2, cell_w - 4, cell_h, rx=3, fill=fill_c, stroke=stroke_c, sw=1.2 if is_mult else 1.0))
        mark = "+1" if is_mult else "0"
        col = "#c92a2a" if is_mult else "#adb5bd"
        frags.append(text(x + cell_w/2 - 2, y2 + 22, mark, size=10, bold=is_mult, color=col, anchor="middle"))

    # Level k=3: multiples of 2^3 = 8 (⌊12/8⌋ = 1)
    y3 = 191
    frags.append(text(start_x, y3 + 22, "k=3: ⌊12/2³⌋ = 1", size=10, bold=True, color="#099268", anchor="start"))
    for i in range(1, 13):
        x = start_x + 100 + (i - 1) * cell_w
        is_mult = (i % 8 == 0)
        fill_c = "#c3fae8" if is_mult else "#ffffff"
        stroke_c = "#0ca678" if is_mult else "#e9ecef"
        frags.append(rect(x, y3, cell_w - 4, cell_h, rx=3, fill=fill_c, stroke=stroke_c, sw=1.2 if is_mult else 1.0))
        mark = "+1" if is_mult else "0"
        col = "#099268" if is_mult else "#adb5bd"
        frags.append(text(x + cell_w/2 - 2, y3 + 22, mark, size=10, bold=is_mult, color=col, anchor="middle"))

    # Total row v_2(i)
    y4 = 234
    frags.append(text(start_x, y4 + 22, "Сума v₂(i):", size=10, bold=True, color="#212529", anchor="start"))
    powers = [0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2]  # v_2(i) for i = 1..12
    for i in range(1, 13):
        x = start_x + 100 + (i - 1) * cell_w
        p = powers[i - 1]
        fill_c = "#fff9db" if p > 0 else "#ffffff"
        stroke_c = "#f59f00" if p > 0 else "#dee2e6"
        frags.append(rect(x, y4, cell_w - 4, cell_h, rx=3, fill=fill_c, stroke=stroke_c, sw=1.5 if p > 0 else 1.0))
        frags.append(text(x + cell_w/2 - 2, y4 + 22, str(p), size=11, bold=True, color="#d9480f" if p > 0 else "#868e96", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'legendre-formula-grid.svg'), 760, 285, *frags, title="Формула Лежандра для факторів простих чисел")

if __name__ == '__main__':
    draw_floor_ceiling_step()
    draw_division_models_comparison()
    draw_nested_floors_lattice()
    draw_legendre_formula_grid()
    print("Successfully generated all figures for floor-division.")
