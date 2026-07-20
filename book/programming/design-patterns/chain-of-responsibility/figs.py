# -*- coding: utf-8 -*-
"""Фігури теми «Ланцюжок обов'язків». Вивід — ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GOLD = "#e0a800"

# ── Спільна геометрія цибулини (обидві фігури вставки proj-middleware-chain) ──
# Шари вкладені один в одного; у кожного є ВЕРХНЯ смуга (код до next())
# і НИЖНЯ смуга (код після next()). Текст починається на 62 px від лівого краю
# свого шару, значки-номери — на 26 px: між ними лишається порожньо,
# щоб діагональні стрілки трипу йшли лівим жолобом і нічого не перетинали.
W, H = 980, 620
LAYERS = [   # (x, y, w, h, колір рамки, заливка)
    (70,  64,  840, 470),
    (155, 116, 670, 366),
    (240, 168, 500, 262),
]
CORE = (325, 220, 330, 158)
BADGE_DX, TEXT_DX = 26, 62


def badge(cx, cy, n, color):
    return (circle(cx, cy, 12, fill=BG, stroke=color, sw=2.2) +
            text(cx, cy + 4.5, str(n), size=12, color=color, bold=True))


def hop(p1, p2, color):
    """Стрілка між значками, підрізана на радіус значка — вістря не в'їде в коло."""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    r = 15.0
    return arrow(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, color=color, sw=2.0)


def onion(strips, core_lines, core_style, marks):
    """strips: [(індекс шару, 'top'|'bot', текст, колір, значок|None)]"""
    f = []
    for (x, y, w, h, stroke, fill) in LAYERS:
        f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.0, rx=10))
    cx, cy, cw, ch = CORE
    f.append(rect(cx, cy, cw, ch, fill=core_style[1], stroke=core_style[0], sw=2.2, rx=10))
    f.append(mtext(cx + TEXT_DX, cy + ch / 2 - 6, core_lines, size=13,
                   color=core_style[2], anchor="start", bold=True))
    for (i, where, s, color, n) in strips:
        x, y, w, h = LAYERS[i][0], LAYERS[i][1], LAYERS[i][2], LAYERS[i][3]
        sy = y + 26 if where == 'top' else y + h - 26
        if n is not None:
            f.append(badge(x + BADGE_DX, sy, n, color))
        f.append(text(x + TEXT_DX, sy + 4.5, s, size=13, color=color, anchor="start"))
    f.extend(marks)
    return f


def pos(i, where):
    x, y, w, h = LAYERS[i][0], LAYERS[i][1], LAYERS[i][2], LAYERS[i][3]
    return (x + BADGE_DX, y + 26 if where == 'top' else y + h - 26)


def core_badge_pos():
    return (CORE[0] + BADGE_DX, CORE[1] + CORE[3] / 2)


# ── proj-middleware-chain: прохід туди-й-назад ────────────────────────────────
def fig_onion_trip():
    global LAYERS
    LAYERS = [(70, 64, 840, 470, LINE, "#f7f9fb"),
              (155, 116, 670, 366, NEG, "#eef2ff"),
              (240, 168, 500, 262, FIELD, "#eaf7ef")]
    strips = [
        (0, 'top', "logger · запам'ятовує монотонний час t₀", INK, 1),
        (1, 'top', "rateLimit · рахує цей запит з 10.0.0.7", NEG, 2),
        (2, 'top', "auth · токен добрий → state.user = olena", FIELD, 3),
        (2, 'bot', "auth · після next() роботи не має", MUTED, 5),
        (1, 'bot', "rateLimit · після next() роботи не має", MUTED, 6),
        (0, 'bot', "logger · аж ТЕПЕР знає статус: «GET /profile → 200 за 0.2 мс»", INK, 7),
    ]
    cbx, cby = core_badge_pos()
    marks = [badge(cbx, cby, 4, GOLD)]
    f = onion(strips, ["суть застосунку", "200 «Привіт, olena»"], (GOLD, "#fff9e6", "#8a6d00"), marks)

    trip = [pos(0, 'top'), pos(1, 'top'), pos(2, 'top'), (cbx, cby),
            pos(2, 'bot'), pos(1, 'bot'), pos(0, 'bot')]
    for a, b, col in zip(trip, trip[1:], [NEG, NEG, NEG, FIELD, FIELD, FIELD]):
        f.append(hop(a, b, col))

    f.append(text(700, 96, "вниз — код ДО next()", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(700, 512, "вгору — код ПІСЛЯ next()", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(W / 2, 578, "Один виклик next() ділить ланку надвоє: перша половина біжить вниз, друга — на зворотному шляху.",
                  size=12, color=MUTED))
    render(out("onion-trip.svg"), W, H, *f,
           title="Цибулина: запит іде вглиб, відповідь повертається тим самим шляхом")


# ── proj-middleware-chain: коротке замикання ─────────────────────────────────
def fig_onion_shortcircuit():
    global LAYERS
    LAYERS = [(70, 64, 840, 470, LINE, "#f7f9fb"),
              (155, 116, 670, 366, NEG, "#eef2ff"),
              (240, 168, 500, 262, POS, "#fdecea")]
    strips = [
        (0, 'top', "logger · запам'ятовує монотонний час t₀", INK, 1),
        (1, 'top', "rateLimit · рахує цей запит — квота витрачена ВЖЕ ТУТ", NEG, 2),
        (2, 'top', "auth · токена нема → 401, next() НЕ кличемо", POS, 3),
        (2, 'bot', "auth · сюди керування не повертається", MUTED, None),
        (1, 'bot', "rateLimit · після next() роботи не має", MUTED, 4),
        (0, 'bot', "logger · друкує «GET /profile → 401 за 0.0 мс» — лог однаково є", INK, 5),
    ]
    f = onion(strips, ["суть НЕ виконалася —", "auth не покликав next()"], (MUTED, "#f0f0f0", MUTED), [])

    f.append(hop(pos(0, 'top'), pos(1, 'top'), NEG))
    f.append(hop(pos(1, 'top'), pos(2, 'top'), NEG))
    f.append(hop(pos(2, 'top'), pos(1, 'bot'), POS))      # розворот просто в auth
    f.append(hop(pos(1, 'bot'), pos(0, 'bot'), FIELD))

    f.append(text(700, 96, "вниз — код ДО next()", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(700, 512, "вгору — зовнішні ланки доробляють своє", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(W / 2, 578, "Замикання відрізає лише те, що ГЛИБШЕ: зовнішні шари свою другу половину однаково відпрацюють.",
                  size=12, color=MUTED))
    render(out("onion-shortcircuit.svg"), W, H, *f,
           title="Коротке замикання: auth не кличе next() — і суть не бачить запиту")


# ═════════════════════════════════════════════════════════════════════════════
# Фігури вставки math-chain-as-fold. Власна геометрія, LAYERS не чіпають.
# ═════════════════════════════════════════════════════════════════════════════

def tbox(cx, cy, s, **kw):
    """textbox, але повертає лише SVG-фрагмент (без ширини/висоти)."""
    frag, _w, _h = textbox(cx, cy, s, **kw)
    return frag


# ── math: згортка справа перетворює плаский список на вкладений вираз ────────
def fig_fold_nesting():
    f = [text(490, 62, "маємо: список ланок і базу — жодної вкладеності",
              size=13, color=MUTED)]
    for cx, s in ((160, "ланка₁"), (320, "ланка₂"), (480, "ланка₃")):
        f.append(tbox(cx, 105, s))
    f.append(text(590, 111, "+", size=18, color=MUTED))
    f.append(tbox(710, 105, "база z", fill="#eaf7ef", stroke=FIELD))

    f.append(arrow(490, 138, 490, 208))
    f.append(mtext(512, 160, ["згортка справа: кожна ланка",
                              "обгортає РЕШТУ ланцюга"],
                   size=11, color=NEG, anchor="start"))
    f.append(text(490, 234, "ланка₁( ланка₂( ланка₃( база z ) ) )", size=14, bold=True))

    for (x, y, w, h, s, col, fill) in [
        (90,  254, 600, 180, "ланка₁ · логер", INK, "#f7f9fb"),
        (140, 292, 500, 132, "ланка₂ · ліміт частоти", NEG, "#eef2ff"),
        (190, 330, 400, 84,  "ланка₃ · автентифікація", FIELD, "#eaf7ef"),
        (240, 368, 300, 36,  "база z · «ніхто не взяв» → 404", MUTED, "#f0f0f0"),
    ]:
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=10))
        f.append(text(x + 22, y + 24, s, size=12, color=col, bold=True, anchor="start"))

    f.append(mtext(715, 272, ["перша у списку —", "найзовнішня у виразі"],
                   size=11, color=NEG, anchor="start"))
    f.append(mtext(715, 384, ["база — найглибша:", "останнє слово"],
                   size=11, color=FIELD, anchor="start"))
    f.append(text(490, 456, "Порядок списку задає глибину вкладення: перша ланка бачить запит першою, база — останньою.",
                  size=12, color=MUTED))
    render(out("fold-nesting.svg"), 980, 470, *f,
           title="Згортка справа: плаский список стає вкладеним виразом")


# ── math: сполучність — групування не змінює ланцюга ─────────────────────────
def fig_assoc_splice():
    f = [line(490, 58, 490, 178, color=MUTED, sw=1.2, dash="4,4")]

    f.append(text(255, 66, "(auth ⊕ ліміт) ⊕ лог", size=13, bold=True))
    f.append(rect(75, 88, 250, 56, fill="#eef2ff", stroke=NEG, sw=2.0, rx=8))
    f.append(tbox(140, 116, "auth"))
    f.append(tbox(258, 116, "ліміт"))
    f.append(text(348, 122, "⊕", size=17, color=MUTED))
    f.append(tbox(405, 116, "лог"))
    f.append(text(200, 164, "спершу зчепили цю пару", size=11, color=NEG))

    f.append(text(725, 66, "auth ⊕ (ліміт ⊕ лог)", size=13, bold=True))
    f.append(tbox(575, 116, "auth"))
    f.append(text(632, 122, "⊕", size=17, color=MUTED))
    f.append(rect(660, 88, 250, 56, fill="#eaf7ef", stroke=FIELD, sw=2.0, rx=8))
    f.append(tbox(725, 116, "ліміт"))
    f.append(tbox(845, 116, "лог"))
    f.append(text(785, 164, "спершу зчепили іншу пару", size=11, color=FIELD))

    f.append(arrow(300, 186, 400, 244))
    f.append(arrow(680, 186, 580, 244))
    f.append(text(490, 232, "той самий ланцюг", size=13, bold=True))

    f.append(tbox(215, 300, "auth"))
    f.append(tbox(390, 300, "ліміт"))
    f.append(tbox(560, 300, "лог"))
    f.append(tbox(745, 300, "база z", fill="#eaf7ef", stroke=FIELD))
    f.append(arrow(248, 300, 355, 300))
    f.append(arrow(424, 300, 532, 300))
    f.append(arrow(586, 300, 706, 300))

    f.append(mtext(490, 362, ["Сполучність не абстрактна: саме вона дозволяє зібрати кілька ланок в один пакет",
                              "і вставити його в ланцюг як ОДНУ ланку — так вкладений роутер стає звичайною ланкою."],
                   size=12, color=MUTED))
    render(out("assoc-splice.svg"), 980, 405, *f,
           title="Сполучність: як не групуй — ланцюг той самий")


# ── math: вартість проходу — шлях проти дерева ───────────────────────────────
def fig_cost_tree():
    f = [line(490, 58, 490, 418, color=MUTED, sw=1.2, dash="4,4")]

    f.append(text(250, 74, "kᵢ ≤ 1 — щонайбільше один виклик", size=12, color=FIELD, bold=True))
    ys = [108, 164, 220, 276, 332]
    for y, s in zip(ys, ["ланка₁", "ланка₂", "ланка₃", "ланка₄", "база z"]):
        last = (s == "база z")
        f.append(tbox(250, y, s, fill="#eaf7ef" if last else FILL,
                      stroke=FIELD if last else LINE))
    for y1, y2 in zip(ys, ys[1:]):
        f.append(arrow(250, y1 + 21, 250, y2 - 21))
    f.append(text(250, 382, "прохід — ШЛЯХ", size=13, bold=True))
    f.append(text(250, 406, "n кроків · Θ(n)", size=13, color=FIELD, bold=True))

    f.append(text(755, 74, "kᵢ = 2 — ланка-повтор кличе двічі", size=12, color=POS, bold=True))
    lv = [[755], [655, 855], [605, 705, 805, 905],
          [580, 630, 680, 730, 780, 830, 880, 930]]
    lvy = [108, 164, 220, 276]
    for d in range(3):
        for i, px in enumerate(lv[d]):
            for cx in (lv[d + 1][2 * i], lv[d + 1][2 * i + 1]):
                f.append(line(px, lvy[d] + 12, cx, lvy[d + 1] - 12, color=POS, sw=1.3))
    for d in range(4):
        for cx in lv[d]:
            f.append(circle(cx, lvy[d], 12 if d < 3 else 7,
                            fill="#fdecea", stroke=POS, sw=1.8))
    for y, s in zip(lvy, ["ланка₁", "ланка₂ ×2", "ланка₃ ×4", "база ×8"]):
        f.append(text(500, y + 4, s, size=10, color=MUTED, anchor="start"))
    f.append(text(755, 320, "кожен шар множить, а не додає", size=11, color=MUTED))
    f.append(text(755, 382, "прохід — ДЕРЕВО", size=13, bold=True))
    f.append(text(755, 406, "kⁿ вузлів · Θ(kⁿ)", size=13, color=POS, bold=True))

    f.append(mtext(490, 440, ["Три шари, кожен по чотири спроби, дають 4³ = 64 запити в найглибший вузол —",
                              "саме тоді, коли він і так не витримує. Тому koa кидає помилку на другий виклик next()."],
                   size=12, color=MUTED))
    render(out("cost-tree.svg"), 980, 472, *f,
           title="Скільки разів ланка кличе next() — і що з цього виходить")


# ═════════════════════════════════════════════════════════════════════════════
# Фігури вставки hist-chain-birth. Власна геометрія, LAYERS не чіпають.
# ═════════════════════════════════════════════════════════════════════════════

# ── hist: гірлянда дозволу на шині Unibus ────────────────────────────────────
def fig_daisy_grant():
    W2, H2 = 1075, 400
    f = []

    f.append(fitbox(40, 110, 140, 125, ["процесор", "(арбітр)", "", "видає BG,", "не знає кому"],
                    size=13, fill="#eef2ff", stroke=NEG, color=NEG, bold=True))

    # (x, назва, рядок1, рядок2, колір рамки, заливка)
    SLOTS = [
        (215, "диск",          "не просив —",      "повторює сигнал",   LINE,  "#f7f9fb"),
        (380, "порожній слот", "перемичка G727:",  "тільки пропускає",  MUTED, "#f0f0f0"),
        (545, "термінал",      "ПРОСИВ → бере",    "далі не пускає",    FIELD, "#eaf7ef"),
        (710, "принтер",       "теж просив, але",  "сигналу не бачить", POS,   "#fdecea"),
        (875, "стрічка",       "не просила",       "і не дізнається",   MUTED, "#f7f9fb"),
    ]
    SW = 140
    for (x, name, l1, l2, col, fill) in SLOTS:
        f.append(rect(x, 110, SW, 125, fill=fill, stroke=col, sw=2.0, rx=8))
        f.append(text(x + SW / 2, 134, name, size=13, color=col, bold=True))
        f.append(text(x + SW / 2, 200, l1, size=12, color=INK))
        f.append(text(x + SW / 2, 218, l2, size=12, color=INK))

    # дріт BG: живий (синій) до термінала, далі мертвий (сірий пунктир)
    WY, STOP = 172, 612
    f.append(arrow(180, WY, 213, WY, color=NEG, sw=2.4))
    f.append(text(197, WY - 10, "BG", size=12, color=NEG, bold=True))
    f.append(line(215, WY, 355, WY, color=NEG, sw=2.4))      # диск наскрізь
    f.append(arrow(355, WY, 378, WY, color=NEG, sw=2.4))
    f.append(line(380, WY, 520, WY, color=NEG, sw=2.4))      # перемичка наскрізь
    f.append(arrow(520, WY, 543, WY, color=NEG, sw=2.4))
    f.append(line(545, WY, STOP, WY, color=NEG, sw=2.4))     # і тут обривається
    f.append(circle(STOP, WY, 7, fill=FIELD, stroke=FIELD, sw=2))
    f.append(line(STOP, WY, 1015, WY, color=MUTED, sw=1.6, dash="6 5"))
    f.append(text(838, WY - 12, "сюди BG не доходить ніколи", size=12, color=MUTED))

    # спільний дріт BR — усі охочі смикають разом
    BY = 292
    f.append(line(1015, BY, 110, BY, color=POS, sw=2.2))
    f.append(line(STOP, 235, STOP, BY, color=POS, sw=2.2))   # термінал просить
    f.append(line(780, 235, 780, BY, color=POS, sw=2.2))     # принтер просить
    f.append(arrow(110, BY, 110, 237, color=POS, sw=2.2))
    f.append(text(430, BY + 22, "BR — один дріт на всіх: процесор чує, що хтось просив, і не чує хто",
                  size=12, color=POS))

    f.append(text(W2 / 2, 350, "Гірлянда відповідає на «хто?» без арбітра: перший, хто просив, забирає сигнал і далі не пускає.",
                  size=12, color=INK))
    f.append(text(W2 / 2, 374, "Порожній слот РОЗРИВАЄ ланцюг — тому туди ставлять перемичку, чия єдина робота — передати далі.",
                  size=12, color=MUTED))
    render(out("daisy-grant.svg"), W2, H2, *f,
           title="Unibus: правило «не моє — передай сусідові», зашите в мідь")


# ── hist: три незалежні лінії сходяться в одну назву ─────────────────────────
def fig_chain_timeline():
    W2, H2 = 1250, 470
    f = []
    BW, BH = 230, 80
    COLS = [155, 415, 675]

    LANES = [
        (105, "залізо", LINE, "#f7f9fb", [
            ["1954 · NBS DYSEAC", "переривання від", "пристроїв вводу-виводу"],
            ["1957 · Electrologica X1", "Дейкстра: машина стала", "недетермінованою"],
            ["1970 · DEC Unibus", "гірлянда BG: не моє —", "передай дротом далі"],
        ]),
        (245, "мови й помилки", NEG, "#eef2ff", [
            ["1964–65 · PL/I", "ON-unit: помилка спливає", "вгору по стеку викликів"],
            ["1975 · Джон Ґуденаф", "перша спроба записати", "правило як правило"],
            ["1989–91 · C++", "«вернутися чи згорнути»:", "згортаємо — і крапка"],
        ]),
        (385, "каркаси GUI", FIELD, "#eaf7ef", [
            ["1985 · Apple MacApp", "клас «Event-Handler»"],
            ["1988 · ET++ Еріка Ґамми", "теж «Event-Handler»"],
            ["1989 · NeXT «Responder»,", "Symantec TCL «Bureaucrat»"],
        ]),
    ]

    for (cy, label, col, fill, items) in LANES:
        f.append(text(80, cy + 5, label, size=13, color=col, bold=True))
        for i, (x, lines) in enumerate(zip(COLS, items)):
            f.append(fitbox(x, cy - BH / 2, BW, BH, lines, size=13,
                            fill=fill, stroke=col, color=INK))
            if i < 2:
                f.append(arrow(x + BW, cy, x + BW + 28, cy, color=col, sw=2.0))

    f.append(fitbox(965, 170, 255, 150,
                    ["1994 · «банда чотирьох»", "Chain of Responsibility", "",
                     "одне ім'я на три", "незалежні винаходи"],
                    size=13, fill="#fff9e6", stroke=GOLD, color="#8a6d00", bold=True))
    f.append(arrow(905, 105, 962, 212, color=LINE, sw=2.0))
    f.append(arrow(905, 245, 960, 245, color=LINE, sw=2.0))
    f.append(arrow(905, 385, 962, 288, color=LINE, sw=2.0))

    f.append(text(W2 / 2, 445, "Три лінії не знали одна про одну — і кожна прийшла до того самого: «не моє — передай наступному».",
                  size=12, color=MUTED))
    render(out("chain-timeline.svg"), W2, H2, *f,
           title="Одна форма, відкрита тричі незалежно — і названа аж наприкінці")


# ═════════════════════════════════════════════════════════════════════════════
# Фігури головної статті chain-of-responsibility.md.
# ═════════════════════════════════════════════════════════════════════════════

# ── стаття: загальний рух запиту вздовж ланцюга ───────────────────────────────
def fig_chain_flow():
    W2, H2 = 1070, 440
    f = [text(W2 / 2, 60,
              "Сірі стрілки — «не моє, передаю далі»; зелені — «моє, беру і зупиняю»",
              size=12, color=MUTED)]

    f.append(fitbox(20, 105, 150, 80, ["відправник", "кидає запит", "першій ланці"],
                    size=12, fill="#eef2ff", stroke=NEG, color=NEG, bold=True))

    LX = [210, 420, 630]
    LW = 190
    for i, x in enumerate(LX, start=1):
        f.append(fitbox(x, 105, LW, 80, [f"Ланка {i}", "перевіряє поріг"],
                        size=13, fill=FILL, stroke=LINE, bold=True))

    f.append(fitbox(850, 105, 180, 80, ["ніхто не взяв", "запит випадає", "необробленим"],
                    size=12, fill="#f7f9fb", stroke=MUTED, color=MUTED, bold=True))

    chain_x = [(170, 210), (400, 420), (610, 630), (820, 850)]
    for (xa, xb) in chain_x:
        f.append(arrow(xa, 145, xb, 145, color=MUTED, sw=2.0))

    for x in LX:
        cx = x + LW / 2
        f.append(arrow(cx, 187, cx, 298, color=FIELD, sw=2.0))
        f.append(fitbox(x, 300, LW, 70, ["поріг підходить →", "бере й зупиняє"],
                        size=12, fill="#eaf7ef", stroke=FIELD, color=FIELD, bold=True))

    f.append(text(W2 / 2, 405,
                  "Якщо жодна ланка не взяла — запит доходить до кінця й випадає необробленим.",
                  size=12, color=MUTED))
    render(out("chain-flow.svg"), W2, H2, *f,
           title="Ланцюг: кожна ланка перевіряє поріг і або бере, або передає далі")


# ── стаття: скелет типів + зчеплені екземпляри ────────────────────────────────
def fig_handler_skeleton():
    W2, H2 = 1060, 620
    f = []

    f.append(fitbox(380, 60, 300, 70,
                    ["«інтерфейс» Approver", "setNext(next) · handle(запит)"],
                    size=13, fill="#eef2ff", stroke=NEG, color=NEG, bold=True))
    f.append(arrow(530, 130, 530, 168, color=MUTED, sw=2.0))

    f.append(fitbox(280, 170, 500, 100,
                    ["BaseApprover", "поле: next",
                     "next є → next.handle()", "нема next → типове «нічого»"],
                    size=13, fill=FILL, stroke=LINE, bold=True))

    CX = [180, 530, 880]
    for cx in CX:
        f.append(arrow(530, 270, cx, 308, color=MUTED, sw=1.8))

    CLASSES = [
        (40,  "TeamLead", "≤ 1 000 → сам обробляє"),
        (390, "Manager",  "≤ 10 000 → сам обробляє"),
        (740, "Director", "≤ 100 000 → сам обробляє"),
    ]
    for (x, name, rule) in CLASSES:
        f.append(fitbox(x, 310, 280, 110, [name, rule, "інакше → передає далі"],
                        size=13, fill=FILL, stroke=LINE, bold=True))

    f.append(text(530, 440, "Час виконання: екземпляри зчеплені полем next",
                  size=12, color=MUTED, bold=True))
    f.append(line(40, 455, 1020, 455, color=MUTED, sw=1.2, dash="5,5"))

    INSTS = [(70, "lead: TeamLead"), (420, "mgr: Manager"), (770, "dir: Director")]
    IW = 220
    for (x, label) in INSTS:
        f.append(fitbox(x, 480, IW, 70, [label], size=13, fill="#eaf7ef", stroke=FIELD,
                        color=FIELD, bold=True))
    f.append(arrow(290, 515, 418, 515, color=FIELD, sw=2.0))
    f.append(text(354, 505, "next", size=11, color=FIELD, bold=True))
    f.append(arrow(640, 515, 768, 515, color=FIELD, sw=2.0))
    f.append(text(704, 505, "next", size=11, color=FIELD, bold=True))
    f.append(arrow(990, 515, 1013, 515, color=MUTED, sw=1.8))
    f.append(fitbox(995, 490, 55, 50, ["null"], size=11, fill="#f7f9fb", stroke=MUTED,
                    color=MUTED, bold=True))

    f.append(text(530, 590,
                  "Механіку «next» клас має один раз; кожен екземпляр лише посилається на наступний.",
                  size=12, color=MUTED))
    render(out("handler-skeleton.svg"), W2, H2, *f,
           title="Скелет: інтерфейс, спільна основа, конкретні ланки — і зчеплені екземпляри")


# ── стаття: дві породи ланцюга поруч ───────────────────────────────────────────
def fig_two_flavors():
    W2, H2 = 1040, 460
    f = []
    f.append(text(255, 50, "перший, хто може — бере", size=14, color=NEG, bold=True))
    f.append(text(785, 50, "кожен додає своє", size=14, color=FIELD, bold=True))
    f.append(line(520, 45, 520, 395, color=MUTED, sw=1.2, dash="5,5"))

    # ліва порода: зупиняється на другій ланці
    LX, LW = 125, 260
    f.append(fitbox(LX, 90, LW, 64, ["Ланка 1", "не моє → далі"],
                    size=13, fill=FILL, stroke=LINE, bold=True))
    f.append(arrow(255, 154, 255, 178, color=MUTED, sw=2.0))
    f.append(fitbox(LX, 180, LW, 64, ["Ланка 2", "моє! → бере, зупиняє"],
                    size=13, fill="#eaf7ef", stroke=FIELD, color=FIELD, bold=True))
    f.append(text(255, 260, "рух зупинився тут", size=10, color=MUTED, italic=True))
    f.append(fitbox(LX, 270, LW, 64, ["Ланка 3", "не бачить запиту"],
                    size=13, fill="#f0f0f0", stroke=MUTED, color=MUTED, bold=True))
    f.append(text(255, 364, "приклади: погодження, обробка винятків", size=11, color=MUTED))

    # права порода: усі відпрацьовують по черзі
    RX = 655
    f.append(fitbox(RX, 90, LW, 64, ["Ланка 1", "робить своє → далі"],
                    size=13, fill=FILL, stroke=LINE, bold=True))
    f.append(arrow(785, 154, 785, 178, color=FIELD, sw=2.0))
    f.append(fitbox(RX, 180, LW, 64, ["Ланка 2 · перевірка прав", "звично → далі; інколи → обрив"],
                    size=12, fill=FILL, stroke=LINE, bold=True))
    f.append(arrow(785, 244, 785, 268, color=FIELD, sw=2.0))
    f.append(fitbox(RX, 270, LW, 64, ["Ланка 3", "серцевина застосунку"],
                    size=13, fill=FILL, stroke=LINE, bold=True))
    f.append(arrow(915, 212, 938, 212, color=POS, sw=1.8))
    f.append(text(978, 198, "інколи", size=10, color=POS))
    f.append(fitbox(938, 190, 90, 44, ["обрив!"], size=11, fill="#fdecea", stroke=POS,
                    color=POS, bold=True))
    f.append(text(785, 364, "приклади: логування, middleware", size=11, color=MUTED))

    f.append(text(520, 420,
                  "Обидві породи — той самий каркас: різниця лише в одному рішенні всередині ланки.",
                  size=13, color=INK, bold=True))
    render(out("two-flavors.svg"), W2, H2, *f,
           title="Дві породи ланцюга: хто зупиняє рух")


if __name__ == "__main__":
    fig_onion_trip()
    fig_onion_shortcircuit()
    fig_fold_nesting()
    fig_assoc_splice()
    fig_cost_tree()
    fig_daisy_grant()
    fig_chain_timeline()
    fig_chain_flow()
    fig_handler_skeleton()
    fig_two_flavors()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
