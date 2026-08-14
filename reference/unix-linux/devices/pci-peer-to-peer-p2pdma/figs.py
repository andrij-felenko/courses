# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"
BG = "#ffffff"


# ── 1. Порівняння шляхів: Host Bounce vs PCIe P2P ────────────────────────────
def fig_p2p_routing_paths():
    W, H = 1260, 780
    p = []

    # Розділова лінія між двома візуальними варіантами
    p.append(line(W / 2, 70, W / 2, H - 40, color=MUTED, sw=1.2, dash="6 6"))

    # ── Ліворуч: Традиційний шлях через системну RAM (Bounce Buffer)
    lx = 315
    p.append(text(lx, 75, "Традиційний шлях через RAM хоста", size=16, bold=True))

    f_ram, w_ram, h_ram = textbox(lx, 160, ["Системна RAM (DDR5)", "Подвійне навантаження шини пам'яті", "Засмічення L3-кешу CPU"], size=13, pad=14, fill=RED, stroke=POS, sw=1.8)
    p.append(f_ram)

    f_rc1, w_rc1, h_rc1 = textbox(lx, 310, ["Root Complex (CPU)", "Контролер пам'яті"], size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_rc1)

    f_sw1, w_sw1, h_sw1 = textbox(lx, 470, ["PCIe Switch"], size=14, pad=14, fill=BLUE, stroke=LINE)
    p.append(f_sw1)

    f_devA1, w_a1, h_a1 = textbox(lx - 160, 640, ["Ініціатор (NVMe SSD)", "Крок 1: запис у RAM"], size=12, pad=12, fill=WARM, stroke=LINE)
    f_devB1, w_b1, h_b1 = textbox(lx + 160, 640, ["Ціль (GPU VRAM)", "Крок 2: читання з RAM"], size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_devA1)
    p.append(f_devB1)

    # Стрілки ліворуч (Подвійний транзит)
    p.append(arrow(lx - 160, 640 - h_a1 / 2 - 4, lx - 40, 470 + h_sw1 / 2 + 4, color=POS, sw=2))
    p.append(arrow(lx - 40, 470 - h_sw1 / 2 - 4, lx - 40, 310 + h_rc1 / 2 + 4, color=POS, sw=2))
    p.append(arrow(lx - 40, 310 - h_rc1 / 2 - 4, lx - 40, 160 + h_ram / 2 + 4, color=POS, sw=2))

    p.append(arrow(lx + 40, 160 + h_ram / 2 + 4, lx + 40, 310 - h_rc1 / 2 - 4, color=POS, sw=2))
    p.append(arrow(lx + 40, 310 + h_rc1 / 2 + 4, lx + 40, 470 - h_sw1 / 2 - 4, color=POS, sw=2))
    p.append(arrow(lx + 40, 470 + h_sw1 / 2 + 4, lx + 160, 640 - h_b1 / 2 - 4, color=POS, sw=2))

    p.append(text(lx, 740, "Затримка: 3–8 мкс · 2× Смуга RAM", size=13, color=POS, bold=True))

    # ── Праворуч: Прямий доступ P2PDMA через PCIe Switch
    rx = 945
    p.append(text(rx, 75, "Прямий доступ PCIe P2PDMA", size=16, bold=True))

    f_ram2, w_ram2, h_ram2 = textbox(rx, 160, ["Системна RAM (не задіяна)", "Смуга пам'яті вільна для CPU"], size=13, pad=14, fill=GREEN, stroke=FIELD)
    p.append(f_ram2)

    f_rc2, w_rc2, h_rc2 = textbox(rx, 310, ["Root Complex (CPU)", "ACS перевірка (якщо потрібна)"], size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_rc2)

    f_sw2, w_sw2, h_sw2 = textbox(rx, 470, ["PCIe Switch (P2P Routing)", "Локальне перенаправлення TLP"], size=14, pad=14, fill=BLUE, stroke=LINE, sw=2)
    p.append(f_sw2)

    f_devA2, w_a2, h_a2 = textbox(rx - 160, 640, ["Ініціатор (NVMe SSD)", "Прямий TLP MemWrite"], size=12, pad=12, fill=WARM, stroke=LINE)
    f_devB2, w_b2, h_b2 = textbox(rx + 160, 640, ["Ціль (GPU / CMB)", "BAR буфер призначення"], size=12, pad=12, fill=GREEN, stroke=LINE)
    p.append(f_devA2)
    p.append(f_devB2)

    # Стрілка прямого перенаправлення в комутаторі
    p.append(arrow(rx - 160, 640 - h_a2 / 2 - 4, rx - 60, 470 + h_sw2 / 2 + 4, color=FIELD, sw=2.5))
    p.append(arrow(rx - 60, 470 + h_sw2 / 2 + 4, rx + 160, 640 - h_b2 / 2 - 4, color=FIELD, sw=2.5))

    p.append(text(rx, 740, "Затримка: 150–300 нс · 0% Навантаження RAM", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'p2p-routing-paths.svg'), W, H, *p,
           title="Маршрутизація TLP: системна пам'ять проти PCIe P2PDMA")


# ── 2. Шар підсистеми pci-p2pdma в ядрі Linux ──────────────────────────────
def fig_p2pdma_subsystem_layers():
    W, H = 1200, 750
    p = []

    # Верхній рівень: Простір користувача / Застосунок
    f_app, w_app, h_app = textbox(600, 90, ["Простір користувача: io_uring / Direct I/O / GPUDirect Storage", "Вказівник на буфер у /dev/p2pmemX або апаратно виділений CMB"], size=13, pad=14, fill=BLUE, stroke=LINE)
    p.append(f_app)

    # Драйвери блоків / мережі
    f_drv, w_drv, h_drv = textbox(600, 230, ["Драйвер пристрою (NVMe / SmartNIC / GPU Driver)", "Подання `struct scatterlist` до `pci_p2pdma_map_sg()`"], size=13, pad=14, fill=WARM, stroke=LINE)
    p.append(f_drv)
    p.append(arrow(600, 90 + h_app / 2 + 4, 600, 230 - h_drv / 2 - 4))

    # Ядро Linux: MM та pci-p2pdma
    f_mm, w_mm, h_mm = textbox(340, 400, ["Менеджер пам'яті ядра (MM)", "`ZONE_DEVICE` (MEMORY_DEVICE_PCI_P2PDMA)", "Структури `struct page` для MMIO"], size=13, pad=14, fill=GREEN, stroke=LINE)
    f_p2p, w_p2p, h_p2p = textbox(860, 400, ["Підсистема `pci-p2pdma`", "Обчислення відстані `pci_p2pdma_distance_many()`", "Перевірка ACS та перетворення DMA-адрес"], size=13, pad=14, fill=GREEN, stroke=LINE)
    p.append(f_mm)
    p.append(f_p2p)

    p.append(arrow(600, 230 + h_drv / 2 + 4, 340, 400 - h_mm / 2 - 4))
    p.append(arrow(600, 230 + h_drv / 2 + 4, 860, 400 - h_p2p / 2 - 4))

    # Апаратний рівень
    f_bar_prov, w_bp, h_bp = textbox(340, 590, ["Провайдер пам'яті (PCIe BAR)", "NVMe CMB / PMR / GPU VRAM", "Фізичний регіон MMIO"], size=13, pad=14, fill=GREY, stroke=LINE)
    f_dma_client, w_dc, h_dc = textbox(860, 590, ["Ініціатор DMA (Client Endpoint)", "Комутатор PCIe & IOMMU", "Пряме зчитування/запис TLP"], size=13, pad=14, fill=GREY, stroke=LINE)
    p.append(f_bar_prov)
    p.append(f_dma_client)

    p.append(arrow(340, 400 + h_mm / 2 + 4, 340, 590 - h_bp / 2 - 4))
    p.append(arrow(860, 400 + h_p2p / 2 + 4, 860, 590 - h_dc / 2 - 4))

    # Зв'язок між апаратними пристроями на нижньому рівні
    p.append(arrow(340 + w_bp / 2 + 6, 590, 860 - w_dc / 2 - 6, 590, color=FIELD, sw=2.2))

    render(os.path.join(IMG, 'p2pdma-subsystem-layers.svg'), W, H, *p,
           title="Структура підсистеми pci-p2pdma та взаємодія шарів ядра Linux")


if __name__ == '__main__':
    fig_p2p_routing_paths()
    fig_p2pdma_subsystem_layers()
    print("ok")
