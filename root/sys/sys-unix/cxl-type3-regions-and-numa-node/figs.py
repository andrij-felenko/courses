import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def build_cxl_mem_path():
    frags = []

    # CPU Node
    frags.append(rect(50, 50, 300, 200, rx=10, fill="#e3f2fd", stroke="#1565c0", sw=2))
    frags.append(text(200, 80, "CPU (NUMA Node 0)", size=16, color="#0d47a1", bold=True))

    # Cores
    frags.append(rect(80, 110, 100, 60, rx=5, fill="#bbdefb", stroke="#1976d2", sw=1))
    frags.append(text(130, 145, "Core 0", size=14))

    frags.append(rect(220, 110, 100, 60, rx=5, fill="#bbdefb", stroke="#1976d2", sw=1))
    frags.append(text(270, 145, "Core 1", size=14))

    # CXL Root Port
    frags.append(rect(50, 270, 300, 60, rx=5, fill="#ffe0b2", stroke="#e65100", sw=2))
    frags.append(text(200, 305, "CXL Root Port (Host Bridge)", size=14, bold=True))

    # CXL Type 3 Device — рамка охоплює і контролер, і його власні модулі DDR
    frags.append(rect(450, 60, 330, 360, rx=10, fill="#e8f5e9", stroke="#2e7d32", sw=2))
    frags.append(text(615, 95, "CXL Type 3 Device", size=16, color="#1b5e20", bold=True))
    frags.append(text(615, 120, "(CPU-less NUMA Node)", size=12, color="#1b5e20"))

    # DDR modules — усередині пристрою
    frags.append(rect(480, 155, 80, 95, rx=5, fill="#d1c4e9", stroke="#512da8", sw=1))
    frags.append(text(520, 208, "DDR5", size=14, color="#311b92"))

    frags.append(rect(580, 155, 80, 95, rx=5, fill="#d1c4e9", stroke="#512da8", sw=1))
    frags.append(text(620, 208, "DDR5", size=14, color="#311b92"))

    frags.append(rect(680, 155, 80, 95, rx=5, fill="#d1c4e9", stroke="#512da8", sw=1))
    frags.append(text(720, 208, "DDR5", size=14, color="#311b92"))

    # CXL Controller
    frags.append(rect(490, 340, 250, 60, rx=5, fill="#c8e6c9", stroke="#388e3c", sw=1))
    frags.append(text(615, 375, "CXL Controller (cxl_mem)", size=14))

    # Arrows
    frags.append(arrow(200, 250, 200, 270, color="#000", sw=2))
    frags.append(text(210, 260, "Coherent Interconnect", size=10, color="#555", anchor="start"))

    frags.append(arrow(350, 300, 450, 300, color="#e65100", sw=3))
    frags.append(text(400, 290, "CXL.mem / PCIe", size=12, bold=True, color="#e65100"))

    frags.append(arrow(520, 340, 520, 250, color="#512da8", sw=2))
    frags.append(arrow(620, 340, 620, 250, color="#512da8", sw=2))
    frags.append(arrow(720, 340, 720, 250, color="#512da8", sw=2))

    render(os.path.join(IMG, "cxl-mem-path.svg"), 800, 450, *frags)

if __name__ == "__main__":
    build_cxl_mem_path()
