# -*- coding: utf-8 -*-
"""Фігури до теми «Контрольна сума CRC» (embedded-systems).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
GRAY_BG  = "#eef1f4"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=14, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def tb(cx, cy, s, **k):
    """textbox, повертає лише SVG-рядок."""
    body, w, h = textbox(cx, cy, s, **k)
    return body


def tbwh(cx, cy, s, **k):
    return textbox(cx, cy, s, **k)


def cell(x, y, w, h, s, fill=FILL, size=15, color=INK, bold=True):
    """Одна комірка-байт із текстом по центру."""
    r = rect(x, y, w, h, fill=fill)
    r += mono(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color,
              anchor="middle", bold=bold)
    return r


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: один такт програмної CRC (зсув + умовний XOR полінома)
# ─────────────────────────────────────────────────────────────────────────────
def fig_register_step():
    W, H = 820, 430
    frags = []

    # регістр — 8 комірок (наочно замість 16)
    bits = ['1', '0', '1', '1', '0', '0', '1', '0']
    cw, ch = 48, 48
    n = len(bits)
    x0 = 235
    ytop = 96
    frags.append(text(x0 + n * cw / 2, ytop - 16,
                      "Регістр CRC — біжуча остача (тут 8 біт для наочности)",
                      size=15, bold=True))
    for i, b in enumerate(bits):
        fill = RED_BG if i == 0 else FILL
        col = POS if i == 0 else INK
        frags.append(cell(x0 + i * cw, ytop, cw, ch, b, fill=fill, color=col))

    ymid = ytop + ch / 2

    # ліворуч: старший біт випадає
    frags.append(arrow(x0 - 6, ymid, x0 - 78, ymid, color=POS, sw=2.2))
    frags.append(circle(x0 - 104, ymid, 20, fill=RED_BG, stroke=POS, sw=2))
    frags.append(mono(x0 - 104, ymid + 6, "1", size=17, color=POS, anchor="middle", bold=True))
    frags.append(text(x0 - 104, ymid + 44, "старший біт,", size=12.5, color=MUTED))
    frags.append(text(x0 - 104, ymid + 61, "що випав", size=12.5, color=MUTED))

    # праворуч: вхідний біт входить
    xr = x0 + n * cw
    frags.append(arrow(xr + 78, ymid, xr + 6, ymid, color=NEG, sw=2.2))
    frags.append(text(xr + 96, ymid - 12, "вхідний", size=12.5, color=NEG, anchor="start"))
    frags.append(text(xr + 96, ymid + 5, "біт даних", size=12.5, color=NEG, anchor="start"))

    # стрілка вниз до правила
    cx = x0 + n * cw / 2
    frags.append(arrow(cx, ytop + ch + 6, cx, ytop + ch + 46, sw=2))

    # правило — дві гілки
    ry = ytop + ch + 118
    frags.append(tb(cx, ry,
                    "біт = 1   →   зсув ліворуч, тоді ⊕ поліном\n"
                    "біт = 0   →   тільки зсув ліворуч",
                    size=15, pad=16, fill=GRAY_BG))

    # підсумок
    frags.append(arrow(cx, ry + 40, cx, ry + 78, sw=2))
    frags.append(tb(cx, ry + 112,
                    "повторити для кожного біта даних  →  у регістрі лишиться CRC",
                    size=14.5, pad=14, fill=GREEN_BG, stroke=FIELD))

    out("crc-register-step.svg", W, H, *frags,
        title="Крок бітового CRC: зсув і, за старшим бітом, XOR полінома")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: профіль CRC як конвеєр із шести параметрів + контрольні значення
# ─────────────────────────────────────────────────────────────────────────────
def fig_params_pipeline():
    W, H = 1060, 400
    frags = []

    stages = [
        ("Байти\nданих", FILL),
        ("Відбиття\nвходу", BLUE_BG),
        ("Ядро\nзсув-XOR\n(старт · поліном)", AMBER_BG),
        ("Відбиття\nвиходу", BLUE_BG),
        ("Фінальний\nXOR", BLUE_BG),
        ("CRC", GREEN_BG),
    ]
    cy = 108
    centers = [95, 258, 448, 640, 800, 948]
    boxes = []
    for (lbl, fill), cx in zip(stages, centers):
        body, w, h = tbwh(cx, cy, lbl, size=14, pad=13, fill=fill,
                          stroke=(FIELD if fill == GREEN_BG else LINE))
        boxes.append((body, cx, w))

    # стрілки між рамками (малюємо ПІД рамками)
    for i in range(len(boxes) - 1):
        _, cxa, wa = boxes[i]
        _, cxb, wb = boxes[i + 1]
        frags.append(arrow(cxa + wa / 2 + 3, cy, cxb - wb / 2 - 3, cy, sw=2))
    for body, cx, w in boxes:
        frags.append(body)

    # підпис під конвеєром
    frags.append(text(W / 2, 178,
                      "Два кінці зійдуться, лише коли збіжаться ВСІ шість параметрів — сам поліном нічого не гарантує.",
                      size=13.5, color=MUTED))

    # таблиця контрольних значень
    ty = 226
    frags.append(text(150, ty - 8, "Контрольне значення — CRC рядка \"123456789\":",
                      size=14, bold=True, anchor="start"))
    rows = [
        "CRC-8/SMBus          поліном 0x07         →  0xF4",
        "CRC-8/Maxim (1-Wire)  поліном 0x31         →  0xA1",
        "CRC-16/CCITT-FALSE   поліном 0x1021       →  0x29B1",
        "CRC-16/Modbus        поліном 0x8005       →  0x4B37",
        "CRC-32 (zlib, PNG)   поліном 0x04C11DB7   →  0xCBF43926",
    ]
    for i, r in enumerate(rows):
        frags.append(mono(150, ty + 22 + i * 28, r, size=14.5, anchor="start"))

    out("crc-params-pipeline.svg", W, H, *frags,
        title="Профіль CRC — це конвеєр із шести параметрів")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: місце CRC у кадрі (перевірка за сталою остачею) + потокова перевірка
# ─────────────────────────────────────────────────────────────────────────────
def fig_frame_residue():
    W, H = 1080, 440
    frags = []

    # роздільник панелей
    frags.append(line(470, 60, 470, H - 30, color="#cfd6dd", sw=1.4, dash="5,5"))

    # ── ліва панель: перевірка кадру ────────────────────────────────────────
    frags.append(text(250, 62, "Перевірка кадру", size=16, bold=True))

    cw, chh = 50, 42
    fx, fy = 60, 84
    data_n, crc_n = 5, 2
    frags.append(text(fx + (data_n + crc_n) * cw / 2, fy - 12,
                      "кадр: корисні дані, а в хвості — CRC", size=13, color=MUTED))
    for i in range(data_n):
        frags.append(cell(fx + i * cw, fy, cw, chh, "дані", fill=FILL, size=13, bold=False))
    for i in range(crc_n):
        frags.append(cell(fx + (data_n + i) * cw, fy, cw, chh, "CRC",
                          fill=AMBER_BG, color=AMBER, size=13))

    cxL = fx + (data_n + crc_n) * cw / 2
    frags.append(arrow(cxL, fy + chh + 4, cxL, fy + chh + 40, sw=2))
    frags.append(tb(cxL, fy + chh + 74,
                    "регістр жене УВЕСЬ блок\n(дані + CRC)", size=13.5, pad=12, fill=GRAY_BG))
    frags.append(arrow(cxL, fy + chh + 108, cxL, fy + chh + 144, sw=2))
    frags.append(tb(cxL, fy + chh + 178,
                    "= наперед відома\nстала остача?", size=13.5, pad=12, fill=BLUE_BG))

    yb = fy + chh + 214
    frags.append(arrow(cxL - 40, yb, cxL - 120, yb + 30, color=FIELD, sw=2))
    frags.append(arrow(cxL + 40, yb, cxL + 120, yb + 30, color=POS, sw=2))
    frags.append(tb(cxL - 150, yb + 52, "збіглась →\nблок цілий", size=13, pad=11,
                    fill=GREEN_BG, stroke=FIELD))
    frags.append(tb(cxL + 150, yb + 52, "ні →\nблок битий", size=13, pad=11,
                    fill=RED_BG, stroke=POS))

    # ── права панель: потокова перевірка ────────────────────────────────────
    frags.append(text(772, 62, "Потокова перевірка образу", size=16, bold=True))

    pages = ["сторінка 1", "сторінка 2", "…", "остання"]
    pcx = [612, 704, 794, 884]
    py = 112
    for lbl, cx in zip(pages, pcx):
        frags.append(tb(cx, py, lbl, size=12.5, pad=9, fill=FILL))

    # єдиний регістр-смуга, у який течуть сторінки
    rbx, rby, rbw, rbh = 560, 186, 420, 46
    frags.append(rect(rbx, rby, rbw, rbh, fill=AMBER_BG, stroke=AMBER, sw=1.8))
    frags.append(text(rbx + rbw / 2, rby + rbh / 2 + 5,
                      "один регістр — значення переноситься між сторінками",
                      size=13, color=INK, bold=True))
    for cx in pcx:
        frags.append(arrow(cx, py + 20, cx, rby - 4, sw=1.6))

    # старт (тік згори-ліворуч), фінальний XOR (стрілка праворуч)
    frags.append(arrow(534, rby - 22, 534, rby - 2, color=NEG, sw=2))
    frags.append(text(534, rby - 30, "старт (раз)", size=12.5, color=NEG))
    frags.append(arrow(rbx + rbw + 4, rby + rbh / 2, rbx + rbw + 46, rby + rbh / 2, color=FIELD, sw=2))
    frags.append(text(rbx + rbw + 10, rby + rbh / 2 - 13, "фінальний", size=12, color=FIELD, anchor="start"))
    frags.append(text(rbx + rbw + 10, rby + rbh / 2 + 4, "XOR → CRC", size=12, color=FIELD, anchor="start"))

    frags.append(tb(772, rby + rbh + 58,
                    "увесь образ у RAM не тримаємо — лише регістр",
                    size=13.5, pad=12, fill=GREEN_BG, stroke=FIELD))

    out("crc-frame-residue.svg", W, H, *frags,
        title="Місце CRC у кадрі й потокова перевірка образу")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 (вставка hist-rocksoft): один многочлен — п'ять різних чисел
# ─────────────────────────────────────────────────────────────────────────────
def fig_poly_spellings():
    W, H = 1020, 430
    frags = []

    frags.append(text(W / 2, 74, "x¹⁶ + x¹² + x⁵ + 1  —  один і той самий многочлен",
                      size=18, bold=True))
    frags.append(line(90, 96, W - 90, 96, color="#cfd6dd", sw=1.4))

    rows = [
        ("0x11021", "повний запис: усі 17 бітів, старша одиниця на місці"),
        ("0x1021",  "«нормальний»: старша одиниця неявна, її відкинули"),
        ("0x8408",  "відбиті молодші 16 бітів — для правозсувного коду"),
        ("0x0811",  "відбито всі 17 бітів, тоді відкинуто старший"),
        ("0x8810",  "відкинуто не старшу одиницю, а МОЛОДШУ (запис Купмана)"),
    ]
    y0, dy = 140, 46
    for i, (hx, why) in enumerate(rows):
        y = y0 + i * dy
        frags.append(mono(210, y, hx, size=18, anchor="middle", bold=True, color=NEG))
        frags.append(text(320, y, why, size=14.5, color=INK, anchor="start"))

    frags.append(line(90, y0 + 4 * dy + 26, W - 90, y0 + 4 * dy + 26,
                      color="#cfd6dd", sw=1.4))
    frags.append(text(W / 2, y0 + 4 * dy + 62,
                      "Даташит подає одне з цих чисел — і майже ніколи не каже, яке саме.",
                      size=14.5, color=MUTED))

    out("crc-poly-spellings.svg", W, H, *frags,
        title="П'ять записів одного полінома")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 (вставка hist-rocksoft): шлях від теорії коду до номенклатури
# ─────────────────────────────────────────────────────────────────────────────
def fig_rocksoft_timeline():
    W, H = 1020, 640
    frags = []

    xline = 258
    frags.append(line(xline, 76, xline, H - 44, color="#cfd6dd", sw=2.4))

    events = [
        ("1961", "Пітерсон і Браун друкують «Cyclic Codes for Error Detection».\n"
                 "Код задано многочленом — теорії більше нічого й не треба."),
        ("1970-ті\n— 80-ті", "Табличні реалізації розходяться вендорськими записками\n"
                             "й журналами; UART-и накидають відбитий порядок бітів."),
        ("1988", "Сарвате друкує табличний метод у CACM: код став швидким,\n"
                 "але копіювали саме код, а не опис — описів не було."),
        ("1993", "Росс Вільямс: модель Rocksoft — шість параметрів\n"
                 "плюс контрольне значення для рядка «123456789»."),
        ("2002\nі 2004", "Купман рахує відстань Геммінга поліномів для реальних\n"
                         "довжин кадру: стало відомо, ЯКИЙ поліном брати."),
        ("2011", "Ґреґ Кук відкриває каталог параметризованих CRC і RevEng:\n"
                 "додано residue й ступінь засвідченості кожного профілю."),
    ]
    y = 116
    for year, body in events:
        frags.append(circle(xline, y, 10, fill=AMBER_BG, stroke=AMBER, sw=2.4))
        yl = year.split("\n")
        ty = y - (len(yl) - 1) * 16 * 1.3 / 2 + 6
        frags.append(mtext(150, ty, yl, size=16, bold=True, color=INK))
        frags.append(fitbox(300, y - 33, 660, 66, body, size=14.5, pad=14,
                            fill=FILL, stroke=LINE))
        y += 88

    out("crc-rocksoft-timeline.svg", W, H, *frags,
        title="Тридцять два роки від коду до його назви")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (вставка proj): три шляхи до таблиці й куди вона лягає в пам'яті
# ─────────────────────────────────────────────────────────────────────────────
def fig_table_routes():
    W, H = 1180, 600
    frags = []

    cols = [
        (205, "Порахувати на старті\n(код у прошивці)", RED_BG, POS,
         ["RAM: 1 КБ", "старт: тисячі тактів", "+ прапорець «готова?»"]),
        (590, "Порахувати скриптом\nна етапі збірки", GREEN_BG, FIELD,
         ["RAM: 0", "старт: 0", "ціна: крок у зборці"]),
        (975, "Порахувати компілятором\n(constexpr)", GREEN_BG, FIELD,
         ["RAM: 0", "старт: 0", "ціна: потрібен C++17"]),
    ]

    for cx, lbl, fill, stroke, costs in cols:
        frags.append(tb(cx, 92, lbl, size=14.5, pad=13, fill=fill, stroke=stroke))
        for i, c in enumerate(costs):
            frags.append(mono(cx, 152 + i * 25, c, size=13.5, color=MUTED, anchor="middle"))

    # стрілки вниз до смуги пам'яті
    frags.append(arrow(205, 240, 205, 296, color=POS, sw=2))
    frags.append(arrow(590, 240, 620, 296, color=FIELD, sw=2))
    frags.append(arrow(975, 240, 890, 296, color=FIELD, sw=2))

    # смуга пам'яті: RAM ліворуч, FLASH праворуч
    frags.append(rect(75, 300, 265, 128, fill=RED_BG, stroke=POS, sw=2))
    frags.append(text(207, 330, "RAM  ·  .bss", size=15, bold=True, color=POS))
    frags.append(text(207, 360, "таблиця з'їдає оперативку", size=13, color=INK))
    frags.append(text(207, 382, "і рахується на кожному", size=13, color=INK))
    frags.append(text(207, 404, "старті наново", size=13, color=INK))

    frags.append(rect(430, 300, 675, 128, fill=GREEN_BG, stroke=FIELD, sw=2))
    frags.append(text(767, 330, "FLASH  ·  .rodata", size=15, bold=True, color=FIELD))
    frags.append(text(767, 360, "таблиця лежить у флеші й читається звідти напряму:", size=13, color=INK))
    frags.append(text(767, 382, "оперативка не витрачена, старт нічого не коштує,", size=13, color=INK))
    frags.append(text(767, 404, "у гарячому циклі нема чого перевіряти", size=13, color=INK))

    # застереження
    frags.append(tb(W / 2, 508,
                    "Забули const → таблиця лягає в .data: 1 КБ флешу І 1 КБ RAM,\n"
                    "ще й копіюється стартовим кодом. На AVR навіть const живе\n"
                    "в RAM — там потрібен PROGMEM і pgm_read_dword.",
                    size=14, pad=15, fill=AMBER_BG, stroke=AMBER))

    out("crc-table-routes.svg", W, H, *frags,
        title="Три шляхи до таблиці CRC — і куди вона лягає в пам'яті")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (вставка proj): напівбайтова таблиця — 32 байти замість 512
# ─────────────────────────────────────────────────────────────────────────────
def fig_nibble_table():
    W, H = 1040, 500
    frags = []

    # байт розпадається на два півбайти
    frags.append(tb(140, 112, "байт даних\n0x9C", size=14.5, pad=13, fill=FILL))
    frags.append(arrow(212, 98, 296, 78, sw=1.8))
    frags.append(arrow(212, 126, 296, 152, sw=1.8))
    frags.append(tb(410, 76, "молодший півбайт  0xC", size=13.5, pad=11, fill=BLUE_BG))
    frags.append(tb(410, 154, "старший півбайт  0x9", size=13.5, pad=11, fill=BLUE_BG))
    frags.append(circle(280, 62, 15, fill=AMBER_BG, stroke=AMBER, sw=1.8))
    frags.append(mono(280, 67, "1", size=14, color=AMBER, anchor="middle", bold=True))
    frags.append(circle(280, 170, 15, fill=AMBER_BG, stroke=AMBER, sw=1.8))
    frags.append(mono(280, 175, "2", size=14, color=AMBER, anchor="middle", bold=True))
    frags.append(tb(820, 115, "порядок важить:\nу відбитій формі спершу\nйде молодший півбайт",
                    size=13.5, pad=13, fill=GRAY_BG))

    # дві дії над регістром
    frags.append(mono(95, 240, "крок 1:  crc = (crc >> 4) ^ nib[(crc ^ b) & 0x0F]",
                      size=14, anchor="start"))
    frags.append(mono(95, 270, "крок 2:  crc = (crc >> 4) ^ nib[(crc ^ (b >> 4)) & 0x0F]",
                      size=14, anchor="start"))

    # сама таблиця — 16 комірок
    frags.append(text(W / 2, 318, "nib[16] — уся таблиця: 16 записів по 2 байти",
                      size=14, bold=True))
    cw, chh = 46, 40
    x0 = (W - 16 * cw) / 2
    for i in range(16):
        frags.append(cell(x0 + i * cw, 334, cw, chh, "%X" % i, fill=FILL, size=13, bold=False))

    frags.append(tb(W / 2, 438,
                    "32 байти замість 512 — ціна: два пошуки на байт замість одного",
                    size=14.5, pad=14, fill=GREEN_BG, stroke=FIELD))

    out("crc-nibble-table.svg", W, H, *frags,
        title="Напівбайтова таблиця: байт заходить двома половинками")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 8 (вставка api-hw-crc): кремній проти софту — де бракує ланок
# ─────────────────────────────────────────────────────────────────────────────
def fig_hw_silicon_vs_soft():
    W, H = 1180, 560
    frags = []

    SOFT_LBL = "софт"
    SIL_LBL = "кремній"

    def lane(y0, title, subtitle, steps):
        """steps = [(kind, [рядки]), …]; kind ∈ 'soft'|'sil'|'data'"""
        f = [text(60, y0, title, size=17, bold=True, anchor="start"),
             text(60, y0 + 24, subtitle, size=13.5, color=MUTED, anchor="start")]
        x = 60
        cy = y0 + 96
        boxes = []
        for kind, lines in steps:
            if kind == "sil":
                fill, stroke = BLUE_BG, NEG
            elif kind == "soft":
                fill, stroke = AMBER_BG, AMBER
            else:
                fill, stroke = GRAY_BG, LINE
            body, w, h = tbwh(0, cy, "\n".join(lines), size=13, pad=11,
                              fill=fill, stroke=stroke, sw=1.8)
            boxes.append((body, w, h, kind))
        total = sum(b[1] for b in boxes)
        gap = (W - 120 - total) / (len(boxes) - 1)
        for i, (body, w, h, kind) in enumerate(boxes):
            cx = x + w / 2
            # перемалювати рамку в потрібному x (textbox малює навколо cx=0)
            if kind == "sil":
                fill, stroke = BLUE_BG, NEG
            elif kind == "soft":
                fill, stroke = AMBER_BG, AMBER
            else:
                fill, stroke = GRAY_BG, LINE
            lines = steps[i][1]
            f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.8))
            ty = cy - (len(lines) - 1) * 13 * 1.3 / 2 + 13 * 0.35
            f.append(mtext(cx, ty, lines, size=13))
            if kind in ("sil", "soft"):
                tag = SIL_LBL if kind == "sil" else SOFT_LBL
                f.append(text(cx, cy - h / 2 - 10, tag, size=12,
                              color=(NEG if kind == "sil" else AMBER), bold=True))
            if i < len(boxes) - 1:
                f.append(arrow(cx + w / 2 + 6, cy, cx + w / 2 + gap - 6, cy))
            x += w + gap
        return f

    frags += lane(48,
                  "Фіксований блок — STM32 F1, F4",
                  "у кремнії лише ядро: poly 0x04C11DB7, старт 0xFFFFFFFF, старшим бітом уперед",
                  [("data", ["байти", "в пам'яті"]),
                   ("soft", ["__RBIT кожного", "32-бітного слова"]),
                   ("sil", ["CRC_DR ←", "ядро зсув-XOR", "(без відбиття)"]),
                   ("soft", ["__RBIT(CRC_DR)", "^ 0xFFFFFFFF"]),
                   ("data", ["CRC-32", "як у zlib"])])

    frags.append(line(60, 300, W - 60, 300, color="#c9ced6", sw=1.2, dash="6 6"))

    frags += lane(330,
                  "Конфігурований блок — STM32 F3, L4, G4, H7 …",
                  "у кремнії ще й відбиття та власні POL/INIT — лишається один XOR",
                  [("data", ["байти", "в пам'яті"]),
                   ("sil", ["CRC_DR ←", "REV_IN"]),
                   ("sil", ["ядро: POL,", "INIT, POLYSIZE"]),
                   ("sil", ["REV_OUT", "→ CRC_DR"]),
                   ("soft", ["^ 0xFFFFFFFF"]),
                   ("data", ["CRC-32", "як у zlib"])])

    frags.append(tb(W / 2, 522,
                    "Фінального XOR у кремнії немає НІКОЛИ — жодна родина STM32 його не має",
                    size=15, pad=14, fill=RED_BG, stroke=POS, bold=True))

    out("crc-hw-silicon-vs-soft.svg", W, H, *frags,
        title="Апаратний CRC: що робить кремній, а що доводиться доробляти")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 9 (вставка api-hw-crc): розкладка бітів CRC_CR
# ─────────────────────────────────────────────────────────────────────────────
def fig_hw_cr_bits():
    W, H = 1060, 470
    frags = [text(W / 2, 44, "CRC_CR — керівний регістр (зсув 0x08)", size=18, bold=True)]

    # смуга бітів 15…0 (старші 31…16 — зарезервовані, показуємо однією коміркою)
    bw, bh = 52, 54
    x0 = 150
    y = 96
    frags.append(rect(60, y, 80, bh, fill=GRAY_BG))
    frags.append(text(100, y + bh / 2 + 5, "31…16", size=13, color=MUTED))

    fields = {7: ("REV_OUT", GREEN_BG, FIELD), 6: ("REV_IN", AMBER_BG, AMBER),
              5: ("REV_IN", AMBER_BG, AMBER), 4: ("POLYSIZE", BLUE_BG, NEG),
              3: ("POLYSIZE", BLUE_BG, NEG), 0: ("RESET", RED_BG, POS)}
    for i in range(16):
        b = 15 - i
        x = x0 + i * bw
        if b in fields:
            _, fill, stroke = fields[b]
        else:
            fill, stroke = GRAY_BG, LINE
        frags.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=1.6))
        frags.append(mono(x + bw / 2, y + bh / 2 + 5, str(b), size=15,
                          anchor="middle", bold=(b in fields)))

    # підписи полів під смугою (кожен — під своїми комірками, з полем)
    def label(b_hi, b_lo, s, color):
        xl = x0 + (15 - b_hi) * bw
        xr = x0 + (15 - b_lo + 1) * bw
        cx = (xl + xr) / 2
        f = [line(xl + 3, y + bh + 8, xr - 3, y + bh + 8, color=color, sw=2)]
        f.append(text(cx, y + bh + 30, s, size=13.5, color=color, bold=True))
        return f

    frags += label(7, 7, "REV_OUT", FIELD)
    frags += label(6, 5, "REV_IN[1:0]", AMBER)
    frags += label(4, 3, "POLYSIZE[1:0]", NEG)
    frags += label(0, 0, "RESET", POS)

    # три колонки з кодуванням — широкі, з полями
    cy = 262
    col_w = 300
    cols = [
        (150, "POLYSIZE[1:0] — ширина", NEG, BLUE_BG,
         ["00 → 32 біти", "01 → 16 бітів", "10 → 8 бітів", "11 → 7 бітів"]),
        (530, "REV_IN[1:0] — відбиття входу", AMBER, AMBER_BG,
         ["00 → без відбиття", "01 → у межах байта", "10 → у межах півслова",
          "11 → у межах слова"]),
        (910, "REV_OUT — відбиття виходу", FIELD, GREEN_BG,
         ["0 → як є", "1 → біти результату", "        перевертаються"]),
    ]
    for cx, head, color, fill, rows in cols:
        frags.append(text(cx, cy, head, size=14, bold=True, color=color))
        frags.append(rect(cx - col_w / 2, cy + 14, col_w, 26 * len(rows) + 22,
                          fill=fill, stroke=color, sw=1.6))
        for i, r in enumerate(rows):
            frags.append(mono(cx - col_w / 2 + 20, cy + 44 + i * 26, r, size=14,
                              anchor="start"))

    frags.append(tb(W / 2, 430,
                    "RESET = 1 не обнуляє регістр — він перезавантажує в CRC_DR вміст CRC_INIT",
                    size=14.5, pad=13, fill=RED_BG, stroke=POS, bold=True))

    out("crc-hw-cr-bits.svg", W, H, *frags,
        title="CRC_CR: розкладка бітів і кодування полів")


if __name__ == "__main__":
    fig_register_step()
    fig_params_pipeline()
    fig_frame_residue()
    fig_poly_spellings()
    fig_rocksoft_timeline()
    fig_table_routes()
    fig_nibble_table()
    fig_hw_silicon_vs_soft()
    fig_hw_cr_bits()
    print("OK: figures written to", IMG)
