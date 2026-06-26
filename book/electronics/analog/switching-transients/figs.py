# -*- coding: utf-8 -*-
"""Фігури до теми «Перехідні процеси в ключах».
Чотири фігури:
  ideal-vs-real.svg   — ідеальний прямокутник проти реального фронту з дзвоном
  lc-distortion.svg   — C розмазує фронт, L+C дають викид і дзвін
  two-pitfalls.svg    — наскрізний струм у парі ключів + стрибок землі
  switching-loss.svg  — сплеск потужності в момент переходу (перекриття U й I)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def axes(x0, y0, w, h, xlabel, ylabel):
    """Осі: горизонтальна (час) і вертикальна. x0,y0 — лівий нижній кут."""
    out = [line(x0, y0, x0 + w, y0, color=MUTED, sw=1.5),          # вісь часу
           line(x0, y0, x0, y0 - h, color=MUTED, sw=1.5)]          # вісь величини
    out.append(text(x0 + w, y0 + 16, xlabel, size=11, color=MUTED, anchor="end"))
    out.append(text(x0 - 6, y0 - h, ylabel, size=11, color=MUTED, anchor="end"))
    return "".join(out)


# ── 1. Ідеальний стрибок проти реального ────────────────────────────────────
def fig_ideal_vs_real():
    W, H = 720, 330
    title = "Ключ: ідеал на схемі проти осцилографа"
    parts = []

    # ── лівий графік: ідеальний прямокутний спад ──
    x0, y0, gw, gh = 70, 250, 230, 170
    top, bot = y0 - gh, y0
    parts.append(axes(x0, y0, gw, gh, "час", "U"))
    # рівень «1» зліва, миттєвий вертикальний спад посередині, рівень «0» далі
    xmid = x0 + gw * 0.5
    ideal = [(x0, top + 12), (xmid, top + 12), (xmid, bot - 4), (x0 + gw, bot - 4)]
    parts.append(polyline(ideal, color=NEG, sw=2.6))
    parts.append(text(x0 + gw / 2, top - 8, "ідеальний ключ", size=13, bold=True))
    parts.append(text(xmid + 8, top + 26, "миттєвий", size=11, color=NEG, anchor="start"))
    parts.append(text(xmid + 8, top + 40, "стрибок", size=11, color=NEG, anchor="start"))

    # ── правий графік: реальний фронт із нахилом і дзвоном ──
    x1, y1, gw2, gh2 = 430, 250, 250, 170
    top2, bot2 = y1 - gh2, y1
    parts.append(axes(x1, y1, gw2, gh2, "час", "U"))
    parts.append(text(x1 + gw2 / 2, top2 - 8, "реальний ключ", size=13, bold=True))
    # будуємо: плато вгорі, похилий спад, викид (нижній рівень не на дні, щоб дзвін
    # коливався навколо нього й не вилазив нижче осі), згасальний дзвін, осідання
    pts = []
    xa = x1 + 10
    xfall0 = x1 + gw2 * 0.34      # початок фронту
    xfall1 = x1 + gw2 * 0.52      # кінець нахилу
    base = bot2 - 26             # нижній усталений рівень — над віссю на запас дзвону
    A = 22.0                     # амплітуда дзвону (макс. трохи нижче осі, але вище неї)
    for xx in range(int(xa), int(xfall0)):
        pts.append((xx, top2 + 12))
    # похилий спад до нижнього рівня
    for xx in range(int(xfall0), int(xfall1)):
        f = (xx - xfall0) / (xfall1 - xfall0)
        pts.append((xx, top2 + 12 + f * (base - (top2 + 12))))
    # дзвін навколо нижнього рівня (перший викид — донизу, але не нижче осі)
    for xx in range(int(xfall1), int(x1 + gw2 - 4)):
        t = (xx - xfall1) / 22.0
        y = base + A * math.exp(-t * 0.5) * math.cos(t * 2.4)
        pts.append((xx, min(y, bot2 - 2)))
    parts.append(polyline(pts, color=POS, sw=2.6))
    # рівень усталення (пунктир) — щоб видно було, навколо чого гойдається
    parts.append(line(xfall1, base, x1 + gw2 - 4, base, color=MUTED, sw=1.0, dash="4,4"))
    # позначка нахилу (час спаду) — усередині поля, під фронтом
    parts.append(line(xfall0, base + 14, xfall1, base + 14, color=MUTED, sw=1.2))
    parts.append(text((xfall0 + xfall1) / 2, base + 28, "час спаду", size=11, color=MUTED))
    # позначка викиду/дзвону
    parts.append(text(xfall1 + 78, top2 + 40, "викид + дзвін", size=11, color=POS, anchor="middle"))
    parts.append(arrow(xfall1 + 78, top2 + 48, xfall1 + 26, base + A - 2, color=MUTED, sw=1.4))

    render(os.path.join(IMG, "ideal-vs-real.svg"), W, H, *parts, title=title)


# ── 2. Як L і C спотворюють фронт ───────────────────────────────────────────
def fig_lc_distortion():
    W, H = 720, 340
    title = "Два винуватці: ємність розмазує, індуктивність дзвенить"
    parts = []

    # ── лівий: лише C — гладка експонента ──
    x0, y0, gw, gh = 70, 255, 235, 175
    top, bot = y0 - gh, y0
    parts.append(axes(x0, y0, gw, gh, "час", "U"))
    parts.append(text(x0 + gw / 2, top - 8, "тільки ємність C", size=13, bold=True))
    base = bot - 4
    pts = []
    xa = x0 + 10
    xstep = x0 + gw * 0.28
    for xx in range(int(xa), int(xstep)):
        pts.append((xx, top + 12))
    for xx in range(int(xstep), int(x0 + gw - 4)):
        t = (xx - xstep) / 26.0
        y = base - (base - (top + 12)) * math.exp(-t)
        pts.append((xx, y))
    parts.append(polyline(pts, color=NEG, sw=2.6))
    parts.append(text(x0 + gw * 0.7, top + 60, "плавна", size=11, color=NEG))
    parts.append(text(x0 + gw * 0.7, top + 74, "експонента", size=11, color=NEG))
    parts.append(text(x0 + gw * 0.7, top + 88, "τ = R·C", size=12, color=INK, bold=True))

    # ── правий: L + C — викид і згасальний дзвін ──
    x1, y1, gw2, gh2 = 430, 255, 250, 175
    top2, bot2 = y1 - gh2, y1
    parts.append(axes(x1, y1, gw2, gh2, "час", "U"))
    parts.append(text(x1 + gw2 / 2, top2 - 8, "індуктивність L + ємність C", size=13, bold=True))
    base2 = top2 + 14            # новий «високий» рівень, до якого летимо
    final = base2
    pts2 = []
    xa2 = x1 + 10
    xstep2 = x1 + gw2 * 0.24
    start_lvl = bot2 - 6
    for xx in range(int(xa2), int(xstep2)):
        pts2.append((xx, start_lvl))
    A = 40.0
    for xx in range(int(xstep2), int(x1 + gw2 - 4)):
        t = (xx - xstep2) / 16.0
        # підйом до final з викидом понад нього й згасанням
        y = final - (final - start_lvl) * 0  # final base
        env = math.exp(-t * 0.5)
        y = final - A * env * math.cos(t * 2.2)
        # на t=0 cos=1 → final - A (нижче? ні: final малий y=верх). Лишаємо так: коливання навколо final.
        pts2.append((xx, y))
    parts.append(polyline(pts2, color=POS, sw=2.6))
    # лінія цільового рівня
    parts.append(line(xstep2, final, x1 + gw2 - 4, final, color=MUTED, sw=1.0, dash="4,4"))
    parts.append(text(x1 + gw2 - 8, final - 6, "цільовий рівень", size=10, color=MUTED, anchor="end"))
    parts.append(text(x1 + gw2 * 0.46, final - A - 6, "викид", size=11, color=POS))
    parts.append(text(x1 + gw2 * 0.74, final + 30, "дзвін згасає на R", size=11, color=POS))

    render(os.path.join(IMG, "lc-distortion.svg"), W, H, *parts, title=title)


# ── 3. Дві пастки: наскрізний струм і стрибок землі ─────────────────────────
def fig_two_pitfalls():
    W, H = 730, 360
    title = "Дві біди переходу"
    parts = []

    # ── ЛІВО: піврядок ключів — наскрізний струм ──
    cx = 175
    vtop = 70
    parts.append(text(cx, 56, "наскрізний струм", size=13, bold=True))
    # шина «+»
    parts.append(line(cx - 70, vtop, cx + 70, vtop, color=POS, sw=2.4))
    parts.append(text(cx + 78, vtop + 4, "+", size=16, color=POS, bold=True, anchor="start"))
    # верхній ключ (рамка)
    parts.append(fitbox(cx - 38, vtop + 24, 76, 40, "верхній\nключ", size=12,
                        fill="#fdecea", stroke=POS))
    # середній вузол
    ymid = vtop + 24 + 40
    parts.append(line(cx, vtop, cx, vtop + 24, color=INK, sw=2))
    nodey = ymid + 26
    parts.append(line(cx, ymid, cx, nodey, color=INK, sw=2))
    parts.append(circle(cx, nodey, 3.5, fill=INK, stroke=INK))
    parts.append(text(cx + 12, nodey + 4, "вихід", size=11, color=MUTED, anchor="start"))
    # нижній ключ
    parts.append(line(cx, nodey, cx, nodey + 24, color=INK, sw=2))
    parts.append(fitbox(cx - 38, nodey + 24, 76, 40, "нижній\nключ", size=12,
                        fill="#eaf0fd", stroke=NEG))
    # земля
    gy = nodey + 24 + 40 + 22
    parts.append(line(cx, nodey + 64, cx, gy, color=INK, sw=2))
    parts.append(line(cx - 16, gy, cx + 16, gy, color=INK, sw=2.6))
    parts.append(line(cx - 10, gy + 5, cx + 10, gy + 5, color=INK, sw=2))
    parts.append(line(cx - 4, gy + 10, cx + 4, gy + 10, color=INK, sw=2))
    # червона стрілка наскрізного струму
    parts.append(arrow(cx + 46, vtop + 8, cx + 46, gy - 6, color=POS, sw=2.4))
    parts.append(text(cx + 54, (vtop + gy) / 2, "обидва", size=11, color=POS, anchor="start"))
    parts.append(text(cx + 54, (vtop + gy) / 2 + 14, "на мить", size=11, color=POS, anchor="start"))
    parts.append(text(cx + 54, (vtop + gy) / 2 + 28, "відкриті", size=11, color=POS, anchor="start"))

    # ── ПРАВО: стрибок землі ──
    bx = 520
    parts.append(text(bx, 56, "стрибок землі", size=13, bold=True))
    # мікросхема-ключ зверху
    parts.append(fitbox(bx - 60, 72, 120, 42, "ключ комутує\nвеликий струм", size=11,
                        fill=FILL, stroke=LINE))
    # вивід-індуктивність донизу (котушка-зигзаг)
    coil_x = bx
    cy0 = 114
    cy1 = 188
    parts.append(line(coil_x, cy0, coil_x, cy0 + 8, color=INK, sw=2))
    # зигзаг індуктивності
    zig = [(coil_x, cy0 + 8)]
    n = 4
    for i in range(n):
        yy = cy0 + 8 + (cy1 - cy0 - 16) * (i + 0.5) / n
        dx = 9 if i % 2 == 0 else -9
        zig.append((coil_x + dx, yy))
    zig.append((coil_x, cy1 - 8))
    parts.append(polyline(zig, color=INK, sw=2))
    parts.append(line(coil_x, cy1 - 8, coil_x, cy1, color=INK, sw=2))
    parts.append(text(coil_x + 16, (cy0 + cy1) / 2, "L виводу", size=11, color=MUTED, anchor="start"))
    parts.append(text(coil_x + 16, (cy0 + cy1) / 2 + 14, "U = L·di/dt", size=11, color=POS, anchor="start"))
    # вузол локальної «землі» (підстрибує)
    parts.append(circle(coil_x, cy1, 3.5, fill=POS, stroke=POS))
    parts.append(text(coil_x - 12, cy1 + 4, "локальна", size=10, color=POS, anchor="end"))
    parts.append(text(coil_x - 12, cy1 + 17, "«земля» ↑", size=10, color=POS, anchor="end"))
    # справжня земля нижче
    gy2 = cy1 + 40
    parts.append(line(coil_x, cy1, coil_x, gy2, color=INK, sw=2))
    parts.append(line(coil_x - 16, gy2, coil_x + 16, gy2, color=INK, sw=2.6))
    parts.append(line(coil_x - 10, gy2 + 5, coil_x + 10, gy2 + 5, color=INK, sw=2))
    parts.append(line(coil_x - 4, gy2 + 10, coil_x + 4, gy2 + 10, color=INK, sw=2))
    # сусідній чутливий вхід, прив'язаний до тієї ж локальної землі
    inx = bx + 95
    parts.append(line(coil_x, cy1, inx, cy1, color=NEG, sw=1.8))
    parts.append(fitbox(inx - 6, cy1 - 22, 70, 44, "сусідній\nвхід бачить\nхибний рівень", size=10,
                        fill="#eaf0fd", stroke=NEG))

    render(os.path.join(IMG, "two-pitfalls.svg"), W, H, *parts, title=title)


# ── 4. Сплеск потужності в момент переходу ──────────────────────────────────
def fig_switching_loss():
    W, H = 700, 340
    title = "Тепло народжується в момент переходу"
    parts = []

    x0, y0, gw, gh = 70, 260, 580, 200
    top, bot = y0 - gh, y0
    parts.append(axes(x0, y0, gw, gh, "час", ""))

    # координати переходу
    xon0 = x0 + gw * 0.40     # початок фронту
    xon1 = x0 + gw * 0.56     # кінець фронту
    hi = top + 30             # «високий» рівень для U
    lo = bot - 6              # нуль

    # U(t): висока, спадає під час фронту до ~нуля
    u = []
    for xx in range(int(x0 + 6), int(xon0)):
        u.append((xx, hi))
    for xx in range(int(xon0), int(xon1)):
        f = (xx - xon0) / (xon1 - xon0)
        u.append((xx, hi + f * (lo - 8 - hi)))
    for xx in range(int(xon1), int(x0 + gw - 4)):
        u.append((xx, lo - 8))
    parts.append(polyline(u, color=NEG, sw=2.4))
    parts.append(text(x0 + 10, hi - 8, "U на ключі", size=12, color=NEG, anchor="start", bold=True))

    # I(t): нульова, наростає під час фронту до високого рівня
    cur = []
    ihi = top + 60
    for xx in range(int(x0 + 6), int(xon0)):
        cur.append((xx, lo - 2))
    for xx in range(int(xon0), int(xon1)):
        f = (xx - xon0) / (xon1 - xon0)
        cur.append((xx, lo - 2 + f * (ihi - (lo - 2))))
    for xx in range(int(xon1), int(x0 + gw - 4)):
        cur.append((xx, ihi))
    parts.append(polyline(cur, color=POS, sw=2.4))
    parts.append(text(x0 + gw - 8, ihi - 10, "I крізь ключ", size=12, color=POS, anchor="end", bold=True))

    # P = U·I: горб лише в зоні перекриття
    p = []
    for xx in range(int(x0 + 6), int(x0 + gw - 4)):
        # нормовані U і I в [0..1]
        if xx < xon0:
            uu, ii = 1.0, 0.0
        elif xx < xon1:
            f = (xx - xon0) / (xon1 - xon0)
            uu, ii = 1.0 - f, f
        else:
            uu, ii = 0.0, 1.0
        pw = uu * ii            # максимум 0.25 у середині
        y = bot - pw * (gh * 1.6)   # масштаб горба
        p.append((xx, y))
    parts.append(polyline(p, color=FIELD, sw=3.0))
    # заливка горба потужності
    fill_pts = [(x0 + 6, bot)] + p + [(x0 + gw - 4, bot)]
    fill_poly = " ".join("%.1f,%.1f" % (x, y) for x, y in fill_pts)
    parts.append('<polygon points="%s" fill="%s" opacity="0.18"/>' % (fill_poly, FIELD))
    # підпис горба
    xmidp = (xon0 + xon1) / 2
    parts.append(text(xmidp, top + 8, "P = U·I", size=13, color=FIELD, bold=True))
    parts.append(text(xmidp, top + 24, "сплеск тепла", size=11, color=FIELD))

    # зони сталих станів
    parts.append(text((x0 + xon0) / 2, bot + 18, "вимкнено: U є, I=0 → P≈0", size=10, color=MUTED))
    parts.append(text((xon1 + x0 + gw) / 2, bot + 18, "ввімкнено: I є, U≈0 → P≈0", size=10, color=MUTED))
    # вертикальні межі фронту
    parts.append(line(xon0, top + 4, xon0, bot, color=MUTED, sw=1.0, dash="3,3"))
    parts.append(line(xon1, top + 4, xon1, bot, color=MUTED, sw=1.0, dash="3,3"))

    render(os.path.join(IMG, "switching-loss.svg"), W, H, *parts, title=title)


if __name__ == "__main__":
    fig_ideal_vs_real()
    fig_lc_distortion()
    fig_two_pitfalls()
    fig_switching_loss()
    print("OK: 4 figures ->", IMG)
