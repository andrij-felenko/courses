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


# ════════════════ Фігури ДЕТАЛЬНОЇ статті (глибший шар) ══════════════════════

# ── 9. Синтез зсередини: розбір → RTL-оптимізація → технологічне відображення ─
def fig_synth_stages():
    W, H = 780, 340
    p = []
    y = 130
    bw, bh = 150, 90
    gap = 34
    x = 26
    stages = [
        ("розбір", "текст HDL →\nдерево, RTL-граф", HDLC, SOFT),
        ("RTL-оптимізація", "згорнути сталі,\nвикинути мертве,\nспільні підвирази", SYN, SOFTG),
        ("відображення", "покрити граф\nтаблицями LUT-k\n(covering)", AMBER, "#fdf6e3"),
    ]
    centers = []
    for i, (head, sub, col, fill) in enumerate(stages):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.9))
        p.append(text(x + bw / 2, y + 24, head, size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 44, sub, size=10, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y + bh / 2, x - 2, y + bh / 2, color=INK, sw=2.0))
        x += bw + gap
    # результат праворуч
    lastr = centers[-1][1]
    p.append(arrow(lastr, y + bh / 2, lastr + gap - 2, y + bh / 2, color=INK, sw=2.0))
    box, w2, h2 = textbox(lastr + gap + 66, y + bh / 2, "нетліст\nіз LUT-k і тригерів",
                          size=11, bold=True, color=CHIP, fill="#f0f0f0", stroke=CHIP, sw=1.9)
    p.append(box)
    # підпис під відображенням: одна фізична межа
    p.append(text(centers[2][0] + bw / 2, y + bh + 26,
                  "тут форма схеми стрибком міняється:", size=10, color=MUTED, italic=True))
    p.append(text(centers[2][0] + bw / 2, y + bh + 42,
                  "вентилі зникають, лишаються цеглинки кристала", size=10, color=MUTED, italic=True))
    # верхній підпис: усе це — «що», без «де»
    p.append(line(26, y - 26, centers[2][1], y - 26, color=SYN, sw=2.2))
    p.append(text((26 + centers[2][1]) / 2, y - 32,
                  "усе це відповідає на «ЩО будувати» — про «де на кристалі» ще ні слова",
                  size=10, color=SYN, bold=True))
    render(os.path.join(IMG, "synth-stages.svg"), W, H, *p,
           title="Синтез — три стадії: розбір, RTL-оптимізація, відображення в LUT")


# ── 10. STA: слек як різниця «є часу» і «треба часу» на одному шляху ──────────
def fig_slack():
    W, H = 720, 360
    p = []
    # часова вісь
    ax0, ay = 70, 150
    axlen = 560
    p.append(line(ax0, ay, ax0 + axlen, ay, color=INK, sw=1.6))
    p.append(text(ax0 + axlen, ay + 20, "час, нс", size=10, color=INK, anchor="end", italic=True))
    def tick(t, lab, col, up=True):
        x = ax0 + t / 12.0 * axlen
        dy = -8 if up else 8
        p.append(line(x, ay, x, ay + dy, color=col, sw=1.8))
        p.append(text(x, ay + (dy - 6 if up else dy + 14), lab, size=10, color=col, bold=True))
        return x
    # такт 10 нс, вимога прибуття = 10 − tsu; дані прибувають на 8.0
    xlaunch = tick(0, "0: старт такту", INK, up=False)
    xreq = tick(10, "10.0: край такту", MUTED, up=True)
    xsu = tick(9.6, "9.6: край − t_su", NEG, up=True)
    xarr = tick(8.0, "8.0: дані тут", SYN, up=False)
    # дуга прибуття даних (Tcq + logic + wire)
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (xlaunch, ay, (xlaunch + xarr) / 2, ay - 54, xarr, ay, SYN))
    p.append(text((xlaunch + xarr) / 2, ay - 60, "прибуття даних: T_cq + логіка + дріт = 8.0",
                  size=10, color=SYN, bold=True))
    # відрізок слеку
    p.append(line(xarr, ay + 46, xsu, ay + 46, color=POS, sw=2.6))
    p.append(line(xarr, ay + 40, xarr, ay + 52, color=POS, sw=1.6))
    p.append(line(xsu, ay + 40, xsu, ay + 52, color=POS, sw=1.6))
    p.append(text((xarr + xsu) / 2, ay + 70, "слек = 9.6 − 8.0 = +1.6 нс", size=11, color=POS, bold=True))
    p.append(text((xarr + xsu) / 2, ay + 86, "додатний → встигаємо; від'ємний → зрив", size=10, color=MUTED, italic=True))
    # формула зверху
    box, w2, h2 = textbox(W / 2, 300,
                          "слек = (край такту − t_su) − (T_cq + t_логіки + t_дроту)",
                          size=12, bold=True, color=INK, fill=SOFT, stroke=NEG, sw=1.8)
    p.append(box)
    render(os.path.join(IMG, "slack.svg"), W, H, *p,
           title="Статичний аналіз таймінгу: слек одного шляху")


# ── 11. Негоційоване трасування: present + history робить ресурс дорогим ──────
def fig_negotiate():
    W, H = 760, 340
    p = []
    # три ітерації: спільний ресурс дорожчає, поки один сигнал не поступиться
    col_share = POS
    xs = [150, 380, 610]
    labs = ["ітерація 1", "ітерація 5", "ітерація 12"]
    caps = ["обидва сигнали лізуть\nв один канал —\nдозволено, але дорого",
            "історія перевантаження\nросте → канал ще дорожчий\nобом невигідно",
            "слабший сигнал знайшов\nобхід; сильніший лишився —\nконфлікту нема"]
    for i, (cx, lab, cap) in enumerate(zip(xs, labs, caps)):
        # канал (ресурс)
        p.append(rect(cx - 26, 70, 52, 60, fill=("#fdecea" if i < 2 else SOFTG),
                      stroke=(col_share if i < 2 else SYN), sw=2.0))
        # сигнали, що претендують
        if i == 0:
            p.append(circle(cx - 8, 100, 7, fill=NEG, stroke=NEG, sw=1));
            p.append(circle(cx + 8, 100, 7, fill=AMBER, stroke=AMBER, sw=1))
            p.append(text(cx, 150, "2 сигнали / 1 канал", size=9, color=col_share, bold=True))
        elif i == 1:
            p.append(circle(cx - 8, 100, 7, fill=NEG, stroke=NEG, sw=1))
            p.append(circle(cx + 8, 100, 7, fill=AMBER, stroke=AMBER, sw=1))
            p.append(text(cx, 150, "штраф історії ↑", size=9, color=col_share, bold=True))
        else:
            p.append(circle(cx, 100, 7, fill=AMBER, stroke=AMBER, sw=1))
            p.append(circle(cx + 40, 100, 7, fill=NEG, stroke=NEG, sw=1))
            p.append(line(cx + 26, 100, cx + 33, 100, color=NEG, sw=1.6, dash="3 2"))
            p.append(text(cx + 6, 150, "розвели", size=9, color=SYN, bold=True))
        p.append(text(cx, 58, lab, size=11, color=INK, bold=True))
        p.append(mtext(cx, 176, cap, size=9, color=MUTED))
        if i < 2:
            p.append(arrow(xs[i] + 60, 100, xs[i + 1] - 60, 100, color=INK, sw=1.8))
    # формула вартості внизу
    box, w2, h2 = textbox(W / 2, 290,
                          "вартість ресурсу = базова · (1 + present_зайнятість) · (1 + history_штраф)",
                          size=11, bold=True, color=INK, fill=SOFT, stroke=NEG, sw=1.8)
    p.append(box)
    render(os.path.join(IMG, "negotiate.svg"), W, H, *p,
           title="Негоційоване трасування: спільний ресурс дорожчає, поки конфлікт не зникне")


# ── 12. Петля timing closure: зібрав → перевірив слек → правки → знову ────────
def fig_closure_loop():
    W, H = 720, 380
    p = []
    cx = 250
    ys = [70, 145, 220, 295]
    steps = [
        ("синтез + P&R", "інструмент склав розкладку", SYN, SOFTG),
        ("STA: найгірший слек?", "порахувати запас на\nкритичному шляху", AMBER, "#fdf6e3"),
        ("слек < 0 → зрив", "шлях не встигає за тактом", POS, "#fdecea"),
        ("правки дизайну", "конвеєр, менше логіки,\nобмеження, seed", NEG, SOFT),
    ]
    boxw = 250
    hh = []
    for i, (head, sub, col, fill) in enumerate(steps):
        b, bw, bh = textbox(cx, ys[i], head + "\n" + sub, size=11, bold=False, color=INK,
                            fill=fill, stroke=col, sw=1.8, min_w=boxw)
        # заголовок жирним окремо
        p.append(rect(cx - bw / 2, ys[i] - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(cx, ys[i] - bh / 2 + 18, head, size=12, color=col, bold=True))
        p.append(mtext(cx, ys[i] - bh / 2 + 36, sub, size=10, color=INK))
        hh.append(bh)
        if i > 0:
            p.append(arrow(cx, ys[i - 1] + hh[i - 1] / 2, cx, ys[i] - bh / 2, color=INK, sw=1.9))
    # гілка «слек ≥ 0 → готово» праворуч від кроку STA
    rx = cx + boxw / 2 + 30
    b2, w2, h2 = textbox(rx + 70, ys[1], "слек ≥ 0 →\nбітстрім, готово",
                         size=11, bold=True, color=SYN, fill=SOFTG, stroke=SYN, sw=1.9)
    p.append(b2)
    p.append(arrow(cx + boxw / 2, ys[1], rx, ys[1], color=SYN, sw=1.9))
    p.append(text((cx + boxw / 2 + rx) / 2, ys[1] - 8, "так", size=9, color=SYN, bold=True))
    # петля назад від «правок» до «синтез+P&R»
    lx = cx - boxw / 2 - 24
    p.append(line(cx - boxw / 2, ys[3], lx, ys[3], color=NEG, sw=1.8))
    p.append(line(lx, ys[3], lx, ys[0], color=NEG, sw=1.8))
    p.append(arrow(lx, ys[0], cx - boxw / 2, ys[0], color=NEG, sw=1.8))
    p.append(text(lx - 6, (ys[0] + ys[3]) / 2, "знову", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(lx - 6, (ys[0] + ys[3]) / 2 + 14, "весь потік", size=10, color=NEG, anchor="end"))
    render(os.path.join(IMG, "closure-loop.svg"), W, H, *p,
           title="Петля timing closure: збирай, міряй слек, прав, повторюй")


# ═══ Фігури до вставки math-lut-covering (FlowMap) ═══════════════════════════

# Кольори саме для цієї вставки
CONE = "#7b3fbf"      # конус / LUT-межа (фіолетовий)
CONEF = "#f3ecfb"     # світла заливка конуса
CUT = "#c0392b"       # лінія розрізу (червона)


def _dot(cx, cy, r, fill, stroke=INK, sw=1.6):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)


# ── 13. Відображення як покриття DAG конусами по k входів ────────────────────
def fig_cover():
    """Той самий граф вентилів, укритий K-feasible-конусами: кожен конус = один LUT-k."""
    W, H = 760, 430
    p = []
    R = 15
    # координати вузлів графа (шар за шаром знизу вгору)
    # первинні входи
    ins = {"a": (70, 360), "b": (150, 360), "c": (250, 360),
           "d": (350, 360), "e": (470, 360), "f": (590, 360), "g": (690, 360)}
    # внутрішні вузли (вентилі)
    g1 = (110, 275); g2 = (300, 275); g3 = (530, 275); g4 = (650, 275)
    g5 = (205, 185); g6 = (590, 185)
    root = (400, 95)
    nodes = dict(ins); nodes.update({"g1": g1, "g2": g2, "g3": g3, "g4": g4,
                                     "g5": g5, "g6": g6, "root": root})
    edges = [("a", "g1"), ("b", "g1"), ("c", "g2"), ("d", "g2"),
             ("e", "g3"), ("f", "g3"), ("f", "g4"), ("g", "g4"),
             ("g1", "g5"), ("g2", "g5"), ("g3", "g6"), ("g4", "g6"),
             ("g5", "root"), ("g6", "root")]
    # три конуси (кожен ≤ 4 входи) — малюємо як напівпрозорі «шапки» позаду
    def cone(pts, cx, cy):
        # многокутник-обгортка навколо переліку точок (проста опукла шапка)
        return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6" '
                'opacity="0.9"/>' % (" ".join("%.0f,%.0f" % pt for pt in pts), CONEF, CONE))
    # конус L1: g5 з входами g1,g2 → 4 входи (a,b,c,d)
    p.append(cone([(60, 300), (95, 250), (300, 250), (340, 300), (240, 330)],
                  *g5))
    # конус L2: g6 з входами g3,g4 → 4 входи (e,f,g)
    p.append(cone([(455, 300), (500, 250), (680, 250), (720, 300), (600, 330)],
                  *g6))
    # конус root: входи g5,g6 → 2 входи
    p.append(cone([(150, 210), (205, 155), (595, 155), (640, 210), (400, 130)],
                  *root))
    # ребра
    for u, v in edges:
        x1, y1 = nodes[u]; x2, y2 = nodes[v]
        p.append(line(x1, y1 - R + 3, x2, y2 + R - 3, color=MUTED, sw=1.6))
    # вузли-входи (квадратики)
    for nm, (x, y) in ins.items():
        p.append(rect(x - 12, y - 12, 24, 24, fill=SOFT, stroke=NEG, sw=1.7, rx=3))
        p.append(text(x, y + 5, nm, size=12, color=NEG, bold=True))
    # внутрішні вузли (кола)
    for nm in ["g1", "g2", "g3", "g4", "g5", "g6", "root"]:
        x, y = nodes[nm]
        p.append(_dot(x, y, R, fill="#fff", stroke=INK, sw=1.7))
    p.append(text(root[0] + R + 6, root[1], "вихід", size=11, color=INK,
                  anchor="start", bold=True))
    # підписи конусів = LUT (біля вершини конуса, збоку від вузла-кореня)
    p.append(text(g5[0] - R - 8, g5[1] - 2, "LUT₁", size=11, color=CONE,
                  anchor="end", bold=True))
    p.append(text(g6[0] + R + 8, g6[1] - 2, "LUT₂", size=11, color=CONE,
                  anchor="start", bold=True))
    p.append(text(root[0] - R - 8, root[1], "LUT₃", size=11, color=CONE,
                  anchor="end", bold=True))
    # легенда — угорі ліворуч, де вільно
    lb, lw, lh = textbox(120, 90, "квадрат — вхід\nколо — вентиль\nшапка — один LUT-k",
                         size=10, color=INK, fill="#fff", stroke=MUTED, sw=1.3)
    p.append(lb)
    render(os.path.join(IMG, "cover.svg"), W, H, *p,
           title="Відображення = покриття графа конусами по ≤ k входів (кожен конус — один LUT)")


# ── 14. Крок мітки: min-cut вирішує l(t) = p чи p+1 ──────────────────────────
def fig_labelcut():
    """Дві половини: зліва — підмережа N_t зі збором вузлів label≥p у стік;
    справа — розріз ≤ k (успіх, l=p) проти розрізу > k (невдача, l=p+1)."""
    W, H = 760, 400
    p = []
    R = 14
    # ── ліва панель: побудова мережі ──
    p.append(text(190, 40, "1. збери у стік усе з міткою ≥ p", size=12, color=INK, bold=True))
    # вузли: кілька входів з мітками, вузол t згори
    lvl = {"u1": (70, 300, "1"), "u2": (140, 300, "2"), "u3": (210, 300, "1"),
           "u4": (300, 300, "2"), "v1": (110, 220, "2"), "v2": (250, 220, "2")}
    t = (190, 130)
    for nm, (x, y, lb) in lvl.items():
        col = POS if lb == "2" else MUTED
        p.append(_dot(x, y, R, fill="#fff", stroke=col, sw=1.8))
        p.append(text(x, y + 4, lb, size=11, color=col, bold=True))
    # ребра до t
    for nm, (x, y, lb) in lvl.items():
        p.append(line(x, y - R + 2, t[0], t[1] + R - 2, color=MUTED, sw=1.4))
    p.append(_dot(t[0], t[1], R, fill=SOFTG, stroke=SYN, sw=2.0))
    p.append(text(t[0], t[1] + 4, "t", size=12, color=SYN, bold=True))
    # «стік»: пунктирна обгортка навколо label-2 вузлів + t
    p.append('<ellipse cx="185" cy="205" rx="140" ry="120" fill="none" '
             'stroke="%s" stroke-width="1.8" stroke-dasharray="6 5"/>' % CUT)
    p.append(text(185, 345, "p = max мітка входів = 2", size=11, color=POS, bold=True))
    p.append(mtext(300, 95, "стік t′:\nусе з міткою ≥ p\nзлите з t разом", size=9,
                   color=CUT, anchor="middle", lh=1.25))
    # роздільник
    p.append(line(390, 60, 390, 360, color=MUTED, sw=1.4, dash="4 4"))
    # ── права панель: два розрізи ──
    p.append(text(575, 40, "2. є розріз заввишки p−1 з ≤ k ребрами?", size=12, color=INK, bold=True))
    # успіх
    bx = 470
    p.append(_dot(bx, 300, R, fill="#fff", stroke=MUTED, sw=1.6))
    p.append(_dot(bx + 70, 300, R, fill="#fff", stroke=MUTED, sw=1.6))
    p.append(_dot(bx + 35, 210, R, fill=SOFTG, stroke=SYN, sw=1.9))
    p.append(line(bx, 300 - R, bx + 35, 210 + R, color=INK, sw=1.6))
    p.append(line(bx + 70, 300 - R, bx + 35, 210 + R, color=INK, sw=1.6))
    p.append(line(bx - 20, 255, bx + 90, 255, color=CUT, sw=2.4, dash="7 4"))
    p.append(text(bx + 35, 175, "розріз = 2 ≤ k", size=10, color=SYN, bold=True))
    b1, w1, h1 = textbox(bx + 35, 145, "l(t) = p", size=12, bold=True,
                         color=SYN, fill=SOFTG, stroke=SYN, sw=1.9)
    p.append(b1)
    # невдача
    fx = 640
    for dx in (-25, 0, 25, 50):
        p.append(_dot(fx + dx, 300, R - 2, fill="#fff", stroke=MUTED, sw=1.5))
    p.append(_dot(fx + 12, 210, R, fill="#fdecea", stroke=POS, sw=1.9))
    for dx in (-25, 0, 25, 50):
        p.append(line(fx + dx, 300 - R, fx + 12, 210 + R, color=INK, sw=1.4))
    p.append(line(fx - 45, 255, fx + 75, 255, color=CUT, sw=2.4, dash="7 4"))
    p.append(text(fx + 12, 175, "будь-який розріз > k", size=10, color=POS, bold=True))
    b2, w2, h2 = textbox(fx + 12, 145, "l(t) = p+1", size=12, bold=True,
                         color=POS, fill="#fdecea", stroke=POS, sw=1.9)
    p.append(b2)
    render(os.path.join(IMG, "labelcut.svg"), W, H, *p,
           title="Крок мітки: мінімальний розріз вирішує, l(t) = p чи p+1")


# ── 15. Мітки = глибина: найбільша мітка на виходах і є оптимальна глибина ────
def fig_labels_depth():
    """Той самий DAG, але кожен вузол несе свою мітку; мітка виходу = число LUT
    на найдовшому ланцюгу = оптимальна глибина."""
    W, H = 720, 380
    p = []
    R = 16
    # шари; підписуємо мітку в кожному вузлі
    ins = {"a": (60, 320, 0), "b": (130, 320, 0), "c": (210, 320, 0),
           "d": (290, 320, 0), "e": (400, 320, 0), "f": (480, 320, 0), "g": (560, 320, 0)}
    inner = {"g1": (95, 240, 1), "g2": (250, 240, 1), "g3": (440, 240, 1), "g4": (560, 240, 1),
             "g5": (170, 160, 1), "g6": (500, 160, 2), "root": (330, 85, 2)}
    edges = [("a", "g1"), ("b", "g1"), ("c", "g2"), ("d", "g2"),
             ("e", "g3"), ("f", "g3"), ("f", "g4"), ("g", "g4"),
             ("g1", "g5"), ("g2", "g5"), ("g3", "g6"), ("g4", "g6"),
             ("g5", "root"), ("g6", "root")]
    alln = {k: (x, y) for k, (x, y, _) in ins.items()}
    alln.update({k: (x, y) for k, (x, y, _) in inner.items()})
    for u, v in edges:
        x1, y1 = alln[u]; x2, y2 = alln[v]
        p.append(line(x1, y1 - R + 3, x2, y2 + R - 3, color=MUTED, sw=1.5))
    for nm, (x, y, lb) in ins.items():
        p.append(rect(x - 12, y - 12, 24, 24, fill=SOFT, stroke=NEG, sw=1.6, rx=3))
        p.append(text(x, y + 4, str(lb), size=11, color=NEG, bold=True))
    for nm, (x, y, lb) in inner.items():
        hot = (nm in ("g6", "root"))
        p.append(_dot(x, y, R, fill=("#fdecea" if hot else "#fff"),
                      stroke=(POS if hot else INK), sw=1.8))
        p.append(text(x, y + 5, str(lb), size=12, color=(POS if hot else INK), bold=True))
    # позначити критичну гілку g3/g4 → g6 → root
    for u, v in [("g3", "g6"), ("g4", "g6"), ("g6", "root")]:
        x1, y1 = alln[u]; x2, y2 = alln[v]
        p.append(line(x1, y1 - R + 3, x2, y2 + R - 3, color=POS, sw=2.6))
    p.append(text(330, 60, "мітка виходу = 2 = глибина мережі LUT (оптимум)",
                  size=12, color=POS, bold=True))
    lb2, w2, h2 = textbox(620, 330,
                          "мітка = скільки LUT\nна найдовшому шляху\nсюди від входів",
                          size=10, color=INK, fill="#fff", stroke=MUTED, sw=1.3)
    p.append(lb2)
    render(os.path.join(IMG, "labels-depth.svg"), W, H, *p,
           title="Мітки поширюються вперед; найбільша на виходах = оптимальна глибина")


if __name__ == "__main__":
    fig_flow()
    fig_synthesis()
    fig_place_route()
    fig_bitstream()
    fig_config_flash()
    fig_pipeline()
    fig_placeroute_ice()
    fig_anneal()
    fig_synth_stages()
    fig_slack()
    fig_negotiate()
    fig_closure_loop()
    fig_cover()
    fig_labelcut()
    fig_labels_depth()
    print("OK: figures written to", IMG)
