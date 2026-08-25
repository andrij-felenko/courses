# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори-акценти цієї теми (поверх палітри svgkit):
SW   = "#0a8f3c"   # «качає»/увімкнено — зелене поле
OFF  = "#d98a00"   # вимкнено / котушка / бурштин
GREY = "#cdd0d5"   # неактивна гілка


def poly(pts, stroke, sw=2.0, fill="none"):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (s, fill, stroke, sw))


def coil(x, y, w, n=4, amp=11, stroke=OFF, sw=2.2):
    """Горизонтальна котушка з n арок завширшки w, центр по y."""
    step = w / n
    d = "M %.1f %.1f " % (x, y)
    for i in range(n):
        cx = x + step * (i + 0.5)
        d += "q %.2f %.2f %.2f 0 " % (step / 2, -amp * 1.7, step)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, stroke, sw)


def vcoil(x, y0, y1, turns=6, amp=10, stroke="#b5763a", sw=2.6, right=False):
    """Вертикальна обмотка від y0 до y1."""
    h = (y1 - y0) / turns
    sweep = 1 if right else 0
    d = "M %.1f %.1f " % (x, y0)
    for i in range(turns):
        yy = y0 + h * (i + 1)
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (amp, h / 2, sweep, x, yy)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, stroke, sw)


def diode(cx, cy, color=INK, sw=2.0, scale=1.0):
    """Діод (трикутник + риска) вістрям донизу, центр (cx,cy)."""
    a = 11 * scale
    tri = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
           'stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>'
           % (cx - a, cy - a, cx + a, cy - a, cx, cy + a * 0.55, color, sw))
    bar = line(cx - a, cy + a * 0.55, cx + a, cy + a * 0.55, color=color, sw=sw + 0.4)
    return tri + bar


# ──────────────────────────────────────────────────────────────────────────────
# 1) Дві фази бак-перетворювача
# ──────────────────────────────────────────────────────────────────────────────
def fig_buck_phases():
    W, H = 980, 470
    p = []
    p.append(text(W / 2, 30, "Бак-перетворювач: дві фази качають енергію від входу до виходу",
                  size=18, bold=True))
    p.append(text(W / 2, 50, "ключ ВКЛ — котушка запасає енергію; ключ ВИКЛ — котушка віддає її через діод",
                  size=13, color=MUTED))

    def half(x0, title, tcol, on):
        f = [text(x0 + 225, 92, title, size=13, color=tcol, bold=True)]
        f.append(rect(x0, 105, 460, 320, fill=BG, stroke=MUTED, sw=1.0, rx=10))
        # джерело Vвх
        f.append(rect(x0 + 20, 150, 40, 92, fill="#eafaef", stroke=SW, sw=1.4))
        f.append(text(x0 + 40, 200, "Vвх", size=10, color=SW, bold=True))
        wire = SW if on else GREY
        # верхня гілка: джерело → ключ
        f.append(line(x0 + 60, 168, x0 + 102, 168, color=wire, sw=3 if on else 2))
        # ключ
        kf = "#d8f3e0" if on else BG
        kc = SW if on else INK
        f.append(rect(x0 + 102, 150, 56, 36, fill=kf, stroke=kc, sw=1.6))
        f.append(text(x0 + 130, 173, "ВКЛ" if on else "ВИКЛ", size=10, color=kc if on else OFF, bold=True))
        f.append(text(x0 + 130, 142, "ключ", size=9, color=MUTED))
        f.append(line(x0 + 158, 168, x0 + 215, 168, color=wire, sw=3 if on else 2))
        # вузол A
        f.append(circle(x0 + 215, 168, 3.5, fill=INK, stroke=INK, sw=1))
        f.append(text(x0 + 215, 156, "A", size=10, bold=True))
        # котушка
        f.append(coil(x0 + 223, 168, 92, n=4, amp=11, stroke=OFF, sw=2.2))
        f.append(text(x0 + 269, 150, "котушка L", size=9.5, color=OFF, bold=True))
        # вузол B → вихід
        f.append(line(x0 + 315, 168, x0 + 385, 168, color=SW, sw=3))
        f.append(circle(x0 + 385, 168, 3.5, fill=INK, stroke=INK, sw=1))
        f.append(text(x0 + 385, 156, "B", size=10, bold=True))
        f.append(line(x0 + 385, 168, x0 + 443, 168, color=SW, sw=3))
        f.append(text(x0 + 447, 160, "Vвих", size=10, color=SW, bold=True, anchor="start"))
        # конденсатор C
        f.append(line(x0 + 410, 168, x0 + 410, 240, color=SW, sw=2))
        f.append(line(x0 + 396, 242, x0 + 424, 242, color=INK, sw=3))
        f.append(line(x0 + 396, 252, x0 + 424, 252, color=INK, sw=3))
        f.append(line(x0 + 410, 254, x0 + 410, 380, color=SW, sw=2))
        f.append(text(x0 + 430, 250, "C", size=10, color=INK, bold=True, anchor="start"))
        # навантаження R
        f.append(rect(x0 + 430, 238, 26, 60, fill=BG, stroke=INK, sw=1.4, rx=4))
        f.append(text(x0 + 443, 273, "R", size=10, color=INK, bold=True))
        f.append(line(x0 + 443, 168, x0 + 443, 238, color=SW, sw=2))
        f.append(line(x0 + 443, 298, x0 + 443, 380, color=SW, sw=2))
        # земля
        f.append(line(x0 + 40, 242, x0 + 40, 380, color=SW, sw=2))
        f.append(line(x0 + 40, 380, x0 + 443, 380, color=SW, sw=2))
        # діод між землею і A
        dcol = SW if not on else GREY
        f.append(diode(x0 + 215, 300, color=dcol, sw=2.0))
        f.append(line(x0 + 215, 312, x0 + 215, 380, color=dcol, sw=3 if not on else 2))
        f.append(line(x0 + 215, 289, x0 + 215, 172, color=dcol, sw=3 if not on else 2))
        f.append(text(x0 + 200, 300, "діод", size=9, color=dcol, anchor="end"))
        f.append(text(x0 + 230, 300, "пропускає" if not on else "закритий",
                      size=9, color=dcol if not on else MUTED, anchor="start"))
        # підсумок фази
        f.append(text(x0 + 225, 410, "струм у котушці ↑ росте" if on else "струм у котушці ↓ спадає",
                      size=10.5, color=OFF, bold=True))
        return f

    p += half(15, "Фаза 1 — ключ ВКЛ", SW, True)
    p += half(505, "Фаза 2 — ключ ВИКЛ", OFF, False)
    p.append(text(W / 2, 458,
                  "Конденсатор тримає Vвих рівним між фазами; так енергія йде пакетами входу → вихід, майже не гріючи компонентів.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "buck-phases.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 2) Трикутна хвиля струму котушки + Vвих = Vвх × D
# ──────────────────────────────────────────────────────────────────────────────
def fig_inductor_current():
    W, H = 960, 440
    p = []
    p.append(text(W / 2, 30, "Струм котушки — трикутна хвиля; шпаруватість задає напругу",
                  size=18, bold=True))
    p.append(text(W / 2, 50, "росте, поки ключ ВКЛ; спадає, поки ВИКЛ; середнє = струм навантаження",
                  size=13, color=MUTED))
    # осі
    p.append(arrow(90, 340, 630, 340, color=INK, sw=1.4))
    p.append(text(630, 358, "час", size=10.5, color=INK, anchor="end"))
    p.append(arrow(90, 340, 90, 110, color=INK, sw=1.4))
    p.append(text(82, 116, "струм у котушці", size=10.5, color=INK, anchor="end", bold=True))
    # смуги ВКЛ/ВИКЛ
    p.append(rect(90, 120, 64, 220, fill="#eafaef", stroke="none", sw=0, rx=8))
    p.append(text(122, 136, "ВКЛ", size=9, color=SW, bold=True))
    p.append(rect(154, 120, 96, 220, fill="#fdf3e0", stroke="none", sw=0, rx=8))
    p.append(text(202, 136, "ВИКЛ", size=9, color=OFF, bold=True))
    # трикутна хвиля
    p.append(poly([(90, 290), (154, 190), (250, 290), (314, 190),
                   (410, 290), (474, 190), (570, 290)], OFF, sw=2.6))
    # середнє
    p.append(line(90, 240, 570, 240, color=SW, sw=1.6, dash="6 4"))
    p.append(text(98, 234, "середнє = струм навантаження", size=10, color=SW, anchor="start"))
    # розмах = пульсація
    p.append(line(586, 290, 586, 190, color=MUTED, sw=1.0))
    p.append(text(592, 244, "пульсація", size=9, color=MUTED, anchor="start"))
    # формула
    p.append(rect(640, 130, 280, 86, fill=FILL, stroke=INK, sw=1.3, rx=11))
    p.append('<text x="780" y="162" font-family="Consolas, monospace" font-size="16" '
             'fill="%s" text-anchor="middle" font-weight="700">Vвих = Vвх × D</text>' % INK)
    p.append(text(780, 190, "D = частка часу «ВКЛ»", size=11.5, color=INK))
    p.append(text(780, 207, "(шпаруватість)", size=10, color=MUTED))
    p.append(text(W / 2, 428,
                  "Більша шпаруватість D (довше «ВКЛ») → вища Vвих. Саме нею керують вихідною напругою.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "inductor-current.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 3) Шпаруватість → напруга + зворотний зв'язок
# ──────────────────────────────────────────────────────────────────────────────
def fig_duty_cycle():
    W, H = 960, 470
    p = []
    p.append(text(W / 2, 30, "Шпаруватість → напруга, а зворотний зв'язок тримає її сталою",
                  size=18, bold=True))
    p.append(text(W / 2, 50, "контролер міряє вихід і підкручує D — той самий контур «виміряти → порівняти → виправити»",
                  size=13, color=MUTED))
    p.append(text(180, 100, "(при Vвх = 16 В)", size=10, color=MUTED, anchor="start"))

    def train(y, duty, color, label):
        f = [('<text x="70" y="%d" font-family="Consolas, monospace" font-size="12" '
              'fill="%s" text-anchor="start" font-weight="700">D = %s</text>'
              % (y - 22, INK, ("%.2f" % duty).rstrip("0").rstrip(".")))]
        x0, x1 = 180, 480
        top, base = y - 32, y
        f.append(line(x0, base, x1, base, color=MUTED, sw=1.0))
        period = (x1 - x0) / 5.0
        for i in range(5):
            sx = x0 + i * period
            hi = sx + period * duty
            f.append(poly([(sx, base), (sx, top), (hi, top), (hi, base), (sx + period, base)],
                          color, sw=2.0))
        f.append(arrow(490, y - 16, 540, y - 16, color=INK, sw=2.0))
        f.append(rect(544, y - 18, 90, 38, fill=BG, stroke=color, sw=1.6, rx=8))
        f.append(text(589, y + 6, label, size=12, color=color, bold=True))
        return f

    p += train(150, 0.31, SW, "Vвих 5 В")
    p += train(228, 0.5, OFF, "Vвих 8 В")
    p += train(306, 0.75, POS, "Vвих 12 В")
    # рамка зворотного зв'язку
    p.append(rect(120, 360, 720, 76, fill="#eef2ff", stroke=NEG, sw=1.6, rx=12))
    p.append(text(140, 386, "Зворотний зв'язок:", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(140, 410,
                  "виміряти Vвих → порівняти з ціллю → підкрутити D → знову виміряти  (тримає вихід рівним, хоч би як стрибав вхід чи струм)",
                  size=11, color=INK, anchor="start"))
    p.append(text(W / 2, 462,
                  "Без зворотного зв'язку це був би просто «різак»; із ним — точний стабілізатор напруги.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "duty-cycle.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 4) Синхронний випрямляч і boost
# ──────────────────────────────────────────────────────────────────────────────
def fig_sync_boost():
    W, H = 980, 460
    p = []
    p.append(text(W / 2, 30, "Дві важливі варіації: менше втрат і підвищення напруги",
                  size=18, bold=True))
    p.append(text(W / 2, 50, "діод → другий MOSFET (ефективніше); інша схема → boost (вища напруга)",
                  size=13, color=MUTED))

    # ліва панель — синхронний випрямляч
    p.append(rect(40, 90, 440, 320, fill=BG, stroke=SW, sw=1.6, rx=12))
    p.append(text(260, 118, "Синхронний випрямляч", size=13, color=SW, bold=True))
    left = [
        "Діод завжди має падіння ~0.5 В —",
        "а на великому струмі це втрати й тепло.",
        "",
        "Замінюємо діод другим MOSFET:",
        "у нього опір міліоми → майже без втрат.",
        "",
        "Два ключі по черзі: верхній «качає»,",
        "нижній «замикає». ККД ще вищий.",
    ]
    yy = 152
    for ln in left:
        p.append(text(64, yy, ln, size=11, color=INK, anchor="start"))
        yy += 22
    p.append(rect(64, 360, 392, 34, fill="#eafaef", stroke=SW, sw=1.2, rx=8))
    p.append(text(260, 382, "так зроблено майже всі сучасні перетворювачі дрона",
                  size=10.5, color=SW, bold=True))

    # права панель — boost
    p.append(rect(500, 90, 440, 320, fill=BG, stroke=OFF, sw=1.6, rx=12))
    p.append(text(720, 118, "Boost — підвищення напруги", size=13, color=OFF, bold=True))
    right = [
        "Інша розкладка тих самих деталей.",
        "Ключ накачує котушку, а коли рветься —",
        "її «брикання» (викид напруги при",
        "розмиканні) ДОДАЄТЬСЯ до входу.",
        "",
        "Тому boost робить Vвих ВИЩУ за Vвх —",
        "чого лінійний не вміє в принципі.",
    ]
    yy = 152
    for ln in right:
        p.append(text(524, yy, ln, size=11, color=INK, anchor="start"))
        yy += 22
    p.append(rect(524, 360, 392, 34, fill="#fff5e6", stroke=OFF, sw=1.2, rx=8))
    p.append(text(720, 382, "те саме «брикання» котушки, що псувало ключі, — тут на користь",
                  size=10, color=OFF, bold=True))

    p.append(text(W / 2, 450,
                  "Усе це — комбінації ключа, котушки, діода й конденсатора; міняється лише схема їхнього з'єднання.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "sync-boost.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 5) Таймлайн історії імпульсного живлення (вставка hist-smps)
# ──────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 920, 940
    GOLD = "#caa24a"
    p = []
    p.append(text(W / 2, 40, "Імпульсне живлення: довга низка, у якій Apple — пізній вузол",
                  size=21, bold=True))
    p.append(text(W / 2, 62,
                  "перемикання струму існувало за десятиліття до 1977-го; справжній тригер — дешевий швидкий транзистор",
                  size=12.5, color=MUTED, italic=True))
    p.append(line(232, 96, 232, 870, color=MUTED, sw=3))

    items = [
        (118, "1930-ті", "Вібратор у радіоприймачі",
         "Механічний переривач кришить 6 В на пульсації → трансформатор → B+ для ламп", INK, 7.0),
        (191, "1958", "IBM 704 · Pioneer Magnetics",
         "Перші комутаційні регулятори — ще на тиратронах (лампах)", INK, 7.0),
        (264, "1959", "General Electric",
         "Опублікована рання схема напівпровідникового стабілізатора-перемикача", INK, 7.0),
        (337, "1962", "Telstar · Minuteman",
         "Космос і ракети: кожен грам дорогий → ефективність важливіша за простоту", FIELD, 8.5),
        (410, "1966–67", "Tektronix · RO Associates",
         "Портативний осцилограф; перший 20-кГц імпульсний БЖ як готовий товар", INK, 7.0),
        (483, "кін. 1960-х", "Швидкі високовольтні транзистори",
         "Motorola, SSPI, Siemens-Edison-Swan: дешевий ключ — ОСЬ де справжня революція", FIELD, 8.5),
        (556, "1969–71", "DEC PDP-11/20 · HP 2100A",
         "Імпульсне живлення входить у серійні міні-комп'ютери", INK, 7.0),
        (629, "1975", "IBM 5100 · HP 2640A",
         "Імпульсні БЖ — уже ~8% ринку, за два роки до Apple II", INK, 7.0),
        (702, "1976", "SG1524 (Р. Маммано)",
         "Перша мікросхема ШІМ-керування — оце справді змінює зручність розробки", FIELD, 8.5),
        (775, "1976", "Boschert, 80 Вт",
         "Безвентиляторний flyback у серії — той самий клас, що буде в Apple", INK, 7.0),
    ]
    for cy, yr, head, sub, col, r in items:
        sw = 3 if col == FIELD else 2.4
        p.append(circle(232, cy, r, fill=BG, stroke=col, sw=sw))
        p.append(text(210, cy + 5, yr, size=13, color=MUTED, anchor="end", bold=True))
        p.append(text(258, cy - 4, head, size=15.5, color=col, anchor="start", bold=True))
        p.append(text(258, cy + 15, sub, size=12.5, color=INK, anchor="start", italic=True))

    # Apple (золотий вузол)
    p.append(circle(232, 848, 11, fill=BG, stroke=GOLD, sw=3.2))
    p.append(circle(232, 848, 5, fill=GOLD, stroke=GOLD, sw=0))
    p.append(text(210, 853, "1977", size=13, color=MUTED, anchor="end", bold=True))
    p.append(text(258, 844, "Apple II · Род Голт", size=15.5, color=POS, anchor="start", bold=True))
    p.append(text(258, 863, "Акуратний 38-Вт flyback. Гарний інженерно — але ПІЗНІЙ у низці, не її початок",
                  size=12.5, color=INK, anchor="start", italic=True))

    # легенда
    p.append(circle(82, 896, 8.5, fill=BG, stroke=FIELD, sw=3))
    p.append(text(98, 900, "ключовий поштовх", size=12.5, color=INK, anchor="start"))
    p.append(circle(252, 896, 11, fill=BG, stroke=GOLD, sw=3.2))
    p.append(circle(252, 896, 5, fill=GOLD, stroke=GOLD, sw=0))
    p.append(text(270, 900, "вузол, який міф видає за «початок»", size=12.5, color=INK, anchor="start"))
    p.append(text(W / 2, 924,
                  "«Кожен комп'ютер копіює дизайн Голта» — міф: і топології, і ринок існували задовго до Apple II",
                  size=12.5, color=POS, italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 6) Електромеханічний вібратор (вставка hist-smps)
# ──────────────────────────────────────────────────────────────────────────────
def fig_vibrator():
    W, H = 920, 470
    BR = "#b5763a"
    GOLD = "#caa24a"
    p = []
    p.append(text(W / 2, 36, "Вібратор: механічний предок усіх імпульсних БЖ (~1930-ті)",
                  size=21, bold=True))
    p.append(text(W / 2, 58,
                  "перерви постійний струм → трансформуй → випрями. Тут ключ механічний; згодом його замінить транзистор",
                  size=12.5, color=MUTED, italic=True))

    # батарея 6 В
    p.append(line(70, 216, 70, 284, color=INK, sw=2))
    p.append(line(84, 232, 84, 268, color=INK, sw=5))
    p.append(text(73, 204, "+", size=17, color=POS, bold=True))
    p.append(text(84, 310, "6 В", size=14, color=INK, bold=True))
    p.append(text(84, 328, "акумулятор", size=12, color=MUTED))
    p.append(line(84, 250, 150, 250, color=INK, sw=2))

    # корпус вібратора
    p.append(rect(163, 154, 132, 192, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(229, 144, "ВІБРАТОР", size=13, color=INK, bold=True))
    p.append(vcoil(181, 210, 290, turns=5, amp=8, stroke=BR, sw=2.6))
    p.append(text(161, 320, "магніт", size=11.5, color=MUTED))
    p.append(line(223, 180, 223, 320, color=INK, sw=3))
    p.append(text(223, 338, "якір+пружина", size=11.5, color=MUTED))
    p.append(circle(245, 212, 4, fill=POS, stroke=POS, sw=0))
    p.append(circle(245, 288, 4, fill=NEG, stroke=NEG, sw=0))
    p.append(line(223, 212, 245, 212, color=INK, sw=2))
    p.append(line(223, 288, 245, 288, color=INK, sw=2))
    p.append(arrow(197, 242, 217, 242, color=INK, sw=1.8))
    p.append(text(207, 232, "≈100 Гц", size=10.5, color=MUTED, italic=True))
    p.append(line(245, 212, 400, 212, color=INK, sw=2))
    p.append(line(245, 288, 400, 288, color=INK, sw=2))
    p.append(line(150, 250, 400, 250, color=INK, sw=2))

    # трансформатор
    p.append(rect(464, 164, 12, 172, fill="#e4e4e4", stroke=INK, sw=2, rx=0))
    p.append(text(470, 152, "осердя", size=11, color=MUTED))
    p.append(vcoil(448, 186, 314, turns=6, amp=10, stroke=BR, sw=2.6))
    p.append(line(400, 212, 448, 212, color=BR, sw=2))
    p.append(line(400, 288, 448, 288, color=BR, sw=2))
    p.append(line(400, 250, 448, 250, color=BR, sw=2))
    p.append(text(430, 350, "первинна", size=11.5, color=MUTED))
    p.append(vcoil(492, 172, 328, turns=11, amp=11, stroke=BR, sw=2.6, right=True))
    p.append(text(515, 350, "вторинна ×30", size=11.5, color=FIELD, bold=True))
    p.append(line(492, 328, 492, 370, color=INK, sw=2))
    p.append(line(492, 172, 660, 172, color=BR, sw=2))

    # випрямляч (діод)
    p.append(line(660, 172, 660, 220, color=INK, sw=2))
    p.append('<polygon points="648,220 672,220 660,242" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    p.append(line(648, 242, 672, 242, color=INK, sw=2.6))
    p.append(line(660, 242, 660, 268, color=INK, sw=2))
    p.append(text(690, 232, "випрямляч", size=12, color=INK))
    p.append(text(690, 246, "(лампа або", size=10.5, color=MUTED))
    p.append(text(690, 260, "синхр. контакти)", size=10.5, color=MUTED))
    p.append(line(660, 268, 800, 268, color=INK, sw=2))

    # фільтр + вихід B+
    p.append(line(800, 268, 800, 210, color=INK, sw=2))
    p.append(line(784, 290, 816, 290, color=INK, sw=3))
    p.append(line(784, 302, 816, 302, color=INK, sw=3))
    p.append(line(800, 268, 800, 290, color=INK, sw=2))
    p.append(line(800, 302, 800, 330, color=INK, sw=2))
    p.append(text(830, 300, "фільтр", size=11.5, color=MUTED))
    p.append(circle(800, 210, 5, fill=POS, stroke=POS, sw=0))
    p.append(text(800, 196, "B+ ≈ 250 В", size=14, color=POS, bold=True))
    p.append(text(800, 346, "до ламп", size=11.5, color=MUTED))

    # спільний нуль
    p.append(line(84, 284, 84, 370, color=INK, sw=2))
    p.append(line(84, 370, 800, 370, color=INK, sw=2))
    p.append(line(800, 330, 800, 370, color=INK, sw=2))
    p.append(text(435, 386, "спільний нуль", size=11, color=MUTED))

    # підсумкова стрічка
    p.append(rect(60, 418, 800, 34, fill="#fbf7ec", stroke=GOLD, sw=1.5, rx=8))
    p.append(text(W / 2, 440,
                  "Той самий ланцюг «переривай → трансформуй → випрямляй» живе в кожному сучасному імпульсному БЖ — лише ключ тепер транзистор, а частота в тисячі разів вища",
                  size=12.5, color=INK))
    render(os.path.join(OUT, "vibrator.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 7) Вольт-секундний баланс: підйом = спад → Vвих=Vвх·D і розмах ΔI (вставка math)
# ──────────────────────────────────────────────────────────────────────────────
def fig_volt_second_balance():
    W, H = 940, 470
    p = []
    p.append(text(W / 2, 30, "Вольт-секундний баланс: підйом за «ВКЛ» = спад за «ВИКЛ»",
                  size=18, bold=True))
    p.append(text(W / 2, 52,
                  "струм котушки щоперіод повертається до себе — звідси й Vвих = Vвх·D, і розмах ΔI",
                  size=13, color=MUTED))

    ax0, ay, axR, ayTop = 90, 360, 612, 110
    onW, offW = 96, 144
    x0 = ax0
    x1, x2, x3, x4 = x0 + onW, x0 + onW + offW, x0 + 2 * onW + offW, x0 + 2 * onW + 2 * offW
    yband0, ybandH = 120, ay - 120

    # фонові смуги фаз
    p.append(rect(x0, yband0, onW, ybandH, fill="#eafaef", stroke="none", sw=0, rx=0))
    p.append(rect(x1, yband0, offW, ybandH, fill="#fdf3e0", stroke="none", sw=0, rx=0))
    p.append(rect(x2, yband0, onW, ybandH, fill="#eafaef", stroke="none", sw=0, rx=0))
    p.append(rect(x3, yband0, offW, ybandH, fill="#fdf3e0", stroke="none", sw=0, rx=0))
    p.append(text(x0 + onW / 2, 134, "ВКЛ", size=10, color=SW, bold=True))
    p.append(text(x1 + offW / 2, 134, "ВИКЛ", size=10, color=OFF, bold=True))

    # осі
    p.append(arrow(ax0, ay, axR, ay, color=INK, sw=1.4))
    p.append(text(axR, ay + 20, "час", size=11, color=INK, anchor="end"))
    p.append(arrow(ax0, ay, ax0, ayTop, color=INK, sw=1.4))
    p.append(text(ax0 - 6, ayTop + 2, "iл", size=12, color=INK, anchor="end", bold=True))

    yMin, yMax = 300, 200
    # рівневі пунктири + середнє (= навантаження)
    p.append(line(ax0, yMax, 578, yMax, color=MUTED, sw=1.0, dash="4 4"))
    p.append(line(ax0, yMin, 578, yMin, color=MUTED, sw=1.0, dash="4 4"))
    p.append(line(ax0, 250, 570, 250, color=SW, sw=1.4, dash="6 4"))
    p.append(text(ax0 + 6, 244, "середнє = Iвих", size=10, color=SW, anchor="start"))

    # трикутна хвиля
    p.append(poly([(x0, yMin), (x1, yMax), (x2, yMin), (x3, yMax), (x4, yMin)], OFF, sw=2.8))

    # нахили й ширини фаз
    p.append(text((x0 + x1) / 2 - 4, 230, "+(Vвх−Vвих)/L", size=10.5, color=SW, bold=True))
    p.append(text((x1 + x2) / 2 + 6, 230, "−Vвих/L", size=10.5, color=OFF, bold=True))
    p.append(text((x0 + x1) / 2, 378, "D·T", size=11, color=INK))
    p.append(text((x1 + x2) / 2, 378, "(1−D)·T", size=11, color=INK))

    # ΔI праворуч від хвилі
    xdi = 580
    p.append(line(xdi, yMax, xdi, yMin, color=INK, sw=1.2))
    p.append(line(xdi - 4, yMax, xdi + 4, yMax, color=INK, sw=1.2))
    p.append(line(xdi - 4, yMin, xdi + 4, yMin, color=INK, sw=1.2))
    p.append(text(xdi + 8, 254, "ΔI", size=12, color=INK, bold=True, anchor="start"))

    # права колонка — алгебра й результати
    bx, by, bw = 648, 150, 268
    p.append(rect(bx, by, bw, 150, fill=FILL, stroke=INK, sw=1.3, rx=11))
    p.append(text(bx + bw / 2, by + 26, "Щоб хвиля повторювалась:", size=12, color=INK, bold=True))
    p.append(text(bx + bw / 2, by + 48, "підйом = спад", size=12, color=MUTED))
    p.append(text(bx + bw / 2, by + 74, "(Vвх−Vвих)·D·T = Vвих·(1−D)·T", size=11, color=INK))
    p.append(rect(bx + 34, by + 92, bw - 68, 38, fill="#eafaef", stroke=SW, sw=1.4, rx=8))
    p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="16" '
             'fill="%s" text-anchor="middle" font-weight="700">Vвих = Vвх × D</text>'
             % (bx + bw / 2, by + 117, INK))

    p.append(rect(bx, 322, bw, 72, fill=FILL, stroke=OFF, sw=1.3, rx=11))
    p.append(text(bx + bw / 2, 346, "Висота трикутника (розмах):", size=12, color=OFF, bold=True))
    p.append('<text x="%.1f" y="372" font-family="Consolas, monospace" font-size="14" '
             'fill="%s" text-anchor="middle" font-weight="700">ΔI = (Vвх−Vвих)·D·T / L</text>'
             % (bx + bw / 2, INK))

    p.append(text(W / 2, 432,
                  "Одна умова — періодичність — дає одразу два числа: коефіцієнт перетворення і пульсацію струму.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "volt-second-balance.svg"), W, H, *p)


# ──────────────────────────────────────────────────────────────────────────────
# 8) Межа CCM ↔ DCM: де «плаває» трикутник струму (вставка math)
# ──────────────────────────────────────────────────────────────────────────────
def fig_ccm_dcm():
    W, H = 940, 380
    p = []
    p.append(text(W / 2, 30, "Межа CCM ↔ DCM: коли низ трикутника торкнеться нуля",
                  size=18, bold=True))
    p.append(text(W / 2, 52,
                  "вантаж задає, де «плаває» трикутник; під граничним струмом починається переривчастий режим",
                  size=13, color=MUTED))

    def panel(x0, title_, col, kind, note):
        pw, ph, py = 250, 196, 86
        base = py + ph - 34
        f = [text(x0 + pw / 2, py - 8, title_, size=13, color=col, bold=True),
             rect(x0, py, pw, ph, fill=BG, stroke=col, sw=1.6, rx=10)]
        xl, xr = x0 + 18, x0 + pw - 30
        f.append(line(xl - 6, base, xr + 10, base, color=INK, sw=1.6))
        f.append(text(xl - 10, base + 4, "0", size=11, color=INK, anchor="end"))
        period = (xr - xl) / 2.0
        if kind == "high":
            ymin, ypk = base - 34, base - 104
            f.append(poly([(xl, ymin), (xl + 0.4 * period, ypk), (xl + period, ymin),
                           (xl + 1.4 * period, ypk), (xl + 2 * period, ymin)], OFF, sw=2.6))
            f.append(line(xl, (ymin + ypk) / 2, xr, (ymin + ypk) / 2, color=SW, sw=1.3, dash="6 4"))
        elif kind == "edge":
            ymin, ypk = base, base - 86
            f.append(poly([(xl, ymin), (xl + 0.4 * period, ypk), (xl + period, ymin),
                           (xl + 1.4 * period, ypk), (xl + 2 * period, ymin)], OFF, sw=2.6))
            f.append(line(xl, (ymin + ypk) / 2, xr, (ymin + ypk) / 2, color=SW, sw=1.3, dash="6 4"))
            for k in range(3):
                f.append(circle(xl + k * period, ymin, 3.5, fill=POS, stroke=POS, sw=0))
        else:  # dcm
            ypk = base - 96
            f.append(poly([(xl, base), (xl + 0.3 * period, ypk), (xl + 0.62 * period, base),
                           (xl + period, base), (xl + 1.3 * period, ypk),
                           (xl + 1.62 * period, base), (xl + 2 * period, base)], OFF, sw=2.6))
            f.append(line(xl + 0.62 * period, base, xl + period, base, color=POS, sw=4))
            f.append(line(xl + 1.62 * period, base, xl + 2 * period, base, color=POS, sw=4))
            f.append(line(xl, base - 30, xr, base - 30, color=SW, sw=1.3, dash="6 4"))
        f.append(text(x0 + pw / 2, base + 22, note, size=10.5,
                      color=POS if kind == "dcm" else MUTED))
        return f

    p += panel(40, "Велике навантаження", SW, "high", "низ трикутника > 0")
    p += panel(345, "Гранична точка", OFF, "edge", "низ саме торкнувся 0")
    p += panel(650, "Мале навантаження", POS, "dcm", "є фаза спокою на 0")

    p.append(text(W / 2, 360,
                  "Гранична межа Iвих = ΔI/2 залежить лише від L, f і напруг — нижче неї перетворювач у DCM, і Vвих = Vвх·D вже не діє.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "ccm-dcm.svg"), W, H, *p)


if __name__ == "__main__":
    fig_buck_phases()
    fig_inductor_current()
    fig_duty_cycle()
    fig_sync_boost()
    fig_timeline()
    fig_vibrator()
    fig_volt_second_balance()
    fig_ccm_dcm()
    print("OK: figures written to", OUT)
