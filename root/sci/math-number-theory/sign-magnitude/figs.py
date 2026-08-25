import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    os.makedirs('img', exist_ok=True)
    
    frags = []
    
    # 8-bit word
    x_start = 50
    y_start = 80
    box_width = 80
    box_height = 60
    
    for i in range(8):
        x = x_start + i * box_width
        # Sign bit
        if i == 0:
            frags.append(rect(x, y_start, box_width, box_height, fill='#ffebee', stroke='black'))
            frags.append(text(x + box_width/2, y_start + box_height/2 + 5, 'S', size=24, bold=True))
            frags.append(text(x + box_width/2, y_start - 10, 'Знак (1 біт)', size=16))
        else:
            frags.append(rect(x, y_start, box_width, box_height, fill='#e3f2fd', stroke='black'))
            frags.append(text(x + box_width/2, y_start + box_height/2 + 5, f'M{7-i}', size=24))
    
    # Mantissa label
    frags.append(line(x_start + box_width, y_start + box_height + 20, x_start + 8*box_width, y_start + box_height + 20, color='black', sw=2))
    frags.append(line(x_start + box_width, y_start + box_height + 10, x_start + box_width, y_start + box_height + 20, color='black', sw=2))
    frags.append(line(x_start + 8*box_width, y_start + box_height + 10, x_start + 8*box_width, y_start + box_height + 20, color='black', sw=2))
    frags.append(text(x_start + 4.5*box_width, y_start + box_height + 40, 'Величина / Мантиса (7 біт)', size=16))
    
    render('img/fig-sign-magnitude-word.svg', 800, 200, *frags, title='Формат знаку і величини у двійковому слові')

if __name__ == '__main__':
    main()
