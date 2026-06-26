# -*- coding: utf-8 -*-
"""Фігури до теми «Матеріали для кріплення IMU». Чистий Python, svgkit зі scripts/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Кріплення IMU = маса на пружині (механічна модель) ────────────────────
def fig_mass_spring():
    W, H = 720, 360
    el = []
    # ── ЛІВОРУЧ: жорстке кріплення ──
    cx = 185
    # рама (вібрує)
    frame_y = 300
    el.append(rect(cx - 110, frame_y, 220, 26, fill="#e9ecf2", stroke=LINE))
    el.append(text(cx, frame_y + 18, "рама (джерело тряски)", size=12, color=MUTED))
    # жорсткий стовп
    el.append(rect(cx - 14, 150, 28, 150, fill="#d6d9e0", stroke=LINE))
    # IMU зверху
    el.append(rect(cx - 50, 110, 100, 44, fill="#fdecea", stroke=POS, sw=2))
    el.append(text(cx, 137, "IMU", size=16, color=POS, bold=True))
    # вібрація проходить наскрізь
    el.append(arrow(cx + 70, frame_y - 4, cx + 70, 150, color=POS, sw=2.4))
    el.append(text(cx + 96, 230, "тряска", size=12, color=POS))
    el.append(text(cx + 96, 246, "проходить", size=12, color=POS))
    el.append(text(cx + 96, 262, "наскрізь", size=12, color=POS))
    el.append(text(cx, 78, "Жорстко: одне ціле", size=14, bold=True, color=INK))

    # ── ПРАВОРУЧ: м'яке кріплення (маса на пружині) ──
    cx = 540
    el.append(rect(cx - 110, frame_y, 220, 26, fill="#e9ecf2", stroke=LINE))
    el.append(text(cx, frame_y + 18, "рама (джерело тряски)", size=12, color=MUTED))
    # пружина (зиґзаґ) між рамою і масою
    sp_top, sp_bot = 158, frame_y
    coils = 6
    pts = []
    seg = (sp_bot - sp_top) / coils
    for i in range(coils + 1):
        x = cx + (16 if i % 2 else -16)
        if i == 0:
            x = cx
        if i == coils:
            x = cx
        pts.append((x, sp_top + i * seg))
    sp = '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (
        " ".join("%.1f,%.1f" % p for p in pts), FIELD)
    el.append(sp)
    el.append(text(cx + 52, 250, "демпфер", size=12, color=FIELD))
    el.append(text(cx + 52, 266, "= пружина", size=12, color=FIELD))
    el.append(text(cx + 52, 282, "+ тертя", size=12, color=FIELD))
    # IMU (маса) на пружині
    el.append(rect(cx - 50, 112, 100, 46, fill="#fdecea", stroke=POS, sw=2))
    el.append(text(cx - 6, 133, "IMU", size=16, color=POS, bold=True))
    el.append(text(cx - 6, 150, "= маса m", size=11, color=MUTED))
    el.append(text(cx, 78, "М'яко: маса на пружині", size=14, bold=True, color=INK))
    # мала тряска доходить
    el.append(arrow(cx - 78, 158, cx - 78, 130, color=MUTED, sw=1.6))
    el.append(text(cx - 92, 196, "мала", size=11, color=MUTED, anchor="end"))
    el.append(text(cx - 92, 210, "решта", size=11, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "mass-spring.svg"), W, H, *el,
           title="Кріплення IMU — це механічна система «маса на пружині»")


# ── 2. Крива передавання: резонанс і поріг √2 ────────────────────────────────
def fig_transmissibility():
    W, H = 720, 420
    L, R, T, B = 90, 680, 70, 330  # межі поля графіка
    el = []

    # осі
    el.append(line(L, B, R, B, color=INK, sw=1.8))   # X
    el.append(line(L, T, L, B, color=INK, sw=1.8))   # Y
    el.append(text((L + R) / 2, 392, "частота тряски / власна частота кріплення  (f / f₀)",
                   size=13, color=INK))
    # підпис Y вертикально
    el.append('<text x="26" y="%.1f" font-family="%s" font-size="13" fill="%s" '
              'text-anchor="middle" transform="rotate(-90 26 %.1f)">передавання (скільки доходить)</text>'
              % ((T + B) / 2, FONT, INK, (T + B) / 2))

    # координати: r від 0 до 4; T-значення від 0 до ~3.2
    rmax = 4.0
    tmax = 3.2

    def X(r):
        return L + (r / rmax) * (R - L)

    def Y(t):
        return B - (min(t, tmax) / tmax) * (B - T)

    # лінія «доходить = 1» (нічого не змінилось)
    el.append(line(L, Y(1), R, Y(1), color=MUTED, sw=1.2, dash="5,4"))
    el.append(text(R - 4, Y(1) - 8, "=1: тряска проходить як є", size=11, color=MUTED, anchor="end"))

    # крива передавання для помірного загасання (ζ≈0.25)
    zeta = 0.25
    pts = []
    r = 0.02
    while r <= rmax:
        num = math.sqrt(1 + (2 * zeta * r) ** 2)
        den = math.sqrt((1 - r * r) ** 2 + (2 * zeta * r) ** 2)
        Tval = num / den
        pts.append((X(r), Y(Tval)))
        r += 0.02
    el.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
              % (" ".join("%.1f,%.1f" % p for p in pts), POS))

    # вертикаль резонансу r=1
    el.append(line(X(1), T, X(1), B, color=MUTED, sw=1.0, dash="3,4"))
    el.append(text(X(1) + 6, T + 14, "резонанс: тряску", size=11, color=POS))
    el.append(text(X(1) + 6, T + 28, "ПІДСИЛЕНО", size=11, color=POS, bold=True))

    # вертикаль √2 — поріг ізоляції
    r2 = math.sqrt(2)
    el.append(line(X(r2), T, X(r2), B, color=FIELD, sw=1.6, dash="6,4"))
    el.append(text(X(r2), B + 16, "√2", size=12, color=FIELD, bold=True))

    # зони
    box1 = fitbox(X(0.05) + 2, B - 70, X(1) - X(0.05) - 6, 24,
                  "тут робити НЕ можна", size=11, fill="#fdecea", stroke=POS, color=POS)
    el.append(box1)
    box2 = fitbox(X(r2) + 4, T + 44, R - X(r2) - 6, 24,
                  "тут працює ізоляція", size=11, fill="#eafaf0", stroke=FIELD, color=FIELD)
    el.append(box2)

    # стрілка вниз у зоні ізоляції
    el.append(arrow(X(3.0), Y(0.9), X(3.0), Y(0.18), color=FIELD, sw=2.0))
    el.append(text(X(3.4), Y(0.5), "доходить", size=11, color=FIELD))
    el.append(text(X(3.4), Y(0.5) + 14, "усе менше", size=11, color=FIELD))

    # мітки осі X
    for rr in (1, 2, 3, 4):
        el.append(text(X(rr), B + 16, str(rr), size=11, color=MUTED))

    render(os.path.join(OUT, "transmissibility.svg"), W, H, *el,
           title="М'яке кріплення допомагає лише вище порога √2 — нижче воно ПІДСИЛЮЄ")


# ── 3. Перетягнутий гвинт убиває демпфер ─────────────────────────────────────
def fig_overtightening():
    W, H = 720, 340
    el = []

    def stack(cx, label, comp, ok):
        # рама
        el.append(rect(cx - 95, 250, 190, 24, fill="#e9ecf2", stroke=LINE))
        el.append(text(cx, 266, "рама", size=12, color=MUTED))
        # демпфер (висота залежить від стиснення)
        full_h = 70
        h = full_h * (1 - comp)
        dy = 250 - h
        col = FIELD if ok else POS
        fill = "#eafaf0" if ok else "#fdecea"
        el.append(rect(cx - 70, dy, 140, h, fill=fill, stroke=col, sw=2))
        # IMU/плата
        el.append(rect(cx - 70, dy - 40, 140, 40, fill="#d6d9e0", stroke=LINE))
        el.append(text(cx, dy - 16, "плата з IMU", size=12, color=INK))
        # гвинт наскрізь
        el.append(rect(cx - 5, dy - 52, 10, h + 64, fill="#9aa0ab", stroke=LINE, sw=1))
        el.append(circle(cx, dy - 52, 9, fill="#9aa0ab", stroke=LINE))
        # підпис стиснення
        el.append(text(cx, 300, label, size=13, bold=True, color=col))
        # запас ходу
        if ok:
            el.append(arrow(cx + 95, dy, cx + 95, 250, color=FIELD, sw=1.8))
            el.append(arrow(cx + 95, 250, cx + 95, dy, color=FIELD, sw=1.8))
            el.append(text(cx + 110, (dy + 250) / 2, "є хід", size=11, color=FIELD, anchor="start"))
        else:
            el.append(text(cx + 78, (dy + 250) / 2, "ходу", size=11, color=POS, anchor="start"))
            el.append(text(cx + 78, (dy + 250) / 2 + 14, "нема", size=11, color=POS, anchor="start"))

    stack(200, "правильно: підтиснуто", 0.18, True)
    stack(520, "перетягнуто: розчавлено", 0.78, False)

    render(os.path.join(OUT, "overtightening.svg"), W, H, *el,
           title="Перетягнутий гвинт розчавлює демпфер — і він уже не пружинить")


# ── 4. Виведення: основа рухається y(t), маса m відгукується x(t) ─────────────
def fig_base_excitation():
    """Схема задачі базового збудження: рухома основа, маса, пружина+демпфер
    реагують на ВІДНОСНЕ зміщення (x − y). Це серце виведення T(r)."""
    W, H = 720, 380
    el = []
    cx = 300

    # нерухомий «ефір» / опорна рамка координат — пунктир ліворуч
    el.append(line(70, 70, 70, 320, color=MUTED, sw=1.0, dash="3,5"))
    el.append(text(70, 56, "нерухомий відлік", size=11, color=MUTED))

    # ── рухома основа (рама) ──
    base_y = 300
    el.append(rect(cx - 120, base_y, 240, 28, fill="#e9ecf2", stroke=LINE))
    el.append(text(cx, base_y + 19, "основа (рама)", size=12, color=MUTED))
    # її рух y(t)
    el.append(arrow(cx - 150, base_y + 14, cx - 96, base_y + 14, color=NEG, sw=2.2))
    el.append(text(cx - 168, base_y + 4, "y(t)", size=14, color=NEG, bold=True, anchor="end"))
    el.append(text(cx - 168, base_y + 22, "вхід", size=10, color=NEG, anchor="end"))

    # ── маса m ──
    mass_y, mass_h = 96, 56
    el.append(rect(cx - 56, mass_y, 112, mass_h, fill="#fdecea", stroke=POS, sw=2))
    el.append(text(cx, mass_y + 26, "маса m", size=16, color=POS, bold=True))
    el.append(text(cx, mass_y + 44, "(IMU)", size=11, color=MUTED))
    # її рух x(t)
    el.append(arrow(cx + 56 + 18, mass_y + 18, cx + 56 + 72, mass_y + 18, color=POS, sw=2.2))
    el.append(text(cx + 56 + 80, mass_y + 8, "x(t)", size=14, color=POS, bold=True, anchor="start"))
    el.append(text(cx + 56 + 80, mass_y + 26, "вихід", size=10, color=POS, anchor="start"))

    # ── пружина k (зиґзаґ) ліворуч від центру ──
    sp_x = cx - 30
    sp_top, sp_bot = mass_y + mass_h, base_y
    coils = 6
    seg = (sp_bot - sp_top) / coils
    pts = []
    for i in range(coils + 1):
        x = sp_x + (12 if i % 2 else -12)
        if i in (0, coils):
            x = sp_x
        pts.append((x, sp_top + i * seg))
    el.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
              % (" ".join("%.1f,%.1f" % p for p in pts), FIELD))
    el.append(text(sp_x - 30, (sp_top + sp_bot) / 2, "k", size=15, color=FIELD, bold=True, anchor="end"))
    el.append(text(sp_x - 30, (sp_top + sp_bot) / 2 + 16, "пружина", size=10, color=FIELD, anchor="end"))

    # ── демпфер c (поршень) праворуч від центру ──
    dp_x = cx + 30
    # циліндр
    el.append(rect(dp_x - 13, sp_bot - 30, 26, 30, fill="#eef2ff", stroke=NEG, sw=1.6, rx=2))
    # шток + поршень
    el.append(line(dp_x, sp_top, dp_x, sp_bot - 16, color=NEG, sw=2.4))
    el.append(line(dp_x - 11, sp_bot - 16, dp_x + 11, sp_bot - 16, color=NEG, sw=3.0))
    el.append(text(dp_x + 30, (sp_top + sp_bot) / 2, "c", size=15, color=NEG, bold=True, anchor="start"))
    el.append(text(dp_x + 30, (sp_top + sp_bot) / 2 + 16, "тертя", size=10, color=NEG, anchor="start"))

    # ── ключова підказка: сили залежать від РІЗНИЦІ (x − y) ──
    box = fitbox(cx - 150, 24, 300, 30,
                 "пружина й тертя «бачать» лише різницю  x − y",
                 size=12, fill="#fff8e1", stroke="#b8860b", color="#7a5c00")
    el.append(box)

    render(os.path.join(OUT, "base-excitation.svg"), W, H, *el,
           title="Базове збудження: рухома основа y(t) → відгук маси x(t)")


# ── 5. Сімейство кривих T(r) за різних ζ — усі сходяться в √2 ────────────────
def fig_damping_family():
    """Декілька кривих передавання за різних коефіцієнтів загасання.
    Головна думка: усі вони перетинаються в одній точці r=√2, T=1; більше
    тертя — нижчий пік, але ПОЛОГІШИЙ спад далеко за √2."""
    W, H = 760, 460
    L, R, T, B = 95, 720, 78, 360
    el = []

    rmax = 4.0
    tmax = 4.0

    def X(r):
        return L + (r / rmax) * (R - L)

    def Y(t):
        return B - (min(t, tmax) / tmax) * (B - T)

    # осі
    el.append(line(L, B, R, B, color=INK, sw=1.8))
    el.append(line(L, T, L, B, color=INK, sw=1.8))
    el.append(text((L + R) / 2, 432, "відношення частот  r = f / f₀", size=13, color=INK))
    el.append('<text x="30" y="%.1f" font-family="%s" font-size="13" fill="%s" '
              'text-anchor="middle" transform="rotate(-90 30 %.1f)">передавання T(r)</text>'
              % ((T + B) / 2, FONT, INK, (T + B) / 2))

    # сітка по Y
    for tv in (1, 2, 3, 4):
        yy = Y(tv)
        el.append(line(L, yy, R, yy, color="#e6e8ee", sw=1.0))
        el.append(text(L - 8, yy + 4, str(tv), size=11, color=MUTED, anchor="end"))
    for rr in (1, 2, 3, 4):
        el.append(text(X(rr), B + 16, str(rr), size=11, color=MUTED))

    # лінія T=1
    el.append(line(L, Y(1), R, Y(1), color=MUTED, sw=1.2, dash="5,4"))

    # криві за різних ζ
    curves = [
        (0.05, POS,   "ζ = 0.05  (сухо, гострий пік)"),
        (0.15, "#e67e22", "ζ = 0.15"),
        (0.40, FIELD, "ζ = 0.40  (в'язко)"),
        (0.70, NEG,   "ζ = 0.70  (дуже в'язко)"),
    ]
    for zeta, col, _ in curves:
        pts = []
        r = 0.02
        while r <= rmax:
            num = math.sqrt(1 + (2 * zeta * r) ** 2)
            den = math.sqrt((1 - r * r) ** 2 + (2 * zeta * r) ** 2)
            pts.append((X(r), Y(num / den)))
            r += 0.02
        el.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                  % (" ".join("%.1f,%.1f" % p for p in pts), col))

    # вертикаль √2 — спільна точка
    r2 = math.sqrt(2)
    el.append(line(X(r2), T, X(r2), B, color=INK, sw=1.4, dash="6,4"))
    el.append(circle(X(r2), Y(1), 5, fill=BG, stroke=INK, sw=2))
    el.append(text(X(r2), B + 16, "√2", size=12, color=INK, bold=True))
    el.append(text(X(r2) + 8, Y(1) - 12, "усі криві проходять тут: T=1", size=11, color=INK))

    # дві зони
    el.append(fitbox(X(0.06), T + 6, X(1.0) - X(0.06) - 6, 22,
                     "тут тертя РЯТУЄ (тисне пік)", size=10,
                     fill="#fdecea", stroke=POS, color=POS))
    el.append(fitbox(X(2.5), T + 6, R - X(2.5) - 6, 22,
                     "тут тертя ШКОДИТЬ (пологіший спад)", size=10,
                     fill="#eef2ff", stroke=NEG, color=NEG))

    # стрілки-підписи компромісу
    el.append(text(X(1.0), Y(3.6), "малий ζ → пік високий", size=11, color=POS, anchor="middle"))
    el.append(text(X(3.5), Y(0.62), "малий ζ", size=10, color=POS, anchor="middle"))
    el.append(text(X(3.5), Y(0.62) + 13, "падає крутіше", size=10, color=POS, anchor="middle"))

    # легенда
    lx, ly = X(2.2), Y(3.5)
    for i, (zeta, col, lab) in enumerate(curves):
        yy = ly + i * 18
        el.append(line(lx, yy, lx + 24, yy, color=col, sw=3))
        el.append(text(lx + 30, yy + 4, lab, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "damping-family.svg"), W, H, *el,
           title="Більше тертя притлумлює пік, але псує спад — а √2 не зрушити")


if __name__ == "__main__":
    fig_mass_spring()
    fig_transmissibility()
    fig_overtightening()
    fig_base_excitation()
    fig_damping_family()
    print("figures written to", OUT)
