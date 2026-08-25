# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння дальності й тривалості Бреге».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def polyline(pts, color=INK, sw=2.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


# ── Фігура 1: баланс сил + енергія → відстань ───────────────────────────────
def fig_cruise_energy():
    W, H = 830, 430
    F = []
    cx, cy = 195, 220

    # апарат (вид збоку): фюзеляж, кіль, крило-ребро
    F.append(line(cx - 72, cy, cx + 78, cy, color=INK, sw=7))       # фюзеляж
    F.append(line(cx + 78, cy, cx + 100, cy, color=INK, sw=2.5))    # ніс
    F.append(line(cx - 62, cy, cx - 62, cy - 24, color=INK, sw=5))  # кіль
    F.append(line(cx - 6, cy - 5, cx - 6, cy + 5, color=INK, sw=9)) # ребро крила

    # чотири сили з центру
    F.append(arrow(cx, cy - 6, cx, cy - 96, color=FIELD, sw=3.2))   # підйом
    F.append(text(cx, cy - 108, "Підйом L", size=15, color=FIELD, bold=True))
    F.append(arrow(cx, cy + 6, cx, cy + 96, color=POS, sw=3.2))     # вага
    F.append(text(cx, cy + 120, "Вага W", size=15, color=POS, bold=True))
    F.append(arrow(cx + 14, cy - 18, cx + 120, cy - 18, color=NEG, sw=3.2))  # тяга
    F.append(text(cx + 158, cy - 14, "Тяга T", size=15, color=NEG, bold=True))
    F.append(arrow(cx - 14, cy + 18, cx - 120, cy + 18, color=INK, sw=3.2))  # опір
    F.append(text(cx - 156, cy + 22, "Опір D", size=15, color=INK, bold=True))

    F.append(text(cx, cy + 156, "L = W        T = D", size=15, bold=True, color=MUTED))

    # роздільна вертикаль
    F.append(line(400, 70, 400, 380, color="#d0d5db", sw=1.5, dash="4 5"))

    # права колонка — енергетична бухгалтерія
    xc = 605
    F.append(text(xc, 96, "Пройти R — це робота проти опору,", size=14, color=INK))
    F.append(text(xc, 116, "яку оплачує вся енергія на борту:", size=14, color=INK))
    F.append(textbox(xc, 158, "R  =  E / D", size=17, pad=12, bold=True)[0])
    F.append(text(xc, 210, "опір виражаємо через вагу і якість:", size=14, color=INK))
    F.append(textbox(xc, 250, "D  =  W / (L/D)", size=17, pad=12, bold=True)[0])
    F.append(arrow(xc, 278, xc, 306, color=INK, sw=2.2))
    F.append(textbox(xc, 344, "R  =  E · (L/D) / W", size=17, pad=13,
                     bold=True, fill="#eafaf0", stroke=FIELD)[0])

    render(os.path.join(IMG, "cruise-energy.svg"), W, H, *F,
           title="Звідки береться дальність: енергія ділиться на опір")


# ── Фігура 2: опір і потужність від швидкості → різні оптимальні швидкості ───
def fig_speeds():
    W, H = 850, 500
    F = []
    x0, x1 = 100, 720
    yb, yt = 360, 78          # низ / верх поля графіка
    vmin, vmax = 0.55, 1.5
    cmin, cmax = 0.9, 2.5     # діапазон «відносної ціни»

    def X(v):
        return x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)

    def Y(c):
        return yb - (c - cmin) / (cmax - cmin) * (yb - yt)

    vmp = (1.0 / 3.0) ** 0.25          # швидкість мінімальної потужності
    pmin = 1.0 / vmp + vmp ** 3

    def Dr(v):
        return (1.0 / v ** 2 + v ** 2) / 2.0

    def Pr(v):
        return (1.0 / v + v ** 3) / pmin

    # осі
    F.append(line(x0, yt - 6, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1 + 6, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 92, "швидкість польоту V  →", size=14, color=INK))
    F.append(text(x0 - 8, yt - 16, "відносна ціна (менше — краще)", size=13,
                  color=MUTED, anchor="start"))

    # криві
    dr = [(X(v), Y(Dr(v))) for v in frange(vmin, vmax, 80)]
    pr = [(X(v), Y(Pr(v))) for v in frange(vmin, vmax, 80) if Pr(v) <= cmax]
    F.append(polyline(dr, color=NEG, sw=3))
    F.append(polyline(pr, color=POS, sw=3))
    F.append(text(X(1.5) + 6, Y(Dr(1.5)) + 4, "опір D", size=14, color=NEG,
                  anchor="start", bold=True))
    F.append(text(545, 198, "потужність P = D·V", size=14,
                  color=POS, anchor="middle", bold=True))

    # вертикалі до мінімумів
    F.append(line(X(vmp), Y(Pr(vmp)), X(vmp), yb, color=POS, sw=1.6, dash="4 4"))
    F.append(line(X(1.0), Y(Dr(1.0)), X(1.0), yb, color=NEG, sw=1.6, dash="4 4"))
    F.append(circle(X(vmp), Y(1.0), 5, fill=POS, stroke=POS))
    F.append(circle(X(1.0), Y(1.0), 5, fill=NEG, stroke=NEG))

    # підписи-мітки під віссю
    F.append(fitbox(120, yb + 28, 300, 52,
                    "швидкість найменшої потужності:\nнайдовше в повітрі (гвинт/електро)",
                    size=13, fill="#fdecea", stroke=POS))
    F.append(line(X(vmp), yb, 270, yb + 28, color=POS, sw=1.3, dash="3 3"))
    F.append(fitbox(452, yb + 28, 320, 52,
                    "швидкість найменшого опору = макс L/D:\nнайдалі; для реактивного — найдовше",
                    size=13, fill="#eaf0fd", stroke=NEG))
    F.append(line(X(1.0), yb, 470, yb + 28, color=NEG, sw=1.3, dash="3 3"))

    render(os.path.join(IMG, "range-endurance-speeds.svg"), W, H, *F,
           title="Найдовше і найдалі — на різних швидкостях")


# ── Фігура 3: логарифм відношення ваг → спадна віддача пального ──────────────
def fig_weight_log():
    W, H = 790, 450
    F = []
    x0, x1 = 115, 690
    yb, yt = 360, 90
    rmin, rmax = 1.0, 3.0
    lmax = math.log(rmax)

    def X(r):
        return x0 + (r - rmin) / (rmax - rmin) * (x1 - x0)

    def Y(l):
        return yb - l / (lmax * 1.06) * (yb - yt)

    # осі
    F.append(line(x0, yt - 6, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1 + 6, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 66, "відношення ваг  W₀ / W₁  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 16, "множник дальності  ln(W₀/W₁)", size=13,
                  color=MUTED, anchor="start"))

    # крива логарифма
    curve = [(X(r), Y(math.log(r))) for r in frange(rmin, rmax, 90)]
    F.append(polyline(curve, color=FIELD, sw=3.2))

    # дві опорні точки
    for r, frac, side in [(1.5, "⅓ ваги — пальне", "L"),
                          (2.25, "56 % ваги — пальне", "R")]:
        l = math.log(r)
        F.append(line(x0, Y(l), X(r), Y(l), color=MUTED, sw=1.2, dash="3 4"))
        F.append(line(X(r), yb, X(r), Y(l), color=MUTED, sw=1.2, dash="3 4"))
        F.append(circle(X(r), Y(l), 5, fill=FIELD, stroke=FIELD))
        F.append(text(x0 - 10, Y(l) + 4, "%.2f" % l, size=12, color=INK, anchor="end"))
        tx = X(r) + (10 if side == "R" else -10)
        F.append(text(tx, yb + 20, "%.2f" % r, size=12, color=INK,
                      anchor="start" if side == "R" else "end"))
        if side == "R":
            F.append(text(X(r) + 12, Y(l) - 4, frac, size=11.5, color=MUTED, anchor="start"))
        else:
            F.append(text(X(r), Y(l) - 14, frac, size=11.5, color=MUTED))

    # анотація про подвоєння (у вільному верхньо-лівому куті, над кривою)
    F.append(fitbox(140, 100, 320, 62,
                    "щоб подвоїти дальність (ln з 0.41 до 0.81),\n"
                    "відношення ваг треба звести майже у квадрат:\n1.5 → 2.25",
                    size=12.5, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "weight-ratio-log.svg"), W, H, *F,
           title="Пальне доводиться везти, щоб везти пальне")


# ── Фігура 4 (вставка hist): хроніка появи й канонізації імені ───────────────
def fig_history_timeline():
    W, H = 900, 470
    F = []
    sx = 168                      # x вертикальної спини
    top, bot = 66, 432
    F.append(line(sx, top, sx, bot, color=MUTED, sw=2.5))

    # (y вузла, рік, колір-акцент, заливка картки, обвід картки, текст)
    nodes = [
        (110, "1919", INK, "#eef1f4", "#c2c8cf",
         "Літаки щойно перетнули Атлантику (NC-4, потім Алкок і Браун):\n"
         "питання «як далеко долетить?» стає головним"),
        (206, "1920", NEG, "#eaf0fd", NEG,
         "Джозеф Дж. Коффін (США), NACA Report 69 —\n"
         "перше друковане виведення рівняння дальності"),
        (306, "1923", POS, "#fdecea", POS,
         "Луї Шарль Бреге (Франція) незалежно публікує\n"
         "те саме рівняння у практичному вигляді"),
        (402, "згодом", FIELD, "#eafaf0", FIELD,
         "підручники закріплюють назву «рівняння Бреге» —\n"
         "традицією, а не за правом першості"),
    ]
    cx, cw = sx + 40, 648
    for ny, yr, dot, fill, stroke, txt in nodes:
        nlines = txt.count("\n") + 1
        ch = nlines * 21 + 24
        F.append(fitbox(cx, ny - ch / 2, cw, ch, txt, size=14.5, pad=13,
                        fill=fill, stroke=stroke))
        F.append(line(sx, ny, cx, ny, color=stroke, sw=1.4, dash="3 3"))
        F.append(circle(sx, ny, 7.5, fill=dot, stroke=dot))
        F.append(text(sx - 18, ny + 5, yr, size=15, color=dot, anchor="end", bold=True))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *F,
           title="Як рівняння дальності дістало ім'я Бреге")


def polygon(pts, fill, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    s = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (p, fill, s)


# ── Фігура (вставка math): площа під 1/W = ln(W₀/W₁) ─────────────────────────
def fig_fuel_integral():
    W, H = 820, 450
    F = []
    x0, x1 = 120, 700
    yb, yt = 360, 90
    wlo, whi = 0.88, 1.72          # діапазон осі ваги
    w1, w0 = 1.0, 1.6              # сухий / повний бак
    ymax = 1.22                    # верх осі 1/W

    def X(w):
        return x0 + (w - wlo) / (whi - wlo) * (x1 - x0)

    def Y(v):
        return yb - v / ymax * (yb - yt)

    # заштрихована площа під 1/W від w1 до w0
    N = 60
    top = [(X(w1 + (w0 - w1) * i / N), Y(1.0 / (w1 + (w0 - w1) * i / N)))
           for i in range(N + 1)]
    area = [(X(w1), yb)] + top + [(X(w0), yb)]
    F.append(polygon(area, fill="#eafaf0"))

    # одна вузька смужка dW біля w = 1.28
    ws, dw = 1.28, 0.055
    strip = [(X(ws - dw / 2), yb), (X(ws - dw / 2), Y(1.0 / ws)),
             (X(ws + dw / 2), Y(1.0 / ws)), (X(ws + dw / 2), yb)]
    F.append(polygon(strip, fill="#bfe9cf", stroke=FIELD, sw=1.2))
    F.append(text(X(ws), yb + 20, "dW", size=12, color=FIELD, bold=True))
    F.append(text(X(ws) + 78, Y(1.0 / ws) - 6,
                  "смужка = dW/W", size=12.5, color=FIELD, anchor="start"))
    F.append(line(X(ws) + 6, Y(1.0 / ws) - 8, X(ws) + 74, Y(1.0 / ws) - 8,
                  color=FIELD, sw=1.1, dash="3 3"))

    # крива 1/W (ширша за площу — контекст)
    curve = [(X(w), Y(1.0 / w)) for w in
             [wlo + (whi - wlo) * i / 90 for i in range(91)] if 1.0 / w <= ymax]
    F.append(polyline(curve, color=INK, sw=2.6))

    # осі
    F.append(line(x0, yt - 8, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1 + 8, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 66,
                  "вага апарата W:  від сухого W₁ до повного W₀  →", size=14, color=INK))
    F.append(text(x0 - 10, yt - 18, "ціна кроку  1/W", size=13, color=MUTED, anchor="start"))

    # мітки W1, W0
    for w, lab, col in [(w1, "W₁", NEG), (w0, "W₀", POS)]:
        F.append(line(X(w), yb, X(w), Y(1.0 / w), color=col, sw=1.4, dash="4 4"))
        F.append(circle(X(w), Y(1.0 / w), 4.5, fill=col, stroke=col))
        F.append(text(X(w), yb + 42, lab, size=14, color=col, bold=True))

    # підпис площі
    F.append(textbox(432, 168, "площа = ∫ dW/W = ln(W₀/W₁)",
                     size=15, pad=11, bold=True, fill="#eafaf0", stroke=FIELD)[0])

    render(os.path.join(IMG, "fuel-integral-log.svg"), W, H, *F,
           title="Дальність — це площа під кривою 1/W")


# ── Фігура (вставка math): три оптимуми на поляре опору ──────────────────────
def fig_drag_polar_optima():
    W, H = 990, 500
    F = []
    x0, x1 = 92, 560
    yb, yt = 410, 66
    cd0, k = 0.025, 0.045
    cdmax, clmax = 0.12, 1.5

    def X(cd):
        return x0 + cd / cdmax * (x1 - x0)

    def Y(cl):
        return yb - cl / clmax * (yb - yt)

    cl_md = (cd0 / k) ** 0.5
    pts = {
        "md":  (cd0 + k * cl_md ** 2, cl_md, NEG, "①", 120),
        "jet": (cd0 + k * (cl_md / 3 ** 0.5) ** 2, cl_md / 3 ** 0.5, FIELD, "②", 250),
        "mp":  (cd0 + k * (cl_md * 3 ** 0.5) ** 2, cl_md * 3 ** 0.5, POS, "③", 372),
    }

    # осі
    F.append(line(x0, yt - 6, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1 + 8, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 40, "опір  CD  →", size=14, color=INK))
    F.append(text(x0 - 8, yt - 16, "підйом  CL", size=13, color=MUTED, anchor="start"))

    # паразитне дно CD0
    F.append(line(X(cd0), yb, X(cd0), yt + 4, color=MUTED, sw=1.3, dash="4 4"))
    F.append(text(X(cd0), yb + 22, "CD₀", size=12.5, color=MUTED))

    # дотична з початку координат (нахил = (L/D)max), торкається в точці md
    slope = cl_md / (cd0 + k * cl_md ** 2)
    cd_end = 0.066
    F.append(line(X(0), Y(0), X(cd_end), Y(slope * cd_end),
                  color=NEG, sw=1.6, dash="5 4"))
    F.append(text(X(cd_end) + 6, Y(slope * cd_end) - 4,
                  "нахил = (L/D)max", size=12, color=NEG, anchor="start"))

    # поляра CD = CD0 + k·CL²
    polar = [(X(cd0 + k * cl ** 2), Y(cl)) for cl in
             [1.46 * i / 90 for i in range(91)] if cd0 + k * cl ** 2 <= cdmax]
    F.append(polyline(polar, color=INK, sw=3))

    # три робочі точки + номери + лідери до легенди
    for cd, cl, col, num, ly in pts.values():
        F.append(line(X(cd) + 7, Y(cl), 600, ly, color=col, sw=1.1, dash="3 4"))
        F.append(circle(X(cd), Y(cl), 6, fill=col, stroke=col))
        F.append(text(X(cd) - 16, Y(cl) + 5, num, size=15, color=col, bold=True))

    # легенда праворуч
    F.append(fitbox(600, 92, 378, 78,
                    "①  макс L/D   (CL/CD)\n"
                    "k·CL² = CD₀ — індуктивний = паразитний\n"
                    "дальність гвинта, тривалість реактивного:  V = V_md",
                    size=12.5, fill="#eaf0fd", stroke=NEG))
    F.append(fitbox(600, 222, 378, 70,
                    "②  дальність реактивного   (CL^0.5/CD)\n"
                    "CD₀ = 3·k·CL² — паразитний утричі більший\n"
                    "мала CL → швидше:   V ≈ 1.32·V_md",
                    size=12.5, fill="#eafaf0", stroke=FIELD))
    F.append(fitbox(600, 344, 378, 78,
                    "③  тривалість гвинта / мін потужність   (CL^1.5/CD)\n"
                    "k·CL² = 3·CD₀ — індуктивний утричі більший\n"
                    "велика CL → повільніше:   V ≈ 0.76·V_md",
                    size=12.5, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, "drag-polar-optima.svg"), W, H, *F,
           title="Три оптимуми на одній поляре опору")


# ── Фігура (вставка proj): устрій калькулятора — від входів до відповіді ──────
def fig_calc_map():
    W, H = 1000, 470
    F = []
    neu, grn, red, blu = "#eef1f4", "#eafaf0", "#fdecea", "#eaf0fd"

    # заголовки смуг
    F.append(text(141, 78, "ВХІД", size=15, bold=True, color=MUTED))
    F.append(text(396, 78, "ПОЛЯРА  →  3 CL", size=15, bold=True, color=MUTED))
    F.append(text(916, 78, "ВИХІД", size=15, bold=True, color=MUTED))

    # ВХІД — що подаємо
    F.append(fitbox(36, 95, 210, 200,
                    "маса  m\n"
                    "запас: частка або маса\n"
                    "e*   або   SFC (c_p, c_t)\n"
                    "ККД тракту  η\n"
                    "поляра  CD₀, k, S\n"
                    "густина  ρ",
                    size=14, fill=neu, stroke="#c2c8cf"))

    # ПОЛЯРА → три коефіцієнти підйому
    F.append(fitbox(290, 120, 218, 150,
                    "CL_md → макс L/D\n"
                    "CL_mp → мін потужн.\n"
                    "CL_jr → дальн. струменя\n"
                    "+ швидкість кожної",
                    size=13.5, fill=neu, stroke="#c2c8cf"))

    # гілка СТАЛОЇ ваги — акумулятор
    F.append(fitbox(540, 96, 266, 112,
                    "СТАЛА вага — акумулятор\n"
                    "R = e*·(m_bat/m)·η·(L/D) / g\n"
                    "лінійно, без логарифма\n"
                    "тривалість = E_корисна / P_мін",
                    size=13, fill=grn, stroke=FIELD))

    # гілка ТАНУЧОЇ ваги — пальне
    F.append(fitbox(540, 252, 266, 150,
                    "ТАНЕ вага — пальне\n"
                    "R ∝ ln(W₀ / W₁)\n"
                    "гвинт:  E ∝ 1/√W₁ − 1/√W₀\n"
                    "струмінь:  R на CL^0.5/CD\n"
                    "крейсер-набір vs стала висота",
                    size=13, fill=red, stroke=POS))

    # ВИХІД — що дістаємо
    F.append(fitbox(848, 150, 134, 170,
                    "дальність R\n"
                    "тривалість E\n"
                    "V найдальшої\n"
                    "V найдовшої",
                    size=13.5, fill=blu, stroke=NEG))

    # стрілки потоку
    F.append(arrow(250, 195, 288, 195, color=INK, sw=2.2))
    F.append(arrow(510, 166, 538, 150, color=FIELD, sw=2.2))
    F.append(arrow(510, 226, 538, 300, color=POS, sw=2.2))
    F.append(arrow(809, 150, 846, 212, color=FIELD, sw=2.0))
    F.append(arrow(809, 300, 846, 258, color=POS, sw=2.0))

    render(os.path.join(IMG, "calc-map.svg"), W, H, *F,
           title="Устрій калькулятора: від входів до відповіді")


if __name__ == "__main__":
    fig_cruise_energy()
    fig_speeds()
    fig_weight_log()
    fig_history_timeline()
    fig_fuel_integral()
    fig_drag_polar_optima()
    fig_calc_map()
    print("OK: 7 SVG ->", IMG)
