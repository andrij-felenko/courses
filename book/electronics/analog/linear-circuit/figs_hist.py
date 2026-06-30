# -*- coding: utf-8 -*-
"""Фігура до вставки «Народження суперпозиції та еквівалентних джерел» (hist).
Один малюнок:
  superposition-timeline.svg — стрічка часу: Ом 1827 → Кірхгоф 1845 →
      Гельмгольц 1853 (принцип + еквівалентне джерело) → Тевенен 1883 →
      Нортон/Маєр 1926. Показує: ідея зростала десятиліттями, не «один винахідник».
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_timeline():
    W, H = 860, 430
    parts = [text(W/2, 30, "Як визрівали суперпозиція та еквівалентне джерело", size=17, bold=True)]

    # вісь часу
    axy = 150
    x0, x1 = 60, W - 60
    parts.append(line(x0, axy, x1, axy, color=INK, sw=2.4))
    parts.append(arrow(x1 - 30, axy, x1, axy, color=INK, sw=2.4))

    # роки → положення на осі (1820..1935 розкладемо рівномірно за змістом, не лінійно)
    nodes = [
        (1827, "Ом",        "u = R·i\nзакон Ома",                    NEG,  "up"),
        (1845, "Кірхгоф",   "закони вузла\nй контуру",               NEG,  "down"),
        (1853, "Гельмгольц","принцип суперпозиції\n+ еквівалентне джерело", FIELD, "up"),
        (1883, "Тевенен",   "інженерна форма\nеквівалентного джерела", POS, "down"),
        (1926, "Нортон / Маєр", "струмова форма\nеквівалента",        POS,  "up"),
    ]
    xs = [x0 + 30 + i * (x1 - x0 - 60) / (len(nodes) - 1) for i in range(len(nodes))]

    for (yr, who, what, col, side), x in zip(nodes, xs):
        # риска на осі + рік
        parts.append(line(x, axy - 8, x, axy + 8, color=INK, sw=2))
        parts.append(text(x, axy + (24 if side == "up" else -14), str(yr), size=14, bold=True, color=col))
        # картка зі змістом
        cy = axy - 78 if side == "up" else axy + 86
        box, bw, bh = textbox(x, cy, who + "\n" + what, size=11.5, pad=8,
                              fill=FILL, stroke=col, sw=1.6, bold=False)
        parts.append(box)
        # перший рядок (ім'я) — жирним кольором: домалюємо поверх
        # (textbox центрує блок; ім'я вже у блоці — додатково підсвітимо рамкою кольору)
        # тонка лінія від картки до осі
        ly0 = cy + (bh/2 if side == "up" else -bh/2)
        ly1 = axy - 8 if side == "up" else axy + 8
        parts.append(line(x, ly0, x, ly1, color=col, sw=1, dash="3,3"))

    parts.append(text(W/2, H - 18,
                      "одне поняття зростало понад століття — від фізики кіл до інженерного інструмента",
                      size=12.5, italic=True, color=INK))
    render(os.path.join(IMG, "superposition-timeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_timeline()
    print("OK: superposition-timeline")
