import os
import sys

# Add scripts folder to sys.path (4 levels up from topic dir: reference/unix-linux/devices/kvm-irq-virtualization-apicv)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def generate_apic_evolution():
    w, h = 940, 530
    frags = []
    
    # 4 Columns representing the 4 stages of virtualization evolution
    cols = [
        ("1. Userspace QEMU", "#c0392b", "#fdecea", 135),
        ("2. In-Kernel irqchip", "#d35400", "#fef5e7", 360),
        ("3. Intel APICv / AVIC", "#2980b9", "#ebf5fb", 585),
        ("4. Posted Interrupts", "#27ae60", "#eafaf1", 810)
    ]
    
    for title, stroke_col, fill_col, cx in cols:
        col_w = 205
        x = cx - col_w / 2
        # Column background card
        frags.append(rect(x, 45, col_w, 465, fill=fill_col, stroke=stroke_col, sw=1.5, rx=8))
        frags.append(text(cx, 68, title, size=12, bold=True, color=stroke_col, anchor="middle"))

    # Horizontal dividing guides
    frags.append(line(25, 155, w - 25, 155, color="#cbd5e1", sw=1.0, dash="4,4"))
    frags.append(line(25, 275, w - 25, 275, color="#cbd5e1", sw=1.0, dash="4,4"))
    frags.append(line(25, 395, w - 25, 395, color="#cbd5e1", sw=1.0, dash="4,4"))

    # Column 1: Userspace QEMU Emulation
    b1_guest, _, _ = textbox(135, 105, "vCPU: запис TPR / EOI\n(MMIO 0xFEE00000)", size=10, pad=6, fill="#ffffff", stroke="#c0392b")
    b1_kvm, _, _ = textbox(135, 210, "KVM: VM-Exit (MMIO)\nВихід у простір хоста", size=10, pad=6, fill="#ffffff", stroke="#c0392b")
    b1_qemu, _, _ = textbox(135, 335, "QEMU (Userspace):\nЕмуляція APIC/PIC\nioctl(KVM_INTERRUPT)", size=10, pad=6, fill="#ffffff", stroke="#c0392b")
    b1_metric, _, _ = textbox(135, 460, "Затримка: 2500–5000 нс\nОверхед: критичний\n(2 context switch)", size=10, pad=6, fill="#ffffff", stroke="#c0392b", bold=True)
    frags.extend([b1_guest, b1_kvm, b1_qemu, b1_metric])
    frags.append(arrow(135, 128, 135, 185, color="#c0392b", sw=1.5))
    frags.append(arrow(135, 235, 135, 308, color="#c0392b", sw=1.5))
    frags.append(arrow(135, 362, 135, 435, color="#c0392b", sw=1.5))

    # Column 2: In-Kernel IRQChip
    b2_guest, _, _ = textbox(360, 105, "vCPU: запис TPR / EOI\n(MMIO 0xFEE00000)", size=10, pad=6, fill="#ffffff", stroke="#d35400")
    b2_kvm, _, _ = textbox(360, 215, "KVM in-kernel irqchip:\nОбробка в kvm.ko\nБез виходу в QEMU", size=10, pad=6, fill="#ffffff", stroke="#d35400")
    b2_qemu, _, _ = textbox(360, 335, "IRQFD / eventfd:\nПрямий шлях для vhost\nі емульованих ліній", size=10, pad=6, fill="#ffffff", stroke="#d35400")
    b2_metric, _, _ = textbox(360, 460, "Затримка: 800–1500 нс\nОверхед: високий\n(VM-Exit на кожен EOI)", size=10, pad=6, fill="#ffffff", stroke="#d35400", bold=True)
    frags.extend([b2_guest, b2_kvm, b2_qemu, b2_metric])
    frags.append(arrow(360, 128, 360, 190, color="#d35400", sw=1.5))
    frags.append(arrow(360, 245, 360, 308, color="#d35400", sw=1.5))
    frags.append(arrow(360, 362, 360, 435, color="#d35400", sw=1.5))

    # Column 3: Intel APICv / AMD AVIC
    b3_guest, _, _ = textbox(585, 105, "vCPU: запис TPR / EOI\n(Апаратний доступ)", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    b3_hw, _, _ = textbox(585, 215, "APICv / Virtual-APIC Page:\nЗапис у пам'ять vTPR/vEOI\nАвтоматична оцінка RVI/PPR", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    b3_kvm, _, _ = textbox(585, 335, "KVM: втручання лише\nдля APIC-Write Exit\n(ICR IPI / broadcast)", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    b3_metric, _, _ = textbox(585, 460, "Затримка: 50–150 нс\n0 VM-Exit на TPR/EOI\nШвидкість bare-metal", size=10, pad=6, fill="#ffffff", stroke="#2980b9", bold=True)
    frags.extend([b3_guest, b3_hw, b3_kvm, b3_metric])
    frags.append(arrow(585, 128, 585, 190, color="#2980b9", sw=1.5))
    frags.append(arrow(585, 245, 585, 308, color="#2980b9", sw=1.5))
    frags.append(arrow(585, 362, 585, 435, color="#2980b9", sw=1.5))

    # Column 4: Posted Interrupts
    b4_guest, _, _ = textbox(810, 105, "vCPU виконує код гостя\n(Безпечне виконання)", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    b4_cpu, _, _ = textbox(810, 215, "VMX CPU Non-Root:\nАвто-синхронізація PIR→vIRR\nДоставка в гостьовий IDT", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    b4_iommu, _, _ = textbox(810, 335, "VT-d IOMMU + PCIe MSI-X:\nАтомарний запис PIR\n+ Physical IPI (0xf2)", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    b4_metric, _, _ = textbox(810, 460, "Затримка: < 100 нс\n0 VM-Exit на весь шлях!\n100% апаратна лінія", size=10, pad=6, fill="#ffffff", stroke="#27ae60", bold=True)
    frags.extend([b4_guest, b4_cpu, b4_iommu, b4_metric])
    frags.append(arrow(810, 308, 810, 245, color="#27ae60", sw=1.5))
    frags.append(arrow(810, 190, 810, 128, color="#27ae60", sw=1.5))
    frags.append(arrow(810, 362, 810, 435, color="#27ae60", sw=1.5))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, "apic-virtualization-evolution.svg"), w, h, *frags, title="Еволюція доставки переривань у KVM: від емуляції до прямого обладнання")


def generate_apicv_vmcs_structures():
    w, h = 920, 480
    frags = []

    # Left: VMCS Controls
    frags.append(rect(30, 50, 265, 405, fill="#f4f6f8", stroke="#34495e", sw=1.5, rx=8))
    frags.append(text(162, 75, "VMCS Execution Controls", size=13, bold=True, color="#2c3e50", anchor="middle"))
    
    c1, _, _ = textbox(162, 125, "Pin-Based Controls:\n• Process Posted Interrupts (bit 14)", size=10, pad=6, fill="#ffffff", stroke="#34495e")
    c2, _, _ = textbox(162, 195, "Primary Exec Controls:\n• Use TPR shadow (bit 21)\n• TPR threshold register", size=10, pad=6, fill="#ffffff", stroke="#34495e")
    c3, _, _ = textbox(162, 290, "Secondary Exec Controls:\n• Virtualize APIC-accesses (bit 0)\n• Virtual-interrupt delivery (bit 9)\n• APIC-register virtualization (bit 8)\n• Virtualize x2APIC mode (bit 18)", size=10, pad=6, fill="#ffffff", stroke="#34495e")
    c4, _, _ = textbox(162, 398, "Guest Interrupt Status:\n• RVI: Requesting Virtual Vector\n• SVI: Servicing Virtual Vector", size=10, pad=6, fill="#ffffff", stroke="#34495e")
    frags.extend([c1, c2, c3, c4])

    # Middle: Pointers & APIC-access Page
    frags.append(rect(325, 50, 265, 405, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=8))
    frags.append(text(457, 75, "APIC-Access & Вказівники", size=13, bold=True, color="#1b4f72", anchor="middle"))

    p1, _, _ = textbox(457, 130, "APIC-Access Address (HPA):\nВказує на 4 КБ сторінку хоста,\nщо мапується на GPA 0xFEE00000", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    p2, _, _ = textbox(457, 230, "Virtual-APIC Address (HPA):\nФізична сторінка хоста\nз регістрами Virtual APIC", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    p3, _, _ = textbox(457, 335, "Posted-Interrupt Desc Addr:\nВказівник HPA на 64-байтний\nдескриптор PIR у пам'яті", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    frags.extend([p1, p2, p3])

    # Right: Physical Backing Memory Pages
    frags.append(rect(620, 50, 270, 405, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(755, 75, "Фізичні структури в RAM", size=13, bold=True, color="#145a32", anchor="middle"))

    m1, _, _ = textbox(755, 140, "Virtual-APIC Page (4 KB):\n• 0x080: Virtual TPR (vTPR)\n• 0x0B0: Virtual EOI (vEOI)\n• 0x100-0x170: Virtual ISR (vISR)\n• 0x200-0x270: Virtual IRR (vIRR)", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    m2, _, _ = textbox(755, 320, "Posted-Interrupt Descriptor (64 B):\n• PIR[255:0]: 256-бітний бітмап\n• Bit 256: ON (Outstanding Notif)\n• Bit 257: SN (Suppress Notif)\n• Bits 271:264: NV (Notif Vector)\n• Bits 319:288: NDST (Host CPU APIC ID)", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    frags.extend([m1, m2])

    # Connecting arrows
    frags.append(arrow(295, 290, 345, 130, color="#2980b9", sw=1.5))
    frags.append(arrow(295, 290, 345, 230, color="#2980b9", sw=1.5))
    frags.append(arrow(295, 125, 345, 335, color="#2980b9", sw=1.5))
    frags.append(arrow(570, 230, 635, 140, color="#27ae60", sw=1.5))
    frags.append(arrow(570, 335, 635, 320, color="#27ae60", sw=1.5))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, "apicv-vmcs-structures.svg"), w, h, *frags, title="Апаратні структури керування APICv у VMCS та пам'яті хоста")


def generate_posted_interrupt_flow():
    w, h = 940, 520
    frags = []

    # Step 1: PCIe Device
    b1, w1, _ = textbox(130, 115, "1. PCIe Пристрій (VFIO)\nГенерує MSI-X транзакцію:\nAddr = 0xFEE00000 | Data = Vector", size=10, pad=8, fill="#fef9e7", stroke="#f39c12")
    
    # Step 2: VT-d IOMMU
    b2, w2, _ = textbox(470, 115, "2. Intel VT-d IOMMU\nПошук в IRTE (Posted Format):\nВитягує HPA PIR, NV=0xf2, NDST", size=10, pad=8, fill="#ebf5fb", stroke="#2980b9")
    
    # Step 3: Atomic Memory Write to PIR
    b3, w3, _ = textbox(810, 115, "3. Атомарний запис у RAM\nIOMMU ставить біт у PIR[vector]\nта встановлює ON = 1 (Lock Cmpxchg)", size=10, pad=8, fill="#eafaf1", stroke="#27ae60")
    
    # Step 4: Physical IPI
    b4, w4, _ = textbox(810, 275, "4. Апаратний Physical IPI\nIOMMU відправляє IPI (Vector 0xf2)\nна фізичний APIC хоста (NDST)", size=10, pad=8, fill="#eafaf1", stroke="#27ae60")

    # Step 5: CPU VMX Non-Root Sync
    b5, w5, _ = textbox(470, 275, "5. Апаратне перехоплення ЦП\nФізичний CPU у режимі гостя:\nПереносить PIR[255:0] → vIRR\nСкидає ON = 0 (0 VM-Exit!)", size=10, pad=8, fill="#ebf5fb", stroke="#2980b9")

    # Step 6: Guest IDT Delivery
    b6, w6, _ = textbox(130, 275, "6. Виконання в гостьовій ОС\nЦП порівнює RVI > PPR\nта викликає гостьовий IDT handler\nіз затримкою < 100 нс", size=10, pad=8, fill="#fdecea", stroke="#c0392b")

    # Fallback branch for sleeping vCPU
    b_sleep, _, _ = textbox(470, 440, "Альтернативна гілка: vCPU спить / заблокований (HLT)\nKVM виставляє NV = 0xf1 (Wakeup Vector) → Host CPU приймає IPI →\nВикликає pi_wakeup_handler() → Пробуджує потік vCPU в планувальнику CFS", size=10, pad=8, fill="#f4f6f8", stroke="#7f8c8d")

    frags.extend([b1, b2, b3, b4, b5, b6, b_sleep])

    # Forward arrows for active vCPU (calculating box edges accurately)
    frags.append(arrow(130 + w1/2 + 5, 115, 470 - w2/2 - 5, 115, color=LINE, sw=1.6))
    frags.append(arrow(470 + w2/2 + 5, 115, 810 - w3/2 - 5, 115, color=LINE, sw=1.6))
    frags.append(arrow(810, 160, 810, 230, color=LINE, sw=1.6))
    frags.append(arrow(810 - w4/2 - 5, 275, 470 + w5/2 + 5, 275, color=LINE, sw=1.6))
    frags.append(arrow(470 - w5/2 - 5, 275, 130 + w6/2 + 5, 275, color=LINE, sw=1.6))

    # Downward dashed route to sleeping branch around box 5: (310, 150) -> (310, 400)
    frags.append(line(350, 115, 300, 115, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(300, 115, 300, 400, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(arrow(300, 400, 300, 415, color=MUTED, sw=1.2))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, "posted-interrupt-hardware-flow.svg"), w, h, *frags, title="Апаратний конвеєр прямої доставки переривань VT-d Posted Interrupts")


if __name__ == "__main__":
    generate_apic_evolution()
    generate_apicv_vmcs_structures()
    generate_posted_interrupt_flow()
    print("All figures successfully generated in img/")
