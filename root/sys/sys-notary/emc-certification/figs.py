# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

USA  = "#2457d6"   # FCC / США — синій
EU   = "#8e44ad"   # CE / ЄС — фіолетовий
GOOD = FIELD       # проходить / дозвіл — зелений
BAD  = POS         # завал / глушіння — червоний


# ── Фігура 1: дві брами ринку — FCC (США) і CE/RED (ЄС) ──────────────────────

def fig_two_gates():
    W, H = 760, 380
    p = []

    def gate(x0, col, head, rows):
        w = 320
        p.append(rect(x0, 60, w, 300, fill=BG, stroke=col, sw=2.4, rx=10))
        p.append(rect(x0, 60, w, 44, fill=col, stroke=col, sw=2.4, rx=10))
        p.append(text(x0 + w / 2, 88, head, size=16, color="#ffffff", bold=True))
        y = 132
        for lbl, val in rows:
            p.append(text(x0 + 18, y, lbl, size=12.5, color=MUTED, anchor="start"))
            p.append(text(x0 + 18, y + 20, val, size=13, color=INK, anchor="start", bold=True))
            y += 52

    gate(40, USA, "США — FCC", [
        ("Хто дозволяє", "федеральний регулятор"),
        ("Закон", "47 CFR Part 15"),
        ("Для радіо (TX)", "certification → FCC ID"),
        ("Знак на виробі", "FCC ID + логотип"),
    ])
    gate(400, EU, "ЄС — CE / RED", [
        ("Хто дозволяє", "сам виробник (декларує)"),
        ("Закон", "директива RED 2014/53/EU"),
        ("Для радіо (TX)", "гармонізовані стандарти"),
        ("Знак на виробі", "маркування CE"),
    ])

    # спільна суть унизу
    b, bw, bh = textbox(W / 2, 342,
                        "Обидві брами питають те саме: не глуши сусідів і не глухни сам",
                        size=12.5, color=INK, fill="#f0fdf4", stroke=GOOD, min_w=560)
    p.append(b)

    render(os.path.join(OUT, "two-gates.svg"), W, H, *p,
           title="Дві брами на ринок: FCC (США) і CE/RED (ЄС)")


# ── Фігура 2: готовий модуль проносить сертифікат у виріб ────────────────────

def fig_module_shortcut():
    W, H = 780, 380
    p = []
    cy = 190

    # великий контур виробу
    p.append(rect(40, 90, 700, 240, fill="#fbfbfd", stroke=INK, sw=2.0, rx=12))
    p.append(text(60, 118, "твій виріб (host)", size=13, color=MUTED, anchor="start", bold=True))

    # модуль усередині — «чорна скринька» з сертифікатом
    mx, my, mw, mh = 470, 130, 230, 150
    p.append(rect(mx, my, mw, mh, fill="#f3e8fb", stroke=EU, sw=2.6, rx=10))
    p.append(text(mx + mw / 2, my + 24, "радіомодуль", size=13.5, color=EU, bold=True))
    p.append(text(mx + mw / 2, my + 44, "(готовий, сертифікований)", size=10.5, color=MUTED))
    # начинка модуля — це і є ВЧ-тракт зі scope
    for i, lbl in enumerate(["підсилювач (PA/LNA)", "змішувач", "гетеродин · синтезатор"]):
        p.append(text(mx + mw / 2, my + 72 + i * 20, "· " + lbl, size=11, color=INK))
    # печатка на модулі
    p.append(circle(mx + mw - 20, my + 20, 15, fill=GOOD, stroke=GOOD, sw=1))
    p.append(text(mx + mw - 20, my + 25, "✓", size=17, color="#ffffff", bold=True))

    # твоя частина — плата, живлення, USB — це «ненавмисний випромінювач»
    p.append(rect(70, 150, 230, 120, fill="#fdf6e3", stroke=MUTED, sw=1.8, rx=8))
    p.append(text(185, 174, "твоя плата", size=12.5, color=INK, bold=True))
    for i, lbl in enumerate(["MCU, тактовий генератор", "живлення (DC-DC)", "USB, кабелі, роз'єми"]):
        p.append(text(185, 196 + i * 20, "· " + lbl, size=10.5, color=MUTED))

    # стрілка «сертифікат модуля переноситься у виріб»
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" stroke-dasharray="7 4" marker-end="url(#arrow)"/>'
             % (mx, my + mh + 6, (mx + 185) / 2 + 60, my + mh + 44, 300, 214, EU))

    # два вироки внизу
    b1 = fitbox(70, 300, 340, 44,
                "радіо вже сертифіковане модулем →\nповторно ВЧ НЕ випробовують",
                size=12, color=INK, fill="#f0fdf4", stroke=GOOD)
    b2 = fitbox(430, 300, 310, 44,
                "твою плату все одно перевіряють\nна ненавмисні завади й безпеку",
                size=12, color=INK, fill="#fef2f2", stroke=BAD)
    p.append(b1); p.append(b2)

    render(os.path.join(OUT, "module-shortcut.svg"), W, H, *p,
           title="Готовий модуль проносить дозвіл на радіо у твій виріб")


# ── Фігура 3: чотири квадранти EMC — випромінення vs несприйнятливість ───────

def fig_emc_quadrants():
    W, H = 720, 400
    p = []
    cx, cy = 360, 210
    # хрест
    p.append(line(60, cy, 660, cy, color=INK, sw=1.8))
    p.append(line(cx, 70, cx, 360, color=INK, sw=1.8))
    # осі-підписи
    p.append(text(360, 58, "хто винен: ти  ←  |  →  світ навколо", size=12.5, color=MUTED))
    p.append(text(150, cy - 6, "провід", size=12, color=MUTED, bold=True))
    p.append(text(150, cy + 18, "(кондуктивно)", size=10.5, color=MUTED))
    p.append(text(575, cy - 6, "ефір", size=12, color=MUTED, bold=True))
    p.append(text(575, cy + 18, "(радіаційно)", size=10.5, color=MUTED))

    def quad(x, y, head, body, col):
        w, h = 268, 108
        p.append(rect(x, y, w, h, fill=BG, stroke=col, sw=2.2, rx=8))
        p.append(text(x + w / 2, y + 24, head, size=13.5, color=col, bold=True))
        for i, ln in enumerate(body):
            p.append(text(x + w / 2, y + 48 + i * 18, ln, size=11, color=INK))

    # верх = ВИПРОМІНЕННЯ (ти шумиш назовні) — червоне
    quad(84, 96, "Кондуктивні завади", ["скільки бруду ти жене", "у мережу / по кабелю"], BAD)
    quad(368, 96, "Радіаційні завади", ["скільки ти випромінюєш", "в ефір антеною й корпусом"], BAD)
    # низ = НЕСПРИЙНЯТЛИВІСТЬ (світ б'є по тобі, ти терпиш) — зелене
    quad(84, 226, "Кондуктивна стійкість", ["чи виживеш від завад", "по проводах (+ ESD, сплески)"], GOOD)
    quad(368, 226, "Радіаційна стійкість", ["чи виживеш в полі", "від чужого передавача"], GOOD)

    # підписи верх/низ збоку
    p.append(text(360, 90, "ВИПРОМІНЕННЯ — не шуми на інших", size=12.5, color=BAD, bold=True))
    p.append(text(360, 356, "СТІЙКІСТЬ — не ламайся від інших", size=12.5, color=GOOD, bold=True))

    render(os.path.join(OUT, "emc-quadrants.svg"), W, H, *p,
           title="EMC — чотири квадранти: випромінення й стійкість, провід і ефір")


# ── Фігура 4: як міряють радіаційні завади (безлунна камера) ─────────────────

def fig_emc_lab():
    W, H = 760, 380
    p = []
    floor = 320
    # підлога (заземлена площина)
    p.append(line(60, floor, 700, floor, color=INK, sw=2.4))
    for x in range(70, 701, 26):
        p.append(line(x, floor, x - 10, floor + 12, color=MUTED, sw=1))
    p.append(text(380, floor + 32, "заземлена площина (метал)", size=11, color=MUTED))

    # поглинальні піраміди по стінах/стелі
    def pyramids(x0, x1, y, up):
        step = 22
        pts = []
        x = x0
        while x < x1:
            tip = y - 14 if up else y + 14
            p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#eef0f2" '
                     'stroke="%s" stroke-width="1"/>' % (x, y, x + step / 2, tip, x + step, y, MUTED))
            x += step
    pyramids(60, 700, 70, up=False)      # стеля
    p.append(text(380, 44, "безлунна камера — стіни й стеля глушать луну", size=11.5, color=MUTED))

    # EUT на столі 0.8 м, на поворотному столі
    tx = 210
    p.append(rect(tx - 40, floor - 70, 80, 8, fill=FILL, stroke=INK, sw=1.8, rx=2))   # стільниця
    p.append(line(tx, floor - 62, tx, floor, color=INK, sw=1.6))
    # поворотна дуга під столом
    p.append('<path d="M %.1f %.1f A 46 12 0 0 0 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.6" marker-end="url(#arrow)"/>' % (tx - 40, floor + 6, tx + 40, floor + 6, EU))
    p.append(text(tx, floor + 26, "стіл крутиться 360°", size=10.5, color=EU))
    # сам виріб
    p.append(rect(tx - 22, floor - 96, 44, 30, fill="#f3e8fb", stroke=EU, sw=2, rx=4))
    p.append(text(tx, floor - 106, "виріб (EUT)", size=11, color=EU, bold=True))
    p.append(text(tx, floor - 78, "0.8 м", size=10, color=MUTED))

    # вимірювальна антена на 3 м, їздить по висоті
    ax = 560
    p.append(line(ax, floor - 160, ax, floor - 40, color=INK, sw=2))               # щогла
    p.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (ax - 26, floor - 120, ax, floor - 132, ax + 26, floor - 120, USA))  # антена
    p.append(text(ax, floor - 146, "вимірювальна", size=10.5, color=USA, bold=True))
    p.append(text(ax, floor - 132, "антена", size=10.5, color=USA, bold=True))
    # висотний скан
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)" stroke-dasharray="4 3"/>'
             % (ax + 34, floor - 150, ax + 34, floor - 60, USA))
    p.append(text(ax + 60, floor - 105, "1–4 м", size=10.5, color=USA, anchor="start"))

    # відстань між ними
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)"/>' % (tx + 24, floor - 130, ax - 30, floor - 130, INK))
    p.append(text((tx + ax) / 2, floor - 138, "3 м (або 10 м)", size=11, color=INK, bold=True))

    # хвиля від EUT до антени
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="2 5"/>' % (tx + 24, floor - 90, (tx + ax) / 2, floor - 108, ax - 28, floor - 112, BAD))

    # приймач унизу
    b = fitbox(276, floor - 34, 218, 30, "приймач · квазі-піковий детектор",
               size=11, color=INK, fill=BG, stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "emc-lab.svg"), W, H, *p,
           title="Вимір радіаційних завад: виріб крутиться, антена сканує висоту")


# ── Фігура 5 (hist): американська лінія — від хаосу до FCC ────────────────────

def fig_hist_us_timeline():
    W, H = 780, 320
    p = []
    axis = 168
    p.append(line(60, axis, 720, axis, color=INK, sw=2.2))
    p.append('<polygon points="720,%d 706,%d 706,%d" fill="%s"/>'
             % (axis, axis - 6, axis + 6, INK))

    # чотири віхи: рік, підпис, угору/вниз
    marks = [
        (120, "1912", "Radio Act 1912:\nлише «мінімізувати»\nзавади — беззуба норма", -1),
        (300, "1926", "суд у справі Zenith:\nу Комерц-департаменту\nнема влади — ХАОС", +1),
        (500, "1927", "Radio Act 1927\n(Кулідж, 23.02):\nстворено FRC", -1),
        (660, "1934", "Communications Act:\nFCC заміняє FRC\n(Рузвельт, 19.06)", +1),
    ]
    for x, yr, cap, up in marks:
        col = BAD if yr == "1926" else (GOOD if yr in ("1927", "1934") else MUTED)
        p.append(circle(x, axis, 7, fill=col, stroke=col, sw=1))
        p.append(text(x, axis + (34 if up < 0 else -22), yr, size=15, color=col, bold=True))
        by = axis - 92 if up < 0 else axis + 40
        b = fitbox(x - 82, by, 164, 60, cap, size=10.5, color=INK,
                   fill=BG, stroke=col)
        p.append(b)

    render(os.path.join(OUT, "hist-us-timeline.svg"), W, H, *p,
           title="США: від радіохаосу 1920-х до регулятора FCC")


# ── Фігура 6 (hist): що НАСПРАВДІ означає CE — беконім і міф ──────────────────

def fig_hist_ce_names():
    W, H = 760, 360
    p = []

    # великий значок CE по центру вгорі
    p.append(text(380, 88, "CE", size=64, color=EU, bold=True))
    p.append(text(380, 118, "маркування на виробі", size=12, color=MUTED))

    # три картки-версії: походження, беконім, міф
    def card(x, head, body, col, verdict, vcol):
        w, h = 224, 168
        p.append(rect(x, 150, w, h, fill=BG, stroke=col, sw=2.2, rx=10))
        p.append(rect(x, 150, w, 34, fill=col, stroke=col, sw=2.2, rx=10))
        p.append(text(x + w / 2, 172, head, size=13, color="#ffffff", bold=True))
        yb = 206
        for ln in body:
            p.append(text(x + w / 2, yb, ln, size=10.8, color=INK))
            yb += 18
        b = fitbox(x + 12, 150 + h - 40, w - 24, 30, verdict,
                   size=10.5, color=INK, fill=BG, stroke=vcol)
        p.append(b)

    card(30, "звідки взялось", [
        "від фр. Communauté", "Européenne —", "«Європейська спільнота»,", "попередниця ЄС"],
        MUTED, "історичне походження", MUTED)
    card(268, "Conformité Eur.", [
        "«європейська", "відповідність» —", "тлумачення НЕ згадане", "в засновничих директивах"],
        EU, "беконім (задній зміст)", EU)
    card(506, "«China Export»", [
        "нібито таємний знак", "китайського імпорту —", "Єврокомісія: такого", "знака не існує"],
        BAD, "міф без доказів", BAD)

    render(os.path.join(OUT, "hist-ce-names.svg"), W, H, *p,
           title="Що насправді означає CE: походження, беконім і міф")


if __name__ == "__main__":
    fig_two_gates()
    fig_module_shortcut()
    fig_emc_quadrants()
    fig_emc_lab()
    fig_hist_us_timeline()
    fig_hist_ce_names()
    print("OK: figures written to", OUT)
