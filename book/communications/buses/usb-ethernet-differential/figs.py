# -*- coding: utf-8 -*-
"""Фігури до теми «Диференційні пари USB та Ethernet».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Контрольований імпеданс: 90 Ω для USB, 100 Ω для Ethernet ─────────────
def fig_impedance_targets():
    W, H = 780, 460
    f = [text(W / 2, 28, "Геометрія пари задає диференційний імпеданс: USB ≈ 90 Ω, Ethernet ≈ 100 Ω",
              size=15, bold=True)]

    # спільне пояснення: переріз плати (дві доріжки над опорним шаром)
    def stackup(cx, title, sub, color, gap_txt):
        # опорний шар (земля)
        f.append(line(cx - 110, 200, cx + 110, 200, color=MUTED, sw=3.0))
        f.append(text(cx, 218, "опорний шар (GND)", size=10.5, color=MUTED))
        # діелектрик
        f.append(rect(cx - 110, 150, 220, 50, fill="#f1f3f5", stroke="#d0d4d8", sw=1.0, rx=2))
        f.append(text(cx + 96, 178, "FR-4", size=9.5, color=MUTED, anchor="end"))
        # дві доріжки пари
        f.append(rect(cx - 46, 142, 30, 10, fill=color, stroke=color, sw=1.0, rx=2))
        f.append(rect(cx + 16, 142, 30, 10, fill=color, stroke=color, sw=1.0, rx=2))
        f.append(text(cx - 31, 134, "+", size=12, bold=True, color=color))
        f.append(text(cx + 31, 134, "−", size=12, bold=True, color=color))
        # розмір проміжку
        f.append(line(cx - 16, 158, cx + 16, 158, color=INK, sw=1.0))
        f.append(text(cx, 172, gap_txt, size=10, color=INK))
        # заголовок панелі
        f.append(text(cx, 96, title, size=14, bold=True, color=color))
        f.append(text(cx, 114, sub, size=11, color=MUTED))

    stackup(210, "USB 2.0  (D+ / D−)", "ціль ≈ 90 Ω диференційно", NEG, "вужчий проміжок")
    stackup(570, "Ethernet  (вита пара)", "ціль ≈ 100 Ω диференційно", FIELD, "ширший проміжок")

    f.append(line(390, 88, 390, 232, color="#d0d4d8", sw=1.2, dash="4,4"))

    box = fitbox(70, 270, 640, 150, [
                 "Імпеданс пари визначає НЕ протокол, а геометрія: ширина двох доріжок,",
                 "проміжок між ними, товщина діелектрика до опорного шару й сам діелектрик.",
                 "Цифри в стандартах — це просто домовлені цілі, під які зведено цю геометрію:",
                 "USB 2.0 цілить у 90 Ω між D+ і D−, Ethernet — у 100 Ω у кожній парі.",
                 "Відступив від геометрії — попливла ціль, на стрибку імпедансу хвиля частково",
                 "відбивається назад відлунням, і швидка лінія починає збоїти. Тому в правилах",
                 "розведення стоїть конкретне число, а не «приблизно»."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "impedance-targets.svg"), W, H, *f)


# ── 2. Узгодження довжин усередині пари: перекіс і міандр ────────────────────
def fig_length_match():
    W, H = 780, 470
    f = [text(W / 2, 28, "Дроти пари ведуть однакової довжини: інакше фронти приходять урозбіг",
              size=15, bold=True)]

    # --- ліворуч: пара з різною довжиною (поганий випадок) ---
    f.append(text(205, 60, "Один дріт довший — перекіс", size=13.5, bold=True, color=POS))
    # прямий дріт +
    f.append(line(80, 100, 330, 100, color=NEG, sw=2.4))
    f.append(text(74, 96, "+", size=13, bold=True, anchor="end", color=NEG))
    # дріт − з петлею-обходом (довший за дріт +)
    f.append('<path d="M80,150 L150,150 L165,128 L210,128 L225,150 L330,150" '
             'fill="none" stroke="%s" stroke-width="2.4"/>' % POS)
    f.append(text(74, 146, "−", size=13, bold=True, anchor="end", color=POS))
    f.append(text(195, 124, "обхід перешкоди → довший шлях", size=10, color=POS))
    # на приймачі — зсув приходу
    f.append(line(330, 90, 330, 160, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(205, 182, "фронт «−» спізнюється на Δt", size=11, color=POS, anchor="middle"))
    # мить хибної різниці
    f.append(text(205, 200, "у мить переходу A − B на мить хибна", size=10.5, color=POS, anchor="middle"))

    f.append(line(400, 72, 400, 230, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- праворуч: вирівняно міандром (добрий випадок) ---
    f.append(text(590, 60, "Коротший підтягнуто міандром", size=13.5, bold=True, color=FIELD))
    f.append(line(470, 100, 720, 100, color=NEG, sw=2.4))
    f.append(text(464, 96, "+", size=13, bold=True, anchor="end", color=NEG))
    # дріт − з міандром-доважкою + далі обхід
    f.append('<path d="M470,150 L500,150 L500,138 L515,138 L515,150 L530,150 L530,138 '
             'L545,138 L545,150 L600,150 L615,128 L640,128 L655,150 L720,150" '
             'fill="none" stroke="%s" stroke-width="2.4"/>' % FIELD)
    f.append(text(580, 124, "зиґзаґ-доважка зрівнює довжину", size=10, color=FIELD))
    f.append(line(720, 90, 720, 160, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(590, 182, "обидва фронти приходять разом", size=11, color=FIELD, anchor="middle"))
    f.append(text(590, 200, "різниця A − B чиста на переході", size=10.5, color=FIELD, anchor="middle"))

    box = fitbox(70, 265, 640, 158, [
                 "Біт живе в різниці A − B, і вона чиста лише доки фронти на обох дротах",
                 "перемикаються одночасно. Фронт біжить дротом зі скінченною швидкістю, тож",
                 "довший дріт доносить свій фронт пізніше — це перекіс (skew). У мить переходу,",
                 "поки один дріт уже змінив рівень, а другий ще ні, різниця на коротку мить",
                 "провалюється й стає хибною. На повільній лінії ця щілина мізерна, на швидкій —",
                 "доростає до помилки. Тому коротшу доріжку навмисне подовжують зиґзаґом",
                 "(міандром), щоб обидві стали однакової довжини. Для USB це доли міліметра,",
                 "для багатопарного Ethernet вирівнюють ще й пари між собою."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "length-match.svg"), W, H, *f)


# ── 3. Магнетика Ethernet: трансформатор на кінці витих пар ──────────────────
def fig_ethernet_magnetics():
    W, H = 780, 450
    f = [text(W / 2, 28, "Ethernet вмикає кожну виту пару через трансформатор",
              size=15, bold=True)]

    # PHY ліворуч
    pb = textbox(110, 150, ["PHY", "(приймач-", "передавач)"], size=12, fill="#eef2f7", min_w=110)
    f.append(pb[0])

    # дві лінії від PHY до первинної обмотки
    f.append(line(165, 130, 250, 130, color=POS, sw=2.2))
    f.append(line(165, 170, 250, 170, color=NEG, sw=2.2))

    # трансформатор: дві котушки (горбики) + осердя (дві лінії)
    def coil(x, y, color):
        d = "M%d,%d" % (x, y - 18)
        for i in range(3):
            yy = y - 18 + i * 12
            d += " q 14,6 0,12"
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color))
    coil(252, 150, POS)
    coil(290, 150, FIELD)
    # осердя
    f.append(line(268, 128, 268, 172, color=INK, sw=1.4))
    f.append(line(274, 128, 274, 172, color=INK, sw=1.4))
    f.append(text(271, 196, "трансформатор", size=11, color=INK))
    f.append(text(271, 211, "(магнетика)", size=10, color=MUTED))

    # вторинна → роз'єм RJ45 → кабель
    f.append(line(292, 130, 380, 130, color=FIELD, sw=2.2))
    f.append(line(292, 170, 380, 170, color=FIELD, sw=2.2))
    jb = textbox(420, 150, ["RJ45"], size=12, fill="#eef7f0", stroke=FIELD, min_w=70)
    f.append(jb[0])
    # вита пара в кабель
    def wavy(x1, x2, y, color, phase):
        steps = 70
        path = []
        for k in range(steps + 1):
            xx = x1 + (x2 - x1) * k / steps
            yy = y + 7 * math.sin(k * 0.7 + phase)
            path.append("%s%.1f,%.1f" % ("M" if k == 0 else "L", xx, yy))
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path), color))
    wavy(458, 700, 138, FIELD, 0)
    wavy(458, 700, 162, FIELD, math.pi)
    f.append(text(580, 118, "вита пара в кабелі →", size=11, color=FIELD))

    box = fitbox(70, 250, 640, 178, [
                 "Корисний сигнал пари — диференційний, тож трансформатор пропускає його",
                 "майже без втрат: протифазні струми в обмотці створюють поле, що передається",
                 "у вторинну. Натомість магнетика дає три речі, потрібні саме на довгому кабелі.",
                 "Перше — гальванічна розв'язка: між платою і кабелем немає прямого мідного",
                 "шляху, тож різниця потенціалів земель двох пристроїв (а на сотні метрів вона",
                 "велика) не тече крізь схему й нічого не палить. Друге — синфазний дросель",
                 "у складі магнетики додатково тисне спільну заваду, що однаково сидить на",
                 "обох жилах. Третє — постійна складова не проходить крізь трансформатор,",
                 "тож зсув земель не зрушує робочу точку приймача. Тому Ethernet терпить",
                 "і грозові наводки, і десятки метрів між «землями» двох пристроїв."],
                 size=12, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "ethernet-magnetics.svg"), W, H, *f)


# ── 4. Типові граблі розведення диференційної пари ───────────────────────────
def fig_routing_pitfalls():
    W, H = 780, 470
    f = [text(W / 2, 28, "Типові граблі розведення: усе, що порушує однаковість або сталу геометрію",
              size=14.5, bold=True)]

    rows = [
        ("Розвели дроти різними шляхами",
         "пара перестала бути парою: завада сідає нерівно,", "синфазне придушення просідає", POS),
        ("Розрив опорного шару під парою",
         "під доріжками щілина в землі → стрибок імпедансу", "і відлуння на швидкості", POS),
        ("Перехідний отвір (via) лише на одному дроті",
         "один дріт подовжився й змінив імпеданс — асиметрія,", "якої не було в плані", POS),
        ("Залишковий «хвіст» (stub) на лінії",
         "відгалуження-тупик відбиває хвилю назад", "і спотворює фронт", POS),
        ("Гострий поворот під 90°",
         "у куті змінюється ширина → локальний стрибок Z₀;", "ведуть плавно, двома кутами по 45°", POS),
    ]
    y = 70
    for title, l1, l2, col in rows:
        f.append(rect(70, y, 640, 64, fill="#fdf2f0", stroke=POS, sw=1.2, rx=6))
        f.append(text(86, y + 22, "✗  " + title, size=12.5, bold=True, color=POS, anchor="start"))
        f.append(text(104, y + 40, l1, size=11, color=INK, anchor="start"))
        f.append(text(104, y + 56, l2, size=11, color=MUTED, anchor="start"))
        y += 76

    render(os.path.join(IMG, "routing-pitfalls.svg"), W, H, *f)


if __name__ == "__main__":
    fig_impedance_targets()
    fig_length_match()
    fig_ethernet_magnetics()
    fig_routing_pitfalls()
    print("OK: figures written to", IMG)
