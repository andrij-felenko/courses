def render():
    elements = []
    def add_rect(x, y, w, h, rx, fill, stroke, dash=""):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash_attr}/>')
    def add_text(txt, x, y, size, weight="normal", anchor="middle", fill="#333", mono=False):
        font = "monospace" if mono else "sans-serif"
        elements.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{txt}</text>')
    def add_path(d, stroke, dash=""):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        elements.append(f'<path d="{d}" stroke="{stroke}" stroke-width="2" fill="none" marker-end="url(#arrow)"{dash_attr}/>')
    
    # User space
    add_rect(50, 50, 700, 80, 5, "#f0f0f0", "#333")
    add_text("Простір користувача (Userspace)", 400, 70, 16, "bold")
    add_rect(100, 85, 200, 30, 3, "#fff", "#333")
    add_text("io_uring SQE (URING_CMD)", 200, 105, 12)
    
    # Kernel space
    add_rect(50, 150, 700, 220, 5, "#e6f7ff", "#333")
    add_text("Простір ядра (Kernel space)", 400, 170, 16, "bold")
    
    # io_uring core
    add_rect(100, 190, 200, 50, 3, "#b3e0ff", "#005c99")
    add_text("io_uring core", 200, 220, 14)
    
    # VFS / Block layer bypass
    add_rect(350, 190, 150, 50, 3, "#ffd6cc", "#cc3300", "4")
    add_text("VFS / blk-mq", 425, 220, 14)
    
    # NVMe char device driver
    add_rect(100, 280, 600, 70, 3, "#b3ffb3", "#009900")
    add_text("NVMe Character Device Driver (/dev/ng0n1)", 400, 305, 14)
    add_text("nvme_uring_cmd() / uring_cmd_comp()", 400, 330, 12, mono=True)
    
    # Hardware
    add_rect(50, 390, 700, 80, 5, "#ffe6e6", "#333")
    add_text("Апаратне забезпечення (Hardware)", 400, 410, 16, "bold")
    add_rect(300, 425, 200, 30, 3, "#fff", "#333")
    add_text("NVMe Controller", 400, 445, 14)
    
    # Arrows
    add_path("M 200 115 L 200 180", "#333")
    add_path("M 200 240 L 200 270", "#005c99")
    add_path("M 200 215 C 275 215, 325 215, 340 215", "#cc3300", "4")
    add_text("Bypass", 275, 210, 12, fill="#cc3300")
    add_path("M 400 350 L 400 380", "#009900")
    add_path("M 500 425 L 500 355", "#333", "4")
    add_text("Interrupt / CQE", 510, 390, 12)
    
    marker = """<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
    </marker>
  </defs>"""
    
    svg_body = "\n  ".join(elements)
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  {marker}
  {svg_body}
</svg>'''

if __name__ == '__main__':
    with open('fig_uring_passthrough.svg', 'w', encoding='utf-8') as f:
        f.write(render())
