import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def generate_octal_permissions():
    frags = []
    
    frags.append(svgkit.text(400, 40, "Unix Permissions to Octal Mapping", size=24, bold=True))
    
    permissions = [
        ("Owner", "r", "w", "x", 1, 1, 1, "7"),
        ("Group", "r", "-", "x", 1, 0, 1, "5"),
        ("Others", "r", "-", "-", 1, 0, 0, "4")
    ]
    
    start_x = 100
    y_offset_box = 100
    box_w = 60
    box_h = 40
    gap = 20
    group_gap = 40
    
    for i, (label, b1, b2, b3, v1, v2, v3, octal) in enumerate(permissions):
        x = start_x + i * (3 * box_w + gap * 2 + group_gap)
        
        # Group Label
        frags.append(svgkit.text(x + 1.5 * box_w + gap, y_offset_box - 20, label, size=16, color="#555"))
        
        # Draw rwx boxes
        for j, (p, v) in enumerate([(b1, v1), (b2, v2), (b3, v3)]):
            bx = x + j * (box_w + gap)
            fill_color = "#e3f2fd" if v else "#f5f5f5"
            frags.append(svgkit.rect(bx, y_offset_box, box_w, box_h, fill=fill_color, rx=4))
            frags.append(svgkit.text(bx + box_w/2, y_offset_box + 25, p, size=20, bold=True))
            
            # Binary value
            frags.append(svgkit.text(bx + box_w/2, y_offset_box + 70, str(v), size=20, bold=True))
            
            # Binary weight (4, 2, 1)
            weight = 4 >> j
            frags.append(svgkit.text(bx + box_w/2, y_offset_box + 90, f"x{weight}", size=12, color="#666"))
            
        # Octal Value
        ox = x + 1.5 * box_w + gap
        oy = y_offset_box + 140
        frags.append(svgkit.rect(ox - 20, oy - 30, 40, 40, fill="#e8f5e9", rx=8))
        frags.append(svgkit.text(ox, oy - 2, octal, size=20, bold=True))
        
        # Sum formula
        frags.append(svgkit.text(ox, oy + 30, f"{v1}x4 + {v2}x2 + {v3}x1 = {octal}", size=14, color="#333"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-octal-unix-permissions.svg")
    
    svgkit.render(out_path, 800, 350, *frags, title="Octal Unix Permissions")
    print(f"Saved {out_path}")

if __name__ == "__main__":
    generate_octal_permissions()
