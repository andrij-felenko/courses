# -*- coding: utf-8 -*-
"""
Фігури для вставки r09-s3-a-descriptors.md
Рис. 4.9.3a.1 — scatter-gather: ланцюг дескрипторів у RAM + розкидані буфери
Рис. 4.9.3a.2 — порівняння: наївний шлях (копія → один DMA) vs scatter-gather

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.3a.1 — scatter-gather: ланцюг дескрипторів + розкидані буфери
# ══════════════════════════════════════════════════════════════════════════════
def fig1_descriptor_chain():
    W, H = 820, 480
    frags = []

    # ─── Геометрія дескрипторів (ліворуч, вертикально) ───────────────────────
    desc_cx = 200          # центр X для всіх трьох вузлів
    desc_y = [110, 240, 370]  # центри Y дескрипторів 0, 1, 2
    desc_w, desc_h = 200, 96  # розмір блоку дескриптора

    # Кольори: перші два звичайні (FILL), останній виділений (FIELD = зелений)
    desc_fills = [FILL, FILL, "#e8f8ee"]
    desc_strokes = [LINE, LINE, FIELD]

    # ─── Підпис зони RAM ─────────────────────────────────────────────────────
    frags.append(rect(40, 50, 330, 390, fill="#f9fafb", stroke=MUTED, sw=1.0, rx=10))
    frags.append(text(205, 72, "RAM (дескриптори)", size=12, color=MUTED, anchor="middle", bold=True))

    # ─── Малюємо три дескриптори ─────────────────────────────────────────────
    field_labels = [
        ["buf → hdr", "length=64", "owner=1", "eof=0", "next →"],
        ["buf → body", "length=512", "owner=1", "eof=0", "next →"],
        ["buf → crc", "length=4", "owner=1", "eof=1", "next=0"],
    ]
    desc_titles = ["desc[0]", "desc[1]", "desc[2]  (eof=1)"]

    for i, (cy, fill, stroke) in enumerate(zip(desc_y, desc_fills, desc_strokes)):
        x0 = desc_cx - desc_w / 2
        y0 = cy - desc_h / 2

        # Рамка вузла
        frags.append(rect(x0, y0, desc_w, desc_h, fill=fill, stroke=stroke, sw=2.0, rx=6))

        # Заголовок вузла
        title_fill = FIELD if i == 2 else INK
        frags.append(text(desc_cx, y0 + 15, desc_titles[i], size=12, color=title_fill,
                          anchor="middle", bold=True))

        # Роздільник під заголовком
        frags.append(line(x0 + 6, y0 + 22, x0 + desc_w - 6, y0 + 22, color=stroke, sw=1.0))

        # Поля дескриптора (дрібним шрифтом)
        fields = field_labels[i]
        field_y_start = y0 + 34
        for j, fld in enumerate(fields):
            color = FIELD if (i == 2 and j in (3, 4)) else MUTED
            bold = (i == 2 and j in (3, 4))
            frags.append(text(desc_cx, field_y_start + j * 13, fld, size=10,
                              color=color, anchor="middle", bold=bold))

    # ─── Стрілки next між дескрипторами ──────────────────────────────────────
    for i in range(2):
        y_from = desc_y[i] + desc_h / 2
        y_to   = desc_y[i + 1] - desc_h / 2
        mx = desc_cx + desc_w / 2 + 18
        # Ламана стрілка: вниз по боку
        frags.append(line(desc_cx + desc_w / 2, desc_y[i] + desc_h / 2 - 14,
                          mx, desc_y[i] + desc_h / 2 - 14, color=INK, sw=1.8))
        frags.append(line(mx, desc_y[i] + desc_h / 2 - 14,
                          mx, desc_y[i + 1] - desc_h / 2 + 14, color=INK, sw=1.8))
        frags.append(arrow(mx, desc_y[i + 1] - desc_h / 2 + 14,
                           desc_cx + desc_w / 2, desc_y[i + 1] - desc_h / 2 + 14, color=INK, sw=1.8))
        # Підпис «next»
        frags.append(text(mx + 16, (desc_y[i] + desc_y[i + 1]) / 2 + 4,
                          "next", size=10, color=MUTED, anchor="start", italic=True))

    # «next=0 (NULL)» під останнім дескриптором
    last_cx = desc_cx
    last_bot = desc_y[2] + desc_h / 2
    frags.append(line(last_cx, last_bot, last_cx, last_bot + 20, color=FIELD, sw=1.8))
    tb, _, _ = textbox(last_cx, last_bot + 36, "next=0 (NULL)", size=10,
                       fill="#e8f8ee", stroke=FIELD, sw=1.5)
    frags.append(tb)

    # ─── Розкидані буфери (праворуч) ─────────────────────────────────────────
    buf_data = [
        (590, 100,  "hdr",  "64 байти\nзаголовок"),
        (640, 260,  "body", "512 байтів\nкорисне навантаження"),
        (560, 390,  "crc",  "4 байти\nCRC"),
    ]
    buf_w, buf_h = 148, 56

    # Зона «різні місця RAM»
    frags.append(rect(470, 50, 310, 400, fill="#fdf8f0", stroke="#c8a060", sw=1.0, rx=10))
    frags.append(text(625, 72, "Інші місця RAM", size=12, color="#a07030",
                      anchor="middle", bold=True))

    buf_centers = []
    for bx, by, bname, blabel in buf_data:
        bx0, by0 = bx - buf_w / 2, by - buf_h / 2
        frags.append(rect(bx0, by0, buf_w, buf_h, fill="#fff8e8", stroke="#c8a060", sw=1.5, rx=6))
        frags.append(text(bx, by - 8, bname, size=13, color="#7a5000", anchor="middle", bold=True))
        frags.append(text(bx, by + 10, blabel, size=10, color=MUTED, anchor="middle"))
        buf_centers.append((bx, by))

    # ─── Пунктирні стрілки buf (від дескриптора до буфера) ──────────────────
    # Від лівого краю поля «buf» дескриптора до лівого краю буфера
    for i, (bx, by) in enumerate(buf_centers):
        # Виходимо з правого краю дескриптора (середина висоти поля «buf»)
        dx_out = desc_cx + desc_w / 2
        dy_out = desc_y[i] - desc_h / 2 + 32   # рядок «buf →»

        # Заходимо у лівий край буфера
        bx_in  = bx - buf_w / 2

        # Ламана: горизонтально до зони буферів, потім до буфера
        mid_x = 440
        frags.append(line(dx_out, dy_out, mid_x, dy_out, color=MUTED, sw=1.4, dash="5,4"))
        frags.append(line(mid_x, dy_out, mid_x, by, color=MUTED, sw=1.4, dash="5,4"))
        frags.append(arrow(mid_x, by, bx_in, by, color=MUTED, sw=1.4))

    # ─── Мітка «DMA старт: &desc[0]» ─────────────────────────────────────────
    start_x = desc_cx - desc_w / 2 - 20
    start_y = desc_y[0]
    frags.append(arrow(start_x - 60, start_y, start_x, start_y, color=POS, sw=2.2))
    tb2, _, _ = textbox(start_x - 100, start_y - 28, "DMA старт\n(&desc[0])", size=11,
                        fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(tb2)

    # ─── Мітка переривання на eof ────────────────────────────────────────────
    irq_x = desc_cx + desc_w / 2 + 80
    irq_y = desc_y[2]
    frags.append(line(desc_cx + desc_w / 2, irq_y, irq_x - 4, irq_y, color=FIELD, sw=1.8, dash="4,3"))
    frags.append(arrow(irq_x - 4, irq_y, irq_x + 60, irq_y, color=FIELD, sw=1.8))
    tb3, _, _ = textbox(irq_x + 112, irq_y, "IRQ\n(одне переривання)", size=11,
                        fill="#e8f8ee", stroke=FIELD, sw=1.5)
    frags.append(tb3)

    render(os.path.join(OUT, "fig-9-3a-1-descriptor-chain.svg"), W, H, *frags,
           title="Рис. 4.9.3a.1. Дескриптори як вузли однозвʼязного списку в RAM")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.3a.2 — наївний шлях vs scatter-gather
# ══════════════════════════════════════════════════════════════════════════════
def fig2_sg_vs_naive():
    W, H = 820, 400
    frags = []

    # ─── Ліва панель: наївний шлях ────────────────────────────────────────────
    panel_w = 360
    frags.append(rect(20, 30, panel_w, 340, fill="#fff4f4", stroke=POS, sw=1.5, rx=8))
    frags.append(text(20 + panel_w / 2, 54, "Наївний шлях", size=14, color=POS,
                      anchor="middle", bold=True))
    frags.append(text(20 + panel_w / 2, 72, "(CPU копіює → один DMA)", size=11,
                      color=MUTED, anchor="middle", italic=True))

    # Три розкиданих буфери (ліворуч)
    src_names = ["hdr", "body", "crc"]
    src_ys = [120, 200, 285]
    src_cx = 100
    for name, sy in zip(src_names, src_ys):
        frags.append(rect(src_cx - 36, sy - 18, 72, 36, fill="#ffe8e8", stroke=POS, sw=1.2, rx=4))
        frags.append(text(src_cx, sy + 5, name, size=12, color=POS, anchor="middle", bold=True))

    # Великий буфер-ціль посередині/праворуч
    big_cx, big_cy, big_w, big_h = 270, 200, 80, 150
    frags.append(rect(big_cx - big_w / 2, big_cy - big_h / 2, big_w, big_h,
                      fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(big_cx, big_cy - 30, "big_buf", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(big_cx, big_cy - 12, "(склеєне)", size=10, color=MUTED, anchor="middle"))
    frags.append(text(big_cx, big_cy + 8, "hdr", size=10, color=POS, anchor="middle"))
    frags.append(line(big_cx - big_w / 2 + 6, big_cy + 20, big_cx + big_w / 2 - 6, big_cy + 20,
                      color=POS, sw=0.8, dash="3,2"))
    frags.append(text(big_cx, big_cy + 32, "body", size=10, color=POS, anchor="middle"))
    frags.append(line(big_cx - big_w / 2 + 6, big_cy + 44, big_cx + big_w / 2 - 6, big_cy + 44,
                      color=POS, sw=0.8, dash="3,2"))
    frags.append(text(big_cx, big_cy + 56, "crc", size=10, color=POS, anchor="middle"))

    # Стрілки CPU memcpy (суцільні, від кожного шматка до big_buf)
    for sy in src_ys:
        frags.append(arrow(src_cx + 36, sy, big_cx - big_w / 2, big_cy + (sy - 200) * 0.5,
                           color=NEG, sw=1.6))

    # Підпис CPU
    frags.append(text(185, 150, "CPU memcpy\n× 3", size=10, color=NEG, anchor="middle", bold=True))

    # Підпис зайвої роботи
    tb, _, _ = textbox(20 + panel_w / 2, 355, "CPU витрачає час на склейку", size=10,
                       fill="#fdecea", stroke=POS, sw=1.2)
    frags.append(tb)

    # ─── Права панель: scatter-gather ────────────────────────────────────────
    rx0 = 440
    frags.append(rect(rx0, 30, panel_w, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(rx0 + panel_w / 2, 54, "Scatter-gather", size=14, color=FIELD,
                      anchor="middle", bold=True))
    frags.append(text(rx0 + panel_w / 2, 72, "(DMA сама обходить ланцюг)", size=11,
                      color=MUTED, anchor="middle", italic=True))

    # Три дескриптори (ліворуч на правій панелі)
    rdesc_cx = rx0 + 100
    rdesc_ys = [120, 210, 300]
    rdesc_names = ["desc[0]\nbuf=hdr", "desc[1]\nbuf=body", "desc[2]\nbuf=crc\neof=1"]
    for i, (ry, rname) in enumerate(zip(rdesc_ys, rdesc_names)):
        fill = "#e8f8ee" if i == 2 else FILL
        stroke = FIELD if i == 2 else LINE
        fb = fitbox(rdesc_cx - 56, ry - 28, 112, 56, rname, size=10,
                    fill=fill, stroke=stroke, sw=1.5)
        frags.append(fb)

    # Стрілки next між дескрипторами
    for i in range(2):
        frags.append(arrow(rdesc_cx, rdesc_ys[i] + 28, rdesc_cx, rdesc_ys[i + 1] - 28,
                           color=INK, sw=1.6))

    # Три буфери (праворуч на правій панелі)
    rbuf_cx = rx0 + 290
    rbuf_ys = [120, 210, 300]
    rbuf_names = ["hdr", "body", "crc"]
    for by, bname in zip(rbuf_ys, rbuf_names):
        frags.append(rect(rbuf_cx - 32, by - 20, 64, 40, fill="#fff8e8", stroke="#c8a060", sw=1.2, rx=4))
        frags.append(text(rbuf_cx, by + 5, bname, size=12, color="#7a5000", anchor="middle", bold=True))

    # Пунктирні стрілки buf (від дескриптора до буфера)
    for ry, by in zip(rdesc_ys, rbuf_ys):
        frags.append(arrow(rdesc_cx + 56, ry, rbuf_cx - 32, by, color=MUTED, sw=1.4))

    # DMA старт → перший дескриптор
    frags.append(arrow(rx0 + 20, rdesc_ys[0], rdesc_cx - 56, rdesc_ys[0], color=FIELD, sw=2.0))
    frags.append(text(rx0 + 38, rdesc_ys[0] - 12, "DMA\nстарт", size=9, color=FIELD,
                      anchor="middle", bold=True))

    # IRQ лише на останньому
    irq_tx = rdesc_cx + 56 + 10
    frags.append(line(rdesc_cx + 56, rdesc_ys[2], irq_tx + 40, rdesc_ys[2],
                      color=FIELD, sw=1.6, dash="4,3"))
    frags.append(text(irq_tx + 65, rdesc_ys[2] + 4, "IRQ ×1", size=10,
                      color=FIELD, anchor="start", bold=True))

    # Підпис економії
    tb2, _, _ = textbox(rx0 + panel_w / 2, 355, "CPU вільна під час передачі", size=10,
                        fill="#e8f8ee", stroke=FIELD, sw=1.2)
    frags.append(tb2)

    render(os.path.join(OUT, "fig-9-3a-2-sg-vs-naive.svg"), W, H, *frags,
           title="Рис. 4.9.3a.2. Наївний шлях vs scatter-gather")


if __name__ == "__main__":
    fig1_descriptor_chain()
    print("OK: fig-9-3a-1-descriptor-chain.svg")
    fig2_sg_vs_naive()
    print("OK: fig-9-3a-2-sg-vs-naive.svg")
