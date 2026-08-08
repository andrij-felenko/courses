# -*- coding: utf-8 -*-
"""Фігури до теми «Огляд засобів взаємодії: що коли обирати»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_three_axes():
    """Три незалежні питання; кожен спосіб взаємодії — одна відповідь у кожній колонці."""
    W, H = 1120, 640
    g = []

    COLX = [230, 530, 830]
    CW = 260
    TOP = 60
    HEADS = ["Як знайти одне одного", "Як перенести байти", "Як дізнатися про нове"]
    OPTS = [
        ["успадкування дескриптора\nканал, socketpair",
         "ім'я у файловій системі\nFIFO, сокет, /dev/shm",
         "окремий простір імен\nключ SysV, /черга",
         "передача дескриптора\nSCM_RIGHTS"],
        ["дві копії через ядро\nканал, сокет, черга",
         "одна копія\nsplice, process_vm_readv",
         "нуль копій\nспільні сторінки"],
        ["готовність дескриптора\npoll, epoll",
         "сигнал",
         "futex або eventfd",
         "опитування в циклі"],
    ]

    for i, x in enumerate(COLX):
        g.append(text(x + CW / 2, TOP - 16, HEADS[i], size=14, bold=True))
        y = TOP
        for o in OPTS[i]:
            g.append(fitbox(x, y, CW, 62, o, size=12))
            y += 76

    NOTE_Y = TOP + 4 * 76 + 26
    g.append(text(COLX[0] + (3 * CW + 2 * 40) / 2, NOTE_Y,
                  "спосіб взаємодії = одна відповідь із кожної колонки",
                  size=13, color=MUTED))

    ROWS = [
        ("канал", ["успадкування", "дві копії", "готовність дескриптора"]),
        ("спільна пам'ять", ["ім'я у /dev/shm", "нуль копій", "futex"]),
    ]
    ry = NOTE_Y + 28
    for name, cells in ROWS:
        g.append(text(COLX[0] - 30, ry + 34, name, size=13, bold=True, anchor="end"))
        for i, c in enumerate(cells):
            g.append(fitbox(COLX[i], ry, CW, 52, c, size=12,
                            fill="#eef6ef", stroke=FIELD))
        ry += 70

    return render(os.path.join(IMG, 'three-axes.svg'), W, H, *g)


def fig_copies():
    """Дві копії через буфер ядра проти спільних сторінок без копій."""
    W, H = 1060, 470
    g = []

    g.append(text(60, 40, "через об'єкт ядра: канал, сокет, черга повідомлень",
                  size=14, bold=True, anchor="start"))

    g.append(fitbox(60, 66, 230, 64, "процес A\nсвій буфер", size=13))
    g.append(fitbox(415, 66, 230, 64, "буфер у ядрі", size=13, fill="#eef2f7"))
    g.append(fitbox(770, 66, 230, 64, "процес B\nсвій буфер", size=13))

    g.append(arrow(292, 98, 413, 98, color=POS))
    g.append(text(352, 56, "копія 1", size=12, color=POS))
    g.append(text(352, 152, "write()", size=12, color=MUTED))

    g.append(arrow(647, 98, 768, 98, color=POS))
    g.append(text(707, 56, "копія 2", size=12, color=POS))
    g.append(text(707, 152, "read()", size=12, color=MUTED))

    g.append(text(60, 190, "межу перетинають двічі: два системні виклики й два проходи по пам'яті",
                  size=12, color=MUTED, anchor="start"))

    g.append(line(40, 218, 1020, 218, color=MUTED, sw=1, dash="5,5"))

    g.append(text(60, 258, "через спільні сторінки: спільна пам'ять і окреме сповіщення",
                  size=14, bold=True, anchor="start"))

    g.append(fitbox(60, 284, 230, 64, "процес A\nвідображення", size=13))
    g.append(fitbox(415, 284, 230, 64, "ті самі фізичні\nсторінки", size=13, fill="#eef6ef"))
    g.append(fitbox(770, 284, 230, 64, "процес B\nвідображення", size=13))

    g.append(line(292, 316, 413, 316, color=FIELD, sw=1.6, dash="6,4"))
    g.append(line(647, 316, 768, 316, color=FIELD, sw=1.6, dash="6,4"))
    g.append(text(352, 274, "mmap", size=12, color=FIELD))
    g.append(text(707, 274, "mmap", size=12, color=FIELD))

    g.append(line(175, 350, 175, 396, color=NEG, sw=1.4))
    g.append(line(175, 396, 885, 396, color=NEG, sw=1.4))
    g.append(arrow(885, 396, 885, 352, color=NEG, sw=1.4))
    g.append(text(530, 424, "futex або eventfd: сповіщення на кілька байтів, дані нікуди не рухаються",
                  size=12, color=NEG))

    return render(os.path.join(IMG, 'copies.svg'), W, H, *g)


def fig_lifetime():
    """Хто прибирає за собою: три різні відповіді про час життя об'єкта."""
    W, H = 1080, 430
    g = []

    X0, X1, XE = 330, 700, 1000
    ROWS = [
        ("канал, socketpair", 90,
         "зникає разом з останнім закритим дескриптором", None),
        ("FIFO, сокет із іменем", 210,
         "об'єкт зникає, ім'я у каталозі лишається", "порожній файл чекає на rm"),
        ("сегмент SysV, /dev/shm, черга", 330,
         "живе далі без жодного процесу", "доки не викличуть unlink або не перезавантажать"),
    ]

    for name, y, note, tail in ROWS:
        g.append(text(X0 - 24, y + 6, name, size=13, bold=True, anchor="end"))
        g.append(rect(X0, y - 16, X1 - X0, 34, fill="#eef2f7", stroke=LINE, sw=1.2))
        g.append(text((X0 + X1) / 2, y + 6, "процеси працюють", size=12))
        if tail:
            g.append(line(X1, y, XE, y, color=MUTED, sw=1.4, dash="6,4"))
            g.append(text((X1 + XE) / 2, y - 26, tail, size=11, color=MUTED))
        g.append(line(X1, y - 24, X1, y + 26, color=POS, sw=2))
        g.append(text(X0, y + 42, note, size=12, color=MUTED, anchor="start"))

    g.append(text(X1, 400, "остання сторона пішла", size=12, color=POS))

    return render(os.path.join(IMG, 'lifetime.svg'), W, H, *g)


def fig_bench_budget():
    """З чого складається оберт: пробудження, копії в ядрі, дотик до даних."""
    W, H = 1150, 580
    g = []

    C_WAKE = ("#f0c6c0", POS)
    C_COPY = ("#c3d0f2", NEG)
    C_TOUCH = ("#dfe3e8", MUTED)

    X0 = 345
    BH = 30

    def bars(rows, scale, span):
        for name, segs, total, y in rows:
            g.append(text(X0 - 22, y + 5, name, size=13, anchor="end"))
            x = X0
            for val, (fill, stroke) in segs:
                w = val * scale
                if w <= 0.4:
                    continue
                g.append(rect(x, y - BH / 2, w, BH,
                              fill=fill, stroke=stroke, sw=1.0, rx=2))
                x += w
            g.append(text(x + 14, y + 5, total, size=13, anchor="start"))
        return span

    g.append(text(120, 46, "повідомлення 64 Б: оберт — це майже самі пробудження",
                  size=14, bold=True, anchor="start"))

    S1 = 640.0 / 8.6
    bars([
        ("канал",                         [(6.8, C_WAKE)], "6.8 мкс",  100),
        ("сокет домену Unix, SEQPACKET",  [(8.1, C_WAKE)], "8.1 мкс",  148),
        ("спільна пам'ять + futex",       [(4.3, C_WAKE)], "4.3 мкс",  196),
        ("спільна пам'ять + опитування",  [(0.31, C_WAKE)], "0.31 мкс", 244),
    ], S1, None)

    g.append(line(60, 296, 1090, 296, color=MUTED, sw=1, dash="5,5"))

    g.append(text(120, 340, "повідомлення 1 МіБ: різниця вся в синьому — копіях через ядро",
                  size=14, bold=True, anchor="start"))

    S2 = 660.0 / 402.0
    bars([
        ("канал, ємність 64 КіБ",
         [(115, C_WAKE), (177, C_COPY), (110, C_TOUCH)], "402 мкс", 394),
        ("канал, ємність 1 МіБ",
         [(4, C_WAKE), (177, C_COPY), (110, C_TOUCH)],   "291 мкс", 442),
        ("спільна пам'ять + futex",
         [(4, C_WAKE), (0, C_COPY), (110, C_TOUCH)],     "114 мкс", 490),
    ], S2, None)

    LEG = [("пробудження й системні виклики", C_WAKE),
           ("копії через буфер ядра", C_COPY),
           ("дотик до даних обома сторонами", C_TOUCH)]
    lx = 120
    for label, (fill, stroke) in LEG:
        g.append(rect(lx, 540, 22, 14, fill=fill, stroke=stroke, sw=1.0, rx=2))
        g.append(text(lx + 32, 552, label, size=12, color=MUTED, anchor="start"))
        lx += 44 + text_width(label, 12)

    return render(os.path.join(IMG, 'bench-budget.svg'), W, H, *g)


if __name__ == '__main__':
    print(fig_three_axes())
    print(fig_copies())
    print(fig_lifetime())
    print(fig_bench_budget())
