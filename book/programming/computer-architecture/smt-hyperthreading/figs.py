# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори ниток та конвеєра
T0_FILL = '#eaf0fd'    # Світло-синій (Нитка 0)
T0_STROKE = '#2457d6'  # Синій контур
T1_FILL = '#fdecea'    # Світло-червоний (Нитка 1)
T1_STROKE = '#c0392b'  # Червоний контур
EMPTY_FILL = '#f8f9fa' # Порожній слот (бульбашка простою)
EMPTY_STROKE = '#d1d5db'
SHARED_FILL = '#eef7ee'
SHARED_STROKE = '#27ae60'


# ── Фігура 1: Порівняння конвеєрного простою (Single, CGMT, FGMT, SMT) ────────
def fig_smt_pipeline_waste():
    W, H = 840, 410
    frags = []

    frags.append(text(W / 2, 26, 'Утилізація слотів конвеєра за тактами (ширина = 4 мікрооперації)', size=15, bold=True))

    cols = 4
    rows = 6
    cw, ch = 25, 23
    pad_x = 3

    configs = [
        ('Однопотоковий суперскаляр', 40, 65, [
            [1, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 0, 0, 0],
        ], 'Вертикальний і горизонтальний простій'),

        ('Чергова багатонитковість (FGMT)', 300, 65, [
            [1, 1, 1, 0],
            [2, 2, 0, 0],
            [1, 1, 0, 0],
            [2, 2, 2, 0],
            [1, 1, 1, 1],
            [2, 0, 0, 0],
        ], 'Усуває вертикальний простій'),

        ('Одночасна багатонитковість (SMT)', 560, 65, [
            [1, 1, 1, 2],
            [1, 1, 2, 2],
            [2, 2, 2, 0],
            [2, 2, 1, 0],
            [1, 1, 1, 2],
            [1, 2, 2, 2],
        ], 'Усуває обидва види простою')
    ]

    for title, px, py, grid, subtitle in configs:
        frags.append(rect(px, py, 240, 260, fill=FILL, stroke=EMPTY_STROKE, sw=1, rx=6))
        frags.append(text(px + 120, py + 22, title, size=11, bold=True))
        frags.append(text(px + 120, py + 38, subtitle, size=10, color=MUTED, italic=True))

        for c in range(cols):
            frags.append(text(px + 60 + c * (cw + pad_x) + cw / 2, py + 56, 'С%d' % (c + 1), size=10, color=MUTED))

        for r in range(rows):
            frags.append(text(px + 30, py + 72 + r * (ch + 4) + ch / 2 + 3, 'Т%d' % (r + 1), size=10, color=INK, bold=True))
            for c in range(cols):
                val = grid[r][c]
                rx_pos = px + 60 + c * (cw + pad_x)
                ry_pos = py + 72 + r * (ch + 4)
                if val == 1:
                    frags.append(rect(rx_pos, ry_pos, cw, ch, fill=T0_FILL, stroke=T0_STROKE, sw=1.2, rx=3))
                    frags.append(text(rx_pos + cw / 2, ry_pos + ch / 2 + 3, 'Н0', size=10, color=T0_STROKE, bold=True))
                elif val == 2:
                    frags.append(rect(rx_pos, ry_pos, cw, ch, fill=T1_FILL, stroke=T1_STROKE, sw=1.2, rx=3))
                    frags.append(text(rx_pos + cw / 2, ry_pos + ch / 2 + 3, 'Н1', size=10, color=T1_STROKE, bold=True))
                else:
                    frags.append(rect(rx_pos, ry_pos, cw, ch, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
                    frags.append(text(rx_pos + cw / 2, ry_pos + ch / 2 + 3, '·', size=11, color=MUTED))

    ly = H - 40
    frags.append(rect(80, ly, 18, 18, fill=T0_FILL, stroke=T0_STROKE, sw=1.2, rx=3))
    frags.append(text(105, ly + 13, 'Команда Нитки 0 (Н0)', size=11, anchor='start'))

    frags.append(rect(310, ly, 18, 18, fill=T1_FILL, stroke=T1_STROKE, sw=1.2, rx=3))
    frags.append(text(335, ly + 13, 'Команда Нитки 1 (Н1)', size=11, anchor='start'))

    frags.append(rect(540, ly, 18, 18, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(565, ly + 13, 'Порожній слот (бульбашка простою)', size=11, anchor='start'))

    render(os.path.join(IMG, 'smt-pipeline-waste.svg'), W, H, *frags)


# ── Фігура 2: Розподіл ресурсів усередині фізичного SMT-ядра ──────────────────
def fig_smt_core_partitioning():
    W, H = 840, 520
    frags = []

    frags.append(text(W / 2, 24, 'Мікроархітектура SMT-ядра: дублювання, поділ та спільне використання', size=15, bold=True))

    # Блок 1: Дубльований стан
    frags.append(rect(40, 48, 760, 98, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(55, 68, '1. Дубльований архітектурний стан (окремий контекст для кожної нитки)', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(60, 80, 340, 52, fill=T0_FILL, stroke=T0_STROKE, sw=1.2, rx=4))
    frags.append(text(230, 98, 'Логічний процесор 0 (Нитка 0)', size=11, bold=True, color=T0_STROKE))
    frags.append(text(230, 116, 'RAX..R15 · RIP (PC0) · CR3 · APIC 0 · RAT 0 · RSB 0', size=9.5, color=INK))

    frags.append(rect(440, 80, 340, 52, fill=T1_FILL, stroke=T1_STROKE, sw=1.2, rx=4))
    frags.append(text(610, 98, 'Логічний процесор 1 (Нитка 1)', size=11, bold=True, color=T1_STROKE))
    frags.append(text(610, 116, 'RAX..R15 · RIP (PC1) · CR3 · APIC 1 · RAT 1 · RSB 1', size=9.5, color=INK))

    frags.append(arrow(230, 134, 230, 160, color=LINE, sw=1.2))
    frags.append(arrow(610, 134, 610, 160, color=LINE, sw=1.2))

    # Блок 2: Статично розділені буфери
    frags.append(rect(40, 160, 760, 84, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(55, 180, '2. Статично розділені буфери конвеєра (50% / 50% при двох активних нитках)', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(60, 192, 340, 42, fill='#ffffff', stroke=T0_STROKE, sw=1.2, rx=4))
    frags.append(text(230, 208, 'Черга вибірки та декодування 0 (Fetch Queue 0)', size=10.5, bold=True))
    frags.append(text(230, 224, 'Буфер перевпорядкування 0 (ROB 0) · Load/Store Queue 0', size=9.5, color=MUTED))

    frags.append(rect(440, 192, 340, 42, fill='#ffffff', stroke=T1_STROKE, sw=1.2, rx=4))
    frags.append(text(610, 208, 'Черга вибірки та декодування 1 (Fetch Queue 1)', size=10.5, bold=True))
    frags.append(text(610, 224, 'Буфер перевпорядкування 1 (ROB 1) · Load/Store Queue 1', size=9.5, color=MUTED))

    frags.append(arrow(230, 244, 350, 272, color=LINE, sw=1.2))
    frags.append(arrow(610, 244, 490, 272, color=LINE, sw=1.2))

    # Блок 3: Спільний позачерговий рушій
    frags.append(rect(40, 272, 760, 120, fill=SHARED_FILL, stroke=SHARED_STROKE, sw=1.5, rx=6))
    frags.append(text(55, 294, '3. Спільний позачерговий рушій (Out-of-Order Engine) та виконавчі блоки', size=12, bold=True, anchor='start', color=FIELD))

    frags.append(rect(55, 308, 220, 72, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(165, 328, 'Спільний планувальник', size=10.5, bold=True))
    frags.append(text(165, 346, 'Станції резервування (RS)', size=10, color=MUTED))
    frags.append(text(165, 362, 'Єдина черга на всі порти', size=9.5, color=MUTED))

    frags.append(rect(290, 308, 220, 72, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(400, 328, 'Регістровий файл PRF', size=10.5, bold=True))
    frags.append(text(400, 346, 'Спільний фізичний пул', size=10, color=MUTED))
    frags.append(text(400, 362, '180–280 фізичних регістрів', size=9.5, color=MUTED))

    frags.append(rect(525, 308, 260, 72, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(655, 328, 'Виконавчі порти ядра', size=10.5, bold=True))
    frags.append(text(655, 346, 'Порти 0, 1, 5, 6: ALU / FMA / SIMD', size=9.5, color=INK))
    frags.append(text(655, 362, 'Порти 2, 3, 7, 8: Load / Store AGU', size=9.5, color=INK))

    frags.append(arrow(420, 395, 420, 424, color=LINE, sw=1.2))

    # Блок 4: Спільна ієрархія кешу
    frags.append(rect(40, 424, 760, 76, fill='#fdfefe', stroke=LINE, sw=1.2, rx=6))
    frags.append(text(55, 444, '4. Спільна ієрархія кешів та трансляції адрес', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(55, 456, 215, 34, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(162, 477, 'Кеш інструкцій L1I (32–64 КБ)', size=10, bold=True))

    frags.append(rect(285, 456, 215, 34, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(392, 477, 'Кеш даних L1D (32–48 КБ)', size=10, bold=True))

    frags.append(rect(515, 456, 270, 34, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(650, 477, 'Спільний L2 Кеш та DTLB / ITLB', size=10, bold=True))

    render(os.path.join(IMG, 'smt-core-partitioning.svg'), W, H, *frags)


# ── Фігура 3: Атаки побічними каналами на SMT (PortSmash та L1TF) ─────────────
def fig_smt_sidechannel_attack():
    W, H = 840, 410
    frags = []

    frags.append(text(W / 2, 26, 'Атаки побічними каналами та конкуренція за спільні ресурси SMT', size=15, bold=True))

    # Ліва частина: PortSmash
    frags.append(rect(40, 55, 365, 330, fill=FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(222, 80, 'PortSmash: витік через порти виконання', size=12, bold=True, color=POS))
    frags.append(text(222, 98, 'Конкуренція за Порт 0 / Порт 1 в один такт', size=10, color=MUTED))

    frags.append(rect(55, 115, 155, 68, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=4))
    frags.append(text(132, 136, 'Жертва (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(132, 154, 'OpenSSL ECDSA', size=10, color=INK))
    frags.append(text(132, 170, 'Множення точок кривої', size=9.5, color=MUTED))

    frags.append(rect(235, 115, 155, 68, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=4))
    frags.append(text(312, 136, 'Шпигун (Нитка 1)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(312, 154, 'Безперервні інструкції', size=10, color=INK))
    frags.append(text(312, 170, 'Вимір затримки RDTSC', size=9.5, color=MUTED))

    frags.append(arrow(132, 185, 200, 218, color=LINE, sw=1))
    frags.append(arrow(312, 185, 244, 218, color=LINE, sw=1))

    frags.append(rect(95, 218, 255, 54, fill='#ffffff', stroke=POS, sw=1.5, rx=4))
    frags.append(text(222, 239, 'Спільний Порт 0 (ALU/Множення)', size=11, bold=True))
    frags.append(text(222, 257, 'Затримка шпигуна зростає при множенні', size=9.5, color=POS))

    frags.append(rect(55, 290, 335, 80, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(222, 312, 'Наслідок для безпеки:', size=10.5, bold=True))
    frags.append(text(222, 332, 'Шпигун реконструює біти закритого ключа', size=10, color=INK))
    frags.append(text(222, 350, 'за коливаннями затримок виконання операцій', size=9.5, color=MUTED))

    # Права частина: L1TF / Foreshadow
    frags.append(rect(435, 55, 365, 330, fill=FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(617, 80, 'L1TF / Foreshadow: витік через L1D', size=12, bold=True, color=POS))
    frags.append(text(617, 98, 'Спекулятивне читання кешу іншої нитки', size=10, color=MUTED))

    frags.append(rect(450, 115, 155, 68, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=4))
    frags.append(text(527, 136, 'Гіпервізор / SGX (Н0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(527, 154, 'Секретні дані', size=10, color=INK))
    frags.append(text(527, 170, 'Залишаються в L1D', size=9.5, color=MUTED))

    frags.append(rect(630, 115, 155, 68, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=4))
    frags.append(text(707, 136, 'Гість-атакувальник (Н1)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(707, 154, 'Недійсна адреса PTE', size=10, color=INK))
    frags.append(text(707, 170, 'Спекулятивне читання', size=9.5, color=MUTED))

    frags.append(arrow(527, 185, 595, 218, color=LINE, sw=1))
    frags.append(arrow(707, 185, 639, 218, color=LINE, sw=1))

    frags.append(rect(490, 218, 255, 54, fill='#ffffff', stroke=POS, sw=1.5, rx=4))
    frags.append(text(617, 239, 'Спільний кеш даних L1D', size=11, bold=True))
    frags.append(text(617, 257, 'Спекулятивне читання до збою адресації', size=9.5, color=POS))

    frags.append(rect(450, 290, 335, 80, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(617, 312, 'Наслідок для безпеки:', size=10.5, bold=True))
    frags.append(text(617, 332, 'Читання конфіденційної пам\'яті хоста чи VM', size=10, color=INK))
    frags.append(text(617, 350, 'через спільний фізичний кеш одного ядра', size=9.5, color=MUTED))

    render(os.path.join(IMG, 'smt-sidechannel-attack.svg'), W, H, *frags)


# ── Фігура 4: Планування в Linux та Core Scheduling ───────────────────────────
def fig_smt_linux_core_scheduling():
    W, H = 840, 410
    frags = []

    frags.append(text(W / 2, 24, 'Планування в Linux: топологія ядер та ізоляція Core Scheduling', size=15, bold=True))

    # Ліва колонка: Звичайне SMT-планування
    frags.append(rect(40, 50, 365, 330, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(222, 74, '1. Звичайне планування (SMT-aware)', size=12, bold=True))
    frags.append(text(222, 92, 'Пріоритет: спершу вільні фізичні ядра', size=10, color=MUTED))

    # Фізичне ядро 0
    frags.append(rect(55, 108, 335, 110, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    frags.append(text(222, 128, 'Фізичне ядро 0 (Core 0)', size=11, bold=True))
    frags.append(rect(65, 140, 150, 66, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(140, 162, 'CPU 0 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(140, 182, 'Процес A (зайнято)', size=9.5, color=INK))

    frags.append(rect(230, 140, 150, 66, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(305, 162, 'CPU 1 (Нитка 1)', size=10.5, bold=True, color=MUTED))
    frags.append(text(305, 182, 'Вільний (idle)', size=9.5, color=MUTED))

    # Фізичне ядро 1
    frags.append(rect(55, 235, 335, 110, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    frags.append(text(222, 255, 'Фізичне ядро 1 (Core 1)', size=11, bold=True))
    frags.append(rect(65, 267, 150, 66, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(140, 289, 'CPU 2 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(140, 309, 'Процес B (надіслано сюди)', size=9.5, color=FIELD, bold=True))

    frags.append(rect(230, 267, 150, 66, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(305, 289, 'CPU 3 (Нитка 1)', size=10.5, bold=True, color=MUTED))
    frags.append(text(305, 309, 'Вільний (idle)', size=9.5, color=MUTED))

    # Права колонка: Core Scheduling
    frags.append(rect(435, 50, 365, 330, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(617, 74, '2. Core Scheduling (PR_SCHED_CORE)', size=12, bold=True, color=FIELD))
    frags.append(text(617, 92, 'Ізоляція за доменами довіри (Cookie)', size=10, color=MUTED))

    # Фізичне ядро 0
    frags.append(rect(450, 108, 335, 110, fill='#ffffff', stroke=SHARED_STROKE, sw=1.2, rx=4))
    frags.append(text(617, 128, 'Фізичне ядро 0: Домен довіри Cookie = X', size=10.5, bold=True, color=FIELD))
    frags.append(rect(460, 140, 150, 66, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(535, 162, 'CPU 0 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(535, 182, 'VM 1 (Cookie X)', size=9.5, color=INK))

    frags.append(rect(625, 140, 150, 66, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(700, 162, 'CPU 1 (Нитка 1)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(700, 182, 'VM 1 (Cookie X)', size=9.5, color=FIELD, bold=True))

    # Фізичне ядро 1
    frags.append(rect(450, 235, 335, 110, fill='#ffffff', stroke=POS, sw=1.2, rx=4))
    frags.append(text(617, 255, 'Фізичне ядро 1: Конфлікт доменів довіри', size=10.5, bold=True, color=POS))
    frags.append(rect(460, 267, 150, 66, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=3))
    frags.append(text(535, 289, 'CPU 2 (Нитка 0)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(535, 309, 'VM 2 (Cookie Y)', size=9.5, color=INK))

    frags.append(rect(625, 267, 150, 66, fill='#fff5f5', stroke=POS, sw=1, rx=3))
    frags.append(text(700, 289, 'CPU 3 (Нитка 1)', size=10.5, bold=True, color=POS))
    frags.append(text(700, 309, 'Примусовий простій (idle)', size=9, color=POS, bold=True))

    render(os.path.join(IMG, 'smt-linux-core-scheduling.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_smt_pipeline_waste()
    fig_smt_core_partitioning()
    fig_smt_sidechannel_attack()
    fig_smt_linux_core_scheduling()
    print('All figures generated successfully.')
