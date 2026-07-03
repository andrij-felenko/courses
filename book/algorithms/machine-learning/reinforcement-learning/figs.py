# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: контур «агент ↔ середовище» ─────────────────────────────────────
# Серце RL: замкнений цикл. Агент бачить стан s, обирає дію a; середовище
# відповідає новим станом s' і винагородою r. Стрілки йдуть по колу — це не
# «вхід→вихід» одного разу, а безкінечна взаємодія в часі.
def fig_loop():
    W, H = 720, 360
    p = []

    # дві коробки: агент ліворуч, середовище праворуч
    ax, ay, aw, ah = 70, 130, 210, 100
    ex, ey, ew, eh = 440, 130, 210, 100
    p.append(rect(ax, ay, aw, ah, fill="#eef4ff", stroke=NEG, sw=2.2, rx=10))
    p.append(text(ax + aw / 2, ay + 38, "АГЕНТ", size=19, color=NEG, bold=True))
    p.append(text(ax + aw / 2, ay + 66, "стратегія π", size=14, color=MUTED))
    p.append(rect(ex, ey, ew, eh, fill="#eafbf0", stroke=FIELD, sw=2.2, rx=10))
    p.append(text(ex + ew / 2, ey + 38, "СЕРЕДОВИЩЕ", size=19, color=FIELD, bold=True))
    p.append(text(ex + ew / 2, ey + 66, "стан світу", size=14, color=MUTED))

    # верхня дуга: агент → середовище (дія a)
    ya = ay + 6
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ax + aw, ya, ax + aw + 40, ya - 78, ex - 40, ya - 78, ex, ya, POS))
    b, bw, bh = textbox((ax + aw + ex) / 2, ya - 66, "дія  a", size=15, bold=True,
                        fill=BG, stroke=POS, color=POS)
    p.append(b)

    # нижня дуга: середовище → агент (новий стан s' і винагорода r)
    yb = ay + ah - 6
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ex, yb, ex - 40, yb + 86, ax + aw + 40, yb + 86, ax + aw, yb, INK))
    b, bw, bh = textbox((ax + aw + ex) / 2, yb + 74, "стан s'   ·   винагорода r", size=15,
                        bold=True, fill=BG, stroke=INK)
    p.append(b)

    p.append(text(W / 2, 28, "Замкнений контур навчання з підкріпленням", size=17, bold=True))
    render(os.path.join(OUT, "rl-loop.svg"), W, H, *p)


# ── Фігура 2: розвідка vs визиск ──────────────────────────────────────────────
# Три «важелі» (як гральні автомати). Один уже перевірений і дає надійний, але
# скромний виграш. Два — незвідані: під ними ховається невідома величина, серед
# якої може бути краще. Тягнути перевірений = визиск; пробувати нове = розвідка.
def fig_explore_exploit():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 30, "Розвідка проти визиску", size=17, bold=True))

    cols = [
        (140, "перевірений",  "ВИЗИСК",   "+3", "надійно, але скромно",   NEG,   "#eef4ff"),
        (360, "незвіданий",   "РОЗВІДКА", "?",  "може бути +10, може −5", POS,   "#fdf3f0"),
        (580, "незвіданий",   "РОЗВІДКА", "?",  "може бути +8, може 0",   POS,   "#fdf3f0"),
    ]
    base = 300
    for cx, name, tag, val, note, col, fill in cols:
        # «важіль» — коробка з ручкою
        bw2, bh2 = 130, 150
        by = base - bh2
        p.append(rect(cx - bw2 / 2, by, bw2, bh2, fill=fill, stroke=col, sw=2.2, rx=10))
        # ручка-важіль
        p.append(line(cx + bw2 / 2, by + 24, cx + bw2 / 2 + 26, by + 4, color=col, sw=3.4))
        p.append(circle(cx + bw2 / 2 + 26, by + 4, 7, fill=col, stroke=col, sw=1))
        p.append(text(cx, by + 66, val, size=34, color=col, bold=True))
        p.append(text(cx, by + 110, tag, size=13, color=col, bold=True))
        p.append(text(cx, by - 12, name, size=14, color=INK, bold=True))
        # підпис-нотатка під важелем
        p.append(fitbox(cx - 96, base + 20, 192, 40, note, size=12, fill=BG, stroke=col, color=INK))

    render(os.path.join(OUT, "explore-exploit.svg"), W, H, *p)


# ── Фігура 3: закидання винагороди назад по траєкторії ────────────────────────
# Ланцюжок станів s0→s1→…→ціль. Винагорода приходить лише в кінці (+10). Питання
# розподілу заслуги: який із ранніх ходів був корисний? TD «протікає» цінністю
# назад — кожен стан переймає частку цінності наступного, тож сигнал доходить
# і до перших кроків.
def fig_credit():
    W, H = 760, 320
    p = []
    p.append(text(W / 2, 30, "Розподіл заслуги: винагорода тече назад", size=17, bold=True))

    n = 5
    xs = [110 + i * 135 for i in range(n)]
    y = 150
    r = 30
    labels = ["s₀", "s₁", "s₂", "s₃", "ціль"]
    # оцінка цінності, що «просочилася» назад (тьмяніє від цілі до старту)
    vals = ["V≈4", "V≈6", "V≈8", "V≈9", "+10"]
    fills = ["#eef4ff", "#e7f0ff", "#deebff", "#d3e4ff", "#eafbf0"]
    strokes = [NEG, NEG, NEG, NEG, FIELD]

    for i in range(n):
        p.append(circle(xs[i], y, r, fill=fills[i], stroke=strokes[i], sw=2.4))
        p.append(text(xs[i], y - 2, labels[i], size=16, color=INK, bold=True))
        p.append(text(xs[i], y + 15, vals[i], size=12, color=MUTED))
        # стрілка-дія вперед (звичайний рух агента)
        if i < n - 1:
            p.append(arrow(xs[i] + r + 3, y, xs[i + 1] - r - 3, y, color=INK, sw=1.8))

    # велика винагорода в кінці
    b, bw, bh = textbox(xs[-1], y - 78, "винагорода +10", size=14, bold=True,
                        fill="#eafbf0", stroke=FIELD, color=FIELD)
    p.append(b)
    p.append(arrow(xs[-1], y - 78 + bh / 2 + 2, xs[-1], y - r - 3, color=FIELD, sw=1.8))

    # пунктирні дуги «протікання» цінності назад, від цілі до старту
    for i in range(n - 1, 0, -1):
        x2, x1 = xs[i], xs[i - 1]
        p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="5 4" '
                 'marker-end="url(#arrow)"/>'
                 % (x2 - r * 0.3, y + r + 4, x2 - 40, y + r + 58,
                    x1 + 40, y + r + 58, x1 + r * 0.3, y + r + 4, POS))
    p.append(text(W / 2, y + r + 84, "цінність просочується назад: кожен стан переймає частку наступного",
                  size=12, color=POS, italic=True))
    render(os.path.join(OUT, "credit-assignment.svg"), W, H, *p)


# ── Фігура 4 (вставка hist): родовід ідеї ─────────────────────────────────────
# Часова стрічка від закону ефекту Торндайка (1898) до AlphaGo (2016). Кольором
# розрізнено ТРИ роди внеску, які легко сплутати: спостереження/ідея (синє),
# теорія/математика (сіре), працююча реалізація/система (зелене). Сенс фігури —
# показати, що «навчання з підкріпленням» не винайшла одна особа й не один рік:
# ідея, теорія й реалізація прийшли з різних рук і з різницею в десятиліття.
def fig_lineage():
    W, H = 900, 460
    p = []
    p.append(text(W / 2, 30, "Родовід навчання з підкріпленням", size=18, bold=True))
    p.append(text(W / 2, 52, "ідея · теорія · працююча система — різні руки, різні десятиліття",
                  size=12.5, color=MUTED, italic=True))

    # три роди внеску → три кольори
    IDEA = NEG          # спостереження / ідея — синє
    THEORY = "#7a5cc0"  # теорія / математика — фіолетове
    BUILT = FIELD       # реалізація / система — зелене

    # горизонтальна вісь часу
    x0, x1 = 60, W - 34
    axis_y = 232
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
             % (x1, axis_y, x1 - 12, axis_y - 5, x1 - 12, axis_y + 5, INK))

    # Кусково-лінійна вісь: 1985–2020 навмисне РОЗТЯГНУТО, щоб пізній кластер
    # (1988/1989/1992/2016) не наліз сам на себе. Ключові точки (рік → частка ширини).
    span = x1 - 24 - x0
    knots = [(1890, 0.0), (1955, 0.34), (1985, 0.50), (2020, 1.0)]
    def xf(yr):
        for (ya, fa), (yb, fb) in zip(knots, knots[1:]):
            if yr <= yb:
                t = (yr - ya) / (yb - ya)
                return x0 + span * (fa + t * (fb - fa))
        return x0 + span

    # риски-десятиліття
    for yr in range(1900, 2021, 20):
        xx = xf(yr)
        p.append(line(xx, axis_y - 5, xx, axis_y + 5, color=MUTED, sw=1.4))
        p.append(text(xx, axis_y + 22, str(yr), size=11, color=MUTED))

    # віхи: (рік, підпис, ім'я, рід, рівень) — рівень задає ряд картки, щоб рознести
    # близькі за роком події вгору/вниз на різні висоти без накладань.
    #  рівень:  2 = високо вгорі, 1 = вгорі, -1 = внизу, -2 = низько внизу
    miles = [
        (1898, "закон ефекту",            "Торндайк", IDEA,    1),
        (1953, "динамічне\nпрограмування", "Беллман",  THEORY,  1),
        (1988, "часова\nрізниця (TD)",     "Саттон",   THEORY, -1),
        (1989, "Q-навчання",              "Воткінс",  THEORY,  2),
        (1992, "TD-Gammon",               "Тезауро",  BUILT,  -2),
        (2016, "AlphaGo",                 "DeepMind", BUILT,   1),
    ]
    row_y = {2: axis_y - 128, 1: axis_y - 62, -1: axis_y + 54, -2: axis_y + 120}
    for yr, lab, who, col, lvl in miles:
        xx = xf(yr)
        cy = row_y[lvl]
        up = lvl > 0
        lines = lab.split("\n")
        bw = max([text_width(s, 12.5, True) for s in lines] + [text_width(who, 11.5, True)]) + 20
        bw = max(bw, 96)
        bh = 24 + len(lines) * 17
        bx, by = xx - bw / 2, cy - bh / 2
        # точка на осі + виноска до картки
        p.append(circle(xx, axis_y, 6, fill=col, stroke=col, sw=1))
        y_from = axis_y - 6 if up else axis_y + 6
        y_to = (by + bh) if up else by
        p.append(line(xx, y_from, xx, y_to, color=col, sw=1.6, dash="4 3"))
        # картка-віха
        p.append(rect(bx, by, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        p.append(mtext(xx, by + 17, lines, size=12.5, color=INK, bold=True, lh=1.25))
        p.append(text(xx, by + bh - 7, who, size=11.5, color=col, bold=True))
        # рік — біля точки на осі, з боку, протилежного картці
        p.append(text(xx, axis_y + (16 if up else -11), str(yr), size=10.5, color=col, bold=True))

    # легенда трьох родів
    lx, ly = x0, H - 20
    items = [("спостереження / ідея", IDEA), ("теорія / математика", THEORY),
             ("працююча система", BUILT)]
    for lab, col in items:
        p.append(circle(lx, ly - 4, 6, fill=col, stroke=col, sw=1))
        p.append(text(lx + 12, ly, lab, size=12, color=INK, anchor="start"))
        lx += text_width(lab, 12) + 56

    render(os.path.join(OUT, "rl-lineage.svg"), W, H, *p)


fig_loop()
fig_explore_exploit()
fig_credit()
fig_lineage()
print("figures written to", OUT)
