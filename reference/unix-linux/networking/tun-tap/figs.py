import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "scripts")))
from svgkit import SVG, Path, Rect, Text, Group, Circle, Defs, Marker

def draw_tun_tap():
    svg = SVG(width=800, height=400, view_box="0 0 800 400")
    
    # User space and Kernel space
    svg.add(Rect(x=50, y=50, width=700, height=140, rx=5, fill="#f0f8ff", stroke="#b0c4de", stroke_width=2))
    svg.add(Text(x=60, y=70, text="User Space", font_family="sans-serif", font_size=14, font_weight="bold", fill="#333333"))
    
    svg.add(Rect(x=50, y=210, width=700, height=140, rx=5, fill="#fff0f5", stroke="#ffb6c1", stroke_width=2))
    svg.add(Text(x=60, y=230, text="Kernel Space", font_family="sans-serif", font_size=14, font_weight="bold", fill="#333333"))
    
    # Application in User space
    svg.add(Rect(x=150, y=100, width=150, height=60, rx=5, fill="#add8e6", stroke="#4682b4", stroke_width=2))
    svg.add(Text(x=225, y=135, text="Application\n(VPN, QEMU)", font_family="sans-serif", font_size=14, fill="#000000", text_anchor="middle"))
    
    # Interface in Kernel space
    svg.add(Rect(x=150, y=260, width=150, height=60, rx=5, fill="#ffb6c1", stroke="#dc143c", stroke_width=2))
    svg.add(Text(x=225, y=295, text="TUN/TAP Interface", font_family="sans-serif", font_size=14, fill="#000000", text_anchor="middle"))
    
    # /dev/net/tun file descriptor
    svg.add(Rect(x=450, y=170, width=150, height=60, rx=5, fill="#ffd700", stroke="#daa520", stroke_width=2))
    svg.add(Text(x=525, y=205, text="/dev/net/tun\n(Character Device)", font_family="sans-serif", font_size=14, fill="#000000", text_anchor="middle"))
    
    # Physical Interface
    svg.add(Rect(x=600, y=260, width=120, height=60, rx=5, fill="#90ee90", stroke="#228b22", stroke_width=2))
    svg.add(Text(x=660, y=295, text="Physical NIC\n(eth0)", font_family="sans-serif", font_size=14, fill="#000000", text_anchor="middle"))
    
    # Network Stack
    svg.add(Rect(x=350, y=260, width=120, height=60, rx=5, fill="#d3d3d3", stroke="#a9a9a9", stroke_width=2))
    svg.add(Text(x=410, y=295, text="Network Stack\n(IP/TCP)", font_family="sans-serif", font_size=14, fill="#000000", text_anchor="middle"))
    
    # Arrows
    defs = Defs()
    defs.add(Marker(id="arrow", refX=9, refY=5, markerWidth=10, markerHeight=10, orient="auto", path_d="M 0 0 L 10 5 L 0 10 z", fill="#333333"))
    svg.add(defs)
    
    # App to /dev/net/tun
    svg.add(Path(d="M 300 130 C 400 130, 525 150, 525 170", fill="none", stroke="#333333", stroke_width=2, marker_end="url(#arrow)"))
    # /dev/net/tun to TUN/TAP interface
    svg.add(Path(d="M 525 230 C 525 240, 300 290, 300 290", fill="none", stroke="#333333", stroke_width=2, marker_end="url(#arrow)"))
    
    return svg.tostring()

def render():
    with open("fig-tun-tap.svg", "w") as f:
        f.write(draw_tun_tap())

if __name__ == "__main__":
    render()
