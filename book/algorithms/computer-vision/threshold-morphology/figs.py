# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── thresholding: сіре → гістограма з двома купами, T у долині → маска ─────────
# Ідея: якщо об'єкт і тло різняться яскравістю, гістограма має дві купи; поріг T
# у долині між ними ділить кадр на біле (об'єкт) і чорне (тло). Оцу ставить T сам.

def fig_thresholding():
    W, H = 820, 380
    p = []

    # ── ліворуч: сірий кадр ──
    bx, by, bw, bh = 30, 120, 150, 132
    p.append(text(bx + bw / 2, by - 12, "сіре", size=11, color=INK, bold=True))
    p.append(rect(bx, by, bw, bh, fill="#5c5c5c", stroke=INK, sw=1.2, rx=8))
    p.append(circle(bx + bw / 2, by + bh / 2, 40, fill="#cdcdcd", stroke="none", sw=0))
    p.append(arrow(bx + bw + 4, by + bh / 2, bx + bw + 40, by + bh / 2, color=INK, sw=1.7))

    # ── центр: гістограма з двома купами ──
    hx, hw = 232, 356          # вісь по x
    base = by + bh             # лінія підстави
    p.append(text(hx + hw / 2, by - 12, "гістограма: дві купи, T у долині",
                  size=10, color=INK, bold=True))
    p.append(line(hx, base, hx + hw, base, color=INK, sw=1.2))
    # дві гаусоподібні купи (тло — нижче й широке зліва; об'єкт — вище справа)
    n = 44
    for i in range(n):
        t = i / float(n - 1)
        xx = hx + 6 + t * (hw - 12)
        # купа тла біля t=0.28, купа об'єкта біля t=0.72
        g1 = math.exp(-((t - 0.28) ** 2) / (2 * 0.10 ** 2))
        g2 = 0.86 * math.exp(-((t - 0.72) ** 2) / (2 * 0.085 ** 2))
        hgt = (g1 + g2) * 96
        p.append(rect(xx, base - hgt, (hw - 12) / n - 0.6, hgt,
                      fill="#94a3b8", stroke="none", sw=0, rx=2))
    # лінія порога T у долині (≈ t=0.5)
    tx = hx + 6 + 0.5 * (hw - 12)
    p.append(line(tx, base + 2, tx, by + 4, color=POS, sw=2, dash="4,3"))
    p.append(text(tx, by - 1, "T (Оцу)", size=9.5, color=POS, bold=True))
    p.append(text(hx + 0.28 * hw, base + 16, "тло → чорне", size=9, color=MUTED))
    p.append(text(hx + 0.74 * hw, base + 16, "об'єкт → біле", size=9, color=MUTED))

    p.append(arrow(hx + hw + 4, by + bh / 2, hx + hw + 40, by + bh / 2, color=INK, sw=1.7))

    # ── праворуч: чорно-біла маска ──
    mx = hx + hw + 44
    p.append(text(mx + bw / 2, by - 12, "чорно-біле (маска)", size=10, color=INK, bold=True))
    p.append(rect(mx, by, bw, bh, fill="#000000", stroke=INK, sw=1.2, rx=8))
    p.append(circle(mx + bw / 2, by + bh / 2, 40, fill="#ffffff", stroke="none", sw=0))

    p.append(text(W / 2, H - 18,
                  "Поріг — найпростіша сегментація: кадр ділять на «об'єкт» і «тло». "
                  "Оцу знаходить найкраще T сам — у долині між купами.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "thresholding.svg"), W, H, *p,
           title="Поріг: із сірого — чорно-біле")


# ── adaptive: нерівне світло — глобальний поріг провалюється, адаптивний ні ────
# Ідея: при нерівному світлі одне T не годиться (вибілює світле, чорнить темне),
# а локальне T для кожної ділянки читає напис і в тіні, і на світлі.

def fig_adaptive():
    W, H = 820, 366
    p = []
    bw, bh = 220, 132
    ys = 96
    xs = [40, 300, 560]
    word = "ТЕКСТ"

    def frame(x, kind):
        # тло з градієнтом «світло ліворуч → тінь праворуч»
        p.append(rect(x, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
        nseg = 22
        for i in range(nseg):
            t = i / float(nseg)
            xx = x + t * bw
            if kind == "scene":
                # градієнт сірого: яскраво ліворуч, темно праворуч
                v = int(210 - t * 180)
                p.append(rect(xx, ys, bw / nseg + 0.6, bh,
                              fill="rgb(%d,%d,%d)" % (v, v, v), stroke="none", sw=0, rx=0))
        if kind == "scene":
            # напис сірим, ледь контрастний на тлі градієнта
            for k, ch in enumerate(word):
                cxx = x + 24 + k * (bw - 48) / (len(word) - 1)
                p.append(text(cxx, ys + bh / 2 + 7, ch, size=20, color="#555555", bold=True))
        elif kind == "global":
            # ліва половина суцільно біла, права суцільно чорна — напис гине
            p.append(rect(x, ys, bw / 2, bh, fill="#ffffff", stroke="none", sw=0, rx=0))
            p.append(rect(x + bw / 2, ys, bw / 2, bh, fill="#000000", stroke="none", sw=0, rx=0))
        elif kind == "adaptive":
            # увесь напис читається білим на чорному
            p.append(rect(x, ys, bw, bh, fill="#000000", stroke="none", sw=0, rx=0))
            for k, ch in enumerate(word):
                cxx = x + 24 + k * (bw - 48) / (len(word) - 1)
                p.append(text(cxx, ys + bh / 2 + 7, ch, size=20, color="#ffffff", bold=True))

    frame(xs[0], "scene")
    p.append(text(xs[0] + bw / 2, ys + bh + 18, "нерівне світло", size=10.5, color=INK, bold=True))
    p.append(text(xs[0] + bw / 2, ys + bh + 33, "яскраво ⟶ тінь", size=9, color=MUTED))

    frame(xs[1], "global")
    p.append(text(xs[1] + bw / 2, ys + bh + 18, "глобальний поріг (одне T)", size=10.5, color=POS, bold=True))
    p.append(text(xs[1] + bw / 2, ys + bh + 33, "світле вибілило, темне зчорніло — напис гине", size=9, color=MUTED))

    frame(xs[2], "adaptive")
    p.append(text(xs[2] + bw / 2, ys + bh + 18, "адаптивний (своє T на ділянку)", size=10.5, color=FIELD, bold=True))
    p.append(text(xs[2] + bw / 2, ys + bh + 33, "напис читається всюди", size=9, color=MUTED))

    p.append(arrow(xs[0] + bw + 4, ys + bh / 2, xs[1] - 4, ys + bh / 2, color=POS, sw=1.7))
    p.append(arrow(xs[1] + bw + 4, ys + bh / 2, xs[2] - 4, ys + bh / 2, color=FIELD, sw=1.7))

    p.append(text(W / 2, H - 16,
                  "Гуляє світло по кадру — єдине T безсиле; локальний поріг рахує своє число "
                  "з околу кожної ділянки.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "adaptive.svg"), W, H, *p,
           title="Адаптивний поріг: своє T для кожної ділянки")


def _blob_white(p, cx, cy, r):
    p.append(circle(cx, cy, r, fill="#ffffff", stroke="none", sw=0))


# ── erosion-dilation: ерозія стискає біле, дилатація розростає ─────────────────
# Ідея: ерозія лишає піксель білим лише якщо всі сусіди білі (біле худне, цятки
# зникають, перемички рвуться); дилатація — якщо хоч один сусід білий (біле
# гладшає, дірки латаються, тіла зливаються).

def fig_erosion_dilation():
    W, H = 880, 372
    p = []
    bw, bh = 146, 120
    ys = 108
    grp_w = 392          # ширина рамки-групи

    # ── ЛІВА група — ерозія: вхід (пляма + цятки + перемичка) → стиснуте ──
    gx = 24
    p.append(rect(gx, ys - 30, grp_w, bh + 70, fill="#fbfbfd", stroke=NEG, sw=1.6, rx=12))
    p.append(text(gx + grp_w / 2, ys - 12, "ЕРОЗІЯ: усі сусіди білі → лишається",
                  size=10.5, color=NEG, bold=True))
    lx = gx + 24
    p.append(rect(lx, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, lx + 52, ys + bh / 2, 29)
    _blob_white(p, lx + 94, ys + bh / 2, 29)          # дві злиплі через перемичку
    for dx, dy in [(16, 14), (126, 18), (22, 98), (124, 94)]:
        p.append(rect(lx + dx, ys + dy, 5, 5, fill="#ffffff", stroke="none", sw=0, rx=1))
    p.append(text(lx + bw / 2, ys + bh + 16, "цятки + злиплі", size=9, color=MUTED))
    p.append(arrow(lx + bw + 6, ys + bh / 2, lx + bw + 40, ys + bh / 2, color=NEG, sw=1.7))
    ox = lx + bw + 44
    p.append(rect(ox, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, ox + 52, ys + bh / 2, 21)
    _blob_white(p, ox + 96, ys + bh / 2, 21)          # розділилися
    p.append(text(ox + bw / 2, ys + bh + 16, "худне, цятки геть, розрив", size=9, color="#15803d"))

    # ── ПРАВА група — дилатація: вхід (пляма з діркою + щілина) → розрослий ──
    gx2 = gx + grp_w + 40
    p.append(rect(gx2, ys - 30, grp_w, bh + 70, fill="#fbfbfd", stroke=FIELD, sw=1.6, rx=12))
    p.append(text(gx2 + grp_w / 2, ys - 12, "ДИЛАТАЦІЯ: хоч один білий → стає",
                  size=10.5, color="#15803d", bold=True))
    lx2 = gx2 + 24
    p.append(rect(lx2, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, lx2 + bw / 2, ys + bh / 2, 33)
    p.append(circle(lx2 + bw / 2 - 8, ys + bh / 2, 8, fill="#0f172a", stroke="none", sw=0))  # дірка
    p.append(rect(lx2 + bw / 2 + 6, ys + bh / 2 - 4, 14, 8, fill="#0f172a", stroke="none", sw=0))  # щілина
    p.append(text(lx2 + bw / 2, ys + bh + 16, "дірка + щілина", size=9, color=MUTED))
    p.append(arrow(lx2 + bw + 6, ys + bh / 2, lx2 + bw + 40, ys + bh / 2, color=FIELD, sw=1.7))
    ox2 = lx2 + bw + 44
    p.append(rect(ox2, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, ox2 + bw / 2, ys + bh / 2, 37)
    p.append(text(ox2 + bw / 2, ys + bh + 16, "гладшає, залатано", size=9, color="#15803d"))

    p.append(text(W / 2, H - 16,
                  "Поодинці кожна міняє й розмір тіла (ерозія потоншує, дилатація потовщує) — "
                  "тому їх поєднують у пари.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "erosion-dilation.svg"), W, H, *p,
           title="Ерозія і дилатація: стиснути й розростити")


# ── opening-closing: відкриття прибирає цятки, закриття латає — розмір цілий ───
# Ідея: ерозія→дилатація (відкриття) знищує дрібне й повертає розмір головному
# тілу; дилатація→ерозія (закриття) затягує дірки й повертає розмір. Унизу —
# типовий конвеєр сіре/HSV → поріг → морфологія → чиста маска.

def fig_opening_closing():
    W, H = 900, 430
    p = []
    bw, bh = 138, 100
    ys = 96

    # ── ВІДКРИТТЯ (ліворуч) ──
    p.append(rect(36, ys - 24, 396, bh + 56, fill="#fbfbfd", stroke=NEG, sw=1.7, rx=12))
    p.append(text(36 + 198, ys - 6, "ВІДКРИТТЯ = ерозія → дилатація", size=10.5, color=NEG, bold=True))
    ax = 64
    # стан 1: пляма + цятки
    p.append(rect(ax, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, ax + bw / 2, ys + bh / 2, 30)
    for dx, dy in [(16, 14), (118, 18), (22, 84), (116, 80)]:
        p.append(rect(ax + dx, ys + dy, 5, 5, fill="#ffffff", stroke="none", sw=0, rx=1))
    p.append(text(ax + bw / 2, ys + bh + 14, "цятки навколо", size=9, color=MUTED))
    p.append(arrow(ax + bw + 6, ys + bh / 2, ax + bw + 38, ys + bh / 2, color=NEG, sw=1.6))
    # стан 2: чисто, той самий розмір
    ax2 = ax + bw + 42
    p.append(rect(ax2, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, ax2 + bw / 2, ys + bh / 2, 30)
    p.append(text(ax2 + bw / 2, ys + bh + 14, "цятки геть, розмір той самий", size=9, color="#15803d"))

    # ── ЗАКРИТТЯ (праворуч) ──
    p.append(rect(468, ys - 24, 396, bh + 56, fill="#fbfbfd", stroke=FIELD, sw=1.7, rx=12))
    p.append(text(468 + 198, ys - 6, "ЗАКРИТТЯ = дилатація → ерозія", size=10.5, color="#15803d", bold=True))
    cx0 = 496
    p.append(rect(cx0, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, cx0 + bw / 2, ys + bh / 2, 34)
    p.append(circle(cx0 + bw / 2 - 8, ys + bh / 2, 8, fill="#0f172a", stroke="none", sw=0))
    p.append(rect(cx0 + bw / 2 + 8, ys + bh / 2 - 4, 14, 8, fill="#0f172a", stroke="none", sw=0))
    p.append(text(cx0 + bw / 2, ys + bh + 14, "дірки й щербини", size=9, color=MUTED))
    p.append(arrow(cx0 + bw + 6, ys + bh / 2, cx0 + bw + 38, ys + bh / 2, color=FIELD, sw=1.6))
    cx2 = cx0 + bw + 42
    p.append(rect(cx2, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.1, rx=8))
    _blob_white(p, cx2 + bw / 2, ys + bh / 2, 34)
    p.append(text(cx2 + bw / 2, ys + bh + 14, "залатано, розмір той самий", size=9, color="#15803d"))

    # ── конвеєр унизу ──
    py = ys + bh + 70
    p.append(rect(36, py, W - 72, 58, fill="#eef2ff", stroke=NEG, sw=1.4, rx=10))
    stages = ["сіре / HSV", "поріг → маска", "морфологія", "чиста маска"]
    n = len(stages)
    gap = 18
    sw_ = (W - 72 - 2 * 24 - (n - 1) * gap) / n
    for i, s in enumerate(stages):
        sx = 36 + 24 + i * (sw_ + gap)
        p.append(rect(sx, py + 9, sw_, 40, fill="#ffffff", stroke=NEG, sw=1.3, rx=8))
        p.append(text(sx + sw_ / 2, py + 33, s, size=10, color=NEG, bold=True))
        if i < n - 1:
            p.append(arrow(sx + sw_ + 3, py + 29, sx + sw_ + gap - 3, py + 29, color=INK, sw=1.5))

    p.append(text(W / 2, H - 14,
                  "Спершу поріг ріже кадр на чорне-біле, тоді морфологія прибирає цятки й латає "
                  "дірки — і маска готова до пошуку об'єктів.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "opening-closing.svg"), W, H, *p,
           title="Відкриття і закриття: прибрати й залатати")


# ── otsu-variance: гістограма з двох куп + крива σ²_b(t) з максимумом у долині ─
# Ідея: внизу та сама гістограма (дві купи, долина), угорі — крива міжкласової
# дисперсії σ²_b(t); її вершина припадає точно на долину, де Оцу й ставить поріг.

def fig_otsu_variance():
    W, H = 760, 470
    p = []

    # шість рівнів прикладу зі вставки: n = [0,24,16,0,12,28]
    levels = [0, 24, 16, 0, 12, 28]
    nlev = len(levels)
    # σ²_b(t) для t = 0..4 (нормовано на пік) — порахована в тексті:
    # t=1:1.802  t=2:2.723  t=3:2.723  t=4:2.048 ; крайні майже нуль
    var_t = {0: 0.05, 1: 1.802, 2: 2.723, 3: 2.723, 4: 2.048, 5: 0.05}
    vmax = max(var_t.values())

    # геометрія двох панелей, спільна вісь рівнів
    plot_x = 90
    plot_w = 600
    step = plot_w / float(nlev)              # ширина «слота» рівня

    def col_center(i):
        return plot_x + step * (i + 0.5)

    # ── верхня панель: крива σ²_b(t) ──
    top_y0, top_h = 64, 150
    top_base = top_y0 + top_h
    p.append(text(W / 2, 28, "Міжкласова дисперсія σ²_b(t): вершина — у долині",
                  size=15, color=INK, bold=True))
    p.append(line(plot_x, top_base, plot_x + plot_w, top_base, color=INK, sw=1.4))
    p.append(line(plot_x, top_base, plot_x, top_y0, color=INK, sw=1.4))
    p.append(text(plot_x - 10, top_y0 + 6, "σ²_b", size=11, color=INK, anchor="end", bold=True))

    # лінія кривої по точках t=0..5
    pts = []
    for i in range(nlev):
        cx = col_center(i)
        cy = top_base - (var_t[i] / vmax) * (top_h - 14)
        pts.append((cx, cy))
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=NEG, sw=2.4))
    for i, (cx, cy) in enumerate(pts):
        p.append(circle(cx, cy, 3.4, fill=NEG, stroke="none", sw=0))
    # позначити вершину (t=2..3) і впустити пунктир до спільної осі знизу
    peak_x = col_center(2)
    p.append(line(peak_x, pts[2][1] - 4, peak_x, top_base, color=POS, sw=1.6, dash="4,3"))
    p.append(text(peak_x, pts[2][1] - 10, "максимум σ²_b", size=10.5, color=POS, bold=True))

    # ── нижня панель: гістограма ──
    bot_y0, bot_h = 286, 120
    bot_base = bot_y0 + bot_h
    hmax = float(max(levels))
    p.append(text(W / 2, bot_y0 - 14, "Гістограма яскравостей: дві купи й долина",
                  size=13, color=INK, bold=True))
    p.append(line(plot_x, bot_base, plot_x + plot_w, bot_base, color=INK, sw=1.4))
    for i, c in enumerate(levels):
        cx = col_center(i)
        bw = step * 0.62
        if c > 0:
            hgt = (c / hmax) * (bot_h - 10)
            p.append(rect(cx - bw / 2, bot_base - hgt, bw, hgt,
                          fill="#94a3b8", stroke="none", sw=0, rx=3))
        p.append(text(cx, bot_base + 16, str(i), size=10, color=MUTED))   # підпис рівня

    # спільний поріг: пунктир крізь долину (рівень 3) на обох панелях
    thr_x = plot_x + step * 3.0              # межа між рівнем 2 і 3 (поріг t=2..3)
    p.append(line(thr_x, top_y0, thr_x, bot_base, color=POS, sw=1.6, dash="2,4"))
    p.append(text(thr_x + 4, bot_base - bot_h - 4, "поріг Оцу", size=10, color=POS,
                  anchor="start", bold=True))
    p.append(text(plot_x + step * 1.5, bot_base + 32, "тло (темна купа)", size=9.5, color=MUTED))
    p.append(text(plot_x + step * 4.5, bot_base + 32, "об'єкт (світла купа)", size=9.5, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Дисперсія мала на краях (купа недорізана) і сягає вершини над долиною — "
                  "там і стає поріг.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "otsu-variance.svg"), W, H, *p,
           title=None)


# ── adaptive-mean-gauss: рівномірне vs Гауссове локальне середнє ───────────────
# Ідея: біля різкого перепаду яскравості mean-поріг «пливе» (важить далекі
# пікселі), Гаусс притишує далеких — край чіткіший, дрібні штрихи цілі.

def fig_adaptive_mean_gauss():
    W, H = 820, 372
    p = []
    bw, bh = 220, 150
    ys = 78
    xs = [40, 300, 560]

    def scene(x):
        # фон: світла ліва половина, темна права — різкий перепад посередині
        p.append(rect(x, ys, bw / 2, bh, fill="#c8c8c8", stroke="none", sw=0))
        p.append(rect(x + bw / 2, ys, bw / 2, bh, fill="#3a3a3a", stroke="none", sw=0))
        p.append(rect(x, ys, bw, bh, fill="none", stroke=INK, sw=1.2, rx=8))
        # тонкий напис (штрихи) поверх — на світлому темний, на темному світлий
        for k in range(5):
            sx = x + 22 + k * (bw - 44) / 4.0
            col = "#222222" if sx < x + bw / 2 else "#dddddd"
            p.append(rect(sx, ys + bh / 2 - 26, 4, 52, fill=col, stroke="none", sw=0, rx=1))

    def result(x, kind):
        # вихід порога: чорне тло, білі штрихи; mean «пливе» біля перепаду
        p.append(rect(x, ys, bw, bh, fill="#000000", stroke=INK, sw=1.2, rx=8))
        for k in range(5):
            sx = x + 22 + k * (bw - 44) / 4.0
            near = abs(sx - (x + bw / 2))           # відстань до перепаду
            if kind == "mean" and near < 30:
                # біля перепаду штрих розмитий/обрізаний — «пливе»
                p.append(rect(sx, ys + bh / 2 - 14, 4, 28, fill="#9a9a9a", stroke="none", sw=0, rx=1))
            else:
                p.append(rect(sx, ys + bh / 2 - 26, 4, 52, fill="#ffffff", stroke="none", sw=0, rx=1))
        # маркер перепаду
        p.append(line(x + bw / 2, ys, x + bw / 2, ys + bh, color=POS, sw=1.2, dash="3,3"))

    scene(xs[0])
    p.append(text(xs[0] + bw / 2, ys + bh + 20, "шматок кадру", size=11, color=INK, bold=True))
    p.append(text(xs[0] + bw / 2, ys + bh + 36, "тонкі штрихи, різкий перепад тла", size=9, color=MUTED))

    result(xs[1], "mean")
    p.append(text(xs[1] + bw / 2, ys + bh + 20, "рівномірний (mean)", size=11, color=NEG, bold=True))
    p.append(text(xs[1] + bw / 2, ys + bh + 36, "біля перепаду край «пливе»", size=9, color=MUTED))

    result(xs[2], "gauss")
    p.append(text(xs[2] + bw / 2, ys + bh + 20, "Гауссів (зважений)", size=11, color=FIELD, bold=True))
    p.append(text(xs[2] + bw / 2, ys + bh + 36, "край чіткий, штрихи цілі", size=9, color=MUTED))

    p.append(arrow(xs[0] + bw + 4, ys + bh / 2, xs[1] - 4, ys + bh / 2, color=NEG, sw=1.7))
    p.append(arrow(xs[1] + bw + 4, ys + bh / 2, xs[2] - 4, ys + bh / 2, color=FIELD, sw=1.7))

    p.append(text(W / 2, H - 14,
                  "Mean важить усіх сусідів однаково, тож біля перепаду поріг зміщується; "
                  "Гаусс притишує далеких — край тримається.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "adaptive-mean-gauss.svg"), W, H, *p,
           title="Рівномірний vs Гауссів адаптивний поріг")


# ── hit-or-miss: до/після перетворення влучання-промаху (виявлення кутів) ──────
# Ідея: HMT лишає тільки пікселі, навколо яких збігся повний шаблон «біле тут
# ТА чорне там» — так із суцільного об'єкта виокремлюються самі кути.

def fig_hit_or_miss():
    W, H = 720, 372
    p = []
    cell = 26
    cols, rows = 7, 7
    grid_w = cols * cell

    # об'єкт-«сходинка» з виразними кутами (1 — біле)
    obj = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    # «кути» — опуклі кутові пікселі об'єкта (виокремлені шаблоном)
    corners = [(1, 1), (1, 3), (3, 5), (5, 5), (5, 3), (3, 1)]

    def draw_grid(x0, y0, mark=None):
        for r in range(rows):
            for c in range(cols):
                xx = x0 + c * cell
                yy = y0 + r * cell
                if mark is not None:
                    fill = "#facc15" if (r, c) in mark else "#0f172a"
                    if obj[r][c] == 0:
                        fill = "#0f172a"
                else:
                    fill = "#ffffff" if obj[r][c] else "#0f172a"
                p.append(rect(xx, yy, cell - 1.5, cell - 1.5, fill=fill,
                              stroke="#334155", sw=0.7, rx=2))

    y0 = 80
    x_in = 56
    x_out = x_in + grid_w + 96

    p.append(text(x_in + grid_w / 2, y0 - 16, "вхід: суцільний об'єкт", size=12, color=INK, bold=True))
    draw_grid(x_in, y0)

    p.append(text(x_out + grid_w / 2, y0 - 16, "після hit-or-miss: самі кути", size=12, color=INK, bold=True))
    draw_grid(x_out, y0, mark=corners)

    p.append(arrow(x_in + grid_w + 14, y0 + grid_w / 2,
                   x_out - 14, y0 + grid_w / 2, color=POS, sw=2.2))
    p.append(text((x_in + grid_w + x_out) / 2, y0 + grid_w / 2 - 12, "шаблон",
                  size=10.5, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "Шаблон вимагає білого в одних позиціях і чорного в інших — лишаються тільки "
                  "пікселі точної форми (кути).",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "hit-or-miss.svg"), W, H, *p,
           title="Перетворення влучання-промаху: виявлення кутів")


if __name__ == "__main__":
    fig_thresholding()
    fig_adaptive()
    fig_erosion_dilation()
    fig_opening_closing()
    fig_otsu_variance()
    fig_adaptive_mean_gauss()
    fig_hit_or_miss()
    print("OK: figures written to", OUT)
