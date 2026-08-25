# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер переривань: irqchip, irq_domain і шлях від hwirq до номера Linux»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#f4f6f8"
WARM_BG  = "#fff4e0"
BLUE_BG  = "#eaf0fd"
GOLD     = "#b8860b"


# ── 1. Відображення апаратних номерів (hwirq) у віртуальний простір (virq) ────
def fig_hwirq_to_virq():
    W, H = 1200, 680
    P = []

    # Заголовки просторів
    P.append(text(230, 45, "Апаратний простір контролерів (hwirq)", size=15, bold=True, color=INK))
    P.append(text(920, 45, "Єдиний простір ядра Linux (virq / irq_desc)", size=15, bold=True, color=INK))

    # Контролер 1: SoC Root GIC
    P.append(rect(40, 75, 380, 240, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(230, 102, "Root Interrupt Controller (наприклад, GICv3)", size=13, bold=True, color=INK))
    P.append(fitbox(60, 120, 340, 42, "hwirq 0..31: PPI (Per-CPU, локальні таймери)", size=12, fill=WARM_BG, stroke=GOLD))
    P.append(fitbox(60, 172, 340, 42, "hwirq 32: UART (SPI — спільне периферійне)", size=12, fill=GREEN_BG, stroke=FIELD))
    P.append(fitbox(60, 224, 340, 42, "hwirq 33: I2C контролер шини", size=12, fill=BLUE_BG, stroke=NEG))
    P.append(fitbox(60, 276, 340, 32, "hwirq 34..1019: Інші периферійні блоки SoC", size=11, fill=GREY_BG, stroke=MUTED))

    # Контролер 2: GPIO контролер (вторинний)
    P.append(rect(40, 345, 380, 210, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(230, 372, "GPIO Controller (вторинний каскадний)", size=13, bold=True, color=INK))
    P.append(fitbox(60, 390, 340, 42, "hwirq 0: Пін GPIO_0 (кнопка живлення)", size=12, fill=RED_BG, stroke=POS))
    P.append(fitbox(60, 442, 340, 42, "hwirq 1: Пін GPIO_1 (акселерометр INT)", size=12, fill=WARM_BG, stroke=GOLD))
    P.append(fitbox(60, 494, 340, 42, "hwirq 2..31: Решта пінів роз'єму", size=11, fill=GREY_BG, stroke=MUTED))

    # Контролер 3: PCI MSI
    P.append(rect(40, 575, 380, 85, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(230, 602, "PCIe MSI Domain", size=13, bold=True, color=INK))
    P.append(fitbox(60, 615, 340, 36, "MSI Message / Vector 0..2047", size=11, fill=GREY_BG, stroke=MUTED))

    # Центральний блок: irq_domain
    P.append(rect(460, 160, 250, 430, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    P.append(text(585, 195, "struct irq_domain", size=15, bold=True, color=INK))
    P.append(text(585, 220, "Трансляція та ізоляція", size=12, color=MUTED))
    P.append(line(480, 235, 690, 235, color=MUTED, sw=1))

    P.append(fitbox(475, 250, 220, 65, "Linear Domain\n(масив revmap[hwirq])\nO(1) прямий індекс", size=11, fill=GREEN_BG, stroke=FIELD))
    P.append(fitbox(475, 330, 220, 65, "Radix Tree / XArray\n(для розріджених hwirq)\nO(log N) пошук", size=11, fill=BLUE_BG, stroke=NEG))
    P.append(fitbox(475, 410, 220, 65, "Domain Ops\n.map() / .xlate()\n.alloc() / .translate()", size=11, fill=WARM_BG, stroke=GOLD))
    P.append(fitbox(475, 490, 220, 85, "irq_find_mapping()\nвхід: (domain, hwirq)\nвихід: virq (Linux IRQ)\nШвидкий гарячий шлях", size=11, fill=FILL, stroke=LINE))

    # Правий блок: Ядро Linux (virq)
    P.append(rect(750, 75, 410, 585, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(955, 105, "Масив дескрипторів struct irq_desc", size=13, bold=True, color=INK))

    P.append(fitbox(770, 130, 370, 85, "virq 17 (UART)\nirq_data -> hwirq=32, chip=gic_chip\nhandler = handle_fasteoi_irq\naction -> uart_interrupt()", size=11, fill=GREEN_BG, stroke=FIELD))

    P.append(fitbox(770, 230, 370, 85, "virq 18 (I2C Controller)\nirq_data -> hwirq=33, chip=gic_chip\nhandler = handle_fasteoi_irq\naction -> i2c_dw_isr()", size=11, fill=BLUE_BG, stroke=NEG))

    P.append(fitbox(770, 330, 370, 85, "virq 64 (Power Button)\nirq_data -> hwirq=0, chip=gpio_chip\nhandler = handle_level_irq\naction -> gpio_keys_isr()", size=11, fill=RED_BG, stroke=POS))

    P.append(fitbox(770, 430, 370, 85, "virq 65 (Accelerometer INT)\nirq_data -> hwirq=1, chip=gpio_chip\nhandler = handle_edge_irq\naction -> mpu6050_isr()", size=11, fill=WARM_BG, stroke=GOLD))

    P.append(fitbox(770, 530, 370, 110, "virq 128.. (NVMe MSI-X)\nirq_data -> hwirq=0x10, chip=pci_msi_chip\nhandler = handle_edge_irq\naction -> nvme_irq()", size=11, fill=GREY_BG, stroke=MUTED))

    # Стрілки відображення
    P.append(arrow(400, 193, 475, 275, color=FIELD, sw=2))
    P.append(arrow(695, 275, 770, 172, color=FIELD, sw=2))

    P.append(arrow(400, 245, 475, 285, color=NEG, sw=2))
    P.append(arrow(695, 285, 770, 272, color=NEG, sw=2))

    P.append(arrow(400, 411, 475, 360, color=POS, sw=2))
    P.append(arrow(695, 360, 770, 372, color=POS, sw=2))

    P.append(arrow(400, 463, 475, 370, color=GOLD, sw=2))
    P.append(arrow(695, 370, 770, 472, color=GOLD, sw=2))

    render(os.path.join(OUT, "hwirq-to-virq-mapping.svg"), W, H, *P,
           title="Відображення апаратних переривань hwirq у єдиний простір virq Linux")


# ── 2. Ієрархічні домени переривань (Hierarchical IRQ Domains) ────────────────
def fig_hierarchical_domains():
    W, H = 1200, 620
    P = []

    # Верхній заголовок
    P.append(text(600, 50, "Ієрархія доменів (MSI / IOMMU / GIC / CPU)", size=15, bold=True, color=INK))

    # Блоки рівнів ієрархії
    layers = [
        ("Рівень пристрою (PCIe Endpoint / NVMe)",
         100, 1000, 95,
         [("Пристрій PCIe (NVMe / NIC)", 130, 290, "Генерує MSI-X запис у пам'ять\nАдреса: 0xFEE00000 / Дані: 0x4021", RED_BG, POS),
          ("Периферія ядра (I2C / UART)", 460, 290, "Сигнал на фізичному дроті SPI\nЛінія hwirq=48", GREEN_BG, FIELD),
          ("Зовнішній GPIO розширювач", 790, 280, "Спад на піні GPIO_5\nПерериває через I2C шину", WARM_BG, GOLD)]),

        ("Проміжні домени трансформації",
         235, 1000, 95,
         [("PCIe MSI irq_domain", 130, 290, "struct irq_data (рівень MSI)\nchip: pci_msi_irq_chip\nhwirq: 0 (MSI vector index)", RED_BG, POS),
          ("Direct Wire Mapping", 460, 290, "Пряма трансляція ліній без\nпроміжних контролерів", GREY_BG, MUTED),
          ("GPIO irq_domain (nested/chained)", 790, 280, "struct irq_data (рівень GPIO)\nchip: max7301_chip\nhwirq: 5", WARM_BG, GOLD)]),

        ("Домен трансляції повідомлень / переривань",
         370, 1000, 95,
         [("GICv3 ITS / IOMMU IR Domain", 130, 290, "struct irq_data (рівень ITS)\nchip: gic_its_irq_chip\nТрансляція DeviceID + EventID -> LPI", BLUE_BG, NEG),
          ("GIC Distributor Domain", 460, 290, "struct irq_data (рівень SPI/Distributor)\nchip: gic_data.chip\nhwirq: 48 (GIC SPI 16)", GREEN_BG, FIELD),
          ("GIC SPI Parent Domain", 790, 280, "struct irq_data (батьківський SPI)\nchip: gic_data.chip\nhwirq: 54 (GIC SPI 22)", WARM_BG, GOLD)]),

        ("Кореневий домен та інтерфейс CPU",
         505, 1000, 85,
         [("Кореневий апаратний контролер (GIC Distributor / Core APIC)", 130, 940,
           "struct irq_desc (єдиний virq у ядрі) -> generic flow handler (handle_fasteoi_irq / handle_edge_irq)\nКаскадний виклик операцій: parent_data->chip->irq_mask() -> ... -> chip->irq_mask()",
           FILL, LINE)])
    ]

    for title, y, w, h, items in layers:
        P.append(rect(100, y, w, h, fill="#fcfdfe", stroke=MUTED, sw=1, rx=6))
        P.append(text(120, y + 20, title, size=11, bold=True, color=MUTED, anchor="start"))
        for name, ix, iw, desc, bg, stroke in items:
            P.append(fitbox(ix, y + 28, iw, h - 36, f"{name}\n{desc}", size=11, fill=bg, stroke=stroke, sw=1.5))

    # Стрілки ієрархічного зв'язку
    P.append(arrow(275, 195, 275, 235, color=POS, sw=2))
    P.append(arrow(275, 330, 275, 370, color=NEG, sw=2))
    P.append(arrow(275, 465, 350, 505, color=LINE, sw=2))

    P.append(arrow(605, 195, 605, 235, color=FIELD, sw=2))
    P.append(arrow(605, 330, 605, 370, color=FIELD, sw=2))
    P.append(arrow(605, 465, 600, 505, color=LINE, sw=2))

    P.append(arrow(930, 195, 930, 235, color=GOLD, sw=2))
    P.append(arrow(930, 330, 930, 370, color=GOLD, sw=2))
    P.append(arrow(930, 465, 850, 505, color=LINE, sw=2))

    render(os.path.join(OUT, "hierarchical-domains.svg"), W, H, *P,
           title="Ієрархічні домени переривань: зв'язок шарів від шини до ядра")


# ── 3. Поведінка Generic Flow Handlers ────────────────────────────────────────
def fig_generic_flow_handlers():
    W, H = 1200, 640
    P = []

    # Заголовок
    P.append(text(600, 45, "Алгоритми стандартних обробників потоку (Generic IRQ Flow Handlers)", size=15, bold=True, color=INK))

    # 1. Level-triggered
    P.append(rect(50, 75, 340, 530, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(220, 105, "handle_level_irq()", size=14, bold=True, color=POS))
    P.append(text(220, 125, "Для переривань за рівнем напруги", size=11, color=MUTED))

    steps_level = [
        ("1. Захоплення raw_spin_lock", "Блокування дескриптора desc->lock", GREY_BG, MUTED),
        ("2. mask_ack_irq()", "Маскування в chip->irq_mask()\n+ квитування chip->irq_ack()\n(усуває шторм переривань)", RED_BG, POS),
        ("3. Перевірка прапорців", "Чи лінія не відключена (IRQD_IRQ_DISABLED)?", GREY_BG, MUTED),
        ("4. handle_irq_event()", "Зняття замка -> виклик ISR драйвера\naction->handler(irq, dev_id)", GREEN_BG, FIELD),
        ("5. cond_unmask_irq()", "Захоплення замка -> розмаскування\nchip->irq_unmask(), якщо лінія активна", WARM_BG, GOLD),
        ("6. Звільнення замка", "Завершення обробки переривання", GREY_BG, MUTED)
    ]
    y = 145
    for st, dsc, bg, stroke in steps_level:
        P.append(fitbox(70, y, 300, 64, f"{st}\n{dsc}", size=11, fill=bg, stroke=stroke))
        y += 72

    # 2. Edge-triggered
    P.append(rect(430, 75, 340, 530, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(600, 105, "handle_edge_irq()", size=14, bold=True, color=GOLD))
    P.append(text(600, 125, "Для переривань за фронтом сигналу", size=11, color=MUTED))

    steps_edge = [
        ("1. Захоплення raw_spin_lock", "Блокування дескриптора desc->lock", GREY_BG, MUTED),
        ("2. chip->irq_ack()", "Негайне квитування фронту в контролері\n(маскування НЕ робиться!)", WARM_BG, GOLD),
        ("3. Перевірка IRQS_PENDING", "Якщо інше ядро вже обробляє цей IRQ —\nставимо IRQS_PENDING і виходимо", BLUE_BG, NEG),
        ("4. Цикл handle_irq_event()", "Виклик ISR драйвера action->handler()\nпоки з'являються повторні фронти!", GREEN_BG, FIELD),
        ("5. Очищення стану", "Скидання прапорця IRQS_PENDING", GREY_BG, MUTED),
        ("6. Звільнення замка", "Завершення обробки", GREY_BG, MUTED)
    ]
    y = 145
    for st, dsc, bg, stroke in steps_edge:
        P.append(fitbox(450, y, 300, 64, f"{st}\n{dsc}", size=11, fill=bg, stroke=stroke))
        y += 72

    # 3. Fast EOI
    P.append(rect(810, 75, 340, 530, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(980, 105, "handle_fasteoi_irq()", size=14, bold=True, color=FIELD))
    P.append(text(980, 125, "Сучасні контролери (ARM GIC, x86 APIC)", size=11, color=MUTED))

    steps_fasteoi = [
        ("1. Захоплення raw_spin_lock", "Блокування дескриптора desc->lock", GREY_BG, MUTED),
        ("2. Без маскування на вході", "Апаратний контролер сам тримає\nстан переривання Active у процесорі", BLUE_BG, NEG),
        ("3. handle_irq_event()", "Зняття замка -> прямий виклик\naction->handler(irq, dev_id)", GREEN_BG, FIELD),
        ("4. Захоплення замка", "Повернення під захист desc->lock", GREY_BG, MUTED),
        ("5. chip->irq_eoi()", "Єдиний швидкий сигнал End-Of-Interrupt\n(наприклад, запис у ICC_EOIR1_EL1)", FIELD, FIELD),
        ("6. Звільнення замка", "Контролер переводить стан Active->Inactive", GREY_BG, MUTED)
    ]
    y = 145
    for st, dsc, bg, stroke in steps_fasteoi:
        P.append(fitbox(830, y, 300, 64, f"{st}\n{dsc}", size=11, fill=bg, stroke=stroke))
        y += 72

    render(os.path.join(OUT, "generic-flow-handlers.svg"), W, H, *P,
           title="Порівняння generic flow handlers: Level, Edge та FastEOI")


# ── 4. Розпізнавання та зв'язування з Device Tree ─────────────────────────────
def fig_devicetree_resolution():
    W, H = 1200, 600
    P = []

    P.append(text(600, 45, "Шлях трансляції переривання від вузла Device Tree до номера Linux", size=15, bold=True, color=INK))

    # Ліва колонка: Device Tree Source (DTS)
    P.append(rect(40, 75, 360, 495, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(220, 105, "1. Опис у Device Tree (.dts)", size=13, bold=True, color=INK))

    dt_text = (
        "gic: interrupt-controller@2c001000 {\n"
        "    compatible = \"arm,gic-400\";\n"
        "    #interrupt-cells = <3>;\n"
        "    interrupt-controller;\n"
        "};\n\n"
        "serial@1c28000 {\n"
        "    compatible = \"ns16550a\";\n"
        "    interrupt-parent = <&gic>;\n"
        "    interrupts = <GIC_SPI 32\n"
        "                 IRQ_TYPE_LEVEL_HIGH>;\n"
        "};"
    )
    P.append(fitbox(55, 125, 330, 220, dt_text, size=11, fill="#ffffff", stroke=LINE))

    P.append(fitbox(55, 360, 330, 195,
                    "Ключові властивості:\n"
                    "• interrupt-controller: оголошує домен\n"
                    "• #interrupt-cells = <3>: формат кортежу\n"
                    "  [тип, номер, прапорці фронту/рівня]\n"
                    "• interrupt-parent: посилання на контролер\n"
                    "• interrupts: параметри лінії пристрою", size=11, fill=WARM_BG, stroke=GOLD))

    # Середня колонка: Ядро Linux (Трансляція)
    P.append(rect(430, 75, 380, 495, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(620, 105, "2. Ядро Linux: of_irq_get()", size=13, bold=True, color=INK))

    steps_core = [
        ("of_irq_parse_one(dev->of_node, 0, &fwspec)",
         "Парсинг властивості interrupts, знаходження вузла\ninterrupt-parent і заповнення struct irq_fwspec"),
        ("irq_find_matching_fwspec(&fwspec)",
         "Пошук відповідного struct irq_domain за fwnode"),
        ("domain->ops->translate(&fwspec, &hwirq, &type)",
         "Виклик драйверного кольбеку: перетворення\n<GIC_SPI 32> у hwirq = 32 + 32 = 64 (SPI зміщення)"),
        ("irq_create_mapping(domain, hwirq)",
         "Якщо virq ще не виділено -> irq_domain_alloc_descs()\n-> domain->ops->map() -> прив'язка chip + handler")
    ]
    y = 125
    for fn, dsc in steps_core:
        P.append(fitbox(445, y, 350, 95, f"{fn}\n\n{dsc}", size=11, fill=BLUE_BG, stroke=NEG))
        y += 105

    # Права колонка: Драйвер пристрою
    P.append(rect(840, 75, 320, 495, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    P.append(text(1000, 105, "3. Драйвер пристрою", size=13, bold=True, color=INK))

    driver_code = (
        "// У функції probe():\n"
        "int irq = platform_get_irq(pdev, 0);\n"
        "// Повертає virq = 42\n\n"
        "devm_request_irq(&pdev->dev,\n"
        "    irq,\n"
        "    uart_interrupt,\n"
        "    0,\n"
        "    \"serial-uart\",\n"
        "    port);\n\n"
        "// Драйвер НЕ знає про hwirq,\n"
        "// GIC чи регістри контролера.\n"
        "// Він оперує лише virq = 42!"
    )
    P.append(fitbox(855, 125, 290, 240, driver_code, size=11, fill="#ffffff", stroke=FIELD))

    P.append(fitbox(855, 380, 290, 175,
                    "Результат абстракції:\n"
                    "Драйвер повністю переносимий між\n"
                    "x86 (APIC/MSI), ARM (GIC),\n"
                    "RISC-V (PLIC) та MIPS.\n"
                    "Уся апаратна специфіка прихована\n"
                    "всередині irq_domain та irq_chip.", size=11, fill=GREEN_BG, stroke=FIELD))

    # Стрілки переходу
    P.append(arrow(385, 235, 445, 170, color=LINE, sw=2))
    P.append(arrow(795, 445, 855, 245, color=FIELD, sw=2))

    render(os.path.join(OUT, "devicetree-irq-resolution.svg"), W, H, *P,
           title="Трансляція Device Tree: від опису контролера до виділення Linux virq")


if __name__ == "__main__":
    fig_hwirq_to_virq()
    fig_hierarchical_domains()
    fig_generic_flow_handlers()
    fig_devicetree_resolution()
    print("All figures generated successfully.")
