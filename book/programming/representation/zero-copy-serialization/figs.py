# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F = "#eef4ff"
RED_F = "#fdecea"
GREEN_F = "#eaf7ef"
GREY_F = "#f4f6f8"
YELLOW_F = "#fef9e7"


# ── 1. deserialization-pipeline: класична проти нуль-копіювання ──────────────
def fig_deserialization_pipeline():
    W, H = 980, 560
    p = []

    # Верхній блок: Класичний підхід (JSON / Protobuf)
    y_top = 45
    p.append(rect(20, y_top, 940, 230, fill=BG, stroke=POS, sw=1.8, rx=8))
    p.append(text(35, y_top + 28, "Традиційна серіалізація (JSON, Protobuf, Thrift)", size=15, bold=True, color=POS, anchor="start"))
    p.append(text(35, y_top + 48, "перетворення байтів на дерево об'єктів у купі (Heap)", size=12, color=MUTED, anchor="start"))

    t_boxes = [
        (35, 120, 160, 75, "Вхідний потік\nбайтів\n(Socket / File)", GREY_F, LINE),
        (235, 120, 175, 75, "Парсер / Декодер\nvarint, рядки,\nтеги полів", RED_F, POS),
        (450, 120, 195, 75, "Алокації в купі\n`malloc()` / `new`\nдерево об'єктів", RED_F, POS),
        (685, 120, 255, 75, "Доступ до поля\nблукання по покажчиках\n(Pointer Chasing, Cache Miss)", RED_F, POS),
    ]
    for bx, by, bw, bh, blabel, bfill, bstroke in t_boxes:
        p.append(fitbox(bx, by, bw, bh, blabel, size=12, fill=bfill, stroke=bstroke, sw=1.5))

    p.append(arrow(195, 157, 235, 157, color=MUTED, sw=1.8))
    p.append(arrow(410, 157, 450, 157, color=MUTED, sw=1.8))
    p.append(arrow(645, 157, 685, 157, color=MUTED, sw=1.8))

    p.append(fitbox(35, 210, 910, 48,
                    "Накладні витрати: розбір кожного байта O(N) · сотні дрібних алокацій пам'яті · навантаження на Garbage Collector · кеш-промахи процесора",
                    size=12, fill=RED_F, stroke=POS, sw=1.2, color=POS))

    # Нижній блок: Нуль-копіювання (FlatBuffers / Cap'n Proto / SBE)
    y_bot = 295
    p.append(rect(20, y_bot, 940, 240, fill=BG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(35, y_bot + 28, "Формати без копіювання (Zero-Copy: FlatBuffers, Cap'n Proto, SBE)", size=15, bold=True, color=FIELD, anchor="start"))
    p.append(text(35, y_bot + 48, "структура в буфері вже готова до читання процесором", size=12, color=MUTED, anchor="start"))

    b_boxes = [
        (35, 370, 190, 75, "Неперервний буфер\nв пам'яті\n(RAM / mmap / Shm)", BLUE_F, NEG),
        (265, 370, 200, 75, "Вказівник на корінь\n`root = (Table*)(buf + off)`\n(нуль алокацій)", GREEN_F, FIELD),
        (505, 370, 215, 75, "Таблиця зсувів\nзсув поля за O(1)\n(Vtable / фіксований)", GREEN_F, FIELD),
        (760, 370, 180, 75, "Читання поля\nпроста інструкція CPU\n`MOV reg, [ptr + off]`", GREEN_F, FIELD),
    ]
    for bx, by, bw, bh, blabel, bfill, bstroke in b_boxes:
        p.append(fitbox(bx, by, bw, bh, blabel, size=12, fill=bfill, stroke=bstroke, sw=1.5))

    p.append(arrow(225, 407, 265, 407, color=MUTED, sw=1.8))
    p.append(arrow(465, 407, 505, 407, color=MUTED, sw=1.8))
    p.append(arrow(720, 407, 760, 407, color=MUTED, sw=1.8))

    p.append(fitbox(35, 462, 910, 52,
                    "Переваги: час десеріалізації 0 нс · нуль системних виділень пам'яті · читаються лише потрібні поля · локальність кешу L1/L2",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.2, color=FIELD))

    render(os.path.join(OUT, "deserialization-pipeline.svg"), W, H, *p,
           title="Класична десеріалізація проти прямого доступу в буфері (Zero-Copy)")


# ── 2. alignment-and-padding: вирівнювання та межі кеш-ліній ────────────────
def fig_alignment_and_padding():
    W, H = 980, 560
    p = []

    # Верхній пояснювальний заголовок
    p.append(fitbox(30, 40, 920, 50,
                    "Природне вирівнювання (Natural Alignment): n-байтний тип має починатися з адреси, кратної n.\nПорушення веде до штрафів шини, розщеплення кеш-ліній (Split Cache Line) або апаратних виключень.",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.4))

    # Секція 1: Правильне вирівнювання (Aligned Layout)
    y1 = 110
    p.append(text(35, y1 + 22, "Вирівняна розкладка: кожне поле на кратній межі (8, 4, 2, 1 байти)", size=14, bold=True, anchor="start"))

    total_units = 32
    start_x = 35
    total_w = 910
    unit_w = total_w / float(total_units)

    layout_a = [
        (0, 8, "uint64_t a (8 байти)", GREEN_F, FIELD),
        (8, 4, "uint32_t b (4B)", GREEN_F, FIELD),
        (12, 2, "uint16 c", GREEN_F, FIELD),
        (14, 1, "u8 d", GREEN_F, FIELD),
        (15, 1, "pad", YELLOW_F, MUTED),
        (16, 4, "uint32_t e (4B)", GREEN_F, FIELD),
        (20, 4, "паддінг (4 байти)", YELLOW_F, MUTED),
        (24, 8, "double f (8 байтів)", GREEN_F, FIELD),
    ]

    for u_start, u_len, lbl, fill, stroke in layout_a:
        bx = start_x + u_start * unit_w
        bw = u_len * unit_w
        p.append(rect(bx, y1 + 35, bw, 46, fill=fill, stroke=stroke, sw=1.5, rx=3))
        p.append(fitbox(bx + 2, y1 + 37, bw - 4, 42, lbl, size=11, fill=fill, stroke=fill, bold=True))

    # Шкала байтів
    for b in range(0, total_units + 1, 4):
        bx = start_x + b * unit_w
        p.append(line(bx, y1 + 83, bx, y1 + 89, color=LINE, sw=1.2))
        p.append(text(bx, y1 + 102, "+%d B" % b, size=10, color=MUTED))

    # Секція 2: Межа кеш-ліній (64 байти) і розщеплене читання (Split Load)
    y2 = 255
    p.append(text(35, y2 + 22, "Розщеплення кеш-лінії: невирівняне 64-бітне число сидить на межі двох ліній", size=14, bold=True, color=POS, anchor="start"))

    cl1_x = 35
    cl_w = 425
    cl2_x = 520
    p.append(rect(cl1_x, y2 + 38, cl_w, 125, fill=BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(cl1_x + cl_w / 2, y2 + 58, "Кеш-лінія 0 (адреси 0x00 .. 0x3F)", size=13, bold=True))

    p.append(fitbox(cl1_x + 15, y2 + 75, 230, 72, "Попередні поля\nбайти 0x00..0x3B (60 Б)\nзнаходяться в лінії 0", size=11, fill=GREY_F, stroke=MUTED))
    p.append(fitbox(cl1_x + 255, y2 + 75, 155, 72, "Байти 60..63\nмолодші 4B\n(у лінії 0)", size=11, fill=RED_F, stroke=POS, bold=True, color=POS))

    p.append(rect(cl2_x, y2 + 38, cl_w, 125, fill=BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(cl2_x + cl_w / 2, y2 + 58, "Кеш-лінія 1 (адреси 0x40 .. 0x7F)", size=13, bold=True))

    p.append(fitbox(cl2_x + 15, y2 + 75, 155, 72, "Байти 64..67\nстарші 4B\n(у лінії 1)", size=11, fill=RED_F, stroke=POS, bold=True, color=POS))
    p.append(fitbox(cl2_x + 180, y2 + 75, 230, 72, "Наступні поля\nбайти 0x44..0x7F (60 Б)\nзнаходяться в лінії 1", size=11, fill=GREY_F, stroke=MUTED))

    # Центральна розділова позначка межі між лініями
    mid_x = 472
    p.append(line(mid_x, y2 + 35, mid_x, y2 + 165, color=POS, sw=2.0, dash="4,4"))
    p.append(text(mid_x, y2 + 180, "Межа 64 байтів", size=10, color=POS, bold=True))

    # Блок об'єднання результату
    y_bridge = y2 + 195
    p.append(rect(180, y_bridge, 620, 48, fill=YELLOW_F, stroke=POS, sw=1.6, rx=5))
    p.append(text(490, y_bridge + 30, "Цільовий uint64 = [байти 60..63] + [байти 64..67] → 2 транзакції шини L1D Cache", size=12, bold=True, color=POS))

    # Підсумкова картка
    p.append(fitbox(30, 490, 920, 52,
                    "Наслідок: замість 1 такту процесор виконує 2 звернення до кешу, склеює байти в регістрах зсувами та масками, або зазнає зупинки конвеєра.",
                    size=12, fill=RED_F, stroke=POS, sw=1.4, color=POS))

    render(os.path.join(OUT, "alignment-and-padding.svg"), W, H, *p,
           title="Вирівнювання пам'яті, паддінг та штраф перетину кеш-ліній")


# ── 3. vtable-offset-layout: розкладка FlatBuffers (Vtable + Table) ─────────
def fig_vtable_offset_layout():
    W, H = 980, 580
    p = []

    # Верхня інформаційна панель
    p.append(fitbox(30, 40, 920, 52,
                    "FlatBuffers: таблиця звертається до полів через від'ємний зсув до таблиці віртуальних зсувів (Vtable).\nВідсутні поля мають зсув 0 (рантайм повертає дефолт), нові поля дописуються у Vtable без зсуву старих.",
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.5))

    y_mid = 110

    # Блок ліворуч: Vtable (Таблиця зсувів полів)
    vx, vy, vw, vh = 35, y_mid + 40, 420, 340
    p.append(rect(vx, vy, vw, vh, fill=BG, stroke=NEG, sw=1.8, rx=6))
    p.append(text(vx + vw / 2, vy + 26, "Таблиця віртуальних зсувів (Vtable)", size=14, bold=True, color=NEG))
    p.append(text(vx + vw / 2, vy + 46, "значення у 16-бітних словах (uint16_t)", size=11, color=MUTED))

    vt_rows = [
        ("vtable_size = 12 B", "довжина vtable у байтах", BLUE_F, NEG),
        ("table_size = 16 B", "розмір даних таблиці", BLUE_F, NEG),
        ("offset_field_0 = 4", "зсув поля #0: hp (+4 B)", GREEN_F, FIELD),
        ("offset_field_1 = 8", "зсув поля #1: mana (+8 B)", GREEN_F, FIELD),
        ("offset_field_2 = 0", "поле #2 відсутнє (дефолт)", GREY_F, MUTED),
        ("offset_field_3 = 12", "зсув поля #3: name (+12 B)", GREEN_F, FIELD),
    ]

    for i, (name, desc, fill, stroke) in enumerate(vt_rows):
        ry = vy + 65 + i * 42
        p.append(rect(vx + 15, ry, 180, 36, fill=fill, stroke=stroke, sw=1.3, rx=4))
        p.append(text(vx + 105, ry + 22, name, size=11, bold=True, color=stroke))
        p.append(text(vx + 205, ry + 22, desc, size=11, anchor="start", color=INK))

    # Блок праворуч: Table Data (Самі дані екземпляра)
    tx, ty, tw, th = 515, y_mid + 40, 430, 340
    p.append(rect(tx, ty, tw, th, fill=BG, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(tx + tw / 2, ty + 26, "Дані таблиці (Table Data Instance)", size=14, bold=True, color=FIELD))
    p.append(text(tx + tw / 2, ty + 46, "покажчик `root` вказує на початок цієї таблиці", size=11, color=MUTED))

    tbl_rows = [
        ("soffset_to_vtable = −28", "зсув назад до vtable (int32)", RED_F, POS),
        ("hp = 100 (uint32_t)", "поле #0 за зсувом +4 B", GREEN_F, FIELD),
        ("mana = 50 (uint32_t)", "поле #1 за зсувом +8 B", GREEN_F, FIELD),
        ("uoffset_to_name = +24", "поле #3: зсув до рядка (+12 B)", GREEN_F, FIELD),
    ]

    for i, (name, desc, fill, stroke) in enumerate(tbl_rows):
        ry = ty + 65 + i * 55
        p.append(rect(tx + 15, ry, 210, 46, fill=fill, stroke=stroke, sw=1.3, rx=4))
        p.append(text(tx + 120, ry + 28, name, size=11, bold=True, color=stroke))
        p.append(text(tx + 235, ry + 28, desc, size=11, anchor="start", color=INK))

    # Стрілка зворотної індирекції від Table Data до Vtable
    p.append(arrow(tx + 15, ty + 88, vx + vw - 10, vy + 75, color=POS, sw=2.2))
    p.append(text(485, ty + 70, "soffset", size=12, color=POS, bold=True))

    # Стрілка прямого доступу від vtable до поля
    p.append(arrow(vx + vw - 15, vy + 172, tx + 15, ty + 145, color=FIELD, sw=1.8))

    # Нижня рамка правил сумісності
    p.append(fitbox(30, 505, 920, 56,
                    "Еволюція схеми: старий код читає нові повідомлення (ігнорує нові поля у vtable), "
                    "новий код читає старі (бачить зсув 0 або vtable_size < потрібного зсуву і бере константу за замовчуванням).",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, "vtable-offset-layout.svg"), W, H, *p,
           title="Будова FlatBuffers: зв'язок таблиці екземпляра з таблицею віртуальних зсувів")


# ── 4. capnproto-segment-layout: сегменти й покажчики Cap'n Proto ────────────
def fig_capnproto_segment_layout():
    W, H = 980, 560
    p = []

    # Верхній опис
    p.append(fitbox(30, 40, 920, 50,
                    "Cap'n Proto: вирівнювання за 64-бітними словами (Word = 8B). Покажчик кодує тип об'єкта,\nрозмір секції скалярів (Data Section) і розмір секції вкладених покажчиків (Pointer Section).",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.4))

    y_base = 110

    # Блок 1: Заголовок кадру повідомлення (Message Framing Header)
    p.append(rect(30, y_base, 920, 80, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    p.append(text(45, y_base + 24, "Заголовок кадру повідомлення (Framing Header)", size=13, bold=True, color=NEG, anchor="start"))

    hdr_blocks = [
        (45, y_base + 38, 160, 32, "Кількість сегментів N", GREY_F),
        (215, y_base + 38, 180, 32, "Розмір сегмента 0 (слова)", GREY_F),
        (405, y_base + 38, 180, 32, "Розмір сегмента 1 (слова)", GREY_F),
        (595, y_base + 38, 340, 32, "Паддінг до вирівнювання 8 байтів", YELLOW_F),
    ]
    for bx, by, bw, bh, blbl, bfill in hdr_blocks:
        p.append(rect(bx, by, bw, bh, fill=bfill, stroke=LINE, sw=1.1, rx=3))
        p.append(text(bx + bw / 2, by + 20, blbl, size=11))

    # Блок 2: Розбір 64-бітного покажчика структури (Struct Pointer Anatomy)
    y_ptr = 210
    p.append(rect(30, y_ptr, 920, 110, fill=BG, stroke=POS, sw=1.6, rx=6))
    p.append(text(45, y_ptr + 24, "Анатомія 64-бітного покажчика структури (Struct Pointer)", size=13, bold=True, color=POS, anchor="start"))

    ptr_fields = [
        (45, y_ptr + 40, 140, 50, "Тип: Struct\n(біти 0..1 = 00)", RED_F, POS),
        (195, y_ptr + 40, 260, 50, "Зсув: +N слів\n(біти 2..31 зі знаком)", BLUE_F, NEG),
        (465, y_ptr + 40, 220, 50, "Data Section Size\n(біти 32..47: к-сть слів)", GREEN_F, FIELD),
        (695, y_ptr + 40, 240, 50, "Pointer Section Size\n(біти 48..63: к-сть слів)", GREEN_F, FIELD),
    ]
    for bx, by, bw, bh, blbl, bfill, bstroke in ptr_fields:
        p.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, sw=1.3, rx=4))
        p.append(fitbox(bx + 2, by + 2, bw - 4, bh - 4, blbl, size=11, fill=bfill, stroke=bfill, bold=True))

    # Блок 3: Розкладка об'єкта в сегменті
    y_seg = 340
    p.append(rect(30, y_seg, 920, 190, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(45, y_seg + 24, "Цільова структура в сегменті пам'яті", size=13, bold=True, color=FIELD, anchor="start"))

    seg_cols = [
        (45, y_seg + 42, 420, 130,
         "Data Section (Секція чистих значень)\n\n"
         "· Слово 0: `int64_t timestamp` (8 байтів)\n"
         "· Слово 1: `float32 x` (4B) + `float32 y` (4B)\n"
         "Пряме читання за фіксованим зміщенням!",
         GREEN_F, FIELD),
        (495, y_seg + 42, 440, 130,
         "Pointer Section (Секція покажчиків)\n\n"
         "· Покажчик 0: Список точок `List(Struct)`\n"
         "· Покажчик 1: Текстовий рядок `Text (UTF-8)`\n"
         "· Far Pointer: перехід в інший сегмент при IPC",
         BLUE_F, NEG),
    ]
    for bx, by, bw, bh, btext, bfill, bstroke in seg_cols:
        p.append(fitbox(bx, by, bw, bh, btext, size=12, fill=bfill, stroke=bstroke, sw=1.4))

    render(os.path.join(OUT, "capnproto-segment-layout.svg"), W, H, *p,
           title="Сегментна архітектура та 64-бітні типізовані покажчики Cap'n Proto")


# ── 5. zero-copy-transports: mmap, Shared Memory та RDMA ───────────────────
def fig_zero_copy_transports():
    W, H = 980, 560
    p = []

    p.append(fitbox(30, 40, 920, 48,
                    "Наскрізні канали Zero-Copy: усунення проміжних буферів ядра ОС та копіювань між процесами.\nДані кладуться в оперативну пам'ять один раз і читаються всіма споживачами на місці.",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.4))

    # Три стовпці: Файли (mmap), IPC (Shared Memory), Мережа (RDMA)
    cols = [
        (35, 110, 285, 420,
         "1. Файли: POSIX mmap",
         BLUE_F, NEG,
         [
             ("Дисковий накопичувач\nNVMe SSD / HDD", GREY_F),
             ("Сторінковий кеш ОС\n(Page Cache ядра)", BLUE_F),
             ("Таблиця сторінок MMU\nвіртуальний простір процесу", BLUE_F),
             ("Прямий доступ CPU\nбез виклику read()", GREEN_F),
         ],
         "ОС підвантажує сторінки за потребою (Page Fault); нуль копій у буфери користувача"),

        (345, 110, 285, 420,
         "2. IPC: Shared Memory",
         GREEN_F, FIELD,
         [
             ("Процес-виробник\nформує буфер у /dev/shm", GREEN_F),
             ("Спільні сторінки RAM\nфізична пам'ять", BLUE_F),
             ("Процес-споживач\nвідображає той самий буфер", GREEN_F),
             ("Читання без IPC-копій\nзатримка < 100 нс", GREEN_F),
         ],
         "Спільний адресний простір: виключає пересилання через сокети чи пайпи"),

        (655, 110, 290, 420,
         "3. Мережа: RDMA / Bypass",
         RED_F, POS,
         [
             ("Мережева карта (NIC)\nInfiniBand / RoCE", RED_F),
             ("Апаратний DMA через PCIe\nпросто в RAM користувача", BLUE_F),
             ("Буфер користувача\nоминаючи стек ядра (Bypass)", GREEN_F),
             ("Обробка повідомлення\nчас передачі ~ 1 мкс", GREEN_F),
         ],
         "Kernel Bypass: мережева карта записує дані прямо в пам'ять програми"),
    ]

    for cx, cy, cw, ch, ctitle, cfill, cstroke, steps, cfooter in cols:
        p.append(rect(cx, cy, cw, ch, fill=BG, stroke=cstroke, sw=1.8, rx=8))
        p.append(fitbox(cx + 8, cy + 10, cw - 16, 36, ctitle, size=13, fill=cfill, stroke=cstroke, bold=True, color=cstroke))

        sy = cy + 55
        for sidx, (stitle, sfill) in enumerate(steps):
            p.append(fitbox(cx + 15, sy, cw - 30, 52, stitle, size=11, fill=sfill, stroke=LINE, sw=1.1))
            if sidx < len(steps) - 1:
                p.append(arrow(cx + cw / 2, sy + 53, cx + cw / 2, sy + 68, color=MUTED, sw=1.6))
                sy += 70

        p.append(fitbox(cx + 10, cy + ch - 65, cw - 20, 55, cfooter, size=11, fill=cfill, stroke=cfill, color=cstroke))

    render(os.path.join(OUT, "zero-copy-transports.svg"), W, H, *p,
           title="Системні механізми передачі даних без копіювання: mmap, Shm, RDMA")


# ── 6. bounds-validation-traversal: безпека меж та циклів ───────────────────
def fig_bounds_validation_traversal():
    W, H = 980, 540
    p = []

    # Верхній опис
    p.append(fitbox(30, 40, 920, 50,
                    "Безпека форматів без копіювання: перевірка меж (Bounds Checking) запобігає виходу за межі буфера,\nа лічильник глибини обходу (Depth / Budget Limit) захищає від шкідливих циклічних покажчиків.",
                    size=12, fill=RED_F, stroke=POS, sw=1.5))

    # Схема буфера та перевірки зсуву
    y1 = 110
    bx, by, bw, bh = 35, y1 + 10, 910, 150
    p.append(rect(bx, by, bw, bh, fill=BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx + 15, by + 24, "Буфер у пам'яті: [ buffer_start ... buffer_end ], загальний розмір Size", size=13, bold=True, anchor="start"))

    # Смуга буфера (відокремлені блоки замість накладання)
    # Початок буфера
    p.append(rect(bx + 30, by + 42, 90, 40, fill=GREY_F, stroke=LINE, sw=1.3, rx=3))
    p.append(text(bx + 75, by + 66, "0x00 (Start)", size=11, color=INK))

    # Валідний діапазон
    p.append(rect(bx + 140, by + 42, 340, 40, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=3))
    p.append(text(bx + 310, by + 66, "Поле: offset + sizeof(T) ✓ (Валідно)", size=11, color=FIELD, bold=True))

    # Середина буфера
    p.append(rect(bx + 500, by + 42, 140, 40, fill=BLUE_F, stroke=NEG, sw=1.3, rx=3))
    p.append(text(bx + 570, by + 66, "... Дані ...", size=11, color=NEG))

    # Невалідний діапазон (вихід за межі)
    p.append(rect(bx + 660, by + 42, 220, 40, fill=RED_F, stroke=POS, sw=1.8, rx=3))
    p.append(text(bx + 770, by + 66, "Шкідливий зсув > Size ✗", size=11, color=POS, bold=True))

    p.append(fitbox(bx + 30, by + 95, 850, 50,
                    "Правило безпечної перевірки без переповнення цілих чисел (No Integer Overflow):\n"
                    "Неправильно: `offset + size <= total_size` (може переповнитися при зсувах біля 0xFFFFFFFF).\n"
                    "Правильно: `offset <= total_size && size <= total_size - offset`.",
                    size=11, fill=GREY_F, stroke=LINE, sw=1.1))

    # Нижня частина: Захист від петель і вичерпання ресурсів
    y2 = 290
    p.append(rect(35, y2, 440, 230, fill=BG, stroke=POS, sw=1.6, rx=6))
    p.append(text(50, y2 + 26, "Атака: Циклічні покажчики та глибина", size=13, bold=True, color=POS, anchor="start"))

    p.append(circle(120, y2 + 80, 25, fill=RED_F, stroke=POS, sw=1.6))
    p.append(text(120, y2 + 85, "Вузол A", size=11, bold=True))

    p.append(circle(300, y2 + 80, 25, fill=RED_F, stroke=POS, sw=1.6))
    p.append(text(300, y2 + 85, "Вузол B", size=11, bold=True))

    p.append(arrow(145, y2 + 75, 275, y2 + 75, color=POS, sw=1.8))
    p.append(arrow(275, y2 + 88, 145, y2 + 88, color=POS, sw=1.8))
    p.append(text(210, y2 + 65, "offset_to_B", size=10, color=POS))
    p.append(text(210, y2 + 105, "offset_to_A", size=10, color=POS))

    p.append(fitbox(50, y2 + 130, 410, 80,
                    "Загроза: замкнене кільце зсувів викликає нескінченну рекурсію,\nпереповнення стека (Stack Overflow) або вичерпання пам'яті (DoS).",
                    size=11, fill=RED_F, stroke=POS, sw=1.2, color=POS))

    # Права картка захисту
    p.append(rect(505, y2, 440, 230, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(520, y2 + 26, "Захист: Бюджет обходу (Traversal Limit)", size=13, bold=True, color=FIELD, anchor="start"))

    p.append(fitbox(520, y2 + 45, 410, 165,
                    "Механізми валідації:\n\n"
                    "1. Глибина рекурсії (Max Depth): обмеження вкладеності (наприклад, не більше 64 рівнів).\n"
                    "2. Бюджет байтів (Step Budget): лічильник сумарно переглянутих байтів зменшується при кожному переході. Якщо лічильник < 0 — скидання сесії.\n"
                    "3. Однопрохідний валідатор (Fast Verifier): перевірка структури перед доступом.",
                    size=11, fill=GREEN_F, stroke=FIELD, sw=1.3))

    render(os.path.join(OUT, "bounds-validation-traversal.svg"), W, H, *p,
           title="Перевірка меж буфера та захист від циклічних покажчиків")


if __name__ == "__main__":
    fig_deserialization_pipeline()
    fig_alignment_and_padding()
    fig_vtable_offset_layout()
    fig_capnproto_segment_layout()
    fig_zero_copy_transports()
    fig_bounds_validation_traversal()
    print("All figures generated successfully.")
