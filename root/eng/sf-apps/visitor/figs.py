# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREY_F = "#eef1f4"
GREY_S = "#c2c8d0"
BLUE_F = "#eaf0fd"
GREEN_F = "#e8f6ee"
RED_F = "#fdecea"


# ── Подвійна диспетчеризація: два віртуальні виклики поспіль ──────────────────
def fig_double_dispatch():
    W, H = 1180, 620
    frags = []
    frags.append(text(W / 2, 36, "Подвійна диспетчеризація: вибір за двома типами",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 60, "один віртуальний виклик обирає за одним типом — тут потрібні два",
                      size=12.5, color=MUTED))

    y_row = 235
    # ── Клієнт (ліворуч) ─────────────────────────────────────────────────────
    cx_c = 150
    cb, wc, hc = textbox(cx_c, y_row, ["клієнт кличе", "s.accept(v)"],
                         size=13, bold=True, fill=FILL, stroke=LINE, sw=1.8, min_w=190)
    frags.append(cb)
    frags.append(text(cx_c, y_row + hc / 2 + 20, "s: Shape — підтип ?", size=11, color=MUTED))
    frags.append(text(cx_c, y_row + hc / 2 + 36, "v: Visitor — підтип ?", size=11, color=MUTED))

    # ── Обраний елемент: Circle.accept (центр) ───────────────────────────────
    cx_a = 560
    ab, wa, ha = textbox(cx_a, y_row, ["Circle.accept(v)", "→ v.visitCircle(this)"],
                         size=12.5, bold=False, fill=BLUE_F, stroke=NEG, sw=2.2, min_w=270)
    frags.append(ab)
    frags.append(text(cx_a, y_row - ha / 2 - 12, "обрано за типом фігури",
                      size=11.5, bold=True, color=NEG))

    # необроані гілки accept (сірі, нижче)
    for name, iy in [("Rectangle.accept(v)", 360), ("Triangle.accept(v)", 470)]:
        gb, gw, gh = textbox(cx_a, iy, [name, "…"], size=12, bold=False,
                             fill=GREY_F, stroke=GREY_S, sw=1.4, min_w=270, color=MUTED)
        frags.append(gb)
    frags.append(text(cx_a, 520, "інші гілки accept — не обрані цим викликом",
                      size=11, color=MUTED))

    # ── Обраний відвідувач: AreaVisitor.visitCircle (праворуч) ────────────────
    cx_v = 945
    vb, wv, hv = textbox(cx_v, y_row, ["AreaVisitor", "visitCircle(c):", "return π · c.r²"],
                         size=12.5, bold=False, fill=GREEN_F, stroke=FIELD, sw=2.2, min_w=260)
    frags.append(vb)
    frags.append(text(cx_v, y_row - hv / 2 - 12, "обрано за типом візитора",
                      size=11.5, bold=True, color=FIELD))

    # необроана операція (сіра)
    sgb, sgw, sgh = textbox(cx_v, 400, ["SvgVisitor", "visitCircle(c):", "return <circle…>"],
                            size=12, bold=False, fill=GREY_F, stroke=GREY_S, sw=1.4,
                            min_w=260, color=MUTED)
    frags.append(sgb)
    frags.append(text(cx_v, 400 + sgh / 2 + 18, "інша операція — не обрана", size=11, color=MUTED))

    # ── Дві стрілки-стрибки вздовж обраного шляху ────────────────────────────
    a1x1 = cx_c + wc / 2 + 6
    a1x2 = cx_a - wa / 2 - 6
    frags.append(arrow(a1x1, y_row, a1x2, y_row, color=INK, sw=2.0))
    mid1 = (a1x1 + a1x2) / 2
    frags.append(text(mid1, 190, "① за типом ФІГУРИ", size=11.5, bold=True, color=INK))
    frags.append(text(mid1, 206, "(accept — віртуальний)", size=10.5, color=MUTED))

    a2x1 = cx_a + wa / 2 + 6
    a2x2 = cx_v - wv / 2 - 6
    frags.append(arrow(a2x1, y_row, a2x2, y_row, color=INK, sw=2.0))
    mid2 = (a2x1 + a2x2) / 2
    frags.append(text(mid2, 190, "② тип ВІЗИТОРА", size=11.5, bold=True, color=INK))
    frags.append(text(mid2, 206, "(visit — віртуальний)", size=10.5, color=MUTED))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, H - 58, W - 40, H - 58, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 32,
                      "два віртуальні виклики поспіль обрали метод за ДВОМА типами — це подвійна диспетчеризація",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'visitor-double-dispatch.svg'), W, H, *frags)


# ── Сітка операцій×типів: стовпець дешевий, рядок дорогий ─────────────────────
def fig_grid():
    W, H = 990, 500
    frags = []
    frags.append(text(W / 2, 34, "Ціна відвідувача: стовпець дешевий, рядок дорогий",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 58, "операції лягають у стовпці, типи — у рядки",
                      size=12.5, color=MUTED))

    col_lefts = [90, 245, 400, 555]
    col_w = [155, 155, 155, 155]
    row_tops = [110, 160, 220, 280, 340]
    row_h = [50, 60, 60, 60, 60]

    cells = [
        ["тип ╲ операція", "AreaVisitor", "SvgVisitor", "JsonVisitor\n(новий)"],
        ["Circle",    "π · r²",     "<circle>",  "{ r }"],
        ["Rectangle", "w · h",      "<rect>",    "{ w, h }"],
        ["Triangle",  "b · h / 2",  "<polygon>", "{ b, h }"],
        ["Hexagon\n(новий)", "?",   "?",         "?"],
    ]

    for ri in range(5):
        for ci in range(4):
            x = col_lefts[ci]
            y = row_tops[ri]
            w = col_w[ci]
            h = row_h[ri]
            ghost_col = (ci == 3)
            ghost_row = (ri == 4)
            header = (ri == 0 or ci == 0)
            if ghost_row:
                fill, stroke, tcol = RED_F, POS, INK if ci == 0 else MUTED
            elif ghost_col:
                fill, stroke, tcol = GREEN_F, FIELD, INK if ri == 0 else MUTED
            elif header:
                fill, stroke, tcol = FILL, LINE, INK
            else:
                fill, stroke, tcol = BG, LINE, INK
            bold = header or ghost_col and ri == 0 or ghost_row and ci == 0
            frags.append(fitbox(x, y, w, h, cells[ri][ci], size=13, pad=7,
                                 fill=fill, stroke=stroke, color=tcol, bold=bold))

    grid_right = col_lefts[3] + col_w[3]   # 710
    grid_bottom = row_tops[4] + row_h[4]   # 400

    # ── Анотація «новий стовпець дешево» (праворуч, до заголовка Json) ────────
    hdr_cx = col_lefts[3] + col_w[3] / 2   # 632.5
    frags.append(arrow(770, 135, grid_right + 4, 135, color=FIELD, sw=1.8))
    ax = 858
    frags.append(text(ax, 116, "новий візитор =", size=12, bold=True, color=FIELD))
    frags.append(text(ax, 134, "цілий стовпець збоку,", size=11.5, color=INK))
    frags.append(text(ax, 150, "фігури недоторкані.", size=11.5, color=INK))
    frags.append(text(ax, 172, "ДЕШЕВО", size=13, bold=True, color=FIELD))

    # ── Анотація «новий рядок дорого» (знизу, до рядка Hexagon) ───────────────
    row_cx = (col_lefts[0] + grid_right) / 2
    frags.append(arrow(row_cx, 438, row_cx, grid_bottom + 4, color=POS, sw=1.8))
    frags.append(text(row_cx, 458, "новий тип = новий рядок → нова клітина в КОЖНОМУ стовпці",
                      size=12, bold=True, color=POS))
    frags.append(text(row_cx, 476, "ДОРОГО: правимо всі наявні відвідувачі", size=11.5, color=MUTED))

    render(os.path.join(IMG, 'visitor-grid.svg'), W, H, *frags)


# ── Хроніка трьох ниток, що сплелися у Відвідувача ───────────────────────────
def fig_timeline():
    W, H = 1120, 800
    frags = []
    frags.append(text(W / 2, 34, "Три нитки, що сплелися у Відвідувача: хроніка",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 58,
                      "механізм старший за патерн (1986), а його ціна дістала ім'я пізніше (1998)",
                      size=12.5, color=MUTED))

    # ── Легенда: колір нитки ─────────────────────────────────────────────────
    legend = [(NEG,   "механізм: подвійна диспетчеризація", 150),
              (MUTED, "рідна множинна диспетчеризація",     500),
              (POS,   "ціна: проблема вираження",           850)]
    for col, lab, lx in legend:
        frags.append(circle(lx, 88, 6, fill=col, stroke=INK, sw=1))
        frags.append(text(lx + 14, 92, lab, size=11.5, color=INK, anchor="start"))

    spine_x = 178
    y0, step = 142, 96
    events = [
        ("1975", POS, RED_F, False,
         ["Джон Рейнольдс: типи-АТД ⟷ процедурні дані — два додатки до абстракції.",
          "Зерно майбутньої дилеми «легко типи ⟷ легко операції»."]),
        ("1986", NEG, BLUE_F, False,
         ["Ден Інгаллс, «multiple polymorphism»: подвійна диспетчеризація у Smalltalk",
          "на арифметиці різнотипних чисел — механізм за вісім років до патерна."]),
        ("1986", MUTED, GREY_F, False,
         ["CommonLoops (Xerox PARC), та сама конференція: у Lisp множинна",
          "диспетчеризація рідна — мовам із нею відвідувач не потрібен."]),
        ("1988", MUTED, GREY_F, False,
         ["CLOS вносить мультиметоди у стандарт Common Lisp: диспетч за",
          "всіма аргументами без жодного accept/visit."]),
        ("1994", NEG, BLUE_F, True,
         ["«Design Patterns»: прийом дістає ім'я «Відвідувач» і дім — дерево",
          "компілятора. Механізм — Інгаллсів; ім'я й роль — банди чотирьох."]),
        ("1998", POS, RED_F, True,
         ["Філіп Вадлер: «проблема вираження» — ціну відвідувача нарешті названо.",
          "«Нова назва старої задачі»; корінь — Рейнольдс, 1975."]),
        ("2005", POS, RED_F, False,
         ["Бухловський і Тілеке: відвідувач ≈ згортка (катаморфізм) — той самий",
          "обхід дерева, лише без церемоній accept/visit. Дзеркало у ФП."]),
    ]
    ys = [y0 + i * step for i in range(len(events))]
    frags.append(line(spine_x, ys[0], spine_x, ys[-1], color="#c2c8d0", sw=2.6))

    box_cx = 648
    for (yr, col, bf, knot, lines), y in zip(events, ys):
        bx, bw, bh = textbox(box_cx, y, lines, size=13, pad=11,
                             fill=bf, stroke=col, sw=1.8, min_w=816)
        r = 12 if knot else 8
        frags.append(line(spine_x + r + 2, y, box_cx - bw / 2 - 5, y, color=col, sw=1.6))
        frags.append(bx)
        frags.append(circle(spine_x, y, r, fill=col, stroke=INK, sw=1.4))
        if knot:
            frags.append(circle(spine_x, y, r + 4, fill="none", stroke=col, sw=1.6))
        frags.append(text(spine_x - r - 12, y + 4, yr, size=13.5, bold=True,
                          color=INK, anchor="end"))

    frags.append(line(60, 754, W - 60, 754, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 778,
                      "1994 — три нитки сходяться в патерні; 1998 — найглибшій із них, ціні, дають ім'я",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'visitor-timeline.svg'), W, H, *frags)


# ── Дерево виразу 2*(x+3)+-x: структура з 8 вузлів ────────────────────────────
def _tree_edges(frags, nodes, edges, dy=16):
    for a, b in edges:
        x1, y1 = nodes[a][0], nodes[a][1]
        x2, y2 = nodes[b][0], nodes[b][1]
        frags.append(line(x1, y1 + dy, x2, y2 - dy, color=GREY_S, sw=1.6))


def fig_ast_tree():
    W, H = 900, 600
    frags = []
    frags.append(text(W / 2, 34, "AST виразу  2 * (x + 3) + -x", size=18, bold=True))
    frags.append(text(W / 2, 58, "п'ять видів вузлів, 8 вузлів усього — кожен прохід торкнеться кожного рівно раз (O(n))",
                      size=12, color=MUTED))
    # (cx, cy, label, fill, stroke)
    nodes = {
        'root': (450, 108, "Add", FILL, LINE),
        'mul':  (250, 220, "Mul", FILL, LINE),
        'neg':  (650, 220, "Neg", FILL, LINE),
        'num2': (140, 334, "Num 2", BLUE_F, NEG),
        'iadd': (372, 334, "Add", FILL, LINE),
        'vxr':  (650, 334, "Var x", GREEN_F, FIELD),
        'vxl':  (292, 448, "Var x", GREEN_F, FIELD),
        'num3': (452, 448, "Num 3", BLUE_F, NEG),
    }
    edges = [('root', 'mul'), ('root', 'neg'), ('mul', 'num2'), ('mul', 'iadd'),
             ('neg', 'vxr'), ('iadd', 'vxl'), ('iadd', 'num3')]
    _tree_edges(frags, nodes, edges)
    for k, (cx, cy, lbl, fill, stroke) in nodes.items():
        b, w, h = textbox(cx, cy, lbl, size=14, bold=True, fill=fill, stroke=stroke, sw=1.8, min_w=88)
        frags.append(b)
    frags.append(line(120, 520, 780, 520, color="#d0d5db", sw=1.1))
    frags.append(text(140, 548, "Num, Var — листки (без дітей)", size=12, color=MUTED, anchor="start"))
    frags.append(text(140, 570, "Add, Mul — двомісні, Neg — одномісний внутрішній вузол",
                      size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, 'visitor-ast-tree.svg'), W, H, *frags)


# ── Прогін обчислювача: значення повертаються вгору (x=5) ─────────────────────
def fig_eval_trace():
    W, H = 900, 600
    frags = []
    frags.append(text(W / 2, 34, "Прогін обчислювача над тим самим деревом  (x = 5)", size=18, bold=True))
    frags.append(text(W / 2, 58, "кожен visit повертає число вгору; порядок ①—⑧ — post-order: діти раніше за батька",
                      size=12, color=MUTED))
    # (cx, cy, [lines], order)
    nodes = {
        'root': (450, 112, ["Add", "→ 11"], 8),
        'mul':  (250, 226, ["Mul", "→ 16"], 5),
        'neg':  (650, 226, ["Neg", "→ −5"], 7),
        'num2': (140, 342, ["Num 2", "→ 2"], 1),
        'iadd': (372, 342, ["Add", "→ 8"], 4),
        'vxr':  (650, 342, ["Var x", "→ 5"], 6),
        'vxl':  (292, 456, ["Var x", "→ 5"], 2),
        'num3': (452, 456, ["Num 3", "→ 3"], 3),
    }
    edges = [('root', 'mul'), ('root', 'neg'), ('mul', 'num2'), ('mul', 'iadd'),
             ('neg', 'vxr'), ('iadd', 'vxl'), ('iadd', 'num3')]
    _tree_edges(frags, nodes, edges, dy=24)
    for k, (cx, cy, lbl, order) in nodes.items():
        b, w, h = textbox(cx, cy, lbl, size=13, bold=True, fill=GREEN_F, stroke=FIELD, sw=1.8, min_w=94)
        frags.append(b)
        ox = cx - w / 2 - 15
        frags.append(circle(ox, cy, 11, fill=BG, stroke=NEG, sw=1.7))
        frags.append(text(ox, cy + 4, str(order), size=12, bold=True, color=NEG))
    frags.append(line(120, 528, 780, 528, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 556, "8 вузлів → 8 викликів visit, жодного зайвого проходу: час O(n), глибина стека O(h)",
                      size=12.5, bold=True, color=INK))
    render(os.path.join(IMG, 'visitor-eval-trace.svg'), W, H, *frags)


# ── Згортання констант: сталий піддерево → один літерал ───────────────────────
def fig_fold():
    W, H = 920, 520
    frags = []
    frags.append(text(W / 2, 34, "Згортання констант: сталий піддерево → один літерал", size=18, bold=True))
    frags.append(text(W / 2, 58, "2 * (3 + 4) + x   →   14 + x     (змінна x лишається; 7 вузлів → 3)",
                      size=12, color=MUTED))
    L = {
        'add': (200, 112, "Add", FILL, LINE),
        'mul': (120, 214, "Mul", GREEN_F, FIELD),
        'vx':  (300, 214, "Var x", FILL, LINE),
        'n2':  (60, 318, "Num 2", GREEN_F, FIELD),
        'iad': (188, 318, "Add", GREEN_F, FIELD),
        'n3':  (130, 418, "Num 3", GREEN_F, FIELD),
        'n4':  (248, 418, "Num 4", GREEN_F, FIELD),
    }
    Le = [('add', 'mul'), ('add', 'vx'), ('mul', 'n2'), ('mul', 'iad'), ('iad', 'n3'), ('iad', 'n4')]
    _tree_edges(frags, L, Le)
    for k, (cx, cy, lbl, f, s) in L.items():
        bx, w, h = textbox(cx, cy, lbl, size=13, bold=True, fill=f, stroke=s, sw=1.7, min_w=80)
        frags.append(bx)
    frags.append(text(185, 470, "до: 7 вузлів  (зелене — сталі)", size=12, color=MUTED))

    frags.append(arrow(370, 250, 508, 250, color=INK, sw=2.4))
    frags.append(text(439, 231, "Folder", size=13, bold=True, color=INK))
    frags.append(text(439, 276, "post-order:", size=11, color=MUTED))
    frags.append(text(439, 292, "діти раніше", size=11, color=MUTED))

    R = {
        'add': (700, 150, "Add", FILL, LINE),
        'n14': (620, 270, "Num 14", GREEN_F, FIELD),
        'vx':  (790, 270, "Var x", FILL, LINE),
    }
    Re = [('add', 'n14'), ('add', 'vx')]
    _tree_edges(frags, R, Re)
    for k, (cx, cy, lbl, f, s) in R.items():
        bx, w, h = textbox(cx, cy, lbl, size=13, bold=True, fill=f, stroke=s, sw=1.7, min_w=80)
        frags.append(bx)
    frags.append(text(705, 470, "після: 3 вузли", size=12, color=MUTED))
    render(os.path.join(IMG, 'visitor-fold.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_double_dispatch()
    fig_grid()
    fig_timeline()
    fig_ast_tree()
    fig_eval_trace()
    fig_fold()
    print("figs done")
