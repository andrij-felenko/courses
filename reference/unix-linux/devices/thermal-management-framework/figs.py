import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def make_thermal_arch():
    w, h = 800, 500
    frags = [
        # Kernel Space
        rect(50, 70, 700, 360, fill="#e8f4fa", stroke="#a2c4d8", rx=10),
        text(400, 90, "Kernel Space", color="#3b5b72", size=16),
        
        # Thermal Core
        rect(250, 150, 300, 100, fill="#c3deef", stroke="#5792b5", rx=5),
        text(400, 175, "Thermal Core", color="#1c3b52", size=18, bold=True),
        text(400, 210, "/sys/class/thermal/", color="#2f5b7a", size=14),
        
        # Governors
        rect(100, 150, 120, 100, fill="#d2f2d9", stroke="#66a877", rx=5),
        text(160, 180, "Governors", color="#2a5737", size=16, bold=True),
        text(160, 205, "(Step_wise,", color="#3c6b4b", size=12),
        text(160, 220, "Power_allocator)", color="#3c6b4b", size=12),
        
        # Thermal Zones & Sensors
        rect(200, 320, 180, 80, fill="#f9e3e3", stroke="#b56363", rx=5),
        text(290, 350, "Thermal Zones", color="#612323", size=16, bold=True),
        text(290, 375, "(Sensors / Trip Points)", color="#753535", size=12),
        
        # Cooling Devices
        rect(420, 320, 180, 80, fill="#e1f0ec", stroke="#629e8e", rx=5),
        text(510, 350, "Cooling Devices", color="#23473f", size=16, bold=True),
        text(510, 375, "(cpufreq, devfreq, fan)", color="#355c53", size=12),
        
        # Hardware
        rect(50, 450, 700, 40, fill="#f0f0f0", stroke="#cccccc"),
        text(400, 470, "Hardware (SoC, Thermistors, Fans, CPU)", color="#555555", size=14),
        
        # Arrows
        arrow(220, 200, 245, 200, sw=2),
        arrow(250, 210, 225, 210, sw=2),
        arrow(290, 320, 350, 255, sw=2),
        arrow(450, 255, 510, 320, sw=2)
    ]
    render(os.path.join(IMG, 'thermal-arch.svg'), w, h, *frags, title="Linux Thermal Framework Architecture")

if __name__ == '__main__':
    make_thermal_arch()
