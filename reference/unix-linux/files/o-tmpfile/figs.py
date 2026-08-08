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


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Вікно, у якому ім'я існує ─────────────────────────────────────────────
def fig_window():
    W, H = 1120, 500
    p = [text(W / 2, 36, "Звідки береться безіменний файл: два шляхи", size=17, bold=True)]

    p.append(text(70, 96, "класично", size=13, bold=True, anchor="start", color=MUTED))

    a1, a1x0, a1x1, a1y0, a1y1 = tb(235, 165,
                                    ["mkstemp()",
                                     "створює /tmp/sort-a7Bx",
                                     "і відкриває його"],
                                    size=13, fill=BLUE_FILL, stroke=NEG, pad=12)
    a2, a2x0, a2x1, a2y0, a2y1 = tb(600, 165,
                                    ["ім'я лежить у каталозі",
                                     "файл видно кожному,",
                                     "хто читає /tmp"],
                                    size=13, fill=RED_FILL, stroke=POS, pad=12)
    a3, a3x0, a3x1, a3y0, a3y1 = tb(950, 165,
                                    ["unlink()",
                                     "імені немає,",
                                     "дескриптор лишився"],
                                    size=13, fill=GREEN_FILL, stroke=FIELD, pad=12)
    p += [a1, a2, a3]
    p.append(arrow(a1x1 + 8, 165, a2x0 - 8, 165))
    p.append(arrow(a2x1 + 8, 165, a3x0 - 8, 165))
    p.append(text(600, 255, "вікно: чужий процес устигає взяти на цей файл своє ім'я",
                  size=13, color=POS))

    p.append(text(70, 316, "з O_TMPFILE", size=13, bold=True, anchor="start", color=MUTED))

    b1, b1x0, b1x1, b1y0, b1y1 = tb(295, 385,
                                    ["open(\"/var/tmp\",",
                                     "O_TMPFILE | O_RDWR,",
                                     "0600)"],
                                    size=13, fill=BLUE_FILL, stroke=NEG, pad=12)
    b2, b2x0, b2x1, b2y0, b2y1 = tb(760, 385,
                                    ["безіменний inode",
                                     "з першої ж миті:",
                                     "запису в каталозі не було"],
                                    size=13, fill=GREEN_FILL, stroke=FIELD, pad=12)
    p += [b1, b2]
    p.append(arrow(b1x1 + 8, 385, b2x0 - 8, 385))
    p.append(text(760, 470, "вікна немає: імені не існувало жодної миті",
                  size=13, color=FIELD))

    render(os.path.join(IMG, 'name-window.svg'), W, H, *p)


# ── 2. Хто тримає inode із нульовим лічильником ──────────────────────────────
def fig_holders():
    W, H = 1080, 540
    p = [text(W / 2, 36, "Що тримає inode, на який не веде жодне ім'я", size=17, bold=True)]

    p.append(text(300, 138, "тримає, поки процес живий", size=13, color=MUTED))
    p.append(text(790, 138, "тримає, поки система не прибрала", size=13, color=MUTED))

    left, lx0, lx1, ly0, ly1 = tb(160, 240,
                                  ["відкритий дескриптор",
                                   "лише в пам'яті ядра"],
                                  size=13, fill=BLUE_FILL, stroke=NEG, pad=13)
    mid, mx0, mx1, my0, my1 = tb(545, 240,
                                 ["inode на носії",
                                  "імен: 0",
                                  "блоки виділено",
                                  "дані на місці"],
                                 size=13, fill=WARM_FILL, stroke=WARM, pad=14)
    right, rx0, rx1, ry0, ry1 = tb(930, 240,
                                   ["запис у списку сиріт",
                                    "на самому носії"],
                                   size=13, fill=GREEN_FILL, stroke=FIELD, pad=13)
    p += [left, mid, right]
    p.append(arrow(lx1 + 8, 240, mx0 - 8, 240))
    p.append(arrow(rx0 - 8, 240, mx1 + 8, 240))

    out1, o1x0, o1x1, o1y0, o1y1 = tb(275, 445,
                                      ["процес закрив дескриптор",
                                       "блоки звільнено одразу"],
                                      size=13, fill=FILL, stroke=LINE, pad=13)
    out2, o2x0, o2x1, o2y0, o2y1 = tb(815, 445,
                                      ["раптове вимкнення живлення",
                                       "монтування обходить список",
                                       "і звільняє блоки"],
                                      size=13, fill=FILL, stroke=LINE, pad=13)
    p += [out1, out2]
    p.append(arrow(mx0 + 20, my1 + 6, 340, o1y0 - 8))
    p.append(arrow(mx1 - 20, my1 + 6, 750, o2y0 - 8))

    render(os.path.join(IMG, 'holders.svg'), W, H, *p)


# ── 3. Життя безіменного inode ───────────────────────────────────────────────
def fig_states():
    W, H = 1140, 450
    p = [text(W / 2, 36, "Життя inode, створеного з O_TMPFILE", size=17, bold=True)]

    s1, s1x0, s1x1, s1y0, s1y1 = tb(165, 190,
                                    ["inode виділено",
                                     "як звичайний:",
                                     "імен 1"],
                                    size=13, fill=BLUE_FILL, stroke=NEG, pad=13)
    s2, s2x0, s2x1, s2y0, s2y1 = tb(540, 190,
                                    ["імен 0",
                                     "у списку сиріт",
                                     "тримає дескриптор"],
                                    size=13, fill=WARM_FILL, stroke=WARM, pad=13)
    p += [s1, s2]
    p.append(arrow(s1x1 + 8, 190, s2x0 - 8, 190))
    p.append(text((s1x1 + s2x0) / 2, s1y0 - 22, "ядро віднімає одиницю", size=13, color=MUTED))

    s3, s3x0, s3x1, s3y0, s3y1 = tb(925, 105,
                                    ["linkat()",
                                     "імен 1, зі списку прибрано",
                                     "звичайний файл із іменем"],
                                    size=13, fill=GREEN_FILL, stroke=FIELD, pad=13)
    s4, s4x0, s4x1, s4y0, s4y1 = tb(925, 320,
                                    ["close()",
                                     "inode і блоки звільнено"],
                                    size=13, fill=RED_FILL, stroke=POS, pad=13)
    p += [s3, s4]
    p.append(arrow(s2x1 + 8, 172, s3x0 - 8, 125))
    p.append(arrow(s2x1 + 8, 212, s4x0 - 8, 295))

    render(os.path.join(IMG, 'tmpfile-life.svg'), W, H, *p)


# ── 4. Порядок кроків публікації і що лишить збій ────────────────────────────
def fig_publish_order():
    W, H = 1120, 660
    p = [text(W / 2, 36, "Порядок публікації і що лишить раптове вимкнення", size=17, bold=True)]

    steps = [
        (105, ["open(dir, O_TMPFILE | O_RDWR, 0600)"], BLUE_FILL, NEG),
        (185, ["write(): уміст"], BLUE_FILL, NEG),
        (265, ["fchown(), fchmod(), fsetxattr():", "власник, права, атрибути"], BLUE_FILL, NEG),
        (355, ["fsync(fd): уміст на носії"], WARM_FILL, WARM),
        (455, ["linkat(): ім'я з'явилося"], GREEN_FILL, FIELD),
        (545, ["fsync(каталог): ім'я на носії"], WARM_FILL, WARM),
    ]
    box = []
    for cy, lines, fl, st in steps:
        frag, x0, x1, y0, y1 = tb(300, cy, lines, size=13, fill=fl, stroke=st, pad=12)
        p.append(frag)
        box.append((x0, x1, y0, y1))
    for i in range(len(box) - 1):
        p.append(arrow(300, box[i][3] + 5, 300, box[i + 1][2] - 7))

    notes = [
        (215, ["збій тут: на носії не лишиться нічого —",
               "імені не було, блоки поверне список сиріт"], GREEN_FILL, FIELD, 310),
        (410, ["збій тут: ім'я могло не пережити збою,",
               "але якщо пережило — уміст під ним повний"], WARM_FILL, WARM, 405),
        (600, ["після цього кроку ім'я і повний уміст",
               "переживуть будь-яке вимкнення"], GREEN_FILL, FIELD, 583),
    ]
    for cy, lines, fl, st, from_y in notes:
        frag, x0, x1, y0, y1 = tb(810, cy, lines, size=13, fill=fl, stroke=st, pad=12)
        p.append(frag)
        p.append(arrow(box[0][1] + 10, from_y, x0 - 8, cy))

    render(os.path.join(IMG, 'publish-order.svg'), W, H, *p)


fig_window()
fig_holders()
fig_states()
fig_publish_order()
print("ok")
