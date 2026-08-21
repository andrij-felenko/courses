# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми devm-managed-resources."""

import sys
import os

# scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, rect, text, mtext, textbox, fitbox, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)


def fig_devres_node_layout(out_path):
    """Структура struct device, devres_head та анатомія struct devres_node у пам'яті."""
    w, h = 860, 420
    frags = []

    # Тло / контур struct device
    frags.append(rect(20, 50, 240, 330, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(140, 80, "struct device", size=15, bold=True, color=INK))
    frags.append(line(20, 95, 260, 95, color=MUTED, sw=1))

    dev_fields = [
        ("kobj", "struct kobject"),
        ("init_name", "const char *"),
        ("driver", "struct device_driver *"),
        ("devres_lock", "spinlock_t"),
        ("devres_head", "struct list_head"),
    ]
    for i, (fn, ft) in enumerate(dev_fields):
        y_pos = 130 + i * 46
        hl = (fn == "devres_head")
        bg_col = "#e2e8f0" if not hl else "#dbeafe"
        strk_col = LINE if not hl else NEG
        frags.append(rect(35, y_pos - 18, 210, 36, fill=bg_col, stroke=strk_col, sw=1.5 if hl else 1, rx=4))
        frags.append(text(45, y_pos + 4, fn, size=13, bold=hl, color=INK if not hl else NEG, anchor="start"))
        frags.append(text(235, y_pos + 4, ft, size=11, italic=True, color=MUTED, anchor="end"))

    # Стрілка від devres_head до списку вузлів
    frags.append(arrow(245, 314, 305, 314, color=NEG, sw=2))

    # Блок об'єкта devres у пам'яті (Node + Payload)
    frags.append(rect(310, 50, 520, 330, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(570, 80, "Блок керованого ресурсу в пам'яті (SLAB / kmalloc)", size=15, bold=True, color=INK))
    frags.append(line(310, 95, 830, 95, color=MUTED, sw=1))

    # Секція 1: struct devres_node (Службовий заголовок)
    frags.append(rect(330, 115, 480, 130, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(570, 138, "struct devres_node (Службовий заголовок)", size=13, bold=True, color=NEG))
    
    frags.append(rect(345, 155, 220, 30, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(355, 175, "entry: struct list_head", size=12, color=INK, anchor="start"))

    frags.append(rect(580, 155, 215, 30, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(590, 175, "release: dr_release_t", size=12, bold=True, color=POS, anchor="start"))

    frags.append(rect(345, 195, 450, 32, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(355, 216, "name: const char * (наприклад, \"devm_kzalloc_release\")", size=11, color=MUTED, anchor="start"))

    # Секція 2: Корисне навантаження (Resource Data Payload)
    frags.append(rect(330, 260, 480, 100, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(570, 285, "Дані ресурсу: u8 data[] (гнучкий масив / корисне навантаження)", size=13, bold=True, color=FIELD))
    frags.append(text(570, 315, "Пам'ять структури драйвера / iomem mapping / struct irq_action", size=12, color=INK))
    frags.append(text(570, 340, "Повертається викликом devm_kzalloc() як чистий вказівник void *", size=11, italic=True, color=MUTED))

    # Покажчики зміщення devres_to_node та node_to_devres
    frags.append(line(318, 120, 318, 240, color=NEG, sw=2))
    frags.append(line(318, 265, 318, 355, color=FIELD, sw=2))

    render(out_path, w, h, *frags, title="Анатомія керованого ресурсу devres у ядрі Linux")


def fig_probe_unwind_phases(out_path):
    """Фази життєвого циклу probe / remove та автоматичне розмотування LIFO при збої."""
    w, h = 880, 460
    frags = []

    # Верхній сценарій: Успішний probe() та наступний remove()
    frags.append(rect(20, 45, 840, 175, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(35, 70, "1. Успішне завантаження та вивантаження драйвера (probe → remove)", size=14, bold=True, color=INK, anchor="start"))

    steps_ok = [
        ("devm_kzalloc()", "Стек: [Пам'ять]"),
        ("devm_ioremap_resource()", "Стек: [Пам'ять, MMIO]"),
        ("devm_clk_get_enabled()", "Стек: [Пам'ять, MMIO, Clk]"),
        ("devm_request_irq()", "Стек: [Пам'ять, MMIO, Clk, IRQ]"),
    ]
    for i, (fn, st) in enumerate(steps_ok):
        x = 40 + i * 195
        frags.append(rect(x, 90, 185, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
        frags.append(text(x + 92, 112, fn, size=11, bold=True, color=INK))
        frags.append(text(x + 92, 132, st, size=10, color=MUTED))
        if i < 3:
            frags.append(arrow(x + 185, 117, x + 195, 117, color=LINE, sw=1.5))

    # Стрілка до Remove
    frags.append(rect(40, 155, 800, 50, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(440, 175, "Фаза remove() або unbind: devres_release_all() автоматично вивільняє LIFO", size=12, bold=True, color=NEG))
    frags.append(text(440, 193, "Порядок звільнення: 1. free_irq  →  2. clk_disable_unprepare  →  3. iounmap  →  4. kfree", size=11, color=INK))

    # Нижній сценарій: Помилка посеред probe()
    frags.append(rect(20, 240, 840, 195, fill="#fef2f2", stroke=POS, sw=1.2, rx=8))
    frags.append(text(35, 265, "2. Збій посеред probe(): автоматичне аварійне розмотування (Rollback)", size=14, bold=True, color=POS, anchor="start"))

    steps_err = [
        ("devm_kzalloc()", "OK", FIELD),
        ("devm_ioremap_resource()", "OK", FIELD),
        ("devm_clk_get_enabled()", "OK", FIELD),
        ("devm_request_irq()", "ПОМИЛКА (-EBUSY)", POS),
    ]
    for i, (fn, st, col) in enumerate(steps_err):
        x = 40 + i * 195
        bg_col = "#ffffff" if col == FIELD else "#fee2e2"
        frags.append(rect(x, 285, 185, 55, fill=bg_col, stroke=col, sw=1.5, rx=6))
        frags.append(text(x + 92, 307, fn, size=11, bold=True, color=INK))
        frags.append(text(x + 92, 327, st, size=10, bold=(col == POS), color=col))
        if i < 3:
            frags.append(arrow(x + 185, 312, x + 195, 312, color=LINE, sw=1.5))

    # Пояснення автоматичного розмотування
    frags.append(rect(40, 355, 800, 65, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(440, 377, "Драйвер повертає -EBUSY; ядро викликає devres_release_all(dev)", size=12, bold=True, color=POS))
    frags.append(text(440, 396, "Звільняються лише успішно зареєстровані ресурси: Clk → MMIO → Пам'ять", size=11, color=INK))
    frags.append(text(440, 412, "Жодних витоків ресурсів, відсутня потреба в заплутаних goto err_*", size=11, italic=True, color=MUTED))

    render(out_path, w, h, *frags, title="Фази реєстрації та автоматичного LIFO-очищення devres")


def fig_devres_group_hierarchy(out_path):
    """Механізм груп ресурсів: devres_open_group, вкладеність та devres_release_group."""
    w, h = 860, 380
    frags = []

    # Загальна рамка списку devres_head
    frags.append(rect(20, 50, 820, 305, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(430, 75, "Список devres_head з активною групою ресурсів", size=15, bold=True, color=INK))

    # Базові ресурси поза групою
    frags.append(rect(40, 100, 160, 80, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(120, 130, "Базовий стан", size=12, bold=True, color=NEG))
    frags.append(text(120, 155, "devm_kzalloc(priv)", size=11, color=INK))

    frags.append(arrow(200, 140, 230, 140, color=LINE, sw=1.5))

    # Група ресурсів (рамка групи)
    frags.append(rect(230, 95, 390, 175, fill="#ffffff", stroke=FIELD, sw=2, rx=8))
    frags.append(text(425, 118, "Група ресурсів: devres_open_group(dev, id, GFP_KERNEL)", size=12, bold=True, color=FIELD))

    # Вузол 1 у групі
    frags.append(rect(250, 140, 160, 60, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(330, 163, "Ресурс групи A", size=11, bold=True, color=INK))
    frags.append(text(330, 183, "devm_ioremap(...)", size=10, color=MUTED))

    frags.append(arrow(410, 170, 440, 170, color=FIELD, sw=1.5))

    # Вузол 2 у групі
    frags.append(rect(440, 140, 160, 60, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(520, 163, "Ресурс групи B", size=11, bold=True, color=INK))
    frags.append(text(520, 183, "devm_clk_get(...)", size=10, color=MUTED))

    frags.append(text(425, 230, "Закриття групи: devres_close_group(dev, id)", size=11, italic=True, color=MUTED))
    frags.append(text(425, 252, "При збої динамічної фази: devres_release_group(dev, id)", size=11, bold=True, color=POS))

    frags.append(arrow(620, 140, 650, 140, color=LINE, sw=1.5))

    # Наступні ресурси
    frags.append(rect(650, 100, 170, 80, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(735, 130, "Пізніший ресурс", size=12, bold=True, color=NEG))
    frags.append(text(735, 155, "devm_request_irq()", size=11, color=INK))

    # Пояснення знизу
    frags.append(rect(40, 285, 780, 55, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    frags.append(text(430, 308, "Групи дозволяють відкочувати окремі підсистеми або багатофазну ініціалізацію", size=12, bold=True, color=INK))
    frags.append(text(430, 326, "Вивільнення групи знищує лише вузли всередині неї, зберігаючи базові ресурси драйвера", size=11, color=MUTED))

    render(out_path, w, h, *frags, title="Організація груп керованих ресурсів (devres groups)")


def fig_order_of_destruction_pitfall(out_path):
    """Типовий підводний камінь: порушення порядку деініціалізації та Use-After-Free."""
    w, h = 880, 420
    frags = []

    # Ліва колонка: Небезпечний сценарій (Crash / UAF)
    frags.append(rect(20, 50, 410, 345, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(225, 78, "Небезпечно: Ручний kfree + devm переривання", size=13, bold=True, color=POS))

    items_bad = [
        ("1. devm_kzalloc()", "Пам'ять стану priv під керуванням devm", "#ffffff", LINE),
        ("2. devm_request_irq(..., priv)", "IRQ-обробник тримає вказівник на priv", "#ffffff", LINE),
        ("3. remove(): ручний kfree(priv)", "ПАМ'ЯТЬ ЗВІЛЬНЕНО ДО ВІДВ'ЯЗКИ IRQ!", "#fee2e2", POS),
        ("4. Асинхронне апаратне переривання", "ISR звертається до вже звільненого priv->regs", "#fee2e2", POS),
        ("5. Результат: Kernel Oops / Panic", "Use-After-Free через порушення черговості", "#fee2e2", POS),
    ]
    for i, (title_text, sub_text, bg_col, strk_col) in enumerate(items_bad):
        y = 105 + i * 54
        frags.append(rect(35, y, 380, 44, fill=bg_col, stroke=strk_col, sw=1.2, rx=4))
        frags.append(text(45, y + 18, title_text, size=11, bold=True, color=INK if strk_col != POS else POS, anchor="start"))
        frags.append(text(45, y + 34, sub_text, size=10, color=MUTED if strk_col != POS else POS, anchor="start"))

    # Права колонка: Безпечний сценарій (RAII / devm LIFO або action)
    frags.append(rect(450, 50, 410, 345, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(655, 78, "Безпечно: Усі ресурси через devm (LIFO) або Action", size=13, bold=True, color=FIELD))

    items_good = [
        ("1. devm_kzalloc()", "Пам'ять виділено першою (звільниться останньою)", "#ffffff", LINE),
        ("2. devm_request_irq(..., priv)", "IRQ зареєстровано другим (звільниться першим)", "#ffffff", LINE),
        ("3. remove(): cancel_work_sync()", "Зупинка асинхронних черг перед виходом", "#ffffff", FIELD),
        ("4. devres_release_all() (LIFO)", "Крок А: free_irq(dev, priv) вимикає обробник", "#dcfce7", FIELD),
        ("5. devres_release_all() (LIFO)", "Крок Б: kfree(priv) безпечно чистить пам'ять", "#dcfce7", FIELD),
    ]
    for i, (title_text, sub_text, bg_col, strk_col) in enumerate(items_good):
        y = 105 + i * 54
        frags.append(rect(465, y, 380, 44, fill=bg_col, stroke=strk_col, sw=1.2, rx=4))
        frags.append(text(475, y + 18, title_text, size=11, bold=True, color=INK if strk_col != FIELD else FIELD, anchor="start"))
        frags.append(text(475, y + 34, sub_text, size=10, color=MUTED if strk_col != FIELD else INK, anchor="start"))

    render(out_path, w, h, *frags, title="Порядок руйнування ресурсів: ризик Use-After-Free та коректне LIFO")


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    fig_devres_node_layout(os.path.join(img_dir, "devres-node-layout.svg"))
    fig_probe_unwind_phases(os.path.join(img_dir, "probe-unwind-phases.svg"))
    fig_devres_group_hierarchy(os.path.join(img_dir, "devres-group-hierarchy.svg"))
    fig_order_of_destruction_pitfall(os.path.join(img_dir, "order-of-destruction-pitfall.svg"))
    print("All SVGs generated successfully.")


if __name__ == "__main__":
    main()
