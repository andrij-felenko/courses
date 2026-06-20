# -*- coding: utf-8 -*-
"""Фігури до вставки «Електролітичні й танталові: полярність».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Контраст полярності: смуга «−» (алюм.) проти смуги «+» (тантал) ──────────
def fig_polarity_contrast():
    W, H = 760, 470
    f = [text(W / 2, 30, "Той самий знак — поперечна смуга — означає протилежний полюс",
              size=16, bold=True)]

    # ── Рядок 1: алюмінієва «банка», смуга = МІНУС ──────────────────────────
    y = 78
    f.append(text(40, y - 8, "Алюмінієвий електролітичний («банка»)",
                  size=14, bold=True, anchor="start", color=INK))

    # корпус-банка
    cx, cy, cw, ch = 70, y + 6, 150, 70
    f.append(rect(cx, cy, cw, ch, fill="#eef2f7", stroke=LINE, sw=2, rx=10))
    # світла смуга з мінусами уздовж лівого боку
    sb = 26
    f.append(rect(cx, cy, sb, ch, fill="#dbe2ea", stroke=NEG, sw=2, rx=10))
    f.append(mtext(cx + sb / 2, cy + 22, ["−", "−", "−"], size=14, color=NEG, bold=True, lh=1.1))
    # підпис, на що вказує смуга
    f.append(arrow(cx + sb / 2, cy + ch + 6, cx + sb / 2, cy + ch + 26, color=NEG, sw=2))
    f.append(minus(cx + sb / 2, cy + ch + 42, r=11))
    f.append(text(cx + sb / 2, cy + ch + 64, "смуга = мінус", size=12, color=NEG))
    # плюсовий бік
    f.append(plus(cx + cw - 18, cy + ch + 42, r=11))

    # наслідок реверсу
    box = fitbox(300, cy - 2, 430, ch + 10,
                 "Реверс: електроліт кипить → газ →\nзапобіжний клапан стравлює.\nРідко пожежа.",
                 size=13, fill="#eef6ee", stroke=FIELD, sw=1.6)
    f.append(box)

    # розділювач
    f.append(line(40, 232, W - 40, 232, color=MUTED, sw=1, dash="5 5"))

    # ── Рядок 2: танталовий SMD, смуга = ПЛЮС ───────────────────────────────
    y2 = 268
    f.append(text(40, y2 - 8, "Танталовий SMD",
                  size=14, bold=True, anchor="start", color=INK))

    tx, ty, tw, th = 70, y2 + 6, 150, 70
    f.append(rect(tx, ty, tw, th, fill="#f6e9b0", stroke="#b08900", sw=2, rx=8))
    # світла смуга на правому торці = ПЛЮС
    f.append(rect(tx + tw - sb, ty, sb, th, fill="#fff7d6", stroke=POS, sw=2.4, rx=8))
    f.append(text(tx + tw - sb / 2, ty + th / 2 + 6, "+", size=20, color=POS, bold=True))
    # підпис, на що вказує смуга
    f.append(arrow(tx + tw - sb / 2, ty + th + 6, tx + tw - sb / 2, ty + th + 26, color=POS, sw=2))
    f.append(plus(tx + tw - sb / 2, ty + th + 42, r=11))
    f.append(text(tx + tw - sb / 2, ty + th + 64, "смуга = ПЛЮС", size=12, color=POS, bold=True))
    # мінусовий бік
    f.append(minus(tx + 16, ty + th + 42, r=11))

    box2 = fitbox(300, ty - 2, 430, th + 10,
                  "Реверс: пробій → Ta горить у\nкисні з MnO₂ → вогонь за мс.\nНизька напруга НЕ рятує.",
                  size=13, fill="#fdecea", stroke=POS, sw=1.8)
    f.append(box2)

    render(os.path.join(IMG, "polarity-contrast.svg"), W, H, *f)


if __name__ == "__main__":
    fig_polarity_contrast()
    print("OK: img/polarity-contrast.svg")
