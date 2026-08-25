# -*- coding: utf-8 -*-
"""Фігури для теми «NUMA: вузли, політики розміщення й багаторівнева пам'ять»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"
GRY_F = "#eceff3"
PUR_F = "#f3e8fd"


# ── 1. UMA проти NUMA ────────────────────────────────────────────────────────
def fig_numa_topology(path):
    W, H = 1200, 530
    F = []

    # Заголовок лівої частини: UMA
    F.append(fitbox(20, 20, 480, 44, "UMA: спільна системна шина (Uniform Memory Access)", size=14, bold=True, fill=FILL))
    # Блок процесорів UMA
    F.append(fitbox(35, 80, 100, 50, "Ядро 0", size=13, fill=BLU_F))
    F.append(fitbox(145, 80, 100, 50, "Ядро 1", size=13, fill=BLU_F))
    F.append(fitbox(255, 80, 100, 50, "Ядро 2", size=13, fill=BLU_F))
    F.append(fitbox(365, 80, 100, 50, "Ядро 3", size=13, fill=BLU_F))

    # Спільна шина
    F.append(rect(35, 160, 430, 32, fill=RED_F, stroke=POS, sw=1.8))
    F.append(text(250, 181, "Спільна шина пам'яті (вузьке місце при масштабуванні)", size=12, color=POS, bold=True))

    for x in (85, 195, 305, 415):
        F.append(arrow(x, 130, x, 160, color=LINE, sw=1.5))

    # Контролер і спільна пам'ять
    F.append(arrow(250, 192, 250, 220, color=LINE, sw=1.5))
    F.append(fitbox(125, 220, 250, 44, "Контролер пам'яті (IMC)", size=13, fill=FILL))
    F.append(arrow(250, 264, 250, 290, color=LINE, sw=1.5))
    F.append(fitbox(85, 290, 330, 60, "Спільна оперативна пам'ять (DRAM)\nЗатримка однакова для всіх: ~70 нс", size=13, fill=GRN_F))

    # Пояснення UMA
    F.append(fitbox(20, 375, 480, 125, "Конкуренція за шину: що більше процесорів,\nто довша черга до єдиного контролера.\nПропускна здатність на одне ядро падає.", size=12, fill=FILL))

    # Вертикальний роздільник
    F.append(line(520, 20, 520, 505, color=MUTED, sw=1.2, dash="4,4"))

    # Заголовок правої частини: NUMA
    F.append(fitbox(540, 20, 640, 44, "NUMA: локальні контролери та вузли (Non-Uniform Memory Access)", size=14, bold=True, fill=FILL))

    # Вузол 0
    F.append(rect(540, 80, 220, 270, fill="#f8fafc", stroke=LINE, sw=1.5))
    F.append(text(650, 105, "NUMA-вузол 0 (Сокет 0)", size=13, bold=True))
    F.append(fitbox(550, 125, 95, 42, "Ядро 0..3", size=12, fill=BLU_F))
    F.append(fitbox(655, 125, 95, 42, "Ядро 4..7", size=12, fill=BLU_F))
    F.append(arrow(650, 167, 650, 195, color=LINE, sw=1.5))
    F.append(fitbox(550, 195, 200, 42, "Локальний IMC 0", size=12, fill=FILL))
    F.append(arrow(650, 237, 650, 265, color=LINE, sw=1.5))
    F.append(fitbox(550, 265, 200, 65, "Локальна пам'ять 0\nЗатримка: ~65 нс\nВідстань: 10", size=12, fill=GRN_F))

    # Вузол 1
    F.append(rect(960, 80, 220, 270, fill="#f8fafc", stroke=LINE, sw=1.5))
    F.append(text(1070, 105, "NUMA-вузол 1 (Сокет 1)", size=13, bold=True))
    F.append(fitbox(970, 125, 95, 42, "Ядро 8..11", size=12, fill=BLU_F))
    F.append(fitbox(1075, 125, 95, 42, "Ядро 12..15", size=12, fill=BLU_F))
    F.append(arrow(1070, 167, 1070, 195, color=LINE, sw=1.5))
    F.append(fitbox(970, 195, 200, 42, "Локальний IMC 1", size=12, fill=FILL))
    F.append(arrow(1070, 237, 1070, 265, color=LINE, sw=1.5))
    F.append(fitbox(970, 265, 200, 65, "Локальна пам'ять 1\nЗатримка: ~65 нс\nВідстань: 10", size=12, fill=GRN_F))

    # Міжпроцесорне з'єднання (UPI / Infinity Fabric) посередині
    F.append(fitbox(775, 185, 170, 50, "UPI / Infinity Fabric\nМіжпроцесорний лінк", size=11, bold=True, fill=YEL_F))
    F.append(arrow(760, 216, 775, 216, color=POS, sw=2))
    F.append(arrow(775, 216, 760, 216, color=POS, sw=2))
    F.append(arrow(945, 216, 960, 216, color=POS, sw=2))
    F.append(arrow(960, 216, 945, 216, color=POS, sw=2))

    # Пояснення NUMA
    F.append(fitbox(540, 375, 640, 125, "Віддалений доступ (Ядро 0 → Пам'ять 1):\nШлях через міжпроцесорну шину додає затримку (+60–100 нс).\nЗатримка: ~135–160 нс (Відстань: 20–21).\nРоздільні шини масштабують сумарну пропускну здатність системи.", size=12, fill=FILL))

    return render(path, W, H, *F)


# ── 2. Ієрархія pg_data_t і списки зон (zonelists) ───────────────────────────
def fig_pgdata_zonelist(path):
    W, H = 1080, 530
    F = []

    F.append(fitbox(30, 20, 1020, 44, "Структури ядра Linux: вузли pg_data_t, зони та zonelists обходу", size=15, bold=True, fill=FILL))

    # Вузол 0
    F.append(rect(40, 85, 470, 225, fill="#f8fafc", stroke=LINE, sw=1.6))
    F.append(text(275, 112, "NODE 0: struct pglist_data (pg_data_t)", size=14, bold=True))
    F.append(fitbox(55, 130, 130, 55, "ZONE_DMA32\n(0..4 ГіБ)", size=12, fill=BLU_F))
    F.append(fitbox(200, 130, 150, 55, "ZONE_NORMAL\n(DRAM Node 0)", size=12, fill=GRN_F))
    F.append(fitbox(365, 130, 130, 55, "ZONE_MOVABLE\n(гаряча заміна)", size=12, fill=PUR_F))

    F.append(fitbox(55, 205, 440, 85, "Поля вузла 0:\n• node_id = 0, node_present_pages\n• kswapd_wait (окремий потік kswapd0 на вузол)\n• node_zonelists[ZONELIST_FALLBACK]", size=12, fill=FILL))

    # Вузол 1
    F.append(rect(570, 85, 470, 225, fill="#f8fafc", stroke=LINE, sw=1.6))
    F.append(text(805, 112, "NODE 1: struct pglist_data (pg_data_t)", size=14, bold=True))
    F.append(fitbox(585, 130, 130, 55, "ZONE_DMA32\n(порожня)", size=12, fill=GRY_F))
    F.append(fitbox(730, 130, 150, 55, "ZONE_NORMAL\n(DRAM Node 1)", size=12, fill=GRN_F))
    F.append(fitbox(895, 130, 130, 55, "ZONE_MOVABLE\n(гаряча заміна)", size=12, fill=PUR_F))

    F.append(fitbox(585, 205, 440, 85, "Поля вузла 1:\n• node_id = 1, node_present_pages\n• kswapd_wait (окремий потік kswapd1 на вузол)\n• node_zonelists[ZONELIST_FALLBACK]", size=12, fill=FILL))

    # Схема zonelist fallback
    F.append(rect(40, 335, 1000, 165, fill=YEL_F, stroke=LINE, sw=1.4))
    F.append(text(540, 360, "Порядок обходу zonelist при виділенні звичайної пам'яті на Node 0", size=13, bold=True))

    steps = [
        ("1. Пріоритет: Локальний NORMAL", "Node 0 : ZONE_NORMAL", GRN_F),
        ("2. Fallback: Віддалений NORMAL", "Node 1 : ZONE_NORMAL", BLU_F),
        ("3. Fallback: Локальний DMA32", "Node 0 : ZONE_DMA32", RED_F),
    ]

    bx = 60
    for i, (title, sub, col) in enumerate(steps):
        F.append(fitbox(bx, 385, 210, 85, "%s\n%s" % (title, sub), size=12, bold=True, fill=col))
        if i < len(steps) - 1:
            F.append(arrow(bx + 210, 427, bx + 245, 427, color=LINE, sw=2))
        bx += 250

    F.append(fitbox(815, 385, 210, 85, "Стратегія ядра:\nВіддалений NORMAL\nкращий за обмежений\nлокальний DMA32.", size=12, fill=FILL))

    return render(path, W, H, *F)


# ── 3. Порівняння режимів mempolicy ──────────────────────────────────────────
def fig_mempolicy_modes(path):
    W, H = 1040, 560
    F = []

    F.append(fitbox(30, 15, 980, 40, "Режими політик виділення пам'яті ядра Linux (NUMA Memory Policies)", size=15, bold=True, fill=FILL))

    cards = [
        ("MPOL_DEFAULT / MPOL_LOCAL",
         "Локальне виділення за замовчуванням",
         "Пам'ять виділяється на тому вузлі, де виконується потік (first-touch).\nЯкщо потік на CPU 0 (Node 0) торкається сторінки — вона виділяється на Node 0.\nПри переповненні вузла переходить до сусідніх вузлів згідно зі SLIT.",
         BLU_F),
        ("MPOL_BIND (суворий список вузлів)",
         "Жорстка прив'язка до множини вузлів",
         "Виділення дозволено виключно на вузлах із заданої бітової маски (nodemask).\nЯкщо на дозволених вузлах закінчилася пам'ять — повертається помилка -ENOMEM,\nнавіть якщо інші вузли системи повністю вільні.",
         RED_F),
        ("MPOL_INTERLEAVE (чередування сторінок)",
         "Круг-робін розподіл сторінок між вузлами",
         "Сторінки віртуального діапазону циклічно чергуються: Page 0 → Node 0, Page 1 → Node 1...\nРівномірно розподіляє пропускну здатність пам'яті між усіма каналами.\nІдеально для спільних великих буферів і паралельних потоків.",
         GRN_F),
        ("MPOL_PREFERRED / PREFERRED_MANY",
         "Бажаний вузол із м'яким переходом",
         "Ядро намагається виділити пам'ять на вказаному бажаному вузлі.\nЯкщо на цьому вузлі пам'ять вичерпана або досягнуто водяного знаку,\nядро прозоро виділяє кадри на найближчих доступних вузлах.",
         PUR_F),
    ]

    y = 65
    for title, subtitle, desc, col in cards:
        F.append(rect(30, y, 980, 108, fill="#ffffff", stroke=LINE, sw=1.4))
        F.append(fitbox(45, y + 10, 310, 32, title, size=13, bold=True, fill=col))
        F.append(fitbox(45, y + 48, 310, 48, subtitle, size=12, fill=FILL))
        F.append(fitbox(370, y + 10, 625, 86, desc, size=12, fill=FILL))
        y += 120

    return render(path, W, H, *F)


# ── 4. Автоматичне балансування: NUMA Hinting Faults ─────────────────────────
def fig_auto_numa_hinting(path):
    W, H = 1040, 520
    F = []

    F.append(fitbox(30, 15, 980, 40, "Механізм Auto-NUMA Balancing: сканування PTE та Hinting Faults", size=15, bold=True, fill=FILL))

    steps = [
        ("1. Періодичний скан", "Ядро скидає біт Present\nу PTE сторінки\n(позначає _PAGE_NUMA /\nPROT_NONE)", BLU_F),
        ("2. Доступ потоку", "Потік на CPU 1 (Node 1)\nзвертається до пам'яті →\nMMU генерує\nNUMA Hinting Fault", YEL_F),
        ("3. do_numa_page()", "Ядро зчитує:\n• page_to_nid(page) = 0\n• cpu_to_node(cpu) = 1\nВиявлено віддалений доступ", RED_F),
        ("4. Аналіз локальності", "Оцінка доцільності:\nчи сторінка приватна?\nчи часто звертається?\nзахист від пінг-понгу", PUR_F),
        ("5. Міграція або Afinity", "migrate_misplaced_page()\nПеренесення кадру 0 → 1\nАБО міграція потоку\nна Node 0", GRN_F),
    ]

    bx = 30
    card_w = 175
    gap = 26
    for i, (title, desc, col) in enumerate(steps):
        F.append(rect(bx, 75, card_w, 200, fill="#ffffff", stroke=LINE, sw=1.4))
        F.append(fitbox(bx + 8, 85, card_w - 16, 36, title, size=12, bold=True, fill=col))
        F.append(fitbox(bx + 8, 130, card_w - 16, 135, desc, size=11, fill=FILL))
        if i < len(steps) - 1:
            arr_x1 = bx + card_w
            arr_x2 = bx + card_w + gap
            F.append(arrow(arr_x1 + 2, 175, arr_x2 - 2, 175, color=POS, sw=2))
        bx += card_w + gap

    # Нижня частина: стан пам'яті до і після
    F.append(rect(30, 295, 475, 205, fill="#f8fafc", stroke=LINE, sw=1.4))
    F.append(text(267, 320, "ДО балансування (Віддалений доступ)", size=13, bold=True, color=POS))
    F.append(fitbox(45, 335, 200, 60, "Потік виконується на:\nCPU 1 (NUMA Node 1)", size=12, fill=BLU_F))
    F.append(fitbox(290, 335, 200, 60, "Фізичний кадр лежить на:\nDRAM (NUMA Node 0)", size=12, fill=RED_F))
    F.append(line(245, 365, 290, 365, color=POS, sw=2, dash="4,4"))
    F.append(fitbox(45, 410, 445, 75, "Трафік іде через міжпроцесорну шину.\nЗатримка доступу висока (~140 нс),\nпропускна здатність обмежена.", size=12, fill=FILL))

    F.append(rect(535, 295, 475, 205, fill="#f8fafc", stroke=LINE, sw=1.4))
    F.append(text(772, 320, "ПІСЛЯ балансування (Локальний доступ)", size=13, bold=True, color=FIELD))
    F.append(fitbox(550, 335, 200, 60, "Потік виконується на:\nCPU 1 (NUMA Node 1)", size=12, fill=BLU_F))
    F.append(fitbox(795, 335, 200, 60, "Фізичний кадр перенесено:\nDRAM (NUMA Node 1)", size=12, fill=GRN_F))
    F.append(line(750, 365, 795, 365, color=FIELD, sw=2))
    F.append(fitbox(550, 410, 445, 75, "Прямий доступ через локальний контролер пам'яті.\nЗатримка мінімальна (~65 нс),\nміжпроцесорний лінк розвантажено.", size=12, fill=FILL))

    return render(path, W, H, *F)


# ── 5. Багаторівнева пам'ять (Tiered Memory / CXL) ───────────────────────────
def fig_tiered_memory(path):
    W, H = 1040, 520
    F = []

    F.append(fitbox(30, 15, 980, 40, "Багаторівнева пам'ять (Tiered Memory): DRAM, HBM і CXL Expander", size=15, bold=True, fill=FILL))

    # Верхній рівень (Top Tier: Швидка пам'ять)
    F.append(rect(40, 75, 960, 165, fill=GRN_F, stroke=LINE, sw=1.6))
    F.append(text(520, 100, "TOP TIER (Верхній рівень: швидка пам'ять із низькою затримкою)", size=14, bold=True, color=INK))
    F.append(fitbox(60, 115, 420, 105, "Локальна пам'ять DDR5 (Node 0, Node 1)\n• Затримка: ~60–80 нс\n• Призначення: гарячі анонімні сторінки та кеш\n• Політика за замовчуванням для нових виділень", size=12, fill="#ffffff"))
    F.append(fitbox(560, 115, 420, 105, "HBM / Спеціалізована пам'ять процесора\n• Висока пропускна здатність (>1 ТБ/с)\n• Обмежений обсяг\n• Пріоритет для обчислювальних ядер", size=12, fill="#ffffff"))

    # Стрілки переміщення даних між рівнями
    # Вниз: Demotion
    F.append(rect(150, 255, 320, 45, fill=BLU_F, stroke=LINE, sw=1.4))
    F.append(text(310, 277, "Фонове пониження (Demotion via kswapd)", size=12, bold=True))
    F.append(arrow(310, 240, 310, 255, color=LINE, sw=2))
    F.append(arrow(310, 300, 310, 315, color=LINE, sw=2))

    # Вгору: Promotion
    F.append(rect(570, 255, 320, 45, fill=POS, stroke=LINE, sw=1.4))
    F.append(text(730, 277, "Підвищення гарячих сторінок (Auto-NUMA Promotion)", size=12, bold=True, color="#ffffff"))
    F.append(arrow(730, 315, 730, 300, color=POS, sw=2))
    F.append(arrow(730, 255, 730, 240, color=POS, sw=2))

    # Нижній рівень (Slow Tier: Велика місткість)
    F.append(rect(40, 330, 960, 165, fill=YEL_F, stroke=LINE, sw=1.6))
    F.append(text(520, 355, "SLOW TIER / CAPACITY TIER (Нижній рівень: розширена місткість)", size=14, bold=True, color=INK))
    F.append(fitbox(60, 370, 420, 105, "CXL.mem пам'ять (CPU-less NUMA Node 2, 3)\n• Затримка: ~180–250 нс (PCIe / CXL лінк)\n• Велика місткість, спільний пул пам'яті\n• Холодні сторінки без викидання на диск", size=12, fill="#ffffff"))
    F.append(fitbox(560, 370, 420, 105, "Енергонезалежна пам'ять (PMEM / CXL SSD)\n• Стійкість до знеструмлення\n• Проміжний буфер між DRAM і дисковим сховищем\n• Розвантажує системний своп", size=12, fill="#ffffff"))

    return render(path, W, H, *F)


def main():
    figs = {
        'numa-topology.svg': fig_numa_topology,
        'pgdata-zonelist.svg': fig_pgdata_zonelist,
        'mempolicy-modes.svg': fig_mempolicy_modes,
        'auto-numa-hinting.svg': fig_auto_numa_hinting,
        'tiered-memory-numa.svg': fig_tiered_memory,
    }

    for name, func in figs.items():
        path = os.path.join(IMG, name)
        func(path)
        print(f"Generated {name}")


if __name__ == '__main__':
    main()
