# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE  = NEG      # #2457d6 - шини даних, регістри
RED   = POS      # #c0392b - такти, строби керування WR/RD
GREEN = FIELD    # #27ae60 - порти вводу-виводу MMIO, периферія
AMBER = "#b8860b" # адреси, пам'ять програм
GREY  = "#8a8a8a" # неактивне, фон
GRID  = "#dfe3e8"

def clk_tri(x, y, size=7, color=INK):
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.3"/>' % (x, y - size, x + size, y, x, y + size, color))


# ── 1. Повний синтез процесорної системи з будівельних блоків ────────────────
def fig_cpu_synthesis():
    W, H = 940, 560
    p = []
    p.append(text(W / 2, 26, "Синтез мікропроцесорної системи: ядро, шини та адресний простір", size=16, bold=True))

    # Рамка процесорного ядра (CPU Core)
    p.append(rect(30, 55, 410, 480, fill="#f8fafc", stroke=BLUE, sw=2, rx=8))
    p.append(text(235, 80, "ПРОЦЕСОРНЕ ЯДРО (CPU CORE)", size=13, bold=True, color=BLUE))

    # Блок PC (Program Counter)
    p.append(rect(50, 105, 160, 65, fill="#fffbeb", stroke=AMBER, sw=1.5))
    p.append(text(130, 127, "Лічильник команд (PC)", size=11, bold=True, color=AMBER))
    p.append(text(130, 145, "16-бітний регістр +1", size=10, color=MUTED))
    p.append(text(130, 160, "Адреса інструкції", size=9.5, color=INK))
    p.append(clk_tri(50, 137))

    # Блок IR (Instruction Register)
    p.append(rect(240, 105, 180, 65, fill="#fef2f2", stroke=RED, sw=1.5))
    p.append(text(330, 127, "Регістр інструкцій (IR)", size=11, bold=True, color=RED))
    p.append(text(330, 145, "Фіксує код команди", size=10, color=MUTED))
    p.append(text(330, 160, "Opcode [7:0]", size=10, bold=True, color=INK))
    p.append(clk_tri(240, 137))

    # Блок Control Unit (Дешифратор / Керуючий автомат)
    p.append(rect(240, 195, 180, 110, fill="#fef2f2", stroke=RED, sw=1.6))
    p.append(text(330, 218, "Пристрій керування (CU)", size=11, bold=True, color=RED))
    p.append(text(330, 236, "Дешифратор інструкцій", size=10, bold=True, color=INK))
    p.append(text(330, 256, "Генератор мікрооперацій", size=9.5, color=MUTED))
    p.append(text(330, 274, "Строби: RD, WR, MUX", size=9.5, color=RED))
    p.append(text(330, 292, "Керування АЛП і регістрами", size=9.5, color=MUTED))

    # Зв'язок IR -> CU
    p.append(arrow(330, 170, 330, 195, color=RED))

    # Регістровий файл (Register File)
    p.append(rect(50, 205, 160, 155, fill="#eff6ff", stroke=BLUE, sw=1.5))
    p.append(text(130, 227, "Регістровий файл", size=11, bold=True, color=BLUE))
    p.append(rect(65, 238, 130, 24, fill="#ffffff", stroke=BLUE, sw=1))
    p.append(text(130, 254, "ACC (Акумулятор, 8 біт)", size=9.5, bold=True, color=INK))
    p.append(rect(65, 268, 130, 24, fill="#ffffff", stroke=BLUE, sw=1))
    p.append(text(130, 284, "R0 (Загальний, 8 біт)", size=9.5, color=INK))
    p.append(rect(65, 298, 130, 24, fill="#ffffff", stroke=BLUE, sw=1))
    p.append(text(130, 314, "R1 (Загальний, 8 біт)", size=9.5, color=INK))
    p.append(text(130, 345, "D-тригери з вибіркою", size=9.5, color=MUTED))

    # Блок АЛП (ALU)
    p.append(rect(50, 390, 160, 125, fill="#f0fdf4", stroke=GREEN, sw=1.6))
    p.append(text(130, 412, "АЛП (ALU)", size=12, bold=True, color=GREEN))
    p.append(text(130, 430, "Комбінаційна схема", size=9.5, color=MUTED))
    p.append(text(130, 448, "ADD / SUB / AND / OR / XOR", size=9.5, bold=True, color=INK))
    p.append(rect(65, 462, 130, 42, fill="#ffffff", stroke=GREEN, sw=1))
    p.append(text(130, 479, "Регістр прапорців (FLAGS)", size=9.5, bold=True, color=INK))
    p.append(text(130, 495, "Z (Zero), C (Carry), N (Neg)", size=9, color=MUTED))

    # Зв'язки всередині ядра
    # Регістри -> АЛП операнди
    p.append(arrow(100, 360, 100, 390, color=BLUE))
    p.append(arrow(160, 360, 160, 390, color=BLUE))
    # АЛП результат -> Регістри (зворотний зв'язок)
    p.append(line(50, 450, 38, 450, color=GREEN))
    p.append(line(38, 450, 38, 280, color=GREEN))
    p.append(arrow(38, 280, 50, 280, color=GREEN))
    p.append(text(44, 365, "Результат", size=9, color=GREEN, anchor="middle"))

    # CU керує АЛП та Регістрами
    p.append(line(270, 305, 270, 420, color=RED, dash="3,3"))
    p.append(arrow(270, 420, 210, 420, color=RED))
    p.append(text(250, 410, "Код операції", size=9, color=RED))

    p.append(line(250, 250, 210, 250, color=RED, dash="3,3"))
    p.append(text(225, 242, "WR_REG", size=9, color=RED))

    # FLAGS -> CU (для умовних переходів)
    p.append(line(195, 485, 390, 485, color=MUTED))
    p.append(line(390, 485, 390, 305, color=MUTED))
    p.append(arrow(390, 305, 390, 305, color=MUTED))
    p.append(text(300, 476, "Прапорці Z/C -> умовний стрибок", size=9, color=MUTED))

    # ── СИСТЕМНА ШИНА (ВЕРТИКАЛЬНІ ЛІНІЇ ПОСЕРЕДИНІ) ─────────────────────────
    # Шина адреси (Address Bus, 16 біт) - AMBER
    p.append(rect(470, 70, 22, 455, fill="#fef3c7", stroke=AMBER, sw=1.5, rx=3))
    p.append(text(481, 290, "Ш И Н А   А Д Р Е С И   A [ 1 5 : 0 ]", size=10, bold=True, color=AMBER, anchor="middle"))

    # Шина даних (Data Bus, 8 біт) - BLUE
    p.append(rect(510, 70, 22, 455, fill="#dbeafe", stroke=BLUE, sw=1.5, rx=3))
    p.append(text(521, 290, "Ш И Н А   Д А Н И Х   D [ 7 : 0 ]", size=10, bold=True, color=BLUE, anchor="middle"))

    # Шина керування (Control Bus: RD, WR) - RED
    p.append(rect(550, 70, 22, 455, fill="#fee2e2", stroke=RED, sw=1.5, rx=3))
    p.append(text(561, 290, "К Е Р У В А Н Н Я   R D   /   W R", size=10, bold=True, color=RED, anchor="middle"))

    # З'єднання Ядро -> Шини
    # PC -> Шина адреси
    p.append(arrow(210, 137, 470, 137, color=AMBER, sw=2))
    p.append(text(280, 130, "Адреса вибірки", size=9.5, color=AMBER))

    # Шина даних -> IR
    p.append(arrow(510, 137, 420, 137, color=BLUE, sw=2))
    p.append(text(465, 130, "Opcode", size=9.5, color=BLUE))

    # Регістри <-> Шина даних (двоспрямована)
    p.append(line(210, 310, 510, 310, color=BLUE, sw=2))
    p.append(arrow(210, 310, 210, 310, color=BLUE))
    p.append(arrow(510, 310, 510, 310, color=BLUE))
    p.append(text(360, 303, "Читання / Запис операндів", size=9.5, color=BLUE))

    # CU -> Шина керування (RD, WR)
    p.append(arrow(420, 270, 550, 270, color=RED, sw=2))
    p.append(text(465, 263, "/RD, /WR", size=9.5, color=RED))

    # ── ПРАВА ЧАСТИНА: ДЕШИФРАТОР, ПАМ'ЯТЬ ТА MMIO ПЕРИФЕРІЯ ──────────────────
    # Адресний дешифратор (Address Decoder - 74HC138)
    p.append(rect(600, 80, 130, 80, fill="#f3f4f6", stroke=INK, sw=1.6))
    p.append(text(665, 105, "Адресний дешифратор", size=10.5, bold=True, color=INK))
    p.append(text(665, 123, "Логіка A[15:14]", size=9.5, color=MUTED))
    p.append(text(665, 142, "Вибір чіпа (/CS)", size=9.5, bold=True, color=RED))

    # Вхід дешифратора від шини адреси
    p.append(arrow(492, 120, 600, 120, color=AMBER, sw=1.8))
    p.append(text(545, 112, "A[15:14]", size=9, color=AMBER))

    # Блок 1: Пам'ять програм (ROM / Flash)
    p.append(rect(770, 75, 150, 105, fill="#fffbeb", stroke=AMBER, sw=1.6))
    p.append(text(845, 98, "ПАМ'ЯТЬ ПРОГРАМ", size=11, bold=True, color=AMBER))
    p.append(text(845, 116, "ROM / Flash (16 КБ)", size=10, bold=True, color=INK))
    p.append(text(845, 136, "0x0000 – 0x3FFF", size=9.5, color=MUTED))
    p.append(text(845, 154, "Вектор скидання, код", size=9, color=MUTED))
    p.append(text(845, 168, "Тільки читання (/RD)", size=9, color=RED))

    # CS від дешифратора до ROM
    p.append(arrow(730, 110, 770, 110, color=RED))
    p.append(text(748, 102, "/CS0", size=9, color=RED))

    # Блок 2: Оперативна пам'ять даних (SRAM)
    p.append(rect(770, 210, 150, 110, fill="#eff6ff", stroke=BLUE, sw=1.6))
    p.append(text(845, 233, "ПАМ'ЯТЬ ДАНИХ", size=11, bold=True, color=BLUE))
    p.append(text(845, 251, "SRAM (16 КБ)", size=10, bold=True, color=INK))
    p.append(text(845, 271, "0x4000 – 0x7FFF", size=9.5, color=MUTED))
    p.append(text(845, 289, "Змінні, буфери, стек", size=9, color=MUTED))
    p.append(text(845, 305, "Читання/Запис (/RD, /WR)", size=9, color=RED))

    # CS від дешифратора до RAM
    p.append(line(665, 160, 665, 245, color=RED))
    p.append(arrow(665, 245, 770, 245, color=RED))
    p.append(text(710, 237, "/CS1", size=9, color=RED))

    # Блок 3: MMIO Периферія (GPIO / Регістри заліза)
    p.append(rect(770, 350, 150, 165, fill="#f0fdf4", stroke=GREEN, sw=1.8))
    p.append(text(845, 373, "MMIO ПЕРИФЕРІЯ", size=11, bold=True, color=GREEN))
    p.append(text(845, 391, "Регістри портів", size=10, bold=True, color=INK))
    p.append(text(845, 411, "0x8000: GPIO_OUT", size=9.5, bold=True, color=INK))
    p.append(text(845, 427, "0x8001: GPIO_IN", size=9.5, bold=True, color=INK))
    p.append(text(845, 443, "0x8002: TIMER_CNT", size=9.5, color=MUTED))
    p.append(rect(785, 458, 120, 45, fill="#ffffff", stroke=GREEN, sw=1))
    p.append(text(845, 474, "74HC574 D-защіпка", size=9.5, bold=True, color=GREEN))
    p.append(text(845, 492, "Виводи мікросхеми (PIN)", size=9, color=INK))

    # CS від дешифратора до MMIO
    p.append(line(650, 160, 650, 385, color=RED))
    p.append(arrow(650, 385, 770, 385, color=RED))
    p.append(text(710, 377, "/CS2 (0x8000)", size=9, color=RED))

    # З'єднання шин із блоками
    # Шина адреси -> RAM, MMIO
    p.append(arrow(492, 270, 770, 270, color=AMBER))
    p.append(arrow(492, 420, 770, 420, color=AMBER))

    # Шина даних <-> ROM, RAM, MMIO
    p.append(arrow(770, 140, 532, 140, color=BLUE)) # ROM -> Data Bus
    p.append(line(532, 290, 770, 290, color=BLUE))  # RAM <-> Data Bus
    p.append(arrow(532, 290, 532, 290, color=BLUE))
    p.append(arrow(770, 290, 770, 290, color=BLUE))
    p.append(line(532, 440, 770, 440, color=BLUE))  # MMIO <-> Data Bus
    p.append(arrow(532, 440, 532, 440, color=BLUE))
    p.append(arrow(770, 440, 770, 440, color=BLUE))

    # Виходи пінів назовні
    p.append(arrow(905, 480, 935, 480, color=GREEN, sw=2))
    p.append(text(920, 470, "LED", size=9.5, bold=True, color=GREEN))

    return render(os.path.join(OUT, "cpu-synthesis-blocks.svg"), W, H, *p)


# ── 2. Часова діаграма та рух сигналів у циклі Fetch-Decode-Execute ───────────
def fig_fde_timing():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 26, "Покроковий рух сигналів у циклі вибірки та виконання (Fetch-Decode-Execute)", size=15, bold=True))

    # Стовпчики фаз: Fetch (T1), Decode (T2), Execute (T3), Writeback (T4)
    # Замість суцільних кольорових плашок на всю висоту, малюємо рамки заголовків і роздільні лінії
    cols = [
        (130, 290, "ФАЗА ВИБІРКИ (FETCH / T1)", "#fffbeb", AMBER),
        (310, 480, "ДЕКОДУВАННЯ (DECODE / T2)", "#fef2f2", RED),
        (500, 680, "ВИКОНАННЯ (EXECUTE / T3)", "#f0fdf4", GREEN),
        (700, 860, "ЗАПИС (WRITEBACK / T4)", "#eff6ff", BLUE),
    ]
    for x1, x2, label, bg_col, bord_col in cols:
        p.append(rect(x1, 52, x2 - x1, 28, fill=bg_col, stroke=bord_col, sw=1.4, rx=4))
        p.append(text((x1 + x2) / 2, 70, label, size=10, bold=True, color=bord_col))
        p.append(line(x1, 85, x1, 415, color=GRID, sw=1.2, dash="3,3"))
    p.append(line(860, 85, 860, 415, color=GRID, sw=1.2, dash="3,3"))

    # Рядки сигналів
    signals = [
        (110, "Тактовий сигнал CLK", INK),
        (150, "Шина адреси (A[15:0])", AMBER),
        (190, "Строб читання (/RD)", RED),
        (230, "Шина даних (D[7:0])", BLUE),
        (270, "Регістр команд (IR)", RED),
        (310, "Операція АЛП / MMIO", GREEN),
        (350, "Строб запису (/WR)", RED),
        (395, "Фізичний пін (GPIO OUT)", GREEN),
    ]

    for y, name, col in signals:
        p.append(text(120, y + 4, name, size=9.5, bold=True, color=col, anchor="end"))
        p.append(line(130, y, 860, y, color="#e5e7eb", sw=1, dash="2,2"))

    # Сигнал 1: CLK
    clk_path = ("M130 115 L170 115 L170 95 L215 95 L215 115 L260 115 L260 95 L305 95 L305 115 "
                "L350 115 L350 95 L395 95 L395 115 L440 115 L440 95 L490 95 L490 115 "
                "L535 115 L535 95 L580 95 L580 115 L625 115 L625 95 L675 95 L675 115 "
                "L720 115 L720 95 L765 95 L765 115 L810 115 L810 95 L855 95 L855 115")
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (clk_path, INK))

    # Сигнал 2: Address Bus (A[15:0])
    p.append(rect(140, 140, 140, 20, fill="#fef3c7", stroke=AMBER, sw=1.4, rx=3))
    p.append(text(210, 154, "PC = 0x0024", size=9.5, bold=True, color=AMBER))
    p.append(line(280, 150, 520, 150, color=GREY, sw=1.2))
    p.append(rect(520, 140, 330, 20, fill="#fef3c7", stroke=AMBER, sw=1.4, rx=3))
    p.append(text(685, 154, "Цільова адреса MMIO = 0x8000", size=9.5, bold=True, color=AMBER))

    # Сигнал 3: /RD
    p.append(line(130, 185, 160, 185, color=RED, sw=1.8))
    p.append(line(160, 185, 160, 200, color=RED, sw=1.8))
    p.append(line(160, 200, 270, 200, color=RED, sw=1.8))
    p.append(line(270, 200, 270, 185, color=RED, sw=1.8))
    p.append(line(270, 185, 860, 185, color=RED, sw=1.8))
    p.append(text(215, 197, "/RD = 0 (активне)", size=9, bold=True, color=RED))

    # Сигнал 4: Data Bus
    p.append(line(130, 230, 180, 230, color=GREY, sw=1.2))
    p.append(rect(180, 220, 100, 20, fill="#dbeafe", stroke=BLUE, sw=1.4, rx=3))
    p.append(text(230, 234, "Opcode: 0x30", size=9.5, bold=True, color=BLUE))
    p.append(line(280, 230, 530, 230, color=GREY, sw=1.2))
    p.append(rect(530, 220, 320, 20, fill="#dbeafe", stroke=BLUE, sw=1.4, rx=3))
    p.append(text(690, 234, "Дані на запис: ACC = 0x01", size=9.5, bold=True, color=BLUE))

    # Сигнал 5: IR
    p.append(line(130, 270, 260, 270, color=GREY, sw=1.2))
    p.append(rect(260, 260, 590, 20, fill="#fee2e2", stroke=RED, sw=1.4, rx=3))
    p.append(text(555, 274, "STORE_MMIO [0x8000], ACC (зафіксовано на фронті CLK)", size=9.5, bold=True, color=RED))

    # Сигнал 6: ALU / Control
    p.append(line(130, 310, 330, 310, color=GREY, sw=1.2))
    p.append(rect(330, 300, 150, 20, fill="#fef2f2", stroke=RED, sw=1.4, rx=3))
    p.append(text(405, 314, "Дешифрація команди", size=9.5, color=RED))
    p.append(rect(510, 300, 165, 20, fill="#f0fdf4", stroke=GREEN, sw=1.4, rx=3))
    p.append(text(592, 314, "Вибірка операнда ACC", size=9.5, color=GREEN))
    p.append(line(675, 310, 860, 310, color=GREY, sw=1.2))

    # Сигнал 7: /WR
    p.append(line(130, 345, 715, 345, color=RED, sw=1.8))
    p.append(line(715, 345, 715, 360, color=RED, sw=1.8))
    p.append(line(715, 360, 810, 360, color=RED, sw=1.8))
    p.append(line(810, 360, 810, 345, color=RED, sw=1.8))
    p.append(line(810, 345, 860, 345, color=RED, sw=1.8))
    p.append(text(762, 357, "/WR = 0", size=9, bold=True, color=RED))

    # Сигнал 8: GPIO PIN
    p.append(line(130, 400, 810, 400, color=GREEN, sw=1.8))
    p.append(line(810, 400, 810, 380, color=GREEN, sw=2.2))
    p.append(line(810, 380, 860, 380, color=GREEN, sw=2.2))
    p.append(text(470, 395, "0 В (LOW)", size=9.5, color=MUTED))
    p.append(text(835, 375, "3.3 В (HIGH)", size=9.5, bold=True, color=GREEN))

    return render(os.path.join(OUT, "fetch-decode-execute-timing.svg"), W, H, *p)


# ── 3. Карта пам'яті та механіка MMIO ─────────────────────────────────────────
def fig_memory_map_mmio():
    W, H = 880, 480
    p = []
    p.append(text(W / 2, 26, "Організація пам'яті (Memory Map) та відображення вводу-виводу (MMIO)", size=15, bold=True))

    # Стовпчик Memory Map (зліва)
    p.append(rect(80, 60, 240, 390, fill="#f8fafc", stroke=INK, sw=1.8, rx=6))
    p.append(text(200, 80, "КАРТА ПАМ'ЯТІ (64 КБ)", size=12, bold=True, color=INK))

    # Секція 1: ROM / Flash (0x0000 - 0x3FFF)
    p.append(rect(95, 95, 210, 95, fill="#fffbeb", stroke=AMBER, sw=1.4))
    p.append(text(200, 120, "ROM / FLASH (16 КБ)", size=10.5, bold=True, color=AMBER))
    p.append(text(200, 138, "0x0000 – 0x3FFF", size=9.5, color=INK))
    p.append(text(200, 155, "Вектор скидання (0x0000)", size=9, color=MUTED))
    p.append(text(200, 170, "Таблиця переривань, код", size=9, color=MUTED))

    # Секція 2: SRAM (0x4000 - 0x7FFF)
    p.append(rect(95, 200, 210, 95, fill="#eff6ff", stroke=BLUE, sw=1.4))
    p.append(text(200, 225, "SRAM (16 КБ)", size=10.5, bold=True, color=BLUE))
    p.append(text(200, 243, "0x4000 – 0x7FFF", size=9.5, color=INK))
    p.append(text(200, 260, "Глобальні змінні, купа", size=9, color=MUTED))
    p.append(text(200, 275, "Стек викликів (росте вниз)", size=9, color=MUTED))

    # Секція 3: MMIO Регістри (0x8000 - 0x80FF)
    p.append(rect(95, 305, 210, 75, fill="#f0fdf4", stroke=GREEN, sw=1.8))
    p.append(text(200, 325, "MMIO ПЕРИФЕРІЯ", size=10.5, bold=True, color=GREEN))
    p.append(text(200, 343, "0x8000 – 0x80FF", size=9.5, bold=True, color=INK))
    p.append(text(200, 360, "Регістри апаратних блоків", size=9, color=GREEN))

    # Секція 4: Вільний простір (0x8100 - 0xFFFF)
    p.append(rect(95, 390, 210, 50, fill="#f3f4f6", stroke=GREY, sw=1))
    p.append(text(200, 412, "НЕРОЗПОДІЛЕНО (31.75 КБ)", size=9.5, color=MUTED))
    p.append(text(200, 428, "0x8100 – 0xFFFF", size=9, color=MUTED))

    # Збільшений блок MMIO (праворуч)
    p.append(rect(390, 60, 450, 390, fill="#f0fdf4", stroke=GREEN, sw=1.8, rx=6))
    p.append(text(615, 85, "АПАРАТНИЙ ВМІСТ MMIO (АДРЕСА 0x8000)", size=12, bold=True, color=GREEN))

    # Стрілка збільшення від карти пам'яті до деталей
    p.append(arrow(305, 342, 390, 160, color=GREEN, sw=1.5))

    # Схема підключення регістра 0x8000
    p.append(rect(410, 105, 210, 160, fill="#ffffff", stroke=GREEN, sw=1.5))
    p.append(text(515, 127, "0x8000: GPIO_DATA_OUT", size=10.5, bold=True, color=INK))
    p.append(text(515, 145, "8-бітний D-регістр 74HC574", size=9.5, color=MUTED))

    # Розряди регістра [7..0]
    for i in range(8):
        bx = 422 + i * 23
        p.append(rect(bx, 160, 21, 35, fill="#dbeafe" if i == 7 else "#f3f4f6", stroke=INK, sw=1))
        p.append(text(bx + 10.5, 175, "b%d" % (7 - i), size=9, color=MUTED))
        p.append(text(bx + 10.5, 190, "1" if i == 7 else "0", size=10, bold=True, color=BLUE if i == 7 else INK))

    p.append(text(515, 215, "Біт 0 керує піном LED", size=9.5, bold=True, color=BLUE))
    p.append(clk_tri(410, 245))
    p.append(text(440, 248, "CLK (LE)", size=9, color=INK))

    # Входи стробування
    p.append(rect(410, 290, 210, 80, fill="#fef2f2", stroke=RED, sw=1.4))
    p.append(text(515, 310, "Логіка запису в регістр", size=10, bold=True, color=RED))
    p.append(text(515, 330, "CLK_LE = (Addr == 0x8000) AND /WR", size=9.5, bold=True, color=INK))
    p.append(text(515, 350, "Спрацьовує за інструкцією STORE", size=9, color=MUTED))

    p.append(arrow(515, 290, 515, 265, color=RED, sw=1.5))

    # Вихід на світлодіод
    p.append(arrow(620, 185, 680, 185, color=GREEN, sw=2))
    p.append(text(650, 175, "Пін 0", size=9.5, bold=True, color=GREEN))

    p.append(rect(680, 155, 140, 80, fill="#ffffff", stroke=GREEN, sw=1.5))
    p.append(text(750, 177, "Світлодіодний драйвер", size=9.5, bold=True, color=INK))
    p.append(text(750, 195, "Резистор 330 Ом + LED", size=9, color=MUTED))
    p.append(circle(750, 218, 9, fill="#fef08a", stroke=AMBER, sw=1.5))
    p.append(text(750, 222, "★", size=11, color=AMBER))

    # Інші регістри периферії
    p.append(rect(410, 385, 410, 50, fill="#ffffff", stroke=GREEN, sw=1.2))
    p.append(text(615, 403, "0x8001: GPIO_DATA_IN (Буфер 74HC244 зчитує кнопки)", size=9.5, color=INK))
    p.append(text(615, 421, "0x8002: TIMER_PRESCALER / 0x8003: UART_TX_BUF", size=9, color=MUTED))

    return render(os.path.join(OUT, "memory-map-mmio.svg"), W, H, *p)


# ── 4. Від дискретної плати до однокристального мікроконтролера ───────────────
def fig_discrete_to_mcu():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 26, "Еволюція: від дискретної шини на друкованій платі до інтегрованого мікроконтролера", size=15, bold=True))

    # Ліва половина: Дискретна мікропроцесорна система (PCB)
    p.append(rect(30, 55, 395, 345, fill="#f8fafc", stroke=POS, sw=1.8, rx=6))
    p.append(text(227, 80, "ДИСКРЕТНА СИСТЕМА (ПЛАТА 1970-80-х)", size=11.5, bold=True, color=POS))

    p.append(rect(50, 105, 100, 80, fill="#eff6ff", stroke=BLUE, sw=1.4))
    p.append(text(100, 137, "CPU Чіп", size=11, bold=True, color=BLUE))
    p.append(text(100, 155, "(Z80 / 6502)", size=9.5, color=MUTED))

    p.append(rect(180, 105, 100, 80, fill="#fffbeb", stroke=AMBER, sw=1.4))
    p.append(text(230, 137, "ROM Чіп", size=11, bold=True, color=AMBER))
    p.append(text(230, 155, "ПЗП 27C64", size=9.5, color=MUTED))

    p.append(rect(310, 105, 95, 80, fill="#eff6ff", stroke=BLUE, sw=1.4))
    p.append(text(357, 137, "RAM Чіп", size=11, bold=True, color=BLUE))
    p.append(text(357, 155, "ОЗП 62256", size=9.5, color=MUTED))

    p.append(rect(110, 230, 110, 70, fill="#f3f4f6", stroke=INK, sw=1.4))
    p.append(text(165, 257, "Дешифратор", size=10, bold=True, color=INK))
    p.append(text(165, 275, "74HC138", size=9.5, color=MUTED))

    p.append(rect(250, 230, 120, 70, fill="#f0fdf4", stroke=GREEN, sw=1.4))
    p.append(text(310, 257, "GPIO Порт", size=10, bold=True, color=GREEN))
    p.append(text(310, 275, "74HC574 Latch", size=9.5, color=MUTED))

    # Шини на платі
    p.append(line(50, 205, 395, 205, color=AMBER, sw=3))
    p.append(text(227, 200, "Паралельні доріжки друкованої плати (16+8+4 = 28 провідників)", size=9, bold=True, color=AMBER))

    # Проблеми дискретної плати
    p.append(rect(45, 315, 365, 70, fill="#fef2f2", stroke=POS, sw=1))
    p.append(text(227, 332, "Недоліки дискретної архітектури:", size=9.5, bold=True, color=POS))
    p.append(text(227, 348, "• Паразитна ємність доріжок (15–30 пФ на лінію) -> межа 10–20 МГц", size=9, color=INK))
    p.append(text(227, 363, "• Десятки виводів корпусів, висока вартість і габарити плати", size=9, color=INK))
    p.append(text(227, 377, "• Високе енергоспоживання через перезарядку ємностей шин", size=9, color=INK))

    # Права половина: Монолітний мікроконтролер (MCU)
    p.append(rect(455, 55, 395, 345, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(652, 80, "ОДНОКРИСТАЛЬНИЙ МК (STM32, ESP32, AVR)", size=11.5, bold=True, color=FIELD))

    # Кремнієвий кристал (Silicon Die)
    p.append(rect(480, 105, 345, 195, fill="#ffffff", stroke=FIELD, sw=2, rx=4))
    p.append(text(652, 125, "ЄДИНИЙ КРЕМНІЄВИЙ КРИСТАЛ (SILICON DIE)", size=10, bold=True, color=FIELD))

    # Блоки всередині кристала
    p.append(rect(495, 140, 95, 55, fill="#eff6ff", stroke=BLUE, sw=1.2))
    p.append(text(542, 163, "CPU Core", size=9.5, bold=True, color=BLUE))
    p.append(text(542, 178, "Cortex-M / RISC-V", size=9, color=MUTED))

    p.append(rect(605, 140, 100, 55, fill="#fffbeb", stroke=AMBER, sw=1.2))
    p.append(text(655, 163, "Flash Memory", size=9.5, bold=True, color=AMBER))
    p.append(text(655, 178, "64–512 КБ", size=9, color=MUTED))

    p.append(rect(720, 140, 90, 55, fill="#eff6ff", stroke=BLUE, sw=1.2))
    p.append(text(765, 163, "SRAM", size=9.5, bold=True, color=BLUE))
    p.append(text(765, 178, "16–128 КБ", size=9, color=MUTED))

    # Внутрішня матриця шин
    p.append(rect(495, 205, 315, 22, fill="#fef3c7", stroke=AMBER, sw=1.2, rx=2))
    p.append(text(652, 220, "Внутрішня матриця шин (AHB / APB Bus Matrix)", size=9, bold=True, color=AMBER))

    # Периферійні блоки
    p.append(rect(495, 235, 70, 50, fill="#f0fdf4", stroke=GREEN, sw=1))
    p.append(text(530, 255, "GPIO", size=9, bold=True, color=GREEN))
    p.append(text(530, 270, "Порти A, B", size=9, color=MUTED))

    p.append(rect(575, 235, 70, 50, fill="#f0fdf4", stroke=GREEN, sw=1))
    p.append(text(610, 255, "Timers", size=9, bold=True, color=GREEN))
    p.append(text(610, 270, "ШІМ, Capture", size=9, color=MUTED))

    p.append(rect(655, 235, 75, 50, fill="#f0fdf4", stroke=GREEN, sw=1))
    p.append(text(692, 255, "UART/SPI", size=9, bold=True, color=GREEN))
    p.append(text(692, 270, "I2C, CAN", size=9, color=MUTED))

    p.append(rect(740, 235, 70, 50, fill="#f0fdf4", stroke=GREEN, sw=1))
    p.append(text(775, 255, "ADC/DAC", size=9, bold=True, color=GREEN))
    p.append(text(775, 270, "12 біт", size=9, color=MUTED))

    # Переваги МК
    p.append(rect(470, 315, 365, 70, fill="#f0fdf4", stroke=FIELD, sw=1))
    p.append(text(652, 332, "Переваги інтегрованого кристала:", size=9.5, bold=True, color=FIELD))
    p.append(text(652, 348, "• Ємність внутрішніх з'єднань < 10–50 фФ (у 1000 разів менше)", size=9, color=INK))
    p.append(text(652, 363, "• Тактові частоти 48–480 МГц при мізерному струмі споживання", size=9, color=INK))
    p.append(text(652, 377, "• Компактний корпус (QFN/BGA), мінімум зовнішніх провідників", size=9, color=INK))

    return render(os.path.join(OUT, "discrete-to-mcu-integration.svg"), W, H, *p)


if __name__ == "__main__":
    fig_cpu_synthesis()
    fig_fde_timing()
    fig_memory_map_mmio()
    fig_discrete_to_mcu()
    print("All figures generated successfully.")
