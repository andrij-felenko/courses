import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import rect, text, textbox, line, arrow, render, FILL, LINE, INK

def make_fig():
    f = []
    
    # User Space
    f.append(rect(50, 60, 500, 100, fill="#e3f2fd", stroke="#1e88e5"))
    f.append(text(300, 80, "Простір користувача (User Space)", size=16, bold=True, color="#1565c0"))
    
    # Frameworks
    tb_fw, w, h = textbox(135, 120, "TensorFlow / PyTorch", pad=8)
    f.append(tb_fw)
    
    # UMD
    tb_umd, w, h = textbox(300, 120, "User Mode Driver (UMD)", pad=8)
    f.append(tb_umd)
    
    # libdrm
    tb_lib, w, h = textbox(465, 120, "libdrm (Accel API)", pad=8)
    f.append(tb_lib)
    
    # Kernel Space
    f.append(rect(50, 200, 500, 100, fill="#e8f5e9", stroke="#43a047"))
    f.append(text(300, 220, "Простір ядра (Kernel Space, Linux 6.3+)", size=16, bold=True, color="#2e7d32"))
    
    # DRM Core
    tb_drm, w, h = textbox(135, 260, "DRM Core", pad=8)
    f.append(tb_drm)
    
    # DRM Accel Framework
    tb_accel, w, h = textbox(300, 260, "DRM Accel Framework", pad=8)
    f.append(tb_accel)
    
    # KMD
    tb_kmd, w, h = textbox(465, 260, "KMD (Intel VPU, Habana)", pad=8)
    f.append(tb_kmd)
    
    # Hardware
    f.append(rect(50, 330, 500, 50, fill="#fff3e0", stroke="#fb8c00"))
    f.append(text(300, 360, "Апаратне забезпечення: NPUs, TPUs, AI Accelerators", size=16, bold=True, color="#e65100"))
    
    # Arrows
    f.append(arrow(300, 140, 300, 235))
    f.append(text(310, 185, "/dev/accel/accel0", size=12, color="#c0392b", anchor="start"))
    
    f.append(arrow(300, 280, 300, 330))

    render(os.path.join(IMG, 'drm-accel-architecture.svg'), 600, 400, *f, title="Архітектура підсистеми DRM Accel")

if __name__ == "__main__":
    make_fig()
