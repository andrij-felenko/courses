# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def row(x, y, w, s, h=32, size=13, **kw):
    return fitbox(x, y, w, h, s, size=size, **kw)


# ── 1. Каталог як таблиця пар ім'я → номер inode ────────────────────────────
def fig_mapping():
    W, H = 1000, 500
    f = []
    f.append(text(200, 58, "КАТАЛОГИ — таблиці імен", size=13, bold=True, color=MUTED))
    f.append(text(580, 58, "INODE — файл без імені", size=13, bold=True, color=MUTED))
    f.append(text(870, 58, "ДАНІ", size=13, bold=True, color=MUTED))

    # каталог A
    f.append(fitbox(50, 74, 300, 38, "каталог ana/  —  сам файл, inode 12",
                    size=13, fill="#eef2f7", bold=True))
    f.append(row(50, 122, 300, "«.»  →  12"))
    f.append(row(50, 158, 300, "«..»  →  2"))
    f.append(row(50, 194, 300, "«notes.txt»  →  91", fill="#eaf7ef", stroke=FIELD))

    # каталог B
    f.append(fitbox(50, 284, 300, 38, "каталог backup/  —  inode 30",
                    size=13, fill="#eef2f7", bold=True))
    f.append(row(50, 332, 300, "«.»  →  30"))
    f.append(row(50, 368, 300, "«..»  →  2"))
    f.append(row(50, 404, 300, "«notes.old»  →  91", fill="#eaf7ef", stroke=FIELD))

    # inode
    f.append(fitbox(470, 200, 220, 120,
                    "inode 91\nnlink = 2\nправа · час · розмір\nблоки 1204, 1205",
                    size=13, fill="#fdf3ea"))

    # блоки даних
    f.append(fitbox(790, 196, 160, 44, "блок 1204", size=13))
    f.append(fitbox(790, 264, 160, 44, "блок 1205", size=13))

    # стрілки імен
    f.append(arrow(356, 210, 466, 240, color=FIELD))
    f.append(arrow(356, 420, 466, 288, color=FIELD))
    # стрілки на дані
    f.append(arrow(696, 240, 786, 218))
    f.append(arrow(696, 282, 786, 286))

    render(os.path.join(OUT, 'dir-mapping.svg'), W, H, *f,
           title="Ім'я живе в каталозі, дані — в inode")


# ── 2. Коли дані справді зникають ───────────────────────────────────────────
def fig_lifetime():
    W, H = 1040, 310
    f = []
    boxes = [
        (40, "два імені\nnlink = 2\nвідкритих: 1\nдані живі", "#eaf7ef", FIELD),
        (300, "одне ім'я\nnlink = 1\nвідкритих: 1\nдані живі", "#eaf7ef", FIELD),
        (560, "імені немає\nnlink = 0\nвідкритих: 1\nдані ще живі", "#fdf3ea", POS),
        (820, "nlink = 0\nвідкритих: 0\nблоки звільнено", "#eef2f7", LINE),
    ]
    for x, s, fill, stroke in boxes:
        f.append(fitbox(x, 110, 180, 120, s, size=13, fill=fill, stroke=stroke))

    labels = [(240, "unlink()"), (500, "unlink()"), (760, "close()")]
    for x, s in labels:
        f.append(arrow(x - 30, 170, x + 50, 170))
        f.append(text(x + 10, 143, s, size=13, bold=True))

    f.append(text(W / 2, 268,
                  "запис у каталозі й відкритий дескриптор тримають дані незалежно один від одного",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'unlink-lifetime.svg'), W, H, *f,
           title="Дані звільняються тільки тоді, коли на них не лишилось жодного посилання")


# ── 3. Перейменування міняє один запис таблиці ──────────────────────────────
def fig_rename():
    W, H = 1000, 400
    f = []
    f.append(fitbox(40, 70, 340, 36, "каталог /etc — ДО", size=13, fill="#eef2f7", bold=True))
    f.append(row(40, 116, 340, "«app.conf»  →  55"))
    f.append(row(40, 152, 340, "«app.conf.new»  →  77", fill="#eaf7ef", stroke=FIELD))

    f.append(fitbox(620, 70, 340, 36, "каталог /etc — ПІСЛЯ", size=13, fill="#eef2f7", bold=True))
    f.append(row(620, 116, 340, "«app.conf»  →  77", fill="#eaf7ef", stroke=FIELD))

    f.append(text(500, 122, "rename()", size=14, bold=True))
    f.append(arrow(420, 152, 580, 152))
    f.append(text(500, 182, "один крок", size=12, color=MUTED))

    f.append(fitbox(40, 250, 380, 96,
                    "inode 55 — стара версія\nnlink: 1 → 0\nблоки звільняться, коли їх ніхто не тримає",
                    size=13, fill="#fdf3ea"))
    f.append(fitbox(580, 250, 380, 96,
                    "inode 77 — нова версія\nnlink: 1\nбайти на диску не зрушили з місця",
                    size=13, fill="#eaf7ef", stroke=FIELD))

    render(os.path.join(OUT, 'rename-atomic.svg'), W, H, *f,
           title="Перейменування переписує запис, а не дані")


# ── 4. Скільки коштує знайти ім'я ───────────────────────────────────────────
def fig_lookup():
    W, H = 1000, 430
    f = []
    f.append(text(250, 60, "каталог без індексу", size=14, bold=True))
    ys = [90, 146, 202, 258]
    names = ["блок 0: записи", "блок 1: записи", "блок 2: записи", "блок 3: тут шукане ім'я"]
    for i, y in enumerate(ys):
        hit = (i == 3)
        f.append(fitbox(110, y, 290, 44, names[i], size=13,
                        fill="#eaf7ef" if hit else FILL,
                        stroke=FIELD if hit else LINE))
    f.append(arrow(85, 90, 85, 300))
    f.append(text(250, 336, "перебір записів підряд", size=13, color=MUTED))
    f.append(text(250, 360, "у середньому — пів каталогу", size=13, color=MUTED))

    f.append(text(750, 60, "каталог з індексом", size=14, bold=True))
    f.append(fitbox(620, 90, 260, 50, "корінь: хеш → блок", size=13, fill="#eef2f7"))
    f.append(fitbox(540, 202, 130, 44, "блок A", size=13))
    f.append(fitbox(685, 202, 130, 44, "блок B", size=13, fill="#eaf7ef", stroke=FIELD))
    f.append(fitbox(830, 202, 130, 44, "блок C", size=13))
    f.append(arrow(680, 144, 610, 198))
    f.append(arrow(750, 144, 750, 198))
    f.append(arrow(820, 144, 890, 198))
    f.append(text(750, 336, "hash(ім'я) вказує на один блок", size=13, color=MUTED))
    f.append(text(750, 360, "1–2 читання незалежно від розміру", size=13, color=MUTED))

    render(os.path.join(OUT, 'dir-index.svg'), W, H, *f,
           title="Ціна пошуку імені: перебір проти індексу")


# ── 5. Що лежить у буфері після getdents64() ────────────────────────────────
def fig_dirent_buffer():
    W, H = 1060, 372
    f = []
    f.append(text(W / 2, 54,
                  "буфер програми після getdents64(fd, buf, count): записи різної довжини лежать упритул",
                  size=13, color=MUTED))

    for x, s in [(40, "+0"), (300, "+24"), (600, "+56"), (820, "+80")]:
        f.append(text(x, 80, s, size=12, color=MUTED, anchor="start"))

    f.append(fitbox(40, 90, 256, 52, "запис «.»\nd_reclen = 24", size=13, fill="#eef2f7"))
    f.append(fitbox(300, 90, 296, 52, "запис «notes.txt»\nd_reclen = 32",
                    size=13, fill="#eaf7ef", stroke=FIELD))
    f.append(fitbox(600, 90, 216, 52, "запис «src»\nd_reclen = 24", size=13, fill="#eef2f7"))
    f.append(fitbox(820, 90, 200, 52, "хвіст буфера\nне заповнено", size=13, fill=BG, stroke=MUTED))

    f.append(line(300, 144, 60, 190, color=MUTED, dash="5 4"))
    f.append(line(596, 144, 1000, 190, color=MUTED, dash="5 4"))

    cells = [
        (60, 150, "d_ino\n8 байтів"),
        (210, 150, "d_off\n8 байтів"),
        (360, 140, "d_reclen\n2 байти"),
        (500, 120, "d_type\n1 байт"),
        (620, 240, "d_name\n«notes.txt» + \\0"),
        (860, 140, "вирівняно\nдо межі 8"),
    ]
    for x, w, s in cells:
        f.append(fitbox(x, 190, w, 60, s, size=13,
                        fill="#eaf7ef" if x == 620 else FILL,
                        stroke=FIELD if x == 620 else LINE))

    notes = [
        "d_off — не байтове зміщення, а непрозорий маркер позиції: його місце в seekdir(), не в арифметиці",
        "d_type буває DT_UNKNOWN — не кожна файлова система його заповнює; тоді тип питають у fstatat()",
        "перехід до наступного запису — тільки bp += d_reclen: розміру структури тут не існує",
    ]
    for i, s in enumerate(notes):
        f.append(text(W / 2, 284 + i * 24, s, size=12, color=MUTED))

    render(os.path.join(OUT, 'getdents-buffer.svg'), W, H, *f,
           title="Один буфер getdents64: ланцюг записів змінної довжини")


# ── 6. Шлях розв'язується щоразу заново, дескриптор — ні ────────────────────
def fig_anchor():
    W, H = 1080, 560
    COLS = (190, 485, 780)
    BW = 270
    f = []

    def lane(y, s):
        return fitbox(30, y, 140, 64, s, size=13, fill="#eef2f7", bold=True)

    # верхня панель: рядок-шлях
    f.append(text(W / 2, 62, "Наївно: щоразу новий рядок-шлях", size=14, bold=True))
    f.append(lane(78, "наш\nпроцес"))
    f.append(lane(158, "зловмисник"))
    f.append(fitbox(COLS[0], 78, BW, 64,
                    "1  readdir()\n«logs» є в таблиці", size=13))
    f.append(fitbox(COLS[1], 158, BW, 64,
                    "2  запис підмінено:\n«logs» → symlink на /etc",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(fitbox(COLS[2], 78, BW, 64,
                    "3  lstat(\"dump/logs\")\nміряє вже /etc",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(arrow(COLS[0], 248, COLS[2] + BW, 248, color=MUTED))
    f.append(text(COLS[2] + BW - 44, 238, "час", size=12, color=MUTED))

    # нижня панель: дескриптор
    f.append(text(W / 2, 318, "З дескриптором: ім'я вживається один раз", size=14, bold=True))
    f.append(lane(334, "наш\nпроцес"))
    f.append(lane(414, "зловмисник"))
    f.append(fitbox(COLS[0], 334, BW, 64,
                    "1  openat(dfd, «logs»,\nO_DIRECTORY|O_NOFOLLOW)\n→ fd 5", size=13))
    f.append(fitbox(COLS[1], 414, BW, 64,
                    "2  та сама підміна\nзапису в таблиці",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(fitbox(COLS[2], 334, BW, 64,
                    "3  fstatat(fd 5, …)\nтой самий inode",
                    size=13, fill="#eaf7ef", stroke=FIELD))
    f.append(arrow(COLS[0], 504, COLS[2] + BW, 504, color=MUTED))
    f.append(text(COLS[2] + BW - 44, 494, "час", size=12, color=MUTED))

    render(os.path.join(OUT, 'walk-anchor.svg'), W, H, *f,
           title="Рядок-шлях можна підмінити між викликами, дескриптор — ні")


fig_mapping()
fig_lifetime()
fig_rename()
fig_lookup()
fig_dirent_buffer()
fig_anchor()
print("ok")


# ── 7. Три покоління формату запису каталогу (для нарису історії) ───────────
def fig_record_evolution():
    W, H = 1060, 620
    f = []

    # --- V7: фіксовані 16 байтів ---
    f.append(text(60, 46, "V7 (1979) — фіксовані 16 байтів", size=15, bold=True,
                  anchor="start"))
    f.append(text(60, 70, "512-байтовий блок вміщає рівно 32 записи; жоден не перетинає межу",
                  size=12, color=MUTED, anchor="start"))
    x = 60
    for i in range(4):
        f.append(fitbox(x, 88, 60, 44, "ino\n2 Б", size=11, fill="#fdf3ea"))
        f.append(fitbox(x + 60, 88, 150, 44, "ім'я — 14 байтів", size=11, fill=FILL))
        x += 218
    f.append(text(60, 154, "довше ім'я просто обтинається до 14 байтів",
                  size=12, color=POS, anchor="start"))

    # --- FFS/ext2: змінна довжина ---
    f.append(text(60, 218, "4.2BSD FFS (1983) та ext2 (1993) — змінна довжина",
                  size=15, bold=True, anchor="start"))
    f.append(text(60, 242, "заголовок несе довжину запису, тож наступний знаходять додаванням",
                  size=12, color=MUTED, anchor="start"))
    y = 260
    f.append(fitbox(60, y, 70, 44, "ino", size=11, fill="#fdf3ea"))
    f.append(fitbox(130, y, 90, 44, "rec_len", size=11, fill="#eef2f7"))
    f.append(fitbox(220, y, 90, 44, "name_len", size=11, fill="#eef2f7"))
    f.append(fitbox(310, y, 300, 44, "ім'я — до 255 байтів", size=11, fill=FILL))
    f.append(fitbox(610, y, 130, 44, "вільний хвіст", size=11, fill="#f0f0f0"))
    f.append(fitbox(740, y, 70, 44, "ino", size=11, fill="#fdf3ea"))
    f.append(fitbox(810, y, 190, 44, "наступний запис", size=11, fill=FILL))
    f.append(text(60, 326, "видалений запис не стирають — його місце дописують до попереднього",
                  size=12, color=MUTED, anchor="start"))

    # --- htree ---
    f.append(text(60, 392, "htree (ext3/ext4, 2001–2002) — індекс поверх тих самих блоків",
                  size=15, bold=True, anchor="start"))
    f.append(fitbox(390, 416, 280, 52, "корінь індексу:\nдіапазон хешу → номер блока",
                    size=12, fill="#eef2f7", bold=True))
    for i, lab in enumerate(("блок 0", "блок 1", "блок 2")):
        bx = 150 + i * 300
        f.append(fitbox(bx, 528, 240, 52,
                        lab + " — звичайні записи\nзмінної довжини", size=12, fill=FILL))
        f.append(arrow(530, 470, bx + 120, 524, color=MUTED))
    f.append(text(60, 600,
                  "старе ядро бачить вузол індексу як порожній запис і читає каталог лінійно",
                  size=12, color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'record-evolution.svg'), W, H, *f,
           title="Три покоління формату запису каталогу")


fig_record_evolution()
print("ok")
