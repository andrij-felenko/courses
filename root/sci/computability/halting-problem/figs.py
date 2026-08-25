# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: нерівноправність двох відповідей (напіврозв'язність) ───────────────
# Ідея: «спиниться» видно за скінченний час — досить дочекатися зупинки. А «не
# спиниться» — твердження про всю нескінченну майбутню поведінку, і жодне
# скінченне спостереження його не засвідчить. Тому виконання дає лише напівсуддю.
def fig_semidecide_asymmetry():
    W, H = 860, 360
    p = []
    xa = 175.0

    # ── горішній рядок: програма, що спиняється ──
    yt = 118.0
    xs = 470.0                       # точка зупинки
    p.append(text(150, yt + 5, "програма A", size=12.5, color=INK, bold=True, anchor="end"))
    p.append(line(xa, yt, xs, yt, color=INK, sw=1.8))
    for i in range(6):
        gx = xa + (xs - xa) * i / 5
        p.append(line(gx, yt - 5, gx, yt + 5, color=INK, sw=1.3))
        p.append(text(gx, yt + 21, str(i), size=10.5, color=MUTED))
    p.append(circle(xs, yt, 8.5, fill=FIELD, stroke=BG, sw=2.0))
    p.append(text(xs, yt - 15, "спинилась (крок k)", size=12, color=FIELD, bold=True))
    b, bw, bh = textbox(710, yt, "«спиниться» ✓\nдізнаємось", size=12.5, bold=True,
                        fill="#eef7f0", stroke=FIELD, color=FIELD)
    p.append(arrow(xs + 11, yt, 710 - bw / 2 - 8, yt, color=FIELD, sw=1.6))
    p.append(b)

    # ── долішній рядок: програма, що крутиться вічно ──
    yb = 250.0
    xe = 470.0
    p.append(text(150, yb + 5, "програма B", size=12.5, color=INK, bold=True, anchor="end"))
    p.append(line(xa, yb, xe, yb, color=INK, sw=1.8))
    for i in range(6):
        gx = xa + (xe - xa) * i / 5
        p.append(line(gx, yb - 5, gx, yb + 5, color=INK, sw=1.3))
        p.append(text(gx, yb + 21, str(i), size=10.5, color=MUTED))
    # штрихове продовження без кінця + стрілка
    p.append(line(xe, yb, xe + 78, yb, color=POS, sw=1.8, dash="7 6"))
    p.append(arrow(xe + 60, yb, xe + 92, yb, color=POS, sw=1.8))
    p.append(text(xe + 30, yb - 14, "…далі без кінця (∞)", size=11.5, color=POS, anchor="start"))
    b2, bw2, bh2 = textbox(710, yb, "«не спиниться»?\nвирок не настає", size=12.5, bold=True,
                           fill="#f4f6f8", stroke=MUTED, color=INK)
    # пунктирна стрілка «в нікуди» — відповідь так і не приходить
    p.append(line(xe + 96, yb, 710 - bw2 / 2 - 8, yb, color=MUTED, sw=1.4, dash="4 5"))
    p.append(b2)

    render(os.path.join(OUT, "semidecide-asymmetry.svg"), W, H, *p,
           title="Дві відповіді нерівноправні: одну видно, другу — ніколи")


# ── Фіг. 2: доведення від супротивного — машина, що чинить наперекір ───────────
# Ідея: припустимо, суддя halts існує. Будуємо paradox, що робить навпаки вироку
# про саму себе, і питаємо про paradox(paradox). Гілка «спиниться» жене в цикл
# (не спиняється), гілка «не спиниться» — у миттєву зупинку. Обидві суперечать
# вироку — тож правильного вироку немає, а отже, немає й halts.
def fig_paradox_contradiction():
    W, H = 860, 600
    p = []
    cx = 430.0

    # припущений суддя
    b, bw, bh = textbox(cx, 70, "halts(P, x)\nприпущений суддя — завжди правий",
                        size=13, bold=True, fill=FILL, stroke=LINE, color=INK)
    p.append(b)
    p.append(arrow(cx, 70 + bh / 2, cx, 132, color=INK, sw=1.7))

    # збудована пастка
    b, bw, bh = textbox(cx, 160, "paradox(P): робить НАВПАКИ\nвироку halts(P, P)",
                        size=13, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK)
    p.append(b)
    p.append(arrow(cx, 160 + bh / 2, cx, 222, color=INK, sw=1.7))

    # запит
    b, bw, bh = textbox(cx, 250, "запускаємо  paradox(paradox)  —  спиниться?",
                        size=13, bold=True, fill=FILL, stroke=LINE, color=INK)
    p.append(b)

    xL, xR = 218.0, 642.0
    p.append(arrow(cx - 40, 250 + bh / 2, xL + 70, 316, color=INK, sw=1.6))
    p.append(arrow(cx + 40, 250 + bh / 2, xR - 70, 316, color=INK, sw=1.6))

    def column(xc, verdict, behav, actual, vcolor, vfill):
        out = []
        b1, w1, h1 = textbox(xc, 342, verdict, size=12.5, bold=True,
                             fill=vfill, stroke=vcolor, color=vcolor)
        out.append(b1)
        out.append(arrow(xc, 342 + h1 / 2, xc, 406, color=INK, sw=1.5))
        b2, w2, h2 = textbox(xc, 432, behav, size=12.5, bold=True,
                             fill=FILL, stroke=LINE, color=INK)
        out.append(b2)
        out.append(arrow(xc, 432 + h2 / 2, xc, 494, color=INK, sw=1.5))
        b3, w3, h3 = textbox(xc, 520, actual, size=12.5, bold=True,
                             fill="#fdecea", stroke=POS, color=POS)
        out.append(b3)
        return out

    p.extend(column(xL, "halts: «спиниться»",
                    "paradox → while True\nкрутиться вічно",
                    "НЕ спиняється\n— навпаки вироку", NEG, "#eaf0fd"))
    p.extend(column(xR, "halts: «не спиниться»",
                    "paradox → return\nспиняється миттєво",
                    "спиняється\n— навпаки вироку", NEG, "#eaf0fd"))

    # злиття у висновок
    b, bw, bh = textbox(cx, 566, "обидві гілки суперечать вироку  ⟹  halts не існує",
                        size=13.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK)
    p.append(arrow(xL, 520 + 24, cx - bw / 2 - 6, 566, color=MUTED, sw=1.4))
    p.append(arrow(xR, 520 + 24, cx + bw / 2 + 6, 566, color=MUTED, sw=1.4))
    p.append(b)

    render(os.path.join(OUT, "paradox-contradiction.svg"), W, H, *p,
           title="Машина, що чинить наперекір вироку про саму себе")


# ── Фіг. 3: мапа меж — «дорого» це не «неможливо» ─────────────────────────────
# Ідея: три пояси задач. Усередині — швидко розв'язне (P). Ширший пояс — розв'язне,
# але дороге (NP-важке): відповідь є, та чекати її можна астрономічно довго. А за
# суцільною стіною — нерозв'язне: алгоритму нема взагалі, і час тут не зарадить.
def fig_limits_map():
    W, H = 860, 540
    p = []

    # зовнішній пояс — нерозв'язне (товста червона стіна)
    p.append(rect(34, 60, 792, 452, fill="#fdecea", stroke=POS, sw=3.2, rx=16))
    p.append(text(430, 92, "НЕРОЗВ'ЯЗНЕ — алгоритму немає взагалі", size=15, color=POS, bold=True))

    # середній пояс — розв'язне, але дороге
    p.append(rect(140, 182, 580, 262, fill="#fff6e6", stroke="#e08a1e", sw=2.2, rx=14))
    p.append(text(430, 212, "розв'язне, але дороге (NP-важке)", size=13.5, color="#b9700f", bold=True))

    # внутрішній пояс — швидко розв'язне
    p.append(rect(288, 250, 284, 126, fill="#eef7f0", stroke=FIELD, sw=2.0, rx=12))
    p.append(text(430, 282, "швидко розв'язне (P)", size=13, color=FIELD, bold=True))
    p.append(text(430, 316, "сортування", size=12, color=INK))
    p.append(text(430, 340, "найкоротший шлях", size=12, color=INK))

    # приклади в середньому поясі (по боках від внутрішнього)
    def chip(cx, cy, s, fill, stroke):
        b, bw, bh = textbox(cx, cy, s, size=11.5, pad=7, fill=fill, stroke=stroke, color=INK, bold=True)
        return b
    p.append(chip(205, 313, "SAT", "#fbe9cf", "#e08a1e"))
    p.append(chip(645, 313, "комівояжер", "#fbe9cf", "#e08a1e"))

    # приклади в зовнішньому поясі (кути — нерозв'язні задачі)
    p.append(chip(210, 135, "проблема зупинки", "#f9d7d2", POS))
    p.append(chip(636, 135, "чи надрукує «hello»?", "#f9d7d2", POS))
    p.append(chip(214, 476, "еквівалентність програм", "#f9d7d2", POS))
    p.append(chip(632, 476, "теорема Райса", "#f9d7d2", POS))

    # підпис стіни
    p.append(text(430, 500, "суцільна стіна = нерозв'язність: не «дорого», а «неможливо, за будь-який час»",
                  size=11.5, color=POS))

    render(os.path.join(OUT, "limits-map.svg"), W, H, *p,
           title="Мапа меж: розв'язне швидко · розв'язне дорого · нерозв'язне")


# ── Фіг. 4 (hist): хронологія — від Entscheidungsproblem до назви Девіса ───────
# Вертикальна вісь часу: три кольорові фази — Гільбертова мрія (синє), два
# незалежні розв'язки 1936 (червоне), назва від Девіса (зелене).
def fig_hist_timeline():
    W, H = 940, 760
    p = []
    spine_x = 300.0
    y_top, y_bot = 66.0, 712.0
    p.append(line(spine_x, y_top, spine_x, y_bot, color=INK, sw=2.4))

    events = [
        ("1928", "Гільберт і Аккерман, «Grundzüge der\ntheoretischen Logik»: поставлено\nEntscheidungsproblem", NEG, "#eaf0fd"),
        ("вересень 1930", "Кенігсберг: Гільберт — «ми знатимемо»;\nнапередодні Гьодель оголошує\nтеореми про неповноту", NEG, "#eaf0fd"),
        ("15 квітня 1936", "Черч подає «A Note on the\nEntscheidungsproblem» (λ-числення)", POS, "#fdecea"),
        ("28 травня 1936", "Тюрінг подає «On Computable\nNumbers» (машини)", POS, "#fdecea"),
        ("1936–1938", "Тюрінг у Прінстоні; докторат\nпід керівництвом Черча", POS, "#fdecea"),
        ("1952", "Девіс уводить назву «halting problem»\n(лекції, Іллінойс)", FIELD, "#eef7f0"),
        ("1958", "Книга Девіса «Computability and\nUnsolvability» — назва в друці", FIELD, "#eef7f0"),
    ]
    n = len(events)
    y0 = 100.0
    dy = (y_bot - 48 - y0) / (n - 1)
    box_left = 324.0
    for i, (date, desc, col, fill) in enumerate(events):
        cy = y0 + i * dy
        p.append(text(spine_x - 24, cy + 4.5, date, size=12, color=col, bold=True, anchor="end"))
        lines = desc.split("\n")
        tw = max(text_width(ln, 12, False) for ln in lines)
        cx = box_left + (tw + 20) / 2
        b, bw, bh = textbox(cx, cy, desc, size=12, pad=10, fill=fill, stroke=col, color=INK)
        p.append(line(spine_x + 8, cy, box_left, cy, color=MUTED, sw=1.3))
        p.append(b)
        p.append(circle(spine_x, cy, 7.5, fill=col, stroke=BG, sw=2.2))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Хронологія проблеми зупинки (1928–1958)")


# ── Фіг. 5 (hist): те, що довів Тюрінг, — строго вище за «проблему зупинки» ────
# Ідея §7: Тюрінгова задача (circle-free) сидить СТРОГО вище halting в ієрархії
# нерозв'язності: halting зводиться до першого стрибка 0′ (Σ₁), а circle-free —
# до подвійного 0″ (Π₂). Це технічно інша, важча задача.
def fig_circle_free_hierarchy():
    W, H = 880, 476
    p = []
    cx = 496.0

    # вертикальна стрілка «складніша ↑» ліворуч
    ax = 70.0
    p.append(arrow(ax, 406, ax, 96, color=MUTED, sw=1.8))
    p.append(text(ax, 84, "складніша", size=11.5, color=MUTED))

    def rung(cy, s, col, fill):
        b, bw, bh = textbox(cx, cy, s, size=13, pad=12, fill=fill, stroke=col, color=INK,
                            bold=False, min_w=440)
        return b

    p.append(rung(132, "«Circle-free» — задача, яку насправді довів Тюрінг\n"
                        "Π₂-повна · зводиться до 0″ (подвійний стрибок)", POS, "#fdecea"))
    p.append(rung(266, "«Проблема зупинки» — формулювання Девіса\n"
                        "Σ₁-повна · зводиться до 0′ (перший стрибок)", "#b9700f", "#fff6e6"))
    p.append(rung(384, "Розв'язне\nсуддя-алгоритм існує · рівень 0", FIELD, "#eef7f0"))

    # стрілки «строго вище» у проміжках
    p.append(arrow(cx, 352, cx, 300, color=INK, sw=1.7))
    p.append(text(cx + 30, 328, "строго вище", size=11.5, color=INK, anchor="start"))
    p.append(arrow(cx, 232, cx, 166, color=INK, sw=1.7))
    p.append(text(cx + 30, 202, "строго складніша (не halting!)", size=11.5, color=POS, anchor="start"))

    p.append(text(W / 2, 448,
                  "Те, що довів Тюрінг (circle-free), сидить строго вище за «проблему зупинки» — інша, важча задача.",
                  size=11.5, color=INK))

    render(os.path.join(OUT, "circle-free-hierarchy.svg"), W, H, *p,
           title="Чому Тюрінгова задача — не зовсім «проблема зупинки»")


# ── Фіг. (math): зведення A ≤ₘ B — труба для нерозв'язності ────────────────────
# Ідея: обчислюваний перекладач f кладе кожне «так»-запитання про A в «так»-область
# B, а «ні» — у «ні»-область. Тоді конвеєр «f, далі розв'язувач B» був би
# розв'язувачем для A. Якщо A нерозв'язна — розв'язувача B бути не може.
def fig_reduction_mapping():
    W, H = 900, 462
    p = []

    def problem_box(x0, header, sub, top_chip, bot_chip, tcol, tfill, bcol, bfill):
        out = [rect(x0, 60, 250, 232, fill=BG, stroke=LINE, sw=1.6, rx=14)]
        cx = x0 + 125
        out.append(text(cx, 90, header, size=14.5, color=INK, bold=True))
        out.append(text(cx, 110, sub, size=11, color=MUTED))
        b1, _, _ = textbox(cx, 168, top_chip, size=12.5, bold=True,
                           fill=tfill, stroke=tcol, color=tcol)
        b2, _, _ = textbox(cx, 240, bot_chip, size=12.5, bold=True,
                           fill=bfill, stroke=bcol, color=bcol)
        out.append(b1)
        out.append(b2)
        return out

    p.extend(problem_box(70, "Задача A", "відома нерозв'язна",
                         "x ∈ A   (ТАК)", "x ∉ A   (НІ)",
                         FIELD, "#eef7f0", POS, "#fdecea"))
    p.extend(problem_box(580, "Задача B", "доводимо нерозв'язність",
                         "f(x) ∈ B   (ТАК)", "f(x) ∉ B   (НІ)",
                         FIELD, "#eef7f0", POS, "#fdecea"))

    # стрілки перекладу: ТАК→ТАК (зелена), НІ→НІ (червона)
    p.append(arrow(328, 168, 572, 168, color=FIELD, sw=2.0))
    p.append(arrow(328, 240, 572, 240, color=POS, sw=2.0))
    b, bw, bh = textbox(450, 204, "f — обчислюваний\nперекладач запитань",
                        size=11.5, bold=True, fill=FILL, stroke=LINE, color=INK)
    p.append(b)

    p.append(line(70, 316, 830, 316, color="#dfe3e8", sw=1.3))

    # нижній конвеєр: f, далі розв'язувач B → вийшов би розв'язувач A
    yb = 362.0
    b1, w1, _ = textbox(150, yb, "вхід x", size=12, bold=True, fill=FILL, stroke=LINE)
    b2, w2, _ = textbox(342, yb, "порахувати f(x)", size=12, bold=True, fill=FILL, stroke=LINE)
    b3, w3, _ = textbox(562, yb, "розв'язувач B", size=12, bold=True, fill="#eef2fb", stroke=NEG, color=NEG)
    b4, w4, _ = textbox(778, yb, "відповідь:\nx ∈ A ?", size=12, bold=True, fill=FILL, stroke=LINE)
    for bb in (b1, b2, b3, b4):
        p.append(bb)
    p.append(arrow(150 + w1 / 2 + 6, yb, 342 - w2 / 2 - 6, yb, color=INK, sw=1.6))
    p.append(arrow(342 + w2 / 2 + 6, yb, 562 - w3 / 2 - 6, yb, color=INK, sw=1.6))
    p.append(arrow(562 + w3 / 2 + 6, yb, 778 - w4 / 2 - 6, yb, color=INK, sw=1.6))
    p.append(text(450, 430,
                  "Цей конвеєр розв'язав би A. Якщо A нерозв'язна — розв'язувача B, а отже й конвеєра, немає.",
                  size=11.5, color=INK))

    render(os.path.join(OUT, "reduction-mapping.svg"), W, H, *p,
           title="Зведення  A ≤ₘ B:  труба, якою перетікає нерозв'язність")


# ── Фіг. (math): Σ₁ / Π₁ / Δ₁ — розв'язне це перетин ──────────────────────────
# Ідея: напіврозв'язні (Σ₁) і ко-напіврозв'язні (Π₁) овали перетинаються по
# розв'язних (Δ₁). HALT має лише «спиниться» → у Σ₁ поза перетином; co-HALT —
# дзеркально в Π₁. Розв'язне живе лише там, де підтверджувані обидві відповіді.
def fig_decidability_hierarchy():
    W, H = 900, 470
    p = []
    ORNG = "#e08a1e"
    ORNG_D = "#b9700f"

    def ellipse(cx, cy, rx, ry, stroke, fill):
        return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                'fill-opacity="0.10" stroke="%s" stroke-width="2.4"/>'
                % (cx, cy, rx, ry, fill, stroke))

    p.append(ellipse(350, 252, 250, 156, NEG, NEG))
    p.append(ellipse(560, 252, 250, 156, ORNG, ORNG))

    p.append(text(210, 150, "Σ₁ — напіврозв'язні", size=13.5, color=NEG, bold=True))
    p.append(text(700, 150, "Π₁ — ко-напіврозв'язні", size=13.5, color=ORNG_D, bold=True))

    b, _, _ = textbox(205, 268, "HALT\n⟨M,w⟩ спиняється", size=12, bold=True,
                      fill="#eaf0fd", stroke=NEG, color=NEG)
    p.append(b)
    b, _, _ = textbox(705, 268, "co-HALT\nнескінченний цикл", size=12, bold=True,
                      fill="#fff6e6", stroke=ORNG, color=ORNG_D)
    p.append(b)
    b, _, _ = textbox(455, 252, "Δ₁ — розв'язні\nсортування · простота", size=12, bold=True,
                      fill="#eef7f0", stroke=FIELD, color=FIELD)
    p.append(b)

    p.append(text(450, 442,
                  "Мова розв'язна ⟺ і вона, і її доповнення напіврозв'язні. HALT має лише «спиниться» — тож у Σ₁, але поза Δ₁.",
                  size=11.5, color=INK))

    render(os.path.join(OUT, "decidability-hierarchy.svg"), W, H, *p,
           title="Розв'язне — це перетин:  Δ₁ = Σ₁ ∩ Π₁")


# ── Фіг. (proj): спростування будь-якого судді — частина 1 ─────────────────────
# Ідея: хоч що конкретний здогадувач g передбачить про paradox(paradox), машина
# зроблена з g так, щоб зробити навпаки. Три різні g — і кожному paradox робить
# протилежне до вироку: лівий стовпчик щоразу не збігається з правим.
def fig_defeat_ledger():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 52, "paradox будується з судді g — щоб зробити наперекір його вироку",
                  size=12.5, color=MUTED))

    ax0, ax1 = 34, 250          # суддя g
    bx0, bx1 = 258, 512         # пророчить
    cx0, cx1 = 520, 744         # робить насправді
    dx0, dx1 = 752, 866         # вирок
    hy0, hy1 = 74, 116          # заголовковий рядок
    rows = [130, 230, 330]      # верхні краї трьох рядків
    rh = 86

    def cell(x0, x1, y0, h, s, size=12.5, fill=FILL, stroke=LINE, color=INK, bold=False):
        return fitbox(x0, y0, x1 - x0, h, s, size=size, fill=fill, stroke=stroke,
                      color=color, bold=bold, pad=8)

    p.append(cell(ax0, ax1, hy0, hy1 - hy0, "суддя g", fill="#eef1f5", bold=True))
    p.append(cell(bx0, bx1, hy0, hy1 - hy0, "пророчить про paradox(paradox)", fill="#eef1f5", bold=True))
    p.append(cell(cx0, cx1, hy0, hy1 - hy0, "paradox робить насправді", fill="#eef1f5", bold=True))
    p.append(cell(dx0, dx1, hy0, hy1 - hy0, "вирок", fill="#eef1f5", bold=True))

    data = [
        ("always_halts\n(завжди «спиниться»)", "спиниться", FIELD, "#eef7f0",
         "крутиться вічно", NEG, "#eaf0fd"),
        ("always_loops\n(завжди «ні»)", "не спиниться", NEG, "#eaf0fd",
         "спиняється вмить", FIELD, "#eef7f0"),
        ("guess_by_text\n(лякається while True)", "не спиниться", NEG, "#eaf0fd",
         "спиняється вмить", FIELD, "#eef7f0"),
    ]
    for y0, (gname, pred, pcol, pfill, act, acol, afill) in zip(rows, data):
        p.append(cell(ax0, ax1, y0, rh, gname, size=12, bold=True))
        p.append(cell(bx0, bx1, y0, rh, pred, size=13, fill=pfill, stroke=pcol, color=pcol, bold=True))
        p.append(cell(cx0, cx1, y0, rh, act, size=13, fill=afill, stroke=acol, color=acol, bold=True))
        p.append(cell(dx0, dx1, y0, rh, "≠\nбреше", size=12.5, fill="#fdecea", stroke=POS, color=POS, bold=True))

    render(os.path.join(OUT, "defeat-ledger.svg"), W, H, *p,
           title="Хоч який суддя — paradox робить йому наперекір")


# ── Фіг. (proj): надійність проти повноти — три інструменти поруч ──────────────
# Ідея: хто які вироки може виносити. Ідеальний halts заповнив би обидва верхні
# рядки надійно — але його не існує (стовпчик перекреслено). Напівсуддя надійний
# лише на «спиниться». Статичний перевіряльник надійний в обидва боки, та лише на
# вузьких візерунках. Ніхто не жертвує надійністю — усі жертвують повнотою.
def fig_sound_complete_matrix():
    W, H = 940, 470
    p = []

    lx0, lx1 = 26, 196
    cols = [(200, 446), (454, 700), (708, 916)]
    hy0, hy1 = 66, 128
    rows = [136, 246, 356]
    rh = 100

    heads = ["Ідеальний halts\n(не існує)", "Напівсуддя\n(бюджет кроків)", "Статичний\nперевіряльник"]
    rowlabs = ["«спиниться»", "«не спиниться»", "«не знаю»"]

    for y0, lab in zip(rows, rowlabs):
        p.append(fitbox(lx0, y0, lx1 - lx0, rh, lab, size=13, fill=BG, stroke=BG, color=INK, bold=True))
    for (x0, x1), h in zip(cols, heads):
        p.append(fitbox(x0, hy0, x1 - x0, hy1 - hy0, h, size=13, fill="#eef1f5",
                        stroke=LINE, color=INK, bold=True, pad=8))

    G, R, M = "#eef7f0", "#fdecea", "#f4f6f8"
    grid = [
        [("✓ надійно", M, MUTED, MUTED), ("✓ надійно", M, MUTED, MUTED), ("— ніколи", M, MUTED, MUTED)],
        [("✓ надійно", G, FIELD, FIELD), ("✗ ніколи", R, POS, POS), ("часто", M, MUTED, INK)],
        [("✓ але вузько", G, FIELD, FIELD), ("✓ лише тривіальне", G, FIELD, FIELD), ("майже завжди", M, MUTED, INK)],
    ]
    for (x0, x1), col in zip(cols, grid):
        for y0, (s, fill, stroke, color) in zip(rows, col):
            p.append(fitbox(x0, y0, x1 - x0, rh, s, size=13, fill=fill, stroke=stroke,
                            color=color, bold=True, pad=8))

    ix0, ix1 = cols[0]
    iy0, iy1 = hy0, rows[-1] + rh
    p.append(line(ix0 + 6, iy0 + 6, ix1 - 6, iy1 - 6, color=POS, sw=2.4, dash="8 6"))
    p.append(line(ix1 - 6, iy0 + 6, ix0 + 6, iy1 - 6, color=POS, sw=2.4, dash="8 6"))
    b, bw, bh = textbox((ix0 + ix1) / 2, (iy0 + iy1) / 2, "НЕ ІСНУЄ",
                        size=15, bold=True, fill="#fdecea", stroke=POS, color=POS)
    p.append(b)

    p.append(text(W / 2, H - 16,
                  "жоден стовпчик не жертвує надійністю — усі жертвують повнотою, тільки в різні боки",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "sound-complete-matrix.svg"), W, H, *p,
           title="Надійність проти повноти: чого можна досягти без досконалого судді")


if __name__ == "__main__":
    fig_semidecide_asymmetry()
    fig_paradox_contradiction()
    fig_limits_map()
    fig_hist_timeline()
    fig_circle_free_hierarchy()
    fig_reduction_mapping()
    fig_decidability_hierarchy()
    fig_defeat_ledger()
    fig_sound_complete_matrix()
    print("OK figs")
