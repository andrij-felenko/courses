import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def main():
    w, h = 700, 400
    frags = []
    
    # Boxes
    b1, w1, h1 = textbox(150, 100, "__init\n(.init.text)\nКод ініціалізації", bold=True, fill="#ffebee", stroke=POS)
    b2, w2, h2 = textbox(150, 200, "__initdata\n(.init.data)\nДані ініціалізації", bold=True, fill="#ffebee", stroke=POS)
    b3, w3, h3 = textbox(150, 300, "__initcall\n(.initcall.init)\nФункції-виклики", bold=True, fill="#ffebee", stroke=POS)
    
    b_kernel, w_k, h_k = textbox(150, 40, "Ядро в пам'яті (завантаження)", fill="#f0f0f0", stroke=LINE)
    
    b_free, w_f, h_f = textbox(550, 200, "Сторінковий алокатор\n(Page Allocator)\nПам'ять доступна для\nкористувацьких процесів", bold=True, fill="#e8f5e9", stroke=FIELD)
    
    frags.extend([b1, b2, b3, b_kernel, b_free])
    
    # Arrows
    frags.append(arrow(150 + w1/2 + 10, 100, 550 - w_f/2 - 10, 180))
    frags.append(arrow(150 + w2/2 + 10, 200, 550 - w_f/2 - 10, 200))
    frags.append(arrow(150 + w3/2 + 10, 300, 550 - w_f/2 - 10, 220))
    
    # Text labels
    frags.append(text(350, 150, "free_initmem()", size=14, italic=True, color=NEG, bold=True))
    frags.append(text(350, 240, "Звільнення після boot", size=12, color=MUTED))
    
    out_path = os.path.join(IMG, "init-sections.svg")
    render(out_path, w, h, *frags, title="Звільнення пам'яті секцій ініціалізації (__init)")

if __name__ == '__main__':
    main()
