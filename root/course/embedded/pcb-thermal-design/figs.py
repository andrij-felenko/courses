# -*- coding: utf-8 -*-
"""Фігури до теми «Тепловідведення на PCB» (root/course/embedded/komponenty)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

COPPER = "#c8731f"   # мідь
COPPER_L = "#f6e3cf"  # світла мідь (заливка)
FR4 = "#2f7d4f"      # текстоліт
FR4_L = "#dff0e4"    # світлий текстоліт
HOT = POS


# ── 1. Мідний полігон як розтікач тепла ─────────────────────────────────────
def fig_spreader():
    W, H = 760, 430
    p = []
    p.append(text(W/2, 26, "Мідний полігон розтікає тепло від крихітного паду", size=17, bold=True))

    # дві панелі: ліворуч — голий пад, праворуч — пад на полігоні
    # спільна підкладка-розріз: текстоліт знизу, мідь зверху тонким шаром
    base_y = 250
    th_fr4 = 70
    th_cu = 14

    # --- ЛІВА панель: малий пад ---
    lx0, lw = 60, 300
    p.append(text(lx0 + lw/2, 70, "Малий пад: тепло нікуди тікати", size=13, bold=True, color=HOT))
    # текстоліт
    p.append(rect(lx0, base_y, lw, th_fr4, fill=FR4_L, stroke=FR4, sw=1.5, rx=2))
    p.append(text(lx0 + lw/2, base_y + th_fr4 + 18, "текстоліт (FR4): тепло майже не проводить", size=11, color=FR4))
    # маленький мідний пад
    pad_w = 56
    pcx = lx0 + lw/2
    p.append(rect(pcx - pad_w/2, base_y - th_cu, pad_w, th_cu, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    # деталь
    p.append(rect(pcx - 22, base_y - th_cu - 30, 44, 30, fill="#3a3a3a", stroke=INK, sw=1.5, rx=3))
    p.append(text(pcx, base_y - th_cu - 12, "чип", size=11, color="#ffffff", bold=True))
    # стрілки тепла — вузький стовпчик, упирається
    for dx in (-10, 0, 10):
        p.append(arrow(pcx + dx, base_y - th_cu + 4, pcx + dx, base_y + th_fr4 - 8, color=HOT, sw=2.2))
    p.append(text(pcx, base_y + th_fr4/2 + 4, "глухо", size=11, color=HOT, bold=True))

    # --- ПРАВА панель: широкий полігон ---
    rx0, rw = 410, 300
    p.append(text(rx0 + rw/2, 70, "Широкий полігон: тепло розповзається й віддається", size=12, bold=True, color=FIELD))
    p.append(rect(rx0, base_y, rw, th_fr4, fill=FR4_L, stroke=FR4, sw=1.5, rx=2))
    # широкий мідний шар
    p.append(rect(rx0 + 10, base_y - th_cu, rw - 20, th_cu, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    rcx = rx0 + rw/2
    # деталь
    p.append(rect(rcx - 22, base_y - th_cu - 30, 44, 30, fill="#3a3a3a", stroke=INK, sw=1.5, rx=3))
    p.append(text(rcx, base_y - th_cu - 12, "чип", size=11, color="#ffffff", bold=True))
    # тепло входить вузько, розтікається вшир уздовж міді
    p.append(arrow(rcx, base_y - th_cu - 1, rcx, base_y - 2, color=HOT, sw=2.4))
    # горизонтальне розтікання
    for sgn in (-1, 1):
        p.append(arrow(rcx + sgn*16, base_y - th_cu/2, rcx + sgn*120, base_y - th_cu/2, color=COPPER, sw=2.4))
    # віддача в повітря по всій ширині
    for dx in range(-110, 111, 30):
        p.append(arrow(rcx + dx, base_y - th_cu - 2, rcx + dx, base_y - th_cu - 26, color=NEG, sw=1.6))
    p.append(text(rcx, base_y - th_cu - 40, "віддача в повітря з усієї площі", size=11, color=NEG))

    # нижній підсумок
    fb = fitbox(60, 350, 640, 56,
                "Мідь проводить тепло у ~1000 разів краще за текстоліт (k ≈ 400 проти ≈ 0.3 Вт/(м·°C)).\n"
                "Полігон працює як «дріт» для тепла: збирає його з паду й роздає повітрю з великої площі.",
                size=12.5, fill="#fff8ef", stroke=COPPER)
    p.append(fb)
    render(os.path.join(OUT, "copper-spreader.svg"), W, H, *p)


# ── 2. Теплові перехідні отвори (vias) ──────────────────────────────────────
def fig_vias():
    W, H = 720, 440
    p = []
    p.append(text(W/2, 26, "Теплові отвори ведуть тепло крізь текстоліт на інший бік", size=16, bold=True))

    # розріз плати: верхня мідь, FR4, нижня мідь; крізь FR4 — мідні бочки vias
    left, right = 90, 630
    top_cu_y = 110
    th_cu = 16
    fr4_y = top_cu_y + th_cu
    th_fr4 = 150
    bot_cu_y = fr4_y + th_fr4

    # деталь QFN із тепловим падом
    dcx = (left + right)/2
    p.append(rect(dcx - 120, top_cu_y - 44, 240, 44, fill="#3a3a3a", stroke=INK, sw=1.5, rx=4))
    p.append(text(dcx, top_cu_y - 20, "QFN, знизу — тепловий пад", size=12, color="#ffffff", bold=True))

    # верхня мідь (тепловий пад)
    p.append(rect(left, top_cu_y, right-left, th_cu, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    p.append(text(right + 6, top_cu_y + th_cu/2 + 4, "верх", size=11, color=COPPER, anchor="start"))
    # FR4
    p.append(rect(left, fr4_y, right-left, th_fr4, fill=FR4_L, stroke=FR4, sw=1.5, rx=2))
    p.append(text(left + 8, fr4_y + 20, "текстоліт — теплоізолятор", size=12, color=FR4, anchor="start"))
    # нижня мідь
    p.append(rect(left, bot_cu_y, right-left, th_cu, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    p.append(text(right + 6, bot_cu_y + th_cu/2 + 4, "низ", size=11, color=COPPER, anchor="start"))

    # via-бочки (мідні циліндри крізь FR4)
    vias_x = [dcx - 90, dcx - 45, dcx, dcx + 45, dcx + 90]
    for vx in vias_x:
        p.append(rect(vx - 6, fr4_y, 12, th_fr4, fill=COPPER, stroke="#8a4f15", sw=1.2, rx=2))
        # стрілка тепла вниз крізь via
        p.append(arrow(vx, fr4_y + 6, vx, bot_cu_y - 4, color=HOT, sw=2.0))
    p.append(text(dcx + 150, fr4_y + th_fr4/2, "мідні бочки", size=11, color=COPPER, anchor="start"))
    p.append(text(dcx + 150, fr4_y + th_fr4/2 + 16, "(заповнені міддю)", size=11, color=COPPER, anchor="start"))

    # порівняння: де vias нема — тепло вперлось у FR4
    p.append(arrow(left + 30, fr4_y + 4, left + 30, fr4_y + 50, color=MUTED, sw=2.0))
    p.append(text(left + 30, fr4_y + 66, "без via —", size=10, color=MUTED))
    p.append(text(left + 30, fr4_y + 80, "глухо", size=10, color=MUTED))

    # віддача з нижньої міді в повітря/полігон
    for dx in range(-90, 91, 30):
        p.append(arrow(dcx + dx, bot_cu_y + th_cu + 1, dcx + dx, bot_cu_y + th_cu + 24, color=NEG, sw=1.6))
    p.append(text(dcx, bot_cu_y + th_cu + 40, "нижній полігон віддає тепло в повітря", size=11, color=NEG))

    fb = fitbox(90, bot_cu_y + th_cu + 56, 540, 54,
                "Кожен via — крихітний мідний дріт крізь ізолятор. Сітка ~0.3 мм отворів на кроці ~1 мм\n"
                "знижує тепловий опір паду в рази; вище ~25 отворів виграш майже зникає.",
                size=12, fill="#fff8ef", stroke=COPPER)
    p.append(fb)
    render(os.path.join(OUT, "thermal-vias.svg"), W, H, *p)


# ── 3. θJA залежить від міді плати ──────────────────────────────────────────
def fig_theta_curve():
    W, H = 720, 430
    p = []
    p.append(text(W/2, 26, "θJA — не стала деталі, а наслідок міді плати", size=17, bold=True))

    ox, oy = 110, 330        # початок осей
    aw, ah = 540, 230
    # осі
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw/2, oy + 40, "мідь під деталлю: площа полігона й кількість шарів →", size=12, color=INK))
    p.append(text(ox - 70, oy - ah/2, "θJA", size=13, color=INK, bold=True))
    p.append(text(ox - 70, oy - ah/2 + 18, "°C/Вт", size=10, color=MUTED))

    # крива: круто падає, тоді виположується (asymptote)
    import math
    pts = []
    n = 60
    for i in range(n+1):
        t = i/n
        x = ox + t*aw
        # експоненційний спад до асимптоти
        val = 0.12 + 0.88*math.exp(-3.4*t)
        y = oy - ah*0.12 - (ah*0.80)*val
        pts.append((x, y))
    path_d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_d, HOT))

    # три робочі точки
    def mark(t, label, sub, col):
        x = ox + t*aw
        val = 0.12 + 0.88*math.exp(-3.4*t)
        y = oy - ah*0.12 - (ah*0.80)*val
        out = circle(x, y, 6, fill=col, stroke=INK, sw=1.5)
        out += line(x, y, x, oy, color=col, sw=1.0, dash="3,3")
        return out, x, y, label, sub, col

    marks = [
        mark(0.04, "голий пад", "1 шар, мінімум міді", HOT),
        mark(0.30, "полігон", "залив верх міддю", "#d68a1e"),
        mark(0.72, "полігон + vias + шари", "2s2p, теплові отвори", FIELD),
    ]
    for out, x, y, label, sub, col in marks:
        p.append(out)
    # підписи точок (рознесені, щоб не налазили)
    lp = [
        (marks[0], ox + aw*0.04 + 8, oy - ah*0.86, "start"),
        (marks[1], ox + aw*0.30 + 8, oy - ah*0.50, "start"),
        (marks[2], ox + aw*0.72 - 8, oy - ah*0.30, "end"),
    ]
    for (out, x, y, label, sub, col), tx, ty, anch in lp:
        p.append(text(tx, ty, label, size=12, color=col, bold=True, anchor=anch))
        p.append(text(tx, ty + 16, sub, size=10, color=MUTED, anchor=anch))

    # позначка асимптоти
    p.append(line(ox, oy - ah*0.12 - ah*0.80*0.12, ox + aw, oy - ah*0.12 - ah*0.80*0.12,
                  color=MUTED, sw=1.0, dash="2,4"))
    p.append(text(ox + aw - 4, oy - ah*0.12 - ah*0.80*0.12 - 6, "межа: далі мідь майже не допомагає",
                  size=10, color=MUTED, anchor="end"))

    fb = fitbox(110, 372, 540, 46,
                "Те саме число θJA з даташита виміряне на стандартній платі JEDEC. На вашій —\n"
                "інша мідь, інше θJA. Площа полігона й теплові шари тиснуть на нього найдужче.",
                size=12, fill=FILL, stroke=LINE)
    p.append(fb)
    render(os.path.join(OUT, "theta-vs-copper.svg"), W, H, *p)


# ── 4. Доріжка — теж резистор, що гріється ──────────────────────────────────
def fig_trace_heating():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 26, "Доріжка живлення — це резистор: струм її гріє", size=17, bold=True))

    # вузька доріжка
    y1 = 95
    p.append(text(120, y1 - 18, "вузька доріжка", size=12, bold=True, color=HOT))
    p.append(rect(90, y1, 420, 14, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    p.append(arrow(96, y1 + 7, 504, y1 + 7, color=INK, sw=1.6))
    # «гарячі» хвильки над вузькою
    for dx in range(120, 481, 40):
        p.append(text(dx, y1 - 4, "≈", size=12, color=HOT))
    p.append(text(540, y1 + 9, "перегрів", size=11, color=HOT, anchor="start", bold=True))

    # широка доріжка
    y2 = 175
    p.append(text(120, y2 - 22, "широка доріжка, той самий струм", size=12, bold=True, color=FIELD))
    p.append(rect(90, y2, 420, 30, fill=COPPER_L, stroke=COPPER, sw=2, rx=2))
    p.append(arrow(96, y2 + 15, 504, y2 + 15, color=INK, sw=1.6))
    p.append(text(540, y2 + 18, "ледь тепла", size=11, color=FIELD, anchor="start", bold=True))

    # формула
    p.append(rect(90, 240, 540, 44, fill="#fff8ef", stroke=COPPER, sw=1.5, rx=6))
    p.append(text(360, 268, "P = I² · R     R = ρ · L / (товщина · ширина)",
                  size=15, color=INK, bold=True))

    fb = fitbox(90, 296, 540, 44,
                "Ширша й товстіша мідь — менший опір R, менше тепла P при тому самому струмі.\n"
                "Скільки саме треба — дають таблиці IPC (ширина під струм і допустимий перегрів).",
                size=12, fill=FILL, stroke=LINE)
    p.append(fb)
    render(os.path.join(OUT, "trace-heating.svg"), W, H, *p)


# ── 5. Звуження ліній потоку: звідки береться опір розтікання ────────────────
def fig_constriction():
    W, H = 760, 470
    p = []
    p.append(text(W/2, 26, "Опір розтікання: лінії потоку тиснуться біля джерела", size=17, bold=True))

    # широкий блок міді (розріз), згори по центру — мале джерело радіуса a
    bx, by, bw, bh = 70, 90, 620, 250
    p.append(rect(bx, by, bw, bh, fill=COPPER_L, stroke=COPPER, sw=2, rx=4))
    p.append(text(bx + bw - 8, by + bh - 10, "широка мідь (k)", size=12, color=COPPER, anchor="end"))

    cx = bx + bw/2
    a_half = 34                      # піврозмір джерела на малюнку
    # джерело-пад згори
    p.append(rect(cx - a_half, by - 26, 2*a_half, 26, fill="#3a3a3a", stroke=INK, sw=1.5, rx=3))
    p.append(text(cx, by - 9, "джерело 2a", size=11, color="#ffffff", bold=True))

    # лінії потоку: вертикальні й щільні під джерелом, тоді розходяться віялом
    import math
    starts = [cx + sx for sx in range(-a_half + 6, a_half - 5, 12)]
    ys = by
    yb = by + bh - 6
    for x0 in starts:
        frac = (x0 - cx) / a_half        # -1..1
        # кінцева точка розходиться ширше за блоком
        xend = cx + frac * (bw/2 - 30)
        # крива: спершу прямо вниз (звуження), тоді розхід
        c1x, c1y = x0, by + 70
        c2x, c2y = xend, by + 150
        d = "M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (x0, ys, c1x, c1y, c2x, c2y, xend, yb)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, HOT))

    # ізотерми: густі дуги біля джерела (крутий градієнт), рідкі — далі
    for r, op in [(46, 1.0), (74, 0.8), (118, 0.6), (180, 0.45)]:
        d = "M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" % (cx - r, by + 4, r, r*0.78, cx + r, by + 4)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4,4" opacity="%.2f"/>' % (d, NEG, op))
    p.append(text(cx, by + 40, "густі ізотерми", size=10, color=NEG, bold=True))
    p.append(text(cx, by + 54, "крутий ΔT", size=10, color=NEG))
    p.append(text(cx + 196, by + 150, "рідкі ізотерми:", size=10, color=MUTED, anchor="start"))
    p.append(text(cx + 196, by + 164, "далеко майже немає", size=10, color=MUTED, anchor="start"))
    p.append(text(cx + 196, by + 178, "перепаду", size=10, color=MUTED, anchor="start"))

    # дужка-виноска «тут увесь опір»
    p.append(text(cx - 200, by + 96, "увесь опір —", size=12, color=HOT, anchor="start", bold=True))
    p.append(text(cx - 200, by + 112, "у звуженні", size=12, color=HOT, anchor="start", bold=True))

    fb = fitbox(70, 356, 620, 96,
                "Тепло втискається з малого джерела в широку мідь — лінії потоку згущуються тільки коло нього.\n"
                "Майже весь перепад ΔT накопичується в цьому тонкому шарі звуження; далі мідь холодна й нічого не\n"
                "додає. Це й є опір розтікання. Електричний двійник той самий: струм із плямки в товщу металу\n"
                "дає опір R = ρ/(4a) — теплова версія: R = 1/(4·k·a).",
                size=12.5, fill="#fff8ef", stroke=COPPER)
    p.append(fb)
    render(os.path.join(OUT, "spreading-flux-lines.svg"), W, H, *p)


# ── 6. Спадна віддача: опір шляху проти радіуса полігона ─────────────────────
def fig_spreading_curve():
    import math
    W, H = 740, 460
    p = []
    p.append(text(W/2, 26, "Чому віддача полігона спадна: повний опір майже не падає", size=16, bold=True))

    ox, oy = 95, 330
    aw, ah = 580, 250

    # модель: тонкий шар 1 oz, мідь k=400, натуральна конвекція з площі
    k = 400.0; t = 35e-6; a = 1e-3; h = 20.0
    bmin, bmax = 1.5e-3, 50e-3
    def Rspread(b): return math.log(b/a)/(2*math.pi*k*t)
    def Rconv(b):   return 1.0/(h*math.pi*b*b)
    def Rtot(b):    return Rspread(b) + Rconv(b)

    # лог-вісь по радіусу, лінійна по опору (у % від опору при найменшому полігоні? ні — абсолют, лог)
    import math as m
    def X(b): return ox + aw * (m.log(b) - m.log(bmin)) / (m.log(bmax) - m.log(bmin))
    Rref = Rtot(bmin)
    # лог-шкала опору, щоб умістити 7000..50
    Rlo, Rhi = 30.0, Rref
    def Y(R):
        R = max(R, Rlo)
        return oy - ah * (m.log(R) - m.log(Rlo)) / (m.log(Rhi) - m.log(Rlo))

    # осі
    p.append(arrow(ox, oy, ox + aw + 6, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(text(ox + aw/2, oy + 42, "радіус полігона b (мм), лог-шкала →", size=12, color=INK))
    p.append(text(ox - 60, oy - ah - 18, "опір шляху", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(ox - 60, oy - ah - 2, "K/Вт, лог", size=10, color=MUTED, anchor="start"))

    # позначки осі X
    for bm in [2, 5, 10, 20, 50]:
        xx = X(bm*1e-3)
        p.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.4))
        p.append(text(xx, oy + 20, str(bm), size=11, color=MUTED))

    def curve(fn, col, sw=2.6, dash=None):
        pts = []
        n = 80
        for i in range(n+1):
            b = bmin * (bmax/bmin) ** (i/n)
            pts.append((X(b), Y(fn(b))))
        d = "M " + " L ".join("%.1f %.1f" % xy for xy in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, da))

    curve(Rtot, HOT, 3.0)
    curve(Rconv, NEG, 1.8, "6,4")
    curve(Rspread, COPPER, 1.8, "2,4")

    # підписи кривих (рознесені, кожен на «своїй» ділянці без перетину)
    p.append(text(X(3.0e-3), Y(Rtot(3.0e-3)) - 12, "повний опір шляху", size=12, color=HOT, bold=True, anchor="start"))
    p.append(text(X(2.6e-3), Y(Rconv(2.6e-3)) - 10, "віддача в повітря (1/h·площа) ↓", size=11, color=NEG, anchor="start"))
    p.append(text(X(9e-3), Y(Rspread(9e-3)) - 12, "опір розтікання ↑ (ln b)", size=11, color=COPPER, anchor="middle"))

    # зона «доточувати майже марно»
    xk = X(18e-3)
    p.append(line(xk, oy - ah, xk, oy, color=FIELD, sw=1.4, dash="3,3"))
    p.append(text(xk + 6, oy - ah + 14, "далі — майже", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(xk + 6, oy - ah + 30, "марно", size=11, color=FIELD, anchor="start", bold=True))

    fb = fitbox(95, 372, 580, 58,
                "Полігон більшає → опір розтікання повільно росте (як ln b), а віддача з площі швидко падає.\n"
                "Їхня сума спершу круто спадає, тоді виположується: з якогось радіуса дальня мідь холодна,\n"
                "тож кожен наступний сантиметр майже не зменшує повний опір. (1 oz, природна конвекція.)",
                size=12, fill=FILL, stroke=LINE)
    p.append(fb)
    render(os.path.join(OUT, "spreading-vs-radius.svg"), W, H, *p)


# ── 7. Анатомія дна корпусу й три шари посадкового місця ─────────────────────
def fig_epad_anatomy():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 26, "Черево корпусу й три шари посадкового місця", size=17, bold=True))

    # --- ЛІВА панель: дно корпусу (вид знизу) ---
    lx, ly, ls = 60, 70, 250
    p.append(text(lx + ls/2, 58, "Дно корпусу (вид знизу)", size=13, bold=True))
    p.append(rect(lx, ly, ls, ls, fill="#ececec", stroke=INK, sw=1.6, rx=6))
    # сигнальні майданчики по периметру
    n = 6
    step = ls / (n + 1)
    pl = 22   # довжина майданчика
    pw = 12   # ширина
    for i in range(1, n + 1):
        cx = lx + i * step
        cy = ly + i * step
        p.append(rect(cx - pw/2, ly + 6, pw, pl - 6, fill=COPPER_L, stroke=COPPER, sw=1.4, rx=2))
        p.append(rect(cx - pw/2, ly + ls - pl, pw, pl - 6, fill=COPPER_L, stroke=COPPER, sw=1.4, rx=2))
        p.append(rect(lx + 6, cy - pw/2, pl - 6, pw, fill=COPPER_L, stroke=COPPER, sw=1.4, rx=2))
        p.append(rect(lx + ls - pl, cy - pw/2, pl - 6, pw, fill=COPPER_L, stroke=COPPER, sw=1.4, rx=2))
    # тепловий пад посередині
    ep = 110
    epx = lx + (ls - ep)/2
    epy = ly + (ls - ep)/2
    p.append(rect(epx, epy, ep, ep, fill=COPPER, stroke="#8a4f15", sw=1.6, rx=4))
    p.append(text(lx + ls/2, ly + ls/2 - 6, "тепловий", size=12, color="#ffffff", bold=True))
    p.append(text(lx + ls/2, ly + ls/2 + 10, "пад", size=12, color="#ffffff", bold=True))
    p.append(text(lx + ls/2, ly + ls + 22, "по краях — виводи, всередині — пад", size=11, color=MUTED))

    # --- ПРАВА панель: три шари сходинками ---
    rx, ry, rs = 470, 80, 130
    p.append(text(rx + rs/2, 58, "Посадкове місце = три шари", size=13, bold=True))

    def layer(yy, label, draw):
        p.append(rect(rx, yy, rs, rs*0.62, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        p.append(text(rx + rs + 12, yy + rs*0.31, label, size=11, color=INK, anchor="start"))
        draw(yy)

    def draw_copper(yy):
        ix, iy, iw, ih = rx + 22, yy + 12, rs - 44, rs*0.62 - 24
        p.append(rect(ix, iy, iw, ih, fill=COPPER, stroke="#8a4f15", sw=1.3, rx=3))
        for gx in range(1, 4):
            for gy in range(1, 3):
                p.append(circle(ix + gx*iw/4, iy + gy*ih/3, 3.0, fill="#5c3410", stroke="#8a4f15", sw=0.8))

    def draw_mask(yy):
        ix, iy, iw, ih = rx + 22, yy + 12, rs - 44, rs*0.62 - 24
        p.append(rect(ix, iy, iw, ih, fill="#fbe9d6", stroke=COPPER, sw=1.3, rx=3))
        p.append(text(rx + rs/2, yy + rs*0.62/2 + 4, "одне вікно", size=10, color=COPPER))

    def draw_paste(yy):
        ix, iy, iw, ih = rx + 22, yy + 12, rs - 44, rs*0.62 - 24
        nx, ny = 4, 3
        gap = 3
        cw = (iw - (nx + 1)*gap) / nx
        ch = (ih - (ny + 1)*gap) / ny
        for cxi in range(nx):
            for cyi in range(ny):
                qx = ix + gap + cxi*(cw + gap)
                qy = iy + gap + cyi*(ch + gap)
                p.append(rect(qx, qy, cw, ch, fill="#9aa0a6", stroke="#6b7280", sw=0.8, rx=1))

    layer(ry, "мідь: суцільно + отвори", draw_copper)
    layer(ry + 110, "маска: відкрити пад", draw_mask)
    layer(ry + 220, "паста: квадрати (windowpane)", draw_paste)

    fb = fitbox(60, 360, 360, 58,
                "Для виводів усі три шари збігаються. Для теплового паду —\n"
                "навмисно різні: мідь суцільна, маска відкрита, а паста —\n"
                "сіткою квадратів, бо суцільне вікно зіпсує паяння.",
                size=11.5, fill="#fff8ef", stroke=COPPER)
    p.append(fb)
    render(os.path.join(OUT, "epad-anatomy.svg"), W, H, *p)


# ── 8. Порожнини: суцільне вікно пасти проти сітки квадратів ─────────────────
def fig_paste_voids():
    W, H = 780, 410
    p = []
    p.append(text(W/2, 26, "Чому пад ділять на квадрати: газ флюсу проти порожнин", size=16, bold=True))

    base_y = 250
    th = 30   # товщина шару припою в розрізі

    # --- ЛІВА: суцільне вікно → порожнина ---
    lx, lw = 70, 290
    p.append(text(lx + lw/2, 66, "Суцільне вікно пасти", size=13, bold=True, color=HOT))
    p.append(rect(lx + 20, base_y - th - 40, lw - 40, 34, fill="#3a3a3a", stroke=INK, sw=1.4, rx=4))
    p.append(text(lx + lw/2, base_y - th - 20, "корпус", size=11, color="#ffffff", bold=True))
    p.append(rect(lx + 20, base_y - th, lw - 40, th, fill=COPPER_L, stroke=COPPER, sw=1.6, rx=3))
    p.append(circle(lx + lw/2, base_y - th/2, 11, fill="#9aa0a6", stroke="#6b7280", sw=1.4))
    p.append(circle(lx + lw/2 + 40, base_y - th/2, 6, fill="#9aa0a6", stroke="#6b7280", sw=1.2))
    p.append(arrow(lx + lw/2, base_y - th/2, lx + lw/2, base_y - th - 8, color=MUTED, sw=1.8))
    p.append(text(lx + lw/2, base_y + 20, "газ флюсу не встигає вийти →", size=11, color=HOT))
    p.append(text(lx + lw/2, base_y + 36, "застигає порожниною (void)", size=11, color=HOT, bold=True))
    p.append(rect(lx + 20, base_y, lw - 40, 12, fill=COPPER, stroke="#8a4f15", sw=1.2, rx=2))

    # --- ПРАВА: сітка квадратів → газ виходить ---
    rx0, rw = 420, 290
    p.append(text(rx0 + rw/2, 66, "Сітка квадратів (windowpane)", size=13, bold=True, color=FIELD))
    p.append(rect(rx0 + 20, base_y - th - 34, rw - 40, 34, fill="#3a3a3a", stroke=INK, sw=1.4, rx=4))
    p.append(text(rx0 + rw/2, base_y - th - 14, "корпус сів рівно", size=11, color="#ffffff", bold=True))
    n = 5
    gap = 8
    cw = (rw - 40 - (n + 1)*gap) / n
    for i in range(n):
        qx = rx0 + 20 + gap + i*(cw + gap)
        p.append(rect(qx, base_y - th + 6, cw, th - 6, fill=COPPER_L, stroke=COPPER, sw=1.4, rx=2))
        if i < n - 1:
            gxp = qx + cw + gap/2
            p.append(arrow(gxp, base_y - th + 8, gxp, base_y - th - 14, color=FIELD, sw=1.8))
    p.append(text(rx0 + rw/2, base_y + 20, "газ виходить проміжками →", size=11, color=FIELD))
    p.append(text(rx0 + rw/2, base_y + 36, "порожнин майже нема", size=11, color=FIELD, bold=True))
    p.append(rect(rx0 + 20, base_y, rw - 40, 12, fill=COPPER, stroke="#8a4f15", sw=1.2, rx=2))

    fb = fitbox(70, 332, 640, 56,
                "Паста = кульки припою + флюс; при оплавленні флюс кипить і дає газ. Покриття пастою\n"
                "роблять ~50–70 % площі квадратами: газ виходить, припою в міру, корпус не «спливає».\n"
                "Норма порожнин під падом: ≤ 25 % (IPC-A-610); стеля надійності IPC-7093 — 50 %.",
                size=12, fill=FILL, stroke=LINE)
    p.append(fb)
    render(os.path.join(OUT, "paste-voids.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spreader()
    fig_vias()
    fig_theta_curve()
    fig_trace_heating()
    fig_constriction()
    fig_spreading_curve()
    fig_epad_anatomy()
    fig_paste_voids()
    print("OK: 8 figures ->", OUT)
