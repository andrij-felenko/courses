# -*- coding: utf-8 -*-
"""Фігури до теми «Подвійна буферизація».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

DMA_C = NEG      # DMA пише — холодний синій
CPU_C = POS      # ядро читає — теплий червоний
GOLD  = "#b7861b"  # обернення індексу (тепле, читабельне)


# ── Кільце-аннулус: N комірок між двома радіусами ────────────────────────────
def ring_cell(cx, cy, r_out, r_in, a0, a1, fill, stroke, sw=1.4):
    """Сегмент кільця (трапеція по дузі) між кутами a0..a1 (радіани, від 12 год за годинниковою)."""
    def pt(r, a):
        return (cx + r * math.sin(a), cy - r * math.cos(a))
    x0o, y0o = pt(r_out, a0); x1o, y1o = pt(r_out, a1)
    x0i, y0i = pt(r_in, a0);  x1i, y1i = pt(r_in, a1)
    large = 1 if (a1 - a0) > math.pi else 0
    d = ("M%.1f,%.1f L%.1f,%.1f A%.1f,%.1f 0 %d,1 %.1f,%.1f L%.1f,%.1f "
         "A%.1f,%.1f 0 %d,0 %.1f,%.1f Z" %
         (x0i, y0i, x0o, y0o, r_out, r_out, large, x1o, y1o, x1i, y1i,
          r_in, r_in, large, x0i, y0i))
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def ring(cx, cy, r_out, r_in, n, occupied, label="buf[N]"):
    """Намалювати кільце з n комірок; occupied — множина індексів «зайнято» (синіх)."""
    out = []
    for i in range(n):
        a0 = 2 * math.pi * i / n + 0.04
        a1 = 2 * math.pi * (i + 1) / n - 0.04
        am = (a0 + a1) / 2
        fill = "#d0e8ff" if i in occupied else FILL
        st = DMA_C if i in occupied else LINE
        out.append(ring_cell(cx, cy, r_out, r_in, a0, a1, fill, st,
                             sw=2.0 if i in occupied else 1.4))
        rm = (r_out + r_in) / 2
        tx, ty = cx + rm * math.sin(am), cy - rm * math.cos(am) + 4
        out.append(text(tx, ty, str(i), size=12, color=INK))
    out.append(text(cx, cy + 4, label, size=12, color=MUTED))
    return out


# ── 1. Чотири фази ping-pong ─────────────────────────────────────────────────
def fig_pingpong_phases():
    W, H = 760, 330
    f = [text(W / 2, 26, "Подвійна буферизація: ролі чергуються", size=15, bold=True)]

    # дві коробки A і B, чотири знімки в часі
    phases = [
        ("фаза 1", "DMA → A", "ядро ← B", DMA_C, CPU_C),
        ("фаза 2 (обмін)", "DMA → B", "ядро ← A", CPU_C, DMA_C),
    ]
    col_w = 330
    x0 = 40
    for i, (cap, top, bot, ca, cb) in enumerate(phases):
        x = x0 + i * (col_w + 20)
        f.append(text(x + col_w / 2, 60, cap, size=12.5, color=MUTED, bold=True))
        # буфер A
        f.append(rect(x, 80, col_w, 70, fill=FILL, stroke=ca, sw=2))
        f.append(text(x + 24, 122, "A", size=20, color=ca, bold=True, anchor="start"))
        f.append(text(x + col_w / 2 + 20, 122, top, size=13, color=ca, bold=True))
        # буфер B
        f.append(rect(x, 165, col_w, 70, fill=FILL, stroke=cb, sw=2))
        f.append(text(x + 24, 207, "B", size=20, color=cb, bold=True, anchor="start"))
        f.append(text(x + col_w / 2 + 20, 207, bot, size=13, color=cb, bold=True))

    # стрілка обміну між колонками
    f.append(arrow(x0 + col_w + 4, 158, x0 + col_w + 16, 158, color=INK, sw=2))
    f.append(text(x0 + col_w + 10, 252, "переривання «готово»\n→ ролі міняються", size=10,
                  color=MUTED, italic=True))

    f.append(text(W / 2, 300,
                  "у будь-який момент кожен буфер належить лише одному: DMA пише або ядро читає — ніколи разом",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "pingpong-phases.svg"), W, H, *f)


# ── 2. Обмін у момент завершення (часова шкала) ──────────────────────────────
def fig_swap_handoff():
    W, H = 780, 300
    f = [text(W / 2, 26, "Обмін у мить завершення передачі", size=15, bold=True)]

    lane_dma, lane_cpu = 90, 175
    f.append(text(28, lane_dma + 5, "DMA", size=12, color=DMA_C, bold=True, anchor="start"))
    f.append(text(28, lane_cpu + 5, "ядро", size=12, color=CPU_C, bold=True, anchor="start"))

    # часова вісь
    x_start, x_end = 90, 740
    f.append(line(x_start, 235, x_end, 235, color=INK, sw=1.5))
    f.append(arrow(x_end - 2, 235, x_end + 8, 235, color=INK, sw=1.5))
    f.append(text(x_end, 255, "час", size=11, color=MUTED, anchor="end", italic=True))

    seg = (x_end - x_start) / 3.0
    # DMA: пише A, потім B, потім A
    dma_fill = [("пише A", DMA_C), ("пише B", DMA_C), ("пише A", DMA_C)]
    cpu_fill = [("(чекає)", MUTED), ("читає A", CPU_C), ("читає B", CPU_C)]
    for i in range(3):
        x = x_start + i * seg
        f.append(rect(x, lane_dma - 18, seg - 6, 36, fill="#eaf0fd",
                      stroke=DMA_C, sw=1.6))
        f.append(text(x + (seg - 6) / 2, lane_dma + 5, dma_fill[i][0], size=12,
                      color=DMA_C, bold=True))
        cf, cc = cpu_fill[i]
        fillc = "#fdecea" if cc == CPU_C else "#f0f0f0"
        f.append(rect(x, lane_cpu - 18, seg - 6, 36, fill=fillc, stroke=cc, sw=1.6))
        f.append(text(x + (seg - 6) / 2, lane_cpu + 5, cf, size=12, color=cc,
                      bold=(cc == CPU_C)))

    # вертикальні лінії обміну на межах сегментів
    for i in (1, 2):
        xb = x_start + i * seg - 3
        f.append(line(xb, 70, xb, 235, color=FIELD, sw=1.6, dash="4,3"))
        f.append(text(xb, 62, "обмін", size=10, color=FIELD, bold=True))

    f.append(text(W / 2, 285,
                  "переривання завершення міняє ролі за один такт; ядро завжди працює з повним, нерухомим буфером",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "swap-handoff.svg"), W, H, *f)


# ── 3. Один буфер (розрив) проти двох (чисто) ────────────────────────────────
def fig_tearing_vs_clean():
    W, H = 780, 340
    f = [text(W / 2, 26, "Чому одного буфера замало", size=15, bold=True)]

    # ── верх: один буфер → розрив/гонка ──
    f.append(text(40, 64, "Один буфер: DMA пише, ядро читає те саме", size=12.5,
                  color=POS, bold=True, anchor="start"))
    bx, by, bw, bh = 40, 78, 700, 50
    cells = 14
    cw = bw / cells
    split = 8  # межа «новий | старий»
    for i in range(cells):
        x = bx + i * cw
        fill = "#eaf0fd" if i < split else "#fdecea"
        f.append(rect(x, by, cw, bh, fill=fill, stroke=LINE, sw=1, rx=0))
    f.append(text(bx + split * cw / 2, by + bh + 16, "свіже (DMA)", size=10,
                  color=DMA_C, italic=True))
    f.append(text(bx + (split + cells) / 2 * cw, by + bh + 16, "старе", size=10,
                  color=POS, italic=True))
    # курсор DMA посередині
    f.append(line(bx + split * cw, by - 8, bx + split * cw, by + bh + 8,
                  color=INK, sw=2))
    f.append(text(bx + split * cw, by - 14, "курсор DMA", size=10, color=INK, bold=True))
    f.append(text(W / 2, by + bh + 38,
                  "ядро читає тут і тепер → дістає половину нового, половину старого = розрив (tearing)",
                  size=10.5, color=POS, italic=True))

    # ── низ: два буфери → чисто ──
    f.append(text(40, 196, "Два буфери: розведені у просторі — конфлікту немає", size=12.5,
                  color=FIELD, bold=True, anchor="start"))
    ay, ah = 212, 46
    # A — пише DMA
    f.append(rect(40, ay, 330, ah, fill="#eaf0fd", stroke=DMA_C, sw=2))
    f.append(text(205, ay + ah / 2 + 5, "A — DMA пише (зайнятий)", size=12.5,
                  color=DMA_C, bold=True))
    # B — читає ядро
    f.append(rect(410, ay, 330, ah, fill="#fdecea", stroke=CPU_C, sw=2))
    f.append(text(575, ay + ah / 2 + 5, "B — ядро читає (стабільний)", size=12.5,
                  color=CPU_C, bold=True))
    f.append(text(W / 2, ay + ah + 30,
                  "кожен працює зі своєю пам'яттю → ні розриву, ні втрати; на завершенні ролі міняються",
                  size=10.5, color=FIELD, italic=True))

    render(os.path.join(IMG, "tearing-vs-clean.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для вставок (math-buffer-sizing, proj-ring-buffer)
# ════════════════════════════════════════════════════════════════════════════

# ── math-1: часова шкала ping-pong (t_half >= t_proc) ────────────────────────
def fig_pingpong_timeline():
    W, H = 860, 360
    f = [text(W / 2, 28, "Подвійна буферизація: часова шкала DMA + ядро", size=16, bold=True)]
    f.append(text(W / 2, 50, "поки DMA пише B -> ядро читає A; умова t_half >= t_proc, інакше overrun",
                  size=11, color=MUTED))
    f.append(text(70, 127, "DMA", size=13, color=DMA_C, bold=True, anchor="end"))
    f.append(text(70, 227, "ядро", size=13, color=FIELD, bold=True, anchor="end"))

    dma = [("Пише A", "#dbeafe"), ("Пише B", "#bfdbfe"), ("Пише A", "#dbeafe"), ("Пише B", "#bfdbfe")]
    for i, (lab, fill) in enumerate(dma):
        x = 80 + i * 180
        f.append(rect(x, 100, 177, 44, fill=fill, stroke=DMA_C, sw=1.8))
        f.append(text(x + 88.5, 127, lab, size=12, color=DMA_C, bold=True))

    cpu = [("Обробляє A", 260), ("Обробляє B", 440), ("Обробляє A", 620)]
    for lab, x in cpu:
        f.append(rect(x, 200, 132, 44, fill="#d1fae5", stroke=FIELD, sw=1.8))
        f.append(text(x + 66, 227, lab, size=12, color=FIELD, bold=True))

    for xb in (260, 440, 620):
        f.append(line(xb, 86, xb, 274, color="#aaaaaa", sw=1.2, dash="5,4"))

    f.append(line(80, 82, 260, 82, color=DMA_C, sw=1.6))
    f.append(line(80, 76, 80, 88, color=DMA_C, sw=1.6))
    f.append(line(260, 76, 260, 88, color=DMA_C, sw=1.6))
    f.append(text(170, 76, "t_half = N / Rs", size=11, color=DMA_C, bold=True))
    f.append(line(260, 266, 395, 266, color=FIELD, sw=1.6))
    f.append(line(260, 260, 260, 272, color=FIELD, sw=1.6))
    f.append(line(395, 260, 395, 272, color=FIELD, sw=1.6))
    f.append(text(327, 282, "t_proc", size=11, color=FIELD, bold=True))

    body, _, _ = textbox(430, 330, "Умова без втрат:  t_half >= t_proc  ->  N >= Rs * t_proc",
                         size=13, fill="#f0fff4", stroke=FIELD, sw=2.0, bold=True)
    f.append(body)
    ob, _, _ = textbox(557, 226, "Якщо t_proc > t_half\n-> overrun!", size=11,
                       fill="#fef2f2", stroke=POS, sw=1.8, color=POS)
    f.append(ob)
    render(os.path.join(IMG, "pingpong-timeline.svg"), W, H, *f)


# ── math-2: компроміс вибору N (дві стіни) ───────────────────────────────────
def fig_tradeoff():
    W, H = 800, 420
    f = [text(W / 2, 28, "Вибір N: дві стіни - overrun і RAM/затримка", size=16, bold=True)]
    f.append(text(W / 2, 50, "ліворуч - замало (втрати даних), праворуч - забагато (марна SRAM + лаг)",
                  size=11, color=MUTED))
    ax0, ax1, ay = 100, 720, 320
    f.append(arrow(90, ay, 740, ay, color=LINE, sw=2.0))
    f.append(text(750, ay + 5, "N", size=14, color=LINE, anchor="start", bold=True))
    ticks = [64, 128, 256, 512, 1024, 2048, 4096]
    for i, t in enumerate(ticks):
        x = ax0 + (ax1 - ax0) * i / (len(ticks) - 1)
        f.append(line(x, ay - 5, x, ay + 5, color=LINE, sw=1.2))
        f.append(text(x, ay + 20, str(t), size=10, color=MUTED))

    def xof(t):
        i = ticks.index(t)
        return ax0 + (ax1 - ax0) * i / (len(ticks) - 1)

    x_over = (xof(128) + xof(256)) / 2
    x_work = xof(512)
    f.append(rect(ax0, 80, x_over - ax0, 240, fill="#fef2f2", stroke="none", sw=0, rx=0))
    f.append(rect(x_over, 80, xof(4096) - x_over, 240, fill="#f0fff4", stroke="none", sw=0, rx=0))
    f.append(rect(xof(2048), 80, xof(4096) - xof(2048), 240, fill="#eff6ff", stroke="none", sw=0, rx=0))
    f.append(line(x_over, 70, x_over, ay, color=POS, sw=2.0, dash="6,3"))
    f.append(line(x_work, 70, x_work, ay, color=FIELD, sw=1.5, dash="4,4"))
    f.append(text(x_work, 62, "Rs * t_proc * k", size=10, color=FIELD, bold=True))

    ob, _, _ = textbox((ax0 + x_over) / 2, 188,
                       "OVERRUN\n(N < Rs * t_proc)\nDMA дожене\nядро -> втрата",
                       size=11, fill="#fef2f2", stroke=POS, sw=1.8, color=POS)
    f.append(ob)
    rb, _, _ = textbox(xof(4096) - 52, 188, "Надмір RAM\n+ зростання\nзатримки",
                       size=11, fill="#eff6ff", stroke=DMA_C, sw=1.8, color=DMA_C)
    f.append(rb)

    pts = []
    for i in range(0, 51):
        t = 128 + (4096 - 128) * i / 50
        xx = ax0 + (ax1 - ax0) * (math.log(t, 2) - math.log(64, 2)) / (math.log(4096, 2) - math.log(64, 2))
        yy = 294 - (math.log(t, 2) - math.log(128, 2)) * 22
        pts.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" stroke="%s" stroke-width="2" fill="none" '
             'stroke-dasharray="5,3" opacity="0.7"/>' % (" ".join(pts), DMA_C))
    f.append(text(xof(2048) + 30, 150, "B_total = 2N * байт", size=10, color=DMA_C))

    for xx, lab, col in ((x_over, "200\n(впритул,\noverrun)", POS),
                         (x_work, "512\n(робоча)", FIELD),
                         (xof(4096), "4096\n(надмір)", DMA_C)):
        f.append(circle(xx, ay, 8, fill=col, stroke=col, sw=2.0))
        f.append(mtext(xx, 285, lab, size=10, color=col, bold=True))

    band, _, _ = textbox(W / 2, 390,
                         "Робоча зона: N = Rs * t_proc * k, округлити вгору до степеня 2",
                         size=12, fill="#f0fff4", stroke=FIELD, sw=1.8, bold=True)
    f.append(band)
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── proj-1: кільце - індекси head/tail, обернення ────────────────────────────
def fig_ring_indices():
    W, H = 700, 400
    cx, cy = 280, 210
    f = []
    occ = {2, 3, 4, 5, 6}
    f.extend(ring(cx, cy, 140, 90, 10, occ))
    f.append(text(cx, 52, "<- зайнятий (tail -> head) ->", size=12, color=DMA_C))
    f.append(arrow(cx - 144, cy, cx - 190, cy, color=POS, sw=2.2))
    f.append(text(cx - 210, cy + 5, "head", size=13, color=POS, bold=True))
    f.append(arrow(cx + 144, cy, cx + 190, cy, color=FIELD, sw=2.2))
    f.append(text(cx + 210, cy + 5, "tail", size=13, color=FIELD, bold=True))
    ob, _, _ = textbox(cx + 33, 374, "N-1 -> 0", size=11,
                       fill="#fff3cd", stroke=GOLD, sw=1.5, color=GOLD)
    f.append(ob)
    f.append(text(510, 120, "Обернення індексу:", size=13, color=INK, anchor="start", bold=True))
    f.append(rect(470, 132, 210, 86, fill=FILL, stroke="#aaaaaa", sw=1.2))
    f.append(text(478, 152, "head = (head + 1) % N", size=11, color=INK, anchor="start"))
    f.append(text(478, 168, "   // загальний дільник", size=10, color=MUTED, anchor="start"))
    f.append(text(478, 190, "head = (head + 1) & (N-1)", size=11, color=INK, anchor="start"))
    f.append(text(478, 206, "   // N - степінь двійки", size=10, color=MUTED, anchor="start"))
    f.append(text(470, 246, "& (N-1) - один такт;", size=12, color=INK, anchor="start"))
    f.append(text(470, 264, "% N - ділення (~30 тактів).", size=11, color=MUTED, anchor="start"))
    f.append(text(470, 282, "Тому N беруть степенем 2.", size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, "ring-indices.svg"), W, H, *f)


# ── proj-2: head==tail - порожньо проти повно ────────────────────────────────
def fig_full_empty():
    W, H = 740, 410
    f = []
    cxL, cy = 185, 205
    f.append(text(cxL, 72, "ПОРОЖНЬО", size=14, color=MUTED, bold=True))
    f.extend(ring(cxL, cy, 110, 68, 8, set()))
    f.append(arrow(cxL + 30, cy - 96, cxL + 40, cy - 138, color=POS, sw=2.2))
    f.append(text(cxL + 44, cy - 150, "head", size=12, color=POS, bold=True))
    f.append(arrow(cxL + 62, cy - 86, cxL + 84, cy - 122, color=FIELD, sw=2.2))
    f.append(text(cxL + 93, cy - 132, "tail", size=12, color=FIELD, bold=True))
    f.append(text(cxL, 368, "head == tail == 0", size=12, color=INK))
    f.append(text(cxL, 385, "нічого не клали", size=11, color=MUTED))

    f.append(line(370, 90, 370, 320, color="#dddddd", sw=2, dash="6,4"))
    f.append(text(370, 212, "vs", size=22, color=MUTED, bold=True))

    cxR = 560
    f.append(text(cxR, 72, "ПОВНО", size=14, color=POS, bold=True))
    f.extend(ring(cxR, cy, 110, 68, 8, set(range(8))))
    f.append(arrow(cxR + 30, cy - 96, cxR + 40, cy - 138, color=POS, sw=2.2))
    f.append(text(cxR + 44, cy - 150, "head", size=12, color=POS, bold=True))
    f.append(arrow(cxR + 62, cy - 86, cxR + 84, cy - 122, color=FIELD, sw=2.2))
    f.append(text(cxR + 93, cy - 132, "tail", size=12, color=FIELD, bold=True))
    f.append(text(cxR, 368, "head == tail == 0", size=12, color=INK))
    f.append(text(cxR, 385, "writer наздогнав reader", size=11, color=POS))

    f.append(text(370, 336, "Два класичні виходи:", size=12, color=INK, bold=True))
    lb, _, _ = textbox(200, 358, "-1 комірка:\nповно = next(head) == tail",
                       size=11, fill="#eef6ee", stroke=FIELD, sw=1.5, color="#1a5c1a")
    f.append(lb)
    rb, _, _ = textbox(540, 358, "лічильник count:\nповно = count == N",
                       size=11, fill="#fdf0f0", stroke=POS, sw=1.5, color="#7a1a1a")
    f.append(rb)
    render(os.path.join(IMG, "full-empty.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pingpong_phases()
    fig_swap_handoff()
    fig_tearing_vs_clean()
    fig_pingpong_timeline()
    fig_tradeoff()
    fig_ring_indices()
    fig_full_empty()
    print("OK: 7 figures ->", IMG)


