# -*- coding: utf-8 -*-
"""Фігури до теми «Прив'язка драйвера до пристрою: probe, збіг за таблицею й відкладена спроба»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ZONE_DEV = "#eef4fb"   # список пристроїв
ZONE_DRV = "#f3f0fa"   # список драйверів
ZONE_A   = "#fdf1ea"   # сліпий перебір
ZONE_B   = "#eff7ef"   # граф із прошивки


def box(cx, cy, s, size=13, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── 1. Шина тримає два списки й точку збігу ─────────────────────────────────
def fig_two_lists():
    W, H = 1120, 540
    f = []

    f.append(rect(40, 60, 300, 340, fill=ZONE_DEV, stroke=MUTED, sw=1.2))
    f.append(text(190, 92, "пристрої на шині", size=14, bold=True))
    devs = [
        (150, "пристрій A\npci:v8086d2723"),
        (225, "пристрій B\nof: bosch,bmp280"),
        (300, "пристрій C\nusb:v0781p5583"),
    ]
    for cy, s in devs:
        f.append(box(190, cy, s, size=12, min_w=250))

    f.append(rect(780, 60, 300, 340, fill=ZONE_DRV, stroke=MUTED, sw=1.2))
    f.append(text(930, 92, "драйвери на шині", size=14, bold=True))
    drvs = [
        (150, "драйвер X\nтаблиця: v8086 d2723"),
        (225, "драйвер Y\nтаблиця: bosch,bmp280"),
        (300, "драйвер Z\nтаблиця: клас 08"),
    ]
    for cy, s in drvs:
        f.append(box(930, cy, s, size=12, min_w=250))

    f.append(box(560, 150, "match() шини", size=14, min_w=290, bold=True))
    f.append(box(560, 240, "звірити опис пристрою\nз кожним рядком таблиці", size=12, min_w=290))
    f.append(box(560, 340, "probe() драйвера", size=13, min_w=290))

    f.append(arrow(348, 150, 408, 150, color=MUTED, sw=1.6))
    f.append(arrow(772, 150, 712, 150, color=MUTED, sw=1.6))
    f.append(arrow(560, 174, 560, 210, color=INK, sw=1.7))
    f.append(arrow(560, 272, 560, 318, color=INK, sw=1.7))

    f.append(box(560, 440, "прив'язано: dev->driver, посилання в /sys, модуль зайнято",
                 size=13, min_w=620, fill="#eef7ee", stroke=FIELD))
    f.append(arrow(560, 362, 560, 415, color=FIELD, sw=1.9))

    f.append(text(560, 500,
                  "будь-яка нова реєстрація — з боку пристрою чи з боку драйвера — "
                  "запускає прохід по протилежному списку",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "two-lists.svg"), W, H, *f,
           title="Збіг шукає шина, порівнюючи опис пристрою з таблицею драйвера")


# ── 2. Що буває після probe ─────────────────────────────────────────────────
def fig_probe_outcomes():
    W, H = 1140, 630
    f = []

    f.append(box(190, 90, "пристрій зареєстровано\nна шині", size=13, min_w=300))
    f.append(box(190, 215, "match: рядок пристрою\nпроти таблиці драйвера", size=13, min_w=300))
    f.append(box(190, 355, "збігу немає —\nпристрій лишається без драйвера", size=12, min_w=320))

    f.append(arrow(190, 120, 190, 186, color=INK, sw=1.7))
    f.append(arrow(190, 244, 190, 326, color=MUTED, sw=1.6))

    f.append(box(530, 213, "probe()", size=14, min_w=200, bold=True))
    f.append(arrow(345, 214, 425, 213, color=INK, sw=1.7))

    outs = [
        (110, "0 — прив'язано:\ndev->driver, посилання в /sys,\nлічильник модуля +1", "#eef7ee", FIELD),
        (280, "−EPROBE_DEFER —\nпристрій у черзі відкладених,\nспробу повторять", "#fdf6e8", "#b8860b"),
        (450, "інша помилка —\nресурси devres прибрано,\nпристрій без драйвера", "#fdefec", POS),
    ]
    for cy, s, fill, stroke in outs:
        f.append(box(900, cy, s, size=12, min_w=380, fill=fill, stroke=stroke))

    f.append(arrow(635, 200, 700, 130, color=FIELD, sw=1.7))
    f.append(arrow(638, 215, 700, 272, color="#b8860b", sw=1.7))
    f.append(arrow(635, 228, 700, 432, color=POS, sw=1.7))

    f.append(box(880, 570, "unbind, вивантаження модуля\nабо зникнення пристрою → remove()",
                 size=12, min_w=380, fill=FILL, stroke=MUTED))
    f.append(line(1090, 110, 1112, 110, color=MUTED, sw=1.4, dash="6,4"))
    f.append(line(1112, 110, 1112, 570, color=MUTED, sw=1.4, dash="6,4"))
    f.append(arrow(1112, 570, 1074, 570, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "probe-outcomes.svg"), W, H, *f,
           title="Три різні наслідки виклику probe і зворотний шлях через remove")


# ── 3. Повторні спроби проти графа, прочитаного наперед ─────────────────────
def fig_defer_vs_links():
    W, H = 1140, 540
    f = []

    f.append(rect(30, 60, 520, 430, fill=ZONE_A, stroke=MUTED, sw=1.2))
    f.append(text(290, 92, "лише повторні спроби", size=14, bold=True))
    left = [
        (140, "модуль дисплея вантажиться першим"),
        (205, "probe → −EPROBE_DEFER: регулятора немає"),
        (270, "те саме після кожної чужої вдалої прив'язки"),
        (335, "модуль регулятора нарешті завантажено"),
        (400, "прохід по черзі → probe дисплея вдається"),
    ]
    for cy, s in left:
        f.append(box(290, cy, s, size=12, min_w=460))
    for i in range(len(left) - 1):
        f.append(arrow(290, left[i][0] + 20, 290, left[i + 1][0] - 20, color=MUTED, sw=1.5))
    f.append(text(290, 460, "ядро не знає, чого чекає — просто пробує знову",
                  size=12, color=MUTED, italic=True))

    f.append(rect(590, 60, 520, 430, fill=ZONE_B, stroke=MUTED, sw=1.2))
    f.append(text(850, 92, "граф, прочитаний з опису прошивки", size=14, bold=True))
    right = [
        (140, "у дереві пристроїв: дисплей посилається на регулятор"),
        (205, "створено зв'язок постачальник → споживач"),
        (270, "probe дисплея не кличуть, доки регулятор не прив'язано"),
        (335, "регулятор прив'язано"),
        (400, "probe дисплея — один раз, успішно"),
    ]
    for cy, s in right:
        f.append(box(850, cy, s, size=12, min_w=460))
    for i in range(len(right) - 1):
        f.append(arrow(850, right[i][0] + 20, 850, right[i + 1][0] - 20, color=MUTED, sw=1.5))
    f.append(text(850, 460, "порядок відомий наперед; повторів майже немає",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "defer-vs-links.svg"), W, H, *f,
           title="Черга відкладених проти зв'язків, побудованих з опису прошивки")


# ── 4. Три знімки /sys на стенді (до вставки proj-probe-driver) ─────────────
def fig_lab_snapshots():
    W, H = 1460, 620
    f = []

    cols = [
        (30, ZONE_A, "після insmod termo.ko",
         [
             ("/sys/devices/platform/termodatchyk/", "посилання driver немає"),
             ("/sys/bus/platform/drivers/termo/", "у списку драйвера порожньо"),
             ("/sys/kernel/debug/devices_deferred", "termodatchyk   немає джерела"),
             ("/sys/class/hwmon/", "жодного пристрою"),
         ],
         "пристрій є, драйвер є — прив'язки немає"),
        (500, ZONE_B, "після insmod dzherelo.ko",
         [
             (".../termodatchyk/driver", "→ .../drivers/termo"),
             (".../drivers/termo/termodatchyk", "→ .../platform/termodatchyk"),
             ("/sys/kernel/debug/devices_deferred", "порожній файл"),
             ("/sys/class/hwmon/hwmon4/temp1_input", "30100"),
         ],
         "прив'язку записано з обох боків"),
        (970, ZONE_DRV, "після echo > .../termo/unbind",
         [
             (".../termodatchyk/driver", "посилання зникло"),
             ("/sys/bus/platform/drivers/termo/", "у списку драйвера порожньо"),
             ("/sys/kernel/debug/devices_deferred", "порожній файл"),
             ("/sys/class/hwmon/", "жодного пристрою"),
         ],
         "той самий вигляд — інша причина"),
    ]

    for x0, zone, head, rows, tail in cols:
        f.append(rect(x0, 60, 460, 500, fill=zone, stroke=MUTED, sw=1.2))
        f.append(text(x0 + 230, 96, head, size=15, bold=True))
        y = 130
        for path, state in rows:
            f.append(fitbox(x0 + 20, y, 420, 82, path + "\n" + state,
                            size=13, fill=BG, stroke=MUTED, sw=1.2))
            y += 96
        f.append(text(x0 + 230, 530, tail, size=13, color=MUTED, italic=True))

    f.append(arrow(492, 300, 498, 300, color=MUTED, sw=1.6))
    f.append(arrow(962, 300, 968, 300, color=MUTED, sw=1.6))

    f.append(text(W / 2, 596,
                  "відкладення й відв'язка дають однаковий вигляд у /sys — "
                  "розрізняє їх лише файл devices_deferred",
                  size=13, color=INK))

    render(os.path.join(OUT, "lab-snapshots.svg"), W, H, *f,
           title="Три знімки /sys: відкладення, прив'язка, ручна відв'язка")


# ── 5. Стрічка часу: як розвʼязували порядок ініціалізації (hist-вставка) ───
def fig_ordering_timeline():
    W, H = 1740, 470
    f = []

    AX = 235
    f.append(line(60, AX, 1680, AX, color=MUTED, sw=2))

    marks = [
        (100, "до 2011", "порядок задають рівні initcall\nі порядок лінкування", ZONE_A, -1),
        (335, "2011", "ARM іде в дерево пристроїв:\nодне ядро на сотні плат", ZONE_A, 1),
        (570, "3.4 · 2012", "−EPROBE_DEFER: драйвер каже\n«ще не можу» і чекає в черзі", ZONE_B, -1),
        (805, "4.10 · 2017", "зв'язки між пристроями:\nпорядок сну й вимкнення", ZONE_DEV, 1),
        (1040, "4.19 · 2018", "deferred_probe_timeout:\nколи припинити чекати", ZONE_DEV, -1),
        (1275, "5.5 · 2020", "зв'язки будують\nз дерева пристроїв", ZONE_B, 1),
        (1510, "5.13 · 2021", "fw_devlink увімкнено типово\n(після відкоту в 5.12)", ZONE_B, -1),
    ]

    for x, when, what, zone, side in marks:
        cy = AX - 125 if side < 0 else AX + 125
        f.append(line(x, AX, x, cy + (58 if side < 0 else -58), color=MUTED, sw=1.2))
        f.append(circle(x, AX, 7, fill=BG, stroke=MUTED, sw=2))
        f.append(box(x, cy, when + "\n" + what, size=12, min_w=205, fill=zone))

    f.append(text(870, 440,
                  "спершу порядок задавали руками, потім навчилися пробувати ще раз, "
                  "далі — читати залежності з опису прошивки",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "ordering-history.svg"), W, H, *f,
           title="Як у Linux розв'язували порядок ініціалізації драйверів")


fig_two_lists()
fig_probe_outcomes()
fig_defer_vs_links()
fig_lab_snapshots()
fig_ordering_timeline()
print("готово:", OUT)
