# -*- coding: utf-8 -*-
"""Фігури до теми «Другий закон Ньютона».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def poly(points, fill=FILL, stroke='none', sw=0.0):
    """Многокутник (для заштрихованих площ) — локальний помічник цієї теки."""
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


# ── Фігура 1: та сама сила, різні маси → різне прискорення ────────────────────
def fig_proportionality():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Та сама сила: важче тіло розганяється повільніше",
                  size=17, bold=True))

    def row(cy, mlabel, block_h, a_len, a_label, note):
        # блок (маса)
        bx, bw = 250, 96
        by = cy - block_h / 2
        f.append(rect(bx, by, bw, block_h, fill="#eef2fb", stroke=INK, sw=2, rx=6))
        f.append(text(bx + bw / 2, cy + 7, mlabel, size=20, bold=True, color=NEG))
        # сила F — однакова стрілка, штовхає блок зліва (над блоком)
        fy = cy - block_h / 2 - 26
        f.append(arrow(120, fy, bx - 6, fy, color=POS, sw=3.4))
        f.append(text(112, fy - 8, "F", size=17, bold=True, color=POS, anchor="end"))
        f.append(text((120 + bx) / 2, fy - 8, "однакова", size=12, color=MUTED))
        # прискорення a — знизу блока, довжина ∝ a
        ay = cy + block_h / 2 + 30
        f.append(arrow(bx + bw + 6, ay, bx + bw + 6 + a_len, ay, color=FIELD, sw=3.4))
        f.append(text(bx + bw + 6 + a_len + 10, ay + 6, a_label,
                      size=15, bold=True, color=FIELD, anchor="start"))
        f.append(text(bx + bw + 6, ay + 26, note, size=12, color=MUTED, anchor="start"))

    row(155, "m", 62, 300, "a", "велике прискорення")
    row(320, "2m", 96, 150, "a / 2", "удвічі менше")

    b, w, h = textbox(W / 2, H - 30,
                      "a = F / m     однакова F, удвічі більша маса  →  удвічі менше a",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "proportionality.svg"), W, H, *f)


# ── Фігура 2: рівнодійна сил і прискорення вздовж неї ─────────────────────────
def fig_net_force():
    W, H = 780, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Тіло слухає векторну суму сил",
                  size=17, bold=True))

    B = (250, 330)                       # тіло
    f.append(circle(B[0], B[1], 15, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(B[0] - 24, B[1] + 30, "тіло", size=12, color=MUTED, anchor="middle"))

    # дві прикладені сили
    F1 = (B[0] + 210, B[1])              # праворуч
    F2 = (B[0], B[1] - 165)             # угору
    f.append(arrow(B[0], B[1], F1[0], F1[1], color=POS, sw=3.0))
    f.append(text(F1[0] + 14, F1[1] + 6, "F₁", size=16, bold=True, color=POS, anchor="start"))
    f.append(arrow(B[0], B[1], F2[0], F2[1], color=POS, sw=3.0))
    f.append(text(F2[0] - 6, F2[1] - 12, "F₂", size=16, bold=True, color=POS, anchor="middle"))

    # побудова «тіп-у-тіл»: від кінця F1 угору на довжину F2 (пунктир)
    T = (F1[0], F1[1] - 165)
    f.append(line(F1[0], F1[1], T[0], T[1], color=MUTED, sw=1.4, dash="5 5"))
    f.append(line(F2[0], F2[1], T[0], T[1], color=MUTED, sw=1.4, dash="5 5"))

    # рівнодійна від тіла до кута побудови
    f.append(arrow(B[0], B[1], T[0], T[1], color=NEG, sw=3.6))
    f.append(text(T[0] + 12, T[1] - 8, "F_рівн", size=16, bold=True, color=NEG, anchor="start"))

    # прискорення — паралельно рівнодійній, зсунуте в бік вільного поля
    dx, dy = T[0] - B[0], T[1] - B[1]
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    px, py = -uy, ux                     # перпендикуляр (управо-вниз)
    off = 30
    ax0, ay0 = B[0] + px * off, B[1] + py * off
    aL = 140
    ax1, ay1 = ax0 + ux * aL, ay0 + uy * aL
    f.append(arrow(ax0, ay0, ax1, ay1, color=FIELD, sw=3.2))
    f.append(text(ax1 + 12, ay1 + 20, "a", size=16, bold=True, color=FIELD, anchor="start"))

    b, w, h = textbox(W / 2, H - 30,
                      "a = F_рівн / m     напрямлене вздовж рівнодійної",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "net-force.svg"), W, H, *f)


# ── Фігура 3: сила — нахил графіка кількості руху за часом ────────────────────
def fig_momentum_slope():
    W, H = 780, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Сила — це нахил графіка кількості руху p(t)",
                  size=17, bold=True))

    O = (110, 380)                       # початок осей
    xr, yt = 690, 90
    # осі
    f.append(arrow(O[0], O[1], xr, O[1], color=INK, sw=2.0))
    f.append(arrow(O[0], O[1], O[0], yt, color=INK, sw=2.0))
    f.append(text(xr - 4, O[1] + 26, "час  t", size=13, color=MUTED, anchor="end"))
    f.append(text(O[0] - 12, yt + 4, "p", size=15, italic=True, color=MUTED, anchor="end"))
    f.append(text(O[0] + 8, yt - 2, "кількість руху", size=12, color=MUTED, anchor="start"))

    # крута лінія — велика сила
    S = (560, 120)
    f.append(line(O[0], O[1], S[0], S[1], color=NEG, sw=3.2))
    f.append(text(S[0] + 12, S[1] - 2, "велика сила", size=13, bold=True, color=NEG, anchor="start"))

    # полога лінія — мала сила
    G = (650, 260)
    f.append(line(O[0], O[1], G[0], G[1], color=FIELD, sw=3.2))
    f.append(text(G[0] + 12, G[1] + 6, "мала сила", size=13, bold=True, color=FIELD, anchor="start"))

    # горизонталь — нульова сила, p стале (у вільному верхньо-лівому полі)
    hy = 150
    f.append(line(O[0], hy, 300, hy, color=MUTED, sw=2.2, dash="7 5"))
    f.append(text(O[0] + 6, hy - 12, "F = 0:  p стале", size=13, color=MUTED, anchor="start"))

    # трикутник нахилу на пологій лінії
    tx0 = 300
    ty0 = O[1] - (O[1] - G[1]) * (tx0 - O[0]) / (G[0] - O[0])
    tx1 = 430
    ty1 = O[1] - (O[1] - G[1]) * (tx1 - O[0]) / (G[0] - O[0])
    f.append(line(tx0, ty0, tx1, ty0, color=INK, sw=1.4))
    f.append(line(tx1, ty0, tx1, ty1, color=INK, sw=1.4))
    f.append(text((tx0 + tx1) / 2, ty0 + 18, "Δt", size=13, italic=True, color=INK))
    f.append(text(tx1 + 16, (ty0 + ty1) / 2 + 4, "Δp", size=13, italic=True, color=INK, anchor="start"))

    b, w, h = textbox(W / 2, H - 30,
                      "F = Δp / Δt     нахил лінії й дорівнює силі",
                      size=14, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "momentum-slope.svg"), W, H, *f)


# ── Фігура 4 (hist): закон народжувався століттями, не в одних руках ──────────
def fig_law_timeline():
    W, H = 900, 660
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 36, "Закон визрівав дві тисячі років і не в одних руках",
                  size=17, bold=True))
    ax = 262                              # вертикальна вісь часу
    y0, y1 = 84, 604
    f.append(line(ax, y0, ax, y1, color=MUTED, sw=2.5))

    rows = [
        ("~350 до н.е.", "Арістотель", "рух тримає сила; нема сили — рух гасне", POS),
        ("VI–XIV ст.",   "Філопон · Бурідан", "імпетус: тіло несе вкладену «силу руху»", MUTED),
        ("1632 · 1644",  "Ґалілей · Декарт", "інерція: рух триває сам, без сили", FIELD),
        ("1687",         "Ньютон, «Начала»", "закон через ЗМІНУ кількості руху — не F = ma", NEG),
        ("1716",         "Якоб Герман", "Phoronomia: F = m·dv/dt у явному вигляді", NEG),
        ("1750",         "Леонард Ейлер", "«нове начало»: загальна форма F = m·a", NEG),
        ("1948",         "9-та ГКМВ", "одиниці сили дають ім'я «ньютон»", INK),
    ]
    n = len(rows)
    for i, (yr, name, note, col) in enumerate(rows):
        cy = y0 + (y1 - y0) * (i + 0.5) / n
        f.append(circle(ax, cy, 8, fill=col, stroke=BG, sw=2))
        f.append(text(ax - 24, cy + 5, yr, size=13, bold=True, color=INK, anchor="end"))
        f.append(text(ax + 26, cy - 4, name, size=15, bold=True, color=col, anchor="start"))
        f.append(text(ax + 26, cy + 17, note, size=13, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, "law-timeline.svg"), W, H, *f)


# ── Фігура 5 (hist): переворот інтуїції — що робить сила ──────────────────────
def fig_aristotle_vs_inertia():
    W, H = 900, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Переворот інтуїції: що насправді робить сила",
                  size=17, bold=True))

    pw, ptop, ph = 400, 58, 340
    lx, rx = 30, 470
    f.append(rect(lx, ptop, pw, ph, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(rect(rx, ptop, pw, ph, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(lx + pw / 2, ptop + 30, "Світ Арістотеля", size=15, bold=True, color=POS))
    f.append(text(rx + pw / 2, ptop + 30, "Світ інерції  (Ґалілей → Ньютон)",
                  size=15, bold=True, color=FIELD))

    # ── ліва сцена: щоб їхати, треба штовхати ──
    gy = 210
    f.append(line(lx + 30, gy, lx + pw - 30, gy, color=MUTED, sw=2))
    bl = (lx + 150, gy - 36, 62, 36)      # блок стоїть на землі
    f.append(rect(bl[0], bl[1], bl[2], bl[3], fill="#ffffff", stroke=INK, sw=2, rx=5))
    f.append(arrow(lx + 70, gy - 18, bl[0] - 6, gy - 18, color=POS, sw=3.2))   # F штовхає
    f.append(text(lx + 62, gy - 24, "F", size=15, bold=True, color=POS, anchor="end"))
    f.append(arrow(bl[0] + bl[2] + 6, gy - 18, bl[0] + bl[2] + 60, gy - 18, color=NEG, sw=2.6))
    f.append(text(bl[0] + bl[2] + 68, gy - 12, "v", size=14, bold=True, color=NEG, anchor="start"))
    f.append(text(lx + pw / 2, gy + 62, "Сила потрібна, щоб рух ТРИВАВ", size=14, bold=True))
    f.append(text(lx + pw / 2, gy + 90, "прибери силу — тіло спиняється", size=13, color=MUTED))

    # ── права сцена: ковзає само, сила лише міняє рух ──
    f.append(line(rx + 30, gy, rx + pw - 30, gy, color=NEG, sw=2))
    for hx in range(rx + 36, rx + pw - 30, 22):        # штрихування — гладкий лід
        f.append(line(hx, gy, hx - 9, gy + 9, color=NEG, sw=1))
    br = (rx + 120, gy - 36, 62, 36)
    f.append(rect(br[0], br[1], br[2], br[3], fill="#ffffff", stroke=INK, sw=2, rx=5))
    f.append(arrow(br[0] + br[2] + 6, gy - 18, br[0] + br[2] + 96, gy - 18, color=NEG, sw=3.0))
    f.append(text(br[0] + br[2] + 104, gy - 12, "v", size=14, bold=True, color=NEG, anchor="start"))
    f.append(text(br[0] + br[2] / 2, gy - 50, "F = 0", size=13, bold=True, color=MUTED))
    f.append(text(rx + pw / 2, gy + 62, "Рух триває сам — це інерція", size=14, bold=True))
    f.append(text(rx + pw / 2, gy + 90, "сила лише МІНЯЄ рух → прискорення", size=13, color=MUTED))

    return render(os.path.join(IMG, "aristotle-vs-inertia.svg"), W, H, *f)


# ── Фігура 6 (math): ракета — баланс кількості руху за мить dt ────────────────
def fig_rocket_momentum():
    W, H = 860, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Ракета за мить dt: газ несе рух назад — корпус набирає вперед",
                  size=16, bold=True))

    # роздільник панелей + підписи миттєвостей
    f.append(line(430, 66, 430, 300, color=MUTED, sw=1.2, dash="4 6"))
    f.append(text(215, 90, "мить t", size=14, bold=True, color=MUTED))
    f.append(text(645, 90, "мить t + dt", size=14, bold=True, color=MUTED))

    def rocket(x, w, cy, mlabel, vx1, vlabel):
        # корпус + ніс праворуч
        f.append(rect(x, cy - 28, w, 56, fill="#eef2fb", stroke=INK, sw=2, rx=8))
        f.append(poly([(x + w, cy - 28), (x + w + 24, cy), (x + w, cy + 28)],
                      fill="#eef2fb", stroke=INK, sw=2.0))
        f.append(text(x + w / 2, cy + 6, mlabel, size=17, bold=True, color=INK))
        # швидкість — стрілка над корпусом
        f.append(arrow(x, cy - 52, vx1, cy - 52, color=FIELD, sw=3.2))
        f.append(text(vx1 + 12, cy - 47, vlabel, size=15, bold=True, color=FIELD, anchor="start"))

    # ліва панель: маса m, швидкість v
    rocket(150, 128, 175, "m", 300, "v")
    b, w0, h0 = textbox(214, 262, "p = m · v", size=15, pad=9,
                        fill="#eef6ef", stroke=FIELD, sw=1.2, bold=True)
    f.append(b)

    # права панель: маса m+dm (трохи коротша), швидкість v+dv
    rocket(600, 112, 175, "m + dm", 748, "v + dv")
    # газ — червоний згусток позаду, летить назад
    f.append(circle(548, 175, 16, fill="#fdecea", stroke=POS, sw=2))
    f.append(arrow(548, 210, 468, 210, color=POS, sw=3.0))
    f.append(text(509, 233, "газ: маса −dm", size=12, color=POS))
    f.append(text(509, 251, "швидкість v − u", size=12, color=POS))

    # нижня смуга: баланс і тяга
    b2, w2, h2 = textbox(W / 2, 352, "m·dv = F·dt − u·dm     (dm < 0)",
                         size=15, pad=10, fill="#eef2fb", stroke=NEG, sw=1.2, bold=True)
    f.append(b2)
    b3, w3, h3 = textbox(W / 2, 424,
                         "тяга = u · |dm/dt| = швидкість витікання × витрата маси",
                         size=15, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b3)
    return render(os.path.join(IMG, "rocket-momentum.svg"), W, H, *f)


# ── Фігура 7 (math): імпульс сили — площа під графіком F(t) ────────────────────
def fig_impulse_area():
    W, H = 840, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Імпульс сили = площа під F(t); та сама Δp — різна сила",
                  size=16, bold=True))

    def panel(ox, oy, xr, yt, base0, base1, peakx, peaky,
              ptitle, note_top, note_bot, lblxy, tipxy):
        # осі
        f.append(arrow(ox, oy, xr, oy, color=INK, sw=2.0))
        f.append(arrow(ox, oy, ox, yt, color=INK, sw=2.0))
        f.append(text(xr - 2, oy + 24, "t", size=13, italic=True, color=MUTED, anchor="end"))
        f.append(text(ox - 10, yt + 2, "F", size=14, italic=True, color=MUTED, anchor="end"))
        # трикутний імпульс, заштрихований
        f.append(poly([(base0, oy), (peakx, peaky), (base1, oy)],
                      fill="#dbe7ff", stroke=NEG, sw=2.4))
        # пік — пунктир до осі F, підпис сили ліворуч угорі
        f.append(line(ox, peaky, peakx, peaky, color=MUTED, sw=1.1, dash="4 4"))
        f.append(text(ox + 6, peaky - 6, note_top, size=12, color=MUTED, anchor="start"))
        # основа — позначки часу + підпис
        f.append(line(base0, oy, base0, oy + 6, color=INK, sw=1.4))
        f.append(line(base1, oy, base1, oy + 6, color=INK, sw=1.4))
        f.append(text((base0 + base1) / 2, oy + 22, note_bot, size=12, color=MUTED))
        # заголовок панелі
        f.append(text((ox + xr) / 2, oy + 46, ptitle, size=13, bold=True, color=INK))
        # виноска «площа = Δp» з лінією-поводирем у трикутник
        f.append(line(lblxy[0], lblxy[1] + 5, tipxy[0], tipxy[1], color=NEG, sw=1.1))
        f.append(text(lblxy[0], lblxy[1], "площа = Δp", size=13, bold=True, color=NEG))

    # ліва панель — велика сила, короткий час (вузький високий пік)
    panel(80, 290, 400, 60, 150, 210, 180, 80,
          "жорстко: велика F, малий Δt", "велика F", "Δt малий",
          (300, 150), (190, 150))
    # права панель — мала сила, довгий час (широкий низький горб)
    panel(460, 290, 800, 60, 500, 780, 640, 245,
          "м'яко: мала F, великий Δt", "мала F", "Δt великий",
          (640, 150), (640, 244))

    b, w, h = textbox(W / 2, 408,
                      "∫ F dt = Δp     однакова площа ⇒ однакова зміна руху",
                      size=15, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "impulse-area.svg"), W, H, *f)


# ── Ламана (polyline) — для проєктної вставки про числове інтегрування ────────
def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── Фігура 8 (proj): стійкість кроку — вихід на граничну швидкість ────────────
def fig_terminal_stability():
    W, H = 880, 500
    g, beta, vterm = 9.8, 5.0, 1.96
    L, R, T, B = 92, 600, 74, 430
    tmax, ymin, ymax = 2.5, -3.0, 6.0
    X = lambda t: L + (t / tmax) * (R - L)
    Yv = lambda v: B - ((v - ymin) / (ymax - ymin)) * (B - T)

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Падіння з опором: завеликий явний крок вигадує вибух",
                  size=17, bold=True))

    # осі
    f.append(arrow(L, Yv(0), R + 8, Yv(0), color=INK, sw=1.8))
    f.append(text(R + 4, Yv(0) + 26, "час  t, с", size=12, color=MUTED, anchor="end"))
    f.append(arrow(L, B, L, T - 8, color=INK, sw=1.8))
    f.append(text(L + 6, T - 14, "швидкість v, м/с", size=12, color=MUTED, anchor="start"))
    for tv in (0.5, 1.0, 1.5, 2.0, 2.5):
        f.append(text(X(tv), Yv(0) + 16, "%.1f" % tv, size=10, color=MUTED))

    # гранична швидкість
    f.append(line(L, Yv(vterm), R, Yv(vterm), color=MUTED, sw=1.6, dash="7 5"))

    # точне
    exact = [(X(i / 100.0 * tmax), Yv(vterm * (1 - math.exp(-beta * i / 100.0 * tmax))))
             for i in range(0, 101)]
    f.append(polyline(exact, color=MUTED, sw=2.0, dash="2 4"))

    # явний Ейлер, дрібний крок 0.05
    dt, v, t = 0.05, 0.0, 0.0
    es = [(X(0), Yv(0))]
    while t < tmax - 1e-9:
        v = v + dt * (g - beta * v); t += dt
        es.append((X(t), Yv(v)))
    f.append(polyline(es, color=FIELD, sw=2.4))

    # неявний крок 0.5 — гладко до v_гр
    dt, v, t = 0.5, 0.0, 0.0
    im = [(X(0), Yv(0))]
    while t < tmax - 1e-9:
        v = (v + dt * g) / (1 + beta * dt); t += dt
        im.append((X(t), Yv(v)))
    f.append(polyline(im, color=NEG, sw=2.6))
    for (px, py) in im:
        f.append(circle(px, py, 3.0, fill=NEG, stroke=NEG, sw=1))

    # явний Ейлер, крок 0.5 — вибух (перші точки + стрілка за межу)
    big = [(0.0, 0.0), (0.5, 4.9), (1.0, -2.45)]
    f.append(polyline([(X(tt), Yv(vv)) for tt, vv in big], color=POS, sw=2.8))
    v3, v4 = -2.45, 8.575
    tc = 1.0 + (ymax - v3) / (v4 - v3) * 0.5      # де крива тне верхню межу
    f.append(arrow(X(1.0), Yv(v3), X(tc), Yv(ymax), color=POS, sw=2.8))

    # підписи праворуч, рознесені по вертикалі
    gx = 612
    f.append(text(gx, Yv(5.2), "явний Ейлер, Δt = 0.5 с", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(gx, Yv(4.55), "(понад поріг 2τ) → вибух", size=12, color=POS, anchor="start"))
    f.append(text(gx, Yv(3.0), "Ейлер, дрібний крок", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(gx, Yv(2.4), "точне (пунктир)", size=12, color=MUTED, anchor="start"))
    f.append(text(gx, Yv(vterm) - 8, "v_гр = 1.96 м/с", size=12, color=MUTED, anchor="start"))
    f.append(text(gx, Yv(1.0), "неявний, Δt = 0.5 с", size=13, bold=True, color=NEG, anchor="start"))

    return render(os.path.join(IMG, "terminal-stability.svg"), W, H, *f)


# ── Фігура 9 (proj): фазовий простір — дрейф енергії vs симплектичність ───────
def fig_phase_drift():
    W, H = 640, 640
    cx, cy, s = 300, 300, 89.0
    X = lambda x: cx + x * s
    Yv = lambda v: cy - v * s

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Фазовий простір: явний Ейлер тікає, напівнеявний тримається",
                  size=15, bold=True))

    # осі
    f.append(arrow(cx - 265, cy, cx + 265, cy, color=INK, sw=1.6))
    f.append(arrow(cx, cy + 265, cx, cy - 265, color=INK, sw=1.6))
    f.append(text(cx + 258, cy + 20, "положення x", size=12, color=MUTED, anchor="end"))
    f.append(text(cx + 12, cy - 250, "швидкість v", size=12, color=MUTED, anchor="start"))

    # точне коло (радіус 1)
    circ = [(X(math.cos(a / 120.0 * 2 * math.pi)), Yv(math.sin(a / 120.0 * 2 * math.pi)))
            for a in range(0, 121)]
    f.append(polyline(circ, color=MUTED, sw=2.0, dash="3 4"))

    dt, w = 0.1, 1.0
    # явний Ейлер — 3 періоди, спіраль назовні
    x, v = 1.0, 0.0
    euler = [(X(x), Yv(v))]
    for _ in range(int(round(3 * 2 * math.pi / dt))):
        xn = x + dt * v; vn = v - dt * w * w * x
        x, v = xn, vn; euler.append((X(x), Yv(v)))
    f.append(polyline(euler, color=POS, sw=1.8))

    # напівнеявний — замкнений овал коло кола
    x, v = 1.0, 0.0
    semi = [(X(x), Yv(v))]
    for _ in range(int(round(2.5 * 2 * math.pi / dt))):
        vn = v - dt * w * w * x; xn = x + dt * vn
        x, v = xn, vn; semi.append((X(x), Yv(v)))
    f.append(polyline(semi, color=NEG, sw=2.4))

    # легенда внизу
    lx, ly = 44, H - 92
    f.append(line(lx, ly, lx + 26, ly, color=MUTED, sw=2.0, dash="3 4"))
    f.append(text(lx + 34, ly + 4, "точне — коло сталого радіуса", size=12, color=MUTED, anchor="start"))
    f.append(line(lx, ly + 26, lx + 26, ly + 26, color=POS, sw=2.2))
    f.append(text(lx + 34, ly + 30, "явний Ейлер — спіраль назовні (енергія росте)", size=12, bold=True, color=POS, anchor="start"))
    f.append(line(lx, ly + 52, lx + 26, ly + 52, color=NEG, sw=2.4))
    f.append(text(lx + 34, ly + 56, "напівнеявний — замкнено (енергія без дрейфу)", size=12, bold=True, color=NEG, anchor="start"))

    return render(os.path.join(IMG, "phase-drift.svg"), W, H, *f)


# ── Фігура 10 (proj): траєкторії — порожнеча проти квадратичного опору ────────
def fig_projectile_drag():
    W, H = 900, 440
    L, R, T, B = 72, 858, 52, 372
    xmax, ymax = 172.0, 46.0
    X = lambda x: L + (x / xmax) * (R - L)
    Yy = lambda y: B - (y / ymax) * (B - T)
    g = 9.8

    def traj(mode, v0=40.0, ang=45.0, dt=0.004, m=0.145, c=9.03e-4):
        th = math.radians(ang); vx = v0 * math.cos(th); vy = v0 * math.sin(th)
        x = y = 0.0
        pts = [(X(0), Yy(0))]
        while True:
            if mode == "quad":
                sp = math.hypot(vx, vy)
                ax = -(c / m) * sp * vx; ay = -g - (c / m) * sp * vy
            else:
                ax, ay = 0.0, -g
            vx += dt * ax; vy += dt * ay
            xn = x + dt * vx; yn = y + dt * vy
            if yn < 0:
                frac = y / (y - yn)
                xl = x + frac * (xn - x)
                pts.append((X(xl), Yy(0)))
                return pts, xl
            x, y = xn, yn
            pts.append((X(x), Yy(y)))

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Кидок під 45°: опір повітря вкорочує й кособочить параболу",
                  size=16, bold=True))

    # осі й позначки
    f.append(line(L, B, R + 6, B, color=INK, sw=1.8))
    f.append(arrow(L, B, L, T - 8, color=INK, sw=1.8))
    f.append(text(L + 6, T - 12, "висота y, м", size=12, color=MUTED, anchor="start"))
    f.append(text(R, B + 28, "дальність x, м", size=12, color=MUTED, anchor="end"))
    for xv in (50, 100, 150):
        f.append(line(X(xv), B, X(xv), B + 5, color=MUTED, sw=1.3))
        f.append(text(X(xv), B + 18, "%d" % xv, size=10, color=MUTED))
    for yv in (20, 40):
        f.append(line(L - 5, Yy(yv), L, Yy(yv), color=MUTED, sw=1.3))
        f.append(text(L - 10, Yy(yv) + 4, "%d" % yv, size=10, color=MUTED, anchor="end"))

    vac, rv = traj("none")
    qd, rq = traj("quad")
    thin = lambda p: p[::4] + [p[-1]]                # проріджуємо — крива й так гладка
    f.append(polyline(thin(vac), color=MUTED, sw=2.2, dash="6 5"))
    f.append(polyline(thin(qd), color=POS, sw=2.8))

    # позначки приземлення
    f.append(circle(X(rv), Yy(0), 3.5, fill=MUTED, stroke=MUTED, sw=1))
    f.append(circle(X(rq), Yy(0), 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(X(rv), B - 9, "163 м", size=12, color=MUTED))
    f.append(text(X(rq), B - 9, "95 м", size=12, bold=True, color=POS))

    # підписи кривих
    f.append(text(X(112), Yy(39), "порожнеча — симетрична парабола", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(text(X(52), Yy(13), "квадратичний опір — коротше, спуск крутіший", size=13, bold=True, color=POS, anchor="start"))

    return render(os.path.join(IMG, "projectile-drag.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_proportionality(), fig_net_force(), fig_momentum_slope(),
          fig_law_timeline(), fig_aristotle_vs_inertia(),
          fig_rocket_momentum(), fig_impulse_area(),
          fig_terminal_stability(), fig_phase_drift(), fig_projectile_drag()]
    print("written:")
    for p in ps:
        print("  ", p)
