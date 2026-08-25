# -*- coding: utf-8 -*-
"""Фігури до теми «Канал зі стиранням» (erasure-channel).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def edge(cx, cy, tx, ty, rr):
    """Точка на колі радіуса rr навколо (cx,cy) у напрямку до (tx,ty)."""
    dx, dy = tx - cx, ty - cy
    L = math.hypot(dx, dy)
    return cx + rr * dx / L, cy + rr * dy / L


# ── 1. Закон каналу: символ проходить АБО стирається, та НІКОЛИ не плутається ──
# Ідея, яку важко словами: усе визначення — три ребра від одного входу. Зелене
# (проходить) і червоне (стирається) реальні; середнє (символ → ІНШИЙ символ)
# перекреслене — саме його відсутність відрізняє стирання від помилки.
def fig_channel_law():
    W, H = 720, 430
    xin, yin, rin = 150, 232, 34
    xout, rout = 560, 30
    yTop, yMid, yBot = 108, 232, 356
    f = []

    f.append(text(xin, 58, "вхід", 13, INK, "middle", bold=True))
    f.append(text(xout, 58, "вихід", 13, INK, "middle", bold=True))

    # зелене ребро: проходить (той самий символ)
    ax, ay = edge(xin, yin, xout, yTop, rin)
    bx, by = edge(xout, yTop, xin, yin, rout)
    f.append(arrow(ax, ay, bx, by, color=FIELD, sw=2.6))
    f.append(text(352, 128, "1 − p  (проходить)", 13, FIELD, "middle", bold=True))

    # червоне ребро: стирається
    cx0, cy0 = edge(xin, yin, xout, yBot, rin)
    dx0, dy0 = edge(xout, yBot, xin, yin, rout)
    f.append(arrow(cx0, cy0, dx0, dy0, color=POS, sw=2.6))
    f.append(text(352, 338, "p  (стирається)", 13, POS, "middle", bold=True))

    # сіре пунктирне ребро: символ → ІНШИЙ символ — заборонене (перекреслене)
    ex, ey = edge(xin, yin, xout, yMid, rin)
    fx, fy = edge(xout, yMid, xin, yin, rout)
    f.append(line(ex, ey, fx, fy, color=MUTED, sw=1.6, dash="6 5"))
    mxx, myy = (ex + fx) / 2, (ey + fy) / 2
    f.append(line(mxx - 13, myy - 13, mxx + 13, myy + 13, color=POS, sw=2.6))
    f.append(line(mxx - 13, myy + 13, mxx + 13, myy - 13, color=POS, sw=2.6))
    f.append(text(352, 205, "0  (символ не плутається)", 12, MUTED, "middle"))

    # вузол входу
    f.append(circle(xin, yin, rin, fill=BG, stroke=INK, sw=2.2))
    f.append(text(xin, yin + 9, "x", 25, INK, "middle", bold=True, italic=True))
    f.append(text(xin, yin + rin + 22, "будь-який символ", 11, MUTED, "middle"))

    # вихід: той самий символ (зелений)
    f.append(circle(xout, yTop, rout, fill="#eef6ef", stroke=FIELD, sw=2.4))
    f.append(text(xout, yTop + 8, "x", 22, FIELD, "middle", bold=True, italic=True))
    f.append(text(xout + 46, yTop + 5, "той самий", 12.5, FIELD, "start", bold=True))

    # вихід: інший символ (заборонено)
    f.append(circle(xout, yMid, rout, fill=BG, stroke=MUTED, sw=1.8))
    f.append(text(xout, yMid + 7, "y", 20, MUTED, "middle", italic=True))
    f.append(text(xout + 46, yMid + 5, "інший символ", 12.5, MUTED, "start"))

    # вихід: стерто «?» (червоний)
    f.append(circle(xout, yBot, rout, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(xout, yBot + 10, "?", 25, POS, "middle", bold=True))
    f.append(text(xout + 46, yBot + 5, "стерто", 12.5, POS, "start", bold=True))

    f.append(fitbox(58, 398, 604, 26,
                    "втрата, що САМА себе оголошує: приймач бачить «?» і точно знає, ДЕ бракує символа",
                    size=12, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "erasure-law.svg"), W, H, *f,
           title="Канал зі стиранням: символ або проходить, або стає «?»")


# ── 2. Стирання проти помилки: відома позиція проти невідомої ─────────────────
# Ідея, яку важко словами: та сама надлишковість (1 біт парності) виправляє
# стирання (видно, ДЕ) і безсила проти помилки (не видно, ДЕ). Верхній рядок
# показує позицію «?» явно; нижній має цілком «правильний» вигляд — помилку
# видно лише глобально, без адреси.
def fig_erasure_vs_error():
    W, H = 780, 420
    n = 6
    cw, ch, gp = 44, 44, 7
    rowW = n * cw + (n - 1) * gp
    cxr = 232
    x0 = cxr - rowW / 2
    f = []

    def draw_row(cy, cells):
        out = []
        for i, (c, mode) in enumerate(cells):
            x = x0 + i * (cw + gp)
            if mode == "erase":
                fl, st, col, sw = "#fdecea", POS, POS, 2.4
            elif mode == "parity":
                fl, st, col, sw = "#eef2f7", MUTED, INK, 1.6
            else:
                fl, st, col, sw = BG, LINE, INK, 1.6
            out.append(rect(x, cy - ch / 2, cw, ch, fill=fl, stroke=st, sw=sw, rx=6))
            out.append(text(x + cw / 2, cy + 8, c, 22, col, "middle", bold=True))
        return "".join(out)

    xann = x0 + rowW + 28   # ліва межа правих анотацій

    # ── СТИРАННЯ (верх) ──
    yA = 116
    f.append(text(x0, yA - 42, "СТИРАННЯ — позиція втрати ВІДОМА", 13.5, INK, "start", bold=True))
    f.append(draw_row(yA, [("1", "n"), ("0", "n"), ("?", "erase"),
                           ("1", "n"), ("0", "n"), ("1", "parity")]))
    f.append(mtext(xann, yA - 12,
                   ["приймач бачить «?»", "стертий = XOR решти = 1", "відновлено ✓"],
                   12, INK, anchor="start"))
    f.append(text(xann, yA + 30, "✓", 15, FIELD, "start", bold=True))

    # ── ПОМИЛКА (низ) ──
    yB = 250
    f.append(text(x0, yB - 42, "ПОМИЛКА — біт перекинуто мовчки", 13.5, INK, "start", bold=True))
    # пунктирна червона рамка «десь тут» довкола всього рядка
    f.append(rect(x0 - 10, yB - ch / 2 - 10, rowW + 20, ch + 20,
                  fill="none", stroke=POS, sw=1.8, rx=10))
    f.append(draw_row(yB, [("1", "n"), ("0", "n"), ("0", "n"),
                           ("1", "n"), ("0", "n"), ("1", "parity")]))
    f.append(text(x0 - 26, yB + 9, "?", 26, POS, "middle", bold=True))
    f.append(mtext(xann, yB - 12,
                   ["рядок має «правильний» вигляд", "парність не збіглась → помилка Є", "але ДЕ? виправити не можна ✗"],
                   12, INK, anchor="start"))
    f.append(text(xann, yB + 30, "✗", 15, POS, "start", bold=True))

    # підписи «дані / парність» під нижнім рядком
    xdiv = x0 + 5 * (cw + gp) - gp / 2
    f.append(line(xdiv, yB + ch / 2 + 14, xdiv, yB + ch / 2 + 26, color=MUTED, sw=1.2))
    f.append(text(x0 + 2.5 * (cw + gp) - gp / 2, yB + ch / 2 + 40, "дані (5 біт)", 11, MUTED, "middle"))
    f.append(text(x0 + 5.5 * (cw + gp) - gp / 2, yB + ch / 2 + 40, "парність", 11, MUTED, "middle"))

    # підсумок — два рядки по центру
    f.append(text(W / 2, 372, "та сама надлишковість (1 біт парності): стирання виправляється, помилку — ні",
                  12.5, INK, "middle", bold=True))
    f.append(text(W / 2, 394, "загалом код із мінімальною відстанню d долає d − 1 стирань, але лише (d − 1) ∕ 2 помилок",
                  12, MUTED, "middle"))
    render(os.path.join(IMG, "erasure-vs-error.svg"), W, H, *f,
           title="Стирання проти помилки: відома позиція проти невідомої")


# ── 3. Атрибуція: документований доробок Еліаса проти фолклорної приписки ──────
# Ідея, яку важко словами: усе, що ТОЧНО зафіксовано за Еліасом у ці роки, —
# під віссю суцільними вузлами; а «канал зі стиранням» висить над віссю окремою
# рамкою з «?», бо жодне першоджерело його сюди не ставить. Пунктир до 1955 —
# саме той рік, у який приписку зазвичай кидають.
def fig_elias_timeline():
    W, H = 980, 432
    axisY = 250
    xL, xR = 66, 902
    centers = [210, 500, 790]
    years = ["1954", "1955", "1957"]
    f = []

    # ── фолклорна рамка над віссю, прив'язана до 1955 ──
    fbx, fby, fbw, fbh = 500, 112, 396, 104
    f.append(line(fbx, fby + fbh / 2, centers[1], axisY - 11,
                  color=POS, sw=1.7, dash="6 5"))
    f.append(rect(fbx - fbw / 2, fby - fbh / 2, fbw, fbh,
                  fill="#fdecea", stroke=POS, sw=2.2, rx=11))
    f.append(text(fbx - fbw / 2 + 30, fby - fbh / 2 + 34, "?", 34, POS, "middle", bold=True))
    f.append(text(fbx + 14, fby - 28, "«канал зі стиранням»", 16, POS, "middle", bold=True))
    f.append(mtext(fbx + 14, fby - 4,
                   ["приписують Еліасу (~1955), проте жодне",
                    "першоджерело цього не фіксує;",
                    "Wikipedia донині — «citation needed»"],
                   12.5, INK, anchor="middle"))

    # ── вісь часу ──
    f.append(line(xL, axisY, xR - 4, axisY, color=INK, sw=2.4))
    f.append(arrow(xR - 6, axisY, xR + 12, axisY, color=INK, sw=2.4))
    f.append(text(xR + 4, axisY - 13, "час", 11, MUTED, "middle"))

    # ── документовані вузли під віссю ──
    boxes = [
        ["«Error-Free Coding»", "продукт-коди +", "ітеративне декодування"],
        ["«Coding for Noisy Channels»", "двійковий СИМЕТРИЧНИЙ канал:", "випадкове кодування · згорткові коди"],
        ["«List Decoding for Noisy Channels»", "декодування списком", "(вибір не з одного слова, а зі списку)"],
    ]
    bw, bh = 274, 100
    for cx, yr, lines in zip(centers, years, boxes):
        f.append(circle(cx, axisY, 9, fill=BG, stroke=INK, sw=2.6))
        f.append(circle(cx, axisY, 3.2, fill=INK, stroke=INK, sw=0))
        # рік — ПІД віссю, щоб пунктирний зв'язок згори не перетинав напис
        f.append(text(cx, axisY + 26, yr, 17, INK, "middle", bold=True))
        f.append(fitbox(cx - bw / 2, axisY + 40, bw, bh, "\n".join(lines),
                        size=12.5, fill=FILL, stroke=LINE, color=INK, bold=False))

    f.append(text(W / 2, H - 14,
                  "суцільне — зафіксовано першоджерелами; над віссю — усно повторювана приписка без цитати",
                  12, MUTED, "middle"))
    render(os.path.join(IMG, "elias-timeline.svg"), W, H, *f,
           title="Доробок Еліаса середини 1950-х — і приписка, якої в ньому немає")


# ── 4. Ядро відновлення: перевірна матриця розпадається на дві частини ────────
# Ідея, яку важко словами: стерті позиції ВІДОМІ, тож із усієї перевірної
# матриці лишається маленька система Hₑ·x = s — стовпці над відомими бітами
# переносяться у праву частину, над стертими стають єдиними невідомими.
# Конкретика: код Геммінга(7,4), кодове 1 0 1 1 1 0 0, стерто позиції 0,1,2.
def fig_recovery_split():
    W, H = 900, 470
    Hm = [[1, 0, 1, 1, 1, 0, 0],
          [1, 1, 1, 0, 0, 1, 0],
          [0, 1, 1, 1, 0, 0, 1]]
    erased = {0, 1, 2}
    recv = ["?", "?", "?", "1", "1", "0", "0"]
    cw = 34
    f = []

    # ── ліворуч: повна перевірна матриця H, стовпці розфарбовано ──
    xL, yL = 66, 100
    f.append(text(xL + 7 * cw / 2, 76, "перевірна матриця H  (3 × 7)", 13.5, INK, "middle", bold=True))
    for cq in range(7):
        col = "#fdecea" if cq in erased else "#eef2f7"
        f.append(text(xL + cq * cw + cw / 2, yL - 9, str(cq), 10.5, MUTED, "middle"))
        for r in range(3):
            x = xL + cq * cw
            y = yL + r * cw
            f.append(rect(x, y, cw, cw, fill=col, stroke=LINE, sw=1.1, rx=3))
            f.append(text(x + cw / 2, y + cw / 2 + 6, str(Hm[r][cq]), 16, INK, "middle"))
    # прийнятий рядок під матрицею
    yr = yL + 3 * cw + 16
    f.append(text(xL - 12, yr + cw / 2 + 6, "прийнято", 11.5, MUTED, "end"))
    for cq in range(7):
        x = xL + cq * cw
        er = cq in erased
        f.append(rect(x, yr, cw, cw, fill="#fdecea" if er else BG,
                      stroke=POS if er else LINE, sw=2.0 if er else 1.1, rx=3))
        f.append(text(x + cw / 2, yr + cw / 2 + 7, recv[cq], 18,
                      POS if er else INK, "middle", bold=er))
    # короткі підписи-групи під рядком
    ybr = yr + cw + 15
    f.append(line(xL, ybr, xL + 3 * cw, ybr, color=POS, sw=1.6))
    f.append(text(xL + 1.5 * cw, ybr + 16, "стерті → x", 11, POS, "middle", bold=True))
    f.append(line(xL + 3 * cw, ybr, xL + 7 * cw, ybr, color=MUTED, sw=1.6))
    f.append(text(xL + 5 * cw, ybr + 16, "відомі → праворуч", 11, MUTED, "middle"))

    # ── стрілка переносу ──
    ay = yL + 1.5 * cw
    f.append(arrow(xL + 7 * cw + 18, ay, xL + 7 * cw + 96, ay, color=INK, sw=2.2))
    f.append(text(xL + 7 * cw + 57, ay - 12, "переносимо", 10.5, INK, "middle"))
    f.append(text(xL + 7 * cw + 57, ay + 22, "відоме праворуч", 10.5, INK, "middle"))

    # ── праворуч: зведена система Hₑ · x = s ──
    HE = [[Hm[r][cq] for cq in (0, 1, 2)] for r in range(3)]
    xR = xL + 7 * cw + 124
    f.append(text(xR + 1.5 * cw + 64, 76, "зведена система  Hₑ · x = s", 13.5, INK, "middle", bold=True))
    for cq in range(3):
        for r in range(3):
            x = xR + cq * cw
            y = yL + r * cw
            f.append(rect(x, y, cw, cw, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
            f.append(text(x + cw / 2, y + cw / 2 + 6, str(HE[r][cq]), 16, INK, "middle"))
    xx = xR + 3 * cw + 16
    f.append(text(xx - 8, ay + 7, "·", 22, INK, "middle", bold=True))
    xv = ["x₀", "x₁", "x₂"]
    for r in range(3):
        y = yL + r * cw
        f.append(rect(xx, y, cw, cw, fill=BG, stroke=NEG, sw=1.6, rx=3))
        f.append(text(xx + cw / 2, y + cw / 2 + 6, xv[r], 14, NEG, "middle", bold=True))
    xe = xx + cw + 14
    f.append(text(xe - 5, ay + 7, "=", 22, INK, "middle", bold=True))
    xs = xe + 12
    sv = ["0", "0", "1"]
    for r in range(3):
        y = yL + r * cw
        f.append(rect(xs, y, cw, cw, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=3))
        f.append(text(xs + cw / 2, y + cw / 2 + 6, sv[r], 16, INK, "middle"))
    f.append(text(xs + cw / 2, yr + cw / 2 + 6, "s = внесок відомих бітів", 10.5, MUTED, "middle"))
    f.append(text(xR + 1.5 * cw + 30, ybr + 16,
                  "розв'язок над GF(2):  x = (1, 0, 1)  ✓", 11.5, FIELD, "middle", bold=True))

    f.append(fitbox(60, 436, W - 120, 26,
                    "над GF(2) додавання — це XOR, тож «−» те саме, що «+»; лишається розв'язати 3 рівняння з 3 невідомими методом Гаусса",
                    size=11.5, fill=FILL, stroke=LINE, color=INK))
    render(os.path.join(IMG, "erasure-recovery-split.svg"), W, H, *f,
           title="Стерті позиції відомі → лишається маленька лінійна система")


# ── 5. Три режими відновлюваності за числом стирань ───────────────────────────
# Ідея, яку важко словами: до d−1 стирань код латає ЗАВЖДИ; у вікні (d−1, n−k]
# як пощастить зі стовпцями; за n−k — глуха стіна (система недовизначена).
# Приклад — Геммінг(7,4): d−1 = 2, n−k = 3, тож вікно — лише e = 3.
def fig_recovery_regimes():
    W, H = 820, 336
    f = []
    cw, ch = 80, 52
    x0, y0 = 40, 96

    def zone(e):
        if e <= 2:
            return "#eef6ef", FIELD
        if e == 3:
            return "#fff4e5", "#e08a00"
        return "#fdecea", POS

    for e in range(8):
        fill, st = zone(e)
        x = x0 + e * cw
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=st, sw=1.8, rx=6))
        f.append(text(x + cw / 2, y0 + ch / 2 + 3, "e = %d" % e, 15, INK, "middle", bold=True))

    # порогові позначки на межах клітинок
    yb = y0 + ch
    x_d = x0 + 3 * cw
    f.append(line(x_d, y0 - 8, x_d, yb + 8, color=FIELD, sw=1.6, dash="4 3"))
    f.append(text(x_d, yb + 24, "гарантія  d − 1 = 2", 11, FIELD, "middle", bold=True))
    x_nk = x0 + 4 * cw
    f.append(line(x_nk, y0 - 8, x_nk, yb + 8, color=POS, sw=1.6, dash="4 3"))
    f.append(text(x_nk, yb + 42, "стеля  n − k = 3", 11, POS, "middle", bold=True))

    def swatch(x, y, fill, st):
        return rect(x, y - 11, 20, 20, fill=fill, stroke=st, sw=1.8, rx=4)

    ylg = 228
    f.append(swatch(60, ylg, "#eef6ef", FIELD))
    f.append(text(90, ylg + 5, "e = 0, 1, 2  —  завжди відновлюється (до d − 1 стирань код латає гарантовано)", 12, INK, "start"))
    f.append(swatch(60, ylg + 30, "#fff4e5", "#e08a00"))
    f.append(text(90, ylg + 35, "e = 3  —  залежить від стовпців: 28 із 35 трійок ✓,  7 (прямі Фано) ✗", 12, INK, "start"))
    f.append(swatch(60, ylg + 60, "#fdecea", POS))
    f.append(text(90, ylg + 65, "e ≥ 4  —  неможливо: стирань більше за надлишковість n − k = 3, система недовизначена", 12, INK, "start"))

    render(os.path.join(IMG, "erasure-recovery-regimes.svg"), W, H, *f,
           title="Скільки стирань код витягне: поріг, вікно, глуха стіна")


if __name__ == "__main__":
    fig_channel_law()
    fig_erasure_vs_error()
    fig_elias_timeline()
    fig_recovery_split()
    fig_recovery_regimes()
    print("OK: figures written to", IMG)
