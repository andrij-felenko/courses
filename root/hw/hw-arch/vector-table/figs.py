# -*- coding: utf-8 -*-
"""Фігури до теми «Таблиця векторів» (hw-arch).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
GRAY_BG  = "#f3f4f6"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── 1. Організація таблиці векторів Cortex-M ──────────────────────────────────
def fig_vector_table_layout():
    """Розкладка перших слів таблиці векторів: Initial MSP, Reset, System Exceptions, IRQ."""
    W, H = 960, 680
    f = []
    
    f.append(text(W / 2, 40, "Анатомія таблиці векторів ARM Cortex-M: 16 системних слотів та периферійні переривання",
                  size=14, color=INK, bold=True))
    f.append(text(W / 2, 64, "Кожен слот — 32-бітне слово. Слот 0 завантажує SP, слоти 1..N містять адреси з бітом Thumb=1.",
                  size=12, color=MUTED, italic=True))

    # Заголовки колонок
    ytop = 96
    f.append(rect(40, ytop, 880, 32, fill=INK, stroke=INK, sw=1.5, rx=6))
    f.append(text(85, ytop + 21, "Зсув", size=12, color="#ffffff", bold=True))
    f.append(text(160, ytop + 21, "Вектор #", size=12, color="#ffffff", bold=True))
    f.append(text(280, ytop + 21, "Назва / Призначення", size=12, color="#ffffff", bold=True))
    f.append(text(500, ytop + 21, "Тип / Властивість", size=12, color="#ffffff", bold=True))
    f.append(text(750, ytop + 21, "Апаратна дія ядра при скиданні чи спрацюванні", size=12, color="#ffffff", bold=True))

    rows = [
        ("0x00", "0", "Initial MSP Value", "Покажчик стека (не функція!)", "Завантажується в SP (R13) апаратно до першої інструкції", POS, RED_BG),
        ("0x04", "1", "Reset Handler", "Вхідна точка прошивки", "Завантажується в PC (R15), починає виконання коду [Thumb=1]", FIELD, GREEN_BG),
        ("0x08", "2", "NMI Handler", "Немасковане переривання", "Фіксований пріоритет -2; аварії живлення, годинника, ECC", NEG, BLUE_BG),
        ("0x0C", "3", "HardFault Handler", "Критична апаратна відмова", "Фіксований пріоритет -1; падіння ядра, ескалація помилок", POS, RED_BG),
        ("0x10", "4", "MemManage Fault", "Порушення захисту MPU", "Конфігурований пріоритет; доступ до забороненої пам'яті", AMBER, AMBER_BG),
        ("0x14", "5", "BusFault Handler", "Помилка системної шини", "Конфігурований пріоритет; тайм-аут AHB/APB, помилка адреси", AMBER, AMBER_BG),
        ("0x18", "6", "UsageFault Handler", "Помилка інструкцій ядра", "Ділення на нуль, непарний перехід, невирівняний доступ", AMBER, AMBER_BG),
        ("0x1C..28", "7..10", "Reserved Slots", "Зарезервовано архітектурою", "Мають бути заповнені 0 або дескрипторами безпеки", MUTED, GRAY_BG),
        ("0x2C", "11", "SVCall Handler", "Системний виклик (SVC)", "Виклик супервізора для виходу в привілейований режим RTOS", NEG, BLUE_BG),
        ("0x30..34", "12..13", "DebugMon / Reserved", "Монітор відлагодження", "Точки зупинки, відлагоджувальні пастки апаратури", MUTED, GRAY_BG),
        ("0x38", "14", "PendSV Handler", "Відкладене переривання", "Асинхронне перемикання контексту задач в ОС (низький пріоритет)", FIELD, GREEN_BG),
        ("0x3C", "15", "SysTick Handler", "Системний квант часу", "Періодичний таймер планувальника операційної системи", FIELD, GREEN_BG),
        ("0x40+", "16..N", "External IRQ #0..#N", "Периферійні переривання", "Маршрутизуються контролером NVIC: UART, SPI, DMA, GPIO, TIM", INK, "#ffffff"),
    ]

    y = ytop + 34
    rowh = 36
    for offset, num, name, prop, action, col, bg in rows:
        f.append(rect(40, y, 880, rowh, fill=bg, stroke=col, sw=1.1, rx=4))
        f.append(mono(85, y + 22, offset, size=11, color=col, anchor="middle", bold=True))
        f.append(text(160, y + 22, num, size=11.5, color=INK, anchor="middle"))
        f.append(text(280, y + 22, name, size=11.5, color=col, anchor="middle", bold=True))
        f.append(text(500, y + 22, prop, size=10.5, color=INK, anchor="middle"))
        f.append(text(750, y + 22, action, size=10.5, color=INK, anchor="middle"))
        y += rowh + 3

    # Примітка знизу
    f.append(rect(40, y + 10, 880, 48, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    f.append(text(W / 2, y + 28, "Біт 0 адреси обробника (LSB) ЗАВЖДИ має дорівнювати 1, позначаючи виконання в режимі Thumb.",
                  size=11.5, color=POS, bold=True))
    f.append(text(W / 2, y + 44, "Запис адреси з бітом 0 = 0 викликає негайне падіння ядра в UsageFault (INVSTATE) при виклику вектора.",
                  size=10.5, color=MUTED))

    out("cortex-m-vector-table-layout.svg", W, H, *f,
        title="Організація таблиці векторів ARM Cortex-M")


# ── 2. Перепризначення VTOR завантажувач / додаток / SRAM ──────────────────────
def fig_vtor_relocation():
    """Схема релокації VTOR між Flash завантажувача, Flash додатку та SRAM."""
    W, H = 960, 560
    f = []

    f.append(text(W / 2, 38, "Динамічне перепризначення таблиці векторів через регістр SCB->VTOR",
                  size=14, color=INK, bold=True))
    f.append(text(W / 2, 60, "Апаратне переспрямування векторів переривань між завантажувачем, основною прошивкою та оперативною пам'яттю.",
                  size=12, color=MUTED, italic=True))

    # Три блоки пам'яті: Flash Bootloader, Flash App, SRAM
    # 1. Bootloader
    f.append(rect(50, 95, 260, 370, fill=BLUE_BG, stroke=NEG, sw=1.8, rx=8))
    f.append(text(180, 122, "Flash: Завантажувач", size=13, color=NEG, bold=True))
    f.append(mono(180, 142, "0x0800_0000", size=11.5, color=MUTED, anchor="middle"))

    f.append(rect(65, 160, 230, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    f.append(mono(180, 185, "Initial MSP (Boot)", size=11, color=NEG, anchor="middle", bold=True))

    f.append(rect(65, 208, 230, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    f.append(mono(180, 233, "Reset_Handler (Boot)", size=11, color=NEG, anchor="middle", bold=True))

    f.append(rect(65, 256, 230, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(180, 283, "Вектори завантажувача", size=11, color=INK, bold=True))
    f.append(text(180, 305, "UART, USB DFU, Flash Driver", size=10, color=MUTED))

    f.append(rect(65, 334, 230, 115, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    f.append(text(180, 365, "Код завантажувача", size=11.5, color=INK, bold=True))
    f.append(text(180, 388, "Перевірка цілісності CRC", size=10, color=MUTED))
    f.append(text(180, 408, "Оновлення образу в Flash", size=10, color=MUTED))
    f.append(text(180, 428, "Перехід: VTOR = 0x08008000", size=10, color=POS, bold=True))

    # 2. Main App Flash
    f.append(rect(350, 95, 260, 370, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(480, 122, "Flash: Головний Додаток", size=13, color=FIELD, bold=True))
    f.append(mono(480, 142, "0x0800_8000 (вирівняно)", size=11.5, color=MUTED, anchor="middle"))

    f.append(rect(365, 160, 230, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(mono(480, 185, "Initial MSP (App)", size=11, color=FIELD, anchor="middle", bold=True))

    f.append(rect(365, 208, 230, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(mono(480, 233, "Reset_Handler (App)", size=11, color=FIELD, anchor="middle", bold=True))

    f.append(rect(365, 256, 230, 70, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(480, 283, "Вектори додатку", size=11, color=INK, bold=True))
    f.append(text(480, 305, "SysTick, FreeRTOS, Периферія", size=10, color=MUTED))

    f.append(rect(365, 334, 230, 115, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    f.append(text(480, 365, "Код додатку (Firmware)", size=11.5, color=INK, bold=True))
    f.append(text(480, 388, "Ініціалізація FreeRTOS/HAL", size=10, color=MUTED))
    f.append(text(480, 408, "Основний цикл обробки", size=10, color=MUTED))
    f.append(text(480, 428, "Копія в RAM: VTOR = 0x20000000", size=10, color=AMBER, bold=True))

    # 3. SRAM Vector Table
    f.append(rect(650, 95, 260, 370, fill=AMBER_BG, stroke=AMBER, sw=1.8, rx=8))
    f.append(text(780, 122, "SRAM: Динамічні вектори", size=13, color=AMBER, bold=True))
    f.append(mono(780, 142, "0x2000_0000 (вирівняно 512B)", size=11.5, color=MUTED, anchor="middle"))

    f.append(rect(665, 160, 230, 42, fill="#ffffff", stroke=AMBER, sw=1.2, rx=4))
    f.append(mono(780, 185, "Initial MSP (SRAM copy)", size=11, color=AMBER, anchor="middle", bold=True))

    f.append(rect(665, 208, 230, 42, fill="#ffffff", stroke=AMBER, sw=1.2, rx=4))
    f.append(mono(780, 233, "HardFault Handler (RAM)", size=11, color=POS, anchor="middle", bold=True))

    f.append(rect(665, 256, 230, 70, fill="#ffffff", stroke=AMBER, sw=1.2, rx=4))
    f.append(text(780, 283, "Динамічні обробники", size=11, color=INK, bold=True))
    f.append(text(780, 305, "Перехоплення ISR в рантаймі", size=10, color=MUTED))

    f.append(rect(665, 334, 230, 115, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    f.append(text(780, 365, "Переваги релокації в RAM", size=11.5, color=INK, bold=True))
    f.append(text(780, 388, "Нульова затримка (без wait-states)", size=10, color=MUTED))
    f.append(text(780, 408, "Підміна хуків без перепрошивки", size=10, color=MUTED))
    f.append(text(780, 428, "Робота під час запису Flash пам'яті", size=10, color=FIELD, bold=True))

    # Стрілки перемикання VTOR
    f.append(rect(100, 485, 760, 52, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(480, 506, "Регістр SCB->VTOR (0xE000ED08) вказує на активну таблицю векторів в адресному просторі",
                  size=12, color=INK, bold=True))
    f.append(text(480, 524, "Вимога вирівнювання: адреса в VTOR мусить бути вирівняна на степінь двійки за розміром таблиці (від 128 до 512+ байтів).",
                  size=11, color=POS))

    out("vtor-relocation-bootloader-app.svg", W, H, *f,
        title="Динамічне перепризначення таблиці векторів через VTOR")


if __name__ == '__main__':
    fig_vector_table_layout()
    fig_vtor_relocation()
    print("Generated 2 vector-table figures successfully.")
