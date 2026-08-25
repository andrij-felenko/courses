# -*- coding: utf-8 -*-
# Окремий генератор фігури для вставки proj-migration-window (щоб не заважати
# паралельним правкам основного figs.py). Вивід у ту саму теку img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Напрям делегування v1↔v2 у вікні міграції ───────────────────────────────
def fig_delegation_direction():
    W, H = 800, 400
    frags = []
    frags.append(text(W / 2, 30, "Напрям делегування вирішує все", size=17, bold=True))

    box_w = 176
    v2x = 145          # центр рамки v2 (ліворуч)
    v1x = W - 145      # центр рамки v1 (праворуч)

    def version_box(cx, cy, title, fmt, fill, stroke, tcolor):
        b, w, h = textbox(cx, cy, title + "\n" + fmt, size=12, bold=True,
                          pad=9, fill=fill, stroke=stroke, color=tcolor, min_w=box_w)
        frags.append(b)
        return w, h

    # ── Ряд 1: ХИБНИЙ напрям — v2 кличе v1, бракує валюти ──
    y1 = 100
    frags.append(text(W / 2, y1 - 40, "Хибно: новий кличе старого", size=13,
                      bold=True, color="#a02419"))
    version_box(v2x, y1, "v2 (новий)", "потребує {value, currency}", "#fdecea", POS, "#a02419")
    version_box(v1x, y1, "v1 (старий)", "має лише ціле amount", "#eef1f4", MUTED, INK)
    # стрілка v2 → v1 (напис над стрілкою, поза лінією)
    frags.append(arrow(v2x + box_w / 2 + 6, y1, v1x - box_w / 2 - 6, y1, color=POS, sw=2.2))
    b, w, h = textbox(W / 2, y1 - 17, "кличе, щоб розширити", size=11, bold=True,
                      pad=5, fill=BG, stroke=POS, color="#a02419")
    frags.append(b)
    # присуд під рядом
    b, w, h = textbox(W / 2, y1 + 58,
                      "валюти нізвідки взяти — новий формат скалічений",
                      size=12, bold=True, pad=7, fill="#fdecea", stroke=POS, color="#a02419")
    frags.append(b)

    # роздільна лінія
    frags.append(line(50, 214, W - 50, 214, color=MUTED, sw=1, dash="4 4"))

    # ── Ряд 2: ПРАВИЛЬНИЙ напрям — v1 кличе v2, звужує ──
    y2 = 300
    frags.append(text(W / 2, y2 - 40, "Правильно: старий кличе нового", size=13,
                      bold=True, color="#1e7a44"))
    version_box(v2x, y2, "v2 (новий)", "повний {value, currency}", "#eaf7ef", FIELD, "#1e7a44")
    version_box(v1x, y2, "v1 (старий)", "тонка обгортка", "#eaf7ef", FIELD, "#1e7a44")
    # стрілка v1 → v2 (справа наліво)
    frags.append(arrow(v1x - box_w / 2 - 6, y2, v2x + box_w / 2 + 6, y2, color=FIELD, sw=2.2))
    b, w, h = textbox(W / 2, y2 - 17, "кличе, щоб звузити", size=11, bold=True,
                      pad=5, fill=BG, stroke=FIELD, color="#1e7a44")
    frags.append(b)
    # присуд під рядом
    b, w, h = textbox(W / 2, y2 + 58,
                      "валюту відкидаємо — стара відповідь = точний зріз нової",
                      size=12, bold=True, pad=7, fill="#eaf7ef", stroke=FIELD, color="#1e7a44")
    frags.append(b)

    render(os.path.join(IMG, 'delegation-direction.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_delegation_direction()
    print("delegation figure written")
