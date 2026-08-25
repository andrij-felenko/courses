# -*- coding: utf-8 -*-
"""Фігури до теми «Цикл виконання» (вибірка → декодування → виконання).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки на базі палітри svgkit (світлі заливки під рамки фаз)
RED_BG   = "#fdecea"   # вибірка
AMBER    = "#b8860b"   # декодування (тепле, не зелене/червоне)
AMBER_BG = "#fdf6e3"
GREEN_BG = "#eaf6ee"   # виконання
BLUE_BG  = "#eaf0fd"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


# ── 1. Огляд: три фази по колу ───────────────────────────────────────────────
def fig_cycle_overview():
    W, H = 720, 430
    f = []
    # три рамки фаз
    bx, by, bw, bh = 70, 70, 250, 120
    b1, w1, h1 = textbox(bx + bw / 2, by + bh / 2,
                         "ВИБІРКА\nузяти наступну команду\nз пам'яті за адресою PC\nу регістр IR; PC += 1",
                         size=13, fill=RED_BG, stroke=POS, sw=2.2, min_w=bw)
    f.append(b1)
    b2, _, _ = textbox(W - bx - bw / 2, by + bh / 2,
                       "ДЕКОДУВАННЯ\nрозібрати число-команду:\nяка операція,\nякі операнди",
                       size=13, fill=AMBER_BG, stroke=AMBER, sw=2.2, min_w=bw)
    f.append(b2)
    b3, _, _ = textbox(W / 2, H - 90,
                       "ВИКОНАННЯ\nзробити: АЛП рахує, або\nдоступ до пам'яті по шині,\nабо зміна PC (стрибок)",
                       size=13, fill=GREEN_BG, stroke=FIELD, sw=2.2, min_w=bw)
    f.append(b3)
    # стрілки по колу
    f.append(arrow(bx + bw, by + bh / 2, W - bx - bw, by + bh / 2, color=INK, sw=2.4))
    f.append(arrow(W - bx - bw / 2, by + bh, W / 2 + 110, H - 130, color=INK, sw=2.4))
    f.append(arrow(W / 2 - 110, H - 130, bx + bw / 2, by + bh, color=INK, sw=2.4))
    # серце в центрі
    f.append(text(W / 2, by + bh / 2 + 4, "♥", size=34, color=POS, bold=True))
    f.append(text(W / 2, by + bh / 2 + 30, "один оберт = одна команда", size=11, color=MUTED))
    out("cycle-overview.svg", W, H, *f,
        title="Серцебиття процесора: три фази по колу, і знову")


# ── 2. Вибірка ───────────────────────────────────────────────────────────────
def fig_fetch():
    W, H = 760, 360
    f = []
    # PC
    pc, _, _ = textbox(135, 175, "PC\n0x0C", size=14, fill=RED_BG, stroke=POS, sw=2, min_w=120)
    f.append(pc)
    f.append(arrow(200, 165, 360, 165, color=NEG, sw=2.2))
    f.append(text(280, 152, "адреса 0x0C", size=11, color=NEG, bold=True))
    # пам'ять
    f.append(rect(360, 95, 230, 190, fill="#f4f7f4", stroke=FIELD, sw=2))
    f.append(text(475, 120, "ПАМ'ЯТЬ", size=13, color=FIELD, bold=True))
    rows = [("0x0A", "завантаж R1", False), ("0x0B", "завантаж R2", False),
            ("0x0C", "ДОДАЙ R1,R2→R3", True), ("0x0D", "запиши R3", False)]
    ry = 132
    for addr, val, hot in rows:
        f.append(rect(376, ry, 200, 28, fill=(RED_BG if hot else BG),
                      stroke=(POS if hot else FIELD), sw=(1.6 if hot else 1.1)))
        f.append(text(388, ry + 19, addr, size=10, color=MUTED, anchor="start", bold=True))
        f.append(text(566, ry + 19, val, size=11, color=INK, anchor="end", bold=hot))
        ry += 34
    # команда → IR
    f.append(arrow(592, 200, 660, 200, color=FIELD, sw=2.2))
    ir, _, _ = textbox(700, 200, "IR\nДОДАЙ…", size=13, fill=AMBER_BG, stroke=AMBER, sw=2, min_w=110)
    f.append(ir)
    # PC += 1
    f.append(arrow(135, 202, 135, 250, color=FIELD, sw=2))
    inc, _, _ = textbox(135, 280, "PC += 1\n→ 0x0D", size=12, fill=GREEN_BG, stroke=FIELD, sw=1.6, min_w=120)
    f.append(inc)
    out("fetch.svg", W, H, *f,
        title="Вибірка: команду з пам'яті за PC у IR, потім PC += 1")


# ── 3. Декодування ───────────────────────────────────────────────────────────
def fig_decode():
    W, H = 780, 330
    f = []
    ir, _, _ = textbox(150, 165, "IR\nДОДАЙ R1,R2→R3", size=12, fill=AMBER_BG, stroke=AMBER, sw=2, min_w=170)
    f.append(ir)
    f.append(arrow(250, 165, 330, 165, color=INK, sw=2.2))
    cu, _, _ = textbox(430, 165, "пристрій\nкерування\n(декодер)", size=13, fill=BG, stroke=INK, sw=2, min_w=170)
    f.append(cu)
    f.append(arrow(520, 165, 600, 165, color=FIELD, sw=2.2))
    # вихідні поля
    fields = [("операція", "ДОДАТИ (+)", FIELD), ("операнд 1", "регістр R1", NEG),
              ("операнд 2", "регістр R2", NEG), ("результат →", "регістр R3", POS)]
    fy = 95
    for label, val, col in fields:
        f.append(rect(600, fy, 160, 34, fill="#fafafa", stroke=col, sw=1.6))
        f.append(text(610, fy + 22, label, size=10, color=MUTED, anchor="start", bold=True))
        f.append(text(750, fy + 22, val, size=11, color=col, anchor="end", bold=True))
        fy += 42
    f.append(text(W / 2, 300, "сигнали керування — декодер нічого не рахує, лише розуміє наказ",
                  size=11, color=MUTED, italic=True))
    out("decode.svg", W, H, *f,
        title="Декодування: число-команду — на операцію й операнди")


# ── 4. Виконання ─────────────────────────────────────────────────────────────
def fig_execute():
    W, H = 780, 340
    f = []
    # регістри-джерела
    f.append(rect(70, 120, 150, 32, fill=BLUE_BG, stroke=NEG, sw=1.6))
    f.append(text(82, 142, "R1", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(210, 142, "6", size=12, color=INK, anchor="end", bold=True))
    f.append(rect(70, 160, 150, 32, fill=BLUE_BG, stroke=NEG, sw=1.6))
    f.append(text(82, 182, "R2", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(210, 182, "5", size=12, color=INK, anchor="end", bold=True))
    f.append(arrow(222, 136, 320, 165, color=INK, sw=2))
    f.append(arrow(222, 176, 320, 185, color=INK, sw=2))
    # АЛП (трапеція-«воронка»)
    f.append('<path d="M320,150 L398,150 L412,170 L426,150 L504,150 L460,250 L364,250 Z" '
             'fill="%s" stroke="%s" stroke-width="2.2"/>' % (GREEN_BG, FIELD))
    f.append(text(412, 208, "АЛП: +", size=14, color=FIELD, bold=True))
    f.append(arrow(412, 252, 412, 288, color=INK, sw=2.2))
    # результат
    f.append(rect(330, 290, 170, 32, fill=RED_BG, stroke=POS, sw=1.6))
    f.append(text(342, 312, "R3 ← результат", size=12, color=POS, anchor="start", bold=True))
    f.append(text(490, 312, "11", size=12, color=INK, anchor="end", bold=True))
    # прапорці
    f.append(arrow(504, 200, 600, 200, color=AMBER, sw=2))
    fl, _, _ = textbox(685, 200, "прапорці оновлено\nZ=0 · C=0 · N=0 · V=0",
                       size=11, fill=AMBER_BG, stroke=AMBER, sw=1.8, min_w=170)
    f.append(fl)
    out("execute.svg", W, H, *f,
        title="Виконання: АЛП рахує, результат у регістр, прапорці оновлено")


# ── 5. Наскрізний прохід однієї команди ──────────────────────────────────────
def fig_trace():
    W, H = 900, 330
    f = []
    cols = [
        ("після ВИБІРКИ", POS, [("PC", "0x0D (наступна)"), ("IR", "ДОДАЙ R1,R2→R3"),
                                 ("R1 R2 R3", "6   5   —"), ("FLAGS", "—")]),
        ("після ДЕКОДУВАННЯ", AMBER, [("операція", "+ (додати)"), ("джерела", "R1, R2"),
                                       ("призначення", "R3"), ("АЛП", "готова, чекає")]),
        ("після ВИКОНАННЯ", FIELD, [("PC", "0x0D"), ("IR", "ДОДАЙ R1,R2→R3"),
                                     ("R1 R2 R3", "6   5   11"), ("FLAGS", "Z=0 C=0")]),
    ]
    cw, gap = 270, 15
    x0 = (W - 3 * cw - 2 * gap) / 2
    for i, (head, col, rows) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(rect(x, 60, cw, 240, fill="#fafafa", stroke=col, sw=2))
        f.append(rect(x, 60, cw, 32, fill=col, stroke=col, sw=0))
        f.append(text(x + cw / 2, 81, head, size=13, color=BG, bold=True))
        ry = 108
        for label, val in rows:
            f.append(rect(x + 14, ry, cw - 28, 34, fill=BG, stroke=col, sw=1.1))
            f.append(text(x + 26, ry + 22, label, size=10, color=MUTED, anchor="start", bold=True))
            f.append(text(x + cw - 14, ry + 22, val, size=11, color=INK, anchor="end", bold=True))
            ry += 42
        if i < 2:
            f.append(arrow(x + cw + 1, 180, x + cw + gap - 1, 180, color=INK, sw=2.2))
    out("trace.svg", W, H, *f,
        title="Одна команда «ДОДАЙ R1,R2→R3» крізь усі три фази")


# ── 6. Такт жене цикл ────────────────────────────────────────────────────────
def fig_clock():
    W, H = 880, 330
    f = []
    # рядок фаз: В Д В для трьох команд
    labels = ["В", "Д", "В", "В", "Д", "В", "В", "Д", "В"]
    colors = [POS, AMBER, FIELD, POS, AMBER, FIELD, POS, AMBER, FIELD]
    x = 90
    cellw = 66
    for lab, col in zip(labels, colors):
        f.append(rect(x, 90, cellw - 6, 40, fill=BG, stroke=col, sw=1.8))
        f.append(text(x + (cellw - 6) / 2, 116, lab, size=15, color=col, bold=True))
        x += cellw
    f.append(text(72, 116, "фази:", size=11, color=MUTED, anchor="end", bold=True))
    f.append(text(x + 4, 116, "…", size=18, color=MUTED, anchor="start", bold=True))
    # дужки-команди
    for k in range(3):
        cx0 = 90 + k * 3 * cellw
        cx1 = cx0 + 3 * cellw - 6
        f.append(line(cx0, 138, cx1, 138, color=MUTED, sw=1.4))
        f.append(text((cx0 + cx1) / 2, 154, "команда %d" % (k + 1), size=10, color=INK, bold=True))
    # такт-меандр
    f.append(text(72, 196, "такт:", size=11, color=NEG, anchor="end", bold=True))
    pts = []
    tx, hi, lo = 90, 178, 204
    up = True
    while tx <= 90 + 9 * cellw / 2:
        pts.append("%.0f,%.0f" % (tx, hi if up else lo))
        pts.append("%.0f,%.0f" % (tx + 18, hi if up else lo))
        tx += 18
        up = not up
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), NEG))
    f.append(text(W / 2, 240, "кожен удар такту просуває цикл на один крок", size=11, color=NEG, bold=True))
    # стрибок-дуга назад
    f.append('<path d="M%d,80 Q%d,46 90,80" fill="none" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (90 + 9 * cellw - 6, W / 2, NEG))
    f.append(text(W / 2, 40, "стрибок назад → повтор (цикл програми)", size=11, color=NEG, bold=True))
    f.append(text(W / 2, 300,
                  "програма не «запускається» чарівно — це коло крутиться знов і знов",
                  size=12, color=INK, bold=True))
    out("clock-drives-cycle.svg", W, H, *f,
        title="Такт жене цикл; цикл, що крутиться, — це програма в дії")


# ════════════════ ВСТАВКА: іграшковий емулятор ═══════════════════════════════

# ── 7. Цикл ↔ while-петля ────────────────────────────────────────────────────
def fig_emulator_loop():
    W, H = 900, 480
    f = []
    # ліворуч — коло фаз
    cx, cy, r = 220, 280, 130
    f.append(circle(cx, cy, r, fill="none", stroke="#e4e4e4", sw=2))
    # три вузли
    nodes = [(cx, cy - r, "ВИБІРКА", "(fetch)", FIELD),
             (cx + r * 0.87, cy + r * 0.5, "ВИКОНАННЯ", "(execute)", POS),
             (cx - r * 0.87, cy + r * 0.5, "наступна", "команда", NEG)]
    for nx, ny, t1, t2, col in nodes:
        f.append(circle(nx, ny, 10, fill=BG, stroke=col, sw=3))
        f.append(text(nx, ny - 18, t1, size=13, color=col, bold=True))
        f.append(text(nx, ny - 3, t2, size=10, color=col, italic=True))
    f.append(text(cx, cy, "цикл", size=13, color=MUTED, bold=True))
    f.append(text(cx, cy + 18, "крутиться", size=13, color=MUTED, bold=True))
    f.append(text(cx, cy + r + 50, "декодування зливається з вибіркою:", size=11, color=INK, bold=True))
    f.append(text(cx, cy + r + 67, "розрізати байт на op та операнди", size=11, color=INK))
    # праворуч — код у темній панелі
    px, py, pw, ph = 470, 90, 420, 380
    f.append(rect(px, py, pw, ph, fill="#0e1116", stroke="#0e1116", sw=0, rx=12))
    code = [
        ("// ядро емулятора", "#7fd58f"),
        ("while (running) {", "#e8e8e8"),
        ("    op = code[ip++];   // ВИБІРКА", FIELD),
        ("    a  = code[ip++];   //  + декод", FIELD),
        ("    switch (op) {      // ВИКОНАННЯ", POS),
        ("      case LD:  r[a]=code[ip++];", "#e8e8e8"),
        ("      case ADD: r[a]+=r[code[ip++]];", "#e8e8e8"),
        ("      case ST:  mem[code[ip++]]=r[a];", "#e8e8e8"),
        ("      case JMP: ip = a;", NEG),
        ("      case HLT: running = 0;", AMBER),
        ("      // ... решта з 8 опкодів ...", MUTED),
        ("    }", "#e8e8e8"),
        ("}", "#e8e8e8"),
    ]
    ty = py + 30
    for ln, col in code:
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="14" '
                 'fill="%s" text-anchor="start">%s</text>' % (px + 18, ty, col, esc(ln)))
        ty += 26
    # стрілки фаза→рядок
    f.append(arrow(cx + 12, cy - r - 6, px + 8, py + 70, color=FIELD, sw=2))
    f.append(arrow(nodes[1][0] + 8, nodes[1][1], px + 8, py + 130, color=POS, sw=2))
    out("emulator-loop.svg", W, H, *f,
        title="Цикл вибірка → декодування → виконання як while-петля на C")


# ── 8. Набір з 8 інструкцій ──────────────────────────────────────────────────
def fig_toy_isa():
    W, H = 900, 440
    f = []
    fam = {"дані": NEG, "арифм.": POS, "плин": FIELD}
    table = [
        ("0", "HLT",     "0  –  –", "зупинити машину (running ← 0)", "плин"),
        ("1", "LD  r,n", "1  r  n", "r ← n  (поклади число в регістр)", "дані"),
        ("2", "LDM r,a", "2  r  a", "r ← mem[a]  (читати з пам'яті)", "дані"),
        ("3", "ST  r,a", "3  r  a", "mem[a] ← r  (писати в пам'ять)", "дані"),
        ("4", "ADD r,s", "4  r  s", "r ← r + s  (рахує АЛП)", "арифм."),
        ("5", "SUB r,s", "5  r  s", "r ← r − s  (заразом для порівнянь)", "арифм."),
        ("6", "JMP a",   "6  a  –", "ip ← a  (безумовний стрибок)", "плин"),
        ("7", "JNZ r,a", "7  r  a", "якщо r≠0 → ip ← a  (цикл/гілка)", "плин"),
    ]
    x0, y0, rw = 30, 70, 840
    cols_x = [50, 110, 270, 410, 770]
    heads = ["код", "мнемоніка", "байти", "що робить", "родина"]
    rh = 40
    # шапка
    f.append(rect(x0, y0, rw, rh, fill="#eef2f7", stroke=INK, sw=1.6))
    for cx, h in zip(cols_x, heads):
        f.append(text(cx, y0 + 26, h, size=13, color=INK, anchor="start", bold=True))
    y = y0 + rh
    for op, mn, by, desc, family in table:
        col = fam[family]
        f.append(rect(x0, y, rw, rh, fill=(BG if (int(op) % 2 == 0) else "#f7f9fb"),
                      stroke="#e4e4e4", sw=1.1))
        f.append(rect(x0 + 16, y + 7, 26, 26, fill="#f0f0f0", stroke=col, sw=1.8))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="14" '
                 'fill="%s" text-anchor="middle" font-weight="700">%s</text>' % (x0 + 29, y + 26, col, op))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="14" '
                 'fill="%s" text-anchor="start" font-weight="700">%s</text>' % (cols_x[1], y + 26, INK, esc(mn)))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="13" '
                 'fill="%s" text-anchor="start">%s</text>' % (cols_x[2], y + 26, MUTED, esc(by)))
        f.append(text(cols_x[3], y + 26, desc, size=12, color=INK, anchor="start"))
        f.append(text(cols_x[4], y + 26, family, size=12, color=col, anchor="start", bold=True))
        y += rh
    f.append(rect(x0, y0, rw, rh * 9, fill="none", stroke=INK, sw=1.8))
    out("toy-isa.svg", W, H, *f,
        title="Уся «мова» іграшкового процесора: рівно 8 інструкцій")


# ── 9. Трасування множення 6×3 ───────────────────────────────────────────────
def fig_multiply_trace():
    W, H = 900, 470
    f = []
    # ліворуч — програма
    f.append(text(36, 80, "програма в code[] (адреси зліва):", size=13, color=INK, anchor="start", bold=True))
    prog = [(" 0", "LD  r0, 0", NEG), (" 3", "LD  r1, 3", NEG),
            (" 6", "ADD r0, r2", AMBER), (" 9", "SUB r1, r3", AMBER),
            ("12", "JNZ r1, 6", AMBER), ("15", "HLT", NEG)]
    py = 96
    for addr, ins, col in prog:
        f.append(rect(36, py, 250, 30, fill=("#fdf6e3" if col == AMBER else "#f6f8fb"), stroke=col, sw=1.6))
        f.append('<text x="46" y="%.0f" font-family="Consolas, monospace" font-size="12" '
                 'fill="%s" text-anchor="start">%s</text>' % (py + 20, MUTED, addr))
        f.append('<text x="84" y="%.0f" font-family="Consolas, monospace" font-size="13" '
                 'fill="%s" text-anchor="start" font-weight="700">%s</text>' % (py + 20, INK, esc(ins)))
        py += 34
    # дуга циклу
    f.append('<path d="M188,260 C338,286 338,168 196,182" fill="none" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % AMBER)
    f.append(text(300, 214, "цикл", size=11, color=AMBER, anchor="start", bold=True))
    f.append(text(36, 320, "(r2=6, r3=1 — наперед задані сталі)", size=11, color=MUTED, anchor="start", italic=True))
    # праворуч — таблиця обертів
    tx, ty, tw = 360, 90, 510
    f.append(text(tx, 80, "стан після кожного оберту циклу:", size=13, color=INK, anchor="start", bold=True))
    rows = [("старт", "LD r0,0 ; LD r1,3", "0", "3", INK),
            ("1", "r0+=6 ; r1−=1 ; r1≠0 → стриб", "6", "2", POS),
            ("2", "r0+=6 ; r1−=1 ; r1≠0 → стриб", "12", "1", POS),
            ("3", "r0+=6 ; r1−=1 ; r1=0 → далі", "18", "0", FIELD),
            ("стоп", "JNZ не стрибнув ; HLT", "18", "0", AMBER)]
    heads = ["оберт", "що сталося", "r0", "r1"]
    hx = [tx + 12, tx + 90, tx + 410, tx + 470]
    rh = 38
    f.append(rect(tx, ty, tw, rh, fill="#eef2f7", stroke=INK, sw=1.6))
    for cx, h in zip(hx, heads):
        f.append(text(cx, ty + 25, h, size=12, color=INK, anchor="start", bold=True))
    y = ty + rh
    for turn, what, r0, r1, col in rows:
        f.append(rect(tx, y, tw, rh, fill=BG, stroke="#e4e4e4", sw=1.1))
        f.append(text(hx[0], y + 25, turn, size=12, color=col, anchor="start", bold=True))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="12" '
                 'fill="%s" text-anchor="start">%s</text>' % (hx[1], y + 25, INK, esc(what)))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="14" '
                 'fill="%s" text-anchor="start" font-weight="700">%s</text>' % (hx[2], y + 25, col, r0))
        f.append('<text x="%.0f" y="%.0f" font-family="Consolas, monospace" font-size="14" '
                 'fill="%s" text-anchor="start" font-weight="700">%s</text>' % (hx[3], y + 25, col, r1))
        y += rh
    f.append(rect(tx, ty, tw, rh * 6, fill="none", stroke=INK, sw=1.8))
    # висновок
    res, _, _ = textbox(tx + tw / 2, y + 55,
                        "Відповідь у r0: 6 + 6 + 6 = 18 = 6×3.\n"
                        "Множення «зникло» — лишилось додавання в циклі, кероване JNZ.",
                        size=12, fill=GREEN_BG, stroke=FIELD, sw=1.8, min_w=tw)
    f.append(res)
    out("multiply-trace.svg", W, H, *f,
        title="Емулятор у русі: множення 6×3 додаванням у циклі")


if __name__ == "__main__":
    fig_cycle_overview()
    fig_fetch()
    fig_decode()
    fig_execute()
    fig_trace()
    fig_clock()
    fig_emulator_loop()
    fig_toy_isa()
    fig_multiply_trace()
    print("OK: 9 фігур у", IMG)
