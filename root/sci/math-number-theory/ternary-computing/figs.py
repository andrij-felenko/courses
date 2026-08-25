import os
import sys

# Додаємо шлях до scripts/svgkit.py (4 рівні вгору: ternary-computing -> number-theory -> math -> book -> courses)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def main():
    w, h = 600, 300
    
    frags = []
    
    # Заголовок
    frags.append(svgkit.text(w/2, 30, "Збалансована трійкова система (Balanced Ternary)", size=18, bold=True))
    
    # Трит
    frags.append(svgkit.text(300, 80, "Трит (Trit) = {-1, 0, +1}", size=16, color=svgkit.INK))
    
    # Малюємо значення тритів
    frags.append(svgkit.circle(200, 130, 25, fill="#eaf0fd", stroke=svgkit.NEG))
    frags.append(svgkit.text(200, 137, "−1", size=18, bold=True, color=svgkit.NEG))
    
    frags.append(svgkit.circle(300, 130, 25, fill=svgkit.FILL, stroke=svgkit.LINE))
    frags.append(svgkit.text(300, 137, "0", size=18, bold=True, color=svgkit.INK))
    
    frags.append(svgkit.circle(400, 130, 25, fill="#fdecea", stroke=svgkit.POS))
    frags.append(svgkit.text(400, 137, "+1", size=18, bold=True, color=svgkit.POS))
    
    # Графік основи e
    frags.append(svgkit.text(300, 200, "Економічність основи E(b) = b / ln(b)", size=14, bold=True))
    
    # Осі
    frags.append(svgkit.line(100, 270, 500, 270, sw=2)) # X
    frags.append(svgkit.line(150, 270, 150, 210, sw=2)) # Y
    
    frags.append(svgkit.text(500, 285, "Основа (b)", size=12))
    frags.append(svgkit.text(120, 210, "E(b)", size=12))
    
    # Точки
    frags.append(svgkit.circle(200, 240, 4, fill=svgkit.INK)) # 2
    frags.append(svgkit.text(200, 285, "2", size=12))
    
    frags.append(svgkit.circle(235, 230, 4, fill=svgkit.POS)) # e
    frags.append(svgkit.text(235, 285, "e ≈ 2.718", size=12, color=svgkit.POS))
    
    frags.append(svgkit.circle(250, 232, 4, fill=svgkit.NEG)) # 3
    frags.append(svgkit.text(250, 285, "3", size=12, color=svgkit.NEG))
    
    frags.append(svgkit.circle(300, 250, 4, fill=svgkit.INK)) # 4
    frags.append(svgkit.text(300, 285, "4", size=12))
    
    frags.append(svgkit.circle(500, 260, 4, fill=svgkit.INK)) # 10
    frags.append(svgkit.text(500, 285, "10", size=12))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'fig-balanced-ternary.svg')
    
    svgkit.render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == '__main__':
    main()
