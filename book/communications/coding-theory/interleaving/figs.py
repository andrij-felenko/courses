# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Семантичні кольори (єдині на всі фігури теми)
BAD_F, BAD_S = "#fdeceb", POS            # биті символи — гарячі
# чотири блоки — чотири спокійні відтінки (щоб око бачило перегрупування)
BLOCK = [("#eafaee", FIELD),             # A — зелений
         ("#eaf0fd", NEG),               # B — синій
         ("#fdf3e0", "#b8860b"),         # C — бурштин
         ("#f3eafd", "#7c3aed")]         # D — фіолет
BLETTER = ["A", "B", "C", "D"]
SUB = ["₁", "₂", "₃", "₄"]


def polyline(pts, color, sw=3.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── spread: той самий пакет у двох порядках ───────────────────────────────────
def fig_spread():
    W, H = 940, 486
    p = []
    cw, gap = 46.0, 6.0
    pitch = cw + gap
    x0 = 54.0
    N = 16
    burst = {0, 1, 2, 3}                  # пакет — 4 символи каналу поспіль

    def panel(y, order, title):
        # order: список (блок 0..3, індекс-у-блоці 0..3)
        out = [text(20, y - 20, title, size=12.5, color=INK, anchor="start", bold=True)]
        counts = [0, 0, 0, 0]
        for i, (blk, idx) in enumerate(order):
            bx = x0 + i * pitch
            f, s = BLOCK[blk]
            hit = i in burst
            out.append(rect(bx, y, cw, 40, fill=f, stroke=s, sw=1.4, rx=4))
            if hit:
                out.append(rect(bx - 1.5, y - 1.5, cw + 3, 43, fill="none", stroke=POS, sw=2.8, rx=5))
                counts[blk] += 1
            out.append(text(bx + cw / 2, y + 25, BLETTER[blk] + SUB[idx], size=13,
                            color=(POS if hit else s), bold=True))
        # дужка пакета під битими комірками
        bx0, bx1 = x0, x0 + 4 * pitch - gap
        by = y + 52
        out.append(line(bx0, by, bx1, by, color=POS, sw=2.2))
        out.append(line(bx0, by, bx0, by - 6, color=POS, sw=2.2))
        out.append(line(bx1, by, bx1, by - 6, color=POS, sw=2.2))
        out.append(text((bx0 + bx1) / 2, by + 18, "пакет — 4 символи каналу поспіль",
                        size=11.5, color=POS, anchor="middle", bold=True))
        return out, counts

    # верх — природний порядок
    yA = 78
    ordA = [(b, i) for b in range(4) for i in range(4)]      # AAAA BBBB CCCC DDDD
    pa, cntA = panel(yA, ordA, "без перемішування: символи блоків ідуть у канал підряд")
    p += pa

    # низ — перемішаний порядок
    yB = 300
    ordB = [(b, i) for i in range(4) for b in range(4)]      # ABCD ABCD ABCD ABCD
    pb, cntB = panel(yB, ordB, "з перемішуванням: сусіди в каналі — з різних блоків")
    p += pb

    # підсумкові рамки після зворотного розкладання
    def summary(y, counts, note_col):
        out = [text(20, y - 6, "після розкладання назад — помилок на блок:",
                    size=11.5, color=MUTED, anchor="start")]
        bw, bg = 118, 20
        total = 4 * bw + 3 * bg
        sx = (W - total) / 2 + 40
        for b in range(4):
            k = counts[b]
            ok = k <= 1
            bx = sx + b * (bw + bg)
            col = FIELD if ok else POS
            out.append(rect(bx, y + 6, bw, 34, fill=(col + "12"), stroke=col, sw=1.8, rx=6))
            out.append(text(bx + bw / 2, y + 28,
                            "%s: %d %s" % (BLETTER[b], k, "✓" if ok else "✗"),
                            size=12.5, color=col, bold=True))
        return out

    p += summary(yA + 92, cntA, POS)
    p += summary(yB + 92, cntB, FIELD)

    p.append(text(W / 2, 474, "Символи ті самі, помилок стільки ж — змінився лише ПОРЯДОК. "
                              "Пакет із чотирьох обертається на чотири поодинокі похибки.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "spread.svg"), W, H, *p)


# ── block-matrix: пишемо рядками, читаємо стовпцями ───────────────────────────
def fig_block_matrix():
    W, H = 900, 470
    p = []
    R, C = 4, 8
    cw, chh = 52.0, 42.0
    gx, gy = 196.0, 118.0
    burst_cols = {3, 4}                    # пакет накрив 2 сусідні стовпці

    # заголовок дії згори
    p.append(text(gx, gy - 40, "читаємо СТОВПЦЯМИ ↓  (стовпець за стовпцем)  →  у канал",
                  size=12.5, color=INK, anchor="start", bold=True))
    # стрілка «пишемо рядками» зліва
    p.append(text(70, gy - 40, "пишемо", size=12, color=INK, anchor="start", bold=True))
    p.append(text(70, gy - 24, "рядками:", size=12, color=INK, anchor="start", bold=True))
    p.append(arrow(150, gy + 4, 150, gy + R * chh - 8, color=INK, sw=2))

    # матриця: порядок читання стовпцями — дрібний номер у комірці
    for r in range(R):
        f, s = BLOCK[r]
        p.append(text(gx - 12, gy + r * chh + chh / 2 + 4, "слово %s" % BLETTER[r],
                      size=11.5, color=s, anchor="end", bold=True))
        for c in range(C):
            bx, by = gx + c * cw, gy + r * chh
            hit = c in burst_cols
            p.append(rect(bx + 1.5, by + 1.5, cw - 3, chh - 3, fill=f, stroke=s, sw=1.3, rx=3))
            if hit:
                p.append(rect(bx + 0.5, by + 0.5, cw - 1, chh - 1, fill="none", stroke=POS, sw=2.6, rx=3))
            order_no = c * R + r + 1       # позиція символу в каналі
            p.append(text(bx + cw / 2, by + chh / 2 + 4, str(order_no), size=12,
                          color=(POS if hit else MUTED), bold=hit))

    # права анотація: у кожен рядок — по 2
    rx = gx + C * cw + 16
    for r in range(R):
        cy = gy + r * chh + chh / 2 + 4
        p.append(text(rx, cy, "→ 2 ✓", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(rx, gy + R * chh + 22, "по ⌈b / D⌉ = 2", size=11.5, color=FIELD, anchor="start", bold=True))
    p.append(text(rx, gy + R * chh + 40, "на кожне слово", size=11.5, color=FIELD, anchor="start"))

    # позначка пакета (стовпці 3–4)
    b0 = gx + 3 * cw
    b1 = gx + 5 * cw
    p.append(line(b0, gy + R * chh + 10, b1, gy + R * chh + 10, color=POS, sw=2.2))
    p.append(line(b0, gy + R * chh + 10, b0, gy + R * chh + 3, color=POS, sw=2.2))
    p.append(line(b1, gy + R * chh + 10, b1, gy + R * chh + 3, color=POS, sw=2.2))
    p.append(text((b0 + b1) / 2, gy + R * chh + 30, "пакет — 2 стовпці = 8 символів у каналі поспіль",
                  size=11.5, color=POS, bold=True))

    # ключ знизу
    p.append(text(W / 2, 420, "Будь-які D символів поспіль у каналі — з D РІЗНИХ слів. "
                              "Тому пакет розсипається по ⌈b / D⌉ на слово.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 444, "Глибший перемішувач (більше рядків D) розтягує той самий пакет ще тонше.",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "block-matrix.svg"), W, H, *p)


# ── depth-tradeoff: глибина піднімає і стійкість, і затримку ───────────────────
def fig_depth_tradeoff():
    W, H = 880, 470
    p = []
    ox, oy = 108, 372
    xr, ytop = 812, 84
    Dmax = 12

    def X(d):
        return ox + d * (xr - ox) / Dmax

    def Y(frac):                            # frac 0..1 висоти поля
        return oy - frac * (oy - ytop)

    # осі
    p.append(arrow(ox, oy, ox, ytop - 6, color=INK, sw=2))
    p.append(arrow(ox, oy, xr + 6, oy, color=INK, sw=2))
    p.append(text(ox - 10, ytop + 4, "величина →", size=11.5, color=INK, anchor="end", bold=True))
    p.append(text(xr, oy + 30, "глибина перемішування D →", size=12, color=INK, anchor="end", bold=True))

    # поділки по осі D
    for d in range(0, Dmax + 1, 2):
        p.append(line(X(d), oy, X(d), oy + 6, color=INK, sw=1.3))
        p.append(text(X(d), oy + 22, str(d), size=11, color=MUTED))

    # дві прямі з початку координат (обидві ∝ D)
    ptsG = [(X(d), Y(0.045 * d)) for d in range(0, Dmax + 1)]     # посильний пакет ∝ D·t
    ptsA = [(X(d), Y(0.072 * d)) for d in range(0, Dmax + 1)]     # затримка ∝ 2·D·n
    p.append(polyline(ptsA, "#b8860b", sw=3.2))
    p.append(polyline(ptsG, FIELD, sw=3.2))

    # підписи кінців ліній — праворуч, у вільній зоні
    p.append(text(X(Dmax) + 6, Y(0.072 * Dmax), "затримка", size=12, color="#b8860b", anchor="start", bold=True))
    p.append(text(X(Dmax) + 6, Y(0.072 * Dmax) + 16, "≈ 2·D·n  (плата)", size=11, color="#b8860b", anchor="start"))
    p.append(text(X(Dmax) + 6, Y(0.045 * Dmax), "посильний пакет", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(X(Dmax) + 6, Y(0.045 * Dmax) + 16, "= D·t  (виграш)", size=11, color=FIELD, anchor="start"))

    # легенда-ключ у вільному верхньому лівому куті
    p.append(text(ox + 14, ytop + 20, "обидві ростуть лінійно з глибиною —", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(ox + 14, ytop + 38, "стійкість купують затримкою, один до одного", size=11.5, color=INK, anchor="start"))

    # зони обміну під віссю
    p.append(text(X(2.5), oy + 46, "← скромна: голос, керування", size=11.5, color=MUTED, anchor="middle"))
    p.append(text(X(9.5), oy + 46, "щедра: сховище, стріми →", size=11.5, color=MUTED, anchor="middle"))

    p.append(text(W / 2, 440, "«Правильної» глибини немає — є точка, яку обирають під задачу: "
                              "глибоко, де затримка дешева; скромно, де дорога.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "depth-tradeoff.svg"), W, H, *p)


# ── timeline: ідея → доведений оптимум → масова система ───────────────────────
def fig_timeline():
    W, H = 1100, 340
    p = []
    n = 6
    cw, gap = 160.0, 16.0
    x0 = 40.0

    def cardx(i):
        return x0 + i * (cw + gap)

    def cx(i):
        return cardx(i) + cw / 2

    spine_y = 104.0

    # три фази: підпис, перша й остання картка фази, заливка, обвід
    phases = [("прийом без теорії", 0, 1, "#fdf3e0", "#b8860b"),
              ("оптимум доведено",  2, 3, "#eaf0fd", NEG),
              ("масова технологія", 4, 5, "#eafaee", FIELD)]
    for ptitle, i0, i1, pf, ps in phases:
        bx0 = cardx(i0) - 8
        bx1 = cardx(i1) + cw + 8
        p.append(rect(bx0, 44, bx1 - bx0, 212, fill=pf, stroke=ps, sw=1.4, rx=10))
        p.append(text((bx0 + bx1) / 2, 68, ptitle, size=13.5, color=ps, bold=True))

    # хребет часу крізь віхи
    p.append(line(cx(0), spine_y, cx(n - 1), spine_y, color=INK, sw=2.4))

    cards = [
        ("1960",    "Рід–Соломон",   ["код проти", "рідкого шуму"], 0),
        ("1960-ті", "блокове",       ["перемішування —", "прийом без теорії"], 0),
        ("1970",    "J. L. Ramsey",  ["оптимум:", "мінімум пам'яті", "й затримки"], 1),
        ("1971",    "G. D. Forney",  ["ідеальний", "пакетний канал,", "теж оптимум"], 1),
        ("1980",    "CIRC · CD",     ["Philips + Sony:", "згорткове", "перемішування"], 2),
        ("1982",    "Sony CDP-101",  ["перший програвач —", "у кожній хаті"], 2),
    ]
    pcol = ["#b8860b", NEG, FIELD]
    for i, (yr, ttl, notes, ph) in enumerate(cards):
        col = pcol[ph]
        X = cx(i)
        p.append(circle(X, spine_y, 7, fill=col, stroke=BG, sw=2))
        p.append(text(X, 132, yr, size=15, color=col, bold=True))
        cxx = cardx(i)
        p.append(rect(cxx, 148, cw, 94, fill=BG, stroke=col, sw=1.6, rx=8))
        p.append(text(X, 172, ttl, size=12, color=INK, bold=True))
        for j, ln in enumerate(notes):
            p.append(text(X, 194 + j * 15, ln, size=11, color=MUTED))

    p.append(text(W / 2, 296, "Ідея «перемішати, щоб розбити згусток» жила в 1960-х як фольклор інженерів.",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 318, "Ramsey і Forney довели її найдешевшу форму — а компакт-диск за десять років виніс її в кожну вітальню.",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Двадцять років: від теорії оптимуму до звуку без тріску")


# ── proj-conv-stagger: сходинка ліній затримки Форні (перемішувач + зворотний) ──
def _branch_stack(p, y0, lengths, title, endlabel):
    Nn = len(lengths)
    cw, chh, cgap = 38.0, 28.0, 9.0
    pitch = cw + cgap
    row = 56.0
    xlab = 132.0            # правий край підписів гілок
    xin = 182.0            # вхідний комутатор
    xc0 = 224.0            # перша комірка
    maxlen = max(lengths) if max(lengths) > 0 else 1
    xout = xc0 + maxlen * pitch + 40      # вихідний комутатор (вирівняний)
    ytop, ybot = y0, y0 + (Nn - 1) * row
    ymid = (ytop + ybot) / 2
    p.append(text(40, y0 - 30, title, size=13, color=INK, anchor="start", bold=True))
    # комутаторні шини
    p.append(line(xin, ytop - 14, xin, ybot + 14, color=MUTED, sw=2.6))
    p.append(line(xout, ytop - 14, xout, ybot + 14, color=MUTED, sw=2.6))
    p.append(text(xin, ytop - 22, "↻", size=15, color=MUTED))
    p.append(text(xout, ytop - 22, "↻", size=15, color=MUTED))
    for i in range(Nn):
        yy = y0 + i * row
        f, s = BLOCK[i % len(BLOCK)]
        p.append(text(xlab, yy - 3, "гілка %d" % i, size=11.5, color=s, anchor="end", bold=True))
        p.append(text(xlab, yy + 14, "%d комір." % lengths[i], size=10, color=MUTED, anchor="end"))
        p.append(line(xin, yy, xc0, yy, color=s, sw=1.8))
        for c in range(lengths[i]):
            bx = xc0 + c * pitch
            p.append(rect(bx, yy - chh / 2, cw, chh, fill=f, stroke=s, sw=1.4, rx=3))
        xafter = xc0 + lengths[i] * pitch
        p.append(line(xafter, yy, xout, yy, color=s, sw=1.8, dash="4,4" if lengths[i] < maxlen else None))
    p.append(arrow(xin - 58, ymid, xin, ymid, color=INK, sw=2))
    p.append(text(xin - 62, ymid - 8, "вхід", size=11, color=INK, anchor="end", bold=True))
    p.append(arrow(xout, ymid, xout + 52, ymid, color=INK, sw=2))
    p.append(text(xout + 58, ymid + 4, endlabel, size=12, color=INK, anchor="start", bold=True))
    return ytop, ybot


def fig_proj_conv_stagger():
    W, H = 1000, 640
    p = []
    Nn, Mm = 4, 1
    il = [i * Mm for i in range(Nn)]            # 0,1,2,3
    dl = [(Nn - 1 - i) * Mm for i in range(Nn)]  # 3,2,1,0
    _branch_stack(p, 96, il,
                  "ПЕРЕМІШУВАЧ Форні — гілка i затримує символ на i·M комірок", "у канал")
    _branch_stack(p, 392, dl,
                  "ЗВОРОТНИЙ — дзеркало: гілка i затримує на (N−1−i)·M комірок", "відновлено")
    tb, w, h = textbox(W / 2, 604,
                       ["затримка гілки i:  i·M (перемішувач) + (N−1−i)·M (зворотний) = (N−1)·M — однакова для КОЖНОГО символа",
                        "пам'ять кожного кінця: M·N·(N−1)/2 комірок — удвічі менше за рівнозначну блокову матрицю"],
                       size=11.5, bold=True, fill="#eafaee", stroke=FIELD, pad=12)
    p.append(tb)
    render(os.path.join(OUT, "proj-conv-stagger.svg"), W, H, *p)


# ── proj-conv-diagonal: перестановка каналу як діагональ + розсіювання пакета ───
def fig_proj_conv_diagonal():
    W, H = 1000, 508
    p = []
    Nn, Mm = 4, 1
    NIN = 16
    def pos(u):
        return u + (u % Nn) * Nn * Mm          # channel[t]=in[t−(t%N)NM] ⇔ u→pos
    positions = [pos(u) for u in range(NIN)]
    TMAX = max(positions) + 1                   # 28
    burst = set(range(8, 16))                   # пакет — 8 сусідніх символів каналу
    gx, gy = 176.0, 118.0
    cwt = (W - gx - 172) / TMAX
    rowh = 20.0

    p.append(text(40, 40, "Згорткова перестановка як діагональ: символ №u каналу лягає в позицію  u + (u mod N)·N·M",
                  size=12.5, color=INK, anchor="start", bold=True))
    # осі
    p.append(text(gx - 12, gy - 26, "позиція в каналі (час) →", size=11, color=INK, anchor="start", bold=True))
    p.append(text(40, gy + NIN * rowh / 2, "вхідний індекс u", size=11, color=INK, anchor="start", bold=True))
    for c in range(0, TMAX + 1, 4):
        x = gx + c * cwt
        p.append(line(x, gy - 6, x, gy + NIN * rowh, color="#e4e7eb", sw=1))
        p.append(text(x, gy - 12, str(c), size=9.5, color=MUTED))

    # смуги слів по y (4 слова по 4 символи)
    for wd in range(4):
        f, s = BLOCK[wd]
        y = gy + wd * 4 * rowh
        p.append(rect(gx - 2, y, TMAX * cwt + 4, 4 * rowh, fill=f + "66", stroke="none", sw=0, rx=2))
        p.append(text(gx - 12, y + 2 * rowh + 4, "слово %s" % BLETTER[wd], size=11, color=s, anchor="end", bold=True))

    # смуга пакета по x
    bx0 = gx + min(burst) * cwt
    bx1 = gx + (max(burst) + 1) * cwt
    p.append(rect(bx0, gy - 6, bx1 - bx0, NIN * rowh + 6, fill=BAD_F, stroke=POS, sw=1.6, rx=3))
    p.append(text((bx0 + bx1) / 2, gy + NIN * rowh + 20, "пакет: 8 сусідніх символів каналу",
                  size=11, color=POS, bold=True))

    # точки перестановки
    from collections import Counter
    per = Counter()
    for u in range(NIN):
        c = positions[u]
        x = gx + (c + 0.5) * cwt
        y = gy + (u + 0.5) * rowh
        hot = c in burst
        f, s = BLOCK[u // 4]
        p.append(circle(x, y, 6.0, fill=(POS if hot else f), stroke=(POS if hot else s), sw=1.6))
        if hot:
            per[u // 4] += 1

    # підсумок по словах праворуч
    rx = gx + TMAX * cwt + 20
    p.append(text(rx, gy + 6, "помилок", size=10.5, color=MUTED, anchor="start"))
    p.append(text(rx, gy + 20, "на слово:", size=10.5, color=MUTED, anchor="start"))
    for wd in range(4):
        k = per.get(wd, 0)
        y = gy + (wd * 4 + 2) * rowh
        p.append(text(rx, y + 4, "%s: %d ✓" % (BLETTER[wd], k), size=12, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, H - 40, "Сусіди в каналі — з РІЗНИХ слів (діагональ), тож пакет із 8 = ⌈8 / N·M⌉ = 2 на слово.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 18, "Той самий закон, що й у блокової матриці, але роль глибини D грає добуток N·M.",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "proj-conv-diagonal.svg"), W, H, *p)


# ── bit-align: 640 наївно проти 633 гостро — де ховається зайвий байт ─────────
def _byte_cell(x, y, w, h, shade_from, shade_to, idx_label, touched_label=None):
    out = [rect(x, y, w, h, fill=BG, stroke=INK, sw=1.6, rx=3)]
    # поділки на 8 бітів
    for k in range(1, 8):
        bx = x + k * w / 8.0
        out.append(line(bx, y, bx, y + h, color="#d8dbe0", sw=1.0))
    # зачеплена частка байта (пакет)
    if shade_to > shade_from:
        sx = x + shade_from * w
        sw_ = (shade_to - shade_from) * w
        out.append(rect(sx, y + 3, sw_, h - 6, fill=BAD_F, stroke=POS, sw=1.6, rx=2))
    out.append(text(x + w / 2, y + h + 18, idx_label, size=11, color=MUTED, bold=False))
    if touched_label:
        out.append(text(x + w / 2, y - 8, touched_label, size=11, color=POS, bold=True))
    return out


def _bit_align_panel(p, y0, title, shift_bits, note):
    # 3 байти на початку смуги, «…», 3 байти в кінці смуги
    w, h = 78.0, 46.0
    gap = 10.0
    x0 = 76.0
    s = shift_bits / 8.0     # зсув старту в частках байта (0.0 або 0.125)

    p.append(text(40, y0 - 26, title, size=13, color=INK, anchor="start", bold=True))

    # ліва зона: байти 0,1,2 — початок смуги
    labels_left = ["байт 0", "байт 1", "байт 2"]
    for i in range(3):
        x = x0 + i * (w + gap)
        if i == 0:
            fr, to = s, 1.0
        else:
            fr, to = 0.0, 1.0
        p += _byte_cell(x, y0, w, h, fr, to, labels_left[i])

    # багатокрапка — решта смуги
    midx = x0 + 3 * (w + gap) + 60
    p.append(text(midx, y0 + h / 2 + 4, "… 76 повних байтів …", size=12, color=MUTED, anchor="middle"))

    # права зона: останні байти смуги
    xr0 = midx + 96
    if shift_bits == 0:
        # вирівняний: смуга рівно закінчується на межі байта 79 — 80-й (останній) байт
        labels_right = ["байт 77", "байт 78", "байт 79"]
        fracs = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
        extra = None
    else:
        # зсунутий на 1 біт: хвіст залазить у 81-й байт
        labels_right = ["байт 78", "байт 79", "байт 80"]
        fracs = [(0.0, 1.0), (0.0, 1.0), (0.0, s)]
        extra = xr0 + 2 * (w + gap)
    for i in range(3):
        x = xr0 + i * (w + gap)
        fr, to = fracs[i]
        lbl = None
        if shift_bits != 0 and i == 2:
            lbl = "+1 зайвий"
        p += _byte_cell(x, y0, w, h, fr, to, labels_right[i], lbl)

    p.append(text(xr0 + 3 * (w + gap) + 30, y0 + h / 2 + 4, note, size=12.5, color=POS if shift_bits else FIELD,
                  anchor="start", bold=True))


def fig_bit_align():
    W, H = 1060, 380
    p = []
    p.append(text(W / 2, 34, "Той самий 640-бітний пакет: вирівняний торкається 80 байтів, зсунутий на 1 біт — уже 81",
                  size=13.5, color=INK, bold=True))
    _bit_align_panel(p, 96, "вирівняний на межу байта (зсув 0 бітів)", 0,
                     "зачеплено рівно 80 байтів — межа D·t тримається ✓")
    _bit_align_panel(p, 232, "зсунутий на 1 біт", 1,
                     "зачеплено 81 байт — межа D·t провалена ✗")
    tb, w, h = textbox(W / 2, 336,
                       ["гарантія за БУДЬ-ЯКОГО зсуву: ℓ ≤ s·(D·t−1)+1 = 8·79+1 = 633 біти — на s−1 = 7 бітів коротша за наївні 640"],
                       size=12, bold=True, fill="#eafaee", stroke=FIELD, pad=12)
    p.append(tb)
    render(os.path.join(OUT, "bit-align.svg"), W, H, *p)


# ── memory-triangle: прямокутник блокового проти трикутника згорткового ────────
def fig_memory_triangle():
    W, H = 940, 500
    p = []
    D = 6
    cw, chh = 44.0, 40.0

    def grid(gx, gy, title, filled_fn, count, total, color):
        out = [text(gx + D * cw / 2, gy - 22, title, size=13, color=INK, anchor="middle", bold=True)]
        for r in range(D):
            for c in range(D):
                x, y = gx + c * cw, gy + r * chh
                on = filled_fn(r, c)
                if on:
                    f, s = FIELD + "22", color
                    out.append(rect(x + 1.5, y + 1.5, cw - 3, chh - 3, fill=f, stroke=s, sw=1.4, rx=2))
                else:
                    out.append(rect(x + 1.5, y + 1.5, cw - 3, chh - 3, fill="none", stroke="#d8dbe0", sw=1.2,
                                    rx=2))
        out.append(text(gx - 14, gy - 2, "рядки (гілки)", size=10.5, color=MUTED, anchor="start"))
        out.append(text(gx + D * cw / 2, gy + D * chh + 24,
                        "%s клітин %s" % (count, "заповнено одразу" if total is None else "із %s" % total),
                        size=12, color=color, bold=True))
        return out

    gxL, gy = 70, 96
    p += grid(gxL, gy, "блоковий: тримає весь прямокутник D×n одразу",
              lambda r, c: True, str(D * D), None, "#b8860b")

    gxR = 520
    p += grid(gxR, gy, "згортковий: гілка i тримає лише i комірок — сходинки",
              lambda r, c: c < r, str(D * (D - 1) // 2), str(D * D), FIELD)

    p.append(text(W / 2, gy + D * chh + 70,
                  "Площа трикутника — рівно половина площі прямокутника, у якому він вписаний.",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, gy + D * chh + 92,
                  "Тому й пам'ять, і затримка згорткового перемішувача — приблизно половина від блокового тієї самої глибини.",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "memory-triangle.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spread()
    fig_block_matrix()
    fig_depth_tradeoff()
    fig_timeline()
    fig_proj_conv_stagger()
    fig_proj_conv_diagonal()
    fig_bit_align()
    fig_memory_triangle()
    print("ok: spread, block-matrix, depth-tradeoff, timeline, proj-conv-stagger, proj-conv-diagonal, "
          "bit-align, memory-triangle")
