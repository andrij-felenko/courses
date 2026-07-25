# -*- coding: utf-8 -*-
"""figs.py — фігура до статті «Належність точки багатокутнику (метод променя)».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Метод променя (ray casting) — парність перетинів ─────────────────────────
# Ідея: пускаємо з точки промінь праворуч і рахуємо перетини межі багатокутника.
# Непарно = всередині, парно = зовні. Показуємо дві точки: внутрішню (1 перетин)
# і зовнішню (2 перетини крізь виступ).
def fig_ray_casting():
    W, H = 900, 470
    P = []
    P.append(text(W / 2, 30, "Метод променя: парність перетинів межі",
                  size=17, bold=True))

    # неопуклий багатокутник із виступом праворуч (щоб зовнішній промінь дав 2)
    poly = [(150, 110), (470, 90), (470, 220), (620, 260),
            (470, 300), (480, 410), (170, 400), (120, 250)]
    pts = " ".join("%.0f,%.0f" % (x, y) for x, y in poly)
    P.append('<polygon points="%s" fill="#e9f7ef" stroke="%s" stroke-width="2.4"/>'
             % (pts, FIELD))
    P.append(text(300, 78, "багатокутник (дозволена зона)", size=11.5,
                  color=FIELD, bold=True))

    import math

    def crossings_right(px, py):
        """Точки перетину горизонталі y=py, x>=px зі сторонами полігона."""
        xs = []
        n = len(poly)
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if (yi > py) != (yj > py):
                xc = xi + (py - yi) * (xj - xi) / (yj - yi)
                if px < xc:
                    xs.append(xc)
            j = i
        return sorted(xs)

    # промінь із точки: лінія праворуч + позначки перетинів + підпис парності
    def ray(px, py, col, fillc, label):
        xs = crossings_right(px, py)
        xend = W - 40
        P.append(circle(px, py, 6.5, fill=fillc, stroke=col, sw=2.4))
        # сам промінь (пунктир до краю)
        P.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="6 5" marker-end="url(#arrow)"/>'
                 % (px, py, xend, py, col))
        # точки перетину — маленькі гарячі кружки
        for xc in xs:
            P.append(circle(xc, py, 4.5, fill=BG, stroke=POS, sw=2.2))
        parity = "непарно → ВСЕРЕДИНІ" if len(xs) % 2 else "парно → ЗЗОВНІ"
        P.append(text(px, py - 14, label, size=10.5, color=col, bold=True))
        P.append(text(xend, py - 8, "%d перетин(и) — %s" % (len(xs), parity),
                      size=10.5, color=col, bold=True, anchor="end"))

    ray(250, 190, NEG, "#eaf0fd", "точка A (в зоні)")     # внутрішня → 1 перетин
    ray(60, 330, POS, "#fdecea", "точка B (поза)")         # зовнішня → 2 перетини

    # легенда перетину
    P.append(circle(160, 445, 4.5, fill=BG, stroke=POS, sw=2.2))
    P.append(text(172, 449, "— перетин променя зі стороною межі",
                  size=10.5, color=MUTED, anchor="start"))

    render("img/ray-casting.svg", W, H, *P)


if __name__ == "__main__":
    fig_ray_casting()
    print("OK: 1 figure -> img/")
