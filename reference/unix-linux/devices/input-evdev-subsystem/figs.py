import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import render, rect, text, arrow

def draw():
    frags = []
    
    # Hardware, Device Drivers, Input Core, Event Handlers, User Space
    frags.append(rect(50, 400, 700, 60, fill="#f0f0f0", stroke="#333", sw=2))
    frags.append(text(400, 435, "Hardware (USB, I2C, PS/2, Bluetooth)", size=20))
    
    frags.append(rect(50, 300, 700, 60, fill="#d0e0ff", stroke="#333", sw=2))
    frags.append(text(400, 335, "Device Drivers (usbhid, i2c-hid, psmouse)", size=20))
    
    frags.append(rect(50, 200, 700, 60, fill="#ffeedd", stroke="#333", sw=2))
    frags.append(text(400, 235, "Input Core (input.c)", size=20, bold=True))
    
    # Event Handlers
    frags.append(rect(100, 100, 150, 60, fill="#e0ffe0", stroke="#333", sw=2))
    frags.append(text(175, 135, "evdev", size=20))
    
    frags.append(rect(325, 100, 150, 60, fill="#e0ffe0", stroke="#333", sw=2))
    frags.append(text(400, 135, "mousedev", size=20))
    
    frags.append(rect(550, 100, 150, 60, fill="#e0ffe0", stroke="#333", sw=2))
    frags.append(text(625, 135, "joydev", size=20))
    
    # User Space
    frags.append(rect(50, 10, 700, 60, fill="#f9f9f9", stroke="#333", sw=2))
    frags.append(text(400, 45, "User Space (libinput, Xorg, Wayland, evtest)", size=20))
    
    # Arrows
    frags.append(arrow(400, 400, 400, 365))
    frags.append(arrow(400, 300, 400, 265))
    
    frags.append(arrow(175, 200, 175, 165))
    frags.append(arrow(400, 200, 400, 165))
    frags.append(arrow(625, 200, 625, 165))
    
    frags.append(arrow(175, 100, 175, 75))
    frags.append(arrow(400, 100, 400, 75))
    frags.append(arrow(625, 100, 625, 75))
    
    # Labels
    frags.append(text(200, 85, "/dev/input/eventX", size=14, color="#555"))
    frags.append(text(425, 85, "/dev/input/mice", size=14, color="#555"))
    frags.append(text(650, 85, "/dev/input/jsX", size=14, color="#555"))
    
    render(os.path.join(IMG, 'input-subsystem.svg'), 800, 500, *frags)

if __name__ == '__main__':
    draw()
