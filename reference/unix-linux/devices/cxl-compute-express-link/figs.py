import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
import svgkit

def generate_arch():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cxl-arch.svg")

    frags = []

    # Host CPU A
    frags.append(svgkit.rect(20, 40, 210, 200, fill="#eef6ff", stroke="#2457d6", sw=2))
    frags.append(svgkit.text(125, 65, "Host CPU A", size=15, color="#2457d6", bold=True))
    frags.append(svgkit.fitbox(30, 80, 190, 45, "Ядра CPU & L3 Кеш", size=12, fill="#ffffff", stroke="#2457d6"))
    frags.append(svgkit.fitbox(30, 145, 90, 75, "Контролер\nDDR5", size=11, fill="#e8f8f0", stroke="#27ae60"))
    frags.append(svgkit.fitbox(130, 145, 90, 75, "CXL Root\nPort (HDM)", size=11, fill="#fff8e6", stroke="#d97706"))

    # Local DDR5 RAM A
    frags.append(svgkit.fitbox(20, 280, 100, 45, "Локальна\nDDR5 RAM", size=11, fill="#e8f8f0", stroke="#27ae60", bold=True))
    frags.append(svgkit.arrow(75, 220, 75, 280, color="#27ae60", sw=2))

    # Host CPU B
    frags.append(svgkit.rect(610, 40, 210, 200, fill="#eef6ff", stroke="#2457d6", sw=2))
    frags.append(svgkit.text(715, 65, "Host CPU B", size=15, color="#2457d6", bold=True))
    frags.append(svgkit.fitbox(620, 80, 190, 45, "Ядра CPU & L3 Кеш", size=12, fill="#ffffff", stroke="#2457d6"))
    frags.append(svgkit.fitbox(620, 145, 90, 75, "CXL Root\nPort (HDM)", size=11, fill="#fff8e6", stroke="#d97706"))
    frags.append(svgkit.fitbox(720, 145, 90, 75, "Контролер\nDDR5", size=11, fill="#e8f8f0", stroke="#27ae60"))

    # Local DDR5 RAM B
    frags.append(svgkit.fitbox(720, 280, 100, 45, "Локальна\nDDR5 RAM", size=11, fill="#e8f8f0", stroke="#27ae60", bold=True))
    frags.append(svgkit.arrow(765, 220, 765, 280, color="#27ae60", sw=2))

    # CXL Switch (Fabric)
    frags.append(svgkit.rect(290, 130, 260, 110, fill="#f4f4f5", stroke="#41464b", sw=2))
    frags.append(svgkit.text(420, 155, "CXL 2.0/3.0 Switch (Fabric)", size=13, color="#1a1a1a", bold=True))
    frags.append(svgkit.fitbox(300, 175, 110, 50, "Upstream Port 0\n(VCS 0)", size=10, fill="#ffffff", stroke="#6b7280"))
    frags.append(svgkit.fitbox(430, 175, 110, 50, "Upstream Port 1\n(VCS 1)", size=10, fill="#ffffff", stroke="#6b7280"))

    # Connections Host -> Switch
    frags.append(svgkit.line(220, 182, 300, 182, color="#d97706", sw=2))
    frags.append(svgkit.text(260, 172, "CXL.mem", size=10, color="#d97706", bold=True))
    frags.append(svgkit.line(620, 182, 540, 182, color="#d97706", sw=2))
    frags.append(svgkit.text(580, 172, "CXL.mem", size=10, color="#d97706", bold=True))

    # CXL Type 3 MLD Memory Pool
    frags.append(svgkit.rect(270, 280, 300, 130, fill="#fff8e6", stroke="#d97706", sw=2))
    frags.append(svgkit.text(420, 302, "CXL Type 3 Memory Expander (MLD)", size=13, color="#d97706", bold=True))
    frags.append(svgkit.fitbox(285, 320, 130, 75, "Logical Device 0\nvLD 0 (256 GB)\nHost A Node", size=10, fill="#ffffff", stroke="#2457d6"))
    frags.append(svgkit.fitbox(425, 320, 130, 75, "Logical Device 1\nvLD 1 (512 GB)\nHost B Node", size=10, fill="#ffffff", stroke="#2457d6"))

    # Switch -> Memory Pool connection
    frags.append(svgkit.arrow(420, 240, 420, 280, color="#d97706", sw=2.5))

    svgkit.render(out_path, 840, 440, *frags, title="Топологія архітектури CXL та дезагрегація пам'яті")


def generate_protocol_stack():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cxl-protocol-stack.svg")

    frags = []

    # Title / Top Level Protocols
    frags.append(svgkit.text(400, 30, "Стек протоколів CXL (Compute Express Link)", size=16, color="#1a1a1a", bold=True))

    # Three Protocols Boxes
    # CXL.io
    frags.append(svgkit.rect(60, 60, 200, 140, fill="#eef6ff", stroke="#2457d6", sw=2))
    frags.append(svgkit.text(160, 85, "CXL.io", size=15, color="#2457d6", bold=True))
    frags.append(svgkit.mtext(160, 118, "PCIe TLP / DLLP\nВиявлення & Конфігурація\nAER / Переривання / DMA", size=11, color="#1a1a1a"))

    # CXL.cache
    frags.append(svgkit.rect(290, 60, 220, 140, fill="#fff8e6", stroke="#d97706", sw=2))
    frags.append(svgkit.text(400, 85, "CXL.cache", size=15, color="#d97706", bold=True))
    frags.append(svgkit.mtext(400, 118, "Когерентність кешу\nD2H & H2D Запити/Відповіді\nSnoop / Invalidate", size=11, color="#1a1a1a"))

    # CXL.mem
    frags.append(svgkit.rect(530, 60, 210, 140, fill="#e8f8f0", stroke="#27ae60", sw=2))
    frags.append(svgkit.text(635, 85, "CXL.mem", size=15, color="#27ae60", bold=True))
    frags.append(svgkit.mtext(635, 118, "Прямий доступ до RAM\nM2S / S2M Семантика\nLoad / Store інструкції", size=11, color="#1a1a1a"))

    # ARB / MUX Layer
    frags.append(svgkit.rect(60, 230, 680, 50, fill="#f4f4f5", stroke="#41464b", sw=2))
    frags.append(svgkit.text(400, 260, "Arbitration and Multiplexing Layer (ARB / MUX)", size=13, color="#1a1a1a", bold=True))

    # Connectors to ARB/MUX
    frags.append(svgkit.arrow(160, 200, 160, 230, color="#2457d6", sw=2))
    frags.append(svgkit.arrow(400, 200, 400, 230, color="#d97706", sw=2))
    frags.append(svgkit.arrow(635, 200, 635, 230, color="#27ae60", sw=2))

    # Physical Flex Bus PHY Layer
    frags.append(svgkit.rect(60, 310, 680, 50, fill="#eaeaea", stroke="#1a1a1a", sw=2))
    frags.append(svgkit.text(400, 340, "Flex Bus Physical Layer (PCIe 5.0 32GT/s / PCIe 6.0 64GT/s Flit Mode)", size=13, color="#1a1a1a", bold=True))

    # Connect ARB/MUX to PHY
    frags.append(svgkit.arrow(400, 280, 400, 310, color="#1a1a1a", sw=2))

    svgkit.render(out_path, 800, 390, *frags, title="Мультиплексування протоколів CXL поверх фізичного рівня PCIe")


if __name__ == "__main__":
    generate_arch()
    generate_protocol_stack()
