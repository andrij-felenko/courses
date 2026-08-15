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


# ── 1. Звідки береться стеля 2 ГіБ ──────────────────────────────────────────
def fig_offset_ceiling():
    W, H = 1120, 520
    p = []
    p.append(text(W / 2, 42, "32-бітний off_t зі знаком: половина діапазону витрачена",
                  size=17, bold=True, color=INK))

    # ── смуга діапазону типу
    bx, bw, by, bh = 80, 960, 110, 76
    mid = bx + bw / 2
    p.append(rect(bx, by, bw / 2, bh, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=6))
    p.append(rect(mid, by, bw / 2, bh, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))

    p.append(text(bx + bw / 4, by + bh / 2 + 6, "від'ємні — зсувами не бувають",
                  size=14, color=NEG, bold=True))
    p.append(text(mid + bw / 4, by + bh / 2 + 6, "законні зсуви у файлі",
                  size=14, color=FIELD, bold=True))

    p.append(text(bx, by + bh + 26, "−2³¹", size=13, color=MUTED, anchor="start"))
    p.append(text(mid, by + bh + 26, "0", size=13, color=MUTED))
    p.append(text(bx + bw, by + bh + 26, "2³¹ − 1 = 2147483647", size=13,
                  color=MUTED, anchor="end"))

    # ── зарезервоване −1
    tick = mid - 14
    p.append(rect(tick - 6, by, 12, bh, fill=RED_FILL, stroke=POS, sw=2, rx=3))
    b, _, _ = textbox(tick - 190, by - 62, "єдине потрібне від'ємне: (off_t)−1 — «lseek не вдався»",
                      size=13, fill=RED_FILL, stroke=POS, color=POS)
    p.append(b)
    p.append(line(tick - 190, by - 46, tick - 4, by - 10, color=POS, sw=1.4, dash="4,3"))

    # ── смуга реального файлу
    fx, fw, fy, fh = 80, 960, 300, 76
    cut = fx + fw * (2.0 / 4.4)
    p.append(rect(fx, fy, cut - fx, fh, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=6))
    p.append(rect(cut, fy, fx + fw - cut, fh, fill=RED_FILL, stroke=POS, sw=1.8, rx=6))

    p.append(text(fx, fy - 20, "той самий файл на 4.4 ГіБ", size=14,
                  color=INK, bold=True, anchor="start"))
    p.append(text(fx + (cut - fx) / 2, fy + fh / 2 + 6, "досяжна частина",
                  size=14, color=FIELD, bold=True))
    p.append(text(cut + (fx + fw - cut) / 2, fy + fh / 2 + 6,
                  "назвати нічим: числа не існує", size=14, color=POS, bold=True))

    p.append(line(cut, fy - 8, cut, fy + fh + 8, color=POS, sw=2, dash="5,4"))
    p.append(text(cut, fy + fh + 30, "2 ГіБ", size=13, color=POS, bold=True))
    p.append(text(fx + fw, fy + fh + 30, "4.4 ГіБ", size=13, color=MUTED, anchor="end"))

    p.append(text(W / 2, 458,
                  "межа належить типу в програмі, а не диску: сам файл цілий і читається іншими",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'offset-ceiling.svg'), W, H, *p)


# ── 2. Один текст — дві двійкові угоди ──────────────────────────────────────
def fig_two_compilations():
    W, H = 1180, 640
    p = []
    p.append(text(W / 2, 40, "один вихідний файл — дві різні двійкові угоди",
                  size=17, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 92, "checksum.c — текст програми незмінний",
                      size=14, fill=WARM_FILL, stroke=WARM, bold=True)
    p.append(b)

    lcx, rcx = 300, 880
    p.append(arrow(W / 2 - 30, 116, lcx, 168, color=MUTED))
    p.append(arrow(W / 2 + 30, 116, rcx, 168, color=MUTED))

    cols = [
        (lcx, NEG, BLUE_FILL, "cc -m32",
         ["off_t — 4 байти", "lseek(…) → символ lseek",
          "struct stat — вузька", "стеля типу — 2 ГіБ"]),
        (rcx, FIELD, GREEN_FILL, "cc -m32 -D_FILE_OFFSET_BITS=64",
         ["off_t — 8 байтів", "lseek(…) → символ lseek64",
          "struct stat — широка", "стеля типу — 8 ЕіБ"]),
    ]
    for cx, col, fill, head, rows in cols:
        b, _, _ = textbox(cx, 190, head, size=14, fill=fill, stroke=col,
                          color=col, bold=True, min_w=460)
        p.append(b)
        y = 258
        for r in rows:
            p.append(fitbox(cx - 230, y, 460, 54, r, size=14, fill=FILL, stroke=col, sw=1.4))
            y += 70

    p.append(arrow(lcx, 544, W / 2 - 40, 578, color=MUTED))
    p.append(arrow(rcx, 544, W / 2 + 40, 578, color=MUTED))
    b, _, _ = textbox(W / 2, 596, "обидва двійкові файли працюють на одній машині з однією libc",
                      size=14, fill=GREY_FILL, stroke=MUTED, color=INK)
    p.append(b)

    render(os.path.join(IMG, 'two-compilations.svg'), W, H, *p)


# ── 3. Три межі, на яких ширина зсуву може відрізнятися ─────────────────────
def fig_width_layers():
    W, H = 1120, 620
    p = []
    p.append(text(W / 2, 40, "де ширина зсуву ще плаває, а де вже ні",
                  size=17, bold=True, color=INK))

    lx, lw = 70, 660
    right = lx + lw + 40
    bands = [
        (86,  "код програми", "власні змінні, структури й функції з off_t",
         WARM_FILL, WARM, "залежить від макроса"),
        (232, "libc", "заголовки перевизначають типи й перенаправляють імена",
         BLUE_FILL, NEG, "залежить від макроса"),
        (378, "ядро", "зсув у файлі — loff_t, завжди 64 біти зі знаком",
         GREEN_FILL, FIELD, "стала: 64 біти"),
        (500, "файлова система й носій", "розмір записано широким полем в inode",
         GREEN_FILL, FIELD, "стала: 64 біти"),
    ]
    for y, head, sub, fill, col, width_note in bands:
        p.append(rect(lx, y, lw, 90, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(lx + 20, y + 34, head, size=15, color=col, bold=True, anchor="start"))
        p.append(text(lx + 20, y + 64, sub, size=13, color=INK, anchor="start"))
        p.append(text(right, y + 50, width_note, size=13, color=MUTED, anchor="start"))

    edges = [
        (200, "заголовки libc — тут вирішує _FILE_OFFSET_BITS"),
        (346, "межа системного виклику — lseek або _llseek, stat або stat64"),
    ]
    for y, label in edges:
        p.append(line(lx - 16, y, right + 250, y, color=POS, sw=2, dash="6,4"))
        p.append(text(lx - 16, y - 12, label, size=13, color=POS, bold=True, anchor="start"))

    p.append(text(W / 2, 596,
                  "великі файли існували завжди — бракувало лише способу назвати зсув у них",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'width-layers.svg'), W, H, *p)


# ── 4. Розбіжність між одиницями трансляції ─────────────────────────────────
def fig_mixed_translation_units():
    W, H = 1180, 640
    p = []
    p.append(text(W / 2, 40, "власна функція: імена збігаються, ширини — ні",
                  size=17, bold=True, color=INK))

    p.append(fitbox(70, 78, 440, 92,
                    "a.o — зібрано з _FILE_OFFSET_BITS=64\nвикликає file_tail_offset(fd, back)",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(670, 78, 440, 92,
                    "b.o — зібрано без макроса\nвизначає file_tail_offset(fd, back)",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    b, _, _ = textbox(W / 2, 216, "компонувальник: імена символів однакові — з’єднано мовчки",
                      size=14, fill=GREY_FILL, stroke=MUTED, color=INK, bold=True)
    p.append(b)
    p.append(arrow(290, 176, W / 2 - 60, 194, color=MUTED))
    p.append(arrow(890, 176, W / 2 + 60, 194, color=MUTED))

    # ── слоти аргументів
    sx = 240
    cells = [(120, "fd"), (330, "back — молодші 32"), (330, "back — старші 32")]

    y1 = 306
    p.append(text(sx, y1 - 14, "що кладе той, хто викликає (off_t на 8 байтів)",
                  size=13, color=FIELD, bold=True, anchor="start"))
    x = sx
    for w, label in cells:
        p.append(fitbox(x, y1, w, 58, label, size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
        x += w + 10

    y2 = 424
    p.append(text(sx, y2 - 14, "що читає той, кого викликають (off_t на 4 байти)",
                  size=13, color=NEG, bold=True, anchor="start"))
    x = sx
    p.append(fitbox(x, y2, cells[0][0], 58, "fd", size=13, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    x += cells[0][0] + 10
    p.append(fitbox(x, y2, cells[1][0], 58, "back — усе число", size=13,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6))
    x += cells[1][0] + 10
    p.append(fitbox(x, y2, cells[2][0], 58, "цей слот ніхто не читає", size=13,
                    fill=RED_FILL, stroke=POS, sw=1.6))

    p.append(text(W / 2, 556,
                  "плюс повернення: одна сторона віддає 32 біти там, де друга чекає 64",
                  size=14, color=POS, bold=True))
    p.append(text(W / 2, 590,
                  "ані попередження компілятора, ані помилки компонування — лише інші числа",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'mixed-translation-units.svg'), W, H, *p)


# ── 5. Байтова карта однієї структури у двох розкладках (вставка proj) ─────
def fig_struct_byte_map():
    W, H = 1220, 600
    BX, CELL = 216, 57.0
    p = []

    def span_box(y, c0, c1, label, fill, stroke, h=54, size=12.5):
        return fitbox(BX + c0 * CELL, y, (c1 - c0) * CELL, h, label,
                      size=size, fill=fill, stroke=stroke, sw=1.6)

    def ruler(y):
        out = []
        for i in range(16):
            out.append(text(BX + (i + 0.5) * CELL, y, str(i), size=11, color=MUTED))
        return out

    def side(y, l1, l2, color):
        return mtext(BX - 18, y, [l1, l2], size=12.5, color=color,
                     anchor="end", bold=True)

    # ══ верх: вузька сторона пише, широка читає ═════════════════════════════
    p.append(text(W / 2, 62, "struct span { off_t start; long records; int truncated; }",
                  size=14, color=MUTED))

    p.extend(ruler(96))

    yA = 108
    p.append(span_box(yA, 0, 4, "start = 4096", BLUE_FILL, NEG))
    p.append(span_box(yA, 4, 8, "records = 7", BLUE_FILL, NEG))
    p.append(span_box(yA, 8, 12, "truncated = 1", BLUE_FILL, NEG))
    p.append(span_box(yA, 12, 16, "ніхто не писав", GREY_FILL, MUTED))
    p.append(side(yA + 20, "вузька сторона", "пише 12 байтів", NEG))

    yB = 200
    p.append(span_box(yB, 0, 8, "start — усі вісім байтів", GREEN_FILL, FIELD))
    p.append(span_box(yB, 8, 12, "records", GREEN_FILL, FIELD))
    p.append(span_box(yB, 12, 16, "truncated", GREEN_FILL, FIELD))
    p.append(side(yB + 20, "широка сторона", "читає 16 байтів", FIELD))

    b, _, _ = textbox(W / 2, 300,
                      ["start = 7·2³² + 4096 = 30064775168      records = 1      truncated = 0"],
                      size=13.5, fill=RED_FILL, stroke=POS, color=POS, bold=True)
    p.append(b)

    p.append(line(60, 344, W - 60, 344, color=MUTED, sw=1, dash="6,5"))

    # ══ низ: широка сторона пише в об'єкт вузької ═══════════════════════════
    p.append(text(W / 2, 376, "зворотна збірка: широка сторона пише більше, ніж об'єкт має",
                  size=14, color=INK, bold=True))

    p.extend(ruler(406))

    yC = 418
    p.append(span_box(yC, 0, 8, "start = 4096", GREEN_FILL, FIELD))
    p.append(span_box(yC, 8, 12, "records = 7", GREEN_FILL, FIELD))
    p.append(span_box(yC, 12, 16, "truncated = 1", RED_FILL, POS))
    p.append(side(yC + 20, "широка сторона", "пише 16 байтів", FIELD))

    yD = 502
    p.append(span_box(yD, 0, 4, "start = 4096 ✓", BLUE_FILL, NEG))
    p.append(span_box(yD, 4, 8, "records = 0", BLUE_FILL, NEG))
    p.append(span_box(yD, 8, 12, "truncated = 7", BLUE_FILL, NEG))
    p.append(side(yD + 20, "вузька сторона", "має 12 байтів", NEG))

    # межа об'єкта — рівно на стику клітинок, тексту не перетинає
    edge = BX + 12 * CELL
    p.append(line(edge, yC - 12, edge, yD + 66, color=POS, sw=2.4))
    p.append(text(edge + 8, yD + 84, "тут об'єкт закінчився — далі чужа пам'ять",
                  size=12.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, 'struct-byte-map.svg'), W, H, *p,
           title="Один об'єкт у пам'яті, дві розкладки")


if __name__ == '__main__':
    fig_offset_ceiling()
    fig_two_compilations()
    fig_width_layers()
    fig_mixed_translation_units()
    fig_struct_byte_map()
    print("ok")
