# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED_F   = "#fdecea"   # заливка рухомого вузла
GRN_F   = "#eafaf0"   # заливка вузла на шляху / приклад
GRN_S   = FIELD


def tree_pos(i, left, top, width, vgap):
    """Координати центру вузла з індексом i у повному двійковому дереві."""
    L = (i + 1).bit_length() - 1          # рівень (0 — корінь)
    count = 1 << L                        # вузлів на рівні
    pos = (i + 1) - count                 # позиція в рівні
    x = left + (pos + 0.5) * width / count
    y = top + L * vgap
    return x, y


def node(cx, cy, val, r=22, fill=FILL, stroke=LINE, sw=1.6, tcol=INK, fs=16):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw) + \
        text(cx, cy + fs * 0.35, str(val), size=fs, color=tcol, bold=True)


def draw_tree(p, vals, left, top, width, vgap, r=22,
              red=frozenset(), green=frozenset(), swap_edges=frozenset(), up=False):
    """Малює дерево-купу: спершу ребра, потім вузли; ребра-обміни — зелені зі стрілкою."""
    pos = {i: tree_pos(i, left, top, width, vgap) for i in range(len(vals))}
    # звичайні ребра
    for i in range(1, len(vals)):
        par = (i - 1) // 2
        if (par, i) in swap_edges:
            continue
        p.append(line(pos[par][0], pos[par][1], pos[i][0], pos[i][1], color="#c8ccd2", sw=1.6))
    # ребра-обміни (зелені, зі стрілкою в бік руху)
    for (par, i) in swap_edges:
        a, b = pos[par], pos[i]
        # відступ від центрів вузлів, щоб стрілка не ховалась під колом
        import math
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        ax, ay = a[0] + ux * (r + 2), a[1] + uy * (r + 2)
        bx, by = b[0] - ux * (r + 2), b[1] - uy * (r + 2)
        if up:   # рух угору: стрілка від дитини до батька
            p.append(arrow(bx, by, ax, ay, color=GRN_S, sw=2.4))
        else:    # рух униз: стрілка від батька до дитини
            p.append(arrow(ax, ay, bx, by, color=GRN_S, sw=2.4))
    # вузли
    for i, v in enumerate(vals):
        cx, cy = pos[i]
        if i in red:
            p.append(node(cx, cy, v, r=r, fill=RED_F, stroke=POS, sw=2.2, tcol=POS))
        elif i in green:
            p.append(node(cx, cy, v, r=r, fill=GRN_F, stroke=GRN_S, sw=2.0))
        else:
            p.append(node(cx, cy, v, r=r))
    return pos


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — купа як дерево і як масив (одне сховище — два погляди)
# ─────────────────────────────────────────────────────────────────────────────
def fig_heap_array():
    W, H = 960, 520
    p = []
    vals = [1, 3, 6, 5, 9, 8, 7]
    ex = {2, 5, 6}   # приклад: вузол 2 та його діти 5, 6

    # ── дерево (ліворуч) ──
    p.append(text(250, 66, "Погляд-дерево", size=15, color=INK, bold=True))
    draw_tree(p, vals, left=40, top=110, width=420, vgap=118, r=25, green=ex)

    # роздільник
    p.append(line(500, 90, 500, H - 120, color="#d8dde3", sw=1.2, dash="4 5"))

    # ── масив (праворуч) ──
    p.append(text(730, 66, "Погляд-масив (те, що в пам'яті)", size=15, color=INK, bold=True))
    cw, ch = 52, 52
    x0, y0 = 530, 210
    for i, v in enumerate(vals):
        x = x0 + i * cw
        fill = GRN_F if i in ex else FILL
        stk = GRN_S if i in ex else LINE
        p.append(rect(x, y0, cw - 4, ch, fill=fill, stroke=stk, sw=1.6, rx=5))
        p.append(text(x + (cw - 4) / 2, y0 + ch / 2 + 6, str(v), size=17, color=INK, bold=True))
        p.append(text(x + (cw - 4) / 2, y0 + ch + 20, str(i), size=12, color=MUTED))
    p.append(text(x0 + 3.5 * cw, y0 + ch + 42, "індекс", size=11, color=MUTED))

    # формули
    box, bw, bh = textbox(730, 400, "діти вузла i:  2i+1  і  2i+2\nбатько вузла i:  (i−1) / 2",
                          size=15, pad=14, fill="#f8fafc", stroke=MUTED)
    p.append(box)
    p.append(text(730, 452, "приклад: вузол 2  →  діти 5 і 6", size=12.5, color=GRN_S, bold=True))

    render(os.path.join(OUT, "heap-array.svg"), W, H, *p,
           title="Купа: одне сховище — два погляди")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — вставка: просіювання вгору
# ─────────────────────────────────────────────────────────────────────────────
def fig_sift_up():
    W, H = 980, 560
    p = []
    # before: 2 щойно додано в кінець (індекс 7)
    a_vals = [1, 3, 6, 5, 9, 8, 7, 2]
    p.append(text(225, 70, "2 додали в кінець", size=14, color=INK, bold=True))
    draw_tree(p, a_vals, left=20, top=110, width=410, vgap=108, r=21,
              red={7}, swap_edges={(3, 7), (1, 3)}, up=True)
    p.append(text(225, H - 26, "2 підіймається:  2<5, потім 2<3, тоді 2≥1 — стоп",
                  size=12.5, color=MUTED))

    # стрілка-перехід
    p.append(arrow(455, 300, 525, 300, color=INK, sw=2.2))
    p.append(text(490, 284, "просіювання", size=12, color=INK, anchor="middle"))
    p.append(text(490, 322, "вгору", size=12, color=INK, anchor="middle"))

    # after
    b_vals = [1, 2, 6, 3, 9, 8, 7, 5]
    p.append(text(760, 70, "властивість купи відновлено", size=14, color=INK, bold=True))
    draw_tree(p, b_vals, left=555, top=110, width=410, vgap=108, r=21, red={1})
    p.append(text(760, H - 26, "2 стало на своє місце під коренем 1",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "sift-up.svg"), W, H, *p,
           title="Вставка: новий елемент спливає вгору")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — вилучення мінімуму: просіювання вниз
# ─────────────────────────────────────────────────────────────────────────────
def fig_sift_down():
    W, H = 980, 470
    p = []
    # before: корінь 1 забрано, на його місце — останній елемент 7
    a_vals = [7, 3, 6, 5, 9, 8]
    p.append(text(225, 66, "мінімум 1 віддано; у корінь — останній 7", size=13.5, color=INK, bold=True))
    draw_tree(p, a_vals, left=20, top=112, width=410, vgap=110, r=21,
              red={0}, swap_edges={(0, 1), (1, 3)}, up=False)
    p.append(text(225, H - 24, "7 тоне, обмінюючись із меншою дитиною:  7>3, потім 7>5",
                  size=12.5, color=MUTED))

    # стрілка-перехід
    p.append(arrow(455, 250, 525, 250, color=INK, sw=2.2))
    p.append(text(490, 234, "просіювання", size=12, color=INK, anchor="middle"))
    p.append(text(490, 272, "вниз", size=12, color=INK, anchor="middle"))

    # after
    b_vals = [3, 5, 6, 7, 9, 8]
    p.append(text(760, 66, "купа знову правильна", size=13.5, color=INK, bold=True))
    draw_tree(p, b_vals, left=555, top=112, width=410, vgap=110, r=21, red={3})
    p.append(text(760, H - 24, "новий мінімум 3 — у корені", size=12.5, color=MUTED))

    render(os.path.join(OUT, "sift-down.svg"), W, H, *p,
           title="Вилучення мінімуму: вершина занурюється вниз")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — хронологія родоводу купи (для історичної вставки)
# ─────────────────────────────────────────────────────────────────────────────
def fig_heap_timeline():
    W, H = 1280, 560
    p = []
    ymid = 300
    xs = [110, 375, 640, 905, 1170]

    # вісь
    p.append(line(70, ymid, 1210, ymid, color="#c8ccd2", sw=2.4))

    # (рядки, чи «народження купи» — виділити, вгору/вниз)
    items = [
        (["1962 · Флойд", "Алг. 113 «Treesort»", "сортування деревом"], False, True),
        (["1964 черв. · Вільямс", "Алг. 232 «Heapsort»", "двійкова купа в масиві"], True, False),
        (["1964 груд. · Флойд", "Алг. 245 «Treesort 3»", "побудова за O(n)"], True, True),
        (["1978 · Вюємен", "біноміальна купа", "швидке злиття куп"], False, False),
        (["1984/87 · Фредман, Тарян", "фібоначчієва купа", "зменш. ключа за O(1)"], False, True),
    ]

    # спершу конектори (за вузлами)
    for x, (lines, hot, above) in zip(xs, items):
        if above:
            p.append(line(x, ymid - 10, x, 215, color="#d8dde3", sw=1.4))
        else:
            p.append(line(x, ymid + 10, x, 385, color="#d8dde3", sw=1.4))

    # точки на осі
    for x, (lines, hot, above) in zip(xs, items):
        p.append(circle(x, ymid, 9, fill=(FIELD if hot else MUTED),
                        stroke=BG, sw=2.5))

    # рамки-віхи
    for x, (lines, hot, above) in zip(xs, items):
        cy = 180 if above else 420
        fill = GRN_F if hot else FILL
        stroke = GRN_S if hot else MUTED
        box, bw, bh = textbox(x, cy, "\n".join(lines), size=13, pad=12,
                              fill=fill, stroke=stroke, min_w=196)
        p.append(box)

    render(os.path.join(OUT, "heap-timeline.svg"), W, H, *p,
           title="Родовід купи: 1962 — 1987")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 5 — дві побудови купи: згори (Вільямс) і знизу (Флойд)
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_builds():
    W, H = 1060, 560
    p = []
    vals = [1, 3, 6, 5, 9, 8, 7]

    # роздільник
    p.append(line(530, 74, 530, 500, color="#d8dde3", sw=1.2, dash="4 5"))

    # ── ліворуч: Вільямс, згори (вставками) ──
    p.append(text(270, 58, "Вільямс: купа росте вставками", size=15, color=INK, bold=True))
    draw_tree(p, vals, left=70, top=112, width=400, vgap=95, r=19,
              red={6}, swap_edges={(0, 2), (2, 6)}, up=True)
    p.append(text(270, 356, "повторюємо для кожного з n елементів", size=12.5, color=MUTED))
    p.append(text(270, 412, "O(n log n)", size=27, color=POS, bold=True))
    p.append(text(270, 446, "n · O(log n)", size=13, color=MUTED))

    # ── праворуч: Флойд, знизу (просіюванням) ──
    p.append(text(790, 58, "Флойд: купа складається знизу", size=15, color=INK, bold=True))
    draw_tree(p, vals, left=590, top=112, width=400, vgap=95, r=19,
              green={3, 4, 5, 6}, swap_edges={(0, 1), (2, 5)}, up=False)
    p.append(text(790, 356, "листки (½ вузлів) не рухаються", size=12.5, color=MUTED))
    p.append(text(790, 412, "O(n)", size=27, color=GRN_S, bold=True))
    p.append(text(790, 446, "сума роботи збігається", size=13, color=MUTED))

    render(os.path.join(OUT, "two-builds.svg"), W, H, *p,
           title="Дві побудови купи: згори (Вільямс) і знизу (Флойд)")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 6 (math) — рівні, кількість 2^L, індексна арифметика і висота ⌊log₂ n⌋
# ─────────────────────────────────────────────────────────────────────────────
def fig_heap_levels():
    W, H = 1240, 660
    p = []
    vals = list(range(15))                 # індекси 0..14 як підписи вузлів
    left, top, width, vgap, r = 90, 120, 980, 128, 17
    draw_tree(p, vals, left=left, top=top, width=width, vgap=vgap, r=r,
              green={3}, red={7, 8})

    # праворуч — по рядку на рівень: 2^L вузлів і перший індекс 2^L−1
    info = ["1 вузол · поч. 0", "2 вузли · поч. 1",
            "4 вузли · поч. 3", "8 вузлів · поч. 7"]
    for L in range(4):
        y = top + L * vgap
        p.append(text(40, y + 5, "L=%d" % L, size=14, color=MUTED, bold=True))
        p.append(text(1120, y + 5, info[L], size=13.5, color=INK, anchor="start"))

    # нижні пояснювальні рамки
    b1, w1, h1 = textbox(300, 592, "перший індекс рівня L  =  2ᴸ − 1\n0, 1, 3, 7, 15, …",
                         size=14, pad=13, fill="#f8fafc", stroke=MUTED)
    p.append(b1)
    b2, w2, h2 = textbox(720, 592, "діти вузла i:  2i+1  і  2i+2\nнапр. вузол 3 → діти 7 і 8",
                         size=14, pad=13, fill=GRN_F, stroke=GRN_S, color=INK)
    p.append(b2)
    p.append(mtext(1070, 578, ["висота дерева", "= ⌊log₂ n⌋ = 3", "(для n = 15)"],
                   size=13, color=POS, bold=True))

    render(os.path.join(OUT, "heap-levels.svg"), W, H, *p,
           title="Рівні купи: 2ᴸ вузлів, індекс 2ᴸ−1 і висота ⌊log₂ n⌋")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 7 (math) — вартість побудови = зважена сума h·N_h, що збігається до O(n)
# ─────────────────────────────────────────────────────────────────────────────
def fig_heap_build_cost():
    W, H = 1200, 600
    p = []
    # ── ліворуч: дерево, вузли підписані ВИСОТОЮ; листки дешеві (зел.), корінь дорогий (черв.)
    heights = [3, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    draw_tree(p, heights, left=30, top=110, width=520, vgap=118, r=16,
              green=set(range(7, 15)), red={0})
    p.append(text(290, 78, "вузол підписано його висотою h", size=13.5, color=INK, bold=True))
    p.append(text(290, H - 40, "листків (h=0) — половина, коштують 0;", size=12.5, color=FIELD, bold=True))
    p.append(text(290, H - 22, "дорогий вузол угорі один", size=12.5, color=POS, bold=True))

    # роздільник
    p.append(line(600, 70, 600, H - 60, color="#d8dde3", sw=1.2, dash="4 5"))

    # ── праворуч: смужки роботи h·N_h за висотами (n=15)
    p.append(text(900, 78, "робота = ∑ h·N_h  (для n = 15)", size=14, color=INK, bold=True))
    rows = [(3, 1, 3), (2, 2, 4), (1, 4, 4), (0, 8, 0)]   # (h, N_h, робота)
    x0 = 720
    ytop = 135
    scale = 42
    for k, (h, N, work) in enumerate(rows):
        y = ytop + k * 62
        p.append(text(700, y + 5, "h=%d" % h, size=13.5, color=INK, bold=True, anchor="end"))
        col = POS if h == 3 else (FIELD if h == 0 else INK)
        bw = max(work * scale, 3)
        p.append(rect(x0, y - 13, bw, 26, fill="#eef1f4", stroke=col, sw=1.8, rx=4))
        p.append(text(x0 + bw + 12, y + 5, "%d вузл.·%d = %d" % (N, h, work),
                      size=12.5, color=INK, anchor="start"))

    # підсумки
    b, bw2, bh2 = textbox(895, 470,
                          "сума висот = 8·0+4·1+2·2+1·3 = 11  (менше за n)\n"
                          "груба межа  2n = 30\n"
                          "наївно  ≈ n·log₂n ≈ 58",
                          size=13.5, pad=14, fill="#f8fafc", stroke=MUTED)
    p.append(b)
    p.append(text(895, 545, "ряд ∑ h/2ʰ = 2 збігається → уся сума лінійна",
                  size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, "heap-build-cost.svg"), W, H, *p,
           title="Побудова за O(n): дорогих вузлів мало, ряд збігається")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 8 (math) — скільки порядку тримає структура і скільки коштує побудова
# ─────────────────────────────────────────────────────────────────────────────
def fig_heap_order_spectrum():
    W, H = 1160, 560
    p = []
    cx = [200, 580, 950]
    titles = ["Відсортований масив", "Збалансоване BST", "Купа (min)"]
    for x in cx[1:]:
        p.append(line(x - 190, 70, x - 190, H - 90, color="#d8dde3", sw=1.2, dash="4 5"))
    for i, t in enumerate(titles):
        p.append(text(cx[i], 66, t, size=15, color=INK, bold=True))

    # ── колонка 1: відсортований ланцюг (повний порядок) ──
    xs = cx[0]
    cw, ch = 46, 34
    y = 108
    for k, v in enumerate([1, 2, 3, 4, 5]):
        yy = y + k * (ch + 14)
        p.append(rect(xs - cw / 2, yy, cw, ch, fill=GRN_F, stroke=GRN_S, sw=1.6, rx=5))
        p.append(text(xs, yy + ch / 2 + 6, str(v), size=15, color=INK, bold=True))
        if k < 4:
            p.append(text(xs, yy + ch + 8, "≤", size=13, color=MUTED))

    # ── колонка 2: збалансоване BST (повний порядок; обхід дає 1..7) ──
    draw_tree(p, [4, 2, 6, 1, 3, 5, 7], left=cx[1] - 175, top=118, width=350, vgap=80, r=15)

    # ── колонка 3: купа (лише мінімум угорі; сусіди не впорядковані) ──
    draw_tree(p, [1, 3, 2, 8, 5, 9, 7], left=cx[2] - 175, top=118, width=350, vgap=80, r=15,
              red={0})
    p.append(text(cx[2], 306, "сусіди 3 і 2 — не впорядковані", size=12, color=MUTED))

    # ── рядки «гарантує» / «побудова» ──
    guar = ["повний порядок", "повний порядок", "лише мінімум угорі"]
    build = ["O(n log n)", "O(n log n)", "O(n)"]
    for i in range(3):
        p.append(text(cx[i], 378, "гарантує:", size=12.5, color=MUTED))
        p.append(text(cx[i], 398, guar[i], size=13.5, color=INK, bold=True))
        p.append(text(cx[i], 430, "побудова:", size=12.5, color=MUTED))
        col = FIELD if build[i] == "O(n)" else POS
        p.append(text(cx[i], 450, build[i], size=15, color=col, bold=True))

    # ── підсумкова рамка ──
    p.append(fitbox(120, 488, W - 240, 46,
                    "Менше порядку — дешевша побудова.  Межа Ω(n log n) живе у витяганні, не в побудові.",
                    size=15, pad=12, fill="#f8fafc", stroke=MUTED, bold=True))

    render(os.path.join(OUT, "heap-order-spectrum.svg"), W, H, *p,
           title="Скільки порядку тримає структура — стільки коштує побудова")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 9 (proj) — decrease-key і карта позицій (купа й карта — дзеркальні)
# ─────────────────────────────────────────────────────────────────────────────
def _kv_node(cx, cy, idl, kv, red=False, path=False):
    if red:
        fill, stroke, tc = RED_F, POS, POS
    elif path:
        fill, stroke, tc = GRN_F, GRN_S, INK
    else:
        fill, stroke, tc = FILL, LINE, INK
    s = circle(cx, cy, 27, fill=fill, stroke=stroke, sw=2.2 if (red or path) else 1.6)
    s += text(cx, cy - 3, idl, size=15, color=tc, bold=True)
    s += text(cx, cy + 14, kv, size=11, color=MUTED)
    return s


def fig_decrease_key_map():
    import math
    W, H = 1000, 560
    p = []
    labels = [("A", "2"), ("B", "5"), ("C", "4"), ("D", "8"),
              ("E", "9→1"), ("F", "7"), ("G", "6")]
    posc = {i: tree_pos(i, 40, 120, 470, 124) for i in range(7)}
    swap_edges = {(0, 1), (1, 4)}   # шлях E(4) -> B(1) -> A(0)

    p.append(text(275, 84, "знижуємо ключ E:  9 → 1", size=14, color=INK, bold=True))

    # ребра
    for i in range(1, 7):
        par = (i - 1) // 2
        a, b = posc[par], posc[i]
        if (par, i) in swap_edges:
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = math.hypot(dx, dy)
            ux, uy = dx / d, dy / d
            ax, ay = a[0] + ux * 29, a[1] + uy * 29
            bx, by = b[0] - ux * 29, b[1] - uy * 29
            p.append(arrow(bx, by, ax, ay, color=GRN_S, sw=2.4))  # угору: дитина→батько
        else:
            p.append(line(a[0], a[1], b[0], b[1], color="#c8ccd2", sw=1.6))
    # вузли
    for i, (idl, kv) in enumerate(labels):
        cx, cy = posc[i]
        p.append(_kv_node(cx, cy, idl, "k=" + kv, red=(i == 4), path=(i in {0, 1})))

    p.append(text(275, 478, "E спливає вздовж однієї гілки повз B до кореня",
                  size=12.5, color=MUTED))

    # роздільник
    p.append(line(650, 96, 650, 500, color="#e2e6ea", sw=1.1, dash="4 5"))

    # карта позицій (праворуч)
    tx, ty, rh = 688, 118, 43
    cw_id, cw_ix = 66, 172
    tw = cw_id + cw_ix
    p.append(text(tx + tw / 2, ty - 12, "карта позицій після просіювання",
                  size=12.5, color=MUTED, bold=True))
    p.append(rect(tx, ty, tw, rh, fill="#eef1f5", stroke=LINE, sw=1.4))
    p.append(text(tx + cw_id / 2, ty + rh / 2 + 5, "id", size=13, color=INK, bold=True))
    p.append(text(tx + cw_id + cw_ix / 2, ty + rh / 2 + 5, "індекс у h",
                  size=13, color=INK, bold=True))

    rows = [("A", "1", "було 0", True), ("B", "4", "було 1", True),
            ("C", "2", "", False), ("D", "3", "", False),
            ("E", "0", "було 4", True), ("F", "5", "", False), ("G", "6", "", False)]
    for k, (idl, ix, old, ch) in enumerate(rows):
        ry = ty + (k + 1) * rh
        fill = RED_F if ch else BG
        stroke = POS if ch else "#c8ccd2"
        p.append(rect(tx, ry, tw, rh, fill=fill, stroke=stroke, sw=1.8 if ch else 1.1))
        p.append(text(tx + cw_id / 2, ry + rh / 2 + 5, idl, size=14,
                      color=POS if ch else INK, bold=True))
        label = ix if not old else "%s   (%s)" % (ix, old)
        p.append(text(tx + cw_id + cw_ix / 2, ry + rh / 2 + 5, label, size=13, color=INK))
    p.append(line(tx + cw_id, ty, tx + cw_id, ty + 8 * rh, color="#c8ccd2", sw=1.0))
    p.append(text(tx + tw / 2, ty + 8 * rh + 24, "червоне — рядки, оновлені під час обмінів",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "decrease-key-map.svg"), W, H, *p,
           title="decrease-key: купа й карта позицій лишаються дзеркальними")


if __name__ == "__main__":
    fig_heap_array()
    fig_sift_up()
    fig_sift_down()
    fig_heap_timeline()
    fig_two_builds()
    fig_heap_levels()
    fig_heap_build_cost()
    fig_heap_order_spectrum()
    fig_decrease_key_map()
    print("OK: heap-array, sift-up, sift-down, heap-timeline, two-builds, "
          "heap-levels, heap-build-cost, heap-order-spectrum, decrease-key-map")
