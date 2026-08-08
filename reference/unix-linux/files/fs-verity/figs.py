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
GREY_FILL = "#eceff3"
WARM = "#b8860b"


def strip(x, y, w, h, cells, hi, fill, stroke):
    """Ряд однакових клітинок; одна підсвічена червоним."""
    out = ""
    cw = w / float(cells)
    for i in range(cells):
        f = RED_FILL if i == hi else fill
        s = POS if i == hi else stroke
        out += rect(x + i * cw, y, cw, h, fill=f, stroke=s,
                    sw=2.2 if i == hi else 1.2, rx=3)
    return out


def hi_center(x, w, cells, hi):
    cw = w / float(cells)
    return x + (hi + 0.5) * cw


# ── 1. Дерево над файлом і шлях перевірки одного блока ──────────────────────
def fig_merkle_shape():
    W, H = 1300, 800
    p = [text(W / 2, 42, "дерево над файлом на 300 МіБ і шлях перевірки одного блока даних",
              size=17, bold=True, color=INK)]

    SX, SW, SH = 300, 560, 52
    LX = 285          # правий край підписів ліворуч
    NX, NW = 900, 360  # колонка пояснень праворуч
    CELLS = 8

    rows = [
        # (y, підпис ліворуч, індекс підсвіченої клітинки, заливка, обвід, пояснення праворуч)
        (620, ["дані файлу", "76 800 блоків по 4 КіБ"], 6, GREEN_FILL, FIELD,
         ["читаємо один блок даних", "решти файлу не торкаємось"]),
        (500, ["рівень 0 дерева", "76 800 гешів = 600 блоків"], 4, BLUE_FILL, NEG,
         ["у кожному блоці — 128 гешів", "по 32 байти (SHA-256)"]),
        (380, ["рівень 1 дерева", "600 гешів = 5 блоків"], 2, BLUE_FILL, NEG,
         ["128 разів менше блоків,", "ніж на рівні нижче"]),
        (260, ["рівень 2 — корінь", "5 гешів = 1 блок"], 0, WARM_FILL, WARM,
         ["далі стискати нема куди:", "усе вмістилось в один блок"]),
    ]

    for y, lbl, hi, fill, stroke, note in rows:
        p.append(strip(SX, y, SW, SH, CELLS, hi, fill, stroke))
        p.append(mtext(LX, y + SH / 2 - 4, lbl, size=13.5, color=INK, anchor="end"))
        p.append(fitbox(NX, y - 2, NW, SH + 4, note, size=12.5, pad=10,
                        fill=FILL, stroke=LINE, sw=1.1))

    # шлях перевірки: знизу вгору по підсвічених клітинках
    for i in range(len(rows) - 1):
        y_lo, _, hi_lo = rows[i][0], None, rows[i][2]
        y_hi, hi_up = rows[i + 1][0], rows[i + 1][2]
        p.append(arrow(hi_center(SX, SW, CELLS, hi_lo), y_lo - 6,
                       hi_center(SX, SW, CELLS, hi_up), y_hi + SH + 8,
                       color=POS, sw=2.2))

    # корінь → дескриптор → цифра
    p.append(fitbox(SX, 150, SW, 62,
                    ["геш кореневого блока — root_hash"],
                    size=14, pad=10, bold=True, fill=WARM_FILL, stroke=WARM, sw=2))
    p.append(arrow(hi_center(SX, SW, CELLS, 0), 254, SX + 90, 218, color=WARM, sw=2))

    p.append(fitbox(NX, 150, NW, 62,
                    ["дескриптор: версія, алгоритм,", "розмір блока, сіль, розмір файлу"],
                    size=12.5, pad=10, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(SX + SW + 10, 181, NX - 10, 181, color=MUTED, sw=1.8))

    p.append(fitbox(SX, 74, SW + 30, 58,
                    ["цифра файлу = геш дескриптора: 32 байти на весь файл"],
                    size=14, pad=10, bold=True, fill=RED_FILL, stroke=POS, sw=2.2))
    p.append(arrow(NX + NW / 2, 146, SX + SW / 2 + 60, 136, color=POS, sw=2))

    p.append(fitbox(300, 700, 900, 74,
                    ["щоб довіритись одному блоку даних, треба три блоки дерева — 12 КіБ, а не 300 МіБ;",
                     "верхні рівні спільні для всього файлу, тож після першого читання вони вже в кеші"],
                    size=13.5, pad=12, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'merkle-shape.svg'), W, H, *p)


# ── 2. Де саме стоїть перевірка на шляху читання ────────────────────────────
def fig_read_gate():
    W, H = 1180, 720
    p = [text(W / 2, 42, "перевірка стоїть не на відкритті файлу, а на вході сторінки в кеш",
              size=17, bold=True, color=INK)]

    CX, CW = 330, 520

    p.append(fitbox(CX, 78, CW, 58, ["read() або дотик до відображеної адреси"],
                    size=14.5, pad=10, bold=True, fill=FILL, stroke=LINE, sw=1.6))

    p.append(fitbox(CX, 170, CW, 58, ["сторінка вже в кеші й позначена справною?"],
                    size=14.5, pad=10, bold=True, fill=FILL, stroke=LINE, sw=1.6))
    p.append(arrow(CX + CW / 2, 140, CX + CW / 2, 166, color=INK, sw=1.8))

    p.append(fitbox(910, 170, 250, 58, ["так — віддати байти", "без жодної перевірки"],
                    size=12.5, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(arrow(CX + CW + 12, 199, 900, 199, color=FIELD, sw=1.8))

    p.append(fitbox(CX, 262, CW, 58, ["прочитати блок 4 КіБ з носія"],
                    size=14.5, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(arrow(CX + CW / 2, 232, CX + CW / 2, 258, color=NEG, sw=1.8))
    p.append(text(CX + CW / 2 + 26, 251, "ні", size=13, color=NEG, bold=True, anchor="start"))

    p.append(fitbox(CX, 354, CW, 58, ["обчислити SHA-256 прочитаного блока"],
                    size=14.5, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(arrow(CX + CW / 2, 324, CX + CW / 2, 350, color=NEG, sw=1.8))

    p.append(fitbox(CX, 446, CW, 58, ["збігається з гешем у блоці дерева вище?"],
                    size=14.5, pad=10, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(arrow(CX + CW / 2, 416, CX + CW / 2, 442, color=NEG, sw=1.8))

    p.append(fitbox(60, 446, 240, 58, ["блок дерева перевіряють", "так само, аж до кореня"],
                    size=12, pad=10, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(310, 475, 300, 475, color=MUTED, sw=1.6))

    p.append(fitbox(60, 560, 480, 92,
                    ["ні: сторінка НЕ стає справною",
                     "read() → EIO · доступ через mmap → SIGBUS",
                     "наступна спроба почне все спочатку"],
                    size=13, pad=10, fill=RED_FILL, stroke=POS, sw=2.2))
    p.append(arrow(CX + 60, 510, 300, 556, color=POS, sw=2))

    p.append(fitbox(650, 560, 470, 92,
                    ["так: сторінку позначено справною",
                     "далі вона віддається з кешу без перевірок,",
                     "а після витіснення все повториться"],
                    size=13, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=2.2))
    p.append(arrow(CX + CW - 60, 510, 880, 556, color=FIELD, sw=2))

    render(os.path.join(IMG, 'read-gate.svg'), W, H, *p)


# ── 3. Три відповіді на одне питання, різні за одиницею захисту ─────────────
def fig_scope_compare():
    W, H = 1240, 640
    p = [text(W / 2, 42, "три способи зробити вміст незмінним і чим вони різняться",
              size=17, bold=True, color=INK)]

    cols = [(70, "dm-verity", NEG, BLUE_FILL),
            (470, "fs-verity", POS, RED_FILL),
            (870, "образ лише для читання", FIELD, GREEN_FILL)]
    CW = 300

    for x, ttl, col, fill in cols:
        p.append(fitbox(x, 78, CW, 50, [ttl], size=15.5, pad=10, bold=True,
                        fill=fill, stroke=col, sw=2.2))

    rows = [
        ("одиниця захисту",
         ["увесь блоковий пристрій", "окремий файл", "увесь образ файлової системи"]),
        ("носій під ним",
         ["лише для читання цілком", "звичайний, з записом", "лише для читання цілком"]),
        ("сусідні файли",
         ["теж заморожені", "живуть і змінюються", "теж заморожені"]),
        ("корінь довіри",
         ["у ланцюгу завантаження", "цифра файлу: список або підпис", "геш образу ззовні"]),
        ("коли перевіряється",
         ["на читанні блока", "на читанні блока", "на читанні блока"]),
        ("типове застосування",
         ["системний розділ пристрою", "застосунки на розділі даних", "контейнерний шар, прошивка"]),
    ]

    ry, rh, gap = 148, 66, 10
    for j, (label, vals) in enumerate(rows):
        y = ry + j * (rh + gap)
        p.append(text(60, y + rh / 2 + 5, label, size=13, anchor="end", color=MUTED))
        for (x, ttl, col, fill), v in zip(cols, vals):
            p.append(fitbox(x, y, CW, rh, [v], size=13, pad=10,
                            fill=FILL, stroke=col, sw=1.3))

    render(os.path.join(IMG, 'scope-compare.svg'), W, H, *p)


# ── 4. Ланцюг байтів від дескриптора до підпису ─────────────────────────────
def fig_signed_bytes():
    W, H = 900, 720
    CX = 430
    p = [text(CX, 40, "які саме байти проходять шлях до підпису",
              size=17, bold=True, color=INK)]

    boxes = [
        (120, ["struct fsverity_descriptor — 256 байтів",
               "version · hash_algorithm · log_blocksize · salt_size",
               "data_size · root_hash[64] · salt[32] · reserved[144]"],
         BLUE_FILL, NEG),
        (285, ["цифра файлу — 32 байти для SHA-256",
               "саме її віддає FS_IOC_MEASURE_VERITY"],
         GREEN_FILL, FIELD),
        (450, ["struct fsverity_formatted_digest — 44 байти",
               "«FSVerity» (8) + алгоритм (2) + довжина (2) + цифра (32)"],
         WARM_FILL, WARM),
        (615, ["підпис PKCS#7 у sig_ptr — не більше 16128 байтів",
               "ядро звіряє його з кільцем ключів .fs-verity"],
         GREY_FILL, LINE),
    ]

    for cy, lines, fill, stroke in boxes:
        body, w, h = textbox(CX, cy, lines, size=13.5, pad=14,
                             fill=fill, stroke=stroke, sw=1.6)
        p.append(body)

    arrows = [
        (120, 285, "SHA-256 над цими 256 байтами"),
        (285, 450, "обгортка з магією «FSVerity»"),
        (450, 615, "підписують саме ці 44 байти"),
    ]
    for y0, y1, lbl in arrows:
        p.append(arrow(CX, y0 + 52, CX, y1 - 46))
        p.append(text(CX + 22, (y0 + y1) / 2 + 5, lbl,
                      size=12.5, color=MUTED, anchor="start"))

    p.append(text(CX, 690, "fs.verity.require_signatures = 1 → файл без дійсного підпису не відкриється",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'signed-bytes.svg'), W, H, *p)


# ── 5. Байтова карта дескриптора на 256 байтів ──────────────────────────────
def fig_descriptor_map():
    W, H = 1360, 660
    p = [text(W / 2, 40, "struct fsverity_descriptor: 256 байтів, з яких і беруть цифру файлу",
              size=17, bold=True, color=INK)]

    cols = [(40, 96, "зсув"), (136, 92, "байтів"), (228, 236, "поле"),
            (464, 424, "що туди кладемо"), (888, 428, "на чому ловляться")]

    HY, RH = 76, 48
    for x, w, t in cols:
        p.append(rect(x, HY, w, 40, fill=GREY_FILL, stroke=LINE, sw=1.2, rx=4))
        p.append(text(x + w / 2, HY + 26, t, size=13, bold=True, color=INK))

    rows = [
        ("0x00", "1", "version", "одиниця", "версія формату, не версія ядра", BLUE_FILL, NEG),
        ("0x01", "1", "hash_algorithm", "1 = SHA-256, 2 = SHA-512", "номер, а не назва алгоритму", BLUE_FILL, NEG),
        ("0x02", "1", "log_blocksize", "12", "логарифм розміру, а не 4096", BLUE_FILL, NEG),
        ("0x03", "1", "salt_size", "довжина солі, 0..32", "солі СПРАВЖНЬОЇ, не доповненої", BLUE_FILL, NEG),
        ("0x04", "4", "__reserved_0x04", "нулі", "колись тут жив розмір підпису", GREY_FILL, LINE),
        ("0x08", "8", "data_size", "розмір файлу, little-endian", "htole64, а не htobe64", WARM_FILL, WARM),
        ("0x10", "64", "root_hash", "32 байти кореня дерева", "хвіст у 32 байти лишається нулями", GREEN_FILL, FIELD),
        ("0x50", "32", "salt", "сіль як є", "хвіст слота теж нулі", GREEN_FILL, FIELD),
        ("0x70", "144", "__reserved", "нулі", "сміття зі стека тут = інша цифра", GREY_FILL, LINE),
    ]

    y = HY + 44
    for off, n, fld, val, trap, fill, stroke in rows:
        cells = [off, n, fld, val, trap]
        for (x, w, _), s_ in zip(cols, cells):
            p.append(fitbox(x, y, w, RH, s_, size=12.5, pad=9,
                            fill=fill, stroke=stroke, sw=1.2, rx=4))
        y += RH + 4

    p.append(text(W / 2, y + 30,
                  "разом 0x100 = 256 байтів; 144 з них — самі нулі, і кожен із них входить у геш",
                  size=13, color=INK))
    p.append(text(W / 2, y + 58,
                  "цифра файлу = SHA-256 над усіма 256 байтами цієї структури",
                  size=13.5, bold=True, color=POS))

    render(os.path.join(IMG, 'descriptor-map.svg'), W, H, *p)


if __name__ == '__main__':
    fig_merkle_shape()
    fig_read_gate()
    fig_scope_compare()
    fig_signed_bytes()
    fig_descriptor_map()
    print("ok")
