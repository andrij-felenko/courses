# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE  = "#eaf0fd"
GREEN = "#eaf6ef"
WARM  = "#fff6e5"
RED   = "#fdecea"
GREY  = "#eceff1"


# ── 1. Спільна лінія INTx: колізія та оверхед опитування ────────────────────
def fig_intx_overhead():
    W, H = 1000, 560
    p = []

    # 4 пристрої ліворуч
    dev_x = 160
    y_devs = [100, 200, 300, 400]
    dev_names = [
        ("Мережева карта (eth0)", "IRQ_NONE (не моя подія)", GREY),
        ("Контролер SATA (sda)", "IRQ_NONE (не моя подія)", GREY),
        ("Звуковий чип (snd)", "IRQ_HANDLED (виставив лінію)", RED),
        ("USB-контролер (xhci)", "IRQ_NONE (не моя подія)", GREY),
    ]

    for i, (name, status, fill) in enumerate(dev_names):
        y = y_devs[i]
        f, w, h = textbox(dev_x, y, [name, status], size=13, pad=10, fill=fill, stroke=LINE)
        p.append(f)
        # лінія від пристрою до спільного дроту
        p.append(line(dev_x + w / 2, y, 420, y, color=POS if i == 2 else MUTED, sw=2 if i == 2 else 1.2))

    # Спільна фізична лінія INTx (Active-Low Open-Drain)
    p.append(line(420, 80, 420, 420, color=POS, sw=3.5))
    p.append(text(420, 55, "Спільний дріт INTA# (active-low)", size=13, color=POS, bold=True))

    # Зв'язок від спільної лінії до I/O APIC
    p.append(arrow(420, 250, 520, 250, color=POS, sw=2.5))

    # I/O APIC
    f_apic, w_apic, h_apic = textbox(600, 250, ["I/O APIC", "Вхід GSI 16", "(рівневий тригер)"],
                                     size=13, pad=12, fill=WARM, stroke=LINE)
    p.append(f_apic)

    p.append(arrow(600 + w_apic / 2, 250, 720, 250, color=LINE, sw=2))

    # CPU та ланцюжок обробників
    f_cpu, w_cpu, h_cpu = textbox(850, 250, [
        "CPU (Ядро 0)",
        "Виклик усього ланцюжка:",
        "1. eth0_irq() → MMIO read → ні",
        "2. sda_irq()  → MMIO read → ні",
        "3. snd_irq()  → MMIO read → ТАК!",
        "4. xhci_irq() → MMIO read → ні"
    ], size=12, pad=14, fill=BLUE, stroke=LINE)
    p.append(f_cpu)

    # Примітка внизу
    f_note, _, _ = textbox(500, 500, [
        "Оверхед INTx: 4 виклики драйверів поспіль + 4 повільні MMIO non-posted зчитування через шину (~1-2 мкс кожне),",
        "хоча переривання згенерував лише один звуковий контролер."
    ], size=12, pad=10, fill=GREY, stroke=MUTED)
    p.append(f_note)

    render(os.path.join(IMG, 'intx-shared-line-overhead.svg'), W, H, *p,
           title="Спільна фізична лінія INTx: колізія пристроїв та оверхед опитування")


# ── 2. Порівняння архітектури MSI та MSI-X ──────────────────────────────────
def fig_msi_vs_msix():
    W, H = 1060, 580
    p = []

    # Ліва колонка: MSI (PCI 2.2)
    msi_cx = 270
    f_msi_hdr, _, _ = textbox(msi_cx, 75, ["Класичний MSI (PCI 2.2 / PCIe)", "До 32 векторів (степінь 2: 1, 2, 4, 8, 16, 32)"],
                              size=14, pad=10, fill=WARM, stroke=LINE, bold=True)
    p.append(f_msi_hdr)

    f_msi_reg, _, _ = textbox(msi_cx, 190, [
        "PCI Config Space: MSI Capability (0x05)",
        "┌──────────────────────────────────────────────┐",
        "│ Message Address: 0xFEE00000 (Local APIC CPU0)│",
        "│ Message Data: Base Vector 0x60               │",
        "│ Multiple Message Enable: 4 вектори           │",
        "└──────────────────────────────────────────────┘"
    ], size=11, pad=12, fill=FILL, stroke=LINE)
    p.append(f_msi_reg)

    f_msi_vecs, _, _ = textbox(msi_cx, 340, [
        "Вектор 0: Data = 0x60 → CPU0 (Local APIC 0)",
        "Вектор 1: Data = 0x61 → CPU0 (Local APIC 0)",
        "Вектор 2: Data = 0x62 → CPU0 (Local APIC 0)",
        "Вектор 3: Data = 0x63 → CPU0 (Local APIC 0)"
    ], size=12, pad=10, fill=RED, stroke=POS)
    p.append(f_msi_vecs)

    f_msi_lim, _, _ = textbox(msi_cx, 470, [
        "Обмеження MSI:",
        "• Усі вектори мають ОДНУ адресу (летять на одне ядро CPU)",
        "• Вектори мусять бути неперервним блоком у процесорі",
        "• Максимум 32 вектори на функцію"
    ], size=11, pad=10, fill=GREY, stroke=MUTED)
    p.append(f_msi_lim)

    # Розділювач
    p.append(line(530, 50, 530, 530, color=MUTED, sw=1.5, dash="4,4"))

    # Права колонка: MSI-X (PCI 3.0 / PCIe)
    msix_cx = 790
    f_msix_hdr, _, _ = textbox(msix_cx, 75, ["Розширений MSI-X (PCI 3.0 / PCIe)", "До 2048 повністю незалежних векторів"],
                               size=14, pad=10, fill=GREEN, stroke=LINE, bold=True)
    p.append(f_msix_hdr)

    f_msix_tbl, _, _ = textbox(msix_cx, 200, [
        "MSI-X Table (у MMIO BAR пристрою, масив 16 байт):",
        "┌──────────────────────────────────────────────────────────┐",
        "│ Запис 0: Addr=0xFEE00000 (CPU0), Data=0x40, Mask=0       │",
        "│ Запис 1: Addr=0xFEE01000 (CPU1), Data=0x52, Mask=0       │",
        "│ Запис 2: Addr=0xFEE02000 (CPU2), Data=0x71, Mask=0       │",
        "│ Запис 3: Addr=0xFEE03000 (CPU3), Data=0x83, Mask=0       │",
        "└──────────────────────────────────────────────────────────┘"
    ], size=11, pad=12, fill=FILL, stroke=LINE)
    p.append(f_msix_tbl)

    f_msix_vecs, _, _ = textbox(msix_cx, 340, [
        "Вектор 0 → CPU0 (Local APIC 0, вектор 0x40)",
        "Вектор 1 → CPU1 (Local APIC 1, вектор 0x52)",
        "Вектор 2 → CPU2 (Local APIC 2, вектор 0x71)",
        "Вектор 3 → CPU3 (Local APIC 3, вектор 0x83)"
    ], size=12, pad=10, fill=BLUE, stroke=NEG)
    p.append(f_msix_vecs)

    f_msix_adv, _, _ = textbox(msix_cx, 470, [
        "Переваги MSI-X:",
        "• Кожен вектор має власну адресу (пряме націлювання на будь-яке ядро)",
        "• Вектори не залежать один від одного в таблиці IDT",
        "• До 2048 векторів, індивідуальне маскування в MMIO"
    ], size=11, pad=10, fill=GREY, stroke=MUTED)
    p.append(f_msix_adv)

    render(os.path.join(IMG, 'msi-vs-msix-architecture.svg'), W, H, *p,
           title="Архітектурна еволюція: монолітний MSI проти гнучкого MSI-X")


# ── 3. Структура MSI-X Table та PBA у просторі BAR ─────────────────────────
def fig_msix_table_pba():
    W, H = 1020, 560
    p = []

    # Зліва: PCI Configuration Space
    cfg_x = 220
    f_cfg_hdr, _, _ = textbox(cfg_x, 80, ["PCI Configuration Space (Type 0)", "Capability ID 0x11 (MSI-X)"],
                              size=13, pad=10, fill=WARM, stroke=LINE, bold=True)
    p.append(f_cfg_hdr)

    f_cap, w_cap, h_cap = textbox(cfg_x, 240, [
        "MSI-X Capability Structure",
        "offset 0x00: Cap ID (0x11) | Next Pointer",
        "offset 0x02: Message Control (Table Size, Enable)",
        "offset 0x04: Table Offset (29b) | Table BIR (3b)",
        "offset 0x08: PBA Offset (29b)   | PBA BIR (3b)"
    ], size=12, pad=12, fill=FILL, stroke=LINE)
    p.append(f_cap)

    # Стрілки вказівників на BAR
    p.append(arrow(cfg_x + w_cap / 2, 250, 480, 180, color=NEG, sw=2))
    p.append(arrow(cfg_x + w_cap / 2, 275, 480, 410, color=POS, sw=2))

    # Справа: MMIO BAR пристрою
    bar_x = 730

    # MSI-X Table
    f_tbl, _, _ = textbox(bar_x, 180, [
        "MSI-X Table (у BAR[Table BIR] за зсувом Table Offset)",
        "┌─────────────────────────────────────────────────────────────┐",
        "│ Запис 0: Msg Addr Low | Msg Addr High | Msg Data | Vec Ctrl │ (16 байтів)",
        "│ Запис 1: Msg Addr Low | Msg Addr High | Msg Data | Vec Ctrl │ (16 байтів)",
        "│ Запис 2: Msg Addr Low | Msg Addr High | Msg Data | Vec Ctrl │ (16 байтів)",
        "│ ...                                                         │",
        "│ Запис N: Msg Addr Low | Msg Addr High | Msg Data | Vec Ctrl │ (N <= 2047)",
        "└─────────────────────────────────────────────────────────────┘",
        "Vector Control: біт 0 = Mask Bit (1 = вектор замасковано)"
    ], size=11, pad=12, fill=BLUE, stroke=LINE)
    p.append(f_tbl)

    # PBA (Pending Bit Array)
    f_pba, _, _ = textbox(bar_x, 410, [
        "Pending Bit Array (PBA) (у BAR[PBA BIR] за зсувом PBA Offset)",
        "┌─────────────────────────────────────────────────────────────┐",
        "│ QWORD 0 (біти 0..63):    [P63][P62] ... [P2][P1][P0]        │",
        "│ QWORD 1 (біти 64..127):  [P127][P126] ... [P65][P64]        │",
        "│ ...                                                         │",
        "└─────────────────────────────────────────────────────────────┘",
        "P[k] = 1: під час дії Mask Bit для вектора k виникла подія."
    ], size=11, pad=12, fill=RED, stroke=LINE)
    p.append(f_pba)

    p.append(text(bar_x, 525, "Кожен запис таблиці займає рівно 16 байтів (4 DWORD). PBA запаковано по 64 біти на рядок.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'msix-table-and-pba-layout.svg'), W, H, *p,
           title="Розміщення MSI-X Table та PBA у просторі пам'яті BAR пристрою")


# ── 4. Багаточерговість пристрою та пряме прив'язування до ядер CPU ─────────
def fig_multiqueue():
    W, H = 1040, 600
    p = []

    # Ліва колонка: Черги пристрою (NIC / NVMe)
    q_x = 170
    f_nic, _, _ = textbox(q_x, 65, ["PCIe Пристрій (Multi-Queue NIC / NVMe)", "RSS хешування або Per-CPU SQ/CQ"],
                          size=13, pad=10, fill=WARM, stroke=LINE, bold=True)
    p.append(f_nic)

    y_qs = [150, 240, 330, 420]
    q_labels = [
        ("Черга RX 0 / CQ 0", "MSI-X Вектор 0", BLUE),
        ("Черга RX 1 / CQ 1", "MSI-X Вектор 1", GREEN),
        ("Черга RX 2 / CQ 2", "MSI-X Вектор 2", WARM),
        ("Черга RX 3 / CQ 3", "MSI-X Вектор 3", RED),
    ]

    for i, (q_name, v_name, col) in enumerate(q_labels):
        y = y_qs[i]
        f_q, w_q, h_q = textbox(q_x, y, [q_name, v_name], size=12, pad=10, fill=col, stroke=LINE)
        p.append(f_q)

        # Стрілка через PCIe Fabric
        p.append(arrow(q_x + w_q / 2, y, 460, y, color=LINE, sw=1.8))

    # Центральна колонка: PCIe TLP Memory Writes
    tlp_x = 540
    f_pcie, _, _ = textbox(tlp_x, 285, [
        "PCIe Switch / Root Complex",
        "TLP Memory Write 32-bit:",
        "• Запис у 0xFEE00000 (APIC 0)",
        "• Запис у 0xFEE01000 (APIC 1)",
        "• Запис у 0xFEE02000 (APIC 2)",
        "• Запис у 0xFEE03000 (APIC 3)",
        "(In-band запис без виділених ліній)"
    ], size=11, pad=12, fill=FILL, stroke=LINE)
    p.append(f_pcie)

    for y in y_qs:
        p.append(arrow(620, y, 760, y, color=LINE, sw=1.8))

    # Права колонка: Ядра CPU та локальна обробка
    cpu_x = 880
    cpu_labels = [
        ("Ядро CPU 0 (Local APIC 0)", "irq 42 → napi_poll CPU0", BLUE),
        ("Ядро CPU 1 (Local APIC 1)", "irq 43 → napi_poll CPU1", GREEN),
        ("Ядро CPU 2 (Local APIC 2)", "irq 44 → napi_poll CPU2", WARM),
        ("Ядро CPU 3 (Local APIC 3)", "irq 45 → napi_poll CPU3", RED),
    ]

    for i, (cpu_name, isr_name, col) in enumerate(cpu_labels):
        y = y_qs[i]
        f_c, _, _ = textbox(cpu_x, y, [cpu_name, isr_name], size=12, pad=10, fill=col, stroke=LINE)
        p.append(f_c)

    f_bot, _, _ = textbox(520, 530, [
        "Результат паралелізації: кожне ядро CPU обслуговує виключно свою апаратну чергу пристрою.",
        "Повна відсутність між'ядерних замків (lockless), міжпроцесорних IPI та перенесення ліній кешу L1/L2."
    ], size=12, pad=10, fill=GREY, stroke=MUTED)
    p.append(f_bot)

    render(os.path.join(IMG, 'multiqueue-cpu-affinity.svg'), W, H, *p,
           title="Багаточерговість PCIe пристрою та пряме прив'язування переривань до ядер CPU")


if __name__ == '__main__':
    fig_intx_overhead()
    fig_msi_vs_msix()
    fig_msix_table_pba()
    fig_multiqueue()
    print("All figures generated successfully.")
