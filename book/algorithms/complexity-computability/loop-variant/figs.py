# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: строго спадний, обмежений знизу варіант мусить дійти до дна ─────────
# Ідея: величина, що падає щонайменше на одиницю щопрохід і не може впасти нижче
# нуля, дістає дна за скінченне число кроків. Це і є вся механіка завершуваності:
# «немає нескінченного спуску» серед невід'ємних цілих.
def fig_variant_descent():
    W, H = 720, 430
    p = []
    ox, oy = 95.0, 340.0          # початок осей (лівий низ, дно = 0)
    pw, ph = 545.0, 250.0         # робоче поле над дном
    vals = [12, 9, 7, 4, 2, 1, 0] # строго спадний варіант, що дійшов до дна
    vmax = 12
    n = len(vals)

    def X(i):
        return ox + pw * i / (n - 1)

    def Y(v):
        return oy - (ph - 30) * v / vmax

    # зелене дно (обмеження знизу) — товста лінія на рівні нуля
    p.append(line(ox - 10, oy, ox + pw + 20, oy, color=FIELD, sw=3.0))
    p.append(text(ox + pw + 26, oy + 4, "дно = 0", size=12, color=FIELD, bold=True, anchor="start"))
    # вісь варіанта
    p.append(line(ox, oy + 6, ox, Y(vmax) - 18, color=INK, sw=1.4))

    # тонкі напрямні до дна + значення
    for i, v in enumerate(vals):
        gx, gy = X(i), Y(v)
        p.append(line(gx, gy, gx, oy, color="#e2e6ec", sw=1.0))

    # ламана спуску
    pts = " ".join("%.1f,%.1f" % (X(i), Y(v)) for i, v in enumerate(vals))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, NEG))

    # точки + підписи значень
    for i, v in enumerate(vals):
        gx, gy = X(i), Y(v)
        col = FIELD if v == 0 else NEG
        p.append(circle(gx, gy, 5.0, fill=col, stroke=BG, sw=1.6))
        p.append(text(gx, gy - 12, str(v), size=12, color=INK, bold=True))
        p.append(text(gx, oy + 20, str(i), size=11, color=MUTED))

    # величини спаду між сусідніми кроками (сині «−k» під ламаною)
    for i in range(n - 1):
        d = vals[i] - vals[i + 1]
        mx = (X(i) + X(i + 1)) / 2
        my = (Y(vals[i]) + Y(vals[i + 1])) / 2 + 16
        p.append(text(mx, my, "−%d" % d, size=10.5, color=NEG))

    p.append(text(ox + pw / 2, oy + 44, "ітерації циклу", size=12, color=INK))

    # точка зупинки
    p.append(text(X(n - 1), Y(0) - 30, "цикл спиняється", size=11, color=FIELD, bold=True))

    # висновок у рамці (праворуч угорі, з запасом)
    b, bw, bh = textbox(ox + pw - 132, Y(vmax) + 20,
                        "строго вниз щопрохід\n+ є дно знизу\n⟹ кроків скінченно",
                        size=12, bold=True, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "variant-descent.svg"), W, H, *p,
           title="Варіант: спадає до дна — отже, цикл спиниться")


# ── Фіг. 2: інваріант і варіант — дві половини доведення циклу ─────────────────
# Ідея: інваріант лишається ІСТИННИМ на кожному проході (результат буде правильний,
# якщо цикл спиниться) — це часткова коректність. Варіант СПАДАЄ до дна (цикл таки
# спиниться) — це завершуваність. Разом вони дають повну коректність.
def fig_invariant_vs_variant():
    W, H = 780, 450
    p = []

    def panel(px, title, sub, kind):
        out = []
        pw, ph = 300.0, 150.0
        py = 80.0
        ax, ay = px + 40, py + ph - 24     # нижній лівий кут графіка
        gw, gh = pw - 70, ph - 48
        out.append(rect(px, py - 30, pw, ph + 66, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        out.append(text(px + pw / 2, py - 8, title, size=13, color=INK, bold=True))
        # вісь
        out.append(line(ax, ay, ax + gw, ay, color=INK, sw=1.2))
        out.append(line(ax, ay, ax, ay - gh, color=INK, sw=1.2))
        nlab = 5
        if kind == "inv":
            # рівна лінія — «істинно» на кожному кроці
            yv = ay - gh * 0.62
            out.append(line(ax, yv, ax + gw, yv, color=FIELD, sw=2.6))
            for i in range(nlab):
                gx = ax + gw * i / (nlab - 1)
                out.append(circle(gx, yv, 4.2, fill=FIELD, stroke=BG, sw=1.4))
                out.append(text(gx, ay - gh - 6, "✓", size=11, color=FIELD))
        else:
            # спадна лінія до дна
            ys = [0.95, 0.72, 0.5, 0.28, 0.0]
            out.append(line(ax, ay, ax + gw, ay, color=FIELD, sw=2.4))  # дно
            pts = " ".join("%.1f,%.1f" % (ax + gw * i / (nlab - 1), ay - gh * ys[i]) for i in range(nlab))
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, NEG))
            for i in range(nlab):
                gx = ax + gw * i / (nlab - 1)
                out.append(circle(gx, ay - gh * ys[i], 4.2, fill=(FIELD if ys[i] == 0 else NEG), stroke=BG, sw=1.4))
        out.append(text(px + pw / 2, py + ph + 30, sub, size=11, color=MUTED))
        return out, px + pw / 2, py + ph + 46

    a, cxl, byl = panel(40, "Інваріант — лишається істинним",
                        "правильний результат, ЯКЩО спинився", "inv")
    b, cxr, byr = panel(440, "Варіант — строго спадає до дна",
                        "цикл неодмінно спиниться", "var")
    p.extend(a)
    p.extend(b)

    # підписи-містки під панелями
    p.append(text(cxl, byl, "часткова коректність", size=12, color=FIELD, bold=True))
    p.append(text(cxr, byr, "завершуваність", size=12, color=NEG, bold=True))

    # зведення внизу
    bx, by, bwd = 210.0, 400.0, 360.0
    p.append(arrow(cxl, byl + 8, bx + 80, by - 6, color=MUTED, sw=1.4))
    p.append(arrow(cxr, byr + 8, bx + bwd - 80, by - 6, color=MUTED, sw=1.4))
    box = fitbox(bx, by, bwd, 34, "разом  =  ПОВНА КОРЕКТНІСТЬ", size=13, bold=True,
                 fill="#fff6e6", stroke="#e08a1e", color=INK)
    p.append(box)

    render(os.path.join(OUT, "invariant-vs-variant.svg"), W, H, *p,
           title="Дві половини доведення циклу")


# ── Фіг. 3: словниковий (лексикографічний) варіант ────────────────────────────
# Ідея: коли жоден лічильник поодинці не спадає весь час, спадає ПАРА (x, y) за
# словниковим порядком: спершу дивимось на x, при рівних — на y. На межі внутрішній
# y стрибає вгору, зате зовнішній x падає — пара все одно нижча. Нескінченного
# спуску нема й тут.
def fig_lexico_descent():
    W, H = 760, 470
    p = []
    # решітка: колонки — x (3,2,1,0 зліва направо), рядки — y (0..4 знизу вгору)
    xs = [3, 2, 1, 0]
    ymax = 4
    ox, oy = 130.0, 360.0     # низ-ліво (y=0, x=3)
    cw, rh = 150.0, 66.0

    def PX(xi):
        return ox + xs.index(xi) * cw

    def PY(y):
        return oy - y * rh

    # вузли решітки
    for xi in xs:
        p.append(text(PX(xi), oy + 34, "x=%d" % xi, size=12, color=INK, bold=True))
        for y in range(ymax + 1):
            gx, gy = PX(xi), PY(y)
            p.append(circle(gx, gy, 3.4, fill="#d7dde5", stroke="#c2cad4", sw=1.0))
    for y in range(ymax + 1):
        p.append(text(ox - 34, PY(y) + 4, "y=%d" % y, size=11, color=MUTED, anchor="end"))

    # шлях спуску за словниковим порядком
    path = [(3, 2), (3, 1), (3, 0), (2, 4), (2, 3), (2, 2), (2, 1), (2, 0),
            (1, 3), (1, 2), (1, 1), (1, 0), (0, 1), (0, 0)]
    for i in range(len(path) - 1):
        (x1, y1), (x2, y2) = path[i], path[i + 1]
        reset = x2 != x1           # перехід у нову колонку: y стрибає вгору, x падає
        col = POS if reset else NEG
        p.append(arrow(PX(x1), PY(y1), PX(x2), PY(y2), color=col, sw=2.0))
    for (x, y) in path:
        p.append(circle(PX(x), PY(y), 5.2, fill=INK, stroke=BG, sw=1.5))
    # старт і фініш
    sx, sy = path[0]
    fx, fy = path[-1]
    p.append(text(PX(sx) + 12, PY(sy) - 8, "старт", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(PX(fx) + 12, PY(fy) - 8, "кінець", size=11, color=FIELD, bold=True, anchor="start"))

    # пояснення червоної межі (з запасом, ліворуч від решітки)
    b1, w1, h1 = textbox(ox + 1.5 * cw, PY(4) - 34,
                         "межа: y стрибає вгору,\nАЛЕ x падає — пара нижча",
                         size=11, bold=True, fill="#fdecea", stroke=POS)
    p.append(b1)

    # означення словникового порядку внизу
    box = fitbox(ox - 34, oy + 54, cw * 3 + 68, 34,
                 "(a, b) < (c, d)   ⟺   a < c,   або  a = c і b < d",
                 size=12.5, bold=True, fill="#eef2f8", stroke=INK)
    p.append(box)

    render(os.path.join(OUT, "lexico-descent.svg"), W, H, *p,
           title="Коли одного лічильника мало: словниковий варіант (x, y)")


# ══ Фігури вставки math-well-founded.md ═══════════════════════════════════════

# ── Фіг. 4: що НАСПРАВДІ робить роботу — не «дно», а фундованість ─────────────
# Ідея: «строго спадає + обмежена знизу» саме по собі НЕ доводить нічого — у ℚ⁺
# ланцюг 1 > 1/2 > 1/4 > … строго спадний і обмежений нулем, та нескінченний.
# Працює лише фундованість порядку: немає нескінченного строго спадного ланцюга.
def fig_wf_or_not():
    W, H = 900, 610
    p = []

    def chain_row(cx_center, cy, labels, ok, size=12, pad=7, gap=26):
        ws = [text_width(l, size, True) + 2 * pad for l in labels]
        total = sum(ws) + gap * (len(labels) - 1)
        x = cx_center - total / 2
        out = []
        for i, lab in enumerate(labels):
            w = ws[i]
            last = (i == len(labels) - 1)
            bottom = ok and last
            b, bw, bh = textbox(x + w / 2, cy, lab, size=size, pad=pad,
                                fill=("#eef7f0" if bottom else "#eef2f8"),
                                stroke=(FIELD if bottom else "#aab4c0"),
                                color=(FIELD if bottom else INK), bold=True)
            out.append(b)
            if not last:
                out.append(arrow(x + w + 5, cy, x + w + gap - 5, cy, color=MUTED, sw=1.3))
            x += w + gap
        return out

    def panel(px, py, title, chain, ok, verdict, note):
        pw, ph = 420.0, 230.0
        out = [rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10)]
        out.append(text(px + pw / 2, py + 28, title, size=14, color=INK, bold=True))
        out.extend(chain_row(px + pw / 2, py + 82, chain, ok))
        b, bw, bh = textbox(px + pw / 2, py + 152, verdict, size=12, pad=9,
                            fill=("#eef7f0" if ok else "#fdecea"),
                            stroke=(FIELD if ok else POS),
                            color=(FIELD if ok else POS), bold=True)
        out.append(b)
        out.append(text(px + pw / 2, py + 205, note, size=11.5, color=MUTED))
        return out

    p.extend(panel(20, 56, "(ℕ, <)  —  натуральні",
                   ["5", "4", "3", "2", "1", "0"], True,
                   "ФУНДОВАНЕ\nспуск обривається на дні",
                   "кожен крок униз — не менш як на 1"))
    p.extend(panel(460, 56, "(ℤ, <)  —  цілі",
                   ["2", "1", "0", "−1", "−2", "…"], False,
                   "НЕ ФУНДОВАНЕ\nдна немає взагалі",
                   "0 > −1 > −2 > … — і так вічно"))
    p.extend(panel(20, 316, "(ℚ⁺, <)  —  додатні дроби",
                   ["1", "1/2", "1/4", "1/8", "…"], False,
                   "НЕ ФУНДОВАНЕ\nдно (0) є, але недосяжне",
                   "«обмежена знизу» НЕ рятує!"))
    p.extend(panel(460, 316, "(ℕ×ℕ, словниковий)  —  пари",
                   ["(2,1)", "(2,0)", "(1,9)", "…", "(0,0)"], True,
                   "ФУНДОВАНЕ\nце порядок ω² — спуску теж немає",
                   "фундованість ≠ «бути одним числом»"))

    p.append(fitbox(20, 560, 860, 36,
                    "працює не «є дно», а ФУНДОВАНІСТЬ: у порядку немає нескінченного строго спадного ланцюга",
                    size=13, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "wf-or-not.svg"), W, H, *p,
           title="Що насправді доводить зупинку")


# ── Фіг. 5: драбина ординалів — де живе кожен варіант і де стіна PA ───────────
# Ідея: ординали — нормальна форма всіх цілком упорядкованих варіантів. Звичайний
# лічильник живе в ℕ, пара за словниковим порядком — це вже ω², Ґудштейн вимагає
# усього ε₀. Peano-арифметика доводить фундованість кожного α < ε₀, але не ε₀.
def fig_ordinal_ladder():
    W, H = 940, 620
    p = []
    ax = 62.0                       # вісь «сила варіанта»
    lx, lw = 96.0, 232.0            # колонка рунґів
    tx = 352.0                      # початок пояснень

    rungs = [
        (110.0, "ε₀ = ω^ω^ω^···",
         "Ґудштейн, гідра Кірбі-Періса:", "варіант існує, але PA його не доводить"),
        (222.0, "ω^ω",
         "кортежі змінної довжини, мультимножини", "(порядок Дершовіца-Манни, 1979)"),
        (334.0, "ω·ω = ω²",
         "пара (x, y) за словниковим порядком;", "функція Аккермана — (m, n) вниз"),
        (446.0, "ω",
         "необмежений недетермінізм: кроків", "скінченно, але межі в ℕ немає"),
        (546.0, "0, 1, 2, 3, …   (ℕ)",
         "звичайний лічильник: b в Евкліда,", "hi − lo у двійковому пошуку"),
    ]

    # вісь зростання сили
    p.append(arrow(ax, 580, ax, 84, color=INK, sw=1.6))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12" fill="%s" text-anchor="middle">%s</text>'
             % (ax - 16, 330, FONT, MUTED, esc("сила варіанта зростає")))

    for (y, lab, l1, l2) in rungs:
        top = lab.startswith("ε₀")
        p.append(fitbox(lx, y - 21, lw, 42, lab, size=15, bold=True,
                        fill=("#f3ecfb" if top else "#eef2f8"),
                        stroke=("#7c4dbe" if top else INK),
                        color=("#7c4dbe" if top else INK)))
        p.append(line(lx + lw, y, tx - 12, y, color="#dfe4ea", sw=1.2))
        p.append(text(tx, y - 6, l1, size=12.5, color=INK, anchor="start"))
        p.append(text(tx, y + 13, l2, size=12.5, color=MUTED, anchor="start"))

    # стіна Peano-арифметики — між ω^ω і ε₀
    wy = 166.0
    bcx = W / 2 + 40
    b, bw, bh = textbox(bcx, wy, "межа Peano-арифметики: доводить фундованість "
                        "КОЖНОГО α < ε₀ (Ґентцен, 1943) — але не самого ε₀",
                        size=11.5, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    # лінія стіни йде ПОВЗ підпис — переривається обабіч рамки, не крізь неї
    gap = bw / 2 + 10
    p.append(line(ax - 12, wy, bcx - gap, wy, color=POS, sw=2.0, dash="8 5"))
    p.append(line(bcx + gap, wy, W - 24, wy, color=POS, sw=2.0, dash="8 5"))
    p.append(b)

    p.append(fitbox(24, 578, W - 48, 32,
                    "кожна цілком упорядкована множина ізоморфна рівно одному ординалу "
                    "— тож ординал і є нормальна форма варіанта",
                    size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "ordinal-ladder.svg"), W, H, *p,
           title="Драбина ординалів: де живе який варіант")


# ── Фіг. 6: Ґудштейн — число вибухає, ординал спадає ─────────────────────────
# Ідея: підняття основи ординал НЕ бачить (b всюди замінено на ω — вираз той самий),
# а «−1» бачить завжди. Тому число росте як завгодно, а ординал мусить спадати —
# і саме спадання ординала (а не числа) робить послідовність скінченною.
def fig_goodstein_tracks():
    W, H = 940, 500
    p = []
    gut = 116.0                       # гутер під підписи рядків
    x0, xw = 124.0, (W - 124.0 - 20.0) / 7.0

    bases = ["2", "3", "4", "5", "6", "7", "…"]
    nums = ["4", "26", "41", "60", "83", "109", "…"]
    ords = ["ω^ω", "ω²·2+ω·2+2", "ω²·2+ω·2+1", "ω²·2+ω·2", "ω²·2+ω+5", "ω²·2+ω+4", "…"]

    def CX(i):
        return x0 + xw * (i + 0.5)

    # рядок основ
    p.append(text(gut - 10, 68, "основа b", size=12, color=MUTED, anchor="end"))
    for i, b in enumerate(bases):
        p.append(text(CX(i), 68, b, size=13, color=INK, bold=True))

    # рядок чисел — вибухає
    p.append(text(gut - 10, 116, "число G₄", size=12.5, color=POS, anchor="end", bold=True))
    p.append(text(gut - 10, 134, "↑ вибухає", size=11.5, color=POS, anchor="end"))
    for i, v in enumerate(nums):
        b, bw, bh = textbox(CX(i), 124, v, size=13, pad=8,
                            fill="#fdecea", stroke=POS, color=INK, bold=True)
        p.append(b)

    # центральна теза
    b, bw, bh = textbox(W / 2, 218,
                        "підняття основи b → b+1 ординал НЕ БАЧИТЬ: в обох записах основа замінена на ω —\n"
                        "вираз лишається той самий. А «−1» ординал бачить ЗАВЖДИ — і мусить упасти.",
                        size=13, pad=12, fill="#eef2f8", stroke=INK, bold=True)
    p.append(b)

    # рядок ординалів — спадає
    p.append(text(gut - 10, 318, "паралельний", size=12.5, color=NEG, anchor="end", bold=True))
    p.append(text(gut - 10, 336, "ординал ↓ спадає", size=11.5, color=NEG, anchor="end"))
    for i, v in enumerate(ords):
        b, bw, bh = textbox(CX(i), 326, v, size=11.5, pad=7,
                            fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
        p.append(b)

    # стрілки спаду під ординалами
    for i in range(len(ords) - 1):
        p.append(arrow(CX(i) + 30, 366, CX(i + 1) - 30, 366, color=NEG, sw=1.3))
    p.append(text(W / 2, 392, "строго вниз на кожному кроці — а ординали фундовані", size=12, color=NEG))

    p.append(fitbox(24, 424, W - 48, 34,
                    "G₄ доростає до 3·2⁴⁰²⁶⁵³²¹⁰ − 1 — і все одно доходить до нуля: "
                    "скінченність доводить ординал, а не число",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "goodstein-tracks.svg"), W, H, *p,
           title="Ґудштейн: число вгору, ординал униз")


# ══ Фігури вставки proj-variant-bounds.md ═════════════════════════════════════

# ── Фіг. 7: обернене питання — будуємо найдешевший прогін назад від дна ───────
# Ідея: «як швидко падає v?» часто без відповіді — спад залежить від усього стану,
# а не від самого v. Обернене питання відповідь має завжди: яким МУСИТЬ бути старт,
# щоб вистачило на k кроків? Найдешевший прогін будуємо назад від дна; W(k) росте,
# і межа на кроки — просто обернена до W.
def fig_inverted_question():
    W, H = 990, 560
    p = []

    # ── ліва панель: драбина назад ──
    p.append(rect(24, 56, 420, 452, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(234, 84, "Будуємо найдешевший прогін НАЗАД", size=13, color=INK, bold=True))

    rungs = [(462.0, "дно: v = 0", True), (392.0, "W(1)", False), (322.0, "W(2)", False),
             (252.0, "W(3)", False), (182.0, "W(4)", False)]
    for (y, lab, bottom) in rungs:
        p.append(fitbox(74, y - 20, 132, 40, lab, size=14, bold=True,
                        fill=("#eef7f0" if bottom else "#eef2f8"),
                        stroke=(FIELD if bottom else INK),
                        color=(FIELD if bottom else INK)))
    # стрілка «назад/угору» збоку від рунґів
    p.append(arrow(240, 470, 240, 176, color=POS, sw=1.8))
    p.append(text(256, 300, "кожна сходинка —", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(256, 318, "найдешевший крок назад", size=11.5, color=POS, anchor="start"))
    p.append(text(256, 344, "W(k) — найменший старт,", size=11.5, color=MUTED, anchor="start"))
    p.append(text(256, 362, "з якого ще можливо k кроків", size=11.5, color=MUTED, anchor="start"))

    # ── права панель: три закони спуску ──
    p.append(rect(464, 56, 502, 452, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(715, 84, "Той самий механізм — три різні межі", size=13, color=INK, bold=True))

    cols = [(478, 152), (638, 136), (786, 168)]
    heads = ["закон спуску", "драбина W(k)", "межа на кроки"]
    for (cx, cw), h in zip(cols, heads):
        p.append(text(cx + cw / 2, 118, h, size=11.5, color=MUTED, bold=True))

    rows = [
        (140, "лічильник\nv′ = v − 1", "W(k) = k", "k ≤ v₀", "#eef2f8", INK),
        (240, "двійковий пошук\nv′ ≤ ⌊v/2⌋", "W(k) = 2ᵏ⁻¹", "k ≤ ⌊log₂ v₀⌋ + 1", "#eaf0fd", NEG),
        (340, "Евклід\nb′ = a mod b", "W(k) = Fₖ₊₁", "k ≤ logφ(√5·b₀) − 1", "#fdecea", POS),
    ]
    for (ry, law, wk, bound, fill, col) in rows:
        p.append(fitbox(cols[0][0], ry, cols[0][1], 66, law, size=12, bold=True,
                        fill=fill, stroke=col, color=INK))
        p.append(fitbox(cols[1][0], ry, cols[1][1], 66, wk, size=13, bold=True,
                        fill=BG, stroke="#c2cad4", color=col))
        p.append(fitbox(cols[2][0], ry, cols[2][1], 66, bound, size=12.5, bold=True,
                        fill=BG, stroke="#c2cad4", color=INK))
        p.append(arrow(cols[1][0] + cols[1][1] + 3, ry + 33, cols[2][0] - 5, ry + 33,
                       color=MUTED, sw=1.3))

    p.append(text(715, 442, "W росте — тож межа на кроки це просто ОБЕРНЕНА до W", size=12, color=INK))
    p.append(text(715, 466, "лінійна W → лінійна межа · подвоєння → логарифм · Фібоначчі → логарифм за φ",
                  size=11, color=MUTED))

    p.append(fitbox(24, 520, W - 48, 32,
                    "v₀ < W(k)  ⟹  кроків менше за k.   Не «як швидко падає», а «на скільки вистачить»",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "inverted-question.svg"), W, H, *p,
           title="Обернене питання: скільки треба, щоб вистачило на k кроків")


# ── Фіг. 8: назад від дна Евклід сам виписує Фібоначчі ───────────────────────
# Ідея: щоб крок був НАЙДЕШЕВШИМ, частка мусить бути 1 — тоді a mod b = a − b.
# Обернений найдешевший крок — це a = b + r, тобто РІВНО рекурентність Фібоначчі.
# Тому Фібоначчі тут не збіг і не магія: це та сама рекурентність, прочитана назад.
def fig_euclid_backwards():
    W, H = 990, 480
    p = []

    b, bw, bh = textbox(W / 2, 76,
                        "найдешевший крок — частка 1:  a mod b = a − b\n"
                        "(будь-яка більша частка обвалює b швидше — а нам треба ПОВІЛЬНО)",
                        size=12.5, pad=11, fill="#eef2f8", stroke=INK, bold=True)
    p.append(b)

    chain = [("(13, 8)", "F₆"), ("(8, 5)", "F₅"), ("(5, 3)", "F₄"), ("(3, 2)", "F₃"),
             ("(2, 1)", "F₂"), ("(1, 1)", "F₁"), ("(1, 0)", "F₀")]
    x0, xw = 60.0, 128.0
    cy = 250.0

    def CX(i):
        return x0 + xw * i + 54

    for i, (lab, fib) in enumerate(chain):
        last = (i == len(chain) - 1)
        bx, bwd, bhh = textbox(CX(i), cy, lab, size=14, pad=9,
                               fill=("#eef7f0" if last else "#eaf0fd"),
                               stroke=(FIELD if last else NEG), color=INK, bold=True)
        p.append(bx)
        p.append(text(CX(i), cy + 40, "b = " + fib, size=11.5, color=MUTED))

    # прямі кроки алгоритму — під ланцюгом
    for i in range(len(chain) - 1):
        p.append(arrow(CX(i) + 36, cy + 62, CX(i + 1) - 36, cy + 62, color=NEG, sw=1.5))
    p.append(text(W / 2, cy + 90, "прямо: крок Евкліда  (a, b) → (b, a mod b)", size=12, color=NEG))

    # зворотна побудова — над ланцюгом
    for i in range(len(chain) - 1):
        p.append(arrow(CX(i + 1) - 36, cy - 44, CX(i) + 36, cy - 44, color=POS, sw=1.7))
    p.append(text(W / 2, cy - 58, "назад: pred(a, b) = (a + b, a)   —   а це РІВНО Fₖ₊₂ = Fₖ₊₁ + Fₖ",
                  size=12.5, color=POS, bold=True))

    p.append(text(CX(len(chain) - 1), cy - 44, "старт назад", size=11, color=FIELD, bold=True))

    p.append(fitbox(60, 380, W - 120, 34,
                    "тож k кроків вимагають b ≥ Fₖ₊₁ — а мінімальна пара для k кроків це рівно (Fₖ₊₂, Fₖ₊₁)",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))
    p.append(text(W / 2, 438, "Фібоначчі тут не збіг: це найповільніший спуск, виписаний навпаки",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "euclid-backwards.svg"), W, H, *p,
           title="Назад від дна Евклід сам виписує Фібоначчі")


# ── Фіг. 9: згортка одометра — пара стає одним числом ────────────────────────
# Ідея: словниковий варіант доводить ЗУПИНКУ, але межі не дає. Якщо ж відомо, на
# скільки щонайбільше підскакує y за крок, що з'їдає одиницю x (це r), пара
# згортається в одне число N = (r+1)·x + y — і воно спадає щокроку. Уся якість
# межі сидить у вазі: припустив найгірший долив — дістав квадрат; знаєш r = 1 — лінія.
def fig_odometer_collapse():
    W, H = 950, 560
    p = []

    b, bw, bh = textbox(W / 2, 74, "N = (r + 1)·x + y", size=20, pad=13,
                        fill="#fff6e6", stroke="#e08a1e", color=INK, bold=True)
    p.append(b)
    p.append(text(W / 2, 112, "r — на скільки щонайбільше підскакує y за крок, що з'їдає одиницю x",
                  size=11.5, color=MUTED))

    # дві гілки
    p.append(fitbox(60, 146, 390, 96,
                    "y падає, x стоїть\nΔN ≤ −1",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, color=INK))
    p.append(fitbox(500, 146, 390, 96,
                    "x падає на 1, y підскакує на ≤ r\nΔN ≤ −(r + 1) + r = −1",
                    size=13, bold=True, fill="#fdecea", stroke=POS, color=INK))
    p.append(text(W / 2, 266, "обидві гілки — крок униз щонайменше на 1, тож N це звичайний варіант у ℕ",
                  size=12.5, color=INK, bold=True))

    # дві оцінки для сортувальної станції
    p.append(text(W / 2, 310, "сортувальна станція, n токенів — уся якість межі сидить у вазі:",
                  size=12.5, color=MUTED))
    p.append(fitbox(60, 330, 390, 100,
                    "доливу не знаємо → беремо найгірший\nr = n:   N ≤ (n + 1)·n\nКВАДРАТ",
                    size=13, bold=True, fill="#fdecea", stroke=POS, color=INK))
    p.append(fitbox(500, 330, 390, 100,
                    "читання кладе на стек ≤ 1 → r = 1\nN ≤ 2n\nЛІНІЯ",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))
    p.append(arrow(450, 380, 496, 380, color=MUTED, sw=1.6))

    p.append(fitbox(60, 456, W - 120, 34,
                    "вага r замість r+1 — і спуск ламається:  (3, 0) → (2, 1) дає  1·3+0 = 3 → 1·2+1 = 3",
                    size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))
    p.append(text(W / 2, 520, "словниковий варіант доводить ЗУПИНКУ; вагу підбираєш, щоб дістати МЕЖУ",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "odometer-collapse.svg"), W, H, *p,
           title="Згортка одометра: пара стає одним числом")


# ── Фіг. 10 (вставка hist): нитка доведень завершення і розрив на Тюрінгові ────
# Ідея: метод варіанта знайшли двічі. Тюрінг 1949 мав усе — спадну величину,
# ординал, навіть оцінку часу, — але його три сторінки не вплинули ні на кого;
# робоча нитка йде повз них, від «коробок-тверджень» 1947 до Флойда й далі.
# Розрив на осі — не пропуск у даних, а сам сюжет.
def fig_proof_thread():
    W, H = 980, 760
    p = []
    ax = 150.0                      # вісь часу
    bx, bw = 190.0, 760.0           # колонка підписів праворуч

    def node(y, year, lines, fill=FILL, stroke=LINE, sw=1.5, bold_year=False):
        h = len(lines) * 22.0 + 22.0
        out = fitbox(bx, y - h / 2, bw, h, "\n".join(lines),
                     size=14, fill=fill, stroke=stroke, sw=sw)
        out += circle(ax, y, 7, fill=fill, stroke=stroke, sw=2.0)
        out += text(138, y + 5, year, size=14, color=INK, bold=True, anchor="end")
        return out, h

    # суцільна вісь до розриву, штрихована в розриві, знову суцільна після
    p.append(line(ax, 74, ax, 213, color=LINE, sw=2.0))
    p.append(line(ax, 213, ax, 334, color=POS, sw=2.0, dash="7,6"))
    p.append(line(ax, 334, ax, 726, color=LINE, sw=2.0))

    # 1947 — ідея «твердити відношення в точці» вже є
    p.append(node(100, "1947", [
        "Ґолдстайн і фон Нойман: серед чотирьох видів коробок",
        "блок-схеми є «коробка-твердження» — місце, де твердять відношення"])[0])

    # 1949 — Тюрінг: усе вже на місці, але нитка обірветься
    p.append(node(180, "1949", [
        "ТЮРІНГ: «величина, що спадає й зникає, коли машина спиняється»",
        "ординал (n − r)·ω² + (r − s)·ω + k — обидва цикли однією величиною",
        "і вже тут: та сама величина обмежує ЧАС до зупинки"],
        fill="#fdecea", stroke=POS, sw=2.2)[0])

    # розрив: × на осі + пояснення в проміжку
    p.append(line(ax - 11, 262, ax + 11, 284, color=POS, sw=3.0))
    p.append(line(ax + 11, 262, ax - 11, 284, color=POS, sw=3.0))
    p.append(fitbox(bx, 237, bw, 66,
                    "слід обривається: впливу Тюрінгових трьох сторінок\n"
                    "на пізніших авторів не простежено — Флойд його не цитує.\n"
                    "Текст знайдуть і виправлять аж 1984-го (Морріс і Джонс)",
                    size=13.5, fill="#fff6e6", stroke="#e08a1e", color=INK))

    # 1966 — Наур
    p.append(node(360, "1966", [
        "Наур: «загальні знімки» — інваріанти, але без правил виводу;",
        "зазначає, що Флойд дійшов того самого незалежно"])[0])

    # 1967 — Флойд: нитка, що справді лягла
    p.append(node(445, "1967", [
        "ФЛОЙД: W-функція зі значеннями в цілком упорядкованій множині;",
        "глобальна властивість — зупинка — доводиться ЛОКАЛЬНИМИ перевірками.",
        "Сам приписує ідею Перлісу і Ґорну, оригінальності не заявляє"],
        fill="#eef7f0", stroke=FIELD, sw=2.2)[0])

    # 1969 — Гоар
    p.append(node(530, "1969", [
        "Гоар: P{Q}R — формальна система, збудована на Флойдові.",
        "Обіцяє лише «якщо Q завершиться, то R» — часткова коректність;",
        "термінування свідомо лишено ПОЗА системою"])[0])

    # 1976 — Дейкстра
    p.append(node(615, "1976", [
        "Дейкстра: wp вимагає зупинки за самим означенням;",
        "обмежувальна функція для do-od дістає ім'я"])[0])

    # 1985 — назва йде в мову
    p.append(node(700, "1985", [
        "Eiffel (Меєр): variant стає ключовим словом мови —",
        "назва, під якою прийом знають програмісти, прийшла не зі статті"])[0])

    render(os.path.join(OUT, "proof-thread.svg"), W, H, *p,
           title="Нитка доведень завершення: метод знайшли двічі")


if __name__ == "__main__":
    fig_variant_descent()
    fig_invariant_vs_variant()
    fig_lexico_descent()
    fig_wf_or_not()
    fig_ordinal_ladder()
    fig_goodstein_tracks()
    fig_inverted_question()
    fig_euclid_backwards()
    fig_odometer_collapse()
    fig_proof_thread()
    print("OK figs")
