# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори для ниток
T0_FILL = '#eaf0fd'    # Світло-синій (Нитка 0)
T0_STROKE = '#2457d6'  # Синій контур
T1_FILL = '#fdecea'    # Світло-червоний (Нитка 1)
T1_STROKE = '#c0392b'  # Червоний контур
EMPTY_FILL = '#f8f9fa' # Порожній слот (простій)
EMPTY_STROKE = '#d1d5db'
SHARED_FILL = '#eef7ee'
SHARED_STROKE = '#27ae60'

# ── Фігура 1: Порівняння утилізації конвеєра: однопотоковий, FGMT та SMT ──────
def fig_waste_comparison():
    W, H = 840, 400
    frags = []

    frags.append(text(W / 2, 26, 'Утилізація слотів конвеєра за тактами (ширина = 4 команди)', size=15, bold=True))

    cols = 4
    rows = 6
    cw, ch = 25, 23
    pad_x = 3

    configs = [
        ('Однопотоковий суперскаляр', 50, 65, [
            [1, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 0, 0, 0],
        ], 'Вертикальний і горизонтальний простій'),

        ('Чергова багатонитковість (FGMT)', 320, 65, [
            [1, 1, 1, 0],
            [2, 2, 0, 0],
            [1, 1, 0, 0],
            [2, 2, 2, 0],
            [1, 1, 1, 1],
            [2, 0, 0, 0],
        ], 'Усуває вертикальний простій'),

        ('Одночасна багатонитковість (SMT)', 590, 65, [
            [1, 1, 1, 2],
            [1, 1, 2, 2],
            [2, 2, 2, 0],
            [2, 2, 1, 0],
            [1, 1, 1, 2],
            [1, 2, 2, 2],
        ], 'Усуває обидва види простою')
    ]

    for title, px, py, grid, subtitle in configs:
        frags.append(rect(px - 10, py, 205, 255, fill=FILL, stroke=EMPTY_STROKE, sw=1, rx=6))
        frags.append(text(px + 92, py + 20, title, size=11, bold=True))
        frags.append(text(px + 92, py + 36, subtitle, size=10, color=MUTED, italic=True))

        for c in range(cols):
            frags.append(text(px + 40 + c * (cw + pad_x) + cw / 2, py + 54, 'С%d' % (c + 1), size=10, color=MUTED))

        for r in range(rows):
            frags.append(text(px + 18, py + 72 + r * (ch + 4) + ch / 2 + 3, 'Т%d' % (r + 1), size=10, color=INK, bold=True))
            for c in range(cols):
                val = grid[r][c]
                rx_pos = px + 40 + c * (cw + pad_x)
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

    ly = H - 35
    frags.append(rect(140, ly, 18, 18, fill=T0_FILL, stroke=T0_STROKE, sw=1.2, rx=3))
    frags.append(text(165, ly + 13, 'Команда Нитки 0 (Н0)', size=11, anchor='start'))

    frags.append(rect(340, ly, 18, 18, fill=T1_FILL, stroke=T1_STROKE, sw=1.2, rx=3))
    frags.append(text(365, ly + 13, 'Команда Нитки 1 (Н1)', size=11, anchor='start'))

    frags.append(rect(540, ly, 18, 18, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(565, ly + 13, 'Порожній слот (бульбашка простою)', size=11, anchor='start'))

    render(os.path.join(IMG, 'waste-comparison.svg'), W, H, *frags)


# ── Фігура 2: Внутрішня будова SMT-ядра: дубльоване, розділене, спільне ───────
def fig_smt_pipeline_split():
    W, H = 840, 500
    frags = []

    frags.append(text(W / 2, 24, 'Мікроархітектура SMT-ядра: розподіл ресурсів між нитками', size=15, bold=True))

    # Зона 1
    frags.append(rect(40, 48, 760, 98, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(55, 68, '1. Дубльований архітектурний стан (окремо для кожної нитки)', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(60, 80, 340, 52, fill=T0_FILL, stroke=T0_STROKE, sw=1.2, rx=4))
    frags.append(text(230, 98, 'Логічний процесор 0 (Нитка 0)', size=11, bold=True, color=T0_STROKE))
    frags.append(text(230, 116, 'RAX..R15 · RIP (PC0) · CR3 · APIC 0 · RAT 0', size=10, color=INK))

    frags.append(rect(440, 80, 340, 52, fill=T1_FILL, stroke=T1_STROKE, sw=1.2, rx=4))
    frags.append(text(610, 98, 'Логічний процесор 1 (Нитка 1)', size=11, bold=True, color=T1_STROKE))
    frags.append(text(610, 116, 'RAX..R15 · RIP (PC1) · CR3 · APIC 1 · RAT 1', size=10, color=INK))

    frags.append(arrow(230, 134, 230, 160, color=LINE, sw=1.2))
    frags.append(arrow(610, 134, 610, 160, color=LINE, sw=1.2))

    # Зона 2
    frags.append(rect(40, 160, 760, 82, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(55, 178, '2. Статично розділені буфери конвеєра (50% / 50% при двох нитках)', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(60, 190, 340, 42, fill='#ffffff', stroke=T0_STROKE, sw=1.2, rx=4))
    frags.append(text(230, 206, 'Черга вибірки 0 (Fetch Queue 0)', size=10.5, bold=True))
    frags.append(text(230, 222, 'Буфер перевпорядкування 0 (ROB 0) · RSB 0', size=10, color=MUTED))

    frags.append(rect(440, 190, 340, 42, fill='#ffffff', stroke=T1_STROKE, sw=1.2, rx=4))
    frags.append(text(610, 206, 'Черга вибірки 1 (Fetch Queue 1)', size=10.5, bold=True))
    frags.append(text(610, 222, 'Буфер перевпорядкування 1 (ROB 1) · RSB 1', size=10, color=MUTED))

    frags.append(arrow(230, 242, 350, 268, color=LINE, sw=1.2))
    frags.append(arrow(610, 242, 490, 268, color=LINE, sw=1.2))

    # Зона 3
    frags.append(rect(40, 268, 760, 115, fill=SHARED_FILL, stroke=SHARED_STROKE, sw=1.5, rx=6))
    frags.append(text(55, 288, '3. Спільний позачерговий рушій (Out-of-Order Engine) та виконавчі блоки', size=12, bold=True, anchor='start', color=FIELD))

    frags.append(rect(55, 300, 220, 70, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(165, 320, 'Спільний планувальник', size=10.5, bold=True))
    frags.append(text(165, 338, 'Станції резервування', size=10, color=MUTED))
    frags.append(text(165, 354, 'Unified RS (єдина черга)', size=9.5, color=MUTED))

    frags.append(rect(290, 300, 220, 70, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(400, 320, 'Регістровий файл PRF', size=10.5, bold=True))
    frags.append(text(400, 338, 'Спільний фізичний пул', size=10, color=MUTED))
    frags.append(text(400, 354, '180–280 фізичних регістрів', size=9.5, color=MUTED))

    frags.append(rect(525, 300, 260, 70, fill='#ffffff', stroke=SHARED_STROKE, sw=1, rx=4))
    frags.append(text(655, 320, 'Виконавчі порти ядра', size=10.5, bold=True))
    frags.append(text(655, 338, 'Порт 0, 1: ALU / FMA / Вектори', size=9.5, color=INK))
    frags.append(text(655, 354, 'Порт 2, 3: Load / Store AGU', size=9.5, color=INK))

    frags.append(arrow(420, 385, 420, 410, color=LINE, sw=1.2))

    # Зона 4
    frags.append(rect(40, 410, 760, 72, fill='#fdfefe', stroke=LINE, sw=1.2, rx=6))
    frags.append(text(55, 430, '4. Спільна ієрархія кешів та трансляції адрес', size=12, bold=True, anchor='start', color=INK))

    frags.append(rect(55, 442, 215, 30, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(162, 461, 'Кеш інструкцій L1I (32–64 КБ)', size=10, bold=True))

    frags.append(rect(285, 442, 215, 30, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(392, 461, 'Кеш даних L1D (32–48 КБ)', size=10, bold=True))

    frags.append(rect(515, 442, 270, 30, fill=FILL, stroke=MUTED, sw=1, rx=3))
    frags.append(text(650, 461, 'Спільний L2 Кеш та DTLB / ITLB', size=10, bold=True))

    render(os.path.join(IMG, 'smt-pipeline-split.svg'), W, H, *frags)


# ── Фігура 3: Атаки через спільні ресурси (PortSmash та L1TF) ─────────────────
def fig_sidechannel_contention():
    W, H = 820, 400
    frags = []

    frags.append(text(W / 2, 26, 'Атаки побічними каналами та конкуренція за спільні ресурси SMT', size=15, bold=True))

    # Ліва половина: PortSmash
    frags.append(rect(40, 55, 355, 315, fill=FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(217, 80, 'PortSmash: витік через порти виконання', size=12, bold=True, color=POS))
    frags.append(text(217, 98, 'Конкуренція за Порт 0 / Порт 1 в один такт', size=10, color=MUTED))

    frags.append(rect(55, 115, 150, 65, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=4))
    frags.append(text(130, 135, 'Жертва (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(130, 152, 'OpenSSL ECDSA', size=10, color=INK))
    frags.append(text(130, 168, 'Множення точок кривої', size=9.5, color=MUTED))

    frags.append(rect(230, 115, 150, 65, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=4))
    frags.append(text(305, 135, 'Шпигун (Нитка 1)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(305, 152, 'Безперервні операції', size=10, color=INK))
    frags.append(text(305, 168, 'Вимір затримки RDTSC', size=9.5, color=MUTED))

    frags.append(arrow(130, 182, 195, 212, color=LINE, sw=1))
    frags.append(arrow(305, 182, 240, 212, color=LINE, sw=1))

    frags.append(rect(95, 212, 245, 52, fill='#ffffff', stroke=POS, sw=1.5, rx=4))
    frags.append(text(217, 232, 'Спільний Порт 0 (ALU/Множення)', size=11, bold=True))
    frags.append(text(217, 250, 'Затримка шпигуна росте під час множення', size=9.5, color=POS))

    frags.append(rect(55, 280, 325, 75, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(217, 300, 'Наслідок для безпеки:', size=10.5, bold=True))
    frags.append(text(217, 320, 'Шпигун реконструює біти ключа', size=10, color=INK))
    frags.append(text(217, 338, 'за коливаннями затримок виконання', size=9.5, color=MUTED))

    # Права половина: L1TF / Foreshadow
    frags.append(rect(425, 55, 355, 315, fill=FILL, stroke=POS, sw=1.2, rx=6))
    frags.append(text(602, 80, 'L1TF / Foreshadow: витік через L1D', size=12, bold=True, color=POS))
    frags.append(text(602, 98, 'Спекулятивне читання кешу іншої нитки', size=10, color=MUTED))

    frags.append(rect(440, 115, 150, 65, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=4))
    frags.append(text(515, 135, 'Гіпервізор / SGX (Н0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(515, 152, 'Конфіденційні дані', size=10, color=INK))
    frags.append(text(515, 168, 'Залишаються в L1D', size=9.5, color=MUTED))

    frags.append(rect(615, 115, 150, 65, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=4))
    frags.append(text(690, 135, 'Гість-атакувальник (Н1)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(690, 152, 'Недійсна адреса PTE', size=10, color=INK))
    frags.append(text(690, 168, 'Спекулятивне читання', size=9.5, color=MUTED))

    frags.append(arrow(515, 182, 580, 212, color=LINE, sw=1))
    frags.append(arrow(690, 182, 625, 212, color=LINE, sw=1))

    frags.append(rect(480, 212, 245, 52, fill='#ffffff', stroke=POS, sw=1.5, rx=4))
    frags.append(text(602, 232, 'Спільний кеш даних L1D', size=11, bold=True))
    frags.append(text(602, 250, 'Спекулятивне читання до виключення', size=9.5, color=POS))

    frags.append(rect(440, 280, 325, 75, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(602, 300, 'Наслідок для безпеки:', size=10.5, bold=True))
    frags.append(text(602, 320, 'Читання пам\'яті хоста чи інших VM', size=10, color=INK))
    frags.append(text(602, 338, 'через спільний фізичний кеш одного ядра', size=9.5, color=MUTED))

    render(os.path.join(IMG, 'sidechannel-contention.svg'), W, H, *frags)


# ── Фігура 4: Linux Core Scheduling та топологія ──────────────────────────────
def fig_linux_sched_core():
    W, H = 820, 400
    frags = []

    frags.append(text(W / 2, 24, 'Планування в Linux: топологія та механізм Core Scheduling', size=15, bold=True))

    # Ліва колонка
    frags.append(rect(40, 50, 355, 320, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(217, 74, '1. Звичайне планування (SMT-aware)', size=12, bold=True))
    frags.append(text(217, 92, 'Пріоритет: спершу вільні фізичні ядра', size=10, color=MUTED))

    # Ядро 0
    frags.append(rect(55, 108, 325, 105, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    frags.append(text(217, 126, 'Фізичне ядро 0 (Core 0)', size=11, bold=True))
    frags.append(rect(65, 138, 145, 64, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(137, 160, 'CPU 0 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(137, 180, 'Процес A (зайнято)', size=9.5, color=INK))

    frags.append(rect(225, 138, 145, 64, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(297, 160, 'CPU 1 (Нитка 1)', size=10.5, bold=True, color=MUTED))
    frags.append(text(297, 180, 'Вільний (idle)', size=9.5, color=MUTED))

    # Ядро 1
    frags.append(rect(55, 230, 325, 105, fill='#ffffff', stroke=LINE, sw=1, rx=4))
    frags.append(text(217, 248, 'Фізичне ядро 1 (Core 1)', size=11, bold=True))
    frags.append(rect(65, 260, 145, 64, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(137, 282, 'CPU 2 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(137, 302, 'Процес B (надіслано сюди)', size=9.5, color=FIELD, bold=True))

    frags.append(rect(225, 260, 145, 64, fill=EMPTY_FILL, stroke=EMPTY_STROKE, sw=1, rx=3))
    frags.append(text(297, 282, 'CPU 3 (Нитка 1)', size=10.5, bold=True, color=MUTED))
    frags.append(text(297, 302, 'Вільний (idle)', size=9.5, color=MUTED))

    # Права колонка
    frags.append(rect(425, 50, 355, 320, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(602, 74, '2. Core Scheduling (PR_SCHED_CORE)', size=12, bold=True, color=FIELD))
    frags.append(text(602, 92, 'Ізоляція за доменами довіри (Cookie)', size=10, color=MUTED))

    # Ядро 0
    frags.append(rect(440, 108, 325, 105, fill='#ffffff', stroke=SHARED_STROKE, sw=1.2, rx=4))
    frags.append(text(602, 126, 'Фізичне ядро 0: Домен довіри Cookie = X', size=10.5, bold=True, color=FIELD))
    frags.append(rect(450, 138, 145, 64, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(522, 160, 'CPU 0 (Нитка 0)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(522, 180, 'VM 1 (Cookie X)', size=9.5, color=INK))

    frags.append(rect(610, 138, 145, 64, fill=T0_FILL, stroke=T0_STROKE, sw=1, rx=3))
    frags.append(text(682, 160, 'CPU 1 (Нитка 1)', size=10.5, bold=True, color=T0_STROKE))
    frags.append(text(682, 180, 'VM 1 (Cookie X)', size=9.5, color=FIELD, bold=True))

    # Ядро 1
    frags.append(rect(440, 230, 325, 105, fill='#ffffff', stroke=POS, sw=1.2, rx=4))
    frags.append(text(602, 248, 'Фізичне ядро 1: Конфлікт доменів', size=10.5, bold=True, color=POS))
    frags.append(rect(450, 260, 145, 64, fill=T1_FILL, stroke=T1_STROKE, sw=1, rx=3))
    frags.append(text(522, 282, 'CPU 2 (Нитка 0)', size=10.5, bold=True, color=T1_STROKE))
    frags.append(text(522, 302, 'VM 2 (Cookie Y)', size=9.5, color=INK))

    frags.append(rect(610, 260, 145, 64, fill='#fff5f5', stroke=POS, sw=1, rx=3))
    frags.append(text(682, 282, 'CPU 3 (Нитка 1)', size=10.5, bold=True, color=POS))
    frags.append(text(682, 302, 'Примусовий простій (idle)', size=9, color=POS, bold=True))

    render(os.path.join(IMG, 'linux-sched-core.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_waste_comparison()
    fig_smt_pipeline_split()
    fig_sidechannel_contention()
    fig_linux_sched_core()
    print('All figures generated successfully.')
