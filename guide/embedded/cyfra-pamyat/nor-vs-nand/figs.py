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


# ══════════════════════════════════════════════════════════════════════════════
# ФІГУРИ ДЕТАЛЬНОЇ СТАТТІ (nor-vs-nand-d.md) — глибші за базові
# ══════════════════════════════════════════════════════════════════════════════

# ── che-vs-fn: два механізми запису — і чому саме вони розводять NOR і NAND ────
# Ідея: NOR програмує гарячими електронами (CHE) — потрібен великий струм каналу,
# тому клітину не поставиш у щільну низку. NAND і пише, і стирає тунелюванням
# Фаулера–Нордгайма (FN) — струм крихітний, тому клітини можна зшити в ланцюг.
# Ця різниця в ефективності (5–6 порядків) — корінь усіх решти відмінностей.

def fig_che_vs_fn():
    W, H = 900, 560
    frags = []

    # ── ЛІВА панель: NOR — channel hot electron ──
    frags.append(rect(34, 66, 410, 300, fill="#eef0fd", stroke=NEG, sw=2.2, rx=12))
    frags.append(text(239, 92, "NOR: запис гарячими електронами (CHE)", size=13, color=NEG, bold=True))
    # структура клітини: витік — канал — стік, зверху плаваючий затвор
    sy = 250
    frags.append(rect(70, sy, 70, 30, fill="#dfe6fb", stroke=NEG, sw=1.6, rx=4))       # витік
    frags.append(text(105, sy + 19, "витік", size=9, color=NEG, bold=True))
    frags.append(rect(140, sy, 200, 30, fill="#f4f7f4", stroke=MUTED, sw=1.4, rx=0))    # канал
    frags.append(text(240, sy + 19, "канал (сильний струм)", size=9, color=MUTED))
    frags.append(rect(340, sy, 70, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=4))       # стік
    frags.append(text(375, sy + 19, "стік", size=9, color=POS, bold=True))
    # плаваючий затвор
    frags.append(rect(150, sy - 74, 180, 26, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=5))
    frags.append(text(240, sy - 57, "плаваючий затвор", size=10, color="#8a6a18", bold=True))
    frags.append(text(240, sy - 84, "керівний затвор (висока напруга)", size=9, color=INK))
    frags.append(line(150, sy - 90, 330, sy - 90, color=INK, sw=2))
    # гарячий електрон стрибає вгору
    frags.append(line(300, sy, 300, sy - 48, color=POS, sw=2.4))
    frags.append(text(300, sy - 44, "▲", size=12, color=POS))
    frags.append(text(360, sy - 20, "гарячий e⁻", size=9, color=POS, anchor="start", bold=True))
    frags.append(text(240, sy + 58, "розігнати e⁻ в каналі → закинути на затвор", size=10, color=INK, bold=True))
    frags.append(text(240, sy + 76, "коштує великого струму (десятки мкА на клітину)", size=9, color=MUTED, italic=True))

    # ── ПРАВА панель: NAND — Fowler–Nordheim ──
    frags.append(rect(456, 66, 410, 300, fill="#fdecea", stroke=POS, sw=2.2, rx=12))
    frags.append(text(661, 92, "NAND: запис і стирання тунелюванням (FN)", size=13, color=POS, bold=True))
    frags.append(rect(560, sy, 200, 30, fill="#f4f7f4", stroke=MUTED, sw=1.4, rx=0))
    frags.append(text(660, sy + 19, "канал (майже без струму)", size=9, color=MUTED))
    frags.append(rect(570, sy - 74, 180, 26, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=5))
    frags.append(text(660, sy - 57, "плаваючий затвор", size=10, color="#8a6a18", bold=True))
    frags.append(text(660, sy - 84, "керівний затвор (дуже висока напруга)", size=9, color=INK))
    frags.append(line(570, sy - 90, 750, sy - 90, color=INK, sw=2))
    # електрон тунелює крізь тонкий ізолятор (пунктир — крізь бар'єр)
    frags.append(line(660, sy, 660, sy - 48, color=FIELD, sw=2.4, dash="3,3"))
    frags.append(text(660, sy - 44, "▲", size=12, color=FIELD))
    frags.append(text(770, sy - 20, "e⁻ тунелює", size=9, color=FIELD, anchor="start", bold=True))
    frags.append(text(660, sy + 58, "сильне поле «продавлює» e⁻ крізь тонкий ізолятор", size=10, color=INK, bold=True))
    frags.append(text(660, sy + 76, "струм крихітний → клітину можна зшити в низку", size=9, color=POS, italic=True))

    # ── нижня рамка-висновок: ефективність і наслідок ──
    frags.append(rect(60, 388, 780, 76, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 412, "FN-тунелювання ефективніше за гарячі електрони приблизно в 100 000 – 1 000 000 разів за струмом.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 434, "тому NAND живить хоч тисячі клітин у ланцюгу тим самим мізерним струмом — звідси її щільність.",
                      size=11, color=MUTED, italic=True))
    frags.append(text(450, 452, "NOR же мусить гнати струм крізь кожну клітину поодинці — багато проводів, менша щільність, але прямий доступ.",
                      size=10, color=NEG, bold=True))

    frags.append(rect(60, 478, 780, 52, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 500, "корінь усього: спосіб ЗАКИНУТИ заряд визначає, чи можна ставити клітини в щільну низку.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 520, "звідси вже випливають і топологія, і доступ, і ціна за біт, і хто для коду, а хто для даних.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "che-vs-fn.svg"), W, H, *frags,
           title="Два механізми запису — і чому саме вони розводять NOR та NAND")


# ── bit-levels: SLC/MLC/TLC/QLC — скільки рівнів заряду й ціна за щільність ────
# Ідея: більше бітів у клітині = більше рівнів напруги (2/4/8/16), тісніші вікна
# між ними → менший запас на витік заряду → нижча витривалість і збереження.

def _vt_curve(x0, y0, w, centers, sigma, color, h=34):
    """Гаусоподібні «горби» розподілу порогової напруги на осі x0..x0+w."""
    import math
    out = []
    pts = []
    N = 120
    for i in range(N + 1):
        x = x0 + w * i / N
        v = 0.0
        for c in centers:
            cx = x0 + w * c
            v += math.exp(-((x - cx) ** 2) / (2 * (w * sigma) ** 2))
        y = y0 - h * min(v, 1.0)
        pts.append("%.1f,%.1f" % (x, y))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
               % (" ".join(pts), color))
    return "".join(out)


def fig_bit_levels():
    W, H = 900, 560
    frags = []
    rows = [
        ("SLC", "1 біт", "2 рівні", [0.25, 0.75], 0.055, "~100 000 циклів"),
        ("MLC", "2 біти", "4 рівні", [0.14, 0.38, 0.62, 0.86], 0.030, "~3 000 – 10 000"),
        ("TLC", "3 біти", "8 рівнів", [0.07 + 0.86 * k / 7 for k in range(8)], 0.017, "~1 000 – 3 000"),
        ("QLC", "4 біти", "16 рівнів", [0.05 + 0.9 * k / 15 for k in range(16)], 0.010, "~100 – 1 000"),
    ]
    x0 = 250
    axw = 470
    top = 70
    rh = 108
    for i, (name, bits, lvls, centers, sig, endur) in enumerate(rows):
        by = top + i * rh
        base = by + 66
        col = [NEG, FIELD, "#8a6a18", POS][i]
        # мітка ліворуч
        frags.append(text(60, by + 34, name, size=17, color=col, anchor="start", bold=True))
        frags.append(text(60, by + 52, "%s / клітину" % bits, size=10, color=MUTED, anchor="start"))
        frags.append(text(60, by + 68, lvls, size=10, color=INK, anchor="start", bold=True))
        # вісь напруги
        frags.append(line(x0, base, x0 + axw, base, color=INK, sw=1.4))
        # горби розподілу
        frags.append(_vt_curve(x0, base, axw, centers, sig, col))
        # витривалість праворуч
        frags.append(text(x0 + axw + 12, by + 42, endur, size=11, color=col, anchor="start", bold=True))
        frags.append(text(x0 + axw + 12, by + 58, "стирань", size=9, color=MUTED, anchor="start"))
    # підписи осей (внизу під останнім рядком)
    frags.append(text(x0, top + 4 * rh - 20, "порогова напруга Vₜ (заряд на затворі) →", size=10, color=MUTED, anchor="start", italic=True))
    frags.append(text(x0 + axw + 12, top - 6, "витривалість", size=10, color=MUTED, anchor="start", bold=True))

    # рамка-висновок
    frags.append(rect(60, top + 4 * rh - 2, 780, 66, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, top + 4 * rh + 22,
                      "що більше бітів у клітині — то тісніші «горби» й вужчі проміжки між ними.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, top + 4 * rh + 42,
                      "найменший витік заряду вже штовхає клітину в сусідній рівень → менше циклів і гірше збереження.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "bit-levels.svg"), W, H, *frags,
           title="Скільки бітів у клітині: рівні заряду проти витривалості")


# ── nand-org: повна ієрархія NAND і асиметрія програмування/стирання ──────────
# Ідея: клітина → сторінка (одиниця читання/запису) → блок (одиниця стирання) →
# площина/кристал. Програмують сторінками ПО ПОРЯДКУ, стирають цілим блоком.
# Read-disturb: часте читання сусідів псує клітину.

def fig_nand_org():
    W, H = 900, 570
    frags = []

    # ── ліворуч: вкладена ієрархія NAND ──
    frags.append(rect(34, 74, 420, 300, fill="#fbfbfb", stroke=INK, sw=2, rx=10))
    frags.append(text(46, 96, "кристал (die)", size=11, color=INK, anchor="start", bold=True))
    frags.append(rect(48, 106, 392, 254, fill="#f6f7fb", stroke=MUTED, sw=1.4, rx=8))
    frags.append(text(60, 126, "блок — одиниця СТИРАННЯ (сотні КБ – МБ)", size=10, color=NEG, anchor="start", bold=True))
    frags.append(rect(62, 136, 364, 210, fill="#eef0fd", stroke=NEG, sw=1.6, rx=6))
    # сторінки в блоці
    for i in range(6):
        py = 152 + i * 30
        pfill = "#dfe6fb" if i < 3 else BG
        frags.append(rect(80, py, 328, 22, fill=pfill, stroke=POS if i == 3 else MUTED, sw=1.6 if i == 3 else 1.0, rx=3))
        lbl = "сторінка %d — писати/читати" % i
        frags.append(text(88, py + 15, lbl, size=9, color=INK if i < 3 else MUTED, anchor="start"))
    frags.append(text(244, 340, "заповнені ↑   ·   ще стерті (0xFF) ↓", size=9, color=MUTED))
    frags.append(text(430, 152, "◀ пишуться", size=8, color=POS, anchor="end"))
    frags.append(text(430, 165, "по порядку", size=8, color=POS, anchor="end"))

    # ── праворуч: асиметрія програм/стирання ──
    frags.append(rect(474, 74, 392, 300, fill=BG, stroke=FIELD, sw=2, rx=12))
    frags.append(text(670, 98, "три зернистості — і залізне правило", size=13, color=FIELD, bold=True))
    items = [
        (FIELD, "ЧИТАННЯ", "сторінка — найдрібніше, що можна дістати"),
        (POS,   "ЗАПИС (program)", "сторінка; лише 1→0; тільки в стерте; по порядку в блоці"),
        (NEG,   "СТИРАННЯ (erase)", "цілий БЛОК одразу; 0→1 гуртом; сотні клітин-сторінок"),
    ]
    for i, (col, head, sub) in enumerate(items):
        cy = 138 + i * 56
        frags.append(rect(494, cy, 26, 26, fill=BG, stroke=col, sw=2, rx=5))
        frags.append(text(507, cy + 18, "RWE"[i], size=13, color=col, bold=True))
        frags.append(text(532, cy + 11, head, size=12, color=col, anchor="start", bold=True))
        frags.append(text(532, cy + 28, sub, size=9, color=MUTED, anchor="start"))
    frags.append(text(670, 322, "не можна стерти одну сторінку — лише весь блок разом.", size=10, color=INK, bold=True))
    frags.append(text(670, 340, "звідси й потреба переносити живі сторінки перед стиранням.", size=9, color=MUTED, italic=True))

    # ── рамка read-disturb ──
    frags.append(rect(60, 394, 780, 74, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 418, "прихована пастка read-disturb: щоб прочитати одну сторінку, сусідні клітини в ланцюгу тримають відкритими.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 440, "кожне таке відкриття потроху підкидає їм заряд; після сотень тисяч читань сусід може «перекинутися».",
                      size=10, color=MUTED, italic=True))
    frags.append(text(450, 458, "тому контролер веде лік читань блока й вчасно переписує його на свіже місце — цього в NOR немає.",
                      size=10, color="#8a6a18", bold=True))

    # ── рамка: чому це і є «оптовий» характер ──
    frags.append(rect(60, 482, 780, 52, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 504, "усе це — плата за щільність: дрібно дістати не можна, зате бітів дуже багато й дуже дешево.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 524, "керувати цим вручну майже нереально — тому NAND майже завжди йде в парі з розумним контролером.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "nand-org.svg"), W, H, *frags,
           title="Організація NAND: сторінка читає-пише, блок стирає — і що з цього випливає")


# ── xip-fetch: чому для КОДУ важлива саме затримка випадкового читання ────────
# Ідея: процесор на кожен крок робить випадкову вибірку інструкції. NOR віддає
# слово за наносекунди-десятки нс → можна виконувати з неї. NAND має велику
# латентність доступу до сторінки → «на місці» не виконати, лише через RAM.

def fig_xip_fetch():
    W, H = 900, 520
    frags = []

    # ── верх: цикл вибірки процесора ──
    frags.append(text(450, 62, "процесор на КОЖЕН крок вибирає інструкцію за (часто випадковою) адресою", size=12, color=INK, bold=True))
    stages = ["вибірка", "декод", "виконання"]
    for i, s in enumerate(stages):
        bx = 300 + i * 110
        frags.append(rect(bx, 76, 96, 40, fill=BG, stroke=INK if i else FIELD, sw=2.2 if i == 0 else 1.6, rx=8))
        frags.append(text(bx + 48, 101, s, size=11, color=FIELD if i == 0 else INK, bold=(i == 0)))
        if i < 2:
            frags.append(line(bx + 96, 96, bx + 110, 96, color=MUTED, sw=1.6))
    frags.append(text(348, 135, "адреса стрибає за лічильником команд — доступ РІДКО послідовний", size=10, color=MUTED, italic=True))

    # ── дві доріжки-часу: NOR і NAND ──
    def track(y, name, col, lat_txt, blocks, note):
        out = []
        out.append(text(60, y + 6, name, size=13, color=col, anchor="start", bold=True))
        out.append(text(60, y + 24, lat_txt, size=9, color=MUTED, anchor="start"))
        tx = 250
        for i, (w, lbl, bcol) in enumerate(blocks):
            out.append(rect(tx, y - 12, w, 30, fill=bcol, stroke=col, sw=1.4, rx=4))
            out.append(text(tx + w / 2, y + 8, lbl, size=9, color=INK, bold=True))
            tx += w + 6
        out.append(text(tx + 8, y + 8, note, size=9, color=col, anchor="start", bold=True))
        return "".join(out)

    frags.append(track(200, "NOR", NEG,
                       "затримка випадкового читання — десятки наносекунд",
                       [(120, "адреса→слово", "#eef0fd")],
                       "→ слово готове одразу: виконуй прямо з неї (XIP)"))

    frags.append(track(270, "NAND", POS,
                       "латентність доступу до сторінки — десятки МІКРОсекунд",
                       [(150, "адреса сторінки", "#fdecea"),
                        (170, "чекати завантаження сторінки", "#fdecea"),
                        (90, "потік байтів", "#fdecea")],
                       ""))
    frags.append(text(250, 306, "→ поки сторінка не в буфері, жодного слова; тисячі тактів простою на кожну випадкову адресу",
                      size=9, color=POS, anchor="start", bold=True))

    # ── рамка: тому код і дані розводять ──
    frags.append(rect(60, 336, 780, 76, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 360, "для коду важить НЕ пропускна здатність, а затримка ВИПАДКОВОГО читання — скільки чекати одне слово.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 382, "NOR дає слово за десятки нс → процесор годується прямо з неї. NAND змушує спершу підняти сторінку в RAM.",
                      size=10, color=MUTED, italic=True))
    frags.append(text(450, 400, "тому «NAND-система» тримає крихітний завантажувач у NOR-подібній пам'яті — інакше нема звідки взяти першу команду.",
                      size=10, color="#8a6a18", bold=True))

    # ── рамка: а для даних навпаки ──
    frags.append(rect(60, 426, 780, 54, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 450, "а для масових даних важить ПРОПУСКНА здатність і ціна за біт — і тут перемагає NAND зі своїми сторінками.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 470, "великий блок вигідно лити суцільним потоком; випадковий доступ до окремого байта тут майже не потрібен.",
                      size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "xip-fetch.svg"), W, H, *frags,
           title="Для коду важить затримка випадкового читання, для даних — пропускна здатність")


# ══════════════════════════════════════════════════════════════════════════════
# ФІГУРА ІСТОРИЧНОЇ ВСТАВКИ (hist-flash-invention.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── flash-timeline: глухий кут EPROM/EEPROM → розвилка → хронологія винаходу ───
# Ідея: показати, що NOR і NAND — дві відповіді на одне питання (як закинути
# заряд), і три різні дати на кожен рід: ідея (патент) / презентація IEDM /
# комерційний продукт. Ліворуч — що бентежило, праворуч — стрічка часу з двома
# гілками (гарячі електрони → NOR, тунелювання → NAND).

def fig_flash_timeline():
    W, H = 900, 560
    frags = []

    # ── ліва панель: глухий кут до флеші ──
    frags.append(rect(30, 62, 250, 300, fill="#fbfbfb", stroke=INK, sw=2, rx=10))
    frags.append(text(155, 86, "до флеші: глухий кут", size=13, color=INK, bold=True))
    frags.append(rect(48, 104, 214, 110, fill="#eef0fd", stroke=NEG, sw=1.6, rx=8))
    frags.append(text(155, 126, "EPROM", size=13, color=NEG, bold=True))
    frags.append(text(155, 146, "дешева, однотранзисторна,", size=9, color=INK))
    frags.append(text(155, 162, "але стирати — тільки", size=9, color=INK))
    frags.append(text(155, 178, "ультрафіолетом, вийнявши чип", size=9, color=INK))
    frags.append(text(155, 200, "→ не оновиш у пристрої", size=10, color=NEG, bold=True))
    frags.append(rect(48, 228, 214, 120, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    frags.append(text(155, 250, "EEPROM", size=13, color=POS, bold=True))
    frags.append(text(155, 270, "стирати можна електрикою,", size=9, color=INK))
    frags.append(text(155, 286, "побайтово — зручно,", size=9, color=INK))
    frags.append(text(155, 302, "але ДВА транзистори на комірку", size=9, color=INK))
    frags.append(text(155, 324, "→ вдвічі дорожче за біт,", size=10, color=POS, bold=True))
    frags.append(text(155, 340, "не масштабується", size=10, color=POS, bold=True))

    # стрілка «вихід»
    frags.append(text(300, 200, "рішення:", size=10, color=FIELD, anchor="middle", bold=True))
    frags.append(text(300, 216, "1 комірка", size=10, color=FIELD, anchor="middle", bold=True))
    frags.append(text(300, 232, "= 1 транзистор", size=10, color=FIELD, anchor="middle", bold=True))
    frags.append(line(282, 250, 320, 250, color=FIELD, sw=2.4))
    frags.append(text(320, 254, "▶", size=12, color=FIELD))

    # ── права панель: вертикальна стрічка часу ──
    ax = 400                       # вісь часу
    top, bot = 84, 350
    frags.append(line(ax, top, ax, bot, color=INK, sw=2.4))
    frags.append(text(ax, top - 14, "час", size=10, color=MUTED))

    # події: (y, рік, заголовок, підпис, колір, гілка) — гілка: 'C'=центр,'L'=NOR,'R'=NAND
    events = [
        (110, "1980", "патент: однотранзисторна комірка", "ІДЕЯ на папері (Масуока)", INK, "C"),
        (170, "IEDM 1984", "презентація NOR", "гарячі електрони (CHE) → паралельно", NEG, "L"),
        (238, "1988", "перший комерційний NOR-чип", "його вивела на ринок Intel", NEG, "L"),
        (300, "IEDM 1987", "презентація щільної NAND", "тунелювання (FN) → в низку · 4-Мбіт", POS, "R"),
        (348, "~1989", "комерційна NAND", "серійний чип від Toshiba", POS, "R"),
    ]
    for (y, yr, head, sub, col, side) in events:
        frags.append(circle(ax, y, 7, fill=BG, stroke=col, sw=2.4))
        if side == "L":
            frags.append(line(ax - 7, y, ax - 34, y, color=col, sw=1.6))
            frags.append(text(ax - 40, y - 4, yr, size=11, color=col, anchor="end", bold=True))
            frags.append(text(ax - 40, y + 11, head, size=10, color=INK, anchor="end", bold=True))
            frags.append(text(ax - 40, y + 25, sub, size=8, color=MUTED, anchor="end", italic=True))
        elif side == "R":
            frags.append(line(ax + 7, y, ax + 34, y, color=col, sw=1.6))
            frags.append(text(ax + 40, y - 4, yr, size=11, color=col, anchor="start", bold=True))
            frags.append(text(ax + 40, y + 11, head, size=10, color=INK, anchor="start", bold=True))
            frags.append(text(ax + 40, y + 25, sub, size=8, color=MUTED, anchor="start", italic=True))
        else:
            frags.append(text(ax + 40, y - 4, yr, size=11, color=col, anchor="start", bold=True))
            frags.append(text(ax + 40, y + 11, head, size=10, color=INK, anchor="start", bold=True))
            frags.append(text(ax + 40, y + 25, sub, size=8, color=MUTED, anchor="start", italic=True))

    # підписи гілок
    frags.append(text(ax - 150, top + 4, "◀ NOR (для коду)", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(ax + 150, top + 4, "NAND (для даних) ▶", size=11, color=POS, anchor="middle", bold=True))

    # ── нижня рамка: розвилка одним рядком ──
    frags.append(rect(60, 388, 780, 76, fill="#fff8e8", stroke="#caa24a", sw=1.8, rx=10))
    frags.append(text(450, 412, "розвилка вросла у фізику: спосіб ЗАКИНУТИ заряд визначив топологію, а та — рід флеші.",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 434, "гарячі електрони потребують великого струму → комірки нарізно (NOR); тунелювання майже без струму → в низку (NAND).",
                      size=9, color=MUTED, italic=True))
    frags.append(text(450, 452, "різниця струму — близько 100 000 – 1 000 000 разів; звідси й уся несумісність двох топологій.",
                      size=9, color="#8a6a18", bold=True))

    # ── рамка: три різні дати ──
    frags.append(rect(60, 478, 780, 52, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(450, 500, "три різні досягнення — три різні дати: ІДЕЯ (патент) · ПРЕЗЕНТАЦІЯ (IEDM) · ПРОДУКТ (ринок).",
                      size=12, color=INK, bold=True))
    frags.append(text(450, 520, "винайшли флеш у Toshiba (Масуока з командою); першу NOR на ринок вивела Intel — це різні заслуги різних людей.",
                      size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "flash-timeline.svg"), W, H, *frags,
           title="Народження флеші: глухий кут EPROM/EEPROM → розвилка CHE/FN → NOR і NAND")


if __name__ == "__main__":
    fig_architecture()
    fig_xip_vs_storage()
    fig_decision_table()
    fig_three_operations()
    fig_granularity()
    fig_topology()
    # детальна стаття:
    fig_che_vs_fn()
    fig_bit_levels()
    fig_nand_org()
    fig_xip_fetch()
    # історична вставка:
    fig_flash_timeline()
    print("OK: figs written to", OUT)
