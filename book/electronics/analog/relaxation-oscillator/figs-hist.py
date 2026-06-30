# -*- coding: utf-8 -*-
# Фігури для вставки hist-relaxation-name.md (історія поняття).
# Власний генератор, щоб не чіпати figs.py теми. Вивід — у спільну ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Родовід самоколивних систем: від дуги до спільного рівняння ───────────
def fig_lineage():
    W, H = 760, 430
    frags = []

    axx0, axx1 = 70, 690          # вісь часу
    axy = 110
    frags.append(line(axx0, axy, axx1, axy, color=INK, sw=2))
    frags.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
                 % (axx1, axy, axx1 - 11, axy - 5, axx1 - 11, axy + 5, INK))
    frags.append(text(axx1, axy - 12, "час", size=12, color=INK, anchor="end"))

    # роки → x
    y0, y1 = 1900, 1926
    def X(year):
        return axx0 + (axx1 - 30 - axx0) * (year - y0) / (y1 - y0)

    # позначки-роки на осі
    for yr in (1900, 1906, 1917, 1919, 1926):
        x = X(yr)
        frags.append(line(x, axy - 5, x, axy + 5, color=INK, sw=1.6))
        frags.append(text(x, axy + 22, str(yr), size=12, color=MUTED))

    # події: (рік, верх/низ, заголовок, підпис, колір)
    ev = [
        (1900, "up", "Співоча дуга",       "Дадделл: дуга з\nвід'ємним опором",  NEG),
        (1906, "dn", "Тріод (Audion)",     "де Форест: третій\nелектрод-сітка",  POS),
        (1917, "up", "Мультивібратор",     "Абрагам і Блох:\nдва тріоди, меандр", NEG),
        (1919, "dn", "Спільне рівняння",   "Жане: три системи —\nодна математика", FIELD),
        (1926, "up", "Релаксаційні\nколивання", "ван дер Пол:\nназва й модель",   INK),
    ]
    for yr, side, head, sub, col in ev:
        x = X(yr)
        if side == "up":
            cy = axy - 78
            frags.append(line(x, axy, x, cy + 30, color=col, sw=1.4, dash="3,3"))
        else:
            cy = axy + 95
            frags.append(line(x, axy, x, cy - 30, color=col, sw=1.4, dash="3,3"))
        frags.append(circle(x, axy, 4.5, fill=col, stroke=col))
        b, bw, bh = textbox(x, cy, head + "\n" + sub, size=11.5, pad=8,
                            stroke=col, sw=1.8, color=INK)
        frags.append(b)

    # підсумкова стрічка-висновок унизу
    note = ("Одна нитка: усе це — системи, що самі коливаються пилкою, а не синусоїдою.\n"
            "ван дер Пол дав їм спільну назву й перше рівняння; назву «мультивібратор» лишили Абрагам і Блох.")
    b, bw, bh = textbox(W / 2, H - 48, note, size=12, pad=12,
                        stroke=MUTED, sw=1.6, color=INK, fill="#fafbfc")
    frags.append(b)

    render(os.path.join(IMG, "lineage.svg"), W, H, *frags,
           title="Родовід ідеї: від співочої дуги до релаксаційних коливань")


# ── 2. Чому «релаксація»: повільне напруження → різке розслаблення ───────────
def fig_relaxtime():
    W, H = 760, 320
    ox, oy = 80, H - 70
    aw, ah = 600, 200
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 24, "час", size=12, color=INK, anchor="end"))
    frags.append(mtext(ox - 8, oy - ah + 2, "напруга\nна C", size=11, color=INK, anchor="end"))

    yhi = oy - ah * 0.80
    ylo = oy - ah * 0.18

    # один цикл: повільний експо-підйом до порога, тоді миттєвий зрив
    pts = []
    N = 60
    xrise0, xrise1 = ox + 8, ox + aw * 0.62
    for k in range(N + 1):
        t = k / N
        frac = (1 - math.exp(-2.3 * t)) / (1 - math.exp(-2.3))
        x = xrise0 + (xrise1 - xrise0) * t
        y = ylo + (yhi - ylo) * frac
        pts.append((x, y))
    # миттєвий зрив униз
    pts.append((xrise1, ylo))
    # короткий другий підйом-натяк
    xr2 = ox + aw * 0.95
    for k in range(1, N + 1):
        t = k / N
        frac = (1 - math.exp(-2.3 * t)) / (1 - math.exp(-2.3))
        x = xrise1 + (xr2 - xrise1) * t
        y = ylo + (yhi - ylo) * frac * 0.55
        pts.append((x, y))
    pts_str = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (pts_str, INK))

    # поріг
    frags.append(line(ox, yhi, ox + aw, yhi, color=POS, sw=1.6, dash="6,5"))
    frags.append(text(ox + aw + 4, yhi + 4, "поріг", size=11, color=POS, anchor="start"))

    # фаза повільного «напруження»
    frags.append(text((xrise0 + xrise1) / 2, (yhi + ylo) / 2 - 6,
                      "повільне «напруження»", size=12, color=NEG))
    frags.append(text((xrise0 + xrise1) / 2, (yhi + ylo) / 2 + 12,
                      "≈ стала RC", size=11.5, color=NEG, italic=True))

    # миттєве «розслаблення» (relaxatio)
    frags.append(circle(xrise1, yhi, 5, fill=POS, stroke=POS))
    frags.append(arrow(xrise1 + 14, yhi + 6, xrise1 + 14, ylo - 6, color=POS, sw=2))
    frags.append(mtext(xrise1 + 22, (yhi + ylo) / 2, "різке\n«розслаблення»",
                       size=11.5, color=POS, anchor="start"))
    frags.append(text(xrise1 + 22, (yhi + ylo) / 2 + 32, "(relaxatio)",
                      size=11, color=POS, anchor="start", italic=True))

    render(os.path.join(IMG, "relaxtime.svg"), W, H, *frags,
           title="Звідки слово: повільне напруження — миттєвий спад напруги")


if __name__ == "__main__":
    fig_lineage()
    fig_relaxtime()
    print("ok: hist figures written to", IMG)
