# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4):
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw))


# ── 1. Анатомія перехідної кривої ─────────────────────────────────────────────

def fig_step_response():
    W, H = 720, 320
    ox, oy = 80, 250          # початок осей (низ-ліво)
    top = 50
    Ax = 580
    target = 110              # рівень завдання (y)
    p = []

    # осі
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 20, "час", size=12, color=INK))

    # лінія завдання + смуга ±5 %
    band = 7
    p.append(line(ox, target, ox + Ax, target, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, target + 4, "завдання", size=10, color=MUTED, anchor="start"))
    p.append(line(ox, target - band, ox + Ax, target - band, color="#dfe3e8", sw=1.0))
    p.append(line(ox, target + band, ox + Ax, target + band, color="#dfe3e8", sw=1.0))

    # перехідна крива: затухальна синусоїда, що осідає трохи нижче завдання (легкий зсув)
    base = oy
    settle = target + 4        # осідає трохи нижче завдання — показати сталий зсув
    pts = []
    N = 580
    for i in range(N + 1):
        t = i / N * 9.0
        if t < 0.3:
            y = base
        else:
            tt = t - 0.3
            env = math.exp(-0.45 * tt)              # обвідна загасання
            osc = math.cos(1.9 * tt)                # коливання навколо settle
            y = settle + (base - settle) * env * osc
        pts.append((ox + (t / 9.0) * Ax, y))
    p.append(polyline(pts, color=NEG, sw=2.6))

    # час наростання — вертикаль до першого перетину завдання
    x_rise = ox + (1.05 / 9.0) * Ax
    p.append(line(x_rise, oy, x_rise, target, color=FIELD, sw=1.6, dash="3 3"))
    p.append(text(x_rise + 4, oy - 12, "час наростання", size=9, color=FIELD, anchor="start", bold=True))

    # переліт — точка першого максимуму над завданням
    x_os = ox + (1.65 / 9.0) * Ax
    p.append(circle(x_os, target - 58, 4, fill=POS, stroke=POS))
    p.append(text(x_os + 6, target - 62, "переліт", size=10, color=POS, anchor="start", bold=True))

    # сталий зсув
    p.append(text(ox + Ax * 0.62, settle + 22, "сталий зсув (бракує I)", size=9.5, color=INK, anchor="start"))
    p.append(text(ox + Ax * 0.5, target - band - 4, "смуга встановлення ±5 %", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "step-response-anatomy.svg"), W, H, *p,
           title="Що читати у відгуку на стрибок завдання")


# ── 2. Ручне налаштування: P → D → I ──────────────────────────────────────────

def fig_manual_tuning():
    W, H = 720, 300
    p = []
    panel_w = 200
    gap = 30
    x0 = 50
    oy = 210
    top = 70
    target = 120

    def panel(ox, label, curve, color, note):
        q = []
        q.append(line(ox, oy, ox, top, color=INK, sw=1.3))
        q.append(line(ox, oy, ox + panel_w, oy, color=INK, sw=1.3))
        q.append(line(ox, target, ox + panel_w, target, color=MUTED, sw=1.1, dash="5 4"))
        q.append(text(ox + panel_w / 2, top - 8, label, size=13, color=color, bold=True))
        pts = []
        N = 200
        for i in range(N + 1):
            t = i / N * 7.0
            y = curve(t)
            pts.append((ox + (t / 7.0) * panel_w, target - y))
        q.append(polyline(pts, color=color, sw=2.4))
        q.append(text(ox + panel_w / 2, oy + 26, note, size=10.5, color=MUTED))
        return q

    base = 90  # від низу до завдання

    # (1) лише P — недосягання + дзвін навколо нижче за завдання
    def p_only(t):
        if t < 0.3:
            return -(target - oy)
        tt = t - 0.3
        env = math.exp(-0.25 * tt)
        return base * (1 - env * math.cos(2.4 * tt)) - 22  # осідає нижче завдання (зсув) + коливання

    # (2) + D — переліт прибитий, осідає нижче (ще є зсув)
    def pd(t):
        if t < 0.3:
            return -(target - oy)
        tt = t - 0.3
        env = math.exp(-0.7 * tt)
        return base * (1 - env) - 22

    # (3) + I — виходить точно на завдання
    def pid(t):
        if t < 0.3:
            return -(target - oy)
        tt = t - 0.3
        env = math.exp(-0.8 * tt)
        return base * (1 - env * (1 + 0.15 * tt))

    p += panel(x0, "(1) лише P", p_only, NEG, "коливається, не дотягує")
    p += panel(x0 + panel_w + gap, "(2) + D", pd, FIELD, "переліт прибитий")
    p += panel(x0 + 2 * (panel_w + gap), "(3) + I", pid, POS, "виходить на завдання")

    render(os.path.join(OUT, "manual-tuning-pdi.svg"), W, H, *p,
           title="Ручне налаштування по черзі: спершу P, тоді D, наприкінці I")


# ── 3. Зіглер–Ніколс: Ku і Tu ─────────────────────────────────────────────────

def fig_ziegler_nichols():
    W, H = 720, 300
    ox, oy = 80, 165
    Ax = 560
    Ay = 80
    p = []

    p.append(line(ox - 10, oy, ox + Ax + 20, oy, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax, oy, ox + Ax + 22, oy, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 28, oy + 5, "час", size=12, color=MUTED, anchor="end"))

    # стала незгасна синусоїда (межа стійкості)
    span = 4.0 * 2 * math.pi
    pts = []
    N = 400
    for i in range(N + 1):
        th = span * i / N
        x = ox + (th / span) * Ax
        y = oy - Ay * math.sin(th)
        pts.append((x, y))
    p.append(polyline(pts, color=INK, sw=2.6))

    # позначити період Tu між двома вершинами
    # вершина sin при th = π/2, 2π+π/2 ...
    def x_at(th):
        return ox + (th / span) * Ax
    a = math.pi / 2
    b = a + 2 * math.pi
    y_top = oy - Ay - 14
    p.append(line(x_at(a), oy - Ay, x_at(a), y_top, color=POS, sw=1.2, dash="3 3"))
    p.append(line(x_at(b), oy - Ay, x_at(b), y_top, color=POS, sw=1.2, dash="3 3"))
    p.append(line(x_at(a), y_top, x_at(b), y_top, color=POS, sw=1.6))
    p.append(text((x_at(a) + x_at(b)) / 2, y_top - 6, "період Tu", size=12, color=POS, bold=True))

    # амплітуда Ku-режиму
    p.append(line(ox + 8, oy, ox + 8, oy - Ay, color=FIELD, sw=1.6))
    p.append(text(ox + 14, oy - Ay / 2, "Kp = Ku", size=11, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, oy + Ay + 36, "сталі коливання: ні згасають, ні ростуть — це і є гранична жорсткість Ku",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "ziegler-nichols-ku-tu.svg"), W, H, *p,
           title="Гранична жорсткість Ku і період Tu")


# ── 4. Шпаргалка симптом → ліки ───────────────────────────────────────────────

def fig_symptom_remedy():
    W, H = 720, 300
    p = []
    rows = [
        ("Повільно реагує",            "підняти Kp",                FIELD),
        ("Застигає нижче завдання",    "підняти Ki",                NEG),
        ("Перестрілює й коливається",  "підняти Kd або знизити Kp", POS),
        ("Повільне наростальне гойдання", "знизити Ki",             NEG),
        ("Мотори деренчать",           "чистіти вимір, знизити Kd", MUTED),
    ]
    x_sym = 60
    x_arr = 360
    x_fix = 400
    y0 = 70
    dy = 42
    colw_l = 290
    colw_r = 250

    p.append(text(x_sym + colw_l / 2, y0 - 18, "симптом", size=12, color=INK, bold=True))
    p.append(text(x_fix + colw_r / 2, y0 - 18, "ліки", size=12, color=INK, bold=True))

    for i, (sym, fix, col) in enumerate(rows):
        y = y0 + i * dy
        p.append(fitbox(x_sym, y, colw_l, 32, sym, size=12, fill=FILL, stroke=LINE))
        p.append(arrow(x_arr, y + 16, x_arr + 34, y + 16, color=col, sw=2.0))
        p.append(fitbox(x_fix, y, colw_r, 32, fix, size=12, fill="#ffffff", stroke=col, color=col, bold=True))

    render(os.path.join(OUT, "symptom-remedy.svg"), W, H, *p,
           title="Симптом → яка складова винна")


# ── 5. Каскад: зовнішній контур задає завдання внутрішньому ────────────────────

def sumpoint(cx, cy, r=15):
    return (circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=2) +
            line(cx - r * 0.5, cy, cx + r * 0.5, cy, color=INK, sw=1.2) +
            line(cx, cy - r * 0.5, cx, cy + r * 0.5, color=INK, sw=1.2))


def fig_cascade():
    W, H = 720, 270
    oy = 120
    p = []

    # вхід кут*
    p.append(arrow(40, oy, 71, oy, color=NEG, sw=2))
    p.append(text(46, oy - 10, "кут*", size=10, color=NEG, anchor="start", bold=True))
    # суматор зовнішній
    p.append(sumpoint(88, oy))
    p.append(text(80, oy + 30, "−", size=14, color=POS, bold=True))
    p.append(arrow(103, oy, 130, oy, color=INK, sw=2))
    # ПІД кута (зовнішній)
    p.append(fitbox(132, oy - 22, 96, 44, "ПІД кута", size=10.5, fill="#eef3fb", stroke=NEG, bold=True))
    p.append(text(180, oy + 36, "(зовнішній)", size=9, color=MUTED))
    p.append(arrow(228, oy, 260, oy, color=INK, sw=2))
    p.append(text(245, oy - 10, "швид.*", size=9, color=INK))
    # суматор внутрішній
    p.append(sumpoint(277, oy))
    p.append(text(269, oy + 30, "−", size=14, color=POS, bold=True))
    p.append(arrow(292, oy, 318, oy, color=INK, sw=2))
    # ПІД швидкості (внутрішній)
    p.append(fitbox(320, oy - 22, 104, 44, "ПІД швидк.", size=10.5, fill="#eef7ee", stroke=FIELD, bold=True))
    p.append(text(372, oy + 36, "(внутрішній)", size=9, color=MUTED))
    p.append(arrow(424, oy, 450, oy, color=INK, sw=2))
    # об'єкт
    p.append(fitbox(452, oy - 22, 110, 44, "мотори / об'єкт", size=10, fill="#f6f4ec", stroke=INK, bold=True))
    # вихід
    p.append(line(562, oy, 612, oy, color=INK, sw=2))
    p.append(arrow(612, oy, 612, oy - 36, color=INK, sw=2))
    p.append(text(612, oy - 44, "політ", size=10, color=INK, bold=True))

    # зворотний зв'язок внутрішній (швидкість ← гіроскоп)
    p.append(circle(590, oy, 3, fill=INK, stroke=INK))
    p.append(line(590, oy, 590, oy + 80, color=INK, sw=1.6))
    p.append(line(590, oy + 80, 277, oy + 80, color=INK, sw=1.6))
    p.append(arrow(277, oy + 80, 277, oy + 15, color=INK, sw=1.6))
    p.append(text(430, oy + 94, "швидкість ← гіроскоп", size=9, color=MUTED))

    # зворотний зв'язок зовнішній (кут ← поєднання)
    p.append(circle(607, oy, 3, fill=INK, stroke=INK))
    p.append(line(607, oy, 607, oy + 118, color=INK, sw=1.6))
    p.append(line(607, oy + 118, 88, oy + 118, color=INK, sw=1.6))
    p.append(arrow(88, oy + 118, 88, oy + 15, color=INK, sw=1.6))
    p.append(text(330, oy + 132, "кут ← поєднання (оцінка орієнтації)", size=9, color=MUTED))

    # примітка про швидкість
    p.append(text(665, oy - 16, "внутрішній —", size=9, color=MUTED))
    p.append(text(665, oy - 4, "швидший ×5", size=9, color=MUTED))

    render(os.path.join(OUT, "cascade-loops.svg"), W, H, *p,
           title="Каскад: зовнішній контур (кут) задає завдання внутрішньому (швидкість)")


# ── 6. Повний контур стабілізації польоту ─────────────────────────────────────

def fig_flight_stabilization():
    W, H = 720, 290
    p = []
    boxes = [
        ("гіро + акс", "MEMS", "#fbf3f3"),
        ("поєднання", "фільтр", "#eef3fb"),
        ("оцінка\nорієнтації", "", "#eef3fb"),
        ("ПІД кута", "зовнішній", "#eef7ee"),
        ("ПІД швидк.", "D з гіро!", "#eef7ee"),
        ("мікшер", "→ 4 мотори", "#f6f4ec"),
        ("квадро-\nкоптер", "тримає горизонт", "#fdf6e3"),
    ]
    bw, bh = 86, 52
    gap = 6
    x0 = 18
    oy = 100
    centers = []
    x = x0
    for i, (title_b, sub, fill) in enumerate(boxes):
        p.append(fitbox(x, oy, bw, bh, title_b, size=10, fill=fill, stroke=INK, bold=True))
        if sub:
            p.append(text(x + bw / 2, oy + bh + 12, sub, size=9, color=MUTED))
        centers.append(x + bw / 2)
        if i < len(boxes) - 1:
            p.append(arrow(x + bw, oy + bh / 2, x + bw + gap, oy + bh / 2, color=INK, sw=1.8))
        x += bw + gap

    # зворотний зв'язок: з останнього блоку назад до поєднання
    xr = x0 + 6 * (bw + gap) + bw / 2
    p.append(line(xr, oy + bh, xr, oy + bh + 78, color=INK, sw=1.6))
    p.append(line(xr, oy + bh + 78, centers[1], oy + bh + 78, color=INK, sw=1.6))
    p.append(arrow(centers[1], oy + bh + 78, centers[1], oy + bh, color=INK, sw=1.6))

    p.append(text(W / 2, oy + bh + 96, "замкнене коло — сто разів на секунду",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, oy + bh + 130, "виміряй → оціни → порівняй із бажаним → подій проти помилки",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "flight-stabilization.svg"), W, H, *p,
           title="Як стабілізується політ — уся картина на одній схемі")


if __name__ == "__main__":
    fig_step_response()
    fig_manual_tuning()
    fig_ziegler_nichols()
    fig_symptom_remedy()
    fig_cascade()
    fig_flight_stabilization()
    print("OK: figures written to", OUT)
