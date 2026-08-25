# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def rrect(cx, cy, w, h, angle, fill=FILL, stroke=LINE, sw=1.8, rx=8):
    """Прямокутник із центром (cx,cy), повернутий на angle градусів."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" '
            'transform="rotate(%.1f %.1f %.1f)"/>'
            % (cx - w / 2, cy - h / 2, w, h, rx, fill, stroke, sw, angle, cx, cy))


# ── Фігура 1: акселерометр у трьох станах — сила, а не прискорення ────────────
def fig_specific_force():
    W, H = 820, 470
    body = []
    # (cx, title, frac[0..1] показ f, reading, a_txt, f_txt, note)
    panels = [
        (160, "спокій на столі", 0.5, "1g", "a = 0", "f = +9.81", "опора тримає масу"),
        (410, "вільне падіння", 0.0, "0", "a = −9.81", "f = 0", "маса «спливає»"),
        (660, "розгін угору (тяга)", 0.92, ">1g", "a > 0", "f > +9.81", "тисне ще дужче"),
    ]
    cy_top, ch = 108, 140
    cy_bot = cy_top + ch          # 248 — низ корпусу
    plat_y = cy_bot - 16
    m = 42                        # сторона пробної маси
    for (cx, title, frac, rd, a_txt, f_txt, note) in panels:
        body.append(text(cx, 74, title, size=13.5, bold=True))
        cw = 88
        body.append(rect(cx - cw / 2, cy_top, cw, ch, fill=BG, stroke=LINE, sw=2))
        # платформа-опора (шкала) біля дна
        body.append(line(cx - cw / 2 + 8, plat_y, cx + cw / 2 - 8, plat_y, color=MUTED, sw=3))
        # пробна маса: більше сили → сильніше стиснута пружина → маса нижче
        mass_bottom = plat_y - 44 + 36 * frac
        mass_top = mass_bottom - m
        # пружина (коротшає зі зростанням сили)
        pts = []
        coils = 4
        for i in range(coils * 2 + 1):
            xx = cx - 14 if i % 2 == 0 else cx + 14
            yy = mass_bottom + (plat_y - mass_bottom) * i / (coils * 2)
            pts.append("%.1f,%.1f" % (xx, yy))
        body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
                    % (" ".join(pts), NEG))
        body.append(rect(cx - m / 2, mass_top, m, m, fill=FILL, stroke=INK, sw=1.8))
        body.append(text(cx, (mass_top + mass_bottom) / 2 + 5, "m", size=15, italic=True))
        # стрілка показу питомої сили — праворуч від корпусу
        ax = cx + cw / 2 + 30
        if frac > 0.05:
            alen = 26 + frac * 70
            body.append(arrow(ax, cy_bot, ax, cy_bot - alen, color=POS, sw=3.2))
            body.append(text(ax + 9, cy_bot - alen + 4, "f = " + rd, size=12.5,
                             color=POS, bold=True, anchor="start"))
        else:
            body.append(circle(ax, cy_bot - 12, 4.5, fill=NEG, stroke=NEG))
            body.append(text(ax + 9, cy_bot - 8, "f = 0", size=12.5, color=NEG,
                             bold=True, anchor="start"))
        # числа під корпусом
        body.append(fitbox(cx - 92, cy_bot + 26, 184, 46, a_txt + "\n" + f_txt,
                           size=13, bold=True, fill="#f4f6f8", stroke=MUTED))
        body.append(text(cx, cy_bot + 92, note, size=11, color=MUTED))
    body.append(text(W / 2, H - 12,
                     "той самий давач: у спокої +1g, у падінні 0, під тягою — понад 1g",
                     size=12.5, color=MUTED))
    render(os.path.join(OUT, "specific-force.svg"), W, H, *body,
           title="Що показує акселерометр: питому силу, а не прискорення")


# ── Фігура 2: карданова платформа проти strapdown ────────────────────────────
def fig_gimbal_vs_strapdown():
    W, H = 800, 440
    body = []
    tilt = 20
    # ── ліворуч: карданова платформа ──
    lx, ly = 210, 200
    body.append(text(lx, 66, "Карданова платформа", size=15, bold=True, color=NEG))
    body.append(rrect(lx, ly, 210, 140, tilt, fill="#eef2fb", stroke=NEG, sw=2))
    body.append(text(lx + 78, ly + 78, "апарат нахилений", size=11, color=MUTED, anchor="middle"))
    # карданові кільця
    body.append('<ellipse cx="%.1f" cy="%.1f" rx="76" ry="50" fill="none" stroke="%s" stroke-width="1.8"/>'
                % (lx, ly, LINE))
    body.append('<ellipse cx="%.1f" cy="%.1f" rx="50" ry="72" fill="none" stroke="%s" stroke-width="1.8"/>'
                % (lx, ly, LINE))
    # внутрішній сенсорний блок — лишається РІВНИМ (не повернутий)
    body.append(rect(lx - 22, ly - 22, 44, 44, fill=FIELD, stroke=INK, sw=1.8))
    body.append(text(lx, ly + 5, "IMU", size=12, bold=True, color=BG))
    # мітка рівня
    body.append(line(lx - 34, ly + 40, lx + 34, ly + 40, color=FIELD, sw=2.5))
    body.append(text(lx, 330, "сенсори лишаються рівними —", size=12, color=INK))
    body.append(text(lx, 348, "кардани тримають напрям залізом", size=12, color=INK))
    body.append(text(lx, 372, "точно, але важко й багато рухомих частин", size=11, color=MUTED))

    # ── праворуч: strapdown ──
    rx, ry = 590, 170
    body.append(text(rx, 66, "Strapdown", size=15, bold=True, color=POS))
    body.append(rrect(rx, ry, 210, 140, tilt, fill="#fdeeec", stroke=POS, sw=2))
    # сенсорний блок ПРИКРУЧЕНИЙ — нахилений разом з апаратом
    body.append(rrect(rx, ry, 44, 44, tilt, fill=POS, stroke=INK, sw=1.8))
    body.append(text(rx, ry + 5, "IMU", size=12, bold=True, color=BG))
    body.append(text(rx, ry - 54, "блок нахилений разом з апаратом", size=11, color=MUTED))
    # стрілка в комп'ютер
    body.append(arrow(rx, ry + 78, rx, 300, color=LINE, sw=2))
    # комп'ютер тримає «математичну платформу»
    body.append(fitbox(rx - 130, 302, 260, 58,
                       "комп'ютер тримає орієнтацію C\n(кватерніон / DCM) — числами",
                       size=12, bold=True, fill="#f4f6f8", stroke=POS))
    # рівний кубик-платформа поряд
    body.append(rect(rx + 96, 314, 34, 34, fill=FIELD, stroke=INK, sw=1.6))
    body.append(text(rx + 113, 336, "C", size=13, bold=True, color=BG))
    body.append(text(rx, 388, "залізо просте — робота переїхала в обчислення", size=11, color=MUTED))
    render(os.path.join(OUT, "gimbal-vs-strapdown.svg"), W, H, *body,
           title="Дві архітектури інерціального блоку")


# ── Фігура 3: ланцюг strapdown-механізації ───────────────────────────────────
def fig_mechanization():
    W, H = 840, 430
    body = []

    def box(cx, cy, w, h, s, col=LINE, fill=FILL, size=12):
        body.append(fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, bold=True,
                            fill=fill, stroke=col))

    y1, y2 = 110, 250
    # верхній рядок: гіроскоп → орієнтація
    box(120, y1, 130, 56, "гіроскоп\nω (осі тіла)", col=NEG, fill="#eef2fb")
    box(340, y1, 170, 56, "інтегратор орієнтації\n→ поворот C", col=NEG, fill="#eef2fb")
    body.append(arrow(185, y1, 254, y1, color=LINE, sw=2))
    # C вниз у поворот
    body.append(arrow(340, y1 + 28, 340, y2 - 28, color=FIELD, sw=2.2))
    body.append(text(352, (y1 + y2) / 2, "C", size=14, bold=True, color=FIELD, anchor="start"))

    # нижній рядок: акселерометр → повернути → +g → ∫ → ∫
    box(120, y2, 130, 56, "акселерометр\nf (осі тіла)", col=POS, fill="#fdeeec")
    box(340, y2, 150, 56, "повернути\nf_світ = C·f", col=INK)
    box(500, y2, 84, 56, "+ g", col=FIELD, fill="#eaf6ee")
    box(645, y2, 110, 56, "∫ dt\n→ швидкість v", col=INK)
    box(645, 350, 110, 56, "∫ dt\n→ положення p", col=INK)

    body.append(arrow(185, y2, 264, y2, color=LINE, sw=2))
    body.append(text(224, y2 - 8, "f", size=12, italic=True, color=POS))
    body.append(arrow(415, y2, 458, y2, color=LINE, sw=2))
    body.append(text(437, y2 - 8, "f_світ", size=11, color=MUTED))
    body.append(arrow(542, y2, 590, y2, color=LINE, sw=2))
    body.append(text(566, y2 - 8, "a_світ", size=11, color=MUTED))
    body.append(arrow(645, y2 + 28, 645, 350 - 28, color=LINE, sw=2))
    body.append(text(657, (y2 + 350) / 2, "v", size=12, italic=True, color=INK, anchor="start"))

    # модель гравітації живить «+ g» знизу
    body.append(fitbox(430, 340, 140, 40, "модель\nгравітації g", size=11,
                       fill="#eaf6ee", stroke=FIELD))
    body.append(arrow(500, 340, 500, y2 + 28, color=FIELD, sw=2))

    body.append(text(W / 2, H - 14,
                     "орієнтація повертає відчуту силу у світ, гравітація повертає невідчуте, два інтеграли дають шлях",
                     size=12, color=MUTED))
    render(os.path.join(OUT, "mechanization.svg"), W, H, *body,
           title="Ланцюг strapdown-механізації")


# ── Фігура 4: чому похибка гіроскопа тече в горизонт ──────────────────────────
def fig_gravity_leak():
    W, H = 700, 450
    body = []
    O = (300, 150)
    L = 175
    dth = 20  # градуси, для наочності
    A = (O[0], O[1] + L)                                   # справжній низ
    Bx = O[0] + L * math.sin(math.radians(dth))
    B = (Bx, O[1] + L)                                     # підніжжя нахиленої «вертикалі»

    # довідкові осі
    body.append(line(O[0], O[1], O[0], O[1] + L + 34, color=MUTED, sw=1, dash="4 4"))
    # g — справжня вертикаль (синя)
    body.append(arrow(O[0], O[1], A[0], A[1], color=NEG, sw=3))
    body.append(text(O[0] - 14, (O[1] + A[1]) / 2, "g", size=16, bold=True, color=NEG, anchor="end"))
    body.append(text(O[0] - 14, (O[1] + A[1]) / 2 + 20, "справжній низ (1g)", size=11,
                     color=MUTED, anchor="end"))
    # обчислена вертикаль (сіра пунктирна, нахилена на δθ)
    body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" '
                'stroke-dasharray="7 5"/>' % (O[0], O[1], B[0], B[1], LINE))
    body.append(text(B[0] + 40, O[1] + 96, "обчислена", size=11.5, color=INK, anchor="start"))
    body.append(text(B[0] + 40, O[1] + 112, "вертикаль", size=11.5, color=INK, anchor="start"))
    body.append(text(B[0] + 40, O[1] + 128, "(нахил δθ)", size=11.5, color=MUTED, anchor="start"))
    # горизонтальний катет — протікання g·sinδθ (червоний)
    body.append(arrow(A[0], A[1], B[0], B[1], color=POS, sw=3.4))
    body.append(text((A[0] + B[0]) / 2 - 6, A[1] + 26, "g·sinδθ", size=14, bold=True, color=POS))
    body.append(text((A[0] + B[0]) / 2 - 6, A[1] + 44, "хибне бічне прискорення", size=11,
                     color=POS))
    # дужка кута δθ
    body.append('<path d="M%.1f %.1f A 40 40 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                % (O[0], O[1] + 40, O[0] + 40 * math.sin(math.radians(dth)),
                   O[1] + 40 * math.cos(math.radians(dth)), INK))
    body.append(text(O[0] + 20, O[1] + 34, "δθ", size=13, bold=True, color=INK, anchor="start"))
    # числовий підсумок
    body.append(fitbox(W / 2 - 210, 372, 420, 48,
                       "δθ = 1 мрад  →  g·sinδθ ≈ 9.81 · 0.001 = 0.0098 м/с²  (= 1 мілі-g)",
                       size=13, bold=True, fill="#fdeeec", stroke=POS))
    render(os.path.join(OUT, "gravity-leak.svg"), W, H, *body,
           title="Похибка гіроскопа нахиляє «низ» — і гравітація тече в горизонт")


# ── Фігура 5 (hist): дорога до strapdown — часова вісь ────────────────────────
def fig_inertial_timeline():
    W, H = 1000, 400
    body = []
    axis_y = 200
    # (рік, [дві короткі описові лінії], колір-ери)
    pts = [
        ("1907", ["Ейнштейн:", "падіння — це 0 g"], NEG),
        ("1913", ["Саньяк: світло", "чує обертання"], NEG),
        ("1953", ["SPIRE Дрейпера —", "кардани крізь США"], INK),
        ("1963", ["перший лазерний", "гіроскоп, Sperry"], POS),
        ("1976", ["волоконний", "гіроскоп, Utah"], POS),
        ("1983", ["strapdown у Boeing", "757/767, Honeywell"], FIELD),
        ("1991", ["MEMS: гіроскоп", "на цятці кремнію"], FIELD),
    ]
    n = len(pts)
    x0, x1 = 95, 905
    step = (x1 - x0) / (n - 1)
    body.append(line(x0 - 26, axis_y, x1 + 26, axis_y, color=MUTED, sw=2.6))
    cw, ch, stub = 142, 78, 24
    for i, (year, label, col) in enumerate(pts):
        x = x0 + i * step
        body.append(circle(x, axis_y, 7, fill=col, stroke=col))
        s = year + "\n" + "\n".join(label)
        if i % 2 == 0:                       # над віссю
            body.append(line(x, axis_y - 7, x, axis_y - stub, color=col, sw=2))
            body.append(fitbox(x - cw / 2, axis_y - stub - ch, cw, ch, s,
                               size=12.5, fill=BG, stroke=col, color=INK))
        else:                                # під віссю
            body.append(line(x, axis_y + 7, x, axis_y + stub, color=col, sw=2))
            body.append(fitbox(x - cw / 2, axis_y + stub, cw, ch, s,
                               size=12.5, fill=BG, stroke=col, color=INK))
    body.append(text(W / 2, H - 14,
                     "сині — фізичні корені · чорний — карданна доба · червоні — оптичні гіроскопи · зелені — доба strapdown",
                     size=11.5, color=MUTED))
    render(os.path.join(OUT, "inertial-timeline.svg"), W, H, *body,
           title="Дорога до strapdown: сім кроків за вісімдесят років")


# ── Фігура 6 (hist): RLG — колективний винахід, шар за шаром ───────────────────
def fig_rlg_invention_layers():
    W, H = 880, 400
    body = []
    rows = [
        ("Ідея", "Кліффорд Гір (Clifford Heer), 1961 — узяти кільцевий\nлазер і ефект Саньяка, щоб «почути» обертання", NEG, "#eef2fb"),
        ("Теорія", "Гір і Адольф Розенталь (Adolph Rosenthal), 1961–62 —\nяк обертання розводить частоти зустрічних променів", INK, "#f4f6f8"),
        ("Перший робочий зразок", "Вільям Мейсек (William Macek) і Девід Девіс (David Davis),\nSperry Gyroscope, 1963 — квадрат зі стороною ≈ 1 метр", POS, "#fdeeec"),
        ("Робочий прилад", "Honeywell (Фредерік Ароновіц, Джозеф Кілпатрік), 1960–80-ті —\nдовести до розміру й ціни серійного авіаприладу", FIELD, "#eaf6ee"),
    ]
    top0, rh, gap = 84, 62, 12
    body.append(arrow(44, top0 + 4, 44, top0 + len(rows) * (rh + gap) - gap - 4,
                      color=MUTED, sw=2.4))
    for i, (tag, detail, col, light) in enumerate(rows):
        y = top0 + i * (rh + gap)
        body.append(fitbox(72, y, 196, rh, tag, size=13, bold=True,
                           fill=light, stroke=col, color=col))
        body.append(fitbox(286, y, 560, rh, detail, size=12,
                           fill=BG, stroke=MUTED, color=INK))
    body.append(text(W / 2, H - 14,
                     "від ідеї (1961) до серійного приладу — близько двадцяти років; жоден рядок не «винайшов RLG» сам",
                     size=11.5, color=MUTED))
    render(os.path.join(OUT, "rlg-invention-layers.svg"), W, H, *body,
           title="Кільцевий лазерний гіроскоп — винахід у чотири шари")


# ── Фігура 7 (proj): коло з двох сталих векторів; порядок інтегрування ─────────
def fig_circle_recover():
    W, H = 880, 540
    body = []
    Gc, R, Vs = 9.81, 100.0, 20.0
    OM = Vs / R
    gyro = (0.0, 0.0, OM)
    acc = (0.0, OM * OM * R, Gc)

    def qm(a, b):
        aw, ax, ay, az = a; bw, bx, by, bz = b
        return (aw * bw - ax * bx - ay * by - az * bz,
                aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw)

    def qrot(q, v):
        w, x, y, z = q
        r = qm(qm(q, (0.0, v[0], v[1], v[2])), (w, -x, -y, -z))
        return (r[1], r[2], r[3])

    def qu(q):
        n = math.sqrt(sum(c * c for c in q))
        return tuple(c / n for c in q)

    def dq(rv):
        a = math.sqrt(rv[0] ** 2 + rv[1] ** 2 + rv[2] ** 2)
        if a < 1e-12:
            return (1.0, 0.0, 0.0, 0.0)
        s = math.sin(a / 2) / a
        return (math.cos(a / 2), rv[0] * s, rv[1] * s, rv[2] * s)

    def run(dt, laps, scheme):
        n = int(round(laps * (2 * math.pi / OM) / dt))
        q = qu((math.cos(math.pi / 4), 0.0, 0.0, math.sin(math.pi / 4)))
        v = [0.0, Vs, 0.0]; p = [R, 0.0, 0.0]; ap = None
        pts = [(p[0], p[1])]
        for _ in range(n):
            q = qu(qm(q, dq((gyro[0] * dt, gyro[1] * dt, gyro[2] * dt))))
            fw = qrot(q, acc); aw = (fw[0], fw[1], fw[2] - Gc)
            if scheme == "euler":
                for i in range(3):
                    p[i] += v[i] * dt + 0.5 * aw[i] * dt * dt
                for i in range(3):
                    v[i] += aw[i] * dt
            else:
                if ap is None:
                    ap = aw
                vn = [v[i] + 0.5 * (ap[i] + aw[i]) * dt for i in range(3)]
                for i in range(3):
                    p[i] += 0.5 * (v[i] + vn[i]) * dt
                v = vn; ap = aw
            pts.append((p[0], p[1]))
        return pts

    euler = run(1.0 / 8, 3, "euler")     # коарс-крок, щоб розповзання було ВИДНО
    trap = run(1.0 / 8, 3, "trap")
    cx, cy, sc = 300, 300, 1.55

    def polyline(seq, color, sw=2.2):
        s = " ".join("%.2f,%.2f" % (cx + px * sc, cy - py * sc) for (px, py) in seq)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (s, color, sw))

    body.append(line(cx - 205, cy, cx + 205, cy, color=MUTED, sw=1, dash="3 5"))
    body.append(line(cx, cy - 205, cx, cy + 205, color=MUTED, sw=1, dash="3 5"))
    body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="3" stroke-dasharray="2 6"/>' % (cx, cy, R * sc, MUTED))
    body.append(polyline(trap, NEG, sw=3))
    body.append(polyline(euler, POS, sw=2.4))
    body.append(circle(cx + R * sc, cy, 5, fill=INK, stroke=INK))
    body.append(text(cx + R * sc + 12, cy + 22, "старт", size=11, color=INK, anchor="start"))
    ex, ey = cx + euler[-1][0] * sc, cy - euler[-1][1] * sc
    body.append(text(ex - 6, ey - 12, "3-тє коло", size=11, color=POS, anchor="middle"))

    px = 566
    body.append(text(px, 96, "Вхід — два СТАЛИХ вектори:", size=13.5, bold=True, anchor="start"))
    body.append(fitbox(px, 110, 256, 62,
                       "gyro = (0, 0, 0.20) рад/с\nacc = (0, 4.00, 9.81) м/с²",
                       size=13, bold=True, fill="#f4f6f8", stroke=LINE))
    body.append(text(px, 200, "Вихід має бути коло r = 100 м —", size=12.5, anchor="start"))
    body.append(text(px, 218, "уся геометрія у циклі, не в даних.", size=12.5,
                     color=MUTED, anchor="start"))
    ly = 262
    body.append(line(px, ly, px + 34, ly, color=MUTED, sw=3, dash="2 6"))
    body.append(text(px + 46, ly + 4, "істина (ідеал)", size=12, anchor="start"))
    body.append(line(px, ly + 30, px + 34, ly + 30, color=NEG, sw=3))
    body.append(text(px + 46, ly + 34, "трапеція — замкнулося", size=12, color=NEG, anchor="start"))
    body.append(line(px, ly + 60, px + 34, ly + 60, color=POS, sw=2.6))
    body.append(text(px + 46, ly + 64, "прямокутник — розповзлося", size=12, color=POS, anchor="start"))
    body.append(fitbox(px, ly + 92, 286, 92,
                       "Ті самі бездоганні давачі,\nта сама float64, той самий dt.\n"
                       "Різниця — лише в порядку\nінтегрування швидкості.",
                       size=12.5, fill="#fdeeec", stroke=POS))
    body.append(text(W / 2, H - 16,
                     "крок навмисно грубий (8 Гц), щоб розповзання було видно; на 500 Гц ця похибка — 12.6 см за коло",
                     size=11.5, color=MUTED))
    render(os.path.join(OUT, "circle-recover.svg"), W, H, *body,
           title="Прямокутник розповзається, трапеція замикає коло")


# ── Фігура 8 (proj): зростання похибки — акселерометр t², гіроскоп t³ ──────────
def fig_error_growth():
    W, H = 820, 520
    body = []
    Gc = 9.81
    b_a = 1e-3 * Gc
    b_g = 3e-5
    x0, x1, y0, y1 = 168, 700, 96, 424
    lt0, lt1 = math.log10(10.0), math.log10(600.0)
    le0, le1 = math.log10(1.0), math.log10(20000.0)

    def X(t):
        return x0 + (math.log10(t) - lt0) / (lt1 - lt0) * (x1 - x0)

    def Y(e):
        return y1 - (math.log10(e) - le0) / (le1 - le0) * (y1 - y0)

    body.append(rect(x0, y0, x1 - x0, y1 - y0, fill=BG, stroke=LINE, sw=1.5))
    for t in (10, 30, 100, 300, 600):
        gx = X(t)
        body.append(line(gx, y0, gx, y1, color="#e6e8eb", sw=1))
        body.append(text(gx, y1 + 22, str(t), size=11, color=MUTED))
    for e in (1, 10, 100, 1000, 10000):
        gy = Y(e)
        body.append(line(x0, gy, x1, gy, color="#e6e8eb", sw=1))
        lab = {1: "1 м", 10: "10 м", 100: "100 м", 1000: "1 км", 10000: "10 км"}[e]
        body.append(text(x0 - 14, gy + 4, lab, size=11, color=MUTED, anchor="end"))
    body.append(text((x0 + x1) / 2, y1 + 46, "час, с (лог. шкала)", size=12.5, bold=True))

    ts = [10 * (600.0 / 10) ** (i / 60.0) for i in range(61)]
    pa = [(X(t), Y(0.5 * b_a * t * t)) for t in ts if 0.5 * b_a * t * t >= 1.0]
    pg = [(X(t), Y((1.0 / 6) * Gc * b_g * t ** 3)) for t in ts
          if (1.0 / 6) * Gc * b_g * t ** 3 >= 1.0]
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                % (" ".join("%.2f,%.2f" % pt for pt in pa), NEG))
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                % (" ".join("%.2f,%.2f" % pt for pt in pg), POS))

    tx = 3 * b_a / (Gc * b_g)
    ex = 0.5 * b_a * tx * tx
    body.append(circle(X(tx), Y(ex), 5.5, fill=INK, stroke=INK))
    body.append(text(X(tx) - 8, Y(ex) + 22, "перетин ≈ 100 с", size=11.5,
                     bold=True, anchor="start"))
    body.append(text(X(400), Y(0.5 * b_a * 400 * 400) + 22,
                     "акселерометр  ½·b·t²  (нахил 2)", size=12.5, color=NEG,
                     bold=True, anchor="middle"))
    body.append(text(X(60), Y((1.0 / 6) * Gc * b_g * 60 ** 3) - 14,
                     "гіроскоп  ⅙·g·b·t³  (нахил 3)", size=12.5, color=POS,
                     bold=True, anchor="middle"))
    body.append(fitbox(x0 + 10, y0 + 10, 224, 46,
                       "1 мілі-g зсуву → 1766 м за 10 хв\n6.2°/год зсуву → 10.6 км за 10 хв",
                       size=11, fill="#f4f6f8", stroke=MUTED))
    body.append(text(W / 2, H - 14,
                     "спершу гірший зсув акселерометра; після ≈100 с кубічна похибка гіроскопа переганяє все",
                     size=11.5, color=MUTED))
    render(os.path.join(OUT, "error-growth.svg"), W, H, *body,
           title="Похибка позиції: акселерометр росте як t², гіроскоп як t³")


# ── Фігура (math): чотири системи відліку ────────────────────────────────────
def fig_frames():
    W, H = 880, 560
    b = []
    Ox, Oy, R = 350, 330, 150

    # інерціальні «зорі» + підпис (верхній лівий кут)
    for (sx, sy) in [(70, 70), (118, 54), (92, 112), (158, 92),
                     (58, 150), (196, 64), (214, 126), (150, 158)]:
        b.append(text(sx, sy, "✦", size=13, color=MUTED))
    b.append(fitbox(44, 178, 228, 42,
                    "і — інерціальна:\n"
                    "осі на зорях, не крутиться",
                    size=11.5, bold=True, fill="#eef2fb", stroke=NEG))

    # Земля + полярна вісь
    b.append(circle(Ox, Oy, R, fill="#eaf6ee", stroke=FIELD, sw=2))
    b.append(line(Ox, Oy - R - 66, Ox, Oy + R + 34, color=MUTED, sw=1.4, dash="5 5"))
    b.append(text(Ox, Oy + R + 52, "полярна вісь", size=11, color=MUTED))

    # ω_ie — дуга обертання над полюсом
    top = Oy - R - 44
    b.append('<path d="M %.1f %.1f A 30 30 0 1 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrow)"/>' % (Ox - 26, top, Ox + 22, top - 14, NEG))
    b.append(text(Ox - 4, top - 26, "ω_ie", size=14, bold=True, color=NEG))
    b.append(text(Ox + 150, top + 4, "Земля крутиться ≈ 15°/год",
                  size=10.5, color=MUTED, anchor="start"))

    # e — земна (підпис поза колом, ліворуч знизу)
    b.append(fitbox(60, 452, 208, 42,
                    "e — земна:\nосі крутяться з Землею",
                    size=11.5, bold=True, fill="#eaf6ee", stroke=FIELD))

    # апарат A на середній широті (верхній правий сектор)
    beta = math.radians(46)
    Ax = Ox + R * math.sin(beta)
    Ay = Oy - R * math.cos(beta)
    rad = (math.sin(beta), -math.cos(beta))       # назовні від центра
    dn = (-rad[0], -rad[1])                        # вниз (до центра)
    no = (-math.cos(beta), -math.sin(beta))        # північ (до полюса)
    b.append(circle(Ax, Ay, 3.5, fill=INK, stroke=INK))
    b.append(arrow(Ax, Ay, Ax + 50 * dn[0], Ay + 50 * dn[1], color=NEG, sw=2.6))
    b.append(text(Ax + 50 * dn[0] - 6, Ay + 50 * dn[1] + 15, "вниз", size=11, color=NEG))
    b.append(arrow(Ax, Ay, Ax + 50 * no[0], Ay + 50 * no[1], color=INK, sw=2.4))
    b.append(text(Ax + 50 * no[0] - 20, Ay + 50 * no[1] - 6, "північ", size=11, color=INK))
    # осі тіла — нахилений кубик назовні
    bx, by = Ax + 42 * rad[0], Ay + 42 * rad[1]
    b.append(rrect(bx, by, 34, 34, 22, fill="#fdeeec", stroke=POS, sw=1.8))
    b.append(text(bx, by + 4, "b", size=13, bold=True, color=POS))
    b.append(text(bx + 44, by - 5, "осі тіла", size=10.5, color=POS, anchor="start"))
    b.append(text(bx + 44, by + 11, "(гіро + акс)", size=10, color=MUTED, anchor="start"))
    b.append(text(Ax + 98, Ay + 20, "n — навігаційна",
                  size=11.5, bold=True, color=INK, anchor="start"))
    b.append(text(Ax + 98, Ay + 36, "(місцевий горизонт)",
                  size=10, color=MUTED, anchor="start"))

    # ω_en — при русі по поверхні горизонт довертається (дуга вздовж поверхні)
    g1, g2 = math.radians(60), math.radians(82)
    p1 = (Ox + (R + 16) * math.sin(g1), Oy - (R + 16) * math.cos(g1))
    p2 = (Ox + (R + 16) * math.sin(g2), Oy - (R + 16) * math.cos(g2))
    b.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (p1[0], p1[1], R + 16, R + 16, p2[0], p2[1], FIELD))
    b.append(text(p2[0] + 12, p2[1] + 20, "ω_en — при русі",
                  size=10.5, bold=True, color=FIELD, anchor="start"))
    b.append(text(p2[0] + 12, p2[1] + 35, "горизонт довертається",
                  size=10.5, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "frames.svg"), W, H, *b,
           title="Чотири системи відліку інерціальної навігації")


# ── Фігура (math): g проти γ — тяжіння, відцентрове, виска ────────────────────
def fig_gravity_gamma():
    W, H = 720, 470
    b = []
    Ox, Oy, R = 250, 372, 172
    b.append(circle(Ox, Oy, R, fill="#eaf6ee", stroke=FIELD, sw=1.8))
    b.append(line(Ox, Oy - R - 22, Ox, Oy + 46, color=MUTED, sw=1.4, dash="5 5"))
    b.append(text(Ox, Oy - R - 32, "вісь обертання", size=10.5, color=MUTED))
    b.append(circle(Ox, Oy, 3, fill=INK, stroke=INK))
    b.append(text(Ox - 12, Oy + 16, "центр", size=10, color=MUTED, anchor="end"))

    beta = math.radians(42)
    Px = Ox + R * math.sin(beta)
    Py = Oy - R * math.cos(beta)
    b.append(circle(Px, Py, 4, fill=INK, stroke=INK))
    # ρ — відстань до осі (горизонтальний пунктир)
    b.append(line(Px, Py, Ox, Py, color=MUTED, sw=1.2, dash="4 4"))
    b.append(text((Px + Ox) / 2, Py - 8, "ρ", size=13, italic=True, color=MUTED))

    # γ — до центра (синя, довга); підпис збоку по середині стрілки
    gd = (Ox - Px, Oy - Py)
    gl = math.hypot(*gd)
    gd = (gd[0] / gl, gd[1] / gl)
    b.append(arrow(Px, Py, Px + 152 * gd[0], Py + 152 * gd[1], color=NEG, sw=3))
    b.append(text(Px + 78 * gd[0] - 14, Py + 78 * gd[1] - 4, "γ  тяжіння",
                  size=12, bold=True, color=NEG, anchor="end"))
    b.append(text(Px + 78 * gd[0] - 14, Py + 78 * gd[1] + 12, "(до маси)",
                  size=10, color=MUTED, anchor="end"))

    # відцентрове — від осі назовні (горизонтально, червона)
    b.append(arrow(Px, Py, Px + 68, Py, color=POS, sw=2.8))
    b.append(text(Px + 76, Py - 7, "відцентрове", size=11, bold=True, color=POS, anchor="start"))
    b.append(text(Px + 76, Py + 9, "Ω²ρ (від осі)", size=10, color=POS, anchor="start"))

    # g = γ + відцентрове (жирна)
    gx = 152 * gd[0] + 68
    gy = 152 * gd[1]
    b.append(arrow(Px, Py, Px + gx, Py + gy, color=INK, sw=3.6))
    b.append(text(Px + gx + 4, Py + gy + 16, "g — сила тяжіння (виска)",
                  size=12, bold=True, color=INK))

    b.append(fitbox(W / 2 - 250, 412, 500, 44,
                    "екватор g ≈ 9.780   ·   полюс g ≈ 9.832 м/с²   ·   "
                    "відцентрове на екваторі  Ω²R ≈ 0.034 м/с²",
                    size=12, bold=True, fill="#eaf6ee", stroke=FIELD))
    render(os.path.join(OUT, "gravity-gamma.svg"), W, H, *b,
           title="g проти γ: тяжіння, відцентрове й місцева виска")


# ── Фігура (math): coning — некомутативність поворотів ────────────────────────
def fig_coning():
    W, H = 700, 500
    b = []
    apex = (350, 430)
    cx, cy = 350, 178
    rx, ry = 128, 36

    # вісь конуса
    b.append(line(apex[0], apex[1], cx, 158, color=MUTED, sw=1.4, dash="5 5"))
    b.append(arrow(apex[0], apex[1] - 6, cx, 150, color=MUTED, sw=1.6))
    b.append(text(cx + 82, 156, "вісь конуса", size=11, color=MUTED, anchor="start"))

    # ребра + основа
    b.append(line(apex[0], apex[1], cx - rx, cy, color=LINE, sw=1.4))
    b.append(line(apex[0], apex[1], cx + rx, cy, color=LINE, sw=1.4))
    b.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="4 4"/>' % (cx, cy, rx, ry, MUTED))

    def base_pt(deg):
        a = math.radians(deg)
        return (cx + rx * math.cos(a), cy + ry * math.sin(a))

    for d in (150, 215, 300):
        p = base_pt(d)
        b.append(line(apex[0], apex[1], p[0], p[1], color=MUTED, sw=1.0))
    p = base_pt(40)
    b.append(arrow(apex[0], apex[1], p[0], p[1], color=INK, sw=2.6))
    b.append(text(p[0] + 8, p[1] + 5, "миттєва вісь тіла",
                  size=11, bold=True, color=INK, anchor="start"))

    # сталий знос навколо осі — кругова стрілка над еліпсом
    b.append('<path d="M %.1f %.1f A 56 20 0 1 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (cx + 56, cy - ry - 16, cx - 52, cy - ry - 16, POS))
    b.append(text(cx, cy - ry - 44,
                  "сталий знос навколо осі — ∫ω dt його не бачить",
                  size=11, bold=True, color=POS))

    # два хитання в квадратурі — інсет ліворуч
    ix, iy = 118, 372
    b.append(arrow(ix - 34, iy, ix + 34, iy, color=NEG, sw=2))
    b.append(arrow(ix + 34, iy, ix - 34, iy, color=NEG, sw=2))
    b.append(arrow(ix, iy - 30, ix, iy + 30, color=FIELD, sw=2))
    b.append(arrow(ix, iy + 30, ix, iy - 30, color=FIELD, sw=2))
    b.append(text(ix, iy + 52, "два хитання", size=10.5, color=INK))
    b.append(text(ix, iy + 67, "у квадратурі (¼ періоду)", size=10, color=MUTED))

    b.append(fitbox(W / 2 - 214, 452, 428, 42,
                    "поправка:  φ = Δθ₁ + Δθ₂ + (2/3)·(Δθ₁ × Δθ₂)",
                    size=13, bold=True, fill="#fdeeec", stroke=POS))
    render(os.path.join(OUT, "coning.svg"), W, H, *b,
           title="Coning: некомутативність поворотів — знос, якого інтеграл не бачить")


if __name__ == "__main__":
    fig_specific_force()
    fig_gimbal_vs_strapdown()
    fig_mechanization()
    fig_gravity_leak()
    fig_inertial_timeline()
    fig_rlg_invention_layers()
    fig_circle_recover()
    fig_error_growth()
    fig_frames()
    fig_gravity_gamma()
    fig_coning()
    print("figs done")
