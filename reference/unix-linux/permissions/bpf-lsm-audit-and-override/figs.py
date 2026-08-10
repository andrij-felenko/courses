import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import rect, text, arrow, render

def draw_arch():
    frags = []
    
    # User Space
    frags.append(rect(50, 20, 700, 80, fill="#f0f0f0", stroke="#333", rx=5))
    frags.append(text(400, 40, "User Space", bold=True))
    frags.append(rect(100, 50, 150, 40, fill="#fff", stroke="#333"))
    frags.append(text(175, 75, "App (Syscall)"))
    
    frags.append(rect(550, 50, 150, 40, fill="#fff", stroke="#333"))
    frags.append(text(625, 75, "BPF Loader / Audit"))

    # Kernel Space
    frags.append(rect(50, 120, 700, 250, fill="#e6f7ff", stroke="#333", rx=5))
    frags.append(text(400, 140, "Kernel Space", bold=True))
    
    # Core Kernel
    frags.append(rect(100, 170, 150, 40, fill="#fff", stroke="#333"))
    frags.append(text(175, 195, "Syscall Interface"))
    
    frags.append(rect(100, 240, 150, 40, fill="#fff", stroke="#333"))
    frags.append(text(175, 265, "DAC / Core Logic"))
    
    # LSM Framework
    frags.append(rect(320, 220, 150, 80, fill="#ffe6e6", stroke="#333", rx=5))
    frags.append(text(395, 245, "LSM Framework", bold=True))
    frags.append(text(395, 275, "LSM Hooks"))
    
    # BPF LSM
    frags.append(rect(550, 220, 150, 80, fill="#e6ffe6", stroke="#333", rx=5))
    frags.append(text(625, 245, "BPF JIT/VM", bold=True))
    frags.append(text(625, 275, "BPF_PROG_TYPE_LSM", size=12))
    
    # Arrows
    frags.append(arrow(175, 90, 175, 170))
    frags.append(arrow(175, 210, 175, 240))
    frags.append(arrow(250, 260, 320, 260))
    frags.append(arrow(470, 260, 550, 260))
    # Dashed arrow can be passed as dash='5,5' but svgkit arrow doesn't support dash argument directly, so just a regular arrow
    frags.append(arrow(625, 90, 625, 220))
    
    return frags

def main():
    figs_dir = os.path.join(os.path.dirname(__file__), 'figs')
    os.makedirs(figs_dir, exist_ok=True)
    out_path = os.path.join(figs_dir, 'bpf-lsm-arch.svg')
    
    frags = draw_arch()
    render(out_path, 800, 400, *frags)

if __name__ == '__main__':
    main()
