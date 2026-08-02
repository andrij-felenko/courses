# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE  = "#eef4ff"
GREEN = "#eaf7ef"
AMBER = "#fff6e6"
GREY  = "#f2f2f5"
RED   = "#fdecea"


# ── Фігура 1: добуток «місця зміни × подання» проти суми ──────────────────────
def fig_two_homes():
    W, H = 1260, 620
    f = []

    f.append(line(630, 78, 630, 566, color=MUTED, sw=1.2, dash="5 7"))

    srcs = ["завантаження з диска", "правка користувача", "відповідь сервера"]
    views = ["поле вводу", "велика цифра", "кнопка «Зберегти»"]
    ys = [190, 288, 386]

    # ── ЛІВОРУЧ: кожне джерело саме оновлює кожне подання ──
    f.append(text(320, 118, "Руками: кожен, хто пише, знає всіх, хто показує",
                  size=15.5, bold=True))
    for s, y in zip(srcs, ys):
        f.append(fitbox(46, y - 30, 208, 60, s, size=12.5, fill=AMBER, sw=1.6))
    for v, y in zip(views, ys):
        f.append(fitbox(410, y - 30, 190, 60, v, size=12.5, fill=GREEN, sw=1.6))
    for ys_ in ys:                      # смуга 254…404 лишається порожньою під стрілки
        for yv in ys:
            f.append(line(258, ys_, 404, yv, color=MUTED, sw=1.1))
    f.append(text(320, 470, "3 місця зміни × 3 подання = 9 зв'язків",
                  size=14, bold=True, color=POS))
    f.append(text(320, 500, "додати четверте подання — правити всі три джерела",
                  size=12.5, color=MUTED))
    f.append(text(320, 528, "забути один рядок — екран мовчки бреше",
                  size=12.5, color=MUTED))

    # ── ПРАВОРУЧ: усі пишуть у значення, від значення йдуть прив'язки ──
    f.append(text(945, 118, "Прив'язкою: обидва боки знають лише про значення",
                  size=15.5, bold=True))
    for s, y in zip(srcs, ys):
        f.append(fitbox(668, y - 30, 190, 60, s, size=12.5, fill=AMBER, sw=1.6))
    f.append(fitbox(900, 240, 130, 96, "значення", size=14, fill=BLUE, sw=2, bold=True))
    for v, y in zip(views, ys):
        f.append(fitbox(1064, y - 30, 176, 60, v, size=12.5, fill=GREEN, sw=1.6))
    for y in ys:
        f.append(arrow(862, y, 896, 288, color=INK, sw=1.4))
        f.append(arrow(1034, 288, 1060, y, color=FIELD, sw=1.6))
    f.append(text(945, 470, "3 записи + 3 прив'язки = 6 зв'язків",
                  size=14, bold=True, color=FIELD))
    f.append(text(945, 500, "додати четверте подання — один рядок в одному місці",
                  size=12.5, color=MUTED))
    f.append(text(945, 528, "рівність тримає рушій, а не пам'ять програміста",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'two-homes.svg'), W, H, *f,
           title="Одна істина, кілька місць: чому ручна синхронізація росте добутком")


# ── Фігура 2: чотири родини виявлення змін ────────────────────────────────────
def fig_detect_families():
    W, H = 1300, 578
    f = []

    labels = ["як дізнається", "ціна", "чого не бачить", "як мовчить"]
    heads = [("Сповіщення", BLUE), ("Звірка", GREEN), ("Перехоплення", AMBER), ("На складанні", GREY)]
    cells = [
        ["сетер гукає\nпідписників",
         "порівняння з копією\nпісля оберту",
         "посередник ловить\nчитання й запис",
         "компілятор дописує\nсповіщення сам"],
        ["дані мусять бути\nспостережувані",
         "робота від розміру\nекрана, не від змін",
         "посередник —\nне той самий об'єкт",
         "потрібне компіляторове\nполе зору"],
        ["зміну всередині\nзначення",
         "нічого — але лише\nу свій момент",
         "доступ повз\nпосередника",
         "зміну поза\nполем зору"],
        ["забули сповістити —\nекран відстає",
         "не влягається —\nцикл до запобіжника",
         "залежність не\nзахопилася",
         "чуже присвоєння\nлишилося німим"],
    ]

    X0, CW, GAP = 232, 250, 12
    xs = [X0 + i * (CW + GAP) for i in range(4)]
    ROWY, RH, RGAP = 154, 82, 12

    for x, (name, col) in zip(xs, heads):
        f.append(fitbox(x, 84, CW, 54, name, size=15, fill=col, sw=1.8, bold=True))
    for r, lab in enumerate(labels):
        y = ROWY + r * (RH + RGAP)
        f.append(text(212, y + RH / 2 + 5, lab, size=13, anchor="end", bold=True, color=MUTED))
        for c, x in enumerate(xs):
            f.append(fitbox(x, y, CW, RH, cells[r][c], size=12.5, fill=BG, sw=1.3))

    f.append(text(650, 542,
                  "Вибір родини — це вибір, що саме проґавити й чим заплатити; тихим лишається кожен",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'detect-families.svg'), W, H, *f,
           title="Чотири способи дізнатися, що джерело змінилося")


# ── Фігура 3: ромб залежностей і збій узгодженості ────────────────────────────
def fig_glitch_diamond():
    W, H = 1280, 620
    f = []

    f.append(line(430, 84, 430, 580, color=MUTED, sw=1.2, dash="5 7"))

    # ── Граф ──
    f.append(text(220, 112, "граф залежностей", size=14, bold=True))
    nodes = [(220, 176, "a = 5", "висота 0", BLUE),
             (120, 300, "b = a+1", "висота 1", GREEN),
             (320, 300, "c = a·2", "висота 1", GREEN),
             (220, 428, "d = b+c", "висота 2", AMBER)]
    for cx, cy, lab, h, col in nodes:
        f.append(fitbox(cx - 78, cy - 30, 156, 60, lab, size=14, fill=col, sw=1.8, bold=True))
    f.append(text(220, 224, "висота 0", size=11.5, color=MUTED))
    f.append(text(48, 300, "1", size=12, color=MUTED, anchor="middle"))
    f.append(text(392, 300, "1", size=12, color=MUTED, anchor="middle"))
    f.append(text(220, 480, "висота 2", size=11.5, color=MUTED))
    f.append(arrow(196, 208, 140, 266))
    f.append(arrow(244, 208, 300, 266))
    f.append(arrow(140, 334, 196, 396))
    f.append(arrow(300, 334, 244, 396))
    f.append(text(220, 536, "d залежить від a двома шляхами", size=12.5, color=MUTED))

    # ── Слід 1: наївний обхід ──
    f.append(rect(468, 100, 772, 232, fill=RED, stroke=POS, sw=1.8, rx=10))
    f.append(text(494, 130, "наївно: углиб від зміненого вузла", size=14.5, bold=True, anchor="start"))
    trace1 = ["a := 5",
              "b := a+1 = 6",
              "d := b+c = 6+2 = 8      ← c ще старе",
              "c := a·2 = 10",
              "d := b+c = 6+10 = 16"]
    y = 162
    for i, ln in enumerate(trace1):
        f.append(text(510, y, ln, size=13.5, anchor="start",
                      color=POS if i == 2 else INK, bold=(i == 2)))
        y += 26
    f.append(text(494, 316, "d обчислено двічі; перший результат не існував ніколи",
                  size=12.5, anchor="start", color=POS))

    # ── Слід 2: за висотами ──
    f.append(rect(468, 360, 772, 190, fill=GREEN, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(494, 390, "за висотами: спершу все, від чого залежить", size=14.5, bold=True, anchor="start"))
    trace2 = ["a := 5",
              "висота 1:   b := 6,   c := 10",
              "висота 2:   d := 6+10 = 16"]
    y = 422
    for ln in trace2:
        f.append(text(510, y, ln, size=13.5, anchor="start"))
        y += 26
    f.append(text(494, 532, "кожен вузол обчислено рівно раз; проміжної неправди немає",
                  size=12.5, anchor="start", color=FIELD))

    render(os.path.join(IMG, 'glitch-diamond.svg'), W, H, *f,
           title="Збій узгодженості: порядок обходу вирішує, що встигне побачити світ")


# ── Фігура 4 (вставка proj): дві фази поширення й відсічка за значенням ───────
def fig_two_phases():
    W, H = 1330, 706
    f = []

    # ═══ ЛІВОРУЧ: граф ═══
    f.append(text(340, 62, "граф залежностей", size=15, bold=True))

    # (cx, cy, підпис, заливка)
    nodes = [
        (250, 158, "s\n1 → 5", BLUE),
        (530, 158, "t\nне чіпали", BG),
        (170, 290, "p = f(s)", AMBER),
        (330, 290, "q = (s > 0)", AMBER),
        (530, 290, "u = k(t)", BG),
        (250, 422, "r = g(p, q)", AMBER),
        (430, 422, "w = h(q, u)", GREY),
        (250, 554, "ефект: показує r", AMBER),
    ]
    for cx, cy, lab, col in nodes:
        f.append(fitbox(cx - 68, cy - 29, 136, 58, lab, size=12.5, fill=col, sw=1.8, bold=True))

    for y, h in ((158, "висота 0"), (290, "висота 1"), (422, "висота 2"), (554, "висота 3")):
        f.append(text(88, y + 5, h, size=11.5, color=MUTED, anchor="end"))

    f.append(arrow(228, 189, 190, 259))          # s → p
    f.append(arrow(272, 189, 312, 259))          # s → q
    f.append(arrow(530, 189, 530, 259))          # t → u
    f.append(arrow(188, 321, 232, 391))          # p → r
    f.append(arrow(312, 321, 268, 391))          # q → r
    f.append(arrow(352, 321, 410, 391))          # q → w
    f.append(arrow(512, 321, 452, 391))          # u → w
    f.append(arrow(250, 453, 250, 523))          # r → ефект

    f.append(text(340, 626, "жовте — позначене у фазі 1; сіре — позначене, але пропущене",
                  size=12, color=MUTED))
    f.append(text(340, 652, "біле — рушій не торкнувся взагалі", size=12, color=MUTED))

    f.append(line(660, 40, 660, 668, color=MUTED, sw=1.2, dash="5 7"))

    # ═══ ПРАВОРУЧ: дві фази ═══
    f.append(rect(700, 62, 600, 168, fill=AMBER, stroke=LINE, sw=1.6, rx=10))
    f.append(text(726, 96, "ФАЗА 1 — позначити застарілим усе нижче", size=15, bold=True, anchor="start"))
    for i, ln in enumerate(["обхід від s вниз: p, q, r, w, ефект — п'ять вузлів",
                            "жодного обчислення: лише прапорці й черга за висотою",
                            "u недосяжний від s — його не торкнуто зовсім"]):
        f.append(text(726, 134 + i * 30, ln, size=13, anchor="start"))

    f.append(rect(700, 254, 600, 300, fill=GREEN, stroke=LINE, sw=1.6, rx=10))
    f.append(text(726, 288, "ФАЗА 2 — обчислити позначене в порядку висот",
                  size=15, bold=True, anchor="start"))
    rows = [
        ("1", "p", "вхід s змінився", "обчислити — нове", INK),
        ("1", "q", "вхід s змінився", "обчислити — ТЕ САМЕ", INK),
        ("2", "r", "вхід p змінився", "обчислити — нове", INK),
        ("2", "w", "ні q, ні u не змінилися", "пропустити", POS),
        ("3", "e", "вхід r змінився", "виконати ефект", INK),
    ]
    for i, (h, name, why, what, col) in enumerate(rows):
        y = 328 + i * 30
        f.append(text(736, y, "висота " + h, size=12.5, anchor="start", color=MUTED))
        f.append(text(826, y, name, size=13, anchor="start", bold=True))
        f.append(text(858, y, why, size=12.5, anchor="start"))
        f.append(text(1070, y, "→ " + what, size=12.5, anchor="start", color=col, bold=(col == POS)))

    f.append(text(726, 512, "позначено 5 · обчислено 4 · пропущено 1",
                  size=13, anchor="start", bold=True, color=FIELD))

    f.append(text(1000, 600,
                  "Позначення коштує стільки, скільки досяжно вниз від зміни;",
                  size=13, color=MUTED))
    f.append(text(1000, 628,
                  "обчислення — лише стільки, скільки СПРАВДІ змінило значення.",
                  size=13, color=MUTED))
    f.append(text(1000, 662, "решта графа не коштує нічого", size=13, color=MUTED, bold=True))

    render(os.path.join(IMG, 'signal-two-phases.svg'), W, H, *f,
           title="Дві фази поширення: позначити досяжне, обчислити те, чий вхід справді змінився")


# ── Фігура 5 (вставка proj): динамічні залежності через гілку ─────────────────
def fig_dynamic_deps():
    W, H = 1260, 648
    f = []

    f.append(text(630, 58, "label = show ? «n = » + n : «нічого»", size=15.5, bold=True))

    f.append(line(630, 88, 630, 500, color=MUTED, sw=1.2, dash="5 7"))

    def panel(cx, title, show_val, edge_from_n, notes, title_col):
        g = []
        g.append(fitbox(cx - 150, 112, 300, 44, title, size=14.5, fill=title_col, sw=1.7, bold=True))
        g.append(fitbox(cx - 180, 190, 130, 54, "show\n" + show_val, size=12.5, fill=BLUE, sw=1.7, bold=True))
        g.append(fitbox(cx + 50, 190, 130, 54, "n", size=13.5,
                        fill=(GREEN if edge_from_n else GREY), sw=1.7, bold=True))
        g.append(fitbox(cx - 95, 336, 190, 56, "label", size=13.5, fill=AMBER, sw=1.9, bold=True))
        g.append(arrow(cx - 115, 246, cx - 55, 328))
        if edge_from_n:
            g.append(arrow(cx + 115, 246, cx + 55, 328, color=FIELD, sw=2))
        else:
            g.append(text(cx + 115, 292, "не прочитано", size=12, color=MUTED))
            g.append(text(cx + 115, 314, "ребра немає", size=12, color=MUTED))
        for i, (ln, col, bold) in enumerate(notes):
            g.append(text(cx, 428 + i * 28, ln, size=12.5, color=col, bold=bold))
        return g

    f += panel(316, "show = false", "false", False,
               [("label.deps = { show }", INK, False),
                ("n.subs = { }", INK, False),
                ("n.set(7) — граф навіть не ворухнувся", MUTED, True)], GREY)

    f += panel(944, "show = true", "true", True,
               [("label.deps = { show, n }", INK, False),
                ("n.subs = { label }", INK, False),
                ("n.set(8) — label переобчислено", FIELD, True)], GREEN)

    f.append(rect(60, 528, 1140, 92, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    f.append(text(630, 562,
                  "Ребро n → label з'являється й зникає саме тоді, коли label переобчислюється й проходить крізь гілку",
                  size=13))
    f.append(text(630, 592,
                  "те, чого цього разу не прочитано, мусить бути знято зі списку підписників — інакше граф росте назавжди",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'signal-dynamic-deps.svg'), W, H, *f,
           title="Динамічні залежності: гілка вирішує, які ребра існують цієї миті")


# ── Фігура 6 (вставка hist): три струмені родоводу ───────────────────────────
def fig_lineage():
    W, H = 1220, 900
    f = []

    cols = [(250, 300, "Двобічні обмеження", AMBER),
            (620, 320, "Однобічний потік даних", BLUE),
            (990, 300, "Клітинки таблиці", GREEN)]
    for cx, cw, head, _ in cols:
        f.append(text(cx, 74, head, size=15.5, bold=True))
        f.append(line(cx - cw / 2, 88, cx + cw / 2, 88, color=MUTED, sw=1.2))

    def box(col, y, l1, l2, fill, h=58):
        cx, cw, _, _ = cols[col]
        return fitbox(cx - cw / 2, y, cw, h, l1 + "\n" + l2, size=13.5,
                      fill=fill, sw=1.6)

    # струмінь обмежень
    f.append(box(0, 110, "Sketchpad · 1963", "Сазерленд, MIT, TX-2", AMBER, 62))
    f.append(box(0, 258, "ThingLab · 1979", "Борнінґ, Smalltalk, PARC", AMBER, 62))
    f.append(box(0, 406, "Ієрархії обмежень · 1987", "обов'язкові й бажані", AMBER, 62))
    f.append(box(0, 554, "DeltaBlue · 1990", "SkyBlue · 1994", AMBER, 62))
    f.append(arrow(250, 172, 250, 254, color=INK, sw=1.6))
    f.append(arrow(250, 320, 250, 402, color=INK, sw=1.6))
    f.append(arrow(250, 468, 250, 550, color=INK, sw=1.6))
    f.append(text(250, 650, "лишилося в дослідженнях", size=12.5, color=MUTED))
    f.append(text(250, 672, "і в розкладачах макета", size=12.5, color=MUTED))

    # струмінь однобічних формул
    f.append(box(1, 258, "Garnet · 1988 · Amulet · 1995", "Маєрс, CMU: однобічні формули", BLUE, 62))
    f.append(box(1, 406, "Cocoa Bindings · 2003", "Apple: KVO, сповіщення", BLUE, 62))
    f.append(box(1, 554, "WPF {Binding} · 2006", "Microsoft: XAML, сповіщення", BLUE, 62))
    f.append(box(1, 690, "Knockout · 2010", "Сандерсон: стеження виконанням", BLUE, 62))
    f.append(box(1, 800, "MobX 2015 · Solid 2018", "Angular signals 2023", BLUE, 62))
    for y0, y1 in [(320, 402), (468, 550), (616, 686), (752, 796)]:
        f.append(arrow(620, y0, 620, y1, color=INK, sw=1.6))
    # Sketchpad → Garnet, у проміжку між колонками
    f.append(arrow(402, 145, 462, 282, color=MUTED, sw=1.6))

    # струмінь клітинок
    f.append(box(2, 110, "LANPAR · 1969", "Пардо й Ландау: порядок за списком", GREEN, 62))
    f.append(box(2, 258, "VisiCalc · 1979", "Бріклін і Френкстон: проходи", GREEN, 62))
    f.append(box(2, 406, "Lotus 1-2-3 · 1983", "«природний порядок», мінімальний перерахунок", GREEN, 62))
    f.append(line(990, 172, 990, 196, color=MUTED, sw=1.6, dash="6 6"))
    f.append(line(990, 232, 990, 254, color=MUTED, sw=1.6, dash="6 6"))
    f.append(text(990, 218, "не успадковано", size=12, color=POS))
    f.append(arrow(990, 320, 990, 402, color=INK, sw=1.6))
    f.append(text(990, 500, "той самий вибір, зроблений", size=12.5, color=MUTED))
    f.append(text(990, 522, "незалежно від інтерфейсів", size=12.5, color=MUTED))

    f.append(rect(60, 812, 470, 62, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    f.append(text(295, 838, "Стрілка — задокументоване успадкування", size=12.5))
    f.append(text(295, 860, "ідеї, а не просто збіг у часі", size=12.5, color=MUTED))

    render(os.path.join(IMG, 'binding-lineage.svg'), W, H, *f,
           title="Три струмені однієї ідеї: оголошений зв'язок від креслення до сигналу")


# ── Фігура 7 (вставка hist): дві розвилки, які проходять усі ─────────────────
def fig_two_forks():
    W, H = 1240, 640
    f = []

    def fork(y, question, left, right):
        f.append(fitbox(430, y, 380, 54, question, size=15, fill=GREY, sw=2, bold=True))
        f.append(arrow(560, y + 54, 300, y + 108, color=INK, sw=1.7))
        f.append(arrow(680, y + 54, 940, y + 108, color=INK, sw=1.7))
        lt, lwho, lcost = left
        rt, rwho, rcost = right
        f.append(fitbox(60, y + 112, 480, 56, lt, size=14.5, fill=AMBER, sw=1.8, bold=True))
        f.append(text(300, y + 194, lwho, size=13))
        f.append(text(300, y + 218, lcost, size=12.5, color=POS))
        f.append(fitbox(700, y + 112, 480, 56, rt, size=14.5, fill=GREEN, sw=1.8, bold=True))
        f.append(text(940, y + 194, rwho, size=13))
        f.append(text(940, y + 218, rcost, size=12.5, color=POS))

    fork(64, "Розвилка перша: скільки боків має зв'язок?",
         ("Двобічний: обмеження без напрямку",
          "Sketchpad, ThingLab, DeltaBlue",
          "ціна: хто саме посунеться — вирішує планувальник"),
         ("Однобічний: формула з одним виходом",
          "Garnet, таблиці, всі чинні рушії прив'язки",
          "ціна: ввід доводиться доробляти окремим шляхом"))

    f.append(line(60, 350, 1180, 350, color=MUTED, sw=1.2, dash="6 8"))

    fork(384, "Розвилка друга: коли рівність відновлено?",
         ("Повторні проходи, доки не заспокоїться",
          "релаксація Sketchpad, VisiCalc",
          "ціна: проміжна неправда й жодної ознаки «готово»"),
         ("Один прохід у порядку залежностей",
          "LANPAR, Lotus 1-2-3, Garnet, сигнали",
          "ціна: граф мусить бути без циклів"))

    render(os.path.join(IMG, 'binding-two-forks.svg'), W, H, *f,
           title="Обидва рази перемогла та сама відповідь: менше загальності — більше визначеності")


if __name__ == "__main__":
    fig_two_homes()
    fig_detect_families()
    fig_glitch_diamond()
    fig_two_phases()
    fig_dynamic_deps()
    fig_lineage()
    fig_two_forks()
    print("OK: two-homes.svg, detect-families.svg, glitch-diamond.svg, "
          "signal-two-phases.svg, signal-dynamic-deps.svg, "
          "binding-lineage.svg, binding-two-forks.svg")
