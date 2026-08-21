# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdecea"
COOL   = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"

# ── 1. Дворівнева архітектура пам'яті ──────────────────────────────────────
def fig_tiering_architecture():
    W, H = 1200, 700
    p = []

    p.append(text(60, 36, "Дворівнева архітектура пам'яті: Top-tier (DRAM) проти Slow-tier (CXL)",
                  size=16, color=INK, anchor="start", bold=True))

    # Ліва колонка: Top-Tier (Швидкий ярус)
    p.append(rect(50, 70, 520, 250, fill="none", stroke=FIELD, sw=2, rx=10))
    p.append(fitbox(70, 85, 480, 40, "Top-Tier: Локальна пам'ять (DRAM / HBM) — Вузли 0 та 1", size=13, fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))

    p.append(fitbox(75, 140, 225, 75, "CPU Socket 0 / Node 0\n• DDR5 DRAM (60-80 ns)\n• Смуга: 300-800 GB/s", size=12, fill=SOFT, stroke=LINE, sw=1.2, color=INK))
    p.append(fitbox(315, 140, 225, 75, "CPU Socket 1 / Node 1\n• DDR5 DRAM (60-80 ns)\n• Смуга: 300-800 GB/s", size=12, fill=SOFT, stroke=LINE, sw=1.2, color=INK))

    p.append(fitbox(75, 230, 465, 72, "Гарячі дані процесу (Active LRU)\nКод, стек, гаряча купа, кеш індексів бази даних", size=12, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    # Права колонка: Slow-Tier (Повільний ярус)
    p.append(rect(630, 70, 520, 250, fill="none", stroke=NEG, sw=2, rx=10))
    p.append(fitbox(650, 85, 480, 40, "Slow-Tier: Розширена пам'ять (CXL.mem / PMEM) — Вузли 2 та 3", size=13, fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))

    p.append(fitbox(655, 140, 225, 75, "CXL Expander / Node 2\n• PCIe 5.0/6.0 CXL.mem\n• Затримка: 150-250 ns", size=12, fill=SOFT, stroke=LINE, sw=1.2, color=INK))
    p.append(fitbox(895, 140, 225, 75, "CXL Expander / Node 3\n• CPU-less NUMA Node\n• Смуга: 64-128 GB/s", size=12, fill=SOFT, stroke=LINE, sw=1.2, color=INK))

    p.append(fitbox(655, 230, 465, 72, "Холодні дані процесу (Inactive LRU)\nФонові буфери, рідко опитувані кеші, старі сесії", size=12, fill=COOL, stroke=NEG, sw=1.4, color=INK))

    # Стрілки міграцій між ярусами
    # 1. Demotion: з Top-tier донизу в Slow-tier
    p.append(fitbox(80, 360, 460, 80, "Асинхронний спуск (Page Demotion):\nkswapd виявляє дефіцит DRAM -> мігрує холодні сторінки\nпрямо в CXL RAM (без участі диска та swap)", size=12, fill=WARM, stroke=POS, sw=1.6, color=INK))
    p.append(arrow(310, 320, 310, 360, color=POS, sw=2.2))
    p.append(arrow(400, 440, 750, 440, color=POS, sw=2.2))
    p.append(arrow(750, 440, 750, 320, color=POS, sw=2.2))

    # 2. Promotion: зі Slow-tier угору в Top-tier
    p.append(fitbox(660, 465, 460, 80, "Підвищення (Page Promotion):\nAutoNUMA balancing виявляє часті звернення до CXL ->\nмігрує сторінку назад у швидку DRAM", size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))
    p.append(arrow(890, 320, 890, 465, color=FIELD, sw=2.2))
    p.append(arrow(800, 545, 200, 545, color=FIELD, sw=2.2))
    p.append(arrow(200, 545, 200, 320, color=FIELD, sw=2.2))

    # Нижній рівень: Swap / Disk (який уникається)
    p.append(rect(50, 585, 1100, 85, fill=PALE, stroke=LINE, sw=1.5, rx=8))
    p.append(text(75, 615, "Традиційний Swap на NVMe / SSD (Затримка: 10-100 мкс — у 100-500 разів повільніше за CXL):", size=13, color=INK, anchor="start", bold=True))
    p.append(text(75, 645, "Memory Tiering тримає робочий набір на 100% у фізичній RAM. Скидання на диск активується лише тоді, коли переповнено і DRAM, і CXL-вузли.", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "tiering-architecture.svg"), W, H, *p,
           title="Дворівнева архітектура пам'яті Linux")


# ── 2. memory_tiers та абстрактні дистанції ────────────────────────────────
def fig_memory_tier_abstract_distance():
    W, H = 1200, 680
    p = []

    p.append(text(60, 36, "Ієрархія memory_tiers та обчислення абстрактних дистанцій (adist)",
                  size=16, color=INK, anchor="start", bold=True))

    # Блок 1: Джерела апаратних метрик
    p.append(fitbox(50, 80, 320, 160, "Апаратна інформація про пам'ять\n\n• ACPI HMAT (Heterogeneous Memory)\n• CXL CDAT (Coherent Device Attributes)\n• Таблиці затримок і пропускної здатності", size=12, fill=PALE, stroke=LINE, sw=1.5, color=INK))

    p.append(arrow(370, 160, 430, 160, color=LINE, sw=2))

    # Блок 2: Драйвери та обчислення adist
    p.append(fitbox(430, 80, 340, 160, "Драйвери & Калькулятори adist\n\n• drivers/acpi/numa/hmat.c\n• drivers/cxl/core/cdat.c\n• mt_calc_adistance_node()\nОбчислення нормалізованої дистанції", size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    p.append(arrow(770, 160, 830, 160, color=NEG, sw=2))

    # Блок 3: Ядро mm/memory-tiers.c
    p.append(fitbox(830, 80, 320, 160, "Ядерна підсистема memory-tiers\n\n• mm/memory-tiers.c\n• Базовий DRAM adist = 512\n• Розбиття на кошики (chunk = 128)\n• Створення списків demotion targets", size=12, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))

    # Стрілка вниз до sysfs представлення
    p.append(arrow(990, 240, 990, 300, color=FIELD, sw=2))

    # Блок 4: Sysfs структура
    p.append(rect(50, 300, 1100, 350, fill="none", stroke=LINE, sw=1.6, rx=10))
    p.append(text(80, 335, "Відображення у просторі користувача: /sys/devices/system/node/memory_tiers/", size=14, color=INK, anchor="start", bold=True))

    # Ярус 0 (DRAM)
    p.append(fitbox(80, 360, 490, 120, "memory_tier0 (Швидкий ярус, adist: 512)\n\n• nodes: 0-1 (Локальні вузли процесорів)\n• max_tier: вказує на найвищий ярус системи\n• Demotion target -> memory_tier1", size=12, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))

    # Стрілка demotion між ярусами в sysfs
    p.append(arrow(570, 420, 650, 420, color=POS, sw=2.2))
    p.append(text(610, 405, "Demotion", size=11, color=POS, bold=True))

    # Ярус 1 (CXL)
    p.append(fitbox(650, 360, 470, 120, "memory_tier1 (Повільний ярус, adist: 640)\n\n• nodes: 2-3 (CXL memory expanders)\n• Вузли без CPU (CPU-less memory nodes)\n• Demotion target -> порожній (або swap)", size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    # Таблиця цілей витіснення
    p.append(fitbox(80, 505, 1040, 125, "Внутрішній масив ядра: node_demotion_targets[N]\n• Вузол 0 (DRAM) -> ціль витіснення Вузол 2 (найближчий CXL-вузол)\n• Вузол 1 (DRAM) -> ціль витіснення Вузол 3 (найближчий CXL-вузол)\n• Вузол 2/3 (CXL) -> цілей витіснення у пам'ять немає; наступний крок — вивантаження у swap", size=12, fill=PALE, stroke=LINE, sw=1.2, color=INK))

    render(os.path.join(OUT, "memory-tier-abstract-distance.svg"), W, H, *p,
           title="Ієрархія memory_tiers та абстрактні дистанції")


# ── 3. Повний життєвий цикл сторінки ───────────────────────────────────────
def fig_promotion_demotion_lifecycle():
    W, H = 1200, 700
    p = []

    p.append(text(60, 36, "Життєвий цикл сторінки: Аллокація, Demotion, AutoNUMA та Promotion",
                  size=16, color=INK, anchor="start", bold=True))

    # Крок 1: Первинна аллокація
    p.append(fitbox(50, 80, 240, 100, "1. Первинна аллокація\nalloc_pages(GFP_HIGHUSER)\nВиділення у швидкому\nTop-tier DRAM (Вузол 0)", size=12, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))

    p.append(arrow(290, 130, 350, 130, color=LINE, sw=2))

    # Крок 2: Охолодження на LRU
    p.append(fitbox(350, 80, 240, 100, "2. Охолодження сторінки\nActive LRU -> Inactive LRU\nДоступів немає,\nбіт Referenced скинуто", size=12, fill=PALE, stroke=MUTED, sw=1.5, color=INK))

    p.append(arrow(590, 130, 650, 130, color=LINE, sw=2))

    # Крок 3: Асинхронний спуск (Demotion)
    p.append(fitbox(650, 80, 240, 100, "3. Витіснення kswapd\nПам'ять DRAM < WMARK_LOW\nshrink_folio_list()\n-> demote_page_list()", size=12, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(arrow(890, 130, 950, 130, color=POS, sw=2.2))

    # Крок 4: Міграція в Slow-tier
    p.append(fitbox(950, 80, 200, 100, "4. Запис у CXL RAM\nКопіювання RAM-to-RAM,\nоновлення PTE на Вузол 2,\nзвільнення DRAM", size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    # Стрілка вниз до періоду сну та сканування
    p.append(arrow(1050, 180, 1050, 270, color=LINE, sw=2))

    # Крок 5: AutoNUMA сканування
    p.append(fitbox(800, 270, 350, 110, "5. Періодичне сканування AutoNUMA\ntask_numa_work() знаходить сторінку в CXL\nскидає PTE прапорець Present і ставить _PAGE_NUMA (PROT_NONE)", size=12, fill=SOFT, stroke=LINE, sw=1.5, color=INK))

    p.append(arrow(800, 325, 720, 325, color=LINE, sw=2))

    # Крок 6: Доступ процесора та NUMA Hint Fault
    p.append(fitbox(410, 270, 310, 110, "6. Повторний доступ (Trap)\nCPU звертається до сторінки ->\nMinor Fault -> do_numa_page()\nРеєстрація звернення з CPU0 до Node2", size=12, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(arrow(410, 325, 330, 325, color=POS, sw=2))

    # Крок 7: Рішення про підвищення (Promotion)
    p.append(fitbox(50, 270, 280, 110, "7. Оцінка гарячості\nshould_numa_migrate_memory()\nПеревірка лімітів швидкості\n(rate_limit_mbps) та ярусу", size=12, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    # Стрілка вниз до кроку міграції вгору
    p.append(arrow(190, 380, 190, 460, color=FIELD, sw=2.2))

    # Крок 8: Promotion у Top-tier
    p.append(fitbox(50, 460, 1100, 200, "8. Фінальне підвищення (Page Promotion): міграція назад у швидку DRAM\n\n• migrate_pages() виділяє нову сторінку на Node 0 (Top-tier DRAM)\n• Вміст копіюється з CXL-пам'яті у локальну DRAM (copy_highpage)\n• Таблиці сторінок (PTE) процесу атомарно перемикаються на новий PFN у DRAM\n• Відновлюються права доступу (PTE Present), сторінка знову читається/пишеться на швидкості 60-80 ns", size=13, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    render(os.path.join(OUT, "promotion-demotion-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл сторінки у системі з дворівневою пам'яттю")


if __name__ == "__main__":
    fig_tiering_architecture()
    fig_memory_tier_abstract_distance()
    fig_promotion_demotion_lifecycle()
