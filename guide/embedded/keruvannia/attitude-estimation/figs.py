# -*- coding: utf-8 -*-
"""Фігури теми «Оцінка орієнтації». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: передбач-і-виправ ──────────────────────────────────────────────
# Гіроскоп інтегрується вперед і ПОВЗЕ геть від правди (дрейф). Акселерометр/
# магнітометр щоразу ПІДТЯГУЮТЬ оцінку назад до істини. Видно дві швидкості.
def fig_predict_correct():
    W, H = 720, 360
    L, R = 70, 690          # межі графіка по X (час)
    T, B = 60, 300          # межі по Y (кут)
    truth_y = 210           # справжній кут — горизонталь
    parts = []

    # осі
    parts.append(line(L, B, R, B, color=MUTED, sw=1.5))      # вісь часу
    parts.append(line(L, T, L, B, color=MUTED, sw=1.5))      # вісь кута
    parts.append(text((L + R) / 2, B + 30, "час →", size=13, color=MUTED))
    parts.append(text(L - 12, T + 4, "кут", size=13, color=MUTED, anchor="end"))

    # справжній кут (істина)
    parts.append(line(L, truth_y, R, truth_y, color=FIELD, sw=2.4, dash="2 5"))
    parts.append(text(R - 4, truth_y - 10, "справжній кут", size=12,
                      color=FIELD, anchor="end"))

    # «голий» інтеграл гіроскопа — повзе вгору без упину (дрейф)
    drift = []
    for i in range(0, 101):
        x = L + (R - L) * i / 100.0
        y = truth_y - 0.95 * (R - L) * (i / 100.0) ** 1.25 * 0.30
        drift.append((x, y))
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in drift)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-dasharray="6 4"/>' % (dpath, POS))
    parts.append(text(R - 4, drift[-1][1] + 14, "сам гіроскоп (дрейфує)",
                      size=12, color=POS, anchor="end"))

    # оцінка з виправленням — пилкоподібна: між корекціями повзе як гіро,
    # у мить корекції стрибає назад до істини
    n_corr = 7
    seg = (R - L) / n_corr
    est = [(L, truth_y)]
    cur_off = 0.0
    for k in range(n_corr):
        x0 = L + k * seg
        x1 = L + (k + 1) * seg
        # повзе вгору протягом сегмента (як гіро, але на короткому масштабі)
        rise = 26.0
        steps = 8
        for s in range(1, steps + 1):
            x = x0 + (x1 - x0) * s / steps
            y = truth_y - cur_off - rise * (s / steps)
            est.append((x, y))
        cur_off = 6.0      # корекція стягнула майже до істини (лишився малий залишок)
        est.append((x1, truth_y - cur_off))
    epath = "M " + " L ".join("%.1f %.1f" % p for p in est)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (epath, NEG))
    # стрілки-корекції вниз у точках стягування
    for k in range(1, n_corr + 1):
        x = L + k * seg
        parts.append(arrow(x, truth_y - 30, x, truth_y - 8, color=NEG, sw=1.4))
    parts.append(text(L + 6, T + 18, "оцінка = гіро + корекція", size=12,
                      color=NEG, anchor="start"))

    # легенда-підказка коротко
    parts.append(line(L + 4, B - 14, L + 24, B - 14, color=NEG, sw=2.4))
    parts.append(text(L + 30, B - 10, "сині стрілки — корекція від акселерометра/магнітометра",
                      size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "predict-correct.svg"), W, H, *parts,
           title="Передбач гіроскопом — виправ акселерометром")


# ── Фігура 2: блокування шарнірів (gimbal lock) ──────────────────────────────
# Три кільця карданового підвісу. У нормі осі різні; коли середнє кільце
# повертає вісь на 90°, зовнішнє й внутрішнє кільця стають співвісні —
# два повороти роблять те саме, один ступінь свободи зник.
def fig_gimbal_lock():
    W, H = 720, 330
    parts = []

    def gimbal(cx, cy, locked, label):
        out = []
        # зовнішнє кільце — горизонтальна вісь (еліпс «плазом»)
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="92" ry="34" fill="none" '
                   'stroke="%s" stroke-width="3"/>' % (cx, cy, POS))
        if not locked:
            # середнє кільце — нахилене (інша вісь)
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="66" ry="80" fill="none" '
                       'stroke="%s" stroke-width="3"/>' % (cx, cy, NEG))
            # внутрішнє — вертикальне (третя вісь)
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="30" ry="62" fill="none" '
                       'stroke="%s" stroke-width="3"/>' % (cx, cy, FIELD))
        else:
            # середнє повернуте на 90° → внутрішня вісь лягла на зовнішню:
            # обидва кільця тепер «плазом» — співвісні
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="66" ry="24" fill="none" '
                       'stroke="%s" stroke-width="3"/>' % (cx, cy, NEG))
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="40" ry="15" fill="none" '
                       'stroke="%s" stroke-width="3"/>' % (cx, cy, FIELD))
            # подвійна стрілка — два повороти дають той самий рух
            out.append(arrow(cx - 58, cy + 58, cx - 20, cy + 58, color=INK, sw=1.6))
            out.append(arrow(cx + 58, cy + 58, cx + 20, cy + 58, color=INK, sw=1.6))
            out.append(text(cx, cy + 78, "обидві осі крутять однаково",
                            size=12, color=INK))
        # тіло в центрі
        out.append(circle(cx, cy, 9, fill=FILL, stroke=INK, sw=1.5))
        out.append(text(cx, cy - 108, label, size=14, bold=True))
        return "".join(out)

    parts.append(gimbal(195, 150, False, "три різні осі — повна свобода"))
    parts.append(gimbal(530, 150, True,  "вісь на 90° — блокування"))

    # підпис осей у лівій схемі
    parts.append(text(195, 150 + 56, "крен", size=11, color=POS))
    parts.append(text(195 + 96, 150, "тангаж", size=11, color=NEG, anchor="start"))
    parts.append(text(195, 150 - 74, "курс", size=11, color=FIELD))

    render(os.path.join(IMG, "gimbal-lock.svg"), W, H, *parts,
           title="Блокування шарнірів: коли дві осі зливаються")


# ── Фігура 3: комплементарний фільтр як поділ за частотою ─────────────────────
# Гіроскоп несе ШВИДКІ зміни (вирізаємо повільний дрейф — фільтр верхніх частот).
# Акселерометр несе ПОВІЛЬНУ правду (вирізаємо швидкий шум — нижніх частот).
# Сума двох смуг = повна, чесна оцінка.
def fig_complementary():
    W, H = 720, 330
    parts = []

    def band(x, y, w, h, kind, color, caption):
        out = [rect(x, y, w, h, fill="#ffffff", stroke=MUTED, sw=1.2)]
        mid = y + h / 2
        # вісь частоти
        out.append(line(x + 10, mid, x + w - 10, mid, color=MUTED, sw=1))
        # крива пропускання
        pts = []
        for i in range(0, 61):
            fx = x + 14 + (w - 28) * i / 60.0
            t = i / 60.0
            if kind == "high":          # верхні частоти: 0→1
                g = 1.0 / (1.0 + math.exp(-(t - 0.45) * 12))
            else:                        # нижні частоти: 1→0
                g = 1.0 - 1.0 / (1.0 + math.exp(-(t - 0.45) * 12))
            fy = (y + h - 12) - (h - 24) * g
            pts.append((fx, fy))
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                   % (path, color))
        out.append(text(x + w / 2, y - 8, caption, size=12, bold=True, color=color))
        out.append(text(x + 16, y + h + 16, "повільне", size=10,
                        color=MUTED, anchor="start"))
        out.append(text(x + w - 16, y + h + 16, "швидке", size=10,
                        color=MUTED, anchor="end"))
        return "".join(out), x + w, mid

    box_w, box_h, top = 188, 96, 70
    g1, gx, gmid = band(40, top, box_w, box_h, "high", NEG, "гіроскоп (швидке)")
    g2, ax, amid = band(40, top + box_h + 34, box_w, box_h, "low", POS, "акселерометр (повільне)")
    parts.append(g1)
    parts.append(g2)

    # знак суми
    sum_cx = 300
    parts.append(arrow(gx + 6, gmid, sum_cx - 22, top + box_h + 6, color=MUTED, sw=1.4))
    parts.append(arrow(ax + 6, amid, sum_cx - 22, top + box_h + 28, color=MUTED, sw=1.4))
    parts.append(plus(sum_cx, top + box_h + 17, r=13))

    # результат — повна смуга
    res = rect(360, top + 6, 320, box_h + 22, fill="#ffffff", stroke=FIELD, sw=2)
    parts.append(res)
    ry = top + 6 + (box_h + 22) / 2
    parts.append(line(370, ry, 670, ry, color=MUTED, sw=1))
    full = "M " + " L ".join("%.1f %.1f" % (370 + 300 * i / 60.0, ry - 30) for i in range(0, 61))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (full, FIELD))
    parts.append(text(520, top - 6, "повна оцінка орієнтації", size=13, bold=True, color=FIELD))
    parts.append(text(370, ry + 46, "повільне", size=10, color=MUTED, anchor="start"))
    parts.append(text(670, ry + 46, "швидке", size=10, color=MUTED, anchor="end"))
    parts.append(text(520, ry + 30, "рівне пропускання на всіх частотах",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "complementary.svg"), W, H, *parts,
           title="Комплементарний фільтр: кожен давач у своїй смузі")


# ── Фігура 4: похибка як векторний добуток (геометрія Mahony) ─────────────────
# Куля одиничних напрямків. v̂ — куди «низ» дивиться ЗА поточною оцінкою.
# v — куди акселерометр КАЖЕ, що низ. Між ними кут. Векторний добуток
# e = v × v̂ дає вісь, навколо якої треба докрутити оцінку, і величину ≈ sin кута.
def fig_cross_error():
    W, H = 720, 360
    cx, cy, Rr = 250, 195, 130
    parts = []

    # куля (коло + екватор-еліпс для об'єму)
    parts.append(circle(cx, cy, Rr, fill="#fbfcfd", stroke=MUTED, sw=1.5))
    parts.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="34" fill="none" '
                 'stroke="%s" stroke-width="1" stroke-dasharray="4 4"/>'
                 % (cx, cy, Rr, MUTED))
    parts.append(circle(cx, cy, 3.5, fill=INK, stroke=INK, sw=1))
    parts.append(text(cx, cy + 18, "центр", size=10, color=MUTED))

    # два одиничні вектори з центра: оцінка (зелений) і вимір (червоний)
    import math as _m
    a_hat = _m.radians(-72)      # напрям очікуваного «низу» (за оцінкою)
    a_mes = _m.radians(-52)      # напрям виміряного «низу» (акселерометр)
    hx, hy = cx + Rr * _m.cos(a_hat), cy + Rr * _m.sin(a_hat)
    mx, my = cx + Rr * _m.cos(a_mes), cy + Rr * _m.sin(a_mes)
    parts.append(arrow(cx, cy, hx, hy, color=FIELD, sw=2.6))
    parts.append(arrow(cx, cy, mx, my, color=POS, sw=2.6))
    parts.append(text(hx + 6, hy - 6, "v̂ — очікуваний «низ»", size=12,
                      color=FIELD, anchor="start"))
    parts.append(text(mx + 8, my - 2, "v — вимір акселерометра", size=12,
                      color=POS, anchor="start"))

    # дуга кута похибки між ними
    parts.append('<path d="M %.1f %.1f A 56 56 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6"/>'
                 % (cx + 56 * _m.cos(a_mes), cy + 56 * _m.sin(a_mes),
                    cx + 56 * _m.cos(a_hat), cy + 56 * _m.sin(a_hat), INK))
    midang = (a_hat + a_mes) / 2
    parts.append(text(cx + 78 * _m.cos(midang), cy + 78 * _m.sin(midang),
                      "кут похибки", size=11, color=INK))

    # вектор похибки e = v × v̂ — перпендикулярний площині, тут «з кулі на нас»
    ex, ey = cx - 4, cy - Rr - 6
    parts.append(arrow(cx, cy, ex, ey - 30, color=NEG, sw=2.4))
    parts.append(text(ex + 6, ey - 36, "e = v × v̂", size=13, color=NEG,
                      bold=True, anchor="start"))
    parts.append(text(ex + 6, ey - 20, "вісь, навколо якої докрутити", size=11,
                      color=NEG, anchor="start"))

    # пояснення праворуч
    bx = 470
    parts.append(fitbox(bx, 70, 232, 96,
                 "Збіглися v і v̂ →\ne = 0 → корекції нема.\n\n"
                 "Розійшлися → e показує\nі НАСКІЛЬКИ, і В ЯКИЙ БІК\nкрутити оцінку.",
                 size=12, fill="#eef7f0", stroke=FIELD))
    parts.append(fitbox(bx, 182, 232, 70,
                 "|e| ≈ sin(кута похибки):\nмала похибка — мала\nкорекція, велика — більша.",
                 size=12, fill="#eaf0fd", stroke=NEG))
    parts.append(fitbox(bx, 268, 232, 64,
                 "Жодних кутів Ейлера й\nарктангенсів — самий\nвекторний добуток. Дешево.",
                 size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, "cross-error.svg"), W, H, *parts,
           title="Похибка орієнтації як векторний добуток")


# ── Фігура 5: ПІ-корекція Mahony (блок-схема одного такту) ────────────────────
# Гіро − зсув, + Kp·e → інтегруємо в кватерніон. Ki·e інтегрується В зсув
# (онлайн-оцінка дрейфу). Видно дві петлі: швидку (кут) і повільну (зсув).
def fig_mahony_pi():
    W, H = 760, 340
    parts = []

    def box(x, y, w, h, s, col=INK, fill=FILL):
        return fitbox(x, y, w, h, s, size=12, fill=fill, stroke=col, bold=True), x, y, w, h

    # вхід: гіроскоп
    g, gx, gy, gw, gh = box(30, 150, 96, 46, "гіроскоп\nΩ (рад/с)", col=NEG)
    parts.append(g)
    # суматор Ω − b̂ + Kp·e
    sumx, sumy = 200, 173
    parts.append(circle(sumx, sumy, 18, fill="#ffffff", stroke=INK, sw=1.6))
    parts.append(text(sumx, sumy + 4, "Σ", size=16, bold=True))
    parts.append(arrow(gx + gw, gy + gh / 2, sumx - 18, sumy, color=NEG, sw=1.8))

    # інтегратор кватерніона
    qi, qix, qiy, qiw, qih = box(300, 150, 150, 46,
                                 "q ← q + ½·q⊗(0,ω)·Δt\nнормувати q", col=FIELD)
    parts.append(qi)
    parts.append(arrow(sumx + 18, sumy, qix, qiy + qih / 2, color=INK, sw=1.8))
    parts.append(text((sumx + 18 + qix) / 2, sumy - 8, "ω", size=12, color=INK))

    # вихід: орієнтація
    o, ox, oy, ow, oh = box(540, 150, 110, 46, "орієнтація\n(кватерніон)", col=FIELD)
    parts.append(o)
    parts.append(arrow(qix + qiw, qiy + qih / 2, ox, oy + oh / 2, color=FIELD, sw=2.2))

    # блок похибки e = v × v̂ (з акселерометра + поточної оцінки)
    e, ex, ey, ew, eh = box(300, 250, 150, 46,
                            "e = v(акс) × v̂(q)\nпохибка напряму", col=POS)
    parts.append(e)
    # від орієнтації вниз у блок похибки (потрібна q, щоб знати v̂)
    parts.append(arrow(ox + ow / 2, oy + oh, ox + ow / 2, ey + eh / 2,
                       color=MUTED, sw=1.4))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.4"/>' % (ex + ew, ey + eh / 2,
                                            ox + ow / 2, ey + eh / 2, MUTED))
    parts.append(text(ox + ow / 2 + 6, ey + eh / 2 - 6, "v̂(q)", size=10,
                      color=MUTED, anchor="start"))

    # ШВИДКА петля: + Kp·e у суматор
    parts.append(arrow(ex, ey + eh / 2, sumx, sumy + 18, color=POS, sw=1.8))
    parts.append(text((ex + sumx) / 2 - 6, ey + eh / 2 + 16, "+ Kp·e",
                      size=12, color=POS, bold=True))

    # ПОВІЛЬНА петля: Ki·e інтегрується у зсув b̂, що віднімається у суматорі
    bi, bix, biy, biw, bih = box(60, 250, 150, 46,
                                 "b̂ ← b̂ + Ki·e·Δt\nоцінка зсуву гіро", col=NEG)
    parts.append(bi)
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.6"/>' % (ex, ey + eh / 2, bix + biw, biy + bih / 2, POS))
    parts.append(arrow(bix + biw / 2, biy, sumx, sumy + 18, color=NEG, sw=1.8))
    parts.append(text(bix + biw / 2 - 30, biy - 6, "− b̂", size=12,
                      color=NEG, bold=True, anchor="start"))

    # підписи двох петель
    parts.append(text(150, 120, "ШВИДКА петля: підтягни кут зараз  (Kp)",
                      size=11, color=POS, anchor="start"))
    parts.append(text(150, 320, "ПОВІЛЬНА петля: вилови й відніми зсув гіро  (Ki)",
                      size=11, color=NEG, anchor="start"))

    render(os.path.join(IMG, "mahony-pi.svg"), W, H, *parts,
           title="Mahony: дві петлі ПІ-корекції за один такт")


# ── Фігура 6 (вставка hist): сторіччя кватерніонів ───────────────────────────
# Часова стрічка історії: яскравий спалах 1843 (Гамільтон), довга «зима»,
# коли перемогла векторна алгебра, і пізнє повернення через космос і графіку.
# Висота кривої = «в моді» / «в забутті». Несе суть вставки одним поглядом.
def fig_quaternion_timeline():
    W, H = 760, 360
    L, R = 80, 700           # межі осі часу
    base = 270               # лінія часу
    parts = []

    def X(year):
        return L + (R - L) * (year - 1840) / (2000 - 1840)

    # «крива моди» кватерніонів у часі (0…1)
    def fashion(yr):
        if yr < 1843:
            return 0.12
        if yr < 1865:
            return 0.85                                   # розквіт, школа Тейта
        if yr < 1895:
            return 0.85 - 0.70 * (yr - 1865) / 30.0       # спад: перемога векторів
        if yr < 1958:
            return 0.13                                   # «зима» — майже забуто
        if yr < 1985:
            return 0.13 + 0.40 * (yr - 1958) / 27.0       # підйом: космос, strapdown
        return 0.53 + 0.34 * (yr - 1985) / 15.0           # графіка, робототехніка

    def Y(yr):
        return base - 10 - 165 * fashion(yr)

    # вісь часу + риски
    parts.append(line(L, base, R, base, color=INK, sw=2))
    for yr in (1840, 1880, 1920, 1960, 2000):
        x = X(yr)
        parts.append(line(x, base - 5, x, base + 5, color=MUTED, sw=1.4))
        parts.append(text(x, base + 22, str(yr), size=12, color=MUTED))

    # крива
    pts = [(X(1840 + i), Y(1840 + i)) for i in range(0, 161)]
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (path, NEG))

    # зона «зими»
    parts.append(text((X(1900) + X(1958)) / 2, base - 28,
                      "довга «зима» кватерніонів", size=12,
                      color=MUTED, italic=True))
    parts.append(text(X(1854), Y(1854) - 12, "розквіт: школа Тейта",
                      size=11, color=NEG))

    # маркери подій: точка на кривій + виноска-рамка
    def event(year, box_x, box_y, label, color):
        x, y = X(year), Y(year)
        parts.append(circle(x, y, 5, fill=color, stroke=color, sw=1))
        parts.append(line(x, y, box_x + 70, box_y + (30 if box_y < y else 0),
                          color=MUTED, sw=1))
        parts.append(fitbox(box_x, box_y, 150, 32, label, size=10.5,
                            stroke=color))

    event(1843, 92,  295, "1843 — Гамільтон:\ni²=j²=k²=ijk=−1", POS)
    event(1890, 250, 50,  "1880-ті — «велика війна»:\nперемогли вектори", MUTED)
    event(1969, 300, 300, "1960-ті — космос: Apollo,\nбезкарданні системи", FIELD)
    event(1985, 540, 60,  "1985 — комп'ютерна\nграфіка (Шумейк)", FIELD)

    render(os.path.join(IMG, "quaternion-timeline.svg"), W, H, *parts,
           title="Сторіччя кватерніонів: спалах, забуття, повернення")


if __name__ == "__main__":
    fig_predict_correct()
    fig_gimbal_lock()
    fig_complementary()
    fig_cross_error()
    fig_mahony_pi()
    fig_quaternion_timeline()
    print("OK: 6 figures ->", IMG)
