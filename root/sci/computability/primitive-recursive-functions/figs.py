# -*- coding: utf-8 -*-
"""Фігури до статті «Примітивно-рекурсивні функції».
Запуск:  python figs.py   → пише SVG у ./img/
  recursion-schema · arithmetic-tower · diagonal-ceiling ·
  recursion-timeline · recipe-trees · cost-blowup ·
  diagonal-snap · ackermann-levels
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eef2ff"


def boxc(cx, cy, w, h, lines, size=14, fill=FILL, stroke=LINE, sw=1.6,
         color=INK, bold=False, rx=8):
    """Прямокутник із центром (cx,cy) і центрованим багаторядковим написом."""
    if isinstance(lines, str):
        lines = [lines]
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx)
    ty = cy - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
    out += mtext(cx, ty, lines, size=size, color=color, bold=bold)
    return out


# ── 1. Схема примітивної рекурсії: спуск до бази й підйом угору ───────────────
def fig_recursion_schema():
    W, H = 1020, 350
    f = [text(W / 2, 30, "Примітивна рекурсія: значення тримаються одне за одне й спускаються до нуля",
              size=17, bold=True)]

    # схема (дві рядки) — угорі праворуч
    f.append(boxc(800, 96, 400, 66,
                  ["h(x, 0)     =  f(x)",
                   "h(x, y+1) =  g( x, y, h(x, y) )"],
                  size=15, fill=BLUEFILL, stroke=NEG, bold=False))

    # вузли: база ліворуч, лічильник зростає праворуч
    xs = [155, 385, 615, 845]
    ny = 214
    labels = ["h(x, 0)", "h(x, 1)", "h(x, 2)", "h(x, 3)"]
    nw, nh = 150, 52
    for i, (x, lab) in enumerate(zip(xs, labels)):
        base = (i == 0)
        f.append(boxc(x, ny, nw, nh, lab, size=15, bold=base,
                      fill=(GREENFILL if base else FILL),
                      stroke=(FIELD if base else LINE),
                      sw=(2.4 if base else 1.6),
                      color=(FIELD if base else INK)))

    # верхні стрілки залежності (вліво): кожне потребує лівого сусіда
    for i in range(3):
        f.append(arrow(xs[i + 1] - nw / 2 - 6, 170, xs[i] + nw / 2 + 6, 170,
                       color=MUTED, sw=1.8))
    f.append(text((xs[0] + xs[3]) / 2, 152,
                  "залежність: кожне значення потребує попереднього — спуск до бази",
                  size=12.5, color=MUTED, italic=True))

    # нижні стрілки обчислення (вправо): маючи базу, рахуємо вгору
    for i in range(3):
        f.append(arrow(xs[i] + nw / 2 + 6, 258, xs[i + 1] - nw / 2 - 6, 258,
                       color=INK, sw=1.9))
    f.append(text((xs[0] + xs[3]) / 2, 288,
                  "обчислення: від бази рахуємо вправо через g( x, y, попереднє )",
                  size=12.5, color=INK, italic=True))

    # позначка бази під нулем
    f.append(text(xs[0], 322, "дно драбини — відповідь прямо", size=11.5,
                  color=FIELD, italic=True))
    # хвіст «і далі»
    f.append(text(xs[3] + nw / 2 + 30, ny + 6, "…", size=26, bold=True))
    f.append(text(xs[3] + nw / 2 + 34, ny + 30, "будь-яке y", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "recursion-schema.svg"), W, H, *f)


# ── 2. Вежа арифметики: кожна дія — повтор попередньої ───────────────────────
def fig_arithmetic_tower():
    W, H = 760, 590
    f = [text(W / 2, 28, "Вежа арифметики: кожна дія — попередня, повторена y разів",
              size=17, bold=True)]

    cx = 380
    bw = 460
    tops = [64, 194, 324, 454]            # L3 (степінь) … L0 (наступник)
    rows = [
        ("Степінь",   "exp(x, y+1) = mul( x, exp(x, y) )", FILL, LINE),
        ("Множення",  "mul(x, y+1) = add( x, mul(x, y) )", FILL, LINE),
        ("Додавання", "add(x, y+1) = S( add(x, y) )",      FILL, LINE),
        ("Наступник", "S(x) = x + 1",                      GREENFILL, FIELD),
    ]
    bh = 84
    for (name, schema, fill, stroke), top in zip(rows, tops):
        cy = top + bh / 2
        f.append(rect(cx - bw / 2, top, bw, bh, fill=fill, stroke=stroke,
                      sw=(2.4 if fill == GREENFILL else 1.6), rx=9))
        f.append(text(cx, cy - 10, name, size=17, bold=True,
                      color=(FIELD if fill == GREENFILL else INK)))
        f.append(text(cx, cy + 16, schema, size=13.5, color=MUTED))

    # стрілки «означує вищий щабель», у проміжках, ліворуч від центру
    ax = 236
    for i in range(3):
        y_lo = tops[i + 1]                 # верх нижчого блоку
        y_hi = tops[i] + bh                # низ вищого блоку
        f.append(arrow(ax, y_lo - 4, ax, y_hi + 4, color=INK, sw=2.2))
        f.append(text(ax + 40, (y_lo + y_hi) / 2 + 4, "×y", size=13,
                      bold=True, color=NEG))

    f.append(text(W / 2, 566,
                  "нижче — простіше й повільніше, вище — стрімкіше; функція Аккермана лізе цими щаблями всіма",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "arithmetic-tower.svg"), W, H, *f)


# ── 3. Діагональна стеля: d(n)=gₙ(n)+1 поза списком ──────────────────────────
def fig_diagonal_ceiling():
    W, H = 820, 500
    f = [text(W / 2, 28, "Діагональ: функція, якої немає серед примітивно-рекурсивних",
              size=17, bold=True)]

    sub = ["₀", "₁", "₂", "₃", "₄"]
    x0, y0 = 178, 96
    cw, ch = 70, 50
    n = 5

    # заголовки стовпців (входи)
    f.append(text(x0 - 34, y0 - 14, "вхід →", size=12, color=MUTED,
                  italic=True, anchor="middle"))
    for j in range(n):
        f.append(text(x0 + j * cw + cw / 2, y0 - 12, str(j), size=13,
                      bold=True, color=MUTED))
    # заголовки рядків (функції)
    f.append(text(x0 - 44, y0 - 30, "функції ↓", size=12, color=MUTED,
                  italic=True, anchor="middle"))
    for i in range(n):
        f.append(text(x0 - 34, y0 + i * ch + ch / 2 + 5, "g" + sub[i],
                      size=14, bold=True))

    # клітини
    for i in range(n):
        for j in range(n):
            x, y = x0 + j * cw, y0 + i * ch
            diag = (i == j)
            f.append(rect(x, y, cw, ch, fill=(GREENFILL if diag else BG),
                          stroke=(FIELD if diag else "#c9ced6"),
                          sw=(2.2 if diag else 1.2), rx=4))
            f.append(text(x + cw / 2, y + ch / 2 + 5, "g" + sub[i] + "(" + str(j) + ")",
                          size=12.5, bold=diag,
                          color=(FIELD if diag else INK)))

    # d-рядок унизу
    dy = y0 + n * ch + 26
    f.append(text(x0 - 34, dy + ch / 2 + 5, "d", size=15, bold=True, color=POS))
    for j in range(n):
        x = x0 + j * cw
        f.append(rect(x, dy, cw, ch, fill=REDFILL, stroke=POS, sw=1.6, rx=4))
        f.append(text(x + cw / 2, dy + ch / 2 + 5, "g" + sub[j] + "(" + str(j) + ")+1",
                      size=11.5, color=POS))

    # одна стрілка «+1» від діагоналі до d-рядка (у проміжку під стовпцем 4)
    cxg = x0 + 4 * cw + cw / 2
    f.append(arrow(cxg, y0 + n * ch + 2, cxg, dy - 2, color=POS, sw=1.8))

    # пояснювальна рамка праворуч
    nx = x0 + n * cw + 24
    f.append(rect(nx, y0, W - nx - 22, ch * n - 6, fill="#fbfcfe",
                  stroke="#c9ced6", sw=1.4, rx=8))
    note = ["Зелена діагональ — gₙ(n).", "",
            "Будуємо d(n) = gₙ(n) + 1:", "у стовпці n вона на 1", "більша за gₙ(n).", "",
            "Тому d ≠ gₙ для КОЖНОГО n", "— її немає в списку.", "",
            "d обчислювана й тотальна,", "але не примітивно-", "рекурсивна."]
    ty = y0 + 18
    for ln in note:
        f.append(text(nx + 14, ty, ln, size=12, color=INK, anchor="start"))
        ty += 17

    render(os.path.join(IMG, "diagonal-ceiling.svg"), W, H, *f)


# ── 4. Стрічка часу: народження примітивної рекурсії (для вставки hist) ───────
def fig_recursion_timeline():
    W, H = 900, 690
    f = [text(W / 2, 32, "Народження примітивної рекурсії: вісім кроків за 74 роки",
              size=17, bold=True)]
    spine_x, card_x, card_w = 210, 250, 620
    rows = [
        ("1861", "Герман Грассман · Hermann Grassmann",
         "перші рекурсивні означення + і ×; закони доведено індукцією", FILL, LINE),
        ("1881", "Чарлз Пірс · Charles S. Peirce",
         "незалежна рекурсивна аксіоматика арифметики (США)", FILL, LINE),
        ("1888", "Ріхард Дедекінд · Richard Dedekind",
         "теорема рекурсії: така функція існує й єдина (теорема 126)", BLUEFILL, NEG),
        ("1923", "Торальф Сколем · Thoralf Skolem",
         "примітивно-рекурсивна арифметика — фінітна основа", FILL, LINE),
        ("1927", "Габріель Судан · Gabriel Sudan",
         "перша опублікована тотальна функція поза класом", REDFILL, POS),
        ("1928", "Вільгельм Аккерман · Wilhelm Ackermann",
         "друга така функція; обидва — учні Гільберта", REDFILL, POS),
        ("1931", "Курт Гедель · Kurt Gödel",
         "уживає їх («rekursiv») для арифметизації доказовості", BLUEFILL, NEG),
        ("1934–35", "Рожа Петер · Rózsa Péter",
         "термін «примітивно-рекурсивна»; двоаргументний Аккерман", GREENFILL, FIELD),
    ]
    ys = [92 + i * 72 for i in range(len(rows))]
    f.append(line(spine_x, ys[0] - 12, spine_x, ys[-1] + 12, color=MUTED, sw=2))
    for (year, name, det, fill, stroke), cy in zip(rows, ys):
        f.append(line(spine_x, cy, card_x, cy, color=MUTED, sw=1.6))
        f.append(text(spine_x - 18, cy + 5, year, size=14, bold=True, anchor="end"))
        f.append(rect(card_x, cy - 26, card_w, 52, fill=fill, stroke=stroke, sw=1.8, rx=8))
        f.append(text(card_x + 16, cy - 4, name, size=15, bold=True, anchor="start"))
        f.append(text(card_x + 16, cy + 16, det, size=13, color=MUTED, anchor="start"))
        f.append(circle(spine_x, cy, 7, fill=stroke, stroke=BG, sw=2))
    f.append(text(W / 2, H - 22,
                  "червоне — перші функції поза класом (обидва — учні Гільберта); "
                  "синє — теорема й застосування; зелене — коли клас дістав ім'я",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "recursion-timeline.svg"), W, H, *f)


# ── 5. Рецепт як дерево: add повністю, mul через готовий add (для вставки proj) ─
def fig_recipe_trees():
    W, H = 940, 500
    f = [text(W / 2, 30, "Функція — це скінченне дерево-рецепт; один інтерпретатор його виконує",
              size=17, bold=True)]

    OP = BLUEFILL      # операції збірки (Rec, Comp)
    AT = GREENFILL     # атоми (Zero, Succ, Proj)
    RE = REDFILL       # уже зібраний рецеп, вставлений усередину
    nw, nh = 84, 42

    def node(cx, cy, label, fill, stroke, size=15, bold=True):
        return boxc(cx, cy, nw, nh, label, size=size, bold=bold, fill=fill,
                    stroke=stroke, color=(FIELD if fill == AT else
                                          POS if fill == RE else NEG), rx=9)

    def edge(x1, y1, x2, y2):
        return line(x1, y1 + nh / 2, x2, y2 - nh / 2, color=MUTED, sw=1.6)

    # ── add: Rec( P¹₁ , Comp( S, P³₃ ) ) ──
    ax = 232
    f.append(text(ax, 74, "add", size=15, bold=True, color=INK))
    r0 = (ax, 108)
    b0, c0 = (ax - 96, 226), (ax + 96, 226)
    s0, p0 = (ax + 44, 350), (ax + 150, 350)
    f.append(edge(*r0, *b0)); f.append(edge(*r0, *c0))
    f.append(edge(*c0, *s0)); f.append(edge(*c0, *p0))
    f.append(text((r0[0] + b0[0]) / 2 + 21, 176, "база", size=11, color=MUTED, italic=True))
    f.append(text((r0[0] + c0[0]) / 2 - 18, 176, "крок", size=11, color=MUTED, italic=True))
    f.append(node(*r0, "Rec", OP, NEG))
    f.append(node(*b0, "P¹₁", AT, FIELD))
    f.append(node(*c0, "Comp", OP, NEG))
    f.append(node(*s0, "S", AT, FIELD))
    f.append(node(*p0, "P³₃", AT, FIELD))

    # ── mul: Rec( Z , Comp( add, P³₁, P³₃ ) ) ──
    mx = 680
    f.append(text(mx, 74, "mul", size=15, bold=True, color=INK))
    r1 = (mx, 108)
    b1, c1 = (mx - 96, 226), (mx + 84, 226)
    a1, q1, w1 = (mx - 4, 350), (mx + 96, 350), (mx + 196, 350)
    f.append(edge(*r1, *b1)); f.append(edge(*r1, *c1))
    f.append(edge(*c1, *a1)); f.append(edge(*c1, *q1)); f.append(edge(*c1, *w1))
    f.append(text((r1[0] + b1[0]) / 2 + 18, 176, "база", size=11, color=MUTED, italic=True))
    f.append(text((r1[0] + c1[0]) / 2 - 18, 176, "крок", size=11, color=MUTED, italic=True))
    f.append(node(*r1, "Rec", OP, NEG))
    f.append(node(*b1, "Z", AT, FIELD))
    f.append(node(*c1, "Comp", OP, NEG))
    f.append(node(*a1, "add", RE, POS))
    f.append(node(*q1, "P³₁", AT, FIELD))
    f.append(node(*w1, "P³₃", AT, FIELD))

    # легенда
    ly = 430
    for i, (lab, fill, stroke, col) in enumerate([
            ("операції збірки: Rec, Comp", OP, NEG, NEG),
            ("атоми: Zero, Succ, Proj", AT, FIELD, FIELD),
            ("готовий рецепт усередині", RE, POS, POS)]):
        x = 70 + i * 300
        f.append(rect(x, ly - 13, 22, 22, fill=fill, stroke=stroke, sw=1.8, rx=5))
        f.append(text(x + 30, ly + 4, lab, size=12.5, color=INK, anchor="start"))
    f.append(text(W / 2, 470,
                  "exp — те саме дерево, що mul, тільки в крок вставлено готовий рецепт mul замість add",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "recipe-trees.svg"), W, H, *f)


# ── 6. Пастка: наївне дерево робить ~ (2ʸ)² кроків (для вставки proj) ─────────
def fig_cost_blowup():
    import math as _m
    W, H = 940, 520
    f = [text(W / 2, 30, "Наївне дерево: щоб порахувати 2ʸ, обчислювач відвідує ~ (2ʸ)² вузлів",
              size=17, bold=True)]

    # (y, значення 2ʸ, наївних викликів ev) — виміряно
    data = [(2, 4, 42), (3, 8, 120), (4, 16, 398), (5, 32, 1460), (6, 64, 5626),
            (7, 128, 22144), (8, 256, 87942), (9, 512, 350604), (10, 1024, 1400210),
            (11, 2048, 5596568), (12, 4096, 22377886)]
    x0, y0 = 268, 80
    row_h = 33
    bar_max = 470
    logmax = _m.log10(data[-1][2])
    f.append(text(x0 - 12, y0 - 16, "exp(2, y) = 2ʸ", size=12.5, color=MUTED,
                  italic=True, anchor="end"))
    f.append(text(x0 + 8, y0 - 16, "викликів обчислювача ev  (довжина смуги — за log₁₀)",
                  size=12.5, color=MUTED, italic=True, anchor="start"))
    for i, (y, val, ops) in enumerate(data):
        cy = y0 + i * row_h + row_h / 2
        f.append(text(x0 - 14, cy + 5, "exp(2,%d) = %d" % (y, val),
                      size=13, color=INK, anchor="end"))
        bw = bar_max * _m.log10(ops) / logmax
        f.append(rect(x0 + 8, cy - 10, bw, 20, fill=REDFILL, stroke=POS, sw=1.5, rx=5))
        f.append(text(x0 + 16 + bw, cy + 5, "{:,}".format(ops).replace(",", " "),
                      size=12.5, color=POS, anchor="start", bold=True))
    fy = y0 + len(data) * row_h + 40
    f.append(line(60, fy - 18, W - 60, fy - 18, color="#d8dce2", sw=1.2))
    f.append(text(W / 2, fy,
                  "значення скромне, а робота множиться вчетверо на кожен +1 до y — це майже квадрат значення",
                  size=12.5, color=INK, italic=True))
    f.append(text(W / 2, fy + 22,
                  "exp(2,30): значення ≈ 10⁹, а вузлів уже ≈ 10¹⁸ — стіна не в пам'яті, а в кількості дій",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cost-blowup.svg"), W, H, *f)


# ── 7. Ланцюг п'яти кроків: нумерація → U → діагональ → суперечність → висновок (для вставки math) ─
def fig_diagonal_snap():
    W, H = 900, 800
    f = [text(W / 2, 30,
              "П'ять кроків діагоналі: від нумерації рецептів до провалу власного виконавця",
              size=16.5, bold=True)]

    cx, cw, ch = 460, 700, 66
    xs_gap = 96
    ys = [110 + i * xs_gap for i in range(7)]

    cards = [
        (["Крок 1 · рецепти пронумеровано",
          "e₀, e₁, e₂, … → функції g₀, g₁, g₂, …"], FILL, LINE, INK),
        (["Крок 2 · універсальний виконавець",
          "U(n, x) = gₙ(x) — тотальна й обчислювана"], BLUEFILL, NEG, INK),
        (["Крок 3 · діагональ",
          "d(n) = U(n, n) + 1 = gₙ(n) + 1"], FILL, LINE, INK),
        (["Крок 4 · припущення від супротивного",
          "нехай d = gₖ — стоїть у списку під номером k"], FILL, LINE, INK),
        (["Крок 4 · суперечність",
          "gₖ(k) = gₖ(k) + 1  ⟹  0 = 1  →  d не примітивно-рекурсивна"], REDFILL, POS, POS),
        (["Крок 5 · d через U",
          "d(n) = S( U( P¹₁(n), P¹₁(n) ) ) — якби U була ПР, то й d — суперечність"], FILL, LINE, INK),
        (["Висновок",
          "сама U НЕ примітивно-рекурсивна — клас не тлумачить себе зсередини"], GREENFILL, FIELD, FIELD),
    ]

    x = cx - cw / 2
    for (lines, fill, stroke, color), cy in zip(cards, ys):
        y = cy - ch / 2
        bold = (fill == GREENFILL or fill == REDFILL)
        f.append(fitbox(x, y, cw, ch, lines, size=15, pad=14,
                        fill=fill, stroke=stroke, sw=(2.4 if bold else 1.6),
                        color=color, bold=bold, rx=9))

    for i in range(len(ys) - 1):
        f.append(arrow(cx, ys[i] + ch / 2 + 4, cx, ys[i + 1] - ch / 2 - 4, color=MUTED, sw=2))

    f.append(text(W / 2, ys[-1] + ch / 2 + 40,
                  "кожен крок доведений до кінця в тексті; злам на кроці 4 тягне за собою висновок кроку 5",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "diagonal-snap.svg"), W, H, *f)


# ── 8. Віяло стель Аккермана: A(0,·)…A(3,·) і діагональ a(n)=A(n,n) над усіма (для вставки math) ─
def fig_ackermann_levels():
    W, H = 980, 560
    f = [text(W / 2, 28,
              "Стелі Аккермана: діагональ a(n)=A(n,n) переростає кожну фіксовану стелю",
              size=16.5, bold=True)]

    x0, step = 150, 90
    xs = [x0 + i * step for i in range(9)]
    y_base = 500

    curves = [
        ("A0", [452, 432, 412, 392, 372, 352, 332, 312, 292], MUTED, 2.0),
        ("A1", [452, 420, 389, 357, 326, 294, 263, 231, 200], INK, 2.2),
        ("A2", [452, 414, 377, 339, 302, 264, 226, 189, 151], NEG, 2.4),
        ("A3", [452, 408, 364, 320, 276, 232, 188, 144, 100], FIELD, 2.6),
        ("a", [462, 458, 448, 428, 393, 338, 263, 168, 88], POS, 3.4),
    ]

    # осі
    f.append(line(x0, y_base, x0, 92, color="#c9ced6", sw=1.6))
    f.append(line(x0, y_base, 900, y_base, color="#c9ced6", sw=1.6))
    for i in (0, 2, 4, 6, 8):
        f.append(text(xs[i], y_base + 22, str(i), size=12, color=MUTED))
    f.append(text((x0 + 900) / 2, y_base + 44, "n", size=12.5, color=MUTED, italic=True))

    # криві — ламані через відрізки
    for name, ys, color, sw in curves:
        for i in range(len(xs) - 1):
            f.append(line(xs[i], ys[i], xs[i + 1], ys[i + 1], color=color, sw=sw))

    # легенда — у вільному верхньому лівому куті, осторонь від кривих
    lx, ly, lw, lh = 178, 96, 320, 178
    f.append(rect(lx, ly, lw, lh, fill="#fbfcfe", stroke="#c9ced6", sw=1.4, rx=8))
    legend = [
        ("A(0, ·) ≈ n + 1 — найнижча стеля", MUTED, 2.0),
        ("A(1, ·) — вища стеля", INK, 2.2),
        ("A(2, ·) — ще вища", NEG, 2.4),
        ("A(3, ·) — найвища з чотирьох", FIELD, 2.6),
        ("a(n) = A(n, n) — діагональ (жирна)", POS, 3.4),
    ]
    for i, (lab, color, sw) in enumerate(legend):
        ry = ly + 24 + i * 30
        f.append(line(lx + 16, ry, lx + 56, ry, color=color, sw=sw))
        f.append(text(lx + 68, ry + 5, lab, size=12.5, color=INK, anchor="start"))

    f.append(text(W / 2, H - 22,
                  "схематично, не в масштабі — справжні криві A(m,·) розходяться незмірно швидше",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "ackermann-levels.svg"), W, H, *f)


if __name__ == "__main__":
    fig_recursion_schema()
    fig_arithmetic_tower()
    fig_diagonal_ceiling()
    fig_recursion_timeline()
    fig_recipe_trees()
    fig_cost_blowup()
    fig_diagonal_snap()
    fig_ackermann_levels()
    print("OK: figs -> img/")
