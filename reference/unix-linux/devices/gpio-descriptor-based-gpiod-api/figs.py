import sys
import os

scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, scripts_dir)

from svgkit import render, textbox, fitbox, arrow, rect, text, line, mtext, FILL, LINE, INK, POS, NEG, FIELD

def generate_figs():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    # ── 1. gpiod Architecture ────────────────────────────────────────────────
    path1 = os.path.join(img_dir, 'gpiod-architecture.svg')
    frags1 = []
    
    # Left Box: Hardware Description (Device Tree)
    frags1.append(rect(30, 40, 240, 260, fill="#f8f9fa", stroke="#495057", sw=2, rx=8))
    frags1.append(text(150, 70, "Device Tree (.dts)", size=16, bold=True, color="#212529"))
    
    dt_code = "sensor_node {\n  compatible = \"acme,sensor\";\n  reset-gpios = <&gpio1 10\n    GPIO_ACTIVE_LOW>;\n  irq-gpios = <&gpio1 11\n    GPIO_ACTIVE_HIGH>;\n};"
    b_dt, _, _ = textbox(150, 175, dt_code, size=12, fill="#e9ecef", stroke="#adb5bd", pad=8)
    frags1.append(b_dt)
    
    # Middle Arrow
    frags1.append(arrow(275, 170, 335, 170, color="#343a40", sw=2.5))
    frags1.append(text(305, 155, "Lookup", size=12, color="#495057", bold=True))
    
    # Center Box: Kernel Subsystem (gpiolib)
    frags1.append(rect(340, 40, 260, 260, fill="#e8f5e9", stroke="#2e7d32", sw=2, rx=8))
    frags1.append(text(470, 70, "gpiolib (Kernel Subsystem)", size=16, bold=True, color="#1b5e20"))
    
    frags1.append(rect(355, 95, 230, 50, fill="#ffffff", stroke="#81c784", sw=1.5, rx=6))
    frags1.append(text(470, 115, "struct gpio_chip", size=13, bold=True, color="#2e7d32"))
    frags1.append(text(470, 133, "Base HW driver (SoC / I2C)", size=11, color="#555555"))
    
    frags1.append(rect(355, 160, 230, 125, fill="#ffffff", stroke="#4caf50", sw=1.5, rx=6))
    frags1.append(text(470, 180, "struct gpio_desc", size=14, bold=True, color="#1b5e20"))
    gpiolib_info = "• Chip pointer: &gpio_chip\n• Hw pin index: 10\n• Flags: GPIOD_ACTIVE_LOW\n• Label: \"reset\"\n• Active consumer: &dev"
    frags1.append(mtext(365, 198, gpiolib_info.split('\n'), size=11, color="#212529", anchor="start"))
    
    # Right Arrow
    frags1.append(arrow(605, 170, 665, 170, color="#343a40", sw=2.5))
    frags1.append(text(635, 155, "Handle", size=12, color="#495057", bold=True))
    
    # Right Box: Peripheral Device Driver
    frags1.append(rect(670, 40, 250, 260, fill="#e3f2fd", stroke="#1565c0", sw=2, rx=8))
    frags1.append(text(795, 70, "Peripheral Driver", size=16, bold=True, color="#0d47a1"))
    
    drv_code = "devm_gpiod_get(dev,\n  \"reset\", GPIOD_OUT_LOW);\n\n// Logical active=1\ngpiod_set_value(desc, 1);"
    b_drv, _, _ = textbox(795, 175, drv_code, size=12, fill="#ffffff", stroke="#90caf9", pad=8)
    frags1.append(b_drv)
    
    render(path1, 950, 320, *frags1)
    
    # ── 2. Active-Low Logical Inversion ───────────────────────────────────────
    path2 = os.path.join(img_dir, 'gpiod-value-inversion.svg')
    frags2 = []
    
    # Top Box: Driver Call
    b_call, _, _ = textbox(450, 45, "Driver Call: gpiod_set_value(desc, 1)  [Logical State: ACTIVE / 1]", size=14, fill="#e3f2fd", stroke="#1565c0", bold=True, min_w=600)
    frags2.append(b_call)
    
    # Diverging Arrows
    frags2.append(arrow(350, 75, 230, 125, color="#1565c0", sw=2))
    frags2.append(text(270, 95, "ACTIVE_HIGH Flag", size=12, color="#1565c0", bold=True))
    
    frags2.append(arrow(550, 75, 670, 125, color="#c62828", sw=2))
    frags2.append(text(630, 95, "ACTIVE_LOW Flag", size=12, color="#c62828", bold=True))
    
    # Left Branch: Active High
    frags2.append(rect(50, 130, 360, 180, fill="#f1f8e9", stroke="#33691e", sw=2, rx=8))
    frags2.append(text(230, 155, "Standard (ACTIVE_HIGH)", size=15, bold=True, color="#33691e"))
    frags2.append(text(230, 185, "Physical Line Level = HIGH (3.3V)", size=13, bold=True, color="#2e7d32"))
    frags2.append(line(80, 240, 180, 240, color="#2e7d32", sw=3))
    frags2.append(line(180, 240, 180, 210, color="#2e7d32", sw=3))
    frags2.append(line(180, 210, 380, 210, color="#2e7d32", sw=3))
    frags2.append(text(130, 260, "0V (LOW)", size=11, color="#666666"))
    frags2.append(text(280, 200, "3.3V (HIGH)", size=11, color="#2e7d32", bold=True))
    
    # Right Branch: Active Low Inverted
    frags2.append(rect(490, 130, 360, 180, fill="#ffebee", stroke="#c62828", sw=2, rx=8))
    frags2.append(text(670, 155, "Inverted (ACTIVE_LOW)", size=15, bold=True, color="#c62828"))
    frags2.append(text(670, 185, "Physical Line Level = LOW (0V)", size=13, bold=True, color="#c62828"))
    frags2.append(line(520, 210, 620, 210, color="#c62828", sw=3))
    frags2.append(line(620, 210, 620, 240, color="#c62828", sw=3))
    frags2.append(line(620, 240, 820, 240, color="#c62828", sw=3))
    frags2.append(text(570, 200, "3.3V (HIGH)", size=11, color="#666666"))
    frags2.append(text(720, 260, "0V (LOW)", size=11, color="#c62828", bold=True))
    
    # Bottom Note
    b_note, _, _ = textbox(450, 340, "gpiod_set_raw_value(desc, 1) bypasses ACTIVE_LOW flag and forces physical HIGH (3.3V) directly", size=12, fill="#fff8e1", stroke="#ffa000", min_w=650)
    frags2.append(b_note)
    
    render(path2, 900, 375, *frags2)
    
    # ── 3. Execution Contexts: MMIO vs Can-Sleep ─────────────────────────────
    path3 = os.path.join(img_dir, 'gpiod-cansleep-context.svg')
    frags3 = []
    
    # Left Column: Atomic MMIO GPIO
    frags3.append(rect(30, 30, 410, 270, fill="#e8eaf6", stroke="#283593", sw=2, rx=8))
    frags3.append(text(235, 60, "MMIO SoC Controller", size=16, bold=True, color="#1a237e"))
    frags3.append(text(235, 82, "(Memory-Mapped Registers)", size=12, color="#3f51b5"))
    
    b_m1, _, _ = textbox(235, 125, "Function: gpiod_set_value()", size=13, fill="#ffffff", stroke="#3f51b5", bold=True, min_w=340)
    frags3.append(b_m1)
    
    mmio_text = "• Execution time: Nanoseconds (direct register write)\n• Context: Spinlock / Hard IRQ / Atomic safe\n• Sleeping: IMPOSSIBLE (spinlocks held)"
    frags3.append(mtext(55, 185, mmio_text.split('\n'), size=11, color="#212529", anchor="start"))
    
    frags3.append(rect(50, 240, 370, 40, fill="#c8e6c9", stroke="#2e7d32", sw=1.5, rx=6))
    frags3.append(text(235, 265, "SAFE in Interrupt / Spinlock Handlers", size=12, bold=True, color="#1b5e20"))
    
    # Right Column: Off-Chip I2C/SPI Expander
    frags3.append(rect(470, 30, 410, 270, fill="#fff3e0", stroke="#e65100", sw=2, rx=8))
    frags3.append(text(675, 60, "Off-Chip Bus Expander", size=16, bold=True, color="#bf360c"))
    frags3.append(text(675, 82, "(PCF8574 / MCP23017 over I2C/SPI)", size=12, color="#f57c00"))
    
    b_s1, _, _ = textbox(675, 125, "Function: gpiod_set_value_cansleep()", size=13, fill="#ffffff", stroke="#f57c00", bold=True, min_w=340)
    frags3.append(b_s1)
    
    sleep_text = "• Execution time: Milliseconds (I2C/SPI transaction)\n• Context: Threaded IRQ / Workqueue / Process only\n• Sleeping: MANDATORY (wait_for_completion / mutex)"
    frags3.append(mtext(495, 185, sleep_text.split('\n'), size=11, color="#212529", anchor="start"))
    
    frags3.append(rect(490, 240, 370, 40, fill="#ffcdd2", stroke="#c62828", sw=1.5, rx=6))
    frags3.append(text(675, 265, "FORBIDDEN in Atomic Context (might_sleep)", size=12, bold=True, color="#b71c1c"))
    
    render(path3, 910, 320, *frags3)

if __name__ == '__main__':
    generate_figs()
