# -*- coding: utf-8 -*-
"""Фігури до теми «Дерево пристроїв»."""

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


# ── 1. Дві машини: та, що відповідає, і та, що мовчить ──────────────────────
def fig_two_worlds():
    W, H = 1360, 640
    P = [text(W / 2, 40, "Дві шини: одна відповідає на запитання, друга мовчить",
              size=18, bold=True)]

    LX, RX, BW = 60, 720, 580

    P.append(fitbox(LX, 72, BW, 56, "ШИНА ВМІЄ ВІДПОВІДАТИ  —  PCI, USB",
                    size=15, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(RX, 72, BW, 56, "СПИТАТИ НЕМА КОГО  —  I²C, SPI, регістри SoC",
                    size=15, bold=True, fill=RED_BG, stroke=POS, sw=2))

    left = [
        "у кожного учасника є визначене місце,\nде лежить його самоопис",
        "ядро читає ідентифікатори виробника,\nпродукту й класу — і впізнає пристрій",
        "запитання безпечне: коли за адресою\nнікого нема, шина каже про це сама",
    ]
    right = [
        "на двох дротах є лише адреса;\nвідповідь «є» не каже, ХТО там є",
        "звертання за адресою для багатьох\nмікросхем — команда, а не запитання",
        "припаяний до SoC контролер узагалі\nне на шині: просто регістри за адресою",
    ]

    y = 160
    for i in range(3):
        P.append(fitbox(LX, y, BW, 96, left[i], size=14.5, fill=BLUE_BG, stroke=NEG, sw=1.6))
        P.append(fitbox(RX, y, BW, 96, right[i], size=14.5, fill=GREY_BG, stroke=MUTED, sw=1.6))
        if i < 2:
            P.append(arrow(LX + BW / 2, y + 96, LX + BW / 2, y + 128, color=NEG))
            P.append(arrow(RX + BW / 2, y + 96, RX + BW / 2, y + 128, color=MUTED))
        y += 128

    P.append(arrow(RX + BW / 2, 544, 830, 574, color=POS, sw=2.2))
    P.append(fitbox(300, 576, 760, 56,
                    "опис мусить прийти ЗЗОВНІ — окремими даними",
                    size=16, bold=True, fill=WARM_BG, stroke=GOLD, sw=2))
    render(os.path.join(OUT, "two-worlds.svg"), W, H, *P)


# ── 2. Шлях блоба від тексту до probe() ─────────────────────────────────────
def fig_blob_path():
    W, H = 1400, 660
    P = [text(W / 2, 40, "Шлях опису: від тексту на диску до probe() драйвера",
              size=18, bold=True)]

    XS = [40, 385, 730, 1075]
    BW, BH = 285, 110

    row1 = [
        (".dts і .dtsi\nтекстовий опис\nSoC та плати", GREY_BG, MUTED),
        ("dtc\nкомпілятор\nдерева", GREY_BG, MUTED),
        (".dtb — плаский блоб:\nсамі зміщення,\nжодного вказівника", WARM_BG, GOLD),
        ("завантажувач кладе блоб\nу пам'ять і передає ядру\nйого фізичну адресу", WARM_BG, GOLD),
    ]
    row2 = [
        ("of_platform_populate():\nкожен вузол верхнього рівня\nстає platform_device", GREEN_BG, FIELD),
        ("unflatten_device_tree():\nблоб → дерево вузлів\nstruct device_node у пам'яті", BLUE_BG, NEG),
        ("ранній скан плаского блоба:\n/memory — де і скільки RAM\n/chosen — bootargs, initrd", BLUE_BG, NEG),
        ("ядро отримало адресу\nблоба ще до того, як має\nалокатор пам'яті", BLUE_BG, NEG),
    ]

    Y1, Y2 = 100, 320
    for i, (s, fill, stroke) in enumerate(row1):
        P.append(fitbox(XS[i], Y1, BW, BH, s, size=14, fill=fill, stroke=stroke, sw=1.8))
        if i < 3:
            P.append(arrow(XS[i] + BW, Y1 + BH / 2, XS[i + 1], Y1 + BH / 2))
    for i, (s, fill, stroke) in enumerate(row2):
        P.append(fitbox(XS[i], Y2, BW, BH, s, size=14, fill=fill, stroke=stroke, sw=1.8))
        if i > 0:
            P.append(arrow(XS[i], Y2 + BH / 2, XS[i - 1] + BW, Y2 + BH / 2))
    P.append(arrow(XS[3] + BW / 2, Y1 + BH, XS[3] + BW / 2, Y2))

    P.append(arrow(XS[0] + BW / 2, Y2 + BH, XS[0] + BW / 2, 470))
    P.append(fitbox(40, 472, 640, 78,
                    "рядок compatible вузла збігається з of_match_table\nдрайвера → ядро кличе його probe()",
                    size=14.5, fill=GREEN_BG, stroke=FIELD, sw=1.8))
    P.append(arrow(680, 511, 748, 511))
    P.append(fitbox(750, 472, 610, 78,
                    "/sys/firmware/devicetree/base — саме дерево;\n/sys/devices/… — вузли, яким знайшовся драйвер",
                    size=14.5, fill=GREY_BG, stroke=MUTED, sw=1.8))
    render(os.path.join(OUT, "blob-path.svg"), W, H, *P)


# ── 3. Посилання між вузлами: дерево за формою, граф за змістом ─────────────
def fig_phandles():
    W, H = 1360, 620
    P = [text(W / 2, 40, "Посилання роблять із дерева граф — і забирають порядок",
              size=18, bold=True)]

    P.append(fitbox(50, 210, 300, 130,
                    "вузол датчика\ncompatible = \"ti,tmp102\"\nreg = <0x48>",
                    size=14.5, fill=WARM_BG, stroke=GOLD, sw=2))

    props = [
        ("clocks = <&clkc 38>", "вузол контролера тактів\n#clock-cells = <1>"),
        ("vcc-supply = <&supply>", "вузол регулятора живлення"),
        ("interrupt-parent = <&gpio7>\ninterrupts = <16 ...>", "вузол контролера GPIO\n#interrupt-cells = <2>"),
    ]
    ys = [90, 235, 380]
    for i, (label, target) in enumerate(props):
        y = ys[i]
        P.append(fitbox(430, y, 340, 88, label, size=13.5, fill=GREY_BG, stroke=MUTED, sw=1.5))
        P.append(fitbox(870, y, 440, 88, target, size=14, fill=BLUE_BG, stroke=NEG, sw=1.8))
        P.append(arrow(352, 275, 424, y + 44, color=GOLD))
        P.append(arrow(772, y + 44, 864, y + 44, color=NEG))

    P.append(fitbox(120, 505, 1120, 84,
                    "будь-якого з трьох може ще не бути на світі, коли ядро кличе probe() датчика:\n"
                    "драйвер повертає -EPROBE_DEFER, і ядро вертається до нього після кожного нового драйвера",
                    size=15, fill=RED_BG, stroke=POS, sw=2))
    render(os.path.join(OUT, "phandles.svg"), W, H, *P)


# ── 4. Ланцюг слідів: де саме рветься шлях від накладки до градусів ─────────
def fig_probe_ladder():
    W, H = 1460, 840
    P = [text(W / 2, 40, "Від накладки до градусів: п'ять слідів і місця розриву",
              size=18, bold=True)]

    LX, LW = 50, 520
    RX, RW = 700, 700

    P.append(fitbox(LX, 70, LW, 46, "ЛАНКА — ДЕ МАЄ З'ЯВИТИСЯ СЛІД",
                    size=14.5, bold=True, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(fitbox(RX, 70, RW, 46, "ЯК РВЕТЬСЯ І ЧИМ ЦЕ ВИДНО",
                    size=14.5, bold=True, fill=RED_BG, stroke=POS, sw=2))

    rows = [
        ("вузол у дереві ядра\n/proc/device-tree/…/sensor@48",
         "накладка не лягла: у базовому дереві нема __symbols__\n"
         "або мітку перейменували → fdt apply віддає помилку,\n"
         "of_overlay_fdt_apply — EINVAL"),
        ("клієнт на шині\n/sys/bus/i2c/devices/1-0048",
         "шина сама має status = \"disabled\", або адресу вже\n"
         "тримає інший клієнт → у dmesg\n"
         "«Failed to register i2c client … at 0x48 (-16)»"),
        ("прив'язка драйвера\n…/1-0048/driver → tmp102",
         "під рядок compatible нема коду — і в журналі\n"
         "ЖОДНОГО слова; шукай of:N*T*Cti,tmp102\n"
         "у /lib/modules/$(uname -r)/modules.alias"),
        ("probe() дійшов до кінця\n(мовчання = добре)",
         "-EPROBE_DEFER без кінця: ресурс із посилання\n"
         "(vcc-supply, такт, GPIO) так і не зареєстровано →\n"
         "ім'я й причина в /sys/kernel/debug/devices_deferred"),
    ]

    Y, BH, STEP = 140, 118, 148
    for i, (left, right) in enumerate(rows):
        y = Y + i * STEP
        P.append(fitbox(LX, y, LW, BH, left, size=14.5, fill=GREY_BG, stroke=MUTED, sw=1.8))
        P.append(fitbox(RX, y, RW, BH, right, size=13.5, fill=RED_BG, stroke=POS, sw=1.6))
        P.append(arrow(LX + LW, y + BH / 2, RX, y + BH / 2, color=POS, sw=1.6))
        P.append(arrow(LX + LW / 2, y + BH, LX + LW / 2, y + STEP, color=NEG, sw=2))

    y = Y + 4 * STEP
    P.append(fitbox(LX, y, LW, BH, "значення\n/sys/class/hwmon/hwmonN/temp1_input",
                    size=14.5, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(RX, y, RW, BH,
                    "число в тисячних градуса Цельсія:\n42125 → 42.125 °C\n"
                    "дійшли сюди — договір «опис ↔ драйвер» зійшовся",
                    size=13.5, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    render(os.path.join(OUT, "probe-ladder.svg"), W, H, *P)


# ── 5. Блок структури .dtb побайтово ───────────────────────────────────────
def fig_dtb_bytes():
    W, H = 1400, 660
    P = [text(W / 2, 36, "Вузол sensor@48 у блоці структури: самі токени, довжини й зміщення",
              size=18, bold=True)]

    HX, HW = 40, 330
    MX, MW = 390, 470
    SX, SW = 940, 420

    P.append(fitbox(HX, 66, HW + 20 + MW, 36, "БЛОК СТРУКТУРИ  (off_dt_struct)",
                    size=14.5, bold=True, fill=GREY_BG, stroke=MUTED, sw=1.6))
    P.append(fitbox(SX, 66, SW, 36, "БЛОК РЯДКІВ  (off_dt_strings)",
                    size=14.5, bold=True, fill=WARM_BG, stroke=GOLD, sw=1.6))

    rows = [
        ("00 00 00 01", "FDT_BEGIN_NODE — починається вузол"),
        ("73 65 6e 73 6f 72 40 34 38 00 00 00",
         "ім'я «sensor@48» з нулем у кінці,\nдоповнене до кратності 4 байтів"),
        ("00 00 00 03", "FDT_PROP — починається властивість"),
        ("00 00 00 0a", "довжина значення: 10 байтів"),
        ("00 00 00 24", "зміщення ІМЕНІ властивості в блоці рядків"),
        ("74 69 2c 74 6d 70 31 30 32 00 00 00", "значення «ti,tmp102», теж доповнене до 4"),
        ("00 00 00 03   00 00 00 04   00 00 00 2f",
         "друга властивість: тег, довжина 4, зміщення імені"),
        ("00 00 00 48", "значення reg = <0x48> — одна комірка"),
        ("00 00 00 02", "FDT_END_NODE — вузол скінчився"),
        ("00 00 00 09", "FDT_END — блок структури скінчився"),
    ]

    Y0, STEP, BH = 120, 48, 40
    for i, (hx, meaning) in enumerate(rows):
        y = Y0 + i * STEP
        P.append(fitbox(HX, y, HW, BH, hx, size=13, fill=GREY_BG, stroke=MUTED, sw=1.4))
        P.append(fitbox(MX, y, MW, BH, meaning, size=13, fill=BLUE_BG, stroke=NEG, sw=1.4))

    P.append(fitbox(SX, 250, SW, 56, "0x24  →  «compatible» з нулем",
                    size=14.5, fill=WARM_BG, stroke=GOLD, sw=1.8))
    P.append(fitbox(SX, 380, SW, 56, "0x2f  →  «reg» з нулем",
                    size=14.5, fill=WARM_BG, stroke=GOLD, sw=1.8))
    P.append(fitbox(SX, 486, SW, 96,
                    "кожне ім'я властивості лежить тут\nрівно один раз — у блоці структури\nвід нього лишається саме зміщення",
                    size=13.5, fill=GREEN_BG, stroke=FIELD, sw=1.6))

    c4 = Y0 + 4 * STEP + BH / 2
    c6 = Y0 + 6 * STEP + BH / 2
    P.append(arrow(MX + MW + 6, c4, SX - 6, 278, color=GOLD, sw=2))
    P.append(arrow(MX + MW + 6, c6, SX - 6, 408, color=GOLD, sw=2))

    render(os.path.join(OUT, "dtb-bytes.svg"), W, H, *P)


fig_two_worlds()
fig_blob_path()
fig_phandles()
fig_probe_ladder()
fig_dtb_bytes()
print("ok")
