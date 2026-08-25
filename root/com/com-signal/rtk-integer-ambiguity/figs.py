# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: несуча — точна лінійка з невідомим цілим числом поділок ──────────
def fig_ruler():
    W, H = 720, 340
    frags = []

    # Горизонтальний промінь від супутника (ліворуч) до приймача (праворуч).
    y0 = 120
    sx, rx = 78, 642
    frags.append(circle(sx, y0, 16, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(sx, y0 - 26, "супутник", size=13, color=MUTED))
    frags.append(circle(rx, y0, 14, fill="#f4f6f8", stroke=INK, sw=2))
    frags.append(text(rx, y0 - 26, "приймач", size=13, color=MUTED))
    frags.append(line(sx + 16, y0, rx - 14, y0, color=MUTED, sw=1.2, dash="2,4"))

    # Поділки (цикли несучої) — рівні вертикальні рисочки вздовж променя.
    x_start, x_end = sx + 40, rx - 60
    ncyc = 20
    xs = [x_start + (x_end - x_start) * i / ncyc for i in range(ncyc + 1)]
    for x in xs:
        frags.append(line(x, y0 - 9, x, y0 + 9, color="#9aa4b2", sw=1.3))

    # Одна поділка виділена червоним (довжина λ) — 6-й проміжок.
    a, b = xs[6], xs[7]
    frags.append(line(a, y0 - 22, a, y0 + 22, color=POS, sw=1.2, dash="2,3"))
    frags.append(line(b, y0 - 22, b, y0 + 22, color=POS, sw=1.2, dash="2,3"))
    frags.append(line(a, y0 - 22, b, y0 - 22, color=POS, sw=2))
    bx, _, _ = textbox((a + b) / 2, y0 - 46, "λ ≈ 19 см", size=12, color=POS,
                       stroke=POS, fill="#fdecea")
    frags.append(bx)

    # Останній неповний шматок біля приймача — дробова частина φ (зелена дужка).
    lastx = xs[-1]
    frags.append(line(lastx, y0 + 9, lastx, y0 + 40, color=FIELD, sw=1.4))
    frags.append(line(rx - 14, y0 + 9, rx - 14, y0 + 40, color=FIELD, sw=1.4))
    frags.append(line(lastx, y0 + 40, rx - 14, y0 + 40, color=FIELD, sw=2))

    # Три стеки-підписи ПІД лінійкою — не перекриваються.
    b1, _, _ = textbox(360, y0 + 90,
                       "ціле число поділок N уздовж усього променя  —  НЕВІДОМЕ",
                       size=14, bold=True, color=INK, stroke=INK, fill="#fff8e1", min_w=440)
    frags.append(b1)
    b2, _, _ = textbox(360, y0 + 150,
                       "дробову частину φ (останній неповний шматок) міряємо ТОЧНО, до міліметрів",
                       size=12, color=FIELD, stroke=FIELD, fill="#eafaf1", min_w=440)
    frags.append(b2)

    render(os.path.join(OUT, 'carrier-ruler.svg'), W, H,
           *frags,
           title="Несуча як лінійка: дробова поділка відома точно, число цілих N — ні")


# ── Фігура 2: подвійна різниця гасить спільні похибки ─────────────────────────
def fig_double_difference():
    W, H = 720, 360
    frags = []

    # Два супутники вгорі, база й ровер унизу.
    satA = (180, 60); satB = (540, 60)
    base = (200, 300); rover = (520, 300)

    for (x, y), name in [(satA, "супутник A"), (satB, "супутник B")]:
        frags.append(circle(x, y, 15, fill="#eef2ff", stroke=NEG, sw=2))
        frags.append(text(x, y - 24, name, size=12, color=MUTED))

    frags.append(rect(base[0]-42, base[1]-14, 84, 30, fill="#f4f6f8", stroke=INK, sw=1.6))
    frags.append(text(base[0], base[1]+6, "база", size=13))
    frags.append(text(base[0], base[1]+34, "координати відомі", size=11, color=MUTED))
    frags.append(rect(rover[0]-42, rover[1]-14, 84, 30, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(text(rover[0], rover[1]+6, "ровер", size=13, color=FIELD, bold=True))
    frags.append(text(rover[0], rover[1]+34, "координати шукаємо", size=11, color=MUTED))

    # Чотири промені.
    for s, r, col in [(satA, base, MUTED), (satA, rover, INK),
                      (satB, base, MUTED), (satB, rover, INK)]:
        frags.append(line(s[0], s[1], r[0], r[1], color=col, sw=1.3, dash="3,4"))

    # Підпис у центрі: що гаситься.
    b, _, _ = textbox(360, 175,
                      "різниця база↔ровер гасить похибки супутника (годинник, орбіта)\n"
                      "різниця A↔B гасить похибки приймачів  →  лишається чиста геометрія + ціле N",
                      size=12, color=INK, stroke=LINE, fill="#fff8e1")
    frags.append(b)

    render(os.path.join(OUT, 'double-difference.svg'), W, H,
           *frags,
           title="Подвійна різниця: два прийоми, дві різниці — спільні похибки зникають")


# ── Фігура 3: чому не можна округлити — витягнутий еліпс проти цілої ґратки ────
def fig_search():
    W, H = 720, 340
    frags = []

    # ЛІВОРУЧ: корельований (витягнутий, похилий) еліпс над цілою ґраткою.
    cxL, cyL = 200, 185
    # Ґратка цілих точок.
    for gx in range(-3, 4):
        for gy in range(-3, 4):
            px = cxL + gx * 26
            py = cyL - gy * 26
            frags.append(circle(px, py, 2.2, fill=MUTED, stroke=MUTED, sw=0.8))
    # Похилий вузький еліпс (імітуємо як послідовність кіл уздовж осі).
    import math
    ex, ey = cxL + 0.4*26, cyL - 0.6*26   # float-розв'язок (не в вузлі)
    ang = math.radians(35)
    for k in range(-6, 7):
        t = k / 6.0
        px = ex + math.cos(ang) * t * 60
        py = ey - math.sin(ang) * t * 60
        rr = 10 * (1 - 0.55*abs(t))
        frags.append(circle(px, py, max(2.0, rr), fill="none", stroke=NEG, sw=1.0))
    frags.append(circle(ex, ey, 3.4, fill=POS, stroke=POS, sw=1.5))
    b, _, _ = textbox(cxL, cyL + 130, "float-оцінка (не ціла)\nеліпс похилий і вузький",
                      size=12, color=NEG, stroke=NEG, fill="#eef2ff")
    frags.append(b)
    frags.append(text(cxL, 60, "округлити наосліп — легко схибити", size=13, bold=True, color=POS))

    # ПРАВОРУЧ: після декореляції — еліпс майже круглий, вузли по осях.
    cxR, cyR = 540, 185
    for gx in range(-3, 4):
        for gy in range(-3, 4):
            px = cxR + gx * 26
            py = cyR - gy * 26
            frags.append(circle(px, py, 2.2, fill=MUTED, stroke=MUTED, sw=0.8))
    ex2, ey2 = cxR + 0.4*26, cyR - 0.3*26
    for k in range(-5, 6):
        rr = 8 + k*0  # кола
        frags.append(circle(ex2, ey2, 6 + abs(k)*4.0, fill="none", stroke=FIELD, sw=1.0))
    frags.append(circle(ex2, ey2, 3.4, fill=POS, stroke=POS, sw=1.5))
    # найближчий вузол
    frags.append(circle(cxR, cyR, 5, fill="none", stroke=INK, sw=2))
    b2, _, _ = textbox(cxR, cyR + 130, "після декореляції\nеліпс круглий — вузол очевидний",
                       size=12, color=FIELD, stroke=FIELD, fill="#eafaf1")
    frags.append(b2)
    frags.append(text(cxR, 60, "декорелюй — тоді шукай", size=13, bold=True, color=FIELD))

    # Стрілка-перетворення між панелями.
    frags.append(arrow(cxL + 150, 185, cxR - 150, 185, color=INK, sw=2))
    frags.append(text(360, 172, "LAMBDA", size=12, bold=True, color=INK))

    render(os.path.join(OUT, 'integer-search.svg'), W, H,
           *frags,
           title="Чому не округлюють: витягнутий еліпс vs декорельована ґратка")


# ── Фігура 4 (вставка math): драбина скорочень — які члени гинуть на кожній різниці ──
def fig_cancel_ladder():
    W, H = 760, 470
    frags = []

    # Три колонки: сире рівняння · одинарна різниця · подвійна різниця.
    cols = [
        (150, "сире рівняння", MUTED),
        (400, "одинарна різниця\n(база − ровер)", NEG),
        (630, "подвійна різниця\n(супут. A − B)", FIELD),
    ]
    for cx, name, col in cols:
        frags.append(mtext(cx, 62, name, size=13, color=col, bold=True))

    # Рядки-члени рівняння. survive[i] = (жив-у-сирому, жив-після-одинарної, жив-після-подвійної)
    rows = [
        ("геометрія  ρ",        (1, 1, 1)),   # лишається завжди
        ("годинник супутника",  (1, 0, 0)),   # гине на одинарній
        ("орбіта супутника",    (1, 0, 0)),
        ("фазовий зсув супут.", (1, 0, 0)),
        ("годинник приймача",   (1, 1, 0)),   # гине на подвійній
        ("фазовий зсув прийм.", (1, 1, 0)),
        ("іоносфера/тропо",     (1, 1, 1)),   # лишається, але дрібніє на короткій базі
        ("ціле N · λ",          (1, 1, 1)),   # лишається — ЦІЛЕ
        ("шум",                 (1, 1, 1)),
    ]
    y0, dy = 96, 40
    for i, (label, surv) in enumerate(rows):
        y = y0 + i * dy
        # Назва члена ліворуч.
        frags.append(text(18, y + 4, label, size=12, color=INK, anchor="start"))
        for (cx, _, _), alive in zip(cols, surv):
            if alive:
                if label.startswith("ціле N"):
                    frags.append(circle(cx, y, 8, fill="#eafaf1", stroke=FIELD, sw=2))
                    frags.append(text(cx, y + 4, "✓", size=12, color=FIELD, bold=True))
                elif label.startswith("іоносфера"):
                    frags.append(circle(cx, y, 8, fill="#fff8e1", stroke="#b8860b", sw=2))
                    frags.append(text(cx, y + 4, "≈", size=12, color="#b8860b", bold=True))
                else:
                    frags.append(circle(cx, y, 7, fill="#f4f6f8", stroke=MUTED, sw=1.4))
            else:
                # Мертвий член — перекреслене коло.
                frags.append(circle(cx, y, 7, fill="#fbeaea", stroke=POS, sw=1.4))
                frags.append(line(cx - 6, y - 6, cx + 6, y + 6, color=POS, sw=1.8))

    # Легенда під таблицею.
    ly = y0 + len(rows) * dy + 6
    frags.append(circle(70, ly, 7, fill="#fbeaea", stroke=POS, sw=1.4))
    frags.append(line(64, ly - 6, 76, ly + 6, color=POS, sw=1.8))
    frags.append(text(84, ly + 4, "скоротився", size=11, color=MUTED, anchor="start"))
    frags.append(circle(230, ly, 8, fill="#fff8e1", stroke="#b8860b", sw=2))
    frags.append(text(230, ly + 4, "≈", size=11, color="#b8860b", bold=True))
    frags.append(text(244, ly + 4, "майже гаситься (тим краще, чим коротша база)",
                      size=11, color=MUTED, anchor="start"))
    frags.append(circle(600, ly, 8, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(600, ly + 4, "✓", size=11, color=FIELD, bold=True))
    frags.append(text(614, ly + 4, "лишилось ЦІЛИМ", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'cancel-ladder.svg'), W, H,
           *frags,
           title="Що гине на кожній різниці: від сирого рівняння до подвійної")


# ── Фігура 5 (вставка math): чому коротша база → краще гасить атмосферу ────────
def fig_atmosphere_baseline():
    W, H = 760, 360
    frags = []
    import math

    sat = (380, 46)
    frags.append(circle(sat[0], sat[1], 15, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(sat[0], sat[1] - 24, "супутник", size=12, color=MUTED))

    # Атмосферний шар (смуга).
    ytop, ybot = 120, 168
    frags.append(rect(40, ytop, W - 80, ybot - ytop, fill="#fff8e1", stroke="#e0c060", sw=1.2))
    frags.append(text(W - 52, (ytop + ybot) / 2 + 4, "атмосфера", size=11,
                      color="#8a6d1a", anchor="end"))

    # ЛІВОРУЧ: коротка база — база й ровер близько, промені майже збігаються.
    baseL = (250, 300); roverL = (300, 300)
    frags.append(rect(baseL[0]-30, baseL[1]-12, 60, 26, fill="#f4f6f8", stroke=INK, sw=1.4))
    frags.append(text(baseL[0], baseL[1]+5, "база", size=11))
    frags.append(rect(roverL[0]-32, roverL[1]-12, 64, 26, fill="#eafaf1", stroke=FIELD, sw=1.6))
    frags.append(text(roverL[0], roverL[1]+5, "ровер", size=11, color=FIELD, bold=True))
    for pt in (baseL, roverL):
        frags.append(line(sat[0], sat[1], pt[0], pt[1], color=INK, sw=1.2, dash="3,4"))
    frags.append(mtext(275, 340, "коротка база: промені крізь той самий\nстовп повітря → різниця майже нуль",
                       size=11, color=FIELD))

    # ПРАВОРУЧ: довга база — ровер далеко, промені йдуть крізь різні ділянки.
    baseR = (540, 300); roverR = (690, 300)
    frags.append(rect(baseR[0]-30, baseR[1]-12, 60, 26, fill="#f4f6f8", stroke=INK, sw=1.4))
    frags.append(text(baseR[0], baseR[1]+5, "база", size=11))
    frags.append(rect(roverR[0]-32, roverR[1]-12, 64, 26, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(roverR[0], roverR[1]+5, "ровер", size=11, color=POS, bold=True))
    for pt in (baseR, roverR):
        frags.append(line(sat[0], sat[1], pt[0], pt[1], color=INK, sw=1.2, dash="3,4"))
    frags.append(mtext(615, 340, "довга база: промені крізь різні шматки\nнеба → лишок не гаситься",
                       size=11, color=POS))

    # Виділити ділянки перетину променів з атмосферою кружечками.
    def hit_x(pt, y):
        t = (y - sat[1]) / (pt[1] - sat[1])
        return sat[0] + (pt[0] - sat[0]) * t
    ymid = (ytop + ybot) / 2
    for pt, col in [(baseL, INK), (roverL, FIELD)]:
        frags.append(circle(hit_x(pt, ymid), ymid, 4, fill=col, stroke=col, sw=1))
    for pt, col in [(baseR, INK), (roverR, POS)]:
        frags.append(circle(hit_x(pt, ymid), ymid, 4, fill=col, stroke=col, sw=1))

    render(os.path.join(OUT, 'atmosphere-baseline.svg'), W, H,
           *frags,
           title="Короткою базою атмосфера гаситься майже дощенту")


if __name__ == '__main__':
    fig_ruler()
    fig_double_difference()
    fig_search()
    fig_cancel_ladder()
    fig_atmosphere_baseline()
    print("figures written to", OUT)
