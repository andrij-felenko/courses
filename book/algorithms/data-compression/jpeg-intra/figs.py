# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def gray(v):
    """v у [0,255] → hex сірого."""
    v = max(0, min(255, int(round(v))))
    return "#%02x%02x%02x" % (v, v, v)


# ══════════════════════════════════════════════════════════════════════════════
# 1. pipeline-full — увесь конвеєр JPEG вертикально, з поміткою кроків із утратами
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: показати послідовність перетворень і чітко відділити ТРИ кроки з утратами
# (проріджування хроми + квантування) від оборотних. Уся «магія» стиску — у квантуванні.

def fig_pipeline():
    W, H = 760, 620
    p = []
    bx = 200          # ліва межа блоків
    bw = 300          # ширина блока
    y = 58
    gap = 62
    steps = [
        ("RGB-кадр з камери", "нейтр"),
        ("Розділити колір → Y, Cb, Cr", "ok"),
        ("Проріджування хроми 4:2:0", "loss"),
        ("Нарізати на блоки 8×8", "nb"),
        ("DCT: пікселі → 64 частоти", "ok"),
        ("Квантування (округлити, обнулити)", "loss"),
        ("Зигзаг + розділити DC / AC", "nb"),
        ("Гаффман: ентропійне пакування", "ok"),
        (".jpg — крихітний файл", "file"),
    ]
    colmap = {
        "нейтр": (FILL, LINE, INK),
        "ok":    ("#eafaf0", FIELD, INK),
        "loss":  ("#fdecea", POS, INK),
        "nb":    ("#eef4ff", NEG, INK),
        "file":  ("#fdf6e3", "#d98a00", INK),
        "file2": ("#fdf6e3", "#d98a00", INK),
    }
    ys = []
    for i, (label, kind) in enumerate(steps):
        fill, stroke, col = colmap[kind]
        cy = y + i * gap
        ys.append(cy)
        p.append(fitbox(bx, cy - 20, bw, 40, label, size=13, fill=fill, stroke=stroke, sw=2, color=col, bold=(kind in ("loss", "file"))))
    for i in range(len(steps) - 1):
        p.append(arrow(bx + bw / 2, ys[i] + 20, bx + bw / 2, ys[i + 1] - 20, color=MUTED, sw=1.8))

    # праворуч — легенда-помітки на кроки з утратами / оборотні
    def tag(cy, txt, col, fill):
        b = fitbox(bx + bw + 24, cy - 15, 232, 30, txt, size=11, fill=fill, stroke=col, sw=1.5, color=col, bold=True)
        p.append(b)
        p.append(line(bx + bw + 4, cy, bx + bw + 24, cy, color=col, sw=1.4))
    tag(ys[2], "з утратами: −50% даром", POS, "#fdecea")
    tag(ys[5], "з утратами: головний стиск", POS, "#fdecea")
    tag(ys[4], "без утрат: інша форма запису", FIELD, "#eafaf0")
    tag(ys[7], "без утрат: чесний перепис", FIELD, "#eafaf0")

    # ліворуч — вертикальна дужка «незалежно для кожного блока 8×8»
    x0 = bx - 34
    yA, yB = ys[3] - 18, ys[6] + 18
    p.append(line(x0, yA, x0, yB, color=MUTED, sw=1.6))
    p.append(line(x0, yA, x0 + 10, yA, color=MUTED, sw=1.6))
    p.append(line(x0, yB, x0 + 10, yB, color=MUTED, sw=1.6))
    p.append(text(x0 - 6, (yA + yB) / 2 - 8, "кожен", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 6, (yA + yB) / 2 + 6, "блок", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 6, (yA + yB) / 2 + 20, "8×8", size=10, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "pipeline-full.svg"), W, H, *p,
           title="Конвеєр JPEG: три кроки з утратами, решта оборотна")


# ══════════════════════════════════════════════════════════════════════════════
# 2. ycbcr-subsample — RGB → Y, Cb, Cr + проріджування хроми 4:2:0
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: колір розкладають на яскравість (повну) і дві хроми, а хрому проріджують —
# один відлік кольору на квадрат 2×2 пікселів яскравості. Половина даних зникає даром.

def fig_ycbcr():
    W, H = 760, 380
    p = []

    def grid(x0, y0, n, cell, colorfn, stroke="#c9ced6"):
        for r in range(n):
            for c in range(n):
                p.append(rect(x0 + c * cell, y0 + r * cell, cell, cell,
                              fill=colorfn(r, c), stroke=stroke, sw=0.7, rx=0))

    # ── RGB зліва (кольоровий кадрик) ──
    import random
    random.seed(7)
    cols = ["#7fb3e0", "#8fc98f", "#e0a97f", "#c98f8f"]
    gx, gy, cell = 70, 120, 18
    grid(gx, gy, 6, cell, lambda r, c: cols[(r + c) % len(cols)])
    p.append(text(gx + 3 * cell, gy - 14, "RGB-кадр", size=12, color=INK, bold=True))
    p.append(text(gx + 3 * cell, gy + 6 * cell + 20, "3 числа / піксель", size=10, color=MUTED))

    p.append(arrow(gx + 6 * cell + 12, gy + 3 * cell, gx + 6 * cell + 58, gy + 3 * cell, color=INK, sw=2))

    # ── три площини праворуч ──
    def luma(r, c):
        return gray(60 + (r * 6 + c * 5) % 170)
    def chroma_b(r, c):
        return gray(120 + ((r + c) % 3) * 30)
    def chroma_r(r, c):
        return gray(140 - ((r + c) % 3) * 25)

    px = 300
    # Y — повна роздільність 6×6
    yy = 60
    grid(px, yy, 6, cell, luma)
    p.append(text(px + 3 * cell, yy - 12, "Y — яскравість", size=12, color=INK, bold=True))
    p.append(text(px + 6 * cell + 14, yy + 3 * cell + 4, "повна роздільність", size=10, color=FIELD, anchor="start", bold=True))

    # Cb, Cr — проріджені 3×3 (кожна клітина = 2×2 люми), клітина вдвічі більша
    bcell = cell * 2
    cy2 = yy + 6 * cell + 34
    grid(px, cy2, 3, bcell, chroma_b, stroke="#b9c0cc")
    p.append(text(px + 3 * cell, cy2 - 10, "Cb — синь", size=11, color=NEG, bold=True))
    px2 = px + 3 * bcell + 40
    grid(px2, cy2, 3, bcell, chroma_r, stroke="#d8b9b9")
    p.append(text(px2 + 3 * cell, cy2 - 10, "Cr — червінь", size=11, color=POS, bold=True))
    p.append(text(px + 3 * bcell + 20, cy2 + 3 * bcell + 22,
                  "1 відлік кольору на квадрат 2×2 → вчетверо менше чисел кольору",
                  size=10, color=MUTED))

    # виноска: один квадрат 2×2 люми → один піксель хроми
    p.append(rect(px, yy, bcell, bcell, fill="none", stroke=POS, sw=2.2, rx=0))
    p.append(rect(px, cy2, bcell, bcell, fill="none", stroke=POS, sw=2.2, rx=0))
    p.append(line(px + bcell, yy + bcell, px + bcell, cy2, color=POS, sw=1.2, dash="4 3"))

    render(os.path.join(OUT, "ycbcr-subsample.svg"), W, H, *p,
           title="Колір: розділити на яскравість і хрому, хрому — прорідити")


# ══════════════════════════════════════════════════════════════════════════════
# 3. dct-basis — сітка 8×8 базових візерунків DCT
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: ГОЛОВНА фігура. Будь-який блок = зважена сума цих 64 цеглинок. Угорі-ліворуч
# рівний фон (DC), праворуч росте горизонтальна частота, вниз — вертикальна.

def fig_dct_basis():
    W, H = 520, 560
    p = []
    N = 8
    sub = 5           # піксель базису
    b = N * sub       # розмір однієї цеглинки = 40
    gap = 6
    ox, oy = 96, 76
    for v in range(N):          # частота вертикальна (рядок)
        for u in range(N):      # частота горизонтальна (стовпець)
            bx = ox + u * (b + gap)
            by = oy + v * (b + gap)
            for y in range(N):
                for x in range(N):
                    val = math.cos((2 * x + 1) * u * math.pi / 16) * math.cos((2 * y + 1) * v * math.pi / 16)
                    g = 128 + 127 * val
                    p.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s"/>'
                             % (bx + x * sub, by + y * sub, sub, sub, gray(g)))
            p.append(rect(bx, by, b, b, fill="none", stroke="#b9c0cc", sw=0.8, rx=0))

    span = N * (b + gap) - gap
    # осі частот
    p.append(arrow(ox, oy - 20, ox + span, oy - 20, color=NEG, sw=1.8))
    p.append(text(ox + span / 2, oy - 28, "частота горизонтальна u →", size=11, color=NEG, bold=True))
    p.append(arrow(ox - 22, oy, ox - 22, oy + span, color=NEG, sw=1.8))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">частота вертикальна v ↓</text>'
             % (ox - 40, oy + span / 2, FONT, NEG, ox - 40, oy + span / 2))

    # помітки кутів
    p.append(text(ox + b / 2, oy + span + 22, "DC: рівний фон", size=10, color=FIELD, bold=True))
    p.append(text(ox + span - b / 2, oy + span + 22, "найдрібніша", size=10, color=POS, bold=True, anchor="middle"))
    p.append(rect(ox, oy, b, b, fill="none", stroke=FIELD, sw=2.4, rx=0))
    p.append(rect(ox + (N - 1) * (b + gap), oy + (N - 1) * (b + gap), b, b, fill="none", stroke=POS, sw=2.4, rx=0))

    render(os.path.join(OUT, "dct-basis.svg"), W, H, *p,
           title="64 базові візерунки DCT — цеглинки будь-якого блока")


# ══════════════════════════════════════════════════════════════════════════════
# 4. artifacts-detail — три артефакти JPEG
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: показати корінь кожного артефакту. Блочність — незалежні блоки 8×8;
# дзвін — обрізані високі частоти біля різкого краю; розпливання — проріджена хрома.

def fig_artifacts():
    W, H = 760, 320
    p = []
    top = 66
    ph = 150

    # ── Панель A: блочність ──
    ax = 60
    aw = 176
    p.append(text(ax + aw / 2, top - 14, "Блочність", size=13, color=POS, bold=True))
    nb = 4
    bs = aw / nb
    tone = [[70, 92, 88, 120], [96, 150, 120, 100], [80, 118, 175, 140], [110, 96, 132, 96]]
    for r in range(nb):
        for c in range(nb):
            p.append(rect(ax + c * bs, top + r * bs, bs, bs, fill=gray(tone[r][c]), stroke="#ffffff", sw=1.6, rx=0))
    p.append(text(ax + aw / 2, top + ph + 24, "межі блоків 8×8 —", size=10, color=MUTED))
    p.append(text(ax + aw / 2, top + ph + 38, "кожен стискали окремо", size=10, color=MUTED))

    # ── Панель B: дзвін ──
    bx = 300
    bw = 176
    p.append(text(bx + bw / 2, top - 14, "Дзвін", size=13, color=POS, bold=True))
    # фон: ліва темна, права світла — різкий край посередині
    mid = bx + bw * 0.5
    p.append(rect(bx, top, bw * 0.5, ph, fill=gray(70), stroke="none", rx=0))
    p.append(rect(mid, top, bw * 0.5, ph, fill=gray(210), stroke="none", rx=0))
    p.append(rect(bx, top, bw, ph, fill="none", stroke="#c9ced6", sw=1, rx=0))
    # брижі-хвильки біля краю (профіль коливання)
    pts = []
    for i in range(0, 161):
        t = i / 160.0
        xx = bx + t * bw
        d = (t - 0.5) * bw
        env = math.exp(-abs(d) / 22.0)
        val = math.sin(d / 7.0) * env
        yy = top + ph * 0.5 - val * 46
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), POS))
    p.append(line(mid, top, mid, top + ph, color=INK, sw=1, dash="3 3"))
    p.append(text(bx + bw / 2, top + ph + 24, "брижі біля різкого краю —", size=10, color=MUTED))
    p.append(text(bx + bw / 2, top + ph + 38, "обрізані високі частоти", size=10, color=MUTED))

    # ── Панель C: розпливання кольору ──
    cx = 540
    cw = 176
    p.append(text(cx + cw / 2, top - 14, "Розпливання кольору", size=12, color=POS, bold=True))
    p.append(rect(cx, top, cw, ph, fill="#ffffff", stroke="#c9ced6", sw=1, rx=0))
    # рожевий ореол навколо червоної смуги
    p.append(rect(cx + cw * 0.30, top, cw * 0.40, ph, fill="#f6c9c9", stroke="none", rx=0))
    p.append(rect(cx + cw * 0.40, top, cw * 0.20, ph, fill="#c0392b", stroke="none", rx=0))
    p.append(text(cx + cw / 2, top + ph + 24, "барва тече за предмет —", size=10, color=MUTED))
    p.append(text(cx + cw / 2, top + ph + 38, "хрому прорідили 4:2:0", size=10, color=MUTED))

    render(os.path.join(OUT, "artifacts-detail.svg"), W, H, *p,
           title="Три артефакти JPEG ростуть прямо з будови конвеєра")


# ══════════════════════════════════════════════════════════════════════════════
# 5. dct-extension — періодичне (ДПФ) проти дзеркального (DCT) продовження блока
# ══════════════════════════════════════════════════════════════════════════════
# Ідея (math-dct): DCT неявно продовжує блок ДЗЕРКАЛЬНО — без стрибка на межі,
# тому висока частота слабка. ДПФ продовжує ПЕРІОДИЧНО — на шві стрибок 112→40,
# і саме він живить високі частоти. Одна картинка пояснює «чому косинус».

def fig_dct_extension():
    W, H = 760, 452
    p = []
    N = 8
    base = [40, 54, 66, 76, 85, 93, 100, 112]   # зростає: кінці різні (40 і 112)
    vmin, vmax = 28, 124
    dx, x0, bh = 34, 104, 72
    tops = [74, 204, 334]

    def ymap(v, top):
        return top + bh - (v - vmin) / (vmax - vmin) * bh

    def strip(top, vals, real_n, seam_color, note, note_color):
        axis = top + bh + 8
        p.append(rect(x0 - dx / 2, top - 4, real_n * dx, bh + 16, fill="#eaf0fd", stroke="none", rx=4))
        p.append(line(x0 - 12, axis, x0 + (len(vals) - 1) * dx + 12, axis, color="#d0d5dd", sw=1))
        pts = [(x0 + i * dx, ymap(v, top)) for i, v in enumerate(vals)]
        poly = " ".join("%.1f,%.1f" % xy for xy in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (poly, MUTED))
        if len(vals) > real_n:                    # підсвітити шов між блоком і продовженням
            (xa, ya), (xb, yb) = pts[real_n - 1], pts[real_n]
            xs = (xa + xb) / 2
            p.append(line(xs, top - 4, xs, axis, color=seam_color, sw=1, dash="3 3"))
            p.append(line(xa, ya, xb, yb, color=seam_color, sw=3.4))
        for i, (xx, yy) in enumerate(pts):
            col = NEG if i < real_n else MUTED
            p.append(line(xx, axis, xx, yy, color=col, sw=0.9, dash="2 2"))
            p.append(circle(xx, yy, 3.1, fill=col, stroke=col, sw=1))
        if note:
            p.append(text(x0 + (real_n - 0.5) * dx, axis + 20, note, size=11, color=note_color, bold=True))

    strip(tops[0], base, N, None, None, None)
    p.append(text(x0, tops[0] - 12, "Блок: 8 відліків яскравості", size=12, color=INK, anchor="start", bold=True))
    p.append(text(x0 + (N - 0.5) * dx, tops[0] + bh + 28, "кінці різні: 40 і 112", size=11, color=MUTED))

    strip(tops[1], base + base, N, POS, "стрибок 112 → 40", POS)
    p.append(text(x0, tops[1] - 12, "Продовження ДПФ — періодичне (копія блока)", size=12, color=INK, anchor="start", bold=True))

    strip(tops[2], base + base[::-1], N, FIELD, "рівно: 112 = 112", FIELD)
    p.append(text(x0, tops[2] - 12, "Продовження DCT — дзеркальне (відбиток блока)", size=12, color=INK, anchor="start", bold=True))

    lx, ly = 648, 78
    p.append(circle(lx, ly, 3.1, fill=NEG, stroke=NEG, sw=1))
    p.append(text(lx + 9, ly + 4, "блок", size=10, color=INK, anchor="start"))
    p.append(circle(lx, ly + 17, 3.1, fill=MUTED, stroke=MUTED, sw=1))
    p.append(text(lx + 9, ly + 21, "продовження", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "dct-extension.svg"), W, H, *p,
           title="Чому косинус: дзеркальне продовження — без стрибка на межі")


# ══════════════════════════════════════════════════════════════════════════════
# 6. dct-compaction — та сама рампа: як AC-енергія лягає по коефіцієнтах (ДПФ vs DCT)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея (math-dct): f=[1,2,3,4]. DCT кидає майже всю AC-енергію в найнижчий F₁,
# а найвищий F₃ мізерний. ДПФ «бачить» стрибок на періодичному шві й розмазує
# енергію аж до Найквіста. Числа порахованi в тексті вставки — тут вони наочні.

def fig_dct_compaction():
    W, H = 740, 384
    p = []
    base_y = 300
    scale = 40.0                     # 1 одиниця енергії → 40 px (макс 5 → 200 px)

    # горизонтальні напрямні шкали
    for val in range(1, 6):
        gy = base_y - val * scale
        p.append(line(96, gy, 656, gy, color="#eef1f5", sw=1))
        p.append(text(86, gy + 4, str(val), size=9, color=MUTED, anchor="end"))

    def bar(cx, val, color, top_lbl, x_lbl):
        h = max(val * scale, 2.0)
        y = base_y - h
        p.append(rect(cx - 23, y, 46, h, fill=color, stroke=LINE, sw=1, rx=2))
        p.append(text(cx, y - 7, top_lbl, size=11, color=INK, bold=True))
        p.append(text(cx, base_y + 16, x_lbl, size=11, color=INK))

    def axis(x1, x2):
        p.append(line(x1, base_y, x2, base_y, color=INK, sw=1.4))

    # ── ліворуч: ДПФ ──
    axis(96, 316)
    p.append(text(206, 54, "ДПФ: енергія |Xₖ|² / N", size=13, color=NEG, bold=True))
    bar(136, 2.0, "#eaf0fd", "2.0", "k=1")
    bar(206, 1.0, POS, "1.0", "k=2")
    bar(276, 2.0, "#eaf0fd", "2.0", "k=3")
    p.append(text(206, base_y + 32, "k=2 — Найквіст (найвища)", size=10, color=POS, bold=True))

    # ── праворуч: DCT ──
    axis(416, 656)
    p.append(text(536, 54, "DCT: енергія Fₖ²", size=13, color=FIELD, bold=True))
    bar(456, 4.975, "#eafaf0", "4.98", "F₁")
    bar(536, 0.0, "#eafaf0", "0.0", "F₂")
    bar(616, 0.025, POS, "0.025", "F₃")
    p.append(text(536, base_y + 32, "F₃ — найвища частота", size=10, color=POS, bold=True))

    p.append(text(W / 2, 356,
                  "Той самий лінійний сигнал f = [1, 2, 3, 4]. DC відкинуто (=25, однаковий). AC-енергія однакова (=5) — розподіл ні: DCT 0.5% нагорі, ДПФ 20%.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "dct-compaction.svg"), W, H, *p,
           title="Зосередження енергії: DCT стягує сигнал у два коефіцієнти")


# ══════════════════════════════════════════════════════════════════════════════
# 7. hist-timeline — чотири стадії формату на одній осі (для вставки hist-jpeg)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: розчепити «ідею / теорію / стандарт / патент» у часі й показати іронію —
# відкрита теорія 1974-го стала prior art, яким 2006-го скасували патент 1986-го.

def fig_hist_timeline():
    W, H = 960, 480
    p = []
    left = 150

    def X(yr):
        return left + (yr - 1970) * 20.0

    y_top, y_bot = 74, 428

    # рамка іронічної підписи вже відома тут (обчислюємо заздалегідь), щоб
    # вертикальні роки-лінії йшли ПОВЗ неї, а не крізь текст
    irony_cx, irony_cy = X(1993), 236
    irony_w = text_width(max(
        "відкрита теорія 1974 → «попередній рівень техніки»,".split("\n") +
        ["яким 2006-го й скасували патент"], key=len), 11, False) + 20
    irony_h = 2 * 11 * 1.3 + 20 - 11 * 0.3
    ibx0, iby0 = irony_cx - irony_w / 2 - 6, irony_cy - irony_h / 2 - 6
    ibx1, iby1 = irony_cx + irony_w / 2 + 6, irony_cy + irony_h / 2 + 6

    for yr in range(1970, 2009, 5):
        gx = X(yr)
        if ibx0 <= gx <= ibx1:
            # лінія року проходить крізь підпис-рамку — розриваємо її, щоб
            # обидва відрізки лишались ПОЗА написом
            p.append(line(gx, y_top, gx, iby0, color="#e6e9ed", sw=1))
            p.append(line(gx, iby1, gx, y_bot, color="#e6e9ed", sw=1))
        else:
            p.append(line(gx, y_top, gx, y_bot, color="#e6e9ed", sw=1))
        p.append(text(gx, y_top - 8, str(yr), size=11, color=MUTED))

    lanes = [(120, "ІДЕЯ", NEG), (195, "ТЕОРІЯ", FIELD),
             (290, "СТАНДАРТ", "#d98a00"), (380, "ПАТЕНТ", POS)]
    for yc, lab, col in lanes:
        p.append(text(136, yc + 4, lab, size=13, color=col, anchor="end", bold=True))

    def dot(x, y, col, r=6):
        p.append(circle(x, y, r, fill=col, stroke="#ffffff", sw=1.5))

    # ІДЕЯ
    dot(X(1972), 120, NEG)
    p.append(text(X(1972) + 14, 116, "1972 · заявку на ґрант NSF відкинуто («надто просто»)",
                  size=11, color=INK, anchor="start"))
    # ТЕОРІЯ
    dot(X(1974), 195, FIELD)
    p.append(text(X(1974) + 14, 191, "1974 · стаття «Discrete Cosine Transform» — Ахмед · Натараджан · Рао",
                  size=11, color=INK, anchor="start"))
    # СТАНДАРТ
    p.append(rect(X(1986), 290 - 9, X(1994) - X(1986), 18, fill="#fbeecb", stroke="#d98a00", sw=1.6, rx=4))
    for yr in (1986, 1992, 1994):
        dot(X(yr), 290, "#d98a00", r=5)
    p.append(text((X(1986) + X(1994)) / 2, 290 + 30,
                  "комітет 1986  ·  T.81 1992  ·  ISO/IEC 10918-1 1994", size=11, color=INK))
    # ПАТЕНТ
    p.append(rect(X(1986), 380 - 9, X(2006) - X(1986), 18, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    for yr in (1986, 1987, 2003, 2006):
        dot(X(yr), 380, POS, r=5)
    p.append(text((X(1986) + X(2006)) / 2, 380 + 30,
                  "подано 1986 · видано 1987 · вимоги ліцензій (~$105 млн) · скасовано 2006",
                  size=11, color=INK))
    # іронія: відкрита теорія → prior art, що скасував патент
    p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
             % (X(1974), 203, X(1996), 250, X(2006), 371, FIELD))
    lbl, _, _ = textbox(X(1993), 236,
                        "відкрита теорія 1974 → «попередній рівень техніки»,\nяким 2006-го й скасували патент",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.4, color=INK)
    p.append(lbl)

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Чотири різні речі під однією назвою «JPEG» — і хто за кожну відповідав")


# ══════════════════════════════════════════════════════════════════════════════
# 8. file-layout — ланцюг сегментів .jpg від SOI до EOI (для вставки api-markers)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: показати, що .jpg — це не суцільний потік, а низка сегментів у порядку;
# таблиці (DQT/DHT) лежать ПЕРЕД сканом, а стандалон-маркери (SOI/EOI/RST) не мають
# ні довжини, ні даних. Ентропійний потік — змінної довжини, без поля довжини.

def fig_file_layout():
    W, H = 1040, 320
    p = []
    y_box = 118
    bh, bw, gap, x0 = 66, 110, 12, 34
    # (мнемоніка, hex, нотатка, вид)  вид: std=стандалон · seg=сегмент · data=потік
    segs = [
        ("SOI",  "FF D8", "початок\nзображення",        "std"),
        ("APP0", "FF E0", "JFIF: версія,\nщільність",    "seg"),
        ("DQT",  "FF DB", "таблиці\nквантування",        "seg"),
        ("SOF0", "FF C0", "розмір,\nкомпоненти,\nпроріджування", "seg"),
        ("DHT",  "FF C4", "таблиці\nГаффмана",           "seg"),
        ("SOS",  "FF DA", "заголовок\nскану",            "seg"),
        ("дані", "—",     "ентропійний потік\n+ RSTn усередині", "data"),
        ("EOI",  "FF D9", "кінець\nзображення",          "std"),
    ]
    kindcol = {"std": ("#eaf0fd", NEG), "seg": ("#eafaf0", FIELD), "data": ("#fdf6e3", "#d98a00")}
    xs, x = [], x0
    for mn, hx, note, kind in segs:
        fill, stroke = kindcol[kind]
        xs.append(x)
        p.append(text(x + bw / 2, y_box - 12, hx, size=11, color=MUTED, bold=True))
        p.append(rect(x, y_box, bw, bh, fill=fill, stroke=stroke, sw=2, rx=6))
        p.append(text(x + bw / 2, y_box + bh / 2 + 6, mn, size=17, color=INK, bold=True))
        p.append(fitbox(x, y_box + bh + 12, bw, 50, note, size=10, fill="#ffffff", stroke="#e3e7ec", sw=1, color=MUTED))
        x += bw + gap
    for i in range(len(segs) - 1):
        p.append(arrow(xs[i] + bw, y_box + bh / 2, xs[i + 1], y_box + bh / 2, color=MUTED, sw=1.6))

    ly = H - 22
    def leg(lx, col, fill, txt):
        p.append(rect(lx, ly - 12, 16, 16, fill=fill, stroke=col, sw=2, rx=3))
        p.append(text(lx + 22, ly + 1, txt, size=11, color=INK, anchor="start"))
    leg(70, NEG, "#eaf0fd", "стандалон — без поля довжини й без даних (SOI · EOI · RST0–7)")
    leg(600, FIELD, "#eafaf0", "сегмент — маркер + 2 байти довжини + дані")
    render(os.path.join(OUT, "file-layout.svg"), W, H, *p,
           title="Будова .jpg: ланцюг сегментів від SOI до EOI")


# ══════════════════════════════════════════════════════════════════════════════
# 9. segment-anatomy — байтова будова сегмента + байт-стафінг (для api-markers)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: два правила, на яких тримається читання файлу. (А) сегмент = маркер(2) +
# довжина(2) + дані(довжина−2); поле «довжина» рахує себе, але не маркер. (Б) у
# стиснутому потоці справжній 0xFF пишуть як FF 00 — інакше його сплутали б з маркером.

def fig_segment_anatomy():
    W, H = 900, 380
    p = []
    cw, ch = 46, 40

    # ── (А) загальна будова сегмента ──
    p.append(text(W / 2, 52, "Сегмент = маркер (2) + довжина (2) + дані (довжина − 2)", size=14, color=INK, bold=True))
    ya = 96
    x = 64
    def cell(cx, cy, txt, fill, stroke=LINE):
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=stroke, sw=1.4, rx=4))
        p.append(text(cx + cw / 2, cy + ch / 2 + 5, txt, size=13, color=INK, bold=True))
    cell(x, ya, "FF", "#eaf0fd"); cell(x + cw, ya, "xx", "#eaf0fd")
    lx = x + 2 * cw + 8
    cell(lx, ya, "LL", "#eafaf0"); cell(lx + cw, ya, "LL", "#eafaf0")
    dx, dw = lx + 2 * cw + 8, 300
    p.append(rect(dx, ya, dw, ch, fill="#fdf6e3", stroke="#d98a00", sw=1.4, rx=4))
    p.append(text(dx + dw / 2, ya + ch / 2 + 5, "корисні дані — (довжина − 2) байтів", size=12, color=INK))
    # короткі підписи груп
    p.append(text(x + cw, ya + ch + 20, "маркер", size=12, color=NEG, bold=True))
    p.append(text(lx + cw, ya + ch + 20, "довжина", size=12, color=FIELD, bold=True))
    p.append(text(dx + dw / 2, ya + ch + 20, "дані", size=12, color="#d98a00", bold=True))
    # дужка над «довжина + дані»
    by = ya - 16
    p.append(line(lx, by, dx + dw, by, color=POS, sw=1.4))
    p.append(line(lx, by, lx, by + 8, color=POS, sw=1.4))
    p.append(line(dx + dw, by, dx + dw, by + 8, color=POS, sw=1.4))
    p.append(text((lx + dx + dw) / 2, by - 6, "поле «довжина»: старший байт першим, рахує себе + дані (не маркер)", size=10, color=POS, bold=True))

    p.append(line(50, 176, W - 50, 176, color="#e3e7ec", sw=1))

    # ── (Б) байт-стафінг ──
    p.append(text(W / 2, 208, "Байт-стафінг: у стиснутому потоці справжній 0xFF подвоюють нулем", size=14, color=INK, bold=True))
    bx = 250
    def stuffrow(cy, c1, c2, note, col, fill):
        cell(bx, cy, c1, "#fdecea", stroke=POS if c1 == "FF" else LINE)
        cell(bx + cw, cy, c2, fill)
        p.append(arrow(bx + 2 * cw + 10, cy + ch / 2, bx + 2 * cw + 40, cy + ch / 2, color=col, sw=1.8))
        p.append(text(bx + 2 * cw + 50, cy + ch / 2 + 5, note, size=12, color=INK, anchor="start"))
    stuffrow(240, "FF", "00", "справжній байт 0xFF (нуль — лише розділювач, декодер його викидає)", FIELD, "#eaf0fd")
    stuffrow(300, "FF", "D9", "це МАРКЕР (тут EOI): 0xFF + не-нуль = кінець ентропійних даних", POS, "#fdecea")

    render(os.path.join(OUT, "segment-anatomy.svg"), W, H, *p,
           title="Два правила читання: будова сегмента й байт-стафінг")


# ══════════════════════════════════════════════════════════════════════════════
# 10. block-to-stream — той самий канонічний блок: зигзаг стягує 20 ненульових
#     у початок стрічки, а хвіст із 38 нулів закриває один EOB (вставка proj-encode)
# ══════════════════════════════════════════════════════════════════════════════

def fig_block_to_stream():
    W, H = 820, 520
    p = []
    Sq = [
        [-26, -3, -6,  2,  2, -1, 0, 0],
        [  0, -2, -4,  1,  1,  0, 0, 0],
        [ -3,  1,  5, -1, -1,  0, 0, 0],
        [ -3,  1,  2, -1,  0,  0, 0, 0],
        [  1,  0,  0,  0,  0,  0, 0, 0],
        [  0,  0,  0,  0,  0,  0, 0, 0],
        [  0,  0,  0,  0,  0,  0, 0, 0],
        [  0,  0,  0,  0,  0,  0, 0, 0],
    ]
    ZZ = [0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,
          12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,
          35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,
          58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]
    cell = 40
    ox, oy = 46, 58
    for r in range(8):
        for c in range(8):
            v = Sq[r][c]
            nz = (v != 0)
            p.append(rect(ox + c * cell, oy + r * cell, cell, cell,
                          fill="#eaf0fd" if nz else BG,
                          stroke=NEG if nz else "#e2e6ea",
                          sw=1.5 if nz else 0.8, rx=0))
            p.append(text(ox + c * cell + cell / 2, oy + r * cell + cell / 2 + 5, str(v),
                          size=14 if nz else 12,
                          color=INK if nz else "#c4c9cf", bold=nz))
    pts = []
    for k in range(26):
        idx = ZZ[k]
        pts.append((ox + (idx % 8) * cell + cell / 2, oy + (idx // 8) * cell + cell / 2))
    poly = " ".join("%.1f,%.1f" % xy for xy in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" opacity="0.9"/>' % (poly, POS))
    p.append(circle(pts[0][0], pts[0][1], 5.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(circle(pts[25][0], pts[25][1], 5.5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(ox + 4 * cell, oy + 8 * cell + 22,
                  "20 ненульових · усі в куті низьких частот", size=11, color=MUTED))

    px = ox + 8 * cell + 30
    bw = W - px - 24
    p.append(fitbox(px, 64, bw, 48,
                    "Зигзаг: 64 числа → стрічка,\nвід низьких частот до високих",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))
    p.append(fitbox(px, 128, bw, 48,
                    "Червона лінія — порядок обходу;\nзелений старт — DC (сталий фон)",
                    size=12, fill=FILL, stroke=LINE, sw=1.4, color=INK))
    p.append(fitbox(px, 192, bw, 62,
                    "Після 26-го числа — 38 нулів поспіль.\nОдин маркер EOB закриває їх усі —\nна кожен нуль біти не витрачаються.",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6, color=INK))

    stream = [Sq[ZZ[k] // 8][ZZ[k] % 8] for k in range(26)]
    cs = 26
    total = 26 * cs + 6 + 90
    sx = (W - total) / 2
    sy = 430
    p.append(text(W / 2, sy - 14, "Стрічка (зигзаг):", size=12, color=INK, bold=True))
    for k, v in enumerate(stream):
        nz = (v != 0)
        fill = FIELD if k == 0 else ("#eaf0fd" if nz else "#f0f2f4")
        col = "#ffffff" if k == 0 else (INK if nz else "#b7bcc2")
        p.append(rect(sx + k * cs, sy, cs, cs, fill=fill, stroke="#cfd4da", sw=0.8, rx=0))
        p.append(text(sx + k * cs + cs / 2, sy + cs / 2 + 4, str(v), size=10, color=col, bold=nz))
    ex = sx + 26 * cs + 6
    p.append(rect(ex, sy, 90, cs, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(ex + 45, sy + cs / 2 + 4, "EOB · 38×0", size=10, color=POS, bold=True))
    p.append(text(sx + cs / 2, sy + cs + 16, "DC", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "block-to-stream.svg"), W, H, *p,
           title="Зигзаг: квантований блок 8×8 → коротка стрічка")


# ══════════════════════════════════════════════════════════════════════════════
# 11. category-coding — категорія (кількість бітів) + правило знаку амплітуди
#     (proj-encode): додатні пишуть як є, від'ємні — інвертованим модулем
# ══════════════════════════════════════════════════════════════════════════════

def fig_category_coding():
    W, H = 800, 348
    p = []
    lx, ly = 48, 70
    p.append(text(lx, ly - 16, "Категорія = число бітів на |v|",
                  size=12, color=INK, anchor="start", bold=True))
    rows = [("1", "1"), ("2", "2…3"), ("3", "4…7"), ("4", "8…15"),
            ("5", "16…31"), ("6", "32…63"), ("…", "…")]
    rh, cw1, cw2 = 30, 64, 150
    p.append(rect(lx, ly, cw1, rh, fill="#eef4ff", stroke=NEG, sw=1.2, rx=0))
    p.append(text(lx + cw1 / 2, ly + rh / 2 + 4, "SIZE", size=11, color=NEG, bold=True))
    p.append(rect(lx + cw1, ly, cw2, rh, fill="#eef4ff", stroke=NEG, sw=1.2, rx=0))
    p.append(text(lx + cw1 + cw2 / 2, ly + rh / 2 + 4, "діапазон |v|", size=11, color=NEG, bold=True))
    for i, (s, rng) in enumerate(rows):
        yy = ly + (i + 1) * rh
        p.append(rect(lx, yy, cw1, rh, fill=BG, stroke="#d7dbe0", sw=0.8, rx=0))
        p.append(text(lx + cw1 / 2, yy + rh / 2 + 4, s, size=12, color=INK, bold=True))
        p.append(rect(lx + cw1, yy, cw2, rh, fill=BG, stroke="#d7dbe0", sw=0.8, rx=0))
        p.append(text(lx + cw1 + cw2 / 2, yy + rh / 2 + 4, rng, size=11, color=INK))

    rx0 = 322
    p.append(text(rx0, 50, "Значення → біти амплітуди", size=12, color=INK, anchor="start", bold=True))
    examples = [
        ("−26", "|26| = 11010", "від'ємне → інвертувати", "00101", "категорія 5", NEG),
        ("−6",  "|6| = 110",    "від'ємне → інвертувати", "001",   "категорія 3", NEG),
        ("2",   "|2| = 10",     "додатне → як є",          "10",    "категорія 2", POS),
    ]
    ey, eh = 72, 70
    for val, mag, rule, bitsv, catv, col in examples:
        cy = ey + eh / 2
        b, w, h = textbox(rx0 + 32, cy, val, size=17, pad=12, fill="#f4f6f8",
                          stroke=col, sw=2, color=col, bold=True, min_w=56)
        p.append(b)
        p.append(text(rx0 + 80, cy - 7, mag, size=12, color=INK, anchor="start"))
        p.append(text(rx0 + 80, cy + 13, rule, size=10, color=MUTED, anchor="start"))
        p.append(arrow(rx0 + 258, cy, rx0 + 300, cy, color=MUTED, sw=1.6))
        bb, ww, hh = textbox(rx0 + 352, cy, bitsv, size=16, pad=12,
                             fill="#eafaf0" if col == POS else "#eaf0fd",
                             stroke=col, sw=2, color=INK, bold=True, min_w=72)
        p.append(bb)
        p.append(text(rx0 + 352, cy + hh / 2 + 14, catv, size=10, color=MUTED))
        ey += eh + 6

    render(os.path.join(OUT, "category-coding.svg"), W, H, *p,
           title="Кодування значення: категорія + амплітуда")


if __name__ == "__main__":
    fig_pipeline()
    fig_ycbcr()
    fig_dct_basis()
    fig_artifacts()
    fig_dct_extension()
    fig_dct_compaction()
    fig_hist_timeline()
    fig_file_layout()
    fig_segment_anatomy()
    fig_block_to_stream()
    fig_category_coding()
    print("OK: figures written to", OUT)
