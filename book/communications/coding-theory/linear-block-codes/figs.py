# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DFILL = "#eafaf0"; DSTRK = "#27ae60"   # дані / одинична частина
PFILL = "#eef4ff"; PSTRK = "#2457d6"   # надлишок / перевірки
HL    = "#fff7d6"                       # підсвіт активного рядка / стовпця


def cell(x, y, w, h, val, fill, strk, sw=1.8, tcol=INK, tbold=True):
    out = rect(x, y, w, h, fill=fill, stroke=strk, sw=sw, rx=4)
    out += text(x + w / 2, y + h / 2 + 5, str(val), size=15, color=tcol, bold=tbold)
    return out


# ── Fig 1: кодування c = m·G, систематичний вигляд [I | P] ────────────────────
def fig_encode():
    W, H = 800, 470
    p = []
    cw, ch = 46, 42
    rows = [
        [1, 0, 0, 0,  1, 1, 0],
        [0, 1, 0, 0,  0, 1, 1],
        [0, 0, 1, 0,  1, 1, 1],
        [0, 0, 0, 1,  1, 0, 1],
    ]
    m = [1, 0, 1, 1]
    c = [1, 0, 1, 1,  1, 0, 0]

    mx = 250          # лівий край матриці G
    my = 108          # верх матриці G
    mvx = 120         # x вектора m (лівіше матриці)

    # заголовки груп над матрицею
    gi_cx = mx + 2 * cw            # центр блоку I (4 стовпці)
    gp_cx = mx + 4 * cw + 1.5 * cw  # центр блоку P (3 стовпці)
    p.append(text(gi_cx, my - 30, "Iₖ — копія даних", size=12.5, color=DSTRK, bold=True))
    p.append(text(gp_cx, my - 30, "P — надлишок", size=12.5, color=PSTRK, bold=True))
    # номери позицій
    for j in range(7):
        p.append(text(mx + j * cw + cw / 2, my - 10, "%d" % (j + 1), size=10.5, color=MUTED))

    # підсвіт активних рядків (m=1) — тягнемо СМУГУ позаду всієї матриці
    for r in range(4):
        if m[r]:
            p.append(rect(mx - 6, my + r * ch + 3, 7 * cw + 12, ch - 6,
                          fill=HL, stroke="none", sw=0, rx=4))

    # вектор m ліворуч + матриця G
    p.append(text(mvx + cw / 2, my - 30, "дані m", size=12.5, color=INK, bold=True))
    for r in range(4):
        ry = my + r * ch
        # m-біт
        p.append(cell(mvx, ry, cw, ch, m[r], DFILL if m[r] else BG,
                      DSTRK if m[r] else "#c8ccd2", tcol=DSTRK if m[r] else MUTED))
        # рядки матриці
        for j in range(7):
            isI = (j < 4)
            on = rows[r][j]
            x = mx + j * cw
            fill = (DFILL if isI else PFILL) if on else BG
            strk = (DSTRK if isI else PSTRK) if on else "#d0d4da"
            p.append(cell(x, ry, cw, ch, rows[r][j], fill, strk,
                          sw=1.8 if on else 1.0,
                          tcol=(DSTRK if isI else PSTRK) if on else "#c0c4ca"))
        # позначка активного рядка
        if m[r]:
            p.append(text(mx + 7 * cw + 20, ry + ch / 2 + 4, "→ у XOR", size=11,
                          color="#b7791f", bold=True, anchor="start"))

    # «·» між m і G
    p.append(text(mvx + cw + (mx - mvx - cw) / 2, my + 2 * ch, "·", size=26, color=INK, bold=True))
    # роздільник I | P усередині матриці
    dvx = mx + 4 * cw
    p.append(line(dvx, my - 4, dvx, my + 4 * ch + 4, color=INK, sw=2.0, dash="4 3"))

    # стрілка вниз до кодового слова
    mbot = my + 4 * ch
    cy = mbot + 56
    p.append(arrow(mx + 3.5 * cw, mbot + 8, mx + 3.5 * cw, cy - 6, color=INK, sw=2.0))
    p.append(text(mx + 3.5 * cw + 14, (mbot + cy) / 2 + 4,
                  "c = m · G  (XOR активних рядків)", size=12, color=INK, anchor="start", bold=True))

    # кодове слово c (7 клітинок, вирівняне під стовпці матриці)
    p.append(text(mvx + cw / 2, cy + ch / 2 + 5, "слово c", size=12.5, color=INK, bold=True))
    for j in range(7):
        isI = (j < 4)
        x = mx + j * cw
        p.append(cell(x, cy, cw, ch, c[j], DFILL if isI else PFILL,
                      DSTRK if isI else PSTRK, tcol=DSTRK if isI else PSTRK))
    p.append(text(mx + 3.5 * cw, cy + ch + 26,
                  "дані 1 0 1 1 лишилися на видноті (систематичність), надлишок 1 0 0 — порахований",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "encode.svg"), W, H, *p,
           title="Кодування — один добуток: c = m·G у систематичному вигляді [I | P]")


# ── Fig 2: синдром = стовпець перевірної матриці H ────────────────────────────
def fig_syndrome():
    W, H = 820, 430
    p = []
    cw, ch = 50, 42
    Hm = [
        [1, 0, 1, 1,  1, 0, 0],
        [1, 1, 1, 0,  0, 1, 0],
        [0, 1, 1, 1,  0, 0, 1],
    ]
    r = [1, 0, 0, 1, 1, 0, 0]     # прийняте (біт 3 перевернуто)
    s = [1, 1, 1]
    bad = 3                        # 1-based

    mx = 150
    ry = 70                        # верх рядка r
    hy = 190                       # верх матриці H
    colhl = mx + (bad - 1) * cw    # x підсвіченого стовпця

    # номери позицій над r
    for j in range(7):
        p.append(text(mx + j * cw + cw / 2, ry - 12, "%d" % (j + 1), size=10.5, color=MUTED))

    # підсвіт битого стовпця через обидві таблиці
    p.append(rect(colhl - 3, ry - 4, cw + 6, (hy + 3 * ch) - (ry - 4) + 4,
                  fill=HL, stroke="none", sw=0, rx=4))

    # прийняте слово r
    p.append(text(mx - 16, ry + ch / 2 + 5, "r", size=14, color=INK, bold=True, anchor="end"))
    for j in range(7):
        flipped = (j + 1 == bad)
        x = mx + j * cw
        p.append(cell(x, ry, cw, ch, r[j], "#fdecea" if flipped else FILL,
                      POS if flipped else LINE, sw=2.4 if flipped else 1.3,
                      tcol=POS if flipped else INK))
    p.append(text(colhl + cw / 2, ry + ch + 18, "збій у каналі", size=11, color=POS, bold=True))

    # стрілка ×H
    p.append(arrow(mx + 3.5 * cw, ry + ch + 34, mx + 3.5 * cw, hy - 8, color=INK, sw=2.0))
    p.append(text(mx + 3.5 * cw + 14, ry + ch + 54, "s = H · rᵀ", size=12.5,
                  color=INK, anchor="start", bold=True))

    # перевірна матриця H
    p.append(text(mx - 16, hy + 1.5 * ch + 5, "H", size=14, color=PSTRK, bold=True, anchor="end"))
    for rr in range(3):
        for j in range(7):
            on = Hm[rr][j]
            x = mx + j * cw
            p.append(cell(x, hy + rr * ch, cw, ch, Hm[rr][j],
                          PFILL if on else BG, PSTRK if on else "#d0d4da",
                          sw=1.8 if on else 1.0,
                          tcol=PSTRK if on else "#c0c4ca"))

    # синдром s праворуч від H + знак «=»
    sx = mx + 7 * cw + 70
    p.append(text(mx + 7 * cw + 34, hy + 1.5 * ch + 6, "=", size=24, color=INK, bold=True))
    p.append(text(sx + cw / 2, hy - 14, "синдром s", size=12, color=INK, bold=True))
    for rr in range(3):
        p.append(cell(sx, hy + rr * ch, cw, ch, s[rr], "#f6f4ec", INK, sw=2.0))
    p.append(text(sx + cw / 2, hy + 3 * ch + 22, "= стовпець 3", size=12, color="#b7791f", bold=True))

    # підсумковий рядок
    box, bw, bh = textbox(W / 2, hy + 3 * ch + 66,
                          "синдром = стовпцю 3 матриці H  →  бита позиція 3  →  один XOR її лагодить",
                          size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "syndrome.svg"), W, H, *p,
           title="Синдром = стовпець H: добуток H·rᵀ сам називає биту позицію")


# ── Fig 3: увесь кодек — два множення на матрицю замість таблиці ───────────────
def fig_pipeline():
    W, H = 1060, 250
    p = []
    cy = 118
    bw = 148
    step = 208
    cx0 = 40 + bw / 2
    centers = [cx0 + i * step for i in range(5)]
    boxes = [
        ("дані\nm", DFILL, DSTRK),
        ("слово\nc", PFILL, PSTRK),
        ("прийняте\nr", "#fdecea", POS),
        ("синдром\ns", "#f6f4ec", INK),
        ("дані\nm̂", DFILL, DSTRK),
    ]
    hs = []
    for cx, (label, fill, strk) in zip(centers, boxes):
        b, w, h = textbox(cx, cy, label, size=13, bold=True, fill=fill, stroke=strk,
                          sw=2.0, pad=10, min_w=bw)
        hs.append(h)
        p.append(b)

    # стрілки між боксами + підписи над ними
    arr_lbl = [("× G", INK), ("+ e", POS), ("× H", INK), ("таблиця", INK)]
    for i in range(4):
        x1 = centers[i] + bw / 2 + 4
        x2 = centers[i + 1] - bw / 2 - 4
        p.append(arrow(x1, cy, x2, cy, color=LINE, sw=2.0))
        lbl, col = arr_lbl[i]
        p.append(text((x1 + x2) / 2, cy - 16, lbl, size=12.5, color=col, bold=True))

    # підписи-пояснення під стрілками
    sub = [("кодування", 0), ("помилка каналу", 1), ("синдром", 2), ("знайти й виправити", 3)]
    for lbl, i in sub:
        x1 = centers[i] + bw / 2 + 4
        x2 = centers[i + 1] - bw / 2 - 4
        p.append(text((x1 + x2) / 2, cy + 22, lbl, size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, cy + 78,
                  "дві невеликі матриці (G і H) замінюють таблицю на 2ᵏ дозволених слів",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Наскрізний шлях: кодування ×G, перевірка ×H, декодування за синдромом")


# ── Fig 4 (proj): матриця в пам'яті — масив масок; обидва добутки — один примітив ──
def maskstr(x0, y, s, pitch=15, size=15, split=None, ca=DSTRK, cb=PSTRK):
    """Бітовий рядок фіксованим кроком (моноширинний вигляд), з кольоровим поділом."""
    out = []
    for i, ch in enumerate(s):
        col = ca if (split is None or i < split) else cb
        out.append(text(x0 + i * pitch + pitch / 2, y, ch, size=size, color=col, bold=True))
    return "".join(out)


def maskrow(cx, y, label, s, split, pitch=15, ca=DSTRK, cb=PSTRK):
    """Підпис зліва + рамка з бітовою маскою, відцентрована по cx."""
    bw = len(s) * pitch + 22
    bh = 30
    x0 = cx - bw / 2
    out = rect(x0, y - bh / 2, bw, bh, fill="#ffffff", stroke=MUTED, sw=1.4, rx=5)
    out += maskstr(x0 + 11, y + 5, s, pitch=pitch, split=split, ca=ca, cb=cb)
    out += text(x0 - 12, y + 5, label, size=13, color=MUTED, anchor="end")
    return out, bw


def fig_codec_masks():
    W, H = 960, 610
    p = []

    ax, bx = 250, 700          # центри двох смуг
    top = 78

    p.append(text(ax, top, "рядки G — k = 4 маски по n = 7 бітів", size=13, color=INK, bold=True))
    p.append(text(bx, top, "стовпці H — n = 7 масок по n−k = 3 біти", size=13, color=INK, bold=True))

    # ── смуга A: рядки G ──
    grows = ["1000110", "0100011", "0010111", "0001101"]
    ay = top + 34
    for j, s in enumerate(grows):
        frag, bw = maskrow(ax, ay + j * 38, "G[%d]" % j, s, split=4)
        p.append(frag)
    p.append(text(ax - 74, ay - 20, "Iₖ", size=12, color=DSTRK, bold=True))
    p.append(text(ax + 52, ay - 20, "P", size=12, color=PSTRK, bold=True))
    p.append(mtext(ax, ay + 4 * 38 + 16,
                   ["увесь рядок матриці — ОДНЕ ціле:", "G[j] = (1 << j) | (P[j] << k)"],
                   size=12, color=MUTED))

    # ── смуга B: стовпці H ──
    hcols = ["110", "011", "111", "101", "100", "010", "001"]
    by = top + 34
    right_edge = 0
    for j, s in enumerate(hcols):
        frag, bw = maskrow(bx, by + j * 38, "H[%d]" % j, s, split=None,
                           ca=(PSTRK if j < 4 else DSTRK))
        p.append(frag)
        right_edge = bx + bw / 2

    # фігурні пояснення справа від масок
    br = right_edge + 16
    p.append(line(br, by - 14, br, by + 3 * 38 + 14, color=PSTRK, sw=1.4))
    p.append(mtext(br + 10, by + 1.5 * 38 - 6, ["= рядки P як є:", "транспонування", "задарма"],
                   size=11.5, color=PSTRK, anchor="start"))
    p.append(line(br, by + 4 * 38 - 14, br, by + 6 * 38 + 14, color=DSTRK, sw=1.4))
    p.append(mtext(br + 10, by + 5 * 38 - 6, ["= одинична", "матриця"],
                   size=11.5, color=DSTRK, anchor="start"))

    # ── стрілки вниз до спільного примітиву ──
    py0 = by + 7 * 38 + 22          # верх примітиву
    p.append(arrow(ax, ay + 4 * 38 + 44, ax, py0 - 6, color=LINE, sw=2.0))
    p.append(arrow(bx, by + 6 * 38 + 22, bx, py0 - 6, color=LINE, sw=2.0))
    p.append(text(ax + 8, ay + 4 * 38 + 70, "селектор = m (k бітів)",
                  size=12, color=INK, anchor="start", bold=True))
    p.append(text(bx + 8, by + 6 * 38 + 46, "селектор = r (n бітів)",
                  size=12, color=INK, anchor="start", bold=True))

    # ── спільний примітив ──
    pw, ph = 640, 74
    px = W / 2 - pw / 2
    p.append(fitbox(px, py0, pw, ph,
                    ["xor_selected(маски, селектор):  acc = 0;",
                     "для кожного i, де селектор має 1  →  acc ^= маски[i]"],
                    size=15, fill=HL, stroke=INK, sw=2.0, bold=True))

    # ── виходи ──
    oy = py0 + ph
    p.append(arrow(ax, oy + 4, ax, oy + 44, color=LINE, sw=2.0))
    p.append(arrow(bx, oy + 4, bx, oy + 44, color=LINE, sw=2.0))
    p.append(text(ax, oy + 64, "c = m·G   (кодове слово)", size=13, color=DSTRK, bold=True))
    p.append(text(bx, oy + 64, "s = H·rᵀ   (синдром)", size=13, color=PSTRK, bold=True))

    p.append(text(W / 2, oy + 96,
                  "два різні добутки матриць — одна й та сама функція, різні масиви масок",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "codec-masks.svg"), W, H, *p,
           title="Матриця в пам'яті — це масив бітових масок")


# ── Fig 5 (proj): таблиця лідерів як пошук завширшки по синдромах ──────────────
def fig_coset_bfs():
    W, H = 940, 570
    p = []

    lx, rx = 165, 610               # центри рівня 0 і рівня 1
    hcols = ["110", "011", "111", "101", "100", "010", "001"]
    ry0, rstep = 92, 56

    # рівень 0
    l_cy = ry0 + 3 * rstep
    frag, lw, lh = textbox(lx, l_cy, ["s = 000", "e = 0000000", "нічого не робити"],
                           size=14, pad=13, fill=DFILL, stroke=DSTRK, sw=2.2, bold=True)
    p.append(frag)
    p.append(text(lx, l_cy - lh / 2 - 14, "рівень 0", size=12, color=MUTED, bold=True))

    # рівень 1 — сім стовпців H
    boxw = 236
    for j, s in enumerate(hcols):
        cy = ry0 + j * rstep
        y0 = cy - 20
        p.append(fitbox(rx - boxw / 2, y0, boxw, 40,
                        "s = %s   →   e = біт %d" % (s, j),
                        size=14, fill=PFILL, stroke=PSTRK, sw=1.8, bold=True))
        # стрілка від рівня 0 до цієї рамки
        p.append(arrow(lx + lw / 2 + 6, l_cy, rx - boxw / 2 - 6, cy, color=LINE, sw=1.4))
    p.append(text(rx, ry0 - 34, "рівень 1 — усі 7 стовпців H", size=12, color=MUTED, bold=True))

    # підпис на віялі
    p.append(text((lx + rx) / 2 - 40, l_cy + 96, "⊕ один стовпець H",
                  size=13, color=INK, bold=True))

    p.append(mtext(W / 2, ry0 + 7 * rstep + 26,
                   ["8 синдромів = 1 нульовий + 7 стовпців → таблиця заповнилась уже на рівні 1.",
                    "Рівня 2 просто немає: вільних синдромів не лишилось, тож будь-яка помилка",
                    "ваги 2 неминуче збігається з чиїмось стовпцем — і декодер «виправить» не той біт."],
                   size=13, color=INK, lh=1.45))

    render(os.path.join(OUT, "coset-bfs.svg"), W, H, *p,
           title="Таблиця лідерів росте від нуля: пошук завширшки по синдромах")


# ── Fig 6 (hist): як погляд змінився — від геометрії n-куба до алгебри підгруп ──
def evbox(x, y, w, title, lines, fill, strk):
    """Подія стрічки: жирний заголовок + сірі рядки-деталі, вирівняні влівo."""
    ts, ds, pad = 13.5, 12, 12
    h = pad + ts + 8 + len(lines) * ds * 1.4 + pad - ds * 0.4
    out = rect(x, y, w, h, fill=fill, stroke=strk, sw=1.8, rx=6)
    out += text(x + pad, y + pad + ts * 0.85, title, size=ts, color=INK,
                anchor="start", bold=True)
    out += mtext(x + pad, y + pad + ts + 8 + ds * 0.85, lines, size=ds,
                 color=MUTED, anchor="start", lh=1.4)
    return out, h


def fig_algebra_timeline():
    W, H = 920, 720
    p = []
    spx = 190          # хребет стрічки
    bx, bw = 225, 640  # рамки подій

    events = [
        ("1948", "", "Клод Шеннон",
         ["Доведено: надійна передача можлива аж до пропускної здатності.",
          "Доказ неконструктивний — як будувати коди, не сказано."],
         "#f6f4ec", MUTED),
        ("1949", "червень", "Марсель Голей",
         ["«Notes on Digital Coding», Proc. IRE 37, с. 657 — неповна сторінка.",
          "Коди Голея; перевірна матриця в друці — але як побудова, не теорія."],
         "#f6f4ec", MUTED),
        ("1950", "квітень", "Річард Геммінг",
         ["«Error Detecting and Error Correcting Codes», BSTJ 29, с. 147–160.",
          "Геометрія n-куба: відстань, сфери, «контрольне число»."],
         "#f6f4ec", MUTED),
        ("1956", "січень", "Девід Слепіан",
         ["«A Class of Binary Signaling Alphabets», BSTJ 35, с. 203–234.",
          "Код = підгрупа. Стандартний масив, лідери, доказ оптимальності."],
         PFILL, PSTRK),
        ("1960", "вересень", "Девід Слепіан",
         ["«Some Further Theory of Group Codes», BSTJ 39, с. 1219–1252.",
          "Твірна матриця Ω, перевірна A, канонічна форма (Iₖ | M)."],
         PFILL, PSTRK),
        ("1961", "", "Веслі Пітерсон",
         ["«Error-Correcting Codes», MIT Press — перший підручник галузі.",
          "Матрична мова стає просто тим, як предмет викладають."],
         DFILL, DSTRK),
    ]
    ys = [70, 162, 254, 380, 472, 564]

    # хребет — двома відтинками, з розривом під роздільник
    p.append(line(spx, 70, spx, 338, color=MUTED, sw=2.4))
    p.append(line(spx, 366, spx, 638, color=PSTRK, sw=2.4))

    for (yr, mon, title, lines, fill, strk), y in zip(events, ys):
        frag, h = evbox(bx, y, bw, title, lines, fill, strk)
        p.append(frag)
        # вузол на хребті + поличка до рамки
        p.append(line(spx, y + h / 2, bx - 4, y + h / 2, color=strk, sw=1.4))
        p.append(circle(spx, y + h / 2, 7, fill=fill, stroke=strk, sw=2.4))
        # рік і місяць ліворуч від хребта
        p.append(text(168, y + 32, yr, size=15, color=INK, anchor="end", bold=True))
        if mon:
            p.append(text(168, y + 48, mon, size=10.5, color=MUTED, anchor="end"))

    # роздільник епох — лінія з розривом, у розриві напис
    p.append(line(60, 352, 280, 352, color=INK, sw=1.6, dash="6 4"))
    p.append(line(790, 352, 880, 352, color=INK, sw=1.6, dash="6 4"))
    p.append(text(535, 357, "тут погляд змінюється: геометрія n-куба → алгебра підгруп",
                  size=13, color=INK, bold=True))

    p.append(mtext(W / 2, 672,
                   ["Між 1950 і 1956 не з'явилося жодного нового коду — з'явився новий спосіб",
                    "дивитися на ті самі. Слепіан не побудував кращого коду: він помітив, що вже",
                    "побудовані замкнені щодо додавання, — і дотиснув цю думку до кінця."],
                   size=13, color=INK, lh=1.45, bold=True))

    render(os.path.join(OUT, "algebra-timeline.svg"), W, H, *p,
           title="Як коди стали алгеброю: 1948 → 1961")


# ── Fig 7 (hist): стандартний масив Слепіана для коду [5, 2] ──────────────────
def x5(a, b):
    """XOR двох бітових рядків однакової довжини."""
    return "".join("1" if p != q else "0" for p, q in zip(a, b))


def sacell(x, y, w, h, val, fill, strk, sw=1.6, tcol=INK):
    out = rect(x, y, w, h, fill=fill, stroke=strk, sw=sw, rx=4)
    out += text(x + w / 2, y + h / 2 + 5, val, size=14, color=tcol, bold=True)
    return out


def fig_standard_array():
    W, H = 900, 550
    p = []
    CODE = ["00000", "10110", "01011", "11101"]
    LEAD = ["00000", "10000", "01000", "00100", "00010", "00001", "11000", "10001"]
    SYND = ["000", "110", "011", "100", "010", "001", "101", "111"]

    ax, cw, ch = 220, 80, 40      # ліво/розмір клітин масиву
    sx, sw_ = 120, 80             # стовпець синдромів
    y0 = 118
    GOLD = "#b7791f"

    p.append(text(W / 2, 52, "код [5, 2] з чотирьох слів: 00000, 10110, 01011, 11101",
                  size=12.5, color=MUTED))

    # заголовки стовпців
    p.append(text(sx + sw_ / 2, 100, "синдром s", size=11.5, color=MUTED, bold=True))
    p.append(text(ax + cw / 2, 100, "лідери eᵢ", size=11.5, color=PSTRK, bold=True))
    p.append(text(ax + 2.5 * cw, 100, "…решта суміжного класу", size=11.5, color=MUTED))

    for i in range(8):
        y = y0 + i * ch
        # синдром рядка
        p.append(sacell(sx, y, sw_, ch, SYND[i], "#f6f4ec", INK, sw=1.6))
        for j in range(4):
            x = ax + j * cw
            val = x5(LEAD[i], CODE[j])
            if i == 0:                              # верхній рядок — сам код
                fill, strk, tc, s = DFILL, DSTRK, DSTRK, 1.8
            elif j == 0:                            # перший стовпець — лідери
                fill, strk, tc, s = PFILL, PSTRK, PSTRK, 1.8
                if i >= 6:                          # лідери ваги 2 — неоднозначні
                    fill, strk, tc = "#fdecea", POS, POS
            else:
                fill, strk, tc, s = BG, "#d0d4da", INK, 1.0
            # позначені клітини наскрізного прикладу
            if (i, j) == (3, 1):                    # прийняте слово r
                fill, strk, tc, s = HL, POS, POS, 2.6
            elif (i, j) in ((0, 1), (3, 0)):        # відповідь і лідер того рядка
                strk, s = GOLD, 2.6
            p.append(sacell(x, y, cw, ch, val, fill, strk, sw=s, tcol=tc))

    # пояснення праворуч
    p.append(mtext(560, 130, ["рядок 0 — це сам код C", "(лідер 00000: помилки не було)"],
                   size=11.5, color=DSTRK, anchor="start", lh=1.4))
    p.append(mtext(560, 244, ["прийняли r = 10010",
                              "рядок → e = 00100; стовпець → c = 10110",
                              "r ⊕ e = c — біт 3 полагоджено"],
                   size=11.5, color=INK, anchor="start", lh=1.4))
    p.append(line(552, 362, 552, 434, color=POS, sw=1.6))
    p.append(mtext(564, 380, ["лідер ваги 2 — і він не єдиний:",
                              "синдром 101 дають і 11000, і 00101;",
                              "синдром 111 — і 10001, і 01100.",
                              "Тут декодер просто гадає."],
                   size=11.5, color=POS, anchor="start", lh=1.4))

    box, bwid, bh = textbox(W / 2, 490,
                            ["8 рядків × 4 стовпці = 32 = 2⁵: кожне слово простору стоїть рівно раз.",
                             "Рядок — це помилка (лідер), стовпець — це відповідь (слово вгорі)."],
                            size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "standard-array.svg"), W, H, *p,
           title="Стандартний масив: увесь простір, розкладений по суміжних класах")


if __name__ == "__main__":
    fig_encode()
    fig_syndrome()
    fig_pipeline()
    fig_codec_masks()
    fig_coset_bfs()
    fig_algebra_timeline()
    fig_standard_array()
    print("OK: figures written to", OUT)
