# -*- coding: utf-8 -*-
"""Генератор векторних SVG-ілюстрацій для теми «Периферія через регістри»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT,
    INK,
    MUTED,
    NEG,
    POS,
    arrow,
    esc,
    line,
    rect,
    render,
    text,
    textbox,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def gen_mmio_bus_path():
    """Фігура 1: Шлях MMIO — від інструкції процесора до транзистора."""
    w, h = 860, 310
    frags = []

    frags.append(text(w / 2, 28, "Шлях MMIO: від процесорної команди STR до затвора транзистора на ніжці", size=15, bold=True))

    # Блок 1: Ядро CPU
    frags.append(rect(25, 60, 160, 215, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(105, 88, "Ядро процесора", size=13, bold=True, color=INK))
    frags.append(text(105, 110, "ARM Cortex-M / RISC-V", size=10, color=MUTED))
    frags.append(rect(37, 130, 136, 65, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    frags.append(text(105, 155, "STR r0, [r1]", size=12, bold=True, color="#0f172a"))
    frags.append(text(105, 175, "r1 = 0x40020014", size=10, color=MUTED))
    frags.append(text(105, 235, "Адресна шина & Дані", size=10, color=MUTED))

    # Стрілка CPU -> AHB Bus Decoder
    frags.append(arrow(185, 165, 225, 165, color=INK, sw=2))
    frags.append(text(205, 153, "32-біт", size=9, color=MUTED))

    # Блок 2: AHB / APB Міст і Декодер
    frags.append(rect(225, 60, 165, 215, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(307, 88, "Шинний декодер & Міст", size=12, bold=True, color=INK))
    frags.append(text(307, 110, "AHB / APB Bridge", size=10, color=MUTED))
    frags.append(rect(237, 130, 141, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(307, 150, "Діапазон 0x40020000:", size=10, bold=True, color="#0369a1"))
    frags.append(text(307, 170, "GPIOA периферія", size=11, color=INK))
    frags.append(text(307, 190, "Сигнал PCLK & PENABLE", size=9, color=MUTED))
    frags.append(text(307, 240, "Маршрутизація до модуля", size=10, color=MUTED))

    # Стрілка AHB/APB -> GPIO Register
    frags.append(arrow(390, 165, 430, 165, color=INK, sw=2))
    frags.append(text(410, 153, "APB", size=9, color=MUTED))

    # Блок 3: Периферійний модуль GPIO (Регістр ODR)
    frags.append(rect(430, 60, 180, 215, fill="#ecfdf5", stroke="#10b981", sw=1.5, rx=6))
    frags.append(text(520, 88, "Модуль GPIO (Порт A)", size=13, bold=True, color="#065f46"))
    frags.append(text(520, 110, "Базова адреса: 0x40020000", size=9, color=MUTED))
    frags.append(rect(442, 130, 156, 75, fill="#ffffff", stroke="#6ee7b7", sw=1.0, rx=4))
    frags.append(text(520, 150, "Регістр ODR (+0x14)", size=11, bold=True, color="#047857"))
    frags.append(text(520, 170, "D-тригер біта 5: [ Q = 1 ]", size=11, bold=True, color=POS))
    frags.append(text(520, 190, "Апаратна засувка стану", size=9, color=MUTED))
    frags.append(text(520, 240, "Логічний рівень керування", size=10, color=MUTED))

    # Стрілка GPIO Register -> Output Stage (MOSFETs)
    frags.append(arrow(610, 165, 655, 165, color=POS, sw=2))
    frags.append(text(632, 153, "Q = 1", size=9, bold=True, color=POS))

    # Блок 4: Вихідний каскад CMOS Push-Pull і фізична ніжка
    frags.append(rect(655, 60, 180, 215, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(745, 88, "Вихідний каскад піна", size=13, bold=True, color="#991b1b"))
    frags.append(text(745, 110, "CMOS Push-Pull", size=10, color=MUTED))
    frags.append(rect(667, 130, 156, 85, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
    frags.append(text(745, 150, "P-MOSFET: ВІДЧИНЕНО", size=10, bold=True, color=POS))
    frags.append(text(745, 168, "N-MOSFET: ЗАЧИНЕНО", size=10, color=MUTED))
    frags.append(text(745, 188, "Вихідний пін PA5: 3.3 В", size=11, bold=True, color="#b91c1c"))
    frags.append(text(745, 204, "Струм іде у навантаження", size=9, color=MUTED))
    frags.append(text(745, 245, "Фізичний контакт чипа", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "mmio-bus-path.svg"), w, h, *frags)


def gen_atomic_vs_rmw():
    """Фігура 2: Порівняння Read-Modify-Write проти атомарного запису в BSRR/W1TS."""
    w, h = 860, 330
    frags = []

    frags.append(text(w / 2, 26, "Неатомарний Read-Modify-Write проти атомарного запису в BSRR / W1TS", size=15, bold=True))

    # Секція 1: Проблема Read-Modify-Write (RMW)
    frags.append(rect(20, 50, 820, 125, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=6))
    frags.append(text(430, 72, "1. Неатомарна операція: PORT->ODR |= (1 << 5)  [Read-Modify-Write: стан гонки]", size=12, bold=True, color="#be123c"))

    # Часова шкала RMW
    # Крок 1: Головний потік читає ODR
    frags.append(rect(35, 88, 220, 72, fill="#ffffff", stroke="#fda4af", sw=1.0, rx=4))
    frags.append(text(145, 108, "Крок 1 (Main thread)", size=11, bold=True, color=INK))
    frags.append(text(145, 126, "LDR r0, [ODR]  (r0 = 0x00)", size=10, color="#0f172a"))
    frags.append(text(145, 145, "ORR r0, #0x20  (хочемо Pin 5)", size=10, color=MUTED))

    # Переривання посередині
    frags.append(arrow(255, 124, 290, 124, color="#e11d48", sw=1.5))
    frags.append(rect(290, 84, 260, 80, fill="#ffe4e6", stroke="#e11d48", sw=1.5, rx=4))
    frags.append(text(420, 102, "ПЕРЕРИВАННЯ (ISR) вклинилося!", size=10, bold=True, color="#9f1239"))
    frags.append(text(420, 122, "LDR r1, [ODR]; ORR r1, #0x80", size=10, color=INK))
    frags.append(text(420, 140, "STR r1, [ODR] -> Pin 7 = 1 у залізі", size=10, bold=True, color=POS))
    frags.append(text(420, 156, "ODR у залізі тепер = 0x80", size=9, color=MUTED))

    # Крок 3: Головний потік перезаписує ODR старим значенням
    frags.append(arrow(550, 124, 585, 124, color="#e11d48", sw=1.5))
    frags.append(rect(585, 88, 240, 72, fill="#ffffff", stroke="#fda4af", sw=1.0, rx=4))
    frags.append(text(705, 108, "Крок 3 (Main thread повертається)", size=10, bold=True, color="#9f1239"))
    frags.append(text(705, 126, "STR r0, [ODR] (записує 0x20)", size=10, bold=True, color="#be123c"))
    frags.append(text(705, 146, "ПОМИЛКА: Pin 7 стерто в 0!", size=10, bold=True, color=POS))

    # Секція 2: Атомарне рішення BSRR / W1TS
    frags.append(rect(20, 190, 820, 120, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(430, 212, "2. Атомарний бітовий запис: PORT->BSRR = (1 << 5)  [Write-Only, без RMW]", size=12, bold=True, color="#15803d"))

    # Головний потік
    frags.append(rect(35, 228, 230, 68, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    frags.append(text(150, 248, "Головний потік (Main thread)", size=11, bold=True, color=INK))
    frags.append(text(150, 266, "STR 0x0020, [BSRR]", size=10, bold=True, color="#166534"))
    frags.append(text(150, 284, "Тільки 1 інструкція запису", size=9, color=MUTED))

    # Апаратний демультиплексор
    frags.append(arrow(265, 262, 305, 262, color="#16a34a", sw=1.5))
    frags.append(rect(305, 228, 230, 68, fill="#dcfce7", stroke="#16a34a", sw=1.0, rx=4))
    frags.append(text(420, 248, "Апаратна логіка на чипі", size=11, bold=True, color="#14532d"))
    frags.append(text(420, 266, "Set-імпульс лише на тригер 5", size=10, color=INK))
    frags.append(text(420, 284, "Інші біти не чіпаються", size=9, color=MUTED))

    # Стан заліза
    frags.append(arrow(535, 262, 575, 262, color="#16a34a", sw=1.5))
    frags.append(rect(575, 228, 250, 68, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    frags.append(text(700, 248, "Результат у залізі", size=11, bold=True, color="#15803d"))
    frags.append(text(700, 266, "Pin 5 = 1, Pin 7 лишився = 1", size=10, bold=True, color="#166534"))
    frags.append(text(700, 284, "Жодних гонок і блокувань", size=9, color=MUTED))

    render(os.path.join(OUT_DIR, "atomic-vs-rmw.svg"), w, h, *frags)


def gen_register_structure_memory():
    """Фігура 3: Відображення структури C на адресний простір периферійного блока."""
    w, h = 860, 270
    frags = []

    frags.append(text(w / 2, 26, "Відображення C-структури на 32-бітний адресний простір периферійного модуля", size=15, bold=True))

    # Зліва: Опис структури C
    frags.append(rect(25, 50, 360, 200, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(205, 74, "Оголошення структури в C (CMSIS)", size=12, bold=True, color=INK))
    frags.append(rect(37, 88, 336, 150, fill="#0f172a", stroke="#334155", sw=1.0, rx=4))
    code_lines = [
        ("typedef struct {", "#f8fafc"),
        ("  volatile uint32_t MODER;   // +0x00", "#38bdf8"),
        ("  volatile uint32_t OTYPER;  // +0x04", "#38bdf8"),
        ("  volatile uint32_t OSPEEDR; // +0x08", "#38bdf8"),
        ("  volatile uint32_t PUPDR;   // +0x0C", "#38bdf8"),
        ("  volatile uint32_t IDR;     // +0x10", "#38bdf8"),
        ("  volatile uint32_t ODR;     // +0x14", "#38bdf8"),
        ("  volatile uint32_t BSRR;    // +0x18", "#f43f5e"),
        ("} GPIO_TypeDef;", "#f8fafc"),
    ]
    for idx, (l_txt, l_col) in enumerate(code_lines):
        frags.append(
            '<text x="50" y="%d" font-family="%s" font-size="11" fill="%s">%s</text>'
            % (106 + idx * 15, FONT, l_col, esc(l_txt))
        )

    # Стрілка перетворення
    frags.append(arrow(390, 150, 440, 150, color=INK, sw=2))
    frags.append(text(415, 138, "32-біт", size=10, color=MUTED))
    frags.append(text(415, 168, "Offset", size=10, color=MUTED))

    # Справа: Карта пам'яті заліза
    frags.append(rect(445, 50, 390, 200, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(640, 74, "Апаратна карта регістрів (GPIOA: 0x40020000)", size=12, bold=True, color="#0369a1"))

    reg_map = [
        ("0x40020000", "+0x00", "MODER (Режим виводів: In/Out/Alt/Analog)", "#e2e8f0"),
        ("0x40020004", "+0x04", "OTYPER (Тип виходу: Push-Pull / Open-Drain)", "#f1f5f9"),
        ("0x40020008", "+0x08", "OSPEEDR (Швидкість наростання фронту)", "#e2e8f0"),
        ("0x4002000C", "+0x0C", "PUPDR (Внутрішні підтяжки Pull-Up/Down)", "#f1f5f9"),
        ("0x40020010", "+0x10", "IDR (Вхідні дані з фізичних пінів, RO)", "#e2e8f0"),
        ("0x40020014", "+0x14", "ODR (Вихідні засувки даних, RW)", "#f1f5f9"),
        ("0x40020018", "+0x18", "BSRR (Атомарне встановлення/скидання, WO)", "#fee2e2"),
    ]
    for idx, (addr, off, name, bg_col) in enumerate(reg_map):
        y_pos = 92 + idx * 21
        frags.append(rect(457, y_pos, 366, 19, fill=bg_col, stroke="#cbd5e1", sw=1.0, rx=2))
        frags.append(text(498, y_pos + 13, addr, size=9, color="#0f172a", bold=True))
        frags.append(text(545, y_pos + 13, off, size=9, color=MUTED))
        frags.append(
            '<text x="570" y="%d" font-family="%s" font-size="9" fill="%s">%s</text>'
            % (y_pos + 13, FONT, INK, esc(name))
        )

    render(os.path.join(OUT_DIR, "register-structure-memory.svg"), w, h, *frags)


if __name__ == "__main__":
    gen_mmio_bus_path()
    gen_atomic_vs_rmw()
    gen_register_structure_memory()
    print("Згенеровано 3 SVG фігури в img/")
