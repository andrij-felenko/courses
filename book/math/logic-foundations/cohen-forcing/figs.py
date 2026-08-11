import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'fig-cohen-forcing.svg')
    
    frags = []
    
    b1, w1, h1 = svgkit.textbox(300, 120, "Базова транзитивна модель M\n(Зліченна модель ZFC)", min_w=220)
    frags.append(b1)
    
    b2, w2, h2 = svgkit.textbox(300, 260, "Модель розширення M[G]\n(Нова модель з доданим G)", min_w=220, fill="#eaf0fd", stroke=svgkit.NEG)
    frags.append(b2)
    
    frags.append(svgkit.arrow(300, 120 + h1/2, 300, 260 - h2/2, color=svgkit.LINE, sw=2))
    
    b3, w3, h3 = svgkit.textbox(150, 190, "Умови P ∈ M\nЧастковий порядок", min_w=140)
    frags.append(b3)
    
    b4, w4, h4 = svgkit.textbox(450, 190, "Генерний фільтр G ∉ M\nG ⊆ P", min_w=140)
    frags.append(b4)
    
    frags.append(svgkit.arrow(220, 190, 380, 190, color=svgkit.LINE, sw=2))
    frags.append(svgkit.text(300, 180, "форсування", size=12, italic=True))
    
    svgkit.render(out_path, 600, 400, *frags, title="Схема розширення моделі методом форсингу")

if __name__ == '__main__':
    main()
