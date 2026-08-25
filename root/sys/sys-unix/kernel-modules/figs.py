# -*- coding: utf-8 -*-
"""Фігури до теми «Модулі ядра: завантаження, параметри, залежності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ZONE_U = "#eef4fb"   # простір користувача
ZONE_K = "#fdf1ea"   # ядро
DATA   = "#f2f7ef"   # покажчики на диску


def box(cx, cy, s, size=13, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── 1. Поділ праці: хто шукає, а хто лінкує ─────────────────────────────────
def fig_link_vs_search():
    W, H = 1060, 540
    f = []

    f.append(rect(30, 56, 460, 384, fill=ZONE_U, stroke=MUTED, sw=1.2))
    f.append(text(260, 84, "простір користувача — modprobe", size=15, bold=True))

    left = [
        (128, "прийняти назву або рядок аліаса"),
        (196, "знайти модуль у modules.alias"),
        (264, "розкрити залежності за modules.dep"),
        (332, "додати options з /etc/modprobe.d"),
        (400, "відкрити .ko і подати дескриптор"),
    ]
    for cy, s in left:
        f.append(box(260, cy, s, size=13, min_w=400))
    for i in range(len(left) - 1):
        f.append(arrow(260, left[i][0] + 21, 260, left[i + 1][0] - 21, color=MUTED, sw=1.4))

    f.append(rect(600, 56, 430, 384, fill=ZONE_K, stroke=MUTED, sw=1.2))
    f.append(text(815, 84, "ядро — finit_module", size=15, bold=True))

    right = [
        (124, "перевірити підпис"),
        (182, "звірити vermagic"),
        (240, "виділити пам'ять у ядрі"),
        (298, "розв'язати символи по таблиці експорту"),
        (356, "застосувати релокації"),
        (414, "покликати функцію ініціалізації"),
    ]
    for cy, s in right:
        f.append(box(815, cy, s, size=12, min_w=370))

    f.append(line(545, 70, 545, 400, color=POS, sw=3))
    f.append(arrow(492, 462, 598, 462, color=INK, sw=2))
    f.append(text(545, 500, "дескриптор файлу + рядок параметрів", size=13, color=MUTED))

    f.append(text(260, 462, "шукає й упорядковує", size=13, color=MUTED, italic=True))
    f.append(text(815, 462, "лінкує — і більше нічого", size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "link-vs-search.svg"), W, H, *f,
           title="Завантаження модуля: розумна частина зовні, лінкувальник усередині")


# ── 2. Залежності, лічильник тримачів і порядок ─────────────────────────────
def fig_deps():
    W, H = 1140, 490
    f = []

    f.append(box(570,  86, "iwlmvm\nтримачів: 0", size=13, min_w=320))
    f.append(box(400, 206, "mac80211\nтримачів: 1 — iwlmvm", size=13, min_w=290))
    f.append(box(740, 206, "iwlwifi\nтримачів: 1 — iwlmvm", size=13, min_w=290))
    f.append(box(570, 326, "cfg80211\nтримачів: 3 — iwlmvm, iwlwifi, mac80211",
                 size=13, min_w=420))

    # «потребує символи» — від споживача до постачальника
    f.append(arrow(525, 116, 445, 176, color=INK, sw=1.8))
    f.append(arrow(615, 116, 695, 176, color=INK, sw=1.8))
    f.append(arrow(420, 236, 500, 296, color=INK, sw=1.8))
    f.append(arrow(700, 236, 620, 296, color=INK, sw=1.8))

    # пряме ребро iwlmvm → cfg80211, обведене ліворуч
    f.append(line(405, 86, 215, 86, color=INK, sw=1.8))
    f.append(line(215, 86, 215, 326, color=INK, sw=1.8))
    f.append(arrow(215, 326, 355, 326, color=INK, sw=1.8))

    f.append(text(570, 266, "потребує символи", size=12, color=MUTED, italic=True))

    f.append(text(100, 64, "порядок завантаження", size=13, bold=True))
    f.append(arrow(100, 356, 100, 96, color=NEG, sw=2))
    for cy, n in ((326, "1"), (206, "2"), (86, "3")):
        f.append(text(128, cy + 5, n, size=14, color=NEG, bold=True, anchor="start"))

    f.append(text(1040, 64, "порядок вивантаження", size=13, bold=True))
    f.append(arrow(1040, 96, 1040, 356, color=POS, sw=2))
    for cy, n in ((86, "1"), (206, "2"), (326, "3")):
        f.append(text(1012, cy + 5, n, size=14, color=POS, bold=True, anchor="end"))

    f.append(text(570, 424, "поки лічильник тримачів не нульовий, rmmod відмовляє",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "deps.svg"), W, H, *f,
           title="Символи задають граф, граф задає обидва порядки")


# ── 3. Аліас складають з двох боків і зводять ───────────────────────────────
def fig_autoload():
    W, H = 1120, 590
    f = []

    left = [
        (96,  "сирці драйвера:\nMODULE_DEVICE_TABLE(pci, …)"),
        (194, "секція .modinfo у .ko:\nalias=pci:v00008086d00002723…"),
        (292, "depmod складає\nmodules.alias"),
    ]
    right = [
        (96,  "пристрій на шині:\nvendor 8086, device 2723"),
        (194, "sysfs, файл modalias:\npci:v00008086d00002723…"),
        (292, "подія uevent → правило udev"),
    ]

    for cy, s in left:
        f.append(box(258, cy, s, size=12, min_w=390, fill=DATA))
    for cy, s in right:
        f.append(box(862, cy, s, size=12, min_w=390, fill=ZONE_U))

    for col, cx in ((left, 258), (right, 862)):
        for i in range(len(col) - 1):
            f.append(arrow(cx, col[i][0] + 32, cx, col[i + 1][0] - 32, color=MUTED, sw=1.4))

    f.append(text(258, 58, "з боку драйвера", size=14, bold=True))
    f.append(text(862, 58, "з боку пристрою", size=14, bold=True))

    f.append(box(560, 386, "modprobe: рядки збіглися → назва модуля", size=13, min_w=470))
    f.append(arrow(300, 326, 470, 366, color=INK, sw=1.8))
    f.append(arrow(820, 326, 650, 366, color=INK, sw=1.8))

    f.append(box(560, 470, "залежності з modules.dep → finit_module", size=13, min_w=470))
    f.append(arrow(560, 412, 560, 448, color=INK, sw=1.8))

    f.append(text(560, 540, "функція ініціалізації прив'язує драйвер до пристрою",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "autoload.svg"), W, H, *f,
           title="Автозавантаження: один рядок аліаса, складений двічі")


if __name__ == "__main__":
    fig_link_vs_search()
    fig_deps()
    fig_autoload()
    print("ok")
