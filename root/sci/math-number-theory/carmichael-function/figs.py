# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
from math import gcd

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── euler-overpromise: за модулем 8 усі повертаються до 1 уже на квадраті
# Ідея: φ(8)=4 — показник, що працює, та вдвічі задовгий. Три непарні основи
# 3, 5, 7 замикають кільце степенів на кроці 2; спільний момент повернення (λ)
# стоїть на двійці, тоді як Ейлерова стрілка тягнеться аж до четвірки.
def fig_euler_overpromise():
    W, H = 960, 440
    p = []
    XS = {1: 268, 2: 452, 3: 636, 4: 820}
    YS = {3: 188, 5: 258, 7: 328}
    CW, CH = 96, 44

    # зелена смуга за колонкою кроку 2 (λ) і пунктир за кроком 4 (φ)
    p.append(rect(XS[2] - CW / 2 - 12, 128, CW + 24, 236, fill="#eafaf0", stroke="none", sw=0, rx=9))
    # пунктир веде повз написи колонки 4 (розбитий на відрізки в проміжках між рядками)
    for y1, y2 in ((132, 180), (200, 251), (270, 321), (340, 360)):
        p.append(line(XS[4], y1, XS[4], y2, color="#b6bcc4", sw=1.4, dash="5,5"))

    p.append(text(W / 2, 58, "Степені за модулем 8: одиниця повертається до всіх уже на кроці 2",
                  size=16, bold=True))
    for s in (1, 2, 3, 4):
        p.append(text(XS[s], 114, "крок %d" % s, size=12.5, color=MUTED))

    for a in (3, 5, 7):
        y = YS[a]
        p.append(text(150, y + 5, "a = %d" % a, size=15, bold=True, anchor="end"))
        for s in (1, 2, 3, 4):
            v = pow(a, s, 8)
            one = v == 1
            x = XS[s]
            p.append(rect(x - CW / 2, y - CH / 2, CW, CH,
                          fill="#eafaf0" if one else "#fbfbfc",
                          stroke=FIELD if one else LINE, sw=2.0 if one else 1.2))
            p.append(text(x, y + 6, "%d ≡ %d" % (pow(a, s), v) if pow(a, s) != v else "%d" % v,
                          size=14, bold=one, color=FIELD if one else INK))
            if s < 4:
                p.append(arrow(x + CW / 2 + 5, y, XS[s + 1] - CW / 2 - 5, y, color=LINE, sw=1.3))

    p.append(text(XS[2], 392, "λ(8) = 2", size=15, bold=True, color=FIELD))
    p.append(text(XS[2], 414, "тут уже всі — одиниці", size=12.5, color=MUTED))
    p.append(text(XS[4], 392, "φ(8) = 4", size=15, bold=True, color=MUTED))
    p.append(text(XS[4], 414, "куди веде теорема Ейлера", size=12.5, color=MUTED))
    render(os.path.join(OUT, "euler-overpromise.svg"), W, H,
           *p, title="Ейлерів показник завеликий")


# ── lcm-of-cycles: λ — це коли всі кільця повертаються водночас
# Ідея: три доріжки з періодами 2, 6, 4. Зелена позначка там, де кільце знову
# у вихідній точці. Усі три позначки збігаються вперше на 12 = НСК(2,6,4) = λ.
def fig_lcm_of_cycles():
    W, H = 1000, 420
    p = []
    STEPS = list(range(1, 13))
    X0, X1 = 175, 930
    dx = (X1 - X0) / (len(STEPS) - 1)
    xof = lambda s: X0 + (s - 1) * dx
    lanes = [(2, 168), (6, 236), (4, 304)]

    # підсвітка стовпця 12 — спільне повернення
    p.append(rect(xof(12) - 22, 132, 44, 210, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=9))

    p.append(text(W / 2, 58, "Три кільцеві доріжки повертаються у вихідну точку кожне у свій час",
                  size=16, bold=True))
    # номери кроків
    for s in STEPS:
        p.append(text(xof(s), 118, str(s), size=12, color=MUTED if s != 12 else FIELD,
                      bold=(s == 12)))
    p.append(text(xof(6), 96, "крок", size=11.5, color=MUTED))

    for period, y in lanes:
        p.append(text(150, y + 5, "період %d" % period, size=13.5, bold=True, anchor="end"))
        p.append(line(xof(1) - 8, y, xof(12) + 8, y, color="#e3e6ea", sw=1.2))
        for s in STEPS:
            home = (s % period == 0)
            if home:
                p.append(circle(xof(s), y, 9, fill=FIELD, stroke=FIELD, sw=1.5))
            else:
                p.append(circle(xof(s), y, 4.5, fill=BG, stroke="#cfd4da", sw=1.2))

    b, _, _ = textbox(W / 2, 384, "усі три збігаються вперше на кроці 12  —  НСК(2, 6, 4) = 12 = λ",
                      size=14.5, pad=11, fill="#fbfbfc", bold=True)
    p.append(b)
    render(os.path.join(OUT, "lcm-of-cycles.svg"), W, H,
           *p, title="λ — перше спільне повернення всіх кілець")


# ── formula-assembly: λ бере НСК шматків, φ множить їх
# Ідея: те саме 360 = 2³·3²·5 обидві функції ділять на однакові шматки, але
# λ збирає їх НСК-ом (12), а φ добутком (96). НСК ≤ добутку — звідси λ ≤ φ.
def fig_formula_assembly():
    W, H = 1000, 560
    p = []
    PC = [("2³", 2, 4, "аномалія двійки:\n2^(3−2) = 2"),
          ("3²", 6, 6, "непарне просте:\nλ = φ = 6"),
          ("5",  4, 4, "просте:\np − 1 = 4")]
    XS = [255, 500, 745]

    p.append(text(W / 2, 62, "360 = 2³ · 3² · 5", size=19, bold=True))
    p.append(text(W / 2, 88, "обидві функції розбирають число на ті самі прості степені",
                  size=13, color=MUTED, italic=True))

    for (lab, lam, phi, note), x in zip(PC, XS):
        p.append(fitbox(x - 96, 120, 192, 58, "p^k = %s" % lab, size=15,
                        fill="#fbfbfc", stroke=LINE, sw=1.6, bold=True))
        p.append(mtext(x, 200, note, size=12, color=MUTED, lh=1.3))
        # два виходи з кожного шматка: λ-внесок (зелений) і φ-внесок (сірий)
        p.append(text(x, 244, "λ = %d" % lam, size=14.5, bold=True, color=FIELD))
        p.append(text(x, 268, "φ = %d" % phi, size=13.5, color=MUTED))

    # ліворуч — збірка λ через НСК, праворуч — збірка φ через добуток
    LAMX, PHIX, YCOMB = 330, 690, 400
    for x in XS:
        p.append(arrow(x, 278, LAMX, YCOMB - 34, color=FIELD, sw=1.5))
        p.append(arrow(x, 278, PHIX, YCOMB - 34, color="#c7ccd3", sw=1.4))

    b, _, _ = textbox(LAMX, YCOMB, ["λ(360)", "НСК(2, 6, 4)", "= 12"],
                      size=16, pad=14, fill="#eafaf0", stroke=FIELD, sw=2.4, bold=True, color=FIELD)
    p.append(b)
    b, _, _ = textbox(PHIX, YCOMB, ["φ(360)", "4 · 6 · 4", "= 96"],
                      size=16, pad=14, fill="#f4f6f8", stroke=MUTED, sw=2.0, bold=True)
    p.append(b)

    p.append(text(LAMX, 476, "спільний період — вичікує збіг", size=12.5, color=MUTED, italic=True))
    p.append(text(PHIX, 476, "усе населення лишків — множить", size=12.5, color=MUTED, italic=True))

    b, _, _ = textbox(W / 2, 522, "НСК ніколи не більший за добуток  →  λ(n) ≤ φ(n);  "
                                  "тут 12 ділить 96 рівно у 8 разів",
                      size=14, pad=11, fill="#fbfbfc", bold=True)
    p.append(b)
    render(os.path.join(OUT, "formula-assembly.svg"), W, H,
           *p, title="λ бере НСК, φ множить — те саме число, різна збірка")


# ── two-carmichaels: одне ім'я Кармайкла — два різні предмети й дві історії
# Верхня доріжка — функція λ: субстанція вже в Ґауса (1801), Кармайкл дає їй
# ім'я λ як чисту цікавість (1910), застосування приходить аж у RSA (1977) —
# через 67 років. Нижня доріжка — числа Кармайкла: Шимерка знаходить перші сім
# (1885), Корзельт дає критерій без прикладів (1899), Кармайкл наводить 561 і
# систематизує (1910–12). Обидві історії проходять крізь Кармайкла ~1910 —
# звідси спільне ім'я на двох цілком різних предметах.
def fig_two_carmichaels():
    W, H = 1100, 575
    p = []
    X0, X1, yr0, yr1 = 175, 1050, 1795, 1985
    xof = lambda y: X0 + (y - yr0) * (X1 - X0) / (yr1 - yr0)
    yA, yB = 190, 380

    # осі часу (стрілка вправо) для обох доріжок
    p.append(arrow(X0 - 8, yA, X1 + 12, yA, color="#c7ccd3", sw=1.6))
    p.append(arrow(X0 - 8, yB, X1 + 12, yB, color="#c7ccd3", sw=1.6))

    # підписи доріжок ліворуч
    p.append(mtext(26, yA - 4, ["Функція", "λ(n)"], size=15, anchor="start", bold=True, lh=1.25))
    p.append(mtext(26, yB - 4, ["Числа", "Кармайкла"], size=15, anchor="start", bold=True, lh=1.25))

    # вертикальний зв'язок на 1910 — обидві історії проходять крізь Кармайкла;
    # лінію розриваємо навколо рамки, щоб не перетинати напис
    xc = xof(1910)
    ymid = (yA + yB) / 2
    b, _, bh = textbox(xc, ymid, ["одне ім'я —", "два предмети"], size=12.5, pad=8,
                       fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(line(xc, yA, xc, ymid - bh / 2, color=FIELD, sw=1.6, dash="5,5"))
    p.append(line(xc, ymid + bh / 2, xc, yB, color=FIELD, sw=1.6, dash="5,5"))
    p.append(b)

    STY = {"pre": ("#ffffff", INK), "carm": (FIELD, FIELD), "app": ("#fdecea", POS)}

    def event(yr, ybase, cx, cy, lines, kind):
        dot_fill, col = STY[kind]
        xd = xof(yr)
        bb, _, bh = textbox(cx, cy, lines, size=12.5, pad=8, fill="#fbfbfc",
                            stroke=col, sw=1.8, bold=True)
        edge = cy + bh / 2 if cy < ybase else cy - bh / 2   # виноска впирається в край рамки, не в текст
        p.append(line(xd, ybase, cx, edge, color="#cfd4da", sw=1.2))
        p.append(bb)
        p.append(circle(xd, ybase, 7, fill=dot_fill, stroke=col, sw=2.4))

    # доріжка A — функція λ (виноски вгору)
    event(1801, yA, 258, 112, ["1801 · Ґаус", "субстанція вже тут", "Disq. Arith., §82–92"], "pre")
    event(1910, yA, xc,  110, ["1910 · Кармайкл", "дає їй ім'я λ", "чиста цікавість"], "carm")
    event(1977, yA, 990, 110, ["1977 · RSA", "застосування —", "аж через 67 років"], "app")

    # доріжка B — числа Кармайкла (виноски вниз, у два ряди, щоб не тіснилися)
    event(1885, yB, 452, 452, ["1885 · Шимерка", "перші сім чисел,", "лишилися непоміченими"], "pre")
    event(1899, yB, 650, 522, ["1899 · Корзельт", "критерій без", "жодного прикладу"], "pre")
    event(1910, yB, 905, 452, ["1910–12 · Кармайкл", "561 і систематика"], "carm")

    render(os.path.join(OUT, "two-carmichaels.svg"), W, H,
           *p, title="λ-функція і числа Кармайкла — спільне ім'я, різні предмети")


# ── lambda-vs-phi: λ чіпляється до низу, φ тягнеться вгору (діапазон n)
# Ідея: на одному діапазоні порівняти два показники. Для кожного n сіра порожня
# точка — φ(n), зелена повна — λ(n), стрижень між ними — зазор (скільки зайвого в
# Ейлеровому показнику). На простих точки збігаються (λ=φ=n−1) і сидять на верхній
# оболонці; на складених із кількома простими λ різко просідає до низу.
def fig_lambda_vs_phi():
    from math import gcd as _gcd

    def fact(n):
        f, p = [], 2
        while p * p <= n:
            if n % p == 0:
                k = 0
                while n % p == 0:
                    n //= p; k += 1
                f.append((p, k))
            p += 1
        if n > 1:
            f.append((n, 1))
        return f

    def _lcm(a, b):
        return a // _gcd(a, b) * b

    def lam(n):
        r = 1
        for p, k in fact(n):
            if p == 2:
                v = 1 if k == 1 else (2 if k == 2 else 1 << (k - 2))
            else:
                v = (p - 1) * p ** (k - 1)
            r = _lcm(r, v)
        return r

    def phi(n):
        r = n
        for p, _ in fact(n):
            r -= r // p
        return r

    W, H = 1120, 560
    NLO, NHI = 2, 40
    PX0, PX1, PT, PB = 95, 1075, 108, 468
    ymax = 40
    dx = (PX1 - PX0) / (NHI - NLO)
    xof = lambda nn: PX0 + (nn - NLO) * dx
    yof = lambda v: PB - (v / ymax) * (PB - PT)
    p = []

    p.append(text(W / 2, 26, "На одному діапазоні: λ(n) тулиться до низу, φ(n) тягнеться вгору",
                  size=17, bold=True))

    # сітка й підписи осі значень
    for gv in (0, 10, 20, 30, 40):
        y = yof(gv)
        p.append(line(PX0 - 6, y, PX1, y, color="#cfd4da" if gv == 0 else "#eef0f3", sw=1.2))
        p.append(text(PX0 - 12, y + 4, str(gv), size=11.5, color=MUTED, anchor="end"))
    for nn in (2, 10, 20, 30, 40):
        p.append(text(xof(nn), PB + 22, str(nn), size=11.5, color=MUTED))
    p.append(text((PX0 + PX1) / 2, PB + 46, "модуль n", size=12.5, color=MUTED))

    # дані: стрижень зазору + дві точки на кожен n
    for nn in range(NLO, NHI + 1):
        L, F = lam(nn), phi(nn)
        x, yL, yF = xof(nn), yof(lam(nn)), yof(phi(nn))
        if L != F:
            p.append(line(x, yL, x, yF, color="#d7dbe0", sw=2.2))
            p.append(circle(x, yF, 3.6, fill=BG, stroke=MUTED, sw=1.6))
            p.append(circle(x, yL, 4.2, fill=FIELD, stroke=FIELD, sw=1.4))
        else:
            p.append(circle(x, yL, 4.6, fill="#eafaf0", stroke=FIELD, sw=2.4))

    # легенда
    lx, ly = 118, 96
    p.append(circle(lx, ly, 4.2, fill=FIELD, stroke=FIELD, sw=1.4))
    p.append(text(lx + 13, ly + 4, "λ(n) — найменший універсальний показник", size=12.5, anchor="start"))
    p.append(circle(lx, ly + 25, 3.6, fill=BG, stroke=MUTED, sw=1.6))
    p.append(text(lx + 13, ly + 29, "φ(n) — Ейлерів показник", size=12.5, anchor="start"))
    p.append(circle(lx, ly + 50, 4.6, fill="#eafaf0", stroke=FIELD, sw=2.4))
    p.append(text(lx + 13, ly + 54, "λ = φ  (за модулем є первісний корінь)", size=12.5, anchor="start"))

    # виноска на прості (верхня оболонка)
    p.append(text(PX1, yof(phi(37)) - 14, "прості: λ = φ = n−1", size=11.5, color=MUTED,
                  italic=True, anchor="end"))

    # виноска на складений зазор n = 24 (φ=8, λ=2)
    x24 = xof(24)
    b, bw, bh = textbox(x24 + 92, 250, ["n = 24 = 2³·3", "φ = 8, а λ = 2", "зазор — учетверо"],
                        size=11.5, pad=8, fill="#fbfbfc", stroke=MUTED, sw=1.4)
    p.append(line(x24 + 4, yof(phi(24)), x24 + 92 - bw / 2 - 4, 250, color="#cfd4da", sw=1.2))
    p.append(b)

    render(os.path.join(OUT, "lambda-vs-phi.svg"), W, H,
           *p, title=None)


# ── cyclic-when-coprime: циклічна ⟺ порядки множників взаємно прості
# Строге виведення λ спирається на лему: максимальний порядок = НСК порядків.
# Ліворуч — множники порядків 3 і 4 (взаємно прості): склеювання дає один цикл
# довжини 12 = вся група (циклічна). Праворуч — порядки 2 і 4 (спільний множник
# 2): найдовший цикл лише НСК(2,4)=4, друге кільце недосяжне степенями одного
# елемента — саме так поводиться (Z/2^k)* = ⟨5⟩ × ⟨−1⟩ (нециклічна).
def fig_cyclic_when_coprime():
    import math
    W, H = 1040, 520
    p = []

    # ЛІВОРУЧ: взаємно прості порядки → один цикл 12
    cx, cy, R = 285, 292, 132
    n = 12
    pts = [(cx + R * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
            cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p.append(arrow(x1 + ux * 14, y1 + uy * 14, x2 - ux * 14, y2 - uy * 14, color=FIELD, sw=1.7))
    for (x, y) in pts:
        p.append(circle(x, y, 10, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(mtext(cx, cy - 8, ["(Z/3)* × (Z/4)*", "≅ Z/12"], size=15, bold=True))
    p.append(text(cx, cy + 20, "один цикл", size=12.5, color=MUTED, italic=True))
    b, _, _ = textbox(cx, 470, ["порядки 3 і 4 взаємно прості", "НСК(3,4) = 12 = |група|  →  циклічна"],
                      size=13, pad=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    p.append(b)

    # ПРАВОРУЧ: спільний множник → макс. цикл 4 < 8, друге кільце недосяжне
    cx2, cy2 = 770, 292
    Rin, Rout = 86, 142
    m = 4
    inr = [(cx2 + Rin * math.cos(-math.pi / 2 + 2 * math.pi * i / m),
            cy2 + Rin * math.sin(-math.pi / 2 + 2 * math.pi * i / m)) for i in range(m)]
    outr = [(cx2 + Rout * math.cos(-math.pi / 2 + 2 * math.pi * i / m),
             cy2 + Rout * math.sin(-math.pi / 2 + 2 * math.pi * i / m)) for i in range(m)]
    for i in range(m):
        x1, y1 = inr[i]
        x2, y2 = inr[(i + 1) % m]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p.append(arrow(x1 + ux * 13, y1 + uy * 13, x2 - ux * 13, y2 - uy * 13, color=FIELD, sw=1.7))
    for i in range(m):
        x1, y1 = inr[i]
        x2, y2 = outr[i]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p.append(line(x1 + ux * 12, y1 + uy * 12, x2 - ux * 11, y2 - uy * 11,
                      color="#b6bcc4", sw=1.3, dash="4,4"))
    for (x, y) in inr:
        p.append(circle(x, y, 10, fill="#eafaf0", stroke=FIELD, sw=2))
    for (x, y) in outr:
        p.append(circle(x, y, 9, fill="#f1f2f4", stroke="#c2c8cf", sw=1.6))
    p.append(mtext(cx2, cy2 - 4, ["(Z/2)* × (Z/4)*"], size=14, bold=True))
    p.append(text(cx2, cy2 + 16, "макс. цикл 4 < 8", size=12, color=MUTED, italic=True))
    p.append(text(cx2 + 9, cy2 - (Rin + Rout) / 2, "×(−1)", size=11.5, color=MUTED, anchor="start"))
    b, _, _ = textbox(cx2, 470, ["порядки 2 і 4 мають спільний множник", "найдовший цикл лише НСК(2,4) = 4  →  нециклічна"],
                      size=13, pad=11, fill="#fbfbfc", stroke=MUTED, sw=1.6, bold=True)
    p.append(b)

    render(os.path.join(OUT, "cyclic-when-coprime.svg"), W, H, *p,
           title="Циклічна ⟺ порядки множників взаємно прості")


# ── four-square-roots: чому (Z/2^k)* нециклічна — рівно чотири корені x²≡1
# (Z/16)* = ⟨5⟩ × ⟨−1⟩ як дві стрічки. Верхня — степені п'ятірки 1,5,9,13;
# нижня — їхні добутки з −1: 15,11,7,3. Зелені клітини — чотири корені рівняння
# x²≡1: 1, 9, 7, 15. У циклічній групі їх було б лише два (±1) — звідси доказ
# нециклічності, а з нею й того, що λ(16)=4, а не φ(16)=8.
def fig_four_square_roots():
    W, H = 940, 470
    p = []
    top = [1, 5, 9, 13]
    bot = [15, 11, 7, 3]
    powlab = ["5⁰ = 1", "5¹ = 5", "5² = 9", "5³ = 13"]
    roots = {1, 7, 9, 15}
    x0, y_top, y_bot = 262, 118, 206
    cw, ch, gap = 148, 78, 12

    p.append(text(W / 2, 66, "Вісім лишків (Z/16)* = ⟨5⟩ × ⟨−1⟩, а x² ≡ 1 справджують рівно чотири",
                  size=14.5, color=MUTED))

    for j in range(4):
        p.append(text(x0 + j * cw + (cw - gap) / 2, y_top - 14, powlab[j], size=12.5, color=MUTED))
    p.append(text(x0 - 16, y_top + ch / 2 + 5, "степені 5", size=12.5, color=MUTED, anchor="end"))
    p.append(text(x0 - 16, y_bot + ch / 2 + 5, "−1 · (степені 5)", size=12.5, color=MUTED, anchor="end"))

    for j in range(4):
        for (y, vals) in [(y_top, top), (y_bot, bot)]:
            v = vals[j]
            xx = x0 + j * cw
            r = v in roots
            p.append(rect(xx, y, cw - gap, ch,
                          fill="#eafaf0" if r else "#fbfbfc",
                          stroke=FIELD if r else LINE, sw=2.4 if r else 1.3))
            p.append(text(xx + (cw - gap) / 2, y + 34, str(v),
                          size=22 if r else 19, bold=r, color=FIELD if r else INK))
            if r:
                p.append(text(xx + (cw - gap) / 2, y + 62, "x² ≡ 1", size=12.5, color=FIELD, bold=True))

    b, _, _ = textbox(W / 2, 336, "x² ≡ 1 (mod 16)  ⟺  x ≡ ±1 (mod 8):   1, 9 ≡ 1   і   7, 15 ≡ −1",
                      size=13.5, pad=10, fill="#fbfbfc", bold=True)
    p.append(b)
    b, _, _ = textbox(W / 2, 392, "циклічна група мала б лише 2 корені (±1) — чотири  →  нециклічна,  тому λ(16) = 4, а не φ(16) = 8",
                      size=13.5, pad=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=FIELD)
    p.append(b)

    render(os.path.join(OUT, "four-square-roots.svg"), W, H, *p,
           title="Чотири квадратні корені з одиниці за модулем 2^k")


fig_euler_overpromise()
fig_lcm_of_cycles()
fig_formula_assembly()
fig_two_carmichaels()
fig_lambda_vs_phi()
fig_cyclic_when_coprime()
fig_four_square_roots()
print("ok:", sorted(os.listdir(OUT)))
