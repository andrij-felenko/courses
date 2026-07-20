# -*- coding: utf-8 -*-
"""Фігури до теми «Байпасний діод сонячної панелі» (силова електроніка).
Фігури:
  mechanism.svg    — підрядок елементів + байпасний діод у двох станах: усе освітлено (струм крізь елементи, діод замкнений) vs один елемент у тіні (струм звертає в діод, елемент розвантажений)
  junction-box.svg — панель із трьох підрядків, кожен зі своїм діодом у коробці ззаду; один підрядок затінено й обійдено, два працюють
  pv-curve.svg     — крива «потужність–напруга»: гладкий один горб (повне сонце) vs многогорба східчаста (часткове затінення) з глобальним і локальним максимумами
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

LIT   = "#ffe08a"   # освітлений елемент
LITED = "#e0a800"
SHADE = "#9aa3ad"   # затінений елемент
SHDED = "#5b636c"
GREEN = FIELD       # активний струм / діод
GREY  = "#b7bdc4"   # неактивна гілка


def carrow(x1, y1, x2, y2, color=GREEN, sw=3.4):
    """Осеспрямована стрілка заданого кольору (свій наконечник-трикутник)."""
    seg = line(x1, y1, x2, y2, color=color, sw=sw)
    a = 7.0
    if abs(y2 - y1) < 0.5:                     # горизонтальна
        d = 1 if x2 >= x1 else -1
        tri = '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
            x2, y2, x2 - d * a, y2 - a * 0.7, x2 - d * a, y2 + a * 0.7, color)
    else:                                      # вертикальна
        d = 1 if y2 >= y1 else -1
        tri = '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
            x2, y2, x2 - a * 0.7, y2 - d * a, x2 + a * 0.7, y2 - d * a, color)
    return seg + tri


def diode_h(cx, cy, color=INK, fill=FILL, sw=2.2):
    """Діод горизонтально: трикутник вістрям праворуч, смужка-катод праворуч."""
    tri = '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (
        cx - 13, cy - 12, cx - 13, cy + 12, cx + 9, cy, fill, color, sw)
    bar = line(cx + 9, cy - 13, cx + 9, cy + 13, color=color, sw=sw + 0.6)
    return tri + bar


def cell(x, y, w, h, fill, edge):
    """Клітинка-фотоелемент: прямокутник із діагональними «дротиками-шинами»."""
    r = rect(x, y, w, h, fill=fill, stroke=edge, sw=1.6, rx=3)
    bus = (line(x + w * 0.33, y, x + w * 0.33, y + h, color=edge, sw=0.9) +
           line(x + w * 0.66, y, x + w * 0.66, y + h, color=edge, sw=0.9))
    return r + bus


# ─────────────────────────────────────────────────────────────────────────────
def mechanism():
    W, H = 880, 348
    p = []

    def sub(cx, title, shaded):
        out = []
        out.append(rect(cx - 196, 56, 392, 262, fill="#fcfdff", stroke="#d9dee5", sw=1.4, rx=10))
        out.append(text(cx, 82, title, size=15, bold=True))

        # ряд із 4 елементів
        n, cw, gap = 4, 46, 10
        total = n * cw + (n - 1) * gap
        x0 = cx - total / 2
        ymid = 122
        for i in range(n):
            x = x0 + i * (cw + gap)
            if shaded and i == 1:
                out.append(cell(x, ymid - 17, cw, 34, SHADE, SHDED))
            else:
                out.append(cell(x, ymid - 17, cw, 34, LIT, LITED))
            if i < n - 1:                       # перемичка між елементами
                out.append(line(x + cw, ymid, x + cw + gap, ymid, color=INK, sw=2))
        if shaded:
            out.append(text(x0 + cw + gap + cw / 2, ymid - 26, "у тіні", size=11, color=SHDED, bold=True))

        Lx, Rx = cx - total / 2, cx + total / 2
        y_dio, y_bot = 208, 274

        # вертикальні рейки
        railcol = INK
        out.append(line(Lx, ymid, Lx, y_bot, color=railcol, sw=2))
        out.append(line(Rx, ymid, Rx, y_bot, color=railcol, sw=2))
        # гілка діода
        out.append(line(Lx, y_dio, Lx - 0, y_dio, color=railcol, sw=2))
        out.append(line(Lx, y_dio, cx - 13, y_dio, color=(GREEN if shaded else INK), sw=2))
        out.append(line(cx + 9, y_dio, Rx, y_dio, color=(GREEN if shaded else INK), sw=2))
        out.append(diode_h(cx, y_dio,
                            color=(GREEN if shaded else INK),
                            fill=("#e8f7ee" if shaded else FILL),
                            sw=2.4))
        out.append(text(cx, y_dio + 30, ("діод відкритий" if shaded else "діод замкнений"),
                        size=11.5, color=(GREEN if shaded else MUTED), bold=shaded))

        # зовнішні виводи + полярність
        out.append(minus(Lx, y_bot + 4, r=8))
        out.append(plus(Rx, y_bot + 4, r=8))

        # струм
        if not shaded:
            out.append(carrow(Lx, y_bot - 6, Lx, ymid + 2))                # вгору лівою рейкою
            out.append(carrow(x0 + cw, ymid, x0 + total - cw, ymid))       # праворуч крізь елементи
            out.append(carrow(Rx, ymid + 2, Rx, y_bot - 6))                # вниз правою рейкою
        else:
            out.append(carrow(Lx, y_bot - 6, Lx, y_dio + 2))               # вгору до діода
            out.append(carrow(cx - 30, y_dio, cx + 24, y_dio))             # праворуч крізь діод
            out.append(carrow(Rx, y_dio + 2, Rx, y_bot - 6))               # вниз
            # елементи майже без струму
            out.append(text(cx, ymid + 40, "елементи розвантажені", size=10.5, color=MUTED))
        return out

    p += sub(232, "Усе освітлено", False)
    p += sub(648, "Один елемент — у тіні", True)

    render(os.path.join(OUT, 'mechanism.svg'), W, H, *p,
           title="Байпасний діод: у нормі мовчить, у тіні забирає струм на себе")


# ─────────────────────────────────────────────────────────────────────────────
def junction_box():
    W, H = 860, 470
    p = []

    box_x, box_y, box_w, box_h = 590, 74, 210, 348
    # розподільна коробка
    p.append(rect(box_x, box_y, box_w, box_h, fill="#f0f2f5", stroke="#9aa3ad", sw=1.8, rx=10))
    p.append(text(box_x + box_w / 2, box_y + 22, "розподільна коробка", size=12.5, bold=True, color="#4b5560"))

    rows = [("Підрядок 1", False), ("Підрядок 2", True), ("Підрядок 3", False)]
    y0, rh, gap = 108, 78, 34
    for i, (name, shaded) in enumerate(rows):
        ry = y0 + i * (rh + gap)
        rx, rw = 70, 470
        # смуга підрядка
        p.append(rect(rx, ry, rw, rh, fill=("#eef1f4" if shaded else "#fff6dc"),
                      stroke=("#9aa3ad" if shaded else LITED), sw=1.8, rx=8))
        p.append(text(rx + 12, ry + 20, name, size=12.5, bold=True,
                      color=("#5b636c" if shaded else "#8a6d00"), anchor="start"))
        # маленькі елементи всередині
        n, cw = 7, 40
        cy = ry + rh / 2 + 6
        span_x0 = rx + 60
        for k in range(n):
            x = span_x0 + k * (cw + 10)
            if shaded and k == 3:
                p.append(cell(x, cy - 13, cw, 26, SHADE, SHDED))
                p.append(text(x + cw / 2, cy - 20, "тінь", size=9.5, color=SHDED, bold=True))
            else:
                p.append(cell(x, cy - 13, cw, 26,
                              (SHADE if shaded else LIT),
                              (SHDED if shaded else LITED)))

        # діод цього підрядка — від правого краю смуги в коробку
        dy = ry + rh / 2
        p.append(line(rx + rw, dy, box_x + 42, dy, color=(GREEN if shaded else GREY),
                      sw=(3 if shaded else 2)))
        p.append(diode_h(box_x + 66, dy,
                         color=(GREEN if shaded else "#8a929b"),
                         fill=("#e8f7ee" if shaded else "#e9ecef"), sw=2.3))
        p.append(line(box_x + 75, dy, box_x + box_w - 20, dy,
                      color=(GREEN if shaded else GREY), sw=(3 if shaded else 2)))
        p.append(text(rx + rw / 2, ry + rh + 20,
                      ("↑ струм іде в обхід — підрядок вимкнено" if shaded else "працює нормально"),
                      size=11, color=(GREEN if shaded else MUTED), bold=shaded))

    # вихід панелі з коробки
    p.append(minus(box_x + box_w - 20, y0 - 10, r=8))
    p.append(plus(box_x + box_w - 20, y0 + 2 * (rh + gap) + rh + 10, r=8))
    p.append(text(box_x + box_w / 2, box_y + box_h - 12, "вихід панелі", size=11, color=MUTED))

    render(os.path.join(OUT, 'junction-box.svg'), W, H, *p,
           title="Три діоди ділять панель на зони: тінь коштує однієї третини, а не всього")


# ─────────────────────────────────────────────────────────────────────────────
def pv_curve():
    W, H = 820, 470
    p = []
    ox, oy, gw, gh = 92, 396, 640, 320
    # осі
    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.8))
    p.append(text(ox + gw, oy + 24, "напруга панелі, В", size=12, color=MUTED, anchor="end"))
    p.append(text(ox + 4, oy - gh - 10, "потужність, Вт", size=12, color=MUTED, anchor="start"))

    Vmax, Pmax = 38.0, 285.0
    def X(v): return ox + gw * (v / Vmax)
    def Y(pw): return oy - gh * (pw / Pmax)

    # засічки осей
    for v in range(0, 39, 6):
        p.append(line(X(v), oy, X(v), oy + 5, color=INK, sw=1.2))
        p.append(text(X(v), oy + 20, str(v), size=10, color=MUTED))
    for pw in range(0, 281, 70):
        p.append(line(ox - 5, Y(pw), ox, Y(pw), color=INK, sw=1.2))
        p.append(text(ox - 10, Y(pw) + 4, str(pw), size=10, color=MUTED, anchor="end"))

    def full_P(v):
        I = 9.0 / (1 + math.exp((v - 31.5) / 1.5))
        return v * I

    def shaded_P(v):
        I = (3.0 + 6.0 / (1 + math.exp((v - 22.0) / 1.4))) / (1 + math.exp((v - 35.8) / 0.9))
        return v * I

    def poly(fn, col, sw, dash=None):
        pts = []
        v = 0.0
        while v <= Vmax + 0.01:
            pts.append((X(v), Y(fn(v))))
            v += 0.25
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        extra = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (d, col, sw, extra))

    # повне сонце
    p.append(poly(full_P, MUTED, 2.6, dash="7 5"))
    # часткове затінення
    p.append(poly(shaded_P, POS, 3.0))

    # знайти піки затіненої кривої
    vs = [i * 0.1 for i in range(0, 381)]
    ps = [(v, shaded_P(v)) for v in vs]
    # глобальний
    gv, gp = max(ps, key=lambda t: t[1])
    # локальний у високовольтній частині (v > 27)
    hi = [(v, pw) for v, pw in ps if v > 27]
    lv, lp = max(hi, key=lambda t: t[1])

    # позначки піків
    p.append(circle(X(gv), Y(gp), 5, fill=POS, stroke=POS, sw=1))
    p.append(circle(X(lv), Y(lp), 5, fill="#fff", stroke=POS, sw=2))

    # підпис повного сонця
    vf = max(vs, key=lambda v: full_P(v))
    p.append(circle(X(vf), Y(full_P(vf)), 4, fill=MUTED, stroke=MUTED, sw=1))
    b, bw, bh = textbox(X(vf) + 6, Y(full_P(vf)) - 30, "повне сонце\nодин максимум",
                        size=11, color="#4b5560", fill="#f4f6f8", stroke="#c9ced6")
    p.append(b)

    b, bw, bh = textbox(X(gv) - 96, Y(gp) - 8, "глобальний\nмаксимум",
                        size=11.5, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b)
    b, bw, bh = textbox(X(lv) + 78, Y(lp) + 4, "локальний максимум\n— пастка трекера",
                        size=11, color="#a03123", fill="#fdecea", stroke="#e0a79f")
    p.append(b)
    # лінія-виноска до локального піка
    p.append(line(X(lv) + 6, Y(lp), X(lv) + 78 - 0.5 * (text_width("локальний максимум", 11) + 16) + 2, Y(lp) + 2,
                  color="#c9877e", sw=1, dash="3 3"))

    render(os.path.join(OUT, 'pv-curve.svg'), W, H, *p,
           title="Затінення розбиває один горб потужності на кілька")


# ─────────────────────────────────────────────────────────────────────────────
def hist_timeline():
    """Вертикальна стрічка часу: як гаряча пляма з випадкового лиха стала
    обов'язковим пунктом випробувань модуля (космос → земля → специфікація)."""
    W, H = 880, 760
    p = []

    rows = [
        (100, "1971", NEG,
         "Здогад у космічній програмі",
         ["Ганс Раушенбах (TRW) друкує аналіз затінених масивів:",
          "затінений елемент іде у зворотне зміщення й гріється —",
          "і пропонує вмикати захисні діоди на групи елементів."]),
        (210, "1975", "#3a4652",
         "Панель сходить на землю: проєкт JPL",
         ["Дешеві кремнієві модулі для дахів і полів. Починаються",
          "«блокові» держзакупівлі — щораз суворіші вимоги до модуля."]),
        (320, "1978", "#3a4652",
         "Блок IV",
         ["Специфікація вже випробовує град, вологу, теплові цикли —",
          "але гарячої плями в переліку тестів іще нема."]),
        (430, "1980", FIELD,
         "Лабораторний тест (Ґонзалес і Вівер, JPL)",
         ["На 14-й конференції PVSC показано, як виміряти,",
          "чи витримає модуль зворотний нагрів затіненого елемента."]),
        (540, "1981", POS,
         "Блок V: гаряча пляма — обов'язкове випробування",
         ["Щоб пройти тест, доводиться вбудовувати байпасні",
          "діоди в кожен модуль. Хитрість стає стандартом."]),
        (650, "1986", MUTED,
         "Спадок: напрацювання → стандарт IEC 61215",
         ["Програму закривають; її тести лягають в основу",
          "міжнародної кваліфікації модулів, чинної й досі."]),
    ]

    ax = 214
    # хребет стрічки
    p.append(line(ax, rows[0][0], ax, rows[-1][0], color="#c9ced6", sw=3))

    for cy, year, col, head, body in rows:
        p.append(text(192, cy + 6, year, size=20, bold=True, color=col, anchor="end"))
        p.append(circle(ax, cy, 9, fill=col, stroke=BG, sw=2))
        p.append(line(ax + 10, cy, ax + 26, cy, color=col, sw=2.4))
        p.append(text(246, cy - 20, head, size=14.5, bold=True, color=INK, anchor="start"))
        for i, ln in enumerate(body):
            p.append(text(246, cy + 2 + i * 17, ln, size=12.3, color="#4b5560", anchor="start"))

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *p,
           title="Гаряча пляма: від здогаду до пункту специфікації")


# ─────────────────────────────────────────────────────────────────────────────
def shading_sim():
    """Реальний вивід симуляції: I–V і P–V частково затіненого модуля (3×20,
    підрядки з фотострумами 9/6/3 А). Ліворуч — струм модуля сходинками; праворуч —
    три горби потужності з позначеним глобальним максимумом і пасткою трекера."""
    W, H = 900, 470
    Vt = 1.380649e-23 * 298.15 / 1.602176634e-19
    nId, I0d, Iph, Vbp = 1.0, 6.5e-10, 9.0, 0.40

    def cellV(I, iph):
        return nId * Vt * math.log(max((iph - I) / I0d + 1.0, 1e-12))

    subs = [[9.0] * 20, [9.0] * 19 + [6.0], [9.0] * 19 + [3.0]]

    def modV(I):
        t = 0.0
        for cells in subs:
            t += (-Vbp) if I > min(cells) else sum(cellV(I, c) for c in cells)
        return t

    N = 1400
    data = []
    for j in range(N + 1):
        I = j * (Iph - 1e-4) / N
        v = modV(I)
        data.append((v, I, v * I))

    gi = max(range(len(data)), key=lambda j: data[j][2])          # глобальний
    peaks = [j for j in range(1, len(data) - 1)
             if data[j][2] >= data[j - 1][2] and data[j][2] > data[j + 1][2]]
    ti = max(peaks, key=lambda j: data[j][0])                     # пастка = найправіший горб
    gV, gI, gP = data[gi]
    tV, tI, tP = data[ti]

    pt, ph = 74, 300
    pb = pt + ph
    Vax = 38.0
    L0, L1 = 74, 410
    R0, R1 = 520, 856

    def XL(v): return L0 + (L1 - L0) * (v / Vax)
    def XR(v): return R0 + (R1 - R0) * (v / Vax)
    def YI(i): return pb - ph * (i / 9.5)
    def YP(pw): return pb - ph * (pw / 150.0)

    p = []

    def axes(x0, x1, ylabel, yticks, Yf):
        out = [line(x0, pb, x1, pb, color=INK, sw=1.8),
               line(x0, pb, x0, pt, color=INK, sw=1.8),
               text((x0 + x1) / 2, pb + 40, "напруга модуля, В", size=12, color=MUTED),
               text(x0 - 44, pt - 14, ylabel, size=12, color=MUTED, anchor="start")]
        for v in range(0, 37, 6):
            xx = x0 + (x1 - x0) * (v / Vax)
            out.append(line(xx, pb, xx, pb + 5, color=INK, sw=1.2))
            out.append(text(xx, pb + 22, str(v), size=10, color=MUTED))
        for yv in yticks:
            out.append(line(x0 - 5, Yf(yv), x0, Yf(yv), color=INK, sw=1.2))
            out.append(text(x0 - 10, Yf(yv) + 4, str(yv), size=10, color=MUTED, anchor="end"))
        return out

    def curve(Xf, Yf, valkey, col, sw):
        pts = ["%.1f %.1f" % (Xf(d[0]), Yf(d[valkey])) for d in data]
        return '<path d="M%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (
            " L".join(pts), col, sw)

    # ── ліва панель: I–V ──
    p += axes(L0, L1, "струм, А", [0, 3, 6, 9], YI)
    p.append(text((L0 + L1) / 2, 56, "Струм модуля (I–V)", size=13.5, bold=True))
    p.append(curve(XL, YI, 1, NEG, 2.6))
    # сходинка 1: діод найслабшого підрядка (3) відкрився при струмі ≈3 А
    b, bw, bh = textbox(XL(31), YI(5.1), "діод підрядка 3\nвідкрився",
                        size=10, color="#3a5bbf", fill="#eef2fd", stroke="#b9c6ef", pad=7)
    p.append(b)
    p.append(line(XL(31), YI(5.1) + bh / 2 + 3, XL(29), YI(3.05), color="#9db0e6", sw=1, dash="3 3"))
    # сходинка 2: відкрились діоди підрядків 2 і 3 при струмі ≈6 А
    b, bw, bh = textbox(XL(17), YI(3.5), "діоди підрядків\n2 і 3 відкрилися",
                        size=10, color="#3a5bbf", fill="#eef2fd", stroke="#b9c6ef", pad=7)
    p.append(b)
    p.append(line(XL(17), YI(3.5) - bh / 2 - 3, XL(17), YI(5.95), color="#9db0e6", sw=1, dash="3 3"))

    # ── права панель: P–V ──
    p += axes(R0, R1, "потужність, Вт", [0, 50, 100, 150], YP)
    p.append(text((R0 + R1) / 2, 56, "Потужність модуля (P–V)", size=13.5, bold=True))
    p.append(curve(XR, YP, 2, POS, 3.0))

    p.append(circle(XR(gV), YP(gP), 6, fill=POS, stroke=POS, sw=1))
    b, bw, bh = textbox(XR(13.5), YP(32), "справжній (глобальний)\nмаксимум ≈ %.0f Вт" % gP,
                        size=10.5, color=POS, bold=True, fill="#fdecea", stroke=POS, pad=7)
    p.append(b)
    p.append(line(XR(13.5) + bw / 2 - 4, YP(32) - bh / 2, XR(gV) - 4, YP(gP) + 7,
                  color="#d98b81", sw=1, dash="3 3"))

    p.append(circle(XR(tV), YP(tP), 6, fill="#fff", stroke=POS, sw=2))
    b, bw, bh = textbox(XR(29.5), YP(38), "тут застряг\nпростий трекер\n≈ %.0f Вт" % tP,
                        size=10.5, color="#a03123", fill="#fdecea", stroke="#e0a79f", pad=7)
    p.append(b)
    p.append(line(XR(29.5), YP(38) - bh / 2, XR(tV) - 1, YP(tP) + 7,
                  color="#c9877e", sw=1, dash="3 3"))

    render(os.path.join(OUT, 'shading-sim.svg'), W, H, *p,
           title="Симуляція: три підрядки → три горби, а простий трекер бере не той")


# ---------------------------------------------------------------------------
def cbs_block():
    """Внутрішня блок-схема активного байпасного ключа (вставка comp-cool-bypass-switch)."""
    W, H = 940, 452
    p = []

    p.append(rect(44, 54, 852, 372, fill="#fcfdff", stroke="#c4ccd6", sw=1.6, rx=14))
    p.append('<rect x="44" y="54" width="852" height="372" rx="14" fill="none" '
             'stroke="#9aa3ad" stroke-width="1.4" stroke-dasharray="8 6"/>')
    p.append(text(470, 82, "активний байпасний ключ — саможивний, у корпусі діода",
                  size=14, bold=True))

    rail = 372
    p.append(line(70, rail, 96, rail, color=INK, sw=3))
    p.append(circle(70, rail, 10, fill="#eef1f4", stroke=INK, sw=2))
    p.append(text(70, rail + 30, "анод", size=12, bold=True))
    p.append(line(844, rail, 872, rail, color=INK, sw=3))
    p.append(circle(880, rail, 10, fill="#eef1f4", stroke=INK, sw=2))
    p.append(text(880, rail + 30, "катод", size=12, bold=True))

    mfx, mfw = 400, 150
    p.append(rect(mfx, rail - 34, mfw, 68, fill="#eef7ff", stroke="#4a6fa5", sw=1.8, rx=8))
    p.append(mtext(mfx + mfw / 2, rail - 6, ["силовий", "MOSFET"], size=13, bold=True))
    p.append(text(mfx + mfw / 2, rail + 18, "відкритий ≈ міліоми", size=10, color=MUTED))
    p.append(text(mfx + mfw / 2, 414, "паралельно — діод тіла (заводить старт)",
                  size=10.5, color=MUTED))

    p.append(arrow(100, rail, mfx - 4, rail, color=FIELD, sw=5))
    p.append(arrow(mfx + mfw + 4, rail, 840, rail, color=FIELD, sw=5))
    p.append(text(250, rail - 12, "струм обходу", size=11.5, color=FIELD, bold=True))

    def blk(x, w, lines):
        p.append(rect(x, 130, w, 62, fill=FILL, stroke=LINE, sw=1.6, rx=8))
        p.append(mtext(x + w / 2, 158 if len(lines) == 2 else 166, lines, size=12, bold=True))
    blk(96, 190, ["компаратор", "(датчик напряму)"])
    blk(372, 202, ["зарядний насос", "+ конденсатор"])
    blk(662, 170, ["драйвер затвора"])

    p.append(line(150, rail, 150, 192, color=NEG, sw=1.6))
    p.append(line(240, rail, 240, 192, color=NEG, sw=1.6))
    p.append(mtext(305, 288, ["падіння", "на MOSFET"], size=10, color=MUTED))

    p.append(arrow(286, 161, 372, 161, color=INK, sw=2))
    p.append(text(329, 149, "дозвіл", size=10, color=MUTED))
    p.append(arrow(574, 161, 662, 161, color=INK, sw=2))

    p.append(line(600, rail, 600, 112, color=NEG, sw=1.8))
    p.append(line(600, 112, 473, 112, color=NEG, sw=1.8))
    p.append(arrow(473, 112, 473, 130, color=NEG, sw=1.8))
    p.append(text(612, 250, "живлення", size=10, color=NEG, anchor="start"))

    p.append(line(747, 192, 747, 306, color=INK, sw=2))
    p.append(line(747, 306, 512, 306, color=INK, sw=2))
    p.append(arrow(512, 306, 512, rail - 34, color=INK, sw=2))
    p.append(text(690, 298, "затвор", size=10, color=MUTED))

    render(os.path.join(OUT, 'block.svg'), W, H, *p,
           title="Що ховається за двома лапами: MOSFET + насос, живлені власним струмом")


# ---------------------------------------------------------------------------
def cbs_cycle():
    """Напруга на активному ключі в часі: блокада -> старт крізь діод тіла -> канал + пульсації."""
    W, H = 980, 424
    p = []
    ox, oy, gx1 = 92, 332, 852

    p.append(line(ox, 78, ox, 352, color=INK, sw=1.6))
    p.append(line(ox, oy, gx1, oy, color=INK, sw=1.6))
    p.append(text(ox + 6, 70, "напруга на ключі", size=11.5, color=MUTED, anchor="start"))
    p.append(text(864, oy - 4, "час ->", size=11.5, color=MUTED, anchor="start"))

    y06, y40 = 142, 300
    p.append(line(ox, y06, gx1, y06, color="#c8ced6", sw=1.2, dash="6 5"))
    p.append(line(ox, y40, gx1, y40, color="#bfe0cc", sw=1.4, dash="6 5"))
    p.append(mtext(862, y06, ["≈ 0.6 В", "діод тіла"], size=11, color="#8a929b", anchor="start"))
    p.append(mtext(862, y40, ["≈ 40 мВ", "канал FET"], size=11, color=FIELD, anchor="start"))

    p.append(line(300, 82, 300, 348, color=POS, sw=1.6, dash="5 4"))
    p.append(text(300, 74, "лягла тінь", size=11.5, color=POS, bold=True))

    pts = [(92, 346), (300, 346), (305, oy), (313, y06), (346, 150), (362, y40)]
    for sx in (446, 536, 626, 716, 790):
        pts += [(sx - 5, y40), (sx, 190), (sx + 7, y40)]
    pts.append((848, y40))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (d, POS))

    p.append(mtext(200, 250, ["блокада:", "витік ~0.3 мкА"], size=10.5, color=MUTED))
    p.append(line(430, 122, 332, y06, color="#b9c0c9", sw=1, dash="3 3"))
    p.append(mtext(452, 108, ["діод тіла заводить", "насос (~200 мкс)"], size=10.5,
                   color=INK, anchor="start"))

    p.append(text(196, 372, "здорова панель: блокада", size=11, color=MUTED))
    p.append(text(333, 372, "старт", size=11, color=MUTED))
    p.append(text(618, 372, "робота: канал відкритий, дрібні піки дозарядки насоса",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'cycle.svg'), W, H, *p,
           title="Життя ключа: тиша й блокада -> спалах старту -> холодний канал із пульсаціями")


# ---------------------------------------------------------------------------
def cbs_compare():
    """Шотткі проти активного ключа: тепло при 9 А + витік у блокаді."""
    W, H = 900, 384
    p = []
    x0, full = 250, 560
    def L(pw): return full * (pw / 3.6)

    p.append(text(238, 122, "Шотткі", size=13, bold=True, anchor="end"))
    p.append(text(238, 140, "0.4 В · 9 А", size=10, color=MUTED, anchor="end"))
    p.append(rect(x0, 100, L(3.6), 44, fill="#f7d2cb", stroke=POS, sw=1.6, rx=5))
    p.append(text(x0 + L(3.6) + 8, 128, "3.6 Вт", size=13, bold=True, color=POS, anchor="start"))

    p.append(text(238, 202, "активний ключ", size=13, bold=True, anchor="end"))
    p.append(text(238, 220, "36 мВ · 9 А", size=10, color=MUTED, anchor="end"))
    p.append(rect(x0, 180, L(0.32), 44, fill="#cdeed9", stroke=FIELD, sw=1.6, rx=5))
    p.append(text(x0 + L(0.32) + 10, 208, "0.32 Вт", size=13, bold=True, color=FIELD, anchor="start"))

    p.append(text(450, 262, "≈ 11× менше тепла  ->  коробка холодніша на ≈ 50 °C",
                  size=12.5, color=FIELD, bold=True))

    p.append(fitbox(150, 290, 600, 62,
                    "У блокаді (панель здорова, майже весь час): витік Шотткі ~100 мкА\n"
                    "проти ~0.3 мкА в активного — у сотні разів менше й без теплового розгону.",
                    size=11.5, fill="#f4f6f8", stroke="#c9ced6"))

    render(os.path.join(OUT, 'compare.svg'), W, H, *p,
           title="Прямий хід і блокада: активний ключ виграє у Шотткі двічі")



if __name__ == '__main__':
    mechanism()
    junction_box()
    pv_curve()
    hist_timeline()
    shading_sim()
    cbs_block()
    cbs_cycle()
    cbs_compare()
    print("OK:", os.listdir(OUT))
