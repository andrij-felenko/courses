from svgkit import *

def draw_netlink_scheme():
    dwg = init_svg(600, 400)
    
    # Kernel Space
    dwg.add(dwg.rect(insert=(50, 200), size=(500, 150), fill="#f0f0f0", stroke="#333", rx=10))
    dwg.add(dwg.text("Kernel Space", insert=(60, 220), font_size="16", font_weight="bold", fill="#555"))
    dwg.add(dwg.rect(insert=(100, 250), size=(150, 60), fill="#cce5ff", stroke="#004085", rx=5))
    dwg.add(dwg.text("Netlink Core", insert=(120, 285), font_size="14", font_weight="bold"))
    
    dwg.add(dwg.rect(insert=(350, 230), size=(150, 40), fill="#d4edda", stroke="#155724", rx=5))
    dwg.add(dwg.text("Networking Subsys", insert=(360, 255), font_size="12", font_weight="bold"))
    
    dwg.add(dwg.rect(insert=(350, 290), size=(150, 40), fill="#d4edda", stroke="#155724", rx=5))
    dwg.add(dwg.text("Audit / SELinux", insert=(370, 315), font_size="12", font_weight="bold"))
    
    # User Space
    dwg.add(dwg.rect(insert=(50, 20), size=(500, 150), fill="#ffffff", stroke="#333", stroke_dasharray="5,5", rx=10))
    dwg.add(dwg.text("User Space", insert=(60, 40), font_size="16", font_weight="bold", fill="#555"))
    dwg.add(dwg.rect(insert=(100, 70), size=(150, 60), fill="#fff3cd", stroke="#856404", rx=5))
    dwg.add(dwg.text("User Process", insert=(125, 105), font_size="14", font_weight="bold"))
    
    # Arrows
    # Bidirectional communication between User Process and Netlink Core
    dwg.add(dwg.line(start=(150, 130), end=(150, 250), stroke="#000", stroke_width="2", marker_end="url(#arrow)", marker_start="url(#arrow)"))
    dwg.add(dwg.text("AF_NETLINK", insert=(160, 190), font_size="12"))
    
    # Internal kernel communication
    dwg.add(dwg.line(start=(250, 260), end=(350, 250), stroke="#000", stroke_width="2", marker_end="url(#arrow)"))
    dwg.add(dwg.line(start=(250, 290), end=(350, 310), stroke="#000", stroke_width="2", marker_end="url(#arrow)"))

    render(dwg, "netlink_arch.svg")

if __name__ == "__main__":
    draw_netlink_scheme()
