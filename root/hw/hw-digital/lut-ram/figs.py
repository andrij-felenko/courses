# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CELL  = "#eef4ff"     # заливка комірки пам'яті
CELLB = "#c9d6f0"     # її обведення
HOT   = "#fdecea"     # підсвітка обраного / записаного
WEG   = "#eafaf0"     # зелена підсвітка «пам'ять»


# ── two-lives: ті самі SRAM-комірки LUT — застиглий конфіг АБО жива пам'ять ────
# Ідея: біти, що в логіці заливаються раз бітстрімом і застигають, у режимі
# пам'яті дістають ДРУГИЙ порт — тактовий запис під час роботи. Схема стала,
# додається лише шлях «записати комірку».

def fig_two_lives():
    W, H = 760, 372
    p = [text(W / 2, 26, "Ті самі комірки — два життя", size=17, bold=True)]

    def bank(x0, y0, label, sub, subcol, frozen):
        cells = []
        vals = ["0", "1", "1", "0"]
        for i, v in enumerate(vals):
            cy = y0 + i * 34
            fill = CELL if frozen else WEG
            cells.append(rect(x0, cy, 34, 30, fill=fill, stroke=CELLB, sw=1.5, rx=4))
            cells.append(text(x0 + 17, cy + 20, v, size=15, bold=True))
        # заголовок банку
        cells.insert(0, text(x0 + 17, y0 - 12, label, size=13, bold=True))
        cells.append(text(x0 + 17, y0 + 4 * 34 + 14, sub, size=12, color=subcol, italic=True))
        return "".join(cells)

    # ліворуч — застиглий конфіг
    lx = 120
    p.append(bank(lx, 90, "логіка", "залив і застиг", MUTED, True))
    # стрілка «бітстрім» згори, один раз
    p.append(arrow(lx + 17, 58, lx + 17, 84, color=MUTED))
    fb, _, _ = textbox(lx + 17, 46, "бітстрім\n(раз)", size=11, color=MUTED, stroke=MUTED,
                       fill="#ffffff", pad=6)
    p.append(fb)

    # праворуч — жива пам'ять
    rx = 470
    p.append(bank(rx, 90, "пам'ять", "пиши під час роботи", FIELD, False))
    # додатковий порт запису: WCLK + WE + адреса запису → у банк
    p.append(arrow(rx - 60, 118, rx - 4, 118, color=FIELD, sw=2))
    p.append(arrow(rx - 60, 152, rx - 4, 152, color=FIELD, sw=2))
    p.append(arrow(rx - 60, 186, rx - 4, 186, color=FIELD, sw=2))
    wb, _, _ = textbox(rx - 118, 152, "порт\nзапису\nWCLK · WE\nадреса", size=11,
                       color=FIELD, stroke=FIELD, fill=WEG, pad=7)
    p.append(wb)

    # спільний вихід читання (той самий мультиплексорний вихід у обох)
    for cx in (lx, rx):
        p.append(arrow(cx + 34, 90 + 3 * 34 + 15, cx + 74, 90 + 3 * 34 + 15, color=INK))
    p.append(text(lx + 96, 90 + 3 * 34 + 19, "→ читання", size=11, color=INK, anchor="start"))
    p.append(text(rx + 96, 90 + 3 * 34 + 19, "→ читання", size=11, color=INK, anchor="start"))

    # порівняльна плашка знизу
    cap, cw, _ = textbox(W / 2, 344,
        "Ліворуч комірки застигли після заливки бітстрімом; праворуч у ті самі комірки\nдодано порт запису — і вони стали живою пам'яттю, яку пишуть під час роботи.",
        size=12, color=INK, fill="#ffffff", stroke=MUTED, pad=8)
    p.append(cap)
    render(os.path.join(OUT, "two-lives.svg"), W, H, *p)


# ── distram-timing: розподілена пам'ять — читання асинхронне, запис тактовий ───
# Ідея: адреса читання одразу тягне біт через те саме дерево мультиплексорів
# (жодного такту), а запис відбувається лише у мить фронту WCLK при WE=1.

def fig_distram_timing():
    W, H = 760, 372
    p = [text(W / 2, 26, "Розподілена пам'ять: читання одразу, запис по фронту", size=17, bold=True)]

    left = 80
    # верх: асинхронне читання
    yR = 78
    p.append(text(left + 300, yR - 34, "жодного такту — комбінаційно, як звичайна LUT",
                  size=12, color=FIELD, italic=True))
    ab, _, _ = textbox(left + 45, yR, "адреса\nчитання", size=12, stroke=INK, pad=7)
    p.append(ab)
    p.append(arrow(left + 108, yR, left + 300, yR, color=INK, sw=2))
    mb, mw, _ = textbox(left + 360, yR, "дерево\nмультиплексорів", size=12, fill=CELL,
                        stroke=CELLB, pad=8)
    p.append(mb)
    p.append(arrow(left + 360 + mw / 2, yR, left + 610, yR, color=INK, sw=2))
    ob, _, _ = textbox(left + 648, yR, "біт\nвиходу", size=12, fill=HOT, stroke=POS, pad=7)
    p.append(ob)

    # роздільник
    p.append(line(40, 132, W - 40, 132, color="#e5e7eb", sw=1.2))

    # низ: синхронний запис — часова діаграма WCLK/WE
    p.append(text(left - 10, 158, "запис — лише в мить фронту WCLK, коли WE=1:",
                  size=12, color=INK, anchor="start"))
    # WE лінія (умовно високий увесь час у прикладі) — над WCLK
    yWE = 184
    xend = left + 40 + 26 + 40 + 26 + 60
    p.append(line(left, yWE, xend, yWE, color=FIELD, sw=2.4))
    p.append(text(left - 8, yWE + 4, "WE=1", size=11, color=FIELD, anchor="end"))
    # WCLK: два імпульси
    base = 250
    top = 208
    seq = [(40, 0), (26, 1), (40, 0), (26, 1), (60, 0)]
    xs = left
    path_pts = []
    for w_, lvl in seq:
        yv = top if lvl else base
        path_pts.append((xs, yv))
        xs += w_
        path_pts.append((xs, yv))
    d = []
    prev = None
    for (px, py) in path_pts:
        if prev is not None and prev[1] != py:
            d.append(line(prev[0], prev[1], prev[0], py, color=NEG, sw=2))
        if prev is not None:
            d.append(line(prev[0], prev[1], px, py, color=NEG, sw=2))
        prev = (px, py)
    p.append("".join(d))
    p.append(text(left - 8, (top + base) / 2 + 4, "WCLK", size=11, color=NEG, anchor="end"))

    # позначити два фронти вгору стрілочками «запис тут»
    f1 = left + 40
    f2 = left + 40 + 26 + 40
    for fx in (f1, f2):
        p.append(arrow(fx, base + 34, fx, base + 6, color=POS, sw=2))
        p.append(text(fx, base + 50, "запис", size=11, color=POS))

    cap, cw, _ = textbox(W / 2, H - 24,
        "Читаєш — бачиш біт тієї ж миті (асинхронно). Пишеш — тільки на фронті WCLK за WE=1.",
        size=12, fill="#ffffff", stroke=MUTED, pad=8)
    p.append(cap)
    render(os.path.join(OUT, "distram-timing.svg"), W, H, *p)


# ── srl-chain: ті самі комірки як зсувний ланцюг; адреса = рухомий відвід ──────
# Ідея: замкнувши комірки в ланцюг «вихід→вхід», дістаємо SRL: біт заходить із
# D, крокує по такту, а адреса A обирає, з якої комірки взяти вихід — тобто
# задає ДОВЖИНУ затримки без жодного окремого тригера.

def fig_srl_chain():
    W, H = 760, 320
    p = [text(W / 2, 26, "Ті самі комірки як зсувний ланцюг (SRL)", size=17, bold=True)]

    n = 6
    x0, y0 = 70, 120
    cw, gap = 78, 24
    labels = ["x[n]", "x[n−1]", "x[n−2]", "x[n−3]", "x[n−4]", "x[n−5]"]
    tapsel = 3  # обрана адреса → відвід 3

    xs = []
    for i in range(n):
        cx = x0 + i * (cw + gap)
        xs.append(cx)
        fill = HOT if i == tapsel else CELL
        p.append(rect(cx, y0, cw, 46, fill=fill, stroke=CELLB, sw=1.6, rx=6))
        p.append(text(cx + cw / 2, y0 + 20, "R%d" % i, size=12, color=MUTED))
        p.append(text(cx + cw / 2, y0 + 38, labels[i], size=12, bold=True))
        if i < n - 1:
            p.append(arrow(cx + cw, y0 + 23, cx + cw + gap, y0 + 23, color=INK, sw=1.8))

    # вхід D зліва
    p.append(arrow(x0 - 44, y0 + 23, x0, y0 + 23, color=FIELD, sw=2.2))
    p.append(text(x0 - 46, y0 + 12, "D", size=13, color=FIELD, anchor="end", bold=True))
    p.append(text(x0 - 46, y0 + 40, "новий\nвідлік", size=10, color=FIELD, anchor="end"))

    # спільний такт знизу
    yc = y0 + 88
    p.append(line(x0, yc, xs[-1] + cw, yc, color=NEG, sw=2))
    for cx in xs:
        p.append(line(cx + cw / 2, yc, cx + cw / 2, y0 + 46, color=NEG, sw=1.2, dash="3,3"))
    p.append(text(x0 - 8, yc + 4, "такт", size=11, color=NEG, anchor="end"))
    p.append(text((x0 + xs[-1] + cw) / 2, yc + 20,
                  "один фронт → усі крокують на щабель", size=11, color=NEG, italic=True))

    # адреса-відвід згори
    ya = y0 - 40
    tcx = xs[tapsel] + cw / 2
    p.append(arrow(tcx, ya + 8, tcx, y0 - 2, color=POS, sw=2.2))
    ab, aw, _ = textbox(tcx, ya, "адреса A=3 → вихід звідси", size=12, color=POS,
                        fill=HOT, stroke=POS, pad=7)
    p.append(ab)

    cap, capw, _ = textbox(W / 2, H - 16,
        "Біт заходить із D і крокує по такту; адреса A обирає відвід —\nтобто задає довжину затримки без жодного окремого тригера.",
        size=12, fill="#ffffff", stroke=MUTED, pad=8)
    p.append(cap)
    render(os.path.join(OUT, "srl-chain.svg"), W, H, *p)


# ── selectram-timeline: три прозріння інженерів Xilinx у часі ─────────────────
# Ідея (для hist-вставки): застиглі SRAM-комірки LUT поступово оживали.
# 1991 — XC4000: LUT як 16×2 / 32×1 біт SelectRAM (рівнева, асинхронна).
# 1998–2000 — Virtex/Spartan-II: 4-входова LUT → SRL16 (1..16 щаблів зсуву).
# 2006 — Virtex-5/Spartan-6: 6-входова LUT → SRL32 (1..32 щаблі).

def fig_selectram_timeline():
    W, H = 780, 336
    p = [text(W / 2, 26, "Як застиглі комірки LUT оживали: три кроки Xilinx", size=17, bold=True)]

    # горизонтальна вісь часу
    axy = 150
    x0, x1 = 70, W - 60
    p.append(line(x0, axy, x1, axy, color=MUTED, sw=2))
    p.append(arrow(x1 - 2, axy, x1 + 2, axy, color=MUTED, sw=2))
    p.append(text(x1 + 6, axy + 4, "час", size=11, color=MUTED, anchor="start"))

    # три віхи: (частка осі, рік, заголовок, опис, «вгору/вниз»)
    marks = [
        (0.12, "1991", "XC4000 · SelectRAM",
         "LUT як 16×2 / 32×1 біт\nрозподілене ОЗП\n(рівневе, асинхронне)", True),
        (0.50, "1998–2000", "Virtex / Spartan-II · SRL16",
         "4-входова LUT →\nзсув 1..16 щаблів\nбез окремих тригерів", False),
        (0.85, "2006", "Virtex-5 / Spartan-6 · SRL32",
         "6-входова LUT →\nзсув 1..32 щаблі\n(SRLC32E)", True),
    ]
    for frac, year, title_, desc, up in marks:
        mx = x0 + (x1 - x0 - 10) * frac
        p.append(circle(mx, axy, 7, fill=HOT, stroke=POS, sw=2.4))
        p.append(text(mx, axy + (28 if not up else -14), year, size=13, bold=True, color=POS))
        if up:
            bx, by = mx, axy - 74
        else:
            bx, by = mx, axy + 92
        box, bw, bh = textbox(bx, by, desc, size=11, fill=CELL, stroke=CELLB, pad=8)
        # заголовок над/під рамкою
        ty = by - bh / 2 - 8 if up else by - bh / 2 - 8
        p.append(text(bx, ty, title_, size=12, bold=True, color=FIELD))
        p.append(box)
        # тонка з'єднувальна лінія від віхи до рамки
        p.append(line(mx, axy + (-7 if up else 7),
                      bx, by + (bh / 2 if up else -bh / 2), color=MUTED, sw=1, dash="3,3"))

    render(os.path.join(OUT, "selectram-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_lives()
    fig_distram_timing()
    fig_srl_chain()
    fig_selectram_timeline()
    print("figs written to", OUT)
