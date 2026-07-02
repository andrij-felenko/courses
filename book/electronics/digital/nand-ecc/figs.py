# -*- coding: utf-8 -*-
"""Фігури до теми «ECC у NAND-флеші».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

DATA = "#2457d6"   # біти даних (= NEG)
PAR  = "#c0392b"   # перевірні біти (= POS)
OVER = "#e67e22"   # зона перекриття рівнів


def _bell(cx, base_y, spread, height, color, sw=1.8):
    """Крива-дзвіночок (розкид заряду) як polyline; cx — центр, base_y — низ."""
    pts = []
    for k in range(-24, 25):
        x = cx + k * (spread / 24.0)
        t = k / 24.0
        y = base_y - height * math.exp(-4.0 * t * t)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── 1. Рівні заряду: SLC vs TLC, вузькі щілини й перекриття ───────────────────
def fig_levels_overlap():
    W, H = 760, 380
    f = [text(W / 2, 26, "Більше рівнів у той самий діапазон → вужчі щілини → помилки",
              size=15, bold=True)]

    # спільна вісь-підпис
    f.append(text(W / 2, H - 14, "вісь: заряд у комірці (мало → багато)",
                  size=11, color=MUTED, italic=True))

    # --- ліва панель: SLC (2 рівні) ---
    Lx, Ly, Lw = 60, 300, 300
    f.append(text(Lx + Lw / 2, 60, "SLC — 2 рівні", size=13, color=FIELD, bold=True))
    f.append(line(Lx, Ly, Lx + Lw, Ly, color=INK, sw=1.5))
    for i, cx in enumerate((Lx + 70, Lx + 230)):
        f.append(_bell(cx, Ly, 55, 150, DATA))
        f.append(text(cx, Ly + 20, "%d" % i, size=12, color=DATA, bold=True))
    f.append(text(Lx + Lw / 2, 150, "широка щілина", size=10.5, color=FIELD))
    f.append(text(Lx + Lw / 2, 168, "хвости не сходяться", size=10.5, color=FIELD))

    # --- права панель: TLC (8 рівнів) ---
    Rx, Ry, Rw = 400, 300, 300
    f.append(text(Rx + Rw / 2, 60, "TLC — 8 рівнів", size=13, color=POS, bold=True))
    f.append(line(Rx, Ry, Rx + Rw, Ry, color=INK, sw=1.5))
    step = Rw / 8.0
    for i in range(8):
        cx = Rx + step * (i + 0.5)
        f.append(_bell(cx, Ry, 20, 120, DATA if i % 2 == 0 else NEG, sw=1.4))
    # заштрихована зона перекриття між двома сусідами (приклад)
    ox = Rx + step * 4
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
             'opacity="0.28"/>' % (ox - 8, Ry - 60, 16, 60, OVER))
    f.append(arrow(ox + 60, 120, ox + 6, Ry - 55, color=OVER, sw=1.8))
    tb = textbox(ox + 120, 108, "хвости\nналазять →\nбіти збиваються",
                 size=10, color=OVER, stroke=OVER, fill=BG)
    f.append(tb[0])

    render(os.path.join(IMG, "levels-overlap.svg"), W, H, *f)


# ── 2. Синдром: перевірні біти накривають підмножини, синдром = номер ─────────
def fig_syndrome():
    W, H = 760, 400
    f = [text(W / 2, 26, "Синдром = двійковий номер зіпсованої позиції",
              size=15, bold=True)]

    # 7 позицій коду в ряд
    n = 7
    bx0, by, bw, gap = 150, 120, 56, 12
    kinds = ["p", "p", "d", "p", "d", "d", "d"]   # позиції 1..7: степені 2 — перевірні
    dcount = 0
    labels = []
    for i in range(n):
        pos = i + 1
        if kinds[i] == "p":
            labels.append("p%d" % pos)
        else:
            labels.append("d%d" % dcount); dcount += 1
    xs = [bx0 + i * (bw + gap) for i in range(n)]
    for i in range(n):
        col = PAR if kinds[i] == "p" else DATA
        fillc = "#fdecea" if kinds[i] == "p" else "#eaf0fd"
        f.append(rect(xs[i], by, bw, 40, fill=fillc, stroke=col, sw=1.8))
        f.append(text(xs[i] + bw / 2, by + 26, labels[i], size=12, color=col, bold=True))
        f.append(text(xs[i] + bw / 2, by - 8, "%d" % (i + 1), size=10, color=MUTED))

    # три дуги-підмножини під рядом
    subsets = [([1, 3, 5, 7], "p₁: поз. 1·3·5·7", 210, PAR),
               ([2, 3, 6, 7], "p₂: поз. 2·3·6·7", 250, "#8e44ad"),
               ([4, 5, 6, 7], "p₄: поз. 4·5·6·7", 290, NEG)]
    for members, cap, ay, col in subsets:
        mxs = [xs[p - 1] + bw / 2 for p in members]
        x1, x2 = min(mxs), max(mxs)
        f.append(line(x1, ay, x2, ay, color=col, sw=1.8))
        for mx in mxs:
            f.append(line(mx, by + 40, mx, ay, color=col, sw=1.2, dash="3,3"))
            f.append(circle(mx, ay, 3.2, fill=col, stroke=col))
        f.append(text(x2 + 14, ay + 4, cap, size=10, color=col, anchor="start"))

    # приклад унизу
    f.append(line(60, 330, W - 60, 330, color=MUTED, sw=1, dash="4,4"))
    f.append(text(bx0, 356, "збився біт на позиції 5  (5 = 101₂)",
                  size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(bx0, 378,
                  "спрацюють p₁ і p₄ (5 у їхніх підмножинах) → синдром p₄p₂p₁ = 101 = 5",
                  size=11, color=OVER, anchor="start"))

    render(os.path.join(IMG, "syndrome.svg"), W, H, *f)


# ── 3. Сторінка NAND: дані + службова ділянка (OOB) під перевірні біти ────────
def fig_page_oob():
    W, H = 760, 340
    f = [text(W / 2, 26, "Сторінка NAND: перевірні біти ECC живуть у службовій ділянці",
              size=15, bold=True)]

    top = 70
    dx, dw = 50, 520          # ділянка даних
    ox, ow = dx + dw + 10, 150  # службова
    ph = 120

    # рамка всієї сторінки
    f.append(text(W / 2, 52, "одна сторінка", size=11, color=MUTED))

    # чотири шматки даних
    chunk = dw / 4.0
    for i in range(4):
        cx = dx + i * chunk
        f.append(rect(cx + 2, top, chunk - 4, ph, fill="#eaf0fd", stroke=DATA, sw=1.6))
        f.append(text(cx + chunk / 2, top + ph / 2 - 6, "дані", size=12, color=DATA, bold=True))
        f.append(text(cx + chunk / 2, top + ph / 2 + 14, "512 Б", size=10.5, color=DATA))
    f.append(text(dx + dw / 2, top - 12, "ділянка даних — 2048 Б (4 шматки по 512)",
                  size=11, color=DATA, bold=True))

    # службова ділянка
    f.append(rect(ox, top, ow, ph, fill="#fdecea", stroke=PAR, sw=1.8))
    f.append(text(ox + ow / 2, top - 12, "службова (OOB)", size=11, color=PAR, bold=True))
    f.append(mtext(ox + ow / 2, top + 30, ["перевірні", "біти ECC", "+ мітки", "дефектів"],
                   size=11, color=PAR))
    f.append(text(ox + ow / 2, top + ph + 4, "64 Б", size=10.5, color=PAR))

    # стрілки: кожен шматок → службова
    for i in range(4):
        cx = dx + i * chunk + chunk / 2
        f.append(arrow(cx, top + ph + 6, ox + ow / 2 - 30, top + ph - 8, color=MUTED, sw=1.2))

    # висновок-бюджет
    y = top + ph + 60
    f.append(line(50, y - 16, W - 50, y - 16, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, y + 2,
                  "стеля корекції = скільки перевірних байтів влазить у службову ділянку",
                  size=12, color=INK, bold=True))
    f.append(text(W / 2, y + 24,
                  "тісніша флеш → більше помилок → більше перевірних → ділянка переповнюється",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "page-oob.svg"), W, H, *f)


# ── 4. GF(2³) як годинник степенів α: множення = додавання показників ─────────
def fig_gf_clock():
    W, H = 760, 430
    f = [text(W / 2, 26, "GF(2³): сім ненульових елементів — це степені α по колу",
              size=15, bold=True)]
    f.append(text(W / 2, 48, "правило поля: α³ = α + 1  (з примітивного x³ + x + 1)",
                  size=11.5, color=MUTED, italic=True))

    # генеруємо GF(2^3): степені α за α^3 = α + 1  →  3-бітові вектори
    m = 3
    poly = 0b1011           # x^3 + x + 1
    exp_to_vec = [1]        # α^0 = 1
    v = 1
    for _ in range(1, 2 ** m - 1):
        v <<= 1
        if v & (1 << m):
            v ^= poly
        exp_to_vec.append(v & ((1 << m) - 1))

    def bits(x):
        return "".join(str((x >> b) & 1) for b in range(m - 1, -1, -1))

    cx, cy, R = W / 2, 250, 130
    N = 2 ** m - 1
    # коло
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="3,4"/>' % (cx, cy, R, MUTED))
    for i in range(N):
        ang = -math.pi / 2 + 2 * math.pi * i / N     # від верху за годинниковою
        px = cx + R * math.cos(ang)
        py = cy + R * math.sin(ang)
        f.append(circle(px, py, 20, fill="#eaf0fd", stroke=NEG, sw=1.8))
        lbl = "1" if i == 0 else ("α" if i == 1 else "α%s" % "".join(
            "⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(i)))
        f.append(text(px, py - 1, lbl, size=12.5, color=NEG, bold=True))
        f.append(text(px, py + 13, bits(exp_to_vec[i]), size=8.5, color=MUTED))

    # центр: правило множення
    tb = textbox(cx, cy, "αⁱ · αʲ = α^((i+j) mod 7)\nмноження = крок по колу",
                 size=11, color=FIELD, stroke=FIELD, fill=BG, bold=False)
    f.append(tb[0])

    # приклад збоку
    f.append(text(60, H - 40, "приклад:  α⁵ · α⁴ = α⁹ = α⁹⁻⁷ = α²   (обійшли коло раз)",
                  size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(60, H - 20,
                  "у бітах: 111 · 110 без таблиці — важко; по колу — просто 5+4",
                  size=10.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "gf-clock.svg"), W, H, *f)


# ── 5. Конвеєр декодування BCH: синдроми → локатор → корені → перевертання ─────
def fig_bch_pipeline():
    W, H = 780, 340
    f = [text(W / 2, 26, "Декодування BCH: від зіпсованого слова до полагодженого",
              size=15, bold=True)]

    boxes = [
        ("прочитане\nслово r(x)", "дані + parity,\nз помилками", NEG, "#eaf0fd"),
        ("синдроми\nS₁…S₂ₜ", "Sⱼ = r(αʲ)\nпідстановки", PAR, "#fdecea"),
        ("локатор\nσ(x)", "Берлекемп–\nМессі", "#8e44ad", "#f3eafd"),
        ("корені σ(x)", "пошук Ченя:\nперебір αⁱ", FIELD, "#eafaf0"),
        ("перевертання\nбітів", "y(x) = r(x)\n⊕ помилки", INK, FILL),
    ]
    n = len(boxes)
    bw, bh, gap = 118, 74, 22
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = 120
    for i, (title_t, sub, col, fillc) in enumerate(boxes):
        bx = x0 + i * (bw + gap)
        f.append(rect(bx, y, bw, bh, fill=fillc, stroke=col, sw=1.9))
        f.append(mtext(bx + bw / 2, y + 24, title_t.split("\n"), size=11.5,
                       color=col, bold=True, lh=1.15))
        yy = y + 24 + (title_t.count("\n") + 1) * 13
        f.append(mtext(bx + bw / 2, yy, sub.split("\n"), size=9.5, color=MUTED, lh=1.15))
        if i < n - 1:
            f.append(arrow(bx + bw + 2, y + bh / 2, bx + bw + gap - 2, y + bh / 2,
                           color=INK, sw=1.8))

    # підписи-стадії під конвеєром
    f.append(line(x0, y + bh + 30, x0 + total, y + bh + 30, color=MUTED, sw=1, dash="4,4"))
    f.append(text(x0 + total / 2, y + bh + 54,
                  "чому саме αʲ: помилка лишає слід тільки якщо перевіряти в коренях g(x)",
                  size=11.5, color=INK, bold=True))
    f.append(text(x0 + total / 2, y + bh + 76,
                  "нуль синдромів → чисто; ненульові → σ(x) кодує, ДЕ саме сидять помилки",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(x0 + total / 2, y + bh + 98,
                  "коренів σ(x) рівно стільки, скільки помилок (доки їх ≤ t)",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "bch-pipeline.svg"), W, H, *f)


# ── 6. Тихі роки: винахід 1947 → патент → публікація 1950 (для hist-вставки) ──
def fig_hamming_timeline():
    W, H = 780, 300
    f = [text(W / 2, 26, "Код був готовий 1947-го — а вийшов друком аж 1950-го",
              size=15, bold=True)]

    # вісь часу
    ax0, ax1, ay = 70, W - 70, 150
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append(arrow(ax1 - 2, ay, ax1 + 14, ay, color=INK, sw=2))

    years = [1947, 1948, 1949, 1950]
    def xof(yr):
        return ax0 + (ax1 - ax0) * (yr - 1947) / 3.0
    for yr in years:
        x = xof(yr)
        f.append(line(x, ay - 6, x, ay + 6, color=INK, sw=2))
        f.append(text(x, ay + 24, str(yr), size=12.5, color=INK, bold=True))

    # заштрихована «тиша» 1947→1950 через патент
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
             'opacity="0.14"/>' % (xof(1947), ay - 40, xof(1950) - xof(1947), 26, PAR))
    f.append(text((xof(1947) + xof(1950)) / 2, ay - 22,
                  "мовчання заради патенту", size=10.5, color=PAR, italic=True))

    # події — підписи над і під віссю, щоб не налазили
    def note(yr, above, lines, col):
        x = xof(yr)
        cy = ay - 78 if above else ay + 66
        tb = textbox(x, cy, "\n".join(lines), size=10, color=col,
                     stroke=col, fill=BG)
        # тримати рамку в межах полотна
        _, w, _ = tb
        x = min(max(x, ax0 + w / 2 - 8), ax1 - w / 2 + 8)
        tb = textbox(x, cy, "\n".join(lines), size=10, color=col, stroke=col, fill=BG)
        anchor_y = cy + (textbox(x, cy, "\n".join(lines), size=10)[2] / 2 if not above
                         else -textbox(x, cy, "\n".join(lines), size=10)[2] / 2)
        return tb[0] + line(x, anchor_y, xof(yr), ay, color=col, sw=1.1, dash="3,3")

    f.append(note(1947, True,  ["внутрішня записка", "Bell Labs:", "код (7,4) готовий"], NEG))
    f.append(note(1948, False, ["Шеннон друкує код", "у своїй статті", "й приписує Гаммінгу"], FIELD))
    f.append(note(1949, True,  ["заявка на патент;", "Ґолей незалежно", "друкує свій код"], "#8e44ad"))
    f.append(note(1950, False, ["стаття в BSTJ", "(кв. 1950):", "код нарешті виходить"], PAR))

    render(os.path.join(IMG, "hamming-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_levels_overlap()
    fig_syndrome()
    fig_page_oob()
    fig_gf_clock()
    fig_bch_pipeline()
    fig_hamming_timeline()
    print("OK: 6 figures ->", IMG)
