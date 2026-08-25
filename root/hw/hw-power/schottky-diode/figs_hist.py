# -*- coding: utf-8 -*-
"""Фігури для вставки «Від котячого вусика до бар'єра Шотткі» (hist).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── hist-timeline: часова лінія однобічного контакту метал—напівпровідник ──────
# Ідея фігури: ефект спостерігали за 64 роки ДО того, як його пояснили. Розтягнута
# в часі відстань між «побачив» (Браун 1874) і «зрозумів чому» (Шотткі 1938) —
# і є головна думка всієї історії.

def fig_timeline():
    W, H = 760, 300
    L, R = 70, 690
    y = 150
    p = []

    p.append(line(L, y, R, y, color=INK, sw=2.5))
    p.append(text(R + 4, y + 5, "→", size=22, color=INK, bold=True, anchor="start"))

    # рік → позиція (лінійно за роками)
    y0, y1 = 1870.0, 1945.0
    def px(year): return L + (year - y0) / (y1 - y0) * (R - L)

    # події: (рік, підпис-верх, підпис-низ, колір, вгору?)
    events = [
        (1874, "Браун", "однобічність\nконтакту", NEG, True),
        (1901, "Бозе", "патент на\nдетектор", MUTED, False),
        (1906, "Пікард", "кремнієвий\n«вусик»", MUTED, True),
        (1938, "Шотткі", "теорія\nбар'єра", FIELD, False),
    ]
    for year, top, bot, col, up in events:
        x = px(year)
        p.append(circle(x, y, 6, fill=col, stroke=col, sw=1.5))
        p.append(text(x, y - 74 if up else y + 88, "%d" % year, size=13, color=INK, bold=True))
        if up:
            p.append(line(x, y - 6, x, y - 58, color=col, sw=1.4, dash="3,3"))
            p.append(text(x, y - 40, top, size=13, color=col, bold=True))
            p.append(mtext(x, y - 24, bot, size=10.5, color=MUTED))
        else:
            p.append(line(x, y + 6, x, y + 40, color=col, sw=1.4, dash="3,3"))
            p.append(text(x, y + 58, top, size=13, color=col, bold=True))
            p.append(mtext(x, y + 74, bot, size=10.5, color=MUTED))

    # дужка «64 роки без пояснення» між Брауном і Шотткі
    xb, xs = px(1874), px(1938)
    yb = y - 108
    p.append(line(xb, yb + 8, xb, yb, color=POS, sw=1.6))
    p.append(line(xs, yb + 8, xs, yb, color=POS, sw=1.6))
    p.append(line(xb, yb, xs, yb, color=POS, sw=1.6))
    p.append(text((xb + xs) / 2, yb - 8, "64 роки: ефект працює, а чому — невідомо",
                  size=12.5, color=POS, bold=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Контакт метал—напівпровідник: спершу користувалися, потім зрозуміли")


# ── hist-three-layers: три різні речі, які плутають під одним словом «винахід» ──
# Ідея: «хто винайшов діод Шотткі» — питання-пастка. Спостереження ефекту,
# теорія бар'єра й промисловий силовий діод — три РІЗНІ досягнення різних людей
# і різних епох. Фігура розкладає їх у три чіткі колонки.

def fig_three_layers():
    W, H = 760, 330
    p = []
    cols = [
        ("СПОСТЕРЕЖЕННЯ", "Браун, 1874", NEG, "#e8eefc",
         "притиснув вістря\nдо кристала —\nструм тече в один бік.\nЧому — не знав"),
        ("ТЕОРІЯ", "Шотткі, 1938", FIELD, "#eaf7ef",
         "бар'єр на контакті =\nрізниця робіт виходу.\nПояснив ефект —\nзвідси й назва"),
        ("СИЛОВИЙ ДІОД", "промисловість, 1960-ті+", POS, "#fdece9",
         "кремнієвий Шотткі\nяк деталь: низьке Vf,\nбез Qrr — у джерелах\nживлення"),
    ]
    bw, gap = 210, 20
    x0 = (W - (3 * bw + 2 * gap)) / 2
    top, bh = 70, 210
    for i, (head, who, col, fill, body) in enumerate(cols):
        x = x0 + i * (bw + gap)
        p.append(rect(x, top, bw, bh, fill=fill, stroke=col, sw=2.2))
        p.append(text(x + bw / 2, top + 30, head, size=15, color=col, bold=True))
        p.append(text(x + bw / 2, top + 54, who, size=12, color=INK, bold=True))
        p.append(line(x + 18, top + 66, x + bw - 18, top + 66, color=col, sw=1.2))
        p.append(mtext(x + bw / 2, top + 92, body, size=11.5, color=INK, lh=1.35))
        if i < 2:
            ax = x + bw + gap / 2
            p.append(text(ax, top + bh / 2 + 6, "→", size=26, color=MUTED, bold=True))

    p.append(text(W / 2, top + bh + 34,
                  "«Хто винайшов діод Шотткі» — питання-пастка: це три різні досягнення різних людей",
                  size=12.5, color=INK, italic=True))

    render(os.path.join(OUT, "hist-three-layers.svg"), W, H, *p,
           title="Три різні речі, які ховаються за словом «винахід»")


if __name__ == "__main__":
    fig_timeline()
    fig_three_layers()
    print("OK: hist figures written to", OUT)
