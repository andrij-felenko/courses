import sys, os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def draw():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, 'job-control-arch.svg')
    
    frags = []
    # Session Box
    frags.append(rect(10, 10, 580, 380, fill="#f8f9fa", stroke="#6b7280", sw=2, rx=10))
    frags.append(text(300, 30, "Сесія (SID = 100, Лідер = bash)", size=16, bold=True))
    
    # Controlling Terminal Box
    frags.append(rect(30, 60, 160, 70, fill="#eaf0fd", stroke="#2457d6"))
    frags.append(text(110, 85, "Управляючий", size=14, bold=True, color="#2457d6"))
    frags.append(text(110, 105, "термінал (TTY)", size=14, bold=True, color="#2457d6"))
    frags.append(text(110, 120, "/dev/pts/1", size=11, color="#6b7280"))
    
    # Foreground Process Group Box
    frags.append(rect(220, 60, 350, 120, fill="#fdecea", stroke="#c0392b", sw=2))
    frags.append(text(395, 85, "Foreground Група (PGID = 200)", size=14, bold=True, color="#c0392b"))
    frags.append(rect(240, 105, 120, 50, fill="#ffffff", stroke="#333333"))
    frags.append(text(300, 125, "make", size=14, bold=True))
    frags.append(text(300, 140, "PID = 200", size=12))
    
    frags.append(rect(430, 105, 120, 50, fill="#ffffff", stroke="#333333"))
    frags.append(text(490, 125, "gcc", size=14, bold=True))
    frags.append(text(490, 140, "PID = 201", size=12))
    
    frags.append(arrow(360, 130, 430, 130))
    
    # Background Process Group Box 1
    frags.append(rect(220, 200, 350, 80, fill="#eef2f3", stroke="#6b7280", sw=1.5))
    frags.append(text(395, 225, "Background Група (PGID = 150)", size=14, bold=True, color="#6b7280"))
    frags.append(rect(340, 240, 110, 30, fill="#ffffff", stroke="#333333"))
    frags.append(text(395, 260, "sleep 100", size=13))
    
    # Background Process Group Box 2 (shell itself)
    frags.append(rect(30, 200, 160, 80, fill="#eef2f3", stroke="#6b7280", sw=1.5))
    frags.append(text(110, 225, "Background", size=13, bold=True, color="#6b7280"))
    frags.append(text(110, 245, "Група (PGID=100)", size=12, color="#6b7280"))
    frags.append(rect(50, 255, 120, 18, fill="#ffffff", stroke="#333333"))
    frags.append(text(110, 268, "bash", size=12))
    
    # Arrows and relations
    frags.append(arrow(110, 130, 220, 110))
    frags.append(text(165, 95, "tcsetpgrp()", size=11, color="#2457d6"))
    frags.append(text(165, 150, "Ctrl+Z", size=13, color="#c0392b", bold=True))
    frags.append(text(165, 165, "(SIGTSTP)", size=11, color="#c0392b"))
    
    render(path, 600, 400, *frags)

if __name__ == '__main__':
    draw()
