import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, textbox, rect, line, arrow, text

def generate_dma_arch():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'dma-mapping-arch.svg')

    frags = []

    # 1. Device Driver / Kernel Memory Layer (Top)
    frags.append(rect(20, 20, 760, 100, fill='#e3f2fd', stroke='#1565c0', rx=8))
    frags.append(text(400, 42, "Драйвер пристрою та підсистеми ядра Linux", size=14, bold=True, color='#1565c0'))
    
    tb_driver, _, _ = textbox(150, 80, "Драйвер пристрою\n(NVMe / NIC / GPU)", size=11, fill='#ffffff', stroke='#1976d2')
    tb_page, _, _ = textbox(400, 80, "Сторінковий розподільник\nkmalloc() / alloc_pages()", size=11, fill='#ffffff', stroke='#1976d2')
    tb_sg, _, _ = textbox(650, 80, "Структури даних\nstruct scatterlist / bio", size=11, fill='#ffffff', stroke='#1976d2')
    frags.extend([tb_driver, tb_page, tb_sg])

    # Arrow to DMA Mapping Core
    frags.append(arrow(400, 120, 400, 150, color='#1565c0'))

    # 2. DMA Mapping Subsystem (Middle)
    frags.append(rect(20, 150, 760, 130, fill='#fff3e0', stroke='#e65100', rx=8))
    frags.append(text(400, 172, "Підсистема dma-mapping (struct dma_map_ops)", size=14, bold=True, color='#e65100'))

    tb_direct, _, _ = textbox(150, 220, "dma-direct\nПряме фізичне\nвідображення", size=11, fill='#ffffff', stroke='#f57c00')
    tb_swiotlb, _, _ = textbox(400, 220, "SWIOTLB\nBounce buffer для\nобмежень адрес", size=11, fill='#ffffff', stroke='#f57c00')
    tb_iommu_ops, _, _ = textbox(650, 220, "iommu-dma\nУправління IOVA\nта таблицями IOMMU", size=11, fill='#ffffff', stroke='#f57c00')
    frags.extend([tb_direct, tb_swiotlb, tb_iommu_ops])

    # Arrows to Hardware Layer
    frags.append(arrow(150, 280, 150, 310, color='#e65100'))
    frags.append(arrow(400, 280, 400, 310, color='#e65100'))
    frags.append(arrow(650, 280, 650, 310, color='#e65100'))

    # 3. Hardware & Memory Layer (Bottom)
    frags.append(rect(20, 310, 760, 120, fill='#e8f5e9', stroke='#2e7d32', rx=8))
    frags.append(text(400, 332, "Апаратний рівень системної шини та RAM", size=14, bold=True, color='#2e7d32'))

    tb_ram, _, _ = textbox(150, 380, "Фізична RAM\n(Синхронізація L1/L2 кешу)", size=11, fill='#ffffff', stroke='#388e3c')
    tb_sw_mem, _, _ = textbox(400, 380, "SWIOTLB RAM (<4GB)\nНизька область RAM", size=11, fill='#ffffff', stroke='#388e3c')
    tb_hw_iommu, _, _ = textbox(650, 380, "Апаратний IOMMU\n(VT-d / AMD-Vi / SMMU)", size=11, fill='#ffffff', stroke='#388e3c')
    frags.extend([tb_ram, tb_sw_mem, tb_hw_iommu])

    render(out_path, 800, 450, *frags)

def generate_coherent_vs_streaming():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'coherent-vs-streaming.svg')

    frags = []

    # Left box: Coherent DMA
    frags.append(rect(20, 20, 365, 340, fill='#e8eaf6', stroke='#3f51b5', rx=8))
    frags.append(text(202, 45, "Coherent (Зв'язане) DMA", size=14, bold=True, color='#3f51b5'))
    
    tb_c1, _, _ = textbox(202, 95, "dma_alloc_coherent()\nВиділення довготривалого буфера", size=11, fill='#ffffff', stroke='#3f51b5')
    tb_c2, _, _ = textbox(202, 175, "Безкешова пам'ять або\nапаратна когерентність шини\n(No CPU cache flush needed)", size=11, fill='#ffffff', stroke='#3f51b5')
    tb_c3, _, _ = textbox(202, 255, "Прямий паралельний доступ\nCPU ↔ Пристрій без dma_sync", size=11, fill='#ffffff', stroke='#3f51b5')
    tb_c4, _, _ = textbox(202, 325, "Призначення: Кільцеві буфери, дескриптори", size=10, bold=True, fill='#e8eaf6', stroke='#3f51b5')
    frags.extend([tb_c1, tb_c2, tb_c3, tb_c4])

    frags.append(arrow(202, 120, 202, 150, color='#3f51b5'))
    frags.append(arrow(202, 205, 202, 230, color='#3f51b5'))

    # Right box: Streaming DMA
    frags.append(rect(415, 20, 365, 340, fill='#fff3e0', stroke='#e65100', rx=8))
    frags.append(text(597, 45, "Streaming (Потокове) DMA", size=14, bold=True, color='#e65100'))

    tb_s1, _, _ = textbox(597, 95, "dma_map_single() / dma_map_sg()\nВідображення наявного sk_buff / bio", size=11, fill='#ffffff', stroke='#e65100')
    tb_s2, _, _ = textbox(597, 175, "Явне скидання/інвалідація кешу CPU\ndma_sync_single_for_device()\ndma_sync_single_for_cpu()", size=11, fill='#ffffff', stroke='#e65100')
    tb_s3, _, _ = textbox(597, 255, "Передача прав власності на буфер\nCPU не чіпає пам'ять під час DMA!", size=11, fill='#ffffff', stroke='#e65100')
    tb_s4, _, _ = textbox(597, 325, "Призначення: Окремі пакети та блоки даних", size=10, bold=True, fill='#fff3e0', stroke='#e65100')
    frags.extend([tb_s1, tb_s2, tb_s3, tb_s4])

    frags.append(arrow(597, 120, 597, 150, color='#e65100'))
    frags.append(arrow(597, 205, 597, 230, color='#e65100'))

    render(out_path, 800, 380, *frags)

def generate_iommu_translation():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'iommu-iova-translation.svg')

    frags = []

    # Device Box
    frags.append(rect(20, 80, 200, 180, fill='#fce4ec', stroke='#c2185b', rx=8))
    frags.append(text(120, 105, "PCIe Пристрій", size=13, bold=True, color='#c2185b'))
    tb_dev, _, _ = textbox(120, 160, "Запит DMA\n32-бітне або 64-бітне\nвіртуальне IOVA", size=11, fill='#ffffff', stroke='#c2185b')
    frags.append(tb_dev)

    # Arrow to IOMMU
    frags.append(arrow(220, 170, 290, 170, color='#c2185b'))
    frags.append(text(255, 155, "IOVA Address", size=10, color='#c2185b'))

    # IOMMU Box
    frags.append(rect(290, 40, 220, 260, fill='#e8f5e9', stroke='#2e7d32', rx=8))
    frags.append(text(400, 65, "Апаратний IOMMU", size=14, bold=True, color='#2e7d32'))
    tb_iommu_tbl, _, _ = textbox(400, 130, "Таблиці сторінок IOMMU\n(Page Tables)\nIOVA 0x1000 → PA Page #5\nIOVA 0x2000 → PA Page #88", size=11, fill='#ffffff', stroke='#2e7d32')
    tb_prot, _, _ = textbox(400, 240, "Перевірка прав доступу\n(R/W Protection & Isolation)", size=10, fill='#ffffff', stroke='#2e7d32')
    frags.extend([tb_iommu_tbl, tb_prot])

    # Arrow to RAM
    frags.append(arrow(510, 170, 580, 170, color='#2e7d32'))
    frags.append(text(545, 155, "Physical RAM (PA)", size=10, color='#2e7d32'))

    # Physical RAM Box
    frags.append(rect(580, 40, 200, 260, fill='#ede7f6', stroke='#512da8', rx=8))
    frags.append(text(680, 65, "Фізична RAM", size=14, bold=True, color='#512da8'))
    tb_p1, _, _ = textbox(680, 120, "Page #5 (Physical Address)", size=10, fill='#ffffff', stroke='#512da8')
    tb_p2, _, _ = textbox(680, 180, "Page #88 (Physical Address)", size=10, fill='#ffffff', stroke='#512da8')
    tb_p3, _, _ = textbox(680, 240, "Розсічені фізичні сторінки\nвиглядають неперервними!", size=10, fill='#ede7f6', stroke='#512da8')
    frags.extend([tb_p1, tb_p2, tb_p3])

    render(out_path, 800, 320, *frags)

if __name__ == '__main__':
    generate_dma_arch()
    generate_coherent_vs_streaming()
    generate_iommu_translation()
    print("SVG generation complete.")
