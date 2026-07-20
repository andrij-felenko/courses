# -*- coding: utf-8 -*-
"""Фігури до теми «Двійковий симетричний канал» (binary-symmetric-channel).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def Hbin(p):
    """Двійкова ентропія H(p) у бітах (з коректними межами 0 і 1)."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


# ── 1. Схема переходів BSC: біт проходить (1−p) або перевертається (p) ─────────
# Ідея, яку важко словами: увесь канал — це два входи, два виходи й чотири
# стрілки; симетрія в тому, що обидва перевороти мають ту саму ймовірність p.
def fig_transition():
    W, H = 700, 400
    xin, xout = 175, 525
    y0, y1 = 145, 300          # центри вузлів: біт 0 угорі, біт 1 унизу
    r = 27
    f = []

    # заголовки колонок
    f.append(text(xin, 74, "вхід  X", 13, INK, "middle", bold=True))
    f.append(text(xout, 74, "вихід  Y", 13, INK, "middle", bold=True))

    # ── прямі стрілки (біт проходить), зелені = «ціле» ──
    f.append(arrow(xin + r, y0, xout - r, y0, color=FIELD, sw=2.4))
    f.append(arrow(xin + r, y1, xout - r, y1, color=FIELD, sw=2.4))
    f.append(text(350, 130, "1 − p", 13.5, FIELD, "middle", bold=True))
    f.append(text(350, 322, "1 − p", 13.5, FIELD, "middle", bold=True))

    # ── перехресні стрілки (біт перевертається), червоні = «помилка» ──
    # ребра вузлів під кутом
    def edge(cx, cy, tx, ty):
        dx, dy = tx - cx, ty - cy
        L = math.hypot(dx, dy)
        return cx + r * dx / L, cy + r * dy / L
    ax, ay = edge(xin, y0, xout, y1)
    bx, by = edge(xout, y1, xin, y0)
    f.append(arrow(ax, ay, bx, by, color=POS, sw=2.4))
    cx0, cy0 = edge(xin, y1, xout, y0)
    dx0, dy0 = edge(xout, y0, xin, y1)
    f.append(arrow(cx0, cy0, dx0, dy0, color=POS, sw=2.4))
    # підписи «p» — у широкому просвіті біля лівих вузлів, зі значним відступом
    f.append(text(252, 160, "p", 14, POS, "middle", bold=True))
    f.append(text(252, 285, "p", 14, POS, "middle", bold=True))

    # ── вузли (поверх стрілок) ──
    for (cx, cy, val) in [(xin, y0, "0"), (xin, y1, "1"), (xout, y0, "0"), (xout, y1, "1")]:
        f.append(circle(cx, cy, r, fill=BG, stroke=INK, sw=2))
        f.append(text(cx, cy + 8, val, 22, INK, "middle", bold=True))

    # підсумкова смуга
    f.append(fitbox(70, 356, 560, 30,
                    "перевороти 0→1 і 1→0 однаково ймовірні (обидва p) — завада сліпа до змісту біта",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "transition-diagram.svg"), W, H, *f,
           title="Двійковий симетричний канал: біт проходить або перевертається")


# ── 2. Крива ємності C = 1 − H(p) ─────────────────────────────────────────────
# Ідея: ємність — 1 біт на краях (p=0 і p=1), і рівно нуль при p=0.5; форма
# симетрична, бо канал з p і з 1−p однаково добрий (вихід досить інвертувати).
def fig_capacity():
    W, H = 720, 430
    ox, oy = 95, 348
    aw, ah = 520, 258
    y_top = oy - ah
    f = []

    def X(p):
        return ox + p * aw

    def Y(c):
        return oy - c * ah

    # сітка й підписи осі y
    for c in (0.0, 0.5, 1.0):
        y = Y(c)
        f.append(line(ox, y, ox + aw, y, color="#e3e7ec", sw=1.2))
        f.append(text(ox - 12, y + 4, "%.1f" % c, 11, MUTED, "end"))
    # осі
    f.append(line(ox, y_top - 6, ox, oy + 6, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + aw + 10, oy, color=INK, sw=1.6))
    # підписи осі x
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        f.append(line(X(p), oy, X(p), oy + 6, color=INK, sw=1.3))
        f.append(text(X(p), oy + 22, ("%.2f" % p).rstrip("0").rstrip("."), 11, MUTED, "middle"))
    f.append(text(ox + aw / 2, oy + 44, "p — перехідна ймовірність", 12.5, INK, "middle", bold=True))
    f.append(text(ox - 12, y_top - 14, "C — біт/символ", 12.5, INK, "start", bold=True))

    # вісь симетрії p = ½ (лише в нижній частині, щоб не перетнути центральний напис)
    f.append(line(X(0.5), oy, X(0.5), Y(0.56), color="#c7d0da", sw=1.3, dash="5 5"))

    # крива C = 1 − H(p)
    pts = []
    p = 0.0
    while p <= 1.00001:
        pts.append("%.2f,%.2f" % (X(p), Y(1 - Hbin(p))))
        p += 0.005
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts), NEG))

    # ключові точки
    for (p, c) in [(0.0, 1.0), (0.5, 0.0), (1.0, 1.0)]:
        f.append(circle(X(p), Y(c), 5.5, fill=BG, stroke=NEG, sw=2.4))

    # ── анотації у вільному верхньому центрі (там, де крива низько) ──
    f.append(mtext(X(0.5), Y(0.70), ["C(p) = C(1 − p)", "p і 1−p однаково добрі"],
                   12, INK, anchor="middle"))

    # p = 0 → ідеальний (ліворуч угорі)
    f.append(arrow(X(0.10) + 6, Y(0.86), X(0.012), Y(0.985), color=MUTED, sw=1.4))
    f.append(mtext(X(0.115), Y(0.80), ["ідеальний:", "p=0 → C=1"], 11, MUTED, anchor="start"))

    # p = 1 → теж ідеальний (праворуч угорі)
    f.append(arrow(X(0.90) - 6, Y(0.86), X(0.988), Y(0.985), color=MUTED, sw=1.4))
    f.append(mtext(X(0.885), Y(0.80), ["теж ідеальний:", "вихід інвертувати"], 11, MUTED, anchor="end"))

    # p = 0.5 → мертвий (стрілка вниз до точки на осі)
    f.append(arrow(X(0.66), Y(0.30), X(0.51), Y(0.02), color=POS, sw=1.6))
    f.append(mtext(X(0.665), Y(0.40), ["мертвий канал:", "вихід не залежить", "від входу, C=0"],
                   11, POS, anchor="start"))

    render(os.path.join(IMG, "capacity-curve.svg"), W, H, *f,
           title="Пропускна здатність BSC: C = 1 − H(p)")


# ── 3. Тверде рішення: аналоговий хвіст за порогом стає ймовірністю p ──────────
# Ідея: p — не первинне, а площа хвоста гаусової хмари, що перелазить за поріг
# рішення; симетрія хмар навколо ±1 робить обидва перевороти рівноймовірними.
def fig_hard_decision():
    W, H = 720, 370
    oy = 258
    xL, xR = 245.0, 475.0      # рівні −1 (біт 1) і +1 (біт 0)
    xb = (xL + xR) / 2.0       # поріг
    sig = 56.0
    peak = 150.0
    f = []

    def by(x, xc):
        return oy - peak * math.exp(-((x - xc) / sig) ** 2 / 2.0)

    # вісь
    f.append(line(70, oy, 668, oy, color=INK, sw=1.6))
    f.append(arrow(654, oy, 672, oy, color=INK, sw=1.6))
    f.append(text(664, oy + 24, "прийнята напруга", 11, INK, "end", bold=True))

    # заштриховані хвости за порогом (площа = p)
    def tail(x_a, x_b, xc):
        p = []
        x = x_a
        while x <= x_b:
            p.append("%.1f,%.1f" % (x, by(x, xc)))
            x += 2.5
        p.append("%.1f,%.1f" % (x_b, oy))
        p.append("%.1f,%.1f" % (x_a, oy))
        return ('<polygon points="%s" fill="%s" fill-opacity="0.34" stroke="none"/>'
                % (" ".join(p), POS))
    f.append(tail(xb, xb + 88, xL))    # хвіст лівої хмари праворуч за поріг
    f.append(tail(xb - 88, xb, xR))    # хвіст правої хмари ліворуч за поріг

    # дзвони
    for xc, col in [(xL, POS), (xR, NEG)]:
        pts = []
        x = xc - 3.1 * sig
        while x <= xc + 3.1 * sig:
            pts.append("%.1f,%.1f" % (x, by(x, xc)))
            x += 2.5
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))

    # позначки рівнів на осі
    f.append(circle(xL, oy, 5, fill=POS, stroke=POS, sw=0))
    f.append(circle(xR, oy, 5, fill=NEG, stroke=NEG, sw=0))
    f.append(mtext(xL, oy + 24, ["рівень −1", "(біт 1)"], 11.5, POS, anchor="middle", bold=True))
    f.append(mtext(xR, oy + 24, ["рівень +1", "(біт 0)"], 11.5, NEG, anchor="middle", bold=True))

    # поріг
    f.append(line(xb, oy + 8, xb, 84, color=INK, sw=1.6, dash="5 4"))
    f.append(text(xb, 76, "поріг", 12, INK, "middle", bold=True))

    # виноска на хвіст
    f.append(arrow(xb + 150, 150, xb + 34, by(xb + 30, xL) - 4, color=POS, sw=1.7))
    f.append(mtext(xb + 150, 126, ["площа хвоста за порогом", "= перехідна ймовірність p"],
                   11, POS, anchor="middle"))

    render(os.path.join(IMG, "hard-decision.svg"), W, H, *f,
           title="Звідки береться p: тверде рішення на порозі")


# ── 4. Декодування = найближче кодове слово за Геммінгом ───────────────────────
# Ідея: на симетричному каналі найправдоподібніше передане слово — те, що
# найближче до прийнятого за відстанню Геммінга (числом розбіжних бітів).
def fig_ml_hamming():
    W, H = 760, 410
    f = []

    def word(cx, cy, bits, diffs, size=21):
        n = len(bits)
        step = 23
        x0 = cx - (n - 1) * step / 2.0
        out = []
        for i, b in enumerate(bits):
            col = POS if i in diffs else INK
            out.append(text(x0 + i * step, cy + 7, b, size, col, "middle", bold=True))
        return "".join(out)

    def wbox(cx, cy, bits, diffs, chosen=False):
        w, h = 156, 52
        st = FIELD if chosen else "#c7d0da"
        fl = "#eef6ef" if chosen else BG
        return (rect(cx - w / 2, cy - h / 2, w, h, fill=fl, stroke=st,
                     sw=2.4 if chosen else 1.6, rx=8) + word(cx, cy, bits, diffs))

    # прийняте слово — центр
    C0 = (380, 212)
    # кандидати
    A = (380, 84)     # d=1, обрано
    Cc = (168, 330)   # d=2
    Bb = (600, 330)   # d=3

    # з'єднувальні лінії (від країв рамок)
    f.append(line(C0[0], C0[1] - 26, A[0], A[1] + 26, color=FIELD, sw=2.2))
    f.append(text(A[0] + 22, (C0[1] + A[1]) / 2 + 4, "d = 1", 12.5, FIELD, "start", bold=True))

    f.append(line(C0[0] - 60, C0[1] + 22, Cc[0] + 55, Cc[1] - 24, color=MUTED, sw=1.6))
    f.append(text(232, 276, "d = 2", 12, MUTED, "middle", bold=True))

    f.append(line(C0[0] + 60, C0[1] + 22, Bb[0] - 55, Bb[1] - 24, color=MUTED, sw=1.6))
    f.append(text(516, 266, "d = 3", 12, MUTED, "middle", bold=True))

    # рамки-слова
    f.append(wbox(*C0, bits="10110", diffs=()))
    f.append(text(C0[0], C0[1] + 44, "прийняте  Y", 11.5, INK, "middle", bold=True))

    f.append(wbox(*A, bits="10010", diffs={2}, chosen=True))
    f.append(text(A[0] + 92, A[1], "← найближче", 12, FIELD, "start", bold=True))

    f.append(wbox(*Cc, bits="11111", diffs={1, 4}))
    f.append(wbox(*Bb, bits="00011", diffs={0, 2, 4}))

    # підсумок
    f.append(fitbox(96, 372, 568, 30,
                    "червоні цифри — розбіжні біти; декодер обирає слово з найменшою відстанню (тут d=1)",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "ml-hamming.svg"), W, H, *f,
           title="Декодування: найближче кодове слово за Геммінгом")


# ── 5. Розклад I = H(Y) − H(Y|X): шум фіксований, вхід максимізує H(Y) ─────────
# Ідея (для вставки math-capacity-derivation): взаємна інформація — це вихідна
# ентропія H(Y) мінус шумовий податок H(Y|X)=H(p). Податок той самий за будь-якого
# входу (синій сегмент однаковий), тож найбільше I дає той вхід, що робить H(Y)
# найбільшою — рівноймовірний (H(Y)=1). Тоді I = 1 − H(p) = C.
def fig_decomposition():
    W, H = 830, 452
    f = []
    x0 = 210
    sc = 470.0                 # 1 біт → 470 px
    bh = 54
    p = 0.1
    hp = Hbin(p)               # шум H(p) = 0.469
    HYa, Ia = 1.0, 1.0 - hp    # рівноймовірний вхід
    HYb = Hbin(0.3)            # перекошений (¼,¾) → P(Y=1)=0.7 → H(Y)=H(0.3)=0.881
    Ib = HYb - hp
    yA, yB = 92, 246
    xn = x0 + hp * sc          # спільна межа шуму (однакова для обох!)
    xceil = x0 + sc            # стеля 1 біт

    def barrow(y, HY, I, lab, sub):
        xend = x0 + HY * sc
        o = []
        # пунктирна стеля — уся одиниця
        o.append(rect(x0, y, sc, bh, fill="none", stroke=MUTED, sw=1.3, rx=6))
        # шумовий сегмент
        o.append(rect(x0, y, hp * sc, bh, fill="#eaf0fd", stroke=NEG, sw=1.9, rx=6))
        o.append(text((x0 + xn) / 2, y + bh / 2 + 5, "шум H(p)=%.3f" % hp, 12, NEG, "middle", bold=True))
        # наскрізний сегмент
        o.append(rect(xn, y, (HY - hp) * sc, bh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=6))
        o.append(text((xn + xend) / 2, y + bh / 2 + 5, "I=%.3f" % I, 12, FIELD, "middle", bold=True))
        # мітка рядка ліворуч
        o.append(text(x0 - 18, y + bh / 2 - 4, lab, 12.5, INK, "end", bold=True))
        o.append(text(x0 - 18, y + bh / 2 + 14, sub, 10.5, MUTED, "end"))
        # H(Y) над правим кінцем бару
        o.append(text(xend, y - 9, "H(Y)=%.3f" % HY, 11.5, INK, "middle", bold=True))
        return "".join(o)

    f.append(barrow(yA, HYa, Ia, "рівноймовірний вхід", "P(0)=P(1)=½"))
    f.append(barrow(yB, HYb, Ib, "перекошений вхід", "P(0)=¼, P(1)=¾"))

    # стеля-підпис
    f.append(text(xceil, yA - 30, "стеля: H(Y) ≤ 1 біт", 11, MUTED, "middle"))
    # недобір у перекошеного (порожній хвіст пунктирної стелі)
    f.append(arrow(xceil + 8, yB + bh / 2, x0 + HYb * sc + 6, yB + bh / 2, color=POS, sw=1.5))
    f.append(text(xceil + 14, yB + bh / 2 - 12, "недобір:", 10.5, POS, "start", bold=True))
    f.append(text(xceil + 14, yB + bh / 2 + 4, "H(Y)<1 →", 10.5, POS, "start", bold=True))
    f.append(text(xceil + 14, yB + bh / 2 + 20, "менше I", 10.5, POS, "start", bold=True))

    # спільна межа шуму — вертикаль крізь обидва бари
    f.append(line(xn, yA - 20, xn, yB + bh + 26, color=NEG, sw=1.3, dash="4 4"))
    f.append(text(xn, yB + bh + 44, "синій сегмент однаковий: шум H(p) не залежить від розподілу входу",
                  11, NEG, "middle"))

    # підсумкова рамка
    f.append(fitbox(150, yB + bh + 62, W - 300, 34,
                    "рівноймовірний вхід дає повну стелю H(Y)=1  →  найбільше I = 1 − H(p) = C",
                    size=12, fill="#eef6ef", stroke=FIELD, color=INK, bold=True))
    render(os.path.join(IMG, "mi-decomposition.svg"), W, H, *f,
           title="I(X;Y) = H(Y) − H(Y|X): шум фіксований, максимізуємо H(Y)")


# ── 6. Чому p=½ вбиває канал: шум H(p) з'їдає всю одиницю ──────────────────────
# Ідея (для вставки math-capacity-derivation): при рівноймовірному вході H(Y)=1
# завжди; що ближче p до ½, то більший шумовий податок H(p), і при p=½ він
# заповнює всю одиницю — на корисне не лишається нічого, C=0.
def fig_noise_fills():
    W, H = 820, 372
    f = []
    x0 = 190
    sc = 452.0
    bh = 46
    xceil = x0 + sc
    rows = [(0.1, 96), (0.3, 178), (0.5, 260)]

    # стеля 1 біт — спільна вертикаль
    f.append(line(xceil, 70, xceil, 300, color=MUTED, sw=1.3, dash="5 4"))
    f.append(text(xceil + 6, 66, "1 біт (стеля H(Y))", 10.5, MUTED, "start"))

    for p, y in rows:
        hp = Hbin(p)
        C = 1.0 - hp
        xn = x0 + hp * sc
        # пунктирна стеля
        f.append(rect(x0, y, sc, bh, fill="none", stroke=MUTED, sw=1.2, rx=6))
        # шум
        f.append(rect(x0, y, hp * sc, bh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
        f.append(text(x0 + hp * sc / 2, y + bh / 2 + 5, "H(p)=%.3f" % hp, 11.5, NEG, "middle", bold=True))
        # наскрізний сегмент (корисне C)
        if C > 0.006:
            f.append(rect(xn, y, C * sc, bh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
        # мітка рядка ліворуч
        f.append(text(x0 - 18, y + bh / 2 + 5, "p = %.1f" % p, 13, INK, "end", bold=True))
        # значення C — над наскрізним сегментом (або праворуч, коли його нема)
        if C > 0.03:
            f.append(text(xn + C * sc / 2, y - 8, "C=%.3f" % C, 11.5, FIELD, "middle", bold=True))
        else:
            f.append(text(xceil + 14, y + bh / 2 + 5, "C = 0", 13, POS, "start", bold=True))

    render(os.path.join(IMG, "noise-fills-unit.svg"), W, H, *f,
           title="Що ближче p до ½, то більше H(p) — при p=½ шум заповнює всю одиницю")


# ── 7. Конвеєр симуляції: як влаштована вимірювальна оснастка ──────────────────
# Ідея (для вставки proj-bsc-simulation), яку важко словами: увесь код-проєкт —
# це коротка стрічка (біт → кодер → канал → декодер → лічильник), обгорнута в
# цикл на N прогонів; наприкінці ділимо помилки на N.
def fig_sim_pipeline():
    W, H = 860, 340
    cy = 150
    gap = 52
    pad = 11
    size = 13.5
    f = []

    stages = [
        (["джерело", "біт b"], BG, INK),
        (["кодер", "повтор ×3"], "#eef6ef", FIELD),
        (["канал", "BSC(p)"], "#fdecea", POS),
        (["декодер", "більшість"], "#eef6ef", FIELD),
        (["лічильник", "b̂ ≠ b ?"], BG, INK),
    ]

    def box_w(lines):
        tw = max(text_width(ln, size, True) for ln in lines)
        return tw + 2 * pad

    widths = [box_w(l) for (l, _, _) in stages]
    total = sum(widths) + gap * (len(stages) - 1)
    x = (W - total) / 2.0
    centers = []
    for w in widths:
        centers.append(x + w / 2.0)
        x += w + gap

    # стрілки + підписи-трійки над просвітами
    labels = ["", "b b b", "r r r", "b̂", ""]
    lab_col = [INK, FIELD, POS, INK, INK]
    for i in range(len(stages) - 1):
        x1 = centers[i] + widths[i] / 2.0
        x2 = centers[i + 1] - widths[i + 1] / 2.0
        f.append(arrow(x1 + 3, cy, x2 - 3, cy, color=MUTED, sw=1.8))
        mid = (x1 + x2) / 2.0
        if labels[i + 1]:
            f.append(text(mid, cy - 16, labels[i + 1], 13, lab_col[i + 1], "middle", bold=True))

    # самі рамки-стадії
    for (lines, fill, stroke), w, cx in zip(stages, widths, centers):
        body, bw, bh = textbox(cx, cy, lines, size=size, pad=pad,
                               fill=fill, stroke=stroke, sw=2, color=INK, bold=True)
        f.append(body)

    # петля «× N прогонів» — дуга від лічильника назад до джерела
    xL = centers[0]
    xR = centers[-1]
    yb = cy + 62
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6 5" '
             'marker-end="url(#arrow)"/>'
             % (xR, cy + 34, xR, yb + 26, xL, yb + 26, xL, cy + 34, MUTED))
    f.append(text((xL + xR) / 2.0, yb + 30, "повторити N разів", 13, MUTED, "middle", bold=True))

    # підсумковий оцінювач
    f.append(fitbox(W / 2 - 200, 292, 400, 34,
                    "p̂ = (кількість помилок) ∕ N   →   порівняти з 3p² − 2p³",
                    size=13, fill=FILL, stroke=LINE, color=INK, bold=True))

    render(os.path.join(IMG, "sim-pipeline.svg"), W, H, *f,
           title="Конвеєр симуляції: біт → кодер → канал → декодер → лічильник")


# ── 8. Збіжність оцінки Монте-Карло й пастка малого p ──────────────────────────
# Ідея (для вставки proj-bsc-simulation): при малому p оцінка довго тримається на
# нулі (жодної помилки — брехлива «ідеальність»), і лише коли N·P_пом переростає
# одиниці, сідає на теорію; смуга ±1.96σ звужується як 1∕√N.
def fig_mc_convergence():
    W, H = 780, 430
    ox, oy = 96, 350
    aw, ah = 560, 258
    ytop = oy - ah
    theory = 3 * 0.01 ** 2 - 2 * 0.01 ** 3   # ≈ 2.98e-4
    ymax = 6.5e-4
    xlo, xhi = 1.4, 6.72                       # log10(N): ~25 … ~5.2e6
    f = []

    def X(N):
        return ox + (math.log10(N) - xlo) / (xhi - xlo) * aw

    def Y(v):
        return oy - min(v, ymax) / ymax * ah

    # сітка/осі y
    for v in (0.0, 2e-4, 4e-4, 6e-4):
        y = Y(v)
        f.append(line(ox, y, ox + aw, y, color="#e3e7ec", sw=1.1))
        f.append(text(ox - 10, y + 4, ("%g·10⁻⁴" % (v * 1e4)) if v else "0", 10.5, MUTED, "end"))
    f.append(line(ox, ytop - 6, ox, oy + 6, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + aw + 8, oy, color=INK, sw=1.6))
    # осі x (декади N)
    for e in (2, 3, 4, 5, 6):
        xv = X(10 ** e)
        f.append(line(xv, oy, xv, oy + 6, color=INK, sw=1.3))
        f.append(text(xv, oy + 22, "10" + "²³⁴⁵⁶"[e - 2], 12, MUTED, "middle"))
    f.append(text(ox + aw / 2, oy + 44, "N — кількість прогонів (лог-шкала)", 12.5, INK, "middle", bold=True))
    f.append(text(ox - 8, ytop - 14, "виміряна p̂", 12.5, INK, "start", bold=True))

    # смуга ±1.96σ навколо теорії (звужується як 1∕√N)
    up, lo = [], []
    e = xlo
    while e <= xhi + 1e-9:
        N = 10 ** e
        sig = math.sqrt(theory * (1 - theory) / N)
        up.append("%.2f,%.2f" % (X(N), Y(theory + 1.96 * sig)))
        lo.append("%.2f,%.2f" % (X(N), Y(max(0.0, theory - 1.96 * sig))))
        e += 0.12
    f.append('<polygon points="%s %s" fill="%s" fill-opacity="0.13" stroke="none"/>'
             % (" ".join(up), " ".join(reversed(lo)), NEG))

    # лінія теорії
    yt = Y(theory)
    f.append(line(ox, yt, ox + aw, yt, color=FIELD, sw=2.2, dash="7 5"))
    f.append(text(ox + aw - 4, yt - 8, "теорія 3p² − 2p³ = 2.98·10⁻⁴", 11.5, FIELD, "end", bold=True))

    # межа правдоподібного нуля: N ≈ 1.96²∕P (нижче смуга торкається 0)
    Nz = 1.96 ** 2 / theory
    f.append(line(X(Nz), Y(ymax) + 4, X(Nz), oy, color=MUTED, sw=1.3, dash="3 4"))
    f.append(mtext(X(Nz) - 8, ytop + 26, ["ліворуч 0 помилок", "ще правдоподібний"],
                   10.5, MUTED, anchor="end"))

    # реальна траса p̂ (seed=1, p=0.01): довго на нулі, тоді сідає на теорію
    trace = [(30, 0.0), (100, 0.0), (300, 0.0), (1000, 0.0), (3000, 0.0),
             (10000, 1.0e-4), (30000, 3.333e-5), (100000, 1.70e-4),
             (300000, 2.933e-4), (1000000, 2.95e-4), (3000000, 2.963e-4),
             (5000000, 2.908e-4)]
    pts = ["%.2f,%.2f" % (X(N), Y(v)) for (N, v) in trace]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), INK))
    for (N, v) in trace:
        col = POS if v == 0.0 else INK
        f.append(circle(X(N), Y(v), 4, fill=col, stroke=col, sw=0))
    # виноска на плаский нуль
    f.append(mtext(X(220), Y(0.0) - 52, ["0 помилок →", "p̂ = 0 (брехлива", "«ідеальність»)"],
                   11, POS, anchor="middle", bold=True))
    f.append(arrow(X(400), Y(0.0) - 10, X(1200), Y(0.0) - 2, color=POS, sw=1.5))

    render(os.path.join(IMG, "mc-convergence.svg"), W, H, *f,
           title="Збіжність Монте-Карло: чому при малому p потрібні мільйони прогонів")


if __name__ == "__main__":
    fig_transition()
    fig_capacity()
    fig_hard_decision()
    fig_ml_hamming()
    fig_decomposition()
    fig_noise_fills()
    fig_sim_pipeline()
    fig_mc_convergence()
    print("OK: figures written to", IMG)
