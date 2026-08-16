import sys, os
from pathlib import Path

# Bring scripts directory into path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_vdpa_architecture():
    frags = []
    
    # Title / Background boxes
    # Guest VM box
    frags.append(rect(40, 40, 360, 220, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(220, 65, "Віртуальна машина (Guest VM)", size=15, bold=True, color="#0f172a"))
    
    tb_guest_drv, _, _ = textbox(220, 115, "Стандартний драйвер virtio-net\n(стандартний немодифікований Linux/Windows)", size=12, pad=8, fill="#e2e8f0", stroke="#64748b")
    frags.append(tb_guest_drv)
    
    tb_guest_ram, _, _ = textbox(220, 195, "Пам'ять гостя (Guest RAM)\nКільця Virtqueue (Split/Packed Vring)", size=12, pad=8, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True)
    frags.append(tb_guest_ram)
    
    # Host Userspace & Kernel box
    frags.append(rect(440, 40, 360, 220, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(620, 65, "Хост (Host System)", size=15, bold=True, color="#0f172a"))
    
    tb_qemu, _, _ = textbox(620, 115, "QEMU / VMM Process (Control Path)\n/dev/vhost-vdpa-N (ioctl interface)", size=12, pad=8, fill="#fef3c7", stroke="#d97706", color="#92400e")
    frags.append(tb_qemu)
    
    tb_kernel, _, _ = textbox(620, 195, "Ядро хоста: vDPA Bus Core\nvhost-vdpa / mgmt driver (mlx5_vdpa / ifcvf)", size=12, pad=8, fill="#e2e8f0", stroke="#64748b")
    frags.append(tb_kernel)
    
    # Hardware SmartNIC / DPU box
    frags.append(rect(140, 310, 560, 150, fill="#f1f5f9", stroke="#475569", sw=2, rx=8))
    frags.append(text(420, 335, "SmartNIC / DPU (Hardware Acceleration)", size=15, bold=True, color="#0f172a"))
    
    tb_nic_vq, _, _ = textbox(290, 395, "Hardware Virtqueue Engine\n(ASIC/FPGA Ring Offload)", size=12, pad=10, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)
    frags.append(tb_nic_vq)
    
    tb_nic_dma, _, _ = textbox(550, 395, "PCIe DMA Controller + IOMMU\nDirect GPA -> HPA Translation", size=12, pad=10, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)
    frags.append(tb_nic_dma)
    
    # Control Path arrows (Dashed orange/blue)
    frags.append(line(620, 140, 620, 170, color="#d97706", sw=2, dash="4,4"))
    frags.append(arrow(620, 220, 580, 365, color="#d97706", sw=2))
    frags.append(text(640, 290, "Control Path (ioctl setup)", size=11, color="#b45309", italic=True))
    
    # Data Path arrows (Solid green/blue)
    frags.append(arrow(220, 225, 270, 365, color="#2563eb", sw=2.5))
    frags.append(arrow(310, 365, 260, 225, color="#16a34a", sw=2.5))
    frags.append(text(150, 290, "Data Path (Direct DMA)", size=12, color="#1d4ed8", bold=True))
    
    render(os.path.join(IMG, 'vdpa-architecture.svg'), 840, 480, *frags, title="Архітектура vDPA: Розділення Data Path та Control Path")

def render_vhost_vdpa_control_flow():
    frags = []
    
    # Columns
    frags.append(text(100, 30, "QEMU (Userspace)", size=14, bold=True, color="#b45309"))
    frags.append(text(340, 30, "vhost-vdpa (/dev/vhost-vdpa-0)", size=14, bold=True, color="#1d4ed8"))
    frags.append(text(620, 30, "SmartNIC / DPU (Hardware)", size=14, bold=True, color="#15803d"))
    
    # Lifelines
    frags.append(line(100, 45, 100, 440, color="#cbd5e1", sw=1.5, dash="4,4"))
    frags.append(line(340, 45, 340, 440, color="#cbd5e1", sw=1.5, dash="4,4"))
    frags.append(line(620, 45, 620, 440, color="#cbd5e1", sw=1.5, dash="4,4"))
    
    steps = [
        (70, "1. open('/dev/vhost-vdpa-0')", 100, 340, "#b45309"),
        (130, "2. VHOST_GET_FEATURES / SET_FEATURES", 100, 340, "#b45309"),
        (190, "3. Реєстрація регіонів пам'яті (IOTLB) та ASID", 100, 340, "#b45309"),
        (250, "4. VHOST_SET_VRING_ADDR (GPA кілець vring)", 100, 340, "#b45309"),
        (310, "5. Програмування кілець та IOMMU в залізо", 340, 620, "#1d4ed8"),
        (370, "6. VHOST_VDPA_SET_STATUS (DRIVER_OK)", 100, 340, "#b45309"),
        (420, "7. Data Path: DMA між пам'яттю гостя та SmartNIC (0% CPU)", 100, 620, "#15803d")
    ]
    
    for y, label_text, x1, x2, col in steps:
        if x1 == 100 and x2 == 620:
            # Long direct arrow
            frags.append(arrow(x1, y, x2, y, color=col, sw=2.5))
            frags.append(text((x1 + x2) / 2, y - 8, label_text, size=11, bold=True, color=col))
        else:
            frags.append(arrow(x1, y, x2, y, color=col, sw=1.8))
            frags.append(text((x1 + x2) / 2, y - 8, label_text, size=11, bold=False, color="#334155"))
            
    render(os.path.join(IMG, 'vhost-vdpa-control-flow.svg'), 750, 460, *frags, title="Послідовність ініціалізації vhost-vdpa")

def render_vdpa_bus_drivers():
    frags = []
    
    # Upper drivers layer
    frags.append(rect(40, 40, 720, 90, fill="#f8fafc", stroke="#94a3b8", rx=8))
    frags.append(text(400, 60, "Верхній рівень: споживачі та керування (vDPA Upper Layer)", size=14, bold=True))
    
    tb1, _, _ = textbox(160, 95, "vhost-vdpa\n(/dev/vhost-vdpa-N -> QEMU)", size=11, pad=6, fill="#fef3c7", stroke="#d97706")
    tb2, _, _ = textbox(400, 95, "virtio-vdpa\n(Local host / Container virtio)", size=11, pad=6, fill="#dbeafe", stroke="#2563eb")
    tb3, _, _ = textbox(640, 95, "vdpa netlink\n(iproute2 / vdpa CLI)", size=11, pad=6, fill="#e2e8f0", stroke="#475569")
    frags.extend([tb1, tb2, tb3])
    
    # Bus Layer
    tb_bus, _, _ = textbox(400, 190, "Ядро Linux: Шина vDPA (vDPA Bus Core)\nstruct vdpa_device & struct vdpa_config_ops", size=13, pad=12, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)
    frags.append(tb_bus)
    
    # Lower Management Drivers
    frags.append(rect(40, 250, 720, 90, fill="#f8fafc", stroke="#94a3b8", rx=8))
    frags.append(text(400, 270, "Нижній рівень: Драйвери апаратури (vDPA Management Drivers)", size=14, bold=True))
    
    tb_m1, _, _ = textbox(160, 305, "mlx5_vdpa\n(NVIDIA ConnectX/BlueField)", size=11, pad=6, fill="#f1f5f9", stroke="#475569")
    tb_m2, _, _ = textbox(400, 305, "ifcvf\n(Intel FPGA / NIC)", size=11, pad=6, fill="#f1f5f9", stroke="#475569")
    tb_m3, _, _ = textbox(640, 305, "vdpa-sim\n(Software Kernel Simulator)", size=11, pad=6, fill="#f1f5f9", stroke="#475569")
    frags.extend([tb_m1, tb_m2, tb_m3])
    
    # Connecting arrows
    frags.append(arrow(160, 120, 320, 165, color="#94a3b8", sw=1.5))
    frags.append(arrow(400, 120, 400, 165, color="#94a3b8", sw=1.5))
    frags.append(arrow(640, 120, 480, 165, color="#94a3b8", sw=1.5))
    
    frags.append(arrow(320, 215, 160, 285, color="#94a3b8", sw=1.5))
    frags.append(arrow(400, 215, 400, 285, color="#94a3b8", sw=1.5))
    frags.append(arrow(480, 215, 640, 285, color="#94a3b8", sw=1.5))
    
    render(os.path.join(IMG, 'vdpa-bus-drivers.svg'), 800, 370, *frags, title="Шинова архітектура підсистеми vDPA в ядрі Linux")

if __name__ == "__main__":
    render_vdpa_architecture()
    render_vhost_vdpa_control_flow()
    render_vdpa_bus_drivers()
