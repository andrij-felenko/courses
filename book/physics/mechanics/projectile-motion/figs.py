# -*- coding: utf-8 -*-
"""Фігури до теми «Рух тіла, кинутого під кутом (балістична траєкторія)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOR = "#2457d6"   # горизонтальна складова / стале — холодне синє
VER = "#c0392b"   # вертикальна складова / падіння — гаряче червоне
RES = "#7d3c98"   # повна швидкість — фіолетове
WIN = "#27ae60"   # найкращий кут (45°) — зелене


def ball(cx, cy, r=6):
    return circle(cx, cy, r, fill="#fef6e7", stroke=VER, sw=2)


def ground(x1, x2, y, n=10):
    out = line(x1, y, x2, y, color=LINE, sw=2)
    step = (x2 - x1) / n
    for i in range(n):
        gx = x1 + i * step
        out += line(gx, y, gx - 7, y + 8, color=MUTED, sw=1.0)
    return out


# ── Фігура 1: розклад швидкості вздовж дуги ──────────────────────────────────
def fig_velocity_components():
    W, H = 820, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Швидкість = стала горизонтальна + мінлива вертикальна складова",
                  size=15.5, bold=True))

    gy, Hpx, ax, half = 395, 235, 415, 325

    def yof(x):
        return gy - Hpx * (1 - ((x - ax) / half) ** 2)

    # земля + парабола
    f.append(ground(70, 748, gy, n=13))
    pts = []
    x = 90.0
    while x <= 740.001:
        pts.append("%.1f,%.1f" % (x, yof(x)))
        x += 5
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), "#b9c0cc"))

    VX = 75.0  # довжина горизонтальної стрілки (усюди однакова)

    def cluster(px, vy, label_side):
        """px — точка на дузі; vy>0 — угору, vy<0 — вниз, 0 — вершина."""
        py = yof(px)
        out = ball(px, py, 6)
        tipx = px + VX
        # горизонтальна складова — синя стрілка, стала
        out += arrow(px, py, tipx, py, color=HOR, sw=3)
        if abs(vy) < 1:   # вершина: лише горизонтальна
            out += text((px + tipx) / 2, py - 12, "v = vₓ", size=13, bold=True, color=RES)
            out += text(px, py + 26, "у вершині лише vₓ", size=11.5, color=MUTED)
            return out
        tipy = py - vy
        # вертикальна складова — червона стрілка
        out += arrow(px, py, px, tipy, color=VER, sw=3)
        # рамка розкладу (пунктир) + повна швидкість (діагональ)
        out += line(tipx, py, tipx, tipy, color=MUTED, sw=1.1, dash="3,4")
        out += line(px, tipy, tipx, tipy, color=MUTED, sw=1.1, dash="3,4")
        out += arrow(px, py, tipx, tipy, color=RES, sw=3)
        # підписи
        out += text((px + tipx) / 2, py + (18 if vy > 0 else -8), "vₓ", size=13, bold=True, color=HOR)
        vylab_y = (py + tipy) / 2 + 4
        out += text(px - 12, vylab_y, "v_y", size=13, bold=True, color=VER, anchor="end")
        out += text(tipx + 8, tipy + (0 if vy > 0 else 6), "v", size=14, bold=True, color=RES, anchor="start")
        return out

    f.append(cluster(205, 70, "up"))     # висхідна ділянка: v_y угору
    f.append(cluster(415, 0, "top"))     # вершина: v_y = 0
    f.append(cluster(625, -70, "down"))  # низхідна: v_y униз

    # підписи фаз під точками
    f.append(text(205, 300, "зліт", size=11.5, color=MUTED))
    f.append(text(625, 372, "спуск", size=11.5, color=MUTED))

    b, bw, bh = textbox(W / 2, 462,
                        "Горизонтальна складова vₓ = v₀·cosα однакова всюди — вбік ніщо не діє.\n"
                        "Вертикальна v_y = v₀·sinα тане до нуля у вершині й відроджується вниз — це вільне падіння.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "velocity-components.svg"), W, H, *f)


# ── Фігура 2: політ = пряма інерції мінус падіння ∝ t² ───────────────────────
def fig_parabola_build():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Політ = рівномірний рух по прямій  −  вільне падіння (∝ t²)",
                  size=15.5, bold=True))

    lx, ly = 90, 430          # точка кидка (на землі)
    dx, up, gu = 112.0, 90.0, 15.0
    X = lambda k: lx + dx * k
    y_in = lambda k: ly - up * k          # інерційна пряма
    y_ac = lambda k: ly - up * k + gu * k * k   # справжній політ

    f.append(ground(70, 792, ly, n=15))

    # інерційна пряма (обрізана, щоб не вилазила вгору)
    kk = 3.7
    f.append(line(lx, ly, X(kk), y_in(kk), color=HOR, sw=2.2, dash="7,6"))
    f.append(text(X(3.75) + 6, y_in(3.75) - 4, "якби не тяжіння —", size=12.5, bold=True, color=HOR, anchor="start"))
    f.append(text(X(3.75) + 6, y_in(3.75) + 13, "летіло б по прямій", size=12.5, color=HOR, anchor="start"))

    # справжня парабола
    pts, k = [], 0.0
    while k <= 6.001:
        pts.append("%.1f,%.1f" % (X(k), y_ac(k)))
        k += 0.2
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), VER))

    # провали ∝ t² (1:4:9:16)
    props = {1: "×1", 2: "×4", 3: "×9", 4: "×16"}
    for k in (1, 2, 3, 4):
        x = X(k)
        f.append(line(x, y_in(k), x, y_ac(k), color=MUTED, sw=1.4, dash="4,4"))
        f.append(circle(x, y_in(k), 3.2, fill=HOR, stroke=HOR, sw=1))    # точка на прямій
        f.append(circle(x, y_ac(k), 4.5, fill="#fef6e7", stroke=VER, sw=2))  # справжня точка
        ymid = (y_in(k) + y_ac(k)) / 2
        f.append(text(x + 12, ymid + 4, props[k], size=12.5, bold=True, color=VER, anchor="start"))

    # точка кидка
    f.append(circle(lx, ly, 5, fill="#fef6e7", stroke=VER, sw=2))

    # часові позначки на землі
    for k in range(7):
        x = X(k)
        f.append(line(x, ly, x, ly + 6, color=INK, sw=1.4))
        f.append(text(x, ly + 22, "t=%d" % k, size=11, color=MUTED))

    b, bw, bh = textbox(W / 2, 476,
                        "Уперед — рівні кроки за рівний час (пряма). Униз — провал ½g·t², що росте як 1 : 4 : 9 : 16.\n"
                        "Пряма мінус ці квадратичні провали й згинає політ у параболу.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "parabola-build.svg"), W, H, *f)


# ── Фігура 3: дальність від кута — 45° найдалі, доповняльні кути в одну точку ─
def fig_range_vs_angle():
    W, H = 780, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий кидок під різними кутами: найдалі — під 45°",
                  size=15.5, bold=True))

    ox, gy = 110, 402
    S = 560.0            # горизонтальний масштаб (дальність при 45° у px)

    specs = [(15, "#e67e22"), (30, "#c0392b"), (45, WIN), (60, "#2457d6"), (75, "#7d3c98")]

    f.append(ground(90, 700, gy, n=14))

    for ang, col in specs:
        a = math.radians(ang)
        R = S * math.sin(2 * a)          # дальність у px
        Hpk = (S / 2) * math.sin(a) ** 2  # висота підйому у px
        thick = 3.4 if ang == 45 else 2.2
        pts, fr = [], 0.0
        while fr <= 1.0001:
            x = ox + R * fr
            y = gy - 4 * Hpk * fr * (1 - fr)
            pts.append("%.1f,%.1f" % (x, y))
            fr += 0.02
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (" ".join(pts), col, thick))
        # підпис кута біля вершини
        xv, yv = ox + R * 0.5, gy - Hpk
        f.append(text(xv, yv - 8, "%d°" % ang, size=12.5, bold=True, color=col))

    # спільні точки падіння доповняльних кутів
    def landing(ang):
        return ox + S * math.sin(2 * math.radians(ang))

    x45 = landing(45)
    x3060 = landing(30)
    x1575 = landing(15)
    for xx, lab, col in [(x1575, "15° і 75°", MUTED), (x3060, "30° і 60°", MUTED)]:
        f.append(circle(xx, gy, 4.5, fill=BG, stroke=INK, sw=1.8))
        f.append(text(xx, gy + 24, lab, size=11, color=col))
    f.append(circle(x45, gy, 5, fill=WIN, stroke=WIN, sw=1.5))
    f.append(text(x45, gy + 24, "45° — найдалі", size=11.5, bold=True, color=WIN))

    b, bw, bh = textbox(W / 2, 462,
                        "Дальність ∝ sin(2α): найбільша під 45°. Кути, що доповнюються до 90° (30°/60°, 15°/75°),\n"
                        "падають у ту саму точку — пологий постріл швидкий і низький, крутий довгий і високий.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "range-vs-angle.svg"), W, H, *f)


# ── Фігура 4 (історія): як уявляли політ — Арістотель → Тарталья → Ґалілей ───
def fig_trajectory_history():
    W, H = 940, 458
    OLD = "#6b7280"   # застаріле уявлення — сіре
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Як уявляли політ ядра: від Арістотеля до Ґалілея",
                  size=16, bold=True))

    gy = 340
    panels = [
        (40,  "Арістотель",       "пряма, тоді прямовисне падіння"),
        (350, "Тарталья · 1537",  "пряма + дуга кола + падіння"),
        (660, "Ґалілей · 1638",   "єдина плавна парабола"),
    ]
    for x0, ttl, sub in panels:
        cx = x0 + 125
        f.append(text(cx, 66, ttl, size=14, bold=True))
        f.append(text(cx, 86, sub, size=11.5, color=MUTED))
        f.append(ground(x0 + 20, x0 + 235, gy, n=7))
        lx = x0 + 40
        f.append(line(lx - 11, gy, lx + 8, gy - 9, color=INK, sw=4))   # маленька гармата

    # A — Арістотель: різкий злам, дузі немає звідки взятися
    x0 = 40; lx = x0 + 40
    f.append(line(lx, gy, x0 + 150, 168, color=OLD, sw=3.2))
    f.append(line(x0 + 150, 168, x0 + 150, gy, color=OLD, sw=3.2))
    f.append(circle(x0 + 150, 168, 5, fill=BG, stroke=VER, sw=2.4))    # злам — червона цятка

    # B — Тарталья: пряма + дуга кола (шульдер) + вертикаль
    x0 = 350; lx = x0 + 40
    d = ("M %.0f %.0f L %.0f %.0f Q %.0f %.0f %.0f %.0f L %.0f %.0f"
         % (lx, gy, x0 + 118, 182, x0 + 165, 138, x0 + 196, 188, x0 + 196, gy))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (d, HOR))

    # C — Ґалілей: чиста парабола
    x0 = 660; cxp = x0 + 120; halfw = 90.0; peak = 150.0
    pts, x = [], cxp - halfw
    while x <= cxp + halfw + 0.01:
        y = gy - (gy - peak) * (1 - ((x - cxp) / halfw) ** 2)
        pts.append("%.1f,%.1f" % (x, y))
        x += 4
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.4"/>'
             % (" ".join(pts), WIN))

    b, bw, bh = textbox(W / 2, 426,
                        "Арістотель: насильницький рух прямою, тоді раптом прямовисне падіння — плавній дузі немає звідки взятися.\n"
                        "Тарталья зігнув злам дугою кола (1537); Ґалілей вивів єдину параболу з двох незалежних рухів (1638).",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "trajectory-history.svg"), W, H, *f)


# ── Фігура 5 (історія): ядро Ньютона — від пострілу до орбіти ────────────────
def _cap_pts(cx, cy, r, ymax, n=56):
    """Точки видимої «шапки» кола (центр за межами полотна, r >> висота полотна) —
    щоб не писати в SVG буквальний cx/cy, який лежить поза viewBox."""
    cos_t = max(-1.0, min(1.0, (cy - ymax) / r))
    tmax = math.acos(cos_t)
    pts = []
    for i in range(n + 1):
        t = -tmax + (2 * tmax) * i / n
        pts.append((cx + r * math.sin(t), cy - r * math.cos(t)))
    return pts


def fig_newton_cannonball():
    W, H = 760, 650
    SKY = "#eaf2fb"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ядро Ньютона: розганяй постріл — і падіння стає орбітою",
                  size=15.5, bold=True))

    Cx, Cy, R = 380.0, 800.0, 470.0
    Lx, Ly = 380.0, 305.0            # жерло на вершині гори, ~25 px над поверхнею

    # Земля — величезне коло, центр далеко під полотном; малюємо лише видиму
    # «шапку» полігоном (без cx/cy поза межами), суцільно залитим до низу кадру.
    cap = _cap_pts(Cx, Cy, R, H)
    ex0, ey0 = cap[0]; exN, eyN = cap[-1]
    poly = " ".join("%.1f,%.1f" % p for p in cap)
    d_earth = "M %.1f,%.1f L %s L %.1f,%.1f Z" % (ex0, H + 40, poly, exN, H + 40)
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d_earth, SKY, MUTED))
    f.append(text(Cx, 545, "Земля", size=15, color=MUTED, bold=True))

    # гора + ствол гармати
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (Cx - 26, Cy - R, Cx + 26, Cy - R, Lx, Ly, "#d8dee7", MUTED))
    f.append(line(Lx, Ly, Lx + 26, Ly, color=INK, sw=6))
    f.append(text(Lx, Ly - 16, "гармата на горі", size=11.5, color=INK))

    def surf(theta_deg):
        a = math.radians(theta_deg)
        return (Cx + R * math.sin(a), Cy - R * math.cos(a))

    # два постріли, що падають на Землю (старт горизонтальний → контроль на висоті жерла)
    for th, col in [(20, VER), (48, "#e67e22")]:
        ex, ey = surf(th)
        d = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (Lx, Ly, ex, Ly, ex, ey)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, col))
        f.append(circle(ex, ey, 4.5, fill=BG, stroke=col, sw=2.2))

    e1x, e1y = surf(20); e2x, e2y = surf(48)
    f.append(text(e1x + 12, e1y + 3, "повільно —", size=11, color=VER, anchor="start"))
    f.append(text(e1x + 12, e1y + 18, "впаде близько", size=11, color=VER, anchor="start"))
    f.append(text(e2x - 12, e2y + 6, "швидше — далі", size=11, color="#e67e22", anchor="end"))

    # колова орбіта через жерло (радіус = відстань жерла до центру) — та ж хитрість:
    # лише видима дуга, без буквального cx/cy поза полотном.
    Ro = Cy - Ly
    ocap = _cap_pts(Cx, Cy, Ro, H)
    opoly = " ".join("%.1f,%.1f" % p for p in ocap)
    f.append('<polyline points="%s" fill="none" stroke="%s" '
             'stroke-width="2.6" stroke-dasharray="7,6"/>' % (opoly, WIN))
    f.append(text(150, 300, "досить швидко —", size=12.5, color=WIN, bold=True))
    f.append(text(150, 318, "оминає Землю: орбіта", size=12.5, color=WIN, bold=True))

    b, bw, bh = textbox(W / 2, 615,
                        "Стріляй горизонтально дедалі швидше — парабола падіння витягується, аж поки Земля\n"
                        "не тікає з-під ядра рівно так само швидко, як воно падає. Тоді ядро не сягає землі — це орбіта.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "newton-cannonball.svg"), W, H, *f)


# ── Числове ядро для фігур із квадратичним опором (self-contained RK4) ────────
G = 9.81
K_BALL = 6.2095e-3     # c/m для м'яча (Cd=0.35, A=0.0042, m=0.145) → v_т ≈ 39.8 м/с
V0 = 40.0
RVAC = V0 * V0 / G     # дальність у порожнечі при 45° ≈ 163.1 м


def _deriv(s, k):
    x, y, vx, vy = s
    sp = math.hypot(vx, vy)
    return (vx, vy, -k * sp * vx, -G - k * sp * vy)


def _rk4(s, k, dt):
    a = _deriv(s, k)
    b = _deriv(tuple(si + dt / 2 * ai for si, ai in zip(s, a)), k)
    c = _deriv(tuple(si + dt / 2 * bi for si, bi in zip(s, b)), k)
    d = _deriv(tuple(si + dt * ci for si, ci in zip(s, c)), k)
    return tuple(si + dt / 6 * (ai + 2 * bi + 2 * ci + di)
                 for si, ai, bi, ci, di in zip(s, a, b, c, d))


def _flight(v0, ang, k, dt=0.01, collect=False):
    """Політ до перетину землі; повертає (дальність, вершина_x, вершина_y, кут_падіння) або шлях."""
    t = math.radians(ang)
    s = (0.0, 0.0, v0 * math.cos(t), v0 * math.sin(t))
    apx = apy = 0.0
    path = [(0.0, 0.0)]
    while True:
        nx = _rk4(s, k, dt)
        if nx[1] > apy:
            apy, apx = nx[1], nx[0]
        if collect:
            path.append((nx[0], max(nx[1], 0.0)))
        if nx[1] <= 0.0 and nx[0] > 0.0:
            fr = s[1] / (s[1] - nx[1])
            xr = s[0] + fr * (nx[0] - s[0])
            vx = s[2] + fr * (nx[2] - s[2])
            vy = s[3] + fr * (nx[3] - s[3])
            land = math.degrees(math.atan2(-vy, vx))
            if collect:
                path[-1] = (xr, 0.0)
                return path
            return xr, apx, apy, land
        s = nx


# ── Фігура A: асиметрія — крутіший спуск і зсунута вершина ────────────────────
def fig_drag_asymmetry():
    W, H = 840, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Опір ламає дзеркальність: зліт пологий, спуск крутий",
                  size=15.5, bold=True))

    ox, gy = 78, 396
    sx = (770 - ox) / 172.0            # px на метр (умістити 163 м порожнечі)
    sy = (gy - 92) / 43.0
    X = lambda x: ox + x * sx
    Y = lambda y: gy - y * sy

    f.append(ground(ox, 782, gy, n=15))

    # порожня парабола (світла, для контрасту): y = x − (g/2v²cos²)·x²
    b = G / (2 * V0 * V0 * 0.5)
    pts, x = [], 0.0
    while x <= RVAC + 0.01:
        pts.append("%.1f,%.1f" % (X(x), Y(x - b * x * x)))
        x += 1.5
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7,6"/>'
             % (" ".join(pts), "#9db0cc"))
    f.append(text(X(150), Y(6) + 4, "порожнеча — 163 м", size=11.5, color="#5b7bb0", anchor="middle"))

    # дугa з опором (жирна червона)
    path = _flight(V0, 45.0, K_BALL, dt=0.006, collect=True)
    pts = " ".join("%.1f,%.1f" % (X(px), Y(py)) for px, py in path)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (pts, VER))

    xr, apx, apy, land = _flight(V0, 45.0, K_BALL, dt=0.002)

    # вершина з опором + вертикаль середини
    f.append(circle(X(apx), Y(apy), 4.5, fill="#fef6e7", stroke=VER, sw=2))
    f.append(line(X(xr / 2), gy, X(xr / 2), gy + 8, color=MUTED, sw=1.4))
    f.append(line(X(apx), Y(apy), X(apx), gy, color=MUTED, sw=1.1, dash="3,4"))
    f.append(text(X(apx) + 6, Y(apy) - 8, "вершина — за серединою", size=11, color=VER, anchor="start"))
    f.append(text(X(xr / 2), gy + 22, "середина", size=10.5, color=MUTED))

    # кути зльоту й падіння
    f.append(text(X(6), Y(9), "45°", size=12.5, bold=True, color=INK, anchor="start"))
    f.append(text(X(xr) - 4, Y(9), "≈57° — крутіше", size=12, bold=True, color=VER, anchor="end"))
    f.append(circle(X(xr), gy, 4.5, fill=VER, stroke=VER, sw=1.5))
    f.append(text(X(xr), gy + 22, "96 м", size=11, bold=True, color=VER))

    bb, bw, bh = textbox(W / 2, 446,
                         "Той самий кидок під 45°. З опором (червона) вершина зсувається ЗА середину, а спуск\n"
                         "крутіший за зліт (падає під ~57°, не 45°): злітати вільно ще можна, а падати вже впирається в опір.",
                         size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(bb)
    return render(os.path.join(IMG, "drag-asymmetry.svg"), W, H, *f)


# ── Фігура B: дальність від кута — пік тікає з 45° і симетрія кутів гине ───────
def fig_range_angle_drag():
    W, H = 840, 494
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Найкращий кут тікає з-під 45°, а рівність доповняльних кутів гине",
                  size=15.5, bold=True))

    ox, oy, gy, top = 104, 404, 404, 74
    X = lambda a: ox + a * (760 - ox) / 92.0
    Y = lambda R: gy - R * (gy - top) / 176.0

    # осі
    f.append(line(ox, top - 6, ox, gy, color=INK, sw=1.6))
    f.append(line(ox, gy, 772, gy, color=INK, sw=1.6))
    for a in range(0, 91, 15):
        f.append(line(X(a), gy, X(a), gy + 6, color=INK, sw=1.4))
        f.append(text(X(a), gy + 22, "%d°" % a, size=11, color=MUTED))
    for R in range(0, 176, 25):
        f.append(line(ox - 6, Y(R), ox, Y(R), color=INK, sw=1.4))
        f.append(text(ox - 12, Y(R) + 4, "%d" % R, size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox - 8, top - 12, "дальність, м", size=11.5, color=MUTED, anchor="start"))

    # порожня крива: R = RVAC·sin(2α)
    pts, a = [], 0.0
    while a <= 90.01:
        pts.append("%.1f,%.1f" % (X(a), Y(RVAC * math.sin(2 * math.radians(a)))))
        a += 1.0
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,6"/>'
             % (" ".join(pts), HOR))

    # крива з опором (обчислена)
    pts, a = [], 2.0
    dragR = {}
    while a <= 88.01:
        R = _flight(V0, a, K_BALL, dt=0.01)[0]
        dragR[round(a)] = R
        pts.append("%.1f,%.1f" % (X(a), Y(R)))
        a += 1.0
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), VER))

    # піки
    f.append(line(X(45), Y(0), X(45), Y(RVAC), color=HOR, sw=1.1, dash="3,4"))
    f.append(text(X(45), top - 12, "порожнеча: пік рівно 45°", size=11.5, bold=True, color=HOR))
    f.append(line(X(41), gy, X(41), Y(96.4), color=VER, sw=1.1, dash="3,4"))
    f.append(circle(X(41), Y(96.4), 4.5, fill=VER, stroke=VER, sw=1.5))
    f.append(text(X(41) - 6, Y(96.4) - 10, "опір: пік ≈ 41°", size=11.5, bold=True, color=VER, anchor="end"))

    # доповняльна пара 30°/60°
    for a in (30, 60):
        Rv = RVAC * math.sin(2 * math.radians(a))
        f.append(circle(X(a), Y(Rv), 3.6, fill=BG, stroke=HOR, sw=1.8))
        f.append(circle(X(a), Y(dragR[a]), 4.2, fill="#fef6e7", stroke=VER, sw=2))
    f.append(text(X(30), Y(dragR[30]) + 20, "30°→91 м", size=10.5, bold=True, color=VER))
    f.append(text(X(60) + 4, Y(dragR[60]) - 12, "60°→80 м", size=10.5, bold=True, color=VER, anchor="start"))
    f.append(text(X(45) + 2, Y(141) + 4, "у порожнечі 30° і 60° — рівні (141 м)", size=10.5, color="#5b7bb0", anchor="start"))

    bb, bw, bh = textbox(W / 2, 470,
                         "Порожня крива (синя) симетрична, пік точно на 45°. Крива з опором (червона) нижча й скошена:\n"
                         "пік сповз до ≈41°, і доповняльні кути більше не рівні — пологіший 30° б'є далі за крутий 60°.",
                         size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(bb)
    return render(os.path.join(IMG, "range-angle-drag.svg"), W, H, *f)


# ── Фігура C: універсальна крива — оптимальний кут від v₀/v_т ─────────────────
def fig_optimal_angle_ratio():
    W, H = 800, 512
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Одне число вирішує все: оптимальний кут від v₀ / v_т",
                  size=15.5, bold=True))

    ox, gy, top = 108, 400, 76
    X = lambda r: ox + r * (748 - ox) / 8.4
    Y = lambda a: gy - (a - 23) * (gy - top) / 24.0

    # верифіковані точки (RK4): ratio → оптимальний кут
    data = [(0.1, 44.9), (0.25, 44.6), (0.5, 43.7), (1.0, 41.0),
            (2.0, 36.2), (3.0, 33.0), (5.0, 29.3), (8.0, 26.4)]

    # осі
    f.append(line(ox, top - 6, ox, gy, color=INK, sw=1.6))
    f.append(line(ox, gy, 760, gy, color=INK, sw=1.6))
    for r in range(0, 9):
        f.append(line(X(r), gy, X(r), gy + 6, color=INK, sw=1.4))
        f.append(text(X(r), gy + 22, "%d" % r, size=11, color=MUTED))
    f.append(text((ox + 748) / 2, gy + 40, "v₀ / v_т  (швидкість кидка ÷ гранична)", size=11.5, color=MUTED))
    for a in range(25, 46, 5):
        f.append(line(ox - 6, Y(a), ox, Y(a), color=INK, sw=1.4))
        f.append(text(ox - 12, Y(a) + 4, "%d°" % a, size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox - 8, top - 12, "оптимальний кут", size=11.5, color=MUTED, anchor="start"))

    # межа порожнечі 45°
    f.append(line(ox, Y(45), 748, Y(45), color=WIN, sw=1.6, dash="6,5"))
    f.append(text(730, Y(45) - 8, "порожнеча — 45°", size=11.5, bold=True, color=WIN, anchor="end"))

    # крива
    pts = " ".join("%.1f,%.1f" % (X(r), Y(a)) for r, a in data)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (pts, VER))
    for r, a in data:
        f.append(circle(X(r), Y(a), 3.4, fill="#fef6e7", stroke=VER, sw=1.8))

    # приклади-мітки
    def mark(r, a, lab, dxp, dyp):
        f.append(circle(X(r), Y(a), 5, fill=VER, stroke=VER, sw=1.5))
        f.append(text(X(r) + dxp, Y(a) + dyp, lab, size=11, bold=True, color=INK,
                      anchor="start" if dxp > 0 else "end"))
    mark(1.0, 41.0, "м'яч (v₀≈v_т) → 41°", 10, -6)
    mark(3.0, 33.0, "різкий удар легкого м'яча → 33°", 10, -4)
    mark(8.0, 26.4, "ядро, куля (v₀≫v_т) → 26°", -10, 16)

    bb, bw, bh = textbox(W / 2, 487,
                         "Уся сім'я траєкторій зводиться до одного числа — v₀/v_т. Мала швидкість (слабкий опір) → кут коло 45°;\n"
                         "що дужче кидок перевищує граничну швидкість, то нижче осідає оптимум — до 30° і менше.",
                         size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(bb)
    return render(os.path.join(IMG, "optimal-angle-ratio.svg"), W, H, *f)


# ── Фігура (математика): траєкторія-парабола — корені 0 і R, вершина при R/2 ──
def fig_trajectory_parabola():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Траєкторія y = A·x − B·x²  —  парабола вниз",
                  size=15.5, bold=True))

    ox, gy = 110, 372          # x = 0 (кидок), рівень землі
    Rpx, Hpx = 590.0, 205.0    # дальність і висота у px
    apx, apy = ox + Rpx / 2, gy - Hpx

    def px(fr):
        return ox + Rpx * fr

    def py(fr):
        return gy - 4 * Hpx * fr * (1 - fr)

    # осі
    f.append(line(ox, gy + 2, ox, 74, color=MUTED, sw=1.3))          # вісь y
    f.append(ground(ox - 18, ox + Rpx + 66, gy, n=14))               # земля / вісь x

    # парабола
    pts, fr = [], 0.0
    while fr <= 1.0001:
        pts.append("%.1f,%.1f" % (px(fr), py(fr)))
        fr += 0.01
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts), VER))

    # вершина + пунктири до осей
    f.append(line(apx, apy, apx, gy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(apx, apy, ox, apy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(circle(apx, apy, 5, fill="#fef6e7", stroke=VER, sw=2))
    f.append(text(apx + 12, apy - 8, "вершина (R/2, H)", size=12.5, bold=True, color=VER, anchor="start"))
    f.append(text(ox - 12, apy + 4, "H", size=14, bold=True, color=VER, anchor="end"))

    # корені (точки на землі)
    f.append(circle(ox, gy, 5, fill=WIN, stroke=WIN, sw=1.5))
    f.append(circle(ox + Rpx, gy, 5, fill=WIN, stroke=WIN, sw=1.5))
    f.append(text(ox, gy + 24, "x = 0", size=12, bold=True, color=WIN))
    f.append(text(ox + Rpx, gy + 24, "x = R", size=12, bold=True, color=WIN))

    # подвійні стрілки R/2 | R/2 (вершина рівно між коренями)
    yb = gy + 46
    f.append(arrow(apx, yb, ox, yb, color=HOR, sw=1.6))
    f.append(arrow(apx, yb, ox + Rpx, yb, color=HOR, sw=1.6))
    for xx in (ox, apx, ox + Rpx):
        f.append(line(xx, gy + 34, xx, yb + 6, color=MUTED, sw=1))
    f.append(text((ox + apx) / 2, yb - 7, "R/2", size=11.5, bold=True, color=HOR))
    f.append(text((apx + ox + Rpx) / 2, yb - 7, "R/2", size=11.5, bold=True, color=HOR))

    b, bw, bh = textbox(W / 2, 478,
                        "A = tan α,  B = g/(2·v₀²·cos²α).  Корені y = 0: x = 0 (кидок) і x = A/B = R (падіння).\n"
                        "Вершина параболи стоїть рівно між коренями, при x = R/2, заввишки H — це й є симетрія дуги.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "trajectory-parabola.svg"), W, H, *f)


# ── Фігура (математика): cos α, sin α і дальність sin 2α від кута — пік на 45° ─
def fig_range_factors():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дальність ∝ sin 2α = 2·sin α·cos α: добуток двох суперників, пік на 45°",
                  size=15, bold=True))

    L, Rt, T, Bt = 96, 744, 92, 372

    def X(a):
        return L + (Rt - L) * (a / 90.0)     # a у градусах

    def Y(v):
        return Bt - (Bt - T) * v              # v у [0, 1]

    # горизонтальна легенда під заголовком
    items = [(HOR, "cos α — уперед"), (VER, "sin α — час"), (WIN, "sin 2α — дальність")]
    gap, swl, tpad = 32, 26, 8
    widths = [swl + tpad + text_width(lab, 12, True) for _, lab in items]
    lx = (W - (sum(widths) + gap * (len(items) - 1))) / 2
    for (col, lab), wd in zip(items, widths):
        f.append(line(lx, 56, lx + swl, 56, color=col, sw=3.6))
        f.append(text(lx + swl + tpad, 60, lab, size=12, color=col, bold=True, anchor="start"))
        lx += wd + gap

    # осі + сітка
    f.append(line(L, Bt, Rt, Bt, color=LINE, sw=1.6))         # вісь α
    f.append(line(L, Bt, L, T - 6, color=LINE, sw=1.6))       # вісь значення
    f.append(line(L, Y(1), Rt, Y(1), color=MUTED, sw=1, dash="3,5"))
    f.append(text(L - 8, Y(1) + 4, "1", size=11, color=MUTED, anchor="end"))
    f.append(text(L - 8, Y(0.5) + 4, "0.5", size=11, color=MUTED, anchor="end"))
    for a in (0, 15, 30, 45, 60, 75, 90):
        f.append(line(X(a), Bt, X(a), Bt + 6, color=INK, sw=1.3))
        c = WIN if a == 45 else MUTED
        f.append(text(X(a), Bt + 22, "%d°" % a, size=11, color=c, bold=(a == 45)))
    f.append(text(X(45), Bt + 40, "найдалі", size=11.5, bold=True, color=WIN))

    def curve(fn, col, w=2.4):
        pts, a = [], 0.0
        while a <= 90.0001:
            pts.append("%.1f,%.1f" % (X(a), Y(fn(math.radians(a)))))
            a += 1.0
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), col, w)

    f.append(curve(lambda a: math.cos(a), HOR))
    f.append(curve(lambda a: math.sin(a), VER))
    f.append(curve(lambda a: math.sin(2 * a), WIN, 3.3))

    # вертикаль 45° + пік sin 2α + точка перетину cos = sin
    f.append(line(X(45), Bt, X(45), Y(1), color=MUTED, sw=1.2, dash="4,4"))
    f.append(circle(X(45), Y(math.sin(math.radians(45))), 4, fill=BG, stroke=INK, sw=1.6))
    f.append(circle(X(45), Y(1), 5.5, fill=WIN, stroke=WIN, sw=1.5))

    b, bw, bh = textbox(W / 2, 462,
                        "cos α (швидкість уперед) падає, sin α (час у повітрі) росте; їхній подвоєний добуток\n"
                        "sin 2α сягає одиниці рівно там, де вони зрівнюються, — під 45°. Це й найдальший постріл.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "range-factors.svg"), W, H, *f)


if __name__ == "__main__":
    fig_velocity_components()
    fig_parabola_build()
    fig_range_vs_angle()
    fig_trajectory_history()
    fig_newton_cannonball()
    fig_drag_asymmetry()
    fig_range_angle_drag()
    fig_optimal_angle_ratio()
    fig_trajectory_parabola()
    fig_range_factors()
    print("OK: фігури у", IMG)
