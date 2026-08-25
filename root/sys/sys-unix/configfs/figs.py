# -*- coding: utf-8 -*-
"""Фігури до теми «configfs: об'єкти ядра, які створює простір користувача»."""

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


# ── 1. Напрямок створення: sysfs проти configfs ─────────────────────────────
def fig_direction():
    W, H = 1200, 500
    P = []
    P.append(text(W / 2, 38, "Хто в кого просить: два протилежні напрямки",
                  size=18, bold=True))

    # рамки панелей
    P.append(rect(40, 62, 520, 400, fill="#fbfcfd", stroke=MUTED, sw=1.5))
    P.append(rect(640, 62, 520, 400, fill="#fbfcfd", stroke=MUTED, sw=1.5))
    P.append(text(300, 92, "sysfs — показ наявного", size=16, bold=True, color=NEG))
    P.append(text(900, 92, "configfs — створення нового", size=16, bold=True, color=FIELD))

    for x0, col in ((70, NEG), (670, FIELD)):
        P.append(fitbox(x0, 116, 460, 62,
                        "ЯДРО",
                        size=14, fill=GREY_BG, stroke=LINE, sw=2))
        P.append(fitbox(x0, 248, 460, 62,
                        "ДЕРЕВО ІМЕН",
                        size=14, fill=WARM_BG, stroke=GOLD, sw=2))
        P.append(fitbox(x0, 380, 460, 62,
                        "ПРОСТІР КОРИСТУВАЧА",
                        size=14, fill=BLUE_BG if col is NEG else GREEN_BG,
                        stroke=col, sw=2))

    # ліва панель: стрілка вниз від ядра, коротка вгору від користувача
    P.append(arrow(200, 180, 200, 244, color=NEG))
    P.append(text(214, 206, "знайшло залізо —", size=12.5, color=MUTED, anchor="start"))
    P.append(text(214, 226, "каталог з'явився сам", size=12.5, color=MUTED, anchor="start"))

    P.append(arrow(200, 378, 200, 314, color=NEG))
    P.append(text(214, 338, "write у наявний атрибут", size=12.5, color=MUTED, anchor="start"))
    P.append(text(214, 358, "змінює те, що вже є", size=12.5, color=MUTED, anchor="start"))

    P.append(line(468, 378, 468, 316, color=POS, sw=2, dash="6 5"))
    P.append(text(468, 348, "✕", size=20, color=POS, bold=True))
    P.append(text(468, 300, "mkdir", size=12.5, color=POS, bold=True))

    # права панель: обидві стрілки вгору
    P.append(arrow(800, 378, 800, 314, color=FIELD))
    P.append(text(814, 338, "mkdir створює каталог", size=12.5, color=MUTED, anchor="start"))
    P.append(text(814, 358, "командою людини", size=12.5, color=MUTED, anchor="start"))

    P.append(arrow(800, 246, 800, 182, color=FIELD))
    P.append(text(814, 206, "ядро виділяє об'єкт", size=12.5, color=MUTED, anchor="start"))
    P.append(text(814, 226, "у відповідь на каталог", size=12.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "direction.svg"), W, H, *P,
           title="Напрямок створення в sysfs і configfs")


# ── 2. Анатомія піддерева ───────────────────────────────────────────────────
def fig_tree():
    W, H = 1280, 660
    P = []
    P.append(text(W / 2, 38, "Одне дерево — каталоги трьох різних походжень",
                  size=18, bold=True))

    ROWS = [
        # (відступ, підпис, заливка, обвідка)
        (60,  "/sys/kernel/config/",        GREY_BG,  MUTED),
        (110, "usb_gadget/",                GREY_BG,  MUTED),
        (170, "g1/",                        GREEN_BG, FIELD),
        (230, "idVendor   idProduct   UDC", WARM_BG,  GOLD),
        (230, "strings/",                   BLUE_BG,  NEG),
        (290, "0x409/",                     GREEN_BG, FIELD),
        (230, "functions/",                 BLUE_BG,  NEG),
        (290, "acm.usb0/",                  GREEN_BG, FIELD),
        (230, "configs/",                   BLUE_BG,  NEG),
        (290, "c.1/",                       GREEN_BG, FIELD),
        (350, "acm.usb0  →",                RED_BG,   POS),
    ]

    y0, step, bh = 86, 50, 38
    geom = []
    for i, (x, label, fill, stroke) in enumerate(ROWS):
        y = y0 + i * step
        w = max(150, text_width(label, 14) + 30)
        P.append(fitbox(x, y, w, bh, label, size=14, fill=fill, stroke=stroke, sw=1.8))
        geom.append((x, y, w))

    # елбоу-лінії від батька до дитини
    def elbow(pi, ci):
        px, py, _ = geom[pi]
        cx, cy, _ = geom[ci]
        vx = px + 16
        P.append(line(vx, py + bh, vx, cy + bh / 2, color=MUTED, sw=1.4))
        P.append(line(vx, cy + bh / 2, cx, cy + bh / 2, color=MUTED, sw=1.4))

    for pi, ci in ((0, 1), (1, 2),
                   (2, 3), (2, 4), (2, 6), (2, 8),
                   (4, 5), (6, 7), (8, 9), (9, 10)):
        elbow(pi, ci)

    # посилання: з рядка 10 назад у рядок 7, в обхід праворуч
    sx, sy, sw_ = geom[10]
    tx, ty, tw_ = geom[7]
    rx = 620
    P.append(line(sx + sw_, sy + bh / 2, rx, sy + bh / 2, color=POS, sw=1.8, dash="6 5"))
    P.append(line(rx, sy + bh / 2, rx, ty + bh / 2, color=POS, sw=1.8, dash="6 5"))
    P.append(arrow(rx, ty + bh / 2, tx + tw_ + 4, ty + bh / 2, color=POS))
    P.append(text(rx + 14, sy + bh / 2 - 12, "символьне посилання —", size=12.5,
                  color=POS, anchor="start"))
    P.append(text(rx + 14, sy + bh / 2 + 8, "оголошений зв'язок", size=12.5,
                  color=POS, anchor="start"))

    # легенда
    lx, ly = 830, 96
    P.append(fitbox(lx, ly, 400, 46, "заводить модуль ядра — не видалити",
                    size=13, fill=GREY_BG, stroke=MUTED, sw=1.8))
    P.append(fitbox(lx, ly + 72, 400, 46, "створює mkdir — це і є об'єкт",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=1.8))
    P.append(fitbox(lx, ly + 144, 400, 46, "типова група — частина об'єкта",
                    size=13, fill=BLUE_BG, stroke=NEG, sw=1.8))
    P.append(fitbox(lx, ly + 216, 400, 46, "атрибут — файл, заданий типом",
                    size=13, fill=WARM_BG, stroke=GOLD, sw=1.8))
    P.append(fitbox(lx, ly + 288, 400, 46, "посилання — зв'язок між об'єктами",
                    size=13, fill=RED_BG, stroke=POS, sw=1.8))
    P.append(fitbox(lx, ly + 372, 400, 92,
                    "нового файлу не створити:\n"
                    "у таблиці дій над каталогом\n"
                    "просто немає такої функції",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.5))

    render(os.path.join(OUT, "tree-anatomy.svg"), W, H, *P,
           title="Анатомія піддерева configfs")


# ── 3. Життєвий цикл об'єкта ────────────────────────────────────────────────
def fig_lifecycle():
    W, H = 1240, 620
    P = []
    P.append(text(W / 2, 38, "Кожна дія в оболонці — виклик функції модуля",
                  size=18, bold=True))
    P.append(text(250, 76, "у оболонці", size=15, bold=True, color=FIELD))
    P.append(text(830, 76, "у ядрі", size=15, bold=True, color=MUTED))

    LX, LW = 70, 360
    RX, RW = 560, 540
    ys = [100, 200, 300, 400]
    bh = 66

    left = [
        "mkdir g1",
        "echo 0x1d6b > idVendor",
        "ln -s functions/acm.usb0 configs/c.1",
        "rmdir g1",
    ]
    right = [
        "ct_group_ops->make_group()\nмодуль виділяє пам'ять, лічильник = 1",
        "configfs_attribute->store()\nтекст, не більше 4096 байтів",
        "ct_item_ops->allow_link()\nмодуль запам'ятовує зв'язок",
        "перевірки: діти? посилання? залежності?",
    ]

    for i, y in enumerate(ys):
        P.append(fitbox(LX, y, LW, bh, left[i], size=13.5,
                        fill=GREEN_BG, stroke=FIELD, sw=1.8))
        P.append(fitbox(RX, y, RW, bh, right[i], size=13.5,
                        fill=GREY_BG, stroke=LINE, sw=1.8))
        P.append(arrow(LX + LW + 8, y + bh / 2, RX - 8, y + bh / 2, color=MUTED))

    # успіх — униз
    P.append(arrow(RX + RW / 2, ys[3] + bh, RX + RW / 2, 496, color=LINE))
    P.append(fitbox(RX, 500, RW, 66,
                    "drop_item() → config_item_put()\n"
                    "останнє посилання пішло → release() звільняє пам'ять",
                    size=13.5, fill=GREY_BG, stroke=LINE, sw=1.8))

    # відмова — ліворуч
    P.append(arrow(RX - 8, ys[3] + bh / 2 + 14, LX + LW + 8, 512, color=POS))
    P.append(fitbox(LX, 486, LW, 94,
                    "ENOTEMPTY — є ваші діти\n"
                    "EBUSY — посилання або залежність\n"
                    "EPERM — це типова група",
                    size=13.5, fill=RED_BG, stroke=POS, sw=1.8))

    render(os.path.join(OUT, "lifecycle.svg"), W, H, *P,
           title="Життєвий цикл об'єкта configfs")


# ── 4. Демо-модуль: каталоги і виділені ділянки пам'яті ─────────────────────
def fig_demo_memory():
    W, H = 1200, 600
    P = []
    P.append(text(W / 2, 36, "Два каталоги — одна виділена ділянка",
                  size=18, bold=True))

    # ліва панель: дерево в оболонці
    P.append(rect(40, 66, 470, 470, fill="#fbfcfd", stroke=MUTED, sw=1.5))
    P.append(text(275, 98, "що видно в оболонці", size=15, bold=True, color=MUTED))

    tree = [
        (70, 146, "/sys/kernel/config/demo/", False),
        (104, 186, "t1/", True),
        (140, 224, "limit", False),
        (140, 260, "label", False),
        (140, 296, "nr_links", False),
        (140, 336, "slots/", True),
        (176, 374, "s0/", True),
        (212, 410, "weight", False),
    ]
    for x, y, s, key in tree:
        P.append(text(x, y, s, size=14, anchor="start",
                      color=FIELD if key else MUTED, bold=key))

    P.append(text(70, 470, "типова група slots/ і файли —", size=12.5,
                  color=MUTED, anchor="start"))
    P.append(text(70, 492, "не окремі речі, а частини t1", size=12.5,
                  color=MUTED, anchor="start"))

    # права частина: блоки пам'яті
    P.append(rect(630, 110, 530, 250, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(text(895, 140, "kzalloc(sizeof(struct demo_target))",
                  size=14.5, bold=True, color=FIELD))
    rows_a = [
        (162, "struct config_group group;"),
        (212, "struct config_group slots;"),
        (262, "unsigned int limit;   char label[64];"),
        (306, "unsigned int nr_links;"),
    ]
    for y, s in rows_a:
        P.append(fitbox(652, y, 486, 40, s, size=13.5,
                        fill="#ffffff", stroke=LINE, sw=1.3))

    P.append(rect(630, 400, 530, 150, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(text(895, 430, "kzalloc(sizeof(struct demo_slot))",
                  size=14.5, bold=True, color=NEG))
    P.append(fitbox(652, 448, 486, 40, "struct config_item item;",
                    size=13.5, fill="#ffffff", stroke=LINE, sw=1.3))
    P.append(fitbox(652, 496, 486, 40, "unsigned int weight;",
                    size=13.5, fill="#ffffff", stroke=LINE, sw=1.3))

    # стрілки каталог → поле (у порожній смузі між панелями)
    P.append(arrow(330, 182, 646, 182, color=FIELD))
    P.append(arrow(330, 332, 646, 232, color=FIELD))
    P.append(arrow(330, 370, 646, 468, color=NEG))

    render(os.path.join(OUT, "demo-memory.svg"), W, H, *P,
           title="Каталоги демо-модуля і пам'ять, яку вони займають")


if __name__ == "__main__":
    fig_direction()
    fig_tree()
    fig_lifecycle()
    fig_demo_memory()
    print("готово:", OUT)
