# -*- coding: utf-8 -*-
"""Фігури до кроку «Стійкий ланцюжок A→B→C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"   # бурштиновий — «чекає / повільно»
AMBERBG = "#fff8e8"
AMBERST = "#c9a93b"
SPENTBG = "#eef1f4"   # весь дедлайн — тьмяно-сірий
GREENBG = "#eafaf0"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"


# ═════════ Фіг. 1: дедлайн тече крізь ланцюг і скорочується ═════════
def fig_deadline_flow():
    W, H = 1000, 520
    f = []
    x0, span = 150, 684          # 0..1000 мс → x0 .. x0+span

    def X(ms):
        return x0 + span * ms / 1000.0

    def seg(a, b, y, h, fill, stroke, label=None, lcolor=INK, lsize=12, lbold=True):
        x = X(a)
        w = X(b) - X(a)
        g = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=4)
        if label and w > 42:
            g += text(x + w / 2, y + h / 2 + lsize * 0.35, label,
                      size=lsize, color=lcolor, bold=lbold)
        return g

    def rlab(y, h, s, color=INK):
        return text(x0 - 14, y + h / 2 + 5, s, size=13, color=color, anchor="end", bold=True)

    def dl(yT, yB):
        return (line(X(1000), yT, X(1000), yB, color=POS, sw=1.7, dash="4,5") +
                text(X(1000) + 5, yT + 12, "дедлайн 1000 мс", size=11, color=POS,
                     bold=True, anchor="start"))

    hb, gap = 30, 14

    # ── Панель A: здоровий випадок ──
    f.append(text(x0 - 14, 58, "Здоровий випадок — залишок доходить до C",
                  size=15, bold=True, color=FIELD, anchor="start"))
    yin = 78
    f.append(dl(yin - 6, yin + 4 * (hb + gap) - gap + 4))
    f.append(rlab(yin, hb, "вхід"))
    f.append(seg(0, 1000, yin, hb, SPENTBG, MUTED, "весь дедлайн — 1000 мс", INK, 12))
    yA = yin + hb + gap
    f.append(rlab(yA, hb, "A→B"))
    f.append(seg(60, 1000, yA, hb, GREENBG, FIELD, "A з'їв 60 мс → віддає B бюджет 940 мс", INK, 12))
    yB = yA + hb + gap
    f.append(rlab(yB, hb, "B→C"))
    f.append(seg(110, 1000, yB, hb, GREENBG, FIELD, "B з'їв 50 мс → віддає C бюджет 890 мс", INK, 12))
    yC = yB + hb + gap
    f.append(rlab(yC, hb, "C"))
    f.append(seg(110, 310, yC, hb, GREENBG, FIELD, "C: 200 мс", INK, 12))
    f.append(seg(310, 1000, yC, hb, BG, "#d7dde3", "запас 690 мс", MUTED, 11, False))

    # роздільник панелей
    f.append(line(40, 262, W - 40, 262, color="#e5e7eb", sw=1))

    # ── Панель B: B забарився ──
    f.append(text(x0 - 14, 300, "B забарився — C бачить, що часу нема, і не береться",
                  size=15, bold=True, color=POS, anchor="start"))
    yin2 = 320
    f.append(dl(yin2 - 6, yin2 + 4 * (hb + gap) - gap + 4))
    f.append(rlab(yin2, hb, "вхід"))
    f.append(seg(0, 1000, yin2, hb, SPENTBG, MUTED, "весь дедлайн — 1000 мс", INK, 12))
    yA2 = yin2 + hb + gap
    f.append(rlab(yA2, hb, "A→B"))
    f.append(seg(60, 1000, yA2, hb, GREENBG, FIELD, "A віддає B бюджет 940 мс", INK, 12))
    yB2 = yA2 + hb + gap
    f.append(rlab(yB2, hb, "B→C", POS))
    f.append(seg(60, 980, yB2, hb, AMBERBG, AMBERST, "B забарився — з'їв 920 мс", AMBER, 12))
    f.append(seg(980, 1000, yB2, hb, REDBG, POS))     # червоний крихітний залишок
    yC2 = yB2 + hb + gap
    f.append(rlab(yC2, hb, "C", POS))
    f.append(text(x0 + 6, yC2 + hb / 2 + 5,
                  "C потребує 200 мс, а бюджету лишилось 20 мс", size=12.5,
                  color=POS, bold=True, anchor="start"))
    f.append(fitbox(X(1000) + 6, yC2 - 3, 138, hb + 6, "C падає\nодразу", size=12,
                    fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    render(os.path.join(IMG, "deadline-flow.svg"), W, H, *f,
           title="Дедлайн — спільний на весь ланцюг, скорочується всередину")


# ═════════ Фіг. 2: множення повторів (27) проти дисципліни ═════════
def fig_retry_amplification():
    W, H = 1040, 440
    f = []
    f.append(line(540, 60, 540, 388, color="#e5e7eb", sw=1))

    # ── ЛІВА панель: повтор на кожному рівні ──
    f.append(text(285, 62, "Повтор на КОЖНОМУ рівні", size=15, bold=True, color=POS))

    f.append(fitbox(240, 78, 90, 34, "1 клік", size=12, fill=FILL,
                    stroke=INK, color=INK, bold=True))
    rootx, rooty = 285, 112

    # рівень A→B: 3 вузли
    ax = [165, 285, 405]
    ayT, ayB = 140, 170
    for x in ax:
        f.append(line(rootx, rooty, x, ayT, color=POS, sw=1.4))
        f.append(fitbox(x - 34, ayT, 68, 30, "A→B", size=11, fill=REDBG,
                        stroke=POS, color=POS, bold=True))
    f.append(text(505, 157, "×3", size=13, bold=True, color=POS))

    # рівень B→C: 9 вузлів
    bx = [60 + i * (450 / 8.0) for i in range(9)]
    byT, byB = 212, 236
    for i, x in enumerate(bx):
        parent = ax[i // 3]
        f.append(line(parent, ayB, x, byT, color=POS, sw=1.0))
        f.append(rect(x - 17, byT, 34, 24, fill=REDBG, stroke=POS, sw=1.1, rx=3))
    f.append(text(505, 226, "×3", size=13, bold=True, color=POS))

    # рівень C: 27 позначок
    cy = 270
    for i in range(27):
        x = 60 + i * (450 / 26.0)
        parent_b = bx[i // 3]
        f.append(line(parent_b, byB, x, cy, color=POS, sw=0.7))
        f.append(line(x, cy, x, cy + 16, color=POS, sw=2.0))
    f.append(text(505, 276, "×3", size=13, bold=True, color=POS))

    f.append(fitbox(110, 308, 350, 40, "27 викликів падає на C",
                    size=15, fill=REDBG, stroke=POS, color=POS, bold=True, sw=2))
    f.append(text(285, 374, "а C і так уже було важко — тому й мовчав", size=12,
                  color=MUTED, italic=True))

    # ── ПРАВА панель: один рівень + бюджет ──
    f.append(text(790, 62, "Один рівень + бюджет повторів", size=15, bold=True, color=FIELD))
    f.append(fitbox(745, 78, 90, 34, "1 клік", size=12, fill=FILL,
                    stroke=INK, color=INK, bold=True))
    f.append(line(790, 112, 790, 150, color=FIELD, sw=1.6))
    f.append(fitbox(645, 150, 290, 40, "повтор ЛИШЕ на 1 рівні  ·  ×3",
                    size=12, fill=GREENBG, stroke=FIELD, color=INK, bold=True))
    f.append(line(790, 190, 790, 220, color=FIELD, sw=1.6))
    f.append(fitbox(626, 220, 328, 46,
                    "бюджет ≤10% трафіку  ·  запобіжник\nкоротить, коли C падає масово",
                    size=12, fill=GREENBG, stroke=FIELD, color=INK, bold=True))
    f.append(line(790, 266, 790, 302, color=FIELD, sw=1.6))
    f.append(fitbox(650, 308, 280, 40, "≤ кілька викликів на C",
                    size=15, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))
    f.append(text(790, 374, "повтори самі пригасають під навантаженням", size=12,
                  color=MUTED, italic=True))

    # нижній банер
    f.append(fitbox(150, 398, 740, 34,
                    "Спроби на дні  =  ДОБУТОК спроб на кожному рівні",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "retry-amplification.svg"), W, H, *f,
           title="Повтор на кожному стрибку множиться; дисципліна зрізає добуток")


# ═════════ Фіг. 3: порядок обгорток навколо одного виклику ═════════
def fig_guard_onion():
    W, H = 980, 520
    f = []
    cx = 336

    rings = [
        (48,  46, 576, 340, "Повтор — під бюджетом, найзовнішній", POS,   BG),
        (108, 82, 456, 268, "Запобіжник", NEG, BLUEBG),
        (166, 118, 340, 196, "Таймаут", AMBER, AMBERBG),
        (222, 154, 228, 124, "Перебірка", FIELD, GREENBG),
    ]
    lyt = [66, 102, 138, 172]
    for (x, y, w, h, lab, col, fill), ly in zip(rings, lyt):
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.8, rx=12))
        f.append(text(cx, ly, lab, size=13, bold=True, color=col))
    f.append(fitbox(cx - 72, 188, 144, 52, "виклик\nдо C", size=14,
                    fill=INK, stroke=INK, color=BG, bold=True))

    # анотація «розімкнене коло коротить тут»
    f.append(fitbox(654, 92, 300, 76,
                    "Коло розімкнене →\nповтор коротить ТУТ,\nглибше не йдемо",
                    size=13, fill=BLUEBG, stroke=NEG, color=NEG, bold=True, sw=1.8))
    f.append(arrow(654, 118, 566, 108, color=NEG, sw=1.8))

    # чому саме такий порядок — дві короткі причини
    f.append(mtext(804, 214,
                   ["таймаут — ВСЕРЕДИНІ", "запобіжника: зависання", "рахується йому невдачею"],
                   size=12, color=INK))
    f.append(mtext(804, 292,
                   ["повтор — ЗЗОВНІ:", "коло розімкнене →", "спроба падає миттєво"],
                   size=12, color=INK))

    # ── нижня стрічка: та сама цибулина на кожному стрибку ──
    f.append(line(40, 408, W - 40, 408, color="#e5e7eb", sw=1))
    f.append(text(468, 432, "та сама цибулина обгортає виклик на КОЖНОМУ стрибку",
                  size=13, bold=True, color=INK))
    stripY = 476

    def mini_onion(cxm):
        g = ""
        for i, (rr, cc) in enumerate([(26, POS), (20, NEG), (14, AMBER), (8, FIELD)]):
            g += circle(cxm, stripY, rr, fill=(INK if i == 3 else BG), stroke=cc, sw=1.6)
        return g

    for cxm, lab in [(150, "A"), (468, "B"), (786, "C")]:
        f.append(mini_onion(cxm))
        f.append(text(cxm, stripY + 5, lab, size=12, bold=True, color=BG))
    f.append(arrow(190, stripY, 428, stripY, color=INK, sw=2.0))
    f.append(arrow(508, stripY, 746, stripY, color=INK, sw=2.0))

    render(os.path.join(IMG, "guard-onion.svg"), W, H, *f,
           title="Порядок охоронців навколо одного виклику")


# ── помічник: ламана (для графіків вставки-арифметики) ──────────────────────
def _poly(pts, color, sw):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


# ═════════ Вст. math-1: доступність тане що довший ланцюг ════════════════════
def fig_availability_decay():
    W, H = 940, 430
    f = []
    BAR = "#e0655a"
    baseX, ppm = 330, 0.85            # px на хвилину простою
    bh, y0, step = 34, 86, 58
    rows = [(1, "¹", "1 ланка"), (2, "²", "2 ланки"), (3, "³", "3 ланки"),
            (5, "⁵", "5 ланок"), (10, "¹⁰", "10 ланок")]
    for i, (n, sup, lab) in enumerate(rows):
        A = 0.999 ** n
        mins = (1 - A) * 43200
        y = y0 + i * step
        f.append(text(baseX - 16, y + bh / 2 + 5,
                      "%s:  0.999%s ≈ %.4f" % (lab, sup, A),
                      size=13, bold=True, anchor="end"))
        w = max(4, mins * ppm)
        f.append(rect(baseX, y, w, bh, fill=BAR, stroke=POS, sw=1.2, rx=4))
        if mins >= 120:
            note = "~%.0f хв (%.1f год) простою/міс" % (mins, mins / 60.0)
        else:
            note = "~%.0f хв простою/міс" % mins
        f.append(text(baseX + w + 12, y + bh / 2 + 5, note,
                      size=12.5, color=INK, anchor="start"))
    f.append(fitbox(60, y0 + 5 * step - 12, W - 120, 46,
                    "Це — ОПТИМІЗМ: формула припускає НЕЗАЛЕЖНІ відмови. Спільна ланка (БД · мережа · деплой) —\n"
                    "стеля: ланцюг ніколи не буває доступніший за неї, хоч би які надійні решта.",
                    size=13, fill=BLUEBG, stroke=NEG, color=INK, sw=1.5))
    render(os.path.join(IMG, "availability-decay.svg"), W, H, *f,
           title="Що довший синхронний ланцюг — то більше сумарного простою")


# ═════════ Вст. math-2: досить одному стрибку бути повільним ═════════════════
def fig_tail_amplification():
    import math
    W, H = 940, 448
    f = []
    L, R, T, B = 128, 812, 104, 360
    q = 0.01

    def X(n):
        return L + (math.log10(n) / 2.0) * (R - L)        # n: 1..100

    def Y(p):
        return B - (p / 0.70) * (B - T)                    # p: 0..0.70

    f.append(text(W / 2, 50, "кожен стрибок повільний лише 1% часу (це його p99); "
                  "ланцюг повільний, щойно повільний БУДЬ-ХТО", size=13, color=MUTED))
    f.append(text(L, T - 16, "частка повільних запитів", size=12.5, color=MUTED, anchor="start"))
    f.append(line(L, T, L, B, color=INK, sw=1.4))
    f.append(line(L, B, R, B, color=INK, sw=1.4))
    for p in [0.10, 0.30, 0.50]:
        yy = Y(p)
        f.append(line(L, yy, R, yy, color="#eceff2", sw=1))
        f.append(text(L - 10, yy + 4, "%d%%" % round(p * 100), size=12, color=MUTED, anchor="end"))
    f.append(text(L - 10, Y(0) + 4, "0", size=12, color=MUTED, anchor="end"))
    for n in [1, 3, 10, 30, 100]:
        xx = X(n)
        f.append(line(xx, B, xx, B + 5, color=INK, sw=1.2))
        f.append(text(xx, B + 21, str(n), size=12, color=INK))
    f.append(text((L + R) / 2, B + 44, "кількість послідовних стрибків n  (лог-шкала)",
                  size=12.5, color=MUTED))
    ns = [1, 2, 3, 5, 10, 20, 30, 50, 100]
    pts = [(X(n), Y(1 - (1 - q) ** n)) for n in ns]
    f.append(_poly(pts, POS, 2.8))
    for (x, y), n in zip(pts, ns):
        f.append(circle(x, y, 3.6, fill=POS, stroke=POS, sw=1))
    f.append(line(L, Y(0.63), R, Y(0.63), color=NEG, sw=1.3, dash="5,5"))
    f.append(text(L + 6, Y(0.63) - 7, "63%", size=12, color=NEG, bold=True, anchor="start"))
    f.append(fitbox(556, 60, 250, 52,
                    "100 стрибків → 63% повільних:\nобіцяний p99 став p37-м",
                    size=12.5, fill=BLUEBG, stroke=NEG, color=NEG, sw=1.6))
    f.append(line(X(3), Y(0.03), X(3) + 30, 208, color=MUTED, sw=1))
    f.append(mtext(X(3) + 34, 210, ["3 стрибки → ~3%", "(1 із 33, а не 1 із 100)"],
                   size=12, color=INK, anchor="start"))
    render(os.path.join(IMG, "tail-amplification.svg"), W, H, *f,
           title="Досить одному стрибку зі 100 бути повільним — і повільний увесь запит")


# ═════════ Вст. math-3: фіксований лік vs бюджет повторів ════════════════════
def fig_retry_budget():
    W, H = 940, 430
    f = []
    L, R, T, B = 128, 688, 104, 348
    b = 0.10

    def X(fr):
        return L + fr * (R - L)                             # fr: 0..1

    def Y(load):
        return B - (load - 1.0) / 2.0 * (B - T)             # load: 1..3

    f.append(text(W / 2, 50, "праворуч — масова відмова: C уже ледь живий, "
                  "а фіксовані повтори б'ють саме тоді найсильніше", size=13, color=MUTED))
    f.append(text(L, T - 16, "навантаження на C  (× базове)", size=12.5, color=MUTED, anchor="start"))
    f.append(line(L, T, L, B, color=INK, sw=1.4))
    f.append(line(L, B, R, B, color=INK, sw=1.4))
    for load in [1.0, 1.5, 2.0, 2.5, 3.0]:
        yy = Y(load)
        f.append(line(L, yy, R, yy, color="#eceff2", sw=1))
        f.append(text(L - 10, yy + 4, "×%.1f" % load, size=12, color=MUTED, anchor="end"))
    for fr in [0.0, 0.25, 0.5, 0.75, 1.0]:
        xx = X(fr)
        f.append(line(xx, B, xx, B + 5, color=INK, sw=1.2))
        f.append(text(xx, B + 21, "%d%%" % round(fr * 100), size=12, color=INK))
    f.append(text((L + R) / 2, B + 44, "частка викликів, що падають (f)", size=12.5, color=MUTED))
    N = 48
    fixed = [(X(i / N), Y(1 + (i / N) + (i / N) ** 2)) for i in range(N + 1)]
    budg = [(X(i / N), Y(1 + min((i / N) + (i / N) ** 2, b))) for i in range(N + 1)]
    f.append(_poly(fixed, POS, 2.8))
    f.append(_poly(budg, FIELD, 2.8))
    f.append(fitbox(704, 118, 228, 74,
                    "Фіксовані 3 спроби\n→ до ×3  (+200%)\nсаме коли C вже падає",
                    size=12.5, fill=REDBG, stroke=POS, color=POS, sw=1.6))
    f.append(fitbox(704, 232, 228, 74,
                    "Бюджет 10%\n→ ≤ ×1.10  (+10%)\nЗАВЖДИ, хоч би як зле",
                    size=12.5, fill=GREENBG, stroke=FIELD, color=FIELD, sw=1.6))
    render(os.path.join(IMG, "retry-budget.svg"), W, H, *f,
           title="Фіксований лік vs бюджет: зайве навантаження під відмовою")


# ═════════ Вст. hist: родовід прийомів — дві нитки на осі часу ═══════════════
def fig_lineage():
    W, H = 1060, 585
    f = []
    axisY = 300
    xL, xR = 70, 980

    # вісь часу
    f.append(line(xL, axisY, xR, axisY, color=INK, sw=2.2))
    f.append(arrow(xR, axisY, xR + 30, axisY, color=INK, sw=2.2))
    f.append(text(xR + 24, axisY + 22, "час", size=12, color=MUTED, italic=True))

    # легенда двох ниток
    f.append(circle(250, 48, 7, fill=BLUEBG, stroke=NEG, sw=2))
    f.append(text(266, 52, "нитка охоронців — назвати й зібрати", size=12.5,
                  color=INK, anchor="start", bold=True))
    f.append(circle(628, 48, 7, fill=REDBG, stroke=POS, sw=2))
    f.append(text(644, 52, "нитка розплати — повтори можуть убити", size=12.5,
                  color=INK, anchor="start", bold=True))

    cw, ch = 190, 102

    def card(cx, top, accent, title, details):
        g = rect(cx - cw / 2, top, cw, ch, fill=BG, stroke=accent, sw=1.8, rx=9)
        g += text(cx, top + 25, title, size=13.5, color=accent, bold=True)
        g += mtext(cx, top + 48, details, size=11.5, color=INK, lh=1.3)
        return g

    ABOVE_TOP, BELOW_TOP = 74, 336
    milestones = [
        (128, "up",   NEG, "2007 · Release It!",
         ["Найгард дав імена", "Запобіжнику й Перебірці", "(перебірка — з корабля)"]),
        (366, "down", NEG, "2011–12 · Hystrix",
         ["Netflix зібрав докупи:", "запобіжник, перебірка,", "fallback, дашборд (JVM)"]),
        (600, "up",   POS, "2016 · Google SRE",
         ["спроби = добуток рівнів", "4³ = 64; бюджети", "повторів"]),
        (720, "down", NEG, "2018 · resilience4j",
         ["Netflix спинив Hystrix;", "естафета — функційному", "resilience4j"]),
        (858, "up",   POS, "2021 · HotOS",
         ["метастабільні відмови", "(Бронсон та ін.):", "повтори — сталий ефект"]),
        (948, "down", POS, "2022 · OSDI",
         ["розбір аварій наживо:", "22 випадки / 11 компаній,", "повтори > 50% із них"]),
    ]
    for cx, side, accent, title, det in milestones:
        f.append(circle(cx, axisY, 7, fill=accent, stroke=accent, sw=1.5))
        if side == "up":
            top = ABOVE_TOP
            f.append(line(cx, top + ch, cx, axisY - 7, color=accent, sw=1.4, dash="3,4"))
        else:
            top = BELOW_TOP
            f.append(line(cx, axisY + 7, cx, top, color=accent, sw=1.4, dash="3,4"))
        f.append(card(cx, top, accent, title, det))

    f.append(fitbox(150, 552, 760, 26,
                    "дві нитки зійшлися: обгортай кожен стрибок — але тримай повтори на прив'язі",
                    size=12.5, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.4))

    render(os.path.join(IMG, "lineage.svg"), W, H, *f,
           title="Родовід прийомів стійкості: дві нитки, що зійшлися")


# ═════════ Вст. proj-1: що друкує стенд — до і після ════════════════════════
def fig_bench_dashboard():
    W, H = 1020, 412
    f = []
    f.append(text(W / 2, 28, "Що друкує стенд: до і після", size=17, bold=True))

    # легенда
    f.append(rect(150, 46, 15, 15, fill=REDBG, stroke=POS, sw=1.5, rx=3))
    f.append(text(174, 58, "наївно — повтор на кожному рівні", size=12, color=INK, anchor="start"))
    f.append(rect(520, 46, 15, 15, fill=GREENBG, stroke=FIELD, sw=1.5, rx=3))
    f.append(text(544, 58, "дисципліна — 1 рівень + бюджет + запобіжник + дедлайн",
                  size=12, color=INK, anchor="start"))

    f.append(line(510, 84, 510, 248, color="#e5e7eb", sw=1))

    def panel(x0, title, nv, dv, nlbl, dlbl, factor):
        g = []
        g.append(text(x0 + 20, 104, title, size=14, bold=True, color=INK))
        barx, maxw = x0 + 30, 300
        w2 = max(18, maxw * dv / nv)
        g.append(rect(barx, 124, maxw, 32, fill=REDBG, stroke=POS, sw=1.6, rx=5))
        g.append(text(barx + 8, 145, "наївно", size=12, bold=True, color=POS, anchor="start"))
        g.append(text(barx + maxw + 8, 145, nlbl, size=13, bold=True, color=POS, anchor="start"))
        g.append(rect(barx, 172, w2, 32, fill=GREENBG, stroke=FIELD, sw=1.6, rx=5))
        g.append(text(barx + w2 + 8, 193, dlbl, size=13, bold=True, color=FIELD, anchor="start"))
        g.append(text(x0 + 40, 232, factor, size=13, bold=True, color=INK, anchor="start"))
        return "".join(g)

    f.append(panel(20, "Викликів на дно (лічильник C)", 52000, 7300,
                   "≈ 52 000", "≈ 7 300", "≈ ×7 менше"))
    f.append(panel(520, "p99 наскрізної затримки", 8100, 320,
                   "≈ 8 100 мс", "≈ 320 мс", "≈ ×25 менше — і в межах дедлайну 1000 мс"))

    f.append(fitbox(160, 268, 700, 38,
                    "Один «приречений» клік у наївному ланцюзі  =  3·3·3 = 27 ударів по C",
                    size=14, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))
    f.append(mtext(W / 2, 344,
                   ["Числа злегка гуляють від насіння — але порядок саме такий:",
                    "шторм множить виклики й роздуває хвіст, дисципліна кладе обидва додолу"],
                   size=12.5, color=MUTED))

    render(os.path.join(IMG, "bench-dashboard.svg"), W, H, *f)


# ═════════ Вст. proj-2: три стани запобіжника й переходи ════════════════════
def fig_breaker_states():
    W, H = 1040, 476
    f = []
    f.append(text(W / 2, 28, "Запобіжник: три стани й переходи між ними", size=17, bold=True))

    closed, openS, half = (210, 178), (830, 178), (520, 352)
    R = 66
    f.append(circle(*closed, R, fill=GREENBG, stroke=FIELD, sw=2.2))
    f.append(mtext(closed[0], closed[1] - 4, ["ЗАМКНЕНО", "пропускаю"], size=13, bold=True, color=FIELD))
    f.append(circle(*openS, R, fill=REDBG, stroke=POS, sw=2.2))
    f.append(mtext(openS[0], openS[1] - 4, ["РОЗІМКНЕНО", "корочу"], size=13, bold=True, color=POS))
    f.append(circle(*half, R, fill=AMBERBG, stroke=AMBERST, sw=2.2))
    f.append(mtext(half[0], half[1] - 4, ["НАПІВ-", "ВІДКРИТО"], size=13, bold=True, color=AMBER))

    # closed → open
    f.append(arrow(closed[0] + R, 162, openS[0] - R, 162, color=POS, sw=2))
    f.append(text(520, 150, "k невдач поспіль — таймаут теж рахується", size=12, bold=True, color=POS))
    # open → half
    f.append(arrow(785, 232, 575, 302, color=AMBER, sw=2))
    f.append(mtext(700, 250, ["минув кулдаун →", "пропусти ОДНУ пробу"], size=12, bold=True,
                   color=AMBER, anchor="end"))
    # half → closed
    f.append(arrow(462, 305, 252, 235, color=FIELD, sw=2))
    f.append(mtext(250, 250, ["проба вдала →", "знову замкнено"], size=12, bold=True,
                   color=FIELD, anchor="end"))
    # half → open (проба провалилась)
    f.append(arrow(586, 372, 812, 240, color=POS, sw=1.8))
    f.append(text(660, 442, "проба провалилась → знову розімкнено", size=12, bold=True, color=POS))
    # closed self-note
    f.append(text(210, 272, "успіх → лічильник невдач у нуль", size=11, italic=True, color=MUTED))

    f.append(fitbox(388, 52, 264, 70,
                    "Розімкнене коло:\nC не чіпаю, віддаю швидку\nвідмову + «не повторюй»",
                    size=12, fill=BLUEBG, stroke=NEG, color=NEG, bold=True, sw=1.6))

    render(os.path.join(IMG, "breaker-states.svg"), W, H, *f)


if __name__ == "__main__":
    fig_deadline_flow()
    fig_retry_amplification()
    fig_guard_onion()
    fig_availability_decay()
    fig_tail_amplification()
    fig_retry_budget()
    fig_lineage()
    fig_bench_dashboard()
    fig_breaker_states()
    print("OK: deadline-flow, retry-amplification, guard-onion, "
          "availability-decay, tail-amplification, retry-budget, lineage, "
          "bench-dashboard, breaker-states")
