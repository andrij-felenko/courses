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
GREY_FILL = "#eef0f3"
WARM = "#b8860b"


def box(x, y, w, h, lines, fill=FILL, stroke=LINE, size=14, bold=False, sw=1.6):
    """Рамка заданого розміру з багаторядковим текстом усередині."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)]
    if isinstance(lines, str):
        lines = lines.split("\n")
    cy = y + h / 2 - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
    out.append(mtext(x + w / 2, cy, lines, size=size, bold=bold))
    return out


# ── 1. Дві гілки під спільним read ─────────────────────────────────────────
def fig_two_branches():
    W, H = 1240, 760
    p = []

    # спільна вершина
    p += box(440, 30, 360, 54, "read(fd, buf, n)", size=17, bold=True, fill=GREY_FILL)
    p += box(440, 120, 360, 54, "VFS: викликати read цієї ФС",
             size=15, fill=GREY_FILL)
    p.append(arrow(620, 84, 620, 118))

    cols = [
        (30, NEG, BLUE_FILL, "ext4, XFS", [
            ("зсув → номери блоків", None),
            ("кеш сторінок", None),
            ("блоковий пристрій", "hard"),
        ], "дані лежать на носії"),
        (450, POS, RED_FILL, "procfs, sysfs", [
            ("викликати функцію ядра", None),
            ("сформатувати текст\nіз живих структур", None),
            ("не зберігається нічого", "hard"),
        ], "вміст народжується\nу мить читання"),
        (870, FIELD, GREEN_FILL, "tmpfs, devtmpfs", [
            ("узяти готові сторінки", None),
            ("кеш сторінок\nбез пристрою під ним", None),
            ("своп — єдиний вихід", "hard"),
        ], "дані справжні,\nносієм є пам'ять"),
    ]

    CW = 340
    for cx0, color, fill, title, steps, foot in cols:
        p += box(cx0, 210, CW, 46, title, size=16, bold=True, fill=fill, stroke=color)
        # від VFS до заголовка колонки
        p.append(arrow(620, 176, cx0 + CW / 2, 206))
        y = 290
        for i, (txt, kind) in enumerate(steps):
            lines = txt.split("\n")
            h = 40 + (len(lines) - 1) * 20
            st = color if kind == "hard" else LINE
            fl = fill if kind == "hard" else FILL
            p += box(cx0 + 20, y, CW - 40, h, lines, size=13,
                     fill=fl, stroke=st, bold=(kind == "hard"))
            if i < len(steps) - 1:
                p.append(arrow(cx0 + CW / 2, y + h, cx0 + CW / 2, y + h + 34))
            y += h + 34
        p += box(cx0 + 20, 600, CW - 40, 66, foot.split("\n"), size=13,
                 fill="#ffffff", stroke=MUTED, sw=1.1)

    p.append(text(620, 720, "Контракт read однаковий; різне тільки те, звідки беруться байти",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'two-branches.svg'), W, H, *p)


# ── 2. Розірване читання довгого файлу з procfs ────────────────────────────
def fig_torn_read():
    W, H = 1240, 700
    p = []

    axis_y = 200
    p.append(line(60, axis_y, 1180, axis_y, color=MUTED, sw=1.4))
    p.append(text(60, axis_y + 34, "час →", size=13, color=MUTED, anchor="start"))

    reads = [
        (120, "read №1", "ділянки A, B, C"),
        (500, "read №2", "ділянки D, F"),
        (880, "read №3", "кінець файлу"),
    ]
    for x, title, got in reads:
        p += box(x, axis_y - 118, 250, 92, [title, got], size=14, bold=False,
                 fill=BLUE_FILL, stroke=NEG)
        p.append(arrow(x + 125, axis_y - 24, x + 125, axis_y - 6))
        p.append(circle(x + 125, axis_y, 6, fill=NEG, stroke=NEG))

    events = [
        (415, "процес зробив munmap(B)"),
        (795, "процес зробив mmap(E)"),
    ]
    for x, txt in events:
        p.append(circle(x, axis_y, 7, fill=RED_FILL, stroke=POS, sw=2))
        p.append(line(x, axis_y + 8, x, axis_y + 52, color=POS, sw=1.4, dash="4,4"))
        p += box(x - 150, axis_y + 52, 300, 44, txt, size=13,
                 fill=RED_FILL, stroke=POS)

    p += box(180, 400, 420, 150, [
        "зібраний читачем текст",
        "",
        "A   B   C   D   F",
    ], size=15, fill=GREY_FILL, sw=1.8)

    p += box(680, 400, 460, 150, [
        "B тут є, хоч ділянки вже немає",
        "E тут немає, хоч ділянка вже є",
    ], size=14, fill=WARM_FILL, stroke=WARM, sw=1.8)
    p.append(arrow(604, 475, 676, 475))

    p.append(text(620, 620, "кожен рядок був правдою у свою мить; неправдою є їхня сукупність",
                  size=15, color=MUTED, italic=True))

    render(os.path.join(IMG, 'torn-read.svg'), W, H, *p)


# ── 3. devtmpfs і udev над одним вузлом ────────────────────────────────────
def fig_devtmpfs_udev():
    W, H = 1240, 700
    p = []

    split = 330
    p.append(line(40, split, 1200, split, color=MUTED, sw=1.6, dash="8,6"))
    p.append(text(50, split - 14, "ядро", size=15, color=MUTED,
                  anchor="start", bold=True))
    p.append(text(50, split + 28, "простір користувача", size=15, color=MUTED,
                  anchor="start", bold=True))

    k_steps = [
        (60, ["драйвер реєструє", "пристрій"]),
        (390, ["devtmpfs одразу створює", "вузол /dev/sda", "root:root  0600"]),
        (740, ["ядро надсилає", "подію про появу"]),
    ]
    for i, (x, lines) in enumerate(k_steps):
        h = 40 + len(lines) * 24
        p += box(x, 60, 300, h, lines, size=14, fill=BLUE_FILL, stroke=NEG)
        if i < len(k_steps) - 1:
            p.append(arrow(x + 300, 60 + h / 2, x + 355, 60 + h / 2))

    p += box(740, 400, 300, 88, ["udev звіряє подію", "з правилами"],
             size=14, fill=GREEN_FILL, stroke=FIELD)
    p.append(arrow(890, 152, 890, 396))

    acts = [
        (60, ["група → disk"]),
        (300, ["права → 0660"]),
        (540, ["посилання", "/dev/disk/by-id/…"]),
    ]
    for x, lines in acts:
        h = 40 + len(lines) * 24
        p += box(x, 400, 220, h, lines, size=13, fill=GREEN_FILL, stroke=FIELD)
        p.append(arrow(730, 444, x + 230, 444))

    p += box(340, 570, 560, 60, "вузол /dev/sda весь час один і той самий",
             size=15, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8)

    render(os.path.join(IMG, 'devtmpfs-udev.svg'), W, H, *p)


# ── 4. Родовід ідеї «процес — це файл» ─────────────────────────────────────
def fig_proc_lineage():
    W, H = 1220, 730
    p = []

    rows = [
        ("1984", "V8, Bell Labs", BLUE_FILL, NEG,
         ["Том Кілліан, доповідь «Processes as Files»:",
          "/proc/<pid> — один файл на процес, керування через ioctl"]),
        ("кін. 1980-х", "Plan 9", BLUE_FILL, NEG,
         ["каталог на процес; замість ioctl —",
          "запис слова у файл керування ctl"]),
        ("1991", "SVR4", GREY_FILL, LINE,
         ["Фолкнер і Гомс переносять /proc у System V;",
          "1996, Solaris 2.6 — каталоги на потоки, без ioctl"]),
        ("1992", "Linux 0.97.3", WARM_FILL, WARM,
         ["/proc з'являється; уже в 0.98.6, за три місяці, —",
          "перші дані, що не стосуються жодного процесу"]),
        ("1994", "4.4BSD", GREY_FILL, LINE,
         ["/proc за зразком Plan 9;",
          "згодом відмирає на користь sysctl"]),
        ("2002", "Linux 2.5", GREEN_FILL, FIELD,
         ["Патрік Мохел: driverfs → sysfs разом із kobject —",
          "окреме дерево з правилами замість купок у /proc"]),
    ]

    YX, YW = 30, 260
    BX, BW = 340, 850
    RH, GAP = 82, 30
    y = 26
    for year, sysname, fill, stroke, lines in rows:
        p += box(YX, y, YW, RH, [year, sysname], size=15, bold=True,
                 fill=fill, stroke=stroke, sw=1.8)
        p += box(BX, y, BW, RH, lines, size=15, fill=fill, stroke=stroke)
        if y + RH + GAP < H:
            p.append(arrow(YX + YW / 2, y + RH + 3, YX + YW / 2, y + RH + GAP - 3))
        y += RH + GAP

    render(os.path.join(IMG, 'proc-lineage.svg'), W, H, *p)


# ── 5. Де саме біжить show(): single_open проти повного ітератора ──────────
def fig_show_timing():
    W, H = 1240, 730
    p = []

    p.append(line(620, 20, 620, 640, color=MUTED, sw=1.4, dash="7,6"))

    panels = [
        (40, 200, 270, 320, "single_open() — один суцільний знімок", NEG, BLUE_FILL, [
            ("openat()", ["single_open(): виділити seq_file",
                          "show() ще не викликано"], False),
            ("read() №1", ["start → show() → stop",
                           "увесь текст народжується тут"], True),
            ("GAP", ["буфер уже повний — обходу більше не буде"], "calm"),
            ("read() №2", ["start віддає NULL",
                           "0 — кінець файлу"], False),
            ("close()", ["single_release: звільнити буфер"], False),
        ]),
        (650, 200, 880, 320, "seq_operations — обхід порціями по сторінці",
         FIELD, GREEN_FILL, [
            ("openat()", ["seq_open(): виділити seq_file",
                          "позиція обходу = 0"], False),
            ("read() №1", ["start(0) → show/next/show/next…",
                           "сторінка повна → stop"], True),
            ("GAP", ["замка немає — система живе далі"], "hot"),
            ("read() №2", ["start(178) — НОВИЙ обхід",
                           "уже за новим станом"], True),
            ("close()", ["seq_release: звільнити буфер"], False),
        ]),
    ]

    for sx, sw, kx, kw, title, color, fill, rows in panels:
        full = kx + kw - sx
        p += box(sx, 26, full, 46, title, size=16, bold=True, fill=fill, stroke=color)
        y = 110
        for name, lines, mark in rows:
            if name == "GAP":
                fl = RED_FILL if mark == "hot" else GREY_FILL
                st = POS if mark == "hot" else MUTED
                p += box(sx, y, full, 46, lines, size=13, fill=fl, stroke=st, sw=1.4)
                y += 46 + 22
                continue
            h = 40 + len(lines) * 22
            p += box(sx, y, sw, h, name, size=14, bold=True, fill=GREY_FILL)
            fl = WARM_FILL if mark else FILL
            st = WARM if mark else LINE
            p += box(kx, y, kw, h, lines, size=13, fill=fl, stroke=st,
                     sw=1.8 if mark else 1.5)
            p.append(arrow(sx + sw + 4, y + h / 2, kx - 4, y + h / 2))
            y += h + 22

    p.append(text(620, 690,
                  "show() біжить на read, а не на open — тому два cat поспіль дають різні числа",
                  size=15, color=MUTED, italic=True))

    render(os.path.join(IMG, 'show-timing.svg'), W, H, *p)


fig_two_branches()
fig_torn_read()
fig_devtmpfs_udev()
fig_proc_lineage()
fig_show_timing()
print("ok")
