# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Базова стаття (arithmetic-coding.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── narrowing: уся послідовність → один інтервал ──────────────────────────────
# Ідея: один відрізок [0,1) звужується символ за символом; підсумкове число
# всередині останнього інтервалу = код усієї послідовності.

def fig_narrowing():
    W, H = 720, 320
    p = []
    # моделюємо: A=0.6, B=0.3, C=0.1; кодуємо "A B"
    x0, x1 = 90, 630
    full = x1 - x0

    def bar(y, lo, hi, label, probs, hi_idx=None):
        # відрізок [lo,hi) у координатах [0,1); ділимо на A/B/C пропорційно
        bx0 = x0 + lo * full
        bw = (hi - lo) * full
        names = ["A", "B", "C"]
        cols = ["#eef4ff", "#eafaf0", "#fdf6e3"]
        edge = [NEG, FIELD, "#d98a00"]
        acc = 0.0
        for i, pr in enumerate(probs):
            sx = bx0 + acc * bw
            sw_ = pr * bw
            sel = (hi_idx == i)
            p.append(rect(sx, y, sw_, 34, fill=cols[i] if not sel else "#fdecea",
                          stroke=edge[i] if not sel else POS, sw=2.4 if sel else 1.2))
            if sw_ > 22:
                p.append(text(sx + sw_ / 2, y + 22, names[i], size=12,
                              color=(POS if sel else edge[i]), bold=True))
            acc += pr
        p.append(text(x0 - 12, y + 22, label, size=11, color=INK, anchor="end", bold=True))

    probs = [0.6, 0.3, 0.1]
    # рядок 1: повний [0,1), підсвічуємо A
    bar(70, 0.0, 1.0, "[0, 1)", probs, hi_idx=0)
    p.append(text(x0, 58, "0", size=10, color=MUTED, anchor="middle"))
    p.append(text(x1, 58, "1", size=10, color=MUTED, anchor="middle"))
    p.append(text(W / 2, 130, "символ «A» → лишаємо лише його підвідрізок", size=11,
                  color=POS, italic=True))

    # рядок 2: [0,0.6), підсвічуємо B усередині
    bar(150, 0.0, 0.6, "[0, 0.6)", probs, hi_idx=1)
    p.append(text(W / 2, 210, "символ «B» → знову лишаємо його частку, уже всередині", size=11,
                  color=POS, italic=True))

    # рядок 3: підсумковий вузький інтервал [0.36,0.54) — будь-яке число тут = код
    bar(230, 0.36, 0.54, "[.36,.54)", probs)
    cxnum = x0 + 0.45 * full
    p.append(circle(cxnum, 247, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(cxnum, 284, "0.45 — будь-яке число тут кодує «A B»",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "narrowing.svg"), W, H, *p,
           title="Уся послідовність — один інтервал, що звужується")


# ── one-step: як символ звужує інтервал (формули low/high) ─────────────────────
# Ідея: поточний [low,high) → новий [low+r·c_lo, low+r·c_hi), r=high−low.
# Показати, що ширина нового = стара ширина × p(символу).

def fig_one_step():
    W, H = 720, 300
    p = []
    x0, x1, y = 90, 630, 130
    full = x1 - x0
    lo, hi = 0.2, 0.8
    bx0 = x0 + lo * full
    bw = (hi - lo) * full

    # поточний інтервал
    p.append(rect(bx0, y, bw, 40, fill="#f4f6f8", stroke=INK, sw=1.6))
    p.append(text(bx0, y - 12, "low", size=11, color=NEG, anchor="middle", bold=True))
    p.append(text(bx0 + bw, y - 12, "high", size=11, color=NEG, anchor="middle", bold=True))
    p.append(line(bx0, y + 40, bx0, y + 58, color=MUTED, sw=1))
    p.append(line(bx0 + bw, y + 40, bx0 + bw, y + 58, color=MUTED, sw=1))
    p.append(text(bx0 + bw / 2, y + 74, "ширина r = high − low", size=11, color=MUTED))

    # ділимо на частки символів (кумулятивні межі c)
    cum = [0.0, 0.6, 0.9, 1.0]
    names = ["A", "B", "C"]
    cols = ["#eef4ff", "#eafaf0", "#fdf6e3"]
    edge = [NEG, FIELD, "#d98a00"]
    for i in range(3):
        sx = bx0 + cum[i] * bw
        sw_ = (cum[i + 1] - cum[i]) * bw
        sel = (i == 1)
        p.append(rect(sx, y, sw_, 40, fill="#fdecea" if sel else cols[i],
                      stroke=POS if sel else edge[i], sw=2.4 if sel else 1.0))
        p.append(text(sx + sw_ / 2, y + 25, names[i], size=12,
                      color=POS if sel else edge[i], bold=True))

    # формула нового інтервалу під вибраним B
    bsx = bx0 + cum[1] * bw
    bsw = (cum[2] - cum[1]) * bw
    p.append(arrow(bsx + bsw / 2, y + 92, bsx + bsw / 2, y + 112, color=POS, sw=1.8))
    b, w_, h_ = textbox(W / 2, 150 + 30, "new_low  = low + r · c_lo\nnew_high = low + r · c_hi",
                        size=12, bold=True, fill="#fdf6e3", stroke="#d98a00", sw=1.6, color=INK)
    # розмістимо рамку нижче
    b2, w2, h2 = textbox(W / 2, 235, "обираємо символ «B»:  new_low = low + r·c(B)\n"
                                     "нова ширина = r · p(B)  — частка від старої",
                         size=11, bold=False, fill="#eef4ff", stroke=NEG, sw=1.4, color=INK)
    p.append(b2)

    render(os.path.join(OUT, "one-step.svg"), W, H, *p,
           title="Один символ звужує інтервал пропорційно своїй імовірності")


# ── fractional-bits: дробові біти vs цілі (Гаффман) ───────────────────────────
# Ідея: коли p далеке від степеня ½, Гаффман округлює довжину коду до цілого
# й переплачує; арифметичне платить дробову −log2(p) і майже дістає ентропію.

def fig_fractional_bits():
    W, H = 720, 330
    p = []
    ax0, ay = 110, 250
    aw, ah = 520, 190
    p.append(arrow(ax0, ay, ax0, ay - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ax0, ay, ax0 + aw, ay, color=INK, sw=1.6))
    p.append(text(ax0 + aw, ay + 22, "p (імовірність символу)", size=11, color=INK,
                  italic=True, anchor="end"))
    p.append(text(ax0 - 12, ay - ah + 2, "біт", size=11, color=INK, bold=True, anchor="end"))

    bits_max = 5.0
    for b in range(1, 6):
        yv = ay - b / bits_max * ah
        p.append(line(ax0 - 4, yv, ax0 + 4, yv, color=INK, sw=1))
        p.append(text(ax0 - 8, yv + 4, str(b), size=9, color=MUTED, anchor="end"))

    # крива −log2(p): чесна (дробова) ціна = те, що платить арифметичне
    pts = []
    n = 220
    for i in range(n + 1):
        pr = 0.04 + (1.0 - 0.04) * i / n
        bits = -math.log(pr, 2)
        x = ax0 + pr * aw
        yv = ay - min(bits, bits_max) / bits_max * ah
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))
    p.append(text(ax0 + 0.30 * aw, ay - 3.4 / bits_max * ah - 8,
                  "−log₂(p): чесна ціна (арифметичне)", size=10, color=FIELD,
                  bold=True, anchor="start"))

    # сходинки Гаффмана: ціле число біт = ceil(−log2 p) на ділянках
    def step(p_lo, p_hi, bitval, lab):
        x_lo = ax0 + p_lo * aw
        x_hi = ax0 + p_hi * aw
        yv = ay - bitval / bits_max * ah
        p.append(line(x_lo, yv, x_hi, yv, color=POS, sw=2.4))
        if lab:
            p.append(text((x_lo + x_hi) / 2, yv - 6, lab, size=9, color=POS, anchor="middle"))
    step(0.04, 0.0625, 5, "")
    step(0.0625, 0.125, 4, "4 біти")
    step(0.125, 0.25, 3, "3")
    step(0.25, 0.5, 2, "2")
    step(0.5, 1.0, 1, "1 біт")
    p.append(text(ax0 + 0.62 * aw, ay - 1 / bits_max * ah - 24,
                  "Гаффман: цілі біти (сходинки)", size=10, color=POS, bold=True, anchor="middle"))

    # вертикаль розриву на p=0.9
    pr = 0.9
    xg = ax0 + pr * aw
    yh = ay - 1 / bits_max * ah          # Гаффман дав би 1 біт
    yf = ay - (-math.log(pr, 2)) / bits_max * ah
    p.append(line(xg, yh, xg, yf, color=INK, sw=1.4, dash="3 3"))
    p.append(text(xg - 6, (yh + yf) / 2 + 4, "переплата", size=9, color=INK, anchor="end"))

    p.append(text(W / 2, ay + 60,
                  "що далі p від степеня ½ — то більший розрив: цілий біт ≫ дробова −log₂(p)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "fractional-bits.svg"), W, H, *p,
           title="Дробові біти на символ: арифметичне тулиться до ентропії")


# ── everywhere: де живе арифметичне кодування ─────────────────────────────────
# Ідея: одна ідея «інтервал» — у кількох сучасних стандартах; розрізнити
# класичне арифметичне (CABAC, JPEG2000) і сучасний нащадок rANS (Zstd, JPEG XL).

def fig_everywhere():
    W, H = 720, 290
    p = []
    cx, cy = W / 2, 78
    core, cw, ch = textbox(cx, cy, "інтервал → код", size=15, bold=True,
                           fill="#f6f4ec", stroke=INK, sw=2, pad=14, color=INK)
    p.append(core)
    children = [
        (140, 210, "CABAC\nH.264 / H.265", NEG, "#eef4ff"),
        (360, 210, "MQ-кодер\nJPEG2000 · JBIG2", FIELD, "#eafaf0"),
        (580, 210, "rANS\nZstd · JPEG XL · LZFSE", "#8a5fb0", "#f2ecf8"),
    ]
    for gx, gy, lab, col, fill in children:
        b, bw, bh = textbox(gx, gy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(line(cx, cy + ch / 2, gx, gy - bh / 2, color=MUTED, sw=1.4))
        p.append(b)
    p.append(text(W / 2, H - 18,
                  "одна ідея — звузити інтервал — у кожному сучасному кодеку фото й відео",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "everywhere.svg"), W, H, *p,
           title="Звуження інтервалу — усюди в сучасному стисненні")


# ══════════════════════════════════════════════════════════════════════════════
# Детальна стаття (arithmetic-coding-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── renorm: нескінченна точність → renormalization ────────────────────────────
# Ідея: щойно [low,high) цілком влізли в одну половину [0,½) чи [½,1), старший
# біт уже відомий — видаємо його й розтягуємо інтервал ×2 (вертаємо точність).

def fig_renorm():
    W, H = 720, 320
    p = []
    x0, x1 = 110, 630
    full = x1 - x0

    def axis(y, lab):
        p.append(line(x0, y, x1, y, color=INK, sw=1.4))
        p.append(text(x0, y + 16, "0", size=9, color=MUTED, anchor="middle"))
        p.append(text((x0 + x1) / 2, y + 16, "½", size=9, color=MUTED, anchor="middle"))
        p.append(text(x1, y + 16, "1", size=9, color=MUTED, anchor="middle"))
        p.append(line((x0 + x1) / 2, y - 6, (x0 + x1) / 2, y + 6, color=MUTED, sw=1, dash="2 2"))
        p.append(text(x0 - 12, y + 4, lab, size=11, color=INK, anchor="end", bold=True))

    # крок 1: інтервал [0.55,0.70) — цілком у верхній половині [½,1)
    y1 = 80
    axis(y1, "було")
    a, b = 0.55, 0.70
    p.append(rect(x0 + a * full, y1 - 12, (b - a) * full, 24, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(x0 + (a + b) / 2 * full, y1 - 20, "[.55,.70) ⊂ [½,1)", size=10,
                  color=POS, anchor="middle", bold=True))

    # стрілка-операція
    p.append(arrow(W / 2, y1 + 30, W / 2, y1 + 58, color=INK, sw=1.8))
    bb, ww, hh = textbox(W / 2, y1 + 78, "верхня половина → старший біт = 1\nвидаємо «1», віднімаємо ½, множимо ×2",
                         size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, color=INK)
    p.append(bb)

    # крок 2: розтягнутий інтервал [0.10,0.40)
    y2 = 250
    axis(y2, "стало")
    a2, b2 = (a - 0.5) * 2, (b - 0.5) * 2   # 0.10 .. 0.40
    p.append(rect(x0 + a2 * full, y2 - 12, (b2 - a2) * full, 24, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(x0 + (a2 + b2) / 2 * full, y2 - 20, "[.10,.40) — точність відновлено",
                  size=10, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "renorm.svg"), W, H, *p,
           title="Renormalization: відомий старший біт — видати й розтягнути ×2")


# ── int-range: цілочисельний діапазон [low,high] на 32 бітах ───────────────────
# Ідея: замість дробів [0,1) тримаємо цілі low,high у 32-бітних регістрах;
# звуження = масштабування цілими; коли збігся старший байт — виводимо його.

def fig_int_range():
    W, H = 720, 270
    p = []
    # два регістри як рядок «байтів»: старший байт збігся → готовий до виводу
    bx, by, cell = 150, 90, 46
    nbytes = 4

    def reg(y, bytes_, lab, match):
        p.append(text(bx - 14, y + cell / 2 + 4, lab, size=12, color=INK, anchor="end", bold=True))
        for i in range(nbytes):
            sel = (i == 0 and match)
            col = "#fdecea" if sel else "#f4f6f8"
            edge = POS if sel else "#bbbbbb"
            p.append(rect(bx + i * (cell + 4), y, cell, cell, fill=col, stroke=edge, sw=1.4 if sel else 0.9))
            p.append(text(bx + i * (cell + 4) + cell / 2, y + cell / 2 + 4, bytes_[i], size=11,
                          color=POS if sel else MUTED, anchor="middle", bold=sel))

    reg(by, ["B3", "6A", "·", "·"], "high", True)
    reg(by + cell + 12, ["B3", "1C", "·", "·"], "low ", True)

    # рамка довкола спільного старшого байта
    p.append(rect(bx - 3, by - 3, cell + 6, 2 * cell + 18, fill="none", stroke=POS, sw=2, rx=8))
    p.append(text(bx + cell / 2, by - 14, "старший байт збігся", size=11, color=POS, bold=True, anchor="middle"))

    p.append(arrow(bx + cell + 8, by + cell + 6, bx + cell + 70, by + cell + 6, color=INK, sw=1.7))
    b, w_, h_ = textbox(bx + cell + 170, by + cell + 6, "виводимо байт 0xB3\nі зсуваємо обидва ×256",
                        size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, color=NEG)
    p.append(b)

    p.append(text(W / 2, H - 22,
                  "цілі low, high у 32-бітних регістрах; щойно старший байт спільний — він готовий: виводимо й зсуваємо",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "int-range.svg"), W, H, *p,
           title="Цілочисельний range coder: дроби → цілі регістри")


# ── adaptive: модель учиться на льоту ─────────────────────────────────────────
# Ідея: лічильники символів ростуть під час кодування; частки в інтервалі
# міняються кадр у кадр — кодер і декодер ведуть ту саму статистику синхронно.

def fig_adaptive():
    W, H = 720, 290
    p = []
    # три знімки лічильників A/B/C, що змінюються
    names = ["A", "B", "C"]
    cols = [NEG, FIELD, "#d98a00"]
    fills = ["#eef4ff", "#eafaf0", "#fdf6e3"]
    snaps = [
        ("старт", [1, 1, 1]),
        ("після A A B", [3, 2, 1]),
        ("після ще A", [4, 2, 1]),
    ]
    bw, gap = 180, 40
    x0 = (W - (3 * bw + 2 * gap)) / 2
    y0, bh = 70, 150
    for s, (lab, cnt) in enumerate(snaps):
        x = x0 + s * (bw + gap)
        p.append(rect(x, y0, bw, bh, fill="#ffffff", stroke=INK, sw=1.4))
        p.append(text(x + bw / 2, y0 - 8, lab, size=11, color=INK, bold=True))
        tot = sum(cnt)
        # стовпчики часток
        bx0 = x + 18
        bwid = (bw - 36) / 3
        for i in range(3):
            frac = cnt[i] / tot
            hh = frac * (bh - 50)
            p.append(rect(bx0 + i * bwid + 6, y0 + bh - 18 - hh, bwid - 12, hh,
                          fill=fills[i], stroke=cols[i], sw=1.6))
            p.append(text(bx0 + i * bwid + bwid / 2, y0 + bh - 4, names[i], size=10,
                          color=cols[i], bold=True))
            p.append(text(bx0 + i * bwid + bwid / 2, y0 + bh - 22 - hh, str(cnt[i]),
                          size=9, color=cols[i], anchor="middle", bold=True))
        if s < 2:
            p.append(arrow(x + bw + 4, y0 + bh / 2, x + bw + gap - 4, y0 + bh / 2, color=INK, sw=1.6))

    p.append(text(W / 2, y0 + bh + 36,
                  "кодер і декодер оновлюють ті самі лічильники однаково — модель адаптується без окремої таблиці",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "adaptive.svg"), W, H, *p,
           title="Адаптивна модель: частки символів учаться на льоту")


if __name__ == "__main__":
    # базова
    fig_narrowing()
    fig_one_step()
    fig_fractional_bits()
    fig_everywhere()
    # детальна
    fig_renorm()
    fig_int_range()
    fig_adaptive()
    print("OK: figures written to", OUT)
