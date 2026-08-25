# -*- coding: utf-8 -*-
"""Фігури до статті «Девіація Аллана і стабільність частоти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GPS = "#8e44ad"   # окремий колір для GPSDO


def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s stroke-linejoin="round"/>' % (p, color, sw, d)


# ── 1. Чому класична дисперсія не працює: дрейф проти сусідів ────────────────
def fig_divergence():
    W, H = 940, 470
    f = [text(W / 2, 30, "Дрейфливий запис частоти: два способи міряти розкид", size=17, bold=True),
         text(W / 2, 52, "той самий ряд відліків y ліворуч і праворуч — різняться лише запитанням до нього",
              size=12, color=MUTED, italic=True)]

    # спільний ряд відліків (умовні одиниці; ряд повзе вгору з тремтінням)
    ys = [20, 26, 22, 30, 34, 30, 40, 46, 42, 52, 58, 55, 66, 72]
    n = len(ys)
    ymin, ymax = 8, 84
    mean = sum(ys) / n

    def panel(L, R, T, B):
        def X(i):
            return L + (R - L) * i / (n - 1)

        def Y(v):
            return B - (v - ymin) / (ymax - ymin) * (B - T)
        return X, Y

    # ── ЛІВА панель: відстань від глобального середнього ──
    L, R, T, B = 70, 445, 100, 380
    X, Y = panel(L, R, T, B)
    f.append(line(L, T - 6, L, B, color=INK, sw=1.8))
    f.append(line(L, B, R + 8, B, color=INK, sw=1.8))
    f.append(text(L - 8, T + 4, "y", size=13, bold=True, anchor="end"))
    f.append(text(R + 8, B + 20, "час →", size=12, color=MUTED, anchor="end"))
    # лінія глобального середнього
    ymid = Y(mean)
    f.append(line(L, ymid, R, ymid, color=FIELD, sw=1.8, dash="7 5"))
    f.append(text(R + 12, ymid + 4, "середнє ȳ", size=11.5, color=FIELD, bold=True, anchor="start"))
    # відрізки від кожного відліку до середнього + точки
    pts = [(X(i), Y(v)) for i, v in enumerate(ys)]
    for (px, py) in pts:
        f.append(line(px, py, px, ymid, color=POS, sw=1.2, dash="2 3"))
    f.append(polyline(pts, INK, sw=1.6))
    for (px, py) in pts:
        f.append(circle(px, py, 3.6, fill=BG, stroke=INK, sw=1.6))
    # виноска про крайні відхилення
    f.append(line(X(n - 1) + 0, Y(ys[-1]), X(n - 1) + 0, ymid, color=POS, sw=2.6))
    f.append(text((L + R) / 2, B + 40, "відстань від середнього", size=12.5, color=POS, bold=True))
    f.append(text((L + R) / 2, B + 58, "роздута дрейфом; росте з довжиною запису", size=11, color=MUTED, italic=True))
    f.append(text((L + R) / 2, T - 14, "класична дисперсія", size=13, bold=True))

    # ── ПРАВА панель: різниця сусідів ──
    L2, R2, T2, B2 = 545, 900, 100, 380
    X2, Y2 = panel(L2, R2, T2, B2)
    f.append(line(L2, T2 - 6, L2, B2, color=INK, sw=1.8))
    f.append(line(L2, B2, R2 + 8, B2, color=INK, sw=1.8))
    f.append(text(L2 - 8, T2 + 4, "y", size=13, bold=True, anchor="end"))
    f.append(text(R2 + 8, B2 + 20, "час →", size=12, color=MUTED, anchor="end"))
    pts2 = [(X2(i), Y2(v)) for i, v in enumerate(ys)]
    f.append(polyline(pts2, INK, sw=1.6))
    # вертикальні скоби між сусідами (маленькі)
    for i in range(n - 1):
        x_mid = (pts2[i][0] + pts2[i + 1][0]) / 2
        y_lo = min(pts2[i][1], pts2[i + 1][1])
        y_hi = max(pts2[i][1], pts2[i + 1][1])
        f.append(line(x_mid, y_lo, x_mid, y_hi, color=NEG, sw=2.2))
        f.append(line(pts2[i][0], pts2[i][1], x_mid, pts2[i][1], color=NEG, sw=1.0, dash="2 2"))
        f.append(line(pts2[i + 1][0], pts2[i + 1][1], x_mid, pts2[i + 1][1], color=NEG, sw=1.0, dash="2 2"))
    for (px, py) in pts2:
        f.append(circle(px, py, 3.6, fill=BG, stroke=INK, sw=1.6))
    f.append(text((L2 + R2) / 2, B2 + 40, "різниця сусідів  yₖ₊₁ − yₖ", size=12.5, color=NEG, bold=True))
    f.append(text((L2 + R2) / 2, B2 + 58, "мала; від повільного дрейфу не залежить", size=11, color=MUTED, italic=True))
    f.append(text((L2 + R2) / 2, T2 - 14, "дисперсія Аллана", size=13, bold=True))

    render(os.path.join(IMG, "problem-divergence.svg"), W, H, *f)


# ── 2. σ‑τ‑крива: ванна з нахилів різних шумів ──────────────────────────────
def fig_sigma_tau():
    W, H = 900, 540
    f = [text(W / 2, 30, "σ‑τ‑крива: форма ванни читає фізику шумів", size=17, bold=True),
         text(W / 2, 52, "у подвійному лог-масштабі кожен тип шуму — пряма зі своїм нахилом",
              size=12, color=MUTED, italic=True)]

    L, R, T, B = 120, 720, 90, 430
    # діапазони в лог-одиницях
    lt0, lt1 = -3.0, 4.0            # log10(τ), с
    ls0, ls1 = -12.7, -9.0         # log10(σy); більший σ = вище

    def X(lt):
        return L + (lt - lt0) / (lt1 - lt0) * (R - L)

    def Y(ls):
        return T + (ls1 - ls) / (ls1 - ls0) * (B - T)

    # осі
    f.append(line(L, T - 6, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 6, B, color=INK, sw=2))
    f.append(text(R + 6, B + 24, "τ, с  (лог)", size=13, bold=True, anchor="end"))
    f.append(text(L - 60, T + 2, "σy(τ)", size=13, bold=True, anchor="start"))
    f.append(text(L - 60, T + 20, "(лог)", size=11, color=MUTED, anchor="start"))
    # осьові риски декад τ (короткі, не наскрізна сітка — щоб лінії не різали підписи)
    for lt in range(-3, 5):
        x = X(lt)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 20, "10%s" % _sup(lt), size=10.5, color=MUTED))
    # осьові риски декад σ
    for ls in (-12, -11, -10, -9):
        y = Y(ls)
        f.append(line(L - 6, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 10, y + 4, "10%s" % _sup(ls), size=10.5, color=MUTED, anchor="end"))

    # контрольні точки ванни (lt, ls)
    cp = [(-3.0, -9.35), (-2.2, -9.95), (-1.4, -10.45), (-0.6, -10.9),
          (0.2, -11.28), (1.0, -11.5), (1.8, -11.56), (2.4, -11.5),
          (3.0, -11.15), (3.5, -10.6), (4.0, -9.95)]
    curve = [(X(lt), Y(ls)) for lt, ls in cp]
    f.append(polyline(curve, POS, sw=3.2))

    # позначка мінімуму (флікерна підлога) — маркер без ліній, що б різали підписи
    mx, my = X(1.8), Y(-11.56)
    f.append(circle(mx, my, 5.5, fill=BG, stroke=INK, sw=2.2))

    # три зони — підписи у чистих зонах (арки кривої лишаються вільні)
    f.append(fitbox(150, 305, 205, 74,
                    "нахил −1/2\nбілий шум частоти\nусереднення допомагає (√)\nпричина: тепловий шум",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))
    f.append(fitbox(405, 180, 250, 66,
                    "флікерна підлога — нахил 0\nусереднення вже не помагає\nмінімум = оптимальний τ",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(fitbox(470, 332, 235, 74,
                    "нахил +1/2 і +1\nблукання, дрейф, старіння\nдовше усереднення шкодить\nпричина: температура, старіння",
                    size=11, fill="#fdeeea", stroke=POS, color=INK))

    render(os.path.join(IMG, "sigma-tau-curve.svg"), W, H, *f)


# ── 3. Сорти генераторів: криві перетинаються ───────────────────────────────
def fig_grades():
    W, H = 900, 560
    f = [text(W / 2, 30, "Сорти генераторів: найкращого нема — є найкращий для вашого τ", size=16, bold=True),
         text(W / 2, 52, "σ‑τ‑криві перетинаються; хто виграє, залежить від масштабу часу",
              size=12, color=MUTED, italic=True)]

    L, R, T, B = 120, 660, 100, 430
    lt0, lt1 = -1.0, 5.0
    ls0, ls1 = -13.4, -8.4

    def X(lt):
        return L + (lt - lt0) / (lt1 - lt0) * (R - L)

    def Y(ls):
        return T + (ls1 - ls) / (ls1 - ls0) * (B - T)

    f.append(line(L, T - 6, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 6, B, color=INK, sw=2))
    f.append(text(R + 6, B + 24, "τ, с  (лог)", size=13, bold=True, anchor="end"))
    f.append(text(L - 62, T + 2, "σy(τ)", size=13, bold=True, anchor="start"))
    f.append(text(L - 62, T + 20, "(лог)", size=11, color=MUTED, anchor="start"))
    for lt in range(-1, 6):
        x = X(lt)
        f.append(line(x, T - 6, x, B, color="#ededed", sw=1))
        f.append(text(x, B + 20, "10%s" % _sup(lt), size=10.5, color=MUTED))
    for ls in (-13, -12, -11, -10, -9):
        y = Y(ls)
        f.append(line(L, y, R, y, color="#ededed", sw=1))
        f.append(text(L - 10, y + 4, "10%s" % _sup(ls), size=10.5, color=MUTED, anchor="end"))
    # орієнтири часу
    for lt, lab in ((0, "1 с"), (1.78, "1 хв"), (3.56, "1 год"), (4.94, "1 доба")):
        x = X(lt)
        f.append(text(x, T - 12, lab, size=10.5, color=MUTED, italic=True))

    curves = [
        ("TCXO", POS, [(-1, -8.8), (0, -9.05), (1, -9.15), (2, -9.0), (3, -8.65), (4, -8.25), (5, -7.85)]),
        ("OCXO", NEG, [(-1, -11.3), (0, -11.7), (1, -12.0), (1.6, -12.05), (2.2, -11.9), (3, -11.4), (4, -10.8), (5, -10.2)]),
        ("рубідій", FIELD, [(-1, -10.8), (0, -11.05), (1, -11.45), (2, -11.95), (3, -12.5), (3.8, -12.9), (4.4, -13.0), (5, -12.85)]),
        ("GPSDO", GPS, [(-1, -11.3), (0, -11.6), (1, -11.85), (2, -11.9), (2.6, -11.82), (3.2, -12.2), (4, -12.75), (5, -13.15)]),
    ]
    for name, col, cp in curves:
        pts = [(X(lt), Y(ls)) for lt, ls in cp]
        dash = "8 5" if name == "GPSDO" else None
        f.append(polyline(pts, col, sw=2.8, dash=dash))

    # легенда — праворуч, у чистій зоні
    lx, ly = R + 30, T + 20
    leg = [("TCXO", POS, "10⁻⁹ @1с, рано вгору"),
           ("OCXO", NEG, "глибоке дно на секундах"),
           ("рубідій", FIELD, "усереднюється далі вниз"),
           ("GPSDO", GPS, "довгий τ — GPS ріже дрейф")]
    f.append(text(lx, ly - 14, "сорт  ·  де сильний", size=11, color=MUTED, bold=True, anchor="start"))
    for i, (name, col, note) in enumerate(leg):
        yy = ly + i * 40
        f.append(line(lx, yy, lx + 26, yy, color=col, sw=3.2,
                      dash="8 5" if name == "GPSDO" else None))
        f.append(text(lx + 34, yy + 4, name, size=12, bold=True, color=col, anchor="start"))
        f.append(text(lx, yy + 22, note, size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "grades-comparison.svg"), W, H, *f)


# ── 4. Хроніка народження двовибіркової дисперсії ───────────────────────────
def fig_timeline():
    W, H = 1000, 470
    f = [text(W / 2, 30, "Народження двовибіркової дисперсії: хроніка", size=17, bold=True),
         text(W / 2, 52, "від перших атомних еталонів до кризи статистики й розв'язку Аллана 1966 року",
              size=12, color=MUTED, italic=True)]

    axis_y = 250
    L, R = 60, 924
    f.append(arrow(L, axis_y, R + 14, axis_y, color=INK, sw=2.4))
    f.append(text(R + 20, axis_y + 5, "час", size=12, color=MUTED, anchor="start"))

    xs = [130, 278, 426, 574, 722, 870]
    items = [
        (["1955", "перший цезієвий еталон", "Ессен і Паррі · NPL"], MUTED, "#f4f6f8", "above"),
        (["близько 1960", "Аллан — фізик у NBS", "Боулдер, Колорадо"], INK, "#f4f6f8", "below"),
        (["початок 1960-х", "атомні стандарти ламають", "статистику: σ не сходиться"], POS, "#fdeeea", "above"),
        (["1966", "стаття Аллана, Proc. IEEE", "двовибіркова дисперсія"], FIELD, "#eafaf0", "below"),
        (["1971", "Барнс та ін.: спільна", "характеризація стабільности"], NEG, "#eaf0fd", "above"),
        (["1988", "IEEE Std 1139: назва", "«дисперсія Аллана»"], NEG, "#eaf0fd", "below"),
    ]

    bw = 226
    for x, (lines, col, fill, side) in zip(xs, items):
        bh = 20 + len(lines) * 17
        if side == "above":
            box_bottom = axis_y - 44
            box_top = box_bottom - bh
            f.append(line(x, box_bottom, x, axis_y, color=col, sw=1.6))
        else:
            box_top = axis_y + 44
            f.append(line(x, axis_y, x, box_top, color=col, sw=1.6))
        f.append(fitbox(x - bw / 2, box_top, bw, bh, "\n".join(lines),
                        size=12, fill=fill, stroke=col, color=INK))
        f.append(circle(x, axis_y, 6.5, fill=fill, stroke=col, sw=2.6))

    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *f)


# ── 5. Дві машинки як два фільтри: що вони роблять із низькими частотами ────
def fig_highpass():
    W, H = 960, 540
    f = [text(W / 2, 30, "Усереднення й різниця як фільтри: що дістається низьким частотам", size=17, bold=True),
         text(W / 2, 52, "квадрат передавальної функції |H(f)|² у подвійному лог-масштабі",
              size=12, color=MUTED, italic=True)]

    L, R, T, B = 110, 630, 100, 390
    lx0, lx1 = -3.0, -0.05      # log10(f·τ)
    ly0, ly1 = -5.3, 0.45       # log10(|H|²)

    def X(lx):
        return L + (lx - lx0) / (lx1 - lx0) * (R - L)

    def Y(ly):
        return B - (ly - ly0) / (ly1 - ly0) * (B - T)

    f.append(line(L, T - 8, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 8, B, color=INK, sw=2))
    f.append(text(R + 8, B + 21, "f·τ  (лог)", size=12.5, bold=True, anchor="end"))
    f.append(text(L - 66, T - 14, "|H(f)|²", size=12.5, bold=True, anchor="start"))
    for lx in (-3, -2, -1):
        x = X(lx)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 21, "10%s" % _sup(lx), size=10.5, color=MUTED))
    for ly in (-5, -4, -3, -2, -1, 0):
        y = Y(ly)
        f.append(line(L - 6, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 10, y + 4, "10%s" % _sup(ly), size=10.5, color=MUTED, anchor="end"))

    n = 160
    avg, alv = [], []
    for i in range(n + 1):
        lx = lx0 + (lx1 - lx0) * i / n
        u = math.pi * (10 ** lx)
        s = math.sin(u)
        avg.append((X(lx), Y(math.log10((s / u) ** 2))))
        alv.append((X(lx), Y(math.log10(2 * s ** 4 / u ** 2))))
    f.append(polyline(avg, NEG, sw=3.0))
    f.append(polyline(alv, POS, sw=3.0))

    # підписи нахилів — у порожніх зонах між кривими / під нижньою
    f.append(text(X(-2.10), Y(-0.62), "нахил 0 — усе повільне проходить наскрізь",
                  size=11.5, color=NEG, bold=True))
    f.append(text(X(-1.50), Y(-4.05), "нахил +2:  |H|² ≈ 2(πfτ)²",
                  size=11.5, color=POS, bold=True))
    f.append(text(X(-1.50), Y(-4.45), "низькі частоти задавлено як f²",
                  size=11, color=MUTED, italic=True))

    # легенда праворуч, у чистій зоні
    lx0p, ly0p = R + 42, T + 26
    f.append(line(lx0p, ly0p, lx0p + 28, ly0p, color=NEG, sw=3.2))
    f.append(text(lx0p + 36, ly0p + 5, "саме усереднення", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(lx0p, ly0p + 26, "sin²(πfτ) / (πfτ)²", size=11.5, color=INK, anchor="start"))
    f.append(text(lx0p, ly0p + 44, "класична дисперсія", size=11, color=MUTED, italic=True, anchor="start"))
    f.append(line(lx0p, ly0p + 82, lx0p + 28, ly0p + 82, color=POS, sw=3.2))
    f.append(text(lx0p + 36, ly0p + 87, "усереднення + різниця", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(lx0p, ly0p + 108, "2 sin⁴(πfτ) / (πfτ)²", size=11.5, color=INK, anchor="start"))
    f.append(text(lx0p, ly0p + 126, "дисперсія Аллана", size=11, color=MUTED, italic=True, anchor="start"))

    f.append(fitbox(110, 430, 740, 84,
                    "шум зі степеневим спектром  S_y(f) = h·f^α;  біля f = 0 підінтегральна функція:\n"
                    "класика  →  f^α  ·  збігається лише при  α > −1        Аллан  →  f^(α+2)  ·  збігається при  α > −3\n"
                    "два зайві степені f — це і є весь виграш першої різниці",
                    size=12, fill="#f4f6f8", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "math-highpass.svg"), W, H, *f)


# ── 6. Збіжність на ділі: класична оцінка росте з довжиною запису ────────────
def fig_convergence():
    W, H = 980, 520
    f = [text(W / 2, 30, "Що робиться з обома оцінками, коли запис довшає", size=17, bold=True),
         text(W / 2, 52, "N — довжина запису у відліках; класична оцінка росте, Алланова стоїть",
              size=12, color=MUTED, italic=True)]

    # ── ЛІВА панель: випадкове блукання, точна формула ──
    L, R, T, B = 92, 430, 128, 388
    bx0, bx1 = 2.0, 12.0        # log2 N
    by0, by1 = -0.7, 3.1        # log10 значення в одиницях q (дисперсія одного кроку)

    def X(b):
        return L + (b - bx0) / (bx1 - bx0) * (R - L)

    def Y(v):
        return B - (v - by0) / (by1 - by0) * (B - T)

    f.append(text((L + R) / 2, T - 34, "випадкове блукання  (α = −2)", size=13, bold=True))
    f.append(text((L + R) / 2, T - 16, "точна формула, обидві осі логарифмічні", size=10.5,
                  color=MUTED, italic=True))
    f.append(line(L, T - 6, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 8, B, color=INK, sw=2))
    for b, lab in ((2, "4"), (4, "16"), (6, "64"), (8, "256"), (10, "1024"), (12, "4096")):
        x = X(b)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 20, lab, size=10, color=MUTED))
    f.append(text((L + R) / 2, B + 42, "N, відліків", size=11.5, color=MUTED))
    for v, lab in ((0, "1"), (1, "10"), (2, "100"), (3, "1000")):
        y = Y(v)
        f.append(line(L - 6, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 10, y + 4, lab, size=10, color=MUTED, anchor="end"))

    pts = [(X(b), Y(math.log10((2 ** b + 1) / 6.0))) for b in range(2, 13)]
    f.append(polyline(pts, POS, sw=3.0))
    f.append(line(X(bx0), Y(math.log10(0.5)), X(bx1), Y(math.log10(0.5)), color=NEG, sw=3.0))
    f.append(text(X(2.3), Y(2.75), "класична s²  =  q·(N+1)/6", size=12, color=POS,
                  bold=True, anchor="start"))
    f.append(text(X(2.3), Y(2.45), "нахил +1: росте разом із записом", size=10.5,
                  color=MUTED, italic=True, anchor="start"))
    f.append(text(X(4.6), Y(-0.06), "½⟨(Δy)²⟩ = q/2  — стоїть на місці", size=12, color=NEG,
                  bold=True, anchor="start"))

    # ── ПРАВА панель: флікер, чисельний дослід ──
    L2, R2, T2, B2 = 600, 928, 128, 388
    cx0, cx1 = 4.0, 12.0
    cy0, cy1 = 0.0, 6.4

    def X2(b):
        return L2 + (b - cx0) / (cx1 - cx0) * (R2 - L2)

    def Y2(v):
        return B2 - (v - cy0) / (cy1 - cy0) * (B2 - T2)

    f.append(text((L2 + R2) / 2, T2 - 34, "флікер  (α = −1)", size=13, bold=True))
    f.append(text((L2 + R2) / 2, T2 - 16, "чисельний дослід; вісь N логарифмічна", size=10.5,
                  color=MUTED, italic=True))
    f.append(line(L2, T2 - 6, L2, B2, color=INK, sw=2))
    f.append(line(L2, B2, R2 + 8, B2, color=INK, sw=2))
    for b, lab in ((4, "16"), (6, "64"), (8, "256"), (10, "1024"), (12, "4096")):
        x = X2(b)
        f.append(line(x, B2, x, B2 + 6, color=INK, sw=1.2))
        f.append(text(x, B2 + 20, lab, size=10, color=MUTED))
    f.append(text((L2 + R2) / 2, B2 + 42, "N, відліків", size=11.5, color=MUTED))
    for v in range(0, 7, 2):
        y = Y2(v)
        f.append(line(L2 - 6, y, L2, y, color=INK, sw=1.2))
        f.append(text(L2 - 10, y + 4, str(v), size=10, color=MUTED, anchor="end"))

    fl = [(4, 1.90), (6, 2.63), (8, 3.61), (10, 4.47), (12, 5.50)]
    pf = [(X2(b), Y2(v)) for b, v in fl]
    f.append(polyline(pf, POS, sw=3.0))
    for (px, py) in pf:
        f.append(circle(px, py, 3.8, fill=BG, stroke=POS, sw=1.8))
    f.append(line(X2(cx0), Y2(1.0), X2(cx1), Y2(1.0), color=NEG, sw=3.0))
    f.append(text(X2(4.3), Y2(6.0), "класична s²: пряма проти log N", size=11.5, color=POS,
                  bold=True, anchor="start"))
    f.append(text(X2(4.3), Y2(5.55), "тобто росте як ln N", size=10.5, color=MUTED,
                  italic=True, anchor="start"))
    f.append(text(X2(4.3), Y2(0.45), "½⟨(Δy)²⟩ — стоїть", size=11.5, color=NEG,
                  bold=True, anchor="start"))

    f.append(fitbox(92, 442, 836, 52,
                    "праворуч усе поділено на Алланову оцінку, щоб не залежати від умовних одиниць генератора;\n"
                    "кожне вчетверо довше вимірювання додає до класичної оцінки ту саму порцію — підпис логарифма",
                    size=11.5, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "math-convergence.svg"), W, H, *f)


# ── Вставка proj: один доданок по частоті й по фазі ─────────────────────────
def fig_phase_trick():
    W, H = 980, 412
    f = [text(W / 2, 32, "Один і той самий доданок: порахований по частоті й по фазі", size=17, bold=True),
         text(W / 2, 54, "перехід до фази прибирає внутрішню суму — три звертання до масиву замість 2m",
              size=12, color=MUTED, italic=True)]

    # ── ЛІВА панель: частотні дані ──
    PL, PR, PT, PB = 36, 470, 76, 348
    f.append(rect(PL, PT, PR - PL, PB - PT, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    f.append(text((PL + PR) / 2, 100, "журнал частоти y", size=14, bold=True))

    cw, gapc, ncell = 28, 5, 12
    x0 = PL + ((PR - PL) - (ncell * (cw + gapc) - gapc)) / 2
    for k in range(ncell):
        cx = x0 + k * (cw + gapc)
        if 2 <= k <= 5:
            fl, st = "#eaf0fd", NEG
        elif 6 <= k <= 9:
            fl, st = "#fdecea", POS
        else:
            fl, st = FILL, MUTED
        f.append(rect(cx, 118, cw, 30, fill=fl, stroke=st, sw=1.6, rx=4))

    def bracket(k1, k2, col, label, lx):
        a = x0 + k1 * (cw + gapc)
        b = x0 + k2 * (cw + gapc) + cw
        f.append(line(a, 158, a, 166, color=col, sw=1.8))
        f.append(line(b, 158, b, 166, color=col, sw=1.8))
        f.append(line(a, 166, b, 166, color=col, sw=1.8))
        f.append(text(lx, 186, label, size=12.5, color=col, bold=True))

    bracket(2, 5, NEG, "m відліків → ȳₖ", x0 + 3.5 * (cw + gapc))
    bracket(6, 9, POS, "ще m → ȳₖ₊ₘ", x0 + 7.5 * (cw + gapc) + cw)

    f.append(fitbox(PL + 24, 202, PR - PL - 48, 54,
                    "ȳₖ₊ₘ − ȳₖ  — різниця двох сусідніх середніх\nщоб дістати ОДИН доданок, треба скласти 2m чисел",
                    size=12.5))
    f.append(fitbox(PL + 106, 274, PR - PL - 212, 44, "O(m) на кожен доданок",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=2))

    # ── ПРАВА панель: фазові дані ──
    QL, QR = 510, 944
    f.append(rect(QL, PT, QR - QL, PB - PT, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    f.append(text((QL + QR) / 2, 100, "фаза x — накопичена похибка часу", size=14, bold=True))

    AL, AR, AB = QL + 30, QR - 22, 182
    vals = [0, 6, 10, 9, 14, 20, 23, 22, 28, 34, 33, 39, 44]
    step = (AR - AL) / (len(vals) - 1)
    f.append(line(AL - 10, AB, AR + 8, AB, color=INK, sw=1.6))
    pts = [(AL + i * step, AB - v * 1.35) for i, v in enumerate(vals)]
    f.append(polyline(pts, MUTED, sw=1.8))
    for i, (px, py) in enumerate(pts):
        f.append(circle(px, py, 3.0, fill=BG, stroke=MUTED, sw=1.3))
    for i, lab, col in ((2, "xₖ", NEG), (6, "xₖ₊ₘ", NEG), (10, "xₖ₊₂ₘ", POS)):
        px, py = pts[i]
        f.append(line(px, py, px, AB, color=col, sw=1.2, dash="3 4"))
        f.append(circle(px, py, 5.4, fill=col, stroke=col, sw=1.6))
        f.append(text(px, AB + 20, lab, size=13, color=col, bold=True))

    f.append(fitbox(QL + 24, 214, QR - QL - 48, 54,
                    "ȳₖ = (xₖ₊ₘ − xₖ) / (m·τ₀)\nȳₖ₊ₘ − ȳₖ = (xₖ₊₂ₘ − 2xₖ₊ₘ + xₖ) / (m·τ₀)",
                    size=12.5))
    f.append(fitbox(QL + 106, 274, QR - QL - 212, 44, "O(1) на кожен доданок",
                    size=14, bold=True, fill="#eafaf1", stroke=FIELD, sw=2))

    f.append(text(W / 2, 382, "обидві форми дають ТЕ САМЕ число — різна тільки ціна",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "compute-phase-trick.svg"), W, H, *f)


# ── Вставка proj: неперекривна проти перекривної драбини ─────────────────────
def fig_strides():
    W, H = 960, 472
    f = [text(W / 2, 32, "Дві драбини по тому самому запису", size=17, bold=True),
         text(W / 2, 54, "M = 12 вимірів, N = 13 фазових точок, m = 2; рядок — одна трійка xₖ, xₖ₊ₘ, xₖ₊₂ₘ",
              size=12, color=MUTED, italic=True)]
    f.append(line(W / 2, 76, W / 2, 436, color="#d8dde3", sw=1.4))

    def panel(L, R, head, starts, summary, col):
        f.append(text((L + R) / 2, 96, head, size=14, bold=True, color=col))
        sp = (R - L) / 12.0
        f.append(line(L - 6, 128, R + 6, 128, color=MUTED, sw=1.2))
        for k in range(13):
            xk = L + k * sp
            f.append(line(xk, 124, xk, 132, color=MUTED, sw=1.2))
            if k % 2 == 0:
                f.append(text(xk, 118, str(k), size=10.5, color=MUTED))
        y = 156
        for s in starts:
            a, b = L + s * sp, L + (s + 4) * sp
            f.append(line(a, y, b, y, color=col, sw=2.2))
            for k in (s, s + 2, s + 4):
                f.append(circle(L + k * sp, y, 4.4, fill=col, stroke=col, sw=1.4))
            y += 24
        f.append(fitbox(L + 6, 366, R - L - 12, 56, summary, size=12.5,
                        fill=FILL, stroke=col, sw=1.8))

    panel(56, 440, "неперекривна: крок m",
          [0, 2, 4, 6, 8],
          "⌊M/m⌋ − 1 = 5 доданків\nкожен вимір потрапляє рівно в одне середнє", NEG)
    panel(520, 904, "перекривна: крок τ₀",
          list(range(9)),
          "N − 2m = 9 доданків\nкожен вимір бере участь у m середніх", POS)

    f.append(text(W / 2, 456, "той самий запис, той самий τ — різна лише кількість трійок, які з нього дістали",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "compute-strides.svg"), W, H, *f)


# ── Вставка proj: доданки проти ступенів свободи ─────────────────────────────
def fig_tau_limit():
    W, H = 960, 466
    N = 3601
    f = [text(W / 2, 32, "Доданків багато, а незалежної інформації мало", size=17, bold=True),
         text(W / 2, 54, "запис на годину: M = 3600 вимірів із кроком τ₀ = 1 с, перекривна оцінка",
              size=12, color=MUTED, italic=True)]

    L, R, T, B = 122, 690, 104, 356
    lx0, lx1 = -0.5, 10.7          # log2(τ/τ₀)
    ly0, ly1 = -0.25, 3.75         # log10(кількість)

    def X(v):
        return L + (v - lx0) / (lx1 - lx0) * (R - L)

    def Y(v):
        return B - (v - ly0) / (ly1 - ly0) * (B - T)

    # зона малої довіри
    f.append(rect(L, Y(1.0), R - L, B - Y(1.0), fill="#fdecea", stroke="none", sw=0, rx=0))
    f.append(text(L + 12, Y(1.0) + 18, "менш як 10 ступенів свободи", size=11.5, color=POS,
                  anchor="start", bold=True))

    f.append(line(L, T - 10, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 10, B, color=INK, sw=2))
    f.append(text(R + 10, B + 34, "τ, с  (лог)", size=12.5, bold=True, anchor="end"))
    f.append(text(L - 4, T - 20, "кількість (лог)", size=12.5, bold=True, anchor="start"))
    for e in (0, 2, 4, 6, 8, 10):
        x = X(e)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 22, str(2 ** e), size=11, color=MUTED))
    for e in (0, 1, 2, 3):
        y = Y(e)
        f.append(line(L - 6, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 11, y + 4, str(10 ** e), size=11, color=MUTED, anchor="end"))

    terms, edfs = [], []
    for e in range(0, 11):
        m = 2 ** e
        k = N - 2 * m
        edf = (3.0 * (N - 1) / (2.0 * m) - 2.0 * (N - 2) / N) * (4.0 * m * m / (4.0 * m * m + 5.0))
        terms.append((X(e), Y(math.log10(k))))
        edfs.append((X(e), Y(math.log10(edf))))
    f.append(polyline(terms, NEG, sw=3.0))
    f.append(polyline(edfs, POS, sw=3.0))
    for (px, py) in terms:
        f.append(circle(px, py, 3.6, fill=BG, stroke=NEG, sw=1.8))
    for (px, py) in edfs:
        f.append(circle(px, py, 3.6, fill=BG, stroke=POS, sw=1.8))

    # виноска
    f.append(fitbox(724, 150, 214, 96,
                    "τ = 1024 с:\n1553 доданки в сумі,\nа ступенів свободи ≈ 3\n— крива вже про оцінку,\nа не про генератор",
                    size=11.5, fill=FILL, stroke=POS, sw=1.8))
    f.append(arrow(722, 214, edfs[-1][0] + 12, edfs[-1][1] - 6, color=POS, sw=1.6))

    # легенда
    ly = 404
    f.append(line(L, ly, L + 34, ly, color=NEG, sw=3.0))
    f.append(text(L + 44, ly + 5, "доданків у сумі: N − 2m", size=12.5, color=INK, anchor="start"))
    f.append(line(L + 300, ly, L + 334, ly, color=POS, sw=3.0))
    f.append(text(L + 344, ly + 5, "ступенів свободи (білий частотний шум)",
                  size=12.5, color=INK, anchor="start"))
    f.append(text(W / 2, 442, "число доданків майже не спадає, а довіра — спадає як 1/τ",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "compute-tau-limit.svg"), W, H, *f)


def _sup(n):
    """Верхній індекс степеня (з мінусом), напр. −11 → ⁻¹¹."""
    smap = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
            "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(smap[c] for c in str(n))


if __name__ == "__main__":
    fig_divergence()
    fig_sigma_tau()
    fig_grades()
    fig_timeline()
    fig_highpass()
    fig_convergence()
    fig_phase_trick()
    fig_strides()
    fig_tau_limit()
    print("OK: 9 SVG -> img/")
