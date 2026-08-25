# -*- coding: utf-8 -*-
"""Фігури до теми «Проєктування пакета».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
SYNCc = POS          # SYNC — гаряча позначка старту
LENc  = "#b9770e"    # LEN — тепле, але читабельне
IDc   = NEG          # ID/TYPE — холодне
DATAc = INK          # дані — нейтральне
CRCc  = FIELD        # CRC — зелене (цілість)
GREY  = "#9aa0a8"    # сміття / невідоме


def _cell(f, x, y, w, h, top, val, color, valcol=INK):
    """Клітинка байта: верхня мітка поля + значення всередині рамки."""
    f.append(rect(x, y, w, h, fill="#fcfcfd", stroke=color, sw=1.7))
    if top:
        f.append(text(x + w / 2, y - 7, top, size=10.5, color=color, bold=True))
    f.append(text(x + w / 2, y + h / 2 + 5, val, size=12.5, color=valcol, bold=True))


# ── 1. Сирий потік не має меж ────────────────────────────────────────────────
def fig_noboundary():
    W, H = 720, 300
    f = [text(W / 2, 26, "Сирий потік возить байти, а не повідомлення", size=15, bold=True)]

    vals = ["12", "41", "42", "07", "FF", "41", "42", "09", "3C"]
    x0, y, w, gap = 70, 96, 58, 4
    for i, v in enumerate(vals):
        x = x0 + i * (w + gap)
        f.append(rect(x, y, w, 42, fill=FILL, stroke=GREY, sw=1.4))
        f.append(text(x + w / 2, y + 27, v, size=13, bold=True))
    right = x0 + len(vals) * (w + gap) - gap

    # вісь часу
    f.append(arrow(x0, y + 70, right, y + 70, color=INK, sw=1.6))
    f.append(text(right + 6, y + 74, "час →", size=11, color=MUTED, anchor="start"))

    # дві суперечливі межі
    c1 = x0 + 3 * (w + gap) - gap / 2
    c2 = x0 + 5 * (w + gap) - gap / 2
    f.append(line(c1, y - 14, c1, y + 58, color=LENc, sw=1.6, dash="4,3"))
    f.append(line(c2, y - 14, c2, y + 58, color=LENc, sw=1.6, dash="4,3"))
    f.append(text((c1 + c2) / 2, y - 20, "тут початок? чи тут?", size=11, color=LENc, bold=True))

    note = ("той самий потік нарізається на повідомлення по-різному — "
            "і для UART усі поділи однаково правомірні")
    f.append(fitbox(60, 220, 600, 52, note, size=12, color=INK,
                    fill=FILL, stroke=GREY, sw=1.3))
    render(os.path.join(IMG, "noboundary.svg"), W, H, *f)


# ── 2. Анатомія пакета ───────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 760, 340
    f = [text(W / 2, 26, "Анатомія пакета: SYNC · LEN · ID · дані · CRC", size=15, bold=True)]

    y, h = 86, 48
    fields = [
        ("SYNC", "0xAA", 86,  SYNCc),
        ("LEN",  "0x03", 158, LENc),
        ("ID",   "0x12", 230, IDc),
        ("DATA", "0x41", 302, DATAc),
        ("DATA", "0x42", 374, DATAc),
        ("DATA", "0x43", 446, DATAc),
        ("CRC",  "0x6C", 518, CRCc),
    ]
    w = 64
    for top, val, x, col in fields:
        _cell(f, x, y, w, h, top, val, col, valcol=INK)
    crc_lo = 158          # LEN
    crc_hi = 446 + w      # кінець останнього DATA

    # дужка «CRC рахується по цих байтах»
    by = y + h + 22
    f.append(line(crc_lo, by, crc_hi, by, color=CRCc, sw=1.6))
    f.append(line(crc_lo, by - 6, crc_lo, by, color=CRCc, sw=1.6))
    f.append(line(crc_hi, by - 6, crc_hi, by, color=CRCc, sw=1.6))
    f.append(text((crc_lo + crc_hi) / 2, by + 16, "CRC рахують по цьому: від LEN до останнього байта даних",
                  size=11, color=CRCc, bold=True))

    # легенда
    leg = [
        (SYNCc, "SYNC — стала позначка початку (одна чи дві)"),
        (LENc,  "LEN — скільки байтів даних далі (де кінець)"),
        (IDc,   "ID/TYPE — що це за повідомлення (необов'язково)"),
        (CRCc,  "CRC — контроль цілості всього пакета"),
    ]
    ly = 196
    for col, s in leg:
        f.append(circle(96, ly, 5, fill=col, stroke=col, sw=0))
        f.append(text(110, ly + 4, s, size=11.5, anchor="start"))
        ly += 24

    f.append(text(W / 2, 322,
                  "обов'язкового стандарту немає — структуру задаєш ти; головне, щоб обидві сторони знали її однаково",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 3. Дві стратегії меж: роздільник чи довжина ──────────────────────────────
def fig_framing():
    W, H = 760, 360
    f = [text(W / 2, 26, "Дві стратегії меж: роздільник проти поля довжини", size=15, bold=True)]

    # ── роздільник
    f.append(text(40, 70, "роздільник (напр. 0x0A = '\\n')", size=12.5, bold=True, anchor="start"))
    vals = [("48", DATAc), ("49", DATAc), ("0A", SYNCc), ("4F", DATAc), ("0A", SYNCc)]
    x0, y, w, gap = 40, 82, 58, 4
    for i, (v, col) in enumerate(vals):
        x = x0 + i * (w + gap)
        fill = "#fdecea" if col is SYNCc else "#fcfcfd"
        f.append(rect(x, y, w, 38, fill=fill, stroke=col, sw=1.5))
        f.append(text(x + w / 2, y + 24, v, size=12.5, color=(SYNCc if col is SYNCc else INK), bold=True))
    f.append(text(x0 + 5 * (w + gap) + 4, y + 24, "← пастка: 0x0A у даних = хибний кінець",
                  size=11, color=SYNCc, bold=True, anchor="start"))

    f.append(fitbox(40, 138, 680, 44,
                    "двійкові дані можуть містити байт-роздільник →\n"
                    "потрібне екранування (byte stuffing; елегантно — COBS)",
                    size=11.5, color=INK, fill="#fdecea", stroke=SYNCc, sw=1.3))

    # ── поле довжини
    f.append(text(40, 226, "поле довжини", size=12.5, bold=True, anchor="start"))
    y2 = 238
    f.append(rect(x0, y2, w, 38, fill="#fdf6e8", stroke=LENc, sw=1.5))
    f.append(text(x0 + w / 2, y2 + 24, "LEN=3", size=12, color=LENc, bold=True))
    for i, v in enumerate(["D", "A", "T"]):
        x = x0 + (i + 1) * (w + gap)
        f.append(rect(x, y2, w, 38, fill="#fcfcfd", stroke=IDc, sw=1.5))
        f.append(text(x + w / 2, y2 + 24, v, size=12.5, bold=True))
    f.append(text(x0 + 4 * (w + gap) + 4, y2 + 24, "→ читаємо рівно 3 байти; які саме — байдуже",
                  size=11, color=CRCc, bold=True, anchor="start"))

    f.append(fitbox(40, 294, 680, 50,
                    "для тексту зручний роздільник (рядок = повідомлення); для двійкових даних — поле довжини;\n"
                    "найнадійніше — поєднати: SYNC для старту, LEN для кінця",
                    size=11.5, color=INK, fill=FILL, stroke=GREY, sw=1.3))
    render(os.path.join(IMG, "framing.svg"), W, H, *f)


# ── 4. SYNC і самовідновлення ────────────────────────────────────────────────
def fig_resync():
    W, H = 760, 300
    f = [text(W / 2, 26, "SYNC: знайти початок після збою чи підключення посеред потоку", size=14, bold=True)]

    cells = [
        ("сміття", "…", GREY, "#f1f2f4"),
        (None, "3F", GREY, "#f1f2f4"),
        (None, "91", GREY, "#f1f2f4"),
        ("SYNC!", "AA", SYNCc, "#fdecea"),
        ("LEN", "03", LENc, "#fdf6e8"),
        ("ID", "12", IDc, "#fcfcfd"),
        (None, "41", DATAc, "#fcfcfd"),
        (None, "42", DATAc, "#fcfcfd"),
        ("CRC", "6C", CRCc, "#eef6ef"),
    ]
    x0, y, w, gap, h = 56, 96, 70, 4, 44
    sync_x = x0 + 3 * (w + gap)
    for i, (top, val, col, fill) in enumerate(cells):
        x = x0 + i * (w + gap)
        valcol = MUTED if col is GREY else INK
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.6))
        if top:
            f.append(text(x + w / 2, y - 7, top, size=10.5, color=col, bold=True))
        f.append(text(x + w / 2, y + h / 2 + 5, val, size=12.5, color=valcol, bold=True))
    right = x0 + len(cells) * (w + gap) - gap

    by = y + h + 18
    f.append(arrow(sync_x, by, x0, by, color=GREY, sw=1.5))
    f.append(text((x0 + sync_x) / 2, by + 16, "відкинуто (шукаємо SYNC)", size=11, color=MUTED, italic=True))
    f.append(line(sync_x, by, right, by, color=CRCc, sw=1.6))
    f.append(line(sync_x, by - 6, sync_x, by, color=CRCc, sw=1.6))
    f.append(line(right, by - 6, right, by, color=CRCc, sw=1.6))
    f.append(text((sync_x + right) / 2, by + 16, "пакет від SYNC до CRC", size=11, color=CRCc, bold=True))

    f.append(fitbox(56, 230, 648, 50,
                    "одна зіпсована посилка не валить зв'язок назавжди: наступний SYNC дає почати наново;\n"
                    "тому SYNC часто двобайтовий (0xAA 0x55) — рідше плутати з даними",
                    size=11.5, color=INK, fill=FILL, stroke=GREY, sw=1.3))
    render(os.path.join(IMG, "resync.svg"), W, H, *f)


# ── 5. Проста сума проти CRC ─────────────────────────────────────────────────
def fig_checksum_crc():
    W, H = 720, 320
    f = [text(W / 2, 26, "Проста сума сліпа до перестановки — CRC її ловить", size=15, bold=True)]

    def row(y, label, bytes_, xorval, crcval, xorcol, crccol, xornote, crcnote):
        f.append(text(40, y - 24, label, size=12, bold=True, anchor="start"))
        x0, w, gap = 40, 56, 6
        for i, b in enumerate(bytes_):
            x = x0 + i * (w + gap)
            f.append(rect(x, y, w, 36, fill="#fcfcfd", stroke=IDc, sw=1.4))
            f.append(text(x + w / 2, y + 24, b, size=12.5, bold=True))
        bx = x0 + len(bytes_) * (w + gap) + 16
        f.append(text(bx, y + 16, "XOR = " + xorval, size=12.5, color=xorcol, bold=True, anchor="start"))
        f.append(text(bx, y + 33, xornote, size=10, color=xorcol, italic=True, anchor="start"))
        cx = bx + 210
        f.append(text(cx, y + 16, "CRC = " + crcval, size=12.5, color=crccol, bold=True, anchor="start"))
        f.append(text(cx, y + 33, crcnote, size=10, color=crccol, italic=True, anchor="start"))

    row(96, "пакет А", ["41", "42", "43"], "0x40", "0x52", LENc, CRCc, "", "")
    row(176, "пакет Б (1-й↔3-й)", ["43", "42", "41"], "0x40", "0x8A", POS, CRCc,
        "та сама — сума не бачить перестановки", "інша — CRC ловить")

    f.append(fitbox(60, 238, 600, 64,
                    "XOR-сума не зважає на порядок (переставив байти — сума та сама)\n"
                    "і пропускає компенсовані помилки; CRC залежить від значень І позицій\n"
                    "бітів, тож ловить майже все це",
                    size=11.5, color=INK, fill=FILL, stroke=GREY, sw=1.3))
    render(os.path.join(IMG, "checksum-crc.svg"), W, H, *f)


# ── 6. Як працює CRC: ділення за модулем 2 ───────────────────────────────────
def fig_crc_div():
    W, H = 720, 372
    f = [text(W / 2, 26, "CRC = остача від ділення за модулем 2 (XOR)", size=15, bold=True)]

    # стовпчик ділення
    rows = [
        ("1101000", "дані 1101 + три нулі", INK, 0),
        ("1011",    "⊕ генератор 1011 (x³+x+1)", POS, 0),
        ("0110000", None, MUTED, 0),
        ("1011",    None, POS, 1),
        ("0011100", None, MUTED, 0),
        ("1011",    None, POS, 2),
        ("0001010", None, MUTED, 0),
        ("1011",    None, POS, 3),
        ("0000001", "остача = 001 = CRC", CRCc, 0),
    ]
    x0, y, dx, lh = 130, 78, 13, 26
    for bits, note, col, shift in rows:
        s = " " * shift + bits
        # моноширинний рядок бітів
        for j, ch in enumerate(s):
            if ch == " ":
                continue
            f.append(text(x0 + j * dx, y, ch, size=15, color=col, bold=True))
        if note:
            f.append(text(x0 + 9 * dx + 18, y, note, size=11, color=col, anchor="start", italic=(col != CRCc)))
        y += lh

    f.append(line(x0 - 6, 92, x0 + 7 * dx, 92, color=MUTED, sw=1.2))

    f.append(fitbox(60, 306, 600, 54,
                    "передаємо 1101 001; на прийомі ділимо весь рядок 1101001 на той самий\n"
                    "генератор — остача 0 означає «цілий», ненульова — пакет відкидаємо",
                    size=11.5, color=INK, fill=FILL, stroke=GREY, sw=1.3))
    render(os.path.join(IMG, "crc-div.svg"), W, H, *f)


# ── 7. Збирання й перевірка на прийомі ───────────────────────────────────────
def fig_receive():
    W, H = 760, 290
    f = [text(W / 2, 26, "Прийом і перевірка: рішення — лише після CRC", size=15, bold=True)]

    steps = [
        ("чекати\nSYNC", SYNCc),
        ("прочитати\nLEN", LENc),
        ("зібрати LEN\nбайтів", IDc),
        ("прочитати\nCRC", DATAc),
        ("звірити\nCRC", CRCc),
    ]
    x, y, w, h, gap = 30, 78, 112, 56, 22
    centers = []
    for label, col in steps:
        f.append(rect(x, y, w, h, fill=FILL, stroke=col, sw=1.7))
        f.append(mtext(x + w / 2, y + 24, label.split("\n"), size=12, color=col, bold=True))
        centers.append(x + w / 2)
        x += w + gap
    for i in range(len(steps) - 1):
        f.append(arrow(centers[i] + w / 2, y + h / 2, centers[i + 1] - w / 2, y + h / 2, color=INK, sw=1.8))

    # дві гілки з останнього кроку
    lastx = centers[-1]
    by = y + h + 18
    f.append(arrow(lastx, y + h, lastx, by, color=INK, sw=1.6))
    f.append(line(lastx, by, lastx - 160, by, color=INK, sw=1.4))
    f.append(arrow(lastx - 160, by, lastx - 160, by + 16, color=CRCc, sw=1.6))
    f.append(arrow(lastx, by, lastx, by + 16, color=POS, sw=1.6))
    f.append(fitbox(lastx - 230, by + 16, 140, 30, "збіг → у роботу",
                    size=11, color=CRCc, bold=True, fill="#eef6ef", stroke=CRCc, sw=1.3))
    f.append(fitbox(lastx - 66, by + 16, 150, 30, "не збіг → відкинути",
                    size=11, color=POS, bold=True, fill="#fdecea", stroke=POS, sw=1.3))

    f.append(text(W / 2, 280,
                  "побитий пакет не калічить систему — його тихо відкидають, наступний SYNC дає шанс почати спочатку",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "receive.svg"), W, H, *f)


if __name__ == "__main__":
    fig_noboundary()
    fig_anatomy()
    fig_framing()
    fig_resync()
    fig_checksum_crc()
    fig_crc_div()
    fig_receive()
    print("OK: 7 figures ->", IMG)
