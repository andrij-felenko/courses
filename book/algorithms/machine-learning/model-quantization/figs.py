# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── grid: неперервна вісь float → 256 рівнів цілого; scale = крок, zero-point = де 0 ──
# Ідея: показати саму суть афінного відображення. Зверху суцільна вісь дробових ваг
# з реальним нулем; знизу — 256 рівнів цілого (−128…127). Крок між рівнями = scale;
# ціле, що відповідає справжньому нулю, = zero-point. Одна вага «клацає» вниз до рівня.
def fig_grid():
    W, H = 860, 340
    p = []

    axL, axR = 90, W - 60
    rmin, rmax = -0.6, 1.8          # приклад: діапазон ваг [-0.6, 1.8]
    yF = 96                          # вісь float
    yI = 236                         # вісь int

    def Xr(r):
        return axL + (r - rmin) / (rmax - rmin) * (axR - axL)

    # ── верхня вісь: неперервні дробові ваги ──
    p.append(line(axL, yF, axR, yF, color=INK, sw=2.0))
    p.append(text(axL - 8, yF + 4, "float", size=12, color=NEG, bold=True, anchor="end"))
    for r in (-0.6, 0.0, 0.6, 1.2, 1.8):
        x = Xr(r)
        p.append(line(x, yF - 6, x, yF + 6, color=INK, sw=1.5))
        p.append(text(x, yF - 12, ("%.1f" % r), size=10, color=MUTED))
    # справжній нуль — виділити
    p.append(line(Xr(0.0), yF - 22, Xr(0.0), yF + 22, color=FIELD, sw=1.4, dash="4 3"))
    p.append(text(Xr(0.0), yF + 34, "справжній 0", size=9.5, color=FIELD, bold=True))

    # ── нижня вісь: 256 цілих рівнів (показуємо кожен ~16-й штрихом) ──
    p.append(line(axL, yI, axR, yI, color=INK, sw=2.0))
    p.append(text(axL - 8, yI + 4, "int8", size=12, color=POS, bold=True, anchor="end"))
    # scale і zero-point для [-0.6,1.8] у −128..127:
    s = (rmax - rmin) / 255.0
    z = round(-rmin / s) - 128       # ціле, що лягає на r=0 (тут ≈ −43)
    qs = [-128, -64, 0, 64, 127]
    for q in qs:
        r = s * (q - z)              # де цей рівень стоїть на реальній осі
        x = Xr(max(rmin, min(rmax, r)))
        p.append(line(x, yI - 6, x, yI + 6, color=INK, sw=1.4))
        p.append(text(x, yI + 20, str(q), size=10, color=MUTED))
    # zero-point рівень
    xz = Xr(0.0)
    p.append(line(xz, yI - 22, xz, yI + 6, color=FIELD, sw=1.4, dash="4 3"))
    p.append(text(xz, yI - 28, "zero-point z = %d" % z, size=9.5, color=FIELD, bold=True))

    # ── одна вага «клацає» вниз до найближчого рівня ──
    rw = 0.83
    xw = Xr(rw)
    q = round(rw / s) + z
    rq = s * (q - z)
    xq = Xr(rq)
    p.append(circle(xw, yF, 5, fill=POS, stroke=POS, sw=1))
    p.append(text(xw, yF - 12, "вага 0.83", size=10, color=POS, bold=True))
    p.append(arrow(xw, yF + 8, xq, yI - 8, color=POS, sw=1.8))
    p.append(circle(xq, yI, 5, fill=POS, stroke=POS, sw=1))
    p.append(text(xq + 6, yI - 12, "q = %d" % q, size=10, color=POS, bold=True, anchor="start"))

    # крок = scale
    x0 = Xr(s * (0 - z)); x1 = Xr(s * (1 - z))
    p.append(text((axL + axR) / 2, 300, "крок між сусідніми рівнями = scale s ≈ %.4f" % s,
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "grid.svg"), W, H, *p,
           title="Афінна сітка: дробову вагу клацають у 1 з 256 цілих рівнів")


# ── symasym: симетричне (z=0, для ваг) vs асиметричне (z≠0, для активацій) ──
# Ідея: дві осі. Ліворуч ваги ~симетричні навколо 0 → сітку центруємо, z=0, жодного
# рівня не марнуємо. Праворуч активація після ReLU ≥ 0 (несиметрична) → якби центрували
# в 0, половина рівнів (від'ємні) простоювала б; зсуваємо zero-point → усі 256 в діло.
def fig_symasym():
    W, H = 860, 330
    p = []
    pw = 360
    top = 78
    gapx = 60
    L = 34

    def panel(px, title, sub, lo, hi, z_at_zero, col, note):
        frs = []
        axL, axR = px + 26, px + pw - 16
        yA = top + 78

        def X(r):
            return axL + (r - lo) / (hi - lo) * (axR - axL)

        frs.append(text(px + pw / 2, top - 20, title, size=13, color=col, bold=True))
        frs.append(text(px + pw / 2, top - 4, sub, size=10, color=MUTED))
        # гістограма-«хмара» значень (схематично)
        import math
        for i in range(60):
            t = i / 59.0
            r = lo + (hi - lo) * t
            # щільність: для ваг — дзвін навколо 0; для активації — пік біля 0, хвіст управо
            if z_at_zero:
                d = math.exp(-(r * r) / (2 * ((hi) * 0.4) ** 2))
            else:
                d = math.exp(-((r - hi * 0.18) ** 2) / (2 * (hi * 0.28) ** 2)) if r >= 0 else 0.0
            h = d * 42
            if h > 1:
                frs.append(line(X(r), yA - h, X(r), yA, color=col, sw=2.2))
        # вісь
        frs.append(line(axL, yA, axR, yA, color=INK, sw=1.8))
        # рівні (кілька штрихів)
        for r in [lo, (lo + hi) / 2, hi]:
            frs.append(line(X(r), yA, X(r), yA + 7, color=INK, sw=1.3))
            frs.append(text(X(r), yA + 19, ("%.1f" % r), size=9.5, color=MUTED))
        # zero-point
        xz = X(0.0)
        frs.append(line(xz, yA - 52, xz, yA + 7, color=FIELD, sw=1.5, dash="4 3"))
        zlab = "z = 0 (справжній 0 у центрі)" if z_at_zero else "z ≠ 0 (0 зсунено вбік)"
        frs.append(text(xz if z_at_zero else axL + 4, yA - 58, zlab, size=9.5, color=FIELD,
                        bold=True, anchor="middle" if z_at_zero else "start"))
        frs.append(fitbox(px + 8, yA + 30, pw - 16, 44, note, size=10, fill=FILL,
                          stroke="#c9d2dc", sw=1.1, color=INK))
        return frs

    p += panel(L, "Симетричне (ваги)", "z = 0, діапазон [−m, +m]", -1.0, 1.0, True, NEG,
               "Ваги майже симетричні навколо нуля. Сітку центруємо в 0,\n"
               "фіксуємо z = 0 — множення спрощується, рівні не марнуються.")
    p += panel(L + pw + gapx, "Асиметричне (активації)", "z ≠ 0, діапазон [0, +m]", -0.2, 1.6, False, POS,
               "Після ReLU значення ≥ 0. Центрувати в нулі — марнувати\n"
               "половину рівнів. Зсуваємо zero-point → усі 256 в роботі.")

    render(os.path.join(OUT, "symasym.svg"), W, H, *p,
           title="Симетричне для ваг (z=0) vs асиметричне для активацій (z≠0)")


# ── perchannel: один scale на весь тензор vs свій scale на кожен вихідний канал ──
# Ідея: у згортці різні фільтри (канали) мають дуже різний розмах ваг. Один спільний
# scale підганяється під найгучніший канал і «топить» тихі (їхні ваги майже всі в 0).
# Свій scale на канал — кожен використовує всі 256 рівнів. Ключ до точності на вагах.
def fig_perchannel():
    W, H = 860, 340
    p = []
    chans = [("канал A", 1.0), ("канал B", 0.25), ("канал C", 0.08), ("канал D", 0.5)]
    top = 76
    barw = 150
    gap = 34
    x0 = 40
    axh = 150

    def draw(px, per):
        frs = []
        # спільний scale = під найгучніший канал
        gmax = max(m for _, m in chans)
        for i, (name, m) in enumerate(chans):
            cx = px + i * (barw / len(chans) if False else 0)  # placeholder
        return frs

    # ЛІВО: спільний scale
    def col_block(px, title, per):
        frs = [text(px + (barw) / 2, top - 34, title, size=13,
                    color=(POS if not per else FIELD), bold=True)]
        gmax = max(m for _, m in chans)
        slot = barw / len(chans)
        base = top + axh
        for i, (name, m) in enumerate(chans):
            cx = px + slot * (i + 0.5)
            # діапазон, покритий 256 рівнями:
            span = gmax if not per else m
            # «використана» частка рівнів цим каналом
            used = m / span
            full_h = axh
            # сірий контур = увесь виділений діапазон рівнів
            frs.append(rect(cx - slot * 0.32, base - full_h, slot * 0.64, full_h,
                            fill="#eef1f5", stroke="#c9d2dc", sw=1.1, rx=3))
            # кольорова частина = реально зайняті рівні
            hh = full_h * used
            col = POS if not per else FIELD
            frs.append(rect(cx - slot * 0.32, base - hh, slot * 0.64, hh,
                            fill=col, stroke="none", sw=0, rx=3))
            frs.append(text(cx, base + 16, name, size=9.5, color=MUTED))
            frs.append(text(cx, base - hh - 6, "%d%%" % round(used * 100), size=9.5,
                            color=INK, bold=True))
        frs.append(line(px, base, px + barw, base, color=INK, sw=1.6))
        return frs

    p += col_block(x0, "Один scale на тензор", per=False)
    p += col_block(x0 + barw + 220, "Свій scale на канал", per=True)

    # стрілка-порівняння між блоками
    midy = top + axh / 2
    p.append(arrow(x0 + barw + 30, midy, x0 + barw + 210, midy, color=INK, sw=2.0))
    p.append(text(x0 + barw + 120, midy - 12, "на канал", size=11, color=INK, bold=True))

    p.append(fitbox(x0, top + axh + 44, W - 2 * x0, 44,
                    "Кольором — частка з 256 рівнів, що реально працює. Спільний scale тягнеться до найгучнішого каналу, "
                    "тож тихі канали (B, C) майже нічого не використовують. Власний scale на канал — кожен бере всі рівні.",
                    size=11, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "perchannel.svg"), W, H, *p,
           title="Один scale на весь тензор vs свій scale на кожен канал")


# ── ptq-qat: два шляхи стиснути — після навчання (швидко) чи з навчанням (точніше) ──
# Ідея: PTQ — узяв готову модель, зміряв діапазони на калібрувальних даних, клацнув у
# int8, готово (хвилини, дані не треба перенавчати). QAT — вставив «псевдо-квантування»
# у навчання, мережа сама компенсує округлення (довше, але тримає точність на 4/2 бітах).
def fig_ptq_qat():
    W, H = 880, 350
    p = []
    bw, bh = 150, 46
    yT = 96      # верхня стрічка PTQ
    yB = 236     # нижня стрічка QAT
    x0 = 40
    step = 176

    def chain(y, steps, col, fill):
        frs = []
        prev = None
        for i, lab in enumerate(steps):
            x = x0 + i * step
            frs.append(fitbox(x, y - bh / 2, bw, bh, lab, size=10, fill=fill,
                              stroke=col, sw=1.3, color=INK))
            if prev is not None:
                frs.append(arrow(prev + bw + 2, y, x - 2, y, color=col, sw=1.8))
            prev = x
        return frs

    p.append(text(x0, yT - 44, "PTQ — квантування після навчання", size=13, color=NEG, bold=True, anchor="start"))
    p += chain(yT, [
        "навчена модель\nfloat32",
        "калібрування:\nзміряти діапазони",
        "клацнути ваги\nй активації в int8",
        "готова int8-\nмодель",
    ], NEG, "#eaf0fd")
    p.append(text(x0, yT + bh / 2 + 22, "швидко (хвилини), без перенавчання; трохи втрачає точності", size=10, color=MUTED, anchor="start"))

    p.append(text(x0, yB - 44, "QAT — навчання з урахуванням квантування", size=13, color="#8e44ad", bold=True, anchor="start"))
    p += chain(yB, [
        "навчати з «псевдо-\nквантуванням»",
        "мережа компенсує\nокруглення",
        "клацнути в int8\n(вже пристосовану)",
        "готова int8-\nмодель, точніша",
    ], "#8e44ad", "#f3e8fb")
    p.append(text(x0, yB + bh / 2 + 22, "довше (треба тренувати), але тримає точність навіть на 4 чи 2 бітах", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ptq-qat.svg"), W, H, *p,
           title="Два шляхи: PTQ (після навчання) і QAT (з навчанням)")


# ── round-error: похибка округлення обмежена ±s/2 (пила між рівнями) ──────────
# Ідея математичної вставки: коли неперервне r клацають до найближчого рівня,
# похибка e = r_відн − r ходить пилкою в межах [−s/2, +s/2]. Показуємо саму пилку
# на реальній осі: рівні-вузли, під ними — «клацнуте» r, а різниця — зубець пили.
def fig_round_error():
    W, H = 860, 300
    p = []
    axL, axR = 80, W - 40
    rmin, rmax = 0.0, 1.0
    s = 0.125                        # крок сітки для наочності (8 рівнів на [0,1])
    yE = 150                         # вісь нуля похибки
    amp = 66                         # масштаб зубця (px на s/2)

    def X(r):
        return axL + (r - rmin) / (rmax - rmin) * (axR - axL)

    # смуга ±s/2
    p.append(rect(axL, yE - amp, axR - axL, 2 * amp, fill="#eef7f0", stroke="none", sw=0, rx=4))
    p.append(line(axL, yE - amp, axR, yE - amp, color=FIELD, sw=1.3, dash="5 4"))
    p.append(line(axL, yE + amp, axR, yE + amp, color=FIELD, sw=1.3, dash="5 4"))
    p.append(text(axR + 2, yE - amp + 4, "+s/2", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(axR + 2, yE + amp + 4, "−s/2", size=10, color=FIELD, bold=True, anchor="start"))
    # вісь нульової похибки
    p.append(line(axL, yE, axR, yE, color=INK, sw=1.8))
    p.append(text(axL - 8, yE + 4, "0", size=11, color=MUTED, anchor="end"))
    p.append(text(axL - 8, yE - amp + 4, "похибка", size=10, color=MUTED, anchor="end"))

    # пилка похибки округлення: e(r) = r − s·round(r/s), у межах [−s/2, s/2]
    n = 480
    prev = None
    for i in range(n + 1):
        r = rmin + (rmax - rmin) * i / n
        q = round(r / s)
        e = r - s * q                # у [−s/2, s/2]
        x = X(r)
        y = yE - (e / (s / 2.0)) * amp
        if prev is not None:
            # розрив на переході через середину між рівнями (стрибок пили)
            if abs(y - prev[1]) < amp * 1.3:
                p.append(line(prev[0], prev[1], x, y, color=POS, sw=2.2))
        prev = (x, y)

    # вузли сітки (рівні) на осі
    k = 0
    while k * s <= rmax + 1e-9:
        xr = X(k * s)
        p.append(line(xr, yE - 5, xr, yE + 5, color=INK, sw=1.2))
        p.append(circle(xr, yE, 3.0, fill=NEG, stroke=NEG, sw=1))
        k += 1
    p.append(text((axL + axR) / 2, yE + amp + 34,
                  "вузли сітки (рівні) — тут похибка = 0; найдалі від вузла вона сягає ±s/2",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "round-error.svg"), W, H, *p,
           title="Похибка округлення ходить пилкою в межах ±s/2")


# ── intdot: розклад цілочисельного скалярного добутку на 4 доданки + реквантувач ─
# Ідея: y = sᵥsₓ·Σ(qᵥ−zᵥ)(qₓ−zₓ) розкривається на Σqᵥqₓ (серце, int8×int8→int32)
# мінус два зсуви −zₓΣqᵥ, −zᵥΣqₓ плюс сталу N·zᵥzₓ; наприкінці — один множник M
# (dyadic: ціле M₀ × 2⁻ⁿ) переганяє int32-акумулятор у int8 наступного шару.
def fig_intdot():
    W, H = 880, 430
    p = []
    cx = W / 2
    # верх: серце-сума
    heart_y = 96
    p.append(fitbox(cx - 210, heart_y - 30, 420, 60,
                    "Σ qᵥ·qₓ   — серце: int8 × int8, копичиться в int32-акумулятор",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, color=INK, bold=True))

    # три доданки-корективи (зсуви + стала)
    ty = 214
    col_w = 250
    gap = 24
    total = 3 * col_w + 2 * gap
    x0 = cx - total / 2
    boxes = [
        ("− zₓ · Σ qᵥ", "зсув входу: зняти внесок\nzₓ з суми кодів ваг", POS),
        ("− zᵥ · Σ qₓ", "зсув ваги: зняти внесок\nzᵥ з суми кодів входу", POS),
        ("+ N · zᵥ · zₓ", "стала: N доданків,\nрахується раз наперед", FIELD),
    ]
    for i, (head, sub, col) in enumerate(boxes):
        bx = x0 + i * (col_w + gap)
        p.append(fitbox(bx, ty, col_w, 40, head, size=13, fill=FILL, stroke=col, sw=1.4,
                        color=INK, bold=True))
        p.append(fitbox(bx, ty + 44, col_w, 38, sub, size=9.5, fill=BG, stroke="#d7dde5",
                        sw=1.0, color=MUTED))
        # стрілка від серця вниз до кожного доданка
        p.append(arrow(cx, heart_y + 32, bx + col_w / 2, ty - 4, color=MUTED, sw=1.4))

    # акумулятор int32
    acc_y = 330
    p.append(fitbox(cx - 200, acc_y, 400, 40,
                    "= int32-акумулятор  (сума всіх чотирьох, іще ціла)",
                    size=12, fill="#f1f6ff", stroke=NEG, sw=1.5, color=INK, bold=True))
    for i in range(3):
        bx = x0 + i * (col_w + gap)
        p.append(arrow(bx + col_w / 2, ty + 84, cx, acc_y - 4, color=MUTED, sw=1.3))

    # реквантувач: ×M (dyadic) → int8
    rq_y = 392
    p.append(fitbox(cx - 260, rq_y, 520, 34,
                    "× M = sᵥ·sₓ / s_вих  ≈  M₀ · 2⁻ⁿ   (ціле M₀ + зсув)  →  int8 наступного шару",
                    size=12, fill="#eef7f0", stroke=FIELD, sw=1.6, color=INK, bold=True))
    p.append(arrow(cx, acc_y + 40, cx, rq_y - 4, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "intdot.svg"), W, H, *p,
           title="Цілочисельний скалярний добуток: серце + зсуви + один множник M")


# ── int8-lineage: три нитки, що злилися в галузевий стандарт on-device int8 ──
# Ідея (для вставки hist-int8-jacob): показати, що афінна int8-сітка TFLite —
# збіг трьох окремих ліній. (1) STE: як пускати градієнт крізь недиференційовне
# округлення — Гінтон 2012 (лекція курсу) → Бенжіо-Леонар-Курвіль 2013. (2) Крайнє
# квантування/QAT: BinaryConnect 2015 → BNN/QNN 2016 (Курбар'ю, Бенжіо, Давід та ін.).
# (3) Афінна int8-сітка: doc gemmlowp 2016 → Джейкоб та ін., CVPR 2017 (стаття +
# бібліотека). Усі три зливаються 2017–2018 у TFLite / масовий mobile+edge int8.
def fig_int8_lineage():
    W, H = 900, 430
    p = []
    xL, xR = 84, W - 44
    y1, y2, y3 = 96, 198, 300           # три нитки
    yM = 392                            # злиття

    def X(t):                           # рік t (2011..2018.6) → координата
        return xL + (t - 2011.0) / (2018.6 - 2011.0) * (xR - xL)

    # легкі рейки років унизу
    for yr in (2012, 2014, 2016, 2018):
        p.append(line(X(yr), 62, X(yr), yM - 24, color="#e3e7ec", sw=1.0))
        p.append(text(X(yr), 54, str(yr), size=10, color=MUTED))

    def node(x, y, lab, col, fill, w=158):
        return fitbox(x - w / 2, y - 21, w, 42, lab, size=9.5, fill=fill,
                      stroke=col, sw=1.3, color=INK)

    def head(y, name, col):
        p.append(text(xL - 8, y - 32, name, size=11, color=col, bold=True, anchor="start"))

    # ── нитка 1: STE (як навчати крізь округлення) ──
    head(y1, "Прямий оцінювач градієнта (STE)", NEG)
    n1a, n1b = X(2012.3), X(2013.7)
    p.append(node(n1a, y1, "Гінтон, курс 2012:\n«пропусти градієнт»", NEG, "#eaf0fd"))
    p.append(arrow(n1a + 82, y1, n1b - 82, y1, color=NEG, sw=1.6))
    p.append(node(n1b, y1, "Бенжіо–Леонар–\nКурвіль 2013: STE", NEG, "#eaf0fd"))

    # ── нитка 2: крайнє квантування / QAT ──
    head(y2, "Крайнє квантування (QAT)", "#8e44ad")
    n2a, n2b = X(2015.85), X(2016.6)
    p.append(node(n2a, y2, "BinaryConnect 2015\n(Курбар'ю та ін.)", "#8e44ad", "#f3e8fb"))
    p.append(arrow(n2a + 82, y2, n2b - 82, y2, color="#8e44ad", sw=1.6))
    p.append(node(n2b, y2, "BNN/QNN 2016:\nваги + активації", "#8e44ad", "#f3e8fb"))

    # ── нитка 3: афінна int8-сітка ──
    head(y3, "Афінна int8-сітка (scale + zero-point)", FIELD)
    n3a, n3b = X(2016.45), X(2017.95)
    p.append(node(n3a, y3, "doc gemmlowp 2016:\nсхема вперше", FIELD, "#e7f6ec"))
    p.append(arrow(n3a + 82, y3, n3b - 82, y3, color=FIELD, sw=1.6))
    p.append(node(n3b, y3, "Джейкоб та ін.,\nCVPR 2017 + бібліотека", FIELD, "#e7f6ec"))

    # ── злиття у стандарт ──
    tb, wb, hb = textbox(W / 2, yM,
                         "TFLite: галузевий стандарт on-device int8\n(MobileNet · Snapdragon · Hexagon · масовий edge)",
                         size=11, fill="#fff6e6", stroke="#d98a00", sw=1.6, color=INK, bold=True, pad=12)
    for nx, ny, col in ((n1b, y1, NEG), (n2b, y2, "#8e44ad"), (n3b, y3, FIELD)):
        p.append(arrow(nx, ny + 21, W / 2, yM - hb / 2 - 2, color=col, sw=1.5))
    p.append(tb)

    render(os.path.join(OUT, "int8-lineage.svg"), W, H, *p,
           title="Три нитки, що злилися в галузевий стандарт int8-квантування")


if __name__ == "__main__":
    fig_grid()
    fig_symasym()
    fig_perchannel()
    fig_ptq_qat()
    fig_round_error()
    fig_intdot()
    fig_int8_lineage()
    print("OK: figures written to", OUT)
