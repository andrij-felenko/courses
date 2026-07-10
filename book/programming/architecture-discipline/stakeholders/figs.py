# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
F_GREY = "#f4f6f8"
GOLD_LINE = "#b8860b"


# ── origin: гроші на кілку в руках нейтрального тримача ───────────────────────
def fig_origin():
    W, H = 760, 340
    p = [text(W / 2, 28, "Звідки слово: тримач ставок", size=17, bold=True)]
    p.append(text(W / 2, 48, "спершу — нейтральна людина, у якої лежать гроші, поки не з'ясується результат",
                  size=10.5, color=MUTED, italic=True))

    # два гравці
    p.append(rect(40, 120, 130, 60, fill=F_RED, stroke=POS, sw=1.8))
    p.append(text(105, 148, "Гравець A", size=13, bold=True))
    p.append(text(105, 167, "ставить своє", size=10, color=MUTED))

    p.append(rect(590, 120, 130, 60, fill=F_BLUE, stroke=NEG, sw=1.8))
    p.append(text(655, 148, "Гравець B", size=13, bold=True))
    p.append(text(655, 167, "ставить своє", size=10, color=MUTED))

    # кілок із грошима посередині
    cx = 380
    p.append(line(cx, 110, cx, 210, color=GOLD_LINE, sw=4))           # кілок
    p.append(rect(cx - 46, 92, 92, 34, fill=F_GLD, stroke=GOLD_LINE, sw=1.8))
    p.append(text(cx, 114, "ставки", size=12, bold=True, color=GOLD_LINE))
    p.append(circle(cx, 232, 34, fill="#fff", stroke=INK, sw=1.8))
    p.append(text(cx, 228, "тримач", size=11, bold=True))
    p.append(text(cx, 244, "ставок", size=11, bold=True))

    # руки-стрілки від гравців до кілка
    p.append(arrow(170, 150, cx - 50, 130, color=POS))
    p.append(arrow(590, 150, cx + 50, 130, color=NEG))

    # висновок унизу — своя рамка, окремо від ліній
    box, _, _ = textbox(W / 2, 300,
        "Сьогодні «стейкхолдер» — той, у кого в цій справі є що втратити чи здобути",
        size=11.5, pad=12, fill=F_GREY)
    p.append(box)

    render(os.path.join(OUT, "origin.svg"), W, H, *p)


# ── classes: система в центрі, довкола класи стейкхолдерів із їхньою турботою ──
def fig_classes():
    W, H = 820, 560
    p = [text(W / 2, 30, "Різні люди дивляться на ту саму систему по-різному", size=17, bold=True)]
    p.append(text(W / 2, 50, "кожен клас несе свою турботу — і саме вона тисне на архітектуру",
                  size=10.5, color=MUTED, italic=True))

    # система в центрі
    ccx, ccy = W / 2, 300
    p.append(circle(ccx, ccy, 66, fill=F_GRN, stroke=FIELD, sw=2.2))
    p.append(text(ccx, ccy - 4, "Система", size=15, bold=True))
    p.append(text(ccx, ccy + 15, "(одна)", size=10, color=MUTED, italic=True))

    # картки-стейкхолдери довкола; кожна — назва + турбота одним рядком
    cards = [
        ("Замовник",      "чи вкладемось у бюджет і строк", F_GLD, GOLD_LINE, 150, 130),
        ("Користувач",    "чи зроблю тут своє швидко й без болю", F_BLUE, NEG, 500, 130),
        ("Розробник",     "чи зрозуміла структура, куди класти код", F_RED, POS, 60, 300),
        ("Супровід",      "чи легко змінити, коли зміняться вимоги", F_BLUE, NEG, 590, 300),
        ("Адміністратор", "чи видно збій і чи підніму систему вночі", F_RED, POS, 150, 470),
        ("Аудитор",       "чи виконано норми, приватність, безпеку", F_GLD, GOLD_LINE, 500, 470),
    ]
    cw, ch = 230, 66
    for t, care, fill, stroke, x, y in cards:
        p.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=1.8))
        p.append(text(x + cw / 2, y + 26, t, size=13.5, bold=True))
        p.append(text(x + cw / 2, y + 47, care, size=9.5, color=MUTED))
        # тонка лінія від картки до системи (веду до краю картки, повз написи)
        ax = x + cw / 2
        ay = y + ch if y < ccy else y
        p.append(line(ax, ay, ccx + (ax - ccx) * 0.28, ccy + (ay - ccy) * 0.28,
                      color="#c9cdd3", sw=1.2, dash="3,4"))

    render(os.path.join(OUT, "classes.svg"), W, H, *p)


# ── chain: стейкхолдер → турбота → атрибут → сценарій → в'ю ───────────────────
def fig_chain():
    W, H = 860, 250
    p = [text(W / 2, 28, "Від турботи людини — до перевірної вимоги й до креслення", size=17, bold=True)]

    steps = [
        ("Стейкхолдер", "хто саме", F_GLD, GOLD_LINE),
        ("Турбота", "що йому важить", F_RED, POS),
        ("Якісний\nатрибут", "яка властивість", F_BLUE, NEG),
        ("Сценарій", "стимул → міра", F_GRN, FIELD),
        ("Архіт. в'ю", "як показано", F_GREY, LINE),
    ]
    n = len(steps)
    bw, bh, gap = 132, 78, 26
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = 96
    for i, (t, sub, fill, stroke) in enumerate(steps):
        x = x0 + i * (bw + gap)
        p.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=1.8))
        lines = t.split("\n")
        ty = y + 30 if len(lines) == 1 else y + 24
        p.append(mtext(x + bw / 2, ty, lines, size=13, bold=True))
        p.append(text(x + bw / 2, y + bh - 14, sub, size=9.5, color=MUTED))
        if i < n - 1:
            ax = x + bw
            p.append(arrow(ax + 3, y + bh / 2, ax + gap - 3, y + bh / 2, color=INK))

    p.append(text(W / 2, y + bh + 44,
                  "Тримати цей ланцюг цілим — і є щоденна робота архітектора",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "chain.svg"), W, H, *p)


# ── timeline: дорога слова «стейкхолдер» крізь три століття ───────────────────
def fig_timeline():
    W, H = 980, 430
    p = [text(W / 2, 30, "Дорога слова «стейкхолдер»: від картярського столу до стандарту",
              size=17, bold=True)]
    p.append(text(W / 2, 50, "кожна станція додала змісту, який ми досі несемо в терміні",
                  size=10.5, color=MUTED, italic=True))

    # горизонтальна вісь
    ax_y = 150
    x_lo, x_hi = 70, W - 70
    p.append(line(x_lo, ax_y, x_hi, ax_y, color="#c9cdd3", sw=2.4))
    p.append(arrow(x_hi - 30, ax_y, x_hi, ax_y, color="#c9cdd3"))

    # станції: (рік, назва, суть — унизу), рівномірно по осі
    stations = [
        ("1708", "Тримач ставок",  "нейтрал тримає\nчужі гроші на парі", F_GLD, GOLD_LINE),
        ("1963", "SRI: меморандум", "ширше за акціонера:\nгрупи, без яких\nфірми не стане", F_RED, POS),
        ("1984", "Фрімен: теорія",  "хто впливає\nАБО зазнає впливу", F_BLUE, NEG),
        ("2000\n→2011", "IEEE 1471\n→ ISO 42010", "стейкхолдер +\nйого «турбота»\n= старт опису", F_GRN, FIELD),
    ]
    n = len(stations)
    xs = [x_lo + 55 + i * (x_hi - x_lo - 90) / (n - 1) for i in range(n)]
    cw = 190

    for i, (yr, name, sub, fill, stroke) in enumerate(stations):
        cx = xs[i]
        # вузол на осі
        p.append(circle(cx, ax_y, 7, fill=stroke, stroke="#fff", sw=2))
        # рік — над віссю, у своїй рамці
        ybox, _, yh = textbox(cx, ax_y - 40, yr, size=13, bold=True,
                              fill="#fff", stroke=stroke, pad=7, min_w=64)
        p.append(ybox)
        # картка назви+суті — під віссю, з ЗАПАСОМ між станціями
        card_top = ax_y + 34
        p.append(rect(cx - cw / 2, card_top, cw, 118, fill=fill, stroke=stroke, sw=1.6))
        p.append(mtext(cx, card_top + 22, name.split("\n"), size=13, bold=True))
        nlines = len(name.split("\n"))
        sub_y = card_top + 22 + nlines * 17 + 8
        p.append(mtext(cx, sub_y, sub.split("\n"), size=9.8, color=MUTED, lh=1.28))
        # тонка з'єднувальна риска рік↔вузол
        p.append(line(cx, ax_y - 40 + yh / 2, cx, ax_y - 7, color=stroke, sw=1.1, dash="2,3"))

    # висновок унизу — окрема рамка, поза картками й лініями
    box, _, _ = textbox(W / 2, 400,
        "Спільна серцевина всіх станцій: у стейкхолдера щось поставлено на кону — є що втратити чи здобути",
        size=11.5, pad=12, fill=F_GREY, min_w=520)
    p.append(box)

    render(os.path.join(OUT, "timeline.svg"), W, H, *p)


# ── salience: три кола (влада/легіт./терм.) і сім класів у перетинах ──────────
def fig_salience():
    W, H = 780, 670
    p = [text(W / 2, 30, "Вагомість — місце в перетині трьох осей", size=17, bold=True)]
    p.append(text(W / 2, 52, "влада · легітимність · терміновість — і сім класів у їхніх перетинах",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 74, "латентні — одна ознака    ·    очікувальні — дві    ·    визначальний — усі три",
                  size=10, color=MUTED))

    Ax, Ay = 310, 305
    Bx, By = 470, 305
    Cx, Cy = 390, 440
    R = 146
    p.append(circle(Ax, Ay, R, fill="none", stroke=POS, sw=2.4))
    p.append(circle(Bx, By, R, fill="none", stroke=NEG, sw=2.4))
    p.append(circle(Cx, Cy, R, fill="none", stroke=FIELD, sw=2.4))

    # підписи осей — поза колами
    p.append(text(248, 150, "ВЛАДА", size=13, bold=True, color=POS))
    p.append(text(532, 150, "ЛЕГІТИМНІСТЬ", size=13, bold=True, color=NEG))
    p.append(text(390, 616, "ТЕРМІНОВІСТЬ", size=13, bold=True, color=FIELD))

    # сім класів — кожен у своїй області перетину
    regions = [
        (210, 262, "сплячий"),
        (570, 262, "на-розсуд"),
        (390, 530, "вимогливий"),
        (390, 248, "панівний"),
        (298, 408, "небезпечний"),
        (482, 408, "залежний"),
        (390, 352, "визначальний"),
    ]
    for x, y, name in regions:
        p.append(text(x, y, name, size=11.5, bold=True))

    render(os.path.join(OUT, "salience.svg"), W, H, *p)


# ── grid: сітка «влада–інтерес» із чотирма стратегіями й стейкхолдерами ───────
def fig_grid():
    W, H = 740, 560
    p = [text(W / 2, 30, "Сітка «влада–інтерес»: скільки уваги й якого роду", size=17, bold=True)]
    p.append(text(W / 2, 52, "стратегія — про смугу спілкування, а не про те, чия воля переможе",
                  size=10.5, color=MUTED, italic=True))

    gx, gy, gw, gh = 155, 95, 495, 380
    mx, my = gx + gw / 2, gy + gh / 2
    q = gw / 4
    p.append(rect(gx, gy, gw / 2, gh / 2, fill=F_GLD, stroke=LINE, sw=1.2, rx=0))    # TL
    p.append(rect(mx, gy, gw / 2, gh / 2, fill=F_RED, stroke=LINE, sw=1.2, rx=0))    # TR
    p.append(rect(gx, my, gw / 2, gh / 2, fill=F_GREY, stroke=LINE, sw=1.2, rx=0))   # BL
    p.append(rect(mx, my, gw / 2, gh / 2, fill=F_BLUE, stroke=LINE, sw=1.2, rx=0))   # BR
    p.append(line(gx, my, gx + gw, my, color=INK, sw=1.8))
    p.append(line(mx, gy, mx, gy + gh, color=INK, sw=1.8))

    # TL — тримати вдоволеним
    p.append(text(gx + q, gy + 56, "Тримати вдоволеним", size=13.5, bold=True))
    b, _, _ = textbox(gx + q, gy + 108, "Спонсор", size=11, fill="#fff", pad=8); p.append(b)
    # TR — вести щільно
    p.append(text(mx + q, gy + 50, "Вести щільно", size=13.5, bold=True))
    b, _, _ = textbox(mx + q, gy + 98, "Замовник", size=11, fill="#fff", pad=8); p.append(b)
    b, _, _ = textbox(mx + q, gy + 140, "Головний аудитор", size=11, fill="#fff", pad=8); p.append(b)
    # BL — спостерігати
    p.append(text(gx + q, my + 52, "Спостерігати", size=13.5, bold=True))
    b, _, _ = textbox(gx + q, my + 100, "Постачальник", size=11, fill="#fff", pad=8); p.append(b)
    # BR — тримати в курсі (тихий оператор)
    p.append(text(mx + q, my + 48, "Тримати в курсі", size=13.5, bold=True))
    b, _, _ = textbox(mx + q, my + 96, "Оператор", size=11.5, fill="#fff", stroke=POS, sw=2, bold=True); p.append(b)
    p.append(text(mx + q, my + 132, "тихий, та велика ставка", size=9.5, color=MUTED, italic=True))

    # осі
    p.append(text(86, gy + gh / 2, "ВЛАДА", size=12, bold=True))
    p.append(text(120, gy + 14, "висока", size=9, color=MUTED))
    p.append(text(120, gy + gh - 6, "низька", size=9, color=MUTED))
    p.append(text(W / 2, gy + gh + 36, "ІНТЕРЕС →", size=12, bold=True))
    p.append(text(gx + 92, gy + gh + 16, "низький", size=9, color=MUTED))
    p.append(text(gx + gw - 92, gy + gh + 16, "високий", size=9, color=MUTED))

    render(os.path.join(OUT, "grid.svg"), W, H, *p)


# ── tradeoff: точка чутливості vs точка компромісу ───────────────────────────
def fig_tradeoff():
    W, H = 820, 440
    p = [text(W / 2, 30, "Точка чутливості проти точки компромісу", size=17, bold=True)]
    p.append(text(W / 2, 52, "де ставки двох стейкхолдерів сходяться на одному параметрі",
                  size=10.5, color=MUTED, italic=True))
    p.append(line(410, 78, 410, 348, color="#c9cdd3", sw=1.4, dash="4,5"))

    # ліворуч — чутливість (один атрибут)
    p.append(text(210, 96, "Точка чутливості", size=13.5, bold=True))
    p.append(text(210, 114, "чіпає ОДИН атрибут", size=10, color=MUTED, italic=True))
    b, _, _ = textbox(210, 158, "Розмір пулу потоків", size=11.5, fill=F_GREY, pad=10); p.append(b)
    p.append(arrow(210, 180, 210, 232, color=INK))
    b, _, _ = textbox(210, 258, "Швидкодія", size=12, fill=F_BLUE, stroke=NEG, pad=10, bold=True); p.append(b)
    p.append(text(210, 312, "крутнув трохи — затримка стрибнула", size=9.5, color=MUTED))

    # праворуч — компроміс (два атрибути в різні боки)
    p.append(text(600, 96, "Точка компромісу", size=13.5, bold=True))
    p.append(text(600, 114, "чіпає ДВА в різні боки", size=10, color=MUTED, italic=True))
    b, _, _ = textbox(600, 158, "Ширина реплікації даних", size=11.5, fill=F_GLD, stroke=GOLD_LINE, pad=10); p.append(b)
    p.append(arrow(575, 182, 520, 232, color=FIELD))
    p.append(arrow(625, 182, 690, 232, color=POS))
    b, _, _ = textbox(512, 258, "Доступність", size=11.5, fill=F_GRN, stroke=FIELD, pad=9, bold=True); p.append(b)
    p.append(plus(512, 298, 9))
    b, _, _ = textbox(700, 258, "Локальність", size=11.5, fill=F_RED, stroke=POS, pad=9, bold=True); p.append(b)
    p.append(minus(700, 298, 9))
    p.append(text(512, 330, "оператор радий", size=9, color=MUTED))
    p.append(text(700, 330, "аудитор проти", size=9, color=MUTED))

    b, _, _ = textbox(W / 2, 405,
                      "На точці компромісу бали не складають — її виносять на світло й домовляються явно",
                      size=11, fill=F_GREY, pad=11, min_w=560); p.append(b)
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p)


# ── views-matrix: стейкхолдер × в'ю, правило «жоден рядок не порожній» ────────
def fig_views():
    W, H = 790, 470
    p = [text(W / 2, 30, "Матриця «стейкхолдер × в'ю»", size=17, bold=True)]
    p.append(text(W / 2, 52, "правило 42010: жоден рядок не порожній — кожну турботу показує хоч одне в'ю",
                  size=10.5, color=MUTED, italic=True))

    cols = ["Контекст", "Контейнери", "Компоненти", "Розгортання", "Сценарії"]
    rows = [
        ("Замовник / бізнес", [1, 0, 0, 0, 1]),
        ("Користувач",        [1, 0, 0, 0, 1]),
        ("Розробник",         [0, 1, 1, 0, 1]),
        ("Супровід",          [0, 1, 1, 1, 0]),
        ("Оператор",          [1, 0, 0, 1, 0]),
        ("Аудитор",           [1, 0, 0, 1, 1]),
    ]
    lx, tw = 45, 175
    cw = 112
    hy, hh = 82, 52
    ry, rh = hy + hh, 44
    gx = lx + tw

    for j, c in enumerate(cols):
        x = gx + j * cw
        p.append(rect(x, hy, cw, hh, fill=F_GREY, stroke=LINE, sw=1, rx=0))
        p.append(text(x + cw / 2, hy + hh / 2 + 4, c, size=10.5, bold=True))
    p.append(rect(lx, hy, tw, hh, fill="#fff", stroke=LINE, sw=1, rx=0))
    p.append(text(lx + tw / 2, hy + hh / 2 + 4, "стейкхолдер ↓", size=10.5, bold=True, color=MUTED))

    for i, (name, marks) in enumerate(rows):
        y = ry + i * rh
        p.append(rect(lx, y, tw, rh, fill="#fff", stroke=LINE, sw=1, rx=0))
        p.append(text(lx + 12, y + rh / 2 + 4, name, size=11, anchor="start"))
        for j, m in enumerate(marks):
            x = gx + j * cw
            p.append(rect(x, y, cw, rh, fill=("#eef7ee" if m else "#fff"), stroke=LINE, sw=1, rx=0))
            if m:
                p.append(text(x + cw / 2, y + rh / 2 + 6, "✓", size=16, bold=True, color=FIELD))
            else:
                p.append(text(x + cw / 2, y + rh / 2 + 4, "·", size=13, color=MUTED))

    yend = ry + len(rows) * rh
    b, _, _ = textbox(W / 2, yend + 28,
                      "Порожній рядок — не брак діаграми, а нечутий голос стейкхолдера",
                      size=11, fill=F_GREY, pad=11, min_w=520); p.append(b)
    render(os.path.join(OUT, "views-matrix.svg"), W, H, *p)


# ── engine: один реєстр → п'ять перевірок → один звіт ─────────────────────────
def fig_engine():
    W, H = 980, 600
    p = [text(W / 2, 30, "Рушій: один реєстр — п'ять перевірок — один звіт", size=17, bold=True)]
    p.append(text(W / 2, 52,
                  "ті самі дані проходять крізь п'ять незалежних лінз і сходяться в перелік того, що підсвічено",
                  size=10.5, color=MUTED, italic=True))

    # вхід ліворуч — реєстр як дані
    ix, iy, iw, ih = 40, 250, 190, 120
    icx, icy = ix + iw / 2, iy + ih / 2
    p.append(rect(ix, iy, iw, ih, fill=F_GLD, stroke=GOLD_LINE, sw=2))
    p.append(text(icx, iy + 32, "Реєстр", size=14, bold=True))
    p.append(mtext(icx, iy + 56, ["хто · 3 булеві осі", "турбота · інтерес"],
                   size=10, color=MUTED, lh=1.4))
    p.append(text(icx, iy + 102, "як дані, не в голові", size=9.5, color=MUTED, italic=True))

    # п'ять перевірок посередині
    checks = [
        ("1 · Клас вагомості",   "3 булеві → 1 із 7 класів",    F_RED,  POS),
        ("2 · Квадрант сітки",   "влада × інтерес → 1 із 4",    F_BLUE, NEG),
        ("3 · Покриття турбот",  "турбота без рішення = діра",  F_GRN,  FIELD),
        ("4 · Точки компромісу", "спільний параметр, конфлікт", F_GLD,  GOLD_LINE),
        ("5 · Матриця в'ю",      "жоден рядок не порожній",     F_GREY, LINE),
    ]
    bx, bw, bh = 350, 300, 66
    ys = [92, 176, 260, 344, 428]
    centers = []
    for (t, sub, fill, stroke), by in zip(checks, ys):
        bcy = by + bh / 2
        centers.append(bcy)
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=stroke, sw=1.7))
        p.append(text(bx + bw / 2, by + 27, t, size=13, bold=True))
        p.append(text(bx + bw / 2, by + 48, sub, size=10, color=MUTED))
        p.append(arrow(ix + iw + 4, icy, bx - 6, bcy, color="#c9cdd3"))  # у лівому жолобі, повз написи

    # звіт праворуч — що рушій підсвічує
    rx, ry, rw, rh = 735, 175, 205, 260
    rcx, rcy = rx + rw / 2, ry + rh / 2
    p.append(rect(rx, ry, rw, rh, fill="#fff", stroke=INK, sw=2))
    p.append(text(rcx, ry + 30, "Звіт підсвічує", size=13, bold=True))
    report = [
        "— залежний без важеля",
        "— турбота без рішення",
        "— вето твердого порогу",
        "— компроміс на параметрі",
        "— голос без жодного в'ю",
    ]
    for i, r in enumerate(report):
        p.append(text(rx + 16, ry + 66 + i * 34, r, size=10.5, anchor="start"))
    for bcy in centers:
        p.append(arrow(bx + bw + 4, bcy, rx - 6, rcy, color="#c9cdd3"))  # у правому жолобі

    # підсумок унизу — окрема рамка, поза боксами й лініями
    box, _, _ = textbox(W / 2, 550,
        "Знімок фіксує миттєвий розподіл осей — щойно осі повзуть, рушій переганяють",
        size=11, pad=11, fill=F_GREY, min_w=560)
    p.append(box)

    render(os.path.join(OUT, "engine.svg"), W, H, *p)


# ── lattice: булів куб без порожньої вершини — 7 класів, яруси 1·3·3·1 ────────
def fig_lattice():
    W, H = 880, 600
    p = [text(W / 2, 30, "Ґратка вагомості: булів куб без порожньої вершини", size=17, bold=True)]
    p.append(text(W / 2, 51, "три бінарні ознаки → 2³−1 = 7 класів; яруси за числом ознак: 1·3·3·1",
                  size=10.5, color=MUTED, italic=True))

    y1, y2, y3 = 475, 320, 170          # латентні · очікувальні · визначальний
    hh, cw = 24, 164

    dorm = (195, y1, "сплячий", "влада", F_RED, POS)
    disc = (475, y1, "на-розсуд", "легітимність", F_BLUE, NEG)
    dem  = (755, y1, "вимогливий", "терміновість", F_GRN, FIELD)
    domi = (195, y2, "панівний", "влада+легітим.", F_GLD, GOLD_LINE)
    dang = (475, y2, "небезпечний", "влада+термін.", F_RED, POS)
    dep  = (755, y2, "залежний", "легітим.+термін.", F_BLUE, NEG)
    defi = (475, y3, "визначальний", "усі три ознаки", "#eafaf1", FIELD)
    nodes = [dorm, disc, dem, domi, dang, dep, defi]

    # ребра ґратки — підмножина ⊂ надмножина, різняться однією ознакою;
    # веду від краю рамки до краю рамки (у міжʼярусному просвіті, повз написи)
    edges = [(dorm, domi), (dorm, dang), (disc, domi), (disc, dep),
             (dem, dang), (dem, dep), (domi, defi), (dang, defi), (dep, defi)]
    for lo, up in edges:
        p.append(line(lo[0], lo[1] - hh, up[0], up[1] + hh, color="#c9cdd3", sw=1.4))
    # підсвічене ребро динаміки: сплячий, набувши терміновості, → небезпечний
    p.append(line(dorm[0], dorm[1] - hh, dang[0], dang[1] + hh, color=POS, sw=2.4, dash="5,4"))

    for cx, cy, name, sub, fill, stroke in nodes:
        p.append(rect(cx - cw / 2, cy - hh, cw, 2 * hh, fill=fill, stroke=stroke, sw=1.8))
        p.append(text(cx, cy - 4, name, size=13, bold=True))
        p.append(text(cx, cy + 14, sub, size=9.5, color=MUTED))

    for yy, lab in ((y1, "латентні"), (y2, "очікувальні"), (y3, "визначальний")):
        p.append(text(100, yy - 5, lab, size=11.5, bold=True, color=MUTED, anchor="end"))
    for yy, cnt in ((y1, "×3"), (y2, "×3"), (y3, "×1")):
        p.append(text(100, yy + 13, cnt, size=10, color=MUTED, anchor="end"))

    box, _, _ = textbox(W / 2, 565,
        "Ребро — набути чи втратити одну ознаку. Пунктиром: сплячий, діставши терміновості,\n"
        "стає небезпечним, а з легітимністю на додачу — визначальним.",
        size=11, pad=11, fill=F_GREY)
    p.append(box)
    render(os.path.join(OUT, "lattice.svg"), W, H, *p)


# ── projection: сітка «влада–інтерес» як проєкція куба, з волокнами ───────────
def fig_projection():
    W, H = 900, 620
    p = [text(W / 2, 30, "Сітка «влада–інтерес» — проєкція куба на дві осі", size=17, bold=True)]
    p.append(text(W / 2, 51, "π(влада, легітимність, терміновість) = (влада,  легітимність ∨ терміновість)",
                  size=11, color=MUTED, italic=True))

    gx, gy, gw, gh = 210, 90, 620, 380
    cw2, ch2 = gw / 2, gh / 2
    p.append(rect(gx, gy, cw2, ch2, fill=F_GLD, stroke=LINE, sw=1.2, rx=0))
    p.append(rect(gx + cw2, gy, cw2, ch2, fill=F_RED, stroke=LINE, sw=1.2, rx=0))
    p.append(rect(gx, gy + ch2, cw2, ch2, fill=F_GREY, stroke=LINE, sw=1.2, rx=0))
    p.append(rect(gx + cw2, gy + ch2, cw2, ch2, fill=F_BLUE, stroke=LINE, sw=1.2, rx=0))
    p.append(line(gx, gy + ch2, gx + gw, gy + ch2, color=INK, sw=1.6))
    p.append(line(gx + cw2, gy, gx + cw2, gy + gh, color=INK, sw=1.6))

    def chip(cx, cy, label):
        b, _, _ = textbox(cx, cy, label, size=10.5, pad=6, fill="#fff", min_w=158)
        return b

    lcx, rcx = gx + cw2 / 2, gx + cw2 + cw2 / 2
    # TL — тримати вдоволеним (волокно з одного)
    p.append(text(lcx, gy + 34, "тримати вдоволеним", size=12.5, bold=True))
    p.append(chip(lcx, gy + 82, "сплячий  (1·0·0)"))
    # TR — вести щільно (волокно з трьох)
    p.append(text(rcx, gy + 30, "вести щільно", size=12.5, bold=True))
    for i, lab in enumerate(["панівний  (1·1·0)", "небезпечний  (1·0·1)", "визначальний  (1·1·1)"]):
        p.append(chip(rcx, gy + 64 + i * 40, lab))
    # BL — спостерігати (порожньо)
    p.append(text(lcx, gy + ch2 + 34, "спостерігати", size=12.5, bold=True))
    p.append(text(lcx, gy + ch2 + 78, "(порожньо)", size=11, color=MUTED, italic=True))
    p.append(text(lcx, gy + ch2 + 100, "жоден справжній клас сюди не лягає", size=9.5, color=MUTED))
    # BR — тримати в курсі (волокно з трьох)
    p.append(text(rcx, gy + ch2 + 30, "тримати в курсі", size=12.5, bold=True))
    for i, lab in enumerate(["на-розсуд  (0·1·0)", "вимогливий  (0·0·1)", "залежний  (0·1·1)"]):
        p.append(chip(rcx, gy + ch2 + 64 + i * 40, lab))

    p.append(text(150, gy + ch2, "ВЛАДА", size=12, bold=True))
    p.append(text(180, gy + 18, "висока", size=9, color=MUTED))
    p.append(text(180, gy + gh - 8, "низька", size=9, color=MUTED))
    p.append(text(gx + gw / 2, gy + gh + 34, "ІНТЕРЕС = легітимність ∨ терміновість  →", size=11, bold=True))

    box, _, _ = textbox(W / 2, 562,
        "Проєкція не взаємно-однозначна: втрачено вісь легітимності. Тому в «вести щільно»\n"
        "небезпечний (примус) невідрізнити від панівного, а в «тримати в курсі» залежний\n"
        "(тихий оператор) зливається з вимогливим крикуном.",
        size=10.5, pad=11, fill=F_GREY)
    p.append(box)
    render(os.path.join(OUT, "projection.svg"), W, H, *p)


# ── compensation: геометрія зваженої суми проти твердого порога ───────────────
def fig_compensation():
    W, H = 720, 500
    p = [text(W / 2, 30, "Чому зважена сума обманює: геометрія компенсації", size=17, bold=True)]
    p.append(text(W / 2, 51, "більший бал за вподобаннями «викуповує» будь-який недобір — та не поріг-закон",
                  size=10.5, color=MUTED, italic=True))

    px, py, pw, ph = 150, 95, 520, 310
    p.append(rect(px, py, pw, ph, fill="#fff", stroke=LINE, sw=1.4, rx=0))

    thr_y = py + 195
    p.append(rect(px, thr_y, pw, py + ph - thr_y, fill="#fdecea", stroke="#f0c9c4", sw=1, rx=0))
    p.append(line(px, thr_y, px + pw, thr_y, color=POS, sw=1.8, dash="6,4"))
    p.append(text(px + 138, thr_y - 8, "поріг доступності — закон", size=10, color=POS))
    p.append(text(px + 150, thr_y + 42, "недійсна зона (порушено тверде обмеження)", size=10, color=POS))

    # напрям зростання зваженої суми (праворуч-угору)
    p.append(arrow(px + 300, py + 250, px + 430, py + 120, color=INK))
    p.append(text(px + 232, py + 262, "більша зважена сума", size=10, color=MUTED, italic=True))

    # осі
    p.append(text(78, py + ph / 2, "доступність", size=11, bold=True))
    p.append(text(120, py + 16, "висока", size=9, color=MUTED))
    p.append(text(120, py + ph - 6, "низька", size=9, color=MUTED))
    p.append(text(px + pw / 2, py + ph + 40, "виграш за вподобаннями (дешевше, швидше)  →", size=11, bold=True))

    # A — найвища сума, але в недійсній зоні; B — менша сума, зате дійсний
    Ax, Ay = px + pw - 78, thr_y + 66
    p.append(circle(Ax, Ay, 9, fill=F_RED, stroke=POS, sw=2))
    p.append(text(Ax, Ay - 18, "A — найвища сума", size=10, color=POS, bold=True))
    p.append(text(Ax, Ay + 26, "але нижче порога", size=9, color=POS))
    Bx, By = px + 150, py + 78
    p.append(circle(Bx, By, 9, fill=F_GRN, stroke=FIELD, sw=2))
    p.append(text(Bx, By - 18, "B — менша сума", size=10, color=FIELD, bold=True))
    p.append(text(Bx, By + 26, "зате дійсний", size=9, color=FIELD))

    box, _, _ = textbox(W / 2, 472,
        "Спершу відсій недійсні порогом, і лише тоді максимізуй суму серед дійсних.",
        size=11, pad=10, fill=F_GREY)
    p.append(box)
    render(os.path.join(OUT, "compensation.svg"), W, H, *p)


# ── swap: аргумент обміну сусідів — звідки береться відношення WSJF ───────────
def fig_swap():
    W, H = 820, 430
    p = [text(W / 2, 30, "WSJF як оптимум: аргумент обміну сусідів", size=17, bold=True)]
    p.append(text(W / 2, 51, "переставити двох сусідів вигідно ⇔ першим іде більший wᵢ / pᵢ",
                  size=10.5, color=MUTED, italic=True))
    p.append(line(410, 78, 410, 348, color="#c9cdd3", sw=1.4, dash="4,5"))

    # ліворуч: i перший → j чекає зайві pᵢ → крос-ціна wⱼ·pᵢ (широка, низька)
    p.append(text(230, 92, "i перший → j чекає зайві pᵢ", size=12, bold=True))
    p.append(rect(155, 220, 150, 80, fill=F_BLUE, stroke=NEG, sw=1.8))
    p.append(text(230, 266, "wⱼ · pᵢ", size=15, bold=True))
    p.append(text(230, 322, "← pᵢ →", size=10, color=MUTED))
    p.append(text(138, 260, "wⱼ", size=10, color=MUTED))
    p.append(text(230, 344, "ціна: j чекає, поки триває i", size=9.5, color=MUTED))

    # праворуч: j перший → i чекає зайві pⱼ → крос-ціна wᵢ·pⱼ (вузька, висока)
    p.append(text(590, 92, "j перший → i чекає зайві pⱼ", size=12, bold=True))
    p.append(rect(550, 185, 80, 115, fill=F_RED, stroke=POS, sw=1.8))
    p.append(text(590, 248, "wᵢ · pⱼ", size=15, bold=True))
    p.append(text(590, 322, "← pⱼ →", size=10, color=MUTED))
    p.append(text(520, 240, "wᵢ", size=10, color=MUTED))
    p.append(text(590, 344, "ціна: i чекає, поки триває j", size=9.5, color=MUTED))

    box, _, _ = textbox(W / 2, 388,
        "Різниця порядків (i,j) − (j,i) = wⱼ·pᵢ − wᵢ·pⱼ   ⇒   i перший вигідно ⇔ wᵢ/pᵢ > wⱼ/pⱼ",
        size=11.5, pad=11, fill=F_GREY, min_w=560)
    p.append(box)
    render(os.path.join(OUT, "swap.svg"), W, H, *p)


if __name__ == "__main__":
    fig_origin()
    fig_classes()
    fig_chain()
    fig_timeline()
    fig_salience()
    fig_grid()
    fig_tradeoff()
    fig_views()
    fig_engine()
    fig_lattice()
    fig_projection()
    fig_compensation()
    fig_swap()
    print("figs done")
