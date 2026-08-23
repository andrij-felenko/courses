# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RED_TINT = "#fdecea"
BLUE_TINT = "#eaf0fd"
GREEN_TINT = "#eaf7ef"
CODE_FILL = "#eef2f7"


# ── Figure 1: закон Літтла як труба ──────────────────────────────────────────
def fig_littles_law():
    W, H = 860, 340
    p = []
    # система — велика рамка
    p.append(rect(200, 95, 460, 140, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(430, 84, "система — запити «у польоті»", size=14, bold=True))
    # напис про W усередині, над колами
    p.append(text(430, 122, "кожен проводить усередині W = 0.05 с", size=12.5, color=MUTED))
    # кола — одиниці в системі (L)
    cx = 245
    while cx <= 615:
        p.append(circle(cx, 165, 13, fill=FIELD, stroke=FIELD, sw=1))
        cx += 46
    p.append(text(430, 216, "L ≈ 10 одночасно в системі", size=13, bold=True, color=INK))
    # потік усередину
    p.append(arrow(70, 165, 198, 165, color=LINE, sw=2.0))
    p.append(text(134, 149, "надходять", size=12.5, color=INK))
    p.append(text(134, 189, "λ = 200/с", size=12.5, color=MUTED))
    # потік назовні
    p.append(arrow(662, 165, 800, 165, color=LINE, sw=2.0))
    p.append(text(731, 149, "виходять", size=12.5, color=INK))
    p.append(text(731, 189, "λ = 200/с", size=12.5, color=MUTED))
    # тотожність
    b, _, _ = textbox(430, 294, "L = λ · W = 200 · 0.05 = 10", size=15, bold=True,
                      fill=GREEN_TINT, stroke=FIELD, color=INK)
    p.append(b)
    render(os.path.join(OUT, 'littles-law.svg'), W, H, *p,
           title="Закон Літтла: скільки «в польоті» = темп · час усередині")


# ── Figure 2: коліно завантаження (час у системі проти ρ) ────────────────────
def fig_utilization_knee():
    W, H = 800, 400
    p = []
    x0, x1 = 95, 700          # ρ = 0 .. 1
    ybot, ytop = 330, 75      # W = 1 .. Wcap
    Wcap = 20.0

    def xr(rho):
        return x0 + rho * (x1 - x0)

    def yw(w):
        w = min(w, Wcap)
        return ybot - (w - 1) / (Wcap - 1) * (ybot - ytop)

    # осі
    p.append(line(x0, ybot, x1 + 20, ybot, color=LINE, sw=1.5))
    p.append(line(x0, ybot, x0, ytop - 10, color=LINE, sw=1.5))
    p.append(text(x0 + (x1 - x0) / 2, 372, "завантаження ρ  (наскільки ресурс зайнятий)",
                  size=13, color=MUTED))
    p.append(text(58, 200, "час", size=12, color=MUTED))
    p.append(text(58, 218, "у системі", size=12, color=MUTED))
    # позначки осі x
    for rho, lab in [(0.0, "0"), (0.5, "50%"), (0.9, "90%"), (1.0, "100%")]:
        p.append(text(xr(rho), 350, lab, size=12, color=MUTED))

    # крива W = 1/(1-ρ)
    pts = []
    rho = 0.0
    while rho <= 0.955:
        pts.append((xr(rho), yw(1.0 / (1.0 - rho))))
        rho += 0.005
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=POS, sw=2.6))

    # вертикальні орієнтири
    p.append(line(xr(0.5), ybot, xr(0.5), yw(2), color=MUTED, sw=1.2, dash="4 4"))
    p.append(line(xr(0.9), ybot, xr(0.9), yw(10), color=MUTED, sw=1.2, dash="4 4"))
    # мітки множників у порожньому лівому-верхньому куті / біля точок
    p.append(circle(xr(0.5), yw(2), 4, fill=INK, stroke=INK))
    p.append(text(xr(0.5), yw(2) - 12, "×2", size=12.5, bold=True, color=INK))
    p.append(circle(xr(0.9), yw(10), 4, fill=INK, stroke=INK))
    p.append(text(xr(0.9) - 20, yw(10), "×10", size=12.5, bold=True, color=INK, anchor="end"))
    p.append(text(xr(0.955) + 6, yw(20) + 4, "вибух", size=13, bold=True, color=POS, anchor="start"))
    # коліно
    p.append(mtext(200, 130, ["до коліна — рівно;", "за коліном черга й"
                              , "чекання злітають угору"], size=13, color=INK))
    render(os.path.join(OUT, 'utilization-knee.svg'), W, H, *p,
           title="Що ближче до 100%, то різкіше злітає чекання")


# ── Figure 3: середнє бреше — дивись у хвіст ──────────────────────────────────
def fig_latency_tail():
    W, H = 820, 380
    p = []
    heights = [6, 22, 48, 70, 76, 66, 50, 37, 27, 20, 15, 11, 9, 7, 6, 5, 4, 4, 3, 3]
    x0 = 90
    bw, gap = 30, 2
    step = bw + gap
    ybase = 315
    scale = 3.0
    for i, h in enumerate(heights):
        bx = x0 + i * step
        p.append(rect(bx, ybase - h * scale, bw, h * scale,
                      fill=BLUE_TINT, stroke=NEG, sw=1.0, rx=2))
    # вісь
    p.append(line(x0 - 6, ybase, x0 + len(heights) * step + 6, ybase, color=LINE, sw=1.5))
    p.append(text(x0 + len(heights) * step / 2, 350, "затримка одного запиту →",
                  size=13, color=MUTED))

    def mark(idx, label, color, laby):
        mx = x0 + idx * step + bw / 2
        p.append(line(mx, 70, mx, ybase, color=color, sw=1.8, dash="5 4"))
        p.append(text(mx, laby, label, size=12.5, bold=True, color=color))

    # медіана й середнє близько — рознесемо підписи по висоті
    mark(4, "p50 (медіана)", FIELD, 64)
    mark(6, "середнє", MUTED, 90)
    mark(16, "p99", POS, 64)
    mark(19, "p99.9", POS, 90)
    p.append(mtext(470, 148, ["тут — рідкісний, але", "болючий повільний хвіст:",
                              "затори, замки, паузи GC"], size=12.5, color=INK))
    render(os.path.join(OUT, 'latency-tail.svg'), W, H, *p,
           title="Середнє сидить біля горба — біль живе у хвості")


# ── Figure 4: узгоджений пропуск (coordinated omission) ──────────────────────
def fig_coordinated_omission():
    W, H = 900, 350
    p = []
    axis_y = 210
    xa, xb = 80, 820
    p.append(line(xa, axis_y, xb, axis_y, color=LINE, sw=1.5))
    p.append(arrow(xb - 4, axis_y, xb + 10, axis_y, color=LINE, sw=1.5))
    p.append(text(xb + 6, axis_y + 20, "час", size=12, color=MUTED, anchor="end"))

    ticks = [110, 170, 230, 290, 350, 410, 470, 530, 590, 650, 710]
    stall_from, stall_to = 290, 530

    # смуга затику
    p.append(rect(stall_from, 95, stall_to - stall_from, 90, fill=RED_TINT, stroke=POS, sw=1.6))
    p.append(text((stall_from + stall_to) / 2, 118, "СИСТЕМА ЗАВМЕРЛА", size=13.5, bold=True, color=POS))
    # заголовок над смугою — пропущені проби
    p.append(text((stall_from + stall_to) / 2, 78,
                  "5 проб, які цикл НЕ надіслав (він заблокований)", size=12.5, color=INK))
    # хрестики пропущених проб усередині смуги
    for tx in [290, 350, 410, 470, 530]:
        p.append(text(tx, 160, "×", size=20, bold=True, color=POS))

    # зелені вчасні проби до і після
    for tx in [110, 170, 230, 590, 650, 710]:
        p.append(line(tx, axis_y - 9, tx, axis_y + 9, color=FIELD, sw=2.4))
    p.append(text(170, axis_y + 30, "надіслано вчасно → швидкі", size=12, color=FIELD))
    p.append(text(650, axis_y + 30, "знову вчасно → швидкі", size=12, color=FIELD))

    # єдиний повільний запит, що потрапив у вибірку
    p.append(arrow(stall_from, 196, stall_to, 196, color=INK, sw=2.0))
    p.append(text((stall_from + stall_to) / 2, 246,
                  "єдиний повільний запит у вибірці (60 мс)", size=12, color=INK))

    # висновок
    b, _, _ = textbox(450, 305,
                      "у вибірці 1 повільна подія замість 6 → наївний p99 «здоровий», поки люди чекають",
                      size=12.5, bold=False, fill=GREEN_TINT, stroke=FIELD, color=INK)
    p.append(b)
    render(os.path.join(OUT, 'coordinated-omission.svg'), W, H, *p,
           title="Узгоджений пропуск: наївний вимір ховає повільний хвіст")


# ── Figure 5 (вставка math): ланцюг M/M/1 — стани й баланс ────────────────────
def _carrow(x1, y1, x2, y2, bend, color=LINE, sw=1.8):
    """Дугова стрілка через квадратичну криву; bend<0 — вигин угору."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bend
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x1, y1, mx, my, x2, y2, color, sw))


def fig_mm1_chain():
    W, H = 900, 350
    p = []
    cy, r = 178, 26
    xs = [78, 226, 374, 522, 670]        # стани 0..4
    labels = ["0", "1", "2", "3", "4"]
    xdots = 818                          # «…»
    centers = xs + [xdots]

    # дуги переходів між сусідніми вузлами (усі темпи однакові — підписуємо раз)
    for i in range(len(centers) - 1):
        a, b = centers[i], centers[i + 1]
        # надходження λ (угору, праворуч)
        p.append(_carrow(a + r, cy - 9, b - r, cy - 9, -48, color=POS, sw=2.0))
        # обслуговування μ (донизу, ліворуч)
        p.append(_carrow(b - r, cy + 9, a + r, cy + 9, 48, color=NEG, sw=2.0))
        if i == 0:
            p.append(text((a + b) / 2, cy - 64, "λ  (надходження)", size=14,
                          bold=True, color=POS))
            p.append(text((a + b) / 2, cy + 80, "μ  (обслуговування)", size=14,
                          bold=True, color=NEG))

    # вузли-стани
    for x, lab in zip(xs, labels):
        p.append(circle(x, cy, r, fill=FILL, stroke=LINE, sw=1.8))
        p.append(text(x, cy + 6, lab, size=17, bold=True, color=INK))
    p.append(text(xdots, cy + 6, "…", size=22, bold=True, color=MUTED))

    # розріз між станами 2 і 3
    xcut = (xs[2] + xs[3]) / 2
    p.append(line(xcut, cy - 96, xcut, cy + 96, color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(xcut, cy - 104, "розріз", size=12, color=MUTED))

    # баланс через будь-який розріз
    b, _, _ = textbox(W / 2, 322,
                      "потік праворуч = потік ліворуч:   λ·πₙ = μ·πₙ₊₁   ⟹   πₙ₊₁ = ρ·πₙ",
                      size=13.5, bold=True, fill=GREEN_TINT, stroke=FIELD, color=INK)
    p.append(b)
    render(os.path.join(OUT, 'mm1-chain.svg'), W, H, *p,
           title="M/M/1: стан = кількість у системі;  ρ = λ/μ")


# ── Figure 6 (вставка math): мінливість підіймає множник, стіна спільна ───────
def fig_variability_curves():
    W, H = 820, 420
    p = []
    x0, x1 = 100, 690
    ybot, ytop = 350, 80
    cap = 12.0

    def xr(rho):
        return x0 + rho * (x1 - x0)

    def yw(v):
        v = min(v, cap)
        return ybot - v / cap * (ybot - ytop)

    # осі
    p.append(line(x0, ybot, x1 + 40, ybot, color=LINE, sw=1.5))
    p.append(line(x0, ybot, x0, ytop - 10, color=LINE, sw=1.5))
    p.append(text(x0 + (x1 - x0) / 2, 392, "завантаження ρ = λ/μ", size=13, color=MUTED))
    p.append(text(60, 205, "час", size=12, color=MUTED))
    p.append(text(60, 223, "× t_обсл", size=12, color=MUTED))
    for rho, lab in [(0.0, "0"), (0.5, "50%"), (0.9, "90%"), (1.0, "100%")]:
        p.append(text(xr(rho), 370, lab, size=12, color=MUTED))

    def curve(f, color, rho_max=0.98):
        pts, rho = [], 0.0
        while rho <= rho_max:
            v = f(rho)
            if v >= cap:
                pts.append((xr(rho), yw(cap)))
                break
            pts.append((xr(rho), yw(v)))
            rho += 0.004
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=color, sw=2.6))

    # M/M/1: 1/(1-ρ);  M/D/1: 1 + ½·ρ/(1-ρ);  D/D/1: рівно 1, тоді стіна
    curve(lambda r: 1.0 / (1.0 - r), POS)
    curve(lambda r: 1.0 + 0.5 * r / (1.0 - r), NEG)
    # D/D/1 — годинниковий потік: черги нема зовсім, пласко аж до самої стіни
    p.append(line(xr(0.0), yw(1), xr(0.99), yw(1), color=MUTED, sw=2.6))

    # стіна ρ→1
    p.append(line(xr(1.0), ybot, xr(1.0), ytop, color=INK, sw=1.4, dash="4 5"))
    p.append(mtext(xr(1.0) + 8, ytop + 30, ["стіна", "ρ→1"], size=12.5, bold=True,
                   color=INK, anchor="start"))

    # легенда у вільному верхньому-лівому куті
    lx, ly = 150, 110
    p.append(line(lx, ly, lx + 26, ly, color=POS, sw=2.6))
    p.append(text(lx + 34, ly + 4, "M/M/1  (c_a=c_s=1) → множник 1", size=12.5,
                  color=INK, anchor="start"))
    p.append(line(lx, ly + 24, lx + 26, ly + 24, color=NEG, sw=2.6))
    p.append(text(lx + 34, ly + 28, "M/D/1  (c_s=0) → множник ½", size=12.5,
                  color=INK, anchor="start"))
    p.append(line(lx, ly + 48, lx + 26, ly + 48, color=MUTED, sw=2.6))
    p.append(text(lx + 34, ly + 52, "D/D/1  (годинник) → черги нема", size=12.5,
                  color=INK, anchor="start"))

    render(os.path.join(OUT, 'variability-curves.svg'), W, H, *p,
           title="Мінливість задає множник; стіну 1/(1−ρ) не зсунути")


# ── Figure 7 (вставка hist): віхи народження теорії черг ──────────────────────
def fig_queueing_timeline():
    W, H = 960, 390
    p = []
    # вісь часу
    p.append(arrow(110, 150, 860, 150, color=LINE, sw=1.6))
    p.append(text(858, 142, "час", size=12, color=MUTED, anchor="end"))
    nodes = [
        (190, "1909", "Аґнер Краруп Ерланг",
         ["Копенгаген, телефонія:", "дзвінки — випадковий процес"]),
        (480, "1953", "Девід Кендалл",
         ["нотація  A / S / c —", "спільна мова всякої черги"]),
        (770, "1961", "Джон Літтл",
         ["перший загальний доказ", "L = λ · W"]),
    ]
    for cx, year, name, lines in nodes:
        p.append(text(cx, 120, year, size=20, bold=True, color=INK))
        p.append(circle(cx, 150, 7, fill=INK, stroke=INK))
        p.append(line(cx, 157, cx, 202, color=MUTED, sw=1.0, dash="3 3"))
        p.append(rect(cx - 125, 202, 250, 82, fill=FILL, stroke=LINE, sw=1.4))
        p.append(text(cx, 228, name, size=14, bold=True, color=INK))
        p.append(mtext(cx, 250, lines, size=12.5, color=MUTED, lh=1.25))
    b, _, _ = textbox(480, 330,
                      ["телефонний «ерланг»:  A = λ · h",
                       "— та сама L = λ·W, за півстоліття до серверів"],
                      size=13, fill=GREEN_TINT, stroke=FIELD, color=INK)
    p.append(b)
    render(os.path.join(OUT, 'queueing-timeline.svg'), W, H, *p,
           title="Прилад конкурентності виріс із телефонії")


# ── Figure 8 (вставка proj): конвеєр DH під приладами конкурентності ──────────
def fig_pipeline_sensors():
    W, H = 1000, 415
    p = []
    cy = 190
    bh = 62
    boxtop, boxbot = cy - bh / 2, cy + bh / 2

    # пайплайн: край → ворота → черга → пул → пристрої
    eb, ew, _ = textbox(90, cy, "край\nλ надходять", size=13, bold=True,
                        fill=BLUE_TINT, stroke=NEG, min_w=112)
    p.append(eb)
    gb, gw, _ = textbox(250, cy, "ворота\nпротитиск", size=13, bold=True,
                        fill=RED_TINT, stroke=POS, min_w=120)
    p.append(gb)

    ch_cx, ch_w = 470, 200
    p.append(rect(ch_cx - ch_w / 2, boxtop, ch_w, bh, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(ch_cx, boxtop - 9, "черга (буфер-канал)", size=12.5, bold=True))
    nslot, filled = 8, 5
    sc, gap = 18, 4
    total = nslot * sc + (nslot - 1) * gap
    sx = ch_cx - total / 2
    for i in range(nslot):
        on = i < filled
        p.append(rect(sx + i * (sc + gap), cy - 9, sc, 20,
                      fill=(GREEN_TINT if on else BG), stroke=(FIELD if on else MUTED),
                      sw=1.2, rx=2))

    pool_cx, pool_w = 700, 170
    p.append(rect(pool_cx - pool_w / 2, boxtop, pool_w, bh, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(pool_cx, boxtop - 9, "пул робітників", size=12.5, bold=True))
    wn, busy = 6, 4
    for i in range(wn):
        on = i < busy
        p.append(circle(pool_cx - 55 + i * 22, cy, 8,
                        fill=(GREEN_TINT if on else BG), stroke=(FIELD if on else MUTED), sw=1.5))

    db, dw, _ = textbox(905, cy, "пристрої\nвихід λ", size=13, bold=True,
                        fill=FILL, stroke=LINE, min_w=112)
    p.append(db)

    # стрілки потоку
    p.append(arrow(90 + ew / 2, cy, 250 - gw / 2, cy, sw=2.0))
    p.append(arrow(250 + gw / 2, cy, ch_cx - ch_w / 2, cy, sw=2.0))
    p.append(arrow(ch_cx + ch_w / 2, cy, pool_cx - pool_w / 2, cy, sw=2.0))
    p.append(arrow(pool_cx + pool_w / 2, cy, 905 - dw / 2, cy, sw=2.0))

    # дужка W над трубою: від enqueue до виходу
    bx0, bx1, by = ch_cx - ch_w / 2, 905, 120
    p.append(line(bx0, by, bx1, by, color=INK, sw=1.6))
    p.append(line(bx0, by, bx0, by + 20, color=INK, sw=1.6))
    p.append(line(bx1, by, bx1, by + 20, color=INK, sw=1.6))
    p.append(text((bx0 + bx1) / 2, by - 8,
                  "W — час у системі: черга + обслуга, від enqueue до виходу", size=12.5, bold=True))

    # прилади під вузлами
    cy2 = 332
    def sensor(cx, node_x, s, stroke=LINE, fill=FILL):
        p.append(line(node_x, boxbot, cx, cy2 - 26, color=MUTED, sw=1.1, dash="4 4"))
        b, _, _ = textbox(cx, cy2, s, size=12, fill=fill, stroke=stroke)
        p.append(b)

    sensor(250, 250, "протитиск\nвідмовляй / гальмуй", stroke=POS, fill=RED_TINT)
    sensor(460, 470, "глибина черги\nlen(канал)", stroke=FIELD, fill=GREEN_TINT)
    sensor(662, 700, "насиченість пулу\nзайнято / усього", stroke=LINE)
    sensor(880, 700, "рантайм-лаг\n/sched · /sync/mutex", stroke=NEG, fill=BLUE_TINT)

    # алерт-петля: черга росте → вмикає протитиск (U-маршрут знизу)
    p.append(line(460, cy2 + 26, 460, 384, color=POS, sw=1.6, dash="5 4"))
    p.append(line(460, 384, 250, 384, color=POS, sw=1.6, dash="5 4"))
    p.append(arrow(250, 384, 250, cy2 + 26, color=POS, sw=1.6))
    p.append(text(355, 402, "алерт: черга росте → вмикає протитиск", size=12, bold=True, color=POS))

    render(os.path.join(OUT, 'pipeline-sensors.svg'), W, H, *p,
           title="Прилади конкурентності сідають на вузли конвеєра DH")


# ── Figure 9 (вставка proj): алерт на РІСТ черги (нахил, не рівень) → протитиск ─
def fig_queue_backpressure():
    W, H = 900, 380
    p = []
    x0, x1 = 80, 830
    ybot, ytop = 300, 70
    dmax = 40.0

    def X(t):
        return x0 + t * (x1 - x0)

    def Y(d):
        return ybot - (d / dmax) * (ybot - ytop)

    # осі
    p.append(line(x0, ybot, x1 + 10, ybot, color=LINE, sw=1.5))
    p.append(line(x0, ybot, x0, ytop - 6, color=LINE, sw=1.5))
    p.append(text((x0 + x1) / 2, ybot + 34, "час →", size=12.5, color=MUTED))
    p.append(mtext(42, (ytop + ybot) / 2 - 8, ["глибина", "черги"], size=12, color=MUTED))

    # поріг за РІВНЕМ — запізнілий орієнтир
    p.append(line(x0, Y(36), x1, Y(36), color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(x1, Y(36) - 8, "поріг за РІВНЕМ — спрацював би пізно", size=11.5,
                  color=MUTED, anchor="end"))

    pts = [(0.00, 3), (0.08, 4), (0.16, 3), (0.24, 5), (0.30, 4),
           (0.36, 9), (0.42, 15), (0.48, 22), (0.54, 29), (0.58, 32),
           (0.63, 30), (0.70, 22), (0.80, 13), (0.90, 8), (1.00, 6)]
    trip_t = 0.58
    for i in range(len(pts) - 1):
        t_a, d_a = pts[i]
        t_b, d_b = pts[i + 1]
        if t_b <= 0.30:
            col = FIELD
        elif t_a >= trip_t:
            col = NEG
        else:
            col = POS
        p.append(line(X(t_a), Y(d_a), X(t_b), Y(d_b), color=col, sw=2.8))

    # лінія спрацювання протитиску + підпис у вільному верхньому полі з поводком
    p.append(line(X(trip_t), ybot, X(trip_t), Y(33), color=POS, sw=1.6, dash="4 4"))
    b, _, _ = textbox(430, 52, "протитиск вмикається", size=12, bold=True,
                      fill=RED_TINT, stroke=POS)
    p.append(b)
    p.append(line(430, 68, X(trip_t), Y(33) - 2, color=POS, sw=1.0, dash="3 3"))

    # підписи фаз
    p.append(text(X(0.14), 284, "нахил ≈ 0 · спокій", size=12, color=FIELD))
    p.append(text(X(0.31), 286, "нахил > 0 тримається → тривога", size=12,
                  bold=True, color=POS, anchor="start"))
    p.append(text(X(0.86), 175, "джерело гальмує → черга спадає", size=12,
                  color=NEG, anchor="middle"))

    render(os.path.join(OUT, 'queue-backpressure.svg'), W, H, *p,
           title="Стеж за НАХИЛОМ черги, не за рівнем")


if __name__ == '__main__':
    fig_littles_law()
    fig_utilization_knee()
    fig_latency_tail()
    fig_coordinated_omission()
    fig_mm1_chain()
    fig_variability_curves()
    fig_queueing_timeline()
    fig_pipeline_sensors()
    fig_queue_backpressure()
    print("ok")
