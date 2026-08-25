import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

from svgkit import *

def make_bot_vs_uas_svg():
    w, h = 800, 350
    frags = []
    
    # BOT Section
    frags.append(rect(10, 10, 380, 330, fill="#f8f9fa", stroke="#dee2e6"))
    frags.append(text(200, 35, "Bulk-Only Transport (BOT)", size=14, bold=True))
    
    frags.append(rect(30, 60, 150, 40, rx=5, fill="#e9ecef", stroke="#6c757d"))
    frags.append(text(105, 85, "USB Host (usb-storage)", size=12))
    
    frags.append(rect(220, 60, 150, 40, rx=5, fill="#e9ecef", stroke="#6c757d"))
    frags.append(text(295, 85, "USB Device (Flash)", size=12))
    
    # Commands BOT
    frags.append(text(200, 125, "CBW (Command Block)", size=11, color="#0d6efd"))
    frags.append(arrow(105, 135, 295, 135, color="#0d6efd", sw=2))
    
    frags.append(text(200, 175, "Data Out / Data In", size=11, color="#198754"))
    frags.append(line(105, 185, 295, 185, color="#198754", sw=2, dash="4,4"))
    
    frags.append(text(200, 225, "CSW (Status Block)", size=11, color="#dc3545"))
    frags.append(arrow(295, 235, 105, 235, color="#dc3545", sw=2))
    
    frags.append(text(200, 290, "Sync, 1 Command at a time", size=12, italic=True))
    
    # UAS Section
    frags.append(rect(410, 10, 380, 330, fill="#f8f9fa", stroke="#dee2e6"))
    frags.append(text(600, 35, "USB Attached SCSI (UAS)", size=14, bold=True))
    
    frags.append(rect(430, 60, 150, 40, rx=5, fill="#e9ecef", stroke="#6c757d"))
    frags.append(text(505, 85, "USB Host (uas)", size=12))
    
    frags.append(rect(620, 60, 150, 40, rx=5, fill="#e9ecef", stroke="#6c757d"))
    frags.append(text(695, 85, "USB Device (SSD)", size=12))
    
    # Pipes
    pipes = ["Command Pipe", "Status Pipe", "Data IN Pipe", "Data OUT Pipe"]
    colors = ["#0d6efd", "#dc3545", "#198754", "#198754"]
    y_starts = [120, 170, 220, 270]
    
    for i, (p, c, y) in enumerate(zip(pipes, colors, y_starts)):
        frags.append(text(600, y-5, p, size=11, color=c))
        if i == 1 or i == 2:
            # Device to Host
            frags.append(arrow(695, y+5, 505, y+5, color=c, sw=2))
        else:
            # Host to Device
            frags.append(arrow(505, y+5, 695, y+5, color=c, sw=2))

    frags.append(text(600, 320, "Async, NCQ (Native Command Queuing)", size=12, italic=True))

    render("img/bot-vs-uas.svg", w, h, *frags)

if __name__ == "__main__":
    make_bot_vs_uas_svg()
