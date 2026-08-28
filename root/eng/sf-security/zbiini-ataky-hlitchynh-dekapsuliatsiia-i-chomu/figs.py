# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Збійні атаки, глітчинг, декапсуляція»."""

import os
import sys

# Додаємо scripts до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_glitch_timing():
    """Фігура 1: Часова діаграма збою напруги та порушення часу встановлення (Setup Violation)."""
    w, h = 760, 360
    frags = []

    # Заголовок блоків
    frags.append(rect(10, 10, 740, 340, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Ліва колонка — мітки сигналів
    frags.append(text(75, 55, "CLK (100 МГц)", size=12, color=INK, bold=True, anchor="middle"))
    frags.append(text(75, 135, "Живлення Vdd", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(75, 215, "Дані АЛП (Data)", size=12, color=NEG, bold=True, anchor="middle"))
    frags.append(text(75, 295, "Вихід тригера Q", size=12, color=FIELD, bold=True, anchor="middle"))

    # Роздільні лінії
    for y in [95, 175, 255]:
        frags.append(line(15, y, 735, y, color="#edf2f7", sw=1, dash="4,4"))

    # 1. Тактовий сигнал CLK (період 100 px = 10 нс, фронти на x=170, 270, 370, 470, 570, 670)
    clk_pts = [
        (130, 70), (170, 70), (170, 40), (220, 40), (220, 70),
        (270, 70), (270, 40), (320, 40), (320, 70),
        (370, 70), (370, 40), (420, 40), (420, 70),
        (470, 70), (470, 40), (520, 40), (520, 70),
        (570, 70), (570, 40), (620, 40), (620, 70),
        (670, 70), (670, 40), (710, 40)
    ]
    for i in range(len(clk_pts) - 1):
        frags.append(line(clk_pts[i][0], clk_pts[i][1], clk_pts[i+1][0], clk_pts[i+1][1], color=INK, sw=2))

    # Вертикальні пунктири тактових фронтів
    for x in [270, 370, 470, 570]:
        frags.append(line(x, 30, x, 325, color="#cbd5e1", sw=1, dash="3,3"))

    # 2. Напруга Vdd (номінал 1.2 В на y=120, просідання до 0.5 В на y=155 біля x=330..365)
    frags.append(line(130, 120, 320, 120, color=POS, sw=2.5))
    frags.append(line(320, 120, 335, 155, color=POS, sw=2.5))
    frags.append(line(335, 155, 360, 155, color=POS, sw=2.5))
    frags.append(line(360, 155, 375, 120, color=POS, sw=2.5))
    frags.append(line(375, 120, 710, 120, color=POS, sw=2.5))

    # Пояснення імпульсу збою
    frags.append(text(348, 170, "Глітч: 20 нс, 0.5 В", size=10, color=POS, bold=True, anchor="middle"))

    # 3. Дані на вході тригера (Data)
    # Штатне поширення (на такті 1, фронт на 270): стабілізується на x=200 (t_pd = 3 нс)
    frags.append(line(130, 230, 175, 230, color=NEG, sw=2))
    frags.append(line(175, 230, 195, 205, color=NEG, sw=2))
    frags.append(line(175, 205, 195, 230, color=NEG, sw=2))
    frags.append(line(195, 205, 370, 205, color=NEG, sw=2))

    # Збійне поширення: через падіння Vdd t_pd розтягується, сигнал змінюється лише на x=395 (після фронту 370!)
    frags.append(line(370, 205, 395, 230, color=NEG, sw=2, dash="4,2"))
    frags.append(line(370, 230, 395, 205, color=NEG, sw=2, dash="4,2"))
    frags.append(line(395, 230, 710, 230, color=NEG, sw=2))

    # Зона порушення часу встановлення
    frags.append(rect(345, 190, 25, 35, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    frags.append(text(357, 185, "Setup Violation", size=9, color=POS, bold=True, anchor="middle"))

    # 4. Вихід тригера Q
    # Такт 1 (x=270): коректне замикання нового значення
    frags.append(line(130, 305, 270, 305, color=FIELD, sw=2.5))
    frags.append(line(270, 305, 275, 280, color=FIELD, sw=2.5))
    frags.append(line(275, 280, 470, 280, color=FIELD, sw=2.5))

    # Такт 2 (x=370): тригер захоплює старий/хибний стан через запізнення входу
    frags.append(rect(370, 270, 100, 35, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(420, 292, "Хибний стан (NOP / 0)", size=10, color="#b45309", bold=True, anchor="middle"))
    frags.append(line(470, 280, 570, 280, color=FIELD, sw=2.5))
    frags.append(line(570, 280, 575, 305, color=FIELD, sw=2.5))
    frags.append(line(575, 305, 710, 305, color=FIELD, sw=2.5))

    # Інформаційний підпис вгорі праворуч
    frags.append(text(540, 48, "Тактовий фронт (Latch Edge)", size=10, color=MUTED, anchor="middle"))
    frags.append(arrow(540, 52, 473, 52, color=MUTED, sw=1.2))

    render(os.path.join(IMG_DIR, "glitch-waveform-timing.svg"), w, h, *frags)


def fig_instruction_skip():
    """Фігура 2: Конвеєр процесора та пропуск перевірки пароля/підпису."""
    w, h = 760, 310
    frags = []

    frags.append(rect(10, 10, 740, 290, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Три колонки: 1. Штатний стан -> 2. Введення збою -> 3. Результат у конвеєрі
    # Блок 1: Код перевірки
    frags.append(fitbox(25, 25, 215, 260,
                        "1. Штатна логіка захисту\n\n"
                        "CMP   R0, #0       ; R0=перевірка\n"
                        "BEQ   lock_device  ; якщо 0 -> бан\n"
                        "LDR   R1, =KEY_PTR ; доступ до ключа\n"
                        "BL    decrypt_boot ; розшифрування\n\n"
                        "Результат: R0 == 0\n"
                        "-> перехід на блокування\n"
                        "-> пристрій захищено",
                        size=11, pad=10, fill="#f8fafc", stroke="#94a3b8"))

    # Стрілка 1 -> 2
    frags.append(arrow(245, 155, 275, 155, color=LINE, sw=2))

    # Блок 2: Фізичний глітч
    frags.append(fitbox(280, 25, 205, 260,
                        "2. Ін'єкція збою (Глітч)\n\n"
                        "Момент: виконання BEQ\n"
                        "Тривалість: 15–30 нс\n"
                        "Вплив: просідання Vdd\n\n"
                        "Вентилі прапорців не встигають\n"
                        "перемкнутися (t_pd > T_clk).\n\n"
                        "Декодер бачить зміщення 0\n"
                        "або опкод стає NOP (0xBF00).",
                        size=11, pad=10, fill="#fef2f2", stroke=POS))

    # Стрілка 2 -> 3
    frags.append(arrow(490, 155, 520, 155, color=POS, sw=2))

    # Блок 3: Зламаний конвеєр
    frags.append(fitbox(525, 25, 210, 260,
                        "3. Зламаний потік (Bypass)\n\n"
                        "CMP   R0, #0       ; виконано\n"
                        "[ГЛІТЧ] -> BEQ стає NOP\n"
                        "LDR   R1, =KEY_PTR ; ВИКОНАНО!\n"
                        "BL    decrypt_boot ; ВИКОНАНО!\n\n"
                        "Результат: умовний\n"
                        "перехід проігноровано,\n"
                        "захист RDP/Boot знято!",
                        size=11, pad=10, fill="#fffbeb", stroke="#d97706"))

    render(os.path.join(IMG_DIR, "instruction-skip-pipeline.svg"), w, h, *frags)


def fig_decapsulation_layers():
    """Фігура 3: Шари кремнієвого кристала, декапсуляція та методи фізичного доступу."""
    w, h = 760, 370
    frags = []

    frags.append(rect(10, 10, 740, 350, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Шари структури чипа (зверху вниз)
    # 1. Епоксидний компаунд (Decapsulated zone)
    frags.append(rect(30, 30, 420, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(240, 58, "Епоксидний корпус (видалено HNO3 / H2SO4)", size=12, color=POS, bold=True, anchor="middle"))

    # 2. Верхній захисний екран (Active Tamper Shield - Metal Top)
    frags.append(rect(30, 85, 420, 35, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(240, 107, "Активна захисна сітка (Top Metal Shield)", size=12, color="#b45309", bold=True, anchor="middle"))

    # 3. Шари металізації (M3-M1 Interconnects)
    frags.append(rect(30, 130, 420, 70, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(240, 160, "Шари металізації M1–M6 (шини даних і живлення)", size=12, color=INK, bold=True, anchor="middle"))
    frags.append(text(240, 185, "Тут проходять відкриті шини Flash / SRAM / Crypto", size=10, color=MUTED, anchor="middle"))

    # 4. Активний кремній: транзистори, комірки ROM/SRAM
    frags.append(rect(30, 210, 420, 65, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(240, 240, "Активний шар транзисторів (CMOS Gates, ROM, SRAM)", size=12, color=NEG, bold=True, anchor="middle"))
    frags.append(text(240, 262, "Оптичне зчитування маски ROM / LFI ін'єкції", size=10, color=MUTED, anchor="middle"))

    # 5. Кремнієва підкладка (Bulk Silicon Substrate)
    frags.append(rect(30, 285, 420, 55, fill="#f8fafc", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(240, 318, "Кремнієва підкладка (доступ для ІЧ-лазера 1064 нм)", size=12, color=INK, bold=True, anchor="middle"))

    # Права панель: Вектори фізичних інвазивних атак
    frags.append(fitbox(470, 30, 260, 310,
                        "Вектори інвазивного злому:\n\n"
                        "• Декапсуляція:\n"
                        "  Кислотне травлення оголює кристал\n"
                        "  без пошкодження золотих розварок.\n\n"
                        "• Мікрозондування (Microprobing):\n"
                        "  Вольфрамові голки підключаються\n"
                        "  прямо до шин M2/M3 для дампу даних.\n\n"
                        "• FIB (Іонний пучок):\n"
                        "  Перерізання ліній захисних сенсорів\n"
                        "  та перемикання бітів eFuse.\n\n"
                        "• Backside LFI:\n"
                        "  Інфрачервоний лазер крізь підкладку\n"
                        "  збуджує фотострум у p-n переходах.",
                        size=11, pad=10, fill="#f8fafc", stroke="#94a3b8"))

    # Стрілки атак до шарів
    frags.append(arrow(470, 100, 452, 100, color="#d97706", sw=1.5))
    frags.append(arrow(470, 165, 452, 165, color=POS, sw=1.5))
    frags.append(arrow(470, 315, 452, 315, color=NEG, sw=1.5))

    render(os.path.join(IMG_DIR, "optical-decapsulation-layers.svg"), w, h, *frags)


def fig_hardware_defenses():
    """Фігура 4: Апаратні механізми захисту від збоїв та обходу обфускації."""
    w, h = 760, 320
    frags = []

    frags.append(rect(10, 10, 740, 300, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Чотири блоки апаратного захисту
    # 1. Детектори глітчів
    frags.append(fitbox(25, 25, 340, 125,
                        "1. Апаратні детектори збоїв\n\n"
                        "• Аналоговий монітор Vdd (Low/High Voltage Detect)\n"
                        "• Кільцевий генератор (Ring Oscillator) для тактових глітчів\n"
                        "• Фантомний критичний шлях (Dummy Delay Line)\n"
                        "-> Миттєве апаратне переривання / HardFault",
                        size=11, pad=8, fill="#f0fdf4", stroke=FIELD))

    # 2. Диференційна Dual-Rail логіка
    frags.append(fitbox(390, 25, 340, 125,
                        "2. Dual-Rail логіка з передзарядом\n\n"
                        "• Передає два взаємно-доповняльні сигнали: D та D_bar\n"
                        "• Інваріант: D != D_bar у кожному такті\n"
                        "• Будь-який збій (0,0 або 1,1) викликає апаратну тривогу\n"
                        "-> Неможливо змінити один біт лазером/глітчем",
                        size=11, pad=8, fill="#eff6ff", stroke=NEG))

    # 3. Активна захисна сітка (Tamper Shield)
    frags.append(fitbox(25, 165, 340, 130,
                        "3. Активний захисний екран (Mesh)\n\n"
                        "• Верхній шар металу з псевдовипадковим сигналом (LFSR)\n"
                        "• Обрив мікрозондом або травлення кислотою змінює стан\n"
                        "• Контролер тампера миттєво стирає ключі (Zeroization)\n"
                        "-> Блокує інвазивний мікропробінг і FIB",
                        size=11, pad=8, fill="#fef2f2", stroke=POS))

    # 4. Апаратне шифрування шин пам'яті
    frags.append(fitbox(390, 165, 340, 130,
                        "4. Шифрування шин та пам'яті\n\n"
                        "• Апаратний AES-XTS/CTR модуль на шині Flash/SRAM\n"
                        "• Скремблювання адрес і ліній даних\n"
                        "• Програмна обфускація не потрібна: шина апаратно криптостійка\n"
                        "-> Зчитаний мікрозондом дамп є випадковим шумом",
                        size=11, pad=8, fill="#faf5ff", stroke="#7c3aed"))

    render(os.path.join(IMG_DIR, "hardware-defenses-overview.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_glitch_timing()
    fig_instruction_skip()
    fig_decapsulation_layers()
    fig_hardware_defenses()
    print("Всі фігури успішно згенеровано.")
