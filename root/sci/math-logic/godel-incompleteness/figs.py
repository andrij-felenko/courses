# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Теореми Геделя про неповноту».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = POS          # «ні», суперечність, гаряче
BLUE  = NEG          # припущення, нейтральне холодне
GREEN = FIELD        # повне/розв'язне, висновок
AMBER = "#b9770e"
LRED  = "#fdecea"
LBLUE = "#eef4ff"
LGREEN = "#eafaf0"
LGREY = "#f2f3f5"


def lines_at(x, y0, rows, size=11.5, color=INK, lh=19, anchor="start"):
    """Стовпчик рядків тексту від (x, y0) вниз."""
    out = []
    for i, s in enumerate(rows):
        out.append(text(x, y0 + i * lh, s, size=size, color=color, anchor=anchor))
    return out


def pill(cx, cy, s, col, size=12):
    """Кольорова капсула з білим написом."""
    w = text_width(s, size, True) + 24
    return [rect(cx - w / 2, cy - 14, w, 28, fill=col, stroke=col, sw=1, rx=14),
            text(cx, cy + size * 0.36, s, size=size, color="#ffffff", bold=True)]


# ── Фігура 1: три бажання Гільберта і три «ні» ────────────────────────────────
# Повнота, фінітно доведена несуперечливість, розв'язність — і три результати
# 1931/1936, що закрили кожне. Унизу — три умови, без яких удар не влучає.
def fig_hilbert_wishes():
    W, H = 1000, 606
    P = [text(W / 2, 34, "Програма Гільберта: три бажання і три «ні»", size=17, bold=True),
         text(W / 2, 56, "1928 — що математика мала засвідчити сама про себе", size=12, color=MUTED)]
    cols = [175, 500, 825]
    cw = 290

    wishes = [
        (GREEN, "Повнота", ["кожне твердження — або", "доводиться, або спросто-", "вується; жодне не зависає"]),
        (BLUE, "Несуперечливість", ["з F не виводяться разом", "A і ¬A — і це доведено", "фінітними засобами"]),
        (AMBER, "Розв'язність", ["є механічна процедура, що", "про кожне твердження скаже:", "доказовне воно чи ні"]),
    ]
    wtop = 80
    for cx, (col, title, body) in zip(cols, wishes):
        P.append(rect(cx - cw / 2, wtop, cw, 120, fill=BG, stroke=col, sw=2, rx=10))
        P.append(text(cx, wtop + 26, title, size=14, color=col, bold=True))
        P.extend(lines_at(cx - cw / 2 + 18, wtop + 52, body))
        P.append(arrow(cx, wtop + 122, cx, 244, color=MUTED, sw=1.8))

    results = [
        ("Перша теорема · 1931", ["існує істинне речення, яке", "не доводиться й не спросто-", "вується — F неповна"], "ні — Гедель"),
        ("Друга теорема · 1931", ["F не може довести", "власної несуперечливості", "своїми ж засобами"], "ні — Гедель"),
        ("Entscheidungsproblem · 1936", ["такого алгоритму немає:", "доказовність неможливо", "розв'язати механічно"], "ні — Черч і Тюринг"),
    ]
    rtop = 246
    for cx, (title, body, stamp) in zip(cols, results):
        P.append(rect(cx - cw / 2, rtop, cw, 120, fill=LRED, stroke=RED, sw=2, rx=10))
        P.append(text(cx, rtop + 24, title, size=12.5, color=RED, bold=True))
        P.extend(lines_at(cx - cw / 2 + 18, rtop + 48, body, color=INK))
        P.extend(pill(cx, rtop + 120, stamp, RED))

    # смуга умов
    btop = 420
    P.append(rect(30, btop, W - 60, 150, fill=LGREY, stroke=MUTED, sw=1.6, rx=12))
    P.append(text(W / 2, btop + 32, "Але виделка влучає ЛИШЕ в систему, яка водночас:", size=14, bold=True))
    conds = [(200, "① несуперечлива"), (500, "② механічно аксіоматизована"),
             (800, "③ вміщає арифметику (з ×)")]
    for cx, s in conds:
        P.extend(pill(cx, btop + 78, s, GREEN, size=12.5))
    P.append(text(W / 2, btop + 122, "приберіть будь-яку з трьох умов — і теорема більше не діє",
                  size=12, color=MUTED))
    render("img/hilbert-wishes.svg", W, H, *P)


# ── Фігура 2: міст Геделя — синтаксис стає арифметикою ────────────────────────
# Формула → коди символів → показники простих → одне число (розклад однозначний,
# дорога назад одна). Той самий прийом — до послідовності формул: доведення теж
# стає числом. Наслідок: Prf(y,x) — арифметичне відношення мовою самої системи.
def fig_godel_numbering():
    W, H = 1020, 662
    P = [text(W / 2, 32, "Міст Геделя: синтаксис стає арифметикою", size=17, bold=True)]

    P.append(text(44, 62, "Крок 1 — формула стає одним числом", size=13.5, color=GREEN, anchor="start", bold=True))
    xs = [285, 405, 525]
    rows = [(88, "символ", ["0", "=", "0"], INK),
            (140, "код", ["1", "3", "1"], INK),
            (192, "просте pᵢ", ["2", "3", "5"], NEG),
            (244, "показник", ["2¹", "3³", "5¹"], INK)]
    labx = 210
    for top, lab, cells, col in rows:
        P.append(text(labx, top + 29, lab, size=12, color=MUTED, anchor="end"))
        for cx, s in zip(xs, cells):
            P.append(rect(cx - 24, top, 48, 44, fill=BG, stroke=col, sw=1.6, rx=4))
            P.append(text(cx, top + 30, s, size=17, color=col, bold=True))
    # знаки множення між показниками + вихід на 270
    P.append(text((xs[0] + xs[1]) / 2, 274, "·", size=22, color=MUTED))
    P.append(text((xs[1] + xs[2]) / 2, 274, "·", size=22, color=MUTED))
    P.append(arrow(xs[2] + 30, 266, 636, 266, color=MUTED, sw=1.8))
    b, bw, bh = textbox(690, 266, "270", size=24, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=16)
    P.append(b)
    P.append(text(W / 2 + 30, 322, "розклад 270 на прості — 2¹·3³·5¹ — однозначний, тож дорога назад рівно одна",
                  size=12, color=MUTED))

    P.append(text(44, 372, "Крок 2 — доведення (ланцюжок формул) стає одним числом", size=13.5, color=NEG, anchor="start", bold=True))
    chain = [
        (150, LGREY, INK, ["доведення", "⟨φ₁, φ₂, …, φₙ⟩", "ланцюжок формул"]),
        (400, LBLUE, NEG, ["кожна формула φᵢ", "вже має свій код", "⌜φᵢ⌝ (крок 1)"]),
        (655, LGREY, INK, ["2^⌜φ₁⌝ · 3^⌜φ₂⌝ ·", "… · pₙ^⌜φₙ⌝"]),
        (895, LGREEN, GREEN, ["одне число —", "код усього", "доведення"]),
    ]
    boxes = []
    for cx, fill, stroke, body in chain:
        b, bw, bh = textbox(cx, 438, "\n".join(body), size=12, fill=fill, stroke=stroke, color=INK, pad=12)
        boxes.append((cx, bw))
        P.append(b)
    for (cx, bw), (ncx, nbw) in zip(boxes, boxes[1:]):
        P.append(arrow(cx + bw / 2 + 4, 438, ncx - nbw / 2 - 4, 438, color=MUTED, sw=1.8))

    b, _, _ = textbox(W / 2, 604,
                      "Тепер «y — код доведення формули x» — це відношення Prf(y, x) між двома числами.\n"
                      "Воно перевіряється скінченно, отже записується формулою мовою самої арифметики.",
                      size=13, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=14)
    P.append(b)
    render("img/godel-numbering.svg", W, H, *P)


# ── Фігура 3: виделка першої теореми і безкінечна латка ───────────────────────
# G ⟺ «G не доводиться». Доведення G → суперечність; доведення ¬G → ω-суперечли-
# вість. Обидва виходи замкнені, F мовчить, G істинне ззовні. Латка додає G
# аксіомою — але нова система має власне нове G′. Дірок нескінченно.
def fig_godel_fork():
    W, H = 1020, 700
    P = [text(W / 2, 32, "Виделка першої теореми — і чому латка не рятує", size=17, bold=True)]

    b, gw, gh = textbox(510, 78, "G  ⟺  «G не доводиться в F»", size=15,
                        fill=FILL, stroke=INK, color=INK, bold=True, pad=13)
    P.append(b)
    P.append(arrow(510, 78 + gh / 2, 300, 148, color=MUTED, sw=1.8))
    P.append(arrow(510, 78 + gh / 2, 720, 148, color=MUTED, sw=1.8))

    def branch(cx, assume, mid, verdict):
        out = []
        b, w, h = textbox(cx, 172, assume, size=12.5, fill=FILL, stroke=BLUE, color=INK, bold=True, pad=11)
        out.append(b)
        out.append(arrow(cx, 172 + h / 2, cx, 236, color=MUTED, sw=1.7))
        b, w, h = textbox(cx, 274, mid, size=11.5, fill=FILL, stroke=MUTED, color=INK, pad=11)
        out.append(b)
        out.append(arrow(cx, 274 + h / 2, cx, 352, color=MUTED, sw=1.7))
        b, w, h = textbox(cx, 378, verdict, size=13, fill=LRED, stroke=RED, color=RED, bold=True, pad=12)
        out.append(b)
        return out

    P.extend(branch(285, "Припустімо:  F ⊢ G",
                    "G каже «мене не доводять».\nОтже F довела хибне\nпро власну арифметику.",
                    "F суперечлива  ✗"))
    P.extend(branch(735, "Припустімо:  F ⊢ ¬G",
                    "«доведення G існує» — та для\nкожного y = 0, 1, 2, … F\nвизнає: «це не воно».",
                    "F ω-суперечлива  ✗"))

    P.append(arrow(285, 398, 470, 438, color=RED, sw=1.7))
    P.append(arrow(735, 398, 550, 438, color=RED, sw=1.7))
    b, _, _ = textbox(510, 462, "Отже, ні G, ні ¬G — F мовчить.\nА ми ззовні бачимо: G істинне.",
                      size=13.5, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=12)
    P.append(b)

    P.append(line(40, 522, W - 40, 522, color="#dfe3e8", sw=1.4))
    P.append(text(44, 548, "Спроба порятунку — і чому вона безкінечна:", size=13.5, color=INK, anchor="start", bold=True))
    patch = [
        (165, LGREY, INK, ["додаймо G", "аксіомою до F"]),
        (430, LBLUE, NEG, ["нова система", "F′ = F + {G}"]),
        (770, LGREY, INK, ["інший список аксіом → інша", "нумерація → своє нове", "речення Геделя G′, недоказовне в F′"]),
    ]
    pboxes = []
    for cx, fill, stroke, body in patch:
        b, bw, bh = textbox(cx, 604, "\n".join(body), size=11.5, fill=fill, stroke=stroke, color=INK, pad=11)
        pboxes.append((cx, bw))
        P.append(b)
    for (cx, bw), (ncx, nbw) in zip(pboxes, pboxes[1:]):
        P.append(arrow(cx + bw / 2 + 4, 604, ncx - nbw / 2 - 4, 604, color=MUTED, sw=1.8))
    P.append(text(W / 2, 666, "Дірку залатано — поруч зяє наступна. Кожна латка приносить своє G.",
                  size=12.5, color=RED, bold=True))
    render("img/godel-fork.svg", W, H, *P)


# ── Фігура 4: де стоїть стіна — на переході від додавання до множення ─────────
# Драбина систем: слабкі повні й розв'язні; стіна встає, щойно до додавання
# додали множення. Праворуч — виняток: істинна арифметика повна, але її не
# виписати механічним списком, тож теорема її не стосується.
def fig_where_the_wall():
    W, H = 1020, 600
    P = [text(W / 2, 34, "Де стоїть стіна неповноти", size=17, bold=True),
         text(W / 2, 56, "усе вирішує один значок — множення", size=12, color=MUTED)]

    bx, bw = 60, 550

    def bar(top, name, sub, status, zone_fill, zone_stroke, stat_col):
        out = [rect(bx, top, bw, 50, fill=zone_fill, stroke=zone_stroke, sw=1.7, rx=8)]
        out.append(text(bx + 18, top + 22, name, size=13, color=INK, anchor="start", bold=True))
        out.append(text(bx + 18, top + 40, sub, size=10.5, color=MUTED, anchor="start"))
        out.append(text(bx + bw - 16, top + 31, status, size=12, color=stat_col, anchor="end", bold=True))
        return out

    P.extend(bar(84, "ZFC — аксіоматика теорії множин", "звичний фундамент усієї математики",
                 "неповна", LRED, RED, RED))
    P.extend(bar(142, "Арифметика Пеано (PA)", "натуральні числа з індукцією",
                 "неповна", LRED, RED, RED))
    P.extend(bar(200, "Арифметика Робінсона Q", "зовсім слабка, навіть без індукції",
                 "неповна · нерозв'язна", LRED, RED, RED))

    # стіна
    P.append(rect(bx, 264, bw, 44, fill=RED, stroke=RED, sw=1, rx=8))
    P.append(text(bx + bw / 2, 291, "◄  тут до додавання доклали МНОЖЕННЯ  ×  ►",
                  size=13, color="#ffffff", bold=True))

    P.extend(bar(322, "Арифметика Пресбургера", "+, <, індукція — але БЕЗ множення",
                 "повна · розв'язна", LGREEN, GREEN, GREEN))
    P.extend(bar(380, "Логіка предикатів 1-го порядку", "чиста логіка без арифметики",
                 "повна (Гедель, 1929)", LGREEN, GREEN, GREEN))
    P.extend(bar(438, "Числення висловлювань", "лише зв'язки ¬ ∧ ∨ →",
                 "повна · розв'язна", LGREEN, GREEN, GREEN))

    # стрілка «сила росте»
    P.append(arrow(44, 480, 44, 92, color=MUTED, sw=1.6))
    P.append(text(30, 300, "сила системи росте", size=10.5, color=MUTED, anchor="middle"))

    P.append(text(W / 2, 528, "Приберіть множення — і Пресбургер спокійно повний і розв'язний.",
                  size=12.5, color=INK, bold=True))
    P.append(text(W / 2, 550, "Уся драма Геделя вміщається в один значок «×».", size=12, color=MUTED))

    # права виноска — істинна арифметика
    cx0, cw0, ctop = 648, 340, 150
    P.append(rect(cx0, ctop, cw0, 240, fill=LGREY, stroke=AMBER, sw=1.8, rx=10))
    P.append(text(cx0 + 20, ctop + 28, "Третя умова — і виняток", size=13, color=AMBER, anchor="start", bold=True))
    body = ["Істинна арифметика — усі істини про ℕ —",
            "ПОВНА: кожне твердження про числа",
            "в ній або є, або спростоване.",
            "",
            "Але її не можна ефективно аксіома-",
            "тизувати: список її «аксіом» неможливо",
            "задати механічно.",
            "",
            "Порушено умову ②, тож теорема",
            "Геделя її просто не стосується."]
    P.extend(lines_at(cx0 + 20, ctop + 54, body, size=11.5, lh=18.5, color=INK))
    render("img/where-the-wall.svg", W, H, *P)


# ── Фігура 5 (вставка hist): стрічка часу — криза, програма, крах ─────────────
# Вертикальна вісь від тріщини в основах (1902) до надгробка (1943). Кульмінація
# — два дні в Кенігсберзі віч-на-віч: тиха репліка Геделя 7-го і промова
# Гільберта «Wir müssen wissen» 8-го. Далі — поступка фон Неймана й публікація.
def fig_two_speeches():
    W, H = 1060, 792
    SX = 530
    P = [text(W / 2, 32, "Тридцять років розбігу і два дні", size=17, bold=True),
         text(W / 2, 54, "від тріщини в основах математики до надгробка з викликом долі", size=12, color=MUTED)]
    P.append(line(SX, 74, SX, H - 24, color="#c8ccd2", sw=2.6))

    def node(y, side, fill, stroke, body):
        cx = 300 if side == "L" else 760
        b, w, h = textbox(cx, y, "\n".join(body), size=11.5, fill=fill, stroke=stroke,
                          color=INK, pad=12, min_w=300)
        out = [circle(SX, y, 7, fill=stroke, stroke=stroke, sw=1)]
        if side == "L":
            out.append(line(cx + w / 2, y, SX - 7, y, color=stroke, sw=1.6))
        else:
            out.append(line(cx - w / 2, y, SX + 7, y, color=stroke, sw=1.6))
        out.append(b)
        return out

    P.extend(node(110, "R", LRED, RED,
                  ["1902 · Тріщина в основі",
                   "Рассел пише Фреге: множина всіх множин,",
                   "які не містять себе, суперечлива.",
                   "«Арифметика хитається»."]))
    P.extend(node(206, "L", LBLUE, BLUE,
                  ["1925 · Ліки Гільберта",
                   "«Нікому не вигнати нас із раю Кантора».",
                   "Врятувати математику фінітним",
                   "доведенням несуперечливості."]))
    P.extend(node(302, "R", LGREY, MUTED,
                  ["1928 · Три бажання оформлено",
                   "Гільберт і Аккерман ставлять",
                   "Entscheidungsproblem; того ж року",
                   "Брауера виганяють — «війна жаб і мишей»."]))

    # Кульмінація — двоє діб у Кенігсберзі
    pill_y = 372
    pb, pw, ph = textbox(SX, pill_y, "Кенігсберг · вересень 1930", size=12,
                         fill="#fef7e6", stroke=AMBER, color=INK, bold=True, pad=10, rx=14)
    P.append(pb)
    cy = 470
    lb, lw, lh = textbox(248, cy,
                         "\n".join(["7 вересня · круглий стіл",
                                    "Гедель кидає тиху репліку: у",
                                    "несуперечливій системі є істинне,",
                                    "але недоказовне твердження.",
                                    "Почув лише фон Нейман."]),
                         size=11.5, fill=LBLUE, stroke=BLUE, color=INK, pad=12)
    rb, rw, rh = textbox(812, cy,
                         "\n".join(["8 вересня · промова в радіоефір",
                                    "Гільберт: «Wir müssen wissen.",
                                    "Wir werden wissen».",
                                    "Він ще не знає, що напередодні",
                                    "його програму вже спростовано."]),
                         size=11.5, fill="#fef7e6", stroke=AMBER, color=INK, pad=12)
    P.append(circle(SX, cy, 8, fill=AMBER, stroke=AMBER, sw=1))
    P.append(line(248 + lw / 2, cy, SX - 8, cy, color=BLUE, sw=1.6))
    P.append(line(812 - rw / 2, cy, SX + 8, cy, color=AMBER, sw=1.6))
    P.append(line(SX, pill_y + ph / 2, SX, cy - 8, color=AMBER, sw=1.6, dash="3,3"))
    P.append(lb)
    P.append(rb)

    P.extend(node(576, "L", LBLUE, BLUE,
                  ["листопад 1930 · поступка",
                   "Фон Нейман виводить другу теорему",
                   "(лист 20.XI) — та Гедель здав рукопис",
                   "17.XI. Першість визнано за Геделем."]))
    P.extend(node(664, "R", LGREY, MUTED,
                  ["1931 · надруковано",
                   "Стаття виходить у «Monatshefte».",
                   "Криза стала теоремою."]))
    P.extend(node(724, "L", LGREEN, GREEN,
                  ["1943 · надгробок у Геттінгені",
                   "На камені — ті самі слова.",
                   "Виклик пережив власне спростування."]))
    render("img/two-speeches.svg", W, H, *P)


# ── Фігура 6 (вставка math): β-функція — послідовність у пару чисел без степеня ─
# (a₀,a₁,a₂) → d=4! → модулі 1+(i+1)d попарно взаємно прості → КТО дає c →
# β(c,d,i)=остача c за модулем mᵢ повертає кожен член. Лише +, ·, остача.
def fig_beta_crt():
    W, H = 1020, 606
    P = [text(W / 2, 32, "β-функція: послідовність — у пару чисел, без жодного степеня", size=16.5, bold=True),
         text(W / 2, 54, "член дістається самою остачею — тому це під силу навіть найслабшій арифметиці", size=12, color=MUTED)]

    # Крок 1 — послідовність
    P.append(text(60, 96, "Крок 1 — ось послідовність (це коди «0 = 0»)", size=13, color=NEG, anchor="start", bold=True))
    seqx = [370, 490, 610]
    for cx, s in zip(seqx, ["a₀ = 1", "a₁ = 3", "a₂ = 1"]):
        P.append(rect(cx - 52, 108, 104, 42, fill=LBLUE, stroke=NEG, sw=1.6, rx=6))
        P.append(text(cx, 134, s, size=14, color=INK, bold=True))

    # Крок 2 — модулі
    P.append(text(60, 194, "Крок 2 — беремо d = 4! = 24 і будуємо модулі  mᵢ = 1 + (i+1)·d", size=13, color=NEG, anchor="start", bold=True))
    for cx, s in zip(seqx, ["m₀ = 25", "m₁ = 49", "m₂ = 73"]):
        P.append(rect(cx - 52, 206, 104, 42, fill=FILL, stroke=MUTED, sw=1.6, rx=6))
        P.append(text(cx, 232, s, size=13.5, color=INK, bold=True))
    b, _, _ = textbox(838, 227, "попарно\nвзаємно прості\n(d кратне 4!)", size=11.5, fill=LGREY, stroke=MUTED, color=INK, pad=12)
    P.append(b)
    P.append(arrow(490, 250, 490, 300, color=MUTED, sw=1.8))

    # Крок 3 — КТО → c
    P.append(text(60, 296, "Крок 3 — китайська теорема про остачі дає одне узгоджене число c", size=13, color=GREEN, anchor="start", bold=True))
    b, _, _ = textbox(490, 336, "c = 74826    (разом із d = 24 — уся трійка)", size=15, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=15)
    P.append(b)
    P.append(arrow(490, 366, 490, 412, color=MUTED, sw=1.8))

    # Крок 4 — витяг остачею
    P.append(text(60, 408, "Крок 4 — витягаємо кожен член:  β(c, d, i) = остача c за модулем mᵢ", size=13, color=GREEN, anchor="start", bold=True))
    recx = [270, 510, 750]
    rec = [("74826 mod 25", "= 1 = a₀"), ("74826 mod 49", "= 3 = a₁"), ("74826 mod 73", "= 1 = a₂")]
    for cx, (top, bot) in zip(recx, rec):
        P.append(rect(cx - 100, 424, 200, 58, fill=BG, stroke=GREEN, sw=1.7, rx=8))
        P.append(text(cx, 448, top, size=13, color=INK))
        P.append(text(cx, 470, bot, size=13.5, color=GREEN, bold=True))

    b, _, _ = textbox(W / 2, 548,
                      "Жодного піднесення до степеня — лише +, ·, остача. Тому «i-й член послідовності» —\n"
                      "арифметична формула навіть у слабкій системі; саме на цьому тримається представність.",
                      size=12.5, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=13)
    P.append(b)
    render("img/beta-crt.svg", W, H, *P)


# ── Фігура 7 (вставка math): діагональна лема — самопокликання без магії ────────
# θ(x) діагоналізує x і застосовує ψ; годуємо θ її власним кодом m=⌜θ⌝, і
# підстановка коду θ у саму θ будує рівно D, тож sub(m,m)=⌜D⌝ → F ⊢ D ⟺ ψ(⌜D⌝).
def fig_diagonal():
    W, H = 1020, 590
    P = [text(W / 2, 32, "Діагональна лема: як речення тримає власний код", size=16.5, bold=True),
         text(W / 2, 54, "самопокликання без зачарованого кола — той самий код ужито двічі", size=12, color=MUTED)]

    b, _, _ = textbox(500, 116, "θ(x)  :=  ∃r ( Sub(x, x, r) ∧ ψ(r) )", size=16, fill=LBLUE, stroke=NEG, color=INK, bold=True, pad=15)
    P.append(b)
    P.append(text(500, 158, "«візьми формулу з кодом x, підстав у неї її ж код x, і застосуй ψ до результату»", size=12, color=MUTED))

    P.append(arrow(500, 178, 500, 252, color=POS, sw=2))
    b, _, _ = textbox(792, 215, "годуємо θ\nїї власним кодом\nm = ⌜θ⌝", size=12, fill=LRED, stroke=RED, color=INK, bold=True, pad=12)
    P.append(b)

    b, _, _ = textbox(500, 288, "D  :=  θ(m̄)", size=17, fill=LGREY, stroke=INK, color=INK, bold=True, pad=14)
    P.append(b)
    b, _, _ = textbox(206, 288, "підстановка коду θ\nу саму θ будує\nрівно D", size=12, fill=FILL, stroke=MUTED, color=INK, pad=12)
    P.append(b)
    P.append(arrow(306, 288, 456, 288, color=MUTED, sw=1.7))

    P.append(arrow(500, 312, 500, 352, color=MUTED, sw=1.7))
    b, _, _ = textbox(500, 378, "тому  sub(m, m) = ⌜D⌝  — код результату і є код самого D", size=13, fill=BG, stroke=GREEN, color=INK, bold=True, pad=12)
    P.append(b)

    P.append(arrow(500, 402, 500, 444, color=MUTED, sw=1.7))
    b, _, _ = textbox(500, 480, "F ⊢   D   ⟺   ψ(⌜D⌝)", size=18, fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=16)
    P.append(b)
    P.append(text(500, 524, "D рівносильне (у самій F) твердженню «ψ справджується для мого власного коду»", size=12.5, color=INK, bold=True))
    P.append(text(500, 550, "підстав ψ = ¬Bew — і дістанеш G, що каже «мене не доводять»", size=12, color=MUTED))
    render("img/diagonal-lemma.svg", W, H, *P)


# ── Фігура (вставка proj): механіка квайна — рядок у двох ролях ───────────────
# Один рядок s іде двома дорогами: як КОД (шаблон виконується) і як ДАНІ (лапкована
# копія через %r). s % s зводить обидві дороги, і вивід дорівнює самій програмі.
def fig_quine_mechanism():
    W, H = 900, 560
    P = [text(W / 2, 34, "Механіка квайна: один рядок — дві ролі", size=17, bold=True),
         text(W / 2, 56, "чому копія не мусить містити саму себе", size=12, color=MUTED)]

    b, _, _ = textbox(W / 2, 100, "рядок  s   =   « s = %r \\n print(s % s) »",
                      size=13.5, fill=LGREY, stroke=INK, color=INK, bold=True, pad=14)
    P.append(b)
    P.append(text(W / 2, 139, "шаблон-дані: програма без власного значення", size=11.5, color=MUTED))

    lx, rx = 235, 665
    P.append(arrow(W / 2 - 40, 152, lx, 202, color=MUTED, sw=1.8))
    P.append(arrow(W / 2 + 40, 152, rx, 202, color=MUTED, sw=1.8))
    b, _, _ = textbox(lx, 252, "РОЛЬ 1 — КОД\n\nувесь текст шаблону\nвиконується як програма",
                      size=12, fill=LBLUE, stroke=NEG, color=INK, pad=14)
    P.append(b)
    b, _, _ = textbox(rx, 252, "РОЛЬ 2 — ДАНІ\n\n%r → repr(s):\ns у лапках, дослівно",
                      size=12, fill=LGREEN, stroke=GREEN, color=INK, pad=14)
    P.append(b)

    P.append(arrow(lx, 298, W / 2 - 34, 368, color=MUTED, sw=1.8))
    P.append(arrow(rx, 298, W / 2 + 34, 368, color=MUTED, sw=1.8))
    b, _, _ = textbox(W / 2, 392, "s % s", size=20, fill=BG, stroke=INK, color=INK, bold=True, pad=14)
    P.append(b)
    P.append(text(W / 2, 432, "діру %r затикаємо копією s — обидві ролі сходяться", size=11.5, color=MUTED))

    P.append(arrow(W / 2, 446, W / 2, 480, color=INK, sw=2))
    b, _, _ = textbox(W / 2, 504, "вивід  =  сама програма   (байт у байт)", size=14,
                      fill=LGREEN, stroke=GREEN, color=INK, bold=True, pad=14)
    P.append(b)
    render("img/quine-mechanism.svg", W, H, *P)


# ── Фігура (вставка proj): одна машина нерухомої точки — різні результати ──────
# Будівник бере властивість P і повертає X із X ⟺ P(⌜X⌝). Начинка «надрукуй» дає
# квайн, «не довести» — речення G, «не зупиниться» — проблему зупинки; «хибне»
# не збирається (немає предиката істинності — Тарський).
def fig_fixed_point_machine():
    W, H = 1000, 600
    P = [text(W / 2, 34, "Одна машина — різні знамениті результати", size=17, bold=True),
         text(W / 2, 56, "той самий прийом нерухомої точки, різна начинка P", size=12, color=MUTED)]

    b, _, _ = textbox(W / 2, 118, "Будівник нерухомої точки\nX   ⟺   P(⌜X⌝)",
                      size=14, fill=LGREY, stroke=INK, color=INK, bold=True, pad=14)
    P.append(b)
    P.append(arrow(W / 2, 156, W / 2, 196, color=INK, sw=2))

    px, cx0, rx = 300, 515, 730
    P.append(text(px, 214, "вкладаєш  P", size=11.5, color=MUTED, bold=True))
    P.append(text(cx0, 214, "будівник", size=11.5, color=MUTED))
    P.append(text(rx, 214, "дістаєш  X", size=11.5, color=MUTED, bold=True))

    rows = [
        (250, "P = «надрукуй цей текст»", "Квайн", LGREEN, GREEN),
        (330, "P = «X не доводиться у F»", "Речення G Ґеделя", LRED, RED),
        (410, "P = «X не зупиняється»", "Проблема зупинки", LBLUE, NEG),
        (492, "P = «X хибне»", "Брехун — не збирається", LGREY, AMBER),
    ]
    for cy, payload, result, rfill, rcol in rows:
        b, pw, _ = textbox(px, cy, payload, size=12, fill=BG, stroke=MUTED, color=INK, pad=12)
        P.append(b)
        b2, rw, _ = textbox(rx, cy, result, size=12.5, fill=rfill, stroke=rcol, color=INK, bold=True, pad=12)
        P.append(arrow(px + pw / 2 + 6, cy, rx - rw / 2 - 6, cy, color=MUTED, sw=1.7))
        P.append(b2)
    P.append(text(rx, 528, "(предиката «істинне» в арифметиці немає)", size=10.5, color=AMBER))

    P.append(text(W / 2, 572, "Речення G — це квайн із начинкою «мене не можна довести».",
                  size=12.5, color=INK, bold=True))
    render("img/fixed-point-machine.svg", W, H, *P)


if __name__ == "__main__":
    fig_hilbert_wishes()
    fig_godel_numbering()
    fig_godel_fork()
    fig_where_the_wall()
    fig_two_speeches()
    fig_beta_crt()
    fig_diagonal()
    fig_quine_mechanism()
    fig_fixed_point_machine()
    print("OK: hilbert-wishes.svg, godel-numbering.svg, godel-fork.svg, where-the-wall.svg, "
          "two-speeches.svg, beta-crt.svg, diagonal-lemma.svg, quine-mechanism.svg, fixed-point-machine.svg")
