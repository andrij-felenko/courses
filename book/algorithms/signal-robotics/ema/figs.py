# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── update: один крок EMA — зсув оцінки на частку α до нового відліку ──────────
# Ідея: на числовій осі стоять поточна оцінка y і новий відлік x; між ними
# проміжок (x − y); фільтр пересуває y на частку α цього проміжку. Усе — одне
# множення.

def fig_update():
    W, H = 700, 240
    ax0, ax1, ay = 80, 620, 150
    p = []

    # числова вісь
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.8))
    p.append(arrow(ax1 - 1, ay, ax1, ay, color=INK, sw=1.8))

    yx = ax0 + 90          # положення y
    xx = ax1 - 70          # положення x
    a = 0.32
    nx = yx + a * (xx - yx)  # новий y після кроку

    # дужка проміжку (x − y)
    bracket_y = ay - 54
    p.append(line(yx, ay - 10, yx, bracket_y, color=MUTED, sw=1.2, dash="4 3"))
    p.append(line(xx, ay - 10, xx, bracket_y, color=MUTED, sw=1.2, dash="4 3"))
    p.append(line(yx, bracket_y, xx, bracket_y, color=MUTED, sw=1.4))
    p.append(text((yx + xx) / 2, bracket_y - 8, "проміжок (x − y)", size=12, color=MUTED))

    # відрізок кроку α·(x − y) — гарячий
    p.append(line(yx, ay + 34, nx, ay + 34, color=POS, sw=3.2))
    p.append(line(yx, ay + 26, yx, ay + 42, color=POS, sw=2))
    p.append(line(nx, ay + 26, nx, ay + 42, color=POS, sw=2))
    p.append(text((yx + nx) / 2, ay + 58, "крок α·(x − y)", size=12, color=POS, bold=True))

    # точки на осі
    p.append(circle(yx, ay, 5.5, fill=BG, stroke=INK, sw=2))
    p.append(text(yx, ay - 16, "y", size=15, color=INK, bold=True, italic=True))
    p.append(text(yx, ay + 18, "оцінка", size=10, color=MUTED))

    p.append(circle(xx, ay, 5.5, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(xx, ay - 16, "x", size=15, color=POS, bold=True, italic=True))
    p.append(text(xx, ay + 18, "відлік", size=10, color=MUTED))

    # нова оцінка
    p.append(circle(nx, ay, 4.5, fill=FIELD, stroke=FIELD, sw=2))
    p.append(arrow(yx + 8, ay, nx - 6, ay, color=FIELD, sw=2.2))
    p.append(text(nx, ay + 18, "новий y", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "update.svg"), W, H, *p,
           title="Один крок EMA: оцінку підштовхують на частку α до нового відліку")


# ── weighting: ваги минулих відліків спадають експоненційно з віком ───────────
# Ідея: стовпчики ваг α, (1−α)α, (1−α)²α… вишиковуються в спадну експоненту;
# поруч пунктиром — рівні ваги ковзного середнього, що різко обриваються.

def fig_weighting():
    W, H = 700, 320
    ox, oy = 80, 250
    aw, ah = 560, 196
    p = []

    a = 0.45
    n = 11
    dx = aw / (n + 1)

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "вік відліку (кроків назад)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah + 4, "вага", size=12, color=INK, bold=True, anchor="end"))

    # стовпчики ваг EMA: w_k = a*(1-a)^k
    wmax = a
    scale = (ah - 16) / wmax
    for k in range(n):
        w = a * (1 - a) ** k
        h = w * scale
        bx = ox + (k + 0.5) * dx
        p.append(rect(bx, oy - h, dx * 0.62, h, fill="#fde7e3", stroke=POS, sw=1.2, rx=2))

    # пунктирна гребінка ковзного середнього (рівні ваги, різкий обрив)
    Nbox = 5
    wbox = (a) * 0.9              # умовний рівень для наочності
    hb = wbox * scale
    for k in range(Nbox):
        bx = ox + (k + 0.5) * dx + dx * 0.62
        p.append(line(bx, oy - hb, bx + dx * 0.30, oy - hb, color=NEG, sw=1.6, dash="3 2"))
        p.append(line(bx, oy, bx, oy - hb, color=NEG, sw=1.0, dash="2 3"))
    # обрив гребінки
    bx_cut = ox + (Nbox - 0.5) * dx + dx * 0.62 + dx * 0.30
    p.append(line(bx_cut, oy - hb, bx_cut, oy, color=NEG, sw=1.6, dash="3 2"))

    # легенда
    p.append(rect(ox + aw - 260, oy - ah + 6, 14, 12, fill="#fde7e3", stroke=POS, sw=1.2, rx=2))
    p.append(text(ox + aw - 240, oy - ah + 16, "EMA: спадають експоненційно, ніколи не зникають",
                  size=10, color=POS, anchor="start"))
    p.append(line(ox + aw - 260, oy - ah + 30, ox + aw - 246, oy - ah + 30, color=NEG, sw=1.6, dash="3 2"))
    p.append(text(ox + aw - 240, oy - ah + 34, "ковзне середнє: рівні, тоді різкий обрив",
                  size=10, color=NEG, anchor="start"))

    render(os.path.join(OUT, "weighting.svg"), W, H, *p,
           title="Чому «експоненційне»: ваги минулого спадають у (1−α) разів за крок")


# ── alpha: мала α — гладко й повільно; велика α — спритно й шумно ──────────────
# Ідея: один зашумлений вхід, дві EMA-оцінки: мала α (гладка, загайна) і велика
# α (спритна, шумна) — той самий компроміс згладжування ↔ затримка.

def fig_alpha():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 590, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "відліки", size=11, color=INK, italic=True, anchor="end"))

    N = 120
    sx = aw / N
    base = oy - ah * 0.30
    amp = ah * 0.42

    # зашумлений вхід (сходинка вгору + шум) — детермінований «шум»
    def signal(i):
        step = 0.0 if i < N * 0.35 else 1.0
        noise = 0.16 * math.sin(i * 1.7) + 0.11 * math.sin(i * 0.7 + 1.0) + 0.08 * math.sin(i * 3.1)
        return step + noise

    xs = [signal(i) for i in range(N)]

    def to_y(v):
        return base - v * amp

    # сирий вхід — світло-сірий
    pts = ["%.1f,%.1f" % (ox + i * sx, to_y(xs[i])) for i in range(N)]
    p.append('<polyline points="%s" fill="none" stroke="#c4c8cf" stroke-width="1.4"/>' % " ".join(pts))

    # EMA з двома α
    def ema(alpha):
        y = xs[0]
        out = []
        for v in xs:
            y = y + alpha * (v - y)
            out.append(y)
        return out

    small = ema(0.06)
    big = ema(0.45)

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
             % (" ".join("%.1f,%.1f" % (ox + i * sx, to_y(small[i])) for i in range(N)), FIELD))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
             % (" ".join("%.1f,%.1f" % (ox + i * sx, to_y(big[i])) for i in range(N)), NEG))

    # легенда
    p.append(line(ox + 20, oy - ah + 10, ox + 46, oy - ah + 10, color="#c4c8cf", sw=1.6))
    p.append(text(ox + 52, oy - ah + 14, "зашумлений вхід", size=10, color=MUTED, anchor="start"))
    p.append(line(ox + 20, oy - ah + 28, ox + 46, oy - ah + 28, color=FIELD, sw=2.6))
    p.append(text(ox + 52, oy - ah + 32, "мала α (0.06) — гладко, але загайно", size=10, color=FIELD, anchor="start", bold=True))
    p.append(line(ox + 20, oy - ah + 46, ox + 46, oy - ah + 46, color=NEG, sw=2.2))
    p.append(text(ox + 52, oy - ah + 50, "велика α (0.45) — спритно, та шумно", size=10, color=NEG, anchor="start", bold=True))

    render(os.path.join(OUT, "alpha.svg"), W, H, *p,
           title="Одна ручка α — увесь компроміс згладжування ↔ затримка")


# ── step: відгук EMA на стрибок — експоненційний підйом до нового рівня ────────
# Ідея: вхідна сходинка; EMA відповідає експонентою; позначено 63% за одну
# сталу часу й 95% за три.

def fig_step():
    W, H = 700, 300
    ox, oy = 70, 240
    aw, ah = 590, 186
    p = []

    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "відліки", size=11, color=INK, italic=True, anchor="end"))

    top = oy - ah * 0.86
    bot = oy - ah * 0.10

    # вхідна сходинка (сіра)
    sx0 = ox + aw * 0.18
    p.append(line(ox, bot, sx0, bot, color=MUTED, sw=1.8))
    p.append(line(sx0, bot, sx0, top, color=MUTED, sw=1.8, dash="5 4"))
    p.append(line(sx0, top, ox + aw, top, color=MUTED, sw=1.8, dash="5 4"))
    p.append(text(ox + aw - 4, top - 8, "новий рівень", size=10, color=MUTED, anchor="end"))

    # експонента EMA від сходинки
    span = aw - (sx0 - ox)
    tau_frac = 0.16            # частка span на одну сталу часу
    pts = []
    for i in range(0, 301):
        t = i / 300.0          # 0..1 уздовж span
        v = 1 - math.exp(-t / tau_frac)
        x = sx0 + t * span
        y = bot + (top - bot) * v
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-linejoin="round"/>'
             % (" ".join(pts), FIELD))

    # позначка 63% за τ
    def lvl(frac):
        return bot + (top - bot) * frac
    x_tau = sx0 + tau_frac * span
    p.append(line(sx0, lvl(0.63), x_tau, lvl(0.63), color=POS, sw=1.2, dash="3 3"))
    p.append(line(x_tau, oy, x_tau, lvl(0.63), color=POS, sw=1.2, dash="3 3"))
    p.append(text(x_tau + 6, lvl(0.63) + 4, "63% за τ", size=11, color=POS, anchor="start", bold=True))

    # позначка 95% за 3τ
    x_3tau = sx0 + 3 * tau_frac * span
    p.append(line(sx0, lvl(0.95), x_3tau, lvl(0.95), color=NEG, sw=1.2, dash="3 3"))
    p.append(line(x_3tau, oy, x_3tau, lvl(0.95), color=NEG, sw=1.2, dash="3 3"))
    p.append(text(x_3tau + 6, lvl(0.95) - 6, "95% за 3τ", size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(OUT, "step.svg"), W, H, *p,
           title="Відгук EMA на стрибок: експонента, не рампа і не миттєвий стрибок")


# ── rc-twin: EMA дає ту саму експоненту, що й аналогова RC-ланка ───────────────
# Ідея: ліворуч схема RC (резистор+конденсатор), праворуч EMA-формула; між ними
# однакова крива заряду — підпис «один і той самий фільтр 1-го порядку».

def fig_rc_twin():
    W, H = 700, 300
    p = []

    # ── ліва панель: RC-ланка ──
    lx = 60
    p.append(text(lx + 90, 56, "Аналог: RC-ланка", size=13, color=NEG, bold=True))
    # вхід
    p.append(text(lx, 110, "Uвх", size=12, color=INK, anchor="start", italic=True))
    p.append(line(lx + 30, 110, lx + 70, 110, color=INK, sw=1.8))
    # резистор (зигзаг)
    zz = "M%d 110" % (lx + 70)
    x = lx + 70
    for i in range(6):
        x += 8
        zz += " L%d %d" % (x, 110 + (10 if i % 2 == 0 else -10))
    zz += " L%d 110" % (x + 8)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (zz, INK))
    p.append(text(lx + 92, 92, "R", size=12, color=INK, italic=True))
    node_x = x + 8 + 22
    p.append(line(x + 8, 110, node_x, 110, color=INK, sw=1.8))
    # конденсатор донизу
    p.append(line(node_x, 110, node_x, 142, color=INK, sw=1.8))
    p.append(line(node_x - 14, 142, node_x + 14, 142, color=INK, sw=2.4))
    p.append(line(node_x - 14, 150, node_x + 14, 150, color=INK, sw=2.4))
    p.append(line(node_x, 150, node_x, 178, color=INK, sw=1.8))
    p.append(text(node_x + 20, 150, "C", size=12, color=INK, anchor="start", italic=True))
    # вихід
    p.append(line(node_x, 110, node_x + 40, 110, color=INK, sw=1.8))
    p.append(circle(node_x + 40, 110, 3.2, fill=INK, stroke=INK, sw=1))
    p.append(text(node_x + 48, 106, "Uвих", size=12, color=INK, anchor="start", italic=True))
    # земля
    gy = 182
    p.append(line(node_x - 10, gy, node_x + 10, gy, color=INK, sw=1.6))
    p.append(line(node_x - 6, gy + 4, node_x + 6, gy + 4, color=INK, sw=1.6))
    p.append(text(lx + 96, 214, "стала часу τ = R·C", size=11, color=NEG))

    # ── права панель: EMA ──
    rx = 400
    p.append(text(rx + 110, 56, "Код: EMA", size=13, color=FIELD, bold=True))
    box, bw, bh = textbox(rx + 110, 120, "y += α·(x − y)", size=14, bold=True,
                          fill="#eafaf0", stroke=FIELD, sw=2, pad=16)
    p.append(box)
    p.append(text(rx + 110, 168, "α грає роль сталої часу", size=11, color=FIELD))

    # ── спільна крива заряду внизу ──
    cx0, cy0 = 80, 280
    cw, chh = 540, 70
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        v = 1 - math.exp(-3.0 * t)
        pts.append("%.1f,%.1f" % (cx0 + t * cw, cy0 - v * chh))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
             % (" ".join(pts), INK))
    p.append(text(W / 2, cy0 + 16, "та сама експонента заряду — один фільтр 1-го порядку, в залізі й у коді",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "rc-twin.svg"), W, H, *p,
           title="EMA = RC у коді: однакова експонента, лише носій різний")


# ── cost: ціна на МК — EMA (1 число) проти буфера середнього й сортування ─────
# Ідея: три стовпці-фільтри з «ціною» пам'яті/такту; EMA — крихітна смужка
# поряд із буфером ковзного середнього й сортуванням медіани.

def fig_cost():
    W, H = 700, 320
    p = []
    base = 250
    colw = 150
    gap = 40
    x0 = 90

    items = [
        ("Ковзне середнє", "буфер N чисел\n+ N дій", 0.80, NEG, "#e9eefb"),
        ("Медіана", "буфер N + \nсортування щокроку", 1.00, POS, "#fdecea"),
        ("EMA", "1 число,\n1 множення", 0.10, FIELD, "#eafaf0"),
    ]
    maxh = 170
    for i, (name, sub, frac, col, fill) in enumerate(items):
        cx = x0 + i * (colw + gap)
        h = maxh * frac
        p.append(rect(cx, base - h, colw, h, fill=fill, stroke=col, sw=1.8, rx=4))
        p.append(text(cx + colw / 2, base + 18, name, size=12, color=col, bold=True))
        p.append(mtext(cx + colw / 2, base - h - 26, sub, size=10, color=MUTED, lh=1.25))

    p.append(line(x0 - 14, base, x0 + 3 * (colw + gap) - gap + 14, base, color=INK, sw=1.8))
    p.append(text(W / 2, H - 22, "за пам'яттю й тактами EMA дешевша на порядки — тому стандарт там, де ресурсів обмаль",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cost.svg"), W, H, *p,
           title="Чому EMA панує у вбудованих: ціна однієї змінної")


if __name__ == "__main__":
    fig_update()
    fig_weighting()
    fig_alpha()
    fig_step()
    fig_rc_twin()
    fig_cost()
    print("OK: figures written to", OUT)
