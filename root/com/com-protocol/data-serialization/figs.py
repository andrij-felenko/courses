# -*- coding: utf-8 -*-
"""Фігури до теми «Серіалізація даних» (data-serialization).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"   # старший байт / «гаряче» / небезпека
BLUE_BG  = "#eaf0fd"   # молодший байт / «холодне»
GREEN_BG = "#eaf6ee"   # добре / висновок
GRAY_BG  = "#e9ecef"   # набивка-сміття
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def cell(x, y, w, h, s, bg=FILL, stroke=LINE, color=INK, size=13, bold=False, sw=1.5):
    return (rect(x, y, w, h, fill=bg, stroke=stroke, sw=sw, rx=4) +
            ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
             'text-anchor="middle"%s>%s</text>'
             % (x + w / 2, y + h / 2 + size * 0.35, MONO, size, color,
                ' font-weight="700"' if bold else '', esc(s))))


# ════════════ 1. Чому не memcpy: три залежності від машини ════════════════════
def fig_why_not():
    W, H = 900, 500
    f = []
    f.append(text(W / 2, 30, "Чому байтовий образ структури — НЕ переносний формат", size=16, bold=True))
    f.append(text(W / 2, 52, "struct { uint8_t id; uint32_t value; char *name; }", size=12, color=MUTED))

    cw = 44
    # ── (1) Ендіанність ──
    y = 96
    f.append(text(40, y - 8, "1 · Порядок байтів", size=13, color=POS, anchor="start", bold=True))
    f.append(mono(40, y + 12, "value = 0x11223344", size=12, color=INK))
    # little-endian
    f.append(text(360, y + 12, "little-endian (ESP32)", size=11, color=MUTED, anchor="start"))
    for i, b in enumerate(["44", "33", "22", "11"]):
        f.append(cell(360 + i * (cw + 3), y + 24, cw, 30, b, bg=BLUE_BG, color=NEG, bold=True))
    # big-endian
    f.append(text(600, y + 12, "big-endian (сервер)", size=11, color=MUTED, anchor="start"))
    for i, b in enumerate(["11", "22", "33", "44"]):
        f.append(cell(600 + i * (cw + 3), y + 24, cw, 30, b, bg=RED_BG, color=POS, bold=True))
    f.append(text(W / 2, y + 74, "ті самі байти читаються як різні числа → задом наперед",
                  size=11, color=POS))

    # ── (2) Набивка ──
    y = 220
    f.append(text(40, y - 8, "2 · Вирівнювання й набивка", size=13, color=AMBER, anchor="start", bold=True))
    f.append(text(40, y + 12, "корисних: 1+4 = 5 байтів", size=11, color=MUTED, anchor="start"))
    labels = [("id", FILL, INK), ("pad", GRAY_BG, MUTED), ("pad", GRAY_BG, MUTED), ("pad", GRAY_BG, MUTED),
              ("value", FILL, INK), ("value", FILL, INK), ("value", FILL, INK), ("value", FILL, INK)]
    x0 = 300
    for i, (s, bg, col) in enumerate(labels):
        f.append(cell(x0 + i * (cw + 2), y, cw, 32, s, bg=bg, color=col, size=11))
    f.append(text(x0 + 4 * (cw + 2), y + 54, "sizeof = 8: три байти набивки — сміття; інший тулчейн дасть іншу",
                  size=11, color=AMBER))

    # ── (3) Вказівник ──
    y = 340
    f.append(text(40, y - 8, "3 · Вказівник", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(40, y + 12, "name = 0x2000A4C0", size=11, color=MUTED, anchor="start"))
    # у структурі — лише адреса
    f.append(cell(300, y, 150, 34, "0x2000A4C0", bg=BLUE_BG, color=NEG, bold=True))
    f.append(text(375, y + 52, "у образ входить лише АДРЕСА", size=10, color=MUTED))
    # стрілка на дані десь-інде
    f.append(arrow(452, y + 17, 560, y + 17, color=NEG))
    f.append(cell(560, y, 190, 34, '"sensor-A" ← не в образі!', bg=FILL, color=INK, size=11))
    f.append(text(645, y + 52, "рядок лежить деінде, у потік не потрапляє", size=10, color=NEG))

    f.append(fitbox(120, y + 78, W - 240, 34,
                    "Формат мусить: диктувати порядок · викинути набивку · розкрутити вказівник у дані",
                    size=12, fill=GREEN_BG, stroke=FIELD, color=INK, bold=True))
    out("why-not-memcpy.svg", W, H, *f)


# ════════════ 2. Фіксована розкладка проти самоопису ══════════════════════════
def fig_fixed_vs():
    W, H = 900, 430
    f = []
    f.append(text(W / 2, 30, "Дві сім'ї форматів: та сама порція даних", size=16, bold=True))
    f.append(text(W / 2, 52, "температура = 235, статус = 1", size=12, color=MUTED))

    cw = 58

    # ── Фіксована ──
    f.append(text(40, 96, "Фіксована розкладка", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 114, "голі значення впритул — структуру читач знає з коду", size=11, color=MUTED, anchor="start"))
    x0 = 210
    y = 130
    vals = [("00", "temp"), ("00", "temp"), ("00", "temp"), ("EB", "temp"), ("01", "статус")]
    for i, (b, lab) in enumerate(vals):
        bg = RED_BG if lab == "temp" else BLUE_BG
        col = POS if lab == "temp" else NEG
        f.append(cell(x0 + i * (cw + 3), y, cw, 34, b, bg=bg, color=col, bold=True))
        f.append(text(x0 + i * (cw + 3) + cw / 2, y + 50, lab, size=10, color=MUTED))
    f.append(text(x0 + 5 * (cw + 3) + 40, y + 18, "5 байтів", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(W / 2, y + 74, "щільно й швидко, але «мовчить» про структуру → крихке до змін",
                  size=11, color=MUTED))

    # ── Самоопис ──
    f.append(text(40, 268, "Самоопис (стиль CBOR)", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 286, "перед значенням — тег-заголовок «що це»", size=11, color=MUTED, anchor="start"))
    x0 = 210
    y = 302
    # тег «uint32», 4 байти значення, значення статусу коротким кодом
    seq = [("1A", "тег:u32", AMBER_BG, AMBER),
           ("00", "temp", RED_BG, POS), ("00", "temp", RED_BG, POS),
           ("00", "temp", RED_BG, POS), ("EB", "temp", RED_BG, POS),
           ("01", "статус", BLUE_BG, NEG)]
    for i, (b, lab, bg, col) in enumerate(seq):
        f.append(cell(x0 + i * (cw + 3), y, cw, 34, b, bg=bg, color=col, bold=True))
        f.append(text(x0 + i * (cw + 3) + cw / 2, y + 50, lab, size=9, color=MUTED))
    f.append(text(x0 + 6 * (cw + 3) + 20, y + 18, "довше", size=12, color=AMBER, anchor="start", bold=True))
    f.append(text(W / 2, y + 74, "тег розповідає структуру → додаси поле, старий читач переступить незнайоме",
                  size=11, color=MUTED))
    out("fixed-vs-selfdesc.svg", W, H, *f)


# ════════════ 3. Схемна еволюція: новий тег не ламає старого читача ════════════
def fig_schema():
    W, H = 900, 440
    f = []
    f.append(text(W / 2, 30, "Схемна еволюція: новий тег не ламає старого читача", size=16, bold=True))

    cw = 74
    x0 = 250
    # ── Потік від відправника v2 ──
    f.append(text(40, 92, "Відправник v2 шле:", size=13, color=INK, anchor="start", bold=True))
    tags = [("тег 1", "temp", GREEN_BG, FIELD),
            ("тег 2", "статус", GREEN_BG, FIELD),
            ("тег 3", "вологість", AMBER_BG, AMBER)]
    y = 74
    for i, (t, lab, bg, col) in enumerate(tags):
        f.append(cell(x0 + i * (cw + 6), y, cw, 40, t, bg=bg, color=col, bold=True, size=12))
        f.append(text(x0 + i * (cw + 6) + cw / 2, y + 56, lab, size=10, color=MUTED))

    # ── Читач v1 ──
    f.append(text(40, 210, "Читач v1 (знає теги 1, 2):", size=13, color=INK, anchor="start", bold=True))
    y = 192
    marks = [("тег 1", "чит.", GREEN_BG, FIELD, "✓"),
             ("тег 2", "чит.", GREEN_BG, FIELD, "✓"),
             ("тег 3", "?", GRAY_BG, MUTED, "→")]
    for i, (t, lab, bg, col, mk) in enumerate(marks):
        f.append(cell(x0 + i * (cw + 6), y, cw, 40, t, bg=bg, color=col, bold=True, size=12))
        f.append(text(x0 + i * (cw + 6) + cw / 2, y - 8, mk, size=16, color=col, bold=True))
    f.append(text(x0 + 2 * (cw + 6) + cw / 2, y + 56, "незнайоме →\nпереступити", size=9, color=MUTED))
    # текст пояснення
    f.append(text(W / 2, y + 92, "поля 1 і 2 прочитані; тег 3 незнайомий — пропущено за його довжиною, БЕЗ падіння",
                  size=11, color=INK))

    # ── Дзеркальний випадок ──
    f.append(fitbox(90, 350, W - 180, 60,
                    ["Дзеркально: читач v2, діставши від старого відправника лише теги 1 і 2,",
                     "підставляє для відсутнього поля 3 значення за замовчуванням.",
                     "Правило: номер поля, раз виданий, закріплений НАВІЧНО — не міняти, не перевикористовувати."],
                    size=11, fill=GREEN_BG, stroke=FIELD, color=INK, bold=False))
    out("schema-evolution.svg", W, H, *f)


# ════════════ 4. Varint: як 300 лягає у два байти (біт-прапорець) ══════════════
def fig_varint():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Varint: число 300 → два байти base-128", size=16, bold=True))
    f.append(text(W / 2, 52, "300 = 0b1_0010_1100  (потрібно 9 бітів → в один байт по 7 не влазить)",
                  size=12, color=MUTED))

    # ── крок 1: 7-бітні групи, молодша перша ──
    f.append(text(40, 100, "1 · розбити на 7-бітні групи, МОЛОДША перша", size=13, color=INK, anchor="start", bold=True))
    f.append(mono(60, 128, "0010 1100  →  групи по 7:  010 1100 | 000 0010", size=13))
    f.append(mono(60, 150, "               молодші 7 = 0101100   старші = 0000010", size=12, color=MUTED))

    # ── крок 2: приліпити старший біт-прапорець ──
    f.append(text(40, 196, "2 · старший біт = «далі ще є?» (1 — так, 0 — це останній)",
                  size=13, color=INK, anchor="start", bold=True))
    bw = 34
    # байт 0: continuation=1, payload=0101100
    y = 216
    x0 = 120
    f.append(text(x0 + 4 * bw, y - 8, "байт 0 (перший на дроті)", size=11, color=MUTED))
    bits0 = [("1", POS), ("0", INK), ("1", INK), ("0", INK), ("1", INK), ("1", INK), ("0", INK), ("0", INK)]
    for i, (b, col) in enumerate(bits0):
        bg = RED_BG if i == 0 else BLUE_BG
        f.append(cell(x0 + i * (bw + 2), y, bw, 34, b, bg=bg, color=col, bold=(i == 0)))
    f.append(text(x0 + bw / 2, y + 52, "прапор=1", size=10, color=POS))
    f.append(text(x0 + 4.5 * bw, y + 52, "молодші 7 бітів", size=10, color=NEG))

    # байт 1: continuation=0, payload=0000010
    x1 = x0 + 8 * (bw + 2) + 40
    f.append(text(x1 + 4 * bw, y - 8, "байт 1 (останній)", size=11, color=MUTED))
    bits1 = [("0", FIELD), ("0", INK), ("0", INK), ("0", INK), ("0", INK), ("0", INK), ("1", INK), ("0", INK)]
    for i, (b, col) in enumerate(bits1):
        bg = GREEN_BG if i == 0 else BLUE_BG
        f.append(cell(x1 + i * (bw + 2), y, bw, 34, b, bg=bg, color=col, bold=(i == 0)))
    f.append(text(x1 + bw / 2, y + 52, "прапор=0", size=10, color=FIELD))
    f.append(text(x1 + 4.5 * bw, y + 52, "старші біти", size=10, color=NEG))

    # ── крок 3: байти на дроті ──
    f.append(text(40, 306, "3 · на дроті (шістнадцятково):", size=13, color=INK, anchor="start", bold=True))
    cw = 60
    xb = 360
    for i, (b, lab) in enumerate([("AC", "0xAC"), ("02", "0x02")]):
        f.append(cell(xb + i * (cw + 6), 288, cw, 34, b, bg=AMBER_BG, color=AMBER, bold=True))
    f.append(text(xb + 2 * (cw + 6) + 30, 305, "мале число — мало байтів", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(120, 360, W - 240, 70,
                    ["Декодер читає байти, поки старший біт = 1; на першому байті з 0 — стоп.",
                     "Payload-сімки склеює у ЗВОРОТНОМУ порядку (молодша група — молодші біти):",
                     "0000010·0101100 = 1_0010_1100 = 300."],
                    size=12, fill=GREEN_BG, stroke=FIELD, color=INK, bold=False))
    out("varint-anatomy.svg", W, H, *f)


# ════════════ 5. Тег Protobuf і zigzag: одне число несе номер+тип; знак — у парність
def fig_tag_zigzag():
    W, H = 900, 480
    f = []
    f.append(text(W / 2, 30, "Один varint несе номер поля І тип; zigzag ховає знак у парність",
                  size=16, bold=True))

    # ── тег: (номер << 3) | тип ──
    f.append(text(40, 78, "Тег поля = (номер_поля << 3) | тип_на_дроті", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 98, "приклад: поле 3, тип VARINT(0)  →  (3<<3)|0 = 24 = 0x18", size=11, color=MUTED, anchor="start"))
    bw = 40
    x0 = 200
    y = 116
    # 8 бітів тега 0x18 = 0001 1000: старші 5 = номер, молодші 3 = тип
    tbits = [("0", MUTED), ("0", MUTED), ("0", MUTED), ("1", FIELD), ("1", FIELD),
             ("0", POS), ("0", POS), ("0", POS)]
    for i, (b, col) in enumerate(tbits):
        if i < 5:
            bg = GREEN_BG
        else:
            bg = RED_BG
        f.append(cell(x0 + i * (bw + 2), y, bw, 36, b, bg=bg, color=col, bold=True))
    f.append(text(x0 + 2.5 * (bw + 2), y + 56, "номер поля = 3", size=11, color=FIELD))
    f.append(text(x0 + 6.5 * (bw + 2), y + 56, "тип = 0 (VARINT)", size=11, color=POS))

    # табличка типів
    f.append(text(40, 210, "3 молодші біти — тип на дроті:", size=12, color=INK, anchor="start", bold=True))
    types = [("0", "VARINT", "int/bool/enum, zigzag"), ("1", "I64", "fixed64, double"),
             ("2", "LEN", "рядок, bytes, вкладене"), ("5", "I32", "fixed32, float")]
    ty = 226
    for i, (code, name, use) in enumerate(types):
        yy = ty + i * 26
        f.append(cell(80, yy, 34, 22, code, bg=AMBER_BG, color=AMBER, bold=True, size=12))
        f.append(mono(126, yy + 16, name, size=12, bold=True))
        f.append(text(230, yy + 16, use, size=11, color=MUTED, anchor="start"))
    f.append(text(80, ty + 4 * 26 + 8, "(3 і 4 — застарілі групи; пропущено)", size=10, color=MUTED, anchor="start"))

    # ── zigzag число-лінія ──
    f.append(text(480, 210, "ZigZag: знакове → беззнакове", size=13, color=INK, anchor="start", bold=True))
    f.append(text(480, 228, "мале за модулем (і мінус!) → малий varint", size=11, color=MUTED, anchor="start"))
    pairs = [("0", "0"), ("−1", "1"), ("1", "2"), ("−2", "3"), ("2", "4"), ("−3", "5")]
    zw = 62
    zx = 500
    zy = 250
    for i, (sgn, enc) in enumerate(pairs):
        col = NEG if sgn.startswith("−") else INK
        f.append(cell(zx + (i % 3) * (zw + 6), zy + (i // 3) * 66, zw, 28, sgn,
                      bg=(BLUE_BG if sgn.startswith("−") else FILL), color=col, bold=True, size=13))
        f.append(text(zx + (i % 3) * (zw + 6) + zw / 2, zy + (i // 3) * 66 + 42, "↓", size=13, color=AMBER))
        f.append(cell(zx + (i % 3) * (zw + 6), zy + (i // 3) * 66 + 44, zw, 22, enc,
                      bg=AMBER_BG, color=AMBER, bold=True, size=12))

    f.append(fitbox(60, 400, W - 120, 60,
                    ["Кодування: (n << 1) ^ (n >> 31)  — від'ємні стають непарними, додатні — парними.",
                     "Розкодування: (u >> 1) ^ -(u & 1)  — молодший біт-парність відновлює знак.",
                     "Без zigzag −1 у two's complement = 0xFFFFFFFF → аж 5 байтів varint; із zigzag −1 = 1 → один байт."],
                    size=12, fill=GREEN_BG, stroke=FIELD, color=INK, bold=False))
    out("tag-zigzag.svg", W, H, *f)


# ════════════ 6. Задача обрамлення: у потоці немає меж кадру ═══════════════════
def fig_framing_problem():
    W, H = 900, 340
    f = []
    f.append(text(W / 2, 30, "Обрамлення: у байтовому потоці немає видимих меж кадру", size=16, bold=True))
    f.append(text(W / 2, 52, "UART віддає рівний струмінь октетів — де кадр почався й де скінчився?",
                  size=12, color=MUTED))

    cw = 46
    x0 = 60
    y = 96
    stream = ["7E", "02", "EB", "01", "7E", "02", "1C", "00", "7E", "02", "FF", "40"]
    for i, b in enumerate(stream):
        f.append(cell(x0 + i * (cw + 3), y, cw, 34, b, bg=FILL, color=INK, bold=False, size=13))
    f.append(text(W / 2, y + 60, "сам потік — це просто байти; жоден із них не «підписаний» як межа",
                  size=11, color=MUTED))

    # той самий потік, розібраний на кадри маркером 0x7E
    y = 210
    f.append(text(x0, y - 14, "той самий потік очима приймача (0x7E — початок кадру):",
                  size=12, color=INK, anchor="start", bold=True))
    groups = [(0, 4, GREEN_BG), (4, 4, BLUE_BG), (8, 4, RED_BG)]
    for gi, (start, n, bg) in enumerate(groups):
        for j in range(n):
            i = start + j
            f.append(cell(x0 + i * (cw + 3), y, cw, 34, stream[i], bg=bg,
                          color=(POS if j == 0 else INK), bold=(j == 0), size=13))
        cx = x0 + (start + n / 2.0) * (cw + 3) - cw / 2
        f.append(text(cx, y + 52, "кадр %d" % (gi + 1), size=11, color=MUTED))
    out("framing-problem.svg", W, H, *f)


# ════════════ 7. Два обрамлення: префікс довжини проти маркера з екрануванням ══
def fig_two_framings():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Два способи намацати межі кадру", size=16, bold=True))

    cw = 60

    # ── Префікс довжини ──
    f.append(text(40, 84, "Префікс довжини", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 102, "спершу читаємо, скільки байтів далі — тоді відлічуємо рівно стільки",
                  size=11, color=MUTED, anchor="start"))
    x0 = 90
    y = 128
    seq = [("LEN", "3", AMBER_BG, AMBER), ("D0", "дані", GREEN_BG, FIELD),
           ("D1", "дані", GREEN_BG, FIELD), ("D2", "дані", GREEN_BG, FIELD),
           ("CRC", "сума", BLUE_BG, NEG), ("CRC", "сума", BLUE_BG, NEG)]
    for i, (b, lab, bg, col) in enumerate(seq):
        f.append(cell(x0 + i * (cw + 4), y, cw, 36, b, bg=bg, color=col, bold=True, size=12))
        f.append(text(x0 + i * (cw + 4) + cw / 2, y + 54, lab, size=10, color=MUTED))
    f.append(arrow(x0 + cw / 2, y - 10, x0 + 3.5 * (cw + 4), y - 10, color=AMBER))
    f.append(text(x0 + 2 * (cw + 4), y - 18, "«далі 3 байти даних»", size=10, color=AMBER, anchor="middle"))
    f.append(fitbox(x0, y + 74, 700, 30,
                    "Дані прозорі: 0x7E всередині — звичайний байт. Але збрехана довжина губить синхронізацію.",
                    size=11, fill=AMBER_BG, stroke=AMBER, color=INK))

    # ── Маркер + екранування ──
    f.append(text(40, 276, "Маркер із екрануванням (стиль HDLC / PPP)", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 294, "0x7E — межа кадру; якщо байт даних = 0x7E чи 0x7D, його екранують",
                  size=11, color=MUTED, anchor="start"))
    x0 = 90
    y = 320
    seq2 = [("7E", "межа", RED_BG, POS), ("02", "дані", GREEN_BG, FIELD),
            ("7D", "escape", AMBER_BG, AMBER), ("5E", "=дані 7E", AMBER_BG, AMBER),
            ("01", "дані", GREEN_BG, FIELD), ("7E", "межа", RED_BG, POS)]
    for i, (b, lab, bg, col) in enumerate(seq2):
        f.append(cell(x0 + i * (cw + 4), y, cw, 36, b, bg=bg, color=col, bold=True, size=12))
        f.append(text(x0 + i * (cw + 4) + cw / 2, y + 54, lab, size=10, color=MUTED))
    f.append(text(x0 + 2.5 * (cw + 4), y - 10, "0x7D 0x5E = дані 0x7E   (0x7E XOR 0x20 = 0x5E)",
                  size=10, color=AMBER, anchor="middle"))
    f.append(fitbox(x0, y + 74, 700, 30,
                    "0x7E ніколи не трапляється в даних → межу видно завжди. Ціна — escape-байти й стан «щойно був 0x7D».",
                    size=11, fill=GREEN_BG, stroke=FIELD, color=INK))
    out("two-framings.svg", W, H, *f)


# ════════════ 8. Скінченний автомат приймача кадру ════════════════════════════
def fig_receiver_fsm():
    W, H = 900, 480
    f = []
    f.append(text(W / 2, 30, "Автомат приймача: збираємо кадр із UART побайтово", size=16, bold=True))

    def state(cx, cy, label, bg=FILL, col=INK):
        r = 50
        return (circle(cx, cy, r, fill=bg, stroke=LINE, sw=2) +
                text(cx, cy + 5, label, size=13, color=col, bold=True))

    yc = 170
    xs = [140, 400, 660]
    f.append(state(xs[0], yc, "WAIT", bg=BLUE_BG, col=NEG))
    f.append(state(xs[1], yc, "DATA", bg=GREEN_BG, col=FIELD))
    f.append(state(xs[2], yc, "ESC", bg=AMBER_BG, col=AMBER))

    # WAIT -> DATA
    f.append(arrow(xs[0] + 50, yc - 12, xs[1] - 50, yc - 12, color=INK))
    f.append(text((xs[0] + xs[1]) / 2, yc - 22, "0x7E → почати кадр", size=11, color=INK))

    # DATA -> ESC
    f.append(arrow(xs[1] + 50, yc - 12, xs[2] - 50, yc - 12, color=AMBER))
    f.append(text((xs[1] + xs[2]) / 2, yc - 22, "0x7D → чекати наступний", size=11, color=AMBER))

    # ESC -> DATA
    f.append(arrow(xs[2] - 50, yc + 16, xs[1] + 50, yc + 16, color=AMBER))
    f.append(text((xs[1] + xs[2]) / 2, yc + 32, "байт XOR 0x20 → у буфер", size=11, color=AMBER))

    # DATA loop
    f.append(arrow(xs[1] - 18, yc + 50, xs[1] + 18, yc + 50, color=FIELD))
    f.append(text(xs[1], yc + 86, "звич. байт → у буфер", size=11, color=FIELD))

    # DATA -> WAIT (close)
    f.append(line(xs[1], yc - 50, xs[1], yc - 100, color=INK, dash="4 3"))
    f.append(line(xs[1], yc - 100, xs[0], yc - 100, color=INK, dash="4 3"))
    f.append(arrow(xs[0], yc - 100, xs[0], yc - 50, color=INK))
    f.append(text((xs[0] + xs[1]) / 2, yc - 108, "0x7E → кадр закрито: звірити CRC, віддати", size=11, color=INK))

    # DATA -> WAIT (overflow)
    f.append(line(xs[1], yc + 50, xs[1], yc + 116, color=POS, dash="4 3"))
    f.append(line(xs[1], yc + 116, xs[0], yc + 116, color=POS, dash="4 3"))
    f.append(arrow(xs[0], yc + 116, xs[0] - 18, yc + 50, color=POS))
    f.append(text((xs[0] + xs[1]) / 2, yc + 132, "буфер повний → скинути кадр, назад у WAIT", size=11, color=POS))

    f.append(fitbox(80, 410, W - 160, 50,
                    ["Три стани ловлять усі пастки: WAIT відкидає сміття до першого 0x7E (ресинхронізація);",
                     "ESC пам'ятає розірваний байт екранування; переповнення скидає кадр, а не псує сусідню пам'ять."],
                    size=11, fill=FILL, stroke=LINE, color=INK))
    out("receiver-fsm.svg", W, H, *f)


# ════════════ 9. Родовід серіалізації: дві гілки від однієї задачі ════════════
def fig_family_tree():
    W, H = 900, 620
    f = []
    f.append(text(W / 2, 30, "Дві гілки серіалізації від однієї задачі", size=16, bold=True))

    # ── Спільний корінь: несумісні машини ──
    f.append(fitbox(W / 2 - 260, 48, 520, 42,
                    "Стіна: несумісні машини (big/little-endian, EBCDIC, слова Cray) — байти не означають те саме",
                    size=11, fill=GRAY_BG, stroke=LINE, color=INK, bold=True))

    LX, RX = 225, 675          # центри лівої (телеком) і правої (Unix) колонок
    bw = 350                   # ширина вузла

    def node(cx, top, title, sub, bg, stroke, col):
        h = 46
        f.append(fitbox(cx - bw / 2, top, bw, h, title, size=12,
                        fill=bg, stroke=stroke, color=col, bold=True))
        f.append(text(cx, top + h + 14, sub, size=10, color=MUTED))

    # заголовки колонок
    f.append(text(LX, 114, "ТЕЛЕКОМ · комітет, наперед, на все", size=11, color=POS, bold=True))
    f.append(text(RX, 114, "UNIX / SUN · мінімум, швидко, дешево", size=11, color=NEG, bold=True))

    # ── ліва гілка (телеком) ──
    node(LX, 128, "X.400 (пошта MHS, 1980–84)", "потрібно передати структуру листа", RED_BG, POS, POS)
    f.append(arrow(LX, 188, LX, 208, color=POS))
    node(LX, 210, "ASN.1 · X.409 (1984)", "мова опису + кодування разом", RED_BG, POS, POS)
    f.append(arrow(LX, 270, LX, 290, color=POS))
    node(LX, 292, "X.208 нотація + X.209 BER (1988)", "форма ОКРЕМО від кодування (TLV)", RED_BG, POS, POS)
    f.append(arrow(LX, 352, LX, 372, color=POS))
    node(LX, 374, "DER → сертифікати X.509", "канонічне кодування для підписів", AMBER_BG, AMBER, AMBER)

    # ── права гілка (Unix) ──
    node(RX, 128, "NFS + ONC RPC (Sun, 1984)", "потрібно передати аргументи й файли", BLUE_BG, NEG, NEG)
    f.append(arrow(RX, 188, RX, 208, color=NEG))
    node(RX, 210, "XDR · RFC 1014 (1987)", "канонічний big-endian, БЕЗ тегів", BLUE_BG, NEG, NEG)
    f.append(arrow(RX, 270, RX, 290, color=NEG))
    node(RX, 292, "«відправник усе виправляє»", "1 порядок на всіх; 4-байтові слова", BLUE_BG, NEG, NEG)

    # ── схема від телекома, щільність від Unix → Protobuf ──
    f.append(arrow(LX + bw / 2 - 30, 398, W / 2 - 120, 470, color=POS))
    f.append(arrow(RX, 328, W / 2 + 120, 470, color=NEG))
    f.append(fitbox(W / 2 - 185, 474, 370, 60,
                    ["Protocol Buffers (Google: Proto1 2001 → відкрито 2008)",
                     "СХЕМА (від телекома) + ЩІЛЬНІСТЬ (від Unix)",
                     "+ сталий числовий тег поля → еволюція без поломки"],
                    size=11, fill=GREEN_BG, stroke=FIELD, color=INK, bold=True))

    # ── безсхемна гілка збоку ──
    f.append(fitbox(W / 2 - 215, 552, 430, 48,
                    ["Безсхемний бунт: «як JSON, лише швидко й компактно»",
                     "MessagePack (2008) · CBOR — RFC 7049 (2013) / 8949 (2020): двійковий самоопис, без схеми"],
                    size=10, fill=FILL, stroke=LINE, color=INK, bold=False))
    out("serialization-family-tree.svg", W, H, *f)


if __name__ == "__main__":
    fig_why_not()
    fig_fixed_vs()
    fig_schema()
    fig_varint()
    fig_tag_zigzag()
    fig_framing_problem()
    fig_two_framings()
    fig_receiver_fsm()
    fig_family_tree()
    print("OK: figures written to", IMG)
