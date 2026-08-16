# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
PURPLE_FILL = "#f3e8ff"
GREY_FILL = "#f5f7fa"
LINE_COLOR = "#333333"

# ── 1. Порівняння варіантів підключення: PCIe vs RDMA vs TCP ──
def fig_transport_comparison():
    W, H = 1000, 480
    p = []

    col_w = 300
    gap = 20

    # Колонка 1: Локальний PCIe NVMe
    x1 = 20
    p.append(rect(x1, 20, col_w, 440, fill=BLUE_FILL, stroke=LINE_COLOR, rx=8))
    p.append(text(x1 + 150, 48, "1. Локальний PCIe NVMe", size=15, bold=True))
    
    p.append(rect(x1 + 20, 75, 260, 55, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x1 + 150, 98, "Хост CPU / App", size=12, bold=True))
    p.append(text(x1 + 150, 116, "blk-mq & nvme.ko", size=11, color="#555555"))

    p.append(arrow(x1 + 150, 130, x1 + 150, 160, color=LINE_COLOR, sw=2))

    p.append(rect(x1 + 20, 160, 260, 60, fill=GREY_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x1 + 150, 185, "PCIe Bus & Doorbell BAR", size=12, bold=True))
    p.append(text(x1 + 150, 205, "Direct PCIe DMA Transfers", size=11, color="#555555"))

    p.append(arrow(x1 + 150, 220, x1 + 150, 250, color=LINE_COLOR, sw=2))

    p.append(rect(x1 + 20, 250, 260, 65, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x1 + 150, 275, "Локальний NVMe SSD", size=12, bold=True))
    p.append(text(x1 + 150, 295, "Затримка: 10 - 20 µs", size=11, color="#2e7d32", bold=True))

    p.append(rect(x1 + 20, 340, 260, 105, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x1 + 150, 362, "Особливості:", size=11, bold=True))
    p.append(text(x1 + 150, 382, "• Максимальна швидкість", size=11, color="#333333"))
    p.append(text(x1 + 150, 402, "• Фізичне обмеження шасі", size=11, color="#333333"))
    p.append(text(x1 + 150, 422, "• Без мережевого оверхеду", size=11, color="#333333"))

    # Колонка 2: NVMe over RDMA (RoCE/InfiniBand)
    x2 = x1 + col_w + gap
    p.append(rect(x2, 20, col_w, 440, fill=WARM_FILL, stroke=LINE_COLOR, rx=8))
    p.append(text(x2 + 150, 48, "2. NVMe over RDMA", size=15, bold=True))

    p.append(rect(x2 + 20, 75, 260, 55, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x2 + 150, 98, "Хост CPU (Bypassed on Data)", size=12, bold=True))
    p.append(text(x2 + 150, 116, "nvme-rdma (Zero-Copy)", size=11, color="#555555"))

    p.append(arrow(x2 + 150, 130, x2 + 150, 160, color=LINE_COLOR, sw=2))

    p.append(rect(x2 + 20, 160, 260, 60, fill=PURPLE_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x2 + 150, 185, "RDMA NIC (RNIC) & Fabric", size=12, bold=True))
    p.append(text(x2 + 150, 205, "InfiniBand / RoCEv2 (No CPU)", size=11, color="#555555"))

    p.append(arrow(x2 + 150, 220, x2 + 150, 250, color=LINE_COLOR, sw=2))

    p.append(rect(x2 + 20, 250, 260, 65, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x2 + 150, 275, "Віддалений Target SSD", size=12, bold=True))
    p.append(text(x2 + 150, 295, "Затримка: 20 - 45 µs", size=11, color="#2e7d32", bold=True))

    p.append(rect(x2 + 20, 340, 260, 105, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x2 + 150, 362, "Особливості:", size=11, bold=True))
    p.append(text(x2 + 150, 382, "• Апаратне розвантаження CPU", size=11, color="#333333"))
    p.append(text(x2 + 150, 402, "• Потребує Lossless Ethernet", size=11, color="#333333"))
    p.append(text(x2 + 150, 422, "• Спеціалізовані RNIC картки", size=11, color="#333333"))

    # Колонка 3: NVMe over TCP
    x3 = x2 + col_w + gap
    p.append(rect(x3, 20, col_w, 440, fill=GREY_FILL, stroke=LINE_COLOR, rx=8))
    p.append(text(x3 + 150, 48, "3. NVMe over TCP", size=15, bold=True))

    p.append(rect(x3 + 20, 75, 260, 55, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x3 + 150, 98, "Хост CPU / TCP Stack", size=12, bold=True))
    p.append(text(x3 + 150, 116, "nvme-tcp (Kernel Sockets)", size=11, color="#555555"))

    p.append(arrow(x3 + 150, 130, x3 + 150, 160, color=LINE_COLOR, sw=2))

    p.append(rect(x3 + 20, 160, 260, 60, fill=BLUE_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x3 + 150, 185, "Стандартний Ethernet", size=12, bold=True))
    p.append(text(x3 + 150, 205, "Звичайний TCP/IP (Port 4420)", size=11, color="#555555"))

    p.append(arrow(x3 + 150, 220, x3 + 150, 250, color=LINE_COLOR, sw=2))

    p.append(rect(x3 + 20, 250, 260, 65, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(x3 + 150, 275, "Віддалений Target SSD", size=12, bold=True))
    p.append(text(x3 + 150, 295, "Затримка: 60 - 120 µs", size=11, color="#d32f2f", bold=True))

    p.append(rect(x3 + 20, 340, 260, 105, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(x3 + 150, 362, "Особливості:", size=11, bold=True))
    p.append(text(x3 + 150, 382, "• Працює на будь-яких NIC", size=11, color="#333333"))
    p.append(text(x3 + 150, 402, "• Не вимагає налаштувань SAN", size=11, color="#333333"))
    p.append(text(x3 + 150, 422, "• Навантажує CPU (TCP stack)", size=11, color="#333333"))

    render(os.path.join(IMG, "nvme-of-transport-comparison.svg"), W, H, *p)

# ── 2. Структура PDU NVMe/TCP та Капсули ──
def fig_tcp_pdu_capsule():
    W, H = 960, 360
    p = []

    p.append(text(480, 25, "Анатомія NVMe/TCP Command PDU (Капсула Команди)", size=15, bold=True))

    p.append(rect(20, 50, 920, 280, fill=GREY_FILL, stroke=LINE_COLOR, rx=8))

    # Блок 1: PDU Header (8 байт)
    p.append(rect(40, 90, 180, 200, fill=BLUE_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(130, 115, "PDU Header (8 Б)", size=13, bold=True))
    p.append(line(40, 130, 220, 130, color=LINE_COLOR, sw=1))
    p.append(text(130, 155, "type = 0x04 (Cmd)", size=11))
    p.append(text(130, 180, "flags (HDigest/DDigest)", size=11))
    p.append(text(130, 205, "hlen = 72 (8+64 Б)", size=11))
    p.append(text(130, 230, "pdo = Data Offset", size=11))
    p.append(text(130, 255, "plen = Total Length", size=11))

    # Блок 2: Command Capsule (64 байти SQE)
    p.append(rect(240, 90, 360, 200, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(420, 115, "NVMe Command Capsule (64 Б)", size=13, bold=True))
    p.append(line(240, 130, 600, 130, color=LINE_COLOR, sw=1))
    p.append(text(420, 155, "opcode (Read/Write/Flush)", size=11))
    p.append(text(420, 180, "command_id (16-bit SQE ID)", size=11))
    p.append(text(420, 205, "nsid (Namespace ID)", size=11))
    p.append(text(420, 230, "SGL Descriptor (Data Pointer)", size=11, bold=True, color="#1a5fb4"))
    p.append(text(420, 255, "cdw10..15 (LBA start, count, flags)", size=11))

    # Блок 3: In-Capsule Data (Опціонально)
    p.append(rect(620, 90, 200, 200, fill=WARM_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(720, 115, "In-Capsule Data", size=13, bold=True))
    p.append(text(720, 135, "(до 4-8 КБ, опція)", size=10, color="#666666"))
    p.append(line(620, 150, 820, 150, color=LINE_COLOR, sw=1))
    p.append(text(720, 180, "Дані Запису (Write)", size=11))
    p.append(text(720, 205, "Передаються разом", size=11))
    p.append(text(720, 230, "із командою в одному", size=11))
    p.append(text(720, 255, "мережевому пакунку", size=11))

    # Блок 4: CRC32C Digest
    p.append(rect(830, 90, 90, 200, fill=PURPLE_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(875, 135, "CRC32C", size=12, bold=True))
    p.append(text(875, 160, "Header &", size=11))
    p.append(text(875, 180, "Data", size=11))
    p.append(text(875, 200, "Digest", size=11))
    p.append(text(875, 225, "(4 Б + 4 Б)", size=10, color="#555555"))

    render(os.path.join(IMG, "nvme-tcp-pdu-capsule.svg"), W, H, *p)

# ── 3. Архітектура Ядра Linux: Initiator blk-mq -> Target nvmet ──
def fig_kernel_nvme_stack():
    W, H = 1000, 460
    p = []

    p.append(text(500, 25, "Стек підсистем NVMe-oF у ядрі Linux (Initiator та Target)", size=15, bold=True))

    # Ліва сторона: Host Initiator
    p.append(rect(20, 50, 440, 390, fill=BLUE_FILL, stroke=LINE_COLOR, rx=8))
    p.append(text(240, 75, "Хост (Initiator Node)", size=14, bold=True))

    p.append(rect(40, 95, 400, 50, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(240, 120, "User Space App / VFS (/dev/nvme0n1)", size=12, bold=True))

    p.append(arrow(240, 145, 240, 165, color=LINE_COLOR, sw=2))

    p.append(rect(40, 165, 400, 55, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(240, 185, "blk-mq (Multi-Queue Block Layer)", size=12, bold=True))
    p.append(text(240, 205, "Hardware Contexts (hctx) = 1:1 CPU cores", size=10, color="#444444"))

    p.append(arrow(240, 220, 240, 240, color=LINE_COLOR, sw=2))

    p.append(rect(40, 240, 400, 60, fill=WARM_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(240, 260, "nvme-core & nvme-fabrics", size=12, bold=True))
    p.append(text(240, 282, "Транспортний драйвер: nvme-tcp / nvme-rdma", size=11, color="#1a5fb4"))

    p.append(arrow(240, 300, 240, 325, color=LINE_COLOR, sw=2))

    p.append(rect(40, 325, 400, 95, fill=GREY_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(240, 350, "Мережевий стек ядра", size=12, bold=True))
    p.append(text(240, 372, "TCP Sockets (AF_INET) / IB Verbs", size=11))
    p.append(text(240, 395, "NIC / RNIC Driver", size=11, color="#555555"))

    # Стрілка зв'язку в центрі
    p.append(arrow(460, 370, 540, 370, color="#d32f2f", sw=3))
    p.append(text(500, 355, "Мережа Fabric", size=11, bold=True, color="#d32f2f"))

    # Права сторона: Target Server (nvmet)
    p.append(rect(540, 50, 440, 390, fill=PURPLE_FILL, stroke=LINE_COLOR, rx=8))
    p.append(text(760, 75, "Таргет (Target Node / nvmet)", size=14, bold=True))

    p.append(rect(560, 95, 400, 50, fill="#ffffff", stroke=LINE_COLOR, rx=4))
    p.append(text(760, 118, "Configfs / nvmetcli", size=12, bold=True))
    p.append(text(760, 134, "/sys/kernel/config/nvmet/", size=10, color="#555555"))

    p.append(arrow(760, 145, 760, 165, color=LINE_COLOR, sw=2))

    p.append(rect(560, 165, 400, 60, fill=WARM_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(760, 185, "Підсистема nvmet (Kernel Target)", size=12, bold=True))
    p.append(text(760, 207, "nvmet-tcp / nvmet-rdma", size=11, color="#1a5fb4"))

    p.append(arrow(760, 225, 760, 245, color=LINE_COLOR, sw=2))

    p.append(rect(560, 245, 400, 65, fill=GREEN_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(760, 267, "nvmet_bdev / nvmet_passthru", size=12, bold=True))
    p.append(text(760, 290, "Емуляція контролера або Pass-through", size=11, color="#333333"))

    p.append(arrow(760, 310, 760, 325, color=LINE_COLOR, sw=2))

    p.append(rect(560, 325, 400, 95, fill=GREY_FILL, stroke=LINE_COLOR, rx=4))
    p.append(text(760, 350, "Локальні Накопичувачі Таргета", size=12, bold=True))
    p.append(text(760, 372, "/dev/nvme0n1, LVM volumes, RAW Disks", size=11))
    p.append(text(760, 395, "PCIe NVMe Controllers", size=11, color="#555555"))

    render(os.path.join(IMG, "nvme-kernel-target-stack.svg"), W, H, *p)

def run_all():
    fig_transport_comparison()
    fig_tcp_pdu_capsule()
    fig_kernel_nvme_stack()

if __name__ == "__main__":
    run_all()
