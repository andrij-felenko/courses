import sys
import os

scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, scripts_dir)

from svgkit import render, textbox, fitbox, arrow, rect, text, line, mtext, FILL, LINE, INK, POS, NEG, FIELD

def generate_figs():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    path = os.path.join(img_dir, 'gpio-api.svg')
    frags = []
    
    # Header / Title
    frags.append(text(450, 30, "Еволюція GPIO у Linux: Sysfs vs gpiod", size=18, bold=True, color="#1a1a1a"))
    
    # Left Column: Legacy Sysfs API
    frags.append(rect(30, 50, 390, 300, fill="#fff5f5", stroke="#e53e3e", sw=2, rx=8))
    frags.append(text(225, 80, "Застарілий Sysfs API (Legacy)", size=16, bold=True, color="#c53030"))
    
    b1, _, _ = textbox(225, 130, "Userspace: /sys/class/gpio/gpio42\nstrings ASCII ('echo 42 > export')", size=12, fill="#ffffff", stroke="#feb2b2", pad=8, min_w=340)
    frags.append(b1)
    
    b2, _, _ = textbox(225, 200, "Kernel: int gpio = 42\nГлобальні номери, раси, без автозвільнення", size=12, fill="#ffffff", stroke="#feb2b2", pad=8, min_w=340)
    frags.append(b2)
    
    b3, _, _ = textbox(225, 275, "Вади: Неатомарність, повільний ASCII,\nколізії номерів при гарячому підключенні", size=12, fill="#fff5f5", stroke="#e53e3e", pad=8, min_w=340)
    frags.append(b3)
    
    # Arrow between columns
    frags.append(arrow(430, 200, 470, 200, color="#4a5568", sw=3))
    
    # Right Column: Modern gpiod API
    frags.append(rect(480, 50, 390, 300, fill="#f0fff4", stroke="#38a169", sw=2, rx=8))
    frags.append(text(675, 80, "Сучасний Двоврівневий gpiod API", size=16, bold=True, color="#276749"))
    
    b4, _, _ = textbox(675, 130, "Userspace: /dev/gpiochipN (chardev v2)\nlibgpiod (C/C++), атомарні ioctl()", size=12, fill="#ffffff", stroke="#9ae6b4", pad=8, min_w=340)
    frags.append(b4)
    
    b5, _, _ = textbox(675, 200, "Kernel: struct gpio_desc*\nПрив'язка до dev, Active-Low, sleep semantics", size=12, fill="#ffffff", stroke="#9ae6b4", pad=8, min_w=340)
    frags.append(b5)
    
    b6, _, _ = textbox(675, 275, "Переваги: Атомарність bulk-ліній, RAII/FD,\nбезпека доступу, логічні рівні, debouncing", size=12, fill="#f0fff4", stroke="#38a169", pad=8, min_w=340)
    frags.append(b6)
    
    render(path, 900, 370, *frags)

if __name__ == '__main__':
    generate_figs()
