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


if __name__ == "__main__":
    fig_decision_tree()
    fig_power_map()
    fig_recognize_board()
    fig_secondary_axes()
    fig_tradeoffs()
    fig_pitfalls()
    fig_cascade_efficiency()
    print("ok figs: 7 файлів у img/")
