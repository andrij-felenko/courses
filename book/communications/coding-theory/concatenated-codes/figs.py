# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Семантичні кольори (єдині на всі фігури теми)
DATA_F, DATA_S = "#eafaee", FIELD        # чисті дані — зелені
BAD_F,  BAD_S  = "#fdeceb", POS          # биті — гарячі
OUT_C          = POS                     # зовнішній код — червоний
IN_C           = NEG                     # внутрішній код — синій
CHAN_C         = "#caa24a"               # канал — бурштин
MSG_C          = FIELD                   # повідомлення — зелене


def polyline(pts, color, sw=3.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── pipeline: кодуємо ззовні всередину, декодуємо у зворотному порядку ─────────
def fig_pipeline():
    W, H = 940, 350
    p = []

    def stage(x, y, w, label, col, sub=None):
        out = rect(x, y, w, 50, fill=(BG if col is INK else col + "12"), stroke=col, sw=2.2, rx=8)
        if sub:
            out += text(x + w / 2, y + 21, label, size=12, color=col, bold=True)
            out += text(x + w / 2, y + 39, sub, size=9.5, color=MUTED)
        else:
            out += text(x + w / 2, y + 30, label, size=12, color=col, bold=True)
        return out

    # верх — КОДУВАННЯ (зліва направо)
    y1 = 66
    p.append(text(30, y1 - 14, "кодуємо — зовнішній, потім внутрішній:", size=12.5, color=INK, anchor="start", bold=True))
    seq = [
        (110, "повідомлення", MSG_C, "дані"),
        (176, "зовнішній код", OUT_C, "+ контрольні символи"),
        (128, "перемішування", CHAN_C, "interleaving"),
        (140, "внутрішній код", IN_C, "поверх зовнішнього"),
        (78,  "канал", CHAN_C, None),
    ]
    x = 30
    for i, (w, lab, col, sub) in enumerate(seq):
        p.append(stage(x, y1, w, lab, col, sub))
        x2 = x + w
        if i < len(seq) - 1:
            p.append(arrow(x2 + 4, y1 + 25, x2 + 30, y1 + 25, color=INK))
        x = x2 + 34

    # середина — напрям і наймення
    ym = 176
    p.append(text(W / 2, ym, "у каналі — і рідкий шум, і зрідка цілий пакет; на прийомі шари знімають У ЗВОРОТНОМУ ПОРЯДКУ",
                  size=11.5, color=CHAN_C, bold=True))

    # низ — ДЕКОДУВАННЯ (зліва направо: зворотні операції)
    y2 = 214
    p.append(text(30, y2 - 14, "декодуємо — спершу внутрішній, тоді зовнішній:", size=12.5, color=INK, anchor="start", bold=True))
    seq2 = [
        (78,  "з каналу", CHAN_C, None),
        (168, "внутрішній декодер", IN_C, "гасить рідкий шум"),
        (192, "зворотне перемішування", CHAN_C, "de-interleaving"),
        (176, "зовнішній декодер", OUT_C, "замітає пакети"),
        (118, "повідомлення", MSG_C, "без діри"),
    ]
    x = 30
    for i, (w, lab, col, sub) in enumerate(seq2):
        p.append(stage(x, y2, w, lab, col, sub))
        x2 = x + w
        if i < len(seq2) - 1:
            col_a = MSG_C if i == len(seq2) - 2 else INK
            p.append(arrow(x2 + 4, y2 + 25, x2 + 30, y2 + 25, color=col_a))
        x = x2 + 34

    # підпис-наймення
    p.append(text(W / 2, 306, "«Внутрішній» — той, що ближчий до каналу (бачить сирий шум).   "
                              "«Зовнішній» — ближчий до даних (чистить залишок).",
                  size=11.5, color=INK))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p)


# ── cleanup: канал → після внутрішнього (пакет) → після зовнішнього (чисто) ────
def fig_cleanup():
    W, H = 900, 400
    p = []
    n = 40
    cw, gap = 15, 2
    x0 = 210
    row_h = 26

    def strip(y, title, bad_set, title_col):
        out = mtext(20, y + 4, title, size=11.5, color=title_col, anchor="start", bold=True)
        for k in range(n):
            bx = x0 + k * (cw + gap)
            f, s = (BAD_F, BAD_S) if k in bad_set else (DATA_F, DATA_S)
            out += rect(bx, y - row_h / 2, cw, row_h, fill=f, stroke=s, sw=1.2, rx=2)
        return out

    # A: після каналу — рідкі поодинокі помилки
    yA = 80
    scattered = {3, 9, 16, 21, 27, 33, 38}
    p.append(strip(yA, "після каналу", scattered, CHAN_C))
    p.append(text((x0 + n * (cw + gap) / 2), yA + 40, "канал сипле рідкі поодинокі помилки — розкидані по всьому блоку",
                  size=11, color=MUTED))

    # B: після внутрішнього декодера — шум прибрано, але лишився компактний ПАКЕТ
    yB = 185
    burst = set(range(22, 30))
    p.append(strip(yB, "після\nвнутрішнього\nдекодера", burst, IN_C))
    bx0 = x0 + 22 * (cw + gap) - 3
    bx1 = x0 + 30 * (cw + gap)
    p.append(rect(bx0, yB - row_h / 2 - 5, bx1 - bx0, row_h + 10, fill="none", stroke=IN_C, sw=2, rx=4))
    p.append(text((x0 + n * (cw + gap) / 2), yB + 44, "рідкий шум прибрано — але, спіткнувшись, декодер лишив компактний ПАКЕТ підряд",
                  size=11, color=IN_C, bold=True))

    # C: після зовнішнього декодера — чисто
    yC = 300
    p.append(strip(yC, "після\nзовнішнього\nдекодера", set(), OUT_C))
    p.append(text((x0 + n * (cw + gap) / 2), yC + 40, "символьний зовнішній код з'їв пакет цілком — дані відновлено без діри",
                  size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "cleanup.svg"), W, H, *p)


# ── complexity: один довгий код — вибух вартості; каскад — помірно ────────────
def fig_complexity():
    W, H = 840, 470
    p = []
    ox, oy = 96, 388          # початок осей
    xmax, ytop = 772, 78
    ceil_y = 150              # стеля здійсненного (значення вартості)
    cap_x = 690              # межа Шеннона (ємність)

    # осі
    p.append(arrow(ox, oy, ox, ytop - 4, color=INK, sw=2))
    p.append(arrow(ox, oy, xmax + 4, oy, color=INK, sw=2))
    p.append(text(ox - 8, ytop + 6, "вартість", size=11.5, color=INK, anchor="end", bold=True))
    p.append(text(ox - 8, ytop + 22, "декодування", size=11.5, color=INK, anchor="end", bold=True))
    p.append(text(xmax, oy + 26, "довжина / потужність коду →", size=11.5, color=INK, anchor="end", bold=True))

    # стеля здійсненного
    p.append(line(ox, ceil_y, xmax, ceil_y, color=MUTED, sw=1.6, dash="7 5"))
    p.append(text(ox + 8, ceil_y - 9, "стеля здійсненного (більше — не порахувати)", size=10.5, color=MUTED, anchor="start"))

    # межа Шеннона — вертикаль
    p.append(line(cap_x, oy, cap_x, ytop + 30, color=FIELD, sw=1.6, dash="6 5"))
    p.append(text(cap_x + 6, ytop + 40, "межа Шеннона", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(text(cap_x + 6, ytop + 55, "(пропускна здатність)", size=10, color=FIELD, anchor="start"))

    # крива A — один довгий (оптимальний) код: вибух ~2ⁿ
    A, scale = 0.5, 46.0
    ptsA = []
    xx = ox + 14
    while xx <= xmax:
        drop = A * (math.exp((xx - (ox + 14)) / scale) - 1)
        y = oy - drop
        if y < ytop + 6:
            ptsA.append((xx, ytop + 6)); break
        ptsA.append((xx, y)); xx += 3
    p.append(polyline(ptsA, OUT_C, sw=3.2))

    # крива B — конкатенація: поліном, лишається під стелею
    ptsB = []
    for k in range(0, 64):
        xx = ox + 14 + k * ((xmax - ox - 14) / 63.0)
        drop = 150.0 * (((xx - (ox + 14)) / (xmax - ox - 14)) ** 1.4)
        ptsB.append((xx, oy - drop))
    p.append(polyline(ptsB, FIELD, sw=3.2))

    # підписи кривих
    p.append(text(150, 112, "один довгий (оптимальний) код:", size=12, color=OUT_C, anchor="start", bold=True))
    p.append(text(150, 130, "вартість ~ 2ⁿ — швидко за межею здійсненного", size=11, color=OUT_C, anchor="start"))
    p.append(text(486, 334, "конкатенація: дві короткі ланки", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(486, 352, "декодуємо окремо — вартість помірна (поліном)", size=11, color=FIELD, anchor="start"))

    # ключ
    p.append(text(W / 2, 448, "Щоб дійти до межі Шеннона, потрібен довгий код. Конкатенація дає довгий код, який ще й можна декодувати.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "complexity.svg"), W, H, *p)


GOOD_C = FIELD                           # гарантовано лагодить
MAYBE_C = "#b8860b"                      # лагодить лише GMD
NEVER_C = POS                            # не лагодить ніхто


def brace(x1, x2, y, label, color, size=11.5, drop=8):
    """Проста скоба знизу: горизонталь із засічками + підпис під нею."""
    out = line(x1, y, x2, y, color=color, sw=1.6)
    out += line(x1, y, x1, y - drop, color=color, sw=1.6)
    out += line(x2, y, x2, y - drop, color=color, sw=1.6)
    out += text((x1 + x2) / 2, y + size + 4, label, size=size, color=color, bold=True)
    return out


# ── params: як із двох наборів чисел складається третій ───────────────────────
def fig_params():
    W, H = 980, 560
    p = []
    NS, SW, SG = 15, 38, 6
    pitch = SW + SG
    x0 = 252

    # ── лан A: кодове слово зовнішнього коду — лічба в СИМВОЛАХ ──────────────
    yA = 118
    p.append(mtext(20, yA + 4, ["зовнішній RS(15,11)", "над GF(16)", "лічить СИМВОЛИ"],
                   size=12, color=OUT_C, anchor="start", bold=True, lh=1.35))
    for i in range(NS):
        bx = x0 + i * pitch
        f, s = (DATA_F, DATA_S) if i < 11 else (BAD_F, BAD_S)
        p.append(rect(bx, yA, SW, 40, fill=f, stroke=s, sw=1.6, rx=4))
    p.append(brace(x0, x0 + 11 * pitch - SG, yA + 54, "K = 11 символів даних", FIELD))
    p.append(brace(x0 + 11 * pitch, x0 + NS * pitch - SG, yA + 54, "N − K = 4 контрольні", OUT_C))

    # ── напрямні зуму з символа №3 ───────────────────────────────────────────
    zx1, zx2 = x0 + 2 * pitch, x0 + 2 * pitch + SW
    p.append(rect(zx1 - 3, yA - 3, SW + 6, 46, fill="none", stroke=IN_C, sw=2.2, rx=5))
    zy = 236
    p.append(line(zx1, yA + 43, 252, zy, color=IN_C, sw=1.2, dash="4 4"))
    p.append(line(zx2, yA + 43, 366, zy, color=IN_C, sw=1.2, dash="4 4"))

    # ── смуга зуму: символ = k бітів → внутрішній кодер → n бітів ────────────
    p.append(mtext(20, zy + 26, ["внутрішній", "код [7,4,3]"], size=12, color=IN_C,
                   anchor="start", bold=True, lh=1.35))
    bw, bg = 24, 5
    for i in range(4):
        p.append(rect(252 + i * (bw + bg), zy + 12, bw, 30, fill=BG, stroke=IN_C, sw=1.6, rx=3))
    p.append(text(309, zy + 68, "k = 4 біти — рівно один символ GF(16)", size=11, color=IN_C))
    p.append(arrow(376, zy + 27, 414, zy + 27, color=INK))
    p.append(fitbox(420, zy + 8, 168, 38, "кодер [7,4,3]", size=12.5,
                    fill=IN_C + "12", stroke=IN_C, sw=2, color=IN_C, bold=True))
    p.append(arrow(598, zy + 27, 636, zy + 27, color=INK))
    for i in range(7):
        f = BG if i < 4 else IN_C + "22"
        p.append(rect(644 + i * (bw + bg), zy + 12, bw, 30, fill=f, stroke=IN_C, sw=1.6, rx=3))
    p.append(text(744, zy + 68, "n = 7 бітів у канал", size=11, color=IN_C))

    # ── лан B: і так КОЖЕН із N символів ─────────────────────────────────────
    yB = 400
    p.append(mtext(20, yB + 4, ["…і так КОЖЕН", "із N = 15 символів"],
                   size=12, color=INK, anchor="start", bold=True, lh=1.35))
    for i in range(NS):
        gx = x0 + i * pitch + 2
        for j in range(7):
            p.append(rect(gx + j * 5.0, yB, 4.0, 34,
                          fill=(DATA_F if i < 11 else BAD_F),
                          stroke=(DATA_S if i < 11 else BAD_S), sw=0.7, rx=1))
    p.append(brace(x0, x0 + NS * pitch - SG, yB + 48,
                   "у канал іде N · n = 15 · 7 = 105 бітів", INK, size=12.5))

    p.append(text(W / 2, 528, "Умова стикування: один символ зовнішнього коду має нести РІВНО стільки бітів, "
                              "скільки внутрішній кодер бере на вхід (k = 4).",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "params.svg"), W, H, *p)


# ── product-distance: чому відстані ПЕРЕМНОЖУЮТЬСЯ ────────────────────────────
def fig_product():
    W, H = 980, 590
    p = []
    NS, CW, CG = 15, 40, 6
    pitch = CW + CG
    x0 = 250
    A = list("37A15C92F06B4E8")
    B = list("372154D2F01B498")
    diff = [i for i in range(NS) if A[i] != B[i]]

    def row(y, syms, tag, tag_col):
        out = mtext(20, y + 4, tag, size=12, color=tag_col, anchor="start", bold=True, lh=1.35)
        for i, s in enumerate(syms):
            bx = x0 + i * pitch
            hot = i in diff
            f, st = (BAD_F, BAD_S) if hot else (FILL, MUTED)
            out += rect(bx, y, CW, 38, fill=f, stroke=st, sw=1.6, rx=4)
            out += text(bx + CW / 2, y + 25, s, size=15,
                        color=(POS if hot else MUTED), bold=True)
        return out

    yA, yB = 106, 214
    p.append(row(yA, A, ["кодове слово", "каскаду A"], INK))
    p.append(row(yB, B, ["кодове слово", "каскаду B"], INK))

    # ряд різниць між ланами
    for i in range(NS):
        cx = x0 + i * pitch + CW / 2
        if i in diff:
            p.append(text(cx, yB - 18, "≠", size=15, color=POS, bold=True))
        else:
            p.append(text(cx, yB - 18, "=", size=14, color=MUTED))

    p.append(brace(x0, x0 + NS * pitch - CG, yB + 54,
                   "зовнішній код гарантує: різних символів — щонайменше D = 5", POS, size=12.5))

    # ── зум на позицію, де символи різні ─────────────────────────────────────
    zi = diff[0]
    zy = 336
    p.append(rect(x0 + zi * pitch - 5, yA - 5, CW + 10, (yB + 38) - (yA - 5) + 5,
                  fill="none", stroke=IN_C, sw=2.4, rx=6))

    p.append(text(20, zy + 2, "зазирнімо всередину такої позиції:", size=12.5,
                  color=IN_C, anchor="start", bold=True))

    cA = "1010011"
    cB = "0010110"
    bw, bg = 44, 8
    bx0 = 250
    for k, (lab, bits, y) in enumerate([("символ A → внутрішнє слово", cA, zy + 22),
                                        ("символ 2 → внутрішнє слово", cB, zy + 82)]):
        p.append(text(bx0 - 8, y + 26, lab, size=11.5, color=INK, anchor="end"))
        for j, b in enumerate(bits):
            hot = cA[j] != cB[j]
            p.append(rect(bx0 + j * (bw + bg), y, bw, 38,
                          fill=(BAD_F if hot else DATA_F),
                          stroke=(BAD_S if hot else DATA_S), sw=1.6, rx=4))
            p.append(text(bx0 + j * (bw + bg) + bw / 2, y + 26, b, size=15,
                          color=(POS if hot else FIELD), bold=True))
    for j in range(7):
        if cA[j] != cB[j]:
            p.append(text(bx0 + j * (bw + bg) + bw / 2, zy + 74, "↕", size=14, color=POS, bold=True))
    p.append(brace(bx0, bx0 + 7 * (bw + bg) - bg, zy + 138,
                   "різні символи → РІЗНІ слова внутрішнього коду → різних бітів ≥ d = 3", IN_C, size=12.5))

    p.append(text(W / 2, 556, "≥ D позицій   ×   ≥ d бітів у кожній   =   ≥ D · d = 5 · 3 = 15 різних бітів. "
                              "Однакові символи дають однакові блоки — рівно 0.",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(OUT, "product-distance.svg"), W, H, *p)


# ── gmd-radius: наївний декодер губить половину запасу ────────────────────────
def fig_radius():
    W, H = 960, 430
    p = []
    x1, x2 = 200, 890
    ax = 214
    u = (x2 - x1) / 15.0

    def X(v):
        return x1 + v * u

    # смуги зон
    p.append(rect(X(0), ax - 20, X(5) - X(0), 40, fill="#eafaee", stroke=GOOD_C, sw=1.8, rx=4))
    p.append(rect(X(5), ax - 20, X(7) - X(5), 40, fill="#fdf5e0", stroke=MAYBE_C, sw=1.8, rx=4))
    p.append(rect(X(7), ax - 20, X(15) - X(7), 40, fill=BAD_F, stroke=NEVER_C, sw=1.8, rx=4))

    # вісь із поділками
    p.append(arrow(x1, ax + 44, x2 + 30, ax + 44, color=INK, sw=2))
    for v in range(16):
        p.append(line(X(v), ax + 44, X(v), ax + 51, color=INK, sw=1.4))
        p.append(text(X(v), ax + 68, str(v), size=11, color=MUTED))
    p.append(text(x2 + 30, ax + 92, "перевернутих бітів на блок зі 105 →", size=12,
                  color=INK, anchor="end", bold=True))

    # підписи зон — угорі, з великим просвітом
    p.append(text(X(2.5), ax - 40, "наївний каскад лагодить", size=12.5, color=GOOD_C, bold=True))
    p.append(text(X(6), ax - 62, "лагодить", size=12, color=MAYBE_C, bold=True))
    p.append(text(X(6), ax - 46, "лише GMD", size=12, color=MAYBE_C, bold=True))
    p.append(text(X(11), ax - 40, "не лагодить ніхто — за межею відстані", size=12.5, color=NEVER_C, bold=True))

    # позначка Dd/2
    p.append(line(X(7.5), ax - 96, X(7.5), ax + 32, color=INK, sw=1.8, dash="6 4"))
    p.append(text(X(7.5) - 8, ax - 106, "D·d / 2 = 7.5 — стеля однозначного декодування",
                  size=11.5, color=INK, anchor="end", bold=True))

    # позначка Dd
    p.append(line(X(15), ax - 96, X(15), ax + 32, color=OUT_C, sw=1.8, dash="6 4"))
    p.append(text(X(15), ax - 126, "D·d = 15", size=11.5, color=OUT_C, bold=True))
    p.append(text(X(15), ax - 110, "мін. відстань", size=11, color=OUT_C))

    # втрачений шматок
    p.append(line(X(5), ax + 108, X(7), ax + 108, color=MAYBE_C, sw=2.4))
    p.append(line(X(5), ax + 108, X(5), ax + 100, color=MAYBE_C, sw=2.4))
    p.append(line(X(7), ax + 108, X(7), ax + 100, color=MAYBE_C, sw=2.4))
    p.append(text(X(6), ax + 132, "цей шматок наївний декодер віддає задарма:", size=12,
                  color=MAYBE_C, bold=True))
    p.append(text(X(6), ax + 150, "код має запас, декодер — ні", size=12, color=MAYBE_C, bold=True))

    p.append(mtext(20, ax - 6, ["каскад", "RS(15,11) ∘ [7,4,3]", "= [105, 44, ≥15]"],
                   size=12, color=INK, anchor="start", bold=True, lh=1.35))

    p.append(text(W / 2, 404, "Той самий код, ті самі два декодери — але GMD витискає з них 7 замість 5, "
                              "бо не викидає інформацію про те, як важко далося внутрішнє рішення.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "gmd-radius.svg"), W, H, *p)


def drect(x, y, w, h, color=MUTED, sw=1.8, rx=10, dash="8 6"):
    """Пунктирна рамка БЕЗ тексту (написи — окремо)."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="none" '
            'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' % (x, y, w, h, rx, color, sw, dash))


# ── superchannel: кодер+канал+декодер, побачені ЗЗОВНІ, — це знову канал ───────
def fig_superchannel():
    W, H = 980, 580
    p = []
    bh = 56

    # 1. Сирий ланцюг
    p.append(text(34, 64, "1. Беремо звичайний ланцюг — кодер, канал, декодер:",
                  size=13, anchor="start", bold=True))
    yA = 126
    chain = [(206, 158, "внутрішній кодер", IN_C),
             (414, 122, "канал", CHAN_C),
             (622, 158, "внутрішній декодер", IN_C)]
    for (x, w, lab, col) in chain:
        p.append(fitbox(x, yA - bh / 2, w, bh, lab, size=12.5, color=col, stroke=col, sw=2, fill=col + "12"))
    p.append(arrow(368, yA, 410, yA, color=INK))
    p.append(arrow(540, yA, 618, yA, color=INK))
    p.append(drect(180, yA - bh / 2 - 30, 626, bh + 60, color=MUTED))
    p.append(text(820, yA - 6, "усе це разом", size=12, color=MUTED, anchor="start", bold=True))
    p.append(text(820, yA + 12, "— одна коробка", size=12, color=MUTED, anchor="start"))

    # 2. Погляд ззовні
    p.append(arrow(W / 2, 222, W / 2, 266, color=FIELD, sw=2.4))
    p.append(text(W / 2 + 16, 250, "дивимося ЗЗОВНІ — що в коробці, байдуже",
                  size=12.5, color=FIELD, anchor="start", bold=True))

    yB = 324
    p.append(fitbox(258, yB - 34, 452, 68,
                    "СУПЕРКАНАЛ:  eᴺᴿ входів, eᴺᴿ виходів,\nдуже рідко плутає вхід із виходом",
                    size=12.5, color=CHAN_C, stroke=CHAN_C, sw=2.4, fill=CHAN_C + "16"))
    p.append(text(730, yB - 16, "вхід, вихід і ймовірності", size=12, color=MUTED, anchor="start"))
    p.append(text(730, yB + 2, "помилки — це ВИЗНАЧЕННЯ", size=12, color=MUTED, anchor="start"))
    p.append(text(730, yB + 20, "каналу. Отже, це канал.", size=12, color=MUTED, anchor="start", bold=True))

    # 3. Кодуємо суперканал
    p.append(arrow(W / 2, 368, W / 2, 412, color=FIELD, sw=2.4))
    p.append(text(W / 2 + 16, 396, "а канал ми вміємо кодувати", size=12.5, color=FIELD, anchor="start", bold=True))

    yC = 470
    chain2 = [(206, 158, "зовнішній кодер", OUT_C),
              (414, 122, "суперканал", CHAN_C),
              (622, 158, "зовнішній декодер", OUT_C)]
    for (x, w, lab, col) in chain2:
        p.append(fitbox(x, yC - bh / 2, w, bh, lab, size=12.5, color=col, stroke=col, sw=2, fill=col + "12"))
    p.append(arrow(368, yC, 410, yC, color=INK))
    p.append(arrow(540, yC, 618, yC, color=INK))
    p.append(drect(180, yC - bh / 2 - 30, 626, bh + 60, color=FIELD))
    p.append(text(820, yC - 14, "і це — знову", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(820, yC + 4, "той самий рисунок:", size=12, color=FIELD, anchor="start"))
    p.append(text(820, yC + 22, "можна ще раз", size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "superchannel.svg"), W, H, *p,
           title="Кодування не виводить нас із класу каналів — тому крок можна повторювати")


# ── exchange: похибка не від ДОВЖИНИ, а від ЦІНИ ──────────────────────────────
def fig_exchange():
    W, H = 940, 560
    p = []
    ox, oy, xr, ytop = 130, 445, 900, 140

    # осі
    p.append(line(ox, ytop - 14, ox, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, xr + 6, oy, color=INK, sw=2))
    p.append(text(xr + 4, oy + 50, "вартість декодування G  (log) →", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 96, ytop - 24, "ймовірність", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ox - 96, ytop - 8, "похибки ↓", size=12, color=INK, anchor="start", bold=True))

    # позначки по осі похибки (лише засічки при осі — щоб жодна лінія не лізла
    # крізь написи всередині поля; сама фігура про ФОРМУ кривих, не про точні числа)
    for i, lb in enumerate(["10⁻²", "10⁻⁴", "10⁻⁶", "10⁻⁸", "10⁻¹⁰"]):
        yy = ytop + i * (oy - ytop) / 4.0
        p.append(line(ox - 6, yy, ox, yy, color=INK, sw=1.4))
        p.append(text(ox - 12, yy + 4, lb, size=11.5, color=MUTED, anchor="end"))

    # позначки ціни
    for i, lb in enumerate(["G", "×10", "×100", "×1000"]):
        xx = ox + 60 + i * (xr - ox - 90) / 3.0
        p.append(line(xx, oy, xx, oy + 6, color=INK, sw=1.4))
        p.append(text(xx, oy + 22, lb, size=11.5, color=MUTED))

    # A — один довгий код + оптимальний декодер: на log-log степенева = пряма
    p.append(polyline([(175 + k * (890 - 175) / 40.0, 168 + 100.0 * (k / 40.0)) for k in range(41)],
                      OUT_C, sw=3.2))
    # B — каскад: на малому бюджеті ГІРШИЙ за оптимальний (він-бо неоптимальний),
    # але від ціни падає майже вибухово й переганяє його — саме в цьому вся угода
    p.append(polyline([(175 + (k / 60.0) * (890 - 175), 152 + 286.0 * ((k / 60.0) ** 1.6)) for k in range(61)],
                      FIELD, sw=3.2))

    # напис при кривій A — у вільній смузі НАД нею, справа
    p.append(text(618, 182, "×1000 заліза — і лише сталий множник виграшу",
                  size=12, color=OUT_C, anchor="start", bold=True))
    p.append(text(618, 200, "(на log-log степенева — це пряма)", size=11.5, color=OUT_C, anchor="start"))

    # легенда — у порожньому куті ПІД обома кривими
    p.append(line(186, 311, 206, 311, color=OUT_C, sw=3.2))
    p.append(text(214, 316, "один довгий код + оптимальний декодер:", size=12, color=OUT_C, anchor="start", bold=True))
    p.append(text(214, 334, "Pr(e) ≈ G^(−E/R) — від ціни лише СТЕПЕНЕВА", size=12, color=OUT_C, anchor="start"))
    p.append(line(186, 366, 206, 366, color=FIELD, sw=3.2))
    p.append(text(214, 371, "каскад RS-ланок:  G ≈ L³", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(214, 389, "Pr(e) ≈ p₀^(L^(1−Δ)) — від ціни майже ВИБУХОВА", size=12, color=FIELD, anchor="start"))

    p.append(text(W / 2, 532, "Обіцянка Шеннона вибухова від ДОВЖИНИ. Але платять не за довжину — платять за декодер.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "exchange.svg"), W, H, *p,
           title="Та сама теорема в осі, за яку платять")


# ══ фігури вставки «Вояджери дзвонять додому» ═════════════════════════════════

EARTH_C = NEG                            # Земля — можна переробляти
BOARD_C = "#8a5a00"                      # борт — застигле залізо
WALL_C  = POS                            # мить запуску — стіна


# ── voyager-timeline: Земля рухається, борт застиг 1977-го ────────────────────
def fig_voyager_timeline():
    W, H = 1180, 500
    p = []
    ax_y = 262                            # вісь часу Землі
    x_launch = 410

    # вісь часу
    p.append(arrow(70, ax_y, 1150, ax_y, color=EARTH_C, sw=2.2))
    p.append(text(76, 286, "ЗЕМЛЯ: теорію й залізо переробляють далі",
                  size=12, color=EARTH_C, anchor="start", bold=True))

    # події Землі: (x, рівень A/B, рядки)
    BW, BH = 176, 62
    evA, evB = 90, 172                    # верхні краї двох рівнів
    events = [
        (95,  'A', ["1960", "Рід і Соломон", "друкують код"]),
        (200, 'B', ["1967", "Вітербі: алгоритм,", "автор — «непрактично»"]),
        (305, 'A', ["1971", "воркшоп:", "«кодування померло»"]),
        (560, 'A', ["1982", "Берлекамп чистить", "код → стандарт CCSDS"]),
        (700, 'B', ["1986", "наземний декодер", "RS нарешті готовий"]),
        (840, 'A', ["1990-і", "Big Viterbi Decoder:", "8192 ланок"]),
        (970, 'B', ["2000-і", "турбокоди", "й LDPC"]),
        (1095, 'A', ["2021", "аматор перечитує", "борт 1977-го"]),
    ]
    for (x, lvl, lines) in events:
        top = evA if lvl == 'A' else evB
        p.append(fitbox(x - BW / 2, top, BW, BH, lines, size=11.5,
                        fill=BG, stroke=EARTH_C, sw=1.8, color=EARTH_C))
        p.append(line(x, top + BH, x, ax_y - 6, color=EARTH_C, sw=1.3, dash="4 4"))
        p.append(circle(x, ax_y, 5, fill=EARTH_C, stroke=EARTH_C, sw=1))

    # стіна запуску
    p.append(line(x_launch, 56, x_launch, 478, color=WALL_C, sw=2.6, dash="9 6"))
    p.append(circle(x_launch, ax_y, 7, fill=WALL_C, stroke=WALL_C, sw=1))
    p.append(text(x_launch + 12, 44, "1977 — ЗАПУСК: остання мить, коли ще можна щось припаяти",
                  size=12.5, color=WALL_C, anchor="start", bold=True))

    # доріжка борту
    band_y = 334
    p.append(rect(x_launch, band_y, 1150 - x_launch, 44, fill=BOARD_C + "18",
                  stroke=BOARD_C, sw=2.2, rx=8))
    p.append(text(30, band_y + 26, "БОРТ: уже не змінити", size=12.5, color=BOARD_C,
                  anchor="start", bold=True))
    p.append(text((x_launch + 1150) / 2, band_y + 27,
                  "те, що припаяли 1977-го, — і так до сьогодні, без жодної зміни  →",
                  size=12.5, color=BOARD_C, bold=True))

    # три речі на борту
    chips = [
        (420, 230, ["внутрішній: згортковий", "K = 7, r = 1/2"]),
        (660, 230, ["зовнішній: Ґолей (24,12)", "100 % надлишку"]),
        (900, 250, ["кодер RS(255,223)", "вимкнений — чекає на Землю"]),
    ]
    for (cx0, cw, lines) in chips:
        p.append(fitbox(cx0, 398, cw, 50, lines, size=11.5,
                        fill=BG, stroke=BOARD_C, sw=1.8, color=BOARD_C))

    # 1986: єдина зміна, яку ще можна внести
    p.append(arrow(700, ax_y + 10, 700, band_y - 6, color=FIELD, sw=2.4))
    p.append(text(712, 300, "1986: єдине, що ще можна змінити, — команда «увімкни RS»",
                  size=11.5, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, 482, "Кодер летить і застигає назавжди; декодер лишається на Землі й може рости десятиліттями. "
                              "Каскад ділиться саме по цьому шву.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "voyager-timeline.svg"), W, H, *p,
           title="Асиметрія далекого космосу: борт застигає в мить запуску, Земля — ні")


# ── voyager-rates: 1/r² тягне вниз, інженерія тягне вгору ─────────────────────
def fig_voyager_rates():
    W, H = 1000, 540
    p = []
    oy, ytop = 424, 96
    lo, hi = 1000.0, 200000.0
    span = math.log10(hi) - math.log10(lo)

    def Y(v):
        return oy - (math.log10(v) - math.log10(lo)) * (oy - ytop) / span

    # осі
    p.append(line(120, ytop - 10, 120, oy, color=INK, sw=2))
    p.append(line(120, oy, 950, oy, color=INK, sw=2))
    for v, lb in [(1000, "1 кбіт/с"), (10000, "10 кбіт/с"), (100000, "100 кбіт/с")]:
        p.append(line(114, Y(v), 120, Y(v), color=INK, sw=1.4))
        p.append(text(108, Y(v) + 4, lb, size=11, color=MUTED, anchor="end"))
        p.append(line(120, Y(v), 950, Y(v), color=MUTED, sw=0.8, dash="3 6"))

    groups = [
        (215, "Юпітер", "5.2 а.о. · 1979", 115200, 115200, None),
        (400, "Сатурн", "10 а.о. · 1981", 29000, 44800, "×1.5"),
        (585, "Уран", "19 а.о. · 1986", 9000, 29900, "×3.3"),
        (770, "Нептун", "30 а.о. · 1989", 3200, 21600, "×6.8"),
    ]
    BWD = 64
    for (cx, name, dist, exp_v, got_v, fac) in groups:
        xa, xb = cx - BWD - 5, cx + 5
        p.append(rect(xa, Y(exp_v), BWD, oy - Y(exp_v), fill=MUTED + "22", stroke=MUTED, sw=1.8, rx=3))
        p.append(rect(xb, Y(got_v), BWD, oy - Y(got_v), fill=FIELD + "22", stroke=FIELD, sw=2.2, rx=3))
        p.append(text(xa + BWD / 2, Y(exp_v) - 8, "%d" % exp_v, size=11, color=MUTED, bold=True))
        p.append(text(xb + BWD / 2, Y(got_v) - 8, "%d" % got_v, size=11.5, color=FIELD, bold=True))
        p.append(text(cx, oy + 22, name, size=12.5, color=INK, bold=True))
        p.append(text(cx, oy + 40, dist, size=11, color=MUTED))
        if fac:
            p.append(text(cx, oy + 62, fac, size=13, color=POS, bold=True))

    # легенда — у вільному куті над стовпчиками Урана й Нептуна, між сітками
    p.append(rect(700, 150, 22, 14, fill=MUTED + "22", stroke=MUTED, sw=1.8, rx=2))
    p.append(text(730, 162, "чого чекати від самої фізики (1/r²)", size=11.5, color=MUTED, anchor="start"))
    p.append(rect(700, 178, 22, 14, fill=FIELD + "22", stroke=FIELD, sw=2.2, rx=2))
    p.append(text(730, 190, "що справді витягли", size=11.5, color=FIELD, anchor="start", bold=True))

    p.append(text(120, 62, "швидкість донизу, яку мав «Вояджер-2» на кожній планеті",
                  size=12.5, color=INK, anchor="start", bold=True))
    p.append(text(535, oy + 88, "Нептун утричі далі за Сатурн — сигнал ослаб у 9 разів. Швидкість упала лише вдвічі.",
                  size=12, color=INK, bold=True))
    p.append(text(535, oy + 108, "Різницю зробили стиснення, Рід–Соломон і перебудовані антени. Дані: JPL, Table 6-1.",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "voyager-rates.svg"), W, H, *p,
           title="Фізика тягне швидкість донизу як 1/r², інженерія тягне назад угору")


# ── voyager-fragile: стиснення робить кожен біт незамінним ────────────────────
def fig_voyager_fragile():
    W, H = 1000, 560
    p = []
    N = 12
    CW, CG = 46, 8
    x0 = 250
    base = [120, 122, 125, 128, 130, 131, 133, 134, 136, 138, 139, 140]
    ERR = 5                                   # де перевернувся біт (вага 8)

    def shade(v):
        g = max(0, min(255, int((v - 110) * 6 + 40)))
        return "#%02x%02x%02x" % (g, g, g)

    def strip(y, vals, hot, tag, tag_col, show):
        out = mtext(20, y + 12, tag, size=11.5, color=tag_col, anchor="start", bold=True, lh=1.3)
        for i, v in enumerate(vals):
            bx = x0 + i * (CW + CG)
            st = POS if i in hot else MUTED
            out += rect(bx, y, CW, 40, fill=shade(v), stroke=st, sw=(2.4 if i in hot else 1.2), rx=3)
            out += text(bx + CW / 2, y + 58, show(v), size=11,
                        color=(POS if i in hot else MUTED), bold=(i in hot))
        return out

    # ── A: знімок як є ────────────────────────────────────────────────────────
    yA = 96
    valsA = list(base); valsA[ERR] += 8
    p.append(strip(yA, valsA, {ERR}, ["знімок як є:", "кожен піксель —", "своє число"], INK, lambda v: str(v)))
    p.append(text(x0, yA + 86, "перевернувся один біт → зіпсована одна крапка. На знімку 800×800 її не видно.",
                  size=12, color=INK, anchor="start", bold=True))
    p.append(text(x0, yA + 106, "Саме тому Юпітерові й Сатурнові вистачало BER 5·10⁻³.",
                  size=11.5, color=MUTED, anchor="start"))

    # ── B: що насправді летить після стиснення ───────────────────────────────
    yB = 268
    diffs = [base[0]] + [base[i] - base[i - 1] for i in range(1, N)]
    dshow = ["%d" % diffs[0]] + ["%+d" % d for d in diffs[1:]]
    valsB = [base[0]] + [128 + d * 6 for d in diffs[1:]]
    out = mtext(20, yB + 12, ["стиснений знімок:", "кожен піксель —", "різниця з попереднім"],
                size=11.5, color=NEG, anchor="start", bold=True, lh=1.3)
    for i in range(N):
        bx = x0 + i * (CW + CG)
        st = POS if i == ERR else NEG
        out += rect(bx, yB, CW, 40, fill=(BG if i != ERR else BAD_F), stroke=st,
                    sw=(2.4 if i == ERR else 1.2), rx=3)
        out += text(bx + CW / 2, yB + 26, dshow[i], size=12,
                    color=(POS if i == ERR else NEG), bold=True)
    p.append(out)
    p.append(text(x0 + ERR * (CW + CG) + CW / 2, yB - 12, "тут", size=11, color=POS, bold=True))
    p.append(text(x0, yB + 68, "той самий один біт → «+1» стало «+9». Разів у 2.5 менше бітів у канал — заради цього все й робилося.",
                  size=11.5, color=NEG, anchor="start"))

    # ── C: що збереться на Землі ──────────────────────────────────────────────
    yC = 388
    valsC = list(base)
    for i in range(ERR, N):
        valsC[i] += 8
    p.append(strip(yC, valsC, set(range(ERR, N)), ["що збереться", "на Землі"], POS, lambda v: str(v)))
    p.append(line(x0 + ERR * (CW + CG) - 4, yC - 8, x0 + N * (CW + CG) - CG + 4, yC - 8,
                  color=POS, sw=2.2))
    p.append(text(x0 + ((ERR + N) / 2) * (CW + CG), yC - 16,
                  "попливло все до кінця рядка", size=11.5, color=POS, bold=True))
    p.append(text(x0, yC + 86, "кожен піксель складається з попереднього — тож похибка їде далі й далі, до самого краю.",
                  size=12, color=POS, anchor="start", bold=True))

    p.append(text(W / 2, 534, "Стиснення прибирає з даних природний надлишок — і кожен уцілілий біт стає незамінним. "
                              "Звідси й вимога BER 10⁻⁶, а з нею — Рід–Соломон.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "voyager-fragile.svg"), W, H, *p,
           title="Чому стиснення змусило взяти зовнішній код")


# ══ фігури вставки «Каскад у роботі: конвеєр від байта до байта» ══════════════

IL_N, IL_DEPTH, IL_T = 32, 8, 4          # RS(32,24): слово 32 байти, t=4; глибина 8
IL_AT, IL_LEN, IL_SBITS = 1400, 300, 14  # той самий пакет, що й у прогоні вставки


def _burst_slots(at=IL_AT, ln=IL_LEN, s=IL_SBITS):
    """Байтові комірки, яких торкнувся пакет (s бітів у каналі на один байт)."""
    return list(range(at // s, (at + ln - 1) // s + 1))


# ── interleave-grid: та сама смуга завади у двох розкладках ───────────────────
def fig_interleave_grid():
    W, H = 648, 500
    cw, chh = 13.6, 16.0
    gx = 84.0
    slots = _burst_slots()
    # рядок за рядком: комірка i → слово i//32, позиція i%32
    hitA = {(i // IL_N, i % IL_N) for i in slots}
    # стовпець за стовпцем: комірка i → слово i%8, позиція i//8
    hitB = {(i % IL_DEPTH, i // IL_DEPTH) for i in slots}
    p = []

    def panel(gy, hit, header, order_note):
        out = [text(gx, gy - 12, header, size=12.5, color=INK, anchor="start", bold=True)]
        for r in range(IL_DEPTH):
            cy = gy + r * chh
            out.append(text(gx - 8, cy + 11.5, "слово %d" % r, size=10.5,
                            color=MUTED, anchor="end"))
            n = sum(1 for c in range(IL_N) if (r, c) in hit)
            for c in range(IL_N):
                bad = (r, c) in hit
                out.append(rect(gx + c * cw, cy + 1.5, cw - 1.6, chh - 3.0,
                                fill=BAD_F if bad else DATA_F,
                                stroke=BAD_S if bad else DATA_S, sw=0.7, rx=2))
            ok = n <= IL_T
            out.append(text(gx + IL_N * cw + 10, cy + 11.5,
                            "%d %s" % (n, "✓" if ok else "✗"), size=10.5,
                            color=GOOD_C if ok else POS, anchor="start", bold=True))
        out.append(text(gx, gy + IL_DEPTH * chh + 17, order_note, size=11,
                        color=MUTED, anchor="start"))
        return out

    p += panel(72, hitA, "У канал — слово за словом (перемішування немає)",
               "пакет лягає ВЗДОВЖ одного рядка — усі 22 байти в одне слово")
    p.append(text(gx, 240, "слово 3 дістало 22 помилки при запасі t=4 → декодер здався, кадр утрачено",
                  size=12, color=POS, anchor="start", bold=True))

    p += panel(288, hitB, "У канал — стовпець за стовпцем (перемішування, глибина 8)",
               "пакет лягає ВПОПЕРЕК рядків — по 2–3 байти на слово")
    p.append(text(gx, 456, "жодне слово не дістало більш як 3 при запасі t=4 → RS виправив усе, дані чисті",
                  size=12, color=GOOD_C, anchor="start", bold=True))

    p.append(text(W / 2, 484, "Той самий пакет, ті самі коди. Різниця лише в ПОРЯДКУ, "
                              "у якому байти пішли в канал.", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "interleave-grid.svg"), W, H, *p,
           title="Куди лягає пакет: 8 слів RS(32,24) × 32 байти, пакет 300 бітів")


# ── burst-threshold: заміряний обрив — і чому він рівно у 8 разів далі ────────
def fig_burst_threshold():
    W, H = 720, 424
    x0, x1, y0, y1 = 84.0, 660.0, 76.0, 330.0
    BMAX = 660.0
    sx = lambda b: x0 + b * (x1 - x0) / BMAX
    sy = lambda v: y1 - v * (y1 - y0)
    # заміряно кодом вставки: 250 прогонів на точку, місце пакета випадкове
    WITH = [(14, 1.0), (42, 1.0), (196, 1.0), (392, 1.0), (434, 1.0),
            (448, 0.492), (462, 0.02), (490, 0.0), (644, 0.0)]
    WITHOUT = [(14, 1.0), (42, 1.0), (56, 0.556), (70, 0.104), (84, 0.064),
               (112, 0.02), (140, 0.0), (644, 0.0)]
    p = []

    # легенда — понад полем, щоб нічого не перетнути
    p.append(line(x0, 52, x0 + 26, 52, color=POS, sw=3.0))
    p.append(text(x0 + 32, 56, "без перемішування", size=11.5, color=INK, anchor="start"))
    p.append(line(340, 52, 366, 52, color=NEG, sw=3.0))
    p.append(text(372, 56, "з перемішуванням, глибина 8", size=11.5, color=INK, anchor="start"))

    # сітка й осі
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        p.append(line(x0, sy(v), x1, sy(v), color="#e3e6ea", sw=1.0))
        p.append(text(x0 - 8, sy(v) + 4, "%d%%" % (v * 100), size=10.5,
                      color=MUTED, anchor="end"))
    for b in range(0, 601, 100):
        p.append(text(sx(b), 350, str(b), size=10.5, color=MUTED))
    p.append(line(x0, y1, x1, y1, color=LINE, sw=1.5))
    p.append(line(x0, y0, x0, y1, color=LINE, sw=1.5))
    p.append(text(x0, 66, "кадрів відновлено", size=11, color=MUTED, anchor="start"))
    p.append(text((x0 + x1) / 2, 372, "довжина пакета помилок, біт", size=11.5, color=INK))

    # теоретичні межі s·(t·D−1)+1
    for b, lab in ((43, "43"), (435, "435")):
        p.append(line(sx(b), y0, sx(b), y1, color=MUTED, sw=1.3, dash="5 4"))
        p.append(text(sx(b), 364, lab, size=10.5, color=MUTED, bold=True))

    # східчасті криві
    def steps(pts):
        out = []
        for i in range(len(pts) - 1):
            out.append((sx(pts[i][0]), sy(pts[i][1])))
            out.append((sx(pts[i + 1][0]), sy(pts[i][1])))
            out.append((sx(pts[i + 1][0]), sy(pts[i + 1][1])))
        return out

    p.append(polyline(steps(WITHOUT), POS, sw=3.0))
    p.append(polyline(steps(WITH), NEG, sw=3.0))

    p.append(text(W / 2, 398, "Глибина 8 подовжила посильний пакет рівно у 8 разів: 43 → 435 бітів. "
                              "Штрихові — межа s·(t·D−1)+1.", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "burst-threshold.svg"), W, H, *p,
           title="Найдовший пакет, який каскад ще виправляє")


if __name__ == "__main__":
    fig_pipeline()
    fig_cleanup()
    fig_complexity()
    fig_params()
    fig_product()
    fig_radius()
    fig_superchannel()
    fig_exchange()
    fig_voyager_timeline()
    fig_voyager_rates()
    fig_voyager_fragile()
    fig_interleave_grid()
    fig_burst_threshold()
    print("ok: pipeline, cleanup, complexity, params, product-distance, gmd-radius, superchannel, exchange, "
          "voyager-timeline, voyager-rates, voyager-fragile, interleave-grid, burst-threshold")
