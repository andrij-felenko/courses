import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

try:
    from svgkit import render, text, line, rect, textbox, arrow, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    pass

def generate():
    # Малюємо часову шкалу: 
    # Зверху: звичайний periodic tick
    # Середина: NO_HZ_IDLE
    # Низ: NO_HZ_FULL
    
    frags = []
    
    # 1. Periodic Tick
    frags.append(text(400, 30, "Periodic Tick (CONFIG_HZ)", size=16, bold=True))
    frags.append(line(50, 60, 750, 60, sw=2))
    for i in range(1, 15):
        x = 50 + i * 45
        frags.append(line(x, 50, x, 70, color=NEG, sw=2))
        if i == 1:
            frags.append(text(x, 40, "Tick", size=10, color=NEG))
    
    # 2. NO_HZ_IDLE
    frags.append(text(400, 120, "Dynamic Ticks (NO_HZ_IDLE)", size=16, bold=True))
    frags.append(line(50, 150, 750, 150, sw=2))
    
    # User process running
    frags.append(rect(100, 140, 200, 20, fill=FIELD, stroke=FIELD))
    frags.append(text(200, 155, "User Process", size=12, color=BG, bold=True))
    
    # Idle period
    frags.append(rect(300, 140, 200, 20, fill="#eeeeee", stroke=LINE))
    frags.append(text(400, 155, "Idle (C-States)", size=12, color=MUTED, italic=True))
    
    # Ticks during process execution
    for i in range(1, 5):
        x = 50 + i * 45
        frags.append(line(x, 140, x, 160, color=NEG, sw=2))
    
    # No ticks during idle
    
    # Next process
    frags.append(rect(500, 140, 100, 20, fill=FIELD, stroke=FIELD))
    frags.append(text(550, 155, "User Process", size=12, color=BG, bold=True))
    for i in range(11, 13):
        x = 50 + i * 45
        frags.append(line(x, 140, x, 160, color=NEG, sw=2))
        
    # 3. NO_HZ_FULL
    frags.append(text(400, 210, "Adaptive Tickless (NO_HZ_FULL)", size=16, bold=True))
    frags.append(line(50, 240, 750, 240, sw=2))
    
    # Long user process
    frags.append(rect(100, 230, 600, 20, fill=FIELD, stroke=FIELD))
    frags.append(text(400, 245, "Single Runnable User Process (100% CPU)", size=12, color=BG, bold=True))
    
    # Only one initial tick maybe, then no ticks
    frags.append(line(95, 230, 95, 250, color=NEG, sw=2))
    frags.append(text(95, 220, "Last Tick", size=10, color=NEG))
    
    render('nohz-timeline.svg', 800, 300, *frags)

if __name__ == '__main__':
    generate()
