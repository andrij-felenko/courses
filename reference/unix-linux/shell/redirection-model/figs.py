import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def render():
    svg = svgkit.Drawing(width=800, height=400)
    
    # Background
    svg.rect(x=0, y=0, width=800, height=400, fill="#f9f9f9", rx=10)
    
    # Tables
    # Process FD table
    svg.text(x=100, y=40, text="Process File Descriptor Table", font_size=16, font_weight="bold", fill="#333")
    svg.rect(x=50, y=60, width=200, height=220, fill="#fff", stroke="#333", stroke_width=2)
    
    # FD Entries
    y_offset = 80
    for i, label in enumerate(["0 (stdin)", "1 (stdout)", "2 (stderr)", "3 (file)"]):
        svg.rect(x=50, y=y_offset + i*50, width=200, height=50, fill="#eef", stroke="#ccc")
        svg.text(x=150, y=y_offset + i*50 + 30, text=label, font_size=14, text_anchor="middle", fill="#333")
    
    # System Open File Table
    svg.text(x=500, y=40, text="Open File Table (Kernel)", font_size=16, font_weight="bold", fill="#333")
    svg.rect(x=450, y=60, width=200, height=220, fill="#fff", stroke="#333", stroke_width=2)
    
    # Open Files Entries
    svg.rect(x=450, y=80, width=200, height=50, fill="#ffe", stroke="#ccc")
    svg.text(x=550, y=110, text="/dev/tty (Terminal)", font_size=14, text_anchor="middle", fill="#333")
    
    svg.rect(x=450, y=230, width=200, height=50, fill="#efd", stroke="#ccc")
    svg.text(x=550, y=260, text="output.txt", font_size=14, text_anchor="middle", fill="#333")
    
    # Arrows (Pointers)
    # 0 -> /dev/tty
    svg.line(x1=250, y1=105, x2=450, y2=105, stroke="#333", stroke_width=2, marker_end="url(#arrow)")
    # 2 -> /dev/tty
    svg.line(x1=250, y1=205, x2=430, y2=115, stroke="#333", stroke_width=2, marker_end="url(#arrow)")
    
    # dup2 magic (1 -> output.txt)
    svg.line(x1=250, y1=155, x2=450, y2=255, stroke="#d32f2f", stroke_width=3, stroke_dasharray="5,5", marker_end="url(#arrow_red)")
    svg.text(x=350, y=220, text="dup2(3, 1)", font_size=14, fill="#d32f2f", font_weight="bold", text_anchor="middle", transform="rotate(30, 350, 220)")
    
    # 3 -> output.txt
    svg.line(x1=250, y1=255, x2=450, y2=255, stroke="#4caf50", stroke_width=2, marker_end="url(#arrow)")
    
    # Defs for arrows
    svg.add_raw(r'''
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#333" />
        </marker>
        <marker id="arrow_red" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#d32f2f" />
        </marker>
    </defs>
    ''')
    
    # Save the output
    out_dir = os.path.join(os.path.dirname(__file__), 'figs')
    os.makedirs(out_dir, exist_ok=True)
    svg.save(os.path.join(out_dir, 'dup2_mechanics.svg'))

if __name__ == '__main__':
    render()
