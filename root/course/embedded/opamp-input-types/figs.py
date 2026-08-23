# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Типи входів ОП: BJT, JFET, CMOS» (root/course/embedded/kola).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ───────────────────────────────────────────────────────────────────────────
# 1. Три типи вхідного транзистора: куди й чому тече (чи не тече) вхідний струм
# ───────────────────────────────────────────────────────────────────────────
def fig_three_inputs():
    W, H = 760, 360
    f = []
    col = [130, 380, 630]
    titles = ["BJT (біполярний)", "JFET (польовий p-n)", "CMOS (MOSFET)"]
    pin = ["база", "затвор", "затвор"]
    # підпис струму під кожним стовпцем
    cur = ["~нА: струм бази тече",
           "~пА: дрібний струм витоку",
           "~фА: затвор ізольовано"]
    curcol = [POS, "#b8860b", FIELD]
    for i, cx in enumerate(col):
        f.append(text(cx, 56, titles[i], size=15, bold=True))
        # символ транзистора як проста піктограма
        ty = 150
        if i == 0:
            # BJT: вертикальна лінія-база, стрілка струму ВНУТРІШ
            f.append(line(cx - 6, ty - 38, cx - 6, ty + 38, color=INK, sw=3))           # тіло
            f.append(line(cx - 6, ty - 22, cx + 34, ty - 40, color=INK, sw=2))           # колектор
            f.append(line(cx - 6, ty + 22, cx + 34, ty + 40, color=INK, sw=2))           # емітер
            f.append(arrow(cx - 60, ty, cx - 12, ty, color=POS, sw=2.4))                 # струм у базу
            f.append(text(cx - 58, ty - 12, "вхід", size=12, anchor="start", color=POS))
            f.append(text(cx + 40, ty - 40, "C", size=11, anchor="start"))
            f.append(text(cx + 40, ty + 44, "E", size=11, anchor="start"))
        else:
            # FET/MOSFET: затвор не торкається каналу (зазор)
            chx = cx + 6
            f.append(line(chx, ty - 38, chx, ty + 38, color=INK, sw=3))                  # канал
            f.append(line(chx, ty - 30, chx + 34, ty - 30, color=INK, sw=2))             # стік
            f.append(line(chx, ty + 30, chx + 34, ty + 30, color=INK, sw=2))             # витік
            # затвор з ЗАЗОРОМ від каналу
            gap = 8 if i == 2 else 3
            f.append(line(cx - 60, ty, chx - gap, ty, color=curcol[i], sw=2.4))          # підвід до затвора
            f.append(line(chx - gap, ty - 22, chx - gap, ty + 22, color=INK, sw=3))      # пластина затвора
            f.append(text(cx - 58, ty - 12, "вхід", size=12, anchor="start", color=curcol[i]))
            f.append(text(chx + 40, ty - 34, "D", size=11, anchor="start"))
            f.append(text(chx + 40, ty + 38, "S", size=11, anchor="start"))
            # для CMOS показати ізолятор (оксид) як зелену смужку в зазорі
            if i == 2:
                f.append(rect(chx - gap, ty - 22, 4, 44, fill="#d6f0e0", stroke=FIELD, sw=1.2, rx=1))
                f.append(text(chx - gap + 2, ty + 64, "оксид", size=10, color=FIELD))
        # рамка з висновком по струму
        bx, _, _ = textbox(cx, 268, cur[i], size=12, color=curcol[i], bold=True,
                           fill="#f7f9fb", min_w=180)
        f.append(bx)
    # нижній підсумок-нитка
    bx, _, _ = textbox(W / 2, 326, "Що тече у вхід — те й псує точність на великому опорі джерела",
                       size=12, fill="#eef6ff", stroke=NEG, min_w=560)
    f.append(bx)
    render(os.path.join(IMG, "three-inputs.svg"), W, H, *f,
           title="Вхідний транзистор: куди дівається вхідний струм")


# ───────────────────────────────────────────────────────────────────────────
# 2. Вхідний струм трьох родин — логарифмічна шкала (масштаб різниці)
# ───────────────────────────────────────────────────────────────────────────
def fig_bias_scale():
    W, H = 760, 300
    f = []
    # вісь log10(струм, А): від -15 (фА) до -6 (мкА)
    x0, x1 = 90, 700
    ybar = 150
    def X(log10A):  # лінійно по показнику
        return x0 + (log10A - (-15)) / ((-6) - (-15)) * (x1 - x0)
    # шкала-вісь із підписами декад
    f.append(line(x0, ybar + 70, x1, ybar + 70, color=MUTED, sw=1.5))
    for lg, lab in [(-15, "фА"), (-12, "пА"), (-9, "нА"), (-6, "мкА")]:
        xx = X(lg)
        f.append(line(xx, ybar + 66, xx, ybar + 74, color=MUTED, sw=1.5))
        f.append(text(xx, ybar + 90, lab, size=12, color=MUTED))
    # три «прапорці» з типовими значеннями
    rows = [
        ("BJT", -7.1, "~80 нА (µA741)", POS),      # ~10^-7.1 ≈ 80 нА
        ("JFET", -11.5, "~30 пА (LF356)", "#b8860b"),
        ("CMOS", -14.0, "~10 фА (типово)", FIELD),
    ]
    yy = [70, 105, 140]
    for i, (name, lg, lab, c) in enumerate(rows):
        y = 60 + i * 34
        xx = X(lg)
        f.append(text(x0 - 8, y + 5, name, size=14, bold=True, anchor="end", color=c))
        f.append(line(x0, y, xx, y, color=c, sw=6))
        f.append(circle(xx, y, 5, fill=c, stroke=c, sw=1))
        f.append(text(xx + 12, y + 5, lab, size=12, anchor="start", color=c))
    # стрілка-підказка «менше = краще для високоомного входу»
    f.append(arrow(X(-7), ybar + 118, X(-13.5), ybar + 118, color=NEG, sw=2))
    f.append(text(X(-10.2), ybar + 110, "менший вхідний струм →", size=12, color=NEG))
    f.append(text(X(-10.2), ybar + 134, "менша похибка на великому R", size=11, color=NEG))
    render(os.path.join(IMG, "bias-scale.svg"), W, H, *f,
           title="Типовий вхідний струм: різниця в мільйони разів (log-шкала)")


# ───────────────────────────────────────────────────────────────────────────
# 3. Чому це кусає: вхідний струм × великий резистор = похибка
# ───────────────────────────────────────────────────────────────────────────
def fig_why_matters():
    W, H = 760, 330
    f = []
    # дві однакові схеми: ліворуч BJT, праворуч FET; джерело 10 МОм
    def stage(cx, label, ib_txt, err_txt, c, ok):
        # резистор джерела згори вниз у вузол входу
        node_y = 150
        f.append(text(cx, 54, label, size=14, bold=True, color=c))
        f.append(line(cx, 80, cx, 110, color=INK, sw=1.8))
        f.append(rect(cx - 9, 110, 18, 44, fill="#eef1f5", stroke=INK, sw=1.6, rx=3))  # R 10М
        f.append(text(cx + 16, 134, "10 МОм", size=11, anchor="start"))
        f.append(text(cx, 74, "давач", size=11))
        # вузол входу
        f.append(line(cx, 154, cx, node_y + 36, color=INK, sw=1.8))
        f.append(circle(cx, node_y + 36, 3.5, fill=INK, stroke=INK))
        # стрілка вхідного струму ОП (тягне з вузла)
        f.append(arrow(cx, node_y + 36, cx + 52, node_y + 36, color=c, sw=2.2))
        f.append(text(cx + 56, node_y + 41, ib_txt, size=11, anchor="start", color=c))
        # рамка похибки
        bx, _, _ = textbox(cx, node_y + 96, err_txt, size=12, color=("white" if ok else "white"),
                           fill=(FIELD if ok else POS), stroke=(FIELD if ok else POS),
                           bold=True, min_w=210)
        f.append(bx)
    stage(210, "BJT-входи", "I≈80 нА", "80нА × 10МОм = 0.8 В похибки", POS, ok=False)
    stage(560, "FET-входи", "I≈30 пА", "30пА × 10МОм = 0.3 мВ — дріб'язок", FIELD, ok=True)
    f.append(line(385, 70, 385, 270, color="#e5e7eb", sw=1.5, dash="4 5"))
    bx, _, _ = textbox(W / 2, 308,
                       "Та сама схема, та сама напруга — різниця лише в типі входу",
                       size=12, fill="#f7f9fb", min_w=520)
    f.append(bx)
    render(os.path.join(IMG, "why-matters.svg"), W, H, *f,
           title="Високоомне джерело: вхідний струм перетворюється на похибку")


# ───────────────────────────────────────────────────────────────────────────
# 4. Карта вибору: яка задача — який вхід
# ───────────────────────────────────────────────────────────────────────────
def fig_decision():
    W, H = 760, 360
    f = []
    cards = [
        ("BJT-входи", POS, [
            "малий зсув і дрейф (точний DC)",
            "найменший шум напруги",
            "джерело НИЗЬКООМНЕ",
            "міст, шунт, термопара",
        ]),
        ("JFET-входи", "#b8860b", [
            "високоомне джерело",
            "малий вхідний струм (пА)",
            "швидкість + малий струм",
            "п'єзо, фотодіод, інтегратор",
        ]),
        ("CMOS-входи", FIELD, [
            "НАЙменший вхідний струм (фА)",
            "rail-to-rail, мікроспоживання",
            "однополярне живлення, батарея",
            "pH-електрод, заряд, портативне",
        ]),
    ]
    cw, gap = 230, 20
    x = (W - (cw * 3 + gap * 2)) / 2
    for name, c, items in cards:
        f.append(rect(x, 50, cw, 280, fill="#fbfcfd", stroke=c, sw=2, rx=10))
        f.append(rect(x, 50, cw, 36, fill=c, stroke=c, sw=2, rx=10))
        f.append(text(x + cw / 2, 74, name, size=15, bold=True, color="white"))
        yy = 116
        for it in items:
            f.append(circle(x + 20, yy - 4, 3.5, fill=c, stroke=c))
            f.append(fitbox(x + 32, yy - 18, cw - 44, 28, it, size=12, pad=2,
                            fill="none", stroke="none"))
            yy += 44
        x += cw + gap
    render(os.path.join(IMG, "decision-map.svg"), W, H, *f,
           title="Який тип входу під яку задачу")


# ───────────────────────────────────────────────────────────────────────────
# 5. Історія вхідних каскадів: спільна вісь часу трьох родин (для hist-вставки)
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_timeline():
    # Вертикальний час: три колонки-родини, згори вниз — по три віхи.
    # Жодних наскрізних ліній крізь написи, колонки не наскакують.
    W, H = 760, 440
    f = []
    cols = [
        ("Біполярні (BJT)", POS, [
            (1952, "K2-W", "лампова класика (Philbrick)"),
            (1964, "µA702", "перший монолітний IC-ОП"),
            (1968, "µA741", "внутрішня корекція"),
        ]),
        ("Польові p-n (JFET)", "#b8860b", [
            (1965, "варактор / модулі", "вхідний струм < 1 пА"),
            (1974, "BiFET", "JFET і BJT на кристалі"),
            (1978, "LF356 / TL07x", "масовий JFET-ОП"),
        ]),
        ("МОН (CMOS)", FIELD, [
            (1963, "патент CMOS", "Ф. Ванласс, Fairchild"),
            (1974, "CA3130", "MOSFET-вхід (BiMOS)"),
            (1976, "ICL7611", "повний CMOS-ОП"),
        ]),
    ]
    cw = 230
    gap = 20
    xL = (W - (cw * 3 + gap * 2)) / 2
    ytop, ystep = 116, 100
    for ci, (name, c, evs) in enumerate(cols):
        cx = xL + ci * (cw + gap) + cw / 2
        # заголовок-родина
        f.append(rect(cx - cw / 2, 50, cw, 34, fill=c, stroke=c, rx=8))
        f.append(text(cx, 72, name, size=14, bold=True, color="white"))
        # вертикальна вісь колонки — ЗЛІВА від написів (не крізь них)
        axx = cx - cw / 2 + 26
        f.append(line(axx, ytop - 8, axx, ytop + 2 * ystep + 30, color=c, sw=2))
        for ei, (yr, big, small) in enumerate(evs):
            ey = ytop + ei * ystep
            f.append(circle(axx, ey, 6, fill=c, stroke=c))
            f.append(text(axx - 14, ey + 5, str(yr), size=13, bold=True, anchor="end", color=c))
            # підписи — праворуч від осі, у власних рамках (текст не вилазить)
            f.append(fitbox(axx + 12, ey - 16, cw / 2 + 62, 22, big, size=12,
                            bold=True, fill="#fbfcfd", stroke=c, rx=5))
            f.append(fitbox(axx + 12, ey + 8, cw / 2 + 62, 20, small, size=10,
                            color=MUTED, fill="none", stroke="none"))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f,
           title="Народження трьох родин входів ОП (роки веб-звірені)")


if __name__ == "__main__":
    fig_three_inputs()
    fig_bias_scale()
    fig_why_matters()
    fig_decision()
    fig_hist_timeline()
    print("OK: 5 фігур записано в", IMG)
