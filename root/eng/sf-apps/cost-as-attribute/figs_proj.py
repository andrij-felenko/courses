# -*- coding: utf-8 -*-
# Фігури для вставки proj-cbam.md.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def ctext(cx, cy, lines, size=13, bold=False, color=INK):
    """Багаторядковий текст, вертикально відцентрований навколо cy."""
    if isinstance(lines, str):
        lines = [lines]
    y0 = cy - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
    return mtext(cx, y0, lines, size=size, bold=bold, color=color)


def cell(left, top, w, h, s, size=13, bold=False, fill=BG, color=INK):
    r = rect(left, top, w, h, fill=fill, stroke=LINE, sw=1.2)
    t = ctext(left + w / 2, top + h / 2, s, size=size, bold=bold, color=color)
    return r + t


# ── Фігура 1: звідки береться вигода — вага·(корисність_після − до) ───────────
def fig_benefit():
    W, H = 1015, 340
    els = [text(W / 2, 30, "Вигода стратегії = Σ вага·(корисність_після − корисність_до)", size=16, bold=True)]

    # межі колонок (left, width)
    cols = [
        (20, 150),    # 0 стратегія
        (170, 140),   # 1 продуктивність
        (310, 130),   # 2 доступність
        (440, 135),   # 3 змінюваність
        (575, 120),   # 4 безпека
        (695, 105),   # 5 вигода
        (800, 100),   # 6 вартість
        (900, 95),    # 7 ROI
    ]
    y_head, h_head = 58, 54
    rows_y, h_row = [112, 156, 200, 244], 44

    green = "#eafaf0"
    amber = "#fff8e1"
    grayh = "#eef1f4"

    header = [
        ("стратегія", grayh),
        ("продуктивність\nвага 2", grayh),
        ("доступність\nвага 1.5", grayh),
        ("змінюваність\nвага 1", grayh),
        ("безпека\nвага 1", grayh),
        ("вигода\nΣ вага·Δ", "#dff3e6"),
        ("вартість\nтижні", grayh),
        ("ROI", "#fdf0cf"),
    ]
    for (lx, w), (s, fl) in zip(cols, header):
        els.append(cell(lx, y_head, w, h_head, s, size=12, bold=True, fill=fl))

    # рядки: назва, Δ по атрибутах (— де нема), вигода, вартість, ROI
    data = [
        ("CDN",     "40→65", "—",     "—",     "—",     "50",  "2",  "25.0"),
        ("кеш",     "40→65", "50→70", "—",     "—",     "80",  "4",  "20.0"),
        ("конвеєр", "40→55", "50→90", "50→80", "—",     "120", "10", "12.0"),
        ("платежі", "40→50", "—",     "50→90", "60→90", "90",  "30", "3.0"),
    ]
    fills = [BG, BG, BG, BG, BG, green, BG, amber]
    bolds = [True, False, False, False, False, True, False, True]
    for ry, row in zip(rows_y, data):
        for (lx, w), val, fl, bd in zip(cols, row, fills, bolds):
            els.append(cell(lx, ry, w, h_row, val, size=13, bold=bd, fill=fl))

    els.append(text(W / 2, H - 16,
                    "числа 50 · 80 · 120 · 90 — не з голови: кожне зібране з корисностей по атрибутах, зважених важливістю для стейкхолдерів",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'cbam-benefit.svg'), W, H, *els)


# ── Фігура 2: жадібний за ROI лишає простій і програє точному ─────────────────
def fig_greedy_trap():
    W, H = 1015, 300
    els = [text(W / 2, 30, "Жадібний за ROI лишає бюджет недоробленим — і програє точному", size=16, bold=True)]

    x0 = 210            # старт смуги (після підпису рядка)
    px = 55             # пікселів на тиждень
    bh = 46             # висота смуги

    green = ("#d5f0e0", FIELD)
    blue = ("#dbe6fb", NEG)
    amber = ("#fde7c9", "#b8860b")
    gray = ("#eeeeee", "#b0b6bd")

    def seg(left, weeks, name, fill_stroke, textcol=INK):
        w = weeks * px
        r = rect(left, seg.top, w, bh, fill=fill_stroke[0], stroke=fill_stroke[1], sw=1.6)
        t = ctext(left + w / 2, seg.top + bh / 2, [name, "%d тиж" % weeks], size=13, bold=True, color=textcol)
        return left + w, r + t

    # ── рядок 1: жадібний ──
    seg.top = 74
    els.append(ctext(112, seg.top + bh / 2, ["жадібний", "за ROI"], size=13, bold=True))
    x, frag = seg(x0, 2, "CDN", green); els.append(frag)
    x, frag = seg(x, 4, "кеш", blue); els.append(frag)
    # простій — сірий блок без штрихування (щоб лінії не різали напис)
    idle_w = 6 * px
    els.append(rect(x, seg.top, idle_w, bh, fill=gray[0], stroke=gray[1], sw=1.4))
    els.append(ctext(x + idle_w / 2, seg.top + bh / 2, ["простій 6 тижнів", "(бюджет не дороблено)"],
                     size=12, bold=False, color=MUTED))
    els.append(ctext(942, seg.top + bh / 2, ["вигода", "130"], size=14, bold=True, color=POS))

    # ── рядок 2: точний ──
    seg.top = 156
    els.append(ctext(112, seg.top + bh / 2, ["точний", "(наплічник)"], size=13, bold=True))
    x, frag = seg(x0, 2, "CDN", green); els.append(frag)
    x, frag = seg(x, 10, "конвеєр", amber); els.append(frag)
    els.append(ctext(942, seg.top + bh / 2, ["вигода", "170 ✓"], size=14, bold=True, color=FIELD))

    # ── вісь тижнів під нижньою смугою ──
    ax_y = 156 + bh + 8
    for wk in (0, 2, 4, 6, 8, 10, 12):
        tx = x0 + wk * px
        els.append(line(tx, ax_y, tx, ax_y + 6, color=MUTED, sw=1.2))
        els.append(text(tx, ax_y + 22, str(wk), size=11, color=MUTED))
    els.append(text(x0 + 6 * px, ax_y + 40, "бюджет — 12 тижнів", size=11, color=MUTED, italic=True))

    els.append(text(W / 2, H - 12,
                    "той самий бюджет 12: жадібний бере CDN+кеш (130) і лишає 6 тижнів простою; точний бере CDN+конвеєр (170) без простою",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'greedy-trap.svg'), W, H, *els)


if __name__ == '__main__':
    fig_benefit()
    fig_greedy_trap()
    print("figs_proj done")
