# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── shared-vs-matrix: одна спільна шина проти матриці ─────────────────────────
# Ідея: ліворуч три майстри тиснуться до одного арбітра/однієї шини — двоє чекають,
# хоча цілі різні. Праворуч матриця: рядки-майстри × стовпці-раби, три непересічні
# пари замкнено ОДНОЧАСНО — черги немає.

def fig_shared_vs_matrix():
    W, H = 760, 400
    p = []

    # ── ЛІВОРУЧ: спільна шина ──
    lx = 40
    p.append(text(lx + 150, 52, "Одна спільна шина", size=13, color=INK, bold=True))
    # три майстри
    ms = ["ядро", "DMA1", "DMA2"]
    mx = [lx + 40, lx + 150, lx + 260]
    for x, m in zip(mx, ms):
        p.append(rect(x - 40, 70, 80, 34, fill="#f4f6f8", stroke="#c8ccd0", sw=1.6, rx=6))
        p.append(text(x, 92, m, size=11, color=INK, bold=True))
    # спільна шина (одна лінія-брус)
    bus_y = 150
    p.append(rect(lx + 10, bus_y, 280, 26, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=4))
    p.append(text(lx + 150, bus_y + 17, "спільна шина (одна за раз)", size=10.5, color=NEG, bold=True))
    # від майстрів донизу до шини: один суцільний (пропущений), два пунктирні (чекають)
    p.append(arrow(mx[0], 104, mx[0], bus_y, color=POS, sw=2.2))
    p.append(line(mx[1], 104, mx[1], bus_y, color=MUTED, sw=1.4, dash="5 4"))
    p.append(line(mx[2], 104, mx[2], bus_y, color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(mx[1] + 4, 128, "чекає", size=9.5, color=MUTED, anchor="start", italic=True))
    # три раби внизу
    ss = ["флеш", "SRAM1", "SRAM2"]
    for x, s in zip(mx, ss):
        p.append(rect(x - 40, 232, 80, 34, fill="#f4f6f8", stroke="#c8ccd0", sw=1.6, rx=6))
        p.append(text(x, 254, s, size=11, color=INK))
    for x in mx:
        p.append(line(x, bus_y + 26, x, 232, color=MUTED, sw=1.2))
    p.append(text(lx + 150, 300, "цілі різні — а черга однаково є", size=11, color=POS, italic=True))

    # роздільник
    p.append(line(W / 2, 40, W / 2, H - 30, color="#d5d9dd", sw=1.2, dash="2 5"))

    # ── ПРАВОРУЧ: матриця ──
    rx = 410
    p.append(text(rx + 160, 52, "Матриця шин", size=13, color=INK, bold=True))
    # рядки-майстри зліва
    row_y = [92, 150, 208]
    mlab = ["ядро", "DMA1", "DMA2"]
    for y, m in zip(row_y, mlab):
        p.append(rect(rx, y - 16, 66, 32, fill="#f4f6f8", stroke="#c8ccd0", sw=1.6, rx=6))
        p.append(text(rx + 33, y + 4, m, size=10.5, color=INK, bold=True))
    # стовпці-раби зверху
    col_x = [rx + 130, rx + 210, rx + 290]
    slab = ["флеш", "SRAM1", "SRAM2"]
    for x, s in zip(col_x, slab):
        p.append(rect(x - 33, 66, 66, 26, fill="#f4f6f8", stroke="#c8ccd0", sw=1.6, rx=6))
        p.append(text(x, 83, s, size=10, color=INK))
    # ґратка ліній
    for y in row_y:
        p.append(line(rx + 66, y, col_x[-1] + 8, y, color="#dfe3e7", sw=1.2))
    for x in col_x:
        p.append(line(x, 92 + 0, x, row_y[-1] + 8, color="#dfe3e7", sw=1.2))
    # замкнені пари по діагоналі: ядро→флеш, DMA1→SRAM1, DMA2→SRAM2
    pairs = [(row_y[0], col_x[0]), (row_y[1], col_x[1]), (row_y[2], col_x[2])]
    for (y, x) in pairs:
        # активний шлях: рядок до перетину, тоді вниз у стовпець (зелений)
        p.append(line(rx + 66, y, x, y, color=FIELD, sw=2.6))
        p.append(line(x, y, x, 92, color=FIELD, sw=2.6))
        p.append(circle(x, y, 6, fill="#d4edda", stroke=FIELD, sw=2.2))
    p.append(text(rx + 160, 300, "три пари — три дороги ОДНОЧАСНО", size=11, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "shared-vs-matrix.svg"), W, H, *p,
           title="Спільна шина серіалізує всіх; матриця веде непересічні пари паралельно")


# ── crossbar-grid: ґратка зблизька + арбітр стовпця на суперництві ────────────
# Ідея: рядки M0..M2 × стовпці S0..S2, кружечки-комутатори на перетинах.
# Три непересічні пари замкнено зеленим. У стовпець S1 цілять ДВОЄ (M1 і M2),
# тож на вході саме S1 сидить арбітр — точкова серіалізація.

def fig_crossbar_grid():
    W, H = 720, 430
    p = []

    row_y = [130, 210, 290]
    col_x = [280, 420, 560]
    mlab = ["M0", "M1", "M2"]
    slab = ["S0\n(флеш)", "S1\n(SRAM1)", "S2\n(SRAM2)"]

    # підписи «майстри» / «раби»
    p.append(text(90, 92, "майстри", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(text(col_x[0] - 20, 62, "раби", size=11, color=MUTED, italic=True, anchor="start"))

    # рядки-майстри зліва
    for y, m in zip(row_y, mlab):
        p.append(rect(90, y - 18, 84, 36, fill="#f4f6f8", stroke="#c8ccd0", sw=1.7, rx=6))
        p.append(text(132, y + 5, m, size=13, color=INK, bold=True))

    # стовпці-раби зверху
    for x, s in zip(col_x, slab):
        p.append(rect(x - 38, 74, 76, 40, fill="#f4f6f8", stroke="#c8ccd0", sw=1.7, rx=6))
        p.append(mtext(x, 90, s.split("\n"), size=10, color=INK, bold=True))

    # ґратка (тонкі сірі лінії рядків і стовпців)
    for y in row_y:
        p.append(line(174, y, col_x[-1] + 30, y, color="#dfe3e7", sw=1.3))
    for x in col_x:
        p.append(line(x, 114, x, row_y[-1] + 30, color="#dfe3e7", sw=1.3))

    # усі перетини — кружечки-комутатори (сірі), активні — зелені
    active = {(0, 0), (1, 1), (2, 2)}          # замкнені пари по діагоналі
    contend = (2, 1)                            # M2 теж цілить у S1 — суперництво
    for r, y in enumerate(row_y):
        for c, x in enumerate(col_x):
            if (r, c) in active:
                # активний шлях: рядок → перетин → угору в стовпець
                p.append(line(174, y, x, y, color=FIELD, sw=2.8))
                p.append(line(x, y, x, 114, color=FIELD, sw=2.8))
                p.append(circle(x, y, 8, fill="#d4edda", stroke=FIELD, sw=2.4))
            elif (r, c) == contend:
                # другий запит у той самий стовпець S1 — червоний, у чергу
                p.append(line(174, y, x, y, color=POS, sw=2.0, dash="6 4"))
                p.append(circle(x, y, 8, fill="#fdecea", stroke=POS, sw=2.2))
            else:
                p.append(circle(x, y, 5, fill=BG, stroke="#c8ccd0", sw=1.3))

    # арбітр стовпця S1 — виносимо у вільне поле збоку, щоб не перетинати зелений
    # шлях; тонкий пунктирний повідець указує на точку суперництва (M2→S1)
    ax_arb, ay_arb = 500, 250
    p.append(line(ax_arb - 34, ay_arb + 6, 428, 285, color="#e0a800", sw=1.3, dash="3 3"))
    arb, aw, ah = textbox(ax_arb, ay_arb, "арбітр\nстовпця S1", size=9.5, bold=True,
                          fill="#fff9e6", stroke="#e0a800", sw=1.8, pad=8)
    p.append(arb)

    # позначки-виноски внизу
    ny = 360
    p.append(circle(150, ny, 7, fill="#d4edda", stroke=FIELD, sw=2.2))
    p.append(text(166, ny + 4, "замкнено — пара йде паралельно", size=11, color=INK, anchor="start"))
    p.append(circle(470, ny, 7, fill="#fdecea", stroke=POS, sw=2.2))
    p.append(text(486, ny + 4, "другий у той самий стовпець — у чергу", size=11, color=INK, anchor="start"))
    p.append(text(W / 2, ny + 34, "конкурують не за шину, а за ціль: арбітр — лише там, де двоє цілять в один стовпець",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "crossbar-grid.svg"), W, H, *p,
           title="Матриця зблизька: паралельні пари, арбітр лише на спільному стовпці")


# ── amba-timeline: шлях AMBA від однієї шини до матриці ───────────────────────
# Ідея: чотири віхи на часовій смузі. AMBA1 (1996) — дві спільні шини;
# AMBA2 (1999) — швидка, та досі спільна AHB; Multi-layer AHB (~2001) —
# перша матриця над старим протоколом; AMBA3 (2003) — AXI, кросбар штатний.
# Під кожною віхою — мініатюра топології: точка-серіалізація vs ґратка.

def fig_amba_timeline():
    W, H = 820, 400
    p = []

    # горизонтальна вісь часу
    axis_y = 120
    p.append(line(60, axis_y, W - 40, axis_y, color=MUTED, sw=2.0))
    p.append(arrow(W - 60, axis_y, W - 34, axis_y, color=MUTED, sw=2.0))
    p.append(text(W - 40, axis_y - 12, "час", size=10.5, color=MUTED, anchor="end", italic=True))

    # чотири віхи: x, рік, назва, чи спільна шина (False = матриця)
    marks = [
        (150, "1996", "AMBA 1",            "ASB + APB",        True),
        (330, "1999", "AMBA 2",            "AHB",              True),
        (510, "~2001", "Multi-layer AHB",  "матриця на AHB",   False),
        (690, "2003", "AMBA 3",            "AXI",              False),
    ]

    for (x, year, name, sub, shared) in marks:
        col = NEG if shared else FIELD
        # засічка на осі
        p.append(circle(x, axis_y, 6, fill=BG, stroke=col, sw=2.4))
        # рік над засічкою
        p.append(text(x, axis_y - 22, year, size=13, color=INK, bold=True))
        # назва редакції під засічкою
        p.append(text(x, axis_y + 30, name, size=11.5, color=INK, bold=True))
        p.append(text(x, axis_y + 47, sub, size=9.5, color=MUTED))

        # мініатюра топології нижче
        ty = axis_y + 90
        if shared:
            # спільна шина: три майстри → одна лінія → одна ціль (двоє чекають)
            for dx, act in [(-26, True), (0, False), (26, False)]:
                p.append(circle(x + dx, ty, 5, fill="#f4f6f8", stroke="#c8ccd0", sw=1.5))
                lc = POS if act else MUTED
                ld = None if act else "4 3"
                p.append(line(x + dx, ty + 5, x, ty + 34, color=lc, sw=1.8 if act else 1.2, dash=ld))
            p.append(rect(x - 34, ty + 34, 68, 14, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
            p.append(text(x, ty + 78, "одна дорога:", size=9, color=NEG, italic=True))
            p.append(text(x, ty + 91, "двоє чекають", size=9, color=NEG, italic=True))
        else:
            # матриця: ґратка 2×2, дві непересічні пари замкнено
            gx = [x - 18, x + 18]
            gy = [ty + 6, ty + 30]
            for yy in gy:
                p.append(line(gx[0] - 8, yy, gx[1] + 8, yy, color="#dfe3e7", sw=1.2))
            for xx in gx:
                p.append(line(xx, gy[0] - 8, xx, gy[1] + 8, color="#dfe3e7", sw=1.2))
            # замкнені перетини по діагоналі — зелені
            for (r, c) in [(0, 0), (1, 1)]:
                p.append(circle(gx[c], gy[r], 5, fill="#d4edda", stroke=FIELD, sw=2.2))
            for (r, c) in [(0, 1), (1, 0)]:
                p.append(circle(gx[c], gy[r], 3.5, fill=BG, stroke="#c8ccd0", sw=1.2))
            p.append(text(x, ty + 78, "ґратка доріг:", size=9, color=FIELD, italic=True))
            p.append(text(x, ty + 91, "пари паралельно", size=9, color=FIELD, italic=True))

    # підпис-місток унизу: де саме народжується матриця
    p.append(line(420, axis_y + 8, 420, axis_y + 60, color="#d5d9dd", sw=1.2, dash="2 5"))
    p.append(text(240, axis_y + 66, "одна дорога на всіх", size=10.5, color=NEG, italic=True, bold=True))
    p.append(text(600, axis_y + 66, "кожному — своя дорога", size=10.5, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "amba-timeline.svg"), W, H, *p,
           title="AMBA: від однієї спільної шини (1996) до матриці-кросбара (AXI, 2003)")


if __name__ == "__main__":
    fig_shared_vs_matrix()
    fig_crossbar_grid()
    fig_amba_timeline()
    print("OK: figures written to", OUT)
