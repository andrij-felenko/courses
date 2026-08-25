import os
import sys

# Add scripts folder to sys.path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def generate_iommufd_architecture():
    w, h = 880, 500
    frags = []

    # Title
    frags.append(text(w/2, 28, "Порівняння архітектур: VFIO Type1 vs IOMMUFD", size=18, bold=True))

    # Left Container: VFIO Type1 (Monolithic)
    frags.append(rect(25, 55, 400, 420, fill="#fdf2e9", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(225, 82, "Класичний VFIO Type1 (Монолітна модель)", size=14, bold=True, color="#a04000"))

    box_v1_c1, _, _ = textbox(130, 135, "VFIO Container 1\n(/dev/vfio/vfio #1)", size=11, pad=8, fill="#ffffff", stroke="#d35400")
    box_v1_c2, _, _ = textbox(320, 135, "VFIO Container 2\n(/dev/vfio/vfio #2)", size=11, pad=8, fill="#ffffff", stroke="#d35400")
    frags.append(box_v1_c1)
    frags.append(box_v1_c2)

    box_v1_d1, _, _ = textbox(130, 225, "IOMMU Domain 1\n(Таблиця сторінок #1)", size=11, pad=8, fill="#ffffff", stroke="#e67e22")
    box_v1_d2, _, _ = textbox(320, 225, "IOMMU Domain 2\n(Таблиця сторінок #2)", size=11, pad=8, fill="#ffffff", stroke="#e67e22")
    frags.append(box_v1_d1)
    frags.append(box_v1_d2)

    box_v1_p1, _, _ = textbox(130, 320, "Закріплена RAM #1\n(pin_user_pages: 32 GB)", size=11, pad=8, fill="#fadbd8", stroke=POS)
    box_v1_p2, _, _ = textbox(320, 320, "Закріплена RAM #2\n(Дубль pin: ще 32 GB!)", size=11, pad=8, fill="#fadbd8", stroke=POS)
    frags.append(box_v1_p1)
    frags.append(box_v1_p2)

    box_v1_hw, _, _ = textbox(225, 425, "Апаратні PCIe пристрої (NIC 1 та NIC 2)\nІзольовані в окремих доменах без спільного IOVA", size=11, pad=8, fill="#ffffff", stroke="#7f8c8d")
    frags.append(box_v1_hw)

    frags.append(arrow(130, 165, 130, 195, color=LINE, sw=1.5))
    frags.append(arrow(320, 165, 320, 195, color=LINE, sw=1.5))
    frags.append(arrow(130, 255, 130, 290, color=LINE, sw=1.5))
    frags.append(arrow(320, 255, 320, 290, color=LINE, sw=1.5))
    frags.append(arrow(130, 350, 180, 395, color=LINE, sw=1.5))
    frags.append(arrow(320, 350, 270, 395, color=LINE, sw=1.5))

    # Right Container: IOMMUFD (Decoupled Object Model)
    frags.append(rect(455, 55, 400, 420, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(655, 82, "Сучасний IOMMUFD (Об'єктна модель)", size=14, bold=True, color="#145a32"))

    box_iommu_fd, _, _ = textbox(655, 125, "Контекст iommufd_ctx\n(Єдиний /dev/iommufd FD)", size=11, pad=8, fill="#ffffff", stroke="#27ae60", bold=True)
    frags.append(box_iommu_fd)

    box_ioas, _, _ = textbox(655, 205, "Спільний IOAS (I/O Address Space)\nЄдина карта мапінгу пам'яті (IOPT)", size=11, pad=8, fill="#d5f5e3", stroke="#27ae60")
    frags.append(box_ioas)

    box_shared_pin, _, _ = textbox(655, 290, "Спільне закріплення RAM (Single Pinning)\n(pin_user_pages: рівно 32 GB для всіх пристроїв)", size=11, pad=8, fill="#e8f8f5", stroke="#16a085")
    frags.append(box_shared_pin)

    box_hwpt1, _, _ = textbox(545, 375, "HWPT #1 (DevID 1)\n(Прив'язка до NIC 1)", size=10.5, pad=6, fill="#ffffff", stroke="#2980b9")
    box_hwpt2, _, _ = textbox(765, 375, "HWPT #2 (DevID 2)\n(Прив'язка до NIC 2)", size=10.5, pad=6, fill="#ffffff", stroke="#2980b9")
    frags.append(box_hwpt1)
    frags.append(box_hwpt2)

    box_iommu_hw, _, _ = textbox(655, 445, "PCIe пристрої (NIC 1, NIC 2) використовують спільний IOAS", size=10.5, pad=6, fill="#ffffff", stroke="#7f8c8d")
    frags.append(box_iommu_hw)

    frags.append(arrow(655, 155, 655, 175, color=LINE, sw=1.5))
    frags.append(arrow(655, 235, 655, 260, color=LINE, sw=1.5))
    frags.append(arrow(600, 320, 545, 350, color=LINE, sw=1.5))
    frags.append(arrow(710, 320, 765, 350, color=LINE, sw=1.5))
    frags.append(arrow(545, 400, 610, 430, color=LINE, sw=1.5))
    frags.append(arrow(765, 400, 700, 430, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "iommufd-architecture.svg"), w, h, *frags)

def generate_iommufd_object_graph():
    w, h = 860, 480
    frags = []

    frags.append(text(w/2, 28, "Граф об'єктів підсистеми IOMMUFD у ядрі Linux", size=18, bold=True))

    # Top level: iommufd_ctx
    box_ctx, _, _ = textbox(w/2, 75, "iommufd_ctx (Дескриптор файлу /dev/iommufd)\nКореневий простір імен для всіх дескрипторів uAPI", size=13, pad=10, fill="#e8f4f8", stroke="#2980b9", bold=True)
    frags.append(box_ctx)

    # Core objects layer
    # 1. IOAS
    box_ioas, _, _ = textbox(190, 185, "IOAS (I/O Address Space)\n• Логічний контейнер IOVA -> HVA\n• Таблиця сторінок IOPT\n• Спільний облік pin_user_pages", size=11.5, pad=10, fill="#eafaf1", stroke="#27ae60")
    frags.append(box_ioas)

    # 2. HWPT
    box_hwpt, _, _ = textbox(520, 185, "HWPT (Hardware Page Table)\n• Фізичний домен IOMMU\n• Stage 1 (Guest) або Stage 2 (Host)\n• Автоматичний або вкладений (Nested)", size=11.5, pad=10, fill="#fef9e7", stroke="#f39c12")
    frags.append(box_hwpt)

    # 3. Fault Queue
    box_fault, _, _ = textbox(750, 185, "Fault Queue\n• Черга сторінкових помилок\n• Доставка PRI у userspace\n• Обробка сторінок на вимогу", size=11, pad=8, fill="#fadbd8", stroke="#c0392b")
    frags.append(box_fault)

    # 4. Device (DevID)
    box_dev1, _, _ = textbox(360, 320, "iommufd_device (DevID #1)\nПрив'язка фізичного PCIe пристрою (GPU)", size=11.5, pad=8, fill="#ffffff", stroke="#2980b9")
    box_dev2, _, _ = textbox(680, 320, "iommufd_device (DevID #2)\nПрив'язка фізичного PCIe пристрою (NIC)", size=11.5, pad=8, fill="#ffffff", stroke="#2980b9")
    frags.append(box_dev1)
    frags.append(box_dev2)

    # Bottom hardware layer
    box_hw1, _, _ = textbox(360, 425, "PCIe Device 0000:01:00.0 (VFIO driver)", size=11, pad=8, fill="#f4f6f8", stroke="#7f8c8d")
    box_hw2, _, _ = textbox(680, 425, "PCIe Device 0000:02:00.0 (VFIO driver)", size=11, pad=8, fill="#f4f6f8", stroke="#7f8c8d")
    frags.append(box_hw1)
    frags.append(box_hw2)

    # Connection arrows
    frags.append(arrow(340, 105, 220, 145, color=LINE, sw=1.5))
    frags.append(arrow(430, 105, 500, 145, color=LINE, sw=1.5))
    frags.append(arrow(520, 105, 710, 145, color=LINE, sw=1.5))

    # Relationship between IOAS and HWPT
    frags.append(arrow(310, 185, 395, 185, color="#27ae60", sw=1.8))
    frags.append(text(352, 173, "генерує", size=10.5, color="#27ae60", bold=True))

    # Device attachments
    frags.append(arrow(480, 230, 390, 290, color=LINE, sw=1.5))
    frags.append(arrow(560, 230, 650, 290, color=LINE, sw=1.5))
    frags.append(text(410, 255, "Attach", size=10.5, color=MUTED))
    frags.append(text(620, 255, "Attach", size=10.5, color=MUTED))

    # Fault queue link
    frags.append(arrow(750, 230, 700, 290, color="#c0392b", sw=1.5))
    frags.append(text(750, 260, "PRI Faults", size=10, color="#c0392b"))

    frags.append(arrow(360, 355, 360, 395, color=LINE, sw=1.5))
    frags.append(arrow(680, 355, 680, 395, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "iommufd-object-graph.svg"), w, h, *frags)

def generate_nested_paging_hwpt():
    w, h = 900, 500
    frags = []

    frags.append(text(w/2, 28, "Двостадійна апаратна трансляція (Nested HWPT) в IOMMUFD", size=18, bold=True))

    # Userspace / Guest container
    frags.append(rect(30, 55, 840, 145, fill="#e8f4f8", stroke="#2980b9", sw=1.5, rx=8))
    frags.append(text(50, 76, "Простір користувача / Гостьова ОС (Userspace / Guest VM)", size=12, bold=True, color="#1b4f72", anchor="start"))

    box_gva, _, _ = textbox(150, 140, "Гостьовий процес / Драйвер\nГенерує DMA з адресою GVA", size=11, pad=8, fill="#ffffff", stroke="#2980b9")
    box_s1_user, _, _ = textbox(450, 140, "Stage 1 Таблиця сторінок (HWPT S1)\nКерується безпосередньо гостем (GVA -> GPA)", size=11, pad=8, fill="#ffffff", stroke="#2980b9")
    box_inval, _, _ = textbox(750, 140, "IOMMU_HWPT_INVALIDATE\nІнвалідація IOTLB без VM-exit", size=11, pad=8, fill="#ffffff", stroke="#c0392b")
    frags.append(box_gva)
    frags.append(box_s1_user)
    frags.append(box_inval)

    frags.append(arrow(260, 140, 310, 140, color=LINE, sw=1.5))
    frags.append(arrow(590, 140, 635, 140, color="#c0392b", sw=1.5))

    # Kernel / Hardware container
    frags.append(rect(30, 245, 840, 225, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(50, 268, "Ядро Linux (Хост) та Апаратний IOMMU (Intel VT-d / ARM SMMUv3)", size=12, bold=True, color="#145a32", anchor="start"))

    box_dev_trans, _, _ = textbox(120, 360, "PCIe Пристрій\n(DMA: GVA)", size=11, pad=8, fill="#ffffff", stroke="#7f8c8d")
    box_hw_s1, _, _ = textbox(330, 360, "Стадія 1 (Stage 1)\nЧитання HWPT S1\nТрансляція GVA -> GPA", size=11, pad=8, fill="#ffffff", stroke="#27ae60")
    box_hw_s2, _, _ = textbox(565, 360, "Стадія 2 (Stage 2 / IOAS)\nЧитання HWPT S2\nТрансляція GPA -> HPA", size=11, pad=8, fill="#ffffff", stroke="#27ae60")
    box_dram, _, _ = textbox(780, 360, "Фізична RAM (HPA)\nХост пам'ять", size=11, pad=8, fill="#d5f5e3", stroke="#1e8449", bold=True)

    frags.append(box_dev_trans)
    frags.append(box_hw_s1)
    frags.append(box_hw_s2)
    frags.append(box_dram)

    frags.append(arrow(180, 360, 235, 360, color=LINE, sw=1.8))
    frags.append(arrow(425, 360, 465, 360, color=LINE, sw=1.8))
    frags.append(arrow(665, 360, 715, 360, color=LINE, sw=1.8))

    # Cross-layer pointers
    frags.append(arrow(450, 180, 360, 305, color="#2980b9", sw=1.5))
    box_s1_lbl, _, _ = textbox(390, 220, "Вказівник на HWPT S1", size=10, pad=4, fill="#ffffff", stroke="#2980b9")
    frags.append(box_s1_lbl)

    frags.append(arrow(750, 180, 580, 305, color="#c0392b", sw=1.5))
    box_inv_lbl, _, _ = textbox(685, 220, "Скидання IOTLB", size=10, pad=4, fill="#ffffff", stroke="#c0392b")
    frags.append(box_inv_lbl)

    render(os.path.join(IMG_DIR, "nested-paging-hwpt.svg"), w, h, *frags)

def generate_sva_pasid_iommufd():
    w, h = 880, 480
    frags = []

    frags.append(text(w/2, 28, "Спільна віртуальна адресація (SVA) та PASID через IOMMUFD", size=18, bold=True))

    # Left: CPU Process space
    frags.append(rect(30, 60, 380, 390, fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(220, 85, "Процеси ЦП (CPU Processes)", size=13, bold=True, color="#2c3e50"))

    box_p1, _, _ = textbox(130, 145, "Процес A (CR3 #1)\nВіртуальний простір VA", size=11, pad=8, fill="#ffffff", stroke="#2980b9")
    box_p2, _, _ = textbox(310, 145, "Процес B (CR3 #2)\nВіртуальний простір VA", size=11, pad=8, fill="#ffffff", stroke="#2980b9")
    frags.append(box_p1)
    frags.append(box_p2)

    box_mmu_pt, _, _ = textbox(220, 250, "Таблиці сторінок ядра MMU (CPU Page Tables)\nЄдині сторінки для CPU та периферії", size=11.5, pad=10, fill="#e8f4f8", stroke="#2980b9")
    frags.append(box_mmu_pt)

    box_pf_handler, _, _ = textbox(220, 370, "Обробник Page Fault ядра Linux\nПідвантажує сторінки на вимогу (Demand Paging)", size=11, pad=8, fill="#ffffff", stroke="#27ae60")
    frags.append(box_pf_handler)

    frags.append(arrow(130, 180, 190, 215, color=LINE, sw=1.5))
    frags.append(arrow(310, 180, 250, 215, color=LINE, sw=1.5))
    frags.append(arrow(220, 285, 220, 335, color=LINE, sw=1.5))

    # Right: PCIe Device & IOMMU with PASID
    frags.append(rect(470, 60, 380, 390, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    frags.append(text(660, 85, "Периферія та IOMMU з підтримкою PASID", size=13, bold=True, color="#7e5109"))

    box_dev_pasid, _, _ = textbox(660, 145, "PCIe Пристрій (Акселератор / GPU)\nГенерує TLP з PASID 1 (Процес A) та PASID 2 (Процес B)", size=11, pad=8, fill="#ffffff", stroke="#f39c12")
    frags.append(box_dev_pasid)

    box_pasid_tbl, _, _ = textbox(660, 250, "Таблиця PASID (IOMMU Context Directory)\nPASID 1 -> Вказівник на CR3 Процесу A\nPASID 2 -> Вказівник на CR3 Процесу B", size=11, pad=8, fill="#ffffff", stroke="#f39c12")
    frags.append(box_pasid_tbl)

    box_iommufd_fq, _, _ = textbox(660, 370, "iommufd Fault Queue (PRI)\nПередає сторінкові промахи пристрою в ядро", size=11, pad=8, fill="#fadbd8", stroke="#c0392b")
    frags.append(box_iommufd_fq)

    frags.append(arrow(660, 180, 660, 215, color=LINE, sw=1.5))
    frags.append(arrow(660, 285, 660, 335, color="#c0392b", sw=1.5))

    # Cross connections
    frags.append(arrow(515, 250, 345, 250, color="#27ae60", sw=1.8))
    frags.append(text(430, 238, "Спільний CR3", size=10.5, color="#27ae60", bold=True))

    frags.append(arrow(535, 370, 345, 370, color="#c0392b", sw=1.8))
    frags.append(text(440, 358, "PRI Fault", size=10.5, color="#c0392b", bold=True))

    render(os.path.join(IMG_DIR, "sva-pasid-iommufd.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_iommufd_architecture()
    generate_iommufd_object_graph()
    generate_nested_paging_hwpt()
    generate_sva_pasid_iommufd()
    print("All diagrams generated successfully.")
