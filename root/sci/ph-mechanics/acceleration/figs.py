# -*- coding: utf-8 -*-
"""Фігури до теми «Прискорення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

VEL = "#c0392b"   # швидкість — гаряче червоне
ACC = "#8e44ad"   # прискорення — фіолетове (окремий колір, щоб не плутати з v)


def ball(cx, cy, r=9):
    return circle(cx, cy, r, fill="#fef6e7", stroke=VEL, sw=2)


def uarrow(x, y, ux, uy, L, color, sw=3.0):
    """Стрілка з точки (x,y) уздовж одиничного (ux,uy) завдовжки L."""
    return arrow(x, y, x + ux * L, y + uy * L, color=color, sw=sw)


# ── Фігура 1: три способи змінити швидкість → прискорення ─────────────────────
def fig_three_ways():
    W, H = 980, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три способи змінити швидкість — три роди прискорення", size=17, bold=True))
    for dx in (327, 654):
        f.append(line(dx, 62, dx, 372, color="#dfe4ea", sw=1.2, dash="4,6"))

    midy = 210

    # ── A: Розгін (a вздовж v) ──
    cx = 164
    f.append(text(cx, 88, "Розгін", size=15, bold=True))
    f.append(text(cx, 108, "швидкість росте", size=12, color=MUTED))
    # напрямна руху
    f.append(line(cx - 118, midy, cx + 118, midy, color="#e2e7ee", sw=1.2, dash="3,6"))
    f.append(ball(cx - 92, midy))
    f.append(arrow(cx - 92, midy, cx + 46, midy, color=VEL, sw=3.2))
    f.append(text(cx + 40, midy - 14, "v", size=15, bold=True, color=VEL, anchor="start", italic=True))
    # прискорення — вздовж руху, нижче
    f.append(uarrow(cx - 92, midy + 40, 1, 0, 92, ACC, sw=3.4))
    f.append(text(cx + 8, midy + 62, "a", size=15, bold=True, color=ACC, italic=True))
    f.append(textbox(cx, midy + 128, "a — вздовж v", size=12.5, pad=8,
                     fill="#f3ecf9", stroke=ACC, sw=1.4, color=ACC, bold=True)[0])

    # ── B: Гальмування (a проти v) ──
    cx = 490
    f.append(text(cx, 88, "Гальмування", size=15, bold=True))
    f.append(text(cx, 108, "швидкість спадає", size=12, color=MUTED))
    f.append(line(cx - 118, midy, cx + 118, midy, color="#e2e7ee", sw=1.2, dash="3,6"))
    f.append(ball(cx - 92, midy))
    f.append(arrow(cx - 92, midy, cx + 46, midy, color=VEL, sw=3.2))
    f.append(text(cx + 40, midy - 12, "v", size=15, bold=True, color=VEL, anchor="start", italic=True))
    # прискорення — проти руху (стрілка ліворуч), нижче, з правого боку
    f.append(uarrow(cx + 46, midy + 40, -1, 0, 92, ACC, sw=3.4))
    f.append(text(cx - 52, midy + 62, "a", size=15, bold=True, color=ACC, italic=True))
    f.append(textbox(cx, midy + 128, "a — проти v", size=12.5, pad=8,
                     fill="#f3ecf9", stroke=ACC, sw=1.4, color=ACC, bold=True)[0])

    # ── C: Поворот (a впоперек v, до центра) ──
    cx = 816
    f.append(text(cx, 88, "Поворот", size=15, bold=True))
    f.append(text(cx, 108, "швидкість та сама", size=12, color=MUTED))
    # дуга: центр нижче панелі
    C = (cx, midy + 118)
    R = 118.0
    # намалюємо верхню дугу
    a1, a2 = 118, 62   # градуси
    p1 = (C[0] + R * math.cos(math.radians(a1)), C[1] - R * math.sin(math.radians(a1)))
    p2 = (C[0] + R * math.cos(math.radians(a2)), C[1] - R * math.sin(math.radians(a2)))
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="#e2e7ee" stroke-width="1.4" stroke-dasharray="3,6"/>'
             % (p1[0], p1[1], R, R, p2[0], p2[1]))
    # тіло на вершині дуги
    top = (C[0], C[1] - R)
    f.append(ball(top[0], top[1]))
    # швидкість — по дотичній (горизонтально праворуч на вершині)
    f.append(arrow(top[0] - 4, top[1], top[0] + 64, top[1], color=VEL, sw=3.2))
    f.append(text(top[0] + 58, top[1] - 12, "v", size=15, bold=True, color=VEL, anchor="start", italic=True))
    # прискорення — до центра (вниз)
    f.append(uarrow(top[0], top[1] + 6, 0, 1, 70, ACC, sw=3.4))
    f.append(text(top[0] - 16, top[1] + 52, "a", size=15, bold=True, color=ACC, italic=True))
    # позначка центра
    f.append(circle(C[0], C[1], 2.6, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(C[0], C[1] + 18, "центр", size=10.5, color=MUTED))
    f.append(textbox(cx, midy + 128, "a — до центра", size=12.5, pad=8,
                     fill="#f3ecf9", stroke=ACC, sw=1.4, color=ACC, bold=True)[0])

    b = textbox(W / 2, 446,
                "Швидкість — вектор: у неї є довжина й напрям. Прискорення ловить будь-яку його зміну — витягнув, укоротив чи повернув",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "three-ways.svg"), W, H, *f)


# ── Фігура 2: чому поворот = прискорення до центра (Δv усередину) ─────────────
def fig_turn_is_accel():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Поворот при сталій швидкості: різниця Δv показує до центра", size=16.5, bold=True))
    f.append(line(470, 66, 470, 392, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ліворуч: коло з двома дотичними швидкостями ──
    f.append(text(230, 92, "рух по дузі", size=13.5, bold=True))
    C = (230.0, 320.0)
    R = 150.0
    # дуга (майже повне коло, тонко)
    f.append(circle(C[0], C[1], R, fill="none", stroke="#d7dde5", sw=1.6))
    # дві близькі точки вгорі
    th1, th2 = 118.0, 62.0
    P1 = (C[0] + R * math.cos(math.radians(th1)), C[1] - R * math.sin(math.radians(th1)))
    P2 = (C[0] + R * math.cos(math.radians(th2)), C[1] - R * math.sin(math.radians(th2)))
    # радіуси до точок (блідо)
    f.append(line(C[0], C[1], P1[0], P1[1], color="#e2e7ee", sw=1.2, dash="3,5"))
    f.append(line(C[0], C[1], P2[0], P2[1], color="#e2e7ee", sw=1.2, dash="3,5"))
    f.append(circle(C[0], C[1], 3, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(C[0], C[1] + 20, "центр", size=11, color=MUTED))
    # дотичні напрями (одиничні): v1 угору-праворуч, v2 униз-праворуч
    u1 = (math.cos(math.radians(-25)), math.sin(math.radians(-25)))   # (0.906, -0.423)
    u2 = (math.cos(math.radians(25)), math.sin(math.radians(25)))     # (0.906,  0.423)
    Lv = 96.0
    f.append(ball(P1[0], P1[1], 8))
    f.append(uarrow(P1[0], P1[1], u1[0], u1[1], Lv, VEL, sw=3.2))
    f.append(text(P1[0] + u1[0] * Lv + 6, P1[1] + u1[1] * Lv - 4, "v₁", size=15, bold=True, color=VEL, anchor="start", italic=True))
    f.append(ball(P2[0], P2[1], 8))
    f.append(uarrow(P2[0], P2[1], u2[0], u2[1], Lv, VEL, sw=3.2))
    f.append(text(P2[0] + u2[0] * Lv + 6, P2[1] + u2[1] * Lv + 12, "v₂", size=15, bold=True, color=VEL, anchor="start", italic=True))

    # ── праворуч: трикутник віднімання Δv = v₂ − v₁ ──
    f.append(text(690, 92, "віднімаємо: Δv = v₂ − v₁", size=13.5, bold=True))
    O = (600.0, 190.0)
    t1 = (O[0] + u1[0] * Lv, O[1] + u1[1] * Lv)
    t2 = (O[0] + u2[0] * Lv, O[1] + u2[1] * Lv)
    f.append(circle(O[0], O[1], 3.4, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0] - 10, O[1] - 6, "спільний початок", size=10.5, color=MUTED, anchor="end"))
    f.append(uarrow(O[0], O[1], u1[0], u1[1], Lv, VEL, sw=3.0))
    f.append(text(t1[0] + 8, t1[1] - 2, "v₁", size=14, bold=True, color=VEL, anchor="start", italic=True))
    f.append(uarrow(O[0], O[1], u2[0], u2[1], Lv, VEL, sw=3.0))
    f.append(text(t2[0] + 8, t2[1] + 6, "v₂", size=14, bold=True, color=VEL, anchor="start", italic=True))
    # Δv від кінця v1 до кінця v2 (вертикально вниз)
    f.append(arrow(t1[0], t1[1], t2[0], t2[1], color=ACC, sw=3.6))
    f.append(text(t2[0] + 14, (t1[1] + t2[1]) / 2 + 5, "Δv", size=16, bold=True, color=ACC, anchor="start", italic=True))
    f.append(text(t2[0] + 14, (t1[1] + t2[1]) / 2 + 26, "(до центра)", size=11, color=ACC, anchor="start"))
    # a = Δv/Δt униз
    f.append(text(690, 360, "a = Δv / Δt  →  теж до центра", size=13, bold=True, color=ACC))

    b = textbox(W / 2, 440,
                "Обидві швидкості однакові завдовжки, та різні за напрямом.\n"
                "Їхня різниця дивиться всередину — тому прискорення в повороті центрострімке",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "turn-is-accel.svg"), W, H, *f)


# ── Фігура 3: прискорення відчуваєш, швидкість — ні ───────────────────────────
def fig_felt():
    W, H = 1000, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Що чуєш тілом: не швидкість, а прискорення", size=17, bold=True))
    for dx in (250, 500, 750):
        f.append(line(dx, 60, dx, 338, color="#dfe4ea", sw=1.2, dash="4,6"))

    def car(cx, cy, felt=None, acc=None, curve=False):
        """Машина згори (їде вгору). felt/acc — (ux,uy) напрями; None — немає."""
        out = []
        # шлях
        if curve:
            out.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                       'stroke="#e2e7ee" stroke-width="1.4" stroke-dasharray="3,6"/>'
                       % (cx + 46, cy + 70, cx + 30, cy - 40, cx - 34, cy - 92))
        else:
            out.append(line(cx, cy + 78, cx, cy - 86, color="#e2e7ee", sw=1.3, dash="3,6"))
        # кузов (згори): заокруглений прямокутник, ніс угору
        out.append(rect(cx - 22, cy - 40, 44, 80, fill="#eef2f7", stroke="#8a94a6", sw=1.8, rx=12))
        # лобове скло
        out.append(line(cx - 15, cy - 20, cx + 15, cy - 20, color="#8a94a6", sw=1.4))
        # голова пасажира
        out.append(circle(cx, cy + 6, 8, fill="#fde9c8", stroke="#b98", sw=1.4))
        # швидкість — завжди вгору (червона), збоку зліва
        out.append(arrow(cx - 44, cy + 30, cx - 44, cy - 40, color=VEL, sw=2.8))
        out.append(text(cx - 52, cy - 6, "v", size=13.5, bold=True, color=VEL, anchor="end", italic=True))
        # прискорення (фіолетове), справа
        if acc is not None:
            ux, uy = acc
            out.append(uarrow(cx + 44, cy, ux, uy, 46, ACC, sw=3.2))
            out.append(text(cx + 52, cy + uy * 40 + 4,
                            "a", size=13.5, bold=True, color=ACC, anchor="start", italic=True))
        # відчуття (сірий пунктир) — на голові, протилежно до a
        if felt is not None:
            ux, uy = felt
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                       'stroke-width="2.6" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
                       % (cx, cy + 6, cx + ux * 34, cy + 6 + uy * 34, MUTED))
        return "".join(out)

    y0 = 180
    # 1: рівний рух — a=0, нічого не чуєш
    f.append(text(125, 82, "Рівний рух", size=14, bold=True))
    f.append(car(125, y0, felt=None, acc=None))
    f.append(text(125, 122, "a = 0", size=12.5, bold=True, color=ACC))
    f.append(textbox(125, 322, "тіло мовчить", size=12, pad=8, fill=FILL, stroke=LINE, sw=1.2)[0])

    # 2: розгін — a вперед, чуєш «у крісло» (назад)
    f.append(text(375, 82, "Розгін", size=14, bold=True))
    f.append(car(375, y0, felt=(0, 1), acc=(0, -1)))
    f.append(text(375 + 60, y0 + 44, "чуєш: у крісло", size=11, color=MUTED, anchor="start"))
    f.append(textbox(375, 322, "вдавлює назад", size=12, pad=8, fill=FILL, stroke=LINE, sw=1.2)[0])

    # 3: гальмування — a назад, чуєш «на пасок» (вперед)
    f.append(text(625, 82, "Гальмування", size=14, bold=True))
    f.append(car(625, y0, felt=(0, -1), acc=(0, 1)))
    f.append(text(625 + 60, y0 - 40, "чуєш: на пасок", size=11, color=MUTED, anchor="start"))
    f.append(textbox(625, 322, "кидає вперед", size=12, pad=8, fill=FILL, stroke=LINE, sw=1.2)[0])

    # 4: поворот — a до центра (вліво), чуєш «на дверцята» (вправо)
    f.append(text(875, 82, "Поворот", size=14, bold=True))
    f.append(car(875, y0, felt=(1, 0), acc=(-1, 0), curve=True))
    f.append(text(875 + 22, y0 - 30, "чуєш: убік", size=11, color=MUTED, anchor="start"))
    f.append(textbox(875, 322, "тягне назовні", size=12, pad=8, fill=FILL, stroke=LINE, sw=1.2)[0])

    # легенда
    lx = 300
    f.append(line(lx, 372, lx + 26, 372, color=VEL, sw=3))
    f.append(text(lx + 32, 376, "швидкість v", size=11.5, color=INK, anchor="start"))
    f.append(line(lx + 170, 372, lx + 196, 372, color=ACC, sw=3.4))
    f.append(text(lx + 202, 376, "прискорення a", size=11.5, color=INK, anchor="start"))
    f.append('<line x1="%.1f" y1="372" x2="%.1f" y2="372" stroke="%s" stroke-width="2.6" stroke-dasharray="4,3"/>'
             % (lx + 360, lx + 386, MUTED))
    f.append(text(lx + 392, 376, "що чуєш (протилежне до a)", size=11.5, color=INK, anchor="start"))

    b = textbox(W / 2, 410,
                "Рівну швидкість неможливо відчути — вона для тіла те саме, що спокій. Відчувається лише зміна швидкості, тобто прискорення",
                size=12.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "felt.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до математичної вставки (границя · сходинки похідних · розклад a)
# ══════════════════════════════════════════════════════════════════════════════

SEC = "#2980b9"   # січні — сині
TAN = "#8e44ad"   # дотична / прискорення — фіолетове (як ACC)


# ── Math-1: середнє → миттєве (січні стягуються до дотичної) ───────────────────
def fig_limit_secant():
    W, H = 860, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Середнє прискорення → миттєве: січна стає дотичною", size=17, bold=True))

    # поле графіка
    L, Rr, T, Bm = 92, 700, 70, 402      # межі області
    tmin, tmax, vmax = 0.0, 4.0, 48.0

    def X(t):
        return L + (t - tmin) / (tmax - tmin) * (Rr - L)

    def Y(v):
        return Bm - v / vmax * (Bm - T)

    # осі
    f.append(arrow(L, Bm, Rr + 22, Bm, color=INK, sw=1.8))       # t
    f.append(arrow(L, Bm, L, T - 14, color=INK, sw=1.8))         # v
    f.append(text(Rr + 20, Bm + 22, "t", size=14, italic=True, anchor="end"))
    f.append(text(L - 12, T - 2, "v", size=14, italic=True, anchor="end"))
    f.append(text(L - 10, Bm + 20, "0", size=11.5, color=MUTED, anchor="end"))

    # крива v = 3 t²
    pts = []
    tt = 0.0
    while tt <= 3.62:
        pts.append("%.1f,%.1f" % (X(tt), Y(3 * tt * tt)))
        tt += 0.08
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), VEL))
    f.append(text(X(1.0) + 8, Y(3 * 1.0 * 1.0) - 8, "v = 3t²", size=13,
                  color=VEL, anchor="start", italic=True))

    # точка P при t=2
    tp = 2.0
    vp = 3 * tp * tp                       # 12
    Px, Py = X(tp), Y(vp)

    # січні до дедалі ближчих точок (сині, тонші зі зближенням)
    for dt, sw in ((1.4, 1.6), (0.8, 1.8), (0.35, 2.0)):
        tq = tp + dt
        vq = 3 * tq * tq
        # продовжимо трохи за Q для наочності
        f.append(line(Px, Py, X(tq), Y(vq), color=SEC, sw=sw))
        f.append(circle(X(tq), Y(vq), 3.4, fill=BG, stroke=SEC, sw=1.8))
    f.append(text(X(3.4) + 6, Y(3 * 3.4 * 3.4) + 4, "січні: a_сер", size=12.5,
                  color=SEC, anchor="start", bold=True))

    # дотична в P: нахил dv/dt = 6t = 12 (v за t)
    slope = 12.0
    ta, tb = 1.15, 2.95
    f.append(line(X(ta), Y(vp + slope * (ta - tp)), X(tb), Y(vp + slope * (tb - tp)),
                  color=TAN, sw=3.2))
    f.append(text(X(2.95) + 8, Y(vp + slope * 0.95) - 4, "дотична: a (миттєве)",
                  size=12.5, color=TAN, anchor="start", bold=True))

    # точка P
    f.append(circle(Px, Py, 5.2, fill=TAN, stroke=BG, sw=1.6))
    f.append(text(Px - 10, Py - 16, "P (t = 2 с)", size=12, color=INK, anchor="end"))

    # табличка збіжності
    tb_lines = ("Δt      a_сер = 12 + 3·Δt",
                "1.0     15.0",
                "0.1     12.3",
                "0.01    12.03",
                "→ 0     12.0   = dv/dt")
    bx = 470
    f.append(textbox(bx, 158, "\n".join(tb_lines), size=12, pad=10,
                     fill="#eef4fb", stroke=SEC, sw=1.3)[0])

    b = textbox(W / 2, 470,
                "Нахил січної через дві точки — середнє прискорення.\n"
                "Друга точка сповзає до P, січна лягає дотичною, її нахил — миттєве a",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "limit-secant.svg"), W, H, *f)


# ── Math-2: сходинки похідних  x → v → a ─────────────────────────────────────
def fig_deriv_ladder():
    W, H = 640, 680
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Сходинки похідних: x → v → a", size=17, bold=True))

    PL, PW = 70, 360           # ліва межа й ширина панелей
    PH = 150                   # висота панелі
    tops = (58, 250, 442)      # верх кожної панелі
    tmax = 2.0

    def panel(top, fn, ymax, label, formula, color, straight=False):
        out = []
        bottom = top + PH
        # осі панелі
        out.append(line(PL, bottom, PL + PW, bottom, color=INK, sw=1.5))
        out.append(line(PL, bottom, PL, top + 6, color=INK, sw=1.5))
        out.append(text(PL - 8, top + 4, label.split("=")[0].strip(), size=13,
                        italic=True, anchor="end", color=color))

        def Xx(t):
            return PL + t / tmax * (PW - 30)

        def Yy(v):
            return bottom - v / ymax * (PH - 22)

        pts = []
        tt = 0.0
        while tt <= tmax + 1e-9:
            pts.append("%.1f,%.1f" % (Xx(tt), Yy(fn(tt))))
            tt += 0.05
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                    % (" ".join(pts), color))
        # формула в рамці справа
        out.append(textbox(PL + PW + 108, top + PH / 2, formula, size=13, pad=9,
                           fill="#f3ecf9" if color == TAN else FILL,
                           stroke=color, sw=1.4, color=color, bold=True)[0])
        return "".join(out)

    f.append(panel(tops[0], lambda t: t ** 3, 8.2, "x =", "x(t) = t³", VEL))
    f.append(panel(tops[1], lambda t: 3 * t * t, 12.5, "v =", "v = dx/dt = 3t²", SEC))
    f.append(panel(tops[2], lambda t: 6 * t, 12.5, "a =", "a = dv/dt = 6t\n= d²x/dt²", TAN))

    # стрілки «похідна (нахил)» між панелями
    for y0 in (tops[0] + PH + 4, tops[1] + PH + 4):
        f.append(arrow(PL + 150, y0, PL + 150, y0 + 34, color=MUTED, sw=2.2))
        f.append(text(PL + 162, y0 + 24, "похідна (нахил)", size=11.5,
                      color=MUTED, anchor="start"))

    # спільна вісь часу знизу
    f.append(text(PL + PW - 10, tops[2] + PH + 14, "t", size=13, italic=True, anchor="end"))

    b = textbox(W / 2, 642,
                "Кожна крива — нахил тієї, що над нею.\n"
                "Прискорення — нахил швидкості, тобто друга похідна координати",
                size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "deriv-ladder.svg"), W, H, *f)


# ── Math-3: розклад прискорення на дотичну й нормальну ────────────────────────
def fig_tangent_normal():
    W, H = 860, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Розклад прискорення: дотична a_τ + нормальна a_n", size=17, bold=True))

    C = (430.0, 520.0)      # центр кривини (нижче кадру видимої дуги)
    R = 250.0
    P = (C[0], C[1] - R)    # тіло на вершині дуги: (430, 270)

    # дуга траєкторії
    a1, a2 = 128, 52
    q1 = (C[0] + R * math.cos(math.radians(a1)), C[1] - R * math.sin(math.radians(a1)))
    q2 = (C[0] + R * math.cos(math.radians(a2)), C[1] - R * math.sin(math.radians(a2)))
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="#cdd5df" stroke-width="2.2"/>' % (q1[0], q1[1], R, R, q2[0], q2[1]))
    f.append(text(q1[0] - 6, q1[1] - 6, "траєкторія", size=12, color=MUTED, anchor="end"))

    # радіус до центра (пунктир) + центр
    f.append(line(P[0], P[1], C[0], C[1], color="#c8b7de", sw=1.6, dash="5,6"))
    f.append(text(P[0] + 12, (P[1] + C[1]) / 2, "r", size=14, italic=True, color=MUTED, anchor="start"))
    f.append(circle(C[0], C[1], 3.4, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(C[0], C[1] + 20, "центр кривини", size=11.5, color=MUTED))

    # тіло
    f.append(circle(P[0], P[1], 8.5, fill="#fef6e7", stroke=VEL, sw=2.2))

    # швидкість — по дотичній (праворуч), червона, трохи вище
    f.append(arrow(P[0] - 2, P[1] - 22, P[0] + 150, P[1] - 22, color=VEL, sw=3.0))
    f.append(text(P[0] + 150, P[1] - 30, "v", size=15, bold=True, italic=True,
                  color=VEL, anchor="start"))

    # дотична складова a_τ — уздовж руху (праворуч), фіолетова
    at_len = 95.0
    f.append(uarrow(P[0], P[1], 1, 0, at_len, TAN, sw=3.4))
    f.append(text(P[0] + at_len + 8, P[1] - 8, "a_τ = dv/dt", size=13.5, bold=True,
                  italic=True, color=TAN, anchor="start"))

    # нормальна складова a_n — до центра (вниз), фіолетова
    an_len = 175.0
    f.append(uarrow(P[0], P[1], 0, 1, an_len, TAN, sw=3.4))
    f.append(text(P[0] - 12, P[1] + an_len - 6, "a_n = v²/r", size=13.5, bold=True,
                  italic=True, color=TAN, anchor="end"))

    # повне прискорення a — діагональ (сума), темна товста
    f.append(arrow(P[0], P[1], P[0] + at_len, P[1] + an_len, color=INK, sw=3.8))
    f.append(text(P[0] + at_len + 10, P[1] + an_len - 4, "a", size=16, bold=True,
                  italic=True, color=INK, anchor="start"))
    f.append(text(P[0] + at_len + 10, P[1] + an_len + 16, "= √(a_τ² + a_n²)", size=12.5,
                  color=INK, anchor="start"))

    # прямий кут між складовими
    s = 15
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6"/>'
             % (P[0] + s, P[1], P[0] + s, P[1] + s, P[0], P[1] + s, INK))

    # легенда
    lx, ly = 560, 112
    f.append(rect(lx - 16, ly - 24, 268, 122, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=8))
    f.append(line(lx, ly, lx + 30, ly, color=VEL, sw=3))
    f.append(text(lx + 38, ly + 4, "v — швидкість (по дотичній)", size=12, anchor="start"))
    f.append(line(lx, ly + 30, lx + 30, ly + 30, color=TAN, sw=3.4))
    f.append(text(lx + 38, ly + 34, "a_τ — міняє модуль швидкості", size=12, anchor="start"))
    f.append(line(lx, ly + 60, lx + 30, ly + 60, color=TAN, sw=3.4))
    f.append(text(lx + 38, ly + 64, "a_n — міняє напрям (до центра)", size=12, anchor="start"))
    f.append(line(lx, ly + 90, lx + 30, ly + 90, color=INK, sw=3.8))
    f.append(text(lx + 38, ly + 94, "a — повне прискорення (сума)", size=12, anchor="start"))

    b = textbox(W / 2, 512,
                "Дотична складова розганяє чи гальмує (міняє модуль v); нормальна\n"
                "завертає (міняє напрям). Вони перпендикулярні — тому a = √(a_τ² + a_n²)",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "tangent-normal.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до історичної вставки (Мертон · трикутник Орема · жолоби Ґалілея)
# ══════════════════════════════════════════════════════════════════════════════

def _poly(points, fill, stroke="none", sw=0):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


def _dblarrow(x1, y1, x2, y2, color=LINE, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s '
            'marker-start="url(#arrow)" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw, d))


# ── Hist-1: доведення Орема (площа під графіком швидкості = шлях) ──────────────
def fig_oresme_proof():
    W, H = 900, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Доведення Орема: площа під графіком швидкості = шлях", size=17, bold=True))

    O = (150.0, 430.0)          # початок координат
    Tx = 650.0                  # кінець проміжку (час t)
    Vy = 140.0                  # рівень кінцевої швидкості v_к
    My = 285.0                  # серединний рівень v_к/2
    Mx = 400.0                  # середина основи

    # прямокутник середньої швидкості (заливка)
    f.append(rect(O[0], My, Tx - O[0], O[1] - My, fill="#eef2f7", stroke="none", sw=0, rx=0))
    # два рівні трикутники: нестача (ліворуч-унизу) і надлишок (праворуч-угорі)
    f.append(_poly([(O[0], My), (O[0], O[1]), (Mx, My)], fill="#e2f4ea", stroke="#8fd3ac", sw=1.2))
    f.append(_poly([(Mx, My), (Tx, My), (Tx, Vy)], fill="#e2f4ea", stroke="#8fd3ac", sw=1.2))
    # межа прямокутника
    f.append(rect(O[0], My, Tx - O[0], O[1] - My, fill="none", stroke=MUTED, sw=1.3, rx=0))

    # діагональ швидкості (рівномірне наростання)
    f.append(line(O[0], O[1], Tx, Vy, color=VEL, sw=3.6))
    # серединна лінія (середня швидкість)
    f.append(line(O[0], My, Tx, My, color=ACC, sw=2.2, dash="7,5"))
    # серединна мить (тонка вертикаль)
    f.append(line(Mx, My, Mx, O[1], color="#c9cfd8", sw=1.2, dash="3,5"))

    # осі
    f.append(arrow(O[0], O[1], Tx + 55, O[1], color=INK, sw=1.8))
    f.append(arrow(O[0], O[1], O[0], Vy - 35, color=INK, sw=1.8))
    f.append(text(O[0], 100, "швидкість v", size=12.5, color=INK))
    f.append(text(Tx + 42, O[1] + 22, "час t", size=12.5, color=INK))
    f.append(text(O[0] - 8, O[1] + 18, "0", size=12, color=MUTED, anchor="end"))
    # позначки на осі v
    f.append(line(O[0] - 6, Vy, O[0], Vy, color=INK, sw=1.4))
    f.append(text(O[0] - 12, Vy + 4, "v_к", size=13, color=VEL, anchor="end", bold=True, italic=True))
    f.append(line(O[0] - 6, My, O[0], My, color=INK, sw=1.4))
    f.append(text(O[0] - 12, My + 4, "v_к/2", size=12.5, color=ACC, anchor="end", bold=True, italic=True))
    # мітка серединної швидкості праворуч
    f.append(text(Tx + 8, My + 4, "v_сер", size=12.5, color=ACC, anchor="start", italic=True))
    f.append(text(Mx, O[1] + 18, "серед. мить", size=10.5, color=MUTED))

    # написи всередині
    f.append(text(400, 405, "площа фігури = пройдений шлях", size=13, color=INK))
    f.append(text(272, 210, "швидкість зростає рівно", size=12, color=VEL))
    f.append(text(578, 232, "надлишок", size=12, color="#1c7a43", bold=True))
    f.append(text(252, 352, "нестача", size=12, color="#1c7a43", bold=True))
    # надлишок дорівнює нестачі — переносимо трикутник
    f.append('<path d="M 560 232 Q 470 150 258 344" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5,5" marker-end="url(#arrow)"/>' % MUTED)
    f.append(text(455, 138, "площі рівні", size=11.5, color=MUTED))

    b = textbox(W / 2, 508,
                "Трикутник рівноприскореного руху й прямокутник середньої швидкості мають однакову площу — тому й однаковий шлях",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "oresme-proof.svg"), W, H, *f)


# ── Hist-2: жолоб Ґалілея — шлях ~ t², прирости — непарні числа ───────────────
def fig_galileo_ramp():
    W, H = 940, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Жолоб Ґалілея: шлях росте як квадрат часу (непарні прирости)", size=16.5, bold=True))

    S = (150.0, 150.0)
    E = (800.0, 410.0)
    L = math.hypot(E[0] - S[0], E[1] - S[1])
    ux, uy = (E[0] - S[0]) / L, (E[1] - S[1]) / L
    perp = (-uy, ux)
    if perp[1] > 0:                     # хочемо перпендикуляр, що дивиться ВГОРУ
        perp = (-perp[0], -perp[1])
    up = perp

    def P(frac):
        return (S[0] + ux * L * frac, S[1] + uy * L * frac)

    marks = [(P(1 / 16.0), "t=1 · шлях 1"),
             (P(4 / 16.0), "t=2 · шлях 4"),
             (P(9 / 16.0), "t=3 · шлях 9"),
             (P(16 / 16.0), "t=4 · шлях 16")]

    # опора-схил (тло)
    f.append(_poly([(S[0], S[1]), (S[0], E[1]), (E[0], E[1])], fill="#f7f9fb", stroke="#e0e5ec", sw=1.2))
    # жолоб
    f.append(line(S[0], S[1], E[0], E[1], color=INK, sw=4.2))

    # прирости (непарні) — двобічні стрілки НАД жолобом
    seg = [(0.0, 1 / 16.0, "1"), (1 / 16.0, 4 / 16.0, "3"),
           (4 / 16.0, 9 / 16.0, "5"), (9 / 16.0, 16 / 16.0, "7")]
    for a, b_, lab in seg:
        Pa, Pb = P(a), P(b_)
        Aa = (Pa[0] + up[0] * 13, Pa[1] + up[1] * 13)
        Ab = (Pb[0] + up[0] * 13, Pb[1] + up[1] * 13)
        f.append(_dblarrow(Aa[0], Aa[1], Ab[0], Ab[1], color=ACC, sw=2.4))
        mid = ((Aa[0] + Ab[0]) / 2 + up[0] * 15, (Aa[1] + Ab[1]) / 2 + up[1] * 15)
        f.append(text(mid[0], mid[1], lab, size=14, color=ACC, bold=True))

    # позначки-риски й підписи t/шлях ПІД жолобом
    for pt, lab in marks:
        pl = (pt[0] - up[0] * 10, pt[1] - up[1] * 10)
        pr = (pt[0] + up[0] * 10, pt[1] + up[1] * 10)
        f.append(line(pl[0], pl[1], pr[0], pr[1], color=INK, sw=2.2))
        f.append(circle(pt[0], pt[1], 3.2, fill=INK, stroke=INK, sw=1))
        f.append(text(pt[0], pt[1] + 34, lab, size=12, color=INK))

    # кулька на старті
    f.append(circle(S[0], S[1], 10, fill="#fef6e7", stroke=VEL, sw=2.4))
    f.append(text(S[0] - 4, S[1] - 20, "старт", size=12, color=MUTED))

    # водяний годинник (кут)
    vx, vy = 852, 92
    f.append(rect(vx, vy, 46, 34, fill="#eaf2fb", stroke="#8aa6c8", sw=1.6, rx=4))
    f.append(line(vx + 4, vy + 12, vx + 42, vy + 12, color="#4a79b8", sw=1.4))
    f.append(circle(vx + 23, vy + 48, 4, fill="#4a79b8", stroke="#4a79b8", sw=1))
    f.append(mtext(vx + 23, vy - 16, ["водяний", "годинник"], size=10.5, color=MUTED))

    b = textbox(W / 2, 498,
                "За рівні проміжки часу шлях від старту росте як 1, 4, 9, 16 = t²; "
                "прирости між сусідніми позначками — непарні 1, 3, 5, 7",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "galileo-ramp.svg"), W, H, *f)


# ── Hist-3: часова смуга (ідея → доведення → здогад → дослід) ─────────────────
def fig_accel_timeline():
    W, H = 1000, 545
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Народження прискорення: ідея → доведення → здогад → дослід", size=16.5, bold=True))

    IDEA, IDEA_F = "#2457d6", "#e8edfb"
    PROOF, PROOF_F = "#1c7a43", "#e6f5ec"
    GUESS, GUESS_F = "#b5790a", "#fbf1dd"
    EXPT, EXPT_F = "#b3341f", "#fbe9e4"

    AY = 250.0
    def X(year):
        return 90.0 + (year - 1320) * (820.0 / 330.0)

    # легенда ролей
    for lx, c, cf, lab in [(110, IDEA, IDEA_F, "ІДЕЯ — правило"),
                           (300, PROOF, PROOF_F, "ДОВЕДЕННЯ — геометрія"),
                           (560, GUESS, GUESS_F, "ЗДОГАД — інтуїція"),
                           (800, EXPT, EXPT_F, "ДОСЛІД — вимір")]:
        f.append(rect(lx, 56, 16, 12, fill=cf, stroke=c, sw=1.4, rx=3))
        f.append(text(lx + 22, 66, lab, size=12, color=c, anchor="start", bold=True))

    # вісь часу
    f.append(line(80, AY, 920, AY, color=INK, sw=2))
    for yr in (1400, 1500, 1600):
        f.append(line(X(yr), AY - 4, X(yr), AY + 4, color=MUTED, sw=1.3))
        f.append(text(X(yr), AY - 10, str(yr), size=10.5, color=MUTED))

    def stationbox(cx, cy, dots, lines, c, cf):
        out = []
        bx = textbox(cx, cy, "\n".join(lines), size=12, pad=9,
                     fill=cf, stroke=c, sw=1.6, color=c)
        top = cy - bx[2] / 2
        for dxp in dots:
            out.append(circle(dxp, AY, 4, fill=c, stroke=c, sw=1))
            out.append(line(dxp, AY, cx, top, color=c, sw=1.3))
        out.append(bx[0])
        return out

    # A · Мертон 1335 (ІДЕЯ) — верхній ряд ліворуч
    f += stationbox(120, 345, [X(1335)],
                    ["1335 · Мертон", "(Гейтсбері)", "ІДЕЯ: правило", "середньої швидкості"], IDEA, IDEA_F)
    # B · Орем і Казалі ~1350 (ДОВЕДЕННЯ) — нижній ряд
    f += stationbox(255, 458, [X(1350)],
                    ["бл. 1350", "Орем і Казалі", "ДОВЕДЕННЯ:", "площа під графіком"], PROOF, PROOF_F)
    # C · де Сото 1551 (ЗДОГАД) — верхній ряд
    f += stationbox(664, 345, [X(1551)],
                    ["1551 · де Сото", "ЗДОГАД:", "падіння —", "рівноприскорене"], GUESS, GUESS_F)
    # D · Ґалілей 1604/1638 (ДОСЛІД) — нижній ряд, дві точки
    f += stationbox(840, 458, [X(1604), X(1638)],
                    ["1604 досліди · 1638 книга", "Ґалілей", "ДОСЛІД: жолоби, t²"], EXPT, EXPT_F)

    # вимірювальна дужка Орем → Декарт (майже 285 років)
    xo, xd = X(1350), X(1637)
    by = 158.0
    f.append(line(xo, by, xo, AY, color=MUTED, sw=1.1, dash="3,5"))
    f.append(line(xd, by, xd, AY, color=MUTED, sw=1.1, dash="3,5"))
    f.append(_dblarrow(xo, by, xd, by, color=MUTED, sw=2.0))
    f.append(circle(xd, AY, 3.2, fill="#9aa0a8", stroke="#9aa0a8", sw=1))
    f.append(text((xo + xd) / 2, by - 10,
                  "трикутник Орема — майже за 285 років до координат Декарта (1637)",
                  size=12, color=MUTED))

    b = textbox(W / 2, 522,
                "Ідея, доведення, здогад і дослід — різні роди роботи, розтягнені на три століття "
                "й чотири країни; жодного єдиного автора",
                size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)[0]
    f.append(b)
    return render(os.path.join(IMG, "accel-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_ways()
    fig_turn_is_accel()
    fig_felt()
    fig_limit_secant()
    fig_deriv_ladder()
    fig_tangent_normal()
    fig_oresme_proof()
    fig_galileo_ramp()
    fig_accel_timeline()
    print("OK: фігури у", IMG)
