# -*- coding: utf-8 -*-
"""Фігури до теми «Простій ядра процесора: cpuidle і глибина сну»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
GOLD     = "#b8860b"


# ── 1. Сходи глибини сну ─────────────────────────────────────────────────────
def fig_depth_ladder():
    W, H = 1340, 700
    P = []

    NX, NW = 50, 120
    DX, DW = 190, 640
    EX, EW = 862, 170
    RX, RW = 1062, 218

    heads = [(NX, NW, "стан"), (DX, DW, "що вимкнено"),
             (EX, EW, "вихід, мкс"), (RX, RW, "мін. простій, мкс")]
    for x, w, h in heads:
        P.append(text(x + w / 2, 52, h, size=13, bold=True))
    P.append(line(NX, 68, RX + RW, 68, color=MUTED, sw=1))

    rows = [
        ("C0", "усе ввімкнено: конвеєр вибирає інструкції", "—", "—", GREY_BG, MUTED),
        ("C1", "спинено вибирання інструкцій і такт ядра;\nкеші й стан живі",
         "2", "2", WARM_BG, GOLD),
        ("C1E", "плюс знижено частоту й напругу всього пакета",
         "10", "20", WARM_BG, GOLD),
        ("C3", "L1 і L2 скинуто, ядро вийшло з когерентності кешів",
         "70", "100", RED_BG, POS),
        ("C6", "живлення ядра знято, стан збережено в окрему пам'ять",
         "85", "200", RED_BG, POS),
        ("C10", "спільне на пакет: L3 вимкнено, генератор частоти стоїть,\nпам'ять у самооновленні",
         "890", "5000", RED_BG, POS),
    ]

    y, RH = 92, 76
    for name, what, ex, res, bg, st in rows:
        P.append(fitbox(NX, y, NW, RH, name, size=15, bold=True,
                        fill=bg, stroke=st, sw=1.8))
        P.append(fitbox(DX, y, DW, RH, what, size=12.5, fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(EX, y, EW, RH, ex, size=14, fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(RX, y, RW, RH, res, size=14, fill=GREY_BG, stroke=MUTED))
        y += RH + 14

    P.append(text(NX, y + 26,
                  "нижче — більше вимкнено, більша економія й довший шлях назад",
                  size=12.5, color=MUTED, anchor="start"))
    P.append(text(NX, y + 50,
                  "числа — таблиця драйвера intel_idle для Skylake; на іншій моделі ті самі назви означають інше",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "depth-ladder.svg"), W, H, *P,
           title="Сходи глибини сну: що вимкнено і скільки коштує повернення")


# ── 2. Окупність глибокого сну ───────────────────────────────────────────────
def fig_break_even():
    W, H = 1120, 640
    P = []

    X0, Y0 = 150, 500          # початок координат
    XS, YS = 2.0, 0.55         # мкс → px, мкДж → px

    def px(t):
        return X0 + t * XS

    def py(e):
        return Y0 - e * YS

    P.append(arrow(X0, Y0, 1010, Y0, color=MUTED, sw=1.2))
    P.append(arrow(X0, Y0, X0, 120, color=MUTED, sw=1.2))
    P.append(text(X0 - 8, 108, "витрачена енергія, мкДж", size=12.5,
                  color=MUTED, anchor="start"))
    P.append(text(1010, 552, "тривалість простою, мкс", size=12.5,
                  color=MUTED, anchor="end"))

    for t in (0, 100, 200, 300, 400):
        P.append(line(px(t), Y0, px(t), Y0 + 6, color=MUTED, sw=1))
        P.append(text(px(t), Y0 + 24, str(t), size=11.5, color=MUTED))

    P1, P6, ENTRY = 1.4, 0.05, 120.0
    TMAX = 420.0
    TBE = ENTRY / (P1 - P6)

    P.append(line(X0, py(0), px(TMAX), py(P1 * TMAX), color=GOLD, sw=2.4))
    P.append(line(X0, py(ENTRY), px(TMAX), py(ENTRY + P6 * TMAX), color=FIELD, sw=2.4))

    P.append(text(px(TMAX) + 12, py(P1 * TMAX) + 4, "лишитися неглибоко",
                  size=12.5, color=GOLD, anchor="start"))
    P.append(text(px(TMAX) + 12, py(ENTRY + P6 * TMAX) + 4, "піти в глибокий стан",
                  size=12.5, color=FIELD, anchor="start"))

    P.append(line(X0, py(0), X0, py(ENTRY), color=FIELD, sw=2.4, dash="4 4"))
    P.append(fitbox(238, 168, 300, 52,
                    "разова плата за вхід і вихід:\nскид кеша й відновлення стану",
                    size=12.5, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    P.append(arrow(320, 222, X0 + 6, py(ENTRY) - 10, color=FIELD, sw=1.4))

    P.append(line(px(TBE), Y0, px(TBE), py(P1 * TBE) - 6, color=MUTED, sw=1.2, dash="5 5"))
    P.append(circle(px(TBE), py(P1 * TBE), 5, fill=BG, stroke=INK, sw=2))
    P.append(text(px(TBE), 596,
                  "окупність ≈ 89 мкс — це і є мінімальний виправданий простій",
                  size=12.5, color=INK))

    P.append(text(px(TBE / 2), 148, "тут сон збитковий", size=12.5, color=POS))

    render(os.path.join(OUT, "break-even.svg"), W, H, *P,
           title="Коли глибокий сон починає окупатися")


# ── 3. Коло рішення ──────────────────────────────────────────────────────────
def fig_decide_loop():
    W, H = 1320, 660
    P = []

    CX = 640
    steps = [
        (70,  "задача простою: роботи немає", GREY_BG, MUTED),
        (190, "керувальник: cpuidle_select()", WARM_BG, GOLD),
        (320, "драйвер: cpuidle_enter() → mwait 0x20", GREEN_BG, FIELD),
        (450, "переривання будить ядро процесора", RED_BG, POS),
        (570, "облік: cpuidle_reflect()", WARM_BG, GOLD),
    ]
    geom = {}
    for y, label, bg, st in steps:
        body, w, h = textbox(CX, y, label, size=13.5, fill=bg, stroke=st, sw=1.8)
        P.append(body)
        geom[y] = (w, h)

    for (y1, _, _, _), (y2, _, _, _) in zip(steps, steps[1:]):
        P.append(arrow(CX, y1 + geom[y1][1] / 2 + 2, CX, y2 - geom[y2][1] / 2 - 8))

    ins = [(118, "час до найближчого таймера"),
           (190, "вісім останніх простоїв"),
           (262, "межа затримки з /dev/cpu_dma_latency")]
    for y, label in ins:
        body, w, h = textbox(230, y, label, size=12.5, fill=GREY_BG, stroke=MUTED, sw=1.4)
        P.append(body)
        P.append(arrow(230 + w / 2 + 6, y, CX - geom[190][0] / 2 - 10, 190, color=MUTED, sw=1.4))

    body, w, h = textbox(250, 570, "above: простій вийшов закороткий\nbelow: глибший стан підійшов би краще",
                         size=12.5, fill=GREY_BG, stroke=MUTED, sw=1.4)
    P.append(body)
    P.append(arrow(CX - geom[570][0] / 2 - 8, 570, 250 + w / 2 + 8, 570, color=MUTED, sw=1.4))

    RX = 1160
    P.append(line(CX + geom[570][0] / 2 + 8, 570, RX, 570, color=LINE, sw=1.6))
    P.append(line(RX, 570, RX, 190, color=LINE, sw=1.6))
    P.append(arrow(RX, 190, CX + geom[190][0] / 2 + 10, 190, color=LINE, sw=1.6))
    P.append(text(RX - 16, 386, "наступний прохід циклу", size=12.5,
                  color=MUTED, anchor="end"))

    render(os.path.join(OUT, "decide-loop.svg"), W, H, *P,
           title="Ставка робиться до простою, а перевіряється після нього")


# ── 4. Захисна смуга: поріг як функція частки коротких простоїв ──────────────
def fig_guard_band():
    W, H = 1180, 620
    P = []

    X0, X1 = 175, 835
    Y0, YTOP = 520, 130
    YS = 0.2857                      # мкс → px
    TBE, SLOPE = 88.9, 1229.6        # θ*(q) = TBE + SLOPE·q

    def px(q):
        return X0 + q * (X1 - X0)

    def py(t):
        return Y0 - t * YS

    P.append(arrow(X0, Y0, X1 + 40, Y0, color=MUTED, sw=1.2))
    P.append(arrow(X0, Y0, X0, YTOP - 20, color=MUTED, sw=1.2))
    P.append(text(X0 - 32, YTOP - 34,
                  "поріг: скільки простою треба напророчити, мкс",
                  size=12.5, color=MUTED, anchor="start"))
    P.append(text(X1 + 40, Y0 + 52, "частка коротких простоїв q",
                  size=12.5, color=MUTED, anchor="end"))

    for t in (0, 400, 800, 1200):
        P.append(line(X0 - 6, py(t), X0, py(t), color=MUTED, sw=1))
        P.append(text(X0 - 14, py(t) + 4, str(t), size=11.5, color=MUTED, anchor="end"))

    for q, lab in ((0.0, "0"), (0.2, "20 %"), (0.4, "40 %"),
                   (0.6, "60 %"), (0.8, "80 %"), (1.0, "100 %")):
        P.append(line(px(q), Y0, px(q), Y0 + 6, color=MUTED, sw=1))
        P.append(text(px(q), Y0 + 24, lab, size=11.5, color=MUTED))

    # два орієнтири: чиста окупність і число з таблиці драйвера
    P.append(line(X0, py(TBE), X0 + 425, py(TBE), color=FIELD, sw=1.4, dash="5 5"))
    P.append(text(X0 + 437, py(TBE) + 4,
                  "89 мкс — чиста окупність за енергією",
                  size=12.5, color=FIELD, anchor="start"))
    P.append(line(X0, py(200), X0 + 425, py(200), color=GOLD, sw=1.4, dash="5 5"))
    P.append(text(X0 + 437, py(200) + 4,
                  "200 мкс — число з таблиці intel_idle",
                  size=12.5, color=GOLD, anchor="start"))

    # сама пряма порога
    P.append(line(px(0), py(TBE), px(1), py(TBE + SLOPE), color=POS, sw=2.6))
    P.append(text(px(0.62) + 12, py(TBE + SLOPE * 0.62) - 14,
                  "θ*(q) = 89 + 1230·q", size=13, color=POS, anchor="start"))

    P.append(text(px(0.3), YTOP + 24, "вище лінії — глибокий стан окупається",
                  size=12.5, color=MUTED))

    # перетин із 200 мкс
    q200 = (200 - TBE) / SLOPE
    P.append(circle(px(q200), py(200), 5, fill=BG, stroke=INK, sw=2))
    P.append(text(px(q200), Y0 + 44, "9 %", size=12, color=INK))

    # робоча точка q = 0.8
    P.append(circle(px(0.8), py(TBE + SLOPE * 0.8), 6, fill=BG, stroke=POS, sw=2.4))
    body, bw, bh = textbox(px(0.68), py(260),
                           "80 % коротких простоїв —\nі пірнати варто лише від 1073 мкс",
                           size=12.5, fill=RED_BG, stroke=POS, sw=1.6)
    P.append(body)
    P.append(arrow(px(0.68), py(260) - bh / 2 - 6,
                   px(0.8) - 4, py(TBE + SLOPE * 0.8) + 12, color=POS, sw=1.4))

    render(os.path.join(OUT, "guard-band.svg"), W, H, *P,
           title="Ціна затримки може лише підняти поріг, ніколи не опустити")


# ── 5. Перевірка правила «2–3 часи виходу» ───────────────────────────────────
def fig_residency_ratio():
    W, H = 1190, 600
    P = []

    NX, NW = 50, 76
    EX, EW = 140, 118
    RX, RW = 270, 150
    X0, U = 452, 60                  # початок шкали відношень і піксель на одиницю
    X1 = X0 + 11 * U

    heads = [(NX, NW, "стан"), (EX, EW, "вихід, мкс"), (RX, RW, "мін. простій, мкс")]
    for x, w, h in heads:
        P.append(text(x + w / 2, 62, h, size=13, bold=True))
    P.append(text((X0 + X1) / 2, 62, "мін. простій ÷ час виходу", size=13, bold=True))
    P.append(line(NX, 78, X1, 78, color=MUTED, sw=1))

    rows = [
        ("C1",  2,    2, "core"), ("C1E", 10,   20, "core"),
        ("C3",  70,  100, "core"), ("C6",  85,  200, "core"),
        ("C7s", 124, 800, "pkg"),  ("C8",  200, 800, "pkg"),
        ("C9",  480, 5000, "pkg"), ("C10", 890, 5000, "pkg"),
    ]

    Y, RH, GAP = 96, 40, 8
    ybot = Y + len(rows) * (RH + GAP) - GAP

    for r in (2, 3):
        P.append(line(X0 + r * U, 88, X0 + r * U, ybot + 6,
                      color=MUTED, sw=1.2, dash="5 5"))

    for i, (name, ex, res, grp) in enumerate(rows):
        y = Y + i * (RH + GAP)
        cy = y + RH / 2
        bg = GREEN_BG if grp == "core" else WARM_BG
        st = FIELD if grp == "core" else GOLD
        P.append(fitbox(NX, y, NW, RH, name, size=14, bold=True, fill=bg, stroke=st, sw=1.8))
        P.append(fitbox(EX, y, EW, RH, str(ex), size=13.5, fill=GREY_BG, stroke=MUTED))
        P.append(fitbox(RX, y, RW, RH, str(res), size=13.5, fill=GREY_BG, stroke=MUTED))
        k = res / float(ex)
        P.append(line(X0, cy, X0 + k * U, cy, color=st, sw=2.2))
        P.append(circle(X0 + k * U, cy, 6.5, fill=BG, stroke=st, sw=2.4))
        P.append(text(X1 + 22, cy + 5, "×%.2f" % k, size=13, color=st, anchor="start"))

    P.append(line(X0, ybot + 22, X1, ybot + 22, color=MUTED, sw=1.2))
    for r in (0, 2, 4, 6, 8, 10):
        P.append(line(X0 + r * U, ybot + 22, X0 + r * U, ybot + 28, color=MUTED, sw=1))
        P.append(text(X0 + r * U, ybot + 46, str(r), size=11.5, color=MUTED))

    body, bw, bh = textbox(150, ybot + 40, "стани ядра", size=12.5,
                           fill=GREEN_BG, stroke=FIELD, sw=1.4)
    P.append(body)
    body, bw, bh = textbox(330, ybot + 40, "стани пакета", size=12.5,
                           fill=WARM_BG, stroke=GOLD, sw=1.4)
    P.append(body)

    P.append(text(NX, ybot + 82,
                  "у смугу «2–3×» потрапляють лише два рядки з восьми; "
                  "800 і 5000 повторюються двічі при різних часах виходу",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "residency-ratio.svg"), W, H, *P,
           title="Таблиця Skylake проти правила «мінімальний простій ≈ 2–3 часи виходу»")


if __name__ == "__main__":
    fig_depth_ladder()
    fig_break_even()
    fig_decide_loop()
    fig_guard_band()
    fig_residency_ratio()
    print("ok")
