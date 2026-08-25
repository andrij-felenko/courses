import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    os.makedirs('img', exist_ok=True)
    w, h = 600, 400
    
    b1, w1, h1 = textbox(300, 100, "W0 (Поточне знання)\nНевідомо p, невідомо q", size=14, pad=10, fill=FILL, min_w=160)
    b2, w2, h2 = textbox(150, 280, "W1 (Відкриття)\nДоведено p", size=14, pad=10, fill="#eaf0fd", stroke=NEG, min_w=120)
    b3, w3, h3 = textbox(450, 280, "W2 (Відкриття)\nДоведено q", size=14, pad=10, fill="#fdecea", stroke=POS, min_w=120)
    
    arr1 = arrow(280, 125, 170, 255)
    arr2 = arrow(320, 125, 430, 255)
    
    t1 = text(200, 180, "≤ (час/знання зростає)", size=12, color=MUTED, italic=True)
    t2 = text(400, 180, "≤ (час/знання зростає)", size=12, color=MUTED, italic=True)
    
    msg = text(300, 360, "У W0 твердження (p ∨ q) хибне, хоча може стати істинним у майбутньому", size=13, color=INK)
    
    render('img/fig-kripke-semantics.svg', w, h,
           arr1, arr2, b1, b2, b3, t1, t2, msg,
           title="Модель світів Кріпке (Інтуїціоністська логіка)")

if __name__ == '__main__':
    main()
