# -*- coding: utf-8 -*-
"""
Фігури для вставки r09-history-dma-channels.md
Рис. 4.9.0.1 — стрічка часу еволюції канального вводу-виводу (704 → DMA МК)
Рис. 4.9.0.2 — порівняння «канал IBM» проти «DMA мікроконтролера»

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.0.1 — горизонтальна стрічка часу: 6 віх
# ══════════════════════════════════════════════════════════════════════════════
def fig1_timeline():
    W, H = 860, 320
    frags = []

    # ── Горизонтальна вісь ───────────────────────────────────────────────────
    axis_y = 150
    ax_x1, ax_x2 = 50, 810
    frags.append(arrow(ax_x1, axis_y, ax_x2, axis_y, color=LINE, sw=2.5))

    # ── Дані вузлових точок ─────────────────────────────────────────────────
    milestones = [
        {"x": 100, "year": "1953",  "label": "IBM 704\nProgrammed I/O",
         "desc": "ядро саме\nгнало кожен байт",
         "fill": "#fdecea", "stroke": POS},
        {"x": 235, "year": "1957",  "label": "IBM 709\nData Synchronizer",
         "desc": "перший канал:\nпаралельний I/O",
         "fill": "#fff6e0", "stroke": "#c0a020"},
        {"x": 378, "year": "1959",  "label": "IBM 7090\nКанали 7607/7606",
         "desc": "до 8 каналів;\nядро лише ініціює",
         "fill": "#eef6ef", "stroke": FIELD},
        {"x": 521, "year": "1964",  "label": "System/360\nCCW-програма",
         "desc": "канал виконує\nзбережену програму",
         "fill": "#eaf0fd", "stroke": NEG},
        {"x": 664, "year": "1981",  "label": "System/370-XA\nПроцесор каналів",
         "desc": "RISC-процесор\nдля I/O",
         "fill": "#f4eaf8", "stroke": "#8e44ad"},
        {"x": 784, "year": "сьогодні", "label": "DMA у МК\n(ESP32 та ін.)",
         "desc": "спрощений нащадок:\nфіксований переказ",
         "fill": FILL, "stroke": LINE},
    ]

    BOX_W, BOX_H = 130, 52
    DOT_R = 9

    for i, m in enumerate(milestones):
        x = m["x"]
        # Чергуємо: парні — зверху осі, непарні — знизу
        above = (i % 2 == 0)
        dot_y = axis_y

        # ── Крапка на осі ─────────────────────────────────────────────────
        frags.append(circle(x, dot_y, DOT_R, fill=m["fill"], stroke=m["stroke"], sw=2.2))

        # ── Рік під/над крапкою ───────────────────────────────────────────
        year_y = dot_y + DOT_R + 16 if above else dot_y - DOT_R - 8
        frags.append(text(x, year_y, m["year"], size=11, color=MUTED, anchor="middle", bold=False))

        # ── Рамка-підпис ──────────────────────────────────────────────────
        if above:
            box_cy = dot_y - DOT_R - 18 - BOX_H / 2
            connector_y2 = dot_y - DOT_R
            connector_y1 = box_cy + BOX_H / 2
        else:
            box_cy = dot_y + DOT_R + 22 + BOX_H / 2
            connector_y1 = dot_y + DOT_R
            connector_y2 = box_cy - BOX_H / 2

        frags.append(line(x, connector_y1, x, connector_y2, color=m["stroke"], sw=1.4, dash="5,3"))
        frags.append(fitbox(x - BOX_W / 2, box_cy - BOX_H / 2, BOX_W, BOX_H,
                            m["label"], size=11, fill=m["fill"], stroke=m["stroke"],
                            sw=1.8, bold=True))

        # ── Коротке пояснення під/над рамкою ──────────────────────────────
        if above:
            desc_y = box_cy + BOX_H / 2 + 14
        else:
            desc_y = box_cy - BOX_H / 2 - 28
        for di, dl in enumerate(m["desc"].split("\n")):
            frags.append(text(x, desc_y + di * 14, dl, size=10, color=MUTED,
                              anchor="middle", italic=True))

    # ── Підпис-підсумок унизу ────────────────────────────────────────────────
    frags.append(text(W // 2, H - 14,
                      "Одна ідея «звільнити ядро від I/O» пройшла від кімнатної шафи до кутка кремнію за 70 років.",
                      size=11, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, "fig-channel-timeline.svg"), W, H, *frags,
           title="Рис. 4.9.0.1. Еволюція канального I/O: від IBM 704 до DMA мікроконтролера")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.0.2 — порівняння «канал IBM» vs «DMA МК»
# ══════════════════════════════════════════════════════════════════════════════
def fig2_channel_vs_dma():
    W, H = 820, 420
    frags = []

    # ── Два стовпці ─────────────────────────────────────────────────────────
    mid = W // 2
    col_w = 330

    # Заголовки стовпців
    frags.append(fitbox(mid - col_w - 10, 14, col_w, 38,
                        "Канал IBM (System/360)",
                        size=14, fill="#eaf0fd", stroke=NEG, sw=2, bold=True))
    frags.append(fitbox(mid + 10, 14, col_w, 38,
                        "DMA мікроконтролера (ESP32)",
                        size=14, fill=FILL, stroke=LINE, sw=2, bold=True))

    # ── Розділова лінія ──────────────────────────────────────────────────────
    frags.append(line(mid, 10, mid, H - 50, color=MUTED, sw=1.2, dash="6,4"))

    # ── Спільне (угорі, широка плашка) ──────────────────────────────────────
    common_y = 72
    common_h = 46
    common_label = "СПІЛЬНЕ: окремий апаратний агент на шині — ядро вільне рахувати"
    frags.append(fitbox(30, common_y, W - 60, common_h,
                        common_label, size=12,
                        fill="#eef6ef", stroke=FIELD, sw=2, bold=True))

    # ── Блоки «канал IBM» ───────────────────────────────────────────────────
    ibm_items = [
        ("Ядро лишає в пам'яті\nканальну програму (CCW)", NEG, "#eaf0fd"),
        ("Канал сам виконує CCW:\nчитай / перемотай / читай", NEG, "#eaf0fd"),
        ("Умовні переходи й\nперевірка даних у програмі", NEG, "#eaf0fd"),
        ("Повноцінна збережена\nпрограма з гілками", NEG, "#d6e8fd"),
    ]
    bx = mid - col_w - 10
    by = common_y + common_h + 14
    bw = col_w
    bh = 46
    gap = 10

    for lbl, stk, fl in ibm_items:
        frags.append(fitbox(bx, by, bw, bh, lbl, size=11,
                            fill=fl, stroke=stk, sw=1.5))
        by += bh + gap

    # Стрілки між блоками IBM
    arrow_x = bx + bw // 2
    start_y = common_y + common_h + 14 + bh
    for _ in range(len(ibm_items) - 1):
        frags.append(arrow(arrow_x, start_y + gap // 2 - 3,
                           arrow_x, start_y + gap // 2 + 3 + 1, color=NEG, sw=1.5))
        start_y += bh + gap

    # ── Блоки «DMA МК» ───────────────────────────────────────────────────────
    dma_items = [
        ("Ядро задає один дескриптор:\nадреса → адреса, N байтів", LINE, FILL),
        ("DMA виконує фіксований\nпереказ (або список блоків)", LINE, FILL),
        ("Гілок немає:\ntільки scatter-gather (§4.9.3)", MUTED, "#f0f0f0"),
        ("Спрощений нащадок:\nлише «скопіюй цей блок»", FIELD, "#eef6ef"),
    ]
    dx = mid + 10
    dy = common_y + common_h + 14
    dw = col_w

    for lbl, stk, fl in dma_items:
        frags.append(fitbox(dx, dy, dw, bh, lbl, size=11,
                            fill=fl, stroke=stk, sw=1.5))
        dy += bh + gap

    # ── Підсумок знизу ───────────────────────────────────────────────────────
    conclusion_y = H - 48
    frags.append(fitbox(30, conclusion_y, W - 60, 36,
                        "DMA — це канал, з якого зняли процесор: той самий агент на шині, але виконує лише фіксований переказ.",
                        size=12, fill="#fff6e0", stroke="#c0a020", sw=2, bold=False))

    render(os.path.join(OUT, "fig-channel-vs-dma.svg"), W, H, *frags,
           title="Рис. 4.9.0.2. Канал IBM проти DMA мікроконтролера")


if __name__ == "__main__":
    fig1_timeline()
    print("OK: fig-channel-timeline.svg")
    fig2_channel_vs_dma()
    print("OK: fig-channel-vs-dma.svg")
