# -*- coding: utf-8 -*-
"""Фігури до теми «Шина platform»."""

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


# ── 1. Дві дороги до пари «пристрій ↔ драйвер» ──────────────────────────────
def fig_two_roads():
    W, H = 1280, 600
    P = [text(W / 2, 40, "Дві дороги до пари «пристрій ↔ драйвер»", size=18, bold=True)]

    LX, RX, BW = 60, 680, 540

    P.append(fitbox(LX, 70, BW, 52, "ШИНА, ЯКА ВМІЄ ПИТАТИ  —  PCI, USB",
                    size=15, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(RX, 70, BW, 52, "ШИНА, У ЯКОЇ НЕМА КОГО ПИТАТИ  —  platform",
                    size=15, bold=True, fill=RED_BG, stroke=POS, sw=2))

    left = [
        "залізо саме тримає свої ідентифікатори\nу визначеному місці",
        "шина обходить позиції й читає їх:\nвиробник, продукт, клас",
        "збіг — порівняння прочитаних чисел\nіз таблицею драйвера",
    ]
    right = [
        "залізо не має що відповісти:\nє лише адреса й припаяні дроти",
        "хтось ззовні створює ЗАПИС:\nім'я, адреси регістрів, номер лінії",
        "збіг — порівняння рядка із запису\nіз таблицею драйвера",
    ]

    ys = [140, 250, 360]
    for i, y in enumerate(ys):
        P.append(fitbox(LX, y, BW, 84, left[i], size=14, fill=GREY_BG))
        P.append(fitbox(RX, y, BW, 84, right[i], size=14, fill=WARM_BG))
        if i < 2:
            P.append(arrow(LX + BW / 2, y + 84, LX + BW / 2, ys[i + 1] - 2))
            P.append(arrow(RX + BW / 2, y + 84, RX + BW / 2, ys[i + 1] - 2))

    P.append(fitbox(330, 500, 620, 64,
                    "далі — та сама дорога: probe(), sysfs, живлення, вивантаження",
                    size=15, bold=True, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(arrow(LX + BW / 2, 444, 520, 498))
    P.append(arrow(RX + BW / 2, 444, 760, 498))
    return render(os.path.join(OUT, "two-roads.svg"), W, H, *P)


# ── 2. Хто створює платформні пристрої ──────────────────────────────────────
def fig_who_creates():
    W, H = 1340, 660
    P = [text(W / 2, 40, "Платформний пристрій не знаходять — його створюють", size=18, bold=True)]

    SX, SW = 50, 430
    sources = [
        "ДЕРЕВО ПРИСТРОЇВ\nof_platform_default_populate() обходить\nвузли з compatible",
        "ТАБЛИЦІ ACPI\nоб'єкти простору імен, для яких\nнема спеціальнішої шини",
        "КОД ПЛАТИ В ЯДРІ\nplatform_device_register() з готовим\nмасивом ресурсів",
        "ІНШИЙ ДРАЙВЕР\nбагатофункційна мікросхема заводить\nдіти на свої блоки",
        "ЧИСТО ПРОГРАМНА РІЧ\nзапис без заліза — щоб дістати\nprobe(), sysfs і живлення",
    ]
    ys = [90, 196, 302, 408, 514]
    for i, y in enumerate(ys):
        P.append(fitbox(SX, y, SW, 88, sources[i], size=13, fill=WARM_BG))
        P.append(arrow(SX + SW, y + 44, 610, y + 44))

    P.append(rect(610, 90, 250, 512, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(mtext(735, 130, ["ШИНА platform", "перелік записів"], size=15, bold=True))
    P.append(mtext(735, 210,
                   ["serial.0", "e0001000.serial", "gpio-keys.0", "reg-dummy",
                    "…рівно те, що", "їй розповіли"], size=13, color=MUTED))

    P.append(text(1075, 300, "platform_match()", size=14, bold=True))
    P.append(arrow(860, 340, 1290, 340))
    P.append(arrow(1290, 380, 860, 380))

    P.append(fitbox(890, 430, 400, 100,
                    "ДРАЙВЕРИ\nвбудовані й завантажені модулями,\nз таблицею compatible або імен",
                    size=13, fill=BLUE_BG, stroke=NEG))

    return render(os.path.join(OUT, "who-creates.svg"), W, H, *P)


# ── 3. Що з опису стає чим у записі ─────────────────────────────────────────
def fig_props_to_resources():
    W, H = 1300, 620
    P = [text(W / 2, 40, "Властивість опису → поле запису → те, що бере probe()",
              size=18, bold=True)]

    LX, LW = 60, 440
    RX, RW = 780, 460

    P.append(fitbox(LX, 70, LW, 46, "у вузлі дерева пристроїв", size=15, bold=True,
                    fill=GREY_BG, stroke=MUTED))
    P.append(fitbox(RX, 70, RW, 46, "у платформному пристрої", size=15, bold=True,
                    fill=GREEN_BG, stroke=FIELD))

    pairs = [
        ("compatible =\n\"acme,myuart-r1p2\"",
         "of_node → рядок, за яким\nшукається збіг із драйвером"),
        ("reg = <0xe0001000 0x1000>",
         "resource[0], IORESOURCE_MEM →\ndevm_platform_ioremap_resource()"),
        ("interrupts = <0 59 4>",
         "resource[1], IORESOURCE_IRQ →\nplatform_get_irq() після мапування"),
        ("clocks = <&clkc 24>",
         "лишається у вузлі: драйвер бере\nйого сам, уже в probe()"),
    ]
    ys = [140, 232, 324, 416]
    for i, y in enumerate(ys):
        P.append(fitbox(LX, y, LW, 76, pairs[i][0], size=13, fill=WARM_BG))
        P.append(fitbox(RX, y, RW, 76, pairs[i][1], size=13, fill=BLUE_BG))
        P.append(arrow(LX + LW + 10, y + 38, RX - 10, y + 38))

    P.append(fitbox(60, 520, 1180, 66,
                    "жодне з цих чисел ядро не перевіряло: усі вони прийшли ззовні, "
                    "з документації на мікросхему",
                    size=14, bold=True, fill=RED_BG, stroke=POS, sw=2))
    return render(os.path.join(OUT, "props-to-resources.svg"), W, H, *P)


# ── 4. Поверхня дослідів у /sys (до вставки proj-platform-driver) ───────────
def fig_probe_playground():
    W, H = 1320, 650
    P = [text(W / 2, 38, "Поверхня дослідів: де в /sys видно кожен крок", size=18, bold=True)]

    LX, LW = 60, 470
    RX, RW = 790, 470

    P.append(fitbox(LX, 70, LW, 50, "ЗАПИС ПРО ПРИСТРІЙ", size=15, bold=True,
                    fill=WARM_BG, stroke=POS, sw=2))
    P.append(fitbox(RX, 70, RW, 50, "ДРАЙВЕР", size=15, bold=True,
                    fill=BLUE_BG, stroke=NEG, sw=2))

    P.append(fitbox(LX, 128, LW, 44, "/sys/bus/platform/devices/myuart.0/",
                    size=13, fill=GREY_BG, stroke=MUTED))
    P.append(fitbox(RX, 128, RW, 44, "/sys/bus/platform/drivers/myuart/",
                    size=13, fill=GREY_BG, stroke=MUTED))

    left = [
        "modalias — рядок, за яким udev шукає модуль",
        "driver_override — «тільки цей драйвер»",
        "driver → посилання на прив'язаний драйвер",
        "power/ — місце в порядку засинання",
    ]
    right = [
        "unbind — вписати ім'я: зняти прив'язку",
        "bind — вписати те саме ім'я: покликати probe()",
        "myuart.0 → посилання на прив'язаний пристрій",
        "uevent — перевидати подію для udev",
    ]
    ys = [186, 248, 310, 372]
    for i, y in enumerate(ys):
        P.append(fitbox(LX, y, LW, 54, left[i], size=13))
        P.append(fitbox(RX, y, RW, 54, right[i], size=13))

    P.append(mtext(660, 268, ["прив'язка —", "пара посилань"], size=14, bold=True, color=MUTED))
    P.append(arrow(540, 330, 780, 330))
    P.append(arrow(780, 366, 540, 366))

    P.append(fitbox(60, 452, 1200, 62,
                    "нема запису в devices/ → біда в описі  ·  запис є, посилань нема "
                    "→ не зійшовся compatible або ім'я",
                    size=14, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(fitbox(60, 538, 1200, 78,
                    "/sys/kernel/debug/devices_deferred — сюди потрапляє той, чий probe() "
                    "повернув -EPROBE_DEFER:\nпристрій живий, драйвер знайдено, спробу "
                    "відкладено до появи того, чого бракує",
                    size=14, fill=BLUE_BG, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "probe-playground.svg"), W, H, *P)


if __name__ == "__main__":
    print(fig_two_roads())
    print(fig_who_creates())
    print(fig_props_to_resources())
    print(fig_probe_playground())
