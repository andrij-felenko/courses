import sys, os

sys.path.append(os.path.abspath('../../../../scripts'))
import svgkit

def draw_quotient_sets():
    W = 800
    H = 450
    os.makedirs('img', exist_ok=True)
    
    frags = []
    
    # Left Set X
    frags.append(svgkit.rect(50, 50, 300, 350, rx=20, fill=svgkit.FILL, stroke=svgkit.LINE, sw=2))
    frags.append(svgkit.text(200, 40, "Множина X", size=20, bold=True, anchor="middle"))
    
    # Partitions in X
    frags.append(svgkit.line(50, 166, 350, 166, sw=2, color=svgkit.MUTED, dash="5,5"))
    frags.append(svgkit.line(50, 283, 350, 283, sw=2, color=svgkit.MUTED, dash="5,5"))
    
    # Points in X
    pts = [
        (120, 100), (200, 80), (280, 120),  
        (100, 200), (180, 230), (260, 190), (220, 260), 
        (150, 330), (250, 360)
    ]
    for px, py in pts:
        frags.append(svgkit.circle(px, py, 4, fill=svgkit.INK, stroke=svgkit.INK))
        
    frags.append(svgkit.text(120, 150, "Клас [a]", size=14, anchor="middle"))
    frags.append(svgkit.text(120, 270, "Клас [b]", size=14, anchor="middle"))
    frags.append(svgkit.text(150, 380, "Клас [c]", size=14, anchor="middle"))
    
    # Right Quotient Set X/~
    frags.append(svgkit.rect(450, 100, 250, 250, rx=20, fill=svgkit.FIELD, stroke=svgkit.LINE, sw=2))
    frags.append(svgkit.text(575, 90, "Фактор-множина X/~", size=20, bold=True, anchor="middle"))
    
    # Points in X/~
    q_pts = [
        (575, 140, "Точка [a]"),
        (575, 225, "Точка [b]"),
        (575, 310, "Точка [c]")
    ]
    for px, py, label in q_pts:
        frags.append(svgkit.circle(px, py, 6, fill=svgkit.POS, stroke=svgkit.POS))
        frags.append(svgkit.text(px+15, py+5, label, size=14, anchor="start"))
        
    # Projection π
    frags.append(svgkit.arrow(360, 225, 430, 225, sw=3, color=svgkit.POS))
    frags.append(svgkit.text(395, 215, "π : X → X/~", size=16, bold=True, anchor="middle", color=svgkit.POS))
    
    # Mapping arrows
    frags.append(svgkit.line(360, 100, 450, 140, sw=2, color=svgkit.MUTED, dash="4,4"))
    frags.append(svgkit.line(360, 225, 450, 225, sw=2, color=svgkit.MUTED, dash="4,4"))
    frags.append(svgkit.line(360, 350, 450, 310, sw=2, color=svgkit.MUTED, dash="4,4"))
    
    svgkit.render('img/fig-quotient-sets.svg', W, H, *frags, title="Канонічна проекція та фактор-множина")

if __name__ == '__main__':
    draw_quotient_sets()
