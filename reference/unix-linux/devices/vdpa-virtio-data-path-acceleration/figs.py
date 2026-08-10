import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def render_diagram():
    frags = []
    
    # Host OS
    frags.append(rect(50, 100, 300, 300, fill="#f0f0f0", stroke=LINE))
    frags.append(text(200, 130, "Host OS (vDPA Framework)", size=16, bold=True))
    frags.append(rect(100, 160, 200, 60, fill="#add8e6", stroke=LINE))
    frags.append(text(200, 195, "vhost-vdpa / virtio-vdpa", size=14))
    
    # Guest OS
    frags.append(rect(450, 100, 300, 200, fill="#f0f0f0", stroke=LINE))
    frags.append(text(600, 130, "Guest OS / VM", size=16, bold=True))
    frags.append(rect(500, 160, 200, 60, fill="#90ee90", stroke=LINE))
    frags.append(text(600, 195, "virtio-net driver", size=14))
    
    # SmartNIC
    frags.append(rect(250, 350, 300, 150, fill="#ffb6c1", stroke=LINE))
    frags.append(text(400, 380, "SmartNIC (Hardware)", size=16, bold=True))
    frags.append(rect(300, 410, 200, 60, fill="#ffc0cb", stroke=LINE))
    frags.append(text(400, 445, "vDPA Hardware Datapath", size=14))
    
    # Arrows
    frags.append(arrow(200, 220, 350, 410, color=LINE, sw=2))
    frags.append(arrow(600, 220, 450, 410, color=LINE, sw=2))
    
    render("vdpa_architecture.svg", 800, 600, *frags, title="Апаратне прискорення Virtio: vDPA та SmartNIC")

if __name__ == "__main__":
    render_diagram()
