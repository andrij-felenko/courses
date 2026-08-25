# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: подвоєння проти зростання «на одиницю» — сумарна робота ─────────────
# Ідея: вартість кожного додатка — стовпчик. При подвоєнні місткості дорогі
# копіювання трапляються дедалі рідше (сплески на межах 1,2,4,8…), і вся площа
# (сумарна робота) лишається лінійною ≈2n. При зростанні на одиницю копіює КОЖЕН
# додаток — стовпчики ростуть сходами, площа стає трикутником ≈n²/2. Той самий
# масив, різний коефіцієнт росту: амортизований O(1) проти O(n).
def fig_doubling_vs_linear():
    W, H = 940, 500
    p = []
    n = 16
    # вартість i-го додатка (i=1..16): подвоєння vs +1
    doub = [1, 2, 3, 1, 5, 1, 1, 1, 9, 1, 1, 1, 1, 1, 1, 1]   # спік = копіювання при рості
    lin  = [i + 1 for i in range(n)]                          # 1,2,3,…,16 — щоразу копіює все
    vmax = 16.0
    sum_d, sum_l = sum(doub), sum(lin)

    def panel(px, title, costs, spikes, summary, scolor):
        out = []
        pw, ph = 400.0, 300.0
        py = 66.0
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        out.append(text(px + pw / 2, py + 26, title, size=14, color=INK, bold=True))
        ax, ay = px + 40, py + ph - 52       # низ-ліво осей
        gw, gh = pw - 66, ph - 96            # робоче поле під стовпчики
        # вісь
        out.append(line(ax, ay, ax + gw, ay, color=INK, sw=1.3))
        bw = gw / n * 0.66
        step = gw / n
        for i, c in enumerate(costs):
            bx = ax + step * (i + 0.5) - bw / 2
            bh = gh * c / vmax
            spike = (i + 1) in spikes
            col = POS if spike else "#9fb3c8"
            fill = "#fdecea" if spike else "#e8eef5"
            out.append(rect(bx, ay - bh, bw, bh, fill=fill, stroke=col, sw=1.4, rx=2))
            if spike:
                out.append(text(bx + bw / 2, ay - bh - 7, str(c), size=11, color=POS, bold=True))
        out.append(text(ax + gw / 2, ay + 22, "додатки 1 … 16 →", size=11.5, color=MUTED))
        # підсумок під панеллю
        b, bwd, bhh = textbox(px + pw / 2, py + ph + 34, summary, size=12.5, pad=9,
                              fill="#eef7f0" if scolor == FIELD else "#fdecea",
                              stroke=scolor, color=INK, bold=True)
        out.append(b)
        return out

    p.extend(panel(24, "місткість × 2  (подвоєння)", doub, {2, 3, 5, 9},
                   "сума ≈ 2n  →  O(1) на операцію", FIELD))
    p.extend(panel(516, "місткість + 1  (на одиницю)", lin, set(range(1, n + 1)),
                   "сума ≈ n²/2  →  O(n) на операцію", POS))

    render(os.path.join(OUT, "doubling-vs-linear.svg"), W, H, *p,
           title="Сумарна вартість n додатків: лінія проти квадрата")


# ── Фіг. 2: метод банкіра — баланс кредиту не падає нижче нуля ─────────────────
# Ідея: кожна операція вносить сталу амортизовану плату (3). Дешеві додатки платять
# більше, ніж коштують, і надлишок осідає в кредиті; дорогі копіювання витрачають
# накопичене. Верхня смуга — реальна вартість (стовпчики) і лінія плати = 3.
# Нижня смуга — баланс кредиту: зигзаг, що ПРОВАЛЮЄТЬСЯ на переповненнях, але
# ніколи не стає від'ємним. Отже, стала плата 3 — чесна амортизована межа.
def fig_banker_credit():
    W, H = 920, 520
    p = []
    n = 16
    cost = [1, 2, 3, 1, 5, 1, 1, 1, 9, 1, 1, 1, 1, 1, 1, 1]
    charge = 3
    bal = []
    s = 0
    for c in cost:
        s += charge - c
        bal.append(s)                                   # 2,3,3,5,3,5,7,9,3,…,17

    ax = 118.0
    gw = W - ax - 40
    step = gw / n

    def CX(i):
        return ax + step * (i + 0.5)

    # ── верхня смуга: реальна вартість + лінія плати = 3 ──
    ty0, tyb = 74.0, 250.0                                # верх поля / базова лінія
    cmax = 9.0
    tgh = tyb - ty0 - 8
    p.append(text(ax - 12, 92, "реальна", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ax - 12, 110, "вартість cᵢ", size=12, color=INK, anchor="end"))
    p.append(line(ax, tyb, ax + gw, tyb, color=INK, sw=1.3))
    bw = step * 0.6
    for i, c in enumerate(cost):
        bh = tgh * c / cmax
        spike = c > charge
        p.append(rect(CX(i) - bw / 2, tyb - bh, bw, bh,
                      fill="#fdecea" if spike else "#e8eef5",
                      stroke=POS if spike else "#9fb3c8", sw=1.3, rx=2))
    # лінія амортизованої плати
    yline = tyb - tgh * charge / cmax
    p.append(line(ax, yline, ax + gw, yline, color="#e08a1e", sw=2.0, dash="7 5"))
    p.append(text(ax + gw + 6, yline + 4, "плата = 3", size=11.5, color="#e08a1e",
                  bold=True, anchor="start"))

    # ── нижня смуга: баланс кредиту ──
    by0, byb = 300.0, 452.0                               # верх поля / нуль кредиту
    bmax = 18.0
    bgh = byb - by0
    p.append(text(ax - 12, 372, "кредит", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(ax - 12, 390, "(запас)", size=12, color=NEG, anchor="end"))
    p.append(line(ax, byb, ax + gw, byb, color=FIELD, sw=2.4))          # дно = 0
    p.append(text(ax + gw + 6, byb + 4, "0", size=11.5, color=FIELD, bold=True, anchor="start"))

    def BY(v):
        return byb - bgh * v / bmax

    # площа під лінією балансу
    area = "%.1f,%.1f " % (CX(0), byb)
    area += " ".join("%.1f,%.1f" % (CX(i), BY(v)) for i, v in enumerate(bal))
    area += " %.1f,%.1f" % (CX(n - 1), byb)
    p.append('<polygon points="%s" fill="#eaf0fd" stroke="none"/>' % area)
    pts = " ".join("%.1f,%.1f" % (CX(i), BY(v)) for i, v in enumerate(bal))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, NEG))
    for i, v in enumerate(bal):
        drop = (i > 0 and v < bal[i - 1])
        p.append(circle(CX(i), BY(v), 4.0, fill=POS if drop else NEG, stroke=BG, sw=1.4))
    # позначки провалів на переповненнях
    for i in (4, 8):
        p.append(text(CX(i), BY(bal[i]) + 20, "копіювання\nвитрачає запас".split("\n")[0],
                      size=10, color=POS))
        p.append(text(CX(i), BY(bal[i]) + 33, "витрачає запас", size=10, color=POS))
    p.append(text(ax + gw / 2, byb + 26, "додатки 1 … 16 →", size=11.5, color=MUTED))

    p.append(fitbox(24, 480, W - 48, 32,
                    "баланс кредиту ніколи не від'ємний  ⟹  стала плата 3 покриває всі копіювання: це амортизована межа O(1)",
                    size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "banker-credit.svg"), W, H, *p,
           title="Метод банкіра: дешеві операції наперед платять за дорогі")


# ── Фіг. 3: амортизований ≠ середній випадок ──────────────────────────────────
# Ідея: три різні відповіді на «скільки коштує операція». Найгірший на операцію —
# чесний, але песимістичний. Середній випадок усереднює по РОЗПОДІЛУ входів (є
# ймовірність) — зловмисник із лихими даними його ламає. Амортизований усереднює
# по НАЙГІРШІЙ послідовності (без ймовірності) — тримається для кожного входу.
def fig_amortized_vs_average():
    W, H = 960, 560
    p = []
    lx, lw = 22.0, 150.0
    cols = [(180.0, 246.0), (432.0, 246.0), (684.0, 254.0)]   # (x, w) трьох колонок
    heads = ["Найгірший\nна операцію", "Середній\nвипадок", "Амортизований"]
    hcol = [INK, INK, FIELD]

    # шапка
    hy, hh = 62.0, 58.0
    for (cx, cw), h, hc in zip(cols, heads, hcol):
        p.append(fitbox(cx, hy, cw, hh, h, size=14, bold=True,
                        fill="#eef7f0" if hc == FIELD else "#eef2f8",
                        stroke=hc, color=hc))

    rows = [
        ("усереднює\nпо…",
         [("нічого:\nмаксимум однієї\nоперації", "#eef2f8", INK),
          ("розподілу входів\n(є ймовірність)", "#eef2f8", INK),
          ("операціях однієї\nнайгіршої\nпослідовності", "#eef7f0", FIELD)]),
        ("межа для\nмасиву",
         [("O(n) на додаток\n→ O(n²) на n", "#eef2f8", INK),
          ("— (не про це)", "#f2f4f7", MUTED),
          ("O(1) на додаток\n→ O(n) на n", "#eef7f0", FIELD)]),
        ("зловмисник\nзламає?",
         [("ні, та надто\nпесимістично", "#eef2f8", INK),
          ("ТАК: лихі дані\nвалять оцінку", "#fdecea", POS),
          ("НІ: тримається\nдля кожного входу", "#eef7f0", FIELD)]),
        ("тип\nобіцянки",
         [("гарантія,\nале слабка", "#eef2f8", INK),
          ("ставка на\nймовірність", "#fdecea", POS),
          ("детермінована\nгарантія, тісна", "#eef7f0", FIELD)]),
    ]

    ry = hy + hh + 12
    rh = 84.0
    for label, cells in rows:
        p.append(fitbox(lx, ry, lw, rh, label, size=12, bold=True,
                        fill="#f7f9fb", stroke="#dfe4ea", color=MUTED))
        for (cx, cw), (txt, fill, col) in zip(cols, cells):
            p.append(fitbox(cx, ry, cw, rh, txt, size=12.5, bold=(col in (FIELD, POS)),
                            fill=fill, stroke=col if col in (FIELD, POS) else "#cdd6e0",
                            color=col))
        ry += rh + 10

    p.append(fitbox(22, ry + 4, W - 44, 34,
                    "обидва кажуть «в середньому», та амортизований — про найгіршу послідовність без ймовірності, а не про типовий вхід",
                    size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "amortized-vs-average.svg"), W, H, *p,
           title="Три відповіді на «скільки коштує операція»")


# ── Фіг. 4: часова лінія — як визрівав амортизований аналіз (для hist-вставки) ──
# Ідея: прийом працював задовго до назви. Три струмені — агрегат (Ахо-Гопкрофт-
# Ульман 1974), плата наперед/банкір (Браун-Тар'ян 1980; Гадлстон-Мельгорн
# 1981-82) і метод потенціалу (Слейтор, застосований у splay-деревах 1983) —
# Тар'ян звів у 1985-му в один метод, дав НАЗВУ й поставив потенціал у центр.
# Колір крапки й рамки кодує струмінь; 1985 — червоний вузол-синтез.
def fig_timeline_amortized():
    W, H = 1020, 560
    p = []
    AXY = 300.0
    # (x, year, above?, strand-color, fill, три рядки картки, bold?)
    BLUE, AMBER, GRN, RED = NEG, "#e08a1e", FIELD, POS
    TBLUE, TAMBER, TGRN, TRED = "#eaf0fd", "#fdf0dc", "#eef7f0", "#fdecea"
    ev = [
        (150.0, "1974", True,  BLUE,  TBLUE,  "Ахо·Гопкрофт·Ульман\nагрегат: сума по\nвсій послідовності", False),
        (340.0, "1980", False, AMBER, TAMBER, "Браун·Тар'ян\nплата наперед\nу 2-3 деревах", False),
        (530.0, "1982", True,  AMBER, TAMBER, "Гадлстон·Мельгорн\nте саме, B-дерева;\nкредит — Слейтора", False),
        (720.0, "1983", False, GRN,   TGRN,   "Слейтор·Тар'ян\nsplay-дерева →\nметод потенціалу", False),
        (910.0, "1985", True,  RED,   TRED,   "Тар'ян: НАЗВА,\nсинтез трьох поглядів,\nпотенціал у центрі", True),
    ]
    # вісь часу зі стрілкою
    p.append(arrow(56, AXY, 968, AXY, color=INK, sw=2.0))

    cw, ch = 186.0, 96.0
    for x, yr, above, col, fill, txt, bold in ev:
        big = (yr == "1985")
        if above:
            cy0 = AXY - 38 - ch                       # низ картки на 38 над віссю
            p.append(line(x, AXY - 7, x, AXY - 38, color=col, sw=1.6))
            p.append(text(x, AXY + 26, yr, size=15, color=col, bold=True))
        else:
            cy0 = AXY + 38                            # верх картки на 38 під віссю
            p.append(line(x, AXY + 7, x, AXY + 38, color=col, sw=1.6))
            p.append(text(x, AXY - 14, yr, size=15, color=col, bold=True))
        p.append(fitbox(x - cw / 2, cy0, cw, ch, txt, size=12, pad=9,
                        fill=fill, stroke=col, sw=1.8 if big else 1.3, color=INK, bold=bold))
        p.append(circle(x, AXY, 10 if big else 7, fill=fill, stroke=col, sw=2.4 if big else 1.8))

    # підпис-висновок під лінією
    p.append(fitbox(120, 452, W - 240, 32,
                    "ідея визрівала десятиліття — Тар'ян дав їй ім'я, поставив метод потенціалу в центр і звів усе в один метод",
                    size=12.5, bold=True, fill="#fff6e6", stroke=AMBER, color=INK))

    # легенда струменів
    leg = [(90.0, BLUE, "агрегат (сума по пробігу)"),
           (360.0, AMBER, "плата наперед / банкір"),
           (640.0, GRN, "метод потенціалу"),
           (860.0, RED, "назва + синтез")]
    for lx, col, lab in leg:
        p.append(rect(lx, 500, 15, 15, fill=col, stroke=col, sw=1, rx=3))
        p.append(text(lx + 22, 512, lab, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "timeline-amortized.svg"), W, H, *p,
           title="Три струмені до методу: як визрівав амортизований аналіз")


# ── Фіг. 5: телескопічна сума потенціалів ─────────────────────────────────────
# Ідея: розписати Σaᵢ порядково. У кожному рядку aᵢ = cᵢ + Φ(Dᵢ) − Φ(Dᵢ₋₁).
# Плюс-член Φ(Dᵢ) рядка i й мінус-член −Φ(Dᵢ) рядка i+1 — те саме число з різними
# знаками: вони гасяться (діагональні пунктири). З усієї суми уцілівають лише
# крайні Φ(D₀) (мінус, перший рядок) і Φ(Dₙ) (плюс, останній) — підсвічені зеленим.
def fig_telescope():
    W, H = 720, 450
    p = []
    xL = 58.0          # ліво префікса «aᵢ = cᵢ +»
    xP = 258.0         # колонка плюс-члена Φ(Dᵢ)
    xMinus = 330.0     # знак «−»
    xM = 410.0         # колонка мінус-члена Φ(Dᵢ₋₁)
    rows_y = [98.0, 154.0, 210.0, 266.0]
    subs = ["₁", "₂", "₃", "₄"]
    prev = ["₀", "₁", "₂", "₃"]

    # підкладки під уцілілі крайні члени (ПЕРЕД текстом)
    p.append(rect(xM - 42, rows_y[0] - 19, 84, 31, fill="#eef7f0", stroke=FIELD, sw=1.7, rx=7))
    p.append(rect(xP - 42, rows_y[3] - 19, 84, 31, fill="#eef7f0", stroke=FIELD, sw=1.7, rx=7))

    # діагональні зв'язки скорочення: +Φ(Dᵢ) рядка i ↔ −Φ(Dᵢ) рядка i+1
    for i in range(3):
        p.append(line(xP + 40, rows_y[i] + 7, xM - 50, rows_y[i + 1] - 9,
                      color=MUTED, sw=1.5, dash="4 4"))

    # рядки рівнянь
    for i in range(4):
        y = rows_y[i] + 5
        p.append(text(xL, y, "a%s = c%s  +" % (subs[i], subs[i]), size=16, color=INK, anchor="start"))
        p.append(text(xP, y, "Φ(D%s)" % subs[i], size=16, color=FIELD if i == 3 else INK, bold=(i == 3)))
        p.append(text(xMinus, y, "−", size=16, color=INK))
        p.append(text(xM, y, "Φ(D%s)" % prev[i], size=16, color=FIELD if i == 0 else INK, bold=(i == 0)))

    # примітки у правому/лівому полі, повз текст
    p.append(text(xM + 116, (rows_y[1] + rows_y[2]) / 2 - 4, "внутрішні Φ", size=12.5, color=MUTED, anchor="start"))
    p.append(text(xM + 116, (rows_y[1] + rows_y[2]) / 2 + 13, "гасяться", size=12.5, color=MUTED, anchor="start"))
    # «уцілів» — над/під підсвіченою рамкою крайнього члена, а не збоку в рядку
    # (збоку воно налазило на «aᵢ = cᵢ +» того самого рядка)
    p.append(text(xM, rows_y[0] - 26, "уцілів", size=12.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(xP, rows_y[3] + 32, "уцілів", size=12.5, color=FIELD, anchor="middle", bold=True))

    # підсумок
    b, bw, bh = textbox(W / 2, 340, "Σ aᵢ  =  Σ cᵢ  +  Φ(Dₙ) − Φ(D₀)", size=17,
                        pad=12, fill="#eef7f0", stroke=FIELD, color=INK, bold=True)
    p.append(b)
    p.append(fitbox(40, 388, W - 80, 40,
                    "кожне Φ(Dᵢ) входить у суму двічі — з «+» (рядок i) і з «−» (рядок i+1) — і зникає; уцілівають лише крайні Φ(D₀) та Φ(Dₙ)",
                    size=12.5, color=MUTED, fill=BG, stroke="#dfe4ea"))

    render(os.path.join(OUT, "telescope-sum.svg"), W, H, *p,
           title="Телескопічна сума потенціалів")


# ── Фіг. 6: aᵢ = cᵢ + ΔΦ = 3 — і на переповненні, і на дешевому додатку ────────
# Ідея: дві панелі для масиву з Φ = 2·len − cap. Ліворуч дороге переповнення
# (len=cap=8): реальна вартість cᵢ=9 велика, зате Φ ПАДАЄ з 8 до 2 (на 6) —
# падіння гасить копіювання, лишається aᵢ=3. Праворуч звичайний додаток: cᵢ=1
# мала, Φ РОСТЕ з 4 до 6 (на 2), знову aᵢ=3. Стала амортизована ціна в обох.
def fig_potential_cancel():
    W, H = 880, 470
    p = []
    yb = 336.0          # базова лінія (нуль)
    s = 23.0            # px на одиницю висоти

    def bar(cx, val, label, kind):
        out = []
        bw = 62.0
        top = yb - val * s
        fill = {"pot": "#eaf0fd", "cost": "#fdecea"}[kind]
        strk = {"pot": NEG, "cost": POS}[kind]
        out.append(rect(cx - bw / 2, top, bw, yb - top, fill=fill, stroke=strk, sw=1.6, rx=3))
        out.append(text(cx, top - 9, str(val), size=15, color=strk, bold=True))
        out.append(text(cx, yb + 20, label, size=12.5, color=INK))
        return out, top

    def panel(x0, title, phi_before, cost, phi_after, tint):
        out = []
        pw = 400.0
        out.append(rect(x0, 60, pw, 366, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        out.append(fitbox(x0 + 20, 74, pw - 40, 30, title, size=13.5, bold=True,
                          fill=tint, stroke=FIELD if tint != "#fdecea" else POS, color=INK))
        out.append(line(x0 + 30, yb, x0 + pw - 30, yb, color=INK, sw=1.3))
        b1, t1 = bar(x0 + 92, phi_before, "Φ до", "pot"); out.extend(b1)
        b2, _ = bar(x0 + 200, cost, "cᵢ (реальна)", "cost"); out.extend(b2)
        b3, t3 = bar(x0 + 308, phi_after, "Φ після", "pot"); out.extend(b3)
        # позначка зміни потенціалу над крайніми стовпчиками
        d = phi_after - phi_before
        ay = min(t1, t3) - 32
        out.append(line(x0 + 92, ay, x0 + 308, ay, color=MUTED, sw=1.2, dash="3 3"))

        def vgap(x, y0, y1, num_top, num_bot):
            # вертикальний з'єднувач ay→бар, з розривом навколо підпису значення
            # (число малюється якраз між ay і верхом бару — лінія інакше йде НАСКРІЗЬ нього)
            segs = []
            if y0 < num_top - 2:
                segs.append(line(x, y0, x, min(y1, num_top - 2), color=MUTED, sw=1.2, dash="3 3"))
            if y1 > num_bot + 2:
                segs.append(line(x, max(y0, num_bot + 2), x, y1, color=MUTED, sw=1.2, dash="3 3"))
            return segs

        n1_top, n1_bot = (t1 - 9) - 15 * 0.72, (t1 - 9) + 15 * 0.16
        n3_top, n3_bot = (t3 - 9) - 15 * 0.72, (t3 - 9) + 15 * 0.16
        out.extend(vgap(x0 + 308, ay, t3 - 6, n3_top, n3_bot))
        out.extend(vgap(x0 + 92, ay, t1 - 6, n1_top, n1_bot))
        note = "Φ %s на %d" % ("росте" if d > 0 else "падає", abs(d))
        out.append(fitbox(x0 + 160, ay - 26, 180, 24, note, size=12.5, bold=True,
                          fill=BG, stroke=MUTED, color=NEG))
        # рівняння
        sign = "+" if d > 0 else "−"
        eq = "aᵢ = %d + (%s%d) = 3" % (cost, sign, abs(d))
        out.append(fitbox(x0 + 20, 388, pw - 40, 30, eq, size=13.5, bold=True,
                          fill="#eef7f0", stroke=FIELD, color=INK))
        return out

    p.extend(panel(20, "переповнення (дорого): len = cap = 8", 8, 9, 2, "#fdecea"))
    p.extend(panel(460, "звичайний додаток (дешево)", 4, 1, 6, "#eef7f0"))

    render(os.path.join(OUT, "potential-cancel.svg"), W, H, *p,
           title="aᵢ = cᵢ + ΔΦ = 3 у обох випадках")


# ── Фіг. 7 (proj): копій на додаток — стала смуга O(1) проти прямої O(n) ────────
# Ідея: сумарні копіювання поділити на n для коефіцієнтів росту 2, 1.5 і +1 на
# n від 10² до 10⁶. Геометричні (×2, ×1.5) тримаються в тонкій горизонтальній
# смузі (≈1 і ≈2 копії/додаток) — НЕ залежать від n: це амортизований O(1).
# Зростання «+1» дає (n−1)/2 копій/додаток — пряма, що лізе вгору: O(n). Осі
# логарифмічні, тож стала вартість — горизонталь, лінійна — пряма, що росте.
import math as _math
def fig_growth_copies():
    W, H = 880, 560
    p = []
    x0, y0 = 104.0, 84.0
    pw, ph = 588.0, 372.0
    series = [
        ("× 2",   FIELD, [1.27, 1.023, 1.638, 1.311, 1.049]),
        ("× 1.5", NEG,   [2.84, 2.137, 2.428, 2.765, 2.10]),
        ("+ 1",   POS,   [49.5, 499.5, 5000.0, 50000.0, 500000.0]),
    ]
    def PX(e): return x0 + (e - 2) / 4.0 * pw
    def PY(v): return y0 + ph - _math.log10(v) / 6.0 * ph

    p.append(rect(x0, y0, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    # смуга O(1) (копій/додаток від 1 до ~3.3): дві геометричні лінії живуть тут
    p.append(rect(x0, PY(3.3), pw, PY(1.0) - PY(3.3), fill="#eef7f0", stroke="none"))
    p.append(text(x0 + pw * 0.5, PY(3.05) + 4, "O(1)", size=14, color=FIELD, bold=True, italic=True))
    # горизонтальна сітка й підписи y (10⁰…10⁶)
    ylab = ["1", "10", "10²", "10³", "10⁴", "10⁵", "10⁶"]
    for k in range(7):
        yy = y0 + ph - k / 6.0 * ph
        if k:
            p.append(line(x0, yy, x0 + pw, yy, color="#eef1f5", sw=1))
        p.append(text(x0 - 12, yy + 4, ylab[k], size=12, color=MUTED, anchor="end"))
    # вертикальна сітка й підписи x
    sup = "²³⁴⁵⁶"
    for e in (2, 3, 4, 5, 6):
        p.append(line(PX(e), y0, PX(e), y0 + ph, color="#eef1f5", sw=1))
        p.append(text(PX(e), y0 + ph + 24, "10" + sup[e - 2], size=13, color=MUTED))
    p.append(text(x0 + pw / 2, y0 + ph + 50, "кількість додатків  n  →", size=13.5, color=INK, bold=True))
    p.append(text(x0 - 88, y0 - 30, "копій на додаток (амортизована вартість)", size=12.5, color=INK, anchor="start", bold=True))

    # лінії
    endlab = ["×2  ≈1.05", "×1.5  ≈2.1", "+1  =500000"]
    for (name, col, vals), el in zip(series, endlab):
        pts = " ".join("%.1f,%.1f" % (PX(2 + i), PY(v)) for i, v in enumerate(vals))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, col))
        for i, v in enumerate(vals):
            p.append(circle(PX(2 + i), PY(v), 4.0, fill=col, stroke=BG, sw=1.3))
        p.append(text(PX(6) + 12, PY(vals[-1]) + 4, el, size=12.5, color=col, anchor="start", bold=True))
    # позначка «O(n)» біля прямої +1
    p.append(text(PX(3.4), PY(3000.0), "O(n) — росте з n", size=13, color=POS, italic=True, bold=True, anchor="start"))

    p.append(fitbox(x0, y0 + ph + 62, pw, 30,
                    "×2 і ×1.5 — плоскі: копій на один додаток лишається жменя. «+1» лізе прямо вгору.",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))
    render(os.path.join(OUT, "growth-copies.svg"), W, H, *p,
           title="Копій на додаток: стала O(1) проти лінійної O(n)")


# ── Фіг. 8 (proj): чому коеф. ≤ φ перевикористовує звільнену пам'ять ────────────
# Ідея: при рості старий блок звільняється; чи влізе НАСТУПНИЙ запит у суму вже
# звільнених блоків? Для ×2 звільнене (1+2+4+8=15) завжди рівно на 1 менше за
# наступний запит (16) — новий блок не кладеться в стару діру, верхня межа купи
# лізе вгору. Для ×1.5 звільнене (Σ=38) переростає наступний запит (28) — блок
# лягає в діру, купа не росте. Живий блок, з якого копіюємо (штрихований), у
# діру не рахується — тому точний поріг саме золотий переріз φ≈1.618, а не 2.
def fig_block_reuse():
    W, H = 900, 560
    p = []

    def panel(cy, title, freed_blocks, req, fits, note):
        out = []
        total = sum(freed_blocks)
        span = max(total, req)
        gx, gw = 176.0, 596.0
        unit = gw / span
        rowh = 34.0
        yF = cy                       # ряд «звільнене»
        yR = cy + rowh + 20           # ряд «наступний запит»
        # підпис панелі
        out.append(text(gx - 20, cy - 14, title, size=14, color=INK, anchor="start", bold=True))
        # звільнені блоки (сірі сегменти)
        x = gx
        for b in freed_blocks:
            w = b * unit
            out.append(rect(x, yF, w, rowh, fill="#e3e8ee", stroke="#aab4c0", sw=1.1, rx=2))
            x += w
        out.append(text(gx - 16, yF + rowh / 2 + 4, "звільнено", size=11.5, color=MUTED, anchor="end"))
        out.append(text(gx + total * unit / 2, yF + rowh / 2 + 5,
                        "Σ = %d" % total, size=13, color=INK, bold=True))
        # межа звільненого — вертикаль через обидва ряди
        bx = gx + total * unit
        out.append(line(bx, yF - 8, bx, yR + rowh + 8, color=INK, sw=1.4, dash="5 4"))
        # наступний запит (зелений/червоний за влучанням)
        rw = req * unit
        col = FIELD if fits else POS
        tint = "#eef7f0" if fits else "#fdecea"
        out.append(rect(gx, yR, rw, rowh, fill=tint, stroke=col, sw=1.8, rx=2))
        out.append(text(gx + rw / 2, yR + rowh / 2 + 5, "запит %d" % req, size=13, color=col, bold=True))
        out.append(text(gx - 16, yR + rowh / 2 + 4, "новий блок", size=11.5, color=MUTED, anchor="end"))
        # вердикт праворуч — за правим краєм РЯДКА (а не межі звільненого:
        # коли запит займає всю ширину, підпис межі впритул до «запиту» й
        # накладається на нього — тому фіксована точка gx+gw, завжди поза обома боксами)
        out.append(text(gx + gw + 14, yR + rowh / 2 + 5,
                        ("влазить у діру" if fits else "не влазить"),
                        size=12.5, color=col, anchor="start", bold=True))
        # нотатка під панеллю
        out.append(fitbox(gx, yR + rowh + 18, gw, 28, note, size=12.5,
                          fill=tint, stroke=col, color=INK, bold=True))
        return out

    p.extend(panel(78, "коефіцієнт × 2   (звільнені блоки 1, 2, 4)",
                   [1, 2, 4], 16, False,
                   "звільнено 7 < 16 — новий блок у стару діру не лягає: верхня межа купи тільки росте"))
    p.extend(panel(304, "коефіцієнт × 1.5   (звільнені блоки 1, 2, 3, 4, 6, 9, 13)",
                   [1, 2, 3, 4, 6, 9, 13], 28, True,
                   "звільнено 38 ≥ 28 — новий блок лягає у стару діру: пам'ять перевикористано, купа не росте"))

    p.append(fitbox(56, 500, W - 112, 44,
                    "поріг — золотий переріз φ = (1+√5)/2 ≈ 1.618.  Коеф. ≤ φ → звільнене доганяє наступний запит (перевикористання); коеф. > φ (як 2) → ніколи. Живий блок, з якого копіюємо, у діру не рахується — тому межа саме φ, а не 2.",
                    size=12, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))
    render(os.path.join(OUT, "block-reuse.svg"), W, H, *p,
           title="Чому 1.5 перевикористовує пам'ять, а 2 — ні")


if __name__ == "__main__":
    fig_doubling_vs_linear()
    fig_banker_credit()
    fig_amortized_vs_average()
    fig_timeline_amortized()
    fig_telescope()
    fig_potential_cancel()
    fig_growth_copies()
    fig_block_reuse()
    print("OK figs")
