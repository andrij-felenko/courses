# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def ladder():
    """Три сходинки автономності: ручний → висота → позиція."""
    W, H = 720, 360
    steps = [
        ("Ручний режим", "пілот тримає кут",
         ["апарат вирівнює нахил", "усе інше — на пілоті",
          "потрібні лише гіроскопи"], MUTED),
        ("Утримання висоти", "апарат тримає H",
         ["додається барометр", "вертикаль — на автопілоті",
          "по горизонту досі керує пілот"], NEG),
        ("Режими з позицією", "апарат тримає точку",
         ["потрібна оцінка положення", "горизонт — на автопілоті",
          "апарат сам повертається на місце"], FIELD),
    ]
    frags = []
    n = len(steps)
    gap = 18
    bw = (W - 2 * 24 - (n - 1) * gap) / n
    base_y = H - 40
    for i, (title, sub, rows, col) in enumerate(steps):
        x = 24 + i * (bw + gap)
        bh = 150 + i * 56           # кожна сходинка вища
        y = base_y - bh
        frags.append(rect(x, y, bw, bh, fill="#f7fbf8" if col == FIELD else FILL,
                          stroke=col, sw=2.2, rx=10))
        frags.append(text(x + bw / 2, y + 30, title, size=16, bold=True, color=col))
        frags.append(text(x + bw / 2, y + 52, sub, size=12, color=MUTED, italic=True))
        ry = y + 80
        for r in rows:
            frags.append(text(x + bw / 2, ry, r, size=12, color=INK))
            ry += 22
        # номер сходинки
        frags.append(circle(x + 22, y + 22, 13, fill=col, stroke=col))
        frags.append(text(x + 22, y + 27, str(i + 1), size=14, bold=True, color="#ffffff"))
    # спільна вісь-стрілка «більше знаєш — більше можеш»
    frags.append(line(24, base_y + 14, W - 24, base_y + 14, color=INK, sw=2))
    frags.append(text(W / 2, base_y + 34,
                     "що краще апарат знає свій стан — то більше він робить сам",
                     size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "ladder.svg"), W, H, *frags)


def shared_machine():
    """Багато режимів дають ОДНУ ціль → один контролер позиції → мотори."""
    W, H = 760, 400
    frags = []
    frags.append(text(W / 2, 26, "Різні режими — одна машина під ними", size=16, bold=True))

    # ліворуч — стовпчик режимів, кожен лише ВИРІШУЄ, звідки ціль
    modes = [
        ("Loiter / PosHold", "ціль = де відпустив стік"),
        ("Guided", "ціль шле земля/скрипт"),
        ("RTL", "ціль = точка старту"),
        ("Auto", "ціль = маршрутна точка"),
    ]
    mx, mw = 30, 210
    my0, mh, mgap = 70, 56, 16
    for i, (name, how) in enumerate(modes):
        y = my0 + i * (mh + mgap)
        frags.append(rect(mx, y, mw, mh, fill=FILL, stroke=NEG, sw=1.8, rx=8))
        frags.append(text(mx + mw / 2, y + 23, name, size=13, bold=True, color=NEG))
        frags.append(text(mx + mw / 2, y + 42, how, size=11, color=MUTED, italic=True))

    # центр — ОДНА ціль (уставка)
    tx, ty, tw, th = 320, 150, 130, 90
    frags.append(rect(tx, ty, tw, th, fill="#f7fbf8", stroke=FIELD, sw=2.4, rx=10))
    frags.append(mtext(tx + tw / 2, ty + 34,
                      ["ціль по", "положенню", "(N, E, H)"], size=14, bold=True, color=FIELD))
    # стрілки від режимів у ціль
    for i in range(len(modes)):
        y = my0 + i * (mh + mgap) + mh / 2
        frags.append(arrow(mx + mw + 4, y, tx - 4, ty + th / 2, color=NEG, sw=1.6))

    # праворуч — контролер позиції → мотори
    cx, cy, cw, ch = 510, 150, 150, 90
    frags.append(rect(cx, cy, cw, ch, fill=FILL, stroke=INK, sw=2, rx=10))
    frags.append(mtext(cx + cw / 2, cy + 34,
                      ["контролер", "положення", "(той самий)"], size=14, bold=True))
    frags.append(arrow(tx + tw, ty + th / 2, cx, cy + ch / 2, color=INK, sw=2))

    mox, moy, mow, moh = 660, 165, 76, 60
    frags.append(rect(mox, moy, mow, moh, fill=FILL, stroke=POS, sw=1.8, rx=8))
    frags.append(mtext(mox + mow / 2, moy + 28, ["мотори"], size=13, bold=True, color=POS))
    frags.append(arrow(cx + cw, cy + ch / 2, mox, moy + moh / 2, color=INK, sw=2))

    frags.append(text(W / 2, H - 22,
                     "змінюється лише те, ХТО задає ціль; машина під ціллю — спільна",
                     size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "shared.svg"), W, H, *frags)


def gate():
    """Клапан довіри: оцінка → гейт → або в режим, або відмова/падіння назад."""
    W, H = 720, 340
    frags = []
    frags.append(text(W / 2, 26, "Клапан довіри до оцінки положення", size=16, bold=True))

    # вхід: оцінка EKF
    ex, ey, ew, eh = 24, 120, 168, 96
    frags.append(rect(ex, ey, ew, eh, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    frags.append(mtext(ex + ew / 2, ey + 30,
                      ["оцінка EKF", "положення +", "її певність"], size=13, bold=True, color=NEG))

    # гейт-ромб
    gx, gy, gs = 300, 168, 66
    dia = ('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
           'fill="#f7fbf8" stroke="%s" stroke-width="2.4"/>' %
           (gx, gy - gs, gx + gs, gy, gx, gy + gs, gx - gs, gy, FIELD))
    frags.append(dia)
    frags.append(mtext(gx, gy - 4, ["певність", "досить?"], size=13, bold=True, color=FIELD))
    frags.append(arrow(ex + ew, ey + eh / 2, gx - gs - 4, gy, color=INK, sw=2))

    # так → у режим із позицією
    okx, oky, okw, okh = 470, 78, 226, 74
    frags.append(rect(okx, oky, okw, okh, fill="#f7fbf8", stroke=FIELD, sw=2, rx=8))
    frags.append(mtext(okx + okw / 2, oky + 30,
                      ["ТАК → пускаємо в режим", "(Loiter, RTL, Auto…)"],
                      size=13, bold=True, color=FIELD))
    frags.append(arrow(gx + 12, gy - gs + 12, okx - 4, oky + okh / 2, color=FIELD, sw=2))
    frags.append(text(gx + 70, gy - 44, "так", size=12, color=FIELD, italic=True))

    # ні → відмова / падіння на висоту
    nox, noy, now, noh = 470, 196, 226, 74
    frags.append(rect(nox, noy, now, noh, fill="#fdecea", stroke=POS, sw=2, rx=8))
    frags.append(mtext(nox + now / 2, noy + 30,
                      ["НІ → не пускаємо / падаємо", "на висотний режим"],
                      size=13, bold=True, color=POS))
    frags.append(arrow(gx + 12, gy + gs - 12, nox - 4, noy + noh / 2, color=POS, sw=2))
    frags.append(text(gx + 66, gy + 46, "ні", size=12, color=POS, italic=True))

    frags.append(text(W / 2, H - 18,
                     "апарат тримає точку лише тоді, коли впевнено знає, де ця точка",
                     size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "gate.svg"), W, H, *frags)


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

    # зазор близько (майже нема) і далеко (помітний) — вертикальні мірки
    for ad, lab, side in ((3, "близько:\nзазор мізерний", 1), (11, "далеко:\nзазор росте", -1)):
        px, py = on_circle(ad)          # точка на кулі
        plane_y = ty                    # площина горизонтальна на висоті ty
        frags.append(line(px, plane_y, px, py, color=POS, sw=1.8, dash="4,3"))
        frags.append(circle(px, py, 3.5, fill=NEG, stroke=NEG))
        anchor_y = (plane_y + py) / 2
        anc = "start" if side > 0 else "end"
        frags.append(mtext(px + side * 12, anchor_y + (0 if side > 0 else 6),
                          lab.split("\n"), size=11, color=POS, anchor=anc))
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
    ladder()
    shared_machine()
    gate()
    tangent_plane()
    parallel_cos()
    print("ok")
