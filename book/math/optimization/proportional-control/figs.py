# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Спільна модель об'єкта з інерцією для відгуків ────────────────────────────
# Дискретна симуляція: інерційний об'єкт другого порядку (маса + загасання) під
# P-регулятором. Дає правдиві криві: малий Kp повзе й недотягує, великий —
# перестрілює й розгойдується. load — стале навантаження (дає сталий зсув).

def sim(Kp, load=0.0, n=600, dt=0.05, mass=1.0, damp=0.5, setpoint=1.0):
    y = 0.0; v = 0.0; out = []
    for _ in range(n):
        e = setpoint - y
        u = Kp * e
        a = (u - load - damp * v) / mass
        v += a * dt
        y += v * dt
        out.append(y)
    return out


# ── Фігура 1: пропорційний закон u = Kp·e ────────────────────────────────────

def fig_proportional_law():
    W, H = 720, 300
    p = []
    ox, oy = 360, 165          # центр (нуль)
    half = 250
    top = 60
    bot = 250

    # осі
    p.append(arrow(ox - half, oy, ox + half, oy, color=INK, sw=1.8))
    p.append(arrow(ox, bot, ox, top, color=INK, sw=1.8))
    p.append(text(ox + half - 4, oy + 20, "помилка e", size=12, color=INK, anchor="end"))
    p.append(text(ox + 44, top + 8, "вплив u", size=12, color=INK))

    # пряма u = Kp·e через нуль (нахил підібрано так, щоб лінія лишалася в полотні)
    run = half - 30                 # горизонтальний хід від центра
    rise = (oy - top - 12)          # вертикальний хід угору до стелі
    slope = rise / run
    p.append(line(ox - run, oy + run * slope,
                  ox + run, oy - run * slope, color=NEG, sw=3))
    p.append(text(ox + 150, oy - 96, "нахил = Kp", size=12, color=NEG, bold=True))

    # пунктир: велика помилка → велика дія
    ex, ey = ox + 150, oy - 150 * slope
    p.append(line(ex, oy, ex, ey, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(ox, ey, ex, ey, color=MUTED, sw=1.4, dash="4 3"))
    p.append(circle(ex, ey, 4, fill=POS, stroke=POS))
    p.append(text(ox + 130, oy + 36, "велика помилка → велика дія", size=10, color=INK))
    p.append(text(ox - 130, oy - 24, "помилка в один бік —", size=10, color=MUTED))
    p.append(text(ox - 130, oy - 10, "дія в той самий", size=10, color=MUTED))

    render(os.path.join(OUT, "proportional-law.svg"), W, H, *p,
           title="Пропорційний закон: u = Kp · e")


# ── Фігура 2: P як пружина ────────────────────────────────────────────────────

def fig_spring_analogy():
    W, H = 720, 260
    p = []

    def spring(x0, y, coils, length, color=INK):
        seg = length / (coils * 2)
        pts = [(x0, y)]
        for i in range(coils * 2):
            x = x0 + seg * (i + 1)
            yy = y - 14 if i % 2 == 0 else y + 14
            pts.append((x, yy))
        pts.append((x0 + length, y))
        return polyline(pts, color=color, sw=1.8)

    def row(y, length, label, force_label):
        q = []
        anchor_x = 130
        # стіна-ціль
        q.append(line(anchor_x, y - 22, anchor_x, y + 22, color=INK, sw=3))
        q.append(text(anchor_x, y - 30, "ціль", size=9.5, color=MUTED))
        # пружина
        q.append(spring(anchor_x, y, 9, length))
        # вантаж
        bx = anchor_x + length
        q.append(rect(bx, y - 16, 32, 32, fill="#dce4f2", stroke=INK, sw=1.6, rx=3))
        # сила тяги назад (червона) — довша за більшого розтягу
        far = length * 0.42
        q.append(line(bx, y, bx - far, y, color=POS, sw=3))
        q.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="3"/>'
                 % (bx - far + 9, y - 5, bx - far, y, bx - far + 9, y + 5, POS))
        q.append(text(bx + 60, y + 4, label, size=10, color=INK, anchor="start"))
        q.append(text(bx + 16, y - 24, force_label, size=9, color=POS, bold=True))
        return q

    p += row(96, 150, "велика помилка → сильна тяга", "F = Kp·e")
    p += row(190, 60, "мала помилка → слабка тяга", "F = Kp·e")

    render(os.path.join(OUT, "spring-analogy.svg"), W, H, *p,
           title="P — це «пружина» до завдання")


# ── Фігура 3: вплив Kp — повільно / баланс / розгойдування ────────────────────

def fig_kp_tradeoff():
    W, H = 720, 300
    p = []
    ox, oy = 80, 252
    top = 56
    Ax = 580
    # рівень завдання
    y_set = top + 55

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv          # yv=1 → лінія завдання
            pts.append((x, y))
        return polyline(pts, color=color, sw=2.4)

    p.append(curve(sim(Kp=0.7, load=0.18), FIELD))    # малий — повзе, недотягує
    p.append(curve(sim(Kp=3.0, load=0.18), NEG))      # баланс
    p.append(curve(sim(Kp=10.0, load=0.18), POS))     # розгойдування

    # легенда
    lx = ox + 26
    for i, (c, t) in enumerate([(FIELD, "малий Kp"), (NEG, "середній Kp"), (POS, "великий Kp")]):
        ly = top + 6 + i * 16
        p.append(line(lx, ly, lx + 26, ly, color=c, sw=2.4))
        p.append(text(lx + 32, ly + 4, t, size=10, color=c, anchor="start", bold=True))

    render(os.path.join(OUT, "kp-tradeoff.svg"), W, H, *p,
           title="Вплив Kp: малий повзе, великий перестрілює й розгойдується")


# ── Фігура 4: сталий зсув — P завжди недотягує ────────────────────────────────

def fig_steady_state_offset():
    W, H = 720, 300
    p = []
    ox, oy = 80, 246
    top = 58
    Ax = 560
    y_set = top + 20

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.8, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv
            pts.append((x, y))
        return pts

    d_lo = curve(sim(Kp=3.0, load=0.5), FIELD)
    d_hi = curve(sim(Kp=10.0, load=0.5), NEG)
    p.append(polyline(d_lo, color=FIELD, sw=2.4))
    p.append(polyline(d_hi, color=NEG, sw=2.4))

    # маркер сталого зсуву наприкінці кривих
    xend = ox + Ax - 6
    p.append(line(xend, y_set, xend, d_lo[-1][1], color=FIELD, sw=2.4))
    p.append(text(xend - 4, (y_set + d_lo[-1][1]) / 2, "e_ss (малий Kp)", size=9.5, color=FIELD, anchor="end", bold=True))
    p.append(line(xend - 130, y_set, xend - 130, d_hi[-1][1], color=NEG, sw=2.4))
    p.append(text(xend - 134, (y_set + d_hi[-1][1]) / 2 - 2, "e_ss (великий Kp)", size=9.5, color=NEG, anchor="end", bold=True))

    # підпис у межах полотна (не за viewBox!)
    p.append(text(ox + Ax * 0.5, top + 2, "більший Kp → менший зсув, та НІКОЛИ не нуль",
                  size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "steady-state-offset.svg"), W, H, *p,
           title="Сталий зсув: P завжди «недотягує» до завдання")


# ── Фігура 5: чому зсув неминучий ─────────────────────────────────────────────

def fig_why_offset():
    W, H = 720, 270
    p = []

    # об'єкт
    p.append(rect(166, 126, 68, 48, fill="#dce4f2", stroke=INK, sw=1.8, rx=4))
    p.append(text(200, 152, "об'єкт", size=10.5, color=INK, bold=True))
    # навантаження вниз
    p.append(arrow(200, 174, 200, 228, color=POS, sw=3))
    p.append(text(208, 220, "навантаження", size=10, color=POS, anchor="start", bold=True))
    p.append(text(208, 234, "(вага, тертя)", size=9, color=MUTED, anchor="start"))
    # вплив угору
    p.append(arrow(200, 126, 200, 72, color=FIELD, sw=3))
    p.append(text(208, 80, "вплив u₀", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(208, 94, "(щоб утримати)", size=9, color=MUTED, anchor="start"))
    # стрілка до рамки-висновку
    p.append(arrow(280, 150, 384, 150, color=INK, sw=2))
    # рамка-висновок
    p.append(fitbox(390, 96, 300, 108, "", fill="#f6f4ec", stroke=INK, sw=1.6))
    p.append(text(540, 124, "P дає вплив ТІЛЬКИ з помилки:", size=11, color=INK, bold=True))
    p.append(text(540, 150, "u = Kp · e", size=15, color=NEG, bold=True))
    p.append(text(540, 176, "щоб u = u₀  →  e_ss = u₀ / Kp ≠ 0", size=11.5, color=POS, bold=True))
    p.append(text(540, 195, "помилку не прибрати, лише зменшити", size=9.5, color=MUTED))

    render(os.path.join(OUT, "why-offset.svg"), W, H, *p,
           title="Чому зсув неминучий")


# ── Фігура 6: P лишає зсув — його прибирає інтегральна складова ────────────────

def fig_automatic_reset():
    W, H = 720, 280
    p = []
    ox, oy = 80, 240
    top = 56
    Ax = 560
    y_set = top + 20

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.8, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv
            pts.append((x, y))
        return pts

    # лише P — застигає нижче (зсув)
    d_p = curve(sim(Kp=3.0, load=0.5), NEG)
    p.append(polyline(d_p, color=NEG, sw=2.6))
    # з інтегральною — повзе на завдання (схематично: P-крива, дотягнута до 1.0)
    d_pi = []
    N = len(d_p)
    for i, (x, y) in enumerate(d_p):
        frac = min(1.0, i / (N * 0.62))
        ytarget = oy - (oy - y_set) * 1.0
        yy = y + (ytarget - y) * frac
        d_pi.append((x, yy))
    p.append(polyline(d_pi, color=FIELD, sw=2.2, dash="6 4"))

    # маркер зсуву P
    xm = ox + Ax * 0.62
    im = int(N * 0.62)
    p.append(line(xm, y_set, xm, d_p[im][1], color=POS, sw=2.4))
    p.append(text(xm + 8, (y_set + d_p[im][1]) / 2, "сталий зсув (P)", size=10, color=POS, anchor="start", bold=True))

    # легенда
    p.append(line(ox + 22, top + 6, ox + 48, top + 6, color=NEG, sw=2.6))
    p.append(text(ox + 54, top + 10, "лише P", size=10, color=NEG, anchor="start", bold=True))
    p.append(line(ox + 22, top + 24, ox + 48, top + 24, color=FIELD, sw=2.2, dash="6 4"))
    p.append(text(ox + 54, top + 28, "P з інтегральною → зсув зникає", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "automatic-reset.svg"), W, H, *p,
           title="P лишає зсув — його прибирає інтегральна складова")


if __name__ == "__main__":
    fig_proportional_law()
    fig_spring_analogy()
    fig_kp_tradeoff()
    fig_steady_state_offset()
    fig_why_offset()
    fig_automatic_reset()
    print("OK: figures written to", OUT)
