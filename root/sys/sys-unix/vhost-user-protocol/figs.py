import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "scripts"))
sys.path.insert(0, scripts_dir)

try:
    from svgkit import render, rect, text, arrow, line, mtext, textbox
except ImportError as e:
    print(f"Could not import svgkit from {scripts_dir}. Error: {e}")
    sys.exit(1)

def draw_vhost_user_architecture():
    frags = []

    # 1. Guest VM container (left top: x=30, y=30, w=250, h=250)
    frags.append(rect(30, 30, 250, 250, rx=8, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(155, 56, "Гостьова віртуальна машина (VM)", size=13, bold=True, anchor="middle", color="#0f172a"))
    
    frags.append(rect(45, 75, 220, 50, rx=5, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    frags.append(mtext(155, 95, ["Гостьовий застосунок", "Користувацький простір VM"], size=11, anchor="middle", color="#1e293b"))
    
    frags.append(rect(45, 140, 220, 125, rx=5, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(155, 160, "Гостьове ядро (Linux)", size=12, bold=True, anchor="middle", color="#0369a1"))
    frags.append(rect(55, 175, 200, 34, rx=4, fill="#ffffff", stroke="#0284c7", sw=1))
    frags.append(text(155, 197, "Драйвер virtio-net / virtio-blk", size=11, bold=True, anchor="middle", color="#0284c7"))
    frags.append(rect(55, 220, 200, 34, rx=4, fill="#bae6fd", stroke="#0284c7", sw=1))
    frags.append(text(155, 242, "Кільця virtqueue (vring)", size=11, anchor="middle", color="#0369a1"))

    # 2. Host Kernel / KVM (middle top: x=310, y=30, w=220, h=130)
    frags.append(rect(310, 30, 220, 130, rx=8, fill="#fef2f2", stroke="#ef4444", sw=1.5))
    frags.append(text(420, 56, "Ядро хоста / Модуль KVM", size=13, bold=True, anchor="middle", color="#991b1b"))
    frags.append(rect(325, 75, 190, 70, rx=5, fill="#fee2e2", stroke="#f87171", sw=1))
    frags.append(mtext(420, 100, ["Перехоплення MMIO / PIO", "ioeventfd (kick)", "irqfd (call / vIRQ)"], size=11, anchor="middle", color="#7f1d1d"))

    # 3. QEMU Process (Control Plane, right top: x=560, y=30, w=270, h=250)
    frags.append(rect(560, 30, 270, 250, rx=8, fill="#fefce8", stroke="#eab308", sw=1.5))
    frags.append(text(695, 56, "Процес QEMU / VMM (Master)", size=13, bold=True, anchor="middle", color="#713f12"))
    frags.append(rect(575, 75, 240, 50, rx=5, fill="#fef9c3", stroke="#facc15", sw=1))
    frags.append(mtext(695, 95, ["Control Plane: PCI конфігурація,", "узгодження Virtio Features"], size=11, anchor="middle", color="#854d0e"))
    frags.append(rect(575, 135, 240, 50, rx=5, fill="#ffffff", stroke="#ca8a04", sw=1))
    frags.append(mtext(695, 155, ["Виділення RAM (memfd/HugeTLB)", "ініціалізація vhost-user сокета"], size=11, anchor="middle", color="#713f12"))
    frags.append(rect(575, 195, 240, 70, rx=5, fill="#fef08a", stroke="#ca8a04", sw=1))
    frags.append(mtext(695, 220, ["Передача дескрипторів пам'яті", "та сигнальних fd (SCM_RIGHTS)"], size=11, bold=True, anchor="middle", color="#713f12"))

    # 4. Shared Memory Buffer (middle: x=140, y=315, w=400, h=100)
    frags.append(rect(140, 315, 400, 100, rx=8, fill="#f0fdf4", stroke="#16a34a", sw=2))
    frags.append(text(340, 340, "Розділювана пам'ять: memfd / hugetlbfs (Shared RAM)", size=12, bold=True, anchor="middle", color="#14532d"))
    frags.append(rect(155, 355, 175, 48, rx=4, fill="#dcfce7", stroke="#22c55e", sw=1))
    frags.append(mtext(242, 375, ["Дескриптори virtio", "кільця Avail / Used"], size=11, anchor="middle", color="#166534"))
    frags.append(rect(345, 355, 180, 48, rx=4, fill="#dcfce7", stroke="#22c55e", sw=1))
    frags.append(mtext(435, 375, ["Буфери даних", "(пакети / блоки)"], size=11, anchor="middle", color="#166534"))

    # 5. Unix Domain Socket box (right middle: x=580, y=315, w=250, h=100)
    frags.append(rect(580, 315, 250, 100, rx=8, fill="#fffbeb", stroke="#f59e0b", sw=2))
    frags.append(text(705, 340, "UNIX Domain Socket", size=12, bold=True, anchor="middle", color="#b45309"))
    frags.append(mtext(705, 370, ["vhost-user protocol messages", "Передача дескрипторів SCM_RIGHTS"], size=11, anchor="middle", color="#92400e"))

    # 6. External Backend Process (bottom wide: x=30, y=450, w=800, h=180)
    frags.append(rect(30, 450, 800, 180, rx=8, fill="#f3e8ff", stroke="#9333ea", sw=2))
    frags.append(text(430, 476, "Зовнішній сервер у просторі користувача: Slave / Backend (OVS-DPDK / SPDK / virtiofsd)", size=13, bold=True, anchor="middle", color="#581c87"))
    
    frags.append(rect(50, 495, 230, 115, rx=5, fill="#ffffff", stroke="#a855f7", sw=1))
    frags.append(text(165, 520, "Обробник сокета vhost-user", size=12, bold=True, anchor="middle", color="#6b21a8"))
    frags.append(mtext(165, 545, ["Прийом керуючих команд", "Отримання fd через SCM_RIGHTS", "mmap() розділюваної пам'яті"], size=11, anchor="middle", color="#3b0764"))

    frags.append(rect(300, 495, 255, 115, rx=5, fill="#ede9fe", stroke="#a855f7", sw=1.5))
    frags.append(text(427, 520, "Data Plane Worker (PMD)", size=12, bold=True, anchor="middle", color="#6b21a8"))
    frags.append(mtext(427, 545, ["Прямий доступ до vring у RAM", "Опитування кілець без syscall", "Zero-copy обробка дескрипторів"], size=11, bold=True, anchor="middle", color="#4c1d95"))

    frags.append(rect(575, 495, 235, 115, rx=5, fill="#ffffff", stroke="#a855f7", sw=1))
    frags.append(text(692, 520, "Цільовий рушій I/O", size=12, bold=True, anchor="middle", color="#6b21a8"))
    frags.append(mtext(692, 545, ["Мережевий комутатор (OVS/DPDK)", "Контролер NVMe (SPDK bdev)", "Файловий демон (virtiofsd)"], size=11, anchor="middle", color="#3b0764"))

    # Arrows
    # VM to KVM MMIO kick
    frags.append(arrow(245, 145, 310, 95, color="#dc2626", sw=1.8))
    # KVM to VM irqfd call
    frags.append(arrow(310, 120, 245, 165, color="#2563eb", sw=1.8))

    # QEMU to Socket and Socket to Backend
    frags.append(arrow(705, 280, 705, 315, color="#d97706", sw=2))
    frags.append(arrow(705, 415, 705, 450, color="#d97706", sw=2))

    # Shared memory mapping arrows
    frags.append(arrow(155, 280, 210, 315, color="#16a34a", sw=2))
    frags.append(arrow(427, 450, 427, 415, color="#16a34a", sw=2))

    # Direct eventfd arrow between KVM and Backend
    frags.append(arrow(380, 160, 165, 450, color="#9333ea", sw=1.8))

    return frags

def draw_memory_mapping_translation():
    frags = []

    # Title Banner
    frags.append(text(400, 30, "Трансляція адрес: від Guest Physical Address до Backend HVA", size=15, bold=True, anchor="middle", color="#0f172a"))

    # Three layers:
    # 1. Guest Address Space (GPA)
    frags.append(rect(40, 60, 220, 380, rx=8, fill="#eff6ff", stroke="#3b82f6", sw=1.5))
    frags.append(text(150, 85, "Гостьовий простір (VM)", size=13, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(text(150, 105, "Guest Physical Address (GPA)", size=11, italic=True, anchor="middle", color="#1e40af"))
    
    frags.append(rect(55, 120, 190, 50, rx=4, fill="#ffffff", stroke="#93c5fd", sw=1))
    frags.append(mtext(150, 140, ["RAM Регіон 0 (Low Mem)", "GPA: 0x0000_0000 - 0x7FFF_FFFF"], size=10, anchor="middle", color="#1e3a8a"))
    
    frags.append(rect(55, 185, 190, 40, rx=4, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    frags.append(text(150, 210, "PCI / MMIO Hole (немає RAM)", size=10, anchor="middle", color="#475569"))
    
    frags.append(rect(55, 240, 190, 85, rx=4, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(mtext(150, 260, ["RAM Регіон 1 (High Mem)", "GPA: 0x1_0000_0000...", "Дескриптор virtio: GPA = X"], size=10, bold=True, anchor="middle", color="#1e40af"))
    frags.append(rect(65, 290, 170, 25, rx=3, fill="#bfdbfe", stroke="#1d4ed8", sw=1))
    frags.append(text(150, 307, "Буфер пакета: GPA = X", size=10, bold=True, anchor="middle", color="#1e3a8a"))

    frags.append(rect(55, 340, 190, 80, rx=4, fill="#ffffff", stroke="#93c5fd", sw=1))
    frags.append(mtext(150, 365, ["RAM Регіон 2", "GPA: 0x2_0000_0000..."], size=10, anchor="middle", color="#1e3a8a"))

    # 2. File / Shared Memory Backing
    frags.append(rect(290, 60, 220, 380, rx=8, fill="#f0fdf4", stroke="#22c55e", sw=1.5))
    frags.append(text(400, 85, "Розділюваний файл (Хост)", size=13, bold=True, anchor="middle", color="#15803d"))
    frags.append(text(400, 105, "memfd_create() / hugetlbfs fd", size=11, italic=True, anchor="middle", color="#166534"))
    
    frags.append(rect(305, 120, 190, 60, rx=4, fill="#ffffff", stroke="#86efac", sw=1))
    frags.append(mtext(400, 142, ["Файловий дескриптор: fd_0", "Зміщення у файлі: offset = 0", "Розмір: size_0"], size=10, anchor="middle", color="#14532d"))
    
    frags.append(rect(305, 210, 190, 120, rx=4, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(mtext(400, 235, ["Файловий дескриптор: fd_1", "mmap_offset = 0", "Розмір = size_1"], size=10, bold=True, anchor="middle", color="#14532d"))
    frags.append(rect(315, 275, 170, 40, rx=3, fill="#bbf7d0", stroke="#15803d", sw=1))
    frags.append(mtext(400, 292, ["Дані буфера за зміщенням:", "File_Offset = GPA - Base_GPA"], size=10, bold=True, anchor="middle", color="#14532d"))

    frags.append(rect(305, 350, 190, 70, rx=4, fill="#ffffff", stroke="#86efac", sw=1))
    frags.append(mtext(400, 375, ["Файловий дескриптор: fd_2", "mmap_offset = 0"], size=10, anchor="middle", color="#14532d"))

    # 3. Backend Host Virtual Address Space (Backend HVA)
    frags.append(rect(540, 60, 220, 380, rx=8, fill="#faf5ff", stroke="#a855f7", sw=1.5))
    frags.append(text(650, 85, "Простір бекенда (Backend)", size=13, bold=True, anchor="middle", color="#7e22ce"))
    frags.append(text(650, 105, "Backend Host Virtual Addr (HVA)", size=11, italic=True, anchor="middle", color="#6b21a8"))

    frags.append(rect(555, 120, 190, 60, rx=4, fill="#ffffff", stroke="#d8b4fe", sw=1))
    frags.append(mtext(650, 142, ["mmap(fd_0) -> HVA_Base_0", "Відображення Регіону 0"], size=10, anchor="middle", color="#581c87"))

    frags.append(rect(555, 210, 190, 120, rx=4, fill="#f3e8ff", stroke="#9333ea", sw=1.5))
    frags.append(mtext(650, 235, ["mmap(fd_1) -> HVA_Base_1", "Відображення Регіону 1"], size=10, bold=True, anchor="middle", color="#581c87"))
    frags.append(rect(565, 275, 170, 40, rx=3, fill="#e9d5ff", stroke="#7e22ce", sw=1))
    frags.append(mtext(650, 292, ["Покажчик у бекенді:", "HVA = HVA_Base_1 + (GPA - GPA_1)"], size=9, bold=True, anchor="middle", color="#4c1d95"))

    frags.append(rect(555, 350, 190, 70, rx=4, fill="#ffffff", stroke="#d8b4fe", sw=1))
    frags.append(mtext(650, 375, ["mmap(fd_2) -> HVA_Base_2", "Відображення Регіону 2"], size=10, anchor="middle", color="#581c87"))

    # Mapping arrows across layers
    frags.append(arrow(245, 280, 305, 280, color="#16a34a", sw=2))
    frags.append(arrow(495, 280, 555, 280, color="#9333ea", sw=2))

    # Bottom mathematical formula box
    tb_form, _, _ = textbox(400, 470, "Формула адресації: Backend_HVA = mmap_addr + (GPA - guest_phys_addr) + mmap_offset", size=12, pad=8, fill="#ffffff", stroke="#334155", bold=True)
    frags.append(tb_form)

    return frags

def draw_handshake_lifecycle():
    frags = []

    # Title
    frags.append(text(400, 30, "Послідовність рукостискання протоколу vhost-user (QEMU <-> Backend)", size=14, bold=True, anchor="middle", color="#0f172a"))

    # Timelines / Process columns
    frags.append(rect(90, 50, 200, 40, rx=6, fill="#fef9c3", stroke="#ca8a04", sw=1.5))
    frags.append(text(190, 75, "QEMU / VMM (Master)", size=13, bold=True, anchor="middle", color="#713f12"))
    frags.append(line(190, 90, 190, 580, color="#94a3b8", sw=1.5, dash="4,4"))

    frags.append(rect(510, 50, 200, 40, rx=6, fill="#ede9fe", stroke="#9333ea", sw=1.5))
    frags.append(text(610, 75, "Сервер (Slave / Backend)", size=13, bold=True, anchor="middle", color="#581c87"))
    frags.append(line(610, 90, 610, 580, color="#94a3b8", sw=1.5, dash="4,4"))

    # Phase 1: Features (y=105 to 180)
    frags.append(rect(40, 105, 720, 75, rx=6, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    frags.append(text(50, 120, "1. Узгодження можливостей (Feature Negotiation)", size=11, bold=True, color="#334155", anchor="start"))
    
    frags.append(arrow(190, 135, 610, 135, color="#0284c7", sw=1.5))
    frags.append(text(400, 130, "VHOST_USER_GET_FEATURES", size=11, bold=True, anchor="middle", color="#0369a1"))
    
    frags.append(arrow(610, 155, 190, 155, color="#0284c7", sw=1.5))
    frags.append(text(400, 150, "Відповідь: підтримувані біти virtio features (64-bit)", size=10, anchor="middle", color="#0369a1"))
    
    frags.append(arrow(190, 172, 610, 172, color="#0284c7", sw=1.5))
    frags.append(text(400, 168, "VHOST_USER_SET_FEATURES / SET_PROTOCOL_FEATURES", size=10, bold=True, anchor="middle", color="#0369a1"))

    # Phase 2: Memory Table (y=190 to 275)
    frags.append(rect(40, 190, 720, 85, rx=6, fill="#f0fdf4", stroke="#86efac", sw=1))
    frags.append(text(50, 205, "2. Передача таблиці пам'яті (Memory Regions)", size=11, bold=True, color="#166534", anchor="start"))

    frags.append(arrow(190, 225, 610, 225, color="#16a34a", sw=2))
    frags.append(text(400, 220, "VHOST_USER_SET_MEM_TABLE + SCM_RIGHTS [fd_0, fd_1, ...]", size=11, bold=True, anchor="middle", color="#15803d"))
    
    frags.append(text(610, 255, "mmap() кожного отриманого fd", size=10, bold=True, anchor="middle", color="#14532d"))

    # Phase 3: Virtqueue Setup (y=285 to 390)
    frags.append(rect(40, 285, 720, 105, rx=6, fill="#fefce8", stroke="#fde047", sw=1))
    frags.append(text(50, 300, "3. Налаштування віртчерг (Virtqueue Configuration)", size=11, bold=True, color="#854d0e", anchor="start"))

    frags.append(arrow(190, 318, 610, 318, color="#ca8a04", sw=1.5))
    frags.append(text(400, 313, "VHOST_USER_SET_VRING_NUM (розмір черги, напр. 256)", size=10, bold=True, anchor="middle", color="#854d0e"))

    frags.append(arrow(190, 342, 610, 342, color="#ca8a04", sw=1.5))
    frags.append(text(400, 337, "VHOST_USER_SET_VRING_ADDR (HVA дескрипторів, avail і used ring)", size=10, anchor="middle", color="#854d0e"))

    frags.append(arrow(190, 368, 610, 368, color="#ca8a04", sw=1.5))
    frags.append(text(400, 363, "VHOST_USER_SET_VRING_BASE (початковий індекс черги)", size=10, bold=True, anchor="middle", color="#854d0e"))

    # Phase 4: Signaling (y=400 to 485)
    frags.append(rect(40, 400, 720, 85, rx=6, fill="#faf5ff", stroke="#d8b4fe", sw=1))
    frags.append(text(50, 415, "4. Передача сигнальних дескрипторів (Signaling Setup)", size=11, bold=True, color="#6b21a8", anchor="start"))

    frags.append(arrow(190, 435, 610, 435, color="#9333ea", sw=1.8))
    frags.append(text(400, 430, "VHOST_USER_SET_VRING_KICK + SCM_RIGHTS [kick_fd / ioeventfd]", size=10, bold=True, anchor="middle", color="#7e22ce"))

    frags.append(arrow(190, 465, 610, 465, color="#9333ea", sw=1.8))
    frags.append(text(400, 460, "VHOST_USER_SET_VRING_CALL + SCM_RIGHTS [call_fd / irqfd]", size=10, bold=True, anchor="middle", color="#7e22ce"))

    # Phase 5: Activation (y=495 to 570)
    frags.append(rect(40, 495, 720, 75, rx=6, fill="#fee2e2", stroke="#fca5a5", sw=1))
    frags.append(text(50, 510, "5. Активація та запуск Data Plane", size=11, bold=True, color="#991b1b", anchor="start"))

    frags.append(arrow(190, 532, 610, 532, color="#dc2626", sw=2))
    frags.append(text(400, 527, "VHOST_USER_SET_VRING_ENABLE (queue_index, enable=1)", size=11, bold=True, anchor="middle", color="#b91c1c"))

    frags.append(text(610, 555, "Старт робочого циклу опитування (PMD Loop)", size=10, bold=True, anchor="middle", color="#991b1b"))

    return frags

if __name__ == "__main__":
    out_dir = os.path.join(current_dir, "img")
    os.makedirs(out_dir, exist_ok=True)
    
    render(os.path.join(out_dir, "vhost-user-architecture.svg"), 860, 650, *draw_vhost_user_architecture())
    render(os.path.join(out_dir, "memory-mapping-translation.svg"), 800, 510, *draw_memory_mapping_translation())
    render(os.path.join(out_dir, "handshake-lifecycle.svg"), 800, 600, *draw_handshake_lifecycle())
    print("All figures generated successfully.")
