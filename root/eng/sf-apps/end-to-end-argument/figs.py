# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def bracket(x1, x2, y, color, up=True, tick=12, sw=2.2):
    """Горизонтальна дужка з двома засічками. up=True — засічки вниз (дужка згори)."""
    dy = tick if up else -tick
    return (line(x1, y, x2, y, color=color, sw=sw) +
            line(x1, y, x1, y + dy, color=color, sw=sw) +
            line(x2, y, x2, y + dy, color=color, sw=sw))


# ── 1. Ланцюг передавання: що покриває перевірка на ділянці, а що — задача ─────
def fig_hop_coverage():
    W, H = 1240, 440
    frags = []

    labels = [
        "диск A\n(джерело)",
        "буфер\nпрограми A",
        "мережевий\nбуфер A",
        "пам'ять\nшлюза",
        "мережевий\nбуфер B",
        "буфер\nпрограми B",
        "диск B\n(копія)",
    ]
    cy = 260
    x0 = 110
    step = 168
    bw = 100                     # однакова ширина всіх коробок
    cxs = [x0 + i * step for i in range(len(labels))]

    # Коробки
    for cx, lab in zip(cxs, labels):
        body, w, h = textbox(cx, cy, lab, size=13, pad=9, min_w=bw)
        frags.append(body)

    # Стрілки між коробками
    half = bw / 2
    for i in range(len(cxs) - 1):
        frags.append(arrow(cxs[i] + half + 4, cy, cxs[i + 1] - half - 4, cy,
                           color=MUTED, sw=1.8))

    # Дротові ділянки — це переходи 3→4 та 4→5 (індекси 2→3 і 3→4)
    wires = [(2, 3), (3, 4)]
    for a, b in wires:
        mx = (cxs[a] + cxs[b]) / 2
        frags.append(text(mx, cy + 28, "дріт", size=12, color=NEG))

    # Сині дужки під дротовими ділянками
    yb = cy + 74
    for a, b in wires:
        frags.append(bracket(cxs[a] + half + 4, cxs[b] - half - 4, yb, NEG, up=False))
    frags.append(text(cxs[3], yb + 34, "що покриває перевірка транспорту",
                      size=14, bold=True, color=NEG))

    # Зелена дужка над усім ланцюгом
    yg = 150
    frags.append(bracket(cxs[0] - half, cxs[-1] + half, yg, FIELD, up=True))
    frags.append(text((cxs[0] + cxs[-1]) / 2, yg - 34,
                      "що вимагає задача: файл на диску B дорівнює файлові на диску A",
                      size=15, bold=True, color=FIELD))

    # Червоні позначки над проміжними коробками — «нічия земля» для ділянкових перевірок
    for cx in cxs[1:-1]:
        frags.append(circle(cx, 210, 10, fill="#fdecea", stroke=POS, sw=2))
        frags.append(text(cx, 215, "!", size=14, color=POS, bold=True))

    frags.append(text(40, H - 26,
                      "позначені місця не покриває жодна перевірка на ділянці — тільки наскрізна",
                      size=13, color=POS, anchor="start"))

    render(os.path.join(IMG, 'hop-coverage.svg'), W, H, *frags,
           title="Дві різні дужки: ділянка проти всього шляху")


# ── 2. Обрив: коли самої наскрізної перевірки перестає вистачати ──────────────
def fig_reliability_cliff():
    W, H = 1010, 490
    frags = []

    X0, X1 = 150, 920
    Y0, Y1 = 130, 400            # Y0 — рівень P=1, Y1 — рівень P=0
    N = 10000

    def px(lp):                  # lp = log10(p), від -7 до -2
        return X0 + (lp + 7) / 5.0 * (X1 - X0)

    def py(P):
        return Y0 + (1 - P) * (Y1 - Y0)

    def prob(lp):
        p = 10 ** lp
        return math.exp(N * math.log(1 - p))

    # Зони — під кривою й осями
    gx = px(-4.6)
    rx = px(-3.4)
    frags.append(rect(X0, Y0, gx - X0, Y1 - Y0, fill="#eafaf1", stroke="#eafaf1", sw=0, rx=0))
    frags.append(rect(rx, Y0, X1 - rx, Y1 - Y0, fill="#fdf0ee", stroke="#fdf0ee", sw=0, rx=0))

    # Осі
    frags.append(line(X0, Y1, X1 + 12, Y1, color=INK, sw=2))
    frags.append(line(X0, Y0 - 12, X0, Y1, color=INK, sw=2))

    # Поділки осі X
    for lp in range(-7, -1):
        x = px(lp)
        frags.append(line(x, Y1, x, Y1 + 7, color=INK, sw=1.6))
        sup = {7: "⁻⁷", 6: "⁻⁶", 5: "⁻⁵", 4: "⁻⁴", 3: "⁻³", 2: "⁻²"}[-lp]
        frags.append(text(x, Y1 + 26, "10" + sup, size=14, color=INK))

    # Поділки осі Y
    for val, lab in ((1.0, "1"), (0.5, "0.5"), (0.0, "0")):
        y = py(val)
        frags.append(line(X0 - 7, y, X0, y, color=INK, sw=1.6))
        frags.append(text(X0 - 13, y + 5, lab, size=13, color=INK, anchor="end"))

    # Крива
    pts = []
    steps = 240
    for i in range(steps + 1):
        lp = -7 + 5.0 * i / steps
        pts.append((px(lp), py(prob(lp))))
    poly = " ".join("%.1f,%.1f" % (a, b) for a, b in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
                 % (poly, INK))

    # Підписи зон — далеко від кривої: зліва під нею, справа над нею
    frags.append(mtext((X0 + gx) / 2, 300,
                       ["наскрізної перевірки", "тут досить"],
                       size=15, bold=True, color=FIELD))
    frags.append(mtext((rx + X1) / 2, 196,
                       ["без перевірки на ділянках", "передавання не завершується"],
                       size=15, bold=True, color=POS))

    # Позначка конкретної точки p = 10⁻⁴
    mx, my = px(-4), py(prob(-4))
    frags.append(circle(mx, my, 6, fill=POS, stroke=POS, sw=1))
    frags.append(line(mx - 4, my + 6, 578, 344, color=MUTED, sw=1.4))
    frags.append(text(572, 352, "10⁻⁴ — у середньому 2.7 спроби",
                      size=13, color=INK, anchor="end"))

    # Підписи осей
    frags.append(text(X0, 100, "шанс, що файл із 10 000 пакетів пройде цілим",
                      size=14, bold=True, color=INK, anchor="start"))
    frags.append(text((X0 + X1) / 2, Y1 + 60,
                      "ймовірність, що окремий пакет зіпсується на ділянці",
                      size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'reliability-cliff.svg'), W, H, *frags,
           title="Обрив: де ділянкова перевірка стає обов'язковою")


# ── 3. Три питання аргументу і що з відповідей випливає ───────────────────────
def fig_decision():
    W, H = 1190, 500
    frags = []

    qx, qw = 80, 430
    ox, ow = 690, 440
    qh, oh = 78, 78

    questions = [
        (70,  "Чи можна перевірити це,\nне маючи обох кінців?"),
        (208, "Чи здешевлює механізм нижче\nціну помилки?"),
        (346, "Чи вгадує він уподобання застосунку\n(порядок, повтори, затримку)?"),
    ]
    for qy, txt in questions:
        frags.append(fitbox(qx, qy, qw, qh, txt, size=15, bold=True,
                            fill="#eef3ff", stroke=NEG, sw=2.2))

    # Вертикальні переходи між питаннями
    for a, b in ((70, 208), (208, 346)):
        frags.append(arrow(qx + qw / 2, a + qh, qx + qw / 2, b - 6, color=MUTED, sw=1.8))

    outcomes = [
        (70,  "Функція належить кінцям —\nнижче її не завершити.", FIELD, "#eafaf1"),
        (176, "Додай як фільтр\nі міряй як продуктивність.", FIELD, "#eafaf1"),
        (272, "Не додавай: складність\nбез виграшу.", POS, "#fdf0ee"),
        (378, "Дай спосіб вимкнути —\nінакше зверху не обійти.", POS, "#fdf0ee"),
    ]
    for oy, txt, col, fill in outcomes:
        frags.append(fitbox(ox, oy, ow, oh, txt, size=15, fill=fill, stroke=col, sw=2.2))

    # Стрілки питання → наслідок
    links = [
        (70 + qh / 2, 70 + oh / 2, "ні", -14),
        (208 + qh / 2, 176 + oh / 2, "так", -16),
        (208 + qh / 2, 272 + oh / 2, "ні", 22),
        (346 + qh / 2, 378 + oh / 2, "так", 24),
    ]
    for ys, ye, lab, dy in links:
        frags.append(arrow(qx + qw + 6, ys, ox - 6, ye, color=INK, sw=1.8))
        mxl = (qx + qw + ox) / 2
        myl = ys + (ye - ys) * ((mxl - (qx + qw + 6)) / ((ox - 6) - (qx + qw + 6)))
        frags.append(text(mxl, myl + dy, lab, size=15, bold=True, color=INK))

    render(os.path.join(IMG, 'decision.svg'), W, H, *frags,
           title="Три питання, які треба провести для кожної функції")


# ── 4. Хроніка: практика без імені → формулювання → канон і розлам ────────────
def fig_e2e_timeline():
    XL, XV, XT = 300, 330, 358      # праворуч дати · вісь · початок тексту
    y0 = 96

    rows = [
        ('h', None, "ПРАКТИКА, ЯКУ ЩЕ НЕ НАЗВАЛИ", MUTED),
        ('e', "1971–1976", "CYCLADES: за цілісність відповідає хост, а не мережа", MUTED),
        ('e', "1973", "Бренстед: шифрування має бути наскрізним", MUTED),
        ('e', "1978", "TCP ділять на TCP та IP — щоб голос обійшов повтори", MUTED),
        ('h', None, "ФОРМУЛЮВАННЯ", NEG),
        ('e', "грудень 1980", "семінар ACM у Фолбруку: ідею обговорюють у вузькому колі", NEG),
        ('e', "8–10.04.1981", "Париж, 2-га ICDCS: перша публікація, чотири сторінки", NEG),
        ('e', "листопад 1984", "ACM TOCS 2(4), 277–288: канонічний текст", NEG),
        ('h', None, "КАНОН, А ТОДІ РОЗЛАМ", POS),
        ('e', "1988", "Кларк, SIGCOMM: спільна доля стану і сполучення", FIELD),
        ('e', "травень 1994", "RFC 1631: NAT — коробка, що переписує адреси в дорозі", POS),
        ('e', "червень 1996", "RFC 1958: аргумент записано в архітектуру інтернету", FIELD),
        ('e', "1998", "Рід, Зальцер, Кларк: де аргумент шкодить", POS),
        ('e', "серпень 2001", "Блументаль і Кларк: кінцям більше не можна довіряти", POS),
        ('e', "2002", "RFC 3234: перепис проміжних коробок; критика Мурса", POS),
        ('e', "2017", "вимір перехоплення TLS: розлам усередині шифру", POS),
    ]

    ys, y = [], y0
    for r in rows:
        ys.append(y)
        y += 58 if r[0] == 'h' else 52
    H = ys[-1] + 60
    W = 1010

    frags = [text(XT, 48, "Сорок років наскрізного аргументу",
                  size=17, bold=True, color=INK, anchor="start"),
             line(XV, y0 - 34, XV, ys[-1] + 26, color="#c9ced6", sw=2.4)]

    for (kind, date, txt, col), yy in zip(rows, ys):
        if kind == 'h':
            frags.append(rect(XV - 7, yy - 7, 14, 14, fill=col, stroke=col, sw=0, rx=2))
            frags.append(text(XT, yy + 6, txt, size=16, bold=True, color=col, anchor="start"))
        else:
            frags.append(circle(XV, yy, 6, fill=col, stroke=col, sw=1))
            frags.append(text(XL, yy + 5, date, size=14, color=MUTED, anchor="end"))
            frags.append(text(XT, yy + 5, txt, size=15, color=INK, anchor="start"))

    render(os.path.join(IMG, 'e2e-timeline.svg'), W, H, *frags,
           title="Хроніка наскрізного аргументу")


# ── 5. Площа блоку відновлення: три стратегії на сітці «ділянки × пакети» ──────
def fig_recovery_area():
    W, H = 1250, 470
    frags = []

    frags.append(text(W / 2, 52,
                      "рядок — ділянка маршруту (k = 3),   стовпець — пакет (з N = 10 000 показано 8)",
                      size=14, color=MUTED))
    frags.append(text(W / 2, 76,
                      "заливка — що саме йде наново, коли всередині знайдено помилку",
                      size=14, color=MUTED))

    cw, ch = 30, 36
    cols, rows_n = 8, 3
    gy = 160
    panels = [
        (90,  ["одна ділянка,", "один пакет"], lambda r, c: r == 0 and c == 0,
         "A = s·u = 1", "×1.0001"),
        (500, ["весь шлях,", "один пакет"], lambda r, c: c == 0,
         "A = k = 3", "×1.0003"),
        (910, ["весь шлях,", "увесь файл"], lambda r, c: True,
         "A = k·N = 30 000", "×20.1"),
    ]

    for px0, title, sel, alab, flab in panels:
        cx = px0 + cols * cw / 2
        frags.append(mtext(cx, 112, title, size=16, bold=True, color=INK))
        for r in range(rows_n):
            for c in range(cols):
                on = sel(r, c)
                frags.append(rect(px0 + c * cw, gy + r * ch, cw, ch,
                                  fill=("#fdd9d3" if on else "#ffffff"),
                                  stroke=(POS if on else "#c8ccd2"),
                                  sw=(2.0 if on else 1.0), rx=0))
        frags.append(text(px0 + cols * cw + 22, gy + rows_n * ch / 2 + 5, "…",
                          size=20, color=MUTED))
        frags.append(text(cx, gy + rows_n * ch + 42, alab, size=16, bold=True, color=POS))
        frags.append(mtext(cx, gy + rows_n * ch + 78,
                           ["переданих пакето-ділянок", flab + " від найкращого"],
                           size=14, color=INK))

    frags.append(text(W / 2, 436,
                      "E = k·N·(1 − p)⁻ᴬ ≈ k·N·e^(pA)   —   важить лише площа A, не те, де стоїть перевірка",
                      size=16, bold=True, color=NEG))

    render(os.path.join(IMG, 'recovery-area.svg'), W, H, *frags,
           title="Вартість повтору залежить від площі блоку, а не від його місця")


# ── 6. Мінімум сумарної роботи за площею блоку ────────────────────────────────
def fig_cost_vs_area():
    W, H = 1070, 545
    frags = []
    p, c = 1e-4, 0.1

    X0, X1 = 165, 950
    Y0, Y1 = 120, 440          # Y0 — рівень 10², Y1 — рівень 10⁻³

    def px(la):                # la = log10(A), 0..5
        return X0 + la / 5.0 * (X1 - X0)

    def py(v):                 # v — значення (не логарифм)
        lv = math.log10(max(v, 1e-3))
        return Y1 - (lv + 3) / 5.0 * (Y1 - Y0)

    frags.append(line(X0, Y1, X1 + 14, Y1, color=INK, sw=2))
    frags.append(line(X0, Y0 - 14, X0, Y1, color=INK, sw=2))

    sup = {0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵"}
    for la in range(0, 6):
        x = px(la)
        frags.append(line(x, Y1, x, Y1 + 7, color=INK, sw=1.6))
        frags.append(text(x, Y1 + 27, "10" + sup[la], size=14, color=INK))
    ysup = {-3: "10⁻³", -2: "10⁻²", -1: "10⁻¹", 0: "1", 1: "10", 2: "100"}
    for lv in range(-3, 3):
        y = py(10.0 ** lv)
        frags.append(line(X0 - 7, y, X0, y, color=INK, sw=1.6))
        frags.append(text(X0 - 13, y + 5, ysup[lv], size=13, color=INK, anchor="end"))

    def curve(fn, la_max, color, sw, dash=False):
        pts = []
        steps = 260
        for i in range(steps + 1):
            la = la_max * i / steps
            a = 10.0 ** la
            v = fn(a)
            if v < 1e-3 or v > 100:
                continue
            pts.append((px(la), py(v)))
        poly = " ".join("%.1f,%.1f" % (u, v) for u, v in pts)
        d = ' stroke-dasharray="7,6"' if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (poly, color, sw, d))

    frags.append(curve(lambda a: c / a, 5.0, NEG, 2.0, dash=True))
    frags.append(curve(lambda a: math.exp(p * a) - 1, 4.67, POS, 2.0, dash=True))
    frags.append(curve(lambda a: (math.exp(p * a) - 1) + c / a, 4.67, INK, 3.2))

    astar = math.sqrt(c / p)
    vstar = (math.exp(p * astar) - 1) + c / astar
    mx, my = px(math.log10(astar)), py(vstar)
    frags.append(line(mx, my + 11, mx, Y1, color=FIELD, sw=1.6, dash="6,5"))
    frags.append(mtext(270, 404,
                       ["A* = √(c / p) ≈ 32", "зайвого лише 2√(cp) ≈ 0.6 %"],
                       size=15, bold=True, color=FIELD))

    # Чотири точки на кривій — підписані номерами, розшифровка в легенді ліворуч
    marks = [
        (1.0,     "1", 16, -14, POS),
        (3.0,     "2", 2, -22, POS),
        (astar,   "3", 0, -22, FIELD),
        (30000.0, "4", -24, -16, POS),
    ]
    for a, num, dx, dy, col in marks:
        v = (math.exp(p * a) - 1) + c / a
        x, y = px(math.log10(a)), py(v)
        frags.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        frags.append(text(x + dx, y + dy, num, size=15, bold=True, color=col))

    legend = [
        ("1", "A = 1 — повтор на ділянці, по пакету", POS),
        ("2", "A = 3 — наскрізний, по пакету", POS),
        ("3", "A = 32 — найдешевша площа", FIELD),
        ("4", "A = 30 000 — наскрізний, усім файлом", POS),
    ]
    ly = 152
    for num, lab, col in legend:
        frags.append(text(200, ly, num, size=15, bold=True, color=col))
        frags.append(text(218, ly, lab, size=14, color=INK, anchor="start"))
        ly += 27

    frags.append(text(500, 425, "плата за перевірки:  c / A",
                      size=14, color=NEG, anchor="start"))
    frags.append(text(790, 186, "плата за перепосилання:  e^(pA) − 1",
                      size=14, color=POS, anchor="end"))

    frags.append(text(X0, 82, "зайва робота на одну пакето-ділянку   (p = 10⁻⁴, c = 0.1)",
                      size=15, bold=True, color=INK, anchor="start"))
    frags.append(text((X0 + X1) / 2, Y1 + 64,
                      "площа блоку відновлення  A = s·u  (пакето-ділянок)",
                      size=15, bold=True, color=INK))

    render(os.path.join(IMG, 'cost-vs-area.svg'), W, H, *frags,
           title="Мінімум роботи: площа блоку A* = √(c/p)")


# ── 7. Ціна одного відновлення в часі: сусід проти кінця ──────────────────────
def fig_recovery_latency():
    W, H = 1190, 570
    frags = []

    hop = 30                     # 30 px = d = 5 мс
    bot = 476
    top = 152
    names = ["A", "R₁", "R₂", "B"]

    def panel(x0, title, events, clean_y, hit_y, blab):
        xs = [x0 + i * 108 for i in range(4)]
        out = [text(x0 + 162, 94, title, size=16, bold=True, color=INK)]
        for x, nm in zip(xs, names):
            out.append(circle(x, 126, 15, fill="#eef3ff", stroke=NEG, sw=2))
            out.append(text(x, 131, nm, size=14, bold=True, color=NEG))
            out.append(line(x, 144, x, bot, color=MUTED, sw=1.4, dash="4,5"))
        out.append(line(xs[0] - 34, clean_y, xs[3] + 20, clean_y,
                        color=FIELD, sw=1.6, dash="7,6"))
        out.append(text(xs[0] - 36, clean_y - 10, "мав дійти сюди",
                        size=13, color=FIELD, anchor="start"))
        for (a, b, y1, y2, col, mark) in events:
            out.append(arrow(xs[a], y1, xs[b], y2, color=col, sw=2.2))
            if mark:
                out.append(text((xs[a] + xs[b]) / 2 + 20, (y1 + y2) / 2 - 10,
                                mark, size=17, bold=True, color=POS))
        bx = xs[3] + 44
        out.append(line(bx, clean_y, bx, hit_y, color=POS, sw=2.4))
        out.append(line(bx - 9, clean_y, bx + 9, clean_y, color=POS, sw=2.4))
        out.append(line(bx - 9, hit_y, bx + 9, hit_y, color=POS, sw=2.4))
        out.append(text(bx + 13, (clean_y + hit_y) / 2 + 5, blab,
                        size=15, bold=True, color=POS, anchor="start"))
        return out

    e1 = [
        (0, 1, top, top + hop, INK, None),
        (1, 2, top + hop, top + 2 * hop, INK, "✗"),
        (2, 1, top + 2 * hop + 8, top + 3 * hop + 8, POS, None),
        (1, 2, top + 3 * hop + 8, top + 4 * hop + 8, FIELD, None),
        (2, 3, top + 4 * hop + 8, top + 5 * hop + 8, FIELD, None),
    ]
    frags += panel(112, "повтор між сусідами", e1,
                   top + 3 * hop, top + 5 * hop + 8, "2d")

    e2 = [
        (0, 1, top, top + hop, INK, None),
        (1, 2, top + hop, top + 2 * hop, INK, "✗"),
        (3, 2, top + 3 * hop + 8, top + 4 * hop + 8, POS, None),
        (2, 1, top + 4 * hop + 8, top + 5 * hop + 8, POS, None),
        (1, 0, top + 5 * hop + 8, top + 6 * hop + 8, POS, None),
        (0, 1, top + 6 * hop + 8, top + 7 * hop + 8, FIELD, None),
        (1, 2, top + 7 * hop + 8, top + 8 * hop + 8, FIELD, None),
        (2, 3, top + 8 * hop + 8, top + 9 * hop + 8, FIELD, None),
    ]
    frags += panel(690, "повтор із кінця", e2,
                   top + 3 * hop, top + 9 * hop + 8, "2kd")

    frags.append(text(W / 2, 52,
                      "час іде вниз, один крок = d = 5 мс;   червоне — звістка про втрату, зелене — повторне передавання",
                      size=14, color=MUTED))
    frags.append(text(295, 528, "втрачено 2d = 10 мс", size=16, bold=True, color=INK))
    frags.append(text(875, 528, "втрачено 2kd = 30 мс", size=16, bold=True, color=INK))

    render(os.path.join(IMG, 'recovery-latency.svg'), W, H, *frags,
           title="Ціна одного відновлення в часі: RTT ділянки проти RTT шляху")


# ── 8. Сліпа пляма інтернет-контрольної суми: перестановка однакової парності ──
def fig_parity_blindspot():
    W, H = 1200, 450
    frags = []

    B = [0x3A, 0x1F, 0xC4, 0x07]
    names = ["b₀", "b₁", "b₂", "b₃"]
    weights = ["×256", "×1", "×256", "×1"]

    def words(bs):
        return (bs[0] << 8) | bs[1], (bs[2] << 8) | bs[3]

    def panel(x0, i, j, verdict_col, verdict):
        cw, gap = 96, 22
        out = []
        after = list(B)
        after[i], after[j] = after[j], after[i]

        head = "перестановка %s ↔ %s" % (names[i], names[j])
        sub = "обидва байти на парних місцях" if (i % 2 == j % 2) else "місця різної парності"
        out.append(text(x0 + (4 * cw + 3 * gap) / 2, 76, head, size=16, bold=True, color=INK))
        out.append(text(x0 + (4 * cw + 3 * gap) / 2, 100, sub, size=13, color=MUTED))

        cxs = []
        for k in range(4):
            x = x0 + k * (cw + gap)
            cxs.append(x + cw / 2)
            hot = (k == i or k == j)
            out.append(text(x + cw / 2, 130, weights[k], size=13, color=MUTED))
            out.append(rect(x, 146, cw, 62,
                            fill=("#fdecea" if hot else FILL),
                            stroke=(POS if hot else LINE), sw=(2.4 if hot else 1.5)))
            out.append(text(x + cw / 2, 186, "0x%02X" % B[k], size=19, bold=True,
                            color=(POS if hot else INK)))
            out.append(text(x + cw / 2, 232, names[k], size=14, color=MUTED))

        y = 262
        out.append(line(cxs[i], y, cxs[j], y, color=POS, sw=2.2))
        out.append(line(cxs[i], y, cxs[i], y - 12, color=POS, sw=2.2))
        out.append(line(cxs[j], y, cxs[j], y - 12, color=POS, sw=2.2))

        w0, w1 = words(B)
        a0, a1 = words(after)
        out.append(text(x0, 306, "до:     0x%04X + 0x%04X = %d" % (w0, w1, w0 + w1),
                        size=15, color=INK, anchor="start"))
        out.append(text(x0, 336, "після:  0x%04X + 0x%04X = %d" % (a0, a1, a0 + a1),
                        size=15, color=INK, anchor="start"))
        out.append(text(x0, 384, verdict, size=16, bold=True, color=verdict_col, anchor="start"))
        return out

    frags += panel(70, 0, 2, POS, "сума та сама — перевірка мовчить")
    frags += panel(660, 0, 1, FIELD, "сума інша на 255·(0x3A − 0x1F) = 6885")

    frags.append(line(620, 66, 620, 400, color="#c9ced6", sw=1.6, dash="6,6"))

    render(os.path.join(IMG, 'parity-blindspot.svg'), W, H, *frags,
           title="Сума складає байти з вагою за місцем — порядок їй байдужий")


# ── 9. Скільки байтів до першої непоміченої помилки: розкид дорівнює середньому ─
def _first_miss_samples(R, p, L=1024, seed=20260802):
    """Модель стенда: три ділянки з частотою p на байт, псування — перестановка
    пари байтів; ділянкова перевірка сліпа до копії в ретрансляторі і до
    перестановок однакової парності на дротах."""
    import random
    rng = random.Random(seed)
    rate = 3 * p
    lg = math.log(1.0 - rate)
    out = []
    for _ in range(R):
        total = 0
        while True:
            total += int(math.floor(math.log(1.0 - rng.random()) / lg)) + 1
            stage = rng.randrange(3)
            i = rng.randrange(L)
            j = rng.randrange(L)
            while j == i:
                j = rng.randrange(L)
            if rng.getrandbits(8) == rng.getrandbits(8):
                continue                      # байти однакові — зміни не сталося
            if stage != 1 and (i % 2) != (j % 2):
                continue                      # ділянкова перевірка зловила
            out.append(total)
            break
    return out


def fig_miss_histogram():
    W, H = 1150, 540
    frags = []

    R, p = 2000, 1e-6
    xs = _first_miss_samples(R, p)
    MiB = 1048576.0
    mean = sum(xs) / R
    sd = math.sqrt(sum((v - mean) ** 2 for v in xs) / (R - 1))
    srt = sorted(xs)
    med = srt[R // 2]

    X0, X1 = 130, 1050
    Y0, Y1 = 130, 410
    NB, TOP = 25, 2.5            # 25 смуг по 0.1 МіБ + переповнення
    bw = (X1 - X0) / (NB + 1)

    bins = [0] * (NB + 1)
    for v in xs:
        k = int(v / MiB / (TOP / NB))
        bins[min(k, NB)] += 1
    hmax = 0.22                  # верх шкали за часткою прогонів

    frags.append(line(X0, Y1, X1 + 14, Y1, color=INK, sw=2))
    frags.append(line(X0, Y0 - 16, X0, Y1, color=INK, sw=2))

    for k in range(NB + 1):
        f = bins[k] / R
        h = f / hmax * (Y1 - Y0)
        x = X0 + k * bw
        col = MUTED if k == NB else NEG
        frags.append(rect(x + 2, Y1 - h, bw - 4, h, fill=("#dfe6f7" if k < NB else "#e8eaee"),
                          stroke=col, sw=1.4, rx=2))

    for t in range(0, 6):
        val = t * 0.5
        x = X0 + val / TOP * NB * bw
        frags.append(line(x, Y1, x, Y1 + 7, color=INK, sw=1.6))
        frags.append(text(x, Y1 + 27, "%.1f" % val, size=13, color=INK))
    frags.append(text(X0 + NB * bw + bw / 2, Y1 + 27, "далі", size=12, color=MUTED))

    for f in (0.0, 0.05, 0.10, 0.15, 0.20):
        y = Y1 - f / hmax * (Y1 - Y0)
        frags.append(line(X0 - 7, y, X0, y, color=INK, sw=1.6))
        frags.append(text(X0 - 13, y + 5, "%d%%" % round(f * 100), size=13, color=INK, anchor="end"))

    xm = X0 + (mean / MiB) / TOP * NB * bw
    xd = X0 + (med / MiB) / TOP * NB * bw
    frags.append(line(xd, Y0 - 10, xd, Y1, color=FIELD, sw=2.0, dash="6,5"))
    frags.append(line(xm, Y0 - 10, xm, Y1, color=POS, sw=2.2, dash="6,5"))
    frags.append(text(xd - 10, Y0 - 20, "медіана %.2f МіБ" % (med / MiB),
                      size=14, bold=True, color=FIELD, anchor="end"))
    frags.append(text(xm + 10, Y0 - 20, "середнє %.2f МіБ" % (mean / MiB),
                      size=14, bold=True, color=POS, anchor="start"))

    frags.append(mtext(X1 - 40, 196,
                       ["σ = %.2f МіБ — рівно як середнє." % (sd / MiB),
                        "%d%% прогонів кінчаються до 100 КіБ," % round(100 * sum(1 for v in xs if v < 102400) / R),
                        "найдовший тут — %.1f МіБ." % (max(xs) / MiB),
                        "Один прогін не доводить нічого."],
                       size=14, color=INK, anchor="end", lh=1.45))

    frags.append(text(X0, 96, "частка з %d незалежних прогонів стенда" % R,
                      size=14, bold=True, color=INK, anchor="start"))
    frags.append(text((X0 + X1) / 2, Y1 + 62,
                      "скільки МіБ пройшло до першої помилки, якої ділянкова перевірка не побачила",
                      size=15, bold=True, color=INK))

    render(os.path.join(IMG, 'miss-histogram.svg'), W, H, *frags,
           title="Розкид дорівнює середньому: геометричний розподіл першого пропуску")

    print("miss-histogram: mean=%.0f (%.3f МіБ)  median=%.0f  sd=%.0f  min=%d  max=%d  <100КіБ=%.3f"
          % (mean, mean / MiB, med, sd, min(xs), max(xs),
             sum(1 for v in xs if v < 102400) / R))


if __name__ == "__main__":
    fig_hop_coverage()
    fig_reliability_cliff()
    fig_decision()
    fig_e2e_timeline()
    fig_recovery_area()
    fig_cost_vs_area()
    fig_recovery_latency()
    fig_parity_blindspot()
    fig_miss_histogram()
    print("OK: figures written to", IMG)
