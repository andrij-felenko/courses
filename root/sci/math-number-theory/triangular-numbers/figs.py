import sys
import os

# sys.path setup to include scripts directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, circle, text, POS, NEG, INK

def draw_dot_triangle_building():
    frags = []
    
    configs = [
        (1, 60, "T₁ = 1"),
        (2, 180, "T₂ = 3"),
        (3, 330, "T₃ = 6"),
        (4, 500, "T₄ = 10"),
    ]
    
    dot_r = 7
    spacing_x = 22
    spacing_y = 20
    
    for n, base_x, label in configs:
        start_y = 50
        for r in range(1, n + 1):
            row_y = start_y + (r - 1) * spacing_y
            row_count = r
            row_start_x = base_x - (row_count - 1) * spacing_x / 2.0
            for c in range(row_count):
                cx = row_start_x + c * spacing_x
                color = POS if r == n else NEG
                frags.append(circle(cx, row_y, dot_r, fill=color, stroke=INK, sw=1.2))
        
        label_y = start_y + n * spacing_y + 18
        frags.append(text(base_x, label_y, label, size=15, bold=True, color=INK))
        if n > 1:
            diff_text = f"+{n}"
            frags.append(text(base_x, label_y + 20, diff_text, size=13, italic=True, color=POS))
            
    os.makedirs('img', exist_ok=True)
    render('img/dot-triangle-building.svg', 600, 210, *frags, title="Побудова трикутних чисел додаванням рядків")

def draw_doubling_rectangle():
    frags = []
    
    n = 5
    spacing = 26
    dot_r = 8
    
    offset_x = 80
    offset_y = 50
    
    for r in range(n):
        for c in range(n + 1):
            cx = offset_x + c * spacing
            cy = offset_y + r * spacing
            
            if c <= r:
                color = NEG
            else:
                color = POS
            frags.append(circle(cx, cy, dot_r, fill=color, stroke=INK, sw=1.2))
            
    frags.append(text(offset_x + (n * spacing) / 2.0, offset_y - 20, f"n + 1 = {n + 1} стовпчиків", size=14, bold=True, color=INK))
    frags.append(text(offset_x + (n + 1) * spacing + 45, offset_y + ((n - 1) * spacing) / 2.0, f"n = {n} рядків", size=14, bold=True, color=INK))
    
    frags.append(text(280, offset_y + n * spacing + 25, f"2 · T₅ = 5 · 6 = 30   ⇒   T₅ = 15", size=16, bold=True, color=INK))
    
    os.makedirs('img', exist_ok=True)
    render('img/doubling-rectangle.svg', 580, 230, *frags, title="Подвоєння трикутника до прямокутника n × (n+1)")

def draw_consecutive_triangles_square():
    frags = []
    
    n = 4
    spacing = 30
    dot_r = 9
    
    start_x = 80
    start_y = 50
    
    for r in range(n):
        for c in range(n):
            cx = start_x + c * spacing
            cy = start_y + r * spacing
            
            if c <= r:
                color = POS
            else:
                color = NEG
            frags.append(circle(cx, cy, dot_r, fill=color, stroke=INK, sw=1.2))
            
    frags.append(text(start_x + (n - 1) * spacing / 2.0, start_y - 20, f"n = {n} (ширина)", size=14, bold=True, color=INK))
    
    info_x = start_x + n * spacing + 40
    info_y = start_y + 15
    frags.append(text(info_x, info_y, "T₃ = 6 (сині точки)", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(info_x, info_y + 28, "T₄ = 10 (червоні точки)", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(info_x, info_y + 65, "T₃ + T₄ = 6 + 10 = 16 = 4²", size=16, bold=True, color=INK, anchor="start"))
    
    os.makedirs('img', exist_ok=True)
    render('img/consecutive-triangles-square.svg', 540, 200, *frags, title="Сума двох сусідніх трикутних чисел утворює квадрат")

if __name__ == '__main__':
    draw_dot_triangle_building()
    draw_doubling_rectangle()
    draw_consecutive_triangles_square()
