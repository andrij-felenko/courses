# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"   # світла «гаряча» заливка під POS
COOL = "#eaf0fd"   # світла «холодна» заливка під NEG
GRN  = "#eaf7ee"   # світла зелена заливка під FIELD
GOLD = "#caa24a"   # бурштин для «середнього»/застереження
GBG  = "#fff7e6"   # світла заливка під бурштин


# ── predictable: дві системи проти спільного дедлайну ─────────────────────────
# Ідея: ліва швидка в середньому, та з рідкісним сплеском за межу; права рівна.
# Реальний час обирає праву — передбачуваність понад середню швидкість.

def fig_predictable():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 30, "«Реальний час» — це передбачувано вчасно, не швидко", size=16, bold=True))
    p.append(text(W/2, 50, "важить не середній час, а гарантований найгірший випадок",
                  size=11, color=MUTED, italic=True))

    base = 230            # рівень осі-підлоги стовпчиків
    dl   = 150            # лінія дедлайну
    bw, gap = 26, 8

    # ── ліва панель: швидка, та з одним сплеском ──
    lx = 50
    p.append(text(lx + 3.5*(bw+gap), 78, "Швидка, та інколи зволікає",
                  size=11, color=POS, bold=True, anchor="middle"))
    lh = [34, 30, 40, 32, 116, 36, 31]      # п'ятий стовпчик пробиває дедлайн
    for i, h in enumerate(lh):
        x = lx + i*(bw+gap)
        spike = (i == 4)
        p.append(rect(x, base - h, bw, h, fill=(WARM if spike else GRN),
                      stroke=(POS if spike else FIELD), sw=1.4, rx=2))
    rspan = lx + len(lh)*(bw+gap) - gap
    p.append(line(lx - 6, dl, rspan + 6, dl, color=INK, sw=2, dash="6,3"))
    p.append(text(lx - 10, dl + 4, "дедлайн", size=9, color=INK, bold=True, anchor="end"))
    p.append(text(lx + 3.5*(bw+gap), base + 26, "один сплеск зірвав строк",
                  size=9, color=POS, bold=True, anchor="middle"))

    # ── права панель: повільніша, зате завжди в межах ──
    rx0 = 430
    p.append(text(rx0 + 3.5*(bw+gap), 78, "Не найшвидша, та завжди в межах",
                  size=11, color=FIELD, bold=True, anchor="middle"))
    rh = [70, 74, 68, 72, 76, 70, 73]
    for i, h in enumerate(rh):
        x = rx0 + i*(bw+gap)
        p.append(rect(x, base - h, bw, h, fill=GRN, stroke=FIELD, sw=1.4, rx=2))
    rspan2 = rx0 + len(rh)*(bw+gap) - gap
    p.append(line(rx0 - 6, dl, rspan2 + 6, dl, color=INK, sw=2, dash="6,3"))
    p.append(text(rspan2 + 10, dl + 4, "дедлайн", size=9, color=INK, bold=True, anchor="start"))
    p.append(text(rx0 + 3.5*(bw+gap), base + 26, "жодного разу не за межу",
                  size=9, color=FIELD, bold=True, anchor="middle"))

    # ── підсумкова рамка ──
    p.append(fitbox(110, 286, 540, 56,
                    "Реальний час обирає праву систему: повільнішу в середньому,\n"
                    "зате таку, що ніколи не запізнюється понад межу.",
                    size=11, fill=GBG, stroke=GOLD, bold=True))
    render(os.path.join(OUT, "predictable.svg"), W, H, *p)


# ── hard-soft: дві суворості дедлайну поруч ───────────────────────────────────
# Ідея: жорсткий — зрив = відмова, строк абсолютний; м'який — зрив = гірша
# якість, терпимий зрідка. Розрізняти важливо: різний запас і аналіз.

def fig_hard_soft():
    W, H = 760, 340
    p = []
    p.append(text(W/2, 30, "Дедлайн: жорсткий і м'який реальний час", size=16, bold=True))
    p.append(text(W/2, 50, "встигнути до строку; різниця — у ціні запізнення",
                  size=11, color=MUTED, italic=True))

    # ліва — жорсткий
    p.append(rect(40, 78, 340, 196, fill=WARM, stroke=POS, sw=1.8, rx=12))
    p.append(text(210, 104, "ЖОРСТКИЙ", size=13, color=POS, bold=True))
    p.append(text(210, 126, "зрив строку = відмова", size=10, color=INK, bold=True))
    for i, s in enumerate(["подушка безпеки авто", "керування верстатом, мотором",
                           "кардіостимулятор"]):
        p.append(text(64, 156 + i*22, "• " + s, size=10, color=INK, anchor="start"))
    p.append(text(210, 248, "запізнився — катастрофа", size=9.5, color=POS, bold=True))
    p.append(text(210, 266, "строк абсолютний", size=9, color=MUTED))

    # права — м'який
    p.append(rect(420, 78, 340, 196, fill=GRN, stroke=FIELD, sw=1.8, rx=12))
    p.append(text(590, 104, "М'ЯКИЙ", size=13, color=FIELD, bold=True))
    p.append(text(590, 126, "зрив = гірша якість", size=10, color=INK, bold=True))
    for i, s in enumerate(["звук (інколи затинка)", "відео (пропущений кадр)",
                           "оновлення дисплея"]):
        p.append(text(444, 156 + i*22, "• " + s, size=10, color=INK, anchor="start"))
    p.append(text(590, 248, "запізнився зрідка — терпимо", size=9.5, color=FIELD, bold=True))
    p.append(text(590, 266, "аби не часто", size=9, color=MUTED))

    p.append(text(W/2, 306, "Жорсткий вимагає суворого аналізу й запасу; до м'якого можна підійти поблажливіше.",
                  size=10, color=INK, bold=True))
    render(os.path.join(OUT, "hard-soft.svg"), W, H, *p)


# ── determinism: середній час проти обмеженої стелі найгіршого випадку ─────────
# Ідея: звичайна ОС дбає про середнє, найгірший може бути безмежним; RTOS
# обмежує найгірший відомою стелею — лише так дедлайн можна гарантувати.

def fig_determinism():
    W, H = 760, 350
    p = []
    p.append(text(W/2, 30, "Детермінованість: знати й обмежити найгірший випадок", size=15.5, bold=True))
    p.append(text(W/2, 50, "відгук укладається у відому стелю — це й дає змогу обіцяти дедлайн",
                  size=10.5, color=MUTED, italic=True))

    ox, base = 70, 240        # вісь «час відгуку»
    axw = 560
    p.append(line(ox, base, ox + axw, base, color=INK, sw=1.6))
    p.append(text(ox, base + 22, "час відгуку →", size=9, color=INK, bold=True, anchor="start"))

    # дзвоноподібний розподіл часу відгуку (середнє)
    cx, peak = ox + 180, 120
    pts = []
    for i in range(0, 241):
        t = i / 240.0
        xx = ox + t * 520
        # гаус навколо центру 0.31
        g = math.exp(-((t - 0.31) ** 2) / (2 * 0.075 ** 2))
        yy = base - (base - peak) * g
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))
    p.append(text(cx, 108, "типово (середнє)", size=9, color=NEG, bold=True))

    # стеля найгіршого випадку
    ceil_x = ox + 430
    p.append(line(ceil_x, 90, ceil_x, base, color=POS, sw=2.4))
    p.append(text(ceil_x, 82, "стеля (найгірший випадок)", size=9, color=POS, bold=True))
    p.append(line(ceil_x, 90, ox + axw, 90, color=POS, sw=1.4, dash="5,3"))
    p.append(text(ceil_x + 8, base - 6, "далі — ніколи", size=9, color=POS, bold=True, anchor="start"))

    p.append(fitbox(110, 280, 540, 64,
                    "Звичайна ОС оптимізує середнє, та її найгірший випадок може бути безмежним.\n"
                    "RTOS обмежує найгірший: затримку переривань, перемикання, роботу планувальника.\n"
                    "Гарантувати можна лише те, чий найгірший випадок відомий.",
                    size=9.6, fill=COOL, stroke=NEG, bold=True))
    render(os.path.join(OUT, "determinism.svg"), W, H, *p)


# ── priorities: пріоритети кодують терміновість (rate-monotonic) ───────────────
# Ідея: тісніший дедлайн → вищий пріоритет; критична задача витісняє решту.

def fig_priorities():
    W, H = 760, 320
    p = []
    p.append(text(W/2, 30, "Пріоритети — це закодовані дедлайни", size=16, bold=True))
    p.append(text(W/2, 50, "найтерміновіша задача дістає найвищий пріоритет і витісняє решту",
                  size=10.5, color=MUTED, italic=True))

    rows = [("керування мотором", "кожні 1 мс — тісно",  "ВИСОКИЙ",  POS,  WARM),
            ("опитування кнопок", "кожні 20 мс",          "середній", GOLD, GBG),
            ("оновлення дисплея", "кожні 200 мс — вільно","низький",  NEG,  COOL)]
    y0 = 80
    for i, (name, sub, prio, col, fill) in enumerate(rows):
        y = y0 + i*66
        p.append(rect(60, y, 280, 54, fill=BG, stroke=MUTED, sw=1.3, rx=8))
        p.append(text(80, y + 24, name, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(80, y + 42, sub, size=9, color=MUTED, anchor="start"))
        p.append(arrow(346, y + 27, 392, y + 27, color=INK, sw=1.8))
        p.append(rect(400, y, 180, 54, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(490, y + 32, prio, size=12, color=col, bold=True))

    # бічна рамка-правило
    p.append(rect(606, 80, 130, 186, fill=GRN, stroke=FIELD, sw=1.4, rx=12))
    p.append(mtext(671, 108, ["правило", "(rate-monotonic):"], size=9.5, color=FIELD, bold=True))
    p.append(mtext(671, 150, ["тісніший дедлайн", "→ вищий", "пріоритет"], size=9, color=INK))
    p.append(mtext(671, 214, ["критична задача", "витісняє решту", "й завжди встигає"],
                   size=9, color=MUTED))
    render(os.path.join(OUT, "priorities.svg"), W, H, *p)


# ── enemies: чотири вороги передбачуваності ───────────────────────────────────
# Ідея: інверсія, задовге блокування, необмежені операції, голодування — усі
# роблять найгірший випадок невідомим чи величезним.

def fig_enemies():
    W, H = 760, 350
    p = []
    p.append(text(W/2, 30, "Вороги реального часу: що руйнує передбачуваність", size=15.5, bold=True))
    p.append(text(W/2, 50, "уникай їх на критичному шляху, інакше найгірший випадок «попливе»",
                  size=10, color=MUTED, italic=True))

    cards = [("Інверсія пріоритетів", ["низька тримає замок,", "висока чекає", "→ успадкування пріор."], POS),
             ("Задовге блокування",  ["замок або очікування", "надто довго", "→ тримай коротко"], GOLD),
             ("Необмежені операції",  ["купа, довга ISR,", "busy-wait, рекурсія", "→ геть із шляху"], NEG),
             ("Голодування",          ["зажерлива висока", "не дає бігти нижчим", "→ дай решті час"], "#7a4fb0")]
    cw, ch, gap = 168, 150, 16
    x0 = (W - (4*cw + 3*gap)) / 2
    for i, (title, body, col) in enumerate(cards):
        x = x0 + i*(cw+gap)
        p.append(rect(x, 78, cw, ch, fill=BG, stroke=col, sw=1.8, rx=12))
        p.append(text(x + cw/2, 104, title, size=10.5, color=col, bold=True))
        p.append(line(x + 14, 114, x + cw - 14, 114, color="#e4e4e4", sw=1.2))
        p.append(mtext(x + cw/2, 138, body, size=9, color=INK))

    p.append(fitbox(110, 256, 540, 64,
                    "Спільне в усіх ворогів одне: вони роблять найгірший випадок невідомим\n"
                    "або величезним — а без відомого найгіршого випадку\n"
                    "реальний час гарантувати неможливо.",
                    size=9.4, fill=GBG, stroke=GOLD, bold=True))
    render(os.path.join(OUT, "enemies.svg"), W, H, *p)


# ── convergence: піраміда засобів, що сходяться в реальний час ─────────────────
# Ідея: super-loop без гарантій → задачі → планувальник → FreeRTOS → обмін →
# реальний час; кожен рівень додає те, чого бракувало нижчому.

def fig_convergence():
    W, H = 780, 350
    p = []
    p.append(text(W/2, 30, "Як усе сходиться: до здатності обіцяти час", size=15.5, bold=True))
    p.append(text(W/2, 50, "від простого циклу без жодних гарантій — до системи, що встигає гарантовано",
                  size=9.6, color=MUTED, italic=True))

    steps = [("Super-loop",  ["просто, та", "без гарантій"], MUTED, BG),
             ("Задачі",      ["кожна —", "проста справа"],  FIELD, BG),
             ("Планувальник",["пріоритети,", "витіснення"], GOLD,  BG),
             ("FreeRTOS",    ["ядро + два", "ядра ESP32"],  NEG,   BG),
             ("Обмін",       ["черги,", "м'ютекси"],        "#7a4fb0", BG),
             ("Реальний час",["гарантовано", "вчасно"],     POS,   WARM)]
    bw, bh, gap = 116, 84, 10
    x0 = (W - (6*bw + 5*gap)) / 2
    y = 94
    for i, (name, sub, col, fill) in enumerate(steps):
        x = x0 + i*(bw+gap)
        last = (i == len(steps)-1)
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=(2.4 if last else 1.6), rx=10))
        p.append(text(x + bw/2, y + 30, name, size=10, color=col, bold=True))
        p.append(mtext(x + bw/2, y + 50, sub, size=9, color=INK))
        if i < len(steps)-1:
            ax = x + bw
            p.append(arrow(ax + 1, y + bh/2, ax + gap - 1, y + bh/2, color=INK, sw=1.8))

    p.append(fitbox(120, 226, 540, 96,
                    "Super-loop не міг обіцяти час; задачі з пріоритетним витісненням,\n"
                    "обмеженими затримками RTOS і дбайливим дизайном — можуть.\n"
                    "Це й є реальний час: не «якось працює»,\n"
                    "а «гарантовано встигає».",
                    size=9.6, fill=GRN, stroke=FIELD, bold=True))
    render(os.path.join(OUT, "convergence.svg"), W, H, *p)


# ── utilization-model (math): дві задачі на часовій осі ───────────────────────
# Ідея: кожна задача забирає Cᵢ часу кожні Tᵢ, тож з'їдає частку Uᵢ=Cᵢ/Tᵢ;
# сума цих часток U — те, що перевіряють на розкладність.

def fig_utilization_model():
    W, H = 760, 320
    p = []
    p.append(text(W/2, 30, "Модель завантаження: частка часу Uᵢ = Cᵢ / Tᵢ", size=15, bold=True))
    p.append(text(W/2, 50, "кожна задача забирає Cᵢ часу кожні Tᵢ — сума часток U перевіряється на розкладність",
                  size=9.4, color=MUTED, italic=True))

    ox = 70
    axw = 620

    def lane(y, label, col, fill, period_px, c_px, n, sub):
        out = [text(ox - 10, y + 4, label, size=10, color=col, bold=True, anchor="end")]
        out.append(line(ox, y + 14, ox + axw, y + 14, color=INK, sw=1.4))   # вісь часу
        for k in range(n):
            x = ox + k * period_px
            # межа періоду (пунктир) і блок виконання Cᵢ
            out.append(line(x, y - 18, x, y + 14, color=MUTED, sw=1.0, dash="3,3"))
            out.append(rect(x, y - 16, c_px, 30, fill=fill, stroke=col, sw=1.4, rx=2))
        # остання межа
        xl = ox + n * period_px
        out.append(line(xl, y - 18, xl, y + 14, color=MUTED, sw=1.0, dash="3,3"))
        out.append(text(ox + axw - 4, y - 22, sub, size=9, color=MUTED, anchor="end"))
        # дужка періоду
        out.append(line(ox, y + 26, ox + period_px, y + 26, color=col, sw=1.2))
        out.append(text(ox + period_px/2, y + 38, "Tᵢ", size=9, color=col, italic=True))
        out.append(text(ox + c_px/2, y - 22, "Cᵢ", size=9, color=col, bold=True))
        return out

    p += lane(120, "часта", POS, WARM, 78, 18, 7, "період малий → частка велика")
    p += lane(210, "рідка", NEG, COOL, 300, 30, 2, "період великий → частка мала")

    p.append(fitbox(110, 254, 540, 50,
                    "Завантаження U = Σ Cᵢ/Tᵢ — те число, що перевіряють на розкладність\n"
                    "ще до запуску коду на платі.",
                    size=9.6, fill=GBG, stroke=GOLD, bold=True))
    render(os.path.join(OUT, "utilization-model.svg"), W, H, *p)


# ── rm-vs-inverse (math): RM проти зворотних пріоритетів ───────────────────────
# Ідея: те саме навантаження; згори RM (встигають усі), знизу зворотні
# пріоритети (рідка блокує часту, і та зриває дедлайн).

def fig_rm_vs_inverse():
    W, H = 760, 380
    p = []
    p.append(text(W/2, 30, "Той самий набір задач — різниця лише в порядку пріоритетів", size=14.5, bold=True))
    p.append(text(W/2, 50, "згори rate-monotonic: встигають усі; знизу зворотні: рідка блокує часту",
                  size=9.4, color=MUTED, italic=True))

    ox, axw = 90, 600
    fast_dl = 78          # крок дедлайну частої задачі (px)

    def axis(y):
        return [line(ox, y, ox + axw, y, color=INK, sw=1.4)]

    def deadlines(y, col):
        out = []
        x = ox + fast_dl
        while x <= ox + axw:
            out.append(line(x, y - 40, x, y + 6, color=col, sw=1.0, dash="3,3"))
            x += fast_dl
        return out

    # ── верх: RM — часта має пріоритет, усі встигають ──
    yt = 110
    p.append(text(ox - 12, yt - 18, "RM", size=11, color=FIELD, bold=True, anchor="end"))
    p += deadlines(yt, MUTED)
    p += axis(yt)
    # блоки частої (вузькі, в кожному вікні, до дедлайну)
    x = ox + 6
    while x + 16 <= ox + axw:
        p.append(rect(x, yt - 22, 16, 26, fill=WARM, stroke=POS, sw=1.3, rx=2))
        x += fast_dl
    # рідка задача — розкидана між вікнами (нижчий пріоритет, поступається)
    for seg in [(ox+30, 40), (ox+150, 40), (ox+270, 40), (ox+420, 40), (ox+540, 40)]:
        p.append(rect(seg[0], yt + 10, seg[1], 20, fill=COOL, stroke=NEG, sw=1.2, rx=2))
    p.append(text(ox + axw, yt - 12, "часта встигає", size=9, color=FIELD, bold=True, anchor="end"))
    p.append(text(ox, yt + 44, "часта (висока) ▢   рідка (низька) ▢ — поступається у вікнах",
                  size=9, color=MUTED, anchor="start"))

    # ── низ: зворотні пріоритети — рідка блокує часту ──
    yb = 250
    p.append(text(ox - 12, yb - 18, "навпаки", size=11, color=POS, bold=True, anchor="end"))
    p += deadlines(yb, MUTED)
    p += axis(yb)
    # рідка задача (висока тепер) — довгий блок, що накриває кілька вікон
    p.append(rect(ox + 90, yb - 22, 150, 26, fill=COOL, stroke=NEG, sw=1.6, rx=2))
    p.append(text(ox + 165, yb - 30, "рідка тримає процесор", size=9, color=NEG, anchor="middle"))
    # часта намагається, але пропускає дедлайн усередині блоку
    for bx in [ox+6, ox+255, ox+333]:
        p.append(rect(bx, yb - 22, 16, 26, fill=WARM, stroke=POS, sw=1.3, rx=2))
    # позначка зриву дедлайну
    miss_x = ox + 156
    p.append(text(miss_x, yb + 22, "✗ дедлайн частої зірвано", size=9, color=POS, bold=True, anchor="middle"))

    p.append(fitbox(110, 312, 540, 50,
                    "Навантаження те саме. RM-порядок укладає всі дедлайни;\n"
                    "зворотний — рукотворна інверсія за дизайном.",
                    size=9.6, fill=GRN, stroke=FIELD, bold=True))
    render(os.path.join(OUT, "rm-vs-inverse.svg"), W, H, *p)


if __name__ == "__main__":
    fig_predictable()
    fig_hard_soft()
    fig_determinism()
    fig_priorities()
    fig_enemies()
    fig_convergence()
    fig_utilization_model()
    fig_rm_vs_inverse()
    print("OK figs realtime-determinism")
