# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DFILL = "#eafaf0"; DSTRK = "#27ae60"   # дані / значення функції
PFILL = "#eef4ff"; PSTRK = "#2457d6"   # надлишок / нижчий степінь
HL    = "#fff7d6"                       # підсвіт
GOLD  = "#b7791f"

PTS = ["000", "001", "010", "011", "100", "101", "110", "111"]   # (x1 x2 x3), x1 старший


def cell(x, y, w, h, val, fill, strk, sw=1.8, tcol=INK, size=15):
    out = rect(x, y, w, h, fill=fill, stroke=strk, sw=sw, rx=4)
    out += text(x + w / 2, y + h / 2 + size * 0.34, str(val), size=size, color=tcol, bold=True)
    return out


# ── Fig 1: кодове слово = стовпець значень булевої функції ─────────────────────
def fig_truth_table():
    W, H = 780, 560
    p = []
    # значення для f = 1 ⊕ x2 ⊕ x3
    X1 = [int(s[0]) for s in PTS]
    X2 = [int(s[1]) for s in PTS]
    X3 = [int(s[2]) for s in PTS]
    F  = [1 ^ X2[i] ^ X3[i] for i in range(8)]

    cw, ch = 44, 34
    tx = 120                      # лівий край стовпця x1
    ty = 96                       # верх першого рядка даних
    gap = 26                      # проміжок між блоком змінних і стовпцем f
    fx = tx + 3 * cw + gap        # x стовпця f

    p.append(text(tx + 1.5 * cw, ty - 42, "вхід (x₁ x₂ x₃)", size=13, color=INK, bold=True))
    p.append(text(fx + cw / 2, ty - 42, "f = 1 ⊕ x₂ ⊕ x₃", size=13, color=DSTRK, bold=True))
    for j, lab in enumerate(["x₁", "x₂", "x₃"]):
        p.append(text(tx + j * cw + cw / 2, ty - 16, lab, size=12.5, color=MUTED, bold=True))
    p.append(text(fx + cw / 2, ty - 16, "f", size=12.5, color=DSTRK, bold=True))

    for i in range(8):
        ry = ty + i * ch
        for j, col in enumerate([X1, X2, X3]):
            v = col[i]
            p.append(cell(tx + j * cw, ry, cw, ch, v,
                          BG, "#c9ccd2", sw=1.0, tcol=MUTED, size=14))
        # стовпець f — підсвічений
        p.append(cell(fx, ry, cw, ch, F[i], DFILL, DSTRK, sw=1.8, tcol=DSTRK, size=15))

    # стрілка від стовпця f донизу до горизонтального слова
    colbot = ty + 8 * ch
    p.append(text(fx + cw / 2, colbot + 22,
                  "читаємо згори вниз", size=11.5, color=MUTED, italic=True))
    p.append(arrow(fx + cw / 2, colbot + 34, fx + cw / 2, colbot + 60, color=LINE, sw=2.0))

    # горизонтальне кодове слово
    sy = colbot + 66
    sx = tx - 6
    scw = (fx + cw - sx) / 8      # рівномірно по всій ширині таблиці
    scw = 52
    sx = W / 2 - 4 * scw
    p.append(text(sx - 12, sy + ch / 2 + 5, "c", size=15, color=INK, bold=True, anchor="end"))
    for i in range(8):
        p.append(cell(sx + i * scw, sy, scw, ch, F[i], DFILL, DSTRK, sw=1.8, tcol=DSTRK, size=16))
    box, bw, bh = textbox(W / 2, sy + ch + 44,
                          "кодове слово c = 1 0 0 1 1 0 0 1  (довжина n = 2³ = 8, вага 4)",
                          size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=11)
    p.append(box)

    render(os.path.join(OUT, "truth-table.svg"), W, H, *p,
           title="Кодове слово RM(1,3) — це таблиця істинності функції")


# ── Fig 2: драбина сімейства — мономи за степенем + вибір r ────────────────────
def fig_family_ladder():
    W, H = 860, 590
    p = []
    # 8 мономів у порядку степеня + їхні таблиці істинності
    monos = [
        (0, "1",       "11111111"),
        (1, "x₁",      "00001111"),
        (1, "x₂",      "00110011"),
        (1, "x₃",      "01010101"),
        (2, "x₁x₂",    "00000011"),
        (2, "x₁x₃",    "00000101"),
        (2, "x₂x₃",    "00010001"),
        (3, "x₁x₂x₃",  "00000001"),
    ]
    bw, bh = 22, 30               # бітова клітинка
    gx = 250                      # лівий край бітового рядка
    ty = 96
    rh = 40                       # крок рядків

    p.append(text(gx + 4 * bw, ty - 44, "RM(r, 3): узяти всі мономи степеня ≤ r",
                  size=13.5, color=INK, bold=True))
    p.append(text(150, ty - 20, "моном", size=12, color=MUTED, bold=True))
    p.append(text(gx + 4 * bw, ty - 20, "таблиця істинності (8 бітів)", size=12, color=MUTED))

    # групові дужки степенів ліворуч
    deg_groups = [(0, 0, 0), (1, 1, 3), (2, 4, 6), (3, 7, 7)]
    for deg, i0, i1 in deg_groups:
        y0 = ty + i0 * rh
        y1 = ty + i1 * rh + bh
        p.append(line(70, y0, 70, y1, color=MUTED, sw=1.6))
        p.append(line(70, y0, 78, y0, color=MUTED, sw=1.6))
        p.append(line(70, y1, 78, y1, color=MUTED, sw=1.6))
        p.append(text(60, (y0 + y1) / 2 + 4, "степінь %d" % deg, size=11.5,
                      color=MUTED, anchor="end", bold=True))

    for i, (deg, name, tt) in enumerate(monos):
        ry = ty + i * rh
        p.append(text(150, ry + bh / 2 + 5, name, size=14, color=INK, bold=True))
        for j, chb in enumerate(tt):
            on = chb == "1"
            p.append(cell(gx + j * bw, ry, bw, bh, chb,
                          DFILL if on else BG, DSTRK if on else "#d0d4da",
                          sw=1.6 if on else 1.0, tcol=DSTRK if on else "#c0c4ca", size=13))

    # праворуч — вкладені дужки вибору r з параметрами [n,k,d]
    rx0 = gx + 8 * bw + 26
    specs = [(0, 0, "[8, 1, 8]", "повторення"),
             (1, 3, "[8, 4, 4]", "виправляє 1"),
             (2, 6, "[8, 7, 2]", "1 парність"),
             (3, 7, "[8, 8, 1]", "весь простір")]
    for k, (r, i1, param, note) in enumerate(specs):
        bx = rx0 + k * 68
        yt = ty - 4
        yb = ty + i1 * rh + bh + 4
        p.append(line(bx, yt, bx, yb, color=PSTRK, sw=1.8))
        p.append(line(bx, yb, bx - 7, yb, color=PSTRK, sw=1.8))
        p.append(text(bx + 4, yb + 15, "r=%d" % r, size=11.5, color=PSTRK, anchor="start", bold=True))
        p.append(text(bx + 4, yb + 31, param, size=11.5, color=INK, anchor="start", bold=True))
        p.append(text(bx + 4, yb + 46, note, size=10, color=MUTED, anchor="start", italic=True))

    p.append(mtext(W / 2, H - 40,
                   ["k росте як C(3,0)+…+C(3,r) — більше мономів, більше даних;",
                    "d = 2^(3−r) падає вдвічі з кожним поверхом — дрібніший моном, слабший захист."],
                   size=12.5, color=INK, lh=1.5, bold=True))

    render(os.path.join(OUT, "family-ladder.svg"), W, H, *p,
           title="Драбина сімейства: одна ручка r між ємністю й захистом")


# ── Fig 3: голосування за коефіцієнт a₁ (мажоритарне декодування) ──────────────
def fig_voting():
    W, H = 840, 520
    p = []
    R = [1, 0, 1, 1, 1, 0, 0, 1]     # прийняте (точку 010 = індекс 2 перевернуто)
    bad = 2
    cw, ch = 58, 36
    sx = W / 2 - 4 * cw
    ty = 90

    p.append(text(sx + 4 * cw, ty - 44, "прийняте слово r (біт у точці 010 збито каналом)",
                  size=13, color=INK, bold=True))
    for i in range(8):
        flipped = i == bad
        p.append(text(sx + i * cw + cw / 2, ty - 18, PTS[i], size=10.5,
                      color=POS if flipped else MUTED, bold=flipped))
        p.append(cell(sx + i * cw, ty, cw, ch, R[i],
                      "#fdecea" if flipped else FILL, POS if flipped else LINE,
                      sw=2.4 if flipped else 1.2, tcol=POS if flipped else INK, size=16))

    # чотири пари, що різняться лише в x₁ (індекси i та i+4)
    pairs = [(0, 4), (1, 5), (2, 6), (3, 7)]
    vy = ty + ch + 54
    vh = 40
    votes = [R[a] ^ R[b] for a, b in pairs]
    for k, (a, b) in enumerate(pairs):
        ry = vy + k * (vh + 12)
        corrupt = (a == bad or b == bad)
        fill = "#fdecea" if corrupt else PFILL
        strk = POS if corrupt else PSTRK
        txt = "пара (%s , %s):   %d ⊕ %d  =  %d" % (PTS[a], PTS[b], R[a], R[b], votes[k])
        p.append(fitbox(W / 2 - 220, ry, 300, vh, txt, size=14,
                        fill=fill, stroke=strk, sw=2.0 if corrupt else 1.6, bold=True,
                        color=POS if corrupt else INK))
        if corrupt:
            p.append(text(W / 2 + 96, ry + vh / 2 + 5, "← зіпсований голос",
                          size=12, color=POS, anchor="start", bold=True))

    # підсумок голосування
    by = vy + 4 * (vh + 12) + 14
    box, bwid, bh = textbox(W / 2, by,
                            ["голоси:  0  0  1  0     →     більшість = 0     →     a₁ = 0",
                             "один брехливий голос лишився в меншості — помилку виправлено"],
                            size=13.5, bold=True, fill="#f6f4ec", stroke=INK, sw=2.2, pad=13)
    p.append(box)

    render(os.path.join(OUT, "voting.svg"), W, H, *p,
           title="Декодування голосуванням: чотири незалежні свідки a₁")


# ── Fig 4: рекурсія (u, u⊕v) ──────────────────────────────────────────────────
def node(cx, cy, title, param, fill, strk, w=150):
    b, bw, bh = textbox(cx, cy, [title, param], size=13, bold=True,
                        fill=fill, stroke=strk, sw=2.0, pad=11, min_w=w)
    return b, bw, bh


def fig_uv_recursion():
    W, H = 900, 560
    p = []

    # ── верх: конкретне розбиття слова навпіл ──
    c = "00111100"                 # f = x1 ⊕ x2
    cw, ch = 40, 34
    ty = 72
    lx = 150
    p.append(text(W / 2, ty - 24, "слово RM(1,3), f = x₁ ⊕ x₂ :   ліва половина = u,   права = u ⊕ v",
                  size=13, color=INK, bold=True))
    for i, chb in enumerate(c):
        on = chb == "1"
        half_l = i < 4
        fill = (DFILL if half_l else PFILL) if on else BG
        strk = (DSTRK if half_l else PSTRK) if on else "#d0d4da"
        p.append(cell(lx + i * cw, ty, cw, ch, chb, fill, strk,
                      sw=1.7 if on else 1.0,
                      tcol=(DSTRK if half_l else PSTRK) if on else "#c0c4ca", size=15))
    # роздільник половин
    dvx = lx + 4 * cw
    p.append(line(dvx, ty - 6, dvx, ty + ch + 6, color=INK, sw=2.2, dash="4 3"))
    p.append(text(dvx - 10, ty + ch + 20, "u = 0011  ∈ RM(1,2)", size=12, color=DSTRK, bold=True, anchor="end"))
    p.append(text(dvx + 10, ty + ch + 20, "u⊕v = 1100  →  v = 1111 ∈ RM(0,2)",
                  size=12, color=PSTRK, bold=True, anchor="start"))

    # ── дерево рекурсії з параметрами ──
    tx = 620
    yA = ty + ch / 2
    a, aw, ah = node(tx, yA, "RM(1,3)", "[8, 4, 4]", HL, INK, w=150)
    p.append(a)

    yB = yA + 118
    lxB, rxB = tx - 96, tx + 96
    b1, w1, h1 = node(lxB, yB, "u: RM(1,2)", "[4, 3, 2]", DFILL, DSTRK, w=140)
    b2, w2, h2 = node(rxB, yB, "v: RM(0,2)", "[4, 1, 4]", PFILL, PSTRK, w=140)
    p.append(b1); p.append(b2)
    p.append(arrow(tx - 26, yA + ah / 2, lxB, yB - h1 / 2 - 2, color=DSTRK, sw=1.8))
    p.append(arrow(tx + 26, yA + ah / 2, rxB, yB - h2 / 2 - 2, color=PSTRK, sw=1.8))
    p.append(text(tx - 78, yA + ah / 2 + 30, "u", size=12, color=DSTRK, bold=True))
    p.append(text(tx + 74, yA + ah / 2 + 30, "v", size=12, color=PSTRK, bold=True))

    yC = yB + 108
    for (px, lab, par) in [(lxB - 52, "RM(1,1)", "[2,2,1]"),
                           (lxB + 52, "RM(0,1)", "[2,1,2]"),
                           (rxB - 52, "RM(0,1)", "[2,1,2]"),
                           (rxB + 52, "…{0}", "")]:
        nb, nw, nh = node(px, yC, lab, par if par else "", "#f6f4ec", MUTED, w=92)
        p.append(nb)
    p.append(arrow(lxB - 20, yB + h1 / 2, lxB - 52, yC - 20, color=MUTED, sw=1.4))
    p.append(arrow(lxB + 20, yB + h1 / 2, lxB + 52, yC - 20, color=MUTED, sw=1.4))
    p.append(arrow(rxB - 20, yB + h2 / 2, rxB - 52, yC - 20, color=MUTED, sw=1.4))
    p.append(arrow(rxB + 20, yB + h2 / 2, rxB + 52, yC - 20, color=MUTED, sw=1.4))
    p.append(text(tx, yC + 44, "…аж до повторення й повного простору",
                  size=11, color=MUTED, italic=True))

    # ── рекурентності зліва внизу ──
    p.append(mtext(240, yB + 6,
                   ["Розбиття дає рекурентності:",
                    "",
                    "k(r,m) = k(r,m−1) + k(r−1,m−1)",
                    "         → тотожність Паскаля,",
                    "         сума C(m,i)",
                    "",
                    "d(r,m) = 2 · d(r,m−1)",
                    "         → d = 2^(m−r)",
                    "",
                    "Розкрута до кінця = рядки",
                    "кронекерового степеня [[1,0],[1,1]]",
                    "— спільна основа з полярними кодами."],
                   size=12.5, color=INK, anchor="middle", lh=1.42))

    render(os.path.join(OUT, "uv-recursion.svg"), W, H, *p,
           title="Рекурсивне подвоєння (u, u⊕v): усе сімейство з двох цеглинок")


# ── Fig 5: лема Плоткіна про ваги половин (доказ відстані) ─────────────────────
def fig_plotkin_distance():
    W, H = 900, 540
    p = []

    PA_x, PB_x = 48, 470
    PW = 382
    PY, PH = 66, 328

    def panel(x, title, strk, cells, lines, note):
        out = rect(x, PY, PW, PH, fill="#fcfdfe", stroke=strk, sw=1.8, rx=10)
        out += text(x + PW / 2, PY + 30, title, size=15, color=strk, bold=True)
        # дві половини слова
        cw, ch = 118, 42
        cy = PY + 58
        cx0 = x + PW / 2 - cw - 12
        cx1 = x + PW / 2 + 12
        (l1, f1, s1), (l2, f2, s2) = cells
        out += cell(cx0, cy, cw, ch, l1, f1, s1, sw=2.0, tcol=s1, size=17)
        out += cell(cx1, cy, cw, ch, l2, f2, s2, sw=2.0, tcol=s2, size=17)
        out += text(x + PW / 2 - cw - 12 - 8, cy + ch / 2 + 5, "(", size=26, color=INK, anchor="end")
        out += text(x + PW / 2 + cw + 12 + 8, cy + ch / 2 + 5, ")", size=26, color=INK, anchor="start")
        out += mtext(x + PW / 2, cy + ch + 40, lines, size=13.5, color=INK, lh=1.62)
        if note:
            b, bw, bh = textbox(x + PW / 2, PY + PH - 30, note, size=12,
                                fill=HL, stroke=GOLD, sw=1.5, pad=9, bold=True, color=GOLD)
            out += b
        return out

    p.append(panel(PA_x, "Випадок 1:  v = 0", DSTRK,
                   [("u", DFILL, DSTRK), ("u", DFILL, DSTRK)],
                   ["слово ненульове ⇒ u ≠ 0",
                    "вага = wt(u) + wt(u) = 2·wt(u)",
                    "wt(u) ≥ d₁   ⇒   вага ≥ 2·d₁"],
                   "обидві половини рівні"))

    p.append(panel(PB_x, "Випадок 2:  v ≠ 0", PSTRK,
                   [("u", DFILL, DSTRK), ("u⊕v", PFILL, PSTRK)],
                   ["вага = wt(u) + wt(u⊕v)",
                    "≥ wt( u ⊕ (u⊕v) ) = wt(v)",
                    "wt(v) ≥ d₂   ⇒   вага ≥ d₂"],
                   "нерівність трикутника ваг"))

    # нижня смуга — синтез
    box, bw, bh = textbox(W / 2, PY + PH + 52,
                          ["d(r,m) = min( 2·d₁ , d₂ ),   d₁ = d(r,m−1) = 2^((m−1)−r),   d₂ = d(r−1,m−1) = 2^(m−r)",
                           "2·d₁ = 2^(m−r) = d₂   —   обидві межі рівні   ⇒   d(r,m) = 2^(m−r)"],
                          size=13.5, bold=True, fill="#f6f4ec", stroke=INK, sw=2.2, pad=13)
    p.append(box)

    render(os.path.join(OUT, "plotkin-distance.svg"), W, H, *p,
           title="Лема Плоткіна: вага кожної половини дає d = 2^(m−r)")


# ── Fig 6: кронекерів степінь F⊗m — вибір рядків за вагою ──────────────────────
def fig_kronecker():
    W, H = 960, 600
    p = []

    # ── ліворуч: ядро F та правило подвоєння ──
    kx, ky = 60, 150
    kc = 34
    Fk = [["1", "0"], ["1", "1"]]
    p.append(text(kx + kc, ky - 18, "ядро F", size=12.5, color=INK, bold=True))
    for i in range(2):
        for j in range(2):
            on = Fk[i][j] == "1"
            p.append(cell(kx + j * kc, ky + i * kc, kc, kc, Fk[i][j],
                          DFILL if on else BG, DSTRK if on else "#d0d4da",
                          sw=1.6 if on else 1.0, tcol=DSTRK if on else "#c0c4ca", size=15))
    p.append(text(kx + 2 * kc + 14, ky + kc / 2 + 5, "вага 1", size=11, color=MUTED, anchor="start"))
    p.append(text(kx + 2 * kc + 14, ky + kc + kc / 2 + 5, "вага 2", size=11, color=MUTED, anchor="start"))
    p.append(mtext(kx + kc, ky + 2 * kc + 40,
                   ["беремо m-й", "кронекерів", "степінь", "F^{⊗m} = F⊗…⊗F", "(правило", "подвоєння", "(u, u⊕v))"],
                   size=12, color=INK, lh=1.42, bold=False))
    p.append(arrow(kx + 2 * kc + 30, ky + kc, 250, ky + kc, color=LINE, sw=2.0))

    # ── праворуч: F^{⊗3} за спаданням ваги ──
    rows = [
        ("11111111", 8, 0),
        ("11110000", 4, 1),
        ("11001100", 4, 1),
        ("10101010", 4, 1),
        ("11000000", 2, 2),
        ("10100000", 2, 2),
        ("10001000", 2, 2),
        ("10000000", 1, 3),
    ]
    bw, bh = 26, 32
    gx, gy = 300, 96
    rh = 36

    p.append(text(gx + 4 * bw, gy - 40, "F^{⊗3} (рядки за спаданням ваги)", size=13.5, color=INK, bold=True))
    p.append(text(gx + 8 * bw + 40, gy - 40, "вага", size=12, color=MUTED, bold=True))

    for i, (tt, wt, deg) in enumerate(rows):
        ry = gy + i * rh
        for j, chb in enumerate(tt):
            on = chb == "1"
            p.append(cell(gx + j * bw, ry, bw, bh, chb,
                          DFILL if on else BG, DSTRK if on else "#d0d4da",
                          sw=1.5 if on else 1.0, tcol=DSTRK if on else "#c0c4ca", size=13))
        p.append(text(gx + 8 * bw + 46, ry + bh / 2 + 5, str(wt), size=14, color=INK, bold=True))

    # ── вкладені дужки вибору r за порогом ваги ──
    specs = [(0, 0, "[8,1,8]"), (1, 3, "[8,4,4]"), (2, 6, "[8,7,2]"), (3, 7, "[8,8,1]")]
    bx0 = gx + 8 * bw + 96
    for k, (r, ilast, param) in enumerate(specs):
        bx = bx0 + k * 62
        yt = gy - 6
        yb = gy + ilast * rh + bh + 6
        p.append(line(bx, yt, bx, yb, color=PSTRK, sw=1.8))
        p.append(line(bx, yt, bx + 7, yt, color=PSTRK, sw=1.8))
        p.append(line(bx, yb, bx + 7, yb, color=PSTRK, sw=1.8))
        thr = 2 ** (3 - r)
        p.append(text(bx + 4, yb + 16, "r=%d" % r, size=11.5, color=PSTRK, anchor="start", bold=True))
        p.append(text(bx + 4, yb + 31, "вага≥%d" % thr, size=10.5, color=MUTED, anchor="start"))
        p.append(text(bx + 4, yb + 46, param, size=10.5, color=INK, anchor="start", bold=True))

    p.append(mtext(W / 2, H - 52,
                   ["Рядки ваги ≥ 2^(m−r) натягують RM(r,m); їх рівно C(m,0)+…+C(m,r) = k.",
                    "Полярні коди беруть ту саму матрицю — але відбирають рядки за надійністю підканалів, не за вагою."],
                   size=12.5, color=INK, lh=1.5, bold=True))

    render(os.path.join(OUT, "kronecker-rows.svg"), W, H, *p,
           title="Одна матриця F^{⊗m}: поріг ваги вирізає всю драбину RM")


# ── Fig 7 (hist): арка 1954 → 1966 → 1971 ─────────────────────────────────────
def fig_arc():
    W, H = 1080, 440
    p = []
    OCH = "#c1662f"

    p.append(text(190, 66, "1954", size=16, color=GOLD, bold=True))
    p.append(text(590, 66, "1966", size=16, color=GOLD, bold=True))
    p.append(text(895, 66, "1971", size=16, color=GOLD, bold=True))

    # 1954 — дві половини
    mul = textbox(190, 150, ["Маллер (Muller)",
                             "код = таблиця булевої функції",
                             "EC-3, вересень 1954"],
                  size=12, min_w=270, pad=10, fill=DFILL, stroke=DSTRK, sw=1.8, color=INK)[0]
    ree = textbox(190, 240, ["Рід (Reed)",
                             "декодер: голосування більшістю",
                             "PGIT-4, вересень 1954"],
                  size=12, min_w=270, pad=10, fill=PFILL, stroke=PSTRK, sw=1.8, color=INK)[0]
    p.append(mul); p.append(ree)

    # злиття двох половин → одна стрілка
    jx, jy = 355, 195
    p.append(line(325, 150, jx, jy, color=DSTRK, sw=1.6))
    p.append(line(325, 240, jx, jy, color=PSTRK, sw=1.6))
    p.append(circle(jx, jy, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(jx + 8, jy - 12, "код + декодер", size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(arrow(jx + 3, jy, 463, 195, color=INK, sw=2.4))

    # 1966 — зелена машина
    grn = textbox(590, 195, ["Ґрін (Green), JPL",
                             "«зелена машина»:",
                             "швидке перетв. Адамара"],
                  size=12, min_w=250, pad=10, fill=HL, stroke=INK, sw=1.8, color=INK)[0]
    p.append(grn)
    p.append(arrow(716, 194, 770, 189, color=INK, sw=2.4))

    # 1971 — Марінер-9 / Марс
    mar = textbox(895, 190, ["«Марінер-9» → орбіта Марса",
                             "RM(1,5) = [32, 6, 16]",
                             "виправляє 7 помилок",
                             "перші чіткі знімки"],
                  size=12, min_w=250, pad=10, fill="#f6f4ec", stroke=GOLD, sw=1.8, color=INK)[0]
    p.append(mar)
    p.append(circle(895, 322, 26, fill=OCH, stroke="#8a3d18", sw=2))
    p.append(circle(886, 316, 6, fill="#a85526", stroke="none", sw=0))
    p.append(circle(905, 328, 4, fill="#a85526", stroke="none", sw=0))

    p.append(text(W / 2, H - 22,
                  "код (Маллер) + декодер (Рід)  →  швидка машина (Ґрін)  →  різкі знімки Марса",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "arc.svg"), W, H, *p,
           title="Сімнадцять років: від двох статей 1954-го до знімків Марса")


# ── Fig 8 (hist): «зелена машина» — швидке декодування RM(1,5) ─────────────────
def fig_green_machine():
    W, H = 1020, 580
    p = []
    yb = 100

    b1 = textbox(150, yb, ["піксель", "6 бітів = 64 градації"],
                 size=12, min_w=200, pad=10, fill=DFILL, stroke=DSTRK, sw=1.8, color=INK)[0]
    b2 = textbox(410, yb, ["кодер RM(1,5)", "32-бітне слово, d = 16"],
                 size=12, min_w=220, pad=10, fill=FILL, stroke=INK, sw=1.6, color=INK)[0]
    b3 = textbox(680, yb, ["«зелена машина»", "швидке перетв. Адамара"],
                 size=12, min_w=210, pad=10, fill=HL, stroke=INK, sw=1.8, color=INK)[0]
    b4 = textbox(900, yb, ["піксель", "відновлено"],
                 size=12, min_w=170, pad=10, fill=DFILL, stroke=DSTRK, sw=1.8, color=INK)[0]
    p += [b1, b2, b3, b4]

    p.append(arrow(250, yb, 300, yb, color=INK, sw=2.2))
    p.append(arrow(520, yb, 575, yb, color=INK, sw=2.2))
    p.append(text(547, yb - 18, "канал: −7 бітів", size=10.5, color=POS, bold=True))
    p.append(arrow(785, yb, 815, yb, color=INK, sw=2.2))

    # стрілка від машини вниз до діаграми
    p.append(arrow(700, yb + 24, 640, 300, color=MUTED, sw=1.8))
    p.append(text(430, 286, "усі 32 кореляції — одним махом:", size=11.5,
                  color=MUTED, anchor="start", italic=True))

    # діаграма 32 кореляцій
    base = 440
    x0 = 430
    step = 10
    bw = 6.5
    win = 11
    for i in range(32):
        h = 130 if i == win else 10 + ((i * 7 + 3) % 6) * 4
        bx = x0 + i * step
        fill = DFILL if i == win else "#dfe6f2"
        strk = DSTRK if i == win else "#9fb0cc"
        p.append(rect(bx, base - h, bw, h, fill=fill, stroke=strk,
                      sw=1.4 if i == win else 0.8, rx=1))
    p.append(line(x0 - 6, base, x0 + 32 * step, base, color=INK, sw=1.6))

    # виноска до переможця
    wx = x0 + win * step + bw / 2
    p.append(arrow(wx, base - 130 - 4, 795, 252, color=DSTRK, sw=1.8))
    cb = textbox(880, 236, ["найвищий стовпчик виграє:",
                            "номер → 5 бітів,  знак → 6-й"],
                 size=11.5, min_w=240, pad=9, fill="#f6f4ec", stroke=DSTRK, sw=1.6, color=INK)[0]
    p.append(cb)

    # підпис під діаграмою
    uc = textbox(590, 490, "найвищий стовпчик — це найсхожіший кодовий візерунок (функція Волша)",
                 size=12, pad=10, fill=BG, stroke="none", sw=0, color=MUTED)[0]
    p.append(uc)

    # порівняння кількості дій
    oc = textbox(W / 2, 542,
                 "перебір:  64 × 32 ≈ 2048 дій на піксель        ШПА:  32 · log₂32 = 160 дій",
                 size=13, pad=12, fill="#f6f4ec", stroke=INK, sw=2, color=INK, bold=True)[0]
    p.append(oc)

    render(os.path.join(OUT, "green-machine.svg"), W, H, *p,
           title="«Зелена машина»: одне перетворення замість тисяч порівнянь")


if __name__ == "__main__":
    fig_truth_table()
    fig_family_ladder()
    fig_voting()
    fig_uv_recursion()
    fig_plotkin_distance()
    fig_kronecker()
    fig_arc()
    fig_green_machine()
    print("OK: figures written to", OUT)
