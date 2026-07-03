# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Часова смуга народження GNU-тулчейну ────────────────────────────────
def fig_timeline():
    W, H = 780, 300
    frags = []
    frags.append(text(W/2, 26, "Як складався вільний тулчейн: ланка за ланкою", size=17, bold=True))

    # горизонтальна вісь років
    y = 130
    frags.append(line(50, y, 730, y, color=INK, sw=2))
    for x in (50, 730):
        frags.append(line(x, y-5, x, y+5, color=INK, sw=2))

    events = [
        (95,  "1983", "оголошено\nпроєкт GNU", NEG, "up"),
        (215, "1986", "GDB —\nналагоджувач", FIELD, "down"),
        (360, "1987", "GCC 0.9 —\nкомпілятор", POS, "up"),
        (500, "1990-ті", "binutils, newlib\n(Cygnus)", NEG, "down"),
        (655, "2017", "RISC-V у\nмейнлайн GCC", FIELD, "up"),
    ]
    for x, yr, label, col, side in events:
        frags.append(circle(x, y, 6, fill=col, stroke=col))
        frags.append(text(x, y+ (24 if side=="down" else -14), yr, size=13, bold=True, color=col))
        ly = y + (44 if side=="down" else -58)
        frags.append(mtext(x, ly, label.split("\n"), size=11, color=MUTED, lh=1.25))

    frags.append(text(W/2, 288,
                      "спершу — окремі інструменти під одну мету; згодом вони зрослися в ланцюг, спільний для всіх чипів",
                      size=11, color=INK))
    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *frags)


# ── 2. RTL як спільний «горб» — багато мов зверху, багато ядер знизу ───────
def fig_rtl():
    W, H = 720, 340
    frags = []
    frags.append(text(W/2, 26, "Ідея RTL: одна проміжна мова — багато мов і багато ядер", size=16, bold=True))

    # верх: вихідні мови
    langs = [(150, "C"), (300, "C++"), (450, "Ada"), (600, "Fortran")]
    for x, name in langs:
        frags.append(fitbox(x-52, 60, 104, 34, name, size=13, bold=True, fill="#eef2ff", stroke=NEG))
        frags.append(arrow(x, 94, 360, 138, color=MUTED, sw=1.4))

    # середина: RTL
    frags.append(rect(230, 138, 260, 60, fill="#fff7ed", stroke=POS, sw=2, rx=10))
    frags.append(text(360, 162, "RTL", size=18, bold=True, color=POS))
    frags.append(text(360, 184, "проміжна мова (Davidson–Fraser)", size=11, color=MUTED))

    # низ: цільові ядра
    cores = [(140, "VAX"), (280, "ARM"), (420, "RISC-V"), (580, "Xtensa")]
    for x, name in cores:
        frags.append(arrow(360, 198, x, 250, color=MUTED, sw=1.4))
        frags.append(fitbox(x-52, 250, 104, 34, name, size=13, bold=True, fill="#eafaf1", stroke=FIELD))

    frags.append(text(W/2, 316,
                      "нову мову дописуєш лише спереду, новий чіп — лише ззаду; середина спільна — тому портів так багато",
                      size=11, color=INK))
    render(os.path.join(OUT, 'hist-rtl.svg'), W, H, *frags)


fig_timeline()
fig_rtl()
print("ok")
