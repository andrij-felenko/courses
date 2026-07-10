# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: пастка двох законів Лехмана й вихід ───────────────────────────
def fig_dilemma():
    W, H = 760, 430
    parts = []

    # Центральна система
    sysb, sw_, sh_ = textbox(W/2, 220, "Жива\nсистема", size=17, bold=True,
                             fill="#eef2ff", stroke=INK, sw=2, min_w=150)
    parts.append(sysb)

    # Закон 1 — мусить мінятися (тисне зверху вниз, стрілка до системи)
    law1, w1, h1 = textbox(180, 90, "Закон 1: мусить мінятися\n(інакше відстане й помре)",
                           size=13, fill="#fdecea", stroke=POS, sw=1.8)
    parts.append(law1)
    parts.append(arrow(180, 90 + h1/2, W/2 - 70, 200, color=POS, sw=2))

    # Закон 2 — структура псується (тисне знизу)
    law2, w2, h2 = textbox(180, 350, "Закон 2: кожна зміна псує\nструктуру (безлад росте сам)",
                           size=13, fill="#fdecea", stroke=POS, sw=1.8)
    parts.append(law2)
    parts.append(arrow(180, 350 - h2/2, W/2 - 70, 245, color=POS, sw=2))

    # Вихід праворуч — керована зміна
    out, wo, ho = textbox(600, 220, "Вихід: мінятися,\nАЛЕ керовано —\nтримати структуру\nпридатною до зміни",
                          size=13, fill="#eafaf1", stroke=FIELD, sw=2)
    parts.append(out)
    parts.append(arrow(W/2 + 78, 220, 600 - wo/2, 220, color=FIELD, sw=2.2))

    render(os.path.join(IMG, "dilemma.svg"), W, H, *parts,
           title="Два закони затискають систему — вихід один")


# ── Фігура 2: двоє воріт керованої зміни ────────────────────────────────────
def fig_gates():
    W, H = 820, 340
    parts = []
    ymid = 200

    # Вхід: зміна
    chg, wc, hc = textbox(90, ymid, "Зміна", size=16, bold=True,
                          fill="#f4f6f8", stroke=INK, sw=2, min_w=110)
    parts.append(chg)

    # Ворота 1: зворотність
    g1x = 320
    parts.append(rect(g1x - 85, ymid - 70, 170, 140, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(mtext(g1x, ymid - 22, ["Ворота 1", "Зворотність"], size=14, bold=True, color=NEG))
    parts.append(mtext(g1x, ymid + 24, ["помилку легко", "відкотити"], size=12, color=INK))
    parts.append(arrow(90 + wc/2, ymid, g1x - 88, ymid, color=INK, sw=2))

    # Ворота 2: фітнес-функція
    g2x = 560
    parts.append(rect(g2x - 90, ymid - 70, 180, 140, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(mtext(g2x, ymid - 22, ["Ворота 2", "Фітнес-функція"], size=14, bold=True, color=NEG))
    parts.append(mtext(g2x, ymid + 24, ["порушення важливого", "не проходить"], size=12, color=INK))
    parts.append(arrow(g1x + 88, ymid, g2x - 93, ymid, color=INK, sw=2))

    # Вихід: здорова система
    okx = 760
    okb, wok, hok = textbox(okx, ymid, "Структура\nтримає форму", size=13, bold=True,
                            fill="#eafaf1", stroke=FIELD, sw=2)
    parts.append(okb)
    parts.append(arrow(g2x + 93, ymid, okx - wok/2, ymid, color=FIELD, sw=2))

    render(os.path.join(IMG, "gates.svg"), W, H, *parts,
           title="Керована зміна проходить крізь двоє воріт")


# ── Фігура 3: ерозія проти напрямної еволюції в часі ────────────────────────
def fig_trajectories():
    W, H = 760, 420
    parts = []
    # осі
    ox, oy = 90, 340        # початок координат
    ax_w, ax_h = 600, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # час →
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # придатність до зміни ↑
    parts.append(text(ox + ax_w, oy + 26, "час, потік змін", size=13, color=MUTED, anchor="end"))
    parts.append(mtext(ox - 14, oy - ax_h + 6, ["легкість", "зміни"], size=13,
                       color=MUTED, anchor="end"))

    x0, y0 = ox + 10, oy - ax_h + 40   # спільний старт угорі
    parts.append(circle(x0, y0, 5, fill=INK, stroke=INK))
    parts.append(text(x0 + 6, y0 - 12, "спільний старт", size=12, color=MUTED, anchor="start"))

    xe = ox + ax_w - 20

    # Ерозія: спадна крива (структура гниє, зміна дорожчає)
    ey = oy - 30
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.6"/>' % (x0, y0, (x0+xe)/2, y0 + 150, xe, ey, POS))
    parts.append(text(xe - 6, ey + 22, "ерозія: гниє некеровано", size=13, color=POS, anchor="end"))

    # Напрямна еволюція: тримається майже рівно
    gy = oy - ax_h + 60
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.6"/>' % (x0, y0, (x0+xe)/2, y0 - 26, xe, gy, FIELD))
    parts.append(text(xe - 6, gy - 12, "напрямна еволюція: тримає форму",
                      size=13, color=FIELD, anchor="end"))

    render(os.path.join(IMG, "trajectories.svg"), W, H, *parts,
           title="Одна система з роками: гнити чи еволюціонувати")


# ── Фігура 4 (детальна): радіус зміни визначає зчеплення ─────────────────────
def fig_change_radius():
    W, H = 880, 470
    p = []

    # --- Ліва панель: тісне зчеплення (зміна розтікається на всіх) ---
    p.append(text(230, 116, "Тісне зчеплення", size=16, bold=True))
    Le = (230, 274)
    ring = [(230, 176), (150, 238), (184, 338), (280, 338), (312, 238)]
    for (x, y) in ring:
        p.append(line(Le[0], Le[1], x, y, color=POS, sw=1.6))
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        p.append(line(a[0], a[1], b[0], b[1], color=POS, sw=1.3))
    for (x, y) in ring:
        p.append(circle(x, y, 20, fill="#fdecea", stroke=POS, sw=2))
    p.append(circle(Le[0], Le[1], 24, fill="#f4b3aa", stroke=POS, sw=2.6))

    # --- Права панель: слабке зчеплення за швом (зміна стоїть у межах кванта) ---
    p.append(text(600, 116, "Слабке зчеплення за швом", size=16, bold=True))
    p.append(text(580, 176, "межа кванта", size=12, color=NEG))
    p.append(rect(498, 186, 168, 176, fill="#ffffff", stroke=NEG, sw=2, rx=16))
    Re = (600, 274)
    inner = [(540, 216), (540, 332)]
    for (x, y) in inner:
        p.append(line(Re[0], Re[1], x, y, color=POS, sw=1.6))
    p.append(line(inner[0][0], inner[0][1], inner[1][0], inner[1][1], color=POS, sw=1.3))
    for (x, y) in inner:
        p.append(circle(x, y, 20, fill="#fdecea", stroke=POS, sw=2))
    p.append(circle(Re[0], Re[1], 24, fill="#f4b3aa", stroke=POS, sw=2.6))

    seam, sw_, sh_ = textbox(704, 274, "шов", size=13, fill="#eef2ff",
                             stroke=NEG, sw=2, min_w=50)
    p.append(line(666, 274, 704 - sw_ / 2, 274, color=INK, sw=1.6))
    p.append(seam)
    outer = [(802, 208), (808, 274), (802, 340)]
    for (x, y) in outer:
        p.append(line(704 + sw_ / 2, 274, x, y, color=MUTED, sw=1.4))
    for (x, y) in outer:
        p.append(circle(x, y, 20, fill="#eafaf1", stroke=FIELD, sw=2))

    lg1, _, _ = textbox(292, 438, "зачеплено зміною", size=12,
                        fill="#fdecea", stroke=POS, sw=1.4)
    lg2, _, _ = textbox(600, 438, "лишилось незмінним", size=12,
                        fill="#eafaf1", stroke=FIELD, sw=1.4)
    p.append(lg1)
    p.append(lg2)

    render(os.path.join(IMG, "change-radius.svg"), W, H, *p,
           title="Радіус зміни визначає зчеплення")


# ── Фігура 5 (детальна): п'ять вимірів фітнес-функції ───────────────────────
def fig_fitness_dimensions():
    W, H = 880, 470
    p = []
    rows = [
        ("Обсяг",     [("атомарна", 432), ("цілісна", 690)]),
        ("Ритм",      [("за подією", 360), ("постійна", 540), ("часова", 706)]),
        ("Результат", [("статичний", 434), ("динамічний", 700)]),
        ("Виклик",    [("автоматична", 442), ("ручна", 692)]),
        ("Намір",     [("закладена", 432), ("проявлена", 692)]),
    ]
    ys = [98, 170, 242, 314, 386]
    for (name, poles), y in zip(rows, ys):
        p.append(text(40, y + 5, name, size=15, bold=True, anchor="start"))
        boxes = []
        for (label, cx) in poles:
            b, w, h = textbox(cx, y, label, size=13, pad=9)
            boxes.append((b, cx, w))
        for i in range(len(poles) - 1):
            _, cxL, wL = boxes[i]
            _, cxR, wR = boxes[i + 1]
            p.append(line(cxL + wL / 2, y, cxR - wR / 2, y,
                          color=MUTED, sw=1.4, dash="4 3"))
        for (b, cx, w) in boxes:
            p.append(b)
    render(os.path.join(IMG, "fitness-dimensions.svg"), W, H, *p,
           title="П'ять вимірів фітнес-функції")


# ── Фігура 6 (детальна): коли еволюційність окупається ──────────────────────
def fig_breakeven():
    W, H = 800, 470
    p = []
    ox, oy = 92, 384
    axw, axh = 624, 302
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw, oy + 26, "кількість змін у часі →",
                  size=13, color=MUTED, anchor="end"))
    p.append(mtext(ox - 12, oy - axh + 8, ["сукупна", "вартість"],
                   size=13, color=MUTED, anchor="end"))

    # ерозія: старт з нуля, надлінійний ріст
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.8"/>' % (100, 380, 452, 372, 690, 112, POS))
    p.append(text(300, 150, "без дисципліни", size=13, color=POS, anchor="start"))

    # з дисципліною: старт із вкладення I, майже лінійно
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.8"/>' % (100, 320, 452, 272, 690, 232, FIELD))
    p.append(text(300, 236, "з дисципліною", size=13, color=FIELD, anchor="start"))

    # початкове вкладення I
    p.append(line(100, 380, 100, 320, color=FIELD, sw=3))
    p.append(text(110, 356, "I", size=14, color=FIELD, bold=True, anchor="start"))

    # точка окупності
    bx, by = 508, 261
    p.append(line(bx, by, bx, oy, color=MUTED, sw=1.4, dash="5 4"))
    p.append(circle(bx, by, 4, fill=INK, stroke=INK))
    p.append(text(bx + 8, 302, "n* — окупність", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "breakeven.svg"), W, H, *p,
           title="Коли еволюційність окупається")


# ── Фігура 7 (math): чому ерозія квадратична — сума трикутника ────────────────
def fig_erosion_triangle():
    W, H = 820, 470
    p = []
    ox, oy = 96, 384
    axw, axh = 640, 300
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))            # час/номер зміни →
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))            # гранична вартість ↑
    p.append(text(ox + axw, oy + 26, "номер зміни k →", size=13, color=MUTED, anchor="end"))
    p.append(mtext(ox - 12, oy - axh + 12, ["гранична", "вартість m(k)"], size=13,
                   color=MUTED, anchor="end"))

    n = 8
    a_px = 44
    eps_px = 26          # приріст граничної вартості на кожну зміну
    bw = 54
    step = 74
    x0 = ox + 26
    a_level = oy - a_px
    for k in range(1, n + 1):
        cx = x0 + (k - 1) * step
        h = a_px + eps_px * (k - 1)
        p.append(rect(cx, a_level, bw, a_px, fill="#eaf0fd", stroke=NEG, sw=1.4))     # основа a
        if k > 1:
            p.append(rect(cx, oy - h, bw, h - a_px, fill="#fdecea", stroke=POS, sw=1.4))  # надбавка ерозії
        p.append(text(cx + bw / 2, oy + 16, str(k), size=12, color=MUTED))
    p.append(line(ox, a_level, x0 + (n - 1) * step + bw, a_level, color=NEG, sw=1.2, dash="5 4"))
    p.append(text(ox - 8, a_level + 4, "a", size=14, color=NEG, bold=True, anchor="end"))

    lg1, _, _ = textbox(250, 442, "основа a на кожну зміну  →  a·n", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.4)
    lg2, _, _ = textbox(566, 442, "надбавка ерозії (трикутник)  →  b·n²", size=12,
                        fill="#fdecea", stroke=POS, sw=1.4)
    p.append(lg1)
    p.append(lg2)
    render(os.path.join(IMG, "erosion-triangle.svg"), W, H, *p,
           title="Чому ерозія квадратична: сума трикутника")


# ── Фігура 8 (math): цінність опціону росте з невизначеністю ─────────────────
def fig_option_value():
    W, H = 860, 470
    p = []
    base = 402
    scale = 2.1

    def panel(x0, sub, sub2, Emax, opt):
        pp = []
        pp.append(mtext(x0 + 150, 66, [sub, sub2], size=13, bold=True, color=INK))
        pp.append(line(x0 + 40, base, x0 + 300, base, color=INK, sw=1.6))
        h_now = 70 * scale
        # бар «вирішити зараз» = max E
        bx1 = x0 + 90
        pp.append(rect(bx1 - 34, base - h_now, 68, h_now, fill="#eef2ff", stroke=NEG, sw=1.6))
        pp.append(text(bx1, base - h_now - 12, "max E = 70", size=12, color=NEG, bold=True))
        pp.append(text(bx1, base + 20, "вирішити", size=12, color=MUTED))
        pp.append(text(bx1, base + 36, "зараз", size=12, color=MUTED))
        # бар «зачекати» = E[max] = нижня частина + опціон
        bx2 = x0 + 230
        h_wait = Emax * scale
        pp.append(rect(bx2 - 34, base - h_now, 68, h_now, fill="#eef2ff", stroke=NEG, sw=1.6))
        pp.append(rect(bx2 - 34, base - h_wait, 68, h_wait - h_now, fill="#eafaf1", stroke=FIELD, sw=1.8))
        pp.append(text(bx2, base - h_wait - 12, "E[max] = %d" % Emax, size=12, color=FIELD, bold=True))
        pp.append(text(bx2, base + 20, "зачекати", size=12, color=MUTED))
        pp.append(text(bx2, base + 36, "й вибрати", size=12, color=MUTED))
        capmid = base - (h_wait + h_now) / 2
        pp.append(text(bx2 + 44, capmid - 4, "опціон", size=12, color=FIELD, bold=True, anchor="start"))
        pp.append(text(bx2 + 44, capmid + 12, "= %d" % opt, size=12, color=FIELD, bold=True, anchor="start"))
        return pp

    p += panel(20, "мала невизначеність", "(розкид виходів 60)", 100, 30)
    p += panel(450, "велика невизначеність", "(розкид виходів 120)", 130, 60)
    p.append(line(438, 60, 438, 430, color=MUTED, sw=1.2, dash="4 4"))
    render(os.path.join(IMG, "option-value.svg"), W, H, *p,
           title="Цінність опціону росте з невизначеністю")


# ── Фігура 9 (math): останній відповідальний момент — точка перетину ─────────
def fig_lrm_boundary():
    W, H = 820, 440
    p = []
    ox, oy = 92, 356
    axw, axh = 636, 286
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw, oy + 26, "як довго відкладаємо →", size=13, color=MUTED, anchor="end"))
    p.append(mtext(ox - 12, oy - axh + 12, ["цінність /", "вартість"], size=13,
                   color=MUTED, anchor="end"))

    x0 = ox + 8
    xe = ox + axw - 16
    ctl = oy - 120
    # цінність очікування (зелена, спадає — невизначеність тане)
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (x0, oy - axh + 40, (x0 + xe) / 2, ctl, xe, oy - 26, FIELD))
    # вартість зволікання (червона, росте)
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (x0, oy - 26, (x0 + xe) / 2, ctl, xe, oy - axh + 40, POS))

    bx = (x0 + xe) / 2
    by = ((oy - axh + 40) + 2 * ctl + (oy - 26)) / 4     # реальна точка перетину при t=0.5
    p.append(line(bx, by, bx, oy, color=MUTED, sw=1.4, dash="5 4"))
    p.append(circle(bx, by, 5, fill=INK, stroke=INK))

    p.append(text(x0 + 12, oy - axh + 30, "цінність очікування (спадає)", size=13, color=FIELD, anchor="start"))
    p.append(text(xe - 8, oy - axh + 30, "вартість зволікання (росте)", size=13, color=POS, anchor="end"))
    p.append(mtext(bx, oy + 24, ["останній", "відповідальний момент"], size=13, bold=True, color=INK))
    p.append(text(x0 + 96, oy - 40, "тримати опціон відкритим", size=12, color=MUTED))
    p.append(text(xe - 74, oy - 40, "запізно — час вирішувати", size=12, color=MUTED))
    render(os.path.join(IMG, "lrm-boundary.svg"), W, H, *p,
           title="Останній відповідальний момент — точка перетину")


if __name__ == "__main__":
    fig_dilemma()
    fig_gates()
    fig_trajectories()
    fig_change_radius()
    fig_fitness_dimensions()
    fig_breakeven()
    fig_erosion_triangle()
    fig_option_value()
    fig_lrm_boundary()
    print("figs written to", IMG)
