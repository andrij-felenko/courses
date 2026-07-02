# -*- coding: utf-8 -*-
"""Фігури для теми pcb-stackup (шарування плати).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b5763a"      # мідь
CORE   = "#dfe6ee"      # осердя (core) — склотекстоліт
PREPREG = "#eef1e6"     # препрег (склеювальний шар)
COPPER_FILL = "#e8c9a3"


def copper_layer(x, y, w, h, label=None, lsize=10):
    """Смуга міді з підписом ліворуч."""
    out = rect(x, y, w, h, fill=COPPER_FILL, stroke=COPPER, sw=1.4, rx=2)
    if label:
        out += text(x - 10, y + h / 2 + lsize * 0.35, label, size=lsize,
                    color=COPPER, bold=True, anchor="end")
    return out


def diel_layer(x, y, w, h, fill, label=None, rlabel=None, lsize=10):
    """Шар діелектрика (core/prepreg) з підписом усередині й товщиною праворуч."""
    out = rect(x, y, w, h, fill=fill, stroke="#c3ccd6", sw=1.2, rx=2)
    if label and h >= 16:
        out += text(x + w / 2, y + h / 2 + lsize * 0.35, label, size=lsize, color=MUTED)
    if rlabel:
        out += text(x + w + 12, y + h / 2 + lsize * 0.35, rlabel, size=lsize,
                    color=INK, anchor="start")
    return out


# ── 1. Анатомія 4-шарового стека ──────────────────────────────────────────────
def fig_stack():
    W, H = 760, 470
    frags = []
    x, w = 210, 320
    y = 70
    # згори вниз: Cu(sig) / prepreg / Cu(GND) / core / Cu(PWR) / prepreg / Cu(sig)
    tCu, tPre, tCore = 22, 46, 74
    frags.append(copper_layer(x, y, w, tCu, "L1  сигнал + деталі"))
    frags.append(text(x + w + 12, y + tCu / 2 + 3, "35 мкм (1 oz)", size=10,
                      color=INK, anchor="start")); y += tCu
    frags.append(diel_layer(x, y, w, tPre, PREPREG, "препрег", "≈ 0.2 мм")); y += tPre
    frags.append(copper_layer(x, y, w, tCu, "L2  ЗЕМЛЯ (суцільна)"))
    frags.append(text(x + w + 12, y + tCu / 2 + 3, "опорна площина", size=10,
                      color=FIELD, anchor="start", )); y += tCu
    frags.append(diel_layer(x, y, w, tCore, CORE, "осердя (core, FR-4)", "≈ 1.2 мм")); y += tCore
    frags.append(copper_layer(x, y, w, tCu, "L3  ЖИВЛЕННЯ"))
    frags.append(text(x + w + 12, y + tCu / 2 + 3, "площина живлення", size=10,
                      color=POS, anchor="start")); y += tCu
    frags.append(diel_layer(x, y, w, tPre, PREPREG, "препрег", "≈ 0.2 мм")); y += tPre
    frags.append(copper_layer(x, y, w, tCu, "L4  сигнал + деталі")); y += tCu

    # фігурна дужка загальної товщини
    yb0, yb1 = 70, y
    frags.append(line(x - 150, yb0, x - 150, yb1, color=MUTED, sw=1.4))
    frags.append(line(x - 155, yb0, x - 145, yb0, color=MUTED, sw=1.4))
    frags.append(line(x - 155, yb1, x - 145, yb1, color=MUTED, sw=1.4))
    frags.append(text(x - 158, (yb0 + yb1) / 2 - 8, "≈ 1.6 мм", size=11, color=INK,
                      anchor="end", bold=True))
    frags.append(text(x - 158, (yb0 + yb1) / 2 + 8, "уся плата", size=10, color=MUTED,
                      anchor="end"))

    bx, bw, bh = textbox(x + w / 2, 430,
                         ["Симетрія навколо середини — щоб плату не жолобило.",
                          "Ядро — товсте; сигнали — над своєю опорою."],
                         size=11, fill="#f7faf8", stroke="#caa24a")
    frags.append(bx)

    render(os.path.join(OUT, "stack-anatomy.svg"), W, H, *frags,
           title="Класичний 4-шаровий стек: сигнал · земля · живлення · сигнал")


# ── 2. Зворотний струм тулиться до опори; розрив = велика петля ────────────────
def fig_return():
    W, H = 760, 400
    frags = []

    def scene(x0, ok):
        ytr, ygnd = 90, 150
        col = FIELD if ok else POS
        # доріжка сигналу згори
        frags.append(line(x0, ytr, x0 + 300, ytr, color="#caa24a", sw=5))
        frags.append(text(x0, ytr - 14, "доріжка сигналу (L1)", size=11,
                          color="#caa24a", bold=True, anchor="start"))
        # опорна площина знизу
        if ok:
            frags.append(rect(x0, ygnd, 300, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.3, rx=2))
        else:
            # розрив/щілина в площині
            frags.append(rect(x0, ygnd, 130, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.3, rx=2))
            frags.append(rect(x0 + 170, ygnd, 130, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.3, rx=2))
            frags.append(text(x0 + 150, ygnd + 40, "щілина", size=10, color=POS, bold=True))
        frags.append(text(x0, ygnd + 15, "GND (L2)", size=10, color=INK, anchor="end"))
        # шлях зворотного струму (пунктир зі стрілками)
        if ok:
            frags.append(line(x0 + 150, ygnd, x0 + 150, ygnd, color=col))  # noop
            frags.append('<path d="M %d %d L %d %d" fill="none" stroke="%s" '
                         'stroke-width="2.2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>'
                         % (x0 + 280, ygnd, x0 + 20, ygnd, col))
            frags.append(text(x0 + 150, ygnd + 40, "зворот тулиться під доріжкою → мала петля",
                              size=10, color=FIELD))
        else:
            # струм мусить обходити щілину — велика петля
            frags.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" '
                         'stroke="%s" stroke-width="2.2" stroke-dasharray="6,4" '
                         'marker-end="url(#arrow)"/>'
                         % (x0 + 280, ygnd, x0 + 175, ygnd,
                            x0 + 150, ygnd + 70, x0 + 20, ygnd, col))
            frags.append(text(x0 + 150, ygnd + 90, "обхід щілини → величезна петля, дзвін, завади",
                              size=10, color=POS))

    scene(60, ok=True)
    frags.append(line(400, 70, 400, 300, color=MUTED, sw=1, dash="4,4"))
    scene(420, ok=False)
    frags.append(text(210, 75, "суцільна опора", size=13, color=FIELD, bold=True))
    frags.append(text(570, 75, "розрізана опора", size=13, color=POS, bold=True))

    render(os.path.join(OUT, "return-current.svg"), W, H, *frags,
           title="Зворотний струм іде під доріжкою — якщо опора суцільна")


# ── 3. Вага міді → товщина → струм ────────────────────────────────────────────
def fig_copper():
    W, H = 760, 360
    frags = []
    rows = [
        ("½ oz", "17 мкм", "тонкі сигнали,\nгустий монтаж", 0.5, MUTED),
        ("1 oz", "35 мкм", "стандарт:\nсигнали й дрібне живлення", 1.0, INK),
        ("2 oz", "70 мкм", "силові шини,\nбільші струми", 2.0, POS),
        ("4 oz", "140 мкм", "потужне живлення,\nтепловідвід", 4.0, "#8a1f13"),
    ]
    x0, y0 = 70, 90
    colw = [90, 90, 240]
    # заголовки
    heads = ["вага", "товщина міді", "де застосовують"]
    hx = x0
    for hh, cw in zip(heads, colw):
        frags.append(text(hx + cw / 2, y0 - 12, hh, size=11, color=MUTED, bold=True))
        hx += cw
    # смужка-візуалізація товщини праворуч
    frags.append(text(x0 + sum(colw) + 90, y0 - 12, "товщина (в масштабі)", size=11,
                      color=MUTED, bold=True))
    rh = 58
    for i, (wt, th, use, mult, col) in enumerate(rows):
        y = y0 + i * rh
        frags.append(rect(x0, y, sum(colw), rh - 10, fill="#f7faf8", stroke="#c3ccd6", sw=1.2))
        frags.append(text(x0 + colw[0] / 2, y + (rh - 10) / 2 + 5, wt, size=14, color=col, bold=True))
        frags.append(text(x0 + colw[0] + colw[1] / 2, y + (rh - 10) / 2 + 5, th, size=13, color=INK))
        frags.append(mtext(x0 + colw[0] + colw[1] + colw[2] / 2, y + (rh - 10) / 2 - 3,
                           use, size=10, color=INK))
        # смужка міді
        bar_x = x0 + sum(colw) + 30
        bar_h = 6 + mult * 8
        frags.append(rect(bar_x, y + (rh - 10) / 2 - bar_h / 2, 140, bar_h,
                          fill=COPPER_FILL, stroke=COPPER, sw=1.3, rx=2))

    bx, bw, bh = textbox(W / 2, 328,
                         ["«Унція» — це маса міді на квадратний фут; 1 oz = 35 мкм.",
                          "Товща мідь — менший опір і кращий тепловідвід, але дорожче."],
                         size=11, fill="#fbf7ec", stroke="#caa24a")
    frags.append(bx)

    render(os.path.join(OUT, "copper-weight.svg"), W, H, *frags,
           title="Вага міді → товщина → допустимий струм")


# ── 4. Куди що класти на 4 шари ───────────────────────────────────────────────
def fig_assign():
    W, H = 760, 380
    frags = []
    layers = [
        ("L1 верх", "деталі, сигнали, силова гаряча петля", COPPER, "#fff6ec"),
        ("L2 земля", "СУЦІЛЬНА площина — опора для всіх сигналів", FIELD, "#eef7f0"),
        ("L3 живлення", "площини шин; поряд із землею = буферна ємність", POS, "#fdecea"),
        ("L4 низ", "решта сигналів, друга сторона монтажу", COPPER, "#fff6ec"),
    ]
    x, w = 120, 520
    y = 70
    lh = 62
    for name, body, col, fill in layers:
        frags.append(rect(x, y, w, lh - 12, fill=fill, stroke=col, sw=2))
        frags.append(text(x + 12, y + (lh - 12) / 2 + 5, name, size=13, color=col,
                          bold=True, anchor="start"))
        frags.append(text(x + 170, y + (lh - 12) / 2 + 5, body, size=11, color=INK, anchor="start"))
        y += lh

    # стрілка «сигнал над своєю землею»
    frags.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrow)"/>'
                 % (x - 6, 88, x - 46, 120, x - 6, 132, FIELD))
    frags.append(text(x - 52, 118, "сигнал L1\nбачить землю L2", size=9, color=FIELD, anchor="end"))

    render(os.path.join(OUT, "layer-assign.svg"), W, H, *frags,
           title="Розподіл 4 шарів: кожен сигнал — над суцільною опорою")


if __name__ == "__main__":
    fig_stack()
    fig_return()
    fig_copper()
    fig_assign()
    print("ok figs")
