import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_kripke_frames():
    w, h = 600, 300
    out = []
    
    w1_cx, w1_cy = 150, 150
    w2_cx, w2_cy = 300, 100
    w3_cx, w3_cy = 300, 200
    
    out.append(arrow(w1_cx + 25, w1_cy - 10, w2_cx - 25, w2_cy + 10))
    out.append(arrow(w1_cx + 25, w1_cy + 10, w3_cx - 25, w3_cy - 10))
    out.append(arrow(w2_cx, w2_cy + 25, w3_cx, w3_cy - 25))
    out.append('<path d="M %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % 
               (w3_cx + 10, w3_cy + 20, w3_cx + 50, w3_cy + 50, w3_cx + 50, w3_cy + 20, w3_cx + 25, w3_cy, LINE))
               
    out.append(circle(w1_cx, w1_cy, 20))
    out.append(text(w1_cx, w1_cy + 5, "w1"))
    
    out.append(circle(w2_cx, w2_cy, 20))
    out.append(text(w2_cx, w2_cy + 5, "w2"))
    
    out.append(circle(w3_cx, w3_cy, 20))
    out.append(text(w3_cx, w3_cy + 5, "w3"))
    
    out.append(text(w1_cx, w1_cy + 40, "V: p, ¬q", size=12, color=MUTED))
    out.append(text(w2_cx, w2_cy - 30, "V: p, q", size=12, color=MUTED))
    out.append(text(w3_cx, w3_cy + 40, "V: ¬p, q", size=12, color=MUTED))
    
    leg_x, leg_y = 450, 100
    b1, tw1, th1 = textbox(leg_x, leg_y, "W = {w1, w2, w3}")
    out.append(b1)
    b2, tw2, th2 = textbox(leg_x, leg_y + 50, "R = {(w1,w2), (w1,w3),\n(w2,w3), (w3,w3)}")
    out.append(b2)
    b3, tw3, th3 = textbox(leg_x, leg_y + 110, "K = (W, R, V)")
    out.append(b3)
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render(os.path.join(img_dir, 'fig-kripke-frames.svg'), w, h, *out, title="Граф фреймів та можливих світів Кріпке")

if __name__ == "__main__":
    draw_kripke_frames()
