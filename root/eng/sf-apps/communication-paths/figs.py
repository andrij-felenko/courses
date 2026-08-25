# -*- coding: utf-8 -*-
"""Фігури до статті «Комунікаційні шляхи як обмеження архітектури».
Дві фігури:
  conway-mirror.svg — товщина зв'язку в коді копіює товщину зв'язку між людьми;
  paths-growth.svg  — число комунікаційних шляхів n·(n−1)/2 злітає квадратично.
Генерує SVG у ./img/. Запуск: python figs.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_mirror():
    """Ліворуч тісний канал → товстий стик; праворуч бідний канал → тонкий шов."""
    W, H = 760, 430
    frags = []

    # Заголовки колонок з великим запасом, щоб не налазили на фігури нижче.
    frags.append(text(200, 54, "Тісне спілкування", size=15, bold=True, color=POS))
    frags.append(text(560, 54, "Рідке спілкування", size=15, bold=True, color=NEG))

    # Вертикальний роздільник між сценаріями.
    frags.append(line(380, 78, 380, H - 20, color=MUTED, sw=1.2, dash="5 5"))

    # ── Лівий сценарій: двоє поруч, товстий стик ──
    # люди
    frags.append(circle(150, 120, 20, fill="#fdecea", stroke=POS, sw=2))
    frags.append(circle(250, 120, 20, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(150, 125, "A", size=14, bold=True, color=POS))
    frags.append(text(250, 125, "B", size=14, bold=True, color=POS))
    # густий канал між людьми (кілька ліній = багатий зв'язок)
    for dy in (-6, 0, 6):
        frags.append(line(170, 120 + dy, 230, 120 + dy, color=POS, sw=2))
    frags.append(text(200, 158, "багатий канал", size=11, color=MUTED))

    # їхні модулі внизу з ТОВСТИМ переплетеним стиком
    frags.append(fitbox(96, 250, 100, 70, "модуль A", size=13, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(fitbox(204, 250, 100, 70, "модуль B", size=13, fill="#fdecea", stroke=POS, sw=1.8))
    # товстий стик (кілька товстих ліній)
    for dy in (-10, -3, 4, 11):
        frags.append(line(196, 285 + dy, 204, 285 + dy, color=POS, sw=3))
    frags.append(text(200, 350, "товстий переплетений стик", size=12, bold=True, color=POS))

    # ── Правий сценарій: далеко, тонкий шов ──
    frags.append(circle(490, 120, 20, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(circle(630, 120, 20, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(490, 125, "C", size=14, bold=True, color=NEG))
    frags.append(text(630, 125, "D", size=14, bold=True, color=NEG))
    # одна тонка лінія = бідний зв'язок
    frags.append(line(510, 120, 610, 120, color=NEG, sw=1.4, dash="4 4"))
    frags.append(text(560, 158, "бідний канал", size=11, color=MUTED))

    frags.append(fitbox(436, 250, 100, 70, "модуль C", size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(fitbox(624, 250, 100, 70, "модуль D", size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    # тонкий шов
    frags.append(line(536, 285, 624, 285, color=NEG, sw=1.4, dash="4 4"))
    frags.append(text(580, 350, "тонкий бідний шов", size=12, bold=True, color=NEG))

    # Нижній підпис-висновок
    frags.append(text(W / 2, 402, "стик у коді повторює канал між людьми", size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'conway-mirror.svg'), W, H, *frags)


def fig_growth():
    """Крива n·(n−1)/2: майже пологa, тоді круто злітає."""
    W, H = 720, 460
    frags = []
    frags.append(text(W / 2, 30, "Комунікаційні шляхи = n · (n − 1) / 2", size=16, bold=True))

    # осі
    ox, oy = 100, 380          # початок координат (лівий-низ)
    axw, axh = 540, 300        # довжина осей
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))         # X
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))         # Y
    frags.append(text(ox + axw / 2, oy + 46, "людей у групі (n)", size=13, color=INK))
    # підпис осі Y — вертикально, ліворуч від осі, з запасом
    frags.append('<text x="34" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 34 %.1f)">число шляхів</text>'
                 % (oy - axh / 2, FONT, INK, oy - axh / 2))

    # дані
    pts = [(3, 3), (5, 10), (10, 45), (20, 190), (50, 1225)]
    nmax, ymax = 50.0, 1225.0

    def px(n):
        return ox + (n / nmax) * axw

    def py(v):
        return oy - (v / ymax) * axh

    # крива (гладка ламана через точки формули з дрібним кроком)
    poly = []
    n = 2
    while n <= 50:
        v = n * (n - 1) / 2
        poly.append("%.1f,%.1f" % (px(n), py(v)))
        n += 1
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
                 % (" ".join(poly), POS))

    # опорні точки + підписи значень (розставлені так, щоб не налазити)
    for n, v in pts:
        cx, cy = px(n), py(v)
        frags.append(circle(cx, cy, 5, fill=BG, stroke=POS, sw=2))
        # позначка n на осі X
        frags.append(line(cx, oy, cx, oy + 5, color=INK, sw=1.5))
        frags.append(text(cx, oy + 22, str(n), size=12, color=INK))
        # значення шляхів — над точкою, зі зсувом ліворуч для тісних нижніх
        if v <= 45:
            frags.append(text(cx + 26, cy + 4, str(v), size=12, bold=True, color=POS))
        else:
            frags.append(text(cx, cy - 14, str(v), size=13, bold=True, color=POS))

    # анотація крутого злету
    frags.append(text(px(38), py(700), "круто злітає", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'paths-growth.svg'), W, H, *frags)


# ── Фігури до вставки math-communication-paths.md ───────────────────────────

def fig_complete_graphs():
    """K3, K5, K10 поруч: вершини по колу, УСІ ребра — павутина густішає квадратично."""
    W, H = 780, 380
    frags = []
    frags.append(text(W / 2, 30, "Команда як повний граф Kₙ: людина — вершина, канал — ребро",
                      size=15, bold=True))

    # три панелі: (центр_x, радіус_кола, n, підпис-число-ребер)
    panels = [(140, 62, 3, "K₃ — 3 ребра"),
              (390, 68, 5, "K₅ — 10 ребер"),
              (650, 78, 10, "K₁₀ — 45 ребер")]
    cy = 200

    for cx, R, n, cap in panels:
        # позиції вершин рівномірно по колу (старт зверху)
        pts = []
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
        # спершу всі ребра (щоб вершини лягли зверху)
        for i in range(n):
            for j in range(i + 1, n):
                frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1],
                                  color=NEG, sw=1.0))
        # вершини
        for (vx, vy) in pts:
            frags.append(circle(vx, vy, 6, fill=BG, stroke=POS, sw=2))
        # підпис під панеллю — з великим запасом, поза колом
        frags.append(text(cx, cy + R + 46, cap, size=13, bold=True, color=INK))

    # нижній рядок-висновок, окремо, щоб не налазив на підписи панелей
    frags.append(text(W / 2, H - 16,
                      "вершини ростуть по колу рівно — ребра всередині вибухають",
                      size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'complete-graphs.svg'), W, H, *frags)


def fig_linear_vs_quadratic():
    """Пряма 'праця' проти параболи 'координація'; позначена точка перетину."""
    W, H = 720, 470
    frags = []
    frags.append(text(W / 2, 30, "Праця росте лінійно, координація — квадратично", size=16, bold=True))

    ox, oy = 100, 390          # початок координат (лівий-низ)
    axw, axh = 540, 310        # довжина осей
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))    # X
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))    # Y
    frags.append(text(ox + axw / 2, oy + 44, "людей у групі (n)", size=13, color=INK))
    frags.append('<text x="34" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 34 %.1f)">одиниць</text>'
                 % (oy - axh / 2, FONT, INK, oy - axh / 2))

    nmax = 16.0
    # коефіцієнти підібрані так, щоб перетин був у видимій, наочній точці
    a = 3.2           # праця: a·n
    b = 0.5           # координація: b·n·(n−1)/2
    ymax = b * nmax * (nmax - 1) / 2      # найвище значення (парабола на nmax)

    def px(n):
        return ox + (n / nmax) * axw

    def py(v):
        return oy - (v / ymax) * axh

    # парабола координації
    poly = []
    n = 0.0
    while n <= nmax + 0.001:
        v = b * n * (n - 1) / 2
        if v < 0:
            v = 0
        poly.append("%.1f,%.1f" % (px(n), py(v)))
        n += 0.25
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(poly), POS))

    # пряма праці a·n від 0 до nmax
    frags.append(line(px(0), py(0), px(nmax), py(a * nmax), color=NEG, sw=2.6))

    # точка перетину: a·n = b·n·(n−1)/2  →  n = 2a/b + 1
    ncross = 2 * a / b + 1
    vcross = a * ncross
    cxp, cyp = px(ncross), py(vcross)
    frags.append(line(cxp, oy, cxp, cyp, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(circle(cxp, cyp, 6, fill=BG, stroke=INK, sw=2))
    frags.append(text(cxp, oy + 22, "межа", size=12, bold=True, color=INK))

    # підписи кривих — біля їхніх правих кінців, рознесені по вертикалі
    frags.append(text(px(nmax) - 6, py(a * nmax) - 12, "праця  a·n", size=13,
                      bold=True, color=NEG, anchor="end"))
    frags.append(text(px(nmax) - 6, py(b * nmax * (nmax - 1) / 2) - 10,
                      "координація  b·n(n−1)/2", size=13, bold=True, color=POS, anchor="end"))

    # анотації зон — з великим відступом, щоб не лягли на криві
    frags.append(text(px(3.2), oy - 24, "тут наймати", size=11, italic=True, color=MUTED))
    frags.append(text(px(13.4), oy - 210, "тут — на шкоду", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'linear-vs-quadratic.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_mirror()
    fig_growth()
    fig_complete_graphs()
    fig_linear_vs_quadratic()
    print("figs OK ->", IMG)
