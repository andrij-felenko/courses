# -*- coding: utf-8 -*-
"""Фігури теми «Політики витіснення кешу: LRU, LFU, CLOCK». Вивід — ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F = "#fdecea"


# ── trace: одна послідовність — три політики ─────────────────────────────────
# Ідея: на тій самій стрічці звернень і тому самому розмірі кеша різні правила
# вибору жертви дають різну кількість промахів, а ідеал (знання майбутнього)
# задає стелю, до якої всі решта тягнуться.
def fig_trace():
    W, H = 1060, 330
    f = []

    seq = ["A", "B", "C", "A", "B", "D", "A", "B", "C", "D"]
    # (влучання?, кого витіснено)
    fifo = [(0, ""), (0, ""), (0, ""), (1, ""), (1, ""), (0, "A"), (0, "B"), (0, "C"), (0, "D"), (0, "A")]
    lru = [(0, ""), (0, ""), (0, ""), (1, ""), (1, ""), (0, "C"), (1, ""), (1, ""), (0, "D"), (0, "A")]
    opt = [(0, ""), (0, ""), (0, ""), (1, ""), (1, ""), (0, "C"), (1, ""), (1, ""), (0, "A"), (1, "")]

    x0, step, cw, ch = 150, 76, 68, 54

    # шапка: сама послідовність звернень
    f.append(text(80, 76, "звернення:", size=13, color=MUTED, anchor="end"))
    for i, k in enumerate(seq):
        f.append(text(x0 + i * step + cw / 2, 76, k, size=15, bold=True))

    rows = [("FIFO", fifo, "8 промахів"), ("LRU", lru, "6 промахів"), ("OPT", opt, "5 промахів")]
    for r, (name, data, total) in enumerate(rows):
        cy = 125 + r * 66
        b, _, _ = textbox(80, cy, name, size=13, bold=True, min_w=110, pad=10)
        f.append(b)
        for i, (hit, ev) in enumerate(data):
            x = x0 + i * step
            label = "✓" if hit else ("✗\n−" + ev if ev else "✗")
            f.append(fitbox(x, cy - ch / 2, cw, ch, label, size=15,
                            fill=GREEN_F if hit else RED_F,
                            stroke=FIELD if hit else POS,
                            color=FIELD if hit else POS, bold=True))
        f.append(text(x0 + 10 * step + 14, cy + 5, total, size=13, bold=True, anchor="start"))

    f.append(text(W / 2, 316, "✓ — влучання · ✗ — промах · −X — який ключ витіснено",
                  size=13, color=MUTED))

    render(out("trace.svg"), W, H, *f,
           title="Кеш на 3 записи, та сама стрічка звернень — три правила вибору жертви")


# ── quadrant: два сигнали минулого й де політики розходяться ─────────────────
# Ідея: з минулого видно рівно дві речі — коли ключ питали востаннє і скільки
# разів його питали. Два з чотирьох випадків політики бачать однаково, а два
# інші — це рівно ті місця, де кожна з них помиляється.
def fig_quadrant():
    W, H = 1010, 540
    f = []

    f.append(text(365, 104, "звертались ДАВНО", size=15, bold=True, color=MUTED))
    f.append(text(775, 104, "звертались ЩОЙНО", size=15, bold=True, color=MUTED))

    b, _, _ = textbox(85, 200, "багато\nзвернень", size=13, bold=True, min_w=130, pad=12)
    f.append(b)
    b, _, _ = textbox(85, 380, "мало\nзвернень", size=13, bold=True, min_w=130, pad=12)
    f.append(b)

    cells = [
        (175, 120, "гарячий із паузою — або мертва зірка\n"
                   "LRU: викине   ·   LFU: лишить\n"
                   "одного сигналу тут замало", RED_F, POS),
        (585, 120, "стабільно гарячий\n"
                   "LRU: лишить   ·   LFU: лишить\n"
                   "обидві мають рацію", GREEN_F, FIELD),
        (175, 300, "давно й майже не потрібен\n"
                   "LRU: викине   ·   LFU: викине\n"
                   "обидві мають рацію", GREEN_F, FIELD),
        (585, 300, "щойно прочитаний під час скану\n"
                   "LRU: лишить   ·   LFU: викине\n"
                   "одного сигналу тут замало", RED_F, POS),
    ]
    for x, y, s, fill, stroke in cells:
        f.append(fitbox(x, y, 380, 160, s, size=14, fill=fill, stroke=stroke, sw=2, pad=16))

    f.append(text(W / 2, 500, "Дві червоні клітинки — це і є характерні помилки кожної політики.",
                  size=14, color=MUTED))

    render(out("quadrant.svg"), W, H, *f,
           title="Усе, що видно з минулого: коли питали востаннє і скільки разів")


# ── clock: кільце з бітами звернення й стрілка ───────────────────────────────
# Ідея: звернення коштує один запис біта (без замків і без перебудови списку),
# а вся робота відкладена на мить витіснення, коли стрілка обходить кільце
# й роздає другий шанс усім, кого чіпали від її минулого проходу.
def fig_clock():
    W, H = 1020, 580
    f = []

    cx, cy, R = 300, 320, 165
    f.append(circle(cx, cy, R, fill="none", stroke=MUTED, sw=1.5))

    slots = [("K1", 0), ("K2", 1), ("K3", 1), ("K4", 0),
             ("K5", 1), ("K6", 0), ("K7", 1), ("K8", 1)]
    for i, (name, bit) in enumerate(slots):
        a = -math.pi / 2 + i * 2 * math.pi / len(slots)
        sx, sy = cx + R * math.cos(a), cy + R * math.sin(a)
        fill = RED_F if bit == 0 else GREEN_F
        stroke = POS if bit == 0 else FIELD
        b, _, _ = textbox(sx, sy, "%s\nбіт %d" % (name, bit), size=13,
                          fill=fill, stroke=stroke, sw=2, pad=9, min_w=76)
        f.append(b)

    # стрілка-годинник дивиться на K1 (верхній слот)
    f.append(arrow(cx, cy, cx, cy - R + 46, color=INK, sw=3))
    f.append(circle(cx, cy, 7, fill=INK, stroke=INK))
    f.append(text(cx, cy + 34, "стрілка", size=13, color=MUTED))

    panel = [
        (640, 120, "звернення до запису:\nпоставити біт = 1\n(один запис, без замка)", "#eaf0fd", NEG),
        (640, 250, "витіснення: стрілка ступає по колу\nі дивиться на біт слота", FILL, LINE),
        (640, 370, "біт = 1 → скинути в 0\nі крокувати далі (другий шанс)", GREEN_F, FIELD),
        (640, 470, "біт = 0 → це жертва, стоп", RED_F, POS),
    ]
    for x, y, s, fill, stroke in panel:
        h = 96 if s.count("\n") == 2 else (72 if s.count("\n") == 1 else 52)
        f.append(fitbox(x, y, 340, h, s, size=14, fill=fill, stroke=stroke, sw=2, pad=14))

    render(out("clock.svg"), W, H, *f,
           title="CLOCK: один біт на запис замість точного порядку")


# ── admission: двобій на вході ───────────────────────────────────────────────
# Ідея: питання «кого викинути» має пару — «а чи варто взагалі впускати
# новачка»; коли оцінку частоти беруть із довшої історії, ніж уміщає кеш,
# одноразові ключі відбиваються від дверей і не чіпають заслужених.
def fig_admission():
    W, H = 1020, 500
    f = []

    b, _, _ = textbox(160, 130, "кандидат K9\nщойно прочитали з бази", size=13,
                      fill="#eaf0fd", stroke=NEG, sw=2, pad=14)
    f.append(b)
    b, _, _ = textbox(160, 300, "жертва за LRU: K3\nнайдовше не питали", size=13,
                      fill=FILL, stroke=LINE, sw=2, pad=14)
    f.append(b)

    f.append(fitbox(400, 165, 250, 100,
                    "оцінювач частоти\nпам'ятає довшу історію,\nніж уміщає кеш",
                    size=13, fill=FILL, stroke=MUTED, sw=2, pad=12))

    f.append(arrow(300, 140, 396, 190, color=NEG))
    f.append(arrow(300, 292, 396, 240, color=LINE))

    b, _, _ = textbox(790, 150, "K9 ≈ 1 звернення", size=14, fill=RED_F, stroke=POS, sw=2, pad=13)
    f.append(b)
    b, _, _ = textbox(790, 280, "K3 ≈ 7 звернень", size=14, fill=GREEN_F, stroke=FIELD, sw=2, pad=13)
    f.append(b)
    f.append(arrow(654, 200, 700, 160, color=MUTED))
    f.append(arrow(654, 230, 700, 274, color=MUTED))

    b, _, _ = textbox(510, 410, "1 < 7 → новачка не впускаємо, кеш не змінюється",
                      size=15, bold=True, fill=GREEN_F, stroke=FIELD, sw=2, pad=16)
    f.append(b)

    render(out("admission.svg"), W, H, *f,
           title="Двобій на вході: чи заслуговує новачок місця більше за жертву")


# ── anomaly: FIFO дає БІЛЬШЕ промахів на БІЛЬШОМУ кеші ──────────────────────
# Ідея (вставка math-competitive-paging): на стрічці 1 2 3 4 1 2 5 1 2 3 4 5
# FIFO промахується 9 разів на трьох слотах і 10 разів на чотирьох. Ламається
# все на восьмому кроці: менший кеш там влучає, більший — ні.
def fig_anomaly():
    W, H = 1250, 360
    f = []

    seq = ["1", "2", "3", "4", "1", "2", "5", "1", "2", "3", "4", "5"]
    # (влучання?, кого витіснено)
    k3 = [(0, ""), (0, ""), (0, ""), (0, "1"), (0, "2"), (0, "3"),
          (0, "4"), (1, ""), (1, ""), (0, "1"), (0, "2"), (1, "")]
    k4 = [(0, ""), (0, ""), (0, ""), (0, ""), (1, ""), (1, ""),
          (0, "1"), (0, "2"), (0, "3"), (0, "4"), (0, "5"), (0, "1")]

    x0, step, cw, ch = 178, 76, 68, 54

    # підсвітка колонки, де ламається монотонність (крок 8)
    hx = x0 + 7 * step - 4
    f.append(rect(hx, 52, cw + 8, 190, fill="#fff6e0", stroke="#e0a800", sw=2, rx=8))

    f.append(text(160, 84, "звернення:", size=13, color=MUTED, anchor="end"))
    for i, key in enumerate(seq):
        f.append(text(x0 + i * step + cw / 2, 84, key, size=15, bold=True))

    rows = [("FIFO, 3 слоти", k3, "9 промахів"), ("FIFO, 4 слоти", k4, "10 промахів")]
    for r, (name, data, total) in enumerate(rows):
        cy = 138 + r * 72
        b, _, _ = textbox(88, cy, name, size=13, bold=True, min_w=140, pad=10)
        f.append(b)
        for i, (hit, ev) in enumerate(data):
            x = x0 + i * step
            label = "✓" if hit else ("✗\n−" + ev if ev else "✗")
            f.append(fitbox(x, cy - ch / 2, cw, ch, label, size=15,
                            fill=GREEN_F if hit else RED_F,
                            stroke=FIELD if hit else POS,
                            color=FIELD if hit else POS, bold=True))
        f.append(text(x0 + 12 * step + 16, cy + 5, total, size=14, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 288, "крок 8: три слоти влучають, чотири промахуються — "
                                  "більша пам'ять дала гірший результат",
                      size=14, bold=True, fill="#fff6e0", stroke="#e0a800", sw=2, pad=14)
    f.append(b)
    f.append(text(W / 2, 340, "✓ — влучання · ✗ — промах · −X — яку сторінку витіснено",
                  size=13, color=MUTED))

    render(out("anomaly.svg"), W, H, *f,
           title="Аномалія Беладі: та сама стрічка, FIFO, три слоти проти чотирьох")


# ── phases: розбиття стрічки на фази для доведення k-конкурентності LRU ──────
# Ідея: фаза — найдовший блок, у якому ≤ k різних сторінок. Зверху видно, чому
# LRU промахується у фазі ≤ k разів, знизу — чому MIN промахується ≥ 1 разу
# у зсунутому вікні, і чому вікна не перетинаються.
def fig_phases():
    W, H = 1200, 500
    f = []

    seq = ["A", "B", "C", "A", "B", "D", "A", "E", "D", "A", "B", "C", "B", "A"]
    x0, cw, gap = 96, 66, 6
    stp = cw + gap
    cy, ch = 108, 52

    def span(i, j):
        """ліва й права межі клітинок i..j (1-базовані)"""
        return x0 + (i - 1) * stp, x0 + (j - 1) * stp + cw

    for i, key in enumerate(seq):
        x = x0 + i * stp
        f.append(fitbox(x, cy - ch / 2, cw, ch, key, size=16, bold=True,
                        fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(x + cw / 2, cy + 52, str(i + 1), size=11, color=MUTED))

    def bracket(y, i, j, color):
        a, b = span(i, j)
        return [line(a, y, b, y, color=color, sw=2.5),
                line(a, y - 9, a, y + 9, color=color, sw=2.5),
                line(b, y - 9, b, y + 9, color=color, sw=2.5)]

    # фази
    phases = [(1, 5, "фаза 1\n{A, B, C}"), (6, 10, "фаза 2\n{D, A, E}"),
              (11, 14, "фаза 3\n{B, C, A}")]
    for i, j, lab in phases:
        f.extend(bracket(196, i, j, NEG))
        a, b = span(i, j)
        f.append(fitbox(a, 214, b - a, 60, lab, size=13, fill="#eaf0fd",
                        stroke=NEG, sw=2, pad=8))

    f.append(text(W / 2, 306, "у кожній фазі рівно k = 3 різних сторінок → "
                              "LRU промахнеться в ній щонайбільше 3 рази",
                  size=14, bold=True, color=NEG))

    # вікна для нижньої оцінки MIN
    wins = [(2, 6, "вікно 1: {B, C, D} — 3 сторінки, жодна не A"),
            (7, 11, "вікно 2: {E, D, B} — 3 сторінки, жодна не D")]
    for i, j, lab in wins:
        f.extend(bracket(346, i, j, FIELD))
        a, b = span(i, j)
        f.append(fitbox(a, 362, b - a, 46, lab, size=12, fill=GREEN_F,
                        stroke=FIELD, sw=2, pad=8))

    f.append(text(W / 2, 448, "одразу після першого звернення фази MIN тримає ту сторінку "
                              "плюс ще ≤ 2 інші,", size=14, bold=True, color=FIELD))
    f.append(text(W / 2, 470, "а у вікні просять 3 відмінні від неї → хоча б один промах; "
                              "вікна не перетинаються", size=14, bold=True, color=FIELD))

    render(out("phases.svg"), W, H, *f,
           title="Розбиття стрічки на фази: k = 3")


# ── timeline: вісім років, за які задача витіснення стала наукою ─────────────
# Ідея (вставка hist-paging-origins): усі сьогоднішні правила й сама мірка,
# якою їх міряють, з'явилися в одному короткому проміжку довкола сторінкування,
# а у вебові кеші приїхали через сорок років майже без змін.
def fig_eviction_timeline():
    W, H = 1400, 392
    AX = 214                      # вісь часу
    BOX_W, BOX_H = 168, 96
    f = []

    events = [
        (100, "up", "1962 · «Атлас»\nмашина вперше\nсама обирає жертву"),
        (278, "down", "1966 · Беладі\nправило MIN —\nмірка, якої не досягти"),
        (456, "up", "1968 · Корбато\nкільце зі стрілкою\nй один біт заліза"),
        (634, "down", "1968 · Деннінг\nробоча множина:\nпитання «скільки»"),
        (812, "up", "1969 · Беладі,\nНельсон, Шедлер\nбільший кеш —\nбільше промахів"),
        (990, "down", "1970 · Меттсон\nі співавтори\nкрива промахів\nза один прохід"),
    ]

    f.append(line(40, AX, 1080, AX, color=MUTED, sw=2))
    f.append(line(1086, AX, 1120, AX, color=MUTED, sw=2, dash="7 7"))

    for cx, side, txt in events:
        if side == "up":
            top = AX - 44 - BOX_H
            f.append(line(cx, top + BOX_H, cx, AX - 6, color=MUTED))
        else:
            top = AX + 44
            f.append(line(cx, AX + 6, cx, top, color=MUTED))
        f.append(fitbox(cx - BOX_W / 2, top, BOX_W, BOX_H, txt, size=13))
        f.append(circle(cx, AX, 6, fill=INK, stroke=INK))

    f.append(fitbox(1128, AX - 58, 250, 116,
                    "1996 Squid · 2003 memcached\n2009 Redis\n\nті самі правила,\nінші константи",
                    size=13, bold=True, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(1103, AX - 74, "≈ 40 років", size=13, color=MUTED, anchor="end"))

    f.append(text(W / 2, 374, "усе, що сьогодні працює у вебових кешах, придумано довкола "
                              "однієї задачі: розкласти програму між осердям і барабаном",
                  size=13, color=MUTED))

    render(out("timeline.svg"), W, H, *f,
           title="Вісім років, за які «кого викинути» стало питанням із мірою")


# ── thennow: та сама задача, інші константи ──────────────────────────────────
# Ідея: правила переїхали зі сторінкування у вебові кеші без змін, а змінилися
# рівно ті числа, з яких і виростають сьогоднішні рішення про облік свіжості.
def fig_then_now():
    W, H = 940, 528
    x0, c1, c2, c3 = 30, 220, 320, 340
    yh, hh, rh = 62, 48, 54
    f = []

    xs = [x0, x0 + c1, x0 + c1 + c2]
    ws = [c1, c2, c3]

    head = ["", "сторінкування, 1960-ті", "кеш у пам'яті, сьогодні"]
    for i in range(3):
        f.append(fitbox(xs[i], yh, ws[i], hh, head[i], size=14, bold=True))

    rows = [
        ("що витісняємо", "сторінка — усі однакові,\n512 слів", "запис — від сотні байтів\nдо мегабайтів"),
        ("скільки їх у пам'яті", "32 кадри в осерді", "до 10⁸ ключів на вузол"),
        ("влучання коштує", "осердя: мікросекунди", "пам'ять: наносекунди"),
        ("промах коштує", "барабан: мілісекунди", "мережа й база: мілісекунди"),
        ("хто бачить звернення", "ніхто — лише біт заліза", "сам кеш — кожне влучання"),
        ("чому наближаємо", "стежити НЕМОЖЛИВО", "стежити ЗАДОРОГО"),
        ("хто звертається", "один процесор", "десятки ядер одночасно"),
    ]

    for r, (a, b, c) in enumerate(rows):
        y = yh + hh + r * rh
        mark = (a == "чому наближаємо")
        f.append(fitbox(xs[0], y, ws[0], rh, a, size=13, bold=True))
        f.append(fitbox(xs[1], y, ws[1], rh, b, size=13, bold=mark,
                        fill="#fdecea" if mark else BG))
        f.append(fitbox(xs[2], y, ws[2], rh, c, size=13, bold=mark,
                        fill=GREEN_F if mark else BG))

    f.append(text(W / 2, 514, "правило вибору жертви лишилося тим самим — "
                              "переписали лише числа, на які воно спирається",
                  size=13, color=MUTED))

    render(out("thennow.svg"), W, H, *f,
           title="Та сама задача через шістдесят років: що змінилося насправді")


# ── hotpath: де саме стоїть точка серіалізації (вставка proj-lru-clock) ──────
# Ідея: різниця між точним LRU і CLOCK у коді — не в правилі вибору жертви,
# а в тому, яка частка запитів мусить пройти крізь одну спільну точку.
def fig_hotpath():
    W, H = 1100, 440
    f = []

    f.append(rect(30, 46, 500, 356, fill=BG, stroke="#c9ced6", sw=1.2))
    f.append(rect(570, 46, 500, 356, fill=BG, stroke="#c9ced6", sw=1.2))
    f.append(text(280, 74, "точний LRU: влучання переставляє вузол", size=14, bold=True))
    f.append(text(820, 74, "CLOCK: влучання пише свій байт", size=14, bold=True))

    # ядра
    for i in range(4):
        f.append(fitbox(54 + i * 116, 92, 104, 34, "ядро %d" % (i + 1), size=13))
        f.append(fitbox(594 + i * 116, 92, 104, 34, "ядро %d" % (i + 1), size=13))

    # ліворуч: усі стрілки сходяться в один замок
    for i in range(4):
        f.append(arrow(54 + i * 116 + 52, 130, 280, 166, color=POS))
    f.append(fitbox(160, 168, 240, 42, "єдиний замок", size=14, bold=True,
                    fill=RED_F, stroke=POS, sw=2, color=POS))
    f.append(arrow(280, 212, 280, 246, color=POS))
    f.append(fitbox(64, 248, 432, 48,
                    "голова й хвіст списку — одна кеш-лінія,\n"
                    "яку переписує КОЖНЕ влучання",
                    size=13, fill=RED_F, stroke=POS, sw=2))
    f.append(text(280, 334, "крізь замок проходить 100 % запитів", size=14, bold=True, color=POS))
    f.append(text(280, 362, "стеля пропускної здатності — спільна на всі ядра;",
                  size=13, color=MUTED))
    f.append(text(280, 384, "від додавання ядер вона не підіймається", size=13, color=MUTED))

    # праворуч: кожне ядро пише у свій байт
    cells_x0, cw, gap = 644, 28, 4
    for i in range(11):
        x = cells_x0 + i * (cw + gap)
        touched = i in (1, 4, 7, 10)
        f.append(fitbox(x, 166, cw, 34, "1" if touched else "0", size=13,
                        fill=GREEN_F if touched else FILL,
                        stroke=FIELD if touched else LINE,
                        color=FIELD if touched else MUTED, bold=touched, pad=2))
    for i in range(4):
        xc = 594 + i * 116 + 52
        cell_c = cells_x0 + (1 + 3 * i) * (cw + gap) + cw / 2
        f.append(arrow(xc, 130, cell_c, 162, color=FIELD))
    f.append(text(820, 226, "масив байтів звернення: у кожного слота свій",
                  size=13, color=MUTED))
    f.append(fitbox(600, 248, 440, 48,
                    "замок і крок стрілки — лише на промаху,\n"
                    "а промахів рівно 1 − h від усіх запитів",
                    size=13, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(820, 334, "при 99 % влучань серіалізується 1 % запитів",
                  size=14, bold=True, color=FIELD))
    f.append(text(820, 362, "стеля відсунулася в 1/(1−h) разів — у сто;", size=13, color=MUTED))
    f.append(text(820, 384, "саме правило вибору жертви майже не змінилося", size=13, color=MUTED))

    render(out("hotpath.svg"), W, H, *f,
           title="Замок — це один сервер: питання лише в тому, яка частка запитів у нього заходить")


if __name__ == "__main__":
    fig_trace()
    fig_quadrant()
    fig_clock()
    fig_admission()
    fig_anomaly()
    fig_phases()
    fig_eviction_timeline()
    fig_then_now()
    fig_hotpath()
    print("ok:", os.listdir(IMG))
