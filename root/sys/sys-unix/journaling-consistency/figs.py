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
GRAY_FILL = "#eef1f4"
WARM = "#b8860b"


# ── 1. Одна операція — три записи; збій лишає суперечливі метадані ──────────
def fig_split_write():
    W, H = 1120, 790
    p = []

    p.append(text(60, 74, 'echo "17:42 запуск" >> /var/log/app.log   —   три записи в три різні місця',
                  size=15, anchor="start", bold=True))

    # смуга носія
    p.append(rect(60, 120, 1000, 90, fill=GRAY_FILL, stroke=MUTED, sw=1.4, rx=8))
    cells = [
        (90, "бітова карта\n5000 → зайнятий"),
        (440, "блок даних 5000\nваші байти"),
        (790, "inode файлу\nрозмір, вказівник"),
    ]
    for i, (cx0, label) in enumerate(cells):
        p.append(fitbox(cx0, 136, 220, 58, label, size=13, fill=BG, stroke=INK, sw=1.6))
        p.append(circle(cx0 + 110, 100, 15, fill=WARM_FILL, stroke=WARM, sw=2))
        p.append(text(cx0 + 110, 105, str(i + 1), size=14, bold=True, color=WARM))

    p.append(text(60, 240, "носій виконує їх по одному й у порядку, який обирає сам — збій ловить будь-яку підмножину",
                  size=13, color=MUTED, anchor="start"))

    # дві панелі наслідків
    def panel(x0, title, tcolor, tfill, rows, verdict, vfill, vcolor, tag, tagcolor):
        out = []
        out.append(rect(x0, 285, 470, 435, fill=BG, stroke=tcolor, sw=1.8, rx=10))
        out.append(fitbox(x0, 285, 470, 44, title, size=15, bold=True,
                          fill=tfill, stroke=tcolor, sw=1.8, color=tcolor, rx=10))
        for j, (txt, ok) in enumerate(rows):
            out.append(fitbox(x0 + 20, 352 + j * 42, 430, 32, txt, size=13,
                              fill=GREEN_FILL if ok else RED_FILL,
                              stroke=FIELD if ok else POS, sw=1.4))
        out.append(arrow(x0 + 235, 488, x0 + 235, 522, color=tcolor))
        out.append(fitbox(x0 + 20, 528, 430, 108, verdict, size=13, fill=vfill, stroke=vcolor, sw=1.6))
        b, _, _ = textbox(x0 + 235, 678, tag, size=14, bold=True,
                          fill=BG, stroke=tagcolor, color=tagcolor, sw=2, rx=16)
        out.append(b)
        return out

    p += panel(
        60, "збій: не встигла бітова карта", POS, RED_FILL,
        [("блок даних 5000 — записано", True),
         ("inode: «мій блок 5000» — записано", True),
         ("бітова карта: 5000 вільний — НІ", False)],
        "той самий блок видадуть другому файлу;\nдва власники пишуть в одну комірку\nй псують дані одне одному",
        RED_FILL, POS, "руйнівно", POS)

    p += panel(
        590, "збій: не встиг inode", FIELD, GREEN_FILL,
        [("бітова карта: 5000 зайнятий — записано", True),
         ("блок даних 5000 — записано", True),
         ("inode: розмір і вказівник — НІ", False)],
        "на блок 5000 не вказує ніхто;\nйого вже ніколи не видадуть —\nмісце просто зникло з тому",
        WARM_FILL, WARM, "втрачене місце", FIELD)

    render(os.path.join(IMG, 'split-write.svg'), W, H, *p,
           title="Три записи однієї операції — і те, що лишає збій")


# ── 2. Транзакція в журналі, печатка, відтворення, перенесення ──────────────
def fig_journal_transaction():
    W, H = 1160, 710
    p = []

    # кільце журналу
    p.append(rect(60, 90, 1040, 150, fill=GRAY_FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(70, 82, "журнал — кільце: дійшли до кінця, пишемо спочатку",
                  size=13, color=MUTED, anchor="start"))

    p.append(text(348, 122, "транзакція №41 — запечатана", size=13, bold=True, color=FIELD))
    p.append(text(838, 122, "транзакція №42 — обірвана", size=13, bold=True, color=POS))

    t41 = [(90, "дескриптор\n№41", BLUE_FILL, NEG),
           (222, "копія\nблока", BG, INK),
           (354, "копія\nблока", BG, INK),
           (486, "БЛОК\nФІКСАЦІЇ №41", GREEN_FILL, FIELD)]
    for x0, lab, fl, st in t41:
        p.append(fitbox(x0, 140, 120, 76, lab, size=12, fill=fl, stroke=st, sw=1.8))

    t42 = [(646, "дескриптор\n№42", BLUE_FILL, NEG),
           (778, "копія\nблока", BG, INK)]
    for x0, lab, fl, st in t42:
        p.append(fitbox(x0, 140, 120, 76, lab, size=12, fill=fl, stroke=st, sw=1.8))
    p.append(rect(910, 140, 120, 76, fill=RED_FILL, stroke=POS, sw=1.8, rx=6))
    p.append(mtext(970, 172, ["фіксації", "немає"], size=12, color=POS, bold=True))

    p.append(text(60, 264, "скидання кешу носія — перед блоком фіксації і після нього; без них порядок не гарантований",
                  size=13, color=MUTED, anchor="start"))

    p.append(arrow(348, 282, 348, 312, color=FIELD))
    p.append(arrow(838, 282, 838, 312, color=POS))
    p.append(fitbox(148, 316, 400, 82,
                    "печатка є → відтворити:\nпереписати копії в їхні справжні місця",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(638, 316, 400, 82,
                    "печатки немає → відкинути:\nтом такий, ніби операції не було",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.8))

    p.append(fitbox(160, 438, 700, 84,
                    "перенесення: блоки з журналу переписують у їхні справжні місця —\nі лише після цього займане місце в кільці стає вільним",
                    size=13, fill=WARM_FILL, stroke=WARM, sw=1.8))

    for cx, lab in [(300, "бітова карта"), (570, "таблиця inode"), (840, "блок каталогу")]:
        p.append(arrow(cx, 526, cx, 562, color=WARM))
        p.append(fitbox(cx - 100, 568, 200, 62, lab, size=13, fill=BG, stroke=INK, sw=1.6))

    p.append(text(60, 676, "ціна відновлення залежить від того, скільки роботи було в польоті, а не від розміру тому",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'journal-transaction.svg'), W, H, *p,
           title="Транзакція журналу: опис, печатка, відтворення, перенесення")


# ── 3. Три режими даних ext4 ────────────────────────────────────────────────
def fig_data_modes():
    W, H = 1140, 630
    p = []

    cols = [
        (40, "data=ordered", FIELD, GREEN_FILL,
         "лише метадані",
         "спершу дані на носій,\nаж потім фіксація метаданих",
         "свої дані, старі чи нові;\nчужого старого вмісту\nв ньому не буде ніколи",
         "типовий вибір"),
        (400, "data=journal", NEG, BLUE_FILL,
         "метадані й дані",
         "усе проходить журналом,\nкожен байт пишеться двічі",
         "усе, що потрапило\nв запечатану транзакцію,\nвідновиться цілим",
         "найсуворіший і найповільніший"),
        (760, "data=writeback", POS, RED_FILL,
         "лише метадані",
         "порядку між даними\nй метаданими немає взагалі",
         "розмір правильний,\nа всередині старе сміття\nабо нулі",
         "найшвидший і небезпечний"),
    ]

    for x0, name, color, fill, injournal, order, after, verdict in cols:
        p.append(rect(x0, 80, 340, 470, fill=BG, stroke=color, sw=1.8, rx=10))
        p.append(fitbox(x0, 80, 340, 46, name, size=16, bold=True,
                        fill=fill, stroke=color, sw=1.8, color=color, rx=10))
        p.append(text(x0 + 170, 152, "що йде в журнал", size=12, color=MUTED))
        p.append(fitbox(x0 + 16, 164, 308, 56, injournal, size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.4))
        p.append(text(x0 + 170, 248, "порядок записів", size=12, color=MUTED))
        p.append(fitbox(x0 + 16, 260, 308, 76, order, size=13, fill=BG, stroke=INK, sw=1.4))
        p.append(text(x0 + 170, 364, "у файлі після збою", size=12, color=MUTED))
        p.append(fitbox(x0 + 16, 376, 308, 96, after, size=13, fill=fill, stroke=color, sw=1.6))
        b, _, _ = textbox(x0 + 170, 515, verdict, size=13, bold=True,
                          fill=BG, stroke=color, color=color, sw=2, rx=16)
        p.append(b)

    p.append(text(40, 596, "у всіх трьох режимах журнал відповідає лише за несуперечливість структури — "
                           "чи пережили збій ваші байти, вирішує fsync",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'data-modes.svg'), W, H, *p,
           title="Три режими даних ext4: що журналюється і що видно після збою")


# ── 4. Хроніка: три різні відповіді на ту саму задачу ──────────────────────
def fig_history_timeline():
    W, H = 1220, 870

    COLS = {
        'A': (150, 300, MUTED, GRAY_FILL, "повна перевірка\nпісля збою"),
        'B': (480, 300, NEG, BLUE_FILL, "упорядкування\nзаписів"),
        'C': (810, 350, FIELD, GREEN_FILL, "журнал"),
    }
    ROWS = [
        ("1980", [('A', "fsck на стрічці-доповненні до V7\n(Тед Ковальський, Bell Labs)")]),
        ("1984", [('A', "FFS: синхронні записи метаданих\nу безпечному порядку")]),
        ("1990", [('C', "JFS в AIX 3.1 (IBM, лютий)\nжурнал уже в першому випуску")]),
        ("1991", [('C', "VxFS (Veritas): заявка\nна «першу комерційну журнальовану»")]),
        ("1992", [('C', "Sprite LFS: Остергаут і Розенблюм\n— увесь том як один журнал")]),
        ("1994", [('B', "Soft updates: Ґанґер і Патт,\nOSDI — порядок замість журналу"),
                  ('C', "XFS в IRIX 5.3 (SGI)")]),
        ("1998", [('C', "Твіді: «Journaling the Linux\next2fs Filesystem», LinuxExpo")]),
        ("1999", [('B', "Мак-Кусік і Ґанґер, USENIX ATC:\nsoft updates у FFS")]),
        ("2001", [('C', "reiserfs → ядро 2.4.1 (січень)\next3 → ядро 2.4.15 (листопад)")]),
        ("2010", [('B', "журнальовані soft-updates\n(Мак-Кусік і Роберсон)")]),
    ]

    p = []
    p.append(text(40, 46, "Одна задача — три різні відповіді, і всі вони зростали паралельно",
                  size=17, anchor="start", bold=True))

    # заголовки колонок
    for key, (x, w, color, fill, name) in COLS.items():
        p.append(fitbox(x, 70, w, 56, name, size=14, bold=True,
                        fill=fill, stroke=color, sw=1.8, color=color, rx=10))

    SPINE = 122
    y0, step, bh = 160, 68, 52
    p.append(line(SPINE, y0 - 8, SPINE, y0 + (len(ROWS) - 1) * step + bh + 8,
                  color=MUTED, sw=1.6))

    for i, (year, events) in enumerate(ROWS):
        y = y0 + i * step
        cy = y + bh / 2
        p.append(text(96, cy + 5, year, size=15, anchor="end", bold=True, color=MUTED))
        p.append(circle(SPINE, cy, 5, fill=BG, stroke=MUTED, sw=2))

        prev_right = SPINE + 6
        for key, s in events:
            x, w, color, fill, _ = COLS[key]
            p.append(line(prev_right, cy, x - 2, cy, color=MUTED, sw=1.2, dash="4 4"))
            p.append(fitbox(x, y, w, bh, s, size=13,
                            fill=fill, stroke=color, sw=1.6, color=INK))
            prev_right = x + w + 2

    p.append(text(40, 848, "жодна з трьох гілок не витіснила решти: журнал став типовим у Linux, "
                           "упорядкування лишилося в BSD, копіювання при записі виросло в окрему родину",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *p,
           title="Хроніка переходу від повної перевірки до журналу")


# ── 5. Важелі за шарами: де сидить кожен вимикач ────────────────────────────
def fig_journal_levers():
    W, H = 1210, 860

    ROWS = [
        ("Програма",
         "fsync() · fdatasync() · fsync(дескриптор каталогу)\nO_SYNC · O_DSYNC · O_DIRECT",
         "нічого з цього немає —\nжурнал цілий,\nа ваш файл порожній"),
        ("Кеш сторінок",
         "delalloc / nodelalloc\nauto_da_alloc",
         "блоки під дані ще не вибрані,\nа метадані вже фіксуються"),
        ("Файлова система",
         "data=ordered | journal | writeback\ncommit=N (типово 5 с) · errors=",
         "writeback: розмір правильний,\nвсередині чужий старий вміст"),
        ("Журнал\nJBD2 / XFS log",
         "ext4:  -J size=  ·  -J device=  ·  journal_ioprio=\njournal_checksum  ·  journal_async_commit\nXFS:  logbufs=  ·  logbsize=  ·  logdev=",
         "малий журнал —\nчастіші зупинки\nна перенесення"),
        ("Блоковий шар",
         "/sys/block/*/queue/write_cache  (читання й запис)\n/sys/block/*/queue/fua  (лише читання)",
         "«write through» руками —\nядро перестає слати\nскидання кешу"),
        ("Носій",
         "hdparm -W 0|1  (ATA)  ·  sdparm --set=WCE  (SCSI)\nnobarrier — лише за батареї чи конденсаторів",
         "летючий кеш без скидань —\nжурнал не гарантує нічого"),
    ]

    LX, LW = 46, 250
    MX, MW = 316, 560
    RX, RW = 896, 268
    y0, bh, gap = 132, 100, 14

    p = []
    p.append(text(46, 52, "Кожен важіль діє на своєму шарі — а гарантія не сильніша за найнижчий із них",
                  size=17, anchor="start", bold=True))

    p.append(fitbox(LX, y0 - 46, LW, 36, "шар", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))
    p.append(fitbox(MX, y0 - 46, MW, 36, "важелі, що діють саме тут", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))
    p.append(fitbox(RX, y0 - 46, RW, 36, "що зникає, коли зрушити не туди", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))

    for i, (layer, levers, risk) in enumerate(ROWS):
        y = y0 + i * (bh + gap)
        p.append(fitbox(LX, y, LW, bh, layer, size=15, bold=True,
                        fill=BLUE_FILL, stroke=NEG, sw=1.7, color=INK))
        p.append(fitbox(MX, y, MW, bh, levers, size=13,
                        fill=BG, stroke=INK, sw=1.5))
        p.append(fitbox(RX, y, RW, bh, risk, size=12,
                        fill=RED_FILL if i in (0, 4, 5) else WARM_FILL,
                        stroke=POS if i in (0, 4, 5) else WARM, sw=1.5, color=INK))
        if i < len(ROWS) - 1:
            p.append(arrow(LX + LW / 2, y + bh + 1, LX + LW / 2, y + bh + gap - 1, color=MUTED))

    p.append(text(46, y0 + len(ROWS) * (bh + gap) + 26,
                  "Читати знизу вгору: найсуворіший режим даних не додає нічого, "
                  "якщо нижче кеш носія бере записи й забуває їх при знеструмленні.",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'journal-levers.svg'), W, H, *p,
           title="Важелі керування журналом за шарами")


# ── Формат запису власного журналу й три місця обриву ──────────────────────
def fig_record_layout():
    W, H = 1240, 700
    p = []

    p.append(text(60, 56, "Один запис журналу: усе, що потрібно, щоб відтворення могло винести вирок",
                  size=16, anchor="start", bold=True))

    ROW_Y, ROW_H = 150, 66
    fields = [
        ("MAGIC\n4 Б", 110, BLUE_FILL),
        ("len\n4 Б", 100, BLUE_FILL),
        ("seq\n8 Б", 130, BLUE_FILL),
        ("op\n1 Б", 70, GREEN_FILL),
        ("klen\n4 Б", 100, GREEN_FILL),
        ("ключ", 170, GREEN_FILL),
        ("значення", 220, GREEN_FILL),
        ("CRC-32\n4 Б", 100, WARM_FILL),
        ("SEAL\n4 Б", 100, WARM_FILL),
    ]
    x = 60
    for label, w, fill in fields:
        p.append(fitbox(x, ROW_Y, w, ROW_H, label, size=13, fill=fill, stroke=INK, sw=1.4))
        x += w
    END = x

    for gx, gw, label, color in [(60, 340, "ЗАГОЛОВОК — 16 Б", NEG),
                                 (400, 560, "ТІЛО — len Б", FIELD),
                                 (960, 200, "ХВІСТ — печатка", WARM)]:
        p.append(line(gx, ROW_Y - 22, gx + gw, ROW_Y - 22, color=color, sw=2))
        p.append(line(gx, ROW_Y - 22, gx, ROW_Y - 12, color=color, sw=2))
        p.append(line(gx + gw, ROW_Y - 22, gx + gw, ROW_Y - 12, color=color, sw=2))
        p.append(text(gx + gw / 2, ROW_Y - 32, label, size=13, bold=True, color=color))

    for cx, num in [(700, "1"), (1060, "2"), (END, "3")]:
        p.append(line(cx, ROW_Y - 6, cx, ROW_Y + ROW_H + 46, color=POS, sw=2, dash="6 5"))
        p.append(circle(cx, ROW_Y + ROW_H + 68, 15, fill=RED_FILL, stroke=POS, sw=2))
        p.append(text(cx, ROW_Y + ROW_H + 73, num, size=14, bold=True, color=POS))

    verdicts = [
        ("1", "обрив усередині тіла: прочитано менше байтів, ніж обіцяє len → хвіст відкидаємо"),
        ("2", "тіло ціле, печатки немає: запис не завершено → хвіст відкидаємо"),
        ("3", "печатка на місці й CRC сходиться: запис приймаємо й застосовуємо"),
    ]
    for i, (num, s) in enumerate(verdicts):
        yy = 344 + i * 34
        p.append(circle(76, yy - 5, 13, fill=RED_FILL, stroke=POS, sw=1.8))
        p.append(text(76, yy, num, size=13, bold=True, color=POS))
        p.append(text(104, yy, s, size=14, anchor="start"))

    p.append(text(60, 462, "носій вільний класти байти не в тому порядку, у якому їх подали: "
                           "тоді печатка вже є, а CRC не сходиться — вирок той самий",
                  size=13, color=MUTED, anchor="start"))

    p.append(text(60, 512, "Журнал цілком: відтворення йде від початку "
                           "й спиняється на першому записі, що не пройшов перевірку",
                  size=15, anchor="start", bold=True))

    LY, LH = 544, 62
    for rx, rw, label in [(60, 250, "запис 1\nseq 1"), (310, 250, "запис 2\nseq 2"),
                          (560, 250, "запис 3\nseq 3")]:
        p.append(fitbox(rx, LY, rw, LH, label, size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(fitbox(810, LY, 350, LH, "огризок seq 4 — без печатки", size=13,
                    fill=RED_FILL, stroke=POS, sw=1.6))

    p.append(line(810, LY - 14, 810, LY + LH + 14, color=POS, sw=2, dash="6 5"))
    p.append(text(60, LY + LH + 36, "ftruncate до кінця останнього справного запису — "
                                    "далі журнал росте від цієї межі",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(IMG, 'record-layout.svg'), W, H, *p,
           title="Формат запису власного журналу й місця обриву")


if __name__ == '__main__':
    fig_record_layout()
    fig_split_write()
    fig_journal_transaction()
    fig_data_modes()
    fig_history_timeline()
    fig_journal_levers()
    print("ok")
