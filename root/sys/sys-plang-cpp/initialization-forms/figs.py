# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HEAD = "#eef2f7"     # заливка шапки таблиці
SOFT = "#fbfdff"     # звичайна комірка
WARN = "#fdecea"     # там, де мова забороняє / помилка
GOOD = "#eaf5ec"     # там, де мова захищає


# ── Фіг. 1: карта п'яти форм ────────────────────────────────────────────────
# Ідея: форма запису відповідає на два питання — які конструктори потрапляють
# у кандидати і чи дозволене звуження. Таблиця ставить усі п'ять форм поруч,
# щоб видно було: «=» вирізає explicit, фігурні забороняють звуження й дають
# перевагу конструкторові від initializer_list.
def fig_forms_map():
    W, H = 1080, 462
    cols = [(30, 200), (234, 252), (490, 150), (644, 190), (838, 212)]
    header = [
        "запис",
        "кандидати серед\nконструкторів",
        "звуження\nаргументів",
        "конструктор від\ninitializer_list",
        "що ще важливо",
    ]
    rows = [
        ("T x;",
         "типовий\nконструктор",
         "—",
         "не бере\nучасті",
         "скаляр лишається\nневизначеним", SOFT),
        ("T x = a;",
         "лише не-explicit",
         "дозволене",
         "не бере\nучасті",
         "так само працює\nпередача аргументу", SOFT),
        ("T x(a);",
         "усі, разом\nз explicit",
         "дозволене",
         "не бере\nучасті",
         "порожні дужки —\nнайприкріший розбір", WARN),
        ("T x{a};",
         "усі, разом\nз explicit",
         "ЗАБОРОНЕНЕ",
         "має перевагу",
         "T x{} — типовий\nконструктор, не список", GOOD),
        ("T x = {a};",
         "усі; explicit\n— помилка",
         "ЗАБОРОНЕНЕ",
         "має перевагу",
         "ця ж форма — у\nreturn { … }", GOOD),
    ]

    p = []
    y0, hh, rh, gap = 56, 52, 62, 4
    for (cx, cw), htxt in zip(cols, header):
        p.append(fitbox(cx, y0, cw, hh, htxt, size=12, bold=True,
                        fill=HEAD, stroke="#c8d2de", sw=1.2, rx=8))
    for i, r in enumerate(rows):
        ry = y0 + hh + gap + i * (rh + gap)
        fill = r[5]
        for j, (cx, cw) in enumerate(cols):
            cell = r[j]
            bold = (j == 0)
            size = 13 if j == 0 else 12
            col = INK
            if cell == "ЗАБОРОНЕНЕ":
                col = FIELD
            if j == 3 and cell == "має перевагу":
                col = POS
            p.append(fitbox(cx, ry, cw, rh, cell, size=size, bold=bold,
                            fill=fill if j else "#ffffff",
                            stroke="#c8d2de", sw=1.2, rx=8, color=col))
    render(os.path.join(OUT, "init-forms-map.svg"), W, H, *p,
           title="Що вирішує форма запису ініціалізації")


# ── Фіг. 2: дві фази вибору конструктора при фігурних дужках ────────────────
# Ідея: фігурні дужки спершу дивляться ЛИШЕ на конструктори від
# initializer_list; решта отримує шанс тільки коли жоден списочний не придатний.
# Перевірка звуження йде вже після вибору — і відкотити його не може.
# Три приклади показують, де саме зупиняється кожен.
def fig_list_init_phases():
    W, H = 1060, 424
    p = []

    stages = [
        (40, "ФАЗА 1\nкандидати — ЛИШЕ\nконструктори від\ninitializer_list", "#eaf0fd", NEG),
        (380, "ФАЗА 2\nусі конструктори;\nвмикається, лише якщо\nфаза 1 нічого не дала", SOFT, INK),
        (720, "перевірка звуження\nвже ПІСЛЯ вибору;\nвідкоту до фази 1\nне буде", WARN, POS),
    ]
    sy, sh, sw_ = 56, 100, 300
    for x, txt, fill, col in stages:
        p.append(fitbox(x, sy, sw_, sh, txt, size=12, fill=fill,
                        stroke="#c8d2de", sw=1.3, rx=10, color=col))
    p.append(arrow(346, sy + sh / 2, 374, sy + sh / 2))
    p.append(arrow(686, sy + sh / 2, 714, sy + sh / 2))

    lanes = [
        ("vector<int> v{3, 0}",
         "списочний придатний —\nобрано одразу його",
         "[3, 0]\nдва елементи", SOFT),
        ("vector<string> v{10, \"привіт\"}",
         "10 → string неможливо:\nфаза 1 порожня, працює фаза 2",
         "10 однакових\nрядків", SOFT),
        ("Widget{10, true}\nє ctor від initializer_list<bool>",
         "фаза 1 обрала списочний,\nа 10 → bool звужує",
         "помилка\nкомпіляції", WARN),
    ]
    ly, lh = 196, 56
    for i, (code, mid, res, fill) in enumerate(lanes):
        y = ly + i * (lh + 14)
        p.append(fitbox(40, y, 330, lh, code, size=12, bold=True,
                        fill="#ffffff", stroke="#c8d2de", sw=1.2, rx=8))
        p.append(fitbox(410, y, 330, lh, mid, size=12,
                        fill=fill, stroke="#c8d2de", sw=1.2, rx=8))
        p.append(fitbox(780, y, 240, lh, res, size=12, bold=True,
                        fill=fill, stroke="#c8d2de", sw=1.2, rx=8,
                        color=POS if fill == WARN else INK))
        p.append(arrow(374, y + lh / 2, 404, y + lh / 2))
        p.append(arrow(744, y + lh / 2, 774, y + lh / 2))

    render(os.path.join(OUT, "list-init-phases.svg"), W, H, *p,
           title="Фігурні дужки: дві фази вибору конструктора")


# ── Фіг. 3: найприкріший розбір ─────────────────────────────────────────────
# Ідея: один і той самий текст граматика читає двома законними способами, і
# правило мови віддає перевагу оголошенню функції. Показано, у що саме
# перетворюється аргумент — і чим неоднозначність знімають.
def fig_vexing_parse():
    W, H = 1000, 496
    p = []

    p.append(fitbox(330, 52, 340, 44, "Widget w(Clock());", size=16, bold=True,
                    fill="#ffffff", stroke=INK, sw=1.6, rx=8))
    p.append(arrow(430, 98, 300, 146))
    p.append(arrow(570, 98, 700, 146))

    px, py, pw, ph = 40, 150, 420, 146
    p.append(rect(px, py, pw, ph, fill="#f7f8fa", stroke="#c8d2de", sw=1.3, rx=10))
    p.append(text(px + pw / 2, py + 26, "прочитання 1 — визначення об'єкта",
                  size=13, bold=True, color=MUTED))
    p.append(text(px + pw / 2, py + 46, "(відкинуто)", size=12, color=MUTED))
    p.append(mtext(px + 18, py + 76, [
        "w — змінна типу Widget",
        "аргумент — тимчасовий Clock()",
        "саме цього хотів автор коду",
    ], size=12, color=MUTED, anchor="start", lh=1.45))

    qx = 540
    p.append(rect(qx, py, pw, ph, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=10))
    p.append(text(qx + pw / 2, py + 26, "прочитання 2 — оголошення функції",
                  size=13, bold=True, color=NEG))
    p.append(text(qx + pw / 2, py + 46, "(його й обирає мова)", size=12, color=NEG))
    p.append(mtext(qx + 18, py + 76, [
        "w — функція, що повертає Widget",
        "Clock() — безіменний параметр:",
        "«функція без аргументів → Clock»,",
        "а такий параметр стає вказівником",
    ], size=12, color=INK, anchor="start", lh=1.45))

    p.append(fitbox(40, 322, 920, 44,
                    "правило мови: те, що можна прочитати як оголошення, — є оголошенням",
                    size=14, bold=True, fill=WARN, stroke=POS, sw=1.4, rx=10))
    p.append(arrow(750, 320, 750, 300))

    p.append(text(500, 400, "як зняти неоднозначність", size=13, color=MUTED))
    fixes = [("Widget w{};", 40), ("Widget w{Clock{}};", 355), ("Widget w((Clock()));", 670)]
    for txt, x in fixes:
        p.append(fitbox(x, 412, 290, 46, txt, size=14, bold=True,
                        fill=GOOD, stroke=FIELD, sw=1.4, rx=8))

    render(os.path.join(OUT, "vexing-parse.svg"), W, H, *p,
           title="Один рядок, два законні прочитання")


# ── Фіг. 4 (вставка hist): шлях паперів 2003–2008 ───────────────────────────
# Ідея: п'ять років одна лінія паперів вела до «однієї форми для всіх типів»,
# у Беллвю комітет її обрізав, і остаточний механізм прийшов з іншого папера.
def fig_uniform_init_timeline():
    W, H = 1080, 512
    p = []

    row = [
        "N1509 · 18.09.2003\nGeneralized Initializer Lists\nДос Реїс, Страуструп",
        "N1890 · 09.2005\nInitialization and initializers\n«головоломка ініціалізації»",
        "N1919 · 11.12.2005\nInitializer lists\nсинтез: одна форма скрізь",
        "N2100 · 09.09.2006\nInitializer lists (Rev 2.)",
        "N2215 · 08.03.2007\nInitializer lists (Rev. 3)\n+ заборона звуження",
    ]
    bw, bh, by = 196, 92, 46
    for i, t in enumerate(row):
        x = 24 + i * 208
        p.append(fitbox(x, by, bw, bh, t, size=11,
                        fill=SOFT, stroke="#c8d2de", sw=1.2, rx=8))
        if i:
            p.append(arrow(x - 12, by + bh / 2, x - 2, by + bh / 2))

    p.append(arrow(540, by + bh + 4, 540, 176))
    p.append(fitbox(230, 178, 620, 66,
                    "Беллвю, 24.02 – 01.03.2008: N2531 (текст) + N2532 (обґрунтування)\n"
                    "EWG: правила звуження ухвалено, {}-списки як аргументи функцій — відхилено",
                    size=12, fill=WARN, stroke=POS, sw=1.4, rx=10))

    p.append(arrow(400, 248, 280, 292))
    p.append(arrow(680, 248, 800, 292))

    p.append(fitbox(40, 296, 480, 104,
                    "звужена пропозиція\n"
                    "однорідність уже неповна: у виклику функції\n"
                    "голий {}-список писати не можна",
                    size=12, fill="#f7f8fa", stroke="#c8d2de", sw=1.2, rx=10,
                    color=MUTED))
    p.append(fitbox(560, 296, 480, 104,
                    "N2640 · 16.05.2008 — Меррілл (Red Hat), Вандевоорде (EDG)\n"
                    "інший механізм: {}-список — це перетворення,\n"
                    "звуження перевіряють ПІСЛЯ вибору перевантаження",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=10))

    p.append(arrow(800, 404, 640, 442))
    p.append(fitbox(230, 446, 620, 50,
                    "Софія-Антиполіс, 8–14.06.2008: текст N2672 внесено в чорновик C++0x",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=1.4, rx=10))

    render(os.path.join(OUT, "uniform-init-timeline.svg"), W, H, *p,
           title="Шлях однорідної ініціалізації: 2003–2008")


# ── Фіг. 5 (вставка proj): тихе перехоплення викликів ───────────────────────
# Ідея: місце виклику не змінюють жодним символом, у клас додають один
# конструктор від initializer_list — і рядок із фігурними дужками починає
# викликати інший конструктор. Круглі дужки лишаються на місці.
def fig_ctor_hijack():
    W, H = 1020, 442
    p = []

    p.append(text(510, 52, "місце виклику — не змінено жодного символу",
                  size=12, color=MUTED))
    p.append(fitbox(330, 62, 360, 72, "Grid a{3, 4};\nGrid b(3, 4);",
                    size=15, bold=True, fill="#ffffff", stroke=INK, sw=1.6, rx=8))

    p.append(arrow(430, 140, 300, 182))
    p.append(arrow(590, 140, 720, 182))

    p.append(rect(40, 186, 440, 152, fill="#f7f8fa", stroke="#c8d2de", sw=1.3, rx=10))
    p.append(text(260, 212, "збірка 1: у класі лише Grid(int, int)",
                  size=13, bold=True, color=MUTED))
    p.append(fitbox(58, 228, 404, 44, "a  →  Grid(int, int)      сітка 3 × 4",
                    size=12, fill=SOFT, stroke="#c8d2de", sw=1.1, rx=7))
    p.append(fitbox(58, 280, 404, 44, "b  →  Grid(int, int)      сітка 3 × 4",
                    size=12, fill=SOFT, stroke="#c8d2de", sw=1.1, rx=7))

    p.append(rect(540, 186, 440, 152, fill="#fdf6f5", stroke=POS, sw=1.5, rx=10))
    p.append(text(760, 212, "збірка 2: додано Grid(initializer_list<int>)",
                  size=13, bold=True, color=POS))
    p.append(fitbox(558, 228, 404, 44, "a  →  initializer_list<int>      список [3, 4]",
                    size=12, bold=True, fill=WARN, stroke=POS, sw=1.3, rx=7, color=POS))
    p.append(fitbox(558, 280, 404, 44, "b  →  Grid(int, int)      сітка 3 × 4",
                    size=12, fill=SOFT, stroke="#c8d2de", sw=1.1, rx=7))

    p.append(fitbox(140, 364, 740, 46,
                    "фігурні дужки перекинуло мовчки — круглі лишилися на місці",
                    size=14, bold=True, fill=GOOD, stroke=FIELD, sw=1.4, rx=10))

    render(os.path.join(OUT, "ctor-hijack.svg"), W, H, *p,
           title="Той самий рядок виклику, два різні конструктори")


fig_forms_map()
fig_list_init_phases()
fig_vexing_parse()
fig_uniform_init_timeline()
fig_ctor_hijack()
print("ok")
