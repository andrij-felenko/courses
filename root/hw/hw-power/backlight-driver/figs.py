# -*- coding: utf-8 -*-
"""Фігури до теми «Драйвер підсвітки».
  backlight-driver.md →  driver.svg     (силова частина + петля ЗЗ по струму)
                         feedback.svg   (контур стабілізації струму на FB)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви схем ─────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 6, color=INK, sw=1.8),
           line(cx - 13, y + 6, cx + 13, y + 6, color=INK, sw=2.4),
           line(cx - 8, y + 11, cx + 8, y + 11, color=INK, sw=2.0),
           line(cx - 3, y + 16, cx + 3, y + 16, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=10, color=MUTED, bold=False))
    return "".join(out)


def inductor(x1, y, x2, n=4):
    """Горизонтальна котушка від x1 до x2 на висоті y (зиґзаґ)."""
    out, span = [], (x2 - x1)
    step = span / (2 * n)
    px = x1
    up = True
    for i in range(2 * n):
        nx = x1 + step * (i + 1)
        ny = y - 9 if up else y + 9
        if i == 2 * n - 1:
            ny = y
        out.append(line(px, y if i == 0 else (y - 9 if not up else y + 9), nx, ny if i < 2 * n - 1 else y, color=INK, sw=1.8))
        px = nx
        up = not up
    # простіше й надійніше — пилка
    out = []
    pts = [(x1, y)]
    for i in range(2 * n):
        nx = x1 + step * (i + 1)
        ny = y - 8 if i % 2 == 0 else y + 8
        pts.append((nx, ny))
    pts.append((x2, y))
    for i in range(len(pts) - 1):
        out.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=INK, sw=1.8))
    return "".join(out)


def diode_r(x1, y, size=11, color=INK):
    """Діод вправо (трикутник + риска) від точки (x1,y); повертає (svg, x_out)."""
    s = size
    out = [
        line(x1, y, x1 + 4, y, color=color, sw=2),
        '<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="none" stroke="%s" stroke-width="1.8"/>'
        % (x1 + 4, y - s * 0.6, x1 + 4, y + s * 0.6, x1 + 4 + s, y, color),
        line(x1 + 4 + s, y - s * 0.6, x1 + 4 + s, y + s * 0.6, color=color, sw=2.2),
        line(x1 + 4 + s, y, x1 + 8 + s, y, color=color, sw=2),
    ]
    return "".join(out), x1 + 8 + s


def led_down(cx, y1, y2, color=INK):
    """Світлодіод-стрілка вниз між y1 і y2 (трикутник вниз + дві стрілки світла)."""
    s = 11
    midtop = y1 + 8
    out = [
        line(cx, y1, cx, midtop, color=color, sw=2),
        '<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="none" stroke="%s" stroke-width="1.8"/>'
        % (cx - s * 0.6, midtop, cx + s * 0.6, midtop, cx, midtop + s, color),
        line(cx - s * 0.6, midtop + s, cx + s * 0.6, midtop + s, color=color, sw=2.2),
        line(cx, midtop + s, cx, y2, color=color, sw=2),
        # дві стрілочки світла
        line(cx + 7, midtop - 1, cx + 14, midtop - 6, color=FIELD, sw=1.3),
        line(cx + 8, midtop + 4, cx + 15, midtop - 1, color=FIELD, sw=1.3),
    ]
    return "".join(out)


def cap_v(cx, y1, y2):
    """Вертикальний конденсатор (дві пластини) між y1 і y2."""
    mid = (y1 + y2) / 2
    return "".join([
        line(cx, y1, cx, mid - 4, color=INK, sw=2),
        line(cx - 11, mid - 4, cx + 11, mid - 4, color=INK, sw=2.2),
        line(cx - 11, mid + 4, cx + 11, mid + 4, color=INK, sw=2.2),
        line(cx, mid + 4, cx, y2, color=INK, sw=2),
    ])


# ── Фігура 1: силова частина + ЗЗ по струму ─────────────────────────────────
def fig_driver():
    W, H = 720, 430
    f = []

    # рамка чипа
    cx0, cy0, cw, ch = 250, 150, 150, 130
    f.append(rect(cx0, cy0, cw, ch, fill="#eef2f5", stroke=INK, sw=1.8))
    f.append(text(cx0 + cw / 2, cy0 + 34, "boost-драйвер", size=13, color=INK, bold=True))
    f.append(text(cx0 + cw / 2, cy0 + 54, "(клас LED driver)", size=10, color=MUTED))
    f.append(text(cx0 + cw / 2, cy0 + 86, "силовий ключ", size=9.5, color=MUTED))
    f.append(text(cx0 + cw / 2, cy0 + 102, "+ підсилювач помилки", size=9.5, color=MUTED))

    ytop = 175  # силова шина зверху
    # Vin → котушка → вузол SW (вхід чипа зверху-зліва)
    f.append(text(40, ytop + 4, "Vᵢₙ", size=12, color=INK, bold=True, anchor="end"))
    f.append(line(46, ytop, 78, ytop, color=INK, sw=2))
    f.append(inductor(78, ytop, 150, n=4))
    f.append(text(114, ytop - 16, "L", size=11, color=INK))
    f.append(line(150, ytop, cx0, ytop, color=INK, sw=2))
    f.append(text(cx0 - 5, ytop - 7, "SW", size=9, color=MUTED, anchor="end"))

    # EN / dimming до чипа зліва-знизу
    yen = 245
    f.append(line(150, yen, cx0, yen, color=INK, sw=2))
    f.append(text(cx0 - 5, yen - 4, "EN/CTRL", size=9, color=MUTED, anchor="end"))
    f.append(text(108, yen - 18, "димінг (ШІМ)", size=9, color=FIELD))
    # маленький ШІМ-символ
    bx = 92
    f.append("".join([
        line(bx, yen + 6, bx + 8, yen + 6, color=FIELD, sw=1.5),
        line(bx + 8, yen + 6, bx + 8, yen - 4, color=FIELD, sw=1.5),
        line(bx + 8, yen - 4, bx + 18, yen - 4, color=FIELD, sw=1.5),
        line(bx + 18, yen - 4, bx + 18, yen + 6, color=FIELD, sw=1.5),
        line(bx + 18, yen + 6, bx + 28, yen + 6, color=FIELD, sw=1.5),
    ]))

    # вихід чипа справа-зверху → діод → Cout → нитка → Rs → земля
    xout = cx0 + cw
    f.append(line(xout, ytop, xout + 18, ytop, color=INK, sw=2))
    dsvg, xd = diode_r(xout + 18, ytop)
    f.append(dsvg)
    f.append(line(xd, ytop, 560, ytop, color=INK, sw=2))
    f.append(text(xout + 24, ytop - 8, "Vout (скільки треба)", size=9, color=MUTED, anchor="start"))

    # Cout у вузлі виходу
    xc = 500
    f.append(cap_v(xc, ytop, 330))
    f.append(gnd(xc, 330))
    f.append(text(xc + 9, 305, "Cout", size=9, color=MUTED, anchor="start"))

    # нитка світлодіодів від 560 вниз
    xled = 560
    y = ytop
    for i in range(4):
        f.append(led_down(xled, y, y + 30))
        y += 30
    f.append(text(xled + 22, ytop + 60, "нитка", size=9, color=MUTED, anchor="start"))
    f.append(text(xled + 22, ytop + 74, "(послідовно)", size=9, color=MUTED, anchor="start"))

    # Rs знизу нитки
    yrs1 = y
    f.append(line(xled, yrs1, xled, yrs1 + 8, color=INK, sw=2))
    f.append(rect(xled - 20, yrs1 + 8, 40, 18, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(xled, yrs1 + 21, "Rₛ", size=11, color=INK, bold=True))
    f.append(line(xled, yrs1 + 26, xled, yrs1 + 38, color=INK, sw=2))
    f.append(gnd(xled, yrs1 + 38))

    # FB: від верху Rs назад у чип (сіра лінія зворотного звʼязку)
    yfb = yrs1 + 8
    f.append(line(xled, yfb, 630, yfb, color=MUTED, sw=1.5))
    f.append(line(630, yfb, 630, 242, color=MUTED, sw=1.5))
    f.append(line(630, 242, xout, 242, color=MUTED, sw=1.5))
    f.append(text(xout + 5, 238, "FB", size=9, color=MUTED, anchor="start"))
    f.append(text(636, yfb - 6, "струм «читає» Rₛ", size=9, color=MUTED, anchor="start"))

    # формула-плашка
    bx2, by2 = 70, 360
    f.append(rect(bx2, by2, 250, 34, fill="#e7f5ea", stroke=FIELD, sw=1.4))
    f.append(text(bx2 + 125, by2 + 22, "I_LED = V_FB(ref) ÷ Rₛ", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "driver.svg"), W, H, *f,
           title="Boost-драйвер: задаєш Rₛ — чип сам тримає струм")


# ── Фігура 2: контур стабілізації струму (як петля ловить точку) ────────────
def fig_feedback():
    W, H = 720, 300
    f = []

    # центральна вісь: ланцюг причинності по колу
    nodes = [
        (130, 90, "струм нитки\nвпав"),
        (360, 70, "спадання на Rₛ\n< V_ref"),
        (590, 90, "підсилювач:\n«на FB замало»"),
        (590, 210, "ключ качає\nактивніше"),
        (360, 230, "Vout ↑ →\nструм ↑"),
        (130, 210, "спадання на Rₛ\nповертається\nдо V_ref"),
    ]
    boxes = []
    for (x, y, s) in nodes:
        body, w, h = textbox(x, y, s, size=11, pad=9, fill=FILL, stroke=INK, sw=1.5)
        boxes.append((x, y, w, h))
        f.append(body)

    # стрілки по колу
    def edge(a, b):
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        return arrow(ax + (bx - ax) * 0.30, ay + (by - ay) * 0.30,
                     bx - (bx - ax) * 0.30, by - (by - ay) * 0.30, color=POS, sw=1.8)
    for i in range(len(nodes)):
        f.append(edge(i, (i + 1) % len(nodes)))

    # центральна позначка стійкої точки
    body, w, h = textbox(360, 150, "стійка точка:\nU на Rₛ = V_ref\n(≈0.2 В)", size=11,
                         pad=10, fill="#e7f5ea", stroke=FIELD, sw=1.6, bold=True)
    f.append(body)

    render(os.path.join(IMG, "feedback.svg"), W, H, *f,
           title="Петля зворотного звʼязку заганяє струм у єдину точку")


if __name__ == "__main__":
    fig_driver()
    fig_feedback()
    print("figs: driver.svg, feedback.svg -> ./img/")
