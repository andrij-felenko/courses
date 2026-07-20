# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DATA_F, DATA_S = "#eafaee", FIELD     # чисті дані — зелені
REP_F,  REP_S  = "#fff4e0", "#c9922e" # ремонтні — бурштин
BAD_F,  BAD_S  = "#fdeceb", POS       # втрачені — гарячі
CHAN_C         = "#c9922e"


def pkt(x, y, w, h, label, fill, stroke, size=12):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=3) +
            text(x + w / 2, y + h / 2 + size * 0.36, label, size=size, color=stroke, bold=True))


def xmark(cx, cy, r=9, color=POS):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=2.6) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=2.6))


# ── fec-vs-arq: ARQ платить зворотним рейсом, FEC — ні ────────────────────────
def fig_fec_vs_arq():
    W, H = 940, 560
    p = []

    def panel(sy, ry, title, tcol):
        out = [text(30, sy - 30, title, size=13.5, color=tcol, anchor="start", bold=True)]
        out.append(text(30, sy + 6, "Передавач", size=11.5, color=MUTED, anchor="start", bold=True))
        out.append(line(150, sy, 900, sy, color=MUTED, sw=1.2))
        out.append(text(30, ry + 6, "Приймач", size=11.5, color=MUTED, anchor="start", bold=True))
        out.append(line(150, ry, 900, ry, color=MUTED, sw=1.2))
        return out

    # ── Панель А: ARQ ─────────────────────────────────────────────────────────
    syA, ryA = 120, 210
    p += panel(syA, ryA, "ARQ: просимо переслати — потрібен зворотний рейс (RTT)", POS)
    # пакети 1,2,4 доходять; 3 губиться в дорозі
    for xs, xr, lab in [(175, 220, "1"), (240, 285, "2"), (360, 405, "4")]:
        p.append(text(xs, syA - 10, lab, size=11, color=INK, bold=True))
        p.append(arrow(xs, syA + 6, xr, ryA - 6, color=INK, sw=1.6))
    # пакет 3 — губиться
    p.append(text(305, syA - 10, "3", size=11, color=INK, bold=True))
    p.append(line(305, syA + 6, 335, ryA - 55, color=BAD_S, sw=1.6, dash="4 4"))
    p.append(xmark(340, ryA - 48))
    # приймач помітив діру
    p.append(text(430, ryA + 24, "бракує 3", size=11, color=POS, anchor="middle", bold=True))
    # зворотний рейс (NAK) — ключова стрілка, назад і вгору
    p.append(arrow(455, ryA - 6, 545, syA + 6, color=POS, sw=2.6))
    p.append(text(455, ryA + 48, "зворотний рейс (RTT) — просимо переслати 3", size=11.5, color=POS, anchor="start", bold=True))
    # повторна відправка 3
    p.append(text(600, syA - 10, "3", size=11, color=INK, bold=True))
    p.append(arrow(600, syA + 6, 665, ryA - 6, color=INK, sw=1.6))
    # дедлайн кадру
    p.append(line(505, syA - 22, 505, ryA + 32, color=NEG, sw=1.8, dash="7 5"))
    p.append(text(505, syA - 30, "дедлайн кадру", size=11, color=NEG, bold=True))
    p.append(text(775, ryA + 28, "3 дійшло — але запізно", size=12, color=POS, anchor="middle", bold=True))

    # ── Панель Б: FEC ─────────────────────────────────────────────────────────
    syB, ryB = 400, 490
    p += panel(syB, ryB, "FEC: лагодимо на місці — жодного зворотного рейсу", FIELD)
    for xs, xr, lab, col in [(175, 220, "1", INK), (240, 285, "2", INK),
                             (360, 405, "4", INK), (420, 465, "R", REP_S)]:
        p.append(text(xs, syB - 10, lab, size=11, color=col, bold=True))
        p.append(arrow(xs, syB + 6, xr, ryB - 6, color=(REP_S if lab == "R" else INK), sw=1.6))
    # пакет 3 — губиться
    p.append(text(305, syB - 10, "3", size=11, color=INK, bold=True))
    p.append(line(305, syB + 6, 335, ryB - 55, color=BAD_S, sw=1.6, dash="4 4"))
    p.append(xmark(340, ryB - 48))
    # локальне відновлення — без стрілки назад
    p.append(circle(500, ryB, 15, fill=DATA_F, stroke=FIELD, sw=2.2))
    p.append(text(500, ryB + 5, "⊕", size=16, color=FIELD, bold=True))
    p.append(text(500, ryB + 34, "3 відновлено локально", size=11.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(500, ryB + 50, "(XOR наявних + R)", size=10.5, color=MUTED, anchor="middle"))
    # дедлайн
    p.append(line(595, syB - 22, 595, ryB + 40, color=NEG, sw=1.8, dash="7 5"))
    p.append(text(595, syB - 30, "дедлайн кадру", size=11, color=NEG, bold=True))
    p.append(text(760, syB + 30, "жодної стрілки назад →", size=12, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "fec-vs-arq.svg"), W, H, *p,
           title="Чому живе відео бере FEC, а не повтор: зворотний рейс запізнюється")


# ── block-erasure: приймаєш будь-які k із n — і все відновлено ─────────────────
def fig_block_erasure():
    W, H = 900, 470
    p = []
    k, n = 6, 8
    cw, gap = 74, 12
    x0 = 120
    erased = {2, 5}   # позиції, що зникли в каналі (0..n-1)

    def cell(idx, y, lab, fill, stroke):
        bx = x0 + idx * (cw + gap)
        return pkt(bx, y, cw, 44, lab, fill, stroke, size=13)

    # рядок 1 — передано n пакетів (k даних + n-k ремонтних)
    y1 = 90
    p.append(text(x0, y1 - 16, "передано n = 8 пакетів:  6 даних  +  2 ремонтні", size=12.5, color=INK, anchor="start", bold=True))
    for i in range(n):
        if i < k:
            p.append(cell(i, y1, "D%d" % (i + 1), DATA_F, DATA_S))
        else:
            p.append(cell(i, y1, "R%d" % (i - k + 1), REP_F, REP_S))

    # канал — двоє зникли
    y2 = 200
    p.append(rect(x0 - 20, y2 - 8, n * (cw + gap) - gap + 40, 52, fill=CHAN_C + "10", stroke=CHAN_C, sw=1.6, rx=8))
    p.append(text(x0 - 8, y2 + 22, "канал", size=11.5, color=CHAN_C, anchor="start", bold=True))
    for i in range(n):
        bx = x0 + i * (cw + gap) + cw / 2
        if i in erased:
            p.append(xmark(bx, y2 + 18, r=11))
            p.append(text(bx, y2 + 46, "зник", size=10, color=POS))
        else:
            p.append(text(bx, y2 + 24, "↓", size=17, color=FIELD, bold=True))

    # рядок 2 — отримано будь-які 6 із 8
    y3 = 300
    p.append(text(x0, y3 - 16, "отримано: будь-які 6 із 8 (тут — 4 дані + 2 ремонтні)", size=12.5, color=INK, anchor="start", bold=True))
    got = 0
    for i in range(n):
        if i in erased:
            bx = x0 + i * (cw + gap)
            p.append(rect(bx, y3, cw, 44, fill=BG, stroke=MUTED, sw=1.2, rx=3, ))
            p.append(text(bx + cw / 2, y3 + 27, "—", size=15, color=MUTED))
        else:
            if i < k:
                p.append(cell(i, y3, "D%d" % (i + 1), DATA_F, DATA_S))
            else:
                p.append(cell(i, y3, "R%d" % (i - k + 1), REP_F, REP_S))

    # декодер → відновлено всі 6 даних
    y4 = 400
    p.append(arrow(W / 2, y3 + 52, W / 2, y4 - 12, color=FIELD, sw=2.4))
    p.append(text(W / 2 + 14, y4 - 22, "erasure-декодер", size=11.5, color=FIELD, anchor="start", bold=True))
    p.append(text(x0, y4 - 16, "відновлено всі 6 даних — включно з тими, що зникли:", size=12.5, color=FIELD, anchor="start", bold=True))
    for i in range(k):
        bx = x0 + i * (cw + gap)
        st = POS if i in erased else FIELD
        p.append(pkt(bx, y4, cw, 44, "D%d" % (i + 1), DATA_F, st, size=13))

    render(os.path.join(OUT, "block-erasure.svg"), W, H, *p,
           title="Блоковий erasure-код (n, k): будь-які k із n пакетів відновлюють усе")


# ── interleave-burst: той самий пакет завади — з перемішуванням і без ──────────
def fig_interleave_burst():
    W, H = 960, 470
    p = []
    NSLOT = 12
    cw, gap = 58, 8
    x0 = 60
    B_COL = [FIELD, "#c9922e", NEG]           # B1 зелений, B2 бурштин, B3 синій
    B_FILL = ["#eafaee", "#fff4e0", "#eaf0fd"]
    burst = {4, 5, 6}                          # ті самі три слоти в обох смугах

    def strip(y, block_of, title, tcol):
        out = [text(x0, y - 16, title, size=12.5, color=tcol, anchor="start", bold=True)]
        for s in range(NSLOT):
            bx = x0 + s * (cw + gap)
            b = block_of(s)
            hit = s in burst
            f = BAD_F if hit else B_FILL[b]
            st = BAD_S if hit else B_COL[b]
            out.append(rect(bx, y, cw, 42, fill=f, stroke=st, sw=(2.2 if hit else 1.5), rx=3))
            out.append(text(bx + cw / 2, y + 20, "B%d" % (b + 1), size=12, color=(POS if hit else B_COL[b]), bold=True))
            if hit:
                out.append(text(bx + cw / 2, y + 36, "✗", size=11, color=POS, bold=True))
        return out

    # смуга завади — над обома рядками
    bx0 = x0 + 4 * (cw + gap) - 4
    bx1 = x0 + 6 * (cw + gap) + cw + 4

    # рядок А: без перемішування — блоки лежать підряд
    yA = 110
    p += strip(yA, lambda s: s // 4, "БЕЗ перемішування — пакети блоку йдуть підряд", INK)
    p.append(rect(bx0, yA - 6, bx1 - bx0, 54, fill="none", stroke=POS, sw=1.8, rx=6))
    p.append(text((bx0 + bx1) / 2, yA - 32, "пакет завади", size=11, color=POS, bold=True))
    p.append(text(x0, yA + 78, "B2 дістав −3 при запасі 2  →  блок B2 не відновити", size=12.5, color=POS, anchor="start", bold=True))

    # рядок Б: з перемішуванням — по колу B1,B2,B3
    yB = 300
    p += strip(yB, lambda s: s % 3, "З перемішуванням — сусіди з різних блоків", INK)
    p.append(rect(bx0, yB - 6, bx1 - bx0, 54, fill="none", stroke=POS, sw=1.8, rx=6))
    p.append(text((bx0 + bx1) / 2, yB - 32, "та сама завада", size=11, color=POS, bold=True))
    p.append(text(x0, yB + 78, "кожен блок дістав лише −1 (≤ 2)  →  усі три блоки відновлено", size=12.5, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "interleave-burst.svg"), W, H, *p,
           title="Перемішування розтягує пакет завади між блоками")


# ── source-channel: стиснути (прибрати надлишок), тоді захистити (додати) ──────
def fig_source_channel():
    W, H = 1180, 340
    p = []

    def stage(x, w, y, h, lab, sub, col):
        out = rect(x, y, w, h, fill=(BG if col is INK else col + "12"), stroke=col, sw=2.2, rx=8)
        out += text(x + w / 2, y + 24, lab, size=12.5, color=col, bold=True)
        if sub:
            out += mtext(x + w / 2, y + 42, sub, size=10, color=MUTED, lh=1.2)
        return out

    y, h = 96, 66
    stages = [
        (150, "Камера", None, INK),
        (168, "Стиснення", ["source coding:", "прибирає надлишок"], NEG),
        (168, "FEC-кодер", ["channel coding:", "додає надлишок"], POS),
        (150, "Канал", ["губить пакети ✗"], CHAN_C),
        (168, "FEC-декодер", ["відновлює", "втрачене"], FIELD),
        (150, "Відео → екран", None, INK),
    ]
    x = 30
    for i, (w, lab, sub, col) in enumerate(stages):
        p.append(stage(x, w, y, h, lab, sub, col))
        x2 = x + w
        if i < len(stages) - 1:
            p.append(arrow(x2 + 3, y + h / 2, x2 + 27, y + h / 2, color=INK))
        x = x2 + 30

    # смужки-дані під двома серединними стадіями: вузько після стиснення, ширше після FEC
    def strip(cx, ncell, extra, note):
        bw, bg = 12, 3
        total = ncell * (bw + bg) - bg
        sx = cx - total / 2
        out = ""
        for j in range(ncell):
            isrep = j >= ncell - extra
            out += rect(sx + j * (bw + bg), 208, bw, 20,
                        fill=(REP_F if isrep else DATA_F),
                        stroke=(REP_S if isrep else DATA_S), sw=1.0, rx=2)
        out += text(cx, 250, note, size=10.5, color=MUTED)
        return out

    p.append(text(392, 196, "компактний потік", size=10.5, color=NEG, bold=True))
    p.append(strip(392, 8, 0, "лише корисні біти"))
    p.append(text(660, 196, "потік + ремонт", size=10.5, color=POS, bold=True))
    p.append(strip(660, 11, 3, "дані + ремонтні пакети"))
    p.append(arrow(470, 218, 582, 218, color=MUTED, sw=1.4))

    p.append(text(W / 2, 300, "Джерельний код віджимає надлишок, щоб було КОМПАКТНО; канальний код додає інший, "
                              "структурований надлишок, щоб було НАДІЙНО.", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "source-channel.svg"), W, H, *p)


# ── systematic-matrix: G = [I ; Cauchy]; декод = обернути k×k підматрицю ───────
def fig_systematic_matrix():
    W, H = 980, 560
    p = []
    k, m = 4, 3
    n = k + m
    cs = 44
    gx, gy = 80, 150

    def cellrect(r, c, txt, fill, stroke, tcol=None, size=13):
        x = gx + c * cs
        y = gy + r * cs
        return (rect(x, y, cs, cs, fill=fill, stroke=stroke, sw=1.2, rx=0) +
                text(x + cs / 2, y + cs / 2 + 5, txt, size=size, color=(tcol or stroke), bold=True))

    p.append(text(gx, 44, "Систематична матриця кодування  G = [ I ; Cauchy ]", size=14, color=INK, anchor="start", bold=True))
    p.append(text(gx, 68, "y = G · d :  верхні k рядків — одинична (дані проходять як є), нижні m — ремонтні", size=11.5, color=MUTED, anchor="start"))
    p.append(text(gx, gy - 16, "k = 4 стовпці", size=11, color=MUTED, anchor="start"))

    # одинична (дані)
    for r in range(k):
        for c in range(k):
            one = (r == c)
            p.append(cellrect(r, c, "1" if one else "0",
                              DATA_F if one else BG, DATA_S if one else "#cfd6dd",
                              DATA_S if one else MUTED))
    # Cauchy (ремонт)
    clab = [["c₁₁", "c₁₂", "c₁₃", "c₁₄"], ["c₂₁", "c₂₂", "c₂₃", "c₂₄"], ["c₃₁", "c₃₂", "c₃₃", "c₃₄"]]
    for i in range(m):
        for c in range(k):
            p.append(cellrect(k + i, c, clab[i][c], REP_F, REP_S, size=12))

    gright = gx + k * cs
    p.append(text(gright + 12, gy + 2 * cs - 6, "I", size=15, color=DATA_S, anchor="start", bold=True))
    p.append(text(gright + 12, gy + 2 * cs + 12, "дані як є", size=10, color=DATA_S, anchor="start"))
    p.append(text(gright + 12, gy + (k + 1.5) * cs - 4, "Cauchy", size=12, color=REP_S, anchor="start", bold=True))
    p.append(text(gright + 12, gy + (k + 1.5) * cs + 13, "cᵢⱼ=1/(xᵢ⊕yⱼ)", size=9.5, color=REP_S, anchor="start"))

    # · d
    dx = gright + 150
    p.append(text(dx - 26, gy + k * cs / 2 + 5, "·", size=22, color=INK, bold=True))
    p.append(text(dx + cs / 2, gy - 16, "d", size=13, color=INK, bold=True))
    for r in range(k):
        y = gy + r * cs
        p.append(rect(dx, y, cs, cs, fill=DATA_F, stroke=DATA_S, sw=1.2))
        p.append(text(dx + cs / 2, y + cs / 2 + 5, "d%d" % (r + 1), size=12.5, color=DATA_S, bold=True))

    # = y (кодове слово, n клітин)
    yx = dx + cs + 120
    p.append(text(yx - 30, gy + k * cs / 2 + 5, "=", size=20, color=INK, bold=True))
    p.append(text(yx + cs / 2, gy - 16, "y  (n пакетів)", size=13, color=INK, anchor="start", bold=True))
    for r in range(n):
        y = gy + r * cs
        if r < k:
            p.append(rect(yx, y, cs, cs, fill=DATA_F, stroke=DATA_S, sw=1.2))
            p.append(text(yx + cs / 2, y + cs / 2 + 5, "d%d" % (r + 1), size=12.5, color=DATA_S, bold=True))
        else:
            p.append(rect(yx, y, cs, cs, fill=REP_F, stroke=REP_S, sw=1.2))
            p.append(text(yx + cs / 2, y + cs / 2 + 5, "R%d" % (r - k + 1), size=12.5, color=REP_S, bold=True))
    p.append(text(yx + cs + 14, gy + k * cs / 2 - 6, "y₁..y₄ = d₁..d₄", size=10.5, color=DATA_S, anchor="start"))
    p.append(text(yx + cs + 14, gy + k * cs / 2 + 12, "(тому «систематична»)", size=10, color=MUTED, anchor="start"))

    # декод-примітка
    by = gy + n * cs + 26
    p.append(line(gx, by - 12, W - 40, by - 12, color="#e2e6ea", sw=1.2))
    p.append(text(gx, by + 6, "Декод: дійшли будь-які k = 4 пакети → беремо їхні 4 рядки з G → матриця A (4×4) → A⁻¹ →  d = A⁻¹ · y_отримане",
                  size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(gx, by + 26, "Будь-яка k-ка рядків [ I ; Cauchy ] невироджена — тому й вистачає будь-яких k із n.",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "systematic-matrix.svg"), W, H, *p,
           title="Систематичне кодування й декодування (n,k) над GF(256)")


# ── packet-block: вирівнювання до L і позиції стирань із номерів ───────────────
def fig_packet_block():
    W, H = 960, 470
    p = []
    x0 = 70
    cw, gap = 120, 14
    hh = 20            # висота заголовка пакета
    L = 132            # спільна довжина «корисної» частини (для масштабу)
    scale = 0.62
    ytop = 120

    # реальні довжини даних (різні) — доповнюються нулями до L
    real = [96, 132, 70, 118]     # d1..d4
    lab_d = ["d1", "d2", "d3", "d4"]
    lost = 2                       # d3 зник (idx=2)

    p.append(text(x0, 48, "Блок пакетів: вирівнювання до спільної L і стирання за номером", size=14, color=INK, anchor="start", bold=True))
    p.append(text(x0, 72, "Кожен пакет несе заголовок (blk, idx). Дані різної довжини доповнюються нулями до L — інакше XOR/множення читали б за буфером.",
                  size=11, color=MUTED, anchor="start"))

    Lpx = L * scale
    for j in range(4):
        bx = x0 + j * (cw + gap)
        gone = (j == lost)
        head_f = BAD_F if gone else DATA_F
        head_s = BAD_S if gone else DATA_S
        # заголовок (blk, idx)
        p.append(rect(bx, ytop, cw, hh, fill=head_f, stroke=head_s, sw=1.3))
        p.append(text(bx + cw / 2, ytop + 14, "blk 7 · idx %d" % j, size=10.5, color=head_s, bold=True))
        # корисні дані
        realpx = real[j] * scale
        p.append(rect(bx, ytop + hh, realpx, 40, fill=(BG if gone else DATA_F), stroke=head_s, sw=1.3))
        if not gone:
            p.append(text(bx + realpx / 2, ytop + hh + 25, lab_d[j], size=12.5, color=DATA_S, bold=True))
        # доповнення нулями до L
        if realpx < Lpx:
            p.append(rect(bx + realpx, ytop + hh, Lpx - realpx, 40, fill="#f0f2f4", stroke="#cfd6dd", sw=1.1))
            p.append(text(bx + realpx + (Lpx - realpx) / 2, ytop + hh + 25, "0…0", size=10, color=MUTED))
        if gone:
            p.append(xmark(bx + realpx / 2, ytop + hh + 20, r=12))

    # ремонтні пакети — завжди довжина L
    for t in range(2):
        bx = x0 + (4 + t) * (cw + gap)
        p.append(rect(bx, ytop, cw, hh, fill=REP_F, stroke=REP_S, sw=1.3))
        p.append(text(bx + cw / 2, ytop + 14, "blk 7 · idx %d" % (4 + t), size=10.5, color=REP_S, bold=True))
        p.append(rect(bx, ytop + hh, Lpx, 40, fill=REP_F, stroke=REP_S, sw=1.3))
        p.append(text(bx + Lpx / 2, ytop + hh + 25, "R%d" % (t + 1), size=12.5, color=REP_S, bold=True))

    # мірило L
    my = ytop + hh + 58
    p.append(line(x0, my, x0 + Lpx, my, color=MUTED, sw=1.2))
    p.append(line(x0, my - 4, x0, my + 4, color=MUTED, sw=1.2))
    p.append(line(x0 + Lpx, my - 4, x0 + Lpx, my + 4, color=MUTED, sw=1.2))
    p.append(text(x0 + Lpx / 2, my + 16, "спільна довжина L (усі пакети блоку)", size=10.5, color=MUTED))

    # висновок про стирання
    cy = 310
    p.append(rect(x0, cy, W - 2 * x0, 96, fill=FIELD + "0e", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x0 + 18, cy + 26, "Позиція стирання — з номера, не з вмісту", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(mtext(x0 + 18, cy + 48,
                   ["idx у заголовку каже декодеру ТОЧНО, котрий рядок G бракує (тут idx = 2). Це й робить код",
                    "erasure-кодом: позиція відома → декодеру досить будь-яких k пакетів, а не 2× на кожну помилку.",
                    "Приймач бачить у нумерації діру idx=2 — і будує підматрицю A з рядків тих, що дійшли."],
                   size=10.8, color=INK, lh=1.5, anchor="start"))

    render(os.path.join(OUT, "packet-block.svg"), W, H, *p,
           title="Вирівнювання пакетів і стирання за номером послідовності")


# ── fountain-timeline: історія повороту до безрейтових кодів ───────────────────
def fig_fountain_timeline():
    W, H = 920, 980
    p = []
    SX = 150                       # спина осі часу
    rows = [
        ("1997", FIELD, "1997 · Торнадо-коди",
         ["Лубі, Міценмахер, Шокроллагі, Спілман, Стеман: розріджений граф, лише XOR,",
          "майже впритул до ємності каналу зі стиранням — але швидкість ще фіксована."]),
        ("1998", FIELD, "1998 · «Цифровий фонтан» і компанія Digital Fountain",
         ["Байерс, Лубі, Міценмахер, Реге (SIGCOMM): роздача без зворотного каналу.",
          "Лубі залишає ICSI, засновює Digital Fountain, винаходить LT-коди."]),
        ("2002", FIELD, "2002 · LT-коди опубліковано (Лубі, FOCS)",
         ["Перший по-справжньому безрейтовий код: символ = XOR випадкової підмножини",
          "даних; декодування «обчисткою» (peeling) уздовж двочасткового графа."]),
        ("2006", FIELD, "2006 · Raptor-коди опубліковано (Шокроллагі)",
         ["Зовнішній прекод + послаблений внутрішній LT → лінійний час кодування",
          "й декодування та крихітний надлишок прийому."]),
        ("2007", "#c9922e", "2007 · RFC 5053 — Raptor у стандартах мовлення",
         ["3GPP MBMS і DVB-H: мобільне ТБ й роздача на безліч приймачів — саме той",
          "сценарій «один-до-багатьох», заради якого фонтан і шукали."]),
        ("2011", "#c9922e", "2011 · RFC 6330 — RaptorQ",
         ["Майже ідеальний прийом (часто досить k або k+1 символів), вільний",
          "від роялті для сумісних реалізацій."]),
        ("2019", "#c9922e", "2019 · RFC 8627 — FlexFEC у WebRTC",
         ["Для розмови в реальному часі — не фонтан, а проста систематична парність",
          "(і розсіяні, і пакетні втрати); ремонт окремим RTP-потоком поряд."]),
    ]
    bx, bw, bh = 195, 680, 100
    top0, pitch = 64, 128
    centers = [top0 + i * pitch + bh / 2 for i in range(len(rows))]
    p.append(line(SX, centers[0], SX, centers[-1], color=MUTED, sw=2.2))
    for i, (yr, col, head, det) in enumerate(rows):
        top = top0 + i * pitch
        cy = top + bh / 2
        p.append(rect(bx, top, bw, bh, fill=BG, stroke=col, sw=1.8, rx=8))
        p.append(text(126, cy + 5, yr, size=14, color=col, anchor="end", bold=True))
        p.append(circle(SX, cy, 9, fill=col, stroke=BG, sw=2.5))
        p.append(line(SX + 9, cy, bx, cy, color=col, sw=1.6))
        p.append(text(bx + 17, top + 30, head, size=13.5, color=INK, anchor="start", bold=True))
        p.append(mtext(bx + 17, top + 55, det, size=11.5, color=MUTED, anchor="start", lh=1.35))
    render(os.path.join(OUT, "fountain-timeline.svg"), W, H, *p,
           title="Двадцять років повороту: від блокових кодів до фонтана")


# ── fountain-idea: кран ллє нескінченно, кожен ловить свою жменю ────────────────
def fig_fountain_idea():
    W, H = 980, 560
    p = []
    WATER_F, WATER_S = "#eaf0fd", NEG
    p.append(text(W / 2, 56, "Кран-фонтан ллє нескінченний потік РІЗНИХ ремонтних символів "
                             "(кожен — XOR випадкової підмножини даних):",
                  size=12, color=NEG, anchor="middle", bold=True))
    p.append(fitbox(40, 74, 150, 66, "Кодер-\nфонтан", size=13, bold=True,
                    fill=WATER_F, stroke=WATER_S, color=NEG))
    p.append(mtext(115, 158, ["джерело даних", "(k символів)"], size=10.5, color=MUTED, lh=1.25))
    p.append(arrow(192, 100, 234, 110, color=WATER_S, sw=1.4))
    p.append(arrow(192, 120, 296, 156, color=WATER_S, sw=1.4))
    drops = [(240, 110), (300, 160), (370, 120), (440, 168), (510, 120),
             (575, 164), (645, 120), (710, 164), (780, 120), (840, 158)]
    for (dx, dy) in drops:
        p.append(circle(dx, dy, 14, fill=WATER_F, stroke=WATER_S, sw=1.6))
        p.append(text(dx, dy + 4, "⊕", size=13, color=WATER_S, bold=True))
    p.append(text(885, 150, "…", size=18, color=MUTED, bold=True))
    p.append(text(912, 116, "∞", size=22, color=NEG, bold=True))
    for (lx, ly, s) in [(240, 88, "s₁ = b⊕d"), (510, 98, "s₂ = a⊕b⊕e"), (780, 98, "s₃ = c")]:
        p.append(text(lx, ly, s, size=9.5, color=NEG, anchor="middle"))
    for gx in (200, 500, 800):
        p.append(line(gx, 206, gx, 326, color=MUTED, sw=1.2, dash="3 5"))
    buckets = [
        (200, "Приймач R1", "упіймав: s₂,s₃,s₆,s₇,s₉"),
        (500, "Приймач R2", "упіймав: s₁,s₃,s₄,s₈,s₁₀"),
        (800, "Приймач R3", "упіймав: s₄,s₅,s₆,s₈,s₉"),
    ]
    rbw = 230
    for (cx, head, caught) in buckets:
        x0 = cx - rbw / 2
        p.append(rect(x0, 330, rbw, 130, fill=FILL, stroke=FIELD, sw=1.8, rx=8))
        p.append(text(x0 + 16, 358, head, size=13, color=FIELD, anchor="start", bold=True))
        p.append(text(x0 + 16, 382, caught, size=11, color=MUTED, anchor="start"))
        p.append(text(x0 + 16, 404, "різні краплі, ніж у сусідів", size=11, color=INK, anchor="start"))
        p.append(text(x0 + 16, 436, "✓ будь-яких k+ε → файл", size=12, color=FIELD, anchor="start", bold=True))
    p.append(mtext(W / 2, 508,
                   ["Кожен приймач ловить СВОЮ жменю крапель — усі різні. Щойно набралося трохи більше за файл,",
                    "він відновлює все. Жодного «перешли пакет №7»."],
                   size=12, color=INK, lh=1.4, bold=True))
    render(os.path.join(OUT, "fountain-idea.svg"), W, H, *p,
           title="Фонтан: байдуже, ЯКІ краплі впіймав — важливо лише СКІЛЬКИ")


# ── binom-concentration: довший блок → вужчий розподіл частки втрат ────────────
def fig_binom_concentration():
    W, H = 960, 720
    p = []
    p_loss = 0.05
    thresh = 0.20
    ox, aw = 120, 760
    fmax = 0.5

    def panel(oy, ah, titleY, n, label, color, fillc):
        frags = []
        threshLineTop = titleY + 30
        frags.append(text(ox, titleY, label, size=14, color=color, bold=True, anchor="start"))
        frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))
        frags.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.4))
        for f in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
            x = ox + f / fmax * aw
            frags.append(line(x, oy, x, oy + 5, color=INK, sw=1))
            frags.append(text(x, oy + 20, "%.1f" % f, size=10.5, color=MUTED))
        tx = ox + thresh / fmax * aw
        frags.append(line(tx, threshLineTop, tx, oy + 5, color=POS, sw=1.8, dash="5 4"))
        frags.append(text(tx + 8, threshLineTop + 14, "поріг загибелі f = 0.20",
                           size=11.5, color=POS, bold=True, anchor="start"))
        probs = [math.comb(n, l) * p_loss ** l * (1 - p_loss) ** (n - l) for l in range(n + 1)]
        pmax = max(probs)
        spacing = aw / fmax / n
        barw = max(3, spacing * 0.7)
        for l in range(n + 1):
            f = l / n
            if f > fmax + 1e-9:
                continue
            x = ox + f / fmax * aw
            h = probs[l] / pmax * ah
            tail = f > thresh
            frags.append(rect(x - barw / 2, oy - h, barw, h,
                               fill=("#fdeceb" if tail else fillc),
                               stroke=(POS if tail else color), sw=1.2, rx=1))
        tailp = sum(probs[l] for l in range(n + 1) if l / n > thresh)
        frags.append(text(ox + aw, titleY, "хвіст P(f > 0.20) = %.2f %%" % (tailp * 100),
                           size=13, color=POS, anchor="end", bold=True))
        return frags

    p += panel(oy=330, ah=200, titleY=70, n=10, label="Код (10,8) — σ(f) ≈ 6.9 %", color=NEG, fillc="#eaf0fd")
    p += panel(oy=650, ah=200, titleY=400, n=20, label="Код (20,16) — σ(f) ≈ 4.9 %", color=FIELD, fillc="#eafaee")

    p.append(text(ox + aw / 2, 700, "частка втрат f = L / n", size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "binom-concentration.svg"), W, H, *p,
           title="Концентрація частки втрат: довший блок → вужчий розподіл → тонший хвіст за порогом")


# ── risk-vs-blocklen: залишковий ризик спадає експоненційно з n (лог-шкала) ────
def fig_risk_vs_blocklen():
    W, H = 960, 620
    p = []
    R = 0.8
    p_loss = 0.05
    a = 1 - R  # 0.20 — поріг загибелі за часткою
    D = a * math.log(a / p_loss) + (1 - a) * math.log((1 - a) / (1 - p_loss))
    n_lo, n_hi = 5, 38
    ox, oy = 150, 520
    aw, ah = 740, 400
    y_lo, y_hi = -4, 0  # log10(P): від 1e-4 (0.01 %) до 1 (100 %)

    def yof(val):
        lv = max(y_lo, min(y_hi, math.log10(val)))
        return oy - (lv - y_lo) / (y_hi - y_lo) * ah

    def xof(n):
        return ox + (n - n_lo) / (n_hi - n_lo) * aw

    def exact_tail(n):
        e = round(a * n)
        s = sum(math.comb(n, l) * p_loss ** l * (1 - p_loss) ** (n - l) for l in range(0, e + 1))
        return 1 - s

    p.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 46, "n — довжина блоку (пакетів), швидкість R = 0.8 стала",
                   size=12.5, color=INK, bold=True))
    p.append(text(ox, oy - ah - 24, "P(блок гине), лог-шкала", size=12.5, color=INK, bold=True, anchor="start"))

    grid_labels = {0: "100 %", -1: "10 %", -2: "1 %", -3: "0.1 %", -4: "0.01 %"}
    for exp10 in range(y_lo, y_hi + 1):
        val = 10 ** exp10
        y = yof(val)
        p.append(line(ox, y, ox + aw, y, color=("#d6d9de" if exp10 != y_lo else INK), sw=1))
        p.append(text(ox - 12, y + 4, grid_labels[exp10], size=10.5, color=MUTED, anchor="end"))

    for n in range(n_lo, n_hi + 1, 5):
        x = xof(n)
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1))
        p.append(text(x, oy + 20, str(n), size=10.5, color=MUTED))

    ty = yof(0.001)
    p.append(line(ox, ty, ox + aw, ty, color=POS, sw=1.6, dash="6 4"))
    p.append(text(ox + aw, ty - 8, "ціль 0.1 %", size=11.5, color=POS, bold=True, anchor="end"))

    pts_exact = ["%.1f,%.1f" % (xof(n), yof(exact_tail(n))) for n in range(n_lo, n_hi + 1)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts_exact), NEG))

    pts_ch = ["%.1f,%.1f" % (xof(n), yof(math.exp(-n * D))) for n in range(n_lo, n_hi + 1)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="7 5"/>' % (" ".join(pts_ch), MUTED))

    p.append(line(700, 84, 730, 84, color=NEG, sw=2.6))
    p.append(text(738, 88, "точний хвіст (комбінаторний)", size=11.5, color=NEG, anchor="start", bold=True))
    p.append(line(700, 106, 730, 106, color=MUTED, sw=2.2, dash="7 5"))
    p.append(text(738, 110, "межа Чернова exp(−n·D)", size=11.5, color=MUTED, anchor="start", bold=True))

    def mark(n, col, label, dy):
        x, y = xof(n), yof(exact_tail(n))
        p.append(circle(x, y, 4.5, fill=col, stroke=col, sw=1))
        p.append(text(x, y + dy, label, size=11, color=col, bold=True, anchor="middle"))

    mark(10, NEG, "(10,8): 1.15 %", -14)
    mark(20, FIELD, "(20,16): 0.26 %", -14)
    mark(23, POS, "n≈23: перший прорив цілі", 22)

    render(os.path.join(OUT, "risk-vs-blocklen.svg"), W, H, *p,
           title="Залишковий ризик спадає експоненційно з довжиною блоку (лог-шкала)")


if __name__ == "__main__":
    fig_fec_vs_arq()
    fig_block_erasure()
    fig_interleave_burst()
    fig_source_channel()
    fig_systematic_matrix()
    fig_packet_block()
    fig_fountain_timeline()
    fig_fountain_idea()
    fig_binom_concentration()
    fig_risk_vs_blocklen()
    print("ok: fec-vs-arq, block-erasure, interleave-burst, source-channel, systematic-matrix, packet-block, "
          "fountain-timeline, fountain-idea, binom-concentration, risk-vs-blocklen")
