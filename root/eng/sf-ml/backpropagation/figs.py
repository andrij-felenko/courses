# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_node():
    """Один вузол: local × upstream = downstream. Серце ланцюгового правила."""
    W, H = 720, 340
    parts = []
    cx, cy = 360, 165
    r = 46
    # вузол
    parts.append(circle(cx, cy, r, fill="#eef6ff", stroke=NEG, sw=2.5))
    parts.append(text(cx, cy - 4, "операція", size=14, bold=True))
    parts.append(text(cx, cy + 16, "y = f(x)", size=13, color=MUTED))

    # forward: вхід зліва, вихід справа (сірі, тонкі)
    parts.append(arrow(120, cy - 40, cx - r, cy - 40, color=MUTED, sw=1.6))
    parts.append(text(150, cy - 50, "вперед:  x  →", size=13, color=MUTED, anchor="start"))
    parts.append(arrow(cx + r, cy - 40, 600, cy - 40, color=MUTED, sw=1.6))
    parts.append(text(590, cy - 50, "→  y", size=13, color=MUTED, anchor="end"))

    # backward: справа приходить upstream, зліва йде downstream (червоні, товсті)
    parts.append(arrow(600, cy + 46, cx + r, cy + 46, color=POS, sw=2.4))
    b1, _, _ = textbox(560, cy + 78, "прийшов згори\n∂E/∂y", size=13, color=POS,
                       stroke=POS, fill="#fdecea")
    parts.append(b1)

    parts.append(arrow(cx - r, cy + 46, 120, cy + 46, color=POS, sw=2.4))
    b2, _, _ = textbox(170, cy + 78, "пішов униз\n∂E/∂x", size=13, color=POS,
                       stroke=POS, fill="#fdecea")
    parts.append(b2)

    # локальний множник — над вузлом
    b3, _, _ = textbox(cx, cy - 92, "локальна чутливість\n∂y/∂x", size=13, bold=True,
                       stroke=FIELD, fill="#eafaf1", color=FIELD)
    parts.append(b3)
    parts.append(line(cx, cy - 66, cx, cy - r, color=FIELD, sw=1.4, dash="4 3"))

    # формула-підсумок унизу
    f, _, _ = textbox(cx, H - 34, "∂E/∂x  =  ∂E/∂y · ∂y/∂x     (те, що прийшло) × (локальна чутливість)",
                      size=13, bold=True, stroke=INK, fill=FILL)
    parts.append(f)

    render(os.path.join(IMG, 'chain-node.svg'), W, H, *parts,
           title="Один вузол: помножити те, що прийшло згори, на власну чутливість")


def fig_sweep():
    """Два проходи крізь шари: вперед рахує й запамʼятовує, назад несе дельти."""
    W, H = 760, 380
    parts = []
    ys = 150
    xs = [110, 300, 490, 640]
    labels = ["вхід", "шар 1", "шар 2", "похибка E"]
    r = 34
    for i, (x, lab) in enumerate(zip(xs, labels)):
        last = (i == len(xs) - 1)
        fill = "#fdecea" if last else "#eef6ff"
        stroke = POS if last else NEG
        parts.append(circle(x, ys, r, fill=fill, stroke=stroke, sw=2.2))
        parts.append(text(x, ys + 4, lab, size=13, bold=last))

    # forward стрілки (сірі, зверху)
    for i in range(len(xs) - 1):
        parts.append(arrow(xs[i] + r, ys - 8, xs[i + 1] - r, ys - 8, color=MUTED, sw=1.7))
    parts.append(text(xs[0], ys - 58, "ВПЕРЕД:  рахуємо значення й ЗАПАМʼЯТОВУЄМО їх",
                      size=14, bold=True, color=MUTED, anchor="start"))

    # backward стрілки (червоні, знизу)
    for i in range(len(xs) - 1, 0, -1):
        parts.append(arrow(xs[i] - r, ys + 8, xs[i - 1] + r, ys + 8, color=POS, sw=2.4))
    parts.append(text(xs[-1] + 8, ys + 66, "НАЗАД:  несемо дельту, множимо на запамʼятоване",
                      size=14, bold=True, color=POS, anchor="end"))

    # дельти під кожним шаром — кожна будується з наступної (reuse)
    dys = ys + 118
    d2, _, _ = textbox(xs[2], dys, "δ₂", size=15, bold=True, stroke=POS, fill="#fdecea", color=POS)
    d1, _, _ = textbox(xs[1], dys, "δ₁", size=15, bold=True, stroke=POS, fill="#fdecea", color=POS)
    parts.append(d2)
    parts.append(d1)
    parts.append(arrow(xs[2] - 24, dys, xs[1] + 24, dys, color=POS, sw=2.0))
    parts.append(text((xs[1] + xs[2]) / 2, dys - 22,
                      "δ₁ будуємо з δ₂ — не рахуємо заново", size=12, color=INK))

    note, _, _ = textbox(W / 2, H - 30,
                         "Один прохід уперед + один назад дають градієнт для ВСІХ ваг одразу",
                         size=13, bold=True, stroke=INK, fill=FILL)
    parts.append(note)

    render(os.path.join(IMG, 'two-passes.svg'), W, H, *parts,
           title="Два проходи: вперед запамʼятати, назад — пронести похибку")


def fig_timeline():
    """Багаторазове відкриття: три незалежні появи ідеї крізь «зиму ШІ»."""
    W, H = 760, 430
    parts = []
    x0, x1 = 90, 690
    axis_y = 250

    # роки-опори на осі: 1960 .. 1990
    yr_min, yr_max = 1958, 1990

    def X(year):
        return x0 + (x1 - x0) * (year - yr_min) / (yr_max - yr_min)

    # смуга «зими ШІ» (після Perceptrons 1969 до сер. 1980-х) — сірий фон
    wz0, wz1 = X(1969), X(1986)
    parts.append(rect(wz0, axis_y - 118, wz1 - wz0, 236, fill="#f0f1f3",
                      stroke="#d7d9dd", sw=1.2, rx=8))
    parts.append(text((wz0 + wz1) / 2, axis_y - 100, "«зима ШІ» — інтерес і гроші до мереж падають",
                      size=12, color=MUTED, italic=True))

    # вісь часу
    parts.append(arrow(x0 - 10, axis_y, x1 + 20, axis_y, color=INK, sw=2.0))
    for yr in (1960, 1970, 1980, 1990):
        parts.append(line(X(yr), axis_y - 5, X(yr), axis_y + 5, color=INK, sw=1.5))
        parts.append(text(X(yr), axis_y + 22, str(yr), size=12, color=MUTED))

    # три події: (рік, підпис-хто, підпис-що, вгору чи вниз)
    def event(year, who, what, up, hot=False):
        xx = X(year)
        stroke = POS if hot else NEG
        parts.append(circle(xx, axis_y, 7, fill="#fdecea" if hot else "#eef6ff",
                            stroke=stroke, sw=2.4))
        if up:
            parts.append(line(xx, axis_y - 7, xx, axis_y - 44, color=stroke, sw=1.6, dash="4 3"))
            b, _, _ = textbox(xx, axis_y - 66, who + "\n" + what, size=12, bold=True,
                              stroke=stroke, fill="#fdecea" if hot else "#eef6ff",
                              color=INK)
        else:
            parts.append(line(xx, axis_y + 7, xx, axis_y + 44, color=stroke, sw=1.6, dash="4 3"))
            b, _, _ = textbox(xx, axis_y + 66, who + "\n" + what, size=12, bold=True,
                              stroke=stroke, fill="#fdecea" if hot else "#eef6ff",
                              color=INK)
        parts.append(b)

    event(1970, "Ліннайнмаа", "зворотний режим,\nне для мереж", up=True)
    event(1974, "Вербос", "застосував до\nнавчання мереж", up=False)
    event(1986, "Румельгарт·Гінтон·Вільямс", "Nature: метод\nстає гучним", up=True, hot=True)

    # підпис-висновок унизу
    note, _, _ = textbox(W / 2, H - 26,
                         "Та сама ідея зринала тричі за 16 років — і щоразу тонула, доки не влучила в свій час",
                         size=13, bold=True, stroke=INK, fill=FILL)
    parts.append(note)

    render(os.path.join(IMG, 'rediscovery-timeline.svg'), W, H, *parts,
           title="Багаторазове незалежне відкриття зворотного поширення")


if __name__ == '__main__':
    fig_node()
    fig_sweep()
    fig_timeline()
    print("figs done")
