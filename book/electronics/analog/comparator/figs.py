# -*- coding: utf-8 -*-
"""Фігури до теми «Компаратор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Передатна крива: велетенське A робить із підсилювача сходинку ──────────
def fig_transfer():
    W, H = 720, 440
    f = [text(W / 2, 30, "Велетенське підсилення робить передатну криву сходинкою",
              size=16, bold=True)]

    # осі: різниця входів (гориз.), вихід (верт.); нуль різниці — посередині
    ox, oy = 360, 235          # центр координат
    half_w = 250
    hi_y = 80                  # верхня рейка
    lo_y = 390                 # нижня рейка
    # горизонтальна вісь входу
    f.append(line(ox - half_w, oy, ox + half_w, oy, color=INK, sw=2))
    f.append(arrow(ox + half_w, oy, ox + half_w + 16, oy, color=INK, sw=2))
    f.append(text(ox + half_w + 4, oy + 22, "V₊ − V₋", size=13, anchor="end"))
    # вертикальна вісь виходу
    f.append(line(ox, lo_y, ox, hi_y - 14, color=INK, sw=2))
    f.append(arrow(ox, hi_y - 14, ox, hi_y - 30, color=INK, sw=2))
    f.append(text(ox - 12, hi_y - 18, "Vвих", size=13, anchor="end"))

    # рейки пунктиром
    f.append(line(ox - half_w, hi_y, ox + half_w, hi_y, color=MUTED, sw=1, dash="4,4"))
    f.append(line(ox - half_w, lo_y, ox + half_w, lo_y, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox - half_w + 4, hi_y - 8, "+Vрейки  («1»)", size=12, color=MUTED, anchor="start"))
    f.append(text(ox - half_w + 4, lo_y + 18, "−Vрейки  («0»)", size=12, color=MUTED, anchor="start"))

    # передатна крива: рівнина «0» зліва, майже вертикальний стрибок біля нуля, рівнина «1»
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="3"/>'
             % (ox - half_w, lo_y, ox - 6, lo_y, ox + 6, hi_y, ox + half_w, hi_y, POS))

    # крихітна лінійна зона — підпис праворуч від стрибка
    f.append(text(ox + 12, oy - 30, "лінійна зона —", size=12, color=NEG, anchor="start"))
    f.append(text(ox + 12, oy - 12, "лише мікровольти завширшки", size=12, color=NEG, anchor="start"))

    # підписи боків
    f.append(text(ox - half_w / 2, lo_y - 14, "V₋ більший → вихід унизу", size=12, color=INK))
    f.append(text(ox + half_w / 2, hi_y + 22, "V₊ більший → вихід угорі", size=12, color=INK))

    f.append(text(W / 2, 426,
                  "Між рейками — майже вертикальна стінка: трохи переважив один вхід — і вихід уже на рейці",
                  size=12, color=INK))
    return render(os.path.join(IMG, "transfer-curve.svg"), W, H, *f)


# ── 2. Поріг перетворює плавний сигнал на чітке «вище/нижче» ──────────────────
def fig_threshold():
    W, H = 720, 430
    f = [text(W / 2, 30, "Поріг: плавний сигнал → двійкове «вище/нижче»",
              size=16, bold=True)]

    ox = 80
    ax_w = 560
    # ── верхня панель: вхідний сигнал і поріг ──
    base1 = 150
    amp = 60
    f.append(line(ox, base1, ox + ax_w, base1, color=MUTED, sw=1))         # вісь часу
    f.append(text(ox - 8, base1 - amp - 4, "Vвх", size=12, anchor="end"))

    # поріг
    th_y = base1 - 18
    f.append(line(ox, th_y, ox + ax_w, th_y, color=NEG, sw=1.6, dash="6,4"))
    f.append(text(ox + ax_w, th_y - 6, "поріг", size=12, color=NEG, anchor="end"))

    # плавна крива (синус-горб), що двічі переходить поріг
    import math
    pts = []
    for i in range(0, ax_w + 1, 6):
        x = ox + i
        t = i / ax_w
        y = base1 - amp * math.sin(math.pi * t) * 1.15
        pts.append("%.1f %.1f" % (x, y))
    f.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" L".join(pts), POS))

    # точки перетину порога (де sin*1.15*amp == 18)
    def cross_x(rising):
        # розв'язуємо amp*1.15*sin(pi t) = 18  → sin = 18/(amp*1.15)
        s = 18.0 / (amp * 1.15)
        t = math.asin(s) / math.pi
        if not rising:
            t = 1 - t
        return ox + t * ax_w
    cx1 = cross_x(True)
    cx2 = cross_x(False)
    for cx in (cx1, cx2):
        f.append(line(cx, base1 - amp - 10, cx, base1 + 150, color=MUTED, sw=1, dash="3,4"))
        f.append(circle(cx, th_y, 4, fill=POS, stroke=POS, sw=1))

    # ── нижня панель: цифровий вихід ──
    base2 = 360
    lo = base2
    hi = base2 - 70
    f.append(text(ox - 8, hi - 4, "Vвих", size=12, anchor="end"))
    f.append(text(ox + ax_w + 2, lo + 4, "«0»", size=11, color=MUTED, anchor="start"))
    f.append(text(ox + ax_w + 2, hi + 4, "«1»", size=11, color=MUTED, anchor="start"))
    # прямокутник: «0» до cx1, «1» між cx1 і cx2, «0» після
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.8"/>'
             % (ox, lo, cx1, lo, cx1, hi, cx2, hi, cx2, lo, ox + ax_w, lo, NEG))

    f.append(text((cx1 + cx2) / 2, hi - 10, "сигнал вище порога", size=11, color=NEG))
    f.append(text(ox + (cx1 - ox) / 2, lo + 18, "нижче", size=11, color=MUTED))

    f.append(text(W / 2, 414,
                  "Доки сигнал вище порога — вихід «1»; нижче — «0». Аналогова крива стала чітким рішенням",
                  size=12, color=INK))
    return render(os.path.join(IMG, "threshold-crossing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_transfer()
    fig_threshold()
    print("OK: figures ->", IMG)
