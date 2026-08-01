# -*- coding: utf-8 -*-
"""Фігури до теми «Хвильове рівняння».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

STR = "#1a1a1a"    # струна / крива — чорне, товсте
TEN = "#2457d6"    # натяг — синє
RES = "#c0392b"    # рівнодійна / прискорення — червоне
ACC = "#c0392b"
ENV = "#c0392b"
GRID = "#e6e9ee"
GHOST = "#b9c0ca"  # знімки-привиди


def poly(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


# ── Фігура 1: пряма ділянка гасить натяг, вигнута — ні ────────────────────────
def fig_string_forces():
    W, H = 1020, 540
    f = [text(W / 2, 32, "Сила народжується вигином, не відхиленням", size=17, bold=True)]

    # ── лівий панель: пряма ділянка ──
    ox = 60
    f.append(text(ox + 200, 78, "пряма ділянка", size=15, bold=True))
    yb = 250
    xa, xb = ox + 40, ox + 360
    f.append(line(xa, yb, xb, yb, color=STR, sw=3.4))
    # дві точки-кінці шматочка
    xL, xR = ox + 130, ox + 270
    for xx in (xL, xR):
        f.append(circle(xx, yb, 4.5, fill=STR, stroke=STR, sw=1))
    # натяг уздовж прямої: ліворуч і праворуч по одній лінії
    f.append(arrow(xL, yb, xL - 78, yb, color=TEN, sw=2.6))
    f.append(arrow(xR, yb, xR + 78, yb, color=TEN, sw=2.6))
    f.append(text(xL - 82, yb - 12, "T", size=15, bold=True, color=TEN, anchor="end"))
    f.append(text(xR + 82, yb - 12, "T", size=15, bold=True, color=TEN, anchor="start"))
    f.append(text(ox + 200, yb + 46, "тяги вздовж однієї прямої", size=12.5, color=MUTED))
    f.append(text(ox + 200, yb + 68, "— поперечна рівнодійна = 0", size=12.5, bold=True, color=STR))

    # роздільник
    f.append(line(W / 2, 96, W / 2, 470, color=GRID, sw=1.6))

    # ── правий панель: вигнута ділянка (горб) ──
    ox2 = 540
    f.append(text(ox2 + 210, 78, "вигнута ділянка", size=15, bold=True))
    ybR = 300
    A = 96
    s = 150.0
    cx = ox2 + 210
    xa2, xb2 = ox2 + 30, ox2 + 390

    def hump(x):
        return ybR - A * math.exp(-((x - cx) / s) ** 2)

    arc = [(x, hump(x)) for x in range(int(xa2), int(xb2) + 1, 3)]
    f.append(poly(arc, color=STR, sw=3.4))

    # кінці шматочка — на схилах горба
    xL2, xR2 = cx - 96, cx + 96
    yL2, yR2 = hump(xL2), hump(xR2)
    for xx, yy in ((xL2, yL2), (xR2, yR2)):
        f.append(circle(xx, yy, 4.5, fill=STR, stroke=STR, sw=1))

    # дотичні напрямки (натяг тягне НАЗОВНІ вздовж струни)
    def tangent(x):
        h = 1.0
        return (hump(x + h) - hump(x - h)) / (2 * h)  # dy/dx на екрані

    for xx, yy, sgn in ((xL2, yL2, -1), (xR2, yR2, +1)):
        m = tangent(xx)
        L = 92
        dx = sgn * L / math.sqrt(1 + m * m)
        dy = m * dx
        f.append(arrow(xx, yy, xx + dx, yy + dy, color=TEN, sw=2.6))
    f.append(text(xL2 - 74, yL2 + 6, "T", size=15, bold=True, color=TEN, anchor="end"))
    f.append(text(xR2 + 74, yR2 + 6, "T", size=15, bold=True, color=TEN, anchor="start"))

    # рівнодійна вниз під вершиною
    f.append(arrow(cx, hump(cx) - 4, cx, hump(cx) + 74, color=RES, sw=3.2))
    f.append(text(cx + 14, hump(cx) + 52, "рівнодійна", size=13, bold=True, color=RES, anchor="start"))
    f.append(text(ox2 + 210, ybR + 92, "поперечні складники не гасяться", size=12.5, color=MUTED))
    f.append(text(ox2 + 210, ybR + 114, "— лишається сила до випрямлення", size=12.5, bold=True, color=RES))

    render(os.path.join(IMG, "string-forces.svg"), W, H, *f)


# ── Фігура 2: кривина керує прискоренням у кожній точці ───────────────────────
def fig_curvature_acceleration():
    W, H = 1020, 470
    f = [text(W / 2, 32, "Рівняння читається так: прискорення = c²·(кривина) — завжди до рівноваги",
              size=15.5, bold=True)]
    xa, xb = 90, 930
    yc = 250
    A = 120
    cyc = 2.0
    n = 300

    def yof(u):
        return yc - A * math.sin(2 * math.pi * cyc * u)

    # вісь рівноваги
    f.append(line(xa - 10, yc, xb + 10, yc, color=GRID, sw=1.4))
    f.append(text(xb + 16, yc + 4, "рівновага", size=11.5, color=MUTED, anchor="start"))

    # крива
    curve = [(xa + i / n * (xb - xa), yof(i / n)) for i in range(n + 1)]
    f.append(poly(curve, color=STR, sw=3.2))

    # стрілки прискорення в вибраних точках: завжди до осі, довжина ∝ |відхилення|
    for j in range(1, 16):
        u = j / 16.0
        x = xa + u * (xb - xa)
        y = yof(u)
        disp = yc - y  # + якщо горб угорі
        if abs(disp) < 6:
            continue
        # прискорення напрямлене до осі: якщо горб угорі (y<yc), стрілка вниз
        tip = y + (0.42 * disp)      # тягне назад до осі
        f.append(arrow(x, y, x, tip, color=ACC, sw=2.4))

    # підписи горб / западина / перегин (на справжніх гребені та западині)
    f.append(text(xa + 0.625 * (xb - xa), yof(0.625) - 20, "горб: угнута ↓  →  прискорення вниз",
                  size=12.5, bold=True, color=ACC))
    f.append(text(xa + 0.375 * (xb - xa), yof(0.375) + 34, "западина: угнута ↑  →  прискорення вгору",
                  size=12.5, bold=True, color=ACC))
    # точка перегину
    xz = xa + 0.5 * (xb - xa)
    f.append(circle(xz, yc, 5, fill="none", stroke=MUTED, sw=1.8))
    f.append(text(xz, yc - 14, "перегин: кривина 0 → прискорення 0", size=11.5, color=MUTED))

    render(os.path.join(IMG, "curvature-acceleration.svg"), W, H, *f)


# ── Фігура 3: розв'язок д'Аламбера — форма біжить; сума двох напрямів ─────────
def fig_dalembert():
    W, H = 1020, 600
    f = [text(W / 2, 30, "Розв'язок д'Аламбера: будь-яка форма біжить зі швидкістю c, не міняючись",
              size=15.5, bold=True)]
    xa, xb = 80, 940
    sig = 30.0

    def bump(x, c, h=64):
        return h * math.exp(-((x - c) / sig) ** 2)

    # ── верх: та сама форма f у три миті, зсунута праворуч ──
    yb = 150
    f.append(text(xa, 74, "f(x − c·t): одна форма, три послідовні миті", size=13.5, bold=True, anchor="start"))
    f.append(line(xa, yb, xb, yb, color=GRID, sw=1.3))
    centres = [(260, GHOST, "t"), (500, "#7f8a99", "t + Δt"), (740, STR, "t + 2Δt")]
    for c, col, lab in centres:
        pts = [(x, yb - bump(x, c)) for x in range(int(xa), int(xb) + 1, 3)]
        f.append(poly(pts, color=col, sw=2.6 if col == STR else 2.0))
        f.append(text(c, yb - bump(c, c) - 12, lab, size=12, color=col if col != GHOST else MUTED, bold=(col == STR)))
    f.append(arrow(300, yb + 40, 700, yb + 40, color=STR, sw=2.2))
    f.append(text(500, yb + 34, "зсув на c·Δt за кожен крок", size=12.5, bold=True))

    # роздільник
    f.append(line(xa, 300, xb, 300, color=GRID, sw=1.2))

    # ── низ: загальний розв'язок f(x−ct) + g(x+ct) ──
    yb2 = 440
    f.append(text(xa, 356, "загальний розв'язок: правобіжна f(x − c·t)  +  лівобіжна g(x + c·t)",
                  size=13.5, bold=True, anchor="start"))
    f.append(line(xa, yb2, xb, yb2, color=GRID, sw=1.3))
    cR, cL = 360, 640

    def bumpR(x):
        return 62 * math.exp(-((x - cR) / sig) ** 2)

    def bumpL(x):
        return 50 * math.exp(-((x - cL) / 26.0) ** 2)

    ptsR = [(x, yb2 - bumpR(x)) for x in range(int(xa), int(xb) + 1, 3)]
    ptsL = [(x, yb2 - bumpL(x)) for x in range(int(xa), int(xb) + 1, 3)]
    summ = [(x, yb2 - bumpR(x) - bumpL(x)) for x in range(int(xa), int(xb) + 1, 3)]
    f.append(poly(ptsR, color=TEN, sw=1.8, dash="6,5"))
    f.append(poly(ptsL, color=RES, sw=1.8, dash="6,5"))
    f.append(poly(summ, color=STR, sw=3.0))
    f.append(arrow(cR - 40, yb2 + 40, cR + 40, yb2 + 40, color=TEN, sw=2.2))
    f.append(text(cR, yb2 + 60, "f біжить →", size=12, color=TEN))
    f.append(arrow(cL + 40, yb2 + 40, cL - 40, yb2 + 40, color=RES, sw=2.2))
    f.append(text(cL, yb2 + 60, "← біжить g", size=12, color=RES))
    f.append(text(W / 2, yb2 - 92, "чорне — їхня сума (те, що видно на струні)", size=12, color=MUTED))

    render(os.path.join(IMG, "dalembert.svg"), W, H, *f)


# ── Фігура 4: недисперсне тримає форму, дисперсне розпливається ───────────────
def fig_dispersion():
    W, H = 1020, 560
    f = [text(W / 2, 30, "Форма тримається лише коли c однакова для всіх частот", size=16, bold=True)]
    xa, xb = 80, 940
    n = 500
    span = xb - xa

    def packet(xc, width, amp, x):
        env = amp * math.exp(-((x - xc) / width) ** 2)
        return env * math.cos(2 * math.pi * (x - xc) / 26.0)

    # ── верх: недисперсне — той самий згусток, зсунутий, тієї ж ширини ──
    yb = 150
    f.append(text(xa, 74, "недисперсне (c однакова): згусток біжить, тримаючи форму",
                  size=13.5, bold=True, anchor="start", color=FIELD))
    f.append(line(xa, yb, xb, yb, color=GRID, sw=1.3))
    for xc, col in ((280, GHOST), (520, "#7f8a99"), (760, STR)):
        pts = [(xa + i / n * span, yb - packet(xc, 46, 70, xa + i / n * span)) for i in range(n + 1)]
        f.append(poly(pts, color=col, sw=2.4 if col == STR else 1.7))
    f.append(arrow(320, yb + 60, 720, yb + 60, color=FIELD, sw=2.2))
    f.append(text(520, yb + 54, "ширина стала", size=12.5, bold=True, color=FIELD))

    f.append(line(xa, 300, xb, 300, color=GRID, sw=1.2))

    # ── низ: дисперсне — згусток дедалі ширшає й нижчає ──
    yb2 = 450
    f.append(text(xa, 356, "дисперсне (c залежить від частоти): згусток розпливається",
                  size=13.5, bold=True, anchor="start", color=RES))
    f.append(line(xa, yb2, xb, yb2, color=GRID, sw=1.3))
    for xc, wdt, amp, col in ((280, 40, 74, GHOST), (520, 74, 54, "#a9576a"), (760, 120, 40, RES)):
        pts = [(xa + i / n * span, yb2 - packet(xc, wdt, amp, xa + i / n * span)) for i in range(n + 1)]
        f.append(poly(pts, color=col, sw=2.4 if col == RES else 1.7))
    f.append(arrow(320, yb2 + 66, 720, yb2 + 66, color=RES, sw=2.2))
    f.append(text(520, yb2 + 60, "дедалі ширше й нижче", size=12.5, bold=True, color=RES))

    render(os.path.join(IMG, "dispersion.svg"), W, H, *f)


# ── Фігура 5 (для іст. вставки): що є законна форма струни — два табори ────────
def fig_dalembert_euler():
    W, H = 1040, 520
    f = [text(W / 2, 34, "Серце суперечки: яка початкова форма струни законна?",
              size=16.5, bold=True)]

    yb = 275
    # роздільник між таборами
    f.append(line(W / 2, 100, W / 2, 470, color=GRID, sw=1.6))

    # ── лівий табір: д'Аламбер — одна гладка формула ──
    ox = 60
    f.append(text(ox + 210, 84, "Д'Аламбер: лише одна гладка формула", size=14.5, bold=True))
    xa, xb = ox + 30, ox + 390
    A = 128
    cx = (xa + xb) / 2

    def arch(x):  # півсинус — одна аналітична формула
        return yb - A * math.sin(math.pi * (x - xa) / (xb - xa))

    pts = [(x, arch(x)) for x in range(int(xa), int(xb) + 1, 3)]
    f.append(poly(pts, color=STR, sw=3.4))
    for xx in (xa, xb):
        f.append(circle(xx, yb, 5, fill=STR, stroke=STR, sw=1))
    f.append(text(cx, arch(cx) - 16, "y = sin(πx/L) — один вираз", size=12.5, bold=True, color=TEN))
    f.append(text(ox + 210, yb + 44, "«неперервна» у мові XVIII ст.", size=12.5, color=MUTED))
    f.append(text(ox + 210, yb + 66, "= крива, задана ЄДИНИМ рівнянням", size=12.5, bold=True, color=TEN))

    # ── правий табір: Ейлер — будь-яка накреслена крива ──
    ox2 = 560
    f.append(text(ox2 + 210, 84, "Ейлер: будь-яка накреслена крива", size=14.5, bold=True))
    xa2, xb2 = ox2 + 30, ox2 + 390
    xp = xa2 + 0.42 * (xb2 - xa2)
    peakY = yb - 135
    tri = [(xa2, yb), (xp, peakY), (xb2, yb)]
    f.append(poly(tri, color=STR, sw=3.4))
    for xx, yy in ((xa2, yb), (xb2, yb)):
        f.append(circle(xx, yy, 5, fill=STR, stroke=STR, sw=1))
    f.append(circle(xp, peakY, 5, fill=RES, stroke=RES, sw=1))
    f.append(text(xp, peakY - 14, "злам — гострий кут защипу", size=12.5, bold=True, color=RES))
    f.append(text(ox2 + 210, yb + 44, "«механічна» / «розривна» крива", size=12.5, color=MUTED))
    f.append(text(ox2 + 210, yb + 66, "= накреслена від руки, зі зламом", size=12.5, bold=True, color=RES))

    render(os.path.join(IMG, "dalembert-euler-function.svg"), W, H, *f)


# ── Фігура 6 (для math-вставки): точний розклад натягу на кінцях шматочка ──────
def fig_element_freebody():
    W, H = 1040, 520
    f = [text(W / 2, 30, "Точний розклад натягу: горизонталь гаситься, поперек лишається різниця",
              size=15.5, bold=True)]

    # крива — правий схил горба (крутішає зліва направо)
    mu, s, A, yb = 280, 300, 180, 360

    def hump(x):
        return yb - A * math.exp(-((x - mu) / s) ** 2)

    def slope(x):  # dy/dx на екрані (додатний на правому схилі)
        return A * 2 * (x - mu) / s ** 2 * math.exp(-((x - mu) / s) ** 2)

    xa, xb = 150, 640
    arc = [(x, hump(x)) for x in range(xa, xb + 1, 3)]
    f.append(poly(arc, color=STR, sw=3.4))

    # кінці шматочка
    xL, xR = 340, 490
    yL, yR = hump(xL), hump(xR)
    mL, mR = slope(xL), slope(xR)
    for xx, yy in ((xL, yL), (xR, yR)):
        f.append(circle(xx, yy, 5, fill=STR, stroke=STR, sw=1))

    # натяг НАЗОВНІ вздовж дотичної: правий кінець → вниз-праворуч, лівий → вгору-ліворуч
    Larr = 112
    uRx, uRy = 1.0 / math.hypot(1, mR), mR / math.hypot(1, mR)
    uLx, uLy = -1.0 / math.hypot(1, mL), -mL / math.hypot(1, mL)
    RtipX, RtipY = xR + Larr * uRx, yR + Larr * uRy
    LtipX, LtipY = xL + Larr * uLx, yL + Larr * uLy
    f.append(arrow(xR, yR, RtipX, RtipY, color=TEN, sw=2.8))
    f.append(arrow(xL, yL, LtipX, LtipY, color=TEN, sw=2.8))
    f.append(text(RtipX + 6, RtipY + 6, "T₂", size=15, bold=True, color=TEN, anchor="start"))
    f.append(text(LtipX - 8, LtipY - 4, "T₁", size=15, bold=True, color=TEN, anchor="end"))

    # складники правого натягу: горизонталь + вертикаль (пунктир) — трикутник компонент
    f.append(line(xR, yR, RtipX, yR, color=TEN, sw=1.4, dash="5,4"))
    f.append(line(RtipX, yR, RtipX, RtipY, color=RES, sw=1.6, dash="5,4"))
    f.append(text((xR + RtipX) / 2, yR - 8, "T₂·cos θ₂", size=12, color=TEN))
    f.append(text(RtipX + 8, (yR + RtipY) / 2, "T₂·sin θ₂", size=12, color=RES, anchor="start"))
    # θ₂ — на бісектрисі кута між горизонталлю та натягом, поза підписом «T₂·cos θ₂» і поза лінією натягу
    f.append(text(xR + 33, yR + 8, "θ₂", size=13, bold=True))

    # складники лівого натягу
    f.append(line(xL, yL, LtipX, yL, color=TEN, sw=1.4, dash="5,4"))
    f.append(line(LtipX, yL, LtipX, LtipY, color=RES, sw=1.6, dash="5,4"))
    # тут вигин крутіший і натяг іде ВГОРУ від горизонталі (на відміну від правого кінця,
    # де він іде вниз) — клин між дугою й горизонталлю зайнятий стрілкою T₁, тож підпис
    # «T₁·cos θ₁» переносимо ПІД горизонтальну пунктирну (там порожньо: і дуга, і стрілка — вище)
    f.append(text((xL + LtipX) / 2, yL + 14, "T₁·cos θ₁", size=12, color=TEN))
    f.append(text(LtipX - 8, (yL + LtipY) / 2, "T₁·sin θ₁", size=12, color=RES, anchor="end"))
    # θ₁ — близько до вершини, у клині між горизонталлю та стрілкою натягу, поза обома лініями
    f.append(text(xL - 19, yL - 6, "θ₁", size=13, bold=True, anchor="end"))

    # рівнодійна поперек — червона стрілка вниз від середини шматочка
    xm = (xL + xR) / 2
    ym = hump(xm)
    f.append(arrow(xm, ym + 2, xm, ym + 92, color=RES, sw=3.2))
    f.append(text(xm + 10, ym + 66, "рівнодійна", size=12.5, bold=True, color=RES, anchor="start"))

    # відрізок Δx унизу
    ybk = 372
    f.append(line(xL, ybk, xR, ybk, color=MUTED, sw=1.4))
    f.append(line(xL, ybk - 5, xL, ybk + 5, color=MUTED, sw=1.4))
    f.append(line(xR, ybk - 5, xR, ybk + 5, color=MUTED, sw=1.4))
    f.append(text(xm, ybk + 18, "Δx", size=13, bold=True, color=MUTED))

    # два підсумкові рядки-формули внизу (з полем, дрібним шрифтом)
    f.append(text(W / 2, 432,
                  "уздовж струни:  T₁·cos θ₁ = T₂·cos θ₂ ≡ T_h  —  горизонтальний складник однаковий на кінцях",
                  size=13, color=STR))
    f.append(text(W / 2, 460,
                  "упоперек:  T·sin θ = T_h·tg θ = T_h·∂y/∂x  (точно)  →  різниця кінців = T_h · ∂²y/∂x² · Δx",
                  size=13, bold=True, color=RES))
    f.append(text(W / 2, 492, "(кути на рисунку перебільшено; жодного розкладу в ряд тут не знадобилося)",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "element-freebody.svg"), W, H, *f)


# ── Фігура 7 (для math-вставки): область залежності формули д'Аламбера ─────────
def fig_domain_dependence():
    W, H = 1040, 546
    f = [text(W / 2, 30, "Область залежності: значення в (x, t) задають лише дані на відрізку [x−ct, x+ct]",
              size=15.5, bold=True)]

    ax0, ay = 110, 430          # початок осей
    axr, ayt = 950, 84          # кінці осей
    P = (540, 150)
    FL = (360, ay)              # ліва основа: x − ct
    FR = (760, ay)              # права основа: x + ct

    # легка заливка «трикутника залежності»
    f.append(poly([P, FL, FR], color=GRID, sw=0, fill="#eef2f7"))

    # осі
    f.append(arrow(ax0, ay, axr, ay, color=INK, sw=1.8))
    f.append(arrow(ax0, ay, ax0, ayt, color=INK, sw=1.8))
    f.append(text(axr + 4, ay + 5, "x", size=14, bold=True, italic=True, anchor="start"))
    f.append(text(ax0 - 6, ayt - 4, "t", size=14, bold=True, italic=True, anchor="end"))

    # характеристики: ліва основа ← x−ct=const (f, синя), права ← x+ct=const (g, червона)
    f.append(line(P[0], P[1], FL[0], FL[1], color=TEN, sw=2.6))
    f.append(line(P[0], P[1], FR[0], FR[1], color=RES, sw=2.6))
    f.append(text(398, 300, "x − c·t = const", size=12.5, bold=True, color=TEN, anchor="end"))
    f.append(text(690, 300, "x + c·t = const", size=12.5, bold=True, color=RES, anchor="start"))
    f.append(text(360, 246, "(правобіжна f)", size=11, color=TEN, anchor="end"))
    f.append(text(724, 246, "(лівобіжна g)", size=11, color=RES, anchor="start"))

    # відрізок залежності на осі
    f.append(line(FL[0], ay, FR[0], ay, color=FIELD, sw=6))
    for (fx, lab) in ((FL[0], "x − c·t"), (FR[0], "x + c·t")):
        f.append(circle(fx, ay, 5.5, fill=STR, stroke=STR, sw=1))
        f.append(line(fx, ay, fx, P[1] if False else ay, color=STR, sw=1))
        f.append(text(fx, ay + 22, lab, size=12.5, bold=True))

    # точка P
    f.append(circle(P[0], P[1], 6, fill=RES, stroke=RES, sw=1))
    f.append(text(P[0], P[1] - 14, "P = (x, t)", size=13.5, bold=True))

    # що саме входить
    f.append(text((FL[0] + FR[0]) / 2, ay + 46,
                  "початкова швидкість ψ інтегрується на відрізку:  (1/2c)·∫ ψ(s) ds",
                  size=12.5, bold=True, color=FIELD))
    f.append(text((FL[0] + FR[0]) / 2, ay + 68,
                  "початкова форма φ — лише в двох кінцях:  ½[ φ(x−ct) + φ(x+ct) ]",
                  size=12.5, bold=True, color=STR))
    f.append(text(W / 2, 526,
                  "Поза цим відрізком початкові дані на P не впливають — сигнал біжить зі скінченною швидкістю c.",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "domain-dependence.svg"), W, H, *f)


# ── Фігура 8 (для math-вставки): ціна малого кута й де похибка насправді ──────
def fig_small_angle_cost():
    W, H = 1060, 585
    f = [text(W / 2, 30, "Скільки коштує «малий кут» — і де похибка ховається насправді",
              size=16, bold=True)]
    f.append(line(524, 58, 524, 500, color=GRID, sw=1.6))

    # ── ліва панель: похибка малокутового наближення, лог-лог ──
    X0, X1, Y0, Y1 = 140, 480, 430, 120
    f.append(text((X0 + X1) / 2, 78, "похибка заміни sin θ на tg θ росте як θ²", size=13.5, bold=True))

    def PX(deg):
        return X0 + (math.log10(deg) - math.log10(0.3)) / 2.0 * (X1 - X0)

    def PY(v):
        return Y0 - (math.log10(v) + 5.0) / 5.0 * (Y0 - Y1)

    for dec, lab in ((1e-5, "0.001 %"), (1e-4, "0.01 %"), (1e-3, "0.1 %"),
                     (1e-2, "1 %"), (1e-1, "10 %"), (1e0, "100 %")):
        yy = PY(dec)
        f.append(line(X0, yy, X1, yy, color=GRID, sw=1.2))
        f.append(text(X0 - 10, yy + 4, lab, size=12, color=MUTED, anchor="end"))
    for dg, lab in ((0.3, "0.3°"), (1, "1°"), (3, "3°"), (10, "10°"), (30, "30°")):
        xx = PX(dg)
        f.append(line(xx, Y0, xx, Y1, color=GRID, sw=1.2))
        f.append(text(xx, Y0 + 22, lab, size=12.5, color=MUTED))
    f.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))
    f.append(line(X0, Y0, X0, Y1, color=INK, sw=1.6))
    f.append(text((X0 + X1) / 2, Y0 + 48, "найбільший кут нахилу струни θ", size=12.5, color=MUTED))

    pts = []
    n = 90
    for i in range(n + 1):
        dg = 0.3 * (100.0 ** (i / float(n)))
        pts.append((PX(dg), PY(1.0 / math.cos(math.radians(dg)) - 1.0)))
    f.append(poly(pts, color=RES, sw=2.6))

    for dg, lab, side in ((0.83, "струна гітари: 0.83°  →  0.01 %", "br"),
                          (10, "10°  →  1.5 %", "al"),
                          (30, "30°  →  15 %", "al")):
        px, py = PX(dg), PY(1.0 / math.cos(math.radians(dg)) - 1.0)
        f.append(circle(px, py, 5.5, fill=RES, stroke=RES, sw=1))
        if side == "br":
            f.append(text(px + 12, py + 24, lab, size=12.5, bold=True, anchor="start"))
        else:
            f.append(text(px - 12, py - 12, lab, size=12.5, bold=True, anchor="end"))
    f.append(mtext(455, 340, ["нахил 2 на лог-лог:", "похибка ∝ θ²"], size=12.5,
                   color=MUTED, anchor="end"))

    # ── права панель: два доданки поправки для конкретної струни ──
    f.append(text(792, 78, "той самий (∂y/∂x)² — але дві дуже різні ціни", size=13.5, bold=True))
    base = 430
    f.append(line(600, base, 990, base, color=INK, sw=1.6))
    scale = 250.0 / 0.842
    for bx, val, vlab, cap, col, fill in (
            (680, 0.0315, "0.032 %", ["геометрія", "(3/2)·(∂y/∂x)²"], MUTED, "#eef1f4"),
            (880, 0.842, "0.84 %", ["пружність", "(EA/2T₀)·⟨(∂y/∂x)²⟩"], RES, "#fdecea")):
        h = val * scale
        f.append(rect(bx - 55, base - h, 110, h, fill=fill, stroke=col, sw=2, rx=3))
        f.append(text(bx, base - h - 12, vlab, size=14.5, bold=True, color=col))
        f.append(mtext(bx, base + 24, cap, size=12.5, color=INK))
    f.append(arrow(780, 318, 780, 412, color=INK, sw=1.8))
    f.append(arrow(780, 286, 780, 190, color=INK, sw=1.8))
    f.append(text(780, 306, "×26", size=15, bold=True))

    f.append(text(W / 2, 524,
                  "струна T₀ = 80 Н, μ = 0.5 г/м, L = 65 см, сталь d = 0.29 мм (EA = 12.8 кН, тобто EA/T₀ = 160), защип на 3 мм",
                  size=12.5, color=STR))
    f.append(text(W / 2, 552,
                  "0.84 % натягу = +0.42 % частоти ≈ 7 центів угору одразу після защипу; геометричні 0.032 % — це 0.5 цента, і їх не чути",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, "small-angle-cost.svg"), W, H, *f)


# ══ Фігури до вставки proj-wave-sim.md (чисельна модель на сітці) ═════════════
def curve_arrow(p0, p1, p2, p3, color=INK, sw=2.2):
    return ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], color, sw))


# ── Фігура: шаблон кроку на сітці ────────────────────────────────────────────
def fig_grid_stencil():
    W, H = 1020, 690
    f = [text(W / 2, 34, "Крок схеми: чотири відомі вузли дають п'ятий", size=17, bold=True)]

    cols = [180, 340, 500, 660, 820]
    rows = {"n+1": 200, "n": 325, "n-1": 450}

    # сітка
    for yy in rows.values():
        f.append(line(150, yy, 850, yy, color=GRID, sw=1.6))
    for xx in cols:
        f.append(line(xx, 185, xx, 465, color=GRID, sw=1.6))
    for xx in cols:
        for yy in rows.values():
            f.append(circle(xx, yy, 4.2, fill="#ffffff", stroke=GHOST, sw=1.4))

    # мітки рівнів часу
    for lab, yy in (("t + Δt", rows["n+1"]), ("t", rows["n"]), ("t − Δt", rows["n-1"])):
        f.append(text(138, yy + 5, lab, size=13.5, color=MUTED, anchor="end"))

    # відомі вузли
    for xx in (340, 500, 660):
        f.append(circle(xx, rows["n"], 8.5, fill=TEN, stroke=TEN, sw=1))
    f.append(circle(500, rows["n-1"], 8.5, fill=GHOST, stroke=MUTED, sw=1.4))
    # шуканий
    f.append(circle(500, rows["n+1"], 10, fill="#ffffff", stroke=RES, sw=3.2))

    # стрілки внесків
    f.append(arrow(348, rows["n"] - 8, 492, rows["n+1"] + 10, color=TEN, sw=2.2))
    f.append(arrow(652, rows["n"] - 8, 508, rows["n+1"] + 10, color=TEN, sw=2.2))
    f.append(arrow(500, rows["n"] - 12, 500, rows["n+1"] + 12, color=TEN, sw=2.2))
    f.append(curve_arrow((492, rows["n-1"] - 4), (200, 485), (215, 175), (486, 196),
                         color=MUTED, sw=2.0))

    # підписи вузлів
    f.append(text(340, 295, "y[i−1]", size=13.5, bold=True, color=TEN))
    f.append(text(452, 295, "y[i]", size=13.5, bold=True, color=TEN, anchor="end"))
    f.append(text(660, 295, "y[i+1]", size=13.5, bold=True, color=TEN))
    f.append(text(500, 487, "y_стар[i]", size=13.5, bold=True, color=MUTED))
    f.append(text(500, 172, "y_нов[i] — шукане", size=13.5, bold=True, color=RES))

    # осі
    f.append(text(880, rows["n-1"] + 5, "x →", size=13, color=MUTED, anchor="start"))
    f.append(text(138, 172, "↑ t", size=13, color=MUTED, anchor="end"))
    f.append(text(500, 516, "вузли з кроком Δx", size=12.5, color=MUTED, italic=True))

    # формула сегментами (щоб точно знати, де що)
    segs = [("y_нов[i] = ", INK, True),
            ("2·y[i] − y_стар[i]", TEN, True),
            ("  +  ", INK, True),
            ("r²·( y[i−1] − 2·y[i] + y[i+1] )", RES, True)]
    fs = 19
    widths = [text_width(s, fs, b) for (s, c, b) in segs]
    total = sum(widths)
    x = (W - total) / 2
    fy = 570
    centers = []
    for (s, c, b), wd in zip(segs, widths):
        f.append(text(x, fy, s, size=fs, color=c, bold=b, anchor="start"))
        centers.append(x + wd / 2)
        x += wd

    # підкреслення й підписи частин
    f.append(line(centers[1] - widths[1] / 2, fy + 12, centers[1] + widths[1] / 2, fy + 12,
                  color=TEN, sw=2.2))
    f.append(line(centers[3] - widths[3] / 2, fy + 12, centers[3] + widths[3] / 2, fy + 12,
                  color=RES, sw=2.2))
    f.append(text(centers[1], fy + 34, "рух за інерцією", size=13, color=TEN, bold=True))
    f.append(text(centers[3], fy + 34, "поправка від кривини,  r = c·Δt/Δx", size=13, color=RES, bold=True))
    f.append(text(W / 2, fy + 74,
                  "жодних матриць: усе, що треба, — три сусіди й той самий вузол кроком раніше",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "grid-stencil.svg"), W, H, *f)


# ── Фігура: умова Куранта як конус залежності ────────────────────────────────
def fig_courant_cone():
    W, H = 1080, 600
    f = [text(W / 2, 32, "Умова Куранта: чи встигає схема побачити те, що вирішує відповідь",
              size=17, bold=True)]

    def panel(px, r, ok):
        cx = px + 240
        step = 40.0
        top, bot = 150.0, 418.0
        nrow = 4
        dy = (bot - top) / nrow
        col = FIELD if ok else RES
        head = ("r = c·Δt/Δx = %.2f" % r) + ("  —  фізика ВСЕРЕДИНІ шаблона" if ok
                                             else "  —  фізика ЗЗОВНІ шаблона")
        g = [text(cx, 92, head, size=15, bold=True, color=col)]
        # сітка вузлів
        for k in range(-5, 6):
            for m in range(nrow + 1):
                g.append(circle(cx + k * step, bot - m * dy, 3.4, fill="#ffffff",
                                stroke=GHOST, sw=1.2))
        # числовий конус
        g.append(poly([(cx, top), (cx - nrow * step, bot), (cx + nrow * step, bot)],
                      color="#c8cfd8", sw=1.6, fill="#eef1f5"))
        # фізичні характеристики
        g.append(poly([(cx - r * nrow * step, bot), (cx, top), (cx + r * nrow * step, bot)],
                      color=TEN, sw=2.8))
        # точка P
        g.append(circle(cx, top, 7, fill=RES, stroke=RES, sw=1))
        g.append(text(cx, top - 16, "P", size=15, bold=True, color=RES))
        # відрізки-джерела на нижньому рівні
        g.append(line(cx - nrow * step, bot + 16, cx + nrow * step, bot + 16,
                      color="#9aa4b1", sw=7))
        g.append(line(cx - r * nrow * step, bot + 34, cx + r * nrow * step, bot + 34,
                      color=TEN, sw=7))
        g.append(text(cx, bot + 62, "сіре — що встигла обійти схема за 4 кроки",
                      size=12.5, color=MUTED))
        g.append(text(cx, bot + 82, "синє — звідки насправді приходить сигнал",
                      size=12.5, color=TEN, bold=True))
        verdict = ("потрібні дані лежать усередині шаблона —\nсхема має з чого скласти правильну відповідь"
                   if ok else
                   "потрібні дані лежать поза шаблоном —\nжодна арифметика їх не поверне: пилка росте вибухом")
        g.append(fitbox(px + 20, bot + 96, 440, 58, verdict, size=13.5, bold=True,
                        color=col, stroke=col, fill="#ffffff"))
        return g

    f += panel(20, 0.70, True)
    f += panel(560, 1.25, False)
    f.append(line(W / 2, 80, W / 2, 560, color=GRID, sw=1.6))
    render(os.path.join(IMG, "courant-cone.svg"), W, H, *f)


# ── Фігура: відбиття від закріпленого й вільного кінця ───────────────────────
def fig_reflection_ends():
    W, H = 1040, 720
    f = [text(W / 2, 32, "Звідки в моделі береться відбиття: дзеркальний двійник за краєм",
              size=17, bold=True)]
    A = 26.0
    wid = 26.0

    def pulse(s, c0):
        return A * math.exp(-((s - c0) / wid) ** 2)

    def panel(px, kind):
        wallx = px + 250
        col_head = TEN if kind == "fixed" else RES
        head = ("Закріплений кінець:  y[0] = 0" if kind == "fixed"
                else "Вільний кінець:  y[−1] = y[1]  (нахил нуль)")
        g = [text(px + 240, 64, head, size=15.5, bold=True, color=col_head)]
        g.append(text(px + 240, 88, "суцільна — справжня струна · штрихова — уявне продовження за край",
                      size=12, color=MUTED, italic=True))
        rows = [(190.0, 150.0, "імпульс підбігає до краю; за краєм дзеркалиться його двійник"),
                (365.0, 0.0, ("у мить дотику двійник ГАСИТЬ імпульс — струна пряма, уся енергія в русі"
                              if kind == "fixed"
                              else "у мить дотику двійник ДОДАЄТЬСЯ — на краю подвійна висота")),
                (540.0, -150.0, ("назад іде ПЕРЕВЕРНУТИЙ імпульс" if kind == "fixed"
                                 else "назад іде ПРЯМИЙ імпульс, без перевертання"))]
        sgn = -1.0 if kind == "fixed" else 1.0
        for (base, c0, cap) in rows:
            g.append(line(px + 15, base, px + 465, base, color=GRID, sw=1.6))
            # стінка
            g.append(line(wallx, base - 54, wallx, base + 54, color=STR, sw=3.2))
            for m in range(-2, 3):
                g.append(line(wallx, base + m * 22, wallx - 13, base + m * 22 - 11,
                              color=MUTED, sw=1.4))
            real, ghost, tot = [], [], []
            xx = px + 18
            while xx <= px + 462:
                s = xx - wallx
                rv = pulse(s, c0)                 # справжній імпульс
                gv = sgn * pulse(-s, c0)          # дзеркальний двійник
                real.append((xx, base - rv))
                ghost.append((xx, base - gv))
                tot.append((xx, base - (rv + gv)))
                xx += 3.0
            g.append(poly(real, color=TEN, sw=1.5, dash="5 5"))
            g.append(poly(ghost, color=RES, sw=1.5, dash="5 5"))
            g.append(poly([p for p in tot if p[0] >= wallx], color=STR, sw=3.4))
            g.append(poly([p for p in tot if p[0] <= wallx], color=GHOST, sw=2.0, dash="7 5"))
            g.append(text(px + 240, base + 92, cap, size=12.5, color=MUTED))
        g.append(text(wallx, 116, "край", size=13, bold=True))
        return g

    f += panel(20, "fixed")
    f += panel(540, "free")
    f.append(line(W / 2, 55, W / 2, 655, color=GRID, sw=1.6))
    f.append(text(W / 2, 690,
                  "Тримати y[0] = 0 — те саме, що пустити нескінченну струну з перевернутим двійником; "
                  "тримати нульовий нахил — з прямим.",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "reflection-ends.svg"), W, H, *f)


if __name__ == "__main__":
    fig_string_forces()
    fig_curvature_acceleration()
    fig_dalembert()
    fig_dispersion()
    fig_dalembert_euler()
    fig_element_freebody()
    fig_domain_dependence()
    fig_small_angle_cost()
    fig_grid_stencil()
    fig_courant_cone()
    fig_reflection_ends()
    print("OK: figs written to", IMG)
