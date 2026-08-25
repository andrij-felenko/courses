# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: цикл у графі оновлень (двобічна прив'язка двох полів) ──────────
# Два значення живлять одне одного через правило перерахунку. Кожен переказ
# округлює — і поле, яке набрала людина, змінюється саме собою.
def fig_two_way_cycle():
    W, H = 940, 500
    f = []

    # два значення
    b, bw, bh = textbox(180, 120, ["долари", "1234.56"], size=17, pad=18,
                        fill="#eef2ff", stroke=NEG, sw=2.2, min_w=220)
    f.append(b)
    b, bw, bh = textbox(760, 120, ["євро", "1135.80"], size=17, pad=18,
                        fill="#eef2ff", stroke=NEG, sw=2.2, min_w=220)
    f.append(b)

    # стрілка вправо (перерахунок у євро) та її підпис ВИЩЕ за стрілку
    f.append(arrow(300, 106, 640, 106, color=POS, sw=2.2))
    f.append(text(470, 84, "× 0.92 і округлити", size=14, color=POS))
    # стрілка вліво (перерахунок у долари), підпис НИЖЧЕ за стрілку
    f.append(arrow(640, 152, 300, 152, color=POS, sw=2.2))
    f.append(text(470, 180, "÷ 0.92 і округлити", size=14, color=POS))

    f.append(text(470, 232, "кожне значення обчислюється з іншого — це цикл",
                  size=15, color=INK, bold=True))

    # хід «пінг-понгу» з реальними числами
    px, py, pw, ph = 60, 268, 820, 196
    f.append(rect(px, py, pw, ph, fill="#fbfbfd", stroke=MUTED, sw=1.4))
    f.append(text(px + 22, py + 34, "що відбувається після набору 1234.56",
                  size=14, color=MUTED, anchor="start", bold=True))
    f.append(mtext(px + 22, py + 70, [
        "1234.56 × 0.92  =  1135.7952   →   у полі євро   1135.80",
        "1135.80 ÷ 0.92  =  1234.5652   →   у полі долари 1234.57",
        "1234.57 × 0.92  =  1135.8044   →   у полі євро   1135.80   (зупинилось)",
    ], size=14, color=INK, anchor="start", lh=1.55))
    f.append(text(px + 22, py + 172,
                  "набрали 1234.56 — у полі 1234.57: програма переписала введене",
                  size=14, color=POS, anchor="start", bold=True))

    render(os.path.join(IMG, "two-way-cycle.svg"), W, H, *f)


# ── Фігура 2: кільце однонапрямленого потоку ────────────────────────────────
# Цикл нікуди не дівається — але писати в стан має право лише перехід.
def fig_one_way_ring():
    W, H = 1000, 640
    f = []

    b, _, _ = textbox(190, 120, ["Стан", "одна правда"], size=17, pad=16,
                      fill="#eafaf0", stroke=FIELD, sw=2.4, min_w=230)
    f.append(b)
    b, _, _ = textbox(810, 120, ["Подання", "картинка = f(стан)"], size=16, pad=16,
                      fill="#f4f6f8", stroke=LINE, sw=2.0, min_w=230)
    f.append(b)
    b, _, _ = textbox(810, 400, ["Дія", "що саме сталося"], size=16, pad=16,
                      fill="#f4f6f8", stroke=LINE, sw=2.0, min_w=230)
    f.append(b)
    b, _, _ = textbox(190, 400, ["Перехід", "(стан, дія) → стан"], size=16, pad=16,
                      fill="#fdecea", stroke=POS, sw=2.4, min_w=230)
    f.append(b)

    # кільце
    f.append(arrow(315, 120, 685, 120, sw=2.0))
    f.append(text(500, 96, "читає", size=14, color=MUTED))

    f.append(arrow(810, 168, 810, 352, sw=2.0))
    f.append(text(838, 264, "людина натиснула", size=14, color=MUTED, anchor="start"))

    f.append(arrow(685, 400, 315, 400, sw=2.0))
    f.append(text(500, 376, "у чергу дій", size=14, color=MUTED))

    f.append(arrow(190, 352, 190, 172, color=FIELD, sw=2.6))
    f.append(text(162, 264, "новий стан", size=14, color=FIELD, anchor="end", bold=True))

    f.append(mtext(500, 240, ["кільце замкнене — програма ж інтерактивна.",
                              "Але право змінити стан має рівно одна стрілка."],
                   size=15, color=INK, lh=1.5))

    # оболонка з ефектами збоку
    b, _, _ = textbox(500, 560, ["Оболонка: мережа, диск, годинник",
                                 "результат повертається новою дією"],
                      size=14, pad=14, fill="#fbfbfd", stroke=MUTED, sw=1.6, min_w=380)
    f.append(b)
    f.append(arrow(190, 448, 330, 536, color=MUTED, sw=1.8))
    f.append(arrow(670, 536, 810, 448, color=MUTED, sw=1.8))

    render(os.path.join(IMG, "one-way-ring.svg"), W, H, *f)


# ── Фігура 3: ромб і неузгоджена мить ──────────────────────────────────────
# Два похідні значення від одного джерела сходяться в третьому. Порядок
# перерахунку вирішує, чи побачить хтось суміш старого з новим.
def fig_diamond_glitch():
    W, H = 980, 600
    f = []

    b, _, _ = textbox(490, 66, "S — джерело", size=15, pad=14,
                      fill="#eafaf0", stroke=FIELD, sw=2.2, min_w=180)
    f.append(b)
    b, _, _ = textbox(330, 190, "A = S + 1", size=15, pad=14, min_w=170)
    f.append(b)
    b, _, _ = textbox(650, 190, "B = S × 2", size=15, pad=14, min_w=170)
    f.append(b)
    b, _, _ = textbox(490, 314, "C = B − A", size=15, pad=14,
                      fill="#eef2ff", stroke=NEG, sw=2.2, min_w=180)
    f.append(b)

    f.append(arrow(440, 92, 370, 164, sw=1.8))
    f.append(arrow(540, 92, 610, 164, sw=1.8))
    f.append(arrow(370, 216, 440, 288, sw=1.8))
    f.append(arrow(610, 216, 540, 288, sw=1.8))

    # ліва панель — наївне поширення
    lx, ly, lw, lh = 40, 378, 430, 190
    f.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(lx + 20, ly + 32, "перерахунок «як прийшло»", size=14,
                  color=POS, anchor="start", bold=True))
    f.append(mtext(lx + 20, ly + 66, [
        "S: 4 → 5",
        "A = 6,  C = 8 − 6 = 2",
        "B = 10, C = 10 − 6 = 4",
        "мить, коли на екрані 2 — брехня",
    ], size=14, color=INK, anchor="start", lh=1.6))

    # права панель — один прохід у порядку залежностей
    rx_, ry, rw, rh = 510, 378, 430, 190
    f.append(rect(rx_, ry, rw, rh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(rx_ + 20, ry + 32, "один прохід за порядком залежностей",
                  size=14, color=FIELD, anchor="start", bold=True))
    f.append(mtext(rx_ + 20, ry + 66, [
        "S: 4 → 5",
        "A = 6,  B = 10",
        "C = 10 − 6 = 4  (один раз)",
        "проміжної миті не існує",
    ], size=14, color=INK, anchor="start", lh=1.6))

    render(os.path.join(IMG, "diamond-glitch.svg"), W, H, *f)


# ── Фігура 4: вкладені виклики проти плаского циклу з чергою ────────────────
# Ефект відповідає одразу й подає нову дію. Без черги кожен оберт додає кадри
# стека; з чергою дії шикуються в ряд, а глибина стека лишається сталою.
def fig_dispatch_stack_vs_queue():
    W, H = 1020, 600
    f = []

    f.append(text(510, 34, "ефект відповідає одразу й подає нову дію — той самий хід подій двічі",
                  size=15, color=MUTED))

    def panel(px, title, title_color, rows, footer, footer_color):
        out = [rect(px, 90, 460, 380, fill="#fbfbfd", stroke=MUTED, sw=1.4)]
        out.append(text(px + 230, 66, title, size=15, color=title_color, bold=True))
        y = 136
        for indent, s, fill, stroke, color in rows:
            rx0 = px + 18 + indent
            rw = 460 - 36 - indent
            out.append(rect(rx0, y - 20, rw, 40, fill=fill, stroke=stroke, sw=1.4))
            out.append(text(rx0 + 12, y + 5, s, size=13, color=color, anchor="start"))
            y += 56
        out.append(mtext(px + 230, 414, footer, size=12, color=footer_color, lh=1.55))
        return out

    grey = ("#f4f6f8", LINE, INK)
    hot = ("#fdecea", POS, POS)
    cool = ("#eafaf0", FIELD, INK)

    f += panel(40, "без черги: dispatch кличе dispatch", POS, [
        (0,  "dispatch(«оновити курс»)",  *grey),
        (24, "perform(ЗапитКурсу)",        *grey),
        (48, "dispatch(«курс не приїхав»)", *grey),
        (72, "perform(Повторити)",          *grey),
        (96, "dispatch(«оновити курс»)…",   *hot),
    ], ["кожен оберт додає три кадри стека;",
        "через кілька тисяч обертів — падіння,",
        "а в трасуванні тисяча однакових рядків"], POS)

    f += panel(520, "з чергою: dispatch лише стає в ряд", FIELD, [
        (0, "цикл: «оновити курс» → стан, кадр",     *grey),
        (0, "ефект кладе «курс не приїхав» у чергу",  *grey),
        (0, "цикл: «курс не приїхав» → стан, кадр",   *grey),
        (0, "ефект кладе «оновити курс» у чергу",     *grey),
        (0, "цикл: «оновити курс» → … і так далі",    *cool),
    ], ["глибина стека стала;",
        "цикл нікуди не подівся, але його видно",
        "й можна обірвати лічильником дій"], FIELD)

    render(os.path.join(IMG, "dispatch-stack-vs-queue.svg"), W, H, *f)


# ── Фігура 5: журнал дій і рідкі знімки стану ──────────────────────────────
# Чистий перехід дає перемотку: стан після k-ї дії — це знімок плюс дограні
# переходи. Знімки міняють пам'ять на довжину стрибка.
def fig_journal_snapshots():
    W, H = 1000, 320
    f = []

    f.append(text(500, 52, "перемотка історії: журнал дій плюс рідкі знімки",
                  size=16, color=INK, bold=True))

    f.append(text(70, 118, "журнал: n = 1000 дій", size=13, color=MUTED, anchor="start"))
    f.append(text(930, 118, "кружечки — знімки, кожні k = 100", size=13,
                  color=MUTED, anchor="end"))

    f.append(rect(70, 140, 860, 28, fill="#f4f6f8", stroke=MUTED, sw=1.4))
    f.append(line(672, 154, 709, 154, color=POS, sw=7))
    for i in range(11):
        f.append(circle(70 + 86 * i, 154, 6, fill="#eafaf0", stroke=FIELD, sw=2))

    f.append(arrow(709, 176, 709, 206, color=POS, sw=2.0))
    f.append(text(709, 232, "потрібен стан після 743-ї дії", size=13, color=POS))
    f.append(text(500, 276, "беремо знімок 700 і програємо 43 переходи — не 743",
                  size=14, color=INK))

    render(os.path.join(IMG, "journal-snapshots.svg"), W, H, *f)


fig_two_way_cycle()
fig_one_way_ring()
fig_diamond_glitch()
fig_dispatch_stack_vs_queue()
fig_journal_snapshots()
print("ok")


# ── Фігура 4 (вставка hist): родовід ідеї одного напрямку ───────────────────
# Часова смуга не в масштабі: важливий порядок і те, хто в кого позичав.
def fig_hist_lineage():
    W, H = 1200, 540
    f = []
    axis_y = 280
    items = [
        ("1963", "Jack Dennis, MIT", "потокова модель обчислень"),
        ("1976", "мова Lucid", "Ashcroft і Wadge"),
        ("1979", "MVC у Xerox PARC", "Trygve Reenskaug"),
        ("2012", "диплом про Elm", "Evan Czaplicki, Гарвард"),
        ("2014", "Flux на F8", "30 квітня, Jing Chen"),
        ("2015", "Redux", "Abramov і Clark"),
        ("2016", "Elm 0.17", "сигнали прибрано"),
    ]
    f.append(line(60, axis_y, W - 60, axis_y, color=MUTED, sw=2.0))

    xs = [104 + i * 168 for i in range(len(items))]
    for i, (year, head, tail) in enumerate(items):
        x = xs[i]
        above = (i % 2 == 0)
        cy = 160 if above else 400
        col = NEG if i < 3 else POS
        b, bw, bh = textbox(x, cy, [year, head, tail], size=13, pad=12,
                            fill="#fbfbfd", stroke=col, sw=2.0, min_w=160)
        f.append(b)
        y_edge = cy + bh / 2 if above else cy - bh / 2
        f.append(line(x, y_edge, x, axis_y, color=MUTED, sw=1.4, dash="4,4"))
        f.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=1.0))

    f.append(text(60, 44, "коріння: граф обчислень і заборона циклу",
                  size=14, color=NEG, anchor="start", bold=True))
    f.append(text(W - 60, 44, "правило в застосунках",
                  size=14, color=POS, anchor="end", bold=True))
    f.append(text(W / 2, H - 26, "смуга не в масштабі — важить порядок, а не відстань",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "hist-lineage.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): одна подія, три покоління ──────────────────────
# Що саме зникало з ланцюжка від Flux до Redux і Elm.
def fig_hist_generations():
    W, H = 1200, 470
    f = []
    cols = [
        ("Flux, 2014", POS, ["дія (action)", "диспетчер", "кілька сховищ, waitFor",
                             "подання читає сховища"]),
        ("Elm, 2015–2016", FIELD, ["повідомлення (Msg)", "рушій мови",
                                   "update : (Msg, Model) → Model",
                                   "view : Model → Html"]),
        ("Redux, 2015", NEG, ["дія (action)", "диспетчера немає",
                              "один reducer із композиції", "подання читає сховище"]),
    ]
    labels = ["подія", "розподіл", "обчислення стану", "показ"]
    xs = [300, 660, 1020]
    ys = [150, 230, 310, 390]

    for j, lab in enumerate(labels):
        f.append(text(150, ys[j] + 5, lab, size=13, color=MUTED, anchor="end"))

    for i, (title_, col, rows) in enumerate(cols):
        x = xs[i]
        f.append(text(x, 76, title_, size=15, color=col, bold=True))
        for j, r in enumerate(rows):
            b, bw, bh = textbox(x, ys[j], r, size=13, pad=11,
                                fill="#fbfbfd", stroke=col if j == 2 else LINE,
                                sw=2.2 if j == 2 else 1.4, min_w=260)
            f.append(b)
            if j < len(rows) - 1:
                f.append(arrow(x, ys[j] + bh / 2, x, ys[j + 1] - bh / 2,
                               color=MUTED, sw=1.6))

    f.append(text(W / 2, 440, "ланцюжок коротшає, але напрямок стрілок не міняється жодного разу",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "hist-generations.svg"), W, H, *f)


fig_hist_lineage()
fig_hist_generations()


# ── Фігура (вставка math): ланцюжок ромбів і подвоєння перерахунків ─────────
# Кожен ромб подвоює кількість перерахунків наступного вузла: 1, 2, 4, 8…
def fig_cost_chain():
    W, H = 1240, 580
    f = []

    XS = [90, 268, 446, 624, 802, 980, 1158]      # сім колонок
    YX, YA, YB = 190, 96, 284
    MW = 122

    def box(cx, cy, lines, **kw):
        b, w, h = textbox(cx, cy, lines, size=16, pad=12, min_w=MW, **kw)
        f.append(b)
        return w

    box(XS[0], YX, ["x₀", "джерело"], fill="#eafaf0", stroke=FIELD, sw=2.4)
    for k, cx in enumerate([XS[2], XS[4], XS[6]], start=1):
        box(cx, YX, ["x" + "₁₂₃"[k - 1], "×%d" % (2 ** k)],
            fill="#eef2ff", stroke=NEG, sw=2.4)
    for k, cx in enumerate([XS[1], XS[3], XS[5]], start=1):
        box(cx, YA, ["a" + "₁₂₃"[k - 1], "×%d" % (2 ** (k - 1))])
        box(cx, YB, ["b" + "₁₂₃"[k - 1], "×%d" % (2 ** (k - 1))])

    half = MW / 2
    for k in range(3):
        xl, xm, xr = XS[2 * k], XS[2 * k + 1], XS[2 * k + 2]
        f.append(arrow(xl + half, YX - 26, xm - half, YA + 26, sw=1.8))
        f.append(arrow(xl + half, YX + 26, xm - half, YB - 26, sw=1.8))
        f.append(arrow(xm + half, YA + 26, xr - half, YX - 26, sw=1.8))
        f.append(arrow(xm + half, YB - 26, xr - half, YX + 26, sw=1.8))

    f.append(text(624, 380, "aᵢ = xᵢ₋₁ + 1     bᵢ = 2·xᵢ₋₁     xᵢ = bᵢ − aᵢ",
                  size=16, color=INK, bold=True))

    tx, ty, tw, th = 60, 408, 1120, 150
    f.append(rect(tx, ty, tw, th, fill="#fbfbfd", stroke=MUTED, sw=1.4))
    cols = [190, 520, 810, 1060]
    heads = ["ромбів n", "перерахунків стоку 2ⁿ", "вузлів 3n+1", "ребер 4n"]
    for cx, s in zip(cols, heads):
        f.append(text(cx, ty + 36, s, size=14, color=MUTED, bold=True))
    rows = [("3", "8", "10", "12"), ("10", "1 024", "31", "40"),
            ("20", "1 048 576", "61", "80")]
    for r, row in enumerate(rows):
        yy = ty + 72 + r * 28
        for cx, s in zip(cols, row):
            f.append(text(cx, yy, s, size=15,
                          color=POS if cx == cols[1] else INK,
                          bold=(cx == cols[1])))

    render(os.path.join(IMG, "cost-chain.svg"), W, H, *f)


# ── Фігура (вставка math): сходинка ⌈⌈0.8u⌉/0.8⌉ і нерухомі точки ───────────
# Відображення ніколи не спускається нижче діагоналі, тож послідовність
# може тільки рости — і спиняється рівно на кратному п'яти.
def fig_ceil_staircase():
    import math as _m
    W, H = 940, 640
    f = []
    OX, OY, STEP = 100, 540, 58
    LO, HI = 10, 17

    def px(u): return OX + (u - LO) * STEP
    def py(v): return OY - (v - LO) * STEP

    def Fu(u):
        e = _m.ceil(u * 4 / 5)
        return _m.ceil(e * 5 / 4)

    for u in range(LO, HI + 1):
        f.append(line(px(u), py(LO), px(u), py(HI), color="#e5e7eb", sw=1.0))
        f.append(line(px(LO), py(u), px(HI), py(u), color="#e5e7eb", sw=1.0))
        f.append(text(px(u), OY + 28, str(u), size=13, color=MUTED))
        f.append(text(OX - 24, py(u) + 5, str(u), size=13, color=MUTED))
    f.append(line(px(LO), py(LO), px(HI), py(LO), color=LINE, sw=1.6))
    f.append(line(px(LO), py(LO), px(LO), py(HI), color=LINE, sw=1.6))
    f.append(text(px(HI) - 30, OY + 58, "u — долари", size=14, color=INK))
    f.append(text(OX - 48, py(HI) - 22, "F(u)", size=14, color=INK, anchor="start"))

    f.append(line(px(LO), py(LO), px(HI), py(HI), color=MUTED, sw=1.6, dash="6 5"))

    for u in range(LO, HI):
        v = Fu(u)
        fixed = (v == u)
        col = FIELD if fixed else NEG
        f.append(circle(px(u), py(v), 7, fill=col, stroke=col, sw=2))

    for u in range(11, 15):
        v = Fu(u)
        f.append(arrow(px(u), py(u), px(u), py(v), color=POS, sw=2.2))
        f.append(arrow(px(u), py(v), px(v), py(v), color=POS, sw=2.2))

    f.append(text(px(11) + 34, py(10) - 16, "старт 11", size=13, color=POS, anchor="start"))
    f.append(text(px(15) + 14, py(15) + 5, "15", size=13, color=FIELD, anchor="start", bold=True))

    lx, ly, lw, lh = 620, 130, 300, 270
    f.append(rect(lx, ly, lw, lh, fill="#fbfbfd", stroke=MUTED, sw=1.4))
    f.append(mtext(lx + 20, ly + 38, [
        "курс r = 0.8, обидва",
        "перекази округлюють",
        "угору:",
        "",
        "F(u) = ⌈⌈0.8·u⌉ / 0.8⌉",
        "",
        "точок нижче діагоналі",
        "немає: F(u) ≥ u завжди,",
        "тож коло може тільки",
        "рости або спинитись",
    ], size=14, color=INK, anchor="start", lh=1.5))

    render(os.path.join(IMG, "ceil-staircase.svg"), W, H, *f)


fig_cost_chain()
fig_ceil_staircase()
