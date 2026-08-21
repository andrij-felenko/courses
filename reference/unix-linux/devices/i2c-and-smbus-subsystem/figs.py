import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import rect, text, line, arrow, render, mtext, fitbox

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

def render_arch():
    frags = []
    
    # Outer frame
    frags.append(rect(10, 10, 800, 520, fill="#ffffff", stroke="#d1d5db", rx=8))
    
    # Layer 1: Userspace
    frags.append(rect(30, 30, 760, 60, fill="#eef2ff", stroke="#6366f1", rx=6))
    frags.append(text(410, 52, "Простір користувача (Userspace)", size=14, color="#3730a3", bold=True))
    frags.append(text(410, 72, "i2c-tools (i2cdetect, i2cget, i2cset, i2ctransfer)  |  демони сенсорів і прикладні сервіси", size=11, color="#4338ca"))

    # Layer 2: Character Device & sysfs
    frags.append(rect(30, 105, 760, 55, fill="#f5f3ff", stroke="#8b5cf6", rx=6))
    frags.append(text(410, 126, "Символьний інтерфейс та системні дерева (VFS / sysfs)", size=13, color="#5b21b6", bold=True))
    frags.append(text(410, 145, "/dev/i2c-N (драйвер i2c-dev.ko, ioctl I2C_RDWR / I2C_SMBUS)  |  /sys/bus/i2c/devices/*", size=11, color="#6d28d9"))

    # Layer 3: Kernel I2C/SMBus Core
    frags.append(rect(30, 175, 760, 120, fill="#dbeafe", stroke="#2563eb", rx=6))
    frags.append(text(410, 197, "Ядро підсистеми I2C / SMBus (i2c-core)", size=14, color="#1e40af", bold=True))
    
    # Sub-boxes in Core: Drivers/Clients vs Core-Routing
    frags.append(rect(45, 212, 340, 70, fill="#eff6ff", stroke="#3b82f6", rx=4))
    frags.append(text(215, 232, "Клієнти та драйвери пристроїв", size=12, color="#1d4ed8", bold=True))
    frags.append(text(215, 250, "struct i2c_driver (lm75, bmp280, at24)", size=11, color="#1e40af"))
    frags.append(text(215, 268, "struct i2c_client (екземпляри на адресах 0x48, 0x76)", size=11, color="#1e40af"))

    frags.append(rect(405, 212, 370, 70, fill="#eff6ff", stroke="#3b82f6", rx=4))
    frags.append(text(590, 232, "Маршрутизація та емуляція SMBus", size=12, color="#1d4ed8", bold=True))
    frags.append(text(590, 250, "i2c_transfer()  <===>  i2c_smbus_xfer()", size=11, color="#1e40af", bold=True))
    frags.append(text(590, 268, "трансляція команд SMBus у послідовності i2c_msg", size=10, color="#1d4ed8"))

    # Layer 4: Bus Adapter & Algorithm
    frags.append(rect(30, 310, 760, 105, fill="#dcfce7", stroke="#16a34a", rx=6))
    frags.append(text(410, 330, "Шинні адаптери та драйвери контролерів (struct i2c_adapter / struct i2c_algorithm)", size=13, color="#14532d", bold=True))
    
    frags.append(rect(45, 345, 235, 60, fill="#f0fdf4", stroke="#22c55e", rx=4))
    frags.append(text(162, 365, "I2C SoC контролери", size=12, color="#15803d", bold=True))
    frags.append(text(162, 382, "i2c-designware, i2c-imx", size=10, color="#166534"))
    frags.append(text(162, 396, "master_xfer (сирі i2c_msg)", size=10, color="#15803d"))

    frags.append(rect(292, 345, 235, 60, fill="#f0fdf4", stroke="#22c55e", rx=4))
    frags.append(text(409, 365, "Хост-контролери SMBus", size=12, color="#15803d", bold=True))
    frags.append(text(409, 382, "i2c-i801, i2c-piix4 (x86)", size=10, color="#166534"))
    frags.append(text(409, 396, "smbus_xfer (команди SMBus)", size=10, color="#15803d"))

    frags.append(rect(540, 345, 235, 60, fill="#f0fdf4", stroke="#22c55e", rx=4))
    frags.append(text(657, 365, "Програмний Bit-Banging", size=12, color="#15803d", bold=True))
    frags.append(text(657, 382, "i2c-gpio, i2c-algo-bit", size=10, color="#166534"))
    frags.append(text(657, 396, "генерація тактування GPIO", size=10, color="#15803d"))

    # Layer 5: Physical Hardware
    frags.append(rect(30, 430, 760, 80, fill="#f3f4f6", stroke="#4b5563", rx=6))
    frags.append(text(410, 452, "Фізична шина та периферійні мікросхеми (SDA / SCL з підтяжкою Rp до Vdd)", size=13, color="#1f2937", bold=True))
    frags.append(text(410, 472, "Двопровідна відкритий стік топологія  |  Датчики температури, тиску, RTC, EEPROM, PMIC", size=11, color="#374151"))
    frags.append(text(410, 492, "Режими: Standard (100 kHz), Fast (400 kHz), Fast+ (1 MHz), SMBus (10-100 kHz з таймаутом)", size=10, color="#4b5563"))

    # Connecting arrows
    frags.append(arrow(410, 90, 410, 105, color="#4b5563"))
    frags.append(arrow(410, 160, 410, 175, color="#4b5563"))
    frags.append(arrow(410, 295, 410, 310, color="#4b5563"))
    frags.append(arrow(410, 415, 410, 430, color="#4b5563"))

    render(os.path.join(IMG, 'fig-i2c-subsystem-arch.svg'), 820, 540, *frags)

def render_matching():
    frags = []

    # Outer frame
    frags.append(rect(10, 10, 800, 430, fill="#ffffff", stroke="#d1d5db", rx=8))

    # Column 1: Sources of device declaration
    frags.append(rect(30, 30, 220, 380, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    frags.append(text(140, 55, "Джерела опису пристроїв", size=13, color="#0f172a", bold=True))

    frags.append(rect(45, 75, 190, 65, fill="#e0f2fe", stroke="#0284c7", rx=4))
    frags.append(text(140, 95, "Device Tree (.dts)", size=11, color="#0369a1", bold=True))
    frags.append(text(140, 112, "compatible = \"ti,tmp102\"", size=10, color="#0284c7"))
    frags.append(text(140, 128, "reg = <0x48>;", size=10, color="#0284c7"))

    frags.append(rect(45, 150, 190, 65, fill="#fef3c7", stroke="#d97706", rx=4))
    frags.append(text(140, 170, "ACPI (DSDT / SSDT)", size=11, color="#92400e", bold=True))
    frags.append(text(140, 187, "_HID: \"TMP0102\" / \"INT3432\"", size=10, color="#b45309"))
    frags.append(text(140, 203, "I2cSerialBusV2(0x48, ...)", size=10, color="#b45309"))

    frags.append(rect(45, 225, 190, 65, fill="#f3e8ff", stroke="#9333ea", rx=4))
    frags.append(text(140, 245, "Таблиця i2c_device_id", size=11, color="#7e22ce", bold=True))
    frags.append(text(140, 262, "{\"tmp102\", 0}", size=10, color="#9333ea"))
    frags.append(text(140, 278, "Legacy / Board info", size=10, color="#9333ea"))

    frags.append(rect(45, 300, 190, 65, fill="#fee2e2", stroke="#dc2626", rx=4))
    frags.append(text(140, 320, "sysfs new_device", size=11, color="#991b1b", bold=True))
    frags.append(text(140, 337, "echo tmp102 0x48 >", size=10, color="#dc2626"))
    frags.append(text(140, 353, ".../i2c-1/new_device", size=10, color="#dc2626"))

    # Column 2: Kernel Instantiation Core
    frags.append(rect(290, 75, 230, 290, fill="#eff6ff", stroke="#3b82f6", rx=6))
    frags.append(text(405, 105, "Створення i2c_client", size=13, color="#1e40af", bold=True))
    frags.append(text(405, 128, "i2c_new_client_device()", size=11, color="#2563eb", bold=True))
    
    frags.append(rect(305, 145, 200, 75, fill="#ffffff", stroke="#93c5fd", rx=4))
    frags.append(text(405, 168, "struct i2c_client", size=12, color="#1e40af", bold=True))
    frags.append(text(405, 186, ".addr = 0x48", size=11, color="#1e40af"))
    frags.append(text(405, 204, ".adapter = i2c_adapter", size=11, color="#1e40af"))

    frags.append(rect(305, 235, 200, 110, fill="#ffffff", stroke="#93c5fd", rx=4))
    frags.append(text(405, 255, "Зіставлення (Matching)", size=12, color="#1e40af", bold=True))
    frags.append(text(405, 275, "1. of_match_table (DT)", size=10, color="#1d4ed8"))
    frags.append(text(405, 292, "2. acpi_match_table (ACPI)", size=10, color="#1d4ed8"))
    frags.append(text(405, 309, "3. id_table (i2c_device_id)", size=10, color="#1d4ed8"))
    frags.append(text(405, 326, "4. driver.name == client.name", size=10, color="#1d4ed8"))

    # Column 3: Device Driver
    frags.append(rect(560, 110, 210, 220, fill="#f0fdf4", stroke="#16a34a", rx=6))
    frags.append(text(665, 138, "struct i2c_driver", size=13, color="#14532d", bold=True))
    frags.append(text(665, 160, "Драйвер сенсора (tmp102.c)", size=11, color="#15803d"))

    frags.append(rect(575, 175, 180, 135, fill="#ffffff", stroke="#86efac", rx=4))
    frags.append(text(665, 195, ".probe(client)", size=11, color="#166534", bold=True))
    frags.append(text(665, 215, "Ініціалізація чипа,", size=10, color="#15803d"))
    frags.append(text(665, 232, "реєстрація в hwmon / iio,", size=10, color="#15803d"))
    frags.append(text(665, 249, "налаштування переривань IRQ", size=10, color="#15803d"))
    frags.append(text(665, 275, ".remove(client)", size=11, color="#166534", bold=True))
    frags.append(text(665, 295, "Звільнення ресурсів", size=10, color="#15803d"))

    # Arrows
    frags.append(arrow(235, 107, 290, 140, color="#0284c7"))
    frags.append(arrow(235, 182, 290, 180, color="#d97706"))
    frags.append(arrow(235, 257, 290, 230, color="#9333ea"))
    frags.append(arrow(235, 332, 290, 270, color="#dc2626"))

    frags.append(arrow(520, 220, 560, 220, color="#16a34a"))

    render(os.path.join(IMG, 'fig-i2c-matching-flow.svg'), 820, 450, *frags)

def render_frames():
    frags = []

    # Outer frame
    frags.append(rect(10, 10, 800, 480, fill="#ffffff", stroke="#d1d5db", rx=8))

    # Title & Subtitle
    frags.append(text(410, 35, "Порівняння кадрових протоколів: сирий I2C проти SMBus", size=14, color="#111827", bold=True))

    # Section 1: Raw I2C Combined Read/Write Transfer
    frags.append(rect(25, 55, 770, 115, fill="#f8fafc", stroke="#94a3b8", rx=6))
    frags.append(text(45, 78, "1. Сира I2C транзакція (i2c_transfer): запис адреси регістра + читання N байтів", size=12, color="#0f172a", bold=True, anchor="left"))
    
    # Draw frame blocks for I2C
    # START, ADDR+W, ACK, REG, ACK, Sr, ADDR+R, ACK, DATA 0, ACK, DATA N-1, NACK, STOP
    blocks_i2c = [
        ("S", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Addr 7-bit + W (0)", 100, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Reg Addr (0x00)", 95, "#fef3c7", "#f59e0b", "#92400e"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Sr", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Addr 7-bit + R (1)", 100, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Data Byte 0", 85, "#e0e7ff", "#6366f1", "#3730a3"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("...", 35, "#f3f4f6", "#9ca3af", "#4b5563"),
        ("Data Byte N-1", 95, "#e0e7ff", "#6366f1", "#3730a3"),
        ("NA", 28, "#fee2e2", "#ef4444", "#991b1b"),
        ("P", 26, "#fee2e2", "#ef4444", "#991b1b"),
    ]
    
    bx = 45
    by = 95
    bh = 38
    for label, bw, bfill, bstroke, btext in blocks_i2c:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, rx=3))
        frags.append(text(bx + bw / 2, by + 24, label, size=10, color=btext, bold=True))
        bx += bw + 3

    frags.append(text(45, 155, "Немає фіксованого ліміту довжини; немає примусового таймауту тактування; довільний формат даних", size=10, color="#64748b", anchor="left", italic=True))

    # Section 2: SMBus Read Byte Data
    frags.append(rect(25, 185, 770, 115, fill="#f8fafc", stroke="#94a3b8", rx=6))
    frags.append(text(45, 208, "2. SMBus Read Byte Protocol (i2c_smbus_read_byte_data)", size=12, color="#0f172a", bold=True, anchor="left"))
    
    blocks_smb_byte = [
        ("S", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Slave Addr + W", 95, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Command Code", 95, "#fef3c7", "#f59e0b", "#92400e"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Sr", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Slave Addr + R", 95, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 24, "#dcfce7", "#22c55e", "#15803d"),
        ("Data Byte", 85, "#e0e7ff", "#6366f1", "#3730a3"),
        ("NA", 28, "#fee2e2", "#ef4444", "#991b1b"),
        ("P", 26, "#fee2e2", "#ef4444", "#991b1b"),
    ]
    
    bx = 45
    by = 225
    for label, bw, bfill, bstroke, btext in blocks_smb_byte:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, rx=3))
        frags.append(text(bx + bw / 2, by + 24, label, size=10, color=btext, bold=True))
        bx += bw + 3

    frags.append(text(45, 285, "Чітко визначений протокол: команда (регістр) + 1 байт відповіді; таймаут шини tTIMEOUT = 25-35 ms", size=10, color="#64748b", anchor="left", italic=True))

    # Section 3: SMBus Block Read with PEC (Packet Error Checking)
    frags.append(rect(25, 315, 770, 145, fill="#f8fafc", stroke="#94a3b8", rx=6))
    frags.append(text(45, 338, "3. SMBus Block Read з обов'язковим лічильником байтів та PEC (CRC-8)", size=12, color="#0f172a", bold=True, anchor="left"))
    
    blocks_smb_block = [
        ("S", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Slave Addr+W", 80, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 22, "#dcfce7", "#22c55e", "#15803d"),
        ("Command", 70, "#fef3c7", "#f59e0b", "#92400e"),
        ("A", 22, "#dcfce7", "#22c55e", "#15803d"),
        ("Sr", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("Slave Addr+R", 80, "#dbeafe", "#3b82f6", "#1e40af"),
        ("A", 22, "#dcfce7", "#22c55e", "#15803d"),
        ("Byte Count (N)", 95, "#fbcfe8", "#db2777", "#9d174d"),
        ("A", 22, "#dcfce7", "#22c55e", "#15803d"),
        ("Data 1..N", 75, "#e0e7ff", "#6366f1", "#3730a3"),
        ("A", 22, "#dcfce7", "#22c55e", "#15803d"),
        ("PEC (CRC-8)", 85, "#fed7aa", "#f97316", "#c2410c"),
        ("NA", 26, "#fee2e2", "#ef4444", "#991b1b"),
        ("P", 26, "#fee2e2", "#ef4444", "#991b1b"),
    ]

    bx = 45
    by = 355
    for label, bw, bfill, bstroke, btext in blocks_smb_block:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, rx=3))
        frags.append(text(bx + bw / 2, by + 24, label, size=10, color=btext, bold=True))
        bx += bw + 3

    frags.append(text(45, 415, "Byte Count визначає розмір блоку (<=32 байтів у SMBus 2.0); PEC (CRC-8, поліном x^8+x^2+x+1) захищає від спотворень", size=10, color="#64748b", anchor="left", italic=True))
    frags.append(text(45, 440, "Легенда: S/Sr = Start/Repeated Start, P = Stop, A = ACK (0), NA = NACK (1), W = 0, R = 1", size=10, color="#1e293b", anchor="left", bold=True))

    render(os.path.join(IMG, 'fig-i2c-vs-smbus-frames.svg'), 820, 500, *frags)

if __name__ == '__main__':
    render_arch()
    render_matching()
    render_frames()
    print("All figures successfully rendered.")
