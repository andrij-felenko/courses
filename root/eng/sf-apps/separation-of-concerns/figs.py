# -*- coding: utf-8 -*-
"""Фігури теми «Розділення відповідальностей». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── tangled-vs-separated: три клопоти сплетені vs розкладені ──────────────────
# Ідея: ліворуч правило, формат і доступ до бази живуть в одній частині,
# повʼязані навхрест (кожна ниточка = шлях, яким зміна одного смикає інше).
# Праворуч ті самі три — окремі цілі частини з єдиним тонким потоком даних
# зверху вниз. Різниця не в кількості коду, а в кількості звʼязків.
def fig_tangled_vs_separated():
    W, H = 960, 470
    f = []

    f.append(text(250, 60, "Сплетено", size=16, bold=True, color=POS))
    f.append(text(710, 60, "Розділено", size=16, bold=True, color=FIELD))
    f.append(line(480, 88, 480, 432, color=MUTED, sw=1.2, dash="6,5"))

    # ── ліва панель: одна частина, три вузли, звʼязки навхрест ──
    f.append(rect(72, 96, 356, 300, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(250, 146, "залежності навхрест", size=12, color=MUTED))

    b, bw, bh = textbox(168, 172, "правило", size=13, fill=BG, stroke=MUTED, sw=1.6, pad=10)
    f.append(b)
    b, bw, bh = textbox(332, 172, "формат", size=13, fill=BG, stroke=MUTED, sw=1.6, pad=10)
    f.append(b)
    b, bw, bh = textbox(250, 312, "доступ\nдо бази", size=13, fill=BG, stroke=MUTED, sw=1.6, pad=10)
    f.append(b)

    # три ниті — між краями вузлів, крізь текст жодна не йде
    f.append(line(204, 172, 300, 172, color=POS, sw=2.0))
    f.append(line(176, 189, 232, 287, color=POS, sw=2.0))
    f.append(line(324, 189, 268, 287, color=POS, sw=2.0))

    f.append(text(250, 428, "будь-яка ниточка тягне сусіда", size=12, color=POS))

    # ── права панель: три окремі цілі частини, єдиний потік ──
    b, bw, bh = textbox(710, 150, "доступ до бази", size=13, fill="#eefaf0",
                        stroke=FIELD, sw=2, pad=11)
    f.append(b)
    b, bw, bh = textbox(710, 268, "правило", size=13, fill="#eefaf0",
                        stroke=FIELD, sw=2, pad=11)
    f.append(b)
    b, bw, bh = textbox(710, 386, "формат", size=13, fill="#eefaf0",
                        stroke=FIELD, sw=2, pad=11)
    f.append(b)

    f.append(arrow(710, 168, 710, 250, color=MUTED, sw=1.6))
    f.append(arrow(710, 286, 710, 368, color=MUTED, sw=1.6))
    f.append(mtext(770, 254, ["єдиний тонкий", "потік даних"], size=12,
                   color=MUTED, anchor="start"))

    f.append(text(710, 428, "зміна одного не чіпає інших", size=12, color=FIELD))

    render(out("tangled-vs-separated.svg"), W, H, *f,
           title="Та сама трійця клопотів: сплетена й розкладена")


# ── axis-of-cut: девʼять обовʼязків, розрізані за шаром vs за можливістю ───────
# Ідея: 3 можливості (стовпці) × 3 технічні шари (рядки) = 9 клітин.
# Зверху ріжемо за шаром — модуль = рядок; зміна однієї можливості («Знижки»,
# середній стовпець) червоніє в усіх трьох модулях. Знизу ріжемо за можливістю —
# модуль = стовпець; та сама зміна лишається в одному зеленому модулі.
def fig_axis_of_cut():
    W, H = 960, 720
    f = []

    COLS = [330, 500, 670]          # Кошик · Знижки · Оплата
    CAPS = ["Кошик", "Знижки", "Оплата"]
    LAYERS = ["Показ", "Логіка", "Дані"]
    CW = 120                         # ширина клітини
    CH = 54                          # висота клітини

    def cell(cx, cy, fill, stroke, sw):
        f.append(rect(cx - CW / 2, cy - CH / 2, CW, CH, fill=fill, stroke=stroke, sw=sw))

    def headers(hy):
        for cx, cap in zip(COLS, CAPS):
            f.append(text(cx, hy, cap, size=13, bold=True, color=INK))

    def rowlabels(rys):
        for ry, lab in zip(rys, LAYERS):
            f.append(text(254, ry + 5, lab, size=13, color=MUTED, anchor="end"))

    # ── Сценарій А: розріз за шаром → горизонтальні модулі ──
    f.append(text(500, 62, "Розріз за технічним шаром: модуль — це рядок",
                  size=15, bold=True, color=NEG))
    headers(104)
    RA = [148, 214, 280]
    # горизонтальні рамки-модулі (малюємо ПІД клітинами)
    for ry in RA:
        f.append(rect(262, ry - 31, 476, 62, fill=BG, stroke=NEG, sw=2, rx=8))
    rowlabels(RA)
    for ry in RA:
        for cx in COLS:
            if cx == 500:                       # стовпець «Знижки» — гарячий
                cell(cx, ry, "#fdecea", POS, 2.2)
            else:
                cell(cx, ry, FILL, LINE, 1.4)
    # червона дужка праворуч через усі три модулі
    f.append(line(752, 117, 752, 311, color=POS, sw=2.4))
    f.append(line(752, 117, 744, 117, color=POS, sw=2.4))
    f.append(line(752, 311, 744, 311, color=POS, sw=2.4))
    f.append(mtext(762, 200, ["зміна «Знижки»", "зачіпає всі", "3 модулі"],
                   size=12, color=POS, anchor="start", bold=True))
    f.append(text(500, 334, "одна вимога розсипана по трьох шарах",
                  size=12, color=MUTED))

    f.append(line(60, 356, 900, 356, color=MUTED, sw=1.2, dash="6,5"))

    # ── Сценарій Б: розріз за можливістю → вертикальні модулі ──
    f.append(text(500, 400, "Розріз за можливістю: модуль — це стовпець",
                  size=15, bold=True, color=FIELD))
    headers(442)
    RB = [486, 552, 618]
    # вертикальні рамки-модулі (середня — виділена зелена)
    for cx in COLS:
        if cx == 500:
            f.append(rect(cx - 70, 455, 140, 194, fill=BG, stroke=FIELD, sw=3, rx=8))
        else:
            f.append(rect(cx - 70, 455, 140, 194, fill=BG, stroke=NEG, sw=2, rx=8))
    rowlabels(RB)
    for ry in RB:
        for cx in COLS:
            if cx == 500:
                cell(cx, ry, "#d4edda", FIELD, 2.2)
            else:
                cell(cx, ry, FILL, LINE, 1.4)
    f.append(text(500, 676, "та сама зміна «Знижки» лишається в одному модулі",
                  size=13, bold=True, color=FIELD))

    render(out("axis-of-cut.svg"), W, H, *f,
           title="Та сама девʼятка обовʼязків, розрізана двома осями")


# ── soc-timeline: віхи народження ідеї (для вставки hist-soc-origins) ─────────
# Ідея: показати інверсію — критерій розрізу (Парнас, 1972) старший за назву
# (Дейкстра, 1974), мірило прийшло того ж 1974-го з іншої школи, а межу самої
# ідеї назвали аж наприкінці 1990-х. Вісь — послідовність віх, не масштаб часу.
def fig_soc_timeline():
    W, H = 1060, 372
    f = []

    XS = [120, 320, 520, 730, 920]
    YEARS = ["1968", "1972", "1974", "1997", "1999"]
    ROW = [90, 175, 90, 175, 90]          # чергування рядків, щоб не тіснилось
    BOXES = [
        (["визнано кризу ПЗ;", "ОС «THE» — пласти", "заради доказу"], MUTED, FILL),
        (["Парнас: критерій —", "ховати рішення,", "які ймовірно зміняться"], FIELD, "#eefaf0"),
        (["Дейкстра дає назву;", "Константайн і колеги —", "мірило розрізу"], NEG, "#eaf0fd"),
        (["аспекти: є клопоти,", "що ріжуться навскіс", "будь-якому розкладу"], POS, "#fdecea"),
        (["названо причину:", "«тиранія панівного", "розкладу»"], POS, "#fdecea"),
    ]

    AXIS = 250
    f.append(line(60, AXIS, 1010, AXIS, color=LINE, sw=2))

    for x, yr, cy, (lines, stroke, fill) in zip(XS, YEARS, ROW, BOXES):
        b, bw, bh = textbox(x, cy, lines, size=12, pad=10,
                            fill=fill, stroke=stroke, sw=2)
        f.append(b)
        f.append(line(x, cy + bh / 2 + 2, x, AXIS - 6, color=MUTED, sw=1.2, dash="4,4"))
        f.append(circle(x, AXIS, 6, fill=BG, stroke=stroke, sw=2.4))
        f.append(text(x, AXIS + 28, yr, size=14, bold=True, color=INK))

    # дужка 1972→1974: критерій старший за назву
    f.append(line(320, 305, 520, 305, color=POS, sw=2.2))
    f.append(line(320, 305, 320, 297, color=POS, sw=2.2))
    f.append(line(520, 305, 520, 297, color=POS, sw=2.2))
    f.append(text(420, 332, "критерій розрізу зʼявився на два роки раніше за назву",
                  size=13, bold=True, color=POS))

    render(out("soc-timeline.svg"), W, H, *f,
           title="Ідея зібралась із частин: критерій, назва, мірило, межа")


# ── ripple-before-after: радіус трьох змін до й після розплутування ───────────
# Ідея: на кожне з трьох замовлень на зміну — дві смуги. Довжина смуги — скільки
# рядків доводиться відкрити, щоб зробити зміну безпечно; суцільна частина — те,
# що правиш, світла — те, що лише перечитуєш. Праворуч — ціна перевірки
# (повільний тест із базою чи швидкий чистий).
def fig_ripple_before_after():
    W, H = 900, 470
    f = []
    K = 8.0            # пікселів на рядок коду
    X0 = 300

    f.append(text(450, 46, "Скільки рядків треба відкрити заради однієї зміни",
                  size=16, bold=True, color=INK))
    f.append(text(450, 72, "суцільне — правити; світле — перечитати",
                  size=12, color=MUTED))

    groups = [
        ("формат суми", 130,
         (24, 0, "24 ряд. · 1 повільний тест"),
         (4, 3, "7 ряд. · 1 швидкий тест")),
        ("ставка ПДВ і знижка", 240,
         (24, 0, "24 ряд. · 1 повільний тест"),
         (6, 6, "12 ряд. · 3 швидкі тести")),
        ("джерело даних", 350,
         (31, 0, "31 ряд. · 1 повільний тест"),
         (23, 0, "23 ряд. · 1 повільний тест")),
    ]

    for name, y0, before, after in groups:
        f.append(text(56, y0 + 5, name, size=14, bold=True, color=INK, anchor="start"))
        rows = ((before, y0, POS, "#fdecea", "до"),
                (after, y0 + 40, FIELD, "#d4edda", "після"))
        for (seed, reread, note), yy, col, light, tag in rows:
            f.append(text(292, yy + 5, tag, size=12, color=MUTED, anchor="end"))
            x = X0
            if seed:
                f.append(rect(x, yy - 13, seed * K, 26, fill=col, stroke=col, sw=1.5, rx=4))
                x += seed * K
            if reread:
                f.append(rect(x, yy - 13, reread * K, 26, fill=light, stroke=col, sw=1.5, rx=4))
                x += reread * K
            f.append(text(x + 14, yy + 5, note, size=12, color=INK, anchor="start"))

    f.append(text(450, 440, "після розплутування три зміни не мають жодної спільної одиниці",
                  size=13, bold=True, color=FIELD))

    render(out("ripple-before-after.svg"), W, H, *f,
           title="Радіус трьох змін до й після розплутування")


# ── boundary-stops: де хвиля зміни спиняється, а де проходить далі ────────────
# Ідея: змінили formatMoney. Хвиля йде до споживачів і гасне на межі, чиєї
# обіцянки вона не порушує; вище межі код навіть не відкривають. Тест — виняток:
# він навмисне звіряє сам текст, тому бачить крізь будь-яку межу.
def fig_boundary_stops():
    W, H = 900, 420
    f = []

    f.append(line(140, 120, 466, 120, color=POS, sw=9))
    f.append(line(470, 100, 470, 140, color=POS, sw=5))
    f.append(mtext(470, 62, ["межа тримає: споживач спирається",
                             "на обіцянку, а не на текст"],
                   size=12, color=POS, bold=True))
    f.append(text(300, 146, "хвиля йде до споживачів", size=11, color=MUTED))

    boxes = [
        (140, "formatMoney · 4 ряд.\nправити", "#fdecea", POS, 2.4),
        (360, "invoiceLine · 3 ряд.\nперечитати", FILL, MUTED, 2.0),
        (590, "monthlyInvoice · 6 ряд.\nне відкриваєш", BG, LINE, 1.2),
        (800, "main · 9 ряд.\nне відкриваєш", BG, LINE, 1.2),
    ]
    for cx, label, fill, stroke, sw in boxes:
        b, bw, bh = textbox(cx, 180, label, size=13, fill=fill, stroke=stroke, sw=sw, pad=10)
        f.append(b)

    # стрілка від споживача до того, на що він спирається
    f.append(arrow(276, 180, 232, 180, color=MUTED, sw=1.6))
    f.append(arrow(495, 180, 452, 180, color=MUTED, sw=1.6))
    f.append(arrow(742, 180, 693, 180, color=MUTED, sw=1.6))

    b, bw, bh = textbox(150, 306, "test_formatMoney · 7 ряд.\nзвіряє сам текст",
                        size=12, fill="#eaf0fd", stroke=NEG, sw=2, pad=9)
    f.append(b)
    f.append(arrow(150, 276, 150, 208, color=NEG, sw=1.8))
    f.append(text(170, 246, "правиш завжди", size=11, color=NEG, anchor="start"))

    f.append(text(450, 392, "стрілка — хто на кого спирається", size=12, color=MUTED))

    render(out("boundary-stops.svg"), W, H, *f,
           title="Де хвиля зміни спиняється, а де проходить далі")


if __name__ == "__main__":
    fig_tangled_vs_separated()
    fig_axis_of_cut()
    fig_soc_timeline()
    fig_ripple_before_after()
    fig_boundary_stops()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
