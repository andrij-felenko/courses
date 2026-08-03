# -*- coding: utf-8 -*-
"""Фігури до теми «Wear leveling у Flash-пам'яті» (коднотеоретичний кут).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"   # контрольні біти / ECC
STEEL = "#3b6fb0"   # звичайні блоки


# ── 1. Обрив: UBER проти RBER ─────────────────────────────────────────────────
def fig_cliff():
    W, H = 820, 480
    f = [text(W / 2, 30, "Обрив: код перетворює RBER на UBER", size=17, bold=True)]
    f.append(text(W / 2, 52, "невиправний рівень помилок росте як p у степені (t+1) — тому за порогом коду він вистрілює",
                  size=11, color=MUTED, italic=True))

    # плоска рамка графіка
    px0, py0, px1, py1 = 96, 92, 762, 372            # межі поля
    f.append(line(px0, py1, px1, py1, color=INK, sw=1.8))   # вісь X
    f.append(line(px0, py0, px0, py1, color=INK, sw=1.8))   # вісь Y
    f.append(text(px1, py1 + 40, "RBER (сирий рівень помилок) →", size=11.5, color=INK, anchor="end", bold=True))
    f.append(text(px0 - 66, py0 - 12, "UBER", size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(px0 - 66, py0 + 4, "(невиправ.)", size=10, color=MUTED, anchor="start"))

    # мітки осі X
    for xx, lab in [(150, "10⁻⁵"), (300, "10⁻⁴"), (470, "10⁻³"), (640, "10⁻²")]:
        f.append(line(xx, py1, xx, py1 + 5, color=INK, sw=1.2))
        f.append(text(xx, py1 + 20, lab, size=10.5, color=MUTED))
    # мітки осі Y
    for yy, lab in [(120, "10⁻³"), (232, "10⁻⁹"), (300, "10⁻¹⁵")]:
        f.append(line(px0 - 5, yy, px0, yy, color=INK, sw=1.2))
        f.append(text(px0 - 12, yy + 4, lab, size=10.5, color=MUTED, anchor="end"))

    # лінія специфікації UBER = 1e-15
    yspec = 300
    f.append(line(px0, yspec, px1, yspec, color=FIELD, sw=1.6, dash="7 5"))
    f.append(text(px1 - 6, yspec - 8, "межа специфікації  UBER ≤ 10⁻¹⁵", size=10.5, color=FIELD,
                  anchor="end", bold=True))

    # крива обриву (схематична): плоско-низько, тоді стрімко вгору
    pts = [(150, 366), (240, 363), (330, 358), (410, 349), (470, 336),
           (515, 316), (548, 286), (578, 240), (606, 186), (636, 132), (700, 104), (752, 98)]
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, INK))

    # поріг: де крива перетинає лінію специфікації (≈ x=562)
    xthr = 562
    f.append(line(xthr, yspec, xthr, py1, color=POS, sw=1.4, dash="4 4"))
    f.append(text(xthr, py1 + 36, "поріг коду (t)", size=10.5, color=POS, bold=True))

    # три блоки-маркери на кривій, підписи у порожній верхній зоні з тонкими виносками
    def dot(x, y, col):
        return circle(x, y, 5.5, fill=col, stroke=BG, sw=1.5)

    # свіжий (глибоко в безпеці)
    f.append(dot(300, 358, STEEL))
    f.append(line(300, 358, 300, 330, color=MUTED, sw=1))
    f.append(text(300, 320, "свіжий блок", size=11, color=STEEL, bold=True))
    # рівномірно зношений (ще ліворуч від порога)
    f.append(dot(470, 336, STEEL))
    f.append(line(470, 336, 470, 250, color=MUTED, sw=1))
    f.append(fitbox(388, 214, 164, 34, "рівномірно зношений\n(усе ще під межею)", size=10.5,
                    color=INK, fill="#eef3fb", stroke=STEEL, sw=1.2))
    # передчасно зношений (за порогом → втрата даних)
    f.append(dot(620, 158, POS))
    f.append(line(620, 158, 660, 158, color=MUTED, sw=1))
    f.append(fitbox(664, 138, 150, 40, "передчасно зношений\n→ втрата даних", size=10.5,
                    color=POS, fill="#fdeceb", stroke=POS, sw=1.4, bold=True))

    f.append(text(W / 2, 464, "wear leveling тримає RBER кожного блока ліворуч від обриву — там, де код ще бере своє",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "uber-cliff.svg"), W, H, *f)


# ── 2. Розподіл RBER по блоках: перекіс проти вирівнювання ─────────────────────
def fig_distribution():
    W, H = 880, 420
    f = [text(W / 2, 30, "Надійність пристрою = найгірший блок", size=17, bold=True)]
    f.append(text(W / 2, 52, "вирівнювання не опускає середній RBER, а стискає гістограму, ховаючи її хвіст під межу коду",
                  size=11, color=MUTED, italic=True))

    def panel(x0, title_, heights, spike_idx, colnorm, colspike, note, note_col):
        g = []
        base = 336            # низ стовпчиків
        top = 108             # верх зони
        line_y = 150          # межа коду
        pw = 380              # ширина панелі
        g.append(text(x0 + pw / 2, 84, title_, size=13, bold=True))
        # межа коду
        g.append(line(x0 + 14, line_y, x0 + pw - 14, line_y, color=POS, sw=1.5, dash="6 4"))
        g.append(text(x0 + pw - 16, line_y - 8, "межа коду (t)", size=10, color=POS, anchor="end", bold=True))
        # стовпчики
        n = len(heights)
        slot = (pw - 40) / n
        bw = slot * 0.62
        for i, h in enumerate(heights):
            bx = x0 + 20 + i * slot + (slot - bw) / 2
            col = colspike if i == spike_idx else colnorm
            g.append(rect(bx, base - h, bw, h, fill=col, stroke=col, sw=0.6, rx=1))
        # вісь
        g.append(line(x0 + 14, base, x0 + pw - 14, base, color=INK, sw=1.6))
        g.append(text(x0 + pw / 2, base + 20, "блоки пам'яті (RBER кожного)", size=10, color=MUTED))
        # підсумок під панеллю
        g.append(fitbox(x0 + 40, base + 34, pw - 80, 34, note, size=10.5, color=note_col,
                        fill=BG, stroke=note_col, sw=1.4, bold=True))
        return g

    # ліва панель: перекіс — один спайк за межею
    skew = [58, 46, 70, 40, 62, 200, 52, 66, 44, 60]
    f += panel(24, "Без вирівнювання: перекіс",
               skew, 5, STEEL, POS,
               "найгірший блок за межею → втрата даних", POS)
    # права панель: рівно — усі під межею, тісним гуртом
    even = [96, 102, 92, 99, 104, 95, 100, 93, 101, 97]
    f += panel(476, "З вирівнюванням: рівно",
               even, -1, FIELD, FIELD,
               "уся гістограма під межею → пристрій у спеці", FIELD)

    render(os.path.join(IMG, "rber-distribution.svg"), W, H, *f)


# ── 3. Код проти політики: дві ролі на двох рівнях ────────────────────────────
def fig_code_vs_policy():
    W, H = 880, 440
    f = [text(W / 2, 30, "Дві машини надійності Flash — на різних рівнях", size=17, bold=True)]
    f.append(text(W / 2, 52, "код лагодить помилки, що з'явилися; політика не дає їм з'явитися надто рано й надто густо",
                  size=11, color=MUTED, italic=True))

    # ── ліва панель: КОД (ECC) ──
    ax = 30
    f.append(rect(ax, 78, 396, 300, fill=BG, stroke=AMBER, sw=2, rx=12))
    f.append(rect(ax, 78, 396, 40, fill="#fdf3e0", stroke=AMBER, sw=2, rx=12))
    f.append(text(ax + 198, 104, "КОД — ECC", size=14, color=AMBER, bold=True))
    # кодове слово: дані + ECC
    f.append(rect(ax + 30, 142, 250, 30, fill="#eaf0fd", stroke=STEEL, sw=1.4, rx=4))
    f.append(text(ax + 155, 162, "дані блоку", size=12, color=STEEL, bold=True))
    f.append(rect(ax + 288, 142, 78, 30, fill="#fdf3e0", stroke=AMBER, sw=1.4, rx=4))
    f.append(text(ax + 327, 162, "ECC", size=12, color=AMBER, bold=True))
    rows_l = [
        "рівень: у кожному блоці",
        "коли: реактивно, у мить читання",
        "бюджет: до t помилок на слово",
        "мета: з RBER на вході — мізерний UBER",
    ]
    y = 208
    for r in rows_l:
        f.append(circle(ax + 30, y - 4, 3, fill=AMBER, stroke=AMBER, sw=1))
        f.append(text(ax + 44, y, r, size=11.5, anchor="start"))
        y += 34

    # ── права панель: ПОЛІТИКА (wear leveling) ──
    bx = 454
    f.append(rect(bx, 78, 396, 300, fill=BG, stroke=FIELD, sw=2, rx=12))
    f.append(rect(bx, 78, 396, 40, fill="#e9f7ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(bx + 198, 104, "ПОЛІТИКА — wear leveling", size=14, color=FIELD, bold=True))
    # ряд блоків з вирівнювальними стрілками
    by = 150
    for i in range(6):
        cx = bx + 44 + i * 56
        f.append(rect(cx, by, 40, 28, fill="#e9f7ef", stroke=FIELD, sw=1.3, rx=4))
        f.append(text(cx + 20, by + 19, "блок", size=9.5, color=FIELD, bold=True))
    f.append(arrow(bx + 60, by + 44, bx + 320, by + 44, color=INK, sw=1.6))
    f.append(text(bx + 198, by + 62, "знос розкладається рівно по всіх", size=10.5, color=MUTED, italic=True))
    rows_r = [
        "рівень: над усіма блоками",
        "коли: запобіжно, ще до появи помилок",
        "бюджет виправлення: жодного",
        "мета: тримати RBER кожного блока рівним і низьким",
    ]
    y = 240
    for r in rows_r:
        f.append(circle(bx + 30, y - 4, 3, fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(bx + 44, y, r, size=11.5, anchor="start"))
        y += 30

    # нижня спільна смуга
    f.append(rect(30, 392, 820, 34, fill="#f4f6f8", stroke=INK, sw=1.4, rx=10))
    f.append(text(W / 2, 414,
                  "разом → жоден блок не переступає межу коду → UBER під специфікацією ввесь паспортний ресурс",
                  size=12, color=INK, bold=True))
    render(os.path.join(IMG, "code-vs-policy.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Фігури до вставки math-uber-rber.md (біноміальний хвіст, вибір t, розкид)
# ══════════════════════════════════════════════════════════════════════════════
from math import lgamma, log, log1p, exp, log10


def _lterm(n, k, p):
    """log C(n,k)·p^k·(1−p)^(n−k) — у логарифмах, бо числа поза float."""
    return (lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)) + k * log(p) + (n - k) * log1p(-p)


def _l10tail(n, t, p):
    """log₁₀ P(X > t): сума хвоста через log-sum-exp, обрив на мізерних доданках."""
    m = _lterm(n, t + 1, p)
    acc = 0.0
    for k in range(t + 1, n + 1):
        d = _lterm(n, k, p) - m
        if d < -80:
            break
        acc += exp(d)
    return (m + log(acc)) / log(10)


def _l10uber(n, t, p):
    """log₁₀ UBER = log₁₀( P(слово невиправне) / n )."""
    return _l10tail(n, t, p) - log10(n)


# ── 4. Хвіст біноміала — майже геометрична прогресія ──────────────────────────
def fig_tail_terms():
    W, H = 880, 520
    N, T, P = 8752, 40, 1e-3
    f = [text(W / 2, 30, "Хвіст біноміала — майже геометрична прогресія", size=17, bold=True)]
    f.append(text(W / 2, 52, "BCH t = 40 на 1 КіБ (n = 8752), RBER p = 10⁻³: кожен наступний доданок майже вп'ятеро менший",
                  size=11, color=MUTED, italic=True))

    px0, py0, px1, py1 = 112, 112, 782, 400
    LO, HI = -22.0, -12.0

    def Y(v):
        return py1 - (v - LO) / (HI - LO) * (py1 - py0)

    f.append(line(px0, py1, px1, py1, color=INK, sw=1.8))
    f.append(line(px0, py0, px0, py1, color=INK, sw=1.8))
    f.append(text(px0 - 92, py0 - 14, "log₁₀ Tₖ", size=11.5, color=INK, anchor="start", bold=True))

    for v in range(-22, -11, 2):
        f.append(line(px0 - 5, Y(v), px0, Y(v), color=INK, sw=1.2))
        f.append(text(px0 - 11, Y(v) + 4, "%d" % v, size=10.5, color=MUTED, anchor="end"))
        if v > -22:
            # сітку обриваємо перед пояснювальною панеллю (500…776 по x, 122…240 по y),
            # щоб лінія не йшла крізь її текст
            xend = 492 if 122 <= Y(v) <= 240 else px1
            f.append(line(px0, Y(v), xend, Y(v), color="#e8e8e8", sw=1))

    ks = list(range(38, 51))
    pitch = (px1 - px0) / len(ks)
    bw = pitch * 0.62
    for i, k in enumerate(ks):
        v = _lterm(N, k, P) / log(10)
        bx = px0 + pitch * i + (pitch - bw) / 2
        col = FIELD if k <= T else POS
        fillc = "#e6f4ea" if k <= T else "#fdecea"
        f.append(rect(bx, Y(v), bw, py1 - Y(v), fill=fillc, stroke=col, sw=1.6, rx=3))
        f.append(text(bx + bw / 2, py1 + 18, str(k), size=10.5, color=INK))
    f.append(text((px0 + px1) / 2, py1 + 38, "k — скільки бітів перевернулось у слові", size=11.5, color=INK, bold=True))

    # межа коду: між k=40 (виправно) і k=41 (перший доданок хвоста)
    xdiv = px0 + pitch * 3
    f.append(line(xdiv, py0 - 4, xdiv, py1 + 26, color=INK, sw=1.6, dash="5 4"))

    # дужки-групи під віссю
    f.append(line(px0 + 6, py1 + 50, xdiv - 6, py1 + 50, color=FIELD, sw=2.2))
    f.append(text((px0 + xdiv) / 2, py1 + 66, "код виправляє (k ≤ t)", size=10.5, color=FIELD, bold=True))
    f.append(line(xdiv + 6, py1 + 50, px1 - 6, py1 + 50, color=POS, sw=2.2))
    f.append(text((xdiv + px1) / 2, py1 + 66, "хвіст: слово невиправне (k > t)", size=10.5, color=POS, bold=True))

    # виноска на провідний доданок
    xlead = px0 + pitch * 3 + pitch / 2
    ylead = Y(_lterm(N, 41, P) / log(10))
    f.append(text(xlead - 4, ylead - 12, "T₄₁ — провідний доданок", size=10.5, color=POS, bold=True, anchor="start"))

    # пояснювальна панель у вільній верхній правій зоні
    bx, by, bw2, bh2 = 500, 122, 276, 118
    f.append(rect(bx, by, bw2, bh2, fill="#fbfbfb", stroke=MUTED, sw=1.2, rx=8))
    f.append(mtext(bx + 14, by + 24, [
        "ρ = Tₖ₊₁/Tₖ = (n−k)/(k+1) · p/(1−p)",
        "спадає з k ⇒ найбільший при k = t+1:",
        "ρ ≈ n·p/(t+2) = 8.75/42 = 0.21",
        "Σ = T₄₁(1 + ρ + ρ² + …) = 1.26·T₄₁",
        "⇒ перший доданок задає весь хвіст",
    ], size=10.5, color=INK, anchor="start", lh=1.55))
    render(os.path.join(IMG, "tail-terms.svg"), W, H, *f)


# ── 5. Дві криві, два обриви, дві смуги ──────────────────────────────────────
def fig_two_cliffs():
    W, H = 900, 540
    f = [text(W / 2, 30, "Що міцніший код, то вужча смуга RBER, яку він терпить", size=17, bold=True)]
    f.append(text(W / 2, 52, "обидві криві — точний біноміальний хвіст; горизонталь — межа специфікації UBER = 10⁻¹⁵",
                  size=11, color=MUTED, italic=True))

    px0, py0, px1, py1 = 112, 100, 790, 420
    XL, XR, YB, YT = -5.2, -2.4, -30.0, 0.0

    def X(v):
        return px0 + (v - XL) / (XR - XL) * (px1 - px0)

    def Y(v):
        return py1 - (v - YB) / (YT - YB) * (py1 - py0)

    # смуги допуску (малюємо ПІД кривими)
    f.append(rect(X(-5.0), py0, X(log10(5.5061e-5)) - X(-5.0), py1 - py0,
                  fill="#e8eef7", stroke="none", sw=0, rx=0))
    f.append(rect(X(-3.0), py0, X(log10(1.2995e-3)) - X(-3.0), py1 - py0,
                  fill="#fdf3e3", stroke="none", sw=0, rx=0))

    f.append(line(px0, py1, px1, py1, color=INK, sw=1.8))
    f.append(line(px0, py0, px0, py1, color=INK, sw=1.8))
    f.append(text(px1, py1 + 46, "RBER (сирий рівень помилок) →", size=11.5, color=INK, anchor="end", bold=True))
    f.append(text(px0 - 96, py0 - 12, "log₁₀ UBER", size=11.5, color=INK, anchor="start", bold=True))

    for v in [-5, -4.5, -4, -3.5, -3, -2.5]:
        lab = {-5: "10⁻⁵", -4.5: "3·10⁻⁵", -4: "10⁻⁴", -3.5: "3·10⁻⁴", -3: "10⁻³", -2.5: "3·10⁻³"}[v]
        f.append(line(X(v), py1, X(v), py1 + 5, color=INK, sw=1.2))
        f.append(text(X(v), py1 + 21, lab, size=10.5, color=MUTED))
    for v in range(-30, 1, 5):
        f.append(line(px0 - 5, Y(v), px0, Y(v), color=INK, sw=1.2))
        f.append(text(px0 - 11, Y(v) + 4, "%d" % v, size=10.5, color=MUTED, anchor="end"))

    # межа специфікації
    f.append(line(px0, Y(-15), px1, Y(-15), color=FIELD, sw=1.7, dash="7 5"))
    f.append(text(px0 + 8, Y(-15) - 8, "UBER = 10⁻¹⁵ — межа специфікації", size=10.5, color=FIELD,
                  anchor="start", bold=True))

    def curve(n, t, col):
        pts = []
        for i in range(141):
            lp = XL + (XR - XL) * i / 140.0
            v = _l10uber(n, t, 10 ** lp)
            if YB <= v <= YT:
                pts.append((X(lp), Y(v)))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                % (" ".join("%.1f,%.1f" % q for q in pts), col))

    f.append(curve(4200, 8, STEEL))
    f.append(curve(8752, 40, AMBER))

    # робочі точки
    f.append(circle(X(-5.0), Y(_l10uber(4200, 8, 1e-5)), 5.5, fill=STEEL, stroke=BG, sw=1.6))
    f.append(circle(X(-3.0), Y(_l10uber(8752, 40, 1e-3)), 5.5, fill=AMBER, stroke=BG, sw=1.6))

    # підписи кривих
    f.append(text(X(-3.35), Y(-7.4), "BCH t = 8", size=12, color=STEEL, bold=True, anchor="start"))
    f.append(text(X(-2.62), Y(-24.4), "BCH t = 40", size=12, color=AMBER, bold=True, anchor="start"))

    # легенда у вільній верхній лівій зоні
    f.append(rect(126, 116, 396, 84, fill="#fbfbfb", stroke=MUTED, sw=1.2, rx=8))
    f.append(rect(138, 128, 13, 13, fill=STEEL, stroke=STEEL, sw=1, rx=2))
    f.append(text(160, 139, "BCH t = 8 (512 Б, n = 4200)", size=11, color=STEEL, anchor="start", bold=True))
    f.append(text(160, 156, "робоча точка 10⁻⁵ → межа 5.5·10⁻⁵  ⇒  смуга ×5.5", size=10.5, color=INK, anchor="start"))
    f.append(rect(138, 168, 13, 13, fill=AMBER, stroke=AMBER, sw=1, rx=2))
    f.append(text(160, 179, "BCH t = 40 (1 КіБ, n = 8752)", size=11, color=AMBER, anchor="start", bold=True))
    f.append(text(160, 196, "робоча точка 10⁻³ → межа 1.3·10⁻³  ⇒  смуга ×1.3", size=10.5, color=INK, anchor="start"))

    # нижня смуга-висновок
    f.append(rect(112, 464, 678, 34, fill="#f4f6f8", stroke=INK, sw=1.4, rx=10))
    f.append(text(451, 486, "міцніший код відсуває обрив праворуч — але робить його крутішим, тож лишає вужчу смугу",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "two-cliffs.svg"), W, H, *f)


# ── 6. Той самий середній знос — UBER на порядки різний ──────────────────────
def fig_spread_cost():
    W, H = 957, 470
    N, T = 8752, 40
    f = [text(W / 2, 30, "Той самий середній знос — UBER, що різниться на 12 порядків", size=17, bold=True)]
    f.append(text(W / 2, 52, "BCH t = 40 на 1 КіБ; у всіх чотирьох популяцій середній RBER однаковий — 10⁻³",
                  size=11, color=MUTED, italic=True))

    px0, px1 = 352, 852
    XL, XR = -20.0, -5.0

    def X(v):
        return px0 + (v - XL) / (XR - XL) * (px1 - px0)

    def dev(fr, r, pbar=1e-3):
        """UBER пристрою: частка fr блоків на r·p̄, решта — так, щоб середнє лишилось p̄."""
        pc = (1 - fr * r) / (1 - fr) * pbar
        return fr * 10 ** _l10uber(N, T, r * pbar) + (1 - fr) * 10 ** _l10uber(N, T, pc)

    rows = [
        ("рівний знос:\nусі блоки на 10⁻³", 10 ** _l10uber(N, T, 1e-3), "еталон", FIELD, "#e6f4ea"),
        ("1% блоків на 1.5×\n(решта 9.9·10⁻⁴)", dev(0.01, 1.5), "×2.4·10³", AMBER, "#fdf3e3"),
        ("1% блоків на 2×\n(решта 9.9·10⁻⁴)", dev(0.01, 2.0), "×4.8·10⁶", POS, "#fdecea"),
        ("1% блоків на 4×\n(решта 9.7·10⁻⁴)", dev(0.01, 4.0), "×7.4·10¹¹", POS, "#fdecea"),
    ]

    ytop, pitch, bh = 118, 68, 34
    for i, (lab, val, amp, col, fillc) in enumerate(rows):
        y = ytop + pitch * i
        f.append(mtext(px0 - 18, y + 10, lab.split("\n"), size=11, color=INK, anchor="end", lh=1.35))
        f.append(text(px0 - 18, y + 42, amp, size=10.5, color=col, anchor="end", bold=True))
        xe = X(log10(val))
        f.append(rect(px0, y, xe - px0, bh, fill=fillc, stroke=col, sw=1.6, rx=4))
        ok = "✓ у спеці" if val < 1e-15 else "✗ поза спекою"
        f.append(text(xe + 9, y + 22, "10%s   %s" % (_sup(log10(val)), ok), size=11, color=col,
                      anchor="start", bold=True))

    ybot = ytop + pitch * 4 - 20
    f.append(line(px0, ybot, px1, ybot, color=INK, sw=1.8))
    for v in range(-20, -4, 2):
        f.append(line(X(v), ybot, X(v), ybot + 5, color=INK, sw=1.2))
        f.append(text(X(v), ybot + 21, "%d" % v, size=10.5, color=MUTED))
    f.append(text((px0 + px1) / 2, ybot + 40, "log₁₀ UBER пристрою", size=11.5, color=INK, bold=True))

    # межа специфікації
    f.append(line(X(-15), ytop - 14, X(-15), ybot, color=FIELD, sw=1.7, dash="7 5"))
    f.append(text(X(-15), ytop - 22, "межа 10⁻¹⁵", size=10.5, color=FIELD, bold=True))

    f.append(rect(40, 412, 820, 34, fill="#f4f6f8", stroke=INK, sw=1.4, rx=10))
    f.append(text(W / 2, 434, "сумарний знос і середній RBER скрізь однакові — змінюється ЛИШЕ ширина гістограми",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "spread-cost.svg"), W, H, *f)


def _sup(v):
    """−18.57 → «⁻¹⁸·⁵⁷» (надрядкові цифри для підпису степеня)."""
    m = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
         "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻", ".": "·"}
    return "".join(m[c] for c in ("%.2f" % v))


if __name__ == "__main__":
    fig_cliff()
    fig_distribution()
    fig_code_vs_policy()
    fig_tail_terms()
    fig_two_cliffs()
    fig_spread_cost()
    print("OK: 6 figures ->", IMG)


# ── 7. Профіль ризику: хто платить за UBER пристрою ───────────────────────────
from math import fsum
from statistics import NormalDist

_UBER_MEMO = {}


def _rber_of(e):
    """RBER росте експоненційно зі зносом: ×100 за паспортні 3000 циклів."""
    return min(1e-5 * 100.0 ** (e / 3000.0), 0.5)


def _block_uber_of(e):
    if e not in _UBER_MEMO:
        _UBER_MEMO[e] = 10 ** _l10uber(8752, 40, _rber_of(e))
    return _UBER_MEMO[e]


def _wear_pop(nblk, mu, sigma):
    nd = NormalDist(mu, sigma)
    return [max(0, round(nd.inv_cdf((i + 0.5) / nblk))) for i in range(nblk)]


def fig_risk_profile():
    W, H = 900, 560
    NB = 4096
    f = [text(W / 2, 30, "Хто платить за UBER пристрою", size=17, bold=True)]
    f.append(text(W / 2, 52, "внесок окремого блока в UBER усього накопичувача; блоки впорядковані за зносом",
                  size=11, color=MUTED, italic=True))

    px0, py0, px1, py1 = 124, 112, 784, 418
    LO, HI = -22.5, -11.0
    RANKS = 16

    def Y(v):
        return py1 - (v - LO) / (HI - LO) * (py1 - py0)

    def X(i):
        return px0 + (i + 0.5) * (px1 - px0) / RANKS

    # сітка
    grid_ys = []
    for v in range(-22, -11, 2):
        grid_ys.append(Y(v))
        f.append(line(px0, Y(v), px1, Y(v), color="#e8e8e8", sw=1))
        f.append(line(px0 - 5, Y(v), px0, Y(v), color=INK, sw=1.2))
        f.append(text(px0 - 11, Y(v) + 4, "%d" % v, size=10.5, color=MUTED, anchor="end"))
    f.append(line(px0, py1, px1, py1, color=INK, sw=1.8))
    f.append(line(px0, py0, px0, py1, color=INK, sw=1.8))
    f.append(text(px0 - 100, py0 - 16, "log₁₀ внеску", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text((px0 + px1) / 2, py1 + 44, "ранг блока за зносом (1 = найзношеніший з 4096)",
                  size=11.5, color=INK, bold=True))
    for i in range(RANKS):
        f.append(text(X(i), py1 + 20, str(i + 1), size=10, color=MUTED))

    # межа специфікації
    f.append(line(px0, Y(-15), px1, Y(-15), color=FIELD, sw=1.7, dash="7 5"))
    f.append(text(px0 + 8, Y(-15) - 7, "межа специфікації 10⁻¹⁵", size=10.5, color=FIELD, bold=True))

    series = []
    for sigma, col, fillc in ((150, POS, "#fdecea"), (15, NEG, "#eaf0fd")):
        pop = _wear_pop(NB, 3000, sigma)
        dev = fsum(_block_uber_of(e) for e in pop) / NB
        prof = sorted((_block_uber_of(e) / NB for e in pop), reverse=True)
        series.append((sigma, col, dev, prof))

        # лінія UBER пристрою
        dev_y = Y(log10(dev))
        f.append(line(px0, dev_y, px1, dev_y, color=col, sw=1.6, dash="6 4"))
        # мітка над лінією за замовчуванням; якщо там впритул сітка (значення близьке до
        # круглого log-рівня) — переносимо під лінію, де є вільний простір до кривої
        label_y = dev_y - 8
        if any(abs(label_y - gy) < 8 for gy in grid_ys):
            label_y = dev_y + 16
        f.append(text(px1 - 6, label_y, "UBER пристрою = 10%s" % _sup(log10(dev)),
                      size=10.5, color=col, bold=True, anchor="end"))

        # точки внеску
        pts = [(X(i), Y(log10(prof[i]))) for i in range(RANKS)]
        for a, b in zip(pts, pts[1:]):
            f.append(line(a[0], a[1], b[0], b[1], color=col, sw=1.8))
        for cx, cy in pts:
            f.append(circle(cx, cy, 3.6, fill=fillc, stroke=col, sw=1.6))

    # панель-пояснення у вільній смузі між кривими
    bx, by, bw, bh = 168, 228, 570, 70
    f.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke=MUTED, sw=1.2, rx=8))
    s_dev, f_dev = series[0][2], series[1][2]
    s_top, f_top = series[0][3][0], series[1][3][0]
    f.append(mtext(bx + 14, by + 22, [
        "перекіс σ=150: пунктир лежить майже НА блоці №1 (розрив %.1f порядку)" % (log10(s_dev) - log10(s_top)),
        "        ⇒ сума ≈ ОДИН найгірший блок: він несе %.0f%% ризику (чесна частка — 0.02%%)" % (s_top / s_dev * 100),
        "вирівняно σ=15, той самий Σe: розрив %.1f порядку ⇒ сума ≈ 4096 × типовий блок"
        % (log10(f_dev) - log10(f_top)),
    ], size=10.5, color=INK, anchor="start", lh=1.6))
    render(os.path.join(IMG, "risk-profile.svg"), W, H, *f)


if __name__ == "__main__":
    fig_risk_profile()
    print("OK: risk-profile.svg ->", IMG)
