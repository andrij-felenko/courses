# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

FILLED = "#eafaf0"   # зайнята комірка (світло-зелена)
FSTK   = FIELD
EMPTY  = "#f4f6f8"   # вільна комірка


def cell_positions(cx, cy, R, n=8, start_deg=-90):
    """Центри n комірок, розставлених по колу за годинниковою стрілкою."""
    pts = []
    for i in range(n):
        a = math.radians(start_deg + i * (360.0 / n))
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    return pts


# ── ring: прямий масив ↔ логічне коло ────────────────────────────────────────
# Ідея: те саме сховище показано двічі — рядком і кільцем; head/tail женуться
# одне за одним, а на кінці рядка спрацьовує загортання на нуль.

def fig_ring():
    W, H = 900, 450
    p = []
    occupied = {2, 3, 4, 5}     # tail=2 … head=6 (наступний запис)
    tail_i, head_i = 2, 6

    # ── ліва панель: лінійний масив ──
    p.append(text(250, 62, "Масив у пам'яті — прямий", size=13, color=INK, bold=True))
    n = 8
    cw, ch = 46, 46
    x0, y0 = 40, 150
    for i in range(n):
        x = x0 + i * cw
        fill = FILLED if i in occupied else EMPTY
        stk = FSTK if i in occupied else LINE
        p.append(rect(x, y0, cw - 6, ch, fill=fill, stroke=stk, sw=1.4, rx=4))
        p.append(text(x + (cw - 6) / 2, y0 + ch / 2 + 4, str(i), size=11, color=MUTED))
    # tail-покажчик знизу
    tx = x0 + tail_i * cw + (cw - 6) / 2
    p.append(arrow(tx, y0 + ch + 44, tx, y0 + ch + 6, color=NEG, sw=2.0))
    p.append(text(tx, y0 + ch + 62, "tail", size=12, color=NEG, bold=True))
    p.append(text(tx, y0 + ch + 78, "(читати)", size=9.5, color=MUTED))
    # head-покажчик зверху
    hx = x0 + head_i * cw + (cw - 6) / 2
    p.append(arrow(hx, y0 - 40, hx, y0 - 4, color=POS, sw=2.0))
    p.append(text(hx, y0 - 50, "head", size=12, color=POS, bold=True))
    p.append(text(hx + 34, y0 - 50, "(писати)", size=9.5, color=MUTED, anchor="start"))
    # дужка «зайнято» під зайнятими комірками
    ux1 = x0 + tail_i * cw
    ux2 = x0 + (head_i) * cw - 6
    p.append(text((ux1 + ux2) / 2, y0 + ch + 104, "зайнята ділянка", size=10, color=FIELD, bold=True))
    # стрілка загортання: від кінця масиву назад на початок
    ex = x0 + n * cw - 6
    p.append(line(ex, y0 + ch + 14, ex, y0 + ch + 30, color=MUTED, sw=1.6, dash="5 4"))
    p.append(line(ex, y0 + ch + 30, x0 - 4, y0 + ch + 30, color=MUTED, sw=1.6, dash="5 4"))
    p.append(arrow(x0 - 4, y0 + ch + 30, x0 - 4, y0 + ch + 14, color=MUTED, sw=1.6))
    p.append(text((x0 + ex) / 2, y0 + ch + 128, "кінець → загортання на 0  (mod N)",
                  size=10, color=MUTED))

    # роздільник
    p.append(line(470, 70, 470, H - 40, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── права панель: кільце ──
    cx, cy, R = 690, 250, 118
    p.append(text(cx, 62, "Те саме сховище — як коло", size=13, color=INK, bold=True))
    pts = cell_positions(cx, cy, R, n)
    cs = 40
    for i, (x, y) in enumerate(pts):
        fill = FILLED if i in occupied else EMPTY
        stk = FSTK if i in occupied else LINE
        p.append(rect(x - cs / 2, y - cs / 2, cs, cs, fill=fill, stroke=stk, sw=1.4, rx=5))
        p.append(text(x, y + 4, str(i), size=11, color=INK))
    # head / tail покажчики зовні (радіально)
    def radial_ptr(i, label, col):
        x, y = pts[i]
        ux = cx + (R + 60) * (x - cx) / R
        uy = cy + (R + 60) * (y - cy) / R
        ex_ = cx + (R + cs / 2 + 6) * (x - cx) / R
        ey_ = cy + (R + cs / 2 + 6) * (y - cy) / R
        p.append(arrow(ux, uy, ex_, ey_, col, sw=2.0))
        p.append(text(ux + 8 * (1 if x >= cx else -1), uy + 4, label, size=12, color=col,
                      bold=True, anchor="start" if x >= cx else "end"))
    radial_ptr(tail_i, "tail", NEG)
    radial_ptr(head_i, "head", POS)
    p.append(text(cx, cy - 4, "по колу", size=10.5, color=MUTED))
    p.append(text(cx, cy + 12, "за стрілкою", size=10.5, color=MUTED))

    render(os.path.join(OUT, "ring.svg"), W, H, *p,
           title="Прямий масив стає кільцем не в пам'яті, а в рахунку індексів")


# ── ambiguity: порожній і повний однакові з вигляду ──────────────────────────
# Ідея: два кільця — одне порожнє, одне повне — дають рівно head == tail; отже
# самих індексів мало, і нижче наведено три правила, що розрізняють стани.

def fig_ambiguity():
    W, H = 900, 540
    p = []
    n = 8
    cs = 30

    def mini_ring(cx, cy, R, filled, caption, capcol):
        pts = cell_positions(cx, cy, R, n)
        for i, (x, y) in enumerate(pts):
            fill = FILLED if filled else EMPTY
            stk = FSTK if filled else LINE
            p.append(rect(x - cs / 2, y - cs / 2, cs, cs, fill=fill, stroke=stk, sw=1.3, rx=4))
        # head==tail на комірці 0 (верх)
        x0, y0 = pts[0]
        p.append(arrow(x0, y0 - R * 0 - 58, x0, y0 - cs / 2 - 6, color=INK, sw=1.8))
        p.append(text(x0, y0 - 66, "head = tail", size=11.5, color=INK, bold=True))
        p.append(text(cx, cy + 4, caption, size=13, color=capcol, bold=True))

    # ліве — порожнє
    mini_ring(230, 175, 92, False, "порожньо", NEG)
    # праве — повне
    mini_ring(670, 175, 92, True, "повно", POS)
    # знак рівності-запитання посередині
    p.append(text(450, 168, "= ?", size=30, color=MUTED, bold=True))
    p.append(text(450, 205, "індекси однакові", size=10.5, color=MUTED))
    p.append(text(450, 222, "стани різні", size=10.5, color=MUTED))

    # ── три виходи ──
    p.append(text(W / 2, 322, "Три способи розрізнити:", size=13, color=INK, bold=True))
    boxw, boxh, gap = 258, 138, 26
    total = 3 * boxw + 2 * gap
    bx0 = (W - total) / 2
    by = 348
    notes = [
        ("1 · Жертва комірки",
         "Повним звемо на крок раніше:\n(head + 1) & (N−1) == tail.\n\nhead == tail — лише порожньо.\nЦіна: місткість падає до N−1."),
        ("2 · Лічильник size",
         "Окрема змінна рахує елементи.\nsize == 0 — порожньо,\nsize == N — повно.\n\nМісткість повна, але змінну\nпишуть обидві сторони."),
        ("3 · Монотонні індекси",
         "Індекси не загортаються.\nsize = head − tail.\nАдреса: pos & (N−1).\n\nСпільних записів немає —\nдружньо до lock-free."),
    ]
    cols = [NEG, INK, FIELD]
    for k, (title_, body) in enumerate(notes):
        x = bx0 + k * (boxw + gap)
        p.append(rect(x, by, boxw, boxh, fill="#fbfcfd", stroke=cols[k], sw=1.6, rx=8))
        p.append(text(x + boxw / 2, by + 24, title_, size=12, color=cols[k], bold=True))
        p.append(line(x + 16, by + 34, x + boxw - 16, by + 34, color="#e2e6ea", sw=1.0))
        p.append(mtext(x + boxw / 2, by + 56, body, size=10.5, color=INK, lh=1.28))

    render(os.path.join(OUT, "ambiguity.svg"), W, H, *p,
           title="Порожній і повний буфер з вигляду однакові: head == tail в обох")


# ── mask: степінь двійки → маска замість ділення ─────────────────────────────
# Ідея: лічильник pos росте безмежно, а індекс pos & 7 циклиться 0..7; знизу —
# порозрядний розбір, що І з маскою лишає рівно молодші біти = остача.

def fig_mask():
    W, H = 900, 450
    p = []

    # ── верх: pos росте, index = pos & 7 циклиться ──
    p.append(text(W / 2, 60, "Лічильник pos росте безмежно — індекс pos & 7 ходить по колу 0…7",
                  size=12.5, color=INK, bold=True))
    ncol = 10
    cw = 74
    x0 = (W - ncol * cw) / 2 + 6
    yp, yi = 92, 150
    ch = 34
    for i in range(ncol):
        x = x0 + i * cw
        idx = i & 7
        # рядок pos
        p.append(rect(x, yp, cw - 12, ch, fill="#eef4ff", stroke=NEG, sw=1.2, rx=4))
        p.append(text(x + (cw - 12) / 2, yp + 22, str(i), size=13, color=INK, bold=True))
        # рядок index
        wrapped = (i >= 8)
        p.append(rect(x, yi, cw - 12, ch, fill=(FILLED if wrapped else "#fbfcfd"),
                      stroke=(FSTK if wrapped else LINE), sw=1.2, rx=4))
        p.append(text(x + (cw - 12) / 2, yi + 22, str(idx), size=13,
                      color=(FIELD if wrapped else INK), bold=True))
        # стрілка pos → index
        p.append(arrow(x + (cw - 12) / 2, yp + ch + 2, x + (cw - 12) / 2, yi - 3,
                       color=MUTED, sw=1.2))
    p.append(text(x0 - 14, yp + 22, "pos", size=12, color=NEG, bold=True, anchor="end"))
    p.append(text(x0 - 14, yi + 22, "pos & 7", size=12, color=FIELD, bold=True, anchor="end"))
    # позначка загортання під першою «загорнутою» коміркою (i=8)
    xw = x0 + 8 * cw + (cw - 12) / 2
    p.append(text(xw, yi + ch + 18, "↑ загорнулося на 0", size=10, color=FIELD, bold=True))

    # ── низ: порозрядний розбір pos = 13 ──
    p.append(text(W / 2, 268, "Чому це працює: І з маскою лишає рівно молодші біти",
                  size=12.5, color=INK, bold=True))
    bits = [
        ("pos = 13", ["1", "1", "0", "1"], NEG, "#eef4ff"),
        ("маска = 7", ["0", "1", "1", "1"], MUTED, "#f4f6f8"),
        ("& = 5", ["0", "1", "0", "1"], FIELD, FILLED),
    ]
    bw = 40
    bx0 = W / 2 - (4 * bw) / 2 + 40
    ry0 = 292
    rh = 34
    # зелена підсвітка трьох молодших розрядів (спільна колонка на всі рядки)
    lowx = bx0 + 1 * bw
    p.append(rect(lowx - 3, ry0 - 6, 3 * bw + 6, 3 * rh + 12, fill="#eafaf0",
                  stroke=FIELD, sw=1.4, rx=6))
    for r, (lab, row, col, cellfill) in enumerate(bits):
        y = ry0 + r * rh
        p.append(text(bx0 - 18, y + rh / 2 + 5, lab, size=12, color=col, bold=True, anchor="end"))
        for c, b in enumerate(row):
            x = bx0 + c * bw
            muted_hi = (c == 0)   # старший біт, який маска відкидає
            p.append(rect(x, y, bw - 6, rh - 6,
                          fill=(EMPTY if muted_hi else cellfill),
                          stroke=(("#c7ccd2") if muted_hi else col), sw=1.2, rx=3))
            p.append(text(x + (bw - 6) / 2, y + (rh - 6) / 2 + 5, b, size=13,
                          color=("#b8bdc4" if muted_hi else INK), bold=True))
    p.append(text(lowx + 3 * bw / 2, ry0 + 3 * rh + 20, "три молодші біти = остача від ділення на 8",
                  size=10.5, color=FIELD, bold=True))
    p.append(text(bx0 + bw / 2, ry0 + 3 * rh + 40, "відкинуто", size=9.5, color=MUTED))

    render(os.path.join(OUT, "mask.svg"), W, H, *p,
           title="Степінь двійки: pos & (N−1) — це те саме, що pos mod N, за одну інструкцію")


# ── residues: голубник — N+1 зайнятостей не влазять у N залишків ─────────────
# Ідея (вставка math): зайнятість мусить бути функцією від (head, tail), і ця
# функція змушено дорівнює (head − tail) mod N. Залишок бере N значень, а
# зайнятостей N+1 — злиття неминуче, і зливаються РІВНО 0 та N. Це той один
# втрачений біт, по-різному доплачений трьома способами.

def fig_residues():
    W, H = 900, 580
    p = []
    N = 4
    p.append(text(W / 2, 60,
                  "N = 4: зайнятість буває 0…4 — це п'ять станів, а залишок (head − tail) mod 4 має чотири значення",
                  size=11.5, color=MUTED))

    cw, bw, bh = 76, 68, 38
    x0 = 310
    yo, yr = 100, 250
    occ_cx = [x0 + i * cw + bw / 2 for i in range(N + 1)]
    res_cx = [x0 + i * cw + bw / 2 for i in range(N)]

    # рядок зайнятості: 0 і N — ті, що зіллються
    for i in range(N + 1):
        hot = (i == 0 or i == N)
        p.append(rect(x0 + i * cw, yo, bw, bh, fill=("#fdecea" if hot else FILLED),
                      stroke=(POS if hot else FIELD), sw=1.5, rx=5))
        p.append(text(occ_cx[i], yo + bh / 2 + 5, str(i), size=14,
                      color=(POS if hot else INK), bold=True))
    p.append(text(x0 - 16, yo + bh / 2 + 5, "зайнятість size", size=12,
                  color=INK, bold=True, anchor="end"))

    # рядок залишків: значень рівно N
    for i in range(N):
        hot = (i == 0)
        p.append(rect(x0 + i * cw, yr, bw, bh, fill=("#fdecea" if hot else FILLED),
                      stroke=(POS if hot else FIELD), sw=1.5, rx=5))
        p.append(text(res_cx[i], yr + bh / 2 + 5, str(i), size=14,
                      color=(POS if hot else INK), bold=True))
    p.append(text(x0 - 16, yr + bh / 2 + 5, "(head − tail) mod N", size=12,
                  color=INK, bold=True, anchor="end"))

    # прямі стрілки: решта зайнятостей лягає взаємно однозначно
    for i in range(N):
        p.append(arrow(occ_cx[i], yo + bh + 3, res_cx[i], yr - 4,
                       color=(POS if i == 0 else FIELD), sw=1.6))

    # обхідна стрілка N → залишок 0: друга стрілка в ту саму комірку
    yl = 320
    p.append(line(occ_cx[N], yo + bh + 3, occ_cx[N], yl, color=POS, sw=1.8))
    p.append(line(occ_cx[N], yl, res_cx[0], yl, color=POS, sw=1.8))
    p.append(arrow(res_cx[0], yl, res_cx[0], yr + bh + 4, color=POS, sw=1.8))
    p.append(text(496, 346, "size = 0 і size = N дають той самий залишок — рівно тут гине інформація",
                  size=11.5, color=POS, bold=True))

    p.append(textbox(790, 186, "5 станів → 4 залишки.\nЗлиття неминуче:\nзначень більше,\nніж комірок під них.\nЗливаються рівно\n0 і N.",
                     size=10.5, pad=10, fill="#fbfcfd", stroke=MUTED, sw=1.4)[0])

    # ── три способи доплатити той самий біт ──
    p.append(text(W / 2, 394, "Три способи дістати цей один біт:", size=13, color=INK, bold=True))
    boxw, boxh, gap = 254, 140, 24
    bx0 = (W - (3 * boxw + 2 * gap)) / 2
    by = 416
    notes = [
        ("1 · Жертва комірки",
         "Забороняємо size = N.\nЛишається 0…N−1 — рівно\nстільки, скільки й кодує\nзалишок. Нічого зайвого\nне зберігаємо.\nМісткість: N−1."),
        ("2 · Лічильник size",
         "Зберігаємо зайнятість\nокремо (досить і одного\nбіта «повно»).\nМісткість: N — але цей\nбіт пишуть обидві\nсторони."),
        ("3 · Більший модуль",
         "Не зводимо за N: індекси\nживуть за модулем 2ᴮ.\nЗливаються 0 і 2ᴮ,\nа не 0 і N.\nМісткість: N, якщо\nN ≤ 2ᴮ − 1."),
    ]
    cols = [NEG, INK, FIELD]
    for k, (t_, body) in enumerate(notes):
        x = bx0 + k * (boxw + gap)
        p.append(rect(x, by, boxw, boxh, fill="#fbfcfd", stroke=cols[k], sw=1.6, rx=8))
        p.append(text(x + boxw / 2, by + 24, t_, size=12, color=cols[k], bold=True))
        p.append(line(x + 16, by + 34, x + boxw - 16, by + 34, color="#e2e6ea", sw=1.0))
        p.append(mtext(x + boxw / 2, by + 56, body, size=10.5, color=INK, lh=1.3))

    render(os.path.join(OUT, "residues.svg"), W, H, *p,
           title="Голубник: N+1 зайнятостей не влазять у N залишків")


# ── divides: чому монотонним лічильникам N мусить ділити 2ᴮ ──────────────────
# Ідея (вставка math): у змінній лежить h = H mod 2ᴮ, а треба H mod N. Ці дві
# величини збігаються для всіх H тоді й лише тоді, коли N ділить 2ᴮ. Панель
# зверху — N = 8 (ділить 16), знизу — N = 6 (не ділить): рівно на переповненні
# обчислений індекс розходиться з правильним.

def fig_divides():
    W, H = 900, 575
    p = []
    cw, bw, bh = 76, 64, 34
    x0 = 330
    cxs = [x0 + i * cw + bw / 2 for i in range(6)]

    wrapcol = [MUTED, MUTED, MUTED, POS, POS, POS]
    wrapfill = [EMPTY, EMPTY, EMPTY, "#fdecea", "#fdecea", "#fdecea"]
    okcol = [FIELD] * 6
    okfill = [FILLED] * 6
    badcol = [FIELD, FIELD, FIELD, POS, POS, POS]
    badfill = [FILLED, FILLED, FILLED, "#fdecea", "#fdecea", "#fdecea"]

    def row(y, label, labcol, vals, cellcol, cellfill):
        p.append(text(x0 - 14, y + bh / 2 + 5, label, size=11, color=labcol,
                      bold=True, anchor="end"))
        for i, v in enumerate(vals):
            p.append(rect(x0 + i * cw, y, bw, bh, fill=cellfill[i],
                          stroke=cellcol[i], sw=1.3, rx=4))
            p.append(text(cxs[i], y + bh / 2 + 5, str(v), size=13, color=INK, bold=True))

    # ── панель A: N = 8 ділить 16 ──
    p.append(text(W / 2, 58, "N = 8 ділить 16 — переповнення лічильника кільце не помітило",
                  size=12.5, color=FIELD, bold=True))
    yA = 84
    row(yA,       "H — справжній лічильник",   NEG,   [13, 14, 15, 16, 17, 18], [NEG] * 6, ["#eef4ff"] * 6)
    row(yA + 44,  "h = H mod 16 — у змінній",  MUTED, [13, 14, 15, 0, 1, 2],    wrapcol, wrapfill)
    row(yA + 88,  "h & 7 — що обчислили",      FIELD, [5, 6, 7, 0, 1, 2],       okcol, okfill)
    row(yA + 132, "H mod 8 — що мало бути",    INK,   [5, 6, 7, 0, 1, 2],       okcol, okfill)
    p.append(line(552, yA - 6, 552, yA + 132 + bh + 6, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text(W / 2, 274, "два нижні рядки збігаються — індекс іде далі, наче нічого не сталося",
                  size=11.5, color=FIELD, bold=True))

    p.append(line(60, 300, W - 60, 300, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── панель B: N = 6 не ділить 16 ──
    p.append(text(W / 2, 332, "N = 6 не ділить 16 — рівно на переповненні кільце ламається",
                  size=12.5, color=POS, bold=True))
    yB = 358
    row(yB,       "H — справжній лічильник",   NEG,   [13, 14, 15, 16, 17, 18], [NEG] * 6, ["#eef4ff"] * 6)
    row(yB + 44,  "h = H mod 16 — у змінній",  MUTED, [13, 14, 15, 0, 1, 2],    wrapcol, wrapfill)
    row(yB + 88,  "h mod 6 — що обчислили",    POS,   [1, 2, 3, 0, 1, 2],       badcol, badfill)
    row(yB + 132, "H mod 6 — що мало бути",    INK,   [1, 2, 3, 4, 5, 0],       badcol, badfill)
    p.append(line(552, yB - 6, 552, yB + 132 + bh + 6, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text(W / 2, 548, "з колонки H = 16 обчислений індекс розходиться з правильним — буфер поїхав",
                  size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "divides.svg"), W, H, *p,
           title="Монотонні лічильники: N мусить ділити 2ᴮ")


# ── policies: дві чесні відповіді на повний буфер ────────────────────────────
# Ідея (вставка proj): той самий повний буфер і той самий новий елемент X — але
# дві політики. Ліворуч виробник дістає відмову й гальмує (жоден байт не
# втрачено); праворуч виробник не чекає ніколи, а найстаріший елемент гине.
# Показано стан лічильників до/після — бо вся різниця в коді це один рядок.

def fig_policies():
    W, H = 980, 450
    n = 8
    cw, ch = 44, 46
    PW = 470
    p = []

    # слоти: 0:'G' 1:'H' 2:'A'(найстаріша) 3:'B' 4:'C' 5:'D' 6:'E' 7:'F'
    # монотонні лічильники: tail = 2, head = 10 → count = 8 = CAP; обидва → слот 2
    base  = ['G', 'H', 'A', 'B', 'C', 'D', 'E', 'F']
    after = ['G', 'H', 'X', 'B', 'C', 'D', 'E', 'F']

    def panel(px, title, sub, tcolor, letters, write_i, ptr_i, hot_i, refuse, notes):
        q = []
        q.append(text(px + PW / 2, 58, title, size=14.5, color=tcolor, bold=True))
        q.append(text(px + PW / 2, 78, sub, size=11, color=MUTED))

        x0, y0 = px + (PW - n * cw) / 2, 200
        for i in range(n):
            x = x0 + i * cw
            hot = (i == hot_i)
            q.append(rect(x, y0, cw - 6, ch, fill=("#fdecea" if hot else FILLED),
                          stroke=(POS if hot else FSTK), sw=(2.2 if hot else 1.4), rx=4))
            q.append(text(x + (cw - 6) / 2, y0 + ch / 2 + 6, letters[i],
                          size=15, color=(POS if hot else INK), bold=True))
            q.append(text(x + (cw - 6) / 2, y0 - 12, str(i), size=10, color=MUTED))

        wx = x0 + write_i * cw + (cw - 6) / 2     # куди ліг би / ліг X
        cx = x0 + ptr_i * cw + (cw - 6) / 2       # де стоять head/tail ПІСЛЯ

        q.append(text(wx, 102, "новий елемент", size=10, color=MUTED))
        q.append(rect(wx - 17, 110, 34, 34, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
        q.append(text(wx, 133, "X", size=15, color=POS, bold=True))

        if refuse:
            q.append(line(wx, 148, wx, 178, color=POS, sw=2.0, dash="5 4"))
            q.append(line(wx - 11, 152, wx + 11, 174, color=POS, sw=2.8))
            q.append(line(wx + 11, 152, wx - 11, 174, color=POS, sw=2.8))
            q.append(text(wx + 96, 168, "push() → false", size=11.5, color=POS, bold=True))
        else:
            q.append(arrow(wx, 148, wx, y0 - 26, color=POS, sw=2.2))
            q.append(text(wx + 104, 168, "«A» затерто", size=11.5, color=POS, bold=True))

        # після операції head і tail знову дивляться в ту саму комірку — знову повно
        q.append(arrow(cx - 44, 302, cx - 8, y0 + ch + 6, color=POS, sw=2.0))
        q.append(text(cx - 64, 318, "head", size=12, color=POS, bold=True))
        q.append(arrow(cx + 44, 302, cx + 8, y0 + ch + 6, color=NEG, sw=2.0))
        q.append(text(cx + 64, 318, "tail", size=12, color=NEG, bold=True))

        q.append(mtext(px + PW / 2, 358, notes, size=11.5, color=INK, lh=1.5))
        return q

    p += panel(10, "Політика 1 — відмова (протитиск)",
               "буфер недоторканий, гальмує виробник", NEG,
               base, write_i=2, ptr_i=2, hot_i=-1, refuse=True, notes=[
                   "до:  head = 10, tail = 2 → count = 8 = CAP → ПОВНО",
                   "rb3_push() повернув false; head і tail не зрушили",
                   "жоден байт не втрачено — гальмує виробник",
               ])
    p += panel(500, "Політика 2 — затирання найстарішого",
               "виробник не чекає ніколи", POS,
               after, write_i=2, ptr_i=3, hot_i=2, refuse=False, notes=[
                   "до:  head = 10, tail = 2 → count = 8 = CAP → ПОВНО",
                   "tail++ → 3 («A» гине); data[10 & 7] = X; head++ → 11",
                   "count = 11 − 3 = 8 — у буфері останні 8 елементів",
               ])
    p.append(line(490, 45, 490, 420, color="#d8dde3", sw=1.4, dash="6 5"))

    render(os.path.join(OUT, "policies.svg"), W, H, *p,
           title="Буфер повний, виробник несе новий елемент — дві чесні відповіді")


# ── false-sharing: сусідні head і tail в одному рядку кеша ───────────────────
# Ідея (вставка proj): логічно змінні різні й спільної серед них нема, а фізично
# вони в одному рядку — і ядра вибивають цей рядок одне в одного на кожній
# операції. alignas(64) розводить їх: ціна — паддинг, зиск — тиша на шині.

def fig_false_sharing():
    W, H = 980, 450
    PW = 460
    p = []

    def core(cx_c, label, color):
        b, _, _ = textbox(cx_c, 130, label, size=11.5, pad=9,
                          fill=("#fdecea" if color == POS else "#eaf0fd"),
                          stroke=color, color=INK)
        return b

    # ── ліворуч: один рядок на двох ──
    pxL = 10
    p.append(text(pxL + PW / 2, 58, "Як буває: head і tail — сусіди", size=14.5, color=POS, bold=True))
    p.append(text(pxL + PW / 2, 78, "обидва лягли в ОДИН рядок кеша", size=11, color=MUTED))
    p.append(core(pxL + 110, "Ядро 1 — виробник\nпише head", POS))
    p.append(core(pxL + 340, "Ядро 2 — споживач\nпише tail", NEG))
    p.append(rect(pxL + 30, 215, PW - 60, 58, fill="#fdecea", stroke=POS, sw=2.2, rx=6))
    p.append(rect(pxL + 42, 228, 54, 32, fill=BG, stroke=POS, sw=1.6, rx=4))
    p.append(text(pxL + 69, 249, "head", size=11.5, color=POS, bold=True))
    p.append(rect(pxL + 100, 228, 54, 32, fill=BG, stroke=NEG, sw=1.6, rx=4))
    p.append(text(pxL + 127, 249, "tail", size=11.5, color=NEG, bold=True))
    p.append(text(pxL + 300, 249, "решта рядка — 56 Б", size=10.5, color=MUTED))
    p.append(arrow(pxL + 110, 156, pxL + 69, 224, color=POS, sw=2.0))
    p.append(arrow(pxL + 340, 156, pxL + 127, 224, color=NEG, sw=2.0))
    p.append(text(pxL + PW / 2, 294, "один рядок кеша, 64 Б — і head, і tail у ньому",
                  size=11.5, color=POS, bold=True))
    p.append(mtext(pxL + PW / 2, 336, [
        "Змінні різні — рядок один. Запис head робить увесь",
        "рядок недійсним у кеші сусіда: наступне читання tail —",
        "промах. Рядок пінг-понгує між ядрами на КОЖНІЙ операції,",
        "хоча жодної спільної змінної тут насправді нема.",
    ], size=11.5, color=INK, lh=1.5))

    # ── праворуч: кожному свій рядок ──
    pxR = 510
    p.append(text(pxR + PW / 2, 58, "Як треба: alignas(64)", size=14.5, color=FIELD, bold=True))
    p.append(text(pxR + PW / 2, 78, "кожен покажчик — у власному рядку", size=11, color=MUTED))
    p.append(core(pxR + 110, "Ядро 1 — виробник\nпише head", POS))
    p.append(core(pxR + 340, "Ядро 2 — споживач\nпише tail", NEG))
    p.append(rect(pxR + 25, 215, 190, 58, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=6))
    p.append(rect(pxR + 36, 228, 54, 32, fill=BG, stroke=POS, sw=1.6, rx=4))
    p.append(text(pxR + 63, 249, "head", size=11.5, color=POS, bold=True))
    p.append(text(pxR + 155, 249, "паддинг", size=10.5, color=MUTED))
    p.append(rect(pxR + 245, 215, 190, 58, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=6))
    p.append(rect(pxR + 256, 228, 54, 32, fill=BG, stroke=NEG, sw=1.6, rx=4))
    p.append(text(pxR + 283, 249, "tail", size=11.5, color=NEG, bold=True))
    p.append(text(pxR + 375, 249, "паддинг", size=10.5, color=MUTED))
    p.append(arrow(pxR + 110, 156, pxR + 80, 210, color=POS, sw=2.0))
    p.append(arrow(pxR + 340, 156, pxR + 320, 210, color=NEG, sw=2.0))
    p.append(text(pxR + 120, 294, "рядок №1 — лише head", size=10.5, color=FIELD, bold=True))
    p.append(text(pxR + 340, 294, "рядок №2 — лише tail", size=10.5, color=FIELD, bold=True))
    p.append(mtext(pxR + PW / 2, 336, [
        "Ядра більше не зачіпають рядка одне одного: кожне",
        "тримає свій у власному кеші й ганяє його без завад.",
        "Ціна — паддинг (тут 128 Б замість 8); зиск на гарячому",
        "шляху добре помітний.",
    ], size=11.5, color=INK, lh=1.5))

    p.append(line(490, 45, 490, 420, color="#d8dde3", sw=1.4, dash="6 5"))

    render(os.path.join(OUT, "false-sharing.svg"), W, H, *p,
           title="Хибне спільне: логічно змінні різні, фізично — один рядок кеша")


if __name__ == "__main__":
    fig_ring()
    fig_ambiguity()
    fig_mask()
    fig_residues()
    fig_divides()
    fig_policies()
    fig_false_sharing()
    print("figs: готово")
