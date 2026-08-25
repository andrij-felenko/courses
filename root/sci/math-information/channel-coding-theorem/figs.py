# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема Шеннона про кодування каналу» (channel-coding-theorem).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Різкий поріг на C: зона можливого і неможливого ────────────────────────
# Ідея, яку важко передати прозою: між «нижче C» і «вище C» — не плавний перехід,
# а стрімка стіна. Ліворуч похибку можна загнати до нуля НЕ знижуючи швидкості;
# праворуч надійний зв'язок неможливий у принципі.
def fig_threshold():
    W, H = 720, 320
    f = [text(W / 2, 30, "Теорема: різкий поріг рівно на C", 16, INK, "middle", bold=True)]

    left, right = 70, 650
    top, bot = 66, 210
    wall = 430  # положення межі C уздовж осі швидкості

    # зелена зона — можливе
    f.append(rect(left, top, wall - left - 4, bot - top, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    gcx = (left + wall) / 2
    f.append(text(gcx, top + 26, "R < C", 15, FIELD, "middle", bold=True))
    f.append(mtext(gcx, top + 52,
                   ["надійний зв'язок можливий:", "похибку можна загнати", "як завгодно близько до нуля"],
                   11.5, INK))

    # червона зона — неможливе
    f.append(rect(wall + 4, top, right - wall - 4, bot - top, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    rcx = (wall + right) / 2
    f.append(text(rcx, top + 26, "R > C", 15, POS, "middle", bold=True))
    f.append(mtext(rcx, top + 52,
                   ["надійний зв'язок", "неможливий —", "хоч що роби"],
                   11.5, INK))

    # сама стіна C
    f.append(line(wall, top - 8, wall, bot + 22, color=INK, sw=4))
    f.append(text(wall, bot + 40, "C", 15, INK, "middle", bold=True))
    f.append(text(wall, bot + 58, "пропускна здатність каналу", 11, MUTED, "middle"))

    # вісь швидкості
    f.append(line(left, bot, right + 10, bot, color=INK, sw=1.6))
    f.append(arrow(right - 4, bot, right + 16, bot, color=INK, sw=1.6))
    f.append(text(left - 2, bot + 16, "0", 11, MUTED, "middle"))
    f.append(text(right + 6, bot + 20, "швидкість R", 11, INK, "end", bold=True))

    # стрілка «підійти можна як завгодно близько, не знижуючи швидкості»
    f.append(arrow(wall - 150, 250, wall - 8, 250, color=FIELD, sw=2))
    f.append(text(wall - 150, 240, "підійти — як завгодно близько", 10.5, MUTED, "middle"))

    render(os.path.join(IMG, "threshold.svg"), W, H, *f)


# ── 2. Пакування «хмар шуму» в просторі послідовностей ────────────────────────
# Ідея: чому межа — саме C. Кожне довге кодове слово шум розмиває в хмару типових
# прийнятих послідовностей. Скільки роз'єднаних хмар влазить у простір — стільки
# слів і можна розрізнити: 2^(nH(Y)) / 2^(nH(Y|X)) = 2^(nI) = 2^(nC).
def fig_sphere_packing():
    W, H = 760, 475
    f = [text(W / 2, 28, "Чому саме C: пакування «хмар шуму»", 16, INK, "middle", bold=True)]

    # великий простір усіх прийнятих послідовностей
    rx0, ry0, rw, rh = 45, 52, 430, 310
    f.append(rect(rx0, ry0, rw, rh, fill="#fbfcfd", stroke=LINE, sw=1.6, rx=10))
    f.append(mtext(rx0 + rw / 2, 74,
                   ["простір усіх прийнятих послідовностей довжини n",
                    "(усього ~ 2^(n·H(Y)) типових)"],
                   11.5, MUTED))

    # роз'єднані хмари-кулі (кодові слова + типовий розкид шуму)
    r = 28
    rows = [(135, [110, 205, 300, 395]),
            (225, [157, 252, 347]),
            (315, [110, 205, 300, 395])]
    for cy, xs in rows:
        for cx in xs:
            f.append(circle(cx, cy, r, fill="#eaf0fd", stroke=NEG, sw=1.7))
            f.append(circle(cx, cy, 2.6, fill=NEG, stroke=NEG, sw=0))

    # права колонка — сам підрахунок
    bx, by, bw, bh = 500, 66, 235, 200
    f.append(rect(bx, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(mtext(bx + bw / 2, by + 26,
                   ["Скільки роз'єднаних хмар", "уміщує простір?"], 11.5, INK, bold=True))
    f.append(mtext(bx + bw / 2, by + 78,
                   ["2^(n·H(Y))", "──────────────", "2^(n·H(Y|X))"], 12, INK))
    f.append(text(bx + bw / 2, by + 138, "= 2^(n·I(X;Y))", 12.5, INK, "middle", bold=True))
    f.append(text(bx + bw / 2, by + 162, "= 2^(nC)", 13.5, FIELD, "middle", bold=True))
    f.append(text(bx + bw / 2, by + 186, "→ C біт на символ", 11, MUTED, "middle"))

    # легенда зразка-кулі
    ly = 392
    f.append(circle(72, ly, 15, fill="#eaf0fd", stroke=NEG, sw=1.7))
    f.append(circle(72, ly, 2.4, fill=NEG, stroke=NEG, sw=0))
    f.append(text(96, ly + 4,
                  "— кодове слово та його «хмара шуму»: усі послідовності, у які шум може його перетворити",
                  10.5, INK, "start"))

    # підсумкова смуга
    f.append(fitbox(45, 420, 690, 42,
                    "Нижче C хмари роз'єднані — приймач однозначно впізнає слово. Вище C їх більше, ніж місця: хмари налазять, плутанина неминуча.",
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "sphere-packing.svg"), W, H, *f)


# ── 3. Двійковий симетричний канал і бюджет біта ──────────────────────────────
# Ідея: у BSC кожен біт незалежно перевертається з імовірністю p. З 1 біта «місця»
# на символ невизначеність шуму H(p) з'їдає частину, а C = 1 − H(p) лишається на
# надійну інформацію. Для p = 0.1: H ≈ 0.469, C ≈ 0.531.
def fig_bsc_budget():
    W, H = 720, 400
    f = [text(W / 2, 28, "Двійковий симетричний канал і бюджет біта", 16, INK, "middle", bold=True)]

    # вузли входу/виходу
    ix, ox = 175, 415
    y0, y1 = 100, 190
    rr = 22
    f.append(text(ix, 68, "вхід", 11.5, MUTED, "middle", bold=True))
    f.append(text(ox, 68, "вихід", 11.5, MUTED, "middle", bold=True))

    # прямі переходи (біт лишається) — зелені, підпис безпечно над/під лінією
    f.append(arrow(ix + rr, y0, ox - rr, y0, color=FIELD, sw=2))
    f.append(text((ix + ox) / 2, y0 - 12, "1 − p", 11.5, FIELD, "middle", bold=True))
    f.append(arrow(ix + rr, y1, ox - rr, y1, color=FIELD, sw=2))
    f.append(text((ix + ox) / 2, y1 + 22, "1 − p", 11.5, FIELD, "middle", bold=True))

    # перехресні переходи (переворот) — червоні, без інлайн-підпису (легенда праворуч)
    f.append(arrow(ix + rr, y0 + 12, ox - rr, y1 - 12, color=POS, sw=2))
    f.append(arrow(ix + rr, y1 - 12, ox - rr, y0 + 12, color=POS, sw=2))

    for cy, lab in [(y0, "0"), (y1, "1")]:
        f.append(circle(ix, cy, rr, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(ix, cy + 6, lab, 15, INK, "middle", bold=True))
        f.append(circle(ox, cy, rr, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(ox, cy + 6, lab, 15, INK, "middle", bold=True))

    # легенда переходів
    f.append(rect(475, 92, 215, 108, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=8))
    f.append(mtext(582, 118,
                   ["p = 0.1 — біт перевертається", "1 − p = 0.9 — біт лишається", "(кожен біт — незалежно)"],
                   11, INK))
    f.append(text(582, 182, "p — «шум» каналу", 11, POS, "middle", bold=True))

    # бюджет біта
    bx, bw, byy, bhh = 90, 540, 300, 40
    split = bx + 0.469 * bw
    f.append(text(W / 2, 268, "1 біт «місця» на кожен канальний символ", 12.5, INK, "middle", bold=True))
    f.append(rect(bx, byy, split - bx, bhh, fill="#fdecea", stroke=POS, sw=1.6, rx=0))
    f.append(rect(split, byy, bx + bw - split, bhh, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=0))
    f.append(mtext((bx + split) / 2, byy + 17, ["H(p) ≈ 0.469", "з'їв шум"], 11.5, INK))
    f.append(mtext((split + bx + bw) / 2, byy + 17, ["C = 1 − H(p) ≈ 0.531", "надійна інформація"], 11.5, INK))

    f.append(text(W / 2, 372,
                  "навіть коли 1 з 10 бітів перевертається, ~0.53 біта на символ проходять надійно, похибка → 0",
                  11, MUTED, "middle"))

    render(os.path.join(IMG, "bsc-budget.svg"), W, H, *f)


# ── Локальні помічники для кривих (svgkit не має polyline/polygon) ─────────────
def _poly(points, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts = " ".join("%.2f,%.2f" % (x, y) for x, y in points)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (pts, color, sw, d))


def _polygon(points, fill, stroke="none", sw=1.0):
    pts = " ".join("%.2f,%.2f" % (x, y) for x, y in points)
    s = ('stroke="%s"' % stroke) if stroke != "none" else 'stroke="none"'
    return '<polygon points="%s" fill="%s" %s stroke-width="%.1f"/>' % (pts, fill, s, sw)


# ── 4. AEP: маса збирається на типовому наборі ────────────────────────────────
# Ідея математичного ядра: −(1/n)·log₂p(X₁…Xₙ) — це середнє n незалежних величин
# −log₂p(Xᵢ) з матсподіванням H(X). За законом великих чисел воно стискається на
# H(X): який блок не прийшов би, він майже напевно «типовий». Це точна заміна
# нечіткого слова «хмара».
def fig_aep_concentration():
    import math as _m
    W, Hh = 720, 384
    f = [text(W / 2, 30, "AEP: маса збирається на типовому наборі", 16, INK, "middle", bold=True)]
    left, right = 92, 648
    base = 300
    c = 0.469  # H(X) для джерела p = (0.9, 0.1)

    def X(v):
        return left + v * (right - left)   # v ∈ [0, 1]

    # вісь величини −(1/n)·log₂p
    f.append(line(left, base, right + 14, base, color=INK, sw=1.6))
    f.append(arrow(right + 6, base, right + 22, base, color=INK, sw=1.6))
    f.append(text(right + 12, base + 20, "−(1/n)·log₂ p", 11, INK, "end", bold=True))
    f.append(text(left - 4, base + 18, "0", 10.5, MUTED, "middle"))
    f.append(text(right, base + 18, "1", 10.5, MUTED, "middle"))

    # позначка H(X)
    f.append(line(X(c), base, X(c), 70, color=INK, sw=1.4, dash="4,4"))
    f.append(text(X(c), 62, "H(X) ≈ 0.469", 12, INK, "middle", bold=True))

    # три криві, дедалі вужчі (n = 10, 100, 1000)
    curves = [(0.150, 60, MUTED, "n = 10"),
              (0.062, 118, NEG, "n = 100"),
              (0.021, 198, FIELD, "n = 1000")]
    for sig, amp, col, _lab in curves:
        pts, v = [], 0.0
        while v <= 1.0001:
            y = base - amp * _m.exp(-((v - c) / sig) ** 2)
            pts.append((X(v), y))
            v += 0.01
        f.append(_poly(pts, col, sw=2.3))

    # легенда праворуч (де всі криві вже лягли на вісь — без накладань)
    lx, ly = 508, 92
    f.append(rect(lx, ly, 150, 80, fill="#fbfcfd", stroke=LINE, sw=1.3, rx=8))
    for i, (_sig, _amp, col, lab) in enumerate(curves):
        yy = ly + 24 + i * 20
        f.append(line(lx + 14, yy, lx + 40, yy, color=col, sw=3.2))
        f.append(text(lx + 48, yy + 4, lab, 11.5, INK, "start"))

    f.append(fitbox(92, 320, 556, 52,
                    ["Зі зростанням n розподіл величини −(1/n)·log₂p стискається у шпильку над H(X):",
                     "який блок не прийшов би, він майже напевно типовий."],
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "aep-concentration.svg"), W, Hh, *f)


# ── 5. Показник помилки: чому нижче C похибка тане експоненційно ───────────────
# Ідея: усереднена по випадкових кодах похибка ≤ 2^(−n(I−R)). У показнику — пряма
# з нахилом −(I−R): при R < I вона падає (добрий код існує), при R > I росте вгору
# (межа стає марною — територія оберненої частини). C = I = 0.531 (BSC, p = 0.1).
def fig_random_coding():
    W, Hh = 720, 384
    f = [text(W / 2, 30, "Показник помилки: нижче C похибка тане експоненційно",
              15.5, INK, "middle", bold=True)]
    left, right = 100, 632
    top, bot = 86, 300
    Nmax = 1000.0
    vmax, vmin = 30.0, -140.0
    I = 0.531

    def X(n):
        return left + (n / Nmax) * (right - left)

    def Y(val):
        return top + (vmax - val) / (vmax - vmin) * (bot - top)

    # осі
    f.append(line(left, bot, right + 40, bot, color=INK, sw=1.6))
    f.append(arrow(right + 32, bot, right + 48, bot, color=INK, sw=1.6))
    f.append(text(right + 40, bot + 20, "довжина блоку n", 11, INK, "end", bold=True))
    f.append(line(left, top - 8, left, bot + 6, color=INK, sw=1.6))
    f.append(text(left - 8, top - 14, "log₂(межа середньої похибки)", 10.5, INK, "start", bold=True))

    # лінія «межа = 1» (2^0): вище неї межа марна
    f.append(line(left, Y(0), right + 4, Y(0), color=MUTED, sw=1.3, dash="5,4"))
    f.append(text(right + 2, Y(0) - 6, "межа = 1 (2⁰)", 10, MUTED, "end"))

    rates = [(0.40, NEG, "R = 0.40  (< C)"),
             (0.50, FIELD, "R = 0.50  (< C)"),
             (0.55, POS, "R = 0.55  (> C)")]
    for R, col, lab in rates:
        slope = -(I - R)          # нахил показника
        vend = slope * Nmax
        f.append(line(X(0), Y(0), X(Nmax), Y(vend), color=col, sw=2.6))
        yy = Y(vend)
        dy = -8 if vend > 0 else 26
        f.append(text(X(Nmax) - 2, yy + dy, lab, 10.5, col, "end", bold=True))

    # підписи зон
    f.append(text(150, Y(24), "межа > 1 — марна (зона R > C)", 10, POS, "start"))
    f.append(text(150, Y(-120), "межа → 0 — добрий код існує (R < C)", 10, FIELD, "start"))

    f.append(fitbox(100, 326, 532, 50,
                    ["Усереднена похибка ≤ 2^(−n(I−R)). Нахил прямої — рівно (I−R): при R < C вона",
                     "летить до нуля з довжиною блоку, при R > C розвертається вгору."],
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "random-coding.svg"), W, Hh, *f)


# ── 6. Обернена частина: підлога похибки Pₑ ≥ 1 − C/R ─────────────────────────
# Ідея: нерівність Фано замикає стелю зверху. Ліворуч від C похибку можна загнати
# в нуль; праворуч на неї лягає незборима підлога 1 − C/R, що росте зі швидкістю.
def fig_fano_floor():
    W, Hh = 720, 360
    f = [text(W / 2, 30, "Обернена частина: підлога похибки  Pₑ ≥ 1 − C/R",
              15.5, INK, "middle", bold=True)]
    left, right = 100, 646
    top, bot = 74, 286
    Rmax, C = 1.2, 0.531

    def X(R):
        return left + (R / Rmax) * (right - left)

    def Y(P):
        return bot - P * (bot - top)

    # осі
    f.append(line(left, bot, right + 14, bot, color=INK, sw=1.6))
    f.append(arrow(right + 6, bot, right + 22, bot, color=INK, sw=1.6))
    f.append(text(right + 12, bot + 20, "швидкість R", 11, INK, "end", bold=True))
    f.append(line(left, top - 6, left, bot + 6, color=INK, sw=1.6))
    f.append(text(left - 6, top - 12, "похибка Pₑ", 11, INK, "start", bold=True))
    f.append(text(left - 10, Y(1.0) + 4, "1", 10.5, MUTED, "end"))
    f.append(text(left - 10, Y(0.0) + 4, "0", 10.5, MUTED, "end"))

    # межа C
    f.append(line(X(C), bot, X(C), top, color=INK, sw=1.4, dash="4,4"))
    f.append(text(X(C), top - 10, "C = 0.531", 12, INK, "middle", bold=True))

    # ліворуч від C: досяжна нульова похибка
    f.append(line(left, Y(0), X(C), Y(0), color=FIELD, sw=4))
    f.append(mtext((left + X(C)) / 2, Y(0) - 30, ["R < C:", "похибку → 0"], 10.5, FIELD, bold=True))

    # праворуч: заборонена смуга під кривою підлоги + сама крива
    pts, R = [], C
    while R <= Rmax + 1e-9:
        pts.append((X(R), Y(1 - C / R)))
        R += 0.01
    area = pts + [(X(Rmax), Y(0)), (X(C), Y(0))]
    f.append(_polygon(area, fill="#fdecea"))
    f.append(_poly(pts, POS, sw=2.8))
    f.append(text(X(1.02), Y(0.115), "недосяжно", 11, POS, "middle", bold=True))
    f.append(text(X(1.02), Y(0.075), "(Pₑ не може бути нижче)", 9.5, POS, "middle"))

    # робоча точка R = 0.7
    Rp = 0.7
    Pp = 1 - C / Rp
    f.append(line(X(Rp), bot, X(Rp), Y(Pp), color=MUTED, sw=1.2, dash="3,3"))
    f.append(circle(X(Rp), Y(Pp), 3.4, fill=POS, stroke=POS, sw=0))
    f.append(text(X(Rp) + 10, Y(Pp) - 8, "R = 0.70 → Pₑ ≥ 0.24", 10.5, INK, "start", bold=True))

    f.append(fitbox(100, 310, 546, 40,
                    "Вище C надійність неможлива: хоч який код, частка хибних повідомлень не впаде "
                    "нижче 1 − C/R. Рівно на C стіна між нулем і додатною підлогою.",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "fano-floor.svg"), W, Hh, *f)


# ── 7. Проєкт: виміряна блок-похибка vs довжина блока ──────────────────────────
# Не концептуальна, а ПРОЄКТНА фігура — справжні числа симулятора BSC із тексту
# вставки (p = 0.1, випадковий код, ML-декодер, seed 900+n). Вісь похибки —
# логарифмічна, бо саме на ній видно головне: під C крива пірнає на два порядки,
# над C — приклеюється до стелі й повзе до 1. Обидві швидкості дають ЦІЛЕ k:
# R = 1/4 → k = n/4, R = 3/4 → k = 3n/4 (інакше код просто не існує).
def fig_sim_threshold():
    W, Hh = 740, 424
    f = [text(W / 2, 30, "Вимір: блок-похибка пірнає під C і застрягає над C",
              15.5, INK, "middle", bold=True),
         text(W / 2, 51, "двійковий симетричний канал, p = 0.1, C = 0.531 біта/символ",
              11, MUTED, "middle")]
    L, Rx, T, B = 96, 664, 80, 340
    nmax = 68.0

    def X(n):
        return L + (n / nmax) * (Rx - L)

    def Y(e):
        return T + (-math.log10(e)) / 3.0 * (B - T)   # 1.0 угорі → 0.001 унизу

    # осі
    f.append(line(L, T - 10, L, B, color=INK, sw=1.6))
    f.append(arrow(L, T - 6, L, T - 24, color=INK, sw=1.6))
    f.append(line(L, B, Rx + 14, B, color=INK, sw=1.6))
    f.append(arrow(Rx + 6, B, Rx + 24, B, color=INK, sw=1.6))
    for e, lab in [(1.0, "1"), (0.1, "0.1"), (0.01, "0.01"), (0.001, "0.001")]:
        y = Y(e)
        f.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 12, y + 4, lab, 10.5, MUTED, "end"))
    for n in [8, 16, 24, 32, 40, 48, 56, 64]:
        x = X(n)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        f.append(text(x, B + 20, str(n), 10.5, MUTED, "middle"))
    # підпис осі — НИЖЧЕ за позначки n, інакше налазить на «64»
    f.append(text(Rx + 22, B + 40, "довжина блока n", 11, INK, "end", bold=True))
    f.append(mtext(L - 56, T + 6, ["блок-", "похибка"], 10.5, INK, "start"))

    # виміряно симулятором зі вставки (40000 / 20000 спроб на точку)
    below = [(8, 0.085125), (16, 0.056400), (24, 0.027800), (32, 0.013900),
             (40, 0.007725), (48, 0.004300), (56, 0.002475), (64, 0.001450)]
    above = [(4, 0.354350), (8, 0.497600), (12, 0.558400), (16, 0.610250),
             (20, 0.666200), (24, 0.701050)]
    for series, col in [(below, FIELD), (above, POS)]:
        f.append(_poly([(X(n), Y(e)) for n, e in series], col, sw=2.6))
        for n, e in series:
            f.append(circle(X(n), Y(e), 4.6, fill="#ffffff", stroke=col, sw=2.4))

    f.append(text(492, 100, "R = 3/4 = 0.75 > C", 12.5, POS, "middle", bold=True))
    f.append(text(492, 119, "приклеїлася до стелі, повзе до 1", 10.5, MUTED, "middle"))
    f.append(text(252, 300, "R = 1/4 = 0.25 < C", 12.5, FIELD, "middle", bold=True))
    f.append(text(252, 319, "пірнає — і не має дна", 10.5, FIELD, "middle"))

    render(os.path.join(IMG, "proj-sim-threshold.svg"), W, Hh, *f)


# ── 8. Проєкт: пастка повторення — похибка падає лише разом зі швидкістю ────────
# Точний біноміальний хвіст для повторення ×1,3,5,7,9,11. Траєкторія йде вниз-і-
# ліворуч: щоб знизити похибку, повторення жертвує швидкістю. Правий-нижній кут
# (висока швидкість + мала похибка, аж до стелі C) лишається порожнім.
# «×r» — кратність повторення; літеру n тут навмисно НЕ вживаємо, бо в сусідній
# фігурі n — довжина блока, і плутати ці дві осі не можна.
def fig_repetition_trap():
    W, Hh = 740, 432
    f = [text(W / 2, 30, "Пастка повторення: похибка падає лише разом зі швидкістю",
              15.5, INK, "middle", bold=True)]
    L, Rx, T, B = 98, 648, 68, 338
    xr, ytop, ybot = 1.08, -0.8, -3.8   # y — десятковий логарифм похибки

    def X(r):
        return L + (r / xr) * (Rx - L)

    def Y(e):
        return T + (ytop - math.log10(e)) / (ytop - ybot) * (B - T)

    # осі
    f.append(line(L, T - 10, L, B, color=INK, sw=1.6))
    f.append(arrow(L, T - 6, L, T - 24, color=INK, sw=1.6))
    f.append(line(L, B, Rx + 14, B, color=INK, sw=1.6))
    f.append(arrow(Rx + 6, B, Rx + 24, B, color=INK, sw=1.6))
    # 0.0001 лежить нижче за ybot = −3.8 — сітку туди не ведемо, бо лінія і підпис
    # вивалилися б за вісь просто на підписи n.
    for e, lab in [(0.1, "0.1"), (0.01, "0.01"), (0.001, "0.001")]:
        y = Y(e)
        f.append(line(L, y, Rx, y, color=LINE, sw=0.7, dash="2,5"))
        f.append(text(L - 10, y + 4, lab, 10, MUTED, "end"))
    for r in [0.0, 0.25, 0.5, 0.75, 1.0]:
        x = X(r)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        f.append(text(x, B + 20, "%.2f" % r, 10.5, MUTED, "middle"))
    # підпис осі — нижче за позначки R; підпис осі y — вище за позначку «0.1»
    f.append(text(Rx + 22, B + 40, "швидкість R (біт/символ)", 11, INK, "end", bold=True))
    f.append(mtext(L - 58, T - 10, ["залишкова", "похибка"], 10.5, INK, "start"))

    # стеля C
    xc = X(0.531)
    f.append(line(xc, T - 6, xc, B, color=INK, sw=2, dash="6,5"))
    f.append(text(xc + 8, T + 6, "стеля C = 0.531", 11, INK, "start", bold=True))

    pts = [(1.0, 0.1), (0.333, 0.028), (0.2, 0.00856),
           (0.143, 0.00273), (0.111, 0.00089), (0.091, 0.00030)]
    f.append(_poly([(X(r), Y(e)) for r, e in pts], NEG, sw=2.0))
    for r, e in pts:
        f.append(circle(X(r), Y(e), 5, fill="#eaf0fd", stroke=NEG, sw=1.9))
    f.append(text(X(1.0), Y(0.1) - 13, "без коду (×1)", 10, INK, "middle", bold=True))
    f.append(text(X(0.333) - 30, Y(0.028) - 1, "×3", 10, INK, "middle", bold=True))
    f.append(text(X(0.2) - 30, Y(0.00856) - 1, "×5", 10, INK, "middle", bold=True))
    f.append(text(X(0.091) - 26, Y(0.00030) + 4, "×11", 10, INK, "middle", bold=True))

    # стрілка «вниз-і-ліворуч»
    f.append(arrow(X(0.86), Y(0.05), X(0.42), Y(0.006), color=MUTED, sw=1.6))
    f.append(text(X(0.66), Y(0.052), "більше повторень:", 10, MUTED, "middle"))
    f.append(text(X(0.66), Y(0.031), "похибка ↓, але й швидкість ↓", 10, MUTED, "middle"))

    # порожній бажаний кут — правий-низ
    # fitbox лише ЗМЕНШУЄ шрифт під ширину рядка, сам НЕ переносить — тож рядки
    # ділимо руками, інакше довгий напис усохне до нечитабельних 7px.
    f.append(fitbox(400, 274, 230, 52,
                    ["бажане: мала похибка на швидкості",
                     "аж до C — повторення не дістає"],
                    size=10.5, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "proj-repetition-trap.svg"), W, Hh, *f)


# ── hist-1. Сорок п'ять років гонитви: відставання від межі Шеннона ───────────
# Ідея, яку проза дає лише списком: усю історію 1948→2001 видно як ОДНУ криву
# спуску до стелі. Числа — з огляду Костелло й Форні (Eb/N0 для Pb ≈ 10⁻⁵).
def fig_gap_to_limit():
    W, Hh = 780, 560
    f = [text(W / 2, 30, "Сорок п'ять років до стелі: Eb/N0, потрібне для похибки ≈ 10⁻⁵", 15, INK,
              "middle", bold=True)]

    L, R = 92, 690
    T, B = 74, 430
    y_hi, y_lo = 10.6, -2.6          # межі осі Eb/N0, дБ
    x_lo, x_hi = 1945, 2006          # межі осі років

    def X(yr):
        return L + (yr - x_lo) / (x_hi - x_lo) * (R - L)

    def Y(db):
        return T + (y_hi - db) / (y_hi - y_lo) * (B - T)

    # поділки по дБ (саме поділки, не наскрізна сітка: наскрізні лінії
    # перетинали б підписи точок — єдині горизонталі тут це дві межі Шеннона)
    for db in range(-2, 11, 2):
        f.append(line(L - 5, Y(db), L, Y(db), color=INK, sw=1.2))
        f.append(text(L - 11, Y(db) + 4, "%d" % db, 10.5, MUTED, "end"))
    f.append(text(L - 62, T - 16, "Eb/N0, дБ", 11, INK, "start", bold=True))

    # осі
    f.append(line(L, T - 6, L, B, color=INK, sw=1.6))
    f.append(line(L, B, R + 12, B, color=INK, sw=1.6))
    for yr in (1950, 1960, 1970, 1980, 1990, 2000):
        f.append(line(X(yr), B, X(yr), B + 5, color=INK, sw=1.2))
        f.append(text(X(yr), B + 20, str(yr), 10.5, MUTED))
    f.append(text(R + 14, B + 22, "рік", 11, INK, "end", bold=True))

    # дві стелі — підписи ЛІВОРУЧ, подалі від лінії спуску (вона йде вниз-праворуч)
    f.append(line(L, Y(0.19), R, Y(0.19), color=FIELD, sw=2.2))
    f.append(text(L + 8, Y(0.19) - 13, "межа Шеннона для двійкових кодів (η = 1): 0.19 дБ",
                  10.5, FIELD, "start", bold=True))
    f.append(line(L, Y(-1.59), R, Y(-1.59), color=MUTED, sw=1.8, dash="7,5"))
    f.append(text(L + 8, Y(-1.59) + 16, "гранична межа Шеннона (η → 0): −1.59 дБ",
                  10.5, MUTED, "start"))

    # Підписи точок — тільки вгору-праворуч або вниз-ліворуч: лінія спуску йде
    # з верхнього-лівого в нижній-правий, тож ці два сектори біля точки вільні.
    # (рік, Eb/N0, підпис, зсув підпису dx, dy, вирівнювання)
    pts = [
        (1948, 9.6, "без кодування", 12, -12, "start"),
        (1950, 6.6, "коди Геммінга (найкраще можливе)", 12, -12, "start"),
        (1954, 5.8, "Рід–Мюллер (32, 6, 16)", 12, -12, "start"),
        (1977, 2.3, "«Вояджер», 1977 (стандарт NASA)", 12, -12, "start"),
        (1993, 0.7, "турбокоди", 12, -12, "start"),
        (2001, 0.23, "нерегулярний LDPC", -12, 20, "end"),
    ]
    # лінія спуску
    path = [(X(yr), Y(db)) for yr, db, _, _, _, _ in pts]
    for i in range(len(path) - 1):
        f.append(line(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1],
                      color="#9aa3af", sw=1.6, dash="4,4"))
    for (yr, db, lab, dx, dy, anc) in pts:
        f.append(circle(X(yr), Y(db), 5.5, fill=POS, stroke=POS, sw=1.5))
        f.append(text(X(yr) + dx, Y(db) + dy, lab, 11, INK, anc, bold=True))

    # підсумкова смуга внизу — короткі рядки, щоб шрифт не зменшувався
    f.append(fitbox(L, B + 48, R - L, 68,
                    "1948: теорема обіцяє код біля стелі — і не каже, де він.\n"
                    "1962: Галлагер друкує відповідь — її не читають тридцять років.\n"
                    "2001: нерегулярний LDPC заходить на 0.0045 дБ від межі.",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "gap-to-limit.svg"), W, Hh, *f)


# ── hist-2. Турбокод: паралельна конкатенація + петля зворотного зв'язку ──────
# Ідея: показати ОБИДВІ половини винаходу — «випадковоподібність» кодера
# (перемішувач + рекурсивність) і петлю декодера, що дала назву.
def fig_turbo_loop():
    W, Hh = 880, 470
    f = [text(W / 2, 30, "Турбокод: кодер робить код випадковоподібним, декодер замикає петлю",
              15, INK, "middle", bold=True)]

    # ── ліва панель: кодер ────────────────────────────────────────────────────
    f.append(rect(28, 52, 396, 384, fill="#fbfcfd", stroke="#d6dbe1", sw=1.4, rx=10))
    f.append(text(226, 76, "КОДЕР  (швидкість 1/3)", 12.5, MUTED, "middle", bold=True))

    f.append(text(52, 130, "u", 16, INK, "middle", bold=True, italic=True))
    f.append(text(52, 148, "інфо-біти", 9.5, MUTED, "middle"))
    f.append(line(66, 125, 96, 125, color=INK, sw=1.6))
    f.append(circle(96, 125, 4, fill=INK, stroke=INK, sw=1))   # вузол розгалуження
    f.append(line(96, 125, 96, 288, color=INK, sw=1.6))

    # 1) систематична гілка
    f.append(arrow(96, 125, 340, 125, color=INK, sw=1.6))
    f.append(text(362, 130, "u", 13, INK, "middle", bold=True, italic=True))
    f.append(text(226, 114, "систематична гілка — біти йдуть як є", 10, MUTED, "middle"))

    # 2) кодер 1
    f.append(arrow(96, 200, 130, 200, color=INK, sw=1.6))
    f.append(fitbox(130, 176, 172, 48, "рекурсивний\nзгортковий кодер 1", size=10.5,
                    fill=FILL, stroke=LINE, color=INK))
    f.append(arrow(302, 200, 340, 200, color=INK, sw=1.6))
    f.append(text(362, 205, "p₁", 13, INK, "middle", bold=True))

    # 3) перемішувач + кодер 2
    f.append(arrow(96, 288, 130, 288, color=INK, sw=1.6))
    f.append(fitbox(130, 266, 96, 44, "перемішувач\nπ", size=10.5,
                    fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(arrow(226, 288, 252, 288, color=INK, sw=1.6))
    f.append(fitbox(252, 264, 100, 48, "кодер 2\n(такий самий)", size=10,
                    fill=FILL, stroke=LINE, color=INK))
    f.append(arrow(352, 288, 372, 288, color=INK, sw=1.6))
    f.append(text(392, 293, "p₂", 13, INK, "middle", bold=True))

    f.append(mtext(226, 356, ["π робить код «схожим на випадковий»:",
                              "другий кодер бачить ті самі біти в іншому порядку —",
                              "комбінація, згубна для одного, для другого розсипана"],
                   10, MUTED, "middle"))
    f.append(text(226, 416, "рекурсивність не дає одній одиниці породити легке слово",
                  10, MUTED, "middle"))

    # ── права панель: декодер ─────────────────────────────────────────────────
    f.append(rect(452, 52, 400, 384, fill="#fbfcfd", stroke="#d6dbe1", sw=1.4, rx=10))
    f.append(text(652, 76, "ДЕКОДЕР  (ітеративний)", 12.5, MUTED, "middle", bold=True))

    f.append(fitbox(486, 116, 132, 50, "BCJR 1\n(м'який → м'який)", size=10,
                    fill=FILL, stroke=LINE, color=INK))
    f.append(fitbox(686, 116, 132, 50, "BCJR 2\n(м'який → м'який)", size=10,
                    fill=FILL, stroke=LINE, color=INK))

    # прямий шлях: BCJR1 → π → BCJR2
    f.append(arrow(618, 141, 640, 141, color=POS, sw=2))
    f.append(fitbox(640, 127, 46, 28, "π", size=12, fill="#eef6ef", stroke=FIELD, color=INK))

    # зворотний шлях: BCJR2 → π⁻¹ → BCJR1
    f.append(line(752, 166, 752, 222, color=POS, sw=2))
    f.append(line(752, 222, 676, 222, color=POS, sw=2))
    f.append(fitbox(608, 208, 68, 28, "π⁻¹", size=12, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(line(608, 222, 552, 222, color=POS, sw=2))
    f.append(arrow(552, 222, 552, 166, color=POS, sw=2))

    f.append(text(652, 250, "петля: вихід → назад на вхід", 11, POS, "middle", bold=True))
    f.append(text(652, 268, "звідси й назва «турбо»", 10, MUTED, "middle"))

    f.append(arrow(752, 116, 752, 96, color=INK, sw=1.6))
    f.append(text(752, 90, "рішення", 10.5, INK, "middle", bold=True))

    f.append(fitbox(478, 292, 348, 64,
                    "Передають ЛИШЕ зовнішню інформацію —\n"
                    "те, що декодер довідався сам, відібравши те,\n"
                    "що йому й так підказали канал і сусід.",
                    size=10.5, fill="#fdecea", stroke=POS, color=INK))
    f.append(mtext(652, 378, ["Без цього віднімання два декодери просто",
                              "повертають одне одному власні ж думки —",
                              "і переконують себе замість того, щоб учитися."],
                   10, MUTED, "middle"))

    render(os.path.join(IMG, "turbo-loop.svg"), W, Hh, *f)


if __name__ == "__main__":
    fig_threshold()
    fig_sphere_packing()
    fig_bsc_budget()
    fig_aep_concentration()
    fig_random_coding()
    fig_fano_floor()
    fig_sim_threshold()
    fig_repetition_trap()
    fig_gap_to_limit()
    fig_turbo_loop()
    print("OK: figures written to", IMG)
