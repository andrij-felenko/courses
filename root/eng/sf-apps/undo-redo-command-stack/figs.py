# -*- coding: utf-8 -*-
"""Фігури до теми «Скасування й повтор дії: стек команд» (client-architecture)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def panel(x, y, w, h, head):
    """Панель із заголовком угорі; повертає (svg, внутрішній верх)."""
    s = rect(x, y, w, h, fill="#ffffff", stroke="#b8c2cc", sw=1.6, rx=10)
    s += text(x + w / 2, y + 30, head, size=15, bold=True)
    return s, y + 48


# ── 1. Де живе минуле: три способи ─────────────────────────────────────────
def fig_where_past_lives():
    W, H = 1180, 560
    P, PW, PH, PY = [40, 435, 830], 310, 460, 66
    s = ""

    # A — обернена дія
    px = P[0]
    p, top = panel(px, PY, PW, PH, "Обернена дія")
    s += p
    cx = px + PW / 2
    b1, w1, h1 = textbox(cx, top + 55, "стан ДО", size=14, min_w=170)
    b2, w2, h2 = textbox(cx, top + 175, "стан ПІСЛЯ", size=14, min_w=170)
    s += b1 + b2
    s += arrow(cx - 58, top + 82, cx - 58, top + 148, color=POS)
    s += arrow(cx + 58, top + 148, cx + 58, top + 82, color=NEG)
    s += text(cx - 72, top + 118, "дія", size=13, color=POS, anchor="end")
    s += text(cx + 72, top + 118, "відкат", size=13, color=NEG, anchor="start")
    s += mtext(cx, top + 250, [
        "у пам'яті лежить не стан,",
        "а спосіб повернутися назад",
    ], size=13, color=MUTED)
    s += mtext(cx, top + 320, [
        "пам'ять ∝ розмір ЗМІНИ",
        "кожна дія мусить уміти",
        "обернути саму себе",
    ], size=13)

    # B — знімок
    px = P[1]
    p, top = panel(px, PY, PW, PH, "Знімок стану")
    s += p
    cx = px + PW / 2
    for i, lab in enumerate(["стан 1", "стан 2", "стан 3"]):
        bx, _, _ = textbox(cx, top + 40 + i * 62, lab, size=13, min_w=200,
                           fill="#eef3f8")
        s += bx
    s += mtext(cx, top + 250, [
        "у пам'яті лежить повна",
        "копія стану на кожен крок",
    ], size=13, color=MUTED)
    s += mtext(cx, top + 320, [
        "пам'ять ∝ розмір СТАНУ",
        "× число кроків",
        "відновлення миттєве",
    ], size=13)

    # C — версії зі спільною структурою
    px = P[2]
    p, top = panel(px, PY, PW, PH, "Версії зі спільною структурою")
    s += p
    cx = px + PW / 2
    lx, rx_ = cx - 78, cx + 78
    ly = top + 34
    s += circle(lx, ly, 17, fill="#eef3f8", stroke=LINE)
    s += text(lx, ly + 5, "v1", size=12)
    s += circle(rx_, ly, 17, fill="#e8f6ee", stroke=FIELD)
    s += text(rx_, ly + 5, "v2", size=12, color=FIELD)
    # спільна гілка
    sh_x, sh_y = cx - 96, ly + 106
    s += circle(sh_x, sh_y, 17, fill="#eef3f8", stroke=LINE)
    s += text(sh_x, sh_y + 5, "A", size=12)
    old_x = cx + 6
    s += circle(old_x, sh_y, 17, fill="#eef3f8", stroke=LINE)
    s += text(old_x, sh_y + 5, "B", size=12)
    new_x = cx + 106
    s += circle(new_x, sh_y, 17, fill="#e8f6ee", stroke=FIELD)
    s += text(new_x, sh_y + 5, "B′", size=12, color=FIELD)
    s += line(lx, ly + 17, sh_x, sh_y - 17)
    s += line(lx, ly + 17, old_x, sh_y - 17)
    s += line(rx_, ly + 17, sh_x, sh_y - 17, color=FIELD)
    s += line(rx_, ly + 17, new_x, sh_y - 17, color=FIELD)
    s += mtext(cx, top + 200, [
        "нова версія переписує лише",
        "шлях від кореня до зміни;",
        "решту вузлів обидві ділять",
    ], size=13, color=MUTED)
    s += mtext(cx, top + 320, [
        "пам'ять ∝ ГЛИБИНА зміни",
        "старе не руйнується ніколи",
        "відновлення миттєве",
    ], size=13)

    render(os.path.join(OUT, "where-past-lives.svg"), W, H, s,
           title="Три способи зберегти минуле — і чим кожен платить")


# ── 2. Один канал змін ─────────────────────────────────────────────────────
def fig_one_channel():
    W, H = 1180, 500
    s = ""
    PW, PH, PY = 540, 400, 66

    srcs = ["кнопка", "перетяг", "гаряча\nклавіша"]

    # ЛІВОРУЧ — кожен міняє модель сам
    px = 30
    p, top = panel(px, PY, PW, PH, "Кожен міняє модель сам")
    s += p
    sx = px + 90
    model_x = px + 400
    ys = [top + 45, top + 130, top + 220]
    for i, sname in enumerate(srcs):
        b, _, _ = textbox(sx, ys[i], sname, size=13, min_w=120)
        s += b
        s += arrow(sx + 62, ys[i], model_x - 62, top + 130,
                   color=POS if i != 1 else LINE)
    b, _, _ = textbox(model_x, top + 130, "модель", size=14, min_w=120,
                      fill="#eef3f8")
    s += b
    b, _, _ = textbox(model_x, top + 275, "історія", size=14, min_w=120,
                      fill="#fdecea", stroke=POS)
    s += b
    s += line(model_x, top + 165, model_x, top + 248, color=POS, dash="6 5")
    s += mtext(px + PW / 2, top + 330, [
        "історія бачить не всі зміни —",
        "Ctrl+Z відновлює те, чого не було",
    ], size=13, color=POS)

    # ПРАВОРУЧ — один канал
    px = 610
    p, top = panel(px, PY, PW, PH, "Один канал змін")
    s += p
    sx = px + 78
    ch_x = px + 250
    model_x = px + 440
    for i, sname in enumerate(srcs):
        b, _, _ = textbox(sx, ys[i], sname, size=13, min_w=110)
        s += b
        s += arrow(sx + 57, ys[i], ch_x - 52, top + 130)
    b, _, _ = textbox(ch_x, top + 130, "канал\nзмін", size=14, min_w=100,
                      fill="#e8f6ee", stroke=FIELD)
    s += b
    b, _, _ = textbox(model_x, top + 130, "модель", size=14, min_w=110,
                      fill="#eef3f8")
    s += b
    b, _, _ = textbox(ch_x, top + 275, "історія", size=14, min_w=110,
                      fill="#e8f6ee", stroke=FIELD)
    s += b
    s += arrow(ch_x + 52, top + 130, model_x - 57, top + 130)
    s += arrow(ch_x, top + 165, ch_x, top + 248, color=FIELD)
    s += mtext(px + PW / 2, top + 330, [
        "жодна зміна не проходить повз —",
        "тому історія завжди повна",
    ], size=13, color=FIELD)

    render(os.path.join(OUT, "one-channel.svg"), W, H, s,
           title="Скасування вимагає, щоб історія бачила КОЖНУ зміну")


# ── 3. Розкрій стану клієнта ───────────────────────────────────────────────
def fig_state_partition():
    W, H = 1160, 480
    s = ""
    x0, colw, rowh = 40, 560, 106
    y0 = 76
    s += text(x0 + colw / 2, y0 - 14, "частина стану клієнта", size=14, bold=True)
    s += text(x0 + colw + 40 + 240, y0 - 14, "що з нею робить скасування",
              size=14, bold=True)

    rows = [
        ("Документ\nте, що людина створює: текст, фігури, зв'язки",
         "лежить у кроці історії\nі повертається дослівно", "#eef3f8", LINE),
        ("Похідне\nте, що обчислюється: підсумки, індекси, розкладка",
         "в історії НЕ лежить —\nперераховується після відкату", "#e8f6ee", FIELD),
        ("Подання й увага\nкурсор, виділення, прокрутка, фокус",
         "у кроці лежить те, що каже\n«дивись сюди»; решта — ні", "#fdf3e6", "#c07a1e"),
    ]
    for i, (left, right, fill, stroke) in enumerate(rows):
        y = y0 + i * (rowh + 22)
        s += fitbox(x0, y, colw, rowh, left, size=14, fill=fill, stroke=stroke)
        s += arrow(x0 + colw + 8, y + rowh / 2, x0 + colw + 44, y + rowh / 2)
        s += fitbox(x0 + colw + 52, y, 470, rowh, right, size=13,
                    fill="#ffffff", stroke="#b8c2cc")

    render(os.path.join(OUT, "state-partition.svg"), W, H, s,
           title="Не весь стан клієнта відкочується — і це рішення архітектора")


# ── 4. Скасування, коли документ спільний ──────────────────────────────────
def fig_multiplayer_undo():
    W, H = 1180, 530
    s = ""
    # стрічка спільної історії
    lane_y = 78
    ops = [("моя дія 1", NEG), ("чужа дія", POS), ("моя дія 2", NEG)]
    bx = 300
    for i, (lab, col) in enumerate(ops):
        b, _, _ = textbox(bx + i * 230, lane_y, lab, size=13, min_w=180,
                          fill="#f7f9fb", stroke=col)
        s += b
        if i:
            s += arrow(bx + (i - 1) * 230 + 92, lane_y, bx + i * 230 - 92, lane_y)
    s += text(bx - 130, lane_y + 5, "спільний документ:", size=13, bold=True,
              anchor="middle")

    PW, PH, PY = 540, 330, 150
    # ліворуч — один спільний стек
    px = 30
    p, top = panel(px, PY, PW, PH, "Один стек на документ")
    s += p
    s += fitbox(px + 40, top + 20, PW - 80, 62,
                "Ctrl+Z знімає верхівку спільного стека", size=14,
                fill="#ffffff", stroke="#b8c2cc")
    s += fitbox(px + 40, top + 104, PW - 80, 62,
                "а верхівка — «моя дія 2»… доки сусід не додав свою",
                size=13, fill="#ffffff", stroke="#b8c2cc")
    s += mtext(px + PW / 2, top + 208, [
        "мій Ctrl+Z відкочує ЧУЖУ зміну —",
        "людина скасовує те, чого не робила",
    ], size=13, color=POS)

    # праворуч — стек на клієнта
    px = 610
    p, top = panel(px, PY, PW, PH, "Свій стек у кожного клієнта")
    s += p
    s += fitbox(px + 40, top + 20, PW - 80, 62,
                "Ctrl+Z шукає МОЮ останню дію", size=14,
                fill="#ffffff", stroke=FIELD)
    s += fitbox(px + 40, top + 104, PW - 80, 62,
                "її відкат мусить пройти крізь чужі зміни, що лягли пізніше",
                size=13, fill="#ffffff", stroke=FIELD)
    s += mtext(px + PW / 2, top + 208, [
        "відкат переписується під новий стан —",
        "це вже вибіркове скасування, не стопка",
    ], size=13, color=FIELD)

    render(os.path.join(OUT, "multiplayer-undo.svg"), W, H, s,
           title="Коли документ спільний, «останній крок» перестає бути моїм")


# ── Дрібний помічник для кривих ────────────────────────────────────────────
def polyline(pts, color=LINE, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"'
            ' stroke-linejoin="round"%s/>' % (p, color, sw, d))


def swatch(x, y, w, color, sw=4.0):
    return line(x, y, x + w, y, color=color, sw=sw)


# ── 5. Стрічка гібрида: опорні знімки через k кроків ───────────────────────
def fig_checkpoint_timeline():
    W, H = 1180, 430
    s = ""
    ax_y = 205
    x0, x1 = 100, 1080
    marks = 5                       # 0, k, 2k, 3k, 4k
    step = (x1 - x0) / (marks - 1)

    # легенда вгорі
    s += circle(360, 62, 8, fill="#e8f6ee", stroke=FIELD, sw=2.2)
    s += text(376, 67, "повний знімок (S байтів)", size=13, anchor="start")
    s += circle(700, 62, 4.5, fill="#dfe5ec", stroke=MUTED, sw=1.3)
    s += text(714, 67, "обернена дельта (d байтів)", size=13, anchor="start")

    # вісь
    s += line(x0 - 30, ax_y, x1 + 30, ax_y, color="#b8c2cc", sw=2)

    # дельти між опорними точками
    for i in range(marks - 1):
        for j in range(1, 7):
            dx = x0 + i * step + j * step / 7.0
            s += circle(dx, ax_y, 4.5, fill="#dfe5ec", stroke=MUTED, sw=1.3)

    # опорні знімки
    labels = ["0", "k", "2k", "3k", "4k"]
    for i in range(marks):
        mx = x0 + i * step
        s += circle(mx, ax_y, 11, fill="#e8f6ee", stroke=FIELD, sw=2.4)
        s += text(mx, ax_y + 36, labels[i], size=14, bold=True, color=MUTED)

    # ціль відкоту всередині проміжку 2k…3k
    seg_l = x0 + 2 * step
    tgt = seg_l + 0.72 * step
    s += text(tgt, 120, "ціль стрибка j", size=14, bold=True)
    s += arrow(tgt, 132, tgt, ax_y - 16, color=LINE)

    # позначка «поставити знімок»
    s += text(seg_l - 6, 152, "поставити знімок: σ", size=13, color=FIELD,
              anchor="end")
    s += line(seg_l, 160, seg_l, ax_y - 14, color=FIELD, sw=1.4, dash="5 4")

    # дужка «програти вперед»
    br_y = ax_y + 62
    s += line(seg_l, br_y - 12, seg_l, br_y, color=NEG, sw=1.8)
    s += line(tgt, br_y - 12, tgt, br_y, color=NEG, sw=1.8)
    s += line(seg_l, br_y, tgt, br_y, color=NEG, sw=1.8)
    s += text((seg_l + tgt) / 2, br_y + 24,
              "програти вперед ≤ k−1 дельт", size=13, color=NEG)

    # формули внизу
    b, _, _ = textbox(320, 360, "пам'ять    N·d + ⌈N/k⌉·S", size=15,
                      min_w=430, fill="#eef3f8")
    s += b
    b, _, _ = textbox(860, 360, "найгірший час    σ + (k−1)·t", size=15,
                      min_w=430, fill="#eef3f8")
    s += b

    render(os.path.join(OUT, "checkpoint-timeline.svg"), W, H, s,
           title="Гібрид: знімок раз на k кроків — звідки беруться обидві формули")


# ── 6. Ціна гібрида як функція k і її мінімум ──────────────────────────────
def fig_cost_curve():
    import math
    W, H = 1180, 545
    X0, X1, Y0, Y1 = 150, 770, 95, 460
    M_LO, M_HI, V_HI = 0.22, 4.2, 5.0
    s = ""

    def px(m):
        return X0 + (m - M_LO) / (M_HI - M_LO) * (X1 - X0)

    def py(v):
        return Y1 - v / V_HI * (Y1 - Y0)

    # смуга «майже мінімум»
    s += rect(px(0.5), py(2.5), px(2.0) - px(0.5), Y1 - py(2.5),
              fill="#eef3f8", stroke="none", sw=0, rx=4)

    # осі
    s += line(X0, Y0 - 10, X0, Y1, color="#b8c2cc", sw=2)
    s += line(X0, Y1, X1 + 16, Y1, color="#b8c2cc", sw=2)

    # криві
    N_PT = 220
    ms = [M_LO + i * (M_HI - M_LO) / (N_PT - 1) for i in range(N_PT)]
    s += polyline([(px(m), py(1.0 / m)) for m in ms], color=NEG, sw=2.2)
    s += polyline([(px(m), py(m)) for m in ms], color=POS, sw=2.2)
    s += polyline([(px(m), py(m + 1.0 / m)) for m in ms], color=INK, sw=3.0)

    # мінімум
    s += line(px(1.0), Y1, px(1.0), py(2.0), color=MUTED, sw=1.4, dash="5 4")
    s += line(X0, py(2.0), px(1.0), py(2.0), color=MUTED, sw=1.4, dash="5 4")
    s += circle(px(1.0), py(2.0), 6, fill=BG, stroke=INK, sw=2.4)
    s += text(X0 - 12, py(2.0) + 5, "2·√(A·B)", size=13, color=MUTED,
              anchor="end")

    # підписи осі k
    for m, lab in [(0.5, "k*/2"), (1.0, "k*"), (2.0, "2k*"), (3.0, "3k*"),
                   (4.0, "4k*")]:
        s += line(px(m), Y1, px(m), Y1 + 7, color="#b8c2cc", sw=1.6)
        s += text(px(m), Y1 + 26, lab, size=13,
                  bold=(m == 1.0), color=INK if m == 1.0 else MUTED)
    s += text((X0 + X1) / 2, Y1 + 56,
              "k — крок опорного знімка", size=14, color=MUTED)
    s += text(X0 - 12, Y0 - 22, "ціна C(k)", size=14, color=MUTED, anchor="end")

    # легенда праворуч
    lx = 812
    s += swatch(lx, 112, 34, NEG)
    s += text(lx + 46, 117, "пам'ять:  A/k = N·S/k", size=13, anchor="start")
    s += swatch(lx, 146, 34, POS)
    s += text(lx + 46, 151, "час:  B·k = λ·t·k", size=13, anchor="start")
    s += swatch(lx, 180, 34, INK, sw=5)
    s += text(lx + 46, 185, "сума C(k)", size=13, anchor="start", bold=True)

    s += fitbox(lx, 212, 340, 176, "\n".join([
        "C(k) = N·d + N·S/k + λ·(σ + (k−1)·t)",
        "     = const + A/k + B·k",
        "A = N·S,   B = λ·t",
        "C′(k) = −A/k² + B = 0",
        "k* = √(A/B) = √( N·S / (λ·t) )",
        "C(k*) = const + 2·√(A·B)",
    ]), size=14, fill="#ffffff", stroke="#b8c2cc")

    s += fitbox(lx, 402, 340, 86, "\n".join([
        "смуга k*/2 … 2k*:",
        "ціна ≤ 1.25 × мінімум",
        "(відношення = (m + 1/m)/2)",
    ]), size=13, fill="#eef3f8", stroke=MUTED)

    render(os.path.join(OUT, "cost-curve.svg"), W, H, s,
           title="Ціна гібрида: спадна пам'ять проти зростного часу — мінімум у корені")


# ── 7. Зростання пам'яті історії: чотири моделі ────────────────────────────
def fig_memory_growth():
    import math
    W, H = 1180, 560
    X0, X1, Y0, Y1 = 110, 810, 100, 480
    DX = (X1 - X0) / 5.0          # декада N: 10¹ … 10⁶
    DY = (Y1 - Y0) / 9.0          # декада байтів: 10³ … 10¹²
    s = ""

    def px(logn):
        return X0 + (logn - 1.0) * DX

    def py(logm):
        return Y1 - (logm - 3.0) * DY

    # сітка
    for e in range(3, 13):
        y = py(e)
        s += line(X0, y, X1, y, color="#e6eaee", sw=1.2)
    for e in range(1, 7):
        x = px(e)
        s += line(x, Y0, x, Y1, color="#e6eaee", sw=1.2)

    # осі
    s += line(X0, Y0 - 8, X0, Y1, color="#b8c2cc", sw=2)
    s += line(X0, Y1, X1 + 12, Y1, color="#b8c2cc", sw=2)

    for e, lab in [(3, "1 КБ"), (6, "1 МБ"), (9, "1 ГБ"), (12, "1 ТБ")]:
        s += text(X0 - 12, py(e) + 5, lab, size=13, color=MUTED, anchor="end")
    for e, lab in [(1, "10"), (2, "100"), (3, "1 000"), (4, "10⁴"),
                   (5, "10⁵"), (6, "10⁶")]:
        s += line(px(e), Y1, px(e), Y1 + 7, color="#b8c2cc", sw=1.6)
        s += text(px(e), Y1 + 26, lab, size=13, color=MUTED)
    s += text((X0 + X1) / 2, Y1 + 56, "N — кроків історії", size=14, color=MUTED)
    s += text(X0 - 12, Y0 - 26, "пам'ять", size=14, color=MUTED, anchor="end")

    # межа бюджету
    s += line(X0, py(9), X1, py(9), color="#c07a1e", sw=1.8, dash="7 5")
    s += text(X1 - 6, py(9) - 10, "бюджет 1 ГБ", size=13, color="#c07a1e",
              anchor="end")

    models = [
        ("Чисті знімки",       6.4e7,  POS,   "S = 64 МБ на крок",  "16"),
        ("Гібрид, k = 256",    2.508e5, "#c07a1e", "d + S/k ≈ 245 КБ", "4 000"),
        ("Версії, h = 20",     1344.0, FIELD, "(h+1)·w = 1.3 КБ",   "740 000"),
        ("Обернені дельти",    800.0,  NEG,   "d = 800 Б",          "1 250 000"),
    ]

    for name, c, col, _, _ in models:
        lc = math.log10(c)
        n_hi = min(6.0, 12.0 - lc)          # обрізаємо на стелі 10¹² Б
        pts = [(px(1.0), py(1.0 + lc)), (px(n_hi), py(n_hi + lc))]
        s += polyline(pts, color=col, sw=3.0)
        s += circle(px(9.0 - lc), py(9.0), 5.5, fill=BG, stroke=col, sw=2.2)

    # легенда праворуч
    lx, ly, lw, lh = 852, 106, 300, 82
    for i, (name, c, col, per, atgb) in enumerate(models):
        y = ly + i * (lh + 16)
        s += swatch(lx - 26, y + lh / 2, 20, col, sw=4.5)
        s += fitbox(lx, y, lw, lh, "\n".join([
            name, per, "1 ГБ ⇒ " + atgb + " кроків",
        ]), size=13, fill="#ffffff", stroke=col, sw=2.0)

    s += fitbox(lx - 30, 480, lw + 30, 62, "\n".join([
        "документ: n = 10⁶ вузлів по w = 64 Б,",
        "тож повний стан S = 64 МБ",
    ]), size=12, fill="#eef3f8", stroke=MUTED)

    render(os.path.join(OUT, "memory-growth.svg"), W, H, s,
           title="Пам'ять історії росте лінійно в усіх моделях — різняться лише сталі")


# ── 8. Хроніка скасування: ідея → перша реалізація → поширення ─────────────
def fig_undo_timeline():
    W, H = 1240, 830
    s = ""
    AX = 196                      # вісь часу
    Y0, ROW = 108, 116
    BX, BW = 236, 960             # ліва межа й ширина смуги подій

    KIND_COL = {
        "ідея": MUTED,
        "перша реалізація": FIELD,
        "середовище": NEG,
        "масовий редактор": "#c07a1e",
        "записана вимога": POS,
        "багато кроків": "#7d3c98",
    }

    events = [
        ("1966", "ідея",
         "PILOT — Воррен Тейтельман, MIT",
         "вказівка машині подана як порада, а пораду можна відкликати"),
        ("1968–69", "перша реалізація",
         "FRESS — Андріс ван Дам зі студентами, Браунський університет",
         "один крок назад; правка йде в тіньову версію — звідси й автозбереження"),
        ("1970–71", "середовище",
         "Programmer's Assistant у BBN-LISP — В. Тейтельман",
         "історія сесії зберігається як дані; відкотити можна навіть не по порядку"),
        ("1974", "масовий редактор",
         "Bravo — Xerox PARC, перший WYSIWYG-редактор",
         "рівно один крок назад: рятує від описки, не рятує від катастрофи"),
        ("1976", "записана вимога",
         "звіт Ленса Міллера й Джона Томаса, IBM Research",
         "«назад» уперше названо тим, що інтерактивна система МУСИТЬ мати"),
        ("1998", "багато кроків",
         "Photoshop 5.0 — панель історії",
         "минуле стає видимим списком станів, до яких повертаються мишею"),
    ]

    # вісь
    s += line(AX, Y0 - 34, AX, Y0 + (len(events) - 1) * ROW + 44,
              color="#b8c2cc", sw=2.4)

    for i, (year, kind, who, what) in enumerate(events):
        cy = Y0 + i * ROW
        col = KIND_COL[kind]

        s += circle(AX, cy, 11, fill=BG, stroke=col, sw=3.0)
        s += text(AX - 34, cy + 6, year, size=17, bold=True, anchor="end")

        s += rect(BX, cy - 44, BW, 88, fill="#ffffff", stroke="#dfe5ec",
                  sw=1.4, rx=10)
        b, bw, _ = textbox(BX + 22 + 96, cy - 20, kind, size=12, min_w=192,
                           fill="#ffffff", stroke=col, sw=1.8, color=col, rx=12)
        s += b
        s += text(BX + 22, cy + 22, who, size=15, bold=True, anchor="start")
        s += text(BX + 240, cy - 15, what, size=13, color=MUTED, anchor="start")

    # підпис унизу — межа між шарами
    s += text(BX + BW / 2, Y0 + (len(events) - 1) * ROW + 96,
              "далі сперечаються вже не про наявність скасування, "
              "а про його глибину, модель і те, чиє воно",
              size=14, color=MUTED)

    render(os.path.join(OUT, "undo-timeline.svg"), W, H, s,
           title="Тридцять років між «можна передумати» і панеллю історії")


# ── 8b. Два родоводи одного слова: інтерфейс проти відновлення ─────────────
def fig_two_lineages():
    W, H = 1260, 700
    s = ""
    PW, PY, PH = 540, 150, 490
    LX, RX = 40, 680

    b, _, _ = textbox(W / 2, 82, "одне слово — undo / redo", size=16, bold=True,
                      min_w=380, fill="#eef3f8", stroke=LINE, rx=12)
    s += b
    s += arrow(W / 2 - 150, 100, LX + PW / 2, PY - 8, color=MUTED)
    s += arrow(W / 2 + 150, 100, RX + PW / 2, PY - 8, color=MUTED)

    rows_left = [
        ("хто вирішує скасувати", ["людина, свідомо"]),
        ("що скасовують", ["дію, яка ВДАЛАСЯ"]),
        ("одиниця скасування", ["намір людини"]),
        ("коли скасування правильне", ["коли стан збігається з тим,",
                                       "що людина пам'ятає"]),
        ("родовід", ["FRESS 1968 · Bravo 1974 ·",
                     "Міллер і Томас 1976"]),
    ]
    rows_right = [
        ("хто вирішує скасувати", ["ніхто — так вирішив збій"]),
        ("що скасовують", ["транзакцію, яка НЕ дійшла до кінця"]),
        ("одиниця скасування", ["запис журналу"]),
        ("коли скасування правильне", ["коли інваріанти бази",
                                       "знову цілі"]),
        ("родовід", ["журнал попереднього запису ·",
                     "ARIES 1992"]),
    ]

    for px, head, rows, col in ((LX, "Скасування в інтерфейсі", rows_left, NEG),
                                (RX, "Скасування у відновленні бази", rows_right, FIELD)):
        s += rect(px, PY, PW, PH, fill="#ffffff", stroke=col, sw=1.8, rx=12)
        s += text(px + PW / 2, PY + 34, head, size=16, bold=True, color=col)
        s += line(px + 20, PY + 52, px + PW - 20, PY + 52, color="#dfe5ec", sw=1.2)
        for i, (lab, vals) in enumerate(rows):
            ry = PY + 104 + i * 78
            if i:
                s += line(px + 20, ry - 30, px + PW - 20, ry - 30,
                          color="#eceff3", sw=1.0)
            s += text(px + 24, ry, lab, size=12, color=MUTED, anchor="start")
            s += mtext(px + 24, ry + 24, vals, size=13, anchor="start", lh=1.35)

    render(os.path.join(OUT, "two-lineages.svg"), W, H, s,
           title="Два різні скасування, які випадково називають однаково")


# ── Лінія історії: курсор, точка збереження, два кінці ─────────────────────
def fig_history_line():
    W, H = 1240, 620
    s = ""
    ys, cx0, stepx = 250, 212, 136

    for i, lab in enumerate(["s0", "s1", "s2", "s3", "s4", "s5", "s6"]):
        applied = i < 4
        b, _, _ = textbox(cx0 + i * stepx, ys, lab, size=14, min_w=118,
                          fill="#eef3f8" if applied else "#fbfbfc",
                          stroke=LINE if applied else MUTED,
                          color=INK if applied else MUTED)
        s += b

    s += text(cx0 + 1.5 * stepx, 202, "застосовані кроки", size=13, color=MUTED)
    s += text(cx0 + 4.5 * stepx, 202, "гілка повтору", size=13, color=MUTED)

    # курсор index = 4 (межа між s3 і s4)
    bx = cx0 + 3 * stepx + 59 + (stepx - 118) / 2
    s += arrow(bx, 336, bx, 296)
    s += text(bx, 360, "index = 4 — стан, який людина бачить зараз", size=13)
    # зріз проходить рівно по курсору
    s += line(bx, 214, bx, 286, color=POS, sw=2.2, dash="7 5")

    # точка збереження saved = 6 (межа між s5 і s6)
    sx = cx0 + 5 * stepx + 59 + (stepx - 118) / 2
    s += arrow(sx, 190, sx, 228)
    s += mtext(sx, 150, ["saved = 6", "тут документ записали у файл"], size=13)

    # викидання з дна
    s += arrow(cx0 - 59 - 6, ys, 90, ys, color=NEG)
    s += text(120, 292, "з дна", size=12, color=NEG)

    p, top = panel(40, 410, 560, 170, "Випадає з ДНА — вичерпано бюджет")
    s += p
    s += mtext(320, top + 16, [
        "гине корінь «до» найстарішого кроку",
        "звільняється те, що крок ВИЛУЧИВ",
        "saved з'їжджає вниз; пішов під нуль → −1",
    ], size=13, color=NEG)

    p, top = panel(640, 410, 560, 170, "Зрізається ГІЛКА ПОВТОРУ — нова дія")
    s += p
    s += mtext(920, top + 16, [
        "гинуть корені «після» зрізаних кроків",
        "звільняється те, що кроки ДОДАЛИ",
        "saved опинився у зрізаному → −1 назавжди",
    ], size=13, color=POS)

    render(os.path.join(OUT, "history-line.svg"), W, H, s,
           title="Лінія історії: два різні кінці, з яких кроки випадають по-різному")


# ── Транзакція: межа наміру ────────────────────────────────────────────────
def fig_transaction_boundary():
    W, H = 1200, 540
    s = ""
    PW, PH, PY = 550, 400, 66
    cy = 154

    def chain(px, chips, col):
        out = ""
        xs = [px + 80 + i * 130 for i in range(len(chips))]
        for i, (lab, fill, stroke) in enumerate(chips):
            b, _, _ = textbox(xs[i], cy, lab, size=14, min_w=64,
                              fill=fill, stroke=stroke, color=stroke)
            out += b
            if i:
                out += arrow(xs[i - 1] + 36, cy, xs[i] - 36, cy, color=col)
        return out

    # ЛІВОРУЧ — намір дійшов до кінця
    px = 30
    p, top = panel(px, PY, PW, PH, "Намір дійшов до кінця → commit")
    s += p
    s += chain(px, [("r₀", "#eef3f8", LINE), ("r₁", "#eef3f8", LINE),
                    ("r₂", "#eef3f8", LINE), ("r₃", "#e8f6ee", FIELD)], LINE)
    s += mtext(px + 275, 218, [
        "кожна правка одразу видна на екрані:",
        "людина бачить, як фігура їде",
    ], size=13, color=MUTED)
    s += fitbox(px + 40, 268, PW - 80, 86,
                "в історію лягає ОДИН крок:\nbefore = r₀,  after = r₃",
                size=14, fill="#e8f6ee", stroke=FIELD)
    s += mtext(px + 275, 400, [
        "межа кроку — межа наміру,",
        "а не межа зміни моделі",
    ], size=13, color=FIELD)

    # ПРАВОРУЧ — намір урвався
    px = 620
    p, top = panel(px, PY, PW, PH, "Намір урвався → rollback")
    s += p
    s += text(px + 470, 118, "перевірка не пропустила", size=12, color=POS)
    s += chain(px, [("r₀", "#eef3f8", LINE), ("r₁", "#eef3f8", LINE),
                    ("r₂", "#eef3f8", LINE), ("✖", "#fdecea", POS)], LINE)
    s += arrow(px + 470, 188, px + 80, 188, color=POS)
    s += mtext(px + 275, 224, [
        "root = base — одне присвоєння;",
        "усе побудоване стає сміттям",
    ], size=13, color=POS)
    s += fitbox(px + 40, 268, PW - 80, 86,
                "в історію не лягає НІЧОГО:\nнапіврозпочатий крок гірший за його відсутність",
                size=13, fill="#fdecea", stroke=POS)
    s += mtext(px + 275, 400, [
        "у C++ це робить деструктор,",
        "у TypeScript — finally",
    ], size=13, color=MUTED)

    render(os.path.join(OUT, "transaction-boundary.svg"), W, H, s,
           title="Транзакція: у стек лягає лише завершений намір")


if __name__ == "__main__":
    fig_where_past_lives()
    fig_one_channel()
    fig_state_partition()
    fig_multiplayer_undo()
    fig_checkpoint_timeline()
    fig_cost_curve()
    fig_memory_growth()
    fig_undo_timeline()
    fig_two_lineages()
    fig_history_line()
    fig_transaction_boundary()
    print("ok:", os.listdir(OUT))
