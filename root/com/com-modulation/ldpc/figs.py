# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

VFILL = "#eafaf0"   # вузол-біт (variable)
VSTRK = "#27ae60"
CFILL = "#eef4ff"   # вузол-перевірка (check)
CSTRK = "#2457d6"
BADFILL = "#fdecea"
BADSTRK = "#c0392b"

# спільний код: 6 бітів b0..b5, 4 перевірки c0..c3, регулярний (2,3)
#   c0: b0 b1 b2 ; c1: b0 b3 b4 ; c2: b1 b3 b5 ; c3: b2 b4 b5
CHECKS = [[0, 1, 2], [0, 3, 4], [1, 3, 5], [2, 4, 5]]
NB, NC = 6, 4


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── tanner: розріджена матриця H  ⇄  двочастковий граф ────────────────────────

def fig_tanner():
    W, H = 800, 430
    p = []

    # --- ліворуч: матриця H (4 рядки × 6 стовпців) ---
    cw, ch = 42, 38
    mx, my = 66, 108
    p.append(text(mx + NB * cw / 2, my - 40, "матриця H", size=15, color=INK, bold=True))
    # шапка стовпців
    for j in range(NB):
        p.append(text(mx + j * cw + cw / 2, my - 12, "b%d" % j, size=12, color=VSTRK, bold=True))
    for r in range(NC):
        ry = my + r * ch
        p.append(text(mx - 14, ry + ch / 2 + 4, "c%d" % r, size=12, color=CSTRK, bold=True, anchor="end"))
        for j in range(NB):
            on = j in CHECKS[r]
            x = mx + j * cw
            p.append(rect(x, ry, cw, ch, fill=CFILL if on else BG,
                          stroke=CSTRK if on else "#dfe3e8", sw=1.8 if on else 1.0, rx=4))
            p.append(text(x + cw / 2, ry + ch / 2 + 5, "1" if on else "0", size=13,
                          color=CSTRK if on else "#c7ccd3", bold=on))

    # --- посередині: ⇄ ---
    midx = mx + NB * cw + 34
    p.append(text(midx, my + NC * ch / 2 + 6, "⇄", size=30, color=MUTED))

    # --- праворуч: граф Таннера ---
    gx0, gx1 = midx + 34, W - 40
    p.append(text((gx0 + gx1) / 2, my - 40, "граф Таннера", size=15, color=INK, bold=True))
    vy, cy = my - 4, my + NC * ch - 8
    vx = [gx0 + i * (gx1 - gx0) / (NB - 1) for i in range(NB)]
    cxs = [gx0 + 26 + j * (gx1 - gx0 - 52) / (NC - 1) for j in range(NC)]

    # ребра спершу (щоб вузли лягли зверху)
    for r in range(NC):
        for j in CHECKS[r]:
            p.append(line(vx[j], vy + 15, cxs[r], cy - 15, color="#b6bcc4", sw=1.6))
    # вузли-біти (кружки)
    for j in range(NB):
        p.append(circle(vx[j], vy, 15, fill=VFILL, stroke=VSTRK, sw=2.0))
        p.append(text(vx[j], vy + 5, "b%d" % j, size=12, color=VSTRK, bold=True))
    # вузли-перевірки (квадрати)
    for r in range(NC):
        p.append(rect(cxs[r] - 16, cy - 16, 32, 32, fill=CFILL, stroke=CSTRK, sw=2.0, rx=5))
        p.append(text(cxs[r], cy + 5, "c%d" % r, size=12, color=CSTRK, bold=True))

    p.append(text(gx0 - 8, vy - 26, "біти", size=11, color=VSTRK, anchor="start", italic=True))
    p.append(text(gx0 - 8, cy + 40, "перевірки", size=11, color=CSTRK, anchor="start", italic=True))

    p.append(text(W / 2, H - 20, "одиниця в H = ребро у графі  ·  порожнеча матриці = рідкі ребра (низька щільність)",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "tanner.svg"), W, H, *p,
           title="LDPC: розріджена матриця перевірок — це рідкий граф")


# ── decode: один прохід перевертання бітів ───────────────────────────────────

def fig_decode():
    W, H = 780, 430
    p = []

    recv = [1, 1, 1, 0, 1, 1]     # прийняте (b2 перевернуто)
    bad_bit = 2
    # порушені перевірки при цьому слові: c0 і c3
    viol = []
    for r in range(NC):
        s = 0
        for j in CHECKS[r]:
            s ^= recv[j]
        viol.append(s)

    gx0, gx1 = 90, W - 90
    vy, cy = 96, 250
    vx = [gx0 + i * (gx1 - gx0) / (NB - 1) for i in range(NB)]
    cxs = [gx0 + 40 + j * (gx1 - gx0 - 80) / (NC - 1) for j in range(NC)]

    # ребра: червоні — від битого біта до порушених перевірок; решта сірі
    for r in range(NC):
        for j in CHECKS[r]:
            hot = (j == bad_bit and viol[r])
            p.append(line(vx[j], vy + 16, cxs[r], cy - 18, color=BADSTRK if hot else "#c2c8d0",
                          sw=2.6 if hot else 1.4))

    # вузли-біти
    for j in range(NB):
        flip = (j == bad_bit)
        p.append(circle(vx[j], vy, 16, fill=BADFILL if flip else VFILL,
                        stroke=BADSTRK if flip else VSTRK, sw=2.6 if flip else 2.0))
        p.append(text(vx[j], vy - 26, "b%d" % j, size=11, color=MUTED))
        p.append(text(vx[j], vy + 5, str(recv[j]), size=14,
                      color=BADSTRK if flip else INK, bold=True))
    p.append(text(vx[bad_bit], vy - 46, "перевернутий у каналі", size=10.5, color=BADSTRK, bold=True))

    # вузли-перевірки з вердиктом
    for r in range(NC):
        bads = viol[r]
        fill = BADFILL if bads else "#eafaf0"
        strk = BADSTRK if bads else VSTRK
        p.append(rect(cxs[r] - 20, cy - 20, 40, 40, fill=fill, stroke=strk, sw=2.4, rx=6))
        p.append(text(cxs[r], cy + 6, "✗" if bads else "✓", size=18, color=strk, bold=True))
        p.append(text(cxs[r], cy + 40, "c%d" % r, size=11, color=MUTED))
        p.append(text(cxs[r], cy + 56, "порушена" if bads else "сходиться",
                      size=10, color=strk, italic=True))

    box, bw, bh = textbox(W / 2, H - 46,
                          "b2 сидить в обох порушених перевірках (c0, c3)  →  перевертаємо  →  усі перевірки сходяться",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "decode.svg"), W, H, *p,
           title="Декодування: незгодні перевірки сходяться на винному біті")


# ── waterfall: крива надійності, «водоспад» LDPC біля межі Шеннона ────────────

def fig_waterfall():
    W, H = 720, 460
    p = []

    px0, px1 = 96, 660          # вісь X (Eb/N0)
    py0, py1 = 74, 356          # вісь Y (BER: 1e-1 угорі … 1e-7 унизу)
    snr_max = 11.0

    def X(s):
        return px0 + (s / snr_max) * (px1 - px0)

    def Y(e):                   # e — показник степеня 10 (від -1 до -7)
        return py0 + ((-1 - e) / 6.0) * (py1 - py0)

    # рамка й горизонтальні лінії-декади
    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 10, y + 4, "10⁻%d" % k, size=11, color=MUTED, anchor="end"))
    # вісь X
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    for s in range(0, 12, 2):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 20, str(s), size=11, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 40, "відношення сигнал/шум  Eb/N0 , дБ", size=12, color=INK))
    p.append(text(px0 - 62, (py0 + py1) / 2, "BER", size=12, color=INK))

    # межа Шеннона — вертикальна пунктирна
    xs = X(1.0)
    p.append(line(xs, py0 - 4, xs, py1, color=FIELD, sw=2.0, dash="6 5"))
    p.append(text(xs, py0 - 12, "межа Шеннона", size=11, color=FIELD, bold=True))

    # криві (схематичні)
    ldpc = [(1.4, -1), (1.6, -1.8), (1.8, -3.2), (2.0, -5.2), (2.15, -6.8)]
    hamm = [(4.5, -1), (6.5, -2.1), (8.5, -3.5), (10.3, -5.2)]
    unc = [(5.5, -1), (8, -1.9), (10.5, -2.8), (11, -3.0)]
    p.append(polyline([(X(s), Y(e)) for s, e in unc], color=MUTED, sw=2.4))
    p.append(polyline([(X(s), Y(e)) for s, e in hamm], color=CSTRK, sw=2.6))
    p.append(polyline([(X(s), Y(e)) for s, e in ldpc], color=BADSTRK, sw=3.0))

    # стрілка «частки дБ» між межею і водоспадом
    p.append(line(xs, Y(-4), X(1.8), Y(-4), color=INK, sw=1.3, dash="3 3"))
    p.append(text((xs + X(1.8)) / 2, Y(-4) - 8, "частки дБ", size=10.5, color=INK, italic=True))

    # легенда — рядком під віссю X
    ly = py1 + 58
    items = [("LDPC (довгий)", BADSTRK), ("Геммінг (7,4)", CSTRK), ("без коду", MUTED)]
    lx = px0 + 20
    for label, col in items:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3.0))
        p.append(text(lx + 32, ly + 4, label, size=11.5, color=INK, anchor="start"))
        lx += 32 + text_width(label, 11.5) + 42

    render(os.path.join(OUT, "waterfall.svg"), W, H, *p,
           title="Чому LDPC — «майже Шеннон»: водоспад упритул до межі")


# ── incremental: перевертання біта чіпає лише його перевірки ─────────────────

def fig_incremental():
    W, H = 820, 500
    p = []

    recv = [1, 1, 1, 0, 1, 1]          # b2 перевернуто
    flip = 2
    viol = []
    for r in range(NC):
        s = 0
        for j in CHECKS[r]:
            s ^= recv[j]
        viol.append(s)
    touched = [r for r in range(NC) if flip in CHECKS[r]]

    gx0, gx1 = 100, W - 100
    vy, cy = 100, 238
    vx = [gx0 + i * (gx1 - gx0) / (NB - 1) for i in range(NB)]
    cxs = [gx0 + 50 + j * (gx1 - gx0 - 100) / (NC - 1) for j in range(NC)]

    # ребра: гарячі — лише ті, що виходять із перевернутого біта
    for r in range(NC):
        for j in CHECKS[r]:
            hot = (j == flip)
            p.append(line(vx[j], vy + 17, cxs[r], cy - 22,
                          color=BADSTRK if hot else "#dfe3e8", sw=2.8 if hot else 1.2))
    # біти
    for j in range(NB):
        f = (j == flip)
        p.append(circle(vx[j], vy, 17, fill=BADFILL if f else VFILL,
                        stroke=BADSTRK if f else VSTRK, sw=2.6 if f else 1.8))
        p.append(text(vx[j], vy - 30, "b%d" % j, size=11, color=MUTED))
        p.append(text(vx[j], vy + 5, str(recv[j]), size=14,
                      color=BADSTRK if f else INK, bold=True))
    # перевірки: торкнуті vs незаймані
    for r in range(NC):
        t = r in touched
        p.append(rect(cxs[r] - 22, cy - 22, 44, 44, fill=BADFILL if t else BG,
                      stroke=BADSTRK if t else "#c7ccd3", sw=2.6 if t else 1.4, rx=6))
        p.append(text(cxs[r], cy + 6, "c%d" % r, size=13,
                      color=BADSTRK if t else MUTED, bold=True))
        p.append(text(cxs[r], cy + 44, "інвертуємо" if t else "не читали", size=11,
                      color=BADSTRK if t else MUTED, bold=t, italic=not t))

    # синдром до / після
    sy, cwd = 336, 38

    def strip(x0, vals):
        out = []
        for k, v in enumerate(vals):
            hot = k in touched
            out.append(rect(x0 + k * cwd, sy, cwd, cwd, fill=BADFILL if hot else "#f4f6f8",
                            stroke=BADSTRK if hot else "#c7ccd3", sw=2.2 if hot else 1.2, rx=4))
            out.append(text(x0 + k * cwd + cwd / 2, sy + cwd / 2 + 5, str(v), size=14,
                            color=BADSTRK if hot else INK, bold=True))
            out.append(text(x0 + k * cwd + cwd / 2, sy - 9, "c%d" % k, size=10, color=MUTED))
        return out

    lx, rx = 176, 508
    p.append(text(lx + 2 * cwd, sy - 30, "синдром до", size=12.5, color=INK, bold=True))
    p.extend(strip(lx, viol))
    p.append(text(rx + 2 * cwd, sy - 30, "синдром після", size=12.5, color=INK, bold=True))
    p.extend(strip(rx, [0, 0, 0, 0]))
    p.append(arrow(lx + 4 * cwd + 24, sy + cwd / 2, rx - 24, sy + cwd / 2, sw=2.0))
    p.append(text((lx + 4 * cwd + rx) / 2, sy + cwd / 2 - 13, "2 інверсії", size=11,
                  color=INK, italic=True))

    box, bw, bh = textbox(W / 2, 452,
                          "перерахувати весь синдром — 12 XOR по всіх ребрах\n"
                          "інвертувати лише ті дві перевірки, яких торкнувся біт, — 2 дії",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "incremental.svg"), W, H, *p,
           title="Перевернутий біт — подія локальна: чіпає лише свої перевірки")


# ── fliprule: один біт за крок чи всі з максимумом ───────────────────────────

def fig_fliprule():
    W, H = 880, 570
    p = []

    box, bw, bh = textbox(W / 2, 84,
                          "прийнято  0 1 0 0 1 0    (надіслано 1 1 0 0 1 1 — канал побив b0 і b5)\n"
                          "синдром 1 1 1 1: порушені всі чотири, рахунок кожного біта = 2 — глуха нічия",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    lcx, rcx = 228, 652
    p.append(text(lcx, 168, "перевернути ОДИН біт", size=13, color=FIELD, bold=True))
    p.append(text(rcx, 168, "перевернути ВСІ з максимумом", size=13, color=BADSTRK, bold=True))

    y0, y1, y2 = 232, 312, 392

    def state(cx, cy, s, col):
        b, w, h = textbox(cx, cy, s, size=13, bold=True, fill=BG, stroke=col, sw=2.0, pad=11)
        return b

    # ліва гілка: три стани
    p.append(state(lcx, y0, "0 1 0 0 1 0    синдром 1111", "#c7ccd3"))
    p.append(arrow(lcx, y0 + 22, lcx, y1 - 22, sw=1.8))
    p.append(text(lcx + 14, (y0 + y1) / 2 + 4, "перевертає b0", size=11,
                  color=MUTED, anchor="start", italic=True))
    p.append(state(lcx, y1, "1 1 0 0 1 0    синдром 0011", "#c7ccd3"))
    p.append(arrow(lcx, y1 + 22, lcx, y2 - 22, sw=1.8))
    p.append(text(lcx + 14, (y1 + y2) / 2 + 4, "перевертає b5", size=11,
                  color=MUTED, anchor="start", italic=True))
    p.append(state(lcx, y2, "1 1 0 0 1 1    синдром 0000", FIELD))

    # права гілка: один стрибок
    p.append(state(rcx, y0, "0 1 0 0 1 0    синдром 1111", "#c7ccd3"))
    p.append(arrow(rcx, y0 + 22, rcx, y2 - 22, sw=1.8))
    p.append(text(rcx + 14, (y0 + y2) / 2 + 4, "перевертає всі шість", size=11,
                  color=MUTED, anchor="start", italic=True))
    p.append(state(rcx, y2, "1 0 1 1 0 1    синдром 0000", BADSTRK))

    # вердикти
    b, w, h = textbox(lcx, 462, "= надіслане слово  ✓", size=12.5, bold=True,
                      fill="#eafaf0", stroke=FIELD, sw=2.0, pad=10)
    p.append(b)
    b, w, h = textbox(rcx, 462, "теж кодове слово — але за 4 біти\nвід надісланого  ✗", size=12.5,
                      bold=True, fill=BADFILL, stroke=BADSTRK, sw=2.0, pad=10)
    p.append(b)

    box, bw, bh = textbox(W / 2, 530,
                          "той самий блок, той самий рахунок порушених перевірок —\n"
                          "різниця лише в тому, скільки бітів перевертати за один крок",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "fliprule.svg"), W, H, *p,
           title="Скільки бітів перевертати за крок — і куди це заводить")


# ── oscillate: вічний цикл, з якого рятує лише ліміт ─────────────────────────

def fig_oscillate():
    W, H = 900, 520
    p = []

    box, bw, bh = textbox(W / 2, 80,
                          "код на 12 бітів: помилки в b1 і b9 сидять в одній перевірці c5 —\n"
                          "вона їх взаємно гасить і мовчить, тож звинуватити нікого",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    b, w, h = textbox(W / 2, 180,
                      "w = 0100 0000 0100     синдром = 1001 0000\n"
                      "порушені c0, c3 · найбільший рахунок = 1 · нічия на шести бітах",
                      size=12.5, bold=True, fill=BADFILL, stroke=BADSTRK, sw=2.2, pad=12)
    p.append(b)

    b, w, h = textbox(W / 2, 340,
                      "w = 1100 0000 0100     синдром = 0001 1000\n"
                      "порушені c3, c4 · найбільший рахунок = 1 · знову нічия",
                      size=12.5, bold=True, fill=BADFILL, stroke=BADSTRK, sw=2.2, pad=12)
    p.append(b)

    p.append(arrow(380, 222, 380, 298, sw=2.2))
    p.append(text(392, 265, "перевертає b0", size=11, color=MUTED, anchor="start", italic=True))
    p.append(arrow(520, 298, 520, 222, sw=2.2))
    p.append(text(532, 265, "перевертає b0 назад", size=11, color=MUTED, anchor="start", italic=True))

    box, bw, bh = textbox(W / 2, 450,
                          "жодного прогресу: стан повертається на себе — цикл із періодом 2, вічно\n"
                          "єдиний вихід — жорсткий ліміт ітерацій",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "oscillate.svg"), W, H, *p,
           title="Коли декодер зациклюється")


# ── hist-timeline: 30 років між винаходом і вжитком ──────────────────────────

def fig_hist_timeline():
    W, H = 1080, 530
    p = []
    Y0, Y1 = 1948, 2020
    x0, x1 = 80, 1000
    AX = 400                       # вісь років

    def X(y):
        return x0 + (y - Y0) * (x1 - x0) / float(Y1 - Y0)

    # смуга мовчання 1963→1993 (тлом, під усім)
    dz0, dz1 = X(1963), X(1993)
    p.append(rect(dz0, 62, dz1 - dz0, AX - 62, fill="#fbf0ee", stroke="#e9cbc5", sw=1.2, rx=8))

    # вісь + десятиліття
    p.append(line(x0 - 16, AX, x1 + 16, AX, color=INK, sw=2.0))
    for yr in range(1950, 2021, 10):
        p.append(line(X(yr), AX, X(yr), AX + 8, color=INK, sw=1.4))
        p.append(text(X(yr), AX + 26, str(yr), size=12, color=MUTED))

    # рівні підписів: сусіди по горизонталі сидять на РІЗНІЙ висоті
    LEV = [60, 138, 216, 294]
    TINT = {BADSTRK: "#fdecea", CSTRK: "#eef4ff", FIELD: "#eafaf0", MUTED: "#f1f2f4", INK: "#f4f6f8"}

    EV = [
        (1948, ["1948", "Шеннон:", "теорема"],              0, INK),
        (1960, ["1960", "Галлагер:", "дисертація MIT"],     1, BADSTRK),
        (1963, ["1963", "монографія", "MIT Press"],         2, BADSTRK),
        (1975, ["1975", "Зяблов, Пінскер", "ІППІ, Москва"], 0, MUTED),
        (1981, ["1981", "граф Таннера"],                    1, MUTED),
        (1993, ["1993", "турбокоди"],                       3, CSTRK),
        (1996, ["1996", "Маккей і Ніл:", "перевідкриття"],  1, CSTRK),
        (2001, ["2001", "0.0045 дБ"],                       3, CSTRK),
        (2003, ["2003", "DVB-S2"],                          0, FIELD),
        (2016, ["2016", "5G NR"],                           2, FIELD),
        (2020, ["2020", "Японська премія"],                 0, FIELD),
    ]
    for yr, lines, lv, col in EV:
        x, cy = X(yr), AX - LEV[lv]
        box, bw, bh = textbox(x, cy, "\n".join(lines), size=12, pad=10,
                              fill=TINT[col], stroke=col, sw=2.0, color=INK)
        p.append(line(x, AX, x, cy + bh / 2, color=col, sw=1.6))
        p.append(circle(x, AX, 5.5, fill=col, stroke=col, sw=1.0))
        p.append(box)

    # дужка «мертвої зони» під віссю
    by = 468
    p.append(arrow(dz1, by, dz0, by, color=BADSTRK, sw=1.8))
    p.append(arrow(dz0, by, dz1, by, color=BADSTRK, sw=1.8))
    p.append(text((dz0 + dz1) / 2, by + 26,
                  "30 років: код лежить у бібліотеці, поле дивиться в інший бік",
                  size=12.5, color=BADSTRK, bold=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="LDPC: винайдено 1960-го, знадобилося у 1990-х")


# ── hist-compute: арифметика, яка поховала код ───────────────────────────────

def fig_hist_compute():
    import math
    W, H = 880, 430
    p = []
    ax0, ax1 = 250, 830          # вісь: 10² … 10¹¹
    E0, E1 = 2, 11

    def X(v):
        return ax0 + (math.log10(v) - E0) * (ax1 - ax0) / float(E1 - E0)

    SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"

    def sup(n):
        return "".join(SUP[int(d)] for d in str(n))

    # сітка декад — лише у проміжках МІЖ смугами, щоб лінії не лізли на написи
    GAPS = [(62, 70), (116, 145), (191, 220), (266, 286)]
    for e in range(E0, E1 + 1):
        gx = ax0 + (e - E0) * (ax1 - ax0) / float(E1 - E0)
        for gy0, gy1 in GAPS:
            p.append(line(gx, gy0, gx, gy1, color="#e6e9ee", sw=1.0))
        p.append(text(gx, 306, "10" + sup(e), size=11, color=MUTED))
    p.append(line(ax0, 286, ax1, 286, color=INK, sw=1.6))
    p.append(text((ax0 + ax1) / 2, 332, "пропускна здатність декодера, біт/с (логарифмічна шкала)",
                  size=12, color=INK))

    BARS = [
        (70,  ["IBM 7090, 1960:", "декодер Галлагера"], 500, BADSTRK, BADFILL, "≈500 біт/с"),
        (145, ["модем Bell 103, 1962:", "що несла телефонна лінія"], 300, MUTED, "#f1f2f4", "300 біт/с"),
        (220, ["5G NR, стеля IMT-2020:", "LDPC у кишені"], 2e10, FIELD, "#eafaf0", "20 Гбіт/с"),
    ]
    for by, lab, val, col, fill, vlab in BARS:
        bw = X(val) - ax0
        p.append(rect(ax0, by, bw, 46, fill=fill, stroke=col, sw=2.2, rx=4))
        p.append(mtext(ax0 - 15, by + 23 - 12 * 1.3 / 2 + 12 * 0.35, lab,
                       size=12, color=INK, anchor="end"))
        if bw > 180:             # широка смуга — підпис усередині
            p.append(text(ax0 + bw - 14, by + 29, vlab, size=13.5, color=col, bold=True, anchor="end"))
        else:                    # вузька — праворуч від смуги
            p.append(text(ax0 + bw + 12, by + 29, vlab, size=13.5, color=col, bold=True, anchor="start"))

    # множник між 1960-м і сьогоденням
    fy = 366
    p.append(arrow(X(2e10), fy, X(500), fy, color=INK, sw=1.6))
    p.append(arrow(X(500), fy, X(2e10), fy, color=INK, sw=1.6))
    p.append(text((X(500) + X(2e10)) / 2, fy - 16, "≈ ×10⁷", size=15, color=INK, bold=True))

    p.append(text(W / 2, H - 14,
                  "0.1 с на ітерацію для блоку ≈500 бітів — число з монографії Галлагера 1963 року; ~10 ітерацій → ≈500 біт/с",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-compute.svg"), W, H, *p,
           title="Код не змінився — подешевшала арифметика")


# ── bp-messages: правило «все, КРІМ адресата» на обох типах вузлів ────────────

def fig_bp_messages():
    W, H = 1000, 600
    p = []

    p.append(line(W / 2, 56, W / 2, H - 96, color="#dfe3e8", sw=1.5, dash="5 5"))

    # ═══ ЛІВОРУЧ: вузол-біт ═══
    p.append(text(250, 68, "вузол-біт: додай усе, крім адресата", size=14.5, color=VSTRK, bold=True))

    bx, by = 250, 320
    cxs = [140, 250, 360]
    cy = 178
    names = ["c₁", "c₂", "c₃"]

    # ребра
    for i, cx in enumerate(cxs):
        p.append(line(bx, by - 30, cx, cy + 20, color="#ccd2da", sw=1.5))
    # вихідне повідомлення до c₁ — зелене
    p.append(arrow(bx - 12, by - 32, cxs[0] + 14, cy + 24, color=VSTRK, sw=3.0))
    # вхідні від c₂, c₃ — сині
    for cx in cxs[1:]:
        p.append(arrow(cx, cy + 24, bx + (10 if cx > bx else 0), by - 34, color=CSTRK, sw=2.4))

    # вузли-перевірки
    for i, cx in enumerate(cxs):
        tgt = (i == 0)
        p.append(rect(cx - 19, cy - 19, 38, 38, fill=BADFILL if tgt else CFILL,
                      stroke=BADSTRK if tgt else CSTRK, sw=2.2, rx=5))
        p.append(text(cx, cy + 6, names[i], size=13, color=BADSTRK if tgt else CSTRK, bold=True))
    p.append(text(cxs[0], cy - 32, "адресат", size=11.5, color=BADSTRK, bold=True))

    # вузол-біт
    p.append(circle(bx, by, 30, fill=VFILL, stroke=VSTRK, sw=2.6))
    p.append(text(bx, by + 6, "b", size=17, color=VSTRK, bold=True))

    # канальний LLR знизу
    p.append(arrow(bx, by + 92, bx, by + 36, color=INK, sw=2.2))
    p.append(text(bx, by + 114, "L_кан(b)  — те, що сказав канал", size=12, color=INK))

    # «не вертається» — збоку від ребра b–c₁
    p.append(text(96, 262, "✗", size=19, color=BADSTRK, bold=True, anchor="middle"))
    p.append(text(96, 284, "почуте", size=10.5, color=BADSTRK, anchor="middle"))
    p.append(text(96, 298, "від c₁ —", size=10.5, color=BADSTRK, anchor="middle"))
    p.append(text(96, 312, "не назад", size=10.5, color=BADSTRK, anchor="middle"))

    box, bw, bh = textbox(250, 496,
                          "L(b → c₁) = L_кан(b) + M(c₂→b) + M(c₃→b)\nвнесок самого c₁ у суму НЕ входить",
                          size=13, bold=True, fill="#f2fbf5", stroke=VSTRK, sw=2.0, pad=13)
    p.append(box)

    # ═══ ПРАВОРУЧ: вузол-перевірка ═══
    p.append(text(750, 68, "вузол-перевірка: ⊞ усіх, крім адресата", size=14.5, color=CSTRK, bold=True))

    kx, ky = 750, 320
    vxs = [640, 750, 860]
    vy = 178
    vnames = ["b₁", "b₂", "b₃"]

    for i, vx in enumerate(vxs):
        p.append(line(kx, ky - 30, vx, vy + 20, color="#ccd2da", sw=1.5))
    p.append(arrow(kx - 12, ky - 32, vxs[0] + 14, vy + 24, color=VSTRK, sw=3.0))
    for vx in vxs[1:]:
        p.append(arrow(vx, vy + 24, kx + (10 if vx > kx else 0), ky - 34, color=CSTRK, sw=2.4))

    for i, vx in enumerate(vxs):
        tgt = (i == 0)
        p.append(circle(vx, vy, 19, fill=BADFILL if tgt else VFILL,
                        stroke=BADSTRK if tgt else VSTRK, sw=2.2))
        p.append(text(vx, vy + 6, vnames[i], size=13, color=BADSTRK if tgt else VSTRK, bold=True))
    p.append(text(vxs[0], vy - 32, "адресат", size=11.5, color=BADSTRK, bold=True))

    p.append(rect(kx - 24, ky - 24, 48, 48, fill=CFILL, stroke=CSTRK, sw=2.6, rx=6))
    p.append(text(kx, ky + 7, "c", size=17, color=CSTRK, bold=True))

    p.append(text(kx, ky + 76, "перевірка знає лише одне:", size=12, color=MUTED, italic=True))
    p.append(text(kx, ky + 96, "b₁ ⊕ b₂ ⊕ b₃ = 0", size=14, color=INK, bold=True))

    p.append(text(596, 262, "✗", size=19, color=BADSTRK, bold=True, anchor="middle"))
    p.append(text(596, 288, "те саме", size=10.5, color=BADSTRK, anchor="middle"))
    p.append(text(596, 302, "правило", size=10.5, color=BADSTRK, anchor="middle"))

    box2, _, _ = textbox(750, 496,
                         "L(c → b₁) = L(b₂→c) ⊞ L(b₃→c)\nвнесок самого b₁ у добуток НЕ входить",
                         size=13, bold=True, fill="#f1f5ff", stroke=CSTRK, sw=2.0, pad=13)
    p.append(box2)

    p.append(text(W / 2, H - 26,
                  "одне правило на обидва боки: у відповідь вузлові вкладай лише те, що дізнався ПОЗА ним — інакше він почує власне відлуння",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "bp-messages.svg"), W, H, *p,
           title="Правило «все, крім адресата» — серце поширення довіри")


# ── boxplus-minsum: точне ⊞ проти min-sum ────────────────────────────────────

def fig_boxplus():
    import math
    W, H = 860, 560
    p = []

    px0, px1 = 96, 690
    py0, py1 = 78, 396
    xmax, ymax = 6.0, 5.0

    def X(v):
        return px0 + (v / xmax) * (px1 - px0)

    def Y(v):
        return py1 - (v / ymax) * (py1 - py0)

    # осі з рисками (без наскрізної сітки — щоб жодна лінія не лягла на напис)
    for gv in range(0, 6):
        p.append(line(px0 - 5, Y(gv), px0, Y(gv), color=INK, sw=1.4))
        p.append(text(px0 - 12, Y(gv) + 4, str(gv), size=11.5, color=MUTED, anchor="end"))
    for gv in range(0, 7):
        p.append(line(X(gv), py1, X(gv), py1 + 5, color=INK, sw=1.4))
        p.append(text(X(gv), py1 + 21, str(gv), size=11.5, color=MUTED))

    p.append(line(px0, py1, px1, py1, color=INK, sw=1.8))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.8))
    p.append(text((px0 + px1) / 2, py1 + 46, "|L₂| — упевненість ДРУГОГО входу", size=13, color=INK))
    p.append(text(px0 - 46, (py0 + py1) / 2 - 10, "|L", size=13, color=INK, anchor="middle"))
    p.append(text(px0 - 46, (py0 + py1) / 2 + 8, "вих|", size=13, color=INK, anchor="middle"))

    def exact(a, b):
        return 2.0 * math.atanh(math.tanh(a / 2.0) * math.tanh(b / 2.0))

    for L1, col in ((1.0, "#8e44ad"), (2.0, FIELD), (4.0, BADSTRK)):
        pts = [(X(v / 20.0), Y(exact(L1, v / 20.0))) for v in range(0, int(xmax * 20) + 1)]
        p.append(polyline(pts, color=col, sw=3.0))
        ms = [(X(0), Y(0)), (X(L1), Y(L1)), (X(xmax), Y(L1))]
        p.append(polyline(ms, color=col, sw=1.8, dash="6 4"))
        p.append(text(X(xmax) + 10, Y(L1) - 12, "min-sum", size=10.5, color=col, anchor="start"))
        p.append(text(X(xmax) + 10, Y(exact(L1, xmax)) + 16, "точне ⊞", size=10.5, color=col, anchor="start"))
        p.append(text(X(xmax) + 10, Y(L1) + 3, "|L₁|=%d" % int(L1), size=12, color=col, bold=True, anchor="start"))

    # позначка: у нулі обидва в нулі (виноска — у чистій зоні над віссю X)
    p.append(circle(X(0), Y(0), 5, fill=BG, stroke=INK, sw=2.2))
    p.append(line(X(0) + 6, Y(0) - 6, X(1.15), Y(0) - 52, color=INK, sw=1.2))
    p.append(text(X(1.2), Y(0) - 66, "|L₂| = 0 → вихід рівно 0:", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(X(1.2), Y(0) - 50, "один невідомий біт глушить усю перевірку", size=11, color=MUTED, anchor="start"))

    box, _, _ = textbox(W / 2, 470,
                        "суцільна — точне  L₁ ⊞ L₂ = 2·atanh( tanh(L₁/2)·tanh(L₂/2) )     ·     пунктир — min-sum = min(|L₁|, |L₂|)\n"
                        "точна крива ЗАВЖДИ нижча: min-sum перебільшує впевненість, і тим більше, чим ближчі входи",
                        size=12, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    p.append(text(W / 2, H - 20,
                  "виходить не більше за найслабший вхід — ланцюг міцний рівно настільки, наскільки міцна найслабша ланка",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "boxplus-minsum.svg"), W, H, *p,
           title="Точне ⊞ і його дешевий двійник min-sum")


# ── cycle-echo: 4-цикл змушує BP рахувати те саме двічі ──────────────────────

def fig_cycle_echo():
    W, H = 980, 560
    p = []

    p.append(line(452, 60, 452, H - 70, color="#dfe3e8", sw=1.5, dash="5 5"))

    # ═══ ЛІВОРУЧ: граф із 4-циклом ═══
    p.append(text(228, 76, "дві перевірки ділять ДВА біти → 4-цикл", size=13.5, color=BADSTRK, bold=True))

    # цикл малюємо ПРЯМОКУТНИКОМ: b₀ — c₀ — b₁ — c₁ — b₀, жодного перетину
    b0, c0 = (150, 172), (322, 172)
    b1, c1 = (322, 330), (150, 330)

    p.append(line(b0[0] + 21, b0[1], c0[0] - 21, c0[1], color=BADSTRK, sw=3.0))   # верх
    p.append(line(c0[0], c0[1] + 21, b1[0], b1[1] - 21, color=BADSTRK, sw=3.0))   # право
    p.append(line(b1[0] - 21, b1[1], c1[0] + 21, c1[1], color=BADSTRK, sw=3.0))   # низ
    p.append(line(c1[0], c1[1] - 21, b0[0], b0[1] + 21, color=BADSTRK, sw=3.0))   # ліво

    # висячі біти: b₂ від c₀, b₃ від c₁
    b2, b3 = (410, 92), (62, 410)
    p.append(line(c0[0] + 16, c0[1] - 16, b2[0] - 14, b2[1] + 14, color="#c2c8d0", sw=1.6))
    p.append(line(c1[0] - 16, c1[1] + 16, b3[0] + 14, b3[1] - 14, color="#c2c8d0", sw=1.6))

    for pos, lab in ((b0, "b₀"), (b1, "b₁")):
        p.append(circle(pos[0], pos[1], 21, fill=BADFILL, stroke=BADSTRK, sw=2.6))
        p.append(text(pos[0], pos[1] + 6, lab, size=13, color=BADSTRK, bold=True))
    for pos, lab in ((b2, "b₂"), (b3, "b₃")):
        p.append(circle(pos[0], pos[1], 18, fill=VFILL, stroke=VSTRK, sw=2.0))
        p.append(text(pos[0], pos[1] + 5, lab, size=12, color=VSTRK, bold=True))
    for pos, lab in ((c0, "c₀"), (c1, "c₁")):
        p.append(rect(pos[0] - 21, pos[1] - 21, 42, 42, fill=CFILL, stroke=CSTRK, sw=2.4, rx=5))
        p.append(text(pos[0], pos[1] + 6, lab, size=13, color=CSTRK, bold=True))

    # ↻ — усередині прямокутника, де тепер порожньо
    p.append(text(236, 264, "↻", size=34, color=BADSTRK, bold=True))

    p.append(text(236, 392, "думка b₀ обходить цикл і вертається до b₀", size=11.5, color=BADSTRK, bold=True))
    p.append(text(236, 410, "за два кроки — вже як «чуже, незалежне» свідчення", size=11.5, color=BADSTRK, bold=True))

    p.append(text(236, 486, "c₀: b₀⊕b₁⊕b₂ = 0     c₁: b₀⊕b₁⊕b₃ = 0", size=12.5, color=INK, bold=True))
    p.append(text(236, 508, "канал дав: L_кан = +0.5 (b₀, b₁), +1.0 (b₂, b₃)", size=11.5, color=MUTED, italic=True))

    # ═══ ПРАВОРУЧ: точний MAP проти BP ═══
    p.append(text(716, 76, "апостеріорний LLR: точний проти BP", size=13.5, color=INK, bold=True))

    ax0 = 560
    scale = 118.0
    rows = [
        ("b₀, b₁", 0.8775, 1.2834, "роздув", 150),
        ("b₂, b₃", 2.1201, 1.3539, "недобір", 300),
    ]
    for lab, mapv, bpv, verdict, ry in rows:
        p.append(text(ax0 - 14, ry + 4, lab, size=13, color=INK, bold=True, anchor="end"))
        for k, (v, col, nm) in enumerate(((mapv, INK, "точний MAP"), (bpv, BADSTRK, "BP"))):
            byy = ry + 22 + k * 32
            p.append(rect(ax0, byy, v * scale, 24, fill="#e9edf2" if k == 0 else BADFILL,
                          stroke=col, sw=2.0, rx=4))
            p.append(text(ax0 + v * scale + 10, byy + 17, "%+.2f" % v, size=12.5, color=col,
                          bold=True, anchor="start"))
            p.append(text(ax0 + 8, byy + 17, nm, size=11.5, color=col, anchor="start"))
        p.append(text(ax0 + 330, ry + 42, verdict, size=13, color=BADSTRK, bold=True, anchor="start"))

    p.append(text(716, 396, "BP на 4-циклі не просто «трохи неточний»:", size=12.5, color=INK, bold=True))
    p.append(text(716, 418, "на бітах циклу він занадто впевнений,", size=12, color=MUTED))
    p.append(text(716, 438, "а на решті — навпаки, занадто боязкий.", size=12, color=MUTED))

    box, _, _ = textbox(716, 496,
                        "числа пораховано перебором усіх 4 кодових слів\nпроти BP на 30 ітераціях — розбіжність не зникає",
                        size=11.5, fill="#f6f4ec", stroke=INK, sw=1.6, pad=11)
    p.append(box)

    render(os.path.join(OUT, "cycle-echo.svg"), W, H, *p,
           title="Короткий цикл: те саме свідчення враховане двічі")


# ── staircase: сходове (IRA) кодування — паритет одним проходом ───────────────

def fig_staircase():
    W, H = 900, 470
    p = []

    # H = [ A | B ]:  A — інфо-блок, B — сходовий паритетний блок (діагональ+піддіагональ)
    A = [[0, 1], [1, 2], [0, 2], [0, 1, 2]]      # яких інфо-бітів торкається перевірка
    B = [[0], [0, 1], [1, 2], [2, 3]]            # сходи
    NR, KA, KB = 4, 3, 4
    cw = 40
    mx, my = 66, 132
    bx = mx + KA * cw + 40                        # старт блоку B (з проміжком)

    p.append(text(mx + KA * cw / 2, my - 44, "блок A · інформація", size=13, color=VSTRK, bold=True))
    p.append(text(bx + KB * cw / 2, my - 44, "блок B · паритет (сходи)", size=13, color=CSTRK, bold=True))
    for j in range(KA):
        p.append(text(mx + j * cw + cw / 2, my - 16, "s%d" % j, size=12, color=VSTRK, bold=True))
    for j in range(KB):
        p.append(text(bx + j * cw + cw / 2, my - 16, "p%d" % j, size=12, color=CSTRK, bold=True))

    for r in range(NR):
        ry = my + r * cw
        p.append(text(mx - 18, ry + cw / 2 + 4, "c%d" % r, size=12, color=INK, bold=True, anchor="end"))
        for j in range(KA):
            on = j in A[r]
            x = mx + j * cw
            p.append(rect(x, ry, cw, cw, fill="#eafaf0" if on else BG,
                          stroke=VSTRK if on else "#dfe3e8", sw=1.8 if on else 1.0, rx=4))
            if on:
                p.append(circle(x + cw / 2, ry + cw / 2, 6, fill=VSTRK, stroke=VSTRK, sw=1.0))
        for j in range(KB):
            on = j in B[r]
            x = bx + j * cw
            p.append(rect(x, ry, cw, cw, fill="#eef4ff" if on else BG,
                          stroke=CSTRK if on else "#dfe3e8", sw=1.8 if on else 1.0, rx=4))
            if on:
                p.append(circle(x + cw / 2, ry + cw / 2, 6, fill=CSTRK, stroke=CSTRK, sw=1.0))

    dvx = mx + KA * cw + 20
    p.append(line(dvx, my - 6, dvx, my + NR * cw + 6, color="#aeb6c0", sw=1.4, dash="4 4"))

    box, bw, bh = textbox(700, my + 42,
                          "накопичення, один прохід згори вниз:\n"
                          "   p0 = z0\n"
                          "   pi = zi ⊕ p(i−1)\n"
                          "s = 1 0 1  →  z = 1 1 0 0\n"
                          "        →  p = 1 0 0 0",
                          size=13, fill="#f6f4ec", stroke=INK, sw=1.6, pad=13)
    p.append(box)

    box2, _, _ = textbox(W / 2, H - 40,
                         "сходовий блок B (діагональ + піддіагональ) → паритет це біжучий XOR:\n"
                         "один прохід замість обернення матриці — лінійна ціна замість квадратної",
                         size=12.5, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, pad=12)
    p.append(box2)

    render(os.path.join(OUT, "staircase.svg"), W, H, *p,
           title="Сходове кодування: паритет одним проходом")


# ── qc-lifting: базова матриця зсувів → велика розріджена H ───────────────────

def fig_qc_lifting():
    W, H = 900, 460
    Z = 4
    base = [[0, -1, 2, -1], [1, 0, -1, 3]]
    BR, BC = 2, 4
    p = []

    # ліворуч: базова матриця (числа-зсуви)
    cw = 44
    mx, my = 58, 156
    p.append(text(mx + BC * cw / 2, my - 26, "базова матриця (зсуви)", size=13, color=INK, bold=True))
    for r in range(BR):
        for c in range(BC):
            v = base[r][c]
            x, y = mx + c * cw, my + r * cw
            empty = (v < 0)
            p.append(rect(x, y, cw, cw, fill=BG if empty else "#eef4ff",
                          stroke="#dfe3e8" if empty else CSTRK, sw=1.0 if empty else 1.8, rx=4))
            p.append(text(x + cw / 2, y + cw / 2 + 5, "−" if empty else str(v), size=15,
                          color=MUTED if empty else CSTRK, bold=not empty))

    # стрілка
    ax = mx + BC * cw + 28
    p.append(arrow(ax, my + BR * cw / 2, ax + 74, my + BR * cw / 2, sw=2.2))
    p.append(text(ax + 37, my + BR * cw / 2 - 14, "підняття", size=12, color=INK, bold=True))
    p.append(text(ax + 37, my + BR * cw / 2 + 24, "Z = 4", size=12, color=INK))

    # праворуч: розгорнута H
    gx, gy, gc = ax + 98, 76, 15
    NR, NC = BR * Z, BC * Z
    p.append(text(gx + NC * gc / 2, gy - 16, "матриця H після підняття", size=13, color=INK, bold=True))
    for r in range(NR):
        for c in range(NC):
            br, bc = r // Z, c // Z
            i, jj = r % Z, c % Z
            v = base[br][bc]
            on = (v >= 0) and (jj == (i + v) % Z)
            x, y = gx + c * gc, gy + r * gc
            p.append(rect(x, y, gc, gc, fill=BG, stroke="#eceef1", sw=0.6, rx=0))
            if on:
                p.append(circle(x + gc / 2, y + gc / 2, 4.2, fill=CSTRK, stroke=CSTRK, sw=1.0))
    for bc in range(BC + 1):
        x = gx + bc * Z * gc
        p.append(line(x, gy, x, gy + NR * gc, color="#aeb6c0", sw=1.3))
    for br in range(BR + 1):
        y = gy + br * Z * gc
        p.append(line(gx, y, gx + NC * gc, y, color="#aeb6c0", sw=1.3))

    box, _, _ = textbox(W / 2, H - 34,
                        "кожне число s → циркулянт Z×Z (одиниці на діагоналі, зсунутій на s)  ·  кожне −1 → порожній блок Z×Z",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "qc-lifting.svg"), W, H, *p,
           title="Квазіциклічне підняття: жменя чисел → велика розріджена H")


# ── irregular-degree: регулярний проти нерегулярного — степінь як важіль ──────

def fig_irregular():
    W, H = 900, 470
    p = []
    p.append(line(W / 2, 52, W / 2, 372, color="#dfe3e8", sw=1.5, dash="5 5"))

    def panel(cx, title, degs, hub, col):
        out = [text(cx, 66, title, size=14, color=col, bold=True)]
        band_y, band_h, bw = 94, 26, 300
        out.append(rect(cx - bw / 2, band_y, bw, band_h, fill="#eef4ff", stroke=CSTRK, sw=1.4, rx=6))
        out.append(text(cx, band_y + band_h / 2 + 4, "вузли-перевірки", size=11.5, color=CSTRK, italic=True))
        n = len(degs)
        x0, x1 = cx - bw / 2 + 26, cx + bw / 2 - 26
        xs = [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]
        by = 250
        for i, (bxc, d) in enumerate(zip(xs, degs)):
            ishub = (i == hub)
            for k in range(d):
                off = (k - (d - 1) / 2) * 7.0
                out.append(line(bxc + off, by - 18, bxc + off, band_y + band_h,
                                color=BADSTRK if ishub else "#9aa2ad", sw=2.0 if ishub else 1.4))
            out.append(circle(bxc, by, 17, fill=BADFILL if ishub else VFILL,
                              stroke=BADSTRK if ishub else VSTRK, sw=2.6 if ishub else 2.0))
            out.append(text(bxc, by + 5, "b%d" % i, size=11, color=BADSTRK if ishub else VSTRK, bold=True))
            out.append(text(bxc, by + 34, "×%d" % d, size=11, color=INK))
        return out

    p.extend(panel(238, "регулярний: усім порівну", [3, 3, 3, 3, 3], -1, VSTRK))
    p.extend(panel(662, "нерегулярний: кілька хабів", [2, 2, 6, 2, 1], 2, BADSTRK))

    b, _, _ = textbox(238, 344, "кожен біт — 3 ребра\n(рівний степінь)", size=12.5, bold=True,
                      fill="#eafaf0", stroke=FIELD, sw=1.6, pad=11)
    p.append(b)
    b2, _, _ = textbox(662, 344, "хаб b2 — 6 ребер: твердне швидко\nй тримає решту як опора", size=12.5,
                       bold=True, fill=BADFILL, stroke=BADSTRK, sw=1.6, pad=11)
    p.append(b2)

    b3, _, _ = textbox(W / 2, H - 42,
                       "λ(x) задає, яка частка ребер веде до бітів кожного степеня;\n"
                       "нерівність степенів родить «опори», яких у регулярному коді немає",
                       size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b3)

    render(os.path.join(OUT, "irregular-degree.svg"), W, H, *p,
           title="Регулярний і нерегулярний код: степінь як важіль")


if __name__ == "__main__":
    fig_tanner()
    fig_decode()
    fig_waterfall()
    fig_incremental()
    fig_fliprule()
    fig_oscillate()
    fig_hist_timeline()
    fig_hist_compute()
    fig_bp_messages()
    fig_boxplus()
    fig_cycle_echo()
    fig_staircase()
    fig_qc_lifting()
    fig_irregular()
    print("OK: figures written to", OUT)
