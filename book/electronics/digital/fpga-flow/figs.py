# -*- coding: utf-8 -*-
"""Фігури до теми «Потік розробки» (FPGA) та її вставки proj-open-toolchain.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
HDLC = "#2457d6"      # вхід (HDL)
SYN  = "#27ae60"      # синтез
AMBER = "#b9770e"     # розміщення / тепле
CHIP = "#1a1a1a"      # бітстрім / кристал
SOFT = "#eef4ff"      # світло-синя заливка
SOFTG = "#eafaf0"     # світло-зелена заливка


# ── 1. Чотири головні кроки: HDL → синтез → P&R → бітстрім → чип ──────────────
def fig_flow():
    W, H = 760, 360
    p = []
    y = 120
    bw, bh = 128, 78
    gap = 22
    x = 24
    steps = [
        ("HDL-код", "Verilog / VHDL", HDLC, SOFT),
        ("синтез", "→ netlist:\nвентилі, тригери", SYN, SOFTG),
        ("розміщення", "елемент →\nклітинка", AMBER, "#fdf6e3"),
        ("трасування", "дроти крізь\nперемикачі", POS, "#fdecea"),
        ("бітстрім", "біти для всіх\nкомірок", CHIP, "#f0f0f0"),
    ]
    centers = []
    for i, (head, sub, col, fill) in enumerate(steps):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.9))
        p.append(text(x + bw / 2, y + 24, head, size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 44, sub, size=10, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            px = centers[i - 1][1]
            p.append(arrow(px, y + bh / 2, x - 2, y + bh / 2, color=INK, sw=2.0))
        x += bw + gap

    # стрілка вниз від бітстріму до «налаштованої FPGA»
    lastcx = centers[-1][0] + bw / 2
    p.append(arrow(lastcx, y + bh, lastcx, y + bh + 52, color=INK, sw=2.0))
    p.append(text(lastcx + 8, y + bh + 34, "залив у чип", size=10, color=INK, anchor="start", bold=True))
    box, w2, h2 = textbox(lastcx, y + bh + 84, "FPGA набула\nпотрібної схеми",
                          size=11, bold=True, color=SYN, fill=SOFTG, stroke=SYN, sw=2)
    p.append(box)

    # підпис-смуга: де схоже на софт, а де ні
    p.append(line(24, y - 22, 24 + 2 * (bw + gap) - gap, y - 22, color=MUTED, sw=2.2))
    p.append(text(24 + (bw + gap) - gap / 2, y - 28, "схоже на компіляцію", size=10, color=MUTED, bold=True))
    p.append(line(24 + 2 * (bw + gap), y - 22, 24 + 5 * (bw + gap) - gap, y - 22, color=AMBER, sw=2.2))
    p.append(text(24 + 3.4 * (bw + gap), y - 28, "суто апаратне вкладання в кристал", size=10, color=AMBER, bold=True))

    render(os.path.join(IMG, "flow.svg"), W, H, *p,
           title="Від HDL до чипа: синтез, розміщення, трасування, бітстрім")


# ── 2. Синтез: текст HDL → netlist із примітивів ─────────────────────────────
def fig_synthesis():
    W, H = 720, 300
    p = []
    # ліворуч — рядок HDL
    lx, ly = 40, 150
    code, cw, ch = textbox(lx + 150, ly, "assign y =\n(a & b) | (c & d);",
                           size=12, bold=True, fill="#f4f6f8", stroke=INK, sw=1.6, pad=14)
    p.append(code)
    p.append(text(lx + 150, ly - ch / 2 - 12, "опис HDL (текст)", size=11, color=MUTED, bold=True))

    # стрілка синтезу
    ax0 = lx + 150 + cw / 2
    p.append(arrow(ax0, ly, ax0 + 70, ly, color=SYN, sw=2.4))
    p.append(text(ax0 + 35, ly - 12, "синтез", size=11, color=SYN, bold=True))

    # праворуч — netlist: два AND → OR
    gx = ax0 + 110
    def gate(cx, cy, lab, col, fill):
        b, bw, bh = textbox(cx, cy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8, min_w=64)
        return b, cx + bw / 2, (cx - bw / 2)
    g1, g1r, g1l = gate(gx + 50, ly - 48, "AND", NEG, SOFT)
    g2, g2r, g2l = gate(gx + 50, ly + 48, "AND", NEG, SOFT)
    g3, g3r, g3l = gate(gx + 175, ly, "OR", SYN, SOFTG)
    # входи
    for yy, lab in [(ly - 64, "a"), (ly - 32, "b"), (ly + 32, "c"), (ly + 80, "d")]:
        p.append(text(g1l - 18, yy + 4, lab, size=11, color=INK, anchor="end", bold=True))
        p.append(line(g1l - 12, yy, g1l, yy, color=INK, sw=1.4))
    p.append(g1); p.append(g2); p.append(g3)
    # зв'язки AND → OR
    p.append(line(g1r, ly - 48, g3l, ly - 14, color=INK, sw=1.6))
    p.append(line(g2r, ly + 48, g3l, ly + 14, color=INK, sw=1.6))
    p.append(arrow(g3r, ly, g3r + 34, ly, color=INK, sw=1.6))
    p.append(text(g3r + 40, ly + 4, "y", size=12, color=INK, anchor="start", bold=True))
    p.append(text(gx + 110, ly - ch / 2 - 30, "netlist: примітиви + зв'язки", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, "synthesis.svg"), W, H, *p,
           title="Синтез: текст HDL стає списком з'єднаних вентилів (netlist)")


# ── 3. Розміщення й трасування: вузли в сітку, дроти між ними ─────────────────
def fig_place_route():
    W, H = 720, 360
    p = []
    # сітка клітинок 5×4
    gx, gy = 90, 90
    cell = 52
    cols, rows = 5, 4
    for r in range(rows):
        for c in range(cols):
            p.append(rect(gx + c * cell, gy + r * cell, cell - 8, cell - 8,
                          fill="#fbfcff", stroke="#c9d6f0", sw=1.0))
    # розміщені вузли A,B,C,D у конкретних клітинках
    def cellc(c, r):
        return gx + c * cell + (cell - 8) / 2, gy + r * cell + (cell - 8) / 2
    nodes = {"A": (1, 0), "B": (3, 1), "C": (1, 3), "D": (2, 2)}
    pos = {}
    for lab, (c, r) in nodes.items():
        cx, cy = cellc(c, r)
        pos[lab] = (cx, cy)
        p.append(circle(cx, cy, 15, fill=SOFTG, stroke=SYN, sw=2.0))
        p.append(text(cx, cy + 4, lab, size=12, color=SYN, bold=True))

    # трасований шлях A→B (червоний, ламаний крізь канали)
    ax, ay = pos["A"]; bx, by = pos["B"]
    midx = ax + cell
    p.append(line(ax + 15, ay, midx, ay, color=POS, sw=2.6))
    p.append(line(midx, ay, midx, by, color=POS, sw=2.6))
    p.append(line(midx, by, bx - 15, by, color=POS, sw=2.6))
    p.append(text((ax + bx) / 2, ay - 14, "реальний дріт A→B", size=10, color=POS, bold=True))
    # тонкі зв'язки інших
    p.append(line(pos["C"][0], pos["C"][1] - 15, pos["D"][0], pos["D"][1] + 15, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(pos["D"][0] + 15, pos["D"][1], pos["B"][0], pos["B"][1] + 15, color=MUTED, sw=1.4, dash="4 3"))

    # підписи двох дій праворуч
    rx = gx + cols * cell + 30
    p.append(text(rx, gy + 20, "розміщення", size=12, color=AMBER, anchor="start", bold=True))
    p.append(mtext(rx, gy + 40, "кожен вузол →\nконкретна клітинка", size=10, color=INK, anchor="start"))
    p.append(text(rx, gy + 96, "трасування", size=12, color=POS, anchor="start", bold=True))
    p.append(mtext(rx, gy + 116, "дроти між ними\nкрізь перемикачі", size=10, color=INK, anchor="start"))
    p.append(mtext(rx, gy + 170, "зв'язані — ближче:\nкоротший дріт,\nменша затримка", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "place-route.svg"), W, H, *p,
           title="Розміщення садить вузли в клітинки, трасування тягне дроти")


# ── 4. Бітстрім: біти заповнюють усі комірки конфігурації ────────────────────
def fig_bitstream():
    W, H = 760, 320
    p = []
    # ліворуч — стрічка бітів
    bx, by = 44, 150
    bits = "0110 1001 1100 0101 1010 0011"
    cell = 17
    x = bx
    for ch in bits.replace(" ", ""):
        fill = CHIP if ch == "1" else "#ffffff"
        col = "#ffffff" if ch == "1" else INK
        p.append(rect(x, by - cell / 2, cell - 2, cell, fill=fill, stroke=INK, sw=1.0, rx=2))
        p.append(text(x + (cell - 2) / 2, by + 4, ch, size=10, color=col))
        x += cell
    p.append(text(bx, by - 24, "бітстрім: один довгий потік бітів", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx, by + 30, "сотні кбіт … десятки Мбіт", size=10, color=MUTED, anchor="start", italic=True))

    # стрілка вправо
    p.append(arrow(x + 12, by, x + 60, by, color=INK, sw=2.2))
    p.append(text(x + 36, by - 12, "залив", size=10, color=INK, bold=True))

    # праворуч — матриця комірок конфігурації FPGA
    mx, my = x + 78, 80
    mcell = 21
    n = 7
    for r in range(n):
        for c in range(n):
            isLut = (r + c) % 3 == 0
            fill = SOFT if isLut else "#fbfcff"
            p.append(rect(mx + c * mcell, my + r * mcell, mcell - 3, mcell - 3,
                          fill=fill, stroke="#c9d6f0", sw=0.9))
    p.append(text(mx + n * mcell / 2, my - 12, "усі комірки конфігурації", size=11, color=INK, bold=True))
    p.append(text(mx + n * mcell / 2, my + n * mcell + 16,
                  "кожен біт = одна SRAM-комірка LUT або один перемикач", size=10, color=MUTED))

    render(os.path.join(IMG, "bitstream.svg"), W, H, *p,
           title="Бітстрім: біти задають стан кожної комірки конфігурації")


# ── 5. Конфігурація з зовнішньої флеші при кожному старті ────────────────────
def fig_config_flash():
    W, H = 700, 280
    p = []
    # флеш
    fb, fw, fh = (70, 110), 150, 84
    fx, fy = fb
    p.append(rect(fx, fy, fw, fh, fill="#fdf6e3", stroke=AMBER, sw=2.0))
    p.append(text(fx + fw / 2, fy + 28, "флеш-пам'ять", size=12, color=AMBER, bold=True))
    p.append(mtext(fx + fw / 2, fy + 48, "нелетка,\nтримає бітстрім", size=10, color=INK))

    # стрілка завантаження
    p.append(arrow(fx + fw, fy + fh / 2, fx + fw + 90, fy + fh / 2, color=INK, sw=2.4))
    p.append(text(fx + fw + 45, fy + fh / 2 - 12, "при старті", size=10, color=INK, bold=True))
    p.append(text(fx + fw + 45, fy + fh / 2 + 22, "configuration", size=9, color=MUTED, italic=True))

    # FPGA
    gx2 = fx + fw + 90
    p.append(rect(gx2, fy - 8, 200, fh + 16, fill=SOFT, stroke=NEG, sw=2.0))
    p.append(text(gx2 + 100, fy + 18, "FPGA на SRAM", size=12, color=NEG, bold=True))
    p.append(mtext(gx2 + 100, fy + 40, "летка: без живлення\nсхема зникає →\nстартує порожньою", size=10, color=INK))

    p.append(text(W / 2, H - 26, "при кожному ввімкненні чип завантажує себе з флеші за частки секунди",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "config-flash.svg"), W, H, *p,
           title="Летка SRAM-тканина бере бітстрім із зовнішньої флеші")


# ════════════════ Фігури вставки proj-open-toolchain ════════════════════════

# ── 6. Відкритий конвеєр: Yosys → nextpnr → icepack → iceprog ────────────────
def fig_pipeline():
    W, H = 760, 320
    p = []
    y = 130
    bw, bh = 132, 74
    gap = 24
    x = 22
    tools = [
        ("Yosys", "синтез:\nVerilog → netlist", SYN, SOFTG),
        ("nextpnr", "розміщення\nй трасування", AMBER, "#fdf6e3"),
        ("icepack", "пакує у\nдвійковий бітстрім", CHIP, "#f0f0f0"),
        ("iceprog", "заливає у\nфлеш по USB", NEG, SOFT),
    ]
    centers = []
    for i, (head, sub, col, fill) in enumerate(tools):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.9))
        p.append(text(x + bw / 2, y + 24, head, size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 42, sub, size=10, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y + bh / 2, x - 2, y + bh / 2, color=INK, sw=2.0))
        x += bw + gap

    # проміжні файли — підписи під стрілками
    labels = [".v → нетліст", "розкладка", ".bin"]
    for i, lab in enumerate(labels):
        midx = (centers[i][1] + centers[i + 1][0]) / 2
        p.append(text(midx, y - 12, lab, size=9, color=MUTED, italic=True))

    # хвіст: DONE стає високим
    lastcx = centers[-1][0] + bw / 2
    p.append(arrow(lastcx, y + bh, lastcx, y + bh + 44, color=INK, sw=2.0))
    p.append(text(lastcx, y + bh + 66, "чип піднявся сам (DONE = 1)", size=11, color=SYN, bold=True))

    p.append(text(W / 2, y - 44, "усі проміжні файли — текст, кожен крок можна спинити й оглянути",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "pipeline.svg"), W, H, *p,
           title="Відкритий конвеєр iCE40: чотири прозорі утиліти")


# ── 7. Нетліст лягає на фізичну сітку плиток iCE40 ───────────────────────────
def fig_placeroute_ice():
    W, H = 740, 360
    p = []
    # ліворуч — нетліст (граф «що з чим»)
    lx, ly = 60, 180
    def gnode(cx, cy, lab):
        p.append(circle(cx, cy, 16, fill=SOFTG, stroke=SYN, sw=1.8))
        p.append(text(cx, cy + 4, lab, size=11, color=SYN, bold=True))
        return (cx, cy)
    n1 = gnode(lx, ly - 50, "L1")
    n2 = gnode(lx + 60, ly + 10, "FF")
    n3 = gnode(lx, ly + 70, "L2")
    for a, b in [(n1, n2), (n3, n2)]:
        p.append(line(a[0], a[1], b[0], b[1], color=INK, sw=1.5))
    p.append(text(lx + 30, ly - 92, "нетліст:\nщо з чим", size=11, color=MUTED, bold=True))

    # стрілка
    p.append(arrow(lx + 110, ly, lx + 175, ly, color=INK, sw=2.4))
    p.append(text(lx + 142, ly - 12, "P&R", size=11, color=AMBER, bold=True))

    # праворуч — сітка плиток
    gx, gy = lx + 215, 90
    cell = 50
    cols, rows = 6, 4
    for r in range(rows):
        for c in range(cols):
            p.append(rect(gx + c * cell, gy + r * cell, cell - 8, cell - 8,
                          fill="#fbfcff", stroke="#c9d6f0", sw=1.0))
    def cc(c, r):
        return gx + c * cell + (cell - 8) / 2, gy + r * cell + (cell - 8) / 2
    placed = {"L1": (1, 1), "FF": (3, 1), "L2": (1, 2)}
    pos = {}
    for lab, (c, r) in placed.items():
        cx, cy = cc(c, r)
        pos[lab] = (cx, cy)
        p.append(circle(cx, cy, 14, fill=SOFTG, stroke=SYN, sw=1.8))
        p.append(text(cx, cy + 4, lab, size=10, color=SYN, bold=True))
    # дроти каналами
    for a, b, col in [("L1", "FF", POS), ("L2", "FF", POS)]:
        ax, ay = pos[a]; bx, by = pos[b]
        midx = ax + cell
        p.append(line(ax + 14, ay, midx, ay, color=col, sw=2.4))
        p.append(line(midx, ay, midx, by, color=col, sw=2.4))
        p.append(line(midx, by, bx - 14, by, color=col, sw=2.4))
    p.append(text(gx + cols * cell / 2, gy - 12, "плитки кристала iCE40", size=11, color=INK, bold=True))
    p.append(text(gx + cols * cell / 2, gy + rows * cell + 14,
                  "довший дріт → більша затримка → критичний шлях", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "placeroute-ice.svg"), W, H, *p,
           title="Розміщення садить вузли в плитки, трасування — дроти каналами")


# ── 8. Імітація відпалу: цикл swap + вихід із локальної ями ───────────────────
def fig_anneal():
    W, H = 740, 360
    p = []
    # ── ліворуч: цикл відпалу ──
    cx = 175
    ys = [70, 130, 190, 250]
    steps = [
        ("обмін двох вузлів", SOFT, NEG),
        ("оцінити Δвартості", "#fdf6e3", AMBER),
        ("Δ<0 → взяти;\nінакше зрідка теж", SOFTG, SYN),
        ("трохи остудити T", "#f0f0f0", INK),
    ]
    boxw = 200
    for i, (lab, fill, col) in enumerate(steps):
        b, bw, bh = textbox(cx, ys[i], lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.7, min_w=boxw)
        p.append(b)
        if i > 0:
            p.append(arrow(cx, ys[i - 1] + bh / 2, cx, ys[i] - bh / 2, color=INK, sw=1.7))
    # петля назад угору
    p.append(line(cx + boxw / 2 + 6, ys[3], cx + boxw / 2 + 40, ys[3], color=MUTED, sw=1.6))
    p.append(line(cx + boxw / 2 + 40, ys[3], cx + boxw / 2 + 40, ys[0], color=MUTED, sw=1.6))
    p.append(arrow(cx + boxw / 2 + 40, ys[0], cx + boxw / 2 + 6, ys[0], color=MUTED, sw=1.6))
    p.append(text(cx + boxw / 2 + 46, (ys[0] + ys[3]) / 2, "поки", size=9, color=MUTED, anchor="start"))
    p.append(text(cx + boxw / 2 + 46, (ys[0] + ys[3]) / 2 + 12, "T > край", size=9, color=MUTED, anchor="start"))
    p.append(text(cx, 36, "цикл відпалу", size=12, color=INK, bold=True))

    # ── праворуч: поверхня вартості з локальною ямою ──
    ox, oy = 430, 250
    aw, ah = 270, 170
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5))
    p.append(text(ox - 8, oy - ah - 2, "вартість", size=10, color=INK, anchor="end", bold=True))
    p.append(text(ox + aw, oy + 18, "розкладка", size=10, color=INK, italic=True, anchor="end"))
    # крива з двома ямами
    pts = []
    for i in range(0, 271):
        t = i / 270.0
        # дрібна локальна яма ліворуч + глибокий глобальний мінімум праворуч
        v = 0.55 + 0.30 * math.cos(2.4 * math.pi * t) * math.exp(-1.1 * t) - 0.42 * math.exp(-((t - 0.78) ** 2) / 0.02)
        v = max(0.06, min(0.98, v))
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - v * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
             % (" ".join(pts), MUTED))
    # точка в локальній ямі + стрілка «вгору, щоб вибратися»
    lx0 = ox + 0.30 * aw
    p.append(circle(lx0, oy - 0.40 * ah, 5, fill=POS, stroke=POS, sw=1))
    p.append(text(lx0, oy - 0.40 * ah - 14, "локальна яма", size=10, color=POS))
    p.append(arrow(lx0 + 8, oy - 0.40 * ah, lx0 + 34, oy - 0.62 * ah, color=POS, sw=1.8))
    p.append(text(lx0 + 70, oy - 0.66 * ah, "інколи вгору —", size=10, color=POS, bold=True))
    p.append(text(lx0 + 70, oy - 0.66 * ah + 13, "щоб вибратися", size=10, color=POS))
    # глобальний мінімум
    gx0 = ox + 0.78 * aw
    p.append(circle(gx0, oy - 0.16 * ah, 5, fill=SYN, stroke=SYN, sw=1))
    p.append(text(gx0, oy - 0.16 * ah + 22, "справжній\nмінімум", size=10, color=SYN))
    p.append(text(ox + aw / 2, 36, "навіщо лізти вгору", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "anneal.svg"), W, H, *p,
           title="Імітація відпалу: цикл swap і вихід із локальної ями")


if __name__ == "__main__":
    fig_flow()
    fig_synthesis()
    fig_place_route()
    fig_bitstream()
    fig_config_flash()
    fig_pipeline()
    fig_placeroute_ice()
    fig_anneal()
    print("OK: figures written to", IMG)
