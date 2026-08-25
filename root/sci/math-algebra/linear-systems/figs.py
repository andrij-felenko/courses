# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Лінійні системи».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: три геометричні випадки перетину прямих ─────────────────────────
# Серце питання «скільки розв'язків»: дві прямі на площині або перетинаються в
# одній точці (єдиний), або паралельні (нема), або збігаються (безліч). Кожне
# рівняння системи 2×2 — пряма; розв'язок — спільні точки. Три панелі поряд.
def fig_three_cases():
    W, H = 1000, 380
    pw = 300                       # ширина однієї панелі
    gap = 30
    x0s = [20, 20 + pw + gap, 20 + 2 * (pw + gap)]   # 20, 350, 680 → правий край 980
    top = 60
    ph = 270
    parts = []

    def panel(px, lines, dot, caption, color2):
        """px — лівий край панелі; lines — список ((ax,ay),(bx,by),колір) у локальних
        координатах [-3..3]; dot — точка перетину або None; caption — підпис унизу."""
        cx, cy = px + pw / 2, top + ph / 2
        scale = (ph - 50) / 6.0     # 6 одиниць у висоту
        out = [rect(px, top, pw, ph, fill="#fbfcfd", stroke="#d8dde3", sw=1.2)]
        # осі
        out.append(line(px + 16, cy, px + pw - 16, cy, color=MUTED, sw=1.0))
        out.append(line(cx, top + 16, cx, top + ph - 16, color=MUTED, sw=1.0))

        def to_px(u, v):
            return cx + u * scale, cy - v * scale
        for (a, b, col) in lines:
            ax, ay = to_px(*a); bx, by = to_px(*b)
            out.append(line(ax, ay, bx, by, color=col, sw=2.4))
        if dot:
            dx, dy = to_px(*dot)
            out.append(circle(dx, dy, 6, fill=FIELD, stroke="#0e6b35", sw=2))
        out.append(text(cx, top + ph + 26, caption, size=14, bold=True, color=color2))
        return out

    # Панель A — єдиний розв'язок: x+y=2  та  x−y=0  →  (1,1)
    parts += panel(x0s[0],
                   [((-3, 5), (3, -1), POS),      # x+y=2 → y=2−x
                    ((-3, -3), (3, 3), NEG)],      # x−y=0 → y=x
                   (1, 1),
                   "єдиний розв'язок", INK)
    parts.append(text(x0s[0] + pw / 2, top + ph + 46, "прямі перетинаються в 1 точці",
                      size=11, color=MUTED))

    # Панель B — нема розв'язку: x+y=1 та x+y=3 (паралельні)
    parts += panel(x0s[1],
                   [((-3, 4), (3, -2), POS),      # x+y=1
                    ((-1, 4), (3, 0), NEG)],       # x+y=3 (зсунута паралель)
                   None,
                   "нема розв'язку", INK)
    parts.append(text(x0s[1] + pw / 2, top + ph + 46, "паралельні — не перетинаються",
                      size=11, color=MUTED))

    # Панель C — безліч розв'язків: x+y=2 та 2x+2y=4 (та сама пряма)
    parts += panel(x0s[2],
                   [((-3, 5), (3, -1), POS)],     # одна пряма (друга збігається)
                   None,
                   "безліч розв'язків", INK)
    # позначка, що друга пряма лежить поверх першої
    cx2 = x0s[2] + pw / 2
    parts.append(text(cx2, top + ph + 46, "обидві прямі збігаються", size=11, color=MUTED))

    render("img/three-cases.svg", W, H, *parts,
           title="Дві прямі на площині: три можливі картини перетину")


# ── Фігура 2: картина стовпців — Ax=b як рецепт суміші ────────────────────────
# Чому саме Ax=b і коли b досяжний. Стовпці A — вектори a₁, a₂; розв'язок (x,y) —
# ваги, з якими їх змішати, щоб дістати b. Малюємо a₁, a₂ та цільовий b як суму
# x·a₁ + y·a₂ (паралелограм). Видно: b досяжний, бо лежить у площині стовпців.
def fig_column_picture():
    W, H = 880, 440
    ox, oy = 170, 350
    s = 52                         # пікселів на одиницю
    parts = []

    parts.append(arrow(ox - 30, oy, ox + 420, oy, color=INK, sw=1.6))
    parts.append(arrow(ox, oy + 30, ox, oy - 300, color=INK, sw=1.6))

    def P(u, v):
        return ox + u * s, oy - v * s

    # стовпці матриці: a1=(2,1), a2=(-1,2); шукаємо x,y: x·a1+y·a2 = b=(3,4)
    a1 = (2, 1); a2 = (-1, 2); xw, yw = 2, 1     # 2·a1 + 1·a2 = (3,4) = b
    b = (xw * a1[0] + yw * a2[0], xw * a1[1] + yw * a2[1])

    # масштабовані внески (пунктиром — паралелограм складання)
    xa = (xw * a1[0], xw * a1[1])                # 2·a1 = (4,2)
    ya = (yw * a2[0], yw * a2[1])                # 1·a2 = (-1,2)

    # сторони паралелограма
    p_xa = P(*xa); p_b = P(*b); p_o = P(0, 0)
    parts.append(line(p_xa[0], p_xa[1], p_b[0], p_b[1], color=MUTED, sw=1.2, dash="5,4"))
    parts.append(line(P(*ya)[0], P(*ya)[1], p_b[0], p_b[1], color=MUTED, sw=1.2, dash="5,4"))

    # базові стовпці a1, a2 (одиничні напрямки)
    parts.append(arrow(ox, oy, *P(*a1), color=POS, sw=2.4))
    parts.append(arrow(ox, oy, *P(*a2), color=NEG, sw=2.4))
    parts.append(text(P(*a1)[0] + 14, P(*a1)[1] + 16, "a₁", size=15, bold=True, italic=True, color=POS))
    parts.append(text(P(*a2)[0] - 18, P(*a2)[1] - 6, "a₂", size=15, bold=True, italic=True, color=NEG))

    # масштабовані внески x·a1 (вздовж a1) та паралельний перенос y·a2
    parts.append(arrow(ox, oy, *P(*xa), color=POS, sw=1.6))
    parts.append(text((ox + P(*xa)[0]) / 2 + 4, (oy + P(*xa)[1]) / 2 + 22, "x·a₁",
                      size=13, color=POS))
    parts.append(text((p_xa[0] + p_b[0]) / 2 + 8, (p_xa[1] + p_b[1]) / 2, "y·a₂",
                      size=13, color=NEG, anchor="start"))

    # цільовий вектор b
    parts.append(arrow(ox, oy, *p_b, color=FIELD, sw=2.8))
    parts.append(text(p_b[0] + 12, p_b[1] - 8, "b", size=16, bold=True, italic=True, color=FIELD))

    box, bw, bh = textbox(W - 168, 96,
                          "Ax = b означає:\nзмішати стовпці a₁, a₂\nз вагами x, y → дістати b\nтут  2·a₁ + 1·a₂ = b",
                          size=12.5, pad=12, fill="#f4f6f8")
    parts.append(box)

    render("img/column-picture.svg", W, H, *parts,
           title="Картина стовпців: розв'язок — це рецепт, як змішати стовпці A у b")


# ── Фігура 3: виключення = той самий розв'язок, інші рядки ────────────────────
# ЧОМУ елементарні дії не псують розв'язку: рядок — це пряма; замінюючи рядок R2
# на R2−k·R1, ми міняємо саму пряму, але вона ОБЕРТАЄТЬСЯ навколо спільної точки
# перетину — тож точка-розв'язок лишається на місці. Ліва панель: до; права: після.
def fig_elimination_invariant():
    W, H = 880, 400
    pw = 380; gap = 60
    x0s = [30, 30 + pw + gap]
    top = 64; ph = 280
    parts = []

    def panel(px, second_line, caption):
        cx, cy = px + pw / 2, top + ph / 2
        scale = (ph - 50) / 6.0
        out = [rect(px, top, pw, ph, fill="#fbfcfd", stroke="#d8dde3", sw=1.2)]
        out.append(line(px + 16, cy, px + pw - 16, cy, color=MUTED, sw=1.0))
        out.append(line(cx, top + 16, cx, top + ph - 16, color=MUTED, sw=1.0))

        def to_px(u, v):
            return cx + u * scale, cy - v * scale
        ylim = 2.6                  # межа видимого вікна по y (трохи менша за пів-висоту)

        def seg(f):
            """кінці прямої y=f(x), обрізані до [-ylim..ylim] по y, щоб не вилазили."""
            pts = []
            for x in (-2.5, 2.5):
                y = f(x)
                if y > ylim:    x = (ylim - (f(0))) / (f(1) - f(0)); y = ylim
                elif y < -ylim: x = (-ylim - (f(0))) / (f(1) - f(0)); y = -ylim
                pts.append((max(-2.5, min(2.5, x)), y))
            return to_px(*pts[0]), to_px(*pts[1])

        # перша пряма (опорна, незмінна): x+y=2 → y=2−x
        a, b = seg(lambda x: 2 - x)
        out.append(line(a[0], a[1], b[0], b[1], color=POS, sw=2.4))
        out.append(text(b[0] - 8, b[1] + 16, "R₁", size=13, bold=True, color=POS, anchor="start"))
        # друга пряма — задана функцією y(x)
        (f, lbl) = second_line
        a2, b2 = seg(f)
        out.append(line(a2[0], a2[1], b2[0], b2[1], color=NEG, sw=2.4))
        out.append(text(b2[0] - 8, b2[1] + 4, lbl, size=13, bold=True, color=NEG, anchor="start"))
        # спільна точка-розв'язок (1,1) — однакова в обох панелях
        d = to_px(1, 1)
        out.append(circle(d[0], d[1], 6, fill=FIELD, stroke="#0e6b35", sw=2))
        out.append(text(d[0] + 12, d[1] - 8, "(1, 1)", size=12, color="#0e6b35"))
        out.append(text(cx, top + ph + 26, caption, size=13, bold=True))
        return out

    # до: R2 = 3x−y=2  → y=3x−2  (через (1,1))
    parts += panel(x0s[0], (lambda x: 3 * x - 2, "R₂"),
                   "до: R₂ задано як 3x − y = 2")
    # після R2 ← R2 − 3·R1: коефіцієнти інші, але пряма досі через (1,1):
    # (3x−y) − 3(x+y) = 2 − 3·2  → −4y = −4 → y=1 (горизонталь через точку)
    parts += panel(x0s[1], (lambda x: 1.0, "R₂′"),
                   "після R₂ ← R₂ − 3·R₁: −4y = −4")

    parts.append(text(W / 2, H - 12,
                      "пряма R₂ обернулася навколо спільної точки — розв'язок не зрушив",
                      size=12, color=MUTED))

    render("img/elimination-invariant.svg", W, H, *parts,
           title="Чому виключення не псує розв'язку: точка перетину лишається на місці")


if __name__ == "__main__":
    fig_three_cases()
    fig_column_picture()
    fig_elimination_invariant()
    print("OK: img/three-cases.svg, img/column-picture.svg, img/elimination-invariant.svg")
