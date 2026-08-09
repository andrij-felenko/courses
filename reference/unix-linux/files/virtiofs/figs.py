# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f2f3f5"


# ── 1. Шлях запиту: що лежить у спільній пам'яті, а що перетинає межу ─────────
def fig_request_path():
    W, H = 1300, 760
    p = []

    GX, GW = 60, 380          # колонка гостя
    MX, MW = 500, 300         # смуга спільної пам'яті
    HX, HW = 860, 380         # колонка господаря

    p.append(text(GX + GW / 2, 56, "гість", size=16, bold=True))
    p.append(text(MX + MW / 2, 56, "оперативна пам'ять гостя", size=16, bold=True))
    p.append(text(HX + HW / 2, 56, "господар", size=16, bold=True))
    p.append(text(MX + MW / 2, 78, "вона ж — пам'ять господаря", size=11, color=MUTED))

    # ── колонка гостя ────────────────────────────────────────────────────────
    guest = [
        ("програма: read(fd, buf, n)", "звичайний системний виклик", COOL, NEG),
        ("VFS", "переадресує виклик файловій системі", SOFT, MUTED),
        ("клієнт FUSE", "складає fuse_in_header і аргументи", GREEN, FIELD),
        ("драйвер virtio-fs", "кладе ланцюжок у чергу, штовхає", WARM, POS),
    ]
    gy = 120
    BH = 82
    GAP = 40
    for i, (head, sub, tint, accent) in enumerate(guest):
        y = gy + i * (BH + GAP)
        p.append(rect(GX, y, GW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(GX + GW / 2, y + 33, head, size=13, bold=True))
        p.append(text(GX + GW / 2, y + 56, sub, size=10.5, color=MUTED))
        if i < len(guest) - 1:
            p.append(arrow(GX + GW / 2, y + BH + 6, GX + GW / 2, y + BH + GAP - 6, color=MUTED, sw=2))

    # ── смуга спільної пам'яті: дескрипторний ланцюжок ────────────────────────
    band_y, band_h = 120, 4 * BH + 3 * GAP
    p.append(rect(MX, band_y, MW, band_h, fill="#ffffff", stroke=MUTED, sw=1.8, rx=10))

    slots = [
        ("fuse_in_header", "читає пристрій", GREEN, FIELD),
        ("аргументи запиту", "читає пристрій", GREEN, FIELD),
        ("fuse_out_header", "пише пристрій", WARM, POS),
        ("буфер під дані відповіді", "пише пристрій", WARM, POS),
    ]
    sy = band_y + 34
    SH = 66
    SG = 26
    for i, (head, sub, tint, accent) in enumerate(slots):
        y = sy + i * (SH + SG)
        p.append(rect(MX + 26, y, MW - 52, SH, fill=tint, stroke=accent, sw=1.6, rx=6))
        p.append(text(MX + MW / 2, y + 27, head, size=12, bold=True))
        p.append(text(MX + MW / 2, y + 47, sub, size=10, color=MUTED))

    p.append(text(MX + MW / 2, band_y + band_h - 14,
                  "дескрипторний ланцюжок віртчерги", size=11, color=MUTED))

    # ── колонка господаря ────────────────────────────────────────────────────
    host = [
        ("virtiofsd", "пам'ять гостя йому відображена", GREEN, FIELD),
        ("читає запит на місці", "жодного копіювання й пересилання", SOFT, MUTED),
        ("openat, pread, pwrite", "звичайні виклики над спільною текою", COOL, NEG),
        ("файлова система господаря", "справжній диск, справжній кеш", GREY, MUTED),
    ]
    for i, (head, sub, tint, accent) in enumerate(host):
        y = gy + i * (BH + GAP)
        p.append(rect(HX, y, HW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(HX + HW / 2, y + 33, head, size=13, bold=True))
        p.append(text(HX + HW / 2, y + 56, sub, size=10.5, color=MUTED))
        if i < len(host) - 1:
            p.append(arrow(HX + HW / 2, y + BH + 6, HX + HW / 2, y + BH + GAP - 6, color=MUTED, sw=2))

    # ── зв'язки зі смугою ────────────────────────────────────────────────────
    p.append(arrow(GX + GW + 8, gy + 2 * (BH + GAP) + BH / 2,
                   MX - 8, gy + 2 * (BH + GAP) + BH / 2, color=FIELD, sw=2.2))
    p.append(arrow(HX - 8, gy + BH / 2, MX + MW + 8, gy + BH / 2, color=FIELD, sw=2.2))

    # ── межа й поштовх ───────────────────────────────────────────────────────
    by = band_y + band_h + 66
    p.append(line(GX, by, HX + HW, by, color=POS, sw=2, dash="8 6"))
    p.append(text(GX + 8, by - 12, "межа гість ↔ господар: єдине, що її перетинає",
                  size=12, color=POS, anchor="start", bold=True))

    box, bw, bh = textbox(W / 2, by + 46,
                          ["поштовх «у черзі є робота» — вихід із гостя,",
                           "тисячі тактів; дані його не перетинають"],
                          size=12, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(box)

    render(os.path.join(OUT, "request-path.svg"), W, H, *p)


# ── 2. Копія проти DAX-вікна ─────────────────────────────────────────────────
def fig_dax_window():
    W, H = 1300, 720
    p = []

    LX, RX, CW = 60, 700, 540

    p.append(text(LX + CW / 2, 52, "шлях із копіюванням", size=16, bold=True))
    p.append(text(RX + CW / 2, 52, "шлях через DAX-вікно", size=16, bold=True))

    BH = 84
    GAP = 44
    top = 96

    left = [
        ("сторінки кешу господаря", "перший примірник вмісту", GREEN, FIELD),
        ("демон робить pread у буфер гостя", "одне копіювання", WARM, POS),
        ("кеш сторінок гостя", "ДРУГИЙ примірник того самого вмісту", WARM, POS),
        ("буфер програми", "ще одне копіювання в межах гостя", COOL, NEG),
    ]
    right = [
        ("сторінки кешу господаря", "єдиний примірник вмісту", GREEN, FIELD),
        ("SETUPMAPPING: сторінки в область", "спільна пам'ять пристрою — вікно", GREEN, FIELD),
        ("гостьове ядро віддає їх процесу", "записи таблиць сторінок на ті самі сторінки", SOFT, MUTED),
        ("вікно скінченне", "зайве доводиться витісняти REMOVEMAPPING", GREY, MUTED),
    ]

    for col_x, items, gaps in (
        (LX, left, ["відображена пам'ять гостя", "гість кладе прочитане до себе", "копіювання в межах пам'яті"]),
        (RX, right, ["запит демона до гіпервізора", "той самий фізичний кадр", "плата за перекладання"]),
    ):
        for i, (head, sub, tint, accent) in enumerate(items):
            y = top + i * (BH + GAP)
            p.append(rect(col_x, y, CW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
            p.append(text(col_x + CW / 2, y + 34, head, size=13, bold=True))
            p.append(text(col_x + CW / 2, y + 58, sub, size=10.5, color=MUTED))
        for i, lab in enumerate(gaps):
            y0 = top + i * (BH + GAP) + BH
            p.append(arrow(col_x + 70, y0 + 8, col_x + 70, y0 + GAP - 8, color=MUTED, sw=2))
            p.append(text(col_x + 92, y0 + GAP / 2 + 4, lab, size=10.5, color=MUTED, anchor="start"))

    bot = top + 4 * (BH + GAP) + 16
    b1, _, _ = textbox(LX + CW / 2, bot + 34,
                       ["примірників вмісту в пам'яті: два",
                        "копіювань на кожне читання: два"],
                       size=12, fill="#fdecea", stroke=POS, sw=1.8)
    b2, _, _ = textbox(RX + CW / 2, bot + 34,
                       ["примірників вмісту в пам'яті: один",
                        "копіювань на читання через mmap: нуль"],
                       size=12, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b1)
    p.append(b2)

    render(os.path.join(OUT, "dax-window.svg"), W, H, *p)


# ── 3. Що з чим мусить збігтися у трьох командних рядках ─────────────────────
def fig_wiring():
    W, H = 1360, 660
    p = []

    LX, LW = 60, 560
    RX, RW = 760, 540

    p.append(text(LX + LW / 2, 56, "де ім'я оголошують", size=16, bold=True))
    p.append(text(RX + RW / 2, 56, "де воно мусить збігтися", size=16, bold=True))

    rows = [
        ("virtiofsd --socket-path=/tmp/vfsd.sock",
         "демон створює цей сокет і слухає його",
         "-chardev socket,id=char0,path=/tmp/vfsd.sock",
         "QEMU під'єднується до вже піднятого демона",
         GREEN, FIELD),
        ("-chardev socket,id=char0",
         "ім'я символьного пристрою всередині QEMU",
         "-device vhost-user-fs-pci,chardev=char0",
         "пристрій бере з нього канал vhost-user",
         COOL, NEG),
        ("-device vhost-user-fs-pci,tag=myfs",
         "мітка лягає в поле tag конфігурації пристрою",
         "guest# mount -t virtiofs myfs /mnt",
         "гість шукає пристрій саме з цією міткою",
         WARM, POS),
        ("-object memory-backend-memfd,id=mem,share=on",
         "пам'ять гостя — у розділюваному об'єкті",
         "-numa node,memdev=mem",
         "саме цей об'єкт і стає пам'яттю гостя",
         GREY, MUTED),
    ]

    top, BH, GAP = 104, 92, 38
    for i, (lh, ls, rh, rs, tint, accent) in enumerate(rows):
        y = top + i * (BH + GAP)
        p.append(rect(LX, y, LW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(LX + LW / 2, y + 36, lh, size=12.5, bold=True))
        p.append(text(LX + LW / 2, y + 62, ls, size=10.5, color=MUTED))

        p.append(rect(RX, y, RW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(RX + RW / 2, y + 36, rh, size=12.5, bold=True))
        p.append(text(RX + RW / 2, y + 62, rs, size=10.5, color=MUTED))

        p.append(arrow(LX + LW + 14, y + BH / 2, RX - 14, y + BH / 2,
                       color=accent, sw=2.2))

    bot = top + 4 * (BH + GAP) + 10
    box, _, _ = textbox(W / 2, bot + 34,
                        ["share=on — не оптимізація: без розділюваного об'єкта",
                         "демонові нема чого відображати, і черги не працюють зовсім"],
                        size=12, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(box)

    render(os.path.join(OUT, "wiring.svg"), W, H, *p)


fig_request_path()
fig_dax_window()
fig_wiring()
print("ok")
