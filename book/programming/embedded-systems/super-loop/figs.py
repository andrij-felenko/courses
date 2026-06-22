# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Super-loop» та її історичної вставки.
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
REDBG   = "#fdecea"
GREYBG  = "#eef2f7"
MONO    = "'Consolas', 'DejaVu Sans Mono', monospace"


def mono_text(x, y, s, size=14, color=INK, anchor="start"):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s">%s</text>' % (x, y, MONO, size, color, anchor, esc(s)))


# ═══════════════════ СТАТТЯ «SUPER-LOOP» ════════════════════════════════════

# ── 1. setup() раз, loop() вічно ─────────────────────────────────────────────
# Ідея: дві частини моделі — setup один раз згори, loop у вічному колі.
def fig_setup_loop():
    W, H = 900, 430
    P = [text(W / 2, 30, "Super-loop: setup() один раз, loop() вічно", size=17, bold=True)]

    # старт
    fr, w, h = textbox(W / 2, 90, "старт (живлення / reset)", size=12.5, bold=True,
                       color=INK, fill=GREYBG, stroke=INK)
    P.append(fr)
    # setup
    fr, w, h = textbox(W / 2, 165, "setup()\nналаштувати один раз", size=13, bold=True,
                       color=NEG, fill=BLUEBG, stroke=NEG, min_w=300)
    P.append(fr)
    P.append(arrow(W / 2, 108, W / 2, 165 - h / 2, color=MUTED))
    P.append(text(W / 2 + 175, 150, "режими ніжок, зв'язок,\nпочаткові значення",
                  size=10.5, color=MUTED, anchor="start"))

    # loop у кільці
    cy = 300
    fr, w, h = textbox(W / 2, cy, "loop()\nробочий цикл", size=13, bold=True,
                       color=FIELD, fill=GRNBG, stroke=FIELD, min_w=260)
    P.append(fr)
    P.append(arrow(W / 2, 165 + h / 2 + 6, W / 2, cy - h / 2, color=MUTED))

    # кільце «знову й знову» праворуч від loop
    P.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (W / 2 + w / 2, cy - 10, W / 2 + w / 2 + 150, cy - 70,
                W / 2 + w / 2 + 150, cy + 70, W / 2 + w / 2, cy + 10, FIELD))
    P.append(text(W / 2 + w / 2 + 120, cy + 5, "знову\nй знову", size=11.5,
                  color=FIELD, bold=True, anchor="start"))

    fr, w, h = textbox(W / 2 - 150, 390,
                       "налаштував — і вічно тягнеш робочий цикл",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/setup-loop.svg", W, H, *P)


# ── 2. Під капотом — звичайний main() ────────────────────────────────────────
# Ідея: ланцюг reset → завантажувач → main() → setup() раз → loop() у for(;;).
def fig_under_hood():
    W, H = 980, 320
    P = [text(W / 2, 30, "Під капотом — звичайний main()", size=17, bold=True),
         text(W / 2, 50, "«super-loop» — не магія Arduino, а проста програма мовою C",
              size=11, color=MUTED, italic=True)]

    cy = 150
    boxes = [
        ("reset", GREYBG, INK, 95),
        ("завантажувач", GREYBG, INK, 150),
        ("main()", BLUEBG, NEG, 130),
        ("setup()\nодин раз", BLUEBG, NEG, 140),
        ("loop()\nу for(;;)", GRNBG, FIELD, 140),
    ]
    x = 70
    centers = []
    for label, fill, col, bw in boxes:
        fr, w, h = textbox(x + bw / 2, cy, label, size=12.5, bold=True,
                           color=col, fill=fill, stroke=col, min_w=bw)
        P.append(fr)
        centers.append((x + bw / 2, w))
        x += bw + 40
    for i in range(len(centers) - 1):
        cxa, wa = centers[i]
        cxb, wb = centers[i + 1]
        P.append(arrow(cxa + wa / 2, cy, cxb - wb / 2, cy, color=MUTED))

    # кільце над loop()
    lx, lw = centers[-1]
    P.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (lx + lw / 2, cy - 8, lx + lw / 2 + 70, cy - 80,
                lx - lw / 2 - 70, cy - 80, lx - lw / 2, cy - 8, FIELD))
    P.append(text(lx, cy - 72, "вічно", size=11, color=FIELD, bold=True))

    fr, w, h = textbox(W / 2, 270,
                       "між вашим кодом і процесором немає операційної системи — це «голе залізо»",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/under-hood.svg", W, H, *P)


# ── 3. Цикл «читай — обчисли — дій» ──────────────────────────────────────────
# Ідея: три кроки по колу — опитати входи, вирішити, оновити виходи.
def fig_read_compute_act():
    W, H = 760, 540
    P = [text(W / 2, 30, "Класичний цикл: читай → обчисли → дій", size=17, bold=True)]

    cx, cy, R = W / 2, 300, 150
    nodes = [
        ("ЧИТАЙ\nдавачі, кнопки", NEG, BLUEBG, -90),
        ("ОБЧИСЛИ\nприйми рішення", AMBER, AMBERBG, 30),
        ("ДІЙ\nвиходи: LED, мотор", FIELD, GRNBG, 150),
    ]
    pts = []
    for label, col, fill, deg in nodes:
        a = math.radians(deg)
        nx, ny = cx + R * math.cos(a), cy + R * math.sin(a)
        pts.append((nx, ny, label, col, fill))
    # стрілки по колу між вузлами
    for i in range(3):
        x1, y1, *_ = pts[i]
        x2, y2, *_ = pts[(i + 1) % 3]
        # вкоротити до країв «бульбашок»
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        P.append(arrow(x1 + ux * 70, y1 + uy * 55, x2 - ux * 70, y2 - uy * 55,
                       color=MUTED, sw=2.0))
    for nx, ny, label, col, fill in pts:
        fr, w, h = textbox(nx, ny, label, size=12.5, bold=True, color=col,
                           fill=fill, stroke=col)
        P.append(fr)
    P.append(text(cx, cy + 4, "щооберту", size=12, color=MUTED, italic=True))

    fr, w, h = textbox(W / 2, 500,
                       "один прохід loop() — такт «опитати світ → подумати → відповісти»",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/read-compute-act.svg", W, H, *P)


# ── 4. Дві сцени: передній план і тло ────────────────────────────────────────
# Ідея: неквапний loop() попереду; ISR вихоплює процесор на термінове й вертає.
def fig_foreground_background():
    W, H = 960, 420
    P = [text(W / 2, 30, "Дві сцени: головний цикл (рутина) + ISR (термінове)",
              size=17, bold=True)]

    # вісь часу головного циклу
    ax_y = 175
    P.append(arrow(70, ax_y, 890, ax_y, color=INK, sw=1.8))
    P.append(text(890, ax_y + 22, "час →", size=12, color=INK, bold=True))
    P.append(text(150, ax_y - 44, "ПЕРЕДНІЙ ПЛАН — loop()", size=12, color=FIELD,
                  bold=True, anchor="start"))
    # блоки рутини
    for x, w in [(90, 180), (290, 150), (470, 200), (700, 160)]:
        P.append(rect(x, ax_y - 30, w, 30, fill=GRNBG, stroke=FIELD, sw=1.5))
        P.append(text(x + w / 2, ax_y - 10, "рутина", size=11, color=FIELD))

    # ISR — спалахи з тла
    P.append(text(W / 2, 350, "ТЛО — ISR: натискання, прихід байта, переповнення таймера",
                  size=12, color=POS, bold=True))
    for sx in (255, 545, 690):
        P.append(line(sx, ax_y, sx, 320, color=POS, sw=1.4, dash="4 3"))
        P.append(rect(sx - 45, 300, 90, 28, fill=REDBG, stroke=POS, sw=1.6))
        P.append(text(sx, 318, "ISR", size=11, color=POS, bold=True))
        P.append(text(sx, ax_y - 36, "↯", size=14, color=POS, bold=True))

    fr, w, h = textbox(W / 2, 392,
                       "термінове ISR робить ПОЗА чергою; рутину цикл тягне неквапно",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/foreground-background.svg", W, H, *P)


# ── 5. Як швидко крутиться цикл ───────────────────────────────────────────────
# Ідея: короткий цикл — багато швидких обертів; один довгий крок розтягує оберт.
def fig_loop_timing():
    W, H = 960, 430
    P = [text(W / 2, 30, "Швидкість циклу визначає його найповільніший крок",
              size=17, bold=True)]

    # верх — короткі оберти
    y1 = 130
    P.append(text(70, y1 - 36, "КОРОТКИЙ loop() — багато швидких обертів", size=12,
                  color=FIELD, bold=True, anchor="start"))
    P.append(arrow(70, y1, 890, y1, color=INK, sw=1.6))
    x = 90
    for _ in range(11):
        P.append(rect(x, y1 - 24, 60, 24, fill=GRNBG, stroke=FIELD, sw=1.3))
        x += 70
    P.append(text(W / 2, y1 + 24, "реакція майже миттєва", size=11, color=MUTED))

    # низ — один довгий крок
    y2 = 300
    P.append(text(70, y2 - 36, "ОДИН ДОВГИЙ КРОК — оберт розтягнувся, усе чекає",
                  size=12, color=POS, bold=True, anchor="start"))
    P.append(arrow(70, y2, 890, y2, color=INK, sw=1.6))
    P.append(rect(90, y2 - 24, 60, 24, fill=GRNBG, stroke=FIELD, sw=1.3))
    P.append(rect(160, y2 - 24, 520, 24, fill=REDBG, stroke=POS, sw=1.8))
    P.append(text(420, y2 - 8, "delay(1000) — пристрій «заморожений»", size=11.5,
                  color=POS, bold=True))
    P.append(rect(690, y2 - 24, 60, 24, fill=GRNBG, stroke=FIELD, sw=1.3))
    P.append(text(770, y2 + 22, "усе інше чекає кінця довгого кроку", size=11, color=MUTED))

    fr, w, h = textbox(W / 2, 390,
                       "поки тягнеться один тривалий виклик — ні читання, ні оновлення виходу",
                       size=12, bold=True, color=POS, fill=REDBG, stroke=POS)
    P.append(fr)
    render("img/loop-timing.svg", W, H, *P)


# ── 6. Кілька справ через millis() — без блокування ──────────────────────────
# Ідея: один цикл звіряє годинник і запускає лише дозрілі справи (різні ритми).
def fig_several_jobs():
    W, H = 960, 440
    P = [text(W / 2, 30, "Кілька справ в одному циклі через millis() — без блокування",
              size=17, bold=True)]

    # центр — цикл звіряє годинник
    fr, w, h = textbox(W / 2, 95, "loop(): now = millis() — «чи не час?»", size=13,
                       bold=True, color=INK, fill=GREYBG, stroke=INK)
    P.append(fr)

    jobs = [
        ("LED", "щосекунди", FIELD, GRNBG, 200),
        ("давач", "5 разів/с", NEG, BLUEBG, W / 2),
        ("серцебиття", "раз на 5 с", AMBER, AMBERBG, 760),
    ]
    jy = 240
    for label, rhythm, col, fill, jx in jobs:
        fr, w, h = textbox(jx, jy, "%s\n%s" % (label, rhythm), size=12.5, bold=True,
                           color=col, fill=fill, stroke=col, min_w=180)
        P.append(fr)
        P.append(arrow(W / 2, 95 + 18, jx, jy - h / 2, color=MUTED))

    fr, w, h = textbox(W / 2, 350,
                       "кожна спрацьовує у свій час; цикл лише перевіряє millis() "
                       "й нікого не блокує",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    fr, w, h = textbox(W / 2, 405,
                       "порівняння now − t >= interval переживає переповнення лічильника",
                       size=11, color=INK, fill=BG, stroke=MUTED)
    P.append(fr)
    render("img/several-jobs.svg", W, H, *P)


# ═══════════════════ ВСТАВКА «ПОДІЛ ЧАСУ» (історія) ═════════════════════════

# ── insert 1. Одна машина — багатьом ─────────────────────────────────────────
# Ідея: ліворуч черга (троє нудяться), праворуч поділ часу (кожному «вся машина»).
def fig_the_question():
    W, H = 960, 430
    P = [text(W / 2, 30, "Одна машина — багатьом: черга проти поділу часу",
              size=17, bold=True)]

    # ЛІВОРУЧ — пакетна черга
    P.append(fitbox(60, 70, 380, 32, "ПАКЕТНА ЧЕРГА", size=13, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    mx, my = 150, 200
    P.append(rect(mx - 50, my - 35, 100, 70, fill=GREYBG, stroke=INK, sw=1.8))
    P.append(text(mx, my, "машина", size=11, color=INK, bold=True))
    for i in range(3):
        P.append(circle(mx + 130 + i * 55, my, 18, fill=BG, stroke=MUTED, sw=1.5))
        P.append(text(mx + 130 + i * 55, my + 4, "?", size=13, color=MUTED, bold=True))
    P.append(text(250, my + 60, "троє нудяться, поки рахує один", size=11,
                  color=POS, bold=True))

    # ПРАВОРУЧ — поділ часу
    P.append(fitbox(520, 70, 380, 32, "ПОДІЛ ЧАСУ", size=13, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    bx, by = 700, 200
    P.append(rect(bx - 50, by - 35, 100, 70, fill=GREYBG, stroke=INK, sw=1.8))
    P.append(text(bx, by, "машина", size=11, color=INK, bold=True))
    for i, deg in enumerate((-130, 180, 130)):
        a = math.radians(deg)
        ux, uy = bx + 130 * math.cos(a), by + 70 * math.sin(a)
        P.append(circle(ux, uy, 18, fill=GRNBG, stroke=FIELD, sw=1.6))
        P.append(text(ux, uy + 4, "☺", size=13, color=FIELD, bold=True))
        P.append(line(bx + 52 * math.cos(a), by + 38 * math.sin(a),
                      ux - 20 * math.cos(a), uy - 20 * math.sin(a),
                      color=FIELD, sw=1.4, dash="3 2"))
    P.append(text(bx, by + 60, "кожному здається, що машина лише його", size=11,
                  color=FIELD, bold=True))

    P.append(line(W / 2, 60, W / 2, 290, color="#d0d5dd", sw=1.2, dash="5 4"))
    fr, w, h = textbox(W / 2, 360,
                       "перемикатися між справами так швидко, що виникає ілюзія "
                       "одночасності — це й назвали поділом часу",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/the-question.svg", W, H, *P)


# ── insert 2. Завантаження процесора: три епохи ──────────────────────────────
# Ідея: три смуги часу — простій (сірий) поступово зникає від пакету до поділу.
def fig_utilization():
    W, H = 960, 400
    P = [text(W / 2, 30, "Завантаження процесора: пакетно → мультипрограмування → поділ часу",
              size=16, bold=True)]

    rows = [
        ("ПАКЕТНО", [("A", FIELD, 120), ("простій", None, 90), ("B", NEG, 120),
                     ("простій", None, 90), ("C", AMBER, 110)]),
        ("МУЛЬТИПРОГ.", [("A", FIELD, 120), ("B", NEG, 90), ("A", FIELD, 120),
                         ("C", AMBER, 90), ("B", NEG, 110)]),
        ("ПОДІЛ ЧАСУ", None),
    ]
    x0, bar_h, gap = 200, 44, 70
    P.append(text(x0 + 270, 70, "← час →", size=11, color=MUTED))
    for i, (name, segs) in enumerate(rows):
        y = 95 + i * gap
        P.append(text(x0 - 20, y + bar_h / 2 + 4, name, size=12, color=INK,
                      bold=True, anchor="end"))
        if segs is None:
            # поділ часу — дрібнесенькі кванти
            x = x0
            cols = [FIELD, NEG, AMBER]
            for k in range(27):
                P.append(rect(x, y, 18, bar_h, fill=BG, stroke=cols[k % 3], sw=1.1))
                x += 19
            P.append(text(x + 10, y + bar_h / 2 + 4, "дрібні кванти між усіма",
                          size=10.5, color=MUTED, anchor="start"))
        else:
            x = x0
            for label, col, w in segs:
                if col is None:
                    P.append(rect(x, y, w, bar_h, fill="#dfe3e8", stroke=MUTED,
                                  sw=1.0))
                    P.append(text(x + w / 2, y + bar_h / 2 + 4, label, size=10,
                                  color=MUTED))
                else:
                    P.append(rect(x, y, w, bar_h, fill=BG, stroke=col, sw=1.4))
                    P.append(text(x + w / 2, y + bar_h / 2 + 4, label, size=11,
                                  color=col, bold=True))
                x += w + 4

    fr, w, h = textbox(W / 2, 350,
                       "сірі дірки простою заповнюються роботою; поділ часу ріже час "
                       "так тонко, що кожен — наче з машиною наодинці",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/utilization.svg", W, H, *P)


# ── insert 3. Стрічка часу: від ідей 1959-го до Unix ─────────────────────────
# Ідея: горизонтальна вісь років з віхами; дві незалежні ідеї 1959-го.
def fig_timeline():
    W, H = 980, 380
    P = [text(W / 2, 30, "Від ідей 1959-го до Unix", size=17, bold=True)]

    ax_y = 210
    P.append(arrow(70, ax_y, 910, ax_y, color=INK, sw=1.8))
    P.append(text(910, ax_y + 24, "роки →", size=12, color=INK, bold=True))

    marks = [
        (130, "1959", "Маккарті (США)\nта Стрейчі (Британія)\n— ідеї незалежно", NEG, "up"),
        (380, "1961", "CTSS (MIT, Корбато)\nперша жива система", FIELD, "down"),
        (600, "1965", "Multics\nвелика ОС", AMBER, "up"),
        (820, "1969", "Unix\n(Томпсон, Рітчі)", POS, "down"),
    ]
    for x, year, label, col, side in marks:
        P.append(circle(x, ax_y, 7, fill=col, stroke=col, sw=0))
        if side == "up":
            P.append(line(x, ax_y, x, ax_y - 30, color=col, sw=1.3))
            fr, w, h = textbox(x, ax_y - 70, label, size=10.5, bold=True, color=col,
                               fill=BG, stroke=col)
            P.append(fr)
            P.append(text(x, ax_y + 24, year, size=12, color=INK, bold=True))
        else:
            P.append(line(x, ax_y, x, ax_y + 30, color=col, sw=1.3))
            fr, w, h = textbox(x, ax_y + 70, label, size=10.5, bold=True, color=col,
                               fill=BG, stroke=col)
            P.append(fr)
            P.append(text(x, ax_y - 18, year, size=12, color=INK, bold=True))

    fr, w, h = textbox(W / 2, 350,
                       "жоден не «вкрав» в іншого — ідея визріла одразу в багатьох головах",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/timeline.svg", W, H, *P)


# ── insert 4. Механізм ілюзії ────────────────────────────────────────────────
# Ідея: кванти A,B,C на осі; на межах — перемикання контексту, тік від таймера.
def fig_mechanism():
    W, H = 980, 400
    P = [text(W / 2, 30, "Механізм ілюзії: планувальник, квант, перемикання контексту",
              size=16.5, bold=True)]

    ax_y = 170
    P.append(arrow(70, ax_y, 910, ax_y, color=INK, sw=1.8))
    P.append(text(910, ax_y + 24, "час →", size=12, color=INK, bold=True))

    seq = [("A", FIELD, GRNBG), ("B", NEG, BLUEBG), ("C", AMBER, AMBERBG),
           ("A", FIELD, GRNBG), ("B", NEG, BLUEBG)]
    x, qw = 90, 150
    edges = []
    for label, col, fill in seq:
        P.append(rect(x, ax_y - 34, qw, 34, fill=fill, stroke=col, sw=1.5))
        P.append(text(x + qw / 2, ax_y - 13, label, size=13, color=col, bold=True))
        edges.append(x)
        x += qw + 12
    edges.append(x - 12)

    # «тіки» таймера на межах + підпис перемикання
    for ex in edges[1:-1]:
        tx = ex - 6
        P.append(line(tx, ax_y - 48, tx, ax_y + 14, color=POS, sw=1.6, dash="3 2"))
        P.append(text(tx, ax_y - 54, "↯", size=13, color=POS, bold=True))
    P.append(text(edges[1] - 6, ax_y + 34, "перемикання\nконтексту", size=10,
                  color=POS, bold=True))

    fr, w, h = textbox(260, 300,
                       "тік дає ТАЙМЕР; переривання спиняє задачу —\nце й зветься витісненням",
                       size=11.5, bold=True, color=POS, fill=REDBG, stroke=POS)
    P.append(fr)
    fr, w, h = textbox(700, 300,
                       "на кожній межі: зберегти стан старої,\nспитати планувальник, "
                       "відновити нову",
                       size=11.5, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/mechanism.svg", W, H, *P)


# ── insert 5. Спадок: від залу CTSS до RTOS на чипі ──────────────────────────
# Ідея: ліворуч машинний зал з терміналами, праворуч чип; та сама ідея, новий масштаб.
def fig_legacy():
    W, H = 960, 420
    P = [text(W / 2, 30, "Та сама ідея, новий масштаб: від залу CTSS до RTOS на чипі",
              size=16, bold=True)]

    # ЛІВОРУЧ — машинний зал
    P.append(fitbox(60, 75, 380, 32, "1961 — машинний зал (CTSS)", size=12.5,
                    bold=True, color=NEG, fill=BLUEBG, stroke=NEG))
    P.append(rect(180, 150, 130, 80, fill=GREYBG, stroke=INK, sw=1.8))
    P.append(text(245, 195, "мейнфрейм", size=11, color=INK, bold=True))
    for i in range(3):
        P.append(rect(70 + i * 50, 270, 38, 30, fill=BG, stroke=MUTED, sw=1.4))
        P.append(line(89 + i * 50, 250, 89 + i * 50, 270, color=MUTED, sw=1.2))
    P.append(text(140, 320, "термінали (люди)", size=10.5, color=MUTED))

    # стрілка-перехід
    P.append(arrow(450, 230, 530, 230, color=AMBER, sw=2.4))
    P.append(text(490, 212, "зменшилась", size=10.5, color=AMBER, bold=True))

    # ПРАВОРУЧ — чип
    P.append(fitbox(540, 75, 380, 32, "сьогодні — RTOS на чипі ESP32", size=12.5,
                    bold=True, color=FIELD, fill=GRNBG, stroke=FIELD))
    P.append(rect(690, 160, 110, 70, fill="#1f2937", stroke=INK, sw=1.8, rx=8))
    P.append(text(745, 200, "ESP32", size=12, color="#ffffff", bold=True))
    for sx in (690, 800):
        for k in range(4):
            P.append(line(sx, 168 + k * 16, sx + (-14 if sx == 690 else 14),
                          168 + k * 16, color=MUTED, sw=1.4))
    for i in range(3):
        P.append(rect(640 + i * 55, 270, 44, 28, fill=GRNBG, stroke=FIELD, sw=1.4))
        P.append(text(662 + i * 55, 288, "задача", size=9, color=FIELD, bold=True))
    P.append(text(745, 320, "задачі (код)", size=10.5, color=MUTED))

    P.append(line(W / 2, 65, W / 2, 330, color="#d0d5dd", sw=1.2, dash="5 4"))
    fr, w, h = textbox(W / 2, 375,
                       "той самий планувальник і перемикання контексту; нове головне — "
                       "РЕАЛЬНИЙ ЧАС: не лише справедливо, а й вчасно",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/legacy.svg", W, H, *P)


if __name__ == "__main__":
    # стаття
    fig_setup_loop()
    fig_under_hood()
    fig_read_compute_act()
    fig_foreground_background()
    fig_loop_timing()
    fig_several_jobs()
    # вставка «поділ часу»
    fig_the_question()
    fig_utilization()
    fig_timeline()
    fig_mechanism()
    fig_legacy()
    print("OK: 11 figures -> img/")
