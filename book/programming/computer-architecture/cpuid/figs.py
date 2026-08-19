# -*- coding: utf-8 -*-
"""Фігури до статті «Інструкція CPUID». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
AMBER_FILL = "#fff7e6"
AMBER_STK  = "#c98a00"


# ── Фігура 1: Апаратний механізм інструкції CPUID ───────────────────────────
def fig_hardware_flow():
    W, H = 960, 480
    p = []

    # Заголовок та контекст
    p.append(text(480, 32, "Апаратний інтерфейс та серіалізація команди CPUID (opcode 0F A2)", size=16, bold=True))

    # Ліва колонка: Вхідні регістри
    p.append(rect(40, 70, 220, 360, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(150, 98, "Вхідні параметри", size=14, bold=True, color=NEG))
    p.append(fitbox(55, 125, 190, 70, "EAX\n(Номер листка / Leaf)", size=13, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(55, 215, 190, 70, "ECX\n(Номер підлистка / Sub-leaf)", size=13, fill=BLUE_FILL, stroke=NEG, bold=True))
    
    note_in, _, _ = textbox(150, 350, "Доступно з Ring 3\n(без привілеїв, без #GP)\nНе чіпає пам'ять", size=12, fill=BG, stroke=MUTED)
    p.append(note_in)

    # Центральний блок: Ядро процесора
    p.append(rect(310, 70, 340, 360, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(480, 98, "Виконавчий блок процесора (x86)", size=14, bold=True, color=INK))
    
    p.append(fitbox(330, 125, 300, 75, "Апаратна таблиця конфігурацій\n(ROM мікрокоду + Fuses кремнію)", size=13, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))
    
    p.append(fitbox(330, 220, 300, 85, "Апаратна серіалізація конвеєра\n(Pipeline Serialization Barrier):\nскидання спекулятивних черг,\nзавершення попередніх операцій", size=12, fill=RED_FILL, stroke=POS, bold=True))

    note_mid, _, _ = textbox(480, 365, "Абсолютно детерміновано:\nфіксований набір бітів\nдля поточної мікроархітектури", size=12, fill=BG, stroke=MUTED)
    p.append(note_mid)

    # Права колонка: Вихідні регістри
    p.append(rect(700, 70, 220, 360, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(810, 98, "Вихідні регістри", size=14, bold=True, color=FIELD))
    p.append(fitbox(715, 115, 190, 60, "EAX\n(Сигнатура / Макс. листок)", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(715, 185, 190, 60, "EBX\n(Прапорці / ASCII / APIC)", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(715, 255, 190, 60, "ECX\n(Прапорці розширень / ASCII)", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(715, 325, 190, 60, "EDX\n(Базові прапорці / ASCII)", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стрілки передачі
    p.append(arrow(245, 160, 330, 160, color=NEG, sw=2))
    p.append(arrow(245, 250, 330, 250, color=NEG, sw=2))
    p.append(arrow(630, 150, 715, 150, color=FIELD, sw=2))
    p.append(arrow(630, 215, 715, 215, color=FIELD, sw=2))
    p.append(arrow(630, 285, 715, 285, color=FIELD, sw=2))
    p.append(arrow(630, 355, 715, 355, color=FIELD, sw=2))

    render(os.path.join(IMG, "cpuid-hardware-flow.svg"), W, H, *p,
           title="Апаратний інтерфейс та серіалізація команди CPUID")


# ── Фігура 2: Простір листків CPUID ─────────────────────────────────────────
def fig_leaf_ranges():
    W, H = 960, 460
    p = []

    p.append(text(480, 32, "Адресний простір листків CPUID: діапазони та призначення", size=16, bold=True))

    # Діапазон 1: Базові листки
    p.append(rect(30, 70, 285, 360, fill="#f0f7ff", stroke=NEG, sw=1.6))
    p.append(fitbox(45, 85, 255, 45, "Базові листки (Standard)\n0x00000000 – 0x0000001F+", size=13, fill=BLUE_FILL, stroke=NEG, bold=True))
    
    p.append(fitbox(45, 140, 255, 50, "Leaf 0x00: Max Leaf + Vendor\n(\"GenuineIntel\", \"AuthenticAMD\")", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(45, 198, 255, 50, "Leaf 0x01: Signature & Features\n(Family/Model/Step, SSE, AVX, FPU)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(45, 256, 255, 50, "Leaf 0x04 / 0x18: Кеш-топологія\n(Розміри L1/L2/L3, асоціативність)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(45, 314, 255, 50, "Leaf 0x07: Розширені прапорці\n(AVX2, AVX-512, BMI, SMEP, SMAP)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(45, 372, 255, 45, "Leaf 0x0D: Стан XSAVE / XCR0", size=11.5, fill=BG, stroke=MUTED))

    # Діапазон 2: Гіпервізорні листки
    p.append(rect(335, 70, 290, 360, fill="#f4faf5", stroke=FIELD, sw=1.6))
    p.append(fitbox(350, 85, 260, 45, "Листки гіпервізора (Virtual)\n0x40000000 – 0x400000FF", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    
    p.append(fitbox(350, 140, 260, 56, "Leaf 0x40000000: Сигнатура VMM\n(\"KVMKVMKVM\", \"Microsoft Hv\",\n\"VMwareVMware\", \"XenVMMXenVMM\")", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(350, 204, 260, 56, "Leaf 0x40000001+: Можливості VMM\n(Паравіртуальні годинники PV Clock,\nEOI, IPI, Hypercall інтерфейс)", size=11.5, fill=BG, stroke=MUTED))
    
    note_hyp, _, _ = textbox(480, 320, "Активуються лише у VM\nабо емулюються гіпервізором.\nБіт 31 у Leaf 1 (ECX) = 1\nсигналізує про наявність VMM.", size=12, fill=BG, stroke=FIELD)
    p.append(note_hyp)

    # Діапазон 3: Розширені листки
    p.append(rect(645, 70, 285, 360, fill="#fffaf0", stroke=AMBER_STK, sw=1.6))
    p.append(fitbox(660, 85, 255, 45, "Розширені листки (Extended)\n0x80000000 – 0x80000028+", size=13, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))
    
    p.append(fitbox(660, 140, 255, 50, "Leaf 0x80000000: Max Ext Leaf\n(Діапазон розширених функцій)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(660, 198, 255, 50, "Leaf 0x80000001: Ext Features\n(Long Mode 64-bit, NX/XD біт)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(660, 256, 255, 56, "Leaf 0x80000002–0x80000004:\nBrand String (48 байтів ASCII назви\nпроцесора для користувача)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(660, 320, 255, 50, "Leaf 0x80000008: Адресні лінії\n(Фізична та віртуальна ширина шини)", size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(660, 378, 255, 42, "Топологія AMD / Розширений APIC", size=11.5, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "cpuid-leaf-ranges.svg"), W, H, *p,
           title="Адресний простір листків CPUID")


# ── Фігура 3: Диспетчеризація SIMD та перевірка XCR0 ────────────────────────
def fig_simd_dispatch():
    W, H = 960, 480
    p = []

    p.append(text(480, 32, "Дворівнева перевірка підтримки SIMD та динамічна диспетчеризація", size=16, bold=True))

    # Крок 1: Перевірка заліза
    p.append(fitbox(40, 80, 240, 80, "Крок 1: CPUID\n(Апаратна підтримка)\nLeaf 1 / Leaf 7 прапорці\n(AVX2, AVX-512, FMA)", size=12.5, fill=BLUE_FILL, stroke=NEG, bold=True))
    
    # Крок 2: Перевірка ОС
    p.append(fitbox(360, 80, 240, 80, "Крок 2: OSXSAVE + XCR0\n(Підтримка в ядрі ОС)\nЗбереження регістрів YMM/ZMM\nчерез інструкцію XGETBV", size=12.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))
    
    # Крок 3: Диспетчер
    p.append(fitbox(680, 80, 240, 80, "Крок 3: IFUNC / Диспетчер\n(Вибір реалізації)\nОдноразова резолюція адреси\nпри завантаженні або запуску", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стрілки верхнього ряду
    p.append(arrow(280, 120, 360, 120, color=INK, sw=2))
    p.append(arrow(600, 120, 680, 120, color=INK, sw=2))

    # Розгалуження до цільових реалізацій
    p.append(arrow(800, 160, 800, 220, color=FIELD, sw=2))

    # Блок цілей
    p.append(rect(40, 230, 880, 210, fill="#fbfcfd", stroke=MUTED, sw=1.4))
    p.append(text(480, 255, "Цільові спеціалізовані версії обчислювального ядра", size=14, bold=True))

    p.append(fitbox(60, 280, 185, 130, "AVX-512 ядро\n\n512-бітні вектори ZMM\nМаксимальний throughput\n(Потрібно: AVX512F +\nOS XSAVE для ZMM)", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(275, 280, 185, 130, "AVX2 + FMA ядро\n\n256-бітні вектори YMM\nСучасний стандарт x86-64\n(Потрібно: AVX2 +\nOS XSAVE для YMM)", size=12, fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(490, 280, 185, 130, "SSE4.2 ядро\n\n128-бітні вектори XMM\nСумісність зі старими CPU\n(Працює без обов'язкового\nXSAVE XCR0)", size=12, fill=FILL, stroke=MUTED, bold=True))

    p.append(fitbox(705, 280, 185, 130, "Скалярний Fallback\n\nБазові регістри x86\nГарантований запуск\nна будь-якому процесорі\n(Безпечний мінімум)", size=12, fill=RED_FILL, stroke=POS, bold=True))

    # Стрілки вибору
    p.append(arrow(750, 200, 152, 275, color=FIELD, sw=1.8))
    p.append(arrow(770, 200, 367, 275, color=NEG, sw=1.8))
    p.append(arrow(810, 200, 582, 275, color=MUTED, sw=1.8))
    p.append(arrow(830, 200, 797, 275, color=POS, sw=1.8))

    render(os.path.join(IMG, "simd-dispatch-levels.svg"), W, H, *p,
           title="Дворівнева перевірка підтримки SIMD та динамічна диспетчеризація")


# ── Фігура 4: Емуляція та перехоплення CPUID у віртуалізації (KVM) ───────────
def fig_kvm_intercept():
    W, H = 960, 480
    p = []

    p.append(text(480, 32, "Перехоплення та маскування CPUID у гіпервізорі KVM/QEMU", size=16, bold=True))

    # Верхній світ: Гість (Non-Root Mode)
    p.append(rect(40, 70, 880, 140, fill="#f0f4fc", stroke=NEG, sw=1.6))
    p.append(text(140, 95, "Гість (VM Non-Root)", size=13, bold=True, color=NEG))
    
    p.append(fitbox(60, 115, 260, 75, "Застосунок або ядро гостя\nвиконує інструкцію CPUID\n(EAX=1, ECX=0)", size=12.5, fill=BG, stroke=NEG, bold=True))

    p.append(fitbox(640, 115, 260, 75, "Гість отримує віртуалізовані\nзначення регістрів EAX..EDX\nі продовжує виконання", size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Середина: VM-Exit та VM-Entry
    p.append(arrow(340, 150, 460, 240, color=POS, sw=2.2))
    p.append(text(440, 185, "VM-Exit (EXIT_REASON_CPUID)", size=12, color=POS, bold=True))

    p.append(arrow(580, 240, 680, 195, color=FIELD, sw=2.2))
    p.append(text(665, 230, "VM-Entry (Відновлення vCPU)", size=12, color=FIELD, bold=True))

    # Нижній світ: Господар (Root Mode / KVM)
    p.append(rect(40, 250, 880, 190, fill="#fbf8f2", stroke=AMBER_STK, sw=1.6))
    p.append(text(140, 275, "Господар (Root Mode / KVM & QEMU)", size=13, bold=True, color=AMBER_STK))

    p.append(fitbox(60, 295, 260, 125, "Перехоплення в KVM\n\n1. Зчитування вхідних EAX/ECX\n2. Пошук у таблиці конфігурації\n(налаштованій через ioctl\nKVM_SET_CPUID2)", size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(350, 295, 260, 125, "Маскування та фільтрація\n\n• Вимкнення AVX-512 для міграції\n• Додавання бітів IBRS / IBPB\n• Встановлення Hypervisor Bit\n• Формування vCPU топології", size=12, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    p.append(fitbox(640, 295, 260, 125, "Запис у стан vCPU\n\nЗапис змодельованих значень\nу віртуальні EAX, EBX, ECX, EDX\nінкремент гостьового RIP (+2)\nдля переходу до наступної інструкції", size=12, fill=BG, stroke=MUTED))

    # Стрілки всередині KVM
    p.append(arrow(320, 355, 350, 355, color=INK, sw=1.8))
    p.append(arrow(610, 355, 640, 355, color=INK, sw=1.8))

    render(os.path.join(IMG, "kvm-cpuid-intercept.svg"), W, H, *p,
           title="Перехоплення та маскування CPUID у гіпервізорі KVM/QEMU")


if __name__ == "__main__":
    fig_hardware_flow()
    fig_leaf_ranges()
    fig_simd_dispatch()
    fig_kvm_intercept()
    print("Усі 4 фігури згенеровано успішно.")
