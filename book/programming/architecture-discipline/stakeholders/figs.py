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


if __name__ == "__main__":
    fig_origin()
    fig_classes()
    fig_chain()
    fig_timeline()
    print("figs done")
