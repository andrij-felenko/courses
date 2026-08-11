import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "scripts")))
from svgkit import render, rect, textbox, line, arrow, circle, text

def make_bpf_iter_arch():
    frags = []
    
    # Userspace
    frags.append(rect(50, 50, 200, 250, fill="#2d2d2d"))
    frags.append(text(150, 70, "Userspace", size=16, color="#ccc", bold=True))
    frags.append(rect(75, 100, 150, 50, fill="#4CAF50"))
    frags.append(text(150, 125, "cat /sys/fs/bpf/my_iter", color="#fff"))
    
    # Kernel Space
    frags.append(rect(350, 50, 400, 250, fill="#2d2d2d"))
    frags.append(text(550, 70, "Kernel Space", size=16, color="#ccc", bold=True))
    
    # BPF Subsystem
    frags.append(rect(400, 100, 300, 180, fill="#3d3d3d", stroke="#666"))
    frags.append(text(550, 120, "BPF Subsystem", size=14, color="#aaa"))
    
    frags.append(rect(450, 140, 200, 40, fill="#2196F3"))
    frags.append(text(550, 160, "bpf_iter_task", color="#fff"))
    
    frags.append(rect(450, 200, 200, 40, fill="#FF9800"))
    frags.append(text(550, 220, "seq_file / bpf_seq_printf", color="#fff"))
    
    # Arrows
    frags.append(arrow(225, 125, 450, 160, color="#fff"))
    frags.append(arrow(450, 220, 225, 135, color="#fff"))
    
    os.makedirs("figs", exist_ok=True)
    render(os.path.join(IMG, 'bpf-iter-arch.svg'), 800, 350, *frags)

def make_user_ringbuf():
    frags = []
    
    # Producer
    frags.append(rect(100, 100, 150, 80, fill="#E91E63"))
    frags.append(text(175, 130, "Userspace", color="#fff", bold=True))
    frags.append(text(175, 150, "Producer", color="#fff"))
    
    # Consumer
    frags.append(rect(550, 100, 150, 80, fill="#00BCD4"))
    frags.append(text(625, 130, "BPF Program", color="#fff", bold=True))
    frags.append(text(625, 150, "Consumer", color="#fff"))
    
    # Ring Buffer
    frags.append(rect(300, 70, 200, 140, rx=70, fill="#333", stroke="#FFC107", sw=3))
    frags.append(circle(400, 140, 40, fill="#1e1e1e", stroke="#FFC107", sw=3))
    
    frags.append(circle(400, 85, 8, fill="#4CAF50", stroke="none"))
    frags.append(circle(440, 110, 8, fill="#4CAF50", stroke="none"))
    frags.append(circle(440, 170, 8, fill="#4CAF50", stroke="none"))
    frags.append(circle(400, 195, 8, fill="#555", stroke="none"))
    frags.append(circle(360, 170, 8, fill="#555", stroke="none"))
    frags.append(circle(360, 110, 8, fill="#555", stroke="none"))
    
    frags.append(text(400, 40, "User Ring Buffer", color="#FFC107", size=16, bold=True))
    
    # Arrows
    frags.append(arrow(250, 140, 320, 140, color="#fff"))
    frags.append(arrow(480, 140, 550, 140, color="#fff"))
    
    os.makedirs("figs", exist_ok=True)
    render(os.path.join(IMG, 'bpf-user-ringbuf.svg'), 800, 250, *frags)

if __name__ == "__main__":
    make_bpf_iter_arch()
    make_user_ringbuf()
    print("Generated SVGs successfully")
