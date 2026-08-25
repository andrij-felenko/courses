# -*- coding: utf-8 -*-
"""Фігури до теми «Автомат станів ініціалізації SD-картки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

OK    = "#27ae60"   # успішний перехід (= FIELD)
WAIT  = "#b9770e"   # стан очікування / цикл (тепле)
FAIL  = "#c0392b"   # відмова / глухий кут (= POS)


# ── 1. Граф станів ініціалізації ─────────────────────────────────────────────
def fig_state_graph():
    W, H = 860, 560
    frs = []

    def node(cx, cy, label, fill=FILL, stroke=LINE, w=170, sub=None):
        h = 54 if sub is None else 66
        frs.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=2, rx=10))
        if sub is None:
            frs.append(text(cx, cy + 5, label, size=15, bold=True))
        else:
            frs.append(text(cx, cy - 6, label, size=15, bold=True))
            frs.append(text(cx, cy + 15, sub, size=11, color=MUTED))
        return (cx, cy, w, h)

    def edge(a, b, lab, color=LINE, side="mid", labdy=-6):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        x1, y1 = ax, ay + ah / 2
        x2, y2 = bx, by - bh / 2
        frs.append(arrow(x1, y1, x2, y2, color=color, sw=2))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        frs.append(text(mx, my + labdy, lab, size=11, color=color, bold=True))

    # вертикальна лінія станів по центру
    cx = 300
    n_pwr = node(cx, 70,  "Живлення", FILL, MUTED, sub="ramp ≥ 1 мс")
    n_warm = node(cx, 165, "Розігрів шини", "#fff6e6", WAIT, sub="≥ 74 такти, CS=1")
    n_idle = node(cx, 260, "IDLE", FILL, LINE, sub="CMD0 → R1=0x01")
    n_ifc  = node(cx, 355, "Перевірка вольтажу", FILL, LINE, sub="CMD8 → R7")
    n_poll = node(cx, 450, "Опитування", "#fff6e6", WAIT, sub="ACMD41 у циклі")
    n_ready = node(600, 450, "READY", "#e9f7ef", OK, sub="CMD58 → CCS")

    edge(n_pwr, n_warm, "напруга є")
    edge(n_warm, n_idle, "розбудили")
    edge(n_idle, n_ifc, "у SPI-режимі")
    edge(n_ifc, n_poll, "вольтаж ок")

    # цикл ACMD41 (самопетля)
    px, py, pw, ph = n_poll
    frs.append(arrow(px + pw / 2, py - 12, px + pw / 2 + 60, py - 12, color=WAIT, sw=2))
    frs.append(line(px + pw / 2 + 60, py - 12, px + pw / 2 + 60, py + 12, color=WAIT, sw=2))
    frs.append(arrow(px + pw / 2 + 60, py + 12, px + pw / 2, py + 12, color=WAIT, sw=2))
    frs.append(text(px + pw / 2 + 92, py, "ще", size=11, color=WAIT, bold=True))
    frs.append(text(px + pw / 2 + 92, py + 15, "busy", size=11, color=WAIT, bold=True))

    # горизонтальний перехід у READY
    frs.append(arrow(px + pw / 2, py, 600 - 85, py, color=OK, sw=2.2))
    frs.append(text((px + pw / 2 + 515) / 2 + 40, py - 8, "R1=0x00", size=11, color=OK, bold=True))

    # глухий кут відмови
    n_fail = node(600, 260, "ПОМИЛКА", "#fdecea", FAIL, w=150, sub="нема відповіді / таймаут")
    frs.append(arrow(n_idle[0] + n_idle[2] / 2, n_idle[1], n_fail[0] - n_fail[2] / 2, n_fail[1], color=FAIL, sw=1.8))
    frs.append(text((n_idle[0] + 600) / 2 + 20, n_idle[1] - 8, "мовчить", size=11, color=FAIL, bold=True))
    # від IFC теж стрілка вбік (стара картка / відмова)
    frs.append(line(n_ifc[0] + n_ifc[2] / 2, n_ifc[1], 720, n_ifc[1], color=FAIL, sw=1.6, dash="5 4"))
    frs.append(line(720, n_ifc[1], 720, n_fail[1] + 20, color=FAIL, sw=1.6, dash="5 4"))
    frs.append(arrow(720, n_fail[1] + 20, n_fail[0] + n_fail[2] / 2, n_fail[1] + 20, color=FAIL, sw=1.6))
    frs.append(text(730, (n_ifc[1] + n_fail[1]) / 2, "0x1AA", size=10, color=FAIL, anchor="start", bold=True))
    frs.append(text(730, (n_ifc[1] + n_fail[1]) / 2 + 14, "не збігся", size=10, color=FAIL, anchor="start"))

    return render(os.path.join(IMG, "state-graph.svg"), W, H, *frs,
                  title="Ініціалізація як граф станів: уперед лише по правильній відповіді")


# ── 2. Розігрів шини: 74 такти при CS=1 ──────────────────────────────────────
def fig_warmup():
    W, H = 780, 330
    frs = []
    x0, x1 = 90, 690
    y_cs, y_clk = 90, 200

    # підписи ліній
    frs.append(text(70, y_cs + 5, "CS", size=13, bold=True, anchor="end"))
    frs.append(text(70, y_clk + 5, "SCLK", size=13, bold=True, anchor="end"))

    # CS весь час високий (важливо)
    frs.append(line(x0, y_cs - 20, x1, y_cs - 20, color=POS, sw=2.5))
    frs.append(text((x0 + x1) / 2, y_cs - 30, "тримаємо ВИСОКИМ увесь розігрів", size=12, color=POS, bold=True))

    # SCLK — пачка тактів
    base = y_clk + 18
    top = y_clk - 18
    xx = x0
    step = 30
    path = []
    n = 0
    while xx < x1 - step and n < 20:
        path.append((xx, base)); path.append((xx, top))
        path.append((xx + step / 2, top)); path.append((xx + step / 2, base))
        xx += step; n += 1
    d = "M %.1f %.1f " % (path[0][0], path[0][1])
    for px, py in path[1:]:
        d += "L %.1f %.1f " % (px, py)
    frs.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, INK))
    frs.append(text((x0 + x1) / 2, base + 26, "≥ 74 такти на 100–400 кГц (тут показано менше)", size=12, color=MUTED))

    # мітка «тепер картка слухає»
    frs.append(line(x1 - 10, top - 14, x1 - 10, base + 8, color=OK, sw=2, dash="4 3"))
    frs.append(text(x1 - 4, top - 20, "тепер слухає", size=11, color=OK, anchor="end", bold=True))

    return render(os.path.join(IMG, "warmup.svg"), W, H, *frs,
                  title="Перш ніж давати команди — прокрутити картці внутрішній лічильник")


# ── 3. Дерево розпізнавання типу картки ──────────────────────────────────────
def fig_branch_tree():
    W, H = 860, 500
    frs = []

    def box(cx, cy, s, fill=FILL, stroke=LINE, w=180):
        f = fitbox(cx - w / 2, cy - 28, w, 56, s, size=12, fill=fill, stroke=stroke, sw=2, rx=9)
        frs.append(f)
        return (cx, cy, w, 56)

    def link(a, b, lab, color=LINE):
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        frs.append(arrow(ax, ay + ah / 2, bx, by - bh / 2, color=color, sw=1.8))
        mx = (ax + bx) / 2; my = (ay + ah / 2 + by - bh / 2) / 2
        frs.append(text(mx, my, lab, size=11, color=color, bold=True))

    root = box(410, 60, "CMD8 (0x1AA)", "#eef2ff", NEG, w=200)
    v2   = box(230, 180, "R7 із луною 0x1AA\n→ картка v2.0+", FILL, LINE, w=220)
    old  = box(610, 180, "«недозволена»\n→ картка v1 або MMC", "#fbeee6", WAIT, w=230)

    link(root, v2, "відповіла", OK)
    link(root, old, "0x05", WAIT)

    a41  = box(230, 300, "ACMD41 (HCS=1)\nдоки busy зникне", "#fff6e6", WAIT, w=220)
    link(v2, a41, "", LINE)

    c58  = box(230, 415, "CMD58 → OCR", FILL, LINE, w=200)
    link(a41, c58, "готова", OK)

    sdhc = box(600, 375, "CCS=1 → SDHC/SDXC\nадреса = номер блоку", "#e9f7ef", OK, w=250)
    sdsc = box(600, 445, "CCS=0 → SDSC\nадреса = байт (×512)", FILL, LINE, w=250)
    frs.append(arrow(c58[0] + c58[2] / 2, c58[1] - 6, sdhc[0] - sdhc[2] / 2, sdhc[1], color=OK, sw=1.6))
    frs.append(arrow(c58[0] + c58[2] / 2, c58[1] + 6, sdsc[0] - sdsc[2] / 2, sdsc[1], color=LINE, sw=1.6))

    return render(os.path.join(IMG, "branch-tree.svg"), W, H, *frs,
                  title="Одна відповідь — одна розвилка: тип картки випадає з дерева")


if __name__ == "__main__":
    fig_state_graph()
    fig_warmup()
    fig_branch_tree()
    print("OK: figures written to", IMG)
