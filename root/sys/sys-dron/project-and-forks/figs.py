# -*- coding: utf-8 -*-
"""Фігури до теми «Проєкт, ліцензія й вендорські форки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Дві ліцензійні гілки й умова, на якій вони тримаються
# ─────────────────────────────────────────────────────────────────────────────
def fig_license_branches():
    W, H = 1000, 560
    frags = []

    top, _, _ = textbox(500, 90,
                        ["Кодова база QGroundControl",
                         "видана під ДВОМА ліцензіями одразу"],
                        size=15, pad=14, bold=True)
    frags.append(top)

    frags.append(arrow(440, 124, 300, 180, color=NEG))
    frags.append(arrow(560, 124, 700, 180, color=POS))

    left, _, _ = textbox(270, 232,
                         ["GPL v3 — копілефт",
                          "похідне теж відкрите",
                          "джерела змін — на вимогу",
                          "вистачає відкритої версії Qt"],
                         size=14, pad=12, fill="#eaf0fd", stroke=NEG)
    frags.append(left)

    right, _, _ = textbox(730, 232,
                          ["Apache 2.0 — дозвільна",
                           "можна в закритий продукт",
                           "віддавати нічого не треба",
                           "за документацією — комерційна Qt"],
                          size=14, pad=12, fill="#fdecea", stroke=POS)
    frags.append(right)

    frags.append(fitbox(146, 312, 250, 62,
                        ["кого це влаштовує:",
                         "збірка з відкритих джерел"],
                        size=13, color=MUTED))
    frags.append(fitbox(604, 312, 250, 62,
                        ["кого це влаштовує:",
                         "застосунок у магазині"],
                        size=13, color=MUTED))

    frags.append(fitbox(130, 418, 740, 112,
                        ["Умова, на якій тримаються обидві гілки",
                         "всередину приймають лише оригінальний код або запозичення під MIT, BSD-2/3, Apache 2.0",
                         "копілефтний код не беруть: він зробив би дозвільну гілку неможливою"],
                        size=14, pad=16, fill=BG))

    render(os.path.join(OUT, 'license-branches.svg'), W, H, *frags,
           title="Одна кодова база — дві ліцензійні гілки")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Борг злиття росте з площею дотику, а не з обсягом змін
# ─────────────────────────────────────────────────────────────────────────────
def _panel(caption, y_up, y_fork, band_x, band_w, band_fill, band_stroke,
           band_label, label_inside, cost, fork_name):
    f = []
    f.append(text(80, y_up - 46, caption, size=15, anchor="start", bold=True))

    up, _, _ = textbox(115, y_up, "Апстрим", size=13, pad=10)
    f.append(up)
    fk, _, _ = textbox(115, y_fork, fork_name, size=13, pad=10)
    f.append(fk)

    f.append(arrow(178, y_up, 950, y_up))
    f.append(arrow(232, y_fork, 950, y_fork))
    f.append(line(232, y_up, 232, y_fork, color=MUTED, sw=1.4, dash="5,4"))
    f.append(circle(232, y_up, 5, fill=INK, stroke=INK, sw=1))

    if label_inside:
        f.append(fitbox(band_x, y_up + 25, band_w, 50, band_label,
                        size=14, fill=band_fill, stroke=band_stroke))
    else:
        f.append(rect(band_x, y_up + 25, band_w, 50,
                      fill=band_fill, stroke=band_stroke))
        f.append(text(band_x + band_w + 24, y_up + 55, band_label,
                      size=13, anchor="start"))

    f.append(text(232, y_fork + 34, cost, size=13, color=MUTED, anchor="start"))
    return f


def fig_fork_debt():
    W, H = 1000, 530
    frags = []

    frags += _panel("A. Правки розкидані у спільному коді",
                    y_up=118, y_fork=218,
                    band_x=380, band_w=560,
                    band_fill="#fdecea", band_stroke=POS,
                    band_label="площа дотику: правки у 60+ спільних файлах",
                    label_inside=True,
                    cost="кожне підтягування апстриму — ручне злиття; ціна повторюється щороку",
                    fork_name="Форк A")

    frags += _panel("B. Своє живе в окремій теці накладки",
                    y_up=348, y_fork=448,
                    band_x=380, band_w=74,
                    band_fill="#eafaf1", band_stroke=FIELD,
                    band_label="площа дотику: свій код у теці custom/",
                    label_inside=False,
                    cost="підтягування апстриму лишається майже механічним",
                    fork_name="Форк B")

    render(os.path.join(OUT, 'fork-debt.svg'), W, H, *frags,
           title="Вартість форку задає площа дотику зі спільним кодом")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Дві незалежні осі рішення
# ─────────────────────────────────────────────────────────────────────────────
def fig_decision_axes():
    W, H = 920, 570
    frags = []

    col_x = [252, 566]
    col_w = 288
    frags.append(fitbox(col_x[0], 66, col_w, 44, "накладка в теці custom/",
                        size=14, bold=True, fill=BG, stroke=MUTED))
    frags.append(fitbox(col_x[1], 66, col_w, 44, "правки у спільному коді",
                        size=14, bold=True, fill=BG, stroke=MUTED))

    row_y = [130, 306]
    row_h = 152

    rlab1, _, _ = textbox(128, row_y[0] + row_h / 2,
                          ["Apache 2.0", "дозвільна"], size=13, pad=12,
                          fill="#fdecea", stroke=POS)
    frags.append(rlab1)
    rlab2, _, _ = textbox(128, row_y[1] + row_h / 2,
                          ["GPL v3", "копілефт"], size=13, pad=12,
                          fill="#eaf0fd", stroke=NEG)
    frags.append(rlab2)

    cells = [
        (0, 0, ["віддавати нічого не треба", "супровід дешевий",
                "лишається питання ліцензій", "на залежності"]),
        (0, 1, ["віддавати нічого не треба", "супровід дорогий щороку"]),
        (1, 0, ["джерела змін — на вимогу", "супровід дешевий"]),
        (1, 1, ["джерела змін — на вимогу", "супровід дорогий щороку"]),
    ]
    for r, c, lines in cells:
        frags.append(fitbox(col_x[c], row_y[r], col_w, row_h, lines, size=14, pad=14))

    frags.append(text(460, 500, "глибина втручання зростає →",
                      size=13, color=MUTED))
    frags.append(fitbox(128, 516, 712, 40,
                        "осі незалежні: відкритість не здешевлює супровід, глибина не додає обов'язків",
                        size=13, fill=BG, stroke=MUTED, color=MUTED))

    render(os.path.join(OUT, 'decision-axes.svg'), W, H, *frags,
           title="Дві осі рішення про власну збірку")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Ключові дати: від задачі про автономний політ до зникнення старих форм
#    (вставка hist-qgc-origins.md)
# ─────────────────────────────────────────────────────────────────────────────
def fig_origins_timeline():
    W, H = 1040, 800
    frags = []

    spine_x = 296
    date_x = 268
    box_x, box_w = 332, 676
    box_h = 74

    LAB = ("#eaf0fd", NEG)      # лабораторія в Цюриху
    HOME = (BG, MUTED)          # переїзд у спільний дім
    MATURE = ("#eafaf1", FIELD)  # зріла станція

    rows = [
        (["2008"], LAB,
         ["ETH Zürich, лабораторія комп'ютерного зору й геометрії:",
          "задача — автономний політ за зображенням на апараті ≈1 кг"]),
        (["14–17 вересня", "2009"], LAB,
         ["Делфт: команда PIXHAWK виграє місію Indoor Autonomy на EMAV",
          "апарат летить будівлею без GPS і без обчислювача на землі"]),
        (["2011"], LAB,
         ["публікація описує систему цілком: плата pxIMU, обчислювач pxCOMEx,",
          "протокол MAVLink і наземна станція — усе з однієї роботи"]),
        (["13 жовтня 2011"], HOME,
         ["на GitHub створено репозиторій mavlink/qgroundcontrol",
          "код старший за свій репозиторій"]),
        (["13 жовтня 2014"], HOME,
         ["Linux Foundation оголошує Dronecode — вендор-нейтральний дім",
          "станції в тому переліку ще немає; коли приєдналася — не задокументовано"]),
        (["27 липня 2016", "1 серпня 2016"], MATURE,
         ["реліз 3.0: інтерфейс, перебудований під планшет",
          "146 файлів QML — і ще 22 старі форми поряд із ними"]),
        (["≈2022"], MATURE,
         ["реліз 4.2.0: 275 файлів QML, старих форм — жодної",
          "перехід, оголошений 2016 року, завершився аж тут"]),
    ]

    pitch = 98
    y0 = 100
    ys = [y0 + i * pitch for i in range(len(rows))]

    frags.append(line(spine_x, ys[0], spine_x, ys[-1], color=MUTED, sw=1.6, dash="6,5"))

    for cy, (dates, (fill, stroke), lines) in zip(ys, rows):
        dy = cy - (len(dates) - 1) * 15 * 1.3 / 2 + 15 * 0.35
        frags.append(mtext(date_x, dy, dates, size=15, bold=True, anchor="end"))
        frags.append(circle(spine_x, cy, 7, fill=fill, stroke=stroke, sw=2.2))
        frags.append(fitbox(box_x, cy - box_h / 2, box_w, box_h, lines,
                            size=14, pad=14, fill=fill, stroke=stroke))

    frags.append(fitbox(box_x, ys[-1] + 62, box_w, 40,
                        "синє — лабораторія в Цюриху · біле — переїзд у спільний дім · зелене — зріла станція",
                        size=13, pad=14, fill=BG, stroke=MUTED, color=MUTED))

    render(os.path.join(OUT, 'origins-timeline.svg'), W, H, *frags,
           title="Станція старша за свій репозиторій")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Один XML-опис — код для обох боків (вставка hist-qgc-origins.md)
# ─────────────────────────────────────────────────────────────────────────────
def fig_origins_codegen():
    W, H = 1000, 620
    frags = []

    xml, _, _ = textbox(500, 90,
                        ["message_definitions/*.xml",
                         "опис повідомлень: id, поля, типи, переліки"],
                        size=14, pad=12, fill="#eaf0fd", stroke=NEG)
    frags.append(xml)

    frags.append(arrow(500, 120, 500, 186))

    gen, _, _ = textbox(500, 208, "генератор коду (mavgen)",
                        size=15, pad=12, bold=True, fill=BG)
    frags.append(gen)

    frags.append(arrow(460, 228, 268, 305))
    frags.append(arrow(540, 228, 732, 305))

    left, _, _ = textbox(260, 345,
                         ["код пакування на C89",
                          "лягає навіть на 60-мегагерцевий ARM7"],
                         size=14, pad=12, fill="#fdecea", stroke=POS)
    frags.append(left)

    right, _, _ = textbox(740, 345,
                          ["той самий опис у застосунку",
                           "станція розбирає ті самі байти"],
                          size=14, pad=12, fill="#eafaf1", stroke=FIELD)
    frags.append(right)

    frags.append(arrow(260, 378, 260, 428))
    frags.append(arrow(740, 378, 740, 428))

    a1, _, _ = textbox(260, 452, "автопілот на платі", size=14, pad=11, bold=True)
    frags.append(a1)
    a2, _, _ = textbox(740, 452, "наземна станція", size=14, pad=11, bold=True)
    frags.append(a2)

    frags.append(fitbox(80, 512, 840, 84,
                        ["наслідок: поле, id й перелік однакові з обох боків —",
                         "станція розуміє нове повідомлення майже одразу після його опису",
                         "зворотний бік: помилка в описі народжується відразу на обох боках"],
                        size=14, pad=16, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'origins-codegen.svg'), W, H, *frags,
           title="Обидва боки виростають з одного опису")


# ─────────────────────────────────────────────────────────────────────────────
# Що саме міряють від точки розгалуження (вставка proj-fork-divergence)
# ─────────────────────────────────────────────────────────────────────────────
def fig_divergence_measure():
    W, H = 1020, 650
    f = []

    # ── Панель A: дві лінії від однієї точки ────────────────────────────────
    f.append(text(70, 84, "Дві лінії від однієї точки",
                  size=15, anchor="start", bold=True))

    up, _, _ = textbox(150, 130, "Апстрим", size=13, pad=10)
    f.append(up)
    fk, _, _ = textbox(150, 210, "Форк", size=13, pad=10)
    f.append(fk)

    f.append(arrow(250, 130, 960, 130))
    f.append(arrow(250, 210, 830, 210))
    f.append(line(250, 130, 250, 210, color=MUTED, sw=1.4, dash="5,4"))
    f.append(circle(250, 130, 6, fill=INK, stroke=INK, sw=1))

    for x in (350, 450, 550, 650, 750, 850):
        f.append(circle(x, 130, 5, fill=BG, stroke=MUTED, sw=1.4))
    for x in (350, 450, 550):
        f.append(circle(x, 210, 5, fill=BG, stroke=MUTED, sw=1.4))

    f.append(text(650, 108, "1487 комітів, яких у нас немає — «позаду»",
                  size=13, color=MUTED))
    f.append(text(258, 176, "точка розгалуження (merge-base)",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(550, 243, "63 наші коміти — «попереду»",
                  size=13, color=MUTED))

    # ── Панель B: три множини файлів ────────────────────────────────────────
    f.append(text(70, 320, "Три множини файлів — і та єдина, що коштує грошей",
                  size=15, anchor="start", bold=True))

    # рядок U: чуже поза перетином + сам перетин
    f.append(fitbox(70, 350, 230, 46,
                    ["U — змінив апстрим", "3162 файли"], size=13))
    f.append(fitbox(320, 350, 370, 46,
                    ["U \\ C — чужі правки", "прийдуть як є"],
                    size=13, fill="#eaf0fd", stroke=NEG))
    f.append(rect(690, 350, 130, 46, fill="#fdecea", stroke=POS))

    # рядок M: перетин + наше поза перетином
    f.append(fitbox(70, 424, 230, 46,
                    ["M — змінили ми", "57 правок спільних файлів"], size=13))
    f.append(rect(690, 424, 130, 46, fill="#fdecea", stroke=POS))
    f.append(fitbox(820, 424, 160, 46,
                    ["M \\ C — наше", "піде без питань"],
                    size=13, fill="#eafaf1", stroke=FIELD))

    # рядок C: сам перетин
    f.append(fitbox(70, 498, 230, 46,
                    ["C = M ∩ U — перетин", "тут буде ручна робота"], size=13))
    f.append(fitbox(690, 498, 130, 46, ["C", "41 файл"],
                    size=13, fill="#fdecea", stroke=POS))
    f.append(text(835, 526, "рахунок за наступне злиття",
                  size=12, color=POS, anchor="start"))

    # напрямні лише в проміжках між рядками — щоб не перетинати підписи
    for x in (690, 820):
        f.append(line(x, 396, x, 424, color=POS, sw=1.2, dash="4,4"))
        f.append(line(x, 470, x, 498, color=POS, sw=1.2, dash="4,4"))

    f.append(fitbox(70, 570, 910, 46,
                    "поза перетином вибору немає: якщо одна сторона файл "
                    "не чіпала, злиття бере версію другої",
                    size=13, fill=BG, stroke=MUTED, color=MUTED))

    render(os.path.join(OUT, 'divergence-measure.svg'), W, H, *f,
           title="Від чого міряють розходження — і що з нього коштує грошей")


# ─────────────────────────────────────────────────────────────────────────────
# Злиття зберігає базу, ребейз її знищує (вставка proj-fork-divergence)
# ─────────────────────────────────────────────────────────────────────────────
def fig_fork_history_strategy():
    W, H = 1020, 620
    f = []

    # ── A. Злиття ───────────────────────────────────────────────────────────
    f.append(text(70, 84, "A. Злиття: база лишається на місці",
                  size=15, anchor="start", bold=True))

    up, _, _ = textbox(150, 140, "Апстрим", size=13, pad=10)
    f.append(up)
    fk, _, _ = textbox(150, 225, "Форк", size=13, pad=10)
    f.append(fk)

    f.append(arrow(240, 140, 960, 140))
    f.append(arrow(240, 225, 920, 225))
    f.append(line(240, 140, 240, 225, color=MUTED, sw=1.4, dash="5,4"))
    f.append(circle(240, 140, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(248, 186, "база лишається спільним предком",
                  size=12, color=MUTED, anchor="start"))

    for x in (340, 440, 540, 640, 740, 840):
        f.append(circle(x, 140, 5, fill=BG, stroke=MUTED, sw=1.4))
    for x in (340, 440, 540):
        f.append(circle(x, 225, 5, fill=BG, stroke=MUTED, sw=1.4))

    f.append(arrow(620, 150, 658, 214, color=FIELD))
    f.append(arrow(820, 150, 858, 214, color=FIELD))
    f.append(circle(660, 225, 6, fill="#eafaf1", stroke=FIELD, sw=1.6))
    f.append(circle(860, 225, 6, fill="#eafaf1", stroke=FIELD, sw=1.6))

    f.append(text(640, 264,
                  "виміри лишаються можливими; rerere згадує старі розв'язання",
                  size=12, color=MUTED))

    # ── B. Ребейз ───────────────────────────────────────────────────────────
    f.append(text(70, 364,
                  "B. Ребейз довгоживучої гілки: старої бази більше немає",
                  size=15, anchor="start", bold=True))

    up2, _, _ = textbox(150, 420, "Апстрим", size=13, pad=10)
    f.append(up2)
    fk2, _, _ = textbox(190, 500, "Форк", size=13, pad=10)
    f.append(fk2)

    f.append(arrow(240, 420, 960, 420))
    f.append(circle(240, 420, 6, fill=BG, stroke=MUTED, sw=1.6))
    for x in (340, 440, 540, 640, 740):
        f.append(circle(x, 420, 5, fill=BG, stroke=MUTED, sw=1.4))

    # стара, переписана лінія — сіра й пунктирна
    f.append(line(240, 420, 280, 500, color=MUTED, sw=1.3, dash="4,4"))
    f.append(line(280, 500, 530, 500, color=MUTED, sw=1.3, dash="4,4"))
    for x in (340, 420, 500):
        f.append(circle(x, 500, 5, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(292, 530, "старі коміти: інші хеші, більше не існують",
                  size=12, color=MUTED, anchor="start"))

    # нова лінія — від нової точки біля вершини
    f.append(line(800, 420, 800, 500, color=FIELD, sw=1.4, dash="5,4"))
    f.append(circle(800, 420, 6, fill=FIELD, stroke=FIELD, sw=1))
    f.append(arrow(800, 500, 950, 500, color=FIELD))
    for x in (850, 900):
        f.append(circle(x, 500, 5, fill="#eafaf1", stroke=FIELD, sw=1.4))
    f.append(text(808, 468, "нова база — тепер тут",
                  size=12, color=FIELD, anchor="start"))

    f.append(fitbox(70, 552, 910, 46,
                    "клони форку більше не зливаються; записані розв'язання "
                    "конфліктів не збігаються",
                    size=13, fill=BG, stroke=MUTED, color=MUTED))

    render(os.path.join(OUT, 'fork-history-strategy.svg'), W, H, *f,
           title="Злиття зберігає точку розгалуження, ребейз її знищує")


if __name__ == '__main__':
    fig_license_branches()
    fig_fork_debt()
    fig_decision_axes()
    fig_origins_timeline()
    fig_origins_codegen()
    fig_divergence_measure()
    fig_fork_history_strategy()
    print("ok")
