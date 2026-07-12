# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC   = "#7a4ea8"   # фіолетовий — вплив/рішення
ACCBG = "#f3edfb"
AMBER = "#b8862f"
AMBERBG = "#fff6e0"
GREENBG = "#e9f6ee"
REDBG = "#fdecea"
BLUEBG = "#eaf0fd"


# ── FIG 1: розрив влади й місток впливу ───────────────────────────────────────
# Ідея: архітектор стоїть на одному краю (відповідає за форму), команди — на
# іншому (руки в них). Між ними прірва: наказ туди не дотягується (тонка червона
# стрілка гасне в прірві). Єдине, що перекидає місток, — вплив (зелена дуга
# згори). Три яруси написів — місток угорі, стрілка-наказ посередині, підпис
# прірви внизу — щоб нічого не накладалося.
def fig_authority_gap():
    W, H = 860, 300
    p = []
    base_y = 200

    # платформи
    lb = fitbox(60, 150, 240, 60, "АРХІТЕКТОР\nвідповідає за форму системи",
                size=13, pad=10, fill=BLUEBG, stroke=NEG, sw=1.9, color=INK, bold=True)
    rb = fitbox(560, 150, 240, 60, "КОМАНДИ\nпишуть код — руки в них",
                size=13, pad=10, fill=GREENBG, stroke=FIELD, sw=1.9, color=INK, bold=True)
    p.append(lb); p.append(rb)

    # прірва між ними (світла смуга)
    p.append(rect(300, 150, 260, 60, fill="#fbfbfc", stroke="#e3e6ea", sw=1.0, rx=6))

    # місток впливу — зелена дуга згори
    p.append('<path d="M 300 150 Q 430 66 560 150" fill="none" stroke="%s" '
             'stroke-width="3" marker-end="url(#arrow)"/>' % FIELD)
    p.append(text(430, 82, "ВПЛИВ — єдиний місток", size=14, color=FIELD, bold=True))

    # наказ, що не дотягується — червона стрілка, що гасне в прірві
    p.append(arrow(300, 178, 418, 178, color=POS, sw=2.0))
    p.append(text(360, 168, "наказ", size=11, color=POS, bold=True))
    p.append(text(432, 182, "✗", size=15, color=POS, bold=True))
    p.append(text(430, 234, "розрив влади: наслідки на тобі — а команди тобі не підлеглі",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "authority-gap.svg"), W, H, *p,
           title="Відповідаєш за форму, але не командуєш руками")


# ── FIG 2: драбина важелів — від слабшого до міцнішого ────────────────────────
# Ідея: вплив не харизма, а впорядкований набір важелів. Знизу — наказ (дешево
# видати, дорого й недовго тримати), угору — усе міцніше, аж до правила в
# механізмі (дорого раз збудувати, тримається само й для всіх). Кожен важіль —
# у своїй рамці (два рядки), ліворуч вертикальна стрілка «слабший→міцніший»,
# праворуч короткі підписи ціни на нижній і верхній сходинці.
def fig_levers_ladder():
    W, H = 900, 470
    p = []
    x0, bw = 150, 560
    steps = [  # знизу вгору
        ("Хай правило несе МЕХАНІЗМ", "фітнес-функція, процес поради: авторитет у системі, однаковий для всіх — і для тебе", FIELD, GREENBG),
        ("Замости ДОРОГУ до правильного", "правильне = шлях найменшого спротиву; сперечатися вже нема про що", "#2f9e8f", "#e6f5f2"),
        ("Зрозумій, тоді говори їхньою ВАЛЮТОЮ", "рішення стає почасти їхнім — тримається, поки їм болить", AMBER, AMBERBG),
        ("НАКАЗ (гола влада)", "тримається, поки стоїш над душею; роблять букву, не суть — і саботують", POS, REDBG),
    ]
    sh, gap = 78, 16
    top = 70
    for i, (head, sub, col, fill) in enumerate(steps):
        y = top + i * (sh + gap)
        p.append(rect(x0, y, bw, sh, fill=fill, stroke=col, sw=2.0, rx=10))
        p.append(text(x0 + bw / 2, y + 30, head, size=14, color=col, bold=True))
        p.append(text(x0 + bw / 2, y + 55, sub, size=11.5, color=INK))

    # ліворуч — вісь міцності
    ax = 96
    p.append(arrow(ax, top + 4 * sh + 3 * gap, ax, top, color=INK, sw=2.2))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-style="italic" transform="rotate(-90 %d %d)">'
             'слабший  →  міцніший важіль</text>'
             % (ax - 18, (top + top + 4 * sh + 3 * gap) / 2, FONT, MUTED,
                ax - 18, (top + top + 4 * sh + 3 * gap) / 2))

    # праворуч — ціна на краях драбини
    rx = x0 + bw + 18
    p.append(mtext(rx, top + 30, "дорого раз\nзбудувати —\nтримається само",
                   size=10.5, color=FIELD, anchor="start", lh=1.25, bold=True))
    y_bot = top + 3 * (sh + gap)
    p.append(mtext(rx, y_bot + 30, "дешево\nнаказати —\nдорого тримати",
                   size=10.5, color=POS, anchor="start", lh=1.25, bold=True))

    render(os.path.join(OUT, "influence-levers.svg"), W, H, *p,
           title="Важелі впливу: від наказу до правила в механізмі")


# ── FIG 3: та сама розвилка DH — наказ падає, важелі тримають ──────────────────
# Ідея: панель-сквад хоче SQL прямо в Postgres, в обхід TelemetryStore. Ліворуч —
# шлях наказу: цього разу послухались, за тиждень обхід повернувся тихцем.
# Праворуч — чотири важелі, застосовані до цього ж випадку, і правило, що
# тримається без архітектора. Дві колонки з запасом, кроки — кожен у своїй рамці.
def fig_dh_play():
    W, H = 940, 470
    p = []

    # банер сценарію
    p.append(fitbox(60, 44, 820, 40,
                    "DH: панель-сквад хоче писати SQL прямо в Postgres — в обхід інтерфейсу TelemetryStore",
                    size=12.5, pad=10, fill="#eef1f5", stroke=MUTED, sw=1.3, color=INK, bold=True))

    # ── ліва колонка: НАКАЗ ──
    lx, lw = 60, 360
    p.append(text(lx + lw / 2, 116, "НАКАЗ", size=14, color=POS, bold=True))
    p.append(fitbox(lx, 128, lw, 70, "«Заборонено. Ходіть\nчерез інтерфейс.»",
                    size=13, pad=10, fill=REDBG, stroke=POS, sw=1.9, color=INK, bold=True))
    p.append(arrow(lx + lw / 2, 200, lx + lw / 2, 236, color=POS, sw=2.0))
    p.append(fitbox(lx, 238, lw, 78,
                    "цього разу послухались —\nза тиждень прямий SQL повернувся,\nтепер тихцем",
                    size=12, pad=10, fill="#fff4f2", stroke=POS, sw=1.6, color=INK))
    p.append(text(lx + lw / 2, 352, "✗  правило живе, поки ти дивишся", size=11.5, color=POS, bold=True))

    # роздільник
    p.append(line(470, 104, 470, 420, color="#dfe3e8", sw=1.4, dash="5 5"))

    # ── права колонка: ВПЛИВ (чотири важелі) ──
    rx, rw = 520, 360
    p.append(text(rx + rw / 2, 116, "ВПЛИВ", size=14, color=FIELD, bold=True))
    plays = [
        ("Слухаю", "їм пекти звіт до пʼятниці; інтерфейс — зайвий гак", AMBER, AMBERBG),
        ("Валюта", "«зʼїдемо з Postgres — упаде ТВІЙ звіт, о 2-й ночі»", NEG, BLUEBG),
        ("Мощу дорогу", "додаю energyByPeriod() у TelemetryStore — прямий SQL не потрібен", "#2f9e8f", "#e6f5f2"),
        ("Механізм", "перевірка валить білд на import «pg» поза storage/", ACC, ACCBG),
    ]
    sy, sh2, g2 = 128, 56, 10
    for i, (tag, body, col, fill) in enumerate(plays):
        y = sy + i * (sh2 + g2)
        p.append(rect(rx, y, rw, sh2, fill=fill, stroke=col, sw=1.7, rx=8))
        p.append(text(rx + 12, y + 22, tag, size=11.5, color=col, anchor="start", bold=True))
        p.append(text(rx + 12, y + 42, body, size=10.8, color=INK, anchor="start"))
    yb = sy + 4 * (sh2 + g2)
    p.append(text(rx + rw / 2, yb + 8, "✓  тримається без тебе — і для всіх однаково",
                  size=11.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "dh-bypass-play.svg"), W, H, *p,
           title="Той самий обхід: наказ падає — важелі тримають")


# ── FIG 4 (вставка hist): родовід ідеї — переїзд із менеджменту в архітектуру ──
# Ідея: «вплив без влади» не софтверний винахід. Три станції згори вниз —
# менеджмент (Коен-Бредфорд) → софтверна архітектура (Фаулер) → ліфт (Гопе).
# Між першою і другою — підписаний перехід «переїзд у софт» (у тому й суть).
# Роки — окремою колонкою ліворуч (жодна лінія крізь текст не йде); стрілки —
# лише в порожніх проміжках по центру; кожна станція — у своїй рамці з запасом.
def fig_lineage():
    W, H = 900, 510
    p = []
    cx = 515                       # центр колонки-станцій
    bx, bw = 170, 690              # рамки станцій

    def yearbox(y, s):
        return fitbox(40, y, 110, 64, s, size=13, pad=8,
                      fill="#f4f6f8", stroke=MUTED, sw=1.5, color=INK, bold=True)

    # ── станція 1: менеджмент — Коен і Бредфорд ──
    p.append(rect(bx, 60, bw, 96, fill=AMBERBG, stroke=AMBER, sw=1.9, rx=10))
    p.append(text(cx, 88, "Менеджмент · Ален Коен і Девід Бредфорд", size=15, color=AMBER, bold=True))
    p.append(text(cx, 114, "«Influence Without Authority»: валюти обміну + закон взаємності", size=12.5, color=INK))
    p.append(text(cx, 138, "впливаєш не наказом, а обміном того, що цінне для іншого", size=12, color=MUTED, italic=True))
    p.append(yearbox(76, "1989\nстаття\n1990 книга"))

    # перехід «менеджмент → софт» (порожній проміжок 156..214)
    p.append(arrow(cx, 160, cx, 210, color=INK, sw=2.4))
    p.append(fitbox(688, 170, 172, 30, "переїзд у софт →", size=11.5, pad=8,
                    fill="#eef1f5", stroke=MUTED, sw=1.3, color=INK, bold=True))

    # ── станція 2: софтверна архітектура — Фаулер ──
    p.append(rect(bx, 214, bw, 108, fill=ACCBG, stroke=ACC, sw=1.9, rx=10))
    p.append(text(cx, 242, "Софтверна архітектура · Мартін Фаулер, 2003", size=14.5, color=ACC, bold=True))
    p.append(text(cx, 267, "Reloadus (вирішує все сам)  ·  Oryzus (тягне рівень команди)", size=12, color=INK))
    p.append(text(cx, 291, "архітектура = спільне розуміння будови досвідченими", size=11.5, color=MUTED, italic=True))
    p.append(text(cx, 311, "розробниками (означення Ральфа Джонсона)", size=11.5, color=MUTED, italic=True))
    p.append(yearbox(236, "2003"))

    # проміжок 322..364
    p.append(arrow(cx, 326, cx, 360, color=INK, sw=2.4))

    # ── станція 3: ліфт архітектора — Гопе ──
    p.append(rect(bx, 364, bw, 96, fill="#e6f5f2", stroke="#2f9e8f", sw=1.9, rx=10))
    p.append(text(cx, 392, "Ґреґор Гопе, «The Software Architect Elevator», 2020", size=14, color="#1f7d70", bold=True))
    p.append(text(cx, 417, "ліфт: пентхаус ⇄ машинний зал — впливає впоперек рівнів", size=12, color=INK))
    p.append(text(cx, 441, "і відкладає незворотні рішення («продає опції»)", size=11.5, color=MUTED, italic=True))
    p.append(yearbox(380, "2020"))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід «впливу без влади»: з менеджменту — в архітектуру")


# ── FIG 5 (вставка proj): чотири фази ввімкнення межі ──────────────────────────
# Ідея: гейт розкочуємо фазами, де перші дві білд не червонять узагалі, третя
# червоніє лише на НОВЕ, і тільки на четвертій — чистий гейт для всіх. Кожна
# фаза — колонка: заголовок (ескалація кольору) → що робить → колір білда.
def fig_rollout_phases():
    W, H = 980, 380
    p = []
    cw, g, x0, top = 212, 24, 34, 56
    xs = [x0 + i * (cw + g) for i in range(4)]
    heads = [
        ("1 · Тихо", MUTED, "#eef0f2"),
        ("2 · Попередження", AMBER, AMBERBG),
        ("3 · Заморозка", POS, REDBG),
        ("4 · Чистий гейт", FIELD, GREENBG),
    ]
    bodies = [
        "перевірка рахує\nй пише в лог —\nу білд не лізе",
        "друкує список,\nмощену дорогу,\nлінк на ADR",
        "наявні — у базі;\nворота лише на\nНОВИЙ обхід",
        "база осушена —\nбудь-який обхід\nчервоний, для всіх",
    ]
    chips = [
        ("білд не чіпаємо", MUTED, "#eef0f2"),
        ("білд ЗЕЛЕНИЙ", FIELD, GREENBG),
        ("червоний на нове", POS, REDBG),
        ("повний гейт", FIELD, GREENBG),
    ]
    for i, x in enumerate(xs):
        htext, hcol, hbg = heads[i]
        p.append(fitbox(x, top, cw, 34, htext, size=13, pad=8,
                        fill=hbg, stroke=hcol, sw=1.8, color=INK, bold=True))
        p.append(fitbox(x, top + 44, cw, 128, bodies[i], size=12.5, pad=12,
                        fill="#fbfbfc", stroke="#e3e6ea", sw=1.3, color=INK))
        ctext, ccol, cbg = chips[i]
        p.append(fitbox(x, top + 186, cw, 40, ctext, size=12.5, pad=8,
                        fill=cbg, stroke=ccol, sw=1.7, color=INK, bold=True))

    ay = 308
    p.append(arrow(x0, ay, xs[3] + cw, ay, color=INK, sw=2.0))
    p.append(text(W / 2, 334, "фази розгортання — зліва направо, кожна дозріваліша за попередню",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "rollout-phases.svg"), W, H, *p,
           title="Розкат межі фазами: стіни першого дня не буває")


# ── FIG 6 (вставка proj): храповик базової лінії ──────────────────────────────
# Ідея: стеля дозволених порушень у базі спадає сходинками з кожним полагодженим
# обходом і НІКОЛИ не росте (храповик). Спроба нового обходу підняти лік понад
# стелю відскакує червоним білдом і в базу не входить — тому лінія лише вниз.
def fig_arch_ratchet():
    W, H = 900, 440
    p = []
    x0, xr, yb, yt = 110, 830, 360, 80

    def sx(t):
        return x0 + t * 72.0

    def sy(c):
        return yb - c * 11.25

    # осі
    p.append(arrow(x0, yb, xr + 8, yb, color=INK, sw=2.0))   # час →
    p.append(arrow(x0, yb, x0, yt - 4, color=INK, sw=2.0))   # база ↑
    p.append(text(470, 404, "час  →  влиті PR-и", size=12, color=MUTED, italic=True))
    p.append('<text x="44" y="220" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-style="italic" transform="rotate(-90 44 220)">'
             'дозволених порушень у базі</text>' % (FONT, MUTED))

    # сходи (t, c) — монотонно не зростають
    pts = [(0, 23), (1, 23), (1, 20), (3, 20), (3, 14), (5, 14),
           (5, 9), (7, 9), (7, 4), (9, 4), (9, 0), (10, 0)]
    ptstr = " ".join("%.1f,%.1f" % (sx(t), sy(c)) for t, c in pts)
    p.append('<polyline fill="none" stroke="%s" stroke-width="2.6" points="%s"/>' % (FIELD, ptstr))

    # заморозка на старті
    p.append(circle(sx(0), sy(23), 4.5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(sx(0) + 10, sy(23) - 9, "заморозка: 23", size=12, color=FIELD, anchor="start", bold=True))

    # анотація храповика — у вільній верхньо-правій зоні
    p.append(mtext(712, 120, "храповик:\nстеля лише спадає,\nвгору — ніколи",
                   size=12.5, color=INK, anchor="middle", lh=1.32, bold=True))
    p.append(arrow(806, 106, 806, 152, color=MUTED, sw=2.2))

    # відбитий новий обхід (червоний) — пробує підняти лік понад стелю
    xn, yc = sx(4), sy(14)
    p.append(arrow(xn, yc, xn, 170, color=POS, sw=2.0))
    p.append(text(xn, 164, "✗", size=15, color=POS, bold=True))
    p.append(text(415, 150, "новий обхід → ЧЕРВОНИЙ", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(415, 166, "(у базу не входить)", size=10.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "arch-ratchet.svg"), W, H, *p,
           title="Базова лінія з храповиком: стеля лише вниз")


if __name__ == "__main__":
    fig_authority_gap()
    fig_levers_ladder()
    fig_dh_play()
    fig_lineage()
    fig_rollout_phases()
    fig_arch_ratchet()
    print("OK:", OUT)
