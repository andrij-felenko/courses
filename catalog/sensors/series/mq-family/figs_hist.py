# -*- coding: utf-8 -*-
"""Фігури до історичної вставки «hist-taguchi-mq» (тека теми mq-family).
Вивід — ./img/hist-*.svg. Запуск: python figs_hist.py
Ці фігури — ІСТОРИЧНІ (хронологія людей від ефекту до дешевої родини) і
навмисно НЕ дублюють родовід самої статті (mq-lineage.svg — три вузли-принцип).
Підписи розставлено з ЗАПАСОМ; конектори НЕ перетинають чужих написів."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WARM = "#d6a419"
GRN = "#1e7a46"


# ── 1. Хронологія: ланцюг людей від ефекту в лабораторії до дешевої родини ─────
# Кожна віха — окрема картка у СВОЄМУ рядку-поверсі; коротка риска йде від осі
# до краю картки й зупиняється НА краю (не входить у зону тексту).
def fig_timeline():
    W, H = 1000, 600
    f = []
    f.append(text(500, 32, "Від ефекту до дешевої родини: ланцюг людей, а не один винахідник",
                  size=16, bold=True))

    ax_x0, ax_x1, ay = 60, 940, 315
    f.append(line(ax_x0, ay, ax_x1, ay, color=INK, sw=2.2))
    f.append(arrow(ax_x1 - 2, ay, ax_x1 + 2, ay, color=INK, sw=2.2))
    f.append(text(ax_x1 - 4, ay + 62, "час", size=11, color=MUTED, anchor="end"))

    def X(year):
        return ax_x0 + (year - 1950) / (2006 - 1950) * (ax_x1 - ax_x0 - 26)

    # три епохи-смуги ПРЯМО на осі — лише кольорові плашки-групи (без підпису в
    # корі́, куди опускаються конектори); зміст епохи несуть самі картки та колір.
    for (y0, y1, col, lc) in [
        (1950, 1966, "#dfe9ff", NEG),
        (1967, 1975, "#ffeec2", WARM),
        (1997, 2006, "#d6f2e2", GRN),
    ]:
        x0, x1 = X(y0), X(y1)
        f.append(rect(x0, ay - 7, x1 - x0, 14, fill=col, stroke=lc, sw=1.0, rx=4))
    # легенда епох — праворуч угорі, поза корид́ором конекторів
    lx, lyv = 60, 560
    f.append(text(lx, lyv, "фізика (ЧОМУ опір міняється)", size=10.5, color=NEG, bold=True, anchor="start"))
    f.append(text(lx + 250, lyv, "перший прилад", size=10.5, color=WARM, bold=True, anchor="start"))
    f.append(text(lx + 420, lyv, "дешева китайська родина", size=10.5, color=GRN, bold=True, anchor="start"))

    # віхи. floor_y — центр картки; риска йде від осі й спиняється на краю картки.
    # Угору три різні поверхи, униз два — щоб сусіди по осі не налазили.
    ups = [
        (1953, 96,  "1953 · Бреттейн і Бардін (Bell Labs)\nповерхня германію міняє провідність від газу", NEG),
        (1968, 168, "1968 · Наойосі Тагучі — серійний давач\nна SnO₂ (TGS); перший TGS109, на метан", WARM),
        (1998, 96,  "1998 · Hanwei (Чженчжоу)\nдешеві нащадки — родина MQ", GRN),
    ]
    downs = [
        (1962, 420, "1962 · Тайосі Сеяма (Японія)\nтой ефект — на оксиді металу (ZnO)", NEG),
        (1969, 492, "1969 · засновано Figaro\n(на честь героя опери Россіні)", WARM),
        (2003, 420, "2003 · Winsen — нині масовий\nвиробник елементів MQ", GRN),
    ]

    def place(yr, cy, lab, col, above):
        x = X(yr)
        # спершу зміряти картку, тоді центрувати з утриманням у полотні
        _, w, h = textbox(0, 0, lab, size=10.5, pad=9, bold=False)
        cx = min(max(x, 46 + w / 2), W - 46 - w / 2)
        b, w, h = textbox(cx, cy, lab, size=10.5, pad=9, fill="#ffffff", stroke=col, color=INK)
        out = [circle(x, ay, 5.5, fill="#fff", stroke=col, sw=2.4)]
        if above:
            out.append(line(x, ay - 6, x, cy + h / 2, color=col, sw=1.2))  # до НИЖНЬОГО краю картки
        else:
            out.append(line(x, ay + 6, x, cy - h / 2, color=col, sw=1.2))  # до ВЕРХНЬОГО краю картки
        out.append(b)
        return out

    for (yr, cy, lab, col) in ups:
        f += place(yr, cy, lab, col, above=True)
    for (yr, cy, lab, col) in downs:
        f += place(yr, cy, lab, col, above=False)

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── 2. Чому «MQ» без слова-кореня: позначка серії, а не абревіатура ────────────
def fig_naming():
    W, H = 900, 340
    f = []
    f.append(text(450, 32, "Чому «MQ» нічого не «розшифровується»", size=16, bold=True))

    b1, w1, h1 = textbox(210, 118,
                         "Здається:\n«MQ» — абревіатура,\nза буквами — якісь слова",
                         size=12.5, pad=13, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(680, 118,
                         "Насправді:\n«MQ-» — лише префікс серії.\nВесь зміст — у числі після нього",
                         size=12.5, pad=13, fill="#eafaf0", stroke=FIELD, color=GRN, bold=True)
    f.append(b2)
    f.append(arrow(210 + w1 / 2 + 4, 118, 680 - w2 / 2 - 4, 118, color=INK, sw=2))
    f.append(text((210 + w1 / 2 + 680 - w2 / 2) / 2, 104, "розшифровки немає", size=10, color=MUTED))

    # розклад прикладу MQ-135: підписи рознесено ДАЛЕКО вбік (ліворуч і праворуч),
    # кожен зі своєю короткою рискою від відповідної частини напису.
    py = 232
    f.append(text(450, py, "MQ-135", size=28, bold=True, color=INK))
    # «MQ-» → риска ліворуч-вниз до лівого підпису
    f.append(line(408, py + 14, 250, py + 44, color=MUTED, sw=1.2))
    f.append(mtext(190, py + 62, ["префікс серії", "(без слова за буквами)"], size=10.5, color=MUTED, anchor="middle"))
    # «135» → риска праворуч-вниз до правого підпису
    f.append(line(492, py + 14, 660, py + 44, color=GRN, sw=1.2))
    f.append(mtext(730, py + 62, ["число — ось воно й каже,", "під який газ заточено шар"], size=10.5, color=GRN, anchor="middle"))

    render(os.path.join(IMG, "hist-naming.svg"), W, H, *f)


if __name__ == "__main__":
    fig_timeline()
    fig_naming()
    print("OK: hist-timeline.svg, hist-naming.svg")
