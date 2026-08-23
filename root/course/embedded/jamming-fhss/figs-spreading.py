# -*- coding: utf-8 -*-
"""Фігури до вставки «Як будують коди розширення» (math-spreading-codes.md).
Запуск:  python figs-spreading.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Модель LFSR: обчислимо реальну m-послідовність на 4 розряди ────────────────
def lfsr_seq(n, taps, seed=1):
    """n-розрядний LFSR Фібоначчі (стандартна умова, дає СПРАВЖНЮ m-послідовність):
    зсув УЛІВО, новий біт (XOR відводів) заходить у молодший розряд, вихід — старший.
    taps — індекси розрядів (1..n), що йдуть у XOR (мусять бути примітивним поліномом).
    Повертає (стани, вихідні_біти) за один повний період 2ⁿ−1.
    Перевірено чисельно: для (3,4)@n4 і (3,5)@n5 автокореляція = рівно {N, −1}."""
    reg = seed
    states, out = [], []
    period = (1 << n) - 1
    mask = period
    for _ in range(period):
        states.append(reg)
        out.append((reg >> (n - 1)) & 1)    # старший розряд — вихід
        fb = 0
        for t in taps:
            fb ^= (reg >> (t - 1)) & 1
        reg = ((reg << 1) | fb) & mask       # зсув улево, XOR у молодший
    return states, out


# ── 1. Механіка LFSR: зсув + XOR-зворотний зв'язок породжують довгу нитку ──────
# Ідея, яку важко сказати словами: маленький регістр із XOR у зворотному
# зв'язку прокручує майже всі свої стани по колу, перш ніж повторитися.
def fig_lfsr():
    W, H = 720, 440
    n = 4
    taps = (3, 4)                            # x⁴ + x³ + 1 — примітивний → період 15, автокор {15,−1}
    states, out = lfsr_seq(n, taps)

    f = []
    f.append(text(W / 2, 28, "LFSR на 4 розряди: зсув уліво + XOR-зворотний зв'язок породжують довгу нитку", 14.5, INK, "middle", bold=True))

    # ── регістр: чотири комірки, зліва старший розряд b3 (вихід), справа b0 (вхід) ──
    cw, ch = 62, 58
    gap = 16
    total = 4 * cw + 3 * gap
    x0 = (W - total) / 2 + 24
    y0 = 74
    reg0 = states[0]
    bits = [(reg0 >> (n - 1 - i)) & 1 for i in range(n)]   # зліва старший b3..b0 праворуч
    labels = ["b3", "b2", "b1", "b0"]
    cx = []
    for i in range(4):
        x = x0 + i * (cw + gap)
        cx.append(x + cw / 2)
        fill = "#eef6ef" if bits[i] else FILL
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=LINE, sw=1.8))
        f.append(text(x + cw / 2, y0 + ch / 2 + 9, str(bits[i]), 26, INK, "middle", bold=True))
        f.append(text(x + cw / 2, y0 - 8, labels[i], 12, MUTED, "middle"))

    # стрілки зсуву між комірками — управо-в-ліворуч (дані течуть до b3)
    for i in range(3):
        xr = x0 + (i + 1) * (cw + gap) - gap    # правий край сусіда
        xl = x0 + (i + 1) * (cw + gap)          # лівий край наступного
        f.append(arrow(xl - 1, y0 + ch / 2, xr + 1, y0 + ch / 2, color=NEG, sw=2))

    # вихід ліворуч зі старшого розряду b3
    xL = x0
    f.append(arrow(xL - 8, y0 + ch / 2, xL - 52, y0 + ch / 2, color=FIELD, sw=2.4))
    f.append(text(xL - 94, y0 + ch / 2 - 6, "вихід", 12.5, FIELD, "middle", bold=True))
    f.append(text(xL - 94, y0 + ch / 2 + 10, "(старший)", 10.5, FIELD, "middle"))

    # ── XOR-вузол праворуч, зворотний зв'язок від відводів b3, b2 у молодший b0 ──
    xR = x0 + 4 * (cw + gap) - gap              # правий край регістра
    xor_x, xor_y = xR + 72, y0 + ch + 86
    f.append(circle(xor_x, xor_y, 18, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(xor_x, xor_y + 6, "XOR", 11, POS, "middle", bold=True))

    # лінії від відводів (b3 = індекс 0, b2 = індекс 1) вниз і праворуч у XOR
    for idx in (0, 1):
        tx = cx[idx]
        f.append(line(tx, y0 + ch, tx, xor_y, color=POS, sw=1.8, dash="5 4"))
        f.append(line(tx, xor_y, xor_x - 18, xor_y, color=POS, sw=1.8, dash="5 4"))
        f.append(circle(tx, y0 + ch, 3.4, fill=POS, stroke=POS, sw=1))
    f.append(text(xor_x, xor_y + 30, "відводи: b3 ⊕ b2", 12, POS, "middle", bold=True))

    # від XOR назад у молодший розряд b0 (праворуч-угору, вхід справа)
    f.append(line(xor_x, xor_y - 18, xor_x, y0 + ch / 2, color=FIELD, sw=2))
    f.append(arrow(xor_x, y0 + ch / 2, cx[3] + cw / 2 + 8, y0 + ch / 2, color=FIELD, sw=2))
    f.append(text(xor_x + 8, y0 + 6, "новий", 11, FIELD, "start"))
    f.append(text(xor_x + 8, y0 + 20, "молодший", 11, FIELD, "start"))

    # ── стрічка вихідних бітів за повний період (15 кроків) ──────────────────
    by = y0 + ch + 168
    bw = 34
    bx0 = (W - 15 * bw) / 2
    f.append(text(W / 2, by - 16, "вихідні біти за повний період — 2⁴−1 = 15 кроків, тоді точний повтор", 12.5, MUTED, "middle"))
    for i, b in enumerate(out):
        x = bx0 + i * bw
        fill = "#eef6ef" if b else "#ffffff"
        f.append(rect(x, by, bw - 4, 30, fill=fill, stroke=LINE, sw=1.3, rx=4))
        f.append(text(x + (bw - 4) / 2, by + 21, str(b), 15, INK, "middle", bold=True))
    f.append(text(bx0 + 15 * bw + 6, by + 21, "↻", 20, POS, "start", bold=True))

    # підрахунок одиниць/нулів — рівно на одну одиницю більше (баланс ±1)
    ones = sum(out)
    f.append(text(W / 2, by + 58,
                  "одиниць: %d, нулів: %d  —  рівно на одну одиницю більше (майже ідеальний баланс ±1)" % (ones, 15 - ones),
                  12, MUTED, "middle"))

    render(os.path.join(IMG, "s-lfsr.svg"), W, H, *f)


# ── 2. Автокореляція m-послідовності: «кнопка» — пік N, скрізь інакше −1 ───────
# Ідея: посунь код сам відносно себе на будь-яку ненульову кількість чипів —
# збіг миттєво падає з N до рівно −1. Це і є «гострий пік», на якому все тримається.
def fig_autocorr():
    W, H = 720, 400
    n = 5
    taps = (3, 5)                            # x⁵ + x³ + 1 — примітивний → період 31, автокор {31,−1}
    _, out = lfsr_seq(n, taps)
    N = len(out)                             # 31
    seq = [1 if b else -1 for b in out]      # ±1

    # циклічна автокореляція R[k] = Σ seq[i]·seq[i+k]
    R = []
    for k in range(N):
        s = sum(seq[i] * seq[(i + k) % N] for i in range(N))
        R.append(s)

    ox, oy = 70, 300
    aw, ah = 580, 210
    f = []
    f.append(text(W / 2, 28, "Автокореляція m-послідовності (N = 31): пік N у нулі, рівно −1 усюди інакше", 14.5, INK, "middle", bold=True))

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.3))
    f.append(arrow(ox + aw, oy, ox + aw + 16, oy, color=MUTED, sw=1.3))
    f.append(text(ox + aw + 20, oy + 4, "зсув k", 12, MUTED, "start"))
    # нульова лінія трохи вище низу (щоб −1 було видно як провал)
    zero = oy - 40
    f.append(line(ox, zero, ox + aw, zero, color=MUTED, sw=1.1, dash="4 4"))
    f.append(text(ox - 8, zero + 4, "0", 11, MUTED, "end"))

    def bx(k):  return ox + (k / (N - 1)) * aw
    def by(v):  return zero - (v / N) * (ah - 30)   # масштаб: пік N займає майже всю висоту

    # мітка піку N
    f.append(line(ox, by(N), ox + aw, by(N), color=MUTED, sw=1, dash="2 4"))
    f.append(text(ox - 8, by(N) + 4, "N=31", 11, FIELD, "end"))
    f.append(text(ox - 8, by(-1) + 4, "−1", 11, POS, "end"))

    bw = aw / N * 0.55
    for k in range(N):
        x = bx(k)
        v = R[k]
        if v > 1:                            # головний пік
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#eef6ef" stroke="%s" stroke-width="2"/>'
                     % (x - bw / 2, by(v), bw, zero - by(v), FIELD))
        else:                                # бічний рівень −1 (провал під нуль)
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
                     % (x - bw / 2, zero, bw, by(v) - zero, POS))

    # пояснювальні виноски
    tb, tw, th = textbox(bx(0) + 96, by(N) + 20, "суміщено:\nкожен добуток +1\nсума = +N", 11.5, pad=8,
                         fill="#eef6ef", stroke=FIELD, color=FIELD)
    f.append(tb)
    tb2, _, _ = textbox(bx(N * 0.62), zero + 70, "зсунуто хоч на 1 чип:\nплюси/мінуси майже гасяться\nсума = рівно −1", 11.5, pad=8,
                        fill="#fdecea", stroke=POS, color=POS)
    f.append(tb2)

    render(os.path.join(IMG, "s-autocorr.svg"), W, H, *f)


# ── 3. Чому Ґолд: дві m-послідовності лаються, коди Ґолда — ні ─────────────────
# Ідея: у сирих m-послідовностей крос-кореляція має високі гострі піки —
# кілька передавачів заважають одне одному; Ґолд тримає її в трьох малих рівнях.
def fig_gold():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 28, "Крос-кореляція: сирі m-послідовності проти кодів Ґолда (N = 31)", 15, INK, "middle", bold=True))

    n = 5
    # ПЕРЕВІРЕНА чисельно ПЕРЕВАЖНА ПАРА (preferred pair) для n=5:
    #   A: x⁵+x²+1        (відводи 2,5)
    #   B: x⁵+x³+x²+x+1   (відводи 1,2,3,5)
    # їхня крос-кореляція — рівно три значення {−9, −1, 7} = {−t, −1, t−2}, t=9.
    _, a = lfsr_seq(n, (2, 5))
    _, b = lfsr_seq(n, (1, 2, 3, 5))
    N = len(a)
    A = [1 if x else -1 for x in a]
    B = [1 if x else -1 for x in b]

    def xcorr(u, v):
        return [sum(u[i] * v[(i + k) % N] for i in range(N)) for k in range(N)]

    t = 2 ** ((n + 2) // 2) + 1              # = 9 для n=5

    # Ліва панель — крос-кореляція A з РАНДОМНО ЗСУНУТИМ B (не переважна пара для ока):
    # беремо просту крос двох сирих m-послідовностей — вона стрибає без гарантії.
    Cab = xcorr(A, B)                        # тут вона якраз три-значна, бо пара переважна;
    # щоб показати «погану» сиру пару, зсунемо B у геть інший фазовий стан і складемо
    # з ТРЕТЬОЮ m-послідовністю — так видно, що без переважної пари піки вищі.
    _, c = lfsr_seq(n, (3, 5))              # x⁵+x³+1 — ще одна m-послідовність
    C3 = [1 if x else -1 for x in c]
    Cbad = xcorr(A, C3)                      # сира пара БЕЗ гарантії Ґолда

    # Ґолд-коди: родина = A ⊕ (циклічний зсув B); беремо два її члени
    def gold(shift):
        return [A[i] * B[(i + shift) % N] for i in range(N)]   # ±1-добуток = XOR у ±1-світі
    Cgold = xcorr(gold(0), gold(11))

    peak = max(max(abs(v) for v in Cbad), t)     # спільний масштаб для обох панелей
    pw, ph = 300, 250
    py0 = 70

    def draw_panel(px0, title, Cvals, color, note, show_bound):
        ax = px0 + 20
        aw2 = pw - 40
        zero = py0 + ph / 2 + 20
        scale = (ph / 2 - 26) / peak
        frag = [rect(px0, py0, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2),
                text(px0 + pw / 2, py0 + 20, title, 12.5, INK, "middle", bold=True),
                line(ax, zero, ax + aw2, zero, color=MUTED, sw=1, dash="3 4"),
                text(ax - 4, zero + 4, "0", 10, MUTED, "end")]
        if show_bound:                           # межа ±t навколо нуля
            for s in (+t, -t):
                yb = zero - s * scale
                frag.append(line(ax, yb, ax + aw2, yb, color=FIELD, sw=1.2, dash="2 4"))
            frag.append(text(ax + aw2 + 2, zero - t * scale + 4, "+t", 11, FIELD, "start"))
            frag.append(text(ax + aw2 + 2, zero + t * scale + 4, "−t", 11, FIELD, "start"))
        for k in range(N):
            x = ax + (k / (N - 1)) * aw2
            frag.append(line(x, zero, x, zero - Cvals[k] * scale, color=color, sw=2.4))
        tb, _, _ = textbox(px0 + pw / 2, py0 + ph + 26, note, 11, pad=7,
                           fill=("#eef6ef" if show_bound else "#fdecea"),
                           stroke=(FIELD if show_bound else POS),
                           color=(FIELD if show_bound else POS))
        frag.append(tb)
        return frag

    f += draw_panel(40, "сира пара m-послідовностей", Cbad, POS,
                    "піки скачуть до ±%d —\nчужий код лізе в наш" % max(abs(v) for v in Cbad), False)
    f += draw_panel(W - 40 - pw, "коди Ґолда (переважна пара)", Cgold, NEG,
                    "усе в межах ±t = %d —\nчужий тихий, CDMA працює" % t, True)

    render(os.path.join(IMG, "s-gold.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lfsr()
    fig_autocorr()
    fig_gold()
    print("OK: s-lfsr.svg, s-autocorr.svg, s-gold.svg")
