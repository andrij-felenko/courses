# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # ключ / CC — теплий акцент


def usbc(p, x, y):
    """Маленький значок роз'єму USB-C ліворуч від ряду."""
    b, _, _ = textbox(x, y, "USB-C", size=10, bold=True, min_w=60)
    p.append(b)


# ── paths: три архітектури PD-приймача ───────────────────────────────────────
# Ідея: один рядок на архітектуру; спільне — VBUS-вихід на навантаження,
# відрізняється лише «хто веде розмову» і скільки свободи в реальному часі.

def fig_paths():
    W, H = 760, 470
    p = []
    rows = [
        (110, "Тригер", FIELD, "#eafaf0", "веде всю розмову сам",
         "ключ → одна задана напруга", "0 рядків коду · МК не потрібен"),
        (250, "PD-контролер", NEG, "#eef3fb", "веде переговори",
         "МК командує по I²C", "гнучко · протокол на чипі"),
        (390, "МК + PD-PHY", GOLD, "#fbf7ec", "сам говорить PD",
         "вбудований стек", "максимум волі · весь протокол твій"),
    ]
    for y, name, col, fill, sub, midlab, foot in rows:
        usbc(p, 70, y)
        p.append(line(108, y, 168, y, color=GOLD, sw=2.2))
        p.append(text(138, y - 8, "CC", size=10, color=GOLD, bold=True))
        bx, bw = 168, 168
        bbox, _, _ = textbox(bx + bw / 2, y, name + "\n" + sub,
                             size=12, bold=True, color=col, fill=fill, stroke=col, sw=2, min_w=bw)
        p.append(bbox)
        # ключ по power-good
        kx = 392
        kb, kw, _ = textbox(kx, y, "ключ", size=10, color=GOLD, fill="#fff7e6", stroke=GOLD, sw=1.6, min_w=56)
        p.append(kb)
        p.append(text(kx, y + 26, "power-good", size=9, color=MUTED))
        p.append(arrow(bx + bw, y, kx - kw / 2 - 2, y, color=col, sw=1.8))
        # VBUS до навантаження
        lx = 560
        p.append(arrow(kx + kw / 2 + 2, y, lx - 2, y, color=POS, sw=2.0))
        p.append(text((kx + kw / 2 + lx) / 2, y - 9, "VBUS", size=9, color=POS, bold=True))
        lbox, _, _ = textbox(lx + 70, y, "Навантаження", size=11, bold=True,
                             color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2, min_w=130)
        p.append(lbox)
        p.append(text(bx + bw / 2, y + 44, foot, size=10, color=col, bold=True))
        if midlab:
            p.append(text(bx + bw / 2, y - 40, midlab, size=9, color=MUTED, italic=True))

    p.append(text(W / 2, H - 14,
                  "у всіх трьох на VBUS — узгоджена напруга; різниця лише в тому, хто тримає розмову",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "paths.svg"), W, H, *p,
           title="Три шляхи дати пристрою PD: від автономного чипа до стека в МК")


# ── trigger: що всередині тригера ────────────────────────────────────────────
# Ідея: вхід CC/VBUS → апаратний рушій + список бажаних PDO + контроль ключа →
# навантаження дістає напругу лише після контракту.

def fig_trigger():
    W, H = 720, 360
    p = []
    # вхід
    p.append(text(70, 70, "вхід", size=10, color=MUTED, anchor="start"))
    usbc(p, 95, 110)
    p.append(text(95, 150, "CC1 / CC2", size=10, color=GOLD))
    p.append(text(95, 200, "VBUS", size=10, color=POS, bold=True))

    # корпус тригера
    cx0, cy0, cw, ch = 200, 60, 330, 240
    p.append(rect(cx0, cy0, cw, ch, fill="#f6fbf6", stroke=FIELD, sw=2))
    p.append(text(cx0 + cw / 2, cy0 + 20, "ТРИГЕР (sink-контролер)", size=12, color=FIELD, bold=True))

    inner = [
        (cy0 + 70, "апаратний PD-рушій", "сам робить рукостискання", "#eafaf0"),
        (cy0 + 130, "список бажаних PDO", "12 В → 9 В → 5 В (NVM/перемички)", "#eef3fb"),
        (cy0 + 190, "контроль VBUS-ключа", "замикає лише по power-good", "#fff7e6"),
    ]
    for yy, lab, sub, fill in inner:
        b = fitbox(cx0 + 24, yy - 24, cw - 48, 48, lab + "\n" + sub,
                   size=11, fill=fill, stroke=LINE, sw=1.4, bold=True)
        p.append(b)

    p.append(arrow(150, 130, cx0 - 2, 130, color=GOLD, sw=1.8))
    p.append(arrow(150, 200, cx0 - 2, 200, color=POS, sw=1.8))

    # вихід через ключ
    lx = 620
    p.append(arrow(cx0 + cw, 250, lx - 50, 250, color=POS, sw=2.2))
    p.append(text((cx0 + cw + lx - 50) / 2, 240, "12 В", size=10, color=POS, bold=True))
    lbox, _, _ = textbox(lx, 250, "Навантаження", size=11, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2, min_w=120)
    p.append(lbox)

    p.append(text(W / 2, H - 14, "розробник раз обирає, що просити, і пише нуль коду",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "trigger.svg"), W, H, *p,
           title="Що всередині тригера: апаратне рукостискання й ключ навантаження")


# ── nocontract: дерево безпечних відкатів ────────────────────────────────────
# Ідея: просимо профіль; дали — вмикаємо; ні — запасний; зовсім ні — лишаємось
# на 5 В і не вмикаємо навантаження.

def fig_nocontract():
    W, H = 720, 380
    p = []
    cx = W / 2

    def node(x, y, s, col, fill, w=190):
        b = fitbox(x - w / 2, y - 26, w, 52, s, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(b)
        return (x, y, w)

    top = node(cx, 70, "Просимо свій профіль\n(напр. 12 В)", INK, FILL, 220)

    # гілка «дали»
    okx = cx + 210
    ok = node(okx, 180, "Контракт дано\n→ вмикаємо навантаження", FIELD, "#eafaf0", 230)
    p.append(line(cx, top[1] + 26, okx, ok[1] - 26, color=FIELD, sw=1.8))
    p.append(text((cx + okx) / 2 + 30, 128, "так", size=10, color=FIELD, bold=True))

    # гілка «ні» → запасний
    nox = cx - 210
    no1 = node(nox, 180, "Запасний профіль\n(9 чи 15 В) — працюємо обмежено", NEG, "#eef3fb", 250)
    p.append(line(cx, top[1] + 26, nox, no1[1] - 26, color=NEG, sw=1.8))
    p.append(text((cx + nox) / 2 - 30, 128, "ні", size=10, color=NEG, bold=True))

    # зовсім ні → 5 В
    no2 = node(nox, 290, "Нема й того →\nлишаємось на 5 В,\nнавантаження ВИМКНЕНЕ", POS, "#fdecea", 250)
    p.append(arrow(nox, no1[1] + 26, nox, no2[1] - 28, color=POS, sw=1.8))
    p.append(text(nox + 80, 252, "теж ні", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "залізне правило: живлення на навантаження — ЛИШЕ за дійсним контрактом (power-good)",
                  size=11, color=POS, italic=True, bold=True))
    render(os.path.join(OUT, "nocontract.svg"), W, H, *p,
           title="Коли контракту не дали: дерево безпечних відкатів")


# ── wideinput: жорстка vs гнучка архітектура входу ───────────────────────────
# Ідея: ліворуч навантаження висить просто на VBUS і вимагає 12 В; праворуч —
# широковхідний buck-boost приймає будь-що 5..20 В і робить рівні 12 В.

def fig_wideinput():
    W, H = 740, 340
    p = []

    def chain(x0, title, col, items, foot):
        p.append(text(x0 + 150, 70, title, size=13, color=col, bold=True))
        y = 120
        prev_bottom = None
        for lab, sub, fill in items:
            b = fitbox(x0, y, 300, 54, lab + "\n" + sub, size=11, bold=True, fill=fill, stroke=LINE, sw=1.5)
            p.append(b)
            if prev_bottom is not None:
                p.append(arrow(x0 + 150, prev_bottom, x0 + 150, y - 2, color=col, sw=1.8))
            prev_bottom = y + 54
            y += 86
        p.append(text(x0 + 150, y + 6, foot, size=10, color=col, italic=True))

    chain(40, "Жорстка: треба РІВНО 12 В", POS, [
        ("USB-C → VBUS", "просимо саме 12 В", "#fff7e6"),
        ("Навантаження 12 В", "нема 12 В у меню → не вмикається", "#fdecea"),
    ], "прив'язана до тієї самої напруги")

    chain(400, "Гнучка: приймаємо що дали", FIELD, [
        ("USB-C → будь-який профіль 5–20 В", "ловимо найвигідніший", "#eef3fb"),
        ("Buck-boost → рівні 12 В", "оживає навіть від 5 В", "#eafaf0"),
    ], "ціна — зайвий перетворювач")

    render(os.path.join(OUT, "wideinput.svg"), W, H, *p,
           title="Широкий вхід замість точної вимоги напруги")


# ── runtime: що дає розум МК ──────────────────────────────────────────────────
# Ідея: МК читає меню й вибирає напругу за умовами в реальному часі — те, чого
# фіксований тригер не вміє в принципі.

def fig_runtime():
    W, H = 740, 340
    p = []
    # МК + контролер
    mk, mkw, _ = textbox(150, 110, "МК", size=13, bold=True, fill="#fff", stroke=INK, sw=2, min_w=90)
    p.append(mk)
    ctrl, cw, _ = textbox(150, 220, "PD-контролер", size=11, bold=True, color=NEG,
                          fill="#eef3fb", stroke=NEG, sw=1.8, min_w=140)
    p.append(ctrl)
    p.append(arrow(150, 134, 150, 196, color=NEG, sw=1.8))
    p.append(text(150, 175, "I²C", size=10, color=NEG, bold=True))
    p.append(text(150, 270, "читає меню,\nкомандує профілем", size=10, color=MUTED))

    # рішення за умовами
    decisions = [
        (110, "холодно, треба швидко", "→ 20 В, максимум потужності", FIELD),
        (175, "вузол перегрівся", "→ 15 В, менше гріти перетворювач", POS),
        (240, "заряджає батарею", "→ APDO/PPS, веде напругу за коміркою", NEG),
        (305, "споживання впало", "→ перепогоджує дрібніший контракт", MUTED),
    ]
    for yy, cond, act, col in decisions:
        b = fitbox(330, yy - 24, 380, 48, cond + "\n" + act, size=11, bold=True,
                   color=col, fill="#fafafa", stroke=col, sw=1.5)
        p.append(b)
        p.append(arrow(150 + mkw / 2, 110, 328, yy, color=col, sw=1.4))

    render(os.path.join(OUT, "runtime.svg"), W, H, *p,
           title="Що дає розум: МК міняє контракт PD за умовами на ходу")


# ── decision: карта вибору + два залізні правила ─────────────────────────────
# Ідея: одне питання — одна гілка; внизу два правила, спільні для всіх шляхів.

def fig_decision():
    W, H = 740, 360
    p = []
    paths = [
        (130, "Одна стала напруга,\nбез змін на ходу?", "ТРИГЕР", "просто · дешево · 0 коду", FIELD, "#eafaf0"),
        (370, "Міняти напругу\nчи вести PPS під МК?", "PD-КОНТРОЛЕР", "гнучко · чип бере протокол", NEG, "#eef3fb"),
        (610, "Без зайвого чипа,\nповний контроль?", "МК ЗІ СТЕКОМ", "максимум волі · максимум праці", GOLD, "#fbf7ec"),
    ]
    for x, q, ans, sub, col, fill in paths:
        p.append(fitbox(x - 100, 70, 200, 60, q, size=11, bold=True, fill=FILL, stroke=LINE, sw=1.5))
        p.append(arrow(x, 132, x, 158, color=col, sw=1.8))
        p.append(fitbox(x - 100, 160, 200, 58, ans + "\n" + sub, size=11, bold=True,
                        color=col, fill=fill, stroke=col, sw=2))

    # два правила
    p.append(line(40, 250, W - 40, 250, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(W / 2, 272, "Два залізні правила — незалежно від обраного шляху:", size=11, color=INK, bold=True))
    r1 = fitbox(60, 290, 300, 50, "1. Навантаження вмикати\nлише за дійсним контрактом (power-good)",
                size=10, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6)
    r2 = fitbox(380, 290, 300, 50, "2. Пристрій має пережити\nвідкат у 5 В (урізано або чесно мовчить)",
                size=10, bold=True, color=NEG, fill="#eef3fb", stroke=NEG, sw=1.6)
    p.append(r1)
    p.append(r2)

    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Карта вибору: тригер, контролер чи МК")


# ── fsm: машина станів sink (для proj-вставки) ───────────────────────────────
# Ідея: лінія успіху від 5 В до CONTRACT; спільна «червона шина» відкату на 5 В
# від будь-якої проблемної події.

def fig_fsm():
    W, H = 900, 360
    p = []
    states = ["VBUS_5V", "WAIT_CAPS", "CHOOSE", "REQ_SENT", "WAIT_PSRDY", "CONTRACT"]
    edges = ["attach", "caps", "Request", "Accept", "PS_RDY"]
    y = 110
    x = 40
    bw, gap = 118, 18
    centers = []
    for i, s in enumerate(states):
        col = FIELD if s == "CONTRACT" else (NEG if s == "VBUS_5V" else INK)
        fill = "#eafaf0" if s == "CONTRACT" else ("#eef3fb" if s == "VBUS_5V" else FILL)
        b = fitbox(x, y - 26, bw, 52, s, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(b)
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y, x - 2, y, color=INK, sw=1.7))
            mx = (centers[i - 1][1] + x) / 2
            p.append(text(mx, y - 16, edges[i - 1], size=9, color=MUTED))
        x += bw + gap

    # червона шина відкату
    busy = 250
    p.append(line(60, busy, W - 60, busy, color=POS, sw=2.4))
    p.append(text(W / 2, busy + 40, "Reject · таймаут · від'єднання · Hard Reset · нове меню",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, busy + 60, "→ disable_load(); повертаємось у VBUS_5V", size=10, color=POS, italic=True))
    # стрілки вниз від проміжних станів до шини
    for i in (1, 2, 3, 4, 5):
        mx = (centers[i][0] + centers[i][1]) / 2
        p.append(arrow(mx, y + 26, mx, busy - 2, color=POS, sw=1.4))
    # повернення шини в 5 В
    sx = (centers[0][0] + centers[0][1]) / 2
    p.append(line(60, busy, sx, busy, color=POS, sw=2.4))
    p.append(arrow(sx, busy, sx, y + 28, color=POS, sw=1.8))

    p.append(text(W / 2, 70, "політика pick_pdo обирає профіль за пріоритетом і звіряє струм",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "fsm.svg"), W, H, *p,
           title="Машина станів PD-sink: уперед по подіях, відкат на 5 В за будь-якої біди")


# ── timing: часова вісь від під'єднання до контракту (detailed) ──────────────
# Ідея: горизонтальна вісь подій; над кожним відтинком — дедлайн; знизу спільна
# червона лінія відкату в 5 В від будь-якого простроченого дедлайну.

def fig_timing():
    W, H = 900, 380
    p = []
    y = 150
    # вузли-події вздовж осі
    nodes = [
        (70,  "Rd\n(пасивний)", NEG, "#eef3fb"),
        (215, "VBUS 5 В", INK, FILL),
        (370, "меню\ncaps", INK, FILL),
        (525, "Request →\nAccept", INK, FILL),
        (690, "підняття\nнапруги", INK, FILL),
        (835, "PS_RDY →\nнавантаження", FIELD, "#eafaf0"),
    ]
    cxs = []
    for x, s, col, fill in nodes:
        b = fitbox(x - 62, y - 26, 124, 52, s, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(b)
        cxs.append(x)
    # стрілки між подіями + дедлайни над ними
    spans = [
        (0, 1, "джерело бачить Rd", None),
        (1, 2, "SinkWaitCap", "сотні мс"),
        (2, 3, "", None),
        (3, 4, "SenderResponse", "24–33 мс"),
        (4, 5, "PSTransition", "до 550 мс"),
    ]
    for a, b, lab, sub in spans:
        x1, x2 = cxs[a] + 62, cxs[b] - 62
        p.append(arrow(x1, y, x2 - 2, y, color=INK, sw=1.7))
        mx = (x1 + x2) / 2
        if lab:
            p.append(text(mx, y - 40, lab, size=10, color=MUTED, bold=True))
        if sub:
            p.append(text(mx, y - 26, sub, size=9, color=MUTED, italic=True))

    # спільна лінія відкату
    busy = 290
    p.append(line(70, busy, W - 60, busy, color=POS, sw=2.4))
    for i in (2, 3, 4):
        p.append(arrow(cxs[i], y + 26, cxs[i], busy - 2, color=POS, sw=1.4))
    p.append(text(W / 2, busy + 26,
                  "будь-який прострочений дедлайн → відкат у безпечні 5 В, навантаження геть",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, 62, "живлення на навантаження — лише після PS_RDY (контракт стоїть)",
                  size=10, color=FIELD, italic=True, bold=True))
    render(os.path.join(OUT, "timing.svg"), W, H, *p,
           title="Бюджет часу: від пасивного Rd до контракту")


# ── inrush: різке vs плавне замикання ключа (detailed) ───────────────────────
# Ідея: два графіки V(t) на вхідній ємності; різке дає велике dV/dt і кидок,
# плавне — розтягнуте dV/dt і малий кидок. Формула I = C·dV/dt збоку.

def fig_inrush():
    W, H = 760, 400
    p = []

    def plot(x0, title, col, steep, foot):
        gx, gy, gw, gh = x0, 90, 260, 170
        # осі
        p.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.4))
        p.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.4))
        p.append(text(gx - 8, gy + 6, "V", size=10, color=MUTED, anchor="end"))
        p.append(text(gx + gw, gy + gh + 16, "t", size=10, color=MUTED))
        p.append(text(x0 + gw / 2, 74, title, size=12, color=col, bold=True))
        # крива напруги на ємності
        top = gy + 14
        if steep:
            # майже вертикальний фронт
            p.append(line(gx, gy + gh, gx + 24, top, color=col, sw=2.6))
            p.append(line(gx + 24, top, gx + gw, top, color=col, sw=2.6))
            kx = gx + 12
        else:
            # пологий фронт
            p.append(line(gx, gy + gh, gx + gw - 40, top, color=col, sw=2.6))
            p.append(line(gx + gw - 40, top, gx + gw, top, color=col, sw=2.6))
            kx = gx + (gw - 40) / 2
        p.append(text(gx + gw - 6, top - 6, "12 В", size=9, color=col, anchor="end"))
        p.append(text(x0 + gw / 2, gy + gh + 40, foot, size=10, color=col, bold=True))

    plot(70, "Різко: dV/dt велике", POS,  True,  "кидок ≈ 24 А → просадка / скид контракту")
    plot(430, "Плавно: dV/dt розтягнуте", FIELD, False, "кидок ≈ 2 А → чистий старт (~0.6 мс)")

    p.append(fitbox(W / 2 - 150, 300, 300, 46, "I = C · dV/dt\nтой самий C, менше dV/dt → менший кидок",
                    size=11, bold=True, color=INK, fill="#fff7e6", stroke=GOLD, sw=1.6))
    render(os.path.join(OUT, "inrush.svg"), W, H, *p,
           title="Кидок струму при ввімкненні: різко проти плавного старту")


# ── failures: таксономія відмов у три стовпці (detailed) ─────────────────────
# Ідея: три сімейства відмов; усі стрілки збігаються в один fall_to_safe.

def fig_failures():
    W, H = 900, 460
    p = []
    cols = [
        (160, "Узгодження", NEG, "#eef3fb",
         ["не PD-джерело", "Reject профілю", "Wait (спробуй пізніше)", "мовчання на півслові"]),
        (450, "Потужність", GOLD, "#fbf7ec",
         ["стеля струму замала", "кабель без e-marker", "кидок при старті"]),
        (740, "Утримання", POS, "#fdecea",
         ["переукладання меню", "Hard Reset будь-коли", "EPR KeepAlive прострочено", "від'єднання"]),
    ]
    bottoms = []
    for cx, title, col, fill, items in cols:
        p.append(text(cx, 66, title, size=13, color=col, bold=True))
        y = 88
        for it in items:
            p.append(fitbox(cx - 130, y, 260, 40, it, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.5))
            y += 50
        bottoms.append((cx, y))

    # спільний вузол fall_to_safe
    fy = 360
    fb = fitbox(W / 2 - 200, fy, 400, 54,
                "fall_to_safe(): навантаження геть · лишаємось на 5 В · за потреби сигналимо",
                size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2.2)
    for cx, by in bottoms:
        p.append(arrow(cx, by + 2, W / 2 + (cx - W / 2) * 0.15, fy - 2, color=POS, sw=1.5))
    p.append(fb)
    p.append(text(W / 2, fy + 78,
                  "різниться лише причина й чи варто пробувати ще (Wait — так, Reject того ж профілю — ні)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "failures.svg"), W, H, *p,
           title="Таксономія відмов sink → єдина безпечна реакція")


# ── cost: хто розв'язує задачі механіки (detailed) ───────────────────────────
# Ідея: рядки-задачі × три шляхи; зелене — бере чип, червоне — розробник.

def fig_cost():
    W, H = 820, 420
    p = []
    rows = [
        "холодний старт (Rd)",
        "таймери переговорів",
        "логіка pick_pdo",
        "плавний старт ключа",
        "EPR KeepAlive",
        "переукладання на ходу",
    ]
    # хто бере: "chip"=зелене, "dev"=червоне, "obv"=жовте (обв'язка), "-"=немає
    grid = {
        "Тригер":       ["chip", "chip", "-",   "obv", "chip", "-"],
        "Контролер+МК": ["chip", "chip", "dev", "obv", "chip", "dev"],
        "МК зі стеком": ["dev",  "dev",  "dev", "obv", "dev",  "dev"],
    }
    colx = [420, 580, 740]
    heads = list(grid.keys())
    y0 = 80
    rh = 46
    # заголовки стовпців
    for x, h in zip(colx, heads):
        p.append(text(x, y0 - 12, h, size=11, color=INK, bold=True))
    # рядки
    for r, name in enumerate(rows):
        yy = y0 + r * rh
        p.append(text(40, yy + 22, name, size=11, color=INK, anchor="start"))
        for c, x in enumerate(colx):
            kind = grid[heads[c]][r]
            if kind == "-":
                p.append(text(x, yy + 24, "—", size=13, color=MUTED))
                continue
            col, fill, lab = {
                "chip": (FIELD, "#eafaf0", "чип"),
                "dev":  (POS,   "#fdecea", "твій"),
                "obv":  (GOLD,  "#fbf7ec", "обв'язка"),
            }[kind]
            p.append(fitbox(x - 62, yy + 6, 124, 32, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.5))

    p.append(text(W / 2, y0 + len(rows) * rh + 24,
                  "угору кожен рівень ПОВЕРТАЄ розробнику задачу, яку нижчий уже розв'язав",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "cost.svg"), W, H, *p,
           title="Вартість розуму: зелене бере чип, червоне — розробник")


# ── drop_awg: опір за калібром і КВАДРАТИЧНІ втрати тепла (math-cable-drop-power) ─
# Ідея: одна таблиця показує три речі разом — тонший дріт різко опірніший;
# на 5 В той самий пристрій гріє кабель у рази більше, ніж на 20 В (I²·R);
# і що втрати ростуть як КВАДРАТ струму, тож стовпчик 5 В вибухає, а 20 В — тихий.

def fig_drop_awg():
    W, H = 820, 430
    p = []
    # погонний опір (Ом/м, суцільна мідь ~20 °C) для типових жил силової пари USB
    gauges = [("20 AWG", 0.033), ("24 AWG", 0.084),
              ("28 AWG", 0.213), ("30 AWG", 0.339)]
    # пристрій 24 Вт; втрати тепла в кабелі (дві жили, 1 м) для трьох напруг
    P = 24.0
    cols = [("з 5 В", 4.80, POS), ("з 12 В", 2.00, GOLD), ("з 20 В", 1.20, FIELD)]

    x0, y0 = 40, 96
    wg = 128          # стовпчик назви калібру
    wr = 132          # стовпчик опору
    wc = 138          # стовпчик втрат на напругу
    xr = x0 + wg          # ліва межа стовпчика опору
    xL = x0 + wg + wr     # ліва межа групи стовпчиків втрат
    rh = 58
    # шапка
    p.append(text(x0 + wg / 2, y0 - 14, "жила", size=11, color=INK, bold=True))
    p.append(text(xr + wr / 2, y0 - 14, "R кабелю, 1 м", size=11, color=INK, bold=True))
    p.append(text(xL + 1.5 * wc, y0 - 32, "теплові втрати I²·R (Вт)", size=11, color=INK, bold=True))
    for j, (lab, I, col) in enumerate(cols):
        p.append(text(xL + j * wc + wc / 2, y0 - 14, lab, size=10, color=col, bold=True))
    # рядки
    for i, (name, rho) in enumerate(gauges):
        yy = y0 + i * rh
        # калібр
        p.append(fitbox(x0, yy, wg - 10, rh - 12, name, size=13, bold=True,
                        color=INK, fill=FILL, stroke=LINE, sw=1.4))
        # опір двох жил на 1 м
        R = 2 * rho
        p.append(text(xr + wr / 2, yy + rh / 2 + 4, "%.3f Ом" % R,
                      size=12, color=MUTED))
        # втрати для кожної напруги — заливка тим гарячіша, чим більше ват
        for j, (lab, I, col) in enumerate(cols):
            loss = I * I * R
            cx = xL + j * wc
            fill = {POS: "#fdecea", GOLD: "#fbf7ec", FIELD: "#eafaf0"}[col]
            p.append(fitbox(cx + 8, yy + 6, wc - 16, rh - 20, "%.2f" % loss,
                            size=13, bold=True, color=col, fill=fill, stroke=col, sw=1.5))

    yb = y0 + len(gauges) * rh + 8
    p.append(fitbox(x0, yb, W - 2 * x0, 40,
                    "той самий пристрій, той самий кабель — лише напруга інша: "
                    "струм упав у 4 рази (5→20 В), а втрати впали в 16 (I² !)",
                    size=11, bold=True, color=INK, fill="#fff7e6", stroke=GOLD, sw=1.6))
    render(os.path.join(OUT, "drop-awg.svg"), W, H, *p,
           title="Опір за калібром і квадратичні втрати: 24 Вт на кабелі 1 м")


# ── drop_optimum: спільний оптимум кабель+перетворювач (math-cable-drop-power) ──
# Ідея: вища напруга завжди краща для КАБЕЛЯ, та не завжди для ПЕРЕТВОРЮВАЧА.
# На короткому товстому кабелі виграє нижча вища-ефективність (12 В); на довгому
# тонкому — кабель диктує, і виграє висока напруга (20 В). Оптимум зсувається.

def fig_drop_optimum():
    W, H = 840, 420
    p = []

    def panel(x0, title, note, data, win):
        # data: [(V, cable_W, conv_W, col)] ; win — індекс переможця
        gw, gh = 300, 210
        gy = 96
        p.append(text(x0 + gw / 2, 74, title, size=13, color=INK, bold=True))
        # осі
        p.append(line(x0, gy, x0, gy + gh, color=INK, sw=1.4))
        p.append(line(x0, gy + gh, x0 + gw, gy + gh, color=INK, sw=1.4))
        p.append(text(x0 - 8, gy + 4, "Вт", size=10, color=MUTED, anchor="end"))
        totals = [c + v for _, c, v, _ in data]
        scale = (gh - 24) / max(totals)
        bw = 46
        gap = (gw - len(data) * bw) / (len(data) + 1)
        for i, (V, cab, conv, col) in enumerate(data):
            bx = x0 + gap + i * (bw + gap)
            hc = cab * scale
            hv = conv * scale
            base = gy + gh
            # кабель (низ, гарячий) + перетворювач (верх, приглушений)
            p.append(rect(bx, base - hc, bw, hc, fill="#fdecea", stroke=POS, sw=1.4))
            p.append(rect(bx, base - hc - hv, bw, hv, fill="#eef3fb", stroke=NEG, sw=1.4))
            tot = cab + conv
            tcol = FIELD if i == win else INK
            p.append(text(bx + bw / 2, base - hc - hv - 8, "%.1f" % tot,
                          size=11, color=tcol, bold=(i == win)))
            p.append(text(bx + bw / 2, base + 16, "%d В" % V, size=10, color=col, bold=True))
            if i == win:
                p.append(text(bx + bw / 2, base + 30, "◀ оптимум", size=9, color=FIELD, bold=True))
        p.append(text(x0 + gw / 2, gy + gh + 52, note, size=10, color=MUTED, italic=True))

    # короткий товстий кабель R≈0.15 Ом: падіння мале → вирішує ККД, виграє 12 В
    # (кабель, перетворювач) — ті самі числа, що в прозі math-cable-drop-power
    short = [(5, 4.78, 4.24, POS), (9, 1.32, 2.67, GOLD),
             (12, 0.67, 1.26, FIELD), (20, 0.25, 1.81, NEG)]
    # довгий тонкий кабель R≈1.0 Ом: кабель диктує, виразно виграє 20 В
    long = [(5, 31.9, 4.24, POS), (9, 8.78, 2.67, GOLD),
            (12, 4.45, 1.26, GOLD), (20, 1.66, 1.81, FIELD)]
    panel(60, "Короткий товстий кабель (R ≈ 0.15 Ом)",
          "падіння мале → вирішує ККД перетворювача (12→12 майже даром)", short, 2)
    panel(470, "Довгий тонкий кабель (R ≈ 1.0 Ом)",
          "падіння велике → вирішує кабель, виграє висока напруга", long, 3)

    # легенда
    p.append(rect(60, H - 34, 14, 14, fill="#fdecea", stroke=POS, sw=1.4))
    p.append(text(80, H - 22, "втрати в кабелі (I²·R)", size=10, color=INK, anchor="start"))
    p.append(rect(300, H - 34, 14, 14, fill="#eef3fb", stroke=NEG, sw=1.4))
    p.append(text(320, H - 22, "втрати в перетворювачі", size=10, color=INK, anchor="start"))
    render(os.path.join(OUT, "drop-optimum.svg"), W, H, *p,
           title="Спільний оптимум: кабель любить вищу напругу, перетворювач — не завжди")


# ── hist-negotiation: як росла стеля потужності разом зі способом розмови ─────
# Ідея (для вставки-історії): одна вісь — потужність, що дереться вгору роками;
# під кожним стовпчиком — ЯК тоді домовлялися (ніяк → короткий D+/D- → FSK по
# VBUS з жорсткими профілями → BMC по CC з гнучкими PDO → EPR). Наприкінці —
# тригер: він не додає ват, він ХОВАЄ всю цю розмову в залізо для простого sink.

def fig_history():
    import math
    W, H = 780, 440
    p = []
    base = 300          # лінія нуля стовпчиків
    gx0 = 70
    gw = W - 2 * gx0
    n = 5
    step = gw / n
    bw = 66
    pmax = 240.0
    hmax = 205.0        # найвищий стовпчик у px

    # (рік, потужність Вт, стеля-напруга, як домовлялися, колір)
    eras = [
        (1996, 2.5,  "5 В · 0.5 А",  ["USB 1.0:", "порт МОВЧИТЬ,", "фіксовані 5 В"], MUTED),
        (2010, 7.5,  "5 В · 1.5 А",  ["BC 1.2:", "коротять D+/D−,", "сигнал без слів"], GOLD),
        (2012, 100.0, "20 В · 5 А",  ["PD 1.0:", "FSK по VBUS,", "жорсткі профілі"], NEG),
        (2014, 100.0, "20 В · 5 А",  ["PD 2.0 / USB-C:", "BMC по CC,", "гнучкі PDO"], FIELD),
        (2021, 240.0, "48 В · 5 А",  ["PD 3.1 EPR:", "та сама CC,", "стеля вгору"], POS),
    ]

    fills = {MUTED: "#eef0f2", GOLD: "#fbf7ec", NEG: "#eef3fb",
             FIELD: "#eafaf0", POS: "#fdecea"}
    for i, (yr, pw, ceil, how, col) in enumerate(eras):
        cx = gx0 + step * i + step / 2
        bx = cx - bw / 2
        # логарифмічна висота — щоб 2.5 Вт було видно поруч із 240 Вт
        h = hmax * (math.log10(pw) - math.log10(2.0)) / (math.log10(pmax) - math.log10(2.0))
        h = max(h, 12)
        p.append(rect(bx, base - h, bw, h, fill=fills[col], stroke=col, sw=1.8))
        wlab = ("%d Вт" % pw) if pw >= 10 else ("%.1f Вт" % pw)
        p.append(text(cx, base - h - 8, wlab, size=12, color=col, bold=True))
        p.append(text(cx, base + 18, str(yr), size=13, color=INK, bold=True))
        p.append(text(cx, base + 34, ceil, size=10, color=MUTED))
        p.append(mtext(cx, base + 56, how, size=9, color=col, bold=True))

    # вісь
    p.append(line(gx0 - 6, base, W - gx0 + 6, base, color=INK, sw=2.0))
    p.append(text(gx0 - 6, base - hmax - 8, "потужність (лог-шкала) ↑",
                  size=10, color=MUTED, anchor="start"))

    # PD1.0 → PD2.0: та сама стеля, інша розмова
    xa = gx0 + step * 2 + step / 2
    xb = gx0 + step * 3 + step / 2
    yln = base - hmax - 22
    p.append(line(xa, yln, xb, yln, color=INK, sw=1.2, dash="4 3"))
    p.append(text((xa + xb) / 2, yln - 5,
                  "стеля та сама — змінилась РОЗМОВА", size=9, color=INK, bold=True))

    # підсумок: тригер ховає всю цю розмову в залізо
    b, _, _ = textbox(W / 2, base + 100,
        "PD-тригер: не додає жодного вата — ХОВАЄ всю цю еволюцію переговорів\n"
        "у залізо, щоб простий пристрій дістав свою напругу без рядка коду",
        size=11, pad=12, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    p.append(b)

    render(os.path.join(OUT, "history.svg"), W, H, *p,
           title="Стеля лізе вгору, а розмова — від німоти до гнучких PDO")


if __name__ == "__main__":
    fig_history()
    fig_paths()
    fig_trigger()
    fig_nocontract()
    fig_wideinput()
    fig_runtime()
    fig_decision()
    fig_fsm()
    fig_timing()
    fig_inrush()
    fig_failures()
    fig_cost()
    fig_drop_awg()
    fig_drop_optimum()
    print("OK: figures written to", OUT)
