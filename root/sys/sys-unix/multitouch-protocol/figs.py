# -*- coding: utf-8 -*-
import os
import sys

# figs.py у теці теми — чотири рівні вглиб від кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")

W, H = 800, 440
ROW_H, STEP, TOP = 30, 40, 60
COL_W = 300

FILL_ABS = "#e0f0ff"
FILL_SYN = "#ffe0e0"
FILL_SLOT = "#e0ffe0"


def _row_fill(e):
    if e.startswith("SYN_"):
        return FILL_SYN
    if "SLOT" in e:
        return FILL_SLOT
    return FILL_ABS


def _column(x_left, cx, title, events):
    frags = [text(cx, 30, title, size=18, bold=True)]
    y = TOP
    for e in events:
        frags.append(rect(x_left, y, COL_W, ROW_H, fill=_row_fill(e), rx=5))
        frags.append('<text x="%d" y="%d" font-family="monospace" font-size="15" '
                     'text-anchor="middle">%s</text>' % (cx, y + 20, esc(e)))
        y += STEP
    return frags


def generate_mt_comparison():
    events_a = [
        "ABS_MT_POSITION_X  250",
        "ABS_MT_POSITION_Y  300",
        "SYN_MT_REPORT      0",
        "ABS_MT_POSITION_X  400",
        "ABS_MT_POSITION_Y  450",
        "SYN_MT_REPORT      0",
        "SYN_REPORT         0",
    ]
    events_b = [
        "ABS_MT_SLOT        0",
        "ABS_MT_TRACKING_ID 101",
        "ABS_MT_POSITION_X  250",
        "ABS_MT_POSITION_Y  300",
        "ABS_MT_SLOT        1",
        "ABS_MT_TRACKING_ID 102",
        "ABS_MT_POSITION_X  400",
        "ABS_MT_POSITION_Y  450",
        "SYN_REPORT         0",
    ]

    frags = []
    frags += _column(50, 200, "Протокол A (без збереження стану)", events_a)
    frags += _column(450, 600, "Протокол B (зі слотами)", events_b)

    render(os.path.join(IMG, "fig-mt-comparison.svg"), W, H, *frags)


if __name__ == "__main__":
    if not os.path.isdir(IMG):
        os.makedirs(IMG)
    generate_mt_comparison()
