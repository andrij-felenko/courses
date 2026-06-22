# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори стадій (узгоджені з палітрою svgkit): вибірка — гаряча, виконання — поле,
# декодування — нейтральне, пам'ять/запис — холодні відтінки.
C_FETCH = "#fdecea"; S_FETCH = POS          # Виб
C_DEC   = "#eef1f4"; S_DEC   = MUTED        # Дек
C_EXE   = "#eaf6ef"; S_EXE   = FIELD        # Вик
C_MEM   = "#eaf0fd"; S_MEM   = NEG          # Пам
C_WB    = "#f0f0f0"; S_WB    = INK          # Зап
DEAD    = "#fbe9e7"                         # викинута робота


def stage(cx, cy, label, fill, stroke, w=78, h=34):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=5)
            + text(cx, cy + 5, label, size=12, color=stroke, bold=True))


def crossed(cx, cy, w=78, h=34):
    """Викинута стадія: блякла рамка з косим хрестом."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=DEAD, stroke=POS, sw=1.3, rx=5)
    out += line(x + 6, y + 6, x + w - 6, y + h - 6, color=POS, sw=1.5)
    out += line(x + w - 6, y + 6, x + 6, y + h - 6, color=POS, sw=1.5)
    return out


# ── 1. idle: команди по черзі, працює лише один блок ─────────────────────────
def fig_idle():
    W, H = 760, 330
    p = []
    p.append(text(W / 2, 30, "По черзі: у кожен такт працює лише один блок", size=16, bold=True))
    cols0, cw = 150, 62
    rows = [110, 150, 190]                       # три команди, кожна зсунута на 3 такти
    tk_y = 84
    for i in range(9):
        p.append(text(cols0 + i * cw, tk_y, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    seq = [("Виб", C_FETCH, S_FETCH), ("Дек", C_DEC, S_DEC), ("Вик", C_EXE, S_EXE)]
    for r, ry in enumerate(rows):
        p.append(text(cols0 - cw + 4, ry + 4, "ком. %d" % (r + 1), size=11, color=INK, bold=True, anchor="end"))
        for s, (lab, fc, sc) in enumerate(seq):
            cx = cols0 + (r * 3 + s) * cw
            p.append(stage(cx, ry, lab, fc, sc, w=cw - 6, h=30))
    # рамка на такт 4: лише один блок працює
    p.append(rect(cols0 + 3 * cw - cw / 2, 96, cw, 108, fill="none", stroke=MUTED, sw=1.4, rx=5))
    p.append(text(cols0 + 3 * cw, 224, "у т4 зайнятий лише 1 блок,", size=10, color=MUTED))
    p.append(text(cols0 + 3 * cw, 238, "два інші сплять", size=10, color=MUTED))
    p.append(text(W / 2, 280, "Три команди забирають 9 тактів; залізо простоює дві третини часу.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 304, "А якби поки одна виконується, наступну вже декодувати, а ще одну вибирати?",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "idle.svg"), W, H, *p)


# ── 2. overlap: конвеєр — діагональ, усі блоки зайняті ────────────────────────
def fig_overlap():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 30, "Конвеєр: фази перекриваються — усі блоки зайняті щотакту", size=15, bold=True))
    cols0, cw = 150, 64
    rows = [108, 146, 184, 222]
    for i in range(6):
        p.append(text(cols0 + i * cw, 84, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    seq = [("Виб", C_FETCH, S_FETCH), ("Дек", C_DEC, S_DEC), ("Вик", C_EXE, S_EXE)]
    for r, ry in enumerate(rows):
        p.append(text(cols0 - cw + 6, ry + 4, "ком. %d" % (r + 1), size=11, color=INK, bold=True, anchor="end"))
        for s, (lab, fc, sc) in enumerate(seq):
            cx = cols0 + (r + s) * cw            # діагональний зсув на 1 такт
            p.append(stage(cx, ry, lab, fc, sc, w=cw - 6, h=30))
    # стовпчик такту 3: усі три блоки зайняті
    p.append(rect(cols0 + 2 * cw - cw / 2, 92, cw, 148, fill="none", stroke=INK, sw=2, rx=6))
    p.append(text(cols0 + 2 * cw, 258, "такт 3: усі три блоки зайняті", size=10, color=INK, bold=True))
    p.append(text(cols0 + 2 * cw, 272, "(Вик + Дек + Виб)", size=10, color=INK))
    p.append(text(W / 2, 308, "Після розгону нова команда завершується щотакту: 4 команди за 6 тактів замість 12.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 332, "Жоден блок не простоює — кожен обробляє свою команду.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "overlap.svg"), W, H, *p)


# ── 3. laundry: пральня по черзі vs конвеєром ────────────────────────────────
def fig_laundry():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 30, "Аналогія: пральня (прати → сушити → складати)", size=16, bold=True))
    cols0, cw = 90, 96
    seq = [("прати", C_FETCH, S_FETCH), ("сушити", C_DEC, S_DEC), ("складати", C_EXE, S_EXE)]

    # по черзі: 3 партії підряд, 9 інтервалів
    p.append(text(cols0 - 20, 66, "По черзі:", size=12, color=POS, bold=True, anchor="start"))
    y = 84
    for b in range(3):
        for s, (lab, fc, sc) in enumerate(seq):
            cx = cols0 + (b * 3 + s) * (cw - 18)
            p.append(stage(cx, y, lab, fc, sc, w=cw - 24, h=28))
    p.append(text(W / 2, 116, "9 інтервалів — машини більшість часу стоять", size=11, color=POS, bold=True))

    # конвеєром: партії зсунуто на 1 інтервал, 5 інтервалів
    p.append(text(cols0 - 20, 158, "Конвеєром:", size=12, color=FIELD, bold=True, anchor="start"))
    rows = [176, 212, 248]
    for b, ry in enumerate(rows):
        p.append(text(cols0 - 24, ry + 4, "п%d" % (b + 1), size=10, color=INK, bold=True, anchor="end"))
        for s, (lab, fc, sc) in enumerate(seq):
            cx = cols0 + (b + s) * (cw - 18)
            p.append(stage(cx, ry, lab, fc, sc, w=cw - 24, h=28))
    p.append(text(W / 2, 286, "5 інтервалів — бо машини не простоюють", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, 322, "Жодна партія не випралася швидше — але всі три готові скоріше.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 346, "Станції (пралка, сушарка) — це різні блоки процесора. Ламається аналогія там,",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 362, "де партія потребує ту саму машину двічі або залежить від попередньої — як затори.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "laundry.svg"), W, H, *p)


# ── 4. latency vs throughput ─────────────────────────────────────────────────
def fig_latency_throughput():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 30, "Затримка не міняється — пропускна здатність зростає", size=16, bold=True))
    # ліва панель: затримка
    p.append(rect(50, 56, 330, 150, fill="#f6f8fb", stroke=NEG, sw=1.8, rx=10))
    p.append(text(215, 80, "ЗАТРИМКА (час однієї команди)", size=12, color=NEG, bold=True))
    seq = [("Виб", C_FETCH, S_FETCH), ("Дек", C_DEC, S_DEC), ("Вик", C_EXE, S_EXE)]
    for s, (lab, fc, sc) in enumerate(seq):
        p.append(stage(95 + s * 84, 118, lab, fc, sc, w=78, h=30))
    p.append(text(215, 162, "3 такти — конвеєр цього не міняє", size=11, color=NEG, bold=True))
    p.append(text(215, 184, "(кожна команда йде крізь усі фази)", size=10, color=MUTED, italic=True))
    # права панель: пропускна здатність
    p.append(rect(400, 56, 310, 150, fill="#eef7ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(555, 80, "ПРОПУСКНА ЗДАТНІСТЬ", size=12, color=FIELD, bold=True))
    p.append(text(555, 98, "(скільки команд за такт)", size=10, color=MUTED))
    for s in range(4):
        p.append(stage(440 + s * 66, 134, "готова", C_EXE, S_EXE, w=60, h=28))
    p.append(text(555, 178, "одна нова — щотакту", size=11, color=FIELD, bold=True))
    p.append(text(555, 196, "(оце множить конвеєр)", size=10, color=MUTED, italic=True))
    # підсумок
    p.append(rect(50, 228, 660, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 254, "Як завод: конвеєр не складає один автомобіль швидше —",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 274, "він робить так, щоб машини сходили з лінії частіше.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 300, "Так конвеєр доводить CPI до 1, не піднімаючи частоти; N стадій → до ~N× за такт.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "latency-throughput.svg"), W, H, *p)


# ── 5. hazards: дані й розгалуження ──────────────────────────────────────────
def fig_hazards():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 30, "Затори: чому ідеального ×N не буває", size=16, bold=True))
    # ліва панель: залежність даних
    p.append(rect(50, 56, 330, 160, fill="#fef6e9", stroke="#b8860b", sw=1.6, rx=10))
    p.append(text(215, 80, "Залежність даних", size=13, color="#8a6508", bold=True))
    p.append(text(215, 104, "команда 2 чекає результату команди 1", size=10.5, color=INK))
    p.append(text(215, 130, "ДОДАЙ  R3 ← R1+R2", size=11, color=INK, bold=True))
    p.append(text(215, 150, "ВІДНІМИ R4 ← R3−1   (чекає R3)", size=11, color=POS, bold=True))
    p.append(text(215, 180, "бульбашка: конвеєр на такт стає", size=10, color=MUTED, italic=True))
    p.append(text(215, 200, "лікують пробросом результату вперед", size=10, color=FIELD, italic=True))
    # права панель: розгалуження
    p.append(rect(400, 56, 310, 160, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(555, 80, "Розгалуження (стрибок)", size=13, color=POS, bold=True))
    p.append(text(555, 102, "вибрані наперед команди — не ті", size=10.5, color=INK))
    p.append(stage(470, 134, "стриб.", C_FETCH, S_FETCH, w=58, h=28))
    p.append(crossed(534, 134, w=58, h=28))
    p.append(crossed(600, 134, w=58, h=28))
    p.append(text(555, 174, "викид (flush), вибирати заново", size=10, color=MUTED, italic=True))
    p.append(text(555, 196, "лікують передбаченням переходів", size=10, color=FIELD, italic=True))
    # підсумок
    p.append(rect(50, 238, 660, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 264, "Затори спорожнюють конвеєр і крадуть частину виграшу — реально трохи менше за ×N.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 288, "Передбачення вгадує напрям гілки наперед: угадав — летить далі, схибив — викидає.",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 310, "Прості, однакові команди конвеєрити легше — аргумент на користь RISC.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hazards.svg"), W, H, *p)


# ── 6. speedup: ідеал vs реальність ──────────────────────────────────────────
def fig_speedup():
    W, H = 760, 320
    p = []
    p.append(text(W / 2, 30, "Виграш конвеєра — і чому він не безмежний", size=16, bold=True))
    p.append(rect(60, 56, 310, 120, fill="#eef7ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(215, 82, "В ідеалі", size=13, color=FIELD, bold=True))
    p.append(text(215, 108, "N стадій → до ~N× команд за такт", size=11.5, color=INK, bold=True))
    p.append(text(215, 132, "CPI → 1 (команда за такт)", size=11, color=FIELD, bold=True))
    p.append(text(215, 156, "за ту саму частоту", size=10.5, color=MUTED, italic=True))
    p.append(rect(390, 56, 310, 120, fill="#fef6e9", stroke="#b8860b", sw=1.8, rx=10))
    p.append(text(545, 82, "Насправді", size=13, color="#8a6508", bold=True))
    p.append(text(545, 108, "затори крадуть частину виграшу", size=11, color=INK))
    p.append(text(545, 132, "трохи менше за ×N", size=11.5, color=INK, bold=True))
    p.append(text(545, 156, "та все одно велика перемога", size=10.5, color=MUTED, italic=True))
    p.append(rect(60, 196, 640, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 222, "Конвеєр є майже в кожному процесорі: від ESP32 й ARM Cortex до настільних ПК.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 246, "Ось як зменшують CPI, не піднімаючи частоти — перекриваючи фази.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 270, "Конвеєр (один потік швидше) ≠ багатоядерність (різні потоки водночас).",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "speedup.svg"), W, H, *p)


# ── 7. branch-penalty (math insert): 5 стадій, промах викидає 3 такти ─────────
def fig_branch_penalty():
    W, H = 820, 380
    p = []
    p.append(text(W / 2, 30, "Штраф розгалуження: промах спорожнює почату частину конвеєра", size=14.5, bold=True))
    cols0, cw = 150, 66
    for i in range(9):
        p.append(text(cols0 + i * cw, 70, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    five = [("Виб", C_FETCH, S_FETCH), ("Дек", C_DEC, S_DEC), ("Вик", C_EXE, S_EXE),
            ("Пам", C_MEM, S_MEM), ("Зап", C_WB, S_WB)]
    # гілка BNE — повний прохід 5 стадій
    yb = 96
    p.append(text(cols0 - 14, yb + 4, "BNE", size=11, color=INK, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(five):
        p.append(stage(cols0 + s * cw, yb, lab, fc, sc, w=cw - 8, h=28))
    # три команди «по інерції» — викинуті
    for k, ry in enumerate([132, 168, 204]):
        p.append(text(cols0 - 14, ry + 4, "наст.+%d" % (k + 1), size=10, color=POS, bold=True, anchor="end"))
        labs = [("Виб",), ("Дек",), ("Вик",)][:3 - k] if k == 0 else None
        ncols = 3 - k
        for s in range(ncols):
            p.append(crossed(cols0 + (s + 1 + k) * cw, ry, w=cw - 8, h=28))
    # ціль гілки — стартує з т6
    yt = 240
    p.append(text(cols0 - 14, yt + 4, "ціль", size=11, color=NEG, bold=True, anchor="end"))
    for s, (lab, fc, sc) in enumerate(five):
        p.append(stage(cols0 + (s + 5) * cw, yt, lab, fc, sc, w=cw - 8, h=28))
    # лінія «гілка стає відома» на т3 (стадія Вик)
    xk = cols0 + 2 * cw + (cw - 8) / 2
    p.append(line(xk, 84, xk, 262, color=POS, sw=1.5, dash="5 4"))
    p.append(text(xk + 6, 84, "напрям відомий тут", size=10, color=POS, bold=True, anchor="start"))
    # дужка штрафу між т3 і т6
    x1 = cols0 + 2 * cw + cw / 2; x2 = cols0 + 5 * cw - cw / 2
    p.append(line(x1, 286, x2, 286, color=POS, sw=2))
    p.append(text((x1 + x2) / 2, 306, "штраф p = 3 такти (вся почата робота викинута)",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, 344, "Штраф = число тактів від вибірки гілки до такту, коли її напрям відомий.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 366, "Глибший конвеєр — більший штраф; передбачення намагається не платити його зовсім.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "branch-penalty.svg"), W, H, *p)


# ── 8. cpi-curve (math insert): CPI = 1 + f·(1−a)·p ──────────────────────────
def fig_cpi_curve():
    W, H = 760, 470
    p = []
    p.append(text(W / 2, 28, "Ефективний CPI = 1 + f·(1−a)·p   (p = 3)", size=15, bold=True))
    # осі
    ox, oy = 120, 360            # початок (a=0.5 ліворуч, CPI=1 знизу)
    ax_w, ax_h = 520, 270
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))     # вісь CPI
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))     # вісь a
    p.append(text(ox - 8, oy - ax_h - 6, "CPI", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(ox + ax_w, oy + 22, "точність a", size=12, color=INK, bold=True, anchor="end"))

    cpi_lo, cpi_hi = 1.0, 1.9    # вертикальний діапазон
    def Y(cpi): return oy - (cpi - cpi_lo) / (cpi_hi - cpi_lo) * ax_h
    def X(a):   return ox + (a - 0.5) / (1.0 - 0.5) * ax_w        # a у [0.5..1.0]

    # горизонтальні рівні CPI
    for cpi in [1.0, 1.2, 1.4, 1.6, 1.8]:
        p.append(line(ox, Y(cpi), ox + ax_w, Y(cpi), color="#e6e8ea", sw=1))
        p.append(text(ox - 10, Y(cpi) + 4, "%.1f" % cpi, size=10, color=MUTED, anchor="end"))
    # позначки a
    for a in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        p.append(line(X(a), oy, X(a), oy + 5, color=INK, sw=1.3))
        p.append(text(X(a), oy + 20, "%d%%" % int(a * 100), size=10, color=MUTED))
    # ідеал CPI=1
    p.append(line(ox, Y(1.0), ox + ax_w, Y(1.0), color=FIELD, sw=1.4, dash="4 4"))
    p.append(text(ox + ax_w - 4, Y(1.0) - 6, "ідеал CPI = 1", size=10, color=FIELD, bold=True, anchor="end"))

    # криві для f = 0.30, 0.20, 0.10
    def poly(f, col):
        pts = []
        a = 0.5
        while a <= 1.0001:
            cpi = 1 + f * (1 - a) * 3
            pts.append("%.1f,%.1f" % (X(a), Y(min(cpi, cpi_hi))))
            a += 0.025
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                % (" ".join(pts), col))
    p.append(poly(0.30, POS))
    p.append(text(X(0.5) + 6, Y(1 + 0.30 * 0.5 * 3) - 8, "f = 30%", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(poly(0.20, "#b8860b"))
    p.append(text(X(0.5) + 6, Y(1 + 0.20 * 0.5 * 3) - 8, "f = 20%", size=10.5, color="#8a6508", bold=True, anchor="start"))
    p.append(poly(0.10, NEG))
    p.append(text(X(0.5) + 6, Y(1 + 0.10 * 0.5 * 3) - 8, "f = 10%", size=10.5, color=NEG, bold=True, anchor="start"))

    # реалістична точка f=0.2, a=0.9 → CPI 1.06
    rx, ry = X(0.9), Y(1 + 0.2 * 0.1 * 3)
    p.append(circle(rx, ry, 4, fill="#b8860b", stroke=INK, sw=1.3))
    p.append(text(rx - 8, ry - 10, "f=20%, a=90% → CPI ≈ 1.06", size=10, color=INK, bold=True, anchor="end"))

    p.append(text(W / 2, 412, "Дві ручки тримають CPI біля 1: менше гілок (f) і точніше їх угадувати (a).",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 434, "Сучасні передбачувачі дають a ≈ 95–98%, тож надбавка мала; ×N з'їдають саме ці втрати.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "cpi-curve.svg"), W, H, *p)


if __name__ == "__main__":
    fig_idle()
    fig_overlap()
    fig_laundry()
    fig_latency_throughput()
    fig_hazards()
    fig_speedup()
    fig_branch_penalty()
    fig_cpi_curve()
    print("OK: figs written to", OUT)
