# -*- coding: utf-8 -*-
"""Фігури до теми «Присипляння пристрою на ходу: runtime PM»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
BLUE_BG  = "#eaf0fd"
GOLD     = "#b8860b"


# ── 1. Лічильник, затримка й пінг-понг ───────────────────────────────────────
def fig_autosuspend_timeline():
    W, H = 1280, 620
    P = []

    X0, X1 = 170, 1180
    Y1, Y0 = 150, 232          # рівні лічильника: 1 і 0
    DELAY = 200                # 200 px = 200 мс

    # осі рівнів
    P.append(line(X0, Y1, X1, Y1, color=MUTED, sw=1, dash="4,5"))
    P.append(line(X0, Y0, X1, Y0, color=MUTED, sw=1, dash="4,5"))
    P.append(text(X0 - 22, Y1 + 5, "1", size=14, bold=True, anchor="end"))
    P.append(text(X0 - 22, Y0 + 5, "0", size=14, bold=True, anchor="end"))
    P.append(text(X0 - 40, (Y1 + Y0) / 2 - 34, "usage_count", size=13,
                  color=MUTED, anchor="end"))

    # ступінчаста лінія лічильника
    fall1, rise1 = 320, 400
    fall2, rise2 = 500, 590
    fall3        = 730
    steps = [(X0, Y1), (fall1, Y1), (fall1, Y0), (rise1, Y0), (rise1, Y1),
             (fall2, Y1), (fall2, Y0), (rise2, Y0), (rise2, Y1),
             (fall3, Y1), (fall3, Y0), (X1, Y0)]
    for (ax, ay), (bx, by) in zip(steps, steps[1:]):
        P.append(line(ax, ay, bx, by, color=INK, sw=2.6))

    # позначки get / put
    marks = [(fall1, "put"), (rise1, "get"), (fall2, "put"),
             (rise2, "get"), (fall3, "put")]
    for x, lbl in marks:
        col = NEG if lbl == "put" else POS
        P.append(text(x, Y1 - 24, lbl, size=13, bold=True, color=col))

    # вікна відліку затримки
    WY, WH = 286, 40
    wins = [(fall1, "скинуто", GREY_BG, MUTED),
            (fall2, "скинуто", GREY_BG, MUTED),
            (fall3, "добігло", GREEN_BG, FIELD)]
    for x, lbl, bg, st in wins:
        P.append(fitbox(x, WY, DELAY, WH, lbl, size=13, fill=bg, stroke=st, sw=1.6,
                        color=st, bold=True))

    P.append(text(X0 - 40, WY + WH / 2 + 5, "відлік затримки", size=13,
                  color=MUTED, anchor="end"))

    # момент справжнього присипляння
    sx = fall3 + DELAY
    P.append(line(sx, WY - 14, sx, 430, color=FIELD, sw=2, dash="5,4"))
    b, bw, bh = textbox(sx + 128, 400, ".runtime_suspend()\nстатус → suspended",
                        size=13.5, fill=GREEN_BG, stroke=FIELD, sw=1.8, bold=True)
    P.append(b)
    P.append(arrow(sx + 6, 400, sx + 128 - bw / 2 - 8, 400, color=FIELD, sw=1.8))

    # шкала часу
    AY = 480
    P.append(line(X0, AY, X1, AY, color=LINE, sw=1.6))
    for i in range(0, 11):
        x = X0 + i * 100
        if x > X1:
            break
        P.append(line(x, AY - 5, x, AY + 5, color=LINE, sw=1.4))
        P.append(text(x, AY + 24, str(i * 100), size=12, color=MUTED))
    P.append(text(X1 + 4, AY + 24, "мс", size=12, color=MUTED, anchor="start"))

    # пояснення
    P.append(text(X0, 546,
                  "пауза 80 мс і пауза 90 мс коротші за затримку 200 мс — пристрій жодного разу не заснув",
                  size=13.5, color=MUTED, anchor="start"))
    P.append(text(X0, 572,
                  "без затримки на цих двох паузах було б два присипляння і два пробудження — чиста втрата",
                  size=13.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "autosuspend-timeline.svg"), W, H, *P,
           title="Нуль у лічильнику ще не привід засинати: відлік затримки скидає кожен новий get")


# ── 2. Дерево і залежності поза деревом ──────────────────────────────────────
def fig_tree_and_links():
    W, H = 1340, 640
    P = []

    # ─ ліва панель: дерево батько↔дитина
    LX = 70
    P.append(text(LX, 74, "Дерево: батько тримають діти", size=15, bold=True, anchor="start"))

    nodes = [
        (150, "кореневий міст PCIe", "usage_count = 0\nchild_count = 1", RED_BG, POS, "спати не може"),
        (290, "контролер xHCI", "usage_count = 0\nchild_count = 1", RED_BG, POS, "спати не може"),
        (430, "USB-камера", "usage_count = 1\nchild_count = 0", GREEN_BG, FIELD, "нею користуються"),
    ]
    CX = LX + 200
    for y, name, cnt, bg, st, note in nodes:
        b, bw, bh = textbox(CX, y, [name, cnt], size=13.5, fill=bg, stroke=st,
                            sw=1.8, min_w=290)
        P.append(b)
        P.append(text(CX + bw / 2 + 16, y + 5, note, size=13, color=st,
                      bold=True, anchor="start"))

    for ya, yb in ((150, 290), (290, 430)):
        P.append(line(CX, ya + 40, CX, yb - 40, color=LINE, sw=1.6))

    # напрями обходу
    AX = LX + 20
    P.append(arrow(AX, 400, AX, 190, color=NEG, sw=2))
    P.append(text(AX - 14, 300, "присипляння", size=12.5, color=NEG, anchor="end"))
    P.append(text(AX - 14, 318, "знизу вгору", size=12.5, color=NEG, anchor="end"))

    P.append(text(LX, 530,
                  "батько втратить живлення — дитина втратить його теж,",
                  size=13, color=MUTED, anchor="start"))
    P.append(text(LX, 552,
                  "тому ненульовий child_count блокує присипляння батька",
                  size=13, color=MUTED, anchor="start"))

    # ─ роздільник
    P.append(line(730, 60, 730, 580, color=MUTED, sw=1, dash="6,6"))

    # ─ права панель: зв'язки поза деревом
    RX = 790
    P.append(text(RX, 74, "Поза деревом: постачальник і споживач", size=15,
                  bold=True, anchor="start"))

    RCX = RX + 240
    b, bw, bh = textbox(RCX, 180, ["контролер I²C", "споживач"], size=13.5,
                        fill=GREEN_BG, stroke=FIELD, sw=1.8, min_w=240)
    P.append(b)

    sup = [(RCX - 128, "генератор такту"), (RCX + 128, "регулятор напруги")]
    for x, name in sup:
        b, bw, bh = textbox(x, 390, [name, "постачальник"], size=13.5,
                            fill=BLUE_BG, stroke=NEG, sw=1.8, min_w=230)
        P.append(b)
        P.append(arrow(RCX, 222, x, 390 - 40, color=NEG, sw=1.8))

    P.append(text(RX, 530,
                  "ці двоє — не батьки контролера в дереві, але без них",
                  size=13, color=MUTED, anchor="start"))
    P.append(text(RX, 552,
                  "він мертвий; зв'язок оголошують device_link_add()",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "tree-and-links.svg"), W, H, *P,
           title="Пристрій не спить сам по собі: хто ще мусить не спати разом із ним")


# ── 3. Статуси і переходи ────────────────────────────────────────────────────
def fig_status_machine():
    W, H = 1240, 620
    P = []

    boxes = {
        "active":    (300, 160, "active", GREEN_BG, FIELD),
        "suspending": (940, 160, "suspending", WARM_BG, GOLD),
        "suspended": (940, 400, "suspended", BLUE_BG, NEG),
        "resuming":  (300, 400, "resuming", WARM_BG, GOLD),
    }
    dims = {}
    for k, (x, y, label, bg, st) in boxes.items():
        b, bw, bh = textbox(x, y, label, size=17, bold=True, fill=bg, stroke=st,
                            sw=2.2, min_w=210)
        P.append(b)
        dims[k] = (x, y, bw, bh)

    # active → suspending
    P.append(arrow(300 + 105, 138, 940 - 105, 138, color=LINE, sw=1.8))
    P.append(text(620, 118, "лічильник = 0, дітей не лишилось,", size=13))
    P.append(text(620, 100, "затримка добігла", size=13))

    # suspending → suspended
    P.append(arrow(940 + 60, 190, 940 + 60, 370, color=LINE, sw=1.8))
    P.append(text(940 + 76, 262, ".runtime_suspend()", size=13, anchor="start"))
    P.append(text(940 + 76, 282, "повернув 0", size=13, anchor="start"))

    # suspending → active (EBUSY)
    P.append(arrow(940 - 105, 182, 300 + 105, 182, color=POS, sw=1.8))
    P.append(text(620, 216, "повернув −EBUSY або −EAGAIN:", size=13, color=POS))
    P.append(text(620, 234, "хтось устиг зайняти пристрій", size=13, color=POS))

    # suspended → resuming
    P.append(arrow(940 - 105, 400, 300 + 105, 400, color=LINE, sw=1.8))
    P.append(text(620, 378, "pm_runtime_get…() або сигнал", size=13))
    P.append(text(620, 360, "пробудження від самого заліза", size=13))

    # resuming → active
    P.append(arrow(300 - 60, 370, 300 - 60, 190, color=LINE, sw=1.8))
    P.append(text(300 - 76, 262, ".runtime_resume()", size=13, anchor="end"))
    P.append(text(300 - 76, 282, "повернув 0", size=13, anchor="end"))

    # фатальна помилка
    b, bw, bh = textbox(620, 512, ["error", "будь-яка інша помилка: помічники більше не працюють,",
                                   "доки статус не виставлять руками"],
                        size=13.5, fill=RED_BG, stroke=POS, sw=2)
    P.append(b)
    P.append(arrow(940, 200, 700, 512 - bh / 2 - 8, color=POS, sw=1.6))
    P.append(arrow(300, 440, 540, 512 - bh / 2 - 8, color=POS, sw=1.6))

    render(os.path.join(OUT, "status-machine.svg"), W, H, *P,
           title="Що показує power/runtime_status і хто його змінює")


if __name__ == "__main__":
    fig_autosuspend_timeline()
    fig_tree_and_links()
    fig_status_machine()
    print("ok")
