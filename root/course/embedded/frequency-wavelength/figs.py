# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Звідки береться c: дві половини поля живлять одна одну ──────────────────
# Ідея: E, що змінюється, породжує B; B, що змінюється, породжує E. Замкнена
# петля самопідтримки біжить зі швидкістю c = 1/√(μ0·ε0). Показуємо цикл
# причинності + формулу — це «двигун» усієї теми, який базова не розкриває.
def fig_wave_engine():
    W, H = 820, 340
    cx, cy = 300, 175
    R = 92
    parts = []
    parts.append(text(W/2, 30, "Хвиля сама себе штовхає — звідси стала швидкість", size=17, bold=True))

    # два вузли циклу
    eb, ew, eh = textbox(cx - R, cy, "поле E\nзмінюється", size=13, fill="#fdecea",
                         stroke=POS, color=POS, bold=True)
    bb, bw, bh = textbox(cx + R, cy, "поле B\nзмінюється", size=13, fill="#eaf0fd",
                         stroke=NEG, color=NEG, bold=True)

    # дуги-стрілки по колу (E -> B зверху, B -> E знизу)
    def arc(x1, y1, x2, y2, bend, color):
        mx, my = (x1+x2)/2, (y1+y2)/2 + bend
        return ('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                % (x1, y1, mx, my, x2, y2, color))
    parts.append(arc(cx - R + ew/2 + 4, cy - 14, cx + R - bw/2 - 4, cy - 14, -70, POS))
    parts.append(arc(cx + R - bw/2 - 4, cy + 14, cx - R + ew/2 + 4, cy + 14,  70, NEG))
    parts.append(text(cx, cy - 78, "породжує", size=12, color=MUTED, italic=True))
    parts.append(text(cx, cy + 88, "породжує", size=12, color=MUTED, italic=True))
    parts.append(eb); parts.append(bb)

    # формула праворуч
    fb, fw, fh = textbox(660, 118, "         1\nc = ─────────\n     √(μ₀ · ε₀)", size=15,
                         fill=FILL, stroke=LINE, bold=True, min_w=250)
    parts.append(fb)
    parts.append(fitbox(560, 200, 210, 100,
                        "μ₀, ε₀ — сталі порожнього\nпростору. Вони фіксовані —\nтож і c фіксована:\n≈ 299 792 458 м/с",
                        size=12, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(OUT, "wave-engine.svg"), W, H, *parts)


# ── 2. Та сама частота — коротша хвиля в середовищі ───────────────────────────
# Ідея: частота від джерела НЕ міняється, а швидкість у діелектрику падає в √εr
# разів, тож λ у стільки ж разів коротшає. Три доріжки: вакуум, коакс, FR-4.
def fig_lambda_in_medium():
    W, H = 820, 380
    x0, x1 = 210, 780
    parts = []
    parts.append(text(W/2, 28, "Однакова частота, різне середовище → різна довжина хвилі", size=16, bold=True))

    def wavey(y, cycles, color, span):
        pts = []
        n = 240
        amp = 22
        for i in range(n + 1):
            t = i / n
            xx = x0 + t * span
            yy = y - amp * math.sin(2 * math.pi * cycles * t)
            pts.append("%.1f,%.1f" % (xx, yy))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                % (" ".join(pts), color))

    rows = [
        (95,  3.0, "вакуум / повітря", "vf = 1.00", "λ = λ₀", INK),
        (200, 4.55, "коакс, εr≈2.3", "vf ≈ 0.66", "λ ≈ 0.66·λ₀", NEG),
        (305, 6.0, "мікросмужка FR-4", "vf ≈ 0.5", "λ ≈ 0.5·λ₀", POS),
    ]
    span = x1 - x0 - 10
    for y, cyc, name, vf, lam, col in rows:
        parts.append(line(x0, y, x1, y, color="#d7dbe0", sw=1))
        parts.append(wavey(y, cyc, col, span))
        parts.append(text(x0 - 12, y - 6, name, size=12, color=col, anchor="end", bold=True))
        parts.append(text(x0 - 12, y + 12, vf, size=11, color=MUTED, anchor="end"))
        parts.append(text(x1 - 4, y - 30, lam, size=12, color=col, anchor="end", bold=True))

    parts.append(fitbox(x0 - 2, 340, x1 - x0, 30,
                        "Джерело хитає з тією самою f; хвиля просто повільніша — тому в тому ж відрізку вкладається БІЛЬШЕ коротших хвиль",
                        size=12, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, "lambda-in-medium.svg"), W, H, *parts)


# ── 3. Електрична довжина: той самий дріт — «короткий» чи «довгий» ─────────────
# Ідея: важлива не довжина в см, а частка від λ. Один фізичний відрізок 5 см на
# трьох частотах: на низькій — крапка (l≪λ), на межі — помітна частка, на
# високій — ціла хвиля вкладається. Поріг «електрично довгого» ~ λ/10.
def fig_electrical_length():
    W, H = 820, 360
    parts = []
    parts.append(text(W/2, 28, "Один відрізок 5 см — «короткий» чи «довгий»? Залежить від частоти", size=15.5, bold=True))
    seg_x0, seg_x1 = 250, 560   # фізичний відрізок на екрані (умовно 5 см)
    cases = [
        (95,  "10 МГц",  "λ = 30 м",    0.0017, "l ≈ λ/6000 — електрично КРАПКА", FIELD),
        (185, "600 МГц", "λ = 50 см",   0.10,   "l ≈ λ/10 — ПОРІГ: уже треба зважати", MUTED),
        (275, "3 ГГц",   "λ = 10 см",   0.5,    "l ≈ λ/2 — електрично ДОВГИЙ провід", POS),
    ]
    for y, f, lam, frac, note, col in cases:
        # сам відрізок (однаковий на всіх рядках)
        parts.append(line(seg_x0, y, seg_x1, y, color=INK, sw=3))
        parts.append(circle(seg_x0, y, 3, fill=INK, stroke=INK))
        parts.append(circle(seg_x1, y, 3, fill=INK, stroke=INK))
        # скільки хвилі вкладається — синус амплітудою за часткою
        amp = 6 + 20 * min(frac / 0.5, 1.0)
        cyc = max(frac, 0.02)
        n = 200; pts = []
        for i in range(n + 1):
            t = i / n
            xx = seg_x0 + t * (seg_x1 - seg_x0)
            yy = y - amp * math.sin(2 * math.pi * cyc * t)
            pts.append("%.1f,%.1f" % (xx, yy))
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), col))
        parts.append(text(seg_x0 - 14, y - 4, f, size=12.5, anchor="end", bold=True))
        parts.append(text(seg_x0 - 14, y + 13, lam, size=11, anchor="end", color=MUTED))
        parts.append(text(seg_x1 + 14, y + 4, note, size=11.5, anchor="start", color=col))
    parts.append(text((seg_x0+seg_x1)/2, 315, "фізична довжина та сама — 5 см", size=12, color=MUTED, italic=True))
    parts.append(fitbox(60, 330, 700, 22,
                        "Правило: l ≳ λ/10 → провід поводиться як лінія передачі (відбиття, зсув фази), а не як просто дріт",
                        size=11.5, fill=FILL, stroke=LINE))
    render(os.path.join(OUT, "electrical-length.svg"), W, H, *parts)


# ── 4. Кінцевий ефект: реальна чвертьхвиля коротша за теоретичну ───────────────
# Ідея: теорія дає ¼λ₀, але поле «вибухає» на кінці (крайове поле) + струм
# у металі повільніший → різати треба ~на 5%. Показуємо теоретичний штир,
# реальний (коротший) і краплю крайового поля на вершечку.
def fig_end_effect():
    W, H = 760, 380
    parts = []
    parts.append(text(W/2, 28, "Реальну антену ріжуть КОРОТШЕ за теоретичну ¼λ", size=16, bold=True))
    base_y = 320
    gnd_x0, gnd_x1 = 120, 640
    parts.append(line(gnd_x0, base_y, gnd_x1, base_y, color=INK, sw=2.5))
    # штрихування землі
    for gx in range(int(gnd_x0), int(gnd_x1), 26):
        parts.append(line(gx, base_y, gx - 12, base_y + 12, color=MUTED, sw=1))
    parts.append(text((gnd_x0+gnd_x1)/2, base_y + 34, "земляна площина", size=12, color=MUTED))

    # теоретичний штир
    tx = 250; t_top = base_y - 230
    parts.append(line(tx, base_y, tx, t_top, color=NEG, sw=4))
    parts.append(text(tx, t_top - 12, "теорія", size=12.5, bold=True, color=NEG))
    parts.append(text(tx, t_top - 30, "¼λ₀", size=13, bold=True, color=NEG))

    # реальний штир (коротший ~5%)
    rx = 470; r_top = base_y - 218
    parts.append(line(rx, base_y, rx, r_top, color=POS, sw=4))
    parts.append(text(rx, r_top - 30, "реально", size=12.5, bold=True, color=POS))
    parts.append(text(rx, r_top - 12, "≈0.95·¼λ₀", size=12.5, bold=True, color=POS))
    # крайове поле на вершечку — дуги
    for rr in (10, 18, 26):
        parts.append('<path d="M%.1f %.1f a %d %d 0 1 1 %d 0" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>'
                     % (rx - rr, r_top, rr, rr, 2*rr, FIELD))
    parts.append(text(rx + 60, r_top + 6, "крайове поле\n«тягне» кінець", size=11, color=FIELD, anchor="start"))
    # рівень різниці
    parts.append(line(tx, t_top, rx, t_top, color=MUTED, sw=1, dash="4 3"))
    parts.append(text((tx+rx)/2, t_top - 6, "≈5% зрізали", size=11, color=MUTED))

    parts.append(fitbox(90, 348, 580, 26,
                        "Причини: поле розтікається за край + струм у металі трохи повільніший. Товщий провід → коротший.",
                        size=12, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, "end-effect.svg"), W, H, *parts)


# ── 5. Порахували на папері → впіймали в лабораторії (для hist-вставки) ────────
# Ідея всієї історії: c дістали ДВІЧІ, незалежними шляхами, і числа зійшлися.
# Ліва колонка — Максвелл рахує з двох електричних сталих (1862, теорія).
# Права — Герц міряє λ і f у досліді й перемножує (1888, експеримент).
# Обидві стрілки збігаються в одному числі c ≈ 3×10⁸ м/с. Це «вага» вставки —
# епістемологія передбачення-перед-дослідом, яку словами передати важко.
def fig_paper_vs_lab():
    W, H = 840, 430
    parts = []
    parts.append(text(W/2, 30, "Одну швидкість дістали двічі — і числа зійшлися", size=17, bold=True))

    lx, rx = 215, 625     # центри двох колонок
    top = 66

    # ── ліва колонка: папір / теорія ──
    parts.append(fitbox(lx - 165, top, 330, 30,
                        "НА ПАПЕРІ · Максвелл, 1862",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    lb1, _, _ = textbox(lx, top + 78,
                        "дві електричні сталі\nε₀ і μ₀\n(з дослідів із зарядами)",
                        size=12, fill=FILL, stroke=LINE)
    parts.append(lb1)
    parts.append(arrow(lx, top + 118, lx, top + 150, color=NEG, sw=2))
    lb2, _, _ = textbox(lx, top + 188, "        1\nc = ─────────\n     √(μ₀·ε₀)",
                        size=13, fill="#eaf0fd", stroke=NEG, bold=True, min_w=220)
    parts.append(lb2)
    parts.append(arrow(lx, top + 228, lx, top + 262, color=NEG, sw=2))
    parts.append(text(lx, top + 254, "порахував", size=11, color=MUTED, italic=True, anchor="middle"))

    # ── права колонка: лабораторія / дослід ──
    parts.append(fitbox(rx - 165, top, 330, 30,
                        "У ЛАБОРАТОРІЇ · Герц, 1888",
                        size=13, bold=True, fill="#fdecea", stroke=POS, color=POS))
    rb1, _, _ = textbox(rx, top + 78,
                        "λ зі стоячої хвилі (лінійка)\nf з будови диполя\n(обчислена)",
                        size=12, fill=FILL, stroke=LINE)
    parts.append(rb1)
    parts.append(arrow(rx, top + 118, rx, top + 150, color=POS, sw=2))
    rb2, _, _ = textbox(rx, top + 188, "c = λ · f", size=15,
                        fill="#fdecea", stroke=POS, bold=True, min_w=220)
    parts.append(rb2)
    parts.append(arrow(rx, top + 228, rx, top + 262, color=POS, sw=2))
    parts.append(text(rx, top + 254, "зміряв", size=11, color=MUTED, italic=True, anchor="middle"))

    # ── спільний результат унизу: обидві стрілки сходяться ──
    cy = top + 320
    res, rw, rh = textbox(W/2, cy, "c ≈ 3 × 10⁸ м/с\n(швидкість світла)",
                          size=15, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True, min_w=280)
    # діагональні лінії від низу колонок до результату
    parts.append(line(lx, top + 268, W/2 - rw/2 + 40, cy - rh/2, color=NEG, sw=1.6, dash="5 3"))
    parts.append(line(rx, top + 268, W/2 + rw/2 - 40, cy - rh/2, color=POS, sw=1.6, dash="5 3"))
    parts.append(res)
    parts.append(text(W/2, cy + rh/2 + 22,
                      "два незалежні шляхи, жодної причини вести в одне місце — а привели",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "paper-vs-lab.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_wave_engine()
    fig_lambda_in_medium()
    fig_electrical_length()
    fig_end_effect()
    fig_paper_vs_lab()
    print("done:", os.listdir(OUT))
