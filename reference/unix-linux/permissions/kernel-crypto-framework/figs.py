import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_arch():
    out_dir = os.path.dirname(__file__)
    path = os.path.join(out_dir, "crypto-arch.svg")
    
    frags = [
        # Backgrounds
        rect(30, 30, 740, 100, fill="#e1f5fe", stroke="#0277bd"),
        text(400, 80, "User Space (Applications, OpenSSL, AF_ALG sockets)", size=18, bold=True, color="#01579b"),
        
        rect(30, 150, 740, 200, fill="#e8f5e9", stroke="#2e7d32"),
        text(400, 180, "Kernel Space (Linux Crypto API)", size=18, bold=True, color="#1b5e20"),
        
        # Kernel boxes
        rect(50, 200, 200, 120, fill="#c8e6c9", stroke="#388e3c"),
        text(150, 240, "Crypto Core", size=16, bold=True),
        text(150, 270, "Framework & Registry", size=14),
        text(150, 290, "/proc/crypto", size=14),
        
        rect(270, 200, 200, 120, fill="#c8e6c9", stroke="#388e3c"),
        text(370, 230, "Kernel Subsystems", size=16, bold=True),
        text(370, 260, "IPsec, dm-crypt", size=14),
        text(370, 290, "ext4 crypto, mac80211", size=14),
        
        rect(490, 200, 260, 120, fill="#c8e6c9", stroke="#388e3c"),
        text(620, 230, "Algorithm Implementations", size=16, bold=True),
        text(620, 260, "Generic C (aes-generic)", size=14),
        text(620, 290, "Arch-specific (aes-ni)", size=14),
        
        # Hardware box
        rect(30, 370, 740, 100, fill="#fff3e0", stroke="#e65100"),
        text(400, 420, "Hardware Accelerators (Intel QAT, AMD CCP, ARM CE)", size=18, bold=True, color="#e65100"),
        
        # Arrows
        arrow(400, 130, 400, 150, color="#333", sw=2),
        arrow(400, 350, 400, 370, color="#333", sw=2)
    ]
    
    render(path, 800, 500, *frags, title="Архітектура Linux Kernel Crypto API")
    print("Generated crypto-arch.svg")

if __name__ == '__main__':
    render_arch()
