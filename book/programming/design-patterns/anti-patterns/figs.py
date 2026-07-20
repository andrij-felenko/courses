# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Вартість наступної зміни: чистий код проти антипатерну ────────────────
def fig_cost_of_change():
    W, H = 860, 440
    frags = []
    frags.append(text(W/2, 30, "Антипатерн задирає вартість кожної наступної зміни", size=17, bold=True))

    # осі
    ax_x0, ax_x1 = 110, 660
    ax_y0, ax_y1 = 100, 360          # верх / низ області
    frags.append(line(ax_x0, ax_y0, ax_x0, ax_y1, color=INK, sw=1.6))   # вісь Y
    frags.append(line(ax_x0, ax_y1, ax_x1, ax_y1, color=INK, sw=1.6))   # вісь X
    frags.append(text(ax_x0 - 2, 84, "вартість наступної зміни ↑", size=12, color=MUTED, anchor="start"))
    frags.append(text(ax_x0 + 190, 392, "час · більше коду, більше кроків →", size=12, color=MUTED))

    # чистий код — низька майже пласка лінія
    frags.append(line(ax_x0, 335, ax_x1, 318, color=FIELD, sw=3))
    frags.append(text(ax_x1 + 8, 318, "чистий код", size=12.5, color=FIELD, anchor="start", bold=True))

    # антипатерн — сходинки, що лізуть угору
    steps = [(110, 335), (185, 335), (185, 300), (260, 300), (260, 262),
             (335, 262), (335, 220), (410, 220), (410, 176), (485, 176),
             (485, 132), (560, 132), (560, 112), (650, 112)]
    for i in range(len(steps) - 1):
        x1, y1 = steps[i]
        x2, y2 = steps[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=3))
    frags.append(text(ax_x1 + 8, 112, "антипатерн", size=12.5, color=POS, anchor="start", bold=True))

    # підписи у ВІЛЬНИХ кутах (верх-ліворуч і низ-праворуч), геть від ліній
    frags.append(text(122, 116, "обвідна круто здіймається", size=12, color=MUTED, anchor="start", italic=True))
    frags.append(text(648, 348, "кожен крок — «дешево зараз»", size=12, color=MUTED, anchor="end", italic=True))

    # прихований борг — зазор між кривими праворуч
    gx = 672
    frags.append(line(gx, 112, gx, 318, color=POS, sw=1.4, dash="4 4"))
    frags.append(mtext(gx + 8, 205, ["прихований", "борг"], size=12.5, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, 'cost-of-change.svg'), W, H, *frags)


# ── 2. Анатомія антипатерну: чотири смуги, четверта (вихід) — зелена ─────────
def fig_anatomy():
    W, H = 800, 452
    frags = []
    frags.append(text(W/2, 30, "Антипатерн — теж картка з чотирьох частин, але зі знаком мінус", size=16, bold=True))

    rows = [
        ("НАЗВА", "спільне слово, яким команда показує на біль",
         "«Божественний об'єкт»", MUTED, FILL),
        ("ОМАНЛИВИЙ ПСЕВДО-РОЗВ'ЯЗОК", "те зручне, за що хапаються",
         "«дописати сюди, тут же під рукою»", POS, "#fdecea"),
        ("СХОВАНА СПРАВЖНЯ ЦІНА", "що насправді дістаєш",
         "клас знає все — не змінити, не тестувати частинами", POS, "#fdecea"),
        ("РОЗВ'ЯЗОК-ВИХІД", "перевірений спосіб вибратися",
         "розбити за обов'язками, залежності подати ззовні", FIELD, "#eafaf0"),
    ]
    x = 56
    w = W - 112
    y = 62
    rh = 84
    gap = 12
    for title, desc, ex, col, bg in rows:
        frags.append(rect(x, y, w, rh, fill=bg, stroke=col, sw=2.4, rx=9))
        frags.append(text(x + 18, y + 27, title, size=13.5, color=col, anchor="start", bold=True))
        frags.append(text(x + 18, y + 50, desc, size=12.5, color=INK, anchor="start"))
        frags.append(text(x + w - 18, y + 70, ex, size=12, color=MUTED, anchor="end", italic=True))
        y += rh + gap

    render(os.path.join(OUT, 'antipattern-anatomy.svg'), W, H, *frags)


# ── 3. Розплітання божественного об'єкта: до → після ────────────────────────
def fig_god_refactor():
    W, H = 900, 470
    frags = []
    frags.append(text(W/2, 30, "Розплітання божественного об'єкта за обов'язками", size=17, bold=True))

    # ── ЛІВОРУЧ: ДО — один клас робить усе ──
    frags.append(text(210, 64, "ДО", size=14, color=POS, bold=True))
    lx, ly, lw, lh = 50, 82, 320, 250
    frags.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2.6, rx=10))
    frags.append(text(lx + lw/2, ly + 30, "OrderManager", size=15, color=POS, bold=True))
    frags.append(text(lx + lw/2, ly + 50, "один клас робить усе", size=12, color=MUTED, italic=True))
    jobs = ["перевірка кошика", "розрахунок ціни", "запис у базу", "лист покупцеві"]
    jy = ly + 84
    for j in jobs:
        frags.append(rect(lx + 40, jy, lw - 80, 28, fill=BG, stroke=POS, sw=1.2, rx=6))
        frags.append(text(lx + lw/2, jy + 19, j, size=12.5, color=INK))
        jy += 34
    frags.append(text(lx + lw/2, jy + 12, "+ податки, логи, формати…", size=11.5, color=MUTED, italic=True))
    frags.append(text(lx + lw/2, ly + lh + 26, "усе зрощене — не розчепити, не протестувати частинами",
                      size=11.5, color=POS, italic=True))

    # роздільник + місток
    frags.append(line(W/2, 78, W/2, 372, color=MUTED, sw=1.2, dash="5 5"))
    frags.append(text(W/2, 372 + 22, "розбити за обов'язками · залежності — ззовні",
                      size=12, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: ПІСЛЯ — диригент + чотири виконавці ──
    rcx = 682
    frags.append(text(rcx, 64, "ПІСЛЯ", size=14, color=FIELD, bold=True))
    ox, oy, ow, oh = rcx - 180, 82, 360, 52
    frags.append(rect(ox, oy, ow, oh, fill="#eafaf0", stroke=FIELD, sw=2.6, rx=10))
    frags.append(text(rcx, oy + 22, "OrderService", size=14, color=FIELD, bold=True))
    frags.append(text(rcx, oy + 40, "тільки диригує", size=11.5, color=MUTED, italic=True))

    boxes = [
        ("OrderValidator\nперевірка", rcx - 180, 178),
        ("Pricer\nціна",             rcx + 10,  178),
        ("OrderRepository\nзапис",   rcx - 180, 256),
        ("Notifier\nсповіщення",     rcx + 10,  256),
    ]
    bw, bh = 170, 60
    for label, bx, by in boxes:
        frags.append(fitbox(bx, by, bw, bh, label, size=12.5, pad=8,
                            fill=BG, stroke=FIELD, sw=1.7, rx=8, color=INK))
        # стрілка від диригента до виконавця
        frags.append(arrow(rcx, oy + oh, bx + bw/2, by, color=FIELD, sw=1.6))

    frags.append(text(rcx, 256 + bh + 26, "кожен — одна причина змінюватись",
                      size=11.5, color=FIELD, italic=True))

    render(os.path.join(OUT, 'god-object-refactor.svg'), W, H, *frags)


# ── 4. Хроніка: явище описали задовго до того, як дали ім'я ─────────────────
def fig_word_timeline():
    W, H = 960, 808
    frags = []
    frags.append(text(W / 2, 34, "Явище описали за двадцять років до того, як йому дали ім'я",
                      size=17, bold=True))

    spine_x = 206
    box_x = 224
    box_w = W - box_x - 30
    year_x = 186

    def phase(y, label, color):
        frags.append(text(40, y, label, size=12.5, color=color, anchor="start", bold=True))

    def spine(y0, y1):
        frags.append(line(spine_x, y0, spine_x, y1, color=MUTED, sw=1.6))

    def row(y, year, head, sub, color, bg):
        frags.append(rect(box_x, y - 26, box_w, 52, fill=bg, stroke=color, sw=1.8, rx=8))
        frags.append(text(year_x, y + 5, year, size=14, color=color, anchor="end", bold=True))
        frags.append(circle(spine_x, y, 5.5, fill=color, stroke=color, sw=1))
        frags.append(text(box_x + 16, y - 4, head, size=13, color=INK, anchor="start", bold=True))
        frags.append(text(box_x + 16, y + 16, sub, size=11.5, color=MUTED, anchor="start"))

    # ── доба перша: явище вже описане, слова ще нема ──
    phase(66, "ЯВИЩЕ ВЖЕ ОПИСАНЕ — СЛОВА ЩЕ НЕМА", MUTED)
    spine(88, 392)
    row(108, "1975", "Фред Брукс, «Міфічний людино-місяць»",
        "«додати людей до пізнього проєкту — і він стане ще пізнішим»: пастку названо, слова нема",
        MUTED, FILL)
    row(174, "1977", "Крістофер Александер, «A Pattern Language»",
        "патерн як форма повторюваного рішення — поки що про будівлі й міста, не про код",
        MUTED, FILL)
    row(240, "1987", "Кент Бек і Ворд Каннінгем, OOPSLA, Орландо",
        "патерни переносять з архітектури будівель в об'єктний код",
        MUTED, FILL)
    row(306, "1993", "Hillside Group, серпень, схил гори в Колорадо",
        "спільнота патернів дістає осідок; від 1994-го — щорічні PLoP в Аллертон-Парку",
        MUTED, FILL)
    row(372, "1994", "«Банда чотирьох», Design Patterns — 21 жовтня, OOPSLA",
        "23 патерни, вибрані з систем, які вижили. Канон, від якого відштовхнеться Кеніг",
        MUTED, FILL)

    # ── доба друга: слово ──
    phase(424, "СЛОВО З'ЯВЛЯЄТЬСЯ — І ТУТ-ТАКИ МІСЦЕ, ДЕ ПРО НЬОГО СПЕРЕЧАТИСЯ", POS)
    spine(444, 552)
    row(466, "1995", "Ендрю Кеніг, JOOP 8(1), с. 46–48: «Patterns and Antipatterns»",
        "березень–квітень: слово народжується. Оригіналу статті в мережі й досі нема",
        POS, "#fdecea")
    row(532, "1995", "Ворд Каннінгем вмикає першу в світі вікі — 25 березня",
        "той самий місяць: у спільноти з'являється місце, де сперечатися вголос",
        POS, "#fdecea")

    # ── доба третя: каталог ──
    phase(584, "ПОНЯТТЯ ЗБИРАЮТЬ У КАТАЛОГ", FIELD)
    spine(604, 778)
    row(626, "1996", "Майкл Акройд, Object World West",
        "«AntiPatterns: щеплення проти зловживання об'єктами» — поняття виходить на сцену",
        FIELD, "#eafaf0")
    row(692, "1997", "Браян Фут і Джозеф Йодер, «Велика грудка багна», PLoP",
        "відмовляються від ярлика «анти»: надто популярне, щоб бути просто хибним",
        FIELD, "#eafaf0")
    row(758, "1998", "Браун, Мальво, Маккормік, Моубрей — каталог у Wiley",
        "40 антипатернів, три погляди, обов'язковий «розв'язок-вихід» у кожного",
        FIELD, "#eafaf0")

    render(os.path.join(OUT, 'antipattern-timeline.svg'), W, H, *frags)


# ── 5. Чому каталогові успіхів бракувало контрольної групи ──────────────────
def fig_control_group():
    W, H = 900, 536
    frags = []
    frags.append(text(W / 2, 32, "Каталог самих лише успіхів нічого не доводить", size=17, bold=True))
    frags.append(text(W / 2, 56, "щоб перевірити правило «цей хід допомагає», потрібні всі чотири клітинки",
                      size=12.5, color=MUTED, italic=True))

    c1x, c2x, cw = 250, 574, 312
    r1y, r2y, ch = 118, 290, 160
    c1cx, c2cx = c1x + cw / 2, c2x + cw / 2

    frags.append(text(c1cx, 100, "Система вдалася", size=14, color=INK, bold=True))
    frags.append(text(c2cx, 100, "Система лягла", size=14, color=INK, bold=True))
    frags.append(text(238, r1y + ch / 2 + 5, "Хід ПРИСУТНІЙ", size=14, color=INK, anchor="end", bold=True))
    frags.append(text(238, r2y + ch / 2 + 5, "Ходу НЕМАЄ", size=14, color=INK, anchor="end", bold=True))

    def cell(x, y, verdict, lines, color, bg):
        frags.append(rect(x, y, cw, ch, fill=bg, stroke=color, sw=2.2, rx=9))
        frags.append(text(x + cw / 2, y + 36, verdict, size=13.5, color=color, bold=True))
        frags.append(mtext(x + cw / 2, y + 76, lines, size=12.5, color=INK))

    cell(c1x, r1y, "СВІДЧИТЬ ЗА",
         ["Саме це зібрали 1994-го:", "23 патерни, вибрані", "з тих, хто вижив"], FIELD, "#eafaf0")
    cell(c2x, r1y, "СВІДЧИТЬ ПРОТИ",
         ["Хід був — і система лягла.", "Отже, сам собою", "він не рятує"], POS, "#fdecea")
    cell(c1x, r2y, "СВІДЧИТЬ ПРОТИ",
         ["Без нього теж вдавалося.", "Отже, він не був", "потрібен"], POS, "#fdecea")
    cell(c2x, r2y, "СВІДЧИТЬ ЗА",
         ["Ходу не було — і система", "лягла. Правило", "тримається"], FIELD, "#eafaf0")

    frags.append(text(W / 2, 486, "1994-й заповнив ОДНУ клітинку з чотирьох — ліву верхню.",
                      size=13, color=MUTED, italic=True))
    frags.append(text(W / 2, 510, "Решта три — і є та контрольна група, по яку пішли антипатерни.",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'control-group.svg'), W, H, *frags)


# ── 6. Стрибок чи сходинки: різниця в тому, де можна спинитись ──────────────
def fig_steps_vs_bigbang():
    W, H = 960, 410
    frags = []
    frags.append(text(W / 2, 30, "Один стрибок чи вісім кроків — різниця в тому, де ти можеш спинитись",
                      size=17, bold=True))

    # ── МАРШРУТ 1: великий стрибок ──
    frags.append(text(35, 68, "МАРШРУТ 1", size=12, color=POS, anchor="start", bold=True))
    frags.append(fitbox(35, 82, 100, 56, "ДО\nOrderManager", size=11.5, pad=6,
                        fill="#fdecea", stroke=POS, sw=2.2, color=POS))
    frags.append(line(145, 110, 762, 110, color=POS, sw=2.2, dash="8 5"))
    frags.append(arrow(762, 110, 788, 110, color=POS, sw=2.2))
    frags.append(text(455, 100, "переписати все за два тижні", size=12.5, color=POS, italic=True))
    frags.append(text(455, 134,
                      "жодного зеленого прогону · змерджити не можна · впало — винне будь-що з 900 рядків",
                      size=11.5, color=MUTED, italic=True))
    frags.append(fitbox(798, 82, 122, 56, "ПІСЛЯ?", size=14, pad=6,
                        fill="#fdecea", stroke=POS, sw=2.2, color=POS, bold=True))

    # ── МАРШРУТ 2: вісім кроків ──
    frags.append(text(35, 196, "МАРШРУТ 2", size=12, color=FIELD, anchor="start", bold=True))
    frags.append(fitbox(35, 240, 100, 56, "ДО\nOrderManager", size=11.5, pad=6,
                        fill="#fdecea", stroke=POS, sw=2.2, color=POS))
    # з'єднувачі — лише в проміжках між коробками, повз написи
    frags.append(arrow(137, 268, 149, 268, color=FIELD, sw=1.6))
    frags.append(arrow(804, 268, 814, 268, color=FIELD, sw=1.6))

    steps = ["0\nшов", "1\nтест", "2\nмежі", "3\nPricer",
             "4\nValidator", "5\nRepo", "6\nNotifier", "7\nкорінь"]
    for i, s in enumerate(steps):
        bx = 150 + i * 82
        frags.append(fitbox(bx, 240, 78, 56, s, size=11, pad=6,
                            fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK))
        frags.append(text(bx + 39, 318, "✓", size=14, color=FIELD, bold=True))

    frags.append(fitbox(815, 240, 110, 56, "ПІСЛЯ", size=14, pad=6,
                        fill="#eafaf0", stroke=FIELD, sw=2.4, color=FIELD, bold=True))
    frags.append(text(470, 352, "кожен крок: тести зелені · комміт мерджиться · можна спинитись будь-де",
                      size=12, color=FIELD, italic=True))
    frags.append(text(470, 376, "поведінка не рушила ані на йоту — тест із кроку 1 весь час той самий",
                      size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'steps-vs-bigbang.svg'), W, H, *frags)


# ── 7. Шов: місце, де підміняють поведінку, не чіпаючи код у цьому місці ────
def fig_seam():
    W, H = 940, 410
    frags = []
    frags.append(text(W / 2, 30, "Шов — місце, де можна підмінити поведінку, не редагуючи код у цьому місці",
                      size=16, bold=True))
    frags.append(line(470, 66, 470, 384, color=MUTED, sw=1.2, dash="5 5"))

    # ── ЛІВОРУЧ: шва немає — залежність приварена ──
    frags.append(text(235, 92, "БЕЗ ШВА", size=13, color=POS, bold=True))
    frags.append(fitbox(115, 108, 240, 46, "place_order()", size=13, pad=8,
                        fill=FILL, stroke=INK, sw=1.8))
    frags.append(line(235, 154, 235, 212, color=POS, sw=4.5))
    frags.append(text(247, 188, "приварено", size=11, color=POS, anchor="start", italic=True))
    frags.append(fitbox(100, 212, 270, 46, "smtplib.SMTP('mail.local')", size=11.5, pad=8,
                        fill="#fdecea", stroke=POS, sw=2))
    frags.append(arrow(235, 258, 235, 292, color=POS, sw=1.8))
    frags.append(fitbox(150, 292, 170, 40, "справжня пошта", size=12, pad=8,
                        fill=BG, stroke=POS, sw=1.5))
    frags.append(text(235, 356, "щоб підмінити пошту — треба редагувати", size=11.5, color=MUTED, italic=True))
    frags.append(text(235, 374, "place_order, а це і є той код, який", size=11.5, color=MUTED, italic=True))
    frags.append(text(235, 392, "без тестів чіпати страшно", size=11.5, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: шов прорізано — з'явилася точка вибору ──
    frags.append(text(700, 92, "ЗІ ШВОМ", size=13, color=FIELD, bold=True))
    frags.append(fitbox(580, 108, 240, 46, "place_order()", size=13, pad=8,
                        fill=FILL, stroke=INK, sw=1.8))
    frags.append(text(828, 126, "не змінився", size=10.5, color=FIELD, anchor="start", italic=True))
    frags.append(text(828, 142, "ані на рядок", size=10.5, color=FIELD, anchor="start", italic=True))
    frags.append(line(700, 154, 700, 194, color=INK, sw=1.8))
    frags.append(fitbox(600, 194, 200, 42, "self._open_smtp()", size=12, pad=8,
                        fill="#eafaf0", stroke=FIELD, sw=2.6))
    frags.append(text(812, 219, "← ШОВ", size=11.5, color=FIELD, anchor="start", bold=True))
    frags.append(line(675, 236, 615, 288, color=FIELD, sw=1.6, dash="5 4"))
    frags.append(line(725, 236, 785, 288, color=FIELD, sw=1.6, dash="5 4"))
    frags.append(fitbox(528, 288, 165, 44, "справжній SMTP\n(прод)", size=11, pad=6,
                        fill=BG, stroke=MUTED, sw=1.5))
    frags.append(fitbox(707, 288, 165, 44, "FakeSmtp\n(тест)", size=11, pad=6,
                        fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(700, 356, "точка вибору: у тесті — підклас,", size=11.5, color=MUTED, italic=True))
    frags.append(text(700, 374, "що підміняє лише цей метод", size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'seam.svg'), W, H, *frags)


# ── 8. Приз: тести, яких учора не існувало ──────────────────────────────────
def fig_tests_before_after():
    W, H = 940, 440
    frags = []
    frags.append(text(W / 2, 30, "Приз: тести, яких учора не існувало", size=17, bold=True))
    frags.append(line(470, 60, 470, 420, color=MUTED, sw=1.2, dash="5 5"))

    # ── БУЛО: одна брила, жодного тесту ──
    frags.append(text(235, 78, "БУЛО", size=14, color=POS, bold=True))
    frags.append(rect(105, 92, 260, 186, fill="#fdecea", stroke=POS, sw=2.6, rx=10))
    frags.append(text(235, 120, "OrderManager", size=15, color=POS, bold=True))
    frags.append(text(235, 140, "place_order()", size=11.5, color=MUTED, italic=True))
    frags.append(rect(140, 156, 190, 92, fill=BG, stroke=POS, sw=1.2, rx=6))
    for i, j in enumerate(["перевірка", "ціна", "запис у базу", "лист"]):
        frags.append(text(235, 178 + i * 21, j, size=12, color=INK))
    frags.append(text(235, 268, "чотири роботи зрощено в одному методі", size=10.5, color=POS, italic=True))
    frags.append(text(235, 336, "0", size=32, color=POS, bold=True))
    frags.append(text(235, 358, "юніт-тестів", size=12.5, color=POS, bold=True))
    frags.append(text(235, 382, "щоб перевірити знижку, потрібні жива", size=11, color=MUTED, italic=True))
    frags.append(text(235, 398, "база й поштовий сервер — тому", size=11, color=MUTED, italic=True))
    frags.append(text(235, 414, "не перевіряє ніхто", size=11, color=MUTED, italic=True))

    # ── СТАЛО: чотири виконавці, кожен зі своїм тестом ──
    frags.append(text(700, 78, "СТАЛО", size=14, color=FIELD, bold=True))
    frags.append('<rect x="538" y="92" width="330" height="186" rx="12" fill="none" '
                 'stroke="%s" stroke-width="1.6" stroke-dasharray="6 5"/>' % MUTED)
    units = [("Pricer", "2 тести"), ("OrderValidator", "3 тести"),
             ("OrderRepository", "1 тест"), ("EmailNotifier", "1 тест")]
    for i, (n, t) in enumerate(units):
        bx = 550 + (i % 2) * 156
        by = 106 + (i // 2) * 58
        frags.append(fitbox(bx, by, 146, 48, "%s\n%s" % (n, t), size=10.5, pad=5,
                            fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK))
    frags.append(fitbox(550, 222, 302, 44, "OrderService · 1 тест на фейках", size=11.5, pad=6,
                        fill=BG, stroke=FIELD, sw=1.8, color=INK))
    frags.append(text(703, 294, "наскрізний тест із кроку 1 — досі стереже все разом",
                      size=10.5, color=MUTED, italic=True))
    frags.append(text(700, 336, "9", size=32, color=FIELD, bold=True))
    frags.append(text(700, 358, "юніт-тестів", size=12.5, color=FIELD, bold=True))
    frags.append(text(700, 382, "0.15 мс · без бази · без пошти", size=11, color=MUTED, italic=True))
    frags.append(text(700, 398, "знижку тепер видно в один рядок", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'tests-before-after.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_cost_of_change()
    fig_anatomy()
    fig_god_refactor()
    fig_word_timeline()
    fig_control_group()
    fig_steps_vs_bigbang()
    fig_seam()
    fig_tests_before_after()
    print("figures written to", OUT)
