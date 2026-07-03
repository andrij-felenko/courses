# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: густа матриця ваг → поріг за модулем → рідка матриця ───────────
def fig_magnitude():
    W, H = 720, 380
    frags = []
    frags.append(text(W/2, 26, "Прорідження за модулем: дрібні ваги → нулі", size=17, bold=True))

    # матриця значень (5x5) — деякі великі, багато дрібних
    vals = [
        [ 0.9, -0.04,  0.02,  0.7, -0.03],
        [-0.02,  0.8,  0.05, -0.03,  0.06],
        [ 0.03, -0.05, -0.9,  0.02,  0.04],
        [ 0.6,  0.04, -0.02,  0.05, -0.8],
        [-0.03,  0.05,  0.02, -0.06,  0.7],
    ]
    thr = 0.1
    n = 5
    cell = 46
    gx0 = 60
    gy0 = 90

    def draw_grid(x0, cull):
        out = []
        for i in range(n):
            for j in range(n):
                v = vals[i][j]
                x = x0 + j*cell
                y = gy0 + i*cell
                small = abs(v) < thr
                if cull and small:
                    out.append(rect(x, y, cell-4, cell-4, fill="#eef0f2", stroke="#cfd4d8", sw=1, rx=4))
                    out.append(text(x+(cell-4)/2, y+(cell-4)/2+5, "0", size=13, color=MUTED))
                else:
                    fill = "#fdecea" if v > 0 else "#eaf0fd"
                    stroke = POS if v > 0 else NEG
                    # у лівій (до) дрібні позначаємо блідо, щоб видно кандидатів на викид
                    if not cull and small:
                        fill = "#f6f7f8"; stroke = "#c3c8cd"
                    out.append(rect(x, y, cell-4, cell-4, fill=fill, stroke=stroke, sw=1.4, rx=4))
                    txt = ("%.2f" % v).replace("0.", ".").replace("-.", "−.")
                    col = INK if not small else MUTED
                    out.append(text(x+(cell-4)/2, y+(cell-4)/2+4, txt, size=11, color=col))
        return "".join(out)

    frags.append(draw_grid(gx0, cull=False))
    frags.append(text(gx0 + n*cell/2 - 2, gy0 + n*cell + 26, "до: густа", size=13, bold=True))
    frags.append(text(gx0 + n*cell/2 - 2, gy0 + n*cell + 46, "|w| < 0.1 — блідим", size=11, color=MUTED))

    # стрілка з підписом-порогом
    ax = gx0 + n*cell + 14
    frags.append(arrow(ax, gy0 + n*cell/2, ax + 74, gy0 + n*cell/2))
    bx, w1, h1 = textbox(ax + 37, gy0 + n*cell/2 - 30, "поріг\n|w| < 0.1\n→ 0", size=11, pad=6)
    frags.append(bx)

    gx1 = ax + 90
    frags.append(draw_grid(gx1, cull=True))
    frags.append(text(gx1 + n*cell/2 - 2, gy0 + n*cell + 26, "після: рідка", size=13, bold=True))
    frags.append(text(gx1 + n*cell/2 - 2, gy0 + n*cell + 46, "лишились опорні зв'язки", size=11, color=FIELD))

    render(os.path.join(OUT, "magnitude-prune.svg"), W, H, *frags)


# ── Фігура 2: неструктуроване vs структуроване прорідження ───────────────────
def fig_structured():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 26, "Дірки в матриці ще не прискорюють — прискорює викинутий рядок", size=16, bold=True))

    n = 6
    cell = 26
    gy0 = 96

    # ліва: неструктуроване — випадкові нулі
    holes_u = {(0,2),(1,4),(2,1),(2,5),(3,0),(3,3),(4,2),(4,5),(5,1),(0,5),(1,1),(5,4),(3,5),(2,3)}
    lx0 = 70
    for i in range(n):
        for j in range(n):
            x = lx0 + j*cell; y = gy0 + i*cell
            if (i, j) in holes_u:
                frags.append(rect(x, y, cell-3, cell-3, fill="#f0f1f3", stroke="#d3d7db", sw=1, rx=3))
            else:
                frags.append(rect(x, y, cell-3, cell-3, fill="#dfeaff", stroke=NEG, sw=1, rx=3))
    frags.append(text(lx0 + n*cell/2 - 1, gy0 - 14, "неструктуроване", size=13, bold=True))
    frags.append(text(lx0 + n*cell/2 - 1, gy0 + n*cell + 22, "нулі розсипані", size=12, color=MUTED))
    frags.append(text(lx0 + n*cell/2 - 1, gy0 + n*cell + 42, "форма та сама →", size=12, color=POS))
    frags.append(text(lx0 + n*cell/2 - 1, gy0 + n*cell + 60, "звичайне залізо не швидше", size=12, color=POS, bold=True))

    # права: структуроване — цілі рядки геть
    dead_rows = {1, 3}
    rx0 = 430
    row = 0
    for i in range(n):
        for j in range(n):
            x = rx0 + j*cell
            if i in dead_rows:
                # мертвий рядок відсуваємо вбік/блідо (нема в новій матриці)
                y = gy0 + i*cell
                frags.append(rect(x, y, cell-3, cell-3, fill="#f0f1f3", stroke="#d3d7db", sw=1, rx=3))
            else:
                y = gy0 + i*cell
                frags.append(rect(x, y, cell-3, cell-3, fill="#dcf3e6", stroke=FIELD, sw=1, rx=3))
    # перекреслити мертві рядки
    for i in dead_rows:
        yy = gy0 + i*cell + (cell-3)/2
        frags.append(line(rx0 - 4, yy, rx0 + n*cell - 3, yy, color=POS, sw=2.4))
    frags.append(text(rx0 + n*cell/2 - 1, gy0 - 14, "структуроване", size=13, bold=True))
    frags.append(text(rx0 + n*cell/2 - 1, gy0 + n*cell + 22, "цілі нейрони геть", size=12, color=MUTED))
    frags.append(text(rx0 + n*cell/2 - 1, gy0 + n*cell + 42, "матриця менша →", size=12, color=FIELD))
    frags.append(text(rx0 + n*cell/2 - 1, gy0 + n*cell + 60, "менше рядків = менше роботи", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "structured-vs-unstructured.svg"), W, H, *frags)


# ── Фігура 3: цикл навчити → прорідити → донавчити ───────────────────────────
def fig_loop():
    W, H = 720, 340
    frags = []
    frags.append(text(W/2, 26, "Прорідження ітеративне: різати потроху й щоразу лікувати", size=16, bold=True))

    cy = 150
    b1, w1, h1 = textbox(120, cy, "1. Навчити\nповну мережу", size=13, pad=10, min_w=140)
    b2, w2, h2 = textbox(340, cy, "2. Викинути\nнайдрібніші ваги", size=13, pad=10, min_w=150,
                         fill="#fdf0ee", stroke=POS)
    b3, w3, h3 = textbox(575, cy, "3. Донавчити\n(лікувати рану)", size=13, pad=10, min_w=150,
                         fill="#eef8f1", stroke=FIELD)
    frags += [b1, b2, b3]

    frags.append(arrow(120 + w1/2, cy, 340 - w2/2, cy))
    frags.append(arrow(340 + w2/2, cy, 575 - w3/2, cy))
    # петля 3 → 2 зверху
    frags.append(arrow(575, cy - h3/2, 340, cy - h2/2 - 24))
    frags.append(line(340, cy - h2/2 - 24, 340, cy - h2/2, color=LINE, sw=1.8))
    frags.append(text((340+575)/2, cy - h2/2 - 34, "повторювати, доки якість тримається", size=12, color=MUTED, italic=True))

    frags.append(text(W/2, cy + 78, "різко викинути все й спинитись → якість провалюється;", size=12, color=POS))
    frags.append(text(W/2, cy + 96, "потроху + донавчання → мережа встигає перерозподілити роботу", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "prune-retrain-loop.svg"), W, H, *frags)


# ── Фігура 4 (вставка hist): чому друга похідна бачить те, чого модуль не бачить ─
def fig_curvature():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 26, "Модуль питає «яка вага?», крутизна — «наскільки зросте помилка, як її занулити?»",
                      size=14, bold=True))

    # дві параболи помилки як функції ваги: пласка й крута; одна вага мала, друга велика
    ax0, ay0 = 90, 300      # початок осей лівої панелі
    axw, axh = 240, 210
    frags.append(line(ax0, ay0, ax0 + axw, ay0, color=INK, sw=1.5))          # вісь w
    frags.append(line(ax0, ay0, ax0, ay0 - axh, color=INK, sw=1.5))          # вісь E
    frags.append(text(ax0 + axw, ay0 + 18, "вага w", size=12, color=MUTED))
    frags.append(text(ax0 - 6, ay0 - axh - 6, "помилка E", size=12, color=MUTED, anchor="middle"))

    # пласка парабола: велика вага (далеко від 0), але крутизна мала
    import math
    cx = ax0 + axw*0.62          # мінімум праворуч (вага велика за модулем)
    flat_k = 0.9
    pts = []
    for t in range(0, 101):
        w = ax0 + axw*0.10 + (axw*0.80)*t/100.0
        dx = (w - cx)/40.0
        e = ay0 - 20 - flat_k*40*dx*dx
        if e < ay0 - axh: e = ay0 - axh
        pts.append("%.1f,%.1f" % (w, e))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), NEG))
    frags.append(line(cx, ay0, cx, ay0 - 20, color=MUTED, sw=1, dash="3,3"))
    frags.append(circle(cx, ay0 - 20, 4, fill=NEG, stroke=NEG))
    frags.append(text(ax0 + axw/2, ay0 - axh + 4, "велика вага, ПЛАСКО", size=12, color=NEG, bold=True))
    frags.append(text(ax0 + axw/2, ay0 - axh + 22, "занулиш — помилка майже стоїть", size=11, color=MUTED))

    # права панель: мала вага, круто
    bx0 = 400
    frags.append(line(bx0, ay0, bx0 + axw, ay0, color=INK, sw=1.5))
    frags.append(line(bx0, ay0, bx0, ay0 - axh, color=INK, sw=1.5))
    frags.append(text(bx0 + axw, ay0 + 18, "вага w", size=12, color=MUTED))

    cx2 = bx0 + axw*0.30          # мінімум близько до 0 (вага мала за модулем)
    steep_k = 5.0
    pts2 = []
    for t in range(0, 101):
        w = bx0 + axw*0.10 + (axw*0.80)*t/100.0
        dx = (w - cx2)/40.0
        e = ay0 - 20 - steep_k*40*dx*dx
        if e < ay0 - axh: e = ay0 - axh
        pts2.append("%.1f,%.1f" % (w, e))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts2), POS))
    frags.append(line(cx2, ay0, cx2, ay0 - 20, color=MUTED, sw=1, dash="3,3"))
    frags.append(circle(cx2, ay0 - 20, 4, fill=POS, stroke=POS))
    frags.append(text(bx0 + axw/2, ay0 - axh + 4, "мала вага, КРУТО", size=12, color=POS, bold=True))
    frags.append(text(bx0 + axw/2, ay0 - axh + 22, "занулиш — помилка стрибне", size=11, color=MUTED))

    frags.append(text(W/2, 372, "модуль викинув би саме праву (вона мала) — і схибив би: крутизна каже тримати її",
                      size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "curvature-vs-magnitude.svg"), W, H, *frags)


# ── Фігура 5 (вставка hist): зміна погляду — від «обчесати жир» до «знайти квиток» ─
def fig_viewpoint():
    W, H = 720, 300
    frags = []
    frags.append(text(W/2, 28, "Зміна погляду за тридцять років", size=17, bold=True))

    y = 150
    # часова вісь
    frags.append(line(60, y, 660, y, color=INK, sw=1.5))
    for xx, lab in [(120, "1989"), (300, "1993"), (470, "2015"), (620, "2018")]:
        frags.append(line(xx, y-5, xx, y+5, color=INK, sw=1.5))
        frags.append(text(xx, y + 22, lab, size=12, color=MUTED, bold=True))

    b1,_,_ = textbox(120, y-64, "Optimal\nBrain Damage\nдруга похідна", size=11, pad=7,
                     fill="#eef2fb", stroke=NEG, min_w=118)
    b2,_,_ = textbox(300, y-64, "Optimal\nBrain Surgeon\nповний гессіан", size=11, pad=7,
                     fill="#eef2fb", stroke=NEG, min_w=118)
    b3,_,_ = textbox(470, y-64, "магнітудне +\nдонавчання\n≈9× / 13×", size=11, pad=7,
                     fill="#eef8f1", stroke=FIELD, min_w=118)
    b4,_,_ = textbox(620, y-64, "щасливий\nквиток\nрідке з нуля", size=11, pad=7,
                     fill="#fdf0ee", stroke=POS, min_w=112)
    frags += [b1, b2, b3, b4]

    frags.append(text(230, y + 62, "«велика мережа надлишкова — обчешемо жир»",
                      size=12, color=NEG, italic=True))
    frags.append(text(560, y + 88, "«велика мережа — лотерея: знайдемо готовий малий розв'язок»",
                      size=12, color=POS, italic=True, anchor="end"))

    render(os.path.join(OUT, "pruning-viewpoint.svg"), W, H, *frags)


# ── Фігура (вставка math): виразність = кривина × квадрат ваги (той самий зсув, різна ΔL) ─
def fig_saliency_curvature():
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 26, "Той самий зсув у нуль коштує по-різному — за кривиною дна", size=16, bold=True))

    def panel(x0, k, note, klbl, slbl):
        out = []
        pw, ph = 250, 200
        gy0 = 74
        basey = gy0 + ph
        # осі L і w
        out.append(line(x0, gy0, x0, basey, color=INK, sw=1.6))
        out.append(line(x0, basey, x0 + pw, basey, color=INK, sw=1.6))
        out.append(text(x0 - 6, gy0 + 4, "L", size=13, color=INK, anchor="end", bold=True))
        out.append(text(x0 + pw, basey + 18, "w", size=13, color=INK, bold=True))

        Lmin_px = basey - 20        # рівень дна
        wn0 = 0.62                  # де мінімум по осі (нормовано 0..1)
        amp = 640.0                 # спільний масштаб висоти для обох панелей
        pts = []
        wn = 0.0
        while wn <= 1.0001:
            xp = x0 + wn * pw
            yp = Lmin_px - amp * k * (wn - wn0) ** 2
            if yp < gy0 + 6:
                yp = gy0 + 6
            pts.append((xp, yp))
            wn += 0.02
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, NEG))

        # мінімум (навчена вага) та точка «в нулі» — однаковий екранний зсув
        xmin = x0 + wn0 * pw
        wn_zero = wn0 - 0.42
        xzero = x0 + wn_zero * pw
        yzero = Lmin_px - amp * k * (wn_zero - wn0) ** 2
        if yzero < gy0 + 6:
            yzero = gy0 + 6
        out.append(circle(xmin, Lmin_px, 4.5, fill=NEG, stroke=NEG, sw=1))
        out.append(text(xmin, basey + 18, "w*", size=12, color=INK, italic=True))
        out.append(circle(xzero, yzero, 4.5, fill=POS, stroke=POS, sw=1))
        out.append(text(xzero, basey + 18, "0", size=12, color=POS, bold=True))

        # той самий горизонтальний зсув
        out.append(line(xmin, basey, xmin, Lmin_px, color=MUTED, sw=1, dash="3,3"))
        out.append(arrow(xmin, basey - 8, xzero, basey - 8, color=MUTED, sw=1.4))
        out.append(text((xmin + xzero) / 2, basey - 12, "той самий зсув", size=10, color=MUTED))

        # підйом втрати ΔL
        out.append(line(xzero, Lmin_px, xzero, yzero, color=POS, sw=2, dash="4,3"))
        out.append(text(xzero + 8, (Lmin_px + yzero) / 2 + 4, "ΔL", size=13, color=POS, bold=True, anchor="start"))

        # підписи
        bx, bw, bh = textbox(x0 + pw / 2, basey + 60, note, size=12, pad=8, min_w=232,
                             fill="#f7f9fb", stroke="#d3d7db")
        out.append(bx)
        out.append(text(x0 + pw / 2, basey + 96, klbl, size=12, color=INK))
        out.append(text(x0 + pw / 2, basey + 114, slbl, size=12, color=POS, bold=True))
        return out

    frags += panel(60, k=0.45, note="пласка широка долина",
                   klbl="кривина Hᵢᵢ мала",
                   slbl="ΔL мала → викидати не жаль")
    frags += panel(410, k=4.2, note="вузький крутий яр",
                   klbl="кривина Hᵢᵢ велика",
                   slbl="ΔL велика → вагу берегти")

    render(os.path.join(OUT, "saliency-curvature.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_magnitude()
    fig_structured()
    fig_loop()
    fig_curvature()
    fig_viewpoint()
    fig_saliency_curvature()
    print("figures written to", OUT)
