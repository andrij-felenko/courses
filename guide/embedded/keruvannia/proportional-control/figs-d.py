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


# ── Симуляції об'єктів під P ──────────────────────────────────────────────────
# Об'єкт першого порядку (одна інерція, як нагрівач): τ·dy/dt = -y + K·u.
# Дає ЗАВЖДИ згасання без коливань, лише τ коротшає з Kp.
def sim_first(Kp, K=1.0, tau=1.0, load=0.0, n=800, dt=0.01, setpoint=1.0):
    y = 0.0; out = []
    for _ in range(n):
        e = setpoint - y
        u = Kp * e
        dy = (-y + K * (u - load)) / tau
        y += dy * dt
        out.append(y)
    return out


# Об'єкт другого порядку (маса + загасання, як крен): дає перестрілювання й
# дзвін за великого Kp; малий Kp — плавно. damp — власне механічне загасання.
def sim_second(Kp, K=1.0, load=0.0, n=900, dt=0.02, mass=1.0, damp=0.7, setpoint=1.0):
    y = 0.0; v = 0.0; out = []
    for _ in range(n):
        e = setpoint - y
        u = Kp * e
        a = (K * (u - load) - damp * v) / mass
        v += a * dt
        y += v * dt
        out.append(y)
    return out


def axes(p, ox, oy, top, Ax, y_set, set_label="завдання"):
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, set_label, size=10, color=MUTED, anchor="start"))


def plot(data, ox, oy, Ax, y_set, color, sw=2.4, dash=None, ytop_val=1.25):
    pts = []
    N = len(data)
    span = oy - y_set
    for i, yv in enumerate(data):
        x = ox + Ax * i / (N - 1)
        y = oy - span * (yv / 1.0)
        pts.append((x, y))
    return polyline(pts, color=color, sw=sw, dash=dash)


# ── Фігура 1: об'єкт 1-го порядку — P лише КОРОТШАЄ сталу часу, без коливань ───
def fig_first_order_speedup():
    W, H = 720, 320
    p = []
    ox, oy = 80, 262
    top = 58
    Ax = 560
    y_set = top + 26
    axes(p, ox, oy, top, Ax, y_set)

    for Kp, c, lbl in [(1.0, FIELD, "Kp = 1"), (4.0, NEG, "Kp = 4"), (12.0, POS, "Kp = 12")]:
        p.append(plot(sim_first(Kp, load=0.0), ox, oy, Ax, y_set, c))

    # легенда
    lx = ox + Ax - 150
    for i, (c, t) in enumerate([(FIELD, "Kp = 1  (мляво)"),
                                (NEG, "Kp = 4  (жвавіше)"),
                                (POS, "Kp = 12 (майже одразу)")]):
        ly = top + 8 + i * 16
        p.append(line(lx, ly, lx + 24, ly, color=c, sw=2.6))
        p.append(text(lx + 30, ly + 4, t, size=10, color=c, anchor="start", bold=True))

    p.append(text(ox + Ax * 0.5, oy + 34,
                  "об'єкт 1-го порядку: крива лише КРУТІШАЄ — жодного перестрілу",
                  size=10.5, color=INK))

    render(os.path.join(OUT, "first-order-speedup.svg"), W, H, *p,
           title="Об'єкт першого порядку: P пришвидшує, але не розгойдує")


# ── Фігура 2: об'єкт 2-го порядку — Kp керує загасанням (ζ) ────────────────────
def fig_second_order_damping():
    W, H = 720, 330
    p = []
    ox, oy = 80, 252
    top = 58
    Ax = 560
    y_set = top + 64
    axes(p, ox, oy, top, Ax, y_set)

    p.append(plot(sim_second(1.5, load=0.0), ox, oy, Ax, y_set, FIELD))   # переgas
    p.append(plot(sim_second(6.0, load=0.0), ox, oy, Ax, y_set, NEG))     # близько крит.
    p.append(plot(sim_second(22.0, load=0.0), ox, oy, Ax, y_set, POS))    # дзвін

    lx = ox + Ax - 168
    for i, (c, t) in enumerate([(FIELD, "малий Kp: ζ>1, повзе"),
                                (NEG, "середній: ζ≈1, чіткий фронт"),
                                (POS, "великий Kp: ζ≪1, дзвін")]):
        ly = top + 8 + i * 16
        p.append(line(lx, ly, lx + 24, ly, color=c, sw=2.6))
        p.append(text(lx + 30, ly + 4, t, size=9.5, color=c, anchor="start", bold=True))

    p.append(text(ox + Ax * 0.5, oy + 34,
                  "об'єкт 2-го порядку: Kp задає коефіцієнт загасання ζ ~ 1/√Kp",
                  size=10.5, color=INK))

    render(os.path.join(OUT, "second-order-damping.svg"), W, H, *p,
           title="Об'єкт другого порядку: Kp керує загасанням")


# ── Фігура 3: насичення — лінійна зона й зрізана дія ───────────────────────────
def fig_saturation():
    W, H = 720, 320
    p = []
    ox, oy = 360, 200
    half = 250
    top = 56
    bot = 296

    p.append(arrow(ox - half, oy, ox + half, oy, color=INK, sw=1.8))
    p.append(arrow(ox, bot, ox, top, color=INK, sw=1.8))
    p.append(text(ox + half - 4, oy + 20, "помилка e", size=12, color=INK, anchor="end"))
    p.append(text(ox + 40, top + 6, "вплив u", size=12, color=INK))

    umax = oy - top - 18          # стеля дії у пікселях
    umin = bot - oy - 18
    # межі насичення по e
    e_hi = 120                    # де лінія впирається у стелю
    slope = umax / e_hi

    # горизонтальні полиці (насичення)
    p.append(line(ox + e_hi, oy - umax, ox + half - 8, oy - umax, color=POS, sw=3))
    p.append(line(ox - e_hi, oy + umin, ox - half + 8, oy + umin, color=POS, sw=3))
    # лінійний нахил у середині
    p.append(line(ox - e_hi, oy + e_hi * slope, ox + e_hi, oy - e_hi * slope, color=NEG, sw=3))

    # стелі
    p.append(line(ox - half + 8, oy - umax, ox + half - 8, oy - umax, color=MUTED, sw=1.2, dash="4 4"))
    p.append(line(ox - half + 8, oy + umin, ox + half - 8, oy + umin, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(ox - half + 10, oy - umax - 6, "u_max (мотор на повну)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(ox - half + 10, oy + umin + 16, "u_min", size=9.5, color=MUTED, anchor="start"))

    # межі лінійної зони
    p.append(line(ox + e_hi, oy - 4, ox + e_hi, oy + 4, color=INK, sw=1.4))
    p.append(line(ox - e_hi, oy - 4, ox - e_hi, oy + 4, color=INK, sw=1.4))
    p.append(text(ox, top + 2, "лінійна зона: u = Kp·e", size=11, color=NEG, bold=True))
    p.append(text(ox + (e_hi + half) / 2, oy - umax - 22, "зона насичення:", size=9.5, color=POS, bold=True, anchor="middle"))
    p.append(text(ox + (e_hi + half) / 2, oy - umax - 10, "контур розімкнено", size=9.5, color=POS, anchor="middle"))

    render(os.path.join(OUT, "saturation.svg"), W, H, *p,
           title="Насичення: за межами лінійної зони P більше нічого не додає")


# ── Фігура 4: шум давача × Kp = смикання дії ──────────────────────────────────
def fig_noise_gain():
    W, H = 720, 320
    p = []
    top = 40

    # верх: зашумлений вимір
    ox, oy = 80, 120
    Ax = 560
    p.append(text(ox, oy - 54, "вимір y (з шумом давача)", size=11, color=INK, anchor="start", bold=True))
    p.append(line(ox, oy, ox + Ax, oy, color=MUTED, sw=1.2, dash="5 4"))
    import random
    random.seed(7)
    base = [0.0] * 220
    noise = [ (random.random() - 0.5) for _ in base ]
    pts = []
    for i, nsv in enumerate(noise):
        x = ox + Ax * i / (len(noise) - 1)
        y = oy - nsv * 26
        pts.append((x, y))
    p.append(polyline(pts, color=INK, sw=1.4))

    # низ: дія = Kp × шум (той самий шум, більша амплітуда)
    oy2 = 250
    p.append(text(ox, oy2 - 70, "дія u = Kp·e: той самий шум, помножений на Kp", size=11, color=POS, anchor="start", bold=True))
    p.append(line(ox, oy2, ox + Ax, oy2, color=MUTED, sw=1.2, dash="5 4"))
    pts2 = []
    for i, nsv in enumerate(noise):
        x = ox + Ax * i / (len(noise) - 1)
        y = oy2 - nsv * 26 * 2.6      # помножено на Kp
        pts2.append((x, y))
    p.append(polyline(pts2, color=POS, sw=1.4))

    render(os.path.join(OUT, "noise-gain.svg"), W, H, *p,
           title="Kp множить шум давача прямо в керма моторів")


# ── Фігура 5: P-на-помилці проти P-на-вимірі (стрибок завдання) ────────────────
def fig_p_on_measurement():
    W, H = 720, 340
    p = []
    ox, oy = 80, 150
    Ax = 560

    # верхня панель: завдання (стрибок) і вихід
    y_lo = oy
    y_hi = oy - 70
    axes_top = 56
    p.append(text(ox, axes_top, "завдання стрибає r: 0 → 1", size=11, color=INK, anchor="start", bold=True))
    # вісь часу
    p.append(line(ox, oy + 10, ox + Ax, oy + 10, color=INK, sw=1.4))
    # східець завдання
    jx = ox + Ax * 0.18
    p.append(polyline([(ox, y_lo), (jx, y_lo), (jx, y_hi), (ox + Ax, y_hi)], color=MUTED, sw=2.0, dash="6 4"))
    p.append(text(ox + Ax - 4, y_hi - 8, "нове завдання", size=9.5, color=MUTED, anchor="end"))
    # вихід (плавно повзе) — спільний для обох
    pts = [(ox, y_lo), (jx, y_lo)]
    N = 160
    for i in range(N):
        frac = i / (N - 1)
        x = jx + (ox + Ax - jx) * frac
        y = y_lo + (y_hi - y_lo) * (1 - math.exp(-3.2 * frac))
        pts.append((x, y))
    p.append(polyline(pts, color=INK, sw=2.2))
    p.append(text(ox + Ax - 4, y_lo - 4, "вихід y", size=9.5, color=INK, anchor="end"))

    # нижня панель: дія u — два варіанти
    base2 = 300
    p.append(text(ox, base2 - 96, "дія регулятора u у момент стрибка:", size=11, color=INK, anchor="start", bold=True))
    p.append(line(ox, base2, ox + Ax, base2, color=INK, sw=1.4))

    # P-на-помилці: миттєвий стрибок угору (ривок), тоді спад
    ptsE = [(ox, base2), (jx, base2)]
    kick = 74
    ptsE.append((jx, base2 - kick))
    for i in range(N):
        frac = i / (N - 1)
        x = jx + (ox + Ax - jx) * frac
        y = base2 - kick * math.exp(-3.2 * frac)
        ptsE.append((x, y))
    p.append(polyline(ptsE, color=POS, sw=2.4))
    p.append(text(jx + 6, base2 - kick - 4, "P-на-помилці: РИВОК", size=9.5, color=POS, anchor="start", bold=True))

    # P-на-вимірі: без стрибка, плавно наростає з міри
    ptsM = [(ox, base2), (jx, base2)]
    for i in range(N):
        frac = i / (N - 1)
        x = jx + (ox + Ax - jx) * frac
        # пропорційно виміру, що повзе: дзеркально до кривої виходу
        y = base2 - kick * (1 - math.exp(-3.2 * frac)) * 0.5
        ptsM.append((x, y))
    p.append(polyline(ptsM, color=FIELD, sw=2.4, dash="6 4"))
    p.append(text(ox + Ax - 4, base2 - 24, "P-на-вимірі: плавно", size=9.5, color=FIELD, anchor="end", bold=True))

    render(os.path.join(OUT, "p-on-measurement.svg"), W, H, *p,
           title="P-на-помилці дає ривок на стрибку завдання; P-на-вимірі — ні")


if __name__ == "__main__":
    fig_first_order_speedup()
    fig_second_order_damping()
    fig_saturation()
    fig_noise_gain()
    fig_p_on_measurement()
    print("OK: detailed figures written to", OUT)
