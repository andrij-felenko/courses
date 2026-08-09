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
GREY_FILL = "#eeeeee"


# ── 1. Одне під'єднання — дерево інтерфейсів — кілька файлів ────────────────
def fig_interface_tree():
    W, H = 1320, 700
    p = []

    p.append(fitbox(440, 30, 440, 62, "вебкамера в роз'ємі",
                    size=16, bold=True, fill=GREY_FILL, stroke=LINE))
    p.append(arrow(660, 92, 660, 140))

    p.append(fitbox(340, 140, 640, 86,
                    "struct usb_device\n/sys/bus/usb/devices/1-1",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))

    ifaces = [
        (30,  "1-1:1.0\nVideo Control\nклас 0e / 01"),
        (355, "1-1:1.1\nVideo Streaming\nклас 0e / 02"),
        (680, "1-1:1.2\nAudio Control\nклас 01 / 01"),
        (1005, "1-1:1.3\nAudio Streaming\nклас 01 / 02"),
    ]
    for x, s in ifaces:
        p.append(arrow(660, 226, x + 142, 300))
        p.append(fitbox(x, 300, 285, 100, s, size=14, fill=FILL, stroke=LINE))

    p.append(arrow(172, 400, 320, 450))
    p.append(arrow(497, 400, 340, 450))
    p.append(arrow(822, 400, 980, 450))
    p.append(arrow(1147, 400, 1000, 450))

    p.append(fitbox(30, 450, 610, 72, "драйвер uvcvideo",
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(680, 450, 610, 72, "драйвер snd-usb-audio",
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(335, 522, 335, 580))
    p.append(arrow(985, 522, 985, 580))

    p.append(fitbox(30, 580, 610, 78,
                    "підсистема V4L2\n/dev/video0", size=15, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(680, 580, 610, 78,
                    "підсистема ALSA\n/dev/snd/pcmC1D0c", size=15, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'interface-tree.svg'), W, H, *p)


# ── 2. Шлях від зміни на порту до вузла в /dev ──────────────────────────────
def fig_plug_to_file():
    W, H = 1200, 910
    p = []

    steps = [
        (40,  "контролер хоста помічає зміну напруги на порту", GREY_FILL, LINE),
        (146, "usbcore: скидання порту, адреса, читання дескрипторів", BLUE_FILL, NEG),
        (252, "у sysfs з'являється 1-1 і кожен його інтерфейс 1-1:1.N", BLUE_FILL, NEG),
        (358, "ядро надсилає uevent із рядком MODALIAS", BLUE_FILL, NEG),
        (464, "udev віддає рядок kmod; потрібний модуль вантажиться", WARM_FILL, WARM),
        (570, "usbcore кличе probe() — окремо на КОЖЕН інтерфейс", GREEN_FILL, FIELD),
        (676, "драйвер реєструється у своїй підсистемі: input, V4L2, block, tty", GREEN_FILL, FIELD),
        (782, "підсистема створює символьний або блоковий вузол у /dev", GREEN_FILL, FIELD),
    ]
    for y, s, f, st in steps:
        p.append(fitbox(150, y, 900, 68, s, size=15, fill=f, stroke=st))
    for y in [40, 146, 252, 358, 464, 570, 676]:
        p.append(arrow(600, y + 68, 600, y + 106))

    render(os.path.join(IMG, 'plug-to-file.svg'), W, H, *p)


# ── 3. Дві дороги до того самого інтерфейсу ─────────────────────────────────
def fig_two_roads():
    W, H = 1340, 740
    p = []

    p.append(fitbox(70, 30, 520, 92,
                    "програма поверх класового драйвера\nopen(\"/dev/video0\"), ioctl, read",
                    size=15, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(750, 30, 520, 92,
                    "програма поверх libusb\nopen(\"/dev/bus/usb/001/007\")",
                    size=15, fill=WARM_FILL, stroke=WARM))

    p.append(arrow(330, 122, 330, 176))
    p.append(arrow(1010, 122, 1010, 176))

    p.append(fitbox(70, 176, 520, 92,
                    "підсистема V4L2\nдрайвер uvcvideo",
                    size=15, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(750, 176, 520, 92,
                    "usbfs\nioctl USBDEVFS_SUBMITURB / REAPURB",
                    size=15, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(330, 268, 520, 336))
    p.append(arrow(1010, 268, 820, 336))

    p.append(fitbox(330, 336, 680, 88,
                    "usbcore: URB у черзі кінцевої точки",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(670, 424, 670, 476))

    p.append(fitbox(330, 476, 680, 80,
                    "драйвер контролера хоста (xHCI)",
                    size=15, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(670, 556, 670, 608))

    p.append(fitbox(330, 608, 680, 80,
                    "шина: транзакції в мікрокадрах",
                    size=15, fill=GREY_FILL, stroke=LINE))

    p.append(fitbox(30, 470, 270, 96,
                    "інтерфейс віддають\nлише одному\nз двох шляхів",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(1040, 470, 270, 96,
                    "щоб узяти правий,\nтреба відчепити\nкласовий драйвер",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *p)


# ── 4. Життєвий цикл асинхронного URB у usbfs ──────────────────────────────
def fig_urb_cycle():
    W, H = 1260, 600
    p = []

    # верхня дорога: скасування
    p.append(line(170, 208, 170, 118))
    p.append(line(170, 118, 610, 118))
    p.append(arrow(610, 118, 610, 186))
    p.append(text(390, 100, "USBDEVFS_DISCARDURB — вбиває запит, status стає −ENOENT",
                 size=15, color=POS))

    # три стани
    p.append(fitbox(40, 208, 260, 104,
                    "програма\nвласний struct usbdevfs_urb",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(480, 186, 300, 126,
                    "у польоті\nчерга usbcore\nбуфер скопійовано в ядро",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(960, 186, 260, 126,
                    "готові\nчерга usbfs\nчекають, поки заберуть",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(300, 250, 470, 250))
    p.append(text(385, 232, "SUBMITURB", size=15, bold=True))

    p.append(arrow(780, 250, 950, 250))
    p.append(text(865, 232, "транзакція", size=15))

    # зворотна дорога: збирання
    p.append(line(1090, 312, 1090, 392))
    p.append(line(1090, 392, 170, 392))
    p.append(arrow(170, 392, 170, 320))
    p.append(text(600, 374, "REAPURB (блокує) · REAPURBNDELAY (EAGAIN, якщо порожньо)",
                 size=15, bold=True, color=NEG))

    # що приходить у status
    p.append(fitbox(660, 440, 560, 132,
                    "поле status готового запиту\n"
                    "0 — усе передано · −EPIPE — кінцева точка застрягла\n"
                    "−EOVERFLOW — пристрій дав більше, ніж просили\n"
                    "−ENOENT — скасовано · −ENODEV, −ESHUTDOWN — від'єднано",
                    size=14, fill=FILL, stroke=LINE))

    p.append(fitbox(40, 440, 560, 132,
                    "залізне правило\n"
                    "кожен відданий запит треба забрати — і скасований теж;\n"
                    "поки забирають, ядро тримає буфер і пам'ять usbfs\n"
                    "(стеля — модульний параметр usbfs_memory_mb, 16 МіБ)",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'urb-cycle.svg'), W, H, *p)


# ── 5. Чому кільце заявок: одна синхронна передача лишає чергу порожньою ────
def fig_libusb_ring():
    W, H = 1270, 570
    p = []

    p.append(fitbox(30, 84, 230, 66, "одна синхронна\nbulk-передача",
                    size=15, bold=True, fill=GREY_FILL, stroke=LINE))

    for i, x in enumerate((290, 550, 810, 1070)):
        p.append(fitbox(x, 84, 150, 66, "передача %d" % (i + 1),
                        size=14, fill=BLUE_FILL, stroke=NEG))
    for x in (440, 700, 960):
        p.append(fitbox(x, 84, 110, 66, "порожньо",
                        size=13, fill=RED_FILL, stroke=POS))

    p.append(text(290, 196,
                  "поки програма розбирає відповідь і подає наступну заявку,",
                  size=14, color=MUTED, anchor="start"))
    p.append(text(290, 220,
                  "черга кінцевої точки порожня — пристроєві нема куди писати",
                  size=14, color=MUTED, anchor="start"))

    p.append(fitbox(30, 316, 230, 66, "кільце\nз чотирьох заявок",
                    size=15, bold=True, fill=GREY_FILL, stroke=LINE))

    lanes = [
        (280, [(290, 190), (710, 190), (1130, 90)]),
        (322, [(395, 190), (815, 190)]),
        (364, [(500, 190), (920, 190)]),
        (406, [(605, 190), (1025, 190)]),
    ]
    for y, bars in lanes:
        for x, w in bars:
            p.append(fitbox(x, y, w, 34, "заявка",
                            size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(290, 474,
                  "щойно одна заявка завершилась, зворотний виклик подає її знову —",
                  size=14, color=MUTED, anchor="start"))
    p.append(text(290, 498,
                  "вільний буфер у кінцевої точки є завжди",
                  size=14, color=MUTED, anchor="start"))

    p.append(text(268, 538, "час", size=13, color=MUTED, anchor="end"))
    p.append(arrow(290, 533, 1220, 533, color=MUTED))

    render(os.path.join(IMG, 'libusb-ring.svg'), W, H, *p)


fig_interface_tree()
fig_plug_to_file()
fig_two_roads()
fig_urb_cycle()
fig_libusb_ring()
print("ok")
