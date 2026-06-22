# -*- coding: utf-8 -*-
"""Фігури до теми «Біти й порядок байтів» (bits, bytes, words, endianness)
та її вставок (comp-sensor-byte-order, proj-serialization).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки на базі палітри svgkit (заливки під кольорові байти)
RED_BG   = "#fdecea"   # старший байт / «гаряче»
BLUE_BG  = "#eaf0fd"   # молодший байт / «холодне»
GREEN_BG = "#eaf6ee"   # вологість / висновок
AMBER    = "#b8860b"   # третій колір (теплий, не зелений/червоний)
AMBER_BG = "#fdf6e3"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ════════════════ СТАТТЯ ═════════════════════════════════════════════════════

# ── 1. Сходинки групування: біт → півбайт → байт → слово ─────────────────────
def fig_hierarchy():
    W, H = 900, 470
    f = []
    cell = 46
    x0 = 250

    def bitcell(x, y, val):
        c = POS if val else NEG
        bg = RED_BG if val else BLUE_BG
        return (rect(x, y, cell, cell, fill=bg, stroke=c, sw=2, rx=6) +
                text(x + cell / 2, y + cell * 0.66, str(val), size=17, color=c, bold=True))

    # біт
    f.append(text(60, 108, "біт (bit)", size=14, color=INK, anchor="start", bold=True))
    f.append(text(60, 126, "1 розряд", size=10, color=MUTED, anchor="start"))
    f.append(bitcell(x0, 88, 1))
    f.append(text(316, 106, "одне з двох значень: 0 або 1", size=12, color=INK, anchor="start", bold=True))
    f.append(text(316, 126, "найменша одиниця інформації", size=10, color=MUTED, anchor="start"))

    # півбайт
    f.append(text(60, 190, "півбайт (nibble)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(60, 208, "4 біти", size=10, color=MUTED, anchor="start"))
    for i, v in enumerate([1, 0, 1, 0]):
        f.append(bitcell(x0 + i * (cell + 4), 168, v))
    f.append(text(466, 188, "= 1 hex-цифра", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(466, 208, "16 значень · 0…F", size=10, color=MUTED, anchor="start"))

    # байт
    f.append(text(60, 286, "байт (byte)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(60, 304, "8 бітів", size=10, color=MUTED, anchor="start"))
    for i, v in enumerate([1, 0, 1, 1, 0, 1, 1, 0]):
        f.append(bitcell(x0 + i * (cell + 4), 258, v))
    f.append(text(x0 + cell / 2, 248, "MSB", size=10, color=AMBER, bold=True))
    f.append(text(x0 + cell / 2, 322, "старший", size=9, color=MUTED))
    lastx = x0 + 7 * (cell + 4)
    f.append(text(lastx + cell / 2, 248, "LSB", size=10, color=AMBER, bold=True))
    f.append(text(lastx + cell / 2, 322, "молодший", size=9, color=MUTED))
    f.append(text(lastx + cell + 22, 278, "256 значень = 2 hex-цифри", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(lastx + cell + 22, 298, "стандартна «порція» пам'яті", size=10, color=MUTED, anchor="start"))

    # слово
    f.append(text(60, 392, "слово (word)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(60, 410, "машинне", size=10, color=MUTED, anchor="start"))
    for i in range(4):
        wx = x0 + i * 100
        f.append(rect(wx, 367, 92, 46, fill="#eef4ff", stroke=INK, sw=1.8, rx=6))
        f.append(text(wx + 46, 395, "байт", size=11, color=INK, bold=True))
    f.append(text(x0 + 400 + 12, 384, "16 / 32 / 64 біти", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(x0 + 400 + 12, 404, "залежить від машини", size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, 452,
                  "Кожна сходинка — просто більше бітів разом. Біт і байт сталі; «слово» — стільки, скільки машина бере за раз.",
                  size=11, color=INK, bold=True))
    out("hierarchy.svg", W, H, *f,
        title="Сходинки групування: біт → півбайт → байт → слово")


# ── 2. Розмір слова: 8/16/32/64 біти ─────────────────────────────────────────
def fig_wordsize():
    W, H = 900, 470
    f = []
    rows = [
        ("8 біт", 1, POS, RED_BG, "беззнаковий діапазон: 0…255", "приклад: AVR (Arduino Uno), 8051"),
        ("16 біт", 2, AMBER, AMBER_BG, "беззнаковий діапазон: 0…65 535", "приклад: MSP430, 8086"),
        ("32 біти", 4, FIELD, GREEN_BG, "беззнаковий діапазон: 0…~4.29 млрд", "приклад: ARM Cortex-M, ESP32"),
        ("64 біти", 8, NEG, BLUE_BG, "беззнаковий діапазон: 0…~1.8·10¹⁹", "приклад: x86-64, ARM64 (ПК, телефон)"),
    ]
    y = 104
    cell = 36
    for label, n, col, bg, rng, ex in rows:
        f.append(text(128, y + 20, label, size=14, color=col, anchor="end", bold=True))
        for i in range(n):
            f.append(rect(150 + i * (cell + 4), y, cell, cell + 4, fill=bg, stroke=col, sw=1.8, rx=5))
        f.append(text(490, y + 14, rng, size=12.5, color=INK, anchor="start", bold=True))
        f.append(text(490, y + 34, ex, size=10, color=MUTED, anchor="start"))
        y += 74
    f.append(text(150, y - 16, "(кожен квадрат — байт; ширше слово = більше байтів за раз = більші числа)",
                  size=10, color=MUTED, anchor="start", italic=True))
    f.append(rect(60, 422, 780, 34, fill=AMBER_BG, stroke=AMBER, sw=1.4, rx=8))
    f.append(text(W / 2, 444,
                  "Увага: у деяких системах (Windows API) «word» жорстко = 16 біт, dword = 32, qword = 64 — незалежно від машини.",
                  size=11, color=INK, bold=True))
    out("wordsize.svg", W, H, *f,
        title="Розмір слова: 8, 16, 32, 64 біти — скільки машина бере за раз")


# ── 3. Порядок байтів: big-endian vs little-endian ───────────────────────────
def fig_endianness():
    W, H = 900, 500
    f = []
    byts = [("0x12", POS, RED_BG), ("0x34", AMBER, AMBER_BG),
            ("0x56", FIELD, GREEN_BG), ("0x78", NEG, BLUE_BG)]
    # число вгорі
    f.append(text(238, 118, "число", size=13, color=INK, anchor="end", bold=True))
    f.append(mono(238, 138, "0x12345678", size=14, color=INK, anchor="end", bold=True))
    x = 258
    for lbl, col, bg in byts:
        f.append(rect(x, 92, 104, 46, fill=bg, stroke=col, sw=2, rx=6))
        f.append(mono(x + 52, 122, lbl, size=16, color=col, anchor="middle", bold=True))
        x += 120
    f.append(text(310, 162, "старший байт (MSB)", size=10, color=MUTED))
    f.append(text(670, 162, "молодший байт (LSB)", size=10, color=MUTED))

    def memrow(y, order):
        for i, idx in enumerate(order):
            lbl, col, bg = byts[idx]
            cx = 360 + i * 120
            f.append(rect(cx, y, 92, 52, fill=BG, stroke=INK, sw=1.6, rx=6))
            f.append(rect(cx + 5, y + 5, 82, 42, fill=bg, stroke=col, sw=1.6, rx=4))
            f.append(mono(cx + 46, y + 32, lbl, size=16, color=col, anchor="middle", bold=True))
            f.append(text(cx + 46, y - 8, "0x0%d" % i, size=11, color=MUTED))

    f.append(text(150, 232, "BIG-ENDIAN", size=14, color=INK, anchor="start", bold=True))
    f.append(text(150, 252, "старший — першим", size=10, color=MUTED, anchor="start"))
    memrow(212, [0, 1, 2, 3])
    f.append(line(362, 300, 812, 300, color=MUTED, sw=1.6))
    f.append(arrow(792, 300, 812, 300, color=MUTED, sw=1.6))
    f.append(text(360, 292, "адреса →", size=10, color=MUTED, anchor="start", bold=True))

    f.append(text(150, 352, "LITTLE-ENDIAN", size=14, color=INK, anchor="start", bold=True))
    f.append(text(150, 372, "молодший — першим", size=10, color=MUTED, anchor="start"))
    memrow(332, [3, 2, 1, 0])

    f.append(rect(60, 414, 780, 78, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, 438,
                  "Той самий колір — той самий байт: у big-endian 0x12 лежить за адресою 0x00, у little-endian — за 0x03.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 460,
                  "LITTLE-ENDIAN: x86, ARM (звичайно), ESP32, RISC-V.   BIG-ENDIAN: мережа (network byte order), Motorola 68k, PowerPC.",
                  size=10.5, color=MUTED))
    f.append(text(W / 2, 480,
                  "Мнемоніка: little-endian кладе «малий кінець» (молодший байт) за найменшою адресою.",
                  size=10, color=MUTED, italic=True))
    out("endianness.svg", W, H, *f,
        title="Порядок байтів (endianness): у якій послідовності байти лежать у пам'яті")


# ── 4. «Свята війна»: Свіфт і Коен ───────────────────────────────────────────
def fig_holy_war():
    W, H = 900, 470
    f = []
    # ліва панель: Свіфт
    f.append(rect(60, 84, 360, 252, fill="#fafafa", stroke=INK, sw=1.6, rx=10))
    f.append(text(240, 110, "«Мандри Гуллівера» (Свіфт, 1726)", size=12.5, color=INK, bold=True))
    f.append('<ellipse cx="150" cy="198" rx="34" ry="44" fill="#fffdf5" stroke="%s" stroke-width="2.4"/>' % POS)
    f.append('<polyline points="134,236 144,228 152,238 162,229 168,237" fill="none" stroke="%s" stroke-width="2"/>' % POS)
    f.append('<ellipse cx="330" cy="198" rx="34" ry="44" fill="#fffdf5" stroke="%s" stroke-width="2.4"/>' % NEG)
    f.append('<polyline points="316,162 325,154 333,163 341,154 346,162" fill="none" stroke="%s" stroke-width="2"/>' % NEG)
    f.append(text(150, 268, "тупоконечники", size=11.5, color=POS, bold=True))
    f.append(text(150, 284, "(б'ють з тупого кінця)", size=9, color=MUTED))
    f.append(text(330, 268, "гостроконечники", size=11.5, color=NEG, bold=True))
    f.append(text(330, 284, "(б'ють з гострого кінця)", size=9, color=MUTED))
    f.append(text(240, 314, "Ліліпути воювали, з якого кінця бити яйце", size=10.5, color=INK, italic=True))
    # права панель: Коен
    f.append(rect(440, 84, 400, 252, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(640, 110, "Денні Коен, 1980", size=12.5, color=FIELD, bold=True))
    f.append(text(640, 132, "«On Holy Wars and a Plea for Peace»", size=11, color=INK, italic=True))
    for i, ln in enumerate([
            "Коен узяв образ Свіфта й охрестив два",
            "порядки байтів: big-endian і little-endian.",
            "",
            "Його теза: жоден не «кращий» — головне",
            "ДОМОВИТИСЯ, інакше машини не зрозуміють",
            "одна одну. Це й була його «мольба про мир»."]):
        f.append(text(460, 160 + i * 22, ln, size=11, color=INK, anchor="start"))
    # практичний укус
    f.append(text(W / 2, 364,
                  "Практичний укус: на little-endian машині число 0x12345678 у hex-дампі пам'яті виглядає як «78 56 34 12».",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 386,
                  "Новачки лякаються «перевернутих» байтів — а це просто little-endian показує молодший байт першим.",
                  size=10.5, color=MUTED, italic=True))
    f.append(rect(60, 410, 780, 48, fill=AMBER_BG, stroke=AMBER, sw=1.4, rx=10))
    f.append(text(W / 2, 431,
                  "Усередині однієї машини порядок байтів НЕВИДИМИЙ — він кусає лише на МЕЖІ: обмін по мережі, файли, давачі.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 449,
                  "Тому й «свята війна»: суперечка пристрасна, а по суті — лише угода, якого кінця триматися.",
                  size=10, color=MUTED, italic=True))
    out("holy-war.svg", W, H, *f,
        title="Звідки назва й чому це «свята війна»: Ліліпутія, Свіфт і Коен")


# ── 5. Порядок байтів на практиці ────────────────────────────────────────────
def fig_practice():
    W, H = 900, 442
    f = []
    # ліва колонка: коли кусає
    f.append(rect(60, 80, 380, 300, fill="#fdf6f6", stroke=POS, sw=1.6, rx=10))
    f.append(text(250, 106, "Коли кусає", size=14, color=POS, bold=True))
    bites = [
        ("✘ Читаєш багатобайтове значення", "побайтно: файл, пакет, регістр давача"),
        ("✘ Обмін між машинами", "різної ендіанності — байти переставляться"),
        ("✘ Hex-дамп «задом наперед»", "на little-endian: 0x1234 → «34 12»"),
        ("✘ Невідповідність у протоколі", "відправник BE, отримувач LE → сміття"),
    ]
    y = 134
    for head, sub in bites:
        f.append(text(78, y, head, size=12, color=INK, anchor="start", bold=True))
        f.append(text(96, y + 18, sub, size=10, color=MUTED, anchor="start"))
        y += 58
    # права колонка: як жити
    f.append(rect(460, 80, 380, 300, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(650, 106, "Як із цим жити", size=14, color=FIELD, bold=True))
    lives = [
        ("✔ Мережевий порядок = big-endian", "htons/htonl/ntohs/ntohl переставляють байти"),
        ("✔ Даташит каже порядок", "MSB-first чи LSB-first — читай і дотримуйся"),
        ("✔ Складай число явно з байтів", "v = b0 | (b1<<8) | (b2<<16) | (b3<<24)"),
        ("✔ Усередині машини — байдуже", "ендіанність невидима, поки байти «вдома»"),
    ]
    y = 134
    for head, sub in lives:
        f.append(text(478, y, head, size=12, color=INK, anchor="start", bold=True))
        f.append(text(496, y + 18, sub, size=10, color=MUTED, anchor="start"))
        y += 58
    f.append(text(W / 2, 410,
                  "Золоте правило: складай багатобайтові значення явними зсувами — і код працюватиме на будь-якій машині.",
                  size=11.5, color=INK, bold=True))
    out("practice.svg", W, H, *f,
        title="Порядок байтів на практиці: коли кусає і як із ним жити")


# ════════════════ ВСТАВКА proj-serialization ═════════════════════════════════

# ── 6. Серіалізація int32 явними зсувами в мережевий порядок ─────────────────
def fig_pack_int32():
    W, H = 960, 560
    f = []
    byts = [("(v >> 24) & 0xFF", "0x12", POS, RED_BG, "buf[0]"),
            ("(v >> 16) & 0xFF", "0x34", AMBER, AMBER_BG, "buf[1]"),
            ("(v >>  8) & 0xFF", "0x56", FIELD, GREEN_BG, "buf[2]"),
            ("(v >>  0) & 0xFF", "0x78", NEG, BLUE_BG, "buf[3]")]
    # значення в регістрі
    f.append(rect(300, 84, 360, 56, fill="#f4f4f4", stroke=INK, sw=2, rx=8))
    f.append(text(480, 105, "значення в регістрі (uint32_t)", size=13, color=INK, bold=True))
    f.append(mono(480, 127, "v = 0x12345678", size=16, color=INK, anchor="middle", bold=True))
    # крок 1
    f.append(text(60, 176, "крок 1 — дістаємо кожен байт зсувом і маскою:", size=13, color=INK, anchor="start", bold=True))
    for i, (expr, val, col, bg, slot) in enumerate(byts):
        x = 60 + i * 218
        f.append(rect(x, 190, 200, 40, fill=bg, stroke=col, sw=1.8, rx=6))
        f.append(mono(x + 10, 215, expr, size=12.5, color=INK))
        f.append(mono(x + 190, 246, "= " + val, size=12.5, color=col, anchor="end", bold=True))
        f.append(line(x + 100, 252, x + 100, 280, color=col, sw=2))
        f.append(arrow(x + 100, 262, x + 100, 280, color=col, sw=2))
    # крок 2
    f.append(text(60, 300, "крок 2 — кладемо в буфер старшим байтом уперед (мережевий порядок):",
                  size=13, color=INK, anchor="start", bold=True))
    for i, (expr, val, col, bg, slot) in enumerate(byts):
        x = 60 + i * 218
        f.append(rect(x, 310, 200, 56, fill=bg, stroke=col, sw=2, rx=6))
        f.append(mono(x + 100, 343, val, size=16, color=INK, anchor="middle", bold=True))
        f.append(text(x + 100, 359, slot, size=10, color=MUTED))
    f.append(line(60, 392, 914, 392, color=MUTED, sw=1.6))
    f.append(arrow(894, 392, 914, 392, color=MUTED, sw=1.6))
    f.append(text(60, 386, "найменша адреса", size=11, color=MUTED, anchor="start"))
    f.append(text(914, 386, "найбільша", size=11, color=MUTED, anchor="end"))
    # висновок
    f.append(rect(60, 470, 840, 56, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(480, 494, "Код НЕ залежить від ендіанності машини: ми самі диктуємо порядок зсувами.",
                  size=13, color=INK, bold=True))
    f.append(text(480, 514,
                  "Розпакування дзеркальне: v = (buf[0]<<24)|(buf[1]<<16)|(buf[2]<<8)|buf[3].  Треба little-endian — поміняй buf[0..3] місцями.",
                  size=11, color=MUTED, italic=True))
    out("pack-int32.svg", W, H, *f,
        title="Серіалізація int32 у байтовий буфер явними зсувами")


# ── 7. union проти memcpy для доступу до байтів float ────────────────────────
def fig_union_vs_memcpy():
    W, H = 960, 560
    f = []
    f.append(rect(330, 78, 300, 46, fill="#f4f4f4", stroke=INK, sw=1.8, rx=8))
    f.append(text(480, 98, "float f = 1.0f", size=14, color=INK, bold=True))
    f.append(mono(480, 117, "біти IEEE-754: 0x3F800000", size=12, color=MUTED, anchor="middle"))
    # union
    f.append(rect(60, 150, 400, 300, fill=RED_BG, stroke=POS, sw=1.9, rx=12))
    f.append(text(260, 176, "union — спільна пам'ять", size=15, color=POS, bold=True))
    for i, ln in enumerate(["union { float f;", "        uint8_t b[4]; } u;", "u.f = 1.0f;",
                            "u.b[0] … u.b[3]  // читаємо байти"]):
        f.append(mono(82, 206 + i * 21, ln, size=13 if i < 3 else 12.5, color=INK))
    cells = ["3F", "80", "00", "00"]
    for i, v in enumerate(cells):
        cx = 130 + i * 65
        f.append(rect(cx, 300, 60, 34, fill=BG, stroke=INK, sw=1.6, rx=4))
        f.append(mono(cx + 30, 322, v, size=12, color=INK, anchor="middle"))
    f.append(text(260, 292, "ті самі 4 байти", size=11, color=MUTED, italic=True))
    f.append(text(260, 354, "f і b[] — два «вікна» в одну комірку", size=11.5, color=INK))
    f.append(rect(80, 378, 360, 56, fill=BG, stroke=POS, sw=1.5, rx=8))
    f.append(text(260, 399, "У C — поширена практика й зазвичай працює.", size=11.5, color=INK, bold=True))
    f.append(text(260, 419, "У C++ читати НЕ той член union — формально UB.", size=11.5, color=POS, bold=True))
    # memcpy
    f.append(rect(500, 150, 400, 300, fill=GREEN_BG, stroke=FIELD, sw=1.9, rx=12))
    f.append(text(700, 176, "memcpy — байтова копія", size=15, color=FIELD, bold=True))
    for i, (ln, c) in enumerate([("uint8_t b[4];", INK), ("memcpy(b, &f, 4);  // байт-у-байт", INK),
                                 ("// b[] тепер копія байтів f", FIELD)]):
        f.append(mono(522, 210 + i * 24, ln, size=13 if i < 2 else 12, color=c))
    f.append(rect(560, 290, 120, 34, fill=BG, stroke=INK, sw=1.6, rx=4))
    f.append(text(620, 284, "f (float)", size=10, color=MUTED))
    f.append(mono(620, 312, "3F 80 00 00", size=12, color=INK, anchor="middle"))
    f.append(line(685, 307, 730, 307, color=FIELD, sw=2.2))
    f.append(arrow(712, 307, 730, 307, color=FIELD, sw=2.2))
    f.append(text(710, 297, "копія", size=10, color=FIELD))
    f.append(rect(740, 290, 120, 34, fill=BG, stroke=FIELD, sw=1.6, rx=4))
    f.append(text(800, 284, "b[4] (uint8_t)", size=10, color=MUTED))
    f.append(mono(800, 312, "3F 80 00 00", size=12, color=FIELD, anchor="middle"))
    f.append(rect(520, 378, 360, 56, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(700, 399, "Визначено і в C, і в C++. Компілятор згортає", size=11.5, color=INK, bold=True))
    f.append(text(700, 419, "memcpy сталого розміру в той самий код — без накладних.", size=11.5, color=FIELD, bold=True))
    # засторога
    f.append(rect(60, 490, 840, 56, fill=AMBER_BG, stroke=AMBER, sw=1.8, rx=10))
    f.append(text(480, 513, "Спільна засторога: байти float переносні між машинами ЛИШЕ якщо обидві — IEEE-754 і однакової ендіанності.",
                  size=12, color=INK, bold=True))
    f.append(text(480, 531, "Перетинаєш мережу — домовся про формат: 4 байти IEEE-754 у фіксованому (зазвичай мережевому) порядку.",
                  size=11, color=MUTED, italic=True))
    out("union-vs-memcpy.svg", W, H, *f,
        title="Дістати байти float: union проти memcpy")


# ════════════════ ВСТАВКА comp-sensor-byte-order ═════════════════════════════

# ── 8. Карта регістрів давача середовища ─────────────────────────────────────
def fig_register_map():
    W, H = 950, 520
    f = []
    headers = [("Адреса", 88), ("Регістр (даташит)", 210), ("Вміст (8 бітів)", 440), ("Роль байта", 610)]
    f.append(rect(70, 92, 760, 30, fill="#f3f5f8", stroke=MUTED, sw=1.4, rx=0))
    for h, hx in headers:
        f.append(text(hx, 112, h, size=13.5, color=INK, anchor="start", bold=True))
    rows = [
        ("0xF7", "press_msb", "P[19:12]", "старший байт тиску", POS, RED_BG),
        ("0xF8", "press_lsb", "P[11:4]", "молодший байт тиску", POS, RED_BG),
        ("0xF9", "press_xlsb", "P[3:0]·0000", "додаткові 4 біти", POS, RED_BG),
        ("0xFA", "temp_msb", "T[19:12]", "старший байт темпер.", NEG, BLUE_BG),
        ("0xFB", "temp_lsb", "T[11:4]", "молодший байт темпер.", NEG, BLUE_BG),
        ("0xFC", "temp_xlsb", "T[3:0]·0000", "додаткові 4 біти", NEG, BLUE_BG),
        ("0xFD", "hum_msb", "H[15:8]", "старший байт вологості", FIELD, GREEN_BG),
        ("0xFE", "hum_lsb", "H[7:0]", "молодший байт вологості", FIELD, GREEN_BG),
    ]
    y = 122
    for addr, reg, bits, role, col, bg in rows:
        f.append(rect(70, y, 760, 36, fill=bg, stroke="#e4e4e4", sw=1.0, rx=0))
        f.append(mono(88, y + 23, addr, size=14, color=INK, bold=True))
        f.append(mono(210, y + 23, reg, size=14, color=col, bold=True))
        f.append(mono(440, y + 23, bits, size=13, color=INK))
        f.append(text(610, y + 23, role, size=12.5, color=INK, anchor="start"))
        y += 36
    f.append(rect(70, 122, 760, 288, fill="none", stroke=MUTED, sw=1.6, rx=0))
    # дужка «16 бітів вологості»
    f.append(line(844, 342, 856, 342, color=FIELD, sw=2))
    f.append(line(856, 342, 856, 406, color=FIELD, sw=2))
    f.append(line(856, 406, 844, 406, color=FIELD, sw=2))
    f.append(text(864, 368, "16 бітів", size=13, color=FIELD, anchor="start", bold=True))
    f.append(text(864, 386, "вологості", size=12, color=FIELD, anchor="start"))
    f.append(text(70, 440,
                  "MSB-байт — за МЕНШОЮ адресою (0xF7), молодший — за більшою: у даташиті регістри впорядковані big-endian,",
                  size=12.5, color=INK, anchor="start"))
    f.append(text(70, 460,
                  "хоч сам мікроконтролер (ESP32, ARM) — little-endian. Порядок диктує ДАВАЧ, а не процесор.",
                  size=12.5, color=AMBER, anchor="start", bold=True))
    out("register-map.svg", W, H, *f,
        title="Карта регістрів давача середовища: одна величина — кілька регістрів")


# ── 9. Пакетне читання (burst read) ──────────────────────────────────────────
def fig_burst_read():
    W, H = 860, 470
    f = []
    f.append(rect(40, 110, 150, 90, fill="#f3f5f8", stroke=INK, sw=2, rx=8))
    f.append(text(115, 142, "Мікро-", size=15, color=INK, bold=True))
    f.append(text(115, 162, "контролер", size=15, color=INK, bold=True))
    f.append(text(115, 184, "(little-endian)", size=11, color=MUTED))
    f.append(rect(670, 110, 150, 90, fill="#f3f5f8", stroke=INK, sw=2, rx=8))
    f.append(text(745, 142, "Давач", size=15, color=INK, bold=True))
    f.append(text(745, 162, "середовища", size=13, color=INK))
    f.append(text(745, 184, "автоінкремент", size=11, color=FIELD))
    f.append(line(190, 138, 660, 138, color=INK, sw=2.2))
    f.append(arrow(642, 138, 660, 138, color=INK, sw=2.2))
    f.append(text(430, 128, "1) запиши адресу указівника = 0xF7", size=13, color=INK, bold=True))
    f.append(line(670, 176, 200, 176, color=FIELD, sw=2.2))
    f.append(arrow(218, 176, 200, 176, color=FIELD, sw=2.2))
    f.append(text(430, 200, "2) читай — давач віддає байт за байтом, адреса росте сама", size=13, color=FIELD, bold=True))
    cells = [
        ("0xF7", "байт 0", "press_msb", POS, RED_BG),
        ("0xF8", "байт 1", "press_lsb", POS, RED_BG),
        ("0xF9", "байт 2", "press_xlsb", POS, RED_BG),
        ("0xFA", "байт 3", "temp_msb", NEG, BLUE_BG),
        ("0xFB", "байт 4", "temp_lsb", NEG, BLUE_BG),
        ("0xFC", "байт 5", "temp_xlsb", NEG, BLUE_BG),
        ("0xFD", "байт 6", "hum_msb", FIELD, GREEN_BG),
        ("0xFE", "байт 7", "hum_lsb", FIELD, GREEN_BG),
    ]
    x = 70
    for addr, lbl, reg, col, bg in cells:
        f.append(rect(x, 280, 84, 64, fill=bg, stroke=col, sw=1.8, rx=5))
        f.append(mono(x + 42, 272, addr, size=11.5, color=MUTED, anchor="middle"))
        f.append(text(x + 42, 306, lbl, size=12.5, color=INK, bold=True))
        f.append(mono(x + 42, 326, reg, size=10, color=col, anchor="middle"))
        x += 90
    f.append(line(70, 370, 784, 370, color=MUTED, sw=1.8))
    f.append(arrow(766, 370, 784, 370, color=MUTED, sw=1.8))
    f.append(text(70, 394, "порядок у часі →", size=12, color=MUTED, anchor="start", italic=True))
    f.append(text(430, 394,
                  "три величини за одне читання — усі байти з ОДНОГО зрізу часу (без «розриву» між темпер. і тиском)",
                  size=12, color=INK, anchor="middle"))
    out("burst-read.svg", W, H, *f,
        title="Пакетне читання: один указівник регістра — потік байтів поспіль")


# ── 10. Складання результату зсувами проти приведення вказівника ─────────────
def fig_reassembly():
    W, H = 860, 470
    f = []
    parts = [("0xFA", "temp_msb", "T[19:12]", "<< 12", 195),
             ("0xFB", "temp_lsb", "T[11:4]", "<< 4", 385),
             ("0xFC", "temp_xlsb", "T[3:0]", ">> 4", 575)]
    for addr, reg, bits, shift, cx in parts:
        f.append(rect(cx - 75, 92, 150, 52, fill=BLUE_BG, stroke=NEG, sw=1.8, rx=5))
        f.append(mono(cx, 84, addr, size=11.5, color=MUTED, anchor="middle"))
        f.append(mono(cx, 114, reg, size=13, color=NEG, anchor="middle", bold=True))
        f.append(mono(cx, 134, bits, size=12, color=INK, anchor="middle"))
        f.append(mono(cx, 170, shift, size=16, color=POS, anchor="middle", bold=True))
        f.append(line(cx, 180, cx, 208, color=POS, sw=2))
        f.append(arrow(cx, 190, cx, 208, color=POS, sw=2))
    f.append(rect(120, 222, 530, 40, fill=RED_BG, stroke=POS, sw=1.6, rx=6))
    f.append(mono(385, 247, "int32_t T = (msb << 12) | (lsb << 4) | (xlsb >> 4);",
                  size=15.5, color=INK, anchor="middle", bold=True))
    f.append(text(430, 292, "20-бітний «сирий» результат T (raw ADC value)", size=13.5, color=FIELD, bold=True))
    # розкладка бітів результату
    f.append(rect(100, 306, 264, 34, fill=BLUE_BG, stroke=NEG, sw=1.6, rx=0))
    f.append(mono(232, 328, "T[19:12] ← msb", size=12, color=NEG, anchor="middle", bold=True))
    f.append(rect(364, 306, 264, 34, fill=RED_BG, stroke=POS, sw=1.6, rx=0))
    f.append(mono(496, 328, "T[11:4] ← lsb", size=12, color=POS, anchor="middle", bold=True))
    f.append(rect(628, 306, 132, 34, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=0))
    f.append(mono(694, 328, "T[3:0] ← xlsb", size=12, color=FIELD, anchor="middle", bold=True))
    f.append(rect(100, 306, 660, 34, fill="none", stroke=INK, sw=1.8, rx=0))
    f.append(text(430, 362, "✓ той самий результат на БУДЬ-ЯКІЙ машині — little- чи big-endian",
                  size=13, color=FIELD, bold=True))
    f.append(rect(70, 392, 720, 56, fill="#fff4f4", stroke=POS, sw=1.6, rx=6))
    f.append(mono(90, 414, "✗  int32_t T = *(int32_t*)buf;", size=14.5, color=POS, bold=True))
    f.append(text(330, 414, "— читає байти «як лежать»: ламається на чужій ендіанності,",
                  size=12.5, color=INK, anchor="start"))
    f.append(text(330, 434, "а ще — невирівняна адреса (alignment) і суворе аліасування (strict aliasing). Не робіть так.",
                  size=12.5, color=INK, anchor="start"))
    out("reassembly.svg", W, H, *f,
        title="Складання результату: явні зсуви проти «приведення вказівника»")


if __name__ == "__main__":
    fig_hierarchy()
    fig_wordsize()
    fig_endianness()
    fig_holy_war()
    fig_practice()
    fig_pack_int32()
    fig_union_vs_memcpy()
    fig_register_map()
    fig_burst_read()
    fig_reassembly()
    print("OK: 10 фігур у", IMG)
