# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Від вентиля до програмованого чипа'."""

import sys
import os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig1_from_logic_gates_to_alu():
    """Фігура 1: Від дискретних вентилів до арифметико-логічного пристрою (АЛП)."""
    w, h = 860, 420
    frags = []

    # Ліва частина: базові дискретні блоки
    frags.append(rect(20, 45, 250, 350, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(145, 75, "Комбінаційні елементи", size=14, bold=True))

    b1, _, _ = textbox(145, 125, "1-бітний суматор (ADD)\nSum = A ⊕ B ⊕ Cin\nCout = (A∧B) ∨ (Cin∧(A⊕B))", size=11, min_w=220)
    frags.append(b1)

    b2, _, _ = textbox(145, 205, "Побітові логічні вентилі\nAND, OR, XOR, NOT\n(паралельно для всіх бітів)", size=11, min_w=220)
    frags.append(b2)

    b3, _, _ = textbox(145, 285, "Схема віднімання / інверсії\nB_inv = B ⊕ Sub_mode\nCin = Sub_mode (доповняльний код)", size=11, min_w=220)
    frags.append(b3)

    b4, _, _ = textbox(145, 355, "Зсувач (Barrel Shifter)\nЛогічний/арифметичний зсув", size=11, min_w=220)
    frags.append(b4)

    # Стрілки зведення до мультиплексора функцій
    frags.append(arrow(270, 125, 360, 180, color=LINE, sw=1.5))
    frags.append(arrow(270, 205, 360, 210, color=LINE, sw=1.5))
    frags.append(arrow(270, 285, 360, 240, color=LINE, sw=1.5))
    frags.append(arrow(270, 355, 360, 270, color=LINE, sw=1.5))

    # Центральна частина: АЛП з вибором операції
    frags.append(rect(360, 130, 270, 200, fill="#edf2f7", stroke=LINE, sw=2, rx=8))
    frags.append(text(495, 160, "АЛП (ALU)", size=16, bold=True))
    frags.append(text(495, 185, "Арифметико-логічний блок", size=12, color=MUTED))

    # Входи в АЛП
    frags.append(arrow(320, 80, 410, 130, color=POS, sw=2))
    frags.append(text(310, 75, "Операнд A (N бітів)", size=12, color=POS, bold=True))

    frags.append(arrow(580, 80, 500, 130, color=NEG, sw=2))
    frags.append(text(590, 75, "Операнд B (N бітів)", size=12, color=NEG, bold=True))

    # Керування операцією
    frags.append(arrow(495, 385, 495, 330, color="#d97706", sw=2))
    frags.append(text(495, 402, "Код операції: ALU_Op (ADD, SUB, AND, OR, SLT)", size=11, color="#b45309", bold=True))

    # Виходи з АЛП
    frags.append(arrow(630, 200, 720, 200, color=FIELD, sw=2.2))
    frags.append(text(780, 195, "Результат (Y)", size=13, color=FIELD, bold=True))
    frags.append(text(780, 212, "Шина N бітів", size=10, color=MUTED))

    # Прапорці стану (Status Register / Flags)
    frags.append(rect(690, 260, 150, 120, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(765, 282, "Прапорці стану (Flags)", size=12, bold=True, color="#92400e"))
    frags.append(text(765, 305, "Z (Zero) : Y == 0", size=11, color=INK))
    frags.append(text(765, 325, "N (Negative) : MSB == 1", size=11, color=INK))
    frags.append(text(765, 345, "C (Carry) : перенос", size=11, color=INK))
    frags.append(text(765, 365, "V (Overflow) : переповн.", size=11, color=INK))

    frags.append(arrow(630, 270, 690, 300, color="#d97706", sw=1.5))

    render(os.path.join(IMG_DIR, "from-logic-gates-to-alu.svg"), w, h, *frags,
           title="Від дискретних вентилів до обчислювального ядра АЛП")


def fig2_datapath_and_control_unit():
    """Фігура 2: Тракт даних і пристрій керування процесорного ядра."""
    w, h = 900, 480
    frags = []

    # 1. Program Counter (PC)
    pc_box, _, _ = textbox(90, 140, "Program Counter\n(PC)\nЛічильник команд", size=12, min_w=120, fill="#e0e7ff", stroke="#4338ca")
    frags.append(pc_box)

    # 2. Instruction Memory
    im_box, _, _ = textbox(250, 140, "Пам'ять команд\n(ROM / Flash)\nЗбережена програма", size=12, min_w=140, fill="#f1f5f9", stroke=LINE)
    frags.append(im_box)
    frags.append(arrow(150, 140, 180, 140, color=LINE, sw=2))
    frags.append(text(165, 130, "Адреса", size=10, color=MUTED))

    # Стрілка інструкції з пам'яті
    frags.append(arrow(320, 140, 390, 140, color=LINE, sw=2))
    frags.append(text(355, 130, "Інструкція (32/16 біт)", size=10, color=MUTED))

    # 3. Control Unit (Пристрій керування)
    cu_box, _, _ = textbox(370, 320, "Пристрій керування\n(Control Unit / FSM)\nДекодер коду операції", size=12, min_w=170, fill="#fef3c7", stroke="#d97706")
    frags.append(cu_box)
    frags.append(arrow(355, 140, 355, 275, color="#d97706", sw=1.8))
    frags.append(text(315, 210, "Opcode / Func", size=10, color="#b45309"))

    # 4. Register File (Регістровий файл)
    rf_box, _, _ = textbox(470, 140, "Регістровий файл\n(R0...R15 / R31)\n2 порти зчитування\n1 порт запису", size=12, min_w=140, fill="#e0f2fe", stroke="#0369a1")
    frags.append(rf_box)
    frags.append(arrow(355, 140, 400, 140, color=LINE, sw=1.5))

    # Сигнали керування з CU до блоків
    frags.append(arrow(455, 320, 470, 210, color="#d97706", sw=1.5))
    frags.append(text(495, 260, "RegWrite", size=10, color="#b45309"))

    # 5. ALU (АЛП)
    alu_box, _, _ = textbox(650, 140, "АЛП (ALU)\nADD / SUB\nAND / OR / XOR\nПорівняння", size=12, min_w=130, fill="#edf2f7", stroke=LINE)
    frags.append(alu_box)

    # Шини операндів від Register File до ALU
    frags.append(arrow(540, 120, 585, 120, color=POS, sw=1.8))
    frags.append(text(562, 110, "Bus A", size=10, color=POS))
    frags.append(arrow(540, 160, 585, 160, color=NEG, sw=1.8))
    frags.append(text(562, 175, "Bus B", size=10, color=NEG))

    # ALU_Op з CU до ALU
    frags.append(line(455, 335, 650, 335, color="#d97706", sw=1.5, dash="4,3"))
    frags.append(line(650, 335, 650, 205, color="#d97706", sw=1.5, dash="4,3"))
    frags.append(arrow(650, 205, 650, 195, color="#d97706", sw=1.5))
    frags.append(text(550, 348, "Керування операцією (ALU_Op)", size=10, color="#b45309"))

    # 6. Data Memory (Пам'ять даних / ОЗП)
    dm_box, _, _ = textbox(810, 140, "Пам'ять даних\n(SRAM / ОЗП)\nЗавантаження/Запис", size=12, min_w=130, fill="#f1f5f9", stroke=LINE)
    frags.append(dm_box)
    frags.append(arrow(715, 140, 745, 140, color=LINE, sw=1.8))
    frags.append(text(730, 130, "Адреса", size=10, color=MUTED))

    # Зворотний зв'язок: Write-Back у регістровий файл
    frags.append(line(810, 200, 810, 440, color=FIELD, sw=1.8))
    frags.append(line(810, 440, 430, 440, color=FIELD, sw=1.8))
    frags.append(arrow(430, 440, 430, 205, color=FIELD, sw=1.8))
    frags.append(text(620, 455, "Шина повернення результату (Write-Back Data)", size=11, color=FIELD, bold=True))

    # Зворотний зв'язок: Оновлення PC (PC + 4 або Branch/Jump)
    frags.append(line(650, 85, 650, 45, color=LINE, sw=1.5))
    frags.append(line(650, 45, 90, 45, color=LINE, sw=1.5))
    frags.append(arrow(90, 45, 90, 85, color=LINE, sw=1.5))
    frags.append(text(370, 38, "Оновлення адреси команди: PC + 4 або перехід (Branch/Jump)", size=11, color=INK))

    render(os.path.join(IMG_DIR, "datapath-and-control-unit.svg"), w, h, *frags,
           title="Тракт даних (Datapath) та пристрій керування процесорного ядра")


def fig3_instruction_pipeline_stages():
    """Фігура 3: 5-стадійний конвеєр виконання команд RISC-процесора."""
    w, h = 940, 390
    frags = []

    # Заголовки стадій конвеєра
    stages = [
        ("1. IF (Fetch)", "Вибірка команди\nз пам'яті (PC)"),
        ("2. ID (Decode)", "Декодування,\nчитання регістрів"),
        ("3. EX (Execute)", "Обчислення в АЛП,\nрозрахунок адреси"),
        ("4. MEM (Memory)", "Доступ до пам'яті\nданих (Load/Store)"),
        ("5. WB (Writeback)", "Запис результату\nв регістровий файл")
    ]

    colors = ["#e0e7ff", "#fef3c7", "#edf2f7", "#e0f2fe", "#dcfce7"]
    strokes = ["#4338ca", "#d97706", "#475569", "#0284c7", "#16a34a"]

    for i, (title, desc) in enumerate(stages):
        x = 40 + i * 175
        frags.append(rect(x, 48, 160, 75, fill=colors[i], stroke=strokes[i], sw=1.8, rx=6))
        frags.append(text(x + 80, 70, title, size=12, bold=True, color=strokes[i]))
        frags.append(mtext(x + 80, 93, desc, size=10, color=INK))
        if i < 4:
            # Міжстадійний регістр (Pipeline Register)
            frags.append(arrow(x + 160, 85, x + 175, 85, color=LINE, sw=2))
            frags.append(rect(x + 164, 60, 7, 50, fill="#334155", stroke=LINE, sw=1, rx=2))

    frags.append(text(470, 145, "Міжстадійні регістри (Pipeline Registers) фіксують стан на кожному фронті тактового сигналу", size=11, color=MUTED, italic=True))

    # Діаграма просування команд у часі (просторово-часова сітка)
    frags.append(rect(40, 170, 860, 195, fill="#fafafa", stroke=LINE, sw=1, rx=6))
    frags.append(text(105, 195, "Команда / Такт", size=11, bold=True))

    cycles = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
    for c_idx, c_name in enumerate(cycles):
        frags.append(text(230 + c_idx * 80, 195, c_name, size=11, bold=True, color="#4338ca"))

    # Сітка для інструкцій
    instrs = [
        ("Instr 1: ADD R1, R2, R3", 0),
        ("Instr 2: SUB R4, R5, R6", 1),
        ("Instr 3: LDR R7, [R1]", 2),
        ("Instr 4: AND R8, R7, R2", 3),
    ]

    stage_names = ["IF", "ID", "EX", "MEM", "WB"]
    for row_idx, (iname, start_cycle) in enumerate(instrs):
        y = 228 + row_idx * 30
        frags.append(text(120, y + 5, iname, size=10, anchor="start", bold=True))
        for s_idx, sname in enumerate(stage_names):
            cx = 230 + (start_cycle + s_idx) * 80
            frags.append(rect(cx - 32, y - 10, 64, 22, fill=colors[s_idx], stroke=strokes[s_idx], sw=1, rx=4))
            frags.append(text(cx, y + 5, sname, size=10, bold=True, color=strokes[s_idx]))

    render(os.path.join(IMG_DIR, "instruction-pipeline-stages.svg"), w, h, *frags,
           title="Стадії 5-рівневого конвеєра та одночасне виконання інструкцій у часі")


def fig4_microcontroller_die_integration():
    """Фігура 4: Інтеграція процесорного ядра, шин та периферії на кристалі мікроконтролера."""
    w, h = 880, 440
    frags = []

    # Зовнішня межа мікроконтролера (Silicon Die / Package)
    frags.append(rect(30, 45, 820, 375, fill="#f8fafc", stroke="#0f172a", sw=2, rx=12))
    frags.append(text(440, 70, "Кристал мікроконтролера (Single-Chip Microcontroller / SoC)", size=15, bold=True))

    # 1. Процесорне ядро (CPU Core)
    frags.append(rect(50, 95, 230, 230, fill="#e0e7ff", stroke="#3730a3", sw=2, rx=8))
    frags.append(text(165, 125, "Процесорне ядро (CPU Core)", size=13, bold=True, color="#3730a3"))
    frags.append(rect(65, 145, 200, 45, fill="#ffffff", stroke="#4338ca", sw=1, rx=4))
    frags.append(text(165, 172, "АЛП + Регістровий файл", size=11, bold=True))
    frags.append(rect(65, 200, 200, 45, fill="#ffffff", stroke="#4338ca", sw=1, rx=4))
    frags.append(text(165, 227, "Пристрій керування + PC", size=11, bold=True))
    frags.append(rect(65, 255, 200, 55, fill="#ffffff", stroke="#4338ca", sw=1, rx=4))
    frags.append(text(165, 277, "Контролер переривань (NVIC)", size=10, color=MUTED))
    frags.append(text(165, 297, "Апаратний SysTick-таймер", size=10, color=MUTED))

    # 2. Пам'ять (Flash ROM + SRAM)
    frags.append(rect(320, 95, 230, 105, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(435, 125, "Flash ROM (Пам'ять програм)", size=12, bold=True, color="#92400e"))
    frags.append(text(435, 150, "Зберігає двійковий код прошивки", size=10, color=INK))
    frags.append(text(435, 172, "Енергонезалежна (Non-volatile)", size=10, color=MUTED))

    frags.append(rect(320, 215, 230, 105, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=6))
    frags.append(text(435, 245, "SRAM (Пам'ять даних)", size=12, bold=True, color="#075985"))
    frags.append(text(435, 270, "Зберігає змінні, стек, купу", size=10, color=INK))
    frags.append(text(435, 292, "Швидкий однотактовий доступ", size=10, color=MUTED))

    # 3. Системна шинна матриця (Bus Matrix: AHB / APB)
    frags.append(rect(580, 95, 60, 225, fill="#334155", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(610, 175, "ШИННА", size=11, bold=True, color="#ffffff"))
    frags.append(text(610, 205, "МАТРИЦЯ", size=11, bold=True, color="#ffffff"))
    frags.append(text(610, 235, "(AHB/APB)", size=9, bold=True, color="#94a3b8"))

    # Лінії зв'язку до шини
    frags.append(arrow(280, 210, 580, 210, color="#4338ca", sw=2))
    frags.append(arrow(550, 150, 580, 150, color="#d97706", sw=1.8))
    frags.append(arrow(550, 265, 580, 265, color="#0284c7", sw=1.8))

    # 4. Вбудована периферія
    frags.append(rect(670, 95, 165, 225, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(752, 120, "Периферійні блоки", size=12, bold=True))

    periphs = ["GPIO (Введення/виведення)", "Таймери (TIM, PWM)", "UART / USART", "SPI / I2C шини", "АЦП / ЦАП (ADC/DAC)", "Контролер DMA"]
    for p_idx, pname in enumerate(periphs):
        py = 145 + p_idx * 28
        frags.append(rect(680, py - 10, 145, 22, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
        frags.append(text(752, py + 5, pname, size=9, bold=True))

    frags.append(arrow(640, 210, 670, 210, color=LINE, sw=2))

    # Нижня частина: Фізичні виводи кристала (ПІНИ)
    frags.append(rect(50, 350, 785, 50, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(442, 375, "Фізичні виводи корпусу мікроконтролера (Pins / Pads)", size=12, bold=True, color="#991b1b"))
    frags.append(text(442, 392, "VCC, GND, Кварцовий резонатор (XTAL), Reset (NRST), GPIO-порти", size=10, color=INK))

    frags.append(arrow(752, 320, 752, 350, color="#ef4444", sw=1.8))
    frags.append(arrow(165, 325, 165, 350, color="#ef4444", sw=1.8))

    render(os.path.join(IMG_DIR, "microcontroller-die-integration.svg"), w, h, *frags,
           title="Інтеграція процесорного ядра, пам'яті, шин та периферії в єдиний кристал")


if __name__ == "__main__":
    fig1_from_logic_gates_to_alu()
    fig2_datapath_and_control_unit()
    fig3_instruction_pipeline_stages()
    fig4_microcontroller_die_integration()
    print("Всі фігури згенеровано успішно.")
