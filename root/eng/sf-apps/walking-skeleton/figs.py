# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Тонка нитка крізь усі вузли VS повні вузли без нитки ─────────────────────
# Головна ідея: кістяк проходить ВСІ архітектурні вузли наскрізь, але в кожному
# бере лише один найтонший шлях. Ліворуч — кістяк (тонка суцільна нитка від краю
# до краю). Праворуч — звична помилка: два вузли зроблені «повністю», але не
# з'єднані — стик іще не перевірено, ризик цілий.
def fig_thread():
    W, H = 860, 420
    p = []
    p.append(text(W / 2, 28, "Кістяк бере один тонкий шлях, але веде його крізь УСІ вузли до кінця",
                  size=14, bold=True))

    nodes = ["давач", "прошивка\nМК", "радіо-\nканал", "сервер", "екран\nоператора"]

    # ── ЛІВОРУЧ: ходячий кістяк — тонка суцільна нитка наскрізь ──
    lx0 = 55
    p.append(text(lx0 + 150, 62, "ходячий кістяк", size=13, bold=True, color=FIELD))
    p.append(text(lx0 + 150, 78, "один шлях, але від краю до краю", size=9.5, color=MUTED))
    ny = 150
    bx, bw, gap = lx0, 58, 20
    centers = []
    for i, lbl in enumerate(nodes):
        x = bx + i * (bw + gap)
        p.append(rect(x, ny, bw, 46, fill="#e7f7ee", stroke=FIELD, sw=1.6))
        for j, ln in enumerate(lbl.split("\n")):
            p.append(text(x + bw / 2, ny + 22 + j * 13 - (6 if "\n" in lbl else 0), ln, size=9.5, color=INK))
        centers.append(x + bw / 2)
    # суцільна нитка крізь усі
    for i in range(len(centers) - 1):
        p.append(arrow(centers[i] + bw / 2 - 2, ny + 23, centers[i + 1] - bw / 2 + 2, ny + 23,
                       color=FIELD, sw=2.2))
    p.append(text(lx0 + 150, ny + 90, "одне значення доходить до екрана —", size=10.5, color=INK))
    p.append(text(lx0 + 150, ny + 106, "усі стики вже працюють", size=10.5, bold=True, color=FIELD))

    # роздільник
    p.append(line(W / 2, 55, W / 2, 375, color=MUTED, sw=1, dash="4,4"))

    # ── ПРАВОРУЧ: два «повні» вузли без нитки ──
    rx0 = W / 2 + 40
    p.append(text(rx0 + 150, 62, "вузли поодинці", size=13, bold=True, color=POS))
    p.append(text(rx0 + 150, 78, "готові, але не з'єднані", size=9.5, color=MUTED))
    filled = [0, 3]  # давач і сервер зроблені «повністю»
    rcenters = []
    for i, lbl in enumerate(nodes):
        x = rx0 + i * (bw + gap)
        if i in filled:
            p.append(rect(x, ny, bw, 46, fill="#fadbd6", stroke=POS, sw=2))
        else:
            p.append(rect(x, ny, bw, 46, fill=BG, stroke=MUTED, sw=1.3, rx=6))
        for j, ln in enumerate(lbl.split("\n")):
            col = POS if i in filled else MUTED
            p.append(text(x + bw / 2, ny + 22 + j * 13 - (6 if "\n" in lbl else 0), ln, size=9.5, color=col))
        rcenters.append(x + bw / 2)
    # розірвані стики
    for i in range(len(rcenters) - 1):
        p.append(line(rcenters[i] + bw / 2 - 2, ny + 23, rcenters[i + 1] - bw / 2 + 2, ny + 23,
                      color=POS, sw=1.6, dash="4,4"))
    # хрестик на першому стику
    sx = (rcenters[0] + bw / 2 + rcenters[1] - bw / 2) / 2
    p.append(line(sx - 6, ny + 17, sx + 6, ny + 29, color=POS, sw=2.4))
    p.append(line(sx - 6, ny + 29, sx + 6, ny + 17, color=POS, sw=2.4))
    p.append(text(rx0 + 150, ny + 90, "два вузли «готові», а разом", size=10.5, color=INK))
    p.append(text(rx0 + 150, ny + 106, "не працювали жодного разу", size=10.5, bold=True, color=POS))

    p.append(text(W / 2, H - 18,
                  "Ризик архітектури живе не всередині вузлів, а на стиках між ними — кістяк перевіряє саме стики першими",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "thread.svg"), W, H, *p)


# ── 2. Коли виявляється хиба інтеграції: вузли-спершу VS кістяк-спершу ──────────
# Дві часові смуги. Зверху — будуємо вузол за вузлом, стик перевіряємо в кінці:
# помилка інтеграції зринає пізно, коли все дороге до переробки. Знизу — кістяк
# у перший тиждень: та сама помилка зринає одразу, поки дешево.
def fig_risk_timing():
    W, H = 880, 400
    p = []
    p.append(text(W / 2, 28, "Кістяк не прибирає ризик інтеграції — він переносить зустріч із ним на початок",
                  size=14, bold=True))

    x0, x1 = 250, 800
    # шкала часу
    def X(f):
        return x0 + f * (x1 - x0)

    # ── смуга А: спершу вузли ──
    yA = 120
    p.append(text(x0 - 20, yA - 4, "спершу вузли", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(x0 - 20, yA + 12, "поодинці", size=12, bold=True, color=POS, anchor="end"))
    p.append(line(x0, yA, x1, yA, color=INK, sw=2))
    p.append(arrow(x1 - 2, yA, x1 + 8, yA, color=INK, sw=2))
    # відрізки роботи над окремими вузлами
    segs = [(0.02, 0.20, "давач"), (0.22, 0.42, "прошивка"), (0.44, 0.64, "сервер"), (0.66, 0.82, "екран")]
    for a, b, lbl in segs:
        p.append(rect(X(a), yA - 12, X(b) - X(a), 24, fill="#fdece9", stroke=POS, sw=1.3, rx=4))
        p.append(text((X(a) + X(b)) / 2, yA + 5, lbl, size=9.5, color=INK))
    # вибух інтеграції наприкінці
    ix = X(0.92)
    p.append(circle(ix, yA, 12, fill=POS, stroke=POS, sw=2))
    p.append(text(ix, yA + 5, "!", size=15, bold=True, color=BG))
    p.append(text(ix, yA - 22, "стик зібрано", size=10, color=POS, bold=True, anchor="middle"))
    p.append(text(x1, yA + 34, "хиба інтеграції спливає пізно — переробляти дорого", size=10.5,
                  color=POS, bold=True, anchor="end"))

    # ── смуга Б: спершу кістяк ──
    yB = 260
    p.append(text(x0 - 20, yB - 4, "спершу ходячий", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(text(x0 - 20, yB + 12, "кістяк", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(line(x0, yB, x1, yB, color=INK, sw=2))
    p.append(arrow(x1 - 2, yB, x1 + 8, yB, color=INK, sw=2))
    # тонкий наскрізний зріз одразу
    p.append(rect(X(0.02), yB - 12, X(0.13) - X(0.02), 24, fill="#e7f7ee", stroke=FIELD, sw=1.4, rx=4))
    p.append(text((X(0.02) + X(0.13)) / 2, yB + 5, "кістяк", size=9.5, color=INK))
    # вибух одразу
    ix2 = X(0.15)
    p.append(circle(ix2, yB, 12, fill=FIELD, stroke=FIELD, sw=2))
    p.append(text(ix2, yB + 5, "!", size=15, bold=True, color=BG))
    p.append(text(ix2 + 20, yB - 22, "стик зібрано в перший тиждень", size=10, color=FIELD, bold=True, anchor="start"))
    # далі — нарощування м'язів на живому кістяку
    for a, b, lbl in [(0.22, 0.42, "давач"), (0.44, 0.64, "прошивка"), (0.66, 0.98, "решта")]:
        p.append(rect(X(a), yB - 12, X(b) - X(a), 24, fill="#eef6ff", stroke=NEG, sw=1.2, rx=4))
        p.append(text((X(a) + X(b)) / 2, yB + 5, lbl, size=9.5, color=INK))
    p.append(text(x1, yB + 34, "хибу знайдено дешево — м'ясо наростає на робочому кістяку", size=10.5,
                  color=INK, anchor="end"))

    p.append(text(W / 2, H - 18,
                  "Та сама помилка коштує тим менше, чим раніше її зустріти; кістяк призначає зустріч на перший тиждень",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "risk-timing.svg"), W, H, *p)


# ── 3. Родовід ідеї в часі: куля, кістяк, загострення, милиці ──────────────────
# Історична фігура для вставки hist-. Одна вісь часу з подіями-віхами. Дві
# споріднені лінії: «трасувальна куля» (Hunt/Thomas) і «ходячий кістяк»
# (Cockburn), що сходяться в спільну ідею; далі загострення (Freeman/Pryce,
# 97 Things) і уточнення (Adzic). Підписи розставлені з ЗАПАСОМ — над віссю й
# під нею по черзі, щоб жоден напис не ліг на інший.
def fig_lineage():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Родовід ідеї: дві споріднені лінії сходяться в один прийом",
                  size=15, bold=True))

    x0, x1 = 70, 830
    axy = 240                      # вісь часу
    # роки, які реально розставляємо (нерівномірно — за подіями, не за масштабом)
    years = [1996, 1999, 2000, 2004, 2009, 2014]
    fx = {1996: 0.02, 1999: 0.20, 2000: 0.30, 2004: 0.50, 2009: 0.74, 2014: 0.97}

    def X(f):
        return x0 + f * (x1 - x0)

    # головна вісь часу
    p.append(line(x0 - 10, axy, x1 + 18, axy, color=INK, sw=2.4))
    p.append(arrow(x1 + 6, axy, x1 + 22, axy, color=INK, sw=2.4))
    for y in years:
        xx = X(fx[y])
        p.append(line(xx, axy - 6, xx, axy + 6, color=INK, sw=2))
        p.append(text(xx, axy + 22, str(y), size=11, bold=True, color=MUTED))

    # ── подія-картка над/під віссю; side=+1 знизу, −1 зверху ──
    # Без поводків-ліній до карток: вузол-кружок на осі + близька картка вже
    # читаються як пара, а зайва лінія ризикує перетнути напис (svgcheck).
    def event(year, side, title_lines, who, color, fill):
        xx = X(fx[year])
        # вузол на осі
        p.append(circle(xx, axy, 6.5, fill=color, stroke=color, sw=2))
        bw, bh = 168, 52
        gap = 46
        by = axy - gap - bh if side < 0 else axy + gap
        bx = xx - bw / 2
        bx = max(x0 - 8, min(bx, x1 + 18 - bw))     # не за край
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=color, sw=1.6, rx=7))
        for j, ln in enumerate(title_lines):
            p.append(text(bx + bw / 2, by + 18 + j * 15, ln, size=10.5, bold=(j == 0), color=INK))
        p.append(text(bx + bw / 2, by + bh - 7, who, size=9, italic=True, color=MUTED))
        return xx, by, bh

    # трасувальна куля (споріднена лінія) — зверху
    tx, tby, tbh = event(1999, -1, ["трасувальна куля", "лишається в системі"],
                         "Hunt · Thomas, 1999", NEG, "#eef3fe")
    # коинаж кістяка — знизу
    cx96, _, _ = event(1996, +1, ["термін «ходячий кістяк»", "тонко зв'язана архітектура"],
                       "Cockburn, 1996", FIELD, "#e7f7ee")
    # канонічне визначення — зверху
    cx04, cby, cbh = event(2004, -1, ["канонічне визначення", "зв'язати головні складники"],
                          "Crystal Clear, 2004", FIELD, "#e7f7ee")
    # загострення — знизу
    fx09, fby, fbh = event(2009, +1, ["загострення: авто", "збірка·розгортання·тест"],
                          "Freeman · Pryce, 2009", INK, FILL)
    # уточнення милицями — зверху
    ax14, _, _ = event(2014, -1, ["«на милиці»: спершу", "лице, бекенд — потім"],
                      "Adzic, 2014", POS, "#fdecea")

    # тонкий місток спорідненості: куля (1999) ⇢ канонічне визначення (2004)
    p.append(text(W / 2, H - 20,
                  "Куля Ганта й Томаса та кістяк Кокберна — одна ідея наскрізної нитки, що лишається; далі її загострили й уточнили",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p)


# ── 4. Стик як пучок домовленостей + спад шансу наскрізної збірки ───────────────
# Дві панелі. Ліворуч: один стик між двома частинами — це не одна річ, а пучок
# незалежних домовленостей (формат, порядок байтів, одиниці, помилки, версія),
# кожна з яких — окремий шанс на розбіжність. Праворуч: як росте число вузлів,
# так падає ймовірність, що весь ланцюг стикнеться з першого разу — крива
# P(N) = (1−q)^(a·(N−1)) при q=0.1, a=4. Головна думка: ризик сидить на стиках і
# з кожним вузлом множиться.
def fig_seam_decay():
    import math
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 26, "Ризик сидить на стиках: один стик — пучок домовленостей, і з кожним вузлом шанс тане",
                  size=14, bold=True))
    p.append(line(470, 52, 470, 400, color=MUTED, sw=1, dash="4,4"))

    # ── ЛІВОРУЧ: один стик і пучок домовленостей на ньому ──
    p.append(text(238, 58, "Один стик — пучок незалежних домовленостей", size=11, bold=True, color=FIELD))
    p.append(rect(70, 110, 78, 46, fill="#eef6ff", stroke=NEG, sw=1.4))
    p.append(text(109, 138, "частина A", size=10.5, color=INK))
    p.append(rect(330, 110, 78, 46, fill="#eef6ff", stroke=NEG, sw=1.4))
    p.append(text(369, 138, "частина B", size=10.5, color=INK))
    p.append(text(239, 100, "стик", size=10, color=POS, bold=True))
    p.append(arrow(150, 133, 328, 133, color=INK, sw=1.6))
    p.append(line(239, 118, 239, 150, color=POS, sw=2, dash="3,3"))
    p.append(text(239, 184, "на ньому мусять збігтися:", size=10.5, color=INK))
    seams = ["формат кадру", "порядок байтів і полів", "одиниці й масштаб",
             "семантика помилок і таймаутів", "версія та автентифікація"]
    py = 200
    for s in seams:
        p.append(fitbox(78, py, 322, 28, s, size=10.5, fill=FILL, stroke=MUTED, sw=1.2, rx=5))
        py += 34
    p.append(text(239, py + 8, "кожна — окремий шанс на розбіжність", size=10, italic=True, color=MUTED))

    # ── ПРАВОРУЧ: спад P(наскрізна збірка з першого разу) з ростом вузлів ──
    p.append(text(690, 58, "Шанс, що весь ланцюг стикнеться з першого разу", size=11, bold=True, color=POS))
    axx, axr = 530, 858
    ayt, ayb = 112, 360
    p.append(line(axx, ayt, axx, ayb, color=INK, sw=1.8))
    p.append(line(axx, ayb, axr, ayb, color=INK, sw=1.8))
    for v, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]:
        yy = ayb - v * (ayb - ayt)
        p.append(line(axx - 4, yy, axx, yy, color=INK, sw=1.4))
        p.append(text(axx - 10, yy + 4, lab, size=10, color=MUTED, anchor="end"))
    Ns = list(range(2, 9))

    def X(n):
        return axx + 16 + (n - 2) * (axr - axx - 24) / 6.0

    def Y(v):
        return ayb - v * (ayb - ayt)

    pts = [(X(n), Y(0.9 ** (4 * (n - 1)))) for n in Ns]
    for n in Ns:
        xx = X(n)
        p.append(line(xx, ayb, xx, ayb + 4, color=INK, sw=1.4))
        p.append(text(xx, ayb + 18, str(n), size=10, color=MUTED))
    p.append(text((axx + axr) / 2, ayb + 36, "число вузлів N", size=10.5, color=INK))
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=POS, sw=2.2))
    for xx, yy in pts:
        p.append(circle(xx, yy, 3.2, fill=BG, stroke=POS, sw=1.8))
    x5, y5 = X(5), Y(0.9 ** 16)
    p.append(circle(x5, y5, 5, fill=POS, stroke=POS, sw=1.6))
    p.append(mtext(700, 150, ["5 вузлів (4 стики) —", "≈ 18% з першого разу"], size=10.5, color=INK))
    p.append(line(700, 176, x5 + 1, y5 - 7, color=MUTED, sw=1.1))

    p.append(text(W / 2, 442,
                  "Ризик архітектури живе на стиках; що більше вузлів, то менший шанс, що все стикнеться саме собою",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "seam-decay.svg"), W, H, *p)


# ── 5. Вартість переробки росте з часом виявлення дефекту ───────────────────────
# Одна пара осей: x — коли дефект знайдено (день 1 → реліз T), y — скільки коштує
# його переробити. Дві криві: оптимістична лінійна (переробка ∝ обсяг залежного
# коду, накопиченого лінійно) і реалістична компаундна (залежності множаться,
# ∝ e^(g·t)). Кістяк знаходить дефект на день 1 (майже даром), вузли-поодинці —
# аж на релізі (найдорожче). Брекет справа: той самий дефект у e^(g·T) разів
# дорожчий пізно.
def fig_discovery_cost():
    import math
    W, H = 920, 430
    p = []
    p.append(text(W / 2, 26, "Той самий дефект коштує тим більше, чим пізніше його знайдено", size=14, bold=True))
    x0, x1 = 95, 800
    y0 = 350
    p.append(arrow(x0, y0, x0, 64, color=INK, sw=1.8))
    p.append(arrow(x0, y0, x1 + 6, y0, color=INK, sw=1.8))
    p.append(text(104, 56, "вартість переробки", size=10.5, color=INK, anchor="start"))
    p.append(text(x0, y0 + 18, "день 1", size=10, color=MUTED))
    p.append(text(x1, y0 + 18, "реліз T", size=10, color=MUTED))
    p.append(text(450, 390, "час виявлення t_d →", size=10.5, color=INK))

    def X(f):
        return x0 + f * (x1 - x0)

    k = 3.0
    denom = math.e ** k - 1

    def Yc(f):
        return y0 - 270 * (math.e ** (k * f) - 1) / denom

    def Yl(f):
        return y0 - 95 * f

    comp = [(X(i / 20.0), Yc(i / 20.0)) for i in range(0, 21)]
    for i in range(len(comp) - 1):
        p.append(line(comp[i][0], comp[i][1], comp[i + 1][0], comp[i + 1][1], color=POS, sw=2.4))
    p.append(line(X(0.0), Yl(0.0), X(1.0), Yl(1.0), color=NEG, sw=2.0, dash="5,4"))

    p.append(mtext(380, 138, ["реальність: залежності множаться", "переробка ∝ e^(g·t_d)"], size=10.5, color=POS))
    p.append(text(660, 242, "оптимістично — лінійно", size=10.5, color=NEG))

    # маркер кістяка (день 1)
    p.append(circle(X(0.02), Yc(0.02), 5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(mtext(178, 298, ["кістяк знаходить тут —", "переробка майже даром"], size=10, color=FIELD))
    p.append(line(150, 316, X(0.02) + 4, Yc(0.02) - 5, color=FIELD, sw=1.1))
    # маркер вузлів-поодинці (реліз)
    p.append(line(X(1.0), y0, X(1.0), Yc(1.0), color=MUTED, sw=1.2, dash="3,3"))
    p.append(circle(X(1.0), Yc(1.0), 5, fill=POS, stroke=POS, sw=1.5))
    # брекет економії справа
    bx = X(1.0) + 16
    p.append(line(bx, Yc(1.0), bx, Yc(0.02), color=INK, sw=1.4))
    p.append(line(bx - 5, Yc(1.0), bx, Yc(1.0), color=INK, sw=1.4))
    p.append(line(bx - 5, Yc(0.02), bx, Yc(0.02), color=INK, sw=1.4))
    p.append(mtext(bx + 8, 200, ["той самий", "дефект —", "× e^(g·T)", "дорожче"], size=9.5, color=INK, anchor="start"))

    p.append(text(W / 2, 410, "Кістяк призначає виявлення на день перший, коли переробка ще майже безкоштовна",
                  size=10.5, italic=True))
    render(os.path.join(OUT, "discovery-cost.svg"), W, H, *p)


# ── 6. Де сидить головний ризик → який інструмент ──────────────────────────────
# Дерево рішення: спершу спитай, де в системі найбільший ризик, і лише тоді бери
# інструмент. Ризик на стиках («чи складеться ціле») → ходячий кістяк. Ризик
# усередині вузла (важкий алгоритм, точність, швидкодія) → спайк (тонко, але
# вглиб ОДНОГО вузла, викидний). Ризик потрібності (цінність, ринок) → MVP.
# Головна думка: кістяк прицільно б'є ризик інтеграції, не будь-який ризик.
def fig_risk_location():
    W, H = 900, 420
    p = []
    p.append(text(W / 2, 26, "Кістяк — не завжди правильний хід: спершу спитай, де сидить головний ризик",
                  size=14, bold=True))
    p.append(fitbox(360, 52, 180, 46, "Де сидить\nголовний ризик?", size=12.5, fill=FILL, stroke=INK, sw=1.8, bold=True))
    root = (450, 98)
    conds = [
        (60, "На стиках між частинами —\nчи складеться ціле?"),
        (335, "Усередині одного вузла —\nважкий алгоритм,\nточність, швидкодія?"),
        (625, "Чи потрібне це взагалі —\nцінність для людей?"),
    ]
    outs = [
        (60, FIELD, "Ходячий кістяк —\nтонка нитка крізь усі\nвузли, лишається жити"),
        (335, NEG, "Спайк — тонко, але\nвглиб ОДНОГО вузла;\nкод викидний"),
        (625, INK, "MVP — найменше,\nчим уже\nкористуються"),
    ]
    cy, cw, ch = 150, 215, 74
    oy, oh = 268, 74
    for (cx, ctext), (ox, ocol, otext) in zip(conds, outs):
        ccx = cx + cw / 2
        p.append(arrow(root[0], root[1], ccx, cy - 5, color=MUTED, sw=1.5))
        p.append(fitbox(cx, cy, cw, ch, ctext, size=11, fill="#fbfbfb", stroke=MUTED, sw=1.3))
        p.append(arrow(ccx, cy + ch, ccx, oy - 5, color=MUTED, sw=1.5))
        p.append(fitbox(ox, oy, cw, oh, otext, size=11, fill=BG, stroke=ocol, sw=2.0))
    p.append(text(W / 2, 392,
                  "Кістяк прицільно б'є ризик інтеграції — «чи складеться ціле». Інші ризики просять інших інструментів.",
                  size=10.5, italic=True))
    render(os.path.join(OUT, "risk-location.svg"), W, H, *p)


# ── 7. Чутливість P(наскрізна збірка) до N та q (для вставки math-) ─────────────
# Сімейство кривих P(N) = (1−q)^(a·(N−1)) при a=4 для q ∈ {0.05,0.10,0.15,0.20}.
# Показує головне за брифом вставки: шанс падає і з довжиною ланцюга N, і з
# ризиком однієї домовленості q — і падає КРУТО (перемноження ймовірностей).
def fig_pn_sensitivity():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 26, "Шанс наскрізної збірки з першого разу круто падає і з числом вузлів, і з ризиком стику",
                  size=13.5, bold=True))
    xL, xR = 120, 740
    yT, yB = 100, 380
    Ns = list(range(2, 9))

    def X(n):
        return xL + (n - 2) / 6.0 * (xR - xL)

    def Y(v):
        return yB - v * (yB - yT)

    # осі (без стрілок — щоб не було накладань підписів на вістря)
    p.append(line(xL, yT, xL, yB, color=INK, sw=1.8))
    p.append(line(xL, yB, xR, yB, color=INK, sw=1.8))
    for v, lab in [(0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")]:
        yy = Y(v)
        p.append(line(xL - 4, yy, xL, yy, color=INK, sw=1.3))
        p.append(text(xL - 9, yy + 4, lab, size=9.5, color=MUTED, anchor="end"))
    p.append(line(xL, Y(0.5), xR, Y(0.5), color=MUTED, sw=1, dash="4,4"))
    for n in Ns:
        xx = X(n)
        p.append(line(xx, yB, xx, yB + 4, color=INK, sw=1.3))
        p.append(text(xx, yB + 18, str(n), size=10, color=MUTED))
    p.append(text((xL + xR) / 2, yB + 38, "число вузлів N   (стиків N−1)", size=11, color=INK))
    p.append(text(xL - 2, yT - 12, "P — шанс збірки", size=10, color=INK, anchor="start"))

    a = 4
    series = [(0.05, FIELD), (0.10, NEG), (0.15, INK), (0.20, POS)]
    for q, col in series:
        pts = [(X(n), Y((1 - q) ** (a * (n - 1)))) for n in Ns]
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=col, sw=2.2))
        for xx, yy in pts:
            p.append(circle(xx, yy, 2.8, fill=BG, stroke=col, sw=1.6))

    # легенда у порожньому верхньо-правому куті (жодна крива туди не заходить)
    lx, ly = 572, 108
    p.append(rect(lx, ly, 168, 108, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(lx + 84, ly + 18, "a = 4 домовленості/стик", size=9.5, color=INK, bold=True))
    ry = ly + 40
    for q, col in series:
        p.append(line(lx + 14, ry - 4, lx + 42, ry - 4, color=col, sw=2.8))
        p.append(text(lx + 50, ry, "q = %.2f" % q, size=10, color=INK, anchor="start"))
        ry += 19

    mx, my = X(5), Y(0.9 ** 16)
    p.append(circle(mx, my, 5, fill=NEG, stroke=NEG, sw=1.5))
    p.append(mtext(300, 150, ["5 вузлів, q = 0.10:", "≈ 18% з першого разу"], size=10, color=INK))
    p.append(line(335, 178, mx - 3, my - 6, color=MUTED, sw=1.1))

    p.append(text(W / 2, H - 16,
                  "Навіть за скромного ризику стику довгий ланцюг рідко стикається сам собою — бо ймовірності перемножуються",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "pn-sensitivity.svg"), W, H, *p)


# ── 8. Незалежність VS спільні домовленості (послаблення припущення) ────────────
# Ліворуч: 16 незалежних домовленостей (4 стики × 4 типи) → P=(1−q)^16≈0.19.
# Праворуч: ті самі 4 типи вирішено РАЗ на всю систему → 4 незалежні рішення →
# P=(1−q)^4≈0.66. Головна думка вставки: незалежність — песимістичний край;
# менше НЕЗАЛЕЖНИХ рішень (спільна схема/кодек) математично піднімає шанс.
def fig_correlation():
    W, H = 900, 480
    p = []
    p.append(text(W / 2, 26, "Незалежність — песимістичний край: спільні домовленості піднімають шанс збірки",
                  size=13.5, bold=True))
    p.append(line(W / 2, 50, W / 2, 326, color=MUTED, sw=1, dash="4,4"))

    types = ["формат", "порядок б.", "одиниці", "версія"]

    # ── ЛІВОРУЧ: 16 незалежних кидків ──
    p.append(text(232, 58, "Домовленості незалежні", size=12, bold=True, color=POS))
    p.append(text(232, 74, "кожна — окремий кидок", size=9.5, color=MUTED))
    gx0, cell, cgap, gy0 = 150, 30, 10, 112
    p.append(text((gx0 + gx0 + 3 * (cell + cgap) + cell) / 2, 100, "4 стики", size=9.5, color=INK))
    for i, t in enumerate(types):
        yy = gy0 + i * (cell + cgap)
        p.append(text(gx0 - 12, yy + cell / 2 + 4, t, size=9.5, color=INK, anchor="end"))
        for j in range(4):
            xx = gx0 + j * (cell + cgap)
            p.append(rect(xx, yy, cell, cell, fill="#fdecea", stroke=POS, sw=1.3, rx=4))
            p.append(text(xx + cell / 2, yy + cell / 2 + 4, "?", size=12, color=POS, bold=True))
    p.append(mtext(232, 300, ["16 незалежних домовленостей", "P = (1−q)¹⁶ = 0.9¹⁶ ≈ 0.19"],
                   size=11, color=INK))

    # ── ПРАВОРУЧ: 4 спільні рішення ──
    p.append(text(668, 58, "Спільні домовленості", size=12, bold=True, color=FIELD))
    p.append(text(668, 74, "одна схема, один кодек на всю систему", size=9.5, color=MUTED))
    bx0, bw, bh, bgap, by0 = 500, 320, 30, 10, 112
    for i, t in enumerate(types):
        yy = by0 + i * (bh + bgap)
        p.append(rect(bx0, yy, bw, bh, fill="#e7f7ee", stroke=FIELD, sw=1.5, rx=6))
        p.append(text(bx0 + 12, yy + bh / 2 + 4, t + " — вирішено раз на всю систему",
                      size=9.5, color=INK, anchor="start"))
    p.append(mtext(668, 300, ["4 спільні рішення (по типах)", "P = (1−q)⁴ = 0.9⁴ ≈ 0.66"],
                   size=11, color=INK))

    # ── нижня смуга: вилка й кореляція ──
    p.append(line(60, 340, 840, 340, color=MUTED, sw=1))
    p.append(text(W / 2, 366,
                  "Шанс лежить у вилці:   (1−q)^m  (усе незалежно, m = 16)   ≤   P   ≤   (1−q)  (усе спільне, одне рішення)",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 400,
                  "Два стики з кореляцією ρ:   P(обидва чисті) = p² + ρ·p(1−p) ≥ p²   —   додатна кореляція завжди піднімає шанс над добутком",
                  size=10, color=INK))
    p.append(text(W / 2, H - 14,
                  "Менше НЕЗАЛЕЖНИХ рішень на стиках — вищий шанс зібратися; тому одна схема на всю систему математично безпечніша",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "correlation.svg"), W, H, *p)


# ── 9. Куди класти глибину: ΔE/Δk по стиках (формалізація осі Аджича) ───────────
# Смуги ефективності зняття ризику (P·C)/k для стиків-кандидатів, відсортовані
# спадно. Найвища смуга — туди глибину; найнижчі — тонка нитка/милиця. Так «вісь
# Аджича» стає числом: бюджет на зняття ризику клади, де ΔE/Δk найбільше.
def fig_allocation():
    W, H = 900, 440
    p = []
    p.append(text(W / 2, 26, "Клади глибину туди, де зняття ризику на одиницю зусилля найбільше",
                  size=13.5, bold=True))
    seams = [
        ("новий радіопротокол", 0.6, 120, 5),
        ("межа двох команд", 0.5, 80, 4),
        ("чуже платіжне API", 0.4, 90, 4),
        ("своя база (вторована)", 0.1, 50, 3),
        ("UI-рендер (знайомий)", 0.05, 20, 2),
    ]
    rows = []
    for name, P, C, k in seams:
        E = P * C
        rows.append((name, P, C, k, E, E / k))
    rows.sort(key=lambda r: -r[5])
    effmax = rows[0][5]

    x0, xmax, y0, bh, bgap = 270, 680, 92, 40, 18
    p.append(text(x0 - 12, 74, "стик-кандидат", size=9.5, color=MUTED, anchor="end"))
    p.append(text(x0 + 2, 74, "ΔE/Δk = (P·C)/k — знятий ризик на людино-день зусилля",
                  size=9.5, color=MUTED, anchor="start"))
    for idx, (name, P, C, k, E, eff) in enumerate(rows):
        yy = y0 + idx * (bh + bgap)
        p.append(text(x0 - 12, yy + bh / 2 - 3, name, size=10, color=INK, anchor="end"))
        p.append(text(x0 - 12, yy + bh / 2 + 13, "P=%.2f · C=%d · k=%d" % (P, C, k),
                      size=9, color=MUTED, anchor="end"))
        bl = (xmax - x0) * eff / effmax
        deep = (idx == 0)
        col = FIELD if eff >= 5 else MUTED
        fill = "#e7f7ee" if eff >= 5 else FILL
        p.append(rect(x0, yy, bl, bh, fill=fill, stroke=col, sw=1.6, rx=5))
        p.append(text(x0 + bl + 8, yy + bh / 2 + 4, "%.1f" % eff, size=11, color=col, bold=True, anchor="start"))
        if deep:
            p.append(text(x0 + bl + 44, yy + bh / 2 + 4, "← клади глибину сюди", size=10, color=FIELD, bold=True, anchor="start"))
        elif eff < 2:
            p.append(text(x0 + bl + 44, yy + bh / 2 + 4, "← тонка нитка / милиця", size=9.5, color=MUTED, anchor="start"))
    p.append(text(W / 2, H - 14,
                  "Знайомий стик має низьке P — гасити його майже нічого не дає; страшний стик несе найбільше знятого ризику на зусилля",
                  size=10.5, italic=True, color=INK))
    render(os.path.join(OUT, "allocation.svg"), W, H, *p)


# ── Зелений димовий тест ≠ жива нитка (для вставки proj-keep-it-walking) ────────
# Зверху — чесний тест: торкається лише двох країв (вхід/вихід), значення мусить
# пройти крізь СПРАВЖНІЙ брокер і воркера. Знизу — короткозамкнений тест: читає
# сховище повз брокер; вузли «зелені», а стик мертвий, і збірка все одно зелена.
def _qpath(x1, y1, cx, cy, x2, y2, color, sw, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (x1, y1, cx, cy, x2, y2, color, sw, d))


def fig_keep_walking():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 26, "Зелений димовий тест ще не означає живу нитку", size=15, bold=True))

    margin, bw, bh, n = 55, 100, 46, 6
    gap = (W - 2 * margin - n * bw) / (n - 1)      # = 38
    cx = [margin + bw / 2 + i * (bw + gap) for i in range(n)]
    labels = ["POST", "API", "брокер", "воркер", "сховище", "GET"]
    EDGE = "#eef3fd"   # ледь-синій — краї, яких торкається тест

    # роздільник між панелями
    p.append(line(40, 225, 860, 225, color=MUTED, sw=1, dash="4,4"))

    # ── ВЕРХНЯ панель: нитка йде наскрізь ──
    ty = 104
    for i, lbl in enumerate(labels):
        if i == 2:                                  # брокер — справжній, зелений
            p.append(rect(cx[i] - bw / 2, ty, bw, bh, fill="#e7f7ee", stroke=FIELD, sw=1.8))
        elif i in (0, 5):                           # краї — торкається тест
            p.append(rect(cx[i] - bw / 2, ty, bw, bh, fill=EDGE, stroke=NEG, sw=1.6))
        else:
            p.append(rect(cx[i] - bw / 2, ty, bw, bh, fill=FILL, stroke=LINE, sw=1.4))
        p.append(text(cx[i], ty + 28, lbl, size=11.5, color=INK))
    for i in range(n - 1):                          # суцільна нитка крізь УСІ вузли
        p.append(arrow(cx[i] + bw / 2 + 2, ty + 23, cx[i + 1] - bw / 2 - 2, ty + 23, color=FIELD, sw=2.2))
    p.append(text(cx[0], ty + 66, "вхід", size=9, color=NEG))
    p.append(text(cx[5], ty + 66, "вихід", size=9, color=NEG))
    p.append(text(cx[2], ty + 66, "справжній", size=9, color=FIELD, bold=True))
    # дуга-ствердження над рядком: тест звіряє два краї
    p.append(_qpath(cx[0], ty, W / 2, 18, cx[5], ty, FIELD, 2))
    p.append(text(W / 2, 52, "тест звіряє: вихід = вхід", size=11.5, color=FIELD, bold=True))

    # ── НИЖНЯ панель: тест короткозамкнений ──
    by = 300
    for i, lbl in enumerate(labels):
        if i in (2, 3):                             # брокер і воркер — не перевірено, зблякло
            p.append(rect(cx[i] - bw / 2, by, bw, bh, fill="#f6f6f6", stroke=MUTED, sw=1.2))
            p.append(text(cx[i], by + 28, lbl, size=11.5, color=MUTED))
        elif i in (0, 5):
            p.append(rect(cx[i] - bw / 2, by, bw, bh, fill=EDGE, stroke=NEG, sw=1.6))
            p.append(text(cx[i], by + 28, lbl, size=11.5, color=INK))
        else:
            p.append(rect(cx[i] - bw / 2, by, bw, bh, fill=FILL, stroke=LINE, sw=1.4))
            p.append(text(cx[i], by + 28, lbl, size=11.5, color=INK))
    for i in range(n - 1):                          # намічений шлях — сірий пунктир, мертвий
        p.append(line(cx[i] + bw / 2 + 2, by + 23, cx[i + 1] - bw / 2 - 2, by + 23,
                      color=MUTED, sw=1.3, dash="5,4"))
    p.append(text(cx[2], by + 66, "не перевірено", size=9, color=POS, bold=True))
    # червона дуга обходу: значення телепортується API → сховище, ПОВЗ брокер і воркера
    p.append(_qpath(cx[1], by + bh, W / 2, 438, cx[4], by + bh, POS, 2, dash="6,4"))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
             % (cx[4], by + bh - 3, cx[4] - 6, by + bh + 8, cx[4] + 6, by + bh + 8, POS))
    p.append(text(W / 2, 408, "тест читає сховище ПОВЗ брокер і воркера", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "keep-walking.svg"), W, H, *p)


if __name__ == "__main__":
    fig_thread()
    fig_risk_timing()
    fig_lineage()
    fig_seam_decay()
    fig_discovery_cost()
    fig_risk_location()
    fig_pn_sensitivity()
    fig_correlation()
    fig_allocation()
    fig_keep_walking()
    print("figs done")
