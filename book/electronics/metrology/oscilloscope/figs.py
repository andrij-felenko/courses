# -*- coding: utf-8 -*-
"""Фігури, ДОДАНІ до детальної статті «Осцилограф» (oscilloscope-d.md).

Решта SVG у ./img/ (number-vs-shape, screen, read, trigger, reveals, crt*, panel,
coupling, divider тощо) зроблені раніше стороннім інструментом і НЕ чіпаються.
Цей файл генерує лише дві нові фігури, яких бракувало для повного (детального) викладу:

  1) dso-architecture.svg — тракт цифрового осцилографа: щуп → атенюатор/підсилювач →
                            АЦП → пам'ять → екран, і тригер, що заморожує кадр;
  2) aliasing.svg         — замала частота відліків підмінює швидку хвилю повільною.

Запуск:  python figs.py   → пише два SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD    = "#caa24a"
GREEN_F = "#eef6ef"
BLUE_F  = "#e9eefb"
GOLD_F  = "#fff6e0"


def polyline(pts, color=INK, sw=2.0, dash=None):
    """Сирий <polyline> (svgkit не має хелпера): pts — список (x, y)."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


# ── 1. Тракт цифрового осцилографа ──────────────────────────────────────────
def fig_dso():
    W, H = 980, 380
    f = [text(W / 2, 30, "Тракт цифрового осцилографа: від щупа до екрана", size=17, bold=True),
         text(W / 2, 52,
              "оцифрувати напругу, скласти відліки в пам'ять, намалювати; тригер вирішує, коли заморозити кадр",
              size=10, color=MUTED, italic=True)]

    # п'ять блоків головного тракту
    blocks = [
        (24,  "Щуп\n(вхід)",             FILL,    LINE),
        (218, "Атенюатор\n+ підсилювач", FILL,    LINE),
        (412, "АЦП\n(відліки)",          GREEN_F, FIELD),
        (606, "Пам'ять\nвідліків",       BLUE_F,  NEG),
        (800, "Екран\n(РК)",             FILL,    LINE),
    ]
    by, bh, bw = 140, 76, 156
    for x, label, fill, stroke in blocks:
        f.append(fitbox(x, by, bw, bh, label, size=13, bold=True, fill=fill, stroke=stroke, sw=2))

    ay = by + bh / 2                      # рівень стрілок між блоками
    for x, *_ in blocks[:-1]:
        f.append(arrow(x + bw, ay, x + bw + 38, ay, color=INK, sw=2))

    f.append(text(W / 2, 120, "потік чисел (відліки) →", size=10, color=MUTED))

    # ── тригер знизу ──
    tx, tw2, ty2, th2 = 390, 300, 286, 58
    f.append(fitbox(tx, ty2, tw2, th2, "Тригер:\nколи заморозити кадр", size=13, bold=True,
                    fill=GOLD_F, stroke=GOLD, sw=2))

    xadc = 412 + bw / 2                    # 490 — вихід АЦП
    f.append(line(xadc, by + bh, xadc, ty2, color=INK, sw=1.6, dash="5 4"))
    f.append(text(xadc + 12, (by + bh + ty2) / 2 + 4, "стежить за потоком",
                  size=10, color=MUTED, anchor="start"))

    xmem = 606 + bw / 2                    # 684 — пам'ять
    f.append(arrow(tx + tw2, ty2 + th2 / 2, xmem, by + bh + 4, color=POS, sw=2))
    f.append(text(724, 300, "заморозити", size=10, color=POS, anchor="start"))

    return render(os.path.join(IMG, "dso-architecture.svg"), W, H, *f)


# ── 2. Аліасинг: рідкі відліки дають хибну повільну хвилю ────────────────────
def fig_aliasing():
    W, H = 960, 430
    mid, amp = 235, 90
    X0, X1 = 90, 900
    span = X1 - X0

    f = [text(W / 2, 30, "Аліасинг: замала частота відліків підмінює швидку хвилю повільною",
              size=16, bold=True),
         text(W / 2, 52,
              "між знімками осцилограф сліпий; якщо сигнал устигає обернутися в паузі, точки лягають на іншу, повільну хвилю",
              size=10, color=MUTED, italic=True)]

    n = 400
    # справжня швидка хвиля (9 періодів) — світла тонка
    true_pts = [(X0 + span * i / n, mid - amp * math.sin(2 * math.pi * 9 * i / n)) for i in range(n + 1)]
    f.append(polyline(true_pts, color=MUTED, sw=1.6))
    # хибна повільна хвиля (1 період) — червона товста
    alias_pts = [(X0 + span * i / n, mid - amp * math.sin(2 * math.pi * 1 * i / n)) for i in range(n + 1)]
    f.append(polyline(alias_pts, color=POS, sw=3.0))

    # відліки: 10 точок; лежать ТОЧНО і на швидкій, і на повільній хвилі
    m = 10
    xs = []
    for i in range(m):
        t = (i + 0.5) / m
        x = X0 + span * t
        y = mid - amp * math.sin(2 * math.pi * 9 * t)     # тотожно повільній (аліас)
        f.append(circle(x, y, 5, fill=NEG, stroke=BG, sw=1.5))
        xs.append(x)

    # нижня вісь часу з рівними позначками відліків
    axy = 372
    f.append(line(X0, axy, X1 + 8, axy, color=INK, sw=1.6))
    for x in xs:
        f.append(line(x, axy, x, axy + 7, color=INK, sw=1.4))

    # підписи — у чистих зонах, поза лініями
    f.append(text(250, 92, "справжній сигнал — швидкий", size=12, color=MUTED, bold=True))
    f.append(text(700, 120, "хвиля, яку показує осцилограф —", size=12, color=POS, bold=True))
    f.append(text(700, 138, "повільна й хибна", size=12, color=POS, bold=True))
    f.append(text(W / 2, 402, "відліки беруться через рівні проміжки — але надто рідко",
                  size=11, bold=True))

    return render(os.path.join(IMG, "aliasing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dso()
    fig_aliasing()
    print("OK:", IMG)
