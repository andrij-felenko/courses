import sys
import os

# Add scripts directory to path (four levels up from reference/unix-linux/io/nvme-target-kernel-subsystem/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def draw_arch():
    frags = []
    
    # User Space container
    frags.append(rect(20, 20, 780, 90, rx=8, fill="#f0f7ff", stroke="#0066cc", sw=1.5))
    frags.append(text(35, 45, "User Space (Користувацький простір)", size=15, color="#004488", anchor="start", bold=True))
    
    # User Space components
    frags.append(fitbox(50, 52, 330, 42, "nvmetcli (Python CLI / JSON)", size=13, fill="#e6f2ff", stroke="#0066cc"))
    frags.append(fitbox(410, 52, 370, 42, "configfs (/sys/kernel/config/nvmet/)", size=13, fill="#e6f2ff", stroke="#0066cc"))
    
    # Kernel Space container
    frags.append(rect(20, 130, 780, 360, rx=8, fill="#f4fbf7", stroke="#27ae60", sw=1.5))
    frags.append(text(35, 155, "Kernel Space (Простір ядра Linux)", size=15, color="#1e8449", anchor="start", bold=True))
    
    # Target Core box
    frags.append(rect(40, 170, 740, 120, rx=6, fill="#e8f8f5", stroke="#16a085", sw=1.2))
    frags.append(text(55, 195, "NVMe Target Core (nvmet.ko)", size=14, color="#117864", anchor="start", bold=True))
    
    frags.append(fitbox(55, 210, 220, 40, "Підсистеми & NQN-маршрутизація", size=12, fill="#ffffff", stroke="#16a085"))
    frags.append(fitbox(290, 210, 240, 40, "Автентифікація (DH-HMAC-CHAP, kTLS)", size=12, fill="#ffffff", stroke="#16a085"))
    frags.append(fitbox(545, 210, 220, 40, "Диспетчер команд (struct nvmet_req)", size=12, fill="#ffffff", stroke="#16a085"))

    frags.append(text(410, 275, "Фабрична абстракція (struct nvmet_fabrics_ops)", size=12, color="#555555", anchor="middle", italic=True))

    # Network Transports block
    frags.append(rect(40, 310, 350, 160, rx=6, fill="#fef9e7", stroke="#f39c12", sw=1.2))
    frags.append(text(55, 332, "Мережеві транспорти (Transports)", size=13, color="#b7950b", anchor="start", bold=True))
    
    frags.append(fitbox(55, 345, 320, 32, "nvmet-tcp (TCP/IP socket, kTLS)", size=12, fill="#ffffff", stroke="#f39c12"))
    frags.append(fitbox(55, 385, 320, 32, "nvmet-rdma (RoCE, InfiniBand, iWARP)", size=12, fill="#ffffff", stroke="#f39c12"))
    frags.append(fitbox(55, 425, 320, 32, "nvmet-fc (Fibre Channel) / nvmet-loop", size=12, fill="#ffffff", stroke="#f39c12"))

    # Backends block
    frags.append(rect(430, 310, 350, 160, rx=6, fill="#fdf2e9", stroke="#e67e22", sw=1.2))
    frags.append(text(445, 332, "Бекенди зберігання (Storage Backends)", size=13, color="#a04000", anchor="start", bold=True))
    
    frags.append(fitbox(445, 345, 320, 32, "bdev (blk-mq, submit_bio, Direct I/O)", size=12, fill="#ffffff", stroke="#e67e22"))
    frags.append(fitbox(445, 385, 320, 32, "file (VFS, read_iter / write_iter)", size=12, fill="#ffffff", stroke="#e67e22"))
    frags.append(fitbox(445, 425, 320, 32, "passthru (PCIe NVMe, passthru_execute_cmd)", size=12, fill="#ffffff", stroke="#e67e22"))

    # Connections / Arrows
    frags.append(arrow(215, 94, 215, 170, color="#0066cc", sw=1.5))
    frags.append(arrow(595, 94, 595, 170, color="#0066cc", sw=1.5))

    frags.append(arrow(215, 310, 215, 290, color="#f39c12", sw=1.5))
    frags.append(arrow(605, 290, 605, 310, color="#e67e22", sw=1.5))

    render(os.path.join(IMG, "nvmet-arch.svg"), 820, 510, *frags, title="NVMe Target Architecture")

def draw_lifecycle():
    frags = []
    
    # Outer frame
    frags.append(rect(20, 20, 800, 370, rx=8, fill="#fcfcfc", stroke="#cccccc", sw=1.0))
    frags.append(text(40, 45, "Шлях проходження I/O команди у підсистемі nvmet (Fast-Path)", size=15, color="#1a1a1a", anchor="start", bold=True))

    # Process boxes
    frags.append(fitbox(40, 70, 160, 50, "1. Прибуття PDU/Капсули\nTransport Rx (TCP/RDMA)", size=11, fill="#ebf5fb", stroke="#2980b9"))
    frags.append(fitbox(230, 70, 160, 50, "2. Ініціалізація nvmet_req\nВалідація nsid, SGL & Opcode", size=11, fill="#e8f8f5", stroke="#16a085"))
    frags.append(fitbox(420, 70, 160, 50, "3. Диспетчеризація бекенду\n(nvmet_req->execute)", size=11, fill="#fef9e7", stroke="#f39c12"))

    # Decision Split
    frags.append(fitbox(610, 70, 180, 45, "4a. bdev backend\nПобудова bio + submit_bio()", size=11, fill="#fadbd8", stroke="#b03a2e"))
    frags.append(fitbox(610, 150, 180, 45, "4b. passthru backend\nForwarding to NVMe HW", size=11, fill="#f5eeed", stroke="#78281f"))

    # Completion step
    frags.append(fitbox(420, 260, 190, 50, "5. Асинхронний колбек\nnvmet_bio_done() / completion", size=11, fill="#eaf2f8", stroke="#2471a3"))
    frags.append(fitbox(40, 260, 180, 50, "6. Відправка Response PDU\nTransport Tx (Zero-Copy Send)", size=11, fill="#d5f5e3", stroke="#27ae60"))

    # Connective arrows
    frags.append(arrow(200, 95, 230, 95, color="#2980b9", sw=1.5))
    frags.append(arrow(390, 95, 420, 95, color="#16a085", sw=1.5))
    
    # Arrow to 4a
    frags.append(arrow(580, 92, 610, 92, color="#f39c12", sw=1.5))

    # Orthogonal routed line to 4b (down then right)
    frags.append(line(500, 120, 500, 172, color="#f39c12", sw=1.5))
    frags.append(arrow(500, 172, 610, 172, color="#f39c12", sw=1.5))

    # Completions back to 5
    frags.append(arrow(700, 115, 700, 195, color="#b03a2e", sw=1.5))
    frags.append(line(700, 195, 700, 285, color="#b03a2e", sw=1.5))
    frags.append(arrow(700, 285, 610, 285, color="#b03a2e", sw=1.5))

    frags.append(arrow(420, 285, 220, 285, color="#2471a3", sw=1.5))

    render(os.path.join(IMG, "nvmet-req-lifecycle.svg"), 840, 410, *frags, title="NVMe Target Request Lifecycle")

if __name__ == "__main__":
    draw_arch()
    draw_lifecycle()
    print("Figures generated successfully.")
