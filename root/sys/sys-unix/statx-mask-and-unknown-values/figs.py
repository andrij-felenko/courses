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
GREY_FILL = "#eceef1"
WARM = "#b8860b"


def panel(x, y, w, h, title, color, fill):
    """Рамка-панель із заголовковим рядком угорі."""
    out = [rect(x, y, w, h, fill=fill, stroke=color, sw=2.0, rx=10)]
    out.append(text(x + w / 2, y + 27, title, size=15, bold=True, color=color))
    out.append(line(x, y + 40, x + w, y + 40, color=color, sw=1.2))
    return out


def rows(x, y, w, items, rh=30, size=13, color=INK):
    """Рядки «ліворуч назва — праворуч значення» без ліній крізь написи."""
    out = []
    for i, (left, right, rc) in enumerate(items):
        ry = y + rh * i
        out.append(text(x + 16, ry + 20, left, size=size, anchor="start", color=color))
        if right:
            out.append(text(x + w - 16, ry + 20, right, size=size,
                            anchor="end", bold=True, color=rc))
    return out


# ── 1. Дві форми відповіді ─────────────────────────────────────────────────
def fig_answer_forms():
    W, H = 1140, 760
    p = []

    # ЛІВА панель: stat
    lx, ly, lw, lh = 50, 60, 480, 400
    p += panel(lx, ly, lw, lh, "stat: одна форма на всіх", NEG, BLUE_FILL)
    p.append(text(lx + lw / 2, ly + 66, "питання завжди те саме: «дай усе»",
                  size=13, color=MUTED))
    inner_y = ly + 84
    p.append(rect(lx + 20, inner_y, lw - 40, 290, fill=BG, stroke=NEG, sw=1.2, rx=8))
    p += rows(lx + 20, inner_y + 8, lw - 40, [
        ("тип і права", "звичайний, rw-r--r--", INK),
        ("власник", "ann", INK),
        ("розмір", "8412", INK),
        ("зайнято блоків", "24", INK),
        ("кількість імен", "1", POS),
        ("час зміни", "2026-04-02 11:07", INK),
        ("час доступу", "2026-04-02 11:09", INK),
        ("час зміни inode", "2026-04-02 11:07", INK),
        ("час створення", "поля немає", POS),
    ], rh=31)

    p.append(fitbox(lx + 10, ly + lh + 26, lw - 20, 122,
                    ["Btrfs імен у каталогах не рахує й завжди пише 1.",
                     "«Одне ім'я» і «не рахую» — те саме число,",
                     "і жоден біт у відповіді їх не розрізняє."],
                    size=14, fill=RED_FILL, stroke=POS, sw=2))

    # ПРАВА панель: statx
    rx0, ry0, rw, rh = 610, 60, 480, 400
    p += panel(rx0, ry0, rw, rh, "statx: маска туди й маска назад", FIELD, GREEN_FILL)

    p.append(fitbox(rx0 + 20, ry0 + 54, rw - 40, 58,
                    ["маска запиту: розмір · час зміни · час створення"],
                    size=13, fill=BG, stroke=FIELD, sw=1.4))
    p.append(arrow(rx0 + rw / 2, ry0 + 118, rx0 + rw / 2, ry0 + 146, color=FIELD, sw=2))
    p.append(fitbox(rx0 + 20, ry0 + 150, rw - 40, 46,
                    ["ядро питає драйвер файлової системи"],
                    size=13, fill=BG, stroke=FIELD, sw=1.4))
    p.append(arrow(rx0 + rw / 2, ry0 + 200, rx0 + rw / 2, ry0 + 228, color=FIELD, sw=2))

    ans_y = ry0 + 232
    p.append(rect(rx0 + 20, ans_y, rw - 40, 152, fill=BG, stroke=FIELD, sw=1.2, rx=8))
    p.append(text(rx0 + rw / 2, ans_y + 24, "stx_mask — що ядро справді заповнило",
                  size=13, bold=True, color=FIELD))
    p += rows(rx0 + 20, ans_y + 34, rw - 40, [
        ("розмір", "8412  ✓ біт стоїть", FIELD),
        ("час зміни", "2026-04-02  ✓ біт стоїть", FIELD),
        ("час створення", "біта немає", POS),
    ], rh=32)

    p.append(fitbox(rx0 + 10, ry0 + rh + 26, rw - 20, 122,
                    ["Скинутий біт — це відповідь, а не збій:",
                     "«ця файлова система такого не знає».",
                     "Поле без свого біта просто не читають."],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2))

    render(os.path.join(IMG, 'answer-forms.svg'), W, H, *p)


# ── 2. Два яруси масок для атрибутів ───────────────────────────────────────
def fig_attributes_two_masks():
    W, H = 1060, 600
    p = []

    p.append(text(W / 2, 46, "біт у stx_attributes_mask — «чи вміє ця ФС таке взагалі»",
                  size=15, bold=True))

    col1_x, col1_w = 380, 320
    col2_x, col2_w = 730, 280
    head_y = 82
    p.append(fitbox(col1_x, head_y, col1_w, 52, ["1 — уміє й відповідає"],
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(col2_x, head_y, col2_w, 52, ["0 — не має поняття"],
                    size=14, bold=True, fill=GREY_FILL, stroke=MUTED, sw=1.8))

    row1_y, row2_y, row_h = 168, 300, 116
    p.append(fitbox(60, row1_y, 290, row_h,
                    ["біт у stx_attributes", "дорівнює 1"],
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(60, row2_y, 290, row_h,
                    ["біт у stx_attributes", "дорівнює 0"],
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(fitbox(col1_x, row1_y, col1_w, row_h,
                    ["ТАК", "властивість увімкнена"],
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(fitbox(col1_x, row2_y, col1_w, row_h,
                    ["НІ", "властивість вимкнена"],
                    size=15, bold=True, fill=BG, stroke=NEG, sw=2, color=NEG))

    p.append(fitbox(col2_x, row1_y, col2_w, row_h + row_h + 16,
                    ["НЕ ЗНАЮ", "нуль тут нічого",
                     "не означає —", "поле читати не можна"],
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED, sw=2, color=MUTED))

    p.append(fitbox(60, 472, 940, 96,
                    ["Btrfs уміє стискати вміст — і про стиснення відповідає обома бітами.",
                     "FAT такого поняття не має: там нуль у stx_attributes — це мовчання,",
                     "а не заперечення, і саме це розрізняє другий ярус масок."],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'attributes-two-masks.svg'), W, H, *p)


# ── 3. Відповідь, яка росте, не рухаючи старого ────────────────────────────
def fig_growing_reply():
    W, H = 1180, 820
    p = []

    p.append(text(W / 2, 46, "struct statx — 256 байтів від першого дня", size=16, bold=True))

    mx, mw = 60, 520
    my, seg_h = 84, 46
    segs = [
        ("0x00", "stx_mask, stx_blksize", "4.11", BLUE_FILL, NEG),
        ("0x08", "stx_attributes", "4.11", BLUE_FILL, NEG),
        ("0x10", "nlink, uid, gid, mode", "4.11", BLUE_FILL, NEG),
        ("0x20", "ino, size, blocks, attributes_mask", "4.11", BLUE_FILL, NEG),
        ("0x40", "atime, btime, ctime, mtime", "4.11", BLUE_FILL, NEG),
        ("0x80", "rdev_major/minor, dev_major/minor", "4.11", BLUE_FILL, NEG),
        ("0x90", "mnt_id · вирівнювання прямого вводу", "5.8 · 6.1", WARM_FILL, WARM),
        ("0xa0", "subvol · атомарний запис", "6.10 · 6.11", WARM_FILL, WARM),
        ("0xb0", "вирівнювання прямого читання", "6.14", WARM_FILL, WARM),
        ("0xc0", "незайманий запас до кінця структури", "—", GREEN_FILL, FIELD),
    ]
    for i, (off, what, ver, fill, col) in enumerate(segs):
        sy = my + seg_h * i
        p.append(rect(mx, sy, mw, seg_h - 4, fill=fill, stroke=col, sw=1.4, rx=6))
        p.append(text(mx + 14, sy + 27, off, size=12, anchor="start", bold=True, color=col))
        p.append(text(mx + 74, sy + 27, what, size=13, anchor="start"))
        p.append(text(mx + mw - 14, sy + 27, ver, size=12, anchor="end", color=col))
    p.append(text(mx, my + seg_h * len(segs) + 22, "0x100 — кінець, і він не рухається",
                  size=13, anchor="start", bold=True, color=FIELD))

    bx, bw = 650, 470
    p.append(fitbox(bx, 100, bw, 158,
                    ["ПРОГРАМА, ЗІБРАНА 2017 РОКУ",
                     "її заголовок знає поля до 0x90;",
                     "бітів, яких не знає, вона не просить,",
                     "а ядро однаково пише всі 256 байтів —",
                     "буфер саме такий із самого початку"],
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=2))

    p.append(fitbox(bx, 292, bw, 158,
                    ["ПРОГРАМА, ЗІБРАНА 2026 РОКУ",
                     "просить STATX_SUBVOL і перевіряє біт;",
                     "на ядрі 5.4 біт не прийде —",
                     "це не помилка, а чесна відповідь",
                     "«тут такого поняття немає»"],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2))

    p.append(fitbox(bx, 484, bw, 128,
                    ["Нове поле лягає в запас",
                     "і дістає власний біт маски.",
                     "Зміщення старих полів і розмір",
                     "структури не міняються ніколи."],
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM, sw=2))

    p.append(fitbox(60, 646, 1060, 116,
                    ["Ось чому нову можливість тут не треба «вмикати версією»:",
                     "прохання — це набір бітів, відповідь — теж набір бітів,",
                     "і кожна зі сторін просто ігнорує ті, яких не знає."],
                    size=14, fill=BG, stroke=INK, sw=1.8))

    render(os.path.join(IMG, 'growing-reply.svg'), W, H, *p)


# ── 4. Сім років: віхи й заперечення, що змінили конструкцію ───────────────
def fig_seven_years():
    W, H = 1180, 850
    p = []

    p.append(text(W / 2, 44, "Від xstat() до statx(): віхи й правки за заперечення",
                  size=16, bold=True))

    # Стрічка часу
    p.append(line(60, 104, 1114, 104, color=MUTED, sw=2))
    stones = [
        (["30.06.2010", "xstat()/fxstat():", "буфер із довжиною,",
          "номер версії", "всередині структури"], BLUE_FILL, NEG),
        (["15.07.2010", "друга редакція;", "далі обговорення",
          "поволі згасає"], BLUE_FILL, NEG),
        (["квітень 2016", "LSFMM: лишити те,", "що має чітке значення;",
          "29.04 — RFC уже", "під назвою statx()"], WARM_FILL, WARM),
        (["30.11.2016", "третя редакція:", "суперечка про",
          "фемтосекунди", "й вимога тестів"], WARM_FILL, WARM),
        (["03.03.2017", "Ал Віро бере", "патч у дерево;",
          "Linux 4.11 —", "30.04.2017"], GREEN_FILL, FIELD),
    ]
    for i, (lines_, fill, col) in enumerate(stones):
        bx = 60 + i * 216
        p.append(line(bx + 95, 104, bx + 95, 126, color=col, sw=2))
        p.append(fitbox(bx, 128, 190, 168, lines_, size=13, fill=fill, stroke=col, sw=1.8))

    p.append(text(W / 2, 344, "заперечення рецензентів  →  що через нього змінилося",
                  size=15, bold=True, color=INK))

    pairs = [
        (["«Номер версії структури —", "це роки життя з кількома",
          "розкладками; дешевше додати", "ще один виклик, ніж їх тягнути»"],
         ["Версії немає взагалі.", "Нова можливість — це новий біт",
          "маски; сторона, яка його не знає,", "просто його не бачить"]),
        (["«Одна структура і як вхід,", "і як вихід — прохання",
          "та відповідь злиплися", "в одному буфері»"],
         ["Прохання винесено окремим", "аргументом виклику;",
          "у буфер ядро тільки пише,", "і пише завжди всі 256 байтів"]),
        (["«Повертати все, що комусь", "колись здасться корисним» —",
          "поля без чіткого значення", "й без жодного споживача"],
         ["Лишили те, що визначено", "однозначно й комусь потрібне;",
          "решта — у резерв структури,", "куди її дописали пізніше"]),
    ]
    for i, (left_, right_) in enumerate(pairs):
        ry = 372 + i * 154
        p.append(fitbox(60, ry, 450, 134, left_, size=13,
                        fill=RED_FILL, stroke=POS, sw=1.8))
        p.append(arrow(524, ry + 67, 592, ry + 67, color=INK, sw=2.2))
        p.append(fitbox(606, ry, 508, 134, right_, size=13,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'seven-years.svg'), W, H, *p)


# ── 5. Чотири клітинки одного біта (огляд можливостей) ─────────────────────
def fig_mask_bit_cells():
    W, H = 1160, 700
    p = []
    p.append(text(W / 2, 40, "Один біт: що означає кожне поєднання прохання й відповіді",
                  size=18, bold=True))

    gx, gy = 360, 108          # лівий верхній кут сітки клітинок
    cw, ch, gap = 360, 176, 26

    p.append(text(gx + cw / 2, gy - 20, "біт у stx_mask стоїть",
                  size=15, bold=True, color=FIELD))
    p.append(text(gx + cw + gap + cw / 2, gy - 20, "біт у stx_mask скинуто",
                  size=15, bold=True, color=POS))

    rowlab = [
        ["біт стояв", "у масці запиту"],
        ["біта в масці", "запиту не було"],
    ]
    cells = [
        [(["ПОЛЕ Є", "значення читати можна"], GREEN_FILL, FIELD),
         (["ЦЯ ФС ТАКОГО НЕ ЗНАЄ", "у полі нуль, і він",
           "нічого не означає"], RED_FILL, POS)],
        [(["ДІСТАЛОСЯ ЗАДАРМА", "драйвер однаково прочитав",
           "inode й позначив біт"], BLUE_FILL, NEG),
         (["ТИША", "ні прохання, ні відповіді"], GREY_FILL, MUTED)],
    ]
    for r in range(2):
        ry = gy + r * (ch + gap)
        p.append(mtext(gx - 34, ry + ch / 2 - 8, rowlab[r], size=14,
                       anchor="end", bold=True, color=INK))
        for c in range(2):
            lines, fill_, col = cells[r][c]
            cxx = gx + c * (cw + gap)
            p.append(rect(cxx, ry, cw, ch, fill=fill_, stroke=col, sw=2.0, rx=10))
            p.append(text(cxx + cw / 2, ry + 44, lines[0], size=16, bold=True, color=col))
            p.append(mtext(cxx + cw / 2, ry + 82, lines[1:], size=13.5, color=INK))

    tail_y = gy + 2 * (ch + gap) + 22
    p.append(fitbox(gx - 300, tail_y, cw * 2 + gap + 300, 96,
                    ["П'ятий випадок: у stx_mask стоїть біт, якого наш заголовок не називає.",
                     "Ядро новіше за програму — і саме цей залишок каже, наскільки."],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'mask-bit-cells.svg'), W, H, *p)


# ── 6. Три питання про одне число ──────────────────────────────────────────
def fig_three_questions():
    W, H = 1320, 600
    p = []
    p.append(text(W / 2, 40, "Три різні питання про одне й те саме число",
                  size=18, bold=True))

    bands = [
        ("Чи є це поле взагалі?",
         "відповідає stx_mask",
         ["ext4 на томі зі 128-байтовим inode не має де тримати час",
          "створення — і чесно не виставляє біт btime"],
         GREEN_FILL, FIELD),
        ("Чи значення щось означає?",
         "не відповідає ніщо",
         ["FAT віддає власника з опції монтування uid=, а Btrfs пише",
          "будь-якому каталогу лічильник імен 1 — біти при цьому стоять"],
         RED_FILL, POS),
        ("Чи воно свіже?",
         "відповідає прапорець синхронізації",
         ["на мережевій ФС розмір беруть із кеша (DONT_SYNC) або",
          "звіряють із сервером (FORCE_SYNC) — це вибір програми"],
         BLUE_FILL, NEG),
    ]
    y = 96
    for q, who, why, fill_, col in bands:
        p.append(rect(60, y, 340, 132, fill=BG, stroke=col, sw=2.0, rx=10))
        p.append(fitbox(68, y + 8, 324, 116, q, size=16, bold=True, color=col,
                        fill=BG, stroke=BG, sw=0))
        p.append(arrow(414, y + 66, 470, y + 66, color=INK, sw=2.2))
        p.append(fitbox(484, y, 300, 132, who, size=15, bold=True,
                        fill=fill_, stroke=col, sw=2.0))
        p.append(fitbox(806, y, 454, 132, why, size=13, fill=BG, stroke=MUTED, sw=1.4))
        y += 158

    render(os.path.join(IMG, 'three-questions.svg'), W, H, *p)


if __name__ == '__main__':
    fig_answer_forms()
    fig_attributes_two_masks()
    fig_growing_reply()
    fig_seven_years()
    fig_mask_bit_cells()
    fig_three_questions()
    print("ok")
