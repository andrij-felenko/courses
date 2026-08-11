import sys
import os

# Add scripts directory to path (four levels up since we are in E:/develop/courses/reference/unix-linux/io/nvme-target-kernel-subsystem/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def draw():
    frags = []
    
    # User Space
    frags.append(rect(30, 60, 740, 100, fill="#e6f7ff", stroke="#91d5ff"))
    frags.append(text(400, 85, "User Space", size=16, bold=True))
    
    frags.append(rect(100, 100, 150, 40, rx=5, fill="#bae7ff", stroke="#1890ff"))
    frags.append(text(175, 125, "nvmetcli", size=14))
    
    frags.append(rect(550, 100, 150, 40, rx=5, fill="#bae7ff", stroke="#1890ff"))
    frags.append(text(625, 125, "configfs API", size=14))
    
    # Kernel Space
    frags.append(rect(30, 180, 740, 290, fill="#f6ffed", stroke="#b7eb8f"))
    frags.append(text(400, 205, "Kernel Space", size=16, bold=True))
    
    # Core nvmet
    frags.append(rect(250, 240, 300, 60, rx=5, fill="#d9f7be", stroke="#52c41a"))
    frags.append(text(400, 275, "nvmet (Core NVMe Target)", size=16, bold=True))
    
    # Transports
    frags.append(rect(150, 340, 120, 50, rx=5, fill="#fff1b8", stroke="#faad14"))
    frags.append(text(210, 370, "nvmet-tcp", size=14))
    
    frags.append(rect(340, 340, 120, 50, rx=5, fill="#fff1b8", stroke="#faad14"))
    frags.append(text(400, 370, "nvmet-rdma", size=14))
    
    frags.append(rect(530, 340, 120, 50, rx=5, fill="#fff1b8", stroke="#faad14"))
    frags.append(text(590, 370, "nvmet-fc", size=14))
    
    # Backends
    frags.append(rect(250, 410, 300, 40, rx=5, fill="#ffd6e7", stroke="#eb2f96"))
    frags.append(text(400, 435, "Block Device / File Backend", size=14))
    
    # Arrows
    frags.append(arrow(175, 140, 175, 240))
    frags.append(arrow(625, 140, 625, 240))
    frags.append(arrow(400, 300, 210, 340))
    frags.append(arrow(400, 300, 400, 340))
    frags.append(arrow(400, 300, 590, 340))
    
    return frags

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "nvmet-arch.svg")
    frags = draw()
    render(out_path, 800, 500, *frags, title="NVMe Target (nvmet) Architecture in Linux Kernel")
