# -*- coding: utf-8 -*-
"""Фігури теми «Вибір топології живлення» та її вставки про ККД ланцюга.
svgkit зі scripts/ ІМПОРТУЄМО, не переписуємо (AUTHORING §5).

Запуск:  python figs.py   →  кладе всі .svg у ./img/
Перевірка: python ../../../../scripts/svgcheck.py img
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори топологій — у межах палітри svgkit (POS/NEG/FIELD/INK/MUTED)
T_BUCK = NEG     # синій
T_BOOST = POS    # червоний
T_BB = FIELD     # зелений
T_PUMP = "#b8860b"   # темне золото (читабельне на білому)
T_ISO = "#7d3cb5"    # фіолетове — ізольовані
WARN_FILL = "#fbe9e7"
GOOD_FILL = "#eef7f0"


def chip(cx, cy, w, h, title, sub, stroke, fill="#ffffff"):
    """Рамка-вузол: жирний заголовок + дрібний підпис. Текст не вилазить."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=2)
    if sub:
        out += text(cx, cy - 3, title, size=13, color=stroke, bold=True)
        out += text(cx, cy + 15, sub, size=10.5, color=MUTED)
    else:
        out += text(cx, cy + 4, title, size=13, color=stroke, bold=True)
    return out


# ─────────────────────────────────────────────────────────────────────────────
def fig_decision_tree():
    """Дерево рішення: ізоляція → напрямок → окремі гілки (помпа, захист)."""
    W, H = 940, 560
    f = []
    # старт
    f.append(chip(470, 67, 150, 34, "Потрібен DC-DC", "", NEG, fill="#eef0fb"))
    f.append(arrow(470, 84, 470, 102, color=INK))
    # ромб «ізоляція?»
    f.append('<polygon points="470,102 590,134 470,166 350,134" '
             'fill="#fbf7ec" stroke="%s" stroke-width="2"/>' % INK)
    f.append(text(470, 130, "Потрібна ізоляція?", size=12, color=INK, bold=True))
    f.append(text(470, 148, "(мережа / безпека)", size=10, color=MUTED))
    # ТАК → flyback
    f.append(arrow(590, 134, 762, 134, color=T_BOOST))
    f.append(text(676, 124, "ТАК", size=11, color=T_BOOST, bold=True))
    f.append(chip(845, 134, 165, 52, "FLYBACK", "<100 Вт; далі forward/міст", T_BOOST, fill=GOOD_FILL))
    # НІ ↓
    f.append(arrow(470, 166, 470, 196, color=INK))
    f.append(text(486, 188, "НІ", size=11, color=T_BOOST, bold=True))
    f.append(chip(470, 216, 230, 38, "Vвих відносно Vвх?", "", INK))
    # чотири гілки напрямку
    branches = [
        (165, "завжди нижче", "BUCK", "синхронний — ККД", T_BUCK),
        (370, "завжди вище", "BOOST", "стереже КЗ!", T_BOOST),
        (575, "гуляє навколо", "BUCK-BOOST", "4-ключ., +вихід", T_BB),
        (790, "потрібен −", "інверт. b-b", "від'ємний вихід", T_BUCK),
    ]
    for bx, lbl, name, sub, col in branches:
        f.append(line(470, 235, bx, 286, color=MUTED, sw=1.5, dash=None))
        f.append(text(bx, 272, lbl, size=10, color=MUTED, italic=True))
        f.append(chip(bx, 312, 152, 50, name, sub, col, fill=GOOD_FILL))
    # окрема гілка — помпа
    f.append(rect(60, 384, 820, 54, fill="#fff7e6", stroke=T_PUMP, sw=1.8, rx=10))
    f.append(text(470, 408, "малий струм (мА) + проста кратність (×2, −1, ½) + без котушки",
                  size=12, color=INK, bold=True))
    f.append(text(470, 428, "→ CHARGE PUMP (заряд-помпа, на конденсаторах)",
                  size=12, color=T_PUMP, bold=True))
    # нагадування про захист
    f.append(rect(60, 452, 820, 56, fill=WARN_FILL, stroke=T_BOOST, sw=1.6, rx=10))
    f.append(text(470, 475, "boost не захищає власний вихід від КЗ: треба захист — послідовний роз'єднувач",
                  size=11.5, color=INK))
    f.append(text(470, 495, "або SEPIC (рве постійний шлях). Для мережі ізоляція — не опція, а вимога безпеки.",
                  size=11.5, color=INK))
    render(os.path.join(OUT, "decision-tree.svg"), W, H, *f,
           title="Дерево вибору: п'ять питань від найжорсткішого обмеження до тоншого")


# ─────────────────────────────────────────────────────────────────────────────
def fig_power_map():
    """Карта потужність × тип перетворення: область кожної топології."""
    W, H = 940, 470
    L, R, T, B = 130, 860, 70, 360
    f = []
    f.append(arrow(L, B, R + 2, B, color=INK, sw=1.6))
    f.append(arrow(L, B, L, T - 2, color=INK, sw=1.6))
    f.append(text(R - 50, B + 24, "потужність →", size=11, color=INK, bold=True))
    f.append(text(L - 8, T - 6, "тип перетворення", size=11, color=INK, bold=True, anchor="end"))
    # мітки осі x
    for x, lbl in [(190, "мВт"), (350, "Вт"), (510, "10 Вт"), (670, "100 Вт"), (830, "кВт")]:
        f.append(line(x, B, x, B + 5, color=MUTED, sw=1))
        f.append(text(x, B + 20, lbl, size=10, color=MUTED))
    # горизонтальні смуги типів
    for y, lbl in [(110, "підвищення"), (175, "≈ вхід / вниз-вгору"),
                   (240, "зниження"), (305, "інверсія")]:
        f.append(line(L, y, R - 10, y, color="#e4e4e4", sw=1))
        f.append(text(L - 8, y + 4, lbl, size=9.5, color=MUTED, anchor="end"))
    # області
    def area(x, y, w, h, name, col):
        f.append(rect(x, y, w, h, fill="#ffffff", stroke=col, sw=2))
        f.append(rect(x, y, w, h, fill=col, stroke="none", sw=0))  # тінь
        f.append(text(x + w / 2, y + h / 2 + 4, name, size=11.5, color=col, bold=True))
    # напівпрозорі заливки робимо окремо (svgkit rect не дає opacity → робимо світлий fill)
    def area2(x, y, w, h, name, col, lite):
        f.append(rect(x, y, w, h, fill=lite, stroke=col, sw=2))
        f.append(text(x + w / 2, y + h / 2 + 4, name, size=11.5, color=col, bold=True))
    area2(150, 90, 150, 40, "charge pump ×2", T_PUMP, "#faf3e0")
    area2(150, 285, 150, 40, "charge pump", T_PUMP, "#faf3e0")
    area2(310, 92, 280, 36, "BOOST", T_BOOST, "#fdecea")
    area2(310, 157, 300, 36, "BUCK-BOOST", T_BB, "#e9f7ee")
    area2(310, 222, 330, 36, "BUCK (синхр.)", T_BUCK, "#eaf0fd")
    area2(430, 285, 230, 36, "інверт. b-b", T_BUCK, "#eaf0fd")
    area2(650, 130, 120, 150, "FLYBACK", T_ISO, "#f1e9f8")
    area2(778, 90, 82, 230, "forward / міст", T_ISO, "#ece0f5")
    # підсумок
    f.append(rect(70, 430, 800, 28, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=8))
    f.append(text(470, 449,
                  "Помпа — лівий нижній кут; котушкові buck/boost/buck-boost — середина; ізольовані — праворуч зі зростанням потужності",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "power-map.svg"), W, H, *f,
           title="Де живе кожна топологія: потужність × тип перетворення")


# ─────────────────────────────────────────────────────────────────────────────
def fig_recognize_board():
    """Прикмета на платі → яка це топологія."""
    W, H = 940, 440
    f = []
    rows = [
        ("котушка + 1 діод Шотткі", "асинхронний buck або boost", T_BUCK),
        ("котушка + 2 MOSFET (чи power-stage)", "СИНХРОННИЙ buck/boost (ККД)", T_BB),
        ("2 котушки + конденсатор між ними", "SEPIC (вгору/вниз, +вихід)", T_BB),
        ("трансформатор + оптопара", "ІЗОЛЬОВАНИЙ flyback — мережа/безпека", T_BOOST),
        ("2–3 однакові C, без котушки", "charge pump (мала допоміжна шина)", T_PUMP),
        ("велика котушка + контролер + щільні C", "силова шина — головний перетворювач", T_BUCK),
    ]
    y = 70
    for left, right, col in rows:
        f.append(rect(50, y, 400, 46, fill="#f6f9fc", stroke=MUTED, sw=1.4))
        f.append(text(70, y + 28, left, size=11.5, color=INK, bold=True, anchor="start"))
        f.append(arrow(456, y + 23, 496, y + 23, color=INK))
        f.append(rect(500, y, 390, 46, fill=GOOD_FILL, stroke=col, sw=1.8))
        f.append(text(520, y + 28, right, size=11.5, color=col, bold=True, anchor="start"))
        y += 56
    f.append(rect(70, y + 2, 800, 26, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=8))
    f.append(text(470, y + 20,
                  "Найгаласливіший куток (котушка + ключі + щільні конденсатори) — це вузол перемикання; його тримають компактним",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "recognize-board.svg"), W, H, *f,
           title="Як упізнати топологію на платі за її прикметами")


# ─────────────────────────────────────────────────────────────────────────────
def fig_secondary_axes():
    """Вторинні осі вибору всередині обраної сім'ї."""
    W, H = 940, 410
    f = []
    rows = [
        ("Випрямляч", "діод (асинхр.)", "дешево / простіше", "MOSFET (синхр.)", "ККД на струмі"),
        ("Легке навантаж.", "forced-PWM", "чисті завади", "авто-PFM", "автономність у сні"),
        ("Реалізація", "дискрет", "гнучко / дешевше", "інтегр. модуль", "просто / швидко"),
        ("Частота", "нижча", "менші втрати", "вища", "менші котушка й C"),
    ]
    y = 78
    for axis, la, lasub, lb, lbsub in rows:
        f.append(text(60, y + 6, axis, size=12.5, color=INK, bold=True, anchor="start"))
        f.append(rect(210, y - 24, 250, 48, fill="#eaf0fd", stroke=T_BUCK, sw=1.8))
        f.append(text(335, y - 4, la, size=12, color=T_BUCK, bold=True))
        f.append(text(335, y + 14, lasub, size=10, color=MUTED))
        f.append(text(480, y + 6, "⇄", size=18, color=INK, bold=True))
        f.append(rect(500, y - 24, 250, 48, fill=GOOD_FILL, stroke=T_BB, sw=1.8))
        f.append(text(625, y - 4, lb, size=12, color=T_BB, bold=True))
        f.append(text(625, y + 14, lbsub, size=10, color=MUTED))
        f.append(text(820, y + 4, "компроміс", size=9.5, color=MUTED, italic=True))
        y += 84
    render(os.path.join(OUT, "secondary-axes.svg"), W, H, *f,
           title="Сім'ю обрано — лишаються вторинні осі вибору")


# ─────────────────────────────────────────────────────────────────────────────
def fig_tradeoffs():
    """Матриця компромісів: крапки-оцінки за осями (5 = максимум)."""
    W, H = 940, 440
    f = []
    cols = [("простота", 274), ("ціна↓", 384), ("ККД", 484),
            ("потужн.", 584), ("розмір↓", 694), ("тиша", 814)]
    # шапка
    f.append(rect(40, 64, 850, 34, fill="#eaf0fd", stroke=T_BUCK, sw=1.6))
    f.append(text(60, 86, "топологія", size=11.5, color=T_BUCK, bold=True, anchor="start"))
    for name, cx in cols:
        f.append(text(cx, 86, name, size=11.5, color=T_BUCK, bold=True))
    # рядки: оцінки 0..5 за кожною віссю
    data = [
        ("buck (синхр.)", [4, 4, 5, 4, 4, 3]),
        ("boost",         [4, 4, 4, 3, 3, 2]),
        ("buck-boost (4кл.)", [2, 2, 4, 4, 3, 2]),
        ("charge pump",   [5, 5, 2, 1, 5, 4]),
        ("flyback",       [2, 3, 3, 4, 2, 2]),
    ]
    y = 104
    for i, (name, scores) in enumerate(data):
        rowfill = "#ffffff" if i % 2 == 0 else "#f6f6f6"
        f.append(rect(40, y, 850, 44, fill=rowfill, stroke="#e4e4e4", sw=1, rx=0))
        f.append(text(60, y + 27, name, size=11.5, color=INK, bold=True, anchor="start"))
        for (cname, cx), sc in zip(cols, scores):
            for k in range(5):
                col = INK if k < sc else "#dcdcdc"
                f.append(circle(cx - 18 + k * 9, y + 23, 3.2, fill=col, stroke=col, sw=0))
        y += 50
    f.append(rect(70, y + 6, 800, 26, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=8))
    f.append(text(470, y + 24,
                  "Помпа виграє в простоті/розмірі, програє в потужності/ККД; flyback дає ізоляцію ціною складності; buck — універсал",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "tradeoffs.svg"), W, H, *f,
           title="Порівняння за компромісами (більше ● — більше виражено)")


# ─────────────────────────────────────────────────────────────────────────────
def fig_pitfalls():
    """Шість найчастіших пасток вибору — чого не робити."""
    W, H = 940, 430
    f = []
    cards = [
        ("✗ boost «захистить» вихід", "ні — він прозорий для КЗ; додай роз'єднувач"),
        ("✗ charge pump на реальний струм", "ні — це мА; для потужності бери котушку"),
        ("✗ мережа без ізоляції", "смертельно — для 230 В лише flyback/ізольовані"),
        ("✗ котушка boost під вихідний струм", "ні — рахуй під ВХІДНИЙ (більший) струм"),
        ("✗ flyback без снабера", "ключ згорить від викиду індуктивності витоку"),
        ("✗ помпа на проміжну напругу", "палить, як лінійний; узгодь кратність"),
    ]
    positions = [(50, 70), (490, 70), (50, 178), (490, 178), (50, 286), (490, 286)]
    for (title_t, body_t), (x, y) in zip(cards, positions):
        f.append(rect(x, y, 410, 92, fill=WARN_FILL, stroke=T_BOOST, sw=1.6, rx=10))
        f.append(text(x + 20, y + 30, title_t, size=12.5, color=T_BOOST, bold=True, anchor="start"))
        f.append(line(x + 20, y + 44, x + 390, y + 44, color="#e4e4e4", sw=1))
        f.append(text(x + 20, y + 66, body_t, size=10.5, color=INK, anchor="start"))
    render(os.path.join(OUT, "pitfalls.svg"), W, H, *f,
           title="Типові пастки вибору — чого не робити")


# ─────────────────────────────────────────────────────────────────────────────
def fig_cascade_efficiency():
    """Вставка про ККД ланцюга: каскад buck+LDO (61 %) проти одного buck (90 %)."""
    W, H = 900, 420
    f = []

    def node(cx, cy, pct, col):
        return circle(cx, cy, 26, fill="#ffffff", stroke=col, sw=2.4) + \
               text(cx, cy + 5, pct, size=13, color=col, bold=True)

    def stage(cx, cy, name, eta):
        out = rect(cx - 45, cy - 20, 90, 40, fill="#eaf0fd", stroke=T_BUCK, sw=1.8)
        out += text(cx, cy - 1, name, size=10.5, color=T_BUCK, bold=True)
        out += text(cx, cy + 15, eta, size=10, color=INK)
        return out

    # верхній ряд — каскад
    f.append(text(70, 70, "Каскад buck + LDO:", size=13, color=INK, bold=True, anchor="start"))
    f.append(node(110, 130, "100%", INK))
    f.append(line(136, 130, 200, 130, color=INK, sw=2))
    f.append(stage(245, 130, "buck→5В", "η=0.92"))
    f.append(line(290, 130, 360, 130, color=INK, sw=2))
    f.append(node(390, 130, "92%", T_BB))
    f.append(line(416, 130, 480, 130, color=INK, sw=2))
    f.append(stage(525, 130, "LDO→3.3В", "η=0.66"))
    f.append(line(570, 130, 640, 130, color=INK, sw=2))
    f.append(node(672, 130, "61%", T_BOOST))
    f.append(arrow(245, 152, 245, 178, color=T_BOOST))
    f.append(text(245, 196, "−8% тепло", size=9.5, color=T_BOOST))
    f.append(arrow(525, 152, 525, 178, color=T_BOOST))
    f.append(text(525, 196, "LDO палить різницю напруг!", size=9.5, color=T_BOOST))
    f.append(text(745, 130, "→ 61%", size=14, color=T_BOOST, bold=True, anchor="start"))
    f.append(text(745, 148, "0.92×0.66", size=10, color=MUTED, anchor="start"))

    # нижній ряд — один buck
    f.append(text(70, 250, "Один buck:", size=13, color=INK, bold=True, anchor="start"))
    f.append(node(110, 300, "100%", INK))
    f.append(line(136, 300, 270, 300, color=INK, sw=2))
    f.append(stage(320, 300, "buck 12→3.3В", "η=0.90"))
    f.append(line(365, 300, 640, 300, color=INK, sw=2))
    f.append(node(672, 300, "90%", T_BB))
    f.append(arrow(320, 322, 320, 348, color=T_BOOST))
    f.append(text(320, 366, "−10% тепло", size=9.5, color=T_BOOST))
    f.append(text(745, 300, "→ 90%", size=14, color=T_BB, bold=True, anchor="start"))

    f.append(rect(70, 384, 760, 26, fill=GOOD_FILL, stroke=T_BB, sw=1.4, rx=8))
    f.append(text(450, 402,
                  "Один добрий перетворювач (90%) б'є каскад buck+LDO (61%): зайвий каскад, надто лінійний, з'їдає десятки відсотків",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "cascade-efficiency.svg"), W, H, *f,
           title="ККД ланцюга = добуток ККД каскадів (не сума)")


# ─────────────────────────────────────────────────────────────────────────────
def fig_conversion_ratios():
    """Криві M(D) для buck, boost, buck-boost — з балансу вольт-секунд.
    Показує природний напрямок кожної топології й зони-краї (D→0, D→1)."""
    W, H = 900, 520
    L, R, T, B = 100, 690, 70, 430          # межі поля графіка
    Dmin, Dmax = 0.0, 1.0
    Mmax = 6.0                               # стеля осі M (обрізаємо злети)

    def px(d):                               # D → екранний x
        return L + (d - Dmin) / (Dmax - Dmin) * (R - L)

    def py(m):                               # M → екранний y (обрізаємо до Mmax)
        m = min(m, Mmax)
        return B - m / Mmax * (B - T)

    f = []
    # осі
    f.append(arrow(L, B, R + 8, B, color=INK, sw=1.6))
    f.append(arrow(L, B, L, T - 8, color=INK, sw=1.6))
    f.append(text(R - 40, B + 30, "D (заповнення) →", size=11, color=INK, bold=True))
    f.append(text(L - 10, T - 4, "M = Vвих/Vвх", size=11, color=INK, bold=True, anchor="end"))
    # сітка по x
    for d in [0.0, 0.25, 0.5, 0.75, 1.0]:
        x = px(d)
        f.append(line(x, B, x, B + 5, color=MUTED, sw=1))
        f.append(text(x, B + 20, "%.2f" % d, size=9.5, color=MUTED))
    # сітка по M
    for m in [1, 2, 3, 4, 5, 6]:
        y = py(m)
        f.append(line(L - 5, y, L, y, color=MUTED, sw=1))
        f.append(text(L - 10, y + 4, str(m), size=9.5, color=MUTED, anchor="end"))
        if m == 1:                            # лінія M=1 — межа вниз/вгору
            f.append(line(L, y, R, y, color="#d0d0d0", sw=1, dash="4,4"))
            f.append(text(R - 4, y - 6, "M=1 (вхід=вихід)", size=9, color=MUTED, anchor="end"))

    # затінені краї (куди не заходять)
    f.append(rect(px(0.0), T, px(0.06) - px(0.0), B - T, fill="#f3f3f3", stroke="none", sw=0))
    f.append(rect(px(0.87), T, px(1.0) - px(0.87), B - T, fill="#f3f3f3", stroke="none", sw=0))
    f.append(text(px(0.93), T + 16, "край", size=9, color=MUTED, italic=True))
    f.append(text(px(0.93), T + 30, "D→1", size=9, color=MUTED, italic=True))

    def polyline(pts, col, sw=2.6):
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw)

    steps = 200
    # buck: M = D (пряма під 45° у масштабі)
    buck = [(px(i / steps), py(i / steps)) for i in range(steps + 1)]
    f.append(polyline(buck, T_BUCK))
    # boost: M = 1/(1−D), обрізаємо там, де вилітає за Mmax
    boost = []
    for i in range(steps + 1):
        d = i / steps
        if d >= 0.995:
            break
        m = 1.0 / (1.0 - d)
        boost.append((px(d), py(m)))
        if m >= Mmax:
            break
    f.append(polyline(boost, T_BOOST))
    # buck-boost за модулем: |M| = D/(1−D)
    bb = []
    for i in range(steps + 1):
        d = i / steps
        if d >= 0.995:
            break
        m = d / (1.0 - d)
        bb.append((px(d), py(m)))
        if m >= Mmax:
            break
    f.append(polyline(bb, T_BB))

    # мітка точки перелому buck-boost при D=0.5, M=1
    f.append(circle(px(0.5), py(1.0), 4, fill=T_BB, stroke=T_BB, sw=0))
    f.append(text(px(0.5), py(1.0) - 12, "D=0.5", size=9, color=T_BB, bold=True))

    # легенда
    lx, ly = 700, 90
    items = [("buck: M = D", T_BUCK), ("boost: M = 1/(1−D)", T_BOOST),
             ("buck-boost: |M| = D/(1−D)", T_BB)]
    for i, (lbl, col) in enumerate(items):
        yy = ly + i * 26
        f.append(line(lx, yy, lx + 24, yy, color=col, sw=3))
        f.append(text(lx + 30, yy + 4, lbl, size=10.5, color=col, bold=True, anchor="start"))
    f.append(rect(695, 168, 195, 92, fill=GOOD_FILL, stroke=T_BB, sw=1.3, rx=8))
    f.append(mtext(792, 186,
                   ["buck замкнений під M=1;",
                    "boost злітає при D→1;",
                    "buck-boost = 1 при D=0.5"],
                   size=10, color=INK, lh=1.35))

    render(os.path.join(OUT, "conversion-ratios.svg"), W, H, *f,
           title="Коефіцієнт перетворення M(D): форма кривої диктує напрямок")


# ─────────────────────────────────────────────────────────────────────────────
def fig_boost_real_ratio():
    """Реальний M(D) boost із паразитним опором: злітає до стелі, тоді ПАДАЄ.
    Показує, чому boost не дає нескінченного підвищення (вставка math)."""
    W, H = 900, 520
    L, R, T, B = 100, 660, 70, 430
    Dmax = 1.0
    Mmax = 12.0                              # стеля осі M

    def px(d):
        return L + d / Dmax * (R - L)

    def py(m):
        m = min(m, Mmax)
        return B - m / Mmax * (B - T)

    f = []
    # осі
    f.append(arrow(L, B, R + 8, B, color=INK, sw=1.6))
    f.append(arrow(L, B, L, T - 8, color=INK, sw=1.6))
    f.append(text(R - 40, B + 30, "D (заповнення) →", size=11, color=INK, bold=True))
    f.append(text(L - 10, T - 4, "M = Vвих/Vвх", size=11, color=INK, bold=True, anchor="end"))
    for d in [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]:
        x = px(d)
        f.append(line(x, B, x, B + 5, color=MUTED, sw=1))
        f.append(text(x, B + 20, "%.2f" % d, size=9.5, color=MUTED))
    for m in [2, 4, 6, 8, 10, 12]:
        y = py(m)
        f.append(line(L - 5, y, L, y, color=MUTED, sw=1))
        f.append(text(L - 10, y + 4, str(m), size=9.5, color=MUTED, anchor="end"))

    def polyline(pts, col, sw=2.6, dash=None):
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, da)

    steps = 300
    # ідеальний boost: M = 1/(1−D) — злітає в нескінченність
    ideal = []
    for i in range(steps + 1):
        d = i / steps
        if d >= 0.94:
            break
        m = 1.0 / (1.0 - d)
        ideal.append((px(d), py(m)))
        if m >= Mmax:
            break
    f.append(polyline(ideal, MUTED, sw=1.8, dash="5,4"))

    # реальний boost: M = (1/(1−D)) · 1/(1 + r/(R·(1−D)²)), r/R = 0.02 (типове)
    rr = 0.02
    real = []
    for i in range(steps + 1):
        d = i / steps
        if d >= 0.999:
            break
        m = (1.0 / (1.0 - d)) * (1.0 / (1.0 + rr / ((1.0 - d) ** 2)))
        real.append((px(d), py(m)))
    f.append(polyline(real, T_BOOST, sw=3.0))
    # позначка піку: (1−D)² = r/R → D* = 1 − √(r/R)
    import math as _m
    dstar = 1.0 - _m.sqrt(rr)
    mstar = (1.0 / (1.0 - dstar)) * (1.0 / (1.0 + rr / ((1.0 - dstar) ** 2)))
    f.append(circle(px(dstar), py(mstar), 5, fill=T_BOOST, stroke=T_BOOST, sw=0))
    f.append(text(px(dstar), py(mstar) - 12, "пік M ≈ %.1f" % mstar, size=10, color=T_BOOST, bold=True))
    f.append(text(px(dstar), py(mstar) - 26, "при D ≈ %.2f" % dstar, size=9, color=T_BOOST))

    # затінена «стіна» D→1
    f.append(rect(px(0.9), T, px(1.0) - px(0.9), B - T, fill="#f3f3f3", stroke="none", sw=0))
    f.append(text(px(0.95), B - 14, "D→1:", size=9, color=MUTED, italic=True))
    f.append(text(px(0.95), B - 2, "M→0", size=9, color=T_BOOST, italic=True))

    # легенда
    lx, ly = 470, 96
    f.append(line(lx, ly, lx + 26, ly, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text(lx + 32, ly + 4, "ідеал  M = 1/(1−D)  → ∞", size=10.5, color=MUTED, anchor="start"))
    f.append(line(lx, ly + 22, lx + 26, ly + 22, color=T_BOOST, sw=3))
    f.append(text(lx + 32, ly + 26, "реальний boost (r/R = 2 %)", size=10.5, color=T_BOOST, bold=True, anchor="start"))

    f.append(rect(465, 138, 190, 96, fill=WARN_FILL, stroke=T_BOOST, sw=1.3, rx=8))
    f.append(mtext(560, 156,
                   ["паразитний опір r",
                    "тягне M донизу; після",
                    "піку зростання D тільки",
                    "ЗМЕНШУЄ вихід — «стіна»"],
                   size=9.6, color=INK, lh=1.35))

    render(os.path.join(OUT, "boost-real-ratio.svg"), W, H, *f,
           title="Реальний boost: M злітає, тоді ПАДАЄ — нескінченного підвищення немає")


# ─────────────────────────────────────────────────────────────────────────────
def fig_isolated_lineage():
    """Родовід ізольованих: одна ідея (рвати струм у котушці) через п'ять епох."""
    W, H = 940, 560
    f = []
    # спільна ідея зверху
    f.append(rect(70, 58, 800, 40, fill="#fbf7ec", stroke=INK, sw=1.8, rx=10))
    f.append(text(470, 83,
                  "Одна ідея: різко РВАТИ струм у котушці → сплеск напруги; трансформатор дає й розв'язку, й кратність витком",
                  size=11, color=INK, bold=True))

    stages = [
        ("1836", "Індукційна котушка", "Каллан (Maynooth):\nрвемо струм у первинній —\nвисока напруга у вторинній", NEG, "#eaf0fd"),
        ("1853", "Конденсатор на розрив", "Фізо: C через переривач\nрве струм ШВИДШЕ →\nвищий сплеск, менша іскра", T_PUMP, "#faf3e0"),
        ("1910", "Запалювання Delco", "Кеттерінг: котушка + контакти\n+ конденсатор — по суті\nflyback на механічних контактах", T_BOOST, "#fdecea"),
        ("1940-і", "Блокінг-генератор", "У розгортці ТБ: котушка сама\nсебе рве й перезапускає —\nсамозбудний, без зовн. такту", T_BB, "#e9f7ee"),
        ("сьогодні", "RCC → flyback", "«Дзвінкий» самозбудний RCC\nживить дешеві зарядки <150 Вт;\nз контролером — сучасний flyback", T_ISO, "#f1e9f8"),
    ]
    n = len(stages)
    x0, dx = 90, 172
    ytop = 150
    for i, (yr, name, body, col, lite) in enumerate(stages):
        cx = x0 + i * dx
        # маркер року на стрічці часу
        f.append(circle(cx, ytop, 7, fill=col, stroke=col, sw=0))
        f.append(text(cx, ytop - 16, yr, size=12, color=col, bold=True))
        if i < n - 1:
            f.append(arrow(cx + 9, ytop, cx + dx - 9, ytop, color=MUTED, sw=1.6))
        # картка етапу
        f.append(rect(cx - 78, ytop + 26, 156, 150, fill=lite, stroke=col, sw=1.8, rx=8))
        f.append(text(cx, ytop + 48, name, size=11.5, color=col, bold=True))
        f.append(line(cx - 62, ytop + 58, cx + 62, ytop + 58, color="#dcdcdc", sw=1))
        f.append(mtext(cx, ytop + 76, body, size=9.3, color=INK, lh=1.32))
    # стрічка часу
    f.append(line(x0, ytop, x0 + (n - 1) * dx, ytop, color=MUTED, sw=1.4))

    # висновок унизу
    f.append(rect(70, 470, 800, 62, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=10))
    f.append(mtext(470, 493,
                   ["Трансформатор робить дві роботи ОДНИМ осердям: розділяє кола бар'єром ізоляції",
                    "і множить напругу відношенням витків Nвтор/Nперв — тому мережеві зарядки саме ізольовані."],
                   size=10.5, color=INK, lh=1.4))
    render(os.path.join(OUT, "isolated-lineage.svg"), W, H, *f,
           title="Родовід ізольованих топологій: одна ідея крізь епохи")


# ─────────────────────────────────────────────────────────────────────────────
def fig_rcc_cycle():
    """Самозбудний цикл RCC: чому він «дзвенить» і перезапускається сам."""
    W, H = 900, 480
    cx, cy, R = 300, 268, 120
    f = []
    import math
    # чотири фази по колу; підпис виноситься по осі назовні (dir = ±1 по x/y)
    phases = [
        ("1. Ключ ВІДКРИТО", ["струм у первинній росте,", "енергія тече в осердя"],
         NEG, -90, (0, -1)),
        ("2. Допоміжний виток", ["наведена напруга ще дужче", "відкриває ключ (додатн. ЗЗ)"],
         T_BB, 0, (1, 0)),
        ("3. Осердя насичується", ["струм більше не росте → ЗЗ", "зникає → ключ ЗАКРИВАЄТЬСЯ"],
         T_BOOST, 90, (0, 1)),
        ("4. Скид у вихід + «дзвін»", ["енергія летить у вихід; коли", "струм спав до 0 — виток", "дзвенить і знову відкриває ключ"],
         T_PUMP, 180, (-1, 0)),
    ]
    for i, (name, body, col, ang, (dxu, dyu)) in enumerate(phases):
        a = math.radians(ang)
        px = cx + R * math.cos(a)
        py = cy + R * math.sin(a)
        f.append(circle(px, py, 28, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(px, py + 5, str(i + 1), size=16, color=col, bold=True))
        # підпис за вузлом уздовж осі назовні (не залазить у заголовок/краї)
        lx = px + dxu * 40
        ly = py + dyu * 66
        anch = "start" if dxu > 0 else ("end" if dxu < 0 else "middle")
        head_y = ly - (len(body)) * 6 - 6
        f.append(text(lx, head_y, name, size=11, color=col, bold=True, anchor=anch))
        f.append(mtext(lx, head_y + 15, body, size=9.2, color=INK, lh=1.32, anchor=anch))
    # дуги-стрілки по колу (за годинниковою)
    for ang in (-90, 0, 90, 180):
        a1 = math.radians(ang + 22)
        a2 = math.radians(ang + 68)
        x1 = cx + R * math.cos(a1); y1 = cy + R * math.sin(a1)
        x2 = cx + R * math.cos(a2); y2 = cy + R * math.sin(a2)
        f.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (x1, y1, R, R, x2, y2, MUTED))
    f.append(text(cx, cy - 6, "RCC", size=15, color=INK, bold=True))
    f.append(text(cx, cy + 12, "сам себе тактує", size=9.5, color=MUTED))

    # права колонка: чому дешево
    bx = 610
    f.append(rect(bx, 90, 270, 300, fill="#faf3e0", stroke=T_PUMP, sw=1.6, rx=10))
    f.append(text(bx + 135, 116, "Чому RCC такий дешевий", size=12, color=T_PUMP, bold=True))
    f.append(line(bx + 20, 128, bx + 250, 128, color="#dcdcdc", sw=1))
    f.append(mtext(bx + 20, 152,
                   ["• немає контролера — котушка сама",
                    "  вирішує, коли перемикати;",
                    "",
                    "• один ключ, один трансформатор,",
                    "  кілька копійчаних деталей;",
                    "",
                    "• частота «плаває» з навантаженням —",
                    "  для зарядки байдуже;",
                    "",
                    "• ізоляція й кратність — задарма,",
                    "  просто витками трансформатора."],
                   size=9.8, color=INK, lh=1.42, anchor="start"))
    render(os.path.join(OUT, "rcc-cycle.svg"), W, H, *f,
           title="RCC: котушка сама тактує себе — тому копійчаний")


# ─────────────────────────────────────────────────────────────────────────────
def fig_flying_cap_path():
    """Вставка math-wide-input-topologies: шлях струму на вихід.
    Ліворуч buck — постійна складова котушкою повз C; праворуч SEPIC/Ćuk —
    увесь заряд крізь перекидний конденсатор послідовно."""
    W, H = 940, 430
    f = []

    def coil(x, y, col):
        d = "M %d %d q 8 -14 16 0 q 8 -14 16 0 q 8 -14 16 0" % (x, y)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col)

    def cap(cx, cy, col, sw=2.4):
        return (line(cx - 9, cy - 12, cx - 9, cy + 12, color=col, sw=sw) +
                line(cx + 9, cy - 12, cx + 9, cy + 12, color=col, sw=sw))

    # ── ліворуч: buck ──────────────────────────────────────────────
    f.append(text(235, 68, "BUCK: постійний струм несе котушка", size=13, color=T_BUCK, bold=True))
    f.append(text(235, 88, "конденсатор бере лише пульсацію", size=10.5, color=MUTED))
    f.append(rect(60, 120, 60, 34, fill="#eef0fb", stroke=T_BUCK, sw=1.8))
    f.append(text(90, 141, "Vвх", size=11, color=T_BUCK, bold=True))
    f.append(line(120, 137, 175, 137, color=INK, sw=2.4))
    f.append(coil(178, 137, T_BUCK))
    f.append(line(226, 137, 360, 137, color=INK, sw=2.4))
    f.append(rect(360, 120, 60, 34, fill=GOOD_FILL, stroke=T_BUCK, sw=1.8))
    f.append(text(390, 141, "Vвих", size=11, color=T_BUCK, bold=True))
    f.append(arrow(150, 112, 350, 112, color=T_BB, sw=3.2))
    f.append(text(250, 104, "весь постійний струм (гладкий)", size=10, color=T_BB, bold=True))
    f.append(line(340, 137, 340, 175, color=INK, sw=1.8))
    f.append(cap(340, 187, T_BUCK, sw=2.0))
    f.append(line(325, 205, 355, 205, color=INK, sw=2))
    f.append(line(330, 210, 350, 210, color=INK, sw=1.6))
    f.append(text(392, 191, "лише пульсація ↑", size=9.5, color=MUTED, anchor="start"))

    f.append(line(470, 70, 470, 300, color="#dddddd", sw=1.4, dash="5,5"))

    # ── праворуч: SEPIC / Ćuk ─────────────────────────────────────
    f.append(text(700, 68, "SEPIC / Ćuk: увесь заряд крізь Cp", size=13, color=T_BB, bold=True))
    f.append(text(700, 88, "послідовно на шляху — постійної складової не можна", size=10, color=MUTED))
    f.append(rect(510, 120, 55, 34, fill="#eef0fb", stroke=T_BB, sw=1.8))
    f.append(text(537, 141, "Vвх", size=11, color=T_BB, bold=True))
    f.append(line(565, 137, 600, 137, color=INK, sw=2.4))
    f.append(coil(603, 137, T_BB))
    f.append(text(627, 168, "L1", size=9.5, color=MUTED))
    f.append(line(651, 137, 690, 137, color=INK, sw=2.4))
    f.append(cap(700, 137, T_BOOST, sw=3.0))
    f.append(text(700, 112, "Cp", size=12, color=T_BOOST, bold=True))
    f.append(line(710, 137, 748, 137, color=INK, sw=2.4))
    f.append(coil(751, 137, T_BB))
    f.append(text(775, 168, "L2", size=9.5, color=MUTED))
    f.append(line(799, 137, 835, 137, color=INK, sw=2.4))
    f.append(rect(835, 120, 55, 34, fill=GOOD_FILL, stroke=T_BB, sw=1.8))
    f.append(text(862, 141, "Vвих", size=11, color=T_BB, bold=True))
    f.append(arrow(660, 112, 745, 112, color=T_BOOST, sw=3.2))
    f.append(text(703, 235, "весь струм на вихід тече крізь Cp", size=10.5, color=T_BOOST, bold=True))
    f.append(text(703, 253, "лише змінним → Cp гріється (I²·ESR)", size=10.5, color=T_BOOST, bold=True))

    f.append(rect(70, 300, 800, 40, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=8))
    f.append(mtext(470, 316,
                   ["У buck постійний струм «безкоштовно» несе котушка, а конденсатор лише згладжує.",
                    "У SEPIC/Ćuk перекидний конденсатор — на самому шляху передачі, і весь перенос лягає на його змінний струм."],
                   size=10.5, color=INK, lh=1.35))
    render(os.path.join(OUT, "flying-cap-path.svg"), W, H, *f,
           title="Шлях струму на вихід: котушка (buck) проти перекидного конденсатора (SEPIC/Ćuk)")


# ─────────────────────────────────────────────────────────────────────────────
def fig_ripple_compare():
    """Пульсації трьох топологій на вході (згори) та виході (знизу).
    Ćuk гладко з обох боків; SEPIC гладкий вхід / рваний вихід; 4-ключ. — за режимом."""
    W, H = 940, 470
    f = []
    cols = [("Ćuk", 235, T_BB), ("SEPIC", 470, T_BB), ("4-ключовий", 705, T_BUCK)]

    def axis_box(cx, cy, w=190, h=64):
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill="#ffffff", stroke="#e0e0e0", sw=1.2))
        f.append(line(cx - w / 2 + 8, cy + h / 2 - 8, cx + w / 2 - 8, cy + h / 2 - 8,
                      color=MUTED, sw=1))

    def wave(cx, cy, kind, col):
        x0, x1 = cx - 82, cx + 82
        base = cy + 22
        pts = []
        if kind == "smooth":
            lvl = cy - 4
            n = 6
            for i in range(n + 1):
                xx = x0 + (x1 - x0) * i / n
                yy = lvl + (-6 if i % 2 == 0 else 6)
                pts.append((xx, yy))
        else:  # chop — струм росте й падає до нуля (рваний)
            n = 4
            for i in range(n):
                xa = x0 + (x1 - x0) * i / n
                xb = x0 + (x1 - x0) * (i + 1) / n
                pts.append((xa, base))
                pts.append((xa + (xb - xa) * 0.55, cy - 12))
                pts.append((xb, base))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col)

    for name, cx, col in cols:
        f.append(rect(cx - 95, 66, 190, 30, fill=GOOD_FILL, stroke=col, sw=1.6))
        f.append(text(cx, 86, name, size=13, color=col, bold=True))

    f.append(text(60, 150, "струм ВХОДУ", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(60, 300, "струм ВИХОДУ", size=12, color=INK, bold=True, anchor="start"))

    kinds_in = {"Ćuk": "smooth", "SEPIC": "smooth", "4-ключовий": "chop"}
    kinds_out = {"Ćuk": "smooth", "SEPIC": "chop", "4-ключовий": "chop"}
    notes_in = {"Ćuk": "гладко (котушка на вході)",
                "SEPIC": "гладко (котушка на вході)",
                "4-ключовий": "рвано у buck-режимі"}
    notes_out = {"Ćuk": "гладко (котушка на виході)",
                 "SEPIC": "рвано (діод рве струм)",
                 "4-ключовий": "рвано у boost-режимі"}
    for name, cx, col in cols:
        axis_box(cx, 155)
        f.append(wave(cx, 143, kinds_in[name], col))
        f.append(text(cx, 194, notes_in[name], size=9.5, color=MUTED))
        axis_box(cx, 305)
        f.append(wave(cx, 293, kinds_out[name], col))
        f.append(text(cx, 344, notes_out[name], size=9.5, color=MUTED))

    f.append(rect(70, 388, 800, 56, fill=GOOD_FILL, stroke=T_BB, sw=1.5, rx=8))
    f.append(mtext(470, 406,
                   ["Ćuk: котушка послідовна з кожним портом → гладко з обох боків (найтихіший), ціна — від'ємний вихід.",
                    "SEPIC: вхід гладкий, вихід рве діод. 4-ключовий: гладкий той бік, що зараз не перемикається;",
                    "перевагу «гладко з обох боків» він не має, зате вищий ККД (немає гарячого перекидного конденсатора)."],
                   size=10, color=INK, lh=1.35))
    render(os.path.join(OUT, "ripple-compare.svg"), W, H, *f,
           title="Пульсації трьох топологій: де струм гладкий, а де рваний")


if __name__ == "__main__":
    fig_decision_tree()
    fig_power_map()
    fig_recognize_board()
    fig_secondary_axes()
    fig_tradeoffs()
    fig_pitfalls()
    fig_cascade_efficiency()
    fig_conversion_ratios()
    fig_boost_real_ratio()
    fig_isolated_lineage()
    fig_rcc_cycle()
    fig_flying_cap_path()
    fig_ripple_compare()
    print("ok figs: 13 файлів у img/")
