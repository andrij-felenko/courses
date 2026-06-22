# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HARD = "#2457d6"   # тверде ядро — синє (готове, фіксоване)
SOFT = "#27ae60"   # м'яке ядро — зелене (тканина)
ACC  = "#c0392b"   # апаратні блоки-прискорювачі — гаряче


# ── Тверде ядро проти м'якого ────────────────────────────────────────────────
# Ідея: один чип, два способи мати в ньому процесор. Тверде — суцільний блок
# кремнію поряд із тканиною. М'яке — той самий процесор, але викладений із
# окремих клітинок тканини (показуємо «мозаїкою» LUT).

def fig_soft_vs_hard():
    W, H = 720, 340
    p = []

    # ── ліворуч: тверде ядро ──
    lx, ly, lw, lh = 40, 60, 300, 220
    p.append(rect(lx, ly, lw, lh, fill="#fbfbfb", stroke=HARD, sw=1.8, rx=12))
    p.append(text(lx + lw / 2, ly + 26, "Тверде ядро", size=15, color=HARD, bold=True))
    p.append(text(lx + lw / 2, ly + 44, "(hard core)", size=11, color=MUTED, italic=True))
    # суцільний блок CPU у кремнії + смужка тканини поряд
    p.append(rect(lx + 24, ly + 64, 150, 120, fill="#eaf0fd", stroke=HARD, sw=2, rx=8))
    p.append(text(lx + 99, ly + 120, "CPU", size=18, color=HARD, bold=True))
    p.append(text(lx + 99, ly + 142, "у кремнії", size=10, color=MUTED))
    p.append(rect(lx + 186, ly + 64, 90, 120, fill="#eef7ee", stroke=SOFT, sw=1.4, rx=8))
    p.append(mtext(lx + 231, ly + 118, "тканина\nFPGA", size=10, color=SOFT, bold=True))
    p.append(text(lx + lw / 2, ly + 204, "швидкий і малий — але фіксований", size=10.5, color=INK, bold=True))

    # ── праворуч: м'яке ядро (мозаїка клітинок) ──
    rx0, ry, rw, rh = 380, 60, 300, 220
    p.append(rect(rx0, ry, rw, rh, fill="#fbfbfb", stroke=SOFT, sw=1.8, rx=12))
    p.append(text(rx0 + rw / 2, ry + 26, "М'яке ядро", size=15, color=SOFT, bold=True))
    p.append(text(rx0 + rw / 2, ry + 44, "(soft core)", size=11, color=MUTED, italic=True))
    # мозаїка LUT: частина клітинок зайнята під процесор (сині), решта вільна
    cols, rows = 7, 4
    cw, ch, gap = 30, 22, 6
    gx = rx0 + (rw - (cols * cw + (cols - 1) * gap)) / 2
    gy = ry + 64
    used = {(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(2,5),(3,1),(3,2),(3,3)}
    for r in range(rows):
        for c in range(cols):
            cx = gx + c * (cw + gap)
            cy = gy + r * (ch + gap)
            if (r, c) in used:
                p.append(rect(cx, cy, cw, ch, fill="#eaf0fd", stroke=HARD, sw=1.5, rx=3))
            else:
                p.append(rect(cx, cy, cw, ch, fill="#eef7ee", stroke=SOFT, sw=1.0, rx=3))
    p.append(text(rx0 + rw / 2, ry + 204, "процесор, викладений із LUT і тригерів", size=10.5, color=INK, bold=True))

    # підпис-мостик унизу
    p.append(text(W / 2, H - 16,
                  "однакова логіка — два способи її мати: випечена в кремнії проти зібраної з тканини",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "soft-vs-hard.svg"), W, H, *p,
           title="Один чип — два процесори: твердий проти м'якого")


# ── Сила softcore: ядро поряд із власним залізом ─────────────────────────────
# Ідея: усе на одній FPGA — м'яке ядро веде рутину, шина зв'язує його з
# окремими апаратними блоками, що працюють паралельно й швидко.

def fig_soft_system():
    W, H = 720, 360
    p = []

    # межа FPGA
    fx, fy, fw, fh = 40, 56, 640, 244
    p.append(rect(fx, fy, fw, fh, fill="#fbfbfb", stroke=SOFT, sw=1.6, rx=12))
    p.append(text(fx + fw / 2, fy + 22, "усе це — одна FPGA", size=11, color=SOFT, bold=True))

    # м'яке ядро ліворуч
    cpu_x, cpu_y, cpu_w, cpu_h = 70, 120, 170, 120
    p.append(rect(cpu_x, cpu_y, cpu_w, cpu_h, fill="#eaf0fd", stroke=HARD, sw=2, rx=10))
    p.append(text(cpu_x + cpu_w / 2, cpu_y + 28, "м'яке ядро", size=12, color=HARD, bold=True))
    p.append(mtext(cpu_x + cpu_w / 2, cpu_y + 56,
                   "меню · мережа\nконфігурація\nнеспішні рішення", size=9.5, color=INK, lh=1.45))

    # шина (вертикальна жила) + комутатор
    busx = 300
    p.append(line(cpu_x + cpu_w, cpu_y + cpu_h / 2, busx, cpu_y + cpu_h / 2, color=INK, sw=2.5))
    p.append(text((cpu_x + cpu_w + busx) / 2, cpu_y + cpu_h / 2 - 8, "шина", size=9, color=MUTED, bold=True))
    p.append(line(busx, 120, busx, 270, color=INK, sw=2.5))
    p.append(text(busx, 290, "шина", size=9, color=MUTED))

    # три апаратні блоки праворуч
    blocks = [("DSP-фільтр", 120), ("швидкий I/O", 178), ("ШІМ-канали", 236)]
    bx, bw, bh = 400, 200, 40
    for lab, by in blocks:
        p.append(line(busx, cpu_y + cpu_h / 2, bx, by + bh / 2, color=MUTED, sw=1.6))
        p.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=ACC, sw=1.7, rx=8))
        p.append(text(bx + bw / 2, by + bh / 2 + 4, lab, size=11, color=ACC, bold=True))
    p.append(text(bx + bw / 2, blocks[-1][1] + bh + 18,
                  "апаратні блоки: паралельно, наносекунди", size=9.5, color=ACC, bold=True))

    p.append(text(W / 2, H - 16,
                  "рутину веде процесор, гарячі потоки тягнуть прискорювачі поряд — кожен робить своє",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "soft-system.svg"), W, H, *p,
           title="Гібрид: процесор для рутини, залізо для гарячого")


# ── Коли softcore доречний, а коли ні ────────────────────────────────────────
# Ідея: дві колонки-чеклисти. Зелена — коли варто; червона — коли краще
# окремий МК. Без номерів, без «Рис.».

def fig_when():
    W, H = 720, 320
    p = []

    yes = [
        "FPGA вже в системі з іншої причини",
        "потрібна гнучка логіка ПОРЯД зі швидким залізом",
        "хочемо власні інструкції чи периферію",
        "зручно тримати все на одному чипі",
        "потрібна переносимість між FPGA",
    ]
    no = [
        "потрібен лише процесор, без логіки",
        "критична максимальна частота або ціна",
        "вистачає дешевого готового МК",
        "немає паралельних блоків поряд",
        "у цій FPGA вже є тверде ядро",
    ]

    cw, cy, ch = 320, 56, 232
    # ліворуч: доречно
    lx = 40
    p.append(rect(lx, cy, cw, ch, fill="#eef7ee", stroke=SOFT, sw=1.8, rx=12))
    p.append(text(lx + cw / 2, cy + 28, "коли доречно", size=14, color=SOFT, bold=True))
    for i, s in enumerate(yes):
        ty = cy + 60 + i * 33
        p.append(text(lx + 18, ty, "+", size=15, color=SOFT, anchor="start", bold=True))
        p.append(text(lx + 38, ty, s, size=10.5, color=INK, anchor="start"))
    # праворуч: зайве
    rx0 = 360
    p.append(rect(rx0, cy, cw, ch, fill="#fdecea", stroke=ACC, sw=1.8, rx=12))
    p.append(text(rx0 + cw / 2, cy + 28, "коли зайве", size=14, color=ACC, bold=True))
    for i, s in enumerate(no):
        ty = cy + 60 + i * 33
        p.append(text(rx0 + 18, ty, "−", size=15, color=ACC, anchor="start", bold=True))
        p.append(text(rx0 + 38, ty, s, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "м'яке ядро — доповнення до FPGA, а не заміна окремому мікроконтролеру",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "when-soft-core.svg"), W, H, *p,
           title="Коли м'яке ядро виправдане")


if __name__ == "__main__":
    fig_soft_vs_hard()
    fig_soft_system()
    fig_when()
    print("OK: figures written to", OUT)
