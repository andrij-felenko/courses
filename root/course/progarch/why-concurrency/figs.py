# -*- coding: utf-8 -*-
"""Фігури до кроку «Конкурентність ≠ паралелізм».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

A_COL, B_COL, C_COL = NEG, FIELD, POS   # три задачі як категорії кольору


def block(x, y, w, h, color, label=""):
    """Суцільний блок «задача на ядрі» з білим написом, якщо влазить."""
    out = rect(x, y, w, h, fill=color, stroke=color, sw=1, rx=4)
    if label and w > 26:
        out += text(x + w / 2, y + h / 2 + 5, label, size=13, color="#ffffff", bold=True)
    return out


# ───────── Фіг. 1: перемежання (1 ядро) проти водночас (2 ядра) ─────────
def fig_interleave_vs_parallel():
    W, H = 980, 460
    f = []

    # ── ВЕРХ: одне ядро, три задачі перемежаються ──
    f.append(text(510, 60, "ОДНЕ ЯДРО: перемежання = конкурентність",
                  size=16, bold=True, color=INK))

    x0, axisW = 150, 730
    def X(t): return x0 + t / 10.0 * axisW

    rows = [("задача A", 118, A_COL, [(0, 2), (5, 6)]),
            ("задача B", 156, B_COL, [(2, 3.5), (6, 8)]),
            ("задача C", 194, C_COL, [(3.5, 5), (8, 10)])]
    bh = 26
    for name, yc, col, segs in rows:
        # світла доріжка задачі на весь час (прогалини = чекання)
        f.append(rect(X(0), yc - bh / 2, axisW, bh, fill="#eef1f6", stroke="#e2e6ea", sw=1))
        f.append(text(x0 - 16, yc + 5, name, size=13, color=INK, anchor="end"))
        for (t1, t2) in segs:
            f.append(block(X(t1), yc - bh / 2, X(t2) - X(t1), bh, col))

    # вертикаль «одна мить» — перетинає рівно одну зайняту задачу (B на t=2.7)
    xi = X(2.7)
    f.append(line(xi, 100, xi, 210, color=MUTED, sw=1.4, dash="4,5"))
    f.append(text(xi, 94, "будь-яка мить → працює рівно одна", size=11, color=MUTED))
    f.append(text(510, 236,
                  "ядро завжди зайняте — лише міняє власника; за кожну мить біжить одна задача",
                  size=11, color=MUTED))

    # ── НИЗ: два ядра, дві задачі справді водночас ──
    f.append(text(510, 300, "ДВА ЯДРА: справді водночас = паралелізм",
                  size=16, bold=True, color=INK))
    c1y, c2y = 344, 384
    f.append(text(x0 - 16, c1y + 5, "ядро 1", size=13, color=INK, anchor="end"))
    f.append(text(x0 - 16, c2y + 5, "ядро 2", size=13, color=INK, anchor="end"))
    # блоки на весь час; підпис — біля лівого краю, щоб вертикаль-«мить» його не перетинала
    f.append(block(X(0), c1y - bh / 2, axisW, bh, A_COL))
    f.append(text(X(0) + 12, c1y + 5, "задача A біжить увесь час →", size=12,
                  color="#ffffff", bold=True, anchor="start"))
    f.append(block(X(0), c2y - bh / 2, axisW, bh, B_COL))
    f.append(text(X(0) + 12, c2y + 5, "задача B біжить увесь час →", size=12,
                  color="#ffffff", bold=True, anchor="start"))

    xm = X(7.2)
    f.append(line(xm, 326, xm, 402, color=INK, sw=1.5, dash="4,5"))
    f.append(text(xm, 320, "та сама мить → працює двоє", size=11, bold=True, color=INK))
    f.append(text(510, 424,
                  "обидва ядра рахують в один і той самий момент — оце і є «водночас»",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "interleave-vs-parallel.svg"), W, H, *f,
           title="Перемежати на одному ядрі — не те саме, що бігти водночас на двох")


# ───────── Фіг. 2: дві незалежні осі (2×2) ─────────
def fig_two_axes():
    W, H = 940, 566
    f = []

    f.append(text(470, 58,
                  "→ горизонталь — ПАРАЛЕЛІЗМ (виконання): зліва «ні, одне ядро», справа «так, багато ядер»",
                  size=12, color=INK))
    f.append(text(470, 82,
                  "↓ вертикаль — КОНКУРЕНТНІСТЬ (структура): згори «так, незалежні задачі», знизу «ні, одна задача»",
                  size=12, color=INK))

    gx, gy, cw, ch, gap = 95, 108, 360, 200, 20
    col = [gx, gx + cw + gap]
    row = [gy, gy + ch + gap]

    def cell(cx, cy, accent, tint, title, sub, body):
        o = rect(cx, cy, cw, ch, fill=tint, stroke=accent, sw=1.8)
        o += text(cx + cw / 2, cy + 36, title, size=15, bold=True, color=accent)
        o += text(cx + cw / 2, cy + 58, sub, size=11, italic=True, color=MUTED)
        o += mtext(cx + cw / 2, cy + 88, body, size=12.5, color=INK, lh=1.28)
        return o

    f.append(cell(col[0], row[0], FIELD, "#eafaf0",
                  "Конкурентно, НЕ паралельно", "(незалежні задачі · одне ядро)",
                  ["Багато задач перемежаються на", "одному ядрі — заповнюють",
                   "чекання одне одного.", "", "Цикл подій тримає тисячі", "з'єднань на 1 ядрі."]))
    f.append(cell(col[1], row[0], "#0e7d4b", "#e3f7ec",
                  "Конкурентно І паралельно", "(незалежні задачі · багато ядер)",
                  ["Та сама структура лягає на", "кілька ядер — задачі біжать",
                   "водночас.", "", "І структура, і швидкість —", "разом."]))
    f.append(cell(col[0], row[1], MUTED, "#f4f6f8",
                  "Послідовно", "(одна задача · одне ядро)",
                  ["Одна річ за раз.", "", "Простий скрипт, що рахує",
                   "крок за кроком, без жодної", "паралельності й без", "перемежання."]))
    f.append(cell(col[1], row[1], NEG, "#eaf0fd",
                  "Паралельно, але НЕ конкурентно", "(одна задача · багато ядер)",
                  ["Одну задачу ріжуть на", "однакові шматки по ядрах.",
                   "", "Паралельна сума одного", "величезного масиву чисел."]))

    render(os.path.join(IMG, "two-axes.svg"), W, H, *f,
           title="Конкурентність і паралелізм — дві незалежні осі")


# ───────── Фіг. 3: I/O-bound проти CPU-bound — що лікує ─────────
def fig_io_vs_cpu():
    W, H = 980, 470
    f = []

    f.append(line(490, 52, 490, 432, color="#e5e7eb", sw=1.4, dash="4,6"))

    f.append(text(250, 66, "I/O-BOUND — вузьке місце: ЧЕКАННЯ",
                  size=15, bold=True, color=NEG))
    f.append(text(730, 66, "CPU-BOUND — вузьке місце: ЛІЧБА",
                  size=15, bold=True, color=POS))

    # смуги «з чого складається час однієї задачі»
    f.append(text(70, 92, "час однієї задачі:", size=11, color=MUTED, anchor="start"))
    f.append(rect(70, 100, 60, 40, fill=FIELD, stroke=FIELD, sw=1, rx=4))
    f.append(text(100, 124, "лічба", size=10, color="#ffffff", bold=True))
    f.append(rect(130, 100, 300, 40, fill="#eef1f6", stroke="#dfe4ea", sw=1, rx=4))
    f.append(text(280, 124, "чекання (мережа / диск / інша служба)", size=11, color=INK))

    f.append(text(550, 92, "час однієї задачі:", size=11, color=MUTED, anchor="start"))
    f.append(rect(550, 100, 360, 40, fill=POS, stroke=POS, sw=1, rx=4))
    f.append(text(730, 124, "суцільна лічба — ядро не простоює", size=11, color="#ffffff", bold=True))

    # що лікує
    f.append(fitbox(70, 174, 360, 58,
                    "Конкурентність — навіть на 1 ядрі:\nзаповни чекання чужою роботою",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True, sw=1.8))
    f.append(fitbox(70, 244, 360, 52,
                    "Більше ядер — майже дарма:\nвони чекали б так само, лише разом",
                    size=12, fill=FILL, stroke=MUTED, color=INK))

    f.append(fitbox(550, 174, 360, 58,
                    "Паралелізм — реальні ядра\nрахують водночас",
                    size=13, fill="#fdecea", stroke=POS, color=INK, bold=True, sw=1.8))
    f.append(fitbox(550, 244, 360, 52,
                    "Конкурентність сама — 0 виграшу:\nодне ядро лиш ділиться між лічбою",
                    size=12, fill=FILL, stroke=MUTED, color=INK))

    # де це в Digital Homes
    f.append(fitbox(70, 344, 360, 70,
                    "Digital Homes тут:\nопитування 30 пристроїв, віддача\nдашборда, дзвінки в хмару",
                    size=12, fill="#eef2fb", stroke=NEG, color=INK, bold=True))
    f.append(fitbox(550, 344, 360, 70,
                    "Digital Homes тут:\nправила по річній історії,\nаналітика й стиснення логів",
                    size=12, fill="#fdecea", stroke=POS, color=INK, bold=True))

    render(os.path.join(IMG, "io-vs-cpu.svg"), W, H, *f,
           title="Що лікує вузьке місце: конкурентність чи паралелізм")


# ───────── Фіг. 4 (до вставки proj): результати стенда — 3 режими × 2 роботи ─────────
def fig_regimes_results():
    W, H = 1000, 580
    f = []

    y0 = 460            # базова лінія (0 с)
    scale = 145.0       # 1 с = 145 px
    def Y(sec): return y0 - sec * scale

    # легкі горизонтальні орієнтири 1 с і 2 с через обидві панелі
    for sec in (1, 2):
        f.append(line(70, Y(sec), 930, Y(sec), color="#e5e7eb", sw=1.3, dash="4,6"))
        f.append(text(60, Y(sec) + 4, "%d с" % sec, size=12, color=MUTED, anchor="end"))
    f.append(line(70, y0, 930, y0, color=INK, sw=1.4))         # вісь 0
    f.append(line(500, 74, 500, y0, color="#e5e7eb", sw=1.3, dash="3,6"))  # роздільник панелей

    f.append(text(285, 96, "I/O-BOUND · 2 задачі × 1 с чекання", size=15, bold=True, color=NEG))
    f.append(text(715, 96, "CPU-BOUND · 2 задачі × 1 с лічби", size=15, bold=True, color=POS))

    bw = 74
    GREEN_S, RED_S, GRAY = "#1e8f4e", "#96271c", "#cbd2da"

    def bar(cx, sec, fill, stroke, xlabel, note=None, note_col=None):
        o = rect(cx - bw / 2, Y(sec), bw, y0 - Y(sec), fill=fill, stroke=stroke, sw=1.8, rx=4)
        o += text(cx, Y(sec) - 10, "≈%.1f с" % sec, size=13, bold=True, color=INK)
        o += mtext(cx, y0 + 24, xlabel, size=12, color=INK, lh=1.18)
        if note:
            o += mtext(cx, y0 + 62, note, size=11, color=note_col or MUTED, lh=1.18, bold=True)
        return o

    # I/O: послідовно 2 (сірий) · конкурентно 1 (ЗЕЛЕНЕ — виграш) · паралельно 1 (світло-зелене, дарма)
    f.append(bar(160, 2.0, GRAY, MUTED, ["послідовно"]))
    f.append(bar(285, 1.0, FIELD, GREEN_S, ["конкурентно", "1 ядро"], ["← виграш уже тут"], GREEN_S))
    f.append(bar(410, 1.0, "#a7e0bf", GREEN_S, ["паралельно", "N ядер"], ["ядра дарма"], MUTED))

    # CPU: послідовно 2 (сірий) · конкурентно 2 (ЧЕРВОНЕ — GIL, застрягло) · паралельно 1 (ЗЕЛЕНЕ — виграш)
    f.append(bar(590, 2.0, GRAY, MUTED, ["послідовно"]))
    f.append(bar(715, 2.0, POS, RED_S, ["конкурентно", "1 ядро"], ["потоки: GIL —", "0 виграшу"], RED_S))
    f.append(bar(840, 1.0, FIELD, GREEN_S, ["паралельно", "N ядер"], ["← виграш аж тут"], GREEN_S))

    f.append(mtext(500, H - 34,
                   ["Зелене (падіння до ≈1 с) приходить РАНІШЕ для I/O — від самої конкурентності;",
                    "для CPU — лише ПІЗНІШЕ, від справжнього паралелізму на ядрах."],
                   size=12.5, color=INK, lh=1.3))

    render(os.path.join(IMG, "regimes-results.svg"), W, H, *f,
           title="Три режими проти двох робіт: де саме час падає вдвічі")


# ───────── Фіг. (hist): нитка структури — Дейкстра → Гоар → Пайк ─────────
def fig_hist_lineage():
    W, H = 1100, 476
    f = []
    axis_y = 250
    D_X, H_X, P_X = 210, 545, 875   # три віхи — рівновіддалені (вісь-послідовність)
    GRN = "#0e7d4b"

    # головна вісь часу
    f.append(line(90, axis_y, 1010, axis_y, color=INK, sw=2))

    # ── верх: два слова-синоніми, що роз'їхались аж у Пайка ──
    f.append(rect(90, 50, 638, 34, fill="#f4f6f8", stroke="#d7dbe0", sw=1.4, rx=8))
    f.append(text(409, 72, "«конкурентний» = «паралельний»   (пів століття — синоніми)",
                  size=12.5, color=MUTED, italic=True))
    f.append(fitbox(752, 44, 250, 24, "СТРУКТУРА — конкурентність",
                    size=11, fill="#e3f7ec", stroke=GRN, color=INK, bold=True, sw=1.6))
    f.append(fitbox(752, 74, 250, 24, "ВИКОНАННЯ — паралелізм",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK, bold=True, sw=1.6))
    f.append(line(728, 67, 750, 56, color=MUTED, sw=1.3))
    f.append(line(728, 67, 750, 86, color=MUTED, sw=1.3))

    # ── картки-віхи над віссю ──
    def milestone(cx, yr, name, sub, essence, accent, tint):
        cw, ch, cy = 262, 104, 108
        x = cx - cw / 2
        o  = rect(x, cy, cw, ch, fill=tint, stroke=accent, sw=1.8, rx=8)
        o += text(cx, cy + 26, name, size=15, bold=True, color=accent)
        o += text(cx, cy + 46, sub, size=10.5, italic=True, color=MUTED)
        o += mtext(cx, cy + 68, essence, size=11.5, color=INK, lh=1.25)
        o += line(cx, cy + ch, cx, axis_y - 9, color=accent, sw=1.2, dash="3,4")
        o += circle(cx, axis_y, 8, fill=accent, stroke=accent, sw=2)
        o += text(cx, axis_y + 27, yr, size=12.5, bold=True, color=accent)
        return o

    f.append(milestone(D_X, "1965", "Дейкстра", "взаємодійні послідовні процеси",
        ["«нічого не припускай про", "відносні швидкості»:", "структура — не про залізо"], NEG, "#eaf0fd"))
    f.append(milestone(H_X, "1978", "Гоар", "CSP: процеси, що спілкуються",
        ["алгебра структури — як", "незалежні процеси", "складаються й шлють вісті"], GRN, "#e3f7ec"))
    f.append(milestone(P_X, "2012", "Пайк", "«Concurrency is not parallelism»",
        ["дає різниці ім'я:", "структура (як пишеш) ≠", "виконання (скільки ядер)"], POS, "#fdecea"))

    # ── нижня нитка: CSP у мовах Пайка (Гоар → Пайк) ──
    ly = 342
    ly_top = 286   # нижче написів-років під віссю — щоб штрих не перетинав рік
    f.append(line(H_X, ly_top, H_X, ly, color=GRN, sw=1.4, dash="2,4"))
    f.append(line(H_X, ly, P_X, ly, color=GRN, sw=2))
    f.append(line(P_X, ly, P_X, ly_top, color=GRN, sw=1.4, dash="2,4"))
    langs = [("Squeak", 0.0, -1), ("Newsqueak", 0.28, 1), ("Alef", 0.52, -1),
             ("Limbo", 0.72, 1), ("Go", 1.0, -1)]
    for nm, t, side in langs:
        x = H_X + t * (P_X - H_X)
        f.append(circle(x, ly, 4.5, fill=GRN, stroke=GRN, sw=1))
        ty = ly - 12 if side < 0 else ly + 20
        # крайні підписи (Squeak/Go) стоять рівно під штрихом Гоара/Пайка — зсунь текст
        # убік від штриха, крапка лишається на місці (не міняє сенсу — лише розкладку)
        tx = x + 34 if t <= 0.0 else (x - 34 if t >= 1.0 else x)
        f.append(text(tx, ty, nm, size=11, color=GRN, bold=True))
    f.append(text((H_X + P_X) / 2, ly + 46,
                  "нитка CSP Гоара, яку Пайк 25 років вносив у мови → канали Go",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "hist-lineage.svg"), W, H, *f,
           title="Різниця жила з 1965-го — Пайк лише дав їй ім'я")


if __name__ == "__main__":
    fig_interleave_vs_parallel()
    fig_two_axes()
    fig_io_vs_cpu()
    fig_regimes_results()
    fig_hist_lineage()
    print("OK: interleave-vs-parallel.svg, two-axes.svg, io-vs-cpu.svg, regimes-results.svg, hist-lineage.svg")
