import sys
import os

# Додаємо шлях до scripts/ у E:\develop\courses
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def generate_svg():
    os.makedirs('img', exist_ok=True)
    frags = []
    
    # Додаємо заголовок
    frags.append(text(400, 30, "Число Фробеніуса (a=3, b=5)", size=20, bold=True))
    
    # Малюємо числа від 0 до 15
    # Недосяжні: 1, 2, 4, 7 (червоні, без заливки)
    # Досяжні: зелені або сині
    unreachable = {1, 2, 4, 7}
    
    x_start = 50
    y_start = 100
    w = 40
    h = 40
    
    for i in range(16):
        row = i // 8
        col = i % 8
        cx = x_start + col * 90
        cy = y_start + row * 90
        
        if i in unreachable:
            fill_color = "#ffebee"
            stroke_color = POS
        else:
            fill_color = "#e8f5e9"
            stroke_color = FIELD
            
        frags.append(circle(cx, cy, 25, fill=fill_color, stroke=stroke_color, sw=2))
        frags.append(text(cx, cy + 5, str(i), size=18, bold=True))
        
        if i == 7:
            # Вказуємо на число Фробеніуса
            frags.append(arrow(cx, cy + 40, cx, cy + 30, color=POS, sw=2))
            t_box, _, _ = textbox(cx, cy + 60, "g(3,5) = 7", size=14, pad=5, stroke=POS, color=POS, bold=True)
            frags.append(t_box)

    render("img/fig-sylvester-frobenius.svg", 800, 300, *frags)
    print("SVG generated successfully at img/fig-sylvester-frobenius.svg")

if __name__ == '__main__':
    generate_svg()
