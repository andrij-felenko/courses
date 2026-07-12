# -*- coding: utf-8 -*-
"""Фігури до кроку «Парадигми як інструменти» (модуль «Моделі конкурентності»).
Три фігури:
  (1) shape-to-tool      — форма межі ліворуч → інструмент, чия сила під неї, праворуч;
  (2) dh-concurrency-map — DH як мапа меж: чотири парадигми, зшиті підписаними швами;
  (3) read-the-boundary  — чотири питання читають форму межі, форма називає інструмент."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"


# ── Фігура 1: форма межі → інструмент під неї ────────────────────────────────
def fig_shape_to_tool():
    W, H = 1120, 648
    frags = []
    frags.append(text(W / 2, 56, "Ліворуч — форма межі. Праворуч — інструмент, чия сила під цю форму.",
                      size=14, color=MUTED))

    rows = [
        ("спільний змінний стан у процесі,\nсуперечок мало",              "Замки ·\nспільна пам'ять"),
        ("гарячий шлях, один писар,\nсуперечка коштує дорого",            "Без замків\n(Disruptor)"),
        ("багато сутностей зі станом,\nтреба ізоляція збою",              "Актори ·\nскриньки"),
        ("стадії передають роботу,\nнічого не ділять",                    "Канали · CSP"),
        ("тисячі очікувань вводу-виводу,\nCPU на кожне — копійки",        "Цикл подій ·\nasync"),
        ("CPU-робота, ділиться за ключем,\nбез крос-ядерної синхронізації","Пул /\nпотік-на-ядро"),
    ]
    y0, pitch, ch = 82, 88, 66
    lx, lw = 40, 560
    rx, rw = 760, 320
    for i, (shape, tool) in enumerate(rows):
        yt = y0 + i * pitch
        mid = yt + ch / 2
        frags.append(fitbox(lx, yt, lw, ch, shape, size=13, fill=FILL, stroke=INK))
        frags.append(arrow(lx + lw + 6, mid, rx - 4, mid, color=INK, sw=2.0))
        frags.append(fitbox(rx, yt, rw, ch, tool, size=13, bold=True, fill=BLUE_FILL, stroke=NEG))

    frags.append(text(W / 2, 626,
                      "Вибирай не модель, а форму: прочитав форму межі — і вона сама назвала інструмент.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'shape-to-tool.svg'), W, H, *frags,
           title="Кожен інструмент — під свою форму координації")


# ── Фігура 2: мапа меж DH — чотири парадигми, зшиті швами ─────────────────────
def fig_dh_map():
    W, H = 1130, 592
    frags = []

    # вузли
    frags.append(fitbox(40, 250, 220, 120, "Пристрої\n(сотні)", size=14, fill=FILL, stroke=INK))
    frags.append(fitbox(300, 250, 280, 120,
                        "Ядро · цикл подій\nввід-вивід усіх\nпристроїв",
                        size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2.0))
    frags.append(fitbox(780, 70, 300, 110,
                        "Актор на пристрій\nскринька + ізольований\nстан (FSM)",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.0))
    frags.append(fitbox(780, 250, 300, 100,
                        "Пул воркерів\nаналітика — CPU",
                        size=13, bold=True, fill=FILL, stroke=INK, sw=2.0))
    frags.append(fitbox(780, 430, 300, 100,
                        "Правила\nй дії",
                        size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.8))

    # ребра пристрій → ядро
    frags.append(arrow(262, 310, 298, 310, color=INK, sw=2.0))

    # ядро → актор (шов: поштова скринька) — лінія розірвана на два відрізки,
    # щоб напис сидів У ПРОГАЛИНІ, а не під лінією
    frags.append(line(580, 300, 644.7, 247.1, color=FIELD, sw=2.0))
    frags.append(arrow(713.3, 190.9, 778, 138, color=FIELD, sw=2.0))
    frags.append(fitbox(600, 196, 156, 46, "поштова\nскринька", size=12, fill=BG, stroke=FIELD))

    # ядро → пул (шов: обмежена черга = зворотний тиск) — теж із прогалиною
    frags.append(line(580, 312, 627, 309.15, color=INK, sw=2.0))
    frags.append(arrow(727, 303.1, 778, 300, color=INK, sw=2.0))
    frags.append(fitbox(586, 284, 182, 48, "черга 256 ·\nзворотний тиск", size=12, fill=BG, stroke=INK))

    # пул → правила (шов: канал) — теж із прогалиною
    frags.append(line(930, 352, 930, 376.56, color=INK, sw=2.0))
    frags.append(arrow(930, 403.13, 930, 428, color=INK, sw=2.0))
    frags.append(fitbox(876, 368, 108, 42, "канал", size=12, fill=BG, stroke=INK))

    frags.append(text(W / 2, 572,
                      "Чотири моделі в одній системі, кожна на межі своєї форми; "
                      "дії від «Правил» вертаються на пристрої. Підписані шви — теж предмет проєктування.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'dh-concurrency-map.svg'), W, H, *frags,
           title="Система — мапа меж, а не одна модель")


# ── Фігура 3: чотири питання читають форму межі ──────────────────────────────
def fig_read_boundary():
    W, H = 1160, 384
    frags = []
    frags.append(text(W / 2, 54, "Став ці питання на КОЖНОМУ шві окремо — форма назве інструмент.",
                      size=14, color=MUTED))

    qs = [
        "1 · Що тут СПІЛЬНЕ?\nзмінний стан\n↔ не ділимо нічого",
        "2 · Де ВУЗЬКЕ місце?\nочікування В/В\n↔ робота CPU",
        "3 · Ділиться за\nКЛЮЧЕМ?\nтак → shared-nothing",
        "4 · Яка ІЗОЛЯЦІЯ\nЗБОЮ?\nролить сусідів?",
    ]
    xs = [40, 322, 604, 886]
    qw, qy, qh = 262, 78, 104
    for x, q in zip(xs, qs):
        frags.append(fitbox(x, qy, qw, qh, q, size=13, fill=FILL, stroke=INK))

    # збіжні лінії до вузла «форма межі»
    node_cx, node_top = 580, 228
    for x in xs:
        frags.append(line(x + qw / 2, qy + qh, node_cx, node_top, color=MUTED, sw=1.4))
    frags.append(fitbox(480, 228, 200, 44, "ФОРМА МЕЖІ", size=13, bold=True, fill=BLUE_FILL, stroke=NEG))
    frags.append(arrow(node_cx, 272, node_cx, 298, color=INK, sw=2.0))
    frags.append(fitbox(215, 300, 730, 52,
                        "форма визначає інструмент · кілька меж → кілька інструментів, зшитих швами",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))

    frags.append(text(W / 2, 376,
                      "Не «яка модель найкраща», а «яка тут форма» — на кожній межі своя.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'read-the-boundary.svg'), W, H, *frags,
           title="Читай форму межі, не сповідуй модель")


# ── Фігура 4 (вставка hist): часова смуга воєн парадигм ──────────────────────
def fig_paradigm_timeline():
    W, H = 1200, 600
    frags = []
    frags.append(text(W / 2, 52,
                      "Пів століття полювання на «єдину правильну» модель — і як воно скінчилося шухлядою",
                      size=14, color=MUTED))

    # легенда трьох таборів
    legend = [
        (RED_FILL,   POS,   "спільна пам'ять · потоки, замки"),
        (GREEN_FILL, FIELD, "повідомлення · актори, CSP"),
        (BLUE_FILL,  NEG,   "події · цикл подій"),
    ]
    lx = 210
    for fill, stroke, lab in legend:
        frags.append(rect(lx, 74, 16, 16, fill=fill, stroke=stroke, sw=1.6, rx=3))
        frags.append(text(lx + 24, 87, lab, size=12, color=INK, anchor="start"))
        lx += 24 + text_width(lab, 12) + 46

    ty = 332
    frags.append(arrow(46, ty, 1156, ty, color=MUTED, sw=1.6))
    frags.append(text(1150, ty - 12, "час →", size=12, color=MUTED, anchor="end"))

    # (рік, назва, хто, заливка, обведення)
    ev = [
        ("1965", "Семафори",            "Дейкстра",             RED_FILL,   POS),
        ("1973", "Актори",              "Г'юїтт та ін.",        GREEN_FILL, FIELD),
        ("1974", "Монітори",            "Гоар, Брінч Гансен",   RED_FILL,   POS),
        ("1978", "CSP",                 "Тоні Гоар",            GREEN_FILL, FIELD),
        ("1986", "Erlang",              "Армстронг та ін.",     GREEN_FILL, FIELD),
        ("1995", "Реактор",             "Дуглас Шмідт",         BLUE_FILL,  NEG),
        ("1996", "«Потоки —\nпогана ідея»", "Остергаут",       BLUE_FILL,  NEG),
        ("1999", "C10k",                "Ден Кіґел",            BLUE_FILL,  NEG),
        ("2003", "«Події —\nпогана ідея»", "фон Берен та ін.", RED_FILL,   POS),
        ("2009", "node.js · Go",        "події і CSP разом",    FILL,       INK),
    ]
    n = len(ev)
    bw, bh = 158, 88
    for i, (yr, name, who, fill, stroke) in enumerate(ev):
        x = 90 + i * (1020.0 / (n - 1))
        top = (i % 2 == 0)
        label = name + "\n" + who
        if top:
            by = ty - 18 - bh
            frags.append(line(x, by + bh, x, ty, color=stroke, sw=1.5))
            frags.append(text(x, by - 8, yr, size=15, bold=True, color=stroke))
        else:
            by = ty + 18
            frags.append(line(x, ty, x, by, color=stroke, sw=1.5))
            frags.append(text(x, by + bh + 20, yr, size=15, bold=True, color=stroke))
        frags.append(fitbox(x - bw / 2, by, bw, bh, label, size=12,
                            fill=fill, stroke=stroke, sw=1.6))
        frags.append(circle(x, ty, 5, fill=BG, stroke=stroke, sw=2.2))

    frags.append(text(W / 2, 590,
                      "Порядок подій, не в масштабі років. Жодна дата не «перемогла»: усі шість інструментів досі в ужитку.",
                      size=12, color=INK))
    render(os.path.join(IMG, 'paradigm-timeline.svg'), W, H, *frags,
           title="Війни парадигм конкурентності: хронологія")


# ── Фігура 5 (вставка hist): дві річки повідомлень і їхні нащадки ─────────────
def fig_message_genealogy():
    W, H = 1080, 556
    frags = []

    # спільний інстинкт — корінь
    frags.append(fitbox(350, 58, 380, 58, "«Не ділити нічого —\nпередавати повідомлення»",
                        size=15, bold=True, fill=BG, stroke=INK, sw=2.0))
    # від чого тікали
    frags.append(fitbox(25, 58, 210, 84,
                        "тікаючи від\nспільної пам'яті:\nперегони, дедлоки",
                        size=12, fill=FILL, stroke=MUTED, color=MUTED))
    frags.append(arrow(240, 92, 346, 88, color=MUTED, sw=1.5))

    # ліва річка — актори (зелена)
    frags.append(fitbox(145, 150, 220, 80,
                        "Актори\nГ'юїтт · Бішоп · Стайґер\n1973 · скриньки, асинхронно",
                        size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.0))
    frags.append(fitbox(145, 278, 220, 80,
                        "Erlang\nАрмстронг та ін., 1986\nдо акторів — незалежно",
                        size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(fitbox(145, 406, 220, 72,
                        "Elixir\nЖозе Валім, 2011\nна тій самій BEAM",
                        size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    # права річка — CSP (синя)
    frags.append(fitbox(715, 150, 220, 80,
                        "CSP\nТоні Гоар, 1978\nрандеву, названі канали",
                        size=12, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2.0))
    frags.append(fitbox(715, 278, 220, 80,
                        "occam\nMay / Inmos, 1983\nтрансп'ютери: ! і ?",
                        size=12, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    frags.append(fitbox(715, 406, 220, 72,
                        "Go-канали\nПайк та ін., 2009\nоператор <-",
                        size=12, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    # ребра
    frags.append(arrow(455, 116, 300, 146, color=INK, sw=1.8))
    frags.append(arrow(625, 116, 780, 146, color=INK, sw=1.8))
    frags.append(arrow(255, 230, 255, 274, color=FIELD, sw=1.8))
    frags.append(arrow(255, 358, 255, 402, color=FIELD, sw=1.8))
    frags.append(arrow(825, 230, 825, 274, color=NEG, sw=1.8))
    frags.append(arrow(825, 358, 825, 402, color=NEG, sw=1.8))

    frags.append(text(W / 2, 524,
                      "Дві річки повідомлень від того самого інстинкту. Актори й CSP дійшли до нього різними шляхами — обидві досі живі.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'message-passing-genealogy.svg'), W, H, *frags,
           title="Дві лінії передавання повідомлень і їхні живі нащадки")


# ── Фігура 6 (вставка proj): анатомія шва — дві ручки ────────────────────────
def fig_seam_anatomy():
    W, H = 1120, 548
    frags = []
    frags.append(text(W / 2, 52,
                      "Між двома парадигмами — не порожнеча, а об'єкт із двома ручками.",
                      size=14, color=MUTED))

    # парадигми по боках
    frags.append(fitbox(40, 252, 200, 96, "Парадигма А\n(продюсер)\nнапр. цикл подій",
                        size=13, fill=FILL, stroke=INK))
    frags.append(fitbox(880, 252, 200, 96, "Парадигма Б\n(споживач)\nнапр. пул воркерів",
                        size=13, fill=FILL, stroke=INK))

    # велика рамка шва
    frags.append(rect(320, 92, 480, 390, fill=BG, stroke=NEG, sw=2.4))
    frags.append(text(560, 124, "ШОВ = ⟨ місткість, політика ⟩", size=17, bold=True, color=NEG))

    # ── ручка 1: місткість (числова вісь) ──
    frags.append(text(560, 160, "МІСТКІСТЬ — скільки шов терпить", size=13, color=MUTED))
    frags.append(line(360, 200, 760, 200, color=INK, sw=2.0))
    for x, lab, col in [(360, "0\nкрихко", POS), (560, "N\nв самий раз", FIELD), (760, "∞\nOOM", POS)]:
        frags.append(line(x, 191, x, 209, color=col, sw=2.4))
        frags.append(mtext(x, 228, lab, size=12, color=col, bold=(col == FIELD)))

    # ── ручка 2: політика переповнення (чипси) ──
    frags.append(text(560, 302, "ПОЛІТИКА — що робити, коли повно", size=13, color=MUTED))
    chips = [
        ("блокувати\nтиск угору", GREEN_FILL, FIELD),
        ("викинути\nнайстаріший", BLUE_FILL, NEG),
        ("викинути\nнайновіший", BLUE_FILL, NEG),
        ("впасти\nголосно", RED_FILL, POS),
    ]
    cx0, cw, gap = 340, 104, 8
    for i, (lab, fill, stroke) in enumerate(chips):
        frags.append(fitbox(cx0 + i * (cw + gap), 318, cw, 54, lab, size=12, fill=fill, stroke=stroke))
    frags.append(text(560, 400, "конфляція = «викинути найстаріший» аж до місткості 1: у скриньці лише найсвіжіше",
                      size=11, color=MUTED, italic=True))

    # ребра: кладе / бере / зворотний тиск
    frags.append(arrow(240, 304, 316, 304, color=INK, sw=2.0))
    frags.append(text(278, 296, "кладе", size=11, color=INK))
    frags.append(arrow(804, 304, 878, 304, color=INK, sw=2.0))
    frags.append(text(841, 296, "бере", size=11, color=INK))
    frags.append(arrow(316, 264, 240, 264, color=POS, sw=2.0))
    frags.append(text(278, 256, "тиск угору", size=11, color=POS))

    frags.append(text(W / 2, 524,
                      "Дві ручки — місткість і політика — і роблять шов предметом проєктування, окремим від того, що по боках.",
                      size=13, color=INK))
    render(os.path.join(IMG, 'seam-anatomy.svg'), W, H, *frags,
           title="Шов — окремий об'єкт: місткість і політика переповнення")


# ── Фігура 7 (вставка proj): чотири шви DH, кожен зі своїм ⟨місткість, політика⟩ ─
def fig_four_seams():
    W, H = 1180, 436
    frags = []
    frags.append(text(W / 2, 52,
                      "Чотири шви DH — і кожну пару ⟨місткість, політика⟩ диктує СЕНС даних на шві.",
                      size=14, color=MUTED))

    cols = [(40, 210, "Шов"), (254, 150, "Місткість"),
            (408, 250, "Політика переповнення"), (662, 478, "Чому саме так — сенс даних")]
    hy, hh = 70, 44
    for x, w, lab in cols:
        frags.append(fitbox(x, hy, w, hh, lab, size=13, bold=True, fill=BLUE_FILL, stroke=NEG))

    rows = [
        ("Скринька\nактора (на пристрій)", "64 → 1",
         ("конфляція:\nтримай найсвіжіший", GREEN_FILL, FIELD),
         "для СТАНУ пристрою важить лише ОСТАННЄ показання;\nчерга застарілих — сміття, не борг"),
        ("Черга →\nпул (аналітика CPU)", "256",
         ("блокувати:\nтиск до джерела", GREEN_FILL, FIELD),
         "КОЖЕН кадр треба порахувати; втратити не можна,\nа джерело здатне пригальмувати"),
        ("Канал\nпул → правила", "64",
         ("блокувати\n(малий буфер)", GREEN_FILL, FIELD),
         "розв'язати ривки пулу й стадії правил,\nне загубивши жодного вироку"),
        ("Offload циклу\n(сам факт шва)", "> 0",
         ("винести CPU\nу пул", BLUE_FILL, NEG),
         "шов мусить БУТИ: місткість 0 = синхронний рахунок\nу смузі морозить увесь прийом"),
    ]
    ry, rh = 118, 72
    for r, (seam, cap, (pol, pf, ps), why) in enumerate(rows):
        y = ry + r * (rh + 4)
        frags.append(fitbox(cols[0][0], y, cols[0][1], rh, seam, size=12, fill=FILL, stroke=INK))
        frags.append(fitbox(cols[1][0], y, cols[1][1], rh, cap, size=15, bold=True, fill=BG, stroke=MUTED))
        frags.append(fitbox(cols[2][0], y, cols[2][1], rh, pol, size=12, bold=True, fill=pf, stroke=ps))
        frags.append(fitbox(cols[3][0], y, cols[3][1], rh, why, size=12, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'four-seams.svg'), W, H, *frags,
           title="Той самий механізм, протилежна політика — бо різний сенс даних")


if __name__ == "__main__":
    fig_shape_to_tool()
    fig_dh_map()
    fig_read_boundary()
    fig_paradigm_timeline()
    fig_message_genealogy()
    fig_seam_anatomy()
    fig_four_seams()
    print("ok:", os.listdir(IMG))
