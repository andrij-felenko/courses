# -*- coding: utf-8 -*-
"""Фігури до теми «Логарифм відношення правдоподібностей (LLR)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Числова вісь LLR: знак = рішення, модуль = впевненість ──────────────────
# Ідея, яку важко словами: одне число зі знаком одночасно несе «який біт» (по який
# бік нуля) і «наскільки певно» (як далеко від нуля); нуль — цілковита непевність.
def fig_number_line():
    W, H = 780, 320
    axy = 168
    xc = 390                     # x, де L = 0
    scale = 58.0                 # px на одиницю L
    Lmax = 4.4
    f = []

    def X(L):
        return xc + scale * L

    # вісь із двома вістрями
    f.append(arrow(xc, axy, X(Lmax) + 20, axy, color=INK, sw=1.8))
    f.append(arrow(xc, axy, X(-Lmax) - 20, axy, color=INK, sw=1.8))

    # кольорові зони (ледь помітні смуги) — ліворуч синя (одиниця), праворуч червона (нуль)
    f.append(rect(X(-Lmax) - 16, axy - 4, (Lmax) * scale + 16, 8, fill="#eaf0fd", stroke="none", rx=4))
    f.append(rect(xc, axy - 4, (Lmax) * scale + 16, 8, fill="#fdecea", stroke="none", rx=4))

    # центр — нуль
    f.append(line(xc, axy - 34, xc, axy + 20, color=INK, sw=1.6, dash="5 4"))
    f.append(text(xc, axy + 40, "0", 14, INK, "middle", bold=True))
    f.append(mtext(xc, axy + 58, ["не знаю", "(монета)"], 11, MUTED, anchor="middle"))

    # підписи країв (у верхніх кутах, поза колонками зразків): рішення за знаком
    f.append(text(X(-Lmax) - 6, axy - 118, "L < 0  →  біт 1", 13.5, NEG, "start", bold=True))
    f.append(text(X(Lmax) + 6, axy - 118, "біт 0  ←  L > 0", 13.5, POS, "end", bold=True))

    # зразкові точки (L, підпис, вгору/вниз, колір) — значення й підпис вирівняні по x над/під точкою
    pts = [
        (-3.6, "певна одиниця", "up", NEG),
        (-0.8, "слабко одиниця", "down", NEG),
        (0.8, "слабко нуль", "down", POS),
        (3.6, "певний нуль", "up", POS),
    ]
    for L, lab, side, col in pts:
        x = X(L)
        f.append(circle(x, axy, 6, fill=col, stroke=col, sw=0))
        if side == "up":
            f.append(text(x, axy - 22, ("%+.1f" % L), 12, col, "middle", bold=True))
            f.append(text(x, axy - 58, lab, 11, MUTED, "middle"))
        else:
            f.append(text(x, axy + 30, ("%+.1f" % L), 12, col, "middle", bold=True))
            f.append(text(x, axy + 48, lab, 11, MUTED, "middle"))

    f.append(fitbox(150, 292, W - 300, 24,
                    "знак L — рішення  ·  |L| — упевненість  ·  L = 0 — цілковита непевність",
                    size=12, fill=FILL, stroke=LINE, color=INK, bold=True))
    render(os.path.join(IMG, "llr-number-line.svg"), W, H, *f,
           title="LLR: одне число зі знаком несе рішення і впевненість")


# ── 2. Незалежні свідчення додаються (а тверде голосування — ні) ───────────────
# Ідея: м'яке додає L-значення (сильне перекриває слабке зустрічне), тверде дає
# кожному один голос, тож два різні за певністю відліки виходять у нічию.
def fig_evidence_adds():
    W, H = 800, 380
    x0 = 150                     # L = 0
    scale = 116.0                # px на одиницю L
    f = []

    def X(L):
        return x0 + scale * L

    # ── ряд А: м'яке — додаємо стрілки ──
    ya = 118
    f.append(text(70, ya - 46, "м'яке:", 14, FIELD, "start", bold=True))
    # базова вісь із нулем
    f.append(line(x0, ya + 40, X(4.2), ya + 40, color="#cfd6de", sw=1.3))
    f.append(text(x0, ya + 58, "0", 11, MUTED, "middle"))
    for Lt in (1, 2, 3, 4):
        f.append(line(X(Lt), ya + 36, X(Lt), ya + 44, color="#cfd6de", sw=1.1))
        f.append(text(X(Lt), ya + 58, str(Lt), 10.5, MUTED, "middle"))

    # L1 = +3.6 (червона стрілка від 0)
    f.append(arrow(X(0), ya, X(3.6), ya, color=POS, sw=3))
    f.append(text(X(1.8), ya - 12, "L₁ = +3.6", 12.5, POS, "middle", bold=True))
    f.append(text(X(1.8), ya + 22, "певний нуль", 10.5, MUTED, "middle"))
    # L2 = −0.8 (синя стрілка назад від 3.6 до 2.8)
    f.append(arrow(X(3.6), ya, X(2.8), ya, color=NEG, sw=3))
    f.append(text(X(4.35), ya - 12, "L₂ = −0.8", 12.5, NEG, "start", bold=True))
    f.append(text(X(4.35), ya + 6, "слабка одиниця", 10.5, MUTED, "start"))
    # сума
    f.append(circle(X(2.8), ya, 6.5, fill=BG, stroke=FIELD, sw=2.6))
    f.append(line(X(2.8), ya - 8, X(2.8), ya - 34, color=FIELD, sw=1.4, dash="4 3"))
    f.append(text(X(2.8), ya - 40, "сума = +2.8  →  біт 0", 12.5, FIELD, "middle", bold=True))

    # ── ряд Б: тверде — голосуємо ──
    yb = 268
    f.append(text(70, yb - 6, "тверде:", 14, POS, "start", bold=True))
    b1, _, _ = textbox(x0 + 130, yb, ["sign(y₁) = +", "→ голос: 0"], size=12.5,
                       pad=10, fill="#fdecea", stroke=POS, sw=1.8, color=INK, bold=True)
    b2, _, _ = textbox(x0 + 320, yb, ["sign(y₂) = −", "→ голос: 1"], size=12.5,
                       pad=10, fill="#eaf0fd", stroke=NEG, sw=1.8, color=INK, bold=True)
    f.append(b1)
    f.append(b2)
    f.append(text(x0 + 225, yb - 44, "один голос кожному", 11, MUTED, "middle"))
    f.append(arrow(x0 + 400, yb, x0 + 470, yb, color=MUTED, sw=1.8))
    b3, _, _ = textbox(x0 + 545, yb, ["нічия:", "рішення нема"], size=12.5,
                       pad=10, fill=FILL, stroke=INK, sw=1.8, color=INK, bold=True)
    f.append(b3)

    f.append(line(120, 200, W - 60, 200, color="#e3e7ec", sw=1.2))
    f.append(fitbox(150, 344, W - 300, 26,
                    "певність, яку тверде рішення викидає, м'яке пускає в діло — сильний відлік важить більше",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "evidence-adds.svg"), W, H, *f,
           title="Незалежні свідчення додаються; голоси — ні")


# ── 3. Гаусів канал у координатах LLR — це пряма L = 2y/σ² ─────────────────────
# Ідея: дві гаусіани над віссю y мапляться прямою в LLR; нахил задає шум —
# тихий канал (мала σ²) робить пряму крутою, гучний кладе її майже плазом.
def fig_channel_to_llr():
    W, H = 780, 560
    ox, aw = 110, 560
    xc = ox + aw / 2             # y = 0
    yscale = aw / 5.2            # y ∈ [−2.6, 2.6]

    def X(y):
        return xc + yscale * y

    f = []

    # ── верхня панель: дві гаусові хмари над віссю y ──
    base = 190
    peak = 92
    sig_px = yscale * 0.72
    f.append(line(ox - 6, base, ox + aw + 14, base, color=INK, sw=1.6))
    f.append(arrow(ox + aw, base, ox + aw + 16, base, color=INK, sw=1.6))
    f.append(text(ox + aw + 10, base + 22, "прийнята напруга y", 11.5, INK, "end", bold=True))

    def bell(xc0, col):
        pts = []
        x = xc0 - 3.1 * sig_px
        while x <= xc0 + 3.1 * sig_px:
            pts.append("%.1f,%.1f" % (x, base - peak * math.exp(-((x - xc0) / sig_px) ** 2 / 2)))
            x += 2.4
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), col)

    f.append(bell(X(-1), NEG))
    f.append(bell(X(1), POS))
    # мітки рівнів
    f.append(circle(X(-1), base, 5, fill=NEG, stroke=NEG, sw=0))
    f.append(circle(X(1), base, 5, fill=POS, stroke=POS, sw=0))
    f.append(mtext(X(-1), base + 22, ["рівень −1", "(біт 1)"], 11, NEG, anchor="middle", bold=True))
    f.append(mtext(X(1), base + 22, ["рівень +1", "(біт 0)"], 11, POS, anchor="middle", bold=True))
    # поріг у нулі
    f.append(line(xc, base + 8, xc, base - peak - 14, color=MUTED, sw=1.3, dash="5 4"))
    f.append(text(xc, base - peak - 20, "поріг 0", 11, MUTED, "middle"))

    # ── нижня панель: пряма L = 2y/σ² ──
    L0 = 402                     # вісь y тут (L = 0)
    Lscale = 12.5                # px на одиницю L
    Lshow = 8.0
    # осі
    f.append(line(ox - 6, L0, ox + aw + 14, L0, color=INK, sw=1.4))
    f.append(line(xc, L0 - Lshow * Lscale - 12, xc, L0 + Lshow * Lscale + 6, color=INK, sw=1.4))
    f.append(text(xc + 8, L0 - Lshow * Lscale - 6, "L", 13, INK, "start", bold=True))
    for Lt in (-8, -4, 4, 8):
        yy = L0 - Lt * Lscale
        f.append(line(xc - 5, yy, xc + 5, yy, color=MUTED, sw=1.1))
        f.append(text(xc - 12, yy + 4, "%+d" % Lt, 10, MUTED, "end"))

    def draw_line(slope, col, dash=None):
        # L = slope * y, обрізаємо по Lshow
        ya = max(-2.6, -Lshow / slope)
        yb = min(2.6, Lshow / slope)
        f.append(line(X(ya), L0 - slope * ya * Lscale, X(yb), L0 - slope * yb * Lscale,
                      color=col, sw=2.6, dash=dash))

    draw_line(4.0, FIELD)                    # σ²=0.5 → нахил 4 (крута)
    draw_line(1.0, MUTED, dash="7 5")        # σ²=2   → нахил 1 (полога)
    # легенда у вільному верхньому-лівому куті нижньої панелі (там ліній нема)
    lx, lyy = ox + 14, L0 - Lshow * Lscale + 4
    f.append(line(lx, lyy, lx + 26, lyy, color=FIELD, sw=2.6))
    f.append(text(lx + 34, lyy + 4, "тихий канал σ²=0.5: крута", 11, FIELD, "start", bold=True))
    f.append(line(lx, lyy + 20, lx + 26, lyy + 20, color=MUTED, sw=2.6, dash="7 5"))
    f.append(text(lx + 34, lyy + 24, "гучний σ²=2: полога", 11, MUTED, "start", bold=True))

    # зв'язок панелей: приклад y = 0.9 → L = 3.6 (старт нижче підписів рівнів, щоб їх не перетнути)
    ys = 0.9
    f.append(circle(X(ys), base, 3.5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(line(X(ys), base + 52, X(ys), L0 - 4.0 * ys * Lscale, color="#c7d0da", sw=1.2, dash="3 4"))
    f.append(circle(X(ys), L0 - 4.0 * ys * Lscale, 5.5, fill=BG, stroke=FIELD, sw=2.4))
    f.append(text(X(ys) + 10, L0 - 4.0 * ys * Lscale + 4, "y=0.9 → L=3.6", 11, FIELD, "start", bold=True))

    f.append(fitbox(150, 524, W - 300, 26,
                    "квадрат у показнику гаусіани дає різницю квадратів → лінійний L; шум задає нахил",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "channel-to-llr.svg"), W, H, *f,
           title="Гаусів канал у координатах LLR — пряма L = 2y/σ²")


# ── 4. Тест Вальда: біжуча сума LLR між двома порогами (для hist-вставки) ──────
# Ідея, яку важко словами: адитивність log-відношення дає ОПЕРАЦІЙНИЙ прилад —
# після кожного відліку додай його L до суми; поки сума в смузі — бери ще відлік;
# щойно вийшла за верхній чи нижній поріг — спиняйся й вирішуй. Саме так Вальд
# перетворив «свідчення додаються» на процедуру, що заощаджує відліки.
def fig_sprt_walk():
    W, H = 860, 430
    ox = 118                      # x, де n = 0
    xstep = 54.0                  # px на один відлік
    yc = 208                      # y, де сума S = 0
    Sscale = 23.0                 # px на одиницю суми
    A = 4.6                       # верхній поріг → рішення «нуль»
    B = -4.6                      # нижній поріг → рішення «одиниця»
    f = []

    def X(n):
        return ox + xstep * n

    def Y(S):
        return yc - Sscale * S

    # біжуча сума: кожен крок — це +L поточного відліку (net drift догори)
    S = [0, 1.3, 0.7, 1.8, 2.2, 1.3, 2.8, 3.5, 3.0, 4.2, 5.0]
    nstop = len(S) - 1            # перетнули поріг A на останньому кроці

    yA, yB = Y(A), Y(B)

    # смуга нерішучості між порогами
    f.append(rect(X(0) - 8, yA, X(nstop) + 26, yB - yA, fill="#f4f7fb", stroke="none", rx=0))

    # осьова нульова лінія
    f.append(line(X(0) - 8, yc, X(nstop) + 30, yc, color="#cfd6de", sw=1.2, dash="4 4"))
    f.append(text(X(0) - 16, yc + 4, "0", 11, MUTED, "end"))

    # верхній поріг A
    f.append(line(X(0) - 8, yA, X(nstop) + 26, yA, color=POS, sw=1.8, dash="7 4"))
    f.append(mtext(X(0) - 2, yA - 30, ["поріг A", "сюди → рішення «нуль»"], 11.5, POS,
                   anchor="start", bold=True))
    # нижній поріг B
    f.append(line(X(0) - 8, yB, X(nstop) + 26, yB, color=NEG, sw=1.8, dash="7 4"))
    f.append(mtext(X(0) - 2, yB + 20, ["поріг B", "сюди → рішення «одиниця»"], 11.5, NEG,
                   anchor="start", bold=True))

    # сама траєкторія суми
    pts = " ".join("%.1f,%.1f" % (X(n), Y(s)) for n, s in enumerate(S))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, FIELD))
    for n, s in enumerate(S):
        if n == nstop:
            continue
        f.append(circle(X(n), Y(s), 3.6, fill=BG, stroke=FIELD, sw=2))

    # перший крок: підписати, що додаємо L одного відліку
    f.append(text(X(0.5), Y(0.65) - 12, "+L₁", 12, FIELD, "middle", bold=True))
    f.append(mtext(X(3.0), yc + 40, ["поки сума в смузі —", "береш ще один відлік"], 11.5,
                   MUTED, anchor="middle"))

    # точка перетину порога — рішення «нуль»
    f.append(line(X(nstop), Y(S[nstop]), X(nstop), yc + 4, color="#c7d0da", sw=1.1, dash="3 4"))
    f.append(circle(X(nstop), Y(S[nstop]), 6.5, fill=POS, stroke=POS, sw=0))
    f.append(mtext(X(nstop), Y(S[nstop]) - 36, ["перетнули поріг →", "стоп, рішення «нуль»"],
                   11.5, POS, anchor="middle", bold=True))

    # вісь відліків n унизу
    for n in range(nstop + 1):
        f.append(text(X(n), yc + 92, str(n), 10, MUTED, "middle"))
    f.append(text(X(nstop) + 30, yc + 92, "n →", 11, INK, "start", bold=True))
    f.append(text(X(0) - 16, yc + 92, "відлік", 10.5, INK, "end", bold=True))

    f.append(fitbox(160, 396, W - 320, 24,
                    "додай L відліку до суми · у смузі — бери ще · за порогом — спиняйся й вирішуй",
                    size=12, fill=FILL, stroke=LINE, color=INK, bold=True))
    render(os.path.join(IMG, "sprt-walk.svg"), W, H, *f,
           title="Тест Вальда: сума LLR іде, доки не впреться в поріг")


# ── 5. Одна величина, дві епохи: зі статистики в кодування (для hist-вставки) ──
# Ідея: log-відношення народилося у статистиці (Нейман–Пірсон, Вальд), десятиліття
# лишалося майже без ужитку, а тоді та сама адитивна величина стала валютою
# м'якого декодування. Часова вісь лінійна — щоб було видно довгий проміжок.
def fig_two_eras():
    W, H = 940, 470
    ox, x1 = 96, 858              # 1930 .. 2000
    y0, y1 = 1930.0, 2000.0
    axy = 250                     # часова вісь
    ppx = (x1 - ox) / (y1 - y0)   # px на рік

    def X(yr):
        return ox + (yr - y0) * ppx

    f = []

    # «довга тінь» між останньою статистичною й вибухом кодування
    xsh = (X(1948) + X(1993)) / 2
    f.append(rect(X(1948), axy - 6, X(1993) - X(1948), 12, fill="#eef1f5", stroke="none", rx=0))
    f.append(mtext(xsh, 150, ["≈ пів століття у тіні:", "адитивні м'які методи",
                              "чекають на дешеве залізо"], 11.5, MUTED, anchor="middle"))
    f.append(line(xsh, 192, xsh, axy - 6, color="#c7d0da", sw=1.1, dash="3 4"))

    # часова вісь
    f.append(line(ox - 6, axy, x1 + 14, axy, color=INK, sw=1.8))
    f.append(arrow(x1, axy, x1 + 16, axy, color=INK, sw=1.8))
    for yr in (1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000):
        f.append(line(X(yr), axy - 4, X(yr), axy + 4, color=MUTED, sw=1.1))
        f.append(text(X(yr), axy + 20, str(yr), 10, MUTED, "middle"))

    # ── маркер: точка на осі в РІК події + короткий стовпчик до картки; сама
    #    картка стоїть осторонь (рік написано в ній), тож лінії нічого не тнуть ──
    def marker(yr, cx, cy, lines, col):
        xt = X(yr)
        d = 16 if cy > axy else -16
        out = [line(xt, axy, xt, axy + d, color=col, sw=1.4)]
        out.append(circle(xt, axy, 4.5, fill=col, stroke=BG, sw=1.6))
        body, w, h = textbox(cx, cy, lines, size=11, pad=8, fill=BG, stroke=col,
                             sw=1.8, color=INK, bold=False)
        out.append(body)
        return out

    # СТАТИСТИКА (над віссю): дві висоти, щоб близькі 1945/1948 не злиплися
    f.append(text(ox - 6, 70, "СТАТИСТИКА", 12, POS, "start", bold=True))
    f += marker(1933, 150, 112, ["1933 · Нейман–Пірсон", "поріг на відношенні —", "найпотужніший тест"], POS)
    f += marker(1945, 330, 112, ["1945 · Вальд (SPRT)", "біжуча сума log-відношення,", "два пороги"], POS)
    f += marker(1948, 340, 176, ["1948 · Вальд–Волфовіц", "SPRT оптимальний —", "найменше відліків"], POS)

    # КОДУВАННЯ (під віссю): дві висоти
    f.append(text(ox - 6, 402, "КОДУВАННЯ", 12, FIELD, "start", bold=True))
    f += marker(1962, 438, 330, ["1962 · Ґаллаґер (LDPC)", "адитивні м'які підказки —", "надто рано для заліза"], FIELD)
    f += marker(1974, 579, 400, ["1974 · BCJR", "точні апостеріорні", "м'які значення"], FIELD)
    f += marker(1993, 752, 330, ["1993 · турбокоди", "декодери міняються", "extrinsic-LLR"], FIELD)
    f += marker(1996, 845, 400, ["1996 · Гаґенауер", "L-алгебра: канал +", "апріор + extrinsic"], FIELD)

    f.append(fitbox((W - 500) / 2, 440, 500, 22,
                    "та сама адитивна величина: спершу — прилад статистика, згодом — валюта декодера",
                    size=12, fill=FILL, stroke=LINE, color=INK, bold=True))
    render(os.path.join(IMG, "two-eras.svg"), W, H, *f,
           title="Одна величина, дві епохи: log-відношення зі статистики в кодування")


if __name__ == "__main__":
    fig_number_line()
    fig_evidence_adds()
    fig_channel_to_llr()
    fig_sprt_walk()
    fig_two_eras()
    print("OK: figures written to", IMG)
