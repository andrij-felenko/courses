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


if __name__ == "__main__":
    fig_paths()
    fig_trigger()
    fig_nocontract()
    fig_wideinput()
    fig_runtime()
    fig_decision()
    fig_fsm()
    print("OK: figures written to", OUT)
