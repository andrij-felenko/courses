# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── anatomy: як виглядає дерево живлення реального пристрою ────────────────────
# Ідея: одна картинка, що читач має навчитися читати. Корінь — джерело, гілки —
# перетворювачі, листя — навантаження. Поряд із кожною стрілкою — напруга шини.
def fig_anatomy():
    W, H = 760, 430
    p = []

    def node(cx, cy, w, h, lines, fill=FILL, stroke=LINE, color=INK, sw=1.6):
        p.append(fitbox(cx - w / 2, cy - h / 2, w, h, "\n".join(lines),
                        size=13, fill=fill, stroke=stroke, color=color, sw=sw))

    def rail(x1, y, x2, label):
        p.append(arrow(x1, y, x2, y, color=INK, sw=2))
        p.append(text((x1 + x2) / 2, y - 8, label, size=12, color=NEG, bold=True))

    # колонки за рівнями дерева
    xsrc, xprot, xconv, xload = 80, 230, 410, 640

    # корінь: джерело
    node(xsrc, 215, 110, 70, ["БАТАРЕЯ", "1S Li-ion", "3.0–4.2 В"],
         fill="#eaf0fd", stroke=NEG, color=NEG)

    # захист входу
    node(xprot, 215, 110, 64, ["Захист входу", "переполюс. +", "запобіжник"])

    rail(135, 215, 175, "VBAT")
    rail(285, 215, 355, "VBAT")

    # перетворювачі (дві гілки)
    node(xconv, 130, 120, 62, ["BUCK", "→ 3.3 В", "η ≈ 92 %"], fill="#eafaf0", stroke=FIELD)
    node(xconv, 300, 120, 62, ["BOOST", "→ 5.0 В", "η ≈ 90 %"], fill="#eafaf0", stroke=FIELD)

    # розгалуження від захисту до двох перетворювачів
    p.append(line(285, 215, 320, 215, color=INK, sw=2))
    p.append(line(320, 130, 320, 300, color=INK, sw=2))
    p.append(arrow(320, 130, 350, 130, color=INK, sw=2))
    p.append(arrow(320, 300, 350, 300, color=INK, sw=2))

    # листя від buck 3.3 В
    node(xload, 70, 150, 40, ["MCU  (ESP32)"], fill="#fff7e6", stroke="#d6a400")
    node(xload, 130, 150, 40, ["Давачі  I²C"], fill="#fff7e6", stroke="#d6a400")
    node(xload, 190, 150, 40, ["Flash"], fill="#fff7e6", stroke="#d6a400")
    p.append(line(470, 130, 545, 130, color=INK, sw=2))
    for yy in (70, 130, 190):
        p.append(line(545, 130, 545, yy, color=INK, sw=2))
        p.append(arrow(545, yy, 565, yy, color=INK, sw=2))
    p.append(text(520, 118, "3.3 В", size=12, color=NEG, bold=True))

    # листя від boost 5 В
    node(xload, 280, 150, 40, ["USB-вихід"], fill="#fff7e6", stroke="#d6a400")
    node(xload, 340, 150, 40, ["Дисплей"], fill="#fff7e6", stroke="#d6a400")
    p.append(line(470, 300, 545, 300, color=INK, sw=2))
    for yy in (280, 340):
        p.append(line(545, 300, 545, yy, color=INK, sw=2))
        p.append(arrow(545, yy, 565, yy, color=INK, sw=2))
    p.append(text(520, 288, "5.0 В", size=12, color=NEG, bold=True))

    # підписи рівнів
    p.append(text(xsrc, 395, "КОРІНЬ", size=12, color=MUTED, bold=True))
    p.append(text(xsrc, 412, "джерело", size=11, color=MUTED))
    p.append(text(xprot, 395, "стовбур", size=11, color=MUTED))
    p.append(text(xconv, 395, "ГІЛКИ", size=12, color=MUTED, bold=True))
    p.append(text(xconv, 412, "перетворювачі", size=11, color=MUTED))
    p.append(text(xload, 395, "ЛИСТЯ", size=12, color=MUTED, bold=True))
    p.append(text(xload, 412, "навантаження", size=11, color=MUTED))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p,
           title="Дерево живлення: від кореня-джерела до листя-навантажень")


# ── bottom-up: струм рахують від листя до кореня, втрати множаться вгору ───────
# Ідея: попит формують листя; угору по гілці кожен перетворювач додає свою
# неефективність, тож вхідний струм кореня більший за просту суму листя.
def fig_bottomup():
    W, H = 720, 360
    p = []

    # три рівні зліва направо: ЛИСТЯ → ПЕРЕТВОРЮВАЧ → КОРІНЬ
    # листя на 3.3 В
    leaves = [("MCU", "80 мА"), ("Давачі", "15 мА"), ("Flash", "5 мА")]
    ly = [70, 150, 230]
    for (nm, cur), yy in zip(leaves, ly):
        p.append(fitbox(60, yy - 24, 140, 48, nm + "\n" + cur + " @ 3.3 В",
                        size=12, fill="#fff7e6", stroke="#d6a400"))
        p.append(arrow(205, yy, 290, 150, color=INK, sw=1.8))

    # сумарне навантаження шини
    p.append(fitbox(295, 116, 150, 68,
                    "Σ навантаження\n100 мА @ 3.3 В\nP = 0.33 Вт",
                    size=12, fill="#eafaf0", stroke=FIELD, bold=False))

    # перетворювач BUCK
    p.append(arrow(450, 150, 505, 150, color=INK, sw=2))
    p.append(fitbox(508, 116, 130, 68, "BUCK\nη = 90 %\nдодає втрати",
                    size=12, fill=FILL, stroke=LINE))

    # корінь: вхідний струм більший
    p.append(arrow(640, 150, 690, 150, color=INK, sw=2))
    p.append(text(693, 150, "до", size=11, color=MUTED, anchor="start"))
    p.append(text(693, 166, "кореня", size=11, color=MUTED, anchor="start"))

    # обчислення внизу
    p.append(line(60, 290, 690, 290, color=MUTED, sw=1, dash="4,4"))
    calc = [
        "На виході buck:  P_out = 3.3 В × 0.100 А = 0.33 Вт",
        "На вході buck:   P_in = 0.33 / 0.90 = 0.367 Вт",
        "Струм від джерела (3.6 В): 0.367 / 3.6 = 0.102 А",
    ]
    yy = 312
    for ln in calc:
        p.append(text(70, yy, ln, size=13, color=INK, anchor="start"))
        yy += 20

    p.append(text(360, 50, "Попит росте знизу вгору; втрати множаться на кожному перетворювачі",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "bottom-up.svg"), W, H, *p,
           title="Рахунок дерева: від листя вгору до кореня")


# ── two-paths: та сама шина 3.3 В двома шляхами — дерево показує ціну ──────────
# Ідея: однакове листя, різні гілки. Дерево робить видимою різницю у вході й теплі.
def fig_twopaths():
    W, H = 860, 340
    p = []

    def chain(y, title, blocks, total):
        p.append(text(50, y - 46, title, size=13, color=INK, anchor="start", bold=True))
        x = 50
        for i, (lbl, fill, st) in enumerate(blocks):
            w = 132
            p.append(fitbox(x, y - 28, w, 56, lbl, size=12, fill=fill, stroke=st))
            x += w
            if i < len(blocks) - 1:
                p.append(arrow(x, y, x + 30, y, color=INK, sw=2))
                x += 30
        p.append(text(x + 16, y, total, size=13, color=POS, anchor="start", bold=True))

    # шлях A: buck одразу на 3.3 В
    chain(95, "А) один buck  3.6 В → 3.3 В",
          [("3.6 В\nджерело", "#eaf0fd", NEG),
           ("BUCK\nη = 92 %", "#eafaf0", FIELD),
           ("3.3 В\n100 мА", "#fff7e6", "#d6a400")],
          "вхід 0.100 А")

    # шлях B: buck 5 В, тоді LDO на 3.3 В
    chain(225, "Б) buck 5 В, тоді LDO 5 → 3.3 В",
          [("3.6 В\nджерело", "#eaf0fd", NEG),
           ("BOOST 5 В\nη = 90 %", "#eafaf0", FIELD),
           ("LDO 5→3.3\nη = 66 %", "#fdecea", POS),
           ("3.3 В\n100 мА", "#fff7e6", "#d6a400")],
          "вхід 0.168 А")

    p.append(line(50, 285, 810, 285, color=MUTED, sw=1, dash="4,4"))
    p.append(text(50, 308, "Те саме листя (3.3 В, 100 мА) — але шлях Б тягне від джерела на ~68 % більше струму:",
                  size=12, color=INK, anchor="start"))
    p.append(text(50, 328, "зайвий каскад і LDO, що гасить 5→3.3 у тепло. Дерево робить цю різницю видимою з першого погляду.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Дві гілки до однієї шини 3.3 В — різна ціна")


if __name__ == "__main__":
    fig_anatomy()
    fig_bottomup()
    fig_twopaths()
    print("ok")
