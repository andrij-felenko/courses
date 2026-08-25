# -*- coding: utf-8 -*-
"""Фігури до теми «Q полюсів фільтра» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  pole-pair.svg     — s-площина: пара спряжених полюсів, ω₀ = відстань від нуля, кут θ, Q = 1/(2cosθ)
  q-peaking.svg     — АЧХ однієї ланки 2-го порядку для кількох Q: поріг піка Q = 1/√2 ≈ 0.707
  q-step.svg        — реакція на сходинку для тих самих Q: викид і дзвін ростуть із Q
  biquad-cascade.svg— фільтр 4-го порядку = дві біквад-ланки, кожна зі своїм (ω₀, Q); родина = рецепт Q
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def pole_pair():
    """s-площина: пара спряжених полюсів. Відстань до нуля = ω₀; кут θ від (−Re); Q = 1/(2cosθ).
    Показано три позиції одного полюса по дузі радіуса ω₀: мала Q (близько до −Re), Q=0.707 (45°),
    велика Q (близько до уявної осі)."""
    W, H = 720, 430
    p = []
    cx, cy = 360, 230          # початок координат
    R = 150.0                  # ω₀ у пікселях
    axhalf_x = 300
    axhalf_y = 170

    # осі
    p.append(line(cx - axhalf_x, cy, cx + 120, cy, color=MUTED, sw=1.4))      # Re
    p.append(line(cx, cy + axhalf_y, cx, cy - axhalf_y, color=MUTED, sw=1.4)) # Im (jω)
    p.append(arrow(cx + 90, cy, cx + 118, cy, color=MUTED, sw=1.4))
    p.append(arrow(cx, cy - 142, cx, cy - 168, color=MUTED, sw=1.4))
    p.append(text(cx + 112, cy - 10, "Re (σ)", size=13, color=MUTED, anchor="end"))
    p.append(text(cx + 14, cy - 156, "j ω", size=14, color=MUTED, anchor="start", italic=True))

    # дуга сталого ω₀ (радіус R) у лівій півплощині
    arc = []
    a0, a1 = 100.0, 175.0      # градуси від додатної осі Re (ліва-верхня чверть)
    n = 40
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        arc.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    pts = " ".join("%.1f,%.1f" % q for q in arc)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3" '
             'stroke-dasharray="4 4"/>' % (pts, FIELD))

    # три полюси на дузі: θ — кут від НЕГАТИВНОЇ осі Re
    def pole_at(theta_deg, col, qlbl):
        out = []
        a = math.radians(180.0 - theta_deg)        # від додатної Re
        px = cx + R * math.cos(a)
        py = cy - R * math.sin(a)
        out.append(line(cx, cy, px, py, color=col, sw=1.6))
        # позначка полюса — хрестик
        s = 7
        out.append(line(px - s, py - s, px + s, py + s, color=col, sw=2.4))
        out.append(line(px - s, py + s, px + s, py - s, color=col, sw=2.4))
        return out, px, py

    o, px1, py1 = pole_at(20.0, NEG, "low")     # мала Q
    p += o
    o, px2, py2 = pole_at(45.0, INK, "mid")     # Q = 0.707
    p += o
    o, px3, py3 = pole_at(72.0, POS, "high")    # велика Q
    p += o

    # підписи полюсів
    bx, _, _ = textbox(px1 - 64, py1 + 16, "мала Q\nполюс далеко від j ω", size=12,
                       stroke=NEG, color=NEG)
    p.append(bx)
    bx, _, _ = textbox(px2 + 86, py2 - 6, "Q = 0.707\nкут 45°", size=12, stroke=INK)
    p.append(bx)
    bx, _, _ = textbox(px3 + 96, py3 + 6, "велика Q\nполюс коло j ω", size=12,
                       stroke=POS, color=POS)
    p.append(bx)

    # позначка радіуса ω₀ і кута θ
    p.append(text((cx + px2) / 2 - 6, (cy + py2) / 2 - 8, "ω₀", size=15, color=FIELD, italic=True))
    # дуга кута θ біля початку
    aa = []
    for i in range(16):
        a = math.radians(180.0 - 45.0 * i / 15)
        aa.append((cx + 34 * math.cos(a), cy - 34 * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2"/>'
             % (" ".join("%.1f,%.1f" % q for q in aa), INK))
    p.append(text(cx - 50, cy - 16, "θ", size=14, italic=True))

    # формула внизу
    bx, _, _ = textbox(360, 400, "Q = 1 / (2·cos θ)   ·   ω₀ = відстань полюса від нуля",
                       size=14, bold=True, min_w=460)
    p.append(bx)

    render(os.path.join(OUT, 'pole-pair.svg'), W, H, *p)


def q_peaking():
    """АЧХ |H| (дБ) однієї ланки ФНЧ 2-го порядку для кількох Q. Поріг піка — Q = 1/√2."""
    W, H = 720, 400
    p = []
    L, R = 80, 660
    T, B = 60, 320
    span = R - L

    # сітка частот ω/ω₀ у лог-масштабі від 0.1 до 10
    def fx(r):                              # r = ω/ω₀, лог
        return L + span * (math.log10(r) + 1.0) / 2.0

    def fy(db):                             # від +14 (верх) до −26 (низ)
        return T + (B - T) * (14.0 - db) / 40.0

    # осі
    p.append(line(L, T, L, B, color=MUTED, sw=1.3))
    p.append(line(L, B, R, B, color=MUTED, sw=1.3))
    for r in (0.1, 1.0, 10.0):
        x = fx(r)
        p.append(line(x, T, x, B, color="#e5e7eb", sw=1.0))
        lab = "ω₀" if abs(r - 1.0) < 1e-6 else ("0.1·ω₀" if r < 1 else "10·ω₀")
        p.append(text(x, B + 18, lab, size=12, color=MUTED))
    for db in (12, 6, 0, -6, -12, -18, -24):
        y = fy(db)
        p.append(line(L, y, R, y, color="#eef0f2", sw=1.0))
        p.append(text(L - 8, y + 4, ("%+d" % db) if db else "0", size=11,
                      color=MUTED, anchor="end"))
    p.append(text(L - 8, T - 8, "дБ", size=12, color=MUTED, anchor="end"))
    p.append(text(R, B + 18, "частота (лог)", size=12, color=MUTED, anchor="end"))

    # криві |H| ланки 2-го порядку: |H|² = 1 / [ (1−r²)² + (r/Q)² ]
    def curve(Q, col, sw=2.2, dash=None):
        pts = []
        r = 0.1
        while r <= 10.0001:
            mag2 = 1.0 / ((1 - r * r) ** 2 + (r / Q) ** 2)
            db = 10.0 * math.log10(mag2)
            db = max(-26.0, min(14.0, db))
            pts.append((fx(r), fy(db)))
            r *= 1.035
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join("%.1f,%.1f" % q for q in pts), col, sw, d))

    p.append(curve(0.5, NEG))               # без піка, повільний поворот
    p.append(curve(0.707, INK, sw=2.6))     # межа — максимально пласка
    p.append(curve(2.0, FIELD))             # помітний пік
    p.append(curve(8.0, POS))               # гострий пік

    # підписи кривих
    p.append(text(fx(0.16), fy(-3.5), "Q = 0.5", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(fx(0.42), fy(1.6), "Q = 0.707", size=12, anchor="start", bold=True))
    p.append(text(fx(1.0), fy(7.2), "Q = 2", size=12, color=FIELD, anchor="middle", bold=True))
    p.append(text(fx(1.0), fy(13.0), "Q = 8", size=12, color=POS, anchor="middle", bold=True))

    bx, _, _ = textbox(360, 372, "Q ≤ 0.707 — без піка (максимально пласко) · "
                       "Q > 0.707 — горб тим вищий, чим більша Q",
                       size=13, min_w=560)
    p.append(bx)

    render(os.path.join(OUT, 'q-peaking.svg'), W, H, *p)


def q_step():
    """Реакція на сходинку ланки 2-го порядку для тих самих Q: викид і дзвін ростуть із Q."""
    W, H = 720, 400
    p = []
    L, R = 80, 660
    T, B = 55, 300
    span = R - L
    tmax = 18.0                              # у одиницях 1/ω₀

    def fx(t):
        return L + span * t / tmax

    def fy(v):                               # від 1.7 (верх) до −0.1 (низ)
        return T + (B - T) * (1.7 - v) / 1.8

    # осі
    p.append(line(L, T, L, B, color=MUTED, sw=1.3))
    p.append(line(L, fy(0.0), R, fy(0.0), color=MUTED, sw=1.3))
    p.append(line(L, fy(1.0), R, fy(1.0), color="#cfd4da", sw=1.2, dash="5 4"))
    p.append(text(L - 8, fy(1.0) + 4, "1.0", size=11, color=MUTED, anchor="end"))
    p.append(text(L - 8, fy(0.0) + 4, "0", size=11, color=MUTED, anchor="end"))
    p.append(text(R, fy(0.0) + 18, "час →", size=12, color=MUTED, anchor="end"))
    p.append(text(L + 4, T - 6, "вихід", size=12, color=MUTED, anchor="start"))

    def step_resp(Q, col, sw=2.2):
        # нормований відгук ланки 2-го порядку, ω₀ = 1
        pts = []
        wn = 1.0
        zeta = 1.0 / (2.0 * Q)
        t = 0.0
        dt = 0.03
        while t <= tmax + 1e-9:
            if zeta < 1.0:
                wd = wn * math.sqrt(1 - zeta * zeta)
                phi = math.atan2(math.sqrt(1 - zeta * zeta), zeta)
                v = 1.0 - math.exp(-zeta * wn * t) / math.sqrt(1 - zeta * zeta) * math.sin(wd * t + phi)
            elif abs(zeta - 1.0) < 1e-6:
                v = 1.0 - (1.0 + wn * t) * math.exp(-wn * t)
            else:
                s1 = -wn * (zeta - math.sqrt(zeta * zeta - 1))
                s2 = -wn * (zeta + math.sqrt(zeta * zeta - 1))
                v = 1.0 - (s1 * math.exp(s2 * t) - s2 * math.exp(s1 * t)) / (s1 - s2)
            v = max(-0.1, min(1.72, v))
            pts.append((fx(t), fy(v)))
            t += dt
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join("%.1f,%.1f" % q for q in pts), col, sw))

    p.append(step_resp(0.5, NEG))
    p.append(step_resp(0.707, INK, sw=2.6))
    p.append(step_resp(2.0, FIELD))
    p.append(step_resp(8.0, POS))

    # підписи
    p.append(text(fx(11.5), fy(0.92), "Q = 0.5", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(fx(11.5), fy(1.06), "Q = 0.707", size=12, anchor="start", bold=True))
    p.append(text(fx(2.0), fy(1.42), "Q = 2", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(fx(0.7), fy(1.62), "Q = 8", size=12, color=POS, anchor="start", bold=True))

    bx, _, _ = textbox(360, 374, "Більша Q — вищий викид і довший дзвін; "
                       "Q = 0.5 виходить плавно, без викиду",
                       size=12, min_w=520)
    p.append(bx)

    render(os.path.join(OUT, 'q-step.svg'), W, H, *p)


def biquad_cascade():
    """Фільтр 4-го порядку = дві біквад-ланки, кожна зі своїм (ω₀, Q). Родина = рецепт значень Q."""
    W, H = 720, 420
    p = []

    # ланцюг блоків
    y = 90
    p.append(text(360, 34, "Фільтр 4-го порядку = ДВІ ланки 2-го порядку (біквади)",
                  size=15, bold=True))
    bx, w1, _ = textbox(170, y, "Ланка 1\nω₀, Q₁", size=14, bold=True, min_w=150,
                        stroke=NEG, color=NEG)
    p.append(bx)
    bx, w2, _ = textbox(440, y, "Ланка 2\nω₀, Q₂", size=14, bold=True, min_w=150,
                        stroke=POS, color=POS)
    p.append(bx)
    p.append(arrow(60, y, 92, y, color=INK))
    p.append(text(56, y - 8, "вхід", size=12, color=MUTED, anchor="end"))
    p.append(arrow(170 + w1 / 2, y, 440 - w2 / 2, y, color=INK))
    p.append(arrow(440 + w2 / 2, y, 660, y, color=INK))
    p.append(text(664, y - 8, "вихід", size=12, color=MUTED, anchor="start"))

    # таблиця рецептів родин (узагальнено, типові значення)
    tx, ty = 60, 165
    rows = [
        ("Родина (4-й порядок)", "Q₁", "Q₂", "характер"),
        ("Бесселя", "0.52", "0.81", "пласка затримка, без викиду"),
        ("Баттерворта", "0.54", "1.31", "максимально пласка АЧХ"),
        ("Чебишова (1 дБ)", "0.93", "3.56", "крутий зріз, помітний пік"),
    ]
    colx = [tx + 8, tx + 250, tx + 320, tx + 400]
    rh = 42
    p.append(rect(tx, ty, 600, rh * len(rows), fill=BG, stroke=MUTED, sw=1.3))
    for i, row in enumerate(rows):
        ry = ty + i * rh
        if i == 0:
            p.append(rect(tx, ty, 600, rh, fill=FILL, stroke=MUTED, sw=1.3))
        else:
            p.append(line(tx, ry, tx + 600, ry, color="#e5e7eb", sw=1.0))
        bold = (i == 0)
        for j, cell in enumerate(row):
            col = INK
            if i > 0 and j == 1:
                col = NEG
            if i > 0 and j == 2:
                col = POS
            anchor = "start" if j == 0 or j == 3 else "middle"
            cx = colx[j] if (j == 0 or j == 3) else colx[j]
            p.append(text(cx, ry + rh / 2 + 5, cell, size=13, color=col,
                          anchor=anchor, bold=bold))

    bx, _, _ = textbox(360, ty + rh * len(rows) + 28,
                       "Та сама ω₀, ті самі дві ланки — лише ЗНАЧЕННЯ Q різні. "
                       "Рецепт Q й задає родину фільтра.",
                       size=13, min_w=560)
    p.append(bx)

    render(os.path.join(OUT, 'biquad-cascade.svg'), W, H, *p)


def pole_geometry():
    """Прямокутний трикутник одного полюса: гіпотенуза ω₀, катет σ=ω₀/(2Q), кут θ,
    cos θ = σ/ω₀ = 1/(2Q). Для вставки math-pole-location."""
    W, H = 720, 440
    p = []
    cx, cy = 250, 300                  # початок координат (нуль s-площини)
    R = 290.0                          # довжина променя = ω₀ у пікселях
    theta = math.radians(58.0)         # кут від негативної дійсної осі (унаочнено)
    # полюс у лівій верхній чверті: напрям (−cos θ, +sin θ)
    px = cx - R * math.cos(theta)
    py = cy - R * math.sin(theta)
    foot_x = px                        # проєкція полюса на дійсну вісь (катет σ — горизонталь)
    foot_y = cy

    # осі
    p.append(line(cx - 230, cy, cx + 150, cy, color=MUTED, sw=1.4))     # Re
    p.append(line(cx, cy + 70, cx, cy - 300, color=MUTED, sw=1.4))      # jω
    p.append(arrow(cx + 120, cy, cx + 148, cy, color=MUTED, sw=1.4))
    p.append(arrow(cx, cy - 274, cx, cy - 300, color=MUTED, sw=1.4))
    p.append(text(cx + 142, cy + 18, "Re (σ)", size=13, color=MUTED, anchor="end"))
    p.append(text(cx + 14, cy - 286, "j ω", size=14, color=MUTED, anchor="start", italic=True))

    # трикутник: гіпотенуза (промінь), катет σ (горизонталь), катет ω_d (вертикаль до полюса)
    p.append(line(cx, cy, px, py, color=POS, sw=2.4))                   # ω₀ — гіпотенуза
    p.append(line(cx, cy, foot_x, foot_y, color=NEG, sw=2.2))           # σ — прилеглий катет
    p.append(line(foot_x, foot_y, px, py, color=FIELD, sw=2.2))         # ω_d — протилежний катет

    # позначка прямого кута біля основи (foot)
    s = 12
    sgn = -1 if foot_x < cx else 1
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
             'stroke="%s" stroke-width="1.2"/>'
             % (foot_x + sgn * s, foot_y, foot_x + sgn * s, foot_y - s,
                foot_x, foot_y - s, MUTED))

    # полюс — хрестик
    c = 8
    p.append(line(px - c, py - c, px + c, py + c, color=INK, sw=2.6))
    p.append(line(px - c, py + c, px + c, py - c, color=INK, sw=2.6))
    bx, _, _ = textbox(px, py - 26, "полюс  s = −σ + j·ω_d", size=12, bold=True, stroke=INK)
    p.append(bx)

    # дуга кута θ біля нуля (від негативної осі Re до променя)
    aa = []
    n = 18
    for i in range(n + 1):
        a = math.radians(180.0 - 58.0 * i / n)     # від додатної Re на 180°, крутимо до променя
        aa.append((cx + 42 * math.cos(a), cy - 42 * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3"/>'
             % (" ".join("%.1f,%.1f" % q for q in aa), INK))
    p.append(text(cx - 64, cy - 24, "θ", size=15, italic=True, bold=True))

    # підписи сторін
    p.append(text((cx + px) / 2 - 40, (cy + py) / 2 - 6, "ω₀", size=16, color=POS,
                  italic=True, bold=True))
    p.append(text((cx + foot_x) / 2, cy + 24, "σ = ω₀/(2Q)", size=13, color=NEG, bold=True))
    p.append(text(foot_x - 12, (cy + py) / 2 + 4, "ω_d", size=14, color=FIELD,
                  italic=True, bold=True, anchor="end"))

    # підсумкова формула
    bx, _, _ = textbox(500, 110, "cos θ = σ / ω₀ = 1/(2Q)\n⇒  Q = 1 / (2·cos θ)",
                       size=15, bold=True, min_w=300)
    p.append(bx)
    bx, _, _ = textbox(500, 190, "ω_d = ω₀·√(1 − 1/(4Q²))\n|s| = √(σ² + ω_d²) = ω₀",
                       size=13, min_w=300, stroke=MUTED)
    p.append(bx)

    render(os.path.join(OUT, 'pole-geometry.svg'), W, H, *p)


def three_regimes():
    """Рух коренів знаменника зі зростанням Q: дійсні (Q<0.5) → кратний (Q=0.5) → пара (Q>0.5)."""
    W, H = 720, 440
    p = []
    cx, cy = 380, 240
    R = 165.0                          # радіус дуги сталого ω₀

    # осі
    p.append(line(cx - 320, cy, cx + 130, cy, color=MUTED, sw=1.4))
    p.append(line(cx, cy + 170, cx, cy - 175, color=MUTED, sw=1.4))
    p.append(arrow(cx + 100, cy, cx + 128, cy, color=MUTED, sw=1.4))
    p.append(arrow(cx, cy - 148, cx, cy - 175, color=MUTED, sw=1.4))
    p.append(text(cx + 122, cy - 10, "Re (σ)", size=13, color=MUTED, anchor="end"))
    p.append(text(cx + 14, cy - 162, "j ω", size=14, color=MUTED, anchor="start", italic=True))

    # дуга сталого ω₀ (де живе комплексна пара)
    arc = []
    for i in range(61):
        a = math.radians(95.0 + 80.0 * i / 60)     # ліва півплощина, верх+низ навколо −Re
        arc.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3" '
             'stroke-dasharray="4 4"/>'
             % (" ".join("%.1f,%.1f" % q for q in arc), FIELD))
    # точка −ω₀ на осі (кратний корінь)
    mx, my = cx - R, cy

    def crossmark(x, y, col, sz=7, sw=2.4):
        return (line(x - sz, y - sz, x + sz, y + sz, color=col, sw=sw) +
                line(x - sz, y + sz, x + sz, y - sz, color=col, sw=sw))

    # 1) Q<0.5 — два дійсні полюси на осі (один близько до нуля, другий далеко)
    d1x, d2x = cx - 70, cx - 270
    p.append(crossmark(d1x, cy, NEG))
    p.append(crossmark(d2x, cy, NEG))
    # стрілки сходження до −ω₀
    p.append(arrow(d1x - 8, cy - 22, mx + 10, cy - 6, color=NEG, sw=1.3))
    p.append(arrow(d2x + 8, cy - 22, mx - 10, cy - 6, color=NEG, sw=1.3))
    bx, _, _ = textbox(d2x + 8, cy + 40, "Q < 0.5: два дійсні полюси\nрозповзлись по осі",
                       size=12, stroke=NEG, color=NEG)
    p.append(bx)

    # 2) Q=0.5 — кратний корінь у −ω₀
    p.append(crossmark(mx, cy, INK, sz=8, sw=3.0))
    p.append(circle(mx, cy, 13, fill="none", stroke=INK, sw=1.4))
    bx, _, _ = textbox(mx, cy - 50, "Q = 0.5: кратний\nкорінь  s = −ω₀", size=12, stroke=INK)
    p.append(bx)

    # 3) Q>0.5 — комплексна пара на дузі (вгору і вниз)
    th = math.radians(62.0)
    ax = cx - R * math.cos(th)
    ay_up = cy - R * math.sin(th)
    ay_dn = cy + R * math.sin(th)
    p.append(line(cx, cy, ax, ay_up, color=POS, sw=1.4, dash="3 3"))
    p.append(crossmark(ax, ay_up, POS))
    p.append(crossmark(ax, ay_dn, POS))
    bx, _, _ = textbox(ax + 92, ay_up - 6, "Q > 0.5: комплексна\nпара на дузі ω₀",
                       size=12, stroke=POS, color=POS)
    p.append(bx)
    # стрілка руху пари до уявної осі зі зростанням Q
    p.append(arrow(ax - 6, ay_up - 4, cx - 18, cy - R + 14, color=POS, sw=1.3))
    p.append(text((cx + ax) / 2 - 26, (cy + ay_up) / 2 - 6, "ω₀", size=14, color=FIELD,
                  italic=True, bold=True))

    bx, _, _ = textbox(360, 412,
                       "Зі зростанням Q корені сходяться в −ω₀, тоді сходять з осі "
                       "в пару й ковзають по дузі до j ω.",
                       size=13, min_w=560)
    p.append(bx)

    render(os.path.join(OUT, 'three-regimes.svg'), W, H, *p)


def biquad_pipeline():
    """Конвеєр перекладу пари полюсів (f0, Q, fs) у 5 коефіцієнтів цифрового біквада.
    Для вставки proj-biquad-coeffs: показує, де саме входить Q (у α) і де ділення на a0."""
    W, H = 720, 430
    p = []
    p.append(text(360, 30, "Пара полюсів (f0, Q, fs)  →  5 коефіцієнтів біквада",
                  size=16, bold=True))

    # вхідні дані — три комірки
    bx, _, _ = textbox(150, 80, "f0\n(частота)", size=13, min_w=110, stroke=FIELD, color=FIELD)
    p.append(bx)
    bx, _, _ = textbox(360, 80, "Q\n(добротність)", size=13, min_w=130, stroke=POS, color=POS)
    p.append(bx)
    bx, _, _ = textbox(570, 80, "fs\n(дискретизація)", size=13, min_w=140, stroke=NEG, color=NEG)
    p.append(bx)

    # крок 1: ω₀ з f0 і fs
    p.append(arrow(150, 102, 250, 150, color=MUTED))
    p.append(arrow(570, 102, 470, 150, color=MUTED))
    bx, _, _ = textbox(360, 165, "ω₀ = 2·π·f0 / fs", size=14, bold=True, min_w=260)
    p.append(bx)

    # крок 2: cos/sin ліворуч, alpha праворуч (Q входить сюди)
    p.append(arrow(330, 186, 250, 224, color=MUTED))
    bx, _, _ = textbox(210, 250, "cw = cos ω₀\nsw = sin ω₀", size=13, min_w=180)
    p.append(bx)
    # пунктирна стрілка від Q прямо в α
    p.append('<path d="M 360 102 C 480 150, 530 205, 510 232" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" '
             'marker-end="url(#arrow)"/>' % POS)
    bx, _, _ = textbox(515, 250, "α = sw / (2·Q)\n↑ уся Q тут", size=13, min_w=200,
                       stroke=POS, color=POS)
    p.append(bx)

    # крок 3: п'ять сирих коефіцієнтів
    p.append(arrow(210, 274, 290, 312, color=MUTED))
    p.append(arrow(515, 274, 440, 312, color=MUTED))
    bx, _, _ = textbox(360, 334,
                       "b0=(1−cw)/2   b1=1−cw   b2=(1−cw)/2\n"
                       "a0=1+α    a1=−2cw    a2=1−α",
                       size=13, min_w=470)
    p.append(bx)

    # крок 4: нормування на a0
    p.append(arrow(360, 362, 360, 388, color=MUTED))
    bx, _, _ = textbox(360, 404, "÷ a0  →  b0 b1 b2 a1 a2  (готово)",
                       size=14, bold=True, min_w=380, stroke=FIELD)
    p.append(bx)

    render(os.path.join(OUT, 'biquad-pipeline.svg'), W, H, *p)


def stage_ordering():
    """Порядок ланок каскаду за зростанням Q проти переповнення.
    Згори — низька Q першою (рівень тримається); знизу — висока Q першою (насичення)."""
    W, H = 720, 450
    p = []
    p.append(text(360, 28, "Порядок ланок у каскаді — за зростанням Q",
                  size=16, bold=True))

    # горизонтальна «стеля діапазону» для кожного ряду — рахуємо від основи стовпчиків
    def row(y, q1, q2, col1, col2, h1, h2, verdict, vcol, vok):
        out = []
        base = y + 40
        ceil = base - 48                # рівень стелі діапазону
        out.append(arrow(38, y, 76, y, color=INK))
        out.append(text(36, y - 9, "вхід", size=11, color=MUTED, anchor="end"))
        bx, w1, _ = textbox(150, y, "ланка 1\nQ = %s" % q1, size=12, bold=True,
                            min_w=120, stroke=col1, color=col1)
        out.append(bx)
        out.append(arrow(150 + w1 / 2, y, 300, y, color=INK))
        bx, w2, _ = textbox(370, y, "ланка 2\nQ = %s" % q2, size=12, bold=True,
                            min_w=120, stroke=col2, color=col2)
        out.append(bx)
        out.append(arrow(370 + w2 / 2, y, 520, y, color=INK))
        bx, _, _ = textbox(625, y, verdict, size=12, bold=True, min_w=160,
                           stroke=vcol, color=vcol,
                           fill="#eafaf0" if vok else "#fdecea")
        out.append(bx)
        # стовпчики «рівень сигналу» під кожною ланкою
        out.append(line(40, ceil, 470, ceil, color=POS if not vok else MUTED,
                        sw=1.3, dash="6 4"))
        out.append(text(44, ceil - 5, "стеля діапазону", size=10,
                        color=POS if not vok else MUTED, anchor="start"))
        for cx, h, c in ((150, h1, col1), (370, h2, col2)):
            hh = min(h, base - ceil + 6) if not vok else h    # показати биття в стелю
            out.append(line(cx, base, cx, base - hh, color=c, sw=7))
        return out

    p += row(92, "0.5", "8", NEG, POS, 16, 30,
             "рівень у межах\nзапас цілий", FIELD, True)
    p += row(252, "8", "0.5", POS, NEG, 50, 28,
             "пік б'є в стелю\nнасичення!", POS, False)

    bx, _, _ = textbox(360, 415,
                       "Низька Q першою: ранні ланки гасять зайве,\n"
                       "на високу Q приходить слабкий сигнал — пік нема чому роздути.",
                       size=12, min_w=560)
    p.append(bx)

    render(os.path.join(OUT, 'stage-ordering.svg'), W, H, *p)


if __name__ == '__main__':
    pole_pair()
    q_peaking()
    q_step()
    biquad_cascade()
    pole_geometry()
    three_regimes()
    biquad_pipeline()
    stage_ordering()
    print("OK: 8 фігур у", OUT)
