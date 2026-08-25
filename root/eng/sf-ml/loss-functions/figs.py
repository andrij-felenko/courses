# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC1 = "#0ea5e9"   # блакитна крива (MSE / основна)
ACC2 = "#9333ea"   # фіолетова крива (MAE / друга)
ACC3 = "#e08a1e"   # тепла крива (Huber / третя)


# ── loss-as-scorer: приклади → промахи → одне число ────────────────────────────
# Ідея: показати саму суть — модель дала передбачення, істина відома, кожен промах
# перетворюється на «штраф», а всі штрафи згортаються в одне число (втрату).
def fig_scorer():
    W, H = 760, 380
    p = []
    # три приклади: істина, передбачення, штраф
    rows = [
        ("істина 8.0", "модель 7.6", "0.16", 0.16),
        ("істина 3.0", "модель 5.0", "4.00", 4.00),
        ("істина 9.0", "модель 8.7", "0.09", 0.09),
    ]
    x_t, x_p, x_s = 150.0, 360.0, 560.0
    p.append(text(x_t, 78, "правильна відповідь", size=12, color=FIELD, bold=True))
    p.append(text(x_p, 78, "передбачення", size=12, color=ACC1, bold=True))
    p.append(text(x_s, 78, "штраф  (промах)²", size=12, color=POS, bold=True))
    y = 118.0
    tot = 0.0
    for lt, lp, ls, pen in rows:
        p.append(fitbox(x_t - 85, y - 20, 170, 38, lt, size=12.5, fill="#eafaf1", stroke=FIELD))
        p.append(fitbox(x_p - 75, y - 20, 150, 38, lp, size=12.5, fill="#eef6ff", stroke=ACC1))
        p.append(text(x_p + 88, y + 5, "→", size=18, color=MUTED))
        # штраф як стовпчик пропорційно
        bh = 8 + 30 * pen / 4.0
        p.append(rect(x_s - 22, y - bh / 2, 44, bh, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
        p.append(text(x_s + 44, y + 5, ls, size=12, color=POS, bold=True, anchor="start"))
        tot += pen
        y += 62.0
    # згортка в одне число
    p.append(line(120, 300, 660, 300, color=INK, sw=1.2, dash="5 5"))
    b, bw, bh = textbox(W / 2, 340, "втрата = середнє штрафів = %.2f" % (tot / 3.0),
                        size=15, bold=True, fill="#fff7ed", stroke=ACC3)
    p.append(b)
    render(os.path.join(OUT, "loss-scorer.svg"), W, H, *p,
           title="Функція втрат: усі промахи → одне число")


# ── MSE vs MAE: форма штрафу від величини промаху ──────────────────────────────
# Ідея: квадрат карає великі промахи НЕПРОПОРЦІЙНО (парабола злітає), модуль —
# лінійно (пряма-галочка). Звідси різна чутливість до викидів.
def fig_mse_vs_mae():
    W, H = 760, 420
    p = []
    ox, oy = 110.0, 340.0
    pw, ph = 560.0, 280.0
    p.append(rect(ox, oy - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8))
    # осі: X — помилка e (від -3 до 3), Y — штраф (0..9)
    exmax = 3.0
    ymax = 9.0
    cx = ox + pw / 2.0

    def X(e):
        return cx + (pw / 2.0) * e / exmax

    def Y(v):
        return oy - ph * v / ymax

    # нульова вертикаль і сітка
    p.append(line(cx, oy, cx, oy - ph, color="#dfe4ea", sw=1.0))
    for e in (-3, -2, -1, 1, 2, 3):
        p.append(line(X(e), oy, X(e), oy - ph, color="#eef1f4", sw=1.0))
        p.append(text(X(e), oy + 18, "%d" % e, size=11, color=MUTED))
    for v in (3, 6, 9):
        p.append(line(ox, Y(v), ox + pw, Y(v), color="#eef1f4", sw=1.0))
        p.append(text(ox - 8, Y(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    p.append(text(cx, oy + 36, "помилка  e = передбачення − істина", size=12, color=INK))
    p.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 26 %.1f)">штраф</text>'
             % (oy - ph / 2, FONT, INK, oy - ph / 2))

    # парабола e² (MSE) — блакитна
    pts = []
    e = -exmax
    while e <= exmax + 1e-9:
        pts.append("%.1f,%.1f" % (X(e), Y(min(ymax, e * e))))
        e += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), ACC1))
    # модуль |e| (MAE) — фіолетова галочка
    p.append(line(X(-exmax), Y(exmax), cx, Y(0), color=ACC2, sw=2.6))
    p.append(line(cx, Y(0), X(exmax), Y(exmax), color=ACC2, sw=2.6))

    p.append(text(X(2.35), Y(8.2), "e²  (MSE)", size=12, color=ACC1, bold=True, anchor="start"))
    p.append(text(X(2.35), Y(2.0), "|e|  (MAE)", size=12, color=ACC2, bold=True, anchor="start"))
    # позначка «викид»
    p.append(circle(X(3), Y(9), 4.5, fill=ACC1, stroke=BG, sw=1.5))
    p.append(text(X(3), Y(9) - 12, "викид коштує 9!", size=10.5, color=POS, bold=True, anchor="end"))

    render(os.path.join(OUT, "mse-vs-mae.svg"), W, H, *p,
           title="Квадрат злітає, модуль росте рівно")


# ── cross-entropy: штраф за впевнену помилку злітає в нескінченність ───────────
# Ідея: коли істина = «так», штраф = −log(p) від упевненості моделі p у «так».
# Впевнене «так» (p→1) → штраф ~0; вагання (p=0.5) → помірний; впевнене «ні»
# (p→0), хоча істина «так», → штраф злітає до ∞. Оце й є «караємо самовпевненість».
def fig_cross_entropy():
    W, H = 760, 420
    p = []
    ox, oy = 110.0, 340.0
    pw, ph = 560.0, 280.0
    p.append(rect(ox, oy - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.3, rx=8))
    ymax = 6.0

    def X(pr):
        return ox + pw * pr

    def Y(v):
        return oy - ph * min(v, ymax) / ymax

    for pr in (0.2, 0.4, 0.6, 0.8, 1.0):
        p.append(line(X(pr), oy, X(pr), oy - ph, color="#eef1f4", sw=1.0))
        p.append(text(X(pr), oy + 18, "%.1f" % pr, size=11, color=MUTED))
    for v in (2, 4, 6):
        p.append(line(ox, Y(v), ox + pw, Y(v), color="#eef1f4", sw=1.0))
        p.append(text(ox - 8, Y(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    p.append(text(ox + pw / 2, oy + 36, "упевненість моделі в правильному класі  p", size=12, color=INK))
    p.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 26 %.1f)">штраф −log p</text>'
             % (oy - ph / 2, FONT, INK, oy - ph / 2))

    # крива −ln(p)
    pts = []
    pr = 0.006
    while pr <= 1.0 + 1e-9:
        pts.append("%.1f,%.1f" % (X(pr), Y(-math.log(pr))))
        pr += 0.004
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), ACC2))

    # три позначки-стани
    def mark(pr, lab, col, dy):
        v = -math.log(pr)
        p.append(circle(X(pr), Y(v), 5, fill=col, stroke=BG, sw=1.5))
        p.append(text(X(pr), Y(v) + dy, lab, size=10.5, color=col, bold=True, anchor="middle"))

    mark(0.95, "упевнене «так» → ~0", FIELD, -14)
    mark(0.5, "вагання → 0.69", ACC3, -14)
    mark(0.08, "упевнене «ні» → штраф злітає", POS, 22)

    render(os.path.join(OUT, "cross-entropy.svg"), W, H, *p,
           title="Перехресна ентропія: караємо самовпевнену помилку")


# ── mse-derivation: ланцюг «ґаусів шум → сума квадратів» (для вставки math) ────
# Ідея: показати чотири кроки, якими квадрат виповзає з показника дзвона в саму
# функцію втрат: щільність (e² у exp) → добуток по прикладах → логарифм робить
# суму й витягує квадрат → мінус перевертає максимум на мінімум (MSE).
def fig_derivation():
    W, H = 780, 470
    p = []
    cx = W / 2.0
    # чотири «картки»-кроки, з'єднані стрілками вниз
    steps = [
        ("1.  форма шуму: дзвін",
         "p(e) = (стала) · exp( −e² / 2σ² )",
         "квадрат сидить у показнику",
         ACC1),
        ("2.  правдоподібність усіх даних",
         "L = ∏ᵢ (стала) · exp( −eᵢ² / 2σ² )",
         "незалежні приклади → добуток",
         ACC1),
        ("3.  логарифм: добуток → сума",
         "log L = (стала) − 1/2σ² · Σ eᵢ²",
         "log витяг квадрат з-під exp",
         ACC3),
        ("4.  мінус перевертає напрям",
         "макс log L  ⇔  мін Σ eᵢ²  =  MSE",
         "MSE не обрано — вона випала",
         FIELD),
    ]
    y = 74.0
    bw, bh = 520.0, 74.0
    for i, (head, formula, note, col) in enumerate(steps):
        x = cx - bw / 2.0
        p.append(rect(x, y, bw, bh, fill="#fbfdff", stroke=col, sw=1.8, rx=9))
        p.append(text(cx, y + 21, head, size=13, color=col, bold=True))
        p.append(text(cx, y + 43, formula, size=14.5, color=INK, bold=True))
        p.append(text(cx, y + 62, note, size=11, color=MUTED, italic=True))
        if i < len(steps) - 1:
            p.append(arrow(cx, y + bh + 3, cx, y + bh + 26, color=MUTED, sw=2.0))
        y += bh + 29
    render(os.path.join(OUT, "mse-derivation.svg"), W, H, *p,
           title="Квадрат не обирають — він випадає з форми шуму")


if __name__ == "__main__":
    fig_scorer()
    fig_mse_vs_mae()
    fig_cross_entropy()
    fig_derivation()
    print("OK figs")
