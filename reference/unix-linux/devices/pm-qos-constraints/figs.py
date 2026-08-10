# -*- coding: utf-8 -*-
"""Фігури до теми «Вимоги PM QoS»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG  = "#eaf0fd"
GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"


# ── Агрегація вимог за мінімумом ─────────────────────────────────────────────
def fig_aggregation():
    W, H = 980, 430

    P = []
    LX = 210          # центр стовпця споживачів
    AX0, AY0, AW, AH = 470, 150, 170, 130   # рамка агрегації
    RX = 830          # центр рамки результату

    consumers = [
        (110, "Процес A", "не більше 100 мкс"),
        (215, "Процес B", "не більше 10 мкс"),
        (320, "Мережевий драйвер", "не більше 50 мкс"),
    ]

    edges = []
    for cy, who, what in consumers:
        body, w, h = textbox(LX, cy, who + "\n" + what, size=14,
                             fill=BLUE_BG, stroke=NEG, sw=1.6)
        P.append(body)
        edges.append((LX + w / 2, cy))

    P.append(fitbox(AX0, AY0, AW, AH,
                    "PM QoS\nсписок вимог\nCPU latency QoS\nагрегація min()",
                    size=14, fill=GREEN_BG, stroke=FIELD, sw=1.8))

    res, rw, rh = textbox(RX, AY0 + AH / 2, "cpuidle\nціль 10 мкс", size=14,
                          fill=RED_BG, stroke=POS, sw=1.8)
    P.append(res)

    targets = [(AX0 - 6, AY0 + 24), (AX0 - 6, AY0 + AH / 2), (AX0 - 6, AY0 + AH - 24)]
    for (x1, y1), (x2, y2) in zip(edges, targets):
        P.append(arrow(x1 + 6, y1, x2, y2, color=NEG))

    P.append(arrow(AX0 + AW + 6, AY0 + AH / 2, RX - rw / 2 - 6, AY0 + AH / 2))

    P.append(text(LX, 385, "три незалежні вимоги", size=12.5, color=MUTED))
    P.append(text(AX0 + AW / 2, 385, "min(100, 10, 50) = 10", size=12.5, color=MUTED))
    P.append(text(RX, 385, "глибші стани заборонено", size=12.5, color=MUTED))

    P.append(text(W / 2, 412,
                  "виграє найжорсткіша вимога: щойно процес B закриє дескриптор, "
                  "ціллю стане 50 мкс",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "pm-qos-aggregation.svg"), W, H, *P,
           title="Об'єднання вимог у єдине обмеження CPU latency QoS")


if __name__ == "__main__":
    fig_aggregation()
    print("ok")
