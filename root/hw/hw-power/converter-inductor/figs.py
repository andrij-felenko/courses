# -*- coding: utf-8 -*-
"""Фігури для теми converter-inductor (котушка перетворювача) та її math-вставки.
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Усі файли — slug-нейминг, без номерів; вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# теплий приглушений тон для Irms (тепло, але не «пік»-небезпека)
WARM = "#b9770e"
# світлі заливки під рамки
F_NEG = "#eaf0fd"
F_POS = "#fdecea"
F_FIELD = "#eef7f0"
F_WARM = "#fdf3e3"
F_MUT = "#eef0f3"


def _strip(frags, x, y, w, h, s, fill=F_FIELD, stroke=FIELD, size=12, bold=False):
    """Нижня смуга-висновок на всю ширину поля; текст автоматично влазить (fitbox)."""
    frags.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke,
                        color=INK, bold=bold))


# ── 1. datasheet.svg ────────────────────────────────────────────────────────
def fig_datasheet():
    """П'ять чисел даташита: зліва маленька рамка-параметр, стрілка → праворуч
    однорядкове людське значення. Знизу зелена смуга-висновок."""
    W, H = 880, 460
    frags = []

    rows = [
        ("L", "індуктивність",      "задає пульсацію ΔI",                  NEG,  F_NEG),
        ("Isat", "струм насичення", "магнітна межа на ПІК струму",         POS,  F_POS),
        ("Irms", "номінальний RMS", "теплова межа на тривалий струм",      WARM, F_WARM),
        ("DCR", "опір обмотки",     "мідні втрати I²·DCR",                  INK,  FILL),
        ("Pосердя", "втрати в осерді", "змінні втрати ∝ f, ΔI",            MUTED, F_MUT),
    ]

    top = 60
    rh = 64          # крок між рядками
    bx_cx = 150      # центр лівих рамок
    bx_w = 220       # фіксована ширина лівої рамки
    bx_h = 46
    rt_x = 320       # ліва межа правого тексту
    rt_w = W - rt_x - 30

    for i, (sym, sub, meaning, col, fill) in enumerate(rows):
        cy = top + i * rh + bx_h / 2
        # ліва рамка-параметр (символ + підпис), фіксована ширина → fitbox
        frags.append(fitbox(bx_cx - bx_w / 2, cy - bx_h / 2, bx_w, bx_h,
                            "%s\n(%s)" % (sym, sub), size=14,
                            fill=fill, stroke=col, color=col, bold=True))
        # стрілка до правого боку
        frags.append(arrow(bx_cx + bx_w / 2 + 6, cy, rt_x - 8, cy, color=col, sw=1.8))
        # праве значення — однорядкове, у легкій рамці на всю праву ширину
        frags.append(fitbox(rt_x, cy - 19, rt_w, 38, meaning, size=13,
                            fill=BG, stroke=col, color=INK))

    # нижня смуга-висновок
    by = top + len(rows) * rh + 6
    _strip(frags, 30, by, W - 60, 46,
           "L беруть із пульсації, тоді перевіряють ДВІ струмові межі (Isat і Irms) і рахують втрати",
           size=13, bold=True)

    render(os.path.join(OUT, "datasheet.svg"), W, H, *frags,
           title="П'ять чисел даташита котушки")


# ── 2. saturation.svg ───────────────────────────────────────────────────────
def fig_saturation():
    """L(I): плато зліва, коліно й обвал біля Isat. Робоча точка-пік ліворуч від
    Isat із зеленим маркером і запасом 20–30 %."""
    W, H = 820, 470
    L, R = 90, 700
    T, B = 70, 360
    Imax = 10.0          # умовна шкала струму
    Lmax = 1.0           # нормована індуктивність

    def px(i): return L + (i / Imax) * (R - L)
    def py(v): return B - (v / Lmax) * (B - T)

    isat = 7.0           # положення коліна
    ipk = 4.6            # робочий пік (помітно лівіше)

    frags = []
    # осі
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(text((L + R) / 2, B + 40, "струм через котушку, I", size=13, color=INK))
    frags.append(text(L - 60, (T + B) / 2, "індуктивність L", size=13, color=INK))

    # крива L(I): плато → м'яке коліно → стрімкий обвал
    import math
    pts = []
    n = 160
    for k in range(n + 1):
        i = Imax * k / n
        # логістичний спад навколо isat (різке коліно)
        v = 1.0 / (1.0 + math.exp((i - isat) * 2.6))
        v = 0.06 + 0.94 * v        # хвіст не падає в нуль
        pts.append("%.1f,%.1f" % (px(i), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), NEG))

    # вертикаль Isat
    frags.append(line(px(isat), T + 6, px(isat), B, color=POS, sw=1.8, dash="5,4"))
    frags.append(text(px(isat) + 8, T + 22, "Isat", size=13, color=POS, bold=True, anchor="start"))

    # робоча точка-пік
    vpk = 1.0 / (1.0 + math.exp((ipk - isat) * 2.6)); vpk = 0.06 + 0.94 * vpk
    frags.append(circle(px(ipk), py(vpk), 6, fill=FIELD, stroke=FIELD))
    # виноску ведемо ВНИЗ від маркера (зверху бракує місця під плато)
    bcx, bcy = px(ipk) - 4, py(vpk) + 70
    box, bw, bh = textbox(bcx, bcy,
                          ["пік = Iнаван + ΔI/2", "запас 20–30 %"],
                          size=12, fill=F_FIELD, stroke=FIELD, color=INK)
    frags.append(line(px(ipk), py(vpk) + 8, bcx, bcy - bh / 2 - 2, color=FIELD, sw=1.4))
    frags.append(box)

    # анотації плато й урвища
    frags.append(text(px(1.6), py(0.93) + 18, "тут працюємо", size=12, color=NEG, bold=True))
    frags.append(text(px(8.7), py(0.30), "L зникає", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "saturation.svg"), W, H, *frags,
           title="Насичення: індуктивність обвалюється біля Isat")


# ── 3. two-limits.svg ───────────────────────────────────────────────────────
def fig_two_limits():
    """Дві межі за струмом: Isat (магнітна, миттєва, пік) vs Irms (теплова,
    тривала, середнє). Два рядки-картки з контрастом, знизу спільна нота."""
    W, H = 900, 430
    frags = []

    colw = (W - 30 * 3) / 2      # дві колонки з полями
    x1 = 30
    x2 = 30 + colw + 30
    top = 56
    ch = 250

    # ЛІВА панель — Isat
    frags.append(rect(x1, top, colw, ch, fill=F_POS, stroke=POS, sw=2))
    frags.append(text(x1 + colw / 2, top + 30, "Isat — магнітна межа", size=15, color=POS, bold=True))
    frags.append(fitbox(x1 + 18, top + 50, colw - 36, 40,
                        "миттєва: обмежує ПІК", size=14, fill=BG, stroke=POS, color=INK, bold=True))
    frags.append(fitbox(x1 + 18, top + 100, colw - 36, 120,
                        "перевищив на мить →\nосердя насичується,\nL обвалюється,\nструм стрибає",
                        size=13, fill=BG, stroke=POS, color=INK))

    # ПРАВА панель — Irms
    frags.append(rect(x2, top, colw, ch, fill=F_NEG, stroke=NEG, sw=2))
    frags.append(text(x2 + colw / 2, top + 30, "Irms — теплова межа", size=15, color=NEG, bold=True))
    frags.append(fitbox(x2 + 18, top + 50, colw - 36, 40,
                        "тривала: обмежує СЕРЕДНІЙ RMS-струм", size=14, fill=BG, stroke=NEG, color=INK, bold=True))
    frags.append(fitbox(x2 + 18, top + 100, colw - 36, 120,
                        "перевищив надовго →\nперегрів на DCR,\nмідь і осердя гріються,\nдо відмови",
                        size=13, fill=BG, stroke=NEG, color=INK))

    # контраст-вісь посередині
    frags.append(text(W / 2, top + 120, "пік", size=12, color=MUTED, bold=True))
    frags.append(text(W / 2, top + 150, "vs", size=11, color=MUTED, italic=True))
    frags.append(text(W / 2, top + 180, "середнє", size=12, color=MUTED, bold=True))

    # нижня нота
    by = top + ch + 16
    _strip(frags, 30, by, W - 60, 44,
           "обидві мусять виконуватись — їх легко сплутати",
           fill=F_FIELD, stroke=FIELD, size=13, bold=True)

    render(os.path.join(OUT, "two-limits.svg"), W, H, *frags,
           title="Дві межі за струмом: Isat і Irms")


# ── 4. losses.svg ───────────────────────────────────────────────────────────
def fig_losses():
    """Дві сім'ї втрат (мідь ∝ струм, осердя ∝ f,ΔI) → сумарне тепло →
    тепловий опір Rθ → нагрів ΔT → межа Irms."""
    W, H = 880, 470
    frags = []

    # два джерела вгорі
    cu_cx, cu_cy = 220, 90
    co_cx, co_cy = 660, 90
    box, w, h = textbox(cu_cx, cu_cy, ["Мідні втрати", "I²·DCR  (∝ струм)"],
                        size=13, fill=F_POS, stroke=POS, color=INK, bold=True, min_w=240)
    frags.append(box)
    box, w, h = textbox(co_cx, co_cy, ["Втрати в осерді", "(∝ f, ΔI)"],
                        size=13, fill=F_NEG, stroke=NEG, color=INK, bold=True, min_w=240)
    frags.append(box)

    # сумарне тепло
    sum_cx, sum_cy = W / 2, 195
    box, sw_, sh_ = textbox(sum_cx, sum_cy, "сумарне тепло Pвтр",
                            size=14, fill=FILL, stroke=INK, color=INK, bold=True, min_w=260)
    frags.append(box)
    frags.append(arrow(cu_cx, cu_cy + 26, sum_cx - 70, sum_cy - sh_ / 2 - 4, color=POS))
    frags.append(arrow(co_cx, co_cy + 26, sum_cx + 70, sum_cy - sh_ / 2 - 4, color=NEG))

    # тепловий опір
    rt_cx, rt_cy = W / 2, 290
    box, w, h = textbox(rt_cx, rt_cy, "тепловий опір Rθ",
                        size=14, fill=F_FIELD, stroke=FIELD, color=INK, bold=True, min_w=260)
    frags.append(box)
    frags.append(arrow(sum_cx, sum_cy + sh_ / 2 + 2, rt_cx, rt_cy - h / 2 - 2, color=INK))

    # нагрів
    dt_cx, dt_cy = W / 2, 385
    box, w2, h2 = textbox(dt_cx, dt_cy, "нагрів  ΔT = Pвтр·Rθ",
                          size=14, fill=FILL, stroke=INK, color=INK, bold=True, min_w=300)
    frags.append(box)
    frags.append(arrow(rt_cx, rt_cy + h / 2 + 2, dt_cx, dt_cy - h2 / 2 - 2, color=INK))

    # нота → межа Irms
    note_cx = W - 150
    box, w3, h3 = textbox(note_cx, dt_cy, ["визначає", "межу Irms"],
                          size=12, fill=F_WARM, stroke=WARM, color=INK, bold=True, min_w=150)
    frags.append(box)
    frags.append(arrow(dt_cx + w2 / 2 + 4, dt_cy, note_cx - w3 / 2 - 4, dt_cy, color=WARM))

    render(os.path.join(OUT, "losses.svg"), W, H, *frags,
           title="Втрати в котушці: мідь і осердя")


# ── 5. hard-soft.svg ────────────────────────────────────────────────────────
def fig_hard_soft():
    """L(I) з двома кривими: ферит (плато → обрив-урвище) і порошкове залізо
    (нижчий старт → плавний спад). Анотації тверде/м'яке."""
    W, H = 860, 480
    L, R = 90, 720
    T, B = 70, 360
    Imax = 10.0
    Lmax = 1.0

    def px(i): return L + (i / Imax) * (R - L)
    def py(v): return B - (v / Lmax) * (B - T)

    import math
    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(text((L + R) / 2, B + 40, "струм через котушку, I", size=13, color=INK))
    frags.append(text(L - 60, (T + B) / 2, "індуктивність L", size=13, color=INK))

    # ферит: високе плато, різкий обрив біля isat
    isat = 7.2
    fer = []
    n = 160
    for k in range(n + 1):
        i = Imax * k / n
        v = 1.0 / (1.0 + math.exp((i - isat) * 3.0))
        v = 0.05 + 0.93 * v
        fer.append("%.1f,%.1f" % (px(i), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(fer), POS))

    # порошкове залізо: старт нижче, плавний майже лінійний спад
    pwd = []
    for k in range(n + 1):
        i = Imax * k / n
        v = 0.72 - 0.052 * i        # м'який нахил
        v = max(0.10, v)
        pwd.append("%.1f,%.1f" % (px(i), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pwd), FIELD))

    # підписи кривих
    frags.append(text(px(2.0), py(0.99) - 10, "ферит", size=13, color=POS, bold=True))
    frags.append(text(px(2.0), py(0.50) + 4, "порошкове залізо", size=13, color=FIELD, bold=True))

    # анотації у рамках
    box, w, h = textbox(px(8.4), py(0.86),
                        ["тверде:", "різкий обрив,", "потрібен запас"],
                        size=12, fill=F_POS, stroke=POS, color=INK)
    frags.append(box)
    box, w, h = textbox(px(7.8), py(0.30),
                        ["м'яке:", "спадає плавно,", "прощає сплески"],
                        size=12, fill=F_FIELD, stroke=FIELD, color=INK)
    frags.append(box)

    render(os.path.join(OUT, "hard-soft.svg"), W, H, *frags,
           title="Тверде проти м'якого насичення")


# ── 6. pick.svg ─────────────────────────────────────────────────────────────
def fig_pick():
    """Шість кроків наскрізного вибору у дві колонки, з'єднані стрілками.
    Знизу зелена нота."""
    W, H = 900, 470
    frags = []

    steps = [
        ("1", "L із пульсації", NEG),
        ("2", "пік струму\nIнаван + ΔI/2", INK),
        ("3", "Isat (магнітна)", POS),
        ("4", "Irms (теплова)", WARM),
        ("5", "DCR і мідні втрати", INK),
        ("6", "звірка з кривими\nдаташита", FIELD),
    ]

    # дві колонки по три рамки
    col_cx = [240, 660]
    top = 70
    rh = 110
    bw, bh = 280, 76
    pos = []     # (cx, cy) у порядку кроків: ліва колонка згори вниз, потім права
    for i in range(6):
        col = 0 if i < 3 else 1
        row = i % 3
        cx = col_cx[col]
        cy = top + row * rh + bh / 2
        pos.append((cx, cy))

    fills = {NEG: F_NEG, POS: F_POS, WARM: F_WARM, FIELD: F_FIELD, INK: FILL}
    for i, (num, label, col) in enumerate(steps):
        cx, cy = pos[i]
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh,
                            "%s. %s" % (num, label), size=14,
                            fill=fills[col], stroke=col, color=INK, bold=True))

    # стрілки: 1→2→3 (вниз ліва), 3→4 (через низ направо вгору), 4→5→6 (вниз права)
    def below(i): return (pos[i][0], pos[i][1] + bh / 2 + 2)
    def above(i): return (pos[i][0], pos[i][1] - bh / 2 - 2)
    def rightm(i): return (pos[i][0] + bw / 2 + 2, pos[i][1])
    def leftm(i): return (pos[i][0] - bw / 2 - 2, pos[i][1])

    frags.append(arrow(below(0)[0], below(0)[1], above(1)[0], above(1)[1], color=INK))
    frags.append(arrow(below(1)[0], below(1)[1], above(2)[0], above(2)[1], color=INK))
    # 3 (ліва нижня) → 4 (права верхня): горизонтальний місток
    midx = (pos[2][0] + pos[3][0]) / 2
    midy = pos[2][1]
    frags.append(line(rightm(2)[0], rightm(2)[1], midx, midy, color=INK, sw=1.8))
    frags.append(line(midx, midy, midx, pos[3][1], color=INK, sw=1.8))
    frags.append(arrow(midx, pos[3][1], leftm(3)[0], leftm(3)[1], color=INK))
    frags.append(arrow(below(3)[0], below(3)[1], above(4)[0], above(4)[1], color=INK))
    frags.append(arrow(below(4)[0], below(4)[1], above(5)[0], above(5)[1], color=INK))

    by = top + 3 * rh + 10
    _strip(frags, 30, by, W - 60, 44,
           "готова, коли пройдені всі шість",
           fill=F_FIELD, stroke=FIELD, size=13, bold=True)

    render(os.path.join(OUT, "pick.svg"), W, H, *frags,
           title="Наскрізний вибір котушки: шість кроків")


# ── 7. selection-worksheet.svg (math-вставка) ───────────────────────────────
def fig_selection_worksheet():
    """Той самий шестикроковий маршрут, але з конкретними числами прикладу
    buck 5 В → 3.3 В, 2 А. Кожна рамка показує результат обчислення."""
    W, H = 920, 480
    frags = []

    steps = [
        ("1", "D = 3.3/5 = 0.66", NEG),
        ("2", "ΔIціль = 0.35·2 = 0.7 А", INK),
        ("3", "L ≈ 3.2 → беремо 3.3 мкГ\n(реальна ΔI ≈ 0.68 А, 34 %)", NEG),
        ("4", "Iпік = 2 + 0.68/2 ≈ 2.34 А\n→ Isat ≥ 3.0, беремо ≥ 3.3 А", POS),
        ("5", "Irms ≥ 2.5 А", WARM),
        ("6", "DCR ≈ 30 мОм\nPмідь = 2²·0.03 = 0.12 Вт", INK),
    ]

    col_cx = [255, 680]
    top = 66
    rh = 112
    bw, bh = 330, 80
    pos = []
    for i in range(6):
        col = 0 if i < 3 else 1
        row = i % 3
        cx = col_cx[col]
        cy = top + row * rh + bh / 2
        pos.append((cx, cy))

    fills = {NEG: F_NEG, POS: F_POS, WARM: F_WARM, FIELD: F_FIELD, INK: FILL}
    for i, (num, label, col) in enumerate(steps):
        cx, cy = pos[i]
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh,
                            "%s) %s" % (num, label), size=13,
                            fill=fills[col], stroke=col, color=INK, bold=True))

    def below(i): return (pos[i][0], pos[i][1] + bh / 2 + 2)
    def above(i): return (pos[i][0], pos[i][1] - bh / 2 - 2)
    def rightm(i): return (pos[i][0] + bw / 2 + 2, pos[i][1])
    def leftm(i): return (pos[i][0] - bw / 2 - 2, pos[i][1])

    frags.append(arrow(below(0)[0], below(0)[1], above(1)[0], above(1)[1], color=INK))
    frags.append(arrow(below(1)[0], below(1)[1], above(2)[0], above(2)[1], color=INK))
    midx = (pos[2][0] + pos[3][0]) / 2
    midy = pos[2][1]
    frags.append(line(rightm(2)[0], rightm(2)[1], midx, midy, color=INK, sw=1.8))
    frags.append(line(midx, midy, midx, pos[3][1], color=INK, sw=1.8))
    frags.append(arrow(midx, pos[3][1], leftm(3)[0], leftm(3)[1], color=INK))
    frags.append(arrow(below(3)[0], below(3)[1], above(4)[0], above(4)[1], color=INK))
    frags.append(arrow(below(4)[0], below(4)[1], above(5)[0], above(5)[1], color=INK))

    by = top + 3 * rh + 8
    _strip(frags, 30, by, W - 60, 46,
           "Котушка 3.3 мкГ · Isat ≥ 3.3 А · Irms ≥ 2.5 А · DCR ~30 мОм",
           fill=F_FIELD, stroke=FIELD, size=14, bold=True)

    render(os.path.join(OUT, "selection-worksheet.svg"), W, H, *frags,
           title="Розрахунок котушки покроково (buck 5 В → 3.3 В, 2 А)")


if __name__ == "__main__":
    fig_datasheet()
    fig_saturation()
    fig_two_limits()
    fig_losses()
    fig_hard_soft()
    fig_pick()
    fig_selection_worksheet()
    print("ok figs")
