# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три режими обслуговування ──────────────────────────────────────
def fig_regimes():
    W, H = 720, 300
    f = []
    f.append(text(W/2, 26, "Три способи вирішувати, коли обслуговувати", size=17, bold=True))

    col_w = 200
    xs = [40, 260, 480]
    labels = [
        ("До поломки", "чекаємо, поки стане;\nремонт найдорожчий,\nчасто аварійний", POS, "#fdecea"),
        ("За розкладом", "міняємо «про запас»\nкожні N годин;\nвикидаємо ще живе", MUTED, "#f4f6f8"),
        ("За станом", "слухаємо машину,\nдіємо саме тоді,\nколи вона просить", FIELD, "#eafaf0"),
    ]
    for x, (title, body, col, bg) in zip(xs, labels):
        f.append(rect(x, 56, col_w, 150, fill=bg, stroke=col, sw=2, rx=8))
        f.append(text(x+col_w/2, 84, title, size=15, bold=True, color=col))
        f.append(mtext(x+col_w/2, 116, body, size=12, color=INK, lh=1.3))

    # шкала «дорого / марно / вчасно»
    f.append(text(140, 236, "дорого і раптово", size=12, color=POS))
    f.append(text(360, 236, "надійно, але марнотратно", size=12, color=MUTED))
    f.append(text(580, 236, "вчасно й ощадливо", size=12, color=FIELD, bold=True))

    f.append(text(W/2, 274, "ML на давачі вібрації робить можливим саме третій — прямо на машині, без сервера",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'maintenance-regimes.svg'), W, H, *f)


# ── Фігура 2: конвеєр від акселерометра до вердикту ──────────────────────────
def fig_pipeline():
    W, H = 840, 300
    f = []
    f.append(text(W/2, 26, "Шлях від тряски до вердикту", size=17, bold=True))

    y = 120
    bh = 66
    # блоки конвеєра
    stages = [
        (30,  120, "Акселерометр\n(x,y,z, кГц)", FILL, LINE),
        (188, 130, "Вікно +\nспектр (FFT)", "#eef3ff", NEG),
        (356, 120, "Вектор ознак\n(смуги, RMS)", FILL, LINE),
        (516, 130, "Автокодер\nна борту", "#eafaf0", FIELD),
    ]
    xc = []
    for x, w, s, fill, col in stages:
        f.append(rect(x, y-bh/2, w, bh, fill=fill, stroke=col, sw=2, rx=8))
        f.append(mtext(x+w/2, y-4, s, size=12.5, color=INK, lh=1.25, bold=True))
        xc.append((x, w))
    # стрілки між блоками
    for i in range(len(stages)-1):
        x0 = xc[i][0]+xc[i][1]
        x1 = xc[i+1][0]
        f.append(arrow(x0+4, y, x1-4, y))

    # вихід автокодера → похибка → поріг
    ax = 516+130
    f.append(arrow(ax+4, y, ax+40, y))
    # похибка відновлення
    f.append(rect(ax+40, y-30, 74, 60, fill="#fff7e6", stroke=POS, sw=2, rx=8))
    f.append(mtext(ax+77, y-4, "похибка\nвідновлення", size=11.5, color=INK, lh=1.2, bold=True))

    # нижній рядок: поріг → норма / тривога
    f.append(arrow(ax+77, y+30, ax+77, y+58))
    f.append(rect(ax-4, y+58, 162, 40, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(ax+77, y+72, "поріг", size=12, bold=True))
    f.append(text(ax+77, y+90, "мала → норма · велика → тривога", size=10.5, color=MUTED))

    # підпис: що на чипі
    f.append(line(20, 200, W-20, 200, color=MUTED, sw=1, dash="4 4"))
    f.append(text(W/2, 224, "усе, що вище пунктиру, крутиться на самому мікроконтролері — назовні йде лише «норма/тривога»",
                  size=12, color=INK, italic=True))
    f.append(text(W/2, 250, "модель бачила ЛИШЕ здорову машину; усе несхоже на здорове дає велику похибку",
                  size=12, color=FIELD))
    render(os.path.join(IMG, 'vibration-pipeline.svg'), W, H, *f)


# ── Фігура 3: чому похибка відновлення ловить нове ───────────────────────────
def fig_reconstruction():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Автокодер відновлює звичне добре, незвичне — погано", size=16.5, bold=True))

    # два ряди: норма і аномалія
    def band(x0, base, amp, jag, col):
        # проста «спектральна» лінія зі стовпчиків
        pts = []
        n = 22
        for i in range(n):
            h = amp*(0.4+0.6*abs(math.sin(i*0.7+jag)))*(1.0 if i not in (7,14) else 1.4)
            pts.append((x0+i*7, base-h))
        bars = []
        for (px, py) in pts:
            bars.append(line(px, base, px, py, color=col, sw=3))
        return "".join(bars)

    # НОРМА
    yN = 120
    f.append(text(60, yN-64, "здорова машина", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(70, yN+8, "вхід", size=11, color=MUTED, anchor="middle"))
    f.append(band(40, yN, 44, 0.0, NEG))
    f.append(arrow(210, yN-20, 250, yN-20))
    f.append(rect(250, yN-46, 74, 52, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    f.append(mtext(287, yN-24, "авто-\nкодер", size=11.5, bold=True, lh=1.2))
    f.append(arrow(324, yN-20, 364, yN-20))
    f.append(text(400, yN+8, "відновлення", size=11, color=MUTED, anchor="middle"))
    f.append(band(360, yN, 42, 0.05, FIELD))
    f.append(text(600, yN-20, "майже збіглося", size=12, color=FIELD, bold=True, anchor="middle"))
    f.append(text(600, yN+2, "→ мала похибка", size=12, color=FIELD, anchor="middle"))

    # АНОМАЛІЯ
    yA = 250
    f.append(text(60, yA-64, "підшипник сиплеться", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(70, yA+8, "вхід", size=11, color=MUTED, anchor="middle"))
    # у вхід додаємо різкий пік — «нова» гармоніка
    f.append(band(40, yA, 44, 1.1, NEG))
    f.append(line(40+18*7, yA, 40+18*7, yA-72, color=POS, sw=4))
    f.append(arrow(210, yA-20, 250, yA-20))
    f.append(rect(250, yA-46, 74, 52, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    f.append(mtext(287, yA-24, "авто-\nкодер", size=11.5, bold=True, lh=1.2))
    f.append(arrow(324, yA-20, 364, yA-20))
    f.append(text(400, yA+8, "відновлення", size=11, color=MUTED, anchor="middle"))
    # відновлення без піка — кодер такого не вчив
    f.append(band(360, yA, 42, 1.1, FIELD))
    f.append(text(600, yA-20, "піка немає", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(600, yA+2, "→ велика похибка", size=12, color=POS, anchor="middle"))

    f.append(line(20, 300, W-20, 300, color=MUTED, sw=1, dash="4 4"))
    f.append(text(W/2, 324, "кодер уміє малювати лише звичне; нову гармоніку він відтворити не може — і сам себе видає",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'reconstruction-error.svg'), W, H, *f)


# ── Фігура 4 (вставка math): розподіл похибки на здоровій вибірці + поріг ─────
def fig_error_distribution():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Похибка здорової машини — хмарка, а не нуль", size=17, bold=True))

    # осі
    x0, y0 = 70, 250      # початок осей
    xW, yH = 560, 180     # довжина осей
    f.append(line(x0, y0, x0+xW, y0, color=INK, sw=2))          # вісь X
    f.append(line(x0, y0, x0, y0-yH, color=INK, sw=2))          # вісь Y
    f.append(text(x0+xW, y0+22, "похибка відновлення (MSE)", size=12, color=MUTED, anchor="end"))
    f.append(text(x0-8, y0-yH, "як часто", size=12, color=MUTED, anchor="end"))

    # горб (асиметричний: щільний центр, важчий правий хвіст) як гістограма-стовпчики
    import math as _m
    mu_x = x0 + 175       # позиція μ на осі
    sig  = 46             # σ у пікселях
    def dens(xpix):
        z = (xpix - mu_x) / sig
        # лог-нормальна-подібна: горб з правим хвостом
        base = _m.exp(-0.5 * z * z)
        tail = 0.10 * _m.exp(-0.5 * ((xpix - mu_x)/(3.2*sig))**2) if xpix > mu_x else 0.0
        return base + tail
    nb = 46
    bw = xW / nb
    peak = max(dens(x0 + (i+0.5)*bw) for i in range(nb))
    for i in range(nb):
        xc = x0 + (i+0.5)*bw
        h = (dens(xc)/peak) * (yH-20)
        col = POS if xc > mu_x + 3*sig else "#bcd4ea"
        f.append(rect(xc-bw/2+0.6, y0-h, bw-1.2, h, fill=col, stroke="none", sw=0, rx=1))

    # μ
    f.append(line(mu_x, y0, mu_x, y0-yH+8, color=NEG, sw=2, dash="5 4"))
    f.append(text(mu_x, y0-yH-2, "μ  (центр)", size=12.5, color=NEG, bold=True))

    # ширина ±σ (стрілка під горбом)
    yb = y0 - 8
    f.append(line(mu_x-sig, yb, mu_x+sig, yb, color=FIELD, sw=2))
    f.append(line(mu_x-sig, yb-5, mu_x-sig, yb+5, color=FIELD, sw=2))
    f.append(line(mu_x+sig, yb-5, mu_x+sig, yb+5, color=FIELD, sw=2))
    f.append(text(mu_x, yb-9, "σ", size=13, color=FIELD, bold=True))

    # поріг μ + k·σ
    thr = mu_x + 3*sig
    f.append(line(thr, y0, thr, y0-yH, color=POS, sw=2.5))
    f.append(text(thr+4, y0-yH+6, "поріг", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(thr+4, y0-yH+24, "μ + k·σ", size=12, color=POS, anchor="start"))

    # зони
    f.append(text((x0+thr)/2, y0-yH+40, "НОРМА", size=13, color=FIELD, bold=True))
    f.append(text(thr+52, y0-58, "ТРИВОГА", size=12.5, color=POS, bold=True))

    f.append(text(W/2, y0+58,
                  "поріг ставлять не «між нулем і великим», а на правому хвості здорової хмарки: k керує тим, як далеко",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'error-distribution.svg'), W, H, *f)


# ── Фігура 5 (вставка math): два накладені горби і компроміс порога ──────────
def fig_threshold_tradeoff():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Поріг лише пересуває лінію між двома хвостами", size=17, bold=True))

    import math as _m
    x0, y0 = 60, 250
    xW, yH = 600, 180
    f.append(line(x0, y0, x0+xW, y0, color=INK, sw=2))
    f.append(text(x0+xW, y0+22, "похибка відновлення", size=12, color=MUTED, anchor="end"))

    muH = x0 + 210        # центр здорового
    muD = x0 + 360        # центр дефектного (правіше й ширше)
    sH, sD = 52, 78
    thr = x0 + 300        # поріг між горбами

    def gauss(xp, mu, s):
        z = (xp - mu)/s
        return _m.exp(-0.5*z*z)

    npt = 240
    def curve(mu, s, scale):
        pts = []
        for i in range(npt+1):
            xp = x0 + i*(xW/npt)
            yp = y0 - gauss(xp, mu, s)*scale
            pts.append((xp, yp))
        return pts

    scaleH, scaleD = yH-30, (yH-30)*0.82
    curH = curve(muH, sH, scaleH)
    curD = curve(muD, sD, scaleD)

    # заливка хвостів: здоровий праворуч від порога (хибні тривоги, червоний),
    # дефектний ліворуч від порога (пропущені відмови, синій)
    def poly_fill(pts, x_from, x_to, base_y, fill):
        seg = [(x, y) for (x, y) in pts if x_from-0.5 <= x <= x_to+0.5]
        if not seg:
            return ""
        d = "M %.1f %.1f " % (seg[0][0], base_y)
        for (x, y) in seg:
            d += "L %.1f %.1f " % (x, y)
        d += "L %.1f %.1f Z" % (seg[-1][0], base_y)
        return '<path d="%s" fill="%s" fill-opacity="0.30" stroke="none"/>' % (d, fill)

    f.append(poly_fill(curH, thr, x0+xW, y0, POS))    # хибні тривоги
    f.append(poly_fill(curD, x0, thr, y0, NEG))       # пропущені відмови

    # самі криві
    def polyline(pts, col):
        d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, col)
    f.append(polyline(curH, FIELD))
    f.append(polyline(curD, POS))

    # підписи горбів
    f.append(text(muH, y0-scaleH-8, "здорова машина", size=12.5, color=FIELD, bold=True))
    f.append(text(muD+6, y0-scaleD-8, "є дефект", size=12.5, color=POS, bold=True))

    # поріг
    f.append(line(thr, y0, thr, y0-yH+4, color=INK, sw=2.5, dash="6 4"))
    f.append(text(thr, y0-yH-2, "поріг", size=13, color=INK, bold=True))

    # виноски на хвости
    f.append(text(thr+58, y0-40, "хибні тривоги", size=11.5, color=POS, bold=True))
    f.append(text(thr-64, y0-40, "пропущені", size=11.5, color=NEG, bold=True, anchor="end"))
    f.append(text(thr-64, y0-25, "відмови", size=11.5, color=NEG, bold=True, anchor="end"))

    f.append(text(W/2, y0+58,
                  "зсунути поріг = зменшити один хвіст рівно за рахунок другого; прибрати обидва — лише розвівши горби",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'threshold-tradeoff.svg'), W, H, *f)


# ── Фігура 6 (detailed): модуляція — дефект ховається у високочастотному дзвоні ─
def fig_bearing_modulation():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "Дефект підшипника: не пік на BPFO, а модуляція дзвону", size=16, bold=True))

    # ── ЛІВА панель: сигнал у часі ──
    lx, lw = 40, 320
    f.append(text(lx + lw/2, 58, "у часі: серія коротких дзвонів", size=12.5, color=MUTED))
    bx0, by0, bxW, byH = lx, 250, lw, 150
    f.append(line(bx0, by0, bx0 + bxW, by0, color=INK, sw=1.5))       # вісь часу
    f.append(text(bx0 + bxW, by0 + 20, "час", size=11, color=MUTED, anchor="end"))
    # фоновий шум + три сплески-дзвони, розставлені з проміжком BPFO
    import math as _m
    prev = None
    for i in range(bxW):
        xp = bx0 + i
        base = 4.0 * _m.sin(i * 0.9) * (0.4 + 0.3 * _m.sin(i * 0.13))
        # три дзвони на 25%, 55%, 85% ширини — загасаючий високочастотний пакет
        burst = 0.0
        for c in (0.25, 0.55, 0.85):
            d = i - bxW * c
            if 0 <= d < 46:
                burst += 46.0 * _m.exp(-d / 12.0) * _m.sin(d * 1.15)
        yv = by0 - 24 - (base + burst)
        if prev is not None:
            f.append(line(prev[0], prev[1], xp, yv, color=NEG, sw=1.2))
        prev = (xp, yv)
    # позначки проміжку між дзвонами = 1/BPFO
    for c in (0.25, 0.55):
        x1 = bx0 + bxW * c
        x2 = bx0 + bxW * (c + 0.30)
        yb = by0 + 6
        f.append(line(x1, yb, x2, yb, color=POS, sw=1.5))
        f.append(line(x1, yb - 4, x1, yb + 4, color=POS, sw=1.5))
        f.append(line(x2, yb - 4, x2, yb + 4, color=POS, sw=1.5))
    f.append(text(bx0 + bxW * 0.55, by0 + 34, "проміжок = 1 / BPFO", size=11, color=POS, bold=True))

    # ── ПРАВА панель: спектр сирого сигналу ──
    rx0, rw = 420, 300
    f.append(text(rx0 + rw/2, 58, "спектр сирого сигналу", size=12.5, color=MUTED))
    sx0, sy0, sxW, syH = rx0, 250, rw, 150
    f.append(line(sx0, sy0, sx0 + sxW, sy0, color=INK, sw=1.5))       # вісь частоти
    f.append(line(sx0, sy0, sx0, sy0 - syH, color=INK, sw=1.5))       # вісь амплітуди
    f.append(text(sx0 + sxW, sy0 + 20, "частота", size=11, color=MUTED, anchor="end"))
    # мала «позначка» BPFO низько зліва — майже нічого
    bpfo_x = sx0 + 34
    f.append(line(bpfo_x, sy0, bpfo_x, sy0 - 16, color=POS, sw=2))
    f.append(text(bpfo_x, sy0 + 20, "BPFO", size=10.5, color=POS, anchor="middle"))
    f.append(text(bpfo_x + 6, sy0 - 22, "ледь видно", size=10, color=POS, anchor="start"))
    # велика купина на резонансі корпусу справа-вгорі + бічні лінії
    res_x = sx0 + sxW * 0.66
    for i in range(-70, 71):
        xp = res_x + i
        h = 96.0 * _m.exp(-(i * i) / (2 * 26.0 * 26.0))
        f.append(line(xp, sy0, xp, sy0 - h, color="#bcd4ea", sw=1.0))
    # бічні складові на ±BPFO від носія
    for s in (-2, -1, 1, 2):
        xp = res_x + s * 22
        f.append(line(xp, sy0, xp, sy0 - 40, color=FIELD, sw=1.4))
    f.append(text(res_x, sy0 - 108, "резонанс корпусу", size=11, color=NEG, bold=True, anchor="middle"))
    f.append(text(res_x, sy0 - 92, "(2–10 кГц)", size=10, color=NEG, anchor="middle"))
    f.append(text(res_x + 44, sy0 - 34, "бічні лінії ±BPFO", size=9.5, color=FIELD, anchor="start"))

    f.append(text(W/2, 332,
                  "інформація про дефект — не в положенні піка, а в тому, як швидко пульсує високочастотний дзвін",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'bearing-modulation.svg'), W, H, *f)


# ── Фігура 7 (detailed): багатовид здоров'я і проєкція автокодера ─────────────
def fig_manifold():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Автокодер притягує будь-який вхід на багатовид здоров'я", size=15.5, bold=True))

    import math as _m
    # намалюємо вигнуту «поверхню» здоров'я як смугу з двох близьких кривих
    cx0, cxW = 90, 540
    def surf_y(t):   # t від 0 до 1
        return 250 - 70 * _m.sin(t * _m.pi * 0.9) - 20 * t
    # верхня і нижня межі тонкої смуги
    up, lo = [], []
    for i in range(0, 101):
        t = i / 100.0
        xp = cx0 + t * cxW
        yc = surf_y(t)
        up.append((xp, yc - 9))
        lo.append((xp, yc + 9))
    band_pts = up + lo[::-1]
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in band_pts) + " Z"
    f.append('<path d="%s" fill="#eafaf0" stroke="%s" stroke-width="1.5"/>' % (d, FIELD))
    # серединна лінія
    mid = "M " + " L ".join("%.1f %.1f" % (cx0 + i/100.0*cxW, surf_y(i/100.0)) for i in range(101))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (mid, FIELD))
    f.append(text(cx0 + cxW*0.20, surf_y(0.20) - 22, "багатовид здоров'я", size=13, color=FIELD, bold=True, anchor="middle"))

    # розсип здорових точок ПРЯМО на смузі
    for t in (0.12, 0.28, 0.40, 0.52, 0.63, 0.74, 0.86):
        xp = cx0 + t * cxW
        yp = surf_y(t) + (6 if int(t*100) % 2 else -5)
        f.append(circle(xp, yp, 3.2, fill=FIELD, stroke=FIELD, sw=1))

    # ── здорова точка: коротка проєкція ──
    hx, hy = cx0 + 0.34 * cxW, surf_y(0.34) - 4
    f.append(circle(hx, hy - 26, 4.5, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(arrow(hx, hy - 22, hx, surf_y(0.34) - 2, color=FIELD, sw=1.6))
    f.append(text(hx - 8, hy - 34, "здоровий вхід", size=11, color=FIELD, bold=True, anchor="end"))
    f.append(text(hx + 10, hy - 12, "мала", size=10, color=FIELD, anchor="start"))
    f.append(text(hx + 10, hy + 0, "похибка", size=10, color=FIELD, anchor="start"))

    # ── хвора точка: далеко вбік, довга проєкція ──
    dx, dy = cx0 + 0.70 * cxW, 92
    proj_x, proj_y = cx0 + 0.70 * cxW, surf_y(0.70)
    f.append(arrow(dx, dy + 6, proj_x, proj_y - 4, color=POS, sw=2))
    f.append(circle(dx, dy, 5.5, fill="#fdecea", stroke=POS, sw=2.5))
    f.append(text(dx + 10, dy - 4, "вхід із дефектом", size=11.5, color=POS, bold=True, anchor="start"))
    f.append(text(dx + 10, dy + 12, "(стирчить із поверхні)", size=10, color=POS, anchor="start"))
    f.append(text((dx + proj_x)/2 + 12, (dy + proj_y)/2, "велика похибка", size=11, color=POS, bold=True, anchor="start"))
    f.append(text((dx + proj_x)/2 + 12, (dy + proj_y)/2 + 15, "= відстань до здоров'я", size=10, color=POS, anchor="start"))

    f.append(text(W/2, 352,
                  "похибка відновлення = відстань від входу до тонкої поверхні всього, що машина знає про своє здоров'я",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'manifold-projection.svg'), W, H, *f)


# ── Фігура 8 (вставка math): рівні правдоподібності — кола проти еліпсів ──────
def fig_likelihood_contours():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Форма шуму диктує форму «однаково близького»", size=17, bold=True))

    import math as _m

    def panel(cx, title, sx, sy, note, note_col):
        g = []
        cy = 235
        # заголовок панелі
        g.append(text(cx, 62, title, size=14, bold=True))
        # осі ознак (кінці підписуємо ЗБОКУ, щоб лінія не різала напис)
        axL = 128
        g.append(line(cx - axL, cy, cx + axL, cy, color=MUTED, sw=1.2))
        g.append(line(cx, cy + axL*0.74, cx, cy - axL*0.74, color=MUTED, sw=1.2))
        g.append(text(cx + axL + 4, cy - 6, "смуга 1", size=10.5, color=MUTED, anchor="end"))
        g.append(text(cx + 8, cy - axL*0.74 - 4, "смуга 2", size=10.5, color=MUTED, anchor="start"))
        # три кільця рівної правдоподібності (еліпси з півосями sx,sy)
        for r in (1.0, 2.0, 3.0):
            g.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                     'fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="%s"/>'
                     % (cx, cy, sx*r, sy*r, FIELD, "1 0" if r == 1.0 else "4 4"))
        # центр = відновлення x̂ (підпис ліворуч-униз, поза всіма лініями)
        g.append(circle(cx, cy, 3.5, fill=FIELD, stroke=FIELD, sw=1))
        g.append(text(cx - 9, cy + 15, "x̂", size=12, color=FIELD, bold=True, italic=True, anchor="end"))
        # дві пробні точки на ОДНАКОВІЙ евклідовій відстані d від центру, ПО ДІАГОНАЛЯХ,
        # щоб пунктирні поводки не лягали на осі й підписи:
        d = 80
        s45 = d * 0.7071
        # A — праворуч-угору (переважно вздовж смуги 1)
        ax, ay = cx + d*0.94, cy - d*0.34
        # B — ліворуч-угору (переважно вздовж смуги 2)
        bx, by = cx - d*0.34, cy - d*0.94
        for (px, py) in ((ax, ay), (bx, by)):
            g.append(line(cx, cy, px, py, color=INK, sw=1.3, dash="2 3"))
            g.append(plus(px, py, 7))
        g.append(text(ax + 12, ay + 4, "A", size=12, color=POS, bold=True, anchor="start"))
        g.append(text(bx - 12, by + 2, "B", size=12, color=POS, bold=True, anchor="end"))
        # підпис-нота під панеллю (у своїй рамці, щоб не накладалось)
        box, bw, bh = textbox(cx, 372, note, size=11.5, color=note_col, bold=True,
                              fill="#f7fbff", stroke=note_col, pad=9)
        g.append(box)
        return "".join(g)

    # ЛІВА панель — спільне σ: кола, A і B однаково далеко
    f.append(panel(200, "Спільне σ по всіх смугах",
                   64, 64,
                   "кола: A і B однаково\nдалекі → проста MSE", FIELD))
    # ПРАВА панель — різні σ: еліпс, B (уздовж вузької смуги) «голосніший»
    f.append(panel(560, "Різні σᵢ по смугах",
                   96, 44,
                   "еліпс: B перетнув більше\nкілець → зважена похибка", POS))

    # роздільник
    f.append(line(W/2, 52, W/2, 340, color="#e5e7eb", sw=1))

    f.append(text(W/2, 410,
                  "A і B — на ОДНАКОВІЙ евклідовій відстані від x̂; що з них «дивніше», вирішує σ кожної смуги",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, 'likelihood-contours.svg'), W, H, *f)


if __name__ == '__main__':
    fig_regimes()
    fig_pipeline()
    fig_reconstruction()
    fig_error_distribution()
    fig_threshold_tradeoff()
    fig_bearing_modulation()
    fig_manifold()
    fig_likelihood_contours()
    print("ok")
