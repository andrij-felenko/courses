# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── discretization: інтеграл = сума прямокутників, похідна = нахил січної ──────
# Ідея: МК бачить не гладку криву, а відліки через Δt; інтеграл стає сумою
# стовпчиків e·Δt, похідна — нахилом січної між двома сусідніми відліками.

def fig_discretization():
    W, H = 700, 320
    ox, oy = 80, 250          # початок осей
    aw, ah = 560, 196         # довжина осей
    n = 9
    dx = aw / (n + 0.6)
    p = []

    # крива e(t), що спадає — беремо відліки на ній
    def ecurve(t):            # t у [0..1], повертає висоту над віссю в px
        return ah * (0.92 * math.exp(-2.1 * t) + 0.04)

    # стовпчики площі (інтеграл) — затінені прямокутники e·Δt
    for i in range(n):
        t = (i + 0.5) / n
        h = ecurve(t)
        bx = ox + i * dx
        p.append(rect(bx, oy - h, dx, h, fill="#eef4ff", stroke="#c9d6f0", sw=1.0, rx=0))

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 14, oy - ah - 2, "e", size=13, color=INK, bold=True, italic=True, anchor="end"))

    # гладка крива-першоджерело
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        pts.append("%.1f,%.1f" % (ox + t * (n * dx), oy - ecurve(t)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), MUTED))

    # точки-відліки на вершинах стовпчиків
    sample_xy = []
    for i in range(n):
        t = (i + 0.5) / n
        sx, sy = ox + i * dx + dx / 2, oy - ecurve(t)
        sample_xy.append((sx, sy))
        p.append(circle(sx, sy, 3.2, fill=INK, stroke=INK, sw=1))

    # січна між двома сусідніми відліками (похідна = нахил)
    (x1, y1), (x2, y2) = sample_xy[1], sample_xy[2]
    ext = 1.7
    sxa, sya = x1 - (x2 - x1) * (ext - 1), y1 - (y2 - y1) * (ext - 1)
    sxb, syb = x2 + (x2 - x1) * (ext - 1), y2 + (y2 - y1) * (ext - 1)
    p.append(line(sxa, sya, sxb, syb, color=NEG, sw=2.4))
    p.append(text(x2 + 12, y2 - 14, "похідна = нахил січної", size=11, color=NEG, anchor="start"))

    # підпис інтеграла всередині затінення
    p.append(text(ox + aw * 0.62, oy - ah * 0.62, "інтеграл = Σ стовпчиків e·Δt",
                  size=11, color="#3a5bb8"))

    render(os.path.join(OUT, "discretization.svg"), W, H, *p,
           title="МК бачить відліки: інтеграл стає сумою стовпчиків, похідна — нахилом січної")


# ── one-tick: дані за один такт регулятора ────────────────────────────────────
# Ідея: ланцюжок блоків від давача до виводу; підкреслено, що арифметики мало,
# а вага — у затисках (I, u) та фільтрі D.

def fig_one_tick():
    W, H = 740, 220
    p = []
    y = 110
    bw, bh = 78, 52
    step = 98
    x = 30
    boxes = [
        ("давач", FILL, INK),
        ("e = r − y", BG, INK),
        ("I += e·Δt\n(затиск)", "#eafaf0", INK),
        ("D з виміру\n(фільтр)", "#eef4ff", INK),
        ("u = Σ", BG, INK),
        ("затиск u", "#fdf6e3", INK),
        ("вивід", "#eafaf0", INK),
    ]
    centers = []
    for i, (lab, fill, col) in enumerate(boxes):
        b = fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=INK, sw=1.5, bold=True, color=col)
        p.append(b)
        centers.append((x, x + bw))
        if i > 0:
            px = centers[i - 1][1]
            p.append(arrow(px, y, x - 2, y, color=INK, sw=1.7))
        x += step

    p.append(text(W / 2, y + 64, "лічені множення й додавання — робота на мікросекунди",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "one-tick.svg"), W, H, *p,
           title="Один такт регулятора (кожні Δt)")


# ── sample-rate: часта дискретизація тримає, рідка — псує ──────────────────────
# Ідея: той самий ПІД на сходинку завдання; густі такти дають гладкий вихід,
# рідкі — переліт і розгойдування.

def fig_sample_rate():
    W, H = 700, 300
    ox, oy = 80, 250
    aw, ah = 560, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))

    # лінія завдання
    set_y = oy - ah * 0.62
    p.append(line(ox, set_y, ox + aw, set_y, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 4, set_y + 4, "завдання", size=10, color=MUTED, anchor="start"))

    span = 10.0
    sx = aw / span

    def curve(fn, color, sw=2.4):
        pts = []
        for i in range(0, 401):
            t = span * i / 400.0
            v = fn(t)
            pts.append("%.1f,%.1f" % (ox + t * sx, oy - v * ah * 0.62))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))

    # часта: плавний підйом до 1 без перельоту
    def fast(t):
        return 1.0 - math.exp(-1.2 * t)

    # рідка: переліт і повільне згасальне коливання навколо 1
    def slow(t):
        env = 1.0 - math.exp(-0.9 * t)
        osc = math.exp(-0.35 * t) * math.cos(2.0 * t)
        return env + 0.45 * osc * (t > 0.2)

    p.append(curve(slow, POS, 2.2))
    p.append(curve(fast, FIELD, 2.6))

    # легенда
    p.append(line(ox + 24, oy - ah + 8, ox + 50, oy - ah + 8, color=FIELD, sw=2.6))
    p.append(text(ox + 56, oy - ah + 12, "часто (100 Гц) — гладко й стійко",
                  size=11, color=FIELD, anchor="start", bold=True))
    p.append(line(ox + 24, oy - ah + 28, ox + 50, oy - ah + 28, color=POS, sw=2.2))
    p.append(text(ox + 56, oy - ah + 32, "рідко (5 Гц) — переліт, розгойдування",
                  size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "sample-rate.svg"), W, H, *p,
           title="Частота керування вирішує (той самий ПІД)")


# ── uniform-vs-jitter: рівномірні такти проти «плаваючих» ──────────────────────
# Ідея: однакові Δt дають коректні I/D; нерівні (джитер) спотворюють обидві
# складові, бо I множить на Δt, а D ділить на Δt.

def fig_uniform_vs_jitter():
    W, H = 700, 250
    p = []

    def ticks(x0, x1, y, xs, color):
        out = [line(x0, y, x1, y, color=INK, sw=2.0)]
        for i in range(len(xs)):
            out.append(line(xs[i], y - 8, xs[i], y + 8, color=INK, sw=2.0))
            if i < len(xs) - 1:
                mid = (xs[i] + xs[i + 1]) / 2
                out.append(text(mid, y + 22, "Δt", size=9, color=MUTED))
        return out

    x0, x1 = 70, 640

    # рівномірно
    p.append(text(x0, 70, "Рівномірно: однакове Δt → коректні I та D",
                  size=11, color=FIELD, anchor="start", bold=True))
    even = [x0 + i * (x1 - x0) / 7 for i in range(8)]
    p += ticks(x0, x1, 96, even, FIELD)

    # джитер
    p.append(text(x0, 160, "Джитер: крок «плаває» → I та D спотворені",
                  size=11, color=POS, anchor="start", bold=True))
    frac = [0.0, 0.09, 0.27, 0.34, 0.60, 0.66, 0.86, 1.0]
    jit = [x0 + f * (x1 - x0) for f in frac]
    p += ticks(x0, x1, 186, jit, POS)

    p.append(text(W / 2, 230, "I множить на Δt, D ділить на Δt — нерівний крок псує обидві складові",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "uniform-vs-jitter.svg"), W, H, *p,
           title="Сталий крок Δt — передумова правильного ПІД")


# ── four-guards: базова формула + чотири захисти ──────────────────────────────
# Ідея: гола сума трьох складових у центрі; навколо — чотири латки, кожна на
# свою відому аварію.

def fig_four_guards():
    W, H = 700, 300
    cx, cy = W / 2, 150
    p = []

    # центр — базова формула
    core, cw, ch = textbox(cx, cy, "u = Kp·e + Ki·∫e + Kd·de/dt",
                           size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    p.append(core)
    p.append(text(cx, cy + ch / 2 - 6, "базова формула", size=10, color=MUTED))

    # чотири кутові латки
    guards = [
        (150, 64, "антивіндап:\nзатиск I", FIELD, "#eafaf0"),
        (W - 150, 64, "D з виміру\n+ ФНЧ", NEG, "#eef4ff"),
        (150, H - 64, "обмеження\nвиходу u", POS, "#fdecea"),
        (W - 150, H - 64, "скидання стану\nпри ввімкненні", "#8a5fb0", "#f2ecf8"),
    ]
    for gx, gy, lab, col, fill in guards:
        b, bw, bh = textbox(gx, gy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        # стрілка від латки до центру (до краю центральної рамки)
        dirx = 1 if gx < cx else -1
        diry = 1 if gy < cy else -1
        ax = gx + dirx * bw / 2
        ay = gy + diry * bh / 2 * 0.2 + (bh / 2 if diry > 0 else -bh / 2) * 0.0
        tx = cx - dirx * cw / 2
        ty = cy - diry * ch / 2
        p.append(line(ax, gy + diry * bh / 2, tx, ty, color=col, sw=1.7))
        p.append(b)

    render(os.path.join(OUT, "four-guards.svg"), W, H, *p,
           title="Надійний ПІД = формула + чотири захисти")


# ── time-budget: бюджет одного такту ──────────────────────────────────────────
# Ідея: смуга Δt = 5 мс, поділена на етапи; ПІД — тонка смужка, основне — запас.

def fig_time_budget():
    W, H = 700, 230
    p = []
    bx, by, bw, bh = 60, 110, 580, 54
    total = 5.0                       # мс
    segs = [
        ("читання\nдавачів", 0.5, "#cfe0f5"),
        ("фільтр", 0.2, "#dff0df"),
        ("ПІД", 0.02, "#f3dede"),
        ("вивід", 0.1, "#f6efd6"),
        ("запас (slack)", total - 0.82, "#efefef"),
    ]
    p.append(text(bx, by - 16, "період Δt = 5 мс (200 Гц)", size=11, color=INK, anchor="start", bold=True))
    x = bx
    for lab, ms, fill in segs:
        w = bw * ms / total
        p.append(rect(x, by, w, bh, fill=fill, stroke=INK, sw=1.4, rx=0))
        if w > 44:
            p.append(mtext(x + w / 2, by + bh / 2 - 4, lab, size=9, color=INK))
            p.append(text(x + w / 2, by + bh + 16, "%.2f мс" % ms, size=9, color=MUTED))
        x += w

    # тонкі сегменти (фільтр, ПІД, вивід) підписуємо разом унизу
    p.append(text(bx + bw * 0.13, by + bh + 34,
                  "фільтр ~0.2 · ПІД ~0.02 · вивід ~0.1 мс", size=9, color=POS, anchor="start"))

    p.append(text(W / 2, H - 18, "ПІД — найдешевший; якщо сума підбирається під Δt — час бити на сполох",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "time-budget.svg"), W, H, *p,
           title="Бюджет одного такту: усе має вкластися в Δt")


if __name__ == "__main__":
    fig_discretization()
    fig_one_tick()
    fig_sample_rate()
    fig_uniform_vs_jitter()
    fig_four_guards()
    fig_time_budget()
    print("OK: figures written to", OUT)
