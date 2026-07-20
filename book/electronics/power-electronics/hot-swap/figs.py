# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, **kw):
    """textbox, але повертає лише svg-рядок (ширину/висоту відкидаємо)."""
    body, _, _ = textbox(cx, cy, s, **kw)
    return body


def poly(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polyfill(pts, fill=FIELD, stroke=None, sw=2.6, op=0.15, dash=None):
    """Замкнений многокутник із напівпрозорою заливкою (площа = енергія)."""
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    st = stroke if stroke else fill
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, fill, op, st, sw, d))


def cap(cx, cy, lead=18, gap=9, plate=26, color=INK, sw=2.4):
    """Символ конденсатора (дві пластини) з вертикальними виводами."""
    out = []
    out.append(line(cx, cy - lead - gap / 2, cx, cy - gap / 2, color=color, sw=sw))
    out.append(line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color=color, sw=sw))
    out.append(line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color=color, sw=sw))
    out.append(line(cx, cy + gap / 2, cx, cy + lead + gap / 2, color=color, sw=sw))
    return "".join(out)


def gnd(cx, cy, w=26, color=INK, sw=2.2):
    out = [line(cx, cy, cx, cy + 10, color=color, sw=sw)]
    yy = cy + 10
    for i, ww in enumerate((w, w * 0.6, w * 0.25)):
        out.append(line(cx - ww / 2, yy + i * 5, cx + ww / 2, yy + i * 5, color=color, sw=sw))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — проблема: плата в живій шині тягне кидок і просаджує сусідів
# ─────────────────────────────────────────────────────────────────────────────
def fig_live_bus():
    W, H = 880, 470
    f = []
    railY = 130
    # шина
    f.append(line(60, railY, 800, railY, color=POS, sw=3.2))
    f.append(text(60, railY - 16, "спільна шина +12 В (жива)", size=15, color=POS,
                  anchor="start", bold=True))
    # земляна шина знизу
    f.append(line(60, 400, 800, 400, color=NEG, sw=2.6))
    f.append(text(60, 420, "спільна земля (GND)", size=13, color=NEG, anchor="start"))

    # дві плати, що вже працюють
    for bx, name in ((150, "Плата A"), (320, "Плата B")):
        f.append(line(bx + 55, railY, bx + 55, 200, color=INK, sw=2))
        f.append(line(bx + 55, 300, bx + 55, 400, color=INK, sw=2))
        f.append(box(bx + 55, 250, name + "\n(працює)", size=14, min_w=120))
    # напис про просідання (між стемами плат A і B, щоб лінії не перетинали текст)
    f.append(text(290, 345, "шина просідає", size=12, color=POS, anchor="middle"))
    f.append(text(290, 363, "сусіди скидаються", size=12, color=POS, anchor="middle"))

    # нова плата праворуч
    f.append(box(660, 250, "Нова плата", size=14, min_w=150))
    f.append(cap(660, 315, lead=14, gap=10, plate=34, color=INK))
    f.append(text(660, 355, "Cбулк ≈ 0 В (розряджений)", size=12.5, color=INK, anchor="middle"))
    # стем нової плати до шини — місце контакту
    f.append(line(660, railY, 660, 218, color=INK, sw=2))
    f.append(circle(660, railY, 6, fill=POS, stroke=POS))
    # стрілка вставляння
    f.append(arrow(770, 80, 690, 80, color=INK, sw=2.2))
    f.append(text(775, 84, "вставляють", size=13, color=INK, anchor="start"))
    # кидок струму — товста червона стрілка вгору в шину
    f.append(arrow(700, 200, 700, railY + 6, color=POS, sw=3.4))
    f.append(text(715, 175, "кидок струму", size=13.5, color=POS, anchor="start", bold=True))
    f.append(text(715, 193, "(майже коротке)", size=12.5, color=POS, anchor="start"))

    render(os.path.join(IMG, "live-bus-inrush.svg"), W, H, *f,
           title="Вставлення плати в живу шину")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — роз'єм зі сходинкою: різні довжини штирів = порядок торкання
# ─────────────────────────────────────────────────────────────────────────────
def fig_pins():
    W, H = 900, 470
    f = []
    # тіло плати
    f.append(rect(50, 130, 120, 210, fill=FILL, stroke=INK, sw=1.8))
    f.append(box(110, 235, "Плата", size=14, min_w=96))
    # напрям вставляння
    f.append(arrow(60, 100, 210, 100, color=INK, sw=2.2))
    f.append(text(215, 104, "вставляння →", size=13, color=INK, anchor="start"))

    plane = 645
    # контактна площина шини
    f.append(line(plane, 150, plane, 340, color=MUTED, sw=3))
    f.append(text(plane, 138, "контакти шини", size=12.5, color=MUTED, anchor="middle"))

    pins = [
        (175, plane,        POS,  "1. GND (найдовший) — торкається першим"),
        (245, plane - 70,   INK,  "2. живлення (середній) — заряд Cбулк"),
        (315, plane - 150,  NEG,  "3. present (найкоротший) — останнім"),
    ]
    for y, tipx, col, lab in pins:
        f.append(line(170, y, tipx, y, color=col, sw=6))
        f.append(text(185, y - 12, lab, size=12.5, color=col, anchor="start", bold=True))
        if tipx >= plane:
            f.append(circle(plane, y, 6, fill=col, stroke=col))     # торкнулась
        else:
            f.append(line(tipx, y, plane, y, color=MUTED, sw=1.4, dash="4 5"))
            f.append(text((tipx + plane) / 2, y - 10, "ще ні", size=10.5,
                          color=MUTED, anchor="middle"))

    # часова вісь порядку
    f.append(arrow(120, 415, 780, 415, color=INK, sw=2))
    for x, t, col in ((190, "GND", POS), (430, "живлення", INK), (660, "present", NEG)):
        f.append(circle(x, 415, 4, fill=col, stroke=col))
        f.append(text(x, 438, t, size=12.5, color=col, anchor="middle"))
    f.append(text(450, 395, "порядок у часі; при вийманні — навпаки",
                  size=12.5, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "staggered-pins.svg"), W, H, *f,
           title="Роз'єм зі сходинкою: хто торкається першим")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — керований ключ (схема) + форма струму (пік проти плато)
# ─────────────────────────────────────────────────────────────────────────────
def fig_ramp():
    W, H = 960, 480
    f = []
    f.append(line(495, 60, 495, 440, color=MUTED, sw=1.4, dash="3 6"))
    f.append(text(255, 58, "як побудовано", size=14, color=MUTED, bold=True))
    f.append(text(730, 58, "що виходить", size=14, color=MUTED, bold=True))

    # ── ліворуч: передня частина плати ──
    wireY = 150
    f.append(text(70, wireY - 22, "+Vin", size=13, color=POS, anchor="middle", bold=True))
    f.append(line(50, wireY, 110, wireY, color=INK, sw=2.4))
    # шунт
    f.append(rect(110, wireY - 15, 54, 30, fill="#fff5f5", stroke=POS, sw=1.8))
    f.append(text(137, wireY + 5, "Rшунт", size=12, color=POS))
    f.append(line(164, wireY, 210, wireY, color=INK, sw=2.4))
    # MOSFET-ключ
    f.append(box(275, wireY, "MOSFET\n(ключ)", size=12.5, min_w=110))
    f.append(line(330, wireY, 400, wireY, color=INK, sw=2.4))
    # вузол виходу → Cбулк + навантаження
    f.append(circle(400, wireY, 3.5, fill=INK, stroke=INK))
    f.append(cap(400, wireY + 46, lead=14, gap=9, plate=30))
    f.append(text(400, wireY + 92, "Cбулк", size=12, color=INK))
    f.append(gnd(400, wireY + 84))
    f.append(line(400, wireY, 452, wireY, color=INK, sw=2.4))
    f.append(box(452 + 0, wireY, "наван-\nтаження", size=11.5, min_w=78))

    # контролер
    f.append(box(250, 320, "контролер hot-swap:\nтримає струм на Iмежа,\nповільно піднімає затвор",
                 size=11.5, min_w=210))
    # давач струму: від шунта вниз до контролера
    f.append(arrow(137, wireY + 15, 175, 292, color=POS, sw=1.8))
    f.append(text(120, 240, "давач струму", size=11, color=POS, anchor="middle"))
    # керує затвором: від контролера до затвора MOSFET
    f.append(arrow(300, 292, 285, wireY + 22, color=INK, sw=1.8))
    f.append(text(360, 250, "керує затвором", size=11, color=INK, anchor="middle"))

    # ── праворуч: форма струму в часі ──
    ox, oy = 545, 400          # початок осей
    topY = 110
    rgt = 905
    f.append(arrow(ox, oy, rgt, oy, color=INK, sw=1.8))   # вісь часу
    f.append(arrow(ox, oy, ox, topY, color=INK, sw=1.8))  # вісь струму
    f.append(text(rgt, oy + 20, "час", size=12, color=INK, anchor="end"))
    f.append(text(ox - 8, topY - 4, "струм", size=12, color=INK, anchor="middle"))

    # без контролю — вузький високий пік
    f.append(poly([(ox + 4, oy), (ox + 16, topY + 6), (ox + 30, oy)], color=POS, sw=2.6))
    f.append(text(ox + 46, topY + 20, "без контролю:", size=12.5, color=POS, anchor="start", bold=True))
    f.append(text(ox + 46, topY + 37, "вузький пік — сотні А", size=12, color=POS, anchor="start"))

    # hot-swap — плато Iмежа, тоді спад до робочого струму
    platY = 300
    workY = 340
    f.append(poly([(ox + 4, oy), (ox + 55, platY), (ox + 250, platY),
                   (ox + 268, workY), (rgt - 20, workY)], color=FIELD, sw=3))
    f.append(line(ox, platY, ox + 55, platY, color=FIELD, sw=1, dash="3 5"))
    f.append(text(ox - 8, platY + 4, "Iмежа", size=11, color=FIELD, anchor="end"))
    f.append(text(ox + 120, platY - 14, "hot-swap: плато Iмежа,", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(ox + 120, platY + 22, "поки заряджається Cбулк", size=11.5, color=FIELD, anchor="start"))

    # Vout — плавно наростає (пунктир)
    f.append(poly([(ox + 4, oy - 4), (ox + 250, topY + 40), (rgt - 20, topY + 40)],
                  color=NEG, sw=2.2, dash="6 5"))
    f.append(text(ox + 150, topY + 30, "Vout наростає плавно", size=11.5, color=NEG, anchor="start"))

    render(os.path.join(IMG, "controlled-ramp.svg"), W, H, *f,
           title="Керований ключ і форма струму")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 (math-inrush-soa) — потужність на ключі: чесний фронт (трикутник,
# площа = ½·C·Vin²) проти аварії (прямокутник на весь таймер)
# ─────────────────────────────────────────────────────────────────────────────
def fig_power_energy():
    W, H = 1000, 560
    f = []

    P0y = 165           # рівень P₀
    oy = 430            # вісь часу
    axTop = 130         # верх осі потужності

    # ліва панель — чесний фронт
    axA = 95
    rampA = 320         # кінець фронту
    # права панель — аварія
    axB = 585
    endB = 880          # кінець таймера

    # спільна пунктирна лінія P₀ через обидві панелі
    f.append(line(70, P0y, 950, P0y, color=MUTED, sw=1.4, dash="5 5"))
    f.append(text(950, P0y - 10, "P₀ = Vin · Iмежа — той самий пік в обох випадках",
                  size=12.5, color=MUTED, anchor="end"))

    # підписи панелей
    f.append(text(240, 78, "чесний фронт: банк заряджається", size=14.5,
                  color=FIELD, anchor="middle", bold=True))
    f.append(text(730, 78, "аварія: вихід закорочено", size=14.5,
                  color=POS, anchor="middle", bold=True))

    # ── панель A ──
    f.append(arrow(axA, oy, 470, oy, color=INK, sw=1.8))
    f.append(arrow(axA, oy, axA, axTop, color=INK, sw=1.8))
    f.append(text(axA, axTop - 14, "потужність на ключі", size=12, color=INK, anchor="middle"))
    f.append(text(470, oy + 20, "час", size=12, color=INK, anchor="end"))
    # трикутник
    f.append(polyfill([(axA, P0y), (rampA, oy), (axA, oy)], FIELD, FIELD, sw=2.6, op=0.13))
    f.append(line(rampA, oy, rampA, oy + 8, color=FIELD, sw=1.8))
    f.append(text(rampA, oy + 26, "tрамп", size=12, color=FIELD, anchor="middle"))
    f.append(mtext(178, 352, ["Eфронт = ½·P₀·tрамп", "= ½·C·Vin²"],
                   size=12.5, color=FIELD, anchor="middle", bold=True))
    f.append(text(240, 470, "Vds спадає, поки Vout росте →", size=12, color=MUTED, anchor="middle"))
    f.append(text(240, 490, "потужність тане до нуля.", size=12, color=MUTED, anchor="middle"))
    f.append(text(240, 516, "Джоулі задані ЛИШЕ C і Vin.", size=12.5, color=FIELD,
                  anchor="middle", bold=True))

    # ── панель B ──
    f.append(arrow(axB, oy, 950, oy, color=INK, sw=1.8))
    f.append(arrow(axB, oy, axB, axTop, color=INK, sw=1.8))
    f.append(text(950, oy + 20, "час", size=12, color=INK, anchor="end"))
    # прямокутник
    f.append(polyfill([(axB, P0y), (endB, P0y), (endB, oy), (axB, oy)], POS, POS, sw=2.6, op=0.13))
    f.append(line(endB, oy, endB, oy + 8, color=POS, sw=1.8))
    f.append(text(endB, oy + 26, "tтаймер", size=12, color=POS, anchor="middle"))
    f.append(mtext(732, 292, ["Eаварія = P₀ · tтаймер"],
                   size=12.5, color=POS, anchor="middle", bold=True))
    f.append(text(730, 470, "Vout лишається 0 → Vds = Vin,", size=12, color=MUTED, anchor="middle"))
    f.append(text(730, 490, "струм тримається на межі.", size=12, color=MUTED, anchor="middle"))
    f.append(text(730, 516, "Джоулі задає ТАЙМЕР, не C.", size=12.5, color=POS,
                  anchor="middle", bold=True))

    render(os.path.join(IMG, "inrush-power-energy.svg"), W, H, *f,
           title="Потужність на ключі: чесний фронт проти аварії")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 (math-inrush-soa) — сім'я кривих SOA: кожна лінія = стала потужність
# ΔT/Zθ(t); нестійкість Спіріто зрізає верх; робоча точка hot-swap
# ─────────────────────────────────────────────────────────────────────────────
def fig_soa_family():
    W, H = 1020, 545
    f = []

    # логарифмічні осі, однакова декада 170 px
    X0, Y0, DEC = 150.0, 440.0, 170.0     # x(1 В) = 150, y(0.1 А) = 440

    def X(v):
        return X0 + DEC * math.log10(v)

    def Y(i):
        return Y0 - DEC * (math.log10(i) + 1.0)

    # осі
    f.append(arrow(X0, Y0, 500, Y0, color=INK, sw=1.8))
    f.append(arrow(X0, Y0, X0, 85, color=INK, sw=1.8))
    f.append(text(250, 492, "Vds, В (логарифм)", size=12.5, color=INK, anchor="middle"))
    f.append(text(150, 72, "Id, А (логарифм)", size=12.5, color=INK, anchor="middle"))
    for v in (1, 10, 100):
        f.append(line(X(v), Y0, X(v), Y0 + 6, color=INK, sw=1.5))
        f.append(text(X(v), Y0 + 22, str(v), size=11.5, color=MUTED, anchor="middle"))
    for i, lab in ((0.1, "0.1"), (1, "1"), (10, "10")):
        f.append(line(X0 - 6, Y(i), X0, Y(i), color=INK, sw=1.5))
        f.append(text(X0 - 12, Y(i) + 4, lab, size=11.5, color=MUTED, anchor="end"))

    # лінії сталої потужності: Zθ ∝ √t → декада часу = ÷3.16 потужності
    def pline(P, lab, laby):
        pts = []
        for v in (1.0, 3.0, 10.0, 30.0, 100.0):
            i = P / v
            if 0.1 <= i <= 10.0:
                pts.append((X(v), Y(i)))
        # доточити кінці рівно по межах вікна
        if P / 1.0 > 10.0:
            pts.insert(0, (X(P / 10.0), Y(10.0)))
        if P / 100.0 < 0.1:
            pts.append((X(P / 0.1), Y(0.1)))
        f.append(poly(pts, color=NEG, sw=2.6))
        f.append(text(laby[0], laby[1], lab, size=12.5, color=NEG, anchor="start", bold=True))

    pline(100.0, "100 мкс", (508, 268))
    pline(30.0, "1 мс", (508, 357))
    pline(10.0, "10 мс", (508, 434))
    f.append(text(407, 424, "DC", size=12.5, color=NEG, anchor="start", bold=True))
    pts = [(X(1.0), Y(3.0)), (X(30.0), Y(0.1))]
    f.append(poly(pts, color=NEG, sw=2.6))

    # Спіріто: справжня межа 10 мс відламується від 10-Вт лінії при Vds ≈ 5 В
    sp = [(X(5.0), Y(2.0)), (X(9.0), Y(0.75)), (X(14.0), Y(0.30)), (X(20.0), Y(0.125))]
    f.append(poly(sp, color=POS, sw=3.0, dash="7 5"))

    # робоча точка hot-swap: Vds = 20 В, Id = 0.3 А
    f.append(circle(X(20.0), Y(0.3), 7, fill="#ffffff", stroke=POS, sw=3))
    f.append(circle(X(20.0), Y(0.3), 3, fill=POS, stroke=POS, sw=1))
    f.append(mtext(232, 392, ["робоча точка:", "Vds = Vin, Id = Iмежа"],
                   size=11, color=POS, anchor="middle", bold=True))
    f.append(arrow(316, 388, 362, 362, color=POS, sw=1.6))

    # пояснювальні рамки праворуч
    f.append(box(765, 182, "Кожна лінія — СТАЛА потужність:\n"
                           "Id · Vds = (Tj max − Tc) / Zθ(t)\n"
                           "\n"
                           "коротший імпульс → менше Zθ(t)\n"
                           "→ вища дозволена потужність\n"
                           "→ лінія стоїть вище\n"
                           "\n"
                           "У логарифмічних осях стала\n"
                           "потужність — пряма з нахилом −1.",
                 size=12.5, min_w=250))
    f.append(box(765, 400, "Червоний пунктир — СПРАВЖНЯ межа.\n"
                           "\n"
                           "Нестійкість Спіріто зрізає верх\n"
                           "кривої на високих Vds — і тим\n"
                           "раніше, чим довший імпульс.\n"
                           "\n"
                           "Робоча точка лежить НИЖЧЕ суцільної\n"
                           "«10 мс» (теплова формула обіцяє запас),\n"
                           "але ВИЩЕ пунктиру — запасу немає.",
                 size=12, min_w=250, fill="#fff5f5", stroke=POS))

    render(os.path.join(IMG, "soa-curve-family.svg"), W, H, *f,
           title="Крива SOA — це крива Zθ, перемальована в інші осі")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 6 (math-inrush-soa) — точка ZTC: де темпкоеф струму міняє знак
# ─────────────────────────────────────────────────────────────────────────────
def fig_ztc():
    W, H = 1000, 540
    f = []

    X0, Y0 = 140.0, 440.0
    KX, KY = 92.0, 5.4        # px на вольт Vgs / px на ампер Id

    def X(v):
        return X0 + (v - 2.0) * KX

    def Y(i):
        return Y0 - i * KY

    def curve(vth, k, vmax=7.0, steps=60):
        pts = [(X(2.0), Y(0.0)), (X(vth), Y(0.0))]
        for s in range(steps + 1):
            v = vth + (vmax - vth) * s / steps
            pts.append((X(v), Y(k * (v - vth) ** 2)))
        return pts

    # осі
    f.append(arrow(X0, Y0, 620, Y0, color=INK, sw=1.8))
    f.append(arrow(X0, Y0, X0, 100, color=INK, sw=1.8))
    f.append(text(380, 492, "Vgs, В", size=13, color=INK, anchor="middle"))
    f.append(text(140, 86, "Id, А", size=13, color=INK, anchor="middle"))
    for v in (3, 4, 5, 6, 7):
        f.append(line(X(v), Y0, X(v), Y0 + 6, color=INK, sw=1.4))
        f.append(text(X(v), Y0 + 22, str(v), size=11.5, color=MUTED, anchor="middle"))

    # дві передавальні криві
    f.append(poly(curve(4.0, 6.67), color=NEG, sw=2.8))
    f.append(poly(curve(3.4, 3.67), color=POS, sw=2.8))
    f.append(text(592, 122, "25 °C", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(592, 190, "175 °C", size=13, color=POS, anchor="start", bold=True))

    # точка ZTC: 6.67·(V−4)² = 3.67·(V−3.4)² → V ≈ 5.73, Id ≈ 20 А
    ztcV, ztcI = 5.73, 20.0
    f.append(line(X0, Y(ztcI), X(ztcV), Y(ztcI), color=MUTED, sw=1.3, dash="4 5"))
    f.append(circle(X(ztcV), Y(ztcI), 7, fill="#ffffff", stroke=INK, sw=2.6))
    f.append(text(X0 - 10, Y(ztcI) + 4, "ZTC", size=11.5, color=MUTED, anchor="end"))

    f.append(box(790, 168, "ВИЩЕ точки ZTC\n"
                           "рухливість перемагає:\n"
                           "гарячіша комірка бере\n"
                           "МЕНШЕ струму.\n"
                           "Від'ємний зв'язок —\n"
                           "струм сам вирівнюється.",
                 size=12, min_w=210, fill="#eef7f0", stroke=FIELD))
    f.append(box(790, 392, "НИЖЧЕ точки ZTC\n"
                           "поріг Vth перемагає:\n"
                           "гарячіша комірка бере\n"
                           "БІЛЬШЕ струму, гріється\n"
                           "ще дужче — і забирає\n"
                           "струм у сусідів.",
                 size=12, min_w=210, fill="#fff5f5", stroke=POS))

    f.append(mtext(232, 232, ["тут працює hot-swap:", "Vgs ледь над порогом,",
                              "струм малий → зона", "нестійкості Спіріто"],
                   size=11.5, color=POS, anchor="middle", bold=True))
    f.append(arrow(232, 285, 300, 412, color=POS, sw=1.6))

    render(os.path.join(IMG, "ztc-crossover.svg"), W, H, *f,
           title="Точка ZTC: де темпкоефіцієнт струму міняє знак")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 7 (math-inrush-soa) — некерований кидок як розв'язок RLC: три режими
# загасання; V/R і V/Z₀ — це дві РІЗНІ стелі, справжній пік нижчий за обидві
# ─────────────────────────────────────────────────────────────────────────────
def fig_rlc_inrush():
    W, H = 1020, 570
    f = []

    V, C, R = 12.0, 1000e-6, 0.020
    PX0, PX1 = 118.0, 610.0
    PY0, PY1 = 486.0, 108.0
    TMAX, IMAX = 60e-6, 700.0

    def X(t):
        return PX0 + (t / TMAX) * (PX1 - PX0)

    def Y(i):
        return PY0 - (i / IMAX) * (PY0 - PY1)

    def curve(L, N=3200, step=8):
        """RK4 по колу V = L·di/dt + R·i + vc; повертає точки, пік і його час."""
        dt = TMAX / N
        i = vc = 0.0
        ip = tp = 0.0
        pts = []

        def fn(i, vc):
            return ((V - vc - R * i) / L, i / C)

        for n in range(N + 1):
            if n % step == 0:
                pts.append((X(n * dt), Y(i if i > 0 else 0.0)))
            k1 = fn(i, vc)
            k2 = fn(i + dt / 2 * k1[0], vc + dt / 2 * k1[1])
            k3 = fn(i + dt / 2 * k2[0], vc + dt / 2 * k2[1])
            k4 = fn(i + dt * k3[0], vc + dt * k3[1])
            i += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            vc += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            if i > ip:
                ip, tp = i, (n + 1) * dt
        return pts, ip, tp

    # осі
    f.append(arrow(PX0, PY0, PX1 + 34, PY0, color=INK, sw=1.8))
    f.append(arrow(PX0, PY0, PX0, PY1 - 22, color=INK, sw=1.8))
    f.append(text(364, PY0 + 44, "час від дотику контактів, мкс", size=12.5, color=INK))
    f.append(text(PX0 + 6, PY1 - 32, "струм крізь контакти, А", size=12.5, color=INK,
                  anchor="start"))
    for t_us in (0, 10, 20, 30, 40, 50, 60):
        x = X(t_us * 1e-6)
        f.append(line(x, PY0, x, PY0 + 6, color=INK, sw=1.5))
        f.append(text(x, PY0 + 22, str(t_us), size=11.5, color=MUTED))
    for a in (0, 200, 400, 600):
        y = Y(a)
        f.append(line(PX0 - 6, y, PX0, y, color=INK, sw=1.5))
        f.append(text(PX0 - 12, y + 4, str(a), size=11.5, color=MUTED, anchor="end"))

    # стеля опору V/R = 600 А
    f.append(line(PX0, Y(600), PX1 + 24, Y(600), color=MUTED, sw=1.6, dash="6 5"))
    f.append(text(PX1 + 24, Y(600) - 10, "стеля опору  V/R = 600 А", size=12,
                  color=MUTED, anchor="end"))

    # три режими загасання
    specs = [(20e-9, POS, "20"), (100e-9, INK, "100"), (500e-9, NEG, "500")]
    peaks = []
    for L, col, _lab in specs:
        pts, ip, tp = curve(L)
        f.append(poly(pts, color=col, sw=2.8))
        f.append(circle(X(tp), Y(ip), 5, fill="#ffffff", stroke=col, sw=2.4))
        peaks.append((L, col, ip, tp))

    # легенда — окремою колонкою, щоб написи не лізли на криві
    lx, ly = 668.0, 132.0
    f.append(text(lx, ly - 26, "Одна й та сама плата, різна паразитна L:",
                  size=12.5, color=INK, anchor="start", bold=True))
    for k, (L, col, ip, tp) in enumerate(peaks):
        yy = ly + k * 30
        z = (R / 2) * math.sqrt(C / L)
        f.append(line(lx, yy, lx + 30, yy, color=col, sw=3.0))
        f.append(text(lx + 40, yy + 4.5,
                      "L = %d нГн · ζ = %.2f · пік %.0f А" % (L * 1e9, z, ip),
                      size=12, color=col, anchor="start"))

    f.append(box(838, 300, "Дві стелі — і ЖОДНА не є відповіддю:\n"
                           "\n"
                           "V/R    = 600 А   (стеля опору)\n"
                           "V/Z₀  = 1200 А  (стеля індуктивності,\n"
                           "                        Z₀ = √(L/C) при 100 нГн)\n"
                           "\n"
                           "Справжній пік — 441 А — нижчий\n"
                           "за обидві: індуктивність не пускає\n"
                           "струм рости миттєво, а поки він\n"
                           "росте, банк устигає підзарядитися.",
                 size=12, min_w=300))

    f.append(box(838, 472, "Більша L зрізає пік — але дзвонить:\n"
                           "при 500 нГн напруга на банку злітає\n"
                           "до 14.5 В, вище за шину 12 В.",
                 size=12, min_w=300, fill="#eaf0fd", stroke=NEG))

    render(os.path.join(IMG, "rlc-inrush.svg"), W, H, *f,
           title="Некерований кидок: не «V/R», а розв'язок RLC")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (comp-hotswap-controller) — що напхано в корпус контролера
# ─────────────────────────────────────────────────────────────────────────────
def fig_ctrl_block():
    W, H = 1140, 700
    f = []
    PX0, PY0, PX1, PY1 = 180, 88, 960, 648

    f.append(rect(PX0, PY0, PX1 - PX0, PY1 - PY0, fill="#ffffff", stroke=INK, sw=2.2, rx=12))
    f.append(text(PX1 - 20, 112, "контролер hot-swap", size=12.5, color=MUTED, anchor="end"))

    # смуги-пояси
    for ys in (236, 404):
        f.append(line(PX0, ys, PX1, ys, color=MUTED, sw=1.2, dash="6 6"))
    f.append(text(192, 112, "керування затвором", size=11.5, color=MUTED, anchor="start"))
    f.append(text(192, 260, "вимірювання струму", size=11.5, color=MUTED, anchor="start"))
    f.append(text(192, 428, "нагляд і рішення", size=11.5, color=MUTED, anchor="start"))

    def pin_l(y, name):
        return (line(110, y, PX0, y, color=INK, sw=2) +
                text(104, y + 4, name, size=12, color=INK, anchor="end"))

    def pin_r(y, name):
        return (line(PX1, y, 1030, y, color=INK, sw=2) +
                text(1036, y + 4, name, size=12, color=INK, anchor="start"))

    # ── пояс 1: затвор ──
    f.append(box(420, 180, "зарядова помпа:\nтягне затвор ВИЩЕ входу", size=12.5, min_w=310))
    f.append(box(790, 180, "джерело струму Iпідйом ≈ 20 мкА\nі сильний стік на скидання",
                 size=12.5, min_w=290))
    f.append(arrow(575, 180, 643, 180, color=INK, sw=1.8))
    f.append(pin_l(180, "VCC"))
    f.append(line(PX0, 180, 263, 180, color=INK, sw=2))
    f.append(pin_r(180, "GATE"))
    f.append(line(935, 180, PX1, 180, color=INK, sw=2))

    # ── пояс 2: струм ──
    f.append(box(420, 300, "підсилювач обмеження струму:\nтримає Uш на порозі Uпор",
                 size=12.5, min_w=310))
    f.append(box(420, 368, "швидкий компаратор:\nUш ≫ Uпор → миттєве скидання",
                 size=12.5, min_w=310))
    f.append(pin_l(300, "SENSE"))
    f.append(line(PX0, 300, 263, 300, color=POS, sw=2))
    f.append(circle(230, 300, 4, fill=POS, stroke=POS))
    f.append(line(230, 300, 230, 368, color=POS, sw=2))
    f.append(line(230, 368, 263, 368, color=POS, sw=2))
    # обидва тягнуть затвор
    f.append(arrow(577, 292, 700, 207, color=INK, sw=1.7))
    f.append(arrow(577, 360, 760, 207, color=POS, sw=1.7))

    # ── пояс 3: нагляд ──
    f.append(box(420, 470, "таймер: Iт заряджає Cт,\nпоки триває обмеження", size=12.5, min_w=310))
    f.append(box(790, 470, "логіка: засувка\nабо автоповтор", size=12.5, min_w=290))
    f.append(box(420, 570, "компаратори UV / OV:\nдозвіл на старт", size=12.5, min_w=310))
    f.append(box(790, 570, "компаратор PG:\nвихід дійшов до норми", size=12.5, min_w=290))
    f.append(arrow(577, 470, 643, 470, color=INK, sw=1.7))
    f.append(arrow(577, 560, 643, 492, color=INK, sw=1.7))
    f.append(arrow(790, 443, 790, 207, color=INK, sw=1.7))

    f.append(pin_l(470, "TIMER"))
    f.append(line(PX0, 470, 263, 470, color=INK, sw=2))
    f.append(pin_l(560, "UV"))
    f.append(line(PX0, 560, 263, 560, color=NEG, sw=2))
    f.append(pin_l(580, "OV"))
    f.append(line(PX0, 580, 263, 580, color=NEG, sw=2))
    f.append(pin_r(570, "PG"))
    f.append(line(935, 570, PX1, 570, color=INK, sw=2))
    f.append(pin_r(620, "OUT"))
    f.append(line(PX1, 620, 790, 620, color=INK, sw=2))
    f.append(arrow(790, 620, 790, 597, color=INK, sw=1.7))

    # земля контролера
    f.append(line(300, PY1, 300, 652, color=INK, sw=2))
    f.append(gnd(300, 652))
    f.append(text(300, 692, "GND", size=12, color=INK, anchor="middle"))

    render(os.path.join(IMG, "hotswap-block.svg"), W, H, *f,
           title="Що напхано в корпус контролера hot-swap")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (comp-hotswap-controller) — обв'язка: що навісити зовні
# ─────────────────────────────────────────────────────────────────────────────
def fig_ctrl_hookup():
    W, H = 1200, 720
    f = []
    railY = 120

    # ── силовий шлях ──
    f.append(text(60, 96, "+Vin (жива шина)", size=13, color=POS, anchor="start", bold=True))
    f.append(line(60, railY, 170, railY, color=POS, sw=3.2))
    f.append(rect(170, railY - 18, 76, 36, fill="#fff5f5", stroke=POS, sw=1.8))
    f.append(text(208, railY + 5, "Rш", size=13, color=POS, bold=True))
    f.append(line(246, railY, 375, railY, color=POS, sw=3.2))
    f.append(box(440, railY, "MOSFET", size=13, min_w=130))
    f.append(line(505, railY, 640, railY, color=POS, sw=3.2))
    f.append(circle(640, railY, 4, fill=INK, stroke=INK))
    f.append(text(640, 96, "Vout", size=12.5, color=POS, anchor="middle", bold=True))
    f.append(line(640, railY, 640, 164, color=INK, sw=2))
    f.append(cap(640, 185, lead=16, gap=10, plate=32))
    f.append(text(612, 190, "Cбулк", size=12, color=INK, anchor="end"))
    f.append(gnd(640, 206))
    f.append(line(640, railY, 765, railY, color=POS, sw=3.2))
    f.append(box(830, railY, "наван-\nтаження", size=12.5, min_w=130))

    # ── контролер ──
    f.append(rect(330, 330, 400, 250, fill=FILL, stroke=INK, sw=2.2, rx=10))
    f.append(text(530, 360, "контролер hot-swap", size=14, bold=True))
    for y, nm in ((400, "SENSE"), (440, "VIN"), (490, "UV"), (520, "OV")):
        f.append(text(340, y + 4, nm, size=12, color=INK, anchor="start"))
    for y, nm in ((400, "GATE"), (490, "TIMER"), (530, "PG")):
        f.append(text(720, y + 4, nm, size=12, color=INK, anchor="end"))
    f.append(text(530, 572, "GND", size=12, color=INK, anchor="middle"))
    f.append(line(530, 580, 530, 604, color=INK, sw=2))
    f.append(gnd(530, 604))

    # ── Кельвінова пара від шунта ──
    f.append(line(178, 138, 178, 440, color=POS, sw=1.6))     # VIN-трас
    f.append(line(178, 440, 330, 440, color=POS, sw=1.6))
    f.append(line(238, 138, 238, 286, color=POS, sw=1.6))     # SENSE-трас
    f.append(rect(224, 286, 28, 40, fill=FILL, stroke=POS, sw=1.5, rx=3))
    f.append(text(258, 310, "Rф", size=11, color=POS, anchor="start"))
    f.append(line(238, 326, 238, 400, color=POS, sw=1.6))
    f.append(line(238, 400, 330, 400, color=POS, sw=1.6))
    # RC-фільтр: конденсатор між трасами
    f.append(line(178, 370, 198, 370, color=POS, sw=1.4))
    f.append(line(198, 358, 198, 382, color=POS, sw=2))
    f.append(line(208, 358, 208, 382, color=POS, sw=2))
    f.append(line(208, 370, 238, 370, color=POS, sw=1.4))
    f.append(text(203, 350, "Cф", size=11, color=POS, anchor="middle"))
    f.append(mtext(252, 190, ["Кельвінова пара:", "окремі тонкі траси", "просто на п'ятачки", "шунта"],
                   size=11, color=POS, anchor="start"))

    # ── дільник UV / OV ──
    f.append(line(90, railY, 90, 300, color=NEG, sw=1.6))
    f.append(rect(76, 300, 28, 44, fill=FILL, stroke=NEG, sw=1.5, rx=3))
    f.append(line(90, 344, 90, 400, color=NEG, sw=1.6))
    f.append(rect(76, 400, 28, 44, fill=FILL, stroke=NEG, sw=1.5, rx=3))
    f.append(line(90, 444, 90, 500, color=NEG, sw=1.6))
    f.append(rect(76, 500, 28, 44, fill=FILL, stroke=NEG, sw=1.5, rx=3))
    f.append(line(90, 544, 90, 566, color=NEG, sw=1.6))
    f.append(gnd(90, 566))
    f.append(circle(90, 372, 3.5, fill=NEG, stroke=NEG))
    f.append(line(90, 372, 130, 372, color=NEG, sw=1.6))
    f.append(line(130, 372, 130, 520, color=NEG, sw=1.6))
    f.append(line(130, 520, 330, 520, color=NEG, sw=1.6))
    f.append(circle(90, 472, 3.5, fill=NEG, stroke=NEG))
    f.append(line(90, 472, 150, 472, color=NEG, sw=1.6))
    f.append(line(150, 472, 150, 490, color=NEG, sw=1.6))
    f.append(line(150, 490, 330, 490, color=NEG, sw=1.6))
    f.append(mtext(66, 380, ["дільник", "UV / OV:", "пороги", "старту"],
                   size=11, color=NEG, anchor="end"))

    # ── затвор ──
    f.append(line(730, 400, 800, 400, color=INK, sw=2))
    f.append(line(800, 400, 800, 250, color=INK, sw=2))
    f.append(line(800, 250, 440, 250, color=INK, sw=2))
    f.append(line(440, 250, 440, 137, color=INK, sw=2))
    f.append(text(560, 240, "затвор", size=11.5, color=INK, anchor="middle"))
    # Cзат
    f.append(circle(800, 330, 3.5, fill=INK, stroke=INK))
    f.append(line(800, 330, 860, 330, color=INK, sw=1.8))
    f.append(line(860, 330, 860, 339, color=INK, sw=1.8))
    f.append(cap(860, 360, lead=16, gap=10, plate=32))
    f.append(gnd(860, 381))
    f.append(mtext(895, 352, ["Cзат — задає", "швидкість фронту"],
                   size=11.5, color=INK, anchor="start"))

    # ── Cт ──
    f.append(line(730, 490, 790, 490, color=INK, sw=1.8))
    f.append(line(790, 490, 790, 499, color=INK, sw=1.8))
    f.append(cap(790, 520, lead=16, gap=10, plate=32))
    f.append(gnd(790, 541))
    f.append(mtext(825, 512, ["Cт — задає", "вікно аварії"],
                   size=11.5, color=INK, anchor="start"))

    # ── PG ──
    f.append(line(730, 530, 960, 530, color=INK, sw=1.8))
    f.append(circle(960, 530, 3.5, fill=INK, stroke=INK))
    f.append(rect(946, 450, 28, 44, fill=FILL, stroke=POS, sw=1.5, rx=3))
    f.append(line(960, 494, 960, 530, color=POS, sw=1.6))
    f.append(line(960, 450, 960, 424, color=POS, sw=1.6))
    f.append(text(960, 412, "+3.3 В", size=11.5, color=POS, anchor="middle"))
    f.append(text(982, 476, "Rпідт", size=11, color=POS, anchor="start"))
    f.append(arrow(960, 530, 1058, 530, color=INK, sw=1.8))
    f.append(text(1064, 534, "до процесора", size=11.5, color=INK, anchor="start"))

    # ── формула ──
    f.append(box(1030, 230, "dVout/dt = Iпідйом / Cзат\nIкид = Cбулк · Iпідйом / Cзат",
                 size=12, min_w=300, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(IMG, "hotswap-hookup.svg"), W, H, *f,
           title="Обв'язка контролера: що навісити зовні")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (comp-hotswap-controller) — три ешелони на трьох часових масштабах
# ─────────────────────────────────────────────────────────────────────────────
def fig_ctrl_tiers():
    import math
    W, H = 1160, 520
    f = []
    AX0, AX1, AY = 130.0, 1010.0, 380.0
    STEP = (AX1 - AX0) / 6.0          # декада

    def X(t_ns):
        return AX0 + (math.log10(t_ns) - 2.0) * STEP

    # тінь «поза SOA» — під усім
    f.append(rect(X(3e7), 215, 1040 - X(3e7), 165, fill="#fdecea", stroke="#fdecea", sw=0, rx=0))
    f.append(mtext(1050, 280, ["поза", "SOA"], size=12, color=POS, anchor="start", bold=True))

    # вісь часу
    f.append(arrow(AX0, AY, 1060, AY, color=INK, sw=1.8))
    f.append(text(1075, 384, "час", size=12, color=INK, anchor="start"))
    for i, lab in enumerate(("100 нс", "1 мкс", "10 мкс", "100 мкс", "1 мс", "10 мс", "100 мс")):
        x = AX0 + i * STEP
        f.append(line(x, AY - 5, x, AY + 5, color=INK, sw=1.6))
        f.append(text(x, 366, lab, size=11.5, color=MUTED, anchor="middle"))

    # ешелон 1 — швидкий компаратор
    f.append(rect(X(200), 108, X(400) - X(200), 26, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(230, 128, "швидкий компаратор бачить коротке: 200…400 нс",
                  size=12.5, color=POS, anchor="start", bold=True))

    # ешелон 2 — скидання затвора
    f.append(rect(X(1e4), 168, X(5e4) - X(1e4), 26, fill="#fff5f5", stroke=POS, sw=1.8, rx=4))
    f.append(text(538, 188, "а затвор ще треба РОЗРЯДИТИ: 10…50 мкс — увесь цей час струм тече",
                  size=12.5, color=POS, anchor="start"))

    # ешелон 3 — вікно таймера, затиснуте між фронтом і SOA
    f.append(rect(X(5e6), 238, X(3e7) - X(5e6), 26, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(X(5e6) - 12, 258, "вікно таймера мусить лягти СЮДИ",
                  size=12.5, color=FIELD, anchor="end", bold=True))

    # межі вікна
    f.append(line(X(5e6), 215, X(5e6), 400, color=FIELD, sw=2, dash="6 5"))
    f.append(mtext(X(5e6), 412, ["чесний фронт", "кінчається тут"],
                   size=11.5, color=FIELD, anchor="middle"))
    f.append(line(X(3e7), 215, X(3e7), 400, color=POS, sw=2, dash="6 5"))
    f.append(mtext(X(3e7), 452, ["межа SOA ключа", "за цієї потужності"],
                   size=11.5, color=POS, anchor="middle"))

    render(os.path.join(IMG, "hotswap-tiers.svg"), W, H, *f,
           title="Три ешелони захисту — три часові масштаби")


# ── історія (hist-live-insertion.md) ───────────────────────────────────────
def fig_hist_fabric_vs_bus():
    """Чому в електромеханічної станції задачі не було, а в електронної з'явилася."""
    W, H = 1180, 570
    f = []

    # ЛІВОРУЧ: розподілена електромеханіка
    f.append(rect(40, 60, 520, 470, fill=BG, stroke=MUTED, sw=1.6, rx=10))
    f.append(text(300, 94, "Реле й крокові шукачі", size=16, bold=True))
    f.append(text(300, 118, "шляхи незалежні один від одного", size=12, color=MUTED))

    for i, cx in enumerate([150, 300, 450]):
        dead = (i == 1)
        col = POS if dead else FIELD
        f.append(circle(cx, 168, 8, fill=FILL, stroke=MUTED, sw=1.5))
        f.append(circle(cx, 408, 8, fill=FILL, stroke=MUTED, sw=1.5))
        f.append(line(cx, 176, cx, 244, color=col, sw=2.4,
                      dash="7 5" if dead else None))
        if dead:
            f.append(line(cx, 326, cx, 400, color=col, sw=2.4, dash="7 5"))
            f.append(box(cx, 285, ["елемент", "make-busy"], size=12,
                         fill="#fdecea", stroke=POS, sw=2.2, color=POS, min_w=112))
        else:
            f.append(arrow(cx, 326, cx, 400, color=col, sw=2.4))
            f.append(box(cx, 285, ["елемент", "у роботі"], size=12,
                         fill=FILL, stroke=FIELD, sw=2.0, min_w=112))

    f.append(mtext(300, 460,
                   ["Позначив зайнятим — логіка веде виклики повз.",
                    "Витяг чує лише цей шлях: спільної шини",
                    "й спільного банку конденсаторів просто нема."],
                   size=12, color=INK, anchor="middle", lh=1.35))

    # ПРАВОРУЧ: спільна шина
    f.append(rect(620, 60, 520, 470, fill=BG, stroke=MUTED, sw=1.6, rx=10))
    f.append(text(880, 94, "Програмне керування", size=16, bold=True))
    f.append(text(880, 118, "живлення й шина — спільні на всіх", size=12, color=MUTED))

    f.append(line(668, 196, 1100, 196, color=POS, sw=3.0))
    f.append(text(660, 200, "+V", size=12, color=POS, anchor="end", bold=True))
    f.append(line(668, 432, 1100, 432, color=NEG, sw=3.0))
    f.append(text(660, 436, "шина", size=12, color=NEG, anchor="end", bold=True))

    for i, cx in enumerate([730, 840, 950, 1060]):
        out = (i == 2)
        if out:
            f.append(rect(cx - 38, 232, 76, 130, fill="#fdecea", stroke=POS, sw=2.2, rx=6))
            f.append(mtext(cx, 288, ["плату", "витяг-", "ають"], size=11.5, color=POS))
            f.append(arrow(cx, 226, cx, 156, color=POS, sw=2.2))
        else:
            f.append(rect(cx - 38, 252, 76, 130, fill=FILL, stroke=LINE, sw=1.6, rx=6))
            f.append(mtext(cx, 310, ["сусід", "працює"], size=11.5, color=INK))
            f.append(line(cx, 196, cx, 252, color=LINE, sw=1.8))
            f.append(line(cx, 382, cx, 432, color=LINE, sw=1.8))

    f.append(text(748, 178, "просадка живлення", size=12, color=POS, bold=True))
    f.append(text(760, 460, "сміття на шині", size=12, color=NEG, bold=True))
    f.append(mtext(880, 496,
                   ["Одна плата смикнула — відчули всі:",
                    "спільне живлення просіло, шина здригнулася."],
                   size=12, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "hist-fabric-vs-bus.svg"), W, H, *f,
           title="Що електроніка забрала: гаряча заміна з властивості стала задачею")


def fig_hist_descent():
    """Двадцять років задача сповзає вниз стеком: від усієї машини до одного корпусу."""
    W, H = 1200, 650
    f = []

    steps = [
        ("1965 · Bell Labs, 1ESS",
         "спільний процесор і дублювання: задача народжується",
         "рівень: архітектура машини"),
        ("1976 · Tandem/16",
         "усі плати від початку розраховані на гарячу вставку",
         "рівень: архітектура машини"),
        ("1986 · AT&T, патент 4835737",
         "автомат перехоплює шину й спиняє такт усієї машини",
         "рівень: система"),
        ("1993 · IBM, патент 5434752",
         "засувка тримає плату на півдорозі, поки та набирає заряд",
         "рівень: кошик і роз'єм"),
        ("1995 · 3Com, патент 5617081",
         "штирі різної довжини + послідовний MOSFET із плавним фронтом",
         "рівень: плата"),
        ("1997 · Linear Technology, LTC1421",
         "усе те саме — в одному корпусі, під назвою Hot Swap",
         "рівень: компонент"),
    ]

    # вісь «рівень»: згори вся машина, знизу один корпус
    f.append(mtext(72, 92, ["вся", "машина"], size=12, color=MUTED, bold=True))
    f.append(arrow(72, 126, 72, 566, color=MUTED, sw=2.0))
    f.append(mtext(72, 596, ["один", "корпус"], size=12, color=MUTED, bold=True))

    BW, BH = 500, 78
    for i, (who, what, lvl) in enumerate(steps):
        x = 170 + i * 92
        y = 88 + i * 90
        last = (i == len(steps) - 1)
        f.append(fitbox(x, y, BW, BH, [who, what, lvl], size=13,
                        pad=10, fill="#eef7f1" if last else FILL,
                        stroke=FIELD if last else LINE,
                        sw=2.2 if last else 1.6))
        if not last:
            f.append(arrow(x + 34, y + BH + 2, x + 92 + 34, y + 90 - 2,
                           color=MUTED, sw=2.0))

    render(os.path.join(IMG, "hist-descent.svg"), W, H, *f,
           title="Куди сповзала задача: від перебудови машини до однієї мікросхеми")


if __name__ == "__main__":
    fig_live_bus()
    fig_pins()
    fig_ramp()
    fig_power_energy()
    fig_soa_family()
    fig_ztc()
    fig_rlc_inrush()
    fig_ctrl_block()
    fig_ctrl_hookup()
    fig_ctrl_tiers()
    fig_hist_fabric_vs_bus()
    fig_hist_descent()
    print("figs OK")
