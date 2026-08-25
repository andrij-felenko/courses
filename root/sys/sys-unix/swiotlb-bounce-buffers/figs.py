# -*- coding: utf-8 -*-
"""Фігури до теми «swiotlb: підмінні буфери, коли пристрій не дотягується»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_swiotlb_architecture():
    """Фізична пам'ять 64-бітної системи та підмінний пул swiotlb."""
    W, H = 1060, 540
    f = []

    f.append(text(W / 2, 30, "Адресація пам'яті та підмінний пул swiotlb", size=17, bold=True))

    # Ліва колонка: 64-бітна фізична пам'ять
    f.append(text(270, 70, "Фізична пам'ять (RAM 64-бітної системи)", size=14, bold=True))

    # Висока пам'ять (> 4 ГБ)
    f.append(rect(60, 95, 420, 155, fill="#fdf2e9", stroke="#d35400", sw=1.5))
    f.append(text(270, 120, "Висока пам'ять: адреси вище 4 ГБ (0x100000000+)", size=13, bold=True, color="#d35400"))
    f.append(fitbox(80, 138, 380, 50, "Оригінальний буфер драйвера (skb / bio)\nФізична адреса: 0x2_4000_1000", size=12, fill="#ffffff", stroke="#d35400"))
    f.append(text(270, 230, "32-бітний контролер не може виставити біти [63:32]", size=11, color=MUTED, italic=True))

    # Межа 4 ГБ
    f.append(line(50, 265, 490, 265, color=POS, sw=1.8, dash="6 4"))
    f.append(text(270, 260, "Апаратна межа 32-бітної адресації (4 ГБ / 0xFFFFFFFF)", size=11, color=POS, bold=True))

    # Низька пам'ять (< 4 ГБ)
    f.append(rect(60, 280, 420, 205, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(270, 302, "Низька пам'ять: адреси до 4 ГБ (ZONE_DMA32)", size=13, bold=True))
    f.append(fitbox(80, 320, 380, 72, "Пул SWIOTLB (виділено під час завантаження)\nДіапазон адрес: 0x3800_0000 – 0x3C00_0000 (64 МіБ)\nСлот підміни (bounce buffer): 0x3804_2000", size=12, fill="#eafaf0", stroke=FIELD, color=FIELD))
    f.append(fitbox(80, 404, 380, 64, "Пам'ять ядра, системні структури та стек\n(0x0000_0000 – 0x37FF_FFFF)", size=12, fill="#ffffff", stroke=MUTED))

    # Права колонка: Пристрій та процесор
    f.append(text(790, 70, "Апаратний пристрій та ядро ОС", size=14, bold=True))

    # 32-бітний пристрій
    f.append(fitbox(580, 95, 420, 95, "32-бітний пристрій (наприклад, PCI NIC / контролер)\nDMA-маска: 0x00000000FFFFFFFF (32 біти)\nРегістри адрес мають лише 32 розряди", size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Процесор / Ядро (memcpy)
    f.append(fitbox(580, 350, 420, 110, "Ядро Linux: підсистема swiotlb\nВиконує memcpy між високим буфером\nта низьким підмінним слотом", size=13, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    # Прямий DMA неможливий (червоний хрест/лінія)
    f.append(line(580, 142, 465, 142, color=POS, sw=2, dash="4 4"))
    f.append(fitbox(485, 120, 85, 24, "Блоковано", size=10, fill="#ffffff", stroke=POS, color=POS, bold=True))

    # DMA до підмінного слота
    f.append(arrow(700, 190, 465, 340, color=FIELD, sw=2))
    f.append(fitbox(550, 240, 160, 36, "DMA шиною\n(адреса < 4 ГБ)", size=11, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    # Копіювання memcpy
    # 1. Перед передачею
    f.append(arrow(720, 350, 465, 175, color=NEG, sw=1.8))
    f.append(fitbox(530, 290, 140, 36, "1. memcpy\n(перед передачею)", size=10, fill="#ffffff", stroke=NEG, color=NEG, bold=True))

    # 2. Після прийому
    f.append(arrow(465, 365, 580, 395, color=NEG, sw=1.8))
    f.append(fitbox(475, 410, 130, 36, "2. memcpy\n(після прийому)", size=10, fill="#ffffff", stroke=NEG, color=NEG, bold=True))

    # Підпис знизу
    f.append(text(W / 2, 518, "Пристрій здійснює DMA лише з низьким пулом; процесор переносить дані у високу пам'ять", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'swiotlb-architecture.svg'), W, H, *f)


def fig_bounce_lifecycle():
    """Життєвий цикл передачі даних через підмінні буфери."""
    W, H = 1060, 560
    f = []

    f.append(text(W / 2, 30, "Повний цикл відображення та синхронізації підмінного буфера", size=17, bold=True))

    # Два сценарії: передача (DMA_TO_DEVICE) та прийом (DMA_FROM_DEVICE)
    f.append(text(280, 68, "Передача: DMA_TO_DEVICE (CPU → Пристрій)", size=14, bold=True, color=NEG))
    f.append(text(780, 68, "Прийом: DMA_FROM_DEVICE (Пристрій → CPU)", size=14, bold=True, color=POS))

    # Ліва колонка: DMA_TO_DEVICE
    steps_tx = [
        ("1. dma_map_single(dev, buf, len, TO_DEVICE)", "Перевірка маски: буфер лежить у високій пам'яті.\nВиділення N слотів у пулі swiotlb.", "#ffffff", LINE),
        ("2. swiotlb_bounce() [memcpy]", "Копіювання корисних даних із буфера buf\nу виділені низькі слоти пулу swiotlb.", "#eaf0fd", NEG),
        ("3. Пристрій виконує DMA-читання", "Контролер зчитує байти з підмінного слота\nчерез шину PCI/PCIe.", "#eafaf0", FIELD),
        ("4. dma_unmap_single(dev, dma_addr, ...)", "Звільнення слотів у пулі swiotlb.\nДані в пам'яті процесора не змінюються.", "#ffffff", LINE),
    ]

    # Права колонка: DMA_FROM_DEVICE
    steps_rx = [
        ("1. dma_map_single(dev, buf, len, FROM_DEVICE)", "Перевірка маски: буфер у високій пам'яті.\nВиділення слотів у пулі (без початкового memcpy).", "#ffffff", LINE),
        ("2. Пристрій виконує DMA-запис", "Контролер записує прийнятий пакет чи блок\nбезпосередньо у низький слот swiotlb.", "#eafaf0", FIELD),
        ("3. dma_unmap_single(dev, dma_addr, ...)", "Ядро виявляє операцію завершення DMA\nта прапорець напрямку FROM_DEVICE.", "#ffffff", LINE),
        ("4. swiotlb_bounce() [memcpy]", "Копіювання прийнятих байтів зі слота swiotlb\nназад в оригінальний буфер buf. Звільнення слотів.", "#fdecea", POS),
    ]

    y0, bh, gap = 95, 84, 26

    for i, (head, desc, fillc, col) in enumerate(steps_tx):
        y = y0 + i * (bh + gap)
        f.append(fitbox(50, y, 460, bh, head + "\n" + desc, size=12, fill=fillc, stroke=col, color=col if col != LINE else INK))
        if i + 1 < len(steps_tx):
            f.append(arrow(280, y + bh, 280, y + bh + gap, color=MUTED))

    for i, (head, desc, fillc, col) in enumerate(steps_rx):
        y = y0 + i * (bh + gap)
        f.append(fitbox(550, y, 460, bh, head + "\n" + desc, size=12, fill=fillc, stroke=col, color=col if col != LINE else INK))
        if i + 1 < len(steps_rx):
            f.append(arrow(780, y + bh, 780, y + bh + gap, color=MUTED))

    f.append(text(W / 2, 538, "При передачі копіювання відбувається на стадії map, при прийомі — на стадії unmap", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'bounce-lifecycle.svg'), W, H, *f)


def fig_confidential_computing_boundary():
    """Межа захисту пам'яті у конфіденційних віртуальних машинах (SEV / TDX)."""
    W, H = 1060, 500
    f = []

    f.append(text(W / 2, 30, "Підмінні буфери як межа безпеки в Confidential VM (AMD SEV / Intel TDX)", size=17, bold=True))

    # Конфіденційна гостьова VM (Guest VM)
    f.append(rect(40, 65, 550, 390, fill="#fdfefe", stroke=NEG, sw=2))
    f.append(text(315, 92, "Конфіденційна гостьова система (Guest VM)", size=15, bold=True, color=NEG))

    # Приватна зашифрована пам'ять
    f.append(rect(60, 115, 510, 160, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(315, 138, "Приватна пам'ять гостя (Encrypted Memory / C-bit=1)", size=13, bold=True, color=NEG))
    f.append(fitbox(80, 155, 470, 52, "Оперативна пам'ять ядра, програми, стек, файлові буфери\nЗашифрована апаратним ключем процесора (AES-128/256)", size=12, fill="#ffffff", stroke=NEG))
    f.append(fitbox(80, 214, 470, 48, "Гіпервізор бачить тут лише зашифрований шум\nПрямий доступ зовнішніх пристроїв сюди заборонений залізом", size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))

    # Розділена відкрита пам'ять (SWIOTLB Shared Pool)
    f.append(rect(60, 290, 510, 145, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(315, 312, "Спільна відкрита пам'ять (Decrypted Shared Memory / C-bit=0)", size=13, bold=True, color=POS))
    f.append(fitbox(80, 328, 470, 54, "Пул SWIOTLB у гостьовій системі (swiotlb=force)\nСторінки навмисно розшифровано через set_memory_decrypted()", size=12, fill="#ffffff", stroke=POS))
    f.append(fitbox(80, 388, 470, 38, "Тільки тут лежать підмінні буфери введення-виведення", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Недовірене середовище хоста (Host Hypervisor & Devices)
    f.append(rect(680, 65, 340, 390, fill="#fbfcfc", stroke=POS, sw=2))
    f.append(text(850, 92, "Недовірений хост / Гіпервізор", size=15, bold=True, color=POS))

    f.append(fitbox(700, 125, 300, 75, "KVM / QEMU / Емульовані пристрої\n(VirtIO-net, VirtIO-blk, VFIO)", size=13, fill="#ffffff", stroke=LINE))
    f.append(fitbox(700, 220, 300, 65, "Апаратна шина PCIe хоста\nта фізичні мережеві карти / NVMe", size=13, fill="#ffffff", stroke=LINE))

    # Стрілки взаємодії
    # 1. Спроба доступу хоста до зашифрованої пам'яті блокується
    f.append(line(700, 160, 590, 160, color=POS, sw=2, dash="4 4"))
    f.append(fitbox(595, 148, 80, 24, "Блоковано", size=10, fill="#ffffff", stroke=POS, color=POS, bold=True))

    # 2. Доступ хоста до відкритого пулу swiotlb дозволено
    f.append(arrow(700, 355, 590, 355, color=FIELD, sw=2))
    f.append(fitbox(595, 328, 80, 24, "DMA", size=10, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    # 3. Внутрішній перенос даних гостем (memcpy)
    f.append(arrow(315, 275, 315, 290, color=NEG, sw=2))

    f.append(text(W / 2, 478, "SWIOTLB ізолює конфіденційну пам'ять гостя від недовіреного гіпервізора та пристроїв хоста", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'confidential-computing-boundary.svg'), W, H, *f)


def fig_slot_allocation():
    """Внутрішня організація пам'яті swiotlb: слоти, ділянки та маски вирівнювання."""
    W, H = 1060, 520
    f = []

    f.append(text(W / 2, 30, "Внутрішня структура пулу swiotlb: слоти, чанки та вирівнювання", size=17, bold=True))

    # 1. Структура io_tlb_mem та ділянки (areas)
    f.append(text(200, 70, "Структура пулу io_tlb_mem", size=14, bold=True))
    f.append(fitbox(50, 92, 300, 110, "struct io_tlb_mem\n• nslabs: загальна к-ть слотів (напр. 32768)\n• areas: масив незалежних ділянок\n• slots: дескриптори io_tlb_slot[]\n• vaddr: віртуальна адреса пулу", size=12, fill="#ffffff", stroke=LINE))

    # 2. Ділянки для зменшення конкуренції за блокування
    f.append(text(650, 70, "Багатоділянкова структура (io_tlb_area)", size=14, bold=True))
    areas = [("Ділянка 0 (CPU 0..3)\narea->lock", 400), ("Ділянка 1 (CPU 4..7)\narea->lock", 600), ("Ділянка N...\narea->lock", 800)]
    for lab, x in areas:
        f.append(fitbox(x, 92, 180, 60, lab, size=12, fill="#eaf0fd", stroke=NEG, color=NEG))
    f.append(text(680, 175, "Кожна ділянка має власний spinlock — зникає глобальна конкуренція ядер", size=12, color=MUTED, italic=True))

    # 3. Розбиття пам'яті на слоти по 2 КіБ (IO_TLB_SIZE)
    f.append(text(W / 2, 225, "Масив слотів неперервної фізичної пам'яті (IO_TLB_SIZE = 2048 байтів)", size=14, bold=True))

    slot_w = 110
    start_x = 55
    y_slot = 250
    h_slot = 65

    slots = [
        ("Слот 0\n[Вільний]", "#ffffff", LINE),
        ("Слот 1\n[Зайнятий]", "#fdecea", POS),
        ("Слот 2\n[Зайнятий]", "#fdecea", POS),
        ("Слот 3\n[Зайнятий]", "#fdecea", POS),
        ("Слот 4\n[Вільний]", "#ffffff", LINE),
        ("Слот 5\n[Вільний]", "#ffffff", LINE),
        ("Слот 6\n[Зайнятий]", "#eafaf0", FIELD),
        ("Слот N...", "#ffffff", LINE),
    ]

    for i, (sl_text, sl_fill, sl_stroke) in enumerate(slots):
        x = start_x + i * (slot_w + 12)
        f.append(fitbox(x, y_slot, slot_w, h_slot, sl_text, size=12, fill=sl_fill, stroke=sl_stroke, color=sl_stroke if sl_stroke != LINE else INK))

    # Виділення суміжного блоку
    f.append(rect(start_x + 1 * (slot_w + 12) - 4, y_slot - 4, 3 * (slot_w + 12) - 4, h_slot + 8, fill="none", stroke=POS, sw=2, rx=8))
    f.append(text(start_x + 2.5 * (slot_w + 12) - 6, y_slot + h_slot + 24, "Виділення на 6 КіБ (3 суміжні слоти підряд)", size=12, color=POS, bold=True))

    # 4. Збереження зміщення та вирівнювання
    f.append(text(280, 380, "Збереження зміщення в сторінці (Alignment Mask)", size=14, bold=True))
    f.append(fitbox(50, 400, 460, 80, "Оригінальний буфер: 0x2_4000_10A0 (зміщення 0x0A0)\nПідмінний слот:     0x0_3800_20A0 (зміщення 0x0A0)\nЗсув у межах сторінки зберігається через orig_addr & align_mask,\nщоб не порушити апаратне вирівнювання транзакцій пристрою", size=12, fill="#fdf2e9", stroke="#d35400"))

    # 5. Метадані io_tlb_slot
    f.append(text(780, 380, "Метадані дескриптора io_tlb_slot", size=14, bold=True))
    f.append(fitbox(550, 400, 460, 80, "struct io_tlb_slot {\n    phys_addr_t orig_addr;   /* початкова адреса */\n    size_t alloc_size;       /* розмір виділення */\n    unsigned int list;       /* довжина ланцюжка вільних слотів */\n};", size=12, fill="#f4f6f8", stroke=LINE))

    f.append(text(W / 2, 502, "Дескриптори слотів відстежують вихідні адреси для точного зворотного копіювання при unmap", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'slot-allocation.svg'), W, H, *f)


if __name__ == '__main__':
    fig_swiotlb_architecture()
    fig_bounce_lifecycle()
    fig_confidential_computing_boundary()
    fig_slot_allocation()
    print("ok")
