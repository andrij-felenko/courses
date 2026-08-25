# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

LIGHT = ["#fdecea", "#eef4ff", "#eafaf0", "#f3eafa"]
COLS  = [POS, NEG, FIELD, "#8e44ad"]


# ── granularity: одиниця незалежності в програмі vs одиниця власності в залізі ──
# Ідея статті в одному малюнку: програма ділить пам'ять на ЗМІННІ, апаратура —
# на ЛІНІЇ, і власність оформлюється на цілу лінію. Там, де межі не збігаються,
# незалежні дані стають спільними без відома програми.

def fig_granularity():
    W, H = 800, 450
    p = []

    p.append(line(400, 62, 400, 315, color="#d8dde3", sw=1.3, dash="5 4"))

    # ── ліворуч: погляд програми ──
    p.append(text(205, 82, "Як бачить ПРОГРАМА", size=13, color=NEG, bold=True))

    p.append(text(120, 118, "потік A", size=11, color=INK, bold=True))
    p.append(text(300, 118, "потік B", size=11, color=INK, bold=True))
    p.append(arrow(120, 126, 120, 146, color=MUTED, sw=1.5))
    p.append(arrow(300, 126, 300, 146, color=MUTED, sw=1.5))

    p.append(fitbox(58, 150, 124, 46, "лічильник a", size=11,
                    fill=LIGHT[1], stroke=NEG, color=INK, bold=True))
    p.append(fitbox(238, 150, 124, 46, "лічильник b", size=11,
                    fill=LIGHT[1], stroke=NEG, color=INK, bold=True))

    p.append(text(205, 232, "дві окремі змінні,", size=11.5, color=INK))
    p.append(text(205, 250, "жодного спільного байта", size=11.5, color=INK))
    p.append(text(205, 282, "одиниця незалежності = ЗМІННА", size=11, color=NEG, bold=True))

    # ── праворуч: погляд заліза ──
    p.append(text(600, 82, "Як бачить ЗАЛІЗО", size=13, color=POS, bold=True))

    p.append(text(500, 118, "потік A", size=11, color=INK, bold=True))
    p.append(text(700, 118, "потік B", size=11, color=INK, bold=True))
    p.append(arrow(505, 126, 560, 148, color=MUTED, sw=1.5))
    p.append(arrow(695, 126, 640, 148, color=MUTED, sw=1.5))

    p.append(rect(452, 152, 296, 52, fill="none", stroke=POS, sw=1.8))
    p.append(rect(460, 160, 140, 36, fill=LIGHT[0], stroke=POS, sw=1.2, rx=3))
    p.append(text(530, 183, "a", size=12, color=INK, bold=True))
    p.append(rect(602, 160, 138, 36, fill=LIGHT[0], stroke=POS, sw=1.2, rx=3))
    p.append(text(671, 183, "b", size=12, color=INK, bold=True))
    p.append(text(600, 224, "одна кеш-лінія — 64 байти", size=11, color=MUTED))

    p.append(text(600, 252, "власник у кожну мить — рівно одне ядро", size=11.5, color=INK))
    p.append(text(600, 282, "одиниця власності = ЛІНІЯ", size=11, color=POS, bold=True))

    # ── висновок ──
    p.append(fitbox(46, 336, 708, 74,
                    "Дві незалежні змінні опинилися в межах однієї лінії —\n"
                    "і апаратура оформлює власність на них РАЗОМ, як на один об'єкт.\n"
                    "Ядра починають ділити те, чого програма не ділила: це й є хибне спільне.",
                    size=12, fill="#ffffff", stroke=POS, color=INK))

    render(os.path.join(OUT, "granularity.svg"), W, H, *p,
           title="Дві різні одиниці «однієї речі»")


# ── pingpong: куди дівається час, коли лінію треба щоразу передавати ───────────
# Ідея: порівняти дві часові стрічки. Своя лінія — записи щільні, простоїв нема.
# Спільна лінія — на кожен корисний запис припадає передача власності, і обидва
# ядра стоять у черзі за нею.

def fig_pingpong():
    W, H = 840, 540
    p = []

    # ── блок 1: своя лінія ──
    p.append(text(430, 64, "Кожне ядро пише у СВОЮ лінію", size=13, color=FIELD, bold=True))

    for i, y in enumerate((108, 152)):
        p.append(text(96, y + 4, "ядро %s" % "AB"[i], size=11, color=INK, anchor="end", bold=True))
        p.append(line(110, y, 800, y, color="#c7ccd2", sw=1.2))
        for k in range(30):
            x = 122 + k * 22
            p.append(rect(x, y - 9, 10, 18, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=2))

    p.append(text(430, 194, "лінія весь час у стані «моя»: запис коштує близько наносекунди",
                  size=11, color=INK))

    p.append(line(60, 218, 780, 218, color="#d8dde3", sw=1.2, dash="5 4"))

    # ── блок 2: спільна лінія ──
    p.append(text(430, 248, "Обидва ядра пишуть в ОДНУ лінію", size=13, color=POS, bold=True))

    ya, yb = 306, 406
    p.append(text(96, ya + 4, "ядро A", size=11, color=INK, anchor="end", bold=True))
    p.append(text(96, yb + 4, "ядро B", size=11, color=INK, anchor="end", bold=True))
    p.append(line(110, ya, 800, ya, color="#c7ccd2", sw=1.2))
    p.append(line(110, yb, 800, yb, color="#c7ccd2", sw=1.2))

    seg, x0 = 162, 128
    for k in range(4):
        xs = x0 + k * seg
        own, other = (ya, yb) if k % 2 == 0 else (yb, ya)
        # власник: спершу чекав на переїзд, тоді один корисний запис
        p.append(rect(xs, own - 11, seg - 34, 22, fill="#fdecea", stroke=POS, sw=1.1, rx=3))
        p.append(rect(xs + seg - 30, own - 11, 22, 22, fill=LIGHT[2], stroke=FIELD, sw=1.3, rx=3))
        # той, хто чекає на свою чергу, стоїть увесь відтинок
        p.append(rect(xs, other - 11, seg - 8, 22, fill="#fdecea", stroke=POS, sw=1.1, rx=3))
        # переїзд лінії до наступного власника
        if k < 3:
            nxt = yb if own == ya else ya
            p.append(arrow(xs + seg - 19, own + (13 if nxt > own else -13),
                           xs + seg + 4, nxt - (13 if nxt > own else -13),
                           color=MUTED, sw=1.5))

    p.append(text(430, 462, "на КОЖЕН корисний запис — одна передача лінії між ядрами: десятки наносекунд",
                  size=11.5, color=POS, bold=True))

    # ── легенда ──
    p.append(rect(150, 486, 20, 16, fill="#fdecea", stroke=POS, sw=1.1, rx=3))
    p.append(text(180, 499, "простій: ядро чекає на володіння лінією", size=10.5,
                  color=INK, anchor="start"))
    p.append(rect(520, 486, 20, 16, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=3))
    p.append(text(550, 499, "корисний запис", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "pingpong.svg"), W, H, *p,
           title="Куди дівається час: пінг-понг однієї лінії")


# ── partition: як нарізка роботи вирішує долю ліній ────────────────────────────
# Ідея: одна й та сама робота, чотири потоки, різниця лише в порядку роздачі
# елементів. Почергово — у кожній лінії сидять усі чотири потоки. Блоками —
# лінія цілком належить одному потокові.

def fig_partition():
    W, H = 880, 480
    p = []

    cellw, cellh, n = 22, 30, 32
    x0 = 100

    # легенда потоків
    for t in range(4):
        lx = 214 + t * 130
        p.append(rect(lx, 48, 18, 16, fill=LIGHT[t], stroke=COLS[t], sw=1.2, rx=2))
        p.append(text(lx + 26, 61, "потік %d" % t, size=10.5, color=INK, anchor="start"))

    def row(y, owner_of, caption, ccol):
        p.append(text(440, y - 26, caption, size=12.5, color=ccol, bold=True))
        for i in range(n):
            t = owner_of(i)
            x = x0 + i * cellw
            p.append(rect(x + 1, y + 1, cellw - 2, cellh - 2,
                          fill=LIGHT[t], stroke=COLS[t], sw=1.1, rx=2))
        for g in range(4):
            gx = x0 + g * 8 * cellw
            p.append(rect(gx - 3, y - 5, 8 * cellw + 6, cellh + 10,
                          fill="none", stroke=INK, sw=1.5))
            p.append(text(gx + 4 * cellw, y + cellh + 26, "лінія %d" % (g + 1),
                          size=10, color=MUTED))

    row(112, lambda i: i % 4,
        "Почергово: елемент i дістається потокові i mod 4", POS)
    p.append(text(440, 194, "у кожній лінії сидять усі чотири потоки — кожна лінія стає ареною",
                  size=11.5, color=POS, bold=True))

    p.append(line(60, 220, 820, 220, color="#d8dde3", sw=1.2, dash="5 4"))

    row(280, lambda i: i // 8,
        "Блоками: перші вісім елементів — потокові 0, наступні вісім — потокові 1…", FIELD)
    p.append(text(440, 362, "кожна лінія цілком належить одному потокові — спільних ліній немає",
                  size=11.5, color=FIELD, bold=True))

    p.append(fitbox(86, 392, 708, 62,
                    "Робота та сама, потоків стільки ж — різниця лише в тому, ЯК її нарізано.\n"
                    "Коли межі шматків збігаються з межами ліній, хибне спільне зникає саме собою.",
                    size=12, fill="#ffffff", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "partition.svg"), W, H, *p,
           title="Нарізка роботи вирішує, чи ділитимуть ядра лінії")


# ── scaling: сумарний темп записів як функція числа ядер (вставка math) ──
# Дві гілки моделі в одному малюнку: доки лінія не насичена, темп росте лінійно;
# щойно вона насичена — полиця 1/(p·t), яка не залежить від n. Синя лінія —
# рівень одного потоку: усе, що нижче за неї, означає програш паралелізму.

def fig_scaling():
    import math
    W, H = 860, 530
    WR, T = 1.4, 20.0                      # нс: запис у власну лінію; передача володіння
    X0, X1, Y0, Y1 = 120.0, 640.0, 80.0, 420.0
    NMAX = 16

    def px(n):  return X0 + (n - 1) / (NMAX - 1.0) * (X1 - X0)
    def py(v):  return Y1 - (math.log10(v) - 1.0) / 3.0 * (Y1 - Y0)

    def total(n, frac):
        D = (1 - frac) * WR + frac * T     # нс попиту одного ядра на одиницю роботи
        return min(n / D, 1.0 / (frac * T)) * 1000.0    # млн записів/с

    def poly(pts, color, sw=2.8):
        d = " ".join("%.1f,%.1f" % q for q in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"/>' % (d, color, sw))

    one = 1000.0 / WR                      # 714 млн/с — один потік, суперничати нема з ким
    p = []

    p.append(rect(X0, py(one), X1 - X0, Y1 - py(one), fill="#fdecea", stroke="none", rx=0))

    for v in (10, 100, 1000, 10000):
        y = py(v)
        p.append(line(X0, y, X1, y, color="#dfe4ea", sw=1.1))
        p.append(text(X0 - 10, y + 4, "%d" % v, size=11.5, color=MUTED, anchor="end"))

    p.append(line(X0, Y0 - 6, X0, Y1, color=INK, sw=1.6))
    p.append(line(X0, Y1, X1 + 8, Y1, color=INK, sw=1.6))
    for n in (1, 2, 4, 8, 12, 16):
        x = px(n)
        p.append(line(x, Y1, x, Y1 + 5, color=INK, sw=1.4))
        p.append(text(x, Y1 + 20, str(n), size=12, color=INK))
    p.append(text(380, Y1 + 42, "число ядер n", size=13, color=INK, bold=True))
    p.append(text(58, 52, "сумарний темп записів у спільну лінію, млн/с (логарифмічна шкала)",
                  size=12.5, color=MUTED, anchor="start"))

    p.append(line(X0, py(one), X1, py(one), color=NEG, sw=2.0, dash="7 5"))
    p.append(text(X0 + 8, py(one) - 8, "один потік без суперництва — 714 млн/с",
                  size=12, color=NEG, anchor="start", bold=True))

    for frac, col, lab, cap in ((0.01, FIELD, "p = 1 %", "стеля 5000 млн/с"),
                                (0.10, "#d97b1a", "p = 10 %", "стеля 500 млн/с"),
                                (1.00, POS, "p = 100 %", "стеля 50 млн/с")):
        pts = [(px(n), py(total(n, frac))) for n in range(2, NMAX + 1)]
        p.append(poly(pts, col))
        p.append(text(X1 + 12, pts[-1][1] - 4, lab, size=12.5, color=col, anchor="start", bold=True))
        p.append(text(X1 + 12, pts[-1][1] + 13, cap, size=11.5, color=MUTED, anchor="start"))

    kx, ky = px(7.93), py(total(8, 0.01))
    p.append(circle(kx, ky, 4.5, fill="#ffffff", stroke=FIELD, sw=2.2))
    p.append(text(kx - 8, ky - 20, "злам n* ≈ 8", size=11.5, color=FIELD, anchor="end", bold=True))

    p.append(text(390, 300, "нижче синьої лінії — чотири ядра повільніші за одне",
                  size=12.5, color=POS, bold=True))

    p.append(fitbox(90, 466, 690, 50,
                    "Запис у власну лінію w = 1.4 нс, передача володіння t = 20 нс, r = t/w ≈ 14.\n"
                    "Стеля 1/(p·t) не залежить від n — за зламом ядра лише ділять ту саму лінію.",
                    size=12, fill="#f7f9fb", stroke="#c9d2da", color=INK))

    render(os.path.join(OUT, "scaling.svg"), W, H, *p,
           title="Лінійне зростання до зламу, далі полиця, що не залежить від n")


# ── threshold: стеля прискорення як функція частки спільних записів ──
# Гіпербола S∞ = 1/(p·r) у логарифмічних осях — пряма з нахилом −1. Точка,
# де вона перетинає одиницю, і є порогом беззбитковості p* = w/t.

def fig_threshold():
    import math
    W, H = 860, 530
    WR = 1.4
    X0, X1, Y0, Y1 = 130.0, 690.0, 70.0, 410.0
    VIO = "#7d3c98"

    def px(v): return X0 + (math.log10(v) + 4.0) / 4.0 * (X1 - X0)
    def py(s): return Y0 + (3.0 - math.log10(s)) / 5.0 * (Y1 - Y0)

    p = []
    p.append(rect(X0, py(1.0), X1 - X0, Y1 - py(1.0), fill="#fdecea", stroke="none", rx=0))

    for s in (1000, 100, 10, 1, 0.1, 0.01):
        y = py(s)
        p.append(line(X0, y, X1, y, color="#dfe4ea", sw=1.1))
        p.append(text(X0 - 10, y + 4, ("%g" % s) + "×", size=11.5, color=MUTED, anchor="end"))

    for v, lab in ((1e-4, "0.01 %"), (1e-3, "0.1 %"), (1e-2, "1 %"), (1e-1, "10 %"), (1.0, "100 %")):
        x = px(v)
        p.append(line(x, Y1, x, Y1 + 5, color=INK, sw=1.4))
        p.append(text(x, Y1 + 20, lab, size=12, color=INK))

    p.append(line(X0, Y0 - 6, X0, Y1, color=INK, sw=1.6))
    p.append(line(X0, Y1, X1 + 8, Y1, color=INK, sw=1.6))
    p.append(text(410, Y1 + 42, "частка спільних записів p (логарифмічна шкала)",
                  size=13, color=INK, bold=True))
    p.append(text(58, 52, "стеля прискорення S∞ = 1/(p·r) — у скільки разів n ядер швидші за одне",
                  size=12.5, color=MUTED, anchor="start"))

    p.append(line(X0, py(1.0), X1, py(1.0), color=INK, sw=1.8, dash="7 5"))
    p.append(text(X0 + 6, py(1.0) - 9, "беззбитковість: S∞ = 1", size=12, color=INK,
                  anchor="start", bold=True))

    for t_, col in ((20.0, POS), (100.0, VIO)):
        r = t_ / WR
        ax, ay = px(1e-4), py(1.0 / (1e-4 * r))
        bx, by = px(1.0), py(1.0 / (1.0 * r))
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.8"/>'
                 % (ax, ay, bx, by, col))
        p.append(circle(px(1.0 / r), py(1.0), 5, fill="#ffffff", stroke=col, sw=2.4))

    p.append(rect(510, 96, 195, 92, fill="#ffffff", stroke="#c9d2da", sw=1.4))
    p.append(text(607, 120, "поріг p* = w/t", size=12.5, color=INK, bold=True))
    p.append(line(524, 141, 552, 141, color=POS, sw=3.2))
    p.append(text(560, 146, "20 нс → 7 %", size=12, color=POS, anchor="start", bold=True))
    p.append(line(524, 169, 552, 169, color=VIO, sw=3.2))
    p.append(text(560, 174, "100 нс → 1.4 %", size=12, color=VIO, anchor="start", bold=True))

    p.append(fitbox(90, 466, 690, 50,
                    "Пряма з нахилом −1: удесятеро рідший спільний запис — удесятеро вища стеля.\n"
                    "Щоб масштабування дожило до n ядер, треба p ≤ 1/(n·r): 16 ядер, 20 нс → 0.44 %.",
                    size=12, fill="#f7f9fb", stroke="#c9d2da", color=INK))

    render(os.path.join(OUT, "threshold.svg"), W, H, *p,
           title="Стеля прискорення падає обернено до частки спільних записів")


# ── hist: п'ять означень Болоскі й Скотта проти трьох вимог ────────────────
# Наочно головний висновок роботи 1993 року: кожен кандидат провалює рівно ту
# вимогу, яку інші витримують, — і жоден не бере всі три одразу.

def fig_definitions():
    W, H = 980, 534
    p = []

    x0, wname = 40, 372
    cw, gap = 168, 12
    cx = [x0 + wname + gap + i * (cw + gap) for i in range(3)]
    y0, rh, rgap = 100, 50, 10

    heads = ["збігається\nз інтуїцією", "математично\nточне", "можна\nвиміряти"]
    for i, hd in enumerate(heads):
        p.append(fitbox(cx[i], y0 - 62, cw, 54, hd, size=12,
                        fill="#eef4ff", stroke=NEG, color=INK, bold=True))

    rows = [
        ("блок в одне слово",              "ні",  "так", "так"),
        ("інтервали без справжнього обміну", "так", "так", "ні"),
        ("інтервали навмання (евристика)",  "так", "ні",  "так"),
        ("хибне на всю довжину прогону",    "ні",  "так", "так"),
        ("ручне доопрацювання коду",        "так", "ні",  "так"),
        ("розклад ціни на складники",       "так", "так", "лише межа"),
    ]

    for r, (name, a, b, c) in enumerate(rows):
        y = y0 + r * (rh + rgap)
        p.append(fitbox(x0, y, wname, rh, name, size=12.5,
                        fill="#f7f9fb", stroke="#c9d2da", color=INK))
        for i, v in enumerate([a, b, c]):
            if v == "так":
                fill, stroke, col = "#eafaf0", FIELD, "#1e7a45"
            elif v == "ні":
                fill, stroke, col = "#fdecea", POS, "#a03024"
            else:
                fill, stroke, col = "#fff7e6", "#c98a1e", "#8a5a10"
            p.append(fitbox(cx[i], y, cw, rh, v, size=12.5,
                            fill=fill, stroke=stroke, color=col, bold=True))

    p.append(fitbox(40, H - 58, W - 80, 46,
                    "У кожному рядку є червоне. За десять років після появи слова ніхто не подав означення, "
                    "яке водночас відповідає інтуїції, точне й вимірне.",
                    size=12.5, fill="#f3eafa", stroke="#8e44ad", color=INK))

    render(os.path.join(OUT, "definitions.svg"), W, H, *p,
           title="П'ять кандидатів на означення проти трьох вимог (Болоскі й Скотт, 1993)")


# ── hist: та сама хвороба на сторінці й на лінії ───────────────────────────
# Наскрізна думка вставки: між IVY і сучасним кристалом змінилося все, крім
# самого правила — незалежні дані мусять лежати в різних одиницях власності.

def fig_page_vs_line():
    W, H = 940, 544
    p = []

    lx, lw = 34, 236
    ax, bx, colw = 292, 616, 300
    y0, rh, rgap = 100, 62, 12

    p.append(fitbox(ax, y0 - 60, colw, 52, "IVY, 1986\nпрограмна спільна пам'ять", size=12.5,
                    fill="#eef4ff", stroke=NEG, color=INK, bold=True))
    p.append(fitbox(bx, y0 - 60, colw, 52, "багатоядерний кристал\nапаратна когерентність", size=12.5,
                    fill="#fdecea", stroke=POS, color=INK, bold=True))

    rows = [
        ("одиниця власності",  "сторінка ≈ 1 КБ",           "кеш-лінія 64 Б"),
        ("хто відбирає",       "ядро ОС за пасткою\nзахисту сторінки", "протокол когерентності\nв кремнію"),
        ("куди їде",           "мережею до іншої\nмашини",  "між кешами\nна тому самому кристалі"),
        ("ціна одного переїзду", "кілька порядків над\nлокальним доступом", "≈ 20 нс проти ≈ 1.4 нс"),
        ("як не платити",      "класти незалежні дані\nв різні сторінки", "класти незалежні дані\nв різні лінії"),
    ]

    for r, (name, a, b) in enumerate(rows):
        y = y0 + r * (rh + rgap)
        p.append(fitbox(lx, y, lw, rh, name, size=12.5,
                        fill="#ffffff", stroke="#c9d2da", color=MUTED, bold=True))
        p.append(fitbox(ax, y, colw, rh, a, size=12, fill="#f7f9fb", stroke="#c9d2da", color=INK))
        p.append(fitbox(bx, y, colw, rh, b, size=12, fill="#f7f9fb", stroke="#c9d2da", color=INK))

    p.append(fitbox(34, H - 56, W - 68, 44,
                    "Одиниця стиснулася приблизно в шістнадцять разів, переїзд подешевшав на порядки — "
                    "а останній рядок збігається слово в слово.",
                    size=12.5, fill="#eafaf0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "page-vs-line.svg"), W, H, *p,
           title="Та сама хвороба на двох одиницях власності")


if __name__ == "__main__":
    fig_granularity()
    fig_pingpong()
    fig_partition()
    fig_scaling()
    fig_threshold()
    fig_definitions()
    fig_page_vs_line()
    print("figs: готово")
