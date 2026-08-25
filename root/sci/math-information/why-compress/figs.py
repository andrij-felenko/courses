# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── the-gap: сире джерело vs вузький канал ────────────────────────────────────
# Ідея: ліворуч величезний потік (висока смуга), праворуч — вузька «труба»;
# між ними множник розриву. Показати, що стиснення мусить покрити саме його.

def fig_the_gap():
    W, H = 700, 300
    p = []
    # ліва товста смуга — сире джерело
    bx, bw = 60, 150
    p.append(rect(bx, 70, bw, 170, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(bx + bw / 2, 96, "сирий потік", size=12, color=POS, bold=True))
    p.append(text(bx + bw / 2, 150, "1.5 Гбіт/с", size=17, color=POS, bold=True))
    p.append(text(bx + bw / 2, 174, "(1080p · 30)", size=10, color=MUTED))
    p.append(text(bx + bw / 2, 210, "187 МБ", size=11, color=INK))
    p.append(text(bx + bw / 2, 226, "щосекунди", size=10, color=MUTED))

    # стрілка-«лійка» до вузької труби
    p.append(arrow(bx + bw + 6, 155, 372, 155, color=INK, sw=2))

    # вузька труба — реальний канал
    tx, tw = 388, 60
    p.append(rect(tx, 130, tw, 48, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(tx + tw / 2, 120, "канал", size=11, color=NEG, bold=True))
    p.append(text(tx + tw / 2, 158, "~20", size=13, color=NEG, bold=True))
    p.append(text(tx + tw / 2, 196, "Мбіт/с", size=10, color=MUTED))

    # перелік реальних труб праворуч
    lx = 480
    p.append(text(lx, 110, "куди має влізти:", size=11, color=INK, anchor="start", bold=True))
    for i, s in enumerate(["радіо FPV  10–50 Мбіт/с",
                            "Wi-Fi  десятки–сотні",
                            "SD-картка  малий обсяг"]):
        p.append(text(lx, 134 + i * 22, "• " + s, size=10, color=INK, anchor="start"))

    # множник розриву
    b, bbw, bbh = textbox(W / 2, 250, "розрив у сотні–тисячі разів", size=13,
                          bold=True, color=POS, fill="#fdf6e3", stroke="#d98a00", sw=1.8)
    p.append(b)

    render(os.path.join(OUT, "the-gap.svg"), W, H, *p,
           title="Прірва: сире джерело не влазить у реальний канал")


# ── redundancy: три роди надлишку ─────────────────────────────────────────────
# Ідея: три картки поруч — просторовий, часовий, перцептивний; кожна з крихітною
# піктограмою-ідеєю. Це «здобич» стиснення.

def fig_redundancy():
    W, H = 720, 290
    p = []
    cw, ch, gap = 200, 180, 24
    x0 = (W - (3 * cw + 2 * gap)) / 2
    y0 = 70

    cards = [
        ("просторовий", FIELD, "#eafaf0", "сусідні точки\nкадру — схожі",
         "опиши пляму,\nне кожну точку"),
        ("часовий", NEG, "#eef4ff", "сусідні кадри —\nмайже однакові",
         "шли лише те,\nщо змінилося"),
        ("перцептивний", "#8a5fb0", "#f2ecf8", "око не бачить\nдрібниць",
         "викинь те, чого\nне помітно"),
    ]
    for i, (title, col, fill, what, idea) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, y0 + 26, title, size=13, color=col, bold=True))
        p.append(mtext(x + cw / 2, y0 + 58, what, size=11, color=INK))
        p.append(line(x + 20, y0 + 104, x + cw - 20, y0 + 104, color=col, sw=1, dash="4 3"))
        p.append(mtext(x + cw / 2, y0 + 132, idea, size=11, color=col, bold=True))

    render(os.path.join(OUT, "redundancy.svg"), W, H, *p,
           title="Три роди надлишку, що його полює стиснення")


# ── lossless-vs-lossy: дві стратегії стовпчиками ──────────────────────────────
# Ідея: дві вертикальні смуги-стиску: без утрат скромний (~2×), з утратами
# великий (10–100×); підписати ціну й виграш кожної.

def fig_lossless_vs_lossy():
    W, H = 700, 320
    p = []
    base_y, base_h = 250, 170
    # «оригінал» — пунктирна рамка повної висоти для масштабу
    ox = 90
    p.append(rect(ox, base_y - base_h, 90, base_h, fill="#f4f6f8", stroke=MUTED, sw=1.4))
    p.append(text(ox + 45, base_y - base_h - 10, "оригінал", size=11, color=MUTED))
    p.append(text(ox + 45, base_y + 20, "100%", size=10, color=MUTED))

    # без утрат ~50%
    lx = 300
    h1 = base_h * 0.5
    p.append(rect(lx, base_y - h1, 90, h1, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(lx + 45, base_y - base_h - 10, "без утрат", size=12, color=NEG, bold=True))
    p.append(text(lx + 45, base_y - h1 - 8, "~2×", size=13, color=NEG, bold=True))
    p.append(text(lx + 45, base_y + 20, "точно до біта", size=10, color=INK))
    p.append(text(lx + 45, base_y + 36, "(як zip)", size=10, color=MUTED))

    # з утратами ~5%
    rx = 500
    h2 = base_h * 0.08
    p.append(rect(rx, base_y - h2, 90, h2, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(rx + 45, base_y - base_h - 10, "з утратами", size=12, color=POS, bold=True))
    p.append(text(rx + 45, base_y - h2 - 8, "10–100×", size=13, color=POS, bold=True))
    p.append(text(rx + 45, base_y + 20, "≈ оригінал", size=10, color=INK))
    p.append(text(rx + 45, base_y + 36, "(викидаємо непомітне)", size=9, color=MUTED))

    # вісь
    p.append(line(60, base_y, 620, base_y, color=INK, sw=1.6))

    render(os.path.join(OUT, "lossless-vs-lossy.svg"), W, H, *p,
           title="Дві стратегії: точність (скромно) проти розміру (різко)")


# ── principle: передбачення − реальність = несподіванка ───────────────────────
# Ідея: рівняння-схема трьома блоками: відоме → передбачення; реальність;
# різниця = мала несподіванка (її й пишемо).

def fig_principle():
    W, H = 720, 250
    p = []
    y = 120
    # блок «передбачення з відомого»
    b1, w1, h1 = textbox(150, y, "передбач\nз відомого", size=12, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, color=NEG)
    p.append(b1)
    # мінус
    p.append(minus(150 + w1 / 2 + 28, y, r=13))
    # блок «реальність»
    b2, w2, h2 = textbox(360, y, "реальне\nзначення", size=12, bold=True,
                         fill="#f4f6f8", stroke=INK, sw=1.6)
    p.append(b2)
    # дорівнює
    p.append(text(360 + w2 / 2 + 34, y + 6, "=", size=22, color=INK, bold=True))
    # блок «несподіванка»
    b3, w3, h3 = textbox(560, y, "несподіванка\n(мала)", size=12, bold=True,
                         fill="#fdecea", stroke=POS, sw=2, color=POS)
    p.append(b3)

    p.append(text(W / 2, y + 78,
                  "чим краще передбачення — тим менша різниця — тим сильніше стиснення",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "principle.svg"), W, H, *p,
           title="Душа стиснення: записуй лише несподіване")


# ══════════════════════════════════════════════════════════════════════════════
# Фігури історичної вставки (hist-dct.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── waves: клаптик = сума косинусних візерунків ───────────────────────────────
# Ідея: ліворуч клаптик; праворуч три базові хвилі з вагами (велика → ≈0).

def fig_waves():
    W, H = 720, 280
    p = []
    # клаптик-плашка ліворуч (плавний градієнт імітуємо смугами)
    px, py, ps = 60, 90, 120
    for i in range(6):
        shade = 0xe8 - i * 14
        col = "#%02x%02x%02x" % (shade, shade, 0xf2)
        p.append(rect(px, py + i * ps / 6, ps, ps / 6, fill=col, stroke="none", sw=0))
    p.append(rect(px, py, ps, ps, fill="none", stroke=INK, sw=1.6))
    p.append(text(px + ps / 2, py - 12, "клаптик 8×8", size=11, color=INK, bold=True))

    p.append(text(px + ps + 24, py + ps / 2 + 6, "=", size=22, color=INK, bold=True))

    # три хвилі праворуч
    wx0 = px + ps + 60
    ww, wh = 120, 56
    waves = [(1.0, "плавний", "× велика вага", FIELD),
             (3.0, "середній", "× середня", NEG),
             (8.0, "дрібний", "× ≈ 0", MUTED)]
    for i, (freq, lab, wt, col) in enumerate(waves):
        wy = py + i * (wh + 16)
        pts = []
        for k in range(0, 121):
            t = k / 120.0
            v = math.cos(freq * math.pi * t)
            pts.append("%.1f,%.1f" % (wx0 + t * ww, wy + wh / 2 - v * wh * 0.4))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), col))
        p.append(text(wx0 + ww + 12, wy + wh / 2 - 4, lab, size=10, color=col, anchor="start", bold=True))
        p.append(text(wx0 + ww + 12, wy + wh / 2 + 12, wt, size=9, color=MUTED, anchor="start"))
        if i < 2:
            p.append(text(wx0 + ww / 2, wy + wh + 8, "+", size=14, color=INK))

    render(os.path.join(OUT, "waves.svg"), W, H, *p,
           title="Клаптик зображення = сума косинусних хвиль")


# ── compress: енергія збирається в кількох коефіцієнтах ───────────────────────
# Ідея: сітка 8×8 коефіцієнтів DCT; темні (велика енергія) — лише в кутку
# ліворуч-угорі, решта ≈ 0 (світлі) → їх викидаємо.

def fig_compress():
    W, H = 700, 340
    p = []
    n = 8
    cell = 26
    gx, gy = 90, 64
    for r in range(n):
        for c in range(n):
            # енергія падає з відстанню від кутка (0,0)
            d = (r + c)
            val = math.exp(-0.55 * d)
            shade = int(0xf4 - val * 0xd0)
            col = "#%02x%02x%02x" % (shade, shade, shade)
            p.append(rect(gx + c * cell, gy + r * cell, cell, cell, fill=col, stroke="#cccccc", sw=0.6))
    p.append(rect(gx, gy, n * cell, n * cell, fill="none", stroke=INK, sw=1.6))
    # обвести кутову зону «енергії»
    p.append(rect(gx, gy, 3 * cell, 3 * cell, fill="none", stroke=POS, sw=2.2))
    p.append(text(gx + 1.5 * cell, gy - 10, "тут уся енергія", size=11, color=POS, bold=True))

    # підписи осей частот
    p.append(arrow(gx, gy + n * cell + 14, gx + n * cell, gy + n * cell + 14, color=MUTED, sw=1.2))
    p.append(text(gx + n * cell, gy + n * cell + 30, "частота →", size=10, color=MUTED, anchor="end"))
    p.append(arrow(gx - 14, gy, gx - 14, gy + n * cell, color=MUTED, sw=1.2))

    # пояснення праворуч
    tx = gx + n * cell + 40
    for i, s in enumerate(["низькі частоти —", "великі числа (темні).", "",
                            "високі — майже нулі", "(світлі): викидаємо", "чи грубо округлюємо.",
                            "", "було 64 числа —", "лишилось кілька."]):
        p.append(text(tx, gy + 10 + i * 22, s, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "compress.svg"), W, H, *p,
           title="Після DCT уся «енергія» — у кількох коефіцієнтах")


# ── ahmed: часова стрічка ідеї DCT ────────────────────────────────────────────

def fig_ahmed():
    W, H = 720, 230
    p = []
    ax0, ax1, y = 70, 650, 120
    p.append(line(ax0, y, ax1, y, color=INK, sw=2))
    marks = [
        (1972, "«надто просто»\n(грант відмовили)", POS),
        (1974, "стаття\nAhmed–Natarajan–Rao", NEG),
        (1992, "JPEG", FIELD),
        (2003, "H.264", FIELD),
        (2026, "усюди", MUTED),
    ]
    span0, span1 = 1972, 2026
    for yr, lab, col in marks:
        x = ax0 + (yr - span0) / (span1 - span0) * (ax1 - ax0)
        p.append(circle(x, y, 5, fill=col, stroke=col, sw=1))
        p.append(text(x, y - 16, str(yr), size=11, color=col, bold=True))
        p.append(mtext(x, y + 28, lab, size=9, color=INK))
    render(os.path.join(OUT, "ahmed.svg"), W, H, *p,
           title="Шлях «надто простої» ідеї: 1972 → сьогодні")


# ── everywhere: одна цеглинка DCT — у багатьох стандартах ──────────────────────

def fig_everywhere():
    W, H = 700, 260
    p = []
    cx, cy = W / 2, 80
    core, cw, ch = textbox(cx, cy, "DCT", size=16, bold=True, fill="#f6f4ec",
                           stroke=INK, sw=2, pad=16, color=INK)
    p.append(core)
    children = [
        (140, 200, "JPEG\n(фото)", NEG, "#eef4ff"),
        (350, 200, "MPEG / H.264\n(відео)", FIELD, "#eafaf0"),
        (560, 200, "FPV-стрім\nі запис", "#d98a00", "#fdf6e3"),
    ]
    for gx, gy, lab, col, fill in children:
        b, bw, bh = textbox(gx, gy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(line(cx, cy + ch / 2, gx, gy - bh / 2, color=MUTED, sw=1.4))
        p.append(b)
    render(os.path.join(OUT, "everywhere.svg"), W, H, *p,
           title="Одна цеглинка — у кожному стисненому фото й відео")


# ══════════════════════════════════════════════════════════════════════════════
# Фігури детальної версії (why-compress-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── surprise: несподіванка = log2(1/p) ────────────────────────────────────────
# Ідея: крива −log2(p): часте (p→1) майже не дивує (→0 біт), рідкісне (p→0)
# дивує сильно (→∞). Це «ціна в бітах» однієї події.

def fig_surprise():
    W, H = 700, 320
    ox, oy = 80, 260
    aw, ah = 560, 210
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 10, oy + 22, "p (імовірність події)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 14, oy - ah + 4, "біт", size=11, color=INK, bold=True, anchor="end"))

    # крива −log2(p) на p∈[0.02..1]; масштаб біт 0..5.6
    pmax_bits = 5.6
    pts = []
    n = 240
    for i in range(n + 1):
        pr = 0.02 + (1.0 - 0.02) * i / n
        bits = -math.log(pr, 2)
        x = ox + pr * aw
        yv = oy - min(bits, pmax_bits) / pmax_bits * ah
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # позначки рівнів біт
    for bits in (1, 2, 3, 4, 5):
        yv = oy - bits / pmax_bits * ah
        p.append(line(ox - 4, yv, ox + 4, yv, color=INK, sw=1.2))
        p.append(text(ox - 8, yv + 4, str(bits), size=9, color=MUTED, anchor="end"))

    # дві точки-приклади
    def mark(pr, lab, col):
        bits = -math.log(pr, 2)
        x = ox + pr * aw
        yv = oy - bits / pmax_bits * ah
        p.append(circle(x, yv, 4, fill=col, stroke=col, sw=1))
        p.append(line(x, oy, x, yv, color=col, sw=1, dash="3 3"))
        p.append(text(x, yv - 10, lab, size=10, color=col, bold=True))
    mark(0.5, "p=½ → 1 біт", FIELD)
    mark(0.06, "рідкісне → ~4 біти", POS)
    mark(0.9, "часте → ~0.15 біта", MUTED)

    render(os.path.join(OUT, "surprise.svg"), W, H, *p,
           title="Несподіванка події: I = log₂(1/p) бітів")


# ── entropy-bound: ентропія як підлога стиску ─────────────────────────────────
# Ідея: горизонтальна вісь «біт на символ»; підлога = H (ентропія); коди
# наближаються згори, але нижче не можна. RLE→Гаффман→арифметичне ближче до H.

def fig_entropy_bound():
    W, H = 720, 300
    p = []
    ax0, ax1, ay = 90, 640, 210
    p.append(arrow(ax0, ay, ax1, ay, color=INK, sw=1.6))
    p.append(text(ax1, ay + 22, "біт на символ", size=11, color=INK, italic=True, anchor="end"))

    # підлога H
    Hx = ax0 + 70
    p.append(line(Hx, 70, Hx, ay + 6, color=POS, sw=2.4, dash="6 4"))
    p.append(text(Hx, 60, "H — ентропія (межа)", size=12, color=POS, bold=True))
    # заборонена зона ліворуч від H
    p.append(rect(ax0, 80, Hx - ax0, ay - 80, fill="#fdecea", stroke="none", sw=0))
    p.append(text((ax0 + Hx) / 2, 150, "не можна", size=11, color=POS, bold=True))
    p.append(text((ax0 + Hx) / 2, 168, "(без утрат)", size=9, color=POS))

    # три коди-точки праворуч від H, що сходяться до неї
    codes = [(Hx + 230, "наївний фікс. код"), (Hx + 150, "Гаффман (< H+1)"),
             (Hx + 70, "арифметичне ≈ H")]
    for i, (x, lab) in enumerate(codes):
        yv = 110 + i * 30
        p.append(circle(x, yv, 4, fill=NEG, stroke=NEG, sw=1))
        p.append(text(x + 10, yv + 4, lab, size=10, color=NEG, anchor="start"))
        p.append(arrow(x - 4, yv, Hx + 6, yv, color=MUTED, sw=1.2))

    p.append(text(W / 2, ay + 60,
                  "стискати можна аж до H, та не нижче: під H інформація вже зникає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "entropy-bound.svg"), W, H, *p,
           title="Ентропія H — непереборна підлога стиску без утрат")


# ── source-models: краща модель джерела → нижча ентропія ──────────────────────
# Ідея: три сходинки моделі (символи нарізно → пари літер → контекст), кожна
# наступна «бачить» більше зв'язків і дає меншу оцінку біт/символ.

def fig_source_models():
    W, H = 720, 300
    p = []
    steps = [
        ("символи\nнарізно", "не знає зв'язків", "~4.7 біт/символ", "#fdecea", POS),
        ("частоти\nсимволів", "е частіше за ж", "~4.0 біт/символ", "#fdf6e3", "#d98a00"),
        ("контекст\n(сусіди)", "q → майже завжди u", "~1.5 біт/символ", "#eafaf0", FIELD),
    ]
    bw, bh, gap = 200, 150, 24
    x0 = (W - (3 * bw + 2 * gap)) / 2
    y0 = 70
    for i, (title, ex, val, fill, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        # сходинка: що далі, то нижче «дно» (менше біт)
        p.append(rect(x, y0, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(mtext(x + bw / 2, y0 + 30, title, size=13, color=col, bold=True))
        p.append(text(x + bw / 2, y0 + 78, ex, size=10, color=INK))
        p.append(line(x + 20, y0 + 96, x + bw - 20, y0 + 96, color=col, sw=1, dash="4 3"))
        p.append(text(x + bw / 2, y0 + 122, val, size=12, color=col, bold=True))
        if i < 2:
            p.append(arrow(x + bw + 2, y0 + bh / 2, x + bw + gap - 2, y0 + bh / 2, color=INK, sw=1.6))

    p.append(text(W / 2, y0 + bh + 40,
                  "ентропія — не властивість тексту, а властивість моделі: краща модель бачить більше надлишку",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "source-models.svg"), W, H, *p,
           title="Краща модель джерела → нижча ентропія → сильніший стиск")


# ── rle: повтор як найпростіший надлишок ──────────────────────────────────────
# Ідея: довгий рядок однакових символів → пара (символ, лічильник). Наочно,
# як принцип «не пиши те, що передбачуване» працює в найгрубішій формі.

def fig_rle():
    W, H = 700, 230
    p = []
    y = 90
    cell = 26
    seq = "ААААААААBBBBCC"
    x0 = 70
    for i, ch in enumerate(seq):
        col = "#eef4ff" if ch == "А" else ("#eafaf0" if ch == "B" else "#fdf6e3")
        p.append(rect(x0 + i * cell, y, cell, cell, fill=col, stroke=INK, sw=1))
        p.append(text(x0 + i * cell + cell / 2, y + cell / 2 + 5, ch, size=12, color=INK, bold=True))
    p.append(text(x0, y - 12, "%d символів вхідних" % len(seq), size=11, color=MUTED, anchor="start"))

    p.append(arrow(W / 2, y + cell + 16, W / 2, y + cell + 40, color=INK, sw=1.8))

    # вихід: пари (символ × лічильник)
    yo = y + cell + 64
    pairs = [("А", 8, "#eef4ff"), ("B", 4, "#eafaf0"), ("C", 2, "#fdf6e3")]
    xp = 230
    for ch, n, col in pairs:
        b, bw, bh = textbox(xp, yo, "%s×%d" % (ch, n), size=13, bold=True, fill=col, stroke=INK, sw=1.4)
        p.append(b)
        xp += bw + 16
    p.append(text(xp - 6, yo + 4, "→ 3 пари", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "rle.svg"), W, H, *p,
           title="RLE: довгий повтор → (символ, лічильник)")


# ── lossy-pipeline: де ховається стиск з утратами ─────────────────────────────
# Ідея: ланцюг трансформація → квантування (тут утрата) → ентропійне кодування.
# Підкреслити: губимо лише на квантуванні, і саме там вирішуємо, що непомітне.

def fig_lossy_pipeline():
    W, H = 740, 230
    p = []
    y = 110
    bw, bh, step = 150, 60, 196
    x = 40
    boxes = [
        ("трансформація\n(DCT)", "#eef4ff", NEG, "перекласти в\n«частоти»"),
        ("квантування", "#fdecea", POS, "тут і тільки тут\nгубимо — викидаємо\nнепомітне"),
        ("ентропійне\nкодування", "#eafaf0", FIELD, "пакуємо решту\nбез утрат"),
    ]
    cx = []
    for i, (lab, fill, col, note) in enumerate(boxes):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        cx.append((x, x + bw))
        p.append(mtext(x + bw / 2, y + bh / 2 + 22, note, size=9, color=MUTED))
        if i > 0:
            p.append(arrow(cx[i - 1][1] + 2, y, x - 2, y, color=INK, sw=1.7))
        x += step
    p.append(text(W / 2, H - 16,
                  "оборотні кроки нічого не втрачають; уся «втрата з утратами» — в одному квантуванні",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "lossy-pipeline.svg"), W, H, *p,
           title="Конвеєр стиску з утратами: губимо лише на квантуванні")


if __name__ == "__main__":
    # базова стаття
    fig_the_gap()
    fig_redundancy()
    fig_lossless_vs_lossy()
    fig_principle()
    # історична вставка
    fig_waves()
    fig_compress()
    fig_ahmed()
    fig_everywhere()
    # детальна стаття
    fig_surprise()
    fig_entropy_bound()
    fig_source_models()
    fig_rle()
    fig_lossy_pipeline()
    print("OK: figures written to", OUT)
