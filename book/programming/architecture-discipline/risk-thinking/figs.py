# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')

GRN_L = "#eafaf0"; BLU_L = "#eaf0fd"; RED_L = "#fdecea"
AMB = "#b8860b"; AMB_L = "#fff8e1"


def polyline(points, color=INK, sw=2.0, dash=None):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline fill="none" points="%s" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, color, sw, d))
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: експозиція = ймовірність × втрата (три панелі-площі) ──────────
def fig_exposure():
    W, H = 940, 470
    els = []
    els.append(text(W / 2, 30, "Експозиція = ймовірність × втрата: важить ПЛОЩА, не висота й не ширина", size=16, bold=True))

    # три окремі панелі-квадранти; у кожній прямокутник ризику від спільного кута
    panels = [
        (60,  "A: ймовірна\nдрібниця",   0.85, 0.20, NEG,   "#eaf0fd", "0.85 × 0.2"),
        (350, "B: рідкісна\nкатастрофа", 0.15, 0.95, POS,   "#fdecea", "0.15 × 0.95"),
        (640, "C: середній\nризик",       0.50, 0.55, FIELD, "#eafaf0", "0.5 × 0.55"),
    ]
    px = 210          # сторона квадранта в пікселях
    base_y = 360      # низ квадранта (вісь втрати=0 / ймовірності=0)

    for x0, label, p, loss, color, fillc, formula in panels:
        # рамка-квадрант
        els.append(rect(x0, base_y - px, px, px, fill=BG, stroke="#d0d0d0", sw=1, rx=2))
        # осі всередині
        els.append(line(x0, base_y, x0 + px, base_y, color=MUTED, sw=1))   # X втрата
        els.append(line(x0, base_y, x0, base_y - px, color=MUTED, sw=1))   # Y ймовірність
        # прямокутник експозиції (від лівого-нижнього кута)
        w = loss * px
        h = p * px
        els.append(rect(x0, base_y - h, w, h, fill=fillc, stroke=color, sw=2, rx=2))
        # підпис ризику — НАД квадрантом, у власній рамці
        b, bw, bh = textbox(x0 + px / 2, base_y - px - 34, label, size=13, bold=True,
                            min_w=170, fill=BG, stroke=color, color=color)
        els.append(b)
        # формула площі — під квадрантом
        els.append(text(x0 + px / 2, base_y + 24, "площа = " + formula, size=12, color=INK, bold=True))

    # осьові підписи (лише під першою панеллю, щоб не дублювати)
    els.append(text(60 + px / 2, base_y + 44, "ширина = втрата · висота = ймовірність", size=11, color=MUTED, italic=True))

    els.append(text(W / 2, H - 20, "площа A ≈ площа B: часта дрібниця й рідкісна катастрофа важать майже порівну — рангує лише добуток",
                    size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'exposure.svg'), W, H, *els)


# ── Фігура 2: чотири клітини знання про ризик ───────────────────────────────
def fig_known_unknowns():
    W, H = 900, 540
    els = []
    els.append(text(W / 2, 30, "Що ми знаємо про власне незнання: чотири клітини", size=16, bold=True))

    # сітка 2×2
    gx, gy = 190, 90               # лівий-верхній кут поля клітин
    cw, ch = 300, 175             # розмір клітини
    gap = 16

    # осьові підписи (поза сіткою)
    els.append(text(gx + cw / 2, gy - 28, "усвідомлюємо", size=13, bold=True, color=MUTED))
    els.append(text(gx + cw + gap + cw / 2, gy - 28, "НЕ усвідомлюємо", size=13, bold=True, color=MUTED))
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">знаємо</text>'
               % (gx - 32, gy + ch / 2, FONT, MUTED, gx - 32, gy + ch / 2))
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">НЕ знаємо</text>'
               % (gx - 32, gy + ch + gap + ch / 2, FONT, MUTED, gx - 32, gy + ch + gap + ch / 2))

    cells = [
        (0, 0, "Відоме відоме", "факти, на які спираємось.\nПросто робимо.", "#eafaf0", FIELD),
        (1, 0, "Відоме невідоме", "названий ризик.\nЙого В РЕЄСТР —\nмоніторити й гасити.", "#eaf0fd", NEG),
        (0, 1, "Невідоме відоме", "мовчазне знання команди,\nне вимовлене вголос.\nВитягти рев'ю.", "#fff8e1", "#b8860b"),
        (1, 1, "Невідоме невідоме", "чого й уявити не можемо.\nПроти нього — лише\nзапас і зворотність.", "#fdecea", POS),
    ]
    for col, row, title, body, fillc, strokec in cells:
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        els.append(rect(x, y, cw, ch, fill=fillc, stroke=strokec, sw=2, rx=8))
        els.append(text(x + cw / 2, y + 32, title, size=15, bold=True, color=strokec))
        els.append(mtext(x + cw / 2, y + 66, body, size=12.5, color=INK, lh=1.32))

    els.append(text(W / 2, H - 20, "інженерна пара «known/unknown unknowns» — з аерокосмічної практики кінця 1960-х (unk-unks)",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'known-unknowns.svg'), W, H, *els)


# ── Фігура 3: чотири відповіді на ризик, розкладені за експозицією ──────────
def fig_responses():
    W, H = 940, 470
    els = []
    els.append(text(W / 2, 30, "Один ризик — чотири відповіді; яку обрати, диктує експозиція", size=16, bold=True))

    # центр: сам ризик
    cx = W / 2
    br, wr, hr = textbox(cx, 96, "РИЗИК\n(ймовірність × втрата)", size=14, bold=True,
                         min_w=250, fill="#f7f7f7", stroke=INK)
    els.append(br)

    # чотири гілки вниз, у власні рамки з великим кроком
    row_y = 250
    cells = [
        (150, "Уникнути", "прибрати причину:\nінший шлях, де ризику нема", "#eafaf0", FIELD),
        (383, "Зменшити", "збити ймовірність або втрату:\nтест, шов, надлишок", "#eaf0fd", NEG),
        (616, "Передати", "віддати тому, хто впорається:\nстрахування, SLA, хмара", "#fff8e1", "#b8860b"),
        (849, "Прийняти", "лишити свідомо + запас;\nдешевше, ніж боротися", "#fdecea", POS),
    ]
    for bx, title, body, fillc, strokec in cells:
        b, bw, bh = textbox(bx, row_y, title, size=14, bold=True, min_w=170,
                            fill=fillc, stroke=strokec, color=strokec)
        els.append(b)
        els.append(mtext(bx, row_y + 58, body, size=12, color=INK, lh=1.3))
        els.append(arrow(cx, 96 + hr / 2, bx, row_y - bh / 2))

    els.append(text(W / 2, H - 44, "мала експозиція → прийняти й записати; велика → уникнути чи зменшити, поки дешево;",
                    size=12, color=INK))
    els.append(text(W / 2, H - 22, "не своя компетенція → передати. «Нічого не робити» — теж вибір, лише коли він свідомий",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'responses.svg'), W, H, *els)


# ── Фігура 4: два варіанти як стоси ризиків, порівняння сумарної експозиції ──
def fig_exposure_decision():
    W, H = 940, 620
    els = []
    els.append(text(W / 2, 30, "Сумарна експозиція = стос ризиків-прямокутників; порівнюємо два шляхи", size=16, bold=True))

    # вісь-масштаб: 1 одиниця експозиції = SCALE пікселів висоти
    base_y = 540          # низ стосів (експозиція = 0)
    scale = 16.0          # px на одиницю експозиції (макс стос ~25 → ~400 px)
    col_w = 190           # ширина колонки-стосу

    # сегменти кожного варіанта: (підпис, експозиція, колір-заливка, колір-обведення)
    mono = [
        ("вузьке місце\n0.5×20 = 10.0", 10.0, "#fdecea", POS),
        ("точка відмови\n0.2×15 = 3.0",  3.0, "#eaf0fd", NEG),
        ("міграції\n0.3×8 = 2.4",        2.4, "#eafaf0", FIELD),
        ("звіти\n0.4×5 = 2.0",           2.0, "#fff8e1", "#b8860b"),
    ]
    cache = [
        ("неузгодженість\n0.6×12 = 7.2", 7.2, "#fdecea", POS),
        ("інвалідація\n0.5×10 = 5.0",    5.0, "#fdecea", POS),
        ("крива навчання\n0.6×8 = 4.8",  4.8, "#fff8e1", "#b8860b"),
        ("вузьке місце\n0.15×20 = 3.0",  3.0, "#eaf0fd", NEG),
        ("розгортання\n0.5×5 = 2.5",     2.5, "#eafaf0", FIELD),
        ("вузол кешу\n0.4×6 = 2.4",      2.4, "#eafaf0", FIELD),
    ]

    def draw_stack(cx, title, segs):
        total = sum(e for _, e, _, _ in segs)
        x0 = cx - col_w / 2
        y = base_y
        for label, e, fillc, strokec in segs:
            h = e * scale
            y -= h
            els.append(rect(x0, y, col_w, h, fill=fillc, stroke=strokec, sw=1.5, rx=2))
            # підпис у власну рамку — праворуч від сегмента, щоб не лягав на лінії
            b, bw, bh = textbox(cx, y + h / 2, label, size=10.5, min_w=col_w - 16,
                                fill=BG, stroke=strokec, color=INK, pad=5)
            els.append(b)
        # підсумкова висота стосу — вісь зверху
        top = base_y - total * scale
        els.append(line(x0 - 12, top, x0 + col_w + 12, top, color=INK, sw=2, dash="5 4"))
        b2, _, _ = textbox(cx, top - 24, "Σ = %.1f" % total, size=15, bold=True,
                           min_w=120, fill=BG, stroke=INK, color=INK)
        els.append(b2)
        # назва варіанта під колонкою
        els.append(text(cx, base_y + 26, title, size=15, bold=True))

    draw_stack(255, "Варіант M — моноліт", mono)
    draw_stack(690, "Варіант P — кеш",    cache)

    # спільна вісь-підпис ліворуч
    els.append('<text x="40" y="%.1f" font-family="%s" font-size="12" fill="%s" '
               'text-anchor="middle" font-style="italic" transform="rotate(-90 40 %.1f)">'
               'експозиція, людино-дні (вище = гірше)</text>'
               % (base_y - 180, FONT, MUTED, base_y - 180))

    els.append(text(W / 2, H - 22, "кеш збиває головну скелю моноліта (тонкий сегмент вузького місця), "
                    "та власні ризики переважують — за грубими числами моноліт легший",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'exposure-decision.svg'), W, H, *els)


# ── Фігура 5 (детальна): три режими незнання й зброя кожного ─────────────────
def fig_regimes():
    W, H = 1000, 430
    els = [text(W / 2, 30, "Три режими незнання — і зброя кожного", size=17, bold=True)]

    pw, ph, ytop = 290, 250, 70
    xs = [45, 360, 675]
    panels = [
        (GRN_L, FIELD, "Ризик", "розподіл ВІДОМИЙ\n(шанси знаємо)",
         "bars_solid", "Зброя: арифметика —\nекспозиція p × L, важіль"),
        (AMB_L, AMB, "Невизначеність", "розподіл Є, але\nНЕВІДОМИЙ",
         "bars_dash", "Зброя: сценарії, запас,\nсудження, рання перевірка"),
        (RED_L, POS, "Невідоме невідоме", "події годі\nй НАЗВАТИ",
         "qmark", "Зброя: зворотність,\nнадлишок, ізоляція вибуху"),
    ]
    for x0, (fillc, strokec, title, subt, glyph, weapon) in zip(xs, panels):
        cx = x0 + pw / 2
        els.append(rect(x0, ytop, pw, ph, fill=fillc, stroke=strokec, sw=2, rx=10))
        els.append(text(cx, ytop + 34, title, size=16, bold=True, color=strokec))
        els.append(mtext(cx, ytop + 62, subt, size=12, color=INK, lh=1.3))
        # гліф-мітка розподілу
        if glyph in ("bars_solid", "bars_dash"):
            heights = [30, 52, 40, 58, 34]
            bw, gap = 16, 7
            total = len(heights) * bw + (len(heights) - 1) * gap
            bx = cx - total / 2
            gbase = ytop + 178
            for hh in heights:
                if glyph == "bars_solid":
                    els.append(rect(bx, gbase - hh, bw, hh, fill=FIELD, stroke=FIELD, sw=1, rx=1))
                else:
                    els.append(rect(bx, gbase - hh, bw, hh, fill=BG, stroke=AMB, sw=1.4, rx=1))
                bx += bw + gap
        else:
            els.append(text(cx, ytop + 168, "?", size=52, bold=True, color=POS))
        els.append(fitbox(x0 + 22, ytop + 195, pw - 44, 44, weapon, size=12,
                          fill=BG, stroke=strokec, color=INK))

    # спектр-стрілка під панелями
    els.append(arrow(70, 352, 950, 352, color=MUTED, sw=2))
    els.append(text(W / 2, 376, "що менше знаємо про ймовірності — тим слабший розрахунок і тим важливіша структура",
                    size=12.5, color=MUTED))
    els.append(text(W / 2, 410, "Помилка режиму — рахувати там, де рахувати нема чого — одна з найдорожчих",
                    size=12.5, color=INK, italic=True))
    render(os.path.join(OUT, 'regimes.svg'), W, H, *els)


# ── Фігура 6 (детальна): увігнута корисність → премія за ризик ───────────────
def fig_risk_premium():
    W, H = 900, 560
    X0, X1, Y0, Y1 = 110, 690, 470, 95
    els = [text(W / 2, 30, "Увігнута корисність породжує премію за ризик (ставка 50/50: 4 або 100)",
                size=16, bold=True)]

    def mx(w): return X0 + (w / 110.0) * (X1 - X0)
    def my(u): return Y0 - (u / 110.0) * (Y0 - Y1)

    # осі
    els.append(line(X0, Y1, X0, Y0, color=INK, sw=1.6))
    els.append(line(X0, Y0, X1 + 10, Y0, color=INK, sw=1.6))
    els.append('<text x="70" y="%.1f" font-family="%s" font-size="12" fill="%s" '
               'text-anchor="middle" transform="rotate(-90 70 %.1f)">корисність U</text>'
               % ((Y0 + Y1) / 2, FONT, MUTED, (Y0 + Y1) / 2))
    els.append(text(620, Y0 + 34, "багатство / вислід →", size=12, color=MUTED))

    # крива U=10√w
    curve = [(mx(w), my(10 * math.sqrt(w))) for w in [i * 0.5 for i in range(2, 221)]]
    els.append(polyline(curve, color=INK, sw=2.4))
    els.append(text(575, 120, "U(w) = √w", size=13, color=INK, italic=True))

    x1, y1 = mx(4), my(20)      # w1
    x2, y2 = mx(100), my(100)   # w2
    xe, yeu = mx(52), my(60)    # E[w], E[U] (на хорді)
    yc = my(72.11)              # U(E[w]) на кривій
    xce = mx(36)                # CE
    # хорда
    els.append(line(x1, y1, x2, y2, color=NEG, sw=1.8))
    # напрямні
    els.append(line(xe, Y0, xe, yc, color=MUTED, sw=1.2, dash="5 4"))
    els.append(line(xce, Y0, xce, yeu, color=MUTED, sw=1.2, dash="5 4"))
    els.append(line(xce, yeu, xe, yeu, color=MUTED, sw=1.2, dash="5 4"))
    # точки
    for (px, py, col) in [(x1, y1, POS), (x2, y2, FIELD), (xe, yeu, NEG), (xce, yeu, AMB), (xe, yc, INK)]:
        els.append(circle(px, py, 4.5, fill=col, stroke=BG, sw=1.4))
    # короткі теги
    els.append(text(x1 + 16, y1 + 6, "w₁", size=13, bold=True, color=POS, anchor="start"))
    els.append(text(x2 + 14, y2 - 2, "w₂", size=13, bold=True, color=FIELD, anchor="start"))
    els.append(text(xe + 15, yeu + 16, "E[U]", size=12, bold=True, color=NEG, anchor="start"))
    els.append(text(xe, yc - 20, "U(E[w])", size=12, bold=True, color=INK))
    els.append(text(xe, Y0 + 20, "E[w]", size=12, bold=True, color=INK))
    els.append(text(xce, Y0 + 20, "CE", size=12, bold=True, color=AMB))
    # дужка премії за ризик під віссю
    els.append(line(xce, Y0 + 32, xe, Y0 + 32, color=POS, sw=2))
    els.append(line(xce, Y0 + 28, xce, Y0 + 36, color=POS, sw=2))
    els.append(line(xe, Y0 + 28, xe, Y0 + 36, color=POS, sw=2))
    els.append(text((xce + xe) / 2, Y0 + 54, "премія за ризик = 16", size=12.5, bold=True, color=POS))

    # легенда праворуч
    els.append(fitbox(715, 150, 172, 132,
                      "E[w]: сподіване багатство\nE[U]: сподівана корисність\nCE: певний еквівалент\nE[w] − CE: премія",
                      size=11, fill=BG, stroke=MUTED, color=INK))
    els.append(text(W / 2, H - 22, "певний еквівалент нижчий за сподіване багатство — цей проміжок і оплачують, передаючи ризик",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'risk-premium.svg'), W, H, *els)


# ── Фігура 7 (детальна): важіль зменшення ризику RRL ────────────────────────
def fig_leverage():
    W, H = 900, 480
    base_y, scale = 380, 24.0
    els = [text(W / 2, 30, "Важіль зменшення ризику: рангуй тактики за окупністю, не за страхом",
                size=16, bold=True)]

    groups = [
        (250, "Тактика A — повтори + таймаут", 12, 4, 2, "RRL = 8 / 2 = 4.0  ✓", FIELD, GRN_L),
        (650, "Тактика B — переписати звіти на іншу СУБД", 10, 3, 9, "RRL = 7 / 9 ≈ 0.78  ✗", POS, RED_L),
    ]
    for cx, title, re_b, re_a, cost, rrl, hcol, hfill in groups:
        ex_l, ex_w = cx - 70, 55
        cost_l = cx + 15
        top_b = base_y - re_b * scale
        top_a = base_y - re_a * scale
        top_c = base_y - cost * scale
        # смуга «куплене зниження»
        els.append(rect(ex_l, top_b, ex_w, top_a - top_b, fill=GRN_L, stroke=FIELD, sw=1.2, rx=2))
        # «після» (лишкова експозиція)
        els.append(rect(ex_l, top_a, ex_w, base_y - top_a, fill=BLU_L, stroke=NEG, sw=1.5, rx=2))
        # контур «до»
        els.append(rect(ex_l, top_b, ex_w, base_y - top_b, fill="none", stroke=INK, sw=1.6, rx=2))
        # стовпець вартості
        els.append(rect(cost_l, top_c, ex_w, base_y - top_c, fill=AMB_L, stroke=AMB, sw=1.5, rx=2))
        # числові мітки в білих рамках
        b, _, _ = textbox(ex_l - 34, top_b, "до %d" % re_b, size=11, fill=BG, stroke=INK, color=INK, pad=5)
        els.append(b)
        b, _, _ = textbox(ex_l - 34, top_a, "після %d" % re_a, size=11, fill=BG, stroke=NEG, color=NEG, pad=5)
        els.append(b)
        b, _, _ = textbox(cx - 42, (top_a + top_b) / 2, "−%d" % (re_b - re_a), size=12,
                          fill=BG, stroke=FIELD, color=FIELD, bold=True, pad=5)
        els.append(b)
        cy = top_c - 16 if cost < 4 else (top_c + base_y) / 2
        b, _, _ = textbox(cost_l + ex_w / 2, cy, "варт. %d" % cost, size=11, fill=BG, stroke=AMB, color=AMB, pad=5)
        els.append(b)
        # заголовок RRL
        b, _, _ = textbox(cx, 58, rrl, size=15, bold=True, min_w=210, fill=hfill, stroke=hcol, color=hcol)
        els.append(b)
        els.append(text(cx, base_y + 26, title, size=12.5, bold=True))

    els.append(text(W / 2, H - 20, "однаково страшні на око — та A гасить дешево (важіль 4.0), B збиткова (0.78 < 1): дешевше прийняти",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'leverage.svg'), W, H, *els)


# ── Фігура 8 (детальна): крива вартості зміни й зворотність ──────────────────
def fig_cost_curve():
    W, H = 900, 470
    X0, X1, Y0, Y1 = 95, 830, 400, 80
    els = [text(W / 2, 30, "Вартість зміни рішення росте з часом — але наскільки круто, вирішує зворотність",
                size=15.5, bold=True)]

    def mx(t): return X0 + t * (X1 - X0)
    def my(c): return Y0 - (c / 260.0) * (Y0 - Y1)

    els.append(line(X0, Y1, X0, Y0, color=INK, sw=1.6))
    els.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))
    els.append('<text x="52" y="%.1f" font-family="%s" font-size="12" fill="%s" '
               'text-anchor="middle" transform="rotate(-90 52 %.1f)">вартість зміни / відкоту</text>'
               % ((Y0 + Y1) / 2, FONT, MUTED, (Y0 + Y1) / 2))

    ts = [i * 0.02 for i in range(0, 51)]
    steep = [(mx(t), my(8 * math.exp(3.4 * t))) for t in ts]
    gentle = [(mx(t), my(8 + 82 * (t ** 1.3))) for t in ts]
    # рання зона — дешево
    els.append(rect(X0, Y1, mx(0.18) - X0, Y0 - Y1, fill=GRN_L, stroke="none", sw=0))
    els.append(polyline(steep, color=POS, sw=2.6))
    els.append(polyline(gentle, color=FIELD, sw=2.6))

    # фазові позначки
    for t, lab in [(0, "початок"), (0.25, "дизайн"), (0.5, "код"), (0.75, "тест"), (1.0, "прод")]:
        els.append(line(mx(t), Y0, mx(t), Y0 + 5, color=INK, sw=1.2))
        els.append(text(mx(t), Y0 + 20, lab, size=11, color=MUTED))

    els.append(text(690, 138, "незворотне:", size=12.5, bold=True, color=POS))
    els.append(text(690, 156, "крива Бема (вибух)", size=12, color=POS))
    els.append(text(560, 366, "зворотне: криву сплощено", size=12.5, bold=True, color=FIELD))

    # стрілка в ранню зону
    els.append(arrow(250, 184, 180, 352, color=INK, sw=1.8))
    els.append(mtext(285, 150, "атакуй найризикованіше\nтут, поки дешево", size=12, color=INK, lh=1.3, bold=True))

    els.append(text(W / 2, H - 18, "крутість кривої — не фатум, а вибір: зворотність (шви, тести, модулі) згинає її донизу",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'cost-curve.svg'), W, H, *els)


# ── Фігура 9 (детальна): нормалізація відхилення ────────────────────────────
def fig_deviance():
    W, H = 900, 430
    X0, X1, Y0, Y1 = 90, 830, 360, 80
    els = [text(W / 2, 30, "Нормалізація відхилення: поріг «прийнятного» повзе за фактичною небезпекою",
                size=15.5, bold=True)]

    def mx(i): return X0 + (i / 7.0) * (X1 - X0)
    def my(v): return Y0 - (v / 10.0) * (Y0 - Y1)

    els.append(line(X0, Y1, X0, Y0, color=INK, sw=1.6))
    els.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))

    actual = [2.0, 2.6, 3.0, 3.6, 3.9, 4.5, 5.0, 8.4]
    thresh = [3.0, 3.0, 3.5, 4.0, 4.2, 4.8, 5.3, 5.3]
    ap = [(mx(i), my(v)) for i, v in enumerate(actual)]
    # поріг як сходинки
    tp = []
    for i, v in enumerate(thresh):
        if i > 0:
            tp.append((mx(i), my(thresh[i - 1])))
        tp.append((mx(i), my(v)))
    els.append(polyline(tp, color=AMB, sw=2.2, dash="7 4"))
    els.append(polyline(ap[:7], color=POS, sw=2.4))
    els.append(line(ap[6][0], ap[6][1], ap[7][0], ap[7][1], color=POS, sw=2.4, dash="3 3"))
    for (px, py) in ap[:7]:
        els.append(circle(px, py, 4, fill=POS, stroke=BG, sw=1.2))
    # катастрофа
    els.append(circle(ap[7][0], ap[7][1], 8, fill=POS, stroke=INK, sw=1.5))
    els.append(text(ap[7][0] - 8, ap[7][1] - 16, "катастрофа", size=12.5, bold=True, color=POS, anchor="end"))

    els.append(text(255, 205, "поріг «прийнятного»", size=12.5, bold=True, color=AMB))
    els.append(text(300, 320, "фактичне відхилення", size=12.5, bold=True, color=POS))
    els.append(text(560, 150, "кожне «пронесло» → поріг угору", size=12, color=MUTED, italic=True))

    for i in range(8):
        els.append(text(mx(i), Y0 + 20, str(i + 1), size=11, color=MUTED))
    els.append(text(W / 2, Y0 + 40, "запуски / релізи (час →)", size=11.5, color=MUTED))
    els.append(text(W / 2, H - 16, "кожне «пронесло» знижує ВІДЧУТУ ймовірність, не чіпаючи СПРАВЖНЬОЇ — доки вони не розійдуться в біду",
                    size=12, color=INK, italic=True))
    render(os.path.join(OUT, 'deviance.svg'), W, H, *els)


# ── Фігура: родовід теорії рішень (часова вісь віх) ─────────────────────────
def fig_timeline():
    W, H = 1180, 520
    els = [text(W / 2, 34, "Родовід теорії рішень: від гри-парадокса до керування ризиком у софті",
                size=16, bold=True)]
    axis_y = 268
    x0, x1 = 100, 1080
    els.append(line(x0 - 24, axis_y, x1 + 46, axis_y, color=INK, sw=2.2))
    els.append(text(x1 + 52, axis_y + 5, "час →", size=12.5, color=MUTED, anchor="start"))

    pts = [
        ("1713", "Н. Бернуллі",         "гра з ∞ середнім",       NEG,   True),
        ("1738", "Д. Бернуллі",         "корисність, логарифм",   NEG,   False),
        ("1921", "Ф. Найт",             "ризик ≠ невизначеність", FIELD, True),
        ("1944–47", "фон Нейман,\nМорґенштерн", "аксіоми корисності", INK, False),
        ("1953", "М. Алле",             "парадокс аксіом",        POS,   True),
        ("1954", "Л. Севідж",           "суб'єктивна ймовірність", POS,  False),
        ("1991", "Б. Бем",              "експозиція = P × втрата", AMB,  True),
        ("2003", "Демарко, Лістер",     "ризик — першим",         AMB,   False),
    ]
    n = len(pts)
    for i, (yr, name, phrase, col, above) in enumerate(pts):
        x = x0 + i * (x1 - x0) / (n - 1)
        els.append(circle(x, axis_y, 7, fill=col, stroke=BG, sw=2))
        if above:
            box_cy = 148
            els.append(text(x, axis_y + 26, yr, size=13, bold=True, color=col))
            els.append(line(x, axis_y - 10, x, box_cy + 40, color=col, sw=1.3, dash="4 3"))
        else:
            box_cy = 392
            els.append(text(x, axis_y - 15, yr, size=13, bold=True, color=col))
            els.append(line(x, axis_y + 10, x, box_cy - 40, color=col, sw=1.3, dash="4 3"))
        b, bw, bh = textbox(x, box_cy, name + "\n" + phrase, size=12.5,
                            min_w=150, fill=BG, stroke=col, color=INK)
        els.append(b)

    els.append(text(W / 2, H - 16,
                    "ідея (1738) → поняття (1921) → аксіоматизація (1944–47) → виклики (1953–54) → інженерна практика (1991–2003)",
                    size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, 'timeline.svg'), W, H, *els)


# ── Фігура: спадна гранична корисність (увігнута крива log) ──────────────────
def fig_utility():
    W, H = 800, 500
    els = [text(W / 2, 32, "Спадна гранична корисність: чому нескінченний виграш вартий скінченно мало",
                size=15, bold=True)]
    ox, oy = 96, 412        # початок координат (лівий-нижній кут)
    pw, ph = 628, 322
    wmax = 34.0
    umax = math.log(wmax)

    def X(w):
        return ox + (w / wmax) * pw

    def Y(u):
        return oy - (u / umax) * ph

    # осі
    els.append(line(ox, oy, ox + pw + 24, oy, color=INK, sw=1.8))
    els.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=1.8))
    els.append(text(ox + pw + 28, oy + 5, "гроші →", size=12, color=MUTED, anchor="start"))
    els.append(text(ox - 6, oy - ph - 8, "корисність u(w)", size=12, color=MUTED, anchor="start"))

    # крива u = ln(w)
    curve = []
    w = 0.4
    while w <= wmax:
        curve.append((X(w), Y(math.log(w))))
        w += 0.25
    els.append(polyline(curve, color=NEG, sw=2.6))

    # подвоєння: рівні кроки корисності за геометричні кроки грошей
    for wv in [2, 4, 8, 16, 32]:
        u = math.log(wv)
        els.append(line(X(wv), oy, X(wv), Y(u), color=MUTED, sw=1.1, dash="4 3"))
        els.append(line(ox, Y(u), X(wv), Y(u), color=MUTED, sw=1.1, dash="4 3"))
        els.append(line(ox - 5, Y(u), ox + 5, Y(u), color=INK, sw=1.6))  # тик на осі Y
        els.append(circle(X(wv), Y(u), 4.2, fill=NEG, stroke=BG, sw=1.3))
        els.append(text(X(wv), oy + 20, str(wv), size=12.5, bold=True, color=INK))

    # пояснювальна рамка у порожньому верхньо-лівому куті (над кривою)
    b, bw, bh = textbox(287, 116,
                        "× 2 до грошей  →  + ln 2 до корисності\nбільші виграші важать дедалі менше",
                        size=12.5, min_w=0, fill="#eaf0fd", stroke=NEG, color=INK)
    els.append(b)

    els.append(text(ox + pw / 2 + 20, H - 14,
                    "рівні сходинки по вертикалі за подвоєння по горизонталі — гранична корисність спадає",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'utility.svg'), W, H, *els)


# ── Вставка math-decision-under-risk, фіг. 1: зазор Єнсена як лінійка ризику ─
def fig_curvature_gap():
    W, H = 1000, 470
    els = [text(W / 2, 28, "Нерівність Єнсена: зазор між f(середнього) і середнім f — це і є ризик",
                size=15.5, bold=True)]
    xs = [40, 370, 700]
    pw, ph, ytop = 290, 250, 72
    x1n, x2n = 0.06, 0.94

    def f_lin(t): return t
    def f_sqrt(t): return math.sqrt(t)
    def f_log(t): return math.log(1 + 9 * t) / math.log(10)

    panels = [
        (f_lin, "лінійна f",
         "Пряма: втрата додається.\nЗазор нульовий — середнє\nкаже всю правду; кореляція\nчіпає лише розкид, не центр."),
        (f_sqrt, "увігнута f — корисність",
         "Увігнута корисність:\nзазор = премія за ризик.\nПевний еквівалент нижчий\nза сподіване багатство."),
        (f_log, "увігнута f — логарифм",
         "Увігнутий логарифм:\nзазор = плата за коливання.\nГеометричне середнє нижче\nза арифметичне → руїна."),
    ]
    for x0, (fn, title, cap) in zip(xs, panels):
        cx = x0 + pw / 2
        L, R = x0 + 40, x0 + pw - 24
        T, B = ytop + 34, ytop + ph - 34
        els.append(rect(x0, ytop, pw, ph, fill=BG, stroke="#d7dbe0", sw=1.2, rx=8))
        els.append(text(cx, ytop + 22, title, size=13, bold=True, color=INK))

        def mx(t, L=L, R=R): return L + t * (R - L)
        def my(v, T=T, B=B): return B - v * (B - T)
        els.append(line(L, B, R, B, color=MUTED, sw=1.2))
        els.append(line(L, B, L, T, color=MUTED, sw=1.2))
        curve = [(mx(i / 60.0), my(fn(i / 60.0))) for i in range(0, 61)]
        els.append(polyline(curve, color=INK, sw=2.4))
        p1 = (mx(x1n), my(fn(x1n)))
        p2 = (mx(x2n), my(fn(x2n)))
        els.append(polyline([p1, p2], color=NEG, sw=2.0, dash="6 4"))
        els.append(circle(p1[0], p1[1], 4.5, fill=NEG, stroke=BG, sw=1.4))
        els.append(circle(p2[0], p2[1], 4.5, fill=NEG, stroke=BG, sw=1.4))
        xm = mx(0.5)
        y_curve = my(fn(0.5))
        y_chord = my((fn(x1n) + fn(x2n)) / 2.0)
        els.append(circle(xm, y_curve, 4.5, fill=FIELD, stroke=BG, sw=1.4))
        els.append(circle(xm, y_chord, 4.5, fill=POS, stroke=BG, sw=1.4))
        if abs(y_curve - y_chord) > 2:
            els.append(polyline([(xm, y_curve), (xm, y_chord)], color=POS, sw=3.0))
            els.append(polyline([(xm - 6, y_curve), (xm + 6, y_curve)], color=POS, sw=2.0))
            els.append(polyline([(xm - 6, y_chord), (xm + 6, y_chord)], color=POS, sw=2.0))
        els.append(fitbox(x0 + 6, 330, pw - 12, 104, cap, size=12, fill=BG, stroke="#d7dbe0", color=INK))

    els.append(text(W / 2, 462, "лінійна f — зазор нуль; що увігнутіша f, то ширший зазор між кривою і хордою — і то більший ризик",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'curvature-gap.svg'), W, H, *els)


# ── Вставка math-decision-under-risk, фіг. 2: ансамбль проти часу ────────────
def fig_mult_ensemble():
    W, H = 940, 470
    els = [text(W / 2, 28, "Мультиплікативна гра ×1.5 / ×0.6: ансамбль росте, а окрема стежка тоне",
                size=15.5, bold=True)]
    X0, X1, Y0, Y1 = 92, 812, 402, 74
    N = 10
    up, dn = math.log(1.5), math.log(0.6)
    lo, hi = math.log(0.22), math.log(3.0)

    def mx(t): return X0 + (t / float(N)) * (X1 - X0)
    def my(lc): return max(64.0, min(406.0, Y0 - (lc - lo) / (hi - lo) * (Y0 - Y1)))

    yb = my(0.0)
    els.append(line(X0, yb, X1, yb, color="#c8ccd4", sw=1.2, dash="5 5"))

    st = [20250710]

    def rnd():
        st[0] = (1103515245 * st[0] + 12345) & 0x7fffffff
        return st[0] / float(0x7fffffff)

    for _k in range(9):
        lc = 0.0
        pts = [(mx(0), my(0.0))]
        for t in range(1, N + 1):
            lc += up if rnd() < 0.5 else dn
            pts.append((mx(t), my(lc)))
        els.append(polyline(pts, color="#cdd2da", sw=1.4))

    geom = [(mx(t), my(t * math.log(math.sqrt(1.5 * 0.6)))) for t in range(N + 1)]
    arith = [(mx(t), my(t * math.log(1.05))) for t in range(N + 1)]
    els.append(polyline(geom, color=NEG, sw=3.2))
    els.append(polyline(arith, color=POS, sw=3.2))

    els.append(line(X0, Y1, X0, Y0, color=INK, sw=1.6))
    els.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))
    for cap, val in [("×2", math.log(2)), ("×1", 0.0), ("×0.5", math.log(0.5)), ("×0.25", math.log(0.25))]:
        yv = my(val)
        els.append(line(X0 - 5, yv, X0, yv, color=INK, sw=1.2))
        els.append(text(X0 - 12, yv + 4, cap, size=11, color=MUTED, anchor="end"))
    for t in range(0, N + 1, 2):
        els.append(line(mx(t), Y0, mx(t), Y0 + 5, color=INK, sw=1.2))
        els.append(text(mx(t), Y0 + 20, str(t), size=11, color=MUTED))
    els.append(text((X0 + X1) / 2, Y0 + 40, "крок гри (час →)", size=11.5, color=MUTED))
    els.append('<text x="46" y="%.1f" font-family="%s" font-size="11" fill="%s" '
               'text-anchor="middle" transform="rotate(-90 46 %.1f)">капітал (лог)</text>'
               % ((Y0 + Y1) / 2, FONT, MUTED, (Y0 + Y1) / 2))

    els.append(rect(150, 86, 320, 70, fill=BG, stroke="#d7dbe0", sw=1.2, rx=6))
    els.append(text(162, 108, "— ансамблеве середнє  1.05^t  (росте)", size=12, color=POS, anchor="start"))
    els.append(text(162, 130, "— часове / геометричне  0.949^t  (тоне)", size=12, color=NEG, anchor="start"))
    els.append(text(162, 152, "— окремі гравці (здебільшого тонуть)", size=12, color=MUTED, anchor="start"))

    b, _, _ = textbox(872, my(10 * math.log(1.05)), "ансамбль ×1.63", size=11,
                      fill=BG, stroke=POS, color=POS, bold=True, pad=6)
    els.append(b)
    b, _, _ = textbox(872, my(10 * math.log(math.sqrt(1.5 * 0.6))), "часове ×0.59", size=11,
                      fill=BG, stroke=NEG, color=NEG, bold=True, pad=6)
    els.append(b)

    els.append(text(W / 2, 462, "те саме число вислідів — та ансамблеве середнє йде вгору, а майже кожна окрема стежка (і геометричне) — вниз",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'mult-ensemble.svg'), W, H, *els)


if __name__ == '__main__':
    fig_curvature_gap()
    fig_mult_ensemble()
    fig_exposure()
    fig_known_unknowns()
    fig_responses()
    fig_exposure_decision()
    fig_regimes()
    fig_risk_premium()
    fig_leverage()
    fig_cost_curve()
    fig_deviance()
    fig_timeline()
    fig_utility()
    print("figs done")
