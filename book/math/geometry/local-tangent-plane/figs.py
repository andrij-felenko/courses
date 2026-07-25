# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def tangent_plane():
    """Дотична площина торкається кулі Землі; зазор між дугою й прямою росте."""
    import math
    W, H = 720, 420
    frags = []
    frags.append(text(W / 2, 26, "Дотична площина: куля крива, аркуш плаский", size=16, bold=True))

    # Центр кулі внизу за кадром; точка дотику — угорі по центру.
    cx, cy = W / 2, 1550        # центр кулі (глибоко внизу)
    R = 1300                    # радіус у px
    tx, ty = cx, cy - R         # точка дотику (origin) — угорі
    # дуга кулі: параметр — кут від вертикалі, малюємо симетрично навколо дотику
    def on_circle(ang_deg):
        a = math.radians(ang_deg)
        return (cx + R * math.sin(a), cy - R * math.cos(a))
    span = 15                   # градусів у кожен бік
    pts = []
    ad = -span
    while ad <= span + 0.01:
        pts.append(on_circle(ad))
        ad += 1.0
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, NEG))
    # дотична площина — горизонтальний відрізок через точку дотику
    half = R * math.sin(math.radians(span))
    frags.append(line(tx - half, ty, tx + half, ty, color=FIELD, sw=2.6))
    # точка дотику (origin)
    frags.append(circle(tx, ty, 5, fill=INK, stroke=INK))
    frags.append(text(tx, ty - 14, "точка-початок (origin)", size=12, bold=True, color=INK))
    frags.append(text(tx - half + 90, ty - 10, "дотична площина", size=12, color=FIELD, italic=True))
    frags.append(text(tx + half - 60, ty + 150, "куля Землі", size=12, color=NEG, italic=True))

    # зазор близько (майже нема) і далеко (помітний): вертикальна мірка площина→куля,
    # а підпис виносимо ПІД дугу, у чисте поле, з пунктиром-виноскою — щоб жодна
    # лінія не різала напис (напис стоїть поза всіма лініями).
    for ad, lab, ly in ((3, "близько:\nзазор мізерний", 330),
                        (11, "далеко:\nзазор росте", 355)):
        px, py = on_circle(ad)          # точка на кулі
        frags.append(line(px, ty, px, py, color=POS, sw=1.8, dash="4,3"))       # мірка зазору
        frags.append(circle(px, py, 3.5, fill=NEG, stroke=NEG))
        frags.append(line(px, py, px, ly - 10, color=POS, sw=1.2, dash="2,3"))  # виноска до підпису
        frags.append(mtext(px, ly, lab.split("\n"), size=11, color=POS, anchor="middle"))
    render(os.path.join(IMG, "tangent-plane.svg"), W, H, *frags)


def parallel_cos():
    """Осьовий переріз: R до точки на широті φ, її горизонтальна проєкція R·cos φ."""
    import math
    W, H = 660, 400
    frags = []
    frags.append(text(W / 2, 26, "Чому в довготі з'являється cos φ", size=16, bold=True))

    cx, cy = 120, H - 60        # центр Землі — лівий низ
    R = 250                     # радіус у px (уся чверть-дуга лишається на полотні)
    phi = 42                    # широта для картинки
    a = math.radians(phi)
    px = cx + R * math.cos(a)   # точка на поверхні (широта φ), у площині перерізу
    py = cy - R * math.sin(a)

    # чверть-дуга Землі (від екватора до полюса)
    pts = []
    d = 0
    while d <= 90:
        aa = math.radians(d)
        pts.append((cx + R * math.cos(aa), cy - R * math.sin(aa)))
        d += 2
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
                 (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    # вісь обертання (полярна) і екваторіальна
    frags.append(line(cx, cy, cx, cy - R - 16, color=MUTED, sw=1.4, dash="5,4"))
    frags.append(line(cx, cy, cx + R + 24, cy, color=MUTED, sw=1.4, dash="5,4"))
    frags.append(text(cx + 6, cy - R - 20, "вісь обертання", size=11, color=MUTED, anchor="start"))
    frags.append(text(cx + R + 28, cy + 4, "екватор", size=11, color=MUTED, anchor="start"))

    # земний радіус R до точки
    frags.append(line(cx, cy, px, py, color=INK, sw=2.2))
    frags.append(text((cx + px) / 2 - 10, (cy + py) / 2 - 6, "R", size=15, bold=True, color=INK))
    frags.append(circle(px, py, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(px + 12, py - 4, "точка на широті φ", size=12, color=FIELD,
                     anchor="start", bold=True))

    # горизонтальна проєкція = радіус паралелі R·cos φ
    frags.append(line(cx, py, px, py, color=POS, sw=2.6))
    frags.append(circle(cx, py, 4, fill=POS, stroke=POS))
    frags.append(text((cx + px) / 2, py - 10, "R·cos φ", size=14, bold=True, color=POS))
    frags.append(text((cx + px) / 2, py + 18, "радіус паралелі", size=11, color=POS, italic=True))
    # пунктир від точки вниз на проєкцію (показати, що це та сама горизонталь)
    frags.append(line(px, py, px, cy, color=MUTED, sw=1.0, dash="3,3"))

    # кут φ біля центра
    frags.append(text(cx + 34, cy - 12, "φ", size=15, bold=True, color=INK))

    # підпис-висновок праворуч угорі
    box = fitbox(W - 250, 70, 236, 128,
                 "\n".join([
                     "Рух на схід іде по паралелі —",
                     "колу радіусом R·cos φ, меншому",
                     "за екватор. Тому градус довготи",
                     "коротшає до полюсів як cos φ:",
                     "на екваторі — повний, на",
                     "полюсі — нуль.",
                 ]),
                 size=12, fill="#f7fbf8", stroke=FIELD, sw=1.6)
    frags.append(box)
    render(os.path.join(IMG, "parallel-cos.svg"), W, H, *frags)


if __name__ == "__main__":
    tangent_plane()
    parallel_cos()
    print("ok")
