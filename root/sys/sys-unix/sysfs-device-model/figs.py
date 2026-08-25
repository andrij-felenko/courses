# -*- coding: utf-8 -*-
"""Фігури до теми «Модель пристроїв у sysfs»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG = "#eaf0fd"
GREEN_BG = "#e6f5ec"
WARM_BG = "#fff4e0"
GREY_BG = "#eef0f3"
RED_BG = "#fdecea"
GOLD = "#b8860b"


# ── 1. Пристрій, шина, драйвер ──────────────────────────────────────────────
def fig_bind():
    W, H = 1300, 640
    P = []
    P.append(text(W / 2, 40, "Пристрій і драйвер не знають один про одного — знає шина",
                  size=17, bold=True))

    P.append(fitbox(60, 90, 340, 180,
                    "ПРИСТРІЙ  (struct device)\n\n"
                    "ім'я й ознаки для впізнання\n"
                    "вказівник на батька в дереві\n"
                    "стан живлення\n"
                    "хто ним керує (поки ніхто)",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))

    P.append(fitbox(480, 90, 340, 180,
                    "ШИНА  (struct bus_type)\n\n"
                    "перелічити, що на ній є\n"
                    "порівняти ознаки з таблицями\n"
                    "покликати probe() у драйвера",
                    size=13.5, fill=WARM_BG, stroke=GOLD, sw=2))

    P.append(fitbox(900, 90, 340, 180,
                    "ДРАЙВЕР  (device_driver)\n\n"
                    "таблиця ознак: що вміє\n"
                    "probe() — узяти пристрій\n"
                    "remove() — віддати пристрій",
                    size=13.5, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(arrow(400, 180, 476, 180, color=NEG))
    P.append(arrow(900, 180, 824, 180, color=FIELD))
    P.append(text(438, 158, "реєстрація", size=12, color=MUTED))
    P.append(text(862, 158, "реєстрація", size=12, color=MUTED))

    P.append(arrow(650, 274, 650, 340, color=GOLD))
    P.append(fitbox(330, 340, 640, 110,
                    "збіг ознак → шина кличе probe() → пристрій прив'язано\n"
                    "probe відмовився → вузол лишається в дереві без драйвера",
                    size=13.5, fill=GREY_BG, stroke=INK, sw=2))

    P.append(fitbox(60, 490, 1180, 110,
                    "слід прив'язки, видимий ззовні:\n"
                    "/sys/devices/…/1-2:1.0/driver  →  посилання на драйвер\n"
                    "/sys/bus/usb/drivers/usb-storage/1-2:1.0  →  посилання назад на пристрій",
                    size=13, fill=BG, stroke=MUTED, sw=2))

    render(os.path.join(OUT, "device-bus-driver.svg"), W, H, *P)


# ── 2. Три входи в одне дерево ──────────────────────────────────────────────
def fig_views():
    W, H = 1420, 800
    P = []
    P.append(text(W / 2, 40, "Одне дерево, три входи: канонічний шлях і два набори посилань",
                  size=17, bold=True))

    P.append(text(300, 82, "/sys/devices — фізичне під'єднання", size=14, bold=True, color=INK))

    nodes = [
        "pci0000:00  —  корінь шини PCI",
        "0000:00:14.0  —  контролер USB",
        "usb1  —  кореневий концентратор",
        "1-2  —  флешка на другому порту",
        "1-2:1.0  —  інтерфейс накопичувача",
        "host4  —  SCSI-хост",
        "4:0:0:0  —  диск на цьому хості",
        "block/sdb  —  блоковий пристрій",
    ]
    X, Wb, Hb, STEP, Y0 = 80, 440, 58, 86, 104
    for i, s in enumerate(nodes):
        y = Y0 + i * STEP
        fill = GREEN_BG if i in (3, 7) else GREY_BG
        stroke = FIELD if i in (3, 7) else MUTED
        P.append(fitbox(X, y, Wb, Hb, s, size=13.5, fill=fill, stroke=stroke, sw=2))
        if i < len(nodes) - 1:
            P.append(arrow(X + Wb / 2, y + Hb, X + Wb / 2, y + STEP - 2, color=MUTED))

    P.append(text(1060, 240, "додаткові входи", size=14, bold=True, color=NEG))

    P.append(fitbox(800, 268, 560, 96,
                    "/sys/bus/usb/devices/1-2\n"
                    "плаский список усього на цій шині",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(fitbox(800, 580, 560, 96,
                    "/sys/class/block/sdb\n"
                    "згруповано за тим, ЩО пристрій робить",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))

    y3 = Y0 + 3 * STEP + Hb / 2
    y7 = Y0 + 7 * STEP + Hb / 2
    P.append(arrow(796, 316, X + Wb + 6, y3, color=NEG))
    P.append(arrow(796, 628, X + Wb + 6, y7, color=NEG))
    P.append(text(660, 300, "символьне", size=12, color=NEG))
    P.append(text(660, 318, "посилання", size=12, color=NEG))
    P.append(text(660, 612, "символьне", size=12, color=NEG))
    P.append(text(660, 630, "посилання", size=12, color=NEG))

    P.append(fitbox(800, 400, 560, 130,
                    "той самий каталог має кілька шляхів\n"
                    "і рівно один справжній — тому пристрої\n"
                    "порівнюють за розкритим шляхом,\n"
                    "а не за рядком, яким до нього прийшли",
                    size=13, fill=BG, stroke=MUTED, sw=2))

    render(os.path.join(OUT, "sysfs-three-views.svg"), W, H, *P)


# ── 3. Шлях події від заліза до /dev ────────────────────────────────────────
def fig_hotplug():
    W, H = 1400, 800
    P = []
    P.append(text(W / 2, 40, "Від встромленого заліза до файлу в /dev", size=17, bold=True))

    steps = [
        ("На шині з'явився новий учасник",
         "контролер USB помічає зміну на порту\nй будить драйвер шини", WARM_BG, GOLD),
        ("Драйвер шини читає ідентифікатори",
         "дескриптори USB чи конфігураційний простір PCI;\nна шинах, що себе не називають, — опис від прошивки", WARM_BG, GOLD),
        ("Вузол стає на місце в дереві",
         "батько — те, у що фізично встромлено;\nу /sys виникає каталог із файлами-атрибутами", GREEN_BG, FIELD),
        ("Ядро розсилає подію широкомовно",
         "add, шлях у дереві, підсистема, modalias,\nстарший і молодший номери — через netlink", BLUE_BG, NEG),
        ("У /dev з'являється файл, далі — політика",
         "devtmpfs робить вузол за номерами одразу;\nudev ставить права й стійкі імена by-uuid", BLUE_BG, NEG),
        ("Аж тепер шина добирає драйвер",
         "udev міг щойно підвантажити модуль за modalias;\nзбіг → probe(), нема збігу → вузол без драйвера", GREEN_BG, FIELD),
    ]

    X, Wb, Hb, STEP, Y0 = 70, 560, 92, 112, 90
    for i, (left, right, bg, st) in enumerate(steps):
        y = Y0 + i * STEP
        P.append(fitbox(X, y, Wb, Hb, left, size=14, fill=bg, stroke=st, sw=2, bold=True))
        P.append(fitbox(720, y, 610, Hb, right, size=13, fill=BG, stroke=MUTED, sw=2))
        if i < len(steps) - 1:
            P.append(arrow(X + Wb / 2, y + Hb, X + Wb / 2, y + STEP - 2, color=st))

    P.append(text(W / 2, 760,
                  "ядро доводить справу до вузла з номерами; ім'я та права — вже простір користувача",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "hotplug-path.svg"), W, H, *P)


# ── 4. Атрибут і подія: хто раніше ──────────────────────────────────────────
def fig_attr_uevent():
    W, H = 1420, 800
    P = []
    P.append(text(W / 2, 40, "Подія розсилається один раз — усе, що має побачити udev, мусить існувати до неї",
                  size=17, bold=True))

    XL, XR, Wb, Hb, STEP, Y0 = 60, 760, 600, 76, 96, 118
    P.append(text(XL + Wb / 2, 88, "атрибут доданий після реєстрації",
                  size=14.5, bold=True, color=POS))
    P.append(text(XR + Wb / 2, 88, "атрибути описані в групі наперед",
                  size=14.5, bold=True, color=FIELD))

    left = [
        ("class_register() — клас зареєстровано", GREY_BG, MUTED),
        ("device_create() — каталог пристрою створено", GREY_BG, MUTED),
        ("ядро розсилає подію add", WARM_BG, GOLD),
        ("udev виконує правила: ATTR{brightness} — файлу ще нема", RED_BG, POS),
        ("device_create_file() — файл нарешті з'явився", GREY_BG, MUTED),
    ]
    right = [
        ("ATTRIBUTE_GROUPS(lamp) — атрибути описані статично", GREY_BG, MUTED),
        ("lamp_class.dev_groups = lamp_groups", GREY_BG, MUTED),
        ("device_create() — каталог І всі файли групи разом", GREEN_BG, FIELD),
        ("ядро розсилає подію add", WARM_BG, GOLD),
        ("udev виконує правила: ATTR{brightness} читається", GREEN_BG, FIELD),
    ]

    for X, steps in ((XL, left), (XR, right)):
        for i, (s, bg, st) in enumerate(steps):
            y = Y0 + i * STEP
            P.append(fitbox(X, y, Wb, Hb, s, size=13.5, fill=bg, stroke=st, sw=2))
            if i < len(steps) - 1:
                P.append(arrow(X + Wb / 2, y + Hb, X + Wb / 2, y + STEP - 2, color=MUTED))

    YR = Y0 + len(left) * STEP + 24
    P.append(fitbox(XL, YR, Wb, 104,
                    "у /sys файл є, у правило він не потрапив;\n"
                    "другої події ядро саме не надішле",
                    size=13.5, fill=RED_BG, stroke=POS, sw=2))
    P.append(fitbox(XR, YR, Wb, 104,
                    "правило бачить готовий пристрій —\n"
                    "і при першій появі, і при переграванні події",
                    size=13.5, fill=GREEN_BG, stroke=FIELD, sw=2))

    render(os.path.join(OUT, "attr-uevent-order.svg"), W, H, *P)


if __name__ == "__main__":
    fig_bind()
    fig_views()
    fig_hotplug()
    fig_attr_uevent()
    print("ok")
