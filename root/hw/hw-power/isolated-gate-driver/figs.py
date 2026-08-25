# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чому бутстреп ламається, а розв'язка — ні ─────────────────────
# Ліворуч: спільна земля, потенціали близькі — бутстреп працює.
# Праворуч: два світи з різницею в сотні вольт — спільної опори немає.
def fig_why():
    W, H = 760, 400
    frags = []

    # --- лівий блок: спільна земля ---
    lx = 30
    frags.append(fitbox(lx, 60, 300, 46, "Спільна земля",
                        size=16, bold=True, fill="#eaf3ff", stroke=NEG))
    # контролер
    frags.append(fitbox(lx, 140, 130, 70, "Логіка\n0…12 В",
                        size=13, fill=FILL, stroke=LINE))
    # силовий вузол
    frags.append(fitbox(lx + 170, 140, 130, 70, "Силовий\nвузол ~50 В",
                        size=13, fill=FILL, stroke=LINE))
    # спільна земляна шина
    gy = 250
    frags.append(line(lx, gy, lx + 300, gy, color=NEG, sw=3))
    frags.append(text(lx + 150, gy + 22, "одна земля на двох", size=12, color=NEG))
    frags.append(line(lx + 65, 210, lx + 65, gy, color=LINE, sw=1.5))
    frags.append(line(lx + 235, 210, lx + 235, gy, color=LINE, sw=1.5))
    frags.append(fitbox(lx, 300, 300, 62,
                        "бутстреп «дотягується» через\nспільну опору — заряд Cbs є звідки взяти",
                        size=12, fill="#eafaf0", stroke=FIELD))

    # роздільник
    frags.append(line(W/2, 50, W/2, H-30, color=MUTED, sw=1.5, dash="5 6"))

    # --- правий блок: два світи ---
    rx = 420
    frags.append(fitbox(rx, 60, 310, 46, "Різні землі (мережа, привід)",
                        size=15, bold=True, fill="#fdeeec", stroke=POS))
    frags.append(fitbox(rx, 140, 130, 70, "Логіка\n0 В опора",
                        size=13, fill=FILL, stroke=LINE))
    frags.append(fitbox(rx + 180, 140, 130, 70, "Плече мосту\n≈ +540 В",
                        size=13, fill=FILL, stroke=LINE))
    # дві РІЗНІ землі, рознесені по вертикалі
    frags.append(line(rx, 250, rx + 130, 250, color=NEG, sw=3))
    frags.append(text(rx + 65, 272, "земля A = 0 В", size=11, color=NEG))
    frags.append(line(rx + 180, 300, rx + 310, 300, color=POS, sw=3))
    frags.append(text(rx + 245, 322, "земля B «літає» ±540 В", size=11, color=POS))
    frags.append(line(rx + 65, 210, rx + 65, 250, color=LINE, sw=1.5))
    frags.append(line(rx + 245, 210, rx + 245, 300, color=LINE, sw=1.5))
    # розрив між землями
    frags.append(text(rx + 155, 360, "спільної опори НЕМА → бутстреп безсилий",
                     size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'why-isolate.svg'), W, H, *frags,
           title="Коли бутстрепа досить, а коли потрібна розв'язка")


# ── Фігура 2: три способи перенести сигнал через бар'єр ─────────────────────
def fig_channels():
    W, H = 780, 430
    frags = []

    # бар'єр посередині
    bx = W/2
    frags.append(line(bx, 55, bx, H-20, color=POS, sw=2.5, dash="4 5"))
    frags.append(text(bx, H-6, "бар'єр ізоляції", size=12, color=POS, bold=True))
    frags.append(text(W*0.25, 52, "вхід (логіка)", size=13, color=MUTED, bold=True))
    frags.append(text(W*0.75, 52, "вихід (плаваючий затвор)", size=13, color=MUTED, bold=True))

    rows = [
        ("Оптопара", "світлодіод → фотоприймач", "світло крізь прозорий гель", "#fff7e6", "#b8860b"),
        ("Трансформатор", "імпульс струму в котушці", "магнітне поле крізь виток", "#eef2ff", NEG),
        ("Цифровий ізолятор", "модульований фронт", "ємність / мікро-котушка в чипі", "#eafaf0", FIELD),
    ]
    y0 = 90
    dy = 108
    for i, (name, left, mid, fill, col) in enumerate(rows):
        cy = y0 + i*dy + 30
        # ліворуч — джерело
        frags.append(fitbox(60, cy-26, 200, 52, left, size=12, fill=FILL, stroke=LINE))
        # праворуч — приймач + назва каналу
        frags.append(fitbox(W-260, cy-26, 200, 52, name, size=14, bold=True, fill=fill, stroke=col))
        # стрілка через бар'єр з підписом СПОСОБУ (над лінією, по центру між боками)
        frags.append(arrow(268, cy, W-268, cy, color=col, sw=2.2))
        frags.append(text(bx, cy-14, mid, size=11, color=col))

    render(os.path.join(IMG, 'channels.svg'), W, H, *frags,
           title="Три канали через бар'єр: та сама задача, різна фізика")


# ── Фігура 3: CMTI — стрибок землі впорскує струм крізь ємність бар'єра ─────
def fig_cmti():
    W, H = 720, 380
    frags = []

    # вхідний бік
    frags.append(fitbox(40, 150, 150, 80, "Логіка\nземля A\n(нерухома)",
                        size=13, fill="#eef4ff", stroke=NEG))
    # вихідний бік
    frags.append(fitbox(W-190, 150, 150, 80, "Драйвер\nземля B\n(«літає»)",
                        size=13, fill="#fdeeec", stroke=POS))

    # бар'єр з паразитною ємністю Cio
    bx = W/2
    frags.append(line(bx-14, 90, bx-14, 290, color=INK, sw=2.5))
    frags.append(line(bx+14, 90, bx+14, 290, color=INK, sw=2.5))
    frags.append(text(bx, 78, "Cio (паразитна ємність бар'єра)", size=12, bold=True))

    # струм-«злодій» крізь ємність
    frags.append(arrow(bx+40, 190, bx-40, 190, color=POS, sw=2.4))
    frags.append(text(bx, 168, "i = Cio · dV/dt", size=13, color=POS, bold=True))

    # стрибок потенціалу землі B знизу
    frags.append(line(W-190+75, 230, W-190+75, 320, color=POS, sw=2))
    frags.append(text(W-115, 340, "земля B стрибає\nна сотні В за наносекунди",
                     size=11, color=POS))
    # мала стрілка вгору коло B
    frags.append(arrow(W-190+75, 320, W-190+75, 292, color=POS, sw=2))

    # висновок ліворуч знизу
    frags.append(fitbox(40, 300, 250, 60,
                        "цей струм намагається\nхибно ворухнути вихід —\nCMTI каже, скільки dV/dt стерпить",
                        size=11, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, 'cmti.svg'), W, H, *frags,
           title="Звідки береться вимога CMTI")


if __name__ == '__main__':
    fig_why()
    fig_channels()
    fig_cmti()
    print("figures written to", IMG)
