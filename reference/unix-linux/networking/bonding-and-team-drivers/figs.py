import os
import sys

# Додаємо scripts до PYTHONPATH (чотири рівні вгору з reference/unix-linux/networking/bonding-and-team-drivers)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def make_bonding_arch():
    out = []
    
    # Server
    out.append(rect(50, 50, 150, 200, fill="#f4f6f8"))
    out.append(text(125, 70, "Server", size=16, bold=True))
    
    out.append(textbox(125, 120, "eth0", 14)[0])
    out.append(textbox(125, 180, "eth1", 14)[0])
    
    # Switch
    out.append(rect(500, 50, 150, 200, fill="#f4f6f8"))
    out.append(text(575, 70, "Switch", size=16, bold=True))
    
    out.append(textbox(575, 120, "port 1", 14)[0])
    out.append(textbox(575, 180, "port 2", 14)[0])
    
    # Links
    out.append(line(180, 120, 520, 120, sw=4, color="#3498db"))
    out.append(line(180, 180, 520, 180, sw=4, color="#3498db"))
    
    # Logical link
    out.append(textbox(350, 80, "Логічний канал\n(bond0 / team0)", 14, color="#c0392b", min_w=200, bold=True)[0])
    
    render("bonding_arch.svg", 700, 300, *out, title="Архітектура агрегації каналів (Bonding / Team)")

if __name__ == "__main__":
    make_bonding_arch()
