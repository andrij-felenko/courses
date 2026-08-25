# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── coordinates: лишки як координати числа ───────────────────────────────────
# Ідея: 15 чисел і 15 пар (x mod 3, x mod 5) — сітка заповнюється рівно раз.
# Це вся теорема: жодна клітина не порожня (розв'язок є) і жодна не подвійна (він один).
def fig_coordinates():
    W, H = 780, 420
    cw, ch = 88, 62
    gx, gy = 200, 130
    p = []

    grid = {}
    for x in range(15):
        grid[(x % 3, x % 5)] = x

    # заголовки осей — рознесені по x, тому не сходяться між собою
    p.append(text(gx + 2.5 * cw, 84, "залишок за модулем 5", size=13, color=MUTED))
    p.append(text(gx - 14, 84, "залишок за модулем 3", size=13, color=MUTED, anchor="end"))
    for j in range(5):
        p.append(text(gx + j * cw + cw / 2, 114, j, size=13, color=INK, bold=True))
    for i in range(3):
        p.append(text(gx - 14, gy + i * ch + ch / 2 + 5, i, size=13, color=INK, bold=True))

    for i in range(3):
        for j in range(5):
            v = grid[(i, j)]
            hit = (v == 8)
            p.append(rect(gx + j * cw, gy + i * ch, cw, ch,
                          fill="#eafaf0" if hit else "#fbfbff",
                          stroke=FIELD if hit else MUTED, sw=2.2 if hit else 1.2))
            p.append(text(gx + j * cw + cw / 2, gy + i * ch + ch / 2 + 6, v,
                          size=17, color=FIELD if hit else INK, bold=hit))

    p.append(text(W / 2, 352, "8 → (8 mod 3, 8 mod 5) = (2, 3), і жодне інше число з 0…14 цієї пари не дає",
                  size=12.5, color=MUTED, italic=True))
    p.append(text(W / 2, 384, "3 · 5 = 15 клітин на 15 чисел: жодна не порожня й жодна не зайнята двічі",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "coordinates.svg"), W, H, *p,
           title="Пара залишків — це координати числа")


# ── coprime-hinge: що стається, коли модулі НЕ взаємно прості ────────────────
# Ідея: 4 і 6 мають спільну двійку — і сітка ламається одразу з двох боків:
# половина клітин недосяжна, а решту займають по два числа.
def fig_coprime_hinge():
    W, H = 880, 450
    cw, ch = 86, 58
    gx, gy = 182, 130
    p = []

    grid = {}
    for x in range(24):
        grid.setdefault((x % 4, x % 6), []).append(x)

    p.append(text(gx + 3 * cw, 84, "залишок за модулем 6", size=13, color=MUTED))
    p.append(text(gx - 14, 84, "залишок за модулем 4", size=13, color=MUTED, anchor="end"))
    for j in range(6):
        p.append(text(gx + j * cw + cw / 2, 114, j, size=13, color=INK, bold=True))
    for i in range(4):
        p.append(text(gx - 14, gy + i * ch + ch / 2 + 5, i, size=13, color=INK, bold=True))

    for i in range(4):
        for j in range(6):
            xs = grid.get((i, j), [])
            cx = gx + j * cw + cw / 2
            cy = gy + i * ch + ch / 2
            if xs:
                p.append(rect(gx + j * cw, gy + i * ch, cw, ch, fill="#fdecea", stroke=POS, sw=1.6))
                p.append(text(cx, cy + 5, ", ".join(str(v) for v in xs), size=14, color=POS, bold=True))
            else:
                p.append(rect(gx + j * cw, gy + i * ch, cw, ch, fill="#f0f0f2", stroke=MUTED, sw=1.0))
                p.append(text(cx, cy + 6, "—", size=15, color=MUTED))

    p.append(text(W / 2, 398,
                  "сірі клітини недосяжні: x ≡ 0 (mod 4) вимагає парного x, а x ≡ 1 (mod 6) — непарного",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 424,
                  "а решту займають по ДВА числа — єдиність лише за модулем НСК(4, 6) = 12, не 24",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "coprime-hinge.svg"), W, H, *p,
           title="НСД(4, 6) = 2 — і сітка ламається з обох боків")


# ── construction: побудова відповіді через «чисті одиниці» ───────────────────
# Ідея: e₁ = (1,0) і e₂ = (0,1) грають роль базису — кожен доданок працює лише
# на свою координату й невидимий для чужої, тому пара складається як вектор.
def fig_construction():
    W, H = 840, 430
    p = []

    p.append(line(420, 60, 420, 350, color=MUTED, sw=1.2, dash="4 4"))

    # ── ліворуч: як знайти чисті одиниці
    p.append(text(40, 72, "Крок 1. Побудувати «чисті одиниці»", size=15, color=INK,
                  anchor="start", bold=True))

    p.append(text(40, 112, "e₁ ≡ 1 (mod 3),   e₁ ≡ 0 (mod 5)", size=13, color=INK, anchor="start"))
    p.append(text(40, 136, "кратні 5:   5,  10,  15, …", size=12.5, color=MUTED, anchor="start"))
    p.append(text(40, 160, "яке з них дає 1 за модулем 3?", size=12.5, color=MUTED, anchor="start"))
    b, _, _ = textbox(160, 200, "e₁ = 10", size=16, bold=True, color=FIELD,
                      fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(b)

    p.append(text(40, 250, "e₂ ≡ 0 (mod 3),   e₂ ≡ 1 (mod 5)", size=13, color=INK, anchor="start"))
    p.append(text(40, 274, "кратні 3:   3,  6,  9, …", size=12.5, color=MUTED, anchor="start"))
    p.append(text(40, 298, "яке з них дає 1 за модулем 5?", size=12.5, color=MUTED, anchor="start"))
    b, _, _ = textbox(160, 338, "e₂ = 6", size=16, bold=True, color=NEG,
                      fill="#eef4ff", stroke=NEG, sw=2)
    p.append(b)

    # ── праворуч: як із них скласти будь-яку пару
    p.append(text(460, 72, "Крок 2. Скласти потрібну пару", size=15, color=INK,
                  anchor="start", bold=True))
    p.append(text(460, 112, "потрібна пара (2, 3):", size=13, color=INK, anchor="start"))
    p.append(text(460, 148, "x = 2·e₁ + 3·e₂", size=14, color=INK, anchor="start"))
    p.append(text(460, 174, "    = 2·10 + 3·6 = 38", size=14, color=INK, anchor="start"))
    p.append(text(460, 200, "    ≡ 38 − 2·15 = 8 (mod 15)", size=14, color=INK, anchor="start"))
    b, _, _ = textbox(570, 252, "x = 8", size=18, bold=True, color=FIELD,
                      fill="#eafaf0", stroke=FIELD, sw=2.2)
    p.append(b)
    p.append(text(460, 304, "перевірка:", size=12.5, color=MUTED, anchor="start"))
    p.append(text(460, 328, "8 mod 3 = 2 ✓     8 mod 5 = 3 ✓", size=13, color=FIELD, anchor="start"))

    p.append(fitbox(60, 372, 720, 46,
                    "у загальному вигляді:   Nᵢ = N / nᵢ ,    eᵢ = Nᵢ · (Nᵢ⁻¹ mod nᵢ) ,    x = a₁·e₁ + … + aₖ·eₖ  (mod N)",
                    size=14, fill=FILL, stroke=INK, sw=1.4, bold=True))

    render(os.path.join(OUT, "construction.svg"), W, H, *p,
           title="Відповідь складається з «чистих одиниць», як вектор із базису")


# ── rsa-crt-cost: заради чого це в RSA ──────────────────────────────────────
# Ідея: вартість піднесення до степеня ~ куб довжини модуля, тож два вдвічі
# коротших модулі коштують 2·(1/8) = 1/4 від одного довгого. Це і є прискорення.
def fig_rsa_crt_cost():
    W, H = 800, 470
    p = []

    p.append(text(40, 64, "НАПРЯМУ", size=14, color=POS, anchor="start", bold=True))
    p.append(fitbox(150, 76, 500, 46, "одне піднесення до степеня за модулем n = p·q   (2048 біт)",
                    size=14, fill="#fdecea", stroke=POS, sw=1.8))

    p.append(line(40, 152, 760, 152, color=MUTED, sw=1.2, dash="4 4"))

    p.append(text(40, 186, "ЧЕРЕЗ КТЗ", size=14, color=FIELD, anchor="start", bold=True))
    p.append(fitbox(150, 198, 230, 52, "піднесення до степеня\nза модулем p  (1024 біт)",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(fitbox(420, 198, 230, 52, "піднесення до степеня\nза модулем q  (1024 біт)",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(arrow(265, 250, 265, 272, color=FIELD, sw=1.8))
    p.append(arrow(535, 250, 535, 272, color=FIELD, sw=1.8))
    p.append(fitbox(250, 274, 300, 44, "склеїти за КТЗ  →  m",
                    size=14, fill=BG, stroke=FIELD, sw=1.8, bold=True))

    p.append(rect(150, 338, 360, 18, fill=POS, stroke=POS, sw=1, rx=3))
    p.append(text(522, 352, "напряму  ≈ 1", size=12, color=POS, anchor="start", bold=True))
    p.append(rect(150, 364, 90, 18, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    p.append(text(252, 378, "через КТЗ  ≈ ¼", size=12, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(150, 400, 520, 52,
                    "піднесення до степеня коштує приблизно як куб довжини модуля:\n"
                    "удвічі коротший модуль — у 8 разів дешевше, а таких обчислень два → 2/8 = ¼",
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "rsa-crt-cost.svg"), W, H, *p,
           title="Чому RSA розшифровує через залишки, а не напряму")


# ── bezout-set: НСД як найменше, що можна скласти ────────────────────────────
# Ідея (для math-crt-derivation): множина {6u + 15v} — це РІВНО кратні трійки.
# Найменше додатне в ній і є НСД. Саме звідси береться одиниця, а з неї обернений.
def fig_bezout_set():
    W, H = 900, 470
    p = []

    p.append(text(W / 2, 58, "беремо 6 і 15 та складаємо все, що можна: 6·u + 15·v",
                  size=13.5, color=MUTED))

    # ── ліворуч: кілька комбінацій
    p.append(text(60, 100, "кілька комбінацій:", size=13, color=INK, anchor="start", bold=True))
    combos = [
        ("6·(−2) + 15·1", "= 3", FIELD, True),
        ("6·( 1) + 15·0", "= 6", INK, False),
        ("6·(−1) + 15·1", "= 9", INK, False),
        ("6·( 2) + 15·0", "= 12", INK, False),
        ("6·( 0) + 15·1", "= 15", INK, False),
    ]
    for k, (lhs, rhs, col, bold) in enumerate(combos):
        y = 132 + k * 28
        p.append(text(60, y, lhs, size=13, color=col, anchor="start", bold=bold))
        p.append(text(240, y, rhs, size=13, color=col, anchor="start", bold=bold))
    p.append(text(60, 132 + 5 * 28 + 4, "найменше додатне — трійка", size=12,
                  color=FIELD, anchor="start", italic=True))

    # ── праворуч: що з цього випливає
    p.append(text(500, 100, "чого скласти НЕ вдасться:", size=13, color=INK,
                  anchor="start", bold=True))
    p.append(text(500, 132, "1,  2,  4,  5,  7,  8,  10, …", size=13.5, color=POS, anchor="start"))
    p.append(text(500, 160, "хоч як добирай u та v", size=12, color=MUTED,
                  anchor="start", italic=True))
    p.append(text(500, 200, "усе досяжне кратне трьом —", size=13, color=INK, anchor="start"))
    p.append(text(500, 224, "бо трійка ділить і 6, і 15", size=13, color=INK, anchor="start"))
    b, _, _ = textbox(660, 272, "НСД(6, 15) = 3", size=16, bold=True, color=FIELD,
                      fill="#eafaf0", stroke=FIELD, sw=2.2)
    p.append(b)

    # ── числова пряма −9 … 18
    X0, XE, AY = 60, 850, 350
    lo, hi = -9, 18
    step = (XE - X0) / float(hi - lo)
    p.append(line(X0 - 14, AY, XE + 16, AY, color=INK, sw=1.4))
    for n in range(lo, hi + 1):
        x = X0 + (n - lo) * step
        if n % 3 == 0:
            p.append(circle(x, AY, 6.5, fill="#eafaf0" if n else BG, stroke=FIELD, sw=2.2))
            p.append(text(x, AY + 30, n, size=12.5, color=FIELD, bold=True))
        else:
            p.append(circle(x, AY, 2.6, fill=BG, stroke=MUTED, sw=1.1))

    # позначка найменшого додатного
    x3 = X0 + (3 - lo) * step
    p.append(arrow(x3, AY - 44, x3, AY - 13, color=FIELD, sw=1.8))
    p.append(text(x3, AY - 54, "найменше додатне", size=12, color=FIELD, bold=True))

    p.append(fitbox(60, 402, 790, 46,
                    "множина {6u + 15v} — це РІВНО кратні трійки: ні більше, ні менше.\n"
                    "Найменше додатне в ній і є НСД — а якщо НСД = 1, то одиниця складається, і з неї виходить обернений.",
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "bezout-set.svg"), W, H, *p,
           title="НСД — не «найбільший дільник», а найменше, що можна скласти")


# ── ring-iso: гомоморфізм — квадрат, що замикається ──────────────────────────
# Ідея: звести-потім-перемножити = перемножити-потім-звести. Ця половина
# теореми взаємної простоти НЕ потребує взагалі — вона дається задарма.
def fig_ring_iso():
    W, H = 900, 430
    p = []

    b, w1, h1 = textbox(215, 120, "x = 23,   y = 17", size=14, bold=True,
                        fill=FILL, stroke=INK, sw=1.6)
    p.append(b)
    b, w2, h2 = textbox(690, 120, "x → (2, 3, 2)\ny → (2, 2, 3)", size=14,
                        fill="#eef4ff", stroke=NEG, sw=1.6, color=NEG)
    p.append(b)
    b, w3, h3 = textbox(215, 300, "x · y = 391 ≡ 76", size=14, bold=True,
                        fill=FILL, stroke=INK, sw=1.6)
    p.append(b)
    b, w4, h4 = textbox(690, 300, "(2·2, 3·2, 2·3)\n≡ (1, 1, 6)", size=14,
                        fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD)
    p.append(b)

    # горизонтальні стрілки — φ
    p.append(arrow(215 + w1 / 2 + 16, 120, 690 - w2 / 2 - 16, 120, color=NEG, sw=1.8))
    p.append(text(452, 104, "φ — звести за 3, 5, 7", size=12, color=NEG))
    p.append(arrow(215 + w3 / 2 + 16, 300, 690 - w4 / 2 - 16, 300, color=FIELD, sw=1.8))
    p.append(text(452, 284, "φ — те саме зведення", size=12, color=FIELD))

    # вертикальні стрілки — множення
    p.append(arrow(215, 120 + h1 / 2 + 14, 215, 300 - h3 / 2 - 14, color=INK, sw=1.8))
    p.append(text(200, 206, "перемножити", size=12, color=INK, anchor="end"))
    p.append(text(200, 224, "у ℤ/105", size=12, color=MUTED, anchor="end"))
    p.append(arrow(690, 120 + h2 / 2 + 14, 690, 300 - h4 / 2 - 14, color=INK, sw=1.8))
    p.append(text(706, 206, "перемножити", size=12, color=INK, anchor="start"))
    p.append(text(706, 224, "покоординатно", size=12, color=MUTED, anchor="start"))

    p.append(text(452, 214, "обидва шляхи → (1, 1, 6)", size=13, color=INK, bold=True))

    p.append(fitbox(60, 356, 780, 48,
                    "Куди не йди — відповідь одна: φ(x·y) = φ(x)·φ(y), і так само для «+» та «−».\n"
                    "Ця половина не коштує нічого: зведення за модулем ЗАВЖДИ шанує арифметику, хоч які модулі.",
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "ring-iso.svg"), W, H, *p,
           title="Гомоморфізм: квадрат замикається")


# ── overlap-condition: звідки береться умова сумісності ──────────────────────
# Ідея: НСД — це та частина числа, яку обидва модулі бачать ОБИДВА. На цій
# спільній частині вони мусять розповідати одне й те саме — інакше суперечність.
def fig_overlap_condition():
    W, H = 900, 490
    p = []

    cxl, cxr, cy, r = 330, 470, 190, 125
    p.append(circle(cxl, cy, r, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(circle(cxr, cy, r, fill="none", stroke=FIELD, sw=2))

    p.append(text(250, 130, "12", size=19, color=NEG, bold=True))
    p.append(text(550, 130, "18", size=19, color=FIELD, bold=True))

    p.append(text(270, 232, "2", size=20, color=NEG, bold=True))
    p.append(text(400, 232, "2 · 3", size=18, color=POS, bold=True))
    p.append(text(530, 232, "3", size=20, color=FIELD, bold=True))

    p.append(text(400, 278, "спільне", size=12, color=POS))

    p.append(fitbox(636, 128, 230, 54, "НСД(12, 18) = 2·3 = 6\nте, що бачать ОБИДВА",
                    size=12.5, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(fitbox(636, 208, 230, 54, "НСК(12, 18) = 2·(2·3)·3 = 36\nусе разом, без повторів",
                    size=12.5, fill=FILL, stroke=INK, sw=1.6))

    p.append(text(W / 2, 352,
                  "на спільній шістці обидва модулі мусять розповідати одне й те саме",
                  size=13.5, color=INK, bold=True))

    p.append(fitbox(58, 372, 380, 92,
                    "x ≡ 5 (mod 12),   x ≡ 11 (mod 18)\n"
                    "5 mod 6 = 5    і    11 mod 6 = 5\n"
                    "історії збіглися  →  x ≡ 29 (mod 36)",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(fitbox(462, 372, 380, 92,
                    "x ≡ 5 (mod 12),   x ≡ 10 (mod 18)\n"
                    "5 mod 6 = 5    але    10 mod 6 = 4\n"
                    "суперечність  →  розв'язку немає",
                    size=13, fill="#fdecea", stroke=POS, sw=1.8))

    render(os.path.join(OUT, "overlap-condition.svg"), W, H, *p,
           title="Спільний дільник — це спільна частина розповіді")


# ── hist-threads: три незалежні нитки й пізнє знайомство ─────────────────────
# Ідея вставки hist-sunzi-to-gauss: час тече вниз, три колонки — три традиції.
# Головне видно з форми: європейська нитка дійшла до теореми (Гаусс, 1801)
# ЩЕ НЕ ЗНАЮЧИ про Цінь Цзюшао — про нього дізналися аж 1852–1874.
def fig_hist_threads():
    W, H = 1000, 860
    COLS = {"cn": 235, "in": 505, "eu": 775}
    p = []

    p.append(text(W / 2, 52, "час тече вниз; шкала не лінійна — важлива черга подій, не проміжки",
                  size=12.5, color=MUTED, italic=True))

    for key, label in (("cn", "Китай"), ("in", "Індія"), ("eu", "Європа")):
        p.append(textbox(COLS[key], 86, label, size=15, bold=True,
                         fill="#eef1f6", stroke=LINE, min_w=200)[0])

    # (колонка, y, рядки, підсвітка)
    rows = [
        ("cn", 145, ["Лю Сінь, I ст. до н.е.", "шанъюань — епоха, коли", "всі цикли збіглися"], None),
        ("cn", 235, ["«Канон Сунь-цзи», 280–473", "рецепт 70 · 21 · 15", "без доведення, модулі лише 3,5,7"], None),
        ("in", 325, ["Аріабхата, бл. 499", "загальний алгоритм для", "ax + by = c"], FIELD),
        ("in", 415, ["Брахмагупта, 628", "Бхаскара I, бл. 629 —", "назва «куттака»"], None),
        ("cn", 415, ["Ї Сін, 727", "календар Даянь"], None),
        ("eu", 505, ["Фібоначчі, 1202", "окремі випадки"], None),
        ("cn", 505, ["Цінь Цзюшао, 1247", "загальний алгоритм +", "не взаємно прості модулі"], FIELD),
        ("eu", 595, ["Скалігер, 1583", "юліанський період 28·19·15"], None),
        ("eu", 665, ["Ойлер, 1740", "доведення"], None),
        ("eu", 735, ["Гаусс, 1801", "знак ≡ — рецепт стає теоремою"], None),
        ("eu", 800, ["Вайлі 1852 · Матіссен 1874", "Європа читає Ціня Цзюшао"], POS),
    ]
    # окрема анотаційна рамка в колонці Китаю (не входить у rows — свій рядок нижче)
    ANNOT_CN_Y = 700

    # спершу обчислюємо вертикальні межі всіх рамок у кожній колонці, щоб
    # прокласти пунктирну вісь ЛИШЕ в проміжках між ними (лінія не має різати текст)
    spans = {"cn": [], "in": [], "eu": []}
    for key, y, lines, hi in rows:
        _, _, h = textbox(COLS[key], y, "\n".join(lines), size=12.5, min_w=225)
        spans[key].append((y - h / 2, y + h / 2))
    _, _, annot_h = textbox(COLS["cn"], ANNOT_CN_Y,
                            "Європа дізналася про\nцей алгоритм аж через\n600 років — і на 70 років\nПІЗНІШЕ за Гаусса",
                            size=12.5, min_w=225)
    spans["cn"].append((ANNOT_CN_Y - annot_h / 2, ANNOT_CN_Y + annot_h / 2))

    for key in ("cn", "in", "eu"):
        ivals = sorted(spans[key])
        cursor = 108
        for top, bot in ivals:
            if top - 6 > cursor:
                p.append(line(COLS[key], cursor, COLS[key], top - 6,
                              color="#d5d9e0", sw=1.2, dash="4,5"))
            cursor = max(cursor, bot + 6)
        if cursor < 800:
            p.append(line(COLS[key], cursor, COLS[key], 800,
                          color="#d5d9e0", sw=1.2, dash="4,5"))

    for key, y, lines, hi in rows:
        fill = "#eafaf0" if hi == FIELD else ("#fdecea" if hi == POS else "#fbfbff")
        stroke = hi if hi else MUTED
        p.append(textbox(COLS[key], y, "\n".join(lines), size=12.5,
                         fill=fill, stroke=stroke, sw=2.0 if hi else 1.2, min_w=225)[0])

    # стрілка «дізналися пізно» — у порожній колонці Китаю навпроти Ойлера/Гаусса
    p.append(textbox(COLS["cn"], ANNOT_CN_Y, "Європа дізналася про\nцей алгоритм аж через\n600 років — і на 70 років\nПІЗНІШЕ за Гаусса",
                     size=12.5, fill="#fdecea", stroke=POS, sw=2.0, min_w=225, color=POS, bold=True)[0])
    p.append(arrow(COLS["cn"], 645, COLS["cn"], 553, color=POS, sw=2.2))

    render(os.path.join(OUT, "hist-threads.svg"), W, H, *p,
           title="Три нитки, що не знали одна про одну")


# ── hist-calendar-motive: чому календар САМ породжує систему конгруенцій ─────
# Ідея: цикли різної довжини йдуть паралельно; рік — це трійка позицій у них.
# Питання «який рік має цю трійку?» і є китайська теорема, ще до всякої теорії.
def fig_hist_calendar_motive():
    W, H = 940, 470
    p = []

    tracks = [("сонячний цикл", 28, 150, NEG), ("Метонів цикл", 19, 240, FIELD), ("індикт", 15, 330, POS)]
    x0, span = 300, 520
    year = 11  # довільний рік для показу позицій

    p.append(text(W / 2, 56, "рік не має власного номера — він має лише місце в кожному циклі",
                  size=12.5, color=MUTED, italic=True))

    for name, period, y, col in tracks:
        p.append(text(x0 - 22, y + 5, "%s, %d р." % (name, period), size=13, color=INK,
                      anchor="end", bold=True))
        p.append(line(x0, y, x0 + span, y, color=MUTED, sw=1.4))
        step = span / float(period)
        for k in range(period):
            cx = x0 + k * step
            on = (k == year % period)
            p.append(circle(cx, y, 7 if on else 3.2,
                            fill=col if on else "#ffffff", stroke=col if on else MUTED,
                            sw=2.0 if on else 1.0))
        p.append(text(x0 + span + 30, y + 5, "позиція %d" % (year % period),
                      size=13, color=col, anchor="start", bold=True))

    p.append(textbox(W / 2, 405,
                     "трійка (позиція, позиція, позиція) повертається рівно раз на 28 · 19 · 15 = 7980 років,\n"
                     "бо 28, 19 і 15 попарно взаємно прості — отже, трійка ОДНОЗНАЧНО називає рік",
                     size=13, fill="#eafaf0", stroke=FIELD, sw=1.8)[0])

    render(os.path.join(OUT, "calendar-motive.svg"), W, H, *p,
           title="Календар не ставить іншого питання")


# ── garner-growth: розмір проміжних (для proj-crt-solver) ────────────────────
# Ідея: у формулі-сумі кожен доданок майже завбільшки з N, ще й помножений на
# модуль, — тому проміжне переростає машинне слово. У Гарнера перемножуються
# два числа, менші за ОДИН модуль: стеля — nᵢ², і від кількості модулів не
# залежить. Числа виміряні: 6 модулів по 20 бітів, N = 120 бітів.
def fig_garner_growth():
    W, H = 880, 400
    X0, SC = 300, 3.6          # старт смуг; пікселів на біт
    p = []

    p.append(text(W / 2, 56, "шість модулів по 20 бітів кожен; зібране число N — 120 бітів",
                  size=13, color=MUTED))

    # межа машинного слова — пунктир перетинає верхню смугу й лишає нижню осторонь
    xw = X0 + 64 * SC
    p.append(text(xw, 82, "64 біти — межа машинного слова", size=12, color=MUTED))
    p.append(line(xw, 90, xw, 250, color=MUTED, sw=1.4, dash="5 4"))

    p.append(text(40, 106, "ФОРМУЛА-СУМА", size=14, color=POS, anchor="start", bold=True))
    p.append(text(40, 130, "x = Σ aᵢ · Nᵢ · Mᵢ", size=12.5, color=MUTED, anchor="start"))
    p.append(rect(X0, 96, 139 * SC, 36, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(X0 + 139 * SC - 60, 120, "139 бітів", size=13, color=POS, bold=True))

    p.append(text(40, 206, "ГАРНЕР", size=14, color=FIELD, anchor="start", bold=True))
    p.append(text(40, 230, "xᵢ = (… − xⱼ)·nⱼ⁻¹ mod nᵢ", size=12.5, color=MUTED, anchor="start"))
    p.append(rect(X0, 196, 39 * SC, 36, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(X0 + 39 * SC / 2, 220, "39 бітів", size=13, color=FIELD, bold=True))

    p.append(fitbox(40, 272, 800, 100,
                    "Доданок aᵢ·Nᵢ·Mᵢ майже завбільшки з N, помножене ще на модуль — тому росте разом з усім числом.\n"
                    "У Гарнера перемножуються два числа, менші за ОДИН модуль: стеля — nᵢ², тобто два машинні слова.\n"
                    "І ця стеля не залежить від того, скільки модулів у наборі: додайте ще шість — вона не зрушить.\n"
                    "Ліворуч від пунктиру — «вміщається в машинне слово», праворуч — «потрібна довга арифметика».",
                    size=12, fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "garner-growth.svg"), W, H, *p,
           title="Те саме завдання, два шляхи — і різні проміжні")


# ── mixed-radix-order: порядок, повернутий мішаними основами ─────────────────
# Ідея: сирі залишки не впорядковують чисел (8 = (2,3), 9 = (0,4) — жодне
# порівняння не працює). Мішано-основні цифри — позиційні, тому впорядковують:
# порівняння від старшої цифри дає 8 < 9 без збирання чисел назад.
def fig_mixed_radix_order():
    W, H = 900, 470
    p = []

    p.append(line(450, 60, 450, 396, color=MUTED, sw=1.2, dash="4 4"))

    # ── ліворуч: сирі залишки не вміють
    p.append(text(50, 74, "СИРІ ЗАЛИШКИ", size=14, color=POS, anchor="start", bold=True))
    p.append(text(50, 108, "8 → (2, 3)        9 → (0, 4)", size=15, color=INK, anchor="start"))
    p.append(text(50, 132, "за модулями 3 і 5", size=12, color=MUTED, anchor="start", italic=True))

    p.append(fitbox(50, 158, 360, 60,
                    "почленно:  2 > 0,  але  3 < 4\nсуперечність — висновку немає",
                    size=13, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(fitbox(50, 234, 360, 60,
                    "лексикографічно:  (2, 3) > (0, 4)\nтобто «8 > 9» — а це неправда",
                    size=13, fill="#fdecea", stroke=POS, sw=1.6))

    p.append(text(50, 330, "величина числа розмазана по всіх", size=12.5, color=MUTED, anchor="start"))
    p.append(text(50, 352, "залишках одразу — в жодному її немає", size=12.5, color=MUTED, anchor="start"))

    # ── праворуч: мішано-основні цифри вміють
    p.append(text(490, 74, "МІШАНО-ОСНОВНІ ЦИФРИ", size=14, color=FIELD, anchor="start", bold=True))
    p.append(text(490, 108, "8 = 2 + 2·3   →   (2, 2)", size=15, color=INK, anchor="start"))
    p.append(text(490, 134, "9 = 0 + 3·3   →   (3, 0)", size=15, color=INK, anchor="start"))
    p.append(text(490, 158, "цифри виписано від старшої; основи 3 і 5", size=12, color=MUTED,
                  anchor="start", italic=True))

    p.append(fitbox(490, 186, 360, 60,
                    "старша цифра:  2 < 3\nотже 8 < 9  —  і це правда",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.6))

    p.append(text(490, 278, "це позиційний запис, як десятковий:", size=12.5, color=MUTED, anchor="start"))
    p.append(text(490, 300, "старша цифра важить більше за всі молодші", size=12.5, color=MUTED, anchor="start"))
    p.append(text(490, 322, "разом узяті — тому порівняння працює", size=12.5, color=MUTED, anchor="start"))

    b, _, _ = textbox(670, 366, "Гарнер, 1959", size=13, bold=True, color=FIELD,
                      fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b)

    p.append(fitbox(50, 414, 800, 44,
                    "Але задарма це не дається: переведення коштує ~k² модульних множень — стільки ж, скільки й уся збірка.\n"
                    "Порядок повертається не дешево, а лише без довгої арифметики: усі проміжні лишаються в межах модуля.",
                    size=12, fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "mixed-radix-order.svg"), W, H, *p,
           title="Залишки порядку не знають — мішані основи знають")


# ── fault-attack: один біт коштує всього ключа ──────────────────────────────
# Ідея: збій в ОДНІЙ половині лишає другу цілою — і саме ця асиметрія видає
# ключ. Різниця підписів ділиться на «цілий» модуль і не ділиться на «збійний»,
# тож НСД із n витягує множник. Захист — та сама дія, тільки зроблена першим.
def fig_fault_attack():
    W, H = 920, 480
    p = []

    p.append(line(392, 58, 392, 396, color=MUTED, sw=1.2, dash="4 4"))

    # ── ліворуч: шлях підпису
    p.append(text(45, 74, "ПІДПИС ЧЕРЕЗ КТЗ", size=14, color=INK, anchor="start", bold=True))

    b, _, h0 = textbox(200, 108, "повідомлення m", size=13, fill=FILL, stroke=INK, sw=1.6)
    p.append(b)
    p.append(arrow(200, 108 + h0 / 2 + 4, 110, 148, color=INK, sw=1.6))
    p.append(arrow(200, 108 + h0 / 2 + 4, 290, 148, color=INK, sw=1.6))

    b, _, h1 = textbox(110, 172, "s₁ = m^dP mod p", size=12.5, color=POS,
                       fill="#fdecea", stroke=POS, sw=2)
    p.append(b)
    b, _, h2 = textbox(290, 172, "s₂ = m^dQ mod q", size=12.5, color=FIELD,
                       fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(b)

    p.append(text(110, 210, "тут перекинувся біт", size=11.5, color=POS, bold=True))
    p.append(text(290, 210, "ця половина ціла", size=11.5, color=FIELD, bold=True))

    p.append(arrow(110, 222, 200, 254, color=INK, sw=1.6))
    p.append(arrow(290, 222, 200, 254, color=INK, sw=1.6))

    b, _, h3 = textbox(200, 276, "склеїти за Гарнером", size=12.5, fill=FILL, stroke=INK, sw=1.6)
    p.append(b)
    p.append(arrow(200, 276 + h3 / 2 + 4, 200, 320, color=POS, sw=1.8))
    b, _, _ = textbox(200, 344, "ŝ — збійний підпис", size=13, bold=True, color=POS,
                      fill="#fdecea", stroke=POS, sw=2)
    p.append(b)

    # ── праворуч: наслідок
    p.append(text(420, 74, "НАСЛІДОК", size=14, color=INK, anchor="start", bold=True))

    p.append(text(420, 110, "ŝ ≡ s  (mod q)", size=14, color=FIELD, anchor="start", bold=True))
    p.append(text(600, 110, "половина q ціла", size=12.5, color=MUTED, anchor="start"))
    p.append(text(420, 140, "ŝ ≢ s  (mod p)", size=14, color=POS, anchor="start", bold=True))
    p.append(text(600, 140, "у половині p був збій", size=12.5, color=MUTED, anchor="start"))

    p.append(text(420, 182, "отже різниця s − ŝ ділиться на q — і не ділиться на p.", size=12.5,
                  color=INK, anchor="start"))
    p.append(text(420, 204, "Спільний дільник із n = p·q може бути лише один:", size=12.5,
                  color=INK, anchor="start"))

    b, _, _ = textbox(660, 246, "gcd(s − ŝ, n) = q", size=16, bold=True, color=POS,
                      fill="#fdecea", stroke=POS, sw=2.2)
    p.append(b)

    p.append(text(420, 300, "а правильний s навіть не потрібен — досить m:", size=12.5,
                  color=INK, anchor="start"))
    b, _, _ = textbox(660, 344, "gcd(ŝ^e − m, n) = q", size=15, bold=True, color=POS,
                      fill="#fdecea", stroke=POS, sw=2)
    p.append(b)
    p.append(text(420, 380, "Ленстра, 1996", size=12, color=MUTED, anchor="start", italic=True))

    p.append(fitbox(45, 412, 830, 52,
                    "Захист — та сама дія, тільки зроблена першим: піднести ŝ до відкритого показника e й звірити з m.\n"
                    "Виміряно: 0.15 мс проти 6.5 мс на підпис — 2.3%. Стільки коштує різниця між цілим ключем і розкладеним.",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "fault-attack.svg"), W, H, *p,
           title="Один перекинутий біт — і n розкладено на множники")


if __name__ == "__main__":
    fig_coordinates()
    fig_coprime_hinge()
    fig_construction()
    fig_rsa_crt_cost()
    fig_bezout_set()
    fig_ring_iso()
    fig_overlap_condition()
    fig_hist_threads()
    fig_hist_calendar_motive()
    fig_garner_growth()
    fig_mixed_radix_order()
    fig_fault_attack()
    print("OK: figures written to", OUT)
