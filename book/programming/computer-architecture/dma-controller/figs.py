# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── on-bus: ядро, DMA, SRAM, периферія на спільній шині ───────────────────────
# Ідея: до тієї самої системної шини, що й ядро, підключений ще один майстер —
# DMA. Дані течуть периферія → DMA → SRAM, обходячи ядро; ядро лише налаштовує
# маршрут і отримує одне переривання наприкінці.

def fig_on_bus():
    W, H = 700, 360
    p = []

    bus_y, bus_x, bus_w = 196, 60, 580
    p.append(rect(bus_x, bus_y, bus_w, 34, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=4))
    p.append(text(W / 2, bus_y + 22, "Системна шина (AHB / AXI)", size=13, color=NEG, bold=True))

    # арбітр сидить на шині
    arb, aw, ah = textbox(W / 2, 150, "арбітр", size=11, fill="#fff9e6", stroke="#e0a800", sw=1.8, pad=8)
    p.append(arb)
    p.append(line(W / 2, 150 + ah / 2, W / 2, bus_y, color="#e0a800", sw=1.6))

    # три майстри/підлеглі над шиною
    core, cw, ch = textbox(140, 92, "ядро\n(Xtensa LX7)", size=12, bold=True, pad=10)
    p.append(core)
    p.append(arrow(140, 92 + ch / 2, 140, bus_y, color=INK, sw=1.7))

    dma, dw, dh = textbox(420, 92, "DMA-контролер", size=12, bold=True,
                          fill="#d4edda", stroke=FIELD, sw=2.0, pad=10)
    p.append(dma)
    p.append(line(420, 92 + dh / 2, 420, bus_y, color=FIELD, sw=1.7))

    ram, rw, rh = textbox(580, 92, "SRAM", size=12, bold=True, pad=10)
    p.append(ram)
    p.append(line(580, 92 + rh / 2, 580, bus_y, color=INK, sw=1.7))

    # периферія під шиною
    per, pw, ph = textbox(420, 296, "периферія\n(АЦП / шина)", size=12, bold=True,
                          fill="#fdecea", stroke=POS, sw=2.0, pad=10)
    p.append(per)
    p.append(line(420, 296 - ph / 2, 420, bus_y + 34, color=POS, sw=1.7))

    # ядро дало команду «старт» (тонка сіра), потім — одне переривання назад
    p.append(text(140, 150, "старт + 1 IRQ", size=10, color=MUTED))

    # шлях даних: периферія → (через шину) → SRAM, поза ядром
    p.append(text(W / 2, 250, "потік даних: периферія → DMA → SRAM, повз ядро",
                  size=11, color=FIELD, bold=True))

    # легенда
    ly = 338
    p.append(line(70, ly, 100, ly, color=FIELD, sw=3))
    p.append(text(108, ly + 4, "майстер DMA веде дані", size=11, color=INK, anchor="start"))
    p.append(line(330, ly, 360, ly, color=POS, sw=3))
    p.append(text(368, ly + 4, "запит від периферії (DREQ)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "on-bus.svg"), W, H, *p,
           title="DMA-контролер — другий майстер на спільній шині")


# ── with-without: ядро в циклі копіювання проти звільненого ядра ───────────────
# Ідея: без DMA ядро стоїть між кожним байтом і пам'яттю (copy-copy-copy);
# з DMA ядро дає «старт», далі велика вільна зона, наприкінці — одна стрілка
# «done» назад у ядро.

def fig_with_without():
    W, H = 700, 320
    p = []
    bx, bw, bh = 150, 470, 46

    # без DMA — ядро зайняте увесь час
    y1 = 92
    p.append(text(bx - 12, y1 + 5, "без DMA", size=12, color=POS, bold=True, anchor="end"))
    n = 11
    seg = bw / n
    for i in range(n):
        p.append(rect(bx + i * seg, y1 - bh / 2, seg - 3, bh,
                      fill="#fdecea", stroke=POS, sw=1.3, rx=0))
        p.append(text(bx + i * seg + (seg - 3) / 2, y1 + 4, "cp", size=9, color=POS))
    p.append(text(bx + bw / 2, y1 + bh / 2 + 18,
                  "ядро копіює кожен байт — зайняте увесь час", size=10, color=MUTED, italic=True))

    # з DMA — старт, вільно, done
    y2 = 214
    p.append(text(bx - 12, y2 + 5, "з DMA", size=12, color=FIELD, bold=True, anchor="end"))
    sw_ = 52
    p.append(rect(bx, y2 - bh / 2, sw_, bh, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=0))
    p.append(text(bx + sw_ / 2, y2 + 4, "старт", size=9, color=NEG))
    free_x = bx + sw_ + 4
    free_w = bw - sw_ - 4 - 56
    p.append(rect(free_x, y2 - bh / 2, free_w, bh, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(free_x + free_w / 2, y2 + 4, "ядро вільне — робить інше", size=11, color=FIELD, bold=True))
    done_x = free_x + free_w + 4
    p.append(rect(done_x, y2 - bh / 2, 52, bh, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=0))
    p.append(text(done_x + 26, y2 + 4, "done", size=9, color=NEG))
    # стрілка done назад
    p.append(arrow(done_x + 26, y2 - bh / 2 - 2, done_x + 26, y2 - bh / 2 - 26, color=NEG, sw=1.7))
    p.append(text(done_x + 26, y2 - bh / 2 - 32, "1 IRQ", size=9, color=NEG))

    # під смугою — DMA копіює у фоні
    p.append(line(free_x, y2 + bh / 2 + 10, done_x, y2 + bh / 2 + 10, color=FIELD, sw=2.0, dash="5 4"))
    p.append(text(free_x + free_w / 2, y2 + bh / 2 + 26, "DMA копіює у фоні", size=10, color=FIELD, italic=True))

    render(os.path.join(OUT, "with-without.svg"), W, H, *p,
           title="DMA не прискорює шину — він прибирає ядро з циклу копіювання")


# ── cycle-stealing: крадіжка циклів проти пакетного режиму ─────────────────────
# Ідея: на шині такти ядра й DMA чергуються. У крадіжці циклів DMA бере один
# такт і віддає шину назад — ядро майже не помічає; у пакетному режимі DMA
# тримає шину суцільним блоком, а ядро стоїть.

def fig_cycle_stealing():
    W, H = 700, 300
    p = []
    x0, x1 = 70, 640
    cell = (x1 - x0) / 16.0

    def lane(y, owners, label, col):
        p.append(text(x0, y - 22, label, size=11, color=col, bold=True, anchor="start"))
        for i, who in enumerate(owners):
            cx = x0 + i * cell
            if who == "C":
                p.append(rect(cx, y - 14, cell - 2, 28, fill="#eef1f4", stroke=MUTED, sw=1.0, rx=0))
                p.append(text(cx + cell / 2, y + 4, "C", size=10, color=MUTED))
            else:
                p.append(rect(cx, y - 14, cell - 2, 28, fill="#d4edda", stroke=FIELD, sw=1.3, rx=0))
                p.append(text(cx + cell / 2, y + 4, "D", size=10, color=FIELD, bold=True))

    # крадіжка циклів: один такт DMA вкраплений між тактами ядра
    steal = ["C", "C", "D", "C", "C", "C", "D", "C", "C", "D", "C", "C", "C", "D", "C", "C"]
    lane(92, steal, "крадіжка циклів — DMA бере по одному такту", FIELD)
    p.append(text(x0, 128, "ядро майже не помічає пауз", size=10, color=MUTED, anchor="start", italic=True))

    # пакетний режим: DMA тримає шину суцільним блоком
    burst = ["C", "C", "D", "D", "D", "D", "D", "D", "D", "D", "C", "C", "C", "C", "C", "C"]
    lane(214, burst, "пакетний режим — DMA тримає шину блоком", POS)
    p.append(text(x0, 250, "швидше для DMA, але ядро на цей час стоїть", size=10, color=MUTED, anchor="start", italic=True))

    # легенда
    p.append(rect(x1 - 150, 268, 14, 14, fill="#eef1f4", stroke=MUTED, sw=1.0, rx=0))
    p.append(text(x1 - 132, 279, "такт ядра (C)", size=10, color=INK, anchor="start"))
    p.append(rect(x1 - 56, 268, 14, 14, fill="#d4edda", stroke=FIELD, sw=1.3, rx=0))
    p.append(text(x1 - 38, 279, "DMA (D)", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "cycle-stealing.svg"), W, H, *p,
           title="Дві дисципліни арбітра: крадіжка циклів проти пакета")


# ── threshold: час копії від розміру блоку (вставка memcpy проти DMA) ──────────
# Ідея: дві майже паралельні прямі. CPU-memcpy стартує з нуля; DMA — з фіксованих
# накладних O_dma і росте тим самим нахилом (та сама SRAM). DMA не наздоганяє за
# чистим часом; його виграш — вивільнені такти ядра (заштрихована зона).

def fig_threshold():
    W, H = 700, 360
    ox, oy = 80, 300
    aw, ah = 560, 250
    p = []

    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "розмір блоку N", size=11, color=INK, italic=True))
    p.append(text(ox - 10, oy - ah - 2, "час", size=11, color=INK, italic=True, anchor="end"))

    o_dma = ah * 0.30                 # фіксований старт DMA у px
    slope = (ah * 0.55) / aw          # спільний нахил (та сама пам'ять)

    def cpu_y(x):  return oy - slope * x
    def dma_y(x):  return oy - o_dma - slope * x

    # заштрихована зона між прямими = вивільнені такти ядра
    band = ['<polygon points="']
    pts = []
    for i in range(0, 41):
        x = ox + aw * i / 40.0
        pts.append("%.1f,%.1f" % (x, cpu_y(x - ox)))
    for i in range(40, -1, -1):
        x = ox + aw * i / 40.0
        pts.append("%.1f,%.1f" % (x, dma_y(x - ox)))
    band.append(" ".join(pts))
    band.append('" fill="#eafaf0" stroke="none" opacity="0.8"/>')
    p.append("".join(band))

    # прямі
    p.append(line(ox, cpu_y(0), ox + aw, cpu_y(aw), color=FIELD, sw=2.6))
    p.append(line(ox, dma_y(0), ox + aw, dma_y(aw), color=POS, sw=2.6))

    # позначка O_dma
    p.append(line(ox, oy, ox, oy - o_dma, color=POS, sw=1.4, dash="4 3"))
    p.append(text(ox + 8, oy - o_dma / 2 + 4, "O_dma", size=10, color=POS, anchor="start"))

    # підписи прямих
    p.append(text(ox + aw - 6, cpu_y(aw) + 16, "CPU memcpy", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(ox + aw - 6, dma_y(aw) - 8, "DMA M2M", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(ox + aw * 0.46, (cpu_y(aw * 0.46) + dma_y(aw * 0.46)) / 2 + 4,
                  "вивільнені такти ядра", size=10, color="#1f8a4c"))

    render(os.path.join(OUT, "threshold.svg"), W, H, *p,
           title="Пам'ять→пам'ять: DMA не наздоганяє за чистим часом")


# ── timeline: дві часові смуги однієї копії (CPU проти DMA) ────────────────────
# Ідея: зверху CPU-memcpy — ядро зайняте увесь час. Знизу DMA — короткий старт,
# далі DMA копіює у фоні, а ядро або марнує час у busy-wait, або вивільняється;
# мітка готовності праворуч — колбек у перериванні.

def fig_timeline():
    W, H = 700, 300
    p = []
    bx, bw, bh = 120, 500, 44

    # CPU
    y1 = 96
    p.append(text(bx - 12, y1 + 5, "CPU", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(rect(bx, y1 - bh / 2, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(bx + bw / 2, y1 + 4, "ядро зайняте memcpy увесь час", size=11, color=FIELD, bold=True))

    # DMA
    y2 = 206
    p.append(text(bx - 12, y2 + 5, "DMA", size=12, color=NEG, bold=True, anchor="end"))
    sw_ = 70
    p.append(rect(bx, y2 - bh / 2, sw_, bh, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=0))
    p.append(text(bx + sw_ / 2, y2 + 4, "старт", size=9, color=NEG))
    p.append(text(bx + sw_ / 2, y2 + bh / 2 + 14, "O_dma", size=9, color=MUTED))
    rest = bw - sw_
    # верхня половина — ядро (busy-wait або вільне), нижня — DMA у фоні
    p.append(rect(bx + sw_, y2 - bh / 2, rest, bh / 2, fill="#fdf6e3", stroke="#e0a800", sw=1.2, rx=0))
    p.append(text(bx + sw_ + rest / 2, y2 - 4, "ядро: busy-wait АБО вивільнене", size=10, color="#a07800"))
    p.append(rect(bx + sw_, y2, rest, bh / 2, fill="#d4edda", stroke=FIELD, sw=1.2, rx=0))
    p.append(text(bx + sw_ + rest / 2, y2 + 14, "DMA-апаратура копіює у фоні", size=10, color="#1f8a4c"))

    # мітка готовності праворуч
    p.append(arrow(bx + bw, y2 - bh / 2 - 4, bx + bw, y2 - bh / 2 - 28, color=NEG, sw=1.7))
    p.append(text(bx + bw, y2 - bh / 2 - 34, "колбек (IRQ)", size=9, color=NEG))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Одна копія, дві смуги: де ядро зайняте, а де вільне")


if __name__ == "__main__":
    fig_on_bus()
    fig_with_without()
    fig_cycle_stealing()
    fig_threshold()
    fig_timeline()
    print("OK: figures written to", OUT)
