# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Ролі-кольори (єдині для всіх фігур теми):
STATE = NEG          # стан / передбачення — холодне синє
MEAS  = FIELD        # вимір давача — зелене
WARN  = POS          # розплата / зростання похибки — гаряче червоне


def axis(ox, oy, axw, label="час"):
    return [arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6),
            text(ox + axw, oy + 20, label, size=12, color=INK, italic=True, anchor="end")]


# ── 1. deadreckon: точка + вектор швидкості → передбачене положення за Δt ─────
def fig_deadreckon():
    W, H = 700, 300
    bx, by = 110, 175           # теперішнє положення
    p = []
    # вісь руху
    p += [line(60, by, 640, by, color=MUTED, sw=1.0, dash="2 5")]
    # теперішнє положення
    p.append(circle(bx, by, 8, fill="#eaf0fd", stroke=STATE, sw=2.4))
    p.append(text(bx, by + 28, "x(t)", size=13, color=STATE, bold=True))
    # вектор швидкості
    vx = bx + 300
    p.append(arrow(bx, by, vx, by, color=STATE, sw=2.6))
    p.append(text((bx + vx) / 2, by - 12, "v · Δt", size=13, color=STATE, bold=True, italic=True))
    # передбачене положення
    p.append(circle(vx, by, 8, fill=BG, stroke=STATE, sw=2.0))
    p.append(text(vx, by + 28, "x(t+Δt)", size=13, color=STATE, bold=True))
    # «жодного давача не питали»
    p.append(text(vx + 120, by, "жодного давача\nне питали", size=11, color=MUTED, anchor="middle"))
    p[-1] = mtext(vx + 120, by - 6, ["жодного давача", "не питали"], size=11, color=MUTED)
    # формула
    f, fw, fh = textbox(W / 2, H - 34, "x(t+Δt) = x(t) + v · Δt", size=14, bold=True,
                        fill="#eef2fb", stroke=STATE, sw=1.6, pad=10)
    p.append(f)
    render(os.path.join(OUT, "deadreckon.svg"), W, H, *p,
           title="Передбачення = продовжити рух за фізикою")


# ── 2. fillgap: рідкі виміри + гладка лінія передбачення між ними ─────────────
def fig_fillgap():
    W, H = 700, 300
    ox, oy = 60, 235
    axw = 580
    p = list(axis(ox, oy, axw, label="час"))

    # гладка «справжня» крива (синусоїда + нахил) — лінія передбачення
    def curve_y(t):  # t у [0..1]
        return oy - (70 + 55 * math.sin(t * 6.3) + 80 * t)
    pts = [(ox + axw * i / 200, curve_y(i / 200)) for i in range(201)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>'
             % (" ".join("%.1f,%.1f" % q for q in pts), STATE))
    p.append(text(ox + axw - 6, curve_y(1.0) - 14, "передбачення щомиті",
                  size=11, color=STATE, anchor="end", bold=True))

    # рідкі шумні відліки GPS
    samples = [0.10, 0.30, 0.52, 0.74, 0.95]
    jit = [10, -13, 9, -8, 12]
    for t, j in zip(samples, jit):
        x = ox + axw * t
        y = curve_y(t) + j
        p.append(circle(x, y, 6, fill="#eafaf0", stroke=MEAS, sw=2.2))
    p.append(text(ox + axw * samples[0], curve_y(samples[0]) + 36, "виміри GPS — рідко й шумно",
                  size=11, color=MEAS, anchor="start", bold=True))

    render(os.path.join(OUT, "fillgap.svg"), W, H, *p,
           title="Передбачення тримає темп між рідкими вимірами")


def cloud(cx, cy, rx, ry, color, op=0.16):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="1.2" stroke-opacity="0.6"/>'
            % (cx, cy, rx, ry, color, op, color))


# ── 3. uncertainty: хмара розпливається ширше з кожним кроком без виміру ──────
def fig_uncertainty():
    W, H = 700, 320
    ox, oy = 70, 250
    axw = 560
    p = list(axis(ox, oy, axw, label="час без виміру"))

    # траєкторія
    def ty(t):  # t у [0..1]
        return oy - (60 + 110 * t)
    pts = [(ox + axw * i / 100, ty(i / 100)) for i in range(101)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % q for q in pts), WARN))

    # хмари, що ширшають
    for i, t in enumerate((0.06, 0.30, 0.55, 0.82, 1.0)):
        x = ox + axw * t
        y = ty(t)
        r = 9 + 46 * t
        p.append(cloud(x, y, r, r * 0.55, WARN))
        p.append(circle(x, y, 3, fill=WARN, stroke=WARN, sw=1))
    p.append(text(ox + axw * 0.06, ty(0.06) + 36, "щойно після виміру:\nтісно, ми певні",
                  size=10, color=MUTED, anchor="start"))
    p[-1] = mtext(ox + axw * 0.06, ty(0.06) + 40, ["щойно після виміру:", "тісно, ми певні"],
                  size=10, color=MUTED, anchor="start")
    p.append(text(ox + axw, ty(1.0) - 50, "що довше без виміру —\nто менше довіри",
                  size=10, color=WARN, anchor="end"))
    p[-1] = mtext(ox + axw, ty(1.0) - 52, ["що довше без виміру —", "то менше довіри"],
                  size=10, color=WARN, anchor="end")

    render(os.path.join(OUT, "uncertainty.svg"), W, H, *p,
           title="Розплата: невизначеність росте з кожним кроком")


# ── 4. cv-ca: дві моделі — стала швидкість і стале прискорення ────────────────
def fig_cv_ca():
    W, H = 700, 300
    p = []

    def panel(ox, title, accel):
        oy = 230
        axw = 250
        out = list(axis(ox, oy, axw, label="час"))
        out.append(text(ox + axw / 2, 60, title, size=12, color=INK, bold=True))
        # траєкторія положення
        def ty(t):
            base = 60 * t
            if accel:
                base += 90 * t * t
            return oy - (28 + base)
        pts = [(ox + axw * i / 80, ty(i / 80)) for i in range(81)]
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                   % (" ".join("%.1f,%.1f" % q for q in pts), STATE))
        return out, oy, axw

    # CV — пряма (стала швидкість)
    out, oy, axw = panel(60, "стала швидкість (CV)", accel=False)
    p += out
    p.append(mtext(60 + axw / 2, oy + 46, ["стан: x, v", "новий x = x + v·Δt"],
                   size=11, color=MUTED))

    # CA — дуга (стале прискорення)
    out, oy, axw = panel(390, "стале прискорення (CA)", accel=True)
    p += out
    p.append(mtext(390 + axw / 2, oy + 46, ["стан: x, v, a", "v = v + a·Δt;  x = x + v·Δt"],
                   size=11, color=MUTED))

    render(os.path.join(OUT, "cv-ca.svg"), W, H, *p,
           title="Дві типові моделі руху: що кладемо у стан")


# ── 5. predict-step: СТАН → МОДЕЛЬ РУХУ → СТАН за Δt; пунктир — корекція ──────
def fig_predict_step():
    W, H = 700, 300
    cy = 150
    p = []

    b1, w1, h1 = textbox(135, cy, "СТАН\nзараз", size=13, bold=True,
                         fill="#eaf0fd", stroke=STATE, sw=2.0, color=STATE)
    b2, w2, h2 = textbox(355, cy, "МОДЕЛЬ РУХУ\n(+ вхід: газ, IMU)", size=12, bold=True,
                         fill="#f4f6f8", stroke=INK, sw=1.8)
    b3, w3, h3 = textbox(575, cy, "СТАН\nза Δt", size=13, bold=True,
                         fill="#eef2fb", stroke=STATE, sw=2.0, color=STATE)
    p += [b1, b2, b3]
    p.append(arrow(135 + w1 / 2, cy, 355 - w2 / 2, cy, color=INK, sw=2.0))
    p.append(arrow(355 + w2 / 2, cy, 575 - w3 / 2, cy, color=INK, sw=2.0))
    p.append(text(575, cy - h3 / 2 - 12, "+ ширша хмара", size=10, color=WARN))

    # пунктир-корекція знизу
    p.append(line(575, cy + h3 / 2, 575, cy + 72, color=MUTED, sw=1.4, dash="4 4"))
    p.append(line(575, cy + 72, 135, cy + 72, color=MUTED, sw=1.4, dash="4 4"))
    p.append(arrow(135, cy + 72, 135, cy + h1 / 2 + 2, color=MUTED, sw=1.4))
    bb, _, _ = textbox(355, cy + 72, "корекція: вимір виправить (інша тема)",
                       size=10, fill=BG, stroke=MUTED, sw=1.2, color=MUTED)
    p.append(bb)

    render(os.path.join(OUT, "predict-step.svg"), W, H, *p,
           title="Передбачення — ліва половина циклу оцінювання")


if __name__ == "__main__":
    fig_deadreckon()
    fig_fillgap()
    fig_uncertainty()
    fig_cv_ca()
    fig_predict_step()
    print("OK: figures written to", OUT)
