import os
import sys

# Add scripts folder to sys.path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

def generate_vfio_architecture():
    w, h = 850, 480
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    elements.append(text(w/2, 25, "Архітектура VFIO та трансляція IOMMU в Linux", size=18, bold=True))
    
    # Layer 1: Userspace (Y: 50 to 170)
    elements.append(rect(30, 50, w - 60, 120, fill="#e8f4f8", stroke="#2980b9", sw=1.5, rx=8))
    elements.append(text(w/2, 72, "Простір користувача (Userspace)", size=13, bold=True, color="#1b4f72", anchor="middle"))
    
    box_qemu, _, _ = textbox(210, 120, "QEMU / KVM Гіпервізор\n(Guest RAM & Virt devices)", size=12, pad=10, fill="#ffffff", stroke="#2980b9")
    box_dpdk, _, _ = textbox(630, 120, "Користувацький драйвер\n(DPDK / SPDK / custom app)", size=12, pad=10, fill="#ffffff", stroke="#2980b9")
    elements.append(box_qemu)
    elements.append(box_dpdk)
    
    elements.append(line(30, 190, w - 30, 190, color=MUTED, sw=1.2, dash="4,4"))
    elements.append(text(w/2, 185, "Символьні пристрої /dev/vfio/vfio та /dev/vfio/<group_id>", size=11, italic=True, color=MUTED))
    
    # Layer 2: Kernel Space (Y: 200 to 335)
    elements.append(rect(30, 200, w - 60, 135, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    elements.append(text(w/2, 222, "Ядро Linux (Kernel Space)", size=13, bold=True, color="#145a32", anchor="middle"))
    
    box_vfio_core, _, _ = textbox(170, 275, "VFIO Core\n(/dev/vfio/vfio)", size=12, pad=10, fill="#ffffff", stroke="#27ae60")
    box_vfio_pci, _, _ = textbox(425, 275, "vfio-pci / vfio-platform\n(Bus Driver)", size=12, pad=10, fill="#ffffff", stroke="#27ae60")
    box_vfio_iommu, _, _ = textbox(680, 275, "vfio_iommu_type1\n(IOMMU Backend)", size=12, pad=10, fill="#ffffff", stroke="#27ae60")
    elements.append(box_vfio_core)
    elements.append(box_vfio_pci)
    elements.append(box_vfio_iommu)
    
    # Layer 3: Hardware (Y: 355 to 465)
    elements.append(rect(30, 355, w - 60, 110, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    elements.append(text(w/2, 376, "Апаратне забезпечення (Hardware)", size=13, bold=True, color="#7e5109", anchor="middle"))
    
    box_dev, _, _ = textbox(210, 420, "PCIe Пристрій\n(GPU / NVMe / NIC)", size=12, pad=10, fill="#ffffff", stroke="#f39c12")
    box_rc, _, _ = textbox(425, 420, "PCIe Root Complex\n& Interrupt Controller", size=12, pad=10, fill="#ffffff", stroke="#f39c12")
    box_hw_iommu, _, _ = textbox(650, 420, "IOMMU\n(Intel VT-d / AMD-Vi)", size=12, pad=10, fill="#ffffff", stroke="#f39c12")
    elements.append(box_dev)
    elements.append(box_rc)
    elements.append(box_hw_iommu)
    
    elements.append(arrow(210, 150, 170, 245, color=LINE, sw=1.5))
    elements.append(arrow(630, 150, 680, 245, color=LINE, sw=1.5))
    elements.append(arrow(425, 308, 210, 390, color=LINE, sw=1.5))
    elements.append(arrow(680, 308, 650, 390, color=LINE, sw=1.5))
    
    body = "".join(elements)
    
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(os.path.join(IMG_DIR, "vfio-architecture.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n'
                f'<defs>\n'
                f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
                f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
                f'  </marker>\n'
                f'</defs>\n'
                f'{body}\n</svg>')

def generate_iommu_group_topology():
    w, h = 880, 460
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    elements.append(text(w/2, 25, "Топологія PCIe шини, підтримка ACS та IOMMU-групи", size=18, bold=True))
    
    box_rc, _, _ = textbox(w/2, 75, "PCIe Root Complex (з апаратним IOMMU)", size=13, pad=12, fill="#e8f4f8", stroke="#2980b9", bold=True)
    elements.append(box_rc)
    
    # Left Branch: Without ACS
    elements.append(rect(40, 130, 380, 310, fill="#fdf2e9", stroke="#e67e22", sw=1.5, rx=8))
    elements.append(text(230, 150, "Без ACS (P2P DMA без фільтрації)", size=12, bold=True, color="#a04000"))
    
    box_sw1, _, _ = textbox(230, 210, "PCIe Switch (Без ACS)\nP2P йде вминай IOMMU", size=12, pad=10, fill="#ffffff", stroke="#e67e22")
    elements.append(box_sw1)
    
    box_devA, _, _ = textbox(130, 310, "Пристрій A\n(GPU)", size=12, pad=8, fill="#ffffff", stroke="#d35400")
    box_devB, _, _ = textbox(330, 310, "Пристрій B\n(Audio / NIC)", size=12, pad=8, fill="#ffffff", stroke="#d35400")
    elements.append(box_devA)
    elements.append(box_devB)
    
    box_grp1, _, _ = textbox(230, 400, "Спільна IOMMU Group #1\n(Пристрої A та B неподільні)", size=12, pad=10, fill="#fadbd8", stroke="#c0392b", bold=True)
    elements.append(box_grp1)
    
    elements.append(arrow(340, 105, 250, 180, color=LINE, sw=1.5))
    elements.append(line(230, 240, 130, 285, color=LINE, sw=1.5))
    elements.append(line(230, 240, 330, 285, color=LINE, sw=1.5))
    
    elements.append(line(170, 310, 280, 310, color=POS, sw=2, dash="3,3"))
    elements.append(text(225, 298, "P2P DMA", size=10, color=POS, bold=True))

    # Right Branch: With ACS
    elements.append(rect(460, 130, 380, 310, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    elements.append(text(650, 150, "З ACS (Access Control Services)", size=12, bold=True, color="#145a32"))
    
    box_sw2, _, _ = textbox(650, 210, "PCIe Switch (З увімкненим ACS)\nP2P примусово йде в Root Complex", size=12, pad=10, fill="#ffffff", stroke="#27ae60")
    elements.append(box_sw2)
    
    box_devC, _, _ = textbox(550, 310, "Пристрій C\n(NVMe SSD)", size=12, pad=8, fill="#ffffff", stroke="#1e8449")
    box_devD, _, _ = textbox(750, 310, "Пристрій D\n(10GbE NIC)", size=12, pad=8, fill="#ffffff", stroke="#1e8449")
    elements.append(box_devC)
    elements.append(box_devD)
    
    box_grpC, _, _ = textbox(550, 400, "IOMMU Group #2\n(Ізольований C)", size=11, pad=8, fill="#d4efdf", stroke="#27ae60", bold=True)
    box_grpD, _, _ = textbox(750, 400, "IOMMU Group #3\n(Ізольований D)", size=11, pad=8, fill="#d4efdf", stroke="#27ae60", bold=True)
    elements.append(box_grpC)
    elements.append(box_grpD)
    
    elements.append(arrow(540, 105, 630, 180, color=LINE, sw=1.5))
    elements.append(line(650, 240, 550, 285, color=LINE, sw=1.5))
    elements.append(line(650, 240, 750, 285, color=LINE, sw=1.5))
    
    body = "".join(elements)
    
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(os.path.join(IMG_DIR, "iommu-group-topology.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n'
                f'<defs>\n'
                f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
                f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
                f'  </marker>\n'
                f'</defs>\n'
                f'{body}\n</svg>')

def render():
    generate_vfio_architecture()
    generate_iommu_group_topology()

if __name__ == "__main__":
    render()
