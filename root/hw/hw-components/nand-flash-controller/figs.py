# -*- coding: utf-8 -*-
"""Генератор векторних фігур для теми nand-flash-controller (Контролер NAND-флеші).
Використовує спільну бібліотеку svgkit з scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_controller_architecture():
    """Фігура 1: Апаратна структура SoC-контролера NAND-флеші."""
    w, h = 920, 560
    frags = []

    # Загальний контур чипа контролера
    frags.append(rect(20, 20, 880, 520, fill="#ffffff", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(460, 48, "Апаратна архітектура SoC-контролера твердотільного накопичувача (SSD / UFS)", size=16, color=INK, bold=True))

    # Ліва колонка: Інтерфейс хоста
    frags.append(rect(40, 80, 200, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(140, 106, "Інтерфейс хоста (Host)", size=14, color=NEG, bold=True))

    b_pcie, _, _ = textbox(140, 155, "Шина хоста\nPCIe 4.0/5.0 / UFS 4.0\nPHY + MAC", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_pcie)

    b_nvme, _, _ = textbox(140, 240, "NVMe / UFS контролер\nЧерги SQ / CQ / Doorbell\nАпаратний арбітраж", size=12, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(b_nvme)

    b_hdma, _, _ = textbox(140, 325, "Host DMA Engine\nПрямий доступ до RAM\nScatter-Gather списки", size=12, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(b_hdma)

    b_plp, _, _ = textbox(140, 430, "Захист PLP (Power Loss)\nСуперконденсатори\nДетектор збою напруги", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_plp)

    # Центральна магістраль: Системна шина
    frags.append(rect(260, 80, 60, 430, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(290, 290, "Внутрішня шина AXI / NoC Bus Matrix", size=12, color="#334155", bold=True, anchor="middle"))

    # Центральна колонка (вгорі - CPU, внизу - RAM)
    frags.append(rect(340, 80, 250, 205, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(465, 106, "Процесорний комплекс", size=14, color=FIELD, bold=True))

    b_cpu, _, _ = textbox(465, 155, "Багатоядерний CPU\n32/64-bit ARM Cortex-R / RISC-V\nКерування потоками FTL", size=12, pad=6, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(b_cpu)

    b_tcm, _, _ = textbox(465, 235, "Локальна пам'ять ядра\nSRAM TCM + I/D Cache\nШвидкий стек і дескриптори", size=12, pad=6, fill="#eafaf1", stroke=FIELD)
    frags.append(b_tcm)

    frags.append(rect(340, 305, 250, 205, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(465, 330, "Підсистема буферів і FTL", size=14, color="#7c3aed", bold=True))

    b_dram_ctrl, _, _ = textbox(465, 380, "Контролер LPDDR4/DDR5\nКеш таблиць L2P (FTL)\nБуферизація запису даних", size=12, pad=6, fill="#f5f3ff", stroke="#7c3aed", bold=True)
    frags.append(b_dram_ctrl)

    b_sram_buf, _, _ = textbox(465, 460, "Внутрішній SRAM буфер\nЖурнал транзакцій FTL\nПроміжні черги DMA", size=12, pad=6, fill="#f5f3ff", stroke="#7c3aed")
    frags.append(b_sram_buf)

    # Права колонка: Flash Processing & Interface
    frags.append(rect(610, 80, 270, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(745, 106, "Флеш-інтерфейс (FMI & ECC)", size=14, color=POS, bold=True))

    b_ecc, _, _ = textbox(745, 160, "Апаратний рушій ECC / LDPC\nHard / Soft-Decision декодер\nОбчислення синдромів і LLR", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_ecc)

    b_sec, _, _ = textbox(745, 245, "Криптографія та рандомізація\nAES-256 XTS шифрування\nСкремблер для балансу заряду", size=12, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(b_sec)

    b_fmi, _, _ = textbox(745, 335, "Flash Memory Controller (FMC)\n8-16 паралельних каналів\nONFI 5.1 / Toggle DDR5", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_fmi)

    b_chips, _, _ = textbox(745, 440, "Масив 3D NAND Flash Chips\nКристали (Dies) та площини (Planes)\nБагатоканальне переплетення", size=12, pad=6, fill="#ffffff", stroke="#0f172a", bold=True)
    frags.append(b_chips)

    # З'єднувальні шини та стрілки
    frags.append(line(240, 155, 260, 155, color=NEG, sw=2))
    frags.append(line(240, 240, 260, 240, color=NEG, sw=2))
    frags.append(line(240, 325, 260, 325, color=NEG, sw=2))

    frags.append(line(320, 155, 340, 155, color=FIELD, sw=2))
    frags.append(line(320, 380, 340, 380, color="#7c3aed", sw=2))

    frags.append(line(590, 160, 610, 160, color=POS, sw=2))
    frags.append(line(590, 380, 610, 335, color="#7c3aed", sw=2))

    frags.append(line(745, 195, 745, 215, color=POS, sw=1.5))
    frags.append(line(745, 275, 745, 305, color=POS, sw=1.5))
    frags.append(line(745, 370, 745, 405, color=POS, sw=2))

    render(os.path.join(IMG_DIR, "controller-architecture.svg"), w, h, *frags)


def fig_ftl_mapping_gc():
    """Фігура 2: Посторінкове відображення FTL, Out-of-Place запис та збір сміття (GC)."""
    w, h = 920, 540
    frags = []

    frags.append(rect(15, 15, 890, 510, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 42, "Посторінкове відображення FTL, Out-of-Place запис та збирання сміття (GC)", size=16, color=INK, bold=True))

    # Секція 1: Хост і Таблиця FTL (L2P)
    frags.append(rect(30, 70, 270, 435, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(165, 96, "1. Хост і таблиця FTL (DRAM)", size=13, color=NEG, bold=True))

    b_host_req, _, _ = textbox(165, 140, "Запит на запис хоста:\nWrite(LBA=2, Data=D2_new)", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_host_req)

    # Таблиця відображення
    frags.append(rect(45, 190, 240, 190, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(165, 210, "Таблиця L2P (Logical to Physical)", size=11, color=INK, bold=True))
    frags.append(line(45, 222, 285, 222, color="#cbd5e1", sw=1))

    # Рядки таблиці
    frags.append(text(85, 240, "LBA 0  →  Блок 1, Стор 0", size=11, color=INK))
    frags.append(text(85, 265, "LBA 1  →  Блок 1, Стор 1", size=11, color=INK))
    frags.append(text(85, 290, "LBA 2  →  Блок 2, Стор 0", size=11, color=FIELD, bold=True))
    frags.append(text(85, 312, "(старе: Блок 1, Стор 2)", size=10, color=MUTED, italic=True))
    frags.append(text(85, 335, "LBA 3  →  Блок 1, Стор 3", size=11, color=INK))
    frags.append(text(85, 360, "LBA 4  →  Блок 2, Стор 1", size=11, color=INK))

    b_out_place, _, _ = textbox(165, 440, "Out-of-Place запис:\nСтара сторінка стає INVALID\nНова сторінка стає VALID", size=11, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(b_out_place)

    # Секція 2: Фізичні блоки до збору сміття
    frags.append(rect(320, 70, 270, 435, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(455, 96, "2. Фізичні блоки до GC", size=13, color="#d97706", bold=True))

    # Блок 1 (Жертва GC)
    frags.append(rect(335, 125, 240, 210, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(455, 145, "Блок-жертва (Victim Block 1)", size=12, color=POS, bold=True))
    frags.append(rect(345, 160, 220, 30, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 180, "Стор 0: LBA 0 (D0) [VALID]", size=11, color=FIELD, bold=True))

    frags.append(rect(345, 195, 220, 30, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 215, "Стор 1: LBA 1 (D1) [VALID]", size=11, color=FIELD, bold=True))

    frags.append(rect(345, 230, 220, 30, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(455, 250, "Стор 2: LBA 2 (D2_old) [INVALID]", size=11, color=POS, bold=True))

    frags.append(rect(345, 265, 220, 30, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 285, "Стор 3: LBA 3 (D3) [VALID]", size=11, color=FIELD, bold=True))

    frags.append(text(455, 320, "Сміття (Invalid): 25% простору", size=11, color=POS))

    # Блок 2 (Цільовий для нових записів)
    frags.append(rect(335, 350, 240, 140, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(455, 370, "Активний Блок 2 (Active Block)", size=12, color=FIELD, bold=True))
    frags.append(rect(345, 385, 220, 26, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 402, "Стор 0: LBA 2 (D2_new) [VALID]", size=10, color=FIELD))
    frags.append(rect(345, 415, 220, 26, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 432, "Стор 1: LBA 4 (D4) [VALID]", size=10, color=FIELD))
    frags.append(rect(345, 445, 220, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(455, 467, "Стор 2..N: [Вільні / Free]", size=11, color=MUTED))

    # Секція 3: Результат Garbage Collection
    frags.append(rect(610, 70, 280, 435, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(750, 96, "3. Збір сміття (GC) та стирання", size=13, color=FIELD, bold=True))

    b_gc_step, _, _ = textbox(750, 145, "Крок GC:\nКопіювання дійсних сторінок\n(D0, D1, D3) у новий Блок 3", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    frags.append(b_gc_step)

    # Блок 3 (Куди скопіювали)
    frags.append(rect(625, 205, 250, 140, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(750, 225, "Новий Блок 3 (Ущільнені дані)", size=12, color=FIELD, bold=True))
    frags.append(rect(635, 238, 230, 22, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    frags.append(text(750, 253, "Стор 0: LBA 0 (D0) [VALID]", size=10, color=FIELD))
    frags.append(rect(635, 263, 230, 22, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    frags.append(text(750, 278, "Стор 1: LBA 1 (D1) [VALID]", size=10, color=FIELD))
    frags.append(rect(635, 288, 230, 22, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    frags.append(text(750, 303, "Стор 2: LBA 3 (D3) [VALID]", size=10, color=FIELD))
    frags.append(rect(635, 313, 230, 22, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    frags.append(text(750, 328, "Стор 3..N: [Вільні для запису]", size=10, color=MUTED))

    # Блок 1 після стирання
    frags.append(rect(625, 365, 250, 125, fill="#ffffff", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(750, 385, "Блок 1 (Після Block Erase)", size=12, color=INK, bold=True))
    frags.append(rect(635, 400, 230, 45, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(750, 420, "Усі сторінки стерто (стан 0xFF)", size=11, color=INK))
    frags.append(text(750, 436, "Повернено в пул вільних блоків", size=10, color=FIELD, bold=True))
    frags.append(text(750, 465, "Лічильник P/E циклів збільшено на 1", size=11, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "ftl-mapping-gc.svg"), w, h, *frags)


def fig_wear_leveling():
    """Фігура 3: Динамічне та статичне вирівнювання зносу (Dynamic vs Static Wear Leveling)."""
    w, h = 900, 520
    frags = []

    frags.append(rect(15, 15, 870, 490, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(450, 45, "Механізми вирівнювання зносу: динамічний (Dynamic) та статичний (Static)", size=16, color=INK, bold=True))

    # Ліва половина: Динамічне вирівнювання зносу
    frags.append(rect(35, 75, 400, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(235, 105, "Динамічне вирівнювання (Dynamic WL)", size=14, color=NEG, bold=True))

    b_dyn_desc, _, _ = textbox(235, 155, "Застосовується до гарячих даних (Hot Data)\nщо постійно змінюються хостом.\nЦіль: обрати найменш зношений вільний блок.", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(b_dyn_desc)

    # Порівняння блоків для динамічного WL
    frags.append(rect(55, 215, 360, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(235, 235, "Пул вільних блоків (Free Blocks Pool)", size=12, color=INK, bold=True))

    frags.append(rect(70, 250, 150, 60, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(145, 272, "Вільний Блок A", size=11, color=FIELD, bold=True))
    frags.append(text(145, 292, "Знос: 120 P/E", size=12, color=FIELD, bold=True))

    frags.append(rect(245, 250, 150, 60, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(320, 272, "Вільний Блок B", size=11, color=POS, bold=True))
    frags.append(text(320, 292, "Знос: 2850 P/E", size=12, color=POS, bold=True))

    b_dyn_res, _, _ = textbox(235, 390, "Рішення FTL:\nСпрямувати нові гарячі записи в Блок A (120 P/E).\nБлок B тимчасово захищено від навантаження.\nСлабкість: не чіпає блоки з холодними даними!", size=11, pad=8, fill="#fef3c7", stroke="#d97706")
    frags.append(b_dyn_res)

    # Права половина: Статичне вирівнювання зносу
    frags.append(rect(465, 75, 400, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(665, 105, "Статичне вирівнювання (Static WL)", size=14, color=FIELD, bold=True))

    b_stat_desc, _, _ = textbox(665, 155, "Застосовується до холодних даних (Cold Data)\n(файли ОС, які лише читаються й не перезаписуються).\nЦіль: визволити законсервований блок із низьким зносом.", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    frags.append(b_stat_desc)

    # Процес ротації
    frags.append(rect(485, 215, 360, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(665, 235, "Перерозподіл холодних і гарячих зон", size=12, color=INK, bold=True))

    frags.append(rect(500, 250, 150, 60, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(575, 270, "Блок C (Холодний)", size=11, color=FIELD, bold=True))
    frags.append(text(575, 290, "Знос: 15 P/E (ОС)", size=11, color=FIELD))

    frags.append(rect(675, 250, 150, 60, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(750, 270, "Блок D (Зношений)", size=11, color=POS, bold=True))
    frags.append(text(750, 290, "Знос: 2900 P/E", size=11, color=POS))

    b_stat_res, _, _ = textbox(665, 390, "Рокіровка FTL (Static Trigger):\n1. Холодні дані переносяться з Блоку C в Блок D.\n2. Блок C стирається й віддається під гарячі записи.\nРезультат: увесь масив NAND зношується рівномірно.", size=11, pad=8, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(b_stat_res)

    render(os.path.join(IMG_DIR, "wear-leveling-schemes.svg"), w, h, *frags)


def fig_ldpc_soft_decoding():
    """Фігура 4: Тверде (Hard) та м'яке (Soft) декодування LDPC з оцінкою LLR."""
    w, h = 920, 540
    frags = []

    frags.append(rect(15, 15, 890, 510, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 42, "Декодування LDPC: тверде (Hard-Decision) проти м'якого (Soft-Decision)", size=16, color=INK, bold=True))

    # Верхня половина: Тверде декодування
    frags.append(rect(35, 65, 850, 205, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(180, 90, "Тверде декодування (Hard-Decision)", size=13, color=NEG, bold=True))
    frags.append(text(650, 90, "Одне читання напруги V_ref0 → Фіксований біт {0 або 1}", size=12, color=MUTED))

    # Осі та криві напруги Vt
    frags.append(line(70, 210, 830, 210, color="#64748b", sw=1.5))
    frags.append(text(840, 214, "V_t", size=12, color=INK, bold=True))

    # Неперетинні блоки станів L1 і L2
    b_l1, _, _ = textbox(210, 155, "Стан L1 (Логічна 1)\nРозподіл напруги Vt", size=12, pad=8, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_l1)

    b_l2, _, _ = textbox(650, 155, "Стан L2 (Логічний 0)\nРозподіл напруги Vt", size=12, pad=8, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_l2)

    # Зона перекриття між ними
    b_overlap, _, _ = textbox(430, 140, "Зона перекриття\n(Помилки читання)", size=11, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_overlap)

    # Опорна лінія Vref0
    frags.append(line(430, 175, 430, 210, color="#1e293b", sw=2, dash="4,4"))
    frags.append(text(430, 230, "Опорна напруга V_ref0 (Hard threshold)", size=11, color=INK, bold=True))

    # Нижня половина: М'яке декодування
    frags.append(rect(35, 285, 850, 220, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(180, 310, "М'яке декодування (Soft-Decision)", size=13, color=FIELD, bold=True))
    frags.append(text(650, 310, "Багатоточкове сканування V_ref(-2..+2) → Обчислення LLR (впевненості)", size=12, color=FIELD, bold=True))

    frags.append(line(70, 440, 830, 440, color="#64748b", sw=1.5))
    frags.append(text(840, 444, "V_t", size=12, color=INK, bold=True))

    # 5 точок заміру напруги
    v_shifts = [
        (330, "V_ref-2", "+3 (Впевнено 1)", "#2457d6"),
        (380, "V_ref-1", "+1 (Слабко 1)", "#3b82f6"),
        (430, "V_ref0", "0 (Невпевнено)", "#64748b"),
        (480, "V_ref+1", "-1 (Слабко 0)", "#ef4444"),
        (530, "V_ref+2", "-3 (Впевнено 0)", "#c0392b"),
    ]

    for vx, vname, llr_label, col in v_shifts:
        frags.append(line(vx, 335, vx, 450, color=col, sw=1.8, dash="3,3"))
        frags.append(text(vx, 330, vname, size=10, color=col, bold=True))
        frags.append(text(vx, 460, llr_label, size=9, color=col, bold=True))

    b_llr_info, _, _ = textbox(700, 385, "Ітеративний алгоритм\nBelief Propagation (Min-Sum):\nВикористовує вагу LLR для\nвиправлення лавинних помилок\nнавіть при сильному шумі", size=11, pad=6, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(b_llr_info)

    b_llr_formula, _, _ = textbox(170, 385, "Значення LLR:\nLLR = ln( P(b=0|y) / P(b=1|y) )\nЗнак = біт (0 чи 1)\nМодуль = ступінь впевненості", size=11, pad=6, fill="#ffffff", stroke="#64748b")
    frags.append(b_llr_formula)

    render(os.path.join(IMG_DIR, "ldpc-soft-decoding.svg"), w, h, *frags)


def main():
    fig_controller_architecture()
    fig_ftl_mapping_gc()
    fig_wear_leveling()
    fig_ldpc_soft_decoding()
    print("Всі 4 фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
