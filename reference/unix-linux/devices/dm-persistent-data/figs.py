# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GRAY_FILL = "#eef1f4"
PURPLE_FILL = "#f3e8fd"
PURPLE = "#7b1fa2"
WARM = "#b8860b"


# ── 1. Багаторівнева архітектура persistent-data ─────────────────────────────
def fig_architecture_stack():
    W, H = 1380, 840
    p = []

    p.append(text(60, 48, "Архітектурний стек dm-persistent-data: від цілей ядра до фізичних 4 КіБ блоків",
                  size=16, anchor="start", bold=True))

    # Рівень 1: Клієнтські цілі Device Mapper
    p.append(rect(60, 75, 1260, 95, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=8))
    p.append(text(80, 102, "КЛІЄНТСЬКІ ЦІЛІ DEVICE MAPPER (drivers/md/)", size=13, anchor="start", bold=True, color=WARM))
    targets = [
        (100, "dm-thin\nтонкі пули та знімки"),
        (400, "dm-cache\nкешування SSD/NVMe"),
        (700, "dm-era\nвідстеження змін блоків"),
        (1000, "dm-clone\nфонове клонування томів")
    ]
    for x0, label in targets:
        p.append(fitbox(x0, 115, 260, 44, label, size=12, bold=True, fill=BG, stroke=WARM, sw=1.4))

    p.append(arrow(690, 170, 690, 205, color=LINE, sw=2))

    # Рівень 2: Структури даних (B-дерева та карти простору)
    p.append(rect(60, 205, 1260, 150, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(80, 232, "СТРУКТУРИ ДАНИХ (drivers/md/persistent-data/)", size=13, anchor="start", bold=True, color=NEG))
    
    p.append(fitbox(100, 248, 380, 90, "dm-btree (B+ дерева з CoW-тінюванням)\n"
                                        "• 1D/2D ключі (dev_id, logical_block)\n"
                                        "• вузли фіксованого розміру 4 КіБ\n"
                                        "• підтримка знімків і розгалужень",
                    size=12, fill=BG, stroke=NEG, sw=1.4))
    
    p.append(fitbox(520, 248, 370, 90, "dm-space-map-disk (пул даних)\n"
                                        "• бітові карти виділення блоків даних\n"
                                        "• 32-бітні лічильники посилань (refcounts)\n"
                                        "• індексні блоки великого адресного простору",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    p.append(fitbox(920, 248, 380, 90, "dm-space-map-metadata (метадані)\n"
                                        "• облік самих 4 КіБ блоків метаданих\n"
                                        "• розв'язання рекурсії виділення блоків\n"
                                        "• внутрішнє бітове тінювання в пам'яті",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    p.append(arrow(690, 355, 690, 390, color=LINE, sw=2))

    # Рівень 3: Менеджер транзакцій
    p.append(rect(60, 390, 1260, 130, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(80, 417, "ТРАНЗАКЦІЙНИЙ МЕНЕДЖЕР (dm_transaction_manager)", size=13, anchor="start", bold=True, color=FIELD))
    p.append(fitbox(100, 432, 1180, 72, "Координація тіньового копіювання блоків (shadowing) та двофазної фіксації (two-phase commit)\n"
                                         "• dm_tm_shadow_block(): виділяє новий блок при зміні вузла, старий лишається незмінним\n"
                                         "• dm_tm_commit(): скидає брудні буфери, фіксує space map і готує оновлений суперблок\n"
                                         "• Лічильник поколінь транзакцій (generation / transaction ID) для виявлення збоїв",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))

    p.append(arrow(690, 520, 690, 555, color=LINE, sw=2))

    # Рівень 4: Менеджер блоків
    p.append(rect(60, 555, 1260, 140, fill=PURPLE_FILL, stroke=PURPLE, sw=1.8, rx=8))
    p.append(text(80, 582, "МЕНЕДЖЕР БЛОКІВ (dm_block_manager)", size=13, anchor="start", bold=True, color=PURPLE))
    p.append(fitbox(100, 597, 570, 82, "Кеш 4 КіБ буферів і блокування:\n"
                                        "• dm_bm_read_lock() / dm_bm_write_lock_zero()\n"
                                        "• Посторінковий хеш-кеш у RAM\n"
                                        "• Відстеження dirty-буферів для запису",
                    size=12, fill=BG, stroke=PURPLE, sw=1.4))
    p.append(fitbox(700, 597, 580, 82, "Валідація, контрольні суми та скидання I/O:\n"
                                        "• struct dm_block_validator (CRC32c перевірка)\n"
                                        "• Автоматичний розрахунок CRC перед записом на диск\n"
                                        "• dm_bm_flush(): бар'єр скидання з кешів носія",
                    size=12, fill=BG, stroke=PURPLE, sw=1.4))

    p.append(arrow(690, 695, 690, 730, color=LINE, sw=2))

    # Рівень 5: Фізичний пристрій
    p.append(rect(60, 730, 1260, 80, fill=GRAY_FILL, stroke=INK, sw=1.8, rx=8))
    p.append(fitbox(100, 742, 1180, 56, "ФІЗИЧНИЙ АБО ЛОГІЧНИЙ ПРИСТРІЙ МЕТАДАНИХ (raw block device /dev/sdX1, NVMe)\n"
                                         "Блок 0: Суперблок (версія, UUID, transaction_id, корені B-дерев та карт простору, CRC32c)\n"
                                         "Блоки 1..N: Вузли B-дерев, індексні блоки карт простору, бітові карти (розмір блоку строго 4 КіБ)",
                    size=12, fill=BG, stroke=INK, sw=1.4))

    render(os.path.join(IMG, "architecture-stack.svg"), W, H, *p)


# ── 2. Copy-on-Write (тінювання) B-дерев ──────────────────────────────────────
def fig_btree_shadow_cow():
    W, H = 1380, 800
    p = []

    p.append(text(60, 48, "Тінювання (shadowing) B-дерева: модифікація листка без перезапису старих блоків",
                  size=16, anchor="start", bold=True))

    # Ліва частина: Стан До модифікації (Транзакція N)
    p.append(rect(60, 80, 600, 610, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(360, 110, "СТАН ДО ЗМІНИ (Транзакція N, активний Корінь R1)", size=13, anchor="middle", bold=True, color=NEG))

    p.append(fitbox(260, 135, 200, 55, "Корінь R1\n[блок 12, ref=1]", size=12, bold=True, fill=BG, stroke=NEG, sw=1.6))
    
    p.append(arrow(310, 190, 200, 270, color=NEG, sw=1.6))
    p.append(arrow(410, 190, 520, 270, color=NEG, sw=1.6))

    p.append(fitbox(100, 270, 200, 55, "Вузол A1\n[блок 34, ref=1]", size=12, bold=True, fill=BG, stroke=NEG, sw=1.4))
    p.append(fitbox(420, 270, 200, 55, "Вузол B1\n[блок 58, ref=1]", size=12, bold=True, fill=BG, stroke=NEG, sw=1.4))

    p.append(arrow(150, 325, 120, 400, color=NEG, sw=1.4))
    p.append(arrow(250, 325, 280, 400, color=NEG, sw=1.4))
    p.append(arrow(470, 325, 440, 400, color=NEG, sw=1.4))
    p.append(arrow(570, 325, 590, 400, color=NEG, sw=1.4))

    p.append(fitbox(70, 400, 130, 60, "Листок L1\n[блок 71]", size=11, fill=BG, stroke=NEG, sw=1.2))
    p.append(fitbox(220, 400, 130, 60, "Листок L2\n[блок 72]", size=11, fill=BG, stroke=NEG, sw=1.2))
    p.append(fitbox(380, 400, 130, 60, "Листок L3\n[блок 85]", size=11, fill=BG, stroke=NEG, sw=1.2))
    p.append(fitbox(530, 400, 120, 60, "Листок L4\n[блок 89]", size=11, fill=RED_FILL, stroke=POS, sw=1.6, bold=True))

    p.append(fitbox(80, 500, 560, 165, "Ціль: оновити відображення у листку L4.\n"
                                       "• Замість перезапису блока 89 виділяється новий вільний блок 104\n"
                                       "• Вузол B1 мусить отримати нову адресу листка → копіюється у блок 105 (B2)\n"
                                       "• Корінь R1 мусить отримати адресу B2 → копіюється у блок 106 (R2)\n"
                                       "• Усі старі блоки (12, 58, 89) залишаються недоторканими на диску!",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    # Права частина: Стан Після створення тіньової копії (Транзакція N+1 в польоті)
    p.append(rect(720, 80, 600, 610, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(1020, 110, "СТАН ПІСЛЯ ТІНЮВАННЯ (Підготовка транзакції N+1)", size=13, anchor="middle", bold=True, color=FIELD))

    p.append(fitbox(920, 135, 200, 55, "Новий Корінь R2\n[блок 106, ТІНЬ]", size=12, bold=True, fill=WARM_FILL, stroke=POS, sw=1.8))

    p.append(arrow(970, 190, 860, 270, color=MUTED, sw=1.4))
    p.append(arrow(1070, 190, 1180, 270, color=POS, sw=1.8))

    p.append(fitbox(760, 270, 200, 55, "Старий Вузол A1\n[блок 34, СПІЛЬНИЙ]", size=12, fill=BG, stroke=MUTED, sw=1.4))
    p.append(fitbox(1080, 270, 200, 55, "Новий Вузол B2\n[блок 105, ТІНЬ]", size=12, bold=True, fill=WARM_FILL, stroke=POS, sw=1.8))

    p.append(arrow(810, 325, 780, 400, color=MUTED, sw=1.2))
    p.append(arrow(910, 325, 930, 400, color=MUTED, sw=1.2))
    p.append(arrow(1130, 325, 1100, 400, color=MUTED, sw=1.2))
    p.append(arrow(1230, 325, 1250, 400, color=POS, sw=1.8))

    p.append(fitbox(730, 400, 120, 60, "Листок L1\n[блок 71]", size=11, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(870, 400, 120, 60, "Листок L2\n[блок 72]", size=11, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(1040, 400, 120, 60, "Листок L3\n[блок 85]", size=11, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(1190, 400, 120, 60, "Новий L4'\n[блок 104, ТІНЬ]", size=11, fill=WARM_FILL, stroke=POS, sw=1.8, bold=True))

    p.append(fitbox(740, 500, 560, 165, "Підсумок тіньового переписування (Copy-on-Write):\n"
                                         "• Гілка A1 (блоки 34, 71, 72) не змінювалась і розділяється між деревами\n"
                                         "• Листок L3 (блок 85) не змінювався і перевикористовується новим B2\n"
                                         "• До миті запису Суперблоку диск адресує R1; аварія поверне стан R1\n"
                                         "• Після запису Суперблоку активним стає R2, а блоки 12, 58, 89 звільняються",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))

    # Нижній висновок
    p.append(fitbox(60, 710, 1260, 65,
                    "Інваріант стійкості: жоден блок, на який посилається зафіксований на диску суперблок, "
                    "ніколи не змінюється на місці. Будь-яка зміна породжує нову гілку, роблячи дерево самодостатнім і стійким до аварій.",
                    size=13, fill=GRAY_FILL, stroke=INK, sw=1.6))

    render(os.path.join(IMG, "btree-shadow-cow.svg"), W, H, *p)


# ── 3. Двофазна фіксація та стійкість без журналу ────────────────────────────
def fig_two_phase_commit():
    W, H = 1380, 840
    p = []

    p.append(text(60, 48, "Двофазний протокол фіксації (dm_tm_commit): як гарантується атомарність без журналу",
                  size=16, anchor="start", bold=True))

    steps = [
        (60, "Фаза 1: Скидання тіньових метаданих", NEG, BLUE_FILL,
         ["1. Завершення мутацій у RAM",
          "2. dm_sm_commit(sm_metadata)",
          "3. dm_sm_commit(sm_disk)",
          "4. dm_bm_flush(bm)",
          "Змінені 4 КіБ блоки та space map\nзаписуються у вільні блоки носія"],
         "Якщо живлення зникне тут:\n"
         "Суперблок ще вказує на корінь R1.\n"
         "Записані нові блоки вважаються сміттям\n"
         "і безпечно ігноруються. Нуль пошкоджень."),

        (490, "Бар'єр I/O та синхронізація", POS, RED_FILL,
         ["1. Очікування завершення I/O",
          "2. REQ_PREFLUSH на диск",
          "3. Гарантія, що блоки фізично\n   записані на енергонезалежний носій",
          "4. Підготовка блоку 0 (Суперблок)\n   із новим transaction_id = N+1",
          "Розрахунок CRC32c для Суперблоку"],
         "Апаратний бар'єр кешу:\n"
         "Контролер диска не має права\n"
         "переставити запис Суперблоку\n"
         "перед записом самих блоків дерева!"),

        (920, "Фаза 2: Атомарна зміна суперблоку", FIELD, GREEN_FILL,
         ["1. Запис Суперблоку в блок 0",
          "2. REQ_FUA (Force Unit Access)",
          "3. Оновлення кореня на R2",
          "4. Інкремент transaction_id",
          "5. Звільнення старих блоків\n   у space map для наступних дій"],
         "Якщо живлення зникне тут:\n"
         "Після завершення FUA новий суперблок на диску.\n"
         "При завантаженні ядро відкриє стан R2.\n"
         "Транзакція повністю успішна."),
    ]

    for x0, title, col, fil, items, note in steps:
        p.append(fitbox(x0, 80, 400, 52, title, size=13, bold=True, fill=fil, stroke=col, sw=1.8))
        for i, it in enumerate(items):
            p.append(fitbox(x0, 148 + i * 66, 400, 56, it, size=12, fill=BG, stroke=col, sw=1.3))
        p.append(fitbox(x0, 500, 400, 130, note, size=12, fill=fil, stroke=col, sw=1.6))

    # Схема аварійного перемикача
    p.append(rect(60, 650, 1260, 155, fill=GRAY_FILL, stroke=INK, sw=1.8, rx=8))
    p.append(text(80, 678, "ТОЧКА АТОМАРНОГО ПЕРЕХОДУ (BARRIER / SUPERBLOCK FLUSH)", size=13, anchor="start", bold=True, color=INK))
    p.append(fitbox(80, 695, 590, 95, "ДО ЗАПИСУ БЛОКУ 0:\n"
                                      "• transaction_id = N, корінь = R1, valid CRC32c\n"
                                      "• Будь-який збій → відкат до консистентного стану N\n"
                                      "• Непотрібні shadow-блоки безпечно ігноруються",
                    size=12, fill=BG, stroke=NEG, sw=1.5))

    p.append(fitbox(710, 695, 590, 95, "ПІСЛЯ ЗАПИСУ БЛОКУ 0 (FUA OK):\n"
                                       "• transaction_id = N+1, корінь = R2, valid CRC32c\n"
                                       "• Будь-який збій → старт із консистентного стану N+1\n"
                                       "• Транзакція зафіксована на 100% без жодного журналу / WAL",
                    size=12, fill=BG, stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "two-phase-commit.svg"), W, H, *p)


# ── 4. Карти простору: sm-disk та sm-metadata ────────────────────────────────
def fig_space_map_hierarchy():
    W, H = 1380, 820
    p = []

    p.append(text(60, 48, "Архітектура Space Map: облік виділення блоків даних (sm-disk) та метаданих (sm-metadata)",
                  size=16, anchor="start", bold=True))

    # Ліва колонка: sm-disk
    p.append(rect(60, 80, 600, 600, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(360, 110, "sm-disk (КАРТА ПРОСТОРУ БЛОКІВ ДАНИХ)", size=13, anchor="middle", bold=True, color=NEG))

    p.append(fitbox(90, 135, 540, 70, "Призначення: облік великих блоків пулу даних (64 КіБ – 1 ГіБ)\n"
                                      "• Масштаб: мільйони блоків даних (до багатьох ТіБ / ПіБ)\n"
                                      "• Зберігає 32-бітний refcount для кожного блоку даних",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    p.append(fitbox(90, 225, 540, 100, "Дворівнева ієрархія зберігання на диску:\n"
                                       "1. Індексні блоки (index blocks): масив адрес бітових блоків\n"
                                       "2. Блоки бітових карт (bitmap blocks): 2 біти на блок для малих refcount\n"
                                       "   • 00 = вільний, 01 = ref 1, 10 = ref 2, 11 = переповнення (ref ≥ 3)",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    p.append(fitbox(90, 345, 540, 85, "Дерево переповнення (overflow B-tree):\n"
                                      "• Якщо refcount блоку досягає 3+, точне 32-бітне значення\n"
                                      "  зберігається у вторинному B-дереві переповнень\n"
                                      "• Економить 95%+ місця метаданих при відсутності знімків",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    p.append(fitbox(90, 450, 540, 210, "Операції sm-disk:\n"
                                       "• dm_sm_inc_block() — інкремент refcount при створенні знімка або клону\n"
                                       "• dm_sm_dec_block() — декремент refcount при видаленні або discard/trim\n"
                                       "• dm_sm_new_block() — пошук першого вільного біта (ref=0) та його маркування\n"
                                       "• dm_sm_commit() — скидання змінених бітових блоків через транзакційний менеджер",
                    size=12, fill=BG, stroke=NEG, sw=1.4))

    # Права колонка: sm-metadata
    p.append(rect(720, 80, 600, 600, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(1020, 110, "sm-metadata (КАРТА БЛОКІВ МЕТАДАНИХ)", size=13, anchor="middle", bold=True, color=FIELD))

    p.append(fitbox(750, 135, 540, 70, "Призначення: облік самих 4 КіБ блоків метаданих (до 16 ГіБ)\n"
                                       "• Відстежує, які 4 КіБ блоки пристрою метаданих зайняті\n"
                                       "• Refcount для метаданих завжди 1 (або 0 після звільнення)",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))

    p.append(fitbox(750, 225, 540, 100, "Проблема курячого яйця (рекурсія виділення):\n"
                                       "Щоб записати, які блоки метаданих зайнято, треба виділити\n"
                                       "новий блок метаданих для карти простору! Як не зациклитися?\n"
                                       "Розв'язання: In-memory тіньова бітова карта + двофазне фіксування.",
                    size=12, fill=BG, stroke=POS, sw=1.6, bold=True))

    p.append(fitbox(750, 345, 540, 85, "Два стани виділення в пам'яті:\n"
                                       "• Committed bitmap — стан блоків, зафіксований на диску\n"
                                       "• Uncommitted bitmap — блоки, виділені під час поточної транзакції\n"
                                       "  (нові вузли B-дерев, нові блоки індексів sm-disk)",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))

    p.append(fitbox(750, 450, 540, 210, "Фаза фіксації sm-metadata:\n"
                                       "1. Заморожуються всі нові виділення блоків\n"
                                       "2. Структура sm-metadata записує свій стан у зарезервовані блоки\n"
                                       "3. Блоки самого sm-metadata не змінюються рекурсивно\n"
                                       "4. Uncommitted переноситься в committed після успіху суперблоку",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))

    # Нижній висновок
    p.append(fitbox(60, 700, 1260, 95,
                    "Розділення обов'язків: sm-disk оптимізовано під величезні обсяги та часті спільні посилання (refcount > 1 при знімках тонкими томами), "
                    "тоді як sm-metadata оптимізовано під швидкість роботи в оперативній пам'яті та строге розв'язання рекурсії дискових виділень.",
                    size=13, fill=GRAY_FILL, stroke=INK, sw=1.6))

    render(os.path.join(IMG, "space-map-hierarchy.svg"), W, H, *p)


if __name__ == '__main__':
    fig_architecture_stack()
    fig_btree_shadow_cow()
    fig_two_phase_commit()
    fig_space_map_hierarchy()
    print("All figures generated successfully.")
