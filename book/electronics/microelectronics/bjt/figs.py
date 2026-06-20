# -*- coding: utf-8 -*-
"""Фігури до вставки «Дарлінгтонова пара» (тема «BJT-транзистори»).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def npn(cx, cy, label, color=INK):
    """Маленький символ NPN: вертикальна база-смужка, колектор угорі, емітер зі стрілкою вниз."""
    out = []
    bx = cx                       # вертикальна смужка бази
    out.append(line(bx, cy - 22, bx, cy + 22, color=color, sw=2.4))
    out.append(line(bx - 26, cy, bx, cy, color=color, sw=1.8))            # вивід бази
    out.append(line(bx, cy - 14, cx + 22, cy - 30, color=color, sw=1.8))  # до колектора
    out.append(line(cx + 22, cy - 30, cx + 22, cy - 44, color=color, sw=1.8))
    out.append(line(bx, cy + 14, cx + 22, cy + 30, color=color, sw=1.8))  # до емітера (стрілка)
    out.append(arrow(cx + 8, cy + 20, cx + 22, cy + 30, color=color, sw=1.8))
    out.append(line(cx + 22, cy + 30, cx + 22, cy + 44, color=color, sw=1.8))
    out.append(text(bx - 30, cy + 4, label, size=13, color=color, anchor="end", bold=True))
    return "".join(out), (cx + 22, cy - 44), (cx + 22, cy + 44)  # вузли колектора й емітера


# ── 1. Множення β: вихід першого стає базою другого ──────────────────────────
def fig_beta_multiply():
    W, H = 720, 420
    f = [text(W / 2, 28, "Дарлінгтонова пара: вихід першого транзистора живить базу другого",
              size=16, bold=True)]

    # спільний колектор угорі (обидва колектори разом)
    col_y = 70
    f.append(line(150, col_y, 600, col_y, color=POS, sw=2.4))
    f.append(text(610, col_y + 4, "C", size=14, color=POS, anchor="start", bold=True))
    f.append(text(150, col_y - 10, "спільний колектор", size=12, color=MUTED, anchor="start"))

    # Q1 (вхідний, слабкий) та Q2 (вихідний, силовий)
    q1, c1, e1 = npn(250, 200, "Q1")
    q2, c2, e2 = npn(470, 230, "Q2")
    f.append(q1)
    f.append(q2)

    # колектори обох — до спільної шини
    f.append(line(c1[0], c1[1], c1[0], col_y, color=POS, sw=1.8))
    f.append(line(c2[0], c2[1], c2[0], col_y, color=POS, sw=1.8))

    # емітер Q1 → база Q2 (КЛЮЧ: підсилений струм першого = базовий струм другого)
    f.append(line(e1[0], e1[1], e1[0], 230, color=FIELD, sw=2.4))
    f.append(line(e1[0], 230, 470 - 26, 230, color=FIELD, sw=2.4))   # у базу Q2
    f.append(text(335, 222, "e1 → b2", size=12, color=FIELD, anchor="middle", bold=True))

    # спільний емітер унизу
    em_y = 330
    f.append(line(e2[0], e2[1], e2[0], em_y, color=NEG, sw=2.4))
    f.append(line(220, em_y, 600, em_y, color=NEG, sw=2.4))
    f.append(text(610, em_y + 4, "E", size=14, color=NEG, anchor="start", bold=True))

    # вхід бази Q1
    f.append(line(150, 200, 250 - 26, 200, color=INK, sw=1.8))
    f.append(text(140, 204, "B", size=14, color=INK, anchor="end", bold=True))
    f.append(text(150, 184, "крихітний Iб", size=12, color=MUTED, anchor="start"))

    # підписи струмів — наростання
    bx1, by1, bw1, bh1 = 70, 360, 260, 44
    f.append(fitbox(bx1, by1, bw1, bh1,
                    "Q1 підсилює Iб у β1 разів;\nцей струм — уже база для Q2",
                    size=12, fill="#eef7ef", stroke=FIELD))
    bx2, by2, bw2, bh2 = 390, 360, 280, 44
    f.append(fitbox(bx2, by2, bw2, bh2,
                    "Q2 підсилює ще в β2 разів →\nзагальне β ≈ β1 · β2",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, "darlington-beta.svg"), W, H, *f)


# ── 2. Ціна пари: подвійний Vbe і повільне вимкнення ─────────────────────────
def fig_price():
    W, H = 720, 360
    f = [text(W / 2, 28, "Чим платимо: подвійний поріг і застрягання при вимкненні",
              size=16, bold=True)]

    # ── ліворуч: стек двох переходів = ~1.2–1.4 В ──
    lx = 60
    f.append(text(lx + 120, 64, "Поріг = два переходи в стопку", size=13, bold=True, anchor="middle"))
    f.append(fitbox(lx, 86, 240, 40, "Vбе(Q1) ≈ 0.7 В", size=13, fill=FILL, stroke=LINE))
    f.append(text(lx + 120, 142, "+", size=20, color=POS, bold=True))
    f.append(fitbox(lx, 152, 240, 40, "Vбе(Q2) ≈ 0.7 В", size=13, fill=FILL, stroke=LINE))
    f.append(line(lx, 206, lx + 240, 206, color=INK, sw=1.6))
    f.append(fitbox(lx, 216, 240, 44, "разом ≈ 1.2–1.4 В,\nщоб пара відкрилась", size=13,
                    fill="#fdecea", stroke=POS, bold=True))

    # ── праворуч: вимкнення — нікому стягнути заряд із бази Q2 ──
    rx = 380
    f.append(text(rx + 150, 64, "Вимкнення: база Q2 «висить»", size=13, bold=True, anchor="middle"))
    # символ Q2 з відкритою базою
    q2, c2, e2 = npn(rx + 70, 150, "Q2")
    f.append(q2)
    f.append(line(c2[0], c2[1], c2[0], 92, color=MUTED, sw=1.6))
    f.append(line(e2[0], e2[1], e2[0], 220, color=MUTED, sw=1.6))
    # хрест на виводі бази — нема куди витекти струму
    bxn = rx + 70 - 26
    f.append(line(bxn - 16, 150 - 12, bxn - 4, 150 + 12, color=POS, sw=2.4))
    f.append(line(bxn - 16, 150 + 12, bxn - 4, 150 - 12, color=POS, sw=2.4))
    f.append(text(bxn - 22, 138, "нема куди", size=11, color=POS, anchor="end"))
    f.append(fitbox(rx, 240, 300, 64,
                    "Q1, закрившись, перестає давати струм,\n"
                    "але вже накопичений заряд бази Q2\n"
                    "розсотується сам → вимкнення повільне",
                    size=12, fill="#eef1f5", stroke=LINE))

    render(os.path.join(IMG, "darlington-price.svg"), W, H, *f)


if __name__ == "__main__":
    fig_beta_multiply()
    fig_price()
    print("OK: figs у", IMG)
