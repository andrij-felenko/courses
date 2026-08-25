# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Базова стаття (entropy.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── surprise-curve: несподіванка однієї події I = log2(1/p) ────────────────────
# Ідея: це цеглинка ентропії. Часте (p→1) майже не дивує (→0 біт), рідкісне
# (p→0) дивує сильно. Дві точки-приклади прив'язують криву до чисел.

def fig_surprise_curve():
    W, H = 700, 320
    ox, oy = 84, 262
    aw, ah = 556, 214
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 6, oy + 22, "p — імовірність події", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah + 2, "біт", size=11, color=INK, bold=True, anchor="end"))

    pmax = 5.7
    pts = []
    n = 240
    for i in range(n + 1):
        pr = 0.018 + (1.0 - 0.018) * i / n
        bits = -math.log(pr, 2)
        x = ox + pr * aw
        yv = oy - min(bits, pmax) / pmax * ah
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    for bits in (1, 2, 3, 4, 5):
        yv = oy - bits / pmax * ah
        p.append(line(ox - 4, yv, ox + 4, yv, color=INK, sw=1.1))
        p.append(text(ox - 8, yv + 4, str(bits), size=9, color=MUTED, anchor="end"))
    for lbl, pr in (("0", 0.0), ("½", 0.5), ("1", 1.0)):
        x = ox + pr * aw
        p.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.1))
        p.append(text(x, oy + 18, lbl, size=9, color=MUTED))

    def mark(pr, lab, col, dy=-10):
        bits = -math.log(pr, 2)
        x = ox + pr * aw
        yv = oy - min(bits, pmax) / pmax * ah
        p.append(circle(x, yv, 4, fill=col, stroke=col, sw=1))
        p.append(line(x, oy, x, yv, color=col, sw=1, dash="3 3"))
        p.append(text(x + 6, yv + dy, lab, size=10, color=col, bold=True, anchor="start"))
    mark(0.9, "часте → ~0.15 біта", MUTED, dy=18)
    mark(0.5, "p=½ → рівно 1 біт", FIELD)
    mark(0.06, "рідкісне → ~4 біти", POS)

    render(os.path.join(OUT, "surprise-curve.svg"), W, H, *p,
           title="Несподіванка події: I = log₂(1/p) бітів")


# ── entropy-formula: H як зважене середнє несподіванок ─────────────────────────
# Ідея: розкласти формулу візуально на «частота × ціна-в-бітах», по символах,
# і показати, що сума цих добутків = середня вага символу H.

def fig_entropy_formula():
    W, H = 720, 320
    p = []
    # чотири символи з різними частотами
    syms = [("A", 0.50, FIELD, "#eafaf0"),
            ("B", 0.25, NEG, "#eef4ff"),
            ("C", 0.15, "#d98a00", "#fdf6e3"),
            ("D", 0.10, POS, "#fdecea")]
    x0, y0 = 64, 70
    rowh = 46
    p.append(text(x0, y0 - 18, "символ", size=10, color=MUTED, anchor="start", bold=True))
    p.append(text(x0 + 120, y0 - 18, "частота pᵢ", size=10, color=MUTED, anchor="middle", bold=True))
    p.append(text(x0 + 270, y0 - 18, "ціна log₂(1/pᵢ)", size=10, color=MUTED, anchor="middle", bold=True))
    p.append(text(x0 + 470, y0 - 18, "внесок pᵢ·log₂(1/pᵢ)", size=10, color=MUTED, anchor="middle", bold=True))
    total = 0.0
    for i, (s, pr, col, fill) in enumerate(syms):
        y = y0 + i * rowh
        cost = -math.log(pr, 2)
        contrib = pr * cost
        total += contrib
        p.append(rect(x0, y, 30, 30, fill=fill, stroke=col, sw=1.6))
        p.append(text(x0 + 15, y + 21, s, size=14, color=col, bold=True))
        # стовпчик частоти
        bw = pr * 150
        p.append(rect(x0 + 120 - bw / 2, y + 8, bw, 16, fill=fill, stroke=col, sw=1.2))
        p.append(text(x0 + 120, y + 40, "%.2f" % pr, size=9, color=MUTED))
        p.append(text(x0 + 270, y + 20, "%.2f біта" % cost, size=11, color=INK))
        p.append(text(x0 + 470, y + 20, "%.3f" % contrib, size=11, color=col, bold=True))
    # підсумкова рамка
    yb = y0 + len(syms) * rowh + 6
    p.append(line(x0 + 400, yb, x0 + 540, yb, color=INK, sw=1.2))
    b, bw, bh = textbox(x0 + 470, yb + 26, "H = %.2f біта / символ" % total, size=13,
                        bold=True, color=POS, fill="#fdf6e3", stroke="#d98a00", sw=1.8)
    p.append(b)
    p.append(text(x0 + 60, yb + 26, "сума внесків =", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "entropy-formula.svg"), W, H, *p,
           title="Ентропія — зважене середнє несподіванок символів")


# ── entropy-vs-p: крива H(p) для двох наслідків ────────────────────────────────
# Ідея: ГОЛОВНА фігура теми. H максимальна (1 біт) при рівних шансах p=½ і падає
# до 0 на краях (подія певна). Несподіванка живе тільки в невизначеності.

def fig_entropy_vs_p():
    W, H = 700, 330
    ox, oy = 80, 270
    aw, ah = 560, 210
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 6, oy + 22, "p — частка одного з двох наслідків", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "H, біт", size=11, color=INK, bold=True, anchor="end"))

    def Hb(pr):
        if pr <= 0 or pr >= 1:
            return 0.0
        return -(pr * math.log(pr, 2) + (1 - pr) * math.log(1 - pr, 2))

    pts = []
    n = 240
    for i in range(n + 1):
        pr = i / n
        x = ox + pr * aw
        yv = oy - Hb(pr) * ah
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # рівень H=1
    y1 = oy - 1.0 * ah
    p.append(line(ox, y1, ox + aw, y1, color=MUTED, sw=1, dash="5 4"))
    p.append(text(ox - 8, y1 + 4, "1", size=9, color=MUTED, anchor="end"))
    for lbl, pr in (("0", 0.0), ("½", 0.5), ("1", 1.0)):
        x = ox + pr * aw
        p.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.1))
        p.append(text(x, oy + 18, lbl, size=10, color=MUTED))

    # вершина
    xt = ox + 0.5 * aw
    p.append(circle(xt, y1, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(xt, y1 - 12, "макс: рівні шанси — повна несподіванка", size=11, color=POS, bold=True))
    # краї
    p.append(circle(ox, oy, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(ox + aw, oy, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(ox + aw, oy - 16, "подія певна → 0 біт", size=10, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(OUT, "entropy-vs-p.svg"), W, H, *p,
           title="Ентропія двох наслідків: максимум при рівних шансах")


# ── worked-dist: розподіл worked-прикладу ─────────────────────────────────────
# Ідея: розподіл 1/2,1/4,1/8,1/8 — степені двійки, тож H точно ціле число біт,
# і кожен внесок видно стовпчиком. Підпирає обчислення в тексті.

def fig_worked_dist():
    W, H = 700, 350
    p = []
    syms = [("A", 0.5, "1 біт", FIELD, "#eafaf0"),
            ("B", 0.25, "2 біти", NEG, "#eef4ff"),
            ("C", 0.125, "3 біти", "#d98a00", "#fdf6e3"),
            ("D", 0.125, "3 біти", POS, "#fdecea")]
    base_y = 250
    maxh = 170
    bw, gap = 90, 36
    x0 = (W - (len(syms) * bw + (len(syms) - 1) * gap)) / 2
    p.append(line(x0 - 20, base_y, x0 + len(syms) * bw + (len(syms) - 1) * gap + 10, base_y, color=INK, sw=1.6))
    for i, (s, pr, cost, col, fill) in enumerate(syms):
        x = x0 + i * (bw + gap)
        h = pr * maxh * 2
        p.append(rect(x, base_y - h, bw, h, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, base_y - h - 10, "p=%g" % pr, size=11, color=col, bold=True))
        p.append(text(x + bw / 2, base_y + 20, s, size=14, color=col, bold=True))
        p.append(text(x + bw / 2, base_y + 38, "код: " + cost, size=9, color=MUTED))
    b, _, _ = textbox(W / 2, base_y + 70, "H = ½·1 + ¼·2 + ⅛·3 + ⅛·3 = 1.75 біта / символ",
                      size=13, bold=True, color=POS, fill="#fdf6e3", stroke="#d98a00", sw=1.8)
    p.append(b)
    render(os.path.join(OUT, "worked-dist.svg"), W, H, *p,
           title="Worked-приклад: розподіл і його ентропія")


# ══════════════════════════════════════════════════════════════════════════════
# Детальна версія (entropy-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── why-log: чому логарифм — адитивність незалежних ────────────────────────────
# Ідея: дві незалежні події, ймовірності МНОЖАТЬСЯ (¼), а несподіванки ми хочемо
# ДОДАВАТИ (1+1=2). Логарифм — єдиний місток множення→додавання.

def fig_why_log():
    W, H = 720, 270
    p = []
    y = 110
    b1, w1, h1 = textbox(120, y, "подія 1\np=½", size=12, bold=True, color=NEG,
                         fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(b1)
    p.append(text(120 + w1 / 2 + 26, y + 6, "×", size=20, color=INK, bold=True))
    b2, w2, h2 = textbox(250, y, "подія 2\np=½", size=12, bold=True, color=NEG,
                         fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(b2)
    p.append(text(250 + w2 / 2 + 30, y + 6, "=", size=20, color=INK, bold=True))
    b3, w3, h3 = textbox(390, y, "разом\np=¼", size=12, bold=True, color=INK,
                         fill="#f4f6f8", stroke=INK, sw=1.6)
    p.append(b3)
    # стрілка-міст log
    p.append(arrow(390, y + h3 / 2 + 6, 390, y + h3 / 2 + 40, color="#8a5fb0", sw=2))
    p.append(text(412, y + h3 / 2 + 30, "log₂(1/p)", size=11, color="#8a5fb0", anchor="start", bold=True))
    # нижній рядок: біти додаються
    yb = y + 96
    for cx, lab, col in ((120, "1 біт", NEG), (250, "1 біт", NEG)):
        bb, bw, bh = textbox(cx, yb, lab, size=12, bold=True, color=col, fill="#eef4ff", stroke=col, sw=1.6)
        p.append(bb)
    p.append(text(186, yb + 6, "+", size=20, color=POS, bold=True))
    p.append(text(320, yb + 6, "=", size=20, color=INK, bold=True))
    bb, bw, bh = textbox(390, yb, "2 біти", size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(bb)
    p.append(text(W / 2 + 60, y + 6, "ймовірності множаться", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(text(W / 2 + 60, yb + 6, "несподіванки додаються", size=11, color=MUTED, italic=True, anchor="start"))
    render(os.path.join(OUT, "why-log.svg"), W, H, *p,
           title="Чому логарифм: множення ймовірностей → додавання бітів")


# ── conditional: контекст звужує розподіл наступного символу ───────────────────
# Ідея: умовна ентропія. Без контексту наступна літера широко розкидана (висока
# H); знаючи попередню («q»), розподіл стискається майже в одну («u») — H мала.

def fig_conditional():
    W, H = 720, 300
    p = []
    # ліворуч: широкий розподіл (без контексту)
    def dist(cx, cy, probs, title, sub, col, fill, htext):
        bw, gap = 16, 6
        n = len(probs)
        x0 = cx - (n * bw + (n - 1) * gap) / 2
        base = cy + 70
        for i, pr in enumerate(probs):
            h = pr * 150
            p.append(rect(x0 + i * (bw + gap), base - h, bw, h, fill=fill, stroke=col, sw=1.2))
        p.append(line(x0 - 8, base, x0 + n * (bw + gap) + 2, base, color=INK, sw=1.2))
        p.append(text(cx, cy - 8, title, size=12, color=col, bold=True))
        p.append(text(cx, cy + 8, sub, size=10, color=MUTED))
        p.append(text(cx, base + 22, htext, size=11, color=col, bold=True))

    # без контексту — багато ненульових, помірно рівних
    flat = [0.10, 0.12, 0.08, 0.11, 0.09, 0.10, 0.07, 0.12, 0.06, 0.08, 0.07]
    dist(190, 70, flat, "без контексту", "наступна літера — будь-яка", NEG, "#eef4ff",
         "H висока (~4 біти)")
    # стрілка
    p.append(arrow(330, 150, 400, 150, color=INK, sw=2))
    p.append(text(365, 138, "знаємо «q»", size=10, color="#8a5fb0", bold=True))
    # з контекстом — майже все в одній
    spike = [0.01, 0.01, 0.01, 0.94, 0.01, 0.01, 0.005, 0.005]
    dist(540, 70, spike, "після «q»", "майже завжди «u»", FIELD, "#eafaf0",
         "H мала (~0.5 біта)")
    p.append(text(W / 2, 278, "що більше контексту бачить модель — то вужчий розподіл наступного — то нижча ентропія",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "conditional.svg"), W, H, *p,
           title="Умовна ентропія: контекст звужує невизначеність")


# ── cross-entropy: чужа модель коштує зайвого ─────────────────────────────────
# Ідея: вісь біт/символ. H — справжнє дно. Кодуєш за НЕВІРНОЮ моделлю q —
# платиш cross-entropy > H; зайвий шмат = розбіжність (KL), чисто змарновані біти.

def fig_cross_entropy():
    W, H = 720, 280
    p = []
    ax0, ay = 90, 200
    p.append(arrow(ax0, ay, 650, ay, color=INK, sw=1.6))
    p.append(text(650, ay + 22, "біт на символ", size=11, color=INK, italic=True, anchor="end"))

    Hx = ax0 + 150
    Cx = ax0 + 320
    # H — справжня ентропія
    p.append(line(Hx, 70, Hx, ay + 6, color=FIELD, sw=2.4, dash="6 4"))
    p.append(text(Hx, 60, "H — справжнє дно", size=11, color=FIELD, bold=True))
    # cross-entropy — за чужою моделлю
    p.append(line(Cx, 90, Cx, ay + 6, color=POS, sw=2.4, dash="6 4"))
    p.append(text(Cx, 80, "за чужою моделлю q", size=11, color=POS, bold=True))
    # зона перевитрати
    p.append(rect(Hx, 120, Cx - Hx, ay - 120, fill="#fdecea", stroke="none", sw=0))
    p.append(text((Hx + Cx) / 2, 150, "змарновано", size=10, color=POS, bold=True))
    p.append(text((Hx + Cx) / 2, 167, "(розбіжність)", size=9, color=POS))
    # зона змісту
    p.append(rect(ax0, 120, Hx - ax0, ay - 120, fill="#eafaf0", stroke="none", sw=0))
    p.append(text((ax0 + Hx) / 2, 150, "зміст", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, ay + 56,
                  "що далі твоя модель q від правди p — то більше зайвих бітів понад дно H",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cross-entropy.svg"), W, H, *p,
           title="Перехресна ентропія: ціна неточної моделі")


# ── max-entropy: рівномірний розподіл = максимум ентропії ─────────────────────
# Ідея: серед усіх розподілів на N символах рівний дає НАЙБІЛЬШУ ентропію
# (log₂N): нічого не передбачиш. Будь-яка нерівність опускає H — отже, з'являється
# надлишок, який можна вирізати.

def fig_max_entropy():
    W, H = 720, 300
    p = []
    N = 8
    def panel(cx, probs, title, htext, col, fill, hot=False):
        bw, gap = 20, 8
        x0 = cx - (N * bw + (N - 1) * gap) / 2
        base = 210
        for i in range(N):
            h = probs[i] * 320
            p.append(rect(x0 + i * (bw + gap), base - h, bw, h, fill=fill, stroke=col, sw=1.3))
        p.append(line(x0 - 8, base, x0 + N * (bw + gap), base, color=INK, sw=1.3))
        p.append(text(cx, 70, title, size=12, color=col, bold=True))
        b, _, _ = textbox(cx, base + 40, htext, size=11, bold=True, color=col,
                          fill=fill, stroke=col, sw=1.6)
        p.append(b)

    uniform = [1.0 / N] * N
    panel(195, uniform, "рівномірний (усі рівні)", "H = log₂8 = 3 біти  (МАКС)", POS, "#fdecea")
    skew = [0.60, 0.18, 0.09, 0.05, 0.03, 0.02, 0.02, 0.01]
    panel(545, skew, "перекошений (нерівні)", "H ≈ 1.9 біта  (є надлишок)", FIELD, "#eafaf0")
    p.append(arrow(330, 150, 410, 150, color=INK, sw=2))
    p.append(text(W / 2, 268,
                  "будь-яка нерівність частот опускає ентропію нижче log₂N — саме цей розрив і вирізає стиснення",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "max-entropy.svg"), W, H, *p,
           title="Рівномірний розподіл — найбільша можлива ентропія")


if __name__ == "__main__":
    # базова
    fig_surprise_curve()
    fig_entropy_formula()
    fig_entropy_vs_p()
    fig_worked_dist()
    # детальна
    fig_why_log()
    fig_conditional()
    fig_cross_entropy()
    fig_max_entropy()
    print("OK: figures written to", OUT)
