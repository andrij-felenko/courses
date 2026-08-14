# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. virtio-pci-caps.svg ──────────────────────────────────────────────────
def fig_virtio_pci_caps():
    W, H = 1400, 750
    p = []

    p.append(text(700, 40, "КОНФІГУРАЦІЙНИЙ ПРОСТІР PCI ТА VIRTIO CAPABILITIES", size=16, bold=True))
    p.append(text(700, 65, "Драйвер сканує PCI Capabilities (ID 0x09) та отримує зсуви до BAR-регіонів", size=13, color=MUTED))

    # PCI Config Space Panel
    p.append(text(300, 110, "PCI Configuration Space (256 байт)", size=14, bold=True))
    caps = [
        ["PCI Standard Header", "Vendor ID: 0x1AF4", "Device ID: 0x1041"],
        ["Cap 1: VIRTIO_PCI_CAP_COMMON_CFG", "cfg_type = 1, bar = 0", "offset = 0x0000"],
        ["Cap 2: VIRTIO_PCI_CAP_NOTIFY_CFG", "cfg_type = 2, bar = 0", "offset = 0x1000, mult = 4"],
        ["Cap 3: VIRTIO_PCI_CAP_ISR_CFG", "cfg_type = 3, bar = 0", "offset = 0x2000"],
        ["Cap 4: VIRTIO_PCI_CAP_DEVICE_CFG", "cfg_type = 4, bar = 0", "offset = 0x3000"],
    ]
    y_starts = [140, 240, 350, 460, 570]
    cap_geos = []
    for y, lines in zip(y_starts, caps):
        fill_c = BLUE_FILL if "Header" in lines[0] else GREY_FILL
        frag, w, h = textbox(300, y, lines, size=12.5, pad=12, fill=fill_c, stroke=LINE, sw=1.5)
        p.append(frag)
        cap_geos.append((300, y, w, h))

    # Memory Mapped I/O BAR0 Panel
    p.append(text(1000, 110, "MMIO Region (PCI BAR0)", size=14, bold=True))
    bars = [
        ["Common Config (struct virtio_pci_common_cfg)", "device_status, queue_select, queue_size,", "queue_desc, queue_driver, queue_device"],
        ["Doorbell Region (Notify)", "Queue 0 Doorbell (+0x1000)", "Queue 1 Doorbell (+0x1004)"],
        ["ISR Status Register (+0x2000)", "Interrupt Status Flags (INTx)"],
        ["Device Config (+0x3000)", "MAC Address / Disk Capacity / Features"],
    ]
    bar_ys = [240, 350, 460, 570]
    bar_geos = []
    for y, lines in zip(bar_ys, bars):
        fill_c = GREEN_FILL if "Doorbell" in lines[0] else WARM_FILL
        frag, w, h = textbox(1000, y, lines, size=12.5, pad=12, fill=fill_c, stroke=LINE, sw=1.5)
        p.append(frag)
        bar_geos.append((1000, y, w, h))

    # Arrows connecting Caps to BAR regions
    for (_, y1, w1, _), (_, y2, _, _) in zip(cap_geos[1:], bar_geos):
        p.append(arrow(300 + w1 / 2 + 10, y1, 1000 - w1 / 2 - 10, y2, color=LINE, sw=1.6))

    render(os.path.join(IMG, 'virtio-pci-caps.svg'), W, H, *p,
           title="Структура PCI Capabilities у Virtio 1.0+")


# ── 2. virtqueue-split.svg ──────────────────────────────────────────────────
def fig_virtqueue_split():
    W, H = 1500, 950
    p = []
    cx = 560
    nx = 1220

    p.append(text(cx, 46, "СПІЛЬНА ПАМ'ЯТЬ ГОСТЯ ТА ГІПЕРВІЗОРА (SPLIT VIRTQUEUE)", size=15, bold=True))
    p.append(text(cx, 70, "зелене пише лише драйвер · тепле пише лише пристрій", size=12, color=MUTED))

    # Available ring
    avail, wa, ha = textbox(cx, 165,
                            ["ДОСТУПНЕ КІЛЬЦЕ (Available Ring)",
                             "flags │ idx = 5 │ ring[] = 0, 4, 9, 2, 6"],
                            size=13, pad=15, fill=GREEN_FILL, stroke=LINE, sw=1.6)
    p.append(avail)

    # Descriptor Table
    p.append(text(cx, 290, "ТАБЛИЦЯ ДЕСКРИПТОРІВ (Descriptor Table)", size=13, bold=True))
    xs = [270, 560, 850]
    rows = [
        ["#6  addr = 0x3f21000", "len = 16", "flags = NEXT", "next = 7"],
        ["#7  addr = 0x3f8a200", "len = 1500", "flags = WRITE|NEXT", "next = 9"],
        ["#9  addr = 0x3f8c000", "len = 1", "flags = WRITE", "next = —"],
    ]
    dgeo = []
    for x, lines in zip(xs, rows):
        frag, w, h = textbox(x, 410, lines, size=12.5, pad=13, fill=GREY_FILL, stroke=LINE, sw=1.5)
        p.append(frag)
        dgeo.append((x, w, h))
    for (x1, w1, _), (x2, w2, _) in zip(dgeo, dgeo[1:]):
        p.append(arrow(x1 + w1 / 2 + 8, 410, x2 - w2 / 2 - 8, 410))

    # Used ring
    used, wu, hu = textbox(cx, 620,
                           ["ВИКОРИСТАНЕ КІЛЬЦЕ (Used Ring)",
                            "flags │ idx = 3 │ ring[] = { id = 6, len = 1517 }, …"],
                           size=13, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.6)
    p.append(used)

    title_top = 290 - 13 * 0.72 - 5
    title_bot = 290 + 13 * 0.16 + 5
    p.append(line(cx, 165 + ha / 2 + 10, cx, title_top, color=LINE, sw=1.8))
    p.append(arrow(cx, title_bot, cx, 410 - dgeo[1][2] / 2 - 35))
    p.append(arrow(cx, 410 + dgeo[1][2] / 2 + 12, cx, 620 - hu / 2 - 10))

    def note(y, lines, fill=GREY_FILL, anchor_w=0):
        frag, nw, _ = textbox(nx, y, lines, size=12.5, pad=13, fill=fill, stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + anchor_w / 2 + 14, y, nx - nw / 2 - 14, y, color=MUTED, sw=1.1, dash="5 4"))

    note(165, ["idx драйвер збільшує останнім:", "після запису дескрипторів", "та бар'єра пам'яті smp_wmb()"], GREEN_FILL, wa)
    note(410, ["VIRTQ_DESC_F_WRITE каже,", "хто має право писати у буфер:", "1 — пристрій, 0 — гость"], GREY_FILL, dgeo[1][1])
    note(620, ["len — скільки байтів записано;", "id — індекс голови ланцюжка,", "а не позиція в масиві"], WARM_FILL, wu)

    frag, _, _ = textbox(cx, 780,
                         ["Індекси 16-бітні, ростуть монотонно та обертаються за модулем 65536 —",
                          "обидві сторони обчислюють позиції як: slot = idx & (QueueSize - 1)"],
                         size=12.5, pad=13, fill=BLUE_FILL, stroke=FIELD, sw=1.3)
    p.append(frag)

    frag, _, _ = textbox(cx, 880,
                         ["Межу між гостем і хостом перетинають дві події: Kick у дверний дзвоник",
                          "та переривання MSI-X. Самі дані передаються за 0 копіювань (Zero-Copy)."],
                         size=12.5, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'virtqueue-split.svg'), W, H, *p,
           title="Анатомія розділеної черги Split Virtqueue")


# ── 3. packed-virtqueue.svg ─────────────────────────────────────────────────
def fig_packed_virtqueue():
    W, H = 1400, 700
    p = []

    p.append(text(700, 40, "ЄДИНЕ КІЛЬЦЕ ДЕСКРИПТОРІВ (PACKED VIRTQUEUE)", size=16, bold=True))
    p.append(text(700, 65, "Драйвер і пристрій працюють в одному масиві, використовуючи Wrap Counter", size=13, color=MUTED))

    # Ring items
    xs = [200, 450, 700, 950, 1200]
    descs = [
        ["Desc 0 (Used by Device)", "addr = 0x1000, len = 512", "id = 0", "AVAIL = 1, USED = 1"],
        ["Desc 1 (Used by Device)", "addr = 0x2000, len = 1024", "id = 1", "AVAIL = 1, USED = 1"],
        ["Desc 2 (Avail for Device)", "addr = 0x3000, len = 2048", "id = 2", "AVAIL = 1, USED = 0"],
        ["Desc 3 (Avail for Device)", "addr = 0x4000, len = 64", "id = 3", "AVAIL = 1, USED = 0"],
        ["Desc 4 (Free / Old)", "addr = 0x0000, len = 0", "id = 4", "AVAIL = 0, USED = 0"],
    ]

    for x, lines in zip(xs, descs):
        if "Used by Device" in lines[0]:
            fill_c = WARM_FILL
        elif "Avail for Device" in lines[0]:
            fill_c = GREEN_FILL
        else:
            fill_c = GREY_FILL
        frag, w, h = textbox(x, 220, lines, size=12, pad=12, fill=fill_c, stroke=LINE, sw=1.5)
        p.append(frag)

    # Wrap counter panel
    wc, _, _ = textbox(700, 420,
                       ["СТАН WRAP COUNTERS:",
                        "Driver Wrap Counter = 1  │  Device Wrap Counter = 1",
                        "Дескриптор доступний (Avail), коли: AVAIL == Wrap Counter && USED != Wrap Counter",
                        "Дескриптор оброблено (Used), коли: AVAIL == Wrap Counter && USED == Wrap Counter"],
                       size=13, pad=15, fill=BLUE_FILL, stroke=FIELD, sw=1.5)
    p.append(wc)

    # Highlights
    frag, _, _ = textbox(700, 580,
                         ["Головна перевага Packed Virtqueue: виключна локальність кешу (Cache Locality).",
                          "Немає окремих масивів Avail та Used — процесор вичитує лише одну послідовну cache line."],
                         size=13, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.3)
    p.append(frag)

    render(os.path.join(IMG, 'packed-virtqueue.svg'), W, H, *p,
           title="Анатомія упакованої черги Packed Virtqueue")


if __name__ == "__main__":
    fig_virtio_pci_caps()
    fig_virtqueue_split()
    fig_packed_virtqueue()
    print("Всі фігури згенеровано успішно.")
