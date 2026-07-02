# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PS   = "#2457d6"   # тверде ядро / процесорна система — синє (готове в кремнії)
PL   = "#27ae60"   # тканина / програмована логіка — зелене
BUS  = "#8e44ad"   # шина AXI — фіолетова жила між двома світами
HOT  = "#c0392b"   # дані / гарячий потік


# ── Один кристал, дві половини ───────────────────────────────────────────────
# Ідея: SoC FPGA — не два чипи, а один кристал, поділений навпіл. Ліворуч —
# тверда процесорна система (CPU + кеш + контролери), праворуч — тканина.
# Між ними — шина, по якій вони спілкуються.

def fig_soc_die():
    W, H = 760, 400
    p = []

    # межа кристала
    dx, dy, dw, dh = 34, 48, 692, 300
    p.append(rect(dx, dy, dw, dh, fill="#fbfbfb", stroke=INK, sw=1.8, rx=14))
    p.append(text(dx + dw / 2, dy + 22, "один кристал (SoC FPGA)", size=12, color=INK, bold=True))

    # ── ліворуч: процесорна система (PS) ──
    px, py, pw, ph = 58, 92, 300, 232
    p.append(rect(px, py, pw, ph, fill="#eef3fd", stroke=PS, sw=1.8, rx=10))
    p.append(text(px + pw / 2, py + 24, "процесорна система", size=12.5, color=PS, bold=True))
    p.append(text(px + pw / 2, py + 41, "(hard: випечена в кремнії)", size=9.5, color=MUTED, italic=True))
    # блоки всередині PS
    p.append(rect(px + 22, py + 56, 118, 52, fill="#dbe6fb", stroke=PS, sw=1.6, rx=7))
    p.append(mtext(px + 81, py + 76, "2× ядра\nCortex-A", size=10.5, color=PS, bold=True, lh=1.3))
    p.append(rect(px + 158, py + 56, 118, 52, fill="#dbe6fb", stroke=PS, sw=1.4, rx=7))
    p.append(mtext(px + 217, py + 76, "кеш +\nконтролер DDR", size=9.5, color=PS, lh=1.3))
    p.append(rect(px + 22, py + 122, 254, 44, fill="#eef3fd", stroke=PS, sw=1.2, rx=7))
    p.append(text(px + 149, py + 148, "готова периферія: USB · Ethernet · SD · UART", size=9.5, color=INK))
    p.append(text(px + pw / 2, py + 196, "працює як звичайний процесор", size=10, color=INK, bold=True))

    # ── праворуч: програмована логіка (PL) — мозаїка клітинок ──
    lx, ly, lw, lh = 402, 92, 300, 232
    p.append(rect(lx, ly, lw, lh, fill="#eef7ee", stroke=PL, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "програмована тканина", size=12.5, color=PL, bold=True))
    p.append(text(lx + lw / 2, ly + 41, "(soft: задає бітстрім)", size=9.5, color=MUTED, italic=True))
    cols, rows = 8, 4
    cw, ch, gap = 26, 24, 7
    gx = lx + (lw - (cols * cw + (cols - 1) * gap)) / 2
    gy = ly + 58
    for r in range(rows):
        for c in range(cols):
            cx = gx + c * (cw + gap)
            cy = gy + r * (ch + gap)
            p.append(rect(cx, cy, cw, ch, fill="#e0f0e0", stroke=PL, sw=1.0, rx=3))
    p.append(text(lx + lw / 2, ly + 196, "стає будь-якою схемою під задачу", size=10, color=INK, bold=True))

    # ── шина між половинами ──
    midx = (px + pw + lx) / 2
    p.append(rect(midx - 20, py + 40, 40, 150, fill="#f3e9fa", stroke=BUS, sw=1.8, rx=8))
    p.append(mtext(midx, py + 100, "ш\nи\nн\nа", size=11, color=BUS, bold=True, lh=1.25))
    p.append(arrow(px + pw, py + 80, midx - 20, py + 80, color=BUS, sw=2))
    p.append(arrow(midx + 20, py + 150, lx, py + 150, color=BUS, sw=2))
    p.append(arrow(lx, py + 120, midx + 20, py + 120, color=BUS, sw=2))

    p.append(text(W / 2, H - 22,
                  "не два чипи поряд, а один кристал: тверда процесорна система і тканина, зшиті швидкою шиною",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "soc-die.svg"), W, H, *p,
           title="SoC FPGA: процесорна система і тканина на одному кристалі")


# ── Шина AXI: шов між двома світами ──────────────────────────────────────────
# Ідея: показати, ЩО тече через шину і в який бік. PS керує тканиною й читає з
# неї дані; спільна пам'ять доступна обом. Це серце гібрида.

def fig_axi_bridge():
    W, H = 760, 380
    p = []

    # PS ліворуч
    px, py, pw, ph = 40, 70, 190, 200
    p.append(rect(px, py, pw, ph, fill="#eef3fd", stroke=PS, sw=1.8, rx=10))
    p.append(text(px + pw / 2, py + 26, "процесор (PS)", size=12, color=PS, bold=True))
    p.append(mtext(px + pw / 2, py + 58, "веде рутину:\nменю · протоколи\nконфігурація", size=10, color=INK, lh=1.4))
    p.append(text(px + pw / 2, py + 168, "звичайний код", size=10, color=MUTED, italic=True))

    # PL праворуч
    lx, ly, lw, lh = 530, 70, 190, 200
    p.append(rect(lx, ly, lw, lh, fill="#eef7ee", stroke=PL, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, ly + 26, "тканина (PL)", size=12, color=PL, bold=True))
    p.append(mtext(lx + lw / 2, ly + 58, "гарячий потік:\nфільтр · відео\nшвидкий I/O", size=10, color=INK, lh=1.4))
    p.append(text(lx + lw / 2, ly + 168, "паралельне залізо", size=10, color=MUTED, italic=True))

    # шина посередині
    bx, by, bw, bh = 300, 70, 160, 200
    p.append(rect(bx, by, bw, bh, fill="#f3e9fa", stroke=BUS, sw=2, rx=10))
    p.append(text(bx + bw / 2, by + 24, "шина AXI", size=12.5, color=BUS, bold=True))
    p.append(text(bx + bw / 2, by + 41, "(шов між світами)", size=9, color=MUTED, italic=True))

    # стрілка PS→PL: керування, налаштування
    p.append(arrow(px + pw, py + 74, bx, py + 74, color=PS, sw=2.2))
    p.append(arrow(bx + bw, py + 74, lx, py + 74, color=PS, sw=2.2))
    p.append(text((px + pw + lx) / 2, py + 62, "керує · налаштовує реєстри", size=9.5, color=PS, bold=True))

    # стрілка PL→PS: готові дані
    p.append(arrow(lx, py + 128, bx + bw, py + 128, color=HOT, sw=2.2))
    p.append(arrow(bx, py + 128, px + pw, py + 128, color=HOT, sw=2.2))
    p.append(text((px + pw + lx) / 2, py + 150, "віддає готові дані (потоком)", size=9.5, color=HOT, bold=True))

    # спільна пам'ять під шиною — доступна обом
    my, mw, mh = 300, 400, 46
    mx = W / 2 - mw / 2
    p.append(rect(mx, my, mw, mh, fill="#fff6e6", stroke="#b8860b", sw=1.7, rx=8))
    p.append(text(mx + mw / 2, my + 28, "спільна пам'ять DDR — бачать обидві половини", size=10.5, color="#8a6d0b", bold=True))
    p.append(line(px + pw / 2, py + ph, px + pw / 2, my, color="#b8860b", sw=1.4, dash="4,4"))
    p.append(line(lx + lw / 2, ly + lh, lx + lw / 2, my, color="#b8860b", sw=1.4, dash="4,4"))

    p.append(text(W / 2, H - 14,
                  "процесор командує й читає, тканина рахує й віддає — а важкі масиви лежать у спільній пам'яті",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "axi-bridge.svg"), W, H, *p,
           title="Шина AXI: що тече між процесором і тканиною")


# ── Порядок старту: спершу процесор, потім тканина ───────────────────────────
# Ідея: асиметрія завантаження, на якій спотикаються. PS стартує сам із флеші,
# як МК; далі ВІН заливає бітстрім у тканину. Тканина оживає ДРУГОЮ.

def fig_boot_order():
    W, H = 760, 300
    p = []

    steps = [
        (60,  PS,  "1. живлення",       "процесор PS\nстартує сам", "#eef3fd"),
        (270, PS,  "2. PS читає флеш",  "завантажник\nу процесорі",  "#eef3fd"),
        (480, PL,  "3. PS ллє бітстрім","тканина PL\nнабуває схеми",  "#eef7ee"),
    ]
    bw, by, bh = 190, 90, 110
    for bx, col, head, body, fillc in steps:
        p.append(rect(bx, by, bw, bh, fill=fillc, stroke=col, sw=1.8, rx=10))
        p.append(text(bx + bw / 2, by + 26, head, size=11.5, color=col, bold=True))
        p.append(mtext(bx + bw / 2, by + 58, body, size=10, color=INK, lh=1.35))

    p.append(arrow(60 + bw, by + bh / 2, 270, by + bh / 2, color=INK, sw=2))
    p.append(arrow(270 + bw, by + bh / 2, 480, by + bh / 2, color=INK, sw=2))

    # підпис під останнім блоком — тканина готова остання
    p.append(text(480 + bw / 2, by + bh + 26, "аж тепер тканина працює", size=10.5, color=PL, bold=True))
    p.append(text(60 + bw / 2, by + bh + 26, "готовий за мілісекунди, як МК", size=10, color=PS, bold=True))

    p.append(text(W / 2, H - 16,
                  "процесорна половина оживає першою й сама вдихає життя в тканину — тканина завжди друга",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "boot-order.svg"), W, H, *p,
           title="Порядок старту SoC FPGA: процесор першим, тканина другою")


# ── Хто що робить: поділ праці ───────────────────────────────────────────────
# Ідея: дві колонки — що природно кладеться на процесор, а що на тканину, і
# де вони зустрічаються (DMA / реєстри). Допомагає ділити задачу.

def fig_who_does_what():
    W, H = 760, 340
    p = []

    ps_list = [
        "операційна система, файли, мережа",
        "меню, екран, налаштування",
        "повільні протоколи й рішення",
        "розгалужена, «розумна» логіка",
    ]
    pl_list = [
        "фільтри й перетворення потоку",
        "кожен піксель відео однаково",
        "лов кожного біта швидкого I/O",
        "сотні однакових каналів нараз",
    ]

    cw, cy, ch = 320, 58, 208
    lx = 40
    p.append(rect(lx, cy, cw, ch, fill="#eef3fd", stroke=PS, sw=1.8, rx=12))
    p.append(text(lx + cw / 2, cy + 28, "на процесор (PS)", size=13.5, color=PS, bold=True))
    p.append(text(lx + cw / 2, cy + 45, "послідовне й розгалужене", size=9.5, color=MUTED, italic=True))
    for i, s in enumerate(ps_list):
        ty = cy + 78 + i * 31
        p.append(text(lx + 18, ty, "•", size=15, color=PS, anchor="start", bold=True))
        p.append(text(lx + 36, ty, s, size=10.5, color=INK, anchor="start"))

    rx0 = 400
    p.append(rect(rx0, cy, cw, ch, fill="#eef7ee", stroke=PL, sw=1.8, rx=12))
    p.append(text(rx0 + cw / 2, cy + 28, "на тканину (PL)", size=13.5, color=PL, bold=True))
    p.append(text(rx0 + cw / 2, cy + 45, "широке й однотипне", size=9.5, color=MUTED, italic=True))
    for i, s in enumerate(pl_list):
        ty = cy + 78 + i * 31
        p.append(text(rx0 + 18, ty, "•", size=15, color=PL, anchor="start", bold=True))
        p.append(text(rx0 + 36, ty, s, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "ділити задачу по природі: розгалужене й неспішне — процесору, широке й однотипне — тканині",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "who-does-what.svg"), W, H, *p,
           title="Поділ праці в SoC FPGA: процесор проти тканини")


# ── Хронологія: дві майже одночасні появи (для вставки hist) ─────────────────
# Ідея: показати вузьке вікно 2011–2012, у якому два конкуренти зшили ARM із
# тканиною. Xilinx: анонс 1.03.2011 → перші чипи 12.2011. Altera: перші поставки
# 12.2012. Дві доріжки на одній осі часу — видно, наскільки близько вони йшли.

def fig_hist_timeline():
    W, H = 780, 340
    p = []

    # вісь часу
    ax0, ax1, ay = 70, 710, 250
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    p.append(arrow(ax1 - 2, ay, ax1 + 18, ay, color=INK, sw=2))
    p.append(text(ax1 + 6, ay + 24, "час", size=10.5, color=MUTED, anchor="end", italic=True))

    # позначки років на осі
    years = [("2011", 130), ("2012", 400), ("2013", 660)]
    for lbl, x in years:
        p.append(line(x, ay - 6, x, ay + 6, color=INK, sw=1.6))
        p.append(text(x, ay + 24, lbl, size=11, color=INK, bold=True))

    # верхня доріжка — Xilinx
    def milestone(x, y_lbl, col, fillc, head, sub, up=True):
        # вузол на осі
        p.append(circle(x, ay, 6, fill=col, stroke=col, sw=1.5))
        # рамка з підписом над/під віссю
        box, bw, bh = textbox(x, y_lbl, head + "\n" + sub, size=10.5, pad=9,
                              fill=fillc, stroke=col, color=INK, bold=False, rx=8)
        p.append(box)
        # ніжка від вузла до рамки
        y_edge = y_lbl + bh / 2 if up else y_lbl - bh / 2
        p.append(line(x, ay, x, y_edge, color=col, sw=1.4, dash="3,3"))
        return bw

    # Xilinx — над віссю
    p.append(text(130, 70, "Xilinx", size=13, color=PS, bold=True))
    milestone(130, 118, PS, "#eef3fd", "1 бер. 2011: анонс", "Zynq-7000 (EPP)")
    milestone(255, 170, PS, "#eef3fd", "груд. 2011", "перші чипи в руках")

    # Altera — під віссю
    p.append(text(600, 300, "Altera", size=13, color=PL, bold=True))
    milestone(430, 300, PL, "#eef7ee", "12 груд. 2012: поставки", "Cyclone V SoC (HPS)", up=False)

    # спільне ядро — підпис по центру зверху
    p.append(text(W / 2, 48,
                  "спільний хід: двоядерний ARM Cortex-A9, 28 нм, зшитий із тканиною",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Народження SoC FPGA: вузьке вікно 2011–2012")


if __name__ == "__main__":
    fig_soc_die()
    fig_axi_bridge()
    fig_boot_order()
    fig_who_does_what()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
