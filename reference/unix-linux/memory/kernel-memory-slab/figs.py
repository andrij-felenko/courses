# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"
AMBER = "#fdf6e3"
AMBERL = "#b7791f"


# ── 1. Анатомія кеша об'єктів: слаби, слоти й список вільних усередині ────────
def fig_slab_anatomy():
    W, H = 1200, 700
    p = []

    p.append(fitbox(60, 44, 1080, 52,
                    "КЕШ ОБ'ЄКТІВ ОДНОГО ТИПУ — усі слоти в ньому однакового розміру",
                    size=15, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    lists = [
        (60, "ПОВНІ СЛАБИ", MUTED, PALE,
         "вільних слотів немає —\nроздавати з них нічого"),
        (430, "ЧАСТКОВІ СЛАБИ", NEG, COOL,
         "є і зайняті, і вільні слоти —\nсаме звідси беруть"),
        (800, "ПОРОЖНІ СЛАБИ", FIELD, GREENF,
         "усі слоти вільні — сторінки\nможна віддати назад"),
    ]
    for x, name, accent, fillc, note in lists:
        p.append(fitbox(x, 124, 340, 42, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 174, 340, 60, note, size=12,
                        fill=SOFT, stroke=accent, sw=1.2, color=INK))

    p.append(text(600, 268, "один частковий слаб зблизька: суцільний блок сторінок, порізаний на слоти",
                  size=13, color=MUTED))

    slots = ["зайнято", "зайнято", "вільно", "зайнято", "зайнято",
             "вільно", "зайнято", "вільно", "вільно", "зайнято"]
    for i, s in enumerate(slots):
        x = 100 + i * 100
        busy = (s == "зайнято")
        p.append(fitbox(x, 290, 100, 104, s, size=11,
                        fill=(COOL if busy else "#ffffff"),
                        stroke=(NEG if busy else POS), sw=(1.4 if busy else 2.0),
                        color=(INK if busy else POS)))

    free_x = [100 + i * 100 + 50 for i, s in enumerate(slots) if s == "вільно"]
    for x in free_x:
        p.append(line(x, 394, x, 432, color=POS, sw=1.6))
    for a, b in zip(free_x, free_x[1:]):
        p.append(arrow(a, 432, b - 4, 432, color=POS, sw=1.8))

    p.append(fitbox(70, 410, 200, 44, "голова списку", size=12,
                    fill=WARM, stroke=POS, sw=1.6, color=POS, bold=True))
    p.append(arrow(276, 432, free_x[0] - 4, 432, color=POS, sw=1.8))
    p.append(fitbox(1010, 410, 130, 44, "кінець", size=12,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED))
    p.append(arrow(free_x[-1], 432, 1006, 432, color=POS, sw=1.8))

    p.append(text(600, 490,
                  "у вільному слоті лежить не об'єкт, а адреса наступного вільного слота",
                  size=13, color=INK))

    p.append(fitbox(60, 520, 1080, 96,
                    "звідси все й береться: розмір однаковий — шукати придатний шматок не треба;\n"
                    "список вільних живе всередині самих вільних слотів — окремої пам'яті на облік нема",
                    size=13, fill=SOFT, stroke=FIELD, sw=1.6, color=INK))

    p.append(text(600, 656,
                  "виділення — це зняти голову списку; звільнення — покласти слот назад у голову",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "slab-anatomy.svg"), W, H, *p,
           title="Кеш об'єктів, його слаби і список вільних слотів усередині слаба")


# ── 2. Шари, якими спускається виділення, і ціна кожного ─────────────────────
def fig_slub_layers():
    X1, W1 = 60, 300
    X2, W2 = 380, 430
    X3, W3 = 830, 290
    RH, GAP, TOP, HH = 92, 12, 96, 54
    W = X3 + W3 + 60

    rows = [
        ("власний слаб цього процесора", COOL, NEG,
         "вершина списку вільних слотів,\nвже прив'язана саме до цього ядра",
         "кілька інструкцій,\nбез жодного замка"),
        ("часткові слаби цього процесора", COOL, NEG,
         "невеликий запас слабів, у яких\nще лишилися вільні слоти",
         "перемкнути вказівник\nна наступний слаб"),
        ("часткові слаби вузла пам'яті", AMBER, AMBERL,
         "спільний запас на всі ядра вузла;\nтут уже треба домовлятися",
         "замок вузла —\nє за що конкурувати"),
        ("сторінковий алокатор", WARM, POS,
         "нового слаба немає — треба взяти\nсуцільний блок 2ⁿ сторінок",
         "найдорожче: аж до\nвитіснення й ущільнення"),
    ]

    H = TOP + HH + GAP + len(rows) * (RH + GAP) + 130
    p = []

    p.append(text(W / 2, 58,
                  "виділення шукає вільний слот згори вниз і зупиняється на першому, де його знайшло",
                  size=13, color=INK))

    p.append(fitbox(X1, TOP, W1, HH, "куди звертаємось", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED, bold=True))
    p.append(fitbox(X2, TOP, W2, HH, "що там лежить", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED, bold=True))
    p.append(fitbox(X3, TOP, W3, HH, "ціна", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED, bold=True))

    y = TOP + HH + GAP
    for name, fillc, accent, what, cost in rows:
        p.append(fitbox(X1, y, W1, RH, name, size=13, fill=fillc,
                        stroke=accent, sw=1.7, color=INK, bold=True))
        p.append(fitbox(X2, y, W2, RH, what, size=12, fill=SOFT,
                        stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(X3, y, W3, RH, cost, size=12, fill="#ffffff",
                        stroke=accent, sw=1.5, color=accent, bold=True))
        y += RH + GAP

    p.append(fitbox(X1, y + 10, W - 2 * X1, 80,
                    "звільнення йде іншим шляхом: об'єкт завжди повертається у власний слаб,\n"
                    "тому пам'ять не зависає в чужій черзі й видно, який слаб уже цілком вільний",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    p.append(text(W / 2, y + 128,
                  "верхній рядок обслуговує переважну більшість викликів — усе інше є запасним шляхом",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "slub-layers.svg"), W, H, *p,
           title="Шари, якими спускається виділення об'єкта в ядрі")


# ── 3. Дві різні механіки звільнення: сторінки проти об'єктів ядра ───────────
def fig_two_reclaims():
    W, H = 1220, 720
    p = []

    p.append(fitbox(60, 44, 540, 50, "СТОРІНКИ ПРОЦЕСІВ", size=15,
                    fill=COOL, stroke=NEG, sw=1.9, color=NEG, bold=True))
    p.append(fitbox(620, 44, 540, 50, "ОБ'ЄКТИ ЯДРА", size=15,
                    fill=WARM, stroke=POS, sw=1.9, color=POS, bold=True))

    left = [
        "черги: видно, до чого давно не зверталися",
        "зворотні відображення: видно всіх,\nхто на сторінку посилається",
        "підкладка: вміст є куди відкласти —\nу файл або у своп",
    ]
    right = [
        "черг нема: на сторінці слаба\nдесятки об'єктів різних власників",
        "зворотних відображень нема: хто тримає\nвказівник на об'єкт — невідомо нікому",
        "підкладки нема: структуру ядра\nнікуди відкласти й нізвідки перечитати",
    ]
    yy = 112
    for l, r in zip(left, right):
        p.append(fitbox(60, yy, 540, 84, l, size=12,
                        fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        p.append(fitbox(620, yy, 540, 84, r, size=12,
                        fill=SOFT, stroke=POS, sw=1.3, color=INK))
        yy += 96

    p.append(fitbox(60, 404, 540, 66, "відбір ЗАБИРАЄ сам", size=15,
                    fill=COOL, stroke=NEG, sw=2.0, color=NEG, bold=True))
    p.append(fitbox(620, 404, 540, 66, "відбір може лише ПОПРОСИТИ", size=15,
                    fill=WARM, stroke=POS, sw=2.0, color=POS, bold=True))

    p.append(text(610, 512, "протокол прохання складається з двох запитань",
                  size=13, color=INK))

    steps = [
        (60, "скільки об'єктів\nти міг би звільнити?", GREENF, FIELD),
        (400, "стільки-то —\nвідповідає власник", SOFT, MUTED),
        (740, "звільни ось таку\nчастку від них", AMBER, AMBERL),
    ]
    for x, s, fillc, accent in steps:
        p.append(fitbox(x, 536, 300, 76, s, size=12,
                        fill=fillc, stroke=accent, sw=1.6, color=INK))
    p.append(arrow(366, 574, 396, 574, color=MUTED, sw=1.8))
    p.append(arrow(706, 574, 736, 574, color=MUTED, sw=1.8))
    p.append(fitbox(1076, 536, 84, 76, "звіт", size=12,
                    fill="#ffffff", stroke=FIELD, sw=1.6, color=FIELD, bold=True))
    p.append(arrow(1046, 574, 1072, 574, color=MUTED, sw=1.8))

    p.append(text(610, 660,
                  "частку рахують однакову для всіх — і для черг сторінок, і для кожного кеша ядра",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-reclaims.svg"), W, H, *p,
           title="Чому пам'ять ядра звільняють проханням, а не забиранням")


# ── 4. Як росте вимога до кеша, коли відбір стає наполегливішим ──────────────
def fig_pressure_ramp():
    import math
    W, H = 1180, 720
    p = []

    freeable = 4000000
    prios = [12, 10, 8, 6, 4, 2, 0]
    vals = [(freeable >> pr) * 4 // 2 for pr in prios]

    base, top = 470, 130
    lo, hi = 3.0, 7.0

    def Y(v):
        return base - (math.log10(v) - lo) / (hi - lo) * (base - top)

    for e in range(3, 8):
        y = Y(10 ** e)
        p.append(line(120, y, 1090, y, color="#dfe4ec", sw=1.0))
        p.append(text(108, y + 4, "10%s" % "⁰¹²³⁴⁵⁶⁷⁸⁹"[e], size=12,
                      color=MUTED, anchor="end"))

    p.append(line(120, base, 1090, base, color=INK, sw=1.6))

    for i, (pr, v) in enumerate(zip(prios, vals)):
        x = 140 + i * 136
        y = Y(v)
        col = NEG if pr >= 8 else (AMBERL if pr >= 4 else POS)
        p.append(rect(x, y, 96, base - y, fill="#ffffff", stroke=col, sw=2.0, rx=3))
        p.append(text(x + 48, y - 14, "%.2f %%" % (100.0 * v / freeable),
                      size=12, color=col, bold=True))
        p.append(text(x + 48, base + 26, str(pr), size=14, color=INK, bold=True))

    p.append(text(605, base + 56,
                  "наполегливість відбору: 12 — перший, найм'якший захід, 0 — остання спроба перед вбивцею",
                  size=13, color=INK))

    p.append(fitbox(120, base + 84, 970, 96,
                    "вимога до кеша = (скільки об'єктів можна звільнити) ÷ 2^наполегливість × 4 ÷ ціна відтворення\n"
                    "ціна відтворення типово 2 — стільки «пошуків на диску» коштує зробити об'єкт наново",
                    size=13, fill=SOFT, stroke=FIELD, sw=1.6, color=INK))

    p.append(text(605, base + 216,
                  "кеш на чотири мільйони записів: спершу в нього просять пару тисяч, "
                  "наприкінці — удвічі більше, ніж у ньому є",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "pressure-ramp.svg"), W, H, *p,
           title="Скільки просять у кеша ядра залежно від наполегливості відбору")


# ── 5. Три покоління розподілювачів Linux на одній осі (вставка hist) ────────
def fig_slab_generations():
    W, H = 1240, 660
    p = []

    p.append(fitbox(40, 34, 1160, 44,
                    "ТРИ ПОКОЛІННЯ СЛАБОВИХ РОЗПОДІЛЮВАЧІВ LINUX — і одна ідея під ними",
                    size=15, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    def X(year):
        return 150 + (year - 1994) * (950.0 / 32.0)

    p.append(fitbox(60, 96, 470, 60,
                    "1994 · SunOS 5.4 (Solaris 2.4) · Джеф Бонвік\n"
                    "ідея: кешувати зібрані об'єкти, а не байти",
                    size=13, fill=AMBER, stroke=AMBERL, sw=1.6, color=INK))
    p.append(line(X(1994), 156, X(1994), 186, color=AMBERL, sw=2.0))

    axis_y = 192
    p.append(line(130, axis_y, 1130, axis_y, color=MUTED, sw=1.6))
    for yr in (1994, 2000, 2006, 2012, 2018, 2024):
        p.append(line(X(yr), axis_y, X(yr), axis_y + 12, color=MUTED, sw=1.4))
        p.append(text(X(yr), axis_y + 32, str(yr), size=12, color=MUTED))

    rows = [
        (250, "SLAB", "порт задуму Бонвіка,\nз чергами на процесор", NEG, COOL,
         1997, 2024,
         "1997 · ядро 2.1.23 · Марк Гемент",
         "2024 · ядро 6.8 · прибрано"),
        (370, "SLOB", "K&R-список\nдля крихітних систем", MUTED, PALE,
         2006, 2023,
         "2006 · ядро 2.6.16 · Метт Меколл",
         "2023 · ядро 6.4 · прибрано"),
        (490, "SLUB", "без черг;\nєдиний, що лишився", FIELD, GREENF,
         2007, 2026,
         "2007 · 2.6.22 злито, 2.6.23 за умовчанням · Крістоф Ламетер",
         "донині"),
    ]
    for y, name, note, accent, fillc, y0, y1, ann0, ann1 in rows:
        p.append(fitbox(40, y - 14, 190, 62, name + "\n" + note, size=12,
                        fill=fillc, stroke=accent, sw=1.6, color=accent, bold=False))
        x0, x1 = X(y0), X(y1)
        p.append(rect(x0, y, x1 - x0, 30, fill=fillc, stroke=accent, sw=2.0, rx=4))
        p.append(text(x0, y - 22, ann0, size=12, color=INK, anchor="start"))
        p.append(text(x1, y - 22, ann1, size=12, color=accent,
                      anchor="end", bold=True))

    p.append(fitbox(150, 570, 980, 56,
                    "Прибирали не помилку, а надлишок: три різні реалізації одного інтерфейсу\n"
                    "означали, що кожну нову властивість ядра доводилося робити тричі",
                    size=13, fill=SOFT, stroke=FIELD, sw=1.6, color=INK))

    render(os.path.join(OUT, "slab-generations.svg"), W, H, *p,
           title="Три покоління слабових розподілювачів Linux на осі часу")


fig_slab_anatomy()
fig_slub_layers()
fig_two_reclaims()
fig_pressure_ramp()
fig_slab_generations()
print("ok")


# ── Дослід: чому звільнення об'єктів не повертає сторінок ────────────────────
def fig_scatter_cost():
    W, H = 1200, 600
    p = []

    NS, SW, GAP = 10, 108, 8
    X0 = (W - (NS * SW + (NS - 1) * GAP)) / 2.0
    SLOTS, SLW, SLH = 8, 12, 30
    PAD = (SW - SLOTS * SLW) / 2.0
    BOXH = SLH + 12

    pinned = {1: 3, 4: 6, 7: 1}

    def slab(x, y, fills):
        p.append(rect(x, y, SW, BOXH, fill=PALE, stroke=MUTED, sw=1.3, rx=3))
        for s in range(SLOTS):
            sx = x + PAD + s * SLW
            kind = fills[s]
            if kind == "pin":
                p.append(rect(sx, y + 6, SLW - 2, SLH, fill=WARM,
                              stroke=POS, sw=1.6, rx=2))
            elif kind == "live":
                p.append(rect(sx, y + 6, SLW - 2, SLH, fill=COOL,
                              stroke=NEG, sw=1.0, rx=2))
            else:
                p.append(rect(sx, y + 6, SLW - 2, SLH, fill="#ffffff",
                              stroke="#dbe0e8", sw=1.0, rx=2))

    def strip(y, mode):
        for i in range(NS):
            x = X0 + i * (SW + GAP)
            if mode == "before":
                slab(x, y, ["pin" if pinned.get(i) == s else "live"
                            for s in range(SLOTS)])
            elif mode == "after":
                if i in pinned:
                    slab(x, y, ["pin" if pinned[i] == s else "free"
                                for s in range(SLOTS)])
                else:
                    p.append(rect(x, y, SW, BOXH, fill="#ffffff",
                                  stroke="#dbe0e8", sw=1.2, rx=3))
            else:
                if i == 0:
                    slab(x, y, ["pin" if s < 3 else "free" for s in range(SLOTS)])

    p.append(fitbox(60, 40, W - 120, 52,
                    "закріплені об'єкти розсіяні по слабах — і кожен тримає цілий слаб",
                    size=15, fill=SOFT, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, 128,
                  "усі слоти зайняті; червоні — закріплені відкритими файлами",
                  size=13, color=INK))
    strip(142, "before")

    p.append(text(W / 2, 220,
                  "негативні записи викинуто; слаби без червоного повернуто, решта живі",
                  size=13, color=INK))
    strip(234, "after")

    p.append(text(W / 2, 312,
                  "стільки місця вистачило б тим самим червоним об'єктам",
                  size=13, color=INK))
    strip(326, "packed")

    p.append(fitbox(60, 400, W - 120, 96,
                    "0.8 % об'єктів утримали 15 % сторінок: слаб віддають лише цілком,\n"
                    "тож один живий об'єкт коштує стільки ж місця, скільки повний слаб",
                    size=14, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))

    p.append(text(W / 2, 540,
                  "слаб намальовано на 8 слотів замість справжнього 21 — щоб було видно окремі слоти",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "scatter-cost.svg"), W, H, *p,
           title="Чому звільнення більшості об'єктів майже не повертає сторінок")


fig_scatter_cost()


# ── Довідка: сходи розмірів kmalloc і п'ять сімейств кешів ───────────────────
def fig_kmalloc_families():
    W, H = 1240, 700
    p = []

    p.append(fitbox(60, 36, 1120, 46,
                    "Один виклик kmalloc — тринадцять щаблів розміру і п'ять сімейств кешів",
                    size=15, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(text(620, 124,
                  "ЩАБЛІ РОЗМІРУ: запит округлюють угору до найближчого",
                  size=13, color=INK, bold=True))

    steps = ["8", "16", "32", "64", "96", "128", "192",
             "256", "512", "1k", "2k", "4k", "8k"]
    for i, s in enumerate(steps):
        x = 60 + i * 86
        odd = s in ("96", "192")
        p.append(fitbox(x, 150, 82, 54, s, size=15,
                        fill=(AMBER if odd else COOL),
                        stroke=(AMBERL if odd else NEG), sw=1.6,
                        color=(AMBERL if odd else INK), bold=True))

    p.append(arrow(961, 250, 961, 210, color=POS, sw=1.8))
    p.append(fitbox(800, 254, 340, 58,
                    "запит 1032 Б → щабель 2 КіБ\n1016 Б (49.6 %) марно",
                    size=13, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(fitbox(60, 254, 700, 58,
                    "96 і 192 — не степені двійки: щаблі додано там, де округлення коштувало б удвічі\n"
                    "понад 8 КіБ kmalloc іде просто в сторінковий роздавач — блок 2ⁿ сторінок, стеля 4 МіБ",
                    size=12, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))

    p.append(text(620, 346,
                  "СІМЕЙСТВА: ті самі щаблі, різні кеші — сімейство обирає прапорець запиту",
                  size=13, color=INK, bold=True))

    fams = [
        ("kmalloc-<щабель>", "звичайний запит — типовий шлях", NEG, COOL),
        ("kmalloc-cg-<щабель>", "__GFP_ACCOUNT — байти йдуть на рахунок контрольної групи", NEG, COOL),
        ("kmalloc-rcl-<щабель>", "__GFP_RECLAIMABLE — слаби потрапляють у SReclaimable", FIELD, GREENF),
        ("dma-kmalloc-<щабель>", "__GFP_DMA — пам'ять із найнижчої зони, для старих пристроїв", MUTED, PALE),
        ("kmalloc-rnd-00…15-<щабель>", "CONFIG_RANDOM_KMALLOC_CACHES — 16 копій звичайного сімейства;\nкопію обирає адреса коду, що викликав", AMBERL, AMBER),
    ]
    for i, (name, cond, accent, fillc) in enumerate(fams):
        y = 366 + i * 62
        p.append(fitbox(60, y, 340, 52, name, size=13,
                        fill=fillc, stroke=accent, sw=1.6, color=accent, bold=True))
        p.append(fitbox(420, y, 760, 52, cond, size=12,
                        fill=SOFT, stroke=accent, sw=1.2, color=INK))

    render(os.path.join(OUT, "kmalloc-families.svg"), W, H, *p,
           title="Щаблі розміру kmalloc і п'ять сімейств кешів")


fig_kmalloc_families()
