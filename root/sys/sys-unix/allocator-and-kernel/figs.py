# -*- coding: utf-8 -*-
"""Фігури до теми «Звідки алокатор бере пам'ять: brk і mmap»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_two_levels():
    """Два ринки: програма ↔ алокатор (байти) і алокатор ↔ ядро (сторінки)."""
    W, H = 1060, 400
    f = []

    ax, aw = 40, 220
    bx, bw = 390, 290
    cx, cw = 810, 210
    by, bh = 100, 120

    # лічильники над стрілками
    f.append(text((ax + aw + bx) / 2, 72, "1 000 000 разів", size=14, bold=True, color=POS))
    f.append(text((bx + bw + cx) / 2, 72, "десяток разів", size=14, bold=True, color=FIELD))

    f.append(fitbox(ax, by, aw, bh, "Програма\n\nmalloc(32)\nfree(p)", size=14))
    f.append(fitbox(bx, by - 12, bw, bh + 24,
                    "Алокатор\nкод libc усередині процесу\n\nсписки вільних блоків,\nрозділення й злиття", size=14))
    f.append(fitbox(cx, by, cw, bh, "Ядро\n\nсписок VMA,\nсторінки по 4 КіБ", size=14))

    f.append(arrow(ax + aw + 8, by + bh / 2, bx - 10, by + bh / 2))
    f.append(arrow(bx + bw + 8, by + bh / 2, cx - 10, by + bh / 2))

    # підписи під стрілками
    f.append(mtext((ax + aw + bx) / 2, 268,
                   ["виклик функції", "десятки наносекунд", "будь-який розмір"],
                   size=13, color=MUTED))
    f.append(mtext((bx + bw + cx) / 2, 268,
                   ["системний виклик", "сотні наносекунд", "лише цілими сторінками"],
                   size=13, color=MUTED))

    f.append(text(W / 2, 356, "ядро торгує адресами — алокатор торгує байтами", size=15, bold=True))

    render(os.path.join(IMG, 'two-levels.svg'), W, H, *f)


def fig_brk_vs_mmap():
    """Одна межа проти багатьох незалежних ділянок."""
    W, H = 1140, 560
    f = []

    f.append(text(160, 66, "Купа — одна ділянка, одна межа", size=15, bold=True))
    f.append(text(760, 66, "Відображення — багато незалежних ділянок", size=15, bold=True))
    f.append(line(560, 50, 560, 500, color=MUTED, sw=1, dash="6 6"))

    # ── ліворуч: смуга купи (згори — високі адреси) ──
    lx, lw = 60, 170
    rows = [
        (100, 148, "вільно", "#eef7f0"),
        (148, 205, "зайнято", FILL),
        (205, 258, "вільно", "#eef7f0"),
        (258, 320, "зайнято", FILL),
        (320, 365, "вільно", "#eef7f0"),
        (365, 440, "зайнято", FILL),
    ]
    for y0, y1, label, fill in rows:
        f.append(fitbox(lx, y0, lw, y1 - y0, label, size=13, fill=fill))

    # межа купи
    f.append(line(lx - 18, 100, lx + lw + 14, 100, color=POS, sw=2.5))
    f.append(text(lx - 24, 96, "брейк", size=13, color=POS, anchor="end", bold=True))
    f.append(arrow(lx + lw + 34, 100, lx + lw + 34, 66, color=POS))
    f.append(arrow(lx + lw + 34, 116, lx + lw + 34, 150, color=POS))

    f.append(mtext(lx + lw + 58, 88,
                   ["brk рухає тільки цю", "межу — вгору легко,", "вниз лише коли хвіст", "вільний"],
                   size=12.5, color=MUTED, anchor="start"))
    f.append(arrow(lx + lw + 68, 232, lx + lw + 16, 232, color=NEG))
    f.append(mtext(lx + lw + 76, 218,
                   ["ця дірка ядру не", "повертається: нижче", "за брейк не опустиш"],
                   size=12.5, color=NEG, anchor="start"))

    # ── праворуч: незалежні відображення ──
    rx, rw = 620, 230
    f.append(fitbox(rx, 100, rw, 74, "mmap 1 МіБ\nжива ділянка", size=13))
    f.append(fitbox(rx, 214, rw, 74, "mmap 4 МіБ\nmunmap → віддано", size=13,
                    fill="#fdecea", stroke=POS))
    f.append(fitbox(rx, 328, rw, 74, "mmap 512 КіБ\nжива ділянка", size=13))
    f.append(text(rx + rw / 2, 196, "вільні адреси", size=12, color=MUTED))
    f.append(text(rx + rw / 2, 310, "вільні адреси", size=12, color=MUTED))

    f.append(arrow(rx + rw + 76, 251, rx + rw + 14, 251, color=POS))
    f.append(mtext(rx + rw + 84, 230,
                   ["кожна ділянка", "звільняється сама,", "не питаючи сусідів"],
                   size=12.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, 528,
                  "Межа одна — тому купа віддається лише з хвоста; ділянок багато — тому кожна віддається окремо",
                  size=14, bold=True))

    render(os.path.join(IMG, 'brk-vs-mmap.svg'), W, H, *f)


def fig_trapped_heap():
    """Один живий блок під брейком тримає всю купу за процесом."""
    W, H = 1000, 470
    f = []

    aw = 190
    ax, bx = 110, 640

    f.append(text(ax + aw / 2, 76, "після 511 999 free()", size=15, bold=True))
    f.append(text(bx + aw / 2, 76, "після останнього free()", size=15, bold=True))

    # стан A
    f.append(fitbox(ax, 100, aw, 46, "живий блок\n1 КіБ", size=12.5, fill="#fdecea", stroke=POS))
    f.append(fitbox(ax, 146, aw, 234, "вільно\n≈ 500 МіБ", size=14, fill="#eef7f0"))
    f.append(line(ax - 16, 100, ax + aw + 12, 100, color=POS, sw=2.5))
    f.append(text(ax - 22, 96, "брейк", size=13, color=POS, anchor="end", bold=True))
    f.append(text(ax + aw / 2, 412, "RSS ≈ 500 МіБ", size=14, bold=True))
    f.append(text(ax + aw / 2, 438, "вільний хвіст = 0", size=12.5, color=MUTED))

    # стан B
    f.append(fitbox(bx, 340, aw, 40, "купа порожня", size=12.5, fill="#eef7f0"))
    f.append(line(bx - 16, 340, bx + aw + 12, 340, color=FIELD, sw=2.5))
    f.append(text(bx - 22, 336, "брейк", size=13, color=FIELD, anchor="end", bold=True))
    f.append(text(bx + aw / 2, 412, "RSS ≈ 0", size=14, bold=True))
    f.append(text(bx + aw / 2, 438, "хвіст 500 МіБ > 128 КіБ → обрізано", size=12.5, color=MUTED))

    # перехід
    f.append(arrow(ax + aw + 60, 240, bx - 60, 240))
    f.append(mtext((ax + aw + bx) / 2, 196,
                   ["free() того одного блоку", "робить вільним увесь хвіст —", "і аж тоді brk іде вниз"],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'trapped-heap.svg'), W, H, *f)


def fig_arenas():
    """Головна арена росте через brk, арени потоків живуть у mmap-ділянках."""
    W, H = 1020, 480
    f = []

    tw, th, ty = 160, 52, 92
    txs = [50, 270, 490, 710]
    for i, x in enumerate(txs):
        f.append(fitbox(x, ty, tw, th, "потік %d" % (i + 1), size=14))

    aw, ah, ay = 240, 96, 276
    axs = [40, 380, 720]
    f.append(fitbox(axs[0], ay, aw, ah, "головна арена\n[heap]\nросте через brk", size=13.5))
    f.append(fitbox(axs[1], ay, aw, ah, "арена потоку\nmmap-ділянка\n64 МіБ", size=13.5))
    f.append(fitbox(axs[2], ay, aw, ah, "арена потоку\nmmap-ділянка\n64 МіБ", size=13.5))

    pairs = [(0, 0), (1, 1), (2, 2), (3, 2)]
    for ti, ai in pairs:
        f.append(arrow(txs[ti] + tw / 2, ty + th + 6, axs[ai] + aw / 2, ay - 8, color=MUTED))

    f.append(mtext(W / 2, 424,
                   ["Арен не більше ніж 8 × ядер (на 64 бітах); коли ліміт вичерпано, потоки починають ділити арену.",
                    "Додаткова арена не може рости через brk — брейк у процесі один, тому вона живе в mmap-ділянці."],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'arenas.svg'), W, H, *f)


def fig_three_layers():
    """Три шари, з яких склалося сьогоднішнє «brk або mmap»."""
    W, H = 1240, 560
    f = []

    f.append(text(W / 2, 40, "Три шари, що склалися незалежно один від одного", size=16, bold=True))

    lx, lw = 34, 208          # колонка підписів
    cx0, cw, gap = 260, 306, 16
    ry0, rh, rgap = 74, 130, 26

    rows = [
        ("Межа даних\nу ядрі", [
            "1971 · break\n1-ша редакція Unix\nмежа для свопера:\nвище неї нічого не зберігати",
            "1973 · brk / sbrk\nмежа даних процесу;\nпомилка, якщо треба більше\nніж 8 сегментних регістрів",
            "SUSv2 · LEGACY\nприбрано з POSIX.1-2001,\nале в Linux лишається\nназавжди",
        ]),
        ("Відображення\nу простір адрес", [
            "1983 · 4.2BSD\nmmap описано в System Manual,\nале «реалізовано лише\nsbrk і getpagesize»",
            "1988 · SunOS 4.0\nперша широка реалізація;\nу BSD цей код\nне перейшов",
            "1990 · 4.3BSD-Reno\nсвоя реалізація на віртуальній\nпам'яті Mach; звідти —\nу вільні Unix і Linux",
        ]),
        ("Алокатор\nу бібліотеці C", [
            "1987 · dlmalloc\nДаґ Лі пише алокатор\nдля власних програм на C++\nі для libg++",
            "1990-ті · ptmalloc\nВольфрам Ґлоґер додає\nарени й замки,\nщоб потоки не шикувалися",
            "2002 · ptmalloc2\nпереписано з dlmalloc 2.7.0;\nтого ж року входить\nу glibc 2.3",
        ]),
    ]

    for i, (label, cells) in enumerate(rows):
        ry = ry0 + i * (rh + rgap)
        f.append(fitbox(lx, ry, lw, rh, label, size=14.5, fill=BG, stroke=MUTED))
        for j, cell in enumerate(cells):
            f.append(fitbox(cx0 + j * (cw + gap), ry, cw, rh, cell, size=12.5))

    f.append(text(W / 2, H - 22,
                  "brk народився як межа для свопера, mmap — як спосіб покласти файл у простір адрес, "
                  "алокатор — як приватна оптимізація однієї людини",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'three-layers.svg'), W, H, *f)


def fig_threshold_lever():
    """Поріг mmap: де він стоїть, куди сам їде і що його зупиняє."""
    W, H = 1180, 470
    f = []

    f.append(text(W / 2, 44, "Поріг mmap — єдине число, яке алокатор веде сам", size=16, bold=True))

    ay = 232
    x0, x1 = 110, 1010
    xdef, xmax = 300, 860

    # вісь розмірів запиту
    f.append(arrow(x0, ay, x1 + 30, ay, sw=2))
    f.append(text(x1 + 46, ay + 5, "розмір", size=13, color=MUTED, anchor="start"))

    for x, lab in ((x0, "0"), (xdef, "128 КіБ"), (xmax, "32 МіБ")):
        f.append(line(x, ay - 8, x, ay + 8, sw=2))
        f.append(text(x, ay + 30, lab, size=13, color=MUTED))

    f.append(text(xdef, ay + 52, "умовчання порогу", size=12.5, color=NEG))
    f.append(text(xmax, ay + 52, "стеля підняття", size=12.5, color=NEG))

    # маркер порогу і його рух
    f.append(fitbox(xdef - 66, ay - 76, 132, 40, "поріг", size=14, fill="#eaf0fd", stroke=NEG))
    f.append(arrow(xdef + 72, ay - 56, xmax - 12, ay - 56, color=POS, sw=2))
    f.append(mtext((xdef + xmax) / 2 + 30, ay - 104,
                   ["щоразу, коли звільнено блок, виданий через mmap,",
                    "поріг стає рівним розмірові цього блоку"],
                   size=13, color=POS))

    # два боки осі
    f.append(fitbox(x0, ay + 82, 340, 62,
                    "менше за поріг\nз купи, brk рухає межу", size=13.5))
    f.append(fitbox(x0 + 400, ay + 82, 480, 62,
                    "не менше за поріг\nокремий mmap, а на free() — munmap", size=13.5))

    # що вимикає механізм
    f.append(mtext(W / 2, H - 58,
                   ["Явно задати mmap_threshold, trim_threshold, top_pad або mmap_max —",
                    "хоч mallopt, хоч змінною середовища, хоч тюнаблом — і підняття вимикається назавжди:",
                    "поріг застигає там, де його поставили."],
                   size=13.5, color=MUTED))

    render(os.path.join(IMG, 'threshold-lever.svg'), W, H, *f)


def fig_probe_timeline():
    """Вставка proj-heap-probe: VmSize і VmRSS у чотири моменти досліду 4."""
    W, H = 1060, 500
    f = []

    base = 400.0
    top_max = 250.0
    peak = 528040.0
    scale = top_max / peak

    c_size_fill, c_size_line = "#dfe6ef", MUTED
    c_rss_fill, c_rss_line = "#f6d0cb", POS

    groups = [
        (528040, 525812, ["виділено", "512000 × 1 КіБ"]),
        (528040, 525812, ["free() усіх,", "крім верхнього"]),
        (527916, 5812, ["malloc_trim(0)"]),
        (8044, 5808, ["free()", "верхнього"]),
    ]

    def fmt(v):
        s = str(v)
        return s[:-3] + " " + s[-3:] if len(s) > 3 else s

    # легенда
    f.append(rect(300, 48, 20, 16, fill=c_size_fill, stroke=c_size_line, sw=1.5, rx=3))
    f.append(text(332, 61, "VmSize — скільки адрес записано за процесом",
                  size=13, anchor="start", color=INK))
    f.append(rect(300, 76, 20, 16, fill=c_rss_fill, stroke=c_rss_line, sw=1.5, rx=3))
    f.append(text(332, 89, "VmRSS — скільки сторінок справді лежить у пам'яті",
                  size=13, anchor="start", color=INK))

    x0, gw, gap = 60.0, 220.0, 20.0
    for i, (vs, vr, cap) in enumerate(groups):
        cx = x0 + i * (gw + gap) + gw / 2
        for val, dx, cf, cl in ((vs, -45, c_size_fill, c_size_line),
                                (vr, 45, c_rss_fill, c_rss_line)):
            h = max(5.0, val * scale)
            bx = cx + dx - 35
            f.append(rect(bx, base - h, 70, h, fill=cf, stroke=cl, sw=1.5, rx=3))
            f.append(text(cx + dx, base - h - 11, fmt(val), size=13, color=cl, bold=True))
        f.append(mtext(cx, base + 28, cap, size=13, color=INK))

    f.append(line(40, base, 1020, base, color=INK, sw=2))

    f.append(text(W / 2, H - 22,
                  "malloc_trim віддає сторінки, але адреси лишаються за процесом; "
                  "брейк опускається лише після звільнення верхнього блоку",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'probe-timeline.svg'), W, H, *f,
           title="Один процес, чотири моменти досліду (КіБ)")


if __name__ == '__main__':
    fig_probe_timeline()
    fig_three_layers()
    fig_threshold_lever()
    fig_two_levels()
    fig_brk_vs_mmap()
    fig_trapped_heap()
    fig_arenas()
    print('ok')
