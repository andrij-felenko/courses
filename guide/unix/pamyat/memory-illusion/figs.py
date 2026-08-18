# -*- coding: utf-8 -*-
"""Фігури до теми «Ілюзія власної пам'яті: на чому вона тримається» (guide/unix/pamyat)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT   = "#f2f6fd"
GREENBG = "#eafaf0"
REDBG   = "#fdeeec"
GREYBG  = "#f8f9fa"
YELLOWBG = "#fef9e7"


# ── 1. Чотири колони ілюзії ──────────────────────────────────────────────────
def fig_illusion_architecture():
    W, H = 1040, 680
    frags = []

    # Заголовок зверху
    frags.append(text(W / 2, 38, "Чотири колони ілюзії віртуальної пам'яті", size=20, bold=True))

    col_w = 220
    col_gap = 26
    start_x = 36
    top_y = 75
    card_h = 560

    columns = [
        ("1. Простір і ділянки\n(Ядро: mm_struct, VMA)",
         "Карта намірів процесу",
         [
             ("Стек (r/w)", "#eef4fb"),
             ("mmap / бібліотеки (r-x, r--)", "#eef4fb"),
             ("Купа / brk (r/w)", "#eef4fb"),
             ("Сегменти ELF (код r-x, дані r/w)", "#eef4fb"),
             ("Дірки між ділянками\n(неіснуюча пам'ять)", REDBG),
         ],
         "Описує, що процесові\nДОЗВОЛЕНО робити.\nПам'яті під ділянки може\nще не бути взагалі.",
         "#2b5c92"),

        ("2. Багаторівнева таблиця\n(Дерево PGD..PTE)",
         "Розріджений перекладач",
         [
             ("CR3 (корінь у DRAM)", YELLOWBG),
             ("PGD (512 записів)", SOFT),
             ("PUD (512 записів)", SOFT),
             ("PMD (512 записів)", SOFT),
             ("PTE (номер кадру + біти P/W/U)", GREENBG),
         ],
         "Перекладає віртуальну\nсторінку у фізичний кадр.\nПорожні гілки дерева\nне займають RAM.",
         "#8d6b14"),

        ("3. Апаратний MMU + TLB\n(Процесор: Fast Path)",
         "Миттєвий виконавець",
         [
             ("L1 / L2 TLB кеш\n(трансляція за 1 такт)", GREENBG),
             ("MMU Page Walker\n(апаратний обхід дерева)", SOFT),
             ("Контроль прав\n(User/Supervisor, W, NX)", SOFT),
             ("Виняток #PF (Vector 14)\n(якщо P=0 або порушення)", REDBG),
         ],
         "Виконує переклад апаратно\nна кожному зверненні.\nНа TLB Hit не чіпає\nшину пам'яті.",
         "#1b7a42"),

        ("4. Фізичні кадри\n(DRAM: 4 КіБ рамки)",
         "Справжнє сховище",
         [
             ("Кадр А (анонімні дані)", "#f0f4ea"),
             ("Кадр Б (спільний код libc)", GREENBG),
             ("Кадр В (кеш файлу / disk)", SOFT),
             ("Кадр Г (zeroed page / COW)", YELLOWBG),
             ("Вільні кадри (Buddy Allocator)", GREYBG),
         ],
         "Фізичні мікросхеми DRAM\nпорізані на кадри 4 КіБ.\nСусідні віртуальні сторінки\nрозкидані хаотично.",
         "#4a5568"),
    ]

    for i, (title, subtitle, blocks, desc, border_col) in enumerate(columns):
        cx = start_x + i * (col_w + col_gap)

        # Фонова картка колонки
        frags.append(rect(cx, top_y, col_w, card_h, fill="#ffffff", stroke=border_col, sw=1.6, rx=8))

        # Заголовок колонки
        frags.append(fitbox(cx + 8, top_y + 10, col_w - 16, 52, title, size=13, bold=True, fill=border_col, color="#ffffff", rx=6))
        frags.append(text(cx + col_w / 2, top_y + 76, subtitle, size=12, italic=True, color="#555555"))

        # Блоки всередині
        by = top_y + 96
        for btext, bfill in blocks:
            bh = 46 if "\n" in btext else 38
            frags.append(fitbox(cx + 12, by, col_w - 24, bh, btext, size=12, fill=bfill, stroke="#ccd4dc", sw=1.0, rx=4))
            by += bh + 8

        # Опис унизу колонки
        desc_h = 100
        frags.append(fitbox(cx + 8, top_y + card_h - desc_h - 10, col_w - 16, desc_h, desc, size=11, fill="#f4f6f8", stroke="#d0d6dc", sw=0.8, color="#333333", rx=4))

        # Горизонтальні стрілки між колонками
        if i < 3:
            arrow_x0 = cx + col_w
            arrow_x1 = arrow_x0 + col_gap
            frags.append(arrow(arrow_x0 + 2, top_y + 240, arrow_x1 - 2, top_y + 240, color="#6b7280", sw=2.0))

    render(os.path.join(OUT, 'illusion-architecture.svg'), W, H, *frags,
           title="Чотири колони ілюзії віртуальної пам'яті")


# ── 2. Повний цикл виконання інструкції ──────────────────────────────────────
def fig_end_to_end_fault():
    W, H = 1080, 840
    frags = []

    frags.append(text(W / 2, 34, "Повний шлях однієї інструкції: від CPU до пам'яті через збій", size=20, bold=True))

    # Схема з двох світів: Зліва Апаратура / Fast Path, Справа Ядро / Slow Path
    mid_x = 540

    frags.append(rect(30, 60, 490, 750, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    frags.append(fitbox(45, 72, 460, 36, "Апаратний рівень (CPU / MMU / TLB) — наносекунди", size=14, bold=True, fill="#e2e8f0", color="#1e293b", rx=4))

    frags.append(rect(560, 60, 490, 750, fill="#fefdf8", stroke="#d97706", sw=1.2, rx=8))
    frags.append(fitbox(575, 72, 460, 36, "Простір ядра (Обробник #PF) — мікросекунди / мілісекунди", size=14, bold=True, fill="#fef3c7", color="#92400e", rx=4))

    # Ліва колонка (Апаратура)
    frags.append(fitbox(60, 125, 430, 48, "1. Інструкція звертається за адресою:\nmov [0x7f9a1000], 0x42", size=13, bold=True, fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(arrow(275, 173, 275, 200, color="#475569", sw=1.8))

    frags.append(fitbox(60, 200, 430, 52, "2. Пошук у кеші трансляцій (TLB):\nчи є готова пара VA → PA?", size=13, fill=SOFT, stroke="#93c5fd", rx=6))

    # Гілка TLB Hit
    frags.append(arrow(100, 252, 100, 715, color="#16a34a", sw=1.8))
    frags.append(text(108, 480, "TLB Hit (99%+ випадків)\nМиттєвий доступ до DRAM", size=11, color="#16a34a", bold=True, anchor="start"))

    # Гілка TLB Miss
    frags.append(arrow(340, 252, 340, 290, color="#475569", sw=1.8))
    frags.append(text(348, 272, "TLB Miss", size=11, color="#64748b", anchor="start"))

    frags.append(fitbox(180, 290, 310, 58, "3. MMU Page Table Walker:\nобхід CR3 → PGD → P4D → PUD → PMD → PTE", size=12, fill=SOFT, stroke="#93c5fd", rx=6))
    frags.append(arrow(335, 348, 335, 385, color="#475569", sw=1.8))

    frags.append(fitbox(180, 385, 310, 56, "4. Перевірка бітів PTE:\nP = 0 (відсутня) або W = 0 (заборона)", size=12, fill=REDBG, stroke="#fca5a5", rx=6))

    # Стрілка переходу в ядро (Виняток #PF)
    frags.append(arrow(490, 413, 590, 413, color="#dc2626", sw=2.2))
    frags.append(text(540, 400, "Виняток #PF\n(Вектор 14)", size=11, bold=True, color="#dc2626"))

    # Права колонка (Ядро)
    frags.append(fitbox(590, 130, 430, 56, "5. Регістри винятку в ядрі:\nCR2 = 0x7f9a1000 (адреса збою), error_code", size=12, bold=True, fill="#fffbeb", stroke="#fde68a", rx=6))
    frags.append(arrow(805, 186, 805, 215, color="#d97706", sw=1.8))

    frags.append(fitbox(590, 215, 430, 54, "6. Пошук VMA (mm_struct):\nчи законна ця адреса і тип доступу?", size=12, fill="#ffffff", stroke="#fcd34d", rx=6))

    # Розгалуження в ядрі: помилка чи відновлення
    frags.append(arrow(805, 269, 805, 305, color="#d97706", sw=1.8))

    frags.append(fitbox(590, 305, 430, 72, "7. Тип збою й виділення пам'яті:\n• Demand zero: виділити чистий 4 КіБ кадр\n• COW: продублювати кадр / зробити приватним\n• Major: черга вводу-виводу (диск / swap)", size=12, fill=YELLOWBG, stroke="#f59e0b", rx=6))
    frags.append(arrow(805, 377, 805, 415, color="#d97706", sw=1.8))

    frags.append(fitbox(590, 415, 430, 60, "8. Оновлення запису таблиці сторінок:\nPTE = [Фізичний PFN | Present=1 | Writable=1]", size=12, fill=GREENBG, stroke="#86efac", rx=6))
    frags.append(arrow(805, 475, 805, 515, color="#16a34a", sw=1.8))

    frags.append(fitbox(590, 515, 430, 56, "9. Інвалідація старого кешу (invlpg) та\nповернення з переривання інструкцією iret", size=12, fill=GREENBG, stroke="#86efac", rx=6))

    # Стрілка повернення в CPU (Повтор інструкції)
    frags.append(arrow(590, 543, 390, 600, color="#16a34a", sw=2.2))
    frags.append(text(495, 565, "Повтор інструкції\n(Instruction Retry)", size=11, bold=True, color="#16a34a"))

    frags.append(fitbox(60, 600, 330, 65, "10. Процесор знову виконує:\nmov [0x7f9a1000], 0x42\nТепер PTE є чинним!", size=12, bold=True, fill=GREENBG, stroke="#86efac", rx=6))
    frags.append(arrow(225, 665, 225, 715, color="#16a34a", sw=1.8))

    # Фінал
    frags.append(fitbox(60, 715, 430, 56, "11. Запис значення 0x42 у фізичний кад DRAM.\nПрограма не помітила паузи в ядрі.", size=13, bold=True, fill="#ffffff", stroke="#22c55e", rx=6))

    render(os.path.join(OUT, 'end-to-end-fault-cycle.svg'), W, H, *frags,
           title="Повний шлях однієї інструкції крізь MMU, сторінковий збій і ядро")


# ── 3. Видача за вимогою і копіювання при записі ─────────────────────────────
def fig_cow_and_demand():
    W, H = 1040, 560
    frags = []

    frags.append(text(W / 2, 34, "Два механізми лінивої пам'яті: Demand Paging та Copy-on-Write", size=20, bold=True))

    pw = 470
    ph = 470
    p1_x = 35
    p2_x = 535
    top_y = 60

    # Панель 1: Demand Paging
    frags.append(rect(p1_x, top_y, pw, ph, fill="#ffffff", stroke="#2563eb", sw=1.4, rx=8))
    frags.append(fitbox(p1_x + 15, top_y + 12, pw - 30, 36, "1. Видача за вимогою (Demand Paging)", size=14, bold=True, fill="#eff6ff", color="#1e40af", rx=4))

    frags.append(fitbox(p1_x + 25, top_y + 60, pw - 50, 60, "Крок 1: mmap() або malloc()\nЯдро створює VMA (обіцянку на 1 ГіБ).\nФізичних кадрів виділено: 0 байтів!", size=12, fill=GREYBG, stroke="#cbd5e1", rx=4))
    frags.append(arrow(p1_x + pw / 2, top_y + 120, p1_x + pw / 2, top_y + 145, color="#64748b", sw=1.6))

    frags.append(fitbox(p1_x + 25, top_y + 145, pw - 50, 65, "Крок 2: Перший запис: ptr[0] = 10\nMMU бачить порожній PTE (P = 0) → #PF.\nЯдро бачить законний анонімний VMA.", size=12, fill=YELLOWBG, stroke="#fcd34d", rx=4))
    frags.append(arrow(p1_x + pw / 2, top_y + 210, p1_x + pw / 2, top_y + 235, color="#64748b", sw=1.6))

    frags.append(fitbox(p1_x + 25, top_y + 235, pw - 50, 75, "Крок 3: Ядро бере 1 вільний кадр (4 КіБ),\nзанулює його (zero-fill), записує PFN у PTE,\nставить біти Present=1, Writable=1.", size=12, fill=GREENBG, stroke="#86efac", rx=4))
    frags.append(arrow(p1_x + pw / 2, top_y + 310, p1_x + pw / 2, top_y + 335, color="#64748b", sw=1.6))

    frags.append(fitbox(p1_x + 25, top_y + 335, pw - 50, 110, "Результат:\n• Резидентна пам'ять (RSS) зросла рівно на 4 КіБ.\n• Решта 1048572 КіБ лишаються порожніми обіцянками.\n• Час реакції ядра: ~1–2 мікросекунди (Minor Fault).", size=12, fill="#f8fafc", stroke="#94a3b8", rx=4))

    # Панель 2: Copy-on-Write (COW)
    frags.append(rect(p2_x, top_y, pw, ph, fill="#ffffff", stroke="#059669", sw=1.4, rx=8))
    frags.append(fitbox(p2_x + 15, top_y + 12, pw - 30, 36, "2. Копіювання при записі (Copy-on-Write)", size=14, bold=True, fill="#ecfdf5", color="#065f46", rx=4))

    frags.append(fitbox(p2_x + 25, top_y + 60, pw - 50, 60, "Крок 1: fork() народжує процес-дитину\nТаблиці сторінок продубльовано,\nусі PTE батька й дитини помічено як Read-Only (W = 0).", size=12, fill=GREYBG, stroke="#cbd5e1", rx=4))
    frags.append(arrow(p2_x + pw / 2, top_y + 120, p2_x + pw / 2, top_y + 145, color="#64748b", sw=1.6))

    frags.append(fitbox(p2_x + 25, top_y + 145, pw - 50, 65, "Крок 2: Батько пише: data[42] = 99\nMMU ловить порушення захисту (W = 0) → #PF.\nЯдро бачить: VMA дозволяє запис (COW-пастка).", size=12, fill=YELLOWBG, stroke="#fcd34d", rx=4))
    frags.append(arrow(p2_x + pw / 2, top_y + 210, p2_x + pw / 2, top_y + 235, color="#64748b", sw=1.6))

    frags.append(fitbox(p2_x + 25, top_y + 235, pw - 50, 75, "Крок 3: do_wp_page():\n• Якщо власників > 1 → виділити новий кадр і скопіювати 4 КіБ\n• Якщо власник 1 → повернути W=1 без копіювання!", size=12, fill=GREENBG, stroke="#86efac", rx=4))
    frags.append(arrow(p2_x + pw / 2, top_y + 310, p2_x + pw / 2, top_y + 335, color="#64748b", sw=1.6))

    frags.append(fitbox(p2_x + 25, top_y + 335, pw - 50, 110, "Результат:\n• Батько й дитина мають роздільні дані без клонування гігабайтів.\n• Якщо дитина одразу робить execve(), копіювання = 0 байтів.\n• Збій є малим (minflt), без походу на диск.", size=12, fill="#f8fafc", stroke="#94a3b8", rx=4))

    render(os.path.join(OUT, 'cow-and-demand-paging.svg'), W, H, *frags,
           title="Порівняння Demand Paging та Copy-on-Write")


if __name__ == '__main__':
    fig_illusion_architecture()
    fig_end_to_end_fault()
    fig_cow_and_demand()
    print("All figures generated successfully.")
