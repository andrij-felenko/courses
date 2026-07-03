# -*- coding: utf-8 -*-
"""Фігура до вставки «hist-compass-dance.md»
(guide/embedded/avtopilot/fc-setup-calibration).
Та сама задача на кораблі й на дроні: власне залізо носія зсуває й розтягує
слабке коло поля Землі. Чистий Python; svgkit — зі scripts/ (не переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Одна задача — дві епохи. Ліворуч корабель, праворуч дрон; посередині — те саме
# коло вимірів компаса, яке власне залізо носія зсуває (тверде) й розтягує (м'яке).
# ─────────────────────────────────────────────────────────────────────────────
def fig_same_problem():
    W, H = 960, 470
    frags = [text(W / 2, 28, "Та сама задача двічі: залізо носія псує слабке поле Землі",
                  size=16, bold=True)]

    # --- центральна панель: коло вимірів компаса ---
    cx, cy, R = W / 2, 250, 92

    # ідеальне коло поля Землі (пунктир, центр у нулі)
    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="4 4"/>' % (cx, cy, R, MUTED))
    frags.append(text(cx, cy - R - 12, "ідеальне коло: поле Землі, центр у нулі",
                      size=11, color=MUTED))

    # реальний вимір: еліпс, зсунутий і розтягнутий
    ox, oy = 26, -14          # зсув центру = тверде залізо
    rx, ry = R * 1.28, R * 0.74   # розтяг = м'яке залізо
    ang = -22
    ecx, ecy = cx + ox, cy + oy
    frags.append('<g transform="translate(%.1f %.1f) rotate(%.1f)">'
                 '<ellipse cx="0" cy="0" rx="%.1f" ry="%.1f" fill="none" '
                 'stroke="%s" stroke-width="2.4"/></g>'
                 % (ecx, ecy, ang, rx, ry, POS))

    # центр нуля й центр еліпса + вектор зсуву
    frags.append(circle(cx, cy, 3.5, fill=INK, stroke=INK))
    frags.append(text(cx - 12, cy + 16, "0", size=12, color=INK, bold=True))
    frags.append(circle(ecx, ecy, 3.5, fill=POS, stroke=POS))
    frags.append(arrow(cx, cy, ecx, ecy, color=POS, sw=2.2))

    # підписи спотворень
    b1 = textbox(cx, cy + R + 66, "тверде залізо (hard iron)\nзсуває коло з центру → COMPASS_OFS",
                 size=11, color=POS, stroke=POS, fill="#fdecea")[0]
    frags.append(b1)
    b2 = textbox(cx, cy + R + 108, "м'яке залізо (soft iron)\nрозтягує коло в еліпс → COMPASS_DIA/ODI",
                 size=11, color=NEG, stroke=NEG, fill="#eaf0fd")[0]
    frags.append(b2)

    # --- ліва панель: корабель XIX ст. ---
    lx = 150
    frags.append(text(lx, 78, "XIX століття: залізний корабель", size=13, bold=True))
    # схематичний бінакль зі сферами Кельвіна
    binn_y = 150
    frags.append(rect(lx - 10, binn_y, 20, 54, fill=FILL, stroke=LINE, sw=1.6, rx=4))
    frags.append(circle(lx, binn_y - 8, 9, fill="#eef1f4", stroke=LINE, sw=1.6))
    frags.append(text(lx, binn_y - 5, "N", size=9, color=NEG, bold=True))
    # кулі Кельвіна обабіч
    frags.append(circle(lx - 30, binn_y + 6, 12, fill="#e5e7eb", stroke=LINE, sw=1.6))
    frags.append(circle(lx + 30, binn_y + 6, 12, fill="#e5e7eb", stroke=LINE, sw=1.6))
    # брус Фліндерса
    frags.append(rect(lx - 4, binn_y + 22, 8, 30, fill="#d1d5db", stroke=LINE, sw=1.4, rx=2))
    frags.append(mtext(lx, binn_y + 78, ["кулі Кельвіна (м'яке залізо)",
                                         "брус Фліндерса, магніти (тверде)"],
                       size=10, color=MUTED))

    # --- права панель: дрон ---
    rx2 = W - 150
    frags.append(text(rx2, 78, "XXI століття: дрон", size=13, bold=True))
    dy = 150
    # рама-хрест
    frags.append(line(rx2 - 34, dy, rx2 + 34, dy, color=INK, sw=3))
    frags.append(line(rx2, dy - 34, rx2, dy + 34, color=INK, sw=3))
    for mxo, myo in [(-34, 0), (34, 0), (0, -34), (0, 34)]:
        frags.append(circle(rx2 + mxo, dy + myo, 8, fill="#e5e7eb", stroke=LINE, sw=1.4))
    # магнітометр на щоглі
    frags.append(line(rx2, dy, rx2 + 22, dy - 30, color=MUTED, sw=1.6))
    frags.append(circle(rx2 + 22, dy - 30, 8, fill="#eef1f4", stroke=NEG, sw=1.8))
    frags.append(text(rx2 + 22, dy - 27, "N", size=9, color=NEG, bold=True))
    frags.append(mtext(rx2, dy + 66, ["магнітометр на щоглі",
                                      "+ підгонка еліпсоїда"], size=10, color=MUTED))

    # стрілки «та сама задача» від панелей до центру
    frags.append(arrow(lx + 46, binn_y + 6, cx - R - 30, cy, color=LINE, sw=1.6))
    frags.append(arrow(rx2 - 46, dy + 6, cx + R + 30, cy, color=LINE, sw=1.6))

    render(os.path.join(IMG, "same-problem.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_same_problem()
    print("hist figure written")
