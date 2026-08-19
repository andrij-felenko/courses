# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. SMP проти NUMA: спільна шина проти локальних вузлів ────────────────────
def fig_smp_vs_numa():
    W, H = 760, 400
    p = []

    # Заголовок
    p.append(text(W / 2, 24, "Еволюція доступу до пам'яті: спільна шина (SMP) проти розподілених вузлів (NUMA)", size=13, bold=True))

    # ── SMP ліворуч ──
    p.append(rect(20, 45, 345, 335, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(192, 68, "SMP (Symmetric Multiprocessing)", size=13, bold=True, color=POS))
    p.append(text(192, 85, "однакова затримка, вузьке горло на шині", size=10, color=MUTED))

    # Ядра SMP
    for i in range(4):
        cx = 40 + i * 78
        p.append(rect(cx, 105, 68, 48, fill="#fdf2f0", stroke=POS, sw=1.5, rx=5))
        p.append(text(cx + 34, 126, "ЦП %d" % i, size=11, bold=True, color=POS))
        p.append(text(cx + 34, 142, "L1/L2/L3", size=9, color=MUTED))
        p.append(line(cx + 34, 153, cx + 34, 195, color=POS, sw=1.5))

    # Спільна системна шина
    p.append(rect(35, 195, 315, 24, fill="#fadbd6", stroke=POS, sw=1.8, rx=4))
    p.append(text(192, 211, "Спільна системна шина (FSB / контеншн)", size=10, bold=True, color=POS))

    # Лінії до контролера пам'яті
    p.append(line(192, 219, 192, 255, color=POS, sw=2.0))

    # Контролер пам'яті
    p.append(rect(95, 255, 195, 36, fill="#f4f6f8", stroke=INK, sw=1.5, rx=5))
    p.append(text(192, 277, "Контролер пам'яті (Northbridge)", size=10, bold=True))

    p.append(line(192, 291, 192, 320, color=INK, sw=1.8))

    # Спільна оперативна пам'ять
    p.append(rect(65, 320, 255, 42, fill="#eef6ff", stroke=NEG, sw=1.6, rx=5))
    p.append(text(192, 338, "Єдина спільна пам'ять DRAM", size=11, bold=True, color=NEG))
    p.append(text(192, 353, "Затримка однакова для всіх (~70 нс)", size=9, color=MUTED))

    # ── NUMA праворуч ──
    p.append(rect(395, 45, 345, 335, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(567, 68, "NUMA (Non-Uniform Memory Access)", size=13, bold=True, color=FIELD))
    p.append(text(567, 85, "неоднорідний доступ: локальна швидка, віддалена повільна", size=10, color=MUTED))

    # Вузол 0
    p.append(rect(410, 105, 145, 175, fill="#e7f7ee", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(482, 124, "NUMA-вузол 0", size=11, bold=True, color=FIELD))
    p.append(rect(420, 134, 125, 40, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(482, 151, "Сокет 0 (Ядра 0..N)", size=10, bold=True))
    p.append(text(482, 165, "Локальний кеш L3", size=9, color=MUTED))
    p.append(rect(420, 182, 125, 30, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(482, 201, "Контролер IMC 0", size=9, bold=True))
    p.append(line(482, 212, 482, 230, color=FIELD, sw=1.5))
    p.append(rect(420, 230, 125, 40, fill="#eef6ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(482, 247, "Локальна DRAM 0", size=10, bold=True, color=NEG))
    p.append(text(482, 261, "~60 нс (швидко)", size=9, color=FIELD))

    # Вузол 1
    p.append(rect(580, 105, 145, 175, fill="#e7f7ee", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(652, 124, "NUMA-вузол 1", size=11, bold=True, color=FIELD))
    p.append(rect(590, 134, 125, 40, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(652, 151, "Сокет 1 (Ядра N+1..M)", size=10, bold=True))
    p.append(text(652, 165, "Локальний кеш L3", size=9, color=MUTED))
    p.append(rect(590, 182, 125, 30, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(652, 201, "Контролер IMC 1", size=9, bold=True))
    p.append(line(652, 212, 652, 230, color=FIELD, sw=1.5))
    p.append(rect(590, 230, 125, 40, fill="#eef6ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(652, 247, "Локальна DRAM 1", size=10, bold=True, color=NEG))
    p.append(text(652, 261, "~60 нс (швидко)", size=9, color=FIELD))

    # Міжпроцесорна шина між сокетами
    p.append(rect(450, 300, 235, 40, fill="#fadbd6", stroke=POS, sw=1.6, rx=5))
    p.append(text(567, 318, "Міжпроцесорний лінк (UPI / Infinity Fabric)", size=10, bold=True, color=POS))
    p.append(text(567, 332, "Віддалений доступ: ~130–180 нс (штраф 2–3×)", size=9, color=POS))

    p.append(line(482, 280, 482, 300, color=POS, sw=1.6))
    p.append(line(652, 280, 652, 300, color=POS, sw=1.6))

    render(os.path.join(OUT, "smp-vs-numa.svg"), W, H, *p)


# ── 2. Топологія з'єднань, матриця відстаней SLIT та хопи ─────────────────────
def fig_interconnect_topology():
    W, H = 760, 360
    p = []

    p.append(text(W / 2, 24, "Топологія міжпроцесорних лінків та матриця відносних відстаней (ACPI SLIT)", size=13, bold=True))

    # 4 сокети в сітці
    # Вузол 0 (верхній лівий)
    p.append(rect(50, 60, 130, 75, fill="#e7f7ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(115, 83, "Вузол 0", size=12, bold=True, color=FIELD))
    p.append(text(115, 101, "Сокет 0 + RAM 0", size=10))
    p.append(text(115, 119, "Локально: 10", size=9, color=MUTED))

    # Вузол 1 (верхній правий)
    p.append(rect(250, 60, 130, 75, fill="#e7f7ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(315, 83, "Вузол 1", size=12, bold=True, color=FIELD))
    p.append(text(315, 101, "Сокет 1 + RAM 1", size=10))
    p.append(text(315, 119, "Локально: 10", size=9, color=MUTED))

    # Вузол 2 (нижній лівий)
    p.append(rect(50, 220, 130, 75, fill="#e7f7ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(115, 243, "Вузол 2", size=12, bold=True, color=FIELD))
    p.append(text(115, 261, "Сокет 2 + RAM 2", size=10))
    p.append(text(115, 279, "Локально: 10", size=9, color=MUTED))

    # Вузол 3 (нижній правий)
    p.append(rect(250, 220, 130, 75, fill="#e7f7ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(315, 243, "Вузол 3", size=12, bold=True, color=FIELD))
    p.append(text(315, 261, "Сокет 3 + RAM 3", size=10))
    p.append(text(315, 279, "Локально: 10", size=9, color=MUTED))

    # Прямі зв'язки (1 хоп)
    # Вузол 0 <-> Вузол 1
    p.append(line(180, 97, 250, 97, color=NEG, sw=2.5))
    p.append(text(215, 90, "1 хоп", size=9, bold=True, color=NEG))

    # Вузол 0 <-> Вузол 2
    p.append(line(115, 135, 115, 220, color=NEG, sw=2.5))
    p.append(text(88, 178, "1 хоп", size=9, bold=True, color=NEG))

    # Вузол 1 <-> Вузол 3
    p.append(line(315, 135, 315, 220, color=NEG, sw=2.5))
    p.append(text(342, 178, "1 хоп", size=9, bold=True, color=NEG))

    # Вузол 2 <-> Вузол 3
    p.append(line(180, 257, 250, 257, color=NEG, sw=2.5))
    p.append(text(215, 250, "1 хоп", size=9, bold=True, color=NEG))

    # Діагональ без прямого лінка (2 хопи: 0 -> 3 через 1 або 2), розділена на два відрізки навколо підпису
    p.append(line(180, 135, 195, 153, color=POS, sw=1.8, dash="4,3"))
    p.append(line(235, 202, 250, 220, color=POS, sw=1.8, dash="4,3"))
    tb, _, _ = textbox(215, 178, "2 хопи (транзит)", size=9, pad=5, fill="#ffffff", stroke=POS, sw=1.0, color=POS, bold=True, rx=3)
    p.append(tb)

    # Підпис топології
    p.append(text(215, 325, "Топологія кільце/сітка (Ring / Mesh)", size=11, bold=True, color=INK))
    p.append(text(215, 342, "Кількість проміжних пересилань (хопів) визначає затримку", size=9, color=MUTED))

    # Таблиця SLIT праворуч
    p.append(rect(430, 60, 300, 265, fill="#fdfefe", stroke=INK, sw=1.4, rx=6))
    p.append(text(580, 85, "Матриця дистанцій SLIT (numactl -H)", size=11, bold=True, color=INK))

    # Заголовки таблиці
    headers = ["Node", "0", "1", "2", "3"]
    col_x = [450, 505, 555, 605, 655]
    for idx, h in enumerate(headers):
        p.append(text(col_x[idx] + 15, 115, h, size=11, bold=True, color=INK))
    p.append(line(445, 125, 715, 125, color=INK, sw=1.2))

    # Рядки таблиці SLIT
    matrix = [
        ["0:", "10", "21", "21", "31"],
        ["1:", "21", "10", "31", "21"],
        ["2:", "21", "31", "10", "21"],
        ["3:", "31", "21", "21", "10"],
    ]

    for row_idx, row in enumerate(matrix):
        ry = 150 + row_idx * 28
        p.append(text(col_x[0] + 15, ry, row[0], size=11, bold=True, color=INK))
        for col_idx, val in enumerate(row[1:]):
            val_x = col_x[col_idx + 1] + 15
            color = FIELD if val == "10" else (NEG if val == "21" else POS)
            bold = val == "10" or val == "31"
            p.append(text(val_x, ry, val, size=11, bold=bold, color=color))

    p.append(line(445, 260, 715, 260, color=MUTED, sw=0.8, dash="3,3"))
    p.append(text(580, 280, "10 = локальний доступ (базова база ×1.0)", size=9, color=FIELD))
    p.append(text(580, 296, "21 = прямий лінк / 1 хоп (~2.1× затримки)", size=9, color=NEG))
    p.append(text(580, 312, "31 = транзитний вузол / 2 хопи (~3.1× затримки)", size=9, color=POS))

    render(os.path.join(OUT, "interconnect-topology.svg"), W, H, *p)


# ── 3. Ієрархія пам'яті ядра Linux: NODE_DATA, зони та бадді-алокатор ──────────
def fig_linux_numa_arch():
    W, H = 760, 380
    p = []

    p.append(text(W / 2, 24, "Структури пам'яті ядра Linux для NUMA: незалежний стан кожного вузла", size=13, bold=True))

    # Головний масив покажчиків NODE_DATA
    p.append(rect(40, 55, 680, 45, fill="#f4f6f8", stroke=INK, sw=1.6, rx=6))
    p.append(text(380, 74, "Глобальний масив ядра: struct pglist_data *node_data[MAX_NUMNODES]", size=11, bold=True))
    p.append(text(380, 90, "Макрос NODE_DATA(node_id) повертає дескриптор пам'яті відповідного вузла", size=9, color=MUTED))

    # Стрілки вниз до вузлів
    p.append(arrow(200, 100, 200, 130, color=FIELD, sw=1.8))
    p.append(arrow(560, 100, 560, 130, color=FIELD, sw=1.8))

    # Дескриптор Вузла 0
    p.append(rect(40, 130, 320, 230, fill="#e7f7ee", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(200, 150, "NODE_DATA(0) : pg_data_t", size=12, bold=True, color=FIELD))
    p.append(text(200, 166, "Фізичний простір пам'яті Вузла 0", size=9, color=MUTED))

    # Зони вузла 0
    p.append(rect(55, 180, 290, 48, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(200, 198, "Зони пам'яті (node_zones[])", size=10, bold=True))
    p.append(text(200, 214, "ZONE_DMA32 · ZONE_NORMAL · ZONE_MOVABLE", size=9, color=MUTED))

    # Бадді-алокатор вузла 0
    p.append(rect(55, 236, 290, 54, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(200, 254, "Buddy Allocator (free_area[MAX_ORDER])", size=10, bold=True, color=NEG))
    p.append(text(200, 270, "Власні списки вільних сторінок 4 КБ..4 МБ", size=9, color=MUTED))
    p.append(text(200, 283, "Алокація не блокує сусідні вузли", size=9, color=FIELD))

    # Демон kswapd вузла 0
    p.append(rect(55, 298, 290, 48, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(200, 316, "kswapd0 (фонове вивільнення)", size=10, bold=True, color=POS))
    p.append(text(200, 332, "Слідкує за вотермарками (min/low/high) Вузла 0", size=9, color=MUTED))

    # Дескриптор Вузла 1
    p.append(rect(400, 130, 320, 230, fill="#e7f7ee", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(560, 150, "NODE_DATA(1) : pg_data_t", size=12, bold=True, color=FIELD))
    p.append(text(560, 166, "Фізичний простір пам'яті Вузла 1", size=9, color=MUTED))

    # Зони вузла 1
    p.append(rect(415, 180, 290, 48, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    p.append(text(560, 198, "Зони пам'яті (node_zones[])", size=10, bold=True))
    p.append(text(560, 214, "ZONE_NORMAL · ZONE_MOVABLE", size=9, color=MUTED))

    # Бадді-алокатор вузла 1
    p.append(rect(415, 236, 290, 54, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(560, 254, "Buddy Allocator (free_area[MAX_ORDER])", size=10, bold=True, color=NEG))
    p.append(text(560, 270, "Власні списки вільних сторінок 4 КБ..4 МБ", size=9, color=MUTED))
    p.append(text(560, 283, "Алокація не блокує сусідні вузли", size=9, color=FIELD))

    # Демон kswapd вузла 1
    p.append(rect(415, 298, 290, 48, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(560, 316, "kswapd1 (фонове вивільнення)", size=10, bold=True, color=POS))
    p.append(text(560, 332, "Слідкує за вотермарками (min/low/high) Вузла 1", size=9, color=MUTED))

    render(os.path.join(OUT, "linux-numa-arch.svg"), W, H, *p)


# ── 4. NUMA Thrashing і пастка First-Touch у багатопотокових серверах ─────────
def fig_numa_thrashing():
    W, H = 760, 380
    p = []

    p.append(text(W / 2, 24, "Пастка First-Touch і механізм NUMA Thrashing у багатопотокових серверах", size=13, bold=True))

    # Сценарій ліворуч: Помилка First-Touch (усі дані на одному вузлі)
    p.append(rect(20, 50, 345, 315, fill="#fdfefe", stroke=POS, sw=1.4, rx=8))
    p.append(text(192, 72, "1. First-Touch без чергування (Помилка)", size=11, bold=True, color=POS))
    p.append(text(192, 88, "Головний потік виділив спільний пул на Node 0", size=9, color=MUTED))

    # Сокет 0 і його пам'ять
    p.append(rect(35, 105, 150, 80, fill="#fdf2f0", stroke=POS, sw=1.2, rx=5))
    p.append(text(110, 125, "Node 0 (Master)", size=10, bold=True, color=POS))
    p.append(rect(45, 138, 130, 38, fill="#ffffff", stroke=POS, sw=1.0, rx=4))
    p.append(text(110, 153, "Вся пам'ять пулу", size=9, bold=True))
    p.append(text(110, 167, "100% сторінок на Node 0", size=9, color=POS))

    # Сокет 1 і його потоки
    p.append(rect(200, 105, 150, 80, fill="#eef6ff", stroke=NEG, sw=1.2, rx=5))
    p.append(text(275, 125, "Node 1 (Workers)", size=10, bold=True, color=NEG))
    p.append(text(275, 145, "Потоки виконують", size=9.5))
    p.append(text(275, 162, "запити клієнтів", size=9.5))

    # Червона стрілка віддаленого доступу
    p.append(arrow(235, 192, 145, 192, color=POS, sw=2.2))
    p.append(text(192, 212, "Перевантаження шини UPI/IF", size=9.5, bold=True, color=POS))
    p.append(text(192, 226, "Кожен доступ з Node 1 — віддалений!", size=9, color=POS))

    # Наслідки ліворуч
    p.append(rect(35, 238, 315, 115, fill="#fadbd6", stroke=POS, sw=1.0, rx=5))
    p.append(text(192, 255, "Наслідки: деградація продуктивності", size=10, bold=True, color=POS))
    p.append(text(192, 273, "• Штраф латентності пам'яті 2–3× на кожному кеш-промаху", size=9, color=INK))
    p.append(text(192, 290, "• AutoNUMA сканує сторінки й викликає шторм міграцій", size=9, color=INK))
    p.append(text(192, 307, "• Вузол 0 вичерпує пам'ять -> kswapd гальмує запити", size=9, color=INK))
    p.append(text(192, 324, "• Вузол 1 має вільну пам'ять, яка не використовується", size=9, color=INK))

    # Сценарій праворуч: Правильне рішення (Interleave або партиціонування)
    p.append(rect(395, 50, 345, 315, fill="#fdfefe", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(567, 72, "2. NUMA-Aware Архітектура (Рішення)", size=11, bold=True, color=FIELD))
    p.append(text(567, 88, "Чергування сторінок або ізольовані процеси", size=9, color=MUTED))

    # Варіант А: Interleave
    p.append(rect(410, 105, 315, 68, fill="#e7f7ee", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(567, 123, "Варіант А: Чергування (MPOL_INTERLEAVE)", size=10, bold=True, color=FIELD))
    p.append(text(567, 140, "numactl --interleave=all ./postgres", size=9.5, color=INK))
    p.append(text(567, 156, "Сторінки 4 КБ рівномірно діляться між вузлами", size=9, color=MUTED))

    # Варіант Б: Секціонування
    p.append(rect(410, 180, 315, 68, fill="#e7f7ee", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(567, 198, "Варіант Б: Ізольовані екземпляри (Instance Pinning)", size=10, bold=True, color=FIELD))
    p.append(text(567, 215, "numactl --cpunodebind=0 --membind=0 ./redis-server-0", size=9.5, color=INK))
    p.append(text(567, 231, "numactl --cpunodebind=1 --membind=1 ./redis-server-1", size=9.5, color=INK))

    # Зиск праворуч
    p.append(rect(410, 255, 315, 98, fill="#ffffff", stroke=FIELD, sw=1.0, rx=5))
    p.append(text(567, 273, "Результат оптимізації:", size=10, bold=True, color=FIELD))
    p.append(text(567, 291, "✓ Передбачувана низька затримка запитів (p99)", size=9, color=INK))
    p.append(text(567, 308, "✓ Повна утилізація пропускної здатності шин пам'яті", size=9, color=INK))
    p.append(text(567, 325, "✓ Відсутність блокувань міжвузлових лінків", size=9, color=INK))

    render(os.path.join(OUT, "numa-thrashing.svg"), W, H, *p)


if __name__ == "__main__":
    fig_smp_vs_numa()
    fig_interconnect_topology()
    fig_linux_numa_arch()
    fig_numa_thrashing()
    print("Всі фігури згенеровано успішно.")
