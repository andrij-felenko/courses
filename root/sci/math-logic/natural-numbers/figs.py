# -*- coding: utf-8 -*-
"""Фігури до статті «Натуральні числа».
Запуск:  python figs.py   → пише SVG у ./img/
  successor-chain · peano-guards · von-neumann
  recursion-descent · laws-ladder · order-reach   (вставка math-recursive-arithmetic)
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eaf0fd"
ROW = "#f4f6f8"


def node(cx, cy, lab, r=32, fill=FILL, stroke=LINE, sw=1.8, tcol=INK, bold=True):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw) + \
           text(cx, cy + 6, lab, size=17, bold=bold, color=tcol)


# ── 1. Хребет: початок 0 + наступник породжують усю низку ─────────────────────
def fig_successor_chain():
    W, H = 988, 400
    f = [text(W / 2, 34, "Початок і одне правило «наступний» — і виростає вся низка",
              size=18, bold=True),
         text(W / 2, 56, "число — це нуль, до якого стільки разів застосували наступника, скільки в ньому одиниць",
              size=12, color=MUTED, italic=True)]

    cy = 150
    centers = [115, 300, 485, 670, 855]
    labels = ["0", "1", "2", "3", "4"]

    # стрілки «S» між вузлами
    for i in range(len(centers) - 1):
        x1, x2 = centers[i] + 34 + 6, centers[i + 1] - 34 - 6
        f.append(arrow(x1, cy, x2, cy, color=INK, sw=2.0))
        f.append(text((x1 + x2) / 2, cy - 14, "S", size=15, bold=True, color=NEG))
    # хвіст «…»
    f.append(arrow(centers[-1] + 34 + 6, cy, centers[-1] + 34 + 46, cy, color=INK, sw=2.0))
    f.append(text(centers[-1] + 92, cy + 7, "…", size=26, bold=True))
    f.append(text(centers[-1] + 92, cy + 34, "без кінця", size=11, color=MUTED, italic=True))

    # вузли (нуль — зелений початок)
    for i, (cx, lab) in enumerate(zip(centers, labels)):
        first = (i == 0)
        f.append(node(cx, cy, lab, fill=(GREENFILL if first else FILL),
                      stroke=(FIELD if first else LINE), sw=(2.6 if first else 1.8),
                      tcol=(FIELD if first else INK)))

    # позначка «сюди стрілки нема» над нулем
    f.append(text(115, cy - 52, "⊘ жодна стрілка сюди не веде", size=11.5,
                  color=FIELD, italic=True))
    f.append(line(115, cy - 44, 115, cy - 36, color=FIELD, sw=1.4, dash="3,3"))

    # чотири правила — рівний ряд карток унизу
    by, bh = 300, 66
    cards = [
        ("0 — справжній початок", "нуль ні за ким не стоїть"),
        ("рівно один наступник", "у кожного числа один S(n)"),
        ("наступники не зливаються", "різні числа → різні S(n)"),
        ("поза низкою нічого нема", "це аксіома індукції"),
    ]
    cw, gap = 218, 12
    x0 = (W - (cw * 4 + gap * 3)) / 2
    for i, (t1, t2) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, by, cw, bh, fill=ROW, stroke=MUTED, sw=1.3, rx=8))
        f.append(text(x + cw / 2, by + 26, t1, size=13, bold=True))
        f.append(text(x + cw / 2, by + 48, t2, size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "successor-chain.svg"), W, H, *f)


# ── 2. Три способи зіпсувати числа, викинувши одну аксіому ────────────────────
def fig_peano_guards():
    W, H = 980, 400
    f = [text(W / 2, 34, "Що ламається, якщо викинути аксіому", size=18, bold=True),
         text(W / 2, 56, "кожне правило Пеано прибирає рівно одну з цих потвор",
              size=12, color=MUTED, italic=True)]

    # роздільники між панелями
    f.append(line(W / 3, 78, W / 3, 300, color="#dcdfe4", sw=1.2))
    f.append(line(2 * W / 3, 78, 2 * W / 3, 300, color="#dcdfe4", sw=1.2))

    # ── Панель A: кільце (без «0 не наступник») ──
    ax = W / 6
    f.append(text(ax, 100, "без «0 не наступник»", size=13.5, bold=True))
    # три вузли в трикутник + замикальна червона стрілка
    A = (ax, 150)          # 0 (верх)
    B = (ax - 62, 245)     # 1
    C = (ax + 62, 245)     # 2
    f.append(arrow(A[0] - 16, A[1] + 18, B[0] + 4, B[1] - 22, color=INK, sw=1.9))
    f.append(arrow(B[0] + 24, B[1] + 8, C[0] - 24, C[1] + 8, color=INK, sw=1.9))
    f.append(arrow(C[0] + 4, C[1] - 22, A[0] + 16, A[1] + 18, color=POS, sw=2.4))  # 2→0 — зле
    f.append(node(*A, "0", r=25, fill=REDFILL, stroke=POS, sw=2.2, tcol=POS))
    f.append(node(*B, "1", r=25))
    f.append(node(*C, "2", r=25))
    f.append(fitbox(ax - 138, 310, 276, 56,
                    "Низка згортається в кільце —\nсправжнього початку немає.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.3))

    # ── Панель B: злиття (без ін'єктивності) ──
    bx = W / 2
    f.append(text(bx, 100, "без «наступники не зливаються»", size=13.5, bold=True))
    P = (bx - 70, 150)     # a
    Q = (bx - 70, 240)     # b
    Rr = (bx + 78, 195)    # спільний наступник
    f.append(arrow(P[0] + 22, P[1] + 8, Rr[0] - 24, Rr[1] - 14, color=POS, sw=2.4))
    f.append(arrow(Q[0] + 22, Q[1] - 8, Rr[0] - 24, Rr[1] + 14, color=POS, sw=2.4))
    f.append(node(*P, "a", r=25))
    f.append(node(*Q, "b", r=25))
    f.append(node(*Rr, "S", r=25, fill=REDFILL, stroke=POS, sw=2.2, tcol=POS))
    f.append(fitbox(bx - 138, 310, 276, 56,
                    "Два різні числа стікаються\nв один наступник — нитка розгалужена.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.3))

    # ── Панель C: чужа низка (без індукції) ──
    ccx = 5 * W / 6
    f.append(text(ccx, 100, "без індукції", size=13.5, bold=True))
    # головна низка
    main = [ccx - 74, ccx, ccx + 74]
    for i in range(2):
        f.append(arrow(main[i] + 23, 150, main[i + 1] - 23, 150, color=INK, sw=1.9))
    f.append(text(ccx + 96, 156, "…", size=22, bold=True))
    for cx, lab in zip(main, ["0", "1", "2"]):
        first = (lab == "0")
        f.append(node(cx, 150, lab, r=23, fill=(GREENFILL if first else FILL),
                      stroke=(FIELD if first else LINE), tcol=(FIELD if first else INK)))
    # чужа низка нижче — червона, відірвана
    alien = [ccx - 60, ccx + 14]
    f.append(arrow(alien[0] + 22, 245, alien[1] - 22, 245, color=POS, sw=1.9))
    f.append(text(alien[1] + 40, 251, "…", size=22, bold=True, color=POS))
    for cx, lab in zip(alien, ["a", "b"]):
        f.append(node(cx, 245, lab, r=22, fill=REDFILL, stroke=POS, tcol=POS))
    f.append(fitbox(ccx - 138, 310, 276, 56,
                    "Збоку висить чужа низка,\nнедосяжна від нуля.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, "peano-guards.svg"), W, H, *f)


# ── 3. Числа як вкладені множини (фон Нейман) ─────────────────────────────────
def fig_von_neumann():
    W, H = 900, 360
    f = [text(W / 2, 34, "Числа, зібрані з порожнечі", size=18, bold=True),
         text(W / 2, 56, "кожне число — це множина всіх менших за нього; наступник докидає в множину її саму",
              size=12, color=MUTED, italic=True)]

    # чотири клітини 0..3
    centers = [130, 355, 580, 795]
    tops = ["0", "1", "2", "3"]
    sets = ["∅", "{0}", "{0, 1}", "{0, 1, 2}"]

    cy = 175
    for cx, top, st in zip(centers, tops, sets):
        # мітка числа
        f.append(text(cx, cy - 78, top, size=22, bold=True, color=NEG))
        # рамка-множина
        bw = 120 if top != "3" else 150
        bx, byy, bh = cx - bw / 2, cy - 46, 92
        f.append(rect(bx, byy, bw, bh, fill=BLUEFILL, stroke=NEG, sw=1.8, rx=10))
        # вміст: точки-попередники
        n = int(top)
        if n == 0:
            f.append(text(cx, cy + 6, "∅", size=22, color=MUTED))
        else:
            step = bw / (n + 1)
            for k in range(n):
                dx = bx + step * (k + 1)
                f.append(circle(dx, cy, 12, fill=BG, stroke=MUTED, sw=1.5))
                f.append(text(dx, cy + 5, str(k), size=12, color=MUTED, bold=True))
        # запис множинами під клітиною
        f.append(text(cx, cy + 78, st, size=14, color=INK))

    # стрілки наступника між клітинами
    for i in range(3):
        x1 = centers[i] + (60 if tops[i] != "3" else 75) + 6
        x2 = centers[i + 1] - (60 if tops[i + 1] != "3" else 75) - 6
        f.append(arrow(x1, cy, x2, cy, color=FIELD, sw=2.2))
        f.append(text((x1 + x2) / 2, cy - 58, "S", size=14, bold=True, color=FIELD))

    # формула наступника внизу
    box, bw, bh = textbox(W / 2, 328, "наступник:  S(n) = n ∪ { n }   —  докинути в множину саму множину",
                          size=14, fill=GREENFILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(box)

    render(os.path.join(IMG, "von-neumann.svg"), W, H, *f)


# ── 4. Ціна унарного запису: ланцюг комірок проти жмені бітів ─────────────────
def fig_unary_cost():
    W, H = 900, 384
    f = [text(W / 2, 32, "Ціна унарного запису: ланцюг комірок проти жмені бітів",
              size=18, bold=True),
         text(W / 2, 54, "число n у типі Пеано — це n вкладених Succ; те саме число двійкою — лише ⌈log₂n⌉ бітів",
              size=12, color=MUTED, italic=True)]

    # ── Унарна смуга: S→S→S→S→S→Z ──
    f.append(text(W / 2, 92, "Унарно (тип Пеано): щоб записати 5, потрібно 5 комірок Succ",
                  size=13.5, bold=True))
    cells = ["S", "S", "S", "S", "Z"]
    cw, ch, gap = 58, 34, 26
    total = len(cells) * cw + (len(cells) - 1) * gap
    x0, cy = (W - total) / 2, 128
    for i, lab in enumerate(cells):
        x = x0 + i * (cw + gap)
        last = (lab == "Z")
        f.append(rect(x, cy - ch / 2, cw, ch,
                      fill=(GREENFILL if last else REDFILL),
                      stroke=(FIELD if last else POS), sw=1.8, rx=7))
        f.append(text(x + cw / 2, cy + 5, lab, size=16, bold=True,
                      color=(FIELD if last else POS)))
        if i < len(cells) - 1:
            f.append(arrow(x + cw + 4, cy, x + cw + gap - 4, cy, color=INK, sw=1.8))
    f.append(text(W / 2, 172,
                  "S(S(S(S(S(Z)))))  =  5     ·     n комірок у купі на число n     ·     O(n) пам'яті",
                  size=12, color=MUTED, italic=True))

    f.append(line(70, 200, W - 70, 200, color="#dcdfe4", sw=1.2))

    # ── Двійкова смуга: 1 0 1 ──
    f.append(text(W / 2, 230, "Двійково (позиційний запис): те саме 5 — це три біти",
                  size=13.5, bold=True))
    bits = ["1", "0", "1"]
    weights = ["×4", "×2", "×1"]
    bw, bgap = 46, 12
    btot = len(bits) * bw + (len(bits) - 1) * bgap
    bx0, bcy = (W - btot) / 2, 268
    for i, (b, wt) in enumerate(zip(bits, weights)):
        x = bx0 + i * (bw + bgap)
        f.append(rect(x, bcy - ch / 2, bw, ch, fill=BLUEFILL, stroke=NEG, sw=1.8, rx=7))
        f.append(text(x + bw / 2, bcy + 5, b, size=16, bold=True, color=NEG))
        f.append(text(x + bw / 2, bcy + 32, wt, size=10.5, color=MUTED))
    f.append(text(W / 2, 322,
                  "101₂ = 5     ·     ⌈log₂n⌉ біт на число n     ·     O(log n) пам'яті",
                  size=12, color=MUTED, italic=True))

    box, _, _ = textbox(W / 2, 360,
                        "Зберегти 1 000 000: унарно — мільйон комірок; двійково — 20 біт.",
                        size=13, fill=GREENFILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(box)

    render(os.path.join(IMG, "unary-cost.svg"), W, H, *f)


# ── 5. Хроніка аксіоматизації: чотири країни, 28 років (вставка hist) ─────────
def fig_axiom_timeline():
    W, H = 940, 560
    f = [text(W / 2, 34, "Аксіоми Пеано — доробок чотирьох країн за 28 років",
              size=18, bold=True),
         text(W / 2, 56, "хто що додав: від першого рекурсивного означення до переходу на нуль",
              size=12, color=MUTED, italic=True)]

    ys = [120, 214, 308, 402, 496]
    entries = [
        ("1861", "Герман Ґрассман · Німеччина",
         "«Lehrbuch der Arithmetik»: + і × рекурсивно через наступника, закони — індукцією", False),
        ("1881", "Чарлз Сандерс Пірс · США",
         "«On the Logic of Number»: перша повна система аксіом — і роками нею ніхто не переймався", False),
        ("1888", "Ріхард Дедекінд · Німеччина",
         "«Was sind und was sollen die Zahlen?»: ланцюг і категоричність — усі моделі однакові", True),
        ("1889", "Джузеппе Пеано · Італія",
         "«Arithmetices principia»: чіткий список і логічна нотація; почав з 1, визнав борг Дедекінду", True),
        ("1898", "Пеано · «Formulaire»",
         "перше число тепер 0 — звідси й досі розкол «нуль чи одиниця»", False),
    ]

    # хребет-лінія часу
    f.append(line(150, ys[0], 150, ys[-1], color="#cfd4da", sw=2.4))

    for (yr, l1, l2, hot), cy in zip(entries, ys):
        f.append(text(92, cy + 6, yr, size=19, bold=True, color=(NEG if hot else MUTED)))
        f.append(circle(150, cy, 8, fill=(NEG if hot else BG), stroke=NEG, sw=2.2))
        f.append(line(158, cy, 205, cy, color="#cfd4da", sw=1.6))
        cardfill = BLUEFILL if hot else ROW
        cardstroke = NEG if hot else MUTED
        f.append(rect(205, cy - 38, 690, 76, fill=cardfill, stroke=cardstroke,
                      sw=(1.8 if hot else 1.3), rx=9))
        f.append(text(227, cy - 8, l1, size=14, bold=True, anchor="start"))
        f.append(text(227, cy + 16, l2, size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "axiom-timeline.svg"), W, H, *f)


# ── 6. Нуль чи одиниця — дві традиції, не дві істини (вставка hist) ────────────
def fig_zero_vs_one():
    W, H = 900, 380
    f = [text(W / 2, 34, "Нуль чи одиниця — дві традиції, не дві істини", size=18, bold=True),
         text(W / 2, 56, "структура чисел та сама; різниться лише те, як назвати перше",
              size=12, color=MUTED, italic=True)]

    panels = [
        (40, GREENFILL, FIELD, "Починають з 0",
         ["логіка, теорія множин, інформатика",
          "фон Нейман: 0 = ∅ (порожня множина)",
          "Бурбакі й стандарт ISO 80000-2",
          "індекси масивів, залишки, зміщення"]),
        (470, BLUEFILL, NEG, "Починають з 1",
         ["теорія чисел, шкільна традиція",
          "лічба «один, два, три…»",
          "Пеано, «Arithmetices principia» (1889)",
          "натуральне = «додатне ціле»"]),
    ]
    pw, ph, ptop = 390, 210, 84
    for px, hfill, hstroke, htitle, bullets in panels:
        f.append(rect(px, ptop, pw, ph, fill=BG, stroke=hstroke, sw=1.6, rx=10))
        f.append(rect(px, ptop, pw, 42, fill=hfill, stroke=hstroke, sw=1.6, rx=10))
        f.append(rect(px, ptop + 30, pw, 12, fill=hfill, stroke="none", sw=0))
        f.append(text(px + pw / 2, ptop + 27, htitle, size=15, bold=True))
        by = ptop + 68
        for b in bullets:
            f.append(text(px + 20, by, "· " + b, size=13, anchor="start"))
            by += 34

    box, bw, bh = textbox(W / 2, 342,
                          "Це не суперечка про істину, а вибір відправної точки — структура однакова.",
                          size=14, fill=ROW, stroke=MUTED, sw=1.4, bold=True)
    f.append(box)

    render(os.path.join(IMG, "zero-vs-one.svg"), W, H, *f)


# ── 7. Розкручування рекурсії: спуск до бази, тоді збірка (вставка math) ───────
def fig_recursion_descent():
    W, H = 920, 460
    f = [text(W / 2, 32, "Чому рекурсія дає число: спуск до нуля, тоді збірка назад",
              size=18, bold=True),
         text(W / 2, 56, "приклад: обчислюємо 3 + 2 самим означенням",
              size=12, color=MUTED, italic=True)]

    # ── ліворуч: спуск (знімаємо наступник за наступником) ──
    bx_cx, bw, bh = 285, 250, 46
    x0 = bx_cx - bw / 2
    rows = [(104, "3 + 2  =  S(3 + 1)", False),
            (189, "3 + 1  =  S(3 + 0)", False),
            (274, "3 + 0  =  3", True)]
    for yy, s, base in rows:
        f.append(rect(x0, yy, bw, bh, fill=(GREENFILL if base else FILL),
                      stroke=(FIELD if base else LINE), sw=(2.4 if base else 1.5), rx=8))
        f.append(text(bx_cx, yy + bh / 2 + 5, s, size=16, bold=base,
                      color=(FIELD if base else INK)))
    f.append(arrow(bx_cx, 104 + bh + 2, bx_cx, 189 - 2, color=INK, sw=2.0))
    f.append(arrow(bx_cx, 189 + bh + 2, bx_cx, 274 - 2, color=INK, sw=2.0))
    f.append(mtext(92, 176, ["спуск:", "знімаємо", "наступник"], size=12, color=MUTED))
    f.append(text(bx_cx, 274 + bh + 16, "база: додати нуль", size=11, color=FIELD, italic=True))

    # ── праворуч: збірка знизу вгору (значення) ──
    nx = 700
    f.append(node(nx, 297, "3", r=26, fill=FILL))
    f.append(node(nx, 198, "4", r=26, fill=FILL))
    f.append(node(nx, 100, "5", r=26, fill=BLUEFILL, stroke=NEG, tcol=NEG))
    f.append(arrow(nx, 297 - 28, nx, 198 + 28, color=FIELD, sw=2.2))
    f.append(arrow(nx, 198 - 28, nx, 100 + 28, color=FIELD, sw=2.2))
    f.append(text(nx + 44, 252, "4 = S(3)", size=13, color=FIELD, anchor="start"))
    f.append(text(nx + 44, 154, "5 = S(4)", size=13, color=FIELD, anchor="start"))
    f.append(text(nx, 60, "3 + 2 = 5", size=15, bold=True, color=NEG))

    # ── місток дно→старт збірки ──
    f.append(arrow(x0 + bw + 3, 297, nx - 26 - 3, 297, color=MUTED, sw=1.8))
    f.append(text((x0 + bw + nx - 26) / 2, 286, "дно спуску → старт збірки",
                  size=11, color=MUTED, italic=True))

    box, _, _ = textbox(W / 2, 408,
                        "Спуск неминуче впирається в нуль — тож обчислення завершується;\n"
                        "а що воно накриє кожне число, гарантує індукція.",
                        size=13, fill=ROW, stroke=MUTED, sw=1.3)
    f.append(box)
    render(os.path.join(IMG, "recursion-descent.svg"), W, H, *f)


# ── 8. Башта арифметики: означення → леми → закони на опорі індукції (math) ────
def fig_laws_ladder():
    W, H = 940, 450
    f = [text(W / 2, 32, "Арифметика як побудована башта", size=18, bold=True),
         text(W / 2, 56, "кожен закон доводиться з нижчого рівня; наскрізна опора — індукція",
              size=12, color=MUTED, italic=True)]

    # хребет-індукція ліворуч
    f.append(arrow(95, 348, 95, 96, color=FIELD, sw=3.0))
    f.append(text(95, 372, "індукція", size=12, bold=True, color=FIELD))

    def tbox(cx, yy, w, h, title, lines, fill=FILL, stroke=LINE, tcol=INK):
        out = rect(cx - w / 2, yy, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8)
        out += text(cx, yy + 20, title, size=13, bold=True, color=tcol)
        for i, ln in enumerate(lines):
            out += text(cx, yy + 40 + i * 18, ln, size=12.5, color=INK)
        return out

    # рівень 1 — означення (низ)
    d1, d2, dtop, dw, dh = 330, 660, 300, 250, 68
    f.append(tbox(d1, dtop, dw, dh, "означення  +",
                  ["a + 0 = a", "a + S(b) = S(a + b)"], fill=BLUEFILL, stroke=NEG, tcol=NEG))
    f.append(tbox(d2, dtop, dw, dh, "означення  ×",
                  ["a · 0 = 0", "a · S(b) = a·b + a"], fill=BLUEFILL, stroke=NEG, tcol=NEG))
    # рівень 2 — леми
    l1, l2, ltop, lw, lh = 300, 640, 196, 250, 44
    f.append(tbox(l1, ltop, lw, lh, "Лема", ["0 + a = a"], fill=ROW))
    f.append(tbox(l2, ltop, lw, lh, "Лема", ["S(a) + b = S(a + b)"], fill=ROW))
    # рівень 3 — закони (верх)
    a1, a2, a3, atop, aw, ah = 240, 500, 770, 92, 210, 44
    f.append(tbox(a1, atop, aw, ah, "асоціативність +", ["(a+b)+c = a+(b+c)"],
                  fill=GREENFILL, stroke=FIELD, tcol=FIELD))
    f.append(tbox(a2, atop, aw, ah, "комутативність +", ["a + b = b + a"],
                  fill=GREENFILL, stroke=FIELD, tcol=FIELD))
    f.append(tbox(a3, atop, aw, ah, "дистрибутивність", ["a·(b+c) = a·b + a·c"],
                  fill=GREENFILL, stroke=FIELD, tcol=FIELD))

    # стрілки «доводиться з» — лише в проміжках між рівнями, без перетину рамок
    def up(x1, y1, x2, y2):
        return arrow(x1, y1, x2, y2, color=MUTED, sw=1.6)
    f.append(up(d1, dtop - 2, l1, ltop + lh + 2))      # означ.+ → лема 1
    f.append(up(d2, dtop - 2, l2, ltop + lh + 2))      # означ.+ → лема 2
    f.append(up(l1 - 6, ltop - 2, a1 + 30, atop + ah + 2))   # лема 1 → асоц.
    f.append(up(l1 + 10, ltop - 2, a2 - 40, atop + ah + 2))  # лема 1 → комут.
    f.append(up(l2 - 10, ltop - 2, a2 + 40, atop + ah + 2))  # лема 2 → комут.
    f.append(up(l2 + 6, ltop - 2, a3, atop + ah + 2))        # лема 2 → дистриб.
    f.append(text(838, 300, "↑ доводиться з", size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "laws-ladder.svg"), W, H, *f)


# ── 9. Порядок як «дійти від a до b кроками» + лінійність (вставка math) ───────
def fig_order_reach():
    W, H = 900, 430
    f = [text(W / 2, 32, "«a ≤ b» означає: до b можна дійти від a, доклавши кроки",
              size=18, bold=True),
         text(W / 2, 56, "a ≤ b   ⟺   існує c, що a + c = b   (c — відстань по низці наступників)",
              size=12.5, color=MUTED, italic=True)]

    xs = [110 + i * 95 for i in range(8)]
    cy = 185
    ai, bi = 2, 6
    for i in range(7):
        f.append(arrow(xs[i] + 24, cy, xs[i + 1] - 24, cy, color="#c9ced6", sw=1.6))
    for i in range(8):
        if i == ai:
            f.append(node(xs[i], cy, str(i), r=23, fill=GREENFILL, stroke=FIELD, tcol=FIELD))
        elif i == bi:
            f.append(node(xs[i], cy, str(i), r=23, fill=BLUEFILL, stroke=NEG, tcol=NEG))
        else:
            f.append(node(xs[i], cy, str(i), r=21))
    f.append(text(xs[ai], cy + 46, "a", size=15, bold=True, color=FIELD))
    f.append(text(xs[bi], cy + 46, "b", size=15, bold=True, color=NEG))

    # c кроків над низкою
    hy = cy - 54
    for i in range(ai, bi):
        f.append(arrow(xs[i] + 18, hy, xs[i + 1] - 18, hy, color=FIELD, sw=2.2))
    f.append(text((xs[ai] + xs[bi]) / 2, hy - 12, "c = 4 кроки", size=13, bold=True, color=FIELD))
    f.append(line(xs[ai], hy + 6, xs[ai], cy - 24, color=FIELD, sw=1.3, dash="3,3"))
    f.append(line(xs[bi], hy + 6, xs[bi], cy - 24, color=FIELD, sw=1.3, dash="3,3"))

    box, _, _ = textbox(W / 2, 268, "a + c = b   :   2 + 4 = 6   →   a ≤ b",
                        size=15, fill=GREENFILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(box)

    # лінійність
    f.append(line(70, 312, W - 70, 312, color="#dcdfe4", sw=1.2))
    f.append(text(W / 2, 338, "І будь-яка пара чисел порівнянна — порядок лінійний",
                  size=15, bold=True))
    box2, _, _ = textbox(W / 2, 380, "для будь-яких a, b:   a ≤ b   або   b ≤ a",
                         size=15, fill=ROW, stroke=MUTED, sw=1.4, bold=True)
    f.append(box2)
    f.append(text(W / 2, 411, "(жодної непорівнянної пари; доводиться індукцією за b)",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "order-reach.svg"), W, H, *f)


if __name__ == "__main__":
    fig_successor_chain()
    fig_peano_guards()
    fig_von_neumann()
    fig_unary_cost()
    fig_axiom_timeline()
    fig_zero_vs_one()
    fig_recursion_descent()
    fig_laws_ladder()
    fig_order_reach()
    print("OK: successor-chain, peano-guards, von-neumann, unary-cost, axiom-timeline, "
          "zero-vs-one, recursion-descent, laws-ladder, order-reach ->", IMG)
