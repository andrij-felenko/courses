# -*- coding: utf-8 -*-
"""Фігури до теми «Закон всесвітнього тяжіння».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GRAV = "#2457d6"   # тяжіння / притягання — холодне синє
BALL = "#c0392b"   # траєкторія ядра / яблуко — гаряче
MASS = "#e8edf3"   # заливка тіла-маси
SKY  = "#eef3fb"   # заливка планети


# ── Фігура 1: закон тяжіння між двома масами ────────────────────────────────
def fig_force_law():
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Закон тяжіння: однакова сила на обидва тіла", size=16, bold=True))
    f.append(text(W / 2, 56, "уздовж прямої, що їх сполучає — і завжди на притягання",
                  size=12, color=MUTED))

    m1 = (240, 178)
    m2 = (546, 178)
    f.append(circle(m1[0], m1[1], 46, fill=MASS, stroke=LINE, sw=2))
    f.append(text(m1[0], m1[1] + 6, "m₁", size=18, bold=True))
    f.append(circle(m2[0], m2[1], 32, fill=MASS, stroke=LINE, sw=2))
    f.append(text(m2[0], m2[1] + 6, "m₂", size=16, bold=True))

    # сили назустріч одна одній
    f.append(arrow(m1[0] + 52, m1[1], m1[0] + 128, m1[1], color=GRAV, sw=3.4))
    f.append(text(m1[0] + 90, m1[1] - 12, "F", size=16, bold=True, color=GRAV))
    f.append(arrow(m2[0] - 40, m2[1], m2[0] - 116, m2[1], color=GRAV, sw=3.4))
    f.append(text(m2[0] - 78, m2[1] - 12, "F", size=16, bold=True, color=GRAV))

    # розмір r
    yr = 256
    f.append(line(m1[0], m1[1] + 52, m1[0], yr + 8, color=MUTED, sw=1.0, dash="3,4"))
    f.append(line(m2[0], m2[1] + 38, m2[0], yr + 8, color=MUTED, sw=1.0, dash="3,4"))
    f.append(line(m1[0], yr, m2[0], yr, color=MUTED, sw=1.3))
    f.append(text((m1[0] + m2[0]) / 2, yr - 8, "r", size=15, italic=True, color=MUTED))

    b, _, _ = textbox(W / 2, 306, "F = G · m₁ · m₂ / r²      (a = F/m: легше тіло прискорюється сильно, важче — ледь-ледь)",
                      size=13, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "force-law.svg"), W, H, *f)


# ── Фігура 2: гарматне ядро Ньютона — падіння стає орбітою ───────────────────
def fig_newton_cannon():
    W, H = 720, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Гарматне ядро Ньютона: досить швидке — і падіння стає орбітою",
                  size=15.5, bold=True))
    f.append(text(W / 2, 56, "що швидше вистрелити, то далі ядро пролетить, поки падає",
                  size=12, color=MUTED))

    C = (360, 470)
    R = 200
    # планета (центр на полотні; видно верхню шапку — низ виходить за кадр)
    f.append(circle(C[0], C[1], R, fill=SKY, stroke=GRAV, sw=2))
    # орбіта — коло радіуса 240 через жерло гармати
    f.append('<circle cx="%d" cy="%d" r="240" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="7,6"/>' % (C[0], C[1], GRAV))
    # гора з гарматою на вершині
    peak = (360, 230)
    f.append('<polygon points="332,272 388,272 360,230" fill="#d8dee7" stroke="%s" stroke-width="1.4"/>' % LINE)
    f.append(line(peak[0], peak[1], peak[0] + 34, peak[1], color=INK, sw=6))   # ствол
    f.append(circle(peak[0], peak[1], 6, fill=INK, stroke=INK, sw=1))          # ядро в жерлі
    f.append(text(peak[0] + 42, peak[1] - 8, "v →", size=13, bold=True, color=BALL, anchor="start"))

    # балістичні дуги (горизонтальний старт: контроль на y=230)
    f.append('<path d="M 360 230 Q 452 230 460 297" fill="none" stroke="%s" stroke-width="2.4"/>' % BALL)
    f.append('<path d="M 360 230 Q 520 230 537 376" fill="none" stroke="%s" stroke-width="2.4"/>' % BALL)
    f.append(circle(460, 297, 4.5, fill=BALL, stroke=BALL, sw=1))
    f.append(circle(537, 376, 4.5, fill=BALL, stroke=BALL, sw=1))
    f.append(text(474, 288, "падає близько", size=12, color=BALL, anchor="start"))
    f.append(text(552, 372, "летить далі", size=12, color=BALL, anchor="start"))

    # позначка орбіти (ліворуч, де коло йде в чистому небі)
    f.append(text(150, 316, "орбіта", size=13, bold=True, color=GRAV, anchor="middle"))
    f.append(text(150, 336, "(промах!)", size=11.5, color=GRAV, anchor="middle"))

    b, _, _ = textbox(206, 150,
                      "Орбіта — це вільне падіння,\nяке не завершується ударом:\n"
                      "поверхня закруглюється вниз\nтак само швидко, як ядро опускається.",
                      size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "newton-cannon.svg"), W, H, *f)


# ── Фігура 3: чому квадрат — вплив розмазується по сфері площею ~ r² ─────────
def fig_inverse_square():
    W, H = 800, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Чому квадрат: вплив розходиться по сфері, площа якої росте як r²",
                  size=15, bold=True))

    S = (60, 210)
    # джерело
    f.append(circle(S[0], S[1], 15, fill="#fff3d0", stroke=BALL, sw=2))
    for ang in (-38, -13, 13, 38):
        a = math.radians(ang)
        f.append(line(S[0] + 15 * math.cos(a), S[1] + 15 * math.sin(a),
                      S[0] + 26 * math.cos(a), S[1] + 26 * math.sin(a), color=BALL, sw=1.6))

    centers = [250, 440, 630]
    sizes = [72, 144, 216]
    ncells = [1, 2, 3]
    labels = ["r", "2r", "3r"]
    areas = ["площа 1", "площа 4", "площа 9"]
    intens = ["×1", "×1/4", "×1/9"]

    # напрямні конуса — від джерела крізь дальні кути найбільшого квадрата
    top = (630 + 108, 210 - 108)
    bot = (630 + 108, 210 + 108)
    f.append(line(S[0], S[1], top[0], top[1], color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(S[0], S[1], bot[0], bot[1], color=MUTED, sw=1.2, dash="5,5"))

    for cx, s, n, lab, ar, it in zip(centers, sizes, ncells, labels, areas, intens):
        x0, y0 = cx - s / 2, 210 - s / 2
        f.append(rect(x0, y0, s, s, fill="none", stroke=GRAV, sw=1.9))
        step = s / n
        for i in range(1, n):
            f.append(line(x0 + i * step, y0, x0 + i * step, y0 + s, color="#c7d2e6", sw=1.1))
            f.append(line(x0, y0 + i * step, x0 + s, y0 + i * step, color="#c7d2e6", sw=1.1))
        f.append(text(cx, y0 - 12, it, size=13, bold=True, color=BALL))
        f.append(text(cx, 210 + s / 2 + 24, lab, size=15, bold=True))
        f.append(text(cx, 210 + s / 2 + 43, ar, size=12, color=MUTED))

    b, _, _ = textbox(W / 2, 418,
                      "та сама «кількість» тяжіння, розмазана по площі ~ r²   →   на одиницю площі  ~ 1/r²",
                      size=12.5, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "inverse-square.svg"), W, H, *f)


# ── Фігура 4: перевірка Місяцем — те саме число двома шляхами ────────────────
def fig_moon_test():
    W, H = 900, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Перевірка Місяцем: те саме тяжіння, послаблене квадратом відстані",
                  size=15.5, bold=True))

    E = (150, 250)
    Re = 70
    f.append(circle(E[0], E[1], Re, fill=SKY, stroke=GRAV, sw=2))
    f.append(text(E[0], E[1] + 5, "Земля", size=12, color=GRAV))
    # яблуко на поверхні + стрілка тяжіння вниз (до центра)
    ax, ay = E[0], E[1] - Re
    f.append(circle(ax, ay, 8, fill="#fef6e7", stroke=BALL, sw=2))
    f.append(arrow(ax, ay + 4, ax, ay + 40, color=GRAV, sw=2.6))
    f.append(text(ax + 14, ay - 6, "яблуко:  r = R,  a = 9.81 м/с²", size=12, anchor="start", bold=True))

    # Місяць
    M = (772, 250)
    Rm = 24
    f.append(circle(M[0], M[1], Rm, fill="#eef0f3", stroke=MUTED, sw=2))
    f.append(text(M[0], M[1] + 4, "Місяць", size=11.5, color=MUTED))
    f.append(arrow(M[0] - Rm - 4, M[1], M[0] - Rm - 40, M[1], color=GRAV, sw=2.6))
    f.append(text(M[0], M[1] - Rm - 10, "r ≈ 60 R", size=12.5, bold=True))

    # лінія відстані
    yline = 250
    f.append(line(E[0] + Re + 6, yline, M[0] - Rm - 46, yline, color=MUTED, sw=1.2, dash="6,5"))
    f.append(text((E[0] + M[0]) / 2 + 20, yline + 20, "≈ 60 радіусів Землі", size=12, color=MUTED))

    # крива спаду a ~ 1/r²  (над лінією)
    base = 208
    pts = []
    x = E[0] + Re + 8
    while x <= M[0] - Rm - 46:
        r = (x - E[0]) / Re            # відстань у радіусах Землі (поверхня → 1)
        h = 92.0 / (r * r)
        if h > 96:
            h = 96
        pts.append((x, base - h))
        x += 9
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly, BALL))
    f.append(text(300, 120, "a ∝ 1/r²  (тяжіння швидко слабшає)", size=12.5, bold=True, color=BALL, anchor="start"))

    # два незалежні обчислення внизу
    b1, w1, _ = textbox(238, 350, "Закон 1/r² обіцяє:\na = 9.81 / 60²  ≈  2.70·10⁻³ м/с²",
                        size=12.5, pad=10, fill=FILL, stroke=GRAV, sw=1.6)
    f.append(b1)
    b2, w2, _ = textbox(662, 350, "Орбіта Місяця дає:\na = 4π²r / T²  ≈  2.72·10⁻³ м/с²",
                        size=12.5, pad=10, fill=FILL, stroke=BALL, sw=1.6)
    f.append(b2)
    f.append(text(450, 356, "=", size=34, bold=True, color=FIELD))

    b3, _, _ = textbox(450, 408,
                       "два незалежні шляхи — і те саме число:  земне й небесне тяжіння одне",
                       size=12.5, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b3)
    return render(os.path.join(IMG, "moon-test.svg"), W, H, *f)


# ── Фігура 5 (hist): хронологія — не мить, а двадцять років ──────────────────
def fig_principia_timeline():
    W, H = 900, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Не одна мить, а двадцять років: як дозрівали «Начала»",
                  size=16, bold=True))
    f.append(text(W / 2, 56, "яблуко 1666-го — лише зернина; закон склався аж у 1680-х",
                  size=12, color=MUTED))

    ax = 300
    f.append(line(ax, 92, ax, 585, color=LINE, sw=2.6))

    def milestone(y, year, lines, hot=False):
        col = BALL if hot else GRAV
        f.append(circle(ax, y, 7, fill=col, stroke=col, sw=1))
        f.append(text(ax - 22, y + 5, year, size=13.5, bold=True, color=col, anchor="end"))
        f.append(mtext(ax + 26, y - (len(lines) - 1) * 8 + 4, lines,
                       size=12.5, color=INK, anchor="start", lh=1.28))

    milestone(112, "1665–66", ["Вулсторп, чума — Трініті зачинено.",
                               "Перша «перевірка Місяцем»: «доволі близько»."])
    # смуга мовчання
    f.append(rect(ax - 15, 150, 30, 96, fill="#f0f1f4", stroke='none', sw=0, rx=8))
    f.append('<line x1="%d" y1="150" x2="%d" y2="246" stroke="%s" '
             'stroke-width="2.6" stroke-dasharray="3,7"/>' % (ax, ax, MUTED))
    b, _, _ = textbox(ax + 176, 198,
                      "≈ 13 років — відкладено:\nне міг довести, що куля\nтягне як точка в центрі",
                      size=12, pad=9, fill=FILL, stroke=LINE, sw=1.2, color=MUTED)
    f.append(b)

    milestone(272, "1679–80", ["Листи Гука: здогад про 1/r²", "— без доведення."])
    milestone(338, "січень 1684", ["Кав'ярня: Галлей, Рен, Гук.", "Рен ставить заклад на доведення."])
    milestone(400, "серпень 1684", ["Галлей у Ньютона: «Який шлях планети?»", "— «Еліпс. Я вже це порахував.»"])
    milestone(460, "листопад 1684", ["«De motu corporum in gyrum» —", "дев'ять сторінок для Галлея."])
    milestone(516, "1685", ["Радіус Пікара + теорема про кулю:", "тепер збіг стає точним."], hot=True)
    milestone(568, "1687", ["«Начала» виходять — коштом Галлея."], hot=True)

    return render(os.path.join(IMG, "principia-timeline.svg"), W, H, *f)


# ── Фігура 6 (hist): здогад проти доведення — Гук і Ньютон ───────────────────
def fig_guess_vs_proof():
    W, H = 900, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Здогад — ще не закон: що зробив Гук, а що Ньютон",
                  size=16, bold=True))

    py, ph, pw = 62, 300, 390
    lx, rx = 40, 470
    f.append(rect(lx, py, pw, ph, fill="#fbfcfd", stroke=LINE, sw=1.4))
    f.append(rect(rx, py, pw, ph, fill="#fbfcfd", stroke=LINE, sw=1.4))

    hb, _, _ = textbox(lx + pw / 2, py + 26, "РОБЕРТ ГУК — здогад",
                       size=14, pad=8, fill="#fdecea", stroke=BALL, sw=1.5, bold=True, color=BALL)
    f.append(hb)
    hb2, _, _ = textbox(rx + pw / 2, py + 26, "ІСААК НЬЮТОН — доведення",
                        size=14, pad=8, fill="#eaf0fd", stroke=GRAV, sw=1.5, bold=True, color=GRAV)
    f.append(hb2)

    def bullets(px, items, mark_col):
        for i, (s, mut) in enumerate(items):
            yy = py + 82 + i * 46
            f.append(circle(px + 24, yy - 4, 3.5, fill=mark_col, stroke=mark_col, sw=1))
            f.append(mtext(px + 40, yy, s, size=12.5,
                           color=(MUTED if mut else INK), anchor="start", lh=1.22))

    bullets(lx, [
        ("тяжіння тягне до центра тіла", False),
        ("рух по прямій, доки сила не зверне", False),
        ("1/r² — записав у листі, як здогад", False),
        ("але орбіту з нього\nвивести не зумів", True),
    ], BALL)
    bullets(rx, [
        ("з 1/r² математично виводить еліпс", False),
        ("і Кеплерів закон площ", False),
        ("теорема про кулю: тягне як точка", False),
        ("закон — універсальний\nі виражений у числах", False),
    ], GRAV)

    cb, _, _ = textbox(W / 2, 420,
                       "Гук угадав закон — Ньютон довів, що з нього випливають еліпси (і сам Гук це визнав)",
                       size=12, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(cb)
    return render(os.path.join(IMG, "guess-vs-proof.svg"), W, H, *f)


# ── Фігура 7 (вставка Кавендіша): крутильні терези — за що крутиться нитка ────
def fig_cavendish_apparatus():
    W, H = 860, 520
    LEAD = "#7a8794"   # свинець — сірий метал
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Крутильні терези Кавендіша: тяг свинцю закручує нитку",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "вид згори — коромисло на нитці, малі кульки на кінцях, великі кулі підводять збоку",
                  size=12, color=MUTED))

    # махагонієва скриня (захист від протягів і тепла)
    f.append(rect(60, 74, 740, 344, fill="#f6efe4", stroke="#cbb894", sw=1.6, rx=10))
    f.append(text(74, 96, "махагонієва скриня — від протягів і перепадів тепла",
                  size=11.5, color="#9c7f4e", anchor="start"))

    C = (430, 236)   # центр коромисла (тут нитка виходить згори)

    # рейка спокою (пунктир) і відхилене коромисло (суцільне)
    f.append(line(250, 236, 610, 236, color=MUTED, sw=1.2, dash="6,5"))
    Lx, Ly = 252, 272     # лівий кінець відхиленого коромисла (пішов униз)
    Rx, Ry = 608, 200     # правий кінець (пішов угору)
    f.append(line(Lx, Ly, Rx, Ry, color=INK, sw=5))

    # нитка згори (кружок + значок кручення)
    f.append(circle(C[0], C[1], 9, fill="#ffffff", stroke=NEG, sw=2))
    f.append('<path d="M %d %d a 20 20 0 1 1 -6 -16" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>' % (C[0] + 20, C[1] - 6, NEG))
    f.append(text(C[0], C[1] - 58, "нитка (згори): закрут θ", size=12, bold=True,
                  color=NEG, anchor="middle"))

    # малі свинцеві кульки на кінцях
    f.append(circle(Lx, Ly, 15, fill=LEAD, stroke=LINE, sw=1.6))
    f.append(circle(Rx, Ry, 15, fill=LEAD, stroke=LINE, sw=1.6))
    f.append(text(150, 250, "малі кулі", size=12.5, bold=True, anchor="middle"))
    f.append(text(150, 268, "m ≈ 0.73 кг", size=12, color=MUTED, anchor="middle"))

    # великі свинцеві кулі: біля лівої — знизу, біля правої — зверху (пара сил)
    Ax, Ay = 252, 356
    Bx, By = 608, 116
    f.append(circle(Ax, Ay, 30, fill=LEAD, stroke=LINE, sw=1.8))
    f.append(circle(Bx, By, 30, fill=LEAD, stroke=LINE, sw=1.8))
    # стрілки притягання: мала кулька → до своєї великої
    f.append(arrow(Lx, Ly + 16, Ax, Ay - 32, color=GRAV, sw=2.6))
    f.append(arrow(Rx, Ry - 16, Bx, By + 32, color=GRAV, sw=2.6))
    f.append(text(Ax, Ay + 50, "велика куля  M ≈ 158 кг (свинець)", size=12.5, bold=True))
    f.append(text(Bx + 40, By, "M ≈ 158 кг", size=12, anchor="start", color=INK))
    f.append(text(Lx + 60, Ly + 26, "тяг F", size=12, color=GRAV, anchor="start", italic=True))

    b, _, _ = textbox(W / 2, 470,
                      "Тяг спрямований горизонтально, впоперек нитки — тож вертикальне тяжіння Землі\n"
                      "лише тримає коромисло на вазі й виміру не заважає; кут θ і є мірою сили.",
                      size=12.5, pad=11, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b)
    return render(os.path.join(IMG, "cavendish-apparatus.svg"), W, H, *f)


# ── Фігура 8 (вставка Кавендіша): що виказала густина Землі ──────────────────
def fig_earth_density():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Що виказало Кавендішеве число: надра важчі за камінь зверху",
                  size=15.5, bold=True))
    f.append(text(W / 2, 54, "густина відносно води — уся планета вдвічі щільніша за поверхневу породу",
                  size=12, color=MUTED))

    x0 = 300           # старт стовпчиків
    unit = 30          # px на одиницю густини
    rows = [
        ("вода", 1.0, "1.0", NEG),
        ("поверхневий граніт", 2.7, "≈ 2.7", "#8a7a5c"),
        ("уся Земля (Кавендіш)", 5.5, "≈ 5.5 г/см³", FIELD),
        ("залізо-нікелеве ядро", 12.0, "≈ 10–13", POS),
    ]
    y = 96
    bh = 40
    for name, val, lab, col in rows:
        f.append(text(x0 - 14, y + bh / 2 + 5, name, size=12.5, anchor="end", bold=True))
        f.append(rect(x0, y, val * unit, bh, fill=col, stroke=LINE, sw=1.2, rx=4))
        f.append(text(x0 + val * unit + 10, y + bh / 2 + 5, lab, size=12.5,
                      anchor="start", color=col, bold=True))
        y += bh + 22

    b, _, _ = textbox(W / 2, 350,
                      "уся планета щільніша за граніт удвічі  →  під корою ховається щось важче: залізне ядро",
                      size=12.5, pad=10, fill=FILL, stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "earth-density.svg"), W, H, *f)


# ── Фігура (math): другий закон Кеплера — рівні площі за рівний час ───────────
def fig_orbit_equal_areas():
    W, H = 840, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Другий закон Кеплера: рівні площі за рівний час",
                  size=16, bold=True))
    f.append(text(W / 2, 56, "біля Сонця планета мчить, далеко — повзе, а замітані площі однакові",
                  size=12, color=MUTED))

    cx, cy = 402, 262
    a, b = 214, 150
    c = math.sqrt(a * a - b * b)          # фокусна відстань
    Fx, Fy = cx - c, cy                   # Сонце — у лівому фокусі

    def ell(t):
        return (cx + a * math.cos(t), cy + b * math.sin(t))

    def wedge(t0, t1, n=30):
        pts = [(Fx, Fy)]
        for i in range(n + 1):
            pts.append(ell(t0 + (t1 - t0) * i / n))
        s = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0, pts

    # афелійний сектор (тонкий, біля дальнього правого краю) — фіксований кут
    da = 0.46
    A_aph, pts_aph = wedge(-da, da)
    # перигелійний сектор — підганяємо кут під РІВНУ площу
    lo, hi = 0.2, 2.7
    for _ in range(44):
        mid = (lo + hi) / 2
        Am, _ = wedge(math.pi - mid, math.pi + mid)
        if Am < A_aph:
            lo = mid
        else:
            hi = mid
    dp = (lo + hi) / 2
    _, pts_per = wedge(math.pi - dp, math.pi + dp)

    # еліпс
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
             'stroke-width="2"/>' % (cx, cy, a, b, SKY, GRAV))
    # два сектори — однакова заливка, бо однакова площа
    WED, WEDL = "#fde6c6", "#d79b34"
    for pts in (pts_aph, pts_per):
        poly = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4" '
                 'fill-opacity="0.9"/>' % (poly, WED, WEDL))

    # Сонце у фокусі
    f.append(circle(Fx, Fy, 13, fill="#ffe6a1", stroke=BALL, sw=2))
    f.append(text(Fx, Fy - 22, "Сонце", size=12.5, bold=True, color=BALL))

    # планета в кожному секторі + стрілка швидкості (довга близько, коротка далеко)
    pp = ell(math.pi)                     # перигелій (ліворуч, близько)
    pa = ell(0.0)                         # афелій (праворуч, далеко)
    f.append(circle(pp[0], pp[1], 7, fill=GRAV, stroke=INK, sw=1.2))
    f.append(circle(pa[0], pa[1], 7, fill=GRAV, stroke=INK, sw=1.2))
    f.append(arrow(pp[0], pp[1] - 8, pp[0], pp[1] - 76, color=BALL, sw=3.2))
    f.append(text(pp[0], pp[1] - 88, "швидко", size=12, bold=True, color=BALL, anchor="middle"))
    f.append(arrow(pa[0], pa[1] - 8, pa[0], pa[1] - 40, color=NEG, sw=3.2))
    f.append(text(pa[0], pa[1] - 52, "повільно", size=12, bold=True, color=NEG, anchor="middle"))

    f.append(text(pp[0], pp[1] + 28, "перигелій", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(pa[0], pa[1] + 28, "афелій", size=11.5, color=MUTED, anchor="middle"))

    b1, _, _ = textbox(W / 2, 452,
                       "рівні площі за рівний час   ⟺   dA/dt = L / 2m = const   (момент імпульсу)",
                       size=13, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b1)
    return render(os.path.join(IMG, "orbit-equal-areas.svg"), W, H, *f)


# ── Фігура (math): форма орбіти = знак повної енергії ─────────────────────────
def fig_orbit_energy_types():
    W, H = 800, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Форма орбіти — це знак повної енергії", size=16, bold=True))
    f.append(text(W / 2, 56, "та сама точка й напрям, більша швидкість — усе відкритіша траєкторія",
                  size=12, color=MUTED))

    Mx, My = 262, 300
    rp = 56
    Px, Py = Mx + rp, My

    def conic(e, th_max_deg, col, sw=2.6):
        n = 240
        raw = []
        for i in range(n + 1):
            th = math.radians(-th_max_deg + 2 * th_max_deg * i / n)
            denom = 1 + e * math.cos(th)
            if denom <= 0.10:
                raw.append(None)
                continue
            r = rp * (1 + e) / denom
            x = Mx + r * math.cos(th)
            y = My + r * math.sin(th)
            if x < 42 or x > W - 42 or y < 74 or y > H - 74:
                raw.append(None)
            else:
                raw.append((x, y))
        segs, cur = [], []
        for p in raw:
            if p is None:
                if len(cur) > 1:
                    segs.append(cur)
                cur = []
            else:
                cur.append(p)
        if len(cur) > 1:
            segs.append(cur)
        out = []
        for s in segs:
            poly = " ".join("%.1f,%.1f" % q for q in s)
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                       % (poly, col, sw))
        return "".join(out)

    # колова орбіта (пунктир) радіуса rp — окремий, найглибший випадок
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="5,5"/>' % (Mx, My, rp, MUTED))
    # три конічні перерізи зі спільним перигелієм
    f.append(conic(0.5, 180, GRAV))       # еліпс   E<0
    f.append(conic(1.0, 118, BALL))       # парабола E=0
    f.append(conic(1.5, 92, FIELD))       # гіпербола E>0

    # центральне тіло
    f.append(circle(Mx, My, 19, fill=SKY, stroke=GRAV, sw=2))
    f.append(text(Mx, My + 5, "M", size=15, bold=True, color=GRAV))

    # спільний перигелій + стрілка швидкості вгору
    f.append(circle(Px, Py, 5, fill=INK, stroke=INK, sw=1))
    f.append(arrow(Px, Py - 6, Px, Py - 58, color=INK, sw=2.6))
    f.append(text(Px + 12, Py - 42, "v", size=14, italic=True, bold=True, anchor="start"))
    f.append(text(Px + 8, Py + 20, "спільна точка", size=11, color=MUTED, anchor="start"))

    # легенда (праворуч угорі, де немає кривих)
    lx, ly = 560, 138
    rows = [(GRAV, "E < 0  —  еліпс (зв'язана)"),
            (BALL, "E = 0  —  парабола (утеча)"),
            (FIELD, "E > 0  —  гіпербола"),
            (MUTED, "коло:  E = −GMm / 2r")]
    for i, (col, s) in enumerate(rows):
        yy = ly + i * 30
        dash = ' stroke-dasharray="5,5"' if i == 3 else ''
        f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"%s/>'
                 % (lx, yy, lx + 32, yy, col, dash))
        f.append(text(lx + 42, yy + 5, s, size=12.5, color=INK, anchor="start"))

    b1, _, _ = textbox(W / 2, 534,
                       "коло → еліпс → парабола → гіпербола   зі зростанням швидкості в тій самій точці",
                       size=13, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b1)
    return render(os.path.join(IMG, "orbit-energy-types.svg"), W, H, *f)


# ── Числове інтегрування двох тіл (вставка proj-orbit-integrator) ─────────────
ORB  = "#2457d6"   # симплектична орбіта — синє
SPIR = "#c0392b"   # наївний Ейлер — гаряче червоне
GOOD = "#1e7a46"   # leapfrog / збережене — зелене


def _integrate(method, dt, nsteps, x=1.0, y=0.0, vx=0.0, vy=1.2, gm=1.0):
    """Крихітний інтегратор двох тіл (GM у центрі). Повертає списки x, y, E."""
    def acc(x, y):
        r = math.sqrt(x * x + y * y)
        fr = -gm / (r * r * r)
        return fr * x, fr * y
    def en(x, y, vx, vy):
        return 0.5 * (vx * vx + vy * vy) - gm / math.sqrt(x * x + y * y)
    xs, ys, es = [x], [y], [en(x, y, vx, vy)]
    for _ in range(nsteps):
        if method == "euler":
            ax, ay = acc(x, y)
            x, y, vx, vy = x + vx * dt, y + vy * dt, vx + ax * dt, vy + ay * dt
        elif method == "cromer":
            ax, ay = acc(x, y)
            vx, vy = vx + ax * dt, vy + ay * dt
            x, y = x + vx * dt, y + vy * dt
        else:  # verlet
            ax, ay = acc(x, y)
            x = x + vx * dt + 0.5 * ax * dt * dt
            y = y + vy * dt + 0.5 * ay * dt * dt
            ax2, ay2 = acc(x, y)
            vx, vy = vx + 0.5 * (ax + ax2) * dt, vy + 0.5 * (ay + ay2) * dt
        xs.append(x); ys.append(y); es.append(en(x, y, vx, vy))
    return xs, ys, es


# ── Фігура A: наївний Ейлер розкручується, симплектичний тримає еліпс ─────────
def fig_euler_vs_symplectic():
    W, H = 860, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий закон 1/r², той самий крок — різне впорядкування двох рядків коду",
                  size=15, bold=True))

    dt, norb, T = 0.02, 6, 14.9933
    n = int(norb * T / dt)
    xe, ye, _ = _integrate("euler", dt, n)
    xc, yc, _ = _integrate("cromer", dt, n)

    rmax = max(math.hypot(xe[i], ye[i]) for i in range(len(xe)))
    scale = 150.0 / rmax                       # спільний масштаб під більшу траєкторію
    panels = [(228, "Наївний Ейлер", SPIR, xe, ye),
              (632, "Симплектичний (Ейлер-Кромер)", ORB, xc, yc)]

    for cx, ttl, col, xs, ys in panels:
        cyc = 248
        f.append(rect(cx - 196, 50, 392, 372, fill="#fcfcfd", stroke=LINE, sw=1.2))
        f.append(text(cx, 74, ttl, size=13.5, bold=True, color=col))
        f.append(circle(cx, cyc, 8, fill="#fff3d0", stroke="#e0a800", sw=2))     # зоря у фокусі
        k = max(1, len(xs) // 900)
        pts = " ".join("%.1f,%.1f" % (cx + xs[i] * scale, cyc - ys[i] * scale)
                       for i in range(0, len(xs), k))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (pts, col))
        f.append(circle(cx + xs[0] * scale, cyc - ys[0] * scale, 4, fill=INK, stroke=INK, sw=1))

    b1, _, _ = textbox(228, 446, "енергія повзе вгору → орбіта розкручується назовні",
                       size=12, pad=8, fill="#fdecea", stroke=SPIR, sw=1.4)
    f.append(b1)
    b2, _, _ = textbox(632, 446, "енергія тримається → той самий еліпс знову й знову",
                       size=12, pad=8, fill="#eaf2ff", stroke=ORB, sw=1.4)
    f.append(b2)
    return render(os.path.join(IMG, "orbit-euler-vs-symplectic.svg"), W, H, *f)


# ── Фігура B: повна енергія в часі — Ейлер тікає, симплектичні тримають ───────
def fig_energy_drift():
    W, H = 820, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Повна енергія орбіти в часі: хворобу наївного кроку видно лише на довгій дистанції",
                  size=14, bold=True))

    dt, norb, T = 0.01, 6, 14.9933
    n = int(norb * T / dt)
    _, _, ee = _integrate("euler", dt, n)
    _, _, ec = _integrate("cromer", dt, n)
    _, _, ev = _integrate("verlet", dt, n)

    L, R, Tp, B = 92, 770, 68, 348
    Emin, Emax = -0.30, -0.14
    def X(step): return L + (R - L) * step / n
    def Y(e): return B - (B - Tp) * (max(Emin, min(Emax, e)) - Emin) / (Emax - Emin)

    f.append(rect(L, Tp, R - L, B - Tp, fill="#fcfcfd", stroke=LINE, sw=1.2))
    for e in (-0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18, -0.16, -0.14):
        yy = Y(e)
        f.append(line(L, yy, R, yy, color="#eef1f5", sw=1.0))
        f.append(text(L - 10, yy + 4, "%.2f" % e, size=10.5, color=MUTED, anchor="end"))
    f.append(line(L, Y(-0.28), R, Y(-0.28), color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(L + 8, Y(-0.28) - 7, "істинна E = −0.28", size=10.5, color=MUTED, anchor="start"))
    for ob in range(norb + 1):
        xx = L + (R - L) * ob / norb
        f.append(line(xx, B, xx, B + 5, color=LINE, sw=1.0))
        f.append(text(xx, B + 20, str(ob), size=10.5, color=MUTED))
    f.append(text((L + R) / 2, B + 40, "обертів навколо зорі", size=11.5, color=MUTED))
    f.append(text(L - 52, (Tp + B) / 2, "E", size=13, bold=True, color=INK))

    def curve(es, col, sw):
        k = max(1, n // 260)
        pts = " ".join("%.1f,%.1f" % (X(i), Y(es[i])) for i in range(0, n + 1, k))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (pts, col, sw))
    curve(ec, GOOD, 3.6)     # знизу, найширша — щоб не сховалась
    curve(ev, ORB, 2.0)
    curve(ee, SPIR, 2.4)

    f.append(text(R - 8, Y(ee[-1]) - 9, "Ейлер — тікає вгору", size=12, bold=True, color=SPIR, anchor="end"))
    b, _, _ = textbox(320, 318, "Ейлер-Кромер і Verlet майже зливаються з істинною лінією",
                      size=11.5, pad=7, fill="#eafaf1", stroke=GOOD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "orbit-energy-drift.svg"), W, H, *f)


# ── Фігура C: чому наївний крок відходить від центра і як лагодить перестановка ─
def fig_step_geometry():
    W, H = 860, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому наївний крок відходить від зорі — і чим його лагодить перестановка рядків",
                  size=14.5, bold=True))

    # ── ЛІВА панель: прямий крок уздовж дотичної промахується назовні ──
    f.append(rect(30, 50, 400, 324, fill="#fcfcfd", stroke=LINE, sw=1.2))
    f.append(text(230, 72, "крок по прямій промахується назовні", size=12.5, bold=True, color=SPIR))
    cx, cy, Rr = 214, 222, 132
    step = 88
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="5,5"/>' % (cx, cy, Rr, ORB))
    f.append(text(cx, cy - Rr - 8, "справжня орбіта (коло)", size=11, color=ORB))
    f.append(circle(cx, cy, 7, fill="#fff3d0", stroke="#e0a800", sw=2))
    f.append(text(cx + 14, cy + 5, "зоря", size=11, color=MUTED, anchor="start"))
    P = (cx - Rr, cy)
    Q = (cx - Rr, cy + step)
    f.append(circle(P[0], P[1], 4.5, fill=INK, stroke=INK, sw=1))
    f.append(text(P[0] - 8, P[1] - 8, "P", size=12, bold=True, anchor="end"))
    f.append(arrow(P[0], P[1] + 2, Q[0], Q[1], color=SPIR, sw=2.6))
    f.append(text(P[0] - 8, (P[1] + Q[1]) / 2 + 4, "крок", size=11, color=SPIR, anchor="end"))
    f.append(text(P[0] - 8, (P[1] + Q[1]) / 2 + 19, "v·Δt", size=11, color=SPIR, anchor="end"))
    # радіальна лінія зоря→Q, перетин із колом і зовнішній надлишок Δr
    dQ = math.hypot(Q[0] - cx, Q[1] - cy)
    ux, uy = (Q[0] - cx) / dQ, (Q[1] - cy) / dQ
    Cx, Cyy = cx + Rr * ux, cy + Rr * uy
    f.append(line(cx, cy, Q[0], Q[1], color=MUTED, sw=1.1, dash="3,4"))
    f.append(circle(Cx, Cyy, 3.2, fill=ORB, stroke=ORB, sw=1))
    f.append(line(Cx, Cyy, Q[0], Q[1], color=SPIR, sw=3.2))
    f.append(circle(Q[0], Q[1], 4, fill=SPIR, stroke=SPIR, sw=1))
    f.append(text(Q[0] + 10, Q[1] + 16, "опинивсь далі — на Δr назовні", size=11, bold=True, color=SPIR, anchor="start"))
    b, _, _ = textbox(230, 356, "крива загинається до зорі — пряма ні → щокроку трохи назовні",
                      size=10.8, pad=6, fill="#fdecea", stroke=SPIR, sw=1.3)
    f.append(b)

    # ── ПРАВА панель: два впорядкування + вирок за площею фазового простору ──
    px = 452
    f.append(rect(px, 50, 378, 324, fill="#fcfcfd", stroke=LINE, sw=1.2))
    f.append(text(px + 189, 72, "порядок двох рядків вирішує все", size=12.5, bold=True, color=INK))
    f.append(fitbox(px + 22, 92, 334, 84,
                    "Ейлер:  посунь x старою v, тоді онови v\n"
                    "     x ← x + v·Δt      (стара v)\n"
                    "     v ← v + a(x)·Δt",
                    size=11.5, pad=9, fill="#fdecea", stroke=SPIR, sw=1.5))
    f.append(text(px + 189, 196, "площа у фазовому просторі росте  ×(1 + (ωΔt)²)  →  розкрут",
                  size=10.6, color=SPIR))
    f.append(fitbox(px + 22, 216, 334, 84,
                    "Кромер:  спершу онови v, тоді посунь x новою v\n"
                    "     v ← v + a(x)·Δt\n"
                    "     x ← x + v·Δt      (нова v)",
                    size=11.5, pad=9, fill="#eaf2ff", stroke=ORB, sw=1.5))
    f.append(text(px + 189, 328, "площа зберігається  ×1 (det = 1)  →  симплектичність, орбіта в пастці",
                  size=10.6, color=ORB))
    return render(os.path.join(IMG, "orbit-step-geometry.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [fig_force_law(), fig_newton_cannon(), fig_inverse_square(),
            fig_moon_test(), fig_principia_timeline(),
            fig_guess_vs_proof(), fig_cavendish_apparatus(),
            fig_earth_density(), fig_orbit_equal_areas(),
            fig_orbit_energy_types(),
            fig_euler_vs_symplectic(), fig_energy_drift(), fig_step_geometry()]
    print("written:")
    for p in outs:
        print("  ", p)
