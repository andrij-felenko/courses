# -*- coding: utf-8 -*-
"""Фігури до теми «Симуляція кіл (SPICE)» (аналогова електроніка).
Фігури:
  pipeline.svg   — нетліст → рівняння вузлів (KCL) → розв'язати матрицю → числа
  newton.svg     — робоча точка як перетин двох кривих; Ньютон підбирає її ітераціями
  transient.svg  — крок за кроком у часі: на кожному кроці своя «робоча точка»
  analyses.svg   — один рушій, чотири режими аналізу (DC / точка / AC / перехідний)
Вставка math-nodal-mna.md:
  mna-stamp.svg  — резистор «штампує» ±G у чотири клітинки матриці за номерами вузлів
  mna-block.svg  — облямована блок-система MNA: джерело напруги додає рядок і невідомий струм
Вставка hist-spice-berkeley.md:
  lineage.svg    — родовід: CANCER → SPICE1/2/3 (Берклі, public domain) → комерційні нащадки
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def pipeline():
    """Шлях від схеми до чисел: нетліст → KCL у вузлах → матриця → розв'язок."""
    W, H = 760, 360
    p = []
    cy = 150
    boxes = [
        (90, "нетліст", "хто з ким\nз'єднаний", FILL, LINE),
        (255, "рівняння\nвузлів", "KCL у кожному\nвузлі", "#eaf0fd", NEG),
        (420, "матриця\nG · v = i", "система\nлінійних рівнянь", "#fdf3e6", "#b8732e"),
        (585, "розв'язок", "напруги\nй струми", "#eafaf0", FIELD),
    ]
    bw, bh = 120, 96
    for i, (cx, title, sub, fc, sc) in enumerate(boxes):
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fc, stroke=sc, sw=2))
        p.append(mtext(cx, cy - 8, title, size=15, bold=True, color=sc))
        p.append(mtext(cx, cy + 26, sub, size=11, color=MUTED))
        if i < len(boxes) - 1:
            nx = boxes[i + 1][0]
            p.append(arrow(cx + bw / 2 + 4, cy, nx - bw / 2 - 4, cy, color=INK, sw=2.2))
    # підпис над стрілкою «повторити для нелінійних»
    p.append(line(255, cy - bh / 2 - 8, 255, 70, color=POS, sw=1.6, dash="4 3"))
    p.append(line(420, 70, 420, cy - bh / 2 - 8, color=POS, sw=1.6, dash="4 3"))
    p.append(line(255, 70, 420, 70, color=POS, sw=1.6, dash="4 3"))
    p.append(arrow(420, 70, 420, cy - bh / 2 - 8, color=POS, sw=1.6))
    p.append(text((255 + 420) / 2, 60, "якщо нелінійно — повторити (Ньютон)", size=12, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 320,
                      "Симулятор не «малює схему» — він перекладає її в систему рівнянь Кірхгофа\n"
                      "і чисельно її розв'язує. Нелінійні елементи змушують повторювати розв'язок.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'pipeline.svg'), W, H, *p,
           title="Як SPICE рахує схему: від нетліста до чисел")


def newton():
    """Робоча точка = перетин двох ВАХ; Ньютон підходить до неї дотичними."""
    W, H = 720, 420
    p = []
    ox, oy = 90, 340          # початок осей
    aw, ah = 540, 280
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))           # вісь U
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))           # вісь I
    p.append(text(ox + aw - 10, oy + 22, "напруга на діоді U", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - ah + 6, "струм I", size=12, color=MUTED, anchor="end"))

    # пряма навантаження: I = (Vdd - U)/R   (спадна)
    def loadline(u):  # u у частках діапазону 0..1
        return 1.0 - 0.85 * u
    # експонента діода: I ∝ (e^(k u) - 1)   (зростна, крута)
    def diode(u):
        return (math.exp(3.4 * u) - 1) / (math.exp(3.4 * 1.0) - 1) * 1.0

    def XX(u):
        return ox + aw * u
    def YY(i):
        return oy - ah * i

    pts_l = [(XX(u / 100.0), YY(loadline(u / 100.0))) for u in range(0, 101)]
    pts_d = [(XX(u / 100.0), YY(diode(u / 100.0))) for u in range(0, 101)]
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in pts_l) +
             '" fill="none" stroke="%s" stroke-width="2.4"/>' % NEG)
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in pts_d) +
             '" fill="none" stroke="%s" stroke-width="2.4"/>' % POS)
    p.append(text(XX(0.16), YY(loadline(0.16)) - 12, "пряма навантаження (резистор)", size=12, color=NEG, anchor="start"))
    p.append(text(XX(0.62), YY(diode(0.62)) + 4, "ВАХ діода (експонента)", size=12, color=POS, anchor="start"))

    # точка перетину (числово знайдемо де loadline≈diode)
    us = 0.0
    best = 1e9
    for k in range(1, 1000):
        u = k / 1000.0
        d = abs(loadline(u) - diode(u))
        if d < best:
            best = d; us = u
    ix, iy = XX(us), YY(loadline(us))
    p.append(circle(ix, iy, 6, fill=FIELD, stroke=INK, sw=2))
    p.append(text(ix + 10, iy - 10, "робоча точка", size=13, bold=True, color=FIELD, anchor="start"))

    # ітерації Ньютона по осі U: початкова здогадка → ближче → у точку
    guesses = [0.20, 0.46, us]
    for j, ug in enumerate(guesses):
        gx = XX(ug)
        p.append(line(gx, oy, gx, oy + 14, color=MUTED, sw=1.4))
        lbl = "u%d" % j if j < 2 else "→ збіг"
        p.append(text(gx, oy + 30, lbl, size=11, color=MUTED if j < 2 else FIELD, bold=(j == 2)))
        if j < len(guesses) - 1:
            p.append(arrow(gx + 4, oy + 9, XX(guesses[j + 1]) - 4, oy + 9, color=INK, sw=1.6))

    b, _, _ = textbox(W / 2, 398,
                      "Робоча точка — там, де крива діода перетинає пряму навантаження. Рівняння нелінійне,\n"
                      "прямої формули немає: Ньютон стартує з здогадки й кількома кроками сходиться у перетин.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'newton.svg'), W, H, *p,
           title="Робоча точка як перетин кривих; Ньютон сходиться до неї")


def transient():
    """Перехідний аналіз: час ділиться на кроки, у кожному — свій розв'язок."""
    W, H = 740, 380
    p = []
    ox, oy = 80, 280
    aw, ah = 600, 210
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    p.append(text(ox + aw - 6, oy + 22, "час t", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - ah + 4, "напруга", size=12, color=MUTED, anchor="end"))

    # справжня крива — заряд RC (1 - e^-t)
    def vc(t):  # t у 0..1
        return 1 - math.exp(-3.2 * t)
    pts = [(ox + aw * (t / 200.0), oy - ah * vc(t / 200.0) * 0.92) for t in range(0, 201)]
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in pts) +
             '" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % MUTED)

    # кроки симулятора — нерівномірні (густіше там, де круто)
    steps = [0.0, 0.06, 0.13, 0.22, 0.34, 0.50, 0.70, 1.0]
    prev = None
    for i, t in enumerate(steps):
        xx = ox + aw * t
        yy = oy - ah * vc(t) * 0.92
        p.append(line(xx, oy, xx, oy + 12, color=MUTED, sw=1.2))
        if prev:
            p.append(line(prev[0], prev[1], xx, yy, color=NEG, sw=2.4))
        p.append(circle(xx, yy, 4.5, fill="#eaf0fd", stroke=NEG, sw=1.8))
        prev = (xx, yy)
    # підписи кроків
    p.append(text(ox + aw * 0.06, oy + 28, "Δt малий", size=11, color=POS))
    p.append(text(ox + aw * 0.06, oy + 42, "(круто)", size=11, color=POS))
    p.append(text(ox + aw * 0.85, oy + 28, "Δt більший", size=11, color=FIELD))
    p.append(text(ox + aw * 0.85, oy + 42, "(полого)", size=11, color=FIELD))
    p.append(text(ox + aw * 0.42, oy - ah * 0.92 - 6, "кожна точка — окремий розв'язок схеми", size=12, bold=True, color=NEG))

    b, _, _ = textbox(W / 2, 356,
                      "Перехідний аналіз кроками йде в часі: на кожному кроці похідні (струм у C, напруга на L)\n"
                      "замінено різницею за крок Δt — і знову розв'язано схему. Крок сам стискається там, де круто.",
                      size=12, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    render(os.path.join(OUT, 'transient.svg'), W, H, *p,
           title="Перехідний аналіз: рух у часі дрібними кроками")


def analyses():
    """Один рушій — чотири питання до схеми."""
    W, H = 720, 360
    p = []
    # центральний блок-рушій
    cx, cy = 360, 140
    p.append(rect(cx - 90, cy - 40, 180, 80, fill="#f4f6f8", stroke=LINE, sw=2.2))
    p.append(mtext(cx, cy - 6, "ядро SPICE", size=15, bold=True))
    p.append(mtext(cx, cy + 18, "KCL + Ньютон", size=11, color=MUTED))

    outs = [
        (120, 60, "робоча точка", ".op", "усі напруги в спокої", FIELD),
        (600, 60, "розгортка DC", ".dc", "вихід від входу", NEG),
        (120, 250, "AC / частотна", ".ac", "підсилення vs частота", "#b8732e"),
        (600, 250, "перехідний", ".tran", "сигнали в часі", POS),
    ]
    for ex, ey, title, cmd, sub, col in outs:
        bw2, bh2 = 150, 70
        p.append(rect(ex - bw2 / 2, ey - bh2 / 2, bw2, bh2, fill=BG, stroke=col, sw=2))
        p.append(text(ex, ey - 8, title, size=13, bold=True, color=col))
        p.append(text(ex, ey + 10, cmd, size=12, color=INK))
        p.append(text(ex, ey + 26, sub, size=10, color=MUTED))
        # стрілка від ядра
        p.append(arrow(cx + (-1 if ex < cx else 1) * 92,
                       cy + (-1 if ey < cy else 1) * 30,
                       ex + (1 if ex < cx else -1) * (bw2 / 2 + 2),
                       ey + (1 if ey < cy else -1) * (bh2 / 2 + 2),
                       color=MUTED, sw=1.8))

    b, _, _ = textbox(W / 2, 330,
                      "Те саме ядро (рівняння Кірхгофа + Ньютон для нелінійностей) відповідає на чотири різні питання:\n"
                      "де схема стоїть у спокої, як реагує на повільну зміну входу, на частоту й на сигнал у часі.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'analyses.svg'), W, H, *p,
           title="Один рушій — чотири режими аналізу")


def lineage():
    """Родовід SPICE: берклівський стовбур (public domain) → комерційні гілки."""
    W, H = 780, 470
    p = []

    # ── Берклівський стовбур: вертикальна колонка академічних версій ──
    tx = 190
    trunk = [
        (70,  "CANCER", "1969-71 · Рорер, Нейгел", "клас-проєкт, без радіації", "#f4f6f8", MUTED),
        (150, "SPICE1", "1972-73 · Fortran", "віддано в public domain", "#eaf0fd", NEG),
        (230, "SPICE2", "1975 · Fortran", "змінний крок, Гір, MNA", "#eaf0fd", NEG),
        (310, "SPICE3", "1989 · C · Куорлз", "мова C, графіка X11", "#eaf0fd", NEG),
    ]
    bw, bh = 210, 58
    for i, (cy, title, sub, note, fc, sc) in enumerate(trunk):
        p.append(rect(tx - bw / 2, cy - bh / 2, bw, bh, fill=fc, stroke=sc, sw=2))
        p.append(text(tx, cy - 12, title, size=15, bold=True, color=sc))
        p.append(text(tx, cy + 4, sub, size=10.5, color=INK))
        p.append(text(tx, cy + 20, note, size=10, color=MUTED, italic=True))
        if i < len(trunk) - 1:
            ny = trunk[i + 1][0]
            p.append(arrow(tx, cy + bh / 2 + 2, tx, ny - bh / 2 - 2, color=INK, sw=2.2))

    # рамка «Берклі — безкоштовно й відкрито» довкола стовбура
    p.append(rect(tx - bw / 2 - 16, 30, bw + 32, 320, fill="none", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(tx, 360, "Берклі · вихідний код · безкоштовно", size=12, bold=True, color=FIELD))

    # ── Комерційні гілки: відходять праворуч від стовбура ──
    branches = [
        (150, 110, "PSpice", "1984 · MicroSim", "перший на ПК (IBM PC)"),
        (230, 235, "HSPICE", "1981 · Meta-Software", "промисловий стандарт, A. Гейлі"),
        (310, 360, "LTspice", "1998 · Linear Tech", "безкоштовний, М. Енгельгардт"),
    ]
    bx0 = tx + bw / 2
    cbw, cbh = 250, 56
    for srcY, cy, title, sub, note in branches:
        cxb = 560
        p.append(rect(cxb - cbw / 2, cy - cbh / 2, cbw, cbh, fill="#fdf3e6", stroke="#b8732e", sw=2))
        p.append(text(cxb, cy - 11, title, size=15, bold=True, color="#b8732e"))
        p.append(text(cxb, cy + 5, sub, size=10.5, color=INK))
        p.append(text(cxb, cy + 21, note, size=10, color=MUTED, italic=True))
        p.append(arrow(bx0 + 2, srcY, cxb - cbw / 2 - 2, cy, color="#b8732e", sw=1.8))

    b, _, _ = textbox(W / 2, 440,
                      "Один академічний код, відданий у суспільне надбання, породив цілу родину. Комерційні фірми\n"
                      "обгорнули те саме ядро зручностями й моделями — але «мова спайса» лишилася спільною.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'lineage.svg'), W, H, *p,
           title="Родовід SPICE: від берклівського класу до цілої індустрії")


def integ_methods():
    """Три способи замінити похідну: назад-Ейлер, трапеція — геометрично.
    Показуємо на кривій v(t): справжній нахил у новій точці й як кожен метод
    його наближає з відомих значень."""
    W, H = 780, 445
    p = []
    ox, oy = 70, 300
    aw, ah = 640, 240
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    p.append(text(ox + aw - 6, oy + 22, "час t", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - ah + 2, "напруга v", size=12, color=MUTED, anchor="end"))

    def vc(t):            # заряд RC, t у 0..1
        return 1 - math.exp(-2.6 * t)
    def XX(t):
        return ox + aw * t
    def YY(v):
        return oy - ah * v * 0.9
    pts = [(XX(t / 240.0), YY(vc(t / 240.0))) for t in range(0, 241)]
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in pts) +
             '" fill="none" stroke="%s" stroke-width="1.7" stroke-dasharray="5 3"/>' % MUTED)
    p.append(text(XX(0.52), YY(vc(0.52)) - 16, "справжня крива v(t)", size=12, color=MUTED))

    tn, tn1 = 0.30, 0.72
    vn, vn1 = vc(tn), vc(tn1)
    for tt, vv, lab, col in [(tn, vn, "tₙ (відоме)", NEG), (tn1, vn1, "tₙ₊₁ (шукане)", POS)]:
        p.append(line(XX(tt), oy, XX(tt), oy + 12, color=col, sw=1.6))
        p.append(line(XX(tt), oy, XX(tt), YY(vv), color=col, sw=1.0, dash="3 3"))
        p.append(text(XX(tt), oy + 30, lab, size=11, color=col, bold=True))
    p.append(circle(XX(tn), YY(vn), 5, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(circle(XX(tn1), YY(vn1), 5, fill="#fdecea", stroke=POS, sw=2))

    # 1) назад-Ейлер: дотична В НОВІЙ точці
    slope1 = 2.6 * math.exp(-2.6 * tn1)
    x0, x1 = XX(tn1) - aw * 0.13, XX(tn1) + aw * 0.05
    def tang_y(xpix, tpt, vpt, slope):
        dtt = (xpix - XX(tpt)) / aw
        return YY(vpt + slope * dtt)
    p.append(line(x0, tang_y(x0, tn1, vn1, slope1), x1, tang_y(x1, tn1, vn1, slope1),
                  color=FIELD, sw=2.4))
    p.append(text(XX(tn1) + 6, YY(vn1) - 30, "назад-Ейлер:", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(XX(tn1) + 6, YY(vn1) - 16, "нахил лише в новій точці", size=10, color=FIELD, anchor="start"))

    # хорда між точками — фактичний нахил, який дає різниця
    p.append(line(XX(tn), YY(vn), XX(tn1), YY(vn1), color="#b8732e", sw=1.4, dash="2 3"))
    mx = XX((tn + tn1) / 2)
    my = YY((vn + vn1) / 2)
    p.append(text(mx - 6, my + 24, "трапеція:", size=11, bold=True, color="#b8732e", anchor="middle"))
    p.append(text(mx - 6, my + 38, "середній нахил кінців", size=10, color="#b8732e", anchor="middle"))

    b, _, _ = textbox(W / 2, 402,
                      "Похідну dv/dt у новій точці не взяти прямо — її замінюють різницею (vₙ₊₁ − vₙ)/Δt.\n"
                      "Назад-Ейлер прирівнює цю різницю до нахилу лише в новій точці; трапеція — до СЕРЕДНЬОГО\n"
                      "нахилів на обох кінцях кроку, тому точніша (похибка ~Δt², а не ~Δt).",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'integ-methods.svg'), W, H, *p,
           title="Заміна похідної: назад-Ейлер проти трапеції")


def trap_ringing():
    """Зворотний бік трапеції: на різкому перепаді вона «дзвенить» числами,
    а Гір гасить — але заразом гасить і справжній дзвін."""
    W, H = 780, 400
    p = []
    ox, oy = 70, 240
    aw, ah = 640, 170
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    p.append(line(ox, oy - ah * 0.6, ox, oy + ah * 0.4, color=INK, sw=2))
    p.append(text(ox + aw - 6, oy + ah * 0.4 + 2, "час t (кроки)", size=12, color=MUTED, anchor="end"))

    def truth(t):
        return 0.0 if t < 0.30 else 1.0
    N = 200
    pts = [(ox + aw * (k / N), oy - ah * 0.55 * truth(k / N)) for k in range(N + 1)]
    p.append('<path d="M' + " L".join("%.1f %.1f" % q for q in pts) +
             '" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 3"/>' % MUTED)
    p.append(text(ox + aw * 0.64, oy - ah * 0.55 - 8, "справжня відповідь", size=11, color=MUTED))

    steps = [0.30 + 0.045 * i for i in range(11)]
    ring = []
    amp = 0.42
    for i, t in enumerate(steps):
        v = (0.55 + amp * ((-1) ** i)) if i > 0 else 0.0
        amp *= 0.70
        ring.append((ox + aw * t, oy - ah * v))
    p.append('<path d="M%.1f %.1f L' % (ox + aw * 0.30, oy) +
             " L".join("%.1f %.1f" % q for q in ring) +
             '" fill="none" stroke="%s" stroke-width="2.2"/>' % POS)
    for q in ring:
        p.append(circle(q[0], q[1], 3.4, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(ox + aw * 0.49, oy - ah * 0.95, "трапеція: числовий «дзвін»", size=12, bold=True, color=POS))
    p.append(text(ox + aw * 0.49, oy - ah * 0.95 + 15, "коливається щокроку навколо істини", size=10, color=POS))

    grng = []
    v = 0.0
    for i, t in enumerate(steps):
        v = v + (0.55 - v) * 0.55
        grng.append((ox + aw * t, oy - ah * v))
    p.append('<path d="M%.1f %.1f L' % (ox + aw * 0.30, oy) +
             " L".join("%.1f %.1f" % q for q in grng) +
             '" fill="none" stroke="%s" stroke-width="2.2"/>' % FIELD)
    for q in grng:
        p.append(circle(q[0], q[1], 3.4, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(ox + aw * 0.82, oy - ah * 0.28, "Гір: гладко, без дзвону", size=12, bold=True, color=FIELD))
    p.append(text(ox + aw * 0.82, oy - ah * 0.28 + 15, "(але глушить і справжній!)", size=10, color=FIELD))

    b, _, _ = textbox(W / 2, 366,
                      "На різкому перепаді трапеція дає числовий дзвін — паразитне коливання, що міняє знак щокроку\n"
                      "й повільно згасає; це артефакт методу, не схеми. Гір такого не має, але демпфує будь-яке\n"
                      "коливання — і легко «згладить» справжню нестійкість, показавши робочою схему, що насправді дзвенить.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'trap-ringing.svg'), W, H, *p,
           title="Дзвін трапеції проти демпфування Гіра")


def companion():
    """Модель-супутник: конденсатор на кроці Δt = провідність ‖ джерело струму,
    тож він вкладається в ту саму матрицю MNA, що й резистори."""
    W, H = 780, 340
    p = []
    lx = 175
    p.append(rect(lx - 120, 70, 240, 150, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(mtext(lx, 100, "конденсатор", size=14, bold=True, color=NEG))
    p.append(mtext(lx, 134, "i = C · dv/dt", size=15, color=INK))
    p.append(mtext(lx, 170, "похідна —\nнеалгебрична", size=11, color=MUTED))

    p.append(arrow(lx + 128, 145, lx + 248, 145, color=INK, sw=2.4))
    p.append(text(lx + 188, 128, "на кроці Δt", size=11, bold=True))
    p.append(text(lx + 188, 165, "(трапеція)", size=10, color=MUTED))

    rx = 600
    p.append(rect(rx - 135, 68, 270, 204, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(mtext(rx, 96, "модель-супутник", size=14, bold=True, color=FIELD))
    nx1, nx2 = rx - 70, rx + 70
    ny_top, ny_bot = 130, 235
    p.append(line(nx1, ny_top, nx2, ny_top, color=INK, sw=1.6))
    p.append(line(nx1, ny_bot, nx2, ny_bot, color=INK, sw=1.6))
    p.append(circle(nx1, ny_top, 3, fill=INK, stroke=INK))
    p.append(circle(nx2, ny_top, 3, fill=INK, stroke=INK))
    p.append(rect(nx1 - 12, 152, 24, 60, fill=BG, stroke=INK, sw=1.6))
    p.append(text(nx1 - 20, 187, "Geq", size=12, color=NEG, anchor="end"))
    p.append(line(nx1, ny_top, nx1, 152, color=INK, sw=1.6))
    p.append(line(nx1, 212, nx1, ny_bot, color=INK, sw=1.6))
    p.append(circle(nx2, 182, 18, fill=BG, stroke=INK, sw=1.6))
    p.append(arrow(nx2, 195, nx2, 169, color=INK, sw=1.6))
    p.append(text(nx2 + 26, 187, "Ieq", size=12, color=POS, anchor="start"))
    p.append(line(nx2, ny_top, nx2, 164, color=INK, sw=1.6))
    p.append(line(nx2, 200, nx2, ny_bot, color=INK, sw=1.6))

    b, _, _ = textbox(W / 2, 305,
                      "Замінивши dv/dt різницею, конденсатор на кожному кроці стає звичайною провідністю Geq = 2C/Δt\n"
                      "паралельно з джерелом струму Ieq, що ПАМ'ЯТАЄ минулий крок. Тепер він — лінійний елемент і\n"
                      "вкладається в ту саму матрицю, що резистори; час рахується тим самим апаратом Ньютона.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'companion.svg'), W, H, *p,
           title="Модель-супутник: конденсатор → провідність ‖ джерело")


if __name__ == '__main__':
    pipeline()
    newton()
    transient()
    analyses()
    lineage()
    integ_methods()
    trap_ringing()
    companion()
    print("OK: 8 figures ->", OUT)
