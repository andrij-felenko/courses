# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CELL = "#eef4ff"      # заливка комірки пам'яті
CELLB = "#c9d6f0"     # її обведення
HOT = "#fdecea"       # підсвітка обраного рядка/комірки


# ── truth-to-lut: стовпець виходів таблиці істинності переїжджає в пам'ять ─────
# Ідея: таблицю істинності XOR не «рахують» вентилями, а зберігають останній
# стовпець у чотирьох комірках; пара входів (a,b) = адреса, що читає рядок.

def fig_truth_to_lut():
    W, H = 720, 320
    p = []
    p.append(text(W / 2, 26, "Таблиця істинності → стовпець у пам'яті", size=17, bold=True))

    # ── таблиця істинності XOR ліворуч ──
    rows = [("0", "0", "0"), ("0", "1", "1"), ("1", "0", "1"), ("1", "1", "0")]
    tx, ty = 60, 70
    cw, rh = 42, 40
    # шапка
    p.append(text(tx + cw * 0.5, ty - 10, "a", size=14, bold=True, italic=True))
    p.append(text(tx + cw * 1.5, ty - 10, "b", size=14, bold=True, italic=True))
    p.append(text(tx + cw * 2.5, ty - 10, "F", size=14, bold=True, italic=True, color=POS))
    for i, (a, b, f) in enumerate(rows):
        y = ty + i * rh
        p.append(rect(tx, y, cw, rh, fill=BG, sw=1.2, rx=0))
        p.append(rect(tx + cw, y, cw, rh, fill=BG, sw=1.2, rx=0))
        p.append(rect(tx + 2 * cw, y, cw, rh, fill=HOT, sw=1.2, rx=0))
        p.append(text(tx + cw * 0.5, y + rh * 0.62, a, size=14))
        p.append(text(tx + cw * 1.5, y + rh * 0.62, b, size=14))
        p.append(text(tx + cw * 2.5, y + rh * 0.62, f, size=14, bold=True, color=POS))
    p.append(text(tx + cw * 1.5, ty + 4 * rh + 22, "F = a XOR b", size=13, italic=True, color=MUTED))

    # ── стрілка «запам'ятати стовпець» ──
    ax0 = tx + 3 * cw + 14
    p.append(arrow(ax0, ty + 2 * rh, ax0 + 120, ty + 2 * rh, color=FIELD, sw=2.2))
    p.append(text(ax0 + 60, ty + 2 * rh - 12, "запам'ятати", size=12, color=FIELD, bold=True))
    p.append(text(ax0 + 60, ty + 2 * rh + 24, "стовпець F", size=12, color=FIELD))

    # ── LUT праворуч: 4 комірки пам'яті, адресовані (a,b) ──
    lx, ly = ax0 + 150, 70
    bits = ["0", "1", "1", "0"]
    addr = ["00", "01", "10", "11"]
    for i, (bt, ad) in enumerate(zip(bits, addr)):
        y = ly + i * rh
        hot = (ad == "01")
        p.append(rect(lx + 44, y, 56, rh, fill=(HOT if hot else CELL),
                      stroke=(POS if hot else CELLB), sw=(2 if hot else 1.4), rx=4))
        p.append(text(lx + 44 + 28, y + rh * 0.62, bt, size=15, bold=True))
        p.append(text(lx + 30, y + rh * 0.62, "адр " + ad, size=11, color=MUTED, anchor="end"))
    p.append(text(lx + 72, ly - 10, "4 комірки SRAM", size=12, color=MUTED, bold=True))

    # підпис вибору
    p.append(text(lx + 72, ly + 4 * rh + 22, "вхід (a,b)=(0,1) → адреса 01 → читає 1",
                  size=12, color=POS))

    render(os.path.join(OUT, "truth-to-lut.svg"), W, H, *p)


# ── mux-tree: всередині LUT — біти SRAM + дерево мультиплексорів ──────────────
# Ідея: 4 збережені біти зліва, два рівні mux; вхід b обирає в парах, вхід a —
# між двома вцілілими. Вентилі сталі, міняється лише вміст комірок.

def fig_mux_tree():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 26, "Усередині LUT: біти SRAM + дерево мультиплексорів", size=17, bold=True))

    # 4 комірки SRAM
    sx, sy, ch = 60, 70, 50
    bits = ["0", "1", "1", "0"]
    for i, bt in enumerate(bits):
        y = sy + i * (ch + 8)
        p.append(rect(sx, y, 70, ch, fill=CELL, stroke=CELLB, sw=1.4))
        p.append(text(sx + 35, y + ch * 0.62, bt, size=16, bold=True))
    p.append(text(sx + 35, sy - 12, "SRAM", size=12, color=MUTED, bold=True))
    p.append(text(sx + 35, sy + 4 * (ch + 8) + 4, "заливає бітстрім", size=11, color=MUTED))

    # рівень 1: два mux 2→1, керовані b
    m1x = sx + 150
    def mux(cx, cy, label):
        # трапеція mux
        w, h = 26, 56
        d = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
             'fill="%s" stroke="%s" stroke-width="1.5"/>' %
             (cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 10,
              cx + w / 2, cy + h / 2 - 10, cx - w / 2, cy + h / 2, FILL, LINE))
        return d + text(cx, cy + 4, label, size=11, color=MUTED)
    y_a = sy + (ch + 8) * 0.5 + ch / 2 - 4
    y_b = sy + (ch + 8) * 2.5 + ch / 2 - 4
    p.append(mux(m1x, y_a, "mux"))
    p.append(mux(m1x, y_b, "mux"))
    # дроти від комірок до mux рівня 1
    for i in range(4):
        y = sy + i * (ch + 8) + ch / 2
        tgt = y_a if i < 2 else y_b
        p.append(line(sx + 70, y, m1x - 13, tgt + (i % 2 - 0.5) * 18, color=LINE, sw=1.2))
    p.append(text(m1x, sy - 12, "рівень b", size=12, color=NEG, bold=True))

    # рівень 2: один mux, керований a
    m2x = m1x + 130
    y_o = (y_a + y_b) / 2
    p.append(mux(m2x, y_o, "mux"))
    p.append(line(m1x + 13, y_a, m2x - 13, y_o - 14, color=LINE, sw=1.2))
    p.append(line(m1x + 13, y_b, m2x - 13, y_o + 14, color=LINE, sw=1.2))
    p.append(text(m2x, sy - 12, "рівень a", size=12, color=NEG, bold=True))

    # вихід
    p.append(arrow(m2x + 13, y_o, m2x + 90, y_o, color=INK, sw=1.8))
    p.append(text(m2x + 100, y_o + 5, "F", size=15, bold=True, italic=True, color=POS, anchor="start"))

    # керувальні входи b, a знизу
    p.append(text(m1x, H - 28, "b", size=14, bold=True, italic=True, color=NEG))
    p.append(line(m1x, H - 40, m1x, y_b + 36, color=NEG, sw=1.2, dash="4 3"))
    p.append(text(m2x, H - 28, "a", size=14, bold=True, italic=True, color=NEG))
    p.append(line(m2x, H - 40, m2x, y_o + 30, color=NEG, sw=1.2, dash="4 3"))

    render(os.path.join(OUT, "mux-tree.svg"), W, H, *p)


# ── any-function: 16 рядків таблиці ↔ 16 комірок, один-в-один ─────────────────
# Ідея: функція 4 змінних = 16 біт виходу; LUT-4 = 16 комірок; відповідність
# один-в-один, тож будь-який із 2¹⁶ візерунків — це якась функція.

def fig_any_function():
    W, H = 720, 330
    p = []
    p.append(text(W / 2, 26, "16 рядків таблиці ↔ 16 комірок LUT-4", size=17, bold=True))

    # ліворуч: стовпчик 16 рядків (схематично)
    lx, ly = 90, 56
    rh = 16
    for i in range(16):
        y = ly + i * rh
        p.append(rect(lx, y, 24, rh - 2, fill=BG, sw=0.8, rx=0))
        p.append(rect(lx + 24, y, 22, rh - 2, fill=HOT, sw=0.8, rx=0))
    p.append(text(lx + 23, ly - 10, "16 рядків", size=12, color=MUTED, bold=True))
    p.append(text(lx + 12, ly + 16 * rh + 16, "входи", size=10, color=MUTED))
    p.append(text(lx + 35, ly + 16 * rh + 16, "вихід", size=10, color=POS))

    # стрілки відповідності (кілька, щоб не зашумити)
    rx = lx + 240
    for i in (0, 5, 10, 15):
        y = ly + i * rh + (rh - 2) / 2
        p.append(line(lx + 46 + 6, y, rx - 6, y, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text((lx + 46 + rx) / 2, ly - 10, "один-в-один", size=12, color=FIELD, bold=True))

    # праворуч: 4×4 решітка комірок
    for i in range(16):
        col, row = i % 4, i // 4
        x = rx + col * 36
        y = ly + row * 36
        p.append(rect(x, y, 32, 32, fill=CELL, stroke=CELLB, sw=1.2, rx=4))
        p.append(text(x + 16, y + 21, "•", size=14, color=MUTED))
    p.append(text(rx + 70, ly - 10, "16 комірок", size=12, color=MUTED, bold=True))

    # підсумкове число
    p.append(text(W / 2, H - 24, "будь-який із 2¹⁶ = 65 536 візерунків = якась функція 4 змінних",
                  size=13, color=INK))

    render(os.path.join(OUT, "any-function.svg"), W, H, *p)


# ── lut-vs-gates: одна LUT-2, чотири різні функції від чотирьох бітів змісту ──
# Ідея: AND/OR/XOR/довільна — це лише різний 4-бітний вміст однієї й тієї ж
# таблиці. Схема стала, міняється пам'ять.

def fig_lut_vs_gates():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 26, "Та сама LUT-2 — різні функції від 4 бітів змісту", size=17, bold=True))

    cards = [("AND", "0 0 0 1"), ("OR", "0 1 1 1"), ("XOR", "0 1 1 0"), ("a·b̄+c", "1 0 1 1")]
    cw = 150
    gap = 22
    total = len(cards) * cw + (len(cards) - 1) * gap
    x0 = (W - total) / 2
    cy = 150
    for i, (name, content) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, 70, cw, 150, fill=BG, sw=1.5, rx=8))
        p.append(text(x + cw / 2, 96, name, size=16, bold=True, color=POS))
        # 4 комірки змісту в рядок
        vals = content.split()
        bw = 26
        bx0 = x + (cw - 4 * bw) / 2
        for j, v in enumerate(vals):
            bx = bx0 + j * bw
            p.append(rect(bx, 120, bw - 4, 30, fill=CELL, stroke=CELLB, sw=1.2, rx=3))
            p.append(text(bx + (bw - 4) / 2, 141, v, size=14, bold=True))
        p.append(text(x + cw / 2, 178, "вміст комірок", size=11, color=MUTED))
        p.append(text(x + cw / 2, 204, "та сама схема", size=11, color=FIELD, italic=True))

    render(os.path.join(OUT, "lut-vs-gates.svg"), W, H, *p)


# ── lut-size: біти LUT ростуть як 2ⁿ; солодка точка 4–6 входів ────────────────
# Ідея: стовпчики 2ⁿ біт різко злітають; зелена смуга 4–6 — компроміс ємності
# й ціни; LUT-8 (256 біт) непідйомна.

def fig_lut_size():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 26, "Біти LUT ростуть як 2ⁿ — солодка точка 4–6 входів", size=17, bold=True))

    ox, oy = 80, 270
    aw, ah = 560, 200
    ns = [2, 3, 4, 5, 6, 7, 8]
    bits = [4, 8, 16, 32, 64, 128, 256]
    bw = 46
    dx = aw / len(ns)

    # зелена смуга 4–6
    i4 = ns.index(4)
    i6 = ns.index(6)
    bandx0 = ox + i4 * dx + (dx - bw) / 2 - 8
    bandx1 = ox + i6 * dx + (dx - bw) / 2 + bw + 8
    p.append(rect(bandx0, oy - ah - 4, bandx1 - bandx0, ah + 4, fill="#eafaf0",
                  stroke=FIELD, sw=1.2, rx=6))
    p.append(text((bandx0 + bandx1) / 2, oy - ah - 12, "солодка точка", size=12,
                  color=FIELD, bold=True))

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 16, oy - ah, "біти", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox + aw, oy + 22, "входи n", size=12, color=INK, italic=True))

    maxbits = 256
    for i, (n, b) in enumerate(zip(ns, bits)):
        x = ox + i * dx + (dx - bw) / 2
        h = ah * (b / maxbits)
        inband = 4 <= n <= 6
        p.append(rect(x, oy - h, bw, h, fill=(CELL if not inband else "#cdeedd"),
                      stroke=(CELLB if not inband else FIELD), sw=1.4, rx=3))
        p.append(text(x + bw / 2, oy - h - 8, str(b), size=12, bold=True))
        p.append(text(x + bw / 2, oy + 20, str(n), size=13, bold=True))

    render(os.path.join(OUT, "lut-size.svg"), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до математичної вставки (math-lut-math.md)
# ════════════════════════════════════════════════════════════════════════════

# ── lut-is-memory: 3-входова LUT — 8 комірок + mux 8→1, адресований A,B,C ─────
# Ідея: стовпець F таблиці істинності трьох змінних лягає у 8 комірок SRAM;
# трійка входів = адреса, mux 8→1 видає рівно обрану комірку.

def fig_lut_is_memory():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 26, "3-входова LUT: вісім комірок і мультиплексор 8→1", size=17, bold=True))

    # таблиця істинності (схематична) ліворуч: 8 рядків, стовпець F виділено
    tx, ty = 56, 60
    rh = 32
    Fbits = ["0", "1", "1", "0", "1", "0", "0", "1"]
    p.append(text(tx + 30, ty - 10, "A B C", size=12, bold=True, color=MUTED))
    p.append(text(tx + 92, ty - 10, "F", size=12, bold=True, color=POS))
    for i in range(8):
        y = ty + i * rh
        abc = format(i, "03b")
        p.append(text(tx + 30, y + rh * 0.62, " ".join(abc), size=12, color=INK))
        p.append(rect(tx + 78, y, 30, rh - 3, fill=HOT, sw=1.0, rx=0))
        p.append(text(tx + 93, y + rh * 0.62, Fbits[i], size=13, bold=True, color=POS))

    # стрілка → SRAM
    p.append(arrow(tx + 118, ty + 4 * rh - 6, tx + 178, ty + 4 * rh - 6, color=FIELD, sw=2.0))

    # 8 комірок SRAM
    sx = tx + 196
    for i in range(8):
        y = ty + i * rh
        p.append(rect(sx, y, 40, rh - 3, fill=CELL, stroke=CELLB, sw=1.3, rx=4))
        p.append(text(sx + 20, y + rh * 0.62, Fbits[i], size=13, bold=True))
    p.append(text(sx + 20, ty - 10, "SRAM", size=12, color=MUTED, bold=True))

    # mux 8→1
    mx = sx + 150
    my0, my1 = ty, ty + 8 * rh
    cy = (my0 + my1) / 2
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' %
             (mx, my0, mx + 56, my0 + 60, mx + 56, my1 - 60, mx, my1, FILL, LINE))
    p.append(text(mx + 24, cy, "mux", size=13, color=MUTED, bold=True))
    p.append(text(mx + 24, cy + 18, "8→1", size=12, color=MUTED))
    for i in range(8):
        y = ty + i * rh + (rh - 3) / 2
        p.append(line(sx + 40, y, mx, y, color=LINE, sw=1.0))

    # вихід
    p.append(arrow(mx + 56, cy, mx + 120, cy, color=INK, sw=1.8))
    p.append(text(mx + 130, cy + 5, "F", size=15, bold=True, italic=True, color=POS, anchor="start"))

    # адреса A,B,C знизу: лінія від підпису до середини mux (керує вибором)
    p.append(text(mx + 28, H - 12, "адреса = A B C", size=12, color=NEG, bold=True))
    p.append(line(mx + 28, H - 26, mx + 28, cy + 30, color=NEG, sw=1.2, dash="4 3"))
    p.append(line(mx + 28, cy + 30, mx + 20, cy + 12, color=NEG, sw=1.2, dash="4 3"))

    render(os.path.join(OUT, "lut-is-memory.svg"), W, H, *p)


# ── double-exponential: n → 2ⁿ рядків → 2^(2ⁿ) функцій + таблиця стрибка ──────
# Ідея: дві сходинки степеня нанизуються; число функцій вибухає подвійною
# експонентою — наочно ланцюжком і таблицею малих n.

def fig_double_exponential():
    W, H = 720, 330
    p = []
    p.append(text(W / 2, 26, "Дві сходинки степеня: 2ⁿ рядків, 2^(2ⁿ) функцій", size=17, bold=True))

    # ланцюжок угорі: n  →  2ⁿ рядків  →  2^(2ⁿ) функцій
    cy = 80
    b1, w1, h1 = textbox(150, cy, "n входів", size=14, bold=True, fill=BG)
    p.append(b1)
    b2, w2, h2 = textbox(360, cy, "2ⁿ рядків\nтаблиці", size=13, fill=CELL, stroke=CELLB)
    p.append(b2)
    b3, w3, h3 = textbox(580, cy, "2^(2ⁿ)\nфункцій", size=13, fill="#eafaf0", stroke=FIELD)
    p.append(b3)
    p.append(arrow(150 + w1 / 2, cy, 360 - w2 / 2, cy, color=INK, sw=1.8))
    p.append(arrow(360 + w2 / 2, cy, 580 - w3 / 2, cy, color=INK, sw=1.8))

    # таблиця малих n знизу
    rows = [("1", "2", "4"), ("2", "4", "16"), ("3", "8", "256"),
            ("4", "16", "65 536"), ("5", "32", "≈ 4.3·10⁹"), ("6", "64", "≈ 1.8·10¹⁹")]
    tx, ty = 120, 150
    cw = [70, 110, 300]
    heads = ["n", "рядків 2ⁿ", "функцій 2^(2ⁿ)"]
    x = tx
    for j, hd in enumerate(heads):
        p.append(text(x + cw[j] / 2, ty, hd, size=13, bold=True, color=MUTED))
        x += cw[j]
    for i, row in enumerate(rows):
        y = ty + 18 + i * 24
        x = tx
        big = (i >= 3)
        for j, val in enumerate(row):
            col = FIELD if (j == 2 and big) else INK
            p.append(text(x + cw[j] / 2, y, val, size=13, bold=(j == 2),
                          color=col))
            x += cw[j]
    p.append(text(W / 2, ty + 18 + 6 * 24 + 16,
                  "кожен доданий вхід підносить число функцій до квадрата",
                  size=12, color=POS, italic=True))

    render(os.path.join(OUT, "double-exponential.svg"), W, H, *p)


# ── sweet-spot: ціна 2ⁿ росте, виграш насичується; зелена смуга 4–6 ───────────
# Ідея: дві криві на одній осі входів — ціна (2ⁿ, геометрична) і виграш
# (насичується); їхній розумний перетин — смуга 4–6 входів.

def fig_sweet_spot():
    import math
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 26, "Ціна 2ⁿ росте, виграш насичується — компроміс 4–6", size=17, bold=True))

    ox, oy = 80, 280
    aw, ah = 540, 210
    nmin, nmax = 2, 8

    def xof(n):
        return ox + (n - nmin) / (nmax - nmin) * aw

    # зелена смуга 4–6
    p.append(rect(xof(4), oy - ah, xof(6) - xof(4), ah, fill="#eafaf0",
                  stroke=FIELD, sw=1.0, rx=0))
    p.append(text((xof(4) + xof(6)) / 2, oy - ah - 8, "солодка точка", size=12,
                  color=FIELD, bold=True))

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "входи n", size=12, color=INK, italic=True))
    for n in range(nmin, nmax + 1):
        p.append(text(xof(n), oy + 20, str(n), size=12, color=INK))

    # крива ціни 2ⁿ (нормована в лог-вигляді, щоб помістилась і читалась)
    cost_pts = []
    for n in range(nmin, nmax + 1):
        # нормуємо 2ⁿ за максимумом 2^8, але через корінь — щоб крива не злипалась
        yv = oy - ah * (2 ** n / 2 ** nmax) ** 0.6
        cost_pts.append((xof(n), yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in cost_pts), POS))
    p.append(text(cost_pts[-1][0] - 4, cost_pts[-1][1] - 10, "ціна 2ⁿ", size=12,
                  color=POS, bold=True, anchor="end"))

    # крива виграшу (насичення)
    gain_pts = []
    for n in range(nmin, nmax + 1):
        g = 1 - math.exp(-(n - 1) * 0.7)
        gain_pts.append((xof(n), oy - ah * 0.9 * g))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in gain_pts), NEG))
    p.append(text(gain_pts[-1][0] - 4, gain_pts[-1][1] + 18, "виграш (насичується)",
                  size=12, color=NEG, bold=True, anchor="end"))

    render(os.path.join(OUT, "sweet-spot.svg"), W, H, *p)


if __name__ == "__main__":
    fig_truth_to_lut()
    fig_mux_tree()
    fig_any_function()
    fig_lut_vs_gates()
    fig_lut_size()
    # фігури математичної вставки
    fig_lut_is_memory()
    fig_double_exponential()
    fig_sweet_spot()
    print("figs.py: 8 SVG записано у", OUT)
