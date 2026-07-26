# -*- coding: utf-8 -*-
"""Фігури до теми «Проріджування (decimation)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── допоміжне ────────────────────────────────────────────────────────────────
def stem(x, base, h, color, w=3, dot=True):
    out = line(x, base, x, base - h, color=color, sw=w)
    if dot and h > 0:
        out += circle(x, base - h, 3.2, fill=color, stroke=color, sw=0)
    return out


def axis(x0, x1, y, color=INK, sw=1.6, label=None):
    out = line(x0, y, x1 + 6, y, color=color, sw=sw)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x1 + 14, y, x1 + 6, y - 4, x1 + 6, y + 4, color))
    if label:
        out += text(x1 + 6, y + 20, label, size=10, color=MUTED, italic=True, anchor="end")
    return out


def blob(xl, xr, base, height_fn, color, opacity=0.5, N=48):
    pts = [(xl, base)]
    for i in range(N + 1):
        t = i / N
        x = xl + (xr - xl) * t
        pts.append((x, base - height_fn(t)))
    pts.append((xr, base))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="1.4"/>' % (poly, color, opacity, color))


# ── 1. Канонічний ланцюг децимації ───────────────────────────────────────────
def fig_chain():
    W, H = 790, 210
    f = [text(W / 2, 28, "Проріджування — дві дії: спершу фільтр, тоді зниження частоти",
              size=15, bold=True)]
    ycy = 108

    # вхід
    f.append(text(58, ycy - 2, "x[n]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(58, ycy + 20, "48 кГц", size=11, color=MUTED, anchor="start"))
    f.append(arrow(112, ycy, 168, ycy, color=INK, sw=1.9))

    # блок ФНЧ
    b1x, b1w = 170, 190
    f.append(rect(b1x, ycy - 30, b1w, 60, fill="#eaf6ef", stroke=FIELD, sw=1.8))
    f.append(mtext(b1x + b1w / 2, ycy - 4, ["ФНЧ (антиаліасинг)", "зріз fs/2M = 6 кГц"],
                   size=12, color=INK))

    f.append(arrow(b1x + b1w + 2, ycy, b1x + b1w + 58, ycy, color=INK, sw=1.9))

    # блок ↓M
    b2x, b2w = b1x + b1w + 60, 96
    f.append(rect(b2x, ycy - 30, b2w, 60, fill="#eef2fb", stroke=NEG, sw=1.8))
    f.append(text(b2x + b2w / 2, ycy + 8, "↓ M", size=24, color=NEG, bold=True))

    f.append(arrow(b2x + b2w + 2, ycy, b2x + b2w + 58, ycy, color=INK, sw=1.9))

    # вихід
    ox = b2x + b2w + 66
    f.append(text(ox, ycy - 2, "y[m]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(ox, ycy + 20, "12 кГц", size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2, 188,
                  "фільтр знімає верх смуги · проріджувач знижує частоту — разом і лише в цьому порядку",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── 2. Пастка простого викидання: складання в смугу ──────────────────────────
def fig_naive_fold():
    W, H = 770, 300
    f = [text(W / 2, 28, "Просте викидання відліків: висока складова складається в смугу",
              size=15, bold=True)]

    x0, base = 90, 232
    kHz = 50.0  # px на кГц; вісь [0..12 кГц]
    def X(khz): return x0 + khz * kHz
    f.append(axis(x0, X(12), base, label="частота, кГц"))
    # позначки під віссю
    for khz, lab in [(0, "0"), (2, "2"), (3, "3"), (6, "6"), (9, "9"), (12, "12")]:
        f.append(line(X(khz), base, X(khz), base + 5, color=INK, sw=1.2))
        f.append(text(X(khz), base + 18, lab, size=10, color=MUTED))

    # дзеркало на новій межі Найквіста 6 кГц
    f.append(line(X(6), base, X(6), 96, color=MUTED, sw=1.5, dash="5,4"))
    f.append(text(X(6), 86, "дзеркало: нова межа Найквіста 6 кГц",
                  size=10.5, color=MUTED, bold=True))

    # сигнал 2 кГц (зелений)
    f.append(stem(X(2), base, 118, FIELD))
    f.append(text(X(2), base - 128, "сигнал", size=10.5, color=FIELD, bold=True))
    f.append(text(X(2), base - 142, "2 кГц", size=10.5, color=FIELD, bold=True))

    # зайва складова 9 кГц (синій)
    f.append(stem(X(9), base, 92, NEG))
    f.append(text(X(9), base - 102, "зайве", size=10.5, color=NEG, bold=True))
    f.append(text(X(9), base - 116, "9 кГц", size=10.5, color=NEG, bold=True))

    # аліас 3 кГц (червоний)
    f.append(stem(X(3), base, 70, POS))
    f.append(text(X(3) + 6, base - 80, "аліас 3 кГц", size=10.5, color=POS, bold=True, anchor="start"))

    # дуга-відбиття 9к → 3к
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
             % (X(9), base - 96, X(6), 120, X(3), base - 74, POS))

    f.append(text(W / 2, 286,
                  "9 кГц на 3 правіше за дзеркало → аліас лягає на 3 ліворуч → фальшиві 3 кГц у смузі сигналу",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "naive-fold.svg"), W, H, *f)


# ── 3. Три кроки в спектрі: фільтр звільняє смугу, вісь стискається ───────────
def fig_frequency():
    W, H = 730, 470
    f = [text(W / 2, 28, "Проріджування у частотах: зняти верх, тоді стиснути вісь",
              size=15, bold=True)]

    x0, x1 = 96, 654
    span = x1 - x0
    cut = x0 + span * (6.0 / 24.0)      # fs/2M = 6 кГц на осі [0..24]

    def useful(t):  # корисний горб коло нуля
        return 60 * math.exp(-((t / 0.16) ** 2)) + 10 * math.exp(-((t - 0.05) / 0.5) ** 2)

    def junk(t):    # широкосмугова зайвина, невисока
        return 20 * (0.55 + 0.35 * math.exp(-((t - 0.55) / 0.5) ** 2))

    # ── Панель A: вихідний спектр ──
    yA = 118
    f.append(text(x0, yA - 78, "1 · вихідний спектр (48 кГц): корисне коло нуля + зайвина вгорі",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yA))
    f.append(blob(cut, x1, yA, lambda t: junk(t), MUTED, opacity=0.35))
    f.append(blob(x0, cut, yA, lambda t: useful(t * (6.0 / 24.0)), FIELD, opacity=0.55))
    f.append(line(cut, yA, cut, yA - 74, color=NEG, sw=1.4, dash="5,4"))
    f.append(text(cut + 5, yA - 62, "fs/2M = 6 кГц", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(x1, yA + 20, "24 кГц", size=9.5, color=MUTED, anchor="end"))

    # ── Панель B: після ФНЧ ──
    yB = 262
    f.append(text(x0, yB - 78, "2 · після ФНЧ: усе вище 6 кГц зрізано, лишилася сама смуга",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yB))
    f.append(blob(x0, cut, yB, lambda t: useful(t * (6.0 / 24.0)), FIELD, opacity=0.55))
    f.append(line(cut, yB, cut, yB - 74, color=NEG, sw=1.4, dash="5,4"))
    f.append(text(cut + 5, yB - 62, "зріз", size=10, color=NEG, bold=True, anchor="start"))

    # ── Панель C: після ↓M ──
    yC = 406
    mid = x0 + span * 0.5   # 6 кГц = нова межа Найквіста = середина осі [0..12]
    f.append(text(x0, yC - 78, "3 · після ↓M: вісь стиснулась удвічі, смуга розтяглась, образи нарізно",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yC))
    f.append(blob(x0, mid, yC, lambda t: useful(t * 0.5), FIELD, opacity=0.55))       # база
    f.append(blob(mid, x1, yC, lambda t: useful((1 - t) * 0.5), FIELD, opacity=0.22))  # образ
    f.append(line(mid, yC, mid, yC - 74, color=NEG, sw=1.4, dash="5,4"))
    f.append(text(mid + 5, yC - 62, "нова межа 6 кГц", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 + span * 0.25, yC + 20, "смуга", size=9.5, color=FIELD, bold=True))
    f.append(text(x0 + span * 0.75, yC + 20, "образ (копія)", size=9.5, color=MUTED, italic=True))
    f.append(text(x1, yC + 20, "12 кГц", size=9.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "frequency.svg"), W, H, *f)


# ── 4. Ефективність: рахувати лише виходи, що лишаться ───────────────────────
def fig_efficiency():
    W, H = 770, 320
    f = [text(W / 2, 28, "Ефективна децимація: не рахувати те, що викинеш",
              size=15, bold=True)]

    n = 12
    xs = [140 + 42 * i for i in range(n)]
    kept = {0, 4, 8}

    def row(yb, smart, tag, note):
        # підпис рядка
        f.append(text(96, yb - 24, tag, size=11.5, color=INK, bold=True, anchor="end"))
        # вхідні відліки
        f.append(line(xs[0] - 14, yb, xs[-1] + 14, yb, color="#e2e2e2", sw=1.2))
        for x in xs:
            f.append(stem(x, yb, 20, NEG, w=2))
        # виходи нижче
        oy = yb + 46
        for i, x in enumerate(xs):
            if i in kept:
                f.append(circle(x, oy, 8, fill="#eaf6ef", stroke=FIELD, sw=1.8))
                f.append(text(x, oy + 4, "Σ", size=11, color=FIELD, bold=True))
            elif not smart:
                # порахований, але викинутий
                f.append(circle(x, oy, 8, fill="#fdecea", stroke=POS, sw=1.4))
                f.append(text(x, oy + 4, "×", size=11, color=POS, bold=True))
            # у smart — нічого (робота не робиться)
        f.append(text(xs[0] - 14, oy + 30, note, size=10, color=MUTED, italic=True, anchor="start"))

    row(96, False, "Наївно", "рахуємо всі 12 виходів, лишаємо 3 — дев'ять множень намарно")
    row(224, True, "Розумно", "фільтр стрибає через M — рахуємо лише 3 виходи, жодного зайвого")

    # виноска-виграш
    f.append(rect(636, 150, 118, 66, fill="#fffdf5", stroke="#9a7a1e", sw=1.6))
    f.append(mtext(695, 178, ["та сама", "відповідь", "×M менше роботи"], size=10.5,
                   color="#9a7a1e", bold=True))
    render(os.path.join(IMG, "efficiency.svg"), W, H, *f)


# ── 5. Багатошарова децимація замість одного велета ──────────────────────────
def fig_multistage():
    W, H = 770, 300
    f = [text(W / 2, 28, "Велике M: замість одного велета — каскад дешевих шарів",
              size=15, bold=True)]

    def blk(x, y, w, h, lines, stroke, fill, size=11):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8)
        out += mtext(x + w / 2, y + h / 2 - (len(lines) - 1) * size * 0.65 + size * 0.35,
                     lines, size=size, color=INK)
        return out

    def arr(x1, y, x2):
        return arrow(x1, y, x2, y, color=INK, sw=1.8)

    # ── верх: один каскад ↓8 ──
    yT = 92
    f.append(text(72, yT - 30, "Один каскад ↓8", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(72, yT + 6, "48 кГц", size=11, color=INK, bold=True, anchor="start"))
    f.append(arr(122, yT, 168, ))
    f.append(blk(170, yT - 32, 240, 64,
                 ["ФНЧ: зріз fs/16, дуже вузько", "порядок ~ сотні відводів"], POS, "#fdecea"))
    f.append(arr(412, yT, 452))
    f.append(blk(454, yT - 26, 70, 52, ["↓8"], NEG, "#eef2fb", size=16))
    f.append(arr(526, yT, 566))
    f.append(text(574, yT + 6, "6 кГц", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(650, yT + 6, "дорого", size=11, color=POS, bold=True, italic=True, anchor="start"))

    # ── низ: три шари ↓2·↓2·↓2 ──
    yB = 210
    f.append(text(72, yB - 34, "Три шари ↓2 · ↓2 · ↓2", size=12, color=FIELD, bold=True, anchor="start"))
    rates = ["48", "24", "12", "6"]
    x = 72
    f.append(text(x, yB + 6, rates[0] + " кГц", size=10.5, color=INK, bold=True, anchor="start"))
    x = 130
    for i in range(3):
        f.append(arr(x, yB, x + 34))
        bx = x + 36
        f.append(blk(bx, yB - 22, 96, 44, ["ФНЧ ↓2", "пологий"], FIELD, "#eaf6ef", size=10.5))
        x = bx + 96
        f.append(arr(x, yB, x + 30))
        f.append(text(x + 34, yB + 6, rates[i + 1] + " кГц", size=10, color=MUTED, bold=True, anchor="start"))
        x = x + 74

    f.append(text(W / 2, 284,
                  "кожен шар — пологий дешевий фільтр на дедалі нижчій частоті; на найгарячіший шар — безмножниковий CIC",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "multistage.svg"), W, H, *f)


# ── 6. Спектр після ↓M: сума M копій і умова неперекриття (вставка math) ──────
def fig_spectrum_copies():
    W, H = 780, 470
    f = [text(W / 2, 28, "Спектр після ↓M: сума M зсунутих копій — і коли вони налягають",
              size=15, bold=True)]
    PI = 95.0          # px на π
    cx = W / 2

    def X(w):          # ω в одиницях π → піксель
        return cx + w * PI

    def tri(c, hw, h, yb, color, opacity, sw=1.4):
        L, A, R = X(c - hw), X(c), X(c + hw)
        return ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
                'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
                % (L, yb, A, yb - h, R, yb, color, opacity, color, sw))

    def scene(yb, hw, tag, note, overlap):
        f.append(axis(X(-2.5), X(2.5), yb, label="ω"))
        # межі фундаментального періоду ±π
        for s in (-1, 1):
            f.append(line(X(s), yb, X(s), yb - 92, color=MUTED, sw=1.3, dash="5,4"))
        for w, lab in [(-2, "−2π"), (-1, "−π"), (0, "0"), (1, "π"), (2, "2π")]:
            f.append(line(X(w), yb, X(w), yb + 5, color=INK, sw=1.1))
            f.append(text(X(w), yb + 19, lab, size=10, color=MUTED))
        # копії-сусіди k=1,2 (центри ±2π)
        f.append(tri(2.0, hw, 70, yb, NEG, 0.30))
        f.append(tri(-2.0, hw, 70, yb, NEG, 0.30))
        # центральна копія k=0
        f.append(tri(0.0, hw, 70, yb, FIELD, 0.48))
        if overlap:
            for xl, xr in [(2.0 - hw, hw), (-hw, -(2.0 - hw))]:
                f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                         'fill-opacity="0.30"/>' % (X(xl), yb - 70, X(xr) - X(xl), 70, POS))
        f.append(text(X(-2.45), yb - 80, tag, size=12, color=INK, bold=True, anchor="start"))
        f.append(text(X(-2.45), yb + 40, note, size=10.5, color=MUTED, italic=True, anchor="start"))

    scene(150, 1.0, "смуга = π/M   (гранична)",
          "три копії лише торкаються на ±π → образи стоять нарізно, аліасу нема", False)
    scene(340, 1.4, "смуга > π/M   (завелика)",
          "копії налягають → у червоній зоні дві різні частоти сходяться в один відлік (аліас)", True)
    render(os.path.join(IMG, "spectrum-copies.svg"), W, H, *f)


# ── 7. Шляхетна тотожність: фільтр переносимо на низьку частоту (вставка math) ─
def fig_noble_identity():
    W, H = 800, 300
    f = [text(W / 2, 30, "Шляхетна тотожність: той самий фільтр — на низькій частоті",
              size=15, bold=True)]

    def blk(x, y, w, h, lines, stroke, fill, size=12):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8)
        out += mtext(x + w / 2, y + h / 2 - (len(lines) - 1) * size * 0.65 + size * 0.35,
                     lines, size=size, color=INK)
        return out

    def arr(x1, y, x2):
        return arrow(x1, y, x2, y, color=INK, sw=1.8)

    # ── верхній ланцюг: H(z^M) → ↓M (фільтр на високій частоті fs) ──
    yT = 96
    f.append(text(64, yT + 4, "x[n]", size=13, bold=True, anchor="start"))
    f.append(text(64, yT + 23, "fs", size=10.5, color=MUTED, anchor="start"))
    f.append(arr(102, yT, 150))
    f.append(blk(152, yT - 27, 156, 54, ["H(z^M)", "фільтр на fs"], POS, "#fdecea"))
    f.append(arr(310, yT, 356))
    f.append(blk(358, yT - 25, 66, 50, ["↓M"], NEG, "#eef2fb", size=16))
    f.append(arr(426, yT, 472))
    f.append(text(478, yT + 4, "y[m]", size=13, bold=True, anchor="start"))
    f.append(text(566, yT + 4, "≈ N·fs множень/с", size=11, color=POS, italic=True, anchor="start"))

    f.append(text(W / 2, 156, "≡", size=30, bold=True))

    # ── нижній ланцюг: ↓M → H(z) (фільтр на низькій частоті fs/M) ──
    yB = 214
    f.append(text(64, yB + 4, "x[n]", size=13, bold=True, anchor="start"))
    f.append(text(64, yB + 23, "fs", size=10.5, color=MUTED, anchor="start"))
    f.append(arr(102, yB, 150))
    f.append(blk(152, yB - 25, 66, 50, ["↓M"], NEG, "#eef2fb", size=16))
    f.append(arr(220, yB, 266))
    f.append(blk(268, yB - 27, 156, 54, ["H(z)", "фільтр на fs/M"], FIELD, "#eaf6ef"))
    f.append(arr(426, yB, 472))
    f.append(text(478, yB + 4, "y[m]", size=13, bold=True, anchor="start"))
    f.append(text(566, yB + 4, "≈ N·fs/M множень/с", size=11, color=FIELD, italic=True, anchor="start"))

    f.append(text(W / 2, 286,
                  "той самий вихід — але тепер множення на fs/M, а не на fs: у M разів дешевше",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "noble-identity.svg"), W, H, *f)


# ── 8. Потоковий проріджувач: лічильник фази кермує feed()/ready() (вставка proj) ─
def fig_stream_timeline():
    W, H = 800, 250
    f = [text(W / 2, 28, "Потоковий проріджувач: лічильник фази кермує feed() / ready()",
              size=15, bold=True)]
    M, nfeeds, Nill = 4, 16, 8
    x0, dx, base = 70, 44, 150
    xs = [x0 + dx * i for i in range(nfeeds)]

    # смуга розігріву: буфер ще наповнюється (ілюстративно N = 8 відводів)
    warm_l = x0 - dx * 0.5
    warm_r = (xs[Nill - 2] + xs[Nill - 1]) / 2.0
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="150" fill="%s" fill-opacity="0.10"/>'
             % (warm_l, base - 78, warm_r - warm_l, POS))
    f.append(text((warm_l + warm_r) / 2, base - 66, "розігрів: буфер ще з нулів",
                  size=10.5, color=POS, bold=True))

    # вісь подач
    f.append(line(warm_l, base, xs[-1] + dx * 0.6, base, color=INK, sw=1.6))
    f.append(text(xs[-1] + dx * 0.6 + 8, base + 4, "feed()", size=10,
                  color=MUTED, italic=True, anchor="start"))

    for i, x in enumerate(xs):
        f.append(stem(x, base, 26, NEG, w=2))
        ph = (i % M) + 1                        # фаза ПІСЛЯ інкремента: 1,2,3,M
        fire = (ph == M)
        f.append(text(x, base + 20, "M" if fire else str(ph),
                      size=11, color=(POS if fire else MUTED), bold=fire))
        if fire:
            clean = (i + 1) >= Nill             # буфер уже повний?
            col = FIELD if clean else POS
            f.append(line(x, base - 30, x, base - 42, color=col, sw=1.5, dash="4,3"))
            f.append(circle(x, base - 52, 10, fill=("#eaf6ef" if clean else "#fdecea"),
                            stroke=col, sw=1.9))
            f.append(text(x, base - 48, "y" if clean else "×", size=12, color=col, bold=True))

    f.append(text(warm_l, base + 46,
                  "фаза 1→2→3→M: лише на M-й подачі — один вихід (ready), інакше нуль",
                  size=10.5, color=INK, anchor="start"))
    f.append(circle(x0 + 6, base + 72, 8, fill="#eaf6ef", stroke=FIELD, sw=1.7))
    f.append(text(x0 + 22, base + 76, "чистий вихід", size=10, color=MUTED, anchor="start"))
    f.append(circle(x0 + 190, base + 72, 8, fill="#fdecea", stroke=POS, sw=1.7))
    f.append(text(x0 + 206, base + 76, "розігрів — відкинути (для N=64, M=4 це перші 15)",
                  size=10, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "stream-timeline.svg"), W, H, *f)


# ── 9. Q15-акумулятор: чому int32 — пастка, а int64 — безпечно (вставка proj) ──
def fig_q15_accum():
    W, H = 800, 440
    f = [text(W / 2, 28, "Цілочислова згортка Q15: множ · накопич · зсунь · наситити",
              size=15, bold=True)]
    yT = 92

    def box(x, w, lines, stroke, fill):
        out = rect(x, yT - 24, w, 50, fill=fill, stroke=stroke, sw=1.8, rx=6)
        out += mtext(x + w / 2, yT - (len(lines) - 1) * 8 + 3, lines, size=11, color=INK)
        return out

    f.append(box(58, 116, ["a : Q15", "16 біт"], NEG, "#eef2fb"))
    f.append(text(180, yT + 4, "×", size=18, bold=True))
    f.append(box(196, 116, ["h : Q15", "16 біт"], NEG, "#eef2fb"))
    f.append(arrow(314, yT, 348, yT, color=INK, sw=1.8))
    f.append(box(350, 138, ["a·h : Q30", "до 31 біт"], FIELD, "#eaf6ef"))
    f.append(arrow(490, yT, 524, yT, color=INK, sw=1.8))
    f.append(box(526, 212, ["+= Σ (N доданків)", "акумулятор"], POS, "#fdecea"))

    # шкала розрядності
    yb = 300
    bx0, bx1, bits_max = 96, 700, 40

    def bx(bits):
        return bx0 + (bx1 - bx0) * bits / bits_max

    f.append(line(bx0, yb, bx1 + 10, yb, color=INK, sw=1.6))
    for b in range(0, bits_max + 1, 5):
        f.append(line(bx(b), yb, bx(b), yb + 5, color=INK, sw=1.1))
        f.append(text(bx(b), yb + 18, str(b), size=9.5, color=MUTED))
    f.append(text(bx1 + 12, yb + 18, "біт", size=10, color=MUTED, italic=True, anchor="start"))

    # стелі int32 / int64 (підписи рознесено, щоб не налягали)
    f.append(line(bx(31), 184, bx(31), yb, color=POS, sw=1.8, dash="6,4"))
    f.append(text(bx(31), 158, "стеля int32 = 2³¹", size=10.5, color=POS, bold=True))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (bx1 + 22, 178, bx1 + 8, 174, bx1 + 8, 182, FIELD))
    f.append(text(bx1 + 4, 176, "int64: 63 біт →", size=10, color=FIELD, bold=True, anchor="end"))

    def bar(bits, y, color, tip, side="right"):
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="22" fill="%s" fill-opacity="0.5"/>'
               % (bx0, y, bx(bits) - bx0, color))
        out += ('<rect x="%.1f" y="%.1f" width="3" height="22" fill="%s"/>'
                % (bx(bits) - 1.5, y, color))
        if side == "left":                      # підпис ЛІВОРУЧ від краю (осторонь стелі int32)
            out += text(bx(bits) - 8, y + 16, tip, size=11, color=color, bold=True, anchor="end")
        else:
            out += text(bx(bits) + 7, y + 16, tip, size=11, color=color, bold=True, anchor="start")
        return out

    f.append(bar(30.0, 192, FIELD, "2³⁰", side="left"))
    f.append(bar(30.3, 228, NEG, "≈2³⁰·³", side="left"))
    f.append(bar(36.0, 264, POS, "2³⁶", side="right"))

    # легенда
    yl = 356

    def key(x, color, s):
        out = ('<rect x="%.1f" y="%.1f" width="14" height="14" fill="%s" fill-opacity="0.6"/>'
               % (x, yl - 11, color))
        out += text(x + 20, yl, s, size=10, color=INK, anchor="start")
        return out

    f.append(key(96, FIELD, "добуток одного відводу"))
    f.append(key(300, NEG, "реальна сума — ледве в int32"))
    f.append(key(520, POS, "наївна межа — переповнює int32"))

    f.append(text(W / 2, 398,
                  "«добуток влазить у int32» ≠ «і сума влізе» — тому акумулятор int64; "
                  "фініш: (acc+2¹⁴)>>15 → Q15, тоді насичення до int16",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(IMG, "q15-accum.svg"), W, H, *f)


# ── 10. Слово decimatio: римська кара проти децимації в ЦОС (вставка hist) ─────
def fig_decimatio_inversion():
    W, H = 820, 336
    f = [text(W / 2, 30, "Одне слово, обернений облік: Рим проти ЦОС", size=15, bold=True)]

    midx = W / 2
    f.append(line(midx, 58, midx, 300, color="#dcdcdc", sw=1.4, dash="6,5"))

    # ── Рим: decimatio ──
    lx = 52
    f.append(text(lx, 78, "Рим: decimatio", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(lx, 97, "кожен десятий гине, дев'ять лишаються",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    ry = 158
    for i in range(10):
        cxx = lx + 14 + i * 33
        if i == 9:
            f.append(circle(cxx, ry, 11, fill="#fdecea", stroke=POS, sw=2.4))
            f.append(text(cxx, ry + 5, "✗", size=15, color=POS, bold=True))
            f.append(text(cxx, ry + 34, "жертва", size=10, color=POS, bold=True))
        else:
            f.append(circle(cxx, ry, 11, fill="#eaf6ef", stroke=FIELD, sw=1.8))
    f.append(text(lx, 248, "видалено 1 з 10 — решта 9 живуть далі",
                  size=11, color=INK, anchor="start", bold=True))

    # ── ЦОС: децимація ↓M ──
    rx = midx + 34
    f.append(text(rx, 78, "ЦОС: децимація ↓M", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(rx, 97, "лишаємо кожен M-й, решту викидаємо",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    base = 176
    xs = [rx + 12 + i * 29 for i in range(11)]
    for i, x in enumerate(xs):
        if i % 4 == 0:
            f.append(stem(x, base, 44, FIELD, w=3))
        else:
            f.append(line(x, base, x, base - 15, color="#cfcfcf", sw=2.4))
    f.append(text(xs[0], base + 22, "вижив", size=10, color=FIELD, bold=True))
    f.append(text(rx, 248, "лишилось 1 з M — решту відкинуто (тут M = 4)",
                  size=11, color=INK, anchor="start", bold=True))

    f.append(text(W / 2, 322,
                  "у Римі «десятий» — жертва; у ЦОС «M-й» — той, хто лишається. І M уже не конче 10.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decimatio-inversion.svg"), W, H, *f)


# ── 11. Народження мультирейту: часова смуга (вставка hist) ───────────────────
def fig_multirate_timeline():
    W, H = 960, 372
    f = [text(W / 2, 30, "Народження багатошвидкісної обробки: ідея → теорія → CIC",
              size=15, bold=True)]
    y0 = 196
    xL, xR = 64, 900
    f.append(line(xL, y0, xR, y0, color=INK, sw=2.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (xR + 12, y0, xR + 2, y0 - 5, xR + 2, y0 + 5, INK))
    f.append(text(xR + 6, y0 + 22, "рік", size=10, color=MUTED, anchor="start", italic=True))

    def X(year):
        return xL + (year - 1972.2) * (xR - xL - 26) / 11.6

    for yr in range(1973, 1984):
        f.append(line(X(yr), y0 - 5, X(yr), y0 + 5, color=MUTED, sw=1.2))

    BELL, FR, ESLC = "#eef2fb", "#eaf6ef", "#fdecea"

    def milestone(year, above, color, lines, fill):
        xx = X(year)
        gap, size, pad = 30, 11, 8
        bh = len(lines) * size * 1.3 + 2 * pad - size * 0.3
        if above:
            cy = y0 - gap - bh / 2
            f.append(line(xx, y0 - 6, xx, y0 - gap, color=color, sw=1.4))
        else:
            cy = y0 + gap + bh / 2
            f.append(line(xx, y0 + 6, xx, y0 + gap, color=color, sw=1.4))
        box, _, _ = textbox(xx, cy, "\n".join(lines), size=size, pad=pad,
                            fill=fill, stroke=color, sw=1.6, color=INK)
        f.append(box)
        f.append(circle(xx, y0, 6.5, fill=color, stroke=color, sw=0))

    milestone(1973.0, True,  NEG,   ["1973 · Bell Labs", "Schafer & Rabiner", "DSP-інтерполяція"], BELL)
    milestone(1975.6, False, NEG,   ["1975-76 · Bell Labs", "Crochiere & Rabiner", "теорія M ступенів"], BELL)
    milestone(1976.2, True,  FIELD, ["1976 · TRT, Франція", "Bellanger та ін.", "поліфазні мережі"], FR)
    milestone(1979.9, False, POS,   ["лист. 1979 · ESL", "Newbold: CIC у", "пропозиції (практика)"], ESLC)
    milestone(1981.0, True,  POS,   ["1981 · IEEE ASSP", "Hogenauer: CIC", "(публікація)"], ESLC)
    milestone(1983.0, False, NEG,   ["1983 · книга", "Crochiere & Rabiner", "«Multirate DSP»"], BELL)

    # легенда інституцій
    ly = 350
    f.append(circle(150, ly, 6, fill=NEG, stroke=NEG, sw=0))
    f.append(text(162, ly + 4, "Bell Labs (США)", size=10, color=MUTED, anchor="start"))
    f.append(circle(342, ly, 6, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(354, ly + 4, "TRT (Франція)", size=10, color=MUTED, anchor="start"))
    f.append(circle(524, ly, 6, fill=POS, stroke=POS, sw=0))
    f.append(text(536, ly + 4, "ESL (США)", size=10, color=MUTED, anchor="start"))
    f.append(text(690, ly + 4, "практика випередила публікацію на ~16 місяців",
                  size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(IMG, "multirate-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_naive_fold()
    fig_frequency()
    fig_efficiency()
    fig_multistage()
    fig_spectrum_copies()
    fig_noble_identity()
    fig_stream_timeline()
    fig_q15_accum()
    fig_decimatio_inversion()
    fig_multirate_timeline()
    print("OK: 11 figures ->", IMG)
