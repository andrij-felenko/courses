# -*- coding: utf-8 -*-
import os
import sys

# Додаємо scripts до шляху імпорту (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def build_kvm_execution_modes():
    """Фігура 1: Потрійна модель режимів виконання KVM та переходи між ними."""
    w, h = 760, 420
    frags = []

    # Заголовок та шари
    frags.append(rect(15, 50, 730, 110, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(35, 72, "User Space (QEMU Process / Ring 3)", size=13, color=MUTED, bold=True, anchor="start"))
    
    frags.append(rect(15, 175, 730, 110, fill="#f1f5f9", stroke="#94a3b8", rx=8))
    frags.append(text(35, 197, "Kernel Space (Host Linux / KVM Driver / VMX Root / Ring 0)", size=13, color=MUTED, bold=True, anchor="start"))
    
    frags.append(rect(15, 300, 730, 105, fill="#eff6ff", stroke="#60a5fa", rx=8))
    frags.append(text(35, 322, "Guest Mode (VMX Non-Root Operation / Guest OS)", size=13, color=NEG, bold=True, anchor="start"))

    # Блоки режимів
    # User Mode Block
    b_user, uw, uh = textbox(200, 110, "QEMU vCPU Thread\nUser Mode (Ring 3)", size=13, fill="#ffffff", stroke="#475569", bold=True)
    frags.append(b_user)

    # Kernel Mode Block
    b_kern, kw, kh = textbox(200, 235, "KVM Driver (/dev/kvm)\nKernel Mode (Ring 0)", size=13, fill="#ffffff", stroke="#334155", bold=True)
    frags.append(b_kern)

    # Guest Mode Block (Guest Kernel + Guest User)
    b_gk, gkw, gkh = textbox(200, 355, "Guest Kernel (Ring 0)\nGuest User (Ring 3)", size=13, fill="#dbeafe", stroke="#2563eb", color=NEG, bold=True)
    frags.append(b_gk)

    # VMCS block in Kernel space
    b_vmcs, vmcsw, vmcs_h = textbox(560, 235, "VMCS / VMCB Data Structure\n• Guest State Area\n• Host State Area\n• Exit & Entry Controls", size=12, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=False)
    frags.append(b_vmcs)

    # Стрелки переходов
    # 1. ioctl(KVM_RUN)
    frags.append(arrow(180, 135, 180, 205, color=LINE, sw=2))
    frags.append(text(125, 170, "ioctl(KVM_RUN)", size=11, color=INK, bold=True))

    # 2. Return from ioctl
    frags.append(arrow(220, 205, 220, 135, color=MUTED, sw=1.8))
    frags.append(text(275, 170, "Return (KVM_EXIT)", size=11, color=MUTED, bold=False))

    # 3. VMLAUNCH / VMRESUME
    frags.append(arrow(180, 260, 180, 330, color=POS, sw=2))
    frags.append(text(120, 295, "VMLAUNCH / VMRESUME", size=11, color=POS, bold=True))

    # 4. VMEXIT
    frags.append(arrow(220, 330, 220, 260, color=NEG, sw=2))
    frags.append(text(265, 295, "VMEXIT (Hardware Trap)", size=11, color=NEG, bold=True))

    # Зв'язок KVM з VMCS
    frags.append(arrow(310, 235, 435, 235, color="#d97706", sw=1.5))
    frags.append(text(372, 222, "VMREAD / VMWRITE", size=11, color="#92400e", bold=True))

    render(os.path.join(IMG_DIR, "kvm-execution-modes.svg"), w, h, *frags)

def build_ept_address_translation():
    """Фігура 2: Двовимірна сторінкова трансляція пам'яті (EPT/NPT)."""
    w, h = 760, 380
    frags = []

    # Заголовок та концептуальні блоки
    # Left: Guest Address Space
    b_gva, _, _ = textbox(130, 80, "Guest Virtual Address\n(GVA)", size=13, fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True)
    frags.append(b_gva)

    b_gcr3, _, _ = textbox(130, 200, "Guest CR3 &\nGuest Page Tables\n(1D Paging)", size=12, fill="#f0f9ff", stroke="#38bdf8", bold=False)
    frags.append(b_gcr3)

    b_gpa, _, _ = textbox(130, 320, "Guest Physical Address\n(GPA)", size=13, fill="#dbeafe", stroke="#2563eb", color=NEG, bold=True)
    frags.append(b_gpa)

    # Center: EPT Hardware Engine in CPU
    b_ept_root, _, _ = textbox(420, 80, "EPTP (EPT Pointer in VMCS)\nPoints to Host Physical EPT PML4", size=12, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=True)
    frags.append(b_ept_root)

    b_ept_tables, _, _ = textbox(420, 200, "Intel EPT / AMD NPT Page Walk\n• EPT PML4 → EPT PDPT\n• EPT PD → EPT Page Table\n(2D Paging in MMU Hardware)", size=12, fill="#fffbeb", stroke="#f59e0b", color="#78350f", bold=False)
    frags.append(b_ept_tables)

    # Right: Host Physical Address
    b_hpa, _, _ = textbox(650, 200, "Host Physical Address\n(HPA in RAM)", size=13, fill="#dcfce7", stroke="#16a34a", color="#15803d", bold=True)
    frags.append(b_hpa)

    # Strilky
    # GVA -> Guest Page Tables -> GPA
    frags.append(arrow(130, 110, 130, 160, color="#0284c7", sw=2))
    frags.append(arrow(130, 245, 130, 290, color=NEG, sw=2))

    # GPA -> EPT Walk
    frags.append(arrow(225, 320, 320, 240, color=NEG, sw=2))
    frags.append(text(285, 295, "GPA input to EPT", size=11, color=NEG, bold=True))

    # EPTP -> EPT Walk
    frags.append(arrow(420, 115, 420, 150, color="#d97706", sw=1.8))

    # EPT Walk -> HPA
    frags.append(arrow(545, 200, 565, 200, color=FIELD, sw=2.2))
    frags.append(text(555, 185, "Direct RAM", size=11, color=FIELD, bold=True))

    # EPT Violation annotation
    frags.append(rect(310, 290, 220, 65, fill="#fef2f2", stroke="#ef4444", rx=6))
    frags.append(text(420, 310, "EPT Violation (Page Fault)", size=12, color=POS, bold=True))
    frags.append(text(420, 335, "Triggers VMExit to KVM driver", size=11, color=POS, bold=False))
    frags.append(arrow(420, 290, 420, 255, color=POS, sw=1.5))

    render(os.path.join(IMG_DIR, "ept-address-translation.svg"), w, h, *frags)

def build_vcpu_loop_architecture():
    """Фігура 3: Архітектура циклу обробки vCPU."""
    w, h = 760, 400
    frags = []

    # Sequence of steps in vCPU thread loop
    # Step 1: QEMU User space
    b1, _, _ = textbox(140, 100, "1. QEMU vCPU Thread\nCalls ioctl(vcpu_fd, KVM_RUN)", size=12, fill="#ffffff", stroke="#475569", bold=True)
    frags.append(b1)

    # Step 2: KVM Kernel space entry
    b2, _, _ = textbox(420, 100, "2. KVM Kernel Driver\nLoads VMCS Guest state,\nexecutes VMLAUNCH / VMRESUME", size=12, fill="#f1f5f9", stroke="#334155", bold=False)
    frags.append(b2)

    # Step 3: Hardware Guest Mode Execution
    b3, _, _ = textbox(640, 220, "3. Physical CPU (Guest Mode)\nExecutes instructions\nat native speed until trap", size=12, fill="#eff6ff", stroke="#3b82f6", color=NEG, bold=True)
    frags.append(b3)

    # Step 4: Hardware Trap & VMExit
    b4, _, _ = textbox(420, 320, "4. VMExit to KVM Kernel\nReads exit_reason in struct kvm_run\n(e.g., KVM_EXIT_IO, KVM_EXIT_MMIO)", size=12, fill="#fef2f2", stroke="#f87171", color=POS, bold=True)
    frags.append(b4)

    # Decision Box: Kernel handle or Userspace return
    b5, _, _ = textbox(140, 320, "5. Exit Handling Decision\n• In-kernel (timer/vAPIC) → re-enter 2\n• Userspace I/O → return to QEMU 1", size=12, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=False)
    frags.append(b5)

    # Connections
    # 1 -> 2
    frags.append(arrow(245, 100, 315, 100, color=LINE, sw=2))

    # 2 -> 3
    frags.append(arrow(520, 100, 640, 160, color=NEG, sw=2))

    # 3 -> 4
    frags.append(arrow(640, 275, 530, 320, color=POS, sw=2))

    # 4 -> 5
    frags.append(arrow(310, 320, 245, 320, color=LINE, sw=2))

    # 5 -> 1 (Userspace return)
    frags.append(arrow(140, 260, 140, 155, color="#d97706", sw=2))
    frags.append(text(75, 210, "Return to QEMU\n(I/O Emulation)", size=11, color="#92400e", bold=True))

    # 5 -> 2 Fast loop (Kernel handled)
    frags.append(arrow(210, 280, 350, 150, color=FIELD, sw=2))
    frags.append(text(315, 230, "Fast Path\n(Kernel Handled)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "vcpu-loop-architecture.svg"), w, h, *frags)

if __name__ == "__main__":
    build_kvm_execution_modes()
    build_ept_address_translation()
    build_vcpu_loop_architecture()
    print("Figures generated successfully.")
