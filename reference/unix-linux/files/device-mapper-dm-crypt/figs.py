import sys
import os

# Додаємо шлях до scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_figs():
    # 1. Device Mapper Architecture
    frags1 = [
        rect(50, 50, 700, 100, fill="#f0f0f0", stroke="#333", sw=2),
        text(120, 80, "User Space", size=16, bold=True),
        
        rect(100, 90, 150, 40, fill="#d9edf7", stroke="#31708f"),
        text(175, 115, "LVM (lvm2)", size=14),
        
        rect(300, 90, 150, 40, fill="#d9edf7", stroke="#31708f"),
        text(375, 115, "cryptsetup", size=14),
        
        rect(500, 90, 150, 40, fill="#d9edf7", stroke="#31708f"),
        text(575, 115, "dmsetup", size=14),
        
        rect(300, 180, 200, 40, fill="#fcf8e3", stroke="#8a6d3b"),
        text(400, 205, "/dev/mapper/control (ioctl)", size=14),
        
        rect(50, 250, 700, 120, fill="#dff0d8", stroke="#3c763d", sw=2),
        text(145, 275, "Kernel Space (dm-mod)", size=16, bold=True),
        
        rect(100, 300, 150, 40, fill="#c4e3f3", stroke="#31708f"),
        text(175, 325, "Target: linear", size=14),
        
        rect(300, 300, 150, 40, fill="#c4e3f3", stroke="#31708f"),
        text(375, 325, "Target: crypt", size=14),
        
        rect(500, 300, 150, 40, fill="#c4e3f3", stroke="#31708f"),
        text(575, 325, "Target: snapshot", size=14),
        
        arrow(175, 130, 380, 180),
        arrow(375, 130, 400, 180),
        arrow(575, 130, 420, 180),
        arrow(400, 220, 400, 250)
    ]
    render(os.path.join(os.path.dirname(__file__), 'dm-architecture.svg'), 800, 400, *frags1)

    # 2. LUKS Header Structure
    frags2 = [
        rect(50, 50, 700, 300, fill="#f9f9f9", stroke="#333", sw=2),
        
        rect(70, 70, 660, 260, fill="#eee", stroke="#666"),
        text(400, 90, "Блоковий пристрій (/dev/sda1)", size=14),
        
        rect(90, 110, 200, 200, fill="#f2dede", stroke="#a94442"),
        text(190, 135, "LUKS Header", size=16, bold=True),
        
        rect(100, 150, 180, 30, fill="#ebccd1", stroke="#a94442"),
        text(190, 170, "Magic Number", size=12),
        
        rect(100, 185, 180, 30, fill="#ebccd1", stroke="#a94442"),
        text(190, 205, "Master Key Digest", size=12),
        
        rect(100, 220, 180, 80, fill="#ebccd1", stroke="#a94442"),
        text(190, 260, "Key Slots (0-7)", size=14),
        
        rect(320, 110, 390, 200, fill="#dff0d8", stroke="#3c763d"),
        text(515, 210, "Зашифровані дані (Payload)", size=16, bold=True),
        
        arrow(290, 210, 320, 210),
        text(290, 100, "Ключ слоту -> розшифровує Master Key -> Master Key розшифровує дані", size=12)
    ]
    render(os.path.join(os.path.dirname(__file__), 'luks-structure.svg'), 800, 400, *frags2, title="Структура LUKS")

if __name__ == '__main__':
    render_figs()
