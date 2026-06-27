# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: ланцюжок strapdown ──────────────────────────────────────────────

def fig_strapdown_chain():
    W, H = 820, 430
    p = []

    # дві вхідні коробки (гіроскоп, акселерометр)
    bx = 30
    p.append(fitbox(bx, 60, 150, 64, "Гіроскоп\nкутова швидкість",
                    size=13, fill="#eef3fe", stroke=NEG, sw=1.6))
    p.append(fitbox(bx, 250, 150, 64, "Акселерометр\nпитома сила",
                    size=13, fill="#fdecea", stroke=POS, sw=1.6))

    # ланцюг орієнтації (верх)
    p.append(fitbox(230, 60, 150, 64, "інтеграл →\nОРІЄНТАЦІЯ",
                    size=13, fill="#eef3fe", stroke=NEG, sw=1.6))
    p.append(arrow(bx + 150, 92, 230, 92, color=NEG, sw=2.0))

    # поворот у світові осі (центр) — приймає і акселерометр, і орієнтацію
    p.append(fitbox(230, 250, 170, 64, "поворот вектора\nу СВІТОВІ осі",
                    size=13, fill=FILL, stroke=INK, sw=1.6))
    p.append(arrow(bx + 150, 282, 230, 282, color=POS, sw=2.0))
    # орієнтація вниз у поворот
    p.append(arrow(305, 124, 305, 250, color=NEG, sw=2.0))
    p.append(text(312, 192, "повертає", size=11, color=NEG, anchor="start", italic=True))

    # віднімання тяжіння
    p.append(fitbox(440, 250, 160, 64, "− вектор\nТЯЖІННЯ (g)",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(arrow(400, 282, 440, 282, color=INK, sw=2.0))

    # подвійний інтеграл → положення
    p.append(fitbox(640, 250, 150, 64, "ПОДВІЙНИЙ\nінтеграл",
                    size=13, fill=FILL, stroke=INK, sw=1.6))
    p.append(arrow(600, 282, 640, 282, color=INK, sw=2.0))

    p.append(fitbox(640, 110, 150, 60, "ПОЛОЖЕННЯ\nx, y, z",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(arrow(715, 250, 715, 170, color=FIELD, sw=2.2))

    # підпис під центральним рядком: справжнє прискорення руху
    p.append(text(520, 340, "справжнє прискорення руху", size=11, color=MUTED, italic=True))

    # виноска про головну похибку
    p.append(fitbox(30, 358, 760, 50,
                    "помилка ОРІЄНТАЦІЇ криво повертає вектор → тяжіння віднімається неточно "
                    "→ залишок g вливається в положення як фантомний рух",
                    size=12, fill="#fff7ed", stroke="#d97706", sw=1.4))

    render(os.path.join(OUT, "strapdown-chain.svg"), W, H, *p,
           title="Ланцюжок безкарданної (strapdown) інерціальної навігації")


# ── Фігура 2: ріст похибки положення (t, t², t³) ──────────────────────────────

def fig_error_growth():
    W, H = 760, 470
    ox, oy = 90, 380          # початок координат (лівий-нижній)
    Ax, Ay = 600, 320         # довжина осей

    p = []
    # осі
    p.append(line(ox, oy, ox + Ax + 26, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 8, oy, ox + Ax + 28, oy, color=MUTED, sw=1.4))
    p.append(line(ox, oy, ox, oy - Ay - 16, color=MUTED, sw=1.4))
    p.append(arrow(ox, oy - Ay, ox, oy - Ay - 18, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 34, oy + 6, "час", size=13, color=MUTED, italic=True, anchor="end"))
    p.append(text(ox - 14, oy - Ay - 26, "похибка положення", size=13, color=MUTED, italic=True, anchor="start"))

    # нормуємо так, щоб усі три криві помістились; беремо t∈[0..1]
    def curve(fn, color, sw=2.8):
        pts = []
        for i in range(0, 161):
            t = i / 160.0
            val = fn(t)
            xx = ox + Ax * t
            yy = oy - Ay * min(val, 1.0)
            pts.append("%.1f,%.1f" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), color, sw)

    # масштаби підібрані, щоб криві розходились наочно й упирались у стелю в кінці
    p.append(curve(lambda t: 0.55 * t,        NEG))     # лінійна (шум/повільне)
    p.append(curve(lambda t: 1.0 * t * t,     POS))     # квадратична (зсув акселерометра)
    p.append(curve(lambda t: 1.0 * t ** 3,    "#7e22ce"))  # кубічна (дрейф гіроскопа)

    # підписи кривих біля правого краю
    p.append(text(ox + Ax * 0.62 + 6, oy - Ay * 0.55 * 0.62 - 8,
                  "∝ t  (шум)", size=12, color=NEG, anchor="start"))
    p.append(text(ox + Ax * 0.86, oy - Ay * (0.86 ** 2) - 10,
                  "∝ t²  (зсув акселерометра)", size=12, color=POS, anchor="end"))
    p.append(text(ox + Ax * 0.74, oy - Ay * (0.92 ** 3) + 4,
                  "∝ t³  (дрейф гіроскопа)", size=12, color="#7e22ce", anchor="end"))

    # зона «коротко — точно»
    p.append(line(ox + Ax * 0.16, oy - Ay - 4, ox + Ax * 0.16, oy + 4, color=FIELD, sw=1.2, dash="4 4"))
    z1, wz, hz = textbox(ox + Ax * 0.08, oy - Ay * 0.86,
                         "коротко:\nточно",
                         size=11, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(z1)
    z2, wz2, hz2 = textbox(ox + Ax * 0.66, oy - Ay * 0.88,
                           "довго: оцінка тікає",
                           size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(z2)

    render(os.path.join(OUT, "error-growth.svg"), W, H, *p,
           title="Похибка інерціального положення росте швидше за лінійну: t², t³")


# ── Фігура 3: інерціалка заповнює проміжки між поправками GNSS ─────────────────

def fig_fusion_timeline():
    W, H = 800, 360
    ox, oy = 70, 250
    Ax = 660

    p = []
    # вісь часу
    p.append(line(ox - 6, oy, ox + Ax + 26, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox + Ax + 8, oy, ox + Ax + 28, oy, color=MUTED, sw=1.4))
    p.append(text(ox + Ax + 34, oy + 6, "час", size=13, color=MUTED, italic=True, anchor="end"))

    # рівень «істинне положення» — пряма
    y_true = oy - 150
    p.append(line(ox, y_true, ox + Ax, y_true, color=FIELD, sw=2.0, dash="7 5"))
    p.append(text(ox + 4, y_true - 12, "істинне положення", size=12, color=FIELD, anchor="start"))

    # поправки GNSS: рідкі точки, шумні навколо істини
    fixes_x = [ox + Ax * f for f in (0.0, 0.30, 0.60, 0.90)]
    fixes_y = [y_true + d for d in (0, 14, -10, 8)]   # шум GNSS

    # інерціальна оцінка: між поправками тікає (парабола вгору), на поправці — скидається до GNSS
    seg = []
    for k in range(len(fixes_x)):
        x0 = fixes_x[k]
        y0 = fixes_y[k]
        x1 = fixes_x[k + 1] if k + 1 < len(fixes_x) else ox + Ax
        # дрейф угору протягом проміжку (квадратично)
        pts = []
        for i in range(0, 41):
            t = i / 40.0
            xx = x0 + (x1 - x0) * t
            yy = y0 - 70 * (t * t)     # тікає вгору
            pts.append("%.1f,%.1f" % (xx, yy))
        seg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), NEG))
    p += seg

    # точки поправок GNSS поверх
    for x, y in zip(fixes_x, fixes_y):
        p.append(circle(x, y, 5.5, fill=POS, stroke=POS))
        p.append(line(x, oy - 4, x, oy + 4, color=MUTED, sw=1.0))

    # вертикальна «скидка» дрейфу на кожній поправці (крім першої)
    for k in range(1, len(fixes_x)):
        x = fixes_x[k]
        y_drift = fixes_y[k - 1] - 70   # де інерціалка була перед поправкою
        p.append(line(x, y_drift, x, fixes_y[k], color=MUTED, sw=1.4, dash="3 3"))

    # легенда
    p.append(line(ox + 30, 60, ox + 64, 60, color=NEG, sw=2.6))
    p.append(text(ox + 70, 64, "інерціальна оцінка (гладка, тікає в проміжку)", size=12, color=MUTED, anchor="start"))
    p.append(circle(ox + 47, 86, 5.5, fill=POS, stroke=POS))
    p.append(text(ox + 70, 90, "поправка GNSS (рідка, шумна, скидає дрейф)", size=12, color=MUTED, anchor="start"))

    # підпис проміжку
    bx, wbx, hbx = textbox((fixes_x[1] + fixes_x[2]) / 2, oy - 200,
                           "у проміжку веде інерціалка\nна поправці — підтяг до GNSS",
                           size=11, color=INK, fill=FILL, stroke=INK)
    p.append(bx)

    render(os.path.join(OUT, "fusion-timeline.svg"), W, H, *p,
           title="Поєднання: інерціалка веде в проміжках, GNSS скидає дрейф")


# ── Фігура 4 (для вставки proj): поворот вектора в світ і віднімання тяжіння ──

def fig_body_to_world():
    W, H = 840, 430
    p = []

    # --- ЛІВО: осі апарата (нахилені) і виміряний вектор акселерометра ---
    cxL, cyL = 210, 250
    L = 110
    ang = math.radians(22)          # нахил апарата на 22°
    ca, sa = math.cos(ang), math.sin(ang)
    # нахилені осі тіла: forward (xb) і up (zb)
    fx, fy = cxL + L * ca, cyL - L * sa            # вісь "вперед" апарата
    ux, uy = cxL + L * sa, cyL - L * ca            # вісь "вгору" апарата
    p.append(line(cxL, cyL, fx, fy, color=MUTED, sw=1.6, dash="4 3"))
    p.append(line(cxL, cyL, ux, uy, color=MUTED, sw=1.6, dash="4 3"))
    p.append(text(fx + 8, fy + 4, "вісь апарата", size=10, color=MUTED, anchor="start"))
    # виміряний вектор акселерометра у спокої = реакція опори, дивиться по "вгору апарата"
    amx, amy = cxL + 95 * sa, cyL - 95 * ca
    p.append(arrow(cxL, cyL, amx, amy, color=POS, sw=3.0))
    p.append(text(amx + 6, amy - 2, "вимір a_b", size=12, color=POS, anchor="start", bold=True))
    p.append(circle(cxL, cyL, 4, fill=INK, stroke=INK))
    p.append(text(cxL, cyL + 150, "осі АПАРАТА (нахилені)", size=12, color=INK))
    p.append(text(cxL, cyL + 168, "акселерометр міряє тут", size=11, color=MUTED, italic=True))

    # --- стрілка переходу: поворот кватерніоном ---
    p.append(arrow(345, 230, 455, 230, color=NEG, sw=2.4))
    p.append(text(400, 218, "q повертає", size=12, color=NEG))
    p.append(text(400, 246, "у світ", size=12, color=NEG))

    # --- ПРАВО: світові осі (рівні) ---
    cxR, cyR = 620, 250
    # вертикальна (вгору) і горизонтальна (північ)
    p.append(line(cxR, cyR, cxR, cyR - L, color=MUTED, sw=1.6))
    p.append(line(cxR, cyR, cxR + L, cyR, color=MUTED, sw=1.6))
    p.append(text(cxR, cyR - L - 8, "вгору (світ)", size=10, color=MUTED))
    p.append(text(cxR + L + 6, cyR + 4, "північ", size=10, color=MUTED, anchor="start"))
    p.append(circle(cxR, cyR, 4, fill=INK, stroke=INK))

    # повернутий вимір a_w (той самий вектор у світі: майже вертикальний, бо це тяжіння)
    awx, awy = cxR + 95 * sa, cyR - 95 * ca
    p.append(arrow(cxR, cyR, awx, awy, color=POS, sw=3.0))
    p.append(text(awx + 6, awy - 4, "a_w", size=12, color=POS, anchor="start", bold=True))
    # вектор тяжіння, який віднімаємо: рівно вертикально вгору на |g|
    gx, gy = cxR, cyR - 92
    p.append(arrow(cxR, cyR, gx, gy, color=FIELD, sw=3.0))
    p.append(text(cxR - 8, cyR - 50, "− g", size=12, color=FIELD, anchor="end", bold=True))
    # залишок (a_w − g): маленький горизонтальний фантом
    p.append(arrow(gx, gy, awx, awy, color="#d97706", sw=2.6))
    p.append(text((gx + awx) / 2, gy - 8, "залишок", size=11, color="#d97706"))
    p.append(text(cxR, cyR + 150, "осі СВІТУ (рівні)", size=12, color=INK))
    p.append(text(cxR, cyR + 168, "тут віднімаємо g", size=11, color=MUTED, italic=True))

    # підпис-висновок
    box, bw, bh = textbox(W / 2, 388,
                          "крихітна похибка q трохи криво повертає a_w → після − g лишається\n"
                          "фантомний горизонтальний залишок → його інтегрують у неіснуючий рух",
                          size=11.5, color=INK, fill="#fff7ed", stroke="#d97706", sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "body-to-world.svg"), W, H, *p,
           title="Поворот вектора акселерометра у світові осі й віднімання тяжіння")


# ── Фігура 5 (для вставки proj): порядок інтегрування Ейлера ──────────────────

def fig_euler_order():
    W, H = 820, 430
    p = []

    def col(x0, headline, head_fill, head_stroke, l1, l2, note, note_fill, note_stroke):
        frags = []
        w = 340
        frags.append(fitbox(x0, 60, w, 42, headline, size=15, bold=True,
                            fill=head_fill, stroke=head_stroke, sw=1.8))
        # два рядки коду в порядку виконання
        frags.append(fitbox(x0, 128, w, 50, l1, size=13, fill=FILL, stroke=INK, sw=1.4))
        frags.append(arrow(x0 + w / 2, 178, x0 + w / 2, 206, color=MUTED, sw=2.0))
        frags.append(fitbox(x0, 206, w, 50, l2, size=13, fill=FILL, stroke=INK, sw=1.4))
        # нота-висновок
        nb = fitbox(x0, 300, w, 80, note, size=12.5, fill=note_fill, stroke=note_stroke, sw=1.5)
        frags.append(nb)
        return frags

    # ЛІВО — semi-implicit (правильно)
    p += col(40,
             "semi-implicit Euler  ✓",
             "#eafaf0", FIELD,
             "1)  vel += a · dt",
             "2)  pos += vel · dt",
             "pos бере ВЖЕ оновлену vel:\nкрок узгоджений, енергія не\nрозбігається — стандарт для\nнавігації й фізики",
             "#eafaf0", FIELD)

    # ПРАВО — forward (explicit) Euler (гірше)
    p += col(440,
             "explicit (forward) Euler  ✗",
             "#fdecea", POS,
             "1)  pos += vel · dt",
             "2)  vel += a · dt",
             "pos бере СТАРУ vel (до кроку):\nположення відстає на крок,\nпохибка накопичується\nшвидше — так НЕ роблять",
             "#fdecea", POS)

    # підпис унизу
    p.append(text(W / 2, 408,
                  "та сама пара рядків — різний ПОРЯДОК. Спершу оновлюємо швидкість, тоді нею рухаємо положення.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "euler-order.svg"), W, H, *p,
           title="Порядок інтегрування: спершу швидкість, тоді положення")


# ── Фігура 6 (для вставки hist): лінія розвитку інерціальної навігації ─────────

def fig_ins_timeline():
    W, H = 880, 470
    p = []

    # горизонтальна вісь часу
    ox, oy = 60, 120
    Ax = 760
    p.append(line(ox, oy, ox + Ax + 26, oy, color=MUTED, sw=1.6))
    p.append(arrow(ox + Ax + 8, oy, ox + Ax + 28, oy, color=MUTED, sw=1.6))
    p.append(text(ox + Ax + 30, oy - 10, "час", size=13, color=MUTED, italic=True, anchor="end"))

    # п'ять віх: зсув 0..1, рік, назва, суть, колір рамки, бік (верх +1 / низ -1)
    milestones = [
        (0.03, "1852",        "Фуко",                            "НАЗВАВ гіроскоп;\nпоказує обертання",          NEG,       +1),
        (0.27, "1908–14",     "Сперрі / Аншютц",                 "гірокомпас, автопілот:\nгіроскоп ТРИМАЄ курс", "#7e22ce", -1),
        (0.50, "1940-ті",     "«Фау-2» (LEV-3)",                 "перша масова РЕАЛІЗАЦІЯ:\n2 гіро + інт. акселер.", POS,    +1),
        (0.73, "1953 →",      "Дрейпер: SPIRE,\nSINS, «Аполлон»","карданна платформа;\nдоведено навігацію",    "#b45309", -1),
        (0.96, "1970–80-ті →","strapdown + MEMS",                "механіку платформи\nзамінює процесор",         FIELD,     +1),
    ]

    for fx, year, name, gist, col, side in milestones:
        x = ox + Ax * fx
        p.append(circle(x, oy, 6, fill=col, stroke=col))
        p.append(text(x, oy + (26 if side < 0 else -14), year, size=12, color=INK, bold=True))
        by = oy - 102 if side > 0 else oy + 46
        p.append(fitbox(x - 88, by, 176, 84, name + "\n" + gist,
                        size=11, fill=FILL, stroke=col, sw=1.6))
        if side > 0:
            p.append(line(x, oy - 6, x, by + 84, color=col, sw=1.2, dash="3 3"))
        else:
            p.append(line(x, oy + 6, x, by, color=col, sw=1.2, dash="3 3"))

    # нижня смуга-висновок: розум переходить з механіки в математику
    p.append(arrow(ox, H - 40, ox + Ax, H - 40, color=INK, sw=2.0))
    p.append(text(ox + 2, H - 50, "більше МЕХАНІКИ", size=12, color=MUTED, anchor="start", italic=True))
    p.append(text(ox + Ax, H - 50, "більше МАТЕМАТИКИ (обчислень)", size=12, color=MUTED, anchor="end", italic=True))

    render(os.path.join(OUT, "ins-timeline.svg"), W, H, *p,
           title="Лінія розвитку інерціальної навігації: від гіроскопа Фуко до MEMS")


# ── Фігура 7 (для вставки hist): принцип Шулера ───────────────────────────────

def fig_schuler():
    W, H = 800, 470
    p = []

    pivot_y = 78

    # ── ЛІВО: короткий маятник, збитий поштовхом ──
    cx = 200
    p.append(circle(cx, pivot_y, 5, fill=INK, stroke=INK))
    p.append(arrow(cx - 38, pivot_y, cx + 38, pivot_y, color=POS, sw=2.2))
    p.append(text(cx, pivot_y - 16, "різкий поштовх підвісу", size=12, color=POS))
    # справжня вертикаль — пунктир
    p.append(line(cx, pivot_y, cx, pivot_y + 250, color=MUTED, sw=1.4, dash="5 5"))
    p.append(text(cx, pivot_y + 268, "справжній «низ»", size=11, color=MUTED))
    # маятник відхилений (бреше про «низ»)
    bob_x, bob_y = cx + 78, pivot_y + 205
    p.append(line(cx, pivot_y, bob_x, bob_y, color=NEG, sw=2.4))
    p.append(circle(bob_x, bob_y, 15, fill="#eef3fe", stroke=NEG, sw=2.0))
    p.append(text(bob_x + 20, bob_y, "хибний «низ»", size=11, color=POS, anchor="start"))
    b1, w1, h1 = textbox(cx, H - 34,
                         "короткий маятник: поштовх ЗБИВАЄ —\nяк наївна платформа від прискорення",
                         size=11, color=POS, fill="#fdecea", stroke=POS)
    p.append(b1)

    # ── ПРАВО: маятник до центру Землі, незрушний ──
    cx2 = 580
    p.append(circle(cx2, pivot_y, 5, fill=INK, stroke=INK))
    p.append(arrow(cx2 - 38, pivot_y, cx2 + 38, pivot_y, color=POS, sw=2.2))
    p.append(text(cx2, pivot_y - 16, "той самий поштовх", size=12, color=POS))
    # стрижень прямо вниз і далі до центру Землі
    p.append(line(cx2, pivot_y, cx2, pivot_y + 255, color=FIELD, sw=2.6))
    p.append(arrow(cx2, pivot_y + 238, cx2, pivot_y + 258, color=FIELD, sw=2.6))
    p.append(text(cx2, pivot_y + 276, "до центру Землі (R ≈ 6371 км)", size=11, color=FIELD))
    b2, w2, h2 = textbox(cx2, H - 34,
                         "маятник у радіус Землі (T ≈ 84 хв):\nтой самий поштовх НЕ збиває",
                         size=11, color=FIELD, fill="#eafaf0", stroke=FIELD)
    p.append(b2)

    render(os.path.join(OUT, "schuler.svg"), W, H, *p,
           title="Принцип Шулера: платформа з періодом 84 хв лишається вертикальною")


if __name__ == "__main__":
    fig_strapdown_chain()
    fig_error_growth()
    fig_fusion_timeline()
    fig_body_to_world()
    fig_euler_order()
    fig_ins_timeline()
    fig_schuler()
    print("OK: figures written to", OUT)
