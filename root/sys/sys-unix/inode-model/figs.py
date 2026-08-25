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
WARM = "#b8860b"


# ── 1. Імена окремо, об'єкт окремо ──────────────────────────────────────────
def fig_name_to_inode():
    W, H = 1020, 640
    p = []

    # каталоги
    def dirbox(x, y, w, title, rows):
        out = []
        rh = 30
        h = 34 + rh * len(rows)
        out.append(rect(x, y, w, h, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
        out.append(text(x + w / 2, y + 23, title, size=14, bold=True, color=NEG))
        out.append(line(x, y + 34, x + w, y + 34, color=NEG, sw=1.2))
        for i, (nm, num) in enumerate(rows):
            ry = y + 34 + rh * i
            if i:
                out.append(line(x, ry, x + w, ry, color=NEG, sw=0.7, dash="3,3"))
            out.append(text(x + 16, ry + 20, nm, size=13, anchor="start"))
            out.append(text(x + w - 16, ry + 20, num, size=13, anchor="end", bold=True, color=POS))
        return out, h

    lx, ly, lw = 40, 60, 320
    lb, lh = dirbox(lx, ly, lw, "каталог /home/ann", [("report.txt", "4211"), ("notes.md", "5107")])
    p += lb

    rx0, ry0, rw = 660, 60, 320
    rb, rh0 = dirbox(rx0, ry0, rw, "каталог /srv/backup", [("r-2024.txt", "4211")])
    p += rb

    # inode
    ix, iy, iw, ih = 340, 250, 340, 200
    p.append(rect(ix, iy, iw, ih, fill=WARM_FILL, stroke=WARM, sw=2.2, rx=10))
    p.append(text(ix + iw / 2, iy + 26, "inode 4211", size=16, bold=True, color=WARM))
    p.append(line(ix, iy + 38, ix + iw, iy + 38, color=WARM, sw=1.2))
    fields = ["тип: звичайний файл",
              "права: rw-r--r--   власник: ann",
              "лічильник імен: 2",
              "розмір: 8412 байтів",
              "часи: доступу, зміни, метаданих",
              "карта блоків"]
    for i, f in enumerate(fields):
        p.append(text(ix + 18, iy + 62 + i * 24, f, size=13, anchor="start"))

    # стрілки від каталогів до inode
    p.append(arrow(lx + lw / 2, ly + lh, ix + 60, iy, color=NEG, sw=1.8))
    p.append(arrow(rx0 + rw / 2, ry0 + rh0, ix + iw - 60, iy, color=NEG, sw=1.8))

    # примітка про відсутність імені
    p.append(fitbox(40, 300, 250, 76,
                    ["у самому inode", "немає ані імені,", "ані шляху"],
                    size=14, bold=True, fill=RED_FILL, stroke=POS, sw=2, color=POS))
    p.append(line(290, 338, ix, 338, color=POS, sw=1.4, dash="5,4"))

    # блоки даних
    by, bw2, bh2 = 540, 96, 48
    starts = [250, 366, 482, 598, 714]
    p.append(mtext(140, 556, ["блоки даних", "на носії"], size=13, color=MUTED))
    for i, bx in enumerate(starts):
        p.append(rect(bx, by, bw2, bh2, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=6))
        p.append(text(bx + bw2 / 2, by + 30, str(1204 + i * 3), size=13, color=INK))
    for bx in starts:
        p.append(line(ix + iw / 2, iy + ih, bx + bw2 / 2, by, color=FIELD, sw=1.3))

    render(os.path.join(IMG, 'name-to-inode.svg'), W, H, *p)


# ── 2. Як фіксований inode описує файл будь-якого розміру ───────────────────
def fig_block_map():
    W, H = 1060, 600
    p = []

    # ЛІВОРУЧ: класична карта
    p.append(text(255, 44, "класична карта блоків", size=15, bold=True, color=NEG))
    rows = [("12 прямих", "12 × 4 КіБ = 48 КіБ", "1 звертання"),
            ("1× непрямий", "1024 × 4 КіБ = 4 МіБ", "2 звертання"),
            ("2× непрямий", "1024² × 4 КіБ = 4 ГіБ", "3 звертання"),
            ("3× непрямий", "1024³ × 4 КіБ = 4 ТіБ", "4 звертання")]
    cy, ch = 90, 80
    slot_x, slot_w = 40, 150
    cap_x, cap_w = 210, 190
    cost_x = 420
    for i, (nm, cap, cost) in enumerate(rows):
        y = cy + i * (ch + 22)
        p.append(fitbox(slot_x, y, slot_w, ch, [nm], size=14, bold=True,
                        fill=BLUE_FILL, stroke=NEG, sw=1.7))
        p.append(fitbox(cap_x, y, cap_w, ch, ["охоплює", cap], size=13,
                        fill=FILL, stroke=LINE, sw=1.4))
        p.append(arrow(slot_x + slot_w, y + ch / 2, cap_x, y + ch / 2, sw=1.5))
        p.append(text(cost_x, y + ch / 2 + 5, cost, size=12.5, color=MUTED, anchor="start"))
    p.append(text(255, 545, "що глибше рівень, то більше читань", size=13, color=MUTED))
    p.append(text(255, 568, "заради одного байта", size=13, color=MUTED))

    # роздільник
    p.append(line(530, 70, 530, 580, color=MUTED, sw=1.2, dash="6,5"))

    # ПРАВОРУЧ: екстенти
    p.append(text(800, 44, "карта екстентів", size=15, bold=True, color=FIELD))
    ex, ew = 600, 180
    recs = [("початок 1204", "довжина 8192"),
            ("початок 65536", "довжина 4096"),
            ("початок 90112", "довжина 2048")]
    strip_x, strip_w = 830, 190
    for i, (a, b) in enumerate(recs):
        y = 100 + i * 110
        p.append(fitbox(ex, y, ew, 72, [a, b], size=13,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.7))
        p.append(rect(strip_x, y + 14, strip_w, 44, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=4))
        p.append(text(strip_x + strip_w / 2, y + 42, "суцільний ряд блоків", size=12))
        p.append(arrow(ex + ew, y + 36, strip_x, y + 36, color=FIELD, sw=1.5))

    p.append(text(800, 470, "один запис описує тисячі блоків,", size=13, color=MUTED))
    p.append(text(800, 493, "тож проміжні рівні зникають", size=13, color=MUTED))
    p.append(text(800, 545, "ціна: потрібна суцільність на носії", size=13, color=POS))

    render(os.path.join(IMG, 'block-map.svg'), W, H, *p)


# ── 3. Два лічильники: коли вміст справді помирає ───────────────────────────
def fig_two_counters():
    W, H = 940, 560
    p = []

    col_x = [300, 630]
    col_w = 300
    row_y = [150, 340]
    row_h = 160

    p.append(text(col_x[0] + col_w / 2, 76, "лічильник імен > 0", size=14.5, bold=True, color=NEG))
    p.append(text(col_x[0] + col_w / 2, 100, "(є хоча б один запис у каталозі)", size=12, color=MUTED))
    p.append(text(col_x[1] + col_w / 2, 76, "лічильник імен = 0", size=14.5, bold=True, color=POS))
    p.append(text(col_x[1] + col_w / 2, 100, "(останнє ім'я знято)", size=12, color=MUTED))

    p.append(mtext(150, row_y[0] + row_h / 2 - 10,
                   ["є відкриті", "дескриптори"], size=14, bold=True, color=NEG))
    p.append(mtext(150, row_y[1] + row_h / 2 - 10,
                   ["відкритих", "дескрипторів немає"], size=14, bold=True, color=POS))

    cells = [
        (0, 0, ["звичайний відкритий файл:", "видно в каталозі,", "хтось читає просто зараз"], GREEN_FILL, FIELD),
        (1, 0, ["вміст живий, але безіменний:", "місце зайняте, і df його", "не поверне до закриття"], WARM_FILL, WARM),
        (0, 1, ["файл просто лежить:", "має ім'я, ніхто не тримає", "його відкритим"], GREEN_FILL, FIELD),
        (1, 1, ["ніщо не тримає:", "inode і блоки", "звільнено"], RED_FILL, POS),
    ]
    for ci, ri, lines, fill, stroke in cells:
        p.append(fitbox(col_x[ci], row_y[ri], col_w, row_h, lines, size=13.5,
                        fill=fill, stroke=stroke, sw=1.9))

    p.append(text(W / 2, 528, "вміст зникає лише в правому нижньому куті — коли обидва лічильники нульові",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'two-counters.svg'), W, H, *p)


# ── 4. Номер як індекс у масиві ─────────────────────────────────────────────
def fig_inode_table():
    W, H = 1000, 420
    p = []

    y0, h0 = 200, 90
    segs = [("суперблок", 40, 130, FILL, LINE),
            ("бітові карти", 180, 150, FILL, LINE),
            ("таблиця inode", 340, 330, WARM_FILL, WARM),
            ("блоки даних", 690, 270, GREEN_FILL, FIELD)]
    for nm, x, w, fill, stroke in segs:
        p.append(rect(x, y0, w, h0, fill=fill, stroke=stroke, sw=1.8, rx=6))
        p.append(text(x + w / 2, y0 + h0 + 26, nm, size=13.5, color=stroke, bold=True))

    # комірки таблиці inode
    tx, tw = 340, 330
    n = 6
    cw = tw / n
    labels = ["1", "2", "3", "…", "4211", "…"]
    for i, lb in enumerate(labels):
        cx = tx + i * cw
        if i:
            p.append(line(cx, y0, cx, y0 + h0, color=WARM, sw=1.0))
        hot = (lb == "4211")
        if hot:
            p.append(rect(cx + 1, y0 + 1, cw - 2, h0 - 2, fill="#ffe8b0", stroke=WARM, sw=1.6, rx=2))
        p.append(text(cx + cw / 2, y0 + h0 / 2 + 5, lb, size=13,
                      bold=hot, color=POS if hot else INK))

    # запис каталогу згори
    p.append(fitbox(300, 60, 300, 60, ["запис каталогу:", "report.txt → 4211"], size=14,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8, bold=True))
    hot_cx = tx + 4 * cw + cw / 2
    p.append(arrow(450, 120, hot_cx, y0, color=NEG, sw=1.8))

    p.append(text(670, 370, "кількість комірок задано під час створення файлової системи",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'inode-table.svg'), W, H, *p)


# ── 5. Де сучасники тримали опис файлу ──────────────────────────────────────
def fig_where_description_lived():
    W, H = 1060, 700
    p = []
    p.append(text(W / 2, 36, "Де живе опис файлу", size=17, bold=True, color=INK))

    LX, RX, PW = 60, 580, 420
    lc, rc = LX + PW / 2, RX + PW / 2

    p.append(text(lc, 76, "опис — усередині запису каталогу", size=15, bold=True, color=POS))
    p.append(text(lc, 100, "OS/360 (1966), Multics до 1976, згодом FAT (1977)", size=12, color=MUTED))
    p.append(text(rc, 76, "опис — окремий об'єкт, каталог лише вказує", size=15, bold=True, color=FIELD))
    p.append(text(rc, 100, "Unix на PDP-7 (1969)", size=12, color=MUTED))

    # тир А: каталог
    for x, fill, stroke, rowlines in (
            (LX, RED_FILL, POS, ["report.txt · права · розмір · часи", "· і тут-таки адреси блоків"]),
            (RX, BLUE_FILL, NEG, ["report.txt → 4211", "більше в рядку немає нічого"])):
        p.append(rect(x, 120, PW, 112, fill=fill, stroke=stroke, sw=2, rx=8))
        p.append(text(x + PW / 2, 146, "каталог", size=13.5, bold=True, color=stroke))
        p.append(line(x, 158, x + PW, 158, color=stroke, sw=1.1))
        p.append(fitbox(x + 22, 168, PW - 44, 54, rowlines, size=12.5,
                        fill=FILL, stroke=LINE, sw=1.2))

    # тир Б: i-список (лише праворуч)
    p.append(text(LX + 20, 312, "проміжного рівня немає", size=13, color=MUTED, anchor="start"))
    p.append(rect(RX + 35, 280, 350, 54, fill=WARM_FILL, stroke=WARM, sw=2, rx=6))
    cw = 350 / 6
    for i, lb in enumerate(["1", "2", "3", "…", "4211", "…"]):
        cx = RX + 35 + i * cw
        if i:
            p.append(line(cx, 280, cx, 334, color=WARM, sw=1.0))
        hot = (lb == "4211")
        if hot:
            p.append(rect(cx + 1, 281, cw - 2, 52, fill="#ffe8b0", stroke=WARM, sw=1.5, rx=2))
        p.append(text(cx + cw / 2, 313, lb, size=12.5, bold=hot, color=POS if hot else INK))
    p.append(text(rc - 15, 358, "i-список: плаский масив описів", size=12.5, color=WARM, anchor="end"))

    # тир В: блоки
    for cx in (lc, rc):
        for k, bx in enumerate((cx - 155, cx - 45, cx + 65)):
            p.append(rect(bx, 400, 90, 48, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=5))
            p.append(text(bx + 45, 430, "блок", size=12.5, color=INK))

    p.append(arrow(lc, 232, lc, 396, color=POS, sw=1.8))
    p.append(arrow(rc, 232, rc, 276, color=NEG, sw=1.8))
    p.append(arrow(rc, 334, rc, 396, color=WARM, sw=1.8))

    p.append(fitbox(LX, 490, PW, 180,
                    ["друге ім'я — це другий такий рядок,",
                     "а отже, друга правда про той самий вміст",
                     "стерли рядок — стерли й опис",
                     "пристрій сюди не вкладається"],
                    size=13.5, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(fitbox(RX, 490, PW, 180,
                    ["скільки завгодно імен — один опис",
                     "рядок можна прибрати, а опис лишиться",
                     "права й тип належать вмісту",
                     "пристрій — теж елемент списку, просто без блоків"],
                    size=13.5, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'where-description-lived.svg'), W, H, *p)


# ── Розкладка st_mode (вставка api-stat-fields) ─────────────────────────────
def fig_stat_mode_bits():
    W, H = 1120, 470
    p = []
    p.append(text(W / 2, 42, "st_mode — 16 значущих бітів одного цілого числа",
                  size=15, bold=True, color=INK))

    x0, cw, cy, ch = 64, 62, 100, 54
    bits = ["1", "0", "0", "0",
            "0", "0", "0",
            "1", "1", "0", "1", "0", "0", "1", "0", "0"]
    groups = [(0, 4, BLUE_FILL, NEG), (4, 7, WARM_FILL, WARM), (7, 16, GREEN_FILL, FIELD)]
    for a, b, fill, stroke in groups:
        for i in range(a, b):
            bx = x0 + i * cw
            p.append(rect(bx, cy, cw, ch, fill=fill, stroke=stroke, sw=1.5, rx=4))
            p.append(text(bx + cw / 2, cy + 35, bits[i], size=16, bold=True, color=stroke))
            p.append(text(bx + cw / 2, cy - 14, str(15 - i), size=11, color=MUTED))

    gy, gh = 172, 44
    gnames = ["тип файлу", "особливі біти", "права доступу"]
    for (a, b, fill, stroke), nm in zip(groups, gnames):
        p.append(fitbox(x0 + a * cw, gy, (b - a) * cw, gh, [nm], size=14, bold=True,
                        fill=fill, stroke=stroke, sw=1.8))

    ey, eh = 236, 110
    expl = [["маска S_IFMT = 0170000",
             "перевірка — лише макросом",
             "S_ISREG / S_ISDIR / S_ISLNK"],
            ["S_ISUID   04000",
             "S_ISGID   02000",
             "S_ISVTX   01000"],
            ["власник · група · решта — по три біти rwx",
             "S_IRWXU | S_IRWXG | S_IRWXO = 00777",
             "те, що ставить chmod, — це st_mode & 07777"]]
    for (a, b, fill, stroke), lines in zip(groups, expl):
        p.append(fitbox(x0 + a * cw, ey, (b - a) * cw, eh, lines,
                        size=13, fill=FILL, stroke=stroke, sw=1.4))

    p.append(fitbox(x0, 372, 16 * cw, 64,
                    ["приклад: 0100644 — звичайний файл із правами rw-r--r--",
                     "тип займає чотири біти, а не один вісімковий розряд, — тому маска типу двоцифрова"],
                    size=13.5, fill=WARM_FILL, stroke=WARM, sw=1.6))

    render(os.path.join(IMG, 'stat-mode-bits.svg'), W, H, *p)


# ── Маска statx (вставка api-stat-fields) ───────────────────────────────────
def fig_statx_mask():
    W, H = 1120, 430
    p = []
    p.append(text(W / 2, 40, "statx: маска — це питання, stx_mask — чесна відповідь",
                  size=15, bold=True, color=INK))

    by, bh = 86, 170
    cols = [(44, 300, "запит", NEG, BLUE_FILL,
             ["mask, який передали:",
              "STATX_BASIC_STATS",
              "| STATX_BTIME",
              "| STATX_MNT_ID"]),
            (404, 260, "ядро", MUTED, FILL,
             ["питає драйвер ФС",
              "і заповнює те, що той уміє;",
              "зайве, що дісталося задарма,",
              "теж кладе — і теж позначає"]),
            (724, 352, "відповідь", FIELD, GREEN_FILL,
             ["stx_mask, який повернули:",
              "є: BASIC_STATS, MNT_ID",
              "немає: BTIME —",
              "ext4 зі 128-байтовим inode",
              "її просто не зберігає"])]
    for x, w, ttl, stroke, fill, lines in cols:
        p.append(text(x + w / 2, 70, ttl, size=13.5, bold=True, color=stroke))
        p.append(fitbox(x, by, w, bh, lines, size=14, fill=fill, stroke=stroke, sw=1.8))

    p.append(arrow(344, by + bh / 2, 404, by + bh / 2, sw=2))
    p.append(arrow(664, by + bh / 2, 724, by + bh / 2, sw=2))

    p.append(fitbox(44, 300, 1032, 96,
                    ["поле, чийого біта немає в stx_mask, читати не можна:",
                     "там нуль, а нуль у stx_btime — це 1 січня 1970 року,",
                     "цілком правдоподібна дата, якої ніщо не позначить помилкою"],
                    size=14, fill=RED_FILL, stroke=POS, sw=2))

    render(os.path.join(IMG, 'statx-mask.svg'), W, H, *p)


if __name__ == '__main__':
    fig_name_to_inode()
    fig_block_map()
    fig_two_counters()
    fig_inode_table()
    fig_where_description_lived()
    fig_stat_mode_bits()
    fig_statx_mask()
    print("ok")
