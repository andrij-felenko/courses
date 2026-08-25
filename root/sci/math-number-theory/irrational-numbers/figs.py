import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    W, H = 840, 480
    frags = []
    
    # Spiral
    spiral_cx = 250
    spiral_cy = 260
    scale = 45 
    
    current_angle = 0
    pn = (scale, 0)
    
    # draw the first 1
    frags.append(text(spiral_cx + scale/2, spiral_cy + 15, "1", size=14, color=MUTED))
    
    for n in range(1, 15):
        next_radius = math.sqrt(n + 1) * scale
        angle_step = math.atan2(1, math.sqrt(n))
        next_angle = current_angle + angle_step
        
        next_pn = (next_radius * math.cos(next_angle), next_radius * math.sin(next_angle))
        
        abs_p0 = (spiral_cx, spiral_cy)
        abs_pn = (spiral_cx + pn[0], spiral_cy - pn[1]) 
        abs_next_pn = (spiral_cx + next_pn[0], spiral_cy - next_pn[1])
        
        fill_color = "#eaf0fd" if n % 2 == 0 else "#f4f6f8"
        frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>' % 
                     (abs_p0[0], abs_p0[1], abs_pn[0], abs_pn[1], abs_next_pn[0], abs_next_pn[1], fill_color, LINE))
        
        label_text = f"√{n+1}"
        mid_x = (abs_pn[0] + abs_next_pn[0]) / 2
        mid_y = (abs_pn[1] + abs_next_pn[1]) / 2
        
        out_vec = (mid_x - spiral_cx, mid_y - spiral_cy)
        out_len = math.hypot(*out_vec)
        if out_len > 0:
            lx = mid_x + (out_vec[0]/out_len) * 22
            ly = mid_y + (out_vec[1]/out_len) * 22
            frags.append(text(lx, ly + 5, label_text, size=14, color=NEG))
            
            # also add "1" to the outer edge
            mid_edge_x = (abs_pn[0] + abs_next_pn[0]) / 2
            mid_edge_y = (abs_pn[1] + abs_next_pn[1]) / 2
            ex = mid_edge_x + (out_vec[0]/out_len) * 8
            ey = mid_edge_y + (out_vec[1]/out_len) * 8
            frags.append(text(ex, ey + 4, "1", size=10, color=MUTED))
            
        current_angle = next_angle
        pn = next_pn

    # Right part: Tree/fraction
    frags.append(text(600, 100, "Ланцюговий дріб √2", size=16, bold=True))
    
    def draw_fraction(cx, cy, level, max_level):
        if level > max_level:
            frags.append(text(cx + 25, cy + 25, "...", size=16))
            return
            
        is_first = (level == 0)
        coeff = "1" if is_first else "2"
        
        frags.append(text(cx - 20, cy + 5, f"{coeff} +", size=16, anchor="end"))
        frags.append(text(cx + 25, cy - 8, "1", size=16))
        frags.append(line(cx, cy + 4, cx + 50, cy + 4, sw=1.5))
        
        draw_fraction(cx + 20, cy + 34, level + 1, max_level)

    draw_fraction(580, 150, 0, 4)

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-irrational-continued-fractions.svg")
    
    render(out_path, W, H, *frags, title="Спіраль Феодора та нескінченний дріб")

if __name__ == "__main__":
    main()
