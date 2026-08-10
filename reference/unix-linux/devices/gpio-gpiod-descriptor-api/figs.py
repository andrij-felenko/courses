import sys
import os

scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.append(scripts_dir)

from svgkit import render, textbox, arrow, rect, text

def render_gpio_api_svg():
    path = os.path.join(os.path.dirname(__file__), 'gpio_api.svg')
    
    frags = []
    
    # Old API block
    frags.append(rect(50, 50, 300, 250, fill="#fee", stroke="#c00", sw=2))
    frags.append(text(200, 80, "Legacy SysFS API", size=18, bold=True, color="#c00"))
    
    b1, _, _ = textbox(200, 135, "User: echo 4 > /sys/class/gpio/export", min_w=240, fill="#fff")
    frags.append(b1)
    
    b2, _, _ = textbox(200, 185, "Kernel: Global integer ID", min_w=240, fill="#fff")
    frags.append(b2)
    
    b3, _, _ = textbox(200, 235, "Cons: No ownership, slow", min_w=240, fill="#fff")
    frags.append(b3)
    
    # Arrow
    frags.append(arrow(360, 175, 440, 175, sw=4))
    
    # New API block
    frags.append(rect(450, 50, 300, 250, fill="#efe", stroke="#0a0", sw=2))
    frags.append(text(600, 80, "Modern gpiod API", size=18, bold=True, color="#0a0"))
    
    b4, _, _ = textbox(600, 135, "User: /dev/gpiochipN (libgpiod)", min_w=240, fill="#fff")
    frags.append(b4)
    
    b5, _, _ = textbox(600, 185, "Kernel: struct gpio_desc", min_w=240, fill="#fff")
    frags.append(b5)
    
    b6, _, _ = textbox(600, 235, "Pros: Atomic, secure, fast", min_w=240, fill="#fff")
    frags.append(b6)
    
    render(path, 800, 350, *frags)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render_gpio_api_svg()
