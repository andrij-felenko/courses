import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def blk_mq_arch():
    frags = []
    
    # Background for User Space
    frags.append(rect(50, 50, 700, 350, rx=10, fill="#f8f9fa", stroke="#ccc"))
    frags.append(text(400, 80, "User Space", bold=True, anchor="middle"))
    
    # Processes
    frags.append(rect(100, 100, 150, 50, fill="#e3f2fd", stroke="#1e88e5"))
    frags.append(text(175, 130, "Process 1 (CPU 0)", anchor="middle"))
    
    frags.append(rect(325, 100, 150, 50, fill="#e3f2fd", stroke="#1e88e5"))
    frags.append(text(400, 130, "Process 2 (CPU 1)", anchor="middle"))
    
    frags.append(rect(550, 100, 150, 50, fill="#e3f2fd", stroke="#1e88e5"))
    frags.append(text(625, 130, "Process N (CPU N)", anchor="middle"))
    
    # Arrows down
    frags.append(arrow(175, 150, 175, 200, color="#666"))
    frags.append(arrow(400, 150, 400, 200, color="#666"))
    frags.append(arrow(625, 150, 625, 200, color="#666"))
    
    # Software queues
    frags.append(rect(100, 200, 150, 50, fill="#fff3e0", stroke="#f57c00"))
    frags.append(text(175, 230, "Software Queue (ctx)", size=12, anchor="middle"))
    
    frags.append(rect(325, 200, 150, 50, fill="#fff3e0", stroke="#f57c00"))
    frags.append(text(400, 230, "Software Queue (ctx)", size=12, anchor="middle"))
    
    frags.append(rect(550, 200, 150, 50, fill="#fff3e0", stroke="#f57c00"))
    frags.append(text(625, 230, "Software Queue (ctx)", size=12, anchor="middle"))
    
    # Mapping
    frags.append(line(175, 250, 287.5, 300, color="#666", dash="5,5"))
    frags.append(line(400, 250, 287.5, 300, color="#666", dash="5,5"))
    frags.append(line(625, 250, 625, 300, color="#666", dash="5,5"))
    
    # Hardware queues
    frags.append(rect(200, 300, 175, 50, fill="#e8f5e9", stroke="#43a047"))
    frags.append(text(287.5, 330, "Hardware Queue (hctx)", size=12, anchor="middle"))
    
    frags.append(rect(525, 300, 175, 50, fill="#e8f5e9", stroke="#43a047"))
    frags.append(text(612.5, 330, "Hardware Queue (hctx)", size=12, anchor="middle"))
    
    frags.append(text(400, 380, "Hardware Dispatch (NVMe/SCSI)", bold=True, anchor="middle"))
    
    return frags

def main():
    os.makedirs("figs", exist_ok=True)
    frags = blk_mq_arch()
    render(os.path.join(IMG, 'blk-mq-arch.svg'), 800, 450, *frags, title="Архітектура blk-mq")

if __name__ == "__main__":
    main()
