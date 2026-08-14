import sys
import os

# Add scripts directory to path to import svgkit
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "../../../.."))
sys.path.insert(0, os.path.join(repo_root, "scripts"))

from svgkit import render, rect, line, arrow, text, textbox, fitbox, FILL, BG, LINE, POS, NEG, FIELD, MUTED, INK

img_dir = os.path.join(script_dir, "img")
os.makedirs(img_dir, exist_ok=True)


def fig_context_switch():
    """Порівняння перемикання контексту: Virtio-net (QEMU User-space) vs vhost-net (In-Kernel)."""
    w, h = 840, 480
    frags = []

    # Title background banner
    frags.append(rect(15, 15, 810, 450, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    # Left box: User-space Virtio-net (QEMU)
    frags.append(rect(30, 40, 375, 410, fill="#f4f6f8", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(text(217, 65, "Класичний Virtio-net (QEMU Userspace)", size=14, bold=True, color=INK))

    # Regions inside left box
    frags.append(rect(45, 85, 345, 80, fill="#e6f0fa", stroke="#0969da", sw=1, rx=4))
    frags.append(text(217, 105, "Guest Kernel (virtio-net driver)", size=12, bold=True, color="#0969da"))
    frags.append(text(217, 125, "1. Write kick → MMIO register", size=11, color=MUTED))
    frags.append(text(217, 145, "vring_avail update in GPA", size=11, color=MUTED))

    # Boundary 1
    frags.append(line(45, 175, 390, 175, color=POS, dash="4,4"))
    frags.append(text(217, 188, "★ VM EXIT (Guest → Host KVM)", size=10, bold=True, color=POS))

    frags.append(rect(45, 198, 345, 75, fill="#fff8c5", stroke="#bf8700", sw=1, rx=4))
    frags.append(text(217, 218, "Host KVM (kernel-space)", size=12, bold=True, color="#bf8700"))
    frags.append(text(217, 238, "2. Eventfd signal to QEMU thread", size=11, color=MUTED))

    # Boundary 2
    frags.append(line(45, 280, 390, 280, color=POS, dash="4,4"))
    frags.append(text(217, 293, "★ Context Switch (Kernel → QEMU User)", size=10, bold=True, color=POS))

    frags.append(rect(45, 303, 345, 70, fill="#ffebe9", stroke="#cf222e", sw=1, rx=4))
    frags.append(text(217, 323, "QEMU Process (user-space)", size=12, bold=True, color="#cf222e"))
    frags.append(text(217, 343, "3. Process vring & call write() to TAP", size=11, color=MUTED))

    # Boundary 3
    frags.append(line(45, 380, 390, 380, color=POS, dash="4,4"))
    frags.append(text(217, 393, "★ Syscall write() (User → Kernel)", size=10, bold=True, color=POS))

    frags.append(rect(45, 403, 345, 35, fill="#dafbe1", stroke="#1a7f37", sw=1, rx=4))
    frags.append(text(217, 424, "Host Netdev / TAP Interface", size=11, bold=True, color="#1a7f37"))

    # Right box: In-Kernel vhost-net
    frags.append(rect(435, 40, 375, 410, fill="#f4f6f8", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(text(622, 65, "Прискорений vhost-net (In-Kernel)", size=14, bold=True, color=INK))

    # Regions inside right box
    frags.append(rect(450, 85, 345, 80, fill="#e6f0fa", stroke="#0969da", sw=1, rx=4))
    frags.append(text(622, 105, "Guest Kernel (virtio-net driver)", size=12, bold=True, color="#0969da"))
    frags.append(text(622, 125, "1. Write kick → MMIO register", size=11, color=MUTED))
    frags.append(text(622, 145, "vring_avail update in GPA", size=11, color=MUTED))

    # Boundary 1 (Only VM exit to KVM, bypass QEMU userspace!)
    frags.append(line(450, 175, 795, 175, color=FIELD, dash="4,4"))
    frags.append(text(622, 188, "★ Fast VM Exit → KVM ioeventfd", size=10, bold=True, color=FIELD))

    frags.append(rect(450, 203, 345, 185, fill="#dafbe1", stroke="#1a7f37", sw=1.5, rx=4))
    frags.append(text(622, 225, "Host Kernel-Space (vhost-net)", size=13, bold=True, color="#1a7f37"))
    frags.append(text(622, 250, "2. vhost-$PID kernel thread wakes up", size=11, color=INK))
    frags.append(text(622, 275, "3. Direct GPA → HVA translation of vring", size=11, color=INK))
    frags.append(text(622, 300, "4. Directly injects sk_buff into TAP driver", size=11, color=INK))
    frags.append(text(622, 325, "5. irqfd triggers MSI-X interrupt to Guest", size=11, color=INK))
    frags.append(rect(470, 345, 305, 33, fill="#ffffff", stroke="#1a7f37", sw=1, rx=3))
    frags.append(text(622, 366, "Прямий bypass QEMU: 0 перемикань у user-space!", size=10, bold=True, color="#1a7f37"))

    frags.append(rect(450, 403, 345, 35, fill="#dafbe1", stroke="#1a7f37", sw=1, rx=4))
    frags.append(text(622, 424, "Host Netdev / TAP Interface", size=11, bold=True, color="#1a7f37"))

    render(os.path.join(img_dir, "vhost-net-context-switch.svg"), w, h, *frags)


def fig_architecture():
    """Повна архітектура vhost-net: Control Plane vs Data Plane."""
    w, h = 840, 520
    frags = []

    # Title background
    frags.append(rect(15, 15, 810, 490, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    # Top banner: Guest OS RAM & CPU
    frags.append(rect(30, 40, 780, 100, fill="#ddf4ff", stroke="#54aef0", sw=1.5, rx=6))
    frags.append(text(420, 62, "Гостьова система (Guest Virtual Machine)", size=14, bold=True, color="#0969da"))
    frags.append(rect(50, 75, 340, 50, fill="#ffffff", stroke="#54aef0", rx=4))
    frags.append(text(220, 95, "virtio-net Driver (Guest Kernel)", size=12, bold=True, color=INK))
    frags.append(text(220, 112, "kick (MMIO) / MSI-X Interrupt Handler", size=10, color=MUTED))

    frags.append(rect(430, 75, 360, 50, fill="#ffffff", stroke="#54aef0", rx=4))
    frags.append(text(610, 95, "Shared Guest RAM (GPA)", size=12, bold=True, color=INK))
    frags.append(text(610, 112, "vring: Descriptor Table | Avail Ring | Used Ring", size=10, color=MUTED))

    # Control Plane (Left Side, QEMU Userspace)
    frags.append(rect(30, 160, 360, 180, fill="#fff8c5", stroke="#bf8700", sw=1.5, rx=6))
    frags.append(text(210, 182, "Control Plane (QEMU Userspace)", size=13, bold=True, color="#bf8700"))
    frags.append(rect(50, 195, 320, 40, fill="#ffffff", stroke="#bf8700", rx=4))
    frags.append(text(210, 219, "QEMU Process (virtio-net device model)", size=11, bold=True, color=INK))

    frags.append(rect(50, 245, 320, 80, fill="#fff3c4", stroke="#9a6700", rx=4))
    frags.append(text(210, 265, "Ініціалізація через /dev/vhost-net (ioctl):", size=10, bold=True, color="#9a6700"))
    frags.append(text(210, 283, "• VHOST_SET_OWNER / VHOST_SET_MEM_TABLE", size=10, color=INK))
    frags.append(text(210, 301, "• VHOST_SET_VRING_ADDR / KICK / CALL", size=10, color=INK))
    frags.append(text(210, 319, "• VHOST_NET_SET_BACKEND (bind TAP fd)", size=10, color=INK))

    # Data Plane (Right Side, Host Kernel)
    frags.append(rect(410, 160, 400, 330, fill="#dafbe1", stroke="#1a7f37", sw=1.5, rx=6))
    frags.append(text(610, 182, "Data Plane (Host Kernel vhost-net)", size=13, bold=True, color="#1a7f37"))

    frags.append(rect(430, 195, 360, 75, fill="#ffffff", stroke="#1a7f37", rx=4))
    frags.append(text(610, 215, "Потік ядра vhost-$PID (vhost_net_worker)", size=12, bold=True, color="#1a7f37"))
    frags.append(text(610, 235, "Очікує ioeventfd → читає vring з GPA → формує sk_buff", size=10, color=INK))
    frags.append(text(610, 253, "Викликає irqfd після обробки пакету", size=10, color=MUTED))

    # Notification Primitives
    frags.append(rect(430, 280, 170, 60, fill="#f6f8fa", stroke="#d0d7de", rx=4))
    frags.append(text(515, 300, "KVM ioeventfd", size=11, bold=True, color=POS))
    frags.append(text(515, 320, "Guest MMIO → Kernel", size=9, color=MUTED))

    frags.append(rect(620, 280, 170, 60, fill="#f6f8fa", stroke="#d0d7de", rx=4))
    frags.append(text(705, 300, "KVM irqfd", size=11, bold=True, color=NEG))
    frags.append(text(705, 320, "Kernel → Guest MSI-X", size=9, color=MUTED))

    # Host Network Devices
    frags.append(rect(430, 350, 360, 60, fill="#e6f0fa", stroke="#0969da", rx=4))
    frags.append(text(610, 372, "Драйвер TAP / macvtap (/dev/net/tun)", size=11, bold=True, color="#0969da"))
    frags.append(text(610, 392, "tun_sendmsg() / tun_recvmsg() → zero-copy skb", size=10, color=MUTED))

    frags.append(rect(430, 420, 360, 50, fill="#24292f", stroke="#1f2328", rx=4))
    frags.append(text(610, 442, "Фізичний мережевий адаптер (Physical NIC)", size=12, bold=True, color="#ffffff"))
    frags.append(text(610, 458, "Hardware DMA direct to/from Guest RAM", size=10, color="#d0d7de"))

    # Connecting arrows
    frags.append(arrow(210, 335, 210, 410, color=MUTED))
    frags.append(line(210, 410, 410, 410, color=MUTED, dash="3,3"))
    frags.append(text(310, 403, "Setup control only", size=9, color=MUTED))

    frags.append(arrow(220, 125, 515, 280, color=POS, sw=1.5))
    frags.append(arrow(705, 280, 610, 125, color=NEG, sw=1.5))

    render(os.path.join(img_dir, "vhost-net-architecture.svg"), w, h, *frags)


def fig_ring_descriptors():
    """Структура кільцевих буферів virtqueue (vring) у спільній пам'яті."""
    w, h = 840, 460
    frags = []

    frags.append(rect(15, 15, 810, 430, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    # Top: Guest Physical Memory (GPA) vs Host Virtual Memory (HVA)
    frags.append(rect(30, 40, 780, 70, fill="#e6f0fa", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(420, 62, "Трансляція адресації в vhost_memory (GPA → HVA)", size=14, bold=True, color="#0969da"))
    frags.append(text(420, 85, "Guest Physical Address (GPA) + Memory Region Offset = Host Virtual Address (HVA)", size=11, color=INK))

    # Three main blocks of vring
    # 1. Descriptor Table
    frags.append(rect(30, 130, 250, 300, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(rect(30, 130, 250, 40, fill="#ddf4ff", stroke="#54aef0", rx=6))
    frags.append(text(155, 155, "1. Descriptor Table (vring_desc)", size=12, bold=True, color="#0969da"))

    desc_items = [
        ("Desc [0]: addr=0x1000, len=1514, flags=NEXT, next=1", POS),
        ("Desc [1]: addr=0x2000, len=64,   flags=WRITE, next=0", NEG),
        ("Desc [2]: addr=0x3500, len=1024, flags=0,     next=0", MUTED),
        ("Desc [3]: addr=0x4000, len=512,  flags=NEXT, next=4", POS),
        ("...", MUTED)
    ]
    for i, (t, col) in enumerate(desc_items):
        frags.append(rect(40, 185 + i * 48, 230, 40, fill="#f6f8fa", stroke="#e1e4e8", rx=4))
        frags.append(text(155, 209 + i * 48, t, size=9, color=col, bold=True if col != MUTED else False))

    # 2. Available Ring
    frags.append(rect(295, 130, 250, 300, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(rect(295, 130, 250, 40, fill="#fff8c5", stroke="#bf8700", rx=6))
    frags.append(text(420, 155, "2. Available Ring (vring_avail)", size=12, bold=True, color="#bf8700"))

    avail_items = [
        ("flags: 0x0 (Interrupts Enabled)", INK),
        ("idx: 14 (Гість додав 14 буферів)", POS),
        ("ring[0] = Head Desc #0", POS),
        ("ring[1] = Head Desc #3", POS),
        ("ring[2..N] = Pending Descriptors", MUTED)
    ]
    for i, (t, col) in enumerate(avail_items):
        frags.append(rect(305, 185 + i * 48, 230, 40, fill="#fff8c5" if i >= 1 and i <= 3 else "#f6f8fa", stroke="#e1e4e8", rx=4))
        frags.append(text(420, 209 + i * 48, t, size=9.5, color=col, bold=True if i == 1 else False))

    # 3. Used Ring
    frags.append(rect(560, 130, 250, 300, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(rect(560, 130, 250, 40, fill="#dafbe1", stroke="#1a7f37", rx=6))
    frags.append(text(685, 155, "3. Used Ring (vring_used)", size=12, bold=True, color="#1a7f37"))

    used_items = [
        ("flags: 0x0 (No Notification)", INK),
        ("idx: 12 (vhost обробив 12 буферів)", NEG),
        ("used_elem[0]: id=0, len=1514", FIELD),
        ("used_elem[1]: id=1, len=64", FIELD),
        ("used_elem[2..N] = Completed", MUTED)
    ]
    for i, (t, col) in enumerate(used_items):
        frags.append(rect(570, 185 + i * 48, 230, 40, fill="#dafbe1" if i >= 1 and i <= 3 else "#f6f8fa", stroke="#e1e4e8", rx=4))
        frags.append(text(685, 209 + i * 48, t, size=9.5, color=col, bold=True if i == 1 else False))

    render(os.path.join(img_dir, "vhost-ring-descriptors.svg"), w, h, *frags)


def main():
    fig_context_switch()
    fig_architecture()
    fig_ring_descriptors()
    print("Generated 3 SVG figures in ./img/")


if __name__ == "__main__":
    main()
