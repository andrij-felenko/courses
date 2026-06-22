# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── architecture: як з'єднані комірки — паралельно (NOR) чи в низку (NAND) ─────
# Ідея: характер пам'яті виростає просто з топології. У NOR кожна комірка висить
# на лінії біта своїм виходом — її видно з шини напряму (швидке випадкове слово).
# У NAND комірки зшиті послідовно — щільно (дешево, ємно), але доступ сторінками.

def fig_architecture():
    W, H = 760, 430
    frags = []

    # ── NOR (ліва панель) ──
    frags.append(rect(40, 70, 320, 330, fill="#eef0fd", stroke=NEG, sw=2.2, rx=12))
    frags.append(text(200, 98, "NOR — комірки паралельно", size=15, color=NEG, bold=True))
    # лінія біта
    frags.append(line(110, 128, 110, 318, color=INK, sw=2.4))
    frags.append(text(110, 338, "лінія біта", size=11, color=MUTED))
    for i in range(5):
        cy = 144 + i * 36
        frags.append(line(110, cy, 150, cy, color=MUTED, sw=1.4))
        frags.append(circle(166, cy, 13, fill=BG, stroke=NEG, sw=1.6))
        frags.append(text(166, cy + 4, "T", size=11, color=NEG, bold=True))
        frags.append(text(196, cy + 4, "слово %d" % i, size=11, color=MUTED, anchor="start"))
    frags.append(text(200, 358, "кожну комірку видно з шини напряму", size=11, color=INK))
    frags.append(text(200, 380, "→ швидке випадкове читання слова", size=12, color=NEG, bold=True))

    # ── NAND (права панель) ──
    frags.append(rect(400, 70, 320, 330, fill="#fdecea", stroke=POS, sw=2.2, rx=12))
    frags.append(text(560, 98, "NAND — комірки в низку", size=15, color=POS, bold=True))
    frags.append(text(470, 128, "одна низка", size=11, color=MUTED))
    frags.append(line(470, 138, 470, 320, color=INK, sw=2.4))
    for i in range(6):
        cy = 150 + i * 28
        frags.append(rect(458, cy, 24, 20, fill=BG, stroke=POS, sw=1.4, rx=3))
    frags.append(text(500, 248, "комірки", size=11, color=INK, anchor="start"))
    frags.append(text(500, 266, "ланцюгом —", size=11, color=INK, anchor="start"))
    frags.append(text(500, 284, "майже без", size=11, color=INK, anchor="start"))
    frags.append(text(500, 302, "проводів між ними", size=11, color=INK, anchor="start"))
    # стос сторінок
    frags.append(rect(600, 150, 100, 172, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(650, 142, "доступ — сторінками", size=10, color=FIELD, bold=True))
    for i in range(7):
        ly = 168 + i * 21
        frags.append(line(610, ly, 690, ly, color="#dfe7df", sw=1.0))
    frags.append(text(650, 314, "ціла сторінка за раз", size=10, color=MUTED))
    frags.append(text(560, 358, "тісно впаковано → дешево за біт,", size=11, color=POS, bold=True))
    frags.append(text(560, 380, "велика ємність; доступ сторінками", size=11, color=INK))

    render(os.path.join(OUT, "architecture.svg"), W, H, *frags,
           title="NOR проти NAND: як з'єднані комірки — так і відрізняється характер")


# ── xip-vs-storage: дві ролі — виконувати код (XIP) vs зберігати дані ──────────
# Ідея: NOR віддає будь-який байт миттєво → процесор вибирає інструкції прямо з
# неї (XIP), копіювати нікуди. NAND віддає лише сторінки → код спершу в RAM.

def fig_xip_vs_storage():
    W, H = 760, 400
    frags = []

    # ── NOR + XIP ──
    frags.append(rect(40, 64, 320, 310, fill="#eef0fd", stroke=NEG, sw=2.2, rx=12))
    frags.append(text(200, 90, "NOR + XIP (виконання на місці)", size=14, color=NEG, bold=True))
    frags.append(rect(70, 120, 110, 70, fill=BG, stroke=INK, sw=2.2, rx=8))
    frags.append(text(125, 150, "Процесор", size=13, color=INK, bold=True))
    frags.append(text(125, 170, "вибірка", size=10, color=MUTED))
    frags.append(rect(230, 120, 110, 70, fill=BG, stroke=NEG, sw=2.2, rx=8))
    frags.append(text(285, 150, "NOR-флеш", size=13, color=NEG, bold=True))
    frags.append(text(285, 170, "код", size=10, color=MUTED))
    frags.append(line(230, 142, 180, 142, color=NEG, sw=2))
    frags.append(text(205, 134, "адреса", size=9, color=NEG))
    frags.append(line(180, 170, 230, 170, color=FIELD, sw=2))
    frags.append(text(205, 184, "інструкція", size=9, color=FIELD))
    frags.append(text(200, 232, "процесор вибирає команди", size=11, color=INK))
    frags.append(text(200, 250, "прямо з NOR", size=11, color=INK))
    frags.append(text(200, 286, "→ код не треба копіювати", size=12, color=NEG, bold=True))
    frags.append(text(200, 308, "→ але NOR дорога за мегабайт", size=11, color=MUTED))
    frags.append(text(200, 346, "тому в NOR тримають прошивку", size=12, color=NEG, bold=True))

    # ── NAND через буфер у RAM ──
    frags.append(rect(400, 64, 320, 310, fill="#fdecea", stroke=POS, sw=2.2, rx=12))
    frags.append(text(560, 90, "NAND — сховище через буфер у RAM", size=13, color=POS, bold=True))
    frags.append(rect(420, 120, 90, 64, fill=BG, stroke=POS, sw=2.2, rx=8))
    frags.append(text(465, 148, "NAND", size=13, color=POS, bold=True))
    frags.append(text(465, 166, "сторінки", size=9, color=MUTED))
    frags.append(rect(545, 120, 80, 64, fill=BG, stroke=FIELD, sw=2.2, rx=8))
    frags.append(text(585, 148, "RAM", size=13, color=FIELD, bold=True))
    frags.append(text(585, 166, "буфер", size=9, color=MUTED))
    frags.append(rect(655, 120, 55, 64, fill=BG, stroke=INK, sw=2.2, rx=8))
    frags.append(text(682, 156, "ядро", size=12, color=INK, bold=True))
    frags.append(line(510, 152, 545, 152, color=POS, sw=2))
    frags.append(text(527, 142, "копія", size=9, color=POS))
    frags.append(line(625, 152, 655, 152, color=FIELD, sw=2))
    frags.append(text(560, 226, "сторінку спершу копіюють у RAM,", size=11, color=INK))
    frags.append(text(560, 244, "і вже звідти з нею працює ядро", size=11, color=INK))
    frags.append(text(560, 280, "→ виконувати код напряму не можна", size=11, color=POS, bold=True))
    frags.append(text(560, 302, "→ зате дешево й дуже ємно", size=11, color=MUTED))
    frags.append(text(560, 340, "тому в NAND тримають дані:", size=12, color=POS, bold=True))
    frags.append(text(560, 360, "файли, медіа, великі масиви", size=11, color=INK))

    render(os.path.join(OUT, "xip-vs-storage.svg"), W, H, *frags,
           title="Дві ролі: виконувати код на місці (XIP) проти зберігати дані")


# ── decision-table: коротка таблиця рішення NOR проти NAND ─────────────────────
# Ідея: жодна не «краща» — звести властивості пліч-о-пліч, щоб у проєкті швидко
# обрати потрібну флеш. Підсумок одним рядком.

def fig_decision_table():
    W, H = 760, 430
    frags = []
    x0, xN, xA = 50, 380, 590        # ліві краї колонок
    wP, wN, wA = 330, 210, 120       # ширини (властивість / NOR / NAND)
    cN, cA = xN + wN / 2, xA + wA / 2
    top, rh = 60, 44
    rows = [
        ("Випадкове читання слова", "швидке, напряму", "ні — лише сторінками"),
        ("Виконання коду (XIP)",    "так",             "ні (копія в RAM)"),
        ("Ємність за ту саму ціну", "менша",           "велика"),
        ("Швидкість запису/стирання", "повільніша",    "швидша, блоками"),
        ("Дефектні комірки",       "майже немає",      "є завжди (треба ECC)"),
        ("Типове застосування",    "прошивка, код",    "файли, медіа, SSD/SD"),
    ]
    # шапка
    frags.append(rect(x0, top, wP, rh, fill="#eef0f4", stroke=MUTED, sw=1.6, rx=0))
    frags.append(text(x0 + 14, top + 28, "Властивість", size=14, color=INK, anchor="start", bold=True))
    frags.append(rect(xN, top, wN, rh, fill="#eef0f4", stroke=MUTED, sw=1.6, rx=0))
    frags.append(text(cN, top + 28, "NOR", size=14, color=NEG, bold=True))
    frags.append(rect(xA, top, wA, rh, fill="#eef0f4", stroke=MUTED, sw=1.6, rx=0))
    frags.append(text(cA, top + 28, "NAND", size=14, color=POS, bold=True))
    # рядки
    for i, (prop, nor, nand) in enumerate(rows):
        ry = top + rh + i * rh
        shade = BG if i % 2 == 0 else "#fafafa"
        for cx, cw in ((x0, wP), (xN, wN), (xA, wA)):
            frags.append(rect(cx, ry, cw, rh, fill=shade, stroke="#e4e4e4", sw=1.0, rx=0))
        frags.append(text(x0 + 14, ry + 27, prop, size=12, color=INK, anchor="start"))
        frags.append(text(cN, ry + 27, nor, size=11, color=NEG, bold=True))
        frags.append(text(cA, ry + 27, nand, size=11, color=POS, bold=True))
    # зовнішня рамка
    frags.append(rect(x0, top, wP + wN + wA, rh * (len(rows) + 1), fill="none", stroke=MUTED, sw=1.6, rx=0))
    frags.append(text(W / 2, H - 16, "одним рядком: NOR — щоб виконувати, NAND — щоб зберігати",
                      size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, "decision-table.svg"), W, H, *frags,
           title="NOR проти NAND: коротка таблиця рішення")


# ── three-operations: три дії чипа й несиметрична арифметика бітів ─────────────
# Ідея: читати можна будь-де; стирання повертає біти в 1 цілим блоком; запис лише
# ОПУСКАЄ окремі біти 1→0. Підняти біт назад поодинці неможливо — звідси все.

def _bitrow(x, y, bits, n=8, bw=22, bh=24, gap=2):
    out = []
    for i in range(n):
        bx = x + i * (bw + gap)
        b = bits[i] if i < len(bits) else 1
        fill = "#fdecea" if b == 0 else "#eef0fd"
        stroke = POS if b == 0 else NEG
        out.append(rect(bx, y, bw, bh, fill=fill, stroke=stroke, sw=1.3, rx=3))
        out.append(text(bx + bw / 2, y + bh - 7, str(b), size=12, color=stroke, bold=True))
    return "".join(out)


def fig_three_operations():
    W, H = 900, 540
    frags = []

    # три картки-заголовки
    frags.append(rect(30, 78, 270, 150, fill=BG, stroke=FIELD, sw=2.2, rx=12))
    frags.append(text(165, 104, "Читання", size=15, color=FIELD, bold=True))
    frags.append(text(165, 124, "будь-який байт за адресою", size=10, color=MUTED, italic=True))
    frags.append(rect(315, 78, 270, 150, fill=BG, stroke=NEG, sw=2.2, rx=12))
    frags.append(text(450, 104, "Стирання", size=15, color=NEG, bold=True))
    frags.append(text(450, 124, "цілий блок → усі біти в 1", size=10, color=MUTED, italic=True))
    frags.append(rect(600, 78, 270, 150, fill=BG, stroke=POS, sw=2.2, rx=12))
    frags.append(text(735, 104, "Запис", size=15, color=POS, bold=True))
    frags.append(text(735, 124, "у стертому → окремі біти в 0", size=10, color=MUTED, italic=True))

    # читання: ряд клітин, одну дістаємо
    cells = [1, 1, 1, 1, 1, 0, 1, 1]
    for i in range(8):
        bx = 48 + i * 28
        fill = FIELD if i == 5 else "#f4f7f4"
        frags.append(rect(bx, 150, 24, 28, fill="#e9f6ee" if i == 5 else "#f4f7f4",
                          stroke=FIELD if i == 5 else INK, sw=1.6 if i == 5 else 1.2, rx=4))
    frags.append(text(48 + 5 * 28 + 12, 170, "?", size=14, color=FIELD, bold=True))
    frags.append(line(48 + 5 * 28 + 12, 204, 48 + 5 * 28 + 12, 184, color=FIELD, sw=2))
    frags.append(text(165, 216, "точково, миттєво — основа XIP", size=10, color=FIELD, bold=True))

    # стирання: до → 1111...
    frags.append(text(326, 166, "до:", size=10, color=MUTED, anchor="start"))
    frags.append(_bitrow(355, 152, [0, 1, 0, 0, 1, 1, 0, 1], bw=21))
    frags.append(line(450, 182, 450, 198, color=NEG, sw=2.4))
    frags.append(text(450, 196, "стерти", size=9, color=NEG, anchor="start"))
    frags.append(text(326, 220, "по:", size=10, color=MUTED, anchor="start"))
    frags.append(_bitrow(355, 203, [1, 1, 1, 1, 1, 1, 1, 1], bw=21))
    frags.append(text(450, 244, "усе стає 1 — і то блоком, не байтом", size=10, color=INK, bold=True))

    # запис: 1111 → опускаємо окремі в 0
    frags.append(text(611, 166, "є:", size=10, color=MUTED, anchor="start"))
    frags.append(_bitrow(640, 152, [1, 1, 1, 1, 1, 1, 1, 1], bw=21))
    frags.append(line(735, 182, 735, 198, color=POS, sw=2.4))
    frags.append(text(735, 196, "запис", size=9, color=POS, anchor="start"))
    frags.append(text(611, 220, "по:", size=10, color=MUTED, anchor="start"))
    frags.append(_bitrow(640, 203, [0, 1, 1, 0, 1, 0, 0, 1], bw=21))
    frags.append(text(735, 244, "1→0 будь-коли; 0→1 — лише стиранням", size=10, color=INK, bold=True))

    # рамка-висновок (несиметрія)
    frags.append(rect(60, 286, 780, 66, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 312, "головна несиметрія: запис уміє тільки опускати біти 1 → 0.",
                      size=13, color=INK, bold=True))
    frags.append(text(450, 334, "підняти біт 0 → 1 поодинці не можна — це робить лише стирання, цілим блоком.",
                      size=11, color=MUTED, italic=True))

    # рамка-час
    frags.append(rect(60, 366, 780, 92, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 392, "звідси й асиметрія часу: читання — наносекунди-мікросекунди;",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 412, "запис сторінки — частки мілісекунди; стирання блока — десятки-сотні мілісекунд.",
                      size=11, color=INK))
    frags.append(text(450, 434, "читати дешево, стирати дорого — це й визначає, як таким чипом користуються.",
                      size=11, color=MUTED, italic=True))
    frags.append(text(450, 450, "точні числа — за даташитом конкретного чипа; тут важать порядки.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-operations.svg"), W, H, *frags,
           title="Що вміє чип: три дії — і несиметрична арифметика бітів")


# ── granularity: дрібно читаєш/пишеш, крупно стираєш + цикл зміни даних ────────
# Ідея: запис — сторінка (256 Б), стирання — сектор (4 КБ, 16 сторінок). Звідси
# повний цикл «дозвіл → стерти → писати → чекати» і пастка read-modify-write.

def fig_granularity():
    W, H = 900, 560
    frags = []

    # ── ліворуч: вкладена ієрархія ──
    frags.append(rect(40, 86, 380, 250, fill="#fbfbfb", stroke=INK, sw=2, rx=10))
    frags.append(text(52, 108, "чип — 16 МБ (W25Q128)", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(408, 108, "Chip Erase — усе одразу", size=9, color=MUTED, anchor="end", italic=True))
    frags.append(rect(58, 122, 344, 168, fill="#eef0fd", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(68, 142, "блок — 64 КБ (×256)", size=11, color=NEG, anchor="start", bold=True))
    frags.append(text(392, 142, "Block Erase 64K", size=9, color=MUTED, anchor="end", italic=True))
    frags.append(rect(74, 154, 312, 104, fill="#fdf6ee", stroke="#caa24a", sw=1.8, rx=8))
    frags.append(text(84, 173, "сектор — 4 КБ (×16 у блоці)", size=11, color="#8a6a18", anchor="start", bold=True))
    frags.append(text(376, 173, "Sector Erase 4K — найдрібніше", size=9, color="#8a6a18", anchor="end", italic=True))
    for i in range(8):
        bx = 86 + i * 37
        frags.append(rect(bx, 188, 34, 44, fill="#fdecea", stroke=POS, sw=1.3, rx=3))
    frags.append(text(230, 248, "16 сторінок по 256 Б — найдрібніший запис",
                      size=10, color=POS, bold=True))
    frags.append(text(230, 312, "читання — будь-який байт усередині", size=10, color=INK, bold=True))
    frags.append(text(230, 328, "запис — сторінка · стирання — сектор/блок/чип", size=10, color=INK))

    # ── праворуч: цикл зміни даних ──
    frags.append(rect(450, 86, 410, 250, fill=BG, stroke=FIELD, sw=2, rx=12))
    frags.append(text(655, 110, "щоб змінити навіть один байт:", size=13, color=FIELD, bold=True))
    steps = [
        (NEG,  "дозвіл на запис",   "інакше чип мовчки відмовить"),
        (NEG,  "стерти сектор 4 КБ", "усі біти сектора → 1 (десятки мс)"),
        (POS,  "записати сторінки",  "опускаємо біти 1→0, по ≤256 Б"),
        ("#caa24a", "чекати, поки зайнятий", "опитуємо біт Busy; далі — по його скиданню"),
    ]
    for i, (col, head, sub) in enumerate(steps):
        cy = 142 + i * 44
        frags.append(circle(478, cy, 13, fill=BG, stroke=col, sw=2))
        frags.append(text(478, cy + 5, str(i + 1), size=12, color=col, bold=True))
        frags.append(text(500, cy - 3, head, size=11, color=col, anchor="start", bold=True))
        frags.append(text(500, cy + 13, sub, size=9, color=MUTED, anchor="start"))
        if i < 3:
            frags.append(line(478, cy + 14, 478, cy + 30, color=MUTED, sw=1.6))

    # ── рамка read-modify-write ──
    frags.append(rect(60, 352, 780, 86, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 376, "граблі read-modify-write: апаратного «змінити один байт на місці» немає.",
                      size=13, color=INK, bold=True))
    frags.append(text(450, 398, "щоб поправити 1 байт у вже записаному секторі: вичитати сектор у RAM → змінити байт →",
                      size=10, color=MUTED, italic=True))
    frags.append(text(450, 416, "стерти весь сектор 4 КБ → записати назад. один байт коштує стирання й перезапису тисяч.",
                      size=10, color=MUTED, italic=True))
    frags.append(text(450, 432, "тому під часті дрібні зміни (лічильники, журнали) такий чип не годиться — краще EEPROM/FRAM.",
                      size=10, color="#8a6a18", bold=True))

    # ── рамка зносу ──
    frags.append(rect(60, 452, 780, 76, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 476, "і ще наслідок: кожне стирання потроху зношує комірки (тунелювання крізь ізолятор).",
                      size=11, color=INK, bold=True))
    frags.append(text(450, 498, "ресурс — близько 100 000 циклів стирання на сектор, потім сектор «втомлюється».",
                      size=10, color=MUTED, italic=True))
    frags.append(text(450, 516, "тому файлові системи й бутлоадери стирають по черзі різні сектори, щоб не виробити один.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "granularity.svg"), W, H, *frags,
           title="Асиметрія зернистості: дрібно читаєш і пишеш, а стираєш — крупно")


# ── nor-vs-nand-topology: чому NOR читається байтом, а NAND ні (для вставки) ───
# Ідея: різниця у тому, ЯК комірки під'єднані до розрядної лінії — паралельно
# (NOR, прямий доступ → XIP) чи довгим ланцюжком (NAND, лише сторінки).

def fig_topology():
    W, H = 900, 540
    frags = []

    # ── NOR ──
    frags.append(text(130, 88, "NOR", size=17, color=FIELD, bold=True))
    frags.append(text(130, 106, "комірки паралельно", size=10, color=FIELD, bold=True))
    frags.append(line(130, 124, 130, 296, color=INK, sw=2.4))
    frags.append(text(138, 120, "лінія біта", size=9, color=INK, anchor="start"))
    for i in range(3):
        cy = 148 + i * 52
        frags.append(line(130, cy, 176, cy, color=FIELD, sw=2))
        frags.append(rect(176, cy - 13, 44, 26, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=4))
        frags.append(text(198, cy + 4, "комір.", size=9, color=FIELD, bold=True))
        frags.append(line(220, cy, 254, cy, color=MUTED, sw=1.4))
        frags.append(text(258, cy + 4, "лінія слова %d" % i, size=9, color=MUTED, anchor="start"))
    frags.append(text(160, 320, "кожна має прямий доступ до лінії", size=10, color=INK, bold=True))
    frags.append(text(160, 336, "→ читаємо будь-яку поодинці, за наносекунди", size=10, color=FIELD, bold=True))

    # роздільник
    frags.append(line(460, 120, 460, 348, color="#e4e4e4", sw=1.4, dash="4,5"))

    # ── NAND ──
    frags.append(text(610, 88, "NAND", size=17, color=POS, bold=True))
    frags.append(text(610, 106, "комірки в ланцюжку", size=10, color=POS, bold=True))
    frags.append(line(610, 124, 610, 146, color=INK, sw=2.4))
    frags.append(text(618, 122, "лінія біта", size=9, color=INK, anchor="start"))
    for i in range(4):
        cy = 146 + i * 46
        frags.append(rect(590, cy, 40, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
        frags.append(text(610, cy + 19, "к%d" % i, size=10, color=POS, bold=True))
        frags.append(line(610, cy + 30, 610, cy + 46, color=INK, sw=2.4))
    frags.append(text(640, 166, "усі ввімкнені", size=9, color=MUTED, anchor="start"))
    frags.append(text(640, 180, "послідовно", size=9, color=MUTED, anchor="start"))
    frags.append(text(610, 360, "щоб дотягтись до однієї — струм іде крізь сусідів", size=10, color=INK, bold=True))
    frags.append(text(610, 376, "→ читати можна лише цілою сторінкою, не байтом", size=10, color=POS, bold=True))

    # ── міні-таблиця наслідків ──
    frags.append(rect(60, 392, 780, 70, fill=BG, stroke=INK, sw=1.6, rx=10))
    frags.append(text(210, 410, "властивість", size=10, color=MUTED, bold=True))
    frags.append(text(500, 410, "NOR (наш W25Q)", size=10, color=FIELD, bold=True))
    frags.append(text(740, 410, "NAND", size=10, color=POS, bold=True))
    rows = [
        ("Випадкове читання байта", "так — будь-де", "ні — лише сторінками"),
        ("Щільність / ціна за байт", "нижча, дорожча", "вища, дешевша"),
        ("Де доречна", "код, малі прошивки", "масові дані: SD, eMMC, SSD"),
    ]
    for i, (p, n, a) in enumerate(rows):
        ry = 428 + i * 16
        frags.append(text(72, ry, p, size=9, color=INK, anchor="start"))
        frags.append(text(500, ry, n, size=9, color=FIELD, anchor="middle", bold=True))
        frags.append(text(740, ry, a, size=9, color=POS, anchor="middle", bold=True))
    frags.append(line(370, 400, 370, 456, color="#e4e4e4", sw=1))
    frags.append(line(635, 400, 635, 456, color="#e4e4e4", sw=1))

    # ── підсумок ──
    frags.append(rect(60, 476, 780, 50, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 498, "W25Q-клас — це NOR: її козир — читати будь-який байт, тож код виконують прямо з неї (XIP).",
                      size=11, color=INK, bold=True))
    frags.append(text(450, 518, "платня — менший об'єм; коли байтів дуже багато, беруть NAND і миряться з посторінковим доступом.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "nor-vs-nand-topology.svg"), W, H, *frags,
           title="Чому NOR читається побайтово (і годиться для XIP), а NAND — ні")


if __name__ == "__main__":
    fig_architecture()
    fig_xip_vs_storage()
    fig_decision_table()
    fig_three_operations()
    fig_granularity()
    fig_topology()
    print("OK: figs written to", OUT)
