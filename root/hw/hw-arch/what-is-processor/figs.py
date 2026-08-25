# -*- coding: utf-8 -*-
"""Фігури до теми «Що таке процесор» (машина, що виконує інструкції).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
GREEN_BG = "#eaf6ee"
BLUE_BG  = "#eaf0fd"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


# ── 1. Процесор виконує інструкції по одній ──────────────────────────────────
def fig_what():
    W, H = 820, 360
    f = []
    # пам'ять із програмою
    f.append(rect(60, 90, 220, 210, fill="#f4f7f4", stroke=FIELD, sw=2))
    f.append(text(170, 114, "ПАМ'ЯТЬ (програма)", size=12, color=FIELD, bold=True))
    rows = [("0x10", "завантаж 7", False), ("0x11", "додай", True),
            ("0x12", "порівняй", False), ("0x13", "перейти, якщо…", False),
            ("0x14", "запиши", False)]
    ry = 130
    for addr, val, hot in rows:
        f.append(rect(76, ry, 188, 30, fill=(RED_BG if hot else BG),
                      stroke=(POS if hot else FIELD), sw=(2 if hot else 1.2)))
        f.append(text(88, ry + 20, addr, size=10, color=MUTED, anchor="start", bold=True))
        f.append(text(252, ry + 20, val, size=11, color=INK, anchor="end", bold=hot))
        ry += 34
    f.append(text(170, 296, "← поточна команда", size=10, color=POS, bold=True))
    # стрілка до процесора
    f.append(arrow(286, 178, 360, 196, color=INK, sw=2.2))
    # процесор
    proc, _, _ = textbox(470, 196, "ПРОЦЕСОР\nбере команду\nй виконує дію\nдалі — наступна",
                         size=12, fill=RED_BG, stroke=POS, sw=2, min_w=180)
    f.append(proc)
    # дрібна дія
    f.append(arrow(560, 196, 632, 196, color=FIELD, sw=2.2))
    act, _, _ = textbox(710, 196, "крихітна\nдія: A + B", size=12, fill=GREEN_BG,
                        stroke=FIELD, sw=1.8, min_w=130)
    f.append(act)
    # підпис-висновок
    f.append(text(W / 2, 330, "читає чергове число-команду, робить означену дію — і одразу береться за наступну",
                  size=11, color=MUTED, italic=True))
    out("what.svg", W, H, *f,
        title="Процесор виконує інструкції по одній, без упину")


# ── 2. Інструкція — один крихітний наказ ─────────────────────────────────────
def fig_instruction():
    W, H = 820, 360
    f = []
    items = [
        ("завантаж число", "поклади значення в робочу комірку", NEG),
        ("додай / відніми", "склади чи відніми два числа", FIELD),
        ("порівняй", "більше? менше? рівно?", AMBER),
        ("перейди (стрибок)", "роби далі не наступну, а іншу команду", POS),
        ("запиши / прочитай", "перенеси число між процесором і пам'яттю", INK),
    ]
    y = 80
    for name, desc, col in items:
        f.append(rect(150, y, 250, 42, fill="#fafafa", stroke=col, sw=1.8))
        f.append(text(275, y + 27, name, size=13, color=col, bold=True))
        f.append(text(420, y + 27, desc, size=12, color=INK, anchor="start"))
        y += 52
    f.append(text(W / 2, 348, "кілька десятків таких примітивів — і нічого більше; велике зібране з довгих ланцюгів дрібного",
                  size=11, color=MUTED, italic=True))
    out("instruction.svg", W, H, *f,
        title="Інструкція — один крихітний, точно означений наказ")


# ── 3. Програма — впорядкований список ───────────────────────────────────────
def fig_program():
    W, H = 820, 470
    f = []
    prog = [
        ("0", "завантаж лічильник = 0"),
        ("1", "завантаж суму = 0"),
        ("2", "додай число до суми"),
        ("3", "збільш лічильник"),
        ("4", "порівняй лічильник з 10"),
        ("5", "якщо менше — перейди до 2"),
        ("6", "запиши суму в пам'ять"),
        ("7", "стоп"),
    ]
    x0, y0, rw = 250, 86, 300
    rh = 36
    y = y0
    for addr, val in prog:
        hot = addr in ("2", "3", "4", "5")
        f.append(rect(x0, y, rw, rh, fill=("#f4f7f4" if hot else BG),
                      stroke=("#1b1b1b"), sw=1.4))
        f.append(text(x0 + 14, y + 24, addr, size=11, color=MUTED, anchor="start", bold=True))
        f.append(text(x0 + 56, y + 24, val, size=12, color=INK, anchor="start", bold=True))
        y += rh
    # стрілка «по порядку»
    f.append(arrow(x0 - 18, y0 + 6, x0 - 18, y - 6, color=INK, sw=2))
    f.append(text(x0 - 26, (y0 + y) / 2 - 8, "по", size=10, color=INK, anchor="end", bold=True))
    f.append(text(x0 - 26, (y0 + y) / 2 + 6, "порядку", size=10, color=INK, anchor="end", bold=True))
    # дуга стрибка: з рядка 5 назад до рядка 2
    y5 = y0 + 5 * rh + rh / 2
    y2 = y0 + 2 * rh + rh / 2
    f.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" '
             'stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (x0 + rw, y5, x0 + rw + 70, (y2 + y5) / 2, x0 + rw, y2, POS))
    f.append(text(x0 + rw + 80, (y2 + y5) / 2 - 6, "стрибок", size=11, color=POS, anchor="start", bold=True))
    f.append(text(x0 + rw + 80, (y2 + y5) / 2 + 10, "(цикл)", size=10, color=POS, anchor="start"))
    f.append(text(W / 2, 450, "рядки 2–5 повторюються завдяки стрибку — з купки наказів уже постає алгоритм",
                  size=11, color=MUTED, italic=True))
    out("program.svg", W, H, *f,
        title="Програма — впорядкований список інструкцій у пам'яті")


# ── 4. Дурний, та швидкий і слухняний ────────────────────────────────────────
def fig_dumb_fast():
    W, H = 820, 360
    f = []
    # ліворуч — хибна уява
    f.append(rect(50, 80, 340, 220, fill=RED_BG, stroke=POS, sw=1.6))
    f.append(text(220, 106, "Що часто УЯВЛЯЮТЬ", size=13, color=POS, bold=True))
    f.append(circle(220, 168, 42, fill=BG, stroke=POS, sw=2))
    f.append(text(220, 164, "«мозок»", size=13, color=POS, bold=True))
    f.append(text(220, 184, "що думає", size=11, color=MUTED))
    f.append(line(188, 142, 252, 196, color=POS, sw=3))   # перекреслення
    f.append(text(220, 248, "розуміє, має здоровий глузд", size=11, color=INK))
    f.append(text(220, 280, "✘ це не так", size=12, color=POS, bold=True))
    # праворуч — як є
    f.append(rect(430, 80, 340, 220, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    f.append(text(600, 106, "Що Є НАСПРАВДІ", size=13, color=FIELD, bold=True))
    lines = [
        "виконавець, що робить",
        "буквально написане:",
        "• не розуміє сенсу команд",
        "• не сумнівається й не виправляє",
        "• дурний наказ зробить так само",
        "  старанно, як і розумний",
        "• зате мільярди кроків за секунду",
    ]
    ly = 136
    for i, ln in enumerate(lines):
        anc = "middle" if i < 2 else "start"
        x = 600 if i < 2 else 452
        f.append(text(x, ly, ln, size=11.5, color=INK, anchor=anc, bold=(i < 2)))
        ly += 22
    f.append(text(W / 2, 340, "баг — не «помилка процесора»: він бездоганно зробив саме те, що ви написали",
                  size=11, color=MUTED, italic=True))
    out("dumb-fast.svg", W, H, *f,
        title="Процесор не розумний — він дурний, та швидкий і слухняний")


# ── 5. Складність із простоти × швидкість ────────────────────────────────────
def fig_emergence():
    W, H = 820, 360
    f = []
    one, _, _ = textbox(160, 175, "ОДИН крок\nнапр. A + B\nтривіально:\nшколяр зробить",
                        size=12, fill=GREEN_BG, stroke=FIELD, sw=1.8, min_w=200)
    f.append(one)
    f.append(arrow(266, 175, 336, 175, color=INK, sw=2.4))
    mul, _, _ = textbox(410, 175, "× мільярди\nза секунду", size=13, fill=AMBER_BG,
                        stroke=AMBER, sw=1.8, min_w=150)
    f.append(mul)
    f.append(arrow(486, 175, 556, 175, color=INK, sw=2.4))
    res, _, _ = textbox(670, 175, "= усе, що бачимо\n3D-графіка · відео\nкерування дроном\nрозпізнавання, ШІ",
                        size=12, fill=BLUE_BG, stroke=NEG, sw=1.8, min_w=200)
    f.append(res)
    f.append(text(W / 2, 290, "роботу процесора за ОДНУ секунду людина по кроку щосекунди робила б десятки років",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 318, "«розум» машини — це не розумний крок, а безліч простих кроків шалено швидко",
                  size=11, color=MUTED, italic=True))
    out("emergence.svg", W, H, *f,
        title="Звідки складність: тривіальний крок × нечувана швидкість")


# ── 6. Аналогія: надшвидкий слухняний клерк ──────────────────────────────────
def fig_clerk():
    W, H = 820, 400
    f = []
    # клерк зі списком
    f.append(circle(140, 140, 13, fill=BG, stroke=INK, sw=2.4))
    f.append('<path d="M120,172 Q140,150 160,172" fill="none" stroke="%s" stroke-width="2.4"/>' % INK)
    f.append(rect(96, 186, 90, 70, fill="#fafafa", stroke=INK, sw=1.6))
    for i in range(4):
        yy = 202 + i * 14
        f.append(line(108, yy, 174, yy, color=MUTED, sw=1.4))
    f.append(text(140, 276, "клерк зі списком", size=11, color=MUTED, bold=True))
    # де точна
    f.append(rect(250, 80, 520, 130, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    f.append(text(510, 104, "У чому аналогія точна", size=13, color=FIELD, bold=True))
    ok = [
        "• виконує накази строго по порядку, один за одним",
        "• кожен наказ простий і однозначний",
        "• не імпровізує — робить рівно те, що в списку",
    ]
    oy = 134
    for ln in ok:
        f.append(text(268, oy, ln, size=11.5, color=INK, anchor="start"))
        oy += 24
    # де ламається
    f.append(rect(250, 224, 520, 134, fill=RED_BG, stroke=POS, sw=1.6))
    f.append(text(510, 248, "Де аналогія ламається", size=13, color=POS, bold=True))
    bad = [
        "• живий клерк розуміє сенс і помітив би абсурд —",
        "  процесор не розуміє нічого",
        "• для нього команда — просто число, що вмикає дію",
        "• хибний наказ зробить так само ретельно → звідси баги",
    ]
    by = 276
    for ln in bad:
        f.append(text(268, by, ln, size=11.5, color=INK, anchor="start"))
        by += 22
    f.append(text(W / 2, 388, "образ клерка — щоб уявити роботу; «без розуміння» — щоб не чекати здорового глузду",
                  size=11, color=MUTED, italic=True))
    out("clerk.svg", W, H, *f,
        title="Точна аналогія: надшвидкий, бездоганно слухняний клерк")


# ════════════ ВСТАВКА: Беббідж і Ада Лавлейс ════════════════════════════════

def _timeline(name, title, subtitle, nodes):
    """Спільний макет вертикальної стрічки часу (нодами: (year, head, lines, hot))."""
    W = 900
    top = 96
    step = 96
    H = top + step * len(nodes) + 30
    f = []
    f.append(text(W / 2, 58, subtitle, size=12, color=MUTED, italic=True))
    ax = 250
    f.append(line(ax, top - 6, ax, top + step * (len(nodes) - 1) + 40, color=MUTED, sw=3))
    for i, (year, head, lines, hot) in enumerate(nodes):
        cy = top + i * step
        if hot:
            f.append(circle(ax, cy, 10, fill=BG, stroke=POS, sw=3.2))
            f.append(circle(ax, cy, 4.5, fill=POS, stroke=POS, sw=1))
            hc = POS
        else:
            f.append(circle(ax, cy, 7, fill=BG, stroke=INK, sw=2.6))
            hc = INK
        f.append(text(ax - 22, cy + 5, year, size=12, color=MUTED, anchor="end", bold=True))
        f.append(text(ax + 26, cy - 3, head, size=15, color=hc, anchor="start", bold=True))
        ly = cy + 18
        for ln in lines:
            f.append(text(ax + 26, ly, ln, size=12, color=INK, anchor="start", italic=True))
            ly += 17
    out(name, W, H, *f, title=title)


def fig_bl_timeline():
    _timeline(
        "bl-timeline.svg",
        "За століття до електроніки: машина, що мала виконувати програму",
        "Беббідж задумав механічний «процесор», а Лавлейс написала для нього перший алгоритм",
        [
            ("1822", "Різницева машина",
             ["Механічний обчислювач таблиць методом різниць (самі додавання);",
              "уряд фінансує — недобудовано"], False),
            ("1834", "Аналітична машина",
             ["Задум універсальної машини: «Млин» + «Склад» + перфокарти +",
              "розгалуження й цикли"], True),
            ("1843", "Нотатки Ади Лавлейс",
             ["Переклад статті + власні Нотатки: перший опублікований алгоритм",
              "(числа Бернуллі) і бачення «машини символів»"], False),
            ("XIX ст.", "Не збудовано",
             ["Надскладно для механіки тих часів, бракло коштів —",
              "геніальний задум лишився на папері"], False),
            ("1991", "Справдження",
             ["Музей науки в Лондоні будує Різницеву машину №2 за кресленнями —",
              "і вона працює"], False),
        ])


def fig_bl_analytical():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 54, "Беббідж розділив обчислення й пам'ять — рівно як у процесорі",
                  size=12, color=MUTED, italic=True))
    # Склад
    f.append(rect(70, 110, 230, 220, fill=GREEN_BG, stroke=FIELD, sw=2))
    f.append(text(185, 134, "«СКЛАД» (Store)", size=14, color=FIELD, bold=True))
    f.append(text(185, 152, "пам'ять чисел", size=11, color=MUTED, italic=True))
    ry = 166
    for i in range(5):
        f.append(rect(92, ry, 186, 24, fill=BG, stroke=FIELD, sw=1.4))
        f.append(text(185, ry + 17, "число %d  ·  50 цифр" % (i + 1), size=11, color=INK))
        ry += 30
    f.append(text(185, 324, "до ~1000 чисел", size=10, color=MUTED, italic=True))
    # Млин
    f.append(rect(600, 110, 230, 220, fill=RED_BG, stroke=POS, sw=2))
    f.append(text(715, 134, "«МЛИН» (Mill)", size=14, color=POS, bold=True))
    f.append(text(715, 152, "обчислювальний пристрій", size=11, color=MUTED, italic=True))
    f.append(circle(690, 232, 34, fill=BG, stroke=POS, sw=2))
    f.append(circle(690, 232, 14, fill="none", stroke=POS, sw=1.6))
    f.append(circle(758, 256, 24, fill=BG, stroke=POS, sw=2))
    f.append(circle(758, 256, 10, fill="none", stroke=POS, sw=1.6))
    f.append(text(715, 312, "+ − × ÷ над числами", size=11.5, color=INK, bold=True))
    # обмін
    f.append(arrow(305, 200, 595, 200, color=INK, sw=2.4))
    f.append(arrow(595, 250, 305, 250, color=INK, sw=2.4))
    f.append(text(450, 192, "числа туди", size=10.5, color=INK))
    f.append(text(450, 270, "результат назад", size=10.5, color=INK))
    # перфокарти
    f.append(text(450, 360, "ПЕРФОКАРТИ — програма (послідовність операцій)",
                  size=11.5, color=AMBER, bold=True))
    cardx = 372
    for _ in range(5):
        f.append('<path d="M%d,374 L%d,374 L%d,414 L%d,414 L%d,384 Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (cardx, cardx + 20, cardx + 20, cardx - 10, cardx - 10, AMBER_BG, AMBER))
        f.append(circle(cardx + 2, 384, 2.6, fill=AMBER, stroke=AMBER, sw=0))
        f.append(circle(cardx + 6, 397, 2.6, fill=AMBER, stroke=AMBER, sw=0))
        cardx += 38
    f.append(arrow(450, 350, 450, 320, color=INK, sw=2))
    f.append(text(450, 444, "програма лежала на картках, окремо від чисел у «Складі» — це радше Гарвардська ідея",
                  size=10.5, color=MUTED, italic=True))
    out("bl-analytical.svg", W, H, *f,
        title="Аналітична машина: «Млин», «Склад» і перфокарти")


def fig_bl_jacquard():
    W, H = 860, 400
    f = []
    f.append(text(W / 2, 54, "Жаккар (1804) керував візерунком тканини перфокартами; Беббідж узяв ту саму ідею",
                  size=11.5, color=MUTED, italic=True))
    # верстат із сіткою дірок
    f.append(rect(70, 96, 200, 150, fill="#fafafa", stroke=INK, sw=1.8))
    f.append(text(170, 120, "верстат Жаккара", size=12.5, color=INK, bold=True))
    import random
    random.seed(7)
    gy = 134
    for r in range(5):
        gx = 92
        for c in range(8):
            on = random.random() < 0.3
            f.append(rect(gx, gy, 16, 14, fill=(NEG if on else "#eef4ff"), stroke=MUTED, sw=0.8))
            gx += 20
        gy += 18
    f.append(text(170, 238, "перфокартки → візерунок", size=10, color=MUTED))
    f.append(arrow(280, 170, 350, 170, color=INK, sw=2.2))
    # колода карток
    cardx = 372
    for _ in range(5):
        f.append('<path d="M%d,126 L%d,126 L%d,216 L%d,216 L%d,136 Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (cardx, cardx + 22, cardx + 22, cardx - 10, cardx - 10, AMBER_BG, AMBER))
        f.append(circle(cardx + 2, 134, 2.6, fill=AMBER, stroke=AMBER, sw=0))
        f.append(circle(cardx + 8, 172, 2.6, fill=AMBER, stroke=AMBER, sw=0))
        cardx += 40
    f.append(text(460, 236, "колода карток = послідовність наказів", size=10.5, color=AMBER, bold=True))
    f.append(arrow(590, 170, 660, 170, color=INK, sw=2.2))
    am, _, _ = textbox(745, 170, "Аналітична\nмашина\nвиконує по картці",
                       size=12, fill=RED_BG, stroke=POS, sw=1.8, min_w=160)
    f.append(am)
    # цитата
    f.append(rect(60, 290, 740, 88, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    f.append(text(430, 316, "Лавлейс: «Аналітична машина тче алгебраїчні візерунки так само,",
                  size=12, color=INK, bold=True))
    f.append(text(430, 338, "як верстат Жаккара тче квіти й листя».", size=12, color=INK, bold=True))
    f.append(text(430, 362, "Колода карток — це і є програма: послідовність інструкцій одна за одною.",
                  size=11, color=MUTED, italic=True))
    out("bl-jacquard.svg", W, H, *f,
        title="Звідки перфокарти: ткацький верстат Жаккара")


def fig_bl_bernoulli():
    W, H = 900, 420
    f = []
    f.append(text(W / 2, 54, "таблиця операцій для чисел Бернуллі — її вважають першою «програмою» (схема)",
                  size=11.5, color=MUTED, italic=True))
    cols = [(90, "№"), (250, "операція"), (470, "над чим"), (700, "→ результат")]
    # шапка
    f.append(rect(70, 84, 760, 30, fill="#eef2f7", stroke=INK, sw=1.4))
    for cx, h in cols:
        f.append(text(cx, 104, h, size=12.5, color=INK, bold=True))
    rows = [
        ("1", "×", "v₂ × v₃", "v₄", False),
        ("2", "−", "v₄ − 1", "v₅", False),
        ("3", "÷", "v₅ ÷ v₆", "v₇", False),
        ("4", "+", "v₇ + v₈", "v₈", False),
        ("5", "×", "v₁₁ × v₁₃", "v₁₂", False),
        ("6", "повторити", "цикл по індексу", "наступне Bₙ", True),
    ]
    y = 114
    for n, op, over, res, hot in rows:
        f.append(rect(70, y, 760, 32, fill=(RED_BG if hot else (BG if int(n) % 2 else "#f8f9fb")),
                      stroke=(POS if hot else MUTED), sw=(1.4 if hot else 1)))
        f.append(text(90, y + 21, n, size=12, color=MUTED, bold=True))
        f.append(text(250, y + 21, op, size=13, color=(POS if hot else NEG), bold=True))
        f.append(text(470, y + 21, over, size=12, color=INK))
        f.append(text(700, y + 21, res, size=12, color=FIELD, bold=True))
        y += 32
    f.append(text(W / 2, 346, "послідовність операцій із циклом — справжня програма, а не формула; Лавлейс",
                  size=11, color=INK, bold=True))
    f.append(text(W / 2, 366, "ще й знайшла та виправила помилку у викладках Беббіджа — праця була спільна,",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 386, "та саме вона це опублікувала й осмислила як алгоритм; титул «першої» — дискусійний",
                  size=11, color=MUTED, italic=True))
    out("bl-bernoulli.svg", W, H, *f,
        title="Нотатка G Лавлейс: перший опублікований алгоритм")


def fig_bl_vision():
    W, H = 900, 420
    f = []
    f.append(text(W / 2, 54, "Беббідж бачив швидку лічбу; Лавлейс перша зрозуміла, що машина оперує символами",
                  size=11.5, color=MUTED, italic=True))
    # калькулятор
    f.append(rect(70, 86, 360, 150, fill=BLUE_BG, stroke=NEG, sw=1.6))
    f.append(text(250, 112, "Беббідж бачив КАЛЬКУЛЯТОР", size=12.5, color=NEG, bold=True))
    f.append(text(250, 142, "машину, що швидко й безпомилково", size=11.5, color=INK))
    f.append(text(250, 162, "рахує числа — таблиці, обчислення", size=11.5, color=INK))
    f.append(text(250, 190, "(велика, та все ж лише арифметика)", size=10.5, color=MUTED, italic=True))
    f.append(text(250, 214, "123 + 456 = 579", size=12, color=INK, bold=True))
    # машина символів
    f.append(rect(470, 86, 360, 150, fill=RED_BG, stroke=POS, sw=1.8))
    f.append(text(650, 112, "Лавлейс — МАШИНУ СИМВОЛІВ", size=12, color=POS, bold=True))
    f.append(text(650, 142, "якщо числа можуть позначати ноти,", size=11.5, color=INK))
    f.append(text(650, 162, "букви, що завгодно — машина за", size=11.5, color=INK))
    f.append(text(650, 182, "правилами творитиме музику, графіку…", size=11.5, color=INK))
    f.append(text(650, 212, "♪ ♫  ✎  ∑  → не лише лічба", size=12.5, color=POS, bold=True))
    # заперечення Лавлейс
    f.append(rect(70, 254, 760, 58, fill=AMBER_BG, stroke=AMBER, sw=1.6))
    f.append(text(450, 278, "Та вона ж застерегла: «Машина не претендує породжувати нічого нового —",
                  size=11.5, color=INK, bold=True))
    f.append(text(450, 298, "вона робить лише те, що ми вміємо їй наказати» — «заперечення Лавлейс».",
                  size=11.5, color=INK, bold=True))
    # чесно про заслуги
    f.append(rect(70, 330, 760, 70, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    f.append(text(450, 354, "Беббідж спроєктував машини й розробляв обчислення; Лавлейс написала Нотатки,",
                  size=11, color=INK, bold=True))
    f.append(text(450, 374, "опублікувала перший алгоритм і першою осягнула, що це машина загального призначення.",
                  size=11, color=INK, bold=True))
    f.append(text(450, 393, "Обидва внески справжні й різні — велика ідея є праця кількох рук.",
                  size=10.5, color=MUTED, italic=True))
    out("bl-vision.svg", W, H, *f,
        title="Стрибок думки Лавлейс: не калькулятор, а машина символів")


# ════════════ ВСТАВКА: фон Нейман і збережена програма ══════════════════════

def fig_vn_timeline():
    _timeline(
        "vn-timeline.svg",
        "Ланцюг до головної ідеї: як комп'ютер став універсальним",
        "від машин, що вміли одне, до машини, яку перепрограмовуєш, заклавши інші числа",
        [
            ("давні", "рахівниця → Паскаль → Беббідж",
             ["Кожна вміла одне: зроблена під одну задачу;",
              "змінити її — перебудувати залізо"], False),
            ("1945", "ENIAC",
             ["Перша велика електронна — швидка; та «програмування» =",
              "перемикати сотні дротів і тумблерів днями"], False),
            ("питання", "а якщо…?",
             ["Що, як інструкції зберігати в пам'яті як звичайні числа —",
              "поряд із даними?"], False),
            ("1945", "«First Draft» — фон Нейман",
             ["Перший ясний опис збереженої програми;",
              "саме його ім'я закріпилось за архітектурою"], True),
            ("1948", "Манчестерський «Baby»",
             ["Перша машина, що реально виконала збережену програму",
              "(Вільямс і Кілберн)"], False),
            ("1949", "EDSAC",
             ["Перша практична машина зі збереженою програмою",
              "(Вілкс, Кембридж)"], False),
            ("донині", "ПК · телефон · ESP32",
             ["Майже кожен комп'ютер і досі —",
              "машина зі збереженою програмою"], False),
        ])


def fig_vn_rewiring():
    W, H = 900, 420
    f = []
    f.append(text(W / 2, 54, "ENIAC доводилося перекомутовувати; збережену програму змінюєш просто іншими числами",
                  size=11.5, color=MUTED, italic=True))
    # ENIAC — комутація
    f.append(rect(60, 86, 360, 250, fill="#fafafa", stroke=INK, sw=1.8))
    f.append(text(240, 110, "ENIAC: програма = КОМУТАЦІЯ", size=12.5, color=POS, bold=True))
    pts = []
    gy = 140
    for r in range(4):
        gx = 100
        row = []
        for c in range(7):
            f.append(circle(gx, gy, 4, fill=BG, stroke=MUTED, sw=1.6))
            row.append((gx, gy))
            gx += 42
        pts.append(row)
        gy += 34
    wires = [((0, 0), (1, 2), POS), ((0, 3), (3, 6), NEG),
             ((1, 1), (3, 3), FIELD), ((2, 5), (1, 3), AMBER), ((2, 0), (0, 6), INK)]
    for (r1, c1), (r2, c2), col in wires:
        x1, y1 = pts[r1][c1]
        x2, y2 = pts[r2][c2]
        f.append('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (x1, y1, (x1 + x2) / 2, max(y1, y2) + 40, x2, y2, col))
    f.append(text(240, 322, "змінити задачу → ДНІ перетикання дротів вручну", size=10.5, color=INK, bold=True))
    # збережена програма
    f.append(rect(480, 86, 360, 250, fill=GREEN_BG, stroke=FIELD, sw=1.8))
    f.append(text(660, 110, "Збережена програма = ЧИСЛА в пам'яті", size=12, color=FIELD, bold=True))
    cells = [("01101110", "інструкція", FIELD), ("10010001", "інструкція", FIELD),
             ("00111010", "інструкція", FIELD), ("01000101", "дані", NEG),
             ("11001000", "дані", NEG)]
    cy = 132
    for bits, lab, col in cells:
        f.append(rect(560, cy, 130, 28, fill=(GREEN_BG if col == FIELD else BLUE_BG), stroke=col, sw=1.6))
        f.append(text(625, cy + 19, bits, size=12.5, color=INK, bold=True))
        f.append(text(700, cy + 19, lab, size=10, color=col, anchor="start", bold=True))
        cy += 34
    f.append(arrow(520, 150, 520, 296, color=FIELD, sw=2.4))
    f.append(text(512, 226, "інші", size=10, color=FIELD, anchor="end", bold=True))
    f.append(text(660, 322, "змінити задачу → СЕКУНДИ: просто інші числа", size=10.5, color=INK, bold=True))
    f.append(text(W / 2, 366, "та сама пам'ять тримає й інструкції, й дані — бо біти не мають вродженого сенсу:",
                  size=11, color=INK, bold=True))
    f.append(text(W / 2, 388, "одне число можна прочитати і як дані, і як команду — звідси універсальність",
                  size=10.5, color=MUTED, italic=True))
    out("vn-rewiring.svg", W, H, *f,
        title="Дві відповіді на питання «як змінити, що робить машина»")


def fig_vn_architecture():
    W, H = 900, 460
    f = []
    f.append(text(W / 2, 54, "програма й дані живуть в одній пам'яті; процесор по черзі вибирає команди й виконує",
                  size=11.5, color=MUTED, italic=True))
    # пам'ять
    f.append(rect(60, 104, 250, 234, fill=GREEN_BG, stroke=FIELD, sw=2))
    f.append(text(185, 128, "ПАМ'ЯТЬ", size=15, color=FIELD, bold=True))
    f.append(text(185, 146, "програма + дані РАЗОМ", size=10.5, color=MUTED, italic=True))
    cells = [("0x00", "інструкція", FIELD), ("0x01", "інструкція", FIELD),
             ("0x02", "дані", NEG), ("0x03", "інструкція", FIELD), ("0x04", "дані", NEG)]
    cy = 160
    for addr, lab, col in cells:
        f.append(rect(78, cy, 214, 28, fill=(GREEN_BG if col == FIELD else BLUE_BG), stroke=col, sw=1.5))
        f.append(text(92, cy + 19, addr, size=11, color=MUTED, anchor="start", bold=True))
        f.append(text(200, cy + 19, lab, size=11.5, color=col, bold=True))
        cy += 34
    # процесор
    f.append(rect(590, 104, 250, 234, fill=RED_BG, stroke=POS, sw=2))
    f.append(text(715, 128, "ПРОЦЕСОР (CPU)", size=15, color=POS, bold=True))
    f.append(rect(610, 150, 210, 80, fill=BG, stroke=INK, sw=1.7))
    f.append(text(715, 176, "Пристрій керування", size=12.5, color=INK, bold=True))
    f.append(text(715, 194, "(Control Unit)", size=10, color=MUTED))
    f.append(text(715, 214, "вибирає й декодує команди", size=10, color=MUTED, italic=True))
    f.append(rect(610, 244, 210, 80, fill=BG, stroke=INK, sw=1.7))
    f.append(text(715, 270, "АЛП (ALU)", size=12.5, color=INK, bold=True))
    f.append(text(715, 288, "арифметика й логіка", size=10.5, color=MUTED))
    f.append(text(715, 308, "+ регістри — робочі комірки", size=10, color=MUTED, italic=True))
    # шина
    f.append(arrow(312, 190, 588, 190, color=INK, sw=2.6))
    f.append(arrow(588, 250, 312, 250, color=INK, sw=2.6))
    f.append(text(450, 182, "ШИНА", size=12.5, color=INK, bold=True))
    f.append(text(450, 224, "адреси · дані · керування", size=11, color=INK))
    f.append(text(450, 270, "один спільний канал", size=10.5, color=POS, bold=True))
    # I/O
    io, _, _ = textbox(450, 392, "Ввід / Вивід (I/O)\nклавіатура, екран, давачі…",
                       size=11, fill=AMBER_BG, stroke=AMBER, sw=1.8, min_w=200)
    f.append(io)
    f.append(line(450, 256, 450, 368, color=MUTED, sw=1.6, dash="4 3"))
    f.append(text(W / 2, 446, "це й є «архітектура фон Неймана»: процесор читає числа з пам'яті й тлумачить їх як накази",
                  size=10.5, color=MUTED, italic=True))
    out("vn-architecture.svg", W, H, *f,
        title="Архітектура фон Неймана: пам'ять, процесор і одна спільна шина")


def fig_vn_parents():
    W, H = 900, 420
    f = []
    f.append(text(W / 2, 54, "задум, теорія, залізо й перший опис — це різні внески; історія стиснула їх в одне ім'я",
                  size=11.5, color=MUTED, italic=True))
    cards = [
        ("Алан Тюрінг", "1936", "ТЕОРІЯ", NEG,
         ["Універсальна машина: одна", "машина здатна виконати", "будь-яке обчислення"]),
        ("Еккерт і Моклі", "1943–45", "ЗАЛІЗО", AMBER,
         ["Збудували ENIAC; ідея", "зберігати програму", "в пам'яті на лініях затримки"]),
        ("Джон фон Нейман", "1945", "ОПИС", POS,
         ["«First Draft»: перший", "ясний виклад архітектури —", "його ім'я й закріпилось"]),
        ("«Baby» й EDSAC", "1948–49", "ВТІЛЕННЯ", FIELD,
         ["Британські машини, що", "першими реально виконали", "збережену програму"]),
    ]
    cw, gap = 200, 16
    x0 = (W - 4 * cw - 3 * gap) / 2
    for i, (who, yr, badge, col, lines) in enumerate(cards):
        x = x0 + i * (cw + gap)
        hot = (badge == "ОПИС")
        f.append(rect(x, 86, cw, 274, fill=(RED_BG if hot else "#fafafa"),
                      stroke=col, sw=(2.2 if hot else 1.6)))
        f.append(circle(x + cw / 2, 124, 12, fill=BG, stroke=col, sw=2.4))
        f.append('<path d="M%.0f,154 Q%.0f,134 %.0f,154" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (x + cw / 2 - 18, x + cw / 2, x + cw / 2 + 18, col))
        f.append(text(x + cw / 2, 196, who, size=13.5, color=INK, bold=True))
        f.append(text(x + cw / 2, 216, yr, size=11.5, color=MUTED, bold=True))
        f.append(rect(x + cw / 2 - 50, 230, 100, 24, fill=col, stroke=col, sw=0))
        f.append(text(x + cw / 2, 246, badge, size=12, color=BG, bold=True))
        ly = 282
        for ln in lines:
            f.append(text(x + 16, ly, ln, size=10.8, color=INK, anchor="start"))
            ly += 18
    f.append(text(W / 2, 390, "«мати ідею» ≠ «довести теорему» ≠ «збудувати машину» ≠ «ясно описати» — і всі потрібні",
                  size=11, color=INK, bold=True))
    f.append(text(W / 2, 410, "а перші робочі машини зі збереженою програмою були британські",
                  size=10.5, color=MUTED, italic=True))
    out("vn-parents.svg", W, H, *f,
        title="У «архітектури фон Неймана» багато батьків")


def fig_vn_bottleneck():
    W, H = 880, 380
    f = []
    f.append(text(W / 2, 54, "і інструкції, і дані течуть тим самим єдиним каналом — тож процесор інколи голодує",
                  size=11.5, color=MUTED, italic=True))
    f.append(rect(70, 130, 210, 120, fill=RED_BG, stroke=POS, sw=2))
    f.append(text(175, 186, "ПРОЦЕСОР", size=15, color=POS, bold=True))
    f.append(text(175, 208, "швидкий", size=12, color=MUTED, italic=True))
    f.append(rect(600, 130, 210, 120, fill=GREEN_BG, stroke=FIELD, sw=2))
    f.append(text(705, 186, "ПАМ'ЯТЬ", size=15, color=FIELD, bold=True))
    f.append(text(705, 208, "велика", size=12, color=MUTED, italic=True))
    # «пісковий годинник» — вузька шина
    f.append('<path d="M280,150 L420,184 L460,184 L600,150 L600,230 L460,196 L420,196 L280,230 Z" '
             'fill="%s" stroke="%s" stroke-width="2"/>' % (AMBER_BG, AMBER))
    f.append(text(440, 178, "одна", size=10.5, color=AMBER, bold=True))
    f.append(text(440, 200, "вузька", size=10.5, color=AMBER, bold=True))
    f.append(text(440, 138, "інструкції + дані — разом", size=10.5, color=INK, bold=True))
    f.append(rect(60, 280, 760, 84, fill="#f6f8f6", stroke=MUTED, sw=1.4))
    f.append(text(440, 304, "термін увів Джон Бекус (Тюрінгова лекція 1977): чим швидший процесор,",
                  size=11.5, color=INK, bold=True))
    f.append(text(440, 324, "тим частіше він простоює, чекаючи на єдину шину до пам'яті.",
                  size=11.5, color=INK, bold=True))
    f.append(text(440, 348, "інший підхід — Гарвардська архітектура (окремі канали коду й даних); AVR в Arduino — саме така",
                  size=10.5, color=MUTED, italic=True))
    out("vn-bottleneck.svg", W, H, *f,
        title="Слабке місце моделі: «вузьке місце фон Неймана»")


if __name__ == "__main__":
    # стаття
    fig_what()
    fig_instruction()
    fig_program()
    fig_dumb_fast()
    fig_emergence()
    fig_clerk()
    # вставка: Беббідж і Лавлейс
    fig_bl_timeline()
    fig_bl_analytical()
    fig_bl_jacquard()
    fig_bl_bernoulli()
    fig_bl_vision()
    # вставка: фон Нейман
    fig_vn_timeline()
    fig_vn_rewiring()
    fig_vn_architecture()
    fig_vn_parents()
    fig_vn_bottleneck()
    print("OK: 16 фігур у", IMG)
