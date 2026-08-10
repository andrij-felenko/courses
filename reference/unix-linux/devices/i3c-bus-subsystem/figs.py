import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import rect, text, line, arrow, render, mtext

def render_arch():
    frags = []
    
    # I3C Core
    frags.append(rect(200, 150, 200, 80, fill="#cce5ff", stroke="#004085", rx=10))
    frags.append(text(300, 185, "I3C Core", anchor="middle", color="#004085", bold=True))
    frags.append(text(300, 210, "(i3c-core.c)", anchor="middle", color="#004085", size=12))

    # I3C Master Controller
    frags.append(rect(200, 280, 200, 60, fill="#d4edda", stroke="#155724", rx=10))
    frags.append(text(300, 310, "I3C Master Controller Driver", anchor="middle", color="#155724", bold=True))

    # Device drivers
    frags.append(rect(50, 50, 150, 60, fill="#fff3cd", stroke="#856404", rx=10))
    frags.append(text(125, 80, "I3C Device Driver", anchor="middle", color="#856404", bold=True))

    frags.append(rect(400, 50, 150, 60, fill="#fff3cd", stroke="#856404", rx=10))
    frags.append(text(475, 75, "I2C Device Driver", anchor="middle", color="#856404", bold=True))
    frags.append(text(475, 95, "(via i2c_adapter)", anchor="middle", color="#856404", size=12))

    # I2C Subsystem
    frags.append(rect(400, 150, 150, 80, fill="#e2e3e5", stroke="#383d41", rx=10))
    frags.append(text(475, 190, "I2C Subsystem", anchor="middle", color="#383d41", bold=True))
    
    # Arrows
    frags.append(arrow(125, 110, 250, 150, color="#000"))
    frags.append(arrow(475, 110, 475, 150, color="#000"))
    frags.append(arrow(400, 190, 400, 190, color="#000"))
    
    frags.append(arrow(300, 230, 300, 280, color="#000"))
    frags.append(arrow(400, 200, 350, 280, color="#000"))

    # Hardware
    frags.append(rect(100, 370, 400, 30, fill="#6c757d", stroke="#343a40"))
    frags.append(text(300, 390, "I3C Hardware Bus (SCL / SDA)", anchor="middle", color="white", bold=True))

    frags.append(arrow(300, 340, 300, 370, color="#000"))
    
    render("fig-i3c-linux-arch.svg", 600, 450, *frags)

def render_daa():
    frags = []
    
    frags.append(rect(50, 50, 120, 50, fill="#cce5ff", stroke="#004085"))
    frags.append(text(110, 80, "I3C Master", anchor="middle", color="#004085", bold=True))

    frags.append(rect(250, 50, 120, 50, fill="#fff3cd", stroke="#856404"))
    frags.append(text(310, 80, "I3C Device 1", anchor="middle", color="#856404", bold=True))

    frags.append(rect(450, 50, 120, 50, fill="#fff3cd", stroke="#856404"))
    frags.append(text(510, 80, "I3C Device 2", anchor="middle", color="#856404", bold=True))

    # Timelines
    frags.append(line(110, 100, 110, 280, color="#000", dash="4"))
    frags.append(line(310, 100, 310, 280, color="#000", dash="4"))
    frags.append(line(510, 100, 510, 280, color="#000", dash="4"))

    # ENTDAA Broadcast
    frags.append(arrow(110, 130, 600, 130, color="#004085"))
    frags.append(text(150, 120, "Broadcast CCC: ENTDAA", color="#004085", size=12))

    # PID Send
    frags.append(arrow(310, 170, 110, 170, color="#856404"))
    frags.append(text(210, 160, "Send PID 1", color="#856404", size=12, anchor="middle"))

    frags.append(line(510, 190, 310, 190, color="#dc3545", dash="4"))
    frags.append(text(410, 180, "Send PID 2 (Lost Arbit)", color="#dc3545", size=12, anchor="middle"))

    # Master Assigns Address
    frags.append(arrow(110, 220, 310, 220, color="#28a745"))
    frags.append(text(210, 210, "Assign Dyn Addr", color="#28a745", size=12, anchor="middle"))

    # Loop for Device 2
    frags.append(arrow(110, 250, 510, 250, color="#004085"))
    frags.append(text(150, 240, "Repeat ENTDAA cycle for remaining...", color="#004085", size=12))

    render("fig-i3c-daa.svg", 700, 350, *frags)

if __name__ == "__main__":
    render_arch()
    render_daa()
