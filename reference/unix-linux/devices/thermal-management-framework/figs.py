import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def make_thermal_arch():
    w, h = 850, 520
    frags = [
        # Kernel Space container
        rect(30, 60, 790, 380, fill="#e8f4fa", stroke="#a2c4d8", rx=10),
        text(210, 80, "Kernel Space (Linux Thermal Subsystem)", size=14, bold=True, color="#3b5b72"),

        # User Space container
        rect(30, 10, 790, 40, fill="#fdf6e3", stroke="#d33682", rx=6),
        text(240, 35, "User Space (thermald, sysfs, Thermal Netlink Listener)", size=14, bold=True, color="#b58900"),

        # Thermal Core
        fitbox(280, 130, 290, 90, "Thermal Core (thermal_core.c)\n/sys/class/thermal/ (sysfs) & Netlink", fill="#c3deef", stroke="#5792b5", size=14, bold=True, color="#1c3b52"),

        # Governors
        fitbox(50, 130, 190, 90, "Thermal Governors\nstep_wise, power_allocator,\nbang_bang, fair_share", fill="#d2f2d9", stroke="#66a877", size=13, bold=True, color="#2a5737"),

        # Thermal Zones & Sensors
        fitbox(100, 280, 300, 130, "Thermal Zones (thermal_zone_device)\nSensors (x86 TSENS, ARM DT)\nTrip Points (passive, active, crit)\nHysteresis evaluation", fill="#f9e3e3", stroke="#b56363", size=13, bold=True, color="#612323"),

        # Cooling Devices
        fitbox(450, 280, 300, 130, "Cooling Devices (cooling_device)\ncpufreq / devfreq (DVFS)\nintel_powerclamp (idle injection)\nPWM Fans & Backlight", fill="#e1f0ec", stroke="#629e8e", size=13, bold=True, color="#23473f"),

        # Hardware Level
        rect(30, 460, 790, 50, fill="#f0f0f0", stroke="#cccccc", rx=6),
        text(425, 490, "Hardware Layer (SoC Cores, Thermal Diodes, Thermistors, PWM Fan Controllers)", size=13, color="#555555"),

        # Interconnecting Arrows
        arrow(240, 175, 280, 175, sw=2),
        arrow(425, 220, 250, 280, sw=2),
        arrow(425, 220, 600, 280, sw=2),
        arrow(600, 50, 600, 130, sw=2),
        arrow(250, 460, 250, 410, sw=2),
        arrow(600, 410, 600, 460, sw=2)
    ]
    render(os.path.join(IMG, 'thermal-arch.svg'), w, h, *frags, title="Linux Thermal Framework Architecture")

def make_trip_points_hysteresis():
    w, h = 850, 450
    frags = [
        # Grid / Background
        rect(10, 10, 830, 430, fill="#fafafa", stroke="#e0e0e0", rx=8),
        text(425, 35, "Температурна динаміка, точки спрацьовування та гістерезис", size=16, bold=True, color="#333333"),

        # Horizontal Trip Point Lines
        line(100, 90, 780, 90, color="#e74c3c", sw=2, dash="6,4"),
        text(220, 82, "Critical Trip Point (100°C)", size=12, bold=True, color="#c0392b"),

        line(100, 160, 780, 160, color="#e67e22", sw=2, dash="6,4"),
        text(210, 152, "Active Trip Point (70°C)", size=12, bold=True, color="#d35400"),

        line(100, 220, 780, 220, color="#27ae60", sw=2, dash="4,4"),
        text(240, 212, "Active Hysteresis Boundary (66°C)", size=12, bold=True, color="#27ae60"),

        line(100, 290, 780, 290, color="#3498db", sw=2, dash="6,4"),
        text(210, 282, "Passive Trip Point (50°C)", size=12, bold=True, color="#2980b9"),

        # Shaded Hysteresis Band
        rect(100, 160, 680, 60, fill="#27ae60", stroke="none"),
        text(600, 195, "Петля гістерезису ΔT_hyst = 4°C", size=12, bold=True, color="#1e8449"),

        # Temperature Curve Path
        '<path d="M 100 340 L 220 320 L 320 280 L 420 150 L 520 140 L 620 210 L 720 260 L 780 330" stroke="#c0392b" stroke-width="3" fill="none"/>',

        # Cooling State Indicators
        fitbox(380, 370, 280, 50, "Cooling Device Active (cur_state > 0)", fill="#e8f8f5", stroke="#1abc9c", size=13, bold=True, color="#16a085"),

        # Timeline Axis
        line(100, 360, 780, 360, color="#333333", sw=2),
        arrow(770, 360, 790, 360, sw=2),
        text(770, 380, "Час (t)", size=12, color="#333333")
    ]
    render(os.path.join(IMG, 'trip-points-hysteresis.svg'), w, h, *frags, title="Thermal Trip Points and Hysteresis Loop")

def make_power_allocator_pid():
    w, h = 850, 460
    frags = [
        rect(10, 10, 830, 440, fill="#fdfefe", stroke="#d6dbdf", rx=8),
        text(425, 35, "Контур зворотного зв'язку регулятора Power Allocator (PID Control)", size=16, bold=True, color="#2c3e50"),

        # Temperature Inputs
        fitbox(30, 90, 180, 80, "T_target (Trip Point)\nT_current (Sensor)", fill="#eaeded", stroke="#bdc3c7", size=13, bold=True, color="#34495e"),

        # Error Comparator
        fitbox(240, 90, 160, 80, "Помилка e(t) =\nT_target - T(t)", fill="#fef9e7", stroke="#f1c40f", size=13, bold=True, color="#b7950b"),

        # PID Controller Block
        fitbox(430, 80, 190, 100, "PID-контролер\nP_prop + P_integ + P_deriv\n+ P_sustainable", fill="#ebf5fb", stroke="#3498db", size=13, bold=True, color="#2171b5"),

        # Total Power Budget
        fitbox(650, 90, 170, 80, "Сумарний бюджет\nP_alloc (mW)", fill="#e8f8f5", stroke="#1abc9c", size=14, bold=True, color="#117864"),

        # Energy Model Allocator
        fitbox(240, 270, 380, 90, "Розподільник потужності (Energy Model)\nP_granted,i = P_alloc · (P_req,i / P_total_req)", fill="#f4ecf7", stroke="#af7ac5", size=13, bold=True, color="#6c3483"),

        # Actors (Cooling Devices)
        fitbox(50, 380, 210, 60, "CPU big Cluster (OPP)", fill="#fadbd8", stroke="#e74c3c", size=13, bold=True, color="#78281f"),
        fitbox(320, 380, 210, 60, "CPU LITTLE Cluster (OPP)", fill="#d5f5e3", stroke="#2ecc71", size=13, bold=True, color="#145a32"),
        fitbox(590, 380, 210, 60, "GPU / Devfreq (OPP)", fill="#e8daef", stroke="#9b59b6", size=13, bold=True, color="#4a235a"),

        # Arrows
        arrow(210, 130, 240, 130, sw=2),
        arrow(400, 130, 430, 130, sw=2),
        arrow(620, 130, 650, 130, sw=2),
        arrow(735, 170, 430, 270, sw=2),
        arrow(310, 360, 155, 380, sw=2),
        arrow(430, 360, 425, 380, sw=2),
        arrow(550, 360, 695, 380, sw=2)
    ]
    render(os.path.join(IMG, 'power-allocator-pid.svg'), w, h, *frags, title="Power Allocator PID Governor Architecture")

if __name__ == '__main__':
    make_thermal_arch()
    make_trip_points_hysteresis()
    make_power_allocator_pid()
