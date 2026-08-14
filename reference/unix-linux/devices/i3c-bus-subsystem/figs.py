import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import rect, text, line, arrow, render, mtext, textbox

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

def render_arch():
    frags = []
    
    # Header / Title background area
    frags.append(rect(10, 10, 680, 420, fill="#fafbfc", stroke="#d1d5db", rx=8))
    
    # Layer 1: Userspace
    frags.append(rect(30, 30, 640, 50, fill="#eef2ff", stroke="#6366f1", rx=6))
    frags.append(text(350, 52, "Простір користувача (Userspace)", size=14, color="#3730a3", bold=True))
    frags.append(text(350, 70, "/sys/bus/i3c/devices  |  cdev /dev/i3c-*  |  i2c-dev", size=12, color="#4338ca"))

    # Layer 2: Driver & Subsystem layer
    frags.append(rect(30, 95, 290, 70, fill="#fef3c7", stroke="#d97706", rx=6))
    frags.append(text(175, 122, "I3C Device Drivers", size=13, color="#92400e", bold=True))
    frags.append(text(175, 145, "i3c_driver (сенсори, PMIC)", size=11, color="#b45309"))

    frags.append(rect(380, 95, 290, 70, fill="#fef3c7", stroke="#d97706", rx=6))
    frags.append(text(525, 122, "Legacy I2C Device Drivers", size=13, color="#92400e", bold=True))
    frags.append(text(525, 145, "i2c_driver (через i2c_adapter)", size=11, color="#b45309"))

    # Core
    frags.append(rect(30, 180, 640, 75, fill="#dbeafe", stroke="#2563eb", rx=6))
    frags.append(text(350, 205, "Ядро підсистеми I3C (i3c-core.c)", size=14, color="#1e40af", bold=True))
    frags.append(text(350, 227, "Управління шиною, DAA, CCC команди, IBI переривання, Hot-Join", size=12, color="#1d4ed8"))
    frags.append(text(350, 245, "Адаптер сумісності I2C (struct i2c_adapter)", size=11, color="#2563eb", italic=True))

    # Master Controller Driver
    frags.append(rect(30, 270, 640, 60, fill="#dcfce7", stroke="#16a34a", rx=6))
    frags.append(text(350, 295, "Драйвер I3C майстер-контролера (i3c_master_controller)", size=13, color="#14532d", bold=True))
    frags.append(text(350, 317, "dw-i3c-master, cdns-i3c-master, mipi-i3c-hci", size=11, color="#15803d"))

    # Hardware Layer
    frags.append(rect(30, 345, 640, 70, fill="#f3f4f6", stroke="#4b5563", rx=6))
    frags.append(text(350, 368, "Апаратні пристрої та шина (I3C Bus PHY)", size=13, color="#1f2937", bold=True))
    frags.append(text(350, 390, "Двопровідна лінія SDA / SCL  |  I3C Target (SDR/HDR)  |  I2C Target (Legacy)", size=11, color="#374151"))

    # Arrows connecting layers
    frags.append(arrow(350, 80, 350, 95, color="#4b5563"))
    frags.append(arrow(175, 165, 175, 180, color="#4b5563"))
    frags.append(arrow(525, 165, 525, 180, color="#4b5563"))
    frags.append(arrow(350, 255, 350, 270, color="#4b5563"))
    frags.append(arrow(350, 330, 350, 345, color="#4b5563"))

    render(os.path.join(IMG, 'fig-i3c-linux-arch.svg'), 700, 440, *frags)

def render_daa():
    frags = []

    frags.append(rect(10, 10, 720, 340, fill="#ffffff", stroke="#e5e7eb", rx=8))

    # Master and Device Columns
    frags.append(rect(40, 30, 140, 45, fill="#dbeafe", stroke="#2563eb", rx=6))
    frags.append(text(110, 57, "I3C Master", size=13, color="#1e40af", bold=True))

    frags.append(rect(280, 30, 150, 45, fill="#fef3c7", stroke="#d97706", rx=6))
    frags.append(text(355, 57, "Target 1 (Low PID)", size=13, color="#92400e", bold=True))

    frags.append(rect(530, 30, 150, 45, fill="#fee2e2", stroke="#dc2626", rx=6))
    frags.append(text(605, 57, "Target 2 (High PID)", size=13, color="#991b1b", bold=True))

    # Timeline vertical dashed lines
    frags.append(line(110, 75, 110, 320, color="#9ca3af", dash="4"))
    frags.append(line(355, 75, 355, 320, color="#9ca3af", dash="4"))
    frags.append(line(605, 75, 605, 320, color="#9ca3af", dash="4"))

    # Step 1: Broadcast ENTDAA
    frags.append(arrow(110, 105, 605, 105, color="#2563eb"))
    frags.append(text(355, 97, "1. Broadcast CCC: ENTDAA (0x07)", size=11, color="#1e40af", bold=True))

    # Step 2: PID Transmission & Open-drain arbitration
    frags.append(arrow(355, 145, 110, 145, color="#d97706"))
    frags.append(text(230, 137, "2. Передача 48-bit PID", size=11, color="#92400e"))

    frags.append(line(605, 160, 460, 160, color="#dc2626"))
    frags.append(text(530, 152, "Програш арбітражу (0 > 0)", size=10, color="#dc2626", italic=True))

    # Step 3: Master Assigns Address to Target 1
    frags.append(arrow(110, 200, 355, 200, color="#16a34a"))
    frags.append(text(230, 192, "3. Set DynAddr = 0x08", size=11, color="#15803d", bold=True))

    # Step 4: Target 1 ACK and Exits DAA
    frags.append(arrow(355, 235, 110, 235, color="#16a34a"))
    frags.append(text(230, 227, "4. ACK (Target 1 активний)", size=11, color="#15803d"))

    # Step 5: Next ENTDAA cycle for Target 2
    frags.append(arrow(110, 275, 605, 275, color="#2563eb"))
    frags.append(text(355, 267, "5. ENTDAA повтор (Target 2 отримує 0x09)", size=11, color="#1e40af", bold=True))

    # Finish step
    frags.append(arrow(110, 305, 605, 305, color="#4b5563"))
    frags.append(text(355, 297, "6. Завершення DAA (немає відповідей -> STOP)", size=11, color="#374151", italic=True))

    render(os.path.join(IMG, 'fig-i3c-daa.svg'), 740, 360, *frags)

if __name__ == "__main__":
    render_arch()
    render_daa()
