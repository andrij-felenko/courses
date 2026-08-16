# -*- coding: utf-8 -*-
import sys, os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"

def fig_pci_config_space():
    W, H = 1000, 780
    p = []

    # Standard Header (0x00 - 0x3C)
    y_start = 60
    row_h = 34
    col_w = 200
    x_offsets = [100 + i * col_w for i in range(4)]  # Byte 3, Byte 2, Byte 1, Byte 0

    # Header labels
    bytes_hdr = ["Byte 3 (MSB)", "Byte 2", "Byte 1", "Byte 0 (LSB)"]
    for i, b_name in enumerate(bytes_hdr):
        p.append(text(x_offsets[i] + col_w / 2, y_start + 18, b_name, size=12, color=MUTED, bold=True))

    rows_data = [
        ("0x00", [("Device ID (16 біт)", 2, WARM), ("Vendor ID (16 біт)", 2, GREEN)]),
        ("0x04", [("Status Register (16 біт)", 2, BLUE), ("Command Register (16 біт)", 2, RED)]),
        ("0x08", [("Class Code (24 біти)", 3, GREEN), ("Revision ID (8 біт)", 1, GREY)]),
        ("0x0C", [("BIST (8)", 1, GREY), ("Header Type (8)", 1, WARM), ("Latency (8)", 1, GREY), ("CacheLine (8)", 1, GREY)]),
        ("0x10", [("Base Address Register 0 (BAR0) — 32/64 біти MMIO/IO", 4, BLUE)]),
        ("0x14", [("Base Address Register 1 (BAR1) — 32 біти", 4, BLUE)]),
        ("0x18", [("Base Address Register 2 (BAR2)", 4, BLUE)]),
        ("0x1C", [("Base Address Register 3 (BAR3)", 4, BLUE)]),
        ("0x20", [("Base Address Register 4 (BAR4)", 4, BLUE)]),
        ("0x24", [("Base Address Register 5 (BAR5)", 4, BLUE)]),
        ("0x28", [("Cardbus CIS Pointer (32 біти)", 4, GREY)]),
        ("0x2C", [("Subsystem ID (16 біт)", 2, WARM), ("Subsystem Vendor ID (16 біт)", 2, GREEN)]),
        ("0x30", [("Expansion ROM Base Address (32 біти)", 4, GREY)]),
        ("0x34", [("Зарезервовано (24 біти)", 3, GREY), ("Capabilities Pointer (8 біт)", 1, RED)]),
        ("0x38", [("Зарезервовано (32 біти)", 4, GREY)]),
        ("0x3C", [("Max_Lat (8)", 1, GREY), ("Min_Gnt (8)", 1, GREY), ("Interrupt Pin (8)", 1, WARM), ("Interrupt Line (8)", 1, WARM)]),
    ]

    curr_y = y_start + 30
    for offset_str, cells in rows_data:
        # Offset label on the left
        p.append(text(50, curr_y + row_h / 2 + 4, offset_str, size=12, color=INK, bold=True, anchor="end"))
        curr_x = 100
        for label, span_cols, fill_color in cells:
            w_box = span_cols * col_w
            f_box, _, _ = textbox(curr_x + w_box / 2, curr_y + row_h / 2, [label],
                                  size=12, pad=6, fill=fill_color, stroke=LINE, min_w=w_box)
            p.append(f_box)
            curr_x += w_box
        curr_y += row_h + 2

    # Capabilities & Extended Space indicator
    curr_y += 10
    f_ext, _, _ = textbox(500, curr_y + 20,
                          ["Розширений простір PCIe (0x0100 – 0x0FFF): зв'язаний список розширених можливостей (AER, SRIOV, DPC)",
                           "Доступ через ECAM (Enhanced Configuration Access Mechanism) MMIO"],
                          size=12, pad=10, fill=WARM, stroke=POS, min_w=800)
    p.append(f_ext)

    render(os.path.join(IMG, 'pci-config-space.svg'), W, H, *p,
           title="Конфігураційний простір PCI/PCIe (Header Type 0)")


def fig_pcie_topology():
    W, H = 1100, 680
    p = []

    # CPU & RAM
    cx_cpu = 550
    cy_cpu = 110
    f_cpu, w_cpu, h_cpu = textbox(cx_cpu, cy_cpu,
                                  ["Центральний процесор (CPU) & Системна пам'ять (RAM)",
                                   "Фізичний адресний простір MMIO / ECAM"],
                                  size=14, pad=14, fill=GREEN, stroke=LINE, bold=True)
    p.append(f_cpu)

    # Host Bridge / Root Complex
    cy_rc = 220
    f_rc, w_rc, h_rc = textbox(cx_cpu, cy_rc,
                               ["Root Complex (Кореневий комплекс PCIe)",
                                "Host Bridge · Domain 0000 · Bus 00",
                                "Контролер пам'яті, генерація TLP-пакетів, перетворення CPU MMIO ↔ PCIe"],
                               size=13, pad=14, fill=WARM, stroke=LINE, bold=True)
    p.append(f_rc)
    p.append(arrow(cx_cpu, cy_cpu + h_cpu / 2 + 2, cx_cpu, cy_rc - h_rc / 2 - 2))

    # Root Ports / Bridges
    cy_rp = 340
    x_rp1, x_rp2, x_rp3 = 250, 550, 850
    f_rp1, w_rp1, h_rp1 = textbox(x_rp1, cy_rp,
                                  ["Root Port 00:01.0", "PCI Bridge (Bus 00 → 01)"],
                                  size=12, pad=12, fill=BLUE, stroke=LINE)
    f_rp2, w_rp2, h_rp2 = textbox(x_rp2, cy_rp,
                                  ["Root Port 00:02.0", "PCI Bridge (Bus 00 → 02)"],
                                  size=12, pad=12, fill=BLUE, stroke=LINE)
    f_rp3, w_rp3, h_rp3 = textbox(x_rp3, cy_rp,
                                  ["Root Port 00:03.0", "PCI Bridge (Bus 00 → 06)"],
                                  size=12, pad=12, fill=BLUE, stroke=LINE)
    p.append(f_rp1)
    p.append(f_rp2)
    p.append(f_rp3)

    p.append(arrow(cx_cpu - 180, cy_rc + h_rc / 2 + 2, x_rp1, cy_rp - h_rp1 / 2 - 2))
    p.append(arrow(cx_cpu, cy_rc + h_rc / 2 + 2, x_rp2, cy_rp - h_rp2 / 2 - 2))
    p.append(arrow(cx_cpu + 180, cy_rc + h_rc / 2 + 2, x_rp3, cy_rp - h_rp3 / 2 - 2))

    # Level 3: PCIe Switch / Endpoints
    cy_l3 = 470
    # Left: GPU Endpoint
    f_ep1, w_ep1, h_ep1 = textbox(x_rp1, cy_l3,
                                  ["NVidia GPU Endpoint",
                                   "BDF: 0000:01:00.0",
                                   "PCIe x16 Gen4 Link",
                                   "BAR0: MMIO 16MB, BAR1: 16GB VRAM (prefetchable)"],
                                  size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_ep1)
    p.append(arrow(x_rp1, cy_rp + h_rp1 / 2 + 2, x_rp1, cy_l3 - h_ep1 / 2 - 2))

    # Middle: PCIe Switch
    f_sw, w_sw, h_sw = textbox(x_rp2, cy_l3,
                               ["PCIe Switch (Комутатор)",
                                "Upstream Port: 02:00.0",
                                "Downstream Ports: 03:00.0, 03:01.0"],
                               size=12, pad=12, fill=WARM, stroke=LINE)
    p.append(f_sw)
    p.append(arrow(x_rp2, cy_rp + h_rp2 / 2 + 2, x_rp2, cy_l3 - h_sw / 2 - 2))

    # Right: Direct NVMe Endpoint
    f_ep2, w_ep2, h_ep2 = textbox(x_rp3, cy_l3,
                                  ["NVMe Controller",
                                   "BDF: 0000:06:00.0",
                                   "PCIe x4 Gen4 Link",
                                   "BAR0: MMIO 16KB (MSI-X Table)"],
                                  size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_ep2)
    p.append(arrow(x_rp3, cy_rp + h_rp3 / 2 + 2, x_rp3, cy_l3 - h_ep2 / 2 - 2))

    # Devices under switch
    cy_sw_dev = 600
    x_sw1, x_sw2 = 440, 660
    f_sw_dev1, _, h_sd1 = textbox(x_sw1, cy_sw_dev,
                                  ["M.2 NVMe SSD", "BDF: 0000:04:00.0"],
                                  size=12, pad=10, fill=GREY, stroke=LINE)
    f_sw_dev2, _, h_sd2 = textbox(x_sw2, cy_sw_dev,
                                  ["10GbE NIC", "BDF: 0000:05:00.0"],
                                  size=12, pad=10, fill=GREY, stroke=LINE)
    p.append(f_sw_dev1)
    p.append(f_sw_dev2)
    p.append(arrow(x_rp2 - 50, cy_l3 + h_sw / 2 + 2, x_sw1, cy_sw_dev - h_sd1 / 2 - 2))
    p.append(arrow(x_rp2 + 50, cy_l3 + h_sw / 2 + 2, x_sw2, cy_sw_dev - h_sd2 / 2 - 2))

    render(os.path.join(IMG, 'pcie-topology.svg'), W, H, *p,
           title="Ієрархія та топологія PCIe в системі Linux")


def fig_interrupt_mechanisms():
    W, H = 1100, 560
    p = []

    # Left box: INTx
    x_intx = 280
    f_hdr1, _, _ = textbox(x_intx, 85, ["1. Legacy INTx (In-Band Message Emulation)"],
                          size=14, pad=12, fill=RED, stroke=LINE, bold=True)
    p.append(f_hdr1)

    y_dev1 = 180
    f_d1, _, h_d1 = textbox(x_intx, y_dev1,
                            ["PCIe Endpoint", "Генерує TLP: Assert_INTA"],
                            size=12, pad=12, fill=GREY, stroke=LINE)
    p.append(f_d1)

    y_bridge = 300
    f_b, _, h_b = textbox(x_intx, y_bridge,
                          ["PCI Bridge / Host Controller",
                           "Перетворює TLP на фізичну IRQ-лінію (наприклад, IRQ 16)",
                           "Спільне використання лінії (Interrupt Sharing!)"],
                          size=12, pad=12, fill=WARM, stroke=LINE)
    p.append(f_b)
    p.append(arrow(x_intx, y_dev1 + h_d1 / 2 + 2, x_intx, y_bridge - h_b / 2 - 2))

    y_cpu1 = 440
    f_c1, _, h_c1 = textbox(x_intx, y_cpu1,
                            ["CPU Core", "Викликає ВСІ обробники, підключені до IRQ 16",
                             "Повільно, вимагає опитання регістрів пристрою"],
                            size=12, pad=12, fill=RED, stroke=LINE)
    p.append(f_c1)
    p.append(arrow(x_intx, y_bridge + h_b / 2 + 2, x_intx, y_cpu1 - h_c1 / 2 - 2))

    # Right box: MSI / MSI-X
    x_msi = 820
    f_hdr2, _, _ = textbox(x_msi, 85, ["2. MSI / MSI-X (Message Signaled Interrupts)"],
                          size=14, pad=12, fill=GREEN, stroke=LINE, bold=True)
    p.append(f_hdr2)

    y_dev2 = 180
    f_d2, _, h_d2 = textbox(x_msi, y_dev2,
                            ["PCIe Endpoint (NVMe / NIC)",
                             "Вибирає вектор переривання N з MSI-X таблиці (в BAR)",
                             "Генерує PCIe Memory Write TLP"],
                            size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_d2)

    y_apic = 300
    f_apic, _, h_apic = textbox(x_msi, y_apic,
                                ["Local APIC Message Address 0xFEE00000, APIC ID у бітах 19:12",
                                 "Прямий запис у пам'ять системного контролера переривань",
                                 "Немає розділення ліній (No Sharing), унікальний вектор!"],
                                size=12, pad=12, fill=BLUE, stroke=LINE)
    p.append(f_apic)
    p.append(arrow(x_msi, y_dev2 + h_d2 / 2 + 2, x_msi, y_apic - h_apic / 2 - 2))

    y_cpu2 = 440
    f_c2, _, h_c2 = textbox(x_msi, y_cpu2,
                            ["Прив'язане ядро CPU (CPU Affinity)",
                             "Викликає ТІЛЬКИ конкретний обробник черги DMA",
                             "Максимальна паралельність та відсутність блокувань"],
                            size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_c2)
    p.append(arrow(x_msi, y_apic + h_apic / 2 + 2, x_msi, y_cpu2 - h_c2 / 2 - 2))

    render(os.path.join(IMG, 'interrupt-mechanisms.svg'), W, H, *p,
           title="Порівняння механізмів переривань INTx та MSI/MSI-X")


def render_all():
    fig_pci_config_space()
    fig_pcie_topology()
    fig_interrupt_mechanisms()

if __name__ == "__main__":
    render_all()
