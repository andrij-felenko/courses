# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#9a7322"   # бурштиновий акцент (купа / увага)


# ── grow-toward: стек униз, купа вгору, спільний простір ─────────────────────
# Ідея: два регіони ростуть назустріч у той самий вільний простір; коли стек
# дороста до купи — взаємне псування. На ПК ловить ОС, на МК — тиша.

def fig_grow_toward():
    W, H = 720, 430
    cx = 250                       # вісь смуги пам'яті
    bw = 150
    top, bot = 70, 360
    p = []

    # рамка всього адресного простору
    p.append(rect(cx - bw / 2, top, bw, bot - top, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=4))

    # стек згори
    p.append(rect(cx - bw / 2, top, bw, 70, fill="#fdecec", stroke=POS, sw=1.7, rx=0))
    p.append(text(cx, top + 28, "стек", size=14, color=POS, bold=True))
    p.append(text(cx, top + 48, "виклики, локальні", size=9.5, color=MUTED))

    # купа знизу
    p.append(rect(cx - bw / 2, bot - 70, bw, 70, fill="#fff6e6", stroke=WARN, sw=1.7, rx=0))
    p.append(text(cx, bot - 44, "купа + дані", size=14, color=WARN, bold=True))
    p.append(text(cx, bot - 24, "вгору ↑", size=9.5, color=MUTED))

    # вільний простір посередині
    p.append(text(cx, (top + bot) / 2 + 4, "вільний простір", size=10.5, color=MUTED, italic=True))

    # стрілки назустріч
    p.append(arrow(cx - bw / 2 - 24, top + 18, cx - bw / 2 - 24, top + 120, color=POS, sw=2.4))
    p.append(text(cx - bw / 2 - 30, top + 70, "вниз", size=10, color=POS, bold=True, anchor="end"))
    p.append(arrow(cx + bw / 2 + 24, bot - 18, cx + bw / 2 + 24, bot - 120, color=WARN, sw=2.4))
    p.append(text(cx + bw / 2 + 30, bot - 70, "вгору", size=10, color=WARN, bold=True, anchor="start"))

    # зона зіткнення
    p.append(line(cx - bw / 2, (top + bot) / 2 + 34, cx + bw / 2, (top + bot) / 2 + 34,
                  color=POS, sw=1.6, dash="5,4"))
    p.append(text(cx, (top + bot) / 2 + 50, "дороста до купи → псують одне одного",
                  size=10, color=POS, bold=True))

    # права колонка: ПК проти МК
    rx0 = 470
    p.append(fitbox(rx0, 90, 210, 110,
                    "ПК\nапаратний захист (MMU) +\nОС ловлять наїзд → програму\nобривають одразу (segfault)",
                    size=11, fill="#eef7ee", stroke=FIELD))
    p.append(fitbox(rx0, 220, 210, 120,
                    "МК\nзахисту пам'яті немає →\nстек ТИХО перезаписує\nкупу/дані, і пристрій\nпочинає «дуріти»",
                    size=11, fill="#fdecec", stroke=POS))

    render(os.path.join(OUT, "grow-toward.svg"), W, H, *p,
           title="Стек росте вниз, купа вгору — у спільний простір")


# ── buffer-overflow: запис за межі масиву затирає адресу повернення ──────────
# Ідея: 8-байтовий буфер, пишемо 12 — «зайве» перетікає на сусіда, а сусід на
# стеку часто адреса повернення → крах або захоплення керування.

def fig_buffer_overflow():
    W, H = 720, 400
    x0, y0 = 90, 130
    cell = 38
    p = []

    # буфер на 8 байтів
    for i in range(8):
        p.append(rect(x0 + i * cell, y0, cell, cell, fill="#eef4ff", stroke=NEG, sw=1.4, rx=0))
    p.append(text(x0 + 4 * cell, y0 - 16, "буфер: 8 байтів", size=12, color=NEG, bold=True))

    # сусід: збережені регістри + адреса повернення
    nb = x0 + 8 * cell
    p.append(rect(nb, y0, 2 * cell, cell, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=0))
    p.append(text(nb + cell, y0 + cell + 16, "регістри", size=9.5, color=MUTED))
    rb = nb + 2 * cell
    p.append(rect(rb, y0, 2 * cell, cell, fill="#fff6e6", stroke=WARN, sw=1.7, rx=0))
    p.append(mtext(rb + cell, y0 + cell / 2 - 4, "адреса", size=10, color=WARN, bold=True))
    p.append(text(rb + cell, y0 + cell + 16, "повернення", size=9.5, color=WARN))

    # потік запису: 12 байтів накриває буфер і перші 4 сусіда
    wy = y0 - 58
    p.append(rect(x0, wy, 12 * cell, 28, fill="#fdecec", stroke=POS, sw=1.6, rx=4))
    p.append(text(x0 + 6 * cell, wy + 18, "пишемо 12 байтів — не глянувши, чи влазить",
                  size=11, color=POS, bold=True))
    p.append(arrow(x0 + 6 * cell, wy + 30, x0 + 6 * cell, y0 - 4, color=POS, sw=2.0))
    # хвіст «зайвого» дотягується до адреси повернення
    p.append(arrow(x0 + 10 * cell, wy + 30, rb + cell, y0 - 4, color=POS, sw=2.2))
    p.append(text(rb + cell, wy + 6, "«зайве» сюди", size=9.5, color=POS, bold=True, anchor="middle"))

    # два наслідки
    p.append(fitbox(x0, y0 + 90, 280, 96,
                    "адреса = сміття\nфункція «вертається» казна-куди\n→ аварія",
                    size=11, fill="#fdf6f6", stroke=POS))
    p.append(fitbox(x0 + 310, y0 + 90, 300, 96,
                    "адресу підібрав зловмисник\n→ перехід у ЙОГО код\n(захоплення керування,\n«smashing the stack»)",
                    size=11, fill="#fdecec", stroke=POS))

    render(os.path.join(OUT, "buffer-overflow.svg"), W, H, *p,
           title="Переповнення буфера: запис за межі затирає сусіда")


# ── roundup: звід типових бід пам'яті ───────────────────────────────────────
# Ідея: одним поглядом — уся родина споріднених вад пам'яті, кожна одним рядком.

def fig_roundup():
    W, H = 720, 430
    rows = [
        ("Переповнення стека", "стек доріс до купи", POS),
        ("Переповнення буфера", "запис за межі масиву псує сусіда, аж до адреси повернення", POS),
        ("Витік пам'яті", "узяв на купі й не повернув → вичерпання", WARN),
        ("Висячий покажчик", "указує на звільнену / зниклу пам'ять", WARN),
        ("Розіменування null", "піти за нульовим покажчиком", NEG),
        ("Дикий покажчик", "випадкова, ніколи не задана адреса", NEG),
        ("Подвійне звільнення", "free() двічі по тій самій пам'яті", WARN),
        ("Читання неініціалізованого", "узяв змінну до присвоєння → сміття", NEG),
    ]
    x0, y0, w, rh = 60, 64, W - 120, 42
    p = []
    for i, (name, desc, col) in enumerate(rows):
        y = y0 + i * rh
        p.append(rect(x0, y, w, rh - 6, fill="#fbfcfd", stroke=col, sw=1.5, rx=6))
        p.append(text(x0 + 14, y + (rh - 6) / 2 + 4, name, size=12, color=col, bold=True, anchor="start"))
        p.append(text(x0 + 250, y + (rh - 6) / 2 + 4, desc, size=10.5, color=INK, anchor="start"))
    render(os.path.join(OUT, "roundup.svg"), W, H, *p,
           title="Звід типових бід пам'яті")


# ── why-hard: тихі, далекі, несталі; МК проти ПК ────────────────────────────
# Ідея: три риси, через які баг пам'яті найважчий для лову, плюс контраст МК/ПК.

def fig_why_hard():
    W, H = 720, 400
    x0, w = 60, W - 120
    p = []
    traits = [
        ("тихі", "не дають негайної помилки — псують пам'ять і йдуть далі, ніби все гаразд"),
        ("далекі", "симптом виринає не там, де причина: зіпсував одне — впало інше, згодом"),
        ("несталі", "залежать від таймінгу й даних: то є, то нема — важко відтворити"),
    ]
    for i, (k, v) in enumerate(traits):
        y = 64 + i * 50
        p.append(rect(x0, y, w, 42, fill="#fdf6f6", stroke=POS, sw=1.6, rx=8))
        p.append(text(x0 + 16, y + 26, k, size=13, color=POS, bold=True, anchor="start"))
        p.append(text(x0 + 150, y + 26, v, size=10.5, color=INK, anchor="start"))

    p.append(fitbox(x0, 232, w / 2 - 12, 120,
                    "на МК — гірше\nзахисту пам'яті немає →\nхибний доступ ніхто не ловить,\nа в полі ще й нема кому\nперезапустити",
                    size=11, fill="#fdecec", stroke=POS))
    p.append(fitbox(x0 + w / 2 + 12, 232, w / 2 - 12, 120,
                    "на ПК — легше\nапаратний захист (MMU) + ОС\nловлять багато звернень «не туди»\n→ програма падає одразу\n(segfault), ближче до помилки",
                    size=11, fill="#eef7ee", stroke=FIELD))
    render(os.path.join(OUT, "why-hard.svg"), W, H, *p,
           title="Чому біди пам'яті — найважчі для лову")


# ── common-root: дві першопричини всіх бід пам'яті ──────────────────────────
# Ідея: усе розмаїття зводиться до двох коренів — доступ поза межами і вживання
# не у свій час; звідси й уся профілактика.

def fig_common_root():
    W, H = 720, 380
    p = []
    p.append(rect(60, 70, 290, 230, fill="#fdf6f6", stroke=POS, sw=1.7, rx=10))
    p.append(text(205, 98, "доступ поза дійсною пам'яттю", size=12.5, color=POS, bold=True))
    for i, s in enumerate(["за межі масиву (буфер)",
                           "за нульовою / випадковою адресою",
                           "стек доріс до купи"]):
        p.append(text(78, 130 + i * 26, "• " + s, size=10.5, color=INK, anchor="start"))
    p.append(fitbox(74, 214, 262, 72,
                    "корінь: плутанина «адреса / значення»\n+ брак перевірки меж",
                    size=10.5, fill="#fff", stroke=POS))

    p.append(rect(370, 70, 290, 230, fill="#eef4ff", stroke=NEG, sw=1.7, rx=10))
    p.append(text(515, 98, "вживання в не той час", size=12.5, color=NEG, bold=True))
    for i, s in enumerate(["до ініціалізації → сміття",
                           "після звільнення → висячий",
                           "після виходу функції → локальна"]):
        p.append(text(388, 130 + i * 26, "• " + s, size=10.5, color=INK, anchor="start"))
    p.append(fitbox(384, 214, 262, 72,
                    "корінь: брак дисципліни покажчиків\n+ керування часом життя",
                    size=10.5, fill="#fff", stroke=NEG))

    p.append(text(W / 2, 340,
                  "звідси вся профілактика: не виходь за межі й не чіпай пам'ять не у свій час",
                  size=11.5, color=FIELD, bold=True))
    render(os.path.join(OUT, "common-root.svg"), W, H, *p,
           title="Спільний корінь — дві першопричини")


# ── defenses: звички, що гасять більшість бід ───────────────────────────────
# Ідея: набір конкретних звичок — від перевірки меж до вибору мови — кожна
# закриває свій клас бід.

def fig_defenses():
    W, H = 720, 420
    items = [
        ("перевіряй межі", "індекс < розмір; не вір довжині вхідних даних"),
        ("ініціалізуй усе", "змінні й покажчики — одразу при оголошенні"),
        ("звільняй рівно раз", "кожному allocate — один free, тоді обнули покажчик"),
        ("бережи стек", "без нескінченної рекурсії й величезних локальних"),
        ("на МК — статика", "статична / стекова пам'ять переважно над купою"),
        ("інструменти й мови", "санітайзери, статичний аналіз; Rust гасить класи бід"),
    ]
    x0, y0, w, rh = 60, 64, W - 120, 50
    p = []
    for i, (k, v) in enumerate(items):
        y = y0 + i * rh
        p.append(rect(x0, y, w, rh - 8, fill="#eef7ee", stroke=FIELD, sw=1.5, rx=8))
        p.append(text(x0 + 16, y + (rh - 8) / 2 + 4, k, size=12.5, color=FIELD, bold=True, anchor="start"))
        p.append(text(x0 + 220, y + (rh - 8) / 2 + 4, v, size=10.5, color=INK, anchor="start"))
    p.append(text(W / 2, H - 18,
                  "C/C++ на МК довіряє вам — дисципліна цілком на програмістові",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "defenses.svg"), W, H, *p,
           title="Як захищатися: звички, що гасять більшість бід")


# ── detect: canary і high-water mark ловлять переповнення стека ──────────────
# Ідея: дві практичні техніки детекту. Canary — стартовий вартовий-байт перед
# адресою повернення (зіпсувався → ловимо на виході). Watermark — фарбуємо стек
# візерунком, шукаємо найглибший зачеплений байт = пік використання.

def fig_detect():
    W, H = 720, 470
    p = []

    # ЛІВО: canary
    lx = 60
    p.append(text(lx + 150, 64, "Стек-canary (вартовий)", size=12.5, color=POS, bold=True))
    cy = 90
    cell = 30
    labels = [("локальні", "#eef4ff", NEG),
              ("canary 0xDEAD…", "#fff6e6", WARN),
              ("адреса повернення", "#fdecec", POS)]
    for i, (lab, fill, col) in enumerate(labels):
        y = cy + i * (cell + 6)
        p.append(rect(lx, y, 300, cell, fill=fill, stroke=col, sw=1.5, rx=4))
        p.append(text(lx + 150, y + cell / 2 + 4, lab, size=10.5, color=col, bold=True))
    p.append(fitbox(lx, cy + 3 * (cell + 6) + 8, 300, 86,
                    "на виході функції звіряємо canary:\nзмінився → буфер переповнено →\nвиняток / зупинка ще до return",
                    size=10.5, fill="#fff", stroke=POS))

    # ПРАВО: high-water mark
    rx = 410
    p.append(text(rx + 130, 64, "High-water mark (фарбування)", size=12.5, color=FIELD, bold=True))
    bx, by, bw, bh = rx + 70, 90, 60, 250
    n = 10
    ch = bh / n
    used = 4   # скільки відсіків стек уже зачепив
    for i in range(n):
        y = by + i * ch
        if i < used:
            fill, col, txt = "#fdecec", POS, ""          # затерто (використано)
        else:
            fill, col, txt = "#eef7ee", FIELD, "0xAA"     # ще цілий візерунок
        p.append(rect(bx, y, bw, ch, fill=fill, stroke=col, sw=1.0, rx=0))
        if txt and i >= used:
            p.append(text(bx + bw / 2, y + ch / 2 + 3, txt, size=9, color=MUTED))
    p.append(text(bx + bw / 2, by - 8, "верх стека", size=9, color=MUTED))
    p.append(text(bx + bw / 2, by + bh + 16, "дно (вартова смуга)", size=9, color=MUTED))
    # межа піку
    yb = by + used * ch
    p.append(line(bx - 16, yb, bx + bw + 16, yb, color=POS, sw=2.0, dash="5,3"))
    p.append(text(bx + bw + 22, yb + 4, "пік", size=10, color=POS, bold=True, anchor="start"))
    p.append(fitbox(rx, by + bh + 28, 280, 64,
                    "стартом фарбуємо стек 0xAA; перший\nцілий байт = найглибший зачеплений →\nскільки запасу лишилось",
                    size=10, fill="#fff", stroke=FIELD))

    render(os.path.join(OUT, "detect.svg"), W, H, *p,
           title="Як ловити переповнення стека: canary і watermark")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКИ — фігури до 🔌 comp-mpu.md і 📜 hist-morris-worm.md
# ════════════════════════════════════════════════════════════════════════════

# ── mpu-checkpoint: MPU як застава між ядром і пам'яттю ──────────────────────
# Ідея: ядро не дотягується до пам'яті напряму — між ними MPU, що звіряє кожен
# доступ із таблицею регіонів. Збігається — пускає (зелена); порушує — fault.

def fig_mpu_checkpoint():
    W, H = 760, 430
    p = []

    # ядро CPU
    p.append(rect(50, 150, 150, 120, fill="#eef4ff", stroke=NEG, sw=2.0, rx=12))
    p.append(text(125, 178, "ядро CPU", size=14, color=NEG, bold=True))
    p.append(text(125, 202, "виконує код,", size=10, color=MUTED))
    p.append(text(125, 218, "читає й пише змінні", size=10, color=MUTED))
    p.append(text(125, 246, "привілейований чи", size=9.5, color=MUTED, italic=True))
    p.append(text(125, 260, "звичайний режим", size=9.5, color=MUTED, italic=True))

    # MPU посередині
    p.append(rect(286, 120, 188, 200, fill="#fff6e6", stroke=WARN, sw=2.4, rx=14))
    p.append(text(380, 148, "MPU", size=18, color=INK, bold=True))
    p.append(text(380, 167, "Memory Protection Unit", size=9, color=MUTED, italic=True))
    p.append(text(380, 184, "блок захисту пам'яті", size=10, color=MUTED))
    p.append(fitbox(298, 198, 164, 104,
                    "таблиця регіонів\nрегіон 0: база–межа, права\nрегіон 1: база–межа, права\nрегіон 2: база–межа, права\n…",
                    size=9, pad=6, fill="#fff", stroke=INK))

    # адресний простір праворуч
    p.append(text(640, 96, "адресний простір", size=11, color=INK, bold=True))
    mem = [(".text  код", "RX", FIELD),
           (".rodata стал.", "R", FIELD),
           (".data/.bss", "RW", NEG),
           ("купа", "RW", NEG),
           ("стек", "RW", NEG),
           ("MMIO периф.", "прив.", POS)]
    mx, my, mw, mh = 560, 104, 160, 34
    for i, (lab, rights, col) in enumerate(mem):
        y = my + i * (mh + 2)
        p.append(rect(mx, y, mw, mh, fill="#fff", stroke=col, sw=1.6, rx=6))
        p.append(text(mx + 10, y + mh / 2 + 4, lab, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(mx + mw - 10, y + mh / 2 + 4, rights, size=10.5, color=col, bold=True, anchor="end"))

    # стрілка ядро → MPU (доступ)
    p.append(arrow(200, 200, 286, 215, color=INK, sw=2.2))
    p.append(text(243, 184, "доступ:", size=10, color=INK, bold=True))
    p.append(text(243, 198, "адреса + R/W/fetch", size=9, color=MUTED))

    # стрілка MPU → пам'ять (дозволено, зелена)
    p.append(arrow(476, 200, 556, 170, color=FIELD, sw=2.2))
    p.append(text(515, 232, "права збігаються →", size=9.5, color=FIELD, bold=True))
    p.append(text(515, 246, "пускає мовчки", size=9.5, color=FIELD))

    # порушення → fault (червона, вниз)
    p.append(arrow(380, 320, 380, 356, color=POS, sw=2.4))
    p.append(text(396, 344, "права порушено →", size=10, color=POS, bold=True, anchor="start"))
    p.append(fitbox(50, 356, 660, 60,
                    "Звернення поза дозволеним (запис у код, вихід за межі, доступ не з того режиму) MPU не пускає —\nнатомість збуджує апаратний виняток (fault): замість тихого псування — негайна, точна зупинка.",
                    size=10.5, fill="#fdf4f4", stroke=POS))

    render(os.path.join(OUT, "mpu-checkpoint.svg"), W, H, *p,
           title="MPU — застава на шляху кожного доступу до пам'яті")


# ── mpu-regions: таблиця регіонів — база/межа + права ───────────────────────
# Ідея: MPU стереже не кожну комірку, а кілька грубих діапазонів; кожному —
# права. Код RX, сталі R, дані/купа/стек RW+NX, периферія лише привілейованим.

def fig_mpu_regions():
    W, H = 760, 470
    p = []
    x0, w = 50, W - 100

    # шапка таблиці
    cols = [(x0 + 8, "регіон (де лежить)"),
            (x0 + 220, "діапазон: база … межа"),
            (x0 + 420, "читати / писати"),
            (x0 + 545, "викон."),
            (x0 + 605, "режим")]
    p.append(rect(x0, 64, w, 30, fill="#eef1f6", stroke=INK, sw=1.4, rx=6))
    for cx, lab in cols:
        p.append(text(cx, 84, lab, size=11, color=INK, bold=True, anchor="start"))

    rows = [
        (".text — код",      "0x0000_0000 … +код", "R — лише читати", POS, "так (X)", FIELD, "усі", MUTED),
        (".rodata — сталі",  "далі за кодом",       "R — лише читати", POS, "ні",      MUTED, "усі", MUTED),
        (".data/.bss — глоб.","у RAM",              "RW",              NEG, "ні",      MUTED, "усі", MUTED),
        ("купа",             "у RAM, росте вгору",  "RW",              NEG, "ні",      MUTED, "усі", MUTED),
        ("стек",             "у RAM, росте вниз",   "RW",              NEG, "ні",      MUTED, "своя задача", MUTED),
        ("MMIO — периферія", "діапазон регістрів",  "RW",              NEG, "ні",      MUTED, "лише привіл.", POS),
    ]
    rowsep = [FIELD, FIELD, NEG, NEG, NEG, POS]
    ry, rh = 100, 38
    for i, (name, rng, rw_lab, rw_col, x_lab, x_col, m_lab, m_col) in enumerate(rows):
        y = ry + i * (rh + 2)
        p.append(rect(x0, y, w, rh, fill="#fbfcfd" if i % 2 == 0 else "#fff", stroke="#e4e4e4", sw=1.2, rx=5))
        p.append(rect(x0, y, 6, rh, fill=rowsep[i], stroke=rowsep[i], sw=0, rx=0))
        p.append(text(x0 + 8, y + rh / 2 + 4, name, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(x0 + 220, y + rh / 2 + 4, rng, size=10, color=MUTED, anchor="start"))
        p.append(text(x0 + 420, y + rh / 2 + 4, rw_lab, size=10.5, color=rw_col, bold=True, anchor="start"))
        p.append(text(x0 + 545, y + rh / 2 + 4, x_lab, size=10, color=x_col, bold=True, anchor="start"))
        p.append(text(x0 + 605, y + rh / 2 + 4, m_lab, size=10, color=m_col, anchor="start"))

    p.append(fitbox(x0, ry + 6 * (rh + 2) + 8, w, 66,
                    "Два правила гасять цілі класи бід: код позначено «лише читати», дані — «не виконувати» (NX, no-execute),\nа регістри периферії доступні «лише з привілейованого режиму» — звичайна задача їх навіть не торкнеться.",
                    size=10.5, fill="#f4f7f4", stroke=FIELD))

    render(os.path.join(OUT, "mpu-regions.svg"), W, H, *p,
           title="Регіон = шматок адрес + права доступу до нього")


# ── mpu-guard: регіон-вартовий не дає стеку затопити сусіда ──────────────────
# Ідея: без MPU стек мовчки псує сусідню .data; з MPU під стеком лежить смуга
# «жодного доступу» — перший же запис у неї = fault, чип спинено до псування.

def fig_mpu_guard():
    W, H = 760, 470
    p = []

    # ── ЛІВО: без MPU ──
    p.append(text(190, 90, "без MPU", size=13.5, color=MUTED, bold=True))
    p.append(rect(80, 108, 220, 64, fill="#eaf0fb", stroke=NEG, sw=1.6, rx=4))
    p.append(text(190, 134, "стек", size=11.5, color=NEG, bold=True))
    p.append(text(190, 152, "RW, росте вниз ↓", size=9.5, color=MUTED))
    p.append(rect(80, 178, 220, 50, fill="#fafafa", stroke=MUTED, sw=1.6, rx=4))
    p.append(text(190, 199, "спільний", size=10.5, color=MUTED, bold=True))
    p.append(text(190, 216, "вільний простір", size=9.5, color=MUTED))
    p.append(rect(80, 234, 220, 60, fill="#eafaef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(190, 260, ".data сусіда", size=11.5, color=FIELD, bold=True))
    p.append(text(190, 278, "звичайна доступна пам'ять", size=9.5, color=MUTED))
    p.append(line(190, 148, 190, 282, color=POS, sw=3, dash="2,3"))
    p.append(text(190, 314, "стек переріс і мовчки", size=10.5, color=POS, bold=True))
    p.append(text(190, 330, "затер .data сусіда —", size=10.5, color=POS))
    p.append(text(190, 346, "баг тихий, далекий, несталий", size=9.5, color=MUTED, italic=True))

    # роздільник
    p.append(line(W / 2, 84, W / 2, 350, color="#e4e4e4", sw=1.4, dash="4,4"))

    # ── ПРАВО: з MPU ──
    p.append(text(560, 90, "з MPU", size=13.5, color=INK, bold=True))
    p.append(rect(450, 108, 220, 64, fill="#eaf0fb", stroke=NEG, sw=1.8, rx=4))
    p.append(text(560, 134, "стек задачі", size=11.5, color=NEG, bold=True))
    p.append(text(560, 152, "RW, росте вниз ↓", size=9.5, color=MUTED))
    # вартовий — штрихована смуга
    p.append(rect(450, 178, 220, 50, fill="#fdecec", stroke=POS, sw=2.4, rx=4))
    for gx in range(470, 661, 20):
        p.append(line(gx, 178, gx, 228, color=POS, sw=1, dash="3,3"))
    p.append(text(560, 199, "регіон-вартовий", size=11.5, color=POS, bold=True))
    p.append(text(560, 217, "ЖОДНОГО доступу", size=10, color=POS, bold=True))
    p.append(rect(450, 234, 220, 60, fill="#eafaef", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(560, 260, ".data сусіда", size=11.5, color=FIELD, bold=True))
    p.append(text(560, 278, "цілий і недоторканий", size=9.5, color=MUTED))
    p.append(line(560, 148, 560, 174, color=POS, sw=3, dash="2,3"))
    p.append(text(560, 314, "перший же запис у вартового →", size=10, color=POS, bold=True))
    p.append(text(560, 330, "fault, чип спинено", size=10.5, color=INK, bold=True))
    p.append(text(560, 346, "до псування сусіда", size=9.5, color=MUTED, italic=True))

    # підсумок
    p.append(fitbox(50, 366, W - 100, 90,
                    "Стек однаково «хоче» затопити сусіда в обох випадках — різниця в тому, що під ним лежить.\nБез MPU нижче стека звичайна доступна пам'ять, тож перевитрата мовчки псує її, а симптом спливає геть в іншому місці.\nЗ MPU під кожен стек кладуть тонкий регіон «жодного доступу»: перший же запис у нього — fault, і ядро спиняється РАНІШЕ.\nОсь точна відповідь на «чому стек не затопить сусіда»: між ними — апаратна глуха стіна, а не просто порожнеча.",
                    size=10.3, fill="#f7f9fc", stroke=NEG))

    render(os.path.join(OUT, "mpu-guard.svg"), W, H, *p,
           title="Чому стек не затопить сусіда: глуха смуга-вартовий під ним")


# ── fingerd-overflow: 536 байтів у 512-байтовий буфер ───────────────────────
# Ідея: звичайний короткий запит вкладається; запит хробака на 536 затирає
# адресу повернення й наводить її назад у буфер. gets() не приймає розміру.

def fig_fingerd_overflow():
    W, H = 760, 500
    p = []

    # ── ЛІВО: звичайний запит ──
    p.append(text(195, 86, "Звичайний запит (вкладається)", size=12.5, color=FIELD, bold=True))
    p.append(rect(60, 96, 270, 156, fill="#f1f7f2", stroke=FIELD, sw=1.6, rx=6))
    p.append(rect(78, 112, 234, 72, fill="#e7f2ea", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(195, 142, "буфер[512]", size=13, color=INK, bold=True))
    p.append(text(195, 162, "коротке ім'я …", size=11, color=FIELD))
    p.append(rect(78, 190, 234, 24, fill="#eef3fb", stroke=NEG, sw=1.2, rx=3))
    p.append(text(195, 206, "збережені регістри", size=10.5, color=NEG))
    p.append(rect(78, 218, 234, 24, fill="#fff6e6", stroke=WARN, sw=1.4, rx=3))
    p.append(text(195, 234, "адреса повернення (ціла)", size=10, color=INK))
    p.append(text(195, 272, "функція чесно повертається назад", size=10.5, color=FIELD, italic=True))

    # ── ПРАВО: запит хробака ──
    p.append(text(565, 86, "Запит хробака: 536 байтів у 512", size=12.5, color=POS, bold=True))
    p.append(rect(430, 96, 270, 156, fill="#fdf4f4", stroke=POS, sw=1.6, rx=6))
    p.append(rect(448, 112, 234, 72, fill="#f7e2e2", stroke=POS, sw=1.4, rx=4))
    p.append(text(565, 138, "буфер[512]", size=13, color=INK, bold=True))
    p.append(text(565, 158, "код хробака (shell)", size=10.5, color=POS))
    p.append(text(565, 174, "0x90 0x90 … exec()", size=10, color=POS))
    p.append(rect(448, 190, 234, 24, fill="#f7e2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(565, 206, "затерто «зайвими» 24 Б", size=10, color=POS))
    p.append(rect(448, 218, 234, 24, fill="#ffd9d9", stroke=POS, sw=1.8, rx=3))
    p.append(text(565, 234, "адреса повернення = &буфер", size=10, color=POS, bold=True))
    # дуга «назад у буфер»
    p.append(line(682, 230, 712, 230, color=POS, sw=2))
    p.append(line(712, 230, 712, 148, color=POS, sw=2))
    p.append(arrow(712, 148, 684, 148, color=POS, sw=2))
    p.append(text(565, 272, "«повертається» у власний код хробака", size=10.5, color=POS, bold=True, italic=True))

    # ── смуга 512 + 24 ──
    p.append(text(W / 2, 312, "Чому 536 у 512: «зайві» 24 байти перелазять за буфер і лягають точно на адресу повернення",
                  size=12, color=INK, bold=True))
    bar_x, bar_w, bar_y = 150, 470, 326
    over_w = bar_w * 24.0 / 536.0
    p.append(rect(bar_x, bar_y, bar_w - over_w, 30, fill="#e7f2ea", stroke=FIELD, sw=1.4, rx=0))
    p.append(rect(bar_x + bar_w - over_w, bar_y, over_w, 30, fill="#ffd9d9", stroke=POS, sw=1.6, rx=0))
    p.append(text(bar_x + (bar_w - over_w) / 2, bar_y + 20, "512 байтів буфера", size=12, color=INK, bold=True))
    p.append(text(bar_x + bar_w - over_w / 2, bar_y + 50, "+24", size=11, color=POS, bold=True))
    p.append(text(bar_x, bar_y + 48, "0", size=10.5, color=MUTED, anchor="start"))
    p.append(text(bar_x + bar_w, bar_y + 48, "536", size=10.5, color=POS, anchor="end"))

    # ── підсумок ──
    p.append(fitbox(60, 402, W - 120, 86,
                    "Корінь — той самий, що в будь-якому переповненні буфера: запис за межі масиву + відсутність перевірки довжини.\ngets() приймає лише адресу буфера, але не його розмір — і фізично не може спинитись на 512-му байті.\nСаме тому gets() згодом викинули зі стандарту C, а перевірка меж стала залізним правилом.",
                    size=11, fill="#fafafa", stroke=INK))

    render(os.path.join(OUT, "fingerd-overflow.svg"), W, H, *p,
           title="Як хробак пробивав fingerd: класичне «smashing the stack»")


# ── three-doors: хробак пробував три двері паралельно ───────────────────────
# Ідея: атрибуція «це баг gets()» неповна — fingerd-переповнення, debug-режим
# sendmail і перебір слабких паролів rsh/rexec — три незалежні шляхи.

def fig_three_doors():
    W, H = 760, 440
    p = []
    cards = [
        (30, "1. fingerd — переповнення буфера", POS, "#fdf4f4",
         "сервіс finger показував, хто залогінений;\nу ньому 512-байтовий буфер читали через\ngets() без меж. Хробак слав 536 байтів —\nі перехоплював керування.\n\nЦе — герой нашої теми."),
        (276, "2. sendmail — режим DEBUG", WARN, "#fffaf0",
         "поштовий сервер sendmail часто лишали\nз увімкненим debug-режимом, що дозволяв\nслати команди прямо в систему.\nНе переповнення — а відчинені «службові\nдвері», які забули замкнути."),
        (522, "3. rsh / rexec — слабкі паролі", NEG, "#eef3fb",
         "довірчі зв'язки між машинами (rsh) +\nперебір паролів за словником на ~900 слів\nі за іменами користувачів.\nЖодної «діри» в коді — лише людська звичка\nставити слабкі паролі й довіряти сусідам."),
    ]
    cw, cy, ch = 208, 86, 250
    for cx, head, col, fill, body in cards:
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(rect(cx, cy, cw, 38, fill=col, stroke=col, sw=0, rx=10))
        p.append(rect(cx, cy + 20, cw, 18, fill=col, stroke=col, sw=0, rx=0))
        hsize = fit_font(head, cw - 16, 12.5, bold=True)
        p.append(text(cx + cw / 2, cy + 25, head, size=hsize, color="#ffffff", bold=True))
        for i, ln in enumerate(body.split("\n")):
            p.append(text(cx + 14, cy + 64 + i * 19, ln, size=10.5, color=INK, anchor="start"))

    p.append(fitbox(30, 360, W - 60, 64,
                    "Пробивши будь-які з трьох дверей, хробак копіював себе на нову машину — і повторював усе звідти.\nСамопоширення без участі людини — ось чому це «хробак» (worm), а не «вірус», що чекає запуску.",
                    size=11, fill="#f1f7f2", stroke=FIELD))

    render(os.path.join(OUT, "three-doors.svg"), W, H, *p,
           title="Хробак не мав «одного трюка»: він пробував три двері одночасно")


# ── honest-scale: ~6000 із ~60000 ≈ 10%, але «10%» — здогад ──────────────────
# Ідея: ліворуч пропорція ураження сіткою клітинок (червоні ≈ 6000/60000), але
# саме «10%» — не вимір, а здогад; праворуч — машини лягали від власного багу
# хробака «1 із 7» (вичерпання ресурсів, DoS), а не від псування даних.

def fig_honest_scale():
    W, H = 760, 500
    p = []

    # ── ЛІВО: сітка хостів ──
    p.append(text(50, 92, "Скільки заразилось (оцінка за ~добу):", size=13, color=INK, bold=True, anchor="start"))
    cols, rows = 20, 5
    cell, gap = 14, 3
    gx0, gy0 = 50, 106
    infected = 10   # перші 10 клітинок із 100 ≈ 10%
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            x = gx0 + c * (cell + gap)
            y = gy0 + r * (cell + gap)
            if idx < infected:
                p.append(rect(x, y, cell, cell, fill="#f3c0bb", stroke=POS, sw=1.1, rx=2))
            else:
                p.append(rect(x, y, cell, cell, fill="#eef1f4", stroke="#e4e4e4", sw=1.1, rx=2))
    p.append(text(50, gy0 + rows * (cell + gap) + 16, "кожна клітинка ≈ 600 хостів · червоні ≈ ~6 000 із ~60 000",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(fitbox(50, gy0 + rows * (cell + gap) + 28, 360, 62,
                    "Навіть «10%» — це здогад, а не вимір:\nхтось припустив ~60 тис. хостів\nі ~10% уражених. (перевірити)",
                    size=10.5, fill="#fff6e6", stroke=WARN))

    # ── ПРАВО: чому лягали ──
    p.append(text(420, 92, "Чому машини «лягали», хоч хробак", size=12.5, color=INK, bold=True, anchor="start"))
    p.append(text(420, 110, "нічого не стирав і не псував:", size=12.5, color=INK, bold=True, anchor="start"))
    p.append(fitbox(420, 122, 290, 150,
                    "Помилка в самому хроб'якові:\nперш ніж заразити машину, він питав —\n«я тут уже є?». Але щоб його не обманули\nфальшивим «так», він однаково ставив\nще одну копію 1 раз із 7.\nКопії множились на одній машині лавиною.",
                    size=10.8, fill="#fdf4f4", stroke=POS))
    p.append(fitbox(420, 284, 290, 96,
                    "Наслідок — не «знищення», а вичерпання:\nпроцесор і пам'ять з'їдали десятки копій,\nмашина переставала відповідати (DoS).\nДані цілі — але працювати неможливо.",
                    size=10.5, fill="#f1f7f2", stroke=FIELD))

    p.append(fitbox(50, 448, W - 100, 38,
                    "Точніше: хробак не «вимкнув» мережу, а перевантажив тисячі машин до повного гальмування за лічені години.",
                    size=11.5, fill="#fafafa", stroke=INK))

    render(os.path.join(OUT, "honest-scale.svg"), W, H, *p,
           title="Чесний масштаб: «зупинив інтернет» — гіпербола")


# ── aftermath: ланцюг наслідків — запуск, гальмування, латки, вирок, CERT ────
# Ідея: п'ять ланок наслідків від ночі 2.11.1988 до заснування CERT/CC; мораль —
# переповнення буфера не музей, а діра, що дожила до сьогоднішнього коду.

def fig_aftermath():
    W, H = 760, 420
    p = []
    steps = [
        ("2 лист. 1988", NEG, "хробака запущено\n(з мережі MIT,\nщоб сховати слід\nКорнелла)"),
        ("За добу", POS, "~6 000 із ~60 000\nхостів загальмовано;\nадмінів підняли\nпо тривозі"),
        ("Дні по тому", WARN, "команди в Берклі\nта MIT розібрали\nкод, випустили\nлатки, відрізали\nдіри"),
        ("1990–91", INK, "Р. Т. Морріс —\nперший засуджений\nза CFAA (1986):\nумовно + штраф"),
        ("Наслідок", FIELD, "засновано CERT/CC\nу Carnegie Mellon —\nкоординація реакції\nна інциденти"),
    ]
    n = len(steps)
    cw, cy, ch = 134, 90, 168
    gap = (W - 2 * 30 - n * cw) / (n - 1)
    for i, (head, col, body) in enumerate(steps):
        cx = 30 + i * (cw + gap)
        p.append(rect(cx, cy, cw, ch, fill="#fafafa", stroke=col, sw=1.8, rx=10))
        p.append(rect(cx, cy, cw, 32, fill=col, stroke=col, sw=0, rx=10))
        p.append(rect(cx, cy + 16, cw, 16, fill=col, stroke=col, sw=0, rx=0))
        p.append(text(cx + cw / 2, cy + 21, head, size=12.5, color="#ffffff", bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(cx + 12, cy + 54 + j * 18, ln, size=10.3, color=INK, anchor="start"))
        if i < n - 1:
            ax = cx + cw
            p.append(arrow(ax + 2, cy + ch / 2, ax + gap - 2, cy + ch / 2, color=col, sw=2.2))

    p.append(fitbox(30, cy + ch + 24, W - 60, 70,
                    "Урок: переповнення буфера — не музейний експонат, а діра, що відчиняє машину чужому коду.\nПеревірка меж і відмова від «функцій без розміру» (як gets()) — пряма спадщина цієї ночі 1988-го.",
                    size=11.5, fill="#f1f7f2", stroke=FIELD))

    render(os.path.join(OUT, "aftermath.svg"), W, H, *p,
           title="Спадок: один баг переповнення змінив культуру безпеки")


if __name__ == "__main__":
    fig_grow_toward()
    fig_buffer_overflow()
    fig_roundup()
    fig_why_hard()
    fig_common_root()
    fig_defenses()
    fig_detect()
    # вставки
    fig_mpu_checkpoint()
    fig_mpu_regions()
    fig_mpu_guard()
    fig_fingerd_overflow()
    fig_three_doors()
    fig_honest_scale()
    fig_aftermath()
    print("OK: figures written to", OUT)
