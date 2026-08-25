# -*- coding: utf-8 -*-
"""Фігури до теми «Третій закон Ньютона».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: пара сил — при дотику й при тяжінні на відстані ──────────────────
def fig_action_reaction():
    W, H = 900, 448
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Сила завжди у парі: рівна, протилежна, на два різні тіла",
                  size=17, bold=True))
    f.append(line(452, 70, 452, 348, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: дотик ──
    f.append(text(228, 82, "Дотик", size=15, bold=True, color=INK))
    cy = 214
    f.append(rect(150, cy - 32, 78, 64, fill="#eef2fb", stroke=INK, sw=2, rx=6))
    f.append(rect(228, cy - 32, 78, 64, fill="#eef2fb", stroke=INK, sw=2, rx=6))
    f.append(text(189, cy + 7, "A", size=20, bold=True, color=INK))
    f.append(text(267, cy + 7, "B", size=20, bold=True, color=INK))
    ay = cy - 58
    f.append(arrow(233, ay, 340, ay, color=POS, sw=3.4))
    f.append(text(346, ay + 5, "сила на B", size=13, bold=True, color=POS, anchor="start"))
    f.append(arrow(223, ay, 116, ay, color=NEG, sw=3.4))
    f.append(text(110, ay + 5, "сила на A", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(228, cy + 66, "A штовхає B  ·  B штовхає A", size=12, color=MUTED))
    f.append(text(228, cy + 86, "стрілки однакові за довжиною", size=12, color=MUTED))

    # ── права панель: тяжіння на відстані ──
    f.append(text(676, 82, "Тяжіння на відстані", size=15, bold=True, color=INK))
    ey = 214
    ex, mx = 620, 800
    f.append(circle(ex, ey, 40, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(ex, ey + 5, "Земля", size=13, bold=True, color=INK))
    f.append(circle(mx, ey, 16, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(mx, ey - 26, "Місяць", size=12, bold=True, color=INK))
    # сила на Місяць (до Землі) — вище лінії, вліво
    f.append(arrow(mx - 18, ey - 22, mx - 18 - 90, ey - 22, color=NEG, sw=3.4))
    f.append(text(mx - 18 - 45, ey - 32, "на Місяць", size=12, bold=True, color=NEG))
    # сила на Землю (до Місяця) — нижче лінії, вправо
    f.append(arrow(ex + 42, ey + 22, ex + 42 + 90, ey + 22, color=POS, sw=3.4))
    f.append(text(ex + 42 + 45, ey + 40, "на Землю", size=12, bold=True, color=POS))

    b, w, h = textbox(W / 2, H - 40,
                      "F(A→B) = − F(B→A):  однакова величина, протилежний напрям, одна пряма",
                      size=14, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "action-reaction.svg"), W, H, *f)


# ── Фігура 2: чому пара не гаситься (різні тіла vs одне тіло) ──────────────────
def fig_different_bodies():
    W, H = 920, 484
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Чому пара дія-протидія не гаситься", size=17, bold=True))
    f.append(line(462, 70, 462, 384, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: пара на різні тіла ──
    f.append(text(232, 82, "Пара — на РІЗНІ тіла: не гаситься", size=14, bold=True, color=INK))
    cy = 214
    f.append(rect(150, cy - 30, 74, 60, fill="#eef2fb", stroke=INK, sw=2, rx=6))
    f.append(rect(224, cy - 30, 74, 60, fill="#eef2fb", stroke=INK, sw=2, rx=6))
    f.append(text(187, cy + 6, "A", size=19, bold=True, color=INK))
    f.append(text(261, cy + 6, "B", size=19, bold=True, color=INK))
    ay = cy - 54
    f.append(arrow(229, ay, 330, ay, color=POS, sw=3.2))
    f.append(text(336, ay + 5, "сила на B", size=12, bold=True, color=POS, anchor="start"))
    f.append(arrow(219, ay, 118, ay, color=NEG, sw=3.2))
    f.append(text(112, ay + 5, "сила на A", size=12, bold=True, color=NEG, anchor="end"))
    by = cy + 52
    f.append(arrow(261, by, 331, by, color=FIELD, sw=3.2))
    f.append(text(337, by + 5, "a — B рушає", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(232, cy + 92, "рух B: сумуємо лише сили на B", size=12, color=MUTED))

    # ── права панель: сили на одному тілі ──
    f.append(text(700, 82, "Сили на ОДНОМУ тілі: гасяться", size=14, bold=True, color=INK))
    tx, tcy = 700, 224
    bw, bh = 104, 46
    f.append(rect(tx - bw / 2, tcy - bh / 2, bw, bh, fill="#ffffff", stroke=INK, sw=2, rx=6))
    f.append(text(tx, tcy + 5, "книжка", size=13, bold=True, color=INK))
    gy = 330
    f.append(line(tx - 82, gy, tx + 82, gy, color=MUTED, sw=2.5))
    # опора N — угору від верху книжки
    f.append(arrow(tx, tcy - bh / 2, tx, tcy - bh / 2 - 78, color=NEG, sw=3.2))
    f.append(text(tx + 10, tcy - bh / 2 - 70, "опора N", size=12, bold=True, color=NEG, anchor="start"))
    # вага W — униз від низу книжки до опори
    f.append(arrow(tx, tcy + bh / 2, tx, gy - 4, color=POS, sw=3.2))
    f.append(text(tx + 10, gy - 16, "вага W", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(tx, gy + 30, "W + N = 0 → книжка спокійна", size=13, bold=True, color=INK))

    b, w, h = textbox(W / 2, H - 36,
                      "Скасовуються лише сили на ОДНОМУ тілі; пара дія-протидія — завжди на двох різних",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "different-bodies.svg"), W, H, *f)


# ── Фігура 3: відкіт — рівна сила, різний рух, нульова сумарна кількість руху ──
def fig_recoil():
    W, H = 880, 472
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32,
                  "Постріл: рівна сила обом — та легша куля летить, важка гармата ледь відходить",
                  size=15, bold=True))
    cy = 200
    cnx, cnw, cnh = 210, 180, 84
    f.append(rect(cnx, cy - cnh / 2, cnw, cnh, fill="#eef2fb", stroke=INK, sw=2, rx=8))
    f.append(text(cnx + cnw / 2, cy + 6, "M = 800 кг", size=16, bold=True, color=INK))
    f.append(rect(cnx + cnw, cy - 16, 40, 32, fill="#eef2fb", stroke=INK, sw=2, rx=4))
    ballx = cnx + cnw + 70
    f.append(circle(ballx, cy, 17, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(ballx, cy - 28, "m = 4 кг", size=14, bold=True, color=INK))

    # рівні сили (під час пострілу)
    fy = cy - 58
    flen = 86
    f.append(arrow(ballx - 2, fy, ballx - 2 + flen, fy, color=POS, sw=3.4))
    f.append(text(ballx - 2 + flen + 8, fy + 5, "сила на кулю", size=12, bold=True, color=POS, anchor="start"))
    f.append(arrow(cnx + 40, fy, cnx + 40 - flen, fy, color=NEG, sw=3.4))
    f.append(text(cnx + 40 - flen - 8, fy + 5, "сила на гармату", size=12, bold=True, color=NEG, anchor="end"))
    f.append(text((cnx + 40 + ballx) / 2, fy - 14, "сили рівні", size=12, color=MUTED))

    # швидкості (довжина ∝ швидкості)
    vy = cy + 62
    f.append(arrow(ballx + 4, vy, ballx + 4 + 210, vy, color=FIELD, sw=3.4))
    f.append(text(ballx + 4 + 210 + 8, vy + 5, "v = 400 м/с", size=14, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(cnx + 30, vy, cnx + 30 - 26, vy, color=FIELD, sw=3.4))
    f.append(text(cnx + 30 - 32, vy + 5, "V = 2 м/с", size=13, bold=True, color=FIELD, anchor="end"))

    b, w, h = textbox(W / 2, 362,
                      "Рівна сила ⟹ рівна кількість руху:  m·v = M·V = 1600 кг·м/с",
                      size=15, pad=10, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    b2, w2, h2 = textbox(W / 2, 430,
                         "уперед 1600 + назад 1600 = 0 — стільки ж, скільки до пострілу",
                         size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "recoil.svg"), W, H, *f)


# ── Фігура 4 (історія): Декартова хиба — величина руху без напряму ────────────
def fig_descartes_ledger():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Хиба Декарта: величина руху без напряму", size=17, bold=True))

    # стіна праворуч
    f.append(rect(636, 78, 22, 168, fill="#e5e7eb", stroke=INK, sw=2, rx=3))
    for hy in range(88, 240, 20):
        f.append(line(636, hy, 658, hy - 14, color=MUTED, sw=1))
    f.append(text(647, 262, "стіна", size=12, color=MUTED))

    # рядок «до удару»: куля йде праворуч, до стіни
    f.append(text(48, 128, "до удару", size=13, bold=True, color=INK, anchor="start"))
    f.append(circle(400, 128, 18, fill="#eef2fb", stroke=INK, sw=2))
    f.append(arrow(422, 128, 600, 128, color=POS, sw=3.4))
    f.append(text(500, 112, "+v (управо)", size=13, bold=True, color=POS))

    # рядок «після удару»: куля відскочила, іде ліворуч
    f.append(text(48, 208, "після удару", size=13, bold=True, color=INK, anchor="start"))
    f.append(circle(400, 208, 18, fill="#eef2fb", stroke=INK, sw=2))
    f.append(arrow(378, 208, 200, 208, color=NEG, sw=3.4))
    f.append(text(300, 192, "−v (уліво)", size=13, bold=True, color=NEG))

    f.append(text(W / 2, 286, "Та сама швидкість, протилежний бік — насправді геть інший стан руху.",
                  size=13, color=MUTED))
    f.append(line(40, 304, 900, 304, color=MUTED, sw=1.2, dash="4 6"))

    # ── дві лічби ──
    f.append(rect(40, 322, 418, 154, fill="#fdf2f0", stroke=POS, sw=1.6, rx=8))
    f.append(text(60, 350, "Рахунок Декарта — лише |m·v|", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(60, 384, "до удару:     m·v", size=14, color=INK, anchor="start"))
    f.append(text(60, 412, "після удару:  m·v   (та сама величина)", size=14, color=INK, anchor="start"))
    f.append(text(60, 452, "⇒ «зміни немає» — а зміна ж очевидна", size=13.5, bold=True, color=POS, anchor="start"))

    f.append(rect(482, 322, 418, 154, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(502, 350, "Векторний рахунок — m·v із напрямом", size=14, bold=True, color=FIELD, anchor="start"))
    f.append(text(502, 384, "до удару:     + m·v", size=14, color=INK, anchor="start"))
    f.append(text(502, 412, "після удару:  − m·v", size=14, color=INK, anchor="start"))
    f.append(text(502, 452, "⇒ зміна = 2·m·v — стіна дала поштовх", size=13.5, bold=True, color=FIELD, anchor="start"))
    return render(os.path.join(IMG, "descartes-ledger.svg"), W, H, *f)


# ── Фігура 5 (історія): здогад Гюйгенса — один удар, два погляди ──────────────
def fig_huygens_boat():
    W, H = 980, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Здогад Гюйгенса: один удар — два погляди", size=17, bold=True))
    f.append(line(496, 66, 496, 520, color=MUTED, sw=1.1, dash="4 6"))
    f.append(text(258, 60, "до удару", size=12, color=MUTED))
    f.append(text(730, 60, "після удару", size=12, color=MUTED))

    def ball(cx, cy, lab):
        return circle(cx, cy, 15, fill="#eef2fb", stroke=INK, sw=2) + \
               text(cx, cy + 5, lab, size=12, bold=True, color=INK)

    # ── Панель А: на човні (симетрично) ──
    f.append(text(60, 96, "На човні: рух самого човна не рахуємо", size=14, bold=True, color=INK, anchor="start"))
    ay = 180
    f.append(ball(160, ay, "A")); f.append(arrow(178, ay - 30, 262, ay - 30, color=POS, sw=3.2))
    f.append(text(220, ay - 44, "+u", size=13, bold=True, color=POS))
    f.append(ball(372, ay, "B")); f.append(arrow(354, ay - 30, 270, ay - 30, color=NEG, sw=3.2))
    f.append(text(312, ay - 44, "−u", size=13, bold=True, color=NEG))
    f.append(ball(576, ay, "A")); f.append(arrow(558, ay - 30, 474, ay - 30, color=NEG, sw=3.2))
    f.append(text(516, ay - 44, "−u", size=13, bold=True, color=NEG))
    f.append(ball(792, ay, "B")); f.append(arrow(810, ay - 30, 894, ay - 30, color=POS, sw=3.2))
    f.append(text(852, ay - 44, "+u", size=13, bold=True, color=POS))
    f.append(text(278, 244, "симетрія очевидна: кожна відскакує з тією ж швидкістю u", size=12, color=MUTED))

    f.append(line(40, 286, 940, 286, color=MUTED, sw=1.1))

    # ── Панель Б: з берега (додається хід човна v) ──
    f.append(text(60, 328, "З берега: до всього додається хід човна  v →", size=14, bold=True, color=INK, anchor="start"))
    by = 418
    f.append(line(52, 456, 940, 456, color=MUTED, sw=2))
    for gx in range(60, 936, 26):
        f.append(line(gx, 456, gx - 8, 466, color=MUTED, sw=1))
    f.append(ball(150, by, "A")); f.append(arrow(168, by - 30, 300, by - 30, color=POS, sw=3.2))
    f.append(text(234, by - 44, "v+u", size=13, bold=True, color=POS))
    f.append(ball(372, by, "B")); f.append(arrow(390, by - 30, 452, by - 30, color=POS, sw=3.2))
    f.append(text(421, by - 44, "v−u", size=13, bold=True, color=POS))
    f.append(ball(576, by, "A")); f.append(arrow(594, by - 30, 656, by - 30, color=POS, sw=3.2))
    f.append(text(625, by - 44, "v−u", size=13, bold=True, color=POS))
    f.append(ball(792, by, "B")); f.append(arrow(810, by - 30, 918, by - 30, color=POS, sw=3.2))
    f.append(text(864, by - 44, "v+u", size=13, bold=True, color=POS))
    f.append(text(300, 494, "той самий удар — лише інша мірка швидкостей", size=12, color=MUTED))

    b, w, h = textbox(W / 2, 536,
                      "Правила збігаються, тільки якщо стежити за напрямом: скасуй його — і два погляди почнуть суперечити",
                      size=13.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "huygens-boat.svg"), W, H, *f)


# ── Фігура 6 (історія): часова стрічка — від Декарта до Ньютона ────────────────
def fig_collision_timeline():
    W, H = 980, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Від Декартової хиби до Ньютонового закону", size=17, bold=True))
    f.append(line(118, 70, 118, 560, color=MUTED, sw=2))

    rows = [
        ("1644", "Рене Декарт · Франція",
         "«Кількість руху» = маса·швидкість, без напряму. Сім правил удару — майже всі хибні.", POS),
        ("1656", "Крістіан Гюйгенс · Нідерланди",
         "Виводить правильні правила пружного удару з відносності руху; ховає рукопис на 12 років.", FIELD),
        ("1668·xi", "Джон Валліс · Англія",
         "Непружний удар через збереження кількості руху. Перший у друці — 15 листопада.", FIELD),
        ("1668·xii", "Крістофер Рен · Англія",
         "Пружний удар + дослід із маятниками перед Королівським товариством.", FIELD),
        ("1669", "Гюйгенс — у друці",
         "Оприлюднює пружні правила у Philosophical Transactions і Journal des Sçavans.", FIELD),
        ("1687", "Ісаак Ньютон · Англія",
         "Зводить усе в третій закон (actio = reactio); у Схолії віддає належне трьом.", NEG),
        ("1703", "«De motu corporum ex percussione»",
         "Головна праця Гюйгенса про удар виходить друком — уже посмертно.", MUTED),
    ]
    y = 96
    for year, head, desc, col in rows:
        f.append(circle(118, y, 8, fill=col, stroke=INK, sw=1.5))
        f.append(text(100, y + 5, year, size=13, bold=True, color=INK, anchor="end"))
        f.append(fitbox(150, y - 27, 800, 54, head + "\n" + desc,
                        size=14, pad=10, fill=FILL, stroke=col, sw=1.4, rx=8))
        y += 72
    return render(os.path.join(IMG, "collision-timeline.svg"), W, H, *f)


# ── Мінісимуляція (для фігур проєкту зі справжніми даними) ─────────────────────
def _sim(mode):
    """1D, контактний пружинний відпих; повертає (t, [p0,p1,p2], Ptot)."""
    m = [1.0, 3.0, 2.0]
    x = [0.0, 2.0, 5.0]
    v = [4.0, 0.0, -1.0]
    k, d0, dt, steps = 200.0, 1.0, 0.002, 1200
    ts, pind, Ptot = [], [[], [], []], []
    for s in range(steps):
        if mode == "pair":                       # пара-раз: +s тілу i, −s тілу j
            F = [0.0, 0.0, 0.0]
            for i in range(3):
                for j in range(i + 1, 3):
                    dx = x[i] - x[j]; r = abs(dx)
                    if 0.0 < r < d0:
                        sv = (k * (d0 - r)) * (dx / r)
                        F[i] += sv; F[j] -= sv
            for i in range(3): v[i] += F[i] / m[i] * dt
            for i in range(3): x[i] += v[i] * dt
        else:                                     # in-place: лічимо й рушаємо тіло за тілом
            for i in range(3):
                tot = 0.0
                for j in range(3):
                    if j == i: continue
                    dx = x[i] - x[j]; r = abs(dx)
                    if 0.0 < r < d0:
                        tot += (k * (d0 - r)) * (dx / r)
                v[i] += tot / m[i] * dt
                x[i] += v[i] * dt                 # x[i] зрушив ЗАРАЗ — інші тіла бачать нове
        ts.append(s * dt)
        for i in range(3): pind[i].append(m[i] * v[i])
        Ptot.append(sum(m[i] * v[i] for i in range(3)))
    return ts, pind, Ptot


def _poly(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.2f,%.2f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-linejoin="round"%s/>' % (s, color, sw, d))


# ── Фігура 7 (проєкт): одне число — двом тілам (ідіома пари-раз) ───────────────
def fig_pair_idiom():
    W, H = 900, 430
    ORANGE = "#d98324"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Сила пари — одне число, роздане двом тілам із протилежним знаком",
                  size=16, bold=True))

    # два тіла
    cy = 172
    ax, bx = 322, 578
    f.append(rect(ax - 42, cy - 34, 84, 68, fill="#eef2fb", stroke=INK, sw=2, rx=8))
    f.append(rect(bx - 42, cy - 34, 84, 68, fill="#eef2fb", stroke=INK, sw=2, rx=8))
    f.append(text(ax, cy + 7, "тіло i", size=15, bold=True, color=INK))
    f.append(text(bx, cy + 7, "тіло j", size=15, bold=True, color=INK))

    # одне число s посередині, над тілами
    b, w, h = textbox(W / 2, cy - 104, "s = k · (d₀ − r) · (dx ∕ r)",
                      size=15, pad=10, fill="#fff8e6", stroke=ORANGE, sw=1.6, bold=True)
    f.append(b)
    f.append(text(W / 2, cy - 66, "одне обчислення на пару", size=12, color=MUTED))
    f.append(line(W / 2 - 44, cy - 88, ax, cy - 40, color=MUTED, sw=1.2, dash="3 5"))
    f.append(line(W / 2 + 44, cy - 88, bx, cy - 40, color=MUTED, sw=1.2, dash="3 5"))

    # роздача: +s тілу i, −s тілу j
    f.append(arrow(ax + 48, cy, ax + 48 + 88, cy, color=POS, sw=3.6))
    f.append(text(ax + 48 + 44, cy - 14, "F[i] += s", size=14, bold=True, color=POS))
    f.append(text(ax + 48 + 44, cy + 26, "(дія)", size=12, color=POS))
    f.append(arrow(bx - 48, cy, bx - 48 - 88, cy, color=NEG, sw=3.6))
    f.append(text(bx - 48 - 44, cy - 14, "F[j] −= s", size=14, bold=True, color=NEG))
    f.append(text(bx - 48 - 44, cy + 26, "(протидія)", size=12, color=NEG))

    # два вироки
    b1, w1, h1 = textbox(W / 2, 330,
                         "пара-раз: те саме s обом → ΣF = 0 за побудовою, хоч який закон і округлення",
                         size=13.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(W / 2, 390,
                         "свій прохід на кожне тіло: реакцію лічать заново → баланс лише поки збіг тримається",
                         size=13.5, pad=11, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "pair-idiom.svg"), W, H, *f)


# ── Фігура 8 (проєкт): справжній прогін — частини міняються, сума стоїть ───────
def fig_momentum_trace():
    W, H = 960, 486
    ORANGE = "#d98324"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Справжній прогін: тіла обмінюються кількістю руху — сума стоїть",
                  size=16, bold=True))

    ts, pind, _ = _sim("pair")
    _, _, Pbug = _sim("bad")
    _, _, Pgood = _sim("pair")
    N = len(ts); stepn = 8
    idx = list(range(0, N, stepn)) + [N - 1]

    # ── ліва панель: окремі кількості руху + їх сума ──
    ox, oy, pw, ph = 82, 96, 336, 306
    t1 = ts[-1]; y0, y1 = -3.0, 7.0
    def mapL(t, y):
        return (ox + t / t1 * pw, oy + ph - (y - y0) / (y1 - y0) * ph)
    f.append(line(ox, oy, ox, oy + ph, color=INK, sw=1.4))
    f.append(line(ox, oy + ph, ox + pw, oy + ph, color=INK, sw=1.4))
    for yv in (-2, 0, 2, 4, 6):
        py = oy + ph - (yv - y0) / (y1 - y0) * ph
        f.append(line(ox - 4, py, ox, py, color=INK, sw=1.2))
        f.append(text(ox - 10, py + 4, str(yv), size=11, color=MUTED, anchor="end"))
        if yv == 2:
            f.append(line(ox, py, ox + pw, py, color="#dfe3ea", sw=1.0, dash="2 5"))
    f.append(text(ox + pw / 2, oy + ph + 30, "час t →", size=12, color=MUTED))
    f.append(text(ox, oy - 42, "p = m·v", size=12, color=MUTED, anchor="start"))
    f.append(text(ox + pw / 2, oy - 20, "Кожне тіло: p гуляє", size=13, bold=True, color=INK))
    cols = [POS, NEG, ORANGE]
    labs = ["тіло 0", "тіло 1", "тіло 2"]
    for i in range(3):
        pts = [mapL(ts[s], pind[i][s]) for s in idx]
        f.append(_poly(pts, cols[i], sw=2.2))
    pts = [mapL(ts[s], 2.0) for s in idx]     # сума — товста чорна, рівно 2.0
    f.append(_poly(pts, INK, sw=3.6))
    lx, ly = ox + 12, oy + 10                  # легенда
    for i in range(3):
        f.append(line(lx, ly + i * 19, lx + 22, ly + i * 19, color=cols[i], sw=2.6))
        f.append(text(lx + 28, ly + i * 19 + 4, labs[i], size=11, color=INK, anchor="start"))
    f.append(line(lx, ly + 3 * 19, lx + 22, ly + 3 * 19, color=INK, sw=3.4))
    f.append(text(lx + 28, ly + 3 * 19 + 4, "Σ = 2.0 (стала)", size=11, bold=True, color=INK, anchor="start"))

    # ── права панель: сумарна кількість руху — правильно vs баг ──
    ox2 = 566
    yb0, yb1 = 1.95, 2.22
    def mapR(t, y):
        return (ox2 + t / t1 * pw, oy + ph - (y - yb0) / (yb1 - yb0) * ph)
    f.append(line(ox2, oy, ox2, oy + ph, color=INK, sw=1.4))
    f.append(line(ox2, oy + ph, ox2 + pw, oy + ph, color=INK, sw=1.4))
    for yv in (1.95, 2.00, 2.05, 2.10, 2.15, 2.20):
        py = oy + ph - (yv - yb0) / (yb1 - yb0) * ph
        f.append(line(ox2 - 4, py, ox2, py, color=INK, sw=1.2))
        f.append(text(ox2 - 10, py + 4, "%.2f" % yv, size=11, color=MUTED, anchor="end"))
    f.append(text(ox2 + pw / 2, oy + ph + 30, "час t →", size=12, color=MUTED))
    f.append(text(ox2 + pw / 2, oy - 20, "Уся система: Σ p", size=13, bold=True, color=INK))
    ptsb = [mapR(ts[s], Pbug[s]) for s in idx]     # баг — червона, повзе вгору
    f.append(_poly(ptsb, POS, sw=2.8))
    ptsg = [mapR(ts[s], Pgood[s]) for s in idx]     # правильно — зелена, рівна на 2.0
    f.append(_poly(ptsg, FIELD, sw=3.0))
    f.append(text(ox2 + pw - 6, mapR(t1, Pbug[-1])[1] - 10,
                  "баг: +0.16 нізвідки", size=12, bold=True, color=POS, anchor="end"))
    f.append(text(ox2 + pw - 6, mapR(t1, 2.0)[1] + 22,
                  "пара-раз: рівно, |ΔP| < 6·10⁻¹⁵", size=12, bold=True, color=FIELD, anchor="end"))

    b, w, h = textbox(W / 2, H - 24,
                      "частини обмінюються без ліку — сума не здригнеться, поки код чесно тримає пару",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "momentum-trace.svg"), W, H, *f)



import math


# ── math-momentum-conservation: помічники ─────────────────────────────────────
def _mmc_pair(P, Q, rP, rQ, L=32, gap=6, cA=NEG, cB=POS, sw=3.0):
    """Пара рівних-протилежних внутрішніх сил уздовж відрізка P–Q:
    сила на P (біля P, у бік Q) і сила на Q (біля Q, у бік P) — рівні, протилежні."""
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    ax0, ay0 = P[0] + ux * (rP + gap), P[1] + uy * (rP + gap)
    bx0, by0 = Q[0] - ux * (rQ + gap), Q[1] - uy * (rQ + gap)
    return (arrow(ax0, ay0, ax0 + ux * L, ay0 + uy * L, color=cA, sw=sw) +
            arrow(bx0, by0, bx0 - ux * L, by0 - uy * L, color=cB, sw=sw))


def _mmc_com(cx, cy, r=11):
    """Значок центра мас — коло з перехрестям."""
    return (circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8) +
            line(cx - r, cy, cx + r, cy, color=INK, sw=1.4) +
            line(cx, cy - r, cx, cy + r, color=INK, sw=1.4))


def _mmc_oop(cx, cy, r=11):
    """Значок вектора «з площини» — коло з крапкою."""
    return (circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8) +
            circle(cx, cy, 2.6, fill=INK, stroke=INK, sw=1))


# ── Фігура (math): система N тіл — внутрішнє гасне попарно, зовнішнє веде ц.м. ──
def fig_system_com():
    W, H = 920, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Внутрішні пари гасяться попарно — центр мас веде лише зовнішнє",
                  size=16, bold=True))
    f.append(mtext(W / 2, 58,
                   ["внутрішні пари сил (червона-синя) рівні й протилежні",
                    "у сумі кожна пара = 0"],
                   size=12, color=MUTED))

    m1, m2, m3 = (310, 178), (250, 362), (476, 316)
    r = 30
    # внутрішні пари на трьох ребрах (кожна пара — рівна й протилежна)
    f.append(_mmc_pair(m1, m2, r, r))
    f.append(_mmc_pair(m1, m3, r, r))
    f.append(_mmc_pair(m2, m3, r, r))
    # тіла поверх стрілок
    for (cx, cy), lab in [(m1, "m₁"), (m2, "m₂"), (m3, "m₃")]:
        f.append(circle(cx, cy, r, fill="#eef2fb", stroke=INK, sw=2))
        f.append(text(cx, cy + 6, lab, size=17, bold=True, color=INK))

    # зовнішні сили (зелені), що входять у систему
    f.append(arrow(332, 74, 318, 143, color=FIELD, sw=3.4))
    f.append(text(346, 104, "зовнішня", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(628, 300, 510, 312, color=FIELD, sw=3.4))
    f.append(text(636, 300, "зовнішня", size=12, bold=True, color=FIELD, anchor="start"))

    # центр мас і рівнодійна зовнішніх
    cx, cy = 345, 285
    f.append(arrow(cx, cy, cx - 22, cy + 70, color=FIELD, sw=3.6))
    f.append(_mmc_com(cx, cy))
    f.append(text(cx + 20, cy - 6, "центр мас", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(cx - 34, cy + 78, "a_цм", size=13, bold=True, color=FIELD, anchor="end"))

    b, w, h = textbox(W / 2, H - 42,
                      "Σ внутрішніх = 0   →   dP/dt = F_зов = M · a_цм",
                      size=15, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "system-com.svg"), W, H, *f)


# ── Фігура (math): дві рухомі частинки — збій третього закону, кільк. руху поля ─
def fig_field_momentum():
    W, H = 960, 512
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Дві рухомі заряджені частинки: третій закон дає збій, поле тримає баланс",
                  size=15, bold=True))

    yline = 250
    q1 = (300, yline)
    q2 = (600, yline)
    # пряма, що з'єднує заряди
    f.append(line(140, yline, q1[0] - 20, yline, color=MUTED, sw=1.2, dash="4 6"))
    f.append(line(q1[0] + 20, yline, q2[0] - 20, yline, color=MUTED, sw=1.2, dash="4 6"))
    f.append(line(q2[0] + 20, yline, 740, yline, color=MUTED, sw=1.2, dash="4 6"))
    f.append(text(732, yline + 22, "пряма, що з'єднує заряди", size=12, color=MUTED))

    # заряд q1: рух уздовж прямої (вправо)
    f.append(plus(q1[0], q1[1], 16))
    f.append(text(q1[0], q1[1] - 30, "q₁", size=15, bold=True, color=INK))
    f.append(arrow(q1[0] + 20, yline, q1[0] + 92, yline, color=INK, sw=2.6))
    f.append(text(q1[0] + 56, yline - 12, "v₁ (уздовж прямої)", size=12, color=INK))
    # поле q2 у точці q1 — «з площини»
    f.append(_mmc_oop(q1[0] - 54, yline - 40))
    f.append(text(q1[0] - 54, yline - 62, "B від q₂", size=12, bold=True, color=INK))
    # магнітна сила на q1 — вниз, ненульова
    f.append(arrow(q1[0], q1[1] + 22, q1[0], q1[1] + 96, color=NEG, sw=3.6))
    f.append(text(q1[0] + 12, q1[1] + 84, "сила на q₁ ≠ 0", size=13, bold=True, color=NEG, anchor="start"))

    # заряд q2: рух упоперек прямої (вгору)
    f.append(plus(q2[0], q2[1], 16))
    f.append(text(q2[0] - 30, q2[1] - 34, "q₂", size=15, bold=True, color=INK, anchor="end"))
    f.append(arrow(q2[0], yline - 20, q2[0], yline - 92, color=INK, sw=2.6))
    f.append(text(q2[0] + 12, yline - 60, "v₂ (упоперек)", size=12, color=INK, anchor="start"))
    # на q2 магнітної сили нема
    f.append(text(q2[0], q2[1] + 44, "сила на q₂ = 0", size=13, bold=True, color=MUTED))
    f.append(text(q2[0], q2[1] + 64, "(q₁ не дає поля вздовж прямої)", size=11, color=MUTED))

    # кількість руху поля — компенсує (вгору), збоку праворуч
    fx = 790
    f.append(arrow(fx, yline + 50, fx, yline - 40, color=FIELD, sw=3.4))
    f.append(text(fx + 12, yline - 4, "p_поле", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(fx + 12, yline + 16, "росте вгору", size=11, color=FIELD, anchor="start"))

    b1, w1, h1 = textbox(W / 2, 406,
                         "Сили не рівні-протилежні: на q₁ сила є, на q₂ — нема",
                         size=14, pad=10, fill="#fdecea", stroke=POS, sw=1.3, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(W / 2, 468,
                         "Долучи поле — і баланс сходиться:  P_мех + P_поле = стала,  g = ε₀(E×B)",
                         size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "field-momentum.svg"), W, H, *f)

if __name__ == "__main__":
    ps = [fig_action_reaction(), fig_different_bodies(), fig_recoil(),
          fig_descartes_ledger(), fig_huygens_boat(), fig_collision_timeline(),
          fig_pair_idiom(), fig_momentum_trace(),
          fig_system_com(), fig_field_momentum()]
    print("written:")
    for p in ps:
        print("  ", p)
