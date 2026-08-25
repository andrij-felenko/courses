import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import rect, text, arrow, render
except ImportError:
    print("Warning: svgkit not found.")
    sys.exit(0)

def draw_reisub_flow(filename):
    frags = []
    
    # Draw boxes for REISUB sequence
    seq = [
        ('R', 'unRaw', 'Повертає керування клавіатурою'),
        ('E', 'tErminate', 'Надсилає SIGTERM'),
        ('I', 'kIll', 'Надсилає SIGKILL'),
        ('S', 'Sync', 'Синхронізує диски'),
        ('U', 'Unmount', 'Перемонтовує read-only'),
        ('B', 'reBoot', 'Перезавантаження')
    ]
    
    x_start = 50
    y_start = 100
    box_width = 100
    box_height = 80
    gap = 30
    
    for i, (key, name, desc) in enumerate(seq):
        x = x_start + i * (box_width + gap)
        frags.append(rect(x, y_start, box_width, box_height, fill='#e0f7fa', stroke='#006064', rx=10))
        frags.append(text(x + box_width/2, y_start + 30, key, size=24, bold=True))
        frags.append(text(x + box_width/2, y_start + 50, name, size=12))
        
        # split desc into two lines if long, or just smaller text
        if len(desc) > 20:
            words = desc.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            frags.append(text(x + box_width/2, y_start + 65, line1, size=9))
            frags.append(text(x + box_width/2, y_start + 75, line2, size=9))
        else:
            frags.append(text(x + box_width/2, y_start + 65, desc, size=9))
            
        if i < len(seq) - 1:
            frags.append(arrow(x + box_width, y_start + box_height/2, x + box_width + gap, y_start + box_height/2))
            
    render(filename, 900, 300, *frags, title="Схема ланцюжка безпечного завершення системи через SysRq (REISUB)")

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    draw_reisub_flow(os.path.join(out_dir, 'sysrq-reisub.svg'))
