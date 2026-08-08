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


# ── 1. Три способи мати два імені для одного вмісту ──────────────────────────
def fig_three_kinds():
    W, H = 1240, 660
    p = []

    panels = [
        (40, "жорстке посилання", "ln vm.img backup.img"),
        (450, "копія з поділом блоків", "cp --reflink=always vm.img backup.img"),
        (860, "повна копія", "cp --reflink=never vm.img backup.img"),
    ]
    PW = 340

    for x0, ptitle, cmd in panels:
        p.append(rect(x0, 52, PW, 480, fill=BG, stroke=MUTED, sw=1.4, rx=8))
        p.append(text(x0 + PW / 2, 78, ptitle, size=15, bold=True, color=INK))
        p.append(text(x0 + PW / 2, 100, cmd, size=11, color=MUTED))

    # ── панель 1: одне inode, дві назви
    x0 = 40
    p.append(fitbox(x0 + 20, 120, 140, 40, "vm.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(x0 + 180, 120, 140, 40, "backup.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(x0 + 90, 162, x0 + 150, 208, color=MUTED, sw=1.5))
    p.append(arrow(x0 + 250, 162, x0 + 190, 208, color=MUTED, sw=1.5))
    p.append(fitbox(x0 + 60, 212, 220, 74,
                    ["inode 812", "назв: 2"], size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(arrow(x0 + 170, 288, x0 + 170, 328, color=NEG, sw=1.8))
    p.append(fitbox(x0 + 40, 332, 260, 48, "блоки 1204…33971", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(x0 + 20, 400, 300, 116,
                    ["файл ОДИН, у нього два імені",
                      "запис через одне ім'я",
                      "видно через друге",
                      "права й час — спільні"],
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.6))

    # ── панель 2: два inode, спільні блоки
    x0 = 450
    p.append(fitbox(x0 + 20, 120, 140, 40, "vm.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(x0 + 180, 120, 140, 40, "backup.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(x0 + 90, 162, x0 + 90, 208, color=MUTED, sw=1.5))
    p.append(arrow(x0 + 250, 162, x0 + 250, 208, color=MUTED, sw=1.5))
    p.append(fitbox(x0 + 16, 212, 148, 74, ["inode 812", "назв: 1"], size=12.5,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(x0 + 176, 212, 148, 74, ["inode 913", "назв: 1"], size=12.5,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(arrow(x0 + 90, 288, x0 + 140, 328, color=NEG, sw=1.8))
    p.append(arrow(x0 + 250, 288, x0 + 200, 328, color=NEG, sw=1.8))
    p.append(fitbox(x0 + 40, 332, 260, 48, "блоки 1204…33971", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(x0 + 40, 386, 260, 30, "власників: 2", size=12.5,
                    fill=RED_FILL, stroke=POS, sw=1.6, bold=True))
    p.append(fitbox(x0 + 20, 424, 300, 92,
                    ["файли ДВА і вони незалежні",
                      "спільні лише блоки — доти,",
                      "доки хтось не почне писати"],
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.6))

    # ── панель 3: два inode, різні блоки
    x0 = 860
    p.append(fitbox(x0 + 20, 120, 140, 40, "vm.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(x0 + 180, 120, 140, 40, "backup.img", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(x0 + 90, 162, x0 + 90, 208, color=MUTED, sw=1.5))
    p.append(arrow(x0 + 250, 162, x0 + 250, 208, color=MUTED, sw=1.5))
    p.append(fitbox(x0 + 16, 212, 148, 74, ["inode 812", "назв: 1"], size=12.5,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(x0 + 176, 212, 148, 74, ["inode 914", "назв: 1"], size=12.5,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(arrow(x0 + 90, 288, x0 + 90, 328, color=NEG, sw=1.8))
    p.append(arrow(x0 + 250, 288, x0 + 250, 328, color=NEG, sw=1.8))
    p.append(fitbox(x0 + 16, 332, 148, 48, "блоки 1204…", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(x0 + 176, 332, 148, 48, "блоки 90112…", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(x0 + 20, 400, 300, 116,
                    ["файли ДВА і байти теж двоє",
                      "сорок гігабайтів прочитано",
                      "й записано наново",
                      "місця на носії — удвічі більше"],
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.6))

    p.append(fitbox(40, 552, 1160, 74,
                    ["ім'я відв'язане від inode — звідси жорсткі посилання;  inode відв'язаний від блоків — звідси поділ блоків",
                      "перше дає одному файлові багато назв, друге дає одному блокові багато власників"],
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=2, bold=True))

    render(os.path.join(IMG, 'three-kinds.svg'), W, H, *p,
           title="два імені для сорока гігабайтів: три різні речі")


# ── 2. Бітова карта проти лічильника власників ──────────────────────────────
def fig_bit_vs_counter():
    W, H = 1180, 600
    p = []

    # ── ряд 1: бітова карта
    p.append(fitbox(40, 52, 1100, 36,
                    "облік вільного місця бітовою картою: на блок відведено один біт — зайнято або вільно",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.6, bold=True))
    p.append(fitbox(60, 106, 300, 96,
                    ["блок 1204: біт = 1", "у карті двох файлів", "стоїть той самий номер"],
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(400, 138, "rm vm.img", size=12, color=MUTED))
    p.append(arrow(366, 156, 434, 156, color=MUTED, sw=1.8))
    p.append(fitbox(440, 106, 300, 96,
                    ["біт скидає той, хто стер", "перший: біт = 0", "запитати «а скільки ще?» нема в кого"],
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(arrow(746, 156, 814, 156, color=MUTED, sw=1.8))
    p.append(fitbox(820, 106, 300, 96,
                    ["блок віддано новому файлу", "backup.img читає чужі байти", "це не хиба, а брак числа"],
                    size=12.5, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(fitbox(60, 218, 1060, 34,
                    "ext4, ext3, ext2 — тут поділу блоків не буде ніколи: місця під лічильник немає у форматі",
                    size=13, fill=BG, stroke=POS, sw=1.6))

    # ── ряд 2: лічильник
    p.append(fitbox(40, 296, 1100, 36,
                    "облік деревом лічильників: на екстент відведено число — скільки файлів на нього посилається",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.6, bold=True))
    p.append(fitbox(60, 350, 300, 96,
                    ["екстент 1204+32768", "власників: 2", "число лежить в окремому дереві"],
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(400, 382, "rm vm.img", size=12, color=MUTED))
    p.append(arrow(366, 400, 434, 400, color=MUTED, sw=1.8))
    p.append(fitbox(440, 350, 300, 96,
                    ["лічильник зменшується", "власників: 1", "жодного блока не звільнено"],
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(arrow(746, 400, 814, 400, color=MUTED, sw=1.8))
    p.append(fitbox(820, 350, 300, 96,
                    ["місце повернеться тоді,", "коли лічильник дійде нуля", "backup.img читає своє"],
                    size=12.5, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(60, 462, 1060, 34,
                    "XFS із reflink=1 (від ядра 4.9), Btrfs (від 2.6.29), OCFS2, bcachefs — лічильник у форматі є",
                    size=13, fill=BG, stroke=FIELD, sw=1.6))

    p.append(fitbox(40, 520, 1100, 56,
                    ["чи вміє файлова система ділити блоки — вирішує не набір викликів, а те,",
                      "чим у ній записано, що блок зайнято: бітом чи числом"],
                    size=14.5, fill=BLUE_FILL, stroke=NEG, sw=2, bold=True))

    render(os.path.join(IMG, 'bit-vs-counter.svg'), W, H, *p,
           title="що станеться зі спільним блоком, коли один із двох файлів зітруть")


# ── 3. Запис у спільний екстент розриває його на три ─────────────────────────
def fig_write_splits():
    W, H = 1220, 600
    p = []

    L, R = 250, 1120
    M1, M2 = 610, 750      # межі середньої ділянки (не в масштабі)

    p.append(fitbox(60, 52, 1100, 34,
                    "було: обидві карти описано одним записом — від нуля до 40 ГіБ",
                    size=13.5, fill=GREY_FILL, stroke=MUTED, sw=1.6, bold=True))

    p.append(text(150, 122, "vm.img", size=13, color=INK, bold=True))
    p.append(fitbox(L, 100, R - L, 42, "екстент: блоки 1204 + 10 485 760", size=13,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(text(150, 176, "backup.img", size=13, color=INK, bold=True))
    p.append(fitbox(L, 154, R - L, 42, "той самий екстент", size=13,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(L, 204, R - L, 32, "у дереві лічильників на цей екстент записано: власників 2",
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.6))

    p.append(fitbox(60, 264, 1100, 34,
                    "стало: backup.img записав 4 КіБ на зсуві 20 ГіБ",
                    size=13.5, fill=GREY_FILL, stroke=MUTED, sw=1.6, bold=True))

    p.append(text(150, 336, "vm.img", size=13, color=INK, bold=True))
    p.append(fitbox(L, 314, M1 - L, 42, "старі блоки", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(M1, 314, M2 - M1, 42, "старі", size=12.5,
                    fill=GREY_FILL, stroke=MUTED, sw=1.8))
    p.append(fitbox(M2, 314, R - M2, 42, "старі блоки", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(text(150, 390, "backup.img", size=13, color=INK, bold=True))
    p.append(fitbox(L, 368, M1 - L, 42, "старі блоки", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(M1, 368, M2 - M1, 42, "новий", size=12.5,
                    fill=RED_FILL, stroke=POS, sw=1.8, bold=True))
    p.append(fitbox(M2, 368, R - M2, 42, "старі блоки", size=12.5,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(text((L + M1) / 2, 434, "власників 2", size=12, color=NEG))
    p.append(text((M1 + M2) / 2, 434, "по 1 у кожного", size=12, color=POS))
    p.append(text((M2 + R) / 2, 434, "власників 2", size=12, color=NEG))

    p.append(fitbox(60, 458, 1100, 116,
                    ["один запис у 4 КіБ забрав 4 КіБ вільного місця — хоч байти нібито вже були виділені",
                      "тому write у спільну ділянку може відмовити з ENOSPC на повному носії",
                      "і тому карта одного запису перетворилася на карту трьох: поділ блоків платить дробленням"],
                    size=13.5, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'write-splits.svg'), W, H, *p,
           title="запис у спільну ділянку: копіювання при записі на рівні екстентів")


# ── 4. Правило вирівнювання діапазону і виняток для хвоста ───────────────────
def fig_alignment_rule():
    W, H = 1220, 700
    p = []

    X0, X1 = 60, 880
    SIZE = 20000                     # st_size файлу-джерела, байти
    BLK = 4096
    sc = (X1 - X0) / float(SIZE)

    def bx(off):
        return X0 + off * sc

    rows = [
        (78, "src_offset = 8192,  src_length = 8192",
         8192, 8192, True,
         ["обидва кінці лягли", "на межу блока"]),
        (258, "src_offset = 8192,  src_length = 6000",
         8192, 6000, False,
         ["кінець упав усередину", "блока — EINVAL"]),
        (438, "src_offset = 16384,  src_length = 3616",
         16384, 3616, True,
         ["кінець збігся з EOF —", "хвіст вирівнювати не треба"]),
    ]

    for ybase, caption, off, ln, okflag, verdict in rows:
        ys = ybase + 46
        p.append(text(X0, ybase + 12, caption, size=14.5, anchor="start",
                      color=INK, bold=True))

        # сітка блоків файлу-джерела
        b = 0
        while b < SIZE:
            e = min(b + BLK, SIZE)
            partial = (e - b) < BLK
            p.append(rect(bx(b), ys, bx(e) - bx(b), 46,
                          fill=BG if partial else GREY_FILL,
                          stroke=MUTED, sw=1.2, rx=0))
            if partial:
                p.append(text((bx(b) + bx(e)) / 2, ys + 29, "неповний",
                              size=11, color=MUTED))
            b = e

        # смуга запитаного діапазону
        col = FIELD if okflag else POS
        fillcol = GREEN_FILL if okflag else RED_FILL
        p.append(rect(bx(off), ys - 22, bx(off + ln) - bx(off), 16,
                      fill=fillcol, stroke=col, sw=2, rx=3))

        # межі блоків підписами під смугою
        for v in (0, 4096, 8192, 12288, 16384, 20000):
            p.append(line(bx(v), ys + 46, bx(v), ys + 56, color=MUTED, sw=1.1))
            p.append(text(bx(v), ys + 72, str(v), size=11.5, color=MUTED))
        p.append(text(bx(SIZE), ys + 90, "EOF", size=11.5, color=INK, bold=True))

        # кінець діапазону, якщо він не збігся з жодною межею
        end = off + ln
        if end % BLK != 0 and end != SIZE:
            p.append(line(bx(end), ys - 30, bx(end), ys + 56, color=POS, sw=1.6,
                          dash="4,3"))
            p.append(text(bx(end), ys + 108, str(end), size=12, color=POS, bold=True))

        p.append(fitbox(920, ys - 24, 250, 70, verdict, size=12.5,
                        fill=fillcol, stroke=col, sw=2))

    p.append(fitbox(60, 616, 1110, 56,
                    ["src_offset, dest_offset і src_length кратні розміру блока — інакше EINVAL;",
                     "єдиний виняток: діапазон, що впирається в кінець файлу-джерела"],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'alignment-rule.svg'), W, H, *p,
           title="що саме має бути вирівняне у FICLONERANGE і FIDEDUPERANGE")


# ── 5. Розкладка запиту дедуплікації в пам'яті ───────────────────────────────
def fig_dedupe_layout():
    W, H = 1220, 700
    p = []

    BX, BW = 70, 400
    RH = 36

    def bar(y, s, fill, stroke):
        return fitbox(BX, y, BW, 30, s, size=12.5, fill=fill, stroke=stroke,
                      sw=1.6, bold=True)

    def field(y, s, who):
        fill = BLUE_FILL if who == "prog" else GREEN_FILL
        stroke = NEG if who == "prog" else FIELD
        if who == "zero":
            fill, stroke = GREY_FILL, MUTED
        return fitbox(BX, y, BW, RH - 4, s, size=12.5, fill=fill, stroke=stroke, sw=1.5)

    y = 66
    p.append(bar(y, "struct file_dedupe_range — заголовок, 24 Б", GREY_FILL, MUTED))
    y += 38
    for s, who in [("__u64 src_offset      8 Б", "prog"),
                   ("__u64 src_length      8 Б", "prog"),
                   ("__u16 dest_count      2 Б", "prog"),
                   ("__u16 reserved1  +  __u32 reserved2      6 Б", "zero")]:
        p.append(field(y, s, who))
        y += RH

    y += 14
    p.append(bar(y, "info[0] — struct file_dedupe_range_info, 32 Б", GREY_FILL, MUTED))
    y += 38
    for s, who in [("__s64 dest_fd         8 Б", "prog"),
                   ("__u64 dest_offset     8 Б", "prog"),
                   ("__u64 bytes_deduped   8 Б", "kern"),
                   ("__s32 status  +  __u32 reserved      8 Б", "kern")]:
        p.append(field(y, s, who))
        y += RH

    y += 14
    p.append(rect(BX, y, BW, 52, fill=BG, stroke=MUTED, sw=1.6, rx=6))
    p.append(mtext(BX + BW / 2, y + 22,
                   ["info[1] … info[dest_count − 1]",
                    "той самий запис, по 32 Б"], size=12.5, color=MUTED))

    # права колонка
    RX, RW = 540, 620
    p.append(fitbox(RX, 66, RW, 34,
                    "виклик роблять на дескрипторі ДЖЕРЕЛА: ioctl(src_fd, FIDEDUPERANGE, &arg)",
                    size=13, fill=WARM_FILL, stroke=WARM, sw=2, bold=True))

    p.append(fitbox(RX, 118, RW, 118,
                    ["стеля на кількість призначень — розмір сторінки:",
                     "24 + 32 · dest_count ≤ 4096",
                     "32 · dest_count ≤ 4072",
                     "dest_count ≤ 127"],
                    size=13.5, fill=BLUE_FILL, stroke=NEG, sw=2))

    p.append(fitbox(RX, 252, RW, 96,
                    ["src_length ядро мовчки обрізає:",
                     "типова стеля — 16 МіБ на один виклик,",
                     "більше просити можна, але скопійовано буде менше"],
                    size=13.5, fill=GREY_FILL, stroke=MUTED, sw=1.8))

    p.append(fitbox(RX, 364, RW, 130,
                    ["ioctl повертає 0 (успіх) навіть тоді,",
                     "коли ЖОДНОГО байта не злито:",
                     "успіх виклику означає лише «ядро порівняло»,",
                     "результат кожного призначення — у власному status"],
                    size=13.5, fill=RED_FILL, stroke=POS, sw=2))

    p.append(fitbox(RX, 510, RW, 96,
                    ["status = FILE_DEDUPE_RANGE_SAME (0)      байти збіглися, блоки поділено",
                     "status = FILE_DEDUPE_RANGE_DIFFERS (1)   байти розійшлися, нічого не змінено"],
                    size=12.5, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    # легенда
    p.append(fitbox(70, 626, 400, 44, "заповнює програма перед викликом",
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.5))
    p.append(fitbox(540, 626, 400, 44, "заповнює ядро на поверненні",
                    size=12.5, fill=GREEN_FILL, stroke=FIELD, sw=1.5))
    p.append(fitbox(980, 626, 180, 44, "має бути нулем",
                    size=12.5, fill=GREY_FILL, stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, 'dedupe-layout.svg'), W, H, *p,
           title="запит FIDEDUPERANGE: один заголовок і масив призначень змінної довжини")


# ── 6. Розмір вікна хешування вирішує, скільки взагалі можна знайти ──────────
NB4K = 256                                    # 1 МіБ файлу блоками по 4 КіБ
DIRTY4K = [5, 11, 37, 38, 96, 140, 200, 205]  # переписані блоки (3 %)


def fig_dedupe_window():
    W, H = 1340, 760
    p = []
    X0, SW = 272, 780

    p.append(text(X0 - 16, 88, "що справді відрізняється", size=13.5, bold=True, anchor="end"))
    p.append(text(X0 - 16, 108, "8 блоків по 4 КіБ із 256", size=11.5, color=MUTED, anchor="end"))
    p.append(rect(X0, 72, SW, 36, fill=GREEN_FILL, stroke=FIELD, sw=1.4, rx=4))
    cw = SW / float(NB4K)
    for c in DIRTY4K:
        p.append(rect(X0 + c * cw, 72, max(cw, 2.6), 36,
                      fill=RED_FILL, stroke=POS, sw=1.0, rx=1))
    p.append(text(X0 + SW + 18, 94, "p = 3 %", size=13, color=POS, anchor="start", bold=True))

    rows = [(196, "цілий файл",    256, "0 вікон із 1",   "спільних 0"),
            (326, "вікно 128 КіБ",  32, "3 вікна з 8",    "спільних 15.1 ГіБ"),
            (456, "вікно 16 КіБ",    4, "57 вікон із 64", "спільних 35.4 ГіБ")]
    for y, lab, bpw, cnt, gain in rows:
        nwin = NB4K // bpw
        ww = SW / float(nwin)
        p.append(text(X0 - 16, y + 18, lab, size=14, bold=True, anchor="end"))
        p.append(text(X0 - 16, y + 38, "%d блоків у вікні" % bpw,
                      size=11.5, color=MUTED, anchor="end"))
        for i in range(nwin):
            dirty = any(c // bpw == i for c in DIRTY4K)
            p.append(rect(X0 + i * ww + 0.7, y, max(ww - 1.4, 1.8), 44,
                          fill=RED_FILL if dirty else GREEN_FILL,
                          stroke=POS if dirty else FIELD, sw=1.0, rx=2))
        p.append(text(X0 + SW + 18, y + 18, cnt, size=12.5, anchor="start"))
        p.append(text(X0 + SW + 18, y + 38, gain, size=12.5, anchor="start", color=FIELD))

    p.append(fitbox(56, 574, 1228, 130,
                    ["вікно вціліє, тільки якщо в ньому не змінилося НІЧОГО:   частка таких вікон = (1 − p) ^ (W / B)",
                     "p — частка переписаних блоків (тут 0.03), B — блок файлової системи 4 КіБ, W — вікно хешування",
                     "W = 40 ГіБ → 0.97^10485760 ≈ 0        W = 128 КіБ → 0.97³² = 0.377        W = 16 КіБ → 0.97⁴ = 0.885",
                     "дрібніше вікно знаходить більше — і коштує пам'яті: 24 Б на вікно, 60 МіБ проти 480 МіБ на дерево 320 ГіБ"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'dedupe-window.svg'), W, H, *p,
           title="чому по цілих файлах не знаходиться нічого, а по вікнах — майже все")


# ── 7. Від групи однакових хешів до одного виклику на кілька призначень ──────
def fig_dedupe_batch():
    W, H = 1330, 690
    p = []

    AX, AW = 56, 372
    p.append(text(AX + AW / 2, 76, "1. масив ключів, відсортований за хешем", size=14, bold=True))
    keyrows = [("0x1a2b…c4", "base", 17, True),
               ("0x1a2b…c4", "vm1",  17, True),
               ("0x1a2b…c4", "vm3",  41, True),
               ("0x1a2b…c4", "vm7",  17, True),
               ("0x93f0…08", "base", 18, False),
               ("0x93f0…08", "vm1",  18, False)]
    y = 100
    for h, f, w_, ingroup in keyrows:
        p.append(fitbox(AX, y, AW, 30, "%s    %-4s    вікно %d" % (h, f, w_), size=12.5,
                        fill=GREEN_FILL if ingroup else GREY_FILL,
                        stroke=FIELD if ingroup else MUTED, sw=1.4))
        y += 34
    p.append(text(AX + AW / 2, y + 24, "однаковий хеш — одна група", size=12.5, color=MUTED))
    p.append(text(AX + AW / 2, y + 46, "перший у групі стає джерелом", size=12.5, color=MUTED))

    BX, BW = 484, 372
    p.append(text(BX + BW / 2, 76, "2. продовження збігу за хешами", size=14, bold=True))
    bars = [("vm1 від вікна 17", 8, "8 вікон = 1 МіБ"),
            ("vm7 від вікна 17", 8, "8 вікон = 1 МіБ"),
            ("vm3 від вікна 41", 3, "3 вікна = 384 КіБ")]
    y = 116
    for lab, n, note in bars:
        p.append(text(BX, y, lab, size=12.5, anchor="start"))
        for i in range(n):
            p.append(rect(BX + i * 30, y + 12, 26, 26, fill=GREEN_FILL, stroke=FIELD, sw=1.2, rx=2))
        p.append(text(BX, y + 58, note, size=12, color=MUTED, anchor="start"))
        y += 88

    CX, CW = 912, 372
    p.append(text(CX + CW / 2, 76, "3. довжина у запиті одна на всіх", size=14, bold=True))
    p.append(fitbox(CX, 100, CW, 104,
                    ["виклик 1:  src_length = 1 МіБ",
                     "info[0] = vm1      info[1] = vm7",
                     "dest_count = 2"],
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(CX, 226, CW, 104,
                    ["виклик 2:  src_length = 384 КіБ",
                     "info[0] = vm3",
                     "dest_count = 1"],
                    size=12.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(CX, 352, CW, 96,
                    ["vm3 збігається коротше за інших,",
                     "тож в одну пачку з ними не йде:",
                     "спільну довжину довелося б різати"],
                    size=12.5, fill=RED_FILL, stroke=POS, sw=1.8))

    p.append(fitbox(56, 502, 1218, 118,
                    ["у пачку потрапляють лише ті призначення, у яких збіг такої самої довжини — інакше довелося б",
                     "просити мінімум і губити хвости довших збігів",
                     "пачка не робить порівняння спільним: ядро проходить призначення по черзі — вона економить переходи",
                     "в ядро й лишає джерело теплим у кеші сторінок"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'dedupe-batch.svg'), W, H, *p,
           title="від групи однакових хешів до діапазонів і пачок призначень")


# ── 8. Спільне розходиться від записів: дедуплікація — робота періодична ─────
def fig_dedupe_drift():
    W, H = 1180, 650
    p = []
    XL, XR, YB, YT = 130, 1090, 470, 120

    def gx(d):
        return XL + d * (XR - XL) / 28.0

    def gy(v):
        return YB - v * (YB - YT) / 280.0

    p.append(line(XL, YB, XR, YB, color=INK, sw=1.6))
    p.append(line(XL, YB, XL, YT, color=INK, sw=1.6))
    p.append(text(XL, YT - 28, "спільних байтів, ГіБ", size=13, anchor="start", bold=True))
    for v in (0, 80, 160, 240):
        p.append(line(XL - 8, gy(v), XL, gy(v), color=MUTED, sw=1.2))
        p.append(text(XL - 14, gy(v) + 5, str(v), size=12, color=MUTED, anchor="end"))
    for d in (0, 7, 14, 21, 28):
        p.append(line(gx(d), YB, gx(d), YB + 8, color=MUTED, sw=1.2))
        p.append(text(gx(d), YB + 30, "день %d" % d, size=12, color=MUTED))

    decay = [(0, 246, 7, 218), (7, 240, 14, 212), (14, 234, 21, 206), (21, 228, 28, 200)]
    p.append(line(gx(0), gy(0), gx(0), gy(246), color=POS, sw=3))
    for d0, v0, d1, v1 in decay:
        p.append(line(gx(d0), gy(v0), gx(d1), gy(v1), color=NEG, sw=2.4))
    for i, (d, v) in enumerate([(7, 240), (14, 234), (21, 228)]):
        p.append(line(gx(d), gy(decay[i][3]), gx(d), gy(v), color=POS, sw=3))

    p.append(line(gx(0), gy(246), gx(21), gy(228), color=MUTED, sw=1.4, dash="6,5"))
    p.append(text(gx(10.5), gy(246) - 22, "стеля падає: файли розходяться назавжди",
                  size=12.5, color=MUTED))

    p.append(fitbox(130, 522, 960, 108,
                    ["червоні стрибки вгору — прогони програми; сині спуски — звичайна робота машин:",
                     "кожен запис у спільну ділянку відщеплює власні блоки, і спільного стає менше щодня",
                     "прогін доводиться повторювати, а знаходить він щоразу трохи менше за попередній"],
                    size=13, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'dedupe-drift.svg'), W, H, *p,
           title="скільки спільних байтів лишається між прогонами дедуплікації")


if __name__ == '__main__':
    fig_three_kinds()
    fig_bit_vs_counter()
    fig_write_splits()
    fig_alignment_rule()
    fig_dedupe_layout()
    fig_dedupe_window()
    fig_dedupe_batch()
    fig_dedupe_drift()
    print("ok")
