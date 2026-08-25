# -*- coding: utf-8 -*-
"""Фігури до теми «Двійковий канал зі стиранням» (binary-erasure-channel).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def Hbin(p):
    """Двійкова ентропія H(p) у бітах (з коректними межами 0 і 1)."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


# ── 1. Схема переходів BEC: символ проходить (1−ε) або стирається на «?» (ε) ────
# Ідея, яку важко словами: у виході ТРИ значення (0, «?», 1), а перехресних
# стрілок 0→1 / 1→0 немає взагалі — канол лише доносить або губить, не перевертає.
def fig_transition():
    W, H = 720, 400
    xin, xout = 185, 535
    y0, y1 = 130, 342          # входи/бічні виходи: 0 угорі, 1 унизу
    ymid = (y0 + y1) / 2.0     # знак стирання «?» — посередині праворуч
    r = 27
    f = []

    # заголовки колонок
    f.append(text(xin, 76, "вхід  X", 13, INK, "middle", bold=True))
    f.append(text(xout, 76, "вихід  Y", 13, INK, "middle", bold=True))

    def edge(cx, cy, tx, ty):
        dx, dy = tx - cx, ty - cy
        L = math.hypot(dx, dy)
        return cx + r * dx / L, cy + r * dy / L

    # ── прямі стрілки (символ проходить), зелені = «ціле» ──
    f.append(arrow(xin + r, y0, xout - r, y0, color=FIELD, sw=2.4))
    f.append(arrow(xin + r, y1, xout - r, y1, color=FIELD, sw=2.4))
    f.append(text(360, 116, "1 − ε", 13.5, FIELD, "middle", bold=True))
    f.append(text(360, 328, "1 − ε", 13.5, FIELD, "middle", bold=True))

    # ── стрілки стирання (символ зникає), сірі = «втрата з позначкою» ──
    ax, ay = edge(xin, y0, xout, ymid)
    bx, by = edge(xout, ymid, xin, y0)
    f.append(arrow(ax, ay, bx, by, color=MUTED, sw=2.2))
    cx0, cy0 = edge(xin, y1, xout, ymid)
    dx0, dy0 = edge(xout, ymid, xin, y1)
    f.append(arrow(cx0, cy0, dx0, dy0, color=MUTED, sw=2.2))
    # підписи «ε» — над/під своїми стрілками, збоку від лінії
    f.append(text(300, 168, "ε", 14, MUTED, "middle", bold=True))
    f.append(text(300, 300, "ε", 14, MUTED, "middle", bold=True))

    # ── вузли (поверх стрілок) ──
    f.append(circle(xin, y0, r, fill=BG, stroke=INK, sw=2))
    f.append(text(xin, y0 + 8, "0", 22, INK, "middle", bold=True))
    f.append(circle(xin, y1, r, fill=BG, stroke=INK, sw=2))
    f.append(text(xin, y1 + 8, "1", 22, INK, "middle", bold=True))
    f.append(circle(xout, y0, r, fill=BG, stroke=INK, sw=2))
    f.append(text(xout, y0 + 8, "0", 22, INK, "middle", bold=True))
    f.append(circle(xout, y1, r, fill=BG, stroke=INK, sw=2))
    f.append(text(xout, y1 + 8, "1", 22, INK, "middle", bold=True))
    # знак стирання «?» — сірий, «втрачене, але позначене»
    f.append(circle(xout, ymid, r, fill="#eef0f2", stroke=MUTED, sw=2))
    f.append(text(xout, ymid + 8, "?", 22, MUTED, "middle", bold=True))
    f.append(text(xout + r + 12, ymid + 5, "стирання", 12, MUTED, "start", bold=True))

    # підсумкова смуга
    f.append(fitbox(78, 360, 564, 30,
                    "виходів три: 0, 1 і «?»; переворотів 0→1 чи 1→0 немає — приймач бачить, де саме втрата",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "transition-diagram.svg"), W, H, *f,
           title="Двійковий канал зі стиранням: символ проходить або зникає з позначкою")


# ── 2. Дві стелі: пряма 1−ε (стирання) вище за криву 1−H(p) (переворот) ─────────
# Ідея: за однакової частки ваді стирання щедріше, бо не змушує вгадувати позицію;
# при ваді 0.1 — 0.900 проти 0.531, майже вдвічі. Вісь лише [0, 0.5] (робочий діапазон).
def fig_capacity_compare():
    W, H = 720, 440
    ox, oy = 96, 356
    aw, ah = 540, 274
    y_top = oy - ah
    vmax = 0.5
    f = []

    def X(v):
        return ox + (v / vmax) * aw

    def Y(c):
        return oy - c * ah

    # сітка й підписи осі y
    for c in (0.0, 0.5, 1.0):
        y = Y(c)
        f.append(line(ox, y, ox + aw, y, color="#e3e7ec", sw=1.2))
        f.append(text(ox - 12, y + 4, "%.1f" % c, 11, MUTED, "end"))
    # осі
    f.append(line(ox, y_top - 6, ox, oy + 6, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    # підписи осі x
    for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        f.append(line(X(v), oy, X(v), oy + 6, color=INK, sw=1.3))
        f.append(text(X(v), oy + 22, ("%.1f" % v), 11, MUTED, "middle"))
    f.append(text(ox + aw / 2, oy + 44, "частка ушкоджених символів  (ε для стирання, p для переворотів)",
                  12, INK, "middle", bold=True))
    f.append(text(ox - 12, y_top - 14, "C — біт/символ", 12.5, INK, "start", bold=True))

    # крива переворотів C = 1 − H(p) (нижча)
    pts = []
    v = 0.0
    while v <= vmax + 1e-9:
        pts.append("%.2f,%.2f" % (X(v), Y(1 - Hbin(v))))
        v += 0.004
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))
    # пряма стирання C = 1 − ε (вища)
    f.append(line(X(0.0), Y(1.0), X(vmax), Y(1 - vmax), color=FIELD, sw=3.0))

    # вертикаль ваді 0.1 і дві точки
    cb = 1 - 0.1                    # стирання = 0.900
    cs = 1 - Hbin(0.1)              # переворот = 0.531
    f.append(line(X(0.1), Y(cs), X(0.1), Y(cb), color="#c7d0da", sw=1.3, dash="4 4"))
    f.append(circle(X(0.1), Y(cb), 5.5, fill=BG, stroke=FIELD, sw=2.6))
    f.append(circle(X(0.1), Y(cs), 5.5, fill=BG, stroke=NEG, sw=2.6))
    # проміжок = ціна незнання (стрілка збоку)
    f.append(arrow(X(0.1) - 26, Y(cb), X(0.1) - 6, Y(cb), color=POS, sw=1.5))
    f.append(arrow(X(0.1) - 26, Y(cs), X(0.1) - 6, Y(cs), color=POS, sw=1.5))
    f.append(mtext(X(0.1) - 30, (Y(cb) + Y(cs)) / 2 - 4, ["проміжок —", "ціна незнання,", "де втрата"],
                   10.5, POS, anchor="end", bold=True))

    # підписи значень біля точок
    f.append(text(X(0.1) + 12, Y(cb) + 4, "стирання: 0.900", 11.5, FIELD, "start", bold=True))
    f.append(text(X(0.1) + 12, Y(cs) + 4, "переворот: 0.531", 11.5, NEG, "start", bold=True))

    # мітки кривих на правому кінці
    f.append(text(X(vmax) - 6, Y(1 - vmax) - 12, "C = 1 − ε", 12.5, FIELD, "end", bold=True))
    f.append(text(X(0.42), Y(1 - Hbin(0.42)) + 22, "C = 1 − H(p)", 12.5, NEG, "middle", bold=True))

    render(os.path.join(IMG, "capacity-compare.svg"), W, H, *f,
           title="Знати, де втрата, дорожче за біт: 1 − ε вище за 1 − H(p)")


# ── 3. Стирання показує позицію, помилка ховається ─────────────────────────────
# Ідея, яку важко словами: у стиранні відомо ДЕ (лишилось знайти ЩО), у помилці
# невідомо навіть де — тому t стирань коштує відстані t+1, а t помилок аж 2t+1.
def fig_erasure_vs_error():
    W, H = 780, 392
    n = 7
    cw, chh = 50, 50
    gap = 8
    total = n * cw + (n - 1) * gap
    x0 = (W - total) / 2.0 + 46      # трохи праворуч, щоб лишити місце на мітку зліва

    def cell(i):
        return x0 + i * (cw + gap)

    f = []

    # ── рядок «стирання» ──
    yr1 = 96
    f.append(text(x0 - 22, yr1 + chh / 2 - 6, "стирання", 13, FIELD, "end", bold=True))
    f.append(text(x0 - 22, yr1 + chh / 2 + 12, "відомо ДЕ", 10.5, MUTED, "end"))
    bits1 = ["1", "0", "?", "1", "?", "0", "1"]
    for i, b in enumerate(bits1):
        cx = cell(i)
        if b == "?":
            f.append(rect(cx, yr1, cw, chh, fill="#eef0f2", stroke=MUTED, sw=2.2, rx=7))
            f.append(text(cx + cw / 2, yr1 + chh / 2 + 8, "?", 24, MUTED, "middle", bold=True))
        else:
            f.append(rect(cx, yr1, cw, chh, fill=BG, stroke=INK, sw=1.6, rx=7))
            f.append(text(cx + cw / 2, yr1 + chh / 2 + 8, b, 22, INK, "middle", bold=True))
    f.append(text(x0 + total / 2, yr1 + chh + 26,
                  "позиції втрат позначені — лишилось знайти лише ЩО", 12, FIELD, "middle", bold=True))

    # ── рядок «помилка» ──
    yr2 = 226
    f.append(text(x0 - 22, yr2 + chh / 2 - 6, "помилка", 13, POS, "end", bold=True))
    f.append(text(x0 - 22, yr2 + chh / 2 + 12, "невідомо де", 10.5, MUTED, "end"))
    bits2 = ["1", "0", "0", "1", "1", "0", "1"]   # два потай перевернуті — незнати які
    for i, b in enumerate(bits2):
        cx = cell(i)
        f.append(rect(cx, yr2, cw, chh, fill=BG, stroke=INK, sw=1.6, rx=7))
        f.append(text(cx + cw / 2, yr2 + chh / 2 + 8, b, 22, INK, "middle", bold=True))
    # дужка над усім словом: «котрі два брешуть?»
    f.append(text(x0 + total / 2, yr2 + chh + 26,
                  "два біти збрехали — але котрі? спершу вистежити, тоді виправити",
                  12, POS, "middle", bold=True))

    # ── підсумок: удвічі дешевше (широка смуга майже на всю ширину полотна,
    # щоб довгий рядок не змушував шрифт стискатись нижче читабельного) ──
    band_margin = 24
    f.append(fitbox(band_margin, 330, W - 2 * band_margin, 44,
                    "t стирань виправляє код з відстанню t + 1;  t помилок потребує аж 2t + 1  —  знати позицію вдвічі дешевше",
                    size=12.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(IMG, "erasure-vs-error.svg"), W, H, *f,
           title="Стирання показує позицію, помилка ховається")


# ── 4. Історична арка: народження 1955-го, ~40 років сну, вибух 1998–2006 ───────
# Ідея, яку важко словами: абстрактну модель Еліаса ДЕСЯТИЛІТТЯ ніхто не вживав, і
# аж інтернет зробив її реальною — звідси фонтанні / rateless-коди. Проміжок
# 1955→1998 на осі порожній навмисно (зигзаг-розрив) — це і є «сон» моделі.
def fig_history_arc():
    W, H = 920, 430
    spine = 250
    f = []

    def dot(x, color):
        return circle(x, spine, 7, fill=BG, stroke=color, sw=3)

    BW, BH = 172, 54

    def abox(x, l1, l2, color):          # підпис НАД спиною
        bx, by = x - BW / 2, spine - 20 - BH
        return (line(x, by + BH, x, spine, color=MUTED, sw=1.4) + dot(x, color) +
                fitbox(bx, by, BW, BH, l1 + "\n" + l2, size=11,
                       fill=BG, stroke=color, sw=2, color=INK, rx=8))

    def bbox(x, l1, l2, color):          # підпис ПІД спиною
        bx, by = x - BW / 2, spine + 20
        return (line(x, spine, x, by, color=MUTED, sw=1.4) + dot(x, color) +
                fitbox(bx, by, BW, BH, l1 + "\n" + l2, size=11,
                       fill=BG, stroke=color, sw=2, color=INK, rx=8))

    # спина з розривом-зигзагом між 1955 і 1998 (десятиліття тиші)
    f.append(line(58, spine, 345, spine, color=INK, sw=2.2))
    f.append(line(400, spine, 862, spine, color=INK, sw=2.2))
    f.append('<polyline points="345,%d 357,%d 372,%d 388,%d 400,%d" '
             'fill="none" stroke="%s" stroke-width="2.2"/>'
             % (spine, spine - 10, spine + 10, spine - 10, spine, INK))

    # рання теорія — холодним синім; практика — робочим зеленим
    f.append(abox(120, "1948 · Шеннон", "теорія інформації", NEG))
    f.append(bbox(255, "1955 · Еліас", "канал зі стиранням", NEG))
    f.append(abox(495, "1998 · Баєрс, Люби", "цифровий фонтан", FIELD))
    f.append(bbox(650, "2002 · Люби", "LT-коди", FIELD))
    f.append(abox(810, "2006 · Шокроллагі", "Raptor-коди", FIELD))

    # напис про сон — у чистому проміжку над спиною, між 1948 і 1998
    f.append(mtext(330, 150, ["≈ 40 років тиші:", "модель без застосувань"],
                   12, MUTED, anchor="middle"))

    # підсумкова смуга — розв'язка арки
    f.append(fitbox(60, 366, 800, 40,
                    "абстракцію 1955-го зробив реальною лише інтернет — і породив фонтанні коди 2000-х",
                    size=13, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(IMG, "history-arc.svg"), W, H, *f,
           title="Від іграшкового прикладу 1955-го до основи мереж")


# ── 5. H(X|Y) = ε·H(X): невизначеність входу лишається лише на стертій частці ────
# Ідея, яку важко словами: уся маса виходу ділиться надвоє — вцілілій частці 1−ε
# (виходи 0/1) вхід відомий точно (залишок 0), і лише стертій частці ε апостеріор =
# апріор (залишок повний H(X)). Середнє по смузі = (1−ε)·0 + ε·H(X) = ε·H(X).
AMBER_F, AMBER_S, AMBER_I = "#f4ecd8", "#b8860b", "#8a6d1b"


def fig_posterior_by_output():
    W, H = 760, 430
    eps = 0.30                       # ілюстративне ε для видимих пропорцій
    x0, x1 = 84, 676
    bw = x1 - x0
    ytop, bh = 132, 116
    ybot = ytop + bh
    xs = x0 + (1 - eps) * bw          # межа: зліва вціліле (1−ε), справа стерте (ε)
    f = []

    # верхні дужки — ваги P(Y), тобто скільки маси в кожній зоні
    def hbracket(xa, xb, yb, label, col):
        f.append(line(xa, yb, xb, yb, color=col, sw=1.6))
        f.append(line(xa, yb, xa, yb + 7, color=col, sw=1.6))
        f.append(line(xb, yb, xb, yb + 7, color=col, sw=1.6))
        f.append(text((xa + xb) / 2, yb - 8, label, 13, col, "middle", bold=True))

    hbracket(x0, xs, ytop - 20, "P = 1 − ε", FIELD)
    hbracket(xs, x1, ytop - 20, "P = ε", AMBER_I)

    # дві зони: вціліле (залишок 0) і стерте (залишок H(X))
    f.append(rect(x0, ytop, xs - x0, bh, fill="#e7f6ec", stroke=FIELD, sw=2, rx=8))
    f.append(rect(xs, ytop, x1 - xs, bh, fill=AMBER_F, stroke=AMBER_S, sw=2, rx=8))

    f.append(mtext((x0 + xs) / 2, ytop + 38,
                   ["вихід  0  або  1", "вхід відновлено точно", "залишок = 0"],
                   14, INK, "middle", lh=1.5))
    f.append(text((x0 + xs) / 2, ybot - 14, "H(X|Y=0) = H(X|Y=1) = 0",
                  11.5, FIELD, "middle", bold=True))

    f.append(mtext((xs + x1) / 2, ytop + 38,
                   ["вихід  «?»", "нічого не взнав", "залишок = H(X)"],
                   13.5, INK, "middle", lh=1.5))
    f.append(text((xs + x1) / 2, ybot - 14, "H(X|Y=?) = H(X)",
                  11.5, AMBER_I, "middle", bold=True))

    # вісь ймовірнісної маси під смугою
    ya = ybot + 16
    for xx, lab in ((x0, "0"), (xs, "1 − ε"), (x1, "1")):
        f.append(line(xx, ybot, xx, ya, color=MUTED, sw=1.2))
        f.append(text(xx, ya + 15, lab, 11.5, MUTED, "middle", bold=(lab == "1 − ε")))
    f.append(text((x0 + x1) / 2, ya + 33, "частка ймовірнісної маси виходу", 11.5, MUTED, "middle"))

    body, _, _ = textbox(W / 2, 392,
                         "H(X|Y) = (1 − ε)·0 + ε·H(X) = ε·H(X)",
                         size=15, pad=13, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
    f.append(body)

    render(os.path.join(IMG, "posterior-by-output.svg"), W, H, *f,
           title="Невизначеність входу лишається тільки на стертій частці")


# ── 6. Бюджет відстані: 2e + s ≤ d − 1 — помилка коштує 2, стирання 1 ────────────
# Ідея, яку важко словами: той самий розрив d між двома кодовими словами витрачають
# двома способами. Кулі радіуса t навколо кожного слова мусять не злитися (2t+1≤d),
# а стирань код тримає аж d−1, бо однієї вцілілої різниці досить. Звідси «вдвічі».
def fig_distance_budget():
    W, H = 720, 470
    d = 5
    u, x_left = 92, 156
    band = 30

    def xk(k):
        return x_left + k * u

    f = []

    def panel(yb, title, title_col):
        f.append(text(x_left - 120, yb + 5, title, 13.5, title_col, "start", bold=True))
        f.append(line(xk(0), yb, xk(d), yb, color=INK, sw=1.6))
        for k in range(d + 1):
            f.append(line(xk(k), yb - 5, xk(k), yb + 5, color=INK, sw=1.3))
            f.append(text(xk(k), yb + band / 2 + 20, str(k), 10.5, MUTED, "middle"))
        f.append(circle(xk(0), yb, 7, fill=INK, stroke=INK, sw=1))
        f.append(circle(xk(d), yb, 7, fill=INK, stroke=INK, sw=1))
        f.append(text(xk(0) - 20, yb + 5, "c", 15, INK, "middle", bold=True))
        f.append(text(xk(d) + 22, yb + 5, "c′", 15, INK, "middle", bold=True))

    def zone(k1, k2, yb, fill, stroke):
        f.append(rect(xk(k1), yb - band / 2, xk(k2) - xk(k1), band,
                      fill=fill, stroke=stroke, sw=1.8, rx=5))

    def brace_lbl(k1, k2, yb, label, col):
        f.append(text((xk(k1) + xk(k2)) / 2, yb - band / 2 - 10, label, 11.5, col, "middle", bold=True))

    # ── панель «помилки»: дві кулі радіуса t=2 з проміжком 1 ──
    yA = 118
    t = 2
    zone(0, t, yA, "#e7f6ec", FIELD)
    zone(d - t, d, yA, "#e9eefc", NEG)
    panel(yA, "помилки", POS)
    brace_lbl(0, t, yA, "куля c:  t = 2", FIELD)
    brace_lbl(d - t, d, yA, "куля c′:  t = 2", NEG)
    f.append(line(xk(2.5), yA - band / 2 - 2, xk(2.5), yA + band / 2 + 2, color=MUTED, sw=1.3, dash="4 3"))
    f.append(text(W / 2, yA + band / 2 + 42,
                  "кулі не злипаються:  2t + 1 = 5 ≤ d  →  виправляє  t = 2  помилки",
                  12.5, INK, "middle", bold=True))

    # ── панель «стирання»: зона d−1 схованих різниць + одна вціліла ──
    yB = 272
    zone(0, d - 1, yB, AMBER_F, AMBER_S)
    zone(d - 1, d, yB, "#e7f6ec", FIELD)
    panel(yB, "стирання", FIELD)
    brace_lbl(0, d - 1, yB, "стерто ховає  d − 1 = 4", AMBER_I)
    brace_lbl(d - 1, d, yB, "вціліла  1", FIELD)
    f.append(text(W / 2, yB + band / 2 + 42,
                  "однієї вцілілої різниці досить:  s + 1 = 5 ≤ d  →  виправляє  s = 4  стирання",
                  12.5, INK, "middle", bold=True))

    f.append(fitbox(x_left - 132, 388, xk(d) - x_left + 214, 56,
                    "той самий запас d = 5:  4 стирання проти 2 помилок\nзагалом  2e + s ≤ d − 1  —  помилка коштує 2 одиниці, стирання 1",
                    size=13, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    render(os.path.join(IMG, "distance-budget.svg"), W, H, *f,
           title="Бюджет відстані: помилка коштує 2, стирання 1")


if __name__ == "__main__":
    fig_transition()
    fig_capacity_compare()
    fig_erasure_vs_error()
    fig_history_arc()
    fig_posterior_by_output()
    fig_distance_budget()
    print("OK: figures written to", IMG)
