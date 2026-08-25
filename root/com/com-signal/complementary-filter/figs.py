# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GYRO = NEG          # гіроскоп — синій
ACC  = POS          # акселерометр — червоний
TRUE = MUTED        # справжній кут — сірий


def _axes(p, ox, oy, aw, ah, xlabel="час"):
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, xlabel, size=12, color=INK, italic=True))


def _poly(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"%s/>' % (" ".join(pts), color, sw, d))


# ── mirror-errors: чому потрібні обидва давачі ────────────────────────────────
# Ідея: справжній кут (сірий) рівний; гіроскоп тримається близько, але повільно
# спливає (дрейф); акселерометр у середньому правильний, але тремтить (шум).
def fig_mirror_errors():
    W, H = 720, 320
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []
    _axes(p, ox, oy, aw, ah)
    p.append(text(ox - 14, oy - ah - 2, "кут", size=12, color=INK, bold=True, italic=True, anchor="end"))

    span = 10.0
    sx = aw / span
    base = oy - ah * 0.5          # рівень справжнього кута

    # справжній кут — рівна сіра лінія
    p.append(line(ox, base, ox + aw, base, color=TRUE, sw=2.2))
    p.append(text(ox + aw + 4, base + 4, "справжній", size=10, color=TRUE, anchor="start"))

    # гіроскоп: близько на початку, поволі спливає вгору (лінійний дрейф)
    gp = []
    for i in range(0, 401):
        t = span * i / 400.0
        wob = 1.5 * math.sin(2.3 * t)               # дрібні швидкі рухи ловить точно
        drift = -3.2 * t                            # повільне спливання (px), знак вгору
        gp.append("%.1f,%.1f" % (ox + t * sx, base + drift + wob * 0.0))
    p.append(_poly(gp, GYRO, 2.4))

    # акселерометр: у середньому на base, але швидкий шум
    import random
    random.seed(7)
    ap = []
    for i in range(0, 401):
        t = span * i / 400.0
        noise = 14.0 * (random.random() - 0.5)
        ap.append("%.1f,%.1f" % (ox + t * sx, base + noise))
    p.append(_poly(ap, ACC, 1.5))

    # легенда
    lx, ly = ox + 30, oy - ah + 6
    p.append(line(lx, ly, lx + 26, ly, color=GYRO, sw=2.4))
    p.append(text(lx + 32, ly + 4, "гіроскоп — повільно спливає (дрейф)", size=11, color=GYRO, anchor="start", bold=True))
    p.append(line(lx, ly + 20, lx + 26, ly + 20, color=ACC, sw=2.0))
    p.append(text(lx + 32, ly + 24, "акселерометр — швидкий шум, без дрейфу", size=11, color=ACC, anchor="start", bold=True))

    render(os.path.join(OUT, "mirror-errors.svg"), W, H, *p,
           title="Помилки дзеркальні: один поганий там, де другий добрий")


# ── split-by-frequency: поділ за частотою ─────────────────────────────────────
# Ідея: частотну вісь ділять межею; низькі частоти бере акселерометр, високі —
# гіроскоп.
def fig_split_by_frequency():
    W, H = 720, 250
    ox, oy = 70, 180
    aw, ah = 600, 120
    p = []
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "частота", size=12, color=INK, italic=True))

    fc = ox + aw * 0.45
    # ліва зона — акселерометр (низькі)
    p.append(rect(ox, oy - ah, fc - ox, ah, fill="#fdecea", stroke="none", sw=0, rx=0))
    # права зона — гіроскоп (високі)
    p.append(rect(fc, oy - ah, ox + aw - fc, ah, fill="#eaf0fd", stroke="none", sw=0, rx=0))
    # межа
    p.append(line(fc, oy - ah, fc, oy + 6, color=INK, sw=1.6, dash="5 4"))
    p.append(text(fc, oy - ah - 8, "межа: стала часу τ", size=11, color=INK, bold=True))

    p.append(text((ox + fc) / 2, oy - ah / 2 - 6, "НИЗЬКІ частоти", size=13, color=ACC, bold=True))
    p.append(text((ox + fc) / 2, oy - ah / 2 + 14, "акселерометр", size=12, color=ACC))
    p.append(text((ox + fc) / 2, oy - ah / 2 + 32, "(повільна правда, без дрейфу)", size=9, color=ACC))

    p.append(text((fc + ox + aw) / 2, oy - ah / 2 - 6, "ВИСОКІ частоти", size=13, color=GYRO, bold=True))
    p.append(text((fc + ox + aw) / 2, oy - ah / 2 + 14, "гіроскоп", size=12, color=GYRO))
    p.append(text((fc + ox + aw) / 2, oy - ah / 2 + 32, "(швидкі рухи, без шуму)", size=9, color=GYRO))

    render(os.path.join(OUT, "split-by-frequency.svg"), W, H, *p,
           title="Стратегія: поділити сигнал за частотою і скласти")


# ── complement-sum-one: ФВЧ + ФНЧ = 1 ─────────────────────────────────────────
# Ідея: дві дзеркальні криві (ФНЧ червона, ФВЧ синя) перетинаються на −3 дБ;
# їхня сума — рівно одиниця (зелена пряма) на всіх частотах.
def fig_complement_sum_one():
    W, H = 720, 300
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []
    _axes(p, ox, oy, aw, ah, xlabel="частота")
    p.append(text(ox - 14, oy - ah - 2, "коеф.", size=11, color=INK, italic=True, anchor="end"))

    top = oy - ah                       # рівень 1.0
    half = oy - ah * 0.707              # рівень ≈ −3 дБ (0.707)
    p.append(line(ox, top, ox + aw, top, color="#d9d9d9", sw=1.0, dash="3 3"))
    p.append(text(ox - 6, top + 4, "1", size=10, color=MUTED, anchor="end"))

    fc_frac = 0.45
    # ФНЧ: 1 → 0 (спадає), перша-порядкова
    lp = []
    hp = []
    su = []
    for i in range(0, 401):
        f = i / 400.0
        r = f / fc_frac
        lpf = 1.0 / (1.0 + r * r) ** 0.5
        hpf = r / (1.0 + r * r) ** 0.5
        # сума амплітуд не точно 1 для першого порядку, тож показуємо
        # комплементарну пару, де hp = 1 - lp (саме така умова в фільтрі)
        hpf = 1.0 - lpf
        s = lpf + hpf
        xpix = ox + f * aw
        lp.append("%.1f,%.1f" % (xpix, oy - lpf * ah))
        hp.append("%.1f,%.1f" % (xpix, oy - hpf * ah))
        su.append("%.1f,%.1f" % (xpix, oy - s * ah))

    p.append(_poly(lp, ACC, 2.4))
    p.append(_poly(hp, GYRO, 2.4))
    p.append(_poly(su, FIELD, 2.8))

    fcx = ox + fc_frac * aw
    p.append(line(fcx, oy, fcx, half, color=MUTED, sw=1.0, dash="4 3"))
    p.append(circle(fcx, half, 3.0, fill=INK, stroke=INK, sw=1))
    p.append(text(fcx, oy + 18, "f_c (−3 дБ)", size=10, color=MUTED))

    # підписи кривих
    p.append(text(ox + aw * 0.12, oy - 0.86 * ah, "ФНЧ (акселерометр)", size=11, color=ACC, anchor="start", bold=True))
    p.append(text(ox + aw * 0.62, oy - 0.86 * ah, "ФВЧ (гіроскоп)", size=11, color=GYRO, anchor="start", bold=True))
    p.append(text(ox + aw * 0.5, oy - 1.02 * ah - 6, "ФВЧ + ФНЧ = 1", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "complement-sum-one.svg"), W, H, *p,
           title="Чому «комплементарний»: два фільтри в сумі дають рівно 1")


# ── dataflow: потік даних фільтра ─────────────────────────────────────────────
# Ідея: дві гілки (гіро→інтеграл, аксель→atan2) зливаються у зважену суму, що
# повертається назад як попередня оцінка.
def fig_dataflow():
    W, H = 740, 300
    p = []
    bw, bh = 132, 50

    # гілка гіроскопа (верх)
    gy = 80
    g1 = fitbox(40, gy - bh / 2, bw, bh, "гіроскоп ω", size=12, fill="#eaf0fd", stroke=GYRO, sw=1.8, bold=True, color=GYRO)
    g2 = fitbox(40 + 180, gy - bh / 2, bw, bh, "інтеграл\nкут + ω·dt", size=11, fill="#eaf0fd", stroke=GYRO, sw=1.6, color=INK)
    p += [g1, g2]
    p.append(arrow(40 + bw, gy, 40 + 180 - 2, gy, color=GYRO, sw=1.7))

    # гілка акселерометра (низ)
    ay = 220
    a1 = fitbox(40, ay - bh / 2, bw, bh, "акселерометр", size=12, fill="#fdecea", stroke=ACC, sw=1.8, bold=True, color=ACC)
    a2 = fitbox(40 + 180, ay - bh / 2, bw, bh, "atan2(a_y,a_z)\nкут_акс", size=11, fill="#fdecea", stroke=ACC, sw=1.6, color=INK)
    p += [a1, a2]
    p.append(arrow(40 + bw, ay, 40 + 180 - 2, ay, color=ACC, sw=1.7))

    # вузол суми
    sx, sy = 540, 150
    s, sw_, sh = textbox(sx, sy, "зважена сума\nα·гіро + (1−α)·аксель", size=12, bold=True,
                         fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(s)

    # стрілки в суму
    p.append(line(40 + 180 + bw, gy, sx - sw_ / 2, sy - 14, color=GYRO, sw=1.7))
    p.append(line(40 + 180 + bw, ay, sx - sw_ / 2, sy + 14, color=ACC, sw=1.7))
    p.append(text(40 + 180 + bw + 26, gy - 6, "×α", size=11, color=GYRO, bold=True))
    p.append(text(40 + 180 + bw + 18, ay + 16, "×(1−α)", size=11, color=ACC, bold=True))

    # вихід оцінки + петля назад
    out, ow, oh = textbox(sx, sy + 100, "оцінка кута", size=12, bold=True, fill=FILL, stroke=INK, sw=1.6)
    p.append(out)
    p.append(arrow(sx, sy + sh / 2, sx, sy + 100 - oh / 2 - 2, color=INK, sw=1.7))

    # петля назад до інтеграла
    bx = sx - sw_ / 2
    p.append(line(sx, sy + 100 + oh / 2, sx, sy + 100 + oh / 2 + 24, color=MUTED, sw=1.4, dash="5 4"))
    p.append(line(sx, sy + 100 + oh / 2 + 24, 40 + 180 + bw / 2, sy + 100 + oh / 2 + 24, color=MUTED, sw=1.4, dash="5 4"))
    p.append(arrow(40 + 180 + bw / 2, sy + 100 + oh / 2 + 24, 40 + 180 + bw / 2, gy + bh / 2 + 2, color=MUTED, sw=1.4))
    p.append(text((40 + 180 + bw / 2 + sx) / 2, sy + 100 + oh / 2 + 38, "попередня оцінка", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "dataflow.svg"), W, H, *p,
           title="Потік даних: дві гілки зливаються в одну зважену суму")


# ── fused-estimate: поєднана оцінка гладка й без дрейфу ────────────────────────
def fig_fused_estimate():
    W, H = 720, 300
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []
    _axes(p, ox, oy, aw, ah)
    p.append(text(ox - 14, oy - ah - 2, "кут", size=12, color=INK, bold=True, italic=True, anchor="end"))

    span = 10.0
    sx = aw / span
    # справжній кут — пологий підйом-сходинка
    def truth(t):
        return 0.5 + 0.28 * (1.0 - math.exp(-0.9 * t))

    # справжній (сірий пунктир)
    tp = []
    for i in range(0, 401):
        t = span * i / 400.0
        tp.append("%.1f,%.1f" % (ox + t * sx, oy - truth(t) * ah))
    p.append(_poly(tp, TRUE, 2.0, dash="6 4"))
    p.append(text(ox + aw + 4, oy - truth(span) * ah + 4, "справжній", size=9, color=TRUE, anchor="start"))

    # дрейфливий гіроскоп (блідо-синій)
    gp = []
    for i in range(0, 401):
        t = span * i / 400.0
        gp.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) - 0.018 * t) * ah))
    p.append(_poly(gp, "#9fb6ef", 1.8))

    # шумний акселерометр (блідо-червоний)
    import random
    random.seed(3)
    ap = []
    for i in range(0, 401):
        t = span * i / 400.0
        ap.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) + 0.05 * (random.random() - 0.5)) * ah))
    p.append(_poly(ap, "#f0a59c", 1.3))

    # поєднана оцінка (зелена, щільно по справжньому)
    fp = []
    for i in range(0, 401):
        t = span * i / 400.0
        fp.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) + 0.004 * math.sin(5 * t)) * ah))
    p.append(_poly(fp, FIELD, 2.8))

    # легенда
    lx, ly = ox + 28, oy - ah + 8
    for i, (c, lab, swv) in enumerate([("#9fb6ef", "гіроскоп (дрейф)", 1.8),
                                       ("#f0a59c", "акселерометр (шум)", 1.3),
                                       (FIELD, "поєднана оцінка", 2.8)]):
        p.append(line(lx, ly + i * 18, lx + 24, ly + i * 18, color=c, sw=swv))
        p.append(text(lx + 30, ly + i * 18 + 4, lab, size=10, color=c, anchor="start", bold=(i == 2)))

    render(os.path.join(OUT, "fused-estimate.svg"), W, H, *p,
           title="Поєднана оцінка: гладка, як гіроскоп, без дрейфу, як акселерометр")


# ── choosing-alpha: компроміс між дрейфом і шумом ─────────────────────────────
def fig_choosing_alpha():
    W, H = 720, 300
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []
    _axes(p, ox, oy, aw, ah)
    p.append(text(ox - 14, oy - ah - 2, "кут", size=12, color=INK, bold=True, italic=True, anchor="end"))

    span = 10.0
    sx = aw / span
    def truth(t):
        return 0.5 + 0.30 * (1.0 - math.exp(-1.1 * t))
    tp = []
    for i in range(0, 401):
        t = span * i / 400.0
        tp.append("%.1f,%.1f" % (ox + t * sx, oy - truth(t) * ah))
    p.append(_poly(tp, TRUE, 1.6, dash="6 4"))

    import random
    random.seed(11)
    # завелике α=0.995 (синє): гладко, але тягне залишковий дрейф і мляво
    big = []
    for i in range(0, 401):
        t = span * i / 400.0
        big.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) - 0.03 - 0.012 * t) * ah))
    p.append(_poly(big, GYRO, 2.2))

    # замале α=0.90 (червоне): швидко тримає правду, але шумить
    sm = []
    for i in range(0, 401):
        t = span * i / 400.0
        sm.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) + 0.07 * (random.random() - 0.5)) * ah))
    p.append(_poly(sm, ACC, 1.4))

    # збалансоване α=0.98 (зелене)
    bal = []
    for i in range(0, 401):
        t = span * i / 400.0
        bal.append("%.1f,%.1f" % (ox + t * sx, oy - (truth(t) + 0.006 * math.sin(6 * t)) * ah))
    p.append(_poly(bal, FIELD, 2.8))

    lx, ly = ox + 28, oy - ah + 8
    for i, (c, lab, swv) in enumerate([(GYRO, "α=0.995 — гладко, але мляво й тягне дрейф", 2.2),
                                       (ACC, "α=0.90 — швидко, але протікає шум", 1.4),
                                       (FIELD, "α=0.98 — баланс: гладко й без дрейфу", 2.8)]):
        p.append(line(lx, ly + i * 18, lx + 24, ly + i * 18, color=c, sw=swv))
        p.append(text(lx + 30, ly + i * 18 + 4, lab, size=10, color=c, anchor="start", bold=(i == 2)))

    render(os.path.join(OUT, "choosing-alpha.svg"), W, H, *p,
           title="Вибір α: гладкість ↔ швидкість реакції")


# ── accel-lies: тривале прискорення обманює акселерометр ──────────────────────
# Ідея: у спокої вектор = g (вниз) → правильний «низ»; під час розгону вектор =
# g + a, нахилений → опорний кут бреше.
def fig_accel_lies():
    W, H = 720, 290
    p = []

    def panel(cx, title, show_a):
        gp = []
        oy = 230
        # тіло апарата — простий прямокутник
        gp.append(rect(cx - 46, oy - 150, 92, 30, fill=FILL, stroke=INK, sw=1.6, rx=4))
        gp.append(text(cx, oy - 150 - 8, title, size=12, color=INK, bold=True))
        # точка кріплення давача
        px, py = cx, oy - 120
        gp.append(circle(px, py, 3.5, fill=INK, stroke=INK, sw=1))
        # вектор g — завжди вниз
        glen = 70
        gp.append(arrow(px, py, px, py + glen, color=NEG, sw=2.6))
        gp.append(text(px - 10, py + glen - 6, "g", size=13, color=NEG, bold=True, italic=True, anchor="end"))
        if show_a:
            # вектор a — горизонтальний (розгін уперед)
            alen = 56
            gp.append(arrow(px, py, px + alen, py, color=ACC, sw=2.6))
            gp.append(text(px + alen + 4, py - 4, "a", size=13, color=ACC, bold=True, italic=True, anchor="start"))
            # сума g + a — нахилена (виміряний «низ»)
            sxp, syp = px + alen, py + glen
            gp.append(arrow(px, py, sxp, syp, color=FIELD, sw=2.8))
            gp.append(text(sxp + 6, syp, "g + a", size=12, color=FIELD, bold=True, anchor="start"))
            gp.append(text(cx, oy + 36, "«низ» відхилився → кут бреше", size=11, color=ACC))
        else:
            gp.append(text(cx, oy + 36, "«низ» правильний (чисте g)", size=11, color=NEG))
        return gp

    p += panel(190, "Спокій", False)
    p += panel(530, "Тривалий розгін", True)
    # роздільник
    p.append(line(360, 60, 360, 250, color="#e0e0e0", sw=1.2, dash="4 4"))

    p.append(text(W / 2, H - 14,
                  "короткі поштовхи ФНЧ згладжує; тривале прискорення фільтр від нахилу не відрізнить",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "accel-lies.svg"), W, H, *p,
           title="Слабке місце: тривале прискорення обманює акселерометр")


if __name__ == "__main__":
    fig_mirror_errors()
    fig_split_by_frequency()
    fig_complement_sum_one()
    fig_dataflow()
    fig_fused_estimate()
    fig_choosing_alpha()
    fig_accel_lies()
    print("OK: figures written to", OUT)
