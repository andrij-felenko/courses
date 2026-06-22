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


if __name__ == "__main__":
    fig_thresholding()
    fig_adaptive()
    fig_erosion_dilation()
    fig_opening_closing()
    print("OK: figures written to", OUT)
