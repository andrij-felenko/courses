# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


def cell(x, y, w, h, label, fill=FILL, size=13, bold=False, sw=1.4):
    out = rect(x, y, w, h, fill=fill, stroke=LINE, sw=sw, rx=3)
    if label:
        out += "\n" + text(x + w / 2.0, y + h / 2.0 + size * 0.36, label,
                           size=size, bold=bold)
    return out


# ── 1. Розкладка GPT на диску ───────────────────────────────────────────────
def fig_gpt_layout():
    W, H = 1400, 640
    p = []

    x0, band_y, band_h = 100, 180, 84
    segs = [
        (90,  "0",           RED,   "захисний MBR",                 330),
        (90,  "1",           WARM,  "заголовок GPT",                450),
        (190, "2 … 33",      BLUE,  "масив зі 128 записів",         330),
        (540, "34 … N−34",   GREEN, "місце під самі розділи",       330),
        (190, "N−33 … N−1",  BLUE,  "копія масиву",                 330),
        (100, "N",           WARM,  "копія заголовка",              450),
    ]

    x = x0
    centers = []
    for w, inner, fill, _cap, _row in segs:
        p.append(cell(x, band_y, w, band_h, inner, fill=fill, size=13))
        centers.append(x + w / 2.0)
        x += w
    band_right = x

    p.append(text(x0, band_y - 16, "номери секторів (LBA), останній = N",
                  size=13, color=MUTED, anchor="start"))

    # підписи під смугою, у два ряди — щоб не налазили один на одного
    for (w, _inner, _fill, cap, row), cx in zip(segs, centers):
        frag, bw, bh = textbox(cx, row, cap, size=13, pad=12, fill=GREY, stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx, band_y + band_h, cx, row - bh / 2.0, color=MUTED, sw=1.1, dash="4,4"))

    # дзеркало: заголовок ↔ копія заголовка, масив ↔ копія масиву
    y_m = 128
    p.append(line(centers[1], y_m, centers[5], y_m, color=NEG, sw=1.6, dash="6,5"))
    p.append(line(centers[1], y_m, centers[1], band_y, color=NEG, sw=1.6, dash="6,5"))
    p.append(line(centers[5], y_m, centers[5], band_y, color=NEG, sw=1.6, dash="6,5"))
    f, _w, _h = textbox((centers[1] + centers[5]) / 2.0, 70,
                        "та сама таблиця записана двічі: якщо CRC32 першої копії",
                        size=13, pad=12, fill=BLUE, stroke=NEG, sw=1.2)
    p.append(f)
    f2, _w2, _h2 = textbox((centers[1] + centers[5]) / 2.0, 105,
                           "не сходиться, ядро бере другу",
                           size=13, pad=12, fill=BLUE, stroke=NEG, sw=1.2)
    p.append(f2)

    # нижня примітка
    f3, _w3, _h3 = textbox((x0 + band_right) / 2.0, 560,
                           ["перший придатний для розділу сектор — 34:",
                            "1 сектор під захисний MBR + 1 під заголовок + 32 під масив записів"],
                           size=13, pad=14, fill=GREEN, stroke=FIELD, sw=1.3)
    p.append(f3)

    return render(os.path.join(IMG, 'gpt-layout.svg'), W, H, *p)


# ── 2. Розділ як вікно зі зсувом на тому самому пристрої ────────────────────
def fig_partition_window():
    W, H = 1340, 720
    p = []

    x0, y_d, h_d = 90, 150, 76
    segs = [
        (120, "службове", GREY),
        (380, "sda1", GREEN),
        (300, "sda2", BLUE),
        (110, "вільне", GREY),
    ]
    x = x0
    bounds = []
    for w, lab, fill in segs:
        p.append(cell(x, y_d, w, h_d, lab, fill=fill, size=14, bold=(lab.startswith("sda"))))
        bounds.append((x, x + w))
        x += w

    p.append(text(x0, y_d - 20, "/dev/sda — суцільний масив секторів 0 … N",
                  size=14, anchor="start", bold=True))

    p1x0, p1x1 = bounds[1]
    p2x0, p2x1 = bounds[2]

    # власний адресний простір sda1
    y_p, h_p = 360, 66
    p.append(cell(p1x0, y_p, p1x1 - p1x0, h_p, "", fill=GREEN))
    p.append(text(p1x0, y_p - 18, "/dev/sda1 — свій відлік від нуля",
                  size=14, anchor="start", bold=True))
    p.append(text(p1x0 + 6, y_p + h_p / 2.0 + 5, "0", size=13, anchor="start"))
    p.append(text(p1x1 - 6, y_p + h_p / 2.0 + 5, "довжина − 1", size=13, anchor="end"))

    p.append(line(p1x0, y_d + h_d, p1x0, y_p, color=FIELD, sw=1.6, dash="5,4"))
    p.append(line(p1x1, y_d + h_d, p1x1, y_p, color=FIELD, sw=1.6, dash="5,4"))

    f, _w, _h = textbox(1010, 362,
                        ["сектор 0 на sda1",
                         "= сектор 2048 на sda",
                         "весь переклад — одне додавання",
                         "і перевірка, чи не вилізли за довжину"],
                        size=13, pad=14, fill=WARM, stroke=LINE, sw=1.3)
    p.append(f)

    # спільна черга
    y_q = 570
    fq, wq, hq = textbox(560, y_q,
                         ["черга запитів, планувальник, ліміти розміру запиту —",
                          "усе це має ПРИСТРІЙ-ДИСК, а не розділ"],
                         size=14, pad=16, fill=RED, stroke=POS, sw=1.5)
    p.append(fq)
    p.append(arrow((p1x0 + p1x1) / 2.0, y_p + h_p, 470, y_q - hq / 2.0 - 6))
    p.append(arrow((p2x0 + p2x1) / 2.0, y_d + h_d, 700, y_q - hq / 2.0 - 6))

    f2, _w2, _h2 = textbox(560, 668,
                           "два розділи одного диска не працюють паралельно — вони стоять в одній черзі",
                           size=13, pad=13, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f2)

    return render(os.path.join(IMG, 'partition-window.svg'), W, H, *p)


# ── 3. Вирівнювання: звідки починається розділ ──────────────────────────────
def fig_alignment():
    W, H = 1400, 560
    p = []

    cw = 110          # ширина одного фізичного блока на малюнку
    y_ph, h_ph = 180, 58
    y_fs, h_fs = 300, 58

    def panel(px, title, off_cells, n_fs, verdict, verdict_fill, verdict_stroke):
        frag = []
        f, _w, _h = textbox(px + 2 * cw, 108, title, size=14, pad=13,
                            fill=GREY, stroke=MUTED, sw=1.2)
        frag.append(f)
        for k in range(4):
            frag.append(cell(px + k * cw, y_ph, cw, h_ph, "",
                             fill=(GREY if k % 2 == 0 else FILL)))
        fx = px + off_cells * cw
        for k in range(n_fs):
            frag.append(cell(fx + k * cw, y_fs, cw, h_fs, "",
                             fill=(GREEN if k % 2 == 0 else "#f2fbf5")))
        for k in range(5):
            gx = px + k * cw
            frag.append(line(gx, y_ph - 22, gx, y_fs + h_fs + 22,
                             color=NEG, sw=1.2, dash="4,5"))
        fv, _wv, _hv = textbox(px + 2 * cw, 420, verdict, size=13, pad=13,
                               fill=verdict_fill, stroke=verdict_stroke, sw=1.3)
        frag.append(fv)
        return frag

    p += panel(90, "розділ починається з сектора 63", 0.875, 3,
               "один блок ФС лягає на два фізичні", RED, POS)
    p += panel(830, "розділ починається з сектора 2048", 0.0, 4,
               "один блок ФС — рівно один фізичний", GREEN, FIELD)

    f, _w, _h = textbox(700, 500,
                        ["сірий ряд — фізичні блоки носія по 4 КіБ, відлічені від початку ДИСКА;",
                         "зелений — блоки файлової системи по 4 КіБ, відлічені від початку РОЗДІЛУ"],
                        size=13, pad=14, fill=FILL, stroke=MUTED, sw=1.2)
    p.append(f)

    return render(os.path.join(IMG, 'partition-alignment.svg'), W, H, *p)


# ── 4. Ланцюг розширеного розділу (вставка hist) ────────────────────────────
def fig_ebr_chain():
    W, H = 1440, 640
    p = []

    p.append(text(730, 74, "чотири записи таблиці в 64 байтах першого сектора",
                  size=14, color=MUTED))

    x0, by, bh = 90, 110, 76
    prim = [(190, "розділ 1", BLUE), (190, "розділ 2", BLUE),
            (190, "розділ 3", BLUE)]
    x = x0
    for w, lab, fill in prim:
        p.append(cell(x, by, w, bh, lab, fill=fill, size=13))
        x += w
    ext_x, ext_w = x, 700
    p.append(cell(ext_x, by, ext_w, bh, "розширений розділ — контейнер",
                  fill=WARM, size=13, bold=True))

    node_y, node_h = 300, 96
    nodes = [670, 915, 1160]
    names = ["логічний 5", "логічний 6", "логічний 7"]

    p.append(line(ext_x, by + bh, nodes[0], node_y, color=MUTED, sw=1.2, dash="5 5"))
    p.append(line(ext_x + ext_w, by + bh, nodes[-1] + 200, node_y,
                  color=MUTED, sw=1.2, dash="5 5"))

    for nx, nm in zip(nodes, names):
        p.append(cell(nx, node_y, 54, node_h, "EBR", fill=RED, size=12, bold=True))
        p.append(cell(nx + 70, node_y, 130, node_h, nm, fill=GREEN, size=13))

    link_y = 470
    for a, b in zip(nodes, nodes[1:]):
        p.append(line(a + 27, node_y + node_h, a + 27, link_y, color=LINE, sw=1.6))
        p.append(line(a + 27, link_y, b + 27, link_y, color=LINE, sw=1.6))
        p.append(arrow(b + 27, link_y, b + 27, node_y + node_h + 6))

    f, _w, _h = textbox(360, 470,
                        ["у кожній ланці — свій міні-сектор:",
                         "запис про цей розділ і посилання",
                         "на наступну ланку"],
                        size=13, pad=12, fill=FILL, stroke=MUTED, sw=1.2)
    p.append(f)

    f, _w, _h = textbox(1180, 570, "кінець ланцюга — порожнє посилання",
                        size=12, pad=10, fill=GREY, stroke=MUTED, sw=1.2)
    p.append(f)

    return render(os.path.join(IMG, 'ebr-chain.svg'), W, H, *p)


# ── 5. Хронологія схем розмітки (вставка hist) ──────────────────────────────
def fig_partitioning_timeline():
    W, H = 1440, 540
    p = []

    axis_y = 300
    p.append(line(90, axis_y, 1350, axis_y, color=MUTED, sw=2))

    events = [
        ("1983 · PC DOS 2.0",      "4 записи в 64 байтах",     RED),
        ("1986–1987 · DOS 3.2/3.30", "розширений розділ",      WARM),
        ("1987–1988 · APM, disklabel", "свої схеми поза PC",   GREY),
        ("1994–1996 · LBA",        "адреса без геометрії",     BLUE),
        ("1998–2000 · EFI, Itanium", "GPT родом із прошивки",  GREEN),
        ("2005–2006 · UEFI Forum", "GPT у розділі 5 UEFI",     GREEN),
    ]

    xs = [140 + i * 224 for i in range(len(events))]
    for i, (x, (top, bottom, fill)) in enumerate(zip(xs, events)):
        up = (i % 2 == 0)
        cy = 175 if up else 425
        p.append(line(x, axis_y, x, cy + (48 if up else -48), color=MUTED,
                      sw=1.2, dash="4 4"))
        f, _w, _h = textbox(x, cy, [top, bottom], size=12, pad=11,
                            fill=fill, stroke=LINE, sw=1.3)
        p.append(f)
        p.append(circle(x, axis_y, 7, fill=FILL, stroke=INK, sw=2))

    return render(os.path.join(IMG, 'partitioning-timeline.svg'), W, H, *p)


# ── 6. Ті самі LBA — різні байти (512 проти 4096) ───────────────────────────
def fig_sector_size_math():
    W, H = 1240, 470
    p = []

    def band(y, ss, arr_last, first_ok, label):
        cells = [
            (150, "LBA 0",  "захисний MBR",    RED),
            (150, "LBA 1",  "заголовок",       WARM),
            (230, "LBA 2 … %d" % arr_last, "масив 16 КіБ = %d сект." % (16384 // ss), BLUE),
            (280, "LBA %d … N−%d" % (first_ok, arr_last), "самі розділи", GREEN),
        ]
        p.append(text(90, y - 18, label, size=14, bold=True, anchor="start"))
        x, h = 90, 76
        centers = []
        for w, top, bottom, fill in cells:
            p.append(fitbox(x, y, w, h, "%s\n%s" % (top, bottom), size=13, fill=fill))
            centers.append(x + w / 2.0)
            x += w
        p.append(text(x + 20, y + h / 2.0 + 5, "…", size=20, color=MUTED))
        x += 40
        p.append(fitbox(x, y, 200, h, "LBA N\nкопія заголовка", size=13, fill=WARM))
        centers.append(x + 100)

        for cx, off in zip(centers[:3], (0, ss, 2 * ss)):
            p.append(text(cx, y + h + 26, "байт %d" % off, size=12, color=MUTED))
        p.append(text(90, y + h + 58,
                      "байт = LBA · %d        останній LBA = місткість ÷ %d − 1" % (ss, ss),
                      size=13, color=NEG, anchor="start"))

    band(90, 512, 33, 34, "логічний сектор 512 байтів")
    band(300, 4096, 5, 6, "логічний сектор 4096 байтів")

    return render(os.path.join(IMG, 'sector-size-math.svg'), W, H, *p)


if __name__ == '__main__':
    print(fig_gpt_layout())
    print(fig_partition_window())
    print(fig_alignment())
    print(fig_ebr_chain())
    print(fig_partitioning_timeline())
    print(fig_sector_size_math())
