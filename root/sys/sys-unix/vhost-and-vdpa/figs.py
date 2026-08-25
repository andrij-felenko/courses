import sys
import os

# Add scripts directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "scripts"))
sys.path.insert(0, scripts_dir)

try:
    from svgkit import render, rect, text, arrow, line, mtext, textbox
except ImportError as e:
    print(f"Could not import svgkit from {scripts_dir}. Error: {e}")
    sys.exit(1)

def draw_virtio_paths():
    frags = []
    
    # QEMU path
    frags.append(rect(50, 50, 200, 350, rx=10, fill="#f0f0f0", stroke="#333", sw=2))
    frags.append(text(150, 80, "Classic Virtio (QEMU)", size=16, bold=True, anchor="middle"))
    
    frags.append(rect(70, 100, 160, 60, fill="#e6f2ff", stroke="#0066cc"))
    frags.append(text(150, 135, "VM (Guest OS)", size=14, anchor="middle"))
    
    frags.append(rect(70, 200, 160, 60, fill="#fff2e6", stroke="#cc6600"))
    frags.append(text(150, 235, "QEMU (Userspace)", size=14, anchor="middle"))
    
    frags.append(rect(70, 300, 160, 60, fill="#e6ffe6", stroke="#009900"))
    frags.append(text(150, 335, "Host Kernel (Tap)", size=14, anchor="middle"))
    
    # Arrows
    frags.append(arrow(150, 160, 150, 200, color="#333", sw=2))
    frags.append(arrow(150, 260, 150, 300, color="#333", sw=2))
    
    # vhost path
    frags.append(rect(300, 50, 200, 350, rx=10, fill="#f0f0f0", stroke="#333", sw=2))
    frags.append(text(400, 80, "vhost-net (Kernel)", size=16, bold=True, anchor="middle"))
    
    frags.append(rect(320, 100, 160, 60, fill="#e6f2ff", stroke="#0066cc"))
    frags.append(text(400, 135, "VM (Guest OS)", size=14, anchor="middle"))
    
    frags.append(rect(320, 200, 160, 60, fill="#e6ffe6", stroke="#009900"))
    frags.append(mtext(400, 230, ["vhost thread", "(Host Kernel)"], size=14, anchor="middle"))
    
    frags.append(rect(320, 300, 160, 60, fill="#e6ffe6", stroke="#009900"))
    frags.append(text(400, 335, "Host Network Stack", size=14, anchor="middle"))
    
    # Arrows
    frags.append(arrow(400, 160, 400, 200, color="#333", sw=2))
    frags.append(arrow(400, 260, 400, 300, color="#333", sw=2))
    
    # vDPA path
    frags.append(rect(550, 50, 200, 350, rx=10, fill="#f0f0f0", stroke="#333", sw=2))
    frags.append(text(650, 80, "vDPA (Hardware)", size=16, bold=True, anchor="middle"))
    
    frags.append(rect(570, 100, 160, 60, fill="#e6f2ff", stroke="#0066cc"))
    frags.append(text(650, 135, "VM (Guest OS)", size=14, anchor="middle"))
    
    frags.append(rect(570, 300, 160, 60, fill="#ffe6e6", stroke="#cc0000"))
    frags.append(mtext(650, 330, ["SmartNIC/DPU", "(vDPA Hardware)"], size=14, anchor="middle"))
    
    # Arrow direct from VM to NIC
    frags.append(arrow(650, 160, 650, 300, color="#333", sw=3))
    
    tb, w, h = textbox(710, 230, "Direct Ring\nAccess", size=12, pad=4)
    frags.append(tb)

    return frags

if __name__ == "__main__":
    out_dir = os.path.join(current_dir, "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "vdpa-paths.svg")
    frags = draw_virtio_paths()
    render(out_path, 800, 450, *frags)
