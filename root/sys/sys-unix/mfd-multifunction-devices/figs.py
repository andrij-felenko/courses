#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор архітектурних діаграм для теми MFD (Multi-Function Devices)."""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))

try:
    from svgkit import *
except ImportError:
    print("Помилка: не знайдено svgkit у scripts/")
    sys.exit(1)

def draw_pmic_hardware_to_kernel_model():
    """Діаграма 1: Фізичний PMIC на шині I2C та його декомпозиція в моделі ядра Linux."""
    w, h = 980, 540
    frags = []

    # Тло та секції
    frags.append(rect(20, 20, 420, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(230, 48, "Апаратний рівень (PMIC на платі)", size=14, bold=True, color="#0f172a"))

    frags.append(rect(480, 20, 480, 500, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(720, 48, "Рівень ядра Linux (Підсистема MFD)", size=14, bold=True, color="#14532d"))

    # Фізичний чип PMIC
    frags.append(rect(40, 75, 380, 425, fill="#ffffff", stroke="#64748b", sw=1.8, rx=6))
    frags.append(text(230, 100, "Фізична мікросхема PMIC (I2C addr: 0x34)", size=13, bold=True, color="#1e293b"))

    # Апаратні блоки всередині PMIC
    hw_blocks = [
        ("BUCK / LDO Регулятори", "DC-DC перетворювачі 0.8V–3.3V", 130, "#fef3c7", "#d97706"),
        ("GPIO Expander", "Цифрові лінії вводу/виводу", 200, "#e0f2fe", "#0284c7"),
        ("RTC Годинник", "32.768 кГц лічильник часу + Alarm", 270, "#f3e8ff", "#9333ea"),
        ("Power Key / ONKEY", "Апаратний тригер кнопки живлення", 340, "#fee2e2", "#dc2626"),
        ("Battery Charger & ADC", "Контролер заряду CC/CV + АЦП", 410, "#ccfbf1", "#0d9488"),
    ]

    for title, desc, y, fill_c, stroke_c in hw_blocks:
        frags.append(rect(55, y, 350, 54, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(230, y + 22, title, size=12, bold=True, color="#0f172a"))
        frags.append(text(230, y + 42, desc, size=10, color="#475569"))

    # Ядро: Батьківський MFD драйвер
    frags.append(rect(500, 75, 440, 105, fill="#ffffff", stroke="#059669", sw=1.8, rx=6))
    frags.append(text(720, 98, "Батьківський MFD Драйвер (drivers/mfd/)", size=13, bold=True, color="#065f46"))
    frags.append(rect(515, 115, 195, 52, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    frags.append(text(612, 136, "Спільний Regmap", size=11, bold=True, color="#047857"))
    frags.append(text(612, 154, "regmap_i2c / RMW-замки", size=10, color="#065f46"))

    frags.append(rect(725, 115, 200, 52, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=4))
    frags.append(text(825, 136, "Демаршрутизатор IRQ", size=11, bold=True, color="#047857"))
    frags.append(text(825, 154, "regmap-irq / irq_domain", size=10, color="#065f46"))

    # Лінії зв'язку: Фізичні лінії до MFD ядра
    frags.append(arrow(390, 100, 500, 100, color="#2563eb", sw=2.0))
    frags.append(text(445, 90, "Шина I2C", size=10, bold=True, color="#1d4ed8"))

    frags.append(arrow(390, 470, 445, 470, color="#dc2626", sw=1.8))
    frags.append(line(445, 470, 445, 140, color="#dc2626", sw=1.8))
    frags.append(arrow(445, 140, 500, 140, color="#dc2626", sw=1.8))
    frags.append(text(445, 485, "INT# (IRQ)", size=10, bold=True, color="#b91c1c"))

    # Дочірні Platform пристрої та підсистеми ядра
    kernel_children = [
        ("drivers/regulator/", "struct platform_device 'pmic-regulator'", 210, "#fef3c7", "#d97706"),
        ("drivers/gpio/", "struct platform_device 'pmic-gpio'", 270, "#e0f2fe", "#0284c7"),
        ("drivers/rtc/", "struct platform_device 'pmic-rtc'", 330, "#f3e8ff", "#9333ea"),
        ("drivers/input/misc/", "struct platform_device 'pmic-onkey'", 390, "#fee2e2", "#dc2626"),
        ("drivers/power/supply/", "struct platform_device 'pmic-charger'", 450, "#ccfbf1", "#0d9488"),
    ]

    # Вертикальна шина розгалуження від MFD
    frags.append(line(505, 180, 505, 474, color="#059669", sw=1.6))

    for sys_dir, pdev_name, y, fill_c, stroke_c in kernel_children:
        frags.append(rect(530, y, 400, 48, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(730, y + 20, sys_dir, size=11, bold=True, color="#0f172a"))
        frags.append(text(730, y + 38, pdev_name, size=10, color="#334155"))
        # Горизонтальний відвід від шини
        frags.append(arrow(505, y + 24, 530, y + 24, color="#059669", sw=1.4))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "pmic-hardware-to-kernel-model.svg"), w, h, *frags, title="Архітектура MFD: від фізичного PMIC до дочірніх драйверів ядра")

def draw_mfd_regmap_and_irq_demux():
    """Діаграма 2: Розподіл доступу до регістрів через Regmap та демультиплексування переривань."""
    w, h = 980, 520
    frags = []

    # Контейнер Regmap
    frags.append(rect(20, 20, 450, 480, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(245, 48, "Спільний доступ до регістрів: Regmap", size=14, bold=True, color="#0f172a"))

    # Дочірні драйвери зліва
    frags.append(rect(35, 75, 160, 45, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(115, 102, "Драйвер Regulator", size=11, bold=True, color="#92400e"))

    frags.append(rect(35, 135, 160, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    frags.append(text(115, 162, "Драйвер GPIO", size=11, bold=True, color="#075985"))

    frags.append(rect(35, 195, 160, 45, fill="#f3e8ff", stroke="#9333ea", sw=1.2, rx=4))
    frags.append(text(115, 222, "Драйвер RTC", size=11, bold=True, color="#6b21a8"))

    # Ядро Regmap
    frags.append(rect(240, 75, 215, 165, fill="#ffffff", stroke="#0284c7", sw=1.6, rx=6))
    frags.append(text(347, 98, "Ядро Regmap", size=12, bold=True, color="#0369a1"))
    frags.append(rect(252, 112, 190, 32, fill="#f0f9ff", stroke="#bae6fd", sw=1.0, rx=3))
    frags.append(text(347, 133, "Mutex (Блокування RMW)", size=10, bold=True, color="#0284c7"))
    frags.append(rect(252, 150, 190, 32, fill="#f0f9ff", stroke="#bae6fd", sw=1.0, rx=3))
    frags.append(text(347, 171, "Кеш регістрів (Rbtree/Maple)", size=10, bold=True, color="#0284c7"))
    frags.append(rect(252, 188, 190, 32, fill="#f0f9ff", stroke="#bae6fd", sw=1.0, rx=3))
    frags.append(text(347, 209, "regmap_bus (I2C адаптер)", size=10, bold=True, color="#0284c7"))

    frags.append(arrow(195, 97, 240, 110, color="#475569", sw=1.4))
    frags.append(arrow(195, 157, 240, 157, color="#475569", sw=1.4))
    frags.append(arrow(195, 217, 240, 205, color="#475569", sw=1.4))

    # Фізичний контролер I2C та чіп
    frags.append(rect(130, 265, 230, 55, fill="#e2e8f0", stroke="#475569", sw=1.4, rx=6))
    frags.append(text(245, 288, "Хост-адаптер I2C (SoC)", size=11, bold=True, color="#1e293b"))
    frags.append(text(245, 307, "i2c_transfer() транзакції", size=10, color="#475569"))
    frags.append(arrow(347, 240, 245, 265, color="#0284c7", sw=1.6))

    frags.append(rect(40, 355, 410, 120, fill="#ffffff", stroke="#0f172a", sw=1.8, rx=6))
    frags.append(text(245, 380, "Фізична карта регістрів PMIC (0x00–0xFF)", size=11, bold=True, color="#0f172a"))
    frags.append(rect(55, 400, 110, 55, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=3))
    frags.append(text(110, 422, "0x00–0x1F", size=10, bold=True, color="#78350f"))
    frags.append(text(110, 442, "BUCK / LDO", size=9, color="#78350f"))

    frags.append(rect(185, 400, 110, 55, fill="#e0f2fe", stroke="#0284c7", sw=1.0, rx=3))
    frags.append(text(240, 422, "0x20–0x2F", size=10, bold=True, color="#0369a1"))
    frags.append(text(240, 442, "GPIO", size=9, color="#0369a1"))

    frags.append(rect(315, 400, 115, 55, fill="#f3e8ff", stroke="#9333ea", sw=1.0, rx=3))
    frags.append(text(372, 422, "0x30–0x45", size=10, bold=True, color="#581c87"))
    frags.append(text(372, 442, "RTC / Alarm", size=9, color="#581c87"))

    frags.append(arrow(245, 320, 245, 355, color="#1e293b", sw=1.6))

    # Контейнер Regmap-IRQ
    frags.append(rect(490, 20, 470, 480, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(725, 48, "Розподіл переривань: regmap-irq", size=14, bold=True, color="#9a3412"))

    # Фізичний сигнал переривання
    frags.append(rect(510, 75, 430, 55, fill="#fee2e2", stroke="#ef4444", sw=1.4, rx=6))
    frags.append(text(725, 98, "Фізична лінія переривання PMIC INT#", size=11, bold=True, color="#991b1b"))
    frags.append(text(725, 117, "Сигнал LOW -> SoC Hard IRQ пробуджує потік", size=10, color="#7f1d1d"))

    # Потоковий обробник regmap_irq_thread
    frags.append(rect(510, 150, 430, 110, fill="#ffffff", stroke="#f97316", sw=1.6, rx=6))
    frags.append(text(725, 172, "Ядерний потік: regmap_irq_thread()", size=12, bold=True, color="#c2410c"))
    frags.append(text(725, 192, "1. Зчитування регістрів статусу INT_STS (I2C)", size=10, color="#334155"))
    frags.append(text(725, 212, "2. Маскування невикористаних бітів (INT_MASK)", size=10, color="#334155"))
    frags.append(text(725, 232, "3. Квитування подій у PMIC (Write-1-to-Clear)", size=10, color="#334155"))
    frags.append(text(725, 252, "4. Трансляція hwirq -> virq через irq_domain", size=10, color="#334155"))

    frags.append(arrow(725, 130, 725, 150, color="#dc2626", sw=1.6))

    # Виклик handle_nested_irq
    frags.append(rect(530, 280, 390, 40, fill="#ffedd5", stroke="#ea580c", sw=1.2, rx=4))
    frags.append(text(725, 305, "handle_nested_irq(virq) — диспетчер подій", size=11, bold=True, color="#9a3412"))
    frags.append(arrow(725, 260, 725, 280, color="#ea580c", sw=1.6))

    # Дочірні обробники переривань
    virq_handlers = [
        ("IRQ #104: BUCK1 Over-Current", "drivers/regulator/ ISR", 345, "#fef3c7", "#d97706"),
        ("IRQ #105: GPIO Key Pressed", "drivers/gpio/ ISR", 395, "#e0f2fe", "#0284c7"),
        ("IRQ #106: RTC Alarm Match", "drivers/rtc/ ISR", 445, "#f3e8ff", "#9333ea"),
    ]

    # Вертикальна шина розгалуження IRQ
    frags.append(line(520, 320, 520, 465, color="#ea580c", sw=1.6))
    frags.append(line(530, 300, 520, 300, color="#ea580c", sw=1.6))

    for v_title, v_desc, y, fill_c, stroke_c in virq_handlers:
        frags.append(rect(545, y, 375, 40, fill=fill_c, stroke=stroke_c, sw=1.0, rx=3))
        frags.append(text(645, y + 24, v_title, size=10, bold=True, color="#0f172a"))
        frags.append(text(830, y + 24, v_desc, size=9, color="#475569"))
        frags.append(arrow(520, y + 20, 545, y + 20, color="#ea580c", sw=1.4))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "mfd-regmap-and-irq-demux.svg"), w, h, *frags, title="Взаємодія Regmap та демультиплексування переривань regmap-irq")

def draw_device_tree_mfd_hierarchy():
    """Діаграма 3: Ієрархія вузлів Device Tree та їх зв'язок зі struct mfd_cell."""
    w, h = 980, 460
    frags = []

    frags.append(rect(20, 20, 450, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(245, 48, "Дерево пристроїв (Device Tree DTS)", size=14, bold=True, color="#0f172a"))

    # DTS вузол батька
    frags.append(rect(40, 75, 410, 70, fill="#ffffff", stroke="#0284c7", sw=1.6, rx=6))
    frags.append(text(245, 98, "pmic@34 (Батьківський вузол I2C)", size=12, bold=True, color="#0369a1"))
    frags.append(text(245, 118, "compatible = 'rohm,bd71837'; reg = <0x34>;", size=10, color="#475569"))
    frags.append(text(245, 134, "interrupt-controller; #interrupt-cells = <2>;", size=10, color="#475569"))

    dts_children = [
        ("regulators { compatible = 'rohm,bd71837-pmic'; ... }", 165, "#fef3c7", "#d97706"),
        ("gpio-controller { compatible = 'rohm,bd71837-gpio'; ... }", 225, "#e0f2fe", "#0284c7"),
        ("rtc { compatible = 'rohm,bd71837-rtc'; interrupts = <1 0>; }", 285, "#f3e8ff", "#9333ea"),
        ("power-button { compatible = 'rohm,bd71837-pwrkey'; ... }", 345, "#fee2e2", "#dc2626"),
    ]

    # Вертикальна лінія ієрархії дерева ліворуч
    frags.append(line(50, 145, 50, 368, color="#0284c7", sw=1.6))

    for dts_txt, y, fill_c, stroke_c in dts_children:
        frags.append(rect(70, y, 370, 46, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(255, y + 27, dts_txt, size=9, bold=True, color="#0f172a"))
        frags.append(arrow(50, y + 23, 70, y + 23, color="#0284c7", sw=1.4))

    # Зіставлення праворуч: Ядро Linux та struct mfd_cell
    frags.append(rect(490, 20, 470, 420, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(725, 48, "Зіставлення в ядрі: struct mfd_cell", size=14, bold=True, color="#14532d"))

    mfd_cells = [
        (".name = 'bd71837-pmic', .of_compatible = 'rohm,bd71837-pmic'", 165, "#fef3c7", "#d97706"),
        (".name = 'bd71837-gpio', .of_compatible = 'rohm,bd71837-gpio'", 225, "#e0f2fe", "#0284c7"),
        (".name = 'bd71837-rtc',  .of_compatible = 'rohm,bd71837-rtc'", 285, "#f3e8ff", "#9333ea"),
        (".name = 'bd71837-pwrkey',.of_compatible = 'rohm,bd71837-pwrkey'", 345, "#fee2e2", "#dc2626"),
    ]

    for cell_txt, y, fill_c, stroke_c in mfd_cells:
        frags.append(rect(510, y, 430, 46, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        frags.append(text(725, y + 27, cell_txt, size=9, bold=True, color="#0f172a"))
        frags.append(arrow(440, y + 23, 510, y + 23, color="#059669", sw=1.4))

    frags.append(rect(510, 75, 430, 70, fill="#ffffff", stroke="#059669", sw=1.6, rx=6))
    frags.append(text(725, 98, "mfd_add_devices() / mfd_match_of_node()", size=12, bold=True, color="#065f46"))
    frags.append(text(725, 118, "Прив'язує pdev->dev.of_node до дочірнього вузла DTS", size=10, color="#334155"))
    frags.append(text(725, 134, "Автоматично налаштовує переривання через irq_domain", size=10, color="#334155"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "device-tree-mfd-hierarchy.svg"), w, h, *frags, title="Ієрархія Device Tree та зіставлення з масивом mfd_cell")

if __name__ == "__main__":
    draw_pmic_hardware_to_kernel_model()
    draw_mfd_regmap_and_irq_demux()
    draw_device_tree_mfd_hierarchy()
    print("Усі SVG діаграми успішно згенеровано.")
