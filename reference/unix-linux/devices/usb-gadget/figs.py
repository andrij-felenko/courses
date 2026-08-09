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


# ── 1. Два дзеркальні стеки: хост і гаджет ─────────────────────────────────
def fig_mirror_stacks():
    W, H = 1360, 780
    LX, RX, BW = 50, 750, 560
    lc, rc = LX + BW // 2, RX + BW // 2
    p = []

    rows = [
        (30, 64, "машина-хост", "машина-пристрій",
         GREY_FILL, LINE, True),
        (126, 96,
         "драйвер інтерфейсу\nuvcvideo · usb-storage · usbhid",
         "функція\nf_mass_storage · f_ecm · f_hid",
         GREEN_FILL, FIELD, False),
        (252, 96,
         "usbcore\nпошук драйвера за рядком modalias",
         "libcomposite\nдескриптори · ep0 · вибір конфігурації",
         BLUE_FILL, NEG, False),
        (378, 110,
         "struct urb\nдрайвер САМ починає передачу",
         "struct usb_request\nвідповідь лежить, поки її не спитають",
         WARM_FILL, WARM, False),
        (518, 90,
         "драйвер контролера хоста\nxHCI · EHCI",
         "драйвер контролера пристрою\ndwc2 · dwc3 · musb",
         BLUE_FILL, NEG, False),
    ]

    for y, h, ls, rs, f, st, bold in rows:
        p.append(fitbox(LX, y, BW, h, ls, size=16, bold=bold, fill=f, stroke=st))
        p.append(fitbox(RX, y, BW, h, rs, size=16, bold=bold, fill=f, stroke=st))

    for i in range(len(rows) - 1):
        y, h = rows[i][0], rows[i][1]
        nxt = rows[i + 1][0]
        p.append(arrow(lc, y + h, lc, nxt - 4))
        p.append(arrow(rc, y + h, rc, nxt - 4))

    p.append(fitbox(230, 650, 900, 80,
                    "шина: кожну транзакцію починає хост",
                    size=17, bold=True, fill=GREY_FILL, stroke=LINE))
    p.append(arrow(lc, 608, 500, 646))
    p.append(arrow(rc, 608, 860, 646))

    render(os.path.join(IMG, 'mirror-stacks.svg'), W, H, *p)


# ── 2. Каталоги configfs → набір дескрипторів ──────────────────────────────
def fig_configfs_to_descriptors():
    W, H = 1400, 520
    p = []

    p.append(text(340, 46, "що адміністратор створює каталогами",
                  size=16, bold=True))
    p.append(fitbox(40, 74, 600, 320,
                    "/sys/kernel/config/usb_gadget/g1/\n"
                    "   idVendor · idProduct · bcdUSB\n"
                    "   strings/0x409/ → manufacturer, product\n"
                    "   functions/acm.usb0/\n"
                    "   functions/ecm.usb0/\n"
                    "   configs/c.1/ → MaxPower\n"
                    "   configs/c.1/acm.usb0 → посилання\n"
                    "   configs/c.1/ecm.usb0 → посилання\n"
                    "   UDC ← сюди пишуть ім'я контролера",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(text(720, 206, "запис у UDC", size=13, color=POS))
    p.append(arrow(660, 234, 780, 234, color=POS))

    p.append(text(1090, 46, "що хост читає з пристрою", size=16, bold=True))
    p.append(fitbox(800, 74, 560, 320,
                    "Device Descriptor\n"
                    "   idVendor 0x1d6b · idProduct 0x0104\n"
                    "Configuration Descriptor «c.1»\n"
                    "   Interface 0 + 1 — acm (CDC-ACM)\n"
                    "      ep 0x81 IN · 0x01 OUT · 0x82 INT\n"
                    "   Interface 2 + 3 — ecm (CDC-ECM)\n"
                    "      ep 0x83 IN · 0x02 OUT · 0x84 INT",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(700, 462,
                  "номери інтерфейсів і адреси кінцевих точок libcomposite роздає "
                  "в мить прив'язки, а не наперед",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'configfs-to-descriptors.svg'), W, H, *p)


# ── 3. Кошторис кінцевих точок ─────────────────────────────────────────────
def fig_endpoint_budget():
    W, H = 1320, 640
    p = []

    p.append(text(660, 44, "кожна функція просить кінцеві точки, не знаючи заліза",
                  size=16, bold=True))

    funcs = [
        (60, "f_acm\n2 bulk + 1 interrupt"),
        (490, "f_ecm\n2 bulk + 1 interrupt"),
        (920, "f_hid\n1 interrupt IN"),
    ]
    for x, s in funcs:
        p.append(fitbox(x, 76, 340, 100, s, size=15, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(230, 176, 430, 232))
    p.append(arrow(660, 176, 660, 232))
    p.append(arrow(1090, 176, 890, 232))

    p.append(fitbox(230, 236, 860, 90,
                    "usb_ep_autoconfig(): роздає апаратні точки з тих, що ще вільні",
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(660, 326, 660, 390))

    p.append(text(100, 436, "UDC:", size=15, bold=True, anchor="end"))
    slots = ["ep1in", "ep1out", "ep2in", "ep2out", "ep3in", "ep3out"]
    for i, s in enumerate(slots):
        p.append(fitbox(130 + i * 180, 396, 160, 70, s,
                        size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(130, 506, 1060, 80,
                    "сьомій заявці апаратної точки вже нема:\n"
                    "bind функції падає, і весь гаджет не піднімається",
                    size=15, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'endpoint-budget.svg'), W, H, *p)


# ── 4. Родовід: потреба → відповідь ────────────────────────────────────────
def fig_gadget_lineage():
    W, H = 1460, 940
    p = []
    p.append(text(440, 46, "потреба, яка штовхала", size=16, bold=True))
    p.append(text(1060, 46, "що з'явилося в ядрі", size=16, bold=True))

    rows = [
        ("2003",
         "залізо вміє бути пристроєм,\nа ядро цього боку шини не знає",
         "каркас gadget і драйвер net2280\nDavid Brownell",
         BLUE_FILL, NEG),
        ("кін. 2003",
         "протоколу нема чого\nробити всередині ядра",
         "gadgetfs: кінцеві точки як файли,\nале забирає весь пристрій собі",
         GREEN_FILL, FIELD),
        ("2008",
         "окремий монолітний модуль\nна КОЖНУ пару функцій",
         "libcomposite: функція — деталь,\nконфігурація — набір деталей",
         BLUE_FILL, NEG),
        ("2010",
         "свій протокол потрібен разом\nіз готовими функціями",
         "FunctionFS: та сама ідея,\nале як ОДНА функція\nMichał Nazarewicz",
         GREEN_FILL, FIELD),
        ("2013",
         "комбінацію все одно обирають\nпри збиранні ядра",
         "складання через configfs,\nмоноліти — у legacy/\nAndrzej Pietrasiewicz",
         WARM_FILL, WARM),
    ]

    y = 80
    for i, (year, need, ans, fill, stroke) in enumerate(rows):
        h = 132
        p.append(fitbox(40, y, 150, h, year, size=17, bold=True,
                        fill=GREY_FILL, stroke=LINE))
        p.append(fitbox(220, y, 500, h, need, size=15,
                        fill=RED_FILL, stroke=POS))
        p.append(arrow(740, y + h / 2, 796, y + h / 2))
        p.append(fitbox(816, y, 580, h, ans, size=15, fill=fill, stroke=stroke))
        if i < len(rows) - 1:
            p.append(arrow(115, y + h + 6, 115, y + h + 38))
        y += h + 44

    render(os.path.join(IMG, 'gadget-lineage.svg'), W, H, *p)


# ── 5. FunctionFS: хто на кого чекає ───────────────────────────────────────
def fig_ffs_handshake():
    W = 1460
    LX, RX, BW = 50, 800, 610
    lc, rc = LX + BW // 2, RX + BW // 2
    p = []

    p.append(text(lc, 40, "демон у просторі користувача", size=17, bold=True))
    p.append(text(rc, 40, "ядро: f_fs і libcomposite", size=17, bold=True))

    steps = [
        ("row", "mount -t functionfs echo /dev/ffs-echo\n-o uid=1000,gid=1000",
         "у точці монтування є єдиний файл ep0", "L"),
        ("row", "write(ep0, дескриптори)\nодним викликом, magic V2",
         "розбирає: інтерфейс і дві bulk-точки", "L"),
        ("row", "write(ep0, рядки)",
         "поруч із ep0 виникають ep1 і ep2", "L"),
        ("band", "поки цих двох записів нема, гаджет не прив'яжеться до контролера:\n"
                 "підтяжки нема, і для хоста роз'єм порожній"),
        ("row", "open(ep1), open(ep2)\nread(ep1) — блокується",
         "echo fe980000.usb > UDC\nприв'язка, підтяжка, хост питає «хто ти»", "L"),
        ("band", "read(ep1) спить у ядрі, доки хост не ввімкне конфігурацію\n"
                 "(з O_NONBLOCK замість сну — EAGAIN, і чекати нема на чому: poll на ep-файлах не працює)"),
        ("row", "read(ep0) віддає подію ENABLE",
         "хост вибрав конфігурацію,\nкінцеві точки ввімкнено", "R"),
        ("row", "read(ep1) повертає дані,\nwrite(ep2) відсилає їх назад",
         "заявки ходять шиною", "R"),
        ("row", "read(ep1) падає з ESHUTDOWN,\nread(ep0) віддає DISABLE",
         "кабель висмикнуто:\nзаявки в польоті скасовано", "R"),
    ]

    y = 74
    for item in steps:
        if item[0] == "band":
            h = 86
            p.append(fitbox(LX, y, RX + BW - LX, h, item[1], size=15,
                            fill=RED_FILL, stroke=POS))
            y += h + 30
            continue
        _, ls, rs, d = item
        h = 96
        p.append(fitbox(LX, y, BW, h, ls, size=15, fill=BLUE_FILL, stroke=NEG))
        p.append(fitbox(RX, y, BW, h, rs, size=15, fill=GREEN_FILL, stroke=FIELD))
        if d == "L":
            p.append(arrow(LX + BW + 14, y + h / 2, RX - 14, y + h / 2))
        else:
            p.append(arrow(RX - 14, y + h / 2, LX + BW + 14, y + h / 2))
        y += h + 30

    p.append(fitbox(LX, y, RX + BW - LX, 86,
                    "файли точок після DISABLE не закривають:\n"
                    "наступний read(ep1) просто засинає до нового ENABLE",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))
    H = y + 86 + 30

    render(os.path.join(IMG, 'ffs-handshake.svg'), W, H, *p)


fig_mirror_stacks()
fig_configfs_to_descriptors()
fig_endpoint_budget()
fig_gadget_lineage()
fig_ffs_handshake()
print("ok")
