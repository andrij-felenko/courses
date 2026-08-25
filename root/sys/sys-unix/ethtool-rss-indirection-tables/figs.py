import sys
import os

# Add root scripts/ directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, rect, text, line, arrow, textbox, fitbox, FONT, INK, LINE, FILL, POS, NEG, FIELD, MUTED, circle

def generate_single_queue():
    w, h = 720, 340
    frags = []

    # Outer container for NIC
    frags.append(rect(20, 40, 200, 260, fill="#f0f4f8", stroke="#1e3a8a", sw=2, rx=8))
    frags.append(text(120, 68, "Мережевий адаптер (NIC)", size=15, bold=True, color="#1e3a8a"))
    frags.append(text(120, 88, "1 GbE / 10 GbE (Single-Queue)", size=12, color=MUTED, italic=True))

    # Single RX ring box
    tb1, _, _ = textbox(120, 160, "Єдина черга прийому\n(Rx Queue 0)\nDMA Ring Buffer", size=13, fill="#dbeafe", stroke="#2563eb", pad=10, bold=True)
    frags.append(tb1)

    # Packet ingress arrow
    frags.append(arrow(10, 160, 45, 160, color="#2563eb", sw=2.5))
    frags.append(text(28, 148, "Трафік", size=11, color="#2563eb", bold=True, anchor="middle"))

    # Single IRQ arrow to CPU 0
    frags.append(arrow(195, 160, 400, 95, color=POS, sw=3))
    frags.append(rect(225, 105, 150, 36, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(300, 122, "Hardware IRQ 48", size=12, color=POS, bold=True))
    frags.append(text(300, 134, "(Шторм переривань)", size=10, color=POS, italic=True))

    # CPU Cores Container
    frags.append(rect(400, 40, 290, 260, fill="#f8fafc", stroke="#334155", sw=2, rx=8))
    frags.append(text(545, 68, "Багатоядерний процесор (CPU)", size=15, bold=True, color="#334155"))

    # Core 0 - Overloaded
    frags.append(rect(420, 90, 250, 42, fill="#fca5a5", stroke=POS, sw=2, rx=6))
    frags.append(text(545, 107, "Ядро 0: 100% SoftIRQ / ksoftirqd", size=13, color="#7f1d1d", bold=True))
    frags.append(text(545, 123, "Вузьке місце (Bottleneck)", size=11, color="#7f1d1d", italic=True))

    # Core 1 - Idle
    frags.append(rect(420, 142, 250, 38, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(545, 165, "Ядро 1: 0% (Idle / Простой)", size=12, color="#475569"))

    # Core 2 - Idle
    frags.append(rect(420, 190, 250, 38, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(545, 213, "Ядро 2: 0% (Idle / Простой)", size=12, color="#475569"))

    # Core 3 - Idle
    frags.append(rect(420, 238, 250, 38, fill="#e2e8f0", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(545, 261, "Ядро 3: 0% (Idle / Простой)", size=12, color="#475569"))

    img_path = os.path.join(os.path.dirname(__file__), 'img', 'single-queue-interrupt.svg')
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    render(img_path, w, h, *frags, title=None)

def generate_rss_architecture():
    w, h = 860, 440
    frags = []

    # Step 1: Ingress Packet
    frags.append(rect(15, 165, 110, 85, fill="#e0e7ff", stroke="#3730a3", sw=1.5, rx=6))
    frags.append(text(70, 188, "Вхідний пакет", size=13, bold=True, color="#3730a3"))
    frags.append(text(70, 206, "4-Tuple:", size=11, color=INK))
    frags.append(text(70, 222, "IPs, Ports, Proto", size=10, color=MUTED, italic=True))

    frags.append(arrow(125, 207, 160, 207, color=LINE, sw=2))

    # Step 2: Toeplitz Engine
    frags.append(rect(160, 150, 155, 115, fill="#dcfce7", stroke="#15803d", sw=2, rx=8))
    frags.append(text(237, 173, "Toeplitz Hash Engine", size=13, bold=True, color="#15803d"))
    frags.append(text(237, 193, "Ключ RSS (40B)", size=11, color="#166534"))
    frags.append(line(175, 205, 300, 205, color="#86efac", sw=1))
    frags.append(text(237, 222, "32-бітний хеш", size=12, bold=True, color=INK))
    frags.append(text(237, 240, "0x8F4A2C1B", size=11, color=MUTED))

    frags.append(arrow(315, 207, 365, 207, color=LINE, sw=2))
    frags.append(text(340, 192, "7 біт (LSB)", size=11, color=MUTED, bold=True))

    # Step 3: RETA Table
    frags.append(rect(365, 80, 165, 280, fill="#fef9c3", stroke="#a16207", sw=2, rx=8))
    frags.append(text(447, 105, "Таблиця RETA", size=14, bold=True, color="#a16207"))
    frags.append(text(447, 123, "(128 комірок)", size=11, color="#854d0e", italic=True))

    # RETA rows
    reta_entries = [
        ("0", "Rx Queue 0", "#dbeafe", "#1e40af"),
        ("1", "Rx Queue 1", "#fce7f3", "#9d174d"),
        ("2", "Rx Queue 2", "#fef3c7", "#92400e"),
        ("...", "...", "#f3f4f6", MUTED),
        ("127", "Rx Queue 3", "#e0e7ff", "#3730a3"),
    ]
    for i, (idx, qval, bgcol, txtcol) in enumerate(reta_entries):
        ry = 142 + i * 40
        frags.append(rect(380, ry, 135, 32, fill=bgcol, stroke="#ca8a04", sw=1, rx=4))
        frags.append(text(405, ry + 20, idx, size=11, bold=True, color=INK))
        frags.append(text(465, ry + 20, qval, size=11, bold=True, color=txtcol))

    # Arrow from RETA selected entry (idx 2) to Queue 2
    frags.append(arrow(515, 238, 595, 238, color=POS, sw=2.5))

    # Step 4: Multi-Queue RX & CPU Cores
    queues = [
        ("Rx Queue 0", "MSI-X 48", "Core 0", "#dbeafe", "#1e40af", 50),
        ("Rx Queue 1", "MSI-X 49", "Core 1", "#fce7f3", "#9d174d", 140),
        ("Rx Queue 2", "MSI-X 50", "Core 2", "#fef3c7", "#92400e", 230),
        ("Rx Queue 3", "MSI-X 51", "Core 3", "#e0e7ff", "#3730a3", 320),
    ]

    for qname, irqname, cname, bgcol, bordercol, qy in queues:
        # Rx Queue box
        frags.append(rect(595, qy, 105, 55, fill=bgcol, stroke=bordercol, sw=1.5, rx=6))
        frags.append(text(647, qy + 22, qname, size=12, bold=True, color=bordercol))
        frags.append(text(647, qy + 40, irqname, size=10, color=MUTED, italic=True))

        # Arrow queue -> CPU
        frags.append(arrow(700, qy + 27, 740, qy + 27, color=bordercol, sw=2))

        # CPU core box
        frags.append(rect(740, qy + 5, 95, 45, fill="#f8fafc", stroke=bordercol, sw=2, rx=6))
        frags.append(text(787, qy + 30, cname, size=13, bold=True, color=INK))

    img_path = os.path.join(os.path.dirname(__file__), 'img', 'rss-architecture.svg')
    render(img_path, w, h, *frags, title=None)

if __name__ == '__main__':
    generate_single_queue()
    generate_rss_architecture()
    print("Figures generated successfully.")
