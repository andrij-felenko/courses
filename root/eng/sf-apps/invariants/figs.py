# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Вікно спостереження: інваріант тримається у спокої, провалюється в операції ─
def fig_observation_window():
    W, H = 940, 470
    frags = []

    axis_y = 300           # рівень часової осі
    top    = 150           # верх смуги «коректно»
    dip    = 235           # низ провалу (порушення)
    x0, x1 = 70, 870

    # Часова вісь
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 - 40, axis_y, x1 + 6, axis_y, color=INK, sw=2))
    frags.append(text(x1 + 4, axis_y + 26, "час", size=13, color=MUTED, anchor="end"))

    # Дві операції — вертикальні смуги, де інваріант тимчасово провалюється
    ops = [(300, 400), (560, 660)]   # (початок, кінець) кожної операції по x

    # Крива стану: суцільна на висоті top у спокої, провал до dip у межах операції.
    # Малюємо як ламану полілінію.
    pts = [(x0, top)]
    for (a, b) in ops:
        pts.append((a, top))          # підійшли до операції на рівні «коректно»
        pts.append((a + 12, dip))     # різко провалилися всередину
        pts.append((b - 12, dip))     # тримаємось провалу до кінця операції
        pts.append((b, top))          # звели докупи — знову коректно
    pts.append((x1 - 30, top))
    poly = " ".join("%.1f,%.1f" % (px, py) for (px, py) in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (poly, FIELD))

    # Затінити зони операцій + підписати «всередині»
    for i, (a, b) in enumerate(ops):
        frags.append(rect(a, top - 6, b - a, axis_y - top + 6,
                          fill="#fdf0ee", stroke=POS, sw=1.4, rx=8))
        frags.append(text((a + b) / 2, axis_y + 22, "операція %d" % (i + 1),
                          size=13, bold=True, color=POS))

    # Підпис провалу — під смугами, щоб не накладатися на криву/рамки
    frags.append(text((ops[0][0] + ops[0][1]) / 2, dip + 30,
                      "інваріант", size=12, color=POS))
    frags.append(text((ops[0][0] + ops[0][1]) / 2, dip + 47,
                      "тимчасово порушено", size=12, color=POS))

    # Підпис рівня «коректно» — ліворуч над лінією стану, у власній рамці
    lb, lbw, lbh = textbox(x0 + 95, top - 40, "стан коректний",
                           size=13, bold=True, pad=9,
                           fill="#eafaf1", stroke=FIELD, sw=1.6)
    frags.append(lb)

    # Позначки «погляд ззовні» на проміжках спокою (між/поза операціями)
    rest_x = [(x0 + ops[0][0]) / 2, (ops[0][1] + ops[1][0]) / 2, (ops[1][1] + x1 - 30) / 2]
    for rx in rest_x:
        frags.append(circle(rx, top, 5, fill=FIELD, stroke=FIELD, sw=1))
    mid = rest_x[1]
    frags.append(text(mid, top - 20, "погляд ззовні —", size=12, bold=True, color=FIELD))
    frags.append(text(mid, top - 4, "тут виконується", size=12, color=FIELD))

    render(os.path.join(IMG, 'observation-window.svg'), W, H, *frags,
           title="Інваріант: тримається у спокої, може провалитися всередині операції")


# ── Драбина захисту: від сподівання (низ) до неможливості (верх) ──────────────
def fig_defense_ladder():
    W, H = 940, 540
    frags = []

    # Чотири щаблі знизу вгору. Кожен ширший однаково, з підписом-фразою.
    rungs = [
        ("нічого — лише сподівання на дисципліну",
         "правило в голові, поля відкриті — порушать неминуче", POS,   "#fdf0ee"),
        ("перевірка під час виконання",
         "падає на порушенні — у місці й у момент, а не потім",  "#e08a1e", "#fdf3e3"),
        ("інкапсуляція",
         "порушити можна лише через код самого класу",           NEG,   "#eef3ff"),
        ("тип",
         "некоректний стан неможливо навіть виразити",           FIELD, "#eafaf1"),
    ]

    rung_w = 620
    rung_h = 74
    gap    = 18
    x = 150
    # Малюємо знизу вгору: перший елемент списку — найнижчий.
    base_y = 470   # y верхнього краю найнижчого щабля
    for i, (title, sub, col, fill) in enumerate(rungs):
        y = base_y - i * (rung_h + gap)
        frags.append(rect(x, y, rung_w, rung_h, fill=fill, stroke=col, sw=2.2, rx=10))
        frags.append(text(x + rung_w / 2, y + 30, title, size=16, bold=True, color=col))
        frags.append(text(x + rung_w / 2, y + 54, sub, size=12.5, color=INK))

    # Стрілка сили збоку: знизу вгору — «ловиться раніше, людині лишається менше»
    ax = x + rung_w + 46
    y_bottom = base_y + rung_h
    y_top    = base_y - (len(rungs) - 1) * (rung_h + gap)
    frags.append(arrow(ax, y_bottom, ax, y_top - 6, color=INK, sw=2.4))
    # Підписи стрілки — вертикально розкладені збоку, поза щаблями
    frags.append(text(ax + 18, y_top + 30, "порушення", size=12.5, bold=True, anchor="start"))
    frags.append(text(ax + 18, y_top + 48, "ловиться", size=12, anchor="start", color=MUTED))
    frags.append(text(ax + 18, y_top + 64, "раніше", size=12, anchor="start", color=MUTED))
    frags.append(text(ax + 18, y_bottom - 8, "слабший", size=12, bold=True,
                      anchor="start", color=POS))

    # Підпис лівої шкали — «сила гарантії» вертикально біля щаблів
    frags.append(text(x - 24, (y_top + y_bottom) / 2, "сильніше",
                      size=12.5, bold=True, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'defense-ladder.svg'), W, H, *frags,
           title="Драбина захисту інваріанта: вище — раніше й надійніше")


# ── Родовід інваріанта: доведення (1967–72) → дизайн (1985–86) ─────────────────
# (фігура для вставки hist-invariant-lineage.md; окремий файл, чужих не чіпає)
def fig_invariant_lineage():
    W, H = 1000, 560
    frags = []

    axis_y = 300
    x0, x1 = 60, 940

    # Дві зони: ліворуч «доведення», праворуч «дизайн». Межа між 1972 і 1985.
    split_x = 650
    frags.append(rect(x0 - 6, 70, split_x - x0 + 6, 420,
                      fill="#eef3ff", stroke="#eef3ff", sw=0, rx=14))
    frags.append(rect(split_x, 70, x1 - split_x + 6, 420,
                      fill="#eafaf1", stroke="#eafaf1", sw=0, rx=14))
    # межова пунктирна лінія
    frags.append(line(split_x, 78, split_x, 482, color=MUTED, sw=1.6, dash="6 6"))

    # Підписи зон — угорі, кожен у своїй половині, далеко один від одного
    frags.append(text((x0 + split_x) / 2, 100, "інструмент доведення",
                      size=16, bold=True, color=NEG))
    frags.append(text((x0 + split_x) / 2, 122, "(для фахівців)",
                      size=13, color=NEG))
    frags.append(text((split_x + x1) / 2, 100, "інструмент дизайну",
                      size=16, bold=True, color=FIELD))
    frags.append(text((split_x + x1) / 2, 122, "(для щодення)",
                      size=13, color=FIELD))

    # Часова вісь
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(arrow(x1 - 34, axis_y, x1 + 4, axis_y, color=INK, sw=2.4))
    frags.append(text(x1 + 2, axis_y + 28, "час", size=13, color=MUTED, anchor="end"))

    # Чотири віхи: (x, рік, автор, три рядки суті, колір, картка-зверху?)
    milestones = [
        (175, "1967", "Флойд",
         ["метод індуктивних", "тверджень: інваріант", "на петлі блок-схеми"], NEG, True),
        (355, "1969", "Гоар",
         ["логіка Гоара:", "інваріант циклу —", "правило виведення"], NEG, False),
        (540, "1972", "Гоар",
         ["інваріант представлення;", "перший «інваріант класу»:", "злазить із циклу на дані"], NEG, True),
        (800, "1985–86", "Меєр",
         ["Eiffel + Design by Contract:", "клас-інваріант —", "конструкція мови"], FIELD, False),
    ]

    card_w = 250
    card_h = 92
    for (mx, year, who, lines, col, above) in milestones:
        # вузол на осі
        frags.append(circle(mx, axis_y, 8, fill=col, stroke=col, sw=1))
        # рік — жирно з боку осі, протилежного картці
        if above:
            frags.append(text(mx, axis_y + 30, year, size=15, bold=True, color=col))
            cy = axis_y - 14 - card_h / 2       # картка над віссю
        else:
            frags.append(text(mx, axis_y - 20, year, size=15, bold=True, color=col))
            cy = axis_y + 34 + card_h / 2        # картка під віссю
        cx = mx
        # тримати картку в межах полотна
        if cx - card_w / 2 < x0:
            cx = x0 + card_w / 2
        if cx + card_w / 2 > x1:
            cx = x1 - card_w / 2
        # з'єднувач вузол→картка
        conn_y = (axis_y - 14) if above else (axis_y + 34)
        frags.append(line(mx, axis_y + (-8 if above else 8), mx, conn_y,
                          color=col, sw=1.6))
        # тіло картки: заголовок-автор + три рядки суті
        cy_top = cy - card_h / 2
        frags.append(rect(cx - card_w / 2, cy_top, card_w, card_h,
                          fill=BG, stroke=col, sw=2, rx=10))
        frags.append(text(cx, cy_top + 24, who, size=15, bold=True, color=col))
        for i, ln in enumerate(lines):
            frags.append(text(cx, cy_top + 45 + i * 16, ln, size=12, color=INK))

    render(os.path.join(IMG, 'invariant-lineage.svg'), W, H, *frags,
           title="Родовід інваріанта: з доведення — у дизайн")


if __name__ == "__main__":
    fig_observation_window()
    fig_defense_ladder()
    fig_invariant_lineage()
    print("OK: figures written to", IMG)
