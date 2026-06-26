# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Цілісність сигналу (signal integrity)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOOD = FIELD        # «чистий» сигнал
BAD  = POS          # спотворення, небезпека
WAVE = NEG          # хвиля / лінія


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ── 1. Цифровий сигнал — насправді аналоговий ────────────────────────────────
def fig_real_signal():
    W, H = 760, 380
    el = []
    el.append(text(W/2, 26, "Цифровий сигнал — це аналоговий процес", size=17, bold=True))

    # дві осі поряд: ідеал ліворуч, реальність праворуч
    def axes(x0, y0, w, h, caption):
        out = line(x0, y0, x0, y0 - h, MUTED, 1.2)          # вертикальна
        out += line(x0, y0, x0 + w, y0, MUTED, 1.2)          # горизонтальна (час)
        out += line(x0 - 6, y0 - h + 8, x0 + w, y0 - h + 8, MUTED, 1.0, dash="3,4")  # рівень «1»
        out += text(x0 - 10, y0 - h + 12, "Vᴴ", size=12, color=MUTED, anchor="end")
        out += text(x0 - 10, y0 + 4, "0", size=12, color=MUTED, anchor="end")
        out += text(x0 + w/2, y0 + 26, caption, size=13, anchor="middle")
        return out

    lo, hi = 0, 150
    # ── ідеал ──
    bx, by = 80, 300
    el.append(axes(bx, by, 300, hi, "як ми його уявляємо"))
    top = by - hi + 8
    bot = by
    ideal = [(bx, bot), (bx+40, bot), (bx+40, top), (bx+150, top),
             (bx+150, bot), (bx+260, bot), (bx+260, top), (bx+300, top)]
    el.append(polyline(ideal, GOOD, 2.4))
    el.append(text(bx+150, top - 12, "миттєві фронти", size=11, color=GOOD))

    # ── реальність: скінченний фронт + дзвін ──
    rx, ry = 430, 300
    el.append(axes(rx, ry, 300, hi, "як він біжить доріжкою"))
    top = ry - hi + 8
    bot = ry
    pts = [(rx, bot), (rx+40, bot)]
    # наростання з перерегулюванням і згасаючим дзвоном
    base = rx + 40
    span = top
    for i in range(0, 60):
        t = i / 59.0
        # фронт + згасаюча синусоїда (overshoot → дзвін)
        env = math.exp(-3.0 * t)
        val = (1 - math.exp(-6 * t)) + 0.32 * env * math.sin(10 * t)
        y = bot + (top - bot) * max(0.0, min(1.25, val))
        pts.append((base + 70 * t, y))
    # утримання «1» з легким брязкотом
    hold0 = base + 70
    for i in range(0, 30):
        t = i / 29.0
        y = top + 6 * math.exp(-4 * t) * math.sin(14 * t)
        pts.append((hold0 + 40 * t, y))
    # спад
    fall0 = hold0 + 40
    for i in range(0, 50):
        t = i / 49.0
        env = math.exp(-3.0 * t)
        val = math.exp(-6 * t) - 0.28 * env * math.sin(10 * t)
        y = bot + (top - bot) * max(-0.22, min(1.05, val))
        pts.append((fall0 + 70 * t, y))
    pts.append((rx + 300, bot))
    el.append(polyline(pts, BAD, 2.4))

    # підписи дефектів
    el.append(text(rx + 78, top - 14, "overshoot", size=11, color=BAD, anchor="start"))
    el.append(text(rx + 150, top + 24, "дзвін (ringing)", size=11, color=BAD))
    el.append(text(rx + 250, bot + 16, "undershoot", size=11, color=BAD, anchor="middle"))

    render(os.path.join(IMG, "real-signal.svg"), W, H, *el)


# ── 2. Коли доріжка стає лінією: фронт проти подвійної затримки ───────────────
def fig_when_line():
    W, H = 780, 430
    el = []
    el.append(text(W/2, 26, "Вирішує не частота, а крутість фронту", size=17, bold=True))

    def scope(x0, y0, w, h, title, ringing):
        out = line(x0, y0, x0, y0 - h, MUTED, 1.2)
        out += line(x0, y0, x0 + w, y0, MUTED, 1.2)
        top = y0 - h + 10
        bot = y0
        # сам фронт (повільний vs швидкий малюємо однаково, різниться поведінка)
        if not ringing:
            # повільний фронт: затримка << фронт → відбиття «тоне» у фронті
            pts = [(x0, bot)]
            for i in range(0, 70):
                t = i / 69.0
                y = bot + (top - bot) * (1 - math.exp(-3.5 * t))
                pts.append((x0 + 6 + (w-12) * t, y))
            out += polyline(pts, GOOD, 2.4)
            out += text(x0 + w/2, top - 8, "гладко", size=11, color=GOOD)
        else:
            # швидкий фронт: відбиття повертається ПІД час плато → сходинки/дзвін
            pts = [(x0, bot)]
            n = 70
            for i in range(0, n):
                t = i / float(n-1)
                env = math.exp(-2.4 * t)
                y = bot + (top - bot) * (min(1.0, 1 - math.exp(-9*t)) + 0.30*env*math.sin(9*t))
                pts.append((x0 + 6 + (w-12) * t, y))
            out += polyline(pts, BAD, 2.4)
            out += text(x0 + w/2, top - 8, "дзвін", size=11, color=BAD)
        out += text(x0 + w/2, y0 + 22, title, size=12, anchor="middle")
        return out

    # лівий: повільний фронт (велика стала наростання)
    el.append(scope(70, 200, 280, 150, "повільний фронт: 2·t_затр ≪ t_фронт", False))
    # правий: швидкий фронт
    el.append(scope(440, 200, 280, 150, "швидкий фронт: 2·t_затр ≈ t_фронт", True))

    # нижня смуга — правило
    bb, bw, bh = polyline, 0, 0
    box = fitbox(70, 260, 650, 56,
                 "Критерій: фронт стає «лінією», коли подвійна затримка доріжки (туди й назад)\n"
                 "наближається до часу фронту.  t_затр ≈ довжина / швидкість ≈ 150 пс на дюйм на FR-4.",
                 size=13, fill="#eef6ff", stroke=WAVE)
    el.append(box)
    el.append(text(W/2, 348, "Та сама доріжка: для повільного фронту — звичайне з'єднання, "
                             "для швидкого — лінія передачі.", size=12, color=MUTED))

    render(os.path.join(IMG, "when-line.svg"), W, H, *el)


# ── 3. Термінація: послідовна (біля джерела) vs паралельна (біля приймача) ────
def fig_termination():
    W, H = 800, 360
    el = []
    el.append(text(W/2, 26, "Дві школи термінації: погасити на старті чи на фініші", size=17, bold=True))

    def driver(cx, cy):
        out = rect(cx-26, cy-18, 52, 36, fill="#eef6ff", stroke=WAVE, sw=1.6)
        out += text(cx, cy+4, "DRV", size=12, bold=True, color=WAVE)
        return out

    def rxchip(cx, cy):
        out = rect(cx-26, cy-18, 52, 36, fill="#f4f6f8", stroke=LINE, sw=1.6)
        out += text(cx, cy+4, "RX", size=12, bold=True)
        return out

    def res_h(x1, y, x2, label, color=INK):
        # горизонтальний резистор-зигзаг
        n = 6
        seg = (x2 - x1) / n
        pts = [(x1, y)]
        for i in range(1, n):
            yy = y - 7 if i % 2 else y + 7
            pts.append((x1 + seg*i, yy))
        pts.append((x2, y))
        out = polyline(pts, color, 1.8)
        out += text((x1+x2)/2, y - 14, label, size=11, color=color, bold=True)
        return out

    def res_v(x, y1, y2, label):
        n = 6
        seg = (y2 - y1) / n
        pts = [(x, y1)]
        for i in range(1, n):
            xx = x - 7 if i % 2 else x + 7
            pts.append((xx, y1 + seg*i))
        pts.append((x, y2))
        out = polyline(pts, INK, 1.8)
        out += text(x + 16, (y1+y2)/2 + 4, label, size=11, anchor="start")
        return out

    line_y = 150
    # ── послідовна ──
    el.append(text(220, 70, "Послідовна (source / series)", size=13, bold=True))
    el.append(driver(90, line_y))
    el.append(res_h(116, line_y, 176, "Rₛ ≈ Z₀ − Rdrv", color=BAD))
    el.append(line(176, line_y, 330, line_y, WAVE, 2.2))
    el.append(rxchip(356, line_y))
    el.append(line(330, line_y, 330, line_y, WAVE, 2.2))
    el.append(fitbox(60, 196, 320, 64,
                     "Резистор біля драйвера. Відбиття від далекого кінця вертається\n"
                     "й гасне на Rₛ. Нуль постійного струму — економно.",
                     size=11.5, fill="#fdecea", stroke=BAD))

    # ── паралельна ──
    el.append(text(610, 70, "Паралельна (parallel / shunt)", size=13, bold=True))
    el.append(driver(470, line_y))
    el.append(line(496, line_y, 700, line_y, WAVE, 2.2))
    el.append(rxchip(726, line_y))
    # резистор на землю біля приймача
    el.append(circle(700, line_y, 3.0, fill=INK, stroke=INK))
    el.append(res_v(700, line_y, line_y+58, "R = Z₀"))
    # земля
    gy = line_y + 58
    el.append(line(686, gy, 714, gy, INK, 2.0))
    el.append(line(690, gy+5, 710, gy+5, INK, 1.6))
    el.append(line(694, gy+10, 706, gy+10, INK, 1.2))
    el.append(fitbox(440, 196, 330, 64,
                     "Резистор = Z₀ на землю біля приймача. Хвиля одразу «бачить»\n"
                     "узгодження — відбиття немає. Та через нього тече струм.",
                     size=11.5, fill="#eafaf0", stroke=GOOD))

    render(os.path.join(IMG, "termination.svg"), W, H, *el)


# ── 4. Очна діаграма: накладені біти лишають «око» ────────────────────────────
def fig_eye():
    W, H = 740, 400
    el = []
    el.append(text(W/2, 26, "Очна діаграма: тисячі бітів, накладені в одне вікно", size=17, bold=True))

    x0, y0, w, h = 90, 320, 480, 230
    top, bot = y0 - h, y0
    mid = (top + bot) / 2
    # осі
    el.append(line(x0, bot, x0 + w, bot, MUTED, 1.0))
    el.append(line(x0, top, x0, bot, MUTED, 1.0))
    el.append(text(x0 - 10, top + 6, "Vᴴ", size=12, color=MUTED, anchor="end"))
    el.append(text(x0 - 10, bot, "Vᴸ", size=12, color=MUTED, anchor="end"))
    el.append(text(x0 - 10, mid + 4, "Vᵗ", size=12, color=MUTED, anchor="end"))

    # межі одного інтервалу біта (UI): малюємо два UI
    ui = w / 2.0
    # генеруємо багато «прольотів» між рівнями зі зсувом фази й шумом — формують око
    import random
    random.seed(7)
    edges = []
    def lvl(b):
        return top if b == 1 else bot
    for k in range(70):
        jit = random.uniform(-0.06, 0.06) * ui          # тремтіння фронту
        amp = random.uniform(-0.05, 0.05) * h            # шум амплітуди
        seq = [random.randint(0, 1) for _ in range(3)]
        pts = []
        for i in range(3):
            xb = x0 + i * ui + jit
            yb = lvl(seq[i]) + (amp if seq[i] else -amp)
            # фронт: проста S-подібна між рівнями
            if i > 0:
                xprev = x0 + (i-1) * ui + jit
                yprev = lvl(seq[i-1]) + (amp if seq[i-1] else -amp)
                for s in range(0, 9):
                    t = s / 8.0
                    sm = t*t*(3 - 2*t)
                    pts.append((xprev + (xb - xprev) * t, yprev + (yb - yprev) * sm))
            pts.append((xb, yb))
        col = "#9bb7e6" if k % 2 else "#a9d3bd"
        edges.append(polyline(pts, col, 1.0))
    el.extend(edges)

    # рамка ока в центрі першого UI
    ecx = x0 + ui
    ew, eh = ui * 0.5, h * 0.42
    el.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
              'stroke="%s" stroke-width="1.4" stroke-dasharray="4,4"/>'
              % (ecx, mid, ew*0.62, eh*0.55, BAD))
    # розміри ока
    el.append(line(ecx, mid - eh*0.55, ecx, mid + eh*0.55, BAD, 1.4))
    el.append(text(ecx + 8, mid, "розкрив\n(запас по V)", size=10.5, color=BAD, anchor="start"))
    el.append(line(ecx - ew*0.62, mid, ecx + ew*0.62, mid, BAD, 1.4))
    el.append(text(ecx, mid - eh*0.55 - 8, "ширина (запас по часу)", size=10.5, color=BAD))

    # точка вибірки
    el.append(circle(ecx, mid, 4.0, fill=BAD, stroke=BAD))

    el.append(fitbox(x0 + w + 18, top, 150, h,
                     "Око відкрите —\nприймач упевнено\nрозрізнить 0 і 1.\n\n"
                     "Звузиться по\nвисоті — завинив\nшум; по ширині —\nтремтіння (jitter).\n\n"
                     "Закриється —\nпомилки.",
                     size=11, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "eye.svg"), W, H, *el)


# ── 5. Bounce / lattice діаграма: відлуння як зигзаг у часі ───────────────────
def fig_lattice():
    """Решітчаста (bounce) діаграма: вісь відстані горизонтально, час униз;
    хвиля зигзагом б'ється між драйвером і приймачем, біля кожного відрізка —
    його напруга. Числа з прикладу статті: Z0=50, Rdrv=25, t_зат=0.8 нс."""
    W, H = 760, 504
    el = []
    el.append(text(W/2, 26, "Bounce-діаграма: відлуння зигзагом у часі", size=17, bold=True))

    xL, xR = 165, 600          # драйвер ліворуч, приймач праворуч
    yTop = 78                   # t = 0
    dy = 56                     # пікселів на один проліт (t_зат)
    # вертикальні «стіни»
    el.append(line(xL, yTop, xL, yTop + 6*dy, MUTED, 1.4))
    el.append(line(xR, yTop, xR, yTop + 6*dy, MUTED, 1.4))
    el.append(text(xL, yTop - 30, "драйвер", size=12, bold=True, color=WAVE))
    el.append(text(xR, yTop - 30, "відкритий вхід RX", size=12, bold=True, color=BAD))
    el.append(text(xL, yTop - 14, "Γ_s = −1/3", size=11, color=WAVE))
    el.append(text(xR, yTop - 14, "Γ_L = +1", size=11, color=BAD))

    # вісь часу
    for k in range(0, 6):
        lab = "t = 0" if k == 0 else ("t" if k == 1 else "%dt" % k)
        el.append(text(xL - 95, yTop + k*dy + 4, lab, size=11, color=MUTED, anchor="start"))
    el.append(text(xL - 95, yTop + 6*dy + 16, "час ↓  (t = t_зат)",
                   size=11, color=MUTED, anchor="start"))

    # зигзаг: точки на стінах по черзі
    pts = [(xL, yTop)]
    side = 1   # 1 → йдемо вправо до xR
    y = yTop
    for k in range(1, 6):
        y += dy
        x = xR if side == 1 else xL
        pts.append((x, y))
        side *= -1
    # сегменти зигзагу зі стрілками й підписами хвиль (реальні амплітуди)
    seg_labels = ["+2.20", "+2.20", "−0.73", "−0.73", "+0.24"]
    for i in range(5):
        (x1, y1), (x2, y2) = pts[i], pts[i+1]
        col = WAVE if (x2 > x1) else BAD
        el.append(arrow(x1, y1, x2, y2, color=col, sw=2.0))
        mx, my = (x1+x2)/2, (y1+y2)/2
        anc = "start" if x2 > x1 else "end"
        ox = 10 if x2 > x1 else -10
        el.append(text(mx + ox, my - 3, seg_labels[i] + " В", size=10.5, color=col, anchor=anc))

    # напруга на вузлах приймача (права стіна) — у моменти t, 3t, 5t
    rx_v = {1: "4.40", 3: "2.93", 5: "3.42"}
    for k, v in rx_v.items():
        el.append(circle(xR, yTop + k*dy, 3.4, fill=BAD, stroke=BAD))
        el.append(text(xR + 14, yTop + k*dy + 4, "V_RX = " + v + " В",
                       size=10.5, color=BAD, anchor="start"))
    # напруга на вузлах драйвера у моменти 0, 2t, 4t
    dr_v = {0: "2.20", 2: "3.67", 4: "3.18"}
    for k, v in dr_v.items():
        el.append(circle(xL, yTop + k*dy, 3.4, fill=WAVE, stroke=WAVE))
        el.append(text(xL - 14, yTop + k*dy + 4, "V_др = " + v + " В",
                       size=10.5, color=WAVE, anchor="end"))

    el.append(fitbox(110, yTop + 6*dy + 28, 540, 46,
                     "Кожна стрілка — одна хвиля (поряд її амплітуда). Уперше дійшовши, відкритий вхід\n"
                     "подвоює: 4.40 В — це 2 × 2.20. Сума всіх відлунь у вузлі — напруга там у цю мить.",
                     size=11.5, fill="#eef6ff", stroke=WAVE))
    render(os.path.join(IMG, "lattice.svg"), W, H, *el)


# ── 6. Сходинкове встановлення напруги на вході приймача ──────────────────────
def fig_settling():
    """V_RX(t): сходинки 2.00 → 1.33 → 1.56 → 1.48 → ... що сходяться до 2.0 В
    (за Γ_s<0, Γ_L=+1 — згасаюче коливання навколо кінцевого 2.0 В)."""
    W, H = 760, 420
    el = []
    el.append(text(W/2, 26, "Напруга на вході приймача: сходинки до подвоєння", size=17, bold=True))

    x0, y0, w, h = 90, 330, 580, 250
    top, bot = y0 - h, y0
    el.append(line(x0, bot, x0 + w, bot, MUTED, 1.2))         # вісь часу
    el.append(line(x0, top, x0, bot, MUTED, 1.2))             # вісь напруги
    el.append(text(x0 + w/2, bot + 26, "час →  (поділка = подвійна затримка 2t)",
                   size=12, color=MUTED))
    el.append(text(x0 - 10, top + 6, "В", size=12, color=MUTED, anchor="end"))

    # шкала напруги: 0 .. 4.8 В (щоб overshoot 4.4 влазив)
    Vmax = 4.8
    def vy(v):
        return bot - (bot - top) * (v / Vmax)
    for v in (1.0, 2.0, 3.0, 4.0):
        el.append(line(x0, vy(v), x0 + w, vy(v), MUTED, 0.8, dash="2,6"))
        el.append(text(x0 - 8, vy(v) + 4, "%.0f" % v, size=11, color=MUTED, anchor="end"))
    # живлення (рейка) 3.3 В = кінцевий усталений рівень
    el.append(line(x0, vy(3.3), x0 + w, vy(3.3), GOOD, 1.3, dash="5,4"))
    el.append(text(x0 + w - 4, vy(3.3) - 7, "V_жив = 3.3 В = кінцеве",
                   size=11, color=GOOD, anchor="end"))
    # поріг логіки V_IH ~ 2.0 В
    el.append(line(x0, vy(2.0), x0 + w, vy(2.0), POS, 1.0, dash="2,4"))
    el.append(text(x0 + 6, vy(2.0) + 14, "поріг V_IH ≈ 2.0 В", size=10.5, color=POS, anchor="start"))

    # реальні V_RX: рівні з'являються в t,3t,5t,7t,... кожен тримається 2t
    levels = [4.40, 2.93, 3.42, 3.26, 3.31, 3.30]
    step_w = w / (len(levels) + 0.5)
    pts = [(x0, vy(0.0))]
    x = x0 + step_w * 0.5      # перший фронт доходить за t (півкроку від 0)
    pts.append((x, vy(0.0)))
    for v in levels:
        pts.append((x, vy(v)))            # вертикальний стрибок
        pts.append((x + step_w, vy(v)))   # утримання 2t
        x += step_w
    el.append(polyline(pts, BAD, 2.6))

    # overshoot-позначка на першій сходинці
    el.append(circle(x0 + step_w*0.5, vy(4.40), 3.4, fill=BAD, stroke=BAD))
    el.append(text(x0 + step_w*0.5 + 8, vy(4.40) - 8,
                   "4.40 В = 2 × 2.20  (overshoot вище рейки!)",
                   size=10.5, color=BAD, anchor="start"))
    # стрілка «б'є по діодах входу»
    el.append(text(x0 + step_w*1.6, vy(4.40) + 18, "↑ б'є по захисних діодах входу",
                   size=10, color=BAD, anchor="start"))

    render(os.path.join(IMG, "settling.svg"), W, H, *el)


if __name__ == "__main__":
    fig_real_signal()
    fig_when_line()
    fig_termination()
    fig_eye()
    fig_lattice()
    fig_settling()
    print("OK: 6 figures ->", IMG)
