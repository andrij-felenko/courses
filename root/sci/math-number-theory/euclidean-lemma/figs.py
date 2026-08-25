import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_fig_euclid():
    w, h = 600, 350
    path = os.path.join(os.path.dirname(__file__), "img", "fig-euclid-lemma.svg")
    
    frags = []
    
    # Textboxes
    b_pab, w1, h1 = textbox(300, 80, "p | a · b\n(просте p ділить добуток)")
    
    b_pa, w2, h2 = textbox(150, 180, "p | a", color=POS, bold=True)
    b_pb, w3, h3 = textbox(450, 180, "p | b", color=POS, bold=True)
    
    frags.append(b_pab)
    frags.append(b_pa)
    frags.append(b_pb)
    
    frags.append(text(300, 180, "АБО", size=14, bold=True))
    
    # Arrows
    frags.append(arrow(300, 110, 150, 150, color=LINE))
    frags.append(arrow(300, 110, 450, 150, color=LINE))
    
    # Bezout logic
    frags.append(text(300, 240, "Доведення (якщо p ∤ a):", size=15, bold=True))
    frags.append(text(300, 270, "gcd(p, a) = 1  ⇒  p·x + a·y = 1", size=15))
    frags.append(text(300, 300, "множимо на b  ⇒  p·b·x + a·b·y = b", size=15))
    frags.append(text(300, 330, "p ділить ліву частину, отже p | b", size=15, color=FIELD, bold=True))
    
    render(path, w, h, *frags, title="Лема Евкліда та її наслідок")

if __name__ == '__main__':
    make_fig_euclid()
