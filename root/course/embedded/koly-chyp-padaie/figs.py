# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми koly-chyp-padaie."""
import sys
import os

# scripts/ лежить на 4 рівні вище: root/course/embedded/koly-chyp-padaie -> scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_reset_flags_sources():
    """Фігура 1: Джерела апаратного скидання та збереження прапорців у RCC->CSR."""
    w, h = 860, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Джерела апаратного скидання мікроконтролера та прапорці статусу", size=16, bold=True))

    # Ліва колонка: Джерела скидання (6 блоків)
    sources = [
        ("Power-On / Power-Down (POR/PDR)", "Подача живлення або знеструмлення (< 1.8V)", POS),
        ("Brown-Out Detector (BOR / PVD)", "Короткочасне просідання напруги живлення", "#d35400"),
        ("Зовнішній пін скидання (NRST)", "Апаратна кнопка або сигнал зовнішнього супервізора", "#2980b9"),
        ("Незалежний сторож (IWDG)", "Зависання головного циклу / такт від LSI 32 кГц", "#8e44ad"),
        ("Віконний сторож (WWDG)", "Передчасне або запізніле оновлення сторожа", "#16a085"),
        ("Програмне скидання (SFTRST)", "Виклик NVIC_SystemReset() з коду прошивки", "#2c3e50"),
    ]

    sy_start = 65
    sy_step = 62
    src_w = 320
    src_h = 50
    src_x = 30

    for i, (title, desc, clr) in enumerate(sources):
        cy = sy_start + i * sy_step
        # Рамка джерела
        frags.append(rect(src_x, cy, src_w, src_h, fill="#ffffff", stroke=clr, sw=2, rx=6))
        # Текст
        frags.append(text(src_x + 12, cy + 20, title, size=13, color=clr, bold=True, anchor="start"))
        frags.append(text(src_x + 12, cy + 38, desc, size=11, color=MUTED, anchor="start"))
        # Стрілка праворуч
        frags.append(arrow(src_x + src_w, cy + src_h / 2, src_x + src_w + 60, cy + src_h / 2, color=clr, sw=1.8))

    # Центральний блок: Контролер скидання (Reset Controller)
    ctrl_x = 420
    ctrl_y = 65
    ctrl_w = 170
    ctrl_h = 360
    frags.append(rect(ctrl_x, ctrl_y, ctrl_w, ctrl_h, fill="#edf2f7", stroke=LINE, sw=2, rx=8))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 35, "Апаратний", size=14, bold=True))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 55, "контролер скидання", size=14, bold=True))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 75, "(RCC / Reset Control)", size=11, color=MUTED))

    # Внутрішня плашка в контролері: Засувка прапорців
    frags.append(rect(ctrl_x + 12, ctrl_y + 110, ctrl_w - 24, 140, fill="#ffffff", stroke="#718096", sw=1.5, rx=5))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 132, "Липкі тригери", size=12, bold=True, color=POS))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 150, "(Sticky Flags)", size=11, bold=True, color=POS))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 175, "Зберігають джерело", size=11, color=INK))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 195, "крізь перезапуск;", size=11, color=INK))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 215, "не зникають самі!", size=11, color=POS, bold=True))

    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 285, "Генерація сигналу", size=12, color=INK))
    frags.append(text(ctrl_x + ctrl_w / 2, ctrl_y + 305, "System Reset на ядро", size=12, color=INK, bold=True))

    # Стрілка з контролера праворуч
    frags.append(arrow(ctrl_x + ctrl_w, ctrl_y + 180, ctrl_x + ctrl_w + 50, ctrl_y + 180, color=LINE, sw=2))

    # Права колонка: Регістр статусу й дія в коді
    reg_x = 640
    reg_y = 65
    reg_w = 195
    reg_h = 360
    frags.append(rect(reg_x, reg_y, reg_w, reg_h, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(text(reg_x + reg_w / 2, reg_y + 30, "Регістр RCC->CSR", size=14, bold=True, color="#1e3a8a"))
    frags.append(text(reg_x + reg_w / 2, reg_y + 50, "(Reset Status Register)", size=11, color=MUTED))

    # Перелік бітів
    bit_items = [
        ("LPWRRSTF", "Low-power reset"),
        ("WWDGRSTF", "Window watchdog"),
        ("IWDGRSTF", "Independent watchdog"),
        ("SFTRSTF", "Software reset"),
        ("PORRSTF", "Power-on reset"),
        ("PINRSTF", "NRST pin reset"),
        ("BORRSTF", "Brown-out reset"),
    ]
    for j, (bname, bdesc) in enumerate(bit_items):
        by = reg_y + 75 + j * 24
        frags.append(rect(reg_x + 10, by, reg_w - 20, 20, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=3))
        frags.append(text(reg_x + 18, by + 14, bname, size=10, bold=True, anchor="start", color="#0f172a"))
        frags.append(text(reg_x + reg_w - 16, by + 14, bdesc, size=9, anchor="end", color=MUTED))

    # Обов'язкова дія внизу правої колонки
    frags.append(rect(reg_x + 10, reg_y + 255, reg_w - 20, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    frags.append(text(reg_x + reg_w / 2, reg_y + 275, "Діагностика в main():", size=11, bold=True, color=POS))
    frags.append(text(reg_x + reg_w / 2, reg_y + 295, "1. Зчитати прапорці", size=11, color=INK))
    frags.append(text(reg_x + reg_w / 2, reg_y + 315, "2. Записати RMVF = 1", size=11, bold=True, color=POS))
    frags.append(text(reg_x + reg_w / 2, reg_y + 335, "(очистити для історії)", size=10, color=MUTED))

    # Підвал
    frags.append(text(w / 2, 458, "Якщо не скинути RMVF на старті, усі наступні збої змішаються з попередніми", size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "reset-flags-sources.svg"), w, h, *frags)


def fig_fault_escalation():
    """Фігура 2: Ієрархія винятків Cortex-M, механізм ескалації та перехід у Lockup."""
    w, h = 880, 480
    frags = []

    frags.append(text(w / 2, 28, "Ієрархія апаратних винятків Cortex-M та механізм ескалації збоїв", size=16, bold=True))

    # 3 конфігуровані збої зліва
    cfg_faults = [
        ("MemManage Fault", "Порушення MPU, запис у Read-Only,", "виконання з No-Execute (XN)", "#2b6cb0"),
        ("BusFault", "Помилка адресації шини AHB/APB,", "доступ до вимкненої периферії", "#c05621"),
        ("UsageFault", "Невирівняний доступ, ділення на 0,", "невідома інструкція, втрата Thumb", "#2f855a"),
    ]

    bx = 30
    bw = 250
    bh = 76
    y_starts = [65, 160, 255]

    for i, (name, d1, d2, clr) in enumerate(cfg_faults):
        cy = y_starts[i]
        frags.append(rect(bx, cy, bw, bh, fill="#ffffff", stroke=clr, sw=2, rx=6))
        frags.append(text(bx + 14, cy + 22, name, size=13, bold=True, color=clr, anchor="start"))
        frags.append(text(bx + 14, cy + 42, d1, size=11, color=INK, anchor="start"))
        frags.append(text(bx + 14, cy + 60, d2, size=10, color=MUTED, anchor="start"))

        # Стрілка до умови
        frags.append(arrow(bx + bw, cy + bh / 2, bx + bw + 50, cy + bh / 2, color=clr, sw=1.8))

    # Блок перевірки SHCSR (System Handler Control and State Register)
    cx = 330
    cw = 180
    ch = 266
    frags.append(rect(cx, 65, cw, ch, fill="#f7fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(cx + cw / 2, 95, "Чи увімкнено обробник", size=12, bold=True))
    frags.append(text(cx + cw / 2, 115, "у SCB->SHCSR?", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(cx + cw / 2, 135, "(USGFAULTENA,", size=10, color=MUTED))
    frags.append(text(cx + cw / 2, 150, "BUSFAULTENA,", size=10, color=MUTED))
    frags.append(text(cx + cw / 2, 165, "MEMFAULTENA)", size=10, color=MUTED))

    # Гілка ТАК -> Індивідуальні обробники
    frags.append(arrow(cx + cw / 2, 65, cx + cw / 2, 45, color=FIELD, sw=2))
    frags.append(text(cx + cw / 2, 38, "ТАК (увімкнено)", size=11, bold=True, color=FIELD))

    # Блок індивідуальних обробників угорі
    frags.append(rect(560, 20, 290, 50, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(705, 40, "Індивідуальні обробники винятків", size=12, bold=True, color=FIELD))
    frags.append(text(705, 58, "MemManage_Handler / BusFault / UsageFault", size=10, color=INK))
    frags.append(arrow(cx + cw / 2, 20, 560, 40, color=FIELD, sw=1.8))

    # Гілка НІ -> Ескалація до HardFault
    frags.append(text(cx + cw / 2, 230, "НІ (вимкнено за замовч.)", size=11, bold=True, color=POS))
    frags.append(text(cx + cw / 2, 250, "або збій у вищому пріоритеті", size=10, color=POS))
    frags.append(arrow(cx + cw, 250, cx + cw + 50, 250, color=POS, sw=2.2))

    # Центральний вузол: HardFault
    hx = 560
    hy = 140
    hw = 290
    hh = 170
    frags.append(rect(hx, hy, hw, hh, fill="#fff5f5", stroke=POS, sw=2.5, rx=8))
    frags.append(text(hx + hw / 2, hy + 30, "HardFault_Handler", size=16, bold=True, color=POS))
    frags.append(text(hx + hw / 2, hy + 52, "Фіксований пріоритет: -1 (завжди активний)", size=11, color=MUTED))

    # Плашка про HFSR.FORCED
    frags.append(rect(hx + 15, hy + 70, hw - 30, 85, fill="#ffffff", stroke="#feb2b2", sw=1.5, rx=5))
    frags.append(text(hx + hw / 2, hy + 90, "Ескалація: SCB->HFSR.FORCED = 1", size=12, bold=True, color=POS))
    frags.append(text(hx + hw / 2, hy + 110, "Справжню причину треба шукати", size=11, color=INK))
    frags.append(text(hx + hw / 2, hy + 128, "у підлеглих регістрах SCB->CFSR", size=11, bold=True, color=INK))
    frags.append(text(hx + hw / 2, hy + 145, "(UFSR, BFSR, MMFSR)", size=11, color="#1e3a8a"))

    # Стрілка вниз: Подвійний збій (Double fault)
    frags.append(arrow(hx + hw / 2, hy + hh, hx + hw / 2, hy + hh + 45, color="#742a2a", sw=2.2))
    frags.append(text(hx + hw / 2 + 10, hy + hh + 25, "Збій під час обробки HardFault (зіпсований стек / вектор)", size=10, color=POS, anchor="start"))

    # Блок Lockup
    lx = 560
    ly = 365
    lw = 290
    lh = 80
    frags.append(rect(lx, ly, lw, lh, fill="#2d3748", stroke="#1a202c", sw=2, rx=8))
    frags.append(text(lx + lw / 2, ly + 28, "Стан LOCKUP (Повне зависання ядра)", size=14, bold=True, color="#ffffff"))
    frags.append(text(lx + lw / 2, ly + 48, "Процесор зупиняє вибірку інструкцій", size=11, color="#e2e8f0"))
    frags.append(text(lx + lw / 2, ly + 66, "Вихід ТІЛЬКИ через апаратний Reset (Watchdog/NRST)", size=11, bold=True, color="#feb2b2"))

    # Підказка зліва внизу
    frags.append(rect(30, 365, 480, 80, fill="#ebf8ff", stroke="#bee3f8", sw=1.5, rx=6))
    frags.append(text(270, 388, "Золоте правило надійності в Cortex-M:", size=12, bold=True, color="#2b6cb0"))
    frags.append(text(270, 410, "Завжди вмикайте індивідуальні винятки в SHCSR на старті системи!", size=11, bold=True, color=INK))
    frags.append(text(270, 430, "Тоді збій викличе точний обробник замість миттєвого звалювання в HardFault.", size=10, color=MUTED))

    render(os.path.join(OUT, "fault-escalation.svg"), w, h, *frags)


def fig_stack_frame_dump():
    """Фігура 3: Апаратне збереження контексту на стеку та розкодування EXC_RETURN."""
    w, h = 880, 500
    frags = []

    frags.append(text(w / 2, 28, "Стековий фрейм аварії Cortex-M та розкодування регістра LR (EXC_RETURN)", size=16, bold=True))

    # Ліва колонка: Стековий фрейм (Basic Frame 8 слів)
    sx = 40
    sy = 65
    sw_box = 340
    sh_box = 400

    frags.append(rect(sx, sy, sw_box, sh_box, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(text(sx + sw_box / 2, sy + 25, "Стековий фрейм аварії (Hardware Stacking)", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(sx + sw_box / 2, sy + 43, "Зберігається апаратурою ядра до виклику обробника", size=10, color=MUTED))

    # Елементи стеку від SP+0x00 до SP+0x1C
    stack_items = [
        ("SP + 0x00", "R0", "Аргумент 1 / тимчасові дані", "#edf2f7"),
        ("SP + 0x04", "R1", "Аргумент 2 / тимчасові дані", "#edf2f7"),
        ("SP + 0x08", "R2", "Аргумент 3 / тимчасові дані", "#edf2f7"),
        ("SP + 0x0C", "R3", "Аргумент 4 / тимчасові дані", "#edf2f7"),
        ("SP + 0x10", "R12", "Внутрішній тимчасовий регістр (IP)", "#edf2f7"),
        ("SP + 0x14", "LR (R14)", "Повернення з функції до моменту збою", "#fef3c7"),
        ("SP + 0x18", "PC (R15)", "ВИННА ІНСТРУКЦІЯ (Program Counter)!", "#fee2e2"),
        ("SP + 0x1C", "xPSR", "Прапорці стану ядра (Thumb bit T=1)", "#fef3c7"),
    ]

    item_y = sy + 58
    item_h = 34

    for i, (offset, regname, desc, bgc) in enumerate(stack_items):
        iy = item_y + i * (item_h + 4)
        border_clr = POS if "PC" in regname else (LINE if "LR" in regname else "#cbd5e1")
        sw_val = 2 if "PC" in regname else 1.2
        frags.append(rect(sx + 15, iy, sw_box - 30, item_h, fill=bgc, stroke=border_clr, sw=sw_val, rx=4))
        frags.append(text(sx + 25, iy + 22, offset, size=11, bold=True, anchor="start", color="#475569"))
        frags.append(text(sx + 115, iy + 22, regname, size=12, bold=True, anchor="start", color=POS if "PC" in regname else INK))
        frags.append(text(sx + sw_box - 25, iy + 22, desc, size=10, anchor="end", color=MUTED if "PC" not in regname else POS))

    # Стрілка спадання стека зліва
    frags.append(text(sx + 8, sy + 220, "Вершина стека (SP)", size=10, color=MUTED, anchor="middle"))

    # Права верхня секція: Регістр LR на вході в обробник (EXC_RETURN)
    rx = 420
    ry = 65
    rw = 420
    rh = 195

    frags.append(rect(rx, ry, rw, rh, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(rx + rw / 2, ry + 25, "Регістр LR на вході в HardFault_Handler", size=13, bold=True, color=FIELD))
    frags.append(text(rx + rw / 2, ry + 43, "Магічне значення EXC_RETURN (0xFFFFFFxx)", size=11, bold=True, color=INK))

    exc_bits = [
        ("Біт 2 (0x04): Стек переривання", "0 = Головний стек (MSP)  |  1 = Стек задачі (PSP)"),
        ("Біт 3 (0x08): Режим процесора", "0 = Handler Mode (обробник)  |  1 = Thread Mode"),
        ("Біт 4 (0x10): Розширений кадр FPU", "0 = Кадр з FPU (26 слів)  |  1 = Базовий кадр (8 слів)"),
    ]

    for j, (btitle, bval) in enumerate(exc_bits):
        by = ry + 60 + j * 42
        frags.append(rect(rx + 15, by, rw - 30, 36, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
        frags.append(text(rx + 25, by + 16, btitle, size=11, bold=True, anchor="start", color="#166534"))
        frags.append(text(rx + 25, by + 30, bval, size=10, anchor="start", color=INK))

    # Права нижня секція: Пошук винного рядка в C/C++ коді
    dx = 420
    dy = 275
    dw = 420
    dh = 190

    frags.append(rect(dx, dy, dw, dh, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=8))
    frags.append(text(dx + dw / 2, dy + 25, "Від значення PC до винного рядка у вихідному коді", size=13, bold=True, color="#1d4ed8"))

    steps = [
        ("1. Зняти адресу PC зі стеку:", "Наприклад, PC = 0x08001A42"),
        ("2. Запустити утиліту addr2line:", "arm-none-eabi-addr2line -e firmware.elf -a 0x08001A42"),
        ("3. Отримати файл і номер рядка:", "main.c:148  ->  sensor_ptr->read()"),
    ]

    for k, (stitle, sval) in enumerate(steps):
        ky = dy + 45 + k * 45
        frags.append(text(dx + 20, ky + 15, stitle, size=11, bold=True, anchor="start", color="#1e40af"))
        frags.append(rect(dx + 20, ky + 22, dw - 40, 22, fill="#1e293b", stroke="#0f172a", sw=1, rx=3))
        frags.append(text(dx + 30, ky + 37, sval, size=10, bold=True, anchor="start", color="#38bdf8"))

    render(os.path.join(OUT, "stack-frame-dump.svg"), w, h, *frags)


def fig_crash_diagnosis_tree():
    """Фігура 4: Алгоритм та діагностичне дерево пошуку причини HardFault."""
    w, h = 880, 500
    frags = []

    frags.append(text(w / 2, 28, "Діагностичне дерево визначення першопричини аварії чипа", size=16, bold=True))

    # Блок 1: Початок аварії
    frags.append(rect(340, 55, 200, 45, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    frags.append(text(440, 75, "Вхід у HardFault_Handler", size=13, bold=True, color=POS))
    frags.append(text(440, 92, "Визначити SP за EXC_RETURN", size=10, color=MUTED))

    # Стрілка вниз
    frags.append(arrow(440, 100, 440, 130, color=LINE, sw=2))

    # Блок 2: Перевірка SCB->HFSR
    frags.append(rect(320, 130, 240, 48, fill="#f8fafc", stroke=LINE, sw=2, rx=6))
    frags.append(text(440, 150, "Аналіз SCB->HFSR", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(440, 168, "Чи виставлено біт FORCED (0x40000000)?", size=10, color=MUTED))

    # 3 розгалуження вниз до CFSR підрегістрів
    # Лінія розподілу
    frags.append(line(160, 200, 720, 200, color=LINE, sw=1.5))
    frags.append(line(440, 178, 440, 200, color=LINE, sw=1.5))
    frags.append(arrow(160, 200, 160, 225, color=LINE, sw=1.8))
    frags.append(arrow(440, 200, 440, 225, color=LINE, sw=1.8))
    frags.append(arrow(720, 200, 720, 225, color=LINE, sw=1.8))

    # 3 підрегістри CFSR
    # 1. MMFSR (Memory Management)
    frags.append(rect(40, 225, 240, 60, fill="#ebf8ff", stroke="#3182ce", sw=1.8, rx=6))
    frags.append(text(160, 248, "SCB->CFSR: MMFSR (8 біт)", size=12, bold=True, color="#2b6cb0"))
    frags.append(text(160, 268, "DACCVIOL / IACCVIOL / MMARVALID", size=10, color=INK))

    # 2. BFSR (Bus Fault)
    frags.append(rect(320, 225, 240, 60, fill="#fffaf0", stroke="#dd6b20", sw=1.8, rx=6))
    frags.append(text(440, 248, "SCB->CFSR: BFSR (8 біт)", size=12, bold=True, color="#c05621"))
    frags.append(text(440, 268, "PRECISERR / IMPRECISERR / BFARVALID", size=10, color=INK))

    # 3. UFSR (Usage Fault)
    frags.append(rect(600, 225, 240, 60, fill="#f0fff4", stroke="#38a169", sw=1.8, rx=6))
    frags.append(text(720, 248, "SCB->CFSR: UFSR (16 біт)", size=12, bold=True, color="#276749"))
    frags.append(text(720, 268, "UNDEFINSTR / INVSTATE / UNALIGNED", size=10, color=INK))

    # Стрілки до діагнозів
    frags.append(arrow(160, 285, 160, 320, color="#3182ce", sw=1.8))
    frags.append(arrow(440, 285, 440, 320, color="#dd6b20", sw=1.8))
    frags.append(arrow(720, 285, 720, 320, color="#38a169", sw=1.8))

    # Діагнози для кожного випадку
    # Діагноз MMFSR
    frags.append(rect(40, 320, 240, 150, fill="#ffffff", stroke="#90cdf4", sw=1.5, rx=6))
    frags.append(text(160, 340, "Діагноз MPU / Пам'ять", size=11, bold=True, color="#2b6cb0"))
    frags.append(text(50, 365, "• DACCVIOL: розіменування", size=10, anchor="start", color=INK))
    frags.append(text(60, 380, "NULL або запис у Flash", size=10, anchor="start", color=MUTED))
    frags.append(text(50, 400, "• IACCVIOL: спроба стрибка", size=10, anchor="start", color=INK))
    frags.append(text(60, 415, "в пам'ять без права коду (XN)", size=10, anchor="start", color=MUTED))
    frags.append(text(50, 435, "• MMARVALID = 1:", size=10, bold=True, anchor="start", color="#2b6cb0"))
    frags.append(text(60, 450, "Адреса в SCB->MMFAR!", size=10, bold=True, anchor="start", color=POS))

    # Діагноз BFSR
    frags.append(rect(320, 320, 240, 150, fill="#ffffff", stroke="#fbd38d", sw=1.5, rx=6))
    frags.append(text(440, 340, "Діагноз Шина / Периферія", size=11, bold=True, color="#c05621"))
    frags.append(text(330, 365, "• PRECISERR: точна адреса,", size=10, anchor="start", color=INK))
    frags.append(text(340, 380, "доступ до вимкненої периферії", size=10, anchor="start", color=MUTED))
    frags.append(text(330, 400, "• IMPRECISERR: асинхронний", size=10, anchor="start", color=INK))
    frags.append(text(340, 415, "запис через буфер шини", size=10, anchor="start", color=MUTED))
    frags.append(text(330, 435, "• BFARVALID = 1:", size=10, bold=True, anchor="start", color="#c05621"))
    frags.append(text(340, 450, "Адреса в SCB->BFAR!", size=10, bold=True, anchor="start", color=POS))

    # Діагноз UFSR
    frags.append(rect(600, 320, 240, 150, fill="#ffffff", stroke="#9ae6b4", sw=1.5, rx=6))
    frags.append(text(720, 340, "Діагноз Команди / Стан", size=11, bold=True, color="#276749"))
    frags.append(text(610, 365, "• UNDEFINSTR: виконання сміття", size=10, anchor="start", color=INK))
    frags.append(text(620, 380, "(переповнення стека / збій коду)", size=10, anchor="start", color=MUTED))
    frags.append(text(610, 400, "• INVSTATE: біт Thumb T=0", size=10, anchor="start", color=INK))
    frags.append(text(620, 415, "(виклик парної адреси функції)", size=10, anchor="start", color=MUTED))
    frags.append(text(610, 435, "• UNALIGNED: збій вирівнювання", size=10, anchor="start", color=INK))
    frags.append(text(620, 450, "• DIVBYZERO: ділення на 0", size=10, anchor="start", color=INK))

    render(os.path.join(OUT, "crash-diagnosis-tree.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_reset_flags_sources()
    fig_fault_escalation()
    fig_stack_frame_dump()
    fig_crash_diagnosis_tree()
    print("All figures generated successfully.")
