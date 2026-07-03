# -*- coding: utf-8 -*-
# Фігури для вставки hist-failsafe-origin.md.
# Окремий генератор, щоб не чіпати авторський figs.py теми.
# Вивід — у той самий ./img/, імена з префіксом hist-.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_simple_vs_auto():
    """Проста vs автоматична магістраль: що робить розрив труби."""
    W, H = 780, 430
    p = []
    p.append(text(W/2, 28, "Розрив магістралі: два протилежні наслідки", size=17, bold=True))

    # ── ВЕРХ: проста (пряма) магістраль ───────────────────────────────
    yA = 70
    p.append(text(40, yA+6, "ПРОСТА магістраль", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(40, yA+24, "тиск у трубі САМ притискає колодки", size=11, color=MUTED, anchor="start"))

    # локомотив + три вагони, труба між ними
    tube_y = yA+70
    p.append(rect(40, tube_y-16, 90, 46, fill="#eef2ff", stroke=NEG))
    p.append(text(85, tube_y+11, "тиск", size=11, bold=True, color=NEG))
    xs = [175, 315, 455]
    for x in xs:
        p.append(rect(x, tube_y-16, 90, 46, fill=FILL, stroke=LINE))
        p.append(text(x+45, tube_y+11, "вагон", size=11))
    # труба
    p.append(line(130, tube_y+7, 175, tube_y+7, color=NEG, sw=4))
    p.append(line(265, tube_y+7, 315, tube_y+7, color=NEG, sw=4))
    # розрив після 2-го вагона
    xbreak = 405
    p.append(line(405, tube_y+7, 455, tube_y+7, color=NEG, sw=4))
    p.append(text(xbreak+27, tube_y-24, "✂ розрив", size=11, color=POS, bold=True))
    p.append(line(xbreak+15, tube_y-6, xbreak+39, tube_y+20, color=POS, sw=2))
    p.append(line(xbreak+39, tube_y-6, xbreak+15, tube_y+20, color=POS, sw=2))
    # наслідок
    p.append(fitbox(575, tube_y-26, 175, 66,
                    "тиск падає\n→ колодки ВІДПУСКАЮТЬ\n→ гальм НЕМА",
                    size=11, fill="#fdecea", stroke=POS))

    # ── НИЗ: автоматична магістраль ───────────────────────────────────
    yB = 250
    p.append(text(40, yB+6, "АВТОМАТИЧНА магістраль", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(40, yB+24, "магістраль лише ТРИМАЄ колодки відпущеними; тиск б'ється об резервуар вагона",
                  size=11, color=MUTED, anchor="start"))

    tube_y2 = yB+80
    p.append(rect(40, tube_y2-16, 90, 46, fill="#eef2ff", stroke=NEG))
    p.append(text(85, tube_y2+11, "тиск", size=11, bold=True, color=NEG))
    for x in xs:
        p.append(rect(x, tube_y2-16, 90, 46, fill=FILL, stroke=LINE))
        p.append(text(x+45, tube_y2+2, "вагон", size=10.5))
        # резервуар під вагоном
        p.append(text(x+45, tube_y2+22, "⟲ резерв", size=9.5, color=FIELD))
    p.append(line(130, tube_y2+7, 175, tube_y2+7, color=NEG, sw=4))
    p.append(line(265, tube_y2+7, 315, tube_y2+7, color=NEG, sw=4))
    p.append(line(405, tube_y2+7, 455, tube_y2+7, color=NEG, sw=4))
    p.append(text(xbreak+27, tube_y2-24, "✂ розрив", size=11, color=POS, bold=True))
    p.append(line(xbreak+15, tube_y2-6, xbreak+39, tube_y2+20, color=POS, sw=2))
    p.append(line(xbreak+39, tube_y2-6, xbreak+15, tube_y2+20, color=POS, sw=2))
    p.append(fitbox(575, tube_y2-26, 175, 66,
                    "тиск падає\n→ резервуар ПРИТИСКАЄ\n→ гальма СПРАЦЮВАЛИ",
                    size=11, fill="#eafaf0", stroke=FIELD))

    p.append(text(W/2, H-14,
                  "Та сама відмова, протилежний стан: питання лише в тому, ЩО тримає силу.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'hist-simple-vs-auto.svg'), W, H, *p)


def fig_semaphore():
    """Семафор: цілий трос — «вільно»; обрив — гравітація в «стій»."""
    W, H = 700, 380
    p = []
    p.append(text(W/2, 28, "Семафор: обрив троса САМ ставить «стій»", size=17, bold=True))

    def post(cx, base_y, arm_deg, col, cap):
        f = []
        top = base_y-150
        # стовп
        f.append(line(cx, base_y, cx, top, color=INK, sw=4))
        # крило під кутом (0° — горизонт «стій»; підняте вгору — «вільно»)
        import math
        L = 78
        a = math.radians(arm_deg)
        x2 = cx + L*math.cos(a)
        y2 = top - L*math.sin(a)
        f.append(line(cx, top, x2, y2, color=col, sw=8))
        f.append(circle(cx, top, 5, fill=INK, stroke=INK))
        f.append(text(cx, base_y+22, cap, size=12, bold=True, color=col))
        return f

    # зліва: трос цілий, крило підняте — «вільно»
    p += post(190, 250, 35, FIELD, "трос цілий → вільно")
    # трос (натягнутий)
    p.append(line(190, 205, 150, 250, color=NEG, sw=2))
    p.append(text(120, 250, "трос", size=10, color=NEG, anchor="end"))

    # справа: трос обірвано, крило впало в горизонт — «стій»
    p += post(500, 250, 0, POS, "трос обірвано → СТІЙ")
    # обірваний трос
    p.append(line(500, 100, 470, 130, color=MUTED, sw=2, dash="4 4"))
    p.append(text(455, 118, "✂", size=15, color=POS))
    # противага (spectacle) — важча за крило, тягне в «стій»
    p.append(circle(500, 108, 9, fill="#fdf6e3", stroke="#b8860b", sw=2))
    p.append(text(500, 112, "⬤", size=10, color="#b8860b"))
    p.append(text(560, 160, "противага\nтягне вниз", size=10, color="#b8860b", anchor="start"))

    p.append(fitbox(190-90, 285, 180, 40,
                    "силу тримає рука\nсигналіста", size=10.5, fill="#eafaf0", stroke=FIELD))
    p.append(fitbox(500-90, 285, 180, 40,
                    "відмова падає\nу безпечний бік", size=10.5, fill="#fdecea", stroke=POS))

    p.append(text(W/2, H-16,
                  "Верхнє крило: за відмови гравітація сама ставить найобмежніший, найбезпечніший знак.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'hist-semaphore.svg'), W, H, *p)


def fig_lineage():
    """Родовід ідеї: від гальм/семафора XIX ст. до приймача й дрона."""
    W, H = 780, 300
    p = []
    p.append(text(W/2, 28, "Родовід однієї ідеї: відмова → безпечний стан", size=17, bold=True))

    nodes = [
        (40,  "1870-ті\nконтинуальні\nгальма", NEG, "#eef2ff"),
        (215, "1889\nАрма, закон:\nсамозастосовні", POS, "#fdecea"),
        (390, "семафор:\nобрив → «стій»", "#b8860b", "#fdf6e3"),
        (565, "1945–46\nслово\n«fail-safe»", MUTED, "#f0f0f0"),
    ]
    y = 90
    bw, bh = 150, 84
    for x, label, col, fill in nodes:
        p.append(fitbox(x, y, bw, bh, label, size=11.5, bold=True, fill=fill, stroke=col))
    # стрілки між ними
    for x in (40, 215, 390):
        p.append(arrow(x+bw, y+bh/2, x+175, y+bh/2))

    # спуск до сучасного
    p.append(arrow(640, y+bh, 640, y+bh+34))
    p.append(fitbox(300, y+bh+40, 340, 60,
                    "приймач RC та польотний контролер дрона:\nсигнал зник → газ у нуль / RTL / посадка —\nта сама логіка «відмова веде в безпечний бік»",
                    size=11, fill="#eafaf0", stroke=FIELD))

    p.append(text(W/2, H-12,
                  "Принцип старший за слово: інженерія 1870-х уже будувала його в залізі.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'hist-lineage.svg'), W, H, *p)


if __name__ == '__main__':
    fig_simple_vs_auto()
    fig_semaphore()
    fig_lineage()
    print("hist figures written to", IMG)
