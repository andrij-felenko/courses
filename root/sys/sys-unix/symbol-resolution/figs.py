import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

def build_resolution_scope():
    elements = []
    
    # Title / Header
    elements.append(text(350, 25, "Глобальний порядок пошуку символу (Symbol Search Scope)", size=16, bold=True, anchor="middle"))
    
    # Steps / Boxes representing search scope order
    b1, w1, h1 = textbox(150, 90, "1. LD_PRELOAD\n(перехоплювачі)", size=13, fill="#fdecea", stroke=POS, bold=True)
    b2, w2, h2 = textbox(350, 90, "2. Головний бінарник\n(Executable Binary)", size=13, fill="#eaf0fd", stroke=NEG, bold=True)
    b3, w3, h3 = textbox(560, 90, "3. Спільні бібліотеки\n(libc.so, libm.so...)", size=13, fill=FILL, stroke=LINE, bold=True)
    
    elements.extend([b1, b2, b3])
    
    # Arrows between boxes
    elements.append(arrow(225, 90, 270, 90, color=LINE, sw=2))
    elements.append(arrow(430, 90, 480, 90, color=LINE, sw=2))
    
    # Lower annotation box explaining First-Match Wins
    desc = "Динамічний лінкер ld.so шукає назву символу за алгоритмом First-Match Wins.\nПерше знайдене визначення символу зв'язується з усіма GOT-записами."
    fb = fitbox(60, 150, 580, 50, desc, size=12, fill="#eef9f1", stroke=FIELD, rx=6)
    elements.append(fb)
    
    return elements

def build_interposition_chain():
    elements = []
    
    elements.append(text(350, 25, "Ланцюжок перехоплення та виклик RTLD_NEXT", size=16, bold=True, anchor="middle"))
    
    # Node 1: Application
    b1 = fitbox(30, 70, 150, 60, "Програма\n(Call malloc)", size=13, fill=FILL, stroke=LINE, bold=True)
    # Node 2: Hook Library
    b2 = fitbox(250, 70, 180, 60, "myhook.so\nmalloc() hook", size=13, fill="#fdecea", stroke=POS, bold=True)
    # Node 3: Real libc malloc
    b3 = fitbox(510, 70, 150, 60, "libc.so\nРеальний malloc()", size=13, fill="#eaf0fd", stroke=NEG, bold=True)
    
    elements.extend([b1, b2, b3])
    
    # Arrow 1 -> 2
    elements.append(arrow(180, 100, 250, 100, color=LINE, sw=2))
    # Arrow 2 -> 3 with dlsym text above
    elements.append(arrow(430, 100, 510, 100, color=LINE, sw=2))
    elements.append(text(470, 85, "dlsym(RTLD_NEXT)", size=11, color=MUTED, anchor="middle", italic=True))
    
    # Bottom explanation
    desc = "myhook.so отримує виклик першою, виконує логування чи перевірку,\nпісля чого передає керування наступному символу в списку завантаження."
    fb = fitbox(100, 160, 500, 45, desc, size=12, fill="#f4f6f8", stroke=LINE, rx=6)
    elements.append(fb)
    
    return elements

def render_all():
    f1 = os.path.join(IMG_DIR, "symbol-resolution-scope.svg")
    f2 = os.path.join(IMG_DIR, "interposition-chain.svg")
    
    render(f1, 700, 220, *build_resolution_scope())
    render(f2, 700, 220, *build_interposition_chain())
    print("Rendered SVG figures to img/")

if __name__ == "__main__":
    render_all()
